"""Opt-in HIP forward-only submanifold convolution for Stage 4C.

Adapted from FlexGEMM 6dd94a859c26ee8246888502eada3dd8ad85532e,
flex_gemm/ops/spconv/submanifold_conv3d.py, MIT license. The upstream
sort/searchsorted neighbor construction and explicit GEMM semantics are retained;
rows are chunked to bound temporary storage. This is not the full FlexGEMM
extension, and deliberately does not provide training or CPU fallback.

MIT License
Copyright (c) 2025 Jianfeng Xiang (belljig@outlook.com)
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import math
import time
import torch
from torch import nn
from .. import SparseTensor

IM2COL_BUDGET_BYTES = 64 * 1024 * 1024
NEIGHBOR_CHUNK_ROWS = 8192
_TELEMETRY = []


def reset_telemetry():
    _TELEMETRY.clear()


def get_telemetry():
    return [dict(item) for item in _TELEMETRY]


def _triple(value, label):
    values = tuple(value) if isinstance(value, (tuple, list)) else (value,) * 3
    if len(values) != 3 or any(type(v) is not int or v <= 0 for v in values):
        raise ValueError(f'{label} must be three positive integers')
    return values


def sparse_conv3d_init(self, in_channels, out_channels, kernel_size, stride=1,
                       dilation=1, padding=None, bias=True, indice_key=None):
    self.kernel_size = _triple(kernel_size, 'kernel_size')
    self.stride = _triple(stride, 'stride')
    self.dilation = _triple(dilation, 'dilation')
    if self.stride != (1, 1, 1) or padding is not None:
        raise NotImplementedError('torch_native supports only stride-1 submanifold convolution with padding=None')
    if any(k % 2 != 1 for k in self.kernel_size):
        raise NotImplementedError('torch_native requires odd kernel sizes')
    self.in_channels, self.out_channels = in_channels, out_channels
    # Initialize exactly as the official conv_flex_gemm wrapper, then preserve
    # its checkpoint layout [Co, Kx, Ky, Kz, Ci].
    self.weight = nn.Parameter(torch.empty(out_channels, in_channels, *self.kernel_size))
    if bias:
        self.bias = nn.Parameter(torch.empty(out_channels))
    else:
        self.register_parameter('bias', None)
    nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
    if self.bias is not None:
        fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.weight)
        if fan_in:
            nn.init.uniform_(self.bias, -1 / math.sqrt(fan_in), 1 / math.sqrt(fan_in))
    self.weight = nn.Parameter(self.weight.permute(0, 2, 3, 4, 1).contiguous())


def _coordinate_version(coords):
    try:
        return coords._version
    except RuntimeError:  # Inference tensors have no version counter.
        return None


def _signature(coords):
    return (coords.device, coords.dtype, tuple(coords.shape), tuple(coords.stride()),
            coords.data_ptr(), coords.storage_offset(), _coordinate_version(coords))


def _neighbor_map(coords, kernel_size, dilation):
    bounds = tuple(int(v) + 1 for v in coords.max(dim=0).values.tolist())
    if bool((coords < 0).any()):
        raise ValueError('Coordinates must be nonnegative [batch,x,y,z]')
    batches, width, height, depth = bounds
    if batches * width * height * depth > torch.iinfo(torch.int64).max:
        raise ValueError('Coordinate key space exceeds int64')
    # Batch is part of the key, and explicit per-axis guards prevent linear
    # address wrapping at any spatial edge or across batches.
    multipliers = torch.tensor([width * height * depth, height * depth, depth, 1],
                               dtype=torch.int64, device=coords.device)
    coords64 = coords.to(torch.int64)
    keys = (coords64 * multipliers).sum(dim=-1)
    sorted_keys, indices = torch.sort(keys)
    if keys.numel() > 1 and bool((sorted_keys[1:] == sorted_keys[:-1]).any()):
        raise ValueError('Sparse coordinates must be unique')
    axes = [torch.arange(-(k // 2) * d, (k // 2) * d + 1, d,
                         device=coords.device, dtype=torch.int64)
            for k, d in zip(kernel_size, dilation)]
    offsets = torch.stack(torch.meshgrid(*axes, indexing='ij'), dim=-1).reshape(-1, 3)
    volume = math.prod(kernel_size)
    neighbors = torch.full((len(coords), volume), -1, dtype=torch.int32, device=coords.device)
    upper = torch.tensor([width, height, depth], device=coords.device, dtype=torch.int64)
    for start in range(0, len(coords), NEIGHBOR_CHUNK_ROWS):
        stop = min(start + NEIGHBOR_CHUNK_ROWS, len(coords))
        queries = coords64[start:stop, None, :].expand(-1, volume, -1).clone()
        queries[:, :, 1:] += offsets[None, :, :]
        valid = ((queries[:, :, 1:] >= 0) & (queries[:, :, 1:] < upper)).all(dim=-1)
        query_keys = (queries * multipliers).sum(dim=-1).contiguous()
        positions = torch.searchsorted(sorted_keys, query_keys).clamp(max=len(coords) - 1)
        valid &= sorted_keys[positions] == query_keys
        neighbors[start:stop] = torch.where(valid, indices[positions], -1).to(torch.int32)
    return neighbors, bounds


def sparse_conv3d_forward(self, x: SparseTensor) -> SparseTensor:
    if torch.is_grad_enabled():
        raise NotImplementedError('torch_native is forward-only; use torch.no_grad() or inference_mode()')
    feats, coords = x.feats, x.coords
    if not torch.version.hip or not feats.is_cuda or not coords.is_cuda or not self.weight.is_cuda:
        raise NotImplementedError('torch_native requires real HIP GPU tensors; CPU fallback is unavailable')
    if coords.dtype != torch.int32 or coords.ndim != 2 or coords.shape[1] != 4:
        raise ValueError('Coordinates must be int32 [N,4]')
    if len(coords) == 0 or len(coords) != len(feats) or feats.ndim != 2:
        raise ValueError('Expected nonempty aligned sparse features and coordinates')
    if feats.shape[1] != self.in_channels or feats.dtype != self.weight.dtype:
        raise ValueError('Feature channel count and dtype must match the convolution weight')
    if feats.device != coords.device or feats.device != self.weight.device:
        raise ValueError('Features, coordinates, and weights must share one HIP device')
    if self.bias is not None and (self.bias.device != feats.device or self.bias.dtype != feats.dtype):
        raise ValueError('Bias device and dtype must match features')
    started = time.perf_counter()
    cache_key = f'TorchNativeSubM_v1_{self.kernel_size}_{self.dilation}'
    signature = _signature(coords)
    cache = x.get_spatial_cache(cache_key)
    reused = cache is not None and cache['signature'] == signature
    if reused and signature[-1] is None:
        reused = bool(torch.equal(cache['coords_snapshot'], coords))
    if not reused:
        mapping, bounds = _neighbor_map(coords, self.kernel_size, self.dilation)
        cache = {'signature': signature, 'coords_snapshot': coords.clone(),
                 'neighbor_map': mapping, 'bounds': bounds}
        x.register_spatial_cache(cache_key, cache)
    mapping = cache['neighbor_map']
    count, volume = mapping.shape
    ci, co = self.in_channels, self.out_channels
    rows = max(1, IM2COL_BUDGET_BYTES // (volume * ci * feats.element_size()))
    output = torch.empty((count, co), device=feats.device, dtype=feats.dtype)
    weight = self.weight.reshape(co, volume * ci).transpose(0, 1)
    for start in range(0, count, rows):
        stop = min(start + rows, count)
        neighbor_rows = mapping[start:stop].reshape(-1).long()
        valid = neighbor_rows >= 0
        im2col = torch.zeros(((stop - start) * volume, ci), device=feats.device, dtype=feats.dtype)
        im2col[valid] = feats[neighbor_rows[valid]]
        im2col = im2col.view(stop - start, volume * ci)
        if self.bias is None:
            torch.mm(im2col, weight, out=output[start:stop])
        else:
            torch.addmm(self.bias, im2col, weight, out=output[start:stop])
    record = {
        'device': str(feats.device), 'hip': torch.version.hip,
        'input_shape': list(feats.shape), 'output_shape': list(output.shape),
        'kernel_shape': list(self.weight.shape), 'dtype': str(feats.dtype),
        'dilation': list(self.dilation), 'neighbor_cache_reused': reused,
        'coordinate_bounds': list(cache['bounds']), 'chunk_rows': rows,
        'chunks': math.ceil(count / rows),
        'max_im2col_bytes': min(count, rows) * volume * ci * feats.element_size(),
        'neighbor_map_bytes': mapping.numel() * mapping.element_size(),
        # GPU work is asynchronous; the full runner measures synchronized time.
        'host_dispatch_seconds': time.perf_counter() - started,
        'coordinates_preserved': True, 'backward_supported': False,
    }
    self._torch_native_last_run = record
    _TELEMETRY.append(record)
    return x.replace(output)


def sparse_inverse_conv3d_init(self, *args, **kwargs):
    raise NotImplementedError('torch_native inverse convolution is not implemented')


def sparse_inverse_conv3d_forward(self, x):
    raise NotImplementedError('torch_native inverse convolution is not implemented')
