W, H   = 360, 640
FPS    = 60
TITLE  = "Skybit"

GROUND_Y   = 595
CEILING_Y  = 0

GRAVITY   = 1600.0
FLAP_V    = -520.0
MAX_FALL  = 700.0

SCROLL_BASE = 160.0
SCROLL_MAX  = 290.0

PIPE_W        = 58
PIPE_SPACING  = 280
GAP_START     = 170
GAP_MIN       = 115

BIRD_X = 90
BIRD_R = 14

# Pip carries the parcel for the entire run. The parcel's collision
# footprint is a second circle below the bird; pillars touching that
# circle are also lethal.
PARCEL_R          = 9    # forgiving (parcel sprite is 22 px so r=11 would catch its corners)
PARCEL_Y_OFFSET   = 12   # px below bird-centre to parcel-centre (matches intro composition)

COIN_R             = 13

# Coin-rush: every Nth pipe gets a wider gap filled with a dense coin arc.
COIN_RUSH_INTERVAL = 15
COIN_RUSH_GAP_BOOST = 1.30
COIN_RUSH_COINS    = 14

POWERUP_R          = 14    # collision + footprint radius for every power-up
POWERUP_CHANCE     = 0.24  # chance to spawn a power-up after a pipe gate
POWERUP_CHANCE_NEWBIE = 0.10  # warmup starting chance; ramps to POWERUP_CHANCE
                              # on the same _ramp_t() curve as gap/scroll/spacing
                              # so the opening doesn't feel like a powerup parade
POWERUP_COOLDOWN   = 5.5   # min seconds between power-up spawns
TRIPLE_DURATION    = 8.0
MAGNET_DURATION    = 8.0
MAGNET_RADIUS      = 82.0
# Megamagnet — the late-game upgrade form of `magnet`. Same duration,
# 2x pull radius. Magnet is REPLACED by megamagnet at the score
# threshold below — both never spawn simultaneously (see
# POWERUP_REPLACED_AT + the spawn filter in World._maybe_spawn_powerup).
MEGAMAGNET_DURATION = 8.0
MEGAMAGNET_RADIUS   = MAGNET_RADIUS * 2.0   # = 164
SLOWMO_DURATION    = 8.0
SLOWMO_SCALE       = 0.7
KFC_DURATION       = 8.0
KFC_GAP_BOOST      = 1.30    # gap_h multiplier on KFC-flagged pipes - makes
                             # the powerup feel as generous as the bucket
                             # variant already looks. Stacks with COIN_RUSH.
GHOST_DURATION     = 8.0
GROW_DURATION      = 8.0
GROW_SCALE         = 1.4
REVERSE_DURATION   = 8.0
SHRINK_DURATION    = 8.0
SHRINK_SCALE       = 0.6
SHRINK_TRANSITION  = 0.45
RAIL_PILLAR_COUNT  = 5       # cart rides over exactly N pillars then releases
RAIL_SCROLL_MULT   = 2.5     # world scrolls 2.5x faster during the ride
# Lottery tiers: (label, weight, coin_delta). Weights need not sum to anything
# — normalized at pick time. Loss tiers clamp at score 0 (see
# World._apply_lottery_result), so total coins never go negative.
LOTTERY_TIERS = (
    ("JACKPOT",  5,  100),
    ("BIG WIN", 12,   40),
    ("WIN",     20,   15),
    ("NOTHING", 35,    0),
    ("LOSS",    20,  -10),
    ("BUST",     8,  -50),
)
LOTTERY_REVEAL_TIME = 1.0

# Spawn weights for power-up kinds. Must sum to anything — they're
# normalized at pick time. `surprise` resolves at pickup-time to one of
# the six "real" early-game kinds (triple/magnet/slowmo/kfc/ghost/shrink)
# chosen at random — see World._on_powerup.
# `reverse` is intentionally excluded — the implementation is kept in
# place but the power-up doesn't spawn or resolve from a surprise box.
# To re-enable: add ("reverse", 1) below AND restore "reverse" in the
# random.choice() inside World._on_powerup.
# `grow`, `rail`, and `lottery` are late-game late-game-gated (see
# POWERUP_SCORE_GATES below) and intentionally NOT in the surprise
# re-roll pool — letting surprise bypass the gate would defeat the
# purpose of the gate.
POWERUP_WEIGHTS    = (
    ("triple",     1),
    ("slowmo",     1),
    ("magnet",     1),
    ("kfc",        1),
    ("ghost",      1),
    ("shrink",     1),
    ("surprise",   1),
    ("grow",       1),
    ("rail",       1),
    ("lottery",    1),
    ("megamagnet", 1),
)

# Per-kind minimum score before a power-up enters the spawn roll.
# Filter applied in World._maybe_spawn_powerup. Omitted kinds are
# unrestricted (gate of 0). Lets late-game pickups stay rare for new
# players while showing up reliably once the run has built momentum.
POWERUP_SCORE_GATES = {
    "rail":       100,
    "grow":       200,
    "lottery":    250,
    "megamagnet": 250,
}

# Per-kind score at which the kind is REMOVED from the spawn pool.
# Used to implement upgrade-style swaps: when the run hits this
# score, the listed kind stops spawning (presumably replaced by an
# upgraded variant that gates IN at the same score). Filter applied
# in World._maybe_spawn_powerup alongside POWERUP_SCORE_GATES.
POWERUP_REPLACED_AT = {
    "magnet": 250,   # at 250+, megamagnet (radius 2x) takes over
}

# ── Secret late-game power-ups ───────────────────────────────────────────────
# A separate, undeclared tier that only enters the spawn roll once the run
# crosses LATE_GAME_SCORE. Kept out of POWERUP_WEIGHTS (and the Surprise
# re-roll) so the gate can't be bypassed, and out of the help screen so the
# roster stays a surprise. Weights are normalized at pick time alongside the
# normal pool.
LATE_GAME_SCORE        = 500
SECRET_POWERUP_WEIGHTS = (
    ("skateboard", 0.125),
    ("phoenix",    0.125),   # survive-one-hit buff, reskinned as the Knight
    ("genie",      0.125),
)

# GENIE — picking up the lamp summons a conjurer who lays out GENIE_OFFER_COUNT
# alternate power-ups ahead of Pip; flying into one claims it and poofs the rest.
GENIE_OFFER_COUNT   = 3
GENIE_OFFER_X_START = 200
GENIE_OFFER_X_STEP  = 60
GENIE_OFFER_Y_SLOTS = (220, 320, 420)

# SKATEBOARD — timed grind/slide buff. The world scrolls faster while Pip is
# actually grinding a surface; the boost eases in over SKATE_SLIDE_ATTACK and
# fades over SKATE_SLIDE_RELEASE so it reads as "skate rush, gentle coast".
# Flapping while skating spins a backflip trick.
SKATEBOARD_DURATION = 8.0
SKATE_SLIDE_MULT    = 1.5
SKATE_SLIDE_ATTACK  = 0.18
SKATE_SLIDE_RELEASE = 0.55
BACKFLIP_DURATION   = 0.85

# KNIGHT — survive-one-hit buff (internally the "phoenix" kind, locked to the
# knight variant). While active the next lethal hit is consumed and Pip is
# revived with PHOENIX_INVULN seconds of collision grace.
PHOENIX_DURATION    = 30.0
PHOENIX_INVULN      = 1.5
PHOENIX_VARIANT     = "knight"

# ── Pipe collision (hitbox forgiveness) ──────────────────────────────────────
# Effective bird radius for pipe collisions = BIRD_R - PIPE_HITBOX_SHRINK.
# Was 12 px (BIRD_R - 2); 10 px makes pillars feel less magnetic without
# letting the bird visibly clip through.
PIPE_HITBOX_SHRINK = 4

# ── Onboarding warmup ramp ──────────────────────────────────────────────────
# Keyed on pillars_passed: every pipe scored nudges the gap, scroll, and
# spacing one notch closer to the regular endpoints (GAP_START / SCROLL_BASE
# / PIPE_SPACING). After RAMP_PIPES the ramp is complete and the game stays
# at today's regular tuning forever — no late-game tightening to GAP_MIN /
# SCROLL_MAX.
RAMP_PIPES           = 25
# Pillars at the very start of a run that hold the full newbie tuning
# (gap / scroll / spacing / powerup chance) flat before the ease-out ramp
# in World._ramp_t kicks in. Gives complete first-timers a short
# predictable runway to internalize flap timing without anything
# tightening underneath them. Five pillars is ~15 s at PIPE_SPACING_NEWBIE
# / SCROLL_NEWBIE_BASE — short enough that experienced players don't
# perceive a "tutorial mode."
PLATEAU_PIPES        = 5
GAP_NEWBIE_START     = 225
SCROLL_NEWBIE_BASE   = 125.0
PIPE_SPACING_NEWBIE  = 370

SAVE_FILE = "skybit_save.json"
SCORES_FILE = "skybit_scores.json"
