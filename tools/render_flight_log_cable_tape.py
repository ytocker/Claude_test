"""
Flight Log screen concept — `cable_tape`.

A knurled gold marker-tape drum pays out a linen cable tape that lies in
serpentine courses down the canvas and runs off the bottom edge: the day is
longer than the screen. Flown tape is over-printed with phase-coloured ink;
unflown tape stays bare stock carrying the phase names still ahead.

Renders a labelled review sheet (hero run + the two edge cases the layout rule
set has to survive + 2x construction crops) to docs/flight_log_screen/.
"""
import os
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame  # noqa: E402

pygame.display.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
OUT_DIR = os.path.join(ROOT, "docs", "flight_log_screen", "cable_tape")
os.makedirs(OUT_DIR, exist_ok=True)

_FONT_CACHE = {}


def font(px):
    f = _FONT_CACHE.get(px)
    if f is None:
        f = pygame.font.Font(FONT_PATH, px)
        _FONT_CACHE[px] = f
    return f


# ── canvas + supersampling ───────────────────────────────────────────────────
# The tape is rasterised by walking its centreline and stamping cross-sections,
# which has no native antialiasing; rendering the whole mock at 2x and
# smoothscaling down is what keeps the 1.2-degree course tilt from stairstepping.
CW, CH = 360, 640
SS = 2
DW, DH = CW * SS, CH * SS

BG = (8, 8, 20)
GOLD = (240, 192, 64)
SCARLET = (172, 40, 32)
PAPER = (238, 236, 229)
CHARCOAL = (34, 32, 38)
BRASS = (196, 152, 74)
BRASS_HI = (240, 208, 142)
BRASS_LO = (112, 80, 34)
VIOLET_WHITE = (226, 214, 255)
STEEL = (150, 154, 166)


# ── phase palette ────────────────────────────────────────────────────────────
# Colours are the game's biome keyframes verbatim; the phase positions come from
# the brief's PHASE_BOUNDARIES rather than this branch's stripped biome.py,
# which still carries the pre-remap boundary set.
PHASE_BOUNDARIES = [
    (0.000, "DAY"),
    (0.231, "GOLDEN HOUR"),
    (0.363, "SUNSET"),
    (0.513, "DUSK"),
    (0.644, "NIGHT"),
    (0.794, "PREDAWN"),
    (0.906, "SUNRISE"),
]

_SKY = [
    ((40, 110, 200), (90, 170, 230), (170, 220, 245)),   # DAY
    ((80, 120, 200), (220, 175, 140), (255, 210, 160)),  # GOLDEN HOUR
    ((90, 50, 130), (230, 95, 120), (255, 160, 90)),     # SUNSET
    ((25, 20, 70), (70, 45, 130), (170, 95, 140)),       # DUSK
    ((5, 8, 30), (15, 25, 70), (35, 55, 115)),           # NIGHT
    ((30, 30, 80), (70, 60, 140), (200, 130, 180)),      # PREDAWN
    ((50, 100, 180), (255, 150, 150), (255, 220, 170)),  # SUNRISE
]
_STOPS = [f for f, _ in PHASE_BOUNDARIES] + [1.0]
_SKY_W = _SKY + [_SKY[0]]

EVENT_MARKERS = [
    (0.15, "GEYSER"),
    (0.41, "CLOWN"),
    (0.44, "STORM"),
    (0.85, "SNOW"),
]


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_c(a, b, t):
    return (int(lerp(a[0], b[0], t)), int(lerp(a[1], b[1], t)), int(lerp(a[2], b[2], t)))


def sky_color_for_phase(f):
    """Three-stop sky column (top/mid/bot) for a day phase, smoothstepped."""
    f = f % 1.0
    for i in range(len(_STOPS) - 1):
        t0, t1 = _STOPS[i], _STOPS[i + 1]
        if t0 <= f <= t1:
            t = (f - t0) / (t1 - t0) if t1 > t0 else 0.0
            t = t * t * (3 - 2 * t)
            a, b = _SKY_W[i], _SKY_W[i + 1]
            return tuple(lerp_c(a[k], b[k], t) for k in range(3))
    return _SKY[0]


def phase_of_course(i):
    f0 = _STOPS[i]
    f1 = _STOPS[i + 1]
    return f0, f1


# ── tape geometry (canvas units) ─────────────────────────────────────────────
INSET = 24
PITCH = 52
TAPE_W = 28
N_COURSES = 7
ROW0_Y = 132
TILT_CAP = 1.2

HALF = TAPE_W / 2.0
# Ferrules and clamps are crimped *around* the tape, so they stand a little
# proud of both selvedges; the strip carries that margin as transparent pixels.
OVER = 4
STRIP_H = (TAPE_W + 2 * OVER) * SS
TAPE_V0 = OVER * SS
TAPE_V1 = (OVER + TAPE_W) * SS
STRIP_HALF = STRIP_H / 2.0

BEND_M = 78.0
DS = 0.25

_rng = random.Random(20260731)
_TILTS = [TILT_CAP * (1.0 if i % 2 == 0 else -1.0) * _rng.uniform(0.55, 1.0)
          for i in range(N_COURSES)]


def _course_ends(i):
    """Start/end point and unit direction of course i, with its hand-set tilt."""
    fold = HALF + BEND_M * 0.25
    x_l = INSET + fold
    x_r = CW - INSET - fold
    mid = ((x_l + x_r) * 0.5, ROW0_Y + i * PITCH)
    length = x_r - x_l
    a = math.radians(_TILTS[i])
    sgn = 1.0 if i % 2 == 0 else -1.0
    dx, dy = math.cos(a) * sgn, math.sin(a) * sgn
    p0 = (mid[0] - dx * length / 2, mid[1] - dy * length / 2)
    p1 = (mid[0] + dx * length / 2, mid[1] + dy * length / 2)
    return p0, p1, (dx, dy), length


class Path:
    """Arclength-resampled tape centreline with named marks in strip units."""

    def __init__(self):
        self._raw = []
        self.marks = {}
        self.pts = []
        self.tan = []

    def start(self, p):
        self._raw.append(p)

    def mark(self, key):
        self.marks[key] = len(self._raw) - 1

    def line(self, p1):
        p0 = self._raw[-1]
        n = max(2, int(math.dist(p0, p1) * 4))
        for i in range(1, n + 1):
            t = i / n
            self._raw.append((lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t)))

    def hermite(self, t0, p1, t1, n=90):
        p0 = self._raw[-1]
        for i in range(1, n + 1):
            s = i / n
            s2, s3 = s * s, s * s * s
            h00 = 2 * s3 - 3 * s2 + 1
            h10 = s3 - 2 * s2 + s
            h01 = -2 * s3 + 3 * s2
            h11 = s3 - s2
            self._raw.append((h00 * p0[0] + h10 * t0[0] + h01 * p1[0] + h11 * t1[0],
                              h00 * p0[1] + h10 * t0[1] + h01 * p1[1] + h11 * t1[1]))

    def resample(self):
        raw = self._raw
        cum = [0.0]
        for i in range(1, len(raw)):
            cum.append(cum[-1] + math.dist(raw[i - 1], raw[i]))
        total = cum[-1]
        self.total = total
        n = int(total / DS)
        j = 0
        for k in range(n + 1):
            s = k * DS
            while j < len(cum) - 2 and cum[j + 1] < s:
                j += 1
            span = cum[j + 1] - cum[j]
            t = (s - cum[j]) / span if span > 1e-9 else 0.0
            x = lerp(raw[j][0], raw[j + 1][0], t)
            y = lerp(raw[j][1], raw[j + 1][1], t)
            self.pts.append((x, y))
            dx = raw[j + 1][0] - raw[j][0]
            dy = raw[j + 1][1] - raw[j][1]
            d = math.hypot(dx, dy) or 1.0
            self.tan.append((dx / d, dy / d))
        # The path is sampled finer than the texture so the bends lay down
        # gap-free, but strip columns stay square with strip rows (SS px per
        # canvas unit on both axes) or the printing would come out squashed.
        self.marks = {k: int(cum[i] * SS) for k, i in self.marks.items()}
        self.n = len(self.pts)
        return self

    def index_for_u(self, u):
        return max(0, min(self.n - 1, int(u / (DS * SS))))

    def at(self, u):
        """Canvas-space point + unit tangent at strip column u."""
        i = self.index_for_u(u)
        return self.pts[i], self.tan[i]


def build_path():
    p = Path()
    c0, c0e, d0, _ = _course_ends(0)
    # The tape emerges from behind the drum body, so the lead-in starts inside it.
    p.start((38.0, 58.0))
    p.hermite((0.0, 70.0), c0, (d0[0] * 60, d0[1] * 60), 70)
    for i in range(N_COURSES):
        s, e, d, _ = _course_ends(i)
        p.mark(f"c{i}s")
        p.line(e)
        p.mark(f"c{i}e")
        if i < N_COURSES - 1:
            ns, _, nd, _ = _course_ends(i + 1)
            p.hermite((d[0] * BEND_M, d[1] * BEND_M), ns,
                      (nd[0] * BEND_M, nd[1] * BEND_M), 70)
    _, e6, d6, _ = _course_ends(N_COURSES - 1)
    p.hermite((d6[0] * 70, d6[1] * 70), (CW - INSET - HALF, 528.0), (0.0, 70.0), 60)
    p.line((CW - INSET - HALF, CH + 40.0))
    p.mark("tail_end")
    return p.resample()


PATH = build_path()
SW = int(PATH.total * SS) + 1


def u_of_phase(f):
    """Map a day phase onto its strip column: each course carries one phase."""
    for i in range(N_COURSES):
        f0, f1 = phase_of_course(i)
        if f0 <= f <= f1:
            q = (f - f0) / (f1 - f0)
            a, b = PATH.marks[f"c{i}s"], PATH.marks[f"c{i}e"]
            return int(a + q * (b - a)), i
    return PATH.marks[f"c{N_COURSES - 1}e"], N_COURSES - 1


# ── strip texture ────────────────────────────────────────────────────────────
_NOISE = [_rng.random() for _ in range(8192)]


def noise(i):
    return _NOISE[i % 8192]


def _column_course(u):
    """Course index owning strip column u, and its fraction along that course."""
    for i in range(N_COURSES):
        a, b = PATH.marks[f"c{i}s"], PATH.marks[f"c{i}e"]
        if u < a:
            return (i, 0.0, False) if i == 0 else (i - 1, 1.0, False)
        if a <= u <= b:
            return i, (u - a) / max(1, b - a), True
    return N_COURSES - 1, 1.0, False


def _glyph(surf, kind, cx, cy, col):
    """Embossed event glyphs, sized for a ~20px-tall crimped ferrule face."""
    r = 6 * SS
    if kind == "GEYSER":
        pygame.draw.line(surf, col, (cx, cy + r * 0.7), (cx, cy - r * 0.8), 2 * SS)
        pygame.draw.line(surf, col, (cx - r * 0.55, cy + r * 0.5),
                         (cx - r * 0.75, cy - r * 0.15), SS)
        pygame.draw.line(surf, col, (cx + r * 0.55, cy + r * 0.5),
                         (cx + r * 0.75, cy - r * 0.15), SS)
        pygame.draw.circle(surf, col, (int(cx), int(cy - r * 1.0)), max(1, SS))
    elif kind == "CLOWN":
        pygame.draw.circle(surf, col, (int(cx), int(cy + r * 0.15)), int(r * 0.62), SS)
        pygame.draw.circle(surf, col, (int(cx), int(cy + r * 0.15)), max(1, int(SS * 1.2)))
        pygame.draw.arc(surf, col, (cx - r * 0.95, cy - r * 1.15, r * 0.9, r * 0.9),
                        0.2, 2.6, SS)
        pygame.draw.arc(surf, col, (cx + r * 0.05, cy - r * 1.15, r * 0.9, r * 0.9),
                        0.5, 2.9, SS)
    elif kind == "STORM":
        pygame.draw.polygon(surf, col, [
            (cx + r * 0.35, cy - r * 0.95), (cx - r * 0.5, cy + r * 0.12),
            (cx - r * 0.02, cy + r * 0.12), (cx - r * 0.32, cy + r * 0.98),
            (cx + r * 0.52, cy - r * 0.2), (cx + r * 0.04, cy - r * 0.2)])
    elif kind == "SNOW":
        for k in range(6):
            a = math.pi * k / 3.0
            pygame.draw.line(surf, col, (cx, cy),
                             (cx + math.cos(a) * r * 0.9, cy + math.sin(a) * r * 0.9), SS)


def _ferrule(metal, u, flipped, kind):
    """Crimped brass ferrule: a metal band wrapping the full tape width."""
    w = 15 * SS
    x0 = int(u - w / 2)
    for dx in range(w):
        for dy in range(STRIP_H):
            vq = dy / (STRIP_H - 1)
            # Bright through the middle of the band, dark at the rolled edges.
            sh = 1.0 - abs(vq - 0.46) * 1.9
            sh = max(0.0, min(1.0, sh))
            col = lerp_c(BRASS_LO, BRASS_HI, sh ** 1.25)
            col = lerp_c(col, BRASS, 0.35)
            metal.set_at((x0 + dx, dy), col + (255,))
    for cx in (x0 + 3 * SS, x0 + w - 3 * SS):
        pygame.draw.line(metal, BRASS_LO + (255,), (cx, 0), (cx, STRIP_H), SS)
        pygame.draw.line(metal, BRASS_HI + (255,), (cx + SS, 0), (cx + SS, STRIP_H), max(1, SS // 2))
    face = pygame.Surface((w, STRIP_H), pygame.SRCALPHA)
    gc = VIOLET_WHITE if kind == "STORM" else (250, 232, 186)
    _glyph(face, kind, w / 2, STRIP_H / 2 + SS * 0.6, BRASS_LO)
    _glyph(face, kind, w / 2, STRIP_H / 2 - SS * 0.4, gc)
    if flipped:
        face = pygame.transform.rotate(face, 180)
    metal.blit(face, (x0, 0))


def _ghost_ferrule(ink, u, flipped, kind):
    """Events still ahead print as an un-crimped registration mark, not metal."""
    w = 15 * SS
    x0 = int(u - w / 2)
    g = pygame.Surface((w, STRIP_H), pygame.SRCALPHA)
    col = CHARCOAL + (160,)
    pygame.draw.rect(g, col, (0, TAPE_V0 + SS, w, TAPE_V1 - TAPE_V0 - 2 * SS), SS)
    _glyph(g, kind, w / 2, STRIP_H / 2, CHARCOAL + (180,))
    if flipped:
        g = pygame.transform.rotate(g, 180)
    ink.blit(g, (x0, 0))


def build_strip(run):
    """Compose the whole tape as one flat texture, then let the path bend it."""
    u_death, death_course = u_of_phase(run["phase"])
    if run["day"] >= 2:
        u_cut = u_death
    else:
        u_cut = u_death

    # ── ink plate: everything printed with ink, so it picks up weave + bleed ──
    ink = pygame.Surface((SW, STRIP_H), pygame.SRCALPHA)
    metal = pygame.Surface((SW, STRIP_H), pygame.SRCALPHA)

    for i in range(N_COURSES):
        a, b = PATH.marks[f"c{i}s"], PATH.marks[f"c{i}e"]
        flipped = (i % 2 == 1)
        name = PHASE_BOUNDARIES[i][1]
        flown = b <= u_cut
        part = a < u_cut < b
        # Knocked-out white reads over wet ink; charcoal reads on bare stock.
        col = PAPER if (flown or part) else CHARCOAL
        ts = font(11 * SS).render(name, True, col)
        if not (flown or part):
            ts.set_alpha(215)
        if flipped:
            ts = pygame.transform.rotate(ts, 180)
        tx = a + ((b - a) - ts.get_width()) // 2
        if part:
            # Keep the label wholly on whichever side of the cut has room.
            if (u_cut - a) > (b - u_cut):
                tx = a + max(6 * SS, (u_cut - a - ts.get_width()) // 2)
            else:
                tx = u_cut + max(8 * SS, (b - u_cut - ts.get_width()) // 2)
        ink.blit(ts, (tx, (STRIP_H - ts.get_height()) // 2))

    # The tail past SUNRISE is the cycle starting over — the day outruns the screen.
    ts = font(11 * SS).render("DAY", True, CHARCOAL)
    ts.set_alpha(215)
    ink.blit(ts, (PATH.marks["c6e"] + 118 * SS, (STRIP_H - ts.get_height()) // 2))

    for f, kind in EVENT_MARKERS:
        uu, ci = u_of_phase(f)
        if uu <= u_cut:
            _ferrule(metal, uu, ci % 2 == 1, kind)
        else:
            _ghost_ferrule(ink, uu, ci % 2 == 1, kind)

    ink_b = pygame.image.tostring(ink, "RGBA")

    # ── per-pixel pass: linen, phase ink, charcoal caps, bleed ───────────────
    buf = bytearray(SW * STRIP_H * 4)
    cap_w = 5 * SS
    stub_gold = run.get("gold_cap")
    # The clamp sits at the very cut edge, so the guaranteed-legible gold band
    # is laid inboard of it — otherwise the crimp swallows most of the 10px.
    clamp_w = 7 * SS
    gold_hi = u_cut - clamp_w
    gold_lo = gold_hi - 10 * SS
    for u in range(SW):
        ci, q, on_course = _column_course(u)
        f0, f1 = phase_of_course(ci)
        f = lerp(f0, f1, q)
        top, mid, bot = sky_color_for_phase(f)
        flipped = (ci % 2 == 1)
        a, b = PATH.marks[f"c{ci}s"], PATH.marks[f"c{ci}e"]
        inked = u <= u_cut
        capped = on_course and ((u - a) < cap_w or (b - u) < cap_w)
        # Hard greyscale boundary on the flown side of the cut: 5px charcoal stripe.
        cut_end_cap = inked and on_course and 0 <= (u_cut - u) < cap_w
        # Ink-bleed: the printed edge wanders a pixel or two into the weave.
        bl = (noise(u * 3) - 0.5) * 2.4 * SS
        bl2 = (noise(u * 3 + 991) - 0.5) * 2.4 * SS
        in_gold = stub_gold is not None and gold_lo <= u <= gold_hi
        base_off = u * 4
        for v in range(STRIP_H):
            vv = (STRIP_H - 1 - v) if flipped else v
            if v < TAPE_V0 or v >= TAPE_V1:
                continue
            o = (v * SW + u) * 4
            # linen weave — a fine crosshatch plus per-pixel fibre grain
            wv = (math.sin(u * 1.15) + math.sin(v * 1.6)) * 2.0
            gr = (noise(u * 7 + v * 131) - 0.5) * 9.0
            lum = 238 + wv + gr
            ev = min(v - TAPE_V0, TAPE_V1 - 1 - v)
            if ev < 2 * SS:
                lum -= (2 * SS - ev) * 13.0
            r = max(0, min(255, int(lum * 1.000)))
            g = max(0, min(255, int(lum * 0.992)))
            bcol = max(0, min(255, int(lum * 0.962)))
            shade = lum / 238.0
            if inked:
                t0 = TAPE_V0 + bl
                t1 = TAPE_V1 + bl2
                if t0 <= v < t1:
                    vq = (vv - TAPE_V0) / max(1.0, (TAPE_V1 - TAPE_V0))
                    vq = max(0.0, min(1.0, vq))
                    if vq < 0.5:
                        ic = lerp_c(top, mid, vq * 2)
                    else:
                        ic = lerp_c(mid, bot, (vq - 0.5) * 2)
                    if capped or cut_end_cap:
                        ic = CHARCOAL
                    if in_gold:
                        ic = GOLD
                    # Weave shows through the ink instead of sitting under it.
                    r = max(0, min(255, int(ic[0] * shade)))
                    g = max(0, min(255, int(ic[1] * shade)))
                    bcol = max(0, min(255, int(ic[2] * shade)))
            # printed text / ghost ferrules, bled into the weave
            jx = u + int((noise(u * 5 + v) - 0.5) * 2.2)
            jy = v + int((noise(u + v * 17) - 0.5) * 2.2)
            if 0 <= jx < SW and 0 <= jy < STRIP_H:
                io = (jy * SW + jx) * 4
                ia = ink_b[io + 3]
                if ia:
                    al = (ia / 255.0) * (0.80 + 0.20 * shade)
                    r = int(lerp(r, ink_b[io] * shade, al))
                    g = int(lerp(g, ink_b[io + 1] * shade, al))
                    bcol = int(lerp(bcol, ink_b[io + 2] * shade, al))
            buf[o] = r
            buf[o + 1] = g
            buf[o + 2] = bcol
            buf[o + 3] = 255
        base_off += 0

    strip = pygame.image.frombytes(bytes(buf), (SW, STRIP_H), "RGBA")

    # ── cut kerf + scarlet crimp tag ─────────────────────────────────────────
    kerf = 3 * SS
    if run["phase"] < 0.999:
        pygame.draw.rect(strip, (0, 0, 0, 0), (u_cut + 1, 0, kerf, STRIP_H))
        clamp_w = 7 * SS  # matches the gold-cap reservation above
        cx0 = u_cut + 1 - clamp_w
        for dx in range(clamp_w):
            for dy in range(STRIP_H):
                vq = dy / (STRIP_H - 1)
                sh = 1.0 - abs(vq - 0.44) * 1.8
                sh = max(0.0, min(1.0, sh))
                col = lerp_c((92, 18, 14), (226, 92, 78), sh ** 1.3)
                col = lerp_c(col, SCARLET, 0.4)
                strip.set_at((cx0 + dx, dy), col + (255,))
        pygame.draw.line(strip, (255, 170, 150, 220), (cx0 + SS, 0), (cx0 + SS, STRIP_H), max(1, SS // 2))

    # ── DAY 2 lap-splice plate ───────────────────────────────────────────────
    if run["day"] >= 2:
        us = PATH.marks["c0s"] + 10 * SS
        pw, ph = 52 * SS, STRIP_H
        for dx in range(pw):
            for dy in range(ph):
                vq = dy / (ph - 1)
                sh = 1.0 - abs(vq - 0.4) * 1.7
                sh = max(0.0, min(1.0, sh))
                col = lerp_c((72, 76, 86), (216, 220, 230), sh ** 1.2)
                col = lerp_c(col, STEEL, 0.3)
                strip.set_at((us + dx, dy), col + (255,))
        pygame.draw.rect(strip, (54, 58, 68, 255), (us, TAPE_V0 - SS, pw, ph - 2 * (TAPE_V0 - SS)), SS)
        for rx in (us + 5 * SS, us + pw - 5 * SS):
            for ry in (TAPE_V0 + 4 * SS, TAPE_V1 - 4 * SS):
                pygame.draw.circle(strip, (238, 242, 250, 255), (rx, ry), int(SS * 1.5))
                pygame.draw.circle(strip, (60, 64, 74, 255), (rx, ry), max(1, int(SS * 0.7)))
        st = font(10 * SS).render("DAY 2", True, (28, 30, 36))
        strip.blit(st, (us + (pw - st.get_width()) // 2, (ph - st.get_height()) // 2))

    strip.blit(metal, (0, 0))
    return strip, u_cut


# ── lay the flat strip along the serpentine path ─────────────────────────────
def lay_tape(strip):
    sb = pygame.image.tostring(strip, "RGBA")
    buf = bytearray(DW * DH * 4)
    for k in range(PATH.n):
        u = int(k * DS * SS)
        if u >= SW:
            break
        (cx, cy), (tx, ty) = PATH.pts[k], PATH.tan[k]
        nx, ny = -ty, tx
        px0 = cx * SS
        py0 = cy * SS
        for v in range(STRIP_H):
            so = (v * SW + u) * 4
            if not sb[so + 3]:
                continue
            d = v - STRIP_HALF + 0.5
            X = int(px0 + nx * d)
            Y = int(py0 + ny * d)
            if 0 <= X < DW and 0 <= Y < DH:
                o = (Y * DW + X) * 4
                buf[o] = sb[so]
                buf[o + 1] = sb[so + 1]
                buf[o + 2] = sb[so + 2]
                buf[o + 3] = 255
    return pygame.image.frombytes(bytes(buf), (DW, DH), "RGBA")


def desaturate(surf, amount, darken):
    s = surf.copy()
    b = bytearray(pygame.image.tostring(s, "RGBA"))
    for i in range(0, len(b), 4):
        if not b[i + 3]:
            continue
        y = (b[i] * 77 + b[i + 1] * 151 + b[i + 2] * 28) >> 8
        for k in range(3):
            b[i + k] = max(0, min(255, int(lerp(b[i + k], y, amount) * (1.0 - darken))))
    return pygame.image.frombytes(bytes(b), s.get_size(), "RGBA")


# ── canvas-space furniture ───────────────────────────────────────────────────
def glow(surf, cx, cy, r, col, peak):
    """BLEND_ADD ignores alpha, so the falloff is baked into the RGB channels."""
    g = pygame.Surface((r * 2, r * 2))
    for y in range(r * 2):
        for x in range(r * 2):
            d = math.hypot(x - r, y - r)
            if d < r:
                f = (1 - d / r) ** 2 * peak
                g.set_at((x, y), (int(col[0] * f), int(col[1] * f), int(col[2] * f)))
    surf.blit(g, (int(cx - r), int(cy - r)), special_flags=pygame.BLEND_ADD)


def draw_drum(s):
    """Knurled gold marker-tape drum, pinned through the top-left corner."""
    cx, cy, R = 52 * SS, 62 * SS, 26 * SS
    glow(s, cx, cy, int(R * 2.1), (255, 206, 110), 0.30)
    pygame.draw.circle(s, (48, 38, 16), (cx + SS, cy + int(SS * 1.5)), R)
    # knurled rim — alternating teeth around the flange
    teeth = 44
    for k in range(teeth):
        a0 = 2 * math.pi * k / teeth
        a1 = 2 * math.pi * (k + 0.52) / teeth
        c = lerp_c((150, 108, 34), GOLD, 0.5 + 0.5 * math.sin(a0 * 1.0 + 0.6))
        pygame.draw.polygon(s, c, [
            (cx + math.cos(a0) * R, cy + math.sin(a0) * R),
            (cx + math.cos(a1) * R, cy + math.sin(a1) * R),
            (cx + math.cos(a1) * R * 0.86, cy + math.sin(a1) * R * 0.86),
            (cx + math.cos(a0) * R * 0.86, cy + math.sin(a0) * R * 0.86)])
    pygame.draw.circle(s, lerp_c(GOLD, (120, 84, 24), 0.25), (cx, cy), int(R * 0.87))
    # wound stock, lit from upper-left
    for k in range(int(R * 0.87), int(R * 0.30), -1):
        t = (k - R * 0.30) / (R * 0.57)
        pygame.draw.circle(s, lerp_c((252, 226, 150), (128, 88, 26), t * 0.92), (cx, cy), k, 1)
    for k in range(18):
        a = 2 * math.pi * k / 18 + 0.22
        pygame.draw.line(s, (140, 98, 30),
                         (cx + math.cos(a) * R * 0.34, cy + math.sin(a) * R * 0.34),
                         (cx + math.cos(a) * R * 0.84, cy + math.sin(a) * R * 0.84), max(1, SS // 2))
    pygame.draw.circle(s, (86, 60, 20), (cx, cy), int(R * 0.30))
    pygame.draw.circle(s, lerp_c(GOLD, (255, 246, 214), 0.55), (cx, cy), int(R * 0.20))
    pygame.draw.circle(s, (60, 42, 14), (cx, cy), int(R * 0.09))
    pygame.draw.circle(s, (255, 248, 220), (int(cx - R * 0.34), int(cy - R * 0.40)), int(R * 0.08))


def text(s, msg, x, y, px, col, align="left", alpha=255, track=0):
    f = font(px * SS)
    if track:
        surfs = [f.render(ch, True, col) for ch in msg]
        w = sum(t.get_width() for t in surfs) + track * SS * (len(msg) - 1)
        h = surfs[0].get_height() if surfs else 0
        t = pygame.Surface((max(1, w), max(1, h)), pygame.SRCALPHA)
        cx = 0
        for sf in surfs:
            t.blit(sf, (cx, 0))
            cx += sf.get_width() + track * SS
    else:
        t = f.render(msg, True, col)
    if alpha < 255:
        t.set_alpha(alpha)
    X = x * SS
    if align == "center":
        X -= t.get_width() / 2
    elif align == "right":
        X -= t.get_width()
    s.blit(t, (int(X), int(y * SS)))
    return t.get_width() / SS


def render_run(run):
    s = pygame.Surface((DW, DH))
    s.fill(BG)
    for y in range(DH):
        t = y / DH
        c = lerp_c((10, 10, 24), (6, 6, 14), t)
        pygame.draw.line(s, c, (0, y), (DW, y))

    strip, u_cut = build_strip(run)

    if run["day"] >= 2:
        # Day 1 is spent stock: kept in frame, desaturated and set behind.
        prev = dict(run)
        prev["phase"] = 0.9999
        prev["day"] = 1
        prev["gold_cap"] = None
        pstrip, _ = build_strip(prev)
        player = desaturate(lay_tape(pstrip), 0.35, 0.30)
        s.blit(player, (5 * SS, 6 * SS))

    s.blit(lay_tape(strip), (0, 0))
    draw_drum(s)

    # header
    text(s, "FLIGHT LOG", 90, 42, 17, GOLD, track=1)
    text(s, f"SKYBIT  ·  DAY {run['day']}", 90, 65, 9, (150, 156, 176), track=1)
    text(s, run["time"], CW - INSET, 42, 15, PAPER, align="right")
    text(s, "ALOFT", CW - INSET, 62, 8, (130, 136, 156), align="right", track=1)

    # cut furniture, positioned from the path so it always finds the tape
    (dx, dy), (tx, ty) = PATH.at(u_cut)
    nx, ny = -ty, tx
    if run.get("gold_cap"):
        # A 3% stub is too short to label in place: lead the read out to the margin.
        lx, ly = dx * SS, dy * SS
        my = (ROW0_Y - PITCH * 0.46) * SS
        pygame.draw.line(s, (120, 96, 46), (lx, ly - HALF * SS), (lx, my), max(1, SS // 2))
        pygame.draw.line(s, (120, 96, 46), (lx, my), ((CW - INSET) * SS, my), max(1, SS // 2))
        pygame.draw.circle(s, GOLD, (int(lx), int(my)), int(SS * 1.6))
        text(s, run["leader"], CW - INSET, ROW0_Y - PITCH * 0.46 - 12, 9, GOLD, align="right", track=1)
    else:
        # Parallelogram flag hanging off tape outer edge at the cut point.
        # Base spans 10px along the tape edge; body extends 16px outward — well
        # above the 14px minimum and self-explanatory without a text label.
        fx = dx + nx * HALF
        fy = dy + ny * HALF
        tag = [
            (fx - tx * 5, fy - ty * 5),
            (fx + tx * 5, fy + ty * 5),
            (fx + nx * 16 + tx * 5, fy + ny * 16 + ty * 5),
            (fx + nx * 16 - tx * 5, fy + ny * 16 - ty * 5),
        ]
        pygame.draw.polygon(s, SCARLET, [(p[0] * SS, p[1] * SS) for p in tag])
        pygame.draw.polygon(s, (232, 96, 80), [(p[0] * SS, p[1] * SS) for p in tag], max(1, SS // 2))

    # run summary
    by = 512
    pygame.draw.line(s, (46, 48, 62), (INSET * SS, (by - 14) * SS), (250 * SS, (by - 14) * SS), max(1, SS // 2))
    w = text(s, str(run["pillar"]), INSET, by, 42, GOLD)
    text(s, "PILLARS", INSET + w + 8, by + 24, 10, (168, 174, 194), track=1)
    pct = f"{run['phase'] * 100:.1f}% OF DAY FLOWN"
    text(s, pct, INSET, by + 54, 10, PAPER, track=1)
    text(s, f"CUT IN  {run['cut_phase']}", INSET, by + 72, 10, (168, 174, 194), track=1)
    text(s, run["note"], INSET, by + 90, 9, (120, 126, 148), track=1)
    text(s, "TAPE CONTINUES", CW - INSET - 26, 596, 7, (108, 114, 136), align="right", track=1)

    # BACK navigation button — gold outlined rect, tracked caps, 24px tap height.
    _btn_cx = CW // 2
    _btn_cy = 623
    _btn_w = 72
    _btn_h = 22
    pygame.draw.rect(
        s, GOLD,
        (int((_btn_cx - _btn_w // 2) * SS), int((_btn_cy - _btn_h // 2) * SS),
         _btn_w * SS, _btn_h * SS),
        max(1, SS),
    )
    text(s, "BACK", _btn_cx, _btn_cy - 5, 10, GOLD, align="center", track=2)

    return pygame.transform.smoothscale(s, (CW, CH)), s


# ── review sheet ─────────────────────────────────────────────────────────────
RUN_A = dict(phase=0.184, pillar=25, day=1, time="0:47", cut_phase="DAY",
             note="GEYSER CLEARED  ·  3 EVENTS AHEAD", gold_cap=None, leader="")
RUN_B = dict(phase=0.030, pillar=180, day=1, time="0:09", cut_phase="DAY",
             note="SPRINT RUN  ·  4 EVENTS AHEAD", gold_cap=True,
             leader="3%  ·  PILLAR 180")
RUN_C = dict(phase=0.550, pillar=62, day=2, time="7:45", cut_phase="DUSK",
             note="SPLICED AT SUNRISE  ·  SNOW AHEAD", gold_cap=None, leader="")

SHEET_W, SHEET_H = 1560, 880


def label(sheet, msg, x, y, px, col, alpha=255, track=0):
    f = font(px)
    if track:
        surfs = [f.render(ch, True, col) for ch in msg]
        w = sum(t.get_width() for t in surfs) + track * (len(msg) - 1)
        t = pygame.Surface((max(1, w), surfs[0].get_height()), pygame.SRCALPHA)
        cx = 0
        for sf in surfs:
            t.blit(sf, (cx, 0))
            cx += sf.get_width() + track
    else:
        t = f.render(msg, True, col)
    if alpha < 255:
        t.set_alpha(alpha)
    sheet.blit(t, (x, y))
    return t.get_width()


def main():
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    for y in range(SHEET_H):
        pygame.draw.line(sheet, lerp_c((22, 22, 28), (14, 14, 19), y / SHEET_H),
                         (0, y), (SHEET_W, y))

    label(sheet, "SKYBIT  ·  FLIGHT LOG SCREEN", 36, 30, 26, GOLD, track=2)
    label(sheet, "CONCEPT: CABLE TAPE   —   ROUND 2", 36, 64, 15, (176, 182, 202), track=2)
    label(sheet, "marker-tape drum pays out linen cable tape · serpentine courses · "
                 "flown tape over-printed, unflown tape bare stock", 640, 40, 14, (128, 134, 156))
    label(sheet, "360x640 virtual canvas · all art procedural · scarlet reserved for the crimp tag",
          640, 62, 14, (104, 110, 132))

    panels = [(RUN_A, "HERO  ·  RUN A", "phase 0.184 · pillar 25 · day 1 · cut mid-course 1"),
              (RUN_B, "EDGE  ·  3% STUB", "fixed 10px gold end-cap + printed leader to margin"),
              (RUN_C, "EDGE  ·  DAY 2", "lap-splice plate stamped DAY 2 · day 1 set behind")]

    hero_hi = None
    for i, (run, title, sub) in enumerate(panels):
        img, hi = render_run(run)
        if i == 0:
            hero_hi = hi
        x = 36 + i * 396
        y = 124
        pygame.draw.rect(sheet, (58, 60, 74), (x - 2, y - 2, CW + 4, CH + 4), 2)
        sheet.blit(img, (x, y))
        label(sheet, title, x, y + CH + 10, 15, GOLD, track=1)
        label(sheet, sub, x, y + CH + 30, 12, (140, 146, 168))

    # 2x construction crops, taken from the hero's native 2x render
    crops = [((16, 26, 150, 95), "DRUM + PAYOUT", "knurled gold flange · tape emerges from behind the body"),
             ((140, 100, 150, 95), "FERRULE + CUT", "brass GEYSER ferrule · charcoal cap · kerf · scarlet crimp tag"),
             ((196, 250, 150, 95), "FOLD + UNFLOWN", "hand-set fold · bare stock 238 · ghost ferrule ahead")]
    cx = 1224
    for i, (rect, t1, t2) in enumerate(crops):
        cy = 124 + i * 214
        sub = hero_hi.subsurface((rect[0] * SS, rect[1] * SS, rect[2] * SS, rect[3] * SS)).copy()
        pygame.draw.rect(sheet, (58, 60, 74), (cx - 2, cy - 2, rect[2] * SS + 4, rect[3] * SS + 4), 2)
        sheet.blit(sub, (cx, cy))
        label(sheet, f"2x  ·  {t1}", cx, cy + rect[3] * SS + 8, 13, GOLD, track=1)
        label(sheet, t2, cx, cy + rect[3] * SS + 26, 11, (134, 140, 162))

    # footer: colour audit
    fy = 792
    pygame.draw.line(sheet, (52, 54, 68), (36, fy - 18), (SHEET_W - 36, fy - 18), 1)
    label(sheet, "SCARLET AUDIT", 36, fy, 13, (170, 176, 196), track=1)
    sw = [("GOLD  drum · end-cap", GOLD), ("SCARLET  crimp tag ONLY", SCARLET),
          ("BRASS  ferrules", BRASS), ("VIOLET-WHITE  storm glyph", VIOLET_WHITE),
          ("STOCK 238  unflown", PAPER), ("CHARCOAL  caps · print", CHARCOAL)]
    x = 190
    for name, col in sw:
        pygame.draw.rect(sheet, col, (x, fy - 2, 20, 20))
        pygame.draw.rect(sheet, (70, 72, 88), (x, fy - 2, 20, 20), 1)
        w = label(sheet, name, x + 27, fy + 3, 12, (150, 156, 178))
        x += 27 + w + 26
    label(sheet, "phase ink colours sampled from game/biome.py keyframes "
                 "(DAY · GOLDEN HOUR · SUNSET · DUSK · NIGHT · PREDAWN · SUNRISE)",
          36, fy + 34, 12, (104, 110, 132))

    out = os.path.join(OUT_DIR, "round_2.png")
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    return out


if __name__ == "__main__":
    main()
