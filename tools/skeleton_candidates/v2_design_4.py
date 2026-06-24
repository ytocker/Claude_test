"""v2_design_4 — WISP-MACAW: spectral ghost-fire parrot skeleton.

The ``_v2_anatomy`` parrot skeleton (hooked bone beak + long tail) rendered in
glowing spectral green. Two jobs sit in tension and the design resolves them on
opposite skies:

  • DAY (the hard read): additive bloom is dead weight on bright blue, so the
    structure has to ride on OPAQUE value alone — bright core-green bone
    (#C9FFE3) over a dark keyline (#062019). The palette puts the core in the
    brightest ``bone`` slot so every shared-anatomy strut/arc/bead is stamped in
    it; a thin ``post`` re-emphasis re-lays the spine beads, rib-core highlights
    and the beak edge ON TOP of the wing so skull → ribs → wing → tail parse
    instead of tangling into a green blob.
  • NIGHT (the flex): a graded additive aura blooms behind the bones and the eye
    sockets burn as flame-pips. The bloom is concentrated on the torso + skull
    and deliberately kept OFF the beak tip and tail tip so the two parrot tells
    stay sharp; wisp sparks are capped (4) and seated on the mid-body so the
    lower body never turns to confetti.

Scratch only — never registered in ``store_skins.BUILDERS``.
"""
import math

import pygame

from game.store_skins import _make_prebuilt_skin, _poly
from tools.skeleton_candidates import _v2_anatomy as A


# Bright spectral-green "bone" over a dark teal flesh. ``bone`` IS the #C9FFE3
# core (the brightest opaque value) so every shared-anatomy stroke carries the
# day read; ``bone_sh`` is the #54F0A0 mid for roundness; the #062019 keyline is
# darker than the flesh so the bright bone cuts cleanly out of bright sky.
P = A.Pal(
    bone=(201, 255, 227),       # #C9FFE3 core — brightest, the structural value
    bone_sh=(84, 240, 160),     # #54F0A0 mid green
    bone_deep=(22, 116, 88),    # deep green underside / socket rim
    body=(9, 38, 33),           # dark teal flesh floor
    body_deep=(5, 24, 21),
    keyline=(6, 32, 25),        # #062019 dark rim for the day read
    socket=(3, 16, 13),         # near-black hollow behind the flame
    glint=(228, 255, 242),
    rib=(84, 240, 160),         # ribs in the mid so the core caps pop on top
)

_AURA = (24, 200, 166)          # #19C8A6 aura mid-glow — additive
_FLAME = (150, 255, 224)        # cyan-green socket flame core
_CORE = (201, 255, 227)


def _add_glow(layer, color, center, radius, peak=150):
    """Concentric translucent falloff → a soft radial halo once BLEND_RGB_ADD'd."""
    cx, cy = int(center[0]), int(center[1])
    steps = max(2, radius // 2)
    for i in range(steps, 0, -1):
        t = i / steps
        a = int(peak * (1.0 - t) ** 1.7)
        if a <= 0:
            continue
        pygame.draw.circle(layer, (color[0], color[1], color[2], a),
                           (cx, cy), int(radius * t))


def _aura(surf, angle_deg, P):
    # Additive bloom behind the whole bird — the night flex. Concentrated on the
    # torso + skull so it lifts the dense bone cluster; kept OFF the beak tip
    # (~x60) and tail tip (~x2) so those two parrot tells don't dissolve into the
    # halo. A separate additive surface keeps the bloom from washing the opaque
    # bone out when stamped on top.
    glow = pygame.Surface((A.SPRITE_W, A.SPRITE_H), pygame.SRCALPHA)
    _add_glow(glow, _AURA, (30, 33), 17, peak=120)     # torso / rib-core halo
    _add_glow(glow, _AURA, (45, 18), 13, peak=135)     # skull — brightest mass
    _add_glow(glow, _AURA, (16, 38), 9, peak=70)       # faint tail-root haze
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def _fire(surf, angle_deg, P):
    # Socket flame-pip + a capped set of rising wisp sparks. Drawn LAST: first a
    # thin opaque re-emphasis of the spine/rib/beak core so the structure wins
    # the day read over the wing, then the additive flame + sparks for the night
    # flex. The dark socket hollow behind the flame is what actually says "skull".

    # ── opaque day re-emphasis (no blend) — re-lay the tells on top of the wing.
    # Spine bead column re-capped in the bright core so the vertebrae read where
    # the wing crosses the back.
    for vx, vy in ((41, 24), (37, 27), (33, 30), (28, 33), (23, 35), (18, 35)):
        pygame.draw.circle(surf, P.keyline, (vx, vy), 3, 1)
        pygame.draw.circle(surf, _CORE, (vx, vy), 2)
    # Rib-core caps — brighten the front rib arcs so 3 rungs stay distinct.
    for i, ty in enumerate((30, 35, 40)):
        sx = 33 - i * 3
        pygame.draw.arc(surf, _CORE, (sx - 12, ty - 5, 13, 12),
                        math.radians(40), math.radians(140), 1)
    # Dark hollow socket behind the flame keeps it a SKULL, not a green dot.
    pygame.draw.circle(surf, P.socket, (45, 16), 4)
    # Beak top-edge lit in the core so the hook stays the forward-most read.
    pygame.draw.line(surf, _CORE, (50, 11), (61, 16), 1)
    pygame.draw.line(surf, _CORE, (60, 16), (61, 21), 1)

    # ── additive flame + capped wisp sparks (the night flex) ──
    spark = pygame.Surface((A.SPRITE_W, A.SPRITE_H), pygame.SRCALPHA)
    _add_glow(spark, _FLAME, (45, 16), 4, peak=170)        # socket flame bloom
    _poly(spark, (*_FLAME, 230), [(45, 12), (47, 16), (43, 16)])  # teardrop tongue
    pygame.draw.circle(spark, (235, 255, 247), (45, 14), 1)
    # Capped rising sparks (4), seated on the mid-body / hip line only — never on
    # the beak or tail, so the lower body reads as a coherent ghost, not confetti.
    for sx, sy, a in ((43, 10, 110), (34, 25, 95), (27, 30, 80), (21, 34, 70)):
        pygame.draw.circle(spark, (*_FLAME, a), (sx, sy), 1)
    surf.blit(spark, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def _build(wing_angle_deg):
    return A.build_skeleton(wing_angle_deg, P, pre=_aura, post=_fire,
                            socket_fill=(10, 60, 44))


build = _make_prebuilt_skin(_build)
