"""v2_design_1 — BONEWHITE-MACAW: the definitive clean PARROT skeleton.

Evolves the v1 BONEWHITE winner with the corrected anatomy from ``_v2_anatomy``:
pure-white bone on a near-black flesh floor, but now unmistakably a *parrot* —
a big hooked bone beak and a long bony tail. No theme gear; the value split and
the silhouette carry it. Scratch only — never registered in BUILDERS.

This is the no-gear baseline, so its whole job is a crisp, unmistakable read.
The shared anatomy is now correct (proper down-hooked parrot beak, one bold
lengthened tail to the sprite edge, a continuous spine). Our only remaining job
is de-tangling the lower-left quadrant: the shared finger-wing radiates from a
wrist near the body centre, so its lowest strut drops into the leg/tail zone.
We suppress the shared wing and, in a ``post`` hook (which draws on top), lay
down a wing whose lowest finger is lifted to ~y40 so the whole wing sits clearly
ABOVE the spine — leaving the scan skull → ribs → wing(up) → spine → tail clean,
with the legs a separate short pair below. We then re-stamp the shared skull +
beak LAST so the head stays the brightest forward shape and the wing never
crosses the face. We trust the corrected shared beak/tail geometry and add NO
local beak hook or pygostyle re-draw. All local to this file.
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
    # over the skull and steals the head's "brightest top shape" read; the
    # LOWEST finger is lifted off the leg/tail zone so the whole wing seats
    # clearly above the spine instead of clotting into the lower-left limbs.
    tips = ((50, 18), (52, 28), (44, 40))   # three radiating finger-bones
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

    # Re-stamp the corrected shared skull + hooked beak ON TOP so the head stays
    # the brightest forward shape and the wing never crosses the face. We trust
    # the shared down-hook geometry — no local beak re-draw (it would fight the
    # re-cut anatomy). The shared tail already sweeps to the sprite edge, so no
    # local pygostyle re-key either.
    A.skull(surf, Pl)
    A.beak(surf, Pl)


def _build(wing_angle_deg):
    # Suppress the shared wing; our ``post`` lays down the de-tangled one.
    return A.build_skeleton(wing_angle_deg, P, post=_post, draw_wing=False)


build = _make_prebuilt_skin(_build)
