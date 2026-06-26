"""SCOTCH FIFTH — a labeled single-malt whiskey bottle parcel cosmetic.

The IDENTITY is the classic scotch read: a tall ROUND-SHOULDERED glass bottle
holding AMBER whiskey, fenced across the middle by a fat cream+gold rectangular
LABEL (the brand tell), with a FOIL-wrapped neck and a short cap on top. Two
beats carry the premium read before any detail: the warm amber liquid that fills
the body, and the bright label mass that brands it.

22px read tradeoffs (WHY): at true size the label is the loudest premium cue, so
it is a FAT cream block spanning the body's waist, capped with a gold band and
FENCED top + bottom with the dark OUTLINE colour — that hard fence keeps it one
discrete bright mass after the smoothscale instead of bleeding into the amber.
The label is held full-width so it survives the downscale + the bank rotation as
a band, not a sliver. The amber is a single warm gradient (deeper at the base)
rather than micro-glints, because bold masses beat fine detail at 22px. The neck
foil is a small darker-gold sleeve that separates the cap beat from the round
shoulder so the top never fuses at the downscale. A baked dark OUTLINE (inflated,
drawn first) carries the silhouette on bright DAY sky; a cool KEYLINE rim inside
is the NIGHT lifeline; the bottle is held off the surface edges so the gameplay
rotozoom never clips the cap or base.
"""
import pygame

# Tight palette from the concept: cool-green glass, warm amber whiskey, a cream
# label with a gold band (the brand read + grayscale anchor), gold neck foil, a
# dark outline for day and a cool keyline for night.
GLASS = (159, 194, 194)         # cool-green glass shoulder rim / glints
SHOULDER = (176, 118, 48)       # amber-through-glass at the shoulder (whiskey read)
AMBER = (184, 106, 24)          # whiskey body
AMBER_DK = (124, 66, 12)        # deeper amber low in the body (volume)
AMBER_HI = (228, 156, 74)       # bright meniscus / upper liquid
LABEL = (242, 230, 200)         # cream label mass (the brand read)
LABEL_SH = (214, 198, 158)      # faint lower-label shade so it reads as paper
GOLD = (227, 178, 60)           # gold label band + neck foil (premium tell)
GOLD_HI = (248, 224, 138)       # gold highlight edge
CAP = (58, 46, 30)              # dark cork-cap top beat
OUTLINE = (36, 28, 18)          # dark, high-value: reads on bright day sky
KEYLINE = (208, 224, 220)       # cool rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static bottle sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Geometry: a TALL body with a round shoulder, a foil neck, and a short cap.
    # Held off the surface edges so the gameplay rotozoom never clips it.
    BW = 17
    body_top = 17                 # straight body wall starts below the shoulder
    body_bot = 40
    body_rect = pygame.Rect(cx - BW // 2, body_top, BW, body_bot - body_top)
    body_rad = 4                  # base rounds in

    # Round shoulder: a wedge that tucks the body wall up into the neck.
    shoulder_top = 12
    NW = 7
    neck_rect = pygame.Rect(cx - NW // 2, 8, NW, shoulder_top - 8 + 2)

    # Cap: a short dark cork beat on top of the foil neck.
    CW, CH = 8, 5
    cap_rect = pygame.Rect(cx - CW // 2, 4, CW, CH)

    # --- Baked dark outline (drawn first, slightly inflated) for the DAY read.
    pygame.draw.rect(surf, OUTLINE, cap_rect.inflate(4, 4), border_radius=2)
    pygame.draw.rect(surf, OUTLINE, neck_rect.inflate(4, 3))
    # Round shoulder outline: an ellipse spanning body width up to the neck.
    sh_out = pygame.Rect(body_rect.x - 2, shoulder_top - 2,
                         BW + 4, (body_top - shoulder_top) + 6)
    pygame.draw.ellipse(surf, OUTLINE, sh_out)
    pygame.draw.rect(surf, OUTLINE, body_rect.inflate(4, 4),
                     border_radius=body_rad + 2)

    # --- Round shoulder fill: amber-through-glass so the whiskey read carries
    # all the way up the bottle, with a thin cool glass rim at the very top edge.
    sh_fill = pygame.Rect(body_rect.x, shoulder_top, BW, (body_top - shoulder_top) + 4)
    pygame.draw.ellipse(surf, SHOULDER, sh_fill)
    pygame.draw.arc(surf, GLASS, sh_fill, 0.5, 2.64, 1)  # cool glint along the top curve

    # --- BODY built on its own alpha surface: amber whiskey with the cream LABEL
    # mass fenced across the waist, masked to the straight-walled shape and
    # composited in one piece so the label edges antialias cleanly.
    bw, bh = body_rect.w, body_rect.h
    body = pygame.Surface((bw, bh), pygame.SRCALPHA)

    # Amber whiskey gradient: brighter near the top (meniscus), deeper at base —
    # one warm mass, not micro-glints, because masses beat detail at 22px.
    for y in range(bh):
        t = y / max(1, bh - 1)
        c = (
            int(AMBER_HI[0] + (AMBER_DK[0] - AMBER_HI[0]) * t),
            int(AMBER_HI[1] + (AMBER_DK[1] - AMBER_HI[1]) * t),
            int(AMBER_HI[2] + (AMBER_DK[2] - AMBER_HI[2]) * t),
        )
        body.fill(c + (255,), pygame.Rect(0, y, bw, 1))

    # Label band geometry: a FAT cream mass across the body waist. Spanning
    # ~0.34–0.70 of body height so the bright core survives the downscale +
    # rotation as a band, not a sliver — the loudest premium cue.
    label_top = int(bh * 0.30)
    label_bot = int(bh * 0.62)
    gold_h = 2                    # gold band along the label's lower edge

    body.fill(LABEL + (255,), pygame.Rect(0, label_top, bw, label_bot - label_top))
    # Faint lower-label shade so the cream reads as paper, not a flat block.
    body.fill(LABEL_SH + (255,),
              pygame.Rect(0, label_bot - gold_h - 2, bw, 2))
    # Gold band (premium tell) along the label's lower edge.
    body.fill(GOLD + (255,), pygame.Rect(0, label_bot - gold_h, bw, gold_h))
    pygame.draw.line(body, GOLD_HI, (0, label_bot - gold_h),
                     (bw, label_bot - gold_h), 1)
    # FENCE top + bottom with the dark OUTLINE colour so the label stays one
    # hard, discrete bright block after the smoothscale instead of bleeding.
    pygame.draw.line(body, OUTLINE, (0, label_top), (bw, label_top), 1)
    pygame.draw.line(body, OUTLINE, (0, label_bot - 1), (bw, label_bot - 1), 1)

    # Mask to a STRAIGHT-WALLED shape: only the bottom corners round.
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=body_rad, border_top_left_radius=0,
                     border_top_right_radius=0)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # --- Meniscus glint just under the shoulder so the upper amber reads as
    # liquid surface (a bright lip above the label).
    my = body_rect.y + 2
    pygame.draw.line(surf, AMBER_HI,
                     (body_rect.x + 2, my), (body_rect.right - 3, my), 1)
    # Vertical glass glint streak on the amber (a single committed highlight).
    pygame.draw.line(surf, AMBER_HI,
                     (body_rect.x + 3, body_rect.y + 3),
                     (body_rect.x + 3, body_rect.y + label_top - 1), 2)

    # --- NECK: gold FOIL sleeve separating the cap beat from the round shoulder.
    pygame.draw.rect(surf, GOLD, neck_rect)
    pygame.draw.line(surf, GOLD_HI,
                     (neck_rect.x + 1, neck_rect.y),
                     (neck_rect.x + 1, neck_rect.bottom - 1), 1)
    # Hard foil/shoulder groove so the neck stays a distinct beat at the downscale.
    pygame.draw.line(surf, OUTLINE,
                     (neck_rect.x, neck_rect.bottom - 1),
                     (neck_rect.right - 1, neck_rect.bottom - 1), 1)

    # --- CAP: short dark cork top with a faint highlight lip.
    pygame.draw.rect(surf, CAP, cap_rect, border_radius=2)
    pygame.draw.line(surf, GOLD_HI,
                     (cap_rect.x + 1, cap_rect.y + 1),
                     (cap_rect.right - 2, cap_rect.y + 1), 1)

    # --- Cool keyline rim INSIDE the outline — the NIGHT lifeline that glows on
    # dark sky while staying subtle on day. Traces the body wall + shoulder + cap.
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad,
                     border_top_left_radius=0, border_top_right_radius=0)
    pygame.draw.ellipse(surf, KEYLINE, sh_fill, width=1)
    pygame.draw.rect(surf, KEYLINE, cap_rect, width=1, border_radius=2)

    return pygame.transform.smoothscale(surf, (22, 22))
