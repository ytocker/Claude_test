"""JAM JAR parcel cosmetic (LOW tier).

A squat preserve jar with a gingham cloth-capped lid: glass body + a "hat".
Built at 2× then smoothscaled to 22 so the dark outline and one glass-highlight
stripe survive the tiny in-play read and the bird's tilt rotation. The
translucent amber core is the hook — glass material no other parcel has."""
import pygame

SIZE = 22
SS = 44  # 2× supersample; smoothscaled down for a crisp outline at 22px

# DAY palette — amber glass over a lighter translucent core, gingham-red cloth.
GLASS = (0xE8, 0xA3, 0x3D)
CORE = (0xF6, 0xC6, 0x6E)
LID = (0xC2, 0x3B, 0x33)
RIM = (0x7A, 0x4A, 0x1E)
INNER_HI = (0xFF, 0xD9, 0x8A)   # night-leaning inner glow, also lifts day read
OUTLINE = (0x33, 0x18, 0x12)    # dark high-value edge to hold the silhouette


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def build(mode="normal"):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cx = SS // 2

    # Glass BODY — squat rounded rectangle. Outline frame first, then a vertical
    # amber→core gradient masked into the rounded shape so the rim stays dark.
    body = pygame.Rect(0, 0, 26, 24)
    body.center = (cx, 28)
    pygame.draw.rect(s, OUTLINE, body.inflate(4, 4), border_radius=8)

    fill = pygame.Surface((body.w, body.h), pygame.SRCALPHA)
    for y in range(body.h):
        t = y / max(1, body.h - 1)
        # Lighter translucent core down the middle, deeper amber at the glass
        # walls — sells curvature and the see-through preserve.
        edge = _lerp(CORE, GLASS, t)
        for x in range(body.w):
            ex = abs(x - body.w / 2) / (body.w / 2)
            col = _lerp(_lerp(CORE, edge, 0.35), edge, ex)
            fill.set_at((x, y), col + (255,))
    mask = pygame.Surface((body.w, body.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=6)
    fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(fill, body.topleft)

    # Translucent jam meniscus line near the top of the glass.
    pygame.draw.line(s, _lerp(GLASS, RIM, 0.4),
                     (body.x + 3, body.y + 5), (body.right - 4, body.y + 5), 2)

    # Vertical glass-highlight stripe — the cue that this is glass, not box.
    hi = pygame.Surface((4, body.h - 8), pygame.SRCALPHA)
    hi.fill(INNER_HI + (150,))
    s.blit(hi, (body.x + 6, body.y + 5))
    pygame.draw.line(s, (255, 255, 255, 200),
                     (body.x + 6, body.y + 5), (body.x + 6, body.bottom - 6), 1)

    # Dark RIM band where the lid clamps the glass.
    rim = pygame.Rect(body.x - 1, body.y - 3, body.w + 2, 6)
    pygame.draw.rect(s, RIM, rim, border_radius=2)
    pygame.draw.rect(s, OUTLINE, rim, width=1, border_radius=2)

    # Fabric ruffle SKIRT under the rim — a wider scalloped gingham cap that
    # overhangs the glass, reading as the "hat" that makes this a jam jar.
    skirt_top = body.y - 4
    skirt = pygame.Rect(body.x - 5, skirt_top - 9, body.w + 10, 11)
    pygame.draw.rect(s, OUTLINE, skirt.inflate(2, 2), border_radius=6)

    cap = pygame.Surface((skirt.w, skirt.h), pygame.SRCALPHA)
    for y in range(skirt.h):
        t = y / max(1, skirt.h - 1)
        cap.fill(_lerp(_lerp(LID, INNER_HI, 0.25), LID, t) + (255,),
                 pygame.Rect(0, y, skirt.w, 1))
    capmask = pygame.Surface((skirt.w, skirt.h), pygame.SRCALPHA)
    # Domed top so the cloth bulges over the preserve.
    pygame.draw.rect(capmask, (255, 255, 255, 255),
                     pygame.Rect(0, 4, skirt.w, skirt.h - 4), border_radius=4)
    pygame.draw.ellipse(capmask, (255, 255, 255, 255),
                        pygame.Rect(2, 0, skirt.w - 4, 12))
    cap.blit(capmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(cap, skirt.topleft)

    # Scalloped ruffle hem — imply the cloth folds with dots along the bottom.
    hem_y = skirt.bottom - 1
    for i in range(5):
        dx = skirt.x + 4 + i * (skirt.w - 8) / 4
        pygame.draw.circle(s, OUTLINE, (int(dx), hem_y), 2)
        pygame.draw.circle(s, _lerp(LID, INNER_HI, 0.35), (int(dx), hem_y - 1), 1)

    # Gingham hint on the cloth dome — a couple of cross dots, no fine grid.
    for gx, gy in ((skirt.centerx - 4, skirt.y + 4),
                   (skirt.centerx + 4, skirt.y + 4),
                   (skirt.centerx, skirt.y + 6)):
        pygame.draw.circle(s, _lerp(LID, OUTLINE, 0.5), (gx, gy), 1)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
