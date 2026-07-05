"""Shared kit for the PUFFERFISH redesign candidates.

The production puffer reads as a SUN (golden disc + symmetric radial needle
halo). Every candidate here keeps the cute inflated body + inflate gag but adds
FISH anatomy — a tail fin, side fins, an oriented face — and tames the radial
spikes, so it can never be mistaken for a sun. This module holds the parts the
five designs reuse; each design composes them + its distinctive bit.

Mirrors the production contract: builders take (wing_angle_deg) and draw one
flat frame on a 64×84 canvas with the body mass pinned at (BCX,BCY)=(32,44);
`_make_prebuilt_skin` wraps to the cached (frame_idx, tilt_deg) getter.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse,
)

COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY          # body centre → (32, 44), fixed every frame


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
    """0..1 'wing is up' factor. _WING_ANGLES runs 50 (down) → -40 (up)."""
    return (angle_deg + 40) / 90.0


def _inflate(angle_deg):
    """1.0 fully INFLATED on the down-pose → ~0.0 deflated on the up-pose."""
    return 1.0 - _flap(angle_deg)


def _shade(col, f):
    return tuple(max(0, min(255, int(c * f))) for c in col)


def _eye(surf, cx, cy, r, *, iris=(52, 36, 14), white=(255, 250, 240)):
    """Friendly round eye: a real white margin (iris r-2 so the sclera shows all
    around, never a black socket) + a fat top-left catchlight that sells 'alive'
    at 40px."""
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 2))
    pygame.draw.circle(surf, (255, 255, 255),
                       (cx - r // 3, cy - r // 3), max(1, r // 2))


def _radial_body(surf, cx, cy, rx, ry, core, mid, edge):
    """Sphere value structure: dark rim → mid mass → light core (up-left) + a
    crisp specular. Accepts rx≠ry so a design can use an OVAL (non-sun) body."""
    _aaellipse(surf, edge, (cx + 1, cy + 1), rx, ry)
    _aaellipse(surf, mid,  (cx, cy), rx - 1, ry - 1)
    _aaellipse(surf, core, (cx - 2, cy - 2), rx - 5, ry - 5)
    _aaellipse(surf, _shade(core, 1.10), (cx - 5, cy - 6), 4, 3)


def _tail_fin(surf, x, y, size, col_dark, col_light, *, flip=False, ribs=True):
    """A FORKED fan tail fin rooted at (x,y) sweeping back, with a V-notch cut
    into the trailing edge — the classic fishtail shape. `flip` mirrors it. This
    + the oriented face is the core anti-sun fix (a front→back axis + a forked
    tail are shapes a radial sun never has)."""
    s = -1 if flip else 1
    bx = x - s * size                      # trailing (back) edge
    notch = x - s * int(size * 0.5)        # fork bites inward toward the root
    pygame.draw.polygon(surf, col_dark, [
        (x, y - size // 2), (bx, y - size), (notch, y),
        (bx, y + size), (x, y + size // 2)])
    pygame.draw.polygon(surf, col_light, [
        (x, y - size // 3), (x - s * (size - 2), y - size + 2),
        (notch + s, y), (x - s * (size - 2), y + size - 2),
        (x, y + size // 3)])
    if ribs:
        for ry in (-size + 3, 0, size - 3):
            pygame.draw.line(surf, col_dark, (x, y + ry // 3),
                             (x - s * (size - 1), y + ry), 1)


def _side_fin(surf, x, y, size, col_dark, col_light, *, flip=False):
    """A small pectoral fin flicking out from the body side."""
    s = -1 if flip else 1
    pts = [(x, y - size), (x + s * size, y), (x, y + size)]
    pygame.draw.polygon(surf, col_dark, pts)
    pygame.draw.polygon(surf, col_light,
                        [(x, y - size + 1), (x + s * (size - 1), y),
                         (x, y + size - 1)])


def _spots(surf, cx, cy, rx, ry, col, seed_pts):
    """Scatter small dark spots inside the body ellipse (the aquatic tell).
    `seed_pts` is a fixed list of (dx,dy,r) offsets so the 4 cached frames stay
    stable (no RNG)."""
    for dx, dy, rr in seed_pts:
        pygame.draw.circle(surf, col, (cx + dx, cy + dy), rr)


def _spike_field(n, *, base=0.7, var=0.5, gap=(-0.6, 0.6), seed=0):
    """Generate `n` stub-spike placements wrapped around the body with a small
    DETERMINISTIC length jitter (irregular bumpy skin, never even rays) and a
    clear angular `gap` over the face/front so the studs never close into a full
    radial halo. Angles in radians: 0 = front (+x), -pi/2 = top. Returns a list
    of (angle, len_scale) for `_stub_spikes`. No RNG → the 4 cached frames are
    stable. Pass gap=None to wrap the whole body."""
    out = []
    glo, ghi = gap if gap else (1.0, -1.0)
    for i in range(n):
        a = -math.pi + (2 * math.pi) * (i + 0.5) / n
        if gap and glo <= a <= ghi:
            continue
        ls = base + var * (((i * 5 + seed * 3) % 7) / 6.0)
        out.append((a, ls))
    return out


def _stub_spikes(surf, cx, cy, rx, ry, length, col_base, col_tip, placements):
    """Short, BLUNT cone spines at fixed (angle, scale) placements — scattered,
    not a clean radial fan. This is the anti-sun spike: stubby + staggered so it
    reads as bumpy puffer skin, never as solar rays. `placements` = list of
    (angle_rad, len_scale)."""
    for a, ls in placements:
        bx, by = math.cos(a), math.sin(a)
        root = (cx + bx * (rx - 2), cy + by * (ry - 2))
        ln = length * ls
        # base width along the tangent
        tx, ty = -by, bx
        w = 2.4
        p_l = (root[0] + tx * w, root[1] + ty * w)
        p_r = (root[0] - tx * w, root[1] - ty * w)
        tip = (cx + bx * (rx + ln), cy + by * (ry + ln))
        pygame.draw.polygon(surf, col_base, [p_l, p_r, tip])
        # bright nub near the tip for the value step
        pygame.draw.line(surf, col_tip, root, tip, 1)


def _pouty_o(surf, x, y, lip=(140, 72, 64)):
    """The charming pouty O-mouth (warm dark ring, not a black hole)."""
    pygame.draw.circle(surf, lip, (x, y), 3)
    pygame.draw.circle(surf, (96, 48, 44), (x, y), 2)
    pygame.draw.circle(surf, (200, 120, 110), (x - 1, y - 1), 1)
