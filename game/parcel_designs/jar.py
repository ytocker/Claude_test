"""JAM JAR parcel cosmetic (LOW tier).

A squat preserve jar with a gingham cloth-capped lid: glass body + a "hat".
Built at 2× then smoothscaled to 22 so the dark outline, the glass-turn and the
cream gingham cap survive the tiny in-play read and the bird's tilt rotation.

Carry constraint drives the design: Pip's body under the parcel is RED, so a
pure-red cloth cap vanishes into him (the round-1 mushroom read). The cap is
the tell that this is a jar, so it must win on VALUE, not hue — gingham red on
CREAM, with a wide overhang and a hard dark gap so the "hat" survives Pip's
occlusion. The translucent amber glass core is the hook no other parcel has."""
import pygame

SIZE = 22
SS = 44  # 2× supersample; smoothscaled down for a crisp outline at 22px

# DAY palette — amber glass over a lighter translucent core.
GLASS = (0xE0, 0x96, 0x30)      # deeper amber for the lower-right glass wall
CORE = (0xFB, 0xD7, 0x8C)       # lighter translucent core (one step up)
CORE_HI = (0xFF, 0xEC, 0xC2)    # near-white centre so translucency reads
SPEC = (0xFF, 0xFF, 0xF4)       # upper-left specular highlight (glass cue)
# Cloth cap reads on VALUE against Pip's red — cream ground, red gingham checks.
CLOTH = (0xF3, 0xE6, 0xC8)      # cream cloth so it can't merge with red Pip
CLOTH_HI = (0xFF, 0xF8, 0xE6)   # lit cloth dome top
GINGHAM = (0xC8, 0x36, 0x2E)    # gingham red (sits ON the cream, doesn't carry it)
RIM = (0x6E, 0x40, 0x18)        # dark lid-lip band under the cloth
OUTLINE = (0x2C, 0x14, 0x0E)    # dark high-value edge to hold the silhouette
GAP = (0x1C, 0x0D, 0x09)        # hard dark gap separating cap from glass


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def build(mode="normal"):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cx = SS // 2

    # Glass BODY — squat rounded RECTANGLE, wider than tall, near-vertical walls
    # and flat-ish shoulders (small corner radius) so it can't read as a dome.
    body = pygame.Rect(0, 0, 28, 22)
    body.center = (cx, 30)
    pygame.draw.rect(s, OUTLINE, body.inflate(4, 4), border_radius=5)

    # 2-value glass turn: bright lit upper-left, deep amber lower-right wall, a
    # near-white core down the centre — a directional light that survives
    # smoothscale far better than a thin stripe.
    fill = pygame.Surface((body.w, body.h), pygame.SRCALPHA)
    for y in range(body.h):
        ty = y / max(1, body.h - 1)
        for x in range(body.w):
            tx = x / max(1, body.w - 1)
            # Distance from the centre core, biased so the lower-right is darker.
            ex = abs(x - body.w / 2) / (body.w / 2)
            wall = _lerp(CORE, GLASS, 0.5 * ty + 0.5 * tx)   # darker toward br
            col = _lerp(CORE_HI, wall, ex ** 0.85)
            # Upper-left specular wash brightens the lit shoulder.
            lit = max(0.0, (0.6 - tx) + (0.5 - ty)) * 1.1
            if lit > 0:
                col = _lerp(col, SPEC, min(0.55, lit))
            fill.set_at((x, y), col + (255,))
    mask = pygame.Surface((body.w, body.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=4)
    fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(fill, body.topleft)

    # Crisp upper-left specular streak — the single brightest glass cue.
    pygame.draw.line(s, SPEC + (235,),
                     (body.x + 5, body.y + 4), (body.x + 5, body.bottom - 6), 2)
    pygame.draw.line(s, SPEC + (120,),
                     (body.x + 8, body.y + 4), (body.x + 8, body.y + body.h // 2), 1)

    # Translucent jam meniscus line near the top of the glass.
    pygame.draw.line(s, _lerp(GLASS, RIM, 0.4),
                     (body.x + 3, body.y + 4), (body.right - 4, body.y + 4), 2)

    # Hard dark GAP between glass and lid — guarantees the cap edge survives.
    gap = pygame.Rect(body.x - 2, body.y - 3, body.w + 4, 3)
    pygame.draw.rect(s, GAP, gap)

    # Dark RIM band — the lid LIP that clamps the glass, UNDER the cloth.
    rim = pygame.Rect(body.x - 1, body.y - 5, body.w + 2, 4)
    pygame.draw.rect(s, RIM, rim)
    pygame.draw.rect(s, OUTLINE, rim, width=1)

    # Cloth CAP — wide cream gingham hat. Made TALLER than the rim band and wide
    # overhang so it survives Pip's red occlusion and reads as the lid cloth.
    cap_h = 13
    cap_w = body.w + 14
    cap = pygame.Rect(0, 0, cap_w, cap_h)
    cap.midbottom = (body.centerx, rim.top + 1)
    pygame.draw.rect(s, OUTLINE, cap.inflate(2, 2), border_radius=5)

    capsurf = pygame.Surface((cap.w, cap.h), pygame.SRCALPHA)
    for y in range(cap.h):
        t = y / max(1, cap.h - 1)
        capsurf.fill(_lerp(CLOTH_HI, CLOTH, t) + (255,),
                     pygame.Rect(0, y, cap.w, 1))
    capmask = pygame.Surface((cap.w, cap.h), pygame.SRCALPHA)
    # Gently domed top, flat overhanging hem so it reads as cloth, not a ball.
    pygame.draw.rect(capmask, (255, 255, 255, 255),
                     pygame.Rect(0, 3, cap.w, cap.h - 3), border_radius=3)
    pygame.draw.ellipse(capmask, (255, 255, 255, 255),
                        pygame.Rect(2, 0, cap.w - 4, 10))
    capsurf.blit(capmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Gingham checks ON the cream cloth — a coarse 2-row check that survives the
    # downscale (red squares on cream = high value contrast = reads as pattern).
    check = 4
    for gy in range(0, cap.h, check):
        for gx in range(0, cap.w, check):
            if ((gx // check) + (gy // check)) % 2 == 0:
                col = _lerp(GINGHAM, CLOTH, 0.0)
                r = pygame.Rect(gx, gy, check, check)
                # Lit checks toward the top, deeper toward the hem.
                shade = _lerp(GINGHAM, OUTLINE, gy / cap.h * 0.35)
                pygame.draw.rect(capsurf, shade, r)
    capsurf.blit(capmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(capsurf, cap.topleft)

    # Scalloped cloth hem — cream lobes under the overhang sell the tied fabric.
    hem_y = cap.bottom - 1
    for i in range(4):
        dx = cap.x + 5 + i * (cap.w - 10) / 3
        pygame.draw.circle(s, OUTLINE, (int(dx), hem_y), 3)
        pygame.draw.circle(s, CLOTH, (int(dx), hem_y - 1), 2)

    # String tie groove where the cloth cinches to the rim.
    pygame.draw.line(s, _lerp(OUTLINE, GINGHAM, 0.3),
                     (cap.x + 3, cap.bottom - 3), (cap.right - 3, cap.bottom - 3), 1)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
