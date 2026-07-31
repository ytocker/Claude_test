"""Round-1 review render of the `sealed_permit` Flight Log concept.

The run is told as a border-control document rather than a chart: a permit
booklet stood portrait, spine at left, cover flap peeled back off the gutter
to expose one page face. The page is bright unstamped security stock — the
brightest mass on screen against the dark plum field — and the seven phases
of the day cycle are entry boxes waiting to be cancelled. Phases the player
actually flew are struck with a rubber-stamp cachet inked in that phase's own
sky colour; everything ahead of the death stays virgin stock, which is where
the foil sweep is left strongest so the unearned boxes visibly gleam. The run
ends with a scarlet wax seal pressed half onto the last stamped box and half
onto the next unstamped one: the document is closed, the flight stops there.

Scarlet is spent once, on the seal. Every warm phase ink is clamped short of
it so nothing else on the page competes for that read.

Offline tool — writes docs/flight_log_screen/sealed_permit/round_1.png.
Nothing here is imported by the game.
"""
from __future__ import annotations

import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

pygame.display.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
OUT_DIR = os.path.join(ROOT, "docs", "flight_log_screen", "sealed_permit")

W, H = 360, 640

BG = (12, 10, 18)
GOLD = (240, 192, 64)
SCARLET = (172, 40, 32)
SCARLET_DEEP = (116, 24, 20)
SCARLET_LIT = (214, 86, 72)
GUNMETAL = (74, 78, 88)
CHARCOAL = (80, 75, 70)
GREY_TEXT = (160, 155, 150)

STOCK = (244, 242, 240)
STOCK_EDGE = (222, 218, 214)
BAND = (220, 218, 215)
HAIRLINE = (190, 185, 180)
CHIT = (206, 203, 199)
CHIT_EDGE = (150, 146, 142)

COVER = (58, 44, 40)
COVER_LINER = (104, 80, 66)
SPINE_C = (110, 100, 90)

# ── phase data ───────────────────────────────────────────────────────────────

PHASE_BOUNDARIES = [
    (0.000, "DAY"),
    (0.231, "GOLDEN HOUR"),
    (0.363, "SUNSET"),
    (0.513, "DUSK"),
    (0.644, "NIGHT"),
    (0.794, "PREDAWN"),
    (0.906, "SUNRISE"),
]
PHASE_NAMES = [n for _, n in PHASE_BOUNDARIES]
PHASE_END = [PHASE_BOUNDARIES[i + 1][0] if i + 1 < len(PHASE_BOUNDARIES) else 1.0
             for i in range(len(PHASE_BOUNDARIES))]

# Cachet copy is set on two lines so a 27px stamp ring can sit over the box
# centre without burying the label.
PHASE_LINES = {
    "DAY": ("DAY", ""),
    "GOLDEN HOUR": ("GOLDEN", "HOUR"),
    "SUNSET": ("SUNSET", ""),
    "DUSK": ("DUSK", ""),
    "NIGHT": ("NIGHT", ""),
    "PREDAWN": ("PRE", "DAWN"),
    "SUNRISE": ("SUN", "RISE"),
}

EVENT_MARKERS = [
    (0.15, "GEYSER"),
    (0.41, "CLOWN"),
    (0.44, "STORM"),
    (0.85, "SNOW"),
]

RUNS = [
    dict(tag="RUN A", pillars=25, phase=0.184, day=1, time="0:47",
         cause="GEYSER", seed=4021),
    dict(tag="RUN B", pillars=180, phase=0.031, day=2, time="5:30",
         cause="SNOW", seed=9137),
]

# ── phase ink (derived from game/biome.py sky keyframes) ─────────────────────
# `sky_mid` is the channel that actually reads as "what colour was the sky",
# so it drives each cachet's ink.

SKY_MID = {
    "DAY": (90, 170, 230),
    "GOLDEN HOUR": (220, 175, 140),
    "SUNSET": (230, 95, 120),
    "DUSK": (70, 45, 130),
    "NIGHT": (15, 25, 70),
    "PREDAWN": (70, 60, 140),
    "SUNRISE": (255, 150, 150),
}
AMBER_MAX = (204, 104, 56)
AMBER_DEEP = (150, 74, 40)
AMBER_LIGHT = (216, 146, 88)


def _mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _is_warm(c):
    return c[0] > 190 and c[0] > c[1]


def _build_inks():
    """Warm sky keyframes sit close enough to scarlet that a stamped SUNSET
    would read as a second wax seal. They are pulled onto an amber ramp that
    tops out at AMBER_MAX, and re-spread along it by their source luminance so
    the three of them stay tellable apart instead of collapsing to one amber."""
    warm = [n for n in PHASE_NAMES if _is_warm(SKY_MID[n])]
    warm.sort(key=lambda n: _lum(SKY_MID[n]))
    clamped = {}
    for n in PHASE_NAMES:
        if n in warm:
            t = warm.index(n) / max(1, len(warm) - 1)
            clamped[n] = _mix(AMBER_DEEP, AMBER_LIGHT, t)
        else:
            clamped[n] = SKY_MID[n]
    inks = {}
    for n in PHASE_NAMES:
        c = _mix(clamped[n], (26, 22, 30), 0.30)
        # Night ink lands near-black on 244 stock; lift it just enough to keep
        # a hue rather than reading as a smudge.
        if _lum(c) < 45:
            c = _mix(c, (255, 255, 255), (45 - _lum(c)) / (255 - _lum(c)))
        inks[n] = c
    return clamped, inks


CLAMPED_SKY, PHASE_INK = _build_inks()

# ── text helpers ─────────────────────────────────────────────────────────────

_fonts: dict = {}


def _font(size):
    f = _fonts.get(size)
    if f is None:
        f = pygame.font.Font(FONT_PATH, size)
        _fonts[size] = f
    return f


def _fade(img, alpha):
    """set_alpha on a per-pixel-alpha surface is unreliable across SDL builds;
    a multiply blit is not."""
    out = img.convert_alpha()
    out.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    return out


def _caps(surf, txt, x, y, size, color, tracking=1, anchor="left", alpha=255):
    """Letter-spaced caps; `y` is the vertical centre. Tracking is what keeps
    6-8px document lettering reading as print rather than a smudge."""
    f = _font(size)
    glyphs = [f.render(c, True, color) for c in txt]
    if not glyphs:
        return 0
    total = sum(g.get_width() for g in glyphs) + tracking * (len(glyphs) - 1)
    gx = x if anchor == "left" else (x - total if anchor == "right"
                                     else x - total // 2)
    gy = y - glyphs[0].get_height() // 2
    for img in glyphs:
        surf.blit(_fade(img, alpha) if alpha < 255 else img, (int(gx), int(gy)))
        gx += img.get_width() + tracking
    return total


def _caps_w(txt, size, tracking=1):
    f = _font(size)
    if not txt:
        return 0
    return sum(f.size(c)[0] for c in txt) + tracking * (len(txt) - 1)


def _arc_caps(surf, txt, cx, cy, radius, size, color, span_deg, top=True,
              alpha=255):
    """Type set around a stamp ring. Glyph rotation is derived from its own
    angle so the baseline stays tangent all the way round."""
    f = _font(size)
    n = len(txt)
    if n == 0:
        return
    step = span_deg / max(1, n - 1) if n > 1 else 0.0
    for i, ch in enumerate(txt):
        off = (i - (n - 1) / 2.0) * step
        a = (-90.0 + off) if top else (90.0 - off)
        rot = (-(a + 90.0)) if top else (-(a + 90.0) + 180.0)
        g = f.render(ch, True, color)
        if alpha < 255:
            g = _fade(g, alpha)
        g = pygame.transform.rotate(g, rot)
        r = math.radians(a)
        surf.blit(g, g.get_rect(center=(cx + radius * math.cos(r),
                                        cy + radius * math.sin(r))))


# ── page stock ───────────────────────────────────────────────────────────────

_ROSETTE = None


def _rosette():
    """Micro-guilloche. Three nested hypotrochoids per rosette give the
    interlaced band look of real security printing; contrast is kept at a few
    percent so it never competes with the stamps printed over it."""
    global _ROSETTE
    if _ROSETTE is not None:
        return _ROSETTE
    R, r = 60, 20
    size = 180
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size // 2
    for d, alpha in ((45, 26), (38, 20), (31, 15)):
        pts = []
        for i in range(220):
            t = i * 2 * math.pi / 220
            k = (R - r) / r
            pts.append((c + (R - r) * math.cos(t) + d * math.cos(k * t),
                        c + (R - r) * math.sin(t) - d * math.sin(k * t)))
        pygame.draw.lines(surf, (150, 140, 128, alpha), True, pts, 1)
    _ROSETTE = surf
    return surf


def _draw_parrot(surf, cx, cy, s, color):
    """Simplified macaw chop: tail fan left, round body, head and hooked beak
    upper-right — the same silhouette the in-game bird reads as at 8px."""
    def P(pts):
        pygame.draw.polygon(surf, color,
                            [(cx + px * s, cy + py * s) for px, py in pts])

    def E(ox, oy, rx, ry):
        pygame.draw.ellipse(surf, color,
                            pygame.Rect(int(cx + (ox - rx) * s),
                                        int(cy + (oy - ry) * s),
                                        max(1, int(2 * rx * s)),
                                        max(1, int(2 * ry * s))))

    P([(-1.15, 0.02), (-0.30, -0.16), (-0.22, 0.30), (-1.02, 0.44)])
    E(0.00, 0.06, 0.56, 0.43)
    P([(-0.34, -0.20), (0.30, -0.30), (0.16, 0.20), (-0.30, 0.16)])
    E(0.46, -0.36, 0.34, 0.32)
    P([(0.66, -0.46), (0.98, -0.30), (0.82, -0.06), (0.60, -0.14)])


def _page_stock(rect, seed, gutter_w):
    """The page face itself, built once so the guilloche and foil can be
    clipped to the sheet before anything is printed on it."""
    page = pygame.Surface((rect.w, rect.h))
    page.fill(STOCK)

    ros = _rosette()
    for gy in range(-40, rect.h + 120, 120):
        for gx in range(-40, rect.w + 120, 120):
            page.blit(ros, ros.get_rect(center=(gx, gy)))

    # Watermark: a large chop in the stock, printed under everything so the
    # cachets read as over-printed on it.
    wm = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    _draw_parrot(wm, rect.w * 0.54, rect.h * 0.40, 84, (118, 112, 104, 13))
    page.blit(wm, (0, 0))

    rnd = random.Random(seed)
    grain = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for _ in range(3000):
        gx, gy = rnd.randrange(rect.w), rnd.randrange(rect.h)
        if rnd.random() < 0.5:
            grain.set_at((gx, gy), (255, 255, 255, rnd.randint(10, 26)))
        else:
            grain.set_at((gx, gy), (120, 112, 100, rnd.randint(8, 18)))
    page.blit(grain, (0, 0))

    # Gutter: the sheet bending into the spine, plus the lifted outer edge.
    shade = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for i in range(gutter_w):
        a = int(78 * (1 - i / gutter_w) ** 1.7)
        shade.fill((60, 52, 44, a), (i, 0, 1, rect.h))
    for i in range(10):
        shade.fill((70, 60, 50, int(26 * (1 - i / 10))),
                   (rect.w - 1 - i, 0, 1, rect.h))
        shade.fill((70, 60, 50, int(30 * (1 - i / 10))),
                   (0, rect.h - 1 - i, rect.w, 1))
    page.blit(shade, (0, 0))
    return page


def _axis_strip(length, band, peak, dark, angle=-39.0):
    strip = pygame.Surface((length, band), pygame.SRCALPHA)
    col = (44, 38, 32) if dark else (255, 255, 254)
    for i in range(band):
        t = (i - band / 2.0) / (band / 2.0)
        g = math.exp(-3.4 * t * t)
        a = int(peak * ((1.0 - g) if dark else g))
        if a > 0:
            strip.fill((*col, a), (0, i, length, 1))
    return pygame.transform.rotate(strip, angle)


def _foil(target, clip, cx, cy, length, band, peak, dark=False, angle=-39.0):
    """Diagonal specular sweep. Bright stock has barely 11 levels of headroom
    to white, so the gleam is built by shading the sheet *away* from the axis
    as well as lighting it along the axis — the contrast has to come from the
    surround. Drawn per-clip so unflown boxes take a hotter pass than the
    sheet; untouched stock is the thing meant to shine."""
    rot = _axis_strip(length, band, peak, dark, angle)
    old = target.get_clip()
    target.set_clip(clip)
    target.blit(rot, rot.get_rect(center=(cx, cy)))
    target.set_clip(old)


# ── booklet furniture ────────────────────────────────────────────────────────

def _cover_and_spine(surf, page, spine_w, signatures, seed):
    board = page.inflate(14, 14)
    board.x -= 3
    shadow = pygame.Surface((board.w + 16, board.h + 16), pygame.SRCALPHA)
    for i in range(7):
        pygame.draw.rect(shadow, (0, 0, 0, 40 - i * 5),
                         (7 - i, 7 - i, board.w + i * 2, board.h + i * 2),
                         border_radius=5)
    surf.blit(shadow, (board.x - 5, board.y - 1))
    pygame.draw.rect(surf, COVER, board, border_radius=4)
    pygame.draw.rect(surf, _mix(COVER, (0, 0, 0), 0.35), board, 1,
                     border_radius=4)

    spine = pygame.Rect(page.x, page.y, spine_w, page.h)
    for i in range(spine.w):
        t = abs(i - spine.w * 0.38) / spine.w
        pygame.draw.line(surf, _mix(SPINE_C, (48, 40, 34), min(1.0, t * 1.9)),
                         (spine.x + i, spine.y), (spine.x + i, spine.bottom - 1))
    # Signature stitching: one band per day flown, so a second day is legible
    # from the booklet's construction alone.
    rnd = random.Random(seed)
    for s in range(signatures):
        y0 = page.y + 60 + s * 150
        for k in range(9):
            y = y0 + k * 12
            if y > page.bottom - 50:
                break
            pygame.draw.line(surf, (56, 48, 40),
                             (spine.x + 3, y), (spine.right - 4, y), 1)
            pygame.draw.line(surf, (168, 158, 142),
                             (spine.x + 3, y + 1), (spine.right - 4, y + 1), 1)
        pygame.draw.circle(surf, (48, 42, 36), (spine.centerx, y0 - 9), 2)
        pygame.draw.circle(surf, (48, 42, 36),
                           (spine.centerx, y0 + 9 * 12 - 3), 2)
        rnd.random()


def _cover_peel(surf, page, spine_w):
    """The cover flap lifted off the gutter — the reason a page face is visible
    at all. Kept tight to the spine so it never crowds the entry grid."""
    x0, y0 = page.x, page.y
    reach, drop = 40, 104
    edge = []
    for i in range(31):
        t = i / 30.0
        edge.append((x0 + reach * (1 - t) ** 1.6, y0 + drop * t))

    shade = pygame.Surface((page.w, page.h), pygame.SRCALPHA)
    for k in range(9):
        pts = [(px - page.x + k * 1.5, py - page.y + k * 0.8) for px, py in edge]
        pygame.draw.lines(shade, (48, 40, 32, int(34 * (1 - k / 9.0))), False,
                          pts, 2)
    surf.blit(shade, page.topleft)

    flap = [(x0, y0)] + edge + [(x0, y0 + drop)]
    pygame.draw.polygon(surf, COVER_LINER, flap)
    inner = [(x0 + spine_w * 0.4, y0 + 4)]
    inner += [(px - 6 * (1 - i / 30.0), py + 3) for i, (px, py) in enumerate(edge)]
    pygame.draw.polygon(surf, _mix(COVER_LINER, (0, 0, 0), 0.34), inner)
    pygame.draw.lines(surf, _mix(COVER_LINER, (255, 235, 200), 0.42), False,
                      edge, 2)
    pygame.draw.lines(surf, _mix(COVER, (0, 0, 0), 0.2), False,
                      [(px, py + 2) for px, py in edge], 1)


def _prev_page_curl(surf, page, spine_w, curl_w, seed):
    """Day 1 rolling out of the gutter under day 2's face, its cachets dimmed —
    a page turn read from the edge of the sheet rather than from a label."""
    x0 = page.x + spine_w
    top, bot = page.y + 4, page.bottom - 4
    edge = []
    for i in range(41):
        t = i / 40.0
        edge.append((x0 + curl_w * math.sin(math.pi * t) ** 0.55,
                     top + (bot - top) * t))
    poly = [(x0, top)] + edge + [(x0, bot)]
    pygame.draw.polygon(surf, (222, 219, 215), poly)

    lay = pygame.Surface((page.w, page.h), pygame.SRCALPHA)
    rnd = random.Random(seed)
    for k, name in enumerate(PHASE_NAMES[:5]):
        cy = top + 70 + k * 96 - page.y
        cx = x0 + curl_w * 0.42 - page.x
        pygame.draw.circle(lay, (*PHASE_INK[name], 54), (int(cx), int(cy)), 13, 3)
        pygame.draw.circle(lay, (*PHASE_INK[name], 40), (int(cx), int(cy)), 8, 1)
        rnd.random()
    surf.blit(lay, page.topleft)

    for i, (px, py) in enumerate(edge):
        t = i / 40.0
        pygame.draw.line(surf, _mix((196, 192, 187), (120, 110, 100),
                                    math.sin(math.pi * t)),
                         (x0, py), (px, py), 1)
    pygame.draw.lines(surf, (168, 162, 154), False, edge, 1)
    sh = pygame.Surface((page.w, page.h), pygame.SRCALPHA)
    for k in range(10):
        pygame.draw.lines(sh, (52, 44, 36, int(40 * (1 - k / 10.0))), False,
                          [(px - page.x + k, py - page.y) for px, py in edge], 2)
    surf.blit(sh, page.topleft)


# ── cachet ───────────────────────────────────────────────────────────────────

def _cachet(name, r, seed, ink, partial=None):
    """A rubber-stamp impression: ring, arced phase name, and an ink bed that
    is deliberately broken. Real cachets never print solid, and a clean vector
    ring would read as UI chrome instead of something pressed onto paper."""
    m = 10
    size = 2 * (r + m)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size // 2
    rnd = random.Random(seed)

    if partial is not None:
        # Too little of the phase was flown to justify a cancellation; the
        # cachet prints only the arc that was earned.
        sweep = max(6.0, 360.0 * partial)
        pts_o, pts_i = [], []
        steps = max(4, int(sweep / 3))
        for i in range(steps + 1):
            a = math.radians(-90 + sweep * i / steps)
            pts_o.append((c + r * math.cos(a), c + r * math.sin(a)))
            pts_i.append((c + (r - 3) * math.cos(a), c + (r - 3) * math.sin(a)))
        pygame.draw.lines(surf, ink, False, pts_o, 2)
        pygame.draw.lines(surf, ink, False, pts_i, 1)
        pygame.draw.circle(surf, ink, (c, c), 2)
    else:
        pygame.draw.circle(surf, ink, (c, c), r, 3)
        pygame.draw.circle(surf, ink, (c, c), r - 6, 1)
        _arc_caps(surf, name if len(name) <= 9 else name.replace(" ", ""),
                  c, c, r - 10, 7, ink, span_deg=min(190, 15 * len(name)))
        _arc_caps(surf, "SKYBIT", c, c, r - 10, 6, ink, span_deg=76, top=False)
        bar = pygame.Rect(c - r + 9, c - 5, 2 * (r - 9), 10)
        pygame.draw.rect(surf, ink, bar, border_radius=2)
        _caps(surf, "FLOWN", c, c, 7, STOCK, tracking=1, anchor="center")
        pygame.draw.line(surf, ink, (c - r + 12, c - 9), (c + r - 12, c - 9), 1)
        pygame.draw.line(surf, ink, (c - r + 12, c + 9), (c + r - 12, c + 9), 1)

    # Ink break-up: speckle, a few starved wedges, and an overall bite so the
    # impression sits in the paper rather than on top of it.
    mot = pygame.Surface((size, size), pygame.SRCALPHA)
    mot.fill((255, 255, 255, 232))
    for _ in range(190):
        px, py = rnd.randrange(size), rnd.randrange(size)
        pygame.draw.circle(mot, (255, 255, 255, rnd.randint(30, 150)),
                           (px, py), rnd.randint(1, 3))
    for _ in range(4):
        a = rnd.uniform(0, math.tau)
        w = rnd.uniform(0.12, 0.30)
        pygame.draw.polygon(mot, (255, 255, 255, rnd.randint(0, 60)), [
            (c, c),
            (c + (r + m) * math.cos(a - w), c + (r + m) * math.sin(a - w)),
            (c + (r + m) * math.cos(a + w), c + (r + m) * math.sin(a + w)),
        ])
    surf.blit(mot, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return pygame.transform.rotate(surf, rnd.uniform(-4.0, 4.0))


# ── wax seal ─────────────────────────────────────────────────────────────────

def _lobed(cx, cy, r, lobes=8, amp=4.0, jitter=0.0, rnd=None, steps=180):
    pts = []
    for i in range(steps):
        a = i * math.tau / steps
        rr = r + amp * math.sin(lobes * a)
        if jitter and rnd:
            rr += rnd.uniform(-jitter, jitter)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def _wax_seal(surf, cx, cy, r, seed, ribbons=True):
    """Scarlet is spent here and nowhere else. The seal is the only object on
    the page with volume — lobed rim, hot specular, embossed chop — because it
    is the thing that physically stopped the run."""
    rnd = random.Random(seed)

    shadow = pygame.Surface((int(r * 4), int(r * 4)), pygame.SRCALPHA)
    sc = int(r * 2)
    for i in range(9):
        pygame.draw.polygon(shadow, (30, 18, 22, 16),
                            _lobed(sc + 2, sc + 3, r + 3 - i * 0.6))
    surf.blit(shadow, (cx - sc, cy - sc))

    if ribbons:
        for sx, tilt in ((-1, 22), (1, -18)):
            base = (cx + sx * r * 0.42, cy + r * 0.52)
            ang = math.radians(74 + tilt)
            L = r * 1.35
            tip = (base[0] + sx * math.cos(ang) * L * 0.55,
                   base[1] + math.sin(ang) * L)
            wid = r * 0.26
            pts = [(base[0] - wid, base[1]), (base[0] + wid, base[1]),
                   (tip[0] + wid * 1.15, tip[1]), (tip[0], tip[1] - wid * 0.5),
                   (tip[0] - wid * 1.15, tip[1] - wid * 0.2)]
            pygame.draw.polygon(surf, GUNMETAL, pts)
            pygame.draw.polygon(surf, _mix(GUNMETAL, (0, 0, 0), 0.4), pts, 1)
            pygame.draw.line(surf, _mix(GUNMETAL, (210, 216, 226), 0.45),
                             (base[0] - wid * 0.3, base[1] + 2),
                             (tip[0] - wid * 0.3, tip[1] - 3), 1)

    rim = _lobed(cx, cy, r, amp=4.0, jitter=0.7, rnd=rnd)
    pygame.draw.polygon(surf, SCARLET_DEEP, rim)
    body = _lobed(cx, cy, r - 2.4, amp=3.4, jitter=0.5, rnd=rnd)
    pygame.draw.polygon(surf, SCARLET, body)

    # Volume: light from upper-left, so the bead brightens there and the far
    # side sinks.
    vol = pygame.Surface((int(r * 4), int(r * 4)), pygame.SRCALPHA)
    vc = int(r * 2)
    for i in range(int(r * 0.55)):
        t = i / max(1.0, r * 0.55)
        pygame.draw.polygon(vol, (255, 150, 130, int(52 * (1 - t) ** 1.4)),
                            _lobed(vc - 1.4, vc - 1.6, r - 3 - i, amp=3.0), 2)
    for i in range(int(r * 0.4)):
        t = i / max(1.0, r * 0.4)
        pygame.draw.polygon(vol, (70, 12, 12, int(46 * (1 - t) ** 1.2)),
                            _lobed(vc + 1.6, vc + 2.0, r - 2 - i, amp=3.2), 2)
    surf.blit(vol, (cx - vc, cy - vc))

    well = _lobed(cx, cy, r * 0.70, lobes=3, amp=1.2)
    pygame.draw.polygon(surf, _mix(SCARLET, SCARLET_DEEP, 0.34), well)
    pygame.draw.lines(surf, _mix(SCARLET, (0, 0, 0), 0.45), True, well, 1)

    _draw_parrot(surf, cx + 0.9, cy + 1.4, r * 0.030, SCARLET_DEEP)
    _draw_parrot(surf, cx, cy, r * 0.030, SCARLET_LIT)
    _draw_parrot(surf, cx - 0.8, cy - 1.0, r * 0.028,
                 _mix(SCARLET_LIT, (255, 210, 200), 0.5))
    _draw_parrot(surf, cx, cy, r * 0.030, _mix(SCARLET_LIT, SCARLET, 0.45))

    hot = pygame.Surface((int(r * 4), int(r * 4)), pygame.SRCALPHA)
    rect = pygame.Rect(vc - r + 3, vc - r + 3, 2 * (r - 3), 2 * (r - 3))
    pygame.draw.arc(hot, (255, 214, 206, 200), rect,
                    math.radians(96), math.radians(178), 3)
    pygame.draw.arc(hot, (255, 246, 242, 130), rect.inflate(-5, -5),
                    math.radians(108), math.radians(160), 2)
    surf.blit(hot, (cx - vc, cy - vc))
    pygame.draw.circle(surf, (255, 240, 236),
                       (int(cx - r * 0.52), int(cy - r * 0.56)), 2)

    for _ in range(3):
        a = rnd.uniform(0.35, 2.6)
        d = r + rnd.uniform(1.5, 5.0)
        br = rnd.uniform(2.0, 4.2)
        bx, by = cx + d * math.cos(a), cy + d * math.sin(a)
        pygame.draw.circle(surf, SCARLET_DEEP, (int(bx), int(by)), int(br) + 1)
        pygame.draw.circle(surf, SCARLET, (int(bx), int(by)), int(br))


# ── endorsement chits ────────────────────────────────────────────────────────

_PERFIN = {
    "G": ["111", "100", "101", "101", "111"],
    "C": ["111", "100", "100", "100", "111"],
    "S": ["111", "100", "111", "001", "111"],
    "N": ["101", "111", "111", "111", "101"],
}


def _perfin(surf, x, y, letter):
    """Punched initials — the hole shows the dark behind the sheet, with a lit
    lip on the exit side so the paper reads as having thickness."""
    for ry, row in enumerate(_PERFIN[letter]):
        for rx, bit in enumerate(row):
            if bit != "1":
                continue
            px, py = int(x + rx * 4), int(y + ry * 4)
            pygame.draw.circle(surf, (16, 13, 22), (px, py), 2)
            pygame.draw.circle(surf, (250, 249, 247), (px + 1, py + 1), 1)


def _chit(surf, rect, label, phase, reached, seed):
    lay = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    a = 255 if reached else 96
    pygame.draw.rect(lay, (*CHIT, a), (0, 0, rect.w, rect.h), border_radius=2)
    pygame.draw.rect(lay, (*CHIT_EDGE, a), (0, 0, rect.w, rect.h), 1,
                     border_radius=2)
    for i in range(3):
        lay.fill((*CHIT_EDGE, a // 2), (3, rect.h - 13 + i * 4, rect.w - 6, 1))
    surf.blit(lay, rect.topleft)

    if reached:
        _perfin(surf, rect.x + rect.w // 2 - 4, rect.y + 5, label[0])
    txt = _font(7).render(label, True, CHARCOAL if reached else GREY_TEXT)
    txt = pygame.transform.rotate(txt, 90)
    surf.blit(txt, txt.get_rect(center=(rect.centerx, rect.y + 44)))
    pct = _font(6).render("%02d" % round(phase * 100), True,
                          CHARCOAL if reached else GREY_TEXT)
    surf.blit(pct, pct.get_rect(center=(rect.centerx, rect.bottom - 6)))


# ── screen ───────────────────────────────────────────────────────────────────

def _layout(run):
    page = pygame.Rect(14, 40, 336, 556)
    spine_w = 14
    curl_w = 18 if run["day"] > 1 else 0
    gx0 = 42 + (curl_w + 4 if curl_w else 0)
    mx1 = 344
    grid_w = mx1 - 22 - 4 - gx0
    gap = 3
    bw = (grid_w - 3 * gap) // 4
    return dict(page=page, spine_w=spine_w, curl_w=curl_w, gx0=gx0, bw=bw,
                gap=gap, bh=86, row1=106, row2=202, mx0=322, mx1=mx1,
                gutter=12 + curl_w)


def _box_rect(L, idx):
    if idx < 4:
        return pygame.Rect(L["gx0"] + idx * (L["bw"] + L["gap"]), L["row1"],
                           L["bw"], L["bh"])
    row_w = 3 * L["bw"] + 2 * L["gap"]
    full = 4 * L["bw"] + 3 * L["gap"]
    x0 = L["gx0"] + (full - row_w) // 2
    return pygame.Rect(x0 + (idx - 4) * (L["bw"] + L["gap"]), L["row2"],
                       L["bw"], L["bh"])


def render_screen(run):
    L = _layout(run)
    page = L["page"]
    surf = pygame.Surface((W, H))
    surf.fill(BG)

    _caps(surf, "PILLAR %d  ·  DAY %d" % (run["pillars"], run["day"]),
          14, 20, 10, GOLD, tracking=1)
    _caps(surf, "DAY  ·  %s" % run["time"], 350, 20, 10, GOLD, tracking=1,
          anchor="right")

    _cover_and_spine(surf, page, L["spine_w"], run["day"], run["seed"])

    face = pygame.Rect(page.x + L["spine_w"], page.y,
                       page.w - L["spine_w"], page.h)
    surf.blit(_page_stock(face, run["seed"], L["gutter"]), face.topleft)
    pygame.draw.line(surf, STOCK_EDGE, (face.x, face.y), (face.right - 1, face.y))

    # Sheet shading first, then the specular axis over it; unflown boxes take
    # a third, hotter pass below.
    _foil(surf, face, face.centerx - 26, face.centery - 40, 900, 620, 30,
          dark=True)
    _foil(surf, face, face.centerx - 26, face.centery - 40, 900, 150, 46)

    if L["curl_w"]:
        _prev_page_curl(surf, page, L["spine_w"], L["curl_w"], run["seed"] + 7)

    cx0, cx1 = L["gx0"], L["gx0"] + 4 * L["bw"] + 3 * L["gap"]

    _caps(surf, "SKYBIT AVIATION AUTHORITY", cx0, 58, 7, (128, 122, 116),
          tracking=2)
    _caps(surf, "FLIGHT PERMIT", cx0, 74, 15, (46, 42, 40), tracking=2)
    _caps(surf, "No. %05d" % (run["seed"] % 100000), L["mx1"], 74, 8,
          (128, 122, 116), tracking=1, anchor="right")
    pygame.draw.line(surf, HAIRLINE, (cx0, 88), (L["mx1"], 88), 1)
    _caps(surf, "PHASE ENTRY RECORD", cx0, 97, 7, (120, 114, 108), tracking=2)
    _caps(surf, "07 BOXES", cx1, 97, 7, (150, 145, 140), tracking=1,
          anchor="right")

    death = run["phase"]
    flown_idx = 0
    for i, (start, _n) in enumerate(PHASE_BOUNDARIES):
        if death >= start:
            flown_idx = i

    unflown_rects = []
    for i, name in enumerate(PHASE_NAMES):
        rect = _box_rect(L, i)
        flown = i <= flown_idx
        # The box interior is never repainted — it *is* the sheet, so the
        # shading and specular axis run straight through it. A cancelled box
        # only picks up the handling soil that comes with being stamped.
        if flown:
            soil = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            soil.fill((104, 92, 74, 30))
            surf.blit(soil, rect.topleft)
        pygame.draw.rect(surf, HAIRLINE, rect, 1)
        pygame.draw.rect(surf, BAND, (rect.x + 1, rect.y + 1, rect.w - 2, 11))
        pygame.draw.line(surf, HAIRLINE, (rect.x + 1, rect.y + 12),
                         (rect.right - 2, rect.y + 12), 1)
        _caps(surf, "%02d" % (i + 1), rect.x + 4, rect.y + 7, 6, CHARCOAL,
              tracking=1)
        _caps(surf, "%02d-%02d" % (round(PHASE_BOUNDARIES[i][0] * 100),
                                   round(PHASE_END[i] * 100)),
              rect.right - 4, rect.y + 7, 6, (140, 134, 128), tracking=0,
              anchor="right")

        l1, l2 = PHASE_LINES[name]
        col = CHARCOAL if flown else GREY_TEXT
        if l2:
            _caps(surf, l1, rect.centerx, rect.bottom - 20, 9, col, tracking=1,
                  anchor="center")
            _caps(surf, l2, rect.centerx, rect.bottom - 9, 9, col, tracking=1,
                  anchor="center")
        else:
            _caps(surf, l1, rect.centerx, rect.bottom - 14, 9, col, tracking=1,
                  anchor="center")
        if not flown:
            unflown_rects.append(rect)

    for rect in unflown_rects:
        _foil(surf, rect.inflate(-2, -2), rect.centerx - 4, rect.centery - 8,
              260, 84, 150)

    # A run barely into its first phase has not earned a cancellation; a gold
    # tab carries the "you are here" instead, since a hairline arc alone is
    # too small to find.
    tiny = death < 0.06
    for i, name in enumerate(PHASE_NAMES):
        if i > flown_idx:
            continue
        rect = _box_rect(L, i)
        span = max(1e-6, PHASE_END[i] - PHASE_BOUNDARIES[i][0])
        prog = (death - PHASE_BOUNDARIES[i][0]) / span if i == flown_idx else 1.0
        partial = prog if (i == flown_idx and prog < 0.25) else None
        # Cachets are placed by hand, so none of them sits dead centre. The
        # last one is nudged off the seam on purpose: the seal is meant to
        # overlap the final stamp, not erase it.
        jr = random.Random(run["seed"] + i * 31)
        jx, jy = jr.uniform(-4, 4), jr.uniform(-3, 3)
        if i == flown_idx:
            jx -= 10
        st = _cachet(name, 25, run["seed"] + i * 31, PHASE_INK[name], partial)
        surf.blit(st, st.get_rect(center=(rect.centerx + jx,
                                          rect.centery - 3 + jy)))

    if tiny:
        r0 = _box_rect(L, 0)
        pygame.draw.polygon(surf, GOLD, [
            (r0.x + 1, r0.y + 13), (r0.x + 13, r0.y + 13), (r0.x + 1, r0.y + 25)])
        pygame.draw.line(surf, _mix(GOLD, (120, 84, 20), 0.5),
                         (r0.x + 13, r0.y + 13), (r0.x + 1, r0.y + 25), 1)

    # Right margin: one endorsement chit per event, punched only where the run
    # actually reached it.
    reached_n = 0
    for k, (ph, label) in enumerate(EVENT_MARKERS):
        rect = pygame.Rect(L["mx0"] + 1, L["row1"] + k * 90, L["mx1"] - L["mx0"] - 2, 62)
        reached = (run["day"] > 1) or (ph <= death)
        reached_n += 1 if reached else 0
        _chit(surf, rect, label, ph, reached, run["seed"] + k)
    _caps(surf, "END", L["mx0"] + (L["mx1"] - L["mx0"]) // 2, 97, 6,
          (150, 145, 140), tracking=1, anchor="center")

    pygame.draw.line(surf, HAIRLINE, (cx0, 302), (L["mx1"], 302), 1)
    leader = "ENTRY %02d%%  ·  PILLAR %d" % (round(death * 100), run["pillars"])
    lw = _caps(surf, leader, cx0, 314, 9, (58, 54, 52), tracking=1)
    dots = pygame.Surface((W, H), pygame.SRCALPHA)
    x = cx0 + lw + 8
    while x < cx1 - 4:
        dots.fill((110, 104, 98, 150), (int(x), 313, 2, 2))
        x += 6
    surf.blit(dots, (0, 0))

    _caps(surf, "PARTICULARS OF FLIGHT", cx0, 332, 7, (120, 114, 108),
          tracking=2)

    hero = _font(58).render(str(run["pillars"]), True, (36, 33, 32))
    hr = hero.get_rect(center=((cx0 + cx1) // 2, 372))
    surf.blit(_fade(hero, 60), (hr.x + 2, hr.y + 3))
    surf.blit(hero, hr.topleft)
    _caps(surf, "PILLARS CLEARED", (cx0 + cx1) // 2, 406, 9, (110, 104, 98),
          tracking=4, anchor="center")

    rows = [("DAY", str(run["day"])), ("ELAPSED", run["time"]),
            ("TERMINATED BY", run["cause"])]
    for k, (lab, val) in enumerate(rows):
        y = 432 + k * 22
        lw2 = _caps(surf, lab, cx0, y, 8, (128, 122, 116), tracking=2)
        d2 = pygame.Surface((W, H), pygame.SRCALPHA)
        x = cx0 + lw2 + 6
        vw = _caps_w(val, 10, 1)
        while x < cx1 - vw - 6:
            d2.fill((150, 144, 138, 140), (int(x), y - 1, 2, 2))
            x += 6
        surf.blit(d2, (0, 0))
        _caps(surf, val, cx1, y, 10, (46, 42, 40), tracking=1, anchor="right")

    pygame.draw.line(surf, HAIRLINE, (cx0, 494), (L["mx1"], 494), 1)
    _caps(surf, "ENDORSEMENTS", cx0, 506, 7, (120, 114, 108), tracking=2)
    _caps(surf, "%02d / %02d" % (reached_n, len(EVENT_MARKERS)), cx1, 506, 8,
          (58, 54, 52), tracking=1, anchor="right")
    for k, (ph, label) in enumerate(EVENT_MARKERS):
        bx = cx0 + k * 62
        reached = (run["day"] > 1) or (ph <= death)
        br = pygame.Rect(bx, 518, 9, 9)
        pygame.draw.rect(surf, HAIRLINE, br, 1)
        if reached:
            pygame.draw.rect(surf, (96, 92, 88), br.inflate(-4, -4))
        _caps(surf, label, bx + 13, 523, 6,
              CHARCOAL if reached else GREY_TEXT, tracking=1)

    # Margin codes stay charcoal — the page carries no second red.
    _caps(surf, "·".join(["%03d" % ((run["seed"] * (i + 3)) % 1000)
                          for i in range(3)]),
          cx0, 556, 6, (128, 122, 116), tracking=1)

    pygame.draw.line(surf, HAIRLINE, (cx0, 566), (L["mx1"], 566), 1)
    _caps(surf, "PAGE %d" % run["day"], cx0, 578, 8, (100, 95, 90), tracking=2)
    _caps(surf, "DAY %d" % run["day"], cx1, 578, 8, (100, 95, 90), tracking=2,
          anchor="right")

    _cover_peel(surf, page, L["spine_w"])

    # The seal lands on the seam between the last cancelled box and the first
    # untouched one — the document closes exactly where the run stopped. Its
    # radius is held just under a box width so it straddles two boxes and no
    # more; a wider seal swallows the stamp it is supposed to be sitting on.
    a = _box_rect(L, flown_idx)
    if flown_idx < len(PHASE_NAMES) - 1:
        b = _box_rect(L, flown_idx + 1)
        seam_x = (a.right + b.x) / 2 if a.y == b.y else a.centerx
    else:
        seam_x = a.right
    seal = (seam_x, a.centery)
    _wax_seal(surf, seal[0], seal[1], 33, run["seed"] + 3)

    back = pygame.Rect(0, 604, 98, 28)
    back.centerx = W // 2
    pygame.draw.rect(surf, (20, 17, 26), back, border_radius=4)
    pygame.draw.rect(surf, GOLD, back, 1, border_radius=4)
    _caps(surf, "BACK", back.centerx, back.centery, 11, GOLD, tracking=3,
          anchor="center")
    return surf, seal


# ── detail column ────────────────────────────────────────────────────────────

def _detail_column(w, h, run_a_surf, run_a_seal):
    surf = pygame.Surface((w, h))
    surf.fill((20, 17, 26))
    pygame.draw.rect(surf, (52, 46, 40), (0, 0, w, h), 1)
    _caps(surf, "CONSTRUCTION  ·  SCALE", 12, 16, 10, GOLD, tracking=2)

    _caps(surf, "WAX SEAL  ·  2x", 12, 38, 8, (150, 145, 140), tracking=2)
    plate = pygame.Surface((176, 176))
    plate.fill(STOCK)
    ros = _rosette()
    plate.blit(ros, ros.get_rect(center=(88, 88)))
    _wax_seal(plate, 88, 84, 68, 4024)
    surf.blit(plate, (12, 50))
    notes = ["LOBED RIM r+4sin8t", "HOT ARC UPPER-LEFT",
             "EMBOSSED PARROT CHOP", "GUNMETAL RIBBON TAILS",
             "WAX SPATTER, 3 DROPS"]
    for i, n in enumerate(notes):
        _caps(surf, n, 200, 74 + i * 16, 7, (168, 162, 152), tracking=1)
        pygame.draw.circle(surf, SCARLET, (192, 74 + i * 16), 2)

    _caps(surf, "CACHET  ·  FULL / HAIRLINE", 12, 240, 8, (150, 145, 140),
          tracking=2)
    for i, (lab, part) in enumerate((("FLOWN", None), ("03% ARC", 0.134))):
        p = pygame.Surface((92, 92))
        p.fill(STOCK)
        p.blit(ros, ros.get_rect(center=(46, 46)))
        st = _cachet("DAY", 34, 4021 + i, PHASE_INK["DAY"], part)
        p.blit(st, st.get_rect(center=(46, 46)))
        surf.blit(p, (12 + i * 100, 252))
        _caps(surf, lab, 12 + i * 100 + 46, 352, 7, (168, 162, 152),
              tracking=1, anchor="center")
    tabp = pygame.Surface((92, 92))
    tabp.fill(STOCK)
    pygame.draw.rect(tabp, HAIRLINE, (14, 14, 64, 64), 1)
    pygame.draw.polygon(tabp, GOLD, [(15, 15), (27, 15), (15, 27)])
    _caps(tabp, "GOLD TAB", 46, 60, 7, CHARCOAL, tracking=1, anchor="center")
    surf.blit(tabp, (212, 252))
    _caps(surf, "12px", 258, 352, 7, (168, 162, 152), tracking=1,
          anchor="center")

    _caps(surf, "PHASE INK  ·  CLAMPED SHORT OF SCARLET", 12, 372, 8,
          (150, 145, 140), tracking=1)
    for i, name in enumerate(PHASE_NAMES):
        x = 12 + i * 45
        pygame.draw.rect(surf, SKY_MID[name], (x, 384, 40, 12))
        pygame.draw.rect(surf, CLAMPED_SKY[name], (x, 396, 40, 12))
        pygame.draw.rect(surf, PHASE_INK[name], (x, 408, 40, 16))
        _caps(surf, name.split(" ")[0][:6], x + 20, 430, 6, (168, 162, 152),
              tracking=0, anchor="center")
    for i, lab in enumerate(("SKY", "CLAMP", "INK")):
        _caps(surf, lab, 332, 390 + i * 12, 6, (110, 104, 98), tracking=0,
              anchor="right")

    _caps(surf, "SCARLET AUDIT", 12, 452, 8, (150, 145, 140), tracking=2)
    for i, (c, lab) in enumerate(((SCARLET, "SEAL ONLY"),
                                  (GUNMETAL, "RIBBON TAILS"),
                                  (CHARCOAL, "MARGIN CODES"))):
        pygame.draw.rect(surf, c, (12 + i * 108, 464, 22, 22))
        _caps(surf, lab, 38 + i * 108, 475, 6, (168, 162, 152), tracking=0)

    stray = _audit_scarlet(run_a_surf, run_a_seal)
    _caps(surf, "STRAY SCARLET OUTSIDE SEAL: %d px" % stray, 12, 496, 7,
          (120, 200, 130) if stray == 0 else (230, 160, 90), tracking=1)

    _caps(surf, "PAGE STOCK  ·  3x", 12, 516, 8, (150, 145, 140), tracking=2)
    crop = pygame.Surface((104, 28))
    crop.fill(STOCK)
    crop.blit(ros, ros.get_rect(center=(30, 8)))
    crop.blit(ros, ros.get_rect(center=(84, 24)))
    _foil(crop, crop.get_rect(), 52, 14, 240, 60, 30, dark=True)
    _foil(crop, crop.get_rect(), 52, 14, 240, 26, 90)
    surf.blit(pygame.transform.scale(crop, (312, 84)), (12, 528))
    _caps(surf, "VALUE 244  ·  GUILLOCHE 4%  ·  FOIL SWEEP", 12, 620, 7,
          (168, 162, 152), tracking=1)
    _caps(surf, "SEAL 33r  vs  CACHET 25r  —  the stop outweighs the entry",
          12, 632, 7, (140, 134, 126), tracking=1)
    return surf


def _audit_scarlet(screen, seal, pad=10):
    """Proof that scarlet is spent once: nothing red-dominant may exist outside
    the seal's footprint."""
    cx, cy = seal
    r2 = (33 + pad) ** 2
    n = 0
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                continue
            cr, cg, cb = screen.get_at((x, y))[:3]
            if cr > 120 and cr - cg > 60 and cr - cb > 60:
                n += 1
    return n


# ── review sheet ─────────────────────────────────────────────────────────────

def build_sheet(screens, seals):
    col_w = 348
    sw = 12 + W + 14 + W + 14 + col_w + 12
    sh = 12 + 26 + 12 + H + 16
    sheet = pygame.Surface((sw, sh))
    sheet.fill((7, 6, 12))
    _caps(sheet, "SEALED PERMIT  ·  FLIGHT LOG  ·  ROUND 1", 12, 22, 15, GOLD,
          tracking=3)
    _caps(sheet, "permit booklet, spine left, cover peeled  —  flown phases "
                 "cancelled by cachet, run stopped by one wax seal",
          12, 40, 8, (150, 144, 134), tracking=1)
    caps = ["RUN A  ·  PILLAR 25  ·  DAY 1  ·  ENTRY 18%  ·  GEYSER",
            "RUN B  ·  PILLAR 180  ·  DAY 2  ·  ENTRY 03%  ·  PAGE TURN"]
    for i, (scr, cap) in enumerate(zip(screens, caps)):
        x = 12 + i * (W + 14)
        _caps(sheet, cap, x, 40, 8, (168, 160, 142), tracking=1)
        sheet.blit(scr, (x, 50))
    sheet.blit(_detail_column(col_w, H, screens[0], seals[0]),
               (12 + 2 * (W + 14), 50))
    return sheet


def main():
    rendered = [render_screen(r) for r in RUNS]
    screens = [s for s, _ in rendered]
    seals = [c for _, c in rendered]
    sheet = build_sheet(screens, seals)
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(sheet, path)
    print("saved", path, sheet.get_size())
    probes = (("sheet bg", (4, 700)), ("page stock A", (240, 500)),
              ("stock B", (610, 500)), ("seal core A", (112, 200)),
              ("cachet A", (100, 175)), ("spine A", (24, 400)),
              ("detail col", (900, 60)))
    for name, pos in probes:
        print("  %-13s %-11s -> %s" % (name, pos, sheet.get_at(pos)[:3]))
    for r, s, c in zip(RUNS, screens, seals):
        print("  %s seal@%s stray scarlet outside seal: %d"
              % (r["tag"], (int(c[0]), int(c[1])), _audit_scarlet(s, c)))


if __name__ == "__main__":
    main()
