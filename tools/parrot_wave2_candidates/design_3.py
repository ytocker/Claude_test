"""design_3 · BIOLUMEN MACAW — LEGENDARY wave-2 parrot exploration.

A creature of the deep given wings: an abyssal near-black Pip that emits its
OWN cold light. The legendary read, top to bottom, is the silhouette-breaking
ANGLERFISH LURE-STALK arcing up-and-forward off the crown with a white-hot orb
on its tip, a faint additive PLANKTON HALO of drifting motes behind the head
(the legendary tell), TEAL→LIME VEIN NETWORKS + belly PHOTOPHORE dots tracing
the dark plumage, and a sweeping translucent JELLY-FRILL tail replacing the
feather fan, shedding light-motes down-back into open sky. All colour is
emitted, not reflected — the distinctness from MAGMA (cold cyan vs warm) and
AURORA (deep-sea lantern vs cosmic ribbons).

Draw order matters: the halo, vein glow, jelly tail and motes must paint BEHIND
the outlined body, so this can't use store_skins._make_skin's body-first
_compose. Mirroring AURORA's getter, this is a custom back-aura pass — an
ADDITIVE under-glow buffer (so the emission blooms on dark night skies) plus an
OPAQUE bright-detail buffer (so the lure orb / vein cores / jelly spine survive
a bright day sky where additive washes out) — then the abyssal body, then the
front overlay (lure-stalk, vein lines, photophores, lens glints), then the
house outline, then the per-(frame, 3°-bucket) rotation cache.

The glow is BAKED into each of the 4 wing frames (no runtime particle hook):
the lure stalk sways and the jelly frill billows with the wing beat so the
emission still reads alive across the filmstrip. Exploration only — NEVER
registered in store_skins.BUILDERS.
"""
import math

import pygame

from game.parrot import _WING_ANGLES, _add_outline
from game.draw import blit_glow, lerp_color
from game.store_skins import (
    COMPOSITE_W, COMPOSITE_H, PARROT_DY, HX, HY, CROWN_Y,
)
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette (brief) ───────────────────────────────────────────────────────────
_NAVY   = (14, 26, 46)            # #0E1A2E abyssal navy body
_SHADOW = (10, 15, 26)            # #0A0F1A deep shadow
_TEAL   = (51, 240, 200)          # #33F0C8 biolumen teal
_LIME   = (168, 255, 110)         # #A8FF6E lure lime
_WHITE  = (234, 255, 250)         # #EAFFFA core glow-white
_DEEP   = (24, 60, 120)           # cool deep-blue for the jelly tail base

# Abyssal re-plumage: a deep navy-black body where every value sits in the
# near-dark so the emitted teal/lime light is the ONLY thing that reads bright.
# The chest/crown are nudged a touch cooler-blue so the dark mass doesn't go a
# flat void on a dark night sky; the belly is the deepest so the photophore dots
# pop. Lenses stay (Pip's aviators are the anchor) but tint glowing teal so the
# emissive theme reaches the face; the beak is darkened so nothing warm survives.
_BIOLUMEN_PAL = _pal(
    tail=[(10, 16, 28), (12, 20, 36), (16, 28, 50), (22, 38, 66)],
    tail_line=(8, 12, 22),
    body_shadow=(9, 14, 26),
    body_main=_NAVY,
    body_chest=(22, 38, 64),
    body_belly=(12, 20, 38),
    sheen=(80, 200, 220, 55),
    wing_main=(13, 23, 42),
    wing_dark=(8, 13, 24),
    wing_tip=(26, 46, 78),
    wing_secondary=None,
    wing_highlight=(60, 150, 170),
    head_shadow=(9, 14, 26),
    head_main=(16, 28, 50),
    head_cheek=(24, 42, 70),
    head_crown=(22, 40, 70),
    lens_frame=(40, 90, 110),
    lens_body=(8, 14, 26),
    lens_tint=(60, 220, 190, 150),
    lens_glint=(220, 255, 248),
    beak_main=(30, 60, 78),
    beak_dark=(10, 20, 32),
    beak_gloss=(120, 220, 220),
    foot=(28, 56, 74),
)


def _biolumen_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _BIOLUMEN_PAL)


# ── shared helpers ────────────────────────────────────────────────────────────

def _emit_mix(t):
    """Teal→lime emission ramp; t=0 cold teal at the deep base, t=1 hot lime."""
    return lerp_color(_TEAL, _LIME, max(0.0, min(1.0, t)))


def _flap_phase(angle_deg):
    """0 on the down-stroke (wing 50°) → 1 on the up-stroke (-40°). The lure
    stalk sways and the jelly frill billows wider on the up-beat so the baked
    emission still feels like a living, drifting creature across the 4 frames."""
    return 1.0 - (angle_deg + 40) / 90.0


def _bezier(p0, p1, p2, steps=12):
    """Quadratic-Bezier sample list so the lure stalk and jelly frills render as
    smooth curves, not the 3-point polylines that read as straight rods at
    40px."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        pts.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return pts


def _ring(cx, cy, r, a0, a1, steps=16):
    """Point list along a circular arc (radians) — the plankton-halo spine."""
    return [(cx + math.cos(a0 + (a1 - a0) * i / steps) * r,
             cy + math.sin(a0 + (a1 - a0) * i / steps) * r)
            for i in range(steps + 1)]


# ── geometry shared by the back glow + front overlay ──────────────────────────

def _lure_path(phase):
    """The anglerfish lure-stalk: springs from a point set BACK on the crown and
    arcs UP then FORWARD over the head, so the glowing orb hangs out past the
    brow — the silhouette-breaking signature. Sways forward on the up-beat."""
    sway = (phase - 0.5) * 4
    root = (HX - 5, CROWN_Y + 2)
    ctrl = (HX - 9, CROWN_Y - 16)                  # bow up-and-back first
    tip = (HX + 9 + sway, CROWN_Y - 21)            # then forward over the brow
    return _bezier(root, ctrl, tip), tip


def _jelly_paths(phase):
    """Three translucent jelly-frill membranes sweeping down-back where the
    feather fan was. Each is a tapering S that billows wider/longer on the
    up-beat (the creature 'pulsing'), pulling out into open sky behind the
    body — the lower silhouette break that sells the legendary tier."""
    bell = 1.0 + phase * 0.18                       # membrane billow
    paths = []
    for k in range(3):
        bx, by = 13, HY + 6 + k * 4
        reach = (20 + k * 2) * bell
        c1 = (bx - reach * 0.40, by + 3 + k)        # bow out
        c2 = (bx - reach * 0.80, by + 11 + k * 4)   # then down → S
        tip = (bx - reach, by + 17 + k * 6)
        paths.append(_bezier((bx, by), c1, c2, steps=7)
                     + _bezier(c2, ((c2[0] + tip[0]) / 2, tip[1] - 1), tip, 6))
    return paths


def _halo_spine():
    """Plankton halo — a wide arc wrapping the upper-rear of the head, sized
    larger than the skull so the additive ring of motes clears OUTSIDE the
    silhouette on the back flank where the lure doesn't crowd it."""
    return _ring(HX - 3, HY - 2, 21, math.radians(150), math.radians(305))


# ── back layer: halo + vein glow + jelly tail + drifting motes ────────────────

def _biolumen_back(surf, angle_deg):
    """Every glowing element lives here, BEHIND the outlined bird, so the house
    outline (grown from the bird's alpha mask) never boxes a bloom into a dark
    island. Two passes, both un-outlined:

      1. an ADDITIVE under-glow buffer — gives the halo, veins, lure orb, jelly
         frill and motes a soft lit bloom on dark night skies, where additive
         emission shines.
      2. an OPAQUE bright-detail buffer alpha-blitted ON TOP — the lure orb
         core, jelly-frill spines and the brightest mote dots as solid pixels
         over a thin deep-navy backing, so the emission ALSO survives a bright
         day sky where additive washes to nothing. A legendary reads on both."""
    phase = _flap_phase(angle_deg)
    lure_pts, lure_tip = _lure_path(phase)
    jelly = _jelly_paths(phase)
    halo = _halo_spine()

    # Drifting plankton motes: a fixed scatter (stable across frames) riding the
    # halo arc + shedding off the jelly tail, nudged by the flap so they drift.
    drift = (phase - 0.5) * 2
    halo_motes = [halo[2], halo[5], halo[8], halo[11], halo[14]]
    tail_motes = [(jelly[0][-1][0] - 3, jelly[0][-1][1] + 2 + drift),
                  (jelly[1][-1][0] - 1, jelly[1][-1][1] + 4),
                  (jelly[2][-1][0] - 4, jelly[2][-1][1] + 1 - drift)]

    # ── pass 1: additive under-glow (night) ──────────────────────────────────
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    # Plankton halo bloom — soft teal stamps stringing the arc so the whole ring
    # glows, the legendary tell on a dark sky.
    for i, (gx, gy) in enumerate(halo):
        if i % 2:
            blit_glow(glow, int(gx), int(gy), 7, _TEAL, alpha=90)
    # Jelly-frill bloom — teal→deep-blue stamps walking each membrane so the
    # tail reads as a glowing translucent fan, not a sliver.
    for k, path in enumerate(jelly):
        col = lerp_color(_TEAL, _DEEP, k / 2.0)
        for p in (path[2], path[len(path) // 2], path[-1]):
            blit_glow(glow, int(p[0]), int(p[1]), 6, col, alpha=95)
    # Vein-network bloom over the body + wing edge so the dark plumage looks lit
    # from within (the body glow stays soft so the orb still wins the read).
    for vx, vy in ((26, 50), (33, 47), (40, 49), (30, 55), (37, 56), (22, 52)):
        blit_glow(glow, vx, vy, 5, _TEAL, alpha=60)
    # Belly photophore bloom — a row of small hot dots.
    for px in (24, 29, 34, 39):
        blit_glow(glow, px, 60, 3, _LIME, alpha=80)
    # The lure ORB is the brightest emission anywhere — a tight white-hot core
    # over a wider teal bloom, so it blazes as the single hottest point.
    blit_glow(glow, int(lure_tip[0]), int(lure_tip[1]), 9, _TEAL, alpha=150)
    blit_glow(glow, int(lure_tip[0]), int(lure_tip[1]), 5, _WHITE, alpha=180)
    for mx, my in halo_motes + tail_motes:
        blit_glow(glow, int(mx), int(my), 3, _TEAL, alpha=90)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── pass 2: opaque bright detail (day + night) ───────────────────────────
    det = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _INK = (8, 16, 30)                              # thin deep backing for day

    # Jelly-frill membranes — a soft translucent teal→deep-blue band filling
    # between the spine and an offset edge, an ink backing, then a bright teal
    # spine, ending in a glint. The width + S-curve make it read as a living
    # jelly fan on a bright sky, the lower silhouette break.
    for k, path in enumerate(jelly):
        col = lerp_color(_TEAL, _DEEP, k / 2.0)
        edge = [(x, y + 4 + k) for x, y in path]
        pygame.draw.polygon(det, (*col, 95), path + edge[::-1])
        pygame.draw.lines(det, _INK, False, path, 5)
        pygame.draw.lines(det, col, False, path, 2)
        tipd = path[-1]
        pygame.draw.circle(det, _WHITE, (int(tipd[0]), int(tipd[1])), 2)

    # Plankton halo — a thin teal mote-ring: short bright dashes along the arc
    # over a faint ink ghost, reading as a string of glowing plankton on day.
    for i in range(0, len(halo) - 1, 2):
        a, b = halo[i], halo[i + 1]
        pygame.draw.line(det, _INK, a, b, 3)
        pygame.draw.line(det, _TEAL, a, b, 1)
    for mx, my in halo_motes:
        pygame.draw.circle(det, _WHITE, (int(mx), int(my)), 1)

    # Drifting tail motes — bright shed dots so the creature sheds light as it
    # flies; kept off the body so they read as motion in open sky.
    for mx, my in tail_motes:
        pygame.draw.circle(det, _INK, (int(mx), int(my)), 2)
        pygame.draw.circle(det, _TEAL, (int(mx), int(my)), 1)

    # Lure STALK + ORB — the hero. A 4px ink-backed stalk, a 2px teal core, then
    # a layered orb (deep ink ring → teal → lime halo → white-hot centre) so the
    # tip is unmistakably the brightest, silhouette-breaking point on BOTH skies.
    pygame.draw.lines(det, _INK, False, lure_pts, 4)
    pygame.draw.lines(det, _TEAL, False, lure_pts, 2)
    ox, oy = int(lure_tip[0]), int(lure_tip[1])
    pygame.draw.circle(det, _INK, (ox, oy), 6)
    pygame.draw.circle(det, _TEAL, (ox, oy), 5)
    pygame.draw.circle(det, _LIME, (ox, oy), 3)
    pygame.draw.circle(det, _WHITE, (ox, oy), 2)
    pygame.draw.circle(det, (255, 255, 255), (ox - 1, oy - 1), 1)

    surf.blit(det, (0, 0))


# ── front overlay: vein lines, photophores, lens glint ────────────────────────

def _biolumen_front(surf, angle_deg):
    """Painted OVER the body and INSIDE the masked layer, so only crisp opaque
    emission belongs here (soft bloom lives in _biolumen_back to dodge the
    outline): the glowing vein NETWORK tracing the body + wing edge, a row of
    belly PHOTOPHORE dots, a teal rim hugging the lit back edge, and a re-
    asserted aviator/beak so Pip survives the 40px downscale."""
    # Vein network — branching teal→lime lines crawling up the body and out the
    # wing edge, each a 2px core over the dark plumage so it reads as light under
    # the skin. Fixed (not random) so the 4 frames stay stable.
    veins = (
        [(22, 52), (27, 49), (33, 47), (40, 48)],          # spine sweep
        [(27, 49), (29, 55), (32, 60)],                     # belly branch
        [(33, 47), (37, 52), (39, 58)],                     # chest branch
        [(40, 48), (45, 46), (49, 47)],                     # wing-edge run
    )
    for vn in veins:
        pygame.draw.lines(surf, _SHADOW, False, vn, 3)      # dark channel
        pygame.draw.lines(surf, _TEAL, False, vn, 2)
    # Hot lime nodes where the veins branch — small glowing junctions.
    for nx, ny in ((27, 49), (33, 47), (40, 48)):
        pygame.draw.circle(surf, _LIME, (nx, ny), 1)

    # Belly photophore row — spotted glowing organs along the underside, a deep
    # ring around a hot core so each dot reads as a tiny lantern, not a fleck.
    for px in (24, 29, 34, 39):
        pygame.draw.circle(surf, _SHADOW, (px, 60), 2)
        pygame.draw.circle(surf, _LIME, (px, 60), 1)
        pygame.draw.circle(surf, _WHITE, (px, 59), 1)

    # Teal rim-light on the lit upper-back edge so the abyssal body is framed by
    # its own emission rather than reading as a flat void on either sky.
    pygame.draw.lines(surf, _TEAL, False,
                      [(16, 47), (15, 53), (18, 41)], 2)

    # Re-assert Pip at 40px: a bright glint on the teal-tinted near lens and a
    # sharpened beak edge so the macaw face survives the downscale.
    pygame.draw.circle(surf, _WHITE, (HX + 6, HY - 3), 2)
    pygame.draw.line(surf, _TEAL, (HX + 8, HY + 1), (HX + 13, HY + 4), 1)


# ── custom compose + getter (halo/veins/tail need a back layer) ───────────────

def _biolumen_getter():
    """back aura (halo + jelly tail + veins/orb glow) → abyssal body → front
    vein/photophore/rim overlay → house outline, then the per-(frame, 3°-bucket)
    rotation cache shared by every store skin.

    The outline is grown from the bird's alpha mask, so the faint additive halo
    + jelly bloom must NOT join the masked layer (a dark rim would wrap the glow
    and kill it). So outline the OPAQUE bird (body + front overlay) alone, then
    lay the soft back-aura UNDER it, padded to match the outline's 2px grow so
    the bird stays centred for the rotation maths."""
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        bird = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        bird.blit(_biolumen_base(wing_angle), (0, PARROT_DY))
        _biolumen_front(bird, wing_angle)
        bird = _add_outline(bird)

        aura = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
        pad = (bird.get_width() - COMPOSITE_W) // 2
        back = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _biolumen_back(back, wing_angle)
        aura.blit(back, (pad, pad))
        aura.blit(bird, (0, 0))
        return aura

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


build = _biolumen_getter()
