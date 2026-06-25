"""MACHINE GUN — cartoon tommy-gun parcel cosmetic.

A chunky toy-proportioned gangster tommy gun carried below Pip, rotating with
his bank. The read is built from a LONG horizontal run (barrel + receiver, ~2.7×
its height) with a round GUNMETAL drum magazine slung UP under the front third,
a short angled pistol grip, and a stubby wood stock. The long thin barrel is the
load-bearing cue: a short fat one reads as a pistol/cannon, so the barrel is
stretched to project clearly past the body's front edge with a sky gap above and
below, capped by only a tiny muzzle so the tip never bulbs back into a cannon
mouth.

22px read tradeoffs: at the 44->22 downscale fine receiver detail dissolves, so
the read is carried by big masses with clear VALUE separation — dark gunmetal
body+barrel, the bright metal rim light running the FULL barrel length (the cue
that the long prong is a barrel, and the NIGHT lifeline), the slung metal drum
with a vertical seam so it reads as a cylinder not a wheel, and the warm wood
grip/stock that make the held end asymmetric. The drum is raised so its top third
tucks UP behind the receiver — slung up it reads as a magazine; hung fully clear
it reads as a wheel. Everything sits off the surface edges so the in-game
rotozoom never clips the muzzle or stock at hard bank.

Drawn on a 44px work surface then smoothscaled to 22 so the rim light and keyline
antialias cleanly. A baked dark outline is laid first (inflated) so the gun reads
on bright DAY sky; warm keylines ride the metal top edges so the gunmetal still
reads on dark NIGHT sky without a per-mode sprite.
"""
import pygame

# Tight gun palette. Gunmetal stays cool-blued and now carries the drum too; the
# wood is reserved for the grip + a thin stock pad so the warm accent stays the
# "held end" cue rather than reading as a wooden carriage.
GUNMETAL = ( 74,  82,  96)      # blued body / barrel / drum
GUNMETAL_HI = (110, 122, 140)   # mid lift on the drum face
METAL_HI = (170, 184, 200)      # bright rim light along the metal top + seam
WOOD = (138,  86,  44)          # grip + thin stock pad cartoon wood-brown
WOOD_HI = (186, 126,  74)       # warm wood highlight
OUTLINE = ( 28,  30,  38)       # dark, high-value: reads on bright day sky
KEYLINE = (210, 200, 170)       # warm rim — the NIGHT lifeline
MUZZLE = (255, 214, 120)        # tiny warm muzzle tip


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static tommy-gun sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx, cy = S // 2, S // 2

    # --- silhouette geometry -------------------------------------------------
    # A LONG horizontal run: receiver body + a long thin barrel projecting left
    # well past the body's front edge. The whole run is ~2.7× its height so the
    # silhouette reads "machine gun", not "pistol". Drum slung UP under the front
    # third. All masses kept ~4px off every edge for the rotozoom.
    body = pygame.Rect(17, cy - 4, 17, 8)          # gunmetal receiver, right-ish
    barrel = pygame.Rect(4, cy - 2, 16, 5)         # long thin barrel, projects left
    stock = pygame.Rect(33, cy - 3, 7, 7)          # short wood stock pad, right
    grip = [(24, cy + 4), (28, cy + 4), (26, cy + 9), (22, cy + 9)]  # angled grip
    drum_c = (cx - 3, cy + 4)                       # round drum mag, slung UP
    drum_r = 5

    # --- baked outline pass (drawn first, inflated) --------------------------
    # One dark silhouette under every mass so the whole gun reads on day sky.
    pygame.draw.circle(surf, OUTLINE, drum_c, drum_r + 3)
    pygame.draw.rect(surf, OUTLINE, stock.inflate(4, 4), border_radius=3)
    pygame.draw.polygon(surf, OUTLINE,
                        [(20, cy + 3), (30, cy + 3), (27, cy + 11), (21, cy + 11)])
    pygame.draw.rect(surf, OUTLINE, body.inflate(4, 4), border_radius=3)
    pygame.draw.rect(surf, OUTLINE, barrel.inflate(4, 4), border_radius=2)

    # --- the DRUM magazine (drawn under the receiver so it tucks up) ---------
    # GUNMETAL, slung up so its top third overlaps behind the receiver — only a
    # 1px shadow notch shows between, so it reads as a magazine and not a wheel.
    # A vertical seam + face lift make it a cylinder, not a sphere.
    pygame.draw.circle(surf, GUNMETAL, drum_c, drum_r)
    pygame.draw.circle(surf, GUNMETAL_HI, (drum_c[0] - 1, drum_c[1] - 1), drum_r - 2)
    pygame.draw.line(surf, METAL_HI, (drum_c[0] - 1, drum_c[1] - drum_r + 1),
                     (drum_c[0] - 1, drum_c[1] + drum_r - 1), 1)   # leading seam
    pygame.draw.circle(surf, GUNMETAL, drum_c, 2)                  # hub
    pygame.draw.circle(surf, METAL_HI, (drum_c[0] - 1, drum_c[1] - 1), 1)

    # --- wood masses (grip + stock pad) --------------------------------------
    pygame.draw.rect(surf, WOOD, stock, border_radius=3)
    pygame.draw.rect(surf, WOOD_HI, stock, width=1, border_radius=3)
    pygame.draw.polygon(surf, WOOD, grip)
    pygame.draw.line(surf, WOOD_HI, grip[0], grip[3], 1)

    # --- gunmetal body + barrel ----------------------------------------------
    pygame.draw.rect(surf, GUNMETAL, body, border_radius=3)
    pygame.draw.rect(surf, GUNMETAL, barrel, border_radius=2)
    # Bright rim light along the FULL metal top — runs the whole barrel so the
    # long prong reads as a barrel, and so the longer barrel survives on NIGHT
    # sky where it would otherwise sink into the receiver shadow.
    pygame.draw.line(surf, METAL_HI, (barrel.x + 1, barrel.y + 1),
                     (body.right - 2, barrel.y + 1), 2)

    # --- muzzle tip ----------------------------------------------------------
    # A tiny warm cap on the barrel mouth — a spark of colour that pins the
    # "this end fires" read. Kept to ~2px so the tip stays a prong, not a mouth.
    pygame.draw.circle(surf, MUZZLE, (barrel.x + 1, cy), 2)
    pygame.draw.circle(surf, OUTLINE, (barrel.x + 1, cy), 2, 1)

    # --- warm night keyline along the FULL top run --------------------------
    # Rides just inside the outline on the barrel + body upper edge so the
    # gunmetal still separates from a dark sky from the same single sprite.
    pygame.draw.line(surf, KEYLINE, (barrel.x, barrel.y),
                     (body.right - 1, body.y), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
