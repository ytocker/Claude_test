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
SLOWMO_DURATION    = 8.0
SLOWMO_SCALE       = 0.7
KFC_DURATION       = 8.0
KFC_GAP_BOOST      = 1.30    # gap_h multiplier on KFC-flagged pipes - makes
                             # the powerup feel as generous as the bucket
                             # variant already looks. Stacks with COIN_RUSH.
GHOST_DURATION     = 8.0
GROW_DURATION      = 8.0
GROW_SCALE         = 1.3
# Mirror of SHRINK_TRANSITION but running the opposite direction
# (1.0 → GROW_SCALE on activation, GROW_SCALE → 1.0 on expiry). Same
# 0.20s / ~12-frame arc so the two pickups feel like a matched pair.
# Collisions snap to GROW_SCALE on frame 1 (World.bird_radius / pipe
# overlap); only the visible sprite eases.
GROW_TRANSITION    = 0.20
REVERSE_DURATION   = 8.0

# Spawn weights for power-up kinds. Must sum to anything — they're
# normalized at pick time. `surprise` resolves at pickup-time to one of
# the six "real" kinds chosen at random (see World._on_powerup).
# `reverse` is intentionally excluded — the implementation is kept in
# place but the power-up doesn't spawn or resolve from a surprise box.
# To re-enable: add ("reverse", 1) below AND restore "reverse" in the
# random.choice() inside World._on_powerup.
POWERUP_WEIGHTS    = (
    ("triple",   1),
    ("slowmo",   1),
    ("magnet",   1),
    ("kfc",      1),
    ("ghost",    1),
    ("grow",     1),
    ("surprise", 1),
)

# ── SECRET LATE-GAME POWER-UPS ───────────────────────────────────────────────
# These intentionally do NOT appear in game/powerup_help.py — players are meant
# to discover them organically in a deep run. They only enter the spawn pool
# once score >= LATE_GAME_SCORE (nightglow is additionally biome-gated to
# night in World._maybe_spawn_powerup). They never resolve from a `surprise`
# box either; each has its own roll so the visual is always genuinely new.
LATE_GAME_SCORE       = 500

SHRINK_DURATION       = 8.0
SHRINK_SCALE          = 0.6
# Bird sprite eases between 1.0 and SHRINK_SCALE over this many seconds
# when the buff turns on/off — ~12 frames at 60 FPS. Collisions snap on
# frame 1 (see World.bird_radius / Bird vs Pipe collision) so the gameplay
# benefit is immediate; only the visible scale animates.
SHRINK_TRANSITION     = 0.20
SKATEBOARD_DURATION   = 8.0
NIGHTGLOW_DURATION    = 12.0
RAIL_PILLAR_COUNT     = 7       # number of pillars the rail spans
# TREASURE BOX (formerly BANK HEIST): Pip carries the locked chest under
# his belly for TREASURE_BOX_DURATION seconds. Each flap rattles a coin
# loose — the player instantly gains TREASURE_BOX_COINS_PER_FLAP coins
# (multiplied by 3 if the triple buff is also active). No vault attached
# to a pillar anymore; the value is now paced over the buff's lifetime
# instead of paid out in a single brush.
TREASURE_BOX_DURATION       = 8.0
TREASURE_BOX_COINS_PER_FLAP = 2
VACUUM_TRAVEL_TIME    = 0.4

# Lottery tiers: (label, weight, coin_delta). NOTHING is the modal
# outcome (35 %); roughly 37 % of spins win, 28 % lose, 35 % zero. With
# BUST at -50 a deep loss wipes ~7 average spins of progress, which
# makes the gamble feel real instead of a guaranteed payday. EV per
# spin works out to +6.8 coins — slightly positive so the powerup is
# rewarding overall. Losses still cap at the player's current score so
# total coins never go negative (see World._apply_lottery_result).
LOTTERY_TIERS = (
    ("JACKPOT",  5,  100),
    ("BIG WIN", 12,   40),
    ("WIN",     20,   15),
    ("NOTHING", 35,    0),
    ("LOSS",    20,  -10),
    ("BUST",     8,  -50),
)
LOTTERY_REVEAL_TIME   = 1.0

# Each secret is 1/8 the weight of a normal powerup. With 8 secrets eligible
# and 7 normal weights summing to 7, total secret-pickup probability is
# ~12.5% per spawn after the threshold.
SECRET_POWERUP_WEIGHTS = (
    ("skateboard", 0.125),
    ("shrink",     0.125),
    ("heist",      0.125),
    ("vacuum",     0.125),
    ("rail",       0.125),
    ("nightglow",  0.125),   # additionally biome-gated to night in world.py
    ("lottery",    0.125),
)

# ── v5_powerups TEST MODE — REMOVE before merging to v4/main ─────────────────
# Bypasses the score>=500 gate so QA can verify every secret powerup quickly.
# Set TEST_SECRETS_FIRST_N_PILLARS = 0 to disable the forced spawn.
# Set TEST_START_AT_NIGHT = False to keep the normal day-start.
TEST_SECRETS_FIRST_N_PILLARS = 15   # first N pillars guarantee a secret pickup
TEST_START_AT_NIGHT          = True  # start at NIGHT biome so nightglow is eligible

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
