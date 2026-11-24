# Continue The Crucible with another AI

## Start without rereading the whole project
1. Read [PROJECT_STATE.md](PROJECT_STATE.md). It owns current versions, validation
   evidence and the next task; keep it under fifty lines.
2. Read one relevant entry from [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md).
   Follow current session instructions before repository prose. Historical interview
   questions and old plan instructions do not restart discovery or revoke later work.
3. Inspect `git status --short` and the current branch before editing. This checkout
   is normally `feature/combat-coverage-and-timing`, draft PR #2. Do not assume main
   has the current source. Preserve other work; stage explicit task paths.

## Sources of truth
| Question | Owner |
| --- | --- |
| Accepted product intent and family constraints | REQUIREMENTS.md |
| Approved gameplay semantics | RULES_DRAFT.md |
| Implemented/gated coordinator behavior | src/crucible_core/coverage.py and tests |
| Current private-save version, conversion and rollback | SAVE_FORMAT.md |
| Current checkpoint, tests and next work | PROJECT_STATE.md |
| Card face/layout contract | CARD_INFORMATION_CONTRACT.md and CARD_DESIGN.md |
| Current experiments and their limits | Named experiment note and generated table |
| Future human-session preparation | FAMILY_PLAYTEST.md; timing deferred under REQUIREMENTS.md |
| World and terminology | docs/Game_Lore.md; root Game_Lore.md is a pointer |

Rules may describe future mechanics. Implementation coverage is deliberately
restricted; do not enable unsupported rules by copying a plan or external TCG text.
Numeric card/refill costs remain test candidates where the canonical docs say so.

## Repository map
| Path | Responsibility |
| --- | --- |
| run_play.py / crucible_play.desktop | Local Tk hotseat/practice game |
| run_desktop.py / crucible_lab | Combat-lab dashboard and single-combat replay |
| run_lab.py / crucible_sim | Finite combat enumeration, groups, SQLite checkpoints, exports |
| src/crucible_core/combat.py, combat_flow.py | Shared simultaneous damage and declaration kernel |
| src/crucible_core/match.py, turns.py, priority.py | Atomic resolver, turn/refill and response windows |
| src/crucible_core/commands.py, views.py | Session-bound input and allowlisted private/public projections |
| src/crucible_core/lobby.py | Validated singleton setup, redraw locks, frozen match content |
| src/crucible_content/practice.py | Default and opt-in engine-validated practice packs |
| src/crucible_play/session.py, persistence.py, migrate.py | Handoff adapter, private saves and explicit conversion |
| src/crucible_play/opponent.py | Live deterministic permitted-view opponent |
| src/crucible_play/package_opponent.py, package_eval.py | Experimental policies, matched studies and traces |
| design/packages/discard_draw.json | Provisional package source for count model and opt-in pack |
| design/cards | Separate template/editor/art work; see local-state note below |
| tests/fixtures | Immutable synthetic legacy save envelopes and next-command results |
| scripts | Build, equivalence and documentation/handoff tools |

## Run and verify from the Game directory
Python 3.11+ is declared; current validated interpreter details are in the checkpoint.
Tk must be available for desktop/widget tests. No third-party game runtime packages
or API calls are required. This is a source-checkout workflow: the opt-in package
reads its JSON under design/packages; a standalone wheel is not a verified delivery.

```powershell
$env:PYTHONPATH='src'
python run_play.py
python run_play.py --discard-package
python -m unittest discover -s tests -q
python scripts/audit_docs.py --write-index
```

For focused tests, use discover with `-p test_effect_discard.py` or another relevant
module. Existing Windows SQLite checkpoint tests can spend time on disk commits;
do not mistake slow commits for a failed policy. If using a workspace-local temp
folder, create an isolated directory under ignored dist, verify its resolved parent,
and clean only that directory. Never change checkpoint semantics to make tests fast.
Display-dependent Tk tests can skip on headless machines; state that limitation.

## Preserve boundaries while working
Keep pure engine changes separate from card generation and lab checkpoint schemas.
Before any saved-model change, write the compatibility/rollback plan, archive
synthetic old-format fixtures, preserve originals and test exact next-command
continuation. Follow SAVE_FORMAT.md instead of inventing defaults or editing hashes.
Live bots and experimental policy names are different; benchmark improvements are
not silently promoted. Retain named seeds, deck/policy versions, caps and censored
outcomes. A cap is incomplete, not a fabricated win/draw.

## Local card work versus Git
At this audit the local working tree contains modified template/fixture outputs and
untracked Card Studio, batch-art/style/template and image files. These are not all
in Git. The published v1 design baseline and local creator work are different
snapshots. See CARD_DESIGN.md before changing either. Do not regenerate, discard,
stage or publish unrelated art while fixing engine/docs. A separate AI needs those
local files supplied deliberately to continue that particular art/editor work.

## Portable documentation handoff
Run `python scripts/audit_docs.py --bundle` after committing the intended checkpoint.
It creates `dist/Crucible-Documentation-Handoff.zip`, with a file-hash manifest and
the base commit/branch. It is a documentation/proposal-data pack, not a source build.
Clone the named Git revision for code/tests. It excludes private saves, raw study
logs, third-party corpora, interview transcripts and active card-art/editor files.
The separate card-design ZIP generator may include all local design files, including
untracked artwork; review its intended contents before using it. These bundles are
local ignored artifacts, not automatically uploaded or committed.
