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


def _wisp(surf, bx, by, dx, dy, length, *, root_w=2.0):
    """One soft down wisp poking OUTWARD from the silhouette edge at (bx,by) along
    the direction (dx,dy). Drawn as a short fat tapered triangle — a tan-shadow
    root, a buttermilk body — capped with a ROUND 2px tip circle so the end reads
    as a soft nub of down, not a needle point. The tan shadow backing gives the
    wisp its own dark→light value jump so it survives downscale; the rounded cap
    is what keeps the halo reading downy instead of urchin-spiky."""
    n = math.hypot(dx, dy) or 1.0
    ux, uy = dx / n, dy / n
    px, py = -uy, ux
    b0 = (bx + px * root_w, by + py * root_w)
    b1 = (bx - px * root_w, by - py * root_w)
    tip = (bx + ux * length, by + uy * length)
    # A blunt soft head: the wisp tapers to a small ROUND nub set just short of
    # the geometric tip so down ends in a clump, never a spike.
    nub = (bx + ux * (length - 1.2), by + uy * (length - 1.2))
    pygame.draw.polygon(surf, _DB_SHADOW_D,
                        [(b0[0] - ux, b0[1] - uy), (b1[0] - ux, b1[1] - uy), tip])
    pygame.draw.polygon(surf, _DB_BODY, [b0, b1, nub])
    # Round buttermilk nub + a bright fluff-tip spec on top = a soft lit clump
    # end that holds at 40px without sharpening into a needle.
    pygame.draw.circle(surf, _DB_BODY, (int(nub[0]), int(nub[1])), 2)
    pygame.draw.circle(surf, _DB_TIP, (int(nub[0]), int(nub[1])), 1)


def _down_clump(surf, cx, cy, rx, ry, t, *, base_len=3.4, jitter=2.0,
                spread=0.16, count=3):
    """A single TUFT of 2–4 wisps sharing a near-common root on the ellipse edge
    at angle t, fanning over a small angular spread. Clumping wisps into tufts
    (with gaps between tufts handled by the caller) is what reads as DOWN; an
    even ring of equal wisps reads as a comb. Lengths are jittered hard per wisp
    so no two neighbours match — irregularity is the whole tell."""
    for k in range(count):
        # Fan the tuft around its root angle; the centre wisp is longest.
        off = (k - (count - 1) / 2.0) * spread
        a = t + off
        ex, ey = cx + rx * math.cos(a), cy + ry * math.sin(a)
        dx, dy = math.cos(a), math.sin(a)
        # Deterministic per-(angle) length scatter, ±jitter, with the flanking
        # wisps of a tuft pulled shorter so each clump peaks in the middle.
        ln = base_len + jitter * math.sin(a * 9.1 + cx) - abs(off) * 6.0
        ln = max(2.0, ln)
        _wisp(surf, ex, ey, dx, dy, ln, root_w=1.9)


def _fluff_clusters(surf, cx, cy, rx, ry, tufts, *, a0=0.0, a1=2 * math.pi,
                    base_len=3.4, jitter=2.0):
    """Lay `tufts` down-clumps around an ellipse arc [a0,a1] with visible GAPS
    between them (tufts are spaced wider than they fan), so the outline frays
    into irregular clump-and-gap down rather than a uniform spiky ring."""
    n = tufts
    closed = abs((a1 - a0) - 2 * math.pi) < 1e-3
    for i in range(n):
        t = a0 + (a1 - a0) * (i / n if closed else i / max(1, n - 1))
        # Vary tuft size 2–4 by position so the gaps and clump density wander.
        count = 2 + (i + int(cx)) % 3
        _down_clump(surf, cx, cy, rx, ry, t,
                    base_len=base_len, jitter=jitter, count=count)


def _paint_downball(surf, _a):
    # ── 0 · BELLY VALUE STRUCTURE — make the puff read ROUND ─────────────────
    # A soft honey-shadow crease tucked under the chest/wing so the body reads as
    # a rounded ball catching light at the top, not a flat buttermilk mass. Drawn
    # FIRST so the fluff clumps overlay it cleanly.
    pygame.draw.arc(surf, _DB_SHADOW_D, pygame.Rect(24, 50, 24, 16),
                    math.radians(200), math.radians(345), 2)
    pygame.draw.arc(surf, _DB_BELLY, pygame.Rect(23, 49, 24, 16),
                    math.radians(205), math.radians(340), 1)

    # ── 1 · PUFFBALL HALO — irregular down clumps, not a spike ring ──────────
    # The hero silhouette-breaker. Wisps are bunched into 2–4-strand TUFTS with
    # visible GAPS between them and hard per-strand length jitter, so the outline
    # frays into clump-and-gap DOWN (reads soft) instead of an evenly-spaced
    # urchin ring. Body main ellipse composite (32,52) r(19,14). The bottom arc
    # is the read-first puff; the back/bottom halo is THINNED ~25% (fewer tufts,
    # shorter) so the clean round buttermilk form shows under the fluff.
    bcx, bcy = 32, 52
    # Lower belly puff — densest fray (front of the ball), shorter avg than R1.
    _fluff_clusters(surf, bcx, bcy + 1, 19, 15, 6,
                    a0=0.20 * math.pi, a1=0.92 * math.pi, base_len=3.5, jitter=2.0)
    # Forward chest fray — a couple of light tufts.
    _fluff_clusters(surf, bcx, bcy, 19, 14, 2,
                    a0=-0.02 * math.pi, a1=0.18 * math.pi, base_len=3.2, jitter=1.6)
    # Back fray — thinned (2 tufts, shorter) so the round form & tail stay clean.
    _fluff_clusters(surf, bcx, bcy, 19, 14, 2,
                    a0=1.00 * math.pi, a1=1.28 * math.pi, base_len=3.0, jitter=1.6)

    # ── 2 · TAIL TUFTS — even the tail reads downy ───────────────────────────
    # Two soft clumps on the tail wedge (thinned from three) so the sleek wedge
    # doesn't undercut the puff read without re-crowding it.
    for tx, ty in ((5, 49), (9, 56)):
        _wisp(surf, tx, ty, -0.9, 0.3, 3.3, root_w=1.9)

    # ── 3 · WING — one clear bright blob + tan underline ─────────────────────
    # A single 5px bright highlight blob with a 1px tan underline reads as a
    # pudgy half-grown wing at 40px; a short fluff fringe on the trailing edge
    # keeps it downy. No fiddly mid-tones that mush at thumbnail size.
    pygame.draw.circle(surf, _DB_TIP, (35, 45), 5)
    pygame.draw.arc(surf, _DB_SHADOW_D, pygame.Rect(30, 42, 11, 9),
                    math.radians(20), math.radians(160), 1)
    for fx, fy, fdx, fdy in ((28, 53, -0.3, 0.95), (35, 55, 0.1, 1.0)):
        _wisp(surf, fx, fy, fdx, fdy, 3.2, root_w=1.9)

    # ── 4 · HEAD HALO — frayed, but the crown kept CLEAN for the cowlick ─────
    # Head main ellipse composite (47,41) r(12,11). Fray only the BACK and lower
    # arcs into clumps; the top-crown arc (~1.3π–1.7π) is deliberately LEFT BARE
    # so the cowlick rises from clean buttermilk, not a spiky ring. That gap is
    # what lets the cowlick win as a distinct shape.
    hcx, hcy = 47, 41
    _fluff_clusters(surf, hcx, hcy, 12, 11, 2,
                    a0=1.00 * math.pi, a1=1.28 * math.pi, base_len=3.3, jitter=1.6)
    _fluff_clusters(surf, hcx, hcy, 12, 11, 2,
                    a0=1.72 * math.pi, a1=1.95 * math.pi, base_len=3.3, jitter=1.6)
    # One soft cheek tuft on the near lower cheek for a fuzzy baby face.
    _wisp(surf, 41, 51, -0.4, 0.9, 3.2, root_w=1.9)

    # ── 5 · TRIPLE COWLICK — the hero crown tell, distinct from the halo ─────
    # Three soft horns of fluff off the clean crown — deliberately a DIFFERENT
    # shape AND scale from the halo: ~2.7× longer (9–11px vs 3.5px) and fatter
    # (root_w 3.5), each leaning sideways at the tip for a floppy baby curl. Rising
    # from the bare crown arc, this is unmistakably the "it's a baby" signature.
    cwx, cwy = HX - 1, CROWN_Y + 2
    for ang, ln, curl in ((-0.55, 9.5, -2.0), (-0.05, 11.0, 0.5), (0.50, 9.0, 2.0)):
        dx, dy = math.sin(ang), -math.cos(ang)            # mostly-up, splayed
        rx = cwx + math.sin(ang) * 2
        # Build the sprout as a fat tapered tuft with a tip biased sideways so it
        # floppily curls — a soft horn, not a straight spike.
        tipx = rx + dx * ln + curl
        tipy = cwy + dy * ln - 1.0
        n = math.hypot(dx, dy)
        px, py = -dy / n, dx / n
        b0 = (rx + px * 3.5, cwy + py * 3.5)
        b1 = (rx - px * 3.5, cwy - py * 3.5)
        pygame.draw.polygon(surf, _DB_SHADOW_D, [b0, b1, (tipx, tipy + 1)])
        pygame.draw.polygon(surf, _DB_BODY,
                            [(b0[0], b0[1] - 0.5), (b1[0], b1[1] - 0.5), (tipx, tipy)])
        pygame.draw.circle(surf, _DB_TIP, (int(tipx), int(tipy)), 2)
    # A soft tan root mound seats the three sprouts on the crown.
    pygame.draw.circle(surf, _DB_SHADOW, (cwx, cwy + 1), 4)
    pygame.draw.circle(surf, _DB_BODY, (cwx, cwy), 3)

    # ── 6 · BIG-BABY EYES — built to read at 40px ────────────────────────────
    # A 4px white catch-light dome peeks under each aviator lower rim, a 1px DARK
    # pupil biased to the SAME side on both eyes (so they read as a paired gaze),
    # and a 1px pure-white sparkle on the opposite upper edge. The larger dome +
    # off-centre pupil + sparkle survive downscale where a centred 3px dome greyed
    # to mud. Lens centres composite (46,40)/(56,39); domes drop under the rim.
    for lx, ly in ((46, 41), (56, 40)):
        pygame.draw.circle(surf, _DB_TIP, (lx, ly + 4), 4)            # big dome
        pygame.draw.circle(surf, (255, 255, 252), (lx + 2, ly + 2), 1)  # sparkle
        pygame.draw.circle(surf, (58, 44, 30), (lx - 1, ly + 5), 1)   # pupil, biased left

    # ── 7 · CHEEK BLUSH — the rosy baby spot ─────────────────────────────────
    # A 2px rosy blush under the near (screen-left, lower) lens — the one warm
    # off-palette accent that says "baby" and survives downscale as a pink dot.
    pygame.draw.circle(surf, _DB_BLUSH, (42, 48), 2)
    pygame.draw.circle(surf, (248, 196, 190), (42, 47), 1)


# Body recolour through the palette system + the downy overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
build = store_skins._make_skin(
    _paint_downball,
    base_fn=lambda a: _build_parrot_with_palette(a, P_DOWNBALL),
)
