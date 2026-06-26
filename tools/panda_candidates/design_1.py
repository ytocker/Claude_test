"""CLASSIC PANDA — design_1 (scratch candidate builder).

The definitive giant panda: a storybook black-and-white read with no prop.
The whole skin lives or dies on the panda mask — a round white face disc,
two round black ears past the crown, and two black teardrop eye patches
angled down-inward. That mask is the most recognisable animal silhouette
on Earth, so it is what carries the 40px in-motion read; everything else
(black arm masses over the wings, white belly disc, dark shoulder yoke,
two leg stubs) frames it without competing for the eye.

Geometry follows game/animal_skins.py exactly: the body mass stays on the
base bird's BODY centre so the fixed 14px collision circle keeps lining up,
and the ears reach into the tall-canvas headroom. The candidate is rendered
in-gameplay by tools/ninja_render.py; nothing here touches production art.
"""
import pygame

from game import parrot
from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse

# ── composite + anchors (mirror game/animal_skins.py) ────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # body centre → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre → (44, 34)
CROWN_Y  = 12 + DY              # top of head → 24

# ── palette ──────────────────────────────────────────────────────────────────
PANDA_BLACK   = (26, 26, 26)        # #1A1A1A
PANDA_WHITE   = (245, 245, 245)     # #F5F5F5
WHITE_SHADE   = (232, 232, 234)     # #E8E8EA
BLACK_HI      = (58, 58, 64)        # #3A3A40 soft highlight on ears/arms
PINK          = (231, 169, 169)     # #E7A9A9 cheek / nose-tip accent
GLINT         = (255, 255, 255)
NOSE_PINK     = (210, 150, 150)     # slightly deeper pink under the nose tip


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _rot_blit(surf, wing, anchor):
    surf.blit(wing, wing.get_rect(center=anchor).topleft)


def _panda_arm(angle_deg):
    """A black furry arm mass that wraps a wing root. Flapping reads as the
    panda raising its arms — the silhouette-breaker on the body's flanks. A
    soft top highlight keeps the black mass from going flat."""
    w = pygame.Surface((44, 44), pygame.SRCALPHA)
    pts = [(22, 22), (40, 17), (41, 30), (24, 38), (13, 31)]
    pygame.draw.polygon(w, PANDA_BLACK, pts)
    # Rounded paw cap so the limb ends in a soft mitt, not a sharp point.
    pygame.draw.circle(w, PANDA_BLACK, (38, 24), 6)
    pygame.draw.circle(w, BLACK_HI, (24, 23), 4)      # plush top sheen
    pygame.draw.line(w, BLACK_HI, (23, 24), (37, 20), 1)
    return pygame.transform.rotate(w, angle_deg)


def build(wing_angle_deg) -> pygame.Surface:
    """Draw one 64×84 SRCALPHA frame of the Classic Panda. No outline here —
    the prebuilt getter runs every frame through parrot._add_outline."""
    surf = _new()

    # ── two black leg stubs hanging under the body ──
    for lx in (BCX - 8, BCX + 8):
        _aaellipse(surf, PANDA_BLACK, (lx, BCY + 15), 5, 7)
        pygame.draw.circle(surf, PANDA_BLACK, (lx, BCY + 19), 4)   # rounded foot
        pygame.draw.circle(surf, BLACK_HI, (lx - 1, BCY + 12), 2)

    # ── white torso / belly disc over the collision centre ──
    _aaellipse(surf, WHITE_SHADE, (BCX + 1, BCY + 1), 19, 18)
    _aaellipse(surf, PANDA_WHITE, (BCX, BCY), 18, 17)
    # Soft belly shading low-centre so the white disc has volume.
    _aaellipse(surf, WHITE_SHADE, (BCX, BCY + 7), 12, 8)

    # ── black shoulder yoke wrapping across the upper back ──
    # The real panda's dark band joins both arms over the shoulders; drawn as
    # a wide flattened cap that the white belly sits below.
    yoke = pygame.Surface((52, 26), pygame.SRCALPHA)
    pygame.draw.ellipse(yoke, PANDA_BLACK, pygame.Rect(0, 0, 52, 26))
    # Carve the lower edge away so the band hugs the shoulders, not the belly.
    pygame.draw.ellipse(yoke, (0, 0, 0, 0), pygame.Rect(2, 12, 48, 26))
    surf.blit(yoke, (BCX - 26, BCY - 17))

    # ── far arm tucked behind the body ──
    _rot_blit(surf, _panda_arm(wing_angle_deg * 0.5 - 18), (BCX + 9, BCY - 3))

    # ── round white face disc centred over the head ──
    # Two round black ears FIRST, so the white disc overlaps their base and
    # the ears read as sitting up past the crown rather than pasted on.
    for ex in (HCX - 9, HCX + 9):
        _aaellipse(surf, PANDA_BLACK, (ex, CROWN_Y + 1), 6, 6)
        pygame.draw.circle(surf, BLACK_HI, (ex - 1, CROWN_Y - 1), 2)

    _aaellipse(surf, WHITE_SHADE, (HCX + 1, HCY + 1), 13, 13)
    _aaellipse(surf, PANDA_WHITE, (HCX, HCY), 12, 12)

    # ── two black teardrop eye patches, angled down-inward ──
    # Each is a tilted ellipse: wide near the nose, tapering up-and-out, so the
    # pair points toward the muzzle like the real panda mask. Built on its own
    # surface so the rotation can splay them symmetrically.
    for sgn in (-1, 1):
        patch = pygame.Surface((20, 24), pygame.SRCALPHA)
        _aaellipse(patch, PANDA_BLACK, (10, 12), 6, 9)
        patch = pygame.transform.rotate(patch, sgn * 32)
        pcx = HCX + sgn * 5
        _rot_blit(surf, patch, (pcx, HCY - 1))

    # White eye-glint dot inside each patch — keeps the mask friendly, not
    # menacing. Sits high-inner where a real eye catches light.
    for sgn in (-1, 1):
        ecx = HCX + sgn * 5
        pygame.draw.circle(surf, PANDA_BLACK, (ecx, HCY), 1)  # pupil anchor
        pygame.draw.circle(surf, GLINT, (ecx - sgn * 1, HCY - 1), 2)

    # ── little black nose triangle + soft mouth line ──
    nose = [(HCX - 3, HCY + 6), (HCX + 3, HCY + 6), (HCX, HCY + 10)]
    pygame.draw.polygon(surf, PANDA_BLACK, nose)
    pygame.draw.circle(surf, NOSE_PINK, (HCX, HCY + 7), 1)     # warm nose tip
    # Soft mouth: a shallow down-curve under the nose (two short strokes).
    pygame.draw.line(surf, PANDA_BLACK, (HCX, HCY + 10), (HCX - 3, HCY + 12), 1)
    pygame.draw.line(surf, PANDA_BLACK, (HCX, HCY + 10), (HCX + 3, HCY + 12), 1)

    # ── two soft pink-grey cheek blushes low on the white face ──
    for sgn in (-1, 1):
        blush = pygame.Surface((10, 8), pygame.SRCALPHA)
        _aaellipse(blush, (*PINK, 150), (5, 4), 5, 4)
        surf.blit(blush, (HCX + sgn * 9 - 5, HCY + 5 - 4))

    # ── near arm over the body (the flapping panda arm) ──
    _rot_blit(surf, _panda_arm(wing_angle_deg), (BCX - 5, BCY - 1))

    return surf


def _make_prebuilt_skin(build_fn):
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s
    return getter


get_skin = _make_prebuilt_skin(build)
