"""SQUARE BOURBON — a square black-and-gold Tennessee-whiskey bottle parcel.

The IDENTITY is the SQUARE boxy bottle + the BLACK-and-GOLD centre label. Three
beats carry it: SQUARE shoulders (a straight-walled glass box, not a round
bottle), a crisp BLACK rectangular LABEL trimmed in GOLD across the middle, and
a short BLACK screw CAP. Amber whiskey peeks above and below the label so the
vessel reads as a drink before the label even registers.

22px read tradeoffs (WHY): the black label is the loudest premium cue, so it is a
FAT crisp rectangular MASS (~0.34–0.70 of the body) fenced top + bottom with the
dark OUTLINE value, kept near full body width so it survives the smoothscale +
rotation as one hard black block instead of dissolving into the amber. The gold
trim is the SECOND cue — a single bright gold border ring + one gold band drawn
INSIDE the black so gold and black stay distinct masses at true size (micro gold
text would alias to mud). The body walls are kept dead STRAIGHT with only the
base corners tucked so the silhouette stays boxy and squared off — the square
shape is what separates it from a round whiskey bottle across the tilt arc. Amber
is split into a thin band above and a deeper band below the label so a hint of
liquid reads on both sides without competing with the black mass. Drawn on a 44px
work surface then smoothscaled to 22 so the label/gold edges antialias cleanly. A
baked dark OUTLINE (inflated, drawn first) carries the silhouette on bright DAY
sky; a warm gold-tinted KEYLINE rim inside is the NIGHT lifeline; the bottle is
held off the surface edges so the gameplay rotozoom never clips the cap or base.
"""
import pygame

# Tight palette from the concept: pale green glass, amber bourbon, a black centre
# label, gold trim (the premium tell), a dark outline for day and a warm keyline
# for night.
GLASS = (168, 182, 160)        # pale green Tennessee glass (shoulders / edges)
AMBER = (168,  94,  22)        # bourbon liquid
AMBER_HI = (214, 138,  56)     # lit amber / meniscus glint
LABEL = ( 30,  30,  34)        # black centre label (the loudest premium mass)
LABEL_HI = ( 58,  58,  64)     # faint top edge so the black reads as a panel
GOLD = (227, 178,  60)         # gold trim ring + band (the second cue)
GOLD_HI = (248, 224, 138)      # gold highlight glint
CAP = ( 26,  26,  30)          # short black screw cap
CAP_HI = ( 96,  96, 104)       # cap top edge highlight
OUTLINE = ( 22,  22,  14)      # dark, high-contrast: reads on bright day sky
KEYLINE = (228, 196, 120)      # warm gold rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static bottle sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Geometry: a SQUARE-shouldered glass body, a short neck, and a short black
    # cap. Held off the surface edges so the gameplay rotozoom never clips it.
    BW = 18
    body_top = 14
    body_bot = 39
    body_rect = pygame.Rect(cx - BW // 2, body_top, BW, body_bot - body_top)
    body_rad = 2                  # only a faint base tuck so the box stays square

    # Neck: a short narrow step from the square shoulder up to the cap.
    NW = 8
    neck_rect = pygame.Rect(cx - NW // 2, 9, NW, 6)

    # Cap: a short black screw cap — the boxy bourbon top beat. Kept squat + wide
    # so it stays a distinct black block over the body on night / grayscale.
    CW, CH = 11, 7
    cap_rect = pygame.Rect(cx - CW // 2, 3, CW, CH)

    # --- Baked dark outline (drawn first, slightly inflated) for the DAY read.
    pygame.draw.rect(surf, OUTLINE, cap_rect.inflate(4, 4), border_radius=2)
    pygame.draw.rect(surf, OUTLINE, neck_rect.inflate(4, 3))
    pygame.draw.rect(surf, OUTLINE, body_rect.inflate(4, 4), border_radius=body_rad + 2)

    # --- Square shoulder: hard, near-flat tucks from the body wall corners into
    # the neck so the cap/neck and body never fuse, while keeping the shoulder
    # squared rather than rounded (the boxy bourbon read).
    sh_y = neck_rect.bottom
    sh_dark = (44, 50, 40)
    pygame.draw.polygon(surf, sh_dark, [
        (body_rect.x, body_top + 1),
        (neck_rect.x, sh_y - 1),
        (neck_rect.x, sh_y + 1),
        (body_rect.x, body_top + 3),
    ])
    pygame.draw.polygon(surf, sh_dark, [
        (body_rect.right, body_top + 1),
        (neck_rect.right, sh_y - 1),
        (neck_rect.right, sh_y + 1),
        (body_rect.right, body_top + 3),
    ])
    # Fill the shoulder interior so the body wall meets the neck cleanly.
    pygame.draw.polygon(surf, GLASS, [
        (body_rect.x + 1, body_top + 2),
        (neck_rect.x, sh_y),
        (neck_rect.right, sh_y),
        (body_rect.right - 1, body_top + 2),
    ])

    # --- BODY built on its own alpha surface: a thin amber band, the BLACK label
    # with gold trim across the middle, then a deeper amber band below, masked to
    # the straight-walled square shape and composited in one piece.
    bw, bh = body_rect.w, body_rect.h
    body = pygame.Surface((bw, bh), pygame.SRCALPHA)

    # Amber whiskey fills the whole body first; the black label sits on top of it
    # so amber peeks above AND below as a hint of liquid.
    for y in range(bh):
        t = y / max(1, bh - 1)
        c = (
            int(AMBER_HI[0] + (AMBER[0] - AMBER_HI[0]) * t),
            int(AMBER_HI[1] + (AMBER[1] - AMBER_HI[1]) * t),
            int(AMBER_HI[2] + (AMBER[2] - AMBER_HI[2]) * t),
        )
        body.fill(c + (255,), pygame.Rect(0, y, bw, 1))

    # Label band geometry: a FAT crisp black mass across the MIDDLE, near full
    # body width, leaving a thin amber band above and a deeper one below.
    label_top = int(bh * 0.34)
    label_bot = int(bh * 0.70)

    # BLACK centre label — the loudest premium mass. FENCED top + bottom with the
    # dark OUTLINE value so it stays one hard black block after the smoothscale.
    body.fill(LABEL + (255,), pygame.Rect(0, label_top, bw, label_bot - label_top))
    pygame.draw.line(body, OUTLINE, (0, label_top), (bw, label_top), 1)
    pygame.draw.line(body, OUTLINE, (0, label_bot - 1), (bw, label_bot - 1), 1)
    # Faint top edge so the black reads as a flat panel, not a void.
    pygame.draw.line(body, LABEL_HI, (1, label_top + 1), (bw - 2, label_top + 1), 1)

    # GOLD trim — the second cue, drawn INSIDE the black so gold + black stay
    # distinct masses: a bright border ring around the label plus one gold band.
    gold_rect = pygame.Rect(1, label_top + 1, bw - 2, (label_bot - 1) - (label_top + 1))
    pygame.draw.rect(body, GOLD, gold_rect, width=1)
    band_y = label_top + (label_bot - label_top) // 2
    pygame.draw.line(body, GOLD, (2, band_y - 1), (bw - 3, band_y - 1), 1)
    pygame.draw.line(body, GOLD, (2, band_y), (bw - 3, band_y), 1)
    pygame.draw.line(body, GOLD_HI, (2, band_y - 1), (bw // 2, band_y - 1), 1)
    pygame.draw.line(body, GOLD_HI, (2, label_top + 2), (4, label_top + 2), 1)

    # Mask to a STRAIGHT-WALLED square shape: only the bottom corners tuck.
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=body_rad, border_top_left_radius=0,
                     border_top_right_radius=0)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # --- Glass glint on the amber above the label so the body reads as liquid.
    pygame.draw.line(surf, AMBER_HI,
                     (body_rect.x + 2, body_rect.y + 2),
                     (body_rect.x + 2, body_rect.y + label_top - 1), 2)
    # Meniscus glint on the deeper amber below the label.
    pygame.draw.line(surf, AMBER_HI,
                     (body_rect.x + 2, body_rect.y + label_bot + 1),
                     (body_rect.right - 3, body_rect.y + label_bot + 1), 1)

    # --- NECK fill (between the square shoulder and the cap).
    pygame.draw.rect(surf, GLASS, neck_rect)

    # --- CAP: short black screw cap with a flat top highlight + a hard groove at
    # the cap/neck join (OUTLINE colour) so it reads as a screw-on lid.
    pygame.draw.rect(surf, CAP, cap_rect, border_radius=2)
    pygame.draw.line(surf, CAP_HI,
                     (cap_rect.x + 1, cap_rect.y + 1),
                     (cap_rect.right - 2, cap_rect.y + 1), 1)
    pygame.draw.line(surf, OUTLINE,
                     (cap_rect.x, cap_rect.bottom - 1),
                     (cap_rect.right - 1, cap_rect.bottom - 1), 2)

    # --- Warm gold keyline rim INSIDE the outline — the NIGHT lifeline that glows
    # on dark sky while staying subtle on day. Traces the square body wall + cap.
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad,
                     border_top_left_radius=0, border_top_right_radius=0)
    pygame.draw.rect(surf, KEYLINE, cap_rect, width=1, border_radius=2)

    return pygame.transform.smoothscale(surf, (22, 22))
