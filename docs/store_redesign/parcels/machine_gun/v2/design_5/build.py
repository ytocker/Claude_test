"""WATER BLASTER — super-soaker water gun parcel cosmetic.

A bright toy water gun carried below Pip, rotating with his bank. The IDENTITY
is the pairing of a chunky TEAL gun body with a translucent BLUE water RESERVOIR
TANK sitting up on top, showing a bright WATER LINE (meniscus) so the tank reads
as a half-full vessel of water rather than a solid block. A stubby forward NOZZLE
and a yellow PUMP/grip accent finish the read — playful, non-violent, and a
sibling to the WATER BOTTLE already in the roster. The water tank is the cue no
other parcel has, so it carries the read even before colour resolves.

22px read tradeoffs (WHY): at the 44->22 downscale a real soaker's vents and seams
dissolve, so the read is reduced to three bold masses with hard VALUE separation —
the teal body (lower, biggest), the lighter translucent tank (upper, offset so the
two never fuse into one lump), and a short forward nozzle stub. The tank is built
on its own alpha surface with a bright AIR gap above a deeper WATER fill so the
meniscus pops; this two-tone split is what survives the downscale and keeps it
reading as WATER, not a painted box. The nozzle is kept short and capped with a
warm muzzle dot so the tip never bulbs into a cannon mouth. A yellow pump accent
breaks the teal so the held end stays asymmetric and the eye finds a toy.

Drawn on a 44px work surface then smoothscaled to 22 so the meniscus and rim
keylines antialias cleanly. A baked dark OUTLINE is laid first (inflated) so the
blaster reads on bright DAY sky; a cool KEYLINE rim rides the top edges so the
teal still separates on dark NIGHT sky from the same single sprite. Every mass
sits ~4px off the surface edges so the in-game rotozoom never clips the nozzle or
tank at hard bank.
"""
import pygame

# Bright toy palette: a saturated soaker teal body, a translucent water tank that
# splits into a deeper water fill + a bright air gap so the meniscus reads, and a
# yellow pump accent as the grayscale-safe eye-magnet against the cool teal.
TEAL = ( 31, 182, 166)        # soaker body / nozzle — the bright toy mass
TEAL_HI = ( 96, 220, 206)     # body top rim lift
TEAL_SHADE = ( 18, 120, 110)  # body underside / nozzle shade
WATER = ( 46, 143, 208)       # deeper translucent tank water (lower fill)
WATER_HI = (140, 210, 244)    # lighter water / meniscus glint
AIR = (214, 238, 250)         # bright air gap above the water line
YELLOW = (242, 197,  58)      # pump grip / trigger accent
OUTLINE = ( 18,  48,  58)     # dark, high-value: reads on bright day sky
KEYLINE = (176, 232, 236)     # cool rim — the NIGHT lifeline
MUZZLE = (255, 224, 150)      # tiny warm nozzle tip


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static water-blaster sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx, cy = S // 2, S // 2

    # --- silhouette geometry -------------------------------------------------
    # A horizontal blaster: teal BODY low and chunky, a translucent water TANK
    # offset UP over the rear two-thirds, a short forward NOZZLE projecting left,
    # and a yellow PUMP grip slung down at the front. Tank is offset (not centred)
    # so body+tank read as two stacked masses, not one rounded blob. All masses
    # kept ~4px off every edge for the rotozoom.
    body = pygame.Rect(13, cy + 1, 20, 9)          # teal receiver body, low
    nozzle = pygame.Rect(4, cy + 2, 12, 6)         # short forward nozzle, left
    tank = pygame.Rect(16, cy - 9, 16, 11)         # translucent water tank, up + rear
    pump = pygame.Rect(11, cy + 8, 6, 6)           # yellow front pump grip, down
    grip = [(28, cy + 9), (33, cy + 9), (31, cy + 15), (26, cy + 15)]  # rear hand grip

    # --- baked outline pass (drawn first, inflated) --------------------------
    # One dark silhouette under every mass so the whole blaster reads on day sky.
    pygame.draw.rect(surf, OUTLINE, tank.inflate(4, 4), border_radius=4)
    pygame.draw.rect(surf, OUTLINE, pump.inflate(4, 4), border_radius=2)
    pygame.draw.polygon(surf, OUTLINE,
                        [(25, cy + 8), (34, cy + 8), (32, cy + 16), (25, cy + 16)])
    pygame.draw.rect(surf, OUTLINE, body.inflate(4, 4), border_radius=4)
    pygame.draw.rect(surf, OUTLINE, nozzle.inflate(4, 4), border_radius=2)

    # --- rear hand grip (warm-neutral teal-shade, drawn under the body) -------
    pygame.draw.polygon(surf, TEAL_SHADE, grip)

    # --- yellow PUMP grip (front, slung down) --------------------------------
    # The toy accent that breaks the teal and pins the "held / pumped" read.
    pygame.draw.rect(surf, YELLOW, pump, border_radius=2)
    pygame.draw.line(surf, (255, 232, 140),
                     (pump.x + 1, pump.y + 1), (pump.right - 2, pump.y + 1), 1)

    # --- teal BODY + NOZZLE ---------------------------------------------------
    pygame.draw.rect(surf, TEAL, body, border_radius=4)
    pygame.draw.rect(surf, TEAL, nozzle, border_radius=2)
    # Underside shade so the body reads as a rounded volume, not a flat slab.
    pygame.draw.line(surf, TEAL_SHADE, (body.x + 2, body.bottom - 1),
                     (body.right - 2, body.bottom - 1), 2)
    # Bright top rim along body + nozzle so the mass separates on NIGHT sky.
    pygame.draw.line(surf, TEAL_HI, (nozzle.x + 1, nozzle.y + 1),
                     (body.right - 3, body.y + 1), 2)

    # --- translucent water TANK (its own alpha surface, two-tone split) -------
    # A bright AIR gap over a deeper WATER fill so the meniscus reads as a water
    # line — the cue that this is a water reservoir, not a painted box. Built off
    # the main surface so the air/water split composites cleanly in one piece.
    tk = pygame.Surface((tank.w, tank.h), pygame.SRCALPHA)
    line = int(tank.h * 0.42)                       # water fills lower ~58%
    tk.fill(AIR + (235,), pygame.Rect(0, 0, tank.w, line))
    for y in range(line, tank.h):
        t = (y - line) / max(1, tank.h - 1 - line)
        c = (
            int(WATER_HI[0] + (WATER[0] - WATER_HI[0]) * t),
            int(WATER_HI[1] + (WATER[1] - WATER_HI[1]) * t),
            int(WATER_HI[2] + (WATER[2] - WATER_HI[2]) * t),
        )
        tk.fill(c + (245,), pygame.Rect(0, y, tank.w, 1))
    # Round the tank corners so it reads as a soft toy reservoir.
    mask = pygame.Surface((tank.w, tank.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=4)
    tk.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tk, tank.topleft)
    # Bright meniscus across the tank — the load-bearing "water" line.
    my = tank.y + line
    pygame.draw.line(surf, WATER_HI, (tank.x + 2, my), (tank.right - 3, my), 2)
    # A glint on the water below the line — the translucent-plastic cue.
    pygame.draw.line(surf, WATER_HI, (tank.x + 3, my + 2),
                     (tank.x + 3, tank.bottom - 3), 2)
    # Filler cap notch on the tank top so it reads as a fillable reservoir.
    pygame.draw.rect(surf, TEAL, pygame.Rect(tank.right - 7, tank.y - 1, 4, 2),
                     border_radius=1)

    # --- nozzle muzzle tip ----------------------------------------------------
    # A tiny warm cap on the spout so the "this end squirts" read is pinned,
    # kept to ~2px so the tip stays a stub, not a mouth.
    pygame.draw.circle(surf, MUZZLE, (nozzle.x + 1, cy + 5), 2)
    pygame.draw.circle(surf, OUTLINE, (nozzle.x + 1, cy + 5), 2, 1)

    # --- trigger dot ----------------------------------------------------------
    pygame.draw.circle(surf, YELLOW, (25, cy + 7), 1)

    # --- cool NIGHT keyline along the top run of body + tank -----------------
    # Rides just inside the outline so the teal + tank still separate from a dark
    # sky from the same single sprite.
    pygame.draw.line(surf, KEYLINE, (nozzle.x, nozzle.y),
                     (body.right - 2, body.y), 1)
    pygame.draw.rect(surf, KEYLINE, tank, width=1, border_radius=4)

    return pygame.transform.smoothscale(surf, (22, 22))
