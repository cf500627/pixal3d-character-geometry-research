# Third-party notices and release licensing status

This is a research source release with **PUBLICATION = PUBLISHED**.
The user has authorized public repository creation and push of the reviewed
package. Remote inventory, source bytes and anonymous access have been verified.
The public repository is
[pixal3d-character-geometry-research](https://github.com/cf500627/pixal3d-character-geometry-research).
The user has approved the
root MIT license for project-authored code and documentation, retaining the
contributors attribution. The root license does not replace upstream licenses
or grant permission to redistribute commercial character assets or model weights.

The table below was checked against actual local license files and package
metadata during release preparation. The source locations are symbolic,
portable references; workstation paths, package metadata containing personal
addresses and private audit records are not included. No license was inferred
from a package name or from memory.

## Included upstream-derived files

| Component and pinned version | Included files | Verified license and attribution | License evidence retained in this release |
| --- | --- | --- | --- |
| TencentARC/Pixal3D, commit `f7cf38429b0bd264f1995f0f8743a88b1c728b94` | `amd_windows_port/patches/Pixal3D_inference_imports_and_backend.patch` | MIT; Copyright (c) 2026 Tencent. Project-authored changes use the approved root MIT license. | `amd_windows_port/licenses/Pixal3D/LICENSE` and original `NOTICE`, copied unchanged from the local Pixal3D checkout. |
| microsoft/TRELLIS.2, commit `75fbf0183001ed9876c8dbb35de6b68552ee08bd` | `amd_windows_port/hip_hash/src/hash.cu`, `hash.cuh`, `vendor/flexible_dual_grid.py`, and `patches/TRELLIS2_hash_hipify.patch` | MIT; Copyright (c) Microsoft Corporation. The package-level license is retained even where an individual original source file has no copyright header. | `amd_windows_port/licenses/TRELLIS.2/LICENSE`, copied unchanged from the archived local upstream baseline `stage7e_decoder_mesh/backend/LICENSE.upstream`; a second local upstream checkout also contained the same Microsoft MIT text. |
| FlexGEMM, commit `6dd94a859c26ee8246888502eada3dd8ad85532e` | `amd_windows_port/overlay/pixal3d/modules/sparse/conv/conv_torch_native.py`, the existing forward-only adapted convolution | MIT; the original Jianfeng Xiang copyright and author contact are retained in the source and license. Project-authored adaptation remains under MIT. | `amd_windows_port/licenses/FlexGEMM/LICENSE`, copied unchanged from the actual local `stage4c/vendor/FlexGEMM/LICENSE`; the adapted source contains the same MIT terms and explicit pinned provenance. |
| O-Voxel hash API header at the pinned TRELLIS.2 baseline | `amd_windows_port/hip_hash/src/api.h` | MIT, as explicitly stated by the unchanged header; original Jianfeng XIANG copyright and author contact retained. | `amd_windows_port/hip_hash/LICENSE` retains the actual author's MIT license text; the Microsoft TRELLIS.2 package license is separately retained. This author notice does not replace Microsoft attribution for the other hash/conversion files. |

The HIP hash source remains upstream CUDA source for PyTorch's HIP translation.
The HIPify patch is a separate mechanical translation record. Mathematical
source attribution is not a claim that all O-Voxel functionality is ported.

The user has authorized preservation of public upstream author email addresses
only in original copyright, LICENSE and NOTICE text. The API header and the
forward-only adapted sparse convolution are included with their original
notices intact. No address is stripped or added to project contact information.
This narrow notice exception does not authorize private email, account,
credential or operational-log disclosure. A clean build or runtime validation
is a separate gate; licensing approval alone does not establish that gate.

The privacy check admits an email only at the original copyright line of the
following exact files: the adapted convolution, `licenses/FlexGEMM/LICENSE`,
`hip_hash/src/api.h`, and its unchanged author-license copy `hip_hash/LICENSE`,
all relative to `amd_windows_port/`. The line text must match the actual local
original. Other email occurrences remain rejected; there is no directory-wide
or address-wide exception.

## Runtime and build dependencies (installed separately, not bundled)

These licenses govern independently obtained dependencies. No wheel, DLL,
header archive or runtime installation is bundled. The selected upstream source
files in the preceding table are the only corresponding vendored components.
Versions below are the actual locally inspected package versions or the
historically pinned component versions stated in the named existing report.

| Dependency | Verified version | Verified terms | Actual local evidence inspected (symbolic path) | Use / distribution status |
| --- | --- | --- | --- | --- |
| CPython | 3.12.14 | Python Software Foundation License Version 2, with historical incorporated-license sections; documentation examples have the stated dual PSF / 0BSD terms. | `python/LICENSE.txt`, sections A and B; actual local interpreter version. | Standard-library runtime; not bundled. |
| NumPy | 2.5.3 | Core BSD-3-Clause; package metadata expression `BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0`. The installed binary license also lists OpenBLAS BSD-3-Clause, LAPACK BSD-3-Clause-Open-MPI and GCC runtime GPL-3.0-or-later WITH GCC-exception-3.1. Component-specific terms remain in the independently installed package. | `numpy-2.5.3.dist-info/METADATA`, `licenses/LICENSE.txt`, and the metadata-listed component license files. | CPU evaluation and V2 numerical routines; not bundled. |
| PyTorch (Windows ROCm distribution) | 2.9.1+rocm7.2.1 | BSD-3-Clause for the main project, with bundled third-party terms documented by its full LICENSE and NOTICE. | `torch-2.9.1+rocm7.2.1.dist-info/METADATA`, `licenses/LICENSE`, `licenses/NOTICE`. | AMD inference / native-extension build runtime; not bundled. |
| setuptools | 84.0.0 | MIT for the main project; separately installed vendored components retain their own terms. | `setuptools-84.0.0.dist-info/METADATA`, `licenses/LICENSE`. | `hip_hash/setup_hash.py` build dependency; not bundled. |
| Pillow | 12.3.0 | MIT-CMU for Pillow/PIL; the installed wheel's LICENSE contains additional codec/library notices. | `pillow-12.3.0.dist-info/METADATA`, `licenses/LICENSE`, main Pillow/PIL section and bundled-library sections. | Optional historical render/image inspection dependency; not required by the released V2 assembler; not bundled. |
| safetensors | 0.6.2 | Apache-2.0. | `safetensors-0.6.2.dist-info/METADATA`, `licenses/LICENSE`, Apache License Version 2.0 text. | Independently downloaded official model loading; no weights or package bundled. |
| tqdm | 4.70.1 | MPL-2.0 AND MIT, as stated by installed metadata and author/file exceptions in LICENCE. | `tqdm-4.70.1.dist-info/METADATA`, `licenses/LICENCE`. | Optional upstream runtime dependency; not bundled. |
| rocThrust | 4.2.0, `rocm-7.2.1`, commit `ed551d53d9bac8fd55b2a7fc62683946e33060a0` | Apache-2.0 for the component; NOTICES also records incorporated dependencies. | `stage7e_decoder_mesh/backend/deps/rocThrust/LICENSE` and `NOTICES.txt`; version/commit from `STAGE7E_BACKEND_PATCH_LOG.md`, first-party dependencies table. | Independently obtained HIP build headers; not bundled. |
| rocPRIM | 4.2.0, `rocm-7.2.1`, commit `a272f74a01fa2160763122f85ade1b411f407924` | MIT; Copyright (C) Advanced Micro Devices, Inc.; component NOTICES retain additional attribution. | `stage7e_decoder_mesh/backend/deps/rocPRIM/LICENSE.md` and `NOTICES.txt`; version/commit from `STAGE7E_BACKEND_PATCH_LOG.md`, first-party dependencies table. | Independently obtained HIP build headers; not bundled. |
| HIP compiler driver (hipcc) | ROCm SDK 7.2.1 environment; historical HIP 7.2.53211-158bd99533 toolchain | MIT for the locally installed hipcc component. This does not establish one license for the entire ROCm SDK. | `_rocm_sdk_core/share/doc/hipcc/LICENSE.txt`, exact AMD MIT terms; toolchain version from `STAGE4B_SUMMARY.md` and `STAGE7E_BACKEND_PATCH_LOG.md`. | Toolchain installed independently; not bundled. |
| AMD Comgr | ROCm SDK 7.2.1 environment; separate Comgr component version not established | Apache-2.0 WITH LLVM-exception for the locally installed component. | `_rocm_sdk_core/share/doc/amd_comgr/LICENSE.txt`, opening license declaration and text. | Toolchain component installed independently; not bundled. |

Installed dependency license texts may contain original attribution, addresses
and license terms. They are left intact in the independently obtained package,
not copied into this release or edited to remove attribution. The runtime
dependencies' terms do not automatically change the license of separately
authored project code.

## Acknowledged or excluded projects

| Project | License verification / status | Packaging decision |
| --- | --- | --- |
| Direct3D-S2 | The actual local Pixal3D NOTICE lists Direct3D-S2 under MIT and attributes DreamTech. A dedicated Direct3D-S2 source LICENSE and revision were not established in this release selection. | Acknowledgement only; no Direct3D-S2 code or weights redistributed. Any future vendoring requires its own actual source/license review. |
| Full FlexGEMM extension | The selected adapted convolution and actual local MIT license are listed above; their required original author notice is retained under the approved exception. | The complete FlexGEMM extension remains absent. The selected forward-only compatibility module does not add sparse backward, full extension support or VAE training. |
| nvdiffrast | Not included. No license claim is needed or made for absent code. | Excluded as explicitly required; no source, binaries or rewritten substitute distributed. |
| CuMesh | Not included in the AMD port. Dedicated redistribution terms were not established for inclusion. | Excluded; no code, binaries or substitute implementation distributed. |
| Trimesh | No installed package/license was established in the inspected inference environment and no released module imports it. | Not a declared dependency; excluded. |
| DINOv3, RMBG-2.0, official shape VAE and G-series checkpoints | Model redistribution terms were not inferred from repository code licenses. | No weights or checkpoints distributed. Official model links are supplied separately where needed. |
| Commercial character models and all derived data | No redistribution permission established or claimed. | All original models, reconstructions, targets, latents, renderings, comparison pages with their images, per-pixel arrays and NPZ files are excluded. |

## File-level license mapping

`FILE_PROVENANCE.csv` is the authoritative per-file map for the source release.
The following rules apply and must agree with that map:

- The explicitly enumerated Tencent patch and original Tencent license/NOTICE
  retain Tencent attribution and original MIT terms.
- The explicitly enumerated Microsoft hash/conversion source, translation
  patch and original Microsoft LICENSE retain Microsoft MIT attribution.
- The explicitly enumerated adapted convolution and author-specific API header
  retain their original MIT copyright and author-license texts. The separate
  author license does not supersede the retained Tencent or Microsoft notices.
- All other project-authored adapters, evaluation tools, V2 implementations,
  reports, examples, configuration, release documentation, issue drafts and
  provenance/checklist files use the **approved root MIT license**, with the
  contributors attribution retained.
- Runtime dependencies, native headers and any excluded file have no
  redistribution entry as bundled package code.

No unresolved third-party source is accepted merely because the root license
is MIT. Unknown native-header/QEF provenance and independently unverified
third-party sources remain excluded. Owner authorization covers public repository
creation and push of the reviewed source package; it does not authorize submission
of the upstream issue drafts or separate public posts.
