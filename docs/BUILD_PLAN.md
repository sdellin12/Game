# Delivery roadmap

This is a roadmap, not an implementation gate left over from the original interview.
Current versions/evidence and the authorized next task live in PROJECT_STATE.md.
AI_HANDOFF.md maps the implemented source; REQUIREMENTS.md owns product intent.

| Track | Status | Remaining exit evidence |
| --- | --- | --- |
| Canonical product/rules/lore | Consolidated | Maintain owners and explicit future mechanics |
| Combat kernel and finite lab | Implemented | Continue exact fixtures for new rules |
| Batch/checkpoint/report/replay desktop | Implemented | Clean-machine distribution and larger-scale worker work remain |
| Local full-match practice subset | Implemented | Respect coverage.py exclusions; no complete-product claim |
| Practice bots and policy studies | Baseline live, candidate policies experimental | Investigate remaining regression before promotion |
| Private manual save/restore/conversion | Implemented | Durable server autosave/reconnect are future work |
| Standard/full-art templates | Published v1 baseline plus active local edits | Verify/share the intended design snapshot |
| Local card editor/art helpers | Present as uncommitted local work at audit | Separate source review, tracking and reproducible handoff |
| Household server and device clients | Future | Real-device installation, pairing, privacy, reconnect and TV checks |
| Family playtest | Deferred until a usable app takes shape | Follow owner timing in REQUIREMENTS.md; future checklist retained |
| Catalog, creator, progression and complete delivery | Future | Household persistence, artwork queue and all product acceptance checks |

The local Python harness is currently an engineering tool. The next recommended
product slice has begun with a scrollable card table, player zones and fixed turn
controls, guided setup/opening and card-based attack/block selection
(MATCH_UI_FLOW.md), fixed table navigation and exact-payment/target review. Next
improve required choices and damage/trigger ordering, then visual hierarchy,
followed by a revisit of family-test readiness. The existing portable
CrucibleLab executable is combat-only. Source-only package files and old builds
are not an installer for the whole household product.

Device/art/platform feasibility proposals remain in ARCHITECTURE_PROPOSAL.md and
UX_CONTENT_PLAN.md. Keep their external-source findings dated and reverify before
choosing a toolchain or spending money. No platform deployment, subscription or
paid fallback is implied by local prototype work.

Keep changes focused, preserve user art and saved data, and use migration/rollback
planning before changing persisted models. Prefer exact tests and named synthetic
studies; policy game counts do not replace human playtests. Current workflow and
agent preferences are in MODEL_WORKFLOW.md.
