# Windows AMD inference port — research source release

**PUBLICATION = OWNER_AUTHORIZED.** The owner authorized public repository
creation and push of the reviewed package to
[pixal3d-character-geometry-research](https://github.com/cf500627/pixal3d-character-geometry-research).
Remote publication verification is recorded separately after completion.

This directory contains selected inference-only compatibility changes and their existing validation record. It is not a trained model, a complete image-to-character product, a VAE training port, or an official Windows support commitment.

**Core source and original notices: included. Fresh-source compilation and isolated sphere replay: PASS. Complete fresh dependency installation: NOT_VERIFIED.** The user approved MIT for newly authored code and preserving contributors' original public copyright notices, including their author contact addresses. The previously withheld adapted convolution and required API header are now included without modifying their notices. See [EXCLUSIONS.md](EXCLUSIONS.md) for the remaining exclusions.

The included patch was applied to a new pinned pristine Pixal3D source copy, the released convolution overlay was installed there, and the included HIP extension source was freshly compiled. An isolated worker using that new source and rebuilt extension reproduced the existing sphere arrays exactly and exited normally. These PASS flags are recorded in [REPLAY_VERIFICATION.json](../examples/validation/REPLAY_VERIFICATION.json). The existing Torch/HIP environment, CPU O-Voxel I/O and official weights were reused, so a complete fresh dependency installation remains unverified.

## Validated original runtime

| Component | Previously measured version | Existing source |
| --- | --- | --- |
| Windows | Windows 10 22H2, 64-bit, build 19045.6466 | `AMD_TRAINING_COMPATIBILITY.md`, section 1, OS row |
| GPU | AMD Radeon RX 7900 XTX, gfx1100 | `AMD_TRAINING_COMPATIBILITY.md`, section 1, GPU row |
| Inference Python | 3.12.14 | `STAGE4B_SUMMARY.md`, independent environment paragraph |
| Torch | 2.9.1+rocm7.2.1 | `STAGE4B_SUMMARY.md`, independent environment paragraph |
| HIP | 7.2.53211-158bd99533; HIP 7.2 family | `STAGE4B_SUMMARY.md`, independent environment paragraph |
| ROCm SDK packages | 7.2.1 | `AMD_TRAINING_COMPATIBILITY.md`, section 1, ROCm packages row |
| Host/device compiler | AMD clang 22.0.0git, clang-cl / hipcc | `STAGE7E_BACKEND_PATCH_LOG.md`, toolchain section |
| Linker | MSVC 14.44.35207 | `STAGE7E_BACKEND_PATCH_LOG.md`, toolchain section |
| ROCm header components | rocThrust 4.2.0 and rocPRIM 4.2.0 from rocm-7.2.1 | `STAGE7E_BACKEND_PATCH_LOG.md`, first-party dependencies table |

These are historical observations, not a promise that arbitrary wheel or driver combinations work. The recorded Windows 10 host was outside the cited AMD Windows 11 support matrix. No dependency upgrade is required or attempted by this release preparation.

## Source and patch installation

Run the following only in your own new working copies. Never apply release patches to an active project with unsaved changes.

```powershell
git clone https://github.com/TencentARC/Pixal3D.git upstream/Pixal3D
git -C upstream/Pixal3D checkout f7cf38429b0bd264f1995f0f8743a88b1c728b94
git clone https://github.com/microsoft/TRELLIS.2.git upstream/TRELLIS.2
git -C upstream/TRELLIS.2 checkout 75fbf0183001ed9876c8dbb35de6b68552ee08bd
git -C upstream/Pixal3D apply --check ../../amd_windows_port/patches/Pixal3D_inference_imports_and_backend.patch
git -C upstream/Pixal3D apply ../../amd_windows_port/patches/Pixal3D_inference_imports_and_backend.patch
```

Install the exact native Windows ROCm Torch distribution through the [AMD Windows installation instructions](https://rocm.docs.amd.com/projects/radeon-ryzen/en/docs-7.2.1/docs/install/installrad/windows/install-pytorch.html). Generic `pip install torch` is insufficient to select this distribution. Dependency installation should follow the pinned source requirements and preserved notices; no fresh AMD dependency installation is claimed here.

Copy the included adapted convolution into that **fresh** Pixal3D checkout and retain its original FlexGEMM license. These commands assume the release root as the current directory:

```powershell
Copy-Item -LiteralPath amd_windows_port/overlay/pixal3d/modules/sparse/conv/conv_torch_native.py -Destination upstream/Pixal3D/pixal3d/modules/sparse/conv/conv_torch_native.py
New-Item -ItemType Directory -Force upstream/Pixal3D/third_party/FlexGEMM | Out-Null
Copy-Item -LiteralPath amd_windows_port/licenses/FlexGEMM/LICENSE -Destination upstream/Pixal3D/third_party/FlexGEMM/LICENSE
```

The `hip_hash/src/api.h` file is now included unmodified. `hip_hash/LICENSE` preserves its author's MIT notice; the original Microsoft attribution for the remaining O-Voxel package is preserved separately under `licenses/TRELLIS.2/LICENSE`. Contributors and upstream attributions have not been anonymized or removed.

The archived hash source patch is a mechanical translation record; the actual original build used PyTorch's HIP-aware `CUDAExtension` to translate `src/hash.cu`, so do not apply both translation routes to the same file.

Obtain rocThrust and rocPRIM header dependencies independently at the recorded revisions. They remain separately licensed dependencies; no full header archive is bundled. Keep rocThrust's Apache-2.0 LICENSE/NOTICES and rocPRIM's MIT LICENSE/NOTICES alongside those checkouts.

```powershell
git clone https://github.com/ROCm/rocThrust.git installed/hip_hash_dependencies/rocThrust
git -C installed/hip_hash_dependencies/rocThrust checkout ed551d53d9bac8fd55b2a7fc62683946e33060a0
git clone https://github.com/ROCm/rocPRIM.git installed/hip_hash_dependencies/rocPRIM
git -C installed/hip_hash_dependencies/rocPRIM checkout a272f74a01fa2160763122f85ade1b411f407924
python -I -B amd_windows_port/prepare_header_versions.py --rocthrust installed/hip_hash_dependencies/rocThrust --rocprim installed/hip_hash_dependencies/rocPRIM --output installed/hip_hash_dependencies/generated_include
```

`prepare_header_versions.py` reads the original CMake component version 4.2.0 and templates, retains their original copyright/license text and substitutes only their version placeholders. It writes a new output directory and does not edit either dependency checkout. The component version and arithmetic follow `STAGE7E_BACKEND_PATCH_LOG.md`, first-party dependencies and generated headers sections.

Use an x64 Visual Studio developer shell with the recorded linker/Windows SDK available. Configure `HIP_PATH` to your separately installed SDK and `HIP_HASH_DEPENDENCIES` to `installed/hip_hash_dependencies`. Put the SDK's `bin` and `lib/llvm/bin` on this shell's PATH, and select its `clang-cl.exe` as `CXX`. The packaging code derives all source locations relative to its own directory; no original workstation path is embedded.

Build from a **new copy** of the released source, with separate new intermediate and output directories. For example, from the release root:

```powershell
New-Item -ItemType Directory -Force run-output | Out-Null
Copy-Item -LiteralPath amd_windows_port/hip_hash -Destination run-output/hip_hash-source -Recurse
$env:HIP_HASH_DEPENDENCIES=(Resolve-Path installed/hip_hash_dependencies).Path
$env:CXX=Join-Path $env:HIP_PATH 'lib/llvm/bin/clang-cl.exe'
$env:ROCM_HOME=$env:HIP_PATH
$env:ROCM_PATH=$env:HIP_PATH
$env:PYTORCH_ROCM_ARCH='gfx1100'
$env:HIP_PLATFORM='amd'
$env:MAX_JOBS='1'
$env:PATH=(Join-Path $env:HIP_PATH 'bin')+[IO.Path]::PathSeparator+(Join-Path $env:HIP_PATH 'lib/llvm/bin')+[IO.Path]::PathSeparator+$env:PATH
python -I -B run-output/hip_hash-source/setup_hash.py build_ext --build-temp run-output/hip_hash-temp --build-lib run-output/hip_hash-lib
```

Set `HIP_PATH` before this block using your own SDK installation; this example intentionally supplies no machine-specific location. PyTorch's HIP-aware setuptools build route is used, rather than the historically unsuccessful Windows JIT CUDA_HOME route. Compiler flags preserve the recorded build flags and reference the SDK's device bitcode. This operation compiles the included code; it does not execute a model or update any weights.

Verify the fresh module in another new process after importing Torch so its DLL dependencies are loaded. Point the existing sphere replay command's `--repo` to the fresh patched checkout and `--extension-dir` to the new `run-output/hip_hash-lib`, while using the separately installed CPU O-Voxel I/O package and official model files. Never substitute the old compiled extension directory for this fresh-source verification. Fresh compilation, module import and isolated sphere replay are separate gates. They were completed successfully for the new pinned source copy and rebuilt extension, as recorded in [REPLAY_VERIFICATION.json](../examples/validation/REPLAY_VERIFICATION.json); this reused the existing runtime and separately held model files.

`hip_hash/setup_hash.py` remains a packaging adapter. A successful clean-source build in an existing environment is distinct from a fully fresh dependency installation.

## Inference contract

Copy `config.example.json` to your private configuration and set paths there. No original workstation paths, models or input arrays are shipped. Obtain the official paired encoder and decoder files from [Microsoft TRELLIS.2-4B](https://huggingface.co/microsoft/TRELLIS.2-4B/tree/af44b45f2e35a493886929c6d786e563ec68364d). Use `shape_enc_next_dc_f16c32_fp16` and `shape_dec_next_dc_f16c32_fp16` paired JSON/safetensors; all weights remain separate downloads under their own terms.

The preserved inference contract is:

1. Independently produce an official 7-channel O-Voxel target at resolution 1024 from a lawful synthetic or separately licensed input.
2. Select `ATTN_BACKEND=sdpa`, `SPARSE_ATTN_BACKEND=sdpa`, `SPARSE_CONV_BACKEND=torch_native`.
3. Load the original FlexiDualGridVaeEncoder and FlexiDualGridVaeDecoder strictly using the official JSON settings and paired weights; do not replace model mathematics or use a full-model half cast.
4. Under `torch.inference_mode()`, call the encoder with `sample_posterior=False` to obtain the mean posterior. Preserve raw latent values without normalization or added noise.
5. Create a fresh SparseTensor from saved latent coordinates/features. Do not transfer the encoder's ground-truth sparse cache or decoder subdivision guides.
6. Set the decoder's public resolution to 1024. Bind the original eval extraction to the two native HIP hash operations in the process, then execute the original decoder to obtain a raw mesh.
7. Remove observer hooks and retained references, collect once, synchronize and empty the cache once at final cleanup, then return naturally.

The complete historical evidence-bound launchers are deliberately excluded because they embed private paths, character contracts and protection receipts. This source release therefore does not advertise a standalone `run_inference` command. The new `sphere_smoke.py` wrapper supports replay against an independently installed existing backend; the required adapted implementation and its notices are now included, and the new-source/rebuilt-extension replay passed, while a complete fresh dependency installation remains unverified. It must be run in a fresh process with operator-supplied model, target, reference and SDK paths. Only synthetic-sphere inputs are used for the release verification.

## Existing accuracy evidence

See [VALIDATION.md](VALIDATION.md). These are copied historical metrics, not new release measurements.

## Limits

- This release covers inference only. The `torch_native` sparse convolution rejects gradient-enabled execution and is forward-only; it cannot train the shape SC-VAE.
- It supports odd-kernel, stride-one submanifold convolution. CPU fallback, inverse convolution and unsupported kernel/stride configurations are not offered.
- No complete CuMesh, nvdiffrast or FlexGEMM extension is available through this AMD port. It cannot run official `o_voxel.postprocess.to_glb` remesh / UV / baking.
- The two HIP hash operations use the original default-stream contract. They are not the entire O-Voxel GPU producer or a claim of arbitrary-stream safety.
- Strict import isolation for unused pipeline / texture functionality is required; lazy encoder imports alone do not install missing decoder dependencies.
- This result concerns fixed O-Voxel-to-VAE round trips, not image conditioning, three-view generalization, perceptual acceptance or tangent-space normal-map seams.

Original licenses for included upstream-derived files are preserved under `licenses/`. The included adapted FlexGEMM source carries its original copyright notice and complete MIT license intact; newly authored adapters and documents use the approved MIT license.

## Synthetic-sphere replay command

The following wrapper reads an existing official sphere B target and the separately held historical raw latent / decoded arrays. Its comparisons are exact array replay checks; it does not recalculate ray metrics or establish a new scientific result. Use a new output directory for every run. The complete collection of model and backend paths must be supplied explicitly.

```powershell
python -I -B -X utf8 sphere_smoke.py --repo ../upstream/Pixal3D --voxel-package ../installed/o_voxel_cpu --extension-dir ../installed/hip_hash --sdk ../installed/rocm_sdk --target ../sphere-reference/target.vxz --encoder-config ../models/shape_enc_next_dc_f16c32_fp16.json --encoder-weights ../models/shape_enc_next_dc_f16c32_fp16.safetensors --decoder-config ../models/shape_dec_next_dc_f16c32_fp16.json --decoder-weights ../models/shape_dec_next_dc_f16c32_fp16.safetensors --expected-latent ../sphere-reference/raw_latent.npz --expected-decoded ../sphere-reference/decoded_representation.npz --output ../run-output/sphere-replay
```

Add `--check-inputs` first to verify path presence without importing Torch or running GPU work. The wrapper rejects an existing output directory, enforces write isolation, uses the official mean-posterior / fresh decoder container contract, and records array-match booleans without private input paths. The historical local replay, fresh-source compilation and a fresh dependency installation are separate acceptance items. The baseline ray numbers remain those copied in VALIDATION.md.

## Completed release replay verification

**`LOCAL_BACKEND_SPHERE_REPLAY = PASS`.** The actual GPU worker returned exit code 0 and passed normal cleanup. Raw latent and decoded representation arrays exactly matched the existing Stage10A synthetic-sphere reference. The replayed C/ALL ray-metric object also exactly matched the original record. No new geometric conclusion was added.

**`FRESH_SOURCE_BUILD_AND_SPHERE_REPLAY = PASS`.** The included patch and convolution overlay were validated in a new pinned pristine source copy. The included API/header and HIP kernel wrapper compiled successfully, and an isolated GPU worker loaded the rebuilt extension with the new model source. Its raw latent and decoded arrays exactly matched the historical sphere reference; the resulting mesh was byte-identical to the previously ray-measured synthetic replay. The worker returned exit code 0, normal cleanup passed, and original input metadata remained unchanged. No additional ray measurement was needed.

The released version-header helper passed: original template content and version tokens matched the historical headers; only the historical explanatory comment preamble differed. See the corresponding flags in [REPLAY_VERIFICATION.json](../examples/validation/REPLAY_VERIFICATION.json).

The clean CPU evaluation installation and original fixed-camera SOURCE identity check passed separately. See [the compact verification record](../examples/validation/REPLAY_VERIFICATION.json). Its expected numeric values are copied from `STAGE10A_VAE_LOSS_DIAGNOSIS_RESULT.md`, current findings item 2 and A1; they remain historical values.

**`FRESH_AMD_DEPENDENCY_INSTALLATION = NOT_VERIFIED`.** The fresh-source build and replay reused the existing Torch/HIP installation, CPU O-Voxel I/O package, SDK/toolchain and separately held official weights. These checks establish source/build replay compatibility in that existing environment, without establishing a complete new dependency installation. Only the procedural SOURCE sphere and compact verification summary are distributed; the verification's temporary predicted mesh, latent, arrays and cache are not needed in this public package. `USER_VISUAL_ACCEPTANCE = PENDING` is unchanged.
