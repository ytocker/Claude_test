"""
World simulation: physics, spawner, collision, difficulty ramp.
Handles coin/mushroom pickup FX. IMPORTANT: coin pickup must NOT do a
full-screen flash (that was the 'glitch' the user saw) — only localized
sparkle particles around the coin.
"""
import math
import random
import pygame

from game.config import (
    W, H, GROUND_Y, PIPE_W, PIPE_SPACING,
    GAP_START, SCROLL_BASE,
    GAP_NEWBIE_START, SCROLL_NEWBIE_BASE, PIPE_SPACING_NEWBIE, RAMP_PIPES,
    PLATEAU_PIPES,
    PIPE_HITBOX_SHRINK,
    BIRD_X, BIRD_R, COIN_R, POWERUP_R, PARCEL_R, PARCEL_Y_OFFSET,
    POWERUP_CHANCE, POWERUP_CHANCE_NEWBIE, POWERUP_COOLDOWN,
    TRIPLE_DURATION, MAGNET_DURATION, MAGNET_RADIUS,
    SLOWMO_DURATION, SLOWMO_SCALE, KFC_DURATION, KFC_GAP_BOOST, GHOST_DURATION,
    GROW_DURATION, GROW_SCALE, REVERSE_DURATION,
    POWERUP_WEIGHTS,
    COIN_RUSH_INTERVAL, COIN_RUSH_GAP_BOOST, COIN_RUSH_COINS,
    # Secret late-game powerups
    LATE_GAME_SCORE, SECRET_POWERUP_WEIGHTS,
    SKATEBOARD_DURATION, BACKFLIP_TAP_WINDOW, BACKFLIP_DURATION,
    KICKFLIP_TAP_GAP_MIN, KICKFLIP_TAP_GAP_MAX, KICKFLIP_DURATION,
    POPSHUVIT_TAP_GAP_MIN, POPSHUVIT_TAP_GAP_MAX, POPSHUVIT_DURATION,
    HEELFLIP_TAP_GAP_MIN, HEELFLIP_TAP_GAP_MAX, HEELFLIP_DURATION,
    PHOENIX_DURATION, PHOENIX_INVULN, PHOENIX_VARIANT,
    SKATE_SLIDE_MULT, SKATE_SLIDE_ATTACK, SKATE_SLIDE_RELEASE,
    TREASURE_BOX_DURATION, TREASURE_BOX_COINS_PER_FLAP,
    LOTTERY_TIERS, LOTTERY_REVEAL_TIME,
    TEST_SECRETS_FIRST_N_PILLARS, TEST_FORCED_KINDS,
    FLAP_V,
    WEATHER_HEAVY_THRESHOLD, WEATHER_COIN_SHAKE_AMP,
    WEATHER_PIP_SHIVER_AMP, WEATHER_FLAP_DAMPEN_MAX,
    GENIE_OFFER_COUNT, GENIE_OFFER_X_START,
    GENIE_OFFER_X_STEP, GENIE_OFFER_Y_SLOTS,
)
from game.entities import (
    Bird, Pipe, Coin, PowerUp, Particle, CloudPuff, FloatText,
    TreasureCoinParticle, FlyingCoinParticle, Ramp, TrickBubble,
)
from game._proof import ProofState
from game.draw import (
    COIN_GOLD, COIN_LIGHT,
    PARTICLE_GOLD, PARTICLE_ORNG, PARTICLE_WHT, PARTICLE_CRIM,
    UI_GOLD, UI_ORANGE, UI_CREAM, UI_RED, WHITE, BIRD_RED,
)
from game import biome
from game import audio
from game.weather import Weather, rain_intensity as _rain_intensity
from game.ambient import AmbientScenes


def _lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))


class World:
    # Seconds AFTER the ready_t (1.0 s) freeze before the first pipe should
    # enter the visible frame. The intro hands gameplay the cottage + parcel
    # composition; this grace period gives the opener overlay time to scroll
    # the cottage off-screen before pillars take over.
    SPAWN_GRACE = 1.5

    def __init__(self):
        # Reshuffle the meadow at the start of every new World — picks a
        # fresh ground theme + sparsity baseline + decoration positions
        # so no two plays look the same.
        from game import ground_variants
        ground_variants.set_run_seed(None)

        self.bird = Bird()
        self.pipes: list[Pipe] = []
        self.coins: list[Coin] = []
        self.powerups: list[PowerUp] = []
        self.particles: list[Particle] = []
        # Genie cinematic actors — translucent characters that hover
        # ahead of Pip and conjure the three offer powerups in sequence
        # when the Genie lamp is collected. Ticked + drawn parallel to
        # particles. See game/entities.py GenieCharacter.
        self.genie_actors: list = []
        self.float_texts: list[FloatText] = []
        # SKATEBOARD trick bubbles — comic halftone bursts that
        # stack/overlay at a fixed anchor near the E3 score whenever
        # Pip performs a kick/heel/pop/back-flip or a nose/tail grind.
        self.trick_bubbles: list = []
        # Uniform Y offset applied to all SKATEBOARD-effect overlays
        # (banner caption, E3 score, timer bar, trick-bubble anchor).
        # Positive value lifts the whole stack UPWARD by N pixels.
        # 26 was picked from the lift-variant render set
        # (docs/screenshots/skateboard_lift_variants/) — comfortably
        # clears the play area without crowding the top edge.
        self._skateboard_lift_y = 26

        self.scroll_speed = SCROLL_BASE
        self.bg_scroll = 0.0

        # TEST MODE on v5_powerups: fake starting score + coin count so
        # the storm jolt has coins to lose and gated content unlocks
        # closer to play. Restore both to 0 to ship realistically.
        self.score = 250
        self.coin_count = 250

        self.triple_timer = 0.0
        self.magnet_timer = 0.0
        self.slowmo_timer = 0.0
        self.kfc_timer    = 0.0
        # Random index into KFC_MOUNTAIN_DRAWERS, refreshed on each
        # _activate_kfc call so the background fries-pile style varies
        # between powerup activations. `kfc_mountain_layers` holds the
        # three pre-rendered per-parallax-layer Surfaces;
        # `kfc_activation_scroll` snapshots bg_scroll at pickup time so
        # PlayScene can compute the parallax offset for each layer and
        # make the fries pile drift at the same speed as the normal
        # mountains do.
        self.kfc_mountain_variant = 0
        self.kfc_mountain_layers: "list[pygame.Surface] | None" = None
        self.kfc_activation_scroll = 0.0
        self.ghost_timer  = 0.0
        self.grow_timer   = 0.0
        self.reverse_timer = 0.0
        self.powerup_cooldown = 0.0

        # ── SECRET LATE-GAME POWER-UP STATE ─────────────────────────────────
        # Each is gated on score >= LATE_GAME_SCORE (see _maybe_spawn_powerup).
        # Undocumented in powerup_help.py by design.
        self.skateboard_timer = 0.0
        # One-shot activation FX (chosen V4.3 starburst + caption + POW!
        # composition, see game/skateboard_fx.py). Split into two
        # timed pieces — caption (static at top, lingers ~2.5 s) and
        # spike burst (small surface that follows Pip's screen
        # position for ~0.6 s).
        self.skateboard_caption_t = 0.0
        self.skateboard_caption_dur = 0.0
        self.skateboard_caption_overlay = None
        self.skateboard_burst_t = 0.0
        self.skateboard_burst_dur = 0.0
        self.skateboard_burst_surface = None
        # Screen position where the burst was anchored at pickup. Saved
        # once at activation; scenes blits the burst at this fixed
        # point so the spikes stay where they first appeared instead
        # of trailing Pip around.
        self.skateboard_burst_cx = 0
        self.skateboard_burst_cy = 0
        # SKATEBOARD ramps — wooden wedges on the ground that Pip
        # can skate up. Spawned per-pipe during the skateboard
        # window (max 1 per pillar gap, some gaps skipped).
        self.ramps: list = []
        # SKATEBOARD slide boost — 0.0 = normal speed, 1.0 = full
        # SKATE_SLIDE_MULT scroll. Ramps up while Pip is grinding a
        # surface and decays when he goes airborne.
        self.slide_boost = 0.0
        self._sliding_this_frame = False
        # Previous-frame snapshot used to detect rising-edge
        # (landing) and falling-edge (lift-off) transitions for the
        # random-grind feature.
        self._sliding_prev_frame = False
        # Backflip trick: 3 fast taps during the skateboard window spin
        # Pip 360°. _last_tap_t / _tap_streak track the streak; a flip is
        # only triggered when the streak reaches 3 and no flip is mid-air.
        self._last_tap_t = -999.0
        self._tap_streak = 0
        # PHOENIX: 30 s fiery skin + one-shot death revive. While
        # phoenix_timer > 0 the bird sprite renders as a phoenix and the
        # next call to _die() is suppressed (ends the buff + grants
        # phoenix_invuln seconds of collision grace).
        self.phoenix_timer    = 0.0
        self.phoenix_invuln   = 0.0
        # phoenix_rebirth: optional state dict for variants whose revive
        # plays out over multiple frames (mythic: 0.6 s pause; ashes:
        # 0.8 s ash-fall + egg-fall + auto-position). None when no
        # rebirth is in progress. See _resolve_phoenix_rebirth.
        self.phoenix_rebirth: "dict | None" = None
        # Treasure box (formerly BANK HEIST): a duration-based buff. While
        # treasure_box_timer > 0 the chest hangs under Pip's belly and
        # each flap drops TREASURE_BOX_COINS_PER_FLAP coins straight into
        # his score (scaled by triple if also active).
        self.treasure_box_timer = 0.0
        # Lottery reveal animation. None when not rolling; a dict {t, tier,
        # delta} while the scratch-card reels are ticking.
        self.lottery_anim: dict | None = None

        # Coin-rush counter: increments each spawn; every Nth pipe is a rush.
        self.pipes_spawned = 0

        # Per-run stats surfaced on the post-game summary.
        self.pillars_passed = 0
        self.time_alive = 0.0
        self.near_misses = 0
        self.flap_count = 0
        # Every Coin construction increments this; the stats screen uses
        # coin_count / max(1, coins_spawned - len(coins)) as the "% of
        # encountered coins grabbed" figure (coins still on screen don't
        # count as missed yet).
        self.coins_spawned = 0
        self.powerups_picked = {
            "triple": 0, "magnet": 0, "slowmo": 0, "kfc": 0, "ghost": 0,
            "grow": 0, "reverse": 0, "surprise": 0,
            # Secret late-game kinds (still tracked so run summary can show
            # what was picked even though the help screen omits them).
            "skateboard": 0, "heist": 0,
            "lottery": 0,
            "phoenix": 0, "genie": 0,
        }
        # Transient flag so near-miss detection fires once per pillar.
        self._near_miss_flags: dict[int, bool] = {}

        self.hit_flash = 0.0    # death-only red tint, NOT coin
        self.shake_mag = 0.0
        self.shake_t = 0.0

        # Real elapsed gameplay seconds — drives the day/night biome cycle.
        # Held at 0 while ready_t > 0 so the sky doesn't tick over while
        # the player is still on the start-of-run prompt.
        # TEST MODE on v5_powerups: start at phase ~0.46 (heavy dusk
        # storm — rain_intensity ≈ 0.66, well above the 0.20 coin-shake
        # threshold so coins are visibly wobbling from frame 1, and
        # ~5-7 s of biome progression takes the rain past the 0.85
        # storm-jolt trigger so the lightning strike fires within the
        # first ~20 s of play). Restore to 0.0 for a normal noon-start.
        self.biome_time = biome.CYCLE_SECONDS * 0.46

        # Always-ticking clock used for purely-cosmetic idle animations
        # (bird bob during the ready wait) so they keep moving even while
        # biome_time is frozen.
        self._idle_t = 0.0

        # Tamper-evident parallel ledger of every scoring event in the
        # run. The leaderboard submission carries the proof state, not
        # ``self.score``, so a JS-side ``world.score = 99999`` does not
        # change what gets submitted.
        self._proof = ProofState()
        # TEST MODE on v5_powerups: backfill the ledger with the 250
        # fake coin events so plausibility (coin_count == # of coin
        # events) stays valid for the storm-jolt's negative event.
        # Remove when self.coin_count goes back to 0.
        for _ in range(self.coin_count):
            self._proof.record(0.0, 1, "coin")

        self.weather = Weather()
        # Storm jolt: at peak rain LIGHTNING STRIKES Pip — bolt cracks
        # down from the cloud line, world flashes, ~50 coins blast off
        # in a 360° spread. Random fire window while at peak; long
        # lockout after firing so the gag doesn't spam in a single storm.
        self._storm_jolt_lockout = 0.0
        # Active lightning bolt visual state. None when no strike is
        # in flight; otherwise a dict {path, life, life_max} that the
        # scene renderer reads to paint the bolt.
        self.lightning_strike = None
        # Seconds left of the "scorched" sub-state where dark smoke
        # wisps off Pip's body to sell the after-effect of the strike.
        self._lightning_scorch_t = 0.0
        self._scorch_smoke_accum = 0.0
        # Lightning-buildup state. When the storm-jolt trigger fires
        # we DON'T immediately strike Pip — we queue several background
        # bolts as a telegraph, then the final hit. List of
        # (clock_remaining_seconds, event_kind) tuples; `event_kind` is
        # "bg_left" | "bg_right" | "strike". `_storm_buildup_t` is the
        # running clock since the buildup started; events fire when
        # t >= the head item's scheduled time.
        self._storm_buildup_seq = []
        self._storm_buildup_t = 0.0
        self.ambient = AmbientScenes()

        # "Get ready" freeze at the start of a round: physics paused until
        # the player flaps or the timer expires. Gives new players a moment
        # to orient before the first pillar scrolls in (REVIEW.md finding).
        self.ready_t = 1.0

        self.game_over = False

        self._seed_first_pipes()

    # Back-compat: older snapshot/playtest scripts poke `world.mushrooms`.
    @property
    def mushrooms(self):
        return self.powerups

    @mushrooms.setter
    def mushrooms(self, value):
        self.powerups = value

    # ── difficulty ───────────────────────────────────────────────────────────

    def _ramp_t(self):
        # Plateau-then-ease-out onboarding curve. The first PLATEAU_PIPES
        # pillars hold the full newbie tuning so a brand-new player has a
        # short runway to internalize flap timing without anything
        # tightening underneath them. From there the ramp eases out
        # (1-(1-x)^2) so the bulk of the tightening lands in the middle
        # pillars and the last few settle gently into GAP_START /
        # SCROLL_BASE — no last-mile cliff right where a struggling player
        # is most fragile. Linear interpolation tested badly because its
        # biggest absolute deltas landed at the end of the ramp, exactly
        # the wrong place for newbies.
        # RAMP_PIPES <= 0 disables the ramp entirely (test-mode bootstrap
        # on v5_powerups) — every gameplay value collapses straight to
        # the regular endpoint from pillar #1.
        if RAMP_PIPES <= 0:
            return 1.0
        pp = self.pillars_passed
        if pp < PLATEAU_PIPES:
            return 0.0
        x = (pp - PLATEAU_PIPES) / max(1, RAMP_PIPES - PLATEAU_PIPES)
        x = min(1.0, x)
        return 1.0 - (1.0 - x) ** 2

    # ── biome ────────────────────────────────────────────────────────────────

    @property
    def biome_phase(self):
        return biome.phase_for_time(self.biome_time)

    @property
    def biome_palette(self):
        return biome.palette_for_phase(self.biome_phase)

    def _current_gap(self):
        return int(_lerp(GAP_NEWBIE_START, GAP_START, self._ramp_t()))

    def _current_scroll(self):
        base = _lerp(SCROLL_NEWBIE_BASE, SCROLL_BASE, self._ramp_t())
        # SKATEBOARD grind: lerp from 1.0 to SKATE_SLIDE_MULT based on
        # the slide-boost envelope so the speed-up eases in/out instead
        # of snapping.
        if self.slide_boost > 0:
            base *= 1.0 + self.slide_boost * (SKATE_SLIDE_MULT - 1.0)
        return base

    def _current_spacing(self):
        return int(_lerp(PIPE_SPACING_NEWBIE, PIPE_SPACING, self._ramp_t()))

    def _current_powerup_chance(self):
        return _lerp(POWERUP_CHANCE_NEWBIE, POWERUP_CHANCE, self._ramp_t())

    # ── spawning ─────────────────────────────────────────────────────────────

    def _seed_first_pipes(self):
        # Push the seed pipes further off-screen by SPAWN_GRACE seconds of
        # scroll so the gameplay opener (cottage + parcel) has clean air
        # behind Pip before the first pillar arrives.
        offset = int(self.SPAWN_GRACE * SCROLL_BASE)
        x = W + 60 + offset
        spacing = self._current_spacing()
        for _ in range(3):
            self._spawn_pipe(x)
            x += spacing

    def _spawn_pipe(self, x):
        gap_h = self._current_gap()
        # Every Nth pipe is a "coin rush": wider gap + dense coin arc, no
        # power-up. The visual announcement fires below.
        self.pipes_spawned += 1
        is_rush = (self.pipes_spawned % COIN_RUSH_INTERVAL == 0)
        if is_rush:
            gap_h = int(gap_h * COIN_RUSH_GAP_BOOST)
        # Pipes spawned during KFC mode get a wider collision gap so the
        # powerup is an actual gameplay reward, not just visual flair.
        # Stacks with the rush boost if both happen on the same pipe.
        kfc_spawn = self.kfc_timer > 0
        if kfc_spawn:
            gap_h = int(gap_h * KFC_GAP_BOOST)
        margin = 70
        gy = random.randint(margin + gap_h // 2, GROUND_Y - margin - gap_h // 2)
        p = Pipe(x, gy, gap_h)
        p.is_rush = is_rush
        # is_kfc is sticky for the pipe's lifetime - it gates the gap
        # widening (see _activate_kfc) so the wider gap outlives the
        # powerup timer. The visual reverts at timer=0 via the
        # kfc_visual gate in Pipe.draw.
        p.is_kfc = kfc_spawn
        self.pipes.append(p)
        if is_rush:
            self._spawn_rush_coins(p)
            self._announce_rush(p)
        else:
            self._spawn_coins_in_gap(p)
            self._maybe_spawn_powerup(p)
        self._maybe_spawn_ramp(p)

    def _spawn_coins_in_gap(self, pipe: Pipe):
        prev_count = len(self.coins)
        pattern = random.choice(("arc", "line", "cluster"))
        cx = pipe.x + PIPE_W + self._current_spacing() * 0.5
        gy = pipe.gap_y
        if pattern == "arc":
            n = 5
            radius = min(70, pipe.gap_h * 0.35)
            for i in range(n):
                t = i / (n - 1)
                ang = -math.pi * 0.35 + math.pi * 0.7 * t
                x = cx + math.sin(ang) * 50
                y = gy + math.cos(ang) * radius - radius * 0.2
                self.coins.append(Coin(x, y))
        elif pattern == "line":
            n = 4
            for i in range(n):
                x = cx - 40 + i * 22
                self.coins.append(Coin(x, gy))
        else:  # cluster
            for dx, dy in ((0, 0), (-20, -14), (20, -14), (-20, 14), (20, 14)):
                self.coins.append(Coin(cx + dx, gy + dy))
        self.coins_spawned += len(self.coins) - prev_count

    def _spawn_rush_coins(self, pipe: Pipe):
        """Dense coin formation across the gap — random variant each rush."""
        prev_count = len(self.coins)
        spacing = self._current_spacing()
        cx = pipe.x + PIPE_W + spacing * 0.45
        gy = pipe.gap_y
        span = spacing * 0.85
        amp = min(pipe.gap_h * 0.32, 65)
        n = COIN_RUSH_COINS

        variant = random.choice(("wave", "s_curve", "chevron", "oval", "double_arc"))

        if variant == "wave":
            phase = random.uniform(0, math.tau)
            waves = random.uniform(1.0, 1.6)
            for i in range(n):
                t = i / (n - 1)
                x = cx - span / 2 + span * t
                y = gy + math.sin(phase + waves * math.tau * t) * amp
                self.coins.append(Coin(x, y))

        elif variant == "s_curve":
            phase = random.choice((0.0, math.pi))
            for i in range(n):
                t = i / (n - 1)
                x = cx - span / 2 + span * t
                y = gy + math.sin(phase + 3 * math.pi * t) * amp * 0.75
                self.coins.append(Coin(x, y))

        elif variant == "chevron":
            flip = random.choice((1, -1))
            for i in range(n):
                t = i / (n - 1)
                tri = 2.0 * abs(2.0 * t - 1.0) - 1.0
                x = cx - span / 2 + span * t
                y = gy + flip * amp * tri
                self.coins.append(Coin(x, y))

        elif variant == "oval":
            for i in range(n):
                theta = i / n * math.tau
                x = cx + math.cos(theta) * span * 0.32
                y = gy + math.sin(theta) * amp * 0.65
                self.coins.append(Coin(x, y))

        elif variant == "double_arc":
            half = n // 2
            rest = n - half
            for i in range(half):
                t = i / max(half - 1, 1)
                x = cx - span / 2 + span * t
                y = gy - amp * 0.4 + math.sin(math.pi * t) * amp * 0.3
                self.coins.append(Coin(x, y))
            for i in range(rest):
                t = i / max(rest - 1, 1)
                x = cx - span / 2 + span * t
                y = gy + amp * 0.4 - math.sin(math.pi * t) * amp * 0.3
                self.coins.append(Coin(x, y))

        self.coins_spawned += len(self.coins) - prev_count

    def _announce_rush(self, pipe: Pipe):
        """Gold sparkle burst when a rush pipe enters from the right edge."""
        x = pipe.x - 20
        y = pipe.gap_y
        for _ in range(22):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(60, 220)
            col = random.choice((PARTICLE_GOLD, COIN_LIGHT, UI_ORANGE))
            self.particles.append(Particle(
                x, y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.5, 1.0),
                random.randint(2, 4),
                col, gravity=120,
            ))

    def _maybe_spawn_powerup(self, pipe: Pipe):
        # v5_powerups TEST MODE: first N pillars guarantee a forced
        # pickup with no cooldown so QA can verify every revised
        # powerup quickly. Pool is TEST_FORCED_KINDS — equal
        # probability per kind. Bypasses the
        # score>=500 gate.
        if (TEST_SECRETS_FIRST_N_PILLARS > 0
                and self.pipes_spawned <= TEST_SECRETS_FIRST_N_PILLARS):
            kind = random.choice(TEST_FORCED_KINDS)
            x = pipe.x + PIPE_W + self._current_spacing() * 0.5 + random.uniform(-20, 20)
            y = pipe.gap_y + random.uniform(-10, 10)
            self.powerups.append(PowerUp(x, y, kind=kind))
            # NOTE: cooldown deliberately NOT set during test mode so every
            # pillar in the test window gets a fresh pickup.
            return
        if self.powerup_cooldown > 0:
            return
        if random.random() >= self._current_powerup_chance():
            return
        kinds = [k for k, _ in POWERUP_WEIGHTS]
        weights = [w for _, w in POWERUP_WEIGHTS]
        # Secret late-game pool: only enters the roll once score crosses
        # the gate. Undocumented on purpose — discovery is the point.
        if self.score >= LATE_GAME_SCORE:
            for k, w in SECRET_POWERUP_WEIGHTS:
                kinds.append(k)
                weights.append(w)
        kind = random.choices(kinds, weights=weights, k=1)[0]
        x = pipe.x + PIPE_W + self._current_spacing() * 0.5 + random.uniform(-20, 20)
        y = pipe.gap_y + random.uniform(-10, 10)
        self.powerups.append(PowerUp(x, y, kind=kind))
        self.powerup_cooldown = POWERUP_COOLDOWN

    def _maybe_spawn_ramp(self, pipe: Pipe):
        """During the SKATEBOARD window, sometimes drop a wooden
        ramp on top of this pipe's LOWER pillar. Max 1 ramp per
        pillar (~55 % chance per pipe, some skipped). User picked
        the A1 gentle incline (38×22, height-to-width ratio 0.58)
        — a small ±2 px jitter is allowed per spawn so the wedges
        look hand-placed rather than stamped. The ramp is RIGHT-
        ALIGNED on the pillar so the kicker sits flush with the
        pillar's right edge."""
        if self.skateboard_timer <= 0:
            return
        if random.random() >= 0.55:
            return
        ramp_w = 38 + random.randint(-2, 2)
        ramp_h = 22 + random.randint(-2, 2)
        ramp_w = min(ramp_w, PIPE_W - 2)
        # Place the ramp on top of the lower pillar so its base
        # rests at pipe.gap_y + pipe.gap_h/2.  Right edge aligns
        # with the pillar's right edge (kicker flush at the
        # pillar's right side).
        base_y = pipe.gap_y + pipe.gap_h / 2
        rx = pipe.x + PIPE_W - ramp_w
        self.ramps.append(Ramp(rx, ramp_w, ramp_h, base_y=base_y))
        # Tag the pipe so its crown vegetation is hidden under the
        # ramp when the pipe is drawn.
        pipe.has_ramp = True

    # ── public control ──────────────────────────────────────────────────────

    def flap(self):
        if not self.game_over:
            # A tap during the "get ready" freeze both lifts the bird and
            # kicks the world into motion immediately.
            if self.ready_t > 0:
                self.ready_t = 0.0
            sign = -1 if self.reverse_timer > 0 else 1
            self.bird.flap(gravity_sign=sign)
            self.flap_count += 1
            audio.play_flap()
            # Treasure-box buff: every flap rattles coins out of the
            # chest hanging under Pip's belly, and Pip gains them
            # instantly. Skipped during the ready freeze (we just
            # cleared ready_t above, so the first flap of a fresh run
            # never produces drops — the buff has to be picked up
            # first anyway).
            if self.treasure_box_timer > 0:
                self._drop_treasure_box_coins()
            # SKATEBOARD tricks. The detector handles 4 patterns:
            #   1) 3 FAST taps   (gap ≤ BACKFLIP_TAP_WINDOW)   → backflip
            #   2) 2 MEDIUM taps (POPSHUVIT_TAP_GAP_MIN-MAX)  → pop shuvit
            #   3) 2 SLOW taps   (KICKFLIP_TAP_GAP_MIN-MAX)   → kickflip
            #   4) 2 VERY-SLOW   (HEELFLIP_TAP_GAP_MIN-MAX)   → heelflip
            # Windows are disjoint so a tap advances at most one
            # pattern. Only tracked while the skateboard buff is
            # active and no flip is already in progress.
            if (self.skateboard_timer > 0
                    and self.bird.backflip_t <= 0
                    and self.bird.kickflip_t <= 0
                    and self.bird.heelflip_t <= 0
                    and self.bird.popshuvit_t <= 0):
                self._track_skateboard_tricks()

    def _track_skateboard_tricks(self):
        now = self._idle_t
        gap = now - self._last_tap_t
        # 3-fast-tap backflip streak.
        if gap <= BACKFLIP_TAP_WINDOW:
            self._tap_streak += 1
        else:
            self._tap_streak = 1
        self._last_tap_t = now
        if self._tap_streak >= 3:
            self._trigger_backflip()
            self._tap_streak = 0
            return
        # 2-medium-tap pop shuvit.
        if POPSHUVIT_TAP_GAP_MIN <= gap <= POPSHUVIT_TAP_GAP_MAX:
            self._trigger_popshuvit()
            return
        # 2-slow-tap kickflip.
        if KICKFLIP_TAP_GAP_MIN <= gap <= KICKFLIP_TAP_GAP_MAX:
            self._trigger_kickflip()
            return
        # 2-very-slow-tap heelflip.
        if HEELFLIP_TAP_GAP_MIN <= gap <= HEELFLIP_TAP_GAP_MAX:
            self._trigger_heelflip()

    def _trigger_backflip(self):
        self.bird.backflip_t = BACKFLIP_DURATION
        self.bird.backflip_dur = BACKFLIP_DURATION
        audio.play_backflip()
        self._spawn_trick_bubble("BACKFLIP!")

    def _trigger_kickflip(self):
        self.bird.kickflip_t = KICKFLIP_DURATION
        self.bird.kickflip_dur = KICKFLIP_DURATION
        audio.play_backflip()
        self._spawn_trick_bubble("KICKFLIP!")

    def _trigger_heelflip(self):
        self.bird.heelflip_t = HEELFLIP_DURATION
        self.bird.heelflip_dur = HEELFLIP_DURATION
        audio.play_backflip()
        self._spawn_trick_bubble("HEELFLIP!")

    def _trigger_popshuvit(self):
        self.bird.popshuvit_t = POPSHUVIT_DURATION
        self.bird.popshuvit_dur = POPSHUVIT_DURATION
        audio.play_backflip()
        self._spawn_trick_bubble("POP SHUVIT!")

    # Trick bubbles spawn at one of two anchor zones — RIGHT of the
    # E3 score burst (default home of the original POW! badge) OR a
    # mirror LEFT anchor below the coins pill. Each new bubble picks
    # a side at random, so multi-trick stacks spread across both
    # sides instead of piling onto one corner.
    _TRICK_ANCHOR_X_RIGHT = W - 70
    _TRICK_ANCHOR_X_LEFT = 70
    _TRICK_ANCHOR_Y = 165

    def _spawn_trick_bubble(self, label: str):
        anchor_x = (self._TRICK_ANCHOR_X_LEFT
                     if random.random() < 0.5
                     else self._TRICK_ANCHOR_X_RIGHT)
        ox = random.randint(-10, 10)
        oy = random.randint(-10, 10)
        tilt = random.uniform(-18, 18)
        self.trick_bubbles.append(TrickBubble(
            label,
            anchor_x + ox,
            self._TRICK_ANCHOR_Y - self._skateboard_lift_y + oy,
            tilt_deg=tilt,
        ))

    # ── update ──────────────────────────────────────────────────────────────

    def update(self, dt):
        self._idle_t += dt
        # Phoenix rebirth: variants whose revive animation plays out
        # over multiple frames drive their state machine here. Mythic
        # freezes the world; ashes lets it scroll. Both early-return
        # the rest of the simulation appropriately.
        if self.phoenix_rebirth is not None:
            self._resolve_phoenix_rebirth(dt)
            if (self.phoenix_rebirth is not None
                    and self.phoenix_rebirth["kind"] == "mythic_egg"):
                # Mythic: freeze the world. Only update particles and
                # float texts so the egg pulse + crack stays animated.
                for p in self.particles:
                    p.update(dt)
                self.particles = [p for p in self.particles if p.alive()]
                for g in self.genie_actors:
                    g.update(dt)
                self.genie_actors = [g for g in self.genie_actors if g.alive()]
                for t in self.float_texts:
                    t.update(dt)
                self.float_texts = [t for t in self.float_texts if t.alive()]
                for b in self.trick_bubbles:
                    b.update(dt)
                self.trick_bubbles = [b for b in self.trick_bubbles
                                      if b.alive()]
                return
        # The biome cycle only advances once the run has actually started.
        # While ready_t > 0 the sky stays frozen at the dawn palette — the
        # day/night arc was rolling forward earlier even when Pip was
        # still on the post-house porch waiting for input.
        if self.ready_t <= 0:
            self.biome_time += dt
        # Slowmo scales the *world* (scroll, entity velocity, entity spin,
        # pickup physics) — not the bird's input physics. Lets players
        # still flap responsively while everything else crawls.
        world_scale = SLOWMO_SCALE if self.slowmo_timer > 0 else 1.0
        sdt = dt * world_scale
        # Weather tracks biome phase, scales with sdt so slowmo softens rain too.
        self.weather.update(sdt, self.biome_phase)
        # Ambient scenes (V-flocks, fireworks, balloon, parrots, blossoms,
        # campfire) — sparse, phase-gated. Campfire uses bg_scroll to ride
        # the foreground parallax layer so it reads as world scenery.
        self.ambient.update(sdt, self.biome_phase, self.biome_palette,
                            self.bg_scroll)

        # While the "get ready" prompt is up, hold everything still except
        # a tiny idle animation on the bird. The freeze waits indefinitely
        # for the player's first flap (no auto-expiring countdown).
        if self.ready_t > 0 and not self.game_over:
            # Gentle bob without physics integration. Driven by idle_t so it
            # keeps moving even though biome_time is frozen.
            self.bird.vy = 0
            self.bird.y = H * 0.42 + math.sin(self._idle_t * 4.0) * 6
            self.bird.frame_t += dt * 6.0
            # Keep particles / float-texts ticking so nothing freezes visually.
            for p in self.particles:
                p.update(dt)
            self.particles = [p for p in self.particles if p.alive()]
            for g in self.genie_actors:
                g.update(dt)
            self.genie_actors = [g for g in self.genie_actors if g.alive()]
            for t in self.float_texts:
                t.update(dt)
            self.float_texts = [t for t in self.float_texts if t.alive()]
            for b in self.trick_bubbles:
                b.update(dt)
            self.trick_bubbles = [b for b in self.trick_bubbles
                                  if b.alive()]
            return

        if not self.game_over:
            sign = -1 if self.reverse_timer > 0 else 1
            self.bird.update(dt, gravity_sign=sign)  # bird physics at real time

            speed = self._current_scroll() if not self.game_over else 0
            self.bg_scroll += speed * sdt
            for p in self.pipes:
                p.x -= speed * sdt
            for c in self.coins:
                c.x -= speed * sdt
                c.update(sdt)
            for m in self.powerups:
                m.x -= speed * sdt
                m.update(sdt)
            for r in self.ramps:
                r.x -= speed * sdt

            # Weather → gameplay: light rain wobbles coins (visual-only
            # x-offset); heavy rain (intensity > threshold) slides them
            # leftward and shivers Pip + dampens his flap so the storm
            # feels like wind pushing him back.
            self._apply_weather_effects(sdt)

            # Magnet pull — tug uncollected coins toward the bird.
            if self.magnet_timer > 0:
                self._apply_magnet(dt)
            # Phoenix-solar variant pulls coins at half strength while
            # active. Reuses the magnet routine with weaker multipliers
            # so the real MAGNET buff stays strictly stronger.
            elif (self.phoenix_timer > 0 and PHOENIX_VARIANT == "solar"):
                self._apply_magnet(dt, radius_mult=0.55, strength_mult=0.4)
            # Phoenix-ember variant: emit an ember roughly every other
            # frame at Pip's tail position. Reuses the existing Particle
            # entity so we don't pay the cost of a new class.
            if self.phoenix_timer > 0 and PHOENIX_VARIANT == "ember":
                self._ember_trail_accum = getattr(self, "_ember_trail_accum", 0.0) + dt
                if self._ember_trail_accum >= 0.033:
                    self._ember_trail_accum = 0.0
                    self._spawn_ember_trail_particle()

            self.pipes = [p for p in self.pipes if not p.off_screen()]
            self.coins = [c for c in self.coins if c.x + 20 > 0 and not c.collected]
            self.powerups = [m for m in self.powerups if m.x + 20 > 0 and not m.collected]
            self.ramps = [r for r in self.ramps if not r.off_screen()]

            spacing = self._current_spacing()
            if not self.pipes:
                self._spawn_pipe(W + 60)
            elif self.pipes[-1].x < W - spacing:
                self._spawn_pipe(self.pipes[-1].x + spacing)

            # scoring: pass a pipe
            bx = self.bird.x
            by = self.bird.y
            for p in self.pipes:
                if not p.scored and p.x + PIPE_W < bx:
                    p.scored = True
                    self.score += 1
                    self.pillars_passed += 1
                    self._proof.record(self.time_alive, 1, "pipe")

            # Near-miss detection: once per pipe, flag if the bird was within
            # a narrow band of either edge without hitting. Fires as the pipe
            # passes behind the bird so it doesn't double-count mid-flight.
            for p in self.pipes:
                pid = id(p)
                if self._near_miss_flags.get(pid):
                    continue
                # Only check pipes currently overlapping the bird's x-range
                if p.x < bx + BIRD_R and p.x + PIPE_W > bx - BIRD_R:
                    gap_top = p.gap_y - p.gap_h / 2
                    gap_bot = p.gap_y + p.gap_h / 2
                    # Distance from bird to nearest pipe edge vertically
                    d_top = by - gap_top  # positive if below the top edge
                    d_bot = gap_bot - by  # positive if above the bot edge
                    margin = 10
                    if 0 < d_top < margin or 0 < d_bot < margin:
                        self.near_misses += 1
                        self._near_miss_flags[pid] = True

            # Time alive
            self.time_alive += dt

            # collisions
            self._check_collisions()

            # pickups
            self._check_pickups()

            # timers (real time, not scaled — the buffs shouldn't self-extend).
            if self.triple_timer > 0:
                self.triple_timer = max(0.0, self.triple_timer - dt)
            self.bird.triple_active = self.triple_timer > 0
            if self.magnet_timer > 0:
                self.magnet_timer = max(0.0, self.magnet_timer - dt)
            if self.slowmo_timer > 0:
                self.slowmo_timer = max(0.0, self.slowmo_timer - dt)
            if self.kfc_timer > 0:
                self.kfc_timer = max(0.0, self.kfc_timer - dt)
                if self.kfc_timer == 0:
                    self._spawn_poof(self.bird.x, self.bird.y)
            self.bird.kfc_active = self.kfc_timer > 0
            if self.ghost_timer > 0:
                self.ghost_timer = max(0.0, self.ghost_timer - dt)
            self.bird.ghost_active = self.ghost_timer > 0
            if self.grow_timer > 0:
                self.grow_timer = max(0.0, self.grow_timer - dt)
            if self.treasure_box_timer > 0:
                self.treasure_box_timer = max(0.0, self.treasure_box_timer - dt)
            self.bird.grow_active = self.grow_timer > 0
            if self.reverse_timer > 0:
                self.reverse_timer = max(0.0, self.reverse_timer - dt)
            # Secret powerup timers (real time — buffs don't self-extend in slowmo).
            if self.skateboard_timer > 0:
                self.skateboard_timer = max(0.0, self.skateboard_timer - dt)
            self.bird.skateboard_active = self.skateboard_timer > 0
            # Slide-boost envelope: attack while Pip is grinding a
            # surface during the skateboard window, decay otherwise.
            # Reset hard once the buff itself expires so the boost
            # doesn't linger into normal flight.
            if self.bird.skateboard_active and self._sliding_this_frame:
                self.slide_boost = min(
                    1.0, self.slide_boost + dt / SKATE_SLIDE_ATTACK)
            else:
                self.slide_boost = max(
                    0.0, self.slide_boost - dt / SKATE_SLIDE_RELEASE)
            if self.skateboard_caption_t > 0:
                self.skateboard_caption_t = max(
                    0.0, self.skateboard_caption_t - dt)
                if self.skateboard_caption_t <= 0:
                    self.skateboard_caption_overlay = None
            if self.skateboard_burst_t > 0:
                self.skateboard_burst_t = max(
                    0.0, self.skateboard_burst_t - dt)
                if self.skateboard_burst_t <= 0:
                    self.skateboard_burst_surface = None
            if self.phoenix_timer > 0:
                self.phoenix_timer = max(0.0, self.phoenix_timer - dt)
            self.bird.phoenix_active = self.phoenix_timer > 0
            if self.phoenix_invuln > 0:
                self.phoenix_invuln = max(0.0, self.phoenix_invuln - dt)
            # Lottery: tick the reveal animation; apply score delta on reveal.
            if self.lottery_anim is not None:
                self.lottery_anim["t"] += dt
                if (not self.lottery_anim["applied"]
                        and self.lottery_anim["t"] >= LOTTERY_REVEAL_TIME):
                    self._apply_lottery_result()
                    self.lottery_anim["applied"] = True
                # Linger ~1.2s after reveal so the player sees the tier label.
                if self.lottery_anim["t"] >= LOTTERY_REVEAL_TIME + 1.2:
                    self.lottery_anim = None
            if self.powerup_cooldown > 0:
                self.powerup_cooldown -= dt
            if self.hit_flash > 0:
                self.hit_flash = max(0.0, self.hit_flash - dt)
            # Lightning bolt: decay the visual life; expire when life hits 0.
            if self.lightning_strike is not None:
                self.lightning_strike["life"] -= dt
                if self.lightning_strike["life"] <= 0:
                    self.lightning_strike = None
            # Scorch state: emit dark smoke wisps off Pip's silhouette
            # for the duration. Decays so the after-effect fades out.
            if self._lightning_scorch_t > 0:
                self._lightning_scorch_t = max(0.0, self._lightning_scorch_t - dt)
                self._scorch_smoke_accum += dt
                # ~40 wisps/s while the scorch is fresh.
                while self._scorch_smoke_accum >= 0.025:
                    self._scorch_smoke_accum -= 0.025
                    self._spawn_scorch_wisp()
        else:
            # freeze world but let particles + float texts drift
            pass

        # shake decay
        if self.shake_t > 0:
            self.shake_t -= dt
            if self.shake_t <= 0:
                self.shake_mag = 0.0

        # particles and float texts
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]
        for g in self.genie_actors:
            g.update(dt)
        self.genie_actors = [g for g in self.genie_actors if g.alive()]
        for t in self.float_texts:
            t.update(dt)
        self.float_texts = [t for t in self.float_texts if t.alive()]
        for b in self.trick_bubbles:
            b.update(dt)
        self.trick_bubbles = [b for b in self.trick_bubbles if b.alive()]

    def world_idle_tick(self, dt):
        """Run the background without handling bird death/pipe spawning
        logic — used by the Menu scene to keep visuals alive."""
        self.biome_time += dt
        self.weather.update(dt, self.biome_phase)
        self.bg_scroll += SCROLL_BASE * 0.5 * dt
        self.ambient.update(dt, self.biome_phase, self.biome_palette,
                            self.bg_scroll)
        for p in self.pipes:
            p.x -= SCROLL_BASE * 0.25 * dt
        for c in self.coins:
            c.x -= SCROLL_BASE * 0.25 * dt
            c.update(dt)
        for m in self.powerups:
            m.x -= SCROLL_BASE * 0.25 * dt
            m.update(dt)
        self.pipes = [p for p in self.pipes if not p.off_screen()]
        self.coins = [c for c in self.coins if c.x + 20 > 0]
        self.powerups = [m for m in self.powerups if m.x + 20 > 0]
        if self.pipes and self.pipes[-1].x < W - PIPE_SPACING:
            self._spawn_pipe(self.pipes[-1].x + PIPE_SPACING)

        # animate bird gently (bobbing)
        self.bird.frame_t += dt * 8.0
        self.bird.y = H * 0.42 + math.sin(self.bg_scroll * 0.05) * 12
        self.bird.vy = -math.cos(self.bg_scroll * 0.05) * 40

        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]
        for g in self.genie_actors:
            g.update(dt)
        self.genie_actors = [g for g in self.genie_actors if g.alive()]

    # ── collisions ───────────────────────────────────────────────────────────

    def bird_radius(self) -> float:
        if self.grow_timer > 0:
            return BIRD_R * GROW_SCALE
        return BIRD_R

    def _check_collisions(self):
        bx, by = self.bird.x, self.bird.y
        br = self.bird_radius()
        # SKATEBOARD: if Pip is descending into the ground, he slides on
        # it instead of dying. The helmet handles ceiling spikes (see
        # pillar loop below). Spawns occasional dust puffs.
        skating = self.skateboard_timer > 0
        # Reset each frame; the snap blocks below flip this to True
        # while Pip is actually grinding a surface so update() can
        # ramp the slide-boost up or fade it back to zero.
        self._sliding_this_frame = False
        # Ceiling: clamp Pip and zero upward velocity instead of killing.
        # Bonking the top edge feels accidental and was a recurring "unfair
        # death" complaint; the ground still kills.
        if by - br < 0:
            self.bird.y = br
            if self.bird.vy < 0:
                self.bird.vy = 0.0
            by = self.bird.y
        # PHOENIX grace: short window after a phoenix revive where Pip is
        # immune to ground + pipe collisions, so the just-revived bird
        # has a moment to clear the obstacle that killed him. Ceiling
        # clamp above still applies (it's non-lethal anyway). Phoenix-
        # rebirth state machine (ashes egg) also short-circuits here so
        # the egg can sail through pipes during the hatch window.
        if self.phoenix_invuln > 0 or self.phoenix_rebirth is not None:
            return
        # SKATEBOARD: ramp-surface snap (must come BEFORE the ground
        # check). If Pip is over a wooden wedge while skating, snap
        # to the ramp's slope so he rolls UP the incline. The ramp
        # surface sits above GROUND_Y on the slope portion, so this
        # naturally takes precedence over the plain ground slide.
        if skating and self.ramps:
            for r in self.ramps:
                if r.x <= bx <= r.x + r.w:
                    surface_y = r.surface_y_at(bx)
                    if by + br >= surface_y - 1 and self.bird.vy >= -50:
                        self.bird.y = surface_y - br
                        self.bird.vy = 0.0
                        by = self.bird.y
                        self._maybe_skateboard_dust(bx, surface_y)
                        self._maybe_grind_sparks(surface_y)
                        self._sliding_this_frame = True
                    break  # only one ramp under Pip at a time
        if by + br > GROUND_Y:
            if skating:
                # Slide along the ground. Snap, zero vy, dust puff.
                self.bird.y = GROUND_Y - br
                self.bird.vy = 0.0
                self._maybe_grind_sparks(GROUND_Y)
                by = self.bird.y
                self._maybe_skateboard_dust(self.bird.x, GROUND_Y)
                self._sliding_this_frame = True
            else:
                self._die()
                return
        if self.ghost_timer > 0:
            return  # phase through pipes while ghost is active
        # SKATEBOARD proactive pillar-top snap. The pipe collision below
        # uses a SHRUNKEN hitbox (PIPE_HITBOX_SHRINK), which creates a
        # few-pixel deadband above the pillar top where gravity pulls
        # Pip below the snap target before the collision re-snaps him —
        # visible as jitter. This block snaps every frame Pip's full-
        # radius bottom reaches the lower-pillar top, exactly the way
        # the GROUND_Y check does, so the slide reads smooth. Dust puff
        # fires per snap so the trail off the back of the board is
        # consistent with floor sliding.
        if skating:
            for p in self.pipes:
                in_column = (p.x - br < bx < p.x + PIPE_W + br)
                if not in_column:
                    continue
                gap_bot = p.gap_y + p.gap_h / 2
                if ((by + br) >= gap_bot - 1
                        and self.bird.vy >= -50
                        and by < gap_bot):
                    self.bird.y = gap_bot - br
                    self.bird.vy = 0.0
                    by = self.bird.y
                    self._maybe_skateboard_dust(bx, gap_bot)
                    self._maybe_grind_sparks(gap_bot)
                    self._sliding_this_frame = True
                    break
        # Pip's hitboxes: body (existing) + parcel below him. The parcel
        # offset rotates with his tilt so when he dives the parcel swings
        # forward/down with him.
        scale = GROW_SCALE if self.grow_timer > 0 else 1.0
        parcel_offset = pygame.math.Vector2(
            0, PARCEL_Y_OFFSET * scale).rotate(-self.bird.tilt_deg)
        px = bx + parcel_offset.x
        py = by + parcel_offset.y
        pr = PARCEL_R * scale
        # While skateboard is active the parcel IS the skateboard, so its
        # collision footprint is gone — board sits below Pip's feet, not
        # adjacent to obstacles. Pip's body hitbox still applies.
        if skating:
            pr = 0  # disable parcel hitbox
        # Parcel shouldn't graze the ground unless the bird already would
        # have died (the bird circle's r > parcel offset+r in normal flight).
        # Skip ground/ceiling re-check; only pipes are added.
        for p in self.pipes:
            if p.collides_circle(bx, by, br - PIPE_HITBOX_SHRINK):
                if skating and self._skateboard_handle_pipe(p, bx, by, br):
                    continue
                self._die()
                return
            if pr > 0 and p.collides_circle(px, py, pr - 1):
                self._die()
                return

        # SKATEBOARD random grind. On the rising edge of
        # `_sliding_this_frame` (Pip just landed on the ground or a
        # pillar top while skateboard is active), roll a 25% chance
        # to start a random grind. On the falling edge (Pip lifts
        # off), clear the grind. Both edges keyed off the per-frame
        # flag versus the value from the previous frame.
        if (self._sliding_this_frame
                and not self._sliding_prev_frame
                and self.skateboard_timer > 0
                and self.bird.grind_type is None):
            if random.random() < 0.25:
                gtype = random.choice(("nose", "tail"))
                self.bird.grind_type = gtype
                # Trick name shows as a comic halftone bubble near
                # the E3 score (matches the SKATEBOARD powerup's
                # pop-art identity); see _spawn_trick_bubble.
                self._spawn_trick_bubble(f"{gtype.upper()} GRIND!")
        if (not self._sliding_this_frame
                and self._sliding_prev_frame
                and self.bird.grind_type is not None):
            self.bird.grind_type = None
        self._sliding_prev_frame = self._sliding_this_frame

    def _skateboard_handle_pipe(self, p, bx, by, br) -> bool:
        """When SKATEBOARD is active, intercept lethal pipe collisions.

        Returns True if the collision was absorbed (no death):
          - Bottom-pillar TOP hit (Pip's feet hit the cap from above): land
            and roll along the rim.
          - Upper-pillar UNDERSIDE hit (Pip's head bonks the spike from
            below): helmet "CLONK!" deflect with stars + audio.
        Returns False if it's a side hit, which is still lethal.
        """
        gap_top = p.gap_y - p.gap_h / 2  # bottom of upper (ceiling) pillar
        gap_bot = p.gap_y + p.gap_h / 2  # top of lower (floor) pillar
        # Approach from above onto the lower pillar's top:
        # bird's bottom (by + br) overlapped gap_bot AND bird is descending or
        # nearly level AND bird is horizontally over the pipe column.
        in_column = (p.x - br < bx < p.x + PIPE_W + br)
        if in_column and by < gap_bot and self.bird.vy >= -50 and (by + br) >= gap_bot:
            # Roll on the lower-pillar's top edge.
            self.bird.y = gap_bot - br
            self.bird.vy = 0.0
            self._maybe_skateboard_dust(bx, gap_bot)
            self._maybe_grind_sparks(gap_bot)
            self._sliding_this_frame = True
            return True
        # Approach from below onto the upper pillar's underside.
        if in_column and by > gap_top and self.bird.vy <= 50 and (by - br) <= gap_top:
            # Helmet bonk: clamp + stars + audio + shake.
            self.bird.y = gap_top + br
            self.bird.vy = max(self.bird.vy, 0.0) + 60  # bounce gently downward
            self.shake_mag = max(self.shake_mag, 5.0)
            self.shake_t = max(self.shake_t, 0.18)
            audio.play_helmet_bonk()
            # Star burst at the bonk point.
            for _ in range(10):
                ang = random.uniform(-math.pi, 0)
                spd = random.uniform(120, 220)
                self.particles.append(Particle(
                    bx, gap_top,
                    math.cos(ang) * spd, math.sin(ang) * spd,
                    random.uniform(0.3, 0.6),
                    random.randint(2, 4),
                    random.choice((UI_GOLD, UI_CREAM, WHITE)),
                    gravity=400,
                ))
            return True
        # Side hit: lethal.
        return False

    def _maybe_skateboard_dust(self, x, y_ground):
        """Occasional dust puff while sliding — throttled, not every frame."""
        if random.random() < 0.35:
            for _ in range(2):
                ang = random.uniform(math.pi * 0.9, math.pi * 1.1)
                spd = random.uniform(40, 110)
                self.particles.append(Particle(
                    x - random.uniform(0, 10),
                    y_ground - 2,
                    math.cos(ang) * spd,
                    -abs(math.sin(ang) * spd * 0.4),
                    random.uniform(0.25, 0.45),
                    random.randint(2, 3),
                    random.choice(((220, 215, 200), (200, 195, 180), WHITE)),
                    gravity=200,
                ))

    def _maybe_grind_sparks(self, y_ground):
        """Bright spark spray at the grinding wheel — front wheel
        for a nose grind, back wheel for a tail grind. Sprays
        backward (opposite Pip's motion) with a little upward
        kick, fast settle. Brighter + denser than the regular
        slide-dust so the grind reads as metal-on-concrete."""
        if self.bird.grind_type is None:
            return
        # Wheel offset from bird.x — board's wheel centres sit at
        # roughly ±14 px under Pip's feet at game scale.
        if self.bird.grind_type == "nose":
            wheel_dx = +14
        else:  # "tail"
            wheel_dx = -14
        wx = self.bird.x + wheel_dx
        if random.random() < 0.85:
            for _ in range(random.randint(3, 5)):
                # Sparks fan backward (against direction of motion)
                # with a slight upward kick — π ± 0.5 rad.
                ang = random.uniform(math.pi * 0.7, math.pi * 1.3)
                spd = random.uniform(100, 230)
                colour = random.choice((PARTICLE_ORNG,
                                         PARTICLE_GOLD,
                                         PARTICLE_WHT,
                                         (255, 220, 130)))
                self.particles.append(Particle(
                    wx + random.uniform(-2, 2),
                    y_ground - 2,
                    math.cos(ang) * spd,
                    math.sin(ang) * spd - random.uniform(20, 60),
                    random.uniform(0.18, 0.38),
                    random.randint(1, 3),
                    colour,
                    gravity=500,
                ))

    def _die(self):
        if self.game_over:
            return
        # PHOENIX revive: if the buff is active, consume it instead of
        # dying. The revive animation varies by PHOENIX_VARIANT — see
        # the per-variant helper methods below.
        if self.bird.phoenix_active:
            self.phoenix_timer = 0.0
            self.bird.phoenix_active = False
            # Grandiose variants all share the Ashes-style rebirth
            # (ash cloud + falling egg + safe-gap respawn). Variant
            # routes the revive animation only.
            if PHOENIX_VARIANT in ("ashes", "imperial", "fenghuang",
                                   "dragon", "comet", "royal",
                                   "blaze", "sunburst", "twin",
                                   "swift", "grand",
                                   "soar", "rise", "stoop",
                                   "dive", "eternal",
                                   "eternal_warm", "eternal_soft",
                                   "eternal_dawn", "eternal_friend",
                                   "eternal_lite"):
                self._revive_ashes()
            elif PHOENIX_VARIANT == "solar":
                self._revive_solar()
            elif PHOENIX_VARIANT == "ember":
                self._revive_ember()
            elif PHOENIX_VARIANT == "mythic":
                self._revive_mythic()
            else:
                self._revive_classic()
            return
        self.game_over = True
        self.bird.alive = False
        self.hit_flash = 0.35
        self.shake_mag = 8
        self.shake_t = 0.45
        audio.play_death()
        for _ in range(26):
            self.particles.append(Particle(
                self.bird.x, self.bird.y,
                random.uniform(-260, 260), random.uniform(-360, -40),
                random.uniform(0.5, 1.2), random.randint(3, 6),
                random.choice((PARTICLE_CRIM, PARTICLE_ORNG, PARTICLE_WHT)),
                gravity=900,
            ))

    # ── Phoenix revive helpers (one per PHOENIX_VARIANT) ────────────────────

    def _revive_classic(self):
        """The shipped revive: orange/red/white fire burst around Pip,
        auto-flap upward, REBORN! float text. Pip stays where he was."""
        self.phoenix_invuln = PHOENIX_INVULN
        self.bird.vy = FLAP_V * 0.9
        self.shake_mag = max(self.shake_mag, 6.0)
        self.shake_t   = max(self.shake_t,   0.3)
        audio.play_ghost()
        audio.play_thunder()
        for _ in range(36):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(160, 420)
            col = random.choice((
                (255,  90,  30), (255, 180,  60),
                (255, 230, 130), WHITE,
            ))
            self.particles.append(Particle(
                self.bird.x, self.bird.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.5, 1.2),
                random.randint(3, 6),
                col, gravity=180,
            ))
        self.float_texts.append(FloatText(
            "REBORN!", self.bird.x, self.bird.y - 32, (255, 140, 40),
            size=30, life=1.4, vy=-36, style="powerup",
        ))

    def _revive_solar(self):
        """Solar revive: gold-white expanding ring, no red. Brighter,
        more 'sun-flash' than fire-burst."""
        self.phoenix_invuln = PHOENIX_INVULN
        self.bird.vy = FLAP_V * 0.9
        self.shake_mag = max(self.shake_mag, 5.0)
        self.shake_t   = max(self.shake_t,   0.25)
        audio.play_thunder()
        # 48 particles in a uniform ring (not random) so it reads as a
        # single bloom rather than fire spray.
        for i in range(48):
            ang = (i / 48) * math.tau
            spd = random.uniform(260, 360)
            col = random.choice((
                (255, 240, 180), (255, 250, 220),
                (255, 220, 120), WHITE,
            ))
            self.particles.append(Particle(
                self.bird.x, self.bird.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.5, 1.0),
                random.randint(2, 4),
                col, gravity=120,
            ))
        self.float_texts.append(FloatText(
            "REBORN!", self.bird.x, self.bird.y - 32, (255, 230, 130),
            size=30, life=1.4, vy=-36, style="powerup",
        ))

    def _revive_ember(self):
        """Ember revive: classic burst but the trail particles already
        on screen flare brighter (we add a second wave of brighter
        embers along Pip's recent path)."""
        self._revive_classic()
        # Lay down a brighter trail-flash behind Pip.
        for i in range(18):
            ang = math.pi + random.uniform(-0.4, 0.4)
            spd = random.uniform(180, 360)
            col = random.choice(((255, 230, 130), (255, 250, 220), WHITE))
            self.particles.append(Particle(
                self.bird.x, self.bird.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.4, 0.8),
                random.randint(2, 4),
                col, gravity=80,
            ))

    def _revive_mythic(self):
        """Mythic revive: the world freezes for 0.6 s while a flame egg
        pulses and cracks at Pip's position. Standard auto-flap + invuln
        kick in when the egg-crack completes (see _resolve_phoenix_rebirth)."""
        # Defer the invuln + auto-flap to when the rebirth_pause ends.
        self.phoenix_rebirth = {
            "kind": "mythic_egg",
            "t": 0.0,
            "duration": 0.6,
            "x": self.bird.x,
            "y": self.bird.y,
        }
        self.bird.vy = 0.0
        self.shake_mag = max(self.shake_mag, 4.0)
        self.shake_t   = max(self.shake_t,   0.2)
        audio.play_thunder()
        # Initial fiery pulse to mark the egg's appearance.
        for _ in range(20):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(80, 200)
            col = random.choice(((255, 100, 30), (255, 200, 80), WHITE))
            self.particles.append(Particle(
                self.bird.x, self.bird.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.4, 0.7),
                random.randint(2, 4),
                col, gravity=80,
            ))

    def _revive_ashes(self):
        """Ashes revive: Pip collapses to ash, an egg falls through the
        air, and after 0.8 s hatches at the centre of the next safe gap
        ahead. World keeps scrolling normally during the egg phase."""
        self.phoenix_rebirth = {
            "kind": "ashes_egg",
            "t": 0.0,
            "duration": 0.8,
            "x": self.bird.x,
            "y": self.bird.y,
            "egg_y": self.bird.y,
            "egg_vy": 40.0,  # initial downward drift
        }
        audio.play_poof()
        audio.play_thunder()
        # 14-particle grey-and-amber ash cloud at Pip's last position.
        for _ in range(14):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(40, 140)
            col = random.choice((
                (180, 170, 160), (140, 130, 120),
                (220, 180, 110), ( 90,  80,  70),
            ))
            self.particles.append(Particle(
                self.bird.x, self.bird.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.6, 1.2),
                random.randint(3, 5),
                col, gravity=120,
            ))

    def _resolve_phoenix_rebirth(self, dt: float):
        """Called every frame while `self.phoenix_rebirth` is set. Drives
        the per-variant rebirth state machine to completion, then snaps
        Pip back into play with PHOENIX_INVULN grace."""
        st = self.phoenix_rebirth
        st["t"] += dt
        if st["kind"] == "ashes_egg":
            # Egg drifts down + forward, ignoring pipes. Track its y
            # so the renderer can draw an egg sprite where the bird
            # would have been.
            st["egg_vy"] = min(st["egg_vy"] + 320 * dt, 200.0)
            st["egg_y"] += st["egg_vy"] * dt
        if st["t"] < st["duration"]:
            return
        # Time to hatch / wake up.
        if st["kind"] == "ashes_egg":
            # Auto-position Pip at the centre of the next safe gap
            # ahead of his current x. If no pipe is ahead, just snap
            # him to mid-screen so he's not falling through the floor.
            target_y = H * 0.4
            for p in sorted(self.pipes, key=lambda q: q.x):
                if p.x + PIPE_W > self.bird.x - 10:
                    target_y = p.gap_y + p.gap_h / 2
                    break
            self.bird.y = max(40, min(GROUND_Y - 40, target_y))
            self.bird.vy = 0.0
        else:  # mythic_egg
            self.bird.vy = FLAP_V * 0.9
            # Final crack burst.
            for _ in range(30):
                ang = random.uniform(0, math.tau)
                spd = random.uniform(180, 420)
                col = random.choice((
                    (255, 100, 30), (255, 200, 80),
                    (255, 240, 160), WHITE,
                ))
                self.particles.append(Particle(
                    self.bird.x, self.bird.y,
                    math.cos(ang) * spd, math.sin(ang) * spd,
                    random.uniform(0.5, 1.0),
                    random.randint(3, 5),
                    col, gravity=160,
                ))
            audio.play_poof()
        self.phoenix_invuln = PHOENIX_INVULN
        self.shake_mag = max(self.shake_mag, 5.0)
        self.shake_t   = max(self.shake_t,   0.3)
        self.float_texts.append(FloatText(
            "REBORN!", self.bird.x, self.bird.y - 32, (255, 200, 80),
            size=30, life=1.4, vy=-36, style="powerup",
        ))
        self.phoenix_rebirth = None

    # ── pickups ──────────────────────────────────────────────────────────────

    def _check_pickups(self):
        bx, by = self.bird.x, self.bird.y
        br = BIRD_R + 4
        for c in self.coins:
            if c.collected:
                continue
            dx = c.x - bx
            dy = c.y - by
            if dx * dx + dy * dy < (br + COIN_R) ** 2:
                c.collected = True
                self._on_coin(c)
        for m in self.powerups:
            if m.collected:
                continue
            dx = m.x - bx
            dy = m.y - by
            if dx * dx + dy * dy < (br + POWERUP_R) ** 2:
                m.collected = True
                self._on_powerup(m)
        # (The old BANK HEIST vault-on-pillar collision lived here. The
        # treasure-box redesign moved the payout to the per-flap coin
        # drop in `flap()`, so there's nothing to brush off a pillar.)

    def _drop_treasure_box_coins(self):
        """Called on each flap while the treasure-box buff is active.
        Each flap rattles TREASURE_BOX_COINS_PER_FLAP coins loose;
        triple multiplies as it does for normal coin pickups. The coins
        are added straight to score (no in-world coin entities), with a
        small visual burst at the chest position so the cause/effect
        reads clearly. coin_count is NOT bumped — the plausibility check
        enforces coin_count == len(coin events), so per-flap drops are
        recorded under a distinct "treasure_box" event kind."""
        base = TREASURE_BOX_COINS_PER_FLAP
        mult = 3 if self.triple_timer > 0 else 1
        gain = base * mult
        self.score += gain
        self._proof.record(self.time_alive, gain, "treasure_box")
        # Spawn position: top of the chest where the lid seam sits, so
        # the coins look like they're popping out of the lid.
        cx = self.bird.x + 4
        cy = self.bird.y + 56 - 9   # body.y of the chest (lid-body seam)
        # Spawn one TreasureCoinParticle per coin earned. They pop UP
        # out of the lid with a fan-out spread, arc, and fall back
        # under gravity. The score gain has already been applied above
        # — these are pure visual feedback so the player SEES the coins.
        for i in range(gain):
            # Even horizontal spread across the cluster, plus jitter.
            if gain == 1:
                spread = 0.0
            else:
                spread = (i / (gain - 1) - 0.5) * 36  # ±18 px across the fan
            vx0 = spread * 4.5 + random.uniform(-25, 25)
            vy0 = random.uniform(-280, -210)
            self.particles.append(TreasureCoinParticle(
                cx + spread * 0.4, cy,
                vx0, vy0,
                life=0.65,
                spin_rate=random.uniform(6.0, 10.0),
            ))
        # Float text — "+N" rising above the chest. Match the +1/+3
        # gradient-fill-and-outline style used by normal coin pickups.
        color = UI_ORANGE if mult == 3 else UI_GOLD
        self.float_texts.append(FloatText(
            f"+{gain}", cx, cy - 12, color,
            size=24, life=0.7, vy=-50, style="powerup",
        ))
        audio.play_coin()

    def _apply_weather_effects(self, dt):
        """Route current rain intensity to coins (shake / slide) and Pip
        (shiver + flap dampen). Pure read of weather.rain_intensity — no
        randomness in the storm trigger, the biome phase decides when
        weather kicks in. Coin shake is visual-only (weather_dx).
        Coin slide is a real x decrement so collision follows the visual.
        Pip shiver is visual-only (shiver_x/y) so collisions stay fair.
        Flap dampen reduces the next tap's lift, which IS a real
        physics change — that's the felt "wind is pushing me down" cue."""
        ri = _rain_intensity(self.weather.phase)
        if ri <= 0:
            # Clear any lingering offsets so a brief drizzle that drops back
            # to 0 doesn't leave coins permanently nudged.
            for c in self.coins:
                c.weather_dx = 0.0
            self.bird.shiver_x = 0.0
            self.bird.shiver_y = 0.0
            self.bird.flap_dampen = 0.0
            return
        # Coin shake — pure horizontal left-right tremor. Amplitude
        # scales LINEARLY with rain intensity so the wobble is
        # barely perceptible at first drizzle (~0.4 px at ri=0.1)
        # and grows smoothly to a visibly violent ±4 px at peak
        # storm (ri=1.0). Oscillation frequency also speeds up
        # mildly with intensity (4.5 → 9.0 rad/s) so heavy rain
        # feels frantic, not just wider. No vertical wobble, no
        # leftward slide, no real position drift — coins stay on
        # their hover spot and just tremor with the weather.
        amp_x = WEATHER_COIN_SHAKE_AMP * ri
        freq = 4.5 * (1.0 + ri)
        for c in self.coins:
            c._weather_phase += dt * freq
            c.weather_dx = math.sin(c._weather_phase) * amp_x
        # Pip: shiver + flap dampen only above the heavy threshold so
        # ordinary drizzle doesn't make controls feel broken.
        heavy = ri > WEATHER_HEAVY_THRESHOLD
        if heavy:
            heavy_t = (ri - WEATHER_HEAVY_THRESHOLD) / (1.0 - WEATHER_HEAVY_THRESHOLD)
            # Extra jolt during a lightning flash so the strike reads.
            flash_kick = 1.5 if self.weather.flash_remaining > 0 else 1.0
            self.bird.shiver_x = random.uniform(-1, 1) * WEATHER_PIP_SHIVER_AMP * heavy_t * flash_kick
            self.bird.shiver_y = random.uniform(-1, 1) * WEATHER_PIP_SHIVER_AMP * heavy_t * flash_kick
            self.bird.flap_dampen = WEATHER_FLAP_DAMPEN_MAX * heavy_t
        else:
            self.bird.shiver_x = 0.0
            self.bird.shiver_y = 0.0
            self.bird.flap_dampen = 0.0

        # Storm jolt: only at near-peak intensity, after the lockout, and
        # only if Pip actually has coins to lose. Random fire on a small
        # per-frame chance (~0.06 / frame at 60fps ≈ once every ~17 s on
        # average while at peak). Lockout 25 s after firing so a long
        # dusk storm doesn't keep hammering. The trigger doesn't strike
        # Pip directly — it kicks off a ~1.9-second BUILDUP of 3
        # background lightning bolts that miss him, then the real strike
        # lands on the 4th flash.
        if self._storm_jolt_lockout > 0:
            self._storm_jolt_lockout = max(0.0, self._storm_jolt_lockout - dt)
        elif (ri > 0.85
              and self.coin_count > 0
              and not self.game_over
              and self.ready_t <= 0
              and not self._storm_buildup_seq
              and random.random() < 0.06 * dt * 60):
            self._start_storm_buildup()

        # Advance the buildup if one is running. Events at the head of
        # the queue fire when the running clock reaches their scheduled
        # time. The strike is the climax (10th event in the default
        # buildup) — fade-away bolts AFTER the strike stay queued and
        # fire as the storm settles.
        if self._storm_buildup_seq:
            self._storm_buildup_t += dt
            while (self._storm_buildup_seq
                   and self._storm_buildup_t >= self._storm_buildup_seq[0][0]):
                _, kind = self._storm_buildup_seq.pop(0)
                if kind == "strike":
                    self._fire_storm_jolt()
                else:
                    side = -1 if kind.endswith("left") else 1
                    self._fire_background_lightning(side=side)

    def _start_storm_buildup(self):
        """Telegraph the incoming strike with NINE background bolts
        on alternating sides, gaps SHRINKING toward the climax so
        the storm reads as steadily escalating: starts at ~0.8 s
        gaps, ends at ~0.3 s gaps. The real `_fire_storm_jolt` lands
        at t=4.40 s as the 10th lightning. Two FADE-AWAY background
        bolts after the strike (1.0 s + 1.5 s post-strike) close the
        sequence as the storm settles. 12 events total. Lockout is
        set immediately so the trigger can't re-fire mid-buildup;
        the 25-second cooldown starts from the buildup, not the
        strike."""
        self._storm_buildup_seq = [
            # ── 9 bg bolts — escalating tempo (gap shrinks 0.80→0.30) ──
            (0.00, "bg_left"),
            (0.80, "bg_right"),    # gap 0.80
            (1.50, "bg_left"),     # gap 0.70
            (2.10, "bg_right"),    # gap 0.60
            (2.60, "bg_left"),     # gap 0.50
            (3.05, "bg_right"),    # gap 0.45
            (3.45, "bg_left"),     # gap 0.40
            (3.80, "bg_right"),    # gap 0.35
            (4.10, "bg_left"),     # gap 0.30
            # ── climax — the 10th bolt hits Pip ──
            (4.40, "strike"),      # gap 0.30
            # ── 2 fade-away bolts as the storm settles ──
            (5.40, "bg_right"),    # gap 1.00 (sudden slowdown)
            (6.90, "bg_left"),     # gap 1.50 (last distant flash)
        ]
        self._storm_buildup_t = 0.0
        # Reserve the slot — prevents re-trigger during buildup +
        # 25 s cooldown after.
        self._storm_jolt_lockout = 25.0

    def _fire_background_lightning(self, side: int = -1):
        """Non-damaging background lightning bolt — same visual
        ingredients as the real strike (jagged bolt path + flash +
        shake) but the bolt lands on a random sky point well off to
        Pip's side, with reduced flash / shake. Sells "the storm is
        cracking around him" before the real hit. `side` is -1 (left
        of Pip) or +1 (right)."""
        bx, by = self.bird.x, self.bird.y
        # Origin: cloud-line, way over on the chosen side
        origin_x = bx + side * random.uniform(110, 170)
        # Strike point: an air target NOT on Pip — somewhere in the
        # sky on the same side, at varied height so successive bolts
        # don't all look the same.
        impact_x = bx + side * random.uniform(80, 150)
        impact_y = random.uniform(by - 80, by + 80)
        path = [(origin_x, 0.0)]
        # More segments + wider jitter at the cloud end → reads as a
        # genuinely zig-zaggy lightning bolt rather than a near-straight
        # streak. Tightens toward the impact so the convergence still
        # reads cleanly.
        segs = 18
        for i in range(1, segs):
            t = i / segs
            jx = random.uniform(-42, 42) * (1.0 - t * 0.55)
            cx = origin_x * (1 - t) + impact_x * t + jx
            cy = impact_y * t
            path.append((cx, cy))
        path.append((impact_x, impact_y))
        self.lightning_strike = {
            "path": path,
            "life": 0.32,
            "life_max": 0.32,
        }
        # Smaller flash + shake than the real strike — telegraph,
        # not impact.
        self.weather.flash_remaining = max(
            self.weather.flash_remaining, 0.14)
        self.shake_mag = max(self.shake_mag, 3.5)
        self.shake_t = max(self.shake_t, 0.20)
        # Distant thunder for the bg bolts — quieter than the real
        # strike + slight per-bolt volume variation so successive
        # claps feel naturalistic rather than copy-pasted.
        try:
            audio.play_thunder(volume=random.uniform(0.35, 0.55))
        except Exception:
            pass

    def _fire_storm_jolt(self):
        """LIGHTNING STRIKES PIP. A brilliant white-blue bolt cracks
        down from the cloud line to Pip's head; the screen flashes;
        the world shakes hard; up to 50 coins are blasted off in a
        360° spread; cyan electric sparks crackle around the impact;
        Pip enters a short 'scorched' sub-state where dark smoke
        wisps off his body. Plausibility ledger logs the loss as a
        negative weather_jolt event."""
        lost = min(50, self.coin_count)
        if lost <= 0:
            return
        self.score = max(0, self.score - lost)
        self.coin_count -= lost
        self._proof.record(self.time_alive, -lost, "weather_jolt")

        # ── Lightning bolt path: jagged polyline from a cloud above
        # Pip down to a point just above his head, with horizontal
        # jitter at each waypoint so no two strikes look the same.
        bx, by = self.bird.x, self.bird.y
        # Bolt terminates ON Pip's body (slightly past his crown) so the
        # impact reads as "the strike is hitting him", not "the strike
        # is hovering above him". Final waypoint at by - 2 places the
        # bright tip squarely inside his upper body silhouette.
        target_y = by - 2
        # Bolt origin: somewhere along the cloud line, slightly off
        # to either side of Pip so the trace reads diagonal not vertical.
        origin_x = bx + random.uniform(-70, 70)
        path = [(origin_x, 0.0)]
        # More segments + wider jitter than the background bolts so the
        # final strike is visibly thicker / jaggier / longer-lived than
        # the telegraph flashes. Jitter still tightens near impact so
        # the bolt converges cleanly onto Pip's body.
        segs = 22
        for i in range(1, segs):
            t = i / segs
            jx = random.uniform(-42, 42) * (1.0 - t * 0.7)
            cx = origin_x * (1 - t) + bx * t + jx
            cy = target_y * t
            path.append((cx, cy))
        path.append((bx, target_y))

        self.lightning_strike = {
            "path": path,
            "life": 0.50,
            "life_max": 0.50,
        }
        # Force a bright full-screen white pulse so the strike reads.
        self.weather.flash_remaining = max(
            self.weather.flash_remaining, 0.22)
        # Stronger, longer shake than a regular jolt.
        self.shake_mag = max(self.shake_mag, 9.0)
        self.shake_t = max(self.shake_t, 0.55)
        # Lockout — one strike per ~25s of peak storm.
        self._storm_jolt_lockout = 25.0
        # Scorch sub-state — smoke wisps off Pip for the next 3.7 s
        # (bumped to outlast the 3.5 s skeleton-flash window so the
        # smoking aftermath continues for ~0.2 s after the flash
        # ends).
        self._lightning_scorch_t = 3.7
        self._scorch_smoke_accum = 0.0
        # X-Ray Sparks flash — 3.5 s total. Solid skeleton hold for
        # the first 0.5 s, then 3.0 s of strobe at 0.30 s per
        # segment (same frequency as before, just longer period):
        # skel/norm/skel/norm/skel/norm/skel/norm/skel/norm — 10
        # segments giving 5 full alternations + the initial hold,
        # so the player clearly sees Pip swap between his skeleton
        # and his normal sprite several times. Strobe lives in
        # Bird.draw.
        self.bird.skeleton_flash_t = 3.50

        # ── Coin blast: faster spread than the previous gust version
        # so the lightning impulse reads as the cause.
        scatter_bx, scatter_by = self.bird.x, self.bird.y + 4
        n = min(lost, 20)
        for i in range(n):
            ang = (i / n) * math.tau + random.uniform(-0.15, 0.15)
            speed = random.uniform(200.0, 320.0)   # faster than the gust
            vx = math.cos(ang) * speed
            vy = math.sin(ang) * speed - 80.0      # slight upward bias
            self.particles.append(FlyingCoinParticle(
                scatter_bx, scatter_by, vx, vy, life=0.95,
            ))

        # ── Electric sparks: cyan/white tendrils flying outward from
        # the impact point. Slightly bigger + longer life than typical
        # so the crackle reads in a single frame and across the next
        # 0.5s of decay.
        for _ in range(40):
            ang = random.uniform(0, math.tau)
            sp = random.uniform(140, 280)
            spark_col = random.choice((
                (220, 240, 255), (180, 220, 255),
                (255, 255, 255), (140, 200, 255),
                (255, 240, 180),   # warmer flash highlight
            ))
            self.particles.append(Particle(
                scatter_bx, scatter_by - 12,
                math.cos(ang) * sp, math.sin(ang) * sp,
                life=random.uniform(0.35, 0.60),
                r=random.choice((3, 3, 4)),
                color=spark_col,
                gravity=180,
            ))

        # ── Text: only the red -50! — placed directly ABOVE Pip,
        # vertically clear of both his 64×60 sprite (top edge at
        # bird.y - 30) and the silhouette-rim aura (~3 px outward).
        # `bird.y - 58` puts the text centre 25 px above the aura
        # top, with the ~15 px text half-height giving a final
        # ~10 px gap on impact frame; the text drifts up further
        # over its 1.6 s life. Horizontally centred on bird.x so
        # the player's eye reads "score change above Pip", not
        # off to one side. ZAP! removed per playtest feedback.
        self.float_texts.append(FloatText(
            f"-{lost}!", self.bird.x, self.bird.y - 58, UI_RED,
            size=30, life=1.6, vy=-26, style="powerup",
        ))

        # ── Audio: layered impact stack so the strike is clearly
        # the loudest event in the storm. Thunder cranked to 0.98
        # (vs the 0.35-0.55 distant-bg claps), poof for the impact
        # gust, and the magnet chime layered low as an "electric
        # crackle" tail so the listener hears the discharge, not
        # just the rumble.
        try:
            audio.play_thunder(volume=0.98)
            audio.play_poof()
            audio.play_magnet(volume=0.55)
        except Exception:
            pass

    def _spawn_scorch_wisp(self):
        """Smoke puff trailing BEHIND Pip in his wake — spawned to his
        left (he flies right, so left = behind) and drifting further
        left + upward so the wisps stream away from him rather than
        covering his body. Critical for the X-Ray Sparks skeleton
        flicker — `scenes.py` draws particles AFTER the bird sprite,
        so any wisp that originates on Pip's silhouette would layer
        over the skeleton view and hide it."""
        bx, by = self.bird.x, self.bird.y
        # Behind-and-around Pip (to his LEFT, with a small vertical
        # spread). Never spawn on his right-facing body where the
        # skeleton view shows.
        ox = random.uniform(-32, -14)
        oy = random.uniform(-18, 12)
        # Drift further LEFT (behind) and gently upward so the trail
        # streams away from Pip rather than rising over him.
        vx = random.uniform(-40, -10)
        vy = random.uniform(-55, -25)
        # Light grey / cream wisps so they CONTRAST with the dark
        # storm sky. Real smoke off something scorched would be sooty
        # but visually the lighter palette reads as a smoke trail
        # against a purple-blue dusk.
        col = random.choice((
            (170, 165, 175), (200, 195, 200),
            (150, 145, 155), (220, 215, 220),
            (185, 180, 190),
        ))
        self.particles.append(Particle(
            bx + ox, by + oy, vx, vy,
            life=random.uniform(0.70, 1.05),
            r=random.randint(5, 8),       # bigger puffs read better
            color=col,
            gravity=-30,                  # more buoyancy
        ))

    def _apply_magnet(self, dt, radius_mult: float = 1.0,
                      strength_mult: float = 1.0):
        """Tug uncollected coins within MAGNET_RADIUS toward the bird.
        `radius_mult` / `strength_mult` let weaker pseudo-magnets reuse
        this routine (e.g. the solar phoenix variant pulls coins at 55%
        radius and 40% strength)."""
        bx, by = self.bird.x, self.bird.y
        radius = MAGNET_RADIUS * radius_mult
        r2 = radius * radius
        for c in self.coins:
            if c.collected:
                continue
            dx = bx - c.x
            dy = by - c.y
            d2 = dx * dx + dy * dy
            if d2 > r2 or d2 < 1.0:
                continue
            d = math.sqrt(d2)
            pull = 520 * strength_mult * (1.0 - d / radius)
            c.x += (dx / d) * pull * dt
            c.y += (dy / d) * pull * dt

    def _spawn_ember_trail_particle(self):
        """Ember-trail variant: spawn a single small ember at Pip's tail
        position with slight backward velocity so it lags behind as the
        world scrolls forward, fading naturally via the Particle's life."""
        col = random.choice((
            (255,  90,  30), (255, 180,  60),
            (255, 230, 130), WHITE,
        ))
        # Tail position — roughly behind Pip's body, scaled with grow.
        scale = 1.0
        if self.grow_timer > 0:
            scale = GROW_SCALE
        tx = self.bird.x - 12 * scale + random.uniform(-2, 2)
        ty = self.bird.y +  2 * scale + random.uniform(-3, 3)
        # Slight backward drift so the trail lags behind a moving Pip.
        vx = random.uniform(-40, -10)
        vy = random.uniform(-25, 25)
        self.particles.append(Particle(
            tx, ty, vx, vy,
            random.uniform(0.4, 0.7),
            random.randint(2, 4),
            col, gravity=30,
        ))

    def _on_coin(self, coin: Coin):
        # Triple buff is the canonical ×3 multiplier. The ember-trail
        # phoenix variant doubles coin value, but stacks NEVER exceed
        # ×3 — phoenix alone gives ×2, phoenix+triple stays at ×3 (no
        # double-dip to 6×).
        if self.triple_timer > 0:
            value = 3
        elif (self.phoenix_timer > 0 and PHOENIX_VARIANT == "ember"):
            value = 2
        else:
            value = 1
        self.score += value
        self.coin_count += 1
        self._proof.record(self.time_alive, value, "coin")

        # *** GLITCH FIX ***
        # NO screen-wide flash. Only localized sparkle particles.
        for _ in range(10):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(80, 220)
            col = random.choice((PARTICLE_GOLD, COIN_LIGHT, PARTICLE_WHT))
            self.particles.append(Particle(
                coin.x, coin.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.4, 0.8),
                random.randint(2, 4),
                col, gravity=300,
            ))
        if value == 3:
            label = "+3"
            color = UI_ORANGE
            size = 32
            text_y_offset = 18
        else:
            label = "+1"
            color = UI_GOLD
            size = 24
            text_y_offset = 8
        # style="powerup" gives the +N a bold dark outline + vertical
        # gradient + sparkle dots, matching the look of the power-up
        # activation float-texts. Gradient/outline are auto-derived from
        # `color`, so +1 reads gold and +3 reads orange.
        self.float_texts.append(
            FloatText(label, coin.x, coin.y - text_y_offset, color,
                      size=size, life=0.9, style="powerup"))

        if value == 3:
            audio.play_coin_triple()
        else:
            audio.play_coin()

    def _on_powerup(self, m: PowerUp):
        # Genie offer: collecting any one of the 3 spawned offers cancels
        # the other two with a mauve poof. Done BEFORE the normal
        # activation so the chosen kind's activator runs normally.
        if getattr(m, "is_genie_offer", False):
            self._cull_genie_offers_except(m)
        # Surprise box: roll a random "real" kind at pickup time, then route
        # through that kind's activator. The resolved activator plays the
        # matching sound — there's no dedicated surprise SFX.
        kind = m.kind
        if kind == "surprise":
            self.powerups_picked["surprise"] = self.powerups_picked.get("surprise", 0) + 1
            # "reverse" is intentionally excluded — feels too disorienting
            # in stacks. The activation code is still wired up; add it back
            # to this tuple (and to POWERUP_WEIGHTS in config.py) to enable.
            kind = random.choice(("triple", "magnet", "slowmo", "kfc", "ghost", "grow"))
            self._spawn_surprise_reveal(m)
        self.powerups_picked[kind] = self.powerups_picked.get(kind, 0) + 1
        if kind == "triple":
            self._activate_triple(m)
        elif kind == "magnet":
            self._activate_magnet(m)
        elif kind == "slowmo":
            self._activate_slowmo(m)
        elif kind == "kfc":
            self._activate_kfc(m)
        elif kind == "ghost":
            self._activate_ghost(m)
        elif kind == "grow":
            self._activate_grow(m)
        elif kind == "reverse":
            self._activate_reverse(m)
        # Secret late-game powerups
        elif kind == "skateboard":
            self._activate_skateboard(m)
        elif kind == "heist":
            self._activate_heist(m)
        elif kind == "lottery":
            self._activate_lottery(m)
        elif kind == "phoenix":
            self._activate_phoenix(m)
        elif kind == "genie":
            self._activate_genie(m)

    def _spawn_surprise_reveal(self, m):
        """Brief gold-burst + cloud puff so the player sees the box "open"
        before the resolved power-up's own activator fires."""
        for _ in range(18):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(140, 280)
            col = random.choice((UI_GOLD, UI_ORANGE, UI_CREAM, WHITE))
            self.particles.append(Particle(
                m.x, m.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.4, 0.8),
                random.randint(2, 4),
                col, gravity=160,
            ))

    def _pickup_burst(self, m, colors, n=30, speed_hi=320, grav=150):
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(100, speed_hi)
            col = random.choice(colors)
            self.particles.append(Particle(
                m.x, m.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.5, 1.0),
                random.randint(3, 6),
                col, gravity=grav,
            ))

    def _activate_triple(self, m):
        self.triple_timer = TRIPLE_DURATION
        self.shake_mag = max(self.shake_mag, 3.0)
        self.shake_t = max(self.shake_t, 0.25)
        audio.play_triple_coin()
        audio.play_poof()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(m, (UI_ORANGE, UI_GOLD, BIRD_RED, UI_CREAM))
        self.float_texts.append(FloatText(
            "3X POWER!", m.x, m.y - 26, UI_ORANGE,
            size=30, life=1.4, vy=-30, style="powerup",
        ))

    def _activate_magnet(self, m):
        self.magnet_timer = MAGNET_DURATION
        self.shake_mag = max(self.shake_mag, 2.5)
        self.shake_t = max(self.shake_t, 0.25)
        audio.play_magnet()
        self._pickup_burst(m, (BIRD_RED, (220, 30, 40), UI_CREAM, WHITE))
        self.float_texts.append(FloatText(
            "MAGNET!", m.x, m.y - 26, BIRD_RED,
            size=28, life=1.3, vy=-30, style="powerup",
        ))

    def _activate_slowmo(self, m):
        self.slowmo_timer = SLOWMO_DURATION
        self.shake_mag = max(self.shake_mag, 2.5)
        self.shake_t = max(self.shake_t, 0.25)
        audio.play_slowmo()
        self._pickup_burst(m, ((180, 100, 255), (120, 60, 200), WHITE, UI_CREAM))
        self.float_texts.append(FloatText(
            "SLOW-MO!", m.x, m.y - 26, (200, 140, 255),
            size=28, life=1.3, vy=-30, style="powerup",
        ))

    def _activate_kfc(self, m):
        self.kfc_timer = KFC_DURATION
        self.bird.kfc_active = True
        # Pick a fries-mountain variant at random for this activation
        # and pre-render it to a Surface. game.fries_mountains has 3
        # variants (classic / boxes / curly); the chosen index +
        # cached Surface are read by PlayScene._draw_background for as
        # long as kfc_timer > 0.
        from game.fries_mountains import (
            KFC_MOUNTAIN_DRAWERS, get_cached_mountain,
        )
        self.kfc_mountain_variant = random.randint(
            0, len(KFC_MOUNTAIN_DRAWERS) - 1)
        # Module-level cache built once per variant — App.__init__ prewarms
        # all variants under the splash, so this is a guaranteed cache hit
        # at pickup time (no frame spike).
        self.kfc_mountain_layers = get_cached_mountain(
            self.kfc_mountain_variant, GROUND_Y, W)
        # Snapshot scroll at pickup so PlayScene can derive the parallax
        # offset (bg_scroll - kfc_activation_scroll) for each layer.
        self.kfc_activation_scroll = self.bg_scroll
        # Retroactively flip every pipe currently on screen so the entire
        # visible scene becomes fast-food at the moment of pickup, AND
        # widen its collision gap. The KFC *visual* is gated on
        # kfc_timer > 0 (see Pipe.draw), so when the timer expires every
        # pillar snaps back to stone alongside the fries mountain + Pip.
        # The wider gap is sticky on the pipe instance, though: it stays
        # for the rest of that pipe's life so the player isn't punished
        # by a mid-flight gap shrink.
        #
        # `is_kfc` is the sticky gap-widened flag and gates the
        # double-boost guard below — a second KFC pickup (or a pipe born
        # during the active window) must not compound 1.30 again.
        for p in self.pipes:
            if not p.is_kfc:
                p.gap_h = int(p.gap_h * KFC_GAP_BOOST)
                p.is_kfc = True
        self.shake_mag = max(self.shake_mag, 5.0)
        self.shake_t   = max(self.shake_t,   0.4)
        audio.play_poof()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(m, ((210, 138, 42), (238, 178, 72), (148, 82, 18), WHITE), n=28)
        self.float_texts.append(FloatText(
            "DEEP FRIED!", m.x, m.y - 26, (230, 160, 40),
            size=28, life=1.6, vy=-28, style="powerup",
        ))

    def _activate_ghost(self, m):
        GHOST_BLUE  = (140, 180, 255)
        GHOST_WHITE = (210, 225, 255)
        self.ghost_timer = GHOST_DURATION
        self.bird.ghost_active = True
        self.shake_mag = max(self.shake_mag, 2.0)
        self.shake_t   = max(self.shake_t,   0.2)
        audio.play_ghost()
        audio.play_poof()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(m, (GHOST_BLUE, GHOST_WHITE, (180, 200, 255)),
                           n=28, speed_hi=260, grav=120)
        # Wisp orbit particles at bird position
        for i in range(10):
            ang = i / 10 * math.tau
            spd = random.uniform(40, 90)
            self.particles.append(Particle(
                self.bird.x + math.cos(ang) * 20,
                self.bird.y + math.sin(ang) * 20,
                math.cos(ang) * spd, math.sin(ang) * spd - 30,
                random.uniform(0.4, 0.8),
                random.randint(2, 4),
                random.choice((GHOST_BLUE, GHOST_WHITE)),
                gravity=60,
            ))
        self.float_texts.append(FloatText(
            "GHOST!", m.x, m.y - 26, (180, 210, 255),
            size=28, life=1.3, vy=-30, style="powerup",
        ))

    def _activate_grow(self, m):
        GROW_HI  = (50, 220, 100)
        GROW_OUT = (28, 160,  70)
        self.grow_timer = GROW_DURATION
        self.bird.grow_active = True
        self.shake_mag = max(self.shake_mag, 4.0)
        self.shake_t   = max(self.shake_t,   0.3)
        audio.play_grow()
        audio.play_poof()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(m, (GROW_HI, GROW_OUT, WHITE, UI_CREAM), n=30, speed_hi=300)
        self.float_texts.append(FloatText(
            "GROW!", m.x, m.y - 26, GROW_HI,
            size=30, life=1.3, vy=-30, style="powerup",
        ))

    def _spawn_poof(self, x, y):
        """Burst of expanding cloud puffs — used on KFC transformation start and end."""
        puff_colors = [
            (255, 255, 255), (240, 240, 240),
            (225, 225, 225), (210, 215, 220),
        ]
        for _ in range(14):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 130)
            vx    = math.cos(angle) * speed
            vy    = math.sin(angle) * speed - random.uniform(10, 40)
            life  = random.uniform(0.32, 0.52)
            r0    = random.randint(4, 9)
            r1    = random.randint(13, 22)
            color = random.choice(puff_colors)
            self.particles.append(CloudPuff(x, y, vx, vy, life, r0, r1, color))

    def _spawn_genie_reveal_poof(self, x, y):
        """Big dramatic poof when a Genie offer materialises — modelled
        on _spawn_poof (the KFC transformation cloud) so the powerup
        appears in a CLEAR puff of magical cloud, not a wisp.
        Lavender + cream + gold palette so it reads as genie magic
        rather than the KFC transformation."""
        puff_colors = [
            (250, 240, 255), (235, 220, 255),
            (220, 200, 250), (255, 240, 200),
            (255, 220, 140), (200, 180, 240),
        ]
        # Big cloud burst (18 puffs, larger radii + life than the
        # original tiny wisp).
        for _ in range(18):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(60, 150)
            vx    = math.cos(angle) * speed
            vy    = math.sin(angle) * speed - random.uniform(12, 40)
            life  = random.uniform(0.40, 0.65)
            r0    = random.randint(5, 11)
            r1    = random.randint(16, 28)
            color = random.choice(puff_colors)
            self.particles.append(CloudPuff(x, y, vx, vy, life, r0, r1, color))
        # A bright central flash burst — a few high-alpha puffs that
        # POP at the centre to sell the "magical appearance" beat.
        for _ in range(4):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(20, 50)
            vx    = math.cos(angle) * speed
            vy    = math.sin(angle) * speed - random.uniform(8, 20)
            self.particles.append(CloudPuff(
                x, y, vx, vy,
                random.uniform(0.18, 0.28),
                10, 22, (255, 250, 235)))
        # Gold sparkle accents (use the existing Particle class so
        # they twinkle as small gravity-affected dots).
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(80, 160)
            vx    = math.cos(angle) * speed
            vy    = math.sin(angle) * speed - random.uniform(20, 50)
            self.particles.append(Particle(
                x, y, vx, vy,
                life=random.uniform(0.45, 0.75),
                r=random.randint(2, 3),
                color=random.choice([
                    (255, 230, 140), (255, 250, 215),
                    (255, 200, 220),
                ]),
                gravity=120,
            ))

    def _activate_reverse(self, m):
        self.reverse_timer = REVERSE_DURATION
        # Zero vy so the flip feels snappy instead of inheriting downward speed.
        self.bird.vy = 0.0
        self.shake_mag = max(self.shake_mag, 2.5)
        self.shake_t = max(self.shake_t, 0.25)
        audio.play_slowmo()
        self._pickup_burst(m, ((170, 90, 230), (110, 50, 180), (215, 165, 250), WHITE))
        self.float_texts.append(FloatText(
            "FLIP!", m.x, m.y - 26, (190, 130, 245),
            size=30, life=1.3, vy=-30, style="powerup",
        ))

    # ── SECRET LATE-GAME ACTIVATORS ─────────────────────────────────────────

    def _activate_skateboard(self, m):
        from game.skateboard_fx import (
            render_caption_overlay, render_starburst_surface,
        )
        self.skateboard_timer = SKATEBOARD_DURATION
        self.bird.skateboard_active = True
        self._tap_streak = 0
        self._last_tap_t = -999.0
        self.shake_mag = max(self.shake_mag, 4.0)
        self.shake_t = max(self.shake_t, 0.3)
        audio.play_skateboard()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(m, ((60, 60, 70), (180, 180, 190), UI_ORANGE, UI_GOLD), n=28)
        # Activation FX split:
        #   * caption — tilted SKATEBOARD! plate + POW! badge + corner
        #     slashes — STATIC at top of screen, fades over 2.5 s so
        #     the player has time to read it.
        #   * burst — the 14-spike starburst, small surface centered on
        #     Pip's current position each frame so it APPEARS to ride
        #     with him. Short by design (0.6 s) so it doesn't cover the
        #     game for long.
        seed = int(self._idle_t * 1000) & 0xFFFF
        # Caption beats: held at full alpha for the entire skateboard
        # duration MINUS the trailing 0.8 s, then a 0.8 s fade. scenes.py
        # keys the fade off the trailing 0.8 s of the timer. Matching
        # SKATEBOARD_DURATION means the banner is visible for the whole
        # effect (the user wants the D5 score under the banner to coexist
        # with it the entire time).
        self.skateboard_caption_dur = SKATEBOARD_DURATION
        self.skateboard_caption_t = self.skateboard_caption_dur
        self.skateboard_caption_overlay = render_caption_overlay(
            int(self.bird.x), int(self.bird.y), rng_seed=seed,
        )
        # Burst beats: 1.5 s held at full alpha, then a 0.8 s fade.
        # scenes.py keys the fade off the trailing 0.8 s of the timer.
        self.skateboard_burst_dur = 2.3
        self.skateboard_burst_t = self.skateboard_burst_dur
        self.skateboard_burst_surface = render_starburst_surface(
            rng_seed=seed,
        )
        self.skateboard_burst_cx = int(self.bird.x)
        self.skateboard_burst_cy = int(self.bird.y)

    def _activate_heist(self, m):
        # Treasure box: start the duration buff. While it's active the
        # chest hangs under Pip's belly (drawn by PlayScene) and each
        # flap drops coins via _drop_treasure_box_coins().
        self.treasure_box_timer = TREASURE_BOX_DURATION
        self.shake_mag = max(self.shake_mag, 3.0)
        self.shake_t = max(self.shake_t, 0.25)
        audio.play_heist()
        self._pickup_burst(m, (UI_GOLD, UI_ORANGE, UI_CREAM, WHITE), n=26)
        self.float_texts.append(FloatText(
            "TREASURE BOX!", m.x, m.y - 26, UI_GOLD,
            size=26, life=1.5, vy=-30, style="powerup",
        ))

    def _apply_lottery_result(self):
        anim = self.lottery_anim
        if anim is None:
            return
        delta = anim["delta"]
        tier = anim["tier"]
        # Apply score delta with clamping: don't go below 0. coin_count is
        # NOT touched — plausibility requires coin_count == len(coin events),
        # so lottery deltas use a distinct "lottery" event kind in the proof.
        if delta > 0:
            self.score += delta
            self._proof.record(self.time_alive, delta, "lottery")
            color = UI_GOLD if delta >= 40 else UI_ORANGE
            audio.play_lottery_win()
        elif delta < 0:
            actual = -min(self.score, -delta)  # negative number, capped
            self.score += actual
            if actual != 0:
                self._proof.record(self.time_alive, actual, "lottery")
            color = (220, 70, 60)
            audio.play_lottery_bust()
        else:
            color = (200, 200, 200)
        # Result float text over the bird.
        sign = "+" if delta > 0 else ""
        label = f"{tier}! {sign}{delta}" if delta != 0 else f"{tier}!"
        self.float_texts.append(FloatText(
            label, self.bird.x, self.bird.y - 40, color,
            size=28, life=1.4, vy=-30, style="powerup",
        ))
        # Tier-flavored particle burst at the bird.
        if delta >= 100:
            colors = (UI_GOLD, UI_ORANGE, UI_CREAM, WHITE)
            self._pickup_burst(self.bird, colors, n=40, speed_hi=380)
        elif delta >= 15:
            self._pickup_burst(self.bird, (UI_GOLD, UI_CREAM, WHITE), n=20)
        elif delta < 0:
            self._pickup_burst(self.bird, ((220, 70, 60), (140, 30, 30), (80, 80, 80)), n=18)

    def _activate_lottery(self, m):
        # Roll the tier immediately; the reveal animation (slot-reel
        # ticks) just delays the score change for showmanship.
        labels = [t[0] for t in LOTTERY_TIERS]
        weights = [t[1] for t in LOTTERY_TIERS]
        deltas = {t[0]: t[2] for t in LOTTERY_TIERS}
        tier = random.choices(labels, weights=weights, k=1)[0]
        delta = deltas[tier]
        self.lottery_anim = {
            "t": 0.0,
            "tier": tier,
            "delta": delta,
            "x": m.x,
            "y": m.y,
            "applied": False,
        }
        self.shake_mag = max(self.shake_mag, 2.5)
        self.shake_t = max(self.shake_t, 0.2)
        audio.play_lottery_roll()
        self._pickup_burst(m, (UI_GOLD, UI_ORANGE, UI_CREAM, WHITE), n=22)
        self.float_texts.append(FloatText(
            "LOTTERY!", m.x, m.y - 26, UI_GOLD,
            size=26, life=1.0, vy=-30, style="powerup",
        ))

    def _activate_phoenix(self, m):
        PHOENIX_RED  = (240,  50,  30)
        PHOENIX_GOLD = (255, 190,  60)
        self.phoenix_timer = PHOENIX_DURATION
        self.bird.phoenix_active = True
        self.shake_mag = max(self.shake_mag, 3.5)
        self.shake_t   = max(self.shake_t,   0.3)
        audio.play_phoenix()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(m, (PHOENIX_RED, PHOENIX_GOLD, WHITE, UI_CREAM),
                           n=32, speed_hi=320)
        self.float_texts.append(FloatText(
            "PHOENIX!", m.x, m.y - 26, PHOENIX_GOLD,
            size=30, life=1.4, vy=-32, style="powerup",
        ))

    def _activate_genie(self, m):
        """Genie Lamp — instead of granting a buff directly, spawn
        GENIE_OFFER_COUNT alternate powerup pickups in the play field
        ahead of Pip. All offers are unique kinds drawn from
        POWERUP_WEIGHTS (minus 'surprise' and 'genie' itself). The
        player flies into the offer they want; the others get culled
        the moment any one is picked up (see _on_powerup branch on
        is_genie_offer). One-button compatible — no new input."""
        eligible = [k for (k, _w) in POWERUP_WEIGHTS
                    if k not in ("surprise", "genie")]
        # Add secret kinds the player has unlocked (score >= LATE_GAME_SCORE).
        if self.score >= LATE_GAME_SCORE:
            for (k, _w) in SECRET_POWERUP_WEIGHTS:
                if k not in ("genie",) and k not in eligible:
                    eligible.append(k)
        if len(eligible) < GENIE_OFFER_COUNT:
            # Degenerate fallback — pool too small, treat as surprise.
            kind = random.choice(eligible) if eligible else "triple"
            self.powerups_picked[kind] = self.powerups_picked.get(kind, 0) + 1
            self._on_powerup(PowerUp(m.x, m.y, kind=kind))
            return
        chosen = random.sample(eligible, GENIE_OFFER_COUNT)
        # Random y assignment per offer keeps the player from
        # memorising which slot is "best".
        slots = list(GENIE_OFFER_Y_SLOTS[:GENIE_OFFER_COUNT])
        random.shuffle(slots)
        # Summon a Genie character that floats above where the middle
        # offer will be conjured. It scrolls left with the world and
        # spawns the three offers + reveal poofs on its own cast beats
        # (see GenieCharacter in game/entities.py). The lamp's own
        # pickup-site burst / float text / audio still fire below.
        from game.entities import GenieCharacter
        # Genie hovers STATIONARY (vx=0). Default spawn is at
        # (gx=180, gy=215) — below the score pill (y=64..120), at
        # screen centre, where the locked design renders cleanly at
        # display_scale=0.34. If the parrot is currently flying near
        # the default y (i.e., the player happens to be high in the
        # frame), the genie spawns at a FALLBACK position lower down
        # — gy=440, just above the mountain peaks — so it doesn't
        # sit directly on top of the bird. Offers (in _fire_all)
        # are placed independently of genie y, so the cinematic
        # plays out the same either way.
        DEFAULT_GY  = 215
        FALLBACK_GY = 440           # just above the mountain peaks
        TOO_CLOSE   = 100           # px window around a candidate y
        if abs(self.bird.y - DEFAULT_GY) >= TOO_CLOSE:
            gy = DEFAULT_GY
        elif abs(self.bird.y - FALLBACK_GY) >= TOO_CLOSE:
            gy = FALLBACK_GY
        else:
            # Parrot is awkwardly between both candidates — pick the
            # one further from the parrot regardless.
            gy = (DEFAULT_GY
                  if abs(self.bird.y - DEFAULT_GY) > abs(self.bird.y - FALLBACK_GY)
                  else FALLBACK_GY)
        gx = 180                    # screen centre, clear of HUD chrome
        offers = list(zip(chosen, slots))
        self.genie_actors.append(GenieCharacter(
            gx, gy, vx=0.0,
            offers=offers, world=self,
        ))
        # Smoke + brass burst at pickup site.
        self.shake_mag = max(self.shake_mag, 2.0)
        self.shake_t   = max(self.shake_t, 0.2)
        try:
            audio.play_genie()
        except Exception:
            pass
        self._pickup_burst(
            m, ((185, 130, 45), (250, 215, 130),
                (170, 130, 195), (220, 200, 240)),
            n=24, speed_hi=260,
        )
        self.float_texts.append(FloatText(
            "GENIE!", m.x, m.y - 26, (250, 215, 130),
            size=28, life=1.3, vy=-28, style="powerup",
        ))

    def _cull_genie_offers_except(self, chosen: "PowerUp"):
        """Mark every other is_genie_offer pickup as collected (so the
        regular off-screen/collected sweep removes them next frame) and
        puff a small cloud where each sibling stood so the player sees
        the unchosen wishes evaporate."""
        for p in self.powerups:
            if p is chosen or not getattr(p, "is_genie_offer", False):
                continue
            p.collected = True
            # Tiny mauve puff to read "wish evaporates".
            for _ in range(8):
                ang = random.uniform(0, math.tau)
                sp = random.uniform(40, 90)
                self.particles.append(Particle(
                    p.x, p.y,
                    math.cos(ang) * sp, math.sin(ang) * sp - 30,
                    life=0.5, r=3, color=(170, 130, 195),
                    gravity=200,
                ))
        # Kill any active GenieCharacter so its remaining cast beats
        # don't spawn orphan offers after the player has locked in
        # their pick.
        for g in self.genie_actors:
            g.kill()

    # ── utility ──────────────────────────────────────────────────────────────

    def shake_offset(self):
        if self.shake_t <= 0 or self.shake_mag <= 0:
            return 0, 0
        amp = self.shake_mag * (self.shake_t / 0.45)
        return (random.uniform(-amp, amp), random.uniform(-amp, amp))
