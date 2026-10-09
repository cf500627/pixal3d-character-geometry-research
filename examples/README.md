# Synthetic example provenance

`sphere_source.ply` is the unchanged, project-generated Stage10A procedural
fixture: an icosahedron, four midpoint subdivisions, and radial projection to
radius 0.25 about the origin. It has 2,562 vertices and 5,120 faces. The source
is `STAGE10A_VAE_LOSS_DIAGNOSIS_RESULT.md`, section A1, and the original fixture
generator `prepare_a.py`. It was not imported from a commercial character,
asset store or third-party example collection. Its project-authored MIT
attribution is approved by the owner, with copyright attribution to
Pixal3D Character Geometry Research contributors.

`sphere_cpu.json` retains only the existing sphere's camera/threshold scalars
from the Stage10A protocol and the historical source counts. It contains no
private path, asset identity mapping, protected-file inventory or audit pin.
The four depth-exceed thresholds are exactly the inherited 0.11 / 0.25 / 0.5 /
1.0 h. The separate miss-or->2h test remains unchanged.

`gallery_template.json` is an empty, relative-filename template. Its referenced
images are not included. Supply your own synthetic images; the viewer rejects
missing files. No new renderer or character image is shipped.

[validation/REPLAY_VERIFICATION.json](validation/REPLAY_VERIFICATION.json) records packaging/replay assertions and
copies the historical expected sphere values. The clean CPU SOURCE identity
replay matched the original camera visibility. The already-installed AMD
backend reproduced the historical latent and decoded arrays exactly, and its
synthetic C mesh reproduced the entire original C/ALL ray metric object exactly.
The GPU worker exited normally and completed final cleanup.

The additional source/build replay used a new pristine pinned source copy with
the included patch and convolution overlay, plus a freshly compiled HIP hash
extension. A new GPU worker imported that source and rebuilt module. Its latent
and decoded arrays matched the existing Stage10A synthetic reference exactly;
its mesh was byte-identical to the previous synthetic replay. It exited
successfully after normal cleanup. The verification record distinguishes this
new-source replay from the earlier already-installed-backend replay.

This is validation of the packaged interface and historical reference, not a
new research result. Both GPU replays reused existing Torch/HIP, O-Voxel I/O
and official weights. Complete fresh AMD dependency installation remains NOT_VERIFIED
because that separate installation has not been verified. Licensing approval
and permission to retain required public author contacts do not change that
engineering verification status. Newly generated synthetic
latent/decoded arrays, inference mesh, compiler artifacts, runtime caches and
private validation logs are not distributed. The only binary in this candidate
is the procedural SOURCE sphere.
