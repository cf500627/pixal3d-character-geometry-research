# Inclusion decisions and remaining exclusions

The user approved MIT for newly authored code, retaining contributors' signatures, and preserving public author contact addresses **only in the original upstream LICENSE/NOTICE/copyright statements**. This is not a general exception for private contact information, environment details or credentials.

## Permission blocker resolved

The following required sources are now included unmodified:

| Included file | Attribution preserved |
| --- | --- |
| `overlay/pixal3d/modules/sparse/conv/conv_torch_native.py` | Adapted FlexGEMM forward-only convolution, with its full original author copyright and MIT text. |
| `hip_hash/src/api.h` | Original O-Voxel API header with its author copyright and MIT pointer. |
| `licenses/FlexGEMM/LICENSE` | Complete original FlexGEMM MIT license. |
| `hip_hash/LICENSE` | Complete original author MIT notice for the API header; Microsoft package attribution remains separately preserved under `licenses/TRELLIS.2/LICENSE`. |

No original copyright/contact line was stripped or rewritten. Personal workstation information remains excluded. Source and original notices are present; fresh dependency installation is **NOT_VERIFIED**, rather than waiting for a permission decision.

## Still excluded

| File category | Reason and effect |
| --- | --- |
| Original characters and all character-derived assets, targets, latents, arrays, meshes, renders and galleries | Asset rights and privacy; only aggregate anonymized historical numbers are included. |
| Model weights and research checkpoints | Remain separate official downloads or private artifacts; no redistribution. |
| Stage-specific private launchers, protection inventories, SHA audit receipts and process/SSH/billing records | Contain private paths or environment information and are not public examples. |
| Prebuilt native extension binaries | No compiled module is shipped; reviewers build the released source in new output directories. |
| Full third-party dependency source trees | Dependencies are obtained separately with their original licenses/notices. No nvdiffrast or CuMesh package is bundled. |
| Temporary synthetic replay latent/decoded arrays, predicted mesh and caches | Not required for this compact release; the procedural SOURCE sphere and small public verification summary are sufficient. |

Nothing was removed, moved or edited in an original working directory. No training, new geometry experiment or new scientific conclusion was made while preparing this package.
