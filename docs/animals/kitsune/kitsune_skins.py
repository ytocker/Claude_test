"""Candidate KITSUNE skins — round-1 exploration for the ANIMALS store.

KITSUNE (`skin_kitsune`) is the top-ranked legendary showpiece: a celestial
nine-tailed fox, NON-bird. The flying "wings" are the nine-tail FAN — it
sweeps wide on the down-pose and gathers on the up-pose across the 4 base
wing poses (`parrot._WING_ANGLES = 50,20,-10,-40`). There is no live particle
system, so the foxfire glow + gold aura + wisp accents are BAKED into each of
the 4 frames; the flicker is expressed by varying tail spread + wisp
positions between frames.

Contract (mirrors game/animal_skins.py so the winner lifts straight in):

  * `build_kitsune_vN(wing_angle_deg) -> pygame.Surface`  one flat 64×84 frame.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a LOCAL
    `_make_prebuilt_skin(build_fn)` copy.
  * `BUILDERS = {label: getter}` registry at the bottom (label→getter).

Geometry: collision is a fixed 14px circle at the BODY centre, so every
variant keeps the fox body mass anchored at BCX,BCY=(32,44). The head sits at
HCX,HCY≈(44,34); the nine-tail fan spreads BEHIND/AROUND the body and may go
wide, but the body itself stays centred.

North star: "a skin lives or dies at 40px in motion." Each variant leans on
ONE bold silhouette (fox + tail-burst) and ONE high-contrast signature
feature (the glowing forehead blaze + the multi-tail foxfire burst) that must
read against bright-day AND night skies.

These are 5 GENUINELY DIFFERENT takes, not 5 tweaks:
  v1 TENKO ASCENDANT — celestial WHITE fur, leaping pose, full nine violet-
     tipped tails in a wide halo fan, gold aura. Regal + cute.
  v2 KYUBI EMBER     — classic RUSSET fox, gold-fire tail tips, aggressive
     forward leap, dense gold foxfire, a flame-shaped blaze. Fierce.
  v3 CURLED ORACLE   — curled-regal seated fox, tails sweeping UP as a peacock
     fan of white-fire, a round moon-disc blaze. Serene shrine-spirit.
  v4 VIOLET WISP     — implied fan (bold 5 read tails + ghost wisps), heavy
     VIOLET foxfire dominant, white body, comet-like wisp trails. Spooky-myth.
  v5 PRISM TENKO     — white body with a gold→violet GRADIENT tail fan (warm
     inner, cool outer), diamond blaze, balanced spread. Premium jewel look.
"""
import math
import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (tail fan + foxfire need headroom) ─────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body centre → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre → (44, 34)
CROWN_Y  = 12 + DY              # top of head → 24


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter (local copy)."""
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
    """0..1 'tail-fan is GATHERED (up-pose)' factor. _WING_ANGLES runs 50→-40,
    so down-pose (50) → 0 (wide spread) and up-pose (-40) → 1 (gathered)."""
    return (angle_deg + 40) / 90.0


def _eye(surf, cx, cy, r, *, iris=(40, 24, 48), white=(252, 250, 248)):
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 1))
    pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3),
                       max(1, r // 3))


def _soft_glow(surf, center, radius, color, alpha):
    """A baked radial glow blob: cheap, additive-looking warmth/foxfire that
    survives the downscale as a halo. Pre-multiplied falloff in 3 rings."""
    cx, cy = center
    glow = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
    gc = radius + 1
    for i, frac in enumerate((1.0, 0.66, 0.34)):
        a = int(alpha * (0.4 + 0.6 * (1 - frac)))
        pygame.draw.circle(glow, (*color, a), (gc, gc), int(radius * frac))
    surf.blit(glow, (cx - gc, cy - gc), special_flags=pygame.BLEND_RGBA_ADD)


# ── shared palette (per brief) ───────────────────────────────────────────────
FUR        = (255, 244, 214)        # #FFF4D6
FUR_D      = (224, 206, 168)
FUR_H      = (255, 252, 240)
TIP        = (255, 122, 26)         # #FF7A1A ear/tail tip
BLAZE      = (255, 255, 255)        # #FFFFFF blaze mark
WISP       = (184, 107, 255)        # #B86BFF foxfire
WISP_H     = (214, 170, 255)
AURA       = (255, 210, 77)         # #FFD24D
RUSSET     = (224, 122, 52)
RUSSET_D   = (180, 88, 34)
RUSSET_H   = (255, 168, 96)
GOLDFIRE   = (255, 196, 70)
GOLDFIRE_H = (255, 234, 150)
NOSE       = (60, 40, 56)


def _tail(surf, base, ang_deg, length, width, col_root, col_tip,
          tip_kind="violet", curl=0.18):
    """One fox tail: a LONG tapering plume from `base` swept to `ang_deg`,
    fur-root → bright flame-tip. The plume narrows to a point and the flame
    puff is small + bright so the SHAPE (a tail, not a pompom) survives 40px.
    `curl` hooks the tip so the fan reads as soft S-curves, not stiff spokes."""
    bx, by = base
    a = math.radians(ang_deg)
    ax, ay = math.cos(a), -math.sin(a)
    px, py = -ay, ax                       # perpendicular
    # Curl pulls the tip sideways for a flame-hook silhouette.
    tipx = bx + ax * length + px * curl * length
    tipy = by + ay * length + py * curl * length
    # Belly of the plume (fattest ~40% out), then taper to the tip.
    b1x, b1y = bx + ax * length * 0.40, by + ay * length * 0.40
    b2x, b2y = bx + ax * length * 0.72 + px * curl * length * 0.5, \
        by + ay * length * 0.72 + py * curl * length * 0.5
    half = width / 2
    pts = [
        (bx + px * half * 0.7, by + py * half * 0.7),
        (b1x + px * half, b1y + py * half),
        (b2x + px * half * 0.55, b2y + py * half * 0.55),
        (tipx, tipy),
        (b2x - px * half * 0.55, b2y - py * half * 0.55),
        (b1x - px * half, b1y - py * half),
        (bx - px * half * 0.7, by - py * half * 0.7),
    ]
    pygame.draw.polygon(surf, col_root, [(int(x), int(y)) for x, y in pts])
    # A lighter inner highlight up the spine so each tail reads as separate.
    pygame.draw.line(surf, col_tip, (int(bx), int(by)),
                     (int(b2x), int(b2y)), max(1, width // 3))
    # Small bright flame tip puff (kept tight — the plume IS the read).
    if tip_kind == "violet":
        tipcol, tiph = WISP, WISP_H
    elif tip_kind == "gold":
        tipcol, tiph = GOLDFIRE, GOLDFIRE_H
    elif tip_kind == "white":
        tipcol, tiph = (228, 214, 255), (255, 255, 255)
    else:
        tipcol, tiph = col_tip, FUR_H
    pygame.draw.circle(surf, tipcol, (int(tipx), int(tipy)), max(2, width // 3 + 1))
    pygame.draw.circle(surf, tiph, (int(tipx - ax), int(tipy - ay)),
                       max(1, width // 4))
    return (tipx, tipy)


def _wisp(surf, x, y, r, col=WISP, hot=WISP_H):
    """A drifting foxfire ember — baked trail accent."""
    _soft_glow(surf, (int(x), int(y)), r + 2, col, 120)
    pygame.draw.circle(surf, col, (int(x), int(y)), max(1, r // 2))
    pygame.draw.circle(surf, hot, (int(x), int(y)), max(1, r // 3))


# ═════════════════════════════════════════════════════════════════════════════
# v1 · TENKO ASCENDANT — celestial WHITE fur, leaping pose, full nine
#     violet-tipped tails in a wide halo fan, warm gold aura. Regal + cute.
# ═════════════════════════════════════════════════════════════════════════════
def build_kitsune_v1(wing_angle_deg):
    surf = _new()
    g = _flap(wing_angle_deg)               # 1 = gathered (up-pose)
    spread = 1.0 - g                         # 1 = wide fan (down-pose)

    # Baked gold body aura behind everything.
    _soft_glow(surf, (BCX - 4, BCY - 2), 28, AURA, 70)

    # NINE tails fanning out BEHIND the body (to the left/up-and-down). The
    # fan centres on ~165° (back, slightly up) and opens to a wide halo on the
    # spread frame, gathering tighter on the up-pose.
    base = (BCX - 8, BCY)
    fan = 130 + spread * 60                   # total fan arc in degrees
    centre = 165
    n = 9
    for i in range(n):
        t = i / (n - 1)
        ang = centre + (t - 0.5) * fan
        length = 30 + 8 * math.sin(t * math.pi)
        _tail(surf, base, ang, length, 9, FUR_D, FUR, tip_kind="violet",
              curl=0.16 + 0.10 * spread)

    # Foxfire wisps drifting off the fan tips (flicker by frame).
    for i, (wx, wy) in enumerate(((6, BCY - 22), (5, BCY + 14),
                                  (14, BCY - 28))):
        _wisp(surf, wx + spread * 3, wy - g * 4, 4 - i % 2)

    # Leaping fox body (slight forward lean, lower haunch).
    _aaellipse(surf, FUR_D, (BCX + 1, BCY + 2), 15, 13)
    _aaellipse(surf, FUR, (BCX, BCY), 14, 12)
    _aaellipse(surf, FUR_H, (BCX - 3, BCY - 3), 7, 5)
    # Front leg tucked, hind leg extended (leap).
    pygame.draw.line(surf, FUR_D, (BCX + 6, BCY + 10), (BCX + 11, BCY + 16), 3)
    pygame.draw.circle(surf, TIP, (BCX + 11, BCY + 16), 2)
    pygame.draw.line(surf, FUR_D, (BCX - 2, BCY + 11), (BCX - 6, BCY + 16), 3)

    # Head + two pointed ears.
    _aaellipse(surf, FUR_D, (HCX, HCY + 1), 10, 9)
    _aaellipse(surf, FUR, (HCX - 1, HCY), 9, 8)
    for sgn, ex in ((-1, HCX - 5), (1, HCX + 6)):
        pygame.draw.polygon(surf, FUR_D,
                            [(ex - 3, CROWN_Y + 5), (ex + sgn, CROWN_Y - 7),
                             (ex + 4, CROWN_Y + 5)])
        pygame.draw.polygon(surf, TIP,
                            [(ex, CROWN_Y + 2), (ex + sgn, CROWN_Y - 6),
                             (ex + 3, CROWN_Y + 2)])
    # Snout wedge.
    pygame.draw.polygon(surf, FUR,
                        [(HCX + 4, HCY - 1), (HCX + 13, HCY + 2),
                         (HCX + 4, HCY + 5)])
    pygame.draw.circle(surf, NOSE, (HCX + 12, HCY + 2), 2)
    # HERO blaze: a teardrop white flame mark on the forehead, glowing violet.
    _soft_glow(surf, (HCX - 1, HCY - 5), 6, WISP, 150)
    pygame.draw.polygon(surf, BLAZE,
                        [(HCX - 1, CROWN_Y), (HCX - 4, HCY - 3),
                         (HCX + 2, HCY - 3)])
    pygame.draw.circle(surf, BLAZE, (HCX - 1, HCY - 4), 2)
    # Eyes.
    _eye(surf, HCX - 1, HCY, 3)
    return surf


get_kitsune_v1 = _make_prebuilt_skin(build_kitsune_v1)


# ═════════════════════════════════════════════════════════════════════════════
# v2 · KYUBI EMBER — classic RUSSET fox, gold-fire tail tips, aggressive
#     forward leap, dense gold foxfire, a flame-shaped blaze. Fierce.
# ═════════════════════════════════════════════════════════════════════════════
def build_kitsune_v2(wing_angle_deg):
    surf = _new()
    g = _flap(wing_angle_deg)
    spread = 1.0 - g

    # Hot gold aura — denser than v1 for a "wreathed in fire" feel.
    _soft_glow(surf, (BCX - 6, BCY - 2), 30, AURA, 95)
    _soft_glow(surf, (BCX - 8, BCY), 18, GOLDFIRE, 70)

    # Tails stream out behind to the back-left (aggressive forward-pounce),
    # wide fan. Base lifted clear of the body and tails drawn in the LIGHTER
    # russet so the fan separates from the dark russet body mass.
    base = (BCX - 8, BCY - 1)
    fan = 124 + spread * 66
    centre = 168
    n = 9
    for i in range(n):
        t = i / (n - 1)
        ang = centre + (t - 0.5) * fan
        length = 32 + 8 * math.sin(t * math.pi)
        _tail(surf, base, ang, length, 9, RUSSET, RUSSET_H, tip_kind="gold",
              curl=0.20 + 0.12 * spread)

    # Dense gold embers off the fan.
    for i, (wx, wy) in enumerate(((6, BCY - 18), (4, BCY + 14),
                                  (14, BCY - 26), (8, BCY + 4))):
        _wisp(surf, wx + spread * 4, wy - g * 3, 4 - i % 2,
              col=GOLDFIRE, hot=GOLDFIRE_H)

    # Russet body, low aggressive crouch.
    _aaellipse(surf, RUSSET_D, (BCX + 1, BCY + 2), 15, 12)
    _aaellipse(surf, RUSSET, (BCX, BCY), 14, 11)
    _aaellipse(surf, RUSSET_H, (BCX - 3, BCY - 3), 7, 4)
    # Cream belly + chest flash.
    _aaellipse(surf, FUR, (BCX + 1, BCY + 5), 8, 6)
    # Front legs reaching forward (pounce).
    for lx in (BCX + 7, BCX + 4):
        pygame.draw.line(surf, RUSSET_D, (lx, BCY + 8), (lx + 4, BCY + 15), 3)
        pygame.draw.circle(surf, (40, 28, 30), (lx + 4, BCY + 15), 2)

    # Sharp head, swept-back ears.
    _aaellipse(surf, RUSSET_D, (HCX, HCY + 1), 10, 8)
    _aaellipse(surf, RUSSET, (HCX - 1, HCY), 9, 7)
    for sgn, ex in ((-1, HCX - 5), (1, HCX + 6)):
        pygame.draw.polygon(surf, RUSSET_D,
                            [(ex - 3, CROWN_Y + 6), (ex - sgn * 2, CROWN_Y - 6),
                             (ex + 4, CROWN_Y + 5)])
        pygame.draw.polygon(surf, TIP,
                            [(ex, CROWN_Y + 3), (ex - sgn * 2, CROWN_Y - 5),
                             (ex + 3, CROWN_Y + 3)])
    # Long pointed snout.
    pygame.draw.polygon(surf, RUSSET,
                        [(HCX + 4, HCY - 1), (HCX + 15, HCY + 3),
                         (HCX + 4, HCY + 5)])
    pygame.draw.polygon(surf, FUR,
                        [(HCX + 4, HCY + 3), (HCX + 13, HCY + 4),
                         (HCX + 4, HCY + 5)])
    pygame.draw.circle(surf, NOSE, (HCX + 14, HCY + 3), 2)
    # HERO blaze: an upswept gold flame mark on the forehead.
    _soft_glow(surf, (HCX - 1, HCY - 5), 6, GOLDFIRE, 160)
    pygame.draw.polygon(surf, BLAZE,
                        [(HCX - 1, CROWN_Y - 2), (HCX - 4, HCY - 2),
                         (HCX + 1, HCY - 2), (HCX + 3, HCY - 4)])
    # Fierce angled eyes.
    pygame.draw.line(surf, (60, 30, 20), (HCX - 4, HCY - 2), (HCX + 1, HCY - 1), 1)
    _eye(surf, HCX - 1, HCY, 3, iris=(48, 20, 12))
    return surf


get_kitsune_v2 = _make_prebuilt_skin(build_kitsune_v2)


# ═════════════════════════════════════════════════════════════════════════════
# v3 · CURLED ORACLE — curled-regal seated fox, tails sweeping UP as a
#     peacock fan of white-fire, a round moon-disc blaze. Serene shrine-spirit.
# ═════════════════════════════════════════════════════════════════════════════
def build_kitsune_v3(wing_angle_deg):
    surf = _new()
    g = _flap(wing_angle_deg)
    spread = 1.0 - g

    _soft_glow(surf, (BCX - 2, BCY - 2), 28, AURA, 80)

    # Tails sweep UPWARD + back as a tall vertical PEACOCK fan behind the
    # curled body — its distinct silhouette vs the back-swept fans elsewhere.
    base = (BCX - 4, BCY + 4)
    fan = 110 + spread * 40
    centre = 108                              # up + slightly back-left
    n = 9
    for i in range(n):
        t = i / (n - 1)
        ang = centre + (t - 0.5) * fan
        length = 34 + 6 * math.sin(t * math.pi)
        _tail(surf, base, ang, length, 9, FUR_D, FUR, tip_kind="white",
              curl=0.10 + 0.08 * spread)

    # Pale wisps rising between the tails.
    for i, (wx, wy) in enumerate(((BCX - 12, CROWN_Y - 6),
                                  (BCX + 6, CROWN_Y - 4),
                                  (BCX - 2, CROWN_Y - 12))):
        _wisp(surf, wx, wy - g * 3, 3, col=(220, 205, 255), hot=(255, 255, 255))

    # Curled seated body — a rounder, calmer mass with the tail wrapping front.
    _aaellipse(surf, FUR_D, (BCX + 1, BCY + 2), 15, 14)
    _aaellipse(surf, FUR, (BCX, BCY), 14, 13)
    _aaellipse(surf, FUR_H, (BCX - 3, BCY - 2), 8, 6)
    # A single curled tail wrapping over the front paws (curled-regal read).
    pygame.draw.arc(surf, FUR_D, (BCX - 4, BCY + 4, 22, 16),
                    math.radians(200), math.radians(20), 5)
    pygame.draw.circle(surf, (235, 222, 255), (BCX + 16, BCY + 8), 4)
    pygame.draw.circle(surf, (255, 255, 255), (BCX + 16, BCY + 7), 2)
    # Front paws together.
    for px in (BCX + 4, BCX + 9):
        pygame.draw.circle(surf, FUR, (px, BCY + 13), 3)
        pygame.draw.circle(surf, FUR_D, (px, BCY + 13), 3, 1)

    # Calm upright head.
    _aaellipse(surf, FUR_D, (HCX, HCY + 1), 10, 9)
    _aaellipse(surf, FUR, (HCX - 1, HCY), 9, 8)
    for sgn, ex in ((-1, HCX - 5), (1, HCX + 6)):
        pygame.draw.polygon(surf, FUR_D,
                            [(ex - 3, CROWN_Y + 5), (ex, CROWN_Y - 7),
                             (ex + 4, CROWN_Y + 5)])
        pygame.draw.polygon(surf, TIP,
                            [(ex, CROWN_Y + 2), (ex, CROWN_Y - 6),
                             (ex + 3, CROWN_Y + 2)])
    pygame.draw.polygon(surf, FUR,
                        [(HCX + 4, HCY), (HCX + 12, HCY + 2),
                         (HCX + 4, HCY + 5)])
    pygame.draw.circle(surf, NOSE, (HCX + 11, HCY + 2), 2)
    # HERO blaze: a round moon-disc on the forehead, cool-glowing.
    _soft_glow(surf, (HCX - 1, HCY - 4), 6, (200, 180, 255), 150)
    pygame.draw.circle(surf, BLAZE, (HCX - 1, HCY - 4), 3)
    pygame.draw.circle(surf, (210, 190, 255), (HCX - 1, HCY - 4), 3, 1)
    # Gentle closed-content eyes (calm arcs).
    for ex in (HCX - 3, HCX + 3):
        pygame.draw.arc(surf, (70, 50, 70), (ex - 2, HCY - 2, 5, 5),
                        math.radians(200), math.radians(340), 2)
    return surf


get_kitsune_v3 = _make_prebuilt_skin(build_kitsune_v3)


# ═════════════════════════════════════════════════════════════════════════════
# v4 · VIOLET WISP — implied fan (bold 5 read tails + ghost wisps), heavy
#     VIOLET foxfire dominant, white body, comet wisp trails. Spooky-myth.
# ═════════════════════════════════════════════════════════════════════════════
def build_kitsune_v4(wing_angle_deg):
    surf = _new()
    g = _flap(wing_angle_deg)
    spread = 1.0 - g

    # Violet aura sits BEHIND the body so the white fox reads on top of it —
    # the glow halo rings the fan, it doesn't swallow the body.
    _soft_glow(surf, (BCX - 10, BCY - 2), 30, WISP, 80)
    _soft_glow(surf, (BCX - 6, BCY), 16, AURA, 40)

    base = (BCX - 8, BCY)
    fan = 130 + spread * 55
    centre = 168
    # Two GHOST tails (faint, wide, behind) imply the full nine without
    # muddying the foreground read.
    for i in range(2):
        t = i / 1
        ang = centre + (t - 0.5) * (fan + 28)
        ghost = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _tail(ghost, base, ang, 36, 9, (150, 110, 210), (190, 150, 240),
              tip_kind="violet", curl=0.22)
        ghost.set_alpha(110)
        surf.blit(ghost, (0, 0))
    # FIVE bold foreground tails — the read.
    for i in range(5):
        t = i / 4
        ang = centre + (t - 0.5) * fan
        length = 31 + 7 * math.sin(t * math.pi)
        _tail(surf, base, ang, length, 11, FUR_D, FUR, tip_kind="violet",
              curl=0.18 + 0.10 * spread)

    # Comet wisp trails streaking off (motion read).
    for i, (wx, wy) in enumerate(((6, BCY - 22), (4, BCY + 12),
                                  (12, BCY - 28), (3, BCY - 2))):
        _wisp(surf, wx + spread * 5, wy - g * 5, 5 - i % 2)

    # White body.
    _aaellipse(surf, FUR_D, (BCX + 1, BCY + 2), 15, 12)
    _aaellipse(surf, FUR, (BCX, BCY), 14, 11)
    _aaellipse(surf, (240, 235, 255), (BCX - 3, BCY - 2), 7, 5)
    pygame.draw.line(surf, FUR_D, (BCX + 5, BCY + 9), (BCX + 9, BCY + 15), 3)
    pygame.draw.circle(surf, WISP, (BCX + 9, BCY + 15), 2)

    # Head + ears with violet inner.
    _aaellipse(surf, FUR_D, (HCX, HCY + 1), 10, 9)
    _aaellipse(surf, FUR, (HCX - 1, HCY), 9, 8)
    for sgn, ex in ((-1, HCX - 5), (1, HCX + 6)):
        pygame.draw.polygon(surf, FUR_D,
                            [(ex - 3, CROWN_Y + 5), (ex + sgn, CROWN_Y - 7),
                             (ex + 4, CROWN_Y + 5)])
        pygame.draw.polygon(surf, WISP,
                            [(ex, CROWN_Y + 2), (ex + sgn, CROWN_Y - 6),
                             (ex + 3, CROWN_Y + 2)])
    pygame.draw.polygon(surf, FUR,
                        [(HCX + 4, HCY - 1), (HCX + 13, HCY + 2),
                         (HCX + 4, HCY + 5)])
    pygame.draw.circle(surf, NOSE, (HCX + 12, HCY + 2), 2)
    # HERO blaze: a violet diamond flame on the forehead, strongest glow.
    _soft_glow(surf, (HCX - 1, HCY - 5), 7, WISP, 180)
    pygame.draw.polygon(surf, BLAZE,
                        [(HCX - 1, CROWN_Y - 1), (HCX - 4, HCY - 4),
                         (HCX - 1, HCY - 2), (HCX + 2, HCY - 4)])
    pygame.draw.circle(surf, WISP_H, (HCX - 1, HCY - 4), 1)
    # Glowing violet eyes.
    _eye(surf, HCX - 1, HCY, 3, iris=(120, 60, 200), white=(245, 240, 255))
    return surf


get_kitsune_v4 = _make_prebuilt_skin(build_kitsune_v4)


# ═════════════════════════════════════════════════════════════════════════════
# v5 · PRISM TENKO — white body with a gold→violet GRADIENT tail fan (warm
#     inner, cool outer), diamond blaze, balanced spread. Premium jewel look.
# ═════════════════════════════════════════════════════════════════════════════
def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def build_kitsune_v5(wing_angle_deg):
    surf = _new()
    g = _flap(wing_angle_deg)
    spread = 1.0 - g

    # Dual aura: gold inner ring, violet outer ring — the prism signature.
    _soft_glow(surf, (BCX - 6, BCY - 2), 32, WISP, 60)
    _soft_glow(surf, (BCX - 4, BCY), 22, AURA, 85)

    base = (BCX - 8, BCY)
    fan = 130 + spread * 60
    centre = 166
    n = 9
    # Tail tip colour walks gold (centre/inner) → violet (outer), so the fan
    # itself is a warm-to-cool gradient — reads as a prismatic burst at 40px.
    tips = []
    for i in range(n):
        t = i / (n - 1)
        ang = centre + (t - 0.5) * fan
        length = 31 + 7 * math.sin(t * math.pi)
        # distance from fan centre → 0 (gold) at middle, 1 (violet) at edges.
        edge = abs(t - 0.5) * 2
        rootcol = _lerp((236, 220, 200), FUR_D, edge)
        tx, ty = _tail(surf, base, ang, length, 9, rootcol, FUR,
                       tip_kind="none", curl=0.16 + 0.10 * spread)
        tips.append((tx, ty, edge))
    # Re-stamp gradient flame puffs gold→violet on the tips, on top.
    for tx, ty, edge in tips:
        col = _lerp(GOLDFIRE, WISP, edge)
        hot = _lerp(GOLDFIRE_H, WISP_H, edge)
        pygame.draw.circle(surf, col, (int(tx), int(ty)), 3)
        pygame.draw.circle(surf, hot, (int(tx), int(ty)), 2)

    # Two-tone embers (one gold, one violet) for the prism flicker.
    _wisp(surf, 8 + spread * 4, BCY - 20 - g * 4, 4, col=AURA, hot=GOLDFIRE_H)
    _wisp(surf, 5 + spread * 3, BCY + 12 - g * 3, 4)
    _wisp(surf, 14 + spread * 4, BCY - 26, 3, col=AURA, hot=GOLDFIRE_H)

    # White body, leaping but balanced.
    _aaellipse(surf, FUR_D, (BCX + 1, BCY + 2), 15, 13)
    _aaellipse(surf, FUR, (BCX, BCY), 14, 12)
    _aaellipse(surf, FUR_H, (BCX - 3, BCY - 3), 7, 5)
    # Gold-tipped chest tuft.
    _aaellipse(surf, (255, 250, 235), (BCX + 1, BCY + 5), 7, 5)
    pygame.draw.line(surf, FUR_D, (BCX + 6, BCY + 10), (BCX + 10, BCY + 16), 3)
    pygame.draw.circle(surf, AURA, (BCX + 10, BCY + 16), 2)
    pygame.draw.line(surf, FUR_D, (BCX - 1, BCY + 11), (BCX - 5, BCY + 16), 3)

    # Head + ears: gold inner.
    _aaellipse(surf, FUR_D, (HCX, HCY + 1), 10, 9)
    _aaellipse(surf, FUR, (HCX - 1, HCY), 9, 8)
    for sgn, ex in ((-1, HCX - 5), (1, HCX + 6)):
        pygame.draw.polygon(surf, FUR_D,
                            [(ex - 3, CROWN_Y + 5), (ex + sgn, CROWN_Y - 7),
                             (ex + 4, CROWN_Y + 5)])
        pygame.draw.polygon(surf, GOLDFIRE,
                            [(ex, CROWN_Y + 2), (ex + sgn, CROWN_Y - 6),
                             (ex + 3, CROWN_Y + 2)])
        pygame.draw.circle(surf, TIP, (ex + sgn, CROWN_Y - 5), 1)
    pygame.draw.polygon(surf, FUR,
                        [(HCX + 4, HCY - 1), (HCX + 13, HCY + 2),
                         (HCX + 4, HCY + 5)])
    pygame.draw.circle(surf, NOSE, (HCX + 12, HCY + 2), 2)
    # HERO blaze: a faceted diamond, gold core + violet glow ring.
    _soft_glow(surf, (HCX - 1, HCY - 5), 6, WISP, 130)
    _soft_glow(surf, (HCX - 1, HCY - 5), 4, AURA, 150)
    pygame.draw.polygon(surf, BLAZE,
                        [(HCX - 1, CROWN_Y - 1), (HCX - 4, HCY - 4),
                         (HCX - 1, HCY - 1), (HCX + 2, HCY - 4)])
    pygame.draw.circle(surf, GOLDFIRE_H, (HCX - 1, HCY - 4), 1)
    _eye(surf, HCX - 1, HCY, 3, iris=(60, 36, 70))
    return surf


get_kitsune_v5 = _make_prebuilt_skin(build_kitsune_v5)


# ─────────────────────────────────────────────────────────────────────────────
# Label → getter registry for the review sheet.
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "v1 TENKO ASCENDANT": get_kitsune_v1,
    "v2 KYUBI EMBER":     get_kitsune_v2,
    "v3 CURLED ORACLE":   get_kitsune_v3,
    "v4 VIOLET WISP":     get_kitsune_v4,
    "v5 PRISM TENKO":     get_kitsune_v5,
}
