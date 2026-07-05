"""GOLD RESERVE — the finest-tier wax-sealed reserve whiskey parcel cosmetic.

The IDENTITY is "richest bottle in the set": a glass body CASED in metal GOLD
with an amber whiskey window, a gold foil neck collar, and the flex tell — a
crimson WAX SEAL blob capping the cork. Gold is the brand read, so every gold
zone carries a hard dark->bright->mid value sequence to register as polished
METAL rather than flat yellow, even desaturated.

22px read tradeoffs (WHY): at true size only a few masses survive, so the build
commits to three loud beats stacked top-to-bottom — RED wax seal, GOLD neck
foil, GOLD-cased amber body. The gold is split into a deep shade, a struck
HIGHLIGHT band, and a mid so a hard light/dark seam survives the smoothscale and
reads as polished metal on the grayscale row; a single flat yellow would mush to
one value. The amber window is pushed darker/redder than the gold so the glass
never shares a value with the casing, and is widened to a real whiskey band
between the gold neck and gold base. The bottle is slimmed + lengthened so it
reads as elegant fine-spirits glass, not a squat jar. The wax seal is a fat
round crimson MASS (no fine drip detail — it aliases to mud) with a dark rim so
the "finest" cue holds as a saturated focal beat across Pip's tilt arc. The old
ribbon medallion was sub-pixel noise — cut for a cleaner gold foil collar with a
groove dividing neck from shoulder. Drawn on a 44px work surface then
smoothscaled to 22 so the gold seams antialias cleanly. A baked dark OUTLINE
(inflated, drawn first) carries the silhouette on bright DAY sky; a warm gold
KEYLINE rim inside is the NIGHT lifeline; the bottle is held off the surface
edges so the gameplay rotozoom never clips the seal or base.
"""
import pygame

# Tight palette: gilded casing carries a wide value spread (deep shade -> mid ->
# struck highlight) so it reads as polished metal even in grayscale. Amber is
# pushed dark + red so the whiskey window never matches the gold value. Crimson
# wax seal is the saturated focal beat; dark day-outline + warm gold night-key.
GOLD = (223, 170, 52)          # base gilding mid-tone
GOLD_HI = (251, 233, 168)      # bright struck-metal highlight band
GOLD_SHADE = (122, 86, 15)     # deep gold shadow — anchors the metal contrast
AMBER = (120, 56, 12)          # deep whiskey — clearly darker/redder than gold
AMBER_MID = (154, 78, 14)      # whiskey mid
AMBER_HI = (196, 120, 44)      # amber glint / meniscus
WAX = (172, 36, 56)            # crimson wax seal
WAX_HI = (216, 82, 100)        # wax sheen
WAX_SHADE = (108, 20, 38)      # wax underside
OUTLINE = (40, 28, 12)         # dark, warm: reads on bright day sky
KEYLINE = (250, 226, 150)      # warm gold rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static bottle sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Geometry: a slim, tall reserve bottle — narrow gold-cased body, a foil
    # neck collar, and a wax-sealed cork on top. Held off the surface edges so
    # the rotozoom never clips the seal or base. Body slimmed and lengthened
    # (top pushed up) over the squat round-1 so it reads as fine-spirits glass.
    BW = 18
    body_top = 15
    body_bot = 41
    body_rect = pygame.Rect(cx - BW // 2, body_top, BW, body_bot - body_top)
    body_rad = 4

    # Neck: a short gold-foil collar bridging the shoulder to the cork.
    NW = 8
    neck_rect = pygame.Rect(cx - NW // 2, 8, NW, 8)

    # Cork + wax seal sit above the neck as a fat round crimson mass. Kept
    # generous so the "finest" flex tell survives the downscale + tilt.
    seal_cy = 5
    seal_r = 6

    # --- Baked dark outline (drawn first, slightly inflated) for the DAY read.
    pygame.draw.circle(surf, OUTLINE, (cx, seal_cy), seal_r + 2)
    pygame.draw.rect(surf, OUTLINE, neck_rect.inflate(4, 3), border_radius=2)
    pygame.draw.rect(surf, OUTLINE, body_rect.inflate(4, 4), border_radius=body_rad + 2)

    # --- Shoulder tuck: dark diagonals from the body wall up into the neck so
    # the foil neck and gold body never fuse into one mass at the downscale.
    sh_y = neck_rect.bottom
    pygame.draw.polygon(surf, OUTLINE, [
        (body_rect.x, body_top + 1),
        (neck_rect.x - 1, sh_y - 1),
        (neck_rect.x + 1, sh_y + 2),
        (body_rect.x + 4, body_top + 4),
    ])
    pygame.draw.polygon(surf, OUTLINE, [
        (body_rect.right, body_top + 1),
        (neck_rect.right + 1, sh_y - 1),
        (neck_rect.right - 1, sh_y + 2),
        (body_rect.right - 4, body_top + 4),
    ])

    # --- BODY built on its own alpha surface: an AMBER glass window in the
    # middle flanked by GOLD casing top and bottom, masked to the bottle shape
    # and composited in one piece. Each gold zone is laid down as a hard
    # dark->bright->mid sequence so a polished-metal seam survives the downscale.
    bw, bh = body_rect.w, body_rect.h
    body = pygame.Surface((bw, bh), pygame.SRCALPHA)

    # Vertical zones: a wide amber whiskey window between a gold shoulder band
    # and a gold base band. Window widened (~0.30..0.74) so the glass reads as a
    # real liquid volume, not a thin stripe.
    amber_top = int(bh * 0.30)
    amber_bot = int(bh * 0.74)

    def gold_band(y0, y1):
        # Polished-metal sequence: deep shade fill, mid over it, then a bright
        # struck highlight band near the top so a hard light seam survives even
        # in grayscale.
        h = y1 - y0
        body.fill(GOLD_SHADE + (255,), pygame.Rect(0, y0, bw, h))
        body.fill(GOLD + (255,), pygame.Rect(0, y0 + 1, bw, h - 1))
        hi_h = 3 if h >= 6 else 2
        body.fill(GOLD_HI + (255,), pygame.Rect(1, y0 + 1, bw - 2, hi_h))
        # Re-seat the mid below the highlight so the band ends dark->bright->mid.
        body.fill(GOLD + (255,), pygame.Rect(1, y0 + 1 + hi_h, bw - 2, max(0, h - 2 - hi_h)))
        # A deep shade lip at the very bottom of the zone for roundness.
        body.fill(GOLD_SHADE + (255,), pygame.Rect(0, y1 - 1, bw, 1))

    # Top gold band (shoulder casing).
    gold_band(0, amber_top)

    # Amber whiskey window: a vertical deepening so it reads as liquid volume,
    # pushed dark/red so it never shares a value with the gold casing.
    for y in range(amber_top, amber_bot):
        t = (y - amber_top) / max(1, amber_bot - 1 - amber_top)
        # Bright meniscus at the top, deepening through a mid into the darkest
        # whiskey at the base of the window.
        if t < 0.18:
            a, b, tt = AMBER_HI, AMBER_MID, t / 0.18
        else:
            a, b, tt = AMBER_MID, AMBER, (t - 0.18) / 0.82
        c = (int(a[0] + (b[0] - a[0]) * tt),
             int(a[1] + (b[1] - a[1]) * tt),
             int(a[2] + (b[2] - a[2]) * tt))
        body.fill(c + (255,), pygame.Rect(0, y, bw, 1))
    # Amber glint streak (glass translucency cue) down the left wall.
    pygame.draw.line(body, AMBER_HI, (3, amber_top + 2), (3, amber_bot - 3), 2)

    # Bottom gold band (base casing).
    gold_band(amber_bot, bh)

    # Hard outline fences top + bottom of the amber window so the gold/amber
    # seams survive the smoothscale as discrete bands instead of bleeding.
    pygame.draw.line(body, OUTLINE, (0, amber_top), (bw, amber_top), 1)
    pygame.draw.line(body, OUTLINE, (0, amber_bot), (bw, amber_bot), 1)

    # Mask to the bottle shape: only the bottom corners round.
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=body_rad, border_top_left_radius=0,
                     border_top_right_radius=0)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # --- NECK FOIL COLLAR: gold foil with the same dark->bright->mid metal
    # sequence, plus a 1px OUTLINE groove at the base dividing neck from
    # shoulder so the collar reads as a separate cased step.
    pygame.draw.rect(surf, GOLD_SHADE, neck_rect, border_radius=2)
    pygame.draw.rect(surf, GOLD, neck_rect.inflate(-2, -2), border_radius=2)
    pygame.draw.line(surf, GOLD_HI, (neck_rect.x + 2, neck_rect.y + 2),
                     (neck_rect.right - 3, neck_rect.y + 2), 1)
    pygame.draw.line(surf, GOLD_HI, (neck_rect.x + 1, neck_rect.y + 2),
                     (neck_rect.x + 1, neck_rect.bottom - 3), 1)
    # Groove: a dark seam fencing the foil collar off from the shoulder casing.
    pygame.draw.line(surf, OUTLINE, (neck_rect.x - 1, neck_rect.bottom - 1),
                     (neck_rect.right, neck_rect.bottom - 1), 1)

    # --- WAX SEAL: a fat round crimson mass over the cork — the focal flex
    # tell. Dark underside + bright sheen so it reads as a 3D blob, ringed by a
    # 1px dark rim so it stays a clean red against the brighter gold collar.
    pygame.draw.circle(surf, OUTLINE, (cx, seal_cy), seal_r)
    pygame.draw.circle(surf, WAX_SHADE, (cx, seal_cy + 1), seal_r - 1)
    pygame.draw.circle(surf, WAX, (cx, seal_cy), seal_r - 1)
    pygame.draw.circle(surf, WAX_HI, (cx - 2, seal_cy - 2), 2)
    # A small gold press-stamp ring on the wax for the "sealed reserve" read.
    pygame.draw.circle(surf, GOLD_HI, (cx, seal_cy), 2, 1)

    # --- Warm gold keyline rim INSIDE the outline — the NIGHT lifeline that
    # glows on dark sky while staying subtle on day.
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad,
                     border_top_left_radius=0, border_top_right_radius=0)
    pygame.draw.circle(surf, KEYLINE, (cx, seal_cy), seal_r, 1)

    return pygame.transform.smoothscale(surf, (22, 22))
