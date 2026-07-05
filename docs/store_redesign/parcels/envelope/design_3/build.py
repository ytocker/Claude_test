"""ROYAL DECREE — premium ENVELOPE parcel concept.

A wax-sealed noble missive: cream parchment envelope whose two strongest marks
are (1) a real downward flap V — two slanted gold-trimmed edges meeting at a
point BELOW the seal — and (2) an OVERSIZED gold-rimmed crimson wax crest sat at
the flap junction. The flap apex is pushed down so it clears the seal, giving an
unmistakable ENVELOPE read before the crest registers; the crest is the richest
saturated mark so it owns the eye at 22px and survives the gameplay rotozoom on
day AND night sky. Crimson is darkened so the crest reads as an obvious DARK hub
on a LIGHT parchment slab even in grayscale.
"""
import pygame

from game.draw import lerp_color as _lerp_color

# DAY parchment / gold / crimson, plus a warm gold KEYLINE so the slab still
# reads against a dark night sky without a per-mode sprite.
PARCH_HI = (239, 226, 192)     # ~#EFE2C0 parchment (flap face — the LIGHT step)
PARCH_SHADE = (196, 176, 130)  # darkened lower-body so the flap V is a value step
GOLD = (227, 178, 60)          # ~#E3B23C
GOLD_HI = (246, 215, 122)      # ~#F6D77A
GOLD_SHADE = (170, 126, 40)
CRIMSON = (142, 30, 50)        # ~#8E1E32 wax — dark hub for grayscale pass
CRIMSON_HI = (190, 64, 82)
CRIMSON_SHADE = (96, 18, 34)
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

    # Parchment LOWER body: soft vertical gradient masked to the rounded rect,
    # kept on the darker PARCH_SHADE end so the lighter flap face reads as a
    # distinct value step above it.
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        row = _lerp_color(PARCH_HI, PARCH_SHADE, 0.35 + 0.65 * t)
        body.fill(row + (255,), pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)

    # The flap is the second-strongest mark after the crest: a downward V from
    # the top corners to a point BELOW the seal, filled with the LIGHT parchment
    # so the V is a real value step over the darker lower body. Apex pushed to
    # cy+6 so the seal (centred ~cy) sits inside the V, not amputating its tip.
    apex = (cx, cy + 6)
    fl = (rect.x + 2, rect.y + 2)
    fr = (rect.right - 3, rect.y + 2)
    flap = [fl, fr, apex]
    pygame.draw.polygon(surf, PARCH_HI, flap)
    # Gold V trim along the two slanted flap edges, over a dark under-stroke so
    # the two diagonals hold as one continuous V down to the apex at true size.
    for a, b in ((fl, apex), (fr, apex)):
        pygame.draw.line(surf, OUTLINE, a, b, 3)
    for a, b in ((fl, apex), (fr, apex)):
        pygame.draw.line(surf, GOLD, a, b, 2)
    # Brighten the left diagonal only — a single lit edge reads gilt, not noisy.
    pygame.draw.line(surf, GOLD_HI, fl, apex, 1)

    # ONE continuous concentric gold border inset ~1px — a clean gilt frame
    # reads "ornate / royal" far better than four vanishing corner flecks, and
    # doubles as the warm keyline that lifts the slab off a dark night sky.
    pygame.draw.rect(surf, KEYLINE, rect.inflate(-3, -3), width=1,
                     border_radius=rad - 1)

    # OVERSIZED wax crest — the identity. Nudged up ~1px to sit AT the flap
    # junction (where a real wax seal closes the flap), reinforcing the envelope
    # read with the same pixels. Three clean rings only — dark backing, gold rim,
    # crimson body — so nothing smears to mud under the rotozoom; the gold ring
    # pops against both the parchment slab and the dark wax for the richest read.
    scx, scy = cx, cy - 1
    sr = 8
    pygame.draw.circle(surf, OUTLINE, (scx, scy), sr + 1)        # dark backing
    pygame.draw.circle(surf, GOLD, (scx, scy), sr)               # gold rim
    # Lit the upper-left arc of the rim only, for a struck-metal sheen.
    pygame.draw.circle(surf, GOLD_HI, (scx - 1, scy - 1), sr, 1)
    pygame.draw.circle(surf, CRIMSON, (scx, scy), sr - 2)        # wax body
    pygame.draw.circle(surf, CRIMSON_SHADE, (scx, scy), sr - 2, 1)
    # A single crimson gloss dot on the upper-left of the wax — one clean
    # specular, no sub-pixel emblem that would smear to noise at 22px.
    pygame.draw.circle(surf, CRIMSON_HI, (scx - 2, scy - 2), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
