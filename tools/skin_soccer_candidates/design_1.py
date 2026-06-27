"""SOCCER redesign — design_1 THE STRIKER (exploration only).

A Brazil-style canary-yellow striker kit on Pip the macaw. The whole bird is
re-plumaged through the palette system to a canary-yellow jersey so the body
reads as a kit, not bare scarlet; the dark-green collar/cuffs/socks/waistband
carry the team trim, and an oversized white "10" owns the chest as the single
hero read at 40px. The number is built from chunky white rectangles so the
bold digit survives downscale where a thin outlined glyph would smear.

Re-skin priorities, in order of value at 40px:
  * a yellow-jersey blob bird (palette re-plumage),
  * a thick dark-green crew collar ring at the neck — the one shape that says
    "team kit" instantly,
  * a fat white "10" on the chest (the hero),
  * green socks + white cleats anchoring the feet with a black sole + 3 studs,
  * a black hair tuft above the crown and green cuff bands at the wingtips.

Scratch builder — NOT registered in store_skins.BUILDERS. Production art is
untouched until a winner is picked.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, PARROT_DY
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette ──────────────────────────────────────────────────────────────────
_CANARY     = (245, 208, 0)        # #F5D000 jersey yellow
_CANARY_H   = (255, 232, 90)       # jersey highlight
_CANARY_D   = (196, 162, 0)        # jersey shadow / seam
_GREEN      = (10, 122, 60)        # #0A7A3C dark-green trim
_GREEN_H    = (40, 168, 95)
_GREEN_D    = (8, 88, 44)
_WHITE      = (255, 255, 255)      # boots / number
_WHITE_SH   = (214, 220, 226)
_BLACK      = (26, 26, 26)         # #1A1A1A hair / studs / sole
_OUTLINE    = (11, 58, 30)         # #0B3A1E green outline

# Full canary-yellow kit re-plumage. Body/chest/belly + wings + head all go
# jersey-yellow so the bird is one bright kit; the deepest CANARY_D owns the
# line work, tail is green (the shorts colour) and feet read white as the boot
# base. Lenses kept off — the chest number, not the face, owns the read. Beak
# stays a warm macaw orange so Pip still reads as a parrot under the kit.
_STRIKER_PAL = _pal(
    tail=[(8, 100, 50), (10, 122, 60), (200, 170, 10), (245, 208, 0)],
    tail_line=_GREEN_D,
    body_shadow=(196, 162, 0),
    body_main=_CANARY,
    body_chest=(255, 220, 40),
    body_belly=(235, 198, 10),
    sheen=(255, 255, 255, 90),
    wing_main=(232, 196, 0),
    wing_dark=_CANARY_D,
    wing_tip=(255, 224, 70),
    wing_secondary=None,
    wing_highlight=_CANARY_H,
    head_shadow=(200, 166, 0),
    head_main=_CANARY,
    head_cheek=(255, 224, 80),
    head_crown=(255, 220, 60),
    lens_frame=(200, 166, 0),
    lens_body=(150, 124, 0),
    lens_tint=None,
    lens_glint=None,
    beak_main=(255, 168, 40),
    beak_dark=(176, 100, 18),
    beak_gloss=(255, 214, 130),
    foot=_WHITE,
)


def _striker_base(angle_deg):
    # Canary-kit bird, no aviators — the chest "10" owns the read.
    return _build_parrot_with_palette(angle_deg, _STRIKER_PAL, draw_lenses=False)


def _digit_one(surf, x, y, w, h):
    """Chunky white '1' — a bold vertical bar on a wide serif foot so it never
    reads as a stray line at 40px. (x,y) is the top-left of the vertical bar."""
    foot_h = max(3, h // 5)
    foot_w = w * 2 + 2
    # outline underlay (one dark keyline so white holds on yellow)
    pygame.draw.rect(surf, _OUTLINE, (x - 1, y - 1, w + 2, h + 2))
    pygame.draw.rect(surf, _OUTLINE, (x - w + 1, y + h - foot_h - 1, foot_w, foot_h + 2))
    # white fills
    pygame.draw.rect(surf, _WHITE, (x, y, w, h))
    pygame.draw.rect(surf, _WHITE, (x - w + 2, y + h - foot_h, foot_w - 2, foot_h))


def _digit_zero(surf, x, y, w, h):
    """Chunky white '0' — a bold ring (outer white block minus an inner punch)
    so the hole survives downscale without smearing shut."""
    pygame.draw.rect(surf, _OUTLINE, (x - 1, y - 1, w + 2, h + 2), border_radius=4)
    pygame.draw.rect(surf, _WHITE, (x, y, w, h), border_radius=4)
    inset = max(3, w // 3)
    # Punch the hole back to the jersey yellow so the ring reads as a "0".
    pygame.draw.rect(surf, _CANARY, (x + inset, y + inset,
                                     w - inset * 2, h - inset * 2), border_radius=2)


def _paint(surf, wing_angle_deg):
    BCX, BCY = 32, 52       # body centre in composite space (32,32)+PARROT_DY

    # ── green cuff bands at the wingtips: the trim reaches the wings ──────────
    pygame.draw.line(surf, _GREEN_D, (45, 44), (52, 41), 5)
    pygame.draw.line(surf, _GREEN, (45, 43), (52, 40), 3)
    pygame.draw.line(surf, _GREEN_H, (46, 42), (51, 40), 1)

    # ── white cleats + green socks at the feet (drawn first, anchor the base) ─
    # Two boots side by side below the body; each is a white toe-box with a hard
    # black sole line and a 3-stud row, with a green sock cuff above. The sock's
    # white horizontal pad band hints at a shin guard.
    for fx in (BCX - 7, BCX + 4):
        # green sock with white pad band
        pygame.draw.rect(surf, _GREEN_D, (fx - 1, BCY + 8, 8, 8), border_radius=2)
        pygame.draw.rect(surf, _GREEN, (fx, BCY + 8, 6, 7), border_radius=2)
        pygame.draw.rect(surf, _WHITE, (fx, BCY + 10, 6, 2))
        # white cleat (toe-box angled forward)
        boot = [(fx - 2, BCY + 15), (fx + 6, BCY + 15),
                (fx + 9, BCY + 19), (fx - 2, BCY + 19)]
        pygame.draw.polygon(surf, _WHITE_SH, [(px, py + 1) for px, py in boot])
        pygame.draw.polygon(surf, _WHITE, boot)
        # hard black sole as the literal bottom of the boot
        pygame.draw.line(surf, _BLACK, (fx - 2, BCY + 19), (fx + 9, BCY + 19), 2)
        # 3-stud row poking below the sole
        for sx in (fx, fx + 3, fx + 6):
            pygame.draw.circle(surf, _BLACK, (sx, BCY + 20), 1)

    # ── green shorts waistband band at the tail/hip junction ─────────────────
    pygame.draw.line(surf, _GREEN_D, (15, BCY + 6), (26, BCY + 10), 5)
    pygame.draw.line(surf, _GREEN, (15, BCY + 5), (26, BCY + 9), 3)
    pygame.draw.line(surf, _GREEN_H, (16, BCY + 4), (25, BCY + 8), 1)

    # ── thick dark-green crew collar ring at the neck ────────────────────────
    # A bold crew ring at the head/chest junction — the one shape that instantly
    # says "team jersey". Kept high and slim so it frames the neck rather than
    # sprawling over the chest where the number lives. Drawn before the number.
    cnx, cny = HX - 3, HY + 10
    pygame.draw.ellipse(surf, _GREEN_D, (cnx - 10, cny - 3, 22, 10))
    pygame.draw.ellipse(surf, _GREEN, (cnx - 9, cny - 3, 20, 8))
    # punch the neck hole back to yellow so it reads as a ring, not a bib
    pygame.draw.ellipse(surf, _CANARY, (cnx - 5, cny - 1, 12, 5))
    pygame.draw.line(surf, _GREEN_H, (cnx - 7, cny - 1), (cnx + 8, cny - 2), 1)

    # ── the hero: oversized white "10" centred on the chest ──────────────────
    # Sized so the pair owns the chest at 40px. Built from chunky white blocks
    # over a green keyline so the bold digits hold on the yellow jersey.
    num_h = 18
    digit_w = 5
    nx, ny = BCX - 11, BCY - 8
    _digit_one(surf, nx, ny, digit_w, num_h)
    _digit_zero(surf, nx + digit_w + 4, ny, 11, num_h)

    # ── black hair tuft over the crown ───────────────────────────────────────
    # A short spiky black fringe above the crown so the head reads as a player,
    # breaking the yellow crown outline.
    tx, ty = HX, CROWN_Y
    pygame.draw.ellipse(surf, _BLACK, (tx - 9, ty - 2, 18, 7))
    for i, dx in enumerate((-7, -3, 1, 5)):
        h = 5 if i % 2 == 0 else 7
        pygame.draw.polygon(surf, _BLACK, [(tx + dx, ty + 1),
                                           (tx + dx + 4, ty + 1),
                                           (tx + dx + 2, ty - h)])
    pygame.draw.line(surf, (70, 70, 70), (tx - 6, ty - 1), (tx + 4, ty - 1), 1)


build = store_skins._make_skin(_paint, base_fn=_striker_base)
