# Source and redistribution notes

The files here are copied from project-authored research programs. Paths in
this table are symbolic research source locations, not the author's machine
paths. The originals were read only. No source data, weights, provenance
hashes, process logs or protected-file inventories are included.

| Release file | Historical source | Packaging change | License attribution |
| --- | --- | --- | --- |
| `target_source_free_reconstruct_v2_02.py` | `stage9b_v2_1024_causal/tools/target_source_free_reconstruct_v2_02.py` | Exact field constants and `require`, `quad_blueprint`, `reconstruct`, `save_ply` functions retained; machine-bound launcher and audit wrappers omitted; release introduction added. | Project-authored research; approved MIT. |
| `target_v2_validation02.py` | `stage9b_v2_1024_causal/tools/target_v2_validation02.py` | Copied unchanged. | Project-authored research; approved MIT. |
| `target_face_arc_construction_v2_02.py` | `stage9b_v2_1024_causal/tools/target_face_arc_construction_v2_02.py` | Copied unchanged. | Project-authored research; approved MIT. |
| `target_triangle_emission.py` | `stage9b_v2_1024_causal/tools/target_triangle_emission.py` | Copied unchanged. | Project-authored research; approved MIT. |
| `pinned_rounding_reference.py` | `stage9b_v2_1024_causal/tools/pinned_rounding_reference.py` | Exact pure numerical functions retained; reference-mesh import/loader and wrappers omitted. | Project-authored arithmetic implementation; approved MIT. |
| `SCHEMA.md` | `TARGET_V2_DRAFT_SCHEMA.md`, "TRAINABLE_FIELDS / numeric contract" | Numeric-contract excerpt copied; new release introduction explains 512 draft / 1024 reader distinction. | Project-authored research documentation; approved MIT. |
| `LIMITATIONS.md` | `V2_1024_FIXED_CHANNEL_DIAGNOSTICS_RESULT.md`, "A：容量、接口、原 dtype 與精度"; G3D `RESULT.md`, "實測比較" / "本次具體改動與邊界"; `TARGET_V2_DRAFT_SCHEMA.md`, named sections | Existing values copied; character labels anonymized and scope preserved. | Project-authored research documentation; approved MIT. |
| `README.md` | Existing research program interfaces and the named historical reports | Release-only interface and packaging documentation; no new measurement. | Project-authored release documentation; approved MIT. |
| `SOURCE_NOTES.md` | Packaging selection and file inspection | New documentation of copied code and omitted components. | Project-authored release documentation; approved MIT. |

## Mathematical attribution

The historical triangulation and rounding contracts refer to the O-Voxel
conversion logic in microsoft/TRELLIS.2 commit
`75fbf0183001ed9876c8dbb35de6b68552ee08bd`,
`o-voxel/o_voxel/convert/flexible_dual_grid.py`, and the observed eager FP32
arithmetic contract. These included NumPy/integer functions are project-authored
implementations, not copied upstream source files. The independent
`upstream_mesh_reference.py` is deliberately not shipped here.

NumPy is a runtime dependency installed separately. Neither NumPy code nor a
native executable is redistributed by this directory. The root
`THIRD_PARTY_NOTICES.md` records licenses verified from local license files.

## Omitted / pending components

- The full target producer and SOURCE supervision readers: omitted because
  historical paths, source-identity inventory and launcher dependencies are
  not a portable producer interface. No commercial input is provided.
- The native per-sheet QEF solver and any vendored Eigen/native headers:
  omitted until complete per-file redistribution provenance is established.
  QEF consumption and quantization are documented without vendoring them.
- The upstream independent mesh-reference file: omitted from this directory;
  not needed by the extracted pure rounding functions.
- The G-series predictor, training drivers, frozen latents, target payloads
  and checkpoints: omitted. Historical aggregate gate outcomes are reported
  in `LIMITATIONS.md` only.
- The interior-boundary representation and residual meshlets: omitted from
  this regular V2 reader. No integration or completeness claim is made.

This is an intentionally bounded research-code handoff. Packaging did not run
a new V2 experiment, train weights or change assembly mathematics.
