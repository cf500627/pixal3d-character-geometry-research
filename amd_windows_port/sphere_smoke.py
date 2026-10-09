"""Replay an existing synthetic-sphere round trip using separately installed code.

This original wrapper does not include models. The release includes the adapted
convolution and required API header with their original notices, but a fresh
dependency installation remains unverified. It does not make a new geometry claim.
All original input paths are provided by the operator, and writes stay inside
one new output directory. The replay is distinct from a clean release install.
"""
from __future__ import annotations

import argparse
import gc
import importlib.abc
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import types


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def bootstrap_namespace(repo):
    """Expose original module paths without executing unused pipeline initializers."""
    for name in ("pixal3d", "pixal3d.models", "pixal3d.models.sc_vaes"):
        require(name not in sys.modules, "A fresh Python process is required")
        directory = repo.joinpath(*name.split("."))
        require(directory.is_dir(), "Original model package is missing")
        module = types.ModuleType(name)
        module.__package__ = name
        module.__path__ = [str(directory)]
        module.__spec__ = importlib.util.spec_from_loader(name, loader=None, is_package=True)
        module.__spec__.submodule_search_locations = [str(directory)]
        sys.modules[name] = module
        if "." in name:
            parent, child = name.rsplit(".", 1)
            setattr(sys.modules[parent], child, module)


class MeshImportFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Defer unused remesh/texture dependencies; retain the original Mesh classes."""
    name = "pixal3d.representations.mesh.base"

    def __init__(self, source):
        self.source = source

    def find_spec(self, fullname, path=None, target=None):
        if fullname == self.name:
            return importlib.util.spec_from_loader(fullname, self, origin=str(self.source))
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        text = self.source.read_text(encoding="utf-8-sig")
        require(text.count("import cumesh") == 1, "Unexpected original geometry import")
        import_line = "from flex_gemm.ops.grid_sample import grid_sample_3d"
        require(text.count(import_line) == 1, "Unexpected original texture import")
        text = text.replace("import cumesh", "cumesh = _UnusedDependency()")
        text = text.replace(import_line, "grid_sample_3d = _reject_unused_operation")
        prefix = (
            "def _reject_unused_operation(*args, **kwargs):\n"
            "    raise RuntimeError('Remesh and texture operations are outside this replay')\n"
            "class _UnusedDependency:\n"
            "    def __getattr__(self, name):\n"
            "        return _reject_unused_operation\n"
        )
        module.__file__ = str(self.source)
        exec(compile(prefix + text, str(self.source), "exec"), module.__dict__)


def configure(args, output):
    for key in ("PYTHONPATH", "PYTHONHOME", "CONDA_PREFIX", "CONDA_DEFAULT_ENV"):
        os.environ.pop(key, None)
    for key in (
        "HF_HOME", "HF_HUB_CACHE", "HUGGINGFACE_HUB_CACHE", "TRANSFORMERS_CACHE",
        "TORCH_HOME", "XDG_CACHE_HOME", "TEMP", "TMP", "TRITON_CACHE_DIR",
        "TORCH_EXTENSIONS_DIR", "AMD_COMGR_CACHE_DIR", "AMD_CACHE_PATH",
        "HIP_CACHE_PATH", "MIOPEN_CUSTOM_CACHE_DIR", "MIOPEN_USER_DB_PATH",
        "FLEX_GEMM_AUTOTUNE_CACHE_PATH",
    ):
        destination = output / "cache" / key.lower()
        destination.mkdir(parents=True)
        os.environ[key] = str(destination)
    os.environ.update(
        PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1", HF_HUB_OFFLINE="1",
        TRANSFORMERS_OFFLINE="1", WANDB_MODE="disabled", USE_TF="0", USE_FLAX="0",
        ATTN_BACKEND="sdpa", SPARSE_ATTN_BACKEND="sdpa", SPARSE_CONV_BACKEND="torch_native",
        PYTORCH_ROCM_ARCH="gfx1100", GPU_ARCHS="gfx1100", HIP_PLATFORM="amd", MAX_JOBS="1",
        ROCM_PATH=str(args.sdk), ROCM_HOME=str(args.sdk), HIP_PATH=str(args.sdk),
    )
    os.environ["PATH"] = os.pathsep.join((str(args.sdk / "bin"),
                                         str(args.sdk / "lib" / "llvm" / "bin"),
                                         os.environ.get("PATH", "")))
    sys.path[:0] = [str(args.repo), str(args.voxel_package), str(args.extension_dir)]


def write_guard(output):
    def guard(event, values):
        if event != "open":
            return
        path, mode, flags = values
        writing = isinstance(mode, str) and any(letter in mode for letter in "wax+")
        writing |= isinstance(flags, int) and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if writing and not isinstance(path, int):
            require(Path(path).resolve().is_relative_to(output), "Attempt to write outside the new replay directory")
    sys.addaudithook(guard)


def model_from_files(torch, role, config, weights, resolution):
    from safetensors.torch import load_file
    from pixal3d.models.sc_vaes.fdg_vae import FlexiDualGridVaeEncoder, FlexiDualGridVaeDecoder
    cls = FlexiDualGridVaeEncoder if role == "encoder" else FlexiDualGridVaeDecoder
    specification = read_json(config)
    require(specification["name"] == cls.__name__, "The paired official model configuration is required")
    require(specification["args"]["use_fp16"] is True, "Keep the original official FP16 body configuration")
    model = cls(**specification["args"]).eval().requires_grad_(False)
    state = load_file(str(weights), device="cpu")
    current = model.state_dict()
    require(set(state) == set(current), "Official checkpoint keys differ")
    for name, value in state.items():
        require(value.shape == current[name].shape and torch.isfinite(value).all().item(), "Official checkpoint shape or finiteness differs")
        require(value.dtype == current[name].dtype or (value.dtype, current[name].dtype) == (torch.float16, torch.float32), "Unexpected checkpoint precision conversion")
    model.load_state_dict(state, strict=True)
    require(all(torch.equal(value, state[name].to(value.dtype)) for name, value in model.state_dict().items()), "Strict checkpoint values differ")
    del state, current, value
    if role == "decoder":
        require(model.low_vram is False, "CPU model offload is outside the reference contract")
        model.set_resolution(resolution)
    return model.cuda().eval()


def gpu_guard(torch, args):
    torch.cuda.synchronize()
    require(torch.cuda.memory_reserved() <= args.max_reserved_gib * 2**30, "Reserved GPU memory limit exceeded")


def encode(torch, args, output):
    import numpy as np
    import o_voxel
    from pixal3d.modules import sparse as sp
    coords, attrs = o_voxel.io.read_vxz(str(args.target), num_threads=4)
    require(coords.dtype == torch.int32 and coords.ndim == 2 and coords.shape[1] == 3, "Original target support contract differs")
    require(set(attrs) == {"vertices", "intersected"}, "Original target channels differ")
    require(attrs["vertices"].dtype == attrs["intersected"].dtype == torch.uint8, "Original target quantization differs")
    require(((coords >= 0) & (coords < args.resolution)).all().item(), "Target support is outside the configured grid")
    dual = (attrs["vertices"] / 255.0).float()
    packed = attrs["intersected"]
    flags = torch.cat([packed % 2, packed // 2 % 2, packed // 4 % 2], dim=-1).bool()
    model = model_from_files(torch, "encoder", args.encoder_config, args.encoder_weights, args.resolution)
    vertices = sp.SparseTensor(dual, torch.cat([torch.zeros_like(coords[:, :1]), coords], dim=-1)).cuda()
    intersected = vertices.replace(flags.cuda())
    with torch.no_grad():
        latent = model(vertices, intersected, sample_posterior=False)
        require(torch.isfinite(latent.feats).all().item(), "Encoder produced non-finite values")
        arrays = {"coords": latent.coords[:, 1:].cpu().numpy().astype(np.uint8),
                  "feats": latent.feats.cpu().numpy().astype(np.float32)}
    gpu_guard(torch, args)
    with (output / "raw_latent.npz").open("xb") as stream:
        np.savez_compressed(stream, **arrays)
    # The returned object carries only CPU arrays; no encoder SparseTensor/cache.
    del latent, model, vertices, intersected, coords, attrs, dual, packed, flags
    return arrays


def exact_arrays(np, generated, reference):
    with np.load(reference, allow_pickle=False) as old:
        require(set(old.files) == set(generated), "Reference array keys differ")
        return {name: bool(old[name].dtype == generated[name].dtype and
                           np.array_equal(old[name], generated[name])) for name in generated}


def write_mesh(np, path, vertices, faces):
    require(vertices.dtype == np.float32 and faces.dtype == np.int32, "Original mesh precision differs")
    require(np.isfinite(vertices).all() and faces.min() >= 0 and faces.max() < len(vertices), "Invalid mesh output")
    header = (f"ply\nformat binary_little_endian 1.0\nelement vertex {len(vertices)}\n"
              "property float x\nproperty float y\nproperty float z\n"
              f"element face {len(faces)}\nproperty list uchar int vertex_indices\nend_header\n").encode("ascii")
    packed = np.empty(len(faces), dtype=[("n", "u1"), ("f", "<i4", (3,))])
    packed["n"] = 3
    packed["f"] = faces
    with path.open("xb") as stream:
        stream.write(header)
        stream.write(vertices.astype("<f4", copy=False).tobytes())
        stream.write(packed.tobytes())


def decode(torch, args, output):
    import numpy as np
    from pixal3d.modules import sparse as sp
    with np.load(output / "raw_latent.npz", allow_pickle=False) as stored:
        coords, features = stored["coords"].copy(), stored["feats"].copy()
    latent = sp.SparseTensor(torch.from_numpy(features).cuda(),
        torch.from_numpy(np.c_[np.zeros((len(coords), 1), dtype=np.int32), coords.astype(np.int32)]).cuda())
    model = model_from_files(torch, "decoder", args.decoder_config, args.decoder_weights, args.resolution)
    captured = {}

    def observe(module, inputs, h):
        require(h.feats.shape[1] == 7 and torch.isfinite(h.feats).all().item(), "Decoder produced invalid channels")
        captured.update(coords=h.coords[:, 1:].cpu().numpy().copy(), features=h.feats.cpu().numpy().copy(),
                        dual_vertices=(2 * torch.sigmoid(h.feats[:, :3]) - .5).cpu().numpy().copy(),
                        intersected=(h.feats[:, 3:6] > 0).cpu().numpy().copy(),
                        quad_weights=torch.nn.functional.softplus(h.feats[:, 6:7]).cpu().numpy().copy())
    handle = model.output_layer.register_forward_hook(observe)
    try:
        with torch.no_grad():
            meshes = model(latent)
            require(len(meshes) == 1 and captured, "A single original raw mesh is required")
            mesh = meshes[0]
            require(mesh.vertices.is_cuda and mesh.faces.is_cuda, "CPU mesh fallback is forbidden")
            vertices = mesh.vertices.cpu().numpy().copy()
            faces = mesh.faces.cpu().numpy().copy()
        gpu_guard(torch, args)
        comparison = exact_arrays(np, captured, args.expected_decoded)
        with (output / "decoded_representation.npz").open("xb") as stream:
            np.savez_compressed(stream, **captured)
        write_mesh(np, output / "mesh.ply", vertices, faces)
    finally:
        handle.remove()
        handle = model = latent = meshes = mesh = None
    return comparison


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("repo", "voxel-package", "extension-dir", "sdk", "target", "encoder-config",
                 "encoder-weights", "decoder-config", "decoder-weights", "expected-latent", "expected-decoded", "output"):
        parser.add_argument("--" + flag, required=True, type=Path)
    parser.add_argument("--resolution", type=int, default=1024)
    parser.add_argument("--min-driver-free-gib", type=float, default=4)
    parser.add_argument("--max-reserved-gib", type=float, default=4)
    parser.add_argument("--min-disk-free-gib", type=float, default=5)
    parser.add_argument("--check-inputs", action="store_true")
    args = parser.parse_args()
    for name, value in vars(args).items():
        if isinstance(value, Path):
            setattr(args, name, value.resolve())
    require(args.resolution == 1024, "This replay is limited to the archived resolution")
    require(not args.output.exists(), "Choose a new output directory")
    inputs = [value for name, value in vars(args).items() if isinstance(value, Path) and name != "output"]
    require(all(path.exists() for path in inputs), "One or more separately installed inputs are missing")
    require(all(not path.is_relative_to(args.output) and not args.output.is_relative_to(path)
                for path in inputs if path.is_file()), "Input and output paths must be distinct")
    require(shutil.disk_usage(args.output.parent).free >= args.min_disk_free_gib * 2**30, "Disk reserve is insufficient")
    if args.check_inputs:
        print(json.dumps({"status": "INPUT_PATHS_PRESENT", "GPU_execution": False,
                          "clean_release_installation": "NOT_VERIFIED"}))
        return 0
    args.output.mkdir()
    configure(args, args.output)
    write_guard(args.output)
    before = {path: (path.stat().st_size, path.stat().st_mtime_ns) for path in inputs if path.is_file()}
    result = {"status": "FAIL", "reference": "STAGE10A_VAE_LOSS_DIAGNOSIS_RESULT.md: A1 simple closed mesh control",
              "kind": "EXISTING_LOCAL_BACKEND_SYNTHETIC_SPHERE_REPLAY",
              "clean_release_installation": "NOT_VERIFIED", "new_geometry_conclusions": False,
              "optimizer_updates": 0, "checkpoint_writes": 0, "USER_VISUAL_ACCEPTANCE": "PENDING"}
    torch = native_mesh = finder = None
    try:
        import torch
        import numpy as np
        require(torch.__version__ == "2.9.1+rocm7.2.1" and torch.version.hip.startswith("7.2"), "Use the archived native Torch/HIP runtime")
        require(torch.cuda.is_available() and "7900 XTX" in torch.cuda.get_device_name(0), "Use the archived AMD GPU")
        require(torch.cuda.mem_get_info()[0] >= args.min_driver_free_gib * 2**30, "Driver-free GPU reserve is insufficient")
        torch.cuda.reset_peak_memory_stats()
        sys.path.insert(0, str(Path(__file__).resolve().parent / "hip_hash"))
        import native_mesh
        native_mesh.install(args.extension_dir, grid_size=args.resolution)
        bootstrap_namespace(args.repo)
        finder = MeshImportFinder(args.repo / "pixal3d" / "representations" / "mesh" / "base.py")
        sys.meta_path.insert(0, finder)
        arrays = encode(torch, args, args.output)
        result["latent_exact_match"] = exact_arrays(np, arrays, args.expected_latent)
        arrays = None
        result["decoded_exact_match"] = decode(torch, args, args.output)
        result["original_HIP_hash_operations_executed"] = native_mesh.calls() == [
            "hashmap_insert_3d_idx_as_val_cuda", "hashmap_lookup_3d_cuda"]
        require(all(result["latent_exact_match"].values()) and all(result["decoded_exact_match"].values()), "Replay arrays differ from the existing reference")
        require(result["original_HIP_hash_operations_executed"], "Original HIP extraction was not observed")
        require(torch.cuda.max_memory_reserved() <= args.max_reserved_gib * 2**30, "Peak reserved GPU memory limit exceeded")
        result["resource_limits_pass"] = True
        result["status"] = "PASS"
    except BaseException as error:
        result["failure_type"] = type(error).__name__
        # Avoid copying private paths, traceback context or library diagnostics.
    finally:
        if finder is not None and finder in sys.meta_path:
            sys.meta_path.remove(finder)
        finder = None
        if native_mesh is not None:
            native_mesh.cleanup()
        gc.collect()
        if torch is not None and torch.cuda.is_initialized():
            torch.cuda.synchronize()
            torch._C._cuda_clearCublasWorkspaces()
            torch.cuda.empty_cache()
            result["normal_cleanup_pass"] = torch.cuda.memory_allocated() == torch.cuda.memory_reserved() == 0
            if not result["normal_cleanup_pass"]:
                result["status"] = "FAIL"
        result["input_metadata_unchanged"] = all((path.stat().st_size, path.stat().st_mtime_ns) == metadata for path, metadata in before.items())
        if not result["input_metadata_unchanged"]:
            result["status"] = "FAIL"
    with (args.output / "SPHERE_REPLAY_RESULT.json").open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "kind": result["kind"],
                      "normal_cleanup_pass": result.get("normal_cleanup_pass", False)}), flush=True)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
