"""DESIGN 1 — CONFETTI CONE (elevated classic party hat). SCRATCH ONLY.

The familiar tall cone, premiumised: a glossy foil sheen (a vertical white
highlight band down the lit side over flat magenta/violet foil), a scatter of
multicolour confetti dots, and curly ribbon streamers spiralling off the tip
above a small foil pom. The silhouette stays the canonical party cone so it
reads instantly; the sheen + ribbons make it feel celebratory and rich.
"""
import math

import pygame

from tools.partyhat_candidates._template import make_build, make_icon

# Foil colourway. Two body tones (lit/shade) read as a metallic sheen far
# better than a smooth gradient at head_w~26, where blends turn to mud.
_FOIL = (255, 46, 126)        # #FF2E7E magenta foil (lit flank)
_FOIL_LO = (74, 30, 140)      # #4A1E8C deep indigo — shaded flank, real value
                              # range vs Pip's warm body so the cone never
                              # merges into the bird on a bright day sky.
_FOIL_HI = (255, 255, 255)    # foil specular band
# Near-black violet keyline rings the whole silhouette so the warm-hued cone
# stays separated from Pip's warm body against the day sky.
_KEYLINE = (40, 20, 70)
_GOLD = (255, 210, 63)        # #FFD23F
_TEAL = (25, 195, 201)        # #19C3C9
_VIOLET = (123, 47, 247)
_MAGENTA = (255, 46, 126)
_WHITE = (245, 248, 255)
_TRIM = (255, 210, 63)
_TRIM_LO = (214, 168, 40)
_RIBBON = (_GOLD, _TEAL)


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Side-profile CONFETTI CONE sized for a head of width head_w, centred at
    cx with the base line at base_y."""
    r = head_w * 0.5
    f = 1 if facing >= 0 else -1

    # Cone leans a hair forward so it reads as worn. Height is held to ~1.3x
    # head_w so the tall cone clears the 64x100 composite top from the crown.
    tip_x = cx + f * r * 0.20
    tip_y = base_y - head_w * 1.30
    base_hw = r * 0.94
    base_cy = base_y - r * 0.20

    left_x = cx - base_hw
    right_x = cx + base_hw
    seat_dip = r * 0.32

    def underside(n=18):
        out = []
        for i in range(n + 1):
            t = i / n
            x = left_x + (right_x - left_x) * t
            lift = seat_dip * (1.0 - 4.0 * (t - 0.5) ** 2)
            out.append((x, base_cy + r * 0.30 - lift))
        return out

    bottom = underside()
    base_y_line = base_cy + r * 0.30

    # Solid foil body in the lit tone.
    cone = [(tip_x, tip_y)] + bottom
    pygame.draw.polygon(surf, _FOIL, cone)

    # Trailing flank a step darker (deep indigo) for cheap metallic roundness
    # and a true lit/shade value split.
    shade = [
        (tip_x, tip_y),
        (cx + f * -r * 0.10, base_y_line),
        bottom[0] if f >= 0 else bottom[-1],
    ]
    pygame.draw.polygon(surf, _FOIL_LO, shade)

    # Foil specular: a vertical white sheen band down the LIT side. A clipped
    # quad keeps it inside the cone; this single band sells "glossy foil".
    _draw_sheen(surf, tip_x, tip_y, left_x, right_x, base_y_line, r, f)

    # Confetti scatter — small multicolour dots peppered over the cone, gated
    # off below ~22px so the tiny hat stays a clean cone+ribbon silhouette.
    if head_w >= 22:
        _draw_confetti(surf, tip_x, tip_y, left_x, right_x, base_y_line, r, f)

    # Dark keyline around the full cone silhouette — drawn over body+sheen so
    # the warm foil never bleeds into Pip's warm body on the day sky.
    kw = max(1, int(r * 0.10))
    pygame.draw.polygon(surf, _KEYLINE, cone, kw)

    # Gold foil collar at the base.
    _draw_trim(surf, left_x, right_x, base_cy, r)

    # Curly ribbon streamers spiralling off the tip, above a small foil pom.
    _draw_pom(surf, tip_x, tip_y, r, head_w)
    _draw_streamers(surf, tip_x, tip_y, r, f, head_w)


def _draw_sheen(surf, tip_x, tip_y, left_x, right_x, base_y_line, r, f):
    mask_rect = pygame.Rect(int(left_x - 2), int(tip_y - 2),
                            int(right_x - left_x + 4),
                            int(base_y_line - tip_y + 4))
    if mask_rect.width <= 0 or mask_rect.height <= 0:
        return
    ox, oy = mask_rect.left, mask_rect.top
    layer = pygame.Surface(mask_rect.size, pygame.SRCALPHA)

    # Sheen runs from just inside the lit base edge up toward the tip; it
    # narrows as the cone narrows so it tracks the surface, not a flat stripe.
    lit_base = (right_x if f >= 0 else left_x) - f * (right_x - left_x) * 0.20
    bw = (right_x - left_x) * 0.16
    band = [
        (lit_base - bw - ox, base_y_line - oy),
        (lit_base + bw - ox, base_y_line - oy),
        (tip_x + f * r * 0.10 - ox, tip_y + r * 0.4 - oy),
        (tip_x - f * r * 0.02 - ox, tip_y + r * 0.4 - oy),
    ]
    pygame.draw.polygon(layer, _FOIL_HI + (150,), band)
    # A thin hot core inside the band reads as the brightest specular line.
    core = [
        (lit_base - bw * 0.35 - ox, base_y_line - oy),
        (lit_base + bw * 0.2 - ox, base_y_line - oy),
        (tip_x + f * r * 0.06 - ox, tip_y + r * 0.4 - oy),
    ]
    pygame.draw.polygon(layer, _FOIL_HI + (220,), core)

    mask = pygame.Surface(mask_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(tip_x - ox, tip_y - oy),
                         (left_x - ox, base_y_line - oy),
                         (right_x - ox, base_y_line - oy)])
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(layer, (ox, oy))


def _draw_confetti(surf, tip_x, tip_y, left_x, right_x, base_y_line, r, f):
    # Barycentric spots inside the cone triangle — deterministic so the dots
    # don't jitter frame to frame. (u toward base, v toward lit edge.)
    spots = ((0.55, 0.30), (0.72, 0.55), (0.40, 0.62), (0.82, 0.30),
             (0.62, 0.78), (0.50, 0.42), (0.86, 0.62), (0.34, 0.40))
    dot = max(1, int(r * 0.11))
    # The shade flank sits behind the dividing edge that runs from the tip to
    # cx - f*r*0.10 at the base; everything magenta-lit is on the other side.
    div_v = 0.5 - f * 0.10 / 2.0
    for u, v in spots:
        # Blend tip -> base-left -> base-right by (1-u, u*(1-v), u*v).
        bx = left_x + (right_x - left_x) * v
        x = tip_x + (bx - tip_x) * u
        y = tip_y + (base_y_line - tip_y) * u
        # Pick dot colour for contrast against the flank it lands on: cool
        # white/teal pop on the magenta lit flank; magenta on the indigo shade.
        on_shade = (v < div_v) if f >= 0 else (v > div_v)
        col = _MAGENTA if on_shade else (_WHITE if (int(u * 100) % 2) else _TEAL)
        pygame.draw.circle(surf, col, (int(x), int(y)), dot)
        if dot >= 2:  # tiny specular fleck makes each dot read as foil
            pygame.draw.circle(surf, _FOIL_HI,
                               (int(x - dot * 0.3), int(y - dot * 0.3)),
                               max(1, dot // 2))


def _draw_trim(surf, left_x, right_x, base_cy, r):
    # Taller, brighter gold collar so the party-hat triad (gold tip + gold
    # base + magenta cone) survives below the confetti gate.
    band_y = base_cy + r * 0.24
    band_h = max(3, int(r * 0.20) + 1)
    pygame.draw.rect(surf, _TRIM_LO,
                     (int(left_x), int(band_y), int(right_x - left_x), band_h))
    pygame.draw.rect(surf, _TRIM,
                     (int(left_x), int(band_y), int(right_x - left_x),
                      max(1, band_h - 1)))
    # Centred specular line so the collar reads symmetric, not skewed.
    inset = r * 0.18
    pygame.draw.line(surf, _FOIL_HI,
                     (int(left_x + inset), int(band_y + 1)),
                     (int(right_x - inset), int(band_y + 1)), 1)


def _draw_pom(surf, tip_x, tip_y, r, head_w):
    # The gold tip pom is the third leg of the recognizable triad, so below the
    # confetti gate it collapses to ONE clean gold disc (with keyline) that
    # still reads at 40px; above it, the foil-cluster look returns.
    pom_r = max(2, int(r * 0.22))
    if head_w < 22:
        pygame.draw.circle(surf, _KEYLINE, (int(tip_x), int(tip_y)),
                           pom_r + 1)
        pygame.draw.circle(surf, _GOLD, (int(tip_x), int(tip_y)), pom_r)
        pygame.draw.circle(surf, _FOIL_HI,
                           (int(tip_x - pom_r * 0.3), int(tip_y - pom_r * 0.3)),
                           max(1, int(pom_r * 0.4)))
        return
    offs = [(-0.5, 0.25, _GOLD), (0.5, 0.25, _TRIM_LO), (0.0, 0.5, _TRIM_LO),
            (-0.3, -0.15, _GOLD), (0.3, -0.15, _GOLD)]
    for dx, dy, col in offs:
        pygame.draw.circle(surf, col,
                           (int(tip_x + dx * pom_r), int(tip_y + dy * pom_r)),
                           max(1, int(pom_r * 0.6)))
    pygame.draw.circle(surf, _FOIL_HI,
                       (int(tip_x - pom_r * 0.2), int(tip_y - pom_r * 0.2)),
                       max(1, int(pom_r * 0.32)))


def _draw_streamers(surf, tip_x, tip_y, r, f, head_w):
    # Curly ribbon streamers springing off the tip. Each is a polyline whose
    # x oscillates with a decaying sine as y rises, reading as a tight spiral
    # corkscrew. Curl tightness + reach scale with r so they survive small.
    if head_w < 18:
        return
    lw = max(1, int(r * 0.13))
    n = 14
    # Two wider, lower-frequency ribbons so the curls read as ribbon, not as
    # aliased static at the tip.
    configs = (
        (_RIBBON[0], -0.55 * f, 1.20, 0.55, 3.2),
        (_RIBBON[1],  0.35 * f, 1.35, 0.42, 3.8),
    )
    for col, fan, reach, amp, freq in configs:
        pts = []
        for i in range(n + 1):
            t = i / n
            # Rise above the tip; lean in the fan direction as it climbs.
            y = tip_y - r * reach * t
            curl = math.sin(t * freq * math.pi) * (amp * r) * (1.0 - t * 0.35)
            x = tip_x + fan * r * t * 1.4 + curl
            pts.append((int(x), int(y)))
        if len(pts) >= 2:
            pygame.draw.lines(surf, col, False, pts, lw)
            # A lighter inner thread on thicker ribbons reads as ribbon gloss.
            if lw >= 2:
                hi = tuple(min(255, c + 60) for c in col)
                pygame.draw.lines(surf, hi, False, pts[: n // 2], 1)


build = make_build(draw_hat, seat={"hw": 26, "dx": -2, "dy": 17})
icon = make_icon(draw_hat)
