# Pixal3D Character Geometry and Windows AMD Inference Research

Existing research on character geometry representations, pretrained VAE
reconstruction losses, official post-processing, and Windows AMD inference
compatibility. This source release includes geometry evaluation tools, V2
representation readers, selected inference compatibility changes, and
anonymized findings. This is a research record and tool collection, not a
character-generation product. It contains
no fine-tuned model, model weights, training set, or commercial character data.
Release preparation performs no training or new research experiment.

**RELEASE_STATUS = RESEARCH_SOURCE_RELEASE; PUBLICATION = PUBLISHED.**
The owner has authorized creation of the public repository and publication of
this reviewed source package. The owner has approved MIT for
project-authored code and documents, with copyright attribution to
**Pixal3D Character Geometry Research contributors**. Required upstream
LICENSE/NOTICE/copyright statements may retain their public author email;
private personal and operational information remains excluded.
Complete fresh AMD dependency installation remains **NOT_VERIFIED**: licensing
approval does not establish an installation result. See [USER_DECISIONS.md](USER_DECISIONS.md).
See [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) for actual verification scope.

Public repository:
[pixal3d-character-geometry-research](https://github.com/cf500627/pixal3d-character-geometry-research).
The reviewed package is publicly available. The remote file inventory,
source bytes and anonymous public access have been verified.

## Five existing findings

Every value below is copied from an existing report, not measured for this release.
The source registry and original section names are in [reports/SOURCES.md](reports/SOURCES.md).

1. **Same-target AMD inference closely matched the official CUDA reference:**
   Char-A active-cell Jaccard **99.904090%**, flag change **0.124523%**, vertex
   L2 p95 **0.002255804 cell**. Source: `STAGE10B_OFFICIAL_CUDA_REFERENCE_RESULT.md`,
   `R1：同一 B target 的神經網路對照`, Char-A row. This is a bounded round-trip
   fidelity result, not proof of usable character geometry.
2. **Representation and VAE losses remain distinct:** Char-A FACE absolute
   depth p95 was **0.031032h / 0.225903h / 6.198786h** for V2 / official direct
   O-Voxel / pretrained VAE. Source: `STAGE9CR_ORIENTATION_DEPTH_RESULT.md`,
   `全部可見像素：深度分布`, FACE ALL rows.
3. **Similar cell counts conceal structural changes:** Char-A active recall
   **96.353%**, common-cell flag mismatch **7.397%**, vertex L2 p95
   **0.718284 cell**. Source: `STAGE10A_VAE_LOSS_DIAGNOSIS_RESULT.md`, B1/B2/B3.
4. **Projection changes the signed offset:** Char-A B BODY signed depth median
   changed **-1.101703h → -0.085617h** with `remesh_project=0 → 0.9`.
   Source: `STAGE10D_OFFICIAL_POSTPROCESS_PARAMETER_SWEEP_RESULT.md`,
   `SOURCE-visible 逐 ROI 結果（ALL）`, B/P0 and B/P1 BODY rows.
5. **V2 interface cost is still provisional:** the historical explicit field
   accounting reaches **3,915 channels**. This is an accounting assumption,
   not a universal maximum or an implemented complete neural interface.
   Source: `V2_1024_FIXED_CHANNEL_DIAGNOSTICS_RESULT.md`, `一頁結論` / section A.

## Windows AMD inference

The recorded environment was Windows 10 22H2, RX 7900 XTX, Python 3.12.14,
Torch 2.9.1+rocm7.2.1 and HIP 7.2. Historical versions and source sections,
installation instructions, official weight links, patch baselines, per-file
change reasons and R1 array/ray comparisons are in
[amd_windows_port/README.md](amd_windows_port/README.md),
[CHANGELOG.md](amd_windows_port/CHANGELOG.md) and
[VALIDATION.md](amd_windows_port/VALIDATION.md).

The supplied inference patches target TencentARC/Pixal3D
`f7cf38429b0bd264f1995f0f8743a88b1c728b94` and the HIP hash changes target
microsoft/TRELLIS.2 `75fbf0183001ed9876c8dbb35de6b68552ee08bd`.
`torch_native` sparse convolution is forward-only: this port cannot train
the shape SC-VAE. Full CuMesh / nvdiffrast / FlexGEMM extensions and official
`to_glb` remesh are unavailable in this AMD path. Their code is not bundled.
The synthetic packaging replay also passed using a new pristine pinned source
copy, the included patch and convolution overlay, and a freshly compiled HIP
hash extension. A new GPU worker used that source and rebuilt module: latent
and decoded arrays matched the existing Stage10A reference exactly, and the
mesh was byte-identical to the previous synthetic replay. The worker exited
successfully after normal cleanup. The exact scope is recorded in
[examples/validation/REPLAY_VERIFICATION.json](examples/validation/REPLAY_VERIFICATION.json).
This source/build check reused installed Torch/HIP, O-Voxel I/O and official
weights. A complete fresh AMD dependency installation remains **NOT_VERIFIED**.

## CPU synthetic example

Use a fresh Python 3.12 environment. No GPU, model download or character asset
is required. The example uses only the project-generated closed sphere from
Stage10A. Install the CPU dependency:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r eval_harness/requirements.txt
```

Follow [eval_harness/README.md](eval_harness/README.md) to compile the original
CPU measurement helper, set its location in a private configuration and replay
the fixed-camera identity control. The configuration contains relative paths;
runtime overrides select your own build/output locations. The historical
sphere has **2,562 vertices / 5,120 faces**, and **629,228 SOURCE-visible pixels**.
Source: `STAGE10A_VAE_LOSS_DIAGNOSIS_RESULT.md`, `A1：簡單封閉網格對照`.
Release checks are reproducibility/packaging checks, not additional scientific
findings. Research-only components and limits are listed in the tool README.

## V2 representation

[v2_representation/README.md](v2_representation/README.md) provides the original
pure validation, arc, assembly and FP32 triangulation functions with a schema
excerpt. Machine-bound launchers are omitted; assembly mathematics is preserved.
This is research code as provided, not a complete target producer or image model.
The fixed support/latent trials did not learn three-view conditioning or occupied
cells. LINK02 still had **51 pointer errors and 72 sign errors**, with **9 unused
patches**, and no legal free-decoded mesh. Source: G3D LINK02 `RESULT.md`,
`實測比較`. FP16/BF16 sensitivity and the scope of the provisional channel count
are documented in [LIMITATIONS.md](v2_representation/LIMITATIONS.md).

## Findings and open questions

- [Findings and loss definitions](reports/FINDINGS.md)
- [Post-processing projection, face budget and resolution](reports/POSTPROCESS_FINDINGS.md)
- [Closed routes and open questions](reports/OPEN_QUESTIONS.md)
- [Two unsubmitted issue drafts](drafts/issues/)

The open questions include direct B@1536 export NaNs, decoder-only fine-tuning,
`remesh_project=1.0` and orientation-only post-processing. None is tested during
release preparation. No automatic visual winner is selected.
**USER_VISUAL_ACCEPTANCE = PENDING.** Geometric TrueNormal checks do not validate
tangent-space normal-map seams.

## Data, licensing and acknowledgments

Measurements used **three commercial stylized character models not included in
this release**, anonymized as Char-A / Char-B / Char-C. No real-name mapping,
source inventory, character-derived mesh/target/latent/render/pixel array,
comparison page containing character images, or model weight is shipped.
Only the separately generated synthetic sphere is eligible as an example.

Project-authored code and documents are licensed under the owner-approved MIT
license, copyright **Pixal3D Character Geometry Research contributors**.
Upstream-derived code retains its applicable original license, NOTICE and
copyright, including public author email where required. Consult
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and
[FILE_PROVENANCE.csv](FILE_PROVENANCE.csv). Unknown redistribution rights lead
to exclusion, not an assumed license.

Acknowledgments: [Pixal3D](https://github.com/TencentARC/Pixal3D),
[TRELLIS.2](https://github.com/microsoft/TRELLIS.2),
[Direct3D-S2](https://github.com/DreamTechAI/Direct3D-S2), NumPy, PyTorch and the
AMD ROCm/HIP toolchain. Direct3D-S2 code is not vendored; its independent revision
and license remain unresolved beyond the local Pixal3D NOTICE attribution.

The reviewed source package has been published. The two upstream issue drafts
remain unsubmitted; no separate public
post is authorized by this publication request.
