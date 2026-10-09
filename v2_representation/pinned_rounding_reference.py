"""Research integer/FP32 rounding functions, copied without math changes.

Only pure numerical functions are included; the independent upstream mesh
reference, file loader, and comparison wrapper are omitted.
"""
import numpy as np

def _parts(bits):
    sign = -1 if bits >> 31 else 1
    exponent = (bits >> 23) & 255
    fraction = bits & 0x7fffff
    if exponent == 255:
        raise ValueError('Only finite FP32 FMA operands are supported')
    return sign * (fraction if exponent == 0 else fraction | 0x800000), (-149 if exponent == 0 else exponent - 150)


def _rounded_integer(n, shift):
    if shift <= 0:
        return n << -shift
    whole, remainder = divmod(n, 1 << shift)
    halfway = 1 << (shift - 1)
    return whole + int(remainder > halfway or (remainder == halfway and whole & 1))


def _exact_fma_bits(a_bits, b_bits, c_bits, zero_sign_bits):
    """Integer IEEE round-to-nearest/ties-even for a*b+c (finite FP32)."""
    a, ae = _parts(a_bits); b, be = _parts(b_bits); c, ce = _parts(c_bits)
    pe = ae + be; unit = min(pe, ce)
    exact = (a * b << (pe - unit)) + (c << (ce - unit))
    if exact == 0:
        return zero_sign_bits & 0x80000000
    sign = 0x80000000 if exact < 0 else 0
    exact = abs(exact); exponent = exact.bit_length() - 1 + unit
    if exponent < -126:
        return sign | _rounded_integer(exact, -149 - unit)
    mantissa = _rounded_integer(exact, exponent - 23 - unit)
    if mantissa == 0x1000000:
        mantissa >>= 1; exponent += 1
    if exponent > 127:
        return sign | 0x7f800000
    return sign | ((exponent + 127) << 23) | (mantissa & 0x7fffff)


def fma_fp32(a, b, c, *, details=None):
    """Faithful finite FP32 fused a*b+c, with integer double-rounding fallback.

    Two FP32 mantissas multiply exactly in binary64 (at most 48 significant
    bits). Casting the binary64 sum can double-round only at an FP32 midpoint;
    those entries use exact signed integers, never a fitted GPU value.
    """
    a, b, c = np.broadcast_arrays(a, b, c)
    if any(x.dtype != np.float32 or not np.isfinite(x).all() for x in (a, b, c)):
        raise ValueError('Finite FP32 operands required')
    with np.errstate(over='ignore', under='ignore'):
        wide = a.astype(np.float64) * b.astype(np.float64) + c.astype(np.float64)
        rounded = wide.astype(np.float32)
        direction = np.where(wide >= rounded.astype(np.float64), np.float32(np.inf), np.float32(-np.inf))
        neighbor = np.nextafter(rounded, direction)
        midpoint = (rounded.astype(np.float64) + neighbor.astype(np.float64)) * .5
    ambiguous = (wide == midpoint) & (wide != rounded.astype(np.float64)) & np.isfinite(midpoint)
    indices = np.flatnonzero(ambiguous)
    if len(indices):
        af, bf, cf = [np.ascontiguousarray(x).reshape(-1).view(np.uint32) for x in (a, b, c)]
        out = rounded.reshape(-1).view(np.uint32)
        for i in indices:
            out[i] = _exact_fma_bits(int(af[i]), int(bf[i]), int(cf[i]), int(out[i]))
    if not np.isfinite(rounded).all():
        raise ValueError('Nonfinite FP32 FMA result')
    if details is not None:
        details['fma_scalar_operations'] = details.get('fma_scalar_operations', 0) + int(rounded.size)
        details['exact_integer_midpoint_operations'] = details.get('exact_integer_midpoint_operations', 0) + int(len(indices))
    return rounded


def cross_fp32(a, b, *, details=None):
    if a.shape != b.shape or a.ndim != 2 or a.shape[1] != 3:
        raise ValueError('Original cross requires aligned [N,3] operands')
    axis = next((i for i, size in enumerate(a.shape) if size == 3), None)
    if axis is None:
        raise ValueError('No original default-cross size3 axis')
    aa, bb = np.moveaxis(a, axis, -1), np.moveaxis(b, axis, -1)
    out = np.empty_like(aa)
    for i, j, k in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        # The second product is eager FP32 rounded; only the first multiply
        # and subtraction are fused. Operation order is fixed, never selected
        # per quad using the candidate result.
        rhs = np.multiply(aa[..., k], bb[..., j], dtype=np.float32)
        out[..., i] = fma_fp32(aa[..., j], bb[..., k], -rhs, details=details)
    return np.moveaxis(out, -1, axis)


def align_fp32(normal0, normal1):
    p = np.multiply(normal0, normal1, dtype=np.float32)
    # Pinned Reduce.cuh: width=floor_pow2(3)=2, lane0 loads 0 then2,
    # lane1 loads1; the final width2 shuffle adds lane1 to lane0.
    return np.abs(np.add(np.add(p[:, 0], p[:, 2], dtype=np.float32), p[:, 1], dtype=np.float32))[:, None]

