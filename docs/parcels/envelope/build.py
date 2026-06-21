"""SEALED MAILER — LOW-tier parcel cosmetic.

A padded kraft mailer tied with a twine cross + a central red wax seal. It is
the FLATTEST object in the parcel roster — a slab, not a volume — so the read
has to survive the bird's bank without collapsing into "a playing card". The
twine X tied corner-to-corner is the identity; the small red wax seal sits at
the KNOT where the X crosses. The X must read as one continuous cross with a
seal at its centre — never a dot with spokes — so the X is drawn full-diagonal
and the seal is kept small enough that all four twine arms extend clearly past
its rim.
"""
import pygame

from game.draw import lerp_color as _lerp_color

# DAY kraft / twine / red seal, plus a NIGHT-friendly warm keyline so the slab
# still reads against a dark sky without changing the sprite per mode.
KRAFT_BASE = (200, 161, 101)   # ~#C8A165
KRAFT_SHADE = (162, 124,  72)
KRAFT_HI = (224, 192, 138)
# Twine one shade darker + thicker than r1 so the X is unambiguous before the
# seal registers; the lighter twist highlight is dropped as load-bearing detail.
TWINE = ( 92,  71,  40)        # ~#5C4728 (darker than r1's #6B5430)
SEAL = (193,  59,  46)         # ~#C13B2E
SEAL_HI = (228, 116, 100)
SEAL_SHADE = (140,  36,  30)
OUTLINE = ( 40,  24,  14)      # dark, high-value: reads on bright day sky
KEYLINE = (230, 196, 136)      # warm rim (~#E6C488) — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static slab sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)

    # Slab: a touch squarer than r1 (taller body) so the corner-to-corner X
    # reads as a CROSS, not a wide flat bowtie. Kept off the edges so the
    # gameplay rotozoom never clips the corners.
    BW, BH = 34, 28
    cx, cy = S // 2, S // 2
    rect = pygame.Rect(cx - BW // 2, cy - BH // 2, BW, BH)
    rad = 5

    # Baked outline frame (drawn first, slightly inflated) — the dark silhouette
    # that survives on the (170,220,245) day sky.
    pygame.draw.rect(surf, OUTLINE, rect.inflate(6, 6), border_radius=rad + 2)

    # Kraft body: gentle vertical gradient masked to the rounded rect. A faint
    # per-row value wobble replaces the r1 diagonal hatch — at 22px the hatch was
    # micro-noise, so the padded-mailer feel is baked as the softest texture that
    # never competes with the cross + seal.
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        base = _lerp_color(KRAFT_HI, KRAFT_SHADE, t)
        # Subtle alternating-row lift/dip: reads as soft padding, not a pattern.
        wob = 6 if (y % 3 == 0) else (-4 if (y % 3 == 1) else 0)
        row = (max(0, min(255, base[0] + wob)),
               max(0, min(255, base[1] + wob)),
               max(0, min(255, base[2] + wob)))
        body.fill(row + (255,), pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)

    # Warm keyline rim INSIDE the outline — gives a glowing edge on night sky
    # while staying subtle against day.
    pygame.draw.rect(surf, KEYLINE, rect, width=1, border_radius=rad)

    # Twine cross — the identity. Corner-to-corner X, drawn with a dark
    # under-stroke (its own outline over the kraft) and a thick twine core. An X
    # over a slab = a *tied* package at every bank angle. Drawn BEFORE the seal so
    # the seal lands on the knot while all four arms stay continuous past its rim.
    p_tl = (rect.x + 4, rect.y + 4)
    p_br = (rect.right - 5, rect.bottom - 5)
    p_tr = (rect.right - 5, rect.y + 4)
    p_bl = (rect.x + 4, rect.bottom - 5)
    for a, b in ((p_tl, p_br), (p_tr, p_bl)):
        pygame.draw.line(surf, OUTLINE, a, b, 6)
    for a, b in ((p_tl, p_br), (p_tr, p_bl)):
        pygame.draw.line(surf, TWINE, a, b, 4)

    # Wax seal — small, bold round dot at the knot, the one saturated mark. ~28%
    # smaller than r1 (sr 5→4) so it sits at the X's centre WITHOUT swallowing
    # it: the twine arms read continuous and the seal is "the knot," not a hub
    # with spokes. A 2px dark rim keeps the central anchor firm even at 90° edge-
    # on; a tiny offset highlight reads as glossy wax.
    sr = 4
    pygame.draw.circle(surf, OUTLINE, (cx, cy), sr + 2)
    pygame.draw.circle(surf, SEAL, (cx, cy), sr)
    pygame.draw.circle(surf, SEAL_SHADE, (cx, cy), sr, 2)
    pygame.draw.circle(surf, SEAL_HI, (cx - 1, cy - 1), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
