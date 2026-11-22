"""Versioned coverage for the internal coordinator, separate from combat-lab reports."""
MATCH_COVERAGE = {
    'version': 1,
    'full_match_enabled': False,
    'implemented': (
        'priority-and-atomic-effects', 'required-draw-refill-and-recharge',
        'permanent-elimination-and-owned-controlled-cleanup', 'serial-concessions',
        'start-ready-and-eligibility', 'start-natural-growth-and-capacity-refill',
        'registered-capacity-and-resource-grants', 'exact-controlled-token-payments',
        'registered-source-ability-main-reaction-timing', 'exhaust-and-per-turn-costs',
        'end-triggers-discard-and-registered-expiration-consequences',
        'committed-attacks', 'private-simultaneous-blocker-locks',
        'explicit-damage-orders', 'post-declaration-and-final-response-windows',
        'shared-simultaneous-damage-kernel', 'combat-lock-projection',
    ),
    'excluded': (
        'production-match-save-and-reconnect', 'general-player-bot-projections',
        'hand-card-play-and-zone-transitions', 'generic-targets-modes-x-discounts',
        'authored-health-sacrifice-costs-and-replacements', 'leaders-and-recovery',
        'transform-combine-and-continuous-stat-modifiers', 'general-duration-scheduler',
        'discard-draw-damage-and-attack-trigger-abilities',
        'repeated-recharge-debt-and-penalty-bypass',
    ),
}
