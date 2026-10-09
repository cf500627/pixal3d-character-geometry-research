# Official post-processing parameters: existing findings

This report republishes existing Stage9C-R, Stage10C and Stage10D findings. It does not run a new sweep or choose a winning setting. The parameter sweep used **two** commercial stylized character models, Char-A and Char-C, excluded together with all derived data. The earlier direct/round-trip study used **three** such models. **USER_VISUAL_ACCEPTANCE = PENDING.** Sources are identified by filename and section in [SOURCES.md](SOURCES.md).

## Protocol and parameter groups

S denotes SOURCE; B denotes the official direct O-Voxel geometry; C_CUDA denotes the official pretrained shape SC-VAE raw mesh; C_OFFNORM denotes the existing official-normalization raw mesh transformed back to SOURCE coordinates. P0 was reused, not rerun. A neutral constant material only satisfied to_glb's attribute interface; the complete official path still included UV processing and baking. Sources: **R10C, `D1 實際執行`; R10D, opening parameter definitions**.

| Group | Resolution | remesh_project | decimation_target | Existing study status |
|---|---:|---:|---:|---|
| P0 | 1024 | 0 | 1,000,000 | Reused official-example setting |
| P1 | 1024 | 0.9 | 1,000,000 | Public function-signature projection default |
| P2 | 1024 | 0.9 | 4,000,000 | Higher public face target |
| P3 | 1536 | 0.9 | 1,000,000 | True producer/VAE inputs at this resolution |

The table restates the registered groups in **R10D, opening parameter definitions**. The successful optional `P2_NO_SIMPLIFY` output is listed under its existing study name below; it is not a newly selected recipe. P0 and later jobs ran on different NVIDIA hardware, so their elapsed time and peak memory do not form a controlled same-hardware performance comparison. Source: **R10D, opening limitations**.

Camera, SOURCE visibility, mask and @1024 NONE/CONFLICT classifications were retained. `h1024 = 1/1024` world; `T_normal = 15.17005233274145°`; `T_depth = 0.00010808482590720644` world. The comparison keeps the >2h threshold at **2/1024 world**, including P3; it does not recalibrate it to native 1536 grid width. Normal failure is `acos(abs(dot)) > T_normal`. This ignores winding sign but does not guarantee insensitivity to positional change. Sources: **R9CR, `範圍、門檻與分母`; R10D, depth/normal definitions; R10D-NUM, opening definitions**.

Signed depth is **target_t − SOURCE_t** along unit first-hit rays. Positive is farther from the camera and negative is nearer. Signed median/IQR/p95−median use finite both-hit rays only; target misses are counted separately with the original SOURCE-visible denominator. A negative shift is not, by itself, proof of globally outward displacement. The unsigned Stage9C-R depth p95 uses another definition and must not be read as signed bias. Sources: **R9CR, `範圍、門檻與分母`; R10D, signed-depth definitions**.

## Projection: observed signed shift

Exact signed medians are copied from **R10D, `SOURCE-visible 逐 ROI 結果（ALL）`, B and C_CUDA P0/P1 rows**. All entries use h1024.

| Character ROI | Arm | P0: project=0 | P1: project=0.9 |
|---|---|---:|---:|
| Char-A BODY | B | -1.101703 | -0.085617 |
| Char-A FACE | B | -1.353588 | -0.110712 |
| Char-A HAIR | B | -1.352122 | -0.09897 |
| Char-C SHOE | B | -1.677655 | -0.155634 |
| Char-A BODY | C_CUDA | -1.099688 | -0.079337 |
| Char-A FACE | C_CUDA | -1.37197 | -0.125466 |
| Char-A HAIR | C_CUDA | -1.354256 | -0.108092 |
| Char-C SHOE | C_CUDA | -1.767727 | -0.209791 |

These rows support the existing report's statement that P1 reduced part of the systematic depth shift. They do not support a universal claim that project=0.9 puts every surface within 0.1 cell, or that its remaining geometry is acceptable.

The direction-versus-shape distinction was already visible in Stage10C: its `10/10` ALL comparisons improved directed normal failure but worsened unoriented normal failure and absolute depth p95. Example Char-A B FACE changed unsigned normal failure `7.4121% → 23.5912%` and miss-or->2h `1.3155% → 22.2609%` after the P0 official remesh. Source: **R10C, `像素量測：原分層、原門檻`, summary and D_B FACE/ALL row**.

## Raising face count: gains and costs coexist

The following values are literal existing rows, with no newly computed percent improvements. Pixel rows come from **R10D, `SOURCE-visible 逐 ROI 結果（ALL）`, Char-A FACE B/P1/P2/P2_NO_SIMPLIFY**. Topology rows come from **R10D-NUM, Char-A/B whole-character topology table**; counts and rates use actual final faces.

| Char-A B metric | P1 | P2 | P2_NO_SIMPLIFY |
|---|---:|---:|---:|
| Final faces | 949018 | 3955534 | 10799136 |
| FACE unoriented normal failure, % | 15.796191 | 13.793442 | 13.263303 |
| FACE signed median, h1024 | -0.110712 | -0.130695 | -0.13741 |
| FACE IQR, h1024 | 0.192098 | 0.087588 | 0.083714 |
| FACE p95−median, h1024 | 0.296513 | 0.094359 | 0.053284 |
| Non-manifold edges, absolute / per million faces | 1 / 1.054 | 5 / 1.264 | 122 / 11.297 |
| aspect>100, absolute / per million faces | 327 / 344.567 | 5474 / 1383.884 | 31830 / 2947.458 |
| flips>170°, absolute / per million faces | 146 / 153.843 | 3926 / 992.533 | 67 / 6.204 |

More faces did not uniformly improve the existing metrics. Char-A C_CUDA FACE unsigned normal failure was `20.228745%` at P1 and `20.272924%` at P2. For Char-A B BODY, combined missing/far rate was `0.376%` at P1 and `0.459%` at P2. Sources: **R10D, ALL table, Char-A FACE C_CUDA P1/P2; R10D-NUM, Char-A/B BODY ALL P1/P2 rows**.

For Char-C B SHOE, combined missing/far rate was `4.254%` at P2 and `4.29%` at P2_NO_SIMPLIFY. The optional result is therefore not a blanket geometry-quality win. Source: **R10D-NUM, Char-C/B SHOE ALL P2 and P2_NO_SIMPLIFY rows**.

Indexed topology contains UV-split vertices. Indexed boundaries or components alone are not proof of physical cracks; no position welding was introduced to improve those numbers. Source: **R10D-NUM, whole-character topology note; R10C, `全角色拓撲：絕對值及每百萬面`**.

## Resolution 1536: mixed C result and failed B exports

P3 used genuine 1536 producer/VAE inputs rather than relabelling or scaling 1024 output. Both B exports failed with `RuntimeError: Invalid GLB geometry`; existing serialized GLB diagnosis found `34` NaN vertex rows for Char-A and `42` for Char-C. Triangular indices were in range and the failures were not OOM. The report could not locate which intermediate operation first introduced NaN. This B path did **not** use the VAE. Sources: **R10D, opening conclusion and `未完成或證據缺口`; R10D-FAIL, opening POSITION/NaN table and diagnostic limitation**.

The following C_CUDA FACE/HAIR values are copied from **R10D, ALL table** and **R10D-NUM, Char-A/C_CUDA ALL rows**. P1 and P3 both use the one-million face target; h remains h1024.

| Char-A C_CUDA metric | P1 @1024 | P3 @1536 |
|---|---:|---:|
| FACE unoriented normal failure, % | 20.228745 | 14.750638 |
| FACE signed median | -0.125466 | -0.049584 |
| FACE IQR | 0.251716 | 0.243315 |
| FACE p95−median | 0.592346 | 4.917217 |
| FACE target misses | 0/20372 (0%) | 4/20372 (0.02%) |
| HAIR unoriented normal failure, % | 21.3635 | 16.39484 |
| HAIR target misses | 342/126674 (0.27%) | 844/126674 (0.666%) |

The existing Stage10D result remains **BLOCKED** because the required P3 B outputs failed, despite `20` successful new official post-process jobs out of `22`. No invalid mesh was repaired or substituted. Source: **R10D, opening conclusion**.

## Limitations of the reported finding

- This is the specified two-character sweep with fixed camera and visibility, not a universal parameter benchmark.
- Shape, orientation, bias, spread, misses and indexed topology describe different effects; there is no automatically selected winner.
- Conditioning on finite hits can change quantile populations; misses must remain visible alongside quantiles.
- C_OFFNORM has an existing RAW baseline, not an invented P0 normalized remesh. It was measured in SOURCE coordinates after recorded inverse normalization. Sources: **R10D-NUM, opening definitions; R10C, D2**.
- TrueNormal is a geometry diagnostic. Tangent-space normal-map seams, materials, rigging and user visual acceptance were not demonstrated.

Questions about project=1.0, NaN at 1536, decoder-only adaptation and orientation-only post-processing are [open](OPEN_QUESTIONS.md), not additional results.
