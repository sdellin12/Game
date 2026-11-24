# Family playtest checklist — local prototype

Status: prepared for a real session; no family observations are recorded yet.
Use the current source checkout and [PLAY_HARNESS.md](PLAY_HARNESS.md) for controls.
This tests one-PC Tk hotseat/practice, not phone/iPad/TV clients, network pairing,
automatic server saves, TTS/hints, currency or the card creator. Those product
requirements are not present features of this playtest harness.

## Before the session
- [ ] Record Git commit, date, Python version, Windows/display setup and chosen mode.
- [ ] Start with `python run_play.py` from Game. For human hotseat, turn off the
  computer option before creating the new lobby; keep hidden hands hidden on handoff.
- [ ] Use the default deck for the first session. Record leader choices and seats.
  If computers participate, they use the live baseline, not the research variants.
- [ ] An adult rehearses Ready -> opening redraw -> Main -> combat -> End using
  the walkthrough. Record any UI failure before inviting children to diagnose it.
- [ ] Identify a local save location. Use manual Save game before taking a break;
  this prototype does not provide household server autosave or reconnect.

The provisional refill price is shown by the game. Do not alter costs, give extra
cards or change rules halfway through a session to compensate for confusion.
An adult can read text aloud; simpler explanations do not change mechanics.

## First session: learn the interaction
Allow a short learning session rather than requiring a complete first match.
There is no turn timer; suggested session lengths are organizer choices only.

| Check | What to observe |
| --- | --- |
| Private handoff | Can each person hide the hand, pass the PC and acknowledge the correct seat? |
| Opening | Can players keep/replace cards without seeing other hands or acting twice? |
| Cost and resources | Can they identify a card's upfront cost and available resources before confirmation? |
| Priority | Can they tell who must act/pass next and whether the game is waiting rather than frozen? |
| Card inspection | Is the full rule/cost/leader information readable without guessing from art? |
| Combat | Can they declare none/some attacks, choose blocks and understand the simultaneous result? |
| End choices | Is an excess-hand discard clearly different from playing a card into discard? |
| Accessibility | Which words/icons/fonts need explanation? Record exact screens rather than changing rules. |

Ask neutral prompts: “What do you think happens next?” and “Where would you look for
the cost?” Note adult help and misclicks. Avoid coaching toward a particular strategy
when trying to learn whether the controls themselves are understandable.

## A complete match when players are ready
- [ ] Record player/seat order, human/computer seats and random starting seat.
- [ ] Record actual wall-clock duration, pauses, teaching time and long waits.
  Synthetic turn counts do not establish the 40–60 minute product target.
- [ ] Observe whether multiple reactions/passes remain understandable.
- [ ] If a player is eliminated, record what they can still see and how long they
  wait. Do not add player revival. Ending the session is an organizer choice.
- [ ] Save at a natural break; load, confirm it is paused/hidden, then resume and
  acknowledge a human seat. Record whether the next expected action is preserved.
- [ ] Record the result or “session stopped”; do not invent a winner for a stopped
  game. Use the existing confirmed concession flow when a player chooses to leave.

There is no requirement to naturally hit every rare rule in a family game. Use the
automated fixtures for edge cases; do not make children reproduce corrupted saves
or long forced loops.

## Optional second session: discard package
Launch `python run_play.py --discard-package`. Keep other choices as similar as
practical, and record the three changed cards instead of attributing every outcome
to one mechanic. The costs and whole package remain provisional.

- [ ] Insight: can the player choose exactly one current hand card, then follow the
  draw continuation? Does “if you do” make sense when no other hand card remains?
- [ ] Lantern/Well: can they distinguish an optional Use/Skip reward from a required
  discard? Is the waiting-seat/order confirmation understandable?
- [ ] Resources versus capacity: can they distinguish resources usable now from
  capacity available at a later refill?
- [ ] If deck refill occurs: is the life payment and turn consequence understood
  before accepting? Do required draws finish before ordinary plays stop?
- [ ] Record whether the package encourages interesting choices or just additional
  reading/waiting. A win alone does not answer that question.

## Record notes without exposing hidden information
Keep private save files local unless deliberately sharing them for debugging;
they contain hidden cards and shuffle state. A useful issue note usually needs
version/commit, player/phase, committed action, expected result, actual result and
whether the problem repeats. Share only an appropriate public/redacted image.

| Item | Session notes |
| --- | --- |
| Commit, mode, leaders, seats, starter | Not run |
| Started / ended / teaching and pause time | Not run |
| Winner, concession, or stopped session | Not run |
| Confusing screen/word and help needed | Not run |
| Invalid action, crash, privacy or save issue | Not run |
| Favorite choice / boring wait / requested change | Not run |
| Next smallest improvement | Not run |

Classify findings as engine correctness, privacy/save, UI/comprehension, pacing/fun,
or strategy/content. Fix reproducible correctness issues first; keep proposed rule
or cost changes separate from usability fixes. A session with notes and an identified
next change is useful evidence, not a certification that the whole product is ready.
