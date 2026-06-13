"""Branch-only scripted prototype of the Pagoda-Warren beat:

    empty sky → a clown walks on with a floating dice power-up → the player
    grabs the die (rolls N = 10..25) → after a beat, a warren route of N fused
    pagodas scrolls in with N on a sign hung from the first pillar → the player
    flies the route → a couple of seconds later Pip falls to its death.

This is a feel-test harness, NOT shipped gameplay: there is no event trigger,
no gating, no DB write. It only runs when `App` decides to launch it (native,
this R&D branch). The clown, die, and route shapes are the already-approved
look-dev designs, reused verbatim by lazily importing the `tools/` renderers
the first time the demo is constructed — after the display exists, and never on
web (where `tools/` isn't even bundled). Every reuse point is wrapped so a
missing/renamed helper degrades to a plain fallback instead of crashing a run.
"""
import math
import random

import pygame

from game.config import W, GROUND_Y, BIRD_X, BIRD_R, PIPE_W
from game.entities import Pipe
from game import draw as gfx

# ── script timing (seconds) ──────────────────────────────────────────────────
T_CLOWN_IN = 3.0          # empty-sky flight before the clown arrives
T_SPIN = 0.9              # dice tumble before the rolled number is revealed
T_AFTER_PICKUP = 2.0      # beat between the reveal and the route
CELE_LIFE = 1.5           # result celebration banner life (< T_AFTER_PICKUP)
T_AFTER_ROUTE = 2.0       # free flight after the route before Pip drops

# ── warren geometry ──────────────────────────────────────────────────────────
SP = 72                   # fused centre-to-centre spacing (warren window 62-84)
SPAWN_X = W + 40          # where each route pillar enters from the right
ROUTE_SEED = 0            # one pagoda family for the whole route (stupa canopy)
ROUTE_GAP = 172           # per-pillar gap height (inside the 150-185 window)

# ── clown / die placement ────────────────────────────────────────────────────
DICE_DX = 70              # die floats this far LEFT of the clown
DICE_Y = 330              # die height — comfortably reachable mid-flight
DICE_PICK_R = 30          # generous pickup radius around the die

# Local coords for the cached clown bitmap (its shape never changes — only its
# scroll position does — so it's rendered once and blitted each frame).
CLOWN_W, CLOWN_H = 200, 300
CLOWN_CX, CLOWN_FEET = 100, 250


class WarrenDemo:
    def __init__(self):
        # Lazy reuse of the look-dev kit. Constructed only when the demo runs,
        # so this import happens after the real display is up (the modules'
        # SDL_VIDEODRIVER=dummy setdefault is then a no-op) and never on web.
        from tools.render_jester_variants import (
            build_jester, _draw_die_face_noshadow, JESTERS,
        )
        from tools.render_warren_routes import Route
        from tools.render_warren_mockup import assert_passable

        self._build_jester = build_jester
        self._draw_die_face = _draw_die_face_noshadow
        self._Route = Route
        self._assert_passable = assert_passable
        # Hero clown #13 ("Plum & Lime — FINAL"); `no_shadow` is a render_cell
        # flag, not a build_jester kwarg, so drop it (we draw our own shadow).
        spec = dict(JESTERS[-1][1])
        spec.pop("no_shadow", None)
        self.spec = spec

        self.phase = "fly_in"
        self.t = 0.0               # global elapsed
        self.pt = 0.0              # current-phase timer
        self.pulse = 0.0           # die bob/sparkle clock
        self.input_locked = False

        self.clown_x = None        # world x of the clown's feet (None until in)
        self.dice_x = None
        self.dice_y = DICE_Y
        self.collected = False
        self.roll = None
        self.ghost_run = False     # GHOST outcome: phase through the whole route
        self.spin_t = 0.0          # dice tumble clock (phase "rolling")
        self._spin_face = 15       # number shown on the tumbling cube
        self._spin_face_t = 0.0    # countdown to the next tumble face
        self.die_pop_t = 0.0       # celebration-banner life after the reveal

        self.route = None          # list of (gap_cy, gap_h) for N pillars
        self.route_pipes = []      # Pipes we spawned, in order
        self.spawned = 0
        self.sign_pipe = None      # first route pillar (carries the N sign)

        self._clown_surf = None    # cached clown bitmap (built on first draw)
        self._clown_ok = True      # cleared if build_jester ever throws
        self._sign_font = None     # cached sign font

    # ── public hooks ─────────────────────────────────────────────────────────
    def gates_flap(self):
        """True once Pip's input is cut (the final scripted fall)."""
        return self.input_locked

    def update(self, world, dt):
        self.t += dt
        self.pt += dt
        self.pulse += dt * 3.5
        if self.die_pop_t > 0.0:
            self.die_pop_t = max(0.0, self.die_pop_t - dt)   # celebration life

        # The clown + die are world-anchored scenery in a static pose: once they
        # enter (a few seconds in) they ride the world scroll leftward and slide
        # off the left edge — they never walk or hold position on screen. The die
        # rides at the clown's hand until it's grabbed.
        if self.clown_x is not None:
            self.clown_x -= world._current_scroll() * dt
            if not self.collected:
                self.dice_x = self.clown_x - DICE_DX
            if self.clown_x < -160:
                self.clown_x = None

        if self.phase == "fly_in":
            if self.t >= T_CLOWN_IN:
                self.clown_x = float(SPAWN_X)          # enters from the right...
                self.dice_x = self.clown_x - DICE_DX   # ...and scrolls with the world
                self._goto("offer")

        elif self.phase == "offer":
            # grab on contact, or auto-grab once the die has scrolled past Pip
            if self._dice_hit(world) or self.dice_x < BIRD_X - 60:
                self._collect(world)
                self._goto("rolling")

        elif self.phase == "rolling":
            # the cube tumbles in place; the displayed face flickers, settling
            # onto the real roll for the last stretch, then the number reveals.
            self.spin_t += dt
            if self.spin_t >= T_SPIN - 0.18:
                self._spin_face = self.roll
            else:
                self._spin_face_t -= dt
                if self._spin_face_t <= 0.0:
                    self._spin_face = random.randint(10, 25)
                    self._spin_face_t = 0.06
            if self.spin_t >= T_SPIN:
                self._reveal_roll(world)
                self._goto("wait_route")

        elif self.phase == "wait_route":
            # the result celebration is up; the clown keeps scrolling off-screen
            if self.pt >= T_AFTER_PICKUP:
                self._make_route(world)
                if self.ghost_run:
                    world.ghost_timer = max(world.ghost_timer, 2.0)  # ghost on from route start
                self._goto("running")

        elif self.phase == "running":
            # feed pillars in from the right at the fused spacing
            while (self.spawned < len(self.route)
                   and (not self.route_pipes
                        or self.route_pipes[-1].x <= SPAWN_X - SP)):
                self._spawn_next(world)
            # GHOST roll: phase through the whole route. World decays ghost_timer
            # each frame, so keep it topped up while flying the route.
            if self.ghost_run:
                world.ghost_timer = max(world.ghost_timer, 2.0)
            # route done once the last pillar has slipped past Pip
            if (self.spawned >= len(self.route) and self.route_pipes
                    and self.route_pipes[-1].x + PIPE_W < BIRD_X):
                if self.ghost_run:
                    world.ghost_timer = 1.0   # ... then stay a ghost one more second
                self._goto("post_route")

        elif self.phase == "post_route":
            if self.pt >= T_AFTER_ROUTE:
                self.input_locked = True        # let gravity carry Pip down
                self._goto("falling")

        # "falling": nothing to drive — the normal ground collision ends the run.

    def draw_world(self, surf, world, sx, sy):
        """Clown + floating die — drawn BEFORE the pillars so the route occludes
        the strolling clown the way the celebration crowd is layered."""
        if self.clown_x is not None and self.clown_x > -140:
            cx = int(self.clown_x + sx)
            fy = int(GROUND_Y + sy)
            shadow = pygame.Surface((84, 14), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, 84, 14))
            surf.blit(shadow, (cx - 42, fy - 6))
            cs = self._clown_surface()
            if cs is not None:
                surf.blit(cs, (cx - CLOWN_CX, fy - CLOWN_FEET))
            else:
                pygame.draw.circle(surf, (150, 90, 200), (cx, fy - 80), 36)

        if self.dice_x is not None:
            dx = int(self.dice_x + sx)
            if not self.collected:                       # floating, pre-grab
                self._draw_floating_die(surf, dx, int(self.dice_y + sy))
            elif self.phase == "rolling":                # tumbling roll
                self._draw_spinning_die(surf, dx, int(self.dice_y + sy))
            # The settled result is NOT painted on the cube — it pops as a
            # celebration banner in a fixed spot (see _draw_celebration).

    def draw_sign(self, surf, world, sx, sy):
        """The N-of-pillars sign hung from the first route pagoda — drawn AFTER
        the pillars so it reads in front of the pagoda tops. Also hosts the
        result celebration banner (drawn here so it layers over the route)."""
        self._draw_celebration(surf)               # fixed-spot popup; self-gated
        p = self.sign_pipe
        if p is None or self.roll is None:
            return
        if p.x + PIPE_W < 0 or p.x > W + 40:        # bail once fully off either edge
            return
        cx = int(p.x + PIPE_W / 2 + sx)
        top = int(p.gap_y - p.gap_h / 2 + sy)     # gap rim under the top pagoda
        txt = str(self.roll)
        if self._sign_font is None:
            self._sign_font = pygame.font.SysFont(None, 34, bold=True)
        label = self._sign_font.render(txt, True, (60, 40, 20))
        pw = label.get_width() + 22
        ph = label.get_height() + 14
        bx, by = cx - pw // 2, top + 8
        # two short ropes from the rim down to the plaque
        for rx in (bx + 8, bx + pw - 8):
            pygame.draw.line(surf, (120, 86, 48), (rx, top), (rx, by + 2), 3)
        gfx.blit_glow(surf, cx, by + ph // 2, int(pw * 0.7), (255, 214, 110), alpha=120)
        gfx.rounded_rect(surf, (bx, by, pw, ph), 7, (244, 210, 130))
        pygame.draw.rect(surf, (150, 104, 48), (bx, by, pw, ph), 2, border_radius=7)
        surf.blit(label, (cx - label.get_width() // 2, by + 7))

    # ── internals ────────────────────────────────────────────────────────────
    def _clown_surface(self):
        """Render the clown once into a local bitmap (its shape is constant —
        only its scroll position changes) and reuse it each frame instead of
        re-running build_jester (which rotates a scratch surface) per frame."""
        if self._clown_surf is None and self._clown_ok:
            try:
                s = pygame.Surface((CLOWN_W, CLOWN_H), pygame.SRCALPHA)
                # Same raised-arm reach as the chosen design (#13): the left
                # hand points up-left toward the floating die — (cx-60, feet-154)
                # mirrors render_cell's hand_up so the arm isn't stubby.
                hand_up = (CLOWN_CX - 60, CLOWN_FEET - 154)
                self._build_jester(s, CLOWN_CX, CLOWN_FEET, hand_up, **self.spec)
                self._clown_surf = s
            except Exception:
                self._clown_ok = False
        return self._clown_surf

    def _draw_floating_die(self, surf, dx, dy):
        """The pre-grab die: a clean bobbing 3D cube with a few orbiting
        sparkles — NO glow/aura halo (it washed white on the pale sky)."""
        cy = int(dy + math.sin(self.pulse * 1.1) * 3)
        try:
            self._draw_die_face(surf, dx, cy, 40, pips=5)
        except Exception:
            pygame.draw.rect(surf, (250, 246, 230), (dx - 16, cy - 16, 32, 32))
            return
        for i in range(4):
            a = i * math.tau / 4 + self.pulse * 0.4
            rr = 30 + 4 * math.sin(self.pulse * 0.9 + i)
            sxp = int(dx + math.cos(a) * rr)
            syp = int(cy + math.sin(a) * rr * 0.85)
            tw = 0.5 + 0.5 * math.sin(self.pulse * 2.0 + i * 1.7)
            al = int(110 + 130 * tw)
            sz = 3 + int(2 * tw)
            spark = pygame.Surface((sz * 4, sz * 4), pygame.SRCALPHA)
            c = (255, 244, 200, al)
            pygame.draw.line(spark, c, (sz * 2, 0), (sz * 2, sz * 4), 1)
            pygame.draw.line(spark, c, (0, sz * 2), (sz * 4, sz * 2), 1)
            pygame.draw.circle(spark, (255, 255, 230, al), (sz * 2, sz * 2), sz)
            surf.blit(spark, (sxp - sz * 2, syp - sz * 2),
                      special_flags=pygame.BLEND_ADD)

    def _draw_celebration(self, surf):
        """The settled roll, popped as a celebration in a fixed on-screen spot
        (not painted on the cube). Its own festive look — a spinning sunburst
        rosette, confetti, and a big number + label in the game's own font —
        deliberately NOT the clown's motif. A GHOST result reads spooky (cyan +
        ectoplasm wisps) so its 10 never looks like a plain 10.

        Composited on a SS× supersampled canvas and smooth-scaled down each
        frame (the HUD's trick) so every edge stays crisp at any pop scale."""
        if self.roll is None or self.die_pop_t <= 0.0:
            return
        from game import hud                       # vendored bold TTF + cache
        ghost = self.ghost_run
        cx, cy = W // 2, 152
        age = max(0.0, CELE_LIFE - self.die_pop_t)        # secs since the reveal

        # ease-out-back pop-in (slight overshoot), then hold at full size
        p = min(1.0, age / 0.34)
        s = 1.70158
        pop = 1 + (s + 1) * (p - 1) ** 3 + s * (p - 1) ** 2
        scale = 0.45 + 0.55 * pop
        burst = min(1.0, age / 0.5)

        if ghost:
            rose = [(86, 210, 204), (140, 150, 240)]
            num_col, num_edge = (228, 252, 250), (16, 74, 92)
            label_txt, label_col = "GHOST!", (158, 242, 228)
            conf = [(150, 240, 226), (118, 200, 255), (206, 255, 248), (172, 172, 255)]
        else:
            rose = [(255, 178, 60), (255, 120, 138)]
            num_col, num_edge = (255, 224, 118), (122, 62, 14)
            label_txt, label_col = "PILLARS", (255, 240, 196)
            conf = [(255, 208, 88), (255, 118, 150), (118, 200, 255), (172, 255, 150)]

        SS = 3
        D = 264                                    # design size in final px
        HD = D * SS
        c = HD // 2
        canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

        # spinning sunburst rosette — 24 tapered wedges, normal-blended so it
        # stays a festive colour wheel (additive would blow out white on sky)
        rays = 24
        spin = self.pulse * 0.4
        step = math.tau / rays
        Rr = int(HD * 0.30 * (0.7 + 0.3 * burst))
        for i in range(rays):
            a0 = spin + i * step
            a1 = a0 + step * 0.9
            am = (a0 + a1) * 0.5
            col = rose[i % 2] + (66,)
            pygame.draw.polygon(canvas, col, [
                (c, c),
                (c + math.cos(a0) * Rr, c + math.sin(a0) * Rr),
                (c + math.cos(am) * Rr * 1.05, c + math.sin(am) * Rr * 1.05),
                (c + math.cos(a1) * Rr, c + math.sin(a1) * Rr)])
        # a soft colour hub seats the number (low-alpha disc, not white)
        hub = pygame.Surface((HD, HD), pygame.SRCALPHA)
        pygame.draw.circle(hub, rose[1] + (54,), (c, c), int(HD * 0.18))
        canvas.blit(hub, (0, 0))

        # confetti diamonds spraying out, tumbling
        for i in range(18):
            a = (i / 18) * math.tau + (0.2 if ghost else 0.0) + spin * 0.25
            dist = HD * 0.20 + burst * HD * 0.20 + (i % 3) * 9 * SS
            px = c + math.cos(a) * dist
            py = c + math.sin(a) * dist * 0.86
            al = int(235 * (1.0 - burst * 0.55))
            if al <= 0:
                continue
            sz = (5 + (i % 3) * 2) * SS
            d = pygame.Surface((sz, sz), pygame.SRCALPHA)
            pygame.draw.polygon(d, conf[i % 4] + (al,),
                                [(sz // 2, 0), (sz, sz // 2), (sz // 2, sz), (0, sz // 2)])
            d = pygame.transform.rotate(d, (i * 53 + age * 200) % 360)
            canvas.blit(d, (int(px - d.get_width() / 2), int(py - d.get_height() / 2)))

        # ghost: rising ectoplasm wisps behind the number
        if ghost:
            for i in range(4):
                climb = (self.pulse * 16 + i * 11) % 46
                wx = int(c - 42 * SS + i * 28 * SS + math.sin(self.pulse * 1.3 + i) * 7 * SS)
                wy = int(c + 30 * SS - climb * SS)
                al = max(0, 150 - int(climb * 3))
                if al <= 0:
                    continue
                pygame.draw.circle(canvas, (200, 255, 246, al), (wx, wy), 4 * SS)

        # number — vendored bold font, drop shadow + thick edge for pop
        nf = hud._font(int(70 * SS), True)
        num = nf.render(str(self.roll), True, num_col)
        edge = nf.render(str(self.roll), True, num_edge)
        shadow = nf.render(str(self.roll), True, (0, 0, 0))
        shadow.set_alpha(95)
        ncy = c - int(8 * SS)
        canvas.blit(shadow, shadow.get_rect(center=(c + 3 * SS, ncy + 4 * SS)))
        o = 3 * SS
        for ox, oy in ((-o, 0), (o, 0), (0, -o), (0, o),
                       (-o, -o), (o, -o), (-o, o), (o, o)):
            canvas.blit(edge, edge.get_rect(center=(c + ox, ncy + oy)))
        nb = num.get_rect(center=(c, ncy))
        canvas.blit(num, nb)

        # label under the number — same edge colour, tracked out a little
        lf = hud._font(int(26 * SS), True)
        spaced = " ".join(label_txt)
        lab = lf.render(spaced, True, label_col)
        labedge = lf.render(spaced, True, num_edge)
        lcy = nb.bottom + int(16 * SS)
        for ox, oy in ((-SS, 0), (SS, 0), (0, -SS), (0, SS)):
            canvas.blit(labedge, labedge.get_rect(center=(c + ox, lcy + oy)))
        canvas.blit(lab, lab.get_rect(center=(c, lcy)))

        out = pygame.transform.smoothscale(canvas, (int(D * scale), int(D * scale)))
        surf.blit(out, out.get_rect(center=(cx, cy)))

    def _draw_spinning_die(self, surf, dx, dy):
        """A short cube tumble before the reveal: the die spun by an ease-out
        angle (settling upright) with its face flickering through numbers, so
        it reads as a real dice roll. No glow/aura (kept off, per the clean look)."""
        u = min(1.0, self.spin_t / T_SPIN)
        try:
            sc = pygame.Surface((96, 96), pygame.SRCALPHA)
            self._draw_die_face(sc, 48, 48, 40, number=self._spin_face,
                                body=(255, 246, 224), pip_col=(190, 70, 40))
            deg = 360.0 * 3 * (1.0 - (1.0 - u) ** 2)   # 3 turns, decelerate to upright
            rot = pygame.transform.rotate(sc, deg)
            surf.blit(rot, (dx - rot.get_width() // 2, dy - rot.get_height() // 2))
        except Exception:
            pygame.draw.rect(surf, (250, 246, 230), (dx - 16, dy - 16, 32, 32))

    def _goto(self, phase):
        self.phase = phase
        self.pt = 0.0

    def _dice_hit(self, world):
        b = world.bird
        ddx = self.dice_x - b.x
        ddy = self.dice_y - b.y
        return ddx * ddx + ddy * ddy <= (DICE_PICK_R + BIRD_R) ** 2

    def _collect(self, world):
        # Grab → the cube tumbles (phase "rolling"); the number is revealed
        # only once the spin settles (see _reveal_roll). One extra slot in the
        # roll pool is GHOST: the die lands on the range minimum and Pip phases
        # through the whole route (applied in the "running" phase).
        self.collected = True
        pick = random.choice(list(range(10, 26)) + ["ghost"])
        self.ghost_run = pick == "ghost"
        self.roll = 10 if self.ghost_run else pick
        self.spin_t = 0.0
        self._spin_face = random.randint(10, 25)
        self._spin_face_t = 0.06

    def _reveal_roll(self, world):
        # Spin done — arm the celebration banner (drawn in a fixed spot, not on
        # the cube). die_pop_t is its life clock; _draw_celebration reads it.
        self.die_pop_t = CELE_LIFE

    def _spawn_next(self, world):
        gap_cy, gap_h = self.route[self.spawned]
        p = Pipe(float(SPAWN_X), gap_cy, gap_h)
        p.seed = ROUTE_SEED
        p.spawn_index = self.spawned + 1          # >=1: keep ornaments (no quiet rule)
        p.is_rush = False
        p.is_kfc = False
        world.pipes.append(p)
        self.route_pipes.append(p)
        if self.spawned == 0:
            self.sign_pipe = p
        self.spawned += 1

    def _make_route(self, world):
        """Build EXACTLY N (=roll) passable pagodas of a random difficulty-1-5
        archetype; on any passability failure fall back to a flat tube."""
        n = self.roll
        archetype = random.choice([
            self._r_plunge, self._r_ascent, self._r_rolling,
            self._r_valley, self._r_crest,
        ])
        try:
            route = archetype(n)
            self._assert_passable(route.name, route.pagodas)
        except Exception:
            route = self._Route("Flat Tube", "fallback")
            route.hold("flat", n, 300, ROUTE_GAP)
        self.route = [(cy, gap_h) for (_x, cy, gap_h, _seed) in route.pagodas]
        self.spawned = 0
        self.route_pipes = []

    def _pads(self, n):
        pad = 2 if n >= 8 else 1
        return pad, pad

    def _r_plunge(self, n):               # d2 — the long gentle dip
        r = self._Route("Long Plunge", "ride the fall")
        h, t = self._pads(n); m = n - h - t
        r.hold("in", h, 210, ROUTE_GAP).ramp("plunge", 410, m, ROUTE_GAP) \
            .hold("out", t, r.cy, ROUTE_GAP)
        return r

    def _r_ascent(self, n):               # d3 — steady climb
        r = self._Route("The Ascent", "steady climb")
        h, t = self._pads(n); m = n - h - t
        r.hold("in", h, 410, ROUTE_GAP).ramp("climb", 210, m, ROUTE_GAP) \
            .hold("out", t, r.cy, ROUTE_GAP)
        return r

    def _r_rolling(self, n):              # d3 — smooth sine
        r = self._Route("Rolling Hills", "smooth alternation")
        h, t = self._pads(n); m = n - h - t
        r.hold("in", h, 300, ROUTE_GAP).sine("roll", 62, 10, m, ROUTE_GAP, base=300) \
            .hold("out", t, r.cy, ROUTE_GAP)
        return r

    def _r_valley(self, n):               # d4 — fall then climb (V)
        # Endpoints kept within 50px/pagoda even when each leg is only 3 long
        # (N=10), so the V stays inside the drift budget at every length.
        r = self._Route("The Valley", "fall to climb")
        h, t = self._pads(n); m = n - h - t
        m1 = m // 2; m2 = m - m1
        r.hold("in", h, 255, ROUTE_GAP).ramp("fall", 405, m1, ROUTE_GAP) \
            .ramp("climb", 255, m2, ROUTE_GAP).hold("out", t, r.cy, ROUTE_GAP)
        return r

    def _r_crest(self, n):                # d4 — climb then fall (hill)
        r = self._Route("The Crest", "apex management")
        h, t = self._pads(n); m = n - h - t
        m1 = m // 2; m2 = m - m1
        r.hold("in", h, 405, ROUTE_GAP).ramp("climb", 255, m1, ROUTE_GAP) \
            .ramp("fall", 405, m2, ROUTE_GAP).hold("out", t, r.cy, ROUTE_GAP)
        return r
