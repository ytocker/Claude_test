"""GOLD RESERVE — the finest-tier wax-sealed reserve whiskey parcel cosmetic.

The IDENTITY is "richest bottle in the set": a glass body CASED in metal GOLD
with amber whiskey, a gold foil neck, and the flex tell — a crimson WAX SEAL
blob capping the cork, with a tiny ribbon medallion hung off the neck. Gold is
the brand read, so it carries strong value contrast (bright gold-hi banding
against gold-shade) to register as METAL rather than a flat yellow at size.

22px read tradeoffs (WHY): at true size only a few masses survive, so the build
commits to three loud beats stacked top-to-bottom — RED wax seal, GOLD neck
foil, GOLD-banded amber body. The gold is split into a hi band over a shade
band so a hard light/dark seam survives the smoothscale and reads as polished
metal on the grayscale row; a single flat yellow would mush to one value. The
wax seal is a fat round crimson MASS (no fine drip detail — it aliases to mud)
so the "finest" cue holds across Pip's tilt arc. The ribbon medallion is one
small gold disc on a short red tab — enough to read as hung bling without
splitting into noise. Drawn on a 44px work surface then smoothscaled to 22 so
the gold seams antialias cleanly. A baked dark OUTLINE (inflated, drawn first)
carries the silhouette on bright DAY sky; a warm gold KEYLINE rim inside is the
NIGHT lifeline; the bottle is held off the surface edges so the gameplay
rotozoom never clips the seal or base.
"""
import pygame

# Tight palette from the concept: gilded casing (hi/shade for metal contrast),
# amber whiskey in the glass, crimson wax seal, a dark day-outline + a warm
# gold night-keyline.
GOLD = (227, 178, 60)          # base gilding
GOLD_HI = (248, 224, 138)      # bright struck-metal highlight band
GOLD_SHADE = (158, 116, 30)    # deep gold shadow — the metal value contrast
AMBER = (184, 106, 24)         # whiskey in the glass
AMBER_HI = (224, 156, 70)      # amber glint / meniscus
WAX = (168, 36, 58)            # crimson wax seal
WAX_HI = (212, 78, 96)         # wax sheen
WAX_SHADE = (110, 22, 40)      # wax underside
OUTLINE = (42, 30, 14)         # dark, warm: reads on bright day sky
KEYLINE = (250, 226, 150)      # warm gold rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static bottle sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Geometry: a stout reserve bottle — wide gold-banded body, a foil neck, and
    # a wax-sealed cork on top. Held off the surface edges so the rotozoom never
    # clips the seal or base.
    BW = 20
    body_top = 19
    body_bot = 40
    body_rect = pygame.Rect(cx - BW // 2, body_top, BW, body_bot - body_top)
    body_rad = 5

    # Neck: a short gold-foil step bridging the shoulder to the cork.
    NW = 9
    neck_rect = pygame.Rect(cx - NW // 2, 12, NW, 8)

    # Cork + wax seal sit above the neck as a fat round crimson mass. Kept
    # generous so the "finest" flex tell survives the downscale + tilt.
    seal_cy = 8
    seal_r = 7

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
    # and composited in one piece. The gold bands are split hi-over-shade so a
    # hard metal seam survives the downscale.
    bw, bh = body_rect.w, body_rect.h
    body = pygame.Surface((bw, bh), pygame.SRCALPHA)

    # Vertical zones: gold cap-band at the shoulder, amber whiskey window, gold
    # base-band at the foot. The amber window is the glass; the gold bands are
    # the casing that makes this the "reserve".
    amber_top = int(bh * 0.28)
    amber_bot = int(bh * 0.70)

    # Top gold band (shoulder casing): shade base then a struck hi line.
    body.fill(GOLD_SHADE + (255,), pygame.Rect(0, 0, bw, amber_top))
    body.fill(GOLD + (255,), pygame.Rect(0, 1, bw, amber_top - 2))
    body.fill(GOLD_HI + (255,), pygame.Rect(1, 2, bw - 2, 2))

    # Amber whiskey window: a vertical deepening so it reads as liquid volume.
    for y in range(amber_top, amber_bot):
        t = (y - amber_top) / max(1, amber_bot - 1 - amber_top)
        c = (
            int(AMBER_HI[0] + (AMBER[0] - AMBER_HI[0]) * t),
            int(AMBER_HI[1] + (AMBER[1] - AMBER_HI[1]) * t),
            int(AMBER_HI[2] + (AMBER[2] - AMBER_HI[2]) * t),
        )
        body.fill(c + (255,), pygame.Rect(0, y, bw, 1))
    # Amber glint streak (glass translucency cue).
    pygame.draw.line(body, AMBER_HI, (3, amber_top + 2), (3, amber_bot - 2), 2)

    # Bottom gold band (base casing): shade base then a struck hi line, fenced
    # from the amber with the dark outline so the seam stays a hard metal edge.
    body.fill(GOLD_SHADE + (255,), pygame.Rect(0, amber_bot, bw, bh - amber_bot))
    body.fill(GOLD + (255,), pygame.Rect(0, amber_bot + 1, bw, bh - amber_bot - 1))
    body.fill(GOLD_HI + (255,), pygame.Rect(1, amber_bot + 1, bw - 2, 2))

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

    # --- NECK: gold foil, shade base with a struck hi edge for the metal read.
    pygame.draw.rect(surf, GOLD_SHADE, neck_rect, border_radius=2)
    pygame.draw.rect(surf, GOLD, neck_rect.inflate(-2, -2), border_radius=2)
    pygame.draw.line(surf, GOLD_HI, (neck_rect.x + 1, neck_rect.y + 1),
                     (neck_rect.x + 1, neck_rect.bottom - 2), 1)

    # --- RIBBON MEDALLION: a short crimson tab off the neck with a tiny gold
    # disc — hung bling that reads without splitting into noise.
    tab_x = neck_rect.right
    pygame.draw.rect(surf, OUTLINE, (tab_x, neck_rect.y + 1, 4, 7))
    pygame.draw.rect(surf, WAX, (tab_x, neck_rect.y + 1, 3, 6))
    pygame.draw.circle(surf, OUTLINE, (tab_x + 2, neck_rect.y + 9), 3)
    pygame.draw.circle(surf, GOLD, (tab_x + 2, neck_rect.y + 9), 2)
    pygame.draw.circle(surf, GOLD_HI, (tab_x + 1, neck_rect.y + 8), 1)

    # --- WAX SEAL: a fat round crimson mass over the cork — the flex tell.
    # Shade underside + bright sheen so it reads as a 3D blob, not a flat dot.
    pygame.draw.circle(surf, WAX_SHADE, (cx, seal_cy + 1), seal_r)
    pygame.draw.circle(surf, WAX, (cx, seal_cy), seal_r)
    pygame.draw.circle(surf, WAX_HI, (cx - 2, seal_cy - 2), 2)
    # A small gold press-stamp ring on the wax for the "sealed reserve" read.
    pygame.draw.circle(surf, GOLD_HI, (cx, seal_cy), 2, 1)

    # --- Warm gold keyline rim INSIDE the outline — the NIGHT lifeline that
    # glows on dark sky while staying subtle on day.
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad,
                     border_top_left_radius=0, border_top_right_radius=0)
    pygame.draw.circle(surf, KEYLINE, (cx, seal_cy), seal_r, 1)

    return pygame.transform.smoothscale(surf, (22, 22))
