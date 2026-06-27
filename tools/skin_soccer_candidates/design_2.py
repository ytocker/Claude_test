"""SOCCER redesign — design_2 THE GOALKEEPER (exploration only).

An acid-lime goalkeeper kit. The whole bird is re-plumaged to a high-vis
lime jersey through the palette system, then two hard silhouette tells are
painted on: a classic peaked goalkeeper CAP (lime crown + flat black brim
poking left off the head) and chunky padded GLOVES at each wingtip
(rounded black latex mitts with a yellow accent strip + a wrist-strap
circle). Supporting kit reads — a black chevron yoke across the shoulders,
a "1" on the chest, black cleats with lime socks, and a black shorts
waistband at the tail — round out the keeper read at 40px.

The cap + gloves are the KEY tells: a goalie is the one outfield player
allowed to use hands, so chunky padded mitts plus the peaked cap are the
instantly-legible costume cue.

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
_BLACK     = (17, 17, 17)          # #111111 brim/gloves/number
_GOLD      = (255, 196, 0)         # #FFC400 glove accent
_GREEN_D   = (58, 138, 0)          # #3A8A00 shadow/socks
_OUTLINE   = (14, 36, 0)           # #0E2400 keeper outline value
_WHITE     = (245, 248, 240)

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


def _padded_glove(surf, gx, gy, strap_left):
    """Chunky padded latex mitt — black rounded pad with a yellow accent
    strip + a wrist-strap circle. The single hardest tell of the costume,
    so it is drawn as a fat block, never a line."""
    # Outline-weight backing so the pad stays a distinct mass on lime sky.
    pygame.draw.rect(surf, _OUTLINE, (gx - 1, gy - 1, 14, 16), border_radius=5)
    # Black latex pad.
    pygame.draw.rect(surf, _BLACK, (gx, gy, 12, 14), border_radius=4)
    # Padded finger ridges — vertical grooves so it reads as a glove, not a box.
    for i in range(3):
        rx = gx + 2 + i * 3
        pygame.draw.line(surf, (44, 44, 48), (rx, gy + 1), (rx, gy + 7), 1)
    # Yellow accent strip across the back of the hand (the #FFC400 pop).
    pygame.draw.rect(surf, _GOLD, (gx + 1, gy + 8, 10, 3), border_radius=1)
    pygame.draw.line(surf, (255, 224, 120), (gx + 2, gy + 9), (gx + 9, gy + 9), 1)
    # Wrist-strap circle at the cuff.
    sx = gx - 1 if strap_left else gx + 13
    pygame.draw.circle(surf, _BLACK, (sx, gy + 13), 3)
    pygame.draw.circle(surf, _GOLD, (sx, gy + 13), 3, 1)


def _paint(surf, wing_angle_deg):
    # ── black cleats + lime socks at the feet ─────────────────────────────────
    # Sock = lime column with a black stripe; cleat = black boot mass with a
    # studded sole keyline as the bottom of the silhouette.
    for fx in (24, 34):
        pygame.draw.rect(surf, _LIME, (fx - 2, 60, 6, 6))           # sock
        pygame.draw.line(surf, _BLACK, (fx - 2, 62), (fx + 3, 62), 1)  # sock stripe
        pygame.draw.rect(surf, _GREEN_D, (fx - 1, 60, 2, 2))        # shin-guard bulge hint
        pygame.draw.rect(surf, _BLACK, (fx - 3, 65, 9, 5), border_radius=2)   # boot
        pygame.draw.rect(surf, _OUTLINE, (fx - 3, 68, 9, 2), border_radius=1)  # sole/studs
    pygame.draw.circle(surf, _OUTLINE, (24, 70), 1)   # stud dots
    pygame.draw.circle(surf, _OUTLINE, (38, 70), 1)

    # ── black shorts waistband at the tail base ───────────────────────────────
    pygame.draw.line(surf, _BLACK, (8, PARROT_DY + 28), (22, PARROT_DY + 32), 4)
    pygame.draw.line(surf, (52, 52, 56), (9, PARROT_DY + 28), (20, PARROT_DY + 31), 1)

    # ── chevron yoke: a black V across the shoulders + "1" on the chest ───────
    # The V connects the wing roots down to a collar point, framing the number.
    yoke_l = (HX - 22, HY + 4)
    yoke_pt = (HX - 10, HY + 16)
    yoke_r = (HX - 1, HY + 3)
    pygame.draw.lines(surf, _BLACK, False, [yoke_l, yoke_pt, yoke_r], 3)
    pygame.draw.lines(surf, (54, 54, 58), False,
                      [(yoke_l[0] + 1, yoke_l[1] - 1), yoke_pt,
                       (yoke_r[0] - 1, yoke_r[1] - 1)], 1)
    # Black collar notch at the neck so the yoke ties into a jersey crew-neck.
    pygame.draw.line(surf, _BLACK, (HX - 6, HY + 1), (HX + 2, HY + 2), 3)

    # Chest "1": a simple black digit column with a serifed foot + flag.
    nx, ny = HX - 12, HY + 7
    pygame.draw.rect(surf, _BLACK, (nx, ny, 3, 9))             # stem
    pygame.draw.line(surf, _BLACK, (nx - 2, ny + 2), (nx, ny), 2)  # flag
    pygame.draw.line(surf, _BLACK, (nx - 2, ny + 9), (nx + 5, ny + 9), 2)  # foot
    pygame.draw.line(surf, _WHITE, (nx + 1, ny + 1), (nx + 1, ny + 7), 1)  # gloss

    # ── padded gloves at each wingtip — the hero tell ─────────────────────────
    _padded_glove(surf, 4, 38, strap_left=True)    # back/left wingtip
    _padded_glove(surf, 48, 40, strap_left=False)  # near/right wingtip
    # Black cuff bands joining each glove to the lime sleeve.
    pygame.draw.rect(surf, _BLACK, (3, 50, 14, 3), border_radius=1)
    pygame.draw.rect(surf, _BLACK, (47, 52, 14, 3), border_radius=1)

    # ── goalkeeper cap: lime peaked crown + flat black brim ───────────────────
    cy = CROWN_Y
    # Brim FIRST (sits under the crown front edge): a flat black peak poking
    # LEFT off the head — the instant goalie-cap silhouette tell.
    brim = [(HX - 16, cy + 4), (HX - 2, cy + 1), (HX + 8, cy + 4),
            (HX - 2, cy + 6), (HX - 16, cy + 7)]
    pygame.draw.polygon(surf, _OUTLINE, brim)
    pygame.draw.polygon(surf, _BLACK,
                        [(HX - 15, cy + 4), (HX - 2, cy + 2), (HX + 7, cy + 4),
                         (HX - 2, cy + 5), (HX - 15, cy + 6)])
    pygame.draw.line(surf, (60, 60, 64), (HX - 14, cy + 4), (HX + 5, cy + 4), 1)

    # Rounded lime crown dome above CROWN_Y, tilted a touch on the head.
    dome = [(HX - 11, cy + 3), (HX - 9, cy - 5), (HX - 2, cy - 9),
            (HX + 6, cy - 7), (HX + 11, cy - 1), (HX + 12, cy + 4)]
    pygame.draw.polygon(surf, _GREEN_D, [(x, y + 1) for x, y in dome])  # shadow seat
    pygame.draw.polygon(surf, _LIME, dome)
    # Crown panel seams + a top button.
    pygame.draw.line(surf, _LIME_D, (HX - 2, cy - 8), (HX - 1, cy + 3), 1)
    pygame.draw.line(surf, _LIME_D, (HX + 5, cy - 6), (HX + 2, cy + 3), 1)
    pygame.draw.line(surf, _LIME_H, (HX - 7, cy - 3), (HX - 3, cy - 7), 1)  # lit panel
    pygame.draw.circle(surf, _GREEN_D, (HX - 1, cy - 8), 2)
    pygame.draw.circle(surf, _LIME_H, (HX - 2, cy - 9), 1)
    # Black hat band where the crown meets the brim.
    pygame.draw.line(surf, _BLACK, (HX - 11, cy + 3), (HX + 11, cy + 3), 2)


build = store_skins._make_skin(_paint, base_fn=_lime_base)
