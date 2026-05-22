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
# 1.0 → GROW_SCALE on activation, GROW_SCALE → 1.0 on expiry. ~0.20s
# / ~12-frame arc. Collisions snap to GROW_SCALE on frame 1
# (World.bird_radius / pipe overlap); only the visible sprite eases.
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
    # TEST MODE on v5_powerups: Genie is normally late-game
    # (SECRET_POWERUP_WEIGHTS). Promoted to the early pool so testers
    # see it from pillar #1. Remove to restore default behaviour.
    ("genie",    1),
)

# ── SECRET LATE-GAME POWER-UPS ───────────────────────────────────────────────
# These intentionally do NOT appear in game/powerup_help.py — players are meant
# to discover them organically in a deep run. They only enter the spawn pool
# once score >= LATE_GAME_SCORE. They never resolve from a `surprise`
# box either; each has its own roll so the visual is always genuinely new.
LATE_GAME_SCORE       = 500

SKATEBOARD_DURATION   = 8.0
# SKATEBOARD trick: 3 taps with no more than this many seconds between
# consecutive taps trigger a 360° backflip. New flips cannot chain
# until the current one finishes.
BACKFLIP_TAP_WINDOW   = 0.45
# Bumped 0.55 → 0.85 s so the flip reads as a deliberate trick rather
# than a quick spin. Pairs with smootherstep easing in Bird.tilt_deg
# so the rotation is slow→fast→slow instead of constant-rate.
BACKFLIP_DURATION     = 0.85
# SKATEBOARD trick: 2 taps with a deliberate "slow" rhythm trigger
# a kickflip — the deck spins 360° under Pip's feet while he stays
# upright. The gap window starts above BACKFLIP_TAP_WINDOW so the
# kickflip detector and the 3-fast-tap backflip streak never alias
# into each other.
KICKFLIP_TAP_GAP_MIN  = 0.55
KICKFLIP_TAP_GAP_MAX  = 0.75
KICKFLIP_DURATION     = 0.55
# SKATEBOARD trick: 2 MEDIUM taps (gap above the backflip-fast
# ceiling, below the kickflip-slow floor) trigger a Pop Shuvit —
# the deck does a 180° flat-spin around the vertical axis under
# Pip's feet. Narrow 0.08 s window so the rhythm is deliberate
# and never aliases into the fast / slow patterns.
POPSHUVIT_TAP_GAP_MIN = 0.46
POPSHUVIT_TAP_GAP_MAX = 0.54
POPSHUVIT_DURATION    = 0.45
# SKATEBOARD trick: 2 VERY-SLOW taps (gap above the kickflip-slow
# ceiling) trigger a Heelflip — the deck spins 360° in the
# OPPOSITE direction to a kickflip. Disjoint from kickflip's
# window so the player has to deliberately slow down to summon
# the mirror version.
HEELFLIP_TAP_GAP_MIN  = 0.85
HEELFLIP_TAP_GAP_MAX  = 1.05
HEELFLIP_DURATION     = 0.55
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
    # TEST MODE on v5_powerups: Heist temporarily removed from the
    # spawn pool while QA focuses on the other powerups. Code
    # (activator, treasure-box art, audio, score-from-flap mechanic,
    # plausibility ledger) is intact — re-add the line below to
    # restore: ("heist", 0.125),
    ("lottery",    0.125),
    # TEST MODE on v5_powerups: Phoenix temporarily removed from the
    # spawn pool so it doesn't claim a secret-roll slot while QA
    # focuses on the other powerups. Code (activator, halo variants,
    # audio, plausibility ledger) is intact — re-add the line below
    # to restore: ("phoenix", 0.125),
    ("genie",      0.125),
)

# ── Genie Lamp tuning ────────────────────────────────────────────────────────
# On pickup the Genie spawns N "offer" pickups ahead of Pip — unique
# random kinds — and the first one Pip touches activates while the
# other two disappear in a puff. Offers are tagged is_genie_offer so
# the cleanup is targeted (a normal-spawn powerup nearby is safe).
GENIE_OFFER_COUNT       = 3
GENIE_OFFER_X_START     = 200   # px ahead of bird.x for the first offer
GENIE_OFFER_X_STEP      = 60    # spacing between offers along x
GENIE_OFFER_Y_SLOTS     = (220, 320, 420)  # mid-band y positions, top→bottom

# ── v5_powerups TEST MODE — REMOVE before merging to v4/main ─────────────────
# Bypasses the score>=500 gate so QA can verify every secret powerup quickly.
# Set TEST_SECRETS_FIRST_N_PILLARS = 0 to disable the forced spawn.
TEST_SECRETS_FIRST_N_PILLARS = 15   # first N pillars guarantee a secret pickup

# Forced-spawn pool used during the test-mode window — every secret in
# SECRET_POWERUP_WEIGHTS, equal weight per kind so the 15-pillar window
# samples each at least once with reasonable probability.
TEST_FORCED_KINDS = (
    "skateboard",
    # "heist" + "phoenix" temporarily out — see SECRET_POWERUP_WEIGHTS comment.
    "lottery", "genie",
)

# v5_powerups test-mode runs ship with a fake 250-score / 250-coin
# bootstrap (see World.__init__) so any submitted score / play-log
# from this branch would be junk in the real leaderboard + telemetry
# tables. Gate both submit paths off here. Set to False to restore.
TEST_MODE_NO_SUBMIT = True

# ── Pipe collision (hitbox forgiveness) ──────────────────────────────────────
# Effective bird radius for pipe collisions = BIRD_R - PIPE_HITBOX_SHRINK.
# Was 12 px (BIRD_R - 2); 10 px makes pillars feel less magnetic without
# letting the bird visibly clip through.
PIPE_HITBOX_SHRINK = 4

# ── Weather → gameplay ──────────────────────────────────────────────────────
# Layer 1 of weather-as-input: light rain wobbles coins, heavy rain slides
# them and shivers Pip + dampens his flap. All values derived from
# weather.rain_intensity(phase) which already exists.
WEATHER_HEAVY_THRESHOLD  = 0.5
# Peak left-right shake amplitude at rain_intensity = 1.0. Scales
# linearly with rain intensity so the tremor grows smoothly from
# barely-there at first drizzle (≈ 0.4 px at ri=0.1) to clearly
# violent at peak storm (4.0 px). No vertical drift, no sliding —
# the wobble is the ONLY weather effect on coins.
WEATHER_COIN_SHAKE_AMP   = 4.0
WEATHER_PIP_SHIVER_AMP   = 1.5
WEATHER_FLAP_DAMPEN_MAX  = 0.18

# ── Onboarding warmup ramp ──────────────────────────────────────────────────
# Keyed on pillars_passed: every pipe scored nudges the gap, scroll, and
# spacing one notch closer to the regular endpoints (GAP_START / SCROLL_BASE
# / PIPE_SPACING). After RAMP_PIPES the ramp is complete and the game stays
# at today's regular tuning forever — no late-game tightening to GAP_MIN /
# SCROLL_MAX.
# TEST MODE on v5_powerups: newbie ramp disabled — game starts at
# regular speed/gap/spacing from pillar #1. _ramp_t() short-circuits
# to 1.0 when RAMP_PIPES == 0. Restore defaults (RAMP_PIPES = 25,
# PLATEAU_PIPES = 5) to re-enable the warmup curve.
RAMP_PIPES           = 0
PLATEAU_PIPES        = 0
GAP_NEWBIE_START     = 225
SCROLL_NEWBIE_BASE   = 125.0
PIPE_SPACING_NEWBIE  = 370

SAVE_FILE = "skybit_save.json"
SCORES_FILE = "skybit_scores.json"
