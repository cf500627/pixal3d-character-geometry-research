# Included inference changes

Pixal3D baseline: `TencentARC/Pixal3D` commit `f7cf38429b0bd264f1995f0f8743a88b1c728b94`.
TRELLIS.2 / O-Voxel baseline: `microsoft/TRELLIS.2` commit `75fbf0183001ed9876c8dbb35de6b68552ee08bd`.

| File | Change and reason |
| --- | --- |
| `pixal3d/models/sc_vaes/fdg_vae.py` | Move Mesh and extraction imports into the decoder forward. Encoder import no longer requires decoder-only geometry dependencies. The existing model forward mathematics remain unchanged. |
| `pixal3d/modules/sparse/config.py` | Accept the explicit `torch_native` opt-in. The default remains the upstream backend. The adapted implementation is supplied as an overlay, with its original FlexGEMM license intact. |
| `overlay/pixal3d/modules/sparse/conv/conv_torch_native.py` | Include the existing opt-in forward-only implementation without edits; it uses the original neighbor/GEMM semantics and bounded row chunks, with the full original author MIT notice. |
| `hip_hash/src/api.h` | Include the unchanged API declarations and original author copyright/MIT pointer; no kernel behavior changes. |
| `licenses/FlexGEMM/LICENSE`, `hip_hash/LICENSE` | Preserve the original complete MIT notice for adapted convolution and API author attribution. The original Microsoft package license remains separately included. |
| `o-voxel/src/hash.cu` | Archived PyTorch hipify translation: runtime includes and five CUDA launch spellings become HIP equivalents. Grid, block, arguments, stream, key encoding, probing and arithmetic are unchanged. |
| `hip_hash/bindings.cpp` | Expose only the two upstream operations called by evaluation extraction: insert 3-D coordinates with index as value, and lookup 3-D coordinates. The original source still contains its other kernels. |
| `hip_hash/src/hash.cu`, `hip_hash/src/hash.cuh` | Unmodified baseline source copies. Local build uses PyTorch HIP-aware CUDAExtension; the separate patch records the archived mechanical translation. |
| `hip_hash/vendor/flexible_dual_grid.py` | Unmodified upstream extraction wrapper, kept separate from the CPU producer package. |
| `hip_hash/native_mesh.py` | Process-only bindings to the two HIP operations. Portable relative source location and configured grid guard replace historical output-root and Shape256 guard; geometry mathematics are unchanged. |
| `hip_hash/setup_hash.py` | Packaging-only replacement for the historical build wrapper: SDK/dependency locations come from environment configuration. Compiler flags preserve the existing build flags. The included source was freshly compiled successfully in a new private source directory, followed by an isolated exact sphere replay with the rebuilt extension. Existing runtime dependencies were reused; this is not a new benchmark. |
| `prepare_header_versions.py` | Packaging-only helper: read the original ROCm component CMake version and templates, retain original license text, and write the original version substitution into a new output directory. No algorithm changes. The generated template content/version tokens were validated against the historical headers; only their explanatory comment preamble differed. |

Training patches, conditioning/DINO/NAF adaptations, render launchers and data ingest scripts are outside this inference release.

Original upstream licenses are under `licenses/`, with the API author notice also under `hip_hash/LICENSE`. MIT is approved for newly authored adapters and documents; contributors' signatures are retained. This approval does not relicense upstream material. Public author contact information is preserved only where it already appears in original LICENSE/NOTICE/copyright statements.

## Completed source/build verification

The compact [REPLAY_VERIFICATION.json](../examples/validation/REPLAY_VERIFICATION.json) records PASS for a new pinned pristine Pixal3D source copy, included patch and convolution overlay, freshly compiled included HIP API/kernel source, released version-header generation, and isolated sphere replay using the new source and rebuilt extension. Array values matched the existing sphere reference exactly; the mesh matched the previously ray-measured synthetic replay byte-for-byte. Natural worker exit code 0, normal cleanup and unchanged original input metadata were confirmed.

The existing Torch/HIP environment, CPU O-Voxel I/O, toolchain and official weights were reused. A complete fresh dependency installation remains **NOT_VERIFIED**. These are release replay checks, with no new character experiment or scientific conclusion.
