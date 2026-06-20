"""Production SUGAR GLIDER skin — round-2 convergence on V4 TWILIGHT.

A sugar glider is a mammal that GLIDES, not a bird that flaps: a stretchy
patagium membrane runs wrist-to-ankle on each side, so when the limbs spread
the whole animal becomes a flat kite. That flat-kite silhouette is brand-new to
the creature set (every other skin is a winged/round body) and is the whole
reason this concept earns its slot.

Round-2 is a single converged build (winner = V4 twilight flying-squirrel),
folding in the art-director punch list:
  * a continuous dark dorsal SPINE stripe nose-to-tail, one value step darker
    than the slate fur, that survives the 40px read as one line (not a bar);
  * a dark membrane RIM / leading-edge outline (ported from V5) so the kite
    stays razor-crisp on bright AND pale-cloud day skies;
  * two clean, distinct round night-eyes (tight mint rim + one specular each)
    held apart by a dark gap so they don't fuse;
  * an exaggerated glide cycle — taut wide kite on the down pose, tucked dart
    on the up pose — so the silhouette delta is unmistakable;
  * SQUARE kite corners (borrowed from V1) so the membrane reads as a flat
    stretched glider, not a soft blob;
  * a glowing belly that is capped to lit fur, not a neon orb.

The flat kite + round ears + huge eyes deliberately reads distinct from the
existing bat's pointed-wing / pointy-ear silhouette.

Contract (mirrors game/animal_skins.py so the winner lifts straight in):
  * `build_sugar_glider(wing_angle_deg) -> pygame.Surface` draws one flat frame
    on a 64×84 SRCALPHA canvas; body mass centred at (32,44), head near (44,34).
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_sugar_glider": get_sugar_glider}` registry (liftable).
"""
import pygame

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
    """0..1 'limbs tucked' factor across the 50→-40 pose run. For the glider,
    0 = full spread glide (down-pose), 1 = tucked mid-leap dart (up-pose)."""
    return (angle_deg + 40) / 90.0


# ═════════════════════════════════════════════════════════════════════════════
# TWILIGHT FLYING-SQUIRREL — deep slate/charcoal night morph with a subtle
#   violet-cool sheen. The patagium is the BODY colour so the SHAPE carries the
#   kite; a dark RIM frames it crisply on any sky, the pale belly + glowing eyes
#   + dorsal spine carry the read.
# ═════════════════════════════════════════════════════════════════════════════
_FUR     = (96, 100, 122)
_FUR_D   = (66, 70, 92)
_FUR_H   = (140, 144, 172)
_MEMB    = (84, 88, 112)
_MEMB_D  = (58, 62, 84)
_RIM     = (34, 36, 50)          # dark membrane rim — the day-pop edge
_SPINE   = (52, 55, 74)          # one value step darker than the slate fur
_SPINE_D = (38, 40, 56)          # core of the spine line for 40px survival
_BELLY   = (228, 230, 212)       # warm cream, NOT pure white (capped glow)
_BELLY_H = (238, 240, 224)
_GLOW    = (176, 222, 200)       # mint eye-rim


def _night_eye(surf, cx, cy, r):
    """A big round nocturnal eye: dark mask ring, near-black pupil, one bright
    top-left catch-light, and a tight mint rim. The catch-light + the mint rim
    are the two things that survive 40px and keep the eyes reading as 'glowing'
    without blooming into a neon orb."""
    pygame.draw.circle(surf, (30, 32, 44), (cx, cy), r + 1)
    pygame.draw.circle(surf, (250, 248, 244), (cx, cy), r)
    pygame.draw.circle(surf, (20, 21, 26), (cx, cy), max(2, r - 1))
    pygame.draw.circle(surf, (255, 255, 255), (cx - r // 2, cy - r // 2),
                       max(1, r // 3))
    pygame.draw.circle(surf, _GLOW, (cx, cy), r + 1, 1)


def build_sugar_glider(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)

    # Exaggerated glide cycle: wide+flat taut kite on the spread (down) pose,
    # a markedly narrower tucked dart on the up pose so the silhouette delta is
    # unmistakable in motion. The spread swing is large on purpose.
    spread = int(27 - f * 13)        # 27 → 14 px half-span
    droop = int(f * 6)               # limbs/membrane drop + steepen as they tuck
    flat = int((1 - f) * 3)          # taut kite sits flatter when fully spread

    # Plume tail trailing behind (left), with a bright spine highlight.
    pygame.draw.lines(surf, _FUR_D, False,
                      [(BCX - 13, BCY + 2), (11, BCY - 2), (3, BCY + 3)], 6)
    pygame.draw.lines(surf, _FUR_H, False,
                      [(BCX - 13, BCY + 1), (11, BCY - 3), (4, BCY + 2)], 2)

    # ── HERO kite: a SQUARE-cornered patagium in body colour, framed by a dark
    #    rim so the flat-glider silhouette stays crisp on bright + pale skies.
    #    Corners are kept near-right-angled (borrowed from V1) rather than
    #    diamond-soft so it reads as a stretched flat membrane.
    kite = [(BCX - spread,     BCY - 7 - flat + droop),    # back-top  (square)
            (BCX + spread,     BCY - 9 - flat + droop),    # front-top (square)
            (BCX + spread - 2, BCY + 15 + flat - droop),   # front-bot
            (BCX - spread + 2, BCY + 16 + flat - droop)]   # back-bot
    pygame.draw.polygon(surf, _RIM, kite)
    # Inner membrane inset from the rim so the rim frames the kite (~+25% edge).
    inner = [(BCX - spread + 2, BCY - 5 - flat + droop),
             (BCX + spread - 2, BCY - 7 - flat + droop),
             (BCX + spread - 4, BCY + 13 + flat - droop),
             (BCX - spread + 4, BCY + 14 + flat - droop)]
    pygame.draw.polygon(surf, _MEMB_D, inner)
    pygame.draw.polygon(surf, _MEMB,
                        [(BCX - spread + 4, BCY - 3 - flat + droop),
                         (BCX + spread - 4, BCY - 5 - flat + droop),
                         (BCX + spread - 6, BCY + 11 + flat - droop),
                         (BCX - spread + 6, BCY + 12 + flat - droop)])
    # Bright highlight catching the leading (top) membrane edge so the kite
    # SHAPE still reads when colour can't carry it on a dark night sky.
    pygame.draw.line(surf, _FUR_H,
                     (BCX - spread + 2, BCY - 5 - flat + droop),
                     (BCX + spread - 2, BCY - 7 - flat + droop), 2)

    # Body.
    _aaellipse(surf, _FUR_D, (BCX + 1, BCY + 1), 12, 13)
    _aaellipse(surf, _FUR, (BCX, BCY), 11, 12)
    # Capped glowing belly: warm cream lit fur (not pure white), kept smaller
    # than the body so it reads as a lit chest patch, not a neon orb. A small
    # off-centre top highlight gives the lift without blooming.
    _aaellipse(surf, _BELLY, (BCX - 2, BCY + 4), 6, 7)
    _aaellipse(surf, _BELLY_H, (BCX - 3, BCY + 1), 3, 3)

    # ── HERO spine: a single continuous dorsal stripe nose-to-tail down the
    #    centreline ON the dark body — one value step darker than the fur, with
    #    a darker core so the line survives the 40px downscale as ONE stroke.
    #    Runs from the tail root, OVER the body, up onto the brow so it reads as
    #    one unbroken line rather than a short belly bar.
    pygame.draw.line(surf, _SPINE, (BCX - 13, BCY - 3), (HCX + 1, HCY - 5), 5)
    pygame.draw.line(surf, _SPINE_D, (BCX - 13, BCY - 3), (HCX + 1, HCY - 5), 2)

    # Head.
    _aaellipse(surf, _FUR_D, (HCX, HCY + 1), 9, 9)
    _aaellipse(surf, _FUR, (HCX - 1, HCY), 8, 8)
    # Round ears (the bat-differentiator — soft circles, not pointed tufts).
    for ex in (HCX - 5, HCX + 5):
        pygame.draw.circle(surf, _FUR_D, (ex, CROWN_Y + 2), 4)
        pygame.draw.circle(surf, (150, 150, 175), (ex, CROWN_Y + 3), 2)

    # Two oversized glowing night-eyes, resolved as clean DISTINCT rounds with a
    # ~1px dark gap so they don't fuse into one blob at small scale.
    _night_eye(surf, HCX - 2, HCY, 4)
    _night_eye(surf, HCX + 6, HCY, 4)
    pygame.draw.line(surf, (24, 26, 38), (HCX + 2, HCY - 3), (HCX + 2, HCY + 3), 1)

    # Tiny dark nose to finish the muzzle.
    pygame.draw.circle(surf, (40, 42, 54), (HCX + 9, HCY + 3), 2)
    return surf


get_sugar_glider = _make_prebuilt_skin(build_sugar_glider)


# ─────────────────────────────────────────────────────────────────────────────
# Production registry — the single converged build ships as "skin_sugar_glider".
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "skin_sugar_glider": get_sugar_glider,
}
