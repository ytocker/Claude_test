"""GALLON JUG — gym/workout water-jug parcel cosmetic.

A big translucent gallon jug carried below Pip. The IDENTITY is BULK plus a
side carry HANDLE: the widest, squarest body of any drink parcel, with a loop
handle on the side that has a visible HOLE punched through it. That handle-with-
hole is the read no slim squeeze bottle can fake, so it carries the swap even
before colour. A yellow sport flip CAP sits offset on the shoulder (jug caps are
never centred) and a couple of measurement TICK marks climb the side to say
"workout jug, not bottle".

22px read tradeoffs (WHY): a real jug has a moulded neck, threads and a printed
scale; at 22px those vanish, so the shape is reduced to three legible masses — a
wide rounded-square BODY, a chunky offset CAP, and a bold side HANDLE with one
punched hole. The handle is drawn thick and the hole kept large (a 2px gap) so
the loop survives the downscale instead of filling solid; if the hole closes the
jug just reads as a blob. Only TWO short ticks are drawn — more becomes noise at
this size. The body is squarer and shorter than the slim squeeze bottle so the
silhouettes never collide, and the handle is biased toward the body centre so it
holds through the full tilt arc without clipping the work-surface edge. Drawn on
a 44px work surface then smoothscaled to 22 so the handle loop and ticks
antialias cleanly. A baked dark outline (inflated, drawn first) carries the
shape on bright DAY sky; a cool keyline rim inside is the NIGHT lifeline; the
whole jug is held off the surface edges so the rotozoom never clips cap or handle.
"""
import pygame

# Tight palette: translucent jug-blue body + deeper water, a saturated yellow
# sport cap (the grayscale-safe anchor against the cool blue), a dark outline for
# day and a cool keyline for night. Handle frame is a darker blue so the loop
# separates from the body mass.
JUG = ( 96, 168, 210)          # translucent jug-blue (upper body / air)
WATER = ( 62, 154, 214)        # deeper water blue (lower body)
WATER_HI = (170, 222, 248)     # meniscus / glint
HANDLE = ( 34,  86, 160)       # darker-blue handle frame (separates from body)
CAP = (242, 197,  58)          # yellow sport flip cap — the eye-magnet
CAP_HI = (255, 230, 150)       # cap top highlight
TICK = (234, 242, 248)         # measurement tick marks
OUTLINE = ( 30,  53,  80)      # dark, high-value: reads on bright day sky
KEYLINE = (208, 232, 246)      # cool rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static jug sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Body geometry. Wide-and-squat with a generous corner radius so it reads as
    # a bulky JUG, not a tall bottle. Biased LEFT so the side handle has room on
    # the right without clipping the surface edge under rotation.
    BW = 22                       # body width (the bulkiest parcel)
    BH = 22                       # body height (squat, shorter than a bottle)
    body_x = cx - BW // 2 - 2     # nudge left to make handle room on the right
    body_top = 14
    body_rect = pygame.Rect(body_x, body_top, BW, BH)
    body_rad = 6                  # big radius = jug shoulders

    # Cap: a chunky yellow block sat OFFSET on the shoulder (jug caps sit to one
    # side over a moulded neck), so it never centres like a bottle screw cap.
    CW, CH = 11, 8
    cap_x = body_rect.x + 3
    cap_rect = pygame.Rect(cap_x, body_top - 7, CW, CH)

    # Short neck collar bridging the offset cap into the shoulder.
    neck_rect = pygame.Rect(cap_x + 1, body_top - 2, CW - 2, 4)

    # Handle: a loop on the RIGHT side of the body with a punched hole. Outer
    # ring drawn first in outline, then frame colour, then the hole knocked back
    # to transparent so the loop reads even at the downscale.
    h_cx = body_rect.right + 1
    h_cy = body_rect.centery
    h_outer = 8                   # outer radius of the handle loop
    h_inner = 4                   # the punched hole (kept large so it survives)

    # --- Baked dark OUTLINE (drawn first, slightly inflated) for the DAY read.
    pygame.draw.circle(surf, OUTLINE, (h_cx, h_cy), h_outer + 2)
    pygame.draw.rect(surf, OUTLINE, cap_rect.inflate(4, 4), border_radius=2)
    pygame.draw.rect(surf, OUTLINE, neck_rect.inflate(4, 2))
    pygame.draw.rect(surf, OUTLINE, body_rect.inflate(4, 4),
                     border_radius=body_rad + 2)

    # --- HANDLE loop body (frame colour), drawn before the body so the body
    # mass overlaps its inner edge and the loop reads as attached to the jug.
    pygame.draw.circle(surf, HANDLE, (h_cx, h_cy), h_outer)

    # --- Bottle/jug BODY on its own alpha surface so the air/water split and the
    # rounded-square mask composite cleanly, then blitted in one piece.
    body = pygame.Surface((BW, BH), pygame.SRCALPHA)
    meniscus = int(BH * 0.34)     # water fills lower ~66% (full jug)
    body.fill(JUG + (240,), pygame.Rect(0, 0, BW, meniscus))
    for y in range(meniscus, BH):
        t = (y - meniscus) / max(1, BH - 1 - meniscus)
        c = (
            int(WATER_HI[0] + (WATER[0] - WATER_HI[0]) * t),
            int(WATER_HI[1] + (WATER[1] - WATER_HI[1]) * t),
            int(WATER_HI[2] + (WATER[2] - WATER_HI[2]) * t),
        )
        body.fill(c + (255,), pygame.Rect(0, y, BW, 1))
    mask = pygame.Surface((BW, BH), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=body_rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # --- Punch the HOLE through the handle: knock the centre back to transparent
    # AFTER the body is down, so the loop reads as open even on bright sky.
    pygame.draw.circle(surf, (0, 0, 0, 0), (h_cx, h_cy), h_inner)
    # Cool-light KEYLINE on the hole's inner edge (NOT a dark rim): on a dark
    # NIGHT sky a light rim makes the opening pop as an OPENING, not a dimple,
    # and it stays subtle on bright day.
    pygame.draw.circle(surf, KEYLINE, (h_cx, h_cy), h_inner, 1)

    # --- WATER LINE: a bright meniscus across the body — the "water" cue at true
    # size. Inset so it sits on the body, not the outline.
    my = body_rect.y + meniscus
    pygame.draw.line(surf, WATER_HI,
                     (body_rect.x + 3, my), (body_rect.right - 4, my), 2)

    # --- Vertical glint streak on the water (translucent-plastic cue). Kept SHORT
    # and starting below the lower tick so it doesn't merge with the ticks into one
    # vertical smudge on the left edge — the ticks own that column up top.
    glint_top = max(my + 2, body_rect.y + 13)
    pygame.draw.line(surf, WATER_HI,
                     (body_rect.x + 4, glint_top),
                     (body_rect.x + 4, body_rect.bottom - 5), 2)

    # --- Measurement TICK marks up the LEFT side — only two, drawn 2px tall and
    # against the OUTLINE so the contrast survives the smoothscale; any thinner
    # and the scale just dissolves at 22px.
    tx = body_rect.x + 3
    for ty in (body_rect.y + 5, body_rect.y + 10):
        pygame.draw.line(surf, OUTLINE, (tx, ty + 1), (tx + 5, ty + 1), 1)
        pygame.draw.line(surf, TICK, (tx, ty), (tx + 5, ty), 1)

    # --- NECK + CAP: yellow sport flip cap with a flat top highlight and a hard
    # groove at the cap/neck join (OUTLINE) so it reads as a flip lid, not paint.
    pygame.draw.rect(surf, JUG, neck_rect)
    pygame.draw.rect(surf, CAP, cap_rect, border_radius=2)
    pygame.draw.line(surf, CAP_HI,
                     (cap_rect.x + 2, cap_rect.y + 1),
                     (cap_rect.right - 3, cap_rect.y + 1), 1)
    pygame.draw.line(surf, OUTLINE,
                     (cap_rect.x, cap_rect.bottom - 1),
                     (cap_rect.right - 1, cap_rect.bottom - 1), 2)

    # --- Cool KEYLINE rim INSIDE the outline — the NIGHT lifeline. Traces the
    # jug body, the cap and the handle loop so the silhouette glows on dark sky.
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad)
    pygame.draw.rect(surf, KEYLINE, cap_rect, width=1, border_radius=2)
    pygame.draw.circle(surf, KEYLINE, (h_cx, h_cy), h_outer, 1)

    return pygame.transform.smoothscale(surf, (22, 22))
