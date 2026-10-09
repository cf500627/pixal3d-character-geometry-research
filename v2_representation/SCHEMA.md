# V2 variable-length numeric schema (historical excerpt)

Status: **RESEARCH_CODE_AS_IS / DRAFT_V2**, not a frozen neural training contract.
This is a copied excerpt, with a release introduction added, from
`TARGET_V2_DRAFT_SCHEMA.md`, section "TRAINABLE_FIELDS / numeric contract".
No historical target data, source identities, arrays, meshes, or audit receipts
are distributed.

The original draft described a 512 grid. The included Stage 9B reader is the
historical 1024-only reader and deliberately rejects other grid sizes. This
release does not alter that mathematical contract or add a model.

Coordinates are `(cell + offset) / grid_size - 0.5`. QEF offsets use the
historical exact FP32 dequantization `offset_u8.astype(float32) / float32(255)`.
The assembler consumes stored QEF values; it does not solve QEF from a source
mesh. Stored event `t` is Float64 and strictly inside `(0,1)`; equal-t events
retain their multiplicity. Orientation is supplied by event signs at
construction time. No later winding repair is performed.

## TRAINABLE_FIELDS / numeric contract

All arrays are non-object, finite, with an exact key whitelist. `N` events, `P` patches, `M=4N` incidences, `R` face arcs, `A` ambiguity observations and `L` ambiguity-to-patch references are variable length. No fixed K is applied. The categories below describe current evidence and actual reader obligations; they do not imply that every stored array should receive a separate neural output head.

| Field | dtype and shape | Classification | Meaning / minimum-field qualification |
|---|---|---|---|
| grid_size | int32 scalar | required_for_reconstruction | Constant grid contract, not learned. |
| event_owner_xyz | int32[N,3] | required_for_reconstruction | Physical local edge ownership. |
| event_axis | uint8[N] | required_for_reconstruction | X/Y/Z axis. |
| event_rank | uint32[N] | required_for_reconstruction | Local canonical addressing; derived ordering, not global classification. |
| event_t | float64[N] | required_for_reconstruction | Proper crossing fraction, strictly inside `(0,1)`; equal values retain multiplicity. |
| event_sign | int8[N] | required_for_reconstruction | Exactly -1 or +1, applied during construction. |
| patch_cell_xyz | int32[P,3] | required_for_reconstruction | Local spatial support. |
| patch_slot | uint32[P] | required_for_reconstruction | Contiguous cell-local address; derived order. |
| patch_offset_u8 | uint8[P,3] | required_for_reconstruction | Frozen quantized QEF geometry. |
| patch_offset | float32[P,3] | required_for_reconstruction | Current reader requires exact u8/255 consistency. Mathematically derived duplicate; no separate prediction head is justified. A 33-field removal/reload ablation has not been executed. |
| incidence_patch | uint32[M] | required_for_reconstruction | Target table row of the local patch. |
| incidence_local_edge | uint8[M] | required_for_reconstruction | Local physical cell edge, 0–11. |
| incidence_event_rank | uint32[M] | required_for_reconstruction | Local event selection on that edge; all four supports retained. |
| face_arc_lower_cell_xyz | int32[R,3] | required_for_reconstruction | Unique interior physical-face owner. |
| face_arc_axis | uint8[R] | required_for_reconstruction | Face normal axis. |
| face_arc_slot | uint32[R] | required_for_reconstruction | Contiguous face-local canonical address. |
| face_arc_endpoint_count | uint8[R] | required_for_reconstruction | Actual candidate grammar supports 1 or 2 event endpoints. Zero-endpoint interior arcs are absent from this grammar. |
| face_arc_endpoint_local_edge | uint8[R,2] | required_for_reconstruction | Endpoint address in lower-cell convention; absent second endpoint is exactly zero. |
| face_arc_endpoint_rank | uint32[R,2] | required_for_reconstruction | Canonical event rank; absent second endpoint is exactly zero. |
| face_arc_offset | float32[R,2] | required_for_reconstruction | Local UV geometry for initial C2 arc vertices. |
| event_t_class | uint32[N] | required_for_reconstruction | Current multiplicity safety validation; derivable from exact stored t, not an independent geometry feature. |
| event_status | uint8[N] | required_for_reconstruction | Safety enum: unique proper / retained multiplicity / unresolved local numerical orbit. Never a skip mask. Selected MAN targets contain no status2 events after bounded numerical ordering. |
| patch_orbit | uint32[P] | required_for_reconstruction | Local equivalence/safety metadata verified against stored descriptors. Does not label SOURCE sheets. |
| patch_status | uint8[P] | required_for_reconstruction | Explicit candidate/permutation safety metadata. Current branch evidence primarily lives in the separate ambiguity table; status0 alone does not prove no branch. |
| face_arc_status | uint8[R] | required_for_reconstruction | Regular, open one-ended or ambiguous-continuation status; never authorizes dropping a member. |
| face_arc_offset_fp64 | float64[R,2] | required_for_reconstruction | Conditional numeric canonical descriptor and precision audit. Present densely in this research candidate; not proven necessary at every ordinary face. |
| face_arc_geometric_moments | float64[R,4] | required_for_reconstruction | Length, covariance UU/UV/VV used by the stored numerical descriptor. Conditional canonical support, not a SOURCE hash; dense storage is not a minimal network recommendation. |
| ambiguity_cell_xyz | int32[A,3] | required_for_reconstruction | Safety inventory local cell. No branch surface is inferred merely from this row. |
| ambiguity_kind | uint8[A] | required_for_reconstruction | Explicit contact/branch category; known finite enum. |
| ambiguity_position | float64[A,3] | required_for_reconstruction | Local numerical contact point. |
| ambiguity_patch_offsets | uint64[A+1] | required_for_reconstruction | Full variable-length CSR, including zero-length inventory. |
| ambiguity_patch_slot | uint32[L] | required_for_reconstruction | References to local candidate patches in the same cell. |
| ambiguity_status | uint8[A] | required_for_reconstruction | Safety flag for unresolved continuation. Inventory is not an accepted multi-hypothesis triangulation. |

`required_for_training_auxiliary`: no additional auxiliary-only training arrays are frozen. Conditioning, losses and full heads remain unimplemented. The conditional descriptor/safety fields above must not be silently removed before the corresponding numerical/equivalence validation is replaced or ablated.

