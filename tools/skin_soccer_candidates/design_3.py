"""SOCCER redesign — design_3 EL CAPITÁN (exploration only).

The Argentina-style captain: Pip in a vertical azure / white striped match
shirt with a navy V-collar and a navy squad "5", a white crown headband, and
the hero tell — a bright GOLD captain's armband ringing the near wing. Navy
cleats with a white stud row and white socks finish the kit. The body is
re-plumaged to a darker true-azure through the palette system so the bird
reads clearly against the pale day sky, with white feather tips carrying the
stripe two-tone before the painted columns even land.

R2 fix-list (each tied to the 40px read):
  * Azure body deepened to a true medium azure (~#3F8FD6) so the bird stops
    camouflaging blue-on-blue against the ~#87CEEB day sky; a 1px navy keyline
    rings the whole silhouette so it holds on day AND night.
  * Stripes cut to MAX 3 white + 2 blue fat columns (≥3px), clipped to the
    body mask, so the kit reads as bold blocks instead of shimmering static.
  * The gold armband is repositioned as a proper band ringing the near wing
    high on the body — the single warm hero accent, navy-outlined to pop off
    both blue and white.
  * The headband is a flat white rectangle across the crown with a navy edge,
    sized to survive 40px.
  * The lower-back tan/gold patch and stray marks are dropped; the only marks
    are the navy "5" + the gold armband.

Scratch builder — NOT registered in store_skins.BUILDERS. Production art is
untouched until a winner is picked.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, PARROT_DY
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette ──────────────────────────────────────────────────────────────────
_AZURE    = (63, 143, 214)         # #3F8FD6 true medium azure — darker than sky
_AZURE_D  = (40, 102, 162)         # cooler shadow so the blue holds shape
_AZURE_H  = (118, 178, 232)
_WHITE    = (255, 255, 255)
_WHITE_D  = (208, 220, 234)        # off-white shadow for the white stripes
_NAVY     = (19, 41, 75)           # #13294B collar / number / boots / keyline
_NAVY_H   = (54, 84, 130)
_GOLD     = (236, 188, 78)         # #ECBC4E captain armband — the one warm note
_GOLD_D   = (172, 128, 38)
_GOLD_H   = (255, 226, 152)
_OUT      = (12, 28, 54)           # #0C1C36 navy keyline value
_BLACK    = (24, 24, 30)           # hair tuft

# Darker-azure re-plumage: every blue slot is the true medium azure so the
# bird reads clearly darker than the day sky; white feather tips seed the
# stripe two-tone before the painted columns land. Beak stays warm-neutral;
# lenses dropped so the headband + bare eye own the face. Foot is navy.
_CAP_PAL = _pal(
    tail=[(40, 102, 162), (63, 143, 214), (208, 220, 234), (255, 255, 255)],
    tail_line=_AZURE_D,
    body_shadow=_AZURE_D,
    body_main=_AZURE,
    body_chest=_WHITE,
    body_belly=(150, 190, 230),
    sheen=(255, 255, 255, 90),
    wing_main=_AZURE,
    wing_dark=_AZURE_D,
    wing_tip=_WHITE,
    wing_secondary=None,
    wing_highlight=_WHITE,
    head_shadow=_AZURE_D,
    head_main=_AZURE,
    head_cheek=_AZURE_H,
    head_crown=(150, 190, 230),
    lens_frame=(150, 190, 230),
    lens_body=(40, 60, 90),
    lens_tint=None,
    lens_glint=None,
    beak_main=(220, 200, 168),
    beak_dark=(150, 130, 100),
    beak_gloss=(245, 235, 215),
    foot=_NAVY,
)


def _striped_base(angle_deg):
    # Two-tone (azure/white) bird, no aviators — the headband owns the head.
    return _build_parrot_with_palette(angle_deg, _CAP_PAL, draw_lenses=False)


def _stripe_columns(surf):
    """Bold vertical stripe columns over the azure body, clipped to the body
    silhouette so the shirt reads as alternating azure/white blocks.

    R2: capped to MAX 3 white + 2 azure FAT columns (4px each). Thin many
    stripes shimmer into static at 40px in motion; a few wide blocks read as
    a real kit. The columns are stamped on a scratch surface and intersected
    with a body mask so paint never leaks past the silhouette into open sky.
    """
    BCX, BCY = 32, 52                # body centre in composite space
    cols = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    # Three fat WHITE columns alternating with two fat AZURE columns: the
    # rhythm is W-A-W-A-W across the chest/flanks so the kit reads as five
    # bold vertical blocks instead of fine pinstripes.
    white_xs = (BCX - 12, BCX, BCX + 12)
    azure_xs = (BCX - 6, BCX + 6)
    for x in azure_xs:
        pygame.draw.rect(cols, _AZURE, (x, BCY - 11, 4, 26))
        pygame.draw.line(cols, _AZURE_D, (x, BCY - 11), (x, BCY + 14), 1)
    for x in white_xs:
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

    # ── back squad "5": a navy block high on the back so it peeks past the
    #     wing root the way a shirt number does — the one cool readable mark ───
    pygame.draw.rect(surf, _NAVY, (BCX - 12, BCY - 9, 7, 11), border_radius=1)
    pygame.draw.line(surf, _NAVY_H, (BCX - 11, BCY - 8), (BCX - 6, BCY - 8), 1)

    # ── navy V-neck collar: a shallow V notch at the top of the chest ─────────
    vcx = BCX + 4
    pygame.draw.line(surf, _NAVY, (vcx - 7, BCY - 11), (vcx, BCY - 4), 3)
    pygame.draw.line(surf, _NAVY, (vcx + 7, BCY - 11), (vcx, BCY - 4), 3)
    pygame.draw.line(surf, _NAVY_H, (vcx - 6, BCY - 11), (vcx, BCY - 5), 1)

    # ── navy cleats with a white stud row + white socks ───────────────────────
    for fx in (BCX - 6, BCX):
        # White sock just above the boot (azure turnover dropped — at 40px it
        # only muddied; clean white reads better against the navy cleat).
        pygame.draw.line(surf, _WHITE, (fx, BCY + 9), (fx - 1, BCY + 14), 4)
        pygame.draw.line(surf, _WHITE_D, (fx, BCY + 12), (fx - 1, BCY + 14), 3)
        # Navy cleat: a forward-pointing boot mass with a white stud row.
        boot = [(fx - 3, BCY + 14), (fx + 5, BCY + 14),
                (fx + 6, BCY + 18), (fx - 4, BCY + 18)]
        pygame.draw.polygon(surf, _NAVY, boot)
        pygame.draw.line(surf, _NAVY_H, (fx - 2, BCY + 15), (fx + 4, BCY + 15), 1)
        for sx in (fx - 2, fx + 1, fx + 4):
            pygame.draw.circle(surf, _WHITE, (sx, BCY + 18), 1)

    # ── HEAD: a real white headband across the crown, black hair tuft above ───
    #     A flat white rectangle at CROWN_Y+2, 4px tall, navy-edged so it
    #     survives 40px as a clear band rather than a smudge.
    hb_y = CROWN_Y + 2
    hb_x, hb_w = HX - 13, 24
    pygame.draw.rect(surf, _NAVY, (hb_x - 1, hb_y - 1, hb_w + 2, 6), border_radius=2)
    pygame.draw.rect(surf, _WHITE, (hb_x, hb_y, hb_w, 4), border_radius=1)
    pygame.draw.line(surf, _AZURE, (hb_x + 1, hb_y + 1), (hb_x + hb_w - 2, hb_y + 1), 1)
    # Small black hair tuft peeking up over the band.
    for tx, th in ((HX - 5, 5), (HX - 1, 6), (HX + 3, 4)):
        pygame.draw.line(surf, _BLACK, (tx, hb_y), (tx - 1, hb_y - th), 2)

    # ── CAPTAIN'S ARMBAND — the hero tell: a bright GOLD band wrapping the near
    #     wing high on the body, navy-outlined so it pops off blue AND white.
    #     Drawn as a rounded band with a navy "C" stamped on it. This is the
    #     ONLY warm note on the bird. ───────────────────────────────────────────
    ax, ay, aw, ah = BCX - 2, BCY - 13, 14, 6
    pygame.draw.rect(surf, _NAVY, (ax - 1, ay - 1, aw + 2, ah + 2), border_radius=3)
    pygame.draw.rect(surf, _GOLD_D, (ax, ay, aw, ah), border_radius=3)
    pygame.draw.rect(surf, _GOLD, (ax + 1, ay + 1, aw - 2, ah - 2), border_radius=2)
    pygame.draw.line(surf, _GOLD_H, (ax + 2, ay + 1), (ax + aw - 3, ay + 1), 1)
    # Navy "C" mark — a small open arc on the gold band.
    cmx, cmy = ax + aw // 2, ay + ah // 2
    pygame.draw.arc(surf, _NAVY, (cmx - 3, cmy - 3, 6, 6), 0.6, 5.0, 2)

    # ── continuous 1px NAVY keyline so the kit holds on a pale day sky ────────
    mask = pygame.mask.from_surface(surf, threshold=10)
    line = mask.to_surface(setcolor=_OUT, unsetcolor=(0, 0, 0, 0))
    key = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        key.blit(line, (dx, dy))
    key.blit(surf, (0, 0))
    surf.blit(key, (0, 0))


build = store_skins._make_skin(_paint, base_fn=_striped_base)
