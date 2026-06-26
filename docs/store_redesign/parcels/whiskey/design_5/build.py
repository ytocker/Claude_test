"""CASKED DRAM — a cask-aged whiskey bottle in a wooden barrel-stave cradle.

The IDENTITY is two value-separated masses: a warm AMBER glass bottle with a
pale CORK stopper, seated in a curved BROWN wood cradle wrapped by a grey IRON
hoop. The cradle is the tell that lifts this above a plain bottle — a fine
single-cask dram still riding its barrel. The amber bottle reads as the drink;
the wood cradle below reads as the cask.

22px read tradeoffs (WHY): at true size the two materials must NOT fuse, so they
are pushed apart on VALUE as well as hue — the bottle is a bright amber that
desaturates to a light grey, the wood cradle is a deliberately DARKER brown that
desaturates to a clearly lower grey, with a hard iron-hoop band between them as a
third value to fence the join. Micro wood grain turns to mud at this size, so the
cradle is sold by ONE bold curved mass + a single stave-seam down its middle and
the bright hoop band, not by plank lines. The cork is kept a FAT pale block (the
loudest top beat) so the bottle reads as sealed even after the smoothscale. Built
on a 44px work surface then smoothscaled to 22 so the curved cradle and amber
edges antialias cleanly. A baked dark OUTLINE (inflated, drawn first) carries the
silhouette on bright DAY sky; a warm amber KEYLINE rim inside is the NIGHT
lifeline; bottle + cradle are held off the surface edges so the gameplay rotozoom
never clips the cork or the cradle horns under Pip's bank arc.
"""
import pygame

# Tight palette from the concept. Identity rides on VALUE: amber glass is the
# bright mass, wood is pushed darker, the iron hoop is a cool mid-grey band that
# fences the two so they read apart even in grayscale. Cork is a pale beat on top.
AMBER = (190, 115,  32)        # cask-aged whiskey glass (body mid)
AMBER_HI = (240, 180,  90)     # lit amber highlight / left glass sheen
AMBER_DEEP = (140,  74,  18)   # lower-body deepening so the glass reads as volume
CORK = (201, 160, 106)         # pale cork stopper — the loudest top beat
CORK_HI = (230, 200, 156)      # cork top edge highlight
WOOD = (122,  79,  46)         # barrel-stave cradle (darker than amber on value)
WOOD_HI = (158, 110,  70)      # lit upper stave face
WOOD_SHADE = ( 86,  54,  30)   # stave seam + inner cradle shadow
IRON = ( 90,  94, 102)         # iron hoop band (cool grey — third value)
IRON_HI = (150, 154, 162)      # hoop top highlight so it reads as a metal band
OUTLINE = ( 36,  26,  16)      # dark, high-value: reads on bright day sky
KEYLINE = (240, 196, 120)      # warm amber rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static casked-dram sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Geometry: a rounded amber bottle standing in a shallow wooden cradle. The
    # bottle is biased UP so the cork has headroom; the cradle hugs the lower body
    # so the wood reads as a separate mass beneath the glass. Everything is held
    # off the surface edges for the rotozoom.
    BW = 15                       # bottle body width
    body_top = 16
    body_bot = 34
    body_rect = pygame.Rect(cx - BW // 2, body_top, BW, body_bot - body_top)
    body_rad = 6                  # rounded barrel-bellied bottle

    # Neck + cork above the shoulder.
    NW = 6
    neck_rect = pygame.Rect(cx - NW // 2, 9, NW, 8)
    CW, CH = 8, 6
    cork_rect = pygame.Rect(cx - CW // 2, 3, CW, CH)

    # Cradle: a curved wooden trough cupping the lower body, with two raised horns
    # at the sides so it reads as staves wrapping up, not a flat shelf. Pulled UP
    # to overlap the bottle belly so the glass clearly sits INSIDE the cask, and
    # widened past the bottle so the wood reads as its own mass on every side.
    cradle_top = 27
    cradle_bot = 41
    cradle_rect = pygame.Rect(cx - 14, cradle_top, 28, cradle_bot - cradle_top)

    # ---- Baked dark outline (drawn first, inflated) for the DAY silhouette. ----
    pygame.draw.rect(surf, OUTLINE, cork_rect.inflate(4, 4), border_radius=2)
    pygame.draw.rect(surf, OUTLINE, neck_rect.inflate(4, 2))
    pygame.draw.rect(surf, OUTLINE, body_rect.inflate(4, 4), border_radius=body_rad + 2)
    # Cradle outline: an inflated rounded trough (drawn before the wood fill).
    pygame.draw.rect(surf, OUTLINE, cradle_rect.inflate(4, 4),
                     border_radius=9, border_top_left_radius=5,
                     border_top_right_radius=5)

    # ---- Shoulder tuck: dark diagonals so neck and body don't fuse. ----
    sh_y = neck_rect.bottom
    sh_dark = AMBER_DEEP
    pygame.draw.polygon(surf, sh_dark, [
        (body_rect.x, body_top + 3), (neck_rect.x, sh_y - 1),
        (neck_rect.x, sh_y + 1), (body_rect.x, body_top + 5)])
    pygame.draw.polygon(surf, sh_dark, [
        (body_rect.right, body_top + 3), (neck_rect.right, sh_y - 1),
        (neck_rect.right, sh_y + 1), (body_rect.right, body_top + 5)])

    # ---- AMBER BODY: a vertical light->deep gradient masked to the rounded
    # bottle, so the glass reads as a lit volume, not a flat amber slab. ----
    bw, bh = body_rect.w, body_rect.h
    body = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for y in range(bh):
        t = y / max(1, bh - 1)
        # Lit at top, deepening toward the base where the cradle shadows it.
        c = (
            int(AMBER_HI[0] + (AMBER_DEEP[0] - AMBER_HI[0]) * t),
            int(AMBER_HI[1] + (AMBER_DEEP[1] - AMBER_HI[1]) * t),
            int(AMBER_HI[2] + (AMBER_DEEP[2] - AMBER_HI[2]) * t),
        )
        body.fill(c + (255,), pygame.Rect(0, y, bw, 1))
    # A broad mid-body amber band so the centre isn't washed out by the gradient.
    body.fill(AMBER + (255,), pygame.Rect(0, int(bh * 0.34), bw, int(bh * 0.30)))
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=body_rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # A bright vertical glass sheen down the lit (left) edge so the amber reads as
    # glossy glass — the brightest amber stroke, the value anchor on grayscale.
    pygame.draw.line(surf, AMBER_HI, (body_rect.x + 3, body_rect.y + 3),
                     (body_rect.x + 3, body_rect.bottom - 6), 2)

    # ---- NECK fill. ----
    pygame.draw.rect(surf, AMBER, neck_rect)
    pygame.draw.line(surf, AMBER_HI, (neck_rect.x + 1, neck_rect.y + 1),
                     (neck_rect.x + 1, neck_rect.bottom - 1), 1)

    # ---- CORK: a FAT pale block with a top highlight + a hard groove at the
    # cork/neck join so the bottle reads as sealed. ----
    pygame.draw.rect(surf, CORK, cork_rect, border_radius=2)
    pygame.draw.line(surf, CORK_HI, (cork_rect.x + 1, cork_rect.y + 1),
                     (cork_rect.right - 2, cork_rect.y + 1), 1)
    pygame.draw.line(surf, OUTLINE, (cork_rect.x, cork_rect.bottom - 1),
                     (cork_rect.right - 1, cork_rect.bottom - 1), 2)

    # ---- WOODEN CRADLE: ONE bold curved brown mass cupping the lower body. The
    # bottle's amber base sits INTO it, so the wood is drawn over the lower body
    # to read as the bottle resting IN the cradle. Sold by a value step (darker
    # than amber) + a single stave seam, not plank lines that would alias to mud.
    cw, ch = cradle_rect.w, cradle_rect.h
    cradle = pygame.Surface((cw, ch), pygame.SRCALPHA)
    # Lit upper stave face -> shaded trough toward the bottom.
    for y in range(ch):
        t = y / max(1, ch - 1)
        c = (
            int(WOOD_HI[0] + (WOOD_SHADE[0] - WOOD_HI[0]) * t),
            int(WOOD_HI[1] + (WOOD_SHADE[1] - WOOD_HI[1]) * t),
            int(WOOD_HI[2] + (WOOD_SHADE[2] - WOOD_HI[2]) * t),
        )
        cradle.fill(c + (255,), pygame.Rect(0, y, cw, 1))
    # Mid-band of the base wood tone so the cradle holds one readable brown core.
    cradle.fill(WOOD + (255,), pygame.Rect(0, int(ch * 0.30), cw, int(ch * 0.34)))
    # Mask to a rounded trough whose TOP corners round more gently (staves rising)
    # and bottom rounds full (the barrel curve).
    cmask = pygame.Surface((cw, ch), pygame.SRCALPHA)
    pygame.draw.rect(cmask, (255, 255, 255, 255), cmask.get_rect(),
                     border_radius=9, border_top_left_radius=5,
                     border_top_right_radius=5)
    cradle.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(cradle, cradle_rect.topleft)

    # Stave seams (WOOD_SHADE) so the cradle reads as joined staves, stopped just
    # above the iron hoop so the hoop stays one clean unbroken band.
    seam_bot = cradle_bot - 7
    pygame.draw.line(surf, WOOD_SHADE, (cx, cradle_top + 3), (cx, seam_bot), 1)
    pygame.draw.line(surf, WOOD_SHADE, (cx - 7, cradle_top + 4), (cx - 7, seam_bot), 1)
    pygame.draw.line(surf, WOOD_SHADE, (cx + 7, cradle_top + 4), (cx + 7, seam_bot), 1)

    # ---- IRON HOOP: a cool grey band wrapping the cradle across its visible
    # FRONT belly — the third value that fences amber from wood and says "barrel".
    # Placed mid-cradle (below the bottle base) so the glass never overhangs it,
    # and given a bright top edge so it reads as a raised metal hoop. ----
    hoop_y = cradle_bot - 4
    pygame.draw.line(surf, IRON, (cradle_rect.x + 3, hoop_y),
                     (cradle_rect.right - 4, hoop_y), 3)
    pygame.draw.line(surf, IRON_HI, (cradle_rect.x + 3, hoop_y - 2),
                     (cradle_rect.right - 4, hoop_y - 2), 1)

    # ---- Warm amber keyline rim INSIDE the outline — the NIGHT lifeline that
    # glows on dark sky while staying subtle on day. Traces the bottle + cradle. -
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad)
    pygame.draw.rect(surf, KEYLINE, cork_rect, width=1, border_radius=2)
    pygame.draw.rect(surf, KEYLINE, cradle_rect, width=1, border_radius=9,
                     border_top_left_radius=5, border_top_right_radius=5)

    return pygame.transform.smoothscale(surf, (22, 22))
