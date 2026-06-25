"""design_3 · MAGMA CONURE — EPIC parrot rarity candidate (exploration only).

A charcoal Pip lit from within by molten glow. The read is pure value
contrast: a near-black body where the only warm light is the cracks, a
smoke-wisp crest tipped with embers breaking the crown silhouette, and a
few rising sparks above the back. Built on the palette-recolour contract
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

# Near-black charcoal re-plumage. Crown/chest lifted a touch above the deep
# so the dark mass keeps internal form on night sky; the only warm slots are
# the retinted aviators — every other warm note comes from the painted glow.
P_MAGMA = _pal(
    tail=[(22, 18, 21), (30, 25, 28), (40, 33, 37), (52, 44, 48)],
    tail_line=(16, 13, 15),
    body_shadow=(30, 24, 28),
    body_main=_CHARCOAL,
    body_chest=(60, 51, 55),
    body_belly=(40, 33, 37),
    sheen=(255, 150, 70, 45),
    wing_main=(38, 31, 35),
    wing_dark=(22, 18, 21),
    wing_tip=(58, 48, 52),
    wing_secondary=None,
    wing_highlight=(96, 78, 82),
    head_shadow=(30, 24, 28),
    head_main=_CHARCOAL,
    head_cheek=(64, 54, 58),
    head_crown=(70, 59, 63),
    lens_frame=(120, 70, 30),
    lens_body=(24, 16, 14),
    lens_tint=(255, 120, 50, 150),
    lens_glint=(255, 230, 180),
    beak_main=(36, 30, 33),
    beak_dark=(18, 14, 16),
    beak_gloss=(150, 90, 50),
    foot=(34, 28, 31),
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


def _paint_magma(surf, wing_angle_deg, behind):
    # Body centre in composite space (native (32,32) + PARROT_DY) and the
    # wing pivot — the cracks trace the actual plumage masses.
    bcx, bcy = 32, 32 + PARROT_DY

    # ── Smoke-wisp crest: a curling grey plume rising past the crown, tipped
    # with bright embers. Two offset wisps so the silhouette break reads as
    # rising smoke, not a single horn. The embers are the hottest points and
    # sit highest, so they break the outline first at 40px.
    base = CROWN_Y + 3
    for sx, lean, h in ((-2, -6, 20), (3, 5, 24)):
        x = HX + sx
        root = (x, base + 1)
        mid = (x + lean // 2, base - h // 2)
        tip = (x + lean, base - h)
        pygame.draw.lines(surf, _SMOKE_D, False, [root, mid, tip], 4)
        pygame.draw.lines(surf, _SMOKE, False, [root, (mid[0] + 1, mid[1]), tip], 2)
        # Ember tip — a hot core with a soft bloom so it glows past the smoke.
        _glow_dot(behind, tip[0], tip[1], 5, _MAGMA)
        pygame.draw.circle(surf, _MAGMA, tip, 3)
        pygame.draw.circle(surf, _EMBER, tip, 2)
        pygame.draw.circle(surf, _WHITE, (tip[0], tip[1] - 1), 1)
    # A third small mid-crest ember so 2–3 embers crown the bird.
    mex, mey = HX + 1, base - 13
    _glow_dot(behind, mex, mey, 4, _MAGMA)
    pygame.draw.circle(surf, _EMBER, (mex, mey), 2)
    pygame.draw.circle(surf, _WHITE, (mex, mey - 1), 1)

    # ── Magma crack-lines tracing the body. Held off the near-black store-card
    # edge of the silhouette: each vein runs across the BODY INTERIOR (chest /
    # flank), not the outer rim, so the dark outline pass never swallows it.
    _crack(surf, [(bcx - 7, bcy - 4), (bcx - 2, bcy + 1),
                  (bcx + 1, bcy + 7), (bcx - 1, bcy + 12)], behind)
    _crack(surf, [(bcx - 11, bcy + 4), (bcx - 6, bcy + 6),
                  (bcx - 3, bcy + 11)], behind)

    # Wing leading-edge crack — the wing root toward the tip, so the flapping
    # plane carries a hot line too. Wing pivot is native (34,28) → composite.
    wx, wy = 34, 28 + PARROT_DY
    _crack(surf, [(wx - 4, wy + 9), (wx + 4, wy + 4), (wx + 12, wy)], behind)

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
