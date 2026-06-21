"""BAMBOO STEAMER parcel cosmetic (MID tier).

A stacked dim-sum steamer: two shallow bamboo drums under a domed lid — a tidy
ringed tower. Horizontal banding stripes + the dome carry the "steamer" read at
22px. This is a TALL ringed-drum silhouette, distinct from every box/bag/jar.

Built at 2× then smoothscaled to 22 so the dark outline and the band shadows
survive the tiny read and the bird's tilt rotation. The steam puff is kept tiny
and centred on top so it doesn't smear oddly when the sprite banks."""
import pygame

SIZE = 22
SS = 44  # 2× supersample; smoothscaled down for a crisp outline at 22px

# DAY palette — pale woven bamboo, darker band shadows, deep rim under the lid.
BAMBOO = (0xD8, 0xB8, 0x77)
BAND_SH = (0xA0, 0x7C, 0x3C)
LID_RIM = (0x7A, 0x5A, 0x28)
HILITE = (0xEF, 0xDF, 0xB4)   # top sheen on the dome, also lifts the day read
STEAM = (0xEF, 0xE6, 0xD2)    # warm steam-glow puff above the lid
OUTLINE = (0x2C, 0x1C, 0x0E)  # dark high-value edge to hold the silhouette


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def _drum(s, rect, top_shade=False):
    """A shallow bamboo cylinder: dark outline frame, vertical weave gradient
    masked into a soft rounded body, then a band-shadow line so two of them
    stacked read as a ringed tower."""
    pygame.draw.rect(s, OUTLINE, rect.inflate(4, 4), border_radius=5)
    fill = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        # Lighter at the top of each ring, sinking to band shadow at its base —
        # the cue that this is a stack of woven rings, not a smooth tube.
        col = _lerp(BAMBOO, BAND_SH, t * 0.8)
        fill.fill(col + (255,), pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=3)
    fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(fill, rect.topleft)
    # Top weave-sheen so each ring catches light.
    pygame.draw.line(s, HILITE, (rect.x + 3, rect.y + 1),
                     (rect.right - 4, rect.y + 1), 1)
    if top_shade:
        return
    # Band-shadow seam at the base of the ring — the horizontal stripe that
    # makes the silhouette unmistakably a stacked steamer.
    pygame.draw.line(s, BAND_SH, (rect.x + 1, rect.bottom - 2),
                     (rect.right - 2, rect.bottom - 2), 2)
    pygame.draw.line(s, OUTLINE, (rect.x + 1, rect.bottom - 1),
                     (rect.right - 2, rect.bottom - 1), 1)


def build(mode="normal"):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cx = SS // 2
    DRUM_W = 30
    DRUM_H = 11

    # Tiny steam wisp first so the tower bakes over its base — a short centred
    # puff that survives rotation without smearing into a tail.
    for dy, r, a in ((-2, 5, 70), (1, 4, 110), (4, 3, 150)):
        puff = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(puff, STEAM + (a,), (r + 1, r + 1), r)
        s.blit(puff, (cx - r - 1, 4 + dy))

    # Two stacked drums forming the ringed tower body.
    lower = pygame.Rect(0, 0, DRUM_W, DRUM_H)
    lower.center = (cx, 33)
    upper = pygame.Rect(0, 0, DRUM_W, DRUM_H)
    upper.center = (cx, 33 - DRUM_H)
    _drum(s, lower)
    _drum(s, upper)

    # Domed LID — a low rim band plus a shallow cap, the crown of the tower.
    rim = pygame.Rect(upper.x - 2, upper.y - 5, DRUM_W + 4, 6)
    pygame.draw.rect(s, OUTLINE, rim.inflate(2, 2), border_radius=3)
    rimfill = pygame.Surface((rim.w, rim.h), pygame.SRCALPHA)
    for y in range(rim.h):
        rimfill.fill(_lerp(BAMBOO, LID_RIM, y / max(1, rim.h - 1)) + (255,),
                     pygame.Rect(0, y, rim.w, 1))
    s.blit(rimfill, rim.topleft)

    dome = pygame.Rect(rim.x + 4, rim.y - 6, rim.w - 8, 12)
    pygame.draw.ellipse(s, OUTLINE, dome.inflate(2, 2))
    capmask = pygame.Surface((dome.w, dome.h), pygame.SRCALPHA)
    pygame.draw.ellipse(capmask, (255, 255, 255, 255), capmask.get_rect())
    cap = pygame.Surface((dome.w, dome.h), pygame.SRCALPHA)
    for y in range(dome.h):
        cap.fill(_lerp(HILITE, BAND_SH, y / max(1, dome.h - 1)) + (255,),
                 pygame.Rect(0, y, dome.w, 1))
    cap.blit(capmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(cap, dome.topleft)
    # Dome sheen + a tiny knob so the lid reads as a lid, not a third ring.
    pygame.draw.arc(s, HILITE, dome.inflate(-3, -2), 0.5, 2.4, 2)
    pygame.draw.circle(s, LID_RIM, (cx, dome.y + 1), 2)
    pygame.draw.circle(s, OUTLINE, (cx, dome.y + 1), 2, 1)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
