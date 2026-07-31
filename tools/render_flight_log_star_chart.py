#!/usr/bin/env python3
"""
star chart  ·  flight-log screen  ·  round 1

A run is plotted the way an almanac plots a constellation: one star per
pillar strung along a seeded curve, the ones you reached joined into an
asterism, the ones you didn't left as bare survey rings in the dark.

Five ideas carry it:

1. NO CONTAINER. The sky is the screen — indigo to black, edge to edge. A
   panel border would turn a keepsake into a dialog, and the whole point of
   a star chart is that it has no frame, only a sky.
2. REACHED vs UNREACHED DIFFERS BY SIZE AND FILL, never by hue alone. A
   reached star is a filled disc with a halo; an unreached one is a hollow
   ring at half the radius. That survives a greyscale read, a squint read
   and a colourblind read, none of which a gold/grey recolour would.
3. ONE HERO. The pillar numeral is the only large object on the canvas.
   Everything else — chart, labels, phase ring — is authored to sit under
   it. The phase ring in particular is pinned to the rim at alpha <= 40 so
   it can never cross the numeral or compete for the first fixation.
4. ONE SCARLET. The death burst is the single warm-red object in the whole
   frame, which makes "where did it end" answerable in one saccade without
   a callout doing the work.
5. THE EMPTY SKY IS THE POINT. Unreached stars are drawn — they are the
   sky the curve is heading into — but nothing ghosts a would-have-been
   path through them. No line means no promise.

Scale rule: one star per pillar to 40, then one per five, with a brighter
anchor every 50. That keeps a 25-pillar run and a 250-pillar chart at the
same comfortable ~14px star spacing instead of letting a long run collapse
into a solid bead of light. Note the compression is honest but non-linear:
run A reached 25 of 139 charted pillars (18%) yet lights 41% of the plotted
stars, because the far field is sampled five times coarser.

The curve seed is the pillar count, so two runs genuinely chart as two
different constellations rather than one shape with a different amount of
it coloured in.
"""
import os
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color, lerp_color_multi

W, H = 360, 640
SS = 4                      # chart layer supersample: 4 lets a 1px ring keep a hole

FIELD_Y0, FIELD_Y1 = 46, 430
FIELD_X0, FIELD_X1 = 26, 334
CX = 180

FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
_fonts: dict = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


# ── palette ──────────────────────────────────────────────────────────────────
SHEET_BG = (8, 8, 20)
GOLD = (240, 192, 64)
GOLD_DIM = (216, 184, 85)
SCARLET = (172, 40, 32)
CREAM = (232, 228, 216)
STAR_WHITE = (250, 244, 228)
COOL = (126, 140, 178)

SKY_STOPS = [
    (0.00, (20, 25, 62)),
    (0.34, (13, 15, 40)),
    (0.68, (9, 10, 25)),
    (1.00, (5, 5, 14)),
]

PHASE_BOUNDARIES = [
    (0.000, "DAY"),
    (0.231, "GOLDEN HOUR"),
    (0.363, "SUNSET"),
    (0.513, "DUSK"),
    (0.644, "NIGHT"),
    (0.794, "PREDAWN"),
    (0.906, "SUNRISE"),
]

# Landmark pillar anchors. The geyser field is phase-gated rather than
# pillar-gated, so its pillar is whatever pillar that run was on when the
# phase clock hit 0.156 — it moves between runs, and it should.
GEYSER_PHASE = 0.156
LANDMARKS = [
    ("GEYSER FIELD", None),     # resolved per run from GEYSER_PHASE
    ("LAMPS", 50),
    ("CLOWN", 65),
    ("RAIN", 70),
    ("SNOW", 139),
]


class Run:
    def __init__(self, tag, pillars, phase, laps, day, clock, cause):
        self.tag = tag
        self.pillars = pillars
        self.phase = phase
        self.laps = laps            # completed day cycles before `phase`
        self.day = day
        self.clock = clock
        self.cause = cause

    @property
    def total_phase(self):
        return self.laps + self.phase

    def geyser_pillar(self):
        """Pillar index at which this run first crossed the geyser gate."""
        return max(1, int(round(self.pillars * GEYSER_PHASE / self.total_phase)))

    def landmarks(self):
        out = []
        for name, pillar in LANDMARKS:
            p = self.geyser_pillar() if pillar is None else pillar
            out.append((name, p))
        return out


RUN_A = Run("RUN A", 25, 0.184, 0, 1, "0:47", "GEYSER")
RUN_B = Run("RUN B", 180, 0.031, 1, 2, "5:30", "SNOW")


# ── chart sampling ───────────────────────────────────────────────────────────

def chart_span(run):
    """The horizon this chart is drawn out to.

    It steps rather than hugging the run, so a good run visibly eats into a
    fixed sky instead of the sky quietly growing to keep it at 20%.
    """
    need = run.pillars + 40
    for milestone in (140, 250, 400, 600, 900):
        if milestone >= need:
            return milestone
    return 1200


def chart_pillars(run):
    span = chart_span(run)
    ps = set(range(1, min(span, 40) + 1))
    p = 45
    while p <= span:
        ps.add(p)
        p += 5
    for _name, lp in run.landmarks():
        if lp <= span:
            ps.add(lp)
    ps.add(span)
    return sorted(ps), span


def magnitude(pillar, span):
    """Radius of a reached star. Log rather than linear: a linear ramp made
    pillar 250 a blob wider than the gap between it and its neighbour."""
    return 3.0 + 1.35 * math.log10(1.0 + pillar / 11.0)


def is_anchor(pillar):
    return pillar % 50 == 0


# ── the seeded curve ─────────────────────────────────────────────────────────

def curve_points(run, pillars):
    """Star positions: a smooth S spine plus a coherent lateral wander.

    The wander is not decoration. On the raw spine consecutive stars sit
    ~11px apart along a near-vertical line, so a 4px disc with a 2px line
    break leaves nothing to draw; the lateral term lifts real neighbour
    spacing to ~16px and, more importantly, makes the joins change direction
    star to star — which is what makes a chain of dots read as a
    constellation rather than as a dotted rule.
    """
    rng = random.Random(run.pillars)
    lobes = rng.uniform(2.3, 3.0)
    amp = rng.uniform(84, 96)
    ph = rng.uniform(0, math.tau)
    skew = rng.choice((-1, 1))
    a1, k1, q1 = rng.uniform(7, 11), rng.uniform(0.85, 1.25), rng.uniform(0, math.tau)
    a2, k2, q2 = rng.uniform(12, 20), rng.uniform(0.16, 0.30), rng.uniform(0, math.tau)

    n = len(pillars)
    pts = []
    for i in range(n):
        t = i / max(1, n - 1)
        x = CX + skew * amp * math.sin(t * math.pi * lobes + ph)
        y = FIELD_Y0 + (FIELD_Y1 - FIELD_Y0) * t
        x += a1 * math.sin(i * k1 + q1) + a2 * math.sin(i * k2 + q2)
        y += 2.4 * math.sin(i * k1 * 1.7 + q1)
        pts.append((min(FIELD_X1, max(FIELD_X0, x)), y))
    return pts


# ── drawing helpers ──────────────────────────────────────────────────────────

_glow_cache: dict = {}


def glow(radius, color, peak, falloff=2.0):
    """Additive halo with the falloff premultiplied into RGB.

    BLEND_ADD ignores source alpha, so an alpha-ramped disc blits as a flat
    hard-edged plate; baking the ramp into the channels is the only way to
    keep it soft.
    """
    key = (radius, color, peak, falloff)
    if key not in _glow_cache:
        size = radius * 2 + 2
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        c = radius + 1
        for r in range(radius, 0, -1):
            f = (1 - (r / radius) ** falloff) * (peak / 255.0)
            pygame.draw.circle(s, (int(color[0] * f), int(color[1] * f),
                                   int(color[2] * f), 255), (c, c), r)
        _glow_cache[key] = s
    return _glow_cache[key]


def add_glow(surf, cx, cy, radius, color, peak):
    g = glow(radius, color, peak)
    surf.blit(g, (int(cx) - radius - 1, int(cy) - radius - 1),
              special_flags=pygame.BLEND_ADD)


def smallcaps(s, cap=11, small=8, color=(255, 255, 255), track=0.6):
    """Faked small caps: the first letter of each word at cap size, the rest
    of the (already uppercase) string at small size, baselines aligned.

    LiberationSans-Bold has no true small-cap set, and scaling a rendered
    cap down produces a stem weight that no longer matches the initial.
    Two sizes of the same cut keeps the stems honest.
    """
    fc, fs = font(cap), font(small)
    asc = fc.get_ascent()
    parts, fresh = [], True
    for ch in s:
        if not ch.isalpha():
            parts.append((ch, fs))
            fresh = True
            continue
        parts.append((ch, fc if fresh else fs))
        fresh = False

    glyphs = [(f.render(ch, True, color), asc - f.get_ascent()) for ch, f in parts]
    w = sum(g.get_width() for g, _ in glyphs) + track * max(0, len(glyphs) - 1)
    img = pygame.Surface((max(1, int(math.ceil(w))), fc.get_height()), pygame.SRCALPHA)
    x = 0.0
    for g, dy in glyphs:
        img.blit(g, (int(round(x)), dy))
        x += g.get_width() + track
    return img


def outline_of(src, color, alpha):
    """1px hollow version of a rendered word.

    An unreached landmark has to read as *not yet earned* at a glance. Going
    hollow does that structurally; going grey would only have done it by
    hue, which is the one axis this screen refuses to lean on.
    """
    mask = pygame.mask.from_surface(src, threshold=40)
    sil = mask.to_surface(setcolor=(*color, alpha), unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface((src.get_width() + 2, src.get_height() + 2), pygame.SRCALPHA)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                out.blit(sil, (1 + dx, 1 + dy))
    hole = mask.to_surface(setcolor=(0, 0, 0, 0), unsetcolor=(255, 255, 255, 255))
    out.blit(hole, (1, 1), special_flags=pygame.BLEND_RGBA_MULT)
    return out


def alpha_line(surf, rgba, p0, p1, width=1):
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


# ── sky ──────────────────────────────────────────────────────────────────────

def draw_sky(surf):
    for y in range(H):
        surf.fill(lerp_color_multi(SKY_STOPS, y / (H - 1)), pygame.Rect(0, y, W, 1))


def draw_dust(surf, seed):
    """Sub-chart field stars. They are what makes the sky full-bleed: without
    them the lower third — where the numeral sits — is a dead flat plate and
    the composition grows an implied panel edge at the chart's last star."""
    rng = random.Random(seed * 7919 + 13)
    lay = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(420):
        x, y = rng.randrange(W), rng.randrange(H)
        # A soft diagonal over-density reads as a galactic band and gives the
        # empty half of the frame some structure to be empty against.
        band = math.exp(-((y - 0.9 * x - 140) / 190.0) ** 2)
        if rng.random() > 0.22 + 0.62 * band:
            continue
        a = int(rng.uniform(14, 30) + 26 * band * rng.random())
        pygame.draw.circle(lay, (206, 214, 240, a), (x, y), 1 if rng.random() < 0.82 else 2)
    surf.blit(lay, (0, 0))


# ── phase ring, pinned to the rim ────────────────────────────────────────────

_rim_mask = None


def rim_mask():
    """Alpha stencil that keeps only a ~20px border band, feathered inward.

    Cheaper and more reliable than trying to pick arc angles that happen to
    graze the edges: whatever the ring does in the middle of the canvas is
    simply not there.
    """
    global _rim_mask
    if _rim_mask is None:
        m = pygame.Surface((W, H), pygame.SRCALPHA)
        m.fill((0, 0, 0, 0))
        for d in range(34, -1, -1):
            a = 255 if d <= 20 else int(255 * (1.0 - (d - 20) / 14.0))
            pygame.draw.rect(m, (255, 255, 255, a),
                             pygame.Rect(d, d, W - 2 * d, H - 2 * d), 1)
        _rim_mask = m
    return _rim_mask


RING_C = (180, 316)
RING_A, RING_B = 170, 302     # inscribed ellipse: only its four extremes reach the rim


def ring_pt(phase, scale=1.0):
    th = -math.pi / 2 + math.tau * (phase % 1.0)
    return (RING_C[0] + RING_A * scale * math.cos(th),
            RING_C[1] + RING_B * scale * math.sin(th))


def draw_phase_ring(surf, run):
    lay = pygame.Surface((W, H), pygame.SRCALPHA)

    ring = [ring_pt(i / 360.0) for i in range(361)]
    pygame.draw.lines(lay, (*COOL, 34), False, ring, 1)

    for frac, _name in PHASE_BOUNDARIES:
        p0, p1 = ring_pt(frac, 0.965), ring_pt(frac, 1.035)
        pygame.draw.line(lay, (*COOL, 40), p0, p1, 1)

    # Travelled arc. A wrapped run paints the whole ring, so "a full day was
    # flown" is legible from the rim alone without a second readout.
    steps = max(2, int(run.total_phase * 360))
    trav = [ring_pt(run.total_phase * i / steps) for i in range(steps + 1)]
    pygame.draw.lines(lay, (*GOLD, 40), False, trav, 1)

    ex, ey = ring_pt(run.total_phase)
    pygame.draw.circle(lay, (*GOLD, 40), (int(ex), int(ey)), 3)
    pygame.draw.circle(lay, (*GOLD, 40), (int(ex), int(ey)), 5, 1)

    lay.blit(rim_mask(), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(lay, (0, 0))


def draw_phase_labels(surf, cartouche_rect):
    """Only the boundaries whose tick actually lands in the rim band get a
    word; the rest keep the hairline and lose the label. A leader out to a
    tick hiding under the stencil would be a promise the ring can't keep."""
    for frac, name in PHASE_BOUNDARIES:
        x, y = ring_pt(frac)
        if not (0 <= x < W and 0 <= y < H):
            continue
        if min(x, y, W - 1 - x, H - 1 - y) > 24:
            continue
        img = font(7).render(name, True, COOL)
        img.set_alpha(38)
        r = img.get_rect()
        r.center = (int(x + (12 if x < CX else -12) * (0 if abs(y - RING_C[1]) > 240 else 1)),
                    int(y + (11 if y < RING_C[1] else -11)))
        r.clamp_ip(pygame.Rect(3, 3, W - 6, H - 6))
        if r.colliderect(cartouche_rect):
            continue
        surf.blit(img, r)


# ── the chart ────────────────────────────────────────────────────────────────

def draw_chart(surf, run, pillars, pts, span):
    reached = [p <= run.pillars for p in pillars]
    death_i = max(i for i, r in enumerate(reached) if r)

    # Halos go down natively and first: run additively over the vector layer
    # instead and they wash the asterism's own weight straight out.
    for i, (x, y) in enumerate(pts):
        if not reached[i]:
            continue
        t = i / max(1, len(pts) - 1)
        add_glow(surf, x, y, 6, GOLD, int(38 + 30 * t))
    dx, dy = pts[death_i]
    add_glow(surf, dx, dy, 9, SCARLET, 76)

    ss = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    k = SS

    def P(pt):
        return (pt[0] * k, pt[1] * k)

    # Asterism: reached pairs only, each segment stopping 2px short of both
    # discs. The gap is what keeps a 4px star reading as a star instead of
    # as a thickening in a rule.
    for i in range(death_i):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        r0 = magnitude(pillars[i], span)
        r1 = magnitude(pillars[i + 1], span)
        d = math.hypot(x1 - x0, y1 - y0)
        cut0, cut1 = r0 + 2.0, r1 + 2.0
        if d <= cut0 + cut1 + 1.2:
            continue
        ux, uy = (x1 - x0) / d, (y1 - y0) / d
        pygame.draw.line(ss, (*GOLD_DIM, 175),
                         P((x0 + ux * cut0, y0 + uy * cut0)),
                         P((x1 - ux * cut1, y1 - uy * cut1)), k)

    for i, (x, y) in enumerate(pts):
        anchor = is_anchor(pillars[i])
        if reached[i]:
            if i == death_i:
                continue
            r = magnitude(pillars[i], span) + (0.8 if anchor else 0.0)
            pygame.draw.circle(ss, (*GOLD_DIM, 255), (int(x * k), int(y * k)), int(r * k))
            pygame.draw.circle(ss, (*STAR_WHITE, 255), (int(x * k), int(y * k)),
                               int((r - 1.0) * k))
            if anchor:
                for a in range(4):
                    th = math.radians(a * 90 + 45)
                    c0, c1 = r + 1.4, r + 5.2
                    pygame.draw.line(ss, (*GOLD, 210),
                                     P((x + math.cos(th) * c0, y + math.sin(th) * c0)),
                                     P((x + math.cos(th) * c1, y + math.sin(th) * c1)), k)
        else:
            t = i / max(1, len(pts) - 1)
            r = 1.5 + 0.5 * t                      # stays <= 2px, still ramps
            a = int(78 + 62 * t) + (58 if anchor else 0)
            pygame.draw.circle(ss, (*COOL, min(255, a)), (int(x * k), int(y * k)),
                               int(r * k), k - 1)
            if anchor:
                for ax in range(4):
                    th = math.radians(ax * 90)
                    c0, c1 = r + 1.6, r + 3.6
                    pygame.draw.line(ss, (*COOL, 150),
                                     P((x + math.cos(th) * c0, y + math.sin(th) * c0)),
                                     P((x + math.cos(th) * c1, y + math.sin(th) * c1)), k - 1)

    draw_death_burst(ss, pts[death_i], k)

    surf.blit(pygame.transform.smoothscale(ss, (W, H)), (0, 0))
    return death_i


def draw_death_burst(ss, pt, k):
    """Four long rays on the cardinals, four short on the diagonals, tight
    white core. Tapered triangles rather than lines — a burst built from
    even-width strokes reads as a plus sign, not as a star."""
    x, y = pt
    for a in range(8):
        th = math.radians(a * 45)
        long_ray = (a % 2 == 0)
        length = 11.5 if long_ray else 6.0
        half = 1.7 if long_ray else 1.3
        ux, uy = math.cos(th), math.sin(th)
        px, py = -uy, ux
        pygame.draw.polygon(ss, (*SCARLET, 255), [
            ((x + px * half) * k, (y + py * half) * k),
            ((x - px * half) * k, (y - py * half) * k),
            ((x + ux * length) * k, (y + uy * length) * k),
        ])
    pygame.draw.circle(ss, (*SCARLET, 255), (int(x * k), int(y * k)), int(3.4 * k))
    pygame.draw.circle(ss, (255, 246, 240, 255), (int(x * k), int(y * k)), int(1.9 * k))


# ── labels ───────────────────────────────────────────────────────────────────

def place_labels(surf, run, pillars, pts, death_i):
    marks = {p: name for name, p in run.landmarks()}
    placed = []

    def fit(rect):
        for _ in range(30):
            hit = next((r for r in placed if rect.colliderect(r.inflate(7, 5))), None)
            if hit is None:
                return rect
            rect.y = hit.bottom + 4
            if rect.bottom > FIELD_Y1 + 16:
                break
        rect.bottom = min(rect.bottom, FIELD_Y1 + 16)
        for _ in range(30):
            hit = next((r for r in placed if rect.colliderect(r.inflate(7, 5))), None)
            if hit is None:
                break
            rect.y = hit.top - rect.height - 4
        return rect

    for i, pillar in enumerate(pillars):
        name = marks.get(pillar)
        if name is None:
            continue
        lit = pillar <= run.pillars
        x, y = pts[i]
        body = smallcaps(name, 11, 8, (255, 255, 255) if not lit else GOLD, 0.7)
        img = body if lit else outline_of(body, COOL, 178)
        right = x < CX
        rect = img.get_rect()
        rect.centery = int(y)
        if right:
            rect.left = int(x + 13)
        else:
            rect.right = int(x - 13)
        rect.clamp_ip(pygame.Rect(6, FIELD_Y0 - 8, W - 12, FIELD_Y1 - FIELD_Y0 + 26))
        rect = fit(rect)
        placed.append(rect)

        lead_a = (int(x + (7 if right else -7)), int(y))
        lead_b = (rect.left - 4, rect.centery) if right else (rect.right + 4, rect.centery)
        alpha_line(surf, (*GOLD_DIM, 120) if lit else (*COOL, 76), lead_a, lead_b, 1)
        surf.blit(img, rect)

    # Anchor pillar numbers — the chart's own scale. Suppressed where a
    # landmark already owns the star, so no dot carries two readouts.
    for i, pillar in enumerate(pillars):
        if not is_anchor(pillar) or pillar in marks:
            continue
        x, y = pts[i]
        img = font(7).render(str(pillar), True, COOL)
        img.set_alpha(96)
        rect = img.get_rect()
        rect.center = (int(x + (11 if x < CX else -11)), int(y - 9))
        rect.clamp_ip(pygame.Rect(4, FIELD_Y0 - 10, W - 8, FIELD_Y1 - FIELD_Y0 + 24))
        if any(rect.colliderect(r.inflate(4, 3)) for r in placed):
            continue
        placed.append(rect)
        surf.blit(img, rect)

    draw_death_callout(surf, run, pts, death_i, placed)


def draw_death_callout(surf, run, pts, death_i, placed):
    """Hung on whichever side of the curve the neighbouring landmark isn't,
    so the two labels that describe the same few pillars never stack."""
    x, y = pts[death_i]
    near = [r for r in placed if abs(r.centery - y) < 40]
    if near:
        right = sum(1 for r in near if r.centerx > x) < len(near) / 2.0
    else:
        right = x < CX

    l1 = smallcaps("ENDED", 10, 8, CREAM, 0.9)
    l2 = smallcaps(run.cause, 9, 7, GOLD_DIM, 0.9)
    bw = max(l1.get_width(), l2.get_width())
    bh = l1.get_height() + l2.get_height() - 2
    box = pygame.Rect(0, 0, bw, bh)
    box.centery = int(y)
    if right:
        box.left = int(x + 15)
    else:
        box.right = int(x - 15)
    box.clamp_ip(pygame.Rect(6, FIELD_Y0 - 6, W - 12, FIELD_Y1 - FIELD_Y0 + 22))
    for _ in range(24):
        hit = next((r for r in placed if box.colliderect(r.inflate(7, 5))), None)
        if hit is None:
            break
        box.y = hit.bottom + 5 if box.centery >= hit.centery else hit.top - box.height - 5

    a = (int(x + (9 if right else -9)), int(y))
    b = (box.left - 5, box.centery) if right else (box.right + 5, box.centery)
    alpha_line(surf, (*CREAM, 105), a, b, 1)
    surf.blit(l1, (box.left if right else box.right - l1.get_width(), box.top))
    surf.blit(l2, (box.left if right else box.right - l2.get_width(),
                   box.top + l1.get_height() - 2))


# ── cartouche ────────────────────────────────────────────────────────────────

NUMERAL_H = 96


def hero_numeral(s):
    """Gold vertical gradient poured through the glyph's own alpha.

    Sized by measuring the ink box rather than trusting the point size —
    "25" and "180" have the same digit height but different metrics, and
    the two panels have to agree to the pixel or the eye reads one run as
    bigger than the other.
    """
    size = 132
    for cand in range(96, 200):
        if font(cand).render(s, True, (255,) * 3).get_bounding_rect().height >= NUMERAL_H:
            size = cand
            break
    glyph = font(size).render(s, True, (255, 255, 255))
    box = glyph.get_bounding_rect()
    cut = pygame.Surface(box.size, pygame.SRCALPHA)
    cut.blit(glyph, (-box.x, -box.y))

    grad = pygame.Surface(box.size, pygame.SRCALPHA)
    stops = [(0.00, (255, 232, 172)), (0.34, GOLD), (0.72, (206, 150, 48)),
             (1.00, (238, 196, 96))]
    for y in range(box.height):
        grad.fill((*lerp_color_multi(stops, y / max(1, box.height - 1)), 255),
                  pygame.Rect(0, y, box.width, 1))
    grad.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return grad, cut


def draw_cartouche(surf, run):
    label = smallcaps("PILLARS", 11, 8, (168, 176, 206), 3.2)
    lrect = label.get_rect(center=(CX, 466))
    surf.blit(label, lrect)

    grad, cut = hero_numeral(str(run.pillars))
    nx = CX - grad.get_width() // 2
    ny = 482

    # Sunk glow rather than an outline: over a near-black sky a keyline would
    # only carve the numeral thinner, while a low warm bloom gives it the
    # weight a 96px focal point needs without adding a second value edge.
    for rad, peak in ((26, 20), (14, 26)):
        for gx in range(0, grad.get_width(), 9):
            for gy in range(0, grad.get_height(), 9):
                if cut.get_at((min(gx, cut.get_width() - 1),
                               min(gy, cut.get_height() - 1)))[3] > 120:
                    add_glow(surf, nx + gx, ny + gy, rad, (150, 108, 30), peak)
    surf.blit(grad, (nx, ny))

    sub = font(14).render(f"DAY {run.day}   ·   {run.clock}", True, CREAM)
    sub.set_alpha(214)
    srect = sub.get_rect(center=(CX, 602))
    surf.blit(sub, srect)

    return pygame.Rect(min(lrect.left, nx, srect.left) - 8, lrect.top - 6,
                       max(lrect.width, grad.get_width(), srect.width) + 16,
                       srect.bottom - lrect.top + 12)


# ── panel ────────────────────────────────────────────────────────────────────

def render_panel(run):
    surf = pygame.Surface((W, H))
    draw_sky(surf)
    draw_dust(surf, run.pillars)
    draw_phase_ring(surf, run)

    pillars, span = chart_pillars(run)
    pts = curve_points(run, pillars)
    death_i = draw_chart(surf, run, pillars, pts, span)
    place_labels(surf, run, pillars, pts, death_i)

    cart = draw_cartouche(surf, run)
    draw_phase_labels(surf, cart)

    wordmark = font(9).render("F L I G H T   L O G", True, (150, 160, 196))
    wordmark.set_alpha(96)
    surf.blit(wordmark, wordmark.get_rect(center=(CX, 26)))

    return surf, pts, death_i, pillars, span


# ── sheet ────────────────────────────────────────────────────────────────────

def render_sheet(panels, captions):
    pad, gap, top, cap_h = 8, 8, 40, 24
    sw = pad * 2 + W * 2 + gap
    sh = top + H + cap_h
    sheet = pygame.Surface((sw, sh))
    sheet.fill(SHEET_BG)

    head = "STAR CHART · ROUND 1"
    f = font(17)
    glyphs = [f.render(ch, True, GOLD) for ch in head]
    tw = sum(g.get_width() for g in glyphs) + 3 * (len(head) - 1)
    x = (sw - tw) / 2
    for ch, g in zip(head, glyphs):
        sheet.blit(g, (int(x), top // 2 - g.get_height() // 2))
        x += g.get_width() + 3

    for i, (p, cap) in enumerate(zip(panels, captions)):
        px = pad + i * (W + gap)
        sheet.blit(p, (px, top))
        img = font(10).render(cap, True, (142, 150, 180))
        sheet.blit(img, img.get_rect(midtop=(px + W // 2, top + H + 6)))
    return sheet


# ── verification ─────────────────────────────────────────────────────────────

def scarlet_extent(surf):
    """Every warm-red pixel on the panel, as a bounding box + count. The
    concept only holds if this is one small blob."""
    xs, ys, n = [], [], 0
    for y in range(H):
        for x in range(W):
            r, g, b = surf.get_at((x, y))[:3]
            if r > 105 and r > g * 1.85 and r > b * 1.85:
                xs.append(x)
                ys.append(y)
                n += 1
    if not n:
        return None
    return (min(xs), min(ys), max(xs), max(ys), n)


def main():
    out_dir = "/home/user/skybit/docs/flight_log_screen/star_chart"
    os.makedirs(out_dir, exist_ok=True)

    panels, captions = [], []
    for run in (RUN_A, RUN_B):
        surf, pts, death_i, pillars, span = render_panel(run)
        panels.append(surf)
        reached = sum(1 for p in pillars if p <= run.pillars)
        captions.append(f"{run.tag}  ·  PILLAR {run.pillars}  ·  DAY {run.day}  ·  "
                        f"{run.clock}  ·  CAUSE {run.cause}")
        print(f"{run.tag}: charted to pillar {span}, {len(pillars)} stars, "
              f"{reached} reached ({100 * reached / len(pillars):.0f}% of stars, "
              f"{100 * run.pillars / span:.0f}% of charted pillars), "
              f"death star at ({pts[death_i][0]:.0f},{pts[death_i][1]:.0f})")
        sc = scarlet_extent(surf)
        print(f"        scarlet pixels: {sc[4]} in bbox "
              f"({sc[0]},{sc[1]})-({sc[2]},{sc[3]})  "
              f"= {sc[2] - sc[0] + 1}x{sc[3] - sc[1] + 1}px")
        print(f"        sky top {surf.get_at((4, 2))[:3]}   "
              f"sky bottom {surf.get_at((4, 637))[:3]}   "
              f"numeral core {surf.get_at((CX, 530))[:3]}")

    sheet = render_sheet(panels, captions)
    path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, path)
    print("saved", path, sheet.get_size())


if __name__ == "__main__":
    main()
