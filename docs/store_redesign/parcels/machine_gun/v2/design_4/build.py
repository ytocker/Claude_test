"""MACHINE GUN — GOLD DELUXE parcel cosmetic.

A gold-plated showpiece submachine gun carried below Pip, rotating with his
bank. The read is a COMPACT all-gold SMG: a stubby receiver body, a short
horizontal barrel projecting forward, a curved magazine slung down, and an
ivory grip — the gold + the value contrast on the metal are what sell "premium
flex" rather than plain firearm. A cyan GEM inlay on the receiver side and a
4-point sparkle pin the bling read.

22px read tradeoffs: at the 44->22 downscale fine engraving dissolves, so the
gold is carried by big masses with hard VALUE separation — a bright gold-hi
band sitting on top of gold-shade on BOTH the receiver and the barrel — because
"polished gold" only reads as metal (not a flat yellow blob) when the highlight
is much brighter than the body and survives into grayscale. The barrel is long
and thin and clearly PROJECTS past the body so the gun long-axis reads as a gun
and not a gold L-bracket; the receiver is pushed right and the grip hangs only
below the REAR so the asymmetric SMG silhouette (barrel-forward / grip-back)
survives the tilt. Barrel and receiver share the same 3-band value structure so
the whole piece reads as one polished metal gun, not a bright body with a dull
prong. The gem is placed centre-side on the receiver, the widest flat, so it
stays visible across the whole tilt arc rather than rotating behind the body.

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
GEM_HI = (224, 250, 254)     # gem facet glint — kept tiny, just brighter to pop
GOLD_DEEP = (120,  84,  20)  # extra-deep barrel core: widens the barrel value spread
GOLD_FLASH = (255, 240, 170) # extra-bright barrel top line: widens the spread up top
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
    # A gold SMG with a clear long-axis: a chunky receiver pushed RIGHT, a long
    # thin barrel projecting LEFT well past the body (the gun read), a single
    # gold mag slung DOWN under the receiver, and an ivory grip hanging only
    # below the REAR. Barrel-forward + grip-back = the asymmetric SMG that the
    # tilt row needs. Everything kept ~4px off every edge for the rotozoom.
    body = pygame.Rect(23, cy - 5, 13, 10)         # gold receiver, hard right
    barrel = pygame.Rect(4, cy - 2, 19, 4)         # long thin barrel, projects far left
    grip = [(31, cy + 4), (36, cy + 4), (35, cy + 11), (30, cy + 11)]  # ivory grip, REAR
    mag = [(23, cy + 4), (28, cy + 4), (29, cy + 12), (24, cy + 12)]   # single gold mag
    gem_c = (body.centerx, cy)                     # cyan gem on the receiver's widest flat

    # --- baked outline pass (drawn first, inflated) --------------------------
    pygame.draw.polygon(surf, OUTLINE,
                        [(29, cy + 3), (37, cy + 3), (36, cy + 13), (28, cy + 13)])
    pygame.draw.polygon(surf, OUTLINE,
                        [(21, cy + 3), (29, cy + 3), (31, cy + 13), (23, cy + 13)])
    pygame.draw.rect(surf, OUTLINE, body.inflate(4, 4), border_radius=3)
    pygame.draw.rect(surf, OUTLINE, barrel.inflate(4, 4), border_radius=2)

    # --- ivory grip (rear only) ----------------------------------------------
    pygame.draw.polygon(surf, IVORY, grip)
    pygame.draw.polygon(surf, IVORY_SH, [(33, cy + 5), (36, cy + 4), (35, cy + 11),
                                         (33, cy + 11)])
    pygame.draw.line(surf, KEYLINE, grip[0], grip[1], 1)

    # --- single gold magazine (slung down under the receiver) ----------------
    pygame.draw.polygon(surf, GOLD, mag)
    pygame.draw.polygon(surf, GOLD_SHADE, [(26, cy + 5), (29, cy + 5), (29, cy + 12),
                                           (27, cy + 12)])
    pygame.draw.line(surf, GOLD_HI, (23, cy + 5), (25, cy + 11), 1)

    # --- long gold barrel ----------------------------------------------------
    # Same 3-band value structure as the receiver (shade core under a bright top
    # line) so the long barrel reads as one polished metal piece with the body,
    # not a dull prong — the wide value gap is what survives downscale+grayscale.
    pygame.draw.rect(surf, GOLD_DEEP, barrel, border_radius=2)
    pygame.draw.rect(surf, GOLD, pygame.Rect(barrel.x, barrel.y, barrel.w, barrel.h - 1),
                     border_radius=2)
    pygame.draw.line(surf, GOLD_FLASH, (barrel.x + 1, barrel.y),
                     (barrel.right - 2, barrel.y), 1)
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
    # facet glint kept gem-small but brighter so it pops as a cut stone, not a dot
    pygame.draw.line(surf, GEM_HI, (gem_c[0] - 1, gem_c[1] - 1), (gem_c[0] + 1, gem_c[1] - 2), 1)
    surf.set_at((gem_c[0], gem_c[1] - 2), GEM_HI)

    # --- warm night keyline along the metal top run --------------------------
    pygame.draw.line(surf, KEYLINE, (barrel.x, barrel.y),
                     (body.right - 1, body.y), 1)

    # --- bling sparkle -------------------------------------------------------
    # The old thin 4-point star vanished at 22px. A fatter, brighter 1px cross
    # plus one HOT pixel on the brightest gold corner survives the downscale and
    # gives the "luxury" glint the gem alone can't fully carry.
    sx, sy = body.right - 3, body.y - 1
    pygame.draw.line(surf, SPARKLE, (sx - 2, sy), (sx + 2, sy), 1)
    pygame.draw.line(surf, SPARKLE, (sx, sy - 2), (sx, sy + 2), 1)
    surf.set_at((sx, sy), (255, 255, 255))
    surf.set_at((sx + 1, sy), SPARKLE)
    surf.set_at((sx, sy - 1), SPARKLE)

    return pygame.transform.smoothscale(surf, (22, 22))
