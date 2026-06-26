"""CHUBBY DUMPLING — round baby-panda candidate (scratch exploration).

The cuteness pick: defined by SHAPE, not a prop. Where Classic is a panda
standing up, this is a panda drawn as a single ball — a giant round head
melting into an almost-as-big belly with hardly any neck, so the silhouette
is one fat circle even at 40px. Baby proportions drive every choice: ears and
eye patches are pushed oversized (bigger reads younger), features sit LOW and
WIDE on the face, the cheeks are a brighter pink, and the limbs shrink to tiny
stub paddles so nothing pokes out to break the round read. Drawn fully from
scratch (no macaw base underneath) so the body itself can be the round mass —
re-skinning the existing winged bird would leave wing/tail spurs that fight
the dumpling silhouette. Exploration only; not registered in store_skins.
"""
import math
import pygame

from game import parrot
from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse

# Larger-than-base canvas: the oversized head + ears need headroom above the
# crown and the belly needs room below, so the rotozoom in the getter never
# clips the round silhouette.
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12

# Two near-equal stacked circles. The head is intentionally the dominant disc
# and the belly only slightly smaller + lower, so head-into-body reads as one
# continuous ball with no waist — the baby-dumpling tell.
BCX, BCY = 32, 32 + DY            # body / belly centre  (32, 44)
HCX, HCY = 44, 22 + DY           # head centre, set forward+up  (44, 34)

# Palette (brief). Bright white so the ball pops on day sky; soft highlight
# greys keep the black ears/limbs from going to flat holes; baby-pink cheeks
# are pushed brighter than Classic for the "aww".
BLACK   = (26, 26, 26)           # #1A1A1A
BLACK_H = (74, 74, 82)           # #4A4A52 soft ear/arm highlight
WHITE   = (248, 248, 248)        # #F8F8F8 extra-bright white
WHITE_S = (234, 234, 236)        # #EAEAEC white shadow / lower-belly value step
PINK    = (255, 157, 176)        # #FF9DB0 bright baby cheeks
PINK_D  = (236, 126, 150)        # cheek core so the blush has a soft centre
NOSE    = (30, 28, 30)
GLINT   = (255, 255, 255)


def _ball(surf, color, cx, cy, r):
    _aaellipse(surf, color, (cx, cy), r, r)


def _build_frame(wing_angle_deg):
    """One 64x84 SRCALPHA frame of the round baby panda.

    `wing_angle_deg` (one of _WING_ANGLES) drives the tiny stub-arm paddle so
    the flap still animates, but the arms are kept short + rounded so they read
    as excited little paddles rather than full wings poking out of the ball.
    """
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)

    # Map the four wing angles to a small paddle lift. Up-flap = paddles raised
    # and spread; down-flap = tucked low. Kept subtle so the silhouette stays a
    # ball — only the very tips peek past the belly edge.
    lift = wing_angle_deg / 50.0    # ~ +1 (up) .. -0.8 (down)

    # ── Belly: the lower ball. Nearly as big as the head and overlapping it so
    # there is no neck. A slightly darker lower arc gives the round mass form
    # (light from above) without a hard seam.
    belly_r = 19
    _ball(surf, WHITE_S, BCX, BCY + 1, belly_r)
    _ball(surf, WHITE, BCX, BCY - 1, belly_r - 1)
    # Soft lower value step so the bottom of the ball doesn't blow out flat.
    bot = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _aaellipse(bot, WHITE_S, (BCX, BCY + 6), belly_r - 3, belly_r - 6)
    surf.blit(bot, (0, 0))

    # ── Tiny black foot pads peeking out at the very bottom of the ball.
    for fx in (BCX - 7, BCX + 7):
        _aaellipse(surf, BLACK, (fx, BCY + belly_r - 4), 4, 3)
        _aaellipse(surf, BLACK_H, (fx, BCY + belly_r - 5), 2, 1)

    # ── Tiny stub arms (drawn BEFORE the head/belly fronts so only their rounded
    # tips peek out past the ball edge — short excited paddles, never wings).
    for side in (-1, 1):
        ax = BCX + side * (belly_r - 2)
        ay = BCY + 2 - int(lift * 4) * (1 if side else 1)
        # Each arm is a tiny rounded black blob just outside the white ball.
        _aaellipse(surf, BLACK, (ax, ay), 5, 6)
        _aaellipse(surf, BLACK_H, (ax - side, ay - 2), 2, 3)

    # Re-stamp the belly front over the arm roots so the arms read as stubs
    # attached to the ball, not free-floating mitts.
    _ball(surf, WHITE, BCX, BCY - 1, belly_r - 2)
    bot2 = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _aaellipse(bot2, WHITE_S, (BCX, BCY + 7), belly_r - 5, belly_r - 8)
    surf.blit(bot2, (0, 0))

    # ── Oversized round black ears on the crown, drawn before the white face so
    # the face disc tucks over their lower edge (ears sit ON the head, not above
    # a gap). Bigger than Classic = younger read; pushed up past the crown so the
    # silhouette breaks at the top.
    ear_r = 8
    head_r = 20
    for side in (-1, 1):
        ex = HCX + side * 12
        ey = HCY - head_r + 5
        _ball(surf, BLACK, ex, ey, ear_r)
        # Inner ear + a soft grey highlight so the black isn't a flat hole.
        _ball(surf, BLACK_H, ex - side, ey - 2, ear_r - 4)
        _ball(surf, BLACK, ex - side, ey - 1, ear_r - 6)

    # ── Extra-large round white face. Its lower edge overlaps the belly so head
    # and body fuse into one ball.
    _ball(surf, WHITE_S, HCX, HCY + 1, head_r)
    _ball(surf, WHITE, HCX, HCY - 1, head_r - 1)
    # Tiny crown tuft / cowlick between the ears (one charm object).
    tuft = [(HCX - 2, HCY - head_r + 3), (HCX, HCY - head_r - 4),
            (HCX + 2, HCY - head_r + 3)]
    pygame.draw.polygon(surf, BLACK, tuft)
    pygame.draw.line(surf, BLACK_H, (HCX, HCY - head_r - 3),
                     (HCX, HCY - head_r + 2), 1)

    # ── Huge round black eye patches — more circular than teardrop, set LOW and
    # WIDE (baby spacing). They take up most of the face. Each holds a big white
    # sparkle glint so the eyes read awake + sweet, not sleepy.
    for side in (-1, 1):
        px = HCX + side * 8
        py = HCY + 3
        # Patch: a fat near-circle, slightly taller than wide.
        _aaellipse(surf, BLACK, (px, py), 7, 8)
        # Eye white inside the patch, low and inward.
        eye_x = px - side * 1
        eye_y = py + 1
        _ball(surf, WHITE, eye_x, eye_y, 3)
        # Dark pupil + a big bright sparkle for the baby-eye catchlight.
        _ball(surf, BLACK, eye_x, eye_y + 1, 2)
        _ball(surf, GLINT, eye_x - 1, eye_y - 1, 1)
        _aaellipse(surf, GLINT, (eye_x + 1, eye_y + 2), 1, 1)

    # ── Rosy round cheek blushes — larger + brighter than Classic, set low under
    # the eye patches and out wide.
    for side in (-1, 1):
        cx = HCX + side * 13
        cy = HCY + 10
        _aaellipse(surf, PINK, (cx, cy), 4, 3)
        _aaellipse(surf, PINK_D, (cx, cy), 2, 1)

    # ── Tiny black nose + tiny mouth, set LOW for exaggerated baby spacing.
    nose_x, nose_y = HCX, HCY + 9
    _aaellipse(surf, NOSE, (nose_x, nose_y), 2, 1)
    _aaellipse(surf, BLACK_H, (nose_x, nose_y - 1), 1, 1)
    # Little mouth: two short curves under the nose (a soft w / smile).
    pygame.draw.line(surf, NOSE, (nose_x, nose_y + 1), (nose_x, nose_y + 3), 1)
    pygame.draw.arc(surf, NOSE, (nose_x - 4, nose_y + 1, 4, 4),
                    math.radians(200), math.radians(340), 1)
    pygame.draw.arc(surf, NOSE, (nose_x, nose_y + 1, 4, 4),
                    math.radians(200), math.radians(340), 1)

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


def build(wing_angle_deg) -> pygame.Surface:
    """Draw one 64x84 SRCALPHA frame of the Chubby Dumpling baby panda."""
    return _build_frame(wing_angle_deg)


get_skin = _make_prebuilt_skin(build)
