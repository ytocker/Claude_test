"""Panda — DESIGN 2: BAMBOO MUNCHER.

The "panda doing panda things" build: the can't-miss black-and-white panda
mask, but loaded with bamboo gear so the silhouette breaks outward with green
from several directions at once. A thick segmented bamboo stalk is clutched
diagonally corner-to-corner across the body, two leaf sprigs poke up past the
crown beside the ears, a chewed leaf hangs from the mouth, and a small woven
bundle rides on the back. Green is this concept's whole identity — it is the
only panda in the set carrying a second strong colour and a held prop, so the
stalk and leaf tufts are pushed bright and large enough to survive the 40px
in-motion read.

Self-contained full figure (body + head + arms + props) layered the way the
KFC / ghost variants in ``game/parrot.py`` are, rather than reusing the bare
macaw underneath — the black-and-white block has to own the whole silhouette
for the panda read to land.
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


def build(wing_angle_deg):
    """Draw one 64x84 frame of the Bamboo Muncher panda."""
    surf = _new()
    f = _flap(wing_angle_deg)
    lift = (1.0 - f) * 6.0   # down-pose drops the arms; up-pose lifts them

    # ---- Woven bamboo bundle on the back (drawn first, behind everything) ----
    # Sits off the upper-left back so it breaks the back outline past the body.
    bpx, bpy = BCX - 16, BCY - 10
    pygame.draw.ellipse(surf, GREEN_SH, (bpx - 7, bpy - 9, 14, 20))
    pygame.draw.ellipse(surf, GREEN, (bpx - 6, bpy - 9, 11, 18))
    # Woven cross-lashing on the bundle.
    for k in range(-1, 3):
        yy = bpy - 6 + k * 5
        pygame.draw.line(surf, GREEN_SH, (bpx - 5, yy), (bpx + 4, yy - 2), 1)
    pygame.draw.line(surf, (40, 30, 22), (bpx + 4, bpy - 11),
                     (BCX - 4, BCY - 2), 2)   # shoulder strap to the body

    # ---- Leaf sprigs poking up past the crown, beside the ears ----
    # Behind the head so they read as tucked in. Sway opposite the arm lift.
    sway = (f - 0.5) * 3.0
    for side, lx in ((-1, HCX - 9), (1, HCX + 8)):
        rootx, rooty = lx, CROWN_Y + 2
        for j in range(3):
            ang = math.radians(-90 + side * (18 + j * 16) + sway * side)
            ln = 11 - j * 2
            tipx = rootx + math.cos(ang) * ln
            tipy = rooty + math.sin(ang) * ln
            _leaf(surf, (rootx, rooty), (tipx, tipy), 2.6,
                  GREEN if j % 2 == 0 else GREEN_SH, hi=LEAF_HI)

    # ---- Body: white belly block + black shoulder yoke ----
    # Soft drop shadow first for a touch of grounding.
    _aaellipse(surf, (0, 0, 0, 50), (BCX + 1, BCY + 2), 18, 15)
    # Black shoulder yoke (the real panda's dark band across the upper back),
    # ties the two arm masses together so the block reads black-over-white.
    _aaellipse(surf, BLACK, (BCX, BCY - 6), 18, 9)
    _aaellipse(surf, BLACK_HI, (BCX, BCY - 8), 13, 4)
    # White torso/belly disc over the collision centre.
    _aaellipse(surf, WHITE_SH, (BCX, BCY + 3), 16, 13)
    _aaellipse(surf, WHITE, (BCX - 1, BCY + 1), 15, 12)
    _aaellipse(surf, (255, 255, 255), (BCX - 4, BCY - 2), 7, 5)  # belly sheen

    # ---- Black leg stubs under the body ----
    for legx in (BCX - 8, BCX + 7):
        _aaellipse(surf, BLACK, (legx, BCY + 13), 5, 5)
        _aaellipse(surf, BLACK_HI, (legx - 1, BCY + 11), 2, 2)

    # ---- Black arm masses (the flap) wrapping the stalk ----
    # Drawn before the stalk's near end so the near hand can sit over it.
    arm_top = BCY - 2 - lift
    # Upper (off-shoulder) arm reaching up-right past the shoulder.
    _aaellipse(surf, BLACK, (BCX + 11, arm_top - 2), 7, 6)
    _aaellipse(surf, BLACK_HI, (BCX + 11, arm_top - 4), 3, 2)
    # Lower (near) arm reaching down-left across the belly.
    _aaellipse(surf, BLACK, (BCX - 11, BCY + 7 + lift * 0.4), 7, 6)
    _aaellipse(surf, BLACK_HI, (BCX - 12, BCY + 5 + lift * 0.4), 3, 2)

    # ---- Thick bamboo stalk held diagonally corner-to-corner ----
    # Up-right past the shoulder down to lower-left past the hip. The arm lift
    # rocks the stalk slightly so it animates with the flap.
    rock = (f - 0.5) * 4.0
    top = (BCX + 16, BCY - 14 - lift + rock)
    bot = (BCX - 16, BCY + 16 + lift * 0.3 + rock)
    ang = math.atan2(bot[1] - top[1], bot[0] - top[0])
    half = 4
    nx, ny = math.cos(ang + math.pi / 2), math.sin(ang + math.pi / 2)
    # Stalk body as a filled quad with a darker shadow edge along one side.
    quad = [
        (top[0] + nx * half, top[1] + ny * half),
        (top[0] - nx * half, top[1] - ny * half),
        (bot[0] - nx * half, bot[1] - ny * half),
        (bot[0] + nx * half, bot[1] + ny * half),
    ]
    pygame.draw.polygon(surf, GREEN_SH, quad)
    # Lit core inset toward the highlight edge.
    quad_hi = [
        (top[0] + nx * (half - 2), top[1] + ny * (half - 2)),
        (top[0] - nx * (half - 1), top[1] - ny * (half - 1)),
        (bot[0] - nx * (half - 1), bot[1] - ny * (half - 1)),
        (bot[0] + nx * (half - 2), bot[1] + ny * (half - 2)),
    ]
    pygame.draw.polygon(surf, GREEN, quad_hi)
    pygame.draw.line(surf, LEAF_HI,
                     (top[0] + nx * (half - 1), top[1] + ny * (half - 1)),
                     (bot[0] + nx * (half - 1), bot[1] + ny * (half - 1)), 1)
    # Segment node rings along the stalk.
    for t in (0.22, 0.5, 0.78):
        ncx = top[0] + (bot[0] - top[0]) * t
        ncy = top[1] + (bot[1] - top[1]) * t
        _bamboo_node(surf, ncx, ncy, half, ang)
    # A small leaf sprig bursting off the stalk's upper node.
    sprig_base = (top[0] + (bot[0] - top[0]) * 0.22,
                  top[1] + (bot[1] - top[1]) * 0.22)
    _leaf(surf, sprig_base, (sprig_base[0] + 9, sprig_base[1] - 6), 3, GREEN,
          hi=LEAF_HI)
    _leaf(surf, sprig_base, (sprig_base[0] + 11, sprig_base[1] + 2), 3,
          GREEN_SH, hi=LEAF_HI)

    # ---- Darker "mitt" hands gripping the stalk ----
    grip_t_hi, grip_t_lo = 0.30, 0.74
    for gt, gx_off, gy_off in ((grip_t_hi, 0, -lift), (grip_t_lo, 0, lift * 0.3)):
        gcx = top[0] + (bot[0] - top[0]) * gt
        gcy = top[1] + (bot[1] - top[1]) * gt + gy_off
        _aaellipse(surf, BLACK, (gcx, gcy), 5, 5)
        _aaellipse(surf, BLACK_HI, (gcx - 1, gcy - 2), 2, 1)

    # ================= HEAD =================
    # Round black ears push up past the crown (the silhouette-breakers).
    for ex in (HCX - 9, HCX + 9):
        _aaellipse(surf, BLACK, (ex, CROWN_Y + 3), 6, 6)
        _aaellipse(surf, BLACK_HI, (ex - 1, CROWN_Y + 1), 2, 2)

    # Round white face disc.
    _aaellipse(surf, WHITE_SH, (HCX, HCY + 1), 13, 12)
    _aaellipse(surf, WHITE, (HCX - 1, HCY), 12, 11)

    # Two black teardrop eye patches, angled down-inward.
    for side, ex in ((-1, HCX - 5), (1, HCX + 6)):
        patch = pygame.Surface((14, 16), pygame.SRCALPHA)
        _aaellipse(patch, BLACK, (7, 8), 4, 6)
        patch = pygame.transform.rotate(patch, side * 24)
        pr = patch.get_rect(center=(ex, HCY - 1))
        surf.blit(patch, pr.topleft)
        # White eye-glint dot keeps it friendly, not sleepy.
        pygame.draw.circle(surf, (40, 26, 30), (ex, HCY - 1), 2)
        pygame.draw.circle(surf, EYE_GLINT, (ex - 1, HCY - 2), 1)

    # Soft pink-grey cheek blushes low on the face for charm.
    _aaellipse(surf, CHEEK, (HCX - 7, HCY + 6), 3, 2)
    _aaellipse(surf, CHEEK, (HCX + 7, HCY + 6), 3, 2)

    # Little black nose triangle + soft mouth line.
    nx0, ny0 = HCX, HCY + 4
    pygame.draw.polygon(surf, NOSE, [(nx0 - 2, ny0), (nx0 + 2, ny0),
                                     (nx0, ny0 + 3)])
    pygame.draw.line(surf, NOSE, (nx0, ny0 + 3), (nx0, ny0 + 5), 1)
    pygame.draw.arc(surf, NOSE, (nx0 - 5, ny0 + 3, 5, 5),
                    math.radians(200), math.radians(350), 1)
    pygame.draw.arc(surf, NOSE, (nx0, ny0 + 3, 5, 5),
                    math.radians(190), math.radians(340), 1)

    # ---- A single chewed bamboo leaf sticking out of the mouth ----
    mouth = (nx0 + 2, ny0 + 5)
    _leaf(surf, mouth, (mouth[0] + 11, mouth[1] + 3), 3.2, GREEN, hi=LEAF_HI)
    # A ragged chewed bite-notch at the leaf root, drawn as a white gap.
    pygame.draw.line(surf, WHITE, (mouth[0] + 3, mouth[1]),
                     (mouth[0] + 4, mouth[1] + 3), 1)

    return surf


get_skin = _make_prebuilt_skin(build)
