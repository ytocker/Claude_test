"""MACHINE GUN — cartoon tommy-gun parcel cosmetic.

A chunky toy-proportioned gangster tommy gun carried below Pip, rotating with
his bank. The IDENTITY is the round DRUM MAGAZINE slung under the middle of a
horizontal gunmetal body — the drum is what makes the silhouette read as "tommy
gun" rather than a generic stick of metal at 22px, so it is drawn bold and
slightly oversized. A stubby barrel points left, a wood foregrip + wood stock
bracket the body, and a warm muzzle tip caps the barrel.

22px read tradeoffs: at the 44->22 downscale fine receiver detail dissolves, so
the read is carried by three big masses with clear VALUE separation — dark
gunmetal body, the brown drum/grip wood, and the bright metal rim light along
the barrel top. The barrel is kept FAT (toy proportions) because a thin realistic
barrel vanishes when downscaled and clipped by the rotozoom. The drum is held
just below the body so a sliver of sky always separates it from the receiver and
it never fuses into one blob. Everything sits off the surface edges so the
in-game rotozoom never clips the muzzle or stock at hard bank.

Drawn on a 44px work surface then smoothscaled to 22 so the rim light and
keyline antialias cleanly. A baked dark outline is laid first (inflated) so the
gun reads on bright DAY sky; a warm keyline rides the metal top edge so the
gunmetal still reads on dark NIGHT sky without a per-mode sprite.
"""
import pygame

# Tight 5-hex gun palette. Gunmetal stays cool-blued; the wood is a saturated
# cartoon brown that holds a clear value gap from the metal so the grip + stock
# read as separate masses at true size.
GUNMETAL = ( 74,  82,  96)      # blued body / barrel base
METAL_HI = (170, 184, 200)      # bright rim light along the metal top
WOOD = (138,  86,  44)          # foregrip + stock + drum cartoon wood-brown
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
    # Horizontal receiver body, a touch above centre so the slung drum has room
    # below. Barrel points LEFT. All masses kept ~5px off every edge for the
    # rotozoom.
    body = pygame.Rect(11, cy - 5, 22, 9)          # main gunmetal receiver
    barrel = pygame.Rect(4, cy - 4, 13, 7)         # fat stubby barrel, left
    stock = pygame.Rect(31, cy - 4, 9, 8)          # wood stock, right
    grip = pygame.Rect(15, cy + 3, 5, 9)           # foregrip dropping down-left
    drum_c = (cx + 1, cy + 7)                       # round drum mag, slung under
    drum_r = 6

    def _outlined_rect(rect, color, rad, inf=4):
        pygame.draw.rect(surf, OUTLINE, rect.inflate(inf, inf),
                         border_radius=rad + 1)
        pygame.draw.rect(surf, color, rect, border_radius=rad)

    # --- baked outline pass (drawn first, inflated) --------------------------
    # One dark silhouette under every mass so the whole gun reads on day sky.
    pygame.draw.circle(surf, OUTLINE, drum_c, drum_r + 3)
    pygame.draw.rect(surf, OUTLINE, stock.inflate(4, 4), border_radius=3)
    pygame.draw.rect(surf, OUTLINE, grip.inflate(4, 4), border_radius=2)
    pygame.draw.rect(surf, OUTLINE, body.inflate(4, 4), border_radius=3)
    pygame.draw.rect(surf, OUTLINE, barrel.inflate(4, 4), border_radius=2)

    # --- wood masses (drawn under the metal so the receiver overlaps them) ----
    pygame.draw.rect(surf, WOOD, stock, border_radius=3)
    pygame.draw.rect(surf, WOOD_HI, stock, width=1, border_radius=3)
    pygame.draw.rect(surf, WOOD, grip, border_radius=2)
    pygame.draw.rect(surf, WOOD_HI, grip, width=1, border_radius=2)

    # --- gunmetal body + barrel ----------------------------------------------
    pygame.draw.rect(surf, GUNMETAL, body, border_radius=3)
    pygame.draw.rect(surf, GUNMETAL, barrel, border_radius=2)
    # Bright rim light along the metal TOP edge — the cue that says "polished
    # gun metal" and the NIGHT-readable highlight on the receiver + barrel.
    pygame.draw.line(surf, METAL_HI, (body.x + 1, body.y + 1),
                     (body.right - 2, body.y + 1), 2)
    pygame.draw.line(surf, METAL_HI, (barrel.x + 1, barrel.y + 1),
                     (barrel.right, barrel.y + 1), 2)

    # --- the DRUM magazine: the identity beat -------------------------------
    # Bold round wood drum with a metal hub + one ring, so it reads as a tommy
    # drum and not a wheel. Drawn LAST among the lower masses, sitting proud
    # below the receiver with a sky sliver between.
    pygame.draw.circle(surf, WOOD, drum_c, drum_r)
    pygame.draw.circle(surf, WOOD_HI, drum_c, drum_r, 1)
    pygame.draw.circle(surf, GUNMETAL, drum_c, 3)        # metal hub
    pygame.draw.circle(surf, METAL_HI, drum_c, 3, 1)     # hub ring catches light
    pygame.draw.circle(surf, METAL_HI, (drum_c[0], drum_c[1] - 1), 1)

    # --- muzzle tip ----------------------------------------------------------
    # A tiny warm cap on the barrel mouth — a spark of colour that pins the
    # "this end fires" read even when the metal goes flat at true size.
    pygame.draw.circle(surf, MUZZLE, (barrel.x + 1, cy), 3)
    pygame.draw.circle(surf, OUTLINE, (barrel.x + 1, cy), 3, 1)

    # --- warm night keyline along the receiver top --------------------------
    # Rides just inside the outline on the body's upper edge so the gunmetal
    # still separates from a dark sky from the same single sprite.
    pygame.draw.line(surf, KEYLINE, (body.x, body.y),
                     (body.right - 1, body.y), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
