"""NERF BLASTER — bright foam-dart toy parcel cosmetic.

A chunky kid-safe dart blaster carried below Pip, rotating with his bank. The
identity is the BRIGHT-ORANGE shell plus a rotating dart drum showing yellow
foam-dart TIP circles at the front and a wide muzzle — orange + foam tips read
unmistakably as a toy, never a real gun. A blue grip + a small blue trigger
nub asymmetrize the held end so the front/back is never ambiguous.

22px read tradeoffs: at the 44->22 downscale fine detail dissolves, so the read
is carried by three bold masses with clear hue separation — the orange shell
body, the round drum holding 3 chunky yellow dart tips (kept as fat dots, not
rings, so they survive the scale), and the wide grey muzzle ring that pins the
"this end fires" cue. The drum and muzzle are pushed to the front so the toy
profile stays asymmetric across the whole tilt arc.

Drawn on a 44px work surface then smoothscaled to 22 so the rims and tip dots
antialias cleanly. A baked dark outline is laid first (inflated) so the bright
shell reads on DAY sky; a warm keyline rides the orange top edge so the shell
still separates on dark NIGHT sky from the same single sprite.
"""
import pygame

# Tight toy palette. Orange is the whole shell so the toy read dominates; blue
# is reserved for the grip/trigger held-end accent, yellow for the foam tips.
ORANGE = (240, 122, 30)      # main shell — the identity mass
ORANGE_HI = (255, 168, 92)   # warm top lift on the shell
ORANGE_LO = (196,  90, 18)   # underside shade so the shell reads as a volume
BLUE = (46, 111, 200)        # grip + trigger accent
BLUE_HI = (110, 162, 230)    # blue highlight
YELLOW = (242, 210, 58)      # foam-dart tips
YELLOW_HI = (255, 238, 150)  # dart-tip highlight
GREY = (138, 147, 162)       # muzzle ring + drum hub
GREY_HI = (196, 204, 216)    # muzzle rim light (NIGHT lifeline on the front)
OUTLINE = (40, 34, 26)       # dark, high-value: reads on bright day sky
KEYLINE = (255, 206, 150)    # warm rim — the NIGHT lifeline on the shell


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static blaster sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx, cy = S // 2, S // 2

    # --- silhouette geometry -------------------------------------------------
    # A compact toy run: a stubby orange shell body with a fat round dart DRUM
    # slung under the front, a wide grey muzzle projecting forward, and a blue
    # grip dropping from the back. Front is LEFT. Everything kept ~4px off every
    # edge so the in-game rotozoom never clips the muzzle or grip at hard bank.
    body = pygame.Rect(14, cy - 6, 17, 10)         # orange shell, centre-right
    muzzle_c = (10, cy - 1)                         # wide muzzle, projects left
    muzzle_r = 6
    drum_c = (17, cy + 6)                           # round dart drum, slung down
    drum_r = 7
    grip = [(27, cy + 3), (33, cy + 3), (32, cy + 12), (27, cy + 12)]  # blue grip

    # --- baked outline pass (drawn first, inflated) --------------------------
    # One dark silhouette under every mass so the whole blaster reads on day sky.
    pygame.draw.circle(surf, OUTLINE, drum_c, drum_r + 3)
    pygame.draw.circle(surf, OUTLINE, muzzle_c, muzzle_r + 3)
    pygame.draw.polygon(surf, OUTLINE,
                        [(25, cy + 3), (35, cy + 3), (34, cy + 13), (25, cy + 13)])
    pygame.draw.rect(surf, OUTLINE, body.inflate(5, 5), border_radius=4)

    # --- wide muzzle ring (front) --------------------------------------------
    # A fat orange ring around a yellow foam-tip core — the "this end fires" cue,
    # kept wide and blunt so it reads as a toy muzzle, never a thin gun barrel.
    # A loaded yellow dart sits IN the muzzle so the toy read survives up front.
    pygame.draw.circle(surf, ORANGE, muzzle_c, muzzle_r)
    pygame.draw.circle(surf, ORANGE_HI, muzzle_c, muzzle_r, 1)
    pygame.draw.circle(surf, YELLOW, muzzle_c, muzzle_r - 3)
    pygame.draw.circle(surf, YELLOW_HI, (muzzle_c[0] - 1, muzzle_c[1] - 1), 1)

    # --- the DART DRUM (slung under the front) -------------------------------
    # Orange-ringed drum packed with chunky YELLOW foam-dart tips — fat dots, not
    # rings, so the tips survive the downscale. The cluster of yellow against the
    # orange ring is the toy identity, the strongest cue at true size.
    pygame.draw.circle(surf, ORANGE, drum_c, drum_r)
    pygame.draw.circle(surf, ORANGE_HI, drum_c, drum_r, 1)
    pygame.draw.circle(surf, GREY, drum_c, drum_r - 2)   # grey face the tips sit on
    for dx, dy in ((0, -3), (3, 2), (-3, 2), (0, 0)):    # packed foam-dart tips
        tx, ty = drum_c[0] + dx, drum_c[1] + dy
        pygame.draw.circle(surf, YELLOW, (tx, ty), 2)
        pygame.draw.circle(surf, YELLOW_HI, (tx - 1, ty - 1), 1)

    # --- blue grip (held end, back) ------------------------------------------
    pygame.draw.polygon(surf, BLUE, grip)
    pygame.draw.line(surf, BLUE_HI, grip[0], grip[3], 1)

    # --- orange shell body ---------------------------------------------------
    pygame.draw.rect(surf, ORANGE, body, border_radius=4)
    pygame.draw.rect(surf, ORANGE_LO, (body.x + 2, body.bottom - 3, body.w - 4, 3),
                     border_radius=2)                # underside shade
    pygame.draw.line(surf, ORANGE_HI, (body.x + 3, body.y + 2),
                     (body.right - 3, body.y + 2), 2)  # top lift

    # --- blue trigger nub (under the shell, behind the drum) -----------------
    # A small blue trigger pinned at the grip junction so the held end reads.
    pygame.draw.rect(surf, BLUE, (25, cy + 4, 3, 4), border_radius=1)
    pygame.draw.rect(surf, BLUE_HI, (25, cy + 4, 3, 1))

    # --- warm night keyline along the shell top run --------------------------
    # Rides just inside the outline on the orange upper edge so the shell still
    # separates from a dark sky from the same single sprite.
    pygame.draw.line(surf, KEYLINE, (body.x + 1, body.y),
                     (body.right - 2, body.y), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
