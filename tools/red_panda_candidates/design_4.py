"""Red panda — DESIGN 4: MAPLE SPRITE (R1).

Hyper-cute chibi gremlin: a giant round head (~75% of the mass) crowned by
two oversized pointed ears, perched on a tiny russet ball of a body with a
short, perky ringed tail. The read at 40px is deliberately top-heavy — "big
round face + huge ears + tiny body" — so it pops as a toy/mascot silhouette
rather than a naturalistic critter.

Self-contained scratch builder (NOT registered in any BUILDERS dict; never
imports game.animal_red_panda). Tail -> body -> head order so the head dome
overlaps the body top with no visible neck seam.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse

# Canvas / anchors. Chibi proportions push the head HIGH and big; the body is
# a small ball tucked beneath it.
COMPOSITE_W = 64
COMPOSITE_H = 84
DY          = 12
HCX, HCY    = 44, 30        # head centre — large + high
HEAD_R      = 17
BCX, BCY    = 34, 50        # tiny body ball centre

# Palette (per brief).
BODY      = (207, 98, 52)    # #CF6234 base fur
SHADOW    = (132, 55, 28)    # #84371C deepest shade
HIGH      = (251, 168, 92)   # #FBA85C forehead / warm gloss
CREAM     = (251, 239, 216)  # #FBEFD8 eye-surround, cheeks, tail rings
ACCENT    = (46, 31, 23)     # #2E1F17 nose, paw dots, dark detail
EAR_INNER = (240, 200, 160)  # #F0C8A0 ear inner fill
EYEDK     = (28, 18, 14)     # iris
CREAM_AO  = (214, 196, 168)  # cream in shade (AO ring under eye-surround)
RUST_TR   = (150, 60, 30)    # rust tear-track


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
    """0 = down-pose (high flap), 1 = up-pose (low flap). Drives the perky
    tail flick and a tiny springy-toy bounce of the body."""
    return (40 - angle_deg) / 90.0


def _chibi_eye(surf, cx, cy, r):
    """The hero element: oversized glossy chibi eye on a big cream surround
    with an AO ring under it and a bold rust tear-track below the inner edge."""
    # AO ring beneath, then the big clean cream surround.
    pygame.draw.circle(surf, CREAM_AO, (cx, cy + 2), r + 3)
    pygame.draw.circle(surf, CREAM,    (cx, cy),     r + 3)
    # Bold rust tear-track dropping from the inner corner.
    pygame.draw.line(surf, RUST_TR, (cx, cy + r), (cx, cy + r + 6), 2)
    # White sclera, dark iris, big glossy catch-light.
    pygame.draw.circle(surf, (252, 248, 240), (cx, cy), r + 1)
    pygame.draw.circle(surf, EYEDK, (cx + 1, cy), r)
    pygame.draw.circle(surf, (255, 255, 255), (cx - r // 2, cy - r // 2),
                       max(2, r // 2))
    # Tiny lower secondary glint sells the glass-bead toy eye.
    pygame.draw.circle(surf, (255, 255, 255), (cx + 1, cy + 1), 1)


def _ear(surf, tip_x, tip_y, sgn):
    """Large pointed ear spiking up from the crown; cream inner with a soft
    highlight. sgn = -1 left, +1 right."""
    base_l = (tip_x - 6, tip_y + 12)
    base_r = (tip_x + 6, tip_y + 12)
    tip    = (tip_x + sgn * 1, tip_y)
    pygame.draw.polygon(surf, SHADOW, [base_l, base_r, tip])
    pygame.draw.polygon(surf, BODY,
                        [(base_l[0] + 1, base_l[1] - 1),
                         (base_r[0] - 1, base_r[1] - 1),
                         (tip[0], tip[1] + 2)])
    pygame.draw.polygon(surf, EAR_INNER,
                        [(base_l[0] + 2, base_l[1] - 2),
                         (base_r[0] - 2, base_r[1] - 2),
                         (tip[0], tip[1] + 4)])
    # Ear inner highlight on the cream portion (toward the outer flank).
    pygame.draw.line(surf, (250, 224, 196),
                     (tip[0] + sgn * 2, tip[1] + 6),
                     (tip[0] + sgn * 3, tip[1] + 10), 1)


def _tail(surf, f):
    """Short, stubby, perky tail pointing up-left (~150 deg) off the body as a
    stack of chunky ring-hoops: wide CREAM banded with a dark separator and
    russet. Flicks a touch higher on the up-pose."""
    flick = (f - 0.5) * 4            # up-pose lifts the tip
    # March up-left from the body in a short straight stub.
    ang = math.radians(150)
    dx, dy = math.cos(ang), math.sin(ang)
    root = (BCX - 5, BCY - 1)
    seg  = 4.5
    hoops = 4
    centres = []
    for i in range(hoops):
        d = 2 + i * seg
        cx = int(root[0] + dx * d)
        cy = int(root[1] + dy * d - flick * (i / max(1, hoops - 1)))
        centres.append((cx, cy))

    # Russet undercoat / outline pass so hoops read as one connected stub.
    for cx, cy in centres:
        pygame.draw.circle(surf, SHADOW, (cx, cy), 6)
    for cx, cy in centres:
        pygame.draw.circle(surf, BODY, (cx, cy), 5)

    # Alternating cream hoops with dark separators between them.
    for i, (cx, cy) in enumerate(centres):
        if i % 2 == 1:
            pygame.draw.circle(surf, CREAM_AO, (cx, cy + 1), 5)
            pygame.draw.circle(surf, CREAM,    (cx, cy),     4)
        # Dark separator line on the outer edge toward the next hoop.
        if i < hoops - 1:
            nx, ny = centres[i + 1]
            mx, my = (cx + nx) // 2, (cy + ny) // 2
            pygame.draw.circle(surf, ACCENT, (mx, my), 1)

    # Bright cream tip caps the stub.
    tx, ty = centres[-1]
    pygame.draw.circle(surf, (252, 244, 232), (tx, ty - 1), 3)


def _body(surf, f):
    """Tiny russet ball of a body with a small cream belly and dark paw-dots
    below. A subtle vertical bob gives the springy-toy energy."""
    bob = int((1 - f) * 2)          # high flap squashes down a hair
    bcx, bcy = BCX, BCY + bob
    _aaellipse(surf, SHADOW, (bcx + 1, bcy + 1), 9, 9)
    _aaellipse(surf, BODY,   (bcx,     bcy),     8, 8)
    _aaellipse(surf, HIGH,   (bcx - 3, bcy - 3), 3, 2)   # tiny lit shoulder
    # Small cream belly tuft.
    _aaellipse(surf, CREAM_AO, (bcx + 1, bcy + 2), 4, 4)
    _aaellipse(surf, CREAM,    (bcx + 1, bcy + 3), 3, 3)
    # Dark stubby paw-dots tucked below.
    drop = int(5 - f * 2)
    for fx in (bcx - 4, bcx + 4):
        pygame.draw.circle(surf, ACCENT, (fx, bcy + 7 + drop), 3)
        pygame.draw.circle(surf, (60, 38, 26), (fx - 1, bcy + 6 + drop), 1)


def _head(surf, f):
    """Giant round head dominating the figure: shadow + base dome, ears spiking
    from the crown, big cheek patches, the hero chibi eyes, a glossy dome sheen
    and a small nose/mouth."""
    hcx, hcy = HCX, HCY
    # Head dome — shadow, base, warm forehead.
    _aaellipse(surf, SHADOW, (hcx + 1, hcy + 1), HEAD_R, HEAD_R - 1)
    _aaellipse(surf, BODY,   (hcx,     hcy),     HEAD_R - 1, HEAD_R - 2)
    _aaellipse(surf, HIGH,   (hcx - 5, hcy - 8),  6, 4)   # warm forehead

    # Big pointed ears spiking from the crown.
    _ear(surf, hcx - 9, hcy - HEAD_R + 2, -1)
    _ear(surf, hcx + 9, hcy - HEAD_R + 2, +1)

    # Bold cream cheek patches flanking the muzzle.
    _aaellipse(surf, CREAM_AO, (hcx - 9, hcy + 7), 5, 4)
    _aaellipse(surf, CREAM,    (hcx - 9, hcy + 6), 5, 4)
    _aaellipse(surf, CREAM_AO, (hcx + 11, hcy + 7), 5, 4)
    _aaellipse(surf, CREAM,    (hcx + 11, hcy + 6), 5, 4)

    # Hero chibi eyes — big, wide-set, forward-facing.
    _chibi_eye(surf, hcx - 6, hcy, 4)
    _chibi_eye(surf, hcx + 8, hcy, 4)

    # Small nose + tiny smile between the eyes.
    pygame.draw.circle(surf, ACCENT, (hcx + 1, hcy + 9), 2)
    pygame.draw.line(surf, ACCENT, (hcx + 1, hcy + 11), (hcx + 1, hcy + 13), 1)
    pygame.draw.line(surf, ACCENT, (hcx - 2, hcy + 13), (hcx + 1, hcy + 13), 1)
    pygame.draw.line(surf, ACCENT, (hcx + 1, hcy + 13), (hcx + 4, hcy + 13), 1)

    # Glossy head-dome sheen, offset top-left for a toy/plastic shine.
    sheen = pygame.Surface((20, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 255, 255, 140), sheen.get_rect())
    surf.blit(sheen, (hcx - 13, hcy - 13))


def build_maple_sprite(wing_angle_deg):
    """Compose one frame. Tail -> body -> head so the giant head dome overlaps
    the tiny body top (no visible neck) and reads cleanly on front."""
    surf = _new()
    f = _flap(wing_angle_deg)
    _tail(surf, f)
    _body(surf, f)
    _head(surf, f)
    return surf


build = _make_prebuilt_skin(build_maple_sprite)
