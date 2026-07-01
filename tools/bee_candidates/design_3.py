"""IRONHORN — Rhinoceros/Hercules beetle candidate for `skin_bee` (scratch).

An armored bruiser built as MASS + one dominant appendage, the opposite read
of a winged flutter. The tell that survives the 40px downscale is the cephalic
HORN: a broad-based blade sweeping up-left and forking into a Y-split at the
tip, poking well above the crown so the silhouette says "rhino beetle" even as
a solid shadow. Nothing else breaks the top line — antennae are short and
tucked below it so the horn owns the read.

The body is ONE broad domed elytra oval — the largest dark-bronze mass on the
sprite — carrying a crisp gold specular streak and a dark lower-right rim so it
reads as lacquered chitin, not a soft blob, on either sky. The flap is
characterful, not a flutter: the elytra suture cracks open down the midline and
two amber hindwings fan out from behind the shell crown (strike factor s=1),
sealing shut on the up-stroke (s=0) — a heavy beetle labouring into the air.

Exploration only — NOT registered in any live BUILDERS map; production art is
untouched.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44          # thorax/elytra centre — the dome owns the middle
HCX, HCY = 44, 34          # head, set upper-right on the insect body axis
CROWN_Y = 24               # the top line; only the horn may cross it

# Dynastine chitin palette — three clearly separated values so day sky never
# flattens it to a brown blob: a near-black chitin frame, a red-bronze body,
# and a bright clean gold for the specular / horn rim.
CHITIN = (22, 16, 8)       # #16100 8 dark chitin — horn / head / legs / outline
SHELL  = (92, 60, 22)      # #5C3C16 red-bronze elytra shell (olive cast killed)
BRASS  = (168, 122, 52)    # warm bronze mid-band + leg/abdomen rim-light
GOLD   = (236, 200, 96)    # #ECC860 clean gold specular streak / horn rim
AMBER  = (208, 140, 58)    # amber membranous hindwing / suture crack
EYE_G  = (40, 90, 20)      # dark-green compound eye
WHITE  = (244, 240, 226)   # catchlight / specular hotspot / horn-tip glint


def _new(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def _flap(a):
    # 0 at the deepest down-stroke (angle -40), 1 at the top up-stroke (50).
    return (a + 40) / 90.0


def _hindwing(surf, side, o):
    """One amber hindwing fanning out from behind the elytra crown. `side` is
    -1 (left/back) or +1 (right); `o` in [0,1] is how far the fan has opened.
    The roots sit high on the dome and get covered by the shell, so the blade
    reads as emerging from a cracked-open shell — not a belly flipper."""
    if o <= 0:
        return
    root_a = (BCX + side * 2, 34)
    root_b = (BCX + side * 4, 37)
    tip    = (BCX + side * int(17 * o), 33 + int(4 * o))
    mid    = (BCX + side * int(12 * o), 41 + int(5 * o))
    pygame.draw.polygon(surf, (*AMBER, 165), [root_a, tip, mid, root_b])
    pygame.draw.line(surf, (120, 80, 30, 200), root_a, mid, 1)     # vein
    pygame.draw.line(surf, (*GOLD, 190), root_a, tip, 1)           # lit edge


def _leg(surf, hip, knee, foot, spur=False):
    """One chunky spurred beetle leg: a fat 4px femur to the knee, a 3px tibia
    to the tarsus, a brass rim on the tibia underside so it survives the night
    sky, and a joint bead. Front legs carry a forward spur."""
    pygame.draw.line(surf, CHITIN, hip, knee, 4)                   # femur
    pygame.draw.line(surf, CHITIN, knee, foot, 3)                  # tibia
    pygame.draw.line(surf, BRASS, (knee[0], knee[1] + 1),
                     (foot[0], foot[1] + 1), 1)                    # underside rim
    pygame.draw.circle(surf, BRASS, knee, 2)                       # knee joint
    pygame.draw.circle(surf, CHITIN, knee, 2, 1)
    pygame.draw.circle(surf, CHITIN, foot, 2)                      # tarsal bead
    if spur:
        mx, my = (knee[0] + foot[0]) // 2, (knee[1] + foot[1]) // 2
        dx = 3 if foot[0] >= knee[0] else -3
        pygame.draw.line(surf, CHITIN, (mx, my), (mx + dx, my + 3), 2)


def _build_frame(wing_angle_deg):
    surf = _new(COMPOSITE_W, COMPOSITE_H)
    f = _flap(wing_angle_deg)
    s = 1.0 - f                                    # strike: 1 on down, 0 on up
    # Wing stays sealed through the hairline-crack stage, then fans — so the four
    # frames read as a clear progression, not a constant flutter.
    o = max(0.0, (s - 0.35) / 0.65)

    # ── HINDWINGS first, behind the shell: fan out to the sides/back on the
    # down-stroke, seal shut on the up-stroke.
    _hindwing(surf, -1, o)
    _hindwing(surf, +1, o)

    # ── LEGS: two chunky pairs. A spurred front pair reaches forward toward the
    # head, a hind pair rakes back — a planted, heavy stance, not a leg fringe.
    _leg(surf, (39, 50), (48, 51), (53, 48), spur=True)   # front upper
    _leg(surf, (37, 53), (45, 59), (50, 63), spur=True)   # front lower
    _leg(surf, (27, 50), (17, 52), (12, 49))              # hind upper
    _leg(surf, (29, 53), (20, 59), (15, 63))              # hind lower

    # ── ABDOMEN: a dark oval trailing lower-left under the dome so the body
    # doesn't float on its legs; a brass underside arc keeps it off the night.
    _aaellipse(surf, CHITIN, (BCX - 3, BCY + 12), 11, 6)
    _aaellipse(surf, SHELL, (BCX - 3, BCY + 11), 8, 4)
    abd = pygame.Rect(BCX - 3 - 11, BCY + 12 - 6, 22, 12)
    pygame.draw.arc(surf, BRASS, abd, math.radians(200), math.radians(340), 1)

    # ── ELYTRA DOME: the hero mass — one broad red-bronze oval, the largest
    # shape, with a warm brass band arcing over the crown for volume.
    _aaellipse(surf, CHITIN, (BCX + 1, BCY + 1), 16, 13)     # under-shadow
    _aaellipse(surf, SHELL, (BCX, BCY), 16, 13)              # bronze shell
    _aaellipse(surf, BRASS, (BCX - 2, BCY - 4), 12, 7)       # crown band
    _aaellipse(surf, SHELL, (BCX - 2, BCY - 2), 11, 6)       # re-shade below band

    # Dark lower-right rim crescent — the value drop from lit crown to shadowed
    # underside is what sells a hard curved shell rather than a flat disc.
    dome = pygame.Rect(BCX - 16, BCY - 13, 32, 26)
    pygame.draw.arc(surf, CHITIN, dome, math.radians(-70), math.radians(25), 2)

    # Crisp gold specular streak following the dome curve up-left, with a tight
    # near-white hotspot at its head — a hard lacquer glint, not a soft blob.
    sheen_dx = int((f - 0.5) * 4)
    pygame.draw.line(surf, GOLD, (BCX - 9 + sheen_dx, BCY - 7),
                     (BCX + 1 + sheen_dx, BCY - 2), 2)
    pygame.draw.circle(surf, WHITE, (BCX - 9 + sheen_dx, BCY - 7), 1)

    # Elytra suture: a single dark seam when sealed; on the strike it splits into
    # a gold-rimmed amber gap — the visible payoff the hindwings fanned from.
    crack = int(s * 7)
    if crack > 0:
        pygame.draw.polygon(surf, (*AMBER, 235), [
            (BCX, BCY - 12), (BCX - crack, BCY),
            (BCX, BCY + 12), (BCX + crack, BCY)])
        pygame.draw.line(surf, GOLD, (BCX, BCY - 12), (BCX - crack + 1, BCY), 1)
        pygame.draw.line(surf, GOLD, (BCX, BCY + 12), (BCX - crack + 1, BCY), 1)
        pygame.draw.line(surf, CHITIN, (BCX - crack, BCY - 2), (BCX - crack, BCY + 2), 1)
        pygame.draw.line(surf, CHITIN, (BCX + crack, BCY - 2), (BCX + crack, BCY + 2), 1)
    else:
        pygame.draw.line(surf, CHITIN, (BCX, BCY - 12), (BCX, BCY + 12), 2)

    # ── PRONOTAL (lower) HORN: a thickened prong projecting up from the thorax
    # to oppose the cephalic horn — the two tips frame the Hercules pincer gap.
    pron = [(45, 37), (43, 38), (39, 28), (37, 21),
            (39, 23), (42, 31), (45, 37)]
    pygame.draw.polygon(surf, CHITIN, pron)
    pygame.draw.line(surf, GOLD, (43, 38), (37, 21), 1)     # lit inner edge

    # ── HEAD: small dark oval under the horns.
    _aaellipse(surf, CHITIN, (HCX, HCY), 6, 5)
    _aaellipse(surf, SHELL, (HCX - 1, HCY - 1), 4, 3)

    # ── COMPOUND EYES: dark green with a white catchlight so the face reads.
    for ex, ey in ((HCX - 3, HCY + 1), (HCX + 4, HCY)):
        pygame.draw.circle(surf, EYE_G, (ex, ey), 3)
        pygame.draw.circle(surf, CHITIN, (ex, ey), 3, 1)
        pygame.draw.circle(surf, WHITE, (ex - 1, ey - 1), 1)

    # ── ANTENNAE: short, dark, and tucked forward-down BELOW the crown line so
    # nothing but the horn breaks the top of the silhouette.
    pygame.draw.line(surf, CHITIN, (48, 32), (53, 31), 2)
    pygame.draw.line(surf, CHITIN, (48, 33), (52, 35), 2)

    # ── CEPHALIC HORN (HERO TELL): a broad-based blade sweeping up-left and
    # forking into a Y-split at the tip, clearing the crown by ~10px. The gold
    # rim runs the full lit upper edge so it stays legible on the night sky.
    shaft = [(47, 32), (44, 25), (41, 20), (38, 17),
             (36, 17), (38, 21), (40, 25), (42, 32)]
    pygame.draw.polygon(surf, CHITIN, shaft)
    pygame.draw.circle(surf, CHITIN, (37, 17), 2)           # fork hub
    pygame.draw.line(surf, CHITIN, (37, 17), (34, 13), 3)   # left prong
    pygame.draw.line(surf, CHITIN, (37, 17), (40, 13), 3)   # right prong
    pygame.draw.circle(surf, CHITIN, (34, 13), 1)
    pygame.draw.circle(surf, CHITIN, (40, 13), 1)
    pygame.draw.lines(surf, GOLD, False,
                      [(42, 32), (40, 25), (38, 20), (36, 17), (34, 13)], 2)
    pygame.draw.circle(surf, WHITE, (34, 13), 1)            # tip glint

    return surf


_state = {}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    angle = _WING_ANGLES[frame_idx % len(_WING_ANGLES)]
    key = (frame_idx % len(_WING_ANGLES), round(tilt_deg / 3) * 3)
    if key not in _state:
        _state[key] = pygame.transform.rotozoom(
            _add_outline(_build_frame(angle)), key[1], 1.0)
    return _state[key]
