"""GLINTWING — bug/insect skin candidate (Design 4): a Dragonfly.

The anti-bee. Where every other bug reads round and chunky, GLINTWING is a
long slender jewel-green needle held horizontal, crossed by four narrow glassy
wings in an X. That elongated cross — not a blob — is the 40px tell. Two
huge iridescent compound eyes own the head; the abdomen marches lower-left in
banded emerald/dark segments to a fine point.

The four wings beat in OPPOSITION (forewings up while hindwings drop) — the
real dragonfly signature — driven off the shared flap rig so the motion stays
in lock-step with the other skins.

Scratch exploration builder — wrapped by the ninja_render harness, never
registered in store_skins.BUILDERS.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44          # thorax centre — the solid anchor
HCX, HCY = 44, 34          # head, up-right along the body axis
CROWN_Y = 24

# Jewel-toned dragonfly palette.
EMERALD   = (14, 92, 74)     # #0E5C4A — thorax / wing edge
JEWEL     = (34, 195, 154)   # #22C39A — bright body segments / eye iris
GLASS     = (184, 255, 240)  # #B8FFF0 — glassy wing membrane (semi-alpha)
MAGENTA   = (232, 90, 216)   # #E85AD8 — pterostigma + eye catchlight
VEIN_DARK = (8, 32, 28)      # #08201C — dark bands / vein shadow / eye shell
VEIN_LINE = (100, 200, 180)  # faint wing veins


def _flap(a):
    return (a + 40) / 90.0


def _seg(surf, cx, cy, color, along, across, angle=45):
    """One abdomen segment: an x-elongated ellipse tilted onto the body axis
    so the segments read as a narrow banded needle, not a bead chain."""
    pad = 2
    w = int(along * 2 + pad * 2)
    h = int(across * 2 + pad * 2)
    tile = pygame.Surface((w, h), pygame.SRCALPHA)
    _aaellipse(tile, color, (w / 2, h / 2), along, across)
    tile = pygame.transform.rotate(tile, angle)
    surf.blit(tile, tile.get_rect(center=(cx, cy)))


def _blit_rot(dest, image, pivot_img, anchor, angle):
    """Blit `image` rotated by `angle` (CCW) so its `pivot_img` point lands on
    `anchor` — used to fan each wing out from the thorax hub."""
    rect = image.get_rect(topleft=(anchor[0] - pivot_img[0],
                                   anchor[1] - pivot_img[1]))
    offset = pygame.math.Vector2(anchor) - pygame.math.Vector2(rect.center)
    offset = offset.rotate(-angle)
    center = (anchor[0] - offset.x, anchor[1] - offset.y)
    rotated = pygame.transform.rotate(image, angle)
    dest.blit(rotated, rotated.get_rect(center=center))


def _wing(length, is_fore):
    """A single long narrow glassy membrane extending to +x from a left-edge
    pivot, with a green rim, a few veins and a magenta pterostigma near the
    tip. Kept at moderate alpha so it still casts shape at 40px."""
    width = 6
    pivot = (5, 12)
    surf = pygame.Surface((int(length + 12), 24), pygame.SRCALPHA)
    cx = pivot[0] + length / 2
    cy = pivot[1]
    ry = width / 2
    # Hindwings flare a touch wider at the base — the real dragonfly proportion.
    base_ry = ry + (1.4 if not is_fore else 0.0)
    _aaellipse(surf, (*JEWEL, 60), (pivot[0] + 6, cy), 4, base_ry)
    _aaellipse(surf, (*GLASS, 140), (cx, cy), length / 2, ry)
    # Green rim so the transparent membrane keeps a defined edge.
    rect = pygame.Rect(int(pivot[0]), int(cy - ry), int(length), int(ry * 2))
    pygame.draw.ellipse(surf, EMERALD, rect, 1)
    # Fine veins running the length of the wing.
    tip_x = pivot[0] + length
    for vy in (cy - 1.4, cy, cy + 1.4):
        pygame.draw.line(surf, (*VEIN_LINE, 80),
                         (pivot[0] + 3, cy), (tip_x - 2, vy), 1)
    # Pterostigma — magenta cell near the leading tip.
    pygame.draw.circle(surf, MAGENTA, (int(tip_x - 4), int(cy - 1)), 2)
    return surf, pivot


def _build_frame(wing_angle_deg):
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    f = _flap(wing_angle_deg)
    spread = (f - 0.5) * 16.0
    lift = spread * 0.7          # forewings and hindwings beat in opposition

    fore_len, hind_len = 26, 20
    fore_r, fore_pivot = _wing(fore_len, is_fore=True)
    hind_r, hind_pivot = _wing(hind_len, is_fore=False)

    hub = (BCX + 1, BCY - 2)
    # Right forewing up-right, left mirrored; hindwings drop opposite the beat.
    _blit_rot(surf, fore_r, fore_pivot, hub, 28 + lift)          # fore right
    _blit_rot(surf, fore_r, fore_pivot, hub, 152 - lift)         # fore left
    _blit_rot(surf, hind_r, hind_pivot, (BCX, BCY + 2), -22 - lift)   # hind right
    _blit_rot(surf, hind_r, hind_pivot, (BCX, BCY + 2), 202 + lift)   # hind left

    # --- Abdomen: banded needle marching lower-left from the thorax ---
    n = 6
    for i in range(n):
        t = i / (n - 1)
        cx = 30 - 16 * t
        cy = 47 + 16 * t
        along = 4.0 - 1.2 * t
        across = 3.0 - 1.3 * t
        color = JEWEL if i % 2 == 0 else VEIN_DARK
        _seg(surf, cx, cy, color, along, across)
    # A thin jewel spine tying the segments into one needle.
    pygame.draw.line(surf, JEWEL, (30, 47), (15, 62), 1)
    # Dark tail point.
    pygame.draw.polygon(surf, VEIN_DARK,
                        [(15, 61), (11, 66), (16, 63)])

    # --- Thorax: the chunky solid anchor that survives the 40px shrink ---
    _aaellipse(surf, EMERALD, (BCX, BCY), 7, 6)
    _aaellipse(surf, JEWEL, (BCX - 1, BCY - 2), 4, 3)   # top sheen
    _aaellipse(surf, EMERALD, (BCX, BCY + 1), 5, 4)

    # --- Legs: short bristled cluster bunched under the thorax toward the head ---
    for lx, ly in ((BCX + 2, BCY + 4), (BCX + 5, BCY + 4), (BCX + 7, BCY + 3)):
        pygame.draw.line(surf, VEIN_DARK, (lx, ly), (lx + 1, ly + 5), 1)
        pygame.draw.line(surf, VEIN_DARK, (lx + 1, ly + 5), (lx + 3, ly + 6), 1)

    # --- Head + huge compound eyes (the hero tell) ---
    _aaellipse(surf, EMERALD, (HCX, HCY), 7, 6)          # slim head base
    # Two big compound eyes fill the head; front eye leads up-right.
    for (ex, ey, rx, ry) in ((HCX + 3, HCY - 1, 8, 7), (HCX - 4, HCY + 1, 6, 6)):
        _aaellipse(surf, VEIN_DARK, (ex, ey), rx, ry)             # dark shell
        _aaellipse(surf, JEWEL, (ex - 1, ey - 1), rx - 3, ry - 3)  # iridescent iris
        pygame.draw.circle(surf, MAGENTA, (int(ex + 1), int(ey - 2)), 1)  # catchlight
        pygame.draw.circle(surf, (240, 255, 250), (int(ex - 2), int(ey - 2)), 1)

    return surf


_state = {}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    angle = _WING_ANGLES[frame_idx % len(_WING_ANGLES)]
    key = (frame_idx % len(_WING_ANGLES), round(tilt_deg / 3) * 3)
    if key not in _state:
        _state[key] = pygame.transform.rotozoom(
            _add_outline(_build_frame(angle)), key[1], 1.0)
    return _state[key]
