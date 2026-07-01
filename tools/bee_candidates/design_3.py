"""IRONHORN — Rhinoceros/Hercules beetle candidate for `skin_bee` (scratch).

An armored bruiser built as MASS + one big appendage, the opposite read of a
winged flutter. The tell that survives the 40px downscale is the cephalic HORN
sweeping up past CROWN_Y — it pokes clearly above the head so the silhouette
says "horned beetle" even as a solid shadow. Below it a forward pronotal horn
opposes the first, giving the true Hercules pincer.

The body is ONE broad domed elytra oval — the largest dark-bronze mass on the
sprite — carrying a hard gold specular streak so it never flattens into a black
blob on a night sky; on day sky the dark-chitin outline separates it from pale
blue. The flap is characterful, not a flutter: on the down-stroke the elytra
suture cracks open and two amber membranous hindwings fan out from behind
(strike factor s=1), tucking shut on the up-stroke (s=0) — a heavy beetle
labouring into the air.

Exploration only — NOT registered in any live BUILDERS map; production art is
untouched.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44          # thorax/elytra centre — the dome owns the middle
HCX, HCY = 44, 34          # head, set upper-right on the insect body axis
CROWN_Y = 24               # antenna reach; the horn must clear this line

# Dynastine chitin palette — dark base for value anchor, a warm bronze shell,
# and ONE gold specular so the dome reads as a lit curve, not a flat mass.
CHITIN   = (28, 18, 8)     # #1C1208 dark chitin — horn / head / legs / outline
SHELL    = (78, 58, 18)    # #4E3A12 bronze-brown elytra shell
BRASS    = (138, 106, 30)  # #8A6A1E warm brass mid-band on the dome
GOLD     = (216, 178, 74)  # #D8B24A gold specular streak / horn rim-light
AMBER    = (160, 110, 40)  # #A06E28 amber membranous hindwing
EYE_G    = (40, 90, 20)    # dark-green compound eye
WHITE    = (240, 240, 228) # catchlight / horn tip glint


def _new(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def _flap(a):
    # 0 at the deepest down-stroke (angle -40), 1 at the top up-stroke (50).
    return (a + 40) / 90.0


def _rot_blit(dst, src, angle, center):
    """Rotate `src` about its own centre and blit it centred at `center` — used
    to fan the pre-drawn hindwing membranes open on the down-stroke."""
    rot = pygame.transform.rotate(src, angle)
    dst.blit(rot, rot.get_rect(center=center))


def _hindwing_membrane(reach):
    """One amber membranous hindwing, drawn pointing straight down from a top
    pivot so a rotation reads as it swinging open. `reach` stretches the fan so
    the wing both lengthens and swings out with the strike factor."""
    w = _new(20, 34)
    tipx, tipy = 10, 12 + reach            # longer on the down-stroke
    pts = [(10, 2), (3, tipy - 6), (tipx, tipy), (17, tipy - 10)]
    pygame.draw.polygon(w, (*AMBER, 180), pts)
    # Two darker veins radiating from the pivot sell the membrane at 40px.
    pygame.draw.line(w, (110, 74, 26, 200), (10, 3), (5, tipy - 6), 1)
    pygame.draw.line(w, (110, 74, 26, 200), (10, 3), (tipx - 2, tipy - 2), 1)
    # A brighter leading edge so the membrane catches light against the shell.
    pygame.draw.line(w, (210, 158, 86, 170), (10, 3), (16, tipy - 10), 1)
    return w


def _leg(surf, hipx, hipy, kneex, kneey, footx, footy):
    """One chunky spurred beetle leg: a thick femur to the knee joint, a tibia
    to the tarsus, a small joint bead, and a short spur — reads as a beetle
    leg, not a hair."""
    pygame.draw.line(surf, CHITIN, (hipx, hipy), (kneex, kneey), 3)   # femur
    pygame.draw.line(surf, CHITIN, (kneex, kneey), (footx, footy), 2)  # tibia
    pygame.draw.circle(surf, BRASS, (kneex, kneey), 2)                 # knee joint
    pygame.draw.circle(surf, CHITIN, (kneex, kneey), 2, 1)
    # Tarsal foot bead + a short spur off the tibia.
    pygame.draw.circle(surf, CHITIN, (footx, footy), 2)
    spx = kneex + (footx - kneex) // 2
    spy = kneey + (footy - kneey) // 2
    pygame.draw.line(surf, CHITIN, (spx, spy), (spx - 3, spy + 2), 2)


def _build_frame(wing_angle_deg):
    surf = _new(COMPOSITE_W, COMPOSITE_H)
    f = _flap(wing_angle_deg)
    s = 1.0 - f                                    # strike: 1 on down, 0 on up
    reach = int(s * 20)

    # ── HINDWINGS first, behind the shell. They fan out and lengthen on the
    # down-stroke (s→1) and tuck shut on the up-stroke (s→0). Rotated from a
    # tucked ~10° to a wide swing so the flap reads as elytra cracking open.
    if reach > 0:
        mem = _hindwing_membrane(reach)
        swing = 12 + s * 34
        _rot_blit(surf, mem, swing, (BCX - 4 - reach // 2, BCY + 8 + reach // 3))
        _rot_blit(surf, mem, -swing, (BCX + 4 + reach // 2, BCY + 8 + reach // 3))

    # ── LEGS: three chunky pairs spread from the thorax underside, drawn behind
    # the dome so the femurs emerge from under the shell. Front pair reaches
    # forward, mid pair straight out, hind pair rakes back — the beetle stance.
    _leg(surf, BCX - 9, BCY - 4, BCX - 18, BCY - 6, BCX - 22, BCY - 1)   # L front
    _leg(surf, BCX - 10, BCY + 2, BCX - 20, BCY + 3, BCX - 24, BCY + 9)  # L mid
    _leg(surf, BCX - 9, BCY + 8, BCX - 18, BCY + 12, BCX - 21, BCY + 19)  # L hind
    _leg(surf, BCX + 9, BCY - 4, BCX + 18, BCY - 6, BCX + 22, BCY - 1)   # R front
    _leg(surf, BCX + 10, BCY + 2, BCX + 20, BCY + 3, BCX + 24, BCY + 9)  # R mid
    _leg(surf, BCX + 9, BCY + 8, BCX + 18, BCY + 12, BCX + 21, BCY + 19)  # R hind

    # ── ABDOMEN / thorax base: a dark oval trailing lower-left under the dome,
    # tying the elytra to the abdomen so the body doesn't float on its legs.
    _aaellipse(surf, CHITIN, (BCX - 3, BCY + 12), 11, 6)
    _aaellipse(surf, (52, 38, 12), (BCX - 3, BCY + 11), 8, 4)

    # ── ELYTRA DOME: the hero mass — one broad bronze oval, the largest shape.
    _aaellipse(surf, CHITIN, (BCX + 1, BCY + 1), 16, 13)     # under-shadow
    _aaellipse(surf, SHELL, (BCX, BCY), 16, 13)              # bronze shell
    # Warm brass mid-band curving over the crown of the dome for volume.
    _aaellipse(surf, BRASS, (BCX - 2, BCY - 4), 12, 7)
    _aaellipse(surf, SHELL, (BCX - 2, BCY - 2), 11, 6)       # re-shade below band

    # Gold specular streak — a thin bright ellipse offset up-left faking the
    # hard-shell gloss. Slides a touch with the flap so the dome reads metallic
    # and never a flat blob on a night sky.
    sheen_dx = int((f - 0.5) * 4)
    _aaellipse(surf, GOLD, (BCX - 5 + sheen_dx, BCY - 6), 8, 4)
    _aaellipse(surf, WHITE, (BCX - 7 + sheen_dx, BCY - 7), 3, 1)

    # Elytra suture down the midline; on the down-stroke it splits into a gold-
    # rimmed amber crack, the visual promise the hindwings fanned from within.
    crack = int(s * 5)
    if crack > 0:
        pygame.draw.polygon(surf, (*AMBER, 220), [
            (BCX, BCY - 12), (BCX - crack, BCY), (BCX, BCY + 12),
            (BCX + crack, BCY)])
        pygame.draw.line(surf, GOLD, (BCX - crack, BCY - 6), (BCX, BCY - 12), 1)
    pygame.draw.line(surf, CHITIN, (BCX, BCY - 12), (BCX, BCY + 12), 2)
    # A scatter of dark elytra spots — the Dynastes freckling.
    for sx, sy in ((BCX + 6, BCY - 3), (BCX + 9, BCY + 4), (BCX + 4, BCY + 8)):
        pygame.draw.circle(surf, CHITIN, (sx, sy), 1)

    # ── PRONOTAL (lower) HORN: projects forward from the thorax to oppose the
    # cephalic horn — the Hercules pincer. Curved blade with a gold top rim.
    pron = [(HCX - 5, HCY + 4), (HCX - 7, HCY + 1), (HCX - 12, HCY - 3),
            (HCX - 15, HCY - 4), (HCX - 13, HCY - 1), (HCX - 8, HCY + 3)]
    pygame.draw.polygon(surf, CHITIN, pron)
    pygame.draw.line(surf, GOLD, (HCX - 7, HCY),
                     (HCX - 15, HCY - 4), 1)

    # ── HEAD: small dark oval under the horns.
    _aaellipse(surf, CHITIN, (HCX, HCY), 6, 5)
    _aaellipse(surf, (52, 38, 12), (HCX - 1, HCY - 1), 4, 3)

    # ── COMPOUND EYES: one each side, dark green with a white catchlight so the
    # face stays alive at size.
    for ex, ey in ((HCX - 3, HCY + 1), (HCX + 4, HCY)):
        pygame.draw.circle(surf, EYE_G, (ex, ey), 3)
        pygame.draw.circle(surf, CHITIN, (ex, ey), 3, 1)
        pygame.draw.circle(surf, WHITE, (ex - 1, ey - 1), 1)

    # ── ANTENNAE: two short elbowed clubs, bending at CROWN_Y+4 and ending at
    # CROWN_Y with brass lamellar clubs, framing the horn without out-topping it.
    for sign in (-1, 1):
        rootx, rooty = HCX + sign * 4, HCY - 3
        elbx, elby = HCX + sign * 6, CROWN_Y + 4
        clubx, cluby = HCX + sign * 7, CROWN_Y
        pygame.draw.line(surf, CHITIN, (rootx, rooty), (elbx, elby), 2)
        pygame.draw.line(surf, CHITIN, (elbx, elby), (clubx, cluby), 2)
        pygame.draw.circle(surf, BRASS, (clubx, cluby), 2)
        pygame.draw.circle(surf, CHITIN, (clubx, cluby), 2, 1)

    # ── CEPHALIC HORN (HERO TELL): a big curved blade sweeping up-left from the
    # head, tip clearing CROWN_Y so it pokes above the head at 40px. Dark chitin
    # body with a gold rim-line down its lit upper edge for legibility on both
    # skies.
    horn = [(HCX + 1, HCY - 2), (HCX - 3, HCY - 5), (HCX - 6, CROWN_Y - 1),
            (HCX - 8, CROWN_Y - 6), (HCX - 5, CROWN_Y - 4),
            (HCX - 3, CROWN_Y + 2), (HCX + 2, HCY - 4)]
    pygame.draw.polygon(surf, CHITIN, horn)
    pygame.draw.line(surf, GOLD, (HCX - 3, HCY - 5),
                     (HCX - 8, CROWN_Y - 6), 2)
    pygame.draw.circle(surf, WHITE, (HCX - 8, CROWN_Y - 6), 1)  # tip glint

    return surf


_state = {}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    angle = _WING_ANGLES[frame_idx % len(_WING_ANGLES)]
    key = (frame_idx % len(_WING_ANGLES), round(tilt_deg / 3) * 3)
    if key not in _state:
        _state[key] = pygame.transform.rotozoom(
            _add_outline(_build_frame(angle)), key[1], 1.0)
    return _state[key]
