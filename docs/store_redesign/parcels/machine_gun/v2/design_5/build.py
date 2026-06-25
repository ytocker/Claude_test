"""WATER BLASTER — super-soaker water gun parcel cosmetic.

A bright toy water gun carried below Pip, rotating with his bank. The IDENTITY
is the pairing of a chunky TEAL gun body with a translucent BLUE water RESERVOIR
TANK crowning UP over the rear, showing a bright WATER LINE (meniscus) so the tank
reads as a HALF-FULL vessel of water rather than a solid block. A forward NOZZLE
prong projecting into clear sky and a yellow PUMP accent finish the read — playful,
non-violent, and a sibling to the shipped WATER BOTTLE (a tall upright vessel;
this one is a horizontal blaster). The crowning half-full tank is the cue no
other parcel has, so it carries the read even before colour resolves.

22px read tradeoffs (WHY): at the 44->22 downscale a real soaker's vents and seams
dissolve, so the read is reduced to bold masses split by VALUE, not hue. The teal
body is pushed DARK + saturated and the lower water fill is darkened so there is a
HARD light/dark STEP at the meniscus — the meniscus is the single BRIGHTEST
horizontal line in the sprite, with a bright AIR gap held above it, so "half-full
water reservoir" reads by value even in grayscale. The translucent tank is pushed
UP and slightly REAR so it CROWNS above the body with a visible notch between them
(never one fused lump), and a clear filler-cap bump on the tank top keeps the
fillable-reservoir silhouette alive after downscale. The forward nozzle is
lengthened with clear sky gaps above AND below so a spout prong reads in the
below-Pip silhouette, capped with a warm muzzle dot. The rear hand-grip is dropped
(indistinct noise at 22px); the YELLOW pump is enlarged to carry the held end and
echoed by a tiny yellow trigger — yellow is the lone value anchor that survives
grayscale, so the palette stays teal + yellow + water-blue ONLY.

Drawn on a 44px work surface then smoothscaled to 22 so the meniscus and rim
antialias cleanly. A baked dark OUTLINE is laid first (inflated) so the blaster
reads on bright DAY sky; a cool KEYLINE rim rides the top edges so it still
separates on dark NIGHT sky from the same single sprite. Every mass sits ~4px off
the surface edges so the in-game rotozoom never clips the nozzle or tank at hard
bank.
"""
import pygame

# Bright toy palette: a DARK saturated soaker teal body so it steps away by value
# from the lighter translucent water tank; the tank splits into a darkened water
# fill + a bright air gap so the meniscus is the brightest line; a yellow pump is
# the grayscale-safe value anchor against the cool teal + blue.
TEAL = ( 14, 158, 144)        # soaker body / nozzle — dark, saturated mass
TEAL_HI = ( 70, 198, 184)     # body top rim lift
TEAL_SHADE = ( 9,  96,  88)   # body underside / nozzle shade — pushes the step
WATER = ( 30, 110, 176)       # darker translucent tank water (lower fill)
WATER_HI = (170, 224, 250)    # bright water glint / meniscus — the brightest line
AIR = (224, 244, 252)         # bright air gap above the water line
YELLOW = (245, 199,  52)      # pump grip / trigger accent — grayscale anchor
YELLOW_HI = (255, 232, 140)   # pump top highlight
OUTLINE = ( 16,  44,  54)     # dark, high-value: reads on bright day sky
KEYLINE = (176, 232, 236)     # cool rim — the NIGHT lifeline
MUZZLE = (255, 224, 150)      # tiny warm nozzle tip


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static water-blaster sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx, cy = S // 2, S // 2

    # --- silhouette geometry -------------------------------------------------
    # A horizontal blaster: dark teal BODY low and chunky; a translucent water
    # TANK crowning UP and slightly REAR so it sits ABOVE the body with a notch
    # between them; a LONG forward NOZZLE prong projecting left with clear sky
    # above and below; a chunky yellow PUMP slung down at the front as the held
    # end. All masses kept ~4px off every edge for the rotozoom.
    body = pygame.Rect(14, cy + 1, 19, 9)          # teal receiver body, low
    nozzle = pygame.Rect(3, cy + 2, 13, 5)         # LONG forward nozzle prong
    tank = pygame.Rect(18, cy - 11, 15, 10)        # tank crowning up + rear
    pump = pygame.Rect(10, cy + 8, 8, 7)           # enlarged yellow pump grip

    # --- baked outline pass (drawn first, inflated) --------------------------
    # One dark silhouette under every mass so the whole blaster reads on day sky.
    # The tank outline is kept SEPARATE from the body so the notch between them
    # survives — they must not merge into one inflated lump.
    pygame.draw.rect(surf, OUTLINE, tank.inflate(4, 4), border_radius=4)
    pygame.draw.rect(surf, OUTLINE, pump.inflate(4, 4), border_radius=2)
    pygame.draw.rect(surf, OUTLINE, body.inflate(4, 4), border_radius=4)
    pygame.draw.rect(surf, OUTLINE, nozzle.inflate(4, 4), border_radius=2)

    # --- yellow PUMP grip (front, slung down) --------------------------------
    # Enlarged toy accent that breaks the teal, carries the held end, and is the
    # one value anchor that survives grayscale.
    pygame.draw.rect(surf, YELLOW, pump, border_radius=2)
    pygame.draw.line(surf, YELLOW_HI,
                     (pump.x + 1, pump.y + 1), (pump.right - 2, pump.y + 1), 1)
    pygame.draw.line(surf, (200, 150, 30),
                     (pump.x + 1, pump.bottom - 1), (pump.right - 2, pump.bottom - 1), 1)

    # --- teal BODY + NOZZLE ---------------------------------------------------
    pygame.draw.rect(surf, TEAL, body, border_radius=4)
    pygame.draw.rect(surf, TEAL, nozzle, border_radius=2)
    # Strong underside shade so the body reads as a rounded dark volume and the
    # value step under the tank is hard.
    pygame.draw.line(surf, TEAL_SHADE, (body.x + 2, body.bottom - 1),
                     (body.right - 2, body.bottom - 1), 2)
    pygame.draw.line(surf, TEAL_SHADE, (nozzle.x + 1, nozzle.bottom - 1),
                     (nozzle.right - 1, nozzle.bottom - 1), 1)
    # Bright top rim along body + nozzle so the mass separates on NIGHT sky.
    pygame.draw.line(surf, TEAL_HI, (nozzle.x + 1, nozzle.y + 1),
                     (body.right - 3, body.y + 1), 2)

    # --- translucent water TANK (its own alpha surface, two-tone split) -------
    # A bright AIR gap over a DARKENED WATER fill so the meniscus reads as the
    # brightest water line — the cue that this is a half-full reservoir, not a
    # painted box. Built off the main surface so the split composites in one piece.
    tk = pygame.Surface((tank.w, tank.h), pygame.SRCALPHA)
    line = int(tank.h * 0.46)                       # water fills lower ~54% (half-full)
    tk.fill(AIR + (235,), pygame.Rect(0, 0, tank.w, line))
    for y in range(line, tank.h):
        t = (y - line) / max(1, tank.h - 1 - line)
        # Start just below the bright meniscus and deepen DOWN into dark water so
        # the top-of-fill stays well below AIR — that is the hard value step.
        c = (
            int(WATER_HI[0] + (WATER[0] - WATER_HI[0]) * (0.45 + 0.55 * t)),
            int(WATER_HI[1] + (WATER[1] - WATER_HI[1]) * (0.45 + 0.55 * t)),
            int(WATER_HI[2] + (WATER[2] - WATER_HI[2]) * (0.45 + 0.55 * t)),
        )
        tk.fill(c + (248,), pygame.Rect(0, y, tank.w, 1))
    # Round the tank corners so it reads as a soft toy reservoir.
    mask = pygame.Surface((tank.w, tank.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=4)
    tk.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tk, tank.topleft)
    # Bright meniscus across the tank — the single BRIGHTEST horizontal line.
    my = tank.y + line
    pygame.draw.line(surf, WATER_HI, (tank.x + 2, my), (tank.right - 3, my), 2)
    # A glint on the water below the line — the translucent-plastic cue.
    pygame.draw.line(surf, WATER_HI, (tank.x + 3, my + 2),
                     (tank.x + 3, tank.bottom - 3), 2)
    # Filler-cap bump on the tank top — a clear nub so the fillable-reservoir
    # silhouette survives downscale and the one-lump read is broken.
    cap = pygame.Rect(tank.x + 4, tank.y - 3, 5, 3)
    pygame.draw.rect(surf, OUTLINE, cap.inflate(2, 1), border_radius=1)
    pygame.draw.rect(surf, TEAL, cap, border_radius=1)
    pygame.draw.line(surf, TEAL_HI, (cap.x + 1, cap.y + 1), (cap.right - 1, cap.y + 1), 1)

    # --- nozzle muzzle tip ----------------------------------------------------
    # A tiny warm cap on the spout so the "this end squirts" read is pinned,
    # kept to ~2px so the tip stays a prong, not a mouth.
    pygame.draw.circle(surf, MUZZLE, (nozzle.x + 1, cy + 4), 2)
    pygame.draw.circle(surf, OUTLINE, (nozzle.x + 1, cy + 4), 2, 1)

    # --- yellow trigger accent (echoes the pump under the body front) ---------
    pygame.draw.rect(surf, YELLOW, pygame.Rect(20, cy + 7, 2, 3), border_radius=1)

    # --- cool NIGHT keyline along the top run of body + tank -----------------
    # Rides just inside the outline so the teal + tank still separate from a dark
    # sky from the same single sprite.
    pygame.draw.line(surf, KEYLINE, (nozzle.x, nozzle.y),
                     (body.right - 2, body.y), 1)
    pygame.draw.rect(surf, KEYLINE, tank, width=1, border_radius=4)

    return pygame.transform.smoothscale(surf, (22, 22))
