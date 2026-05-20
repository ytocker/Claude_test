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
# once score >= LATE_GAME_SCORE. They never resolve from a `surprise`
# box either; each has its own roll so the visual is always genuinely new.
LATE_GAME_SCORE       = 500

SHRINK_DURATION       = 8.0
SHRINK_SCALE          = 0.6
# Bird sprite eases between 1.0 and SHRINK_SCALE over this many seconds
# when the buff turns on/off — ~27 frames at 60 FPS so the morph is
# clearly visible during play (the previous 0.20 s / 12-frame ramp went
# by too quickly to read). Collisions snap on frame 1 (see
# World.bird_radius / Bird vs Pipe collision) so the gameplay benefit
# is immediate; only the visible scale animates.
SHRINK_TRANSITION     = 0.45
SKATEBOARD_DURATION   = 8.0
# SKATEBOARD trick: 3 taps with no more than this many seconds between
# consecutive taps trigger a 360° backflip. New flips cannot chain
# until the current one finishes.
BACKFLIP_TAP_WINDOW   = 0.45
# Bumped 0.55 → 0.85 s so the flip reads as a deliberate trick rather
# than a quick spin. Pairs with smootherstep easing in Bird.tilt_deg
# so the rotation is slow→fast→slow instead of constant-rate.
BACKFLIP_DURATION     = 0.85
# PHOENIX: 30-second fiery transformation. If Pip would die during the
# window, World._die() intercepts the death, ends the buff, and grants
# PHOENIX_INVULN seconds of grace so the just-revived bird doesn't
# instantly re-collide with the pillar that killed him.
PHOENIX_DURATION      = 30.0
PHOENIX_INVULN        = 1.5
# Visual / perk flavour for the phoenix powerup. The canonical pick
# is "eternal_warm" — slim Imperial-fire body, graceful S-curve wing
# pose, 4-plume cascade ribbon-tail, brighter mid-red palette (less
# blood-crimson, so it reads as a flying phoenix rather than ominous).
# All variants share the 30s / one-shot / death-intercept gameplay
# core; alternatives are kept behind this switch for fast A/B testing
# without branching.
#
# Original 5 (legacy 64×60 canvas — tinted Pip):
#   "classic" — red→gold tint, fire halo, no extra perk.
#   "solar"   — gold-white tint, sun-ray halo, weak coin magnet.
#   "ember"   — fiery tint + ember trail, coins worth 2x during phoenix.
#   "mythic"  — 5-plume crown, plume tail, egg-crack rebirth.
#   "ashes"   — egg-and-ash rebirth animation.
#
# Grandiose 5 (100×76 canvas, hand-painted — non-Pip silhouettes):
#   "imperial"  — eagle-of-fire, full-width spread wings.
#   "fenghuang" — Eastern phoenix, 7-plume peacock fan-tail.
#   "dragon"    — sinuous body, flame banner wings, wispy tail.
#   "comet"     — small bird pulling a massive flame-trail tail.
#   "royal"     — halo-crown of 9 plumes radiating around the head.
#
# Fire-fenghuang 5 (Imperial palette + Fenghuang posture):
#   "blaze" / "sunburst" / "twin" / "swift" / "grand"
#
# Wide-wing Grand-lineage 5 (long wings + short cascade tail — fixes
# the "turkey" tail-fan of the fire-fenghuang lot):
#   "soar" / "rise" / "stoop" / "dive" / "eternal"
#
# Less-creepy Eternal iterations (eternal_warm is canonical):
#   "eternal_warm"   — brighter mid-red palette, classic silhouette ★
#   "eternal_soft"   — rounded feather tips, lighter shadow
#   "eternal_dawn"   — daybreak palette, shorter tail
#   "eternal_friend" — friendlier face (bigger eye, soft beak)
#   "eternal_lite"   — all-in: warm + rounded + short + friendly
PHOENIX_VARIANT       = "eternal_warm"
RAIL_PILLAR_COUNT     = 5       # cart rides over exactly N pillars then releases
RAIL_SCROLL_MULT      = 2.5     # world scrolls 2.5x faster during the ride
# SKATEBOARD slide boost — world scrolls faster while Pip is
# actually grinding a surface (ground, pillar top, or ramp).
# Ramps up over SKATE_SLIDE_ATTACK and decays over
# SKATE_SLIDE_RELEASE when Pip jumps off, so the boost reads as a
# smooth "skate rush, gentle coast" rather than a hard speed snap.
SKATE_SLIDE_MULT      = 1.5
SKATE_SLIDE_ATTACK    = 0.18
SKATE_SLIDE_RELEASE   = 0.55
# TREASURE BOX (formerly BANK HEIST): Pip carries the locked chest under
# his belly for TREASURE_BOX_DURATION seconds. Each flap rattles a coin
# loose — the player instantly gains TREASURE_BOX_COINS_PER_FLAP coins
# (multiplied by 3 if the triple buff is also active). No vault attached
# to a pillar anymore; the value is now paced over the buff's lifetime
# instead of paid out in a single brush.
TREASURE_BOX_DURATION       = 8.0
TREASURE_BOX_COINS_PER_FLAP = 2

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

# Each secret is 1/8 the weight of a normal powerup. With 7 secrets eligible
# and 8 normal weights summing to 8, total secret-pickup probability is
# ~9.8% per spawn after the threshold.
SECRET_POWERUP_WEIGHTS = (
    ("skateboard", 0.125),
    ("shrink",     0.125),
    ("heist",      0.125),
    ("rail",       0.125),
    ("lottery",    0.125),
    ("phoenix",    0.125),
)

# ── v5_powerups TEST MODE — REMOVE before merging to v4/main ─────────────────
# Bypasses the score>=500 gate so QA can verify every secret powerup quickly.
# Set TEST_SECRETS_FIRST_N_PILLARS = 0 to disable the forced spawn.
TEST_SECRETS_FIRST_N_PILLARS = 15   # first N pillars guarantee a secret pickup

# Forced-spawn pool used during the test-mode window: every secret
# in SECRET_POWERUP_WEIGHTS, equal weight per kind so the 15-pillar
# window samples each at least once with reasonable probability.
TEST_FORCED_KINDS = (
    "skateboard", "shrink", "heist", "rail",
    "lottery", "phoenix",
)

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
