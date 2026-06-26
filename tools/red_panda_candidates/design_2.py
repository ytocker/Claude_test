"""Red panda from-scratch redesign — DESIGN 2: DUSK BANDIT.

Sly low-slung night-prowler. The read is built around the most distinct
SILHOUETTE of the five: a long horizontal stretched-loaf body with the tail
held straight out behind like a banded rudder, so the shape alone says
"cat-burglar" even at gameplay scale. The tail is the hero — six hard,
crisp cream/russet blocks with dark separator seams, raccoon-style, so the
banding stays legible where soft cross-bands would mush together.

Palette runs slightly cooler/desaturated than the warm-day pandas and the
top-back carries a moonlit blue-grey rim so the figure reads as lit by night
rather than sun.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W = SPRITE_W   # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY   # body centre (32, 44)
HCX, HCY = 44, 22 + DY   # head centre (44, 34)
CROWN_Y  = 12 + DY        # 24

# Cooler / slightly desaturated dusk palette.
BODY   = (168, 73, 43)    # #A8492B
SHADOW = (90, 38, 20)     # #5A2614
HILITE = (217, 140, 90)   # #D98C5A
CREAM  = (234, 216, 188)  # #EAD8BC
CREAM_D = (196, 178, 152)  # AO'd cream for under-side band shading
ACCENT = (36, 26, 34)     # #241A22  — mask / ears / limbs
RIM    = (138, 170, 184)  # #8AAAB8  — moonlit back rim-light
EYEWHT = (236, 230, 222)


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
    """0 = down-pose, 1 = up-pose; drives the slight tail sway + creep legs."""
    return (angle_deg + 40) / 90.0


def _banded_tail(surf, f):
    """Horizontal rudder behind the rump: 6 hard alternating cream/russet
    blocks with thin dark seams. Sways ±2px at the tip with flap angle."""
    # Root sits at the rump (left) and runs right behind the body. The tip
    # tilts a touch with the flap (sway) and droops slightly at the very end.
    sway = int(round((f - 0.5) * 4))   # ±2px tip tilt across the flap arc
    x0, x1 = 11, 53
    y_root = BCY + 2
    y_tip  = y_root + 3 + sway          # slight droop + flap sway at the tip
    half_w = 5                          # ~9-10px tail thickness

    n = 6
    seg = (x1 - x0) / n

    def band_y(x):
        t = (x - x0) / (x1 - x0)
        return y_root + (y_tip - y_root) * t

    # Soft AO drop-shadow beneath the whole tail so it reads as raised.
    for i in range(n):
        cx = int(x0 + seg * (i + 0.5))
        cy = int(band_y(cx)) + 3
        pygame.draw.circle(surf, SHADOW, (cx, cy), half_w)

    # Bands as clean crisp blocks: alternate cream / russet, with the first
    # block (root) tucked under the body so the body roots into the tail.
    for i in range(n):
        bx0 = x0 + seg * i
        bx1 = x0 + seg * (i + 1)
        is_cream = (i % 2 == 1)
        fill = CREAM if is_cream else BODY
        shade = CREAM_D if is_cream else SHADOW
        # Build the block from overlapping circles between its two seams so
        # the band has true thickness rather than a 1px line.
        step = 1
        x = int(bx0)
        while x <= int(bx1):
            cy = int(band_y(x))
            pygame.draw.circle(surf, shade, (x, cy + 1), half_w)
            pygame.draw.circle(surf, fill,  (x, cy), half_w - 1)
            x += step
        # Crisp value step on the lower edge of the block.
        for x in range(int(bx0), int(bx1) + 1):
            cy = int(band_y(x))
            surf.set_at((x, cy + half_w - 1), shade)

    # Thin dark separator seams between every band — the raccoon "hard step".
    for i in range(1, n):
        sx = int(x0 + seg * i)
        cy = int(band_y(sx))
        pygame.draw.line(surf, ACCENT, (sx, cy - half_w + 1),
                         (sx, cy + half_w), 1)

    # Dark terminal tip + a sliver of moonlit rim on the tail's top edge.
    tx = x1
    ty = int(band_y(tx))
    pygame.draw.circle(surf, ACCENT, (tx, ty), half_w - 1)
    for x in range(x0 + 3, x1 - 2, 2):
        surf.set_at((x, int(band_y(x)) - half_w + 1), RIM)


def _creep_legs(surf, f):
    """Low-creep pose: dark limbs extend slightly DOWN from the belly rather
    than tucking, so the bandit looks like it is prowling."""
    drop = int(7 - f * 3)              # legs reach further on the down-beat
    for fx in (24, 40):
        pygame.draw.line(surf, ACCENT, (fx, BCY + 9), (fx, BCY + 9 + drop), 4)
        pygame.draw.circle(surf, ACCENT, (fx, BCY + 9 + drop), 3)
        # Tiny cream toe glint so the paws don't read as black blobs.
        pygame.draw.circle(surf, CREAM_D, (fx + 1, BCY + 9 + drop), 1)


def build_dusk_bandit(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)

    # Tail first so the body roots over and overlaps its base block.
    _banded_tail(surf, f)

    # Legs sit under the belly, drawn before the body so the belly overlaps
    # the leg tops and they read as emerging from beneath.
    _creep_legs(surf, f)

    # --- Elongated loaf body: wider than tall, belly-heavy, 3-layer shading.
    bcx, bcy = BCX + 2, BCY + 4
    # Strong AO shadow under the belly.
    _aaellipse(surf, SHADOW, (bcx, bcy + 4), 17, 9)
    # Base body.
    _aaellipse(surf, BODY,   (bcx, bcy), 17, 11)
    # Belly-heavy mid shadow on the lower flank.
    _aaellipse(surf, SHADOW, (bcx + 1, bcy + 5), 13, 6)
    # Cream belly patch riding low and forward.
    _aaellipse(surf, CREAM_D, (bcx + 5, bcy + 5), 8, 5)
    _aaellipse(surf, CREAM,   (bcx + 5, bcy + 4), 7, 4)
    # Top-side body highlight.
    _aaellipse(surf, HILITE, (bcx - 3, bcy - 5), 7, 3)
    # Moonlit blue-grey rim along the top-back edge of the body.
    for i in range(13):
        a = math.radians(196 + i * 9)
        px = int(bcx + math.cos(a) * 16)
        py = int(bcy + math.sin(a) * 10)
        surf.set_at((px, py), RIM)
        surf.set_at((px, py - 1), RIM)

    # --- Smaller sneaky head (~50% of body), forward-angled low tilt.
    hcx, hcy = HCX + 1, HCY + 1
    _aaellipse(surf, SHADOW, (hcx + 1, hcy + 2), 10, 9)
    _aaellipse(surf, BODY,   (hcx, hcy), 10, 9)
    # Forward muzzle wedge — pushes the face down-and-forward (sneaky tilt).
    _aaellipse(surf, BODY,   (hcx + 6, hcy + 3), 5, 4)
    _aaellipse(surf, HILITE, (hcx - 2, hcy - 4), 4, 2)

    # Rounded dark ears (more round than pointed), low on the crown.
    for ex, sgn in ((hcx - 7, -1), (hcx + 6, +1)):
        pygame.draw.circle(surf, ACCENT, (ex, CROWN_Y + 4), 5)
        pygame.draw.circle(surf, SHADOW, (ex + sgn, CROWN_Y + 5), 2)

    # --- True bandit mask: ONE dark ellipse band across both eyes FIRST,
    # then the cream cheek patches sit below/around it.
    _aaellipse(surf, ACCENT, (hcx + 1, hcy + 1), 12, 7)

    # Cream cheek patches with rust tear-tracks, outboard of the mask.
    for cx, sgn in ((hcx - 5, -1), (hcx + 7, +1)):
        _aaellipse(surf, CREAM_D, (cx, hcy + 4), 4, 5)
        _aaellipse(surf, CREAM,   (cx, hcy + 3), 3, 4)
        # Rust tear-track running down off the eye.
        pygame.draw.line(surf, SHADOW, (cx + sgn, hcy - 2),
                         (cx + sgn * 2, hcy + 6), 1)

    # Cream brow snip between the eyes (above the mask) for the panda read.
    _aaellipse(surf, CREAM, (hcx + 1, hcy - 4), 2, 2)

    # --- Sly narrowed eyes sitting on the dark mask band.
    for ex in (hcx - 3, hcx + 6):
        pygame.draw.circle(surf, EYEWHT, (ex, hcy), 3)
        pygame.draw.circle(surf, ACCENT, (ex + 1, hcy), 2)
        pygame.draw.circle(surf, (255, 255, 255), (ex - 1, hcy - 1), 1)
        # Narrowed lids — a dark lash line clipping the top of each eye.
        pygame.draw.line(surf, ACCENT, (ex - 3, hcy - 2), (ex + 3, hcy - 1), 1)

    # Nose + small smug muzzle line at the forward wedge.
    pygame.draw.circle(surf, ACCENT, (hcx + 7, hcy + 4), 2)
    pygame.draw.line(surf, ACCENT, (hcx + 7, hcy + 5), (hcx + 7, hcy + 7), 1)

    return surf


build = _make_prebuilt_skin(build_dusk_bandit)
