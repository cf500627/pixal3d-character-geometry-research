# Existing AMD-versus-official inference comparison

The character comparison values are copied from `STAGE10B_OFFICIAL_CUDA_REFERENCE_RESULT.md`, section **R1: same B target neural comparison** and section **R1: original Stage9C-R rays and topology**. No character measurement was repeated for this public candidate. The synthetic sphere was replayed only for release verification, with exact agreement to the existing reference as described below.

The three anonymized cases are commercial stylized character models not included in this release. Char-A / Char-B / Char-C consistently identify the three existing character cases across the public reports. The sphere is a synthetic subdivided icosahedron projected radially, not a character-derived asset.

## Method

Use the exact same official 7-channel B target in both paths, official paired pretrained weights, mean posterior, raw latent, a fresh decoder SparseTensor and resolution 1024. FP16 model body and FP32 external I/O are retained. The comparison does not transfer ground-truth encoder sparse caches to the decoder. Active support Jaccard, common-cell flag changes and dual-vertex L2 p95 use the original array comparison definitions.

The frozen gate allowed three times the existing local FP16-versus-FP32 numerical baseline: Jaccard loss <= 0.003558624744; flag variation <= 0.004017798308; vertex L2 p95 <= 0.007157967946 cells. All four inputs satisfied all three gates. The recorded label **PORT_FAITHFUL** is limited to these fixed-target neural outputs and their allowed numerical variation.

| Input | Active Jaccard | Flag variation | Vertex L2 p95, cells | Historical gate |
| --- | ---: | ---: | ---: | --- |
| Char-A | 99.904090% | 0.124523% | 0.002255804 | PASS |
| Char-B | 99.851868% | 0.171280% | 0.002784252 | PASS |
| Char-C | 99.906869% | 0.128822% | 0.002226522 | PASS |
| Synthetic sphere | 99.990029% | 0.007648% | 0.000985302 | PASS |

Source: `STAGE10B_OFFICIAL_CUDA_REFERENCE_RESULT.md`, **R1: same B target neural comparison**, asset table and frozen upper limits paragraph.

## SOURCE-visible ray comparison

Reuse the original visible SOURCE pixels, fixed rays, masks and resolution-1024 audit classes. Unsigned normal angle is `acos(abs(dot))`; its threshold is 15.17005233274145 degrees. Depth uses first-hit absolute error in h=1/1024. Hole denotes target miss or absolute first-hit depth error >2h. No welding, face reorientation, smoothing, hole filling or remeshing is applied to the raw compared meshes.

| ROI | Unsigned-normal failure AMD -> official reference | Depth p95 AMD -> reference, h | Hole AMD -> reference |
| --- | ---: | ---: | ---: |
| Char-A FACE | 18.7267% -> 18.8052% | 6.198786 -> 6.233937 | 8.6540% -> 8.7129% |
| Char-A HAIR | 17.1243% -> 17.1330% | 2.601251 -> 2.611128 | 5.7273% -> 5.7384% |
| Char-A BODY | 9.7412% -> 9.7412% | 0.430541 -> 0.430851 | 1.6863% -> 1.6902% |
| Char-B SHOE | 21.4822% -> 21.4115% | 1.871778 -> 1.867245 | 4.6806% -> 4.6629% |
| Char-C SHOE | 26.3052% -> 26.3143% | 2.532032 -> 2.517896 | 6.2943% -> 6.2852% |

Source: `STAGE10B_OFFICIAL_CUDA_REFERENCE_RESULT.md`, **R1: original Stage9C-R rays and topology**, ROI comparison table. Arrow pairs are retained instead of calculating new differences.

Similarity to the official neural outputs does not mean the character geometry is good. These same raw outputs still have substantial normal, depth and topology failures. The SOURCE producer comparison separately differed because the official data toolkit applied a second bounding-box center/scale; it was not mixed into the neural gate.

## Existing synthetic-sphere control

A radius-0.25 sphere was generated from a regular icosahedron with four midpoint subdivisions followed by radial projection: 2,562 vertices and 5,120 faces. SOURCE-visible pixels: 629,228 at the fixed 2048 camera.

| Arm | Depth median, h | Depth p95, h | Unsigned normal failure | Miss or >2h |
| --- | ---: | ---: | ---: | ---: |
| B, direct official target extraction | 0.002538 | 0.012051 | 0.001% | 0.001% |
| C, pretrained VAE round trip | 0.006774 | 0.032776 | 0.154634% | 0.162262% |

Source: `STAGE10A_VAE_LOSS_DIAGNOSIS_RESULT.md`, **A1: simple closed mesh control** (depth table), and **currently established problems**, item 2 (unrounded C failure values). Percent precision follows the original source: B was reported rounded to three decimal places. These numbers are copied historical expected-reference values. The completed release replay is documented separately by exact-match booleans in [REPLAY_VERIFICATION.json](../examples/validation/REPLAY_VERIFICATION.json); no newly measured numeric table or conclusion replaces the original record.

## Release replay result

**`LOCAL_BACKEND_SPHERE_REPLAY = PASS`.** Using the existing synthetic-sphere B target, separately installed original model code and unchanged official pretrained weights, the new wrapper reproduced the historical raw latent and decoded arrays exactly. The original C/ALL ray-metric object also matched exactly. The actual GPU worker exited with code 0 and normal GPU cleanup passed. The compact [verification record](../examples/validation/REPLAY_VERIFICATION.json) contains these observed replay checks without private paths, weights or audit receipts.

**`FRESH_SOURCE_BUILD_AND_SPHERE_REPLAY = PASS`.** A new source copy from the pinned Pixal3D commit accepted the included patch and convolution overlay. The included API/header and HIP kernel source were freshly compiled, and a separate GPU worker used that new source and rebuilt extension. Its latent and decoded arrays matched the historical sphere reference exactly; the resulting mesh was byte-identical to the previously ray-measured synthetic replay. The worker exited with code 0, normal cleanup passed and original input metadata was unchanged. These flags are recorded in [REPLAY_VERIFICATION.json](../examples/validation/REPLAY_VERIFICATION.json). No new ray measurement was required for the byte-identical mesh.

The released version-header generator passed; original template content and version tokens matched the historical headers, with only the original explanatory comment preamble differing. The independent clean CPU evaluation installation and fixed-camera SOURCE identity check also passed.

**`FRESH_AMD_DEPENDENCY_INSTALLATION = NOT_VERIFIED`**: the source/build replay reused the existing Torch/HIP environment, CPU O-Voxel I/O, SDK/toolchain and separately held official weights. No character was regenerated, no weights were updated and no new research conclusion was added.

The public candidate retains the procedural SOURCE sphere and compact summary, rather than the replay's temporary predicted mesh, latent, decoded arrays or cache. `USER_VISUAL_ACCEPTANCE = PENDING` remains separate from numerical compatibility.
