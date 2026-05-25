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

# Tailwind event (predawn, phase ~0.85). Two effects scaled by
# weather.wind_intensity(phase):
#   - WEATHER_WIND_LEAN_AMP: max RIGHTWARD visual x-offset on
#     the bird (in screen pixels) when wind = 1.0. Pure visual
#     — does not affect collision (Bird.x stays at BIRD_X).
#     Positive direction is rightward (ahead of normal), applied
#     via Bird.draw shake_x. At 8.0 px Pip's push is ~12% of his
#     64-px sprite width, clearly visible as "tailwind boost".
#   - WEATHER_WIND_SCROLL_FACTOR: max fraction the world scroll
#     is INCREASED at peak wind. At wind 1.0 the scroll runs at
#     (1 + factor) × normal so pipes/coins approach faster and
#     the player covers more distance per second. 0.30 means
#     30% more progress at peak — felt as a real boost.
WEATHER_WIND_LEAN_AMP     = 8.0
WEATHER_WIND_SCROLL_FACTOR = 0.30

# Snow accumulating on Pip's back during the snow squall. The
# tailwind blows snow onto him from behind, so a drift builds up
# over his rear. Modelled as an integrator on bird.snow_load
# (0..1):
#   gain = ACCUM * storm_intensity
#   melt = MELT_BASE + MELT_FADE * (1 - storm_intensity)
#   load += (gain - melt) * dt          (clamped 0..1)
# The melt ACCELERATES as the storm fades: barely any while it's
# snowing hard (so snow piles up), ramping up sharply once the
# storm passes — so the snow STARTS coming off sooner and clears
# quickly instead of lingering. Tuned so load peaks just after the
# storm's own peak, begins fading ~mid-decline, and is gone close
# to when the storm ends.
WEATHER_SNOW_ACCUM_RATE = 0.12
WEATHER_SNOW_MELT_BASE  = 0.025   # melt while snowing hard
WEATHER_SNOW_MELT_FADE  = 0.16    # extra melt as the storm fades out

# ── Morning-thermal geysers ─────────────────────────────────────────────────
# Ground geysers spawned during the thermal window. Spawn density + how many
# appear at once (1→GEYSER_MAX_CONCURRENT) scale with the live intensity, so
# they build sparse→busy toward the ~96s peak. Each geyser, once spawned, is
# ALWAYS erupting: a continuous wind column that reaches the top of the screen
# and a STRONG continuous updraft. Anywhere inside the column's width — at any
# height, all the way up — the air pushes Pip upward (he rides it to the top;
# the ceiling clamps him, it never kills). The push is capped only in SPEED so
# the ride stays readable, not in reach.
THERMAL_SPAWN_THRESHOLD  = 0.08   # legacy floor (kept; geyser gate uses the threshold below)
THERMAL_SPAWN_CHANCE_MAX = 0.85   # per-pillar geyser spawn chance at peak intensity
GEYSER_SPAWN_THRESHOLD   = 0.35   # intensity above which GEYSERS (not just rocks) spawn
GEYSER_MAX_CONCURRENT    = 3      # cap on simultaneous geysers (allowed scales 1→3 with intensity)
ROCK_SPAWN_THRESHOLD     = 0.02   # intensity above which scattered sinter rocks appear
ROCK_SLOTS_PER_PILLAR    = 5      # candidate rock slots rolled per pillar; each fills with prob = intensity
GEYSER_W            = 84.0        # column / lift width (px) — matches the visible air footprint
GEYSER_H            = float(GROUND_Y)  # column reaches the top of the screen; lift acts the full height
GEYSER_LIFT_VY_CAP  = 280.0       # CONSTANT rise speed: inside ANY column Pip rises at exactly this — one constant for every geyser, no stacking, independent of how deep/long he's inside. Below |FLAP_V|=520 so a flap still overrides it.
GEYSER_ACTIVE_HOT   = 3.0         # active-window length at peak intensity (s)
GEYSER_ACTIVE_COLD  = 1.0         # active-window length at the sparse edges (s)
GEYSER_DORMANT_HOT  = 1.2         # dormant gap between actives at peak (s)
GEYSER_DORMANT_COLD = 7.0         # dormant gap at the sparse edges (s)
GEYSER_TELEGRAPH    = 0.5         # bubbling lead-in before the column rises (s)

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
