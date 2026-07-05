"""SOCCER redesign — design_2 THE GOALKEEPER (exploration only).

An acid-lime goalkeeper kit. The whole bird is re-plumaged to a high-vis
lime jersey through the palette system, then the costume rides on two hard
silhouette tells: chunky padded WHITE keeper GLOVES that bulge past each
wingtip (the hero element — a keeper is the one player allowed hands) and a
real peaked CAP whose flat black brim juts forward off the head outline.
Supporting kit stays deliberately minimal so the read survives 40px — one
black collar band across the shoulders and one bold flat "1" on a clean
lime chest.

R2 fix-list (each tied to an art-director note):
  * Gloves rebuilt as the hero silhouette — fat rounded WHITE mitts ~1.4x
    the wingtip width, flat dark finger ridges, a black cuff band, and the
    pad protrudes PAST the wing edge so it breaks the contour at 40px.
  * Cap gets a real peaked brim — a distinct flat black polygon jutting
    forward past the head/beak line, lime dome above with a hard 1px value
    break, no soft gradient.
  * Chevron yoke killed — replaced with ONE clean black collar band so the
    chest reads clean.
  * The "1" is a flat high-contrast black numeral (two bold rectangles),
    centred on the chest with nothing fighting it.
  * All shading flattened to crisp flat fills + one darker lime shadow
    polygon + one outline — no airbrushed edges.

Scratch builder — NOT registered in store_skins.BUILDERS. Production art is
untouched until a winner is picked.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, PARROT_DY
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette ──────────────────────────────────────────────────────────────────
_LIME      = (199, 240, 0)         # #C7F000 jersey/cap primary
_LIME_H    = (224, 255, 96)        # lit jersey
_LIME_D    = (150, 190, 0)         # jersey shadow
_BLACK     = (17, 17, 17)          # #111111 brim/number/collar
_GREEN_D   = (58, 138, 0)          # #3A8A00 deep shadow value
_OUTLINE   = (14, 36, 0)           # #0E2400 keeper outline value
_WHITE     = (244, 247, 240)       # padded glove white
_GLOVE_SH  = (206, 212, 198)       # one flat glove shadow tone
_GREY_D    = (52, 54, 50)          # finger-ridge dark

# Full acid-lime re-plumage. Body/wings/head are lime jersey values so the
# bird reads as a kitted-out keeper, not a scarlet macaw; the tail dips to
# dark green (the dipped-lime shorts/tail), feet go near-black as the boot
# base, and the lens is dropped — the cap brim owns the brow line.
_GK_PAL = _pal(
    tail=[(58, 138, 0), (84, 168, 0), (120, 196, 0), (162, 220, 30)],
    tail_line=_OUTLINE,
    body_shadow=_LIME_D,
    body_main=_LIME,
    body_chest=_LIME_H,
    body_belly=(186, 228, 30),
    sheen=(255, 255, 255, 70),
    wing_main=_LIME,
    wing_dark=_LIME_D,
    wing_tip=_LIME_H,
    wing_secondary=None,
    wing_highlight=(232, 255, 140),
    head_shadow=_LIME_D,
    head_main=_LIME,
    head_cheek=_LIME_H,
    head_crown=(214, 250, 80),
    lens_frame=(150, 190, 0),
    lens_body=(120, 160, 0),
    lens_tint=None,
    lens_glint=None,
    beak_main=(60, 64, 70),       # dark keeper-neutral beak, no warm orange
    beak_dark=(28, 30, 34),
    beak_gloss=(150, 156, 165),
    foot=_BLACK,                  # boot base
)


def _lime_base(angle_deg):
    # Lime-kitted bird, no aviators — the peaked cap brim owns the head.
    return _build_parrot_with_palette(angle_deg, _GK_PAL, draw_lenses=False)


def _padded_glove(surf, cx, cy, finger_dir):
    """Chunky padded WHITE keeper mitt — the hero silhouette tell.

    A fat rounded pad ~1.4x the wingtip width in pale white (contrast against
    the lime sleeve), 3 flat dark finger ridges, one flat shadow tone, a black
    cuff band. ``finger_dir`` is +1 to splay fingers to the right, -1 to the
    left, so each wingtip's fingers point outward off the silhouette.
    """
    gw, gh = 15, 15                       # ~1.4x the ~10px wingtip mass
    gx, gy = cx - gw // 2, cy - gh // 2
    # Outline backing so the white pad stays a distinct mass on lime sky.
    pygame.draw.rect(surf, _OUTLINE, (gx - 1, gy - 1, gw + 2, gh + 2), border_radius=7)
    # White latex pad (the palm/back of the mitt).
    pygame.draw.rect(surf, _WHITE, (gx, gy, gw, gh), border_radius=6)
    # One flat shadow shape — lower band, no gradient.
    pygame.draw.rect(surf, _GLOVE_SH, (gx, gy + gh - 5, gw, 5),
                     border_radius=6)
    # Three short flat finger ridges splaying off the outer edge.
    fx = gx + gw - 3 if finger_dir > 0 else gx
    for i in range(3):
        fy = gy + 2 + i * 4
        pygame.draw.rect(surf, _GREY_D, (fx, fy, 3, 3))
    # Black cuff band across the wrist root (between glove and sleeve).
    if finger_dir > 0:
        pygame.draw.rect(surf, _BLACK, (gx - 3, gy + gh - 3, 6, 4),
                         border_radius=1)
    else:
        pygame.draw.rect(surf, _BLACK, (gx + gw - 3, gy + gh - 3, 6, 4),
                         border_radius=1)
    # One crisp rim highlight on the top edge of the pad.
    pygame.draw.line(surf, (255, 255, 255), (gx + 3, gy + 1), (gx + gw - 4, gy + 1), 1)


def _paint(surf, wing_angle_deg):
    # ── black cleats + lime socks at the feet ─────────────────────────────────
    for fx in (24, 34):
        pygame.draw.rect(surf, _LIME, (fx - 2, 60, 6, 6))              # sock
        pygame.draw.line(surf, _BLACK, (fx - 2, 62), (fx + 3, 62), 1)  # sock stripe
        pygame.draw.rect(surf, _BLACK, (fx - 3, 65, 9, 5), border_radius=2)    # boot
        pygame.draw.rect(surf, _OUTLINE, (fx - 3, 68, 9, 2), border_radius=1)  # sole/studs

    # ── single black collar band across the shoulders (chevron killed) ────────
    # ONE clean horizontal dark band, full body width, so the chest stays clean
    # lime and the number breathes.
    pygame.draw.line(surf, _BLACK, (HX - 19, HY + 3), (HX + 1, HY + 3), 2)
    pygame.draw.line(surf, _GREEN_D, (HX - 19, HY + 5), (HX + 1, HY + 5), 1)

    # ── chest "1": a flat high-contrast black numeral ─────────────────────────
    # Two bold rectangles — a tall stem + a short serif foot — centred on the
    # clean lime chest. Survives 40px as a legible digit.
    nx, ny = HX - 11, HY + 8
    pygame.draw.rect(surf, _BLACK, (nx, ny, 3, 9))            # tall stem (>=6px)
    pygame.draw.rect(surf, _BLACK, (nx - 3, ny + 8, 9, 3))    # serif foot
    pygame.draw.rect(surf, _BLACK, (nx - 2, ny, 2, 3))        # flag

    # ── padded gloves at each wingtip — the hero tell ─────────────────────────
    # Placed just OUTSIDE the wing silhouette (base spans ~x5..57 at the tips)
    # so each fat white mitt protrudes past the contour and breaks it at 40px.
    _padded_glove(surf, 8, 39, finger_dir=-1)    # back/left wingtip
    _padded_glove(surf, 55, 41, finger_dir=+1)   # near/right wingtip

    # ── goalkeeper cap: lime peaked dome + a real flat black brim ─────────────
    cy = CROWN_Y
    # Brim FIRST: a distinct flat black polygon jutting FORWARD (toward the
    # beak, i.e. left) several px past the head/beak line — the goalie tell.
    brim = [(HX - 20, cy + 5), (HX - 4, cy + 2), (HX + 6, cy + 4),
            (HX - 4, cy + 7), (HX - 19, cy + 8)]
    pygame.draw.polygon(surf, _OUTLINE, brim)
    pygame.draw.polygon(surf, _BLACK,
                        [(HX - 19, cy + 5), (HX - 4, cy + 3), (HX + 5, cy + 4),
                         (HX - 4, cy + 6), (HX - 18, cy + 7)])

    # Rounded lime crown dome above the brim — flat fill, one shadow polygon.
    dome = [(HX - 12, cy + 3), (HX - 9, cy - 5), (HX - 2, cy - 9),
            (HX + 6, cy - 7), (HX + 11, cy - 1), (HX + 12, cy + 3)]
    pygame.draw.polygon(surf, _LIME, dome)
    # ONE darker lime shadow shape on the lower-right of the dome (no gradient).
    pygame.draw.polygon(surf, _LIME_D,
                        [(HX + 12, cy + 3), (HX + 11, cy - 1), (HX + 5, cy + 1),
                         (HX + 7, cy + 3)])
    # Hard 1px value break between dome and the black brim band below.
    pygame.draw.line(surf, _BLACK, (HX - 12, cy + 3), (HX + 12, cy + 3), 1)
    # One crisp rim highlight on the lit crown panel.
    pygame.draw.line(surf, _LIME_H, (HX - 8, cy - 4), (HX - 2, cy - 8), 1)
    # Top button.
    pygame.draw.circle(surf, _LIME_D, (HX - 1, cy - 8), 2)
    pygame.draw.circle(surf, _LIME_H, (HX - 2, cy - 9), 1)


build = store_skins._make_skin(_paint, base_fn=_lime_base)
