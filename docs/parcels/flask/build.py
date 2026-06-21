"""GENIE FLASK parcel cosmetic (HIGH tier).

A faceted teardrop perfume/genie flask: a wide-bottomed DIAMOND glass body
that tapers to a narrow shoulder, capped by a gold COLLAR and a round domed
STOPPER — a gem-on-a-stem outline. The only cool-blue jewel tone in HIGH, so
it reads as an angular sapphire rather than the round message bottle. Built at
2× (44px) then smoothscaled to 22 so the dark keyline, the facet seams, and
the gold collar survive the tiny in-play read and the bird's tilt rotation.

Carry context: Pip's red body occludes the TOP, so the main tell — the
faceted blue body — sits in the LOWER/visible half; the warm gold collar gives
a colour break against Pip's red where the two meet."""
import pygame

SIZE = 22
SS = 44  # 2× supersample; smoothscaled down for a crisp outline at 22px

# DAY palette — sapphire glass over a lighter core, gold collar/stopper, icy
# highlight. Night holds the glass and leans on a faint inner glow.
GLASS = (0x3A, 0x6F, 0xD8)       # sapphire glass wall
CORE = (0x7F, 0xA8, 0xF2)        # lighter translucent core (lit facet)
COLLAR = (0xE8, 0xB2, 0x3C)      # gold collar / stopper
COLLAR_HI = (0xFF, 0xDD, 0x88)   # gold sheen
COLLAR_SH = (0xB0, 0x82, 0x20)   # gold underside
HI = (0xDC, 0xEB, 0xFF)          # icy glass highlight / facet line
GLOW = (0x9F, 0xC0, 0xFF)        # faint inner glow tint (night read)
OUTLINE = (0x12, 0x22, 0x4A)     # dark high-value sapphire edge


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def build(mode="normal"):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cx = SS // 2

    # ---- Vertical layout. The teardrop body is bottom-heavy so its widest,
    # most identifiable part lives in the lower/visible half under Pip; the
    # collar + stopper crown the top where Pip's body crops in.
    body_bot = 39        # widest base of the teardrop
    body_top = 19        # narrow shoulder where glass meets the collar
    body_hw = 13         # half-width at the base
    collar_y = body_top  # gold collar band sits on the shoulder
    stop_cy = 11         # centre of the round domed stopper

    # Teardrop / diamond silhouette — wide rounded base tapering to a point-ish
    # shoulder. Drawn as one closed polygon so the outline is a single edge.
    body_poly = [
        (cx,              body_top),                 # shoulder apex
        (cx + body_hw - 4, body_top + 4),
        (cx + body_hw,     body_bot - 8),            # widest below centre
        (cx + body_hw - 5, body_bot - 1),
        (cx,               body_bot + 1),            # rounded base tip
        (cx - body_hw + 5, body_bot - 1),
        (cx - body_hw,     body_bot - 8),
        (cx - body_hw + 4, body_top + 4),
    ]

    # Dark outline pass — fat silhouette first, the gem fill sits inside it.
    pygame.draw.polygon(s, OUTLINE, body_poly)

    # ---- Faceted glass fill. A left dark wall, a bright central facet, and a
    # right mid wall fake the cut-jewel read: the central wedge catches light.
    fill = pygame.Surface((SS, SS), pygame.SRCALPHA)
    inner = [(cx, body_top + 2)]
    inner += [(x - (1 if x > cx else -1) if x != cx else x,
               y) for x, y in body_poly[1:]]
    pygame.draw.polygon(fill, (255, 255, 255, 255), body_poly)

    gem = pygame.Surface((SS, SS), pygame.SRCALPHA)
    # Horizontal gradient across the body: dark left wall → bright spine →
    # mid right, so the diamond reads as a faceted cylinder of light.
    left = cx - body_hw
    for x in range(left, cx + body_hw + 1):
        t = (x - left) / (2 * body_hw)
        if t < 0.45:
            col = _lerp(GLASS, CORE, t / 0.45)
        else:
            col = _lerp(CORE, GLASS, (t - 0.45) / 0.55 * 0.7)
        gem.fill(col + (245,), pygame.Rect(x, 0, 1, SS))
    gem.blit(fill, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(gem, (0, 0))

    # ---- Facet SEAMS — two angular lines from the shoulder fanning to the
    # base corners. These are the cut-gem tell that separates it from a round
    # bottle. A bright spine seam + a shaded right seam.
    pygame.draw.line(s, _lerp(HI, CORE, 0.2),
                     (cx, body_top + 4), (cx - 4, body_bot - 3), 2)
    pygame.draw.line(s, _lerp(OUTLINE, GLASS, 0.55),
                     (cx, body_top + 4), (cx + 6, body_bot - 5), 1)
    # A short upper facet line catching the shoulder.
    pygame.draw.line(s, _lerp(HI, CORE, 0.35),
                     (cx - 4, body_top + 6), (cx, body_top + 4), 1)

    # ---- Bright specular glint high on the left facet — the wet-glass cue.
    pygame.draw.line(s, (0xFF, 0xFF, 0xFF, 220),
                     (cx - 6, body_top + 7), (cx - 7, body_bot - 12), 2)
    pygame.draw.circle(s, (255, 255, 255, 230), (cx - 6, body_top + 8), 2)

    # ---- GOLD COLLAR — a flat band capping the shoulder, the warm break
    # against Pip's red. Drawn as a rounded bar with a lit top edge.
    col_w, col_h = 11, 5
    collar = pygame.Rect(cx - col_w // 2, collar_y - col_h + 1, col_w, col_h)
    pygame.draw.rect(s, OUTLINE, collar.inflate(2, 2), border_radius=2)
    for i in range(col_h):
        t = i / max(1, col_h - 1)
        c = _lerp(COLLAR_HI, COLLAR_SH, t)
        pygame.draw.line(s, c, (collar.x, collar.y + i),
                         (collar.right - 1, collar.y + i))
    pygame.draw.line(s, COLLAR_HI, (collar.x + 1, collar.y),
                     (collar.right - 2, collar.y), 1)

    # ---- Domed STOPPER — a round gold gem perched on the collar, the
    # gem-on-a-stem crown. Short neck links it to the collar.
    pygame.draw.rect(s, OUTLINE,
                     pygame.Rect(cx - 2, stop_cy + 4, 4, collar_y - stop_cy - 5))
    pygame.draw.rect(s, COLLAR,
                     pygame.Rect(cx - 1, stop_cy + 4, 2, collar_y - stop_cy - 5))
    stop_r = 5
    pygame.draw.circle(s, OUTLINE, (cx, stop_cy), stop_r + 1)
    pygame.draw.circle(s, COLLAR, (cx, stop_cy), stop_r)
    pygame.draw.circle(s, COLLAR_SH, (cx, stop_cy), stop_r, 1)
    pygame.draw.circle(s, COLLAR_HI, (cx - 2, stop_cy - 2), 2)

    # ---- Faint inner GLOW — a soft sapphire bloom low in the body so the
    # glass still reads as lit on the dark NIGHT sky.
    glow = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.circle(glow, GLOW + (70,), (cx, body_bot - 9), 7)
    pygame.draw.circle(glow, GLOW + (40,), (cx, body_bot - 9), 11)
    g_mask = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.polygon(g_mask, (255, 255, 255, 255), body_poly)
    glow.blit(g_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(glow, (0, 0))

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
