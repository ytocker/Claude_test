"""GATLING GUN — hand-cranked rotary brass parcel cosmetic.

A rotary gatling carried below Pip, rotating with his bank. The identity beat is
a horizontal CLUSTER of parallel barrels projecting forward from a round brass
breech hub, with a hand-crank at the back — a bundle of barrels reads "rotary /
gatling" the way no single-barrel gun can, so the bundle is the load-bearing
mass and gets the most contrast.

22px read tradeoffs: at the 44->22 downscale the individual barrels would smear
into one bar, so they are drawn as a small odd count (3) of fat parallel rods
with dark sky-gap seams BETWEEN them and bright steel rim caps at the muzzle —
the gaps, not the rods, are what survive the downscale and sell "more than one
barrel". The round brass breech hub anchors the back of the bundle as the
spinning core, and a stubby crank handle hangs off the rear so the silhouette is
asymmetric (bundle forward / crank back) and never reads as a plain pipe cluster.
Brass is reserved for the hub + crank so the warm mass stays the "engine" cue
while the barrels stay cool gunmetal. The bundle is kept short and centred so it
still reads as a barrel cluster across the full tilt arc rather than only level.

Drawn on a 44px work surface then smoothscaled to 22 so the seams and rim caps
antialias cleanly. A baked dark outline is laid first (inflated) so the gun reads
on bright DAY sky; a warm keyline rides the metal top edges so the gunmetal +
brass still separate on dark NIGHT sky from one mode-agnostic sprite. Every mass
sits ~4px off the edges so the in-game rotozoom never clips a barrel or the crank.
"""
import pygame

# Tight gatling palette from the concept. Gunmetal for the cool barrel bundle,
# brass reserved for the breech hub + crank so the warm mass reads as the rotary
# "engine"; steel-hi rims the barrel tops; warm keyline is the NIGHT lifeline.
GUNMETAL = ( 74,  82,  96)      # cool barrel rods
GUNMETAL_HI = (110, 122, 140)   # mid lift on the rods
STEEL_HI = (174, 184, 200)      # bright rim along the barrel tops + muzzle caps
BRASS = (201, 150,  46)         # round breech hub + crank
BRASS_HI = (240, 199,  90)      # warm hub/crank highlight
OUTLINE = ( 28,  30,  38)       # dark, high-value: reads on bright day sky
KEYLINE = (210, 200, 170)       # warm rim — the NIGHT lifeline
MUZZLE = (255, 214, 120)        # tiny warm bore sparks at the barrel mouths


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static gatling sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx, cy = S // 2, S // 2

    # --- silhouette geometry -------------------------------------------------
    # Barrel bundle projects LEFT (forward) from a round brass breech hub; a
    # stubby crank hangs off the RIGHT (back). The bundle is 3 fat parallel rods
    # stacked vertically with wide dark sky-gap seams — the bundle is the
    # DOMINANT horizontal mass so the multi-barrel cluster leads the read, and
    # the hub is trimmed so it caps the bundle's rear without competing with it.
    hub_c = (cx + 7, cy)                # brass breech hub, back, trimmed small
    hub_r = 6
    barrel_x0, barrel_x1 = 5, cx + 5    # long bundle, spans most of the surface
    rod_h = 4                           # each rod's thickness
    rod_ys = (cy - 6, cy, cy + 6)       # 3 stacked rods with wide seams between
    frame_top = pygame.Rect(barrel_x1 - 5, cy - 10, 6, 4)  # short frame spar
    crank_pivot = (hub_c[0] + hub_r - 1, cy + 1)
    crank_knob = (crank_pivot[0] + 5, cy + 8)

    def rod_rect(y):
        return pygame.Rect(barrel_x0, y - rod_h // 2, barrel_x1 - barrel_x0, rod_h)

    # --- baked outline pass (drawn first, inflated) --------------------------
    # One dark silhouette under every mass so the whole gun reads on day sky.
    pygame.draw.circle(surf, OUTLINE, hub_c, hub_r + 3)
    pygame.draw.line(surf, OUTLINE, crank_pivot, crank_knob, 6)
    pygame.draw.circle(surf, OUTLINE, crank_knob, 4)
    pygame.draw.rect(surf, OUTLINE, frame_top.inflate(4, 4), border_radius=2)
    for y in rod_ys:
        pygame.draw.rect(surf, OUTLINE, rod_rect(y).inflate(4, 4), border_radius=2)

    # --- short frame spar (drawn under the bundle) ---------------------------
    pygame.draw.rect(surf, GUNMETAL, frame_top, border_radius=1)
    pygame.draw.line(surf, STEEL_HI, frame_top.topleft, frame_top.topright, 1)

    # --- the barrel BUNDLE ----------------------------------------------------
    # 3 fat gunmetal rods with dark sky-gap seams between them — the gaps are the
    # cue that there is more than one barrel, so they are left as the bare outline
    # showing through. A bright steel top rim runs each rod (also the NIGHT cue),
    # and a steel cap + warm bore spark pins each muzzle as a firing mouth.
    for y in rod_ys:
        r = rod_rect(y)
        pygame.draw.rect(surf, GUNMETAL, r, border_radius=2)
        pygame.draw.line(surf, GUNMETAL_HI, (r.x + 1, r.centery),
                         (r.right - 2, r.centery), 1)
        pygame.draw.line(surf, STEEL_HI, (r.x + 2, r.y), (r.right - 1, r.y), 1)
        # Steel muzzle cap block + warm bore spark so each forward end reads as a
        # firing mouth, not a cut pipe — the cluster of mouths is the gatling cue.
        pygame.draw.rect(surf, STEEL_HI, pygame.Rect(r.x, r.top, 2, rod_h))
        pygame.draw.circle(surf, MUZZLE, (r.x + 1, r.centery), 1)

    # --- the round BRASS breech hub (the rotary core) ------------------------
    # Drawn AFTER the rods so it caps their rear and reads as the spinning body
    # the bundle turns around. Brass keeps it warm against the cool barrels; a
    # small bolt ring of dots sells the rotary face without micro-detail noise.
    pygame.draw.circle(surf, BRASS, hub_c, hub_r)
    pygame.draw.circle(surf, BRASS_HI, (hub_c[0] - 2, hub_c[1] - 2), hub_r - 3)
    pygame.draw.circle(surf, OUTLINE, hub_c, 2)            # central axle
    for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
        pygame.draw.circle(surf, GUNMETAL, (hub_c[0] + dx, hub_c[1] + dy), 1)

    # --- hand CRANK (rear, hangs down) ---------------------------------------
    # Brass arm + knob off the hub's back so the silhouette is asymmetric and
    # reads "hand-cranked", separating it from a plain pipe cluster.
    pygame.draw.line(surf, BRASS, crank_pivot, crank_knob, 3)
    pygame.draw.circle(surf, BRASS, crank_knob, 3)
    pygame.draw.circle(surf, BRASS_HI, (crank_knob[0] - 1, crank_knob[1] - 1), 1)

    # --- warm night keyline along the top run --------------------------------
    # Rides the upper edge of the bundle + hub so the metal still separates from
    # a dark sky from the same single sprite.
    top_rod = rod_rect(rod_ys[0])
    pygame.draw.line(surf, KEYLINE, (top_rod.x, top_rod.y - 1),
                     (hub_c[0], hub_c[1] - hub_r), 1)
    pygame.draw.circle(surf, KEYLINE, (hub_c[0] + 1, hub_c[1] - hub_r + 1), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
