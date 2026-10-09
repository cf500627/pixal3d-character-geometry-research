"""Portable configuration wrapper for the unchanged Windows float64 ray code.

The default replay is synthetic SOURCE -> the same synthetic SOURCE. It verifies
packaging and the inherited camera contract, not a new reconstruction experiment.
"""
import argparse
import json
from pathlib import Path
import struct
import subprocess

import numpy as np

from read_mesh import read_ply
from ray_metrics import DT, errors, hits
import orientation_metrics
from signed_metrics import signed_quantiles


def write_mesh(path, vertices, faces):
    with path.open("xb") as stream:
        stream.write(np.asarray([len(vertices), len(faces)], "<u8").tobytes())
        stream.write(vertices.astype("<f8").tobytes())
        stream.write(faces.astype("<u4").tobytes())


def write_camera_rays(path, camera):
    # The numerical expression and ordering are the original synthetic A1 rays.
    if camera["resolution"] != [2048, 2048] or camera["crop_xyxy"] != [0, 0, 2048, 2048]:
        raise ValueError("This reference replay requires the inherited complete camera frame")
    m = np.asarray(camera["camera_matrix_world"])
    scale = camera["ortho_scale"]
    direction = -m[:3, 2]
    direction /= np.linalg.norm(direction)
    with path.open("xb") as stream:
        stream.write(np.asarray([2048**2], "<u8").tobytes())
        for y0 in range(0, 2048, 64):
            yy, xx = np.mgrid[y0:y0 + 64, 0:2048]
            origin = m[:3, 3] + ((xx.ravel() + .5) / 2048 - .5)[:, None] * scale * m[:3, 0] + (.5 - (yy.ravel() + .5) / 2048)[:, None] * scale * m[:3, 1]
            rays = np.c_[origin, np.broadcast_to(direction, origin.shape)].astype("<f8")
            stream.write(rays.tobytes())


def run_rays(binary, mesh, rays, output):
    process = subprocess.run([str(binary), "rays", str(mesh), str(rays), str(output)], capture_output=True, text=True)
    if process.returncode:
        raise RuntimeError("Native ray process failed: " + process.stderr.strip())
    with output.open("rb") as stream:
        count = struct.unpack("<Q", stream.read(8))[0]
    if output.stat().st_size != 8 + count * DT.itemsize:
        raise ValueError("Native ray output length differs from its header")
    return hits(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--raytracer", type=Path, required=True, help="Locally compiled capacity executable")
    parser.add_argument("--output", type=Path, required=True, help="New output directory; existing directories are rejected")
    parser.add_argument("--candidate", type=Path, help="Optional synthetic candidate mesh from the separately documented inference smoke test")
    args = parser.parse_args()
    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    source_path = config_path.parent / config["source_mesh"]
    if Path(config["source_mesh"]).is_absolute():
        raise ValueError("Example configuration must contain a relative mesh path")
    binary = args.raytracer.resolve()
    if not binary.is_file():
        raise ValueError("Compile the Windows native capacity source first")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    sv, sf, _ = read_ply(source_path)
    expected = config["historical_reference"]
    if (len(sv), len(sf)) != (expected["vertices"], expected["faces"]):
        raise ValueError("Synthetic source geometry differs from the existing A1 reference")
    source_binary = output / "source_mesh.bin"
    full_rays = output / "full_camera_rays.bin"
    source_full_hits = output / "source_full_hits.bin"
    write_mesh(source_binary, sv, sf)
    write_camera_rays(full_rays, config["camera"])
    full_source = run_rays(binary, source_binary, full_rays, source_full_hits)
    visible = full_source["face"] >= 0
    if len(full_source) != 2048**2 or int(visible.sum()) != expected["source_visible_pixels"]:
        raise ValueError("SOURCE-visible count differs from the existing A1 reference")
    # Select the same SOURCE-visible camera rays used by the original A1 process.
    all_rays = np.memmap(full_rays, dtype="<f8", mode="r", offset=8, shape=(2048**2, 6))
    selected_rays = np.asarray(all_rays[visible]).copy()
    del all_rays
    visible_path = output / "source_visible_rays.bin"
    with visible_path.open("xb") as stream:
        stream.write(np.asarray([len(selected_rays)], "<u8").tobytes())
        stream.write(selected_rays.tobytes())
    source = full_source[visible].copy()
    if args.candidate:
        cv, cf, _ = read_ply(args.candidate)
        candidate_binary = output / "synthetic_candidate_mesh.bin"
        write_mesh(candidate_binary, cv, cf)
    else:
        cv, cf = sv, sf
        candidate_binary = source_binary
    target = run_rays(binary, candidate_binary, visible_path, output / "candidate_hits.bin")
    if len(target) != len(source) or (target["face"] >= len(cf)).any():
        raise ValueError("Candidate ray result has an invalid size or face index")
    normal, depth, source_visible = errors(source, target, sv, sf, cv, cf)
    unoriented = np.where(np.isfinite(normal), np.minimum(normal, 180 - normal), np.inf)
    miss = target["face"] < 0
    orientation_metrics.configure(config["metrics"])
    metric = orientation_metrics.metric(source_visible, normal, unoriented, depth / orientation_metrics.H, miss)
    valid = source_visible & ~miss
    signed_world = target["t"][valid] - source["t"][valid]
    signed = {"world": signed_quantiles(signed_world), "h1024": signed_quantiles(signed_world / orientation_metrics.H)}
    identity = not args.candidate
    if identity and (not np.array_equal(source["face"], target["face"]) or not np.array_equal(source["t"], target["t"]) or metric["normal"]["oriented_failure"]["count"] or metric["hole"]["combined"]["count"]):
        raise ValueError("Synthetic identity replay changed faces, depths or failure counts")
    result = {
        "status": "PASS_PACKAGING_REFERENCE_REPLAY" if identity else "SYNTHETIC_INFERENCE_REPLAY_COMPLETED",
        "purpose": "Packaging verification against existing synthetic fixture and protocol; not a new research conclusion",
        "historical_reference": expected,
        "source_vertices": len(sv), "source_faces": len(sf),
        "source_visible_pixels": int(source_visible.sum()),
        "candidate_vertices": len(cv), "candidate_faces": len(cf),
        "strata": {"ALL": metric}, "signed_depth": {"ALL": signed},
        "stratification": config["stratification"],
        "native_workers_exit_zero": True,
        "USER_VISUAL_ACCEPTANCE": "PENDING",
    }
    (output / "RESULT.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "source_visible_pixels": result["source_visible_pixels"], "native_workers_exit_zero": True}))


if __name__ == "__main__":
    main()
