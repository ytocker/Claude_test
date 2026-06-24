"""v2_design_4 — WISP-MACAW: spectral ghost-fire parrot skeleton.

The ``_v2_anatomy`` parrot skeleton (hooked bone beak + long tail) rendered in
glowing spectral green: an additive aura bloom behind the bones (the night flex)
plus bright core-green bone that stays legible by day via opaque strokes and a
dark keyline. Eye sockets burn as green flame-pips. Scratch only.
"""
import pygame

from game.store_skins import _make_prebuilt_skin
from tools.skeleton_candidates import _v2_anatomy as A


# Bright spectral-green "bone" over a dark teal flesh; keyline carries the day
# read where the additive glow flattens.
P = A.Pal(
    bone=(201, 255, 227), bone_sh=(84, 240, 160), bone_deep=(20, 120, 92),
    body=(8, 34, 30), body_deep=(5, 22, 20), keyline=(6, 32, 27),
    socket=(4, 20, 16), glint=(224, 255, 240),
)

_AURA = (25, 200, 166)
_FLAME = (120, 255, 190)


def _aura(surf, angle_deg, P):
    # Additive bloom behind the whole bird — soft, night-flex glow. Drawn pre so
    # the opaque bone reads on top; a separate additive surface keeps it from
    # washing the bone out.
    glow = pygame.Surface((A.SPRITE_W, A.SPRITE_H), pygame.SRCALPHA)
    for r, a in ((16, 40), (11, 60), (7, 80)):
        pygame.draw.circle(glow, (*_AURA, a), (30, 30), r)
        pygame.draw.circle(glow, (*_AURA, a), (45, 18), r - 4)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def _fire(surf, angle_deg, P):
    # Socket flame-pip + a few rising wisp sparks (capped, not confetti).
    spark = pygame.Surface((A.SPRITE_W, A.SPRITE_H), pygame.SRCALPHA)
    pygame.draw.circle(spark, (*_FLAME, 200), (45, 16), 3)
    pygame.draw.circle(spark, (*_FLAME, 120), (45, 14), 2)
    for sx, sy in ((45, 11), (33, 24), (20, 32)):
        pygame.draw.circle(spark, (*_FLAME, 90), (sx, sy), 1)
    surf.blit(spark, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def _build(wing_angle_deg):
    return A.build_skeleton(wing_angle_deg, P, pre=_aura, post=_fire,
                            socket_fill=(10, 60, 44))


build = _make_prebuilt_skin(_build)
