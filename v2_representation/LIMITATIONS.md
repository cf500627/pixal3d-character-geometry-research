# V2 limitations copied from existing reports

All numbers below are historical report values. No new measurement is added
by this release preparation. The commercial character models and every
derived mesh, target, latent, rendering, per-pixel array and checkpoint are
excluded. Public identifiers are Char-A / Char-B / Char-C.

## Fixed-channel capacity is an assumption, not a finished interface

Source: `V2_1024_FIXED_CHANNEL_DIAGNOSTICS_RESULT.md`, sections
"一頁結論" and "A：容量、接口、原 dtype 與精度".

The three measured full targets have the sample envelope `Ke=10`, `Kp=13`,
`Ka=12`, `Kb=5`, `Kr=7`. This is a measured sample envelope, not a universal
capacity bound. Retaining masks/status, orbit metadata and ambiguity produces
the report's explicit output-cost assumption of **3,915 scalar/logit
channels**:

```text
C_output_cost = 18Ke + Kp*(7+12Ke+Kp) + 3Ka*(10+4Ke) + Kb*(10+Kp) = 3915
```

The report states `FIXED_SLOT_ENCODING=PARTIAL` and that the complete neural
encoding and `C_input` remain unresolved. The 3,915 figure is not an implemented
neural interface, a proven minimal encoding, or a bound on future assets.
For Char-A, the reported single output buffer costs **23.984499 GiB** in
FP16/BF16 and **47.968998 GiB** in FP32. The report did not measure training
VRAM, activations, backward, optimizer or allocator overhead.

The released variable-length assembler applies no maximum K and does not
truncate or merge tokens. It requires complete discrete associations.

## Precision changes can break numeric ordering

Source: `V2_1024_FIXED_CHANNEL_DIAGNOSTICS_RESULT.md`, section
"A：容量、接口、原 dtype 與精度", table "固定浮點舍入診斷" and following
descriptor paragraph.

| Character | Precision | Merged adjacent distinct t | Strict t violations | Patch primary-order inversions | New primary ties |
| --- | --- | ---: | ---: | ---: | ---: |
| Char-A | FP32 | 0 | 0 | 0 | 0 |
| Char-A | FP16 | 47 | 902 | 11 | 0 |
| Char-A | BF16 | 324 | 7334 | 112 | 0 |
| Char-B | FP32 | 0 | 0 | 0 | 0 |
| Char-B | FP16 | 390 | 864 | 193 | 3 |
| Char-B | BF16 | 1130 | 6205 | 465 | 45 |
| Char-C | FP32 | 23 | 0 | 4 | 3 |
| Char-C | FP16 | 1379 | 591 | 507 | 393 |
| Char-C | BF16 | 2042 | 4776 | 729 | 454 |

For the 50 existing typed-descriptor distinctions in Char-C, FP32 retained
all 50; FP16/BF16 lost **15/16** distinctions and showed **8** numeric-order
changes. These are stored-value rounding diagnostics. The report did not run a
new rounded decoder or a neural-learning experiment. Reference packing pass,
precision risk and learnability status are separate conclusions.

## Correct counts alone did not produce a legal predicted mesh

Source: `RESULT.md` from the historical G3D NonlinearSign experiment,
sections "實測比較" and "本次具體改動與邊界" (LINK02).

| LINK02 metric | Historical value |
| --- | ---: |
| Correct patch-count groups | 5,116 / 5,116 |
| Correct event-count groups | 15,348 / 15,348 |
| Missing support sides | 0 |
| Pointer errors | 51 / 20,184 |
| Correct nontrivial pointers | 1,486 / 1,537 |
| Sign errors | 72 / 5,046 |
| Unreferenced patches | 9 |
| Optimizer updates in that historical experiment | 2,000 |

The unchanged assembler rejected the raw payload because every patch must
have an incidence. No legal predicted PLY was produced. The raw tokens were
not repaired or replaced with an oracle mesh. Arc counts and pair sets were
not fully correct; arc/continuous-geometry training was not run after the
failed gate. This fixed-support, target-derived-latent experiment did not
learn image conditioning or occupied cells and cannot establish three-view
generation. One bounded failed learning experiment does not prove that V2 or
all other predictors are unlearnable.

## Other boundaries

Source: `TARGET_V2_DRAFT_SCHEMA.md`, sections "What is actually represented",
"Deterministic construction and rejection", and "Freeze blockers and next
boundary".

The ambiguity inventory is not a complete branch-surface triangulation.
No-edge interior geometry remains outside the regular endpoint grammar;
the separate interior-boundary experiment is not integrated. Numeric
canonicalization, preserved target associations and exact structural legality
are distinct from neural learnability and visual acceptance.

TrueNormal describes geometric face orientation. Tangent-space normal-map
UV/cross-tangent seams were not tested. This release makes no material,
normal-map repair, complete character product or visual-quality claim.
