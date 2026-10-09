# Draft only — not submitted

Repository: microsoft/TRELLIS.2

Proposed title: Example remesh_project=0 versus signature default 0.9: fixed-ray geometry observations

At upstream commit `75fbf0183001ed9876c8dbb35de6b68552ee08bd`, we compared the existing example setting `remesh_project=0` with the public signature default **0.9**, holding @1024 and a **1,000,000** face target. For two private stylized characters, official to_glb was unmodified; a constant neutral attr_volume satisfied the material interface and the full UV/baking path was retained.

Copied fixed-ray signed medians, in `h1024 = 1/1024` world:

| Input / ROI | project=0 | project=0.9 |
|---|---:|---:|
| Char-A direct O-Voxel / BODY | -1.101703 | -0.085617 |
| Char-A pretrained VAE / FACE | -1.37197 | -0.125466 |
| Char-C pretrained VAE / SHOE | -1.767727 | -0.209791 |

Signed error is target_t − SOURCE_t: negative means nearer the camera. Quantiles include finite both-hit rays only; misses retain the SOURCE-visible denominator and are reported separately. Source: `STAGE10D_OFFICIAL_POSTPROCESS_PARAMETER_SWEEP_RESULT.md`, §SOURCE-visible ALL, matching P0/P1 rows. Projection reduced observed bias, but did not uniformly resolve shape, misses or topology; higher face targets also had mixed results. See the release's `reports/POSTPROCESS_FINDINGS.md` for definitions and limitations.

Is the example's choice of project=0 intentional, and would a note explaining its geometry tradeoff be appropriate? This is a two-character observation, not a general benchmark or visual-quality claim. The commercial models and all derived data are not included; USER_VISUAL_ACCEPTANCE = PENDING. This draft has not been posted.
