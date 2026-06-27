"""PANDA Store skin.

Giant panda flapping with a diagonal bamboo cane held in both paws, warm-brown
eye patches, rosy cheeks, crown leaf sprig. The high-contrast black/white block
plus the single unbroken bamboo-green stalk are the two reads engineered to
survive 40px in motion; the softer dumpling face (round warm-brown patches,
sparkling glint-lit eyes, blush, smile-mouth) keeps it friendly, not a hollow
mask.

Contract mirrors game/animal_skins.py:

  * `build_red_panda(wing_angle_deg) -> pygame.Surface`  one flat 64x84 frame.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)` — 4 flat frames + per-(frame, 3deg) rotation
    cache, each run through `parrot._add_outline` (the house 1-px dark keyline
    that keeps the edge alive on near-white day skies).
  * `BUILDERS = {"skin_red_panda": get_red_panda}` — liftable label->getter.

Collision is a fixed 14px circle at the BODY centre, so the body mass stays
anchored at BCX/BCY (32,44) — the bamboo cane is silhouette flourish, never
collision mass. The tall canvas gives ear/leaf headroom while the body keeps
the base anchor so the in-game centre-blit rotation maths still holds.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W = SPRITE_W   # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY   # body centre (32, 44)
HCX, HCY = 44, 22 + DY   # head centre (44, 34)
CROWN_Y  = 12 + DY        # 24 — ears push up to here

# Panda palette — high-contrast black/white block + the bamboo green signature.
BLACK   = (26, 26, 26)     # #1A1A1A panda black
BLACK_HI = (58, 58, 64)    # soft highlight on ears / arm tops for roundness
WHITE   = (245, 245, 245)  # #F5F5F5 panda white
WHITE_SH = (224, 224, 228) # white value-step shadow
GREEN   = (95, 166, 58)    # #5FA63A bamboo green
GREEN_SH = (60, 122, 34)   # #3C7A22 bamboo shadow / node rings
LEAF_HI = (201, 226, 154)  # #C9E29A leaf highlight
CHEEK   = (231, 169, 169)  # warm cheek/nose-tip charm
NOSE    = (24, 24, 24)
EYE_GLINT = (255, 255, 255)

# Warm patch + bright blush so the face reads soft, not a hollow mask, even
# after the 40px downscale.
PATCH    = (42, 26, 10)      # warm dark-brown eye patch
PATCH_H  = (66, 44, 22)      # soft brown rim
PINK     = (255, 143, 160)   # rosy cheek blush
PINK_D   = (240, 110, 134)   # cheek centre
GLINT    = (255, 255, 255)   # bright catch-light


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter — lazy 4-frame build +
    per-(frame, 3deg) rotation cache, each frame house-outlined."""
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


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(angle_deg):
    """0 -> down-pose (arms low), 1 -> up-pose (arms raised). Drives both the
    arm lift and the leaf-sprig sway so the whole rig animates as one."""
    return (angle_deg + 40) / 90.0


def _leaf(surf, base, tip, width, col, hi=None):
    """A single bamboo leaf as a slim pointed lens between base and tip, with
    an optional bright centre vein-highlight."""
    bx, by = base
    tx, ty = tip
    dx, dy = tx - bx, ty - by
    length = math.hypot(dx, dy) or 1.0
    # Perpendicular unit vector swells the leaf belly at its midpoint.
    px, py = -dy / length, dx / length
    mx, my = bx + dx * 0.45, by + dy * 0.45
    pts = [
        (bx, by),
        (mx + px * width, my + py * width),
        (tx, ty),
        (mx - px * width, my - py * width),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])
    if hi is not None:
        pygame.draw.line(surf, hi, (int(bx), int(by)), (int(tx), int(ty)), 1)


def _bamboo_node(surf, cx, cy, half_w, ang):
    """A darker ring band crossing the stalk at (cx, cy), perpendicular to the
    stalk axis `ang` (radians) — the segment join that makes it read as bamboo,
    not a plain green bar."""
    nx, ny = math.cos(ang + math.pi / 2), math.sin(ang + math.pi / 2)
    a = (cx + nx * half_w, cy + ny * half_w)
    b = (cx - nx * half_w, cy - ny * half_w)
    pygame.draw.line(surf, GREEN_SH, a, b, 3)


def build_red_panda(wing_angle_deg):
    """Draw one 64x84 frame of the bamboo panda with a chubby face."""
    surf = _new()
    f = _flap(wing_angle_deg)
    lift = (1.0 - f) * 6.0   # down-pose drops the arms; up-pose lifts them

    # Crown leaf sprig poking up between the ears, drawn first so it sits behind
    # the head and reads as tucked into the cane. ONE small fan only — the only
    # green near the crown, so it never competes with an inner-ear colour. Sways
    # opposite the arm lift so it animates.
    sway = (f - 0.5) * 3.0
    sprig_root = (HCX - 1, CROWN_Y + 1)
    for j in range(3):
        ang = math.radians(-90 + (j - 1) * 24 + sway)
        ln = 12 - abs(j - 1) * 2
        tipx = sprig_root[0] + math.cos(ang) * ln
        tipy = sprig_root[1] + math.sin(ang) * ln
        _leaf(surf, sprig_root, (tipx, tipy), 2.8,
              GREEN if j == 1 else GREEN_SH, hi=LEAF_HI)

    # Body: white belly block + black shoulder yoke. Soft drop shadow first for
    # a touch of grounding.
    _aaellipse(surf, (0, 0, 0, 50), (BCX + 1, BCY + 2), 18, 15)
    # Black shoulder yoke (the real panda's dark band across the upper back)
    # ties the two arm masses together so the block reads black-over-white.
    _aaellipse(surf, BLACK, (BCX, BCY - 6), 18, 9)
    _aaellipse(surf, BLACK_HI, (BCX, BCY - 8), 13, 4)
    # White torso/belly disc over the collision centre.
    _aaellipse(surf, WHITE_SH, (BCX, BCY + 3), 16, 13)
    _aaellipse(surf, WHITE, (BCX - 1, BCY + 1), 15, 12)
    _aaellipse(surf, (255, 255, 255), (BCX - 4, BCY - 2), 7, 5)  # belly sheen

    # Black leg stubs under the body.
    for legx in (BCX - 8, BCX + 7):
        _aaellipse(surf, BLACK, (legx, BCY + 13), 5, 5)
        _aaellipse(surf, BLACK_HI, (legx - 1, BCY + 11), 2, 2)

    # ONE unbroken diagonal bamboo cane drawn ON TOP of the whole body block,
    # from the upper-RIGHT (chewing end, by the mouth) down to the lower-LEFT
    # hip. It is one thick capped line so there is NO break or value-shift along
    # its length, and because it is the LAST body layer it crosses the white
    # belly unbroken instead of disappearing behind it. ONE mid-green end to
    # end; the only darker green is the node rings. The arm lift rocks the cane
    # so it animates with the flap. Half-width 4 -> reads as ~2px at 40px.
    rock = (f - 0.5) * 4.0
    top = (BCX + 18, BCY - 16 - lift + rock)     # chewing end, up by the mouth
    bot = (BCX - 17, BCY + 18 + lift * 0.3 + rock)  # butt end, past the hip
    ang = math.atan2(bot[1] - top[1], bot[0] - top[0])
    half = 4
    nx, ny = math.cos(ang + math.pi / 2), math.sin(ang + math.pi / 2)
    # Dark base line gives the cane a one-sided shadow edge without breaking it.
    pygame.draw.line(surf, GREEN_SH, top, bot, half * 2)
    # Single mid-green core inset over the shadow — one colour end to end.
    core_top = (top[0] - nx * 1.0, top[1] - ny * 1.0)
    core_bot = (bot[0] - nx * 1.0, bot[1] - ny * 1.0)
    pygame.draw.line(surf, GREEN, core_top, core_bot, half * 2 - 2)
    # Specular sheen line on the lit edge, continuous along the whole cane.
    pygame.draw.line(surf, LEAF_HI,
                     (top[0] + nx * (half - 1), top[1] + ny * (half - 1)),
                     (bot[0] + nx * (half - 1), bot[1] + ny * (half - 1)), 1)
    # Darker node rings only — the segment joins that make it read as bamboo
    # without ever interrupting the continuous green line.
    for t in (0.2, 0.42, 0.64, 0.86):
        ncx = top[0] + (bot[0] - top[0]) * t
        ncy = top[1] + (bot[1] - top[1]) * t
        _bamboo_node(surf, ncx, ncy, half, ang)

    # Two black paw grips anchoring the cane to the panda's hands — compact paw
    # masses that OVERLAP the cane edge rather than straddling it, so the
    # continuous green line stays visible between them: one near the chewing/
    # mouth end, one near the hip end.
    for gt in (0.34, 0.78):
        gcx = top[0] + (bot[0] - top[0]) * gt
        gcy = top[1] + (bot[1] - top[1]) * gt
        # Offset the paw to the lower-left side of the cane so its inner edge
        # just laps onto the green, leaving the cane's lit side fully exposed.
        pcx, pcy = gcx - nx * 3.0, gcy - ny * 3.0
        _aaellipse(surf, BLACK, (pcx, pcy), 5, 5)
        _aaellipse(surf, BLACK_HI, (pcx - 1, pcy - 2), 2, 1)

    # ── HEAD ──
    # Round black ears on the crown.
    for ex in (HCX - 9, HCX + 9):
        _aaellipse(surf, BLACK, (ex, CROWN_Y + 3), 6, 6)
        _aaellipse(surf, BLACK_HI, (ex - 1, CROWN_Y + 1), 2, 2)

    # Round white face disc.
    _aaellipse(surf, WHITE_SH, (HCX, HCY + 1), 13, 12)
    _aaellipse(surf, WHITE, (HCX - 1, HCY), 12, 11)

    # Round warm-brown eye patches with sparkling glint-lit eyes.
    for side in (-1, 1):
        px = HCX + side * 6
        py = HCY + 2
        _aaellipse(surf, PATCH_H, (px, py), 5, 6)   # warm rim
        _aaellipse(surf, PATCH,   (px, py), 4, 5)   # patch body
        eye_x = px - side            # slightly toward nose
        eye_y = py + 1
        pygame.draw.circle(surf, WHITE,  (eye_x, eye_y), 2)
        pygame.draw.circle(surf, PATCH,  (eye_x, eye_y + 1), 1)  # dark pupil
        # Big catch-light upper-inner (toward nose) — makes eyes sparkle.
        gx = eye_x - side
        gy = eye_y - 1
        pygame.draw.circle(surf, GLINT, (gx, gy), 2)

    # Rosy cheek blushes.
    for side in (-1, 1):
        cx = HCX + side * 9
        cy = HCY + 7
        _aaellipse(surf, PINK,   (cx, cy), 3, 3)
        _aaellipse(surf, PINK_D, (cx, cy), 2, 1)

    # Ellipse nose.
    nx0, ny0 = HCX, HCY + 6
    _aaellipse(surf, NOSE, (nx0, ny0), 2, 1)
    _aaellipse(surf, BLACK_HI, (nx0, ny0 - 1), 1, 1)   # soft highlight

    # Soft w / smile mouth under the nose.
    pygame.draw.line(surf, NOSE, (nx0, ny0 + 1), (nx0, ny0 + 3), 1)
    pygame.draw.arc(surf, NOSE, (nx0 - 4, ny0 + 1, 4, 4),
                    math.radians(200), math.radians(340), 1)
    pygame.draw.arc(surf, NOSE, (nx0, ny0 + 1, 4, 4),
                    math.radians(200), math.radians(340), 1)

    return surf


# ── getter + label->getter registry (mirrors animal_skins.BUILDERS) ──────────
get_red_panda = _make_prebuilt_skin(build_red_panda)

BUILDERS = {"skin_red_panda": get_red_panda}
