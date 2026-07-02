"""MOSQUITO design_3 — NEON SKEETER (scratch exploration candidate).

Synthwave/arcade mosquito: a charcoal body whose two weakest tells — the
proboscis and the six spindly legs — are turned into the hero by rendering
them as glowing cyan/magenta neon tubes. The glow is genuine additive bloom
(BLEND_RGBA_ADD), so the spindly rig lights up like a tiny flying neon sign
and survives the 40px downscale as pure colour + line.

Scratch candidate ONLY — wrapped by the animal-skins prebuilt factory but never
registered in any BUILDERS map or the store catalog.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()

from game.animal_skins import (  # noqa: E402
    _make_prebuilt_skin, COMPOSITE_W, COMPOSITE_H, BCX, BCY, HCX, HCY, _new,
)

# Synthwave palette: matte charcoal body carries the dark silhouette; every
# highlight is one of two electric neons so the linework is the whole show.
CHARCOAL      = (23, 19, 37)
CHARCOAL_H    = (46, 38, 70)      # faint top rim so the hump reads as form
VIOLET_SHADE  = (90, 42, 143)
CYAN          = (23, 232, 232)
MAGENTA       = (255, 47, 166)
MAGENTA_DIM   = (150, 30, 100)    # far-side legs sit back a stop
LIME          = (182, 255, 60)


def _neon_line(surf, color, start, end, core_w=1, glow=((3, 40),)):
    """A crisp core line plus one-or-more additive bloom passes. The bloom is
    what sells 'neon' — a wider, dimmer copy of the stroke ADDed under the core
    so overlaps brighten toward white instead of just stacking alpha."""
    for gw, ga in glow:
        bloom = _new()
        pygame.draw.line(bloom, (*color, ga), start, end, gw)
        surf.blit(bloom, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.line(surf, color, start, end, core_w)


def _neon_dot(surf, color, center, r, glow_r, glow_a):
    """Bright core dot with an additive halo (the eye / lamp look)."""
    bloom = _new()
    pygame.draw.circle(bloom, (*color, glow_a), center, glow_r)
    surf.blit(bloom, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.circle(surf, color, center, r)


def _ellipse_mask(rect):
    m = _new()
    pygame.draw.ellipse(m, (255, 255, 255, 255), rect)
    return m


def _mosq_wing(wing_angle_deg, *, bright=True, rot_bias=0.0):
    """A narrow hot-magenta membrane blade with a diagonal cyan shimmer. It is
    the flap element: at f=0 (wing down) it hangs tall and open, at f=1 (up) it
    squeezes to a slit. The far wing runs dimmer + rotated back for depth."""
    f = (wing_angle_deg + 40) / 90.0
    a_fill = 120 if bright else 58
    a_edge = 185 if bright else 95
    a_shim = 210 if bright else 110
    w = pygame.Surface((22, 46), pygame.SRCALPHA)
    pygame.draw.ellipse(w, (*MAGENTA, a_fill), (4, 2, 13, 42))
    pygame.draw.ellipse(w, (255, 120, 205, a_fill), (7, 8, 7, 26))
    pygame.draw.ellipse(w, (*MAGENTA, a_edge), (4, 2, 13, 42), 1)
    # Diagonal scanline shimmer across the blade.
    pygame.draw.line(w, (*CYAN, a_shim), (7, 38), (14, 8), 1)
    # Squeeze horizontally toward the up-pose so the blade reads as a slit.
    sx = 1.0 - 0.5 * f
    w = pygame.transform.smoothscale(w, (max(1, int(22 * sx)), 46))
    return pygame.transform.rotate(w, 30 + f * 34 + rot_bias)


def build_mosquito_neon(wing_angle_deg):
    surf = _new()
    f = (wing_angle_deg + 40) / 90.0

    # ── Far wing (behind everything, dim, swept further back) ───────────────
    fw = _mosq_wing(wing_angle_deg, bright=False, rot_bias=16)
    surf.blit(fw, fw.get_rect(center=(BCX + 6, BCY - 12)).topleft)

    # ── SIX legs, all glowing magenta neon (drawn before the body so their
    #    roots tuck under the thorax and only the dangling span lights up).
    #    Far triad first (dimmer + a stop back), then the bright near triad.
    far = [
        [(40, 45), (46, 51), (49, 57)],   # front
        [(34, 47), (33, 60)],             # mid
        [(27, 45), (24, 52), (20, 58)],   # rear
    ]
    near = [
        [(38, 46), (43, 52), (46, 59)],   # front (knee at 43,52)
        [(32, 48), (30, 62)],             # mid
        [(25, 46), (21, 53), (17, 60)],   # rear (knee at 21,53)
    ]
    for leg in far:
        for a, b in zip(leg, leg[1:]):
            _neon_line(surf, MAGENTA_DIM, a, b, core_w=1, glow=((3, 26),))
    for leg in near:
        for a, b in zip(leg, leg[1:]):
            _neon_line(surf, MAGENTA, a, b, core_w=1, glow=((3, 44),))

    # ── Charcoal abdomen: a tapered barrel sweeping back-left to a point ─────
    ab_rect = (BCX - 19, BCY - 3, 26, 15)
    pygame.draw.ellipse(surf, CHARCOAL, ab_rect)
    pygame.draw.polygon(surf, CHARCOAL,
                        [(BCX - 17, BCY - 1), (11, BCY + 4), (BCX - 15, BCY + 9)])

    # Alternating cyan / magenta neon banding, clipped to the abdomen shape and
    # then re-added faintly so the bands themselves glow.
    stripes = _new()
    for i, sx in enumerate(range(BCX - 15, BCX + 5, 3)):
        col = CYAN if i % 2 == 0 else MAGENTA
        pygame.draw.line(stripes, (*col, 200), (sx, BCY - 6), (sx - 3, BCY + 12), 2)
    stripes.blit(_ellipse_mask(ab_rect), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(stripes, (0, 0))
    surf.blit(stripes, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # ── Charcoal thorax hump over the abdomen root ──────────────────────────
    pygame.draw.ellipse(surf, CHARCOAL, (BCX - 6, BCY - 12, 22, 20))
    # Violet under-shade + a cool top rim so the matte hump still has form.
    pygame.draw.ellipse(surf, VIOLET_SHADE, (BCX - 4, BCY - 2, 18, 9))
    pygame.draw.ellipse(surf, CHARCOAL, (BCX - 6, BCY - 12, 22, 18))
    pygame.draw.arc(surf, CHARCOAL_H, (BCX - 5, BCY - 12, 20, 18),
                    0.5, 2.6, 2)

    # ── Near wing (bright, over the thorax) ─────────────────────────────────
    nw = _mosq_wing(wing_angle_deg, bright=True)
    surf.blit(nw, nw.get_rect(center=(BCX + 1, BCY - 14)).topleft)

    # ── Head ────────────────────────────────────────────────────────────────
    pygame.draw.ellipse(surf, CHARCOAL, (HCX - 8, HCY - 8, 16, 16))
    pygame.draw.arc(surf, CHARCOAL_H, (HCX - 8, HCY - 8, 16, 16), 0.4, 2.4, 2)

    # ── HERO 1: single lime compound-eye dot with bloom + a hot glint ───────
    _neon_dot(surf, LIME, (HCX, HCY), 5, 9, 70)
    pygame.draw.circle(surf, (245, 255, 210), (HCX - 2, HCY - 2), 1)

    # ── HERO 2: cyan glowing proboscis needle + two palp stubs ──────────────
    _neon_line(surf, CYAN, (44, 36), (63, 34), core_w=2,
               glow=((4, 60), (7, 30)))
    _neon_line(surf, CYAN, (45, 38), (54, 39), core_w=1, glow=((3, 34),))
    _neon_line(surf, CYAN, (45, 33), (53, 30), core_w=1, glow=((3, 34),))

    return surf


build = _make_prebuilt_skin(build_mosquito_neon)
