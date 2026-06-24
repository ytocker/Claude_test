"""v2_design_1 — BONEWHITE-MACAW: the definitive clean PARROT skeleton.

Evolves the v1 BONEWHITE winner with the corrected anatomy from ``_v2_anatomy``:
pure-white bone on a near-black flesh floor, but now unmistakably a *parrot* —
a big hooked bone beak and a long bony tail. No theme gear; the value split and
the silhouette carry it. Scratch only — never registered in BUILDERS.

This is the no-gear baseline, so its whole job is a crisp, unmistakable read.
The shared anatomy is correct but the mid-body tangles (wing finger-bones cross
the ribcage/spine) and the head can lose its hooked-beak tell. We DON'T touch
the shared module — instead we suppress the shared wing, then in a ``post`` hook
(which draws on top) we lay down a de-tangled, up-and-back-SEATED wing with a
1px dark gap off the ribcage, re-stamp the skull + hooked beak LAST so the head
is always the brightest forward shape, and re-key the tail terminal so the long
bony tail clearly extends back-left. All local to this file.
"""
import math
import pygame

from game.parrot import SPRITE_W, SPRITE_H, _aaellipse
from game.store_skins import _poly, _make_prebuilt_skin
from tools.skeleton_candidates import _v2_anatomy as A


P = A.WHITE


# ── a wing that seats UP-AND-BACK off the chest, with a hard root knuckle ─────
# The shared finger_wing radiates from a wrist near the body centre, so when it
# rotates it sweeps its struts straight across the ribcage/spine. We rebuild it
# anchored on its own dark wrist knuckle and add a deep keyline cuff so a 1px
# dark gap always separates the wing root from the ribcage underneath.
def _seated_wing(angle_deg):
    w = pygame.Surface((58, 58), pygame.SRCALPHA)
    wrist = (24, 32)
    # Top finger kept short of the cranium height so the wing never crests
    # over the skull and steal the head's "brightest top shape" read.
    tips = ((50, 18), (53, 30), (42, 46))   # three radiating finger-bones
    # Dark cuff/socket so the wing reads as a separate clattering limb, never
    # fused to the chest it overlaps.
    pygame.draw.circle(w, P.body_deep, wrist, 6)
    for tip in tips:
        pygame.draw.line(w, P.keyline, wrist, tip, 4)
        pygame.draw.circle(w, P.keyline, tip, 3, 1)
    pygame.draw.circle(w, P.keyline, wrist, 5)
    for i, tip in enumerate(tips):
        col = P.bone if i < 2 else P.bone_sh
        pygame.draw.line(w, col, wrist, tip, 2)
        pygame.draw.circle(w, P.bone, tip, 2)
        mid = ((wrist[0] + tip[0]) // 2, (wrist[1] + tip[1]) // 2)
        pygame.draw.circle(w, P.bone_sh, mid, 1)     # finger joint pip
    pygame.draw.circle(w, P.bone, wrist, 3)
    pygame.draw.circle(w, P.body_deep, wrist, 1)
    return pygame.transform.rotate(w, angle_deg)


def _post(surf, angle_deg, Pl):
    # Wing seated up-and-back, its dark cuff carving a gap off the ribcage.
    img = _seated_wing(angle_deg)
    surf.blit(img, img.get_rect(center=(26, 22)).topleft)

    # Re-stamp skull + hooked beak ON TOP so the head stays the brightest
    # forward shape and the wing never crosses the face.
    A.skull(surf, Pl)
    A.beak(surf, Pl)

    # Brighten + sharpen the hook so the down-curved tell survives at 40px: a
    # bone-bright cap on the hooked point and a clean dark gape make the upper
    # mandible clearly curl DOWN past the jaw rather than read as a flat snout.
    pygame.draw.circle(surf, Pl.bone, (60, 26), 2)           # hooked tip cap
    pygame.draw.line(surf, Pl.bone, (54, 11), (62, 17), 1)   # ridge keyline
    pygame.draw.line(surf, Pl.body_deep, (50, 18), (59, 25), 2)  # deepen the gape

    # Extend + re-key the tail so the long bony tail clearly reads as the
    # back-left extension (the second parrot tell) instead of dissolving into
    # the leg cluster: a bright pygostyle stub reaching past the body edge plus
    # a bone-bright terminal cap.
    pygame.draw.line(surf, Pl.keyline, (8, 42), (0, 48), 4)
    pygame.draw.line(surf, Pl.bone, (8, 42), (0, 48), 2)
    pygame.draw.circle(surf, Pl.keyline, (0, 48), 3, 1)
    pygame.draw.circle(surf, Pl.bone, (0, 48), 2)


def _build(wing_angle_deg):
    # Suppress the shared wing; our ``post`` lays down the de-tangled one.
    return A.build_skeleton(wing_angle_deg, P, post=_post, draw_wing=False)


build = _make_prebuilt_skin(_build)
