"""design_2 · DOWNBALL — BABY-PARROT exploration (scratch only, common tier).

Pip de-aged into a round ball of down — "maximum fuzz". The whole sleek
egg-shape of the macaw is feathered into a soft halo of short fluff wisps all
the way around, so the silhouette itself reads PUFFBALL before any detail
lands. The fuzz IS the silhouette-breaker; a triple down-tuft cowlick off the
crown is the hero crown tell, and big white catch-light eye-domes under the
aviators sell the neoteny. Aviators STAY (soft-gold tint) — they are Pip.

North star is "lives or dies at 40px on BOTH day and night sky". So the wisps
are NOT a soft wash: each is a hard ≥2px tapered spike poking past the body
outline, drawn as a bright fluff-tip over a tan-shadow root so the fuzzy edge
carries its own light→dark value jump and survives downscale instead of
mushing into a smooth blob. Buttermilk/honey is held warm and low-contrast so
it stays clear of cockatoo white and sun-conure's saturated orange-yellow.

Body recolour rides the palette system; cowlick + fluff halo + eye-domes are
pure pygame.draw polygons/lines/circles in a paint_fn overlay over the same
fixed macaw geometry — "baby" is sold by palette + overlay, never by shrinking.
Exploration only — NEVER registered in store_skins.BUILDERS.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# Downball palette — buttermilk body with a warm-tan shadow that owns the line
# work, a honey belly so the lower puff carries a touch more colour, and a near-
# white fluff-tip so every wisp end has a bright spec that reads at 40px. The
# warmth is bought with soft yellow local colour, never emission, so it stays
# clear of cockatoo white and reads softer than sun-conure orange.
_DB_BODY   = (251, 241, 201)        # #FBF1C9 buttermilk body
_DB_SHADOW = (224, 192, 121)        # #E0C079 warm tan shadow / fluff root
_DB_BELLY  = (247, 219, 155)        # #F7DB9B honey belly
_DB_TIP    = (255, 251, 232)        # #FFFBE8 fluff-tip highlight (the bright spec)
_DB_BLUSH  = (242, 166, 160)        # #F2A6A0 cheek-blush
_DB_GOLD   = (242, 210, 122)        # #F2D27A aviator soft-gold tint
_DB_SHADOW_D = (196, 162, 92)       # deeper tan = the value floor under a wisp


# Full buttermilk re-plumage. Shadow slots run warm tan so the body already
# carries a soft light→dark range for the fluff to sit on; belly + chest stay
# honey so the puff reads rounder at the bottom. Aviators retinted soft-gold so
# Pip's tell stays warm with the costume.
P_DOWNBALL = _pal(
    tail=[(214, 182, 112), (230, 200, 138), (244, 218, 162), (251, 238, 196)],
    tail_line=_DB_SHADOW_D,
    body_shadow=_DB_SHADOW,
    body_main=_DB_BODY,
    body_chest=(252, 244, 214),
    body_belly=_DB_BELLY,
    sheen=(255, 252, 236, 120),
    wing_main=(238, 210, 142),
    wing_dark=_DB_SHADOW_D,
    wing_tip=(253, 242, 206),
    wing_secondary=None,               # single warm hue — no contrast feather
    wing_highlight=_DB_TIP,
    head_shadow=_DB_SHADOW,
    head_main=_DB_BODY,
    head_cheek=(252, 230, 178),
    head_crown=(248, 226, 162),
    lens_frame=(214, 178, 104),        # warm gold rims
    lens_body=(70, 58, 36),
    lens_tint=(242, 210, 122, 130),    # soft-gold lens tint
    lens_glint=(255, 252, 238),
    beak_main=(236, 198, 132),
    beak_dark=(176, 134, 78),
    beak_gloss=(255, 250, 232),
    foot=(176, 134, 78),
)


def _wisp(surf, bx, by, dx, dy, length):
    """One hard fluff wisp poking OUTWARD from the silhouette edge at (bx,by)
    along the unit-ish direction (dx,dy). Drawn as a fat ≥2px tapered triangle
    — a tan-shadow root, a buttermilk body, then a bright fluff-tip cap — so the
    wisp carries its OWN dark→light value jump and survives downscale as a spike,
    not a soft blur. A thin shadow keyline seats it against the sky."""
    n = math.hypot(dx, dy) or 1.0
    ux, uy = dx / n, dy / n
    # Perpendicular base so the triangle is fat at the root (2px each side → wide
    # enough to read), tapering to a single-pixel point.
    px, py = -uy, ux
    root_w = 2.4
    b0 = (bx + px * root_w, by + py * root_w)
    b1 = (bx - px * root_w, by - py * root_w)
    tip = (bx + ux * length, by + uy * length)
    mid = (bx + ux * length * 0.5, by + uy * length * 0.5)
    # Shadow backing 1px toward the body = a hard rim that keeps the wisp from
    # vanishing on the bright buttermilk body itself.
    pygame.draw.polygon(surf, _DB_SHADOW_D,
                        [(b0[0] - ux, b0[1] - uy), (b1[0] - ux, b1[1] - uy), tip])
    pygame.draw.polygon(surf, _DB_BODY, [b0, b1, tip])
    # Bright tip cap — the spec that survives 40px.
    pygame.draw.line(surf, _DB_TIP, mid, tip, 2)
    pygame.draw.circle(surf, _DB_TIP, (int(tip[0]), int(tip[1])), 1)


def _fluff_ring(surf, cx, cy, rx, ry, wisps, *, a0=0.0, a1=2 * math.pi,
                length=4.5, jitter=0.0):
    """Lay a ring of outward wisps around an ellipse (cx,cy,rx,ry), spanning the
    arc [a0,a1]. Each wisp roots on the ellipse edge and points radially out so
    the whole outline frays into down. Deterministic per-angle length jitter
    breaks the mechanical look without any RNG state."""
    n = len(range(wisps)) if isinstance(wisps, range) else wisps
    for i in range(n):
        t = a0 + (a1 - a0) * (i / max(1, n - 1)) if a1 - a0 < 2 * math.pi \
            else a0 + (a1 - a0) * (i / n)
        ex, ey = cx + rx * math.cos(t), cy + ry * math.sin(t)
        # Radial outward direction from the ellipse centre.
        dx, dy = math.cos(t), math.sin(t)
        ln = length + jitter * math.sin(t * 3.7)
        _wisp(surf, ex, ey, dx, dy, ln)


def _paint_downball(surf, _a):
    # ── 1 · PUFFBALL HALO — the hero silhouette-breaker ──────────────────────
    # A dense ring of fluff wisps fraying the WHOLE lower body + chest + back so
    # the sleek macaw egg reads as a round ball of down. Body main ellipse is at
    # composite (32,52) r(19,14); the ring is pushed just past that edge so the
    # wisps poke OUT past the outline. The bottom arc is the densest (the belly
    # puff the eye reads first); the back/upper arc is sparser so the head + wing
    # stay legible.
    bcx, bcy = 32, 52
    # Lower belly puff — the densest fray (front of the puffball).
    _fluff_ring(surf, bcx, bcy + 1, 19, 15, 14,
                a0=0.18 * math.pi, a1=0.95 * math.pi, length=5.0, jitter=1.4)
    # Chest fray on the screen-right (forward) lower edge.
    _fluff_ring(surf, bcx, bcy, 19, 14, 6,
                a0=-0.05 * math.pi, a1=0.2 * math.pi, length=4.2, jitter=1.0)
    # Back fray — sparser so the tail/wing read stays clean.
    _fluff_ring(surf, bcx, bcy, 19, 14, 6,
                a0=0.95 * math.pi, a1=1.3 * math.pi, length=4.5, jitter=1.2)

    # ── 2 · TAIL TUFTS — even the tail reads downy ───────────────────────────
    # Soften the three tail-wedge tips (composite y ~44-56, x ~2-20) with a short
    # outward fluff each so the sleek wedge doesn't undercut the puff read.
    for tx, ty in ((4, 47), (6, 53), (10, 57)):
        _wisp(surf, tx, ty, -0.9, 0.3, 4.2)

    # ── 3 · WING FLUFF FRINGE + STUBBY HIGHLIGHT ─────────────────────────────
    # A rounded bright highlight blob mid-wing fakes a pudgy half-grown wing,
    # and a short fluff fringe along the trailing (lower) edge keeps the wing
    # downy rather than sleek-feathered. Wing sits centred ~ (34,48) composite.
    pygame.draw.circle(surf, _DB_TIP, (35, 46), 4)
    pygame.draw.circle(surf, _DB_BODY, (35, 46), 4, 1)
    for fx, fy, fdx, fdy in ((26, 53, -0.4, 0.9), (31, 55, 0.0, 1.0),
                             (37, 54, 0.4, 0.9)):
        _wisp(surf, fx, fy, fdx, fdy, 3.8)

    # ── 4 · HEAD HALO — the round head frayed too ────────────────────────────
    # Head main ellipse composite (47,41) r(12,11). Fray the upper + back arc so
    # the crown/cheek read fuzzy, leaving the face (where the aviators + beak
    # sit) clean. The crown wisps lead the eye into the cowlick.
    hcx, hcy = 47, 41
    _fluff_ring(surf, hcx, hcy, 12, 11, 7,
                a0=1.05 * math.pi, a1=1.85 * math.pi, length=4.0, jitter=1.0)
    # A couple of cheek wisps on the near (lower-front) cheek for an extra-fuzzy
    # baby face without crowding the beak.
    _wisp(surf, 40, 50, -0.5, 0.85, 3.6)
    _wisp(surf, 44, 51, 0.0, 1.0, 3.4)

    # ── 5 · TRIPLE COWLICK — the hero crown tell ─────────────────────────────
    # Three short soft down-sprouts off the top of the head, splaying out so the
    # crown outline breaks into an unmistakable baby cowlick. Each is a fat
    # tapered tuft (root → bright tip) so it reads as a soft sprout, not a sharp
    # feather, and survives 40px as the "it's a baby" crown signature. Centred on
    # the crown top (HX, CROWN_Y) and reaching well past the silhouette.
    cwx, cwy = HX - 1, CROWN_Y + 1
    for ang, ln in ((-0.62, 8.5), (-0.10, 9.5), (0.42, 8.0)):
        dx, dy = math.sin(ang), -math.cos(ang)   # mostly-up, splayed
        _wisp(surf, cwx + math.sin(ang) * 2, cwy, dx, dy, ln)
    # A soft tan root mound under the cowlick seats the three sprouts on the
    # crown so they don't look pasted on.
    pygame.draw.circle(surf, _DB_SHADOW, (cwx, cwy + 1), 3)
    pygame.draw.circle(surf, _DB_BODY, (cwx, cwy), 2)

    # ── 6 · BIG-BABY EYES — neoteny under the aviators ───────────────────────
    # Oversized white catch-light domes sitting just UNDER each aviator lens so
    # the round eyes read huge below the frames (the lenses stay; the cuteness is
    # sold around them). Lens centres are base (46,20)/(56,19) → composite
    # (46,40)/(56,39). The domes peek out the lower rim of each lens.
    for lx, ly in ((46, 40), (56, 39)):
        pygame.draw.circle(surf, _DB_TIP, (lx, ly + 5), 3)
        pygame.draw.circle(surf, (252, 246, 224), (lx + 1, ly + 6), 2)
        pygame.draw.circle(surf, (90, 70, 48), (lx, ly + 6), 1)   # tiny pupil dot

    # ── 7 · CHEEK BLUSH — the rosy baby spot ─────────────────────────────────
    # A 2px rosy blush under the near (screen-left, lower) lens — the one warm
    # off-palette accent that says "baby" and survives downscale as a pink dot.
    pygame.draw.circle(surf, _DB_BLUSH, (42, 47), 2)
    pygame.draw.circle(surf, (248, 196, 190), (42, 46), 1)


# Body recolour through the palette system + the downy overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
build = store_skins._make_skin(
    _paint_downball,
    base_fn=lambda a: _build_parrot_with_palette(a, P_DOWNBALL),
)
