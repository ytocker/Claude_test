"""GATLING GUN — hand-cranked rotary brass parcel cosmetic.

A rotary gatling carried below Pip, rotating with his bank. The identity beat is
a horizontal CLUSTER of parallel barrels projecting forward from a round brass
breech hub, with a hand-crank at the back — a bundle of barrels reads "rotary /
gatling" the way no single-barrel gun can, so the bundle is the load-bearing
mass and the round brass hub is the warm rotary "engine" it spins around.

22px read tradeoffs: at the 44->22 downscale the individual barrels would smear
into one bar, so they are drawn as a small odd count (3) of fat parallel rods
with WIDE dark sky-gap seams BETWEEN them — the seams, not the rods, are what
survive the downscale and sell "more than one barrel", so they are protected as
the identity and never allowed to slab into one block. The crank is the second
tell: a knob-on-a-stick reads as a magnifying lens at this size, so it is built
as a real crank THROW instead — a short steel arm dropping off the hub rear and
a short PERPENDICULAR grip bar at its end. That elbow silhouette reads "hand
cranked" where a round knob read "loupe". Brass is reserved for the round breech
HUB (the dominant warm mass / rotary core) so the eye finds the engine where it
expects it; the crank stays cool gunmetal with only a small brass tip.

Drawn on a 44px work surface then smoothscaled to 22 so the seams and rim caps
antialias cleanly. A baked dark outline is laid first (inflated) so the gun reads
on bright DAY sky; a warm keyline rides the metal top edges AND a thin skim runs
the bottom rod's lower edge so the bundle's full height still holds on dark NIGHT
sky from one mode-agnostic sprite. Every mass sits ~4px off the edges so the
in-game rotozoom never clips a barrel or the crank.
"""
import pygame

# Tight gatling palette. Gunmetal for the cool barrel bundle AND the crank arm;
# brass reserved for the round breech HUB (the rotary engine) with only a small
# brass tip on the crank; steel-hi rims the barrel tops; warm keyline is NIGHT.
GUNMETAL = ( 74,  82,  96)      # cool barrel rods + crank arm
GUNMETAL_HI = (110, 122, 140)   # mid lift on the rods
STEEL_HI = (174, 184, 200)      # bright rim along the barrel tops + muzzle caps
BRASS = (201, 150,  46)         # round breech hub (dominant warm mass)
BRASS_HI = (240, 199,  90)      # warm hub highlight + crank tip spark
OUTLINE = ( 28,  30,  38)       # dark, high-value: reads on bright day sky
KEYLINE = (210, 200, 170)       # warm rim — the NIGHT lifeline
MUZZLE = (255, 226, 150)        # warm bore sparks at the barrel mouths


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static gatling sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx, cy = S // 2, S // 2

    # --- silhouette geometry -------------------------------------------------
    # Barrel bundle projects LEFT (forward) from a fat round brass breech hub; a
    # crank THROW hangs off the hub's RIGHT rear. The bundle is 3 fat parallel
    # rods stacked with WIDE dark sky-gap seams — the seams are the multi-barrel
    # cue and must survive the downscale, so the rods are kept thin (3px) and
    # pulled to cy±7 to open ~4px of dark between them. The hub is the dominant
    # warm mass; the crank is a cool steel elbow so it reads as a handle.
    hub_c = (cx + 6, cy)                # round brass breech hub — the engine
    hub_r = 7                           # dominant warm mass
    barrel_x0, barrel_x1 = 5, cx + 4    # long bundle, spans most of the surface
    rod_h = 3                           # thin rods so the seams stay open
    rod_ys = (cy - 7, cy, cy + 7)       # 3 stacked rods, wide dark seams between
    # Crank throw: short arm drops off the hub's lower rear, then a short
    # PERPENDICULAR grip bar at its end. The elbow is the "hand-cranked" tell.
    arm_top = (hub_c[0] + hub_r - 2, cy + 1)
    arm_bot = (hub_c[0] + hub_r - 1, cy + 8)        # short arm down off the hub
    grip_a = (arm_bot[0] - 4, arm_bot[1] + 1)       # perpendicular grip bar
    grip_b = (arm_bot[0] + 4, arm_bot[1] + 1)

    def rod_rect(y):
        return pygame.Rect(barrel_x0, y - rod_h // 2, barrel_x1 - barrel_x0, rod_h)

    # --- baked outline pass (drawn first, inflated) --------------------------
    # One dark silhouette under every mass so the whole gun reads on day sky.
    pygame.draw.circle(surf, OUTLINE, hub_c, hub_r + 3)
    pygame.draw.line(surf, OUTLINE, arm_top, arm_bot, 6)
    pygame.draw.line(surf, OUTLINE, grip_a, grip_b, 6)
    for y in rod_ys:
        pygame.draw.rect(surf, OUTLINE, rod_rect(y).inflate(4, 4), border_radius=2)

    # --- tiny yoke bridging hub to the bundle --------------------------------
    # A short gunmetal bridge between the hub face and the rear of the bundle so
    # the rods read as bolted to the spinning hub, not floating in front of it.
    yoke = pygame.Rect(hub_c[0] - hub_r - 1, cy - 8, 4, 16)
    pygame.draw.rect(surf, GUNMETAL, yoke, border_radius=1)
    pygame.draw.line(surf, STEEL_HI, yoke.topleft, yoke.topright, 1)

    # --- the barrel BUNDLE ----------------------------------------------------
    # 3 fat gunmetal rods with WIDE dark sky-gap seams between them — the gaps are
    # the cue that there is more than one barrel, so they are left as the bare
    # outline showing through. A bright steel top rim runs each rod (also a NIGHT
    # cue), and a 2px steel cap + warm bore spark pins each muzzle as a firing
    # mouth — the cluster of bright mouths is the gatling tell at true size.
    for y in rod_ys:
        r = rod_rect(y)
        pygame.draw.rect(surf, GUNMETAL, r, border_radius=1)
        pygame.draw.line(surf, GUNMETAL_HI, (r.x + 1, r.centery),
                         (r.right - 2, r.centery), 1)
        pygame.draw.line(surf, STEEL_HI, (r.x + 2, r.y), (r.right - 1, r.y), 1)
        pygame.draw.rect(surf, STEEL_HI, pygame.Rect(r.x, r.top, 2, rod_h))
        pygame.draw.circle(surf, MUZZLE, (r.x + 1, r.centery), 1)

    # --- the round BRASS breech hub (the rotary engine) ----------------------
    # Drawn AFTER the rods so it caps their rear and reads as the spinning body
    # the bundle turns around. Brass keeps it the warm DOMINANT mass against the
    # cool barrels; a small bolt ring sells the rotary face without micro-noise.
    pygame.draw.circle(surf, BRASS, hub_c, hub_r)
    pygame.draw.circle(surf, BRASS_HI, (hub_c[0] - 2, hub_c[1] - 2), hub_r - 3)
    pygame.draw.circle(surf, OUTLINE, hub_c, 2)            # central axle
    for dx, dy in ((-4, 0), (4, 0), (0, -4), (0, 4)):
        pygame.draw.circle(surf, GUNMETAL, (hub_c[0] + dx, hub_c[1] + dy), 1)

    # --- hand CRANK throw (rear, steel elbow) --------------------------------
    # A short steel arm down off the hub rear plus a short PERPENDICULAR grip bar
    # — the L-elbow silhouette reads "hand-cranked" where a round knob read like
    # a magnifying lens. Steel keeps the warm mass in the hub, not the handle; a
    # small brass tip pins the grip end as the thing a hand turns.
    pygame.draw.line(surf, GUNMETAL, arm_top, arm_bot, 3)
    pygame.draw.line(surf, GUNMETAL, grip_a, grip_b, 3)
    pygame.draw.line(surf, GUNMETAL_HI, arm_top, (arm_bot[0] - 1, arm_bot[1]), 1)
    pygame.draw.circle(surf, BRASS, grip_b, 2)            # brass grip tip
    pygame.draw.circle(surf, BRASS_HI, (grip_b[0] - 1, grip_b[1] - 1), 1)

    # --- warm night keyline along top + bottom runs --------------------------
    # Rides the upper edge of the bundle + hub so the metal separates from a dark
    # sky; a thin skim on the BOTTOM rod's lower edge holds the bundle's full
    # height so it never collapses to a half-bar on night.
    top_rod = rod_rect(rod_ys[0])
    bot_rod = rod_rect(rod_ys[-1])
    pygame.draw.line(surf, KEYLINE, (top_rod.x, top_rod.y - 1),
                     (hub_c[0], hub_c[1] - hub_r), 1)
    pygame.draw.line(surf, KEYLINE, (bot_rod.x, bot_rod.bottom),
                     (bot_rod.right - 2, bot_rod.bottom), 1)
    pygame.draw.circle(surf, KEYLINE, (hub_c[0] + 1, hub_c[1] - hub_r + 1), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
