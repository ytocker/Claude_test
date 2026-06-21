"""BALLOON BASKET parcel cosmetic (MID tier).

A tiny hot-air balloon: a fat candy-GORED TEARDROP envelope above a small
square wicker BASKET, joined by two short suspension cords. At 22px the
read is the "balloon over a box" outline — a round-shouldered envelope that
tapers to a pinched throat, with a little box hanging clear below.

The envelope carries the glyph. It is built as a TEARDROP, not an ellipse:
the upper two-thirds are round and full, but the lower third is pinched
inward toward a narrow throat, so the silhouette tapers down to the basket
the way a real inflated envelope does. A pure circle reads as a striped
beach-ball/ornament — the taper is the single tell that sells "balloon" at
22px.

Stripes are baked as GORES — vertical fabric panels that converge to a
crown point at the apex rather than even barber-stripes — so the canopy
reads as an envelope sewn from panels, not a banded sphere. Few wide gores
keep the candy tell alive at 22px and when inverted across the −25°→90°
tilt arc.

The canopy is TEAL/azure + cream, NOT red: carried below Pip the parcel
sits against his red body, and a red dome merged into him into a bauble.
Cool teal stripes snap off the warm red bird instantly while still reading
"candy". The whole prop is dropped + nudged forward of Pip so a full
basket row and the suspension gap stay visible — the basket is the
disambiguator; if it hides, the glyph collapses to an ornament.
"""
import math

import pygame

from game.parrot import _lerp_color


# Day palette per brief. Cool TEAL/azure canopy to break off Pip's red body.
STRIPE_TEAL = (38, 168, 174)      # #26A8AE candy teal band
STRIPE_TEAL_HI = (96, 214, 214)   # lit teal on the dome crown
STRIPE_TEAL_LO = (24, 124, 134)   # shaded teal toward the throat
CREAM = (243, 236, 220)           # #F3ECDC cream band
CREAM_HI = (252, 248, 240)        # cream crown highlight
CREAM_LO = (210, 200, 180)        # shaded cream toward the throat
BASKET = (154, 112, 56)           # #9A7038 wicker basket
BASKET_HI = (190, 146, 84)        # lit basket top edge
BASKET_LO = (120, 86, 42)         # shaded basket belly
WEAVE = (96, 68, 34)              # darker weave hatch on the basket
OUTLINE = (24, 40, 44)            # dark teal-leaning keyline for the bright sky
CORD = (60, 40, 22)               # rigging cord (dark so it survives day sky)
WARM_EDGE = (250, 222, 150)       # warm catch on the dome bottom (holds on night sky)


def _teardrop_halfwidth(t, max_rx):
    # Per-row half-width of the envelope as a function of vertical position
    # t in [0,1] (0 = apex, 1 = throat). Classic onion/teardrop: a ROUNDED
    # crown (not a wide flat shoulder — that reads as a parasol), the widest
    # belly around the upper-middle, then a taper that pinches inward to a
    # narrow throat above the basket. The full round belly is what reads
    # "balloon"; the pinched throat is what stops it reading "sphere".
    belly = 0.46                            # vertical position of the widest row
    if t <= belly:
        # Rounded crown → belly: a circular arc so the top curves over
        # smoothly instead of flaring to a flat shoulder.
        u = t / belly                       # 0 at apex → 1 at the belly
        return max_rx * math.sqrt(max(0.0, 1.0 - (1.0 - u) ** 2))
    # Belly → throat: ease full width back down to a small throat. A gentle
    # exponent keeps the lower body rounded so it pinches, not folds.
    v = (t - belly) / (1.0 - belly)         # 0 at belly → 1 at throat
    throat = 0.34                           # throat half-width as a fraction
    return max_rx * (1.0 - (1.0 - throat) * (v ** 1.5))


def build(mode: str = "normal") -> pygame.Surface:
    # mode is ignored — the balloon keeps its festive look across power-ups.
    SIZE = 44
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    cx = SIZE // 2

    # Vertical stack. The whole prop is dropped ~2px and nudged ~1px forward
    # (+x, away from Pip's body) so a full basket row and the suspension gap
    # clear Pip's belly when carried — the basket has to stay visible.
    FWD = 1
    env_cx = cx + FWD
    apex_y = 5                      # envelope crown (top)
    throat_y = 33                   # bottom of the envelope, the pinched mouth
    env_h = throat_y - apex_y
    max_rx = 18                     # widest half-width at the shoulder
    basket_w, basket_h = 14, 12
    basket_top = 40                 # dropped so the suspension gap is visible
    basket_rect = pygame.Rect(env_cx - basket_w // 2, basket_top,
                              basket_w, basket_h)

    # Drop shadow grounds the whole balloon under Pip.
    sh = pygame.Surface((24, 7), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 14, 120), sh.get_rect())
    surf.blit(sh, (env_cx - 12, basket_rect.bottom - 2))

    # SUSPENSION cords first so the basket rim and envelope throat overlap
    # their ends — the cords read as tucked into both. Anchored at the throat
    # (not the wide shoulder) so they stay tucked UNDER the canopy through the
    # full tilt sweep instead of detaching to the side.
    cord_top_y = throat_y - 2
    for sx, bx in ((-4, -basket_w // 2 + 2), (4, basket_w // 2 - 2)):
        pygame.draw.line(surf, CORD, (env_cx + sx, cord_top_y),
                         (env_cx + bx, basket_top + 1), 2)

    # ── ENVELOPE (teardrop) ──────────────────────────────────────────────
    # Build the silhouette as a per-row half-width profile, then fill each
    # row with the GORE colour for its column so stripes converge to the
    # crown. A dark keyline is laid one px outside the profile so the round
    # teardrop pops against the bright day sky and holds when banked.

    # Pre-compute the profile so outline + fill share one taper.
    profile = []                                # (y, halfwidth)
    for y in range(apex_y, throat_y + 1):
        t = (y - apex_y) / env_h
        profile.append((y, _teardrop_halfwidth(t, max_rx)))

    # Keyline: a slightly fatter teardrop drawn behind the fill.
    out_pts_l, out_pts_r = [], []
    for y, hw in profile:
        out_pts_l.append((env_cx - hw - 1.5, y))
        out_pts_r.append((env_cx + hw + 1.5, y))
    pygame.draw.polygon(surf, OUTLINE, out_pts_l + out_pts_r[::-1])

    # GORE fill. Each gore is a fabric panel that is full width at the
    # shoulder and pinches to the crown point — so its colour is assigned by
    # the ANGLE from the apex, not by a fixed vertical band. That makes the
    # stripes fan out from the crown and converge there (envelope read),
    # instead of even vertical barber-stripes (beach-ball read).
    n_gores = 6                                  # few bold panels survive 22px
    for y, hw in profile:
        if hw <= 0:
            continue
        t = (y - apex_y) / env_h
        for x in range(int(env_cx - hw), int(env_cx + hw) + 1):
            # Gore index from the pixel's position ACROSS the local row width
            # (-1..+1), so panels run vertically through the belly and read as
            # sewn fabric, not a radial parasol fan. The boundaries still pull
            # together toward the crown because every row is narrower there —
            # so the gores converge to the apex without flaring outward.
            f = (x - env_cx) / hw                 # -1 left rim .. +1 right rim
            g = (f + 1.0) * 0.5 * n_gores
            is_teal = (int(g) % 2 == 0)
            top = STRIPE_TEAL_HI if is_teal else CREAM_HI
            bot = STRIPE_TEAL_LO if is_teal else CREAM_LO
            col = _lerp_color(top, bot, t)
            surf.set_at((x, y), col + (255,))

    # Crown sheen — a bright cream catch on the upper-left sells the round,
    # inflated shoulder.
    pygame.draw.ellipse(surf, (255, 252, 246, 150),
                        pygame.Rect(env_cx - 10, apex_y + 4, 8, 7))

    # Warm bottom catch — a thin warm arc hugging the lower shoulder keeps the
    # cool canopy from sinking into the dark night sky (value rescue on teal).
    pygame.draw.arc(surf, WARM_EDGE,
                    pygame.Rect(env_cx - max_rx + 3, apex_y + 8,
                                (max_rx - 3) * 2, env_h),
                    3.66, 5.76, 2)

    # Throat — the pinched mouth where the gores gather above the cords. A
    # short cream band with a dark underline reads as the open envelope mouth.
    pygame.draw.ellipse(surf, OUTLINE,
                        pygame.Rect(env_cx - 7, throat_y - 3, 14, 6))
    pygame.draw.ellipse(surf, CREAM,
                        pygame.Rect(env_cx - 5, throat_y - 2, 10, 4))

    # ── BASKET ───────────────────────────────────────────────────────────
    # Outline frame behind a gradient wicker fill — a compact rounded square.
    b_out = basket_rect.inflate(4, 4)
    pygame.draw.rect(surf, OUTLINE, b_out, border_radius=3)
    fill = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    for yy in range(basket_rect.top, basket_rect.bottom):
        t = (yy - basket_rect.top) / max(1, basket_rect.height - 1)
        col = _lerp_color(BASKET_HI, BASKET_LO, t) + (255,)
        fill.fill(col, pygame.Rect(0, yy, SIZE, 1))
    bmask = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    pygame.draw.rect(bmask, (255, 255, 255, 255), basket_rect, border_radius=2)
    fill.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(fill, (0, 0))

    # Weave suggestion — a bound rim band plus a couple of course lines. Fine
    # wicker dies at 22px, so bold hatches carry the basket texture.
    pygame.draw.line(surf, BASKET_HI, (basket_rect.left + 1, basket_rect.top + 1),
                     (basket_rect.right - 2, basket_rect.top + 1), 1)
    pygame.draw.line(surf, WEAVE, (basket_rect.left + 1, basket_rect.top + 4),
                     (basket_rect.right - 2, basket_rect.top + 4), 1)
    pygame.draw.line(surf, WEAVE, (basket_rect.left + 1, basket_rect.top + 7),
                     (basket_rect.right - 2, basket_rect.top + 7), 1)
    for vx in range(basket_rect.left + 2, basket_rect.right - 1, 4):
        pygame.draw.line(surf, WEAVE, (vx, basket_rect.top + 2),
                         (vx, basket_rect.bottom - 2), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
