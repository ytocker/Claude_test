"""BUG/INSECT redesign — design_5 STINGREEL (Giant Hornet, Vespa).

The pinched wasp-waist is the hero read: a blocky orange head + thorax up
front, a hard dark cinch with SKY showing through the pinch, then a pointed
banded dart of an abdomen tapering to a visible stinger. Angular and menacing
where the retired bee was round and cute; the high-contrast black-on-amber
banding is the tell that survives the 40px shrink. Wings buzz in a frantic
wide arc with a motion-blur echo, selling speed and threat.

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
# Cool, light, translucent wing so the orange head reads THROUGH the wing
# rather than fusing with it into one brown blob up front at 40px.
WING   = (150, 140, 120)   # smoky grey-amber hyaline wing tint
WING_D = (120, 112, 96)    # faint wing vein
SPEC   = (255, 227, 154)   # specular sheen down the glossy exoskeleton
CATCH  = (255, 255, 255)   # eye catch-light

# Abdomen spindle axis — head is upper-right, the gaster trails to the lower-
# left as the hero mass. ABD_A is pushed down-left off the thorax so a real
# gap of sky opens under the cinch; the profile is a pointed dart, not an egg.
ABD_A = (BCX - 8, BCY + 10)     # fat end, held clear of the waist
ABD_B = (BCX - 26, BCY + 28)    # narrow end, where the stinger emerges
ABD_HALFW = 8.5


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _axis(a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    return (ax, ay, dx, dy, ux, uy, -uy, ux)   # +perp = (-uy, ux)


def _spindle(a, b, halfw, bias=0.82, n=10):
    """A tapered fusiform outline, fattest point biased toward the head end so
    the trailing tip draws out into a long sharp dart — the hornet's swollen
    banded gaster narrowing to a needle."""
    ax, ay, dx, dy, ux, uy, px, py = _axis(a, b)
    top, bot = [], []
    for i in range(n + 1):
        t = i / n
        w = halfw * math.sin(math.pi * (t ** bias))
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
    # The last band lands high (0.82) so the stinger tip emerges from AMBER.
    band = _new()
    mask = _new()
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    for t in (0.20, 0.42, 0.62, 0.82):
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

    # Amber shoulder just before the tip so the black stinger point separates
    # from the black band instead of merging into one dark smear at 40px.
    sh = (ax + dx * 0.9, ay + dy * 0.9)
    pygame.draw.circle(surf, SPEC, (int(sh[0]), int(sh[1])), 1)

    # Stinger: a long, thin dark needle continuing past the narrow tip.
    tipx, tipy = ax + dx * 1.0, ay + dy * 1.0
    stab = (tipx + ux * 8, tipy + uy * 8)
    pygame.draw.polygon(surf, INK, [
        (tipx + px * 1.6, tipy + py * 1.6),
        stab,
        (tipx - px * 1.6, tipy - py * 1.6),
    ])


# Thread attach point on the thorax underside — the thorax necks down toward
# the waist here, and a thin 2px thread bridges to the abdomen fat end.
WAIST_TOP = (31, 47)


def _thorax_poly():
    # Blocky, squared-off thorax with a concave V-notch cut UP into its
    # underside near the waist, so background intrudes above the cinch and the
    # wasp-waist pinch reads as a real anatomical break. Kept smaller than the
    # gaster so the abdomen stays the hero mass.
    return [
        (28, 35), (37, 33), (43, 37), (43, 43),
        (39, 47), (35, 44), (31, 47), (28, 42),
    ]


def _draw_thorax(surf):
    poly = _thorax_poly()
    pygame.draw.polygon(surf, ORANGE, poly)
    # Lower underside shade for chunky volume.
    pygame.draw.polygon(surf, ORANGE_D, [
        (28, 42), (31, 47), (35, 44), (39, 47), (37, 43), (30, 42),
    ])
    # Top-plate sheen streak (pronotum gloss).
    pygame.draw.line(surf, SPEC, (30, 36), (41, 38), 2)
    # Dark seam separating head from thorax so the two orange blocks read as
    # distinct segments rather than one merged blob.
    pygame.draw.line(surf, ORANGE_D, (42, 35), (44, 44), 2)


def _draw_waist(surf):
    # The signature: a 2px thread — visibly thinner than both masses — bridging
    # thorax → abdomen, with sky showing above it in the thorax notch.
    ab = (ABD_A[0] + 1, ABD_A[1] - 1)
    pygame.draw.line(surf, INK, WAIST_TOP, ab, 2)


def _draw_eye(surf, cx, cy, w, h, ang):
    # A solid dark teardrop, taller than wide and slanted down-toward-mandible
    # for an angry brow. Only a single 1px catch pip in the upper-outer corner,
    # so the eye reads DARK and menacing, not a white googly dot at 40px.
    es = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(es, INK, es.get_rect())
    es = pygame.transform.rotate(es, ang)
    surf.blit(es, es.get_rect(center=(cx, cy)))
    px = max(0, min(COMPOSITE_W - 1, int(cx - w * 0.35)))
    py = max(0, min(COMPOSITE_H - 1, int(cy - h * 0.35)))
    surf.set_at((px, py), CATCH)


def _draw_head(surf):
    # Angular wedge head — squared like a hornet's, never a round bead. Small
    # relative to the gaster; the mandible edge points forward (upper-right).
    head = [(41, 28), (48, 27), (52, 31), (51, 36), (45, 39), (41, 34)]
    pygame.draw.polygon(surf, ORANGE, head)
    pygame.draw.line(surf, SPEC, (43, 29), (49, 29), 1)   # brow gloss

    # Two menacing compound eyes slanted down toward the mandible.
    _draw_eye(surf, 45, 33, 6, 8, 38)
    _draw_eye(surf, 50, 32, 4, 6, 38)

    # Short blade-like mandibles jutting off the lower face.
    pygame.draw.polygon(surf, INK, [(50, 37), (54, 40), (49, 39)])

    # Two elbowed antennae — stiff, kinked, angular (not curved).
    for off in (0, 3):
        base = (HCX - 1 + off, HCY - 5)
        knee = (HCX - 3 + off, CROWN_Y + 2)
        tip  = (HCX - 5 + off, CROWN_Y - 2)
        pygame.draw.lines(surf, INK, False, [base, knee, tip], 2)
        pygame.draw.circle(surf, INK, tip, 1)


def _draw_legs(surf, fi):
    # Long jointed dark legs, hips seated UP on the thorax body and trailing
    # down the near side so NO leg line crosses the wasp-waist cinch. A faint
    # per-beat kick keeps them alive on the flap rig.
    kick = 2 if fi in (0, 3) else -1
    legs = (
        ((34, 45), (31, 55), (27, 63 + kick)),
        ((37, 45), (35, 57), (30, 66 + kick)),
        ((40, 44), (40, 56), (35, 66 + kick)),
    )
    for hip, knee, foot in legs:
        pygame.draw.lines(surf, INK, False, [hip, knee, foot], 2)


def _wing(length, width, angle_deg, alpha):
    w = pygame.Surface((length, width), pygame.SRCALPHA)
    pygame.draw.ellipse(w, (*WING, alpha), w.get_rect())
    pygame.draw.line(w, (*WING_D, min(255, alpha + 40)),
                     (2, width // 2), (length - 2, width // 2), 1)
    return pygame.transform.rotate(w, angle_deg)


def _blit_wing(surf, root, length, width, ang, alpha, echo_off):
    # A fainter, offset echo behind the crisp wing so each frame reads as a
    # buzzing arc rather than a solid plate.
    rad = math.radians(ang)
    cx = root[0] + math.cos(rad) * (length * 0.42)
    cy = root[1] - math.sin(rad) * (length * 0.42)
    echo = _wing(length, width, ang, 50)
    surf.blit(echo, echo.get_rect(center=(cx + echo_off[0], cy + echo_off[1])))
    ws = _wing(length, width, ang, alpha)
    surf.blit(ws, ws.get_rect(center=(cx, cy)))


def _draw_wings(surf, fi, *, front):
    # Frantic buzz: extremes (frames 0/3) fling the wings open and back, the
    # mid frames (1/2) sweep them tight — a real open/closed silhouette change
    # across a wide ~±16° arc, with a per-frame alpha pulse so the strip
    # shimmers. A tiny jitter breaks the 0/3 and 1/2 mirror so all four differ.
    spread = fi in (0, 3)
    jitter = 4 if fi in (0, 1) else -4
    swing = (16 if spread else -12) + jitter
    alpha = 165 if spread else 115
    echo = (-3, 2) if spread else (3, 2)
    fore_len = 33 if spread else 27
    root = (35, 36)
    if front:
        # Forewing + hindwing on the near side, buzzing up-and-back (up-left).
        _blit_wing(surf, root, fore_len, 9, 150 + swing, alpha, echo)
        _blit_wing(surf, root, fore_len - 6, 8, 134 + swing,
                   max(80, alpha - 35), echo)
    else:
        # Far wing, dimmer, peeking up-right from behind the thorax.
        _blit_wing(surf, root, 27, 8, 30 + swing * 0.6, 75,
                   (echo[0], -echo[1]))


def _build_frame(fi):
    surf = _new()
    _draw_wings(surf, fi, front=False)
    _draw_legs(surf, fi)
    _draw_abdomen(surf)
    _draw_waist(surf)
    _draw_thorax(surf)
    _draw_head(surf)
    _draw_wings(surf, fi, front=True)
    return surf


_state = {"frames": None, "rot": {}}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    if _state["frames"] is None:
        _state["frames"] = [_add_outline(_build_frame(i))
                            for i in range(len(_WING_ANGLES))]
    frame_idx %= 4
    key = (frame_idx, int(round(tilt_deg / 3)) * 3)
    if key not in _state["rot"]:
        _state["rot"][key] = pygame.transform.rotozoom(
            _state["frames"][frame_idx], key[1], 1.0)
    return _state["rot"][key]
