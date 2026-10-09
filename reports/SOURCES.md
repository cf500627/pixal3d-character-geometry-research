# Sources for the release excerpts

This release copies selected numbers and existing interpretations from completed research reports. It performs no new experiment, ray measurement, numerical aggregation, or causal attribution. Original reports containing private paths, operational receipts, or asset-derived data are not redistributed. Source references below identify the original report filename and section; the public excerpts appear in the linked release reports.

The measurements used three commercial stylized character models that are **not included in this release**, identified only as Char-A, Char-B, and Char-C. These aliases are consistent across the release. The post-processing parameter sweep covered Char-A and Char-C; the earlier representation and VAE comparisons covered all three. A synthetic sphere is a separate control, not a commercial character.

| Reference | Existing source filename | Source section or table | Public excerpt |
|---|---|---|---|
| R9CR | `STAGE9CR_ORIENTATION_DEPTH_RESULT.md` | `範圍、門檻與分母`; `全部可見像素：法線與破洞診斷`; `全部可見像素：深度分布`; `與原指標並列，原標籤不變` | [Findings](FINDINGS.md), [post-processing](POSTPROCESS_FINDINGS.md) |
| R10A | `STAGE10A_VAE_LOSS_DIAGNOSIS_RESULT.md` | `A1：簡單封閉網格對照`; `A2` FP32 comparison; `B1`, `B2`, `B3`, `B4`; `C：訓練可行性探測 — BLOCKED` | [Findings](FINDINGS.md) |
| R10B | `STAGE10B_OFFICIAL_CUDA_REFERENCE_RESULT.md` | `R1：同一 B target 的神經網路對照`; `官方 SOURCE producer 的獨立結果`; `R1：原 Stage9C-R 射線與拓撲` | [Findings](FINDINGS.md), [Pixal3D issue draft](../drafts/issues/PIXAL3D_AMD_WINDOWS_AND_GEOMETRY.md) |
| R10C | `STAGE10C_OFFICIAL_REMESH_NORMALIZATION_TRAINING_RESULT.md` | `D1 實際執行`; `像素量測：原分層、原門檻`; `D2 官方正規化對照`; `D3 零更新训练探測` | [Findings](FINDINGS.md), [post-processing](POSTPROCESS_FINDINGS.md) |
| R10D | `STAGE10D_OFFICIAL_POSTPROCESS_PARAMETER_SWEEP_RESULT.md` | Opening limitations; parameter definitions; `SOURCE-visible 逐 ROI 結果（ALL）`; `全角色拓撲（絕對值）` | [Post-processing](POSTPROCESS_FINDINGS.md), [TRELLIS.2 issue draft](../drafts/issues/TRELLIS2_REMESH_PROJECTION.md) |
| R10D-NUM | `NUMERIC_COMPARISON_ALL_GROUPS01.md` | Opening measurement definitions; each anonymous character/arm table, ROI `ALL` rows; whole-character indexed topology tables | [Post-processing](POSTPROCESS_FINDINGS.md) |
| R10D-FAIL | `P3_GLB_FAILURE_FINDINGS.md` | Opening diagnosis and POSITION/NaN table | [Post-processing](POSTPROCESS_FINDINGS.md), [open questions](OPEN_QUESTIONS.md) |
| RFIXED | `V2_1024_FIXED_CHANNEL_DIAGNOSTICS_RESULT.md` | `一頁結論`; `A：容量、接口、原 dtype 與精度` | [Findings](FINDINGS.md), [open questions](OPEN_QUESTIONS.md) |
| RG3D | G3D LINK02 `RESULT.md` | `實測比較`; `本次具體改動與邊界`; final scope and stop statement | [Findings](FINDINGS.md), [open questions](OPEN_QUESTIONS.md) |
| R8G8 | `STAGE8G8_RESIDUAL_MESHLET_RESULT.md` | Opening conclusion; `必答結果`; `SHOE：合法介面與失敗品質分開`; `完整candidate topology（既有壞項沒有隱去）` | [Open questions and closed routes](OPEN_QUESTIONS.md) |
| R9A | `STAGE9A_REPRESENTATION_ORACLE_RESULT.md` | `主要發現`; `同一 field 的提取控制`; `完整固定 ROI 的診斷結果`; `最終欄位` | [Open questions and closed routes](OPEN_QUESTIONS.md) |
| R9A-HYBRID | `HYBRID_VECTOR_OCCUPANCY_ORACLE.md` | Synthetic limitation and `FIELD_TO_MESH_EXTRACTION_QA=FAIL` statement | [Open questions and closed routes](OPEN_QUESTIONS.md) |
| RREFINE | `REFINEMENT_CEILING_RESULT.md` | Main result table: `A0 result`, `A1 result`, `A2 result`, `FACE`, `REFINEMENT_FEASIBLE`, `Recommended next step` | [Open questions and closed routes](OPEN_QUESTIONS.md) |

No SHA audit receipts, material inventories, private operational logs, original comparison images, per-pixel arrays, targets, latents, character meshes, or model weights accompany these excerpts. Public aggregate tables retain reported precision; no new rounding-based statistics or estimates are introduced.
