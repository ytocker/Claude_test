"""MESSAGE BOTTLE parcel cosmetic (MID tier).

A corked bottle laid HORIZONTALLY with a rolled cream scroll inside —
adventure mail. The long wide-not-tall profile is unique in the PARCELS tab:
round sea-glass belly on the left, a beefed-up tapered neck and cork nub on
the right, the cream scroll the high-value keyline inside the translucent
glass. Built at 2× (44px) then smoothscaled to 22 so the dark outline, the
neck pinch, and the single glass highlight streak survive the tiny in-play
read and the bird's tilt rotation."""
import pygame

SIZE = 22
SS = 44  # 2× supersample; smoothscaled down for a crisp outline at 22px

# DAY palette — sea-glass green translucent glass over a lighter core, warm
# cork, cream scroll. Night leans on the cream keyline + a faint glass glow.
GLASS = (0x5F, 0xA8, 0x8C)       # sea-glass green wall
CORE = (0x9F, 0xD3, 0xBC)        # lighter translucent core
CORK = (0xC9, 0xA3, 0x68)        # warm cork nub
CORK_HI = (0xE3, 0xC6, 0x95)
SCROLL = (0xF2, 0xE7, 0xC8)      # cream rolled paper — the high-value content
SCROLL_SH = (0xCE, 0xBD, 0x93)   # scroll roll shading for the coil read
OUTLINE = (0x16, 0x32, 0x29)     # dark high-value edge to hold the silhouette


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def build(mode="normal"):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cy = SS // 2

    # ---- Silhouette as one closed polygon so the outline is a single bold
    # edge. Built left→right: rounded belly, shoulder, tapered NECK, cork.
    belly_l = 4          # leftmost of the glass belly
    belly_r = 26         # belly meets the shoulder
    neck_l = 30          # shoulder pinches into the neck here
    neck_r = 36          # neck meets the cork
    cork_r = 41          # cork tip
    belly_hh = 11        # belly half-height (round body)
    neck_hh = 5          # BEEFED-UP neck half-height so it survives 22px
    cork_hh = 6          # cork slightly proud of the neck

    # Glass body outline silhouette — belly arc + tapering shoulder to neck.
    glass_poly = [
        (belly_l, cy),
        (belly_l + 2, cy - belly_hh + 3),
        (belly_l + 7, cy - belly_hh),
        (belly_r - 2, cy - belly_hh),
        (belly_r + 2, cy - belly_hh + 2),
        (neck_l, cy - neck_hh),
        (neck_r, cy - neck_hh),
        (neck_r, cy + neck_hh),
        (neck_l, cy + neck_hh),
        (belly_r + 2, cy + belly_hh - 2),
        (belly_r - 2, cy + belly_hh),
        (belly_l + 7, cy + belly_hh),
        (belly_l + 2, cy + belly_hh - 3),
    ]

    # Dark outline pass — draw the silhouette fat first, fill sits inside it.
    pygame.draw.polygon(s, OUTLINE, glass_poly)
    pygame.draw.line(s, OUTLINE, (belly_l, cy - belly_hh + 4),
                     (belly_l, cy + belly_hh - 4), 5)

    # ---- Glass fill — horizontal-banded green→core→green so the round belly
    # reads as a cylinder lit down its spine. Masked into the silhouette.
    fill = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.polygon(fill, (255, 255, 255, 255),
                        [(x, y) for x, y in glass_poly])
    glass = pygame.Surface((SS, SS), pygame.SRCALPHA)
    for y in range(cy - belly_hh, cy + belly_hh + 1):
        t = abs(y - cy) / belly_hh           # 0 at spine, 1 at the wall
        col = _lerp(CORE, GLASS, min(1.0, t))
        glass.fill(col + (235,), pygame.Rect(0, y, SS, 1))
    glass.blit(fill, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(glass, (0, 0))

    # ---- Rolled SCROLL inside the belly — the cream content that names this a
    # message bottle. A horizontal capsule with two coil end-caps.
    sc_l, sc_r = belly_l + 6, belly_r - 4
    sc_hh = 5
    scroll_rect = pygame.Rect(sc_l, cy - sc_hh, sc_r - sc_l, sc_hh * 2)
    pygame.draw.rect(s, _lerp(SCROLL, SCROLL_SH, 0.3), scroll_rect,
                     border_radius=sc_hh)
    # Lit upper half of the parchment.
    pygame.draw.rect(s, SCROLL,
                     pygame.Rect(sc_l, cy - sc_hh, sc_r - sc_l, sc_hh),
                     border_radius=sc_hh)
    # Two rolled coils at the ends — concentric arcs sell "rolled paper".
    for ex in (sc_l + 2, sc_r - 2):
        pygame.draw.circle(s, SCROLL, (ex, cy), sc_hh)
        pygame.draw.circle(s, SCROLL_SH, (ex, cy), sc_hh, 1)
        pygame.draw.circle(s, _lerp(SCROLL_SH, OUTLINE, 0.4), (ex, cy), 2, 1)
    # A couple of writing ticks on the parchment face for "a message".
    pygame.draw.line(s, _lerp(SCROLL_SH, OUTLINE, 0.5),
                     (sc_l + 6, cy - 1), (sc_r - 6, cy - 1), 1)
    pygame.draw.line(s, _lerp(SCROLL_SH, OUTLINE, 0.5),
                     (sc_l + 6, cy + 2), (sc_r - 8, cy + 2), 1)

    # ---- CORK nub — warm plug capping the neck. Rounded rectangle, lit top.
    cork = pygame.Rect(neck_r - 1, cy - cork_hh, cork_r - neck_r + 1,
                       cork_hh * 2)
    pygame.draw.rect(s, OUTLINE, cork.inflate(2, 2), border_radius=3)
    pygame.draw.rect(s, CORK, cork, border_radius=3)
    pygame.draw.line(s, CORK_HI, (cork.x + 1, cork.y + 1),
                     (cork.right - 2, cork.y + 1), 1)
    # Seam where cork meets glass lip.
    pygame.draw.line(s, OUTLINE, (neck_r, cy - neck_hh),
                     (neck_r, cy + neck_hh), 2)

    # ---- Glass HIGHLIGHT streak — the diagonal cue that this is glass. Sits
    # high on the belly, the one bright specular across the curved wall.
    pygame.draw.line(s, (0xEE, 0xFB, 0xF5, 220),
                     (belly_l + 5, cy - belly_hh + 3),
                     (belly_r - 4, cy - belly_hh + 5), 2)
    pygame.draw.line(s, (255, 255, 255, 150),
                     (belly_l + 6, cy - belly_hh + 2),
                     (belly_l + 11, cy - belly_hh + 2), 1)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
