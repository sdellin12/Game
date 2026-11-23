# Private discard continuation and recovery/refill audit

Source launch: `python run_play.py --discard-package`.
Headless: set PYTHONPATH=src, then run
`python -m crucible_play.smoke --practice --discard-package --players 3`.
This uses an opt-in forty-card pack with the three provisional Actions; default
Practice Forty v9 and frozen saves keep their original content. Package design:
../DISCARD_DRAW_PACKAGE.md. Canonical rules: ../RULES_DRAFT.md.

## Implementation
DiscardThenDraw(target,count) keeps a registered instruction unchanged while its
Resolution pauses. An event-backed discard_request opens a private single-card
selection; the session-bound command requires actor, exact revision, request ID and
current hand membership. The chosen identity becomes public only on commitment.
discard_done persists the successful gate across partial draw/refill; completing
the draw advances the instruction and clears the gate. No intermediate response
window or optional-trigger decision opens. The Action remains pending until atomic
completion. A confirmed concession at the choice deterministically discards the
first hand card to finish the effect; any refill for that conceding player declines
automatically, then safe-boundary elimination proceeds.

The UI uses an explicit single selection with paused confirmation disabled. Existing
private-seat handoff gates apply. The computer sees only its own projected choice,
chooses a hand card and avoids voluntarily playing a last-card outlet. CLI opt-in
persists for new games in that window. Loading a save uses its frozen definitions.

## Save compatibility
Schema v6 / gameplay compatibility 1, with only discard_request=None and
discard_done=False defaults added to historical Resolution records. V5 optional
choices/decisions are preserved. Explicit conversion accepts known v1 and compatible
v2-v5 saves, rejects premature new fields/records and never overwrites input/output.
Both an archived native-v5 private optional decision and partial required-draw refill
retain their original content hash and exact next-command outcome after conversion.
Native-v6 choice and post-discard refill pauses round-trip and resume identically.
DiscardThenDraw has a type-sensitive card/leader content-hash discriminator; old
packs retain their hashes. Full rollback/format policy is in SAVE_FORMAT.md.

## Loop findings
- With one Lantern, Battery and Well installed, one successful Insight costs two,
  then delivers three immediate resources and one permanent capacity. Rewards wait
  until the entire effect finishes; they cannot pay the initial cost.
- Recovering Insight with Second Chance costs three more. Two Insight uses plus
  that recovery end one resource below the post-setup starting amount, grant two
  permanent capacity and consume four deck cards. Second Chance is now in discard,
  not hand, so it cannot immediately play/recover itself. This checks a real paid
  reuse sequence, not a proof that every future recovery combination is safe.
- One newly discarded card alone cannot refill a required two-card draw. The
  pending Action is excluded; one card can draw, but the remaining required draw
  fails and eliminates the player. No card or instruction is duplicated.
- A successful own-turn refill defers all captured trigger decisions until the
  effect completes and then prevents more ordinary recovery plays that turn.
  A concession at an empty-deck discard choice finishes without a waiting-choice
  deadlock or a second discard.

There is no arbitrary loop cap or new balance restriction. Recovery discounts,
additional recovery cards, off-turn outlets, healing packages and penalty bypasses
need separate audits if authored. Permanent capacity's future spending value is not
equated with immediate resources.

## Verification
Six loop tests and ten choice/save/UI tests cover actual paid plays, atomic reward
capture, private/stale/wrong-actor checks, pending-source exclusion, no-fodder no-op,
negation, refill acceptance/decline, repeated commands, concessions, malformed
cursors, original-save preservation, conversion and paused widget confirmation.
Opt-in mixed-client smoke completes at 296/1394/1775 commands and 15/65/69 global
turns for 2/3/4 seats (smoke-1). These runs check progress, not comparative balance.
The next evaluation is seat-rotated package/control deck play with matched policies.
Full suite passes 426 Windows tests (workspace-local isolated temporary directory).
