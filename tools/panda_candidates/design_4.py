"""Panda animal-skin candidate — DESIGN 4: KUNG-FU PANDA.

The action/hero panda. The shared giant-panda kit (white face disc, round
black ears, black eye patches, nose) armoured for a fight by the single tell
that reads at 40px: a RED HEADBAND clamped across the brow, with one bold red
ribbon tail flicking back off the skull. The belt across the white belly is a
thin DARK band with gold edges (a belt, not a second red focal point) carrying
one gold medallion dot. The black panda arms throw a punch — the lead fist is
pushed clear of the silhouette into the sky, and the arms swap which side
extends across the 4-frame cycle so the flap visibly throws.

Scratch builder only — mirrors game/animal_skins.py geometry + the
`_make_prebuilt_skin` factory so it lifts straight into production later. Not
registered in any BUILDERS map; rendered via tools/ninja_render.py.
"""
import math
import pygame

from game import parrot
from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY   # body centre (32, 44)
HCX, HCY = 44, 22 + DY   # head centre (44, 34)
CROWN_Y = 12 + DY        # top of head (24)


# ── palette ──────────────────────────────────────────────────────────────────
BLACK     = (26, 26, 26)        # #1A1A1A panda black
BLACK_HI  = (54, 54, 60)        # soft black highlight on arm/ear mass
WHITE     = (245, 245, 245)     # #F5F5F5 panda white
WHITE_SH  = (216, 216, 220)     # white value step
RED       = (200, 16, 46)       # #C8102E kung-fu red
RED_SH    = (122, 12, 30)       # #7A0C1E red shadow
GOLD      = (227, 178, 60)      # #E3B23C gold emblem + belt trim
GOLD_SH   = (176, 132, 36)
DARK_BELT = (40, 40, 46)        # belt band — dark, NOT red, so red stays unique
PINK      = (231, 169, 169)     # warm cheek/nose-tip accent


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


def _rot_blit(surf, layer, anchor):
    surf.blit(layer, layer.get_rect(center=anchor).topleft)


def _flap(angle_deg):
    """0..1 'wing is up' factor; _WING_ANGLES runs 50→-40. Drives the
    punch reach + the trailing-tail flick so the pose feels alive."""
    return (angle_deg + 40) / 90.0


# ── black panda arm ending in a fist ─────────────────────────────────────────
def _panda_fist(extended):
    """A stubby black panda forearm + a clearly rounded fist knob. No cloth
    wraps — at 40px wrist wraps are invisible noise, so the arm is pure black
    mass whose value the night-sky outline carries. `extended` lengthens the
    reach so a punching arm pushes its fist farther out than a tucked one."""
    w = pygame.Surface((52, 40), pygame.SRCALPHA)
    cy = 20
    reach = 14 if extended else 4
    fist_x = 24 + reach
    # Forearm wedge from the shoulder root out to the fist.
    pygame.draw.polygon(w, BLACK, [
        (10, cy - 6), (fist_x, cy - 7), (fist_x, cy + 7), (10, cy + 7),
    ])
    # Top highlight so the black limb keeps form against dark night sky.
    pygame.draw.line(w, BLACK_HI, (12, cy - 5), (fist_x - 2, cy - 6), 2)
    # Rounded fist knob — the punching read. Drawn big + clean so it stays a
    # distinct knob when it clears the white-belly silhouette.
    pygame.draw.circle(w, BLACK, (fist_x, cy), 9)
    pygame.draw.circle(w, BLACK_HI, (fist_x - 3, cy - 3), 3)
    # Suggested knuckle ridge along the leading face of the fist.
    for ky in (cy - 4, cy, cy + 4):
        pygame.draw.circle(w, (14, 14, 16), (fist_x + 5, ky), 1)
    return w


def _ribbon_tail(flick):
    """ONE bold red ribbon tail — the hero accent's motion read. A fat tapering
    triangle with a gold lower edge; `flick` swings the tip vertically with
    the flap so the cloth streams. Drawn to read as clearly ATTACHED to the
    band (wide root) then flicking back to a point."""
    w = pygame.Surface((26, 26), pygame.SRCALPHA)
    base_y = 12
    tip_y = base_y + flick
    pts = [
        (2, base_y - 5),                 # wide root at the band
        (2, base_y + 5),
        (23, tip_y + 2),                 # flicked point
        (23, tip_y - 1),
    ]
    pygame.draw.polygon(w, RED, pts)
    pygame.draw.polygon(w, RED_SH, pts, 1)
    # Gold edge along the lower run so it ties to the headband's gold line.
    pygame.draw.line(w, GOLD, (3, base_y + 4), (22, tip_y + 1), 1)
    return w


def build(wing_angle_deg) -> pygame.Surface:
    """Draw one 64×84 SRCALPHA frame of the Kung-Fu Panda."""
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    f = _flap(wing_angle_deg)            # 0 (wing down) .. 1 (wing up)

    # ── trailing red ribbon tail (drawn first so it streams BEHIND the head) ──
    # One bold tail flicking back off the right of the skull, attached to the
    # headband knot. Flick tracks the wing for life.
    flick = int(round((f - 0.5) * 9))    # ~-5..+5 px tail-tip swing
    tail = _ribbon_tail(flick)
    # Anchor off the right-back of the head so it pushes past the silhouette.
    _rot_blit(surf, tail, (HCX + 17, HCY - 4))

    # ── far arm (behind the body) — opposite phase to the near arm ──
    # When the near fist is tucked, this one is thrown; gives the swap so the
    # 4-frame cycle reads as a punch being thrown and recovered.
    far_extended = f < 0.5
    far_ang = -22 - (1.0 - f) * 10
    _rot_blit(surf, pygame.transform.rotate(_panda_fist(far_extended), far_ang),
              (BCX + 11, BCY - 3))

    # ── body: chunky white torso framed by a black shoulder yoke ──
    # Black shoulder yoke (the real panda's dark shoulder band).
    _aaellipse(surf, BLACK, (BCX, BCY - 6), 19, 11)
    # White belly/torso disc over the collision centre — kept large + clean so
    # the black-on-white panda contrast survives the night sky.
    _aaellipse(surf, WHITE_SH, (BCX, BCY + 2), 18, 16)
    _aaellipse(surf, WHITE, (BCX - 1, BCY + 1), 17, 15)
    # Soft belly value step low-left for roundness.
    _aaellipse(surf, WHITE_SH, (BCX - 5, BCY + 7), 9, 7)

    # ── black leg stubs braced in a stance ──
    for sgn, lx in ((-1, BCX - 7), (1, BCX + 7)):
        ly = BCY + 13
        pygame.draw.line(surf, BLACK, (lx, ly), (lx + sgn * 2, ly + 7), 5)
        pygame.draw.circle(surf, BLACK, (lx + sgn * 2, ly + 7), 3)

    # ── thin DARK belt across the belly with a gold edge each side ──
    # Demoted from a red obi: a single dark band reads as a belt at 40px
    # without competing with the headband for the "red" attention slot, and
    # it occupies a thin strip so the white belly stays mostly unbroken.
    belt_y = BCY + 6
    pygame.draw.line(surf, DARK_BELT, (BCX - 16, belt_y),
                     (BCX + 16, belt_y - 1), 4)
    pygame.draw.line(surf, BLACK, (BCX - 16, belt_y + 2),
                     (BCX + 16, belt_y + 1), 1)
    # Gold edge cap at each end of the belt — two deliberate warm ticks.
    pygame.draw.circle(surf, GOLD, (BCX - 16, belt_y), 1)
    pygame.draw.circle(surf, GOLD, (BCX + 16, belt_y - 1), 1)
    # ONE gold medallion dot centred on the belt — the single warm accent.
    pygame.draw.circle(surf, GOLD_SH, (BCX, belt_y + 1), 2)
    pygame.draw.circle(surf, GOLD, (BCX, belt_y), 2)

    # ── ears: two round black ears up past the crown ──
    for dx in (-8, 9):
        _aaellipse(surf, BLACK, (HCX + dx, CROWN_Y + 1), 6, 6)
        _aaellipse(surf, BLACK_HI, (HCX + dx - 1, CROWN_Y - 1), 2, 2)

    # ── head: round white face disc ──
    _aaellipse(surf, WHITE_SH, (HCX, HCY + 1), 13, 12)
    _aaellipse(surf, WHITE, (HCX, HCY), 12, 11)

    # ── two black teardrop eye patches angled down-inward ──
    for sgn, ex in ((-1, HCX - 6), (1, HCX + 6)):
        patch = [
            (ex, HCY - 4), (ex + sgn * 5, HCY - 2),
            (ex + sgn * 4, HCY + 5), (ex - sgn * 1, HCY + 4),
        ]
        pygame.draw.polygon(surf, BLACK, patch)
        # White eye glint dot keeps the look fierce-but-friendly.
        pygame.draw.circle(surf, (250, 250, 245), (ex + sgn * 2, HCY + 1), 2)
        pygame.draw.circle(surf, (18, 18, 22), (ex + sgn * 2, HCY + 1), 1)

    # Cheek blush low on the face for charm.
    _aaellipse(surf, PINK, (HCX - 7, HCY + 6), 3, 2)
    _aaellipse(surf, PINK, (HCX + 7, HCY + 6), 3, 2)

    # Nose triangle + soft mouth line.
    pygame.draw.polygon(surf, BLACK, [
        (HCX - 2, HCY + 5), (HCX + 2, HCY + 5), (HCX, HCY + 8)])
    pygame.draw.line(surf, BLACK, (HCX, HCY + 8), (HCX, HCY + 10), 1)
    pygame.draw.line(surf, BLACK, (HCX - 3, HCY + 10), (HCX, HCY + 10), 1)
    pygame.draw.line(surf, BLACK, (HCX, HCY + 10), (HCX + 3, HCY + 10), 1)

    # ── RED HEADBAND across the brow — the hero tell, locked above the eyes ──
    # A clean 2px horizontal red stripe directly above the eye patches, the
    # largest + most eye-catching red on the whole sprite.
    band_y = HCY - 6
    pygame.draw.polygon(surf, RED, [
        (HCX - 12, band_y - 2), (HCX + 12, band_y - 3),
        (HCX + 12, band_y + 2), (HCX - 12, band_y + 1),
    ])
    pygame.draw.line(surf, RED_SH, (HCX - 12, band_y + 1),
                     (HCX + 12, band_y + 2), 1)
    # Hairline gold edge along the top so the band catches a warm glint.
    pygame.draw.line(surf, GOLD, (HCX - 11, band_y - 1),
                     (HCX + 11, band_y - 2), 1)
    # Side knot on the RIGHT where the trailing tail leaves the head — ties the
    # band to the streaming ribbon so it reads as one continuous headband.
    pygame.draw.circle(surf, RED, (HCX + 12, band_y), 3)
    pygame.draw.circle(surf, RED_SH, (HCX + 12, band_y), 3, 1)

    # ── near arm (over the body) — the HERO PUNCH, fist clears the belly ──
    # Pushed out past the white belly into the sky so a distinct black knob
    # sits clear of the silhouette. Extends in opposite phase to the far arm.
    near_extended = f >= 0.5
    near_ang = 24 + f * 16
    # Anchor up-left of the belly so the extended fist punches OUT into the sky
    # well clear of the leg stubs — a distinct black knob off the silhouette.
    reach_x = -9 - (5 if near_extended else 0)
    reach_y = -2 - (7 if near_extended else 0)
    _rot_blit(surf, pygame.transform.rotate(_panda_fist(near_extended), near_ang),
              (BCX + reach_x, BCY + reach_y))

    return surf


get_skin = _make_prebuilt_skin(build)
