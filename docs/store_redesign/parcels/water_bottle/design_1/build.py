"""WATER BOTTLE — sports squeeze-bottle parcel cosmetic.

A clear plastic squeeze-bottle carried upright below Pip. The IDENTITY is the
bottle SILHOUETTE — STRAIGHT vertical side walls (a cycling/sports squeeze
bottle, not a curvy mineral-water bottle), a tucked-in SHOULDER stepping down to
a narrow NECK, and a bold coloured screw CAP — plus ONE bright WATER LINE
(meniscus) sitting high so the bottle reads FULL. No other parcel is a tall,
straight-walled capped vessel, so the outline carries the read even before colour.

22px read tradeoffs (WHY): a real bottle has many subtle curves; at 22px those
collapse into a lozenge, so the shape is reduced to legible masses with STRAIGHT
side walls — the single biggest bottle cue under rotation, since a curvy body
just reads as a pill at any bank. The body corner radius is tiny and biased to
the BASE so the bottom rounds while the side walls stay vertical. An explicit
shoulder diagonal (1px darker) tucks the body wall into the neck so the cap and
body never fuse into one mass at the downscale. Inside the body we keep ONLY
three cues — one meniscus, one air/water split, one glint on the WATER — because
at 22px any label band just muddies the silhouette. The fill is raised to ~70%
(meniscus near the upper third) so the bottle reads FULL; the air gap above is
brighter so the contrast at the water line is sharp. The cap is widened a step
and its groove hardened to OUTLINE colour so it reads as a screw-on lid, not a
painted red stripe, with a clearly flat top edge. Drawn on a 44px work surface
then smoothscaled to 22 so the shoulder and meniscus antialias cleanly. A baked
dark outline (inflated, drawn first) carries the shape on bright DAY sky; a cool
keyline rim inside is the NIGHT lifeline; the bottle is held off the surface
edges so the rotozoom never clips the cap.
"""
import pygame

# Tight palette: translucent water blue + a lighter air/highlight, a saturated
# sport-red cap (the grayscale-safe anchor against the blue), a dark outline for
# day, and a cool keyline for night.
WATER = ( 46, 132, 206)        # translucent water blue (lower body)
WATER_HI = (140, 208, 246)     # lighter water / glint / meniscus
AIR = (224, 240, 250)          # empty air space above the meniscus (bright)
CAP = (212,  58,  52)          # sport-red screw cap — the eye-magnet
CAP_HI = (240, 138, 130)       # cap top edge highlight
OUTLINE = ( 30,  36,  48)      # dark, high-value: reads on bright day sky
KEYLINE = (210, 232, 246)      # cool rim — the NIGHT lifeline
SHOULDER = ( 36,  92, 150)     # 1px-darker shoulder tuck into the neck


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static bottle sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Bottle geometry. Tall-and-narrow with STRAIGHT side walls so the
    # upright-vessel read survives rotation. Held off the surface edges so the
    # gameplay rotozoom never clips the cap or base.
    BW = 18                       # body width (straight side walls)
    body_top = 16                 # where the straight body wall starts (below shoulder)
    body_bot = 38                 # base of the bottle
    body_rect = pygame.Rect(cx - BW // 2, body_top, BW, body_bot - body_top)
    body_rad = 3                  # tiny radius, biased to the base below

    # Neck: a narrow step bridging the shoulder and the cap.
    NW = 6
    neck_top = 11
    neck_rect = pygame.Rect(cx - NW // 2, neck_top, NW, 5)

    # Shoulder zone: the diagonal tuck from the wide body wall up into the narrow
    # neck. Lives in the gap between body_top and neck bottom.
    sh_top = neck_rect.bottom     # 16 — top of the shoulder band == body_top
    # (body_top is set equal so the shoulder diagonal seats on the body wall.)

    # Cap: a bold coloured block, one step wider than R1, slightly wider than the
    # neck. Chunky so it stays the colour anchor even when banked to 90deg, with
    # a flat top edge.
    CW, CH = 14, 8
    cap_rect = pygame.Rect(cx - CW // 2, 3, CW, CH)

    # --- Baked dark outline (drawn first, slightly inflated) for the DAY read.
    pygame.draw.rect(surf, OUTLINE, cap_rect.inflate(4, 4), border_radius=2)
    pygame.draw.rect(surf, OUTLINE, neck_rect.inflate(4, 3))
    # Shoulder + body outline as one bottom-rounded block.
    sh_outline = pygame.Rect(body_rect.x, neck_rect.bottom - 1, body_rect.w,
                             body_rect.bottom - (neck_rect.bottom - 1))
    pygame.draw.rect(surf, OUTLINE, sh_outline.inflate(4, 4),
                     border_radius=body_rad + 2)

    # --- Shoulder tuck: two darker diagonals from the body wall corners up into
    # the neck, so the cap/neck and body never fuse into one mass at downscale.
    sh_y = neck_rect.bottom                       # 16
    pygame.draw.polygon(surf, SHOULDER, [
        (body_rect.x, body_top + 2),
        (neck_rect.x, sh_y - 1),
        (neck_rect.x, sh_y + 1),
        (body_rect.x, body_top + 4),
    ])
    pygame.draw.polygon(surf, SHOULDER, [
        (body_rect.right, body_top + 2),
        (neck_rect.right, sh_y - 1),
        (neck_rect.right, sh_y + 1),
        (body_rect.right, body_top + 4),
    ])
    # Fill the shoulder triangle interior so the body wall meets the neck cleanly.
    pygame.draw.polygon(surf, AIR, [
        (body_rect.x + 1, body_top + 3),
        (neck_rect.x, sh_y),
        (neck_rect.right, sh_y),
        (body_rect.right - 1, body_top + 3),
    ])

    # --- Bottle BODY built on its own alpha surface so the air/water split and
    # the masked straight-walled shape composite cleanly, then blitted in one piece.
    body = pygame.Surface((body_rect.w, body_rect.h), pygame.SRCALPHA)
    meniscus = int(body_rect.h * 0.30)   # water fills lower ~70% (full bottle)
    # Empty air space above the water line (bright, so the meniscus pops).
    body.fill(AIR + (240,), pygame.Rect(0, 0, body_rect.w, meniscus))
    # Water fill below: a gentle vertical deepening so it reads as a volume.
    for y in range(meniscus, body_rect.h):
        t = (y - meniscus) / max(1, body_rect.h - 1 - meniscus)
        c = (
            int(WATER_HI[0] + (WATER[0] - WATER_HI[0]) * t),
            int(WATER_HI[1] + (WATER[1] - WATER_HI[1]) * t),
            int(WATER_HI[2] + (WATER[2] - WATER_HI[2]) * t),
        )
        body.fill(c + (255,), pygame.Rect(0, y, body_rect.w, 1))
    # Mask to a STRAIGHT-WALLED shape: only the bottom corners round.
    mask = pygame.Surface((body_rect.w, body_rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=body_rad, border_top_left_radius=0,
                     border_top_right_radius=0)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # --- WATER LINE: a bright meniscus across the body, the cue that reads as
    # "water" at true size. Inset so it sits on the body, not the outline, and
    # kept bright so it survives the downscale.
    my = body_rect.y + meniscus
    pygame.draw.line(surf, WATER_HI,
                     (body_rect.x + 2, my), (body_rect.right - 3, my), 2)

    # --- Vertical glint streak on the WATER (lower body) — the plastic
    # translucency cue, kept below the meniscus so it reads as light on water.
    pygame.draw.line(surf, WATER_HI,
                     (body_rect.x + 4, my + 2),
                     (body_rect.x + 4, body_rect.bottom - 4), 2)

    # --- NECK fill (sits between the shoulder tuck and the cap).
    pygame.draw.rect(surf, AIR, neck_rect)

    # --- CAP: saturated red block with a flat top highlight + a hard groove at
    # the cap/neck join (OUTLINE colour) so it reads as a screw-on lid.
    pygame.draw.rect(surf, CAP, cap_rect, border_radius=2)
    pygame.draw.line(surf, CAP_HI,
                     (cap_rect.x + 2, cap_rect.y + 1),
                     (cap_rect.right - 3, cap_rect.y + 1), 1)
    # Hard cap/neck groove — a full-width dark line so the lid screws on.
    pygame.draw.line(surf, OUTLINE,
                     (cap_rect.x, cap_rect.bottom - 1),
                     (cap_rect.right - 1, cap_rect.bottom - 1), 2)

    # --- Cool keyline rim INSIDE the outline — the NIGHT lifeline that glows on
    # dark sky while staying subtle on day. Traces the straight body wall + cap.
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad,
                     border_top_left_radius=0, border_top_right_radius=0)
    pygame.draw.rect(surf, KEYLINE, cap_rect, width=1, border_radius=2)

    return pygame.transform.smoothscale(surf, (22, 22))
