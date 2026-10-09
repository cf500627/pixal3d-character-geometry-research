# Existing findings: representation, VAE, and post-processing

This is a release summary of completed research and inference tools. It is not a character-generation product, a fine-tuned model, a training recipe proven to fit the local GPU, or a claim of user-accepted visual quality. **USER_VISUAL_ACCEPTANCE = PENDING.** All numbers below are copied from the existing reports listed in [SOURCES.md](SOURCES.md); no new measurement or conclusion is introduced by release preparation.

The measurements used three commercial stylized character models, Char-A / Char-B / Char-C, excluded with all derived data. The later parameter sweep tested only Char-A and Char-C. A synthetic sphere was used as a separate sanity control.

## Measurement definitions

S is the existing SOURCE reference; A is the existing V2 @1024 mesh; B is the official O-Voxel producer/direct geometry path; C is B passed through the pretrained shape SC-VAE, using mean posterior and a fresh decoder boundary. B used the producer's position and intersection flags and its original quantization/VXZ path; it did not fabricate a seventh splitweight. C used the decoder's actual output. This distinction matters when interpreting the B-to-C change. Source: **R9CR, `範圍、門檻與分母`**.

The fixed ray protocol uses SOURCE-visible pixels and inherited masks. At resolution 1024, `h = 1/1024 = 0.0009765625` world. The inherited thresholds are `T_normal = 15.17005233274145°` and `T_depth = 0.00010808482590720644` world, corresponding to `0.1106788617289794h`. The diagnostic `0.11h` threshold is slightly different and must not be substituted for T_depth. Unoriented normal angle is `acos(abs(dot))`; it removes winding sign, does not prove the same local sheet was hit, and does not generally remove displacement sensitivity. Source: **R9CR, `範圍、門檻與分母`**.

The Stage9C-R absolute-depth tables include target misses as positive infinity in the SOURCE-visible denominator. Stage10D signed-depth quantiles instead condition on finite both-hit rays and report misses separately. These definitions are not interchangeable. The miss-or->2h rate is a ray-error proxy, not proof of a physical hole. Sources: **R9CR, `範圍、門檻與分母`; R10D-NUM, opening definitions**.

## Representation and pretrained VAE round-trip

The following values are copied from the `ALL` rows of **R9CR, `全部可見像素：法線與破洞診斷` and `全部可見像素：深度分布`**. Normal failure is above the inherited T_normal; depth p95 is absolute first-hit error in h.

| ROI | A unoriented normal failure | B unoriented normal failure | C unoriented normal failure | A depth p95 h | B depth p95 h | C depth p95 h |
|---|---:|---:|---:|---:|---:|---:|
| Char-A FACE | 2.179% | 7.412% | 18.727% | 0.031032 | 0.225903 | 6.198786 |
| Char-A HAIR | 2.135% | 10.011% | 17.124% | 0.030581 | 0.352983 | 2.601251 |
| Char-B SHOE | 4.778% | 20.657% | 21.482% | 0.063040 | 0.450488 | 1.871778 |
| Char-C SHOE | 8.423% | 21.200% | 26.305% | 0.133999 | 0.508621 | 2.532032 |
| Char-A BODY control | 1.039% | 2.545% | 9.741% | 0.016001 | 0.030211 | 0.430541 |

Orientation accounts for much of the original extreme normal score: B Char-A BODY was `87.529%` oriented failure and `2.545%` unoriented failure. The report gives `84.984` percentage points attributable to the sign distinction under this diagnostic. That does not repair winding or establish usable geometry. Source: **R9CR, `問題在哪裡`, item 1; `全部可見像素：法線與破洞診斷`, B BODY row**.

The historical labels `V2_GAIN_SMALL = false` and `VAE_LOSS_SMALL = true` are retained, not reclassified. R9CR explains that the latter rule saturates when its directed baseline failure is already high; it must not be presented as proof that actual VAE geometry loss is small. Source: **R9CR, `與原指標並列，原標籤不變`**.

### Array-level losses

These are copied from **R10A, B1 active voxels, B2 `ALL_AXES`, and B3 dual vertex error**. Recall and precision match full integer xyz coordinates, not row order. Flag mismatch is measured only on common cells. Vertex p95 is three-dimensional L2 in cell units, also only on common cells.

| Character | Active recall | Active precision | Common-cell flag mismatch, all axes | Dual vertex L2 p95, cell |
|---|---:|---:|---:|---:|
| Char-A | 96.353% | 95.298% | 7.397% | 0.718284 |
| Char-B | 95.812% | 94.641% | 7.652% | 0.811360 |
| Char-C | 96.788% | 95.698% | 7.353% | 0.885668 |

For the Char-A FACE finite-hit >2h cohort, the source report lists `36.534%` with a missing cell in the original B quad's full four-cell support, `25.341%` with a common-owner flag false negative, and `50.057%` with the specified vertex indicator. **These groups overlap and cannot be added into causal shares.** B/C triangulation, visibility and another-sheet hits remain outside an independent causal decomposition. Source: **R10A, B4, Char-A FACE row and interpretation immediately below the table**.

### Precision and synthetic sanity control

Full FP32 did not remove the existing character depth error. Char-A FACE absolute depth p95 was `6.198786h` in FP16 and `6.195709h` in FP32. The saved FP16/FP32 decoded-array comparison was active Jaccard `99.881%`, common-cell flag change `0.134%`, and vertex L2 p95 `0.002386 cell`. Source: **R10A, `A2` FP32 comparison, ALL depth table and saved-array paragraph**.

The separate synthetic sphere C had unoriented normal failure `0.154634%`, absolute depth p95 `0.032776h`, and miss-or->2h rate `0.162262%`. It was a subdivided icosahedron with `2,562` vertices and `5,120` faces, not a character-derived example. A successful simple control does not alone identify the cause of complex-character failures. Source: **R10A, `目前能確定的問題`, item 2; `A1：簡單封閉網格對照`**.

## AMD inference fidelity: same-target reference

Stage10B compared the same saved B target, mean-posterior encoder output, a raw-latent disk boundary, and decoder @1024, using FP16 body / FP32 I/O. No encoder ground-truth sparse cache was passed to the decoder. **PORT_FAITHFUL** applies only to the frozen same-target neural-output gate, not to every producer path or end-to-end character quality. Source: **R10B, `R1：同一 B target 的神經網路對照`**.

| Input | Active Jaccard | Flag change | Vertex L2 p95, cell | Historical gate |
|---|---:|---:|---:|---|
| Char-A | 99.904090% | 0.124523% | 0.002255804 | PASS |
| Char-B | 99.851868% | 0.171280% | 0.002784252 | PASS |
| Char-C | 99.906869% | 0.128822% | 0.002226522 | PASS |
| Synthetic sphere | 99.990029% | 0.007648% | 0.000985302 | PASS |

The preregistered gate used three times the existing FP16/FP32 reference differences: Jaccard loss at most `0.003558624744`, flag-change fraction at most `0.004017798308`, and vertex L2 p95 at most `0.007157967946` cell. Fractions here are not percentages. These are the source report's literal gate values. Source: **R10B, R1 gate paragraph**.

The following ray comparisons are copied from **R10B, `R1：原 Stage9C-R 射線與拓撲`**; arrows mean local AMD → official CUDA reference. They show the remaining geometry errors alongside the bounded port differences.

| ROI | Unoriented normal failure | Absolute depth p95 h | Miss-or->2h |
|---|---:|---:|---:|
| Char-A FACE | 18.7267% → 18.8052% | 6.198786 → 6.233937 | 8.6540% → 8.7129% |
| Char-A HAIR | 17.1243% → 17.1330% | 2.601251 → 2.611128 | 5.7273% → 5.7384% |
| Char-A BODY | 9.7412% → 9.7412% | 0.430541 → 0.430851 | 1.6863% → 1.6902% |
| Char-B SHOE | 21.4822% → 21.4115% | 1.871778 → 1.867245 | 4.6806% → 4.6629% |
| Char-C SHOE | 26.3052% → 26.3143% | 2.532032 → 2.517896 | 6.2943% → 6.2852% |

The independent official producer comparison used another bbox center/scale normalization and produced different targets; it was not included in the same-target neural gate. Later normalization control was labelled **NORMALIZATION_MATTERS** under its frozen ROI rule. For Char-A FACE, miss-or->2h was `8.7129% → 7.4367%`; for Char-C SHOE it was `6.2852% → 5.5675%`. This did not eliminate the existing error and is not evidence of an AMD kernel defect. Sources: **R10B, `官方 SOURCE producer 的獨立結果`; R10C, `D2 官方正規化對照`**.

## Post-processing is a separate loss stage

The complete official Stage10C to_glb path improved directed normal scores while increasing unoriented normal failure and absolute depth p95 in `10/10` ALL ROI comparisons. Neutral material was supplied only to satisfy the interface; it was not a material-quality result. Source: **R10C, `D1 實際執行`; `像素量測：原分層、原門檻`**.

The public projection parameter changes the observed signed offset. For Char-A B BODY, the signed median was `-1.101703h1024` with P0 project=0 and `-0.085617h1024` with P1 project=0.9. Signed depth is target_t minus SOURCE_t; negative means nearer the camera. See [POSTPROCESS_FINDINGS.md](POSTPROCESS_FINDINGS.md) for exact rows, face-count tradeoffs, resolution failures, and denominator restrictions. Source: **R10D, `SOURCE-visible 逐 ROI 結果（ALL）`, Char-A BODY B/P0 and B/P1 rows**.

Representation, VAE and post-processing errors are not additive independent causal budgets. Their meshes differ in support, triangulation, winding, first-hit visibility and sometimes normalization. The tables quantify the existing stage comparisons without claiming an exact percentage attribution to each cause.

## V2 and fixed-support learnability limits

The fixed-slot accounting in the existing three-target sample envelope gives **3,915** output scalar/logit channels. This is a provisional cost model, not an implemented complete neural interface, a universal capacity maximum, or a demonstrated future-data limit. The largest single output-buffer accounting was FP16/BF16 `23.984499 GiB` and FP32 `47.968998 GiB`; it excluded activations, backward and optimizer state. Source: **RFIXED, `一頁結論`, items 1–3; `A：容量、接口、原 dtype 與精度`**.

Rounding diagnostics recorded Char-C distinct-adjacent-event merges of `23` in FP32, `1379` in FP16 and `2042` in BF16. These are numerical/canonicalization risks, not a newly trained decoder comparison. Source: **RFIXED, A, fixed floating-point rounding table, Char-C rows**.

The bounded G3D LINK02 trial retained `5116/5116` correct patch counts and `15348/15348` correct event counts but ended with `51/20184` pointer errors, `72/5046` sign errors and `9` unreferenced patches. Free arc structure was not fully correct. The unchanged assembler rejected the raw prediction with `every patch token has at least one incidence`; there was no legal predicted PLY. No target-based pointer repair or oracle replacement was used. This demonstrates the importance of the structural validity gate in this specific bounded trial, not that every possible predictor is unlearnable. Source: **RG3D, `實測比較` and following assembler paragraph**.

The G-series trial used fixed support and a target-derived latent; it did not learn image conditioning, occupied cells, three-view generation, or a full character product. Source: **RG3D, final scope statement**.

## VAE training feasibility remains unproven

The local inference sparse backend explicitly refuses execution with gradients; missing render dependencies and the absent requested configuration blocked the Stage10A training probe. Denoiser training evidence is not VAE sparse-backward support. Source: **R10A, `C：訓練可行性探測 — BLOCKED`**.

The later official zero-update probe at 512 completed `5` finite forward/backward passes at loss scale `524288`, with peak allocated/reserved `19.05624/22.67969 GiB`. At 1024 the observed OOM occurred in an **additional master-gradient finite-QA allocation**, not the official forward/backward call itself; the source records a `792 MiB` request. Adam m/v were not allocated because optimizer.step was forbidden. These data do not prove that a complete optimizer step fits, or that official forward/backward itself cannot fit. Source: **R10C, `D3 零更新训练探測`, table, `1024 確切失敗點`, and Adam-state limitation**.

## Research boundaries

See [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) for the routes closed in these particular experiments and the unanswered questions. No tangent-space normal-map seam test is represented by TrueNormal geometry diagnostics. Visual acceptance, arbitrary-reference or three-view character generation, rigging and a usable avatar product remain outside this release's demonstrated result.
