# Owner decisions and publication boundary

The owner explicitly approved the following decisions on 2026-10-09. They are
applied to this research source release. The owner has subsequently authorized
creation of the public repository and push of the reviewed package.
**PUBLICATION = PUBLISHED.** The public repository's file inventory, source
bytes and anonymous public access have been verified.

Public repository:
[stylized-character-geometry-research](https://github.com/cf500627/stylized-character-geometry-research).

| Decision | Status | Applied choice |
| --- | --- | --- |
| License for project-authored code and documentation | PASS | MIT. Upstream-derived files retain their separate original licenses and attribution. |
| Project copyright holder | PASS | `Pixal3D Character Geometry Research contributors`. The root LICENSE retains this exact name. |
| Public upstream copyright-contact exception | PASS | Original public author emails may remain in third-party LICENSE, NOTICE and copyright statements. Only necessary code with confirmed redistribution terms is included. This exception never permits the owner's private information, accounts, SSH records or credentials. |
| Research-input names | PASS | Char-A / Char-B / Char-C only. No real-name mapping is distributed. The measurements concern three commercial stylized character models absent from this release. |
| Repository name | PASS | `stylized-character-geometry-research`, the approved public repository name. |
| Public source publication | PASS | The owner-authorized source package is published. Remote inventory, source bytes and anonymous public access have been verified. |
| Upstream issue submission and separate public posts | NOT_AUTHORIZED | The two issue drafts remain unsubmitted files in the source package. This publication request does not authorize upstream issue submission or separate public posts. |
| Scientific visual acceptance | PENDING_USER | `USER_VISUAL_ACCEPTANCE = PENDING`. Packaging and numerical replay checks provide no visual score or usable-character claim. |

## Excluded material and remaining engineering limits

These items are not unanswered versions of the five decisions above. They
remain excluded or explicitly unverified; MIT approval does not resolve them.

- The full V2 native QEF producer and its third-party headers have incomplete
  per-file redistribution provenance and are not included.
- Direct3D-S2 is acknowledged through the retained Pixal3D NOTICE; its own
  revision and independent source-license selection were not established, so
  no Direct3D-S2 source or weights are bundled.
- The full fixed-render, witness and multi-character capacity orchestration
  is research code within its documented limits. The released CPU subset
  has a demonstrated synthetic replay; this is not full renderer portability.
- A complete fresh AMD dependency installation is separate from a replay
  using the existing local Torch/HIP installation. Consult RELEASE_CHECKLIST.md
  for the exact verified scope rather than treating owner approval as a test.
- Character assets and all derivatives, model weights, private operations
  records and unclear-license material remain excluded.

No further license, copyright, naming or public-notice answer is required for
this source release. Any future inclusion of an excluded dependency needs
its own verified license and provenance, not a guessed license.
