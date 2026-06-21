"""BALLOON BASKET parcel cosmetic (MID tier).

A tiny hot-air-balloon gondola: a fat candy-STRIPED DOME canopy above a
small square wicker BASKET, joined by two short cords. At 22px the read is
the "lollipop on a box" outline — a big round striped dome dominating a
little box below, the most scene-like of the mid parcels.

The dome carries the glyph: it is wide, tall, and dark-keylined so the
round silhouette survives the smoothscale and the bank. Cords are kept
SHORT and thin so basket + dome nearly touch — the thin cords vanish at
22px and the dome/box pairing does the reading. Stripes are baked as a
handful of bold vertical bands (fine stripes die at this size) so the
candy tell holds even inverted across the −25°→90° tilt arc.

The canopy is TEAL/azure + cream, NOT red: carried below Pip the parcel
sits against his red body, and a red dome merged into him into a bauble.
Cool teal stripes snap off the warm red bird instantly while still reading
"candy", and the dome is grown + lowered so its clear lower two-thirds
dominates the silhouette under Pip rather than hiding in his chest.
"""
import pygame

from game.parrot import _lerp_color


# Day palette per brief. Cool TEAL/azure canopy to break off Pip's red body.
STRIPE_TEAL = (38, 168, 174)      # #26A8AE candy teal band
STRIPE_TEAL_HI = (96, 214, 214)   # lit teal on the dome crown
STRIPE_TEAL_LO = (24, 124, 134)   # shaded teal toward the dome base
CREAM = (243, 236, 220)           # #F3ECDC cream band
CREAM_HI = (252, 248, 240)        # cream crown highlight
CREAM_LO = (210, 200, 180)        # shaded cream toward the dome base
BASKET = (154, 112, 56)           # #9A7038 wicker basket
BASKET_HI = (190, 146, 84)        # lit basket top edge
BASKET_LO = (120, 86, 42)         # shaded basket belly
WEAVE = (96, 68, 34)              # darker weave hatch on the basket
OUTLINE = (24, 40, 44)            # dark teal-leaning keyline for the bright sky
CORD = (60, 40, 22)               # rigging cord (dark so it survives day sky)
WARM_EDGE = (250, 222, 150)       # warm catch on the dome bottom (holds on night sky)


def build(mode: str = "normal") -> pygame.Surface:
    # mode is ignored — the balloon keeps its festive look across power-ups.
    SIZE = 44
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    cx = SIZE // 2

    # Vertical stack geometry. The dome is grown ~28% and its centre dropped so
    # its lower two-thirds clears Pip's belly when carried — the dome, not the
    # basket, has to be the dominant clear shape below the bird.
    dome_cx, dome_cy = cx, 21       # dome centre (lowered vs. round 1)
    dome_rx, dome_ry = 20, 19       # fat round canopy (grown for dominance)
    basket_w, basket_h = 14, 12
    basket_top = 37
    basket_rect = pygame.Rect(cx - basket_w // 2, basket_top, basket_w, basket_h)

    # Drop shadow grounds the whole balloon under Pip.
    sh = pygame.Surface((24, 7), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 14, 120), sh.get_rect())
    surf.blit(sh, (cx - 12, basket_rect.bottom - 2))

    # CORDS first so the basket rim and dome skirt overlap their ends — the
    # cords then read as tucked into both, not floating between. Kept short:
    # only the small gap between dome base and basket top.
    cord_top = dome_cy + dome_ry - 3
    for sx, bx in ((-8, -basket_w // 2 + 2), (8, basket_w // 2 - 2)):
        pygame.draw.line(surf, CORD, (dome_cx + sx, cord_top),
                         (cx + bx, basket_top + 1), 2)

    # ── DOME canopy ──────────────────────────────────────────────────────
    # Dark keyline ellipse behind the stripe fill bakes the bold round
    # silhouette so it pops against the bright day sky and holds when banked.
    out_rect = pygame.Rect(dome_cx - dome_rx - 2, dome_cy - dome_ry - 2,
                           (dome_rx + 2) * 2, (dome_ry + 2) * 2)
    pygame.draw.ellipse(surf, OUTLINE, out_rect)

    dome_rect = pygame.Rect(dome_cx - dome_rx, dome_cy - dome_ry,
                            dome_rx * 2, dome_ry * 2)

    # Candy stripes as bold vertical bands. Each band is built full-height
    # with a top→bottom shade so the canopy looks rounded, then all bands are
    # clipped to the dome ellipse in one masked blit. Few wide bands keep the
    # candy read alive at 22px and when inverted. Teal alternates with cream.
    bands = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    band_w = 7
    left = dome_cx - dome_rx
    idx = 0
    x = left
    while x < dome_cx + dome_rx:
        is_teal = (idx % 2 == 0)
        top = STRIPE_TEAL_HI if is_teal else CREAM_HI
        bot = STRIPE_TEAL_LO if is_teal else CREAM_LO
        for yy in range(dome_rect.top, dome_rect.bottom):
            t = (yy - dome_rect.top) / max(1, dome_rect.height - 1)
            col = _lerp_color(top, bot, t) + (255,)
            bands.fill(col, pygame.Rect(x, yy, band_w, 1))
        x += band_w
        idx += 1
    mask = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), dome_rect)
    bands.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(bands, (0, 0))

    # Crown sheen — a bright cream catch on the upper-left of the dome sells
    # the round inflated canopy.
    pygame.draw.ellipse(surf, (255, 252, 246, 150),
                        pygame.Rect(dome_cx - 11, dome_cy - 14, 8, 7))

    # Warm bottom catch — a thin warm arc along the dome's lower rim keeps the
    # cool canopy from sinking into the dark night sky (value rescue on teal).
    pygame.draw.arc(surf, WARM_EDGE,
                    pygame.Rect(dome_cx - dome_rx + 3, dome_cy - dome_ry + 4,
                                (dome_rx - 3) * 2, (dome_ry - 4) * 2),
                    3.66, 5.76, 2)

    # Dome SKIRT — the flat-ish base where the canopy mouth gathers. A short
    # cream band with a dark underline reads as the balloon's open throat and
    # separates the dome from the cords.
    skirt_y = dome_cy + dome_ry - 4
    pygame.draw.ellipse(surf, OUTLINE,
                        pygame.Rect(dome_cx - 10, skirt_y - 2, 20, 7))
    pygame.draw.ellipse(surf, CREAM,
                        pygame.Rect(dome_cx - 8, skirt_y - 1, 16, 5))

    # ── BASKET ───────────────────────────────────────────────────────────
    # Outline frame behind a gradient wicker fill — a compact rounded square.
    b_out = basket_rect.inflate(4, 4)
    pygame.draw.rect(surf, OUTLINE, b_out, border_radius=3)
    fill = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    for yy in range(basket_rect.top, basket_rect.bottom):
        t = (yy - basket_rect.top) / max(1, basket_rect.height - 1)
        col = _lerp_color(BASKET_HI, BASKET_LO, t) + (255,)
        fill.fill(col, pygame.Rect(0, yy, SIZE, 1))
    bmask = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    pygame.draw.rect(bmask, (255, 255, 255, 255), basket_rect, border_radius=2)
    fill.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(fill, (0, 0))

    # Weave suggestion — a bound rim band plus one course line. Fine wicker
    # dies at 22px, so a couple of bold hatches carry the basket texture.
    pygame.draw.line(surf, BASKET_HI, (basket_rect.left + 1, basket_rect.top + 1),
                     (basket_rect.right - 2, basket_rect.top + 1), 1)
    pygame.draw.line(surf, WEAVE, (basket_rect.left + 1, basket_rect.top + 4),
                     (basket_rect.right - 2, basket_rect.top + 4), 1)
    pygame.draw.line(surf, WEAVE, (basket_rect.left + 1, basket_rect.top + 7),
                     (basket_rect.right - 2, basket_rect.top + 7), 1)
    for vx in range(basket_rect.left + 2, basket_rect.right - 1, 4):
        pygame.draw.line(surf, WEAVE, (vx, basket_rect.top + 2),
                         (vx, basket_rect.bottom - 2), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
