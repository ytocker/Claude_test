"""SKELETON costume redesign — design_3 WISP (spectral ghost-fire skeleton).

Scratch exploration only. NEVER registered in store_skins.BUILDERS; production
art is untouched. WISP is the showpiece glow pick: semi-transparent spectral
green bones wreathed in an additive aura, twin flame-pips burning in the eye
sockets, lower body dissolving into wisp tendrils instead of solid legs.

The aura/halo + socket flames are painted onto a separate SRCALPHA layer and
blitted with BLEND_RGB_ADD so they bloom on a dark night sky (the night flex);
the bone is then stamped on top with solid 2px edges so the skeleton read
survives even where the glow flattens out on a bright day sky.

Round-2 read priority: the SKULL (dark hollow sockets), RIBS (dark inter-rib
negative space under bright core-green arcs), and SPINE (bright bead column)
must survive 40px on a DARK sky FIRST — the aura is a bonus, not the read. The
socket bloom is kept tight so the two sockets stay discrete points, and the
dark hollow behind each flame is what actually says "skull".
"""
from __future__ import annotations
import math

import pygame

from game.store_skins import SPRITE_W, SPRITE_H, _poly, _make_prebuilt_skin
from game.parrot import _aaellipse


# ── WISP palette ─────────────────────────────────────────────────────────────
_W_CORE   = (201, 255, 227)        # #C9FFE3 bone core highlight — brightest
_W_BONE   = (84, 240, 160)         # #54F0A0 spectral green bone — THEME
_W_BONE_D = (28, 120, 86)          # darker bone underside / inter-rib floor
_W_AURA   = (25, 200, 166)         # #19C8A6 aura mid-glow — additive
_W_FLESH  = (11, 42, 36)           # #0B2A24 dark translucent flesh base
_W_KEY    = (6, 32, 27)            # #06201B day keyline — darker than flesh
_W_FLAME  = (140, 255, 230)        # cyan-green socket flame core
_W_SOCK   = (3, 14, 12)            # near-black hollow socket behind the flame


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
    """Semi-transparent flesh blob — kept thin (low alpha) so the bone on top
    stays the brightest element and the ribs/spine read through it."""
    tmp = pygame.Surface((rx * 2 + 2, ry * 2 + 2), pygame.SRCALPHA)
    _aaellipse(tmp, (*_W_FLESH, alpha), (rx + 1, ry + 1), rx, ry)
    surf.blit(tmp, (int(center[0] - rx - 1), int(center[1] - ry - 1)))


def _bone_line(surf, p0, p1, width=2):
    """A spectral bone segment. The DAY read is the whole verdict: on bright
    sky the additive aura is dead weight, so the bone must carry the structure
    on opaque value alone. A dark keyline underlay (#0B2A24, full opacity) cuts
    the stroke out of the blue; the THEME green sits over it; the CORE highlight
    is the brightest opaque value and does the actual structural work."""
    pygame.draw.line(surf, _W_KEY, p0, p1, width + 2)      # dark day keyline
    pygame.draw.line(surf, _W_BONE_D, p0, p1, width + 1)
    pygame.draw.line(surf, _W_BONE, p0, p1, width)
    pygame.draw.line(surf, _W_CORE, p0, p1, max(1, width - 2))  # opaque core


def _tendril(surf, ox, oy, dx, dy, alpha, length, width=2):
    """A single graded additive wisp tendril streaming downward — the ghostly
    dissolve. Drawn on its own SRCALPHA scratch then added so it blooms."""
    pad = 4
    w = abs(dx) + width * 2 + pad * 2
    h = length + width * 2 + pad * 2
    t = pygame.Surface((w, h), pygame.SRCALPHA)
    sx = pad + (width if dx < 0 else 0) + max(0, -dx)
    pygame.draw.line(t, (*_W_AURA, alpha), (sx, pad), (sx + dx, pad + dy), width)
    surf.blit(t, (int(ox - sx), int(oy - pad)),
              special_flags=pygame.BLEND_RGB_ADD)


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

    # Translucent spectral membrane between the wrist and the finger tips —
    # kept faint so it never buries the chest bones beneath the shoulder.
    membrane = [wrist] + tips
    mem = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    _poly(mem, (*_W_FLESH, 90), membrane)
    base.blit(mem, (0, 0))

    # Glow streaks trailing the finger-bones (additive). Capped at 3 tips and
    # softened so the flap reads as a faint coherent glow-hint, not a particle
    # cloud — frames 2–3 were over-particled at gameplay scale.
    for tx, ty in tips[:3]:
        _add_glow(glow, _W_AURA, (tx, ty), 5, peak=90)
        # streak back toward the wrist
        mx, my = (wrist[0] + tx) // 2, (wrist[1] + ty) // 2
        pygame.draw.line(glow, (*_W_AURA, 70), wrist, (mx, my), 2)
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
    additive layer, then a thin translucent flesh, then the WING, then the bone
    structure (spine → ribs → skull → beak) stamped LAST so the bones win the
    read at 40px even where the glow flattens out."""
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Skull geometry — centred ~(47,21) r9; sockets pushed wide so they stay two
    # discrete dark points at 40px instead of blooming into one mass.
    skull_c = (47, 21)
    sock_r = (51, 19)
    sock_l = (43, 20)

    # ── 1 · Additive aura layer — soft green halo, brightest at skull + rib core.
    glow = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    _add_glow(glow, _W_AURA, (32, 33), 20, peak=110)     # body/rib-core halo
    _add_glow(glow, _W_AURA, skull_c, 16, peak=130)      # brightest at skull
    _add_glow(glow, _W_AURA, (16, 38), 11, peak=80)      # wispy tail haze
    # Twin socket flames — tight bloom so each socket stays a discrete point.
    _add_glow(glow, _W_FLAME, sock_r, 4, peak=150)
    _add_glow(glow, _W_FLAME, sock_l, 4, peak=150)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # ── 2 · Thin translucent flesh — wispy tail + body, kept low-alpha so bone wins.
    _flesh_ellipse(surf, (33, 33), 18, 13, 90)           # body (lightened)
    _flesh_ellipse(surf, skull_c, 11, 10, 110)           # head

    # Wispy dissolve below the hip line: graded value-fade tendrils streaming
    # down. Fade FLOOR raised 30→70 so the lower body holds a faint coherent
    # shape at gameplay scale instead of dissolving into confetti.
    for i, (hx, alpha) in enumerate(
            ((24, 130), (29, 105), (34, 85), (39, 70))):
        _tendril(surf, hx, 40, (i - 1) * 3 - 2, 16 - i * 2, alpha, 16)

    # ── 3 · Wing (additive streaks baked in) centred on the shoulder anchor.
    wing = _wisp_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # ── 4 · Luminous vertebra SPINE — stamped over the wing so the column reads.
    # Raised to 3px and capped with the OPAQUE core so the bead-column survives
    # the 40px day read where the additive halo flattens to nothing.
    spine = [(40, 23), (35, 27), (30, 31), (25, 34), (21, 36)]
    for i in range(len(spine) - 1):
        _bone_line(surf, spine[i], spine[i + 1], 3)
    for vx, vy in spine:
        pygame.draw.circle(surf, _W_KEY, (vx, vy), 4)      # day keyline seat
        pygame.draw.circle(surf, _W_BONE_D, (vx, vy), 3)   # dark seat
        pygame.draw.circle(surf, _W_CORE, (vx, vy), 2)     # bright opaque bead

    # ── 5 · Rib-arc LADDER across the chest. The DAY verdict lives here: the
    # opaque dark inter-rib floor (full alpha) holds the negative-space rhythm,
    # and each rib is capped in the OPAQUE CORE highlight (the brightest value)
    # so 4–5 distinct bars survive a 40px day read instead of smearing to a blob.
    rib_offs = (-6, -2, 2, 6, 10)        # 5 bars → 4–5 distinct rungs at 40px
    # Opaque dark floor behind the whole ladder keeps the inter-rib gaps black.
    for off_x in rib_offs:
        rect = (24 + off_x, 24, 13, 17)
        pygame.draw.arc(surf, _W_KEY, rect,
                        math.radians(196), math.radians(344), 4)   # day keyline floor
    for off_x in rib_offs:
        rect = (24 + off_x, 24, 13, 17)
        pygame.draw.arc(surf, _W_BONE_D, rect,
                        math.radians(200), math.radians(340), 3)   # dark underside
        pygame.draw.arc(surf, _W_CORE, rect,
                        math.radians(204), math.radians(336), 2)   # bright opaque rung

    # ── 6 · Spectral SKULL — green dome with two near-black hollow sockets.
    # Opaque dark keyline ring under the dome cuts the skull out of bright day
    # sky (the additive halo does this on night; this carries it on day).
    _aaellipse(surf, _W_KEY, (skull_c[0], skull_c[1] + 1), 11, 10)
    _aaellipse(surf, _W_BONE_D, (skull_c[0], skull_c[1] + 1), 10, 9)
    _aaellipse(surf, _W_BONE, skull_c, 9, 8)
    _aaellipse(surf, _W_CORE, (skull_c[0] - 3, skull_c[1] - 3), 4, 3)  # crown highlight
    _aaellipse(surf, _W_BONE_D, (skull_c[0], skull_c[1] + 4), 6, 3)    # jaw shadow

    # Hollow sockets — the dark hole is the skull tell; the flame is the spark
    # inside it. Big near-black hollow (r=4) survives the bloom; 1px gap keeps
    # the two holes from merging.
    for (sx, sy) in (sock_r, sock_l):
        pygame.draw.circle(surf, _W_SOCK, (sx, sy), 4)
        # Tight flame pip — small teardrop core licking up out of the hollow.
        _poly(surf, _W_FLAME, [(sx, sy - 3), (sx + 2, sy + 1), (sx - 2, sy + 1)])
        pygame.draw.circle(surf, (236, 255, 248), (sx, sy - 1), 1)

    # Nose hollow + a thin glowing tooth grin.
    _poly(surf, _W_SOCK, [(46, 24), (48, 24), (47, 26)])
    for gx in (44, 47, 50):
        pygame.draw.line(surf, _W_CORE, (gx, 27), (gx, 29), 1)

    # ── 7 · Beak — translucent flesh beak with a bright core-green top edge so
    # the forward facing stays legible in motion even when the body glow flares.
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    _poly(surf, (*_W_FLESH, 150), beak_pts)
    pygame.draw.polygon(surf, _W_BONE, beak_pts, 2)
    pygame.draw.line(surf, _W_CORE, (55, 21), (61, 24), 1)   # lit top edge

    # ── 8 · Thin glowing leg-bones fading into wisp tendrils at the feet.
    for hipx, kneex, footx in ((28, 27, 25), (34, 35, 37)):
        _bone_line(surf, (hipx, 42), (kneex, 46), 2)
        pygame.draw.circle(surf, _W_CORE, (kneex, 46), 1)      # knee knob
        # Foot dissolves into a couple of coherent downward wisps (floor raised
        # so the feet read as a faint shape, not scattered confetti).
        for k, a in enumerate((120, 85)):
            _tendril(surf, footx + (k - 1) * 2, 46, (k - 1) * 2, 10, a, 10)

    return surf


# Scratch getter — wrapped exactly like the production skeleton redraw so the
# render harness can call it as a candidate `build(frame_idx, tilt_deg)`.
build = _make_prebuilt_skin(_build_design3)
