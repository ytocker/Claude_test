"""
CONSTELLATION store — TAB BAR element loop, hi-res SS=4 explorations.

The category tab strip: ONE committed active state (a filled gold-tinted PILL
with dark BOLD text — the Royal-Match pattern), inactive tabs clearly muted /
recessed, even spacing inside a defined track, and the `< >` overflow chevron
affordance (the real store scrolls SHOES/HATS/SHADES off-screen). Authored
resolution-independently and rendered at SS=4, one smoothscale down — the
shared crispness lever from THEME.md. Reuses the locked pipeline + primitives
from constellation_hi/render_hi.py (vgrad, bevel_rim, gloss_sweep, faux-bold
type, the multistop nebula bg + starfield) so the strip reads as the same
screen as every other element.

Three active-pill treatments are shown so the art-director can choose the
exact gold finish; the track / inactive / chevron language is shared across
all three. Both build targets safe: pure pygame, no numpy, no desktop/web-only
API.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
# render_hi.py lives two dirs up; reuse its pipeline + primitives wholesale so
# this element shares the EXACT materials/edges/type of the rest of the store.
_HI = os.path.abspath(os.path.join(_HERE, "..", "..", "constellation_hi"))
for p in (_ROOT, _HI):
    if p not in sys.path:
        sys.path.insert(0, p)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import render_hi as hi
from render_hi import (m, font, vgrad, bevel_rim, gloss_sweep, plain_text,
                        gradient_text, _glyph_base, _build_static_bg, draw_bg,
                        soft_glow, DW, DH, SS, GOLD, GOLD_PALE, GOLD_DEEP)
from game.draw import lerp_color, NEAR_BLACK


# Full category roster (store_catalog GROUPS), in store order. The first four
# are visible; SHOES/HATS/SHADES live off the right edge behind the chevron —
# exactly the overflow the real strip pages through.
ALL_TABS = ("PARROTS", "ANIMALS", "COSTUMES", "PARCELS", "SHOES", "HATS", "SHADES")
VISIBLE = 4                                # cells shown at once before overflow
ACTIVE = 1                                 # ANIMALS active in the previews

# Inactive / track / chevron language — SHARED by all three variants so only
# the active-pill finish differs between them.
TRACK_TOP = (10, 11, 28)                   # recessed dark track well
TRACK_BOT = (5, 6, 18)
INACTIVE_COL = (150, 152, 178)             # muted lilac-grey, clearly recessed
INACTIVE_KEY = (4, 5, 16)                  # tight dark keyline for crispness
CHEV_COL = (214, 196, 140)                 # warm gold chevron, reads tappable


def _track(surf, rect, rad):
    """The recessed dark tab track: a sunken gradient well with a dark outer
    keyline UNDER a faint gold inner hairline — the DEFINED EDGE per THEME so
    the whole strip is a delineated object, not floating chips on the sky."""
    surf.blit(vgrad(rect.w, rect.h, rad, TRACK_TOP, TRACK_BOT, 235), rect.topleft)
    # inner top shadow so the well reads sunken (light from top-left => the top
    # inner edge is the one in shade for a recess).
    ao = pygame.Surface(rect.size, pygame.SRCALPHA)
    ah = int(rect.h * 0.5)
    for y in range(ah):
        a = int(120 * (1 - y / ah) ** 1.5)
        pygame.draw.line(ao, (0, 0, 0, a), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=rad)
    ao.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(ao, rect.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 210), rect, width=max(1, m(1.6)),
                     border_radius=rad)
    pygame.draw.rect(surf, (*GOLD, 70), rect.inflate(-m(1.6), -m(1.6)),
                     width=max(1, m(1)), border_radius=max(1, rad - m(1)))


def _chevron(surf, cx, cy, s, facing, lit):
    """A `< >` overflow affordance: a chunky beveled gold chevron in a faintly
    recessed round nub so it reads as a tappable control. `lit` chevrons (more
    content that way) are bright; the dead-end side is dimmed."""
    nub_r = int(s * 0.95)
    # round nub well
    well = pygame.Surface((nub_r * 2 + m(4), nub_r * 2 + m(4)), pygame.SRCALPHA)
    c = nub_r + m(2)
    for i in range(nub_r, 0, -1):
        col = lerp_color((22, 23, 46), (8, 9, 24), i / nub_r)
        pygame.draw.circle(well, (*col, 235), (c, c), i)
    surf.blit(well, (cx - c, cy - c))
    pygame.draw.circle(surf, (0, 0, 0, 200), (cx, cy), nub_r, max(1, m(1.3)))
    pygame.draw.circle(surf, (*GOLD, 90 if lit else 40),
                       (cx, cy), nub_r - m(1), max(1, m(0.9)))
    col = CHEV_COL if lit else (96, 96, 116)
    dk = (54, 32, 6) if lit else (10, 11, 24)
    dx = -1 if facing == "left" else 1
    a = (cx - dx * int(s * 0.30), cy - int(s * 0.46))
    b = (cx + dx * int(s * 0.34), cy)
    cc = (cx - dx * int(s * 0.30), cy + int(s * 0.46))
    wkey = max(1, m(3.4))
    # dark keyline pass (under), then the bright stroke (over) => beveled edge
    for (p0, p1) in ((a, b), (b, cc)):
        pygame.draw.line(surf, dk, p0, p1, wkey + max(1, m(1)))
    for (p0, p1) in ((a, b), (b, cc)):
        pygame.draw.line(surf, col, p0, p1, wkey)
    if lit:
        # a fine top-left specular kiss on the upper limb
        pygame.draw.line(surf, (255, 246, 214),
                         (a[0], a[1] + m(0.6)), (b[0], b[1] + m(0.6)),
                         max(1, m(1.1)))


def _inactive_tab(surf, cxx, cy, label, f):
    """A muted, recessed inactive tab: dark-keyed lilac-grey type, no fill, so
    it sits clearly below the active pill plane."""
    plain_text(surf, label, f, (cxx, cy), INACTIVE_COL, shadow_a=120,
               weight=m(0.55), keyline=INACTIVE_KEY, kw=m(0.7))


# ── three active-pill finishes (only the fill/finish differs) ────────────────
def _pill_classic(surf, pill, rad, label, f):
    """Variant A — RICH WARM GOLD. The price-chip gold from the locked spec:
    a single bright-crown -> deep-amber ramp, one gloss sweep, a dark contact
    keyline under a bright top-left bevel. Dark-brown bold text. The safest,
    most cohesive read against the rest of the gold store furniture."""
    surf.blit(vgrad(pill.w, pill.h, rad, (255, 210, 100), (196, 130, 32),
                    255, gamma=1.08), pill.topleft)
    gloss_sweep(surf, pill, rad, peak=120)
    pygame.draw.rect(surf, (90, 54, 12), pill, width=max(1, m(1.5)),
                     border_radius=rad)
    bevel_rim(surf, pill, rad, (90, 54, 12), (*GOLD_PALE, 235), w=max(1, m(1.3)))
    plain_text(surf, label, f, pill.center, (54, 30, 6), shadow_a=0,
               weight=m(0.95))


def _pill_champagne(surf, pill, rad, label, f):
    """Variant B — CHAMPAGNE CROWN. A brighter, more 'candy-premium' pill: a
    pale champagne band over the top ~46% atop the same amber base, a wider
    bright bevel, a tiny gold under-glow so the active cell lifts off the track.
    Same dark text + edge family; reads a touch more festive/Royal-Match."""
    surf.blit(vgrad(pill.w, pill.h, rad, (255, 240, 190), (224, 152, 34),
                    255, gamma=1.1), pill.topleft)
    crown_h = int(pill.h * 0.46)
    crown = pygame.Surface((pill.w, crown_h), pygame.SRCALPHA)
    for yy in range(crown_h):
        a = int(160 * (1 - yy / crown_h) ** 1.2)
        pygame.draw.line(crown, (255, 251, 228, a), (0, yy), (pill.w, yy))
    cm = pygame.Surface((pill.w, crown_h), pygame.SRCALPHA)
    pygame.draw.rect(cm, (255, 255, 255, 255), (0, 0, pill.w, pill.h),
                     border_radius=rad)
    crown.blit(cm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(crown, pill.topleft)
    gloss_sweep(surf, pill, rad, peak=90)
    pygame.draw.rect(surf, (112, 68, 12), pill, width=max(1, m(1.6)),
                     border_radius=rad)
    bevel_rim(surf, pill, rad, (112, 68, 12), (255, 252, 226, 240),
              w=max(1, m(1.5)))
    plain_text(surf, label, f, pill.center, (84, 44, 6), shadow_a=0,
               weight=m(0.95))


def _pill_jewel(surf, pill, rad, label, f):
    """Variant C — RAISED JEWEL PILL. The most tactile: a soft drop shadow so
    the pill physically lifts out of the recessed track, the rich gold body,
    plus a thin double gold rim (dark contact keyline + bright inner hairline)
    echoing the balance capsule / coin rim language. Dark-brown bold text with
    a faint warm under-shadow. The 'this button is pressed up at you' read."""
    # drop shadow into the track so the pill sits on a higher plane
    for k, a in ((m(4), 60), (m(2.5), 90), (m(1), 120)):
        sh = pygame.Surface((pill.w + k * 2, pill.h + k * 2), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, a), sh.get_rect(),
                         border_radius=rad + k)
        surf.blit(sh, (pill.x - k, pill.y - k + m(2)))
    surf.blit(vgrad(pill.w, pill.h, rad, (255, 214, 104), (188, 122, 28),
                    255, gamma=1.06), pill.topleft)
    gloss_sweep(surf, pill, rad, peak=135)
    # double gold rim echoing the coin/capsule: dark contact + bright inner.
    pygame.draw.rect(surf, (74, 44, 8), pill, width=max(1, m(1.8)),
                     border_radius=rad)
    inner = pill.inflate(-m(2.6), -m(2.6))
    pygame.draw.rect(surf, (255, 240, 188, 230), inner, width=max(1, m(1.0)),
                     border_radius=max(1, rad - m(1)))
    bevel_rim(surf, pill, rad, (74, 44, 8), (*GOLD_PALE, 235), w=max(1, m(1.2)))
    plain_text(surf, label, f, (pill.centerx, pill.centery + m(0.5)),
               (50, 28, 4), shadow_a=0, weight=m(1.0))


PILL_FNS = (_pill_classic, _pill_champagne, _pill_jewel)
PILL_NAMES = ("A · RICH WARM GOLD", "B · CHAMPAGNE CROWN", "C · RAISED JEWEL")


def _lane_scrim(surf, cx, y, w, h):
    """A soft dark scrim band behind a strip lane so the pills read against a
    controlled ground (the central nebula bloom is bright by design). Mirrors
    the header's legibility band in render_hi — same screen DNA, not a new look."""
    # author the radial-ish falloff at low res, then smoothscale up so the
    # ends + top/bottom feather smoothly with no hard edge and no slow per-px
    # loop over the SS-width surface.
    lw, lh = 64, 32
    small = pygame.Surface((lw, lh), pygame.SRCALPHA)
    for yy in range(lh):
        dy = abs(yy - lh / 2) / (lh / 2)
        for xx in range(lw):
            dx = abs(xx - lw / 2) / (lw / 2)
            a = int(205 * (1 - dy ** 1.7) * (1 - dx ** 3.0))
            if a > 0:
                small.set_at((xx, yy), (7, 8, 24, a))
    band = pygame.transform.smoothscale(small, (int(w), int(h)))
    surf.blit(band, (int(cx - w / 2), int(y - h / 2)))


def tab_strip(surf, cx, y, w, pill_fn, scrolled=True):
    """Draw one full tab strip centred at (cx, y) with width `w`. `pill_fn`
    paints the active cell's finish. With `scrolled` True the left chevron is
    lit (PARROTS pages back into view) AND the right chevron is lit (SHOES/HATS/
    SHADES wait off the right edge) — the overflow affordance on both ends."""
    th = m(38)
    track = pygame.Rect(int(cx - w / 2), int(y - th / 2), int(w), th)
    rad = th // 2
    # chevron nubs sit just OUTSIDE the track so no tab hugs the edge.
    chev_s = int(th * 0.42)
    chev_gap = m(4)
    cl_x = track.x - chev_gap - int(chev_s * 0.95)
    cr_x = track.right + chev_gap + int(chev_s * 0.95)

    _lane_scrim(surf, cx, y, w + m(70), th + m(34))
    _track(surf, track, rad)

    # equal-width cells with a symmetric inner margin so spacing is even end to
    # end and PARCELS never hugs the right edge.
    edge = m(8)
    cell_w = (track.w - 2 * edge) / VISIBLE
    f = font(13)
    for i in range(VISIBLE):
        label = ALL_TABS[i]
        cxx = int(track.x + edge + cell_w * (i + 0.5))
        if i == ACTIVE:
            pw = int(cell_w) - m(6)
            ph = th - m(10)
            pill = pygame.Rect(cxx - pw // 2, track.centery - ph // 2, pw, ph)
            pill_fn(surf, pill, ph // 2, label, f)
        else:
            _inactive_tab(surf, cxx, track.centery, label, f)

    _chevron(surf, cl_x, track.centery, chev_s, "left", lit=scrolled)
    _chevron(surf, cr_x, track.centery, chev_s, "right", lit=True)


# ── sheet composition ─────────────────────────────────────────────────────────
def _label(surf, txt, cx, y, size=11):
    gradient_text(surf, txt, font(size), (cx, y), (255, 248, 214), (236, 176, 70),
                  weight=m(0.6), keyline=(70, 40, 8), kw=m(0.9), shadow=True)


def main():
    _build_static_bg()
    surf = pygame.Surface((DW, DH))
    draw_bg(surf)

    _label(surf, "CONSTELLATION  STORE  —  CATEGORY  TAB  BAR", DW // 2, m(26), 13)
    _label(surf, "active: ANIMALS  ·  3 active-pill treatments  ·  < > overflow",
           DW // 2, m(50), 9)

    strip_w = DW - m(2 * 30)                       # leaves room for chevron nubs
    ys = (m(150), m(300), m(450))
    for (yc, fn, nm) in zip(ys, PILL_FNS, PILL_NAMES):
        _label(surf, nm, DW // 2, yc - m(40), 10)
        tab_strip(surf, DW // 2, yc, strip_w, fn)

    # a head-to-head row at small (true store) size so the AD can judge crispness
    # at the actual on-screen scale, not just the blown-up previews.
    _label(surf, "AT TRUE STORE SCALE (the size it ships at)", DW // 2, m(560), 10)
    small_w = DW - m(2 * 16)
    sy = m(600)
    th = m(20)
    track = pygame.Rect(int(DW // 2 - small_w / 2), int(sy - th / 2),
                        int(small_w), th)
    rad = th // 2
    _lane_scrim(surf, DW // 2, sy, small_w + m(60), th + m(24))
    _track(surf, track, rad)
    edge = m(5)
    cell_w = (track.w - 2 * edge) / VISIBLE
    f = font(8)
    for i in range(VISIBLE):
        label = ALL_TABS[i]
        cxx = int(track.x + edge + cell_w * (i + 0.5))
        if i == ACTIVE:
            pw = int(cell_w) - m(4)
            ph = th - m(6)
            pill = pygame.Rect(cxx - pw // 2, track.centery - ph // 2, pw, ph)
            _pill_classic(surf, pill, ph // 2, label, f)
        else:
            _inactive_tab(surf, cxx, track.centery, label, f)
    cs = int(th * 0.42)
    _chevron(surf, track.x - m(4) - int(cs * 0.95), track.centery, cs, "left", True)
    _chevron(surf, track.right + m(4) + int(cs * 0.95), track.centery, cs, "right", True)

    out = pygame.transform.smoothscale(surf, (hi.W, hi.H))
    dst = os.path.join(_HERE, "round_1.png")
    pygame.image.save(out, dst)
    print("saved", dst)


if __name__ == "__main__":
    main()
