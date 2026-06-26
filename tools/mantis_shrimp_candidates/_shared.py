"""Shared mantis-shrimp chassis for the FACE-only redesign.

The body (teal carapace + orange stripes), the segmented tail, and the hero
raptorial CLUBS all look good and stay verbatim from production
(`game/animal_mantis_shrimp`). Only the FACE — the head + eye treatment — is
being revised (the production version buries a tiny head behind the shield and
floats two jewels far up on tall stalks, so the face reads as unclear). Each
candidate supplies `face_fn(surf, hcx, hcy, rcy, s, glow)`; everything else is
identical, and the lead club still draws IN FRONT of the face.

Palette + helpers are copied verbatim so the comparison isolates the face.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse,
)

COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY          # body centre → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre → (44, 34)
CROWN_Y  = 12 + DY              # top of head → 24

# ── palette (verbatim) ───────────────────────────────────────────────────────
_CARA   = (38, 178, 168)
_CARA_D = (20, 116, 110)
_CARA_H = (138, 236, 224)
_BAND   = (255, 124, 48)
_BAND_D = (206, 82, 26)
_BAND_H = (255, 192, 120)
_MID_A  = (255, 214, 70)
_MID_B  = (90, 210, 240)
_CLUB   = (255, 112, 56)
_CLUB_H = (255, 206, 140)
_CLUB_D = (182, 60, 24)
_CLUB_TIP = (255, 232, 188)
_STALK  = (36, 18, 58)
_STALK_RIM = (12, 8, 24)
_RIM    = (16, 86, 84)
_EYE_HUE  = (118, 236, 216)
_EYE_HUE2 = (96, 150, 250)
_GLOW   = (120, 240, 220)


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


def _strike(angle_deg):
    return 1.0 - (angle_deg + 40) / 90.0


def _glow_dot(surf, cx, cy, r, col):
    g = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    for rr, a in ((r * 2, 40), (int(r * 1.4), 70), (r, 120)):
        pygame.draw.circle(g, (*col, a), (r * 2, r * 2), rr)
    surf.blit(g, (cx - r * 2, cy - r * 2), special_flags=pygame.BLEND_RGBA_ADD)


def _jewel_eye(surf, cx, cy, r, *, glow):
    """Iridescent compound eye: blue-shifted rim, teal core, the equatorial
    midband of ommatidia + a hot specular; night-only soft halo."""
    if glow:
        _glow_dot(surf, cx, cy, max(2, r - 2), _GLOW)
    pygame.draw.circle(surf, _STALK_RIM, (cx, cy), r + 1, 1)
    pygame.draw.circle(surf, _EYE_HUE2, (cx, cy), r)
    pygame.draw.circle(surf, _EYE_HUE, (cx, cy), max(1, r - 1))
    pygame.draw.line(surf, (250, 252, 250), (cx - r, cy), (cx + r, cy), 1)
    pygame.draw.circle(surf, (255, 255, 255),
                       (cx - max(1, r // 3), cy - max(1, r // 3)), max(1, r // 3))


def _club_arm(surf, shoulder, elbow, fist, *, club_col, club_hi, arm_col,
              club_r, lead, glow, glow_r=None):
    pygame.draw.line(surf, _RIM, shoulder, elbow, 5)
    pygame.draw.line(surf, arm_col, shoulder, elbow, 3)
    pygame.draw.line(surf, _RIM, elbow, fist, 5)
    pygame.draw.line(surf, arm_col, elbow, fist, 3)
    pygame.draw.circle(surf, arm_col, elbow, 2)
    pygame.draw.circle(surf, _STALK_RIM, fist, club_r + 1)
    pygame.draw.circle(surf, club_col, fist, club_r)
    pygame.draw.circle(surf, club_hi, (fist[0] - 1, fist[1] - 1), max(1, club_r - 2))
    dx, dy = fist[0] - shoulder[0], fist[1] - shoulder[1]
    mag = max(1.0, math.hypot(dx, dy))
    ux, uy = dx / mag, dy / mag
    fx, fy = int(fist[0] + ux * (club_r - 1)), int(fist[1] + uy * (club_r - 1))
    pygame.draw.line(surf, _CLUB_D,
                     (int(fist[0] + ux * club_r - uy * club_r),
                      int(fist[1] + uy * club_r + ux * club_r)),
                     (int(fist[0] + ux * club_r + uy * club_r),
                      int(fist[1] + uy * club_r - ux * club_r)), 1)
    pygame.draw.circle(surf, _CLUB_TIP, (fx, fy), 1)
    if glow and lead:
        _glow_dot(surf, fx, fy, glow_r if glow_r is not None else max(2, club_r - 3), _CLUB)


def _segmented_tail(surf, cx, cy, *, count, span):
    step = span / count
    for i in range(count):
        x = cx - int(i * step)
        rx = 8 - i
        ry = 11 - i
        pygame.draw.ellipse(surf, _CARA_D, (x - rx, cy - ry + 1, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, _CARA, (x - rx, cy - ry, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, _BAND, (x - rx, cy - ry, rx * 2, ry * 2), 1)
    tx = cx - int(span)
    for dy, dx in ((-7, -6), (0, -9), (7, -6)):
        pygame.draw.polygon(surf, _BAND, [
            (tx, cy), (tx + dx, cy + dy), (tx + dx + 3, cy + dy)])
        pygame.draw.polygon(surf, _BAND_D, [
            (tx, cy), (tx + dx, cy + dy), (tx + dx + 3, cy + dy)], 1)


def _lerp_pt(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t))


def _build(wing_angle_deg, *, glow, face_fn):
    surf = _new()
    s = _strike(wing_angle_deg)
    rcx = -int(s * 2)
    rcy = int(s * 1)
    bcx, bcy = BCX + rcx, BCY + rcy
    hcx, hcy = HCX + rcx, HCY + rcy
    sh = (bcx + 7, bcy + 3)

    far_shoulder = _lerp_pt((bcx + 2, bcy + 11), (bcx + 4, bcy + 6), s)
    far_elbow = _lerp_pt((bcx + 3, bcy + 16), (bcx + 13, bcy + 8), s)
    far_fist  = _lerp_pt((bcx + 4, bcy + 20), (bcx + 21, bcy + 10), s)
    _club_arm(surf, far_shoulder, far_elbow, far_fist,
              club_col=_CLUB_D, club_hi=_CLUB, arm_col=_CARA_D,
              club_r=6, lead=False, glow=glow)

    _segmented_tail(surf, bcx - 7, bcy + 1, count=3, span=18)

    _aaellipse(surf, _CARA_D, (bcx + 1, bcy + 1), 17, 14)
    _aaellipse(surf, _CARA, (bcx, bcy), 16, 13)
    _aaellipse(surf, _CARA_H, (bcx - 3, bcy - 4), 8, 4)

    for off in (-5, 5):
        pygame.draw.line(surf, _BAND_D, (bcx + off - 1, bcy - 11),
                         (bcx + off - 1, bcy + 11), 4)
        pygame.draw.line(surf, _BAND, (bcx + off, bcy - 11),
                         (bcx + off, bcy + 11), 3)
        pygame.draw.line(surf, _BAND_H, (bcx + off, bcy - 9),
                         (bcx + off, bcy - 3), 1)
    midx = bcx
    for k, ty in enumerate(range(bcy - 9, bcy + 10, 3)):
        pygame.draw.line(surf, (_MID_A, _MID_B)[k % 2], (midx, ty), (midx, ty + 1), 1)
    pygame.draw.ellipse(surf, _CARA_D, (bcx - 16, bcy - 13, 32, 26), 1)

    # ── FACE (head + eyes) — the only varying element ──
    face_fn(surf, hcx, hcy, rcy, s, glow)

    # ── HERO: oversized lead club, drawn IN FRONT of the face (unchanged).
    near_elbow = _lerp_pt((bcx + 13, bcy + 6), (hcx + 5, hcy + 0), s)
    near_fist  = _lerp_pt((bcx + 19, bcy + 11), (hcx + 15, hcy - 10), s)
    lead_glow_r = int(round(3 + s * 2))
    _club_arm(surf, sh, near_elbow, near_fist,
              club_col=_CLUB, club_hi=_CLUB_H, arm_col=_CARA_D,
              club_r=8, lead=True, glow=glow, glow_r=lead_glow_r)
    return surf


def make(face_fn):
    """Wrap a face_fn into a cached (frame_idx, tilt_deg) -> Surface getter
    (day/standard build — flat duotone, no body glow)."""
    return _make_prebuilt_skin(lambda a: _build(a, glow=False, face_fn=face_fn))


def head_base(surf, hcx, hcy):
    """The verbatim carapace head ellipses (most faces start from this)."""
    _aaellipse(surf, _CARA_D, (hcx, hcy + 1), 11, 10)
    _aaellipse(surf, _CARA, (hcx - 1, hcy), 10, 9)
    _aaellipse(surf, _CARA_H, (hcx - 2, hcy - 3), 4, 2)


# The PRODUCTION face (for the comparison's ORIGINAL column reference).
def face_original(surf, hcx, hcy, rcy, s, glow):
    head_base(surf, hcx, hcy)
    for sgn, ex in ((-1, hcx - 6), (1, hcx + 7)):
        base = (hcx + sgn * 3, hcy - 3)
        tip = (ex + sgn * 4, CROWN_Y - 6 + rcy)
        pygame.draw.line(surf, _STALK_RIM, base, tip, 5)
        pygame.draw.line(surf, _STALK, base, tip, 3)
        _jewel_eye(surf, tip[0], tip[1], 6, glow=glow)
