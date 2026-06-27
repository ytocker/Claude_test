"""SOCCER redesign — design_3 EL CAPITÁN (exploration only).

The Argentina-style captain: Pip in a vertical sky-blue / white striped
match shirt with a navy V-collar and squad number, a white headband, and
the hero tell — a bright GOLD captain's armband high on one wing. Navy
cleats with a white stud row and white socks with a sky-blue turnover
finish the kit. The body is re-plumaged to a striped strip through the
palette system: body_main sky-blue + body_chest white, wing_main
sky-blue + wing_tip white — so the macaw already reads two-tone before
the painted columns even land, and the GOLD armband owns the 40px read
against the cool blue/white field.

Scratch builder — NOT registered in store_skins.BUILDERS. Production art
is untouched until a winner is picked.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, PARROT_DY
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette ──────────────────────────────────────────────────────────────────
_SKY      = (127, 182, 230)        # #7FB6E6 Albiceleste sky-blue
_SKY_D    = (86, 138, 190)         # cooler shadow so the blue holds shape
_SKY_H    = (176, 214, 245)
_WHITE    = (255, 255, 255)
_WHITE_D  = (214, 224, 236)        # off-white shadow for the white stripes
_NAVY     = (19, 41, 75)           # #13294B collar / number / boots
_NAVY_H   = (54, 84, 130)
_GOLD     = (232, 184, 75)         # #E8B84B captain armband
_GOLD_D   = (176, 132, 40)
_GOLD_H   = (255, 224, 150)
_OUT      = (10, 26, 51)           # #0A1A33 outline value
_BLACK    = (24, 24, 30)           # hair tuft

# Striped re-plumage: the body alternates sky-blue (main/belly) and white
# (chest), and the wing reads sky-blue main with white feather tips, so the
# bird is already a two-tone match strip before the painted stripe columns
# land. Beak stays warm-neutral; lenses dropped so the headband + bare eye
# own the face. Foot is navy to anchor the cleats.
_CAP_PAL = _pal(
    tail=[(86, 138, 190), (127, 182, 230), (214, 224, 236), (255, 255, 255)],
    tail_line=_SKY_D,
    body_shadow=_SKY_D,
    body_main=_SKY,
    body_chest=_WHITE,
    body_belly=(190, 214, 238),
    sheen=(255, 255, 255, 110),
    wing_main=_SKY,
    wing_dark=_SKY_D,
    wing_tip=_WHITE,
    wing_secondary=None,
    wing_highlight=_WHITE,
    head_shadow=_SKY_D,
    head_main=_SKY,
    head_cheek=_SKY_H,
    head_crown=(190, 214, 238),
    lens_frame=(190, 214, 238),
    lens_body=(40, 60, 90),
    lens_tint=None,
    lens_glint=None,
    beak_main=(220, 200, 168),
    beak_dark=(150, 130, 100),
    beak_gloss=(245, 235, 215),
    foot=_NAVY,
)


def _striped_base(angle_deg):
    # Two-tone (sky/white) bird, no aviators — the headband owns the head.
    return _build_parrot_with_palette(angle_deg, _CAP_PAL, draw_lenses=False)


def _stripe_columns(surf):
    """Wide vertical white columns over the sky-blue body, clipped to the
    body silhouette so the shirt reads as alternating sky/white stripes.

    Stripes are kept WIDE (4px) — thin 1px stripes shimmer and dissolve at
    40px in motion, so a few bold columns read far better than many fine
    ones. The columns are stamped on a scratch surface and intersected with
    a body mask so paint never leaks past the silhouette into open sky.
    """
    BCX, BCY = 32, 52                # body centre in composite space
    cols = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    # White stripe columns sitting between the blue ones; the chest already
    # carries a white field, so these extend the stripe rhythm out to the
    # flanks where the body is sky-blue.
    for x in (BCX - 13, BCX - 4, BCX + 5, BCX + 14):
        pygame.draw.rect(cols, _WHITE, (x, BCY - 11, 4, 26))
        pygame.draw.line(cols, _WHITE_D, (x, BCY - 11), (x, BCY + 14), 1)
    # Intersect with the painted-body mask so columns stay on the shirt.
    mask = pygame.mask.from_surface(surf, 8).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    cols.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(cols, (0, 0))


def _paint(surf, wing_angle_deg):
    BCX, BCY = 32, 52

    # ── vertical stripe columns on the shirt (drawn first, under accents) ─────
    _stripe_columns(surf)

    # ── back squad "5": a navy block hinted between the stripes, high on the
    #     back so it peeks past the wing root the way a shirt number does ──────
    pygame.draw.rect(surf, _NAVY, (BCX - 12, BCY - 9, 7, 11), border_radius=1)
    pygame.draw.line(surf, _NAVY_H, (BCX - 11, BCY - 8), (BCX - 6, BCY - 8), 1)

    # ── navy V-neck collar: a shallow V notch at the top of the chest ─────────
    vcx = BCX + 4
    pygame.draw.line(surf, _NAVY, (vcx - 7, BCY - 11), (vcx, BCY - 4), 3)
    pygame.draw.line(surf, _NAVY, (vcx + 7, BCY - 11), (vcx, BCY - 4), 3)
    pygame.draw.line(surf, _NAVY_H, (vcx - 6, BCY - 11), (vcx, BCY - 5), 1)

    # ── striped sleeve cuff at the near wingtip — a short sky/white band so the
    #     kit's stripe motif reaches the wing extremity ────────────────────────
    cfx, cfy = BCX + 14, BCY - 7
    pygame.draw.line(surf, _SKY_D, (cfx - 4, cfy + 3), (cfx + 4, cfy - 3), 5)
    pygame.draw.line(surf, _WHITE, (cfx - 3, cfy + 3), (cfx, cfy), 2)
    pygame.draw.line(surf, _SKY, (cfx, cfy), (cfx + 3, cfy - 3), 2)

    # ── navy cleats with a white stud row + white socks with a sky turnover ───
    for fx in (BCX - 6, BCX):
        # White sock with a sky-blue turnover band just above the boot.
        pygame.draw.line(surf, _WHITE, (fx, BCY + 9), (fx - 1, BCY + 14), 4)
        pygame.draw.line(surf, _SKY, (fx, BCY + 10), (fx - 1, BCY + 12), 4)
        pygame.draw.line(surf, _WHITE, (fx, BCY + 12), (fx - 1, BCY + 14), 3)
        # Navy cleat: a forward-pointing boot mass with a white stud row.
        boot = [(fx - 3, BCY + 14), (fx + 5, BCY + 14),
                (fx + 6, BCY + 18), (fx - 4, BCY + 18)]
        pygame.draw.polygon(surf, _NAVY, boot)
        pygame.draw.line(surf, _NAVY_H, (fx - 2, BCY + 15), (fx + 4, BCY + 15), 1)
        for sx in (fx - 2, fx + 1, fx + 4):
            pygame.draw.circle(surf, _WHITE, (sx, BCY + 18), 1)

    # ── HEAD: white headband across the forehead, black hair tuft above ───────
    hb_y = CROWN_Y + 2
    pygame.draw.rect(surf, _WHITE, (HX - 12, hb_y, 22, 4), border_radius=2)
    pygame.draw.line(surf, _WHITE_D, (HX - 11, hb_y + 3), (HX + 9, hb_y + 3), 1)
    pygame.draw.line(surf, _SKY, (HX - 11, hb_y + 1), (HX + 9, hb_y + 1), 1)
    # Small black hair tuft peeking up over the band.
    for i, (tx, th) in enumerate(((HX - 4, 5), (HX, 6), (HX + 4, 4))):
        pygame.draw.line(surf, _BLACK, (tx, hb_y), (tx - 1, hb_y - th), 2)

    # ── CAPTAIN'S ARMBAND — the hero tell: a bright GOLD band high on the upper
    #     wing, with a navy "C" stamped on it so it reads as a captain band ────
    ax, ay, aw, ah = 8, 35, 11, 5
    pygame.draw.rect(surf, _GOLD_D, (ax - 1, ay - 1, aw + 2, ah + 2), border_radius=3)
    pygame.draw.rect(surf, _GOLD, (ax, ay, aw, ah), border_radius=2)
    pygame.draw.line(surf, _GOLD_H, (ax + 1, ay + 1), (ax + aw - 2, ay + 1), 1)
    # Navy "C" mark — a small open arc on the gold band.
    cmx, cmy = ax + aw // 2, ay + ah // 2
    pygame.draw.arc(surf, _NAVY, (cmx - 3, cmy - 3, 6, 6),
                    0.6, 5.0, 2)

    # ── continuous outline so the cool white/sky kit holds on a pale day sky ──
    mask = pygame.mask.from_surface(surf, threshold=10)
    line = mask.to_surface(setcolor=_OUT, unsetcolor=(0, 0, 0, 0))
    key = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        key.blit(line, (dx, dy))
    key.blit(surf, (0, 0))
    surf.blit(key, (0, 0))


build = store_skins._make_skin(_paint, base_fn=_striped_base)
