# V2 research representation

**RESEARCH_CODE_AS_IS.** This directory contains the existing variable-length
numeric V2 assembler and specification excerpts. It does not contain a trained
model, a target producer ready for arbitrary assets, or an image-conditioned
character generator. No new representation or geometric experiment was run to
prepare this release.

The measurements used three commercial stylized character models that are not
included in this release. Public report labels are Char-A / Char-B / Char-C.

## Contents and interface

- `SCHEMA.md`: historical numeric field whitelist, dtypes and associations.
- `target_source_free_reconstruct_v2_02.py`: `reconstruct(data)` and the original
  numeric support checks, assembly and PLY writer. The historical Windows
  process/file-audit launcher is omitted; this copy does not claim that
  enforcement layer.
- `target_v2_validation02.py`: multiplicity, canonical order, local orbit and
  ambiguity-inventory validation.
- `target_face_arc_construction_v2_02.py`: original shared-arc and private fan
  construction (C2), with stored event signs applied before faces are emitted.
- `target_triangle_emission.py`: original FP32 two-diagonal selection and
  winding at construction.
- `pinned_rounding_reference.py`: original pure FP32/FMA arithmetic helpers.
- `LIMITATIONS.md`: numerical capacity, precision and learnability boundaries.
- `SOURCE_NOTES.md`: file-level provenance and omitted components.

The Python files depend on NumPy and the standard library. Add this directory
to your Python import path and call `reconstruct(data)` with caller-owned arrays
that match `SCHEMA.md`. The included historical reader requires
`grid_size == 1024`. It returns vertices, faces, oriented support quads,
construction trace and validation details, or raises a concrete validation
error. It does not read SOURCE files or model weights. Neither a character NPZ
nor a replacement oracle mesh is shipped.

The historical target producer and per-sheet QEF backend are omitted. They
depend on private experiment launchers, source-supervision inventory and a
native backend whose complete redistribution provenance is not established
for this release. See the pending items in `SOURCE_NOTES.md`. The portable
library is therefore not an end-to-end target-building tool.

## Unchanged assembly mathematics

Each retained event requires exactly four geometric support assignments.
The original reader rejects absent supports, unreferenced patches, illegal
indices, inconsistent local association, invalid canonical ordering and
nonfinite values. It never deletes erroneous tokens, truncates event counts,
substitutes ground truth, welds positions, fills holes or repairs winding.

QEF values are consumed from the payload with the original uint8/255 contract.
Ordinary events retain the two-diagonal rule. Distinct parallel arcs receive
distinct shared arc vertices; repeated support diagonals receive private event
fan centers. The existing C2 event/polygon-mean blend is unchanged. The
ambiguity table records unresolved alternatives; it does not invent a branch
surface or integrate the separate interior-boundary experiment.

The copied pure functions were checked statically for syntax and equality of
their function ASTs with the historical originals. No decoder experiment was
run for this packaging check. Commercial character data and geometric results
remain excluded. Original launchers, runtime evidence and GPU training loops
are not reproduced here.

Project-authored research code and documentation are covered by the approved
root MIT license, with the contributors attribution retained. No third-party
code or weights are vendored in this directory.
