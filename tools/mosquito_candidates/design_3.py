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
    """A narrow hot-magenta membrane blade with a diagonal cyan shimmer. Kept
    small and swept hard back over the thorax so the BODY stays the largest
    mass — a near-vertical blade reads as a prawn tail, not a mosquito wing.
    At f=0 (wing down) it hangs open, at f=1 (up) it squeezes to a slit; the
    far wing runs dimmer + rotated further back for depth."""
    f = (wing_angle_deg + 40) / 90.0
    a_fill = 105 if bright else 50
    a_edge = 170 if bright else 88
    a_shim = 195 if bright else 100
    w = pygame.Surface((15, 32), pygame.SRCALPHA)
    pygame.draw.ellipse(w, (*MAGENTA, a_fill), (3, 2, 9, 28))
    pygame.draw.ellipse(w, (255, 120, 205, a_fill), (5, 7, 5, 16))
    pygame.draw.ellipse(w, (*MAGENTA, a_edge), (3, 2, 9, 28), 1)
    # Single diagonal scanline shimmer across the blade.
    pygame.draw.line(w, (*CYAN, a_shim), (5, 25), (10, 6), 1)
    # Squeeze horizontally toward the up-pose so the blade reads as a slit.
    sx = 1.0 - 0.5 * f
    w = pygame.transform.smoothscale(w, (max(1, int(15 * sx)), 32))
    # High base rotation sweeps the blade up-AND-back over the thorax.
    return pygame.transform.rotate(w, 46 + f * 26 + rot_bias)


def build_mosquito_neon(wing_angle_deg):
    surf = _new()
    f = (wing_angle_deg + 40) / 90.0

    # ── Far wing (behind everything, dim, swept further back) ───────────────
    fw = _mosq_wing(wing_angle_deg, bright=False, rot_bias=16)
    surf.blit(fw, fw.get_rect(center=(BCX + 4, BCY - 14)).topleft)

    # ── SIX dangling legs — the second non-negotiable mosquito tell. Three per
    #    side, splayed into a fan and hung well BELOW the body, each with a
    #    visible knee (down, then kicked back) so it reads jointed. Roots tuck
    #    under the body (drawn first); the dangling span is what lights up.
    #    Glow is kept TIGHT (2px) so neighbouring legs stay separated rather
    #    than merging into a blob at the 40px downscale.
    far = [
        [(38, 47), (42, 54), (40, 61)],   # front
        [(30, 48), (30, 57), (26, 63)],   # mid
        [(23, 47), (19, 54), (14, 60)],   # rear
    ]
    near = [
        [(40, 48), (45, 55), (42, 63)],   # front — knee kicks forward-back
        [(32, 49), (33, 58), (28, 65)],   # mid
        [(24, 48), (20, 56), (15, 63)],   # rear
    ]
    for leg in far:
        for a, b in zip(leg, leg[1:]):
            _neon_line(surf, MAGENTA_DIM, a, b, core_w=1, glow=((2, 20),))
    for leg in near:
        for a, b in zip(leg, leg[1:]):
            _neon_line(surf, MAGENTA, a, b, core_w=1, glow=((2, 34),))

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

    # ── Near wing (bright, swept back over the thorax) ──────────────────────
    nw = _mosq_wing(wing_angle_deg, bright=True)
    surf.blit(nw, nw.get_rect(center=(BCX - 1, BCY - 16)).topleft)

    # ── Head ────────────────────────────────────────────────────────────────
    pygame.draw.ellipse(surf, CHARCOAL, (HCX - 8, HCY - 8, 16, 16))
    pygame.draw.arc(surf, CHARCOAL_H, (HCX - 8, HCY - 8, 16, 16), 0.4, 2.4, 2)

    # ── HERO 1: the proboscis is a RIGID FORWARD NEEDLE — the primary tell.
    #    A tapered cyan tube (2px base → 1px point) running ~19px forward off
    #    the head, with a 1px charcoal core so it reads as an edge-lit solid
    #    needle and not a diffuse flashlight beam. Faint outer glow only.
    p_base, p_tip = (44, 36), (63, 33)
    beam = _new()
    pygame.draw.line(beam, (*CYAN, 34), p_base, p_tip, 3)
    surf.blit(beam, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.polygon(surf, CYAN, [(44, 35), (44, 37), p_tip])
    pygame.draw.line(surf, CHARCOAL, (45, 36), (61, 33), 1)

    # ── HERO 2: a SMALL lime compound eye, high on the head. Deliberately
    #    tiny (≈3px core + a 2px halo) so the neon linework — not one blown-out
    #    orb — carries the synthwave look. This is a mosquito, not a firefly.
    _neon_dot(surf, LIME, (42, 31), 2, 4, 90)

    # ── Focal apex: the single brightest, tightest highlight sits at the
    #    head/proboscis junction, pulling the eye forward along the needle.
    _neon_dot(surf, (225, 255, 255), (50, 35), 1, 3, 150)

    return surf


build = _make_prebuilt_skin(build_mosquito_neon)
