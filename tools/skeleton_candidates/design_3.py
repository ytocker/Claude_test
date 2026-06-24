"""SKELETON costume redesign — design_3 WISP (spectral ghost-fire skeleton).

Scratch exploration only. NEVER registered in store_skins.BUILDERS; production
art is untouched. WISP is the showpiece glow pick: semi-transparent spectral
green bones wreathed in an additive aura, twin flame-pips burning in the eye
sockets, lower body dissolving into wisp tendrils instead of solid legs.

The aura/halo + socket flames are painted onto a separate SRCALPHA layer and
blitted with BLEND_RGB_ADD so they bloom on a dark night sky (the night flex);
the bone is then stamped on top with solid 2px edges so the skeleton read
survives even where the glow flattens out on a bright day sky.
"""
from __future__ import annotations
import math

import pygame

from game.store_skins import SPRITE_W, SPRITE_H, _poly, _make_prebuilt_skin
from game.parrot import _aaellipse


# ── WISP palette ─────────────────────────────────────────────────────────────
_W_CORE   = (201, 255, 227)        # #C9FFE3 bone core highlight — brightest
_W_BONE   = (84, 240, 160)         # #54F0A0 spectral green bone — THEME
_W_BONE_D = (40, 168, 120)         # darker bone underside for roundness
_W_AURA   = (25, 200, 166)         # #19C8A6 aura mid-glow — additive
_W_FLESH  = (11, 42, 36)           # #0B2A24 dark translucent flesh base
_W_FLAME  = (140, 255, 230)        # cyan-green socket flame core
_W_SOCK   = (4, 18, 16)            # near-black hollow socket behind the flame


def _add_glow(layer, color, center, radius, peak=160):
    """Stack translucent circles into a soft radial bloom on the additive
    layer — concentric falloff reads as a halo once blitted with BLEND_RGB_ADD."""
    cx, cy = int(center[0]), int(center[1])
    steps = max(2, radius // 2)
    for i in range(steps, 0, -1):
        t = i / steps
        a = int(peak * (1.0 - t) ** 1.7)
        if a <= 0:
            continue
        pygame.draw.circle(layer, (color[0], color[1], color[2], a),
                           (cx, cy), int(radius * t))


def _flesh_ellipse(surf, center, rx, ry, alpha):
    """Semi-transparent flesh blob — kept translucent so the body reads
    ethereal rather than solid (the wispy ghost tell)."""
    tmp = pygame.Surface((rx * 2 + 2, ry * 2 + 2), pygame.SRCALPHA)
    _aaellipse(tmp, (*_W_FLESH, alpha), (rx + 1, ry + 1), rx, ry)
    surf.blit(tmp, (int(center[0] - rx - 1), int(center[1] - ry - 1)))


def _bone_line(surf, p0, p1, width=2):
    """A spectral bone segment: dark underside, theme green, then a core
    highlight pip at the joints so the bone reads luminous, not flat."""
    pygame.draw.line(surf, _W_BONE_D, p0, p1, width)
    pygame.draw.line(surf, _W_BONE, p0, p1, max(1, width - 1))


def _wisp_wing(angle_deg):
    """Skeletal wing: translucent membrane + radiating finger-bones that trail
    faint additive glow streaks, so the flap reads as a glowing clattering wing.
    Glow streaks live on their own additive layer baked into the returned frame.
    """
    pad = 16
    base = pygame.Surface((50 + pad * 2, 50 + pad * 2), pygame.SRCALPHA)
    glow = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    ox = oy = pad

    wrist = (24 + ox, 28 + oy)
    # Finger-bone tips fanning out along the wing edge.
    tips = [(46 + ox, 14 + oy), (50 + ox, 24 + oy),
            (44 + ox, 36 + oy), (32 + ox, 44 + oy)]

    # Translucent spectral membrane between the wrist and the finger tips.
    membrane = [wrist] + tips
    mem = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    _poly(mem, (*_W_FLESH, 120), membrane)
    base.blit(mem, (0, 0))

    # Glow streaks trailing each finger-bone (additive).
    for tx, ty in tips:
        _add_glow(glow, _W_AURA, (tx, ty), 7, peak=120)
        # streak back toward the wrist
        mx, my = (wrist[0] + tx) // 2, (wrist[1] + ty) // 2
        pygame.draw.line(glow, (*_W_AURA, 90), wrist, (mx, my), 3)
    base.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # Solid 2px finger-bones over the glow so the wing survives downscale.
    for tx, ty in tips:
        _bone_line(base, wrist, (tx, ty), 2)
        pygame.draw.circle(base, _W_CORE, (tx, ty), 2)
    pygame.draw.circle(base, _W_CORE, wrist, 2)        # bright wrist knob

    rot = pygame.transform.rotate(base, angle_deg)
    return rot


def _build_design3(wing_angle_deg):
    """Full WISP redraw on the 64×60 sprite canvas. Aura/flame bloom first on an
    additive layer, then translucent flesh, then solid bone on top."""
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # ── 1 · Additive aura layer — soft green halo, brightest at skull + rib core.
    glow = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    _add_glow(glow, _W_AURA, (33, 32), 22, peak=120)     # body/rib-core halo
    _add_glow(glow, _W_AURA, (47, 21), 18, peak=150)     # brightest at skull
    _add_glow(glow, _W_AURA, (16, 36), 12, peak=90)      # wispy tail haze
    # Twin socket flames — bright cyan-green bloom (the hero tell).
    _add_glow(glow, _W_FLAME, (50, 19), 7, peak=210)
    _add_glow(glow, _W_FLAME, (44, 20), 7, peak=210)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # ── 2 · Translucent flesh base — wispy tail dissolving into the haze.
    # Tail as a fading fan of three thin wisp tendrils instead of a solid fan.
    for ty, taper in ((26, 130), (32, 100), (38, 70)):
        _bone_line(surf, (22, ty), (8, ty + 4), 2)
        wisp = pygame.Surface((20, 12), pygame.SRCALPHA)
        pygame.draw.line(wisp, (*_W_AURA, taper), (18, 6), (2, 6 + (ty - 32) // 3), 2)
        surf.blit(wisp, (0, ty - 6), special_flags=pygame.BLEND_RGB_ADD)

    _flesh_ellipse(surf, (33, 33), 18, 13, 150)          # body
    _flesh_ellipse(surf, (47, 21), 11, 10, 170)          # head

    # ── 3 · Wing (additive streaks baked in) centred on the shoulder anchor.
    wing = _wisp_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # ── 4 · Luminous vertebra SPINE — bright near the skull, dimming downward.
    spine = [(40, 24), (36, 28), (31, 32), (26, 35), (22, 37)]
    for i in range(len(spine) - 1):
        _bone_line(surf, spine[i], spine[i + 1], 2)
    for i, (vx, vy) in enumerate(spine):
        c = _W_CORE if i == 0 else _W_BONE
        pygame.draw.circle(surf, c, (vx, vy), 2 if i < 2 else 1)

    # ── 5 · Glowing rib-arcs across the chest.
    for off_x in (-5, 0, 5):
        rect = (24 + off_x, 24, 13, 16)
        pygame.draw.arc(surf, _W_BONE_D, rect,
                        math.radians(200), math.radians(340), 2)
        pygame.draw.arc(surf, _W_BONE, rect,
                        math.radians(202), math.radians(338), 2)

    # ── 6 · Spectral SKULL — green dome with hollow sockets + flame pips.
    _aaellipse(surf, _W_BONE_D, (47, 22), 10, 9)
    _aaellipse(surf, _W_BONE, (47, 21), 9, 8)
    _aaellipse(surf, _W_CORE, (45, 18), 4, 3)            # crown highlight
    _aaellipse(surf, _W_BONE_D, (47, 25), 6, 3)          # jaw shadow

    # Hollow sockets, each holding a bright cyan-green flame pip.
    for sx, sy in ((50, 19), (44, 20)):
        pygame.draw.circle(surf, _W_SOCK, (sx, sy), 3)
        # Flame pip — teardrop core licking up out of the socket.
        _poly(surf, _W_FLAME, [(sx, sy - 4), (sx + 2, sy + 1), (sx - 2, sy + 1)])
        pygame.draw.circle(surf, (255, 255, 255), (sx, sy - 1), 1)

    # Nose hollow + a thin glowing tooth grin.
    _poly(surf, _W_SOCK, [(47, 23), (49, 23), (48, 25)])
    for gx in (44, 47, 50):
        pygame.draw.line(surf, _W_CORE, (gx, 27), (gx, 29), 1)

    # ── 7 · Beak — spectral bone outline over a translucent flesh beak.
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    _poly(surf, (*_W_FLESH, 160), beak_pts)
    pygame.draw.polygon(surf, _W_BONE, beak_pts, 2)

    # ── 8 · Thin glowing leg-bones fading into wisp tendrils at the feet.
    for hipx, kneex, footx in ((28, 27, 25), (34, 35, 37)):
        _bone_line(surf, (hipx, 43), (kneex, 47), 2)
        pygame.draw.circle(surf, _W_CORE, (kneex, 47), 1)      # knee knob
        # Foot dissolves into an additive downward wisp instead of a claw.
        foot = pygame.Surface((10, 12), pygame.SRCALPHA)
        for k in range(3):
            a = 130 - k * 40
            pygame.draw.line(foot, (*_W_AURA, a),
                             (5, 0), (5 + (k - 1) * 3, 10), 2)
        surf.blit(foot, (footx - 5, 47), special_flags=pygame.BLEND_RGB_ADD)

    return surf


# Scratch getter — wrapped exactly like the production skeleton redraw so the
# render harness can call it as a candidate `build(frame_idx, tilt_deg)`.
build = _make_prebuilt_skin(_build_design3)
