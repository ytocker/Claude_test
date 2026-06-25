"""ROYAL DECREE — premium ENVELOPE parcel concept.

A wax-sealed noble missive: cream parchment envelope with an ornate gold-
trimmed pointed flap and an OVERSIZED gold-rimmed crimson wax crest dead
centre. The big gilded wax seal is the identity — it has to read as the
single richest mark on the slab, so the seal is drawn large with a bright
gold rim and a dark crimson body so the gold ring pops against both the
parchment and the wax. Gold corner flourishes + flap trim carry the "this
is valuable" read; everything else stays low-contrast so the crest owns the
eye at 22px and survives the gameplay rotozoom on day AND night sky.
"""
import pygame

from game.draw import lerp_color as _lerp_color

# DAY parchment / gold / crimson, plus a warm gold KEYLINE so the slab still
# reads against a dark night sky without a per-mode sprite.
PARCH_HI = (239, 226, 192)     # ~#EFE2C0 parchment
PARCH_SHADE = (208, 190, 146)
GOLD = (227, 178, 60)          # ~#E3B23C
GOLD_HI = (246, 215, 122)      # ~#F6D77A
GOLD_SHADE = (170, 126, 40)
CRIMSON = (168, 36, 58)        # ~#A8243A wax
CRIMSON_HI = (206, 70, 88)
CRIMSON_SHADE = (118, 24, 42)
OUTLINE = (58, 46, 30)         # ~#3A2E1E dark, high-value: reads on day sky
KEYLINE = (246, 215, 122)      # warm gold rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static slab sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)

    BW, BH = 34, 26
    cx, cy = S // 2, S // 2
    rect = pygame.Rect(cx - BW // 2, cy - BH // 2, BW, BH)
    rad = 4

    # Baked outline frame (drawn first, slightly inflated) — the dark
    # silhouette that survives on the bright (170,220,245) day sky.
    pygame.draw.rect(surf, OUTLINE, rect.inflate(6, 6), border_radius=rad + 2)

    # Parchment body: soft vertical gradient masked to the rounded rect. Kept
    # low-contrast so the crimson/gold crest is the only saturated focal mark.
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        row = _lerp_color(PARCH_HI, PARCH_SHADE, t)
        body.fill(row + (255,), pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)

    # Warm gold keyline rim INSIDE the outline — glowing edge on night sky,
    # subtle against day, and it doubles as the envelope's gilt border.
    pygame.draw.rect(surf, KEYLINE, rect, width=1, border_radius=rad)

    # Ornate pointed flap — a downward V from the top corners to a centre
    # point, edged in gold trim. The flap is what makes the slab read as an
    # ENVELOPE before the seal registers; the gold trim makes it read royal.
    apex = (cx, cy + 3)
    fl = (rect.x + 2, rect.y + 2)
    fr = (rect.right - 3, rect.y + 2)
    flap = [fl, fr, apex]
    # Filled flap one shade darker than the body so the V edge is legible.
    pygame.draw.polygon(surf, PARCH_SHADE, flap)
    # Gold trim along the two slanted flap edges (the V), drawn over a dark
    # under-stroke so the gilt line holds against the parchment at true size.
    for a, b in ((fl, apex), (fr, apex)):
        pygame.draw.line(surf, OUTLINE, a, b, 3)
    for a, b in ((fl, apex), (fr, apex)):
        pygame.draw.line(surf, GOLD, a, b, 2)
    pygame.draw.line(surf, GOLD_HI, fl, apex, 1)

    # Gilded corner flourishes — short gold L-marks tucked into each corner.
    # Read as ornamental gilt without competing with the central crest.
    inset = 4
    arm = 4
    corners = (
        ((rect.x + inset, rect.y + inset), (1, 1)),
        ((rect.right - inset, rect.y + inset), (-1, 1)),
        ((rect.x + inset, rect.bottom - inset), (1, -1)),
        ((rect.right - inset, rect.bottom - inset), (-1, -1)),
    )
    for (px, py), (sx, sy) in corners:
        pygame.draw.line(surf, GOLD, (px, py), (px + sx * arm, py), 1)
        pygame.draw.line(surf, GOLD, (px, py), (px, py + sy * arm), 1)

    # OVERSIZED wax crest — the identity. Big crimson disc with a bright gold
    # rim and an embossed crest dot at centre. Layered dark→gold→crimson so
    # the gold ring pops against both the parchment slab and the dark wax,
    # giving the richest "valuable" read; sized large so it owns the eye at
    # 22px and stays a clear hub under the gameplay rotozoom.
    sr = 8
    pygame.draw.circle(surf, OUTLINE, (cx, cy), sr + 1)      # dark backing
    pygame.draw.circle(surf, GOLD, (cx, cy), sr)             # gold rim
    pygame.draw.circle(surf, GOLD_HI, (cx, cy), sr, 1)       # rim highlight
    pygame.draw.circle(surf, CRIMSON, (cx, cy), sr - 2)      # wax body
    pygame.draw.circle(surf, CRIMSON_SHADE, (cx, cy), sr - 2, 1)
    # Embossed crest at centre: a small gold dot ringed by crimson so it reads
    # as a struck emblem, not a flat hole.
    pygame.draw.circle(surf, GOLD, (cx, cy), 2)
    pygame.draw.circle(surf, GOLD_HI, (cx - 1, cy - 1), 1)
    # Glossy wax highlight on the upper-left of the disc.
    pygame.draw.circle(surf, CRIMSON_HI, (cx - 3, cy - 3), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
