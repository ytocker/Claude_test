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
    # Additive bloom behind the whole bird — the night flex, pushed harder this
    # round (peaks 160/175) since dark sky has the headroom. Concentrated on the
    # torso + skull so it lifts the dense bone cluster; kept OFF the beak tip
    # (~x60) and tail tip (~x0) so those two parrot tells don't dissolve into the
    # halo. A faint rim-bloom traces the continuous spine line so the backbone
    # glows as a through-line at night. A separate additive surface keeps the
    # bloom from washing the opaque bone out when stamped on top.
    glow = pygame.Surface((A.SPRITE_W, A.SPRITE_H), pygame.SRCALPHA)
    _add_glow(glow, _AURA, (30, 33), 17, peak=160)     # torso / rib-core halo
    _add_glow(glow, _AURA, (45, 18), 13, peak=175)     # skull — brightest mass
    _add_glow(glow, _AURA, (16, 38), 9, peak=80)       # faint tail-root haze
    # Spine rim-bloom: a thin #54F0A0 additive trace along the through-line so the
    # backbone reads as one glowing arc at night (mid-green keeps it under the
    # opaque bright spine beads stamped later, not competing with them).
    spine_path = [(41, 24), (37, 27), (33, 30), (28, 33), (23, 35), (18, 35)]
    pygame.draw.lines(glow, (*P.bone_sh, 90), False, spine_path, 3)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def _fire(surf, angle_deg, P):
    # Socket flame-pip + a capped set of rising wisp sparks. Drawn LAST: first a
    # thin opaque re-emphasis that sets the day VALUE HIERARCHY (bright spine +
    # beak hook win; ribs + legs drop to mid so they support, not compete), then
    # the additive flame + sparks for the night flex. The dark socket hollow
    # behind the flame is what actually says "skull". The 40px day target is a
    # three-read trace: hooked beak → bright spine line → bright tail line.

    # ── SEPARATE tail from legs by ANGLE + a dark gap (top day fix) ──
    # The shared tail and the legs both exit the hips down-left at nearly the same
    # vector, so at 40px they fuse into one fan. Re-lay the bright tail core as a
    # SHALLOWER, LONGER horizontal sweep (out past the old tip toward the sprite
    # edge) so it reads as a long tail, not a leg; then drop a 1px dark keyline gap
    # between the tail root and the hip/leg cluster so the eye parts "one long
    # horizontal tail" from "two short vertical legs".
    tail_sweep = [(18, 35), (13, 38), (8, 40), (4, 42), (0, 44)]
    pygame.draw.lines(surf, P.keyline, False, tail_sweep, 4)
    pygame.draw.lines(surf, _CORE, False, tail_sweep, 2)
    pygame.draw.circle(surf, P.keyline, (0, 44), 3, 1)
    pygame.draw.circle(surf, _CORE, (0, 44), 2)            # bright terminal cap
    # 1px #062019 keyline gap between the tail root and the hips so they unfuse.
    pygame.draw.line(surf, P.keyline, (20, 38), (22, 43), 1)

    # ── DROP the legs to the mid value (#54F0A0) so the bright tail LINE wins ──
    # The shared anatomy stamps legs in bright `bone`; re-lay them in `bone_sh`
    # so the lower body recedes and the one bold bright tail line is unrivalled.
    for hx, fx in ((27, 26), (33, 34)):
        knee = (hx, 45)
        foot = (fx, 49)
        pygame.draw.line(surf, P.bone_sh, (hx, 41), knee, 2)
        pygame.draw.line(surf, P.bone_sh, knee, foot, 2)
        for dx in (-2, 0, 2):
            pygame.draw.line(surf, P.bone_deep, foot, (foot[0] + dx, foot[1] + 3), 1)

    # ── RECEDE the ribs to ONE darker mid so the spine reads as a single line ──
    # The shared ribcage stamps three bright-ish rib arcs that scatter the chest;
    # over-stamp them in `bone_deep` (the darkest bone shade) so they sink to a
    # quiet supporting ladder and the only bright thing crossing the wing is the
    # spine. Also thicken the keyline directly under the spine so the bright core
    # spine pops off the mid-green wing/ribs around it.
    for i, ty in enumerate((30, 35, 40)):
        sx = 33 - i * 3
        pygame.draw.arc(surf, P.bone_deep, (sx - 12, ty - 5, 13, 12),
                        math.radians(20), math.radians(150), 2)
        pygame.draw.arc(surf, P.bone_deep, (sx - 1, ty - 5, 13, 12),
                        math.radians(30), math.radians(160), 2)

    # ── opaque spine re-emphasis (no blend) — the bright through-line read ──
    # Continuous bright core line UNDER re-capped beads so the backbone is one
    # unbroken bright stroke where the wing crosses it (beads alone scatter). A
    # 4px keyline under-stroke (1px fatter than the bead rim) walls the bright
    # spine off the receded mid ribs/wing so it pops as one clean line.
    spine_path = [(41, 24), (37, 27), (33, 30), (28, 33), (23, 35), (18, 35)]
    pygame.draw.lines(surf, P.keyline, False, spine_path, 4)
    pygame.draw.lines(surf, _CORE, False, spine_path, 1)
    for vx, vy in spine_path:
        pygame.draw.circle(surf, P.keyline, (vx, vy), 3, 1)
        pygame.draw.circle(surf, _CORE, (vx, vy), 2)
    # Thin the hip/leg-root dots so the rib ladder isn't lost in body clutter.
    pygame.draw.circle(surf, P.bone_sh, (27, 41), 1)
    pygame.draw.circle(surf, P.bone_sh, (33, 41), 1)

    # Dark hollow socket behind the flame keeps it a SKULL, not a green dot.
    pygame.draw.circle(surf, P.socket, (45, 16), 4)

    # ── carve the beak NOTCH + re-lay the hook top-edge at the NEW geometry ──
    # Dark #062019 keyline notch at the cranium↔beak junction so the hook reads as
    # a separate forward bone — re-stamped the full y12→20 break so the green fill
    # can't soften the head into a rounded snout; then the upper-mandible top edge
    # lit in #C9FFE3 core along the NEW deepened down-hook (hook tip ~(55,32)) so
    # the down-curl breaks the head's round outline and the curl is unmistakable.
    pygame.draw.line(surf, P.keyline, (49, 12), (49, 20), 1)        # crisp notch
    top_edge = [(50, 9), (56, 10), (59, 14), (60, 19), (58, 26), (55, 32)]
    pygame.draw.lines(surf, _CORE, False, top_edge, 2)             # hook top-curl
    pygame.draw.circle(surf, _CORE, (55, 32), 1)                   # hooked tip nub

    # ── additive flame + capped wisp sparks (the night flex) ──
    spark = pygame.Surface((A.SPRITE_W, A.SPRITE_H), pygame.SRCALPHA)
    _add_glow(spark, _FLAME, (45, 16), 5, peak=200)        # socket flame bloom
    _poly(spark, (*_FLAME, 235), [(45, 11), (47, 16), (43, 16)])  # teardrop tongue
    pygame.draw.circle(spark, (240, 255, 248), (45, 14), 1)        # bright pip core
    # Capped rising sparks (4), seated on the mid-body / hip line only — never on
    # the beak or tail, so the lower body reads as a coherent ghost, not confetti.
    for sx, sy, a in ((43, 9, 120), (34, 25, 95), (27, 30, 80), (21, 34, 70)):
        pygame.draw.circle(spark, (*_FLAME, a), (sx, sy), 1)
    surf.blit(spark, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def _build(wing_angle_deg):
    return A.build_skeleton(wing_angle_deg, P, pre=_aura, post=_fire,
                            socket_fill=(10, 60, 44))


build = _make_prebuilt_skin(_build)
