# Draft only — not submitted

Repository: TencentARC/Pixal3D

Proposed title: Windows AMD inference reference and a remesh projection observation

We prepared an inference-only Windows AMD research port using an RX 7900 XTX, Torch 2.9.1+rocm7.2.1 and HIP 7.2. Sparse convolution is forward-only; this does not provide shape SC-VAE training or the official to_glb remesh dependencies.

For the same saved O-Voxel target, mean-posterior encoder, latent disk boundary and decoder @1024, our Char-A local AMD versus official CUDA reference gave active Jaccard **99.904090%**, flag change **0.124523%**, and dual vertex L2 p95 **0.002255804 cell**. All three characters and a synthetic sphere passed the preregistered same-target gate. This does not claim universal backend equivalence or acceptable character quality. Source: `STAGE10B_OFFICIAL_CUDA_REFERENCE_RESULT.md`, §R1 same B-target neural comparison.

Separately, official post-processing with the example projection setting `remesh_project=0` gave Char-A B BODY signed first-hit median **-1.101703h1024**; changing only projection to **0.9** at the same one-million face target gave **-0.085617h1024**. Signed error is target_t minus SOURCE_t; negative means nearer the camera. The two-character sweep had mixed topology and detail outcomes, so this is not a universal parameter recommendation. Source: `STAGE10D_OFFICIAL_POSTPROCESS_PARAMETER_SWEEP_RESULT.md`, §SOURCE-visible ALL, Char-A BODY B/P0 and B/P1.

Would documentation of the inference backend boundary and the projection setting tradeoff be useful? Aggregate methods/findings can be shared; the three commercial stylized character models and all derived meshes, targets, latents and images are excluded. No weights are redistributed. USER_VISUAL_ACCEPTANCE remains PENDING.
