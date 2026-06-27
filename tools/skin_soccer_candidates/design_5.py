"""SOCCER costume — design_5 THE DEFENDER (exploration only).

A blaugrana centre-back kit on Pip: a claret-and-blue vertical-halves jersey
with a gold round collar and a gold "4" on the back, claret sleeves with a blue
cuff band, blue shorts waistband, and — the hero tell — a pair of chunky pale
shin guards strapped over the lower legs, rolled claret socks above them, and
black cleats with gold studs. The whole macaw is re-plumaged so the body reads
as a CLARET jersey and the wing as a BLUE sleeve through the palette system, so
the kit's two-tone identity holds at 40px instead of fighting the scarlet bird.

The shin guards are the design's signature: two thick armour plates that no
other soccer costume carries, the lowest-and-brightest mass so they read as
the standout at thumbnail.

Scratch builder — NOT registered in store_skins.BUILDERS. Production art is
untouched until a winner is picked.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, PARROT_DY
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette ──────────────────────────────────────────────────────────────────
_CLARET    = (122, 31, 61)         # #7A1F3D claret jersey body
_CLARET_D  = (84, 20, 42)
_CLARET_H  = (168, 58, 92)
_BLUE      = (21, 54, 107)         # #15366B blaugrana blue
_BLUE_D    = (13, 36, 74)
_BLUE_H    = (62, 100, 162)
_GOLD      = (232, 184, 75)        # #E8B84B gold trim / number
_GOLD_D    = (176, 132, 40)
_GOLD_H    = (255, 224, 150)
_BOOT      = (26, 26, 26)          # #1A1A1A boots
_BOOT_H    = (70, 70, 74)
_OUTLINE   = (12, 8, 32)           # #0C0820 deep outline value
_PLATE     = (232, 232, 222)       # pale shin-guard armour
_PLATE_D   = (186, 186, 176)
_PLATE_H   = (255, 255, 252)
_SKIN_DK   = (44, 28, 20)          # dark hair / sweatband

# Full claret-and-blue re-plumage: the body slots become claret so the chest
# reads as the jersey, the wing slots become blue so the sleeve carries the
# second kit colour, and the tail alternates claret/blue. Lenses are dropped so
# the bare macaw face sits under the hair + sweatband; beak stays warm so Pip
# still reads as a parrot wearing a kit, not a recoloured blob.
_DEF_PAL = _pal(
    tail=[_CLARET_D, _BLUE_D, _CLARET, _BLUE],
    tail_line=_OUTLINE,
    body_shadow=_CLARET_D,
    body_main=_CLARET,
    body_chest=_CLARET_H,
    body_belly=(102, 26, 52),
    sheen=(255, 255, 255, 70),
    wing_main=_BLUE,
    wing_dark=_BLUE_D,
    wing_tip=_BLUE_H,
    wing_secondary=None,
    wing_highlight=_BLUE_H,
    head_shadow=_CLARET_D,
    head_main=_CLARET,
    head_cheek=_CLARET_H,
    head_crown=(102, 26, 52),
    lens_frame=(120, 40, 60),
    lens_body=(40, 20, 28),
    lens_tint=None,
    lens_glint=None,
    beak_main=(232, 168, 70),
    beak_dark=(150, 96, 30),
    beak_gloss=(255, 224, 150),
    foot=_BOOT,
)


def _defender_base(angle_deg):
    # Claret body / blue sleeve bird, no aviators — the brow + hair own the head.
    return _build_parrot_with_palette(angle_deg, _DEF_PAL, draw_lenses=False)


def _paint(surf, wing_angle_deg):
    # ── vertical halves: blue over the RIGHT half so the jersey is split
    #     claret(left) / blue(right). Clipped to the painted body silhouette so
    #     the colour stops at the bird's edge instead of squaring off. ─────────
    right = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.rect(right, _BLUE, (HX, HY - 5, 22, 74))
    pygame.draw.rect(right, _BLUE_H, (HX, HY - 5, 2, 74))   # centre seam highlight
    mask = pygame.mask.from_surface(surf, 8).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    right.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(right, (0, 0))

    # ── blue shorts waistband at the tail base (drawn before chest trim so the
    #     belly halves sit cleanly above it) ───────────────────────────────────
    pygame.draw.rect(surf, _BLUE_D, (16, HY + 22, 30, 6), border_radius=2)
    pygame.draw.rect(surf, _BLUE, (16, HY + 22, 30, 4), border_radius=2)
    pygame.draw.line(surf, _BLUE_H, (18, HY + 23), (44, HY + 23), 1)

    # ── gold sponsor bar across the chest — one thin bright rectangle ─────────
    pygame.draw.rect(surf, _GOLD_D, (HX - 8, HY + 13, 16, 5), border_radius=1)
    pygame.draw.rect(surf, _GOLD, (HX - 8, HY + 14, 16, 3), border_radius=1)
    pygame.draw.line(surf, _GOLD_H, (HX - 7, HY + 14), (HX + 6, HY + 14), 1)

    # ── gold "4" hint on the back jersey (claret left half, upper-back) ───────
    nx, ny = HX - 13, HY + 2
    pygame.draw.line(surf, _GOLD, (nx, ny), (nx, ny + 5), 2)        # left vert
    pygame.draw.line(surf, _GOLD, (nx, ny + 5), (nx + 5, ny + 5), 2)  # crossbar
    pygame.draw.line(surf, _GOLD, (nx + 4, ny - 1), (nx + 4, ny + 8), 2)  # right vert
    pygame.draw.line(surf, _GOLD_H, (nx + 4, ny - 1), (nx + 4, ny + 2), 1)

    # ── gold round collar: a bright ring at the neck so the kit reads from the
    #     front; sits over the chest just under the head ──────────────────────
    pygame.draw.circle(surf, _GOLD_D, (HX, HY + 5), 6, 2)
    pygame.draw.circle(surf, _GOLD, (HX, HY + 5), 6, 1)
    pygame.draw.line(surf, _GOLD_H, (HX - 4, HY + 1), (HX + 3, HY + 1), 1)

    # ── blue cuff band on the (near) right wing + a small sponsor-bar hint so
    #     the blue sleeve reads as a kitted arm, not bare plumage ─────────────
    pygame.draw.line(surf, _GOLD, (40, HY + 4), (47, HY + 1), 2)     # sleeve sponsor hint
    cuffx, cuffy = 47, HY + 2
    pygame.draw.line(surf, _BLUE_D, (cuffx - 5, cuffy + 3), (cuffx + 4, cuffy - 2), 5)
    pygame.draw.line(surf, _BLUE_H, (cuffx - 4, cuffy + 2), (cuffx + 3, cuffy - 3), 1)

    # ── short dark hair: a small cluster of dark blocks above the brow ────────
    for hx, hw in ((HX - 9, 4), (HX - 4, 5), (HX + 2, 5), (HX + 8, 3)):
        pygame.draw.rect(surf, _SKIN_DK, (hx, CROWN_Y - 3, hw, 4), border_radius=1)
    pygame.draw.line(surf, (66, 44, 32), (HX - 8, CROWN_Y - 2), (HX + 9, CROWN_Y - 2), 1)

    # ── thin black sweatband low on the brow ──────────────────────────────────
    pygame.draw.rect(surf, _SKIN_DK, (HX - 10, CROWN_Y + 4, 19, 3), border_radius=1)
    pygame.draw.line(surf, (96, 70, 54), (HX - 9, CROWN_Y + 4), (HX + 7, CROWN_Y + 4), 1)

    # ── LEGS — the hero stack, drawn from the body down: rolled claret socks,
    #     chunky pale shin guards, then black cleats with gold studs ──────────
    for legx in (22, 35):
        # Rolled claret sock band just above the guard — a thick claret cuff.
        pygame.draw.rect(surf, _CLARET_D, (legx - 1, 58, 10, 4), border_radius=2)
        pygame.draw.rect(surf, _CLARET, (legx, 58, 8, 3), border_radius=2)
        pygame.draw.line(surf, _CLARET_H, (legx, 58), (legx + 6, 58), 1)

        # Prominent shin guard: a chunky pale rounded plate over the lower leg.
        # This is the standout tell — thick, bright, clearly armour at 40px.
        pygame.draw.rect(surf, _OUTLINE, (legx - 1, 61, 10, 13), border_radius=4)
        pygame.draw.rect(surf, _PLATE_D, (legx, 62, 8, 12), border_radius=4)
        pygame.draw.rect(surf, _PLATE, (legx + 1, 62, 6, 10), border_radius=3)
        pygame.draw.line(surf, _PLATE_H, (legx + 2, 63), (legx + 2, 70), 1)  # centre ridge
        # Two strap ticks crossing the plate so it reads as strapped-on armour.
        pygame.draw.line(surf, _PLATE_D, (legx, 65), (legx + 7, 65), 1)
        pygame.draw.line(surf, _PLATE_D, (legx, 70), (legx + 7, 70), 1)

        # Black cleat under the plate with two gold stud dots.
        pygame.draw.rect(surf, _BOOT, (legx - 1, 73, 11, 5), border_radius=2)
        pygame.draw.line(surf, _BOOT_H, (legx, 73), (legx + 8, 73), 1)
        pygame.draw.circle(surf, _GOLD, (legx + 1, 77), 1)
        pygame.draw.circle(surf, _GOLD, (legx + 7, 77), 1)


build = store_skins._make_skin(_paint, base_fn=_defender_base)
