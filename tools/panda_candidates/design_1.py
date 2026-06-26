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
    """A compact black furry arm mass that sits on ONE flank of the body and
    flaps from its shoulder root. Kept short and rounded so it frames the white
    belly from the side instead of sweeping a diagonal sash across it; the pivot
    is at the surface centre (the shoulder) so rotation swings the paw, not the
    whole mass over the belly. A soft top sheen keeps the black from going flat."""
    w = pygame.Surface((32, 32), pygame.SRCALPHA)
    # A short stubby limb: shoulder root at centre, paw reaching straight down.
    # Kept narrow (±6 of the pivot) so when it is anchored on a flank it frames
    # the white belly from the side and never reaches across the midline.
    _aaellipse(w, PANDA_BLACK, (16, 20), 6, 9)
    pygame.draw.circle(w, PANDA_BLACK, (16, 26), 5)   # rounded paw mitt
    pygame.draw.circle(w, BLACK_HI, (15, 15), 3)      # plush top sheen
    return pygame.transform.rotate(w, angle_deg)


def build(wing_angle_deg) -> pygame.Surface:
    """Draw one 64×84 SRCALPHA frame of the Classic Panda. No outline here —
    the prebuilt getter runs every frame through parrot._add_outline."""
    surf = _new()

    # ── two black leg stubs hanging under the body ──
    for lx in (BCX - 7, BCX + 7):
        _aaellipse(surf, PANDA_BLACK, (lx, BCY + 16), 5, 7)
        pygame.draw.circle(surf, PANDA_BLACK, (lx, BCY + 20), 4)   # rounded foot
        pygame.draw.circle(surf, BLACK_HI, (lx - 1, BCY + 13), 2)

    # ── rounded black torso backing — a firm symmetrical bean ──
    # Drawn first as the body's silhouette so the white belly can be punched on
    # top; the black survives ONLY as a thin rim left/right/top of that belly,
    # which gives the side arm masses and shoulder yoke a base to read against.
    _aaellipse(surf, PANDA_BLACK, (BCX, BCY + 1), 22, 21)

    # ── large WHITE belly bean owning the central + lower torso ──
    # This is the dominant body value: a round, symmetrical white oval centred on
    # the collision point and pushed slightly low so it owns the lower third. A
    # bottom shade-rim under it reads as plush volume, never a diagonal sash.
    _aaellipse(surf, WHITE_SHADE, (BCX, BCY + 3), 18, 18)
    _aaellipse(surf, PANDA_WHITE, (BCX, BCY + 1), 17, 17)
    # Soft belly shading low-centre so the white bean has roundness.
    _aaellipse(surf, WHITE_SHADE, (BCX, BCY + 9), 10, 6)

    # ── thin black shoulder yoke capping the very top of the body ──
    # The real panda's dark band joins both arms over the shoulders; kept as a
    # shallow cap so it crowns the white belly without eating into it.
    yoke = pygame.Surface((44, 16), pygame.SRCALPHA)
    pygame.draw.ellipse(yoke, PANDA_BLACK, pygame.Rect(0, 0, 44, 16))
    # Carve the lower edge away so the band hugs the shoulders, not the belly.
    pygame.draw.ellipse(yoke, (0, 0, 0, 0), pygame.Rect(2, 8, 40, 18))
    surf.blit(yoke, (BCX - 22, BCY - 18))

    # ── far arm tucked on the body's right flank, behind everything ──
    _rot_blit(surf, _panda_arm(wing_angle_deg * 0.5 - 14), (BCX + 18, BCY + 1))

    # ── round white face disc centred over the head ──
    # Two round black ears FIRST, so the white disc overlaps their base and
    # the ears read as sitting up past the crown rather than pasted on.
    for ex in (HCX - 9, HCX + 9):
        _aaellipse(surf, PANDA_BLACK, (ex, CROWN_Y + 1), 6, 6)
        pygame.draw.circle(surf, BLACK_HI, (ex - 1, CROWN_Y - 1), 2)

    # The white disc must DOMINATE — it is the panda read. Two small black eye
    # patches sit ON this white, never the inverse, with a clear white bridge
    # straight down the centre so they always read as two distinct shapes.
    _aaellipse(surf, WHITE_SHADE, (HCX + 1, HCY + 1), 14, 13)
    _aaellipse(surf, PANDA_WHITE, (HCX, HCY), 13, 12)

    # ── two SMALL black teardrop eye patches, splayed off the white bridge ──
    # Each patch is a short tilted ellipse; its INNER edge is pushed outward to
    # ±9 from centre so a ≥2px clean white bridge survives down the muzzle in
    # every wing frame, and the nose below sits on white — eyes never fuse with
    # the nose. Wide-low, tapering up-and-out so the pair points at the nose.
    for sgn in (-1, 1):
        patch = pygame.Surface((16, 16), pygame.SRCALPHA)
        _aaellipse(patch, PANDA_BLACK, (8, 8), 4, 5)
        patch = pygame.transform.rotate(patch, sgn * 28)
        pcx = HCX + sgn * 9
        _rot_blit(surf, patch, (pcx, HCY - 2))

    # White eye-glint inside each patch — a bright eye keeps the mask friendly.
    for sgn in (-1, 1):
        ecx = HCX + sgn * 9
        pygame.draw.circle(surf, PANDA_BLACK, (ecx, HCY - 1), 1)  # pupil anchor
        pygame.draw.circle(surf, GLINT, (ecx - sgn * 1, HCY - 2), 2)

    # ── soft pink cheek blushes — small dots low and wide on mid-cheek white ──
    # Dropped ~4px below the eye line and pushed out to ±11 so they land on clean
    # mid-cheek white, clear of the patches; saturation bumped so they still
    # register at 40px without smudging into the eyes.
    for sgn in (-1, 1):
        blush = pygame.Surface((8, 6), pygame.SRCALPHA)
        _aaellipse(blush, (*PINK, 175), (4, 3), 3, 2)
        surf.blit(blush, (HCX + sgn * 11 - 4, HCY + 8 - 3))

    # ── nose + mouth re-asserted on the WHITE bridge below the patches ──
    # A tiny solid-black nose with a short down-mouth, clearly on white (visible
    # white above it and to each side) so the face has a focal point instead of
    # vanishing into the patches.
    nose = [(HCX - 2, HCY + 5), (HCX + 2, HCY + 5), (HCX, HCY + 8)]
    pygame.draw.polygon(surf, PANDA_BLACK, nose)
    pygame.draw.line(surf, PANDA_BLACK, (HCX, HCY + 8), (HCX - 3, HCY + 11), 1)
    pygame.draw.line(surf, PANDA_BLACK, (HCX, HCY + 8), (HCX + 3, HCY + 11), 1)

    # ── near arm on the body's LEFT flank (the flapping panda arm) ──
    # Pivoted on the left shoulder so flapping swings the paw up/down beside the
    # belly; it frames the white bean from the side and never crosses it.
    _rot_blit(surf, _panda_arm(wing_angle_deg), (BCX - 18, BCY + 1))

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
