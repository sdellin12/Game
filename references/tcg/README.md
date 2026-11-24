# External TCG Reference Intake
Created 2026-11-22. References inform The Crucible; they are NOT executable simulator input or a source of automatic rule changes.

Owner preference: existing MTG and Digimon material is useful; Hearthstone is optional and not a prerequisite. Pokémon is optional accessibility/evolution reference. Optional Yu-Gi-Oh! fusion/chain and Elestrals later only for a scoped question. Full databases not needed.
Save material in the game folders below. Each has a README with examples:
- mtg/
- hearthstone/
- digimon/
- pokemon/

Within each folder use:
- rules_YYYY-MM-DD.pdf or .txt: official complete rules if available.
- cards.csv or cards.json: selected mechanical data with stable IDs, set/version, cost, stats, exact text, source link.
- decks.md: named/dated lists and intended play style, links.
- rulings.md: specific official clarifications and source links.
- notes.md: why an example matters and differences from our game.
Images/screenshots can be added when useful, but searchable text/CSV/JSON is easier to analyze. Start about20–40 relevant cards and1–3 decks/game; these are convenience targets, not prerequisites. A source-links.md file is enough when you don't want to download anything.
Record retrieval date and rule revision/format; do not mix old/new errata silently. Prefer official links and legitimate exports. Do not bulk copy proprietary artwork/databases to a public repo just for reference.
Our executable test content remains separately in src/crucible_content/profiles.json and practice.py; foreign cards are not runnable until explicitly modeled under a labeled experiment.

## Local inventory at documentation audit
MTG includes a rules PDF, SQL/card/ruling exports and generated Markdown references.
Digimon includes DIGIMON-general_rule.pdf. Pokémon includes Pokemon_Rules.md.
Hearthstone currently has intake guidance only. The corpora total roughly 102 MB;
metadata inventory is not verification of their rules revision or content accuracy.
No external reference is required to run the existing tests or practice game.
