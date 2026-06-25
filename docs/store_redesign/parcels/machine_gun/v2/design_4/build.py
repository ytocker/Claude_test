"""MACHINE GUN — GOLD DELUXE parcel cosmetic.

A gold-plated showpiece submachine gun carried below Pip, rotating with his
bank. The read is a COMPACT all-gold SMG: a stubby receiver body, a short
horizontal barrel projecting forward, a curved magazine slung down, and an
ivory grip — the gold + the value contrast on the metal are what sell "premium
flex" rather than plain firearm. A cyan GEM inlay on the receiver side and a
4-point sparkle pin the bling read.

22px read tradeoffs: at the 44->22 downscale fine engraving dissolves, so the
gold is carried by big masses with hard VALUE separation — a bright gold-hi
band sitting on top of gold-shade on the receiver + the full barrel — because
"polished gold" only reads as metal (not a flat yellow blob) when the highlight
is much brighter than the body and survives into grayscale. The gun is kept
compact (barrel only just clears the body) so the masses stay chunky and legible
at true size; a longer thin barrel would dissolve before the bling does. The
gem is placed centre-side on the receiver, the widest flat, so it stays visible
across the whole tilt arc rather than rotating behind the body.

Drawn on a 44px work surface then smoothscaled to 22 so the highlights, gem and
keyline antialias cleanly. A baked dark gold-brown outline is laid first
(inflated) so the gun reads on bright DAY sky; a warm ivory keyline rides the
metal top edges so the gold still separates on dark NIGHT sky — one static
sprite for every Pip skin.
"""
import pygame

# All-gold palette with a wide value spread so the metal reads as polished gold
# and not a flat yellow shape — gold_hi is near-white-warm, gold_shade is a deep
# bronze. The gem + ivory are the only non-gold accents.
GOLD = (227, 178,  60)       # base gold plate
GOLD_HI = (248, 224, 138)    # bright top highlight band — the "polish" cue
GOLD_SHADE = (156, 110,  30) # deep bronze underside / core shadow
GEM_CYAN = ( 92, 208, 224)   # cyan gem inlay
GEM_HI = (200, 245, 250)     # gem facet glint
IVORY = (239, 230, 204)      # grip
IVORY_SH = (196, 184, 150)   # grip shade
OUTLINE = ( 58,  42,  14)    # dark gold-brown: reads on bright day sky
KEYLINE = (244, 232, 196)    # warm ivory rim — the NIGHT lifeline
SPARKLE = (255, 252, 235)    # bling sparkle


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static gold-SMG sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx, cy = S // 2, S // 2

    # --- silhouette geometry -------------------------------------------------
    # A COMPACT gold SMG: a chunky receiver, a short barrel projecting LEFT just
    # past the body, a curved mag slung DOWN under the front, an ivory grip under
    # the rear. Everything kept ~4px off every edge for the in-game rotozoom.
    body = pygame.Rect(18, cy - 5, 16, 10)         # gold receiver, right-of-centre
    barrel = pygame.Rect(5, cy - 3, 15, 5)         # gold barrel, projects clearly left
    grip = [(27, cy + 4), (32, cy + 4), (31, cy + 11), (26, cy + 11)]  # ivory grip
    mag = [(19, cy + 4), (24, cy + 4), (26, cy + 12), (21, cy + 12)]   # curved mag
    gem_c = (body.centerx, cy)                     # cyan gem on the receiver's widest flat

    # --- baked outline pass (drawn first, inflated) --------------------------
    pygame.draw.polygon(surf, OUTLINE,
                        [(25, cy + 3), (33, cy + 3), (32, cy + 13), (24, cy + 13)])
    pygame.draw.polygon(surf, OUTLINE,
                        [(17, cy + 3), (25, cy + 3), (27, cy + 13), (19, cy + 13)])
    pygame.draw.rect(surf, OUTLINE, body.inflate(4, 4), border_radius=3)
    pygame.draw.rect(surf, OUTLINE, barrel.inflate(4, 4), border_radius=2)

    # --- ivory grip ----------------------------------------------------------
    pygame.draw.polygon(surf, IVORY, grip)
    pygame.draw.polygon(surf, IVORY_SH, [(29, cy + 5), (32, cy + 4), (31, cy + 11),
                                         (29, cy + 11)])
    pygame.draw.line(surf, KEYLINE, grip[0], grip[1], 1)

    # --- curved magazine (gold, slung down under the front) ------------------
    pygame.draw.polygon(surf, GOLD, mag)
    pygame.draw.polygon(surf, GOLD_SHADE, [(23, cy + 5), (26, cy + 5), (26, cy + 12),
                                           (24, cy + 12)])
    pygame.draw.line(surf, GOLD_HI, (19, cy + 5), (21, cy + 11), 1)

    # --- gold barrel ---------------------------------------------------------
    # Shaded core under a bright top band so the short prong reads as polished
    # metal — the value gap is what survives the downscale + grayscale.
    pygame.draw.rect(surf, GOLD_SHADE, barrel, border_radius=2)
    pygame.draw.rect(surf, GOLD, barrel.inflate(0, -2), border_radius=2)
    pygame.draw.line(surf, GOLD_HI, (barrel.x + 1, barrel.y + 1),
                     (barrel.right - 1, barrel.y + 1), 1)
    # tiny muzzle ring pins the "this end fires" read
    pygame.draw.circle(surf, GOLD_HI, (barrel.x + 1, cy), 2)
    pygame.draw.circle(surf, OUTLINE, (barrel.x + 1, cy), 2, 1)

    # --- gold receiver body --------------------------------------------------
    # Three stacked value bands (shade core, gold field, bright top band) so the
    # widest mass carries the strongest "polished gold" contrast.
    pygame.draw.rect(surf, GOLD_SHADE, body, border_radius=3)
    pygame.draw.rect(surf, GOLD, pygame.Rect(body.x, body.y + 2, body.w, body.h - 3),
                     border_radius=3)
    pygame.draw.rect(surf, GOLD_HI, pygame.Rect(body.x + 1, body.y + 1, body.w - 2, 2),
                     border_radius=1)

    # --- cyan gem inlay ------------------------------------------------------
    # A diamond on the receiver's widest flat — set off by a thin gold bezel so
    # the cool accent pops against the warm plate, and a white facet glint sells
    # the gem. Centre-placed so it stays read across the tilt arc.
    gem = [(gem_c[0], gem_c[1] - 3), (gem_c[0] + 3, gem_c[1]),
           (gem_c[0], gem_c[1] + 3), (gem_c[0] - 3, gem_c[1])]
    pygame.draw.polygon(surf, GOLD_HI, [(gem_c[0], gem_c[1] - 4), (gem_c[0] + 4, gem_c[1]),
                                        (gem_c[0], gem_c[1] + 4), (gem_c[0] - 4, gem_c[1])])
    pygame.draw.polygon(surf, GEM_CYAN, gem)
    pygame.draw.line(surf, GEM_HI, (gem_c[0] - 1, gem_c[1] - 1), (gem_c[0] + 1, gem_c[1] - 2), 1)

    # --- warm night keyline along the metal top run --------------------------
    pygame.draw.line(surf, KEYLINE, (barrel.x, barrel.y),
                     (body.right - 1, body.y), 1)

    # --- bling sparkle -------------------------------------------------------
    # A 4-point star off the receiver's bright corner — the unmistakable "luxury"
    # tell that the gem + gold can't fully carry at 22px.
    sx, sy = body.right - 3, body.y - 1
    pygame.draw.line(surf, SPARKLE, (sx - 2, sy), (sx + 2, sy), 1)
    pygame.draw.line(surf, SPARKLE, (sx, sy - 2), (sx, sy + 2), 1)
    pygame.draw.circle(surf, SPARKLE, (sx, sy), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
