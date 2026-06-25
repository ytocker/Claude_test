"""design_3 · MAGMA CONURE — EPIC parrot rarity candidate (exploration only).

A charcoal Pip lit from within by molten glow. The read is pure value
contrast: a body lifted one value step off true black where the only warm
light is the cracks, a SHORT charcoal smoke-wisp FEATHER crest (three
tapering plumes each tipped with one small ember) breaking the crown
silhouette behind a clear forward face, and a few rising sparks above the
back. The crest is deliberately subordinate so the head + amber aviators
win the eye, tiering the bird as EPIC. Built on the palette-recolour contract
(`_build_parrot_with_palette` + `_pal`) wrapped by `store_skins._make_skin`.

Why a custom compose: a soft magma underglow is laid down BEHIND the body
so the cracks look like light bleeding through plumage rather than paint on
top — the body-first order in `_make_skin` can't do that. The bright
crack-lines themselves are then painted in front.

North star: lives or dies at 40px. The ember crest breaks the silhouette,
the cracks glow ≥2px and stay OFF the near-black store-card edge, and the
dark-body / hot-glow contrast keeps the bird from going to a black blob on
night sky. Exploration scratch — NEVER registered in store_skins.BUILDERS.
"""
import math
import pygame

from game import store_skins
from game.store_skins import (
    COMPOSITE_W, COMPOSITE_H, PARROT_DY, HX, HY, CROWN_Y,
    _WING_ANGLES, _add_outline,
)
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# Palette per the brief. Aviators retinted warm amber so Pip's signature
# shades read as catching the molten light instead of staying cool.
_CHARCOAL   = (50, 42, 46)        # #322A2E body
_DEEP       = (26, 21, 24)        # #1A1518 deep shadow
_MAGMA      = (255, 106, 30)      # #FF6A1E magma orange
_EMBER      = (255, 197, 58)      # #FFC53A ember yellow
_SMOKE      = (138, 138, 138)     # #8A8A8A smoke grey
_SMOKE_D    = (92, 92, 96)
_WHITE      = (255, 248, 230)

# Charcoal re-plumage lifted ONE value step off true black (#3A3034 main over
# #322A2E shadow) so the cracks have a plumage surface to live on instead of
# floating on stone — and so a faint warm rim-light reads as smouldering
# feather, not rock. Crown/chest sit highest; the only warm slots are the
# retinted aviators — every other warm note comes from the painted glow.
_BODY = (58, 48, 52)              # #3A3034 lifted body main
P_MAGMA = _pal(
    tail=[(26, 21, 24), (34, 28, 31), (46, 38, 42), (60, 50, 54)],
    tail_line=(20, 16, 18),
    body_shadow=(50, 42, 46),     # #322A2E — the old main is now the shadow
    body_main=_BODY,
    body_chest=(72, 60, 64),
    body_belly=(48, 40, 44),
    sheen=(255, 150, 70, 50),
    wing_main=(50, 41, 45),
    wing_dark=(30, 24, 28),
    wing_tip=(70, 58, 62),
    wing_secondary=None,
    wing_highlight=(110, 90, 94),
    head_shadow=(40, 33, 37),
    head_main=_BODY,
    head_cheek=(78, 66, 70),
    head_crown=(86, 72, 76),
    lens_frame=(150, 88, 38),
    lens_body=(26, 17, 15),
    lens_tint=(255, 130, 55, 165),
    lens_glint=(255, 236, 190),
    beak_main=(44, 36, 39),
    beak_dark=(22, 17, 19),
    beak_gloss=(170, 102, 56),
    foot=(40, 33, 36),
)


def _glow_dot(surf, cx, cy, r, color):
    """Soft additive bloom so a crack/ember reads as emitted light, not paint.
    Drawn on its own surface with ADD so overlapping glows stack toward white."""
    g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    cr, cg_, cb = color
    for i in range(r, 0, -1):
        a = int(70 * (i / r) ** 2)
        pygame.draw.circle(g, (cr, cg_, cb, a), (r + 1, r + 1), i)
    surf.blit(g, (int(cx - r - 1), int(cy - r - 1)),
              special_flags=pygame.BLEND_RGBA_ADD)


def _crack(surf, pts, behind):
    """A glowing magma crack: an orange→yellow vein with a hot yellow-white
    core. ≥2px so it survives the 40px downscale; `behind` carries the soft
    underglow that bleeds through the plumage from the back layer."""
    # Underglow bloom following the vein on the back layer.
    for x, y in pts:
        _glow_dot(behind, x, y, 5, _MAGMA)
    # The vein itself: dark cooling rim → orange body → hot yellow core.
    pygame.draw.lines(surf, _DEEP, False, pts, 4)
    pygame.draw.lines(surf, _MAGMA, False, pts, 3)
    pygame.draw.lines(surf, _EMBER, False, pts, 1)


def _smoke_plume(surf, root, lean, h, ember_r, behind):
    """A short charcoal smoke-wisp FEATHER (not a stalk): a tapering quill that
    starts wide+dark at the crown and narrows to a single small ember tip. The
    body is smoke-charcoal that recedes into the silhouette so it reads as
    plumage breaking the outline, while the lone ember tip is one of the two
    hottest hues — the wisp carries the bird's heat up without becoming the
    whole shape."""
    rx, ry = root
    mid = (rx + lean // 2, ry - h * 3 // 5)
    tip = (rx + lean, ry - h)
    # Wide-to-narrow quill: a thick dark base stroke tapering to a thin neck.
    pygame.draw.lines(surf, _SMOKE_D, False, [root, mid], 5)
    pygame.draw.lines(surf, _SMOKE_D, False, [mid, tip], 3)
    pygame.draw.lines(surf, _SMOKE, False, [(rx, ry - 1), mid, tip], 1)
    # One small ember at the very tip — held to the two hottest hues only.
    _glow_dot(behind, tip[0], tip[1], ember_r + 2, _MAGMA)
    pygame.draw.circle(surf, _MAGMA, tip, ember_r)
    pygame.draw.circle(surf, _EMBER, tip, max(1, ember_r - 1))


def _paint_magma(surf, wing_angle_deg, behind):
    # Body centre in composite space (native (32,32) + PARROT_DY) and the
    # wing pivot — the cracks trace the actual plumage masses.
    bcx, bcy = 32, 32 + PARROT_DY

    # ── Smoke-wisp crest, re-cut ~40% shorter and reshaped as FEATHERS. Three
    # short tapering charcoal plumes sit BEHIND/ABOVE the back of the crown
    # (pulled left of the face), each tipped with ONE small ember. They break
    # the crown silhouette without becoming the silhouette — the head and
    # aviators stay forward and unmistakable.
    base = CROWN_Y + 2
    for sx, lean, h, er in ((-5, -4, 12, 2), (-1, -2, 14, 2), (2, 3, 11, 2)):
        _smoke_plume(surf, (HX + sx, base), lean, h, er, behind)

    # ── Forward face read: re-establish the head. A warm rim hugs the crown's
    # FRONT and the beak wedge so the face catches the molten light and wins
    # the eye ahead of the crest. The amber aviator already lives in the base
    # build at native (50,20); we punch a hot glint so the lens reads brightest.
    bx0, bx1 = 55, 61                      # native beak wedge tip span
    pygame.draw.line(surf, _MAGMA, (bx0, 21 + PARROT_DY),
                     (bx1, 24 + PARROT_DY), 2)
    pygame.draw.line(surf, _EMBER, (bx0, 22 + PARROT_DY),
                     (bx1 - 1, 24 + PARROT_DY), 1)
    # Aviator-winning glints: bloom + hot specular on each amber lens so the
    # eye lands on the face, not the crown.
    for lx, ly in ((50, 20 + PARROT_DY), (56, 20 + PARROT_DY)):
        _glow_dot(behind, lx, ly, 4, _MAGMA)
        pygame.draw.circle(surf, _EMBER, (lx - 1, ly - 1), 1)
        pygame.draw.circle(surf, _WHITE, (lx - 1, ly - 2), 1)

    # ── Magma crack-lines tracing the body. Held off the near-black store-card
    # edge of the silhouette: each vein runs across the BODY INTERIOR (chest /
    # flank), not the outer rim, so the dark outline pass never swallows it.
    _crack(surf, [(bcx - 7, bcy - 4), (bcx - 2, bcy + 1),
                  (bcx + 1, bcy + 7), (bcx - 1, bcy + 12)], behind)
    _crack(surf, [(bcx - 11, bcy + 4), (bcx - 6, bcy + 6),
                  (bcx - 3, bcy + 11)], behind)

    # ── Wing shape, so the wing crack has a feather edge to trace instead of
    # floating on a shapeless mass. A faint warm rim-light traces the wing's
    # leading edge + lower feather fan; the leading-edge crack then runs just
    # inboard of that lit edge. Wing pivot is native (34,28) → composite.
    wx, wy = 34, 28 + PARROT_DY
    wing_edge = [(wx - 5, wy + 11), (wx + 1, wy + 5),
                 (wx + 8, wy + 1), (wx + 14, wy)]
    pygame.draw.lines(surf, (150, 96, 70), False, wing_edge, 1)   # warm rim
    # Lower feather-fan ticks define the wing as plumage with a trailing edge.
    for tx, ty in ((wx + 13, wy + 2), (wx + 9, wy + 6), (wx + 4, wy + 9)):
        pygame.draw.line(surf, (110, 78, 64), (tx, ty), (tx - 2, ty + 3), 1)
    _crack(surf, [(wx - 4, wy + 9), (wx + 4, wy + 4), (wx + 12, wy)], behind)

    # ── Faint warm rim-light along the back/upper edge — gives the dark mass a
    # lit contour so it reads as smouldering plumage, not stone.
    back_edge = [(bcx - 9, bcy - 6), (bcx - 4, bcy - 9),
                 (bcx + 3, bcy - 8), (bcx + 9, bcy - 4)]
    pygame.draw.lines(surf, (140, 88, 64), False, back_edge, 1)

    # ── Ember-tipped feather ends: a couple of tail/wing tips glow as if the
    # plumage is smouldering. Small hot dots with a bloom, kept inboard of the
    # outline.
    for fx, fy in ((10, bcy + 4), (16, bcy + 8), (wx + 13, wy + 1)):
        _glow_dot(behind, fx, fy, 4, _MAGMA)
        pygame.draw.circle(surf, _MAGMA, (fx, fy), 2)
        pygame.draw.circle(surf, _EMBER, (fx, fy), 1)

    # ── Rising ember sparks above the back — hottest (largest, whitest) near
    # the body, cooling and shrinking as they rise into open sky. These read as
    # heat shimmer lifting off the plumage and add motion at 40px.
    sparks = ((bcx - 6, bcy - 13, 3, True),
              (bcx - 12, bcy - 19, 2, True),
              (bcx - 4, bcy - 22, 2, False),
              (bcx - 16, bcy - 27, 1, False))
    for ex, ey, r, hot in sparks:
        _glow_dot(behind, ex, ey, r + 3, _MAGMA)
        pygame.draw.circle(surf, _EMBER if hot else _MAGMA, (ex, ey), r)
        if hot:
            pygame.draw.circle(surf, _WHITE, (ex, ey - 1), max(1, r - 1))


def _make_magma_getter():
    """Custom getter: lay the magma underglow on a BACK layer, blit the
    charcoal body over it, then paint the bright glow in front — so the cracks
    read as light bleeding through the plumage. Mirrors `_make_skin`'s cache
    shape (lazy flat frames + per-(frame, 3°-bucket) rotation cache)."""
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        behind = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _paint_magma(comp, wing_angle, behind)        # fills front + behind
        body = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        body.blit(_build_parrot_with_palette(wing_angle, P_MAGMA), (0, PARROT_DY))
        # Compose: underglow → body → front glow, then the house outline pass.
        out = behind
        out.blit(body, (0, 0))
        out.blit(comp, (0, 0))
        return _add_outline(out)

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_flat(a) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


build = _make_magma_getter()
