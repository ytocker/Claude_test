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
# Wing membrane sits between magenta and violet: dark enough that it never
# out-shouts the cyan needle, which is the hero the eye must land on first.
WING_MEMB     = (128, 44, 150)
WING_HILITE   = (168, 96, 178)


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
    # The wing is a supporting tell, not the hero — held to a violet whisper so
    # it never competes with the cyan needle for the eye's first landing.
    a_fill = 70 if bright else 34
    a_edge = 120 if bright else 60
    a_shim = 130 if bright else 66
    w = pygame.Surface((12, 26), pygame.SRCALPHA)
    pygame.draw.ellipse(w, (*WING_MEMB, a_fill), (2, 2, 8, 22))
    pygame.draw.ellipse(w, (*WING_HILITE, a_fill), (4, 6, 4, 13))
    pygame.draw.ellipse(w, (*WING_MEMB, a_edge), (2, 2, 8, 22), 1)
    # Single diagonal scanline shimmer across the blade.
    pygame.draw.line(w, (*CYAN, a_shim), (4, 20), (8, 5), 1)
    # Squeeze horizontally toward the up-pose so the blade reads as a slit.
    sx = 1.0 - 0.5 * f
    w = pygame.transform.smoothscale(w, (max(1, int(12 * sx)), 26))
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
        pygame.draw.line(stripes, (*col, 170), (sx, BCY - 6), (sx - 3, BCY + 12), 2)
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
    #    A cyan tube running ~21px forward off the head, layered with a tight
    #    inner bloom (2px) under two wider dimmer passes so it burns brightest
    #    at its own edge — the FIRST thing the eye catches on the 40px strip.
    #    A 1px charcoal core keeps it reading as an edge-lit solid needle and
    #    not a diffuse flashlight beam.
    p_base, p_tip = (44, 36), (65, 33)
    _neon_line(surf, CYAN, p_base, p_tip, core_w=2,
               glow=((2, 70), (4, 60), (7, 30)))
    pygame.draw.line(surf, CHARCOAL, (45, 36), (63, 33), 1)

    # ── HERO 2: a SMALL lime compound eye, high on the head. Deliberately
    #    tiny (≈3px core + a 2px halo) so the neon linework — not one blown-out
    #    orb — carries the synthwave look. This is a mosquito, not a firefly.
    _neon_dot(surf, LIME, (42, 31), 2, 4, 90)

    # ── Needle-root cap: a small dim highlight where the needle meets the head,
    #    launching the eye FORWARD along the proboscis. Kept quiet (glow_a 110)
    #    and tucked at the root so it can't be mistaken for a second eye.
    _neon_dot(surf, (225, 255, 255), (45, 36), 1, 3, 110)

    return surf


build = _make_prebuilt_skin(build_mosquito_neon)
