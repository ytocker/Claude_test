"""BUG/INSECT redesign — design_5 STINGREEL (Giant Hornet, Vespa).

The pinched wasp-waist is the hero read: a blocky orange head + thorax up
front, a hard dark neck gap, then a fat banded spindle abdomen tapering to a
visible stinger. Angular and menacing where the retired bee was round and
cute; the high-contrast black-and-amber banding is the tell that survives the
40px shrink. Wings buzz in a tight fast arc close to the back rather than a
broad butterfly sweep, selling speed and threat.

Scratch exploration only — NOT registered in store_skins.BUILDERS. Production
art stays untouched until a winner is picked.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44          # thorax centre
HCX, HCY = 44, 34          # head
CROWN_Y = 24

# ── palette ──────────────────────────────────────────────────────────────────
INK    = (18, 14, 10)      # bands / stinger / eyes / legs — the value anchor
ORANGE = (232, 128, 26)    # vespa orange — head + thorax
ORANGE_D = (176, 92, 14)   # thorax underside shade for volume
AMBER  = (246, 198, 60)    # warm amber abdomen band highlight
WING   = (110, 74, 16)     # smoked hyaline wing tint
WING_D = (80, 54, 12)      # wing leading-edge vein
SPEC   = (255, 227, 154)   # specular sheen down the glossy exoskeleton
CATCH  = (255, 255, 255)   # eye catch-light

# Abdomen spindle axis — head is upper-right, abdomen trails to the lower-left.
# The gaster is the hero mass, so it is the largest single shape: long and fat.
ABD_A = (BCX - 5, BCY + 7)      # fat end, tucked under the waist
ABD_B = (BCX - 23, BCY + 25)    # narrow end, where the stinger emerges
ABD_HALFW = 10.0


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(a):
    # 0 = down-beat, 1 = up-beat; used only to jitter the buzzing wings.
    return (a + 40) / 90.0


def _axis(a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    return (ax, ay, dx, dy, ux, uy, -uy, ux)   # +perp = (-uy, ux)


def _spindle(a, b, halfw, n=9):
    """A tapered fusiform outline: zero width at both tips, fattest mid-body —
    the hornet's swollen banded gaster."""
    ax, ay, dx, dy, ux, uy, px, py = _axis(a, b)
    top, bot = [], []
    for i in range(n + 1):
        t = i / n
        w = halfw * math.sin(math.pi * t)
        cx, cy = ax + dx * t, ay + dy * t
        top.append((cx + px * w, cy + py * w))
        bot.append((cx - px * w, cy - py * w))
    return top + bot[::-1]


def _draw_abdomen(surf):
    a, b, halfw = ABD_A, ABD_B, ABD_HALFW
    poly = _spindle(a, b, halfw)
    ax, ay, dx, dy, ux, uy, px, py = _axis(a, b)

    # Amber base, so the ink bands read as a black-on-amber wasp pattern.
    abd = _new()
    pygame.draw.polygon(abd, AMBER, poly)

    # Bold ink bands: thick strokes swept across the body axis, then clipped to
    # the spindle so they wrap the taper instead of spilling past the outline.
    band = _new()
    mask = _new()
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    for t in (0.22, 0.46, 0.70, 0.92):
        cx, cy = ax + dx * t, ay + dy * t
        reach = halfw + 5
        pygame.draw.line(band, INK, (cx + px * reach, cy + py * reach),
                         (cx - px * reach, cy - py * reach), 4)
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    abd.blit(band, (0, 0))
    surf.blit(abd, (0, 0))

    # Specular sheen line down the upper/top edge — the hard-shell gloss.
    sp0 = (ax + dx * 0.2 + px * (halfw * 0.45), ay + dy * 0.2 + py * (halfw * 0.45))
    sp1 = (ax + dx * 0.78 + px * (halfw * 0.35), ay + dy * 0.78 + py * (halfw * 0.35))
    pygame.draw.line(surf, SPEC, sp0, sp1, 2)

    # Stinger: a sharp dark point continuing past the narrow tip.
    tipx, tipy = ax + dx * 1.0, ay + dy * 1.0
    stab = (tipx + ux * 6, tipy + uy * 6)
    pygame.draw.polygon(surf, INK, [
        (tipx + px * 2.4, tipy + py * 2.4),
        stab,
        (tipx - px * 2.4, tipy - py * 2.4),
    ])


THORAX_NECK = (30, 48)          # lower-left corner that pinches to the waist


def _thorax_poly():
    # Blocky, squared-off thorax that necks down toward the waist (lower-left)
    # so the pinch reads as a real anatomical break, not a smooth taper. Kept
    # deliberately smaller than the gaster so the abdomen stays the hero mass.
    return [
        (28, 35), (37, 33), (43, 37), (43, 43),
        (38, 48), (31, 49), (28, 42),
    ]


def _draw_thorax(surf):
    poly = _thorax_poly()
    pygame.draw.polygon(surf, ORANGE, poly)
    # Lower-left underside shade for chunky volume.
    pygame.draw.polygon(surf, ORANGE_D, [
        (28, 42), (31, 49), (38, 48), (36, 43), (30, 42),
    ])
    # Top-plate sheen streak (pronotum gloss).
    pygame.draw.line(surf, SPEC, (30, 36), (41, 38), 2)
    # Dark seam separating head from thorax so the two orange blocks read as
    # distinct segments rather than one merged blob.
    pygame.draw.line(surf, ORANGE_D, (42, 35), (44, 44), 2)


def _draw_waist(surf):
    # The signature: a very narrow dark connector bridging thorax → abdomen.
    tn = THORAX_NECK
    ab = (ABD_A[0] + 1, ABD_A[1] - 1)
    pygame.draw.polygon(surf, INK, [
        (tn[0] + 2, tn[1] - 1), (tn[0] - 2, tn[1] + 1),
        (ab[0] - 2, ab[1] + 1), (ab[0] + 2, ab[1] - 1),
    ])


def _draw_head(surf):
    # Angular wedge head — squared like a hornet's, never a round bead. Small
    # relative to the gaster; the mandible edge points forward (upper-right).
    head = [(41, 28), (48, 27), (52, 31), (51, 36), (45, 39), (41, 34)]
    pygame.draw.polygon(surf, ORANGE, head)
    pygame.draw.line(surf, SPEC, (43, 29), (49, 29), 1)   # brow gloss

    # Two teardrop compound eyes, one to each side of the face.
    for (ex, ey, rx, ry) in ((44, 33, 3, 4), (50, 32, 2, 3)):
        _aaellipse(surf, INK, (ex, ey), rx, ry)
        pygame.draw.circle(surf, CATCH, (ex - 1, ey - 1), 1)

    # Short blade-like mandibles jutting off the lower face.
    pygame.draw.polygon(surf, INK, [(50, 37), (54, 40), (49, 39)])

    # Two elbowed antennae — stiff, kinked, angular (not curved).
    for off in (0, 3):
        base = (HCX - 1 + off, HCY - 5)
        knee = (HCX - 3 + off, CROWN_Y + 2)
        tip  = (HCX - 5 + off, CROWN_Y - 2)
        pygame.draw.lines(surf, INK, False, [base, knee, tip], 2)
        pygame.draw.circle(surf, INK, tip, 1)


def _draw_legs(surf, f):
    # Long jointed dark legs trailing back and down in flight — 2 joints each,
    # angular. A faint per-beat kick keeps them alive on the flap rig.
    kick = (f - 0.5) * 3
    legs = (
        ((30, 47), (24, 56), (17, 58 + kick)),
        ((33, 48), (29, 60), (21, 65 + kick)),
        ((36, 47), (35, 59), (28, 68 + kick)),
    )
    for hip, knee, foot in legs:
        pygame.draw.lines(surf, INK, False, [hip, knee, foot], 2)


def _wing(length, width, angle_deg, alpha):
    w = pygame.Surface((length, width), pygame.SRCALPHA)
    pygame.draw.ellipse(w, (*WING, alpha), w.get_rect())
    pygame.draw.line(w, (*WING_D, min(255, alpha + 60)),
                     (2, width // 2), (length - 2, width // 2), 1)
    return pygame.transform.rotate(w, angle_deg)


def _draw_wings(surf, f, *, front):
    # Narrow hyaline wings held up over the back, folded lengthwise (thin, not
    # broad sails). They buzz in a tight fast arc — a small ±4° jitter — rather
    # than a wide butterfly sweep, selling speed and threat.
    buzz = (f - 0.5) * 8
    root = (35, 36)
    if front:
        # Forewing + hindwing on the near side, sweeping up-and-back (up-left).
        # Kept semi-transparent so the hyaline wing reads as glass, not a slab.
        specs = ((30, 9, 150 + buzz, 150), (25, 8, 133 + buzz, 120))
    else:
        # Far wing, dimmer, peeking up-right from behind the thorax.
        specs = ((27, 8, 34 + buzz, 85),)
    for length, width, ang, alpha in specs:
        ws = _wing(length, width, ang, alpha)
        rad = math.radians(ang)
        # Place the wing body along its sweep so the root sits on the thorax.
        cx = root[0] + math.cos(rad) * (length * 0.42)
        cy = root[1] - math.sin(rad) * (length * 0.42)
        surf.blit(ws, ws.get_rect(center=(cx, cy)).topleft)


def _build_frame(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)

    _draw_wings(surf, f, front=False)
    _draw_legs(surf, f)
    _draw_abdomen(surf)
    _draw_waist(surf)
    _draw_thorax(surf)
    _draw_head(surf)
    _draw_wings(surf, f, front=True)
    return surf


_state = {"frames": None, "rot": {}}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    if _state["frames"] is None:
        _state["frames"] = [_add_outline(_build_frame(a)) for a in _WING_ANGLES]
    frame_idx %= 4
    key = (frame_idx, int(round(tilt_deg / 3)) * 3)
    if key not in _state["rot"]:
        _state["rot"][key] = pygame.transform.rotozoom(
            _state["frames"][frame_idx], key[1], 1.0)
    return _state["rot"][key]
