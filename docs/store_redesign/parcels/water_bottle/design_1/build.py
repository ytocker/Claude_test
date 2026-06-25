"""WATER BOTTLE — clear sports-bottle parcel cosmetic.

A clear plastic sports bottle carried upright below Pip. The IDENTITY is the
bottle SILHOUETTE — a rounded body with a stepped-in NECK and a bold coloured
CAP — plus the WATER LINE (a clear meniscus where the blue water meets the
empty air space in the upper third). No other parcel is a tall, capped vessel,
so the upright-bottle outline carries the read even before the colour lands.

22px read tradeoffs (WHY): a real bottle has many subtle curves and a thin
clear top; at 22px those collapse, so the shape is reduced to three legible
masses — CAP (saturated red, the eye-magnet that survives grayscale against the
blue), a short NECK step, and the rounded BODY. The water fill is kept to the
lower ~2/3 with ONE bright meniscus line, because a soft gradient alone would
not read as "water" — the hard light line is the cue. The body is TALLER than
wide (a vertical accent in a roster of flat slabs) which also keeps the cap
distinct from the body under rotation: a tilted bottle still shows cap-then-body
ordering. A single vertical glint streak gives the plastic its translucency
without micro-detail. A thin label band breaks the body so it doesn't read as a
plain pill. Drawn on a 44px work surface then smoothscaled to 22 so the neck
step and meniscus antialias cleanly. A baked dark outline (inflated, drawn
first) carries the shape on bright DAY sky; a cool keyline rim inside is the
NIGHT lifeline; the bottle is held off the surface edges so the rotozoom never
clips the cap.
"""
import pygame

# Tight palette: translucent water blue + a lighter air/highlight, a saturated
# sport-red cap (the grayscale-safe anchor against the blue), a dark outline for
# day, and a cool keyline for night.
WATER = ( 50, 138, 210)        # translucent water blue (lower body)
WATER_HI = (130, 202, 244)     # lighter water / glint / meniscus
AIR = (214, 234, 247)          # empty air space above the meniscus (pale blue)
CAP = (212,  58,  52)          # sport-red screw cap — the eye-magnet
CAP_HI = (240, 138, 130)       # cap top edge highlight
OUTLINE = ( 30,  36,  48)      # dark, high-value: reads on bright day sky
KEYLINE = (210, 232, 246)      # cool rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static bottle sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Bottle geometry. Tall-and-narrow so the upright-vessel read is unmistakable
    # and the cap stays distinct from the body. Held off the surface edges so the
    # gameplay rotozoom never clips the cap or base.
    BW = 18                       # body width
    body_top = 13                 # where the rounded body starts (below neck)
    body_bot = 37                 # base of the bottle
    body_rect = pygame.Rect(cx - BW // 2, body_top, BW, body_bot - body_top)
    body_rad = 6                  # rounded shoulders + base

    # Neck: a short narrower step bridging body and cap.
    NW = 8
    neck_rect = pygame.Rect(cx - NW // 2, 11, NW, 4)

    # Cap: a bold coloured block on top, slightly wider than the neck. Kept
    # chunky so it stays the colour anchor even when the bottle banks to 90deg.
    CW, CH = 13, 8
    cap_rect = pygame.Rect(cx - CW // 2, 3, CW, CH)

    # --- Baked dark outline (drawn first, slightly inflated) for the DAY read.
    pygame.draw.rect(surf, OUTLINE, cap_rect.inflate(4, 4), border_radius=2)
    pygame.draw.rect(surf, OUTLINE, neck_rect.inflate(4, 3))
    pygame.draw.rect(surf, OUTLINE, body_rect.inflate(4, 4),
                     border_radius=body_rad + 1)

    # --- Bottle BODY built on its own alpha surface so the air/water split and
    # the masked rounded shape composite cleanly, then blitted in one piece.
    body = pygame.Surface((body_rect.w, body_rect.h), pygame.SRCALPHA)
    meniscus = int(body_rect.h * 0.34)   # water fills lower ~2/3
    # Empty air space above the water line (pale, slightly translucent).
    body.fill(AIR + (235,), pygame.Rect(0, 0, body_rect.w, meniscus))
    # Water fill below: a gentle vertical deepening so it reads as a volume.
    for y in range(meniscus, body_rect.h):
        t = (y - meniscus) / max(1, body_rect.h - 1 - meniscus)
        c = (
            int(WATER_HI[0] + (WATER[0] - WATER_HI[0]) * t),
            int(WATER_HI[1] + (WATER[1] - WATER_HI[1]) * t),
            int(WATER_HI[2] + (WATER[2] - WATER_HI[2]) * t),
        )
        body.fill(c + (255,), pygame.Rect(0, y, body_rect.w, 1))
    # Mask the body to the rounded-rect bottle shape.
    mask = pygame.Surface((body_rect.w, body_rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=body_rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # --- WATER LINE: a bright meniscus across the body, the cue that reads as
    # "water" at true size. Drawn a touch inset so it sits on the body, not the
    # outline, and kept bright so it survives the downscale.
    my = body_rect.y + meniscus
    pygame.draw.line(surf, WATER_HI,
                     (body_rect.x + 2, my), (body_rect.right - 3, my), 2)

    # --- Label band across the middle of the body — a thin neutral strip so the
    # bottle isn't a plain pill. Kept low-contrast so it never competes with the
    # cap or the water line.
    lb_y = body_rect.y + int(body_rect.h * 0.58)
    pygame.draw.rect(surf, AIR,
                     pygame.Rect(body_rect.x + 2, lb_y, body_rect.w - 4, 4))
    pygame.draw.line(surf, OUTLINE,
                     (body_rect.x + 2, lb_y), (body_rect.right - 3, lb_y), 1)
    pygame.draw.line(surf, OUTLINE,
                     (body_rect.x + 2, lb_y + 3), (body_rect.right - 3, lb_y + 3), 1)

    # --- Vertical glint streak down the left side — the plastic translucency cue.
    pygame.draw.line(surf, WATER_HI,
                     (body_rect.x + 4, body_rect.y + 4),
                     (body_rect.x + 4, body_rect.bottom - 5), 2)

    # --- NECK fill (sits between body shoulders and cap).
    pygame.draw.rect(surf, AIR, neck_rect)

    # --- CAP: saturated red block with a top highlight + a ring groove so it
    # reads as a screw cap, not a plain box.
    pygame.draw.rect(surf, CAP, cap_rect, border_radius=2)
    pygame.draw.line(surf, CAP_HI,
                     (cap_rect.x + 1, cap_rect.y + 1),
                     (cap_rect.right - 2, cap_rect.y + 1), 1)
    pygame.draw.line(surf, OUTLINE,
                     (cap_rect.x + 1, cap_rect.bottom - 2),
                     (cap_rect.right - 2, cap_rect.bottom - 2), 1)

    # --- Cool keyline rim INSIDE the outline — the NIGHT lifeline that glows on
    # dark sky while staying subtle on day. Traces the body + cap silhouette.
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad)
    pygame.draw.rect(surf, KEYLINE, cap_rect, width=1, border_radius=2)

    return pygame.transform.smoothscale(surf, (22, 22))
