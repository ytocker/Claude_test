"""Shared kit for the SUN secret-item candidates — copied from the original
`animal_pufferfish` star-burst helpers (the art this item is born from) plus a
few sun-specific ray styles.

The puffer's inflate gag becomes a SHINE pulse: the disc brightens + the corona
flares on the down-stroke (`_shine` ~1.0), settling on the up-stroke. Body mass
pinned at (BCX,BCY)=(32,44) every frame so the collision circle stays fair.
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


def _make_glow_skin(build_fn, glow_fn):
    """Like `_make_prebuilt_skin`, but composites a translucent bloom UNDERNEATH
    the outlined sun so `_add_outline` (threshold=8) never stamps a dark halo
    ring around the soft glow. `build_fn(angle)` draws the OPAQUE sun (no glow);
    `glow_fn(angle)` returns a 64×84 bloom layer drawn behind it."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            frames = []
            for a in _WING_ANGLES:
                outlined = _add_outline(build_fn(a))
                ow, oh = outlined.get_size()
                res = pygame.Surface((ow, oh), pygame.SRCALPHA)
                glow = glow_fn(a)
                res.blit(glow, glow.get_rect(center=(ow // 2, oh // 2)))
                res.blit(outlined, (0, 0))
                frames.append(res)
            state["frames"] = frames
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


def _flap(angle_deg):
    return (angle_deg + 40) / 90.0


def _shine(angle_deg):
    """1.0 = fully radiant on the down-stroke → ~0.0 on the up-stroke."""
    return 1.0 - _flap(angle_deg)


def _shade(col, f):
    return tuple(max(0, min(255, int(c * f))) for c in col)


def _eye(surf, cx, cy, r, *, iris=(58, 42, 18), white=(255, 250, 240)):
    """Friendly round eye with a real white margin + a fat top-left catchlight."""
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 2))
    pygame.draw.circle(surf, (255, 255, 255),
                       (cx - r // 3, cy - r // 3), max(1, r // 2))


def _radial_body(surf, cx, cy, r, core, mid, edge):
    """Sun disc with internal value structure: dark rim → mid → light core
    (offset up-left) + a crisp specular."""
    _aaellipse(surf, edge, (cx + 1, cy + 1), r, r)
    _aaellipse(surf, mid,  (cx, cy), r - 1, r - 1)
    _aaellipse(surf, core, (cx - 2, cy - 2), r - 5, r - 5)
    _aaellipse(surf, _shade(core, 1.10), (cx - 5, cy - 6), 4, 3)


def _spike_ring(surf, cx, cy, r_in, length, n, col_base, col_tip, start=0.0,
                taper=0.42):
    """Radial halo of two-tone needle rays (the puffer star-burst, now a sun
    corona). Each ray = a dark base wedge + a brighter tip so the value step
    survives the 40px downscale."""
    half = math.radians((360.0 / n) * taper) * 0.5
    for i in range(n):
        a = start + (2 * math.pi) * i / n
        bx, by = math.cos(a), math.sin(a)
        l_a, r_a = a - half, a + half
        p_l = (cx + math.cos(l_a) * r_in, cy + math.sin(l_a) * r_in)
        p_r = (cx + math.cos(r_a) * r_in, cy + math.sin(r_a) * r_in)
        tip = (cx + bx * (r_in + length), cy + by * (r_in + length))
        m_l = (cx + math.cos(l_a) * (r_in + length * 0.40),
               cy + math.sin(l_a) * (r_in + length * 0.40))
        m_r = (cx + math.cos(r_a) * (r_in + length * 0.40),
               cy + math.sin(r_a) * (r_in + length * 0.40))
        pygame.draw.polygon(surf, col_base, [p_l, p_r, m_r, m_l])
        pygame.draw.polygon(surf, col_tip, [m_l, m_r, tip])


def _ray_ring_alt(surf, cx, cy, r_in, long_len, short_len, n, col_base, col_tip,
                  start=0.0, taper=0.42):
    """The classic sun corona: a full even ring of triangular rays ALTERNATING
    long/short, so the silhouette reads instantly as a sun. `n` long rays with a
    short ray between each."""
    _spike_ring(surf, cx, cy, r_in, long_len, n, col_base, col_tip,
                start=start, taper=taper)
    _spike_ring(surf, cx, cy, r_in, short_len, n, col_base, col_tip,
                start=start + math.pi / n, taper=taper * 0.8)


def _flame_ring(surf, cx, cy, r_in, length, n, col_base, col_tip, sweep=0.5,
                start=0.0):
    """A corona of CURVED flame tongues — each ray's tip is rotated tangentially
    by `sweep` rad so the sun looks like it's spinning/blazing, not static."""
    for i in range(n):
        a = start + (2 * math.pi) * i / n
        bx, by = math.cos(a), math.sin(a)
        half = (math.pi / n) * 0.7
        p_l = (cx + math.cos(a - half) * r_in, cy + math.sin(a - half) * r_in)
        p_r = (cx + math.cos(a + half) * r_in, cy + math.sin(a + half) * r_in)
        ta = a + sweep
        tip = (cx + math.cos(ta) * (r_in + length),
               cy + math.sin(ta) * (r_in + length))
        m = (cx + math.cos(a + sweep * 0.5) * (r_in + length * 0.5),
             cy + math.sin(a + sweep * 0.5) * (r_in + length * 0.5))
        pygame.draw.polygon(surf, col_base, [p_l, p_r, tip])
        pygame.draw.polygon(surf, col_tip, [m, p_r, tip])


def _stub_ring(surf, cx, cy, r_in, length, n, col_base, col_tip, start=0.0):
    """A corona of soft ROUNDED bobble rays (circles) — the kawaii sun: gentle
    scallops, not sharp needles."""
    for i in range(n):
        a = start + (2 * math.pi) * i / n
        bx, by = math.cos(a), math.sin(a)
        tx, ty = cx + bx * (r_in + length), cy + by * (r_in + length)
        pygame.draw.circle(surf, col_base, (int(tx), int(ty)), max(2, length - 1))
        pygame.draw.circle(surf, col_tip,
                           (int(tx - 1), int(ty - 1)), max(1, length - 3))


def _sun_face(surf, cx, cy, *, eye_dx=6, eye_r=4, iris=(80, 44, 16),
              mouth="smile", blush=None, brow=None):
    """The cartoon sun face: two friendly eyes + a mouth, optional blush + brows.
    Locked to the disc centre so it never slides between frames."""
    if brow:
        pygame.draw.line(surf, brow, (cx - eye_dx - 3, cy - eye_r - 1),
                         (cx - eye_dx + 2, cy - eye_r + 1), 2)
        pygame.draw.line(surf, brow, (cx + eye_dx - 2, cy - eye_r + 1),
                         (cx + eye_dx + 3, cy - eye_r - 1), 2)
    if blush:
        pygame.draw.circle(surf, blush, (cx - eye_dx - 2, cy + 4), 2)
        pygame.draw.circle(surf, blush, (cx + eye_dx + 2, cy + 4), 2)
    _eye(surf, cx - eye_dx, cy, eye_r, iris=iris)
    _eye(surf, cx + eye_dx, cy, eye_r, iris=iris)
    my = cy + 6
    # Upward-opening grins (the arc spans the BOTTOM half of its box so it curves
    # up at the corners — an unambiguous happy mouth at 40px).
    if mouth == "smile":
        pygame.draw.arc(surf, (110, 64, 34), (cx - 6, my - 5, 12, 9), 3.45, 6.0, 2)
    elif mouth == "grin":
        pygame.draw.arc(surf, (110, 60, 30), (cx - 7, my - 5, 14, 11), 3.35, 6.07, 3)
    elif mouth == "o":
        pygame.draw.circle(surf, (150, 72, 50), (cx, my + 1), 3)
        pygame.draw.circle(surf, (96, 48, 44), (cx, my + 1), 2)
    elif mouth == "tiny":
        pygame.draw.arc(surf, (110, 64, 34), (cx - 4, my - 2, 8, 7), 3.5, 5.95, 2)
