"""Candidate SUGAR GLIDER skins for the ANIMALS Store — round-1 exploration.

A sugar glider is a mammal that GLIDES, not a bird that flaps: a stretchy
patagium membrane runs wrist-to-ankle on each side, so when the limbs spread
the whole animal becomes a flat kite. That kite silhouette is brand-new to the
creature set (every other skin is a winged/round body) and is the whole reason
this concept earns its slot.

The four base wing poses are reinterpreted as a GLIDE cycle, not a flap:
  * down-pose (50°)  → membrane TAUT and wide, limbs spread (full glide)
  * up-pose  (-40°)  → limbs tuck in, membrane slack (mid-leap, narrower kite)
so the silhouette breathes between a wide diamond and a tighter dart.

Signature 40px tell: the dark dorsal stripe slicing down a pale stretched
membrane + two huge round night-eyes with a dark face-mask. This must pop on
bright-day skies too, so every version keeps a hard pale/dark contrast and an
outline-friendly bold shape rather than relying on the dim night palette.

Contract (mirrors game/animal_skins.py so the winner lifts straight in):
  * `build_<name>(wing_angle_deg) -> pygame.Surface`  draws one flat frame on a
    64×84 SRCALPHA canvas; body mass centred at (32,44), head near (44,34).
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_sugar_glider": ...}` registry at the bottom (one winner
    is chosen later; here every variant is registered for the review sheet).
"""
import math
import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (mirrors animal_skins) ─────────────────────────────
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
    """0..1 'limbs up / tucked' factor across the 50→-40 pose run. For the
    glider, 0 = full spread glide (down-pose), 1 = tucked mid-leap (up-pose)."""
    return (angle_deg + 40) / 90.0


def _night_eye(surf, cx, cy, r, *, pupil=(20, 21, 26), mask=(40, 42, 50)):
    """A big round nocturnal eye: dark mask ring, near-black pupil, bright
    top-left catch-light. The catch-light is the thing that survives 40px."""
    pygame.draw.circle(surf, mask, (cx, cy), r + 1)
    pygame.draw.circle(surf, (252, 250, 246), (cx, cy), r)
    pygame.draw.circle(surf, pupil, (cx, cy), max(2, r - 1))
    pygame.draw.circle(surf, (255, 255, 255), (cx - r // 2, cy - r // 2),
                       max(1, r // 3))


# ═════════════════════════════════════════════════════════════════════════════
# V1 · CLASSIC GREY KITE — the textbook wild sugar glider. A broad SQUARE
#   patagium kite, soft bluish-grey fur, a single bold near-black dorsal stripe
#   nose-to-tail, cream belly, big round eyes with a dark mask. The honest,
#   most "readable as a glider" baseline.
# ═════════════════════════════════════════════════════════════════════════════
_V1_FUR   = (201, 205, 214)
_V1_FUR_D = (160, 165, 178)
_V1_FUR_H = (231, 234, 240)
_V1_MEMB  = (185, 190, 201)
_V1_MEMB_D = (150, 156, 170)
_V1_STRIPE = (62, 66, 78)
_V1_STRIPE_D = (38, 41, 50)
_V1_BELLY = (255, 247, 230)
_V1_MASK  = (40, 43, 52)
_V1_EAR   = (176, 156, 156)


def build_sugar_glider_v1(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    # Membrane width breathes: widest on the glide (down) pose, tucked on up.
    spread = int(26 - f * 8)
    droop = int(f * 4)               # limbs/membrane drop as they tuck

    # Long balance tail trailing behind (left).
    tail_sweep = int(6 - f * 4)
    pygame.draw.lines(surf, _V1_FUR_D, False,
                      [(BCX - 14, BCY + 2), (12, BCY - 2 - tail_sweep),
                       (4, BCY + 4)], 5)
    pygame.draw.lines(surf, _V1_STRIPE, False,
                      [(BCX - 14, BCY + 1), (12, BCY - 3 - tail_sweep),
                       (5, BCY + 3)], 2)

    # ── HERO kite: the stretched square patagium, corner to corner. Drawn as
    #    one broad pale diamond BEHIND the body so the body+stripe ride on top.
    kite = [(BCX - spread, BCY - 6 + droop),         # back-left wrist
            (BCX + spread - 2, BCY - 10 + droop),    # front-left wrist
            (BCX + spread - 6, BCY + 14 - droop),    # front-right ankle
            (BCX - spread + 4, BCY + 16 - droop)]    # back-right ankle
    pygame.draw.polygon(surf, _V1_MEMB_D, kite)
    inner = [(BCX - spread + 3, BCY - 4 + droop),
             (BCX + spread - 5, BCY - 7 + droop),
             (BCX + spread - 9, BCY + 11 - droop),
             (BCX - spread + 7, BCY + 12 - droop)]
    pygame.draw.polygon(surf, _V1_MEMB, inner)

    # Body riding centred on the kite.
    _aaellipse(surf, _V1_FUR_D, (BCX + 1, BCY + 1), 12, 13)
    _aaellipse(surf, _V1_FUR, (BCX, BCY), 11, 12)
    _aaellipse(surf, _V1_BELLY, (BCX - 1, BCY + 4), 7, 8)

    # ── HERO stripe: nose-to-tail dark dorsal line down the centre.
    pygame.draw.line(surf, _V1_STRIPE_D, (BCX - 11, BCY - 1), (HCX + 6, HCY), 4)
    pygame.draw.line(surf, _V1_STRIPE, (BCX - 11, BCY - 2), (HCX + 6, HCY - 1), 2)

    # Head.
    _aaellipse(surf, _V1_FUR_D, (HCX, HCY + 1), 9, 9)
    _aaellipse(surf, _V1_FUR, (HCX - 1, HCY), 8, 8)
    # Two rounded ears.
    for sgn, ex in ((-1, HCX - 5), (1, HCX + 5)):
        pygame.draw.circle(surf, _V1_FUR_D, (ex, CROWN_Y + 2), 4)
        pygame.draw.circle(surf, _V1_EAR, (ex, CROWN_Y + 3), 2)
    # Dark face-mask bands running back from each eye.
    pygame.draw.line(surf, _V1_MASK, (HCX - 4, HCY - 2), (HCX + 8, HCY - 3), 3)
    # Huge night eyes.
    _night_eye(surf, HCX - 2, HCY, 4)
    _night_eye(surf, HCX + 5, HCY, 4)
    # Tiny pink nose.
    pygame.draw.circle(surf, (210, 150, 150), (HCX + 9, HCY + 3), 2)
    return surf


get_sugar_glider_v1 = _make_prebuilt_skin(build_sugar_glider_v1)


# ═════════════════════════════════════════════════════════════════════════════
# V2 · CARAMEL ROUNDED-WING — a warmer caramel/tan morph with a ROUNDED,
#   leaf-shaped patagium (smooth aerofoil edge, not a hard square) and a softer
#   rust-brown dorsal stripe. Reads as a cuddlier, organic glider. Eyes very
#   large, mask softened to chocolate.
# ═════════════════════════════════════════════════════════════════════════════
_V2_FUR   = (214, 178, 132)
_V2_FUR_D = (180, 140, 96)
_V2_FUR_H = (238, 212, 174)
_V2_MEMB  = (204, 166, 120)
_V2_MEMB_D = (172, 132, 88)
_V2_STRIPE = (120, 78, 50)
_V2_STRIPE_D = (86, 52, 32)
_V2_BELLY = (255, 244, 214)
_V2_MASK  = (78, 52, 38)


def _v2_lobe(surf, col, cx, cy, rx, ry):
    """One smooth membrane lobe — a soft ellipse for the rounded aerofoil."""
    _aaellipse(surf, col, (cx, cy), rx, ry)


def build_sugar_glider_v2(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    rx = int(24 - f * 7)
    dy = int(f * 3)

    # Curled balance tail.
    pygame.draw.lines(surf, _V2_FUR_D, False,
                      [(BCX - 12, BCY + 3), (10, BCY + 1), (3, BCY + 8),
                       (8, BCY + 12)], 5)
    pygame.draw.lines(surf, _V2_STRIPE, False,
                      [(BCX - 12, BCY + 2), (10, BCY), (4, BCY + 7)], 2)

    # ── HERO: rounded leaf membrane — two soft lobes top + bottom of the body.
    _v2_lobe(surf, _V2_MEMB_D, BCX, BCY - 6 + dy, rx, 9)
    _v2_lobe(surf, _V2_MEMB_D, BCX, BCY + 8 - dy, rx - 2, 8)
    _v2_lobe(surf, _V2_MEMB, BCX, BCY - 5 + dy, rx - 3, 6)
    _v2_lobe(surf, _V2_MEMB, BCX, BCY + 7 - dy, rx - 5, 6)

    # Body.
    _aaellipse(surf, _V2_FUR_D, (BCX + 1, BCY + 1), 12, 13)
    _aaellipse(surf, _V2_FUR, (BCX, BCY), 11, 12)
    _aaellipse(surf, _V2_FUR_H, (BCX - 3, BCY - 4), 5, 4)
    _aaellipse(surf, _V2_BELLY, (BCX - 1, BCY + 4), 7, 8)

    # Soft rust dorsal stripe.
    pygame.draw.line(surf, _V2_STRIPE_D, (BCX - 11, BCY), (HCX + 5, HCY), 4)
    pygame.draw.line(surf, _V2_STRIPE, (BCX - 11, BCY - 1), (HCX + 5, HCY - 1), 2)

    # Head.
    _aaellipse(surf, _V2_FUR_D, (HCX, HCY + 1), 9, 9)
    _aaellipse(surf, _V2_FUR, (HCX - 1, HCY), 8, 8)
    for sgn, ex in ((-1, HCX - 5), (1, HCX + 5)):
        pygame.draw.circle(surf, _V2_FUR_D, (ex, CROWN_Y + 2), 4)
        pygame.draw.circle(surf, (220, 178, 170), (ex, CROWN_Y + 3), 2)
    pygame.draw.line(surf, _V2_MASK, (HCX - 4, HCY - 2), (HCX + 8, HCY - 3), 3)
    # Extra-large eyes (the cuddly tell).
    _night_eye(surf, HCX - 2, HCY, 5, pupil=(28, 20, 16), mask=(78, 52, 38))
    _night_eye(surf, HCX + 6, HCY, 5, pupil=(28, 20, 16), mask=(78, 52, 38))
    pygame.draw.circle(surf, (200, 140, 130), (HCX + 10, HCY + 4), 2)
    return surf


get_sugar_glider_v2 = _make_prebuilt_skin(build_sugar_glider_v2)


# ═════════════════════════════════════════════════════════════════════════════
# V3 · WHITE-FACED BOLD-STRIPE — a high-contrast leucistic morph: cool
#   white-grey fur, a WHITE face, and a THICK jet-black dorsal stripe that
#   forks across the brow into a dramatic mask (the boldest 40px stripe of the
#   set). A long whip tail. Built for maximum silhouette punch on day skies.
# ═════════════════════════════════════════════════════════════════════════════
_V3_FUR   = (224, 228, 236)
_V3_FUR_D = (182, 188, 200)
_V3_MEMB  = (208, 213, 224)
_V3_MEMB_D = (170, 176, 190)
_V3_STRIPE = (24, 25, 30)
_V3_FACE  = (252, 252, 250)
_V3_BELLY = (255, 255, 252)
_V3_EAR   = (60, 62, 70)


def build_sugar_glider_v3(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    spread = int(27 - f * 9)
    droop = int(f * 4)

    # Long whip tail with a dark tip.
    tail_sweep = int(8 - f * 5)
    pygame.draw.lines(surf, _V3_FUR_D, False,
                      [(BCX - 13, BCY + 1), (12, BCY - 4 - tail_sweep),
                       (2, BCY - 1 - tail_sweep)], 4)
    pygame.draw.circle(surf, _V3_STRIPE, (2, BCY - 1 - tail_sweep), 3)

    # ── HERO kite — sharp square patagium for crisp diamond silhouette.
    kite = [(BCX - spread, BCY - 7 + droop),
            (BCX + spread, BCY - 11 + droop),
            (BCX + spread - 5, BCY + 15 - droop),
            (BCX - spread + 4, BCY + 17 - droop)]
    pygame.draw.polygon(surf, _V3_MEMB_D, kite)
    pygame.draw.polygon(surf, _V3_MEMB,
                        [(BCX - spread + 3, BCY - 5 + droop),
                         (BCX + spread - 4, BCY - 8 + droop),
                         (BCX + spread - 9, BCY + 11 - droop),
                         (BCX - spread + 8, BCY + 12 - droop)])

    # Body.
    _aaellipse(surf, _V3_FUR_D, (BCX + 1, BCY + 1), 12, 13)
    _aaellipse(surf, _V3_FUR, (BCX, BCY), 11, 12)
    _aaellipse(surf, _V3_BELLY, (BCX - 1, BCY + 4), 7, 8)

    # ── HERO: a THICK jet-black dorsal stripe (the boldest of the set).
    pygame.draw.line(surf, _V3_STRIPE, (BCX - 12, BCY - 1), (HCX + 3, HCY - 2), 5)

    # Head with a white face.
    _aaellipse(surf, _V3_FUR_D, (HCX, HCY + 1), 9, 9)
    _aaellipse(surf, _V3_FACE, (HCX - 1, HCY), 8, 8)
    for sgn, ex in ((-1, HCX - 5), (1, HCX + 5)):
        pygame.draw.circle(surf, _V3_EAR, (ex, CROWN_Y + 2), 4)
        pygame.draw.circle(surf, (200, 200, 210), (ex, CROWN_Y + 3), 2)
    # The stripe FORKS over the brow into a dramatic dark mask.
    pygame.draw.polygon(surf, _V3_STRIPE,
                        [(HCX + 3, HCY - 3), (HCX - 7, HCY - 4),
                         (HCX - 7, HCY - 1), (HCX + 3, HCY - 1)])
    pygame.draw.line(surf, _V3_STRIPE, (HCX - 1, HCY - 3), (HCX - 1, HCY + 4), 2)
    # Huge eyes on the white face — maximum contrast.
    _night_eye(surf, HCX - 3, HCY + 1, 4, mask=(24, 25, 30))
    _night_eye(surf, HCX + 4, HCY + 1, 4, mask=(24, 25, 30))
    pygame.draw.circle(surf, (40, 40, 46), (HCX + 8, HCY + 4), 2)
    return surf


get_sugar_glider_v3 = _make_prebuilt_skin(build_sugar_glider_v3)


# ═════════════════════════════════════════════════════════════════════════════
# V4 · TWILIGHT FLYING-SQUIRREL — a deep slate/charcoal night morph with a
#   subtle violet sheen and a pale glowing belly: the patagium is the BODY
#   colour (so the SHAPE, not a colour break, carries it) and the hero contrast
#   is the cream belly + two oversized glowing eyes. Membrane corners caught by
#   bright fur highlights. The most "nocturnal" version.
# ═════════════════════════════════════════════════════════════════════════════
_V4_FUR   = (96, 100, 122)
_V4_FUR_D = (66, 70, 92)
_V4_FUR_H = (140, 144, 172)
_V4_MEMB  = (84, 88, 112)
_V4_MEMB_D = (58, 62, 84)
_V4_STRIPE = (30, 32, 44)
_V4_BELLY = (236, 238, 220)
_V4_GLOW  = (190, 230, 210)


def build_sugar_glider_v4(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    spread = int(26 - f * 8)
    droop = int(f * 4)

    # Plume tail.
    pygame.draw.lines(surf, _V4_FUR_D, False,
                      [(BCX - 13, BCY + 2), (11, BCY - 2), (3, BCY + 3)], 6)
    pygame.draw.lines(surf, _V4_FUR_H, False,
                      [(BCX - 13, BCY + 1), (11, BCY - 3), (4, BCY + 2)], 2)

    # ── HERO via SHAPE: a wide kite in body colour; corners caught by light.
    kite = [(BCX - spread, BCY - 6 + droop),
            (BCX + spread - 2, BCY - 10 + droop),
            (BCX + spread - 6, BCY + 14 - droop),
            (BCX - spread + 4, BCY + 16 - droop)]
    pygame.draw.polygon(surf, _V4_MEMB_D, kite)
    pygame.draw.polygon(surf, _V4_MEMB,
                        [(BCX - spread + 3, BCY - 4 + droop),
                         (BCX + spread - 5, BCY - 7 + droop),
                         (BCX + spread - 9, BCY + 11 - droop),
                         (BCX - spread + 7, BCY + 12 - droop)])
    # Bright highlight catching the leading membrane edge so the kite SHAPE
    # still reads when colour can't carry it on a dark sky.
    pygame.draw.line(surf, _V4_FUR_H,
                     (BCX - spread + 3, BCY - 4 + droop),
                     (BCX + spread - 5, BCY - 7 + droop), 2)

    # Body.
    _aaellipse(surf, _V4_FUR_D, (BCX + 1, BCY + 1), 12, 13)
    _aaellipse(surf, _V4_FUR, (BCX, BCY), 11, 12)
    # Glowing pale belly — the colour contrast hero.
    _aaellipse(surf, _V4_BELLY, (BCX - 1, BCY + 4), 8, 9)

    # Dark dorsal stripe (subtle on this dark fur, carried by the belly split).
    pygame.draw.line(surf, _V4_STRIPE, (BCX - 11, BCY - 1), (HCX + 5, HCY - 1), 4)

    # Head.
    _aaellipse(surf, _V4_FUR_D, (HCX, HCY + 1), 9, 9)
    _aaellipse(surf, _V4_FUR, (HCX - 1, HCY), 8, 8)
    for sgn, ex in ((-1, HCX - 5), (1, HCX + 5)):
        pygame.draw.circle(surf, _V4_FUR_D, (ex, CROWN_Y + 2), 4)
        pygame.draw.circle(surf, (150, 150, 175), (ex, CROWN_Y + 3), 2)
    # Two oversized glowing eyes (the night tell), faint mint rim.
    _night_eye(surf, HCX - 2, HCY, 5, mask=(30, 32, 44))
    _night_eye(surf, HCX + 6, HCY, 5, mask=(30, 32, 44))
    for ex in (HCX - 2, HCX + 6):
        pygame.draw.circle(surf, _V4_GLOW, (ex, HCY), 6, 1)
    return surf


get_sugar_glider_v4 = _make_prebuilt_skin(build_sugar_glider_v4)


# ═════════════════════════════════════════════════════════════════════════════
# V5 · SCALLOPED-EDGE SHOWPIECE — a stylised pose-forward glider: the patagium
#   has a SCALLOPED trailing edge (little finger-strut scoops, flying-squirrel
#   style) and a contrasting dark MEMBRANE RIM so the kite outline is razor
#   sharp even against bright cloud. Warm grey-pink fur, bold stripe, big eyes.
#   The most graphically deliberate / "designed" of the five.
# ═════════════════════════════════════════════════════════════════════════════
_V5_FUR   = (208, 200, 206)
_V5_FUR_D = (170, 160, 170)
_V5_FUR_H = (236, 230, 234)
_V5_MEMB  = (192, 182, 192)
_V5_MEMB_D = (150, 140, 152)
_V5_RIM   = (70, 64, 76)
_V5_STRIPE = (52, 48, 60)
_V5_STRIPE_D = (32, 30, 40)
_V5_BELLY = (255, 246, 240)
_V5_EAR   = (190, 160, 170)


def build_sugar_glider_v5(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    spread = int(27 - f * 9)
    droop = int(f * 4)

    # Tail with a tidy dark tip.
    pygame.draw.lines(surf, _V5_FUR_D, False,
                      [(BCX - 13, BCY + 1), (11, BCY - 3), (3, BCY + 2)], 5)
    pygame.draw.line(surf, _V5_STRIPE, (BCX - 13, BCY), (11, BCY - 4), 2)
    pygame.draw.circle(surf, _V5_STRIPE_D, (3, BCY + 2), 2)

    # ── HERO: scalloped-edge kite. Build the membrane as a fan of points where
    #    the trailing (lower) edge dips into little finger-strut scoops.
    top = [(BCX - spread, BCY - 7 + droop),
           (BCX + spread, BCY - 11 + droop)]
    # Scalloped bottom edge: alternating out/in points front→back.
    bot = []
    n = 5
    for i in range(n + 1):
        t = i / n
        x = int((BCX + spread - 4) * (1 - t) + (BCX - spread + 4) * t)
        base_y = int((BCY + 14 - droop) * (1 - t) + (BCY + 16 - droop) * t)
        scoop = 3 if i % 2 == 0 else -2     # in/out scallop
        bot.append((x, base_y - scoop))
    kite = top + bot
    pygame.draw.polygon(surf, _V5_RIM, kite)
    # Inner membrane inset from the rim so the dark rim frames the kite.
    inner_top = [(BCX - spread + 3, BCY - 5 + droop),
                 (BCX + spread - 3, BCY - 8 + droop)]
    inner_bot = []
    for i in range(n + 1):
        t = i / n
        x = int((BCX + spread - 7) * (1 - t) + (BCX - spread + 7) * t)
        base_y = int((BCY + 11 - droop) * (1 - t) + (BCY + 13 - droop) * t)
        scoop = 2 if i % 2 == 0 else -1
        inner_bot.append((x, base_y - scoop))
    pygame.draw.polygon(surf, _V5_MEMB_D, inner_top + inner_bot)
    pygame.draw.polygon(surf, _V5_MEMB,
                        [(BCX - spread + 6, BCY - 3 + droop),
                         (BCX + spread - 6, BCY - 5 + droop),
                         (BCX + spread - 10, BCY + 8 - droop),
                         (BCX - spread + 10, BCY + 9 - droop)])

    # Body.
    _aaellipse(surf, _V5_FUR_D, (BCX + 1, BCY + 1), 12, 13)
    _aaellipse(surf, _V5_FUR, (BCX, BCY), 11, 12)
    _aaellipse(surf, _V5_FUR_H, (BCX - 3, BCY - 4), 5, 4)
    _aaellipse(surf, _V5_BELLY, (BCX - 1, BCY + 4), 7, 8)

    # Bold dorsal stripe.
    pygame.draw.line(surf, _V5_STRIPE_D, (BCX - 11, BCY - 1), (HCX + 5, HCY), 4)
    pygame.draw.line(surf, _V5_STRIPE, (BCX - 11, BCY - 2), (HCX + 5, HCY - 1), 2)

    # Head.
    _aaellipse(surf, _V5_FUR_D, (HCX, HCY + 1), 9, 9)
    _aaellipse(surf, _V5_FUR, (HCX - 1, HCY), 8, 8)
    for sgn, ex in ((-1, HCX - 5), (1, HCX + 5)):
        pygame.draw.circle(surf, _V5_FUR_D, (ex, CROWN_Y + 2), 4)
        pygame.draw.circle(surf, _V5_EAR, (ex, CROWN_Y + 3), 2)
    pygame.draw.line(surf, _V5_RIM, (HCX - 4, HCY - 2), (HCX + 8, HCY - 3), 3)
    _night_eye(surf, HCX - 2, HCY, 4, mask=(52, 48, 60))
    _night_eye(surf, HCX + 5, HCY, 4, mask=(52, 48, 60))
    pygame.draw.circle(surf, (208, 150, 158), (HCX + 9, HCY + 3), 2)
    return surf


get_sugar_glider_v5 = _make_prebuilt_skin(build_sugar_glider_v5)


# ─────────────────────────────────────────────────────────────────────────────
# Review registry — every variant under its production-style key so the sheet
# can iterate them. The chosen winner ships as the single "skin_sugar_glider".
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "skin_sugar_glider_v1": get_sugar_glider_v1,
    "skin_sugar_glider_v2": get_sugar_glider_v2,
    "skin_sugar_glider_v3": get_sugar_glider_v3,
    "skin_sugar_glider_v4": get_sugar_glider_v4,
    "skin_sugar_glider_v5": get_sugar_glider_v5,
}
