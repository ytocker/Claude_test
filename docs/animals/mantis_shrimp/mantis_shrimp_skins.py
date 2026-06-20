"""Candidate MANTIS SHRIMP skin (`skin_mantis_shrimp`) — round-1 exploration.

Five genuinely different takes on the peacock mantis shrimp as the player's
flappy bird. NOT five tweaks of one body: the variants differ in carapace
banding scheme (rainbow segments vs teal/orange duotone vs jewel-tone),
club size + raised-ness, eye-stalk length/spread, segment count, and how
much hard "armour plating" detail sits on the shell.

Contract mirrors game/animal_skins.py so the winner lifts straight in:

  * `build_mantis_shrimp_vN(wing_angle_deg) -> pygame.Surface` on a
    64×84 SRCALPHA canvas; body mass centred at (32,44), head/eye-stalks
    near (44,34) and up into the headroom.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a local
    `_make_prebuilt_skin(build_fn)`.
  * a label→getter dict at the bottom for the review sheet.

THE FLAP IS A STRIKE, not a feathered flap: the raptorial club-arms cock
BACK on the down-pose (_WING_ANGLES starts at 50) and PUNCH FORWARD on the
up-pose (ends at -40). `_strike()` maps a wing angle to that 0..1 punch.

North star: "a skin lives or dies at 40px in motion." The 40px tell is the
technicolor banded carapace + two periscope eye-stalks — a kaleidoscope in
armour — and the orange club snapping forward.
"""
import math
import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (eye-stalks reach up into the headroom) ─────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre  → (44, 34)
CROWN_Y  = 12 + DY              # top of head  → 24


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter — lazy 4-frame build
    + per-(frame, 3°) rotation cache, each frame house-outlined."""
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


def _eye(surf, cx, cy, r, *, iris=(20, 22, 30), white=(250, 250, 245),
         glint=True):
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 2))
    if glint:
        pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3),
                           max(1, r // 3))


def _strike(angle_deg):
    """0 = clubs cocked back (down-pose, wing=50), 1 = punched fully forward
    (up-pose, wing=-40). The reverse sense of a flap: lift the bird by
    throwing the punch, so the strike reads on the up-stroke."""
    return 1.0 - (angle_deg + 40) / 90.0


def _jewel_eye(surf, cx, cy, r, hue):
    """Iridescent compound eye: a coloured jewel with a bright mid-band and
    a hot glint — the mantis shrimp's signature periscope eye."""
    pygame.draw.circle(surf, (16, 10, 30), (cx, cy), r + 1)
    pygame.draw.circle(surf, hue, (cx, cy), r)
    # Equatorial band (the famous midband of ommatidia) + glint.
    pygame.draw.line(surf, (255, 255, 255), (cx - r, cy), (cx + r, cy), 1)
    pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3),
                       max(1, r // 3))


# ═════════════════════════════════════════════════════════════════════════════
# COMMON club helper — a "boxing-glove" raptorial dactyl club on a folded arm.
# The club is the orange hero; it swings from cocked (back, tucked under the
# head) to punched (forward, jabbing past the snout) by `s` in 0..1.
# ═════════════════════════════════════════════════════════════════════════════
def _club_arm(s, *, club_col, club_hi, arm_col, heel_col, length, club_r,
              sgn=1):
    """One raptorial club arm on its own surface, anchored at the shoulder.
    `s` 0..1 cocked→punched. Returns (surface, anchor_offset) blitted later."""
    w = pygame.Surface((40, 30), pygame.SRCALPHA)
    sh = (8, 18)                                  # shoulder pivot
    # Cocked: elbow tucked high+back, fist low+back. Punched: arm extends fwd.
    ext = s
    elbow = (sh[0] + 8 + int(ext * 4), sh[1] - 6 - int(ext * 2))
    fist = (sh[0] + 12 + int(ext * length), sh[1] - 2 + int((1 - ext) * 4))
    # Upper arm + forearm (segmented limb).
    pygame.draw.line(w, arm_col, sh, elbow, 4)
    pygame.draw.line(w, arm_col, elbow, fist, 4)
    pygame.draw.circle(w, arm_col, elbow, 2)
    # The dactyl club — a chunky rounded fist, the punch's business end.
    pygame.draw.circle(w, heel_col, (fist[0] + 1, fist[1] + 1), club_r + 1)
    pygame.draw.circle(w, club_col, fist, club_r)
    pygame.draw.circle(w, club_hi, (fist[0] - 1, fist[1] - 1), max(1, club_r - 2))
    # Saddle/striking ridge line so the club reads as a hammer, not a ball.
    pygame.draw.line(w, heel_col,
                     (fist[0], fist[1] - club_r), (fist[0], fist[1] + club_r), 1)
    if sgn < 0:
        w = pygame.transform.flip(w, False, True)
    return w


def _segmented_tail(surf, cx, cy, *, plate_col, plate_d, edge, count, span,
                    fan_col=None):
    """Armoured segmented abdomen sweeping back from the body, ending in a
    tail-fan (telson + uropods) when `fan_col` is given."""
    step = span / count
    for i in range(count):
        x = cx - int(i * step)
        rx = 8 - i
        ry = 11 - i
        pygame.draw.ellipse(surf, plate_d,
                            (x - rx, cy - ry + 1, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, plate_col,
                            (x - rx, cy - ry, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, edge, (x - rx, cy - ry, rx * 2, ry * 2), 1)
    if fan_col is not None:
        tx = cx - int(span)
        for dy, dx in ((-7, -6), (0, -9), (7, -6)):
            pygame.draw.polygon(surf, fan_col, [
                (tx, cy), (tx + dx, cy + dy), (tx + dx + 3, cy + dy)])
            pygame.draw.polygon(surf, edge, [
                (tx, cy), (tx + dx, cy + dy), (tx + dx + 3, cy + dy)], 1)


# ═════════════════════════════════════════════════════════════════════════════
# V1 · PEACOCK CLASSIC — the iconic peacock mantis shrimp. Teal carapace with
#     leopard-spotted plates, hot-orange leg fringe, two periscope eye-stalks
#     spread WIDE, mid-size red-orange clubs. The textbook reference, dialled
#     for cuteness. Tell: jewel eyes + teal/orange contrast + spotted shell.
# ═════════════════════════════════════════════════════════════════════════════
_V1_CARA   = (46, 196, 182)
_V1_CARA_D = (28, 150, 142)
_V1_CARA_H = (150, 240, 228)
_V1_PLATE  = (224, 247, 244)
_V1_SPOT   = (255, 145, 60)
_V1_CLUB   = (255, 107, 53)
_V1_CLUB_H = (255, 196, 120)
_V1_CLUB_D = (196, 64, 28)
_V1_STALK  = (58, 30, 90)
_V1_EYEHUE = (90, 220, 200)


def build_mantis_shrimp_v1(wing_angle_deg):
    surf = _new()
    s = _strike(wing_angle_deg)

    # Segmented armoured abdomen sweeping back, ending in an orange tail-fan.
    _segmented_tail(surf, BCX - 8, BCY + 1, plate_col=_V1_CARA, plate_d=_V1_CARA_D,
                    edge=_V1_CARA_D, count=4, span=20, fan_col=_V1_SPOT)

    # Far club arm cocked behind (depth), damped + tucked.
    far = _club_arm(s * 0.7, club_col=_V1_CLUB_D, club_hi=_V1_CLUB,
                    arm_col=_V1_CARA_D, heel_col=_V1_CLUB_D, length=8,
                    club_r=4)
    surf.blit(far, (HCX - 4, HCY + 6))

    # Carapace shield — broad torpedo body.
    _aaellipse(surf, _V1_CARA_D, (BCX + 1, BCY + 1), 17, 14)
    _aaellipse(surf, _V1_CARA, (BCX, BCY), 16, 13)
    _aaellipse(surf, _V1_CARA_H, (BCX - 3, BCY - 4), 8, 4)
    # Leopard plates: pale carapace segments with orange spots.
    for px, py in ((26, 40), (34, 38), (30, 46), (38, 44), (24, 48)):
        pygame.draw.circle(surf, _V1_PLATE, (px, py), 3)
        pygame.draw.circle(surf, _V1_SPOT, (px, py), 1)
    # Hot-orange swimmeret fringe along the belly.
    for fx in range(22, 42, 4):
        pygame.draw.line(surf, _V1_SPOT, (fx, BCY + 11), (fx, BCY + 15), 2)

    # Head + carapace crest.
    _aaellipse(surf, _V1_CARA_D, (HCX, HCY + 1), 11, 10)
    _aaellipse(surf, _V1_CARA, (HCX - 1, HCY), 10, 9)
    _aaellipse(surf, _V1_CARA_H, (HCX - 2, HCY - 3), 5, 3)

    # ── HERO: two periscope eye-stalks spread WIDE up into the headroom ──
    for sgn, ex in ((-1, HCX - 5), (1, HCX + 6)):
        tip = (ex + sgn * 3, CROWN_Y - 4)
        pygame.draw.line(surf, _V1_STALK, (HCX + sgn * 2, HCY - 4), tip, 4)
        _jewel_eye(surf, tip[0], tip[1], 4, _V1_EYEHUE)

    # ── HERO: the orange club punching forward ──
    near = _club_arm(s, club_col=_V1_CLUB, club_hi=_V1_CLUB_H,
                     arm_col=_V1_CARA_D, heel_col=_V1_CLUB_D, length=11,
                     club_r=5)
    surf.blit(near, (HCX - 6, HCY + 4))
    return surf


get_mantis_shrimp_v1 = _make_prebuilt_skin(build_mantis_shrimp_v1)


# ═════════════════════════════════════════════════════════════════════════════
# V2 · RAINBOW SEGMENTS — every abdominal plate a different spectrum hue
#     (red→violet down the body), clean rounded shapes, minimal plating noise.
#     One BIG club. Eye-stalks short + close. Tell: the full-spectrum banded
#     carapace reads as a kaleidoscope even at 40px.
# ═════════════════════════════════════════════════════════════════════════════
_V2_RAINBOW = [
    (255, 78, 90), (255, 150, 50), (255, 214, 63),
    (60, 210, 120), (60, 180, 240), (140, 110, 230),
]
_V2_BODY   = (40, 200, 188)
_V2_BODY_H = (170, 248, 236)
_V2_CLUB   = (255, 96, 48)
_V2_CLUB_H = (255, 200, 130)
_V2_CLUB_D = (190, 58, 24)
_V2_STALK  = (44, 22, 70)


def _v2_shade(col, k):
    return tuple(max(0, min(255, int(c * k))) for c in col)


def build_mantis_shrimp_v2(wing_angle_deg):
    surf = _new()
    s = _strike(wing_angle_deg)

    # Rainbow-banded abdomen: each segment a spectrum hue, big→small back.
    for i, col in enumerate(_V2_RAINBOW):
        x = BCX + 6 - i * 6
        rx, ry = 9 - i, 13 - i
        if rx < 2:
            break
        pygame.draw.ellipse(surf, _v2_shade(col, 0.7),
                            (x - rx, BCY - ry + 1, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, col, (x - rx, BCY - ry, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, _v2_shade(col, 1.35),
                            (x - rx + 1, BCY - ry + 1, max(1, rx), max(1, ry)))
    # Tail-fan picks up the violet tail hue.
    tx = BCX - 30
    for dy in (-6, 0, 6):
        pygame.draw.polygon(surf, _V2_RAINBOW[-1],
                            [(tx + 4, BCY), (tx - 4, BCY + dy),
                             (tx - 1, BCY + dy)])

    # Far club cocked behind.
    far = _club_arm(s * 0.65, club_col=_V2_CLUB_D, club_hi=_V2_CLUB,
                    arm_col=(30, 150, 140), heel_col=_V2_CLUB_D, length=7,
                    club_r=4)
    surf.blit(far, (HCX - 4, HCY + 6))

    # Head (teal, leads the rainbow).
    _aaellipse(surf, (28, 150, 140), (HCX, HCY + 1), 12, 11)
    _aaellipse(surf, _V2_BODY, (HCX - 1, HCY), 11, 10)
    _aaellipse(surf, _V2_BODY_H, (HCX - 2, HCY - 3), 6, 3)

    # Eye-stalks short + close, periscope pair.
    for sgn, ex in ((-1, HCX - 2), (1, HCX + 4)):
        tip = (ex, CROWN_Y - 1)
        pygame.draw.line(surf, _V2_STALK, (ex, HCY - 4), tip, 4)
        _jewel_eye(surf, tip[0], tip[1], 4, (120, 230, 210))

    # ── HERO: one BIG club punching forward ──
    near = _club_arm(s, club_col=_V2_CLUB, club_hi=_V2_CLUB_H,
                     arm_col=(30, 150, 140), heel_col=_V2_CLUB_D, length=12,
                     club_r=7)
    surf.blit(near, (HCX - 6, HCY + 3))
    return surf


get_mantis_shrimp_v2 = _make_prebuilt_skin(build_mantis_shrimp_v2)


# ═════════════════════════════════════════════════════════════════════════════
# V3 · DUOTONE BRUISER — stripped-down teal/orange duotone: a clean dark-teal
#     armoured shield with bold orange banding stripes, and OVERSIZED twin
#     clubs that dominate the silhouette like a heavyweight's gloves. Long
#     widely-spread eye-stalks. Tell: the giant orange double-fist + stripe.
# ═════════════════════════════════════════════════════════════════════════════
_V3_CARA   = (38, 178, 168)
_V3_CARA_D = (22, 122, 116)
_V3_CARA_H = (130, 232, 220)
_V3_BAND   = (255, 124, 48)
_V3_BAND_D = (210, 86, 28)
_V3_CLUB   = (255, 112, 56)
_V3_CLUB_H = (255, 206, 140)
_V3_CLUB_D = (188, 62, 26)
_V3_STALK  = (40, 20, 64)


def build_mantis_shrimp_v3(wing_angle_deg):
    surf = _new()
    s = _strike(wing_angle_deg)

    # Far oversized club cocked behind for double-fist read.
    far = _club_arm(s * 0.75, club_col=_V3_CLUB_D, club_hi=_V3_CLUB,
                    arm_col=_V3_CARA_D, heel_col=_V3_CLUB_D, length=9,
                    club_r=6)
    surf.blit(far, (HCX - 5, HCY + 8))

    # Segmented abdomen, duotone with orange band edges.
    _segmented_tail(surf, BCX - 7, BCY + 1, plate_col=_V3_CARA, plate_d=_V3_CARA_D,
                    edge=_V3_BAND, count=3, span=18, fan_col=_V3_BAND)

    # Carapace shield.
    _aaellipse(surf, _V3_CARA_D, (BCX + 1, BCY + 1), 17, 14)
    _aaellipse(surf, _V3_CARA, (BCX, BCY), 16, 13)
    _aaellipse(surf, _V3_CARA_H, (BCX - 3, BCY - 4), 8, 4)
    # Two bold orange banding stripes across the shield (duotone signature).
    for off in (-4, 5):
        pygame.draw.line(surf, _V3_BAND_D, (BCX + off - 1, BCY - 11),
                         (BCX + off - 1, BCY + 11), 4)
        pygame.draw.line(surf, _V3_BAND, (BCX + off, BCY - 11),
                         (BCX + off, BCY + 11), 3)
    # Re-rim so the bands clamp to the shield.
    pygame.draw.ellipse(surf, _V3_CARA_D, (BCX - 16, BCY - 13, 32, 26), 1)

    # Head.
    _aaellipse(surf, _V3_CARA_D, (HCX, HCY + 1), 11, 10)
    _aaellipse(surf, _V3_CARA, (HCX - 1, HCY), 10, 9)

    # ── HERO: long widely-spread eye-stalks ──
    for sgn, ex in ((-1, HCX - 6), (1, HCX + 7)):
        tip = (ex + sgn * 4, CROWN_Y - 6)
        pygame.draw.line(surf, _V3_STALK, (HCX + sgn * 2, HCY - 3), tip, 4)
        _jewel_eye(surf, tip[0], tip[1], 5, (110, 235, 215))

    # ── HERO: OVERSIZED near club dominating the silhouette ──
    near = _club_arm(s, club_col=_V3_CLUB, club_hi=_V3_CLUB_H,
                     arm_col=_V3_CARA_D, heel_col=_V3_CLUB_D, length=13,
                     club_r=8)
    surf.blit(near, (HCX - 7, HCY + 5))
    return surf


get_mantis_shrimp_v3 = _make_prebuilt_skin(build_mantis_shrimp_v3)


# ═════════════════════════════════════════════════════════════════════════════
# V4 · ARMOURED PLATING — heavy hard-surface read: overlapping carapace plates
#     with hard rim-light edges, riveted segment seams, jewel-tone (amethyst +
#     gold) banding instead of teal. Medium clubs. A "mech-crustacean". Tell:
#     the faceted plated armour + violet/gold jewel banding.
# ═════════════════════════════════════════════════════════════════════════════
_V4_ARMOR   = (90, 110, 200)        # steely amethyst-blue plate
_V4_ARMOR_D = (54, 66, 140)
_V4_ARMOR_H = (180, 200, 255)
_V4_GOLD    = (255, 206, 92)
_V4_GOLD_D  = (200, 150, 50)
_V4_VIOLET  = (158, 96, 224)
_V4_CLUB    = (255, 120, 64)
_V4_CLUB_H  = (255, 206, 140)
_V4_CLUB_D  = (192, 64, 28)
_V4_STALK   = (52, 28, 84)


def build_mantis_shrimp_v4(wing_angle_deg):
    surf = _new()
    s = _strike(wing_angle_deg)

    # Hard-plated segmented abdomen with gold seams.
    step = 6
    for i in range(4):
        x = BCX - 6 - i * step
        rx, ry = 8 - i, 12 - i
        pygame.draw.ellipse(surf, _V4_ARMOR_D, (x - rx, BCY - ry + 1, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, _V4_ARMOR, (x - rx, BCY - ry, rx * 2, ry * 2))
        # Rim-light + gold seam between plates.
        pygame.draw.arc(surf, _V4_ARMOR_H, (x - rx, BCY - ry, rx * 2, ry * 2),
                        math.radians(40), math.radians(150), 2)
        pygame.draw.line(surf, _V4_GOLD, (x + rx - 1, BCY - ry + 2),
                         (x + rx - 1, BCY + ry - 2), 1)
    # Gold tail-fan.
    tx = BCX - 30
    for dy in (-6, 0, 6):
        pygame.draw.polygon(surf, _V4_GOLD,
                            [(tx + 4, BCY), (tx - 4, BCY + dy), (tx, BCY + dy)])
        pygame.draw.polygon(surf, _V4_GOLD_D,
                            [(tx + 4, BCY), (tx - 4, BCY + dy), (tx, BCY + dy)], 1)

    far = _club_arm(s * 0.7, club_col=_V4_CLUB_D, club_hi=_V4_CLUB,
                    arm_col=_V4_ARMOR_D, heel_col=_V4_CLUB_D, length=8, club_r=5)
    surf.blit(far, (HCX - 4, HCY + 7))

    # Faceted carapace shield — drawn as overlapping hard plates.
    _aaellipse(surf, _V4_ARMOR_D, (BCX + 1, BCY + 1), 17, 14)
    _aaellipse(surf, _V4_ARMOR, (BCX, BCY), 16, 13)
    # Faceted top-plate with a hard highlight ridge.
    pygame.draw.polygon(surf, _V4_ARMOR_H,
                        [(BCX - 12, BCY - 6), (BCX + 4, BCY - 11),
                         (BCX + 8, BCY - 5), (BCX - 8, BCY - 2)])
    # Jewel banding: amethyst-violet + gold studs (riveted seams).
    pygame.draw.line(surf, _V4_VIOLET, (BCX - 2, BCY - 11), (BCX - 2, BCY + 11), 4)
    pygame.draw.line(surf, _V4_GOLD, (BCX - 2, BCY - 11), (BCX - 2, BCY + 11), 1)
    for ry in (BCY - 6, BCY, BCY + 6):
        pygame.draw.circle(surf, _V4_GOLD, (BCX + 8, ry), 1)
    pygame.draw.ellipse(surf, _V4_ARMOR_D, (BCX - 16, BCY - 13, 32, 26), 1)

    # Helmeted head plate.
    _aaellipse(surf, _V4_ARMOR_D, (HCX, HCY + 1), 11, 10)
    _aaellipse(surf, _V4_ARMOR, (HCX - 1, HCY), 10, 9)
    pygame.draw.arc(surf, _V4_GOLD, (HCX - 9, HCY - 8, 18, 16),
                    math.radians(30), math.radians(150), 2)

    # Eye-stalks, jewel-tone irises.
    for sgn, ex in ((-1, HCX - 5), (1, HCX + 6)):
        tip = (ex + sgn * 3, CROWN_Y - 4)
        pygame.draw.line(surf, _V4_STALK, (HCX + sgn * 2, HCY - 4), tip, 4)
        _jewel_eye(surf, tip[0], tip[1], 4, _V4_VIOLET)

    near = _club_arm(s, club_col=_V4_CLUB, club_hi=_V4_CLUB_H,
                     arm_col=_V4_ARMOR_D, heel_col=_V4_CLUB_D, length=11, club_r=6)
    surf.blit(near, (HCX - 6, HCY + 4))
    return surf


get_mantis_shrimp_v4 = _make_prebuilt_skin(build_mantis_shrimp_v4)


# ═════════════════════════════════════════════════════════════════════════════
# V5 · NEON DEEP-SEA — a bioluminescent abyssal take: dark indigo carapace lit
#     by glowing neon edge-lines (cyan/magenta), eye-stalks as glowing lamps on
#     long thin stalks, an electric-blue plasma club. Reads on NIGHT skies as a
#     glowing alien; the dark body keeps it bold on bright days. Tell: the neon
#     wireframe banding + lamp eyes + electric club.
# ═════════════════════════════════════════════════════════════════════════════
_V5_BODY   = (24, 30, 64)
_V5_BODY_D = (14, 18, 44)
_V5_NEON_C = (60, 240, 220)         # cyan
_V5_NEON_M = (255, 80, 200)         # magenta
_V5_NEON_Y = (255, 214, 70)
_V5_LAMP   = (120, 255, 240)
_V5_CLUB   = (90, 200, 255)         # electric-blue plasma
_V5_CLUB_H = (220, 250, 255)
_V5_CLUB_D = (40, 120, 200)
_V5_STALK  = (30, 40, 90)


def build_mantis_shrimp_v5(wing_angle_deg):
    surf = _new()
    s = _strike(wing_angle_deg)

    # Dark segmented abdomen, each seam a neon edge-glow.
    for i in range(4):
        x = BCX - 7 - i * 6
        rx, ry = 8 - i, 12 - i
        pygame.draw.ellipse(surf, _V5_BODY_D, (x - rx, BCY - ry, rx * 2, ry * 2))
        col = (_V5_NEON_C, _V5_NEON_M)[i % 2]
        pygame.draw.ellipse(surf, col, (x - rx, BCY - ry, rx * 2, ry * 2), 1)
    # Glowing tail-fan rays.
    tx = BCX - 31
    for dy in (-6, 0, 6):
        pygame.draw.line(surf, _V5_NEON_C, (tx + 4, BCY), (tx - 3, BCY + dy), 2)

    far = _club_arm(s * 0.7, club_col=_V5_CLUB_D, club_hi=_V5_CLUB,
                    arm_col=_V5_STALK, heel_col=_V5_CLUB_D, length=8, club_r=4)
    surf.blit(far, (HCX - 4, HCY + 7))

    # Dark carapace shield with neon wireframe banding.
    _aaellipse(surf, _V5_BODY_D, (BCX + 1, BCY + 1), 17, 14)
    _aaellipse(surf, _V5_BODY, (BCX, BCY), 16, 13)
    pygame.draw.ellipse(surf, _V5_NEON_C, (BCX - 16, BCY - 13, 32, 26), 1)
    for off, col in ((-5, _V5_NEON_M), (4, _V5_NEON_Y)):
        pygame.draw.line(surf, col, (BCX + off, BCY - 10), (BCX + off, BCY + 10), 2)
    # Bioluminescent belly dots.
    for fx in range(24, 42, 5):
        pygame.draw.circle(surf, _V5_LAMP, (fx, BCY + 9), 1)

    # Head.
    _aaellipse(surf, _V5_BODY_D, (HCX, HCY + 1), 11, 10)
    _aaellipse(surf, _V5_BODY, (HCX - 1, HCY), 10, 9)
    pygame.draw.arc(surf, _V5_NEON_C, (HCX - 9, HCY - 8, 18, 16),
                    math.radians(20), math.radians(160), 1)

    # ── HERO: long thin stalks ending in glowing LAMP eyes ──
    for sgn, ex in ((-1, HCX - 5), (1, HCX + 6)):
        tip = (ex + sgn * 4, CROWN_Y - 7)
        pygame.draw.line(surf, _V5_STALK, (HCX + sgn * 2, HCY - 4), tip, 3)
        pygame.draw.circle(surf, _V5_LAMP, tip, 5)
        pygame.draw.circle(surf, (240, 255, 252), tip, 2)
        pygame.draw.circle(surf, _V5_NEON_C, tip, 5, 1)

    # ── HERO: electric-blue plasma club punching forward ──
    near = _club_arm(s, club_col=_V5_CLUB, club_hi=_V5_CLUB_H,
                     arm_col=_V5_STALK, heel_col=_V5_CLUB_D, length=11, club_r=6)
    surf.blit(near, (HCX - 6, HCY + 4))
    return surf


get_mantis_shrimp_v5 = _make_prebuilt_skin(build_mantis_shrimp_v5)


# ─────────────────────────────────────────────────────────────────────────────
# Label → getter (for the round-1 review sheet).
# ─────────────────────────────────────────────────────────────────────────────
VARIANTS = {
    "v1 · PEACOCK CLASSIC":   get_mantis_shrimp_v1,
    "v2 · RAINBOW SEGMENTS":  get_mantis_shrimp_v2,
    "v3 · DUOTONE BRUISER":   get_mantis_shrimp_v3,
    "v4 · ARMOURED PLATING":  get_mantis_shrimp_v4,
    "v5 · NEON DEEP-SEA":     get_mantis_shrimp_v5,
}

VARIANT_TELLS = {
    "v1 · PEACOCK CLASSIC":  "jewel eyes + teal/orange spotted shell",
    "v2 · RAINBOW SEGMENTS": "full-spectrum banded abdomen kaleidoscope",
    "v3 · DUOTONE BRUISER":  "giant orange double-fist + stripe",
    "v4 · ARMOURED PLATING": "faceted plates + violet/gold jewel banding",
    "v5 · NEON DEEP-SEA":    "neon wireframe + lamp eyes + plasma club",
}
