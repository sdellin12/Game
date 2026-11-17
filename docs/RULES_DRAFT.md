# Playtest Rules Draft and Open Decisions
2026-11-17. Accepted requirements: REQUIREMENTS.md. This document proposes missing procedures. Pxx/Rxx are NOT user-approved unless explicitly recorded later. No balance validation yet.

## Engine
Deterministic server-authoritative state machine; clients submit commands. Separate ruleset parameters, immutable card definitions, mutable card instances, effects, hidden-information views, responses/combat, agreements, leaders, forms/combination and revival. Structured effects define trigger, cost, target, duration and resolution, not prose execution. Match pins definitions/rules so catalog edits never mutate active cards.

## Accepted baseline
4 regular players, 40–60min target. 40 singleton draw cards + separate leader; single color+generic. Small gameplay variants allowed. 30 player HP initially, possible50 later. Five opening hand, free selective redraw rejected shuffled back. Draw1 start own turn. End turn hand<=7, normal legal plays before discard. Universal capacity +1/refill own-turn start; temp growth cheaper than permanent. Exact starting capacity unset.

## Proposed phases
P01 Start: ready creatures; recover eligible leader; grow/refill resources; start triggers; draw. Starting capacity0 means1 resource first turn; all players first-turn draw. Order and numerical initial capacity need acceptance.
P02 First action phase -> combat -> second action phase -> cleanup. Creatures/sustained cards in own action phases with empty chain; instants/permitted abilities in response windows. Exact card categories remain draft.
P03 Fixed seat response order, active player first. New action resets consecutive passes. Everyone explicitly responds/passes; inability still shows Pass only. All pass -> resolve newest one -> open fresh window. Empty chain+all pass advances phase. No reaction timer assumed.
P04 Opening replacement: set unwanted cards aside, draw same count, shuffle rejected back. User approved reshuffle, not exact order. No setup discard triggers.
All UI must show target/pending effect/next resolution. Preview conditional public outcome only.

## Combat with THREE stats
Accepted: attack players/split targets; defenders choose blockers; allied help requires acceptance; multiple blockers ordered by attacker; automatic allocation and simultaneous retaliation. Flat defense reduction + persistent health supersedes early examples equating defense with lethal threshold.

P05 Raw damage budget: ready blocker requires defense + remaining HP raw attack to defeat. Assign sufficient raw damage to first, then remainder next. If insufficient, apply defense to assigned amount then HP loss. No negative damage.
Example attacker attack8/defense2/currentHP10 vs A attack3/defense1/currentHP3 and B attack2/defense2/currentHP5:
| Target | Raw assigned | Prevented | HP damage | Outcome |
|---|---:|---:|---:|---|
| A first | 4 | 1 | 3 | Destroyed |
| B second | 4 | 2 | 2 | 3HP survives |
P06 Retaliation unresolved: recommend pool blockers' attack once then apply attacker's defense once (3+2-2=3), attacker remains7HP. Applying defense separately per blocker instead would deal1+0=1. This materially affects swarms/armor and needs explicit selection. Pooling must preserve source/type trigger semantics deliberately; do not fake one source for every effect.
P07 Exhausted blocking accepted as extra creature damage, not automatic overflow. Proposed test formula ceil(max(0,raw-defense)*1.5); allocate minimum raw amount producing lethal HP damage. Exact multiplier/order/rounding UNAPPROVED.
P08 Trample explicitly on cards only: proposed leftover raw budget after lethal allocations to all blockers reaches target player, not multiplied again. With no trample, unused budget does not hit player. Test exhausted-blocker raw-to-HP conversion carefully; cannot multiply whole incoming budget and then overflow again.
Clarify before full battle: P05–P08, damage source grouping, minimum damage, multiple-source defense and card override precedence.

New creatures block immediately, attack next owner turn unless effect. Attacking exhausts until next owner turn; blocking does NOT exhaust by default (user confirmed after planning review); persistent wounds remain and already-exhausted blockers remain exhausted with their damage penalty. Ready survivors may defend in later combats. Exact one-blocker/multiple-attacker assignment per combat remains unresolved. One creature's ability to block multiple attackers also unselected.

## Leaders/forms
Accepted leader outside effects, persistent summoned combat role; no commander damage. Defeated leader returns outside; effects recover owner's next turn. Resummon escalating/differentiated costs may include resources/sacrifice/exile.
R02 Need initial summon requirements, resummon escalation, passive availability in battle and whether recovery also gates summoning. Propose one clear leader per starter with explicit costs; don't invent full arbitrary creator costs.
P09 Transform keeps damage points/readiness; changed max HP mapping is unapproved. If prospective new HP<=0, preview outcome rather than secretly heal. User accepted preservation but not point-versus-ratio mapping.
Combination HP accepted: combinedMax*(sum component currentHP/sum component maxHP).
P10 Propose round down; any exhausted component -> combined exhausted; entering/combining cannot reset attack eligibility. Authored balanced combined max stats, not automatic sum. Components linked under combined object. Destroy all components unless explicit survival. State on separation/exile/bounce/control transfer remains to specify.
Color shapes effects but fitting transformations/combine broadly available.

## Bargains and randomness
Gold enforcement exclusive; terms selected from structured game-state options, not arbitrary speech truth detection. Ordinary promises breakable. Public offers all; secret requests via sneaky-color effects, accepted deals/actions public before resolution. Gold forced commitments temporary, never full-game lock. R03 Clarify impossible obligations, conflicts, expiration order, attack/block capacity and counterplay in concrete starter cards.
Predictable majority; risk cards occasional dice/coin, Silver tentative. Server logs reproducible randomness/draw ordering; no client-picked dice. Creature vulnerabilities explicit/intuitive, no universal personality-color chart; numbers deferred. Avoid prolonged lockouts.

## Revival and ending — major draft gate
Accepted defeated players participate and can conditionally revive. Proposed full-hand payment via giving/discarding and drawing when short; exact size and draw behavior NOT settled. Higher returnHP for gifting candidate. User explicitly deferred these specifics.
R01 Must jointly define defeat-time retained field/hand/resources, defeated legal actions, leader access, revive eligibility including deck-out, payment size, draw-when-short, returnHP, repeat limit and final-window procedure. Drawing cards to discard from an empty hand can still be a weak effective cost, despite full-hand requirement; test.
Candidate for review: at most one revival/player, clearly authored cost, no deck-out return unless drawable deck restored. NOT adopted.
P11 Final window: finish pending effects, offer each eligible defeated player one declared revival opportunity in seat order, resolve responses, then check active players. No real-time countdown. Limits prevent renewal loops. User approved bounded window, not this precise procedure.
Need simultaneous-all-defeated/draw rule. Health-loss versus failed-draw return rules can differ only if explicitly selected.

## Review priorities
Before coding a full match, get product decisions on R01/R02 and selected combat semantics; present worked scenarios rather than every corner-case interview. Other Pxx can be reviewed together as provisional ruleset. No balancing by numerical points alone: test effects, tempo, resource growth, alliances, denial, revival+mill loops, near-duplicate singleton variants.
Later user-requested large comparative team may research MTG/Pokemon/Elestrals/Yu-Gi-Oh! with official sources; separate from completed narrow planning review. Approximate ten-color roster still open and should be designed around distinct play styles before building ten decks.

## Post-draft decision: blocking readiness
Confirmed: blocking itself does not exhaust. Preserve accumulated wounds/existing exhaustion; attacking exhausts as before. Next review P06 pooled blocker retaliation versus applying defense separately to each blocker, using a worked example. P06 remains proposed, not selected.
