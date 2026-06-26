"""CRYSTAL DECANTER — cut-crystal spirits decanter parcel cosmetic.

The IDENTITY is the heavy faceted-crystal read: a SQUAT, WIDE-SHOULDERED
decanter body (much wider than it is tall, unlike the slim bottle parcels),
filled with AMBER whiskey behind a bright meniscus, and capped by a fat round
KNOB stopper on a short pinched neck. The amber liquid + the squat faceted glass
mass + the knob stopper are the three beats that make it read as fine whiskey,
not a water bottle.

22px read tradeoffs (WHY): facets are suggested with 1-2 COMMITTED diagonal
sheen lines plus a single angled shoulder cut, not a fussy cut-crystal grid that
would alias to mud at the downscale — the heavy silhouette and the bold amber
mass do the work, the sheen just says "glass, not plastic". The body is filled
almost entirely with amber (the whiskey is the loudest cue) with only a thin
clear-glass band above the bright meniscus, so the warm mass survives rotation
and grayscale. The knob stopper is kept FAT and round on a short pinched neck so
it stays a distinct top beat — a slim cap would fuse into the wide shoulder when
banked. Drawn on a 44px work surface then smoothscaled to 22 so the facet sheen
and stopper curve antialias cleanly. A baked dark OUTLINE (inflated, drawn first)
carries the shape on bright DAY sky; a cool KEYLINE rim inside is the NIGHT
lifeline; the decanter is held well off the surface edges so the gameplay
rotozoom never clips the knob stopper or the wide base.
"""
import pygame

# Tight palette from the concept: cool crystal glass, a warm amber fill with a
# bright highlight, a gold knob accent, plus the day-outline / night-keyline.
GLASS = (207, 224, 230)       # cool cut-crystal glass (clear band + facet sheen)
GLASS_HI = (240, 248, 250)    # sharp glass glint / sheen line
AMBER = (200, 121, 30)        # amber whiskey body fill
AMBER_LO = (150, 86, 18)      # deeper amber low in the body (volume)
AMBER_HI = (240, 180, 90)     # bright amber highlight under the meniscus
GOLD = (227, 178, 60)         # gold tell on the knob stopper
MENISCUS = (250, 232, 190)    # bright liquid-surface line
OUTLINE = (42, 36, 24)        # dark, warm: reads on bright day sky
KEYLINE = (214, 230, 236)     # cool rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static decanter sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Geometry: a SQUAT wide-shouldered body, a short pinched neck, and a fat
    # round knob stopper. Held off the surface edges so the rotozoom never clips.
    BW = 28                       # wide body (the heavy-crystal mass)
    body_top = 20                 # shoulder line (sits low so the body is squat)
    body_bot = 38                 # wide flat base
    body_rect = pygame.Rect(cx - BW // 2, body_top, BW, body_bot - body_top)
    body_rad = 4

    # Shoulder: the body widens out HARD from a narrow neck — a tall, steep
    # trapezoid cap so the wide-shouldered decanter silhouette is unmistakable
    # (the steep flare is the decanter tell vs. a straight-walled bottle).
    sh_top = 13                   # where the shoulder meets the neck step
    sh_lx = cx - 5                # narrow top of the shoulder (neck width-ish)
    sh_rx = cx + 5

    # Neck: a SHORT pinched step bridging the shoulder to the knob.
    NW = 8
    neck_rect = pygame.Rect(cx - NW // 2, 9, NW, 5)

    # Knob stopper: a FAT round faceted knob — the premium top beat.
    knob_r = 6
    knob_cy = 7

    # --- Baked dark outline (drawn first, slightly inflated) for the DAY read.
    pygame.draw.circle(surf, OUTLINE, (cx, knob_cy), knob_r + 2)
    pygame.draw.rect(surf, OUTLINE, neck_rect.inflate(4, 3))
    # Shoulder trapezoid outline (inflated by drawing a slightly larger polygon).
    pygame.draw.polygon(surf, OUTLINE, [
        (sh_lx - 2, sh_top - 1),
        (sh_rx + 2, sh_top - 1),
        (body_rect.right + 2, body_top + 3),
        (body_rect.x - 2, body_top + 3),
    ])
    pygame.draw.rect(surf, OUTLINE, body_rect.inflate(4, 4), border_radius=body_rad + 2)

    # --- Shoulder fill: the angled crystal shoulder cut between neck and body.
    pygame.draw.polygon(surf, GLASS, [
        (sh_lx, sh_top),
        (sh_rx, sh_top),
        (body_rect.right, body_top + 2),
        (body_rect.x, body_top + 2),
    ])

    # --- BODY built on its own alpha surface: a thin clear-glass band on top,
    # then the amber whiskey fill below the meniscus, masked to the squat shape.
    bw, bh = body_rect.w, body_rect.h
    body = pygame.Surface((bw, bh), pygame.SRCALPHA)

    # Meniscus sits high so the body is almost all amber — the whiskey is the
    # loudest cue and a fat warm mass survives the downscale + rotation.
    fill_top = int(bh * 0.22)

    # Clear crystal band above the liquid surface.
    body.fill(GLASS + (245,), pygame.Rect(0, 0, bw, fill_top))
    # Amber whiskey: a vertical deepening from the bright top to a richer base.
    for y in range(fill_top, bh):
        t = (y - fill_top) / max(1, bh - 1 - fill_top)
        if t < 0.35:
            tt = t / 0.35
            c = (
                int(AMBER_HI[0] + (AMBER[0] - AMBER_HI[0]) * tt),
                int(AMBER_HI[1] + (AMBER[1] - AMBER_HI[1]) * tt),
                int(AMBER_HI[2] + (AMBER[2] - AMBER_HI[2]) * tt),
            )
        else:
            tt = (t - 0.35) / 0.65
            c = (
                int(AMBER[0] + (AMBER_LO[0] - AMBER[0]) * tt),
                int(AMBER[1] + (AMBER_LO[1] - AMBER[1]) * tt),
                int(AMBER[2] + (AMBER_LO[2] - AMBER[2]) * tt),
            )
        body.fill(c + (255,), pygame.Rect(0, y, bw, 1))

    # Bright meniscus line at the liquid surface — the loud "this is liquid" cue.
    pygame.draw.line(body, MENISCUS, (1, fill_top), (bw - 2, fill_top), 2)

    # Mask to a squat shape: base corners round, top stays square under shoulder.
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=body_rad, border_top_left_radius=1,
                     border_top_right_radius=1)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # --- FACET sheen: 1-2 committed diagonal glass glints across the body so it
    # reads as cut crystal, not a smooth plastic bottle. A bright primary glint
    # high-left and a fainter secondary lower-right suggest the diamond cut.
    pygame.draw.line(surf, GLASS_HI,
                     (body_rect.x + 4, body_rect.y + 3),
                     (body_rect.x + 9, body_rect.bottom - 5), 2)
    pygame.draw.line(surf, GLASS_HI,
                     (body_rect.right - 6, body_rect.y + 5),
                     (body_rect.right - 4, body_rect.bottom - 6), 1)
    # A single angled shoulder facet cut so the crystal read carries up top.
    pygame.draw.line(surf, GLASS_HI,
                     (cx - 5, sh_top + 1), (body_rect.x + 3, body_top + 1), 1)

    # --- NECK fill (between the shoulder and the knob).
    pygame.draw.rect(surf, GLASS, neck_rect)

    # --- KNOB stopper: a fat round faceted knob. Gold-tinted with a glass glint
    # and a hard groove at the knob/neck join so it reads as a seated stopper.
    pygame.draw.circle(surf, GOLD, (cx, knob_cy), knob_r)
    # Faceted knob: a brighter top-left arc highlight + a darker lower amber tuck.
    pygame.draw.circle(surf, GLASS_HI, (cx - 2, knob_cy - 2), 2)
    pygame.draw.line(surf, OUTLINE,
                     (cx - knob_r + 1, knob_cy + knob_r - 1),
                     (cx + knob_r - 1, knob_cy + knob_r - 1), 1)
    # Hard groove where the knob seats on the neck.
    pygame.draw.line(surf, OUTLINE,
                     (neck_rect.x, neck_rect.y),
                     (neck_rect.right - 1, neck_rect.y), 2)

    # --- Cool keyline rim INSIDE the outline — the NIGHT lifeline. Traces the
    # body wall, the shoulder, and the knob so each beat glows on dark sky.
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad,
                     border_top_left_radius=1, border_top_right_radius=1)
    pygame.draw.line(surf, KEYLINE, (sh_lx, sh_top), (body_rect.x + 1, body_top + 1), 1)
    pygame.draw.line(surf, KEYLINE, (sh_rx, sh_top), (body_rect.right - 1, body_top + 1), 1)
    pygame.draw.circle(surf, KEYLINE, (cx, knob_cy), knob_r, width=1)

    return pygame.transform.smoothscale(surf, (22, 22))
