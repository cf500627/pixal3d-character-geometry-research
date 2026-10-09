# Portable synthetic CPU replay and research components

The verified subset is a fixed-camera CPU SOURCE-to-itself replay of the existing synthetic sphere. It tests release packaging, reader, camera geometry and native-ray/metric integration. It is not a new character measurement or a VAE result. The sphere is procedural geometry, not a commercial model or its derivative.

## Windows setup

Use a clean Python environment with NumPy and an existing Visual Studio C++ developer command prompt. The unchanged native code uses the Windows API for memory telemetry and is **not** a cross-platform C++ build.

From the release root:

```powershell
python -m venv .venv-eval
.venv-eval\Scripts\python -m pip install -r eval_harness\requirements.txt
mkdir eval_harness\bin
cl /O2 /std:c++17 /EHsc /MD /fp:strict eval_harness\native\capacity.cpp /Fe:eval_harness\bin\capacity.exe /link psapi.lib
.venv-eval\Scripts\python eval_harness\run_cpu_example.py --config examples\sphere_cpu.json --raytracer eval_harness\bin\capacity.exe --output validation\cpu_sphere
```

The output directory must be new. Input paths in the configuration are relative to that file; compiler executable and output location are runtime arguments. No original project location is required.

Expected source geometry and visibility are **2,562 vertices, 5,120 faces and 629,228 SOURCE-visible pixels**, copied from `STAGE10A_VAE_LOSS_DIAGNOSIS_RESULT.md`, §A1 synthetic closed-mesh control. The source-to-itself replay must preserve first-hit face/depth and have no threshold-failure or miss-or->2h pixels. Tiny normal-angle roundoff is retained rather than force-zeroed. Packaging verification is separate from the historical VAE sphere reconstruction error.

An already-generated synthetic inference mesh can be checked with the same command and `--candidate <synthetic-mesh.ply>`. Compare its ALL metric rows with the existing sphere reference in `reports/FINDINGS.md`; this does not run inference or update weights. The synthetic sphere has no inherited NONE/CONFLICT classification, so only ALL is reported.

## Component provenance and unchanged mathematics

| Release file | Existing project source | Change |
|---|---|---|
| `native/capacity.cpp` | Capacity-audit `tools/capacity.cpp` | Exact copy; original admission limits and all math retained |
| `read_mesh.py` | Capacity-audit `tools/read_mesh.py` | Exact copy |
| `ray_metrics.py` | Stage9B `tools/measure_rays.py`: `hits`, `normals`, `errors` | Exact function bodies; machine-specific launcher removed |
| `orientation_metrics.py` | Stage9C-R `tools/analyze.py`: `quantiles`, `metric` | Exact function bodies; threshold globals supplied from config |
| `signed_metrics.py` | Stage10D `local/measure_sweep_mesh.py`: `signed_quantiles` | Exact function body; no private launcher or input registry |
| `run_cpu_example.py` | Release-only integration wrapper; camera expression follows Stage10A `tools/measure_a.py`, `sphere_rays` | Relative configuration, fresh outputs and procedural-reference checks |
| `../examples/sphere_cpu.json` | Stage10A `A_PROTOCOL.json`: sphere camera and metric fields | Selected public numeric fields only; all private pins/references removed |
| `../examples/sphere_source.ply` | Stage10A procedural sphere fixture | Exact synthetic copy |

The full original fixed-render, character ROI and witness orchestration is not claimed portable by this subset. Rendering protocols are described in the findings, but no new renderer is supplied or verified here. The gallery generator accepts user-supplied local images and contains no character payload.

`build_gallery.py` is a small release-only local-image wrapper, not an original renderer. After supplying your own synthetic Clay / TrueNormal / AO images and changing the relative filenames in `examples/gallery_template.json`, run:

```powershell
.venv-eval\Scripts\python eval_harness\build_gallery.py --config examples\gallery_template.json --output validation\synthetic_gallery.html
```

The template deliberately contains no image data. Missing images are rejected. Scroll positions and 1× / 2× / 4× / 8× zoom are synchronized; no visual score is produced. This optional gallery path is not claimed exercised by the CPU ray replay.

## Capacity audit: research code provided as-is

The native executable also retains the original audit interface:

```text
capacity.exe audit mesh.bin RESOLUTION roi.txt output-prefix tolerance-multiplier
```

`mesh.bin` has little-endian uint64 vertex/face counts, float64 xyz vertices and uint32 triangular faces. `roi.txt` starts with an ROI count and then lower xyz / upper xyz world bounds for each ROI. Legal resolutions remain the original CLI choices. The output is the existing fragment/cell/event audit with NO_EDGE, MULTI_SHEET and MULTI_CROSSING-related diagnostics. SOURCE triangle IDs are audit-only identities; they are not a model input or source-free reconstruction aid.

This audit mode is supplied unchanged and **not run during release preparation**. The sphere replay does not invent a capacity classification. Geometry topology QA and original multi-character comparison orchestration remain research components requiring separate setup; the release does not imply they were exercised in the clean example.

The inherited angle/depth thresholds and camera are in configuration. The original metric function's `h=1/1024` unit label is retained; this wrapper rejects another h rather than silently relabelling its results. No miss is removed from the SOURCE-visible failure denominator; signed quantiles condition on finite hits.
