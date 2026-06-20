"""
Procedural achievement badges — the "Courier's Commendation" medallion family.

Every badge is drawn from code (project hard-rule: no PNG sprite sheets). A
badge is a struck-metal medallion: a faceted gold rim lit from the upper-left
(specular hot-spot + lower-right shadow arc, so it reads as a real coin rather
than a flat ring), a beveled inner step, and a recessed enamel field stamped
with an engraved per-key glyph. A twin-laurel sprig sits at the base so the
whole family shares one silhouette.

Lighting is one fixed upper-left source for the whole family — a specular
hot-spot on the gold rim's upper-left crest, a darker recess ring where the
enamel meets the rim, and a soft sheen on each glyph's top edge — so a badge
reads as a real struck medal, not a flat enamel pin.

State is one code path. EVERY locked badge is masked to a "?" so the
achievement stays unknown until it's earned in play — only the rim/well palette
distinguishes a rare Mystery from an ordinary lock:
  * unlocked (normal)   — warm gold rim + navy enamel + embossed glyph.
  * unlocked (Mystery)  — gold rim + DESATURATED amethyst enamel well + a
                          sparkle/star ring, so a rare unlock feels special
                          while gold stays the only fully-saturated accent.
  * locked (normal)     — a warm-pewter "?" disc: the medal asleep AND masked,
                          giving nothing away about what it rewards.
  * locked (Mystery)    — an amethyst "?" disc ringed with a faint sparkle/star
                          halo — enticingly rarer-looking than the pewter "?",
                          still no shape leaked.

Results are cached by ``(icon_key, size, unlocked, hidden)``. ``draw_badge`` is
the only entry point the screen calls; the glyph table is the baseline the
graphics design-loop refines.
"""
from __future__ import annotations

import math
import pygame

from game.draw import lerp_color, blit_glow

# Medallion palette — tuned to the menu's gold-on-navy family. Gold is the
# ONLY fully-saturated accent so "gold = earned" stays the dominant signal.
_RING_HI   = (255, 234, 168)   # specular crest of the rim bevel
_RING_MID  = (236, 186,  72)   # body gold
_RING_LO   = (150, 102,  20)   # shadowed underside of the bevel
_RIM_EDGE  = ( 70,  44,   8)   # thin outer keyline
_SPEC_HOT  = (255, 250, 222)   # single upper-left specular hot-spot
_FACE_TOP  = ( 44,  32,  92)   # enamel field, lit top
_FACE_BOT  = ( 16,  10,  44)   # enamel field, shadowed base
_RECESS    = ( 10,   6,  28)   # dark recess where enamel meets the rim
_STEP_HI   = (255, 226, 150)
_STEP_LO   = (140,  96,  22)
_GLYPH     = (255, 236, 184)   # engraved glyph highlight
_GLYPH_SH  = ( 32,  18,  44)   # engraved glyph inset shadow
_GLYPH_SHEEN = (255, 252, 232) # soft top-edge sheen on the glyph

# Mystery tier — DESATURATED amethyst enamel: reads "rare" but never competes
# with gold for saturation. Used both for the unlocked well and the "?" disc.
_AME_TOP   = ( 96,  74, 128)   # amethyst enamel, lit top
_AME_BOT   = ( 48,  34,  78)   # amethyst enamel, shadowed base
_AME_RECESS = ( 30,  20,  54)
_AME_GLY   = (214, 196, 240)   # cool amethyst glyph highlight
_AME_GLY_SH = ( 34,  22,  58)
_AME_SPARK = (228, 214, 250)   # sparkle-ring star colour
# A cooler gold-with-violet-cast rim for the hidden "?" disc so its frame reads
# rarer than dormant pewter without going fully saturated.
_AME_RIM_HI = (200, 184, 224)
_AME_RIM_MID = (150, 132, 184)
_AME_RIM_LO = ( 86,  70, 118)

# Dormant (locked, known) — the SAME medal asleep: a warm-tinted pewter (not a
# cold grey object). Value-based contrast vs. gold stays colourblind-safe.
_LOCK_HI   = (176, 168, 158)
_LOCK_MID  = (132, 122, 108)
_LOCK_LO   = ( 78,  70,  58)
_LOCK_FACE_TOP = ( 52,  48,  60)
_LOCK_FACE_BOT = ( 30,  27,  40)
_LOCK_RECESS = ( 20,  17,  30)
_LOCK_GLY  = (170, 162, 150)   # lifted ~12% so dormant reads inviting
_LOCK_GLY_SH = ( 28,  25,  34)

_SS = 4  # supersample for crisp edges, then smoothscale down
_BADGES: dict = {}

# The two two-tone glyphs (magnet poles, fry-box tub) carry a saturated accent
# (red/steel) that must appear ONLY on unlock — every dormant medal is bronze
# monochrome, so a leaked red reads as a half-lit error and breaks the locked
# convention. The builder sets this before stamping; the glyphs read it to pick
# their accent, and colour returns as part of the unlock reward.
_GLYPH_DORMANT = False


def _accent(lit_col, dormant_col=_LOCK_GLY):
    # Resolve a saturated glyph accent against the current state: the real
    # colour when the medal is live, the dormant bronze tone when asleep.
    return dormant_col if _GLYPH_DORMANT else lit_col

# Hidden-tier icon keys get the amethyst enamel + rarity ring automatically so
# the screen needn't pass a flag; mirrors the secret roster in achievements.py.
_HIDDEN_KEYS = frozenset({"genie", "knight", "treasure", "lottery", "rail", "poison"})


# ── glyph primitives (drawn in a 0..1 normalized box, scaled by caller) ───────
#
# Each takes (surf, cx, cy, r, col) and is stroked twice by the builder: a dark
# inset 1px down-right, then the lit colour on top, for an engraved look. So
# glyphs use the passed ``col`` only — no hard-coded fills that would skip the
# emboss. The handful of two-tone props (coin face, magnet poles) keep a small
# accent but still inherit the emboss pass.

def _glyph_pillar(surf, cx, cy, r, col):
    # Two sandstone pillars with a flared capital + base — a temple-gate read,
    # not a tally or a pause icon.
    shaft_w = max(3, int(r * 0.30))
    cap_w = int(shaft_w * 1.6)
    h = int(r * 1.0)
    top = cy - h // 2
    cap_h = max(2, int(r * 0.16))
    gap = int(r * 0.42)
    for sgn in (-1, 1):
        cx_p = cx + sgn * (gap // 2 + cap_w // 2)
        pygame.draw.rect(surf, col, (cx_p - shaft_w // 2, top + cap_h,
                                     shaft_w, h - cap_h * 2))
        for yy in (top, cy + h // 2 - cap_h):  # capital + base
            pygame.draw.rect(surf, col, (cx_p - cap_w // 2, yy, cap_w, cap_h),
                             border_radius=max(1, int(r * 0.05)))


def _glyph_coin(surf, cx, cy, r, col):
    rr = int(r * 0.66)
    pygame.draw.circle(surf, col, (cx, cy), rr, max(3, r // 8))
    f = _glyph_font(int(rr * 1.7))
    g = f.render("$", True, col)
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _glyph_day(surf, cx, cy, r, col):
    rr = int(r * 0.46)
    pygame.draw.circle(surf, col, (cx, cy), rr)
    for i in range(8):
        a = i * math.pi / 4
        x1 = cx + int(math.cos(a) * rr * 1.32)
        y1 = cy + int(math.sin(a) * rr * 1.32)
        x2 = cx + int(math.cos(a) * rr * 1.78)
        y2 = cy + int(math.sin(a) * rr * 1.78)
        pygame.draw.line(surf, col, (x1, y1), (x2, y2), max(2, r // 9))


def _glyph_storm(surf, cx, cy, r, col):
    s = r * 0.92
    pts = [
        (cx - s * 0.10, cy - s * 0.68),
        (cx - s * 0.46, cy + s * 0.06),
        (cx - s * 0.08, cy + s * 0.06),
        (cx - s * 0.30, cy + s * 0.68),
        (cx + s * 0.46, cy - s * 0.20),
        (cx + s * 0.05, cy - s * 0.20),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _glyph_nerve(surf, cx, cy, r, col):
    # A heartbeat / EKG line — the close-call "pulse spike" past a near-miss.
    # A flat baseline that leaps into a tall spike then settles: unmistakable
    # at 46px and on-metaphor for a nerve-wracking close shave.
    w = max(3, r // 8)
    pts = [
        (cx - r * 0.82, cy + r * 0.08),
        (cx - r * 0.40, cy + r * 0.08),
        (cx - r * 0.22, cy + r * 0.50),   # small dip
        (cx - r * 0.02, cy - r * 0.66),   # tall spike up
        (cx + r * 0.18, cy + r * 0.40),   # overshoot down
        (cx + r * 0.36, cy + r * 0.08),
        (cx + r * 0.82, cy + r * 0.08),
    ]
    pygame.draw.lines(surf, col, False, [(int(x), int(y)) for x, y in pts], w)


def _glyph_clock(surf, cx, cy, r, col):
    rr = int(r * 0.66)
    pygame.draw.circle(surf, col, (cx, cy), rr, max(3, r // 9))
    # crown nub so it reads as a stopwatch, not a plain ring
    pygame.draw.rect(surf, col, (cx - max(2, r // 10), cy - rr - int(r * 0.18),
                                 max(4, r // 5), max(3, int(r * 0.18))),
                     border_radius=max(1, r // 14))
    pygame.draw.line(surf, col, (cx, cy), (cx, cy - int(rr * 0.66)), max(2, r // 10))
    pygame.draw.line(surf, col, (cx, cy), (cx + int(rr * 0.52), cy + int(rr * 0.12)), max(2, r // 11))


def _glyph_wing(surf, cx, cy, r, col):
    # A single clean macaw wing — one filled silhouette swept up to the right.
    # The leading edge is a strong CONVEX arc (sampled from the shoulder up to
    # the tip) so the wing reads as an arc, not an arrowhead; the trailing edge
    # is a gentler scallop of just three feather lobes so it stays a wing, not
    # a busy fan.
    sx, sy = cx - r * 0.74, cy + r * 0.42          # shoulder
    tx, ty = cx + r * 0.72, cy - r * 0.62          # wing tip
    # Bowed leading edge: quadratic Bézier with the control point pushed up-left
    # of the chord so the top of the wing bulges (a wing's camber), not a point.
    lebx = cx - r * 0.52   # control point well above the chord
    leby = cy - r * 0.70
    leading = []
    for i in range(9):
        t = i / 8
        mt = 1 - t
        bx = mt * mt * sx + 2 * mt * t * lebx + t * t * tx
        by = mt * mt * sy + 2 * mt * t * leby + t * t * ty
        leading.append((bx, by))
    # Trailing edge: three soft feather lobes, tip → shoulder. Fewer notches so
    # the read stays "ONE wing".
    lobes = [
        (cx + r * 0.46, cy + r * 0.04),
        (cx + r * 0.04, cy + r * 0.20),
        (cx - r * 0.36, cy + r * 0.50),
    ]
    pts = leading + lobes
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _glyph_magnet(surf, cx, cy, r, col):
    # A chunky horseshoe magnet pulled inward off the rim, with two
    # unmistakable banded pole-tips at the bottom. Thicker U + a clear gap
    # between the legs so it never reads as a smudge at 46px.
    rr = int(r * 0.50)            # pulled inward off the rim
    leg_w = max(6, int(r * 0.30))
    bar = max(6, int(r * 0.32))
    top = cy - int(r * 0.46)
    # the arched top of the U
    arc_rect = pygame.Rect(cx - rr, top, rr * 2, rr * 2)
    pygame.draw.arc(surf, col, arc_rect, math.radians(6), math.radians(174), bar)
    # the two straight legs hanging down
    leg_top = top + rr
    leg_h = int(r * 0.52)
    for sgn in (-1, 1):
        lx = cx + sgn * rr - leg_w // 2
        pygame.draw.rect(surf, col, (lx, leg_top, leg_w, leg_h))
    # banded pole-tips — one red, one steel — drawn as full caps so they read
    # as poles, not specks. The accents desaturate to bronze when dormant so a
    # sleeping medal stays monochrome.
    tip_h = max(4, int(r * 0.20))
    for sgn, tip in ((-1, _accent((212, 64, 56))), (1, _accent((224, 228, 240)))):
        lx = cx + sgn * rr - leg_w // 2
        pygame.draw.rect(surf, tip, (lx, leg_top + leg_h, leg_w, tip_h))


def _glyph_kfc(surf, cx, cy, r, col):
    # A bucket of fries — trapezoid tub + a few sticks.
    tub = [(cx - r * 0.5, cy + r * 0.62), (cx + r * 0.5, cy + r * 0.62),
           (cx + r * 0.36, cy - r * 0.02), (cx - r * 0.36, cy - r * 0.02)]
    # The red fry-box desaturates to bronze when dormant so the sleeping medal
    # stays monochrome; the brand red returns on unlock.
    pygame.draw.polygon(surf, _accent((214, 74, 60)), [(int(x), int(y)) for x, y in tub])
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in tub], max(2, r // 14))
    for dx in (-0.22, 0.0, 0.22):
        x = int(cx + dx * r)
        pygame.draw.rect(surf, col, (x - max(2, r // 14), int(cy - r * 0.58),
                                     max(3, r // 7), int(r * 0.62)),
                         border_radius=max(1, r // 16))


def _glyph_skate(surf, cx, cy, r, col):
    # A skateboard in profile: a deck with upturned kick-tails (visible
    # curvature) and two wheels tucked UNDER the deck with a clear gap between
    # them — so it reads as a board, not a bench/table.
    th = max(4, int(r * 0.18))
    yk = cy - int(r * 0.10)                 # deck centre line
    # concave deck: two raised ends, dipping in the middle, drawn as a polygon
    deck = [
        (cx - r * 0.78, yk - r * 0.30),     # left kick-tail tip (up)
        (cx - r * 0.52, yk),
        (cx + r * 0.52, yk),
        (cx + r * 0.78, yk - r * 0.30),     # right kick-tail tip (up)
        (cx + r * 0.78, yk - r * 0.30 + th),
        (cx + r * 0.52, yk + th),
        (cx - r * 0.52, yk + th),
        (cx - r * 0.78, yk - r * 0.30 + th),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in deck])
    # Two fat wheels slung well below the deck so they break the badge's lower
    # edge as two distinct dark circles — the cue that sells "skateboard" at
    # 46px (a bare deck alone reads as a bowl/smile). Drawn in the engraved
    # shadow tone so they stay dark against the gold deck.
    wr = max(5, int(r * 0.23))
    wy = yk + th + int(wr * 0.7)
    for dx in (-0.42, 0.42):
        pygame.draw.circle(surf, _GLYPH_SH, (int(cx + dx * r), int(wy)), wr)
        pygame.draw.circle(surf, col, (int(cx + dx * r), int(wy)), max(1, wr // 3))


def _glyph_genie(surf, cx, cy, r, col):
    # Magic lamp with a wisp of smoke.
    body = pygame.Rect(int(cx - r * 0.6), int(cy + r * 0.02), int(r * 1.05), int(r * 0.5))
    pygame.draw.ellipse(surf, col, body)
    pygame.draw.polygon(surf, col, [(int(cx + r * 0.42), int(cy + r * 0.1)),
                                    (int(cx + r * 0.82), int(cy - r * 0.14)),
                                    (int(cx + r * 0.5), int(cy + r * 0.26))])
    pygame.draw.circle(surf, col, (int(cx - r * 0.56), int(cy + r * 0.12)), max(3, r // 9))
    # smoke wisp
    pygame.draw.arc(surf, col, (int(cx - r * 0.3), int(cy - r * 0.85),
                                int(r * 0.6), int(r * 0.7)),
                    -math.pi * 0.2, math.pi * 0.9, max(2, r // 12))


def _glyph_knight(surf, cx, cy, r, col):
    # Great-helm with a visor slit + a plume tick.
    helm = pygame.Rect(int(cx - r * 0.5), int(cy - r * 0.5), int(r), int(r * 1.05))
    pygame.draw.rect(surf, col, helm, border_radius=max(3, r // 4))
    pygame.draw.rect(surf, _GLYPH_SH, (int(cx - r * 0.4), int(cy - r * 0.14),
                                       int(r * 0.8), max(3, r // 7)),
                     border_radius=max(1, r // 12))
    pygame.draw.line(surf, col, (cx, cy - int(r * 0.5)),
                     (cx + int(r * 0.18), cy - int(r * 0.98)), max(3, r // 9))


def _glyph_treasure(surf, cx, cy, r, col):
    base = pygame.Rect(int(cx - r * 0.64), int(cy - r * 0.06), int(r * 1.28), int(r * 0.66))
    pygame.draw.rect(surf, col, base, border_radius=max(2, r // 10))
    lid = pygame.Rect(int(cx - r * 0.68), int(cy - r * 0.5), int(r * 1.36), int(r * 0.42))
    pygame.draw.rect(surf, col, lid, border_radius=max(3, r // 7))
    pygame.draw.line(surf, _GLYPH_SH, (int(cx - r * 0.64), int(cy - r * 0.06)),
                     (int(cx + r * 0.64), int(cy - r * 0.06)), max(2, r // 12))
    pygame.draw.circle(surf, _GLYPH_SH, (cx, int(cy + r * 0.06)), max(3, r // 9))
    pygame.draw.circle(surf, col, (cx, int(cy + r * 0.06)), max(3, r // 9), max(1, r // 18))


def _glyph_lottery(surf, cx, cy, r, col):
    # A five-point star burst (jackpot / score milestone).
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r * 0.78 if i % 2 == 0 else r * 0.32
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _glyph_rail(surf, cx, cy, r, col):
    # A single angled grind rail with a board sliding along it. The rail runs
    # lower-left to upper-right with two short support posts; the board sits on
    # top mid-grind. Reads as a trick, not a window grid.
    rw = max(3, int(r * 0.16))
    x0, y0 = cx - r * 0.78, cy + r * 0.42       # lower-left
    x1, y1 = cx + r * 0.78, cy - r * 0.34       # upper-right
    pygame.draw.line(surf, col, (int(x0), int(y0)), (int(x1), int(y1)), rw)
    # two support posts dropping from the rail
    for f in (0.28, 0.72):
        px = x0 + (x1 - x0) * f
        py = y0 + (y1 - y0) * f
        pygame.draw.line(surf, col, (int(px), int(py)),
                         (int(px), int(py + r * 0.34)), max(2, r // 12))
    # board sliding mid-rail, tilted to match the rail's slope
    bf = 0.50
    bx = x0 + (x1 - x0) * bf
    by = y0 + (y1 - y0) * bf
    dxn, dyn = (x1 - x0), (y1 - y0)
    blen = math.hypot(dxn, dyn)
    ux, uy = dxn / blen, dyn / blen             # along-rail unit
    nx, ny = -uy, ux                            # rail normal (up-ish)
    half = r * 0.42
    lift = r * 0.16
    board = [
        (bx - ux * half + nx * lift,       by - uy * half + ny * lift),
        (bx + ux * half + nx * lift,       by + uy * half + ny * lift),
        (bx + ux * half + nx * (lift + r * 0.14), by + uy * half + ny * (lift + r * 0.14)),
        (bx - ux * half + nx * (lift + r * 0.14), by - uy * half + ny * (lift + r * 0.14)),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in board])


def _glyph_poison(surf, cx, cy, r, col):
    # Skull — round cranium, jaw, two dark sockets.
    pygame.draw.circle(surf, col, (cx, cy - int(r * 0.12)), int(r * 0.56))
    jaw = pygame.Rect(int(cx - r * 0.32), int(cy + r * 0.26), int(r * 0.64), int(r * 0.3))
    pygame.draw.rect(surf, col, jaw, border_radius=max(2, r // 10))
    for dx in (-0.24, 0.24):
        pygame.draw.circle(surf, _GLYPH_SH, (int(cx + dx * r), int(cy - r * 0.16)),
                           max(3, r // 7))


def _glyph_powerup(surf, cx, cy, r, col):
    # A four-point sparkle.
    pts = [(cx, cy - r * 0.78), (cx + r * 0.2, cy - r * 0.2),
           (cx + r * 0.78, cy), (cx + r * 0.2, cy + r * 0.2),
           (cx, cy + r * 0.78), (cx - r * 0.2, cy + r * 0.2),
           (cx - r * 0.78, cy), (cx - r * 0.2, cy - r * 0.2)]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _glyph_ceiling(surf, cx, cy, r, col):
    # An up-arrow bonking the ceiling — "headbanger". A bar across the top, an
    # arrowhead striking it from below, and two impact sparks at the contact.
    w = max(3, r // 7)
    bar_y = cy - int(r * 0.60)
    pygame.draw.rect(surf, col, (cx - int(r * 0.80), bar_y - max(2, r // 9),
                                 int(r * 1.60), max(3, r // 5)),
                     border_radius=max(1, r // 12))
    tip = (cx, bar_y + max(3, r // 7))
    pygame.draw.lines(surf, col, False, [
        (cx - int(r * 0.42), cy + int(r * 0.18)), tip,
        (cx + int(r * 0.42), cy + int(r * 0.18)),
    ], w)
    pygame.draw.line(surf, col, (cx, cy + int(r * 0.80)), tip, w)
    for sgn in (-1, 1):
        sx = cx + sgn * int(r * 0.34)
        pygame.draw.line(surf, col, (sx, bar_y + int(r * 0.16)),
                         (sx + sgn * int(r * 0.18), bar_y + int(r * 0.36)),
                         max(1, r // 14))


_GLYPHS = {
    "pillar": _glyph_pillar,
    "coin": _glyph_coin,
    "day": _glyph_day,
    "score": _glyph_lottery,   # a star for score milestones
    "powerup": _glyph_powerup,
    "magnet": _glyph_magnet,
    "kfc": _glyph_kfc,
    "nerve": _glyph_nerve,
    "clock": _glyph_clock,
    "storm": _glyph_storm,
    "wing": _glyph_wing,
    "skate": _glyph_skate,
    "genie": _glyph_genie,
    "knight": _glyph_knight,
    "treasure": _glyph_treasure,
    "lottery": _glyph_lottery,
    "rail": _glyph_rail,
    "poison": _glyph_poison,
    "ceiling": _glyph_ceiling,
}

_glyph_fonts: dict = {}


def _glyph_font(px: int):
    f = _glyph_fonts.get(px)
    if f is None:
        f = pygame.font.SysFont(None, px, bold=True)
        _glyph_fonts[px] = f
    return f


# ── medallion construction ────────────────────────────────────────────────────

# Single fixed light source for the whole family — upper-left.
_LIGHT = math.radians(135)


def _draw_rim(surf, cx, cy, R, hi, mid, lo, spec=None):
    """A lit metal rim under a single upper-left light: concentric arcs whose
    tone sweeps from the upper-left crest round to the lower-right shadow, then
    one bright specular hot-spot painted on the upper-left so the bevel reads
    as a real struck coin rather than a flat concentric ring."""
    inner = int(R * 0.72)
    # Base body ring (flat) — fills any seam the directional pass leaves.
    for i in range(R, inner, -1):
        t = (R - i) / max(1, R - inner)
        pygame.draw.circle(surf, lerp_color(hi, lo, t * 0.6 + 0.2), (cx, cy), i)
    # Directional sheen: thin arcs whose colour depends on angle from the light.
    steps = 48
    band = (R - inner)
    for seg in range(steps):
        a0 = seg / steps * math.tau
        a1 = (seg + 1) / steps * math.tau
        # cosine falloff: 1 facing the light, 0 facing away
        d = (math.cos(a0 - _LIGHT) + 1) * 0.5
        col = lerp_color(lo, hi, d ** 1.4)
        rect = pygame.Rect(cx - R + band // 3, cy - R + band // 3,
                           (R - band // 3) * 2, (R - band // 3) * 2)
        pygame.draw.arc(surf, col, rect, -a1, -a0, max(2, band - band // 3))
    # Single specular hot-spot on the upper-left crest of the bevel — a short
    # bright arc so the whole rim has ONE obvious light, not an even sheen.
    if spec is not None:
        mid_r = (R + inner) // 2
        hot = pygame.Rect(cx - mid_r, cy - mid_r, mid_r * 2, mid_r * 2)
        pygame.draw.arc(surf, spec, hot, _LIGHT - 0.55, _LIGHT + 0.55,
                        max(2, band // 2))
    pygame.draw.circle(surf, mid, (cx, cy), R, max(2, R // 22))
    pygame.draw.circle(surf, _RIM_EDGE, (cx, cy), R, max(1, R // 36))


def _draw_face(surf, cx, cy, fr, top, bot, recess):
    """Recessed enamel disc — a vertical gradient masked to a circle. A 1–2px
    darker recess ring runs the full inner edge where the enamel meets the rim,
    plus a soft inner top shadow, so the enamel reads as sunk below the rim
    (struck relief) rather than a flat enamel-pin fill."""
    face = pygame.Surface((fr * 2, fr * 2), pygame.SRCALPHA)
    for yy in range(fr * 2):
        t = yy / max(1, fr * 2 - 1)
        pygame.draw.line(face, lerp_color(top, bot, t), (0, yy), (fr * 2, yy))
    mask = pygame.Surface((fr * 2, fr * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (fr, fr), fr)
    face.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Full-perimeter recess ring (darker) where enamel drops below the rim.
    pygame.draw.circle(face, recess, (fr, fr), fr, max(2, fr // 12))
    # Deeper inner top shadow so the recess catches the upper-left light.
    pygame.draw.arc(face, (0, 0, 0, 140), (2, 2, fr * 2 - 4, fr * 2 - 4),
                    math.radians(20), math.radians(160), max(2, fr // 8))
    surf.blit(face, (cx - fr, cy - fr))


def _draw_step(surf, cx, cy, fr, hi, lo):
    """The bevelled step ring between rim and enamel — a 2px lit/shadow keyline
    that gives the medallion its layered, minted depth."""
    pygame.draw.arc(surf, hi, (cx - fr, cy - fr, fr * 2, fr * 2),
                    math.radians(30), math.radians(210), max(2, fr // 10))
    pygame.draw.arc(surf, lo, (cx - fr, cy - fr, fr * 2, fr * 2),
                    math.radians(210), math.radians(390), max(2, fr // 10))


def _draw_laurel(surf, cx, cy, R, col_l, col_d):
    """A twin-laurel sprig hugging the medallion's base — the shared signature
    that ties the family together. Two arcs of leaf ticks sweeping up the lower
    flanks toward a small bottom knot. Each leaf is tinted by its angle to the
    one upper-left light, so the sprig is lit like the rim (its upper-left side
    catches more light) rather than evenly glowing all the way round."""
    leaves = 5
    for sgn in (-1, 1):
        base_a = math.radians(255 if sgn < 0 else 285)  # lower-left / lower-right
        spread = math.radians(58)
        for i in range(leaves):
            f = i / (leaves - 1)
            a = base_a + sgn * spread * f
            rr = R * (1.02 + 0.0 * f)
            bx = cx + math.cos(a) * rr
            by = cy + math.sin(a) * rr
            # directional shade: leaves facing the upper-left light are lighter
            d = (math.cos(a - _LIGHT) + 1) * 0.5
            leaf_col = lerp_color(col_d, col_l, d ** 1.2)
            # each leaf: a short tapered ellipse pointing tangentially up-out
            leaf_len = R * (0.20 - 0.05 * f)
            ang = a - sgn * math.radians(60)
            tip = (bx + math.cos(ang) * leaf_len, by + math.sin(ang) * leaf_len)
            mid = (bx + math.cos(ang) * leaf_len * 0.5 - sgn * math.sin(ang) * leaf_len * 0.4,
                   by + math.sin(ang) * leaf_len * 0.5 + sgn * math.cos(ang) * leaf_len * 0.4)
            pygame.draw.polygon(surf, leaf_col,
                                [(int(bx), int(by)), (int(mid[0]), int(mid[1])),
                                 (int(tip[0]), int(tip[1]))])
            pygame.draw.line(surf, col_d, (int(bx), int(by)),
                             (int(tip[0]), int(tip[1])), max(1, R // 40))
    # bottom knot
    pygame.draw.circle(surf, col_l, (cx, int(cy + R * 1.0)), max(2, R // 14))
    pygame.draw.circle(surf, col_d, (cx, int(cy + R * 1.0)), max(2, R // 14), max(1, R // 40))


def _stamp_glyph(surf, icon_key, cx, cy, gr, hi, sh, sheen=None):
    """Engrave the glyph under the one upper-left light: a dark inset pass
    offset down-right (the cast shadow), the lit body pass, then a faint sheen
    pass offset up-left on the glyph's top edge — so every glyph shares the
    same struck-metal relief regardless of its silhouette."""
    drawer = _GLYPHS.get(icon_key, _glyph_powerup)
    off = max(1, gr // 18)
    drawer(surf, cx + off, cy + off, gr, sh)
    if sheen is not None:
        drawer(surf, cx - off, cy - off, gr, sheen)
    drawer(surf, cx, cy, gr, hi)


def _draw_sparkle_ring(surf, cx, cy, fr, R, col):
    """Eight four-point twinkles riding just inside the rim — the rarity halo
    shared by the Mystery tier in BOTH its hidden-locked and unlocked looks."""
    for i in range(8):
        a = i * math.tau / 8 - math.radians(20)
        sx = cx + int(math.cos(a) * fr * 0.92)
        sy = cy + int(math.sin(a) * fr * 0.92)
        sr = max(2, R // 18)
        pygame.draw.line(surf, col, (sx - sr, sy), (sx + sr, sy), max(1, R // 38))
        pygame.draw.line(surf, col, (sx, sy - sr), (sx, sy + sr), max(1, R // 38))


def _build(icon_key: str, size: int, unlocked: bool, hidden: bool) -> pygame.Surface:
    S = _SS
    px = size * S
    surf = pygame.Surface((px, px), pygame.SRCALPHA)
    cx = cy = px // 2
    R = int(px * 0.46)
    is_mystery = icon_key in _HIDDEN_KEYS
    is_secret = unlocked and is_mystery          # unlocked Mystery (amethyst)

    if unlocked:
        glow_col = (170, 130, 220) if is_secret else (255, 200, 90)
        blit_glow(surf, cx, cy, int(R * 1.12), glow_col, 95)
    elif hidden:
        # the hidden "?" disc gets a faint cool halo so it's more enticing than
        # ordinary dormant pewter
        blit_glow(surf, cx, cy, int(R * 1.05), (140, 116, 196), 60)

    if is_secret:
        # Unlocked Mystery: gold rim, desaturated amethyst enamel well.
        rim_hi, rim_mid, rim_lo, spec = _RING_HI, _RING_MID, _RING_LO, _SPEC_HOT
        face_top, face_bot, recess = _AME_TOP, _AME_BOT, _AME_RECESS
        step_hi, step_lo = _STEP_HI, _STEP_LO
        laurel_l, laurel_d = _RING_HI, _RING_LO
    elif unlocked:
        # Normal earned medal: gold rim + navy enamel.
        rim_hi, rim_mid, rim_lo, spec = _RING_HI, _RING_MID, _RING_LO, _SPEC_HOT
        face_top, face_bot, recess = _FACE_TOP, _FACE_BOT, _RECESS
        step_hi, step_lo = _STEP_HI, _STEP_LO
        laurel_l, laurel_d = _RING_HI, _RING_LO
    elif hidden:
        # Hidden-locked Mystery: cool amethyst-cast rim + amethyst "?" well.
        rim_hi, rim_mid, rim_lo, spec = _AME_RIM_HI, _AME_RIM_MID, _AME_RIM_LO, _AME_SPARK
        face_top, face_bot, recess = _AME_TOP, _AME_BOT, _AME_RECESS
        step_hi, step_lo = _AME_RIM_HI, _AME_RIM_LO
        laurel_l, laurel_d = _AME_RIM_MID, _AME_RIM_LO
    else:
        # Dormant (known): the SAME medal asleep — warm-tinted pewter.
        rim_hi, rim_mid, rim_lo, spec = _LOCK_HI, _LOCK_MID, _LOCK_LO, None
        face_top, face_bot, recess = _LOCK_FACE_TOP, _LOCK_FACE_BOT, _LOCK_RECESS
        step_hi, step_lo = _LOCK_HI, _LOCK_LO
        laurel_l, laurel_d = _LOCK_MID, _LOCK_LO

    # Laurel sits behind the medallion body.
    _draw_laurel(surf, cx, cy, R, laurel_l, laurel_d)
    _draw_rim(surf, cx, cy, R, rim_hi, rim_mid, rim_lo, spec)
    fr = int(R * 0.70)
    _draw_step(surf, cx, cy, fr + max(2, R // 16), step_hi, step_lo)
    _draw_face(surf, cx, cy, fr, face_top, face_bot, recess)

    # Rarity sparkle-ring for the Mystery tier — both hidden-locked and unlocked
    # wear it so the secret achievements always feel like a trophy.
    if is_mystery and (unlocked or hidden):
        _draw_sparkle_ring(surf, cx, cy, fr, R, _AME_SPARK if not unlocked else _GLYPH)

    # Glyph (or the Mystery "?").
    gr = int(R * 0.56)
    if is_secret:
        _stamp_glyph(surf, icon_key, cx, cy, gr, _AME_GLY, _AME_GLY_SH, _GLYPH_SHEEN)
    elif unlocked:
        _stamp_glyph(surf, icon_key, cx, cy, gr, _GLYPH, _GLYPH_SH, _GLYPH_SHEEN)
    elif hidden:
        # Amethyst "?" engraved into the well — embossed like the real glyphs.
        f = _glyph_font(int(R * 1.05))
        off = max(1, R // 18)
        for dx, dy, c in ((off, off, _AME_GLY_SH), (-off, -off, _GLYPH_SHEEN),
                          (0, 0, _AME_GLY)):
            q = f.render("?", True, c)
            surf.blit(q, q.get_rect(center=(cx + dx, cy + dy)))
    else:
        # Dormant (locked): the medal asleep AND masked — a pewter "?" disc, the
        # same enamel-engraved "?" as the Mystery tier but in the warm-pewter
        # palette so a normal locked badge gives nothing away while staying
        # visually distinct from the rarer amethyst Mystery "?".
        f = _glyph_font(int(R * 1.05))
        off = max(1, R // 18)
        for dx, dy, c in ((off, off, _LOCK_GLY_SH), (0, 0, _LOCK_GLY)):
            q = f.render("?", True, c)
            surf.blit(q, q.get_rect(center=(cx + dx, cy + dy)))

    return pygame.transform.smoothscale(surf, (size, size))


def get_badge(icon_key: str, size: int, unlocked: bool,
              hidden: bool = False) -> pygame.Surface:
    key = (icon_key, size, unlocked, hidden)
    s = _BADGES.get(key)
    if s is None:
        s = _build(icon_key, size, unlocked, hidden)
        _BADGES[key] = s
    return s


def draw_badge(surf, icon_key: str, rect: "pygame.Rect", unlocked: bool,
               hidden: bool = False) -> None:
    """Blit a badge centered in ``rect`` (uses the smaller rect dimension).
    ``hidden`` (a still-locked Mystery) swaps the dormant pewter look for an
    amethyst "?" disc with a sparkle ring, so the secret's shape stays hidden
    while reading rarer and more enticing than an ordinary dormant medal."""
    size = min(rect.width, rect.height)
    badge = get_badge(icon_key, size, unlocked, hidden and not unlocked)
    surf.blit(badge, badge.get_rect(center=rect.center))
