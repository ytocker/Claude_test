"""SEALED MAILER — LOW-tier parcel cosmetic.

A padded kraft mailer tied with a twine cross + a central red wax seal. It is
the FLATTEST object in the parcel roster — a slab, not a volume — so the read
has to survive the bird's bank without collapsing into "a playing card". The
diagonal twine cross + the bold central wax-seal dot are the rescue: an X over
a slab is unmistakably a *tied package* at any tilt, and the red dot is the one
saturated mark that anchors the eye dead-centre through the whole flight arc.
"""
import pygame

from game.draw import lerp_color as _lerp_color

# DAY kraft / twine / red seal, plus a NIGHT-friendly warm keyline so the slab
# still reads against a dark sky without changing the sprite per mode.
KRAFT_BASE = (200, 161, 101)   # ~#C8A165
KRAFT_SHADE = (162, 124,  72)
KRAFT_HI = (224, 192, 138)
TWINE = (107,  84,  48)        # ~#6B5430
TWINE_HI = (150, 122,  78)
SEAL = (193,  59,  46)         # ~#C13B2E
SEAL_HI = (228, 116, 100)
SEAL_SHADE = (140,  36,  30)
OUTLINE = ( 40,  24,  14)      # dark, high-value: reads on bright day sky
KEYLINE = (230, 196, 136)      # warm rim (~#E6C488) — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static slab sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)

    # Slab: wide, short, soft-cornered — a thin rectangle, not a box. Kept off
    # the very edges so the rotozoom in gameplay never clips the corners.
    BW, BH = 34, 26
    cx, cy = S // 2, S // 2
    rect = pygame.Rect(cx - BW // 2, cy - BH // 2, BW, BH)
    rad = 5

    # Baked outline frame (drawn first, slightly inflated) — the dark silhouette
    # that survives on the (170,220,245) day sky.
    pygame.draw.rect(surf, OUTLINE, rect.inflate(6, 6), border_radius=rad + 2)

    # Kraft body: gentle vertical gradient masked to the rounded rect.
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        body.fill(_lerp_color(KRAFT_HI, KRAFT_SHADE, t) + (255,),
                  pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)

    # Warm keyline rim INSIDE the outline — gives a glowing edge on night sky
    # while staying subtle against day.
    pygame.draw.rect(surf, KEYLINE, rect, width=1, border_radius=rad)

    # Padded-mailer quilting: faint diagonal hatch so the slab never reads as a
    # smooth card. Kept low-contrast — the cross + seal must dominate.
    pad_col = (*KRAFT_SHADE, 70)
    for d in range(-BH, BW, 9):
        pygame.draw.line(surf, pad_col,
                         (rect.x + max(0, d), rect.y + max(0, -d)),
                         (rect.x + min(BW, d + BH), rect.y + min(BH, BW - d)), 1)

    # Twine cross — the identity. Corner-to-corner X, drawn thick with a dark
    # under-stroke (so it carries its own outline over the kraft) + a lighter
    # twist highlight. An X over a slab = a *tied* package at every bank angle.
    p_tl = (rect.x + 4, rect.y + 4)
    p_br = (rect.right - 5, rect.bottom - 5)
    p_tr = (rect.right - 5, rect.y + 4)
    p_bl = (rect.x + 4, rect.bottom - 5)
    for a, b in ((p_tl, p_br), (p_tr, p_bl)):
        pygame.draw.line(surf, OUTLINE, a, b, 5)
    for a, b in ((p_tl, p_br), (p_tr, p_bl)):
        pygame.draw.line(surf, TWINE, a, b, 3)
        pygame.draw.line(surf, TWINE_HI, a, b, 1)

    # Wax seal — bold round dot dead-centre, the one saturated mark. Outlined so
    # it pops on both skies; a small offset highlight reads as glossy wax.
    sr = 5
    pygame.draw.circle(surf, OUTLINE, (cx, cy), sr + 1)
    pygame.draw.circle(surf, SEAL, (cx, cy), sr)
    pygame.draw.circle(surf, SEAL_SHADE, (cx, cy), sr, 1)
    pygame.draw.circle(surf, SEAL_HI, (cx - 1, cy - 1), 2)

    return pygame.transform.smoothscale(surf, (22, 22))
