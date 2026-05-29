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
    MEGAMAGNET_DURATION, MEGAMAGNET_RADIUS,
    SLOWMO_DURATION, SLOWMO_SCALE, KFC_DURATION, KFC_GAP_BOOST, GHOST_DURATION,
    GROW_DURATION, GROW_SCALE, REVERSE_DURATION,
    POWERUP_WEIGHTS, POWERUP_SCORE_GATES, POWERUP_REPLACED_AT,
    SHRINK_DURATION, SHRINK_SCALE,
    RAIL_PILLAR_COUNT, RAIL_SCROLL_MULT,
    LOTTERY_TIERS, LOTTERY_REVEAL_TIME,
    FLAP_V,
    COIN_RUSH_INTERVAL, COIN_RUSH_GAP_BOOST, COIN_RUSH_COINS,
    SECRET_POWERUP_WEIGHTS, LATE_GAME_SCORE,
    GENIE_OFFER_COUNT, GENIE_OFFER_Y_SLOTS,
    SKATEBOARD_DURATION, SKATE_SLIDE_MULT, SKATE_SLIDE_ATTACK,
    SKATE_SLIDE_RELEASE, BACKFLIP_DURATION,
    KNIGHT_DURATION, KNIGHT_INVULN,
    DEATH_FADE_DURATION,
)
from game.entities import (
    Bird, Pipe, Coin, PowerUp, Particle, CloudPuff, PoofGrain, FloatText,
    GenieCharacter,
)
from game._proof import ProofState
from game.draw import (
    COIN_GOLD, COIN_LIGHT,
    PARTICLE_GOLD, PARTICLE_ORNG, PARTICLE_WHT, PARTICLE_CRIM,
    UI_GOLD, UI_ORANGE, UI_CREAM, WHITE, BIRD_RED,
)
from game import biome
from game import audio
from game.weather import Weather
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
        self.float_texts: list[FloatText] = []

        self.scroll_speed = SCROLL_BASE
        self.bg_scroll = 0.0

        self.score = 0
        self.coin_count = 0

        self.triple_timer = 0.0
        self.magnet_timer = 0.0
        self.megamagnet_timer = 0.0
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
        self.shrink_timer = 0.0
        # RAIL TRACK: pillar-limited buff. Tagging is fixed at activation
        # — exactly RAIL_PILLAR_COUNT pillars get rail_active set in
        # _activate_rail and nothing else picks up the tag afterward.
        # rail_pipes is rebuilt from self.pipes' rail_active flags every
        # frame so the renderer still sees the on-screen tail of tagged
        # pipes after expiry. rail_pending is the count of force-spawned
        # pipes the next _spawn_pipe call should tag.
        self.rail_pillars_left = 0
        self.rail_pipes: list = []
        self.rail_cart_pipe = None
        self.rail_pending = 0
        # Lottery reveal animation. None when not rolling; a dict
        # {t, tier, delta, x, y, applied} while the scratch-card reels
        # are ticking. Result lands at LOTTERY_REVEAL_TIME.
        self.lottery_anim: "dict | None" = None
        self.powerup_cooldown = 0.0

        # ── Secret late-game power-ups ──────────────────────────────────────
        # GENIE: companion conjurer actors. Each is ticked + culled in update.
        self.genie_actors: list = []
        # SKATEBOARD: timed grind buff. slide_boost is an attack/release
        # envelope (0..1) that ramps up while Pip grinds a surface and decays
        # otherwise; _current_scroll reads it to speed the world up.
        self.skateboard_timer = 0.0
        self.slide_boost = 0.0
        self._sliding_this_frame = False
        self._sliding_prev_frame = False
        # Activation overlays (drawn in scenes): caption banner + starburst.
        self.skateboard_caption_t = 0.0
        self.skateboard_caption_dur = 0.0
        self.skateboard_caption_overlay = None
        self.skateboard_burst_t = 0.0
        self.skateboard_burst_dur = 0.0
        self.skateboard_burst_surface = None
        self.skateboard_burst_cx = 0
        self.skateboard_burst_cy = 0
        self._skateboard_lift_y = 26
        # KNIGHT: survive-one-hit. While knight_timer > 0 the next lethal hit
        # is consumed in _die() and Pip revives with knight_invuln seconds of
        # collision grace.
        self.knight_timer = 0.0
        self.knight_invuln = 0.0

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
            "triple": 0, "magnet": 0, "megamagnet": 0, "slowmo": 0, "kfc": 0,
            "ghost": 0, "grow": 0, "reverse": 0, "surprise": 0,
            "shrink": 0, "rail": 0, "lottery": 0,
            "skateboard": 0, "knight": 0, "genie": 0,
            "poison": 0,
        }
        # Transient flag so near-miss detection fires once per pillar.
        self._near_miss_flags: dict[int, bool] = {}

        self.hit_flash = 0.0    # death-only red tint, NOT coin
        self.shake_mag = 0.0
        self.shake_t = 0.0

        # Real elapsed gameplay seconds — drives the day/night biome cycle.
        # Held at 0 while ready_t > 0 so the sky doesn't tick over while
        # the player is still on the start-of-run prompt.
        self.biome_time = 0.0

        # Always-ticking clock used for purely-cosmetic idle animations
        # (bird bob during the ready wait) so they keep moving even while
        # biome_time is frozen.
        self._idle_t = 0.0

        # Tamper-evident parallel ledger of every scoring event in the
        # run. The leaderboard submission carries the proof state, not
        # ``self.score``, so a JS-side ``world.score = 99999`` does not
        # change what gets submitted.
        self._proof = ProofState()

        self.weather = Weather()
        self.ambient = AmbientScenes()

        # "Get ready" freeze at the start of a round: physics paused until
        # the player flaps or the timer expires. Gives new players a moment
        # to orient before the first pillar scrolls in (REVIEW.md finding).
        self.ready_t = 1.0

        self.game_over = False

        # Genie playtest: every fresh run jumps past newbie mode, opens
        # at score 450 (so the genie's late-game gate is met from frame 1),
        # aligns the biome to where it would be at that score, and force-
        # spawns the genie every 5 power-up-eligible pillars up to 5
        # times. v5_skybit_powerups_final ships this unconditionally so
        # the browser deploy starts straight into the playtest scenario.
        self.pillars_passed = RAMP_PIPES
        self.score = 450
        self.biome_time = 450 * PIPE_SPACING / SCROLL_BASE
        self._playtest_genie_remaining = 5
        self._playtest_genie_pipes_until_next = 1

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
        # RAIL: world rushes by RAIL_SCROLL_MULT× while Pip is locked on
        # the cart. Pre-lock, normal speed so the player can take their
        # time deciding whether to land on the parked cart.
        if self.bird.cart_locked:
            base *= RAIL_SCROLL_MULT
        # SKATEBOARD grind: lerp from 1.0 to SKATE_SLIDE_MULT on the
        # slide-boost envelope so the speed-up eases in/out instead of
        # snapping when Pip lands on / lifts off a surface.
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
        # Rail tag: claimed at spawn if _activate_rail is force-spawning
        # pillars to fill out the 5-pillar track and this pipe isn't a
        # rush pillar.
        p.rail_active = False
        self.pipes.append(p)
        if getattr(self, "rail_pending", 0) > 0 and not is_rush:
            p.rail_active = True
            self.rail_pipes.append(p)
            self.rail_pending -= 1
        if is_rush:
            self._spawn_rush_coins(p)
            self._announce_rush(p)
        else:
            self._spawn_coins_in_gap(p)
            self._maybe_spawn_powerup(p)

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
        # Playtest force-spawn: every 5 power-up-eligible (non-rush) pipes
        # plant a genie regardless of cooldown / chance / weights, up to 5
        # times. Hardcoded ON on this branch so the browser deploy starts
        # straight into the playtest scenario.
        if self._playtest_genie_remaining > 0:
            self._playtest_genie_pipes_until_next -= 1
            if self._playtest_genie_pipes_until_next <= 0:
                x = pipe.x + PIPE_W + self._current_spacing() * 0.5
                y = pipe.gap_y
                self.powerups.append(PowerUp(x, y, kind="genie"))
                self.powerup_cooldown = POWERUP_COOLDOWN
                self._playtest_genie_remaining -= 1
                self._playtest_genie_pipes_until_next = 5
                return
        if self.powerup_cooldown > 0:
            return
        if random.random() >= self._current_powerup_chance():
            return
        # Score-gated kinds drop out of the pool until the run's score
        # crosses each kind's threshold. Lets late-game pickups stay
        # rare for new players while showing up reliably once the run
        # has built momentum. POWERUP_REPLACED_AT is the inverse:
        # kinds drop OUT once the score crosses their replacement
        # threshold (used to swap magnet -> megamagnet at 250).
        kinds, weights = [], []
        for k, w in POWERUP_WEIGHTS:
            if POWERUP_SCORE_GATES.get(k, 0) > self.score:
                continue
            replaced_at = POWERUP_REPLACED_AT.get(k)
            if replaced_at is not None and self.score >= replaced_at:
                continue
            kinds.append(k)
            weights.append(w)
        # Secret late-game tier: only enters the roll once the run crosses
        # LATE_GAME_SCORE. Kept out of POWERUP_WEIGHTS (and the Surprise
        # re-roll) so the gate can't be bypassed.
        if self.score >= LATE_GAME_SCORE:
            for k, w in SECRET_POWERUP_WEIGHTS:
                kinds.append(k)
                weights.append(w)
        if not kinds:
            return
        kind = random.choices(kinds, weights=weights, k=1)[0]
        x = pipe.x + PIPE_W + self._current_spacing() * 0.5 + random.uniform(-20, 20)
        y = pipe.gap_y + random.uniform(-10, 10)
        self.powerups.append(PowerUp(x, y, kind=kind))
        self.powerup_cooldown = POWERUP_COOLDOWN

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
            # SKATEBOARD: flapping mid-skate spins a backflip trick.
            if self.bird.skateboard_active and self.bird.backflip_t <= 0:
                self.bird.backflip_t = BACKFLIP_DURATION
                self.bird.backflip_dur = BACKFLIP_DURATION
                audio.play_backflip()

    # ── update ──────────────────────────────────────────────────────────────

    def update(self, dt):
        self._idle_t += dt
        # Dead-Pip cross-fade ticks every frame regardless of game state —
        # bird physics is frozen after death so this is the only thing
        # advancing the alpha blend in Bird.draw.
        if 0 < self.bird.death_fade_t < DEATH_FADE_DURATION:
            self.bird.death_fade_t = min(
                DEATH_FADE_DURATION, self.bird.death_fade_t + dt)
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
            for t in self.float_texts:
                t.update(dt)
            self.float_texts = [t for t in self.float_texts if t.alive()]
            return

        if not self.game_over:
            sign = -1 if self.reverse_timer > 0 else 1
            self.bird.update(dt, gravity_sign=sign)  # bird physics at real time
            # Terminal poison: Bird.update ramps poison_t toward 1.0; when
            # it caps, the death pipeline takes over. Knight intercept in
            # _die handles the only escape path.
            if self.bird.poison_active and self.bird.poison_t >= 1.0:
                self._die()

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

            # Magnet pull — tug uncollected coins toward the bird.
            # Either timer triggers; the bigger radius wins if both
            # are somehow active simultaneously (shouldn't happen
            # under the swap-at-250 rule but defensive anyway).
            if self.magnet_timer > 0 or self.megamagnet_timer > 0:
                self._apply_magnet(dt)

            # cull off-screen — but keep rail-active pipes alive past
            # the normal off-screen threshold so the polyline's left
            # bridge segment is fully off-screen before its anchor
            # pipe culls. Without this, when the player flies above
            # the cart without locking, each rail pipe culls the
            # instant its right edge crosses the left screen edge,
            # and the still-on-screen ~100-150 px bridge from that
            # pipe to the next pipe "pops" off, making chunks of
            # the track disappear behind the parrot.
            # While Pip is locked on the cart, keep rail pipes
            # indefinitely past off-screen so the polyline extends
            # far behind during the ride for visual flair.
            self.pipes = [
                p for p in self.pipes
                if not p.off_screen()
                or (getattr(p, "rail_active", False)
                    and (self.bird.cart_locked or p.x + PIPE_W > -300))
            ]
            # Refresh rail_pipes every frame so the renderer still sees
            # the on-screen tail of tagged pipes after expiry.
            self.rail_pipes = [
                p for p in self.pipes if getattr(p, "rail_active", False)
            ]
            self.coins = [c for c in self.coins if c.x + 20 > 0 and not c.collected]
            self.powerups = [m for m in self.powerups if m.x + 20 > 0 and not m.collected]

            # spawn more pipes. Suppressed while the rail powerup is
            # active so no untagged pipe slips between the pre-spawned
            # track and the right edge. After the ride ends the pipe
            # list may be empty (all rail pipes culled); re-seed one
            # fresh pipe so the player has something to navigate.
            spacing = self._current_spacing()
            if not self.bird.cart_active:
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
                    # RAIL: count down the per-ride pillar budget. Fires
                    # whether or not Pip locked — if all 5 tagged pipes
                    # pass without a lock the powerup expires silently.
                    if (self.bird.cart_active
                            and getattr(p, "rail_active", False)
                            and self.rail_pillars_left > 0):
                        self.rail_pillars_left -= 1
                        if p is getattr(self, "rail_cart_pipe", None):
                            self.rail_cart_pipe = None
                        if self.rail_pillars_left == 0:
                            self._end_rail_ride()

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
            if self.megamagnet_timer > 0:
                self.megamagnet_timer = max(0.0, self.megamagnet_timer - dt)
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
            self.bird.grow_active = self.grow_timer > 0
            if self.reverse_timer > 0:
                self.reverse_timer = max(0.0, self.reverse_timer - dt)
            if self.shrink_timer > 0:
                self.shrink_timer = max(0.0, self.shrink_timer - dt)
            self.bird.shrink_active = self.shrink_timer > 0
            # SKATEBOARD: timer + slide-boost envelope (attack while grinding,
            # release otherwise) + activation overlay timers.
            if self.skateboard_timer > 0:
                self.skateboard_timer = max(0.0, self.skateboard_timer - dt)
            self.bird.skateboard_active = self.skateboard_timer > 0
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
            # KNIGHT: buff timer + post-revive collision grace.
            if self.knight_timer > 0:
                self.knight_timer = max(0.0, self.knight_timer - dt)
            self.bird.knight_active = self.knight_timer > 0
            if self.knight_invuln > 0:
                self.knight_invuln = max(0.0, self.knight_invuln - dt)
            # GENIE: tick + cull companion conjurer actors.
            for g in self.genie_actors:
                g.update(dt)
            self.genie_actors = [g for g in self.genie_actors if g.alive()]
            # Lottery reveal ticks every frame regardless of any other
            # timer. _apply_lottery_result fires once at the reveal
            # mark; the dict lingers a moment after so the confetti /
            # tier label still renders, then clears.
            if self.lottery_anim is not None:
                self.lottery_anim["t"] += dt
                if (not self.lottery_anim["applied"]
                        and self.lottery_anim["t"] >= LOTTERY_REVEAL_TIME):
                    self._apply_lottery_result()
                    self.lottery_anim["applied"] = True
                if self.lottery_anim["t"] >= LOTTERY_REVEAL_TIME + 1.4:
                    self.lottery_anim = None
            if self.powerup_cooldown > 0:
                self.powerup_cooldown -= dt
            if self.hit_flash > 0:
                self.hit_flash = max(0.0, self.hit_flash - dt)
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
        for t in self.float_texts:
            t.update(dt)
        self.float_texts = [t for t in self.float_texts if t.alive()]

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

    # ── collisions ───────────────────────────────────────────────────────────

    def bird_radius(self) -> float:
        if self.grow_timer > 0:
            return BIRD_R * GROW_SCALE
        if self.shrink_timer > 0:
            return BIRD_R * SHRINK_SCALE
        return BIRD_R

    def _check_collisions(self):
        bx, by = self.bird.x, self.bird.y
        br = self.bird_radius()
        # SKATEBOARD: while skating Pip grinds surfaces instead of dying on
        # them. `_sliding_this_frame` is reset each frame and flipped True by
        # the ground / pillar-top snaps below so update() can ramp the
        # slide-boost up while he's actually grinding and fade it otherwise.
        skating = self.skateboard_timer > 0
        self._sliding_this_frame = False
        # Ceiling: clamp Pip and zero upward velocity instead of killing.
        # Bonking the top edge feels accidental and was a recurring "unfair
        # death" complaint; the ground still kills.
        if by - br < 0:
            self.bird.y = br
            if self.bird.vy < 0:
                self.bird.vy = 0.0
            by = self.bird.y
        # KNIGHT grace: brief window after a revive where Pip is immune to
        # ground + pipe collisions so he can clear the obstacle that hit him.
        if self.knight_invuln > 0:
            return
        if by + br > GROUND_Y:
            if skating:
                # Slide along the ground instead of dying.
                self.bird.y = GROUND_Y - br
                self.bird.vy = 0.0
                by = self.bird.y
                self._sliding_this_frame = True
            else:
                self._die()
                return
        if self.ghost_timer > 0:
            return  # phase through pipes while ghost is active
        if self.bird.cart_locked:
            # Rail has taken over — re-snap Pip onto the rail every
            # frame (interpolated y between consecutive rail pipes,
            # slope written to bird.cart_tilt_deg). Phase through
            # tagged pillars; the rail bridges them.
            self._snap_cart_to_rail(self.bird.x)
            return
        # SKATEBOARD: proactive pillar-top snap. Snapping Pip's full-radius
        # bottom to the lower-pillar top (instead of waiting for the shrunken
        # pipe hitbox below) keeps the grind smooth, and the PIPE_HITBOX_SHRINK
        # deadband then clears the lethal check while he rides the top.
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
                    self._sliding_this_frame = True
                    break
        # Pip's hitboxes: body (existing) + parcel below him. The parcel
        # offset rotates with his tilt so when he dives the parcel swings
        # forward/down with him.
        if self.grow_timer > 0:
            scale = GROW_SCALE
        elif self.shrink_timer > 0:
            scale = SHRINK_SCALE
        else:
            scale = 1.0
        parcel_offset = pygame.math.Vector2(
            0, PARCEL_Y_OFFSET * scale).rotate(-self.bird.tilt_deg)
        px = bx + parcel_offset.x
        py = by + parcel_offset.y
        pr = PARCEL_R * scale
        # While skating the parcel IS the board under Pip's feet, so its
        # collision footprint is gone — only Pip's body hitbox applies.
        if skating:
            pr = 0
        # RAIL: parked-cart hitbox. Only touching the cart itself (a
        # small rect sitting in the gap of rail_cart_pipe) locks Pip
        # onto the rail. Hitting the pillar BODY of that same pipe —
        # or any other tagged pillar — is fatal like any other pillar.
        cart_pipe = getattr(self, "rail_cart_pipe", None)
        if (self.bird.cart_active
                and not self.bird.cart_locked
                and cart_pipe is not None):
            if (self._circle_hits_cart(cart_pipe, bx, by, br)
                    or self._circle_hits_cart(cart_pipe, px, py, pr)):
                self._lock_pip_on_cart()
                return
        # Parcel shouldn't graze the ground unless the bird already would
        # have died (the bird circle's r > parcel offset+r in normal flight).
        # Skip ground/ceiling re-check; only pipes are added.
        for p in self.pipes:
            if p.collides_circle(bx, by, br - PIPE_HITBOX_SHRINK):
                self._die()
                return
            if pr > 0 and p.collides_circle(px, py, pr - 1):
                self._die()
                return

    def _die(self):
        if self.game_over:
            return
        # KNIGHT revive: if the survive-one-hit buff is active, consume it
        # instead of dying and revive Pip with a grace window. Knight is
        # the only escape from poison — clear that state too.
        if self.bird.knight_active:
            self.knight_timer = 0.0
            self.bird.knight_active = False
            self.bird.poison_active = False
            self.bird.poison_t = 0.0
            self._revive_knight()
            return
        self.game_over = True
        self.bird.alive = False
        # Start the dead-Pip cross-fade. Tiny non-zero value gates the
        # overlay in Bird.draw; world.update advances it each frame.
        self.bird.death_fade_t = 1e-6
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

    def _apply_magnet(self, dt):
        """Tug uncollected coins toward the bird. Pull radius is
        MEGAMAGNET_RADIUS when the megamagnet timer is active,
        otherwise MAGNET_RADIUS. Pull strength is the same."""
        radius = MEGAMAGNET_RADIUS if self.megamagnet_timer > 0 else MAGNET_RADIUS
        r2 = radius * radius
        bx, by = self.bird.x, self.bird.y
        for c in self.coins:
            if c.collected:
                continue
            dx = bx - c.x
            dy = by - c.y
            d2 = dx * dx + dy * dy
            if d2 > r2 or d2 < 1.0:
                continue
            d = math.sqrt(d2)
            pull = 520 * (1.0 - d / radius)
            c.x += (dx / d) * pull * dt
            c.y += (dy / d) * pull * dt

    def _on_coin(self, coin: Coin):
        value = 3 if self.triple_timer > 0 else 1
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
        # Genie offer: collecting any one of the spawned offers cancels the
        # others (with a poof). Done before activation so the chosen kind's
        # activator still runs normally below.
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
            # `grow` is excluded too — it's a late-game-gated pickup
            # (POWERUP_SCORE_GATES["grow"] == 250). Letting a Surprise
            # Box resolve to grow would bypass the gate.
            # Surprise honours the magnet -> megamagnet swap rule: once
            # the run hits POWERUP_REPLACED_AT["magnet"], surprise rolls
            # megamagnet instead of magnet so the box doesn't sneak the
            # downgrade past the threshold.
            magnet_kind = ("megamagnet"
                           if self.score >= POWERUP_REPLACED_AT.get("magnet", 1 << 30)
                           else "magnet")
            kind = random.choice(("triple", magnet_kind, "slowmo", "kfc", "ghost", "shrink"))
            self._spawn_surprise_reveal(m)
        self.powerups_picked[kind] = self.powerups_picked.get(kind, 0) + 1
        if kind == "triple":
            self._activate_triple(m)
        elif kind == "magnet":
            self._activate_magnet(m)
        elif kind == "megamagnet":
            self._activate_megamagnet(m)
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
        elif kind == "shrink":
            self._activate_shrink(m)
        elif kind == "rail":
            self._activate_rail(m)
        elif kind == "lottery":
            self._activate_lottery(m)
        elif kind == "skateboard":
            self._activate_skateboard(m)
        elif kind == "knight":
            self._activate_knight(m)
        elif kind == "genie":
            self._activate_genie(m)
        elif kind == "poison":
            self._activate_poison(m)

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

    def _activate_megamagnet(self, m):
        self.megamagnet_timer = MEGAMAGNET_DURATION
        self.shake_mag = max(self.shake_mag, 3.5)
        self.shake_t = max(self.shake_t, 0.3)
        audio.play_megamagnet()
        self._pickup_burst(m, (BIRD_RED, (220, 30, 40), UI_CREAM, WHITE),
                           n=42, speed_hi=380)
        self.float_texts.append(FloatText(
            "MEGAMAGNET!", m.x, m.y - 26, BIRD_RED,
            size=32, life=1.4, vy=-32, style="powerup",
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

    # ── Secret late-game power-ups ───────────────────────────────────────────

    def _spawn_grainy_poof(self, x, y, palette=None, n=None, rx=34, ry=34):
        """Magic-dust poof — a puffy CLOUD that covers its source, built from
        a few overlapping soft lobes densely packed with motes so it reads as
        a cohesive, lumpy cloud. (rx, ry) set the area covered. Used for every
        genie beat: the genie / offers appearing and vanishing."""
        if palette is None:
            palette = [(255, 180, 190), (255, 225, 170), (255, 250, 180),
                       (190, 240, 200), (180, 225, 255), (215, 190, 255),
                       (255, 255, 255)]
        if n is None:
            n = max(140, int(rx * ry * 0.28))
        base = min(rx, ry)
        lobes = [(0.0, 0.0, 0.90 * base)]
        for _ in range(random.randint(5, 7)):
            la = random.uniform(0, math.tau)
            lr = random.uniform(0.0, 0.60)
            lobes.append((math.cos(la) * rx * lr,
                          math.sin(la) * ry * lr,
                          random.uniform(0.50, 0.80) * base))
        for _ in range(n):
            lox, loy, lrad = random.choice(lobes)
            a  = random.uniform(0, math.tau)
            rr = math.sqrt(random.random())          # fill the lobe disc
            px = x + lox + math.cos(a) * lrad * rr
            py = y + loy + math.sin(a) * lrad * rr
            vx = random.uniform(-14, 14)
            vy = random.uniform(-20, 6)
            life = random.uniform(0.50, 1.00)
            size = random.choice((3, 3, 4, 4))
            self.particles.append(
                PoofGrain(px, py, vx, vy, life, size, random.choice(palette)))

    def _spawn_genie_reveal_poof(self, x, y):
        """Poof when a Genie offer materialises — the same magic dust as
        every other genie beat so appear and vanish read as one effect."""
        self._spawn_grainy_poof(x, y)

    def _activate_skateboard(self, m):
        from game.skateboard_fx import (
            render_caption_overlay, render_starburst_surface,
        )
        self.skateboard_timer = SKATEBOARD_DURATION
        self.bird.skateboard_active = True
        self.shake_mag = max(self.shake_mag, 4.0)
        self.shake_t = max(self.shake_t, 0.3)
        audio.play_skateboard()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(
            m, ((60, 60, 70), (180, 180, 190), UI_ORANGE, UI_GOLD), n=28)
        seed = int(self._idle_t * 1000) & 0xFFFF
        self.skateboard_caption_dur = SKATEBOARD_DURATION
        self.skateboard_caption_t = self.skateboard_caption_dur
        self.skateboard_caption_overlay = render_caption_overlay(
            int(self.bird.x), int(self.bird.y), rng_seed=seed,
        )
        self.skateboard_burst_dur = 2.3
        self.skateboard_burst_t = self.skateboard_burst_dur
        self.skateboard_burst_surface = render_starburst_surface(
            rng_seed=seed,
        )
        self.skateboard_burst_cx = int(self.bird.x)
        self.skateboard_burst_cy = int(self.bird.y)

    def _activate_knight(self, m):
        KNIGHT_STEEL = (190, 200, 220)
        KNIGHT_GOLD  = (226, 182,  72)
        self.knight_timer = KNIGHT_DURATION
        self.bird.knight_active = True
        self.shake_mag = max(self.shake_mag, 3.5)
        self.shake_t   = max(self.shake_t,   0.3)
        audio.play_knight()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(m, (KNIGHT_STEEL, KNIGHT_GOLD, WHITE, UI_CREAM),
                           n=32, speed_hi=320)
        self.float_texts.append(FloatText(
            "KNIGHT!", m.x, m.y - 26, KNIGHT_GOLD,
            size=30, life=1.4, vy=-32, style="powerup",
        ))

    def _revive_knight(self):
        """Survive-one-hit revive: re-flap up, grant a grace window, and fire
        a steel-and-brass spark burst + GUARD! text."""
        self.knight_invuln = KNIGHT_INVULN
        self.bird.vy = FLAP_V * 0.9
        self.shake_mag = max(self.shake_mag, 6.0)
        self.shake_t   = max(self.shake_t,   0.3)
        audio.play_ghost()
        audio.play_thunder()
        for _ in range(36):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(160, 420)
            col = random.choice((
                (210, 218, 236), (146, 156, 178),
                (226, 182,  72), WHITE,
            ))
            self.particles.append(Particle(
                self.bird.x, self.bird.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.5, 1.2),
                random.randint(3, 6),
                col, gravity=180,
            ))
        self.float_texts.append(FloatText(
            "GUARD!", self.bird.x, self.bird.y - 32, (226, 182, 72),
            size=30, life=1.4, vy=-36, style="powerup",
        ))

    def _activate_genie(self, m):
        """Genie Lamp — instead of a direct buff, summon a conjurer who lays
        out a fixed offer: knight (survive one hit), poison (trap, kills at
        t = 1.0), skateboard (rail buff). Genie is the ONLY path to these
        three kinds; the slot order shuffles so the trap can't be memorised
        by position."""
        chosen = ["knight", "poison", "skateboard"]
        slots = list(GENIE_OFFER_Y_SLOTS[:GENIE_OFFER_COUNT])
        random.shuffle(slots)
        gy = 225
        gx = 180
        offers = list(zip(chosen, slots))
        self.genie_actors.append(GenieCharacter(
            gx, gy, vx=0.0, offers=offers, world=self,
        ))
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

    def _activate_poison(self, m):
        """Poison trap (genie-only). Starts Bird.poison_t at 0; Bird.update
        ramps it toward 1.0 over POISON_DURATION seconds; World.update
        watches for the terminal 1.0 and fires _die(). Knight saves the
        bird AND clears the poison state — only escape path."""
        self.bird.poison_active = True
        self.bird.poison_t = 0.0
        self.shake_mag = max(self.shake_mag, 2.5)
        self.shake_t   = max(self.shake_t, 0.25)
        try:
            audio.play_death()
        except Exception:
            pass
        self._pickup_burst(
            m, ((120, 200, 90), (200, 224, 96), (60, 100, 50), WHITE),
            n=20, speed_hi=240,
        )
        self.float_texts.append(FloatText(
            "POISONED!", m.x, m.y - 26, (200, 224, 96),
            size=28, life=1.4, vy=-30, style="powerup",
        ))

    def _cull_genie_offers_except(self, chosen: "PowerUp"):
        """Mark every other genie offer collected (so the normal sweep removes
        it next frame) and poof a cloud where each unchosen wish stood, then
        kill any active GenieCharacter so it stops casting."""
        for p in self.powerups:
            if p is chosen or not getattr(p, "is_genie_offer", False):
                continue
            p.collected = True
            self._spawn_grainy_poof(p.x, p.y)
        for g in self.genie_actors:
            g.kill()

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

    def _activate_shrink(self, m):
        SHRINK_HI  = (80, 180, 240)
        SHRINK_OUT = (30, 90, 160)
        self.shrink_timer = SHRINK_DURATION
        self.bird.shrink_active = True
        self.shake_mag = max(self.shake_mag, 3.0)
        self.shake_t = max(self.shake_t, 0.25)
        audio.play_shrink()
        audio.play_poof()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(m, (SHRINK_HI, SHRINK_OUT, WHITE, UI_CREAM),
                           n=30, speed_hi=280)
        self.float_texts.append(FloatText(
            "SHRINK!", m.x, m.y - 26, SHRINK_HI,
            size=30, life=1.3, vy=-30, style="powerup",
        ))

    def _activate_rail(self, m):
        """RAIL TRACK — pillar-limited buff. Tags the next 5 pillars
        ahead with rail track and parks a stationary cart on the FIRST
        of them. Pip is NOT auto-locked: he keeps flying with normal
        flap. If he touches the cart pillar the cart locks him in and
        rides through the remaining tagged pillars. Pillars 2-5 still
        have track but no cart — touching them kills Pip like any
        obstacle. If picked up WHILE Pip is already locked on the rail
        (he can't dodge), extend the current ride by 5 more pillars."""
        if self.bird.cart_locked:
            self._extend_rail_ride(m)
            return
        self.rail_pillars_left = RAIL_PILLAR_COUNT
        self.bird.cart_active = True
        self.bird.cart_locked = False
        self.rail_pending = 0
        for p in self.pipes:
            p.rail_active = False
        ahead = sorted(
            (p for p in self.pipes
             if p.x > self.bird.x and not getattr(p, "is_rush", False)),
            key=lambda p: p.x)
        for p in ahead[:RAIL_PILLAR_COUNT]:
            p.rail_active = True
        tagged_ahead = min(len(ahead), RAIL_PILLAR_COUNT)
        need = RAIL_PILLAR_COUNT - tagged_ahead
        if need > 0:
            self.rail_pending = need
            spacing = self._current_spacing()
            next_x = (max((p.x for p in self.pipes), default=self.bird.x)
                      + spacing)
            guard = need * 3
            while self.rail_pending > 0 and guard > 0:
                self._spawn_pipe(next_x)
                next_x += spacing
                guard -= 1
            self.rail_pending = 0
        self.rail_pipes = [p for p in self.pipes if p.rail_active]
        self.rail_cart_pipe = (sorted(self.rail_pipes, key=lambda p: p.x)[0]
                               if self.rail_pipes else None)
        audio.play_rail()
        self._pickup_burst(m, (UI_GOLD, UI_ORANGE, (255, 220, 100), WHITE), n=28)
        self.float_texts.append(FloatText(
            "RAILS UP!", m.x, m.y - 26, UI_GOLD,
            size=28, life=1.3, vy=-30, style="powerup",
        ))

    def _extend_rail_ride(self, m):
        """Mid-ride pickup: extend the current locked ride by tagging
        more pillars ahead so there are RAIL_PILLAR_COUNT tagged in
        front of Pip, then reset the per-ride budget."""
        ahead = sorted(
            (p for p in self.pipes
             if p.x > self.bird.x and not getattr(p, "is_rush", False)),
            key=lambda p: p.x)
        tagged_ahead = sum(1 for p in ahead
                           if getattr(p, "rail_active", False))
        for p in ahead:
            if tagged_ahead >= RAIL_PILLAR_COUNT:
                break
            if not getattr(p, "rail_active", False):
                p.rail_active = True
                tagged_ahead += 1
        need = RAIL_PILLAR_COUNT - tagged_ahead
        if need > 0:
            self.rail_pending = need
            spacing = self._current_spacing()
            next_x = (max((p.x for p in self.pipes), default=self.bird.x)
                      + spacing)
            guard = need * 3
            while self.rail_pending > 0 and guard > 0:
                self._spawn_pipe(next_x)
                next_x += spacing
                guard -= 1
            self.rail_pending = 0
        self.rail_pipes = [p for p in self.pipes if p.rail_active]
        self.rail_pillars_left = RAIL_PILLAR_COUNT
        audio.play_rail()
        self._pickup_burst(m, (UI_GOLD, UI_ORANGE, (255, 220, 100), WHITE), n=18)
        self.float_texts.append(FloatText(
            "+5 RAILS", m.x, m.y - 26, UI_GOLD,
            size=26, life=1.2, vy=-30, style="powerup",
        ))

    # Pip's centre-y when the cart is locked on the rail — chosen so
    # the wagon body sits with its wheels exactly on the rail line.
    _CART_LOCKED_OFFSET = 32

    # Parked-cart hitbox — bounds match the visual painted by
    # scenes._draw_parked_cart so what the player sees as "the cart"
    # is exactly what triggers the lock.
    _CART_HALF_W = 22
    _CART_TOP_OFF = 28
    _CART_BOT_OFF = 5

    def _circle_hits_cart(self, pipe, cx, cy, r):
        """True if the circle at (cx, cy) with radius r overlaps the
        parked-cart rect sitting on `pipe`. The cart lives inside the
        pillar's gap, so touching the pillar BODY of the same pipe
        returns False and falls through to normal pipe collision."""
        cart_cx = pipe.x + PIPE_W // 2
        rail_y = pipe.gap_y + pipe.gap_h / 2
        left = cart_cx - self._CART_HALF_W
        right = cart_cx + self._CART_HALF_W
        top = rail_y - self._CART_TOP_OFF
        bot = rail_y - self._CART_BOT_OFF
        nx = max(left, min(cx, right))
        ny = max(top, min(cy, bot))
        return (cx - nx) ** 2 + (cy - ny) ** 2 <= r * r

    def _lock_pip_on_cart(self):
        """Touched the parked cart — flip into locked-ride mode. Snaps
        Pip onto the rail at the cart pillar's gap-center."""
        self.bird.cart_locked = True
        self._snap_cart_to_rail(self.bird.x)
        self.shake_mag = max(self.shake_mag, 3.0)
        self.shake_t = max(self.shake_t, 0.2)
        audio.play_rail()

    def _snap_cart_to_rail(self, bx):
        """Snap bird.y so the wagon wheels ride the current rail
        segment, interpolating across the bridge between two
        consecutive rail pipes. Also writes the local rail slope to
        bird.cart_tilt_deg so the cart sprite rotates with the curve."""
        sorted_pipes = sorted(self.rail_pipes, key=lambda p: p.x)
        offset = self._CART_LOCKED_OFFSET

        for i, p in enumerate(sorted_pipes):
            if p.x - 6 <= bx <= p.x + PIPE_W + 6:
                rail_y = p.gap_y + p.gap_h / 2
                self.bird.y = rail_y - offset
                self.bird.vy = 0.0
                if i + 1 < len(sorted_pipes):
                    nxt = sorted_pipes[i + 1]
                    self.bird.cart_tilt_deg = self._rail_slope_deg(
                        p.x + PIPE_W, rail_y,
                        nxt.x, nxt.gap_y + nxt.gap_h / 2)
                else:
                    self.bird.cart_tilt_deg = 0.0
                return

        for i in range(len(sorted_pipes) - 1):
            p1, p2 = sorted_pipes[i], sorted_pipes[i + 1]
            if p1.x + PIPE_W <= bx <= p2.x:
                span = max(1, p2.x - (p1.x + PIPE_W))
                t = (bx - (p1.x + PIPE_W)) / span
                y1 = p1.gap_y + p1.gap_h / 2
                y2 = p2.gap_y + p2.gap_h / 2
                self.bird.y = (y1 + (y2 - y1) * t) - offset
                self.bird.vy = 0.0
                self.bird.cart_tilt_deg = self._rail_slope_deg(
                    p1.x + PIPE_W, y1, p2.x, y2)
                return

    @staticmethod
    def _rail_slope_deg(x1: float, y1: float,
                        x2: float, y2: float) -> float:
        """Tilt (degrees, pygame convention) for a rail segment.
        NEGATIVE = downhill-right → nose down; POSITIVE = uphill-right
        → nose up. Capped at ±45° so a wildly steep bridge doesn't
        flip the cart upside-down."""
        dx = x2 - x1
        if dx <= 0.5:
            return 0.0
        dy = y2 - y1
        deg = -math.degrees(math.atan2(dy, dx))
        return max(-45.0, min(45.0, deg))

    def _end_rail_ride(self):
        """End the rail powerup. If Pip rode the cart, release with an
        upward "jump" so the player gets air control on the same
        frame. If he never landed on the cart, clean up silently.
        Existing rail_active flags on already-tagged pipes are NOT
        cleared — the on-screen tail of track scrolls off naturally."""
        was_locked = self.bird.cart_locked
        self.bird.cart_active = False
        self.bird.cart_locked = False
        self.bird.cart_tilt_deg = 0.0
        self.rail_cart_pipe = None
        if was_locked:
            sign = -1 if self.reverse_timer > 0 else 1
            self.bird.vy = FLAP_V * sign
            self.bird.flap_boost = 0.45
            audio.play_flap()

    def _apply_lottery_result(self):
        anim = self.lottery_anim
        if anim is None:
            return
        delta = anim["delta"]
        tier = anim["tier"]
        # Score delta clamps at 0 — total coins never go negative.
        # coin_count is NOT touched (plausibility requires coin_count
        # == len(coin events)); deltas record as a "lottery" event.
        if delta > 0:
            self.score += delta
            self._proof.record(self.time_alive, delta, "lottery")
            color = UI_GOLD if delta >= 40 else UI_ORANGE
            audio.play_lottery_win()
        elif delta < 0:
            actual = -min(self.score, -delta)
            self.score += actual
            if actual != 0:
                self._proof.record(self.time_alive, actual, "lottery")
            color = (220, 70, 60)
            audio.play_lottery_bust()
        else:
            color = (200, 200, 200)
        sign = "+" if delta > 0 else ""
        label = f"{tier}! {sign}{delta}" if delta != 0 else f"{tier}!"
        self.float_texts.append(FloatText(
            label, self.bird.x, self.bird.y - 40, color,
            size=28, life=1.4, vy=-30, style="powerup",
        ))
        if delta >= 100:
            self._pickup_burst(self.bird,
                               (UI_GOLD, UI_ORANGE, UI_CREAM, WHITE),
                               n=40, speed_hi=380)
        elif delta >= 15:
            self._pickup_burst(self.bird, (UI_GOLD, UI_CREAM, WHITE), n=20)
        elif delta < 0:
            self._pickup_burst(self.bird,
                               ((220, 70, 60), (140, 30, 30), (80, 80, 80)),
                               n=18)

    def _activate_lottery(self, m):
        # Roll the tier immediately; the reveal animation delays the
        # score change for showmanship.
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

    # ── utility ──────────────────────────────────────────────────────────────

    def shake_offset(self):
        if self.shake_t <= 0 or self.shake_mag <= 0:
            return 0, 0
        amp = self.shake_mag * (self.shake_t / 0.45)
        return (random.uniform(-amp, amp), random.uniform(-amp, amp))
