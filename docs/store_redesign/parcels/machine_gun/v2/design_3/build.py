"""LASER MINIGUN — sci-fi energy-weapon parcel cosmetic.

A sleek dark futuristic gun carried below Pip, rotating with his bank. The read
is an emissive one: a dark blued body with a glowing neon-cyan energy coil
running the length of the barrel and a bright glowing muzzle core at the front.
The cyan glow IS the identity — it must out-read the body, so it is baked as a
solid bright-cyan core wrapped in a soft lighter-cyan bloom edge (the static
sprite can't animate light, so the bloom fakes the emission). That bloom is the
NIGHT lifeline: on dark sky the dark body sinks and only the glowing coil/muzzle
carry the silhouette, so they are pushed to the brightest values on the sprite.

22px read tradeoffs: at the 44->22 downscale fine machinery dissolves, so the
read is built from two bold masses — a long dark barrel block and a stubby
body/power-cell behind it — with the glow concentrated into ONE continuous coil
line plus a fat muzzle dot rather than scattered detail that would smear. The
barrel is stretched well past the body so the long horizontal run reads "gun"
not "pistol", capped by only the muzzle bloom so the tip never bulbs into a
cannon mouth. A dark high-value outline is laid first (inflated) so the solid
gun shape still reads on bright DAY sky where the cyan glow alone would wash out,
and a cool keyline rides the body top so the dark mass separates from night sky.
Everything sits ~4px off the surface edges so the in-game rotozoom never clips
the muzzle or cell at hard bank, and the coil runs the full barrel so the glow
stays legible across the whole tilt arc.

Drawn on a 44px work surface then smoothscaled to 22 so the glow bloom and rim
antialias into a soft emissive edge instead of a hard ring.
"""
import pygame

# Sci-fi energy palette. The body stays cool-dark so the cyan reads as light
# emitted against it; the glow climbs from neon core to a pale bloom edge.
DARK = ( 35,  42,  58)       # sleek blued body / barrel
DARK_HI = ( 90, 106, 134)    # body top rim — separates dark mass on night sky
NEON = ( 56, 230, 240)       # neon-cyan energy coil + muzzle core
GLOW = (156, 251, 255)       # pale cyan bloom edge — fakes the emission
CELL = ( 70, 200, 214)       # power-cell window, slightly deeper than the bloom
OUTLINE = ( 16,  19,  28)    # dark, high-value: reads on bright day sky
KEYLINE = (120, 150, 180)    # cool rim — the dark-body night lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static energy-gun sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx, cy = S // 2, S // 2

    # --- silhouette geometry -------------------------------------------------
    # A long horizontal run: a stubby body/power-cell on the right, a long dark
    # barrel projecting left. ~2.7x its height so it reads "gun" not "pistol".
    body = pygame.Rect(22, cy - 6, 13, 12)         # chunky energy body, right
    barrel = pygame.Rect(7, cy - 4, 17, 8)         # long barrel, projects left
    cell_c = (34, cy + 7)                          # round power cell, slung under
    cell_r = 5

    # --- baked outline pass (drawn first, inflated) --------------------------
    # Dark silhouette under every mass so the solid gun shape reads on day sky.
    pygame.draw.circle(surf, OUTLINE, cell_c, cell_r + 3)
    pygame.draw.rect(surf, OUTLINE, body.inflate(4, 4), border_radius=4)
    pygame.draw.rect(surf, OUTLINE, barrel.inflate(4, 4), border_radius=3)

    # --- power cell (slung under the body, tucked up so it reads attached) ---
    pygame.draw.circle(surf, DARK, cell_c, cell_r)
    pygame.draw.circle(surf, CELL, (cell_c[0], cell_c[1] + 1), cell_r - 2)
    pygame.draw.circle(surf, GLOW, (cell_c[0] - 1, cell_c[1]), 1)   # charge spark

    # --- dark body + barrel masses -------------------------------------------
    pygame.draw.rect(surf, DARK, body, border_radius=4)
    pygame.draw.rect(surf, DARK, barrel, border_radius=3)
    # Cool top rim along the whole run so the dark body holds its edge on night.
    pygame.draw.line(surf, DARK_HI, (barrel.x + 1, barrel.y + 1),
                     (body.right - 2, body.y + 1), 2)
    pygame.draw.line(surf, KEYLINE, (barrel.x, barrel.y),
                     (body.right - 1, body.y), 1)

    # --- the EMISSIVE energy coil (the identity) -----------------------------
    # One continuous glow line down the barrel centre: a pale bloom band laid
    # under a brighter neon core, so the smoothscale softens it into emission.
    coil_y = cy + 1
    pygame.draw.line(surf, GLOW, (barrel.x + 2, coil_y),
                     (body.x + 5, coil_y), 4)            # soft bloom band
    pygame.draw.line(surf, NEON, (barrel.x + 2, coil_y),
                     (body.x + 5, coil_y), 2)            # bright neon core
    # A few coil ribs so it reads as a wound energy coil, not just a stripe.
    for rx in (barrel.x + 4, barrel.x + 8, barrel.x + 12):
        pygame.draw.line(surf, GLOW, (rx, coil_y - 3), (rx, coil_y + 3), 1)

    # --- glowing muzzle core (front, the "this end fires" pin) ---------------
    # The brightest mass on the sprite: a pale bloom halo around a neon core so
    # it blooms on night sky and still pins the muzzle on day. Pushed a touch
    # bigger than the body detail so the emission survives the downscale.
    mx = barrel.x + 1
    pygame.draw.circle(surf, GLOW, (mx, cy), 5)
    pygame.draw.circle(surf, NEON, (mx, cy), 3)
    pygame.draw.circle(surf, (240, 255, 255), (mx, cy), 1)   # white-hot centre

    return pygame.transform.smoothscale(surf, (22, 22))
