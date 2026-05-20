"""Render 5 RAIL pickup-icon design candidates — OLD-SCHOOL
classic train tickets. User feedback on the first ticket
batch: "looks too much like the lottery card." This pass
deliberately avoids the polish vocabulary that made the first
batch read as casino-cards:

  * NO vertical gradients on the body (flat paper colour only)
  * NO cream highlight passes on text (single black/dark fill)
  * NO sparkle stars
  * NO drop shadows
  * NO gold / teal / chrome accents — only cream paper / faded
    red / sepia / black
  * Steam-locomotive silhouettes (NOT the modern minecart) —
    period-appropriate for the ticket aesthetic
  * Decorative engraving borders, hole-punches, rubber-stamp
    marks — the visual signifiers of actual paper tickets

Native 64×48, 6× supersample, smoothscale-down.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_rail_oldschool_ticket_variants.py
"""

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))

from tools.render_lottery_scratch_variants import (
    _ss_paint, _font,
)
from tools.render_helmet_side_view_variants import (
    build_world, render_play_scene, _label_band,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "rail_oldschool_ticket_variants")
os.makedirs(_OUT, exist_ok=True)


# ── old-paper palette (deliberately muted) ──────────────────────────────────
CREAM      = (238, 225, 195)
CREAM_DK   = (215, 200, 165)
SEPIA      = (228, 210, 170)
TAN        = (240, 220, 175)
PARCH      = (245, 232, 200)
INK        = ( 30,  25,  20)
INK_LITE   = ( 80,  65,  55)
RED_FADE   = (175,  60,  60)
RED_DK     = (130,  35,  35)
NEAR_BLACK = ( 18,  14,  10)


NATIVE_W = 64
NATIVE_H = 48


# ── shared shape helpers ────────────────────────────────────────────────────

def _flat_body(big, rect, fill, border_col=INK, border_w=1):
    """Flat-coloured ticket body with a single-line border. NO
    gradient — this is the antithesis of the lottery card body."""
    pygame.draw.rect(big, fill, rect)
    pygame.draw.rect(big, border_col, rect, border_w)


def _double_border(big, rect, col, outer_w, inner_w, gap):
    """Double-line border, outer thick + inner thin, with a `gap`
    pixel space between. Classic engraving look."""
    pygame.draw.rect(big, col, rect, outer_w)
    inner = rect.inflate(-2 * gap, -2 * gap)
    pygame.draw.rect(big, col, inner, inner_w)


def _corner_flourish(big, SS, cx, cy, col=INK, scale=1.0):
    """Small filigree dot-pattern at a corner: 3 dots forming a
    small triangle pip."""
    s = max(1, int(SS * 0.5 * scale))
    pygame.draw.circle(big, col, (cx, cy), s)
    pygame.draw.circle(big, col, (cx + int(SS * 1.6 * scale), cy), max(1, s - 1))
    pygame.draw.circle(big, col, (cx, cy + int(SS * 1.6 * scale)), max(1, s - 1))


def _punch_hole(big, SS, cx, cy, r):
    """Conductor's punch — a small ring with the inner cleared to
    transparent. Approximated by painting the ring and clipping a
    hole through the alpha."""
    pygame.draw.circle(big, NEAR_BLACK, (cx, cy), r + max(1, SS // 3))
    pygame.draw.circle(big, (0, 0, 0, 0), (cx, cy),
                       max(1, r - SS // 4))


def _rubber_stamp(big, SS, cx, cy, r, text, rot_deg=-12):
    """Faded rubber-stamp circle with text inside, rotated for that
    'hand-stamped' look."""
    sub = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    sc = sub.get_rect().center
    pygame.draw.circle(sub, (190, 60, 60, 180), sc, r,
                       max(1, int(SS * 0.6)))
    pygame.draw.circle(sub, (190, 60, 60, 180), sc, int(r * 0.7),
                       max(1, int(SS * 0.4)))
    f = _font(int(r * 0.85))
    t = f.render(text, True, (170, 50, 50, 220))
    sub.blit(t, t.get_rect(center=sc))
    rotated = pygame.transform.rotate(sub, rot_deg)
    big.blit(rotated, rotated.get_rect(center=(cx, cy)))


def _locomotive(big, SS, cx, cy, scale=1.0, colour=INK,
                window_col=CREAM):
    """Detailed classic steam-locomotive silhouette anchored at its
    centre. Period-appropriate for an old-school train ticket.
    Components, drawn back-to-front:

      * cab (left tall block) with overhanging roof + window
      * boiler (right horizontal cylinder) with 2 lighter iron
        hoop bands
      * smokestack with flared cap
      * steam dome between cab and stack
      * sand dome between dome and stack (smaller)
      * headlight (lamp) on the front of the boiler
      * cowcatcher (slanted pilot) at the front-bottom
      * 2 large spoked driving wheels + 1 small leading wheel,
        connected by a coupling rod
      * 4 stacked smoke puffs above the stack

    All sizes scale with `scale` so the same recipe fits every
    ticket layout."""
    # Base footprint at scale=1.0 is 28 SS × 14 SS — already much
    # bigger than the earlier 14 SS × 6.5 SS silhouette.
    w = int(SS * 28 * scale)
    h = int(SS * 14 * scale)

    # ── Boiler (rounded horizontal cylinder on the right) ──
    boiler_w = int(w * 0.66)
    boiler_h = int(h * 0.50)
    boiler = pygame.Rect(0, 0, boiler_w, boiler_h)
    boiler.midright = (cx + w // 2, cy + int(SS * 0.5 * scale))
    pygame.draw.rect(big, colour, boiler,
                     border_radius=max(1, int(SS * 0.8 * scale)))
    # 2 iron-hoop bands across the boiler (light strokes).
    for band_t in (0.30, 0.65):
        bx = boiler.left + int(boiler.width * band_t)
        pygame.draw.line(big, window_col,
                         (bx, boiler.top + max(1, SS // 3)),
                         (bx, boiler.bottom - max(1, SS // 3)),
                         max(1, int(SS * 0.4 * scale)))

    # ── Cab (taller block on the left) ──
    cab_w = int(w * 0.30)
    cab_h = int(h * 0.85)
    cab = pygame.Rect(0, 0, cab_w, cab_h)
    cab.midleft = (cx - w // 2, cy + int(SS * 1 * scale))
    pygame.draw.rect(big, colour, cab,
                     border_radius=max(1, int(SS * 0.7 * scale)))
    # Cab roof overhang.
    roof_w = int(cab_w * 1.20)
    roof_h = max(2, int(SS * 0.9 * scale))
    roof = pygame.Rect(0, 0, roof_w, roof_h)
    roof.midbottom = (cab.centerx + max(1, int(SS * 0.4 * scale)),
                       cab.top + roof_h)
    pygame.draw.rect(big, colour, roof)
    # Window — lighter rectangle inside the cab.
    win = pygame.Rect(0, 0, int(cab_w * 0.55), int(cab_h * 0.32))
    win.center = (cab.centerx, cab.top + int(cab_h * 0.32))
    pygame.draw.rect(big, window_col, win)
    pygame.draw.rect(big, colour, win, max(1, SS // 3))

    # ── Smokestack with flared cap ──
    stack_w = max(2, int(SS * 2.0 * scale))
    stack_h = max(3, int(SS * 4.5 * scale))
    stack_x = boiler.right - int(SS * 5 * scale) - stack_w // 2
    stack_rect = pygame.Rect(stack_x, boiler.top - stack_h,
                              stack_w, stack_h)
    pygame.draw.rect(big, colour, stack_rect)
    flare_w = int(stack_w * 1.9)
    flare_h = max(1, int(SS * 0.9 * scale))
    flare = pygame.Rect(0, 0, flare_w, flare_h)
    flare.midbottom = (stack_rect.centerx, stack_rect.top)
    pygame.draw.rect(big, colour, flare)

    # ── Steam dome (between cab and stack) ──
    dome_w = max(3, int(SS * 2.4 * scale))
    dome_h = max(2, int(SS * 1.8 * scale))
    dome_cx = boiler.left + int(boiler.width * 0.32)
    dome_rect = pygame.Rect(0, 0, dome_w, dome_h * 2)
    dome_rect.midbottom = (dome_cx, boiler.top + max(1, SS // 3))
    pygame.draw.ellipse(big, colour, dome_rect)
    # Iron cap on the steam dome.
    cap = pygame.Rect(0, 0, int(dome_w * 1.4),
                       max(1, int(SS * 0.5 * scale)))
    cap.midbottom = (dome_cx, dome_rect.midbottom[1] - dome_h)
    pygame.draw.rect(big, colour, cap)

    # ── Sand dome (smaller, between steam dome and stack) ──
    sand_w = max(2, int(SS * 1.8 * scale))
    sand_h = max(2, int(SS * 1.4 * scale))
    sand_cx = boiler.left + int(boiler.width * 0.52)
    sand_rect = pygame.Rect(0, 0, sand_w, sand_h * 2)
    sand_rect.midbottom = (sand_cx, boiler.top + max(1, SS // 3))
    pygame.draw.ellipse(big, colour, sand_rect)

    # ── Headlight on the front of the boiler ──
    hl_r = max(2, int(SS * 1.3 * scale))
    hl_cx = boiler.right - hl_r - int(SS * 0.5 * scale)
    hl_cy = boiler.top + int(boiler.height * 0.42)
    pygame.draw.circle(big, colour, (hl_cx, hl_cy),
                       hl_r + max(1, SS // 3))
    pygame.draw.circle(big, window_col, (hl_cx, hl_cy),
                       max(1, int(hl_r * 0.65)))

    # ── Cowcatcher / pilot at the front-bottom ──
    cow_pts = [
        (boiler.right - int(SS * 1 * scale),
         boiler.bottom - max(1, SS // 3)),
        (boiler.right + int(SS * 3.5 * scale),
         boiler.bottom + int(SS * 1.5 * scale)),
        (boiler.right + int(SS * 3.5 * scale),
         boiler.bottom + int(SS * 3.5 * scale)),
        (boiler.right - int(SS * 1 * scale),
         boiler.bottom + int(SS * 3 * scale)),
    ]
    pygame.draw.polygon(big, colour, cow_pts)
    # 3 vertical vanes hinting at the pilot grille.
    for f in (0.30, 0.55, 0.80):
        vx = cow_pts[0][0] + int((cow_pts[1][0] - cow_pts[0][0]) * f)
        v_top = boiler.bottom + int(SS * 1 * scale * f)
        v_bot = boiler.bottom + int(SS * 3 * scale)
        pygame.draw.line(big, window_col, (vx, v_top), (vx, v_bot),
                         max(1, SS // 3))

    # ── Driving wheels (2 big, spoked) + leading wheel (1 small) ──
    big_wheel_r = max(3, int(SS * 2.5 * scale))
    small_wheel_r = max(2, int(SS * 1.5 * scale))
    wheel_y = boiler.bottom + big_wheel_r - int(SS * 0.5 * scale)
    drive_xs = (
        cab.right + int(SS * 1 * scale) + big_wheel_r // 2,
        boiler.left + int(boiler.width * 0.55),
    )
    for wx in drive_xs:
        pygame.draw.circle(big, colour, (wx, wheel_y),
                           big_wheel_r)
        # 6 spokes.
        for ang_deg in (0, 60, 120, 180, 240, 300):
            ang = math.radians(ang_deg)
            x2 = wx + math.cos(ang) * (big_wheel_r - SS // 2)
            y2 = wheel_y + math.sin(ang) * (big_wheel_r - SS // 2)
            pygame.draw.line(big, window_col, (wx, wheel_y),
                             (int(x2), int(y2)),
                             max(1, int(SS * 0.45 * scale)))
        # Hub centre.
        pygame.draw.circle(big, window_col, (wx, wheel_y),
                           max(1, int(SS * 0.7 * scale)))
        # Inner tyre edge.
        pygame.draw.circle(big, colour, (wx, wheel_y),
                           big_wheel_r,
                           max(1, int(SS * 0.35 * scale)))
    # Leading wheel (front).
    lead_wx = boiler.right - int(SS * 0.5 * scale)
    lead_wy = boiler.bottom + small_wheel_r + int(SS * 1 * scale)
    pygame.draw.circle(big, colour, (lead_wx, lead_wy),
                       small_wheel_r)
    pygame.draw.circle(big, window_col, (lead_wx, lead_wy),
                       max(1, int(SS * 0.45 * scale)))

    # ── Coupling rod connecting the driving wheels ──
    rod_h = max(2, int(SS * 0.6 * scale))
    rod_left = drive_xs[0]
    rod_right = drive_xs[1]
    rod_y = wheel_y - int(big_wheel_r * 0.20) - rod_h // 2
    pygame.draw.rect(big, colour,
                     (rod_left, rod_y,
                      rod_right - rod_left, rod_h))
    # Crank pins.
    for wx in drive_xs:
        pygame.draw.circle(big, window_col,
                           (wx, rod_y + rod_h // 2),
                           max(1, int(SS * 0.5 * scale)))

    # ── Smoke puffs above the stack ──
    smoke_x = stack_rect.centerx
    smoke_y = stack_rect.top - int(SS * 1.5 * scale)
    for dx, dy, sr in (
        (0,                       0,                       int(SS * 1.7 * scale)),
        (int(SS * -1.6 * scale),  int(SS * -2.8 * scale),  int(SS * 2.0 * scale)),
        (int(SS *  1.8 * scale),  int(SS * -5.0 * scale),  int(SS * 1.8 * scale)),
        (int(SS *  0.4 * scale),  int(SS * -7.5 * scale),  int(SS * 1.4 * scale)),
    ):
        pygame.draw.circle(big, colour,
                            (smoke_x + dx, smoke_y + dy),
                            max(1, sr))


# ── 5 old-school ticket variants ────────────────────────────────────────────

def draw_o1_br_edmondson(surf, cx, cy, pulse):
    """O1 — BR-style Edmondson cardstock, 1960s. Flat cream paper,
    single black border, big serif "RAIL" + "TICKET" stacked, red
    diagonal stripe top-left, single punch hole upper-right,
    locomotive silhouette at the bottom."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
        _flat_body(big, card, CREAM,
                   border_col=NEAR_BLACK, border_w=max(1, int(SS * 0.6)))
        # Red diagonal stripe in the top-left corner.
        stripe_pts = [
            (card.left, card.top),
            (card.left + int(SS * 9), card.top),
            (card.left, card.top + int(SS * 9)),
        ]
        pygame.draw.polygon(big, RED_FADE, stripe_pts)
        # Hole punch upper-right.
        _punch_hole(big, SS,
                    card.right - int(SS * 4),
                    card.top + int(SS * 4),
                    int(SS * 1.6))
        # "RAIL TICKET" wordmark — compact header so the big train
        # has room to dominate.
        f_hdr = _font(int(SS * 3.6))
        hdr = f_hdr.render("RAIL TICKET", True, NEAR_BLACK)
        big.blit(hdr, hdr.get_rect(
            center=(card.centerx, card.top + int(SS * 6))))
        # Large detailed locomotive centred on the ticket.
        _locomotive(big, SS,
                    card.centerx, card.centery + int(SS * 4),
                    scale=1.55)
        # Tiny "ADULT" subtext along the bottom.
        f_tiny = _font(int(SS * 1.9))
        ad = f_tiny.render("ADULT FARE", True, INK)
        big.blit(ad, ad.get_rect(midbottom=(card.centerx,
                                              card.bottom - int(SS * 1))))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_o2_victorian(surf, cx, cy, pulse):
    """O2 — Victorian engraved ticket. Sepia paper, ornate
    double-line border with corner flourishes, "RAILWAY" header in
    bold serif spacing, locomotive in the centre, "ONE PASSAGE"
    small caps below."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
        _flat_body(big, card, SEPIA,
                   border_col=NEAR_BLACK,
                   border_w=max(1, int(SS * 0.4)))
        # Double border — outer thick + inner thin, 1-SS gap.
        _double_border(big, card.inflate(-int(SS * 2), -int(SS * 2)),
                       NEAR_BLACK,
                       outer_w=max(1, int(SS * 0.4)),
                       inner_w=max(1, SS // 3),
                       gap=int(SS * 1.2))
        # Corner flourishes — 3-dot triangle pips just inside the
        # inner border.
        margin = int(SS * 4.5)
        for cx0, cy0, sx, sy in (
            (card.left + margin,  card.top + margin,     1,  1),
            (card.right - margin, card.top + margin,    -1,  1),
            (card.left + margin,  card.bottom - margin,  1, -1),
            (card.right - margin, card.bottom - margin, -1, -1),
        ):
            pygame.draw.circle(big, INK, (cx0, cy0),
                               max(1, SS // 2))
            pygame.draw.circle(big, INK,
                               (cx0 + sx * int(SS * 1.4), cy0),
                               max(1, SS // 3))
            pygame.draw.circle(big, INK,
                               (cx0, cy0 + sy * int(SS * 1.4)),
                               max(1, SS // 3))
        # "RAILWAY" header — slimmer so the train can dominate.
        f_hdr = _font(int(SS * 3.4))
        hdr = f_hdr.render("RAILWAY", True, NEAR_BLACK)
        big.blit(hdr, hdr.get_rect(
            center=(card.centerx, card.top + int(SS * 5.5))))
        # Large detailed locomotive centred.
        _locomotive(big, SS,
                    card.centerx,
                    card.centery + int(SS * 4),
                    scale=1.65)
        # "ONE PASSAGE" small caps along the bottom.
        f_sub = _font(int(SS * 2.0))
        sub = f_sub.render("ONE PASSAGE", True, INK)
        big.blit(sub, sub.get_rect(
            midbottom=(card.centerx, card.bottom - int(SS * 2.5))))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_o3_two_tone(surf, cx, cy, pulse):
    """O3 — Cream cardstock with a faded red horizontal band across
    the middle (classic two-tone ticket). Black "RAIL CO." above
    and "EXPRESS" below, locomotive on the left, "FARE 25" on the
    right, two punch holes in the upper corners."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
        _flat_body(big, card, CREAM,
                   border_col=NEAR_BLACK,
                   border_w=max(1, int(SS * 0.5)))
        # Faded red horizontal band across the middle ~30% of the
        # ticket.
        band_h = int(card.height * 0.30)
        band = pygame.Rect(card.left, card.centery - band_h // 2,
                            card.width, band_h)
        pygame.draw.rect(big, RED_FADE, band)
        # "RAIL CO." caption (small, above the band).
        f_hdr = _font(int(SS * 2.6))
        hdr = f_hdr.render("RAIL CO.", True, NEAR_BLACK)
        big.blit(hdr, hdr.get_rect(
            center=(card.centerx, card.top + int(SS * 4.5))))
        # "EXPRESS" in cream on the red band.
        f_express = _font(int(SS * 3.0))
        ex = f_express.render("EXPRESS", True, CREAM)
        big.blit(ex, ex.get_rect(center=band.center))
        # Large detailed locomotive centred below the band.
        _locomotive(big, SS,
                    card.centerx,
                    card.bottom - int(SS * 7),
                    scale=1.40)
        # 2 punch holes upper corners.
        _punch_hole(big, SS,
                    card.left + int(SS * 4),
                    card.top + int(SS * 4),
                    int(SS * 1.4))
        _punch_hole(big, SS,
                    card.right - int(SS * 4),
                    card.top + int(SS * 4),
                    int(SS * 1.4))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_o4_conductor_punch(surf, cx, cy, pulse):
    """O4 — Tan ticket with heavy filigree corners, "TRAIN PASS"
    wordmark, a faded red rubber-stamp circle ("VOID") in the
    upper-right, locomotive in the centre, date stamp lower-right."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
        _flat_body(big, card, TAN,
                   border_col=NEAR_BLACK,
                   border_w=max(1, int(SS * 0.55)))
        # Inner border line.
        pygame.draw.rect(big, INK,
                         card.inflate(-int(SS * 2),
                                       -int(SS * 2)),
                         max(1, SS // 3))
        # Heavy filigree at each corner.
        margin = int(SS * 4)
        _corner_flourish(big, SS,
                         card.left + margin, card.top + margin,
                         scale=1.2)
        _corner_flourish(big, SS,
                         card.right - margin, card.top + margin,
                         scale=1.2)
        _corner_flourish(big, SS,
                         card.left + margin, card.bottom - margin,
                         scale=1.2)
        _corner_flourish(big, SS,
                         card.right - margin, card.bottom - margin,
                         scale=1.2)
        # "TRAIN PASS" wordmark — compact at the top.
        f_hdr = _font(int(SS * 3.0))
        hdr = f_hdr.render("TRAIN PASS", True, NEAR_BLACK)
        big.blit(hdr, hdr.get_rect(
            center=(card.centerx, card.top + int(SS * 6))))
        # Large detailed locomotive dominating the centre.
        _locomotive(big, SS, card.centerx,
                    card.centery + int(SS * 4),
                    scale=1.55)
        # Date stamp lower-right.
        f_date = _font(int(SS * 1.8))
        dt = f_date.render("OCT 26", True, INK)
        big.blit(dt, dt.get_rect(
            midright=(card.right - int(SS * 4),
                       card.bottom - int(SS * 2))))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_o5_pullman(surf, cx, cy, pulse):
    """O5 — Pullman first-class with two thin maroon side stripes,
    ornate decorative border with corner flourishes, "FIRST CLASS"
    in 2-line bold serif, locomotive in the centre with smoke,
    "PULLMAN" small subtext at the bottom."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
        _flat_body(big, card, PARCH,
                   border_col=NEAR_BLACK,
                   border_w=max(1, int(SS * 0.55)))
        # Two thin maroon vertical side stripes 4 SS inside the
        # border.
        for stripe_x in (card.left + int(SS * 4),
                         card.right - int(SS * 4)):
            pygame.draw.line(big, RED_DK,
                             (stripe_x, card.top + int(SS * 4)),
                             (stripe_x, card.bottom - int(SS * 4)),
                             max(1, int(SS * 0.7)))
        # Inner border line tracing around between the stripes.
        inner = pygame.Rect(card.left + int(SS * 6),
                             card.top + int(SS * 2),
                             card.width - int(SS * 12),
                             card.height - int(SS * 4))
        pygame.draw.rect(big, NEAR_BLACK, inner,
                         max(1, SS // 3))
        # Corner flourishes inside.
        margin = int(SS * 1.5)
        _corner_flourish(big, SS,
                         inner.left + margin, inner.top + margin,
                         scale=0.9)
        _corner_flourish(big, SS,
                         inner.right - margin, inner.top + margin,
                         scale=0.9)
        _corner_flourish(big, SS,
                         inner.left + margin,
                         inner.bottom - margin, scale=0.9)
        _corner_flourish(big, SS,
                         inner.right - margin,
                         inner.bottom - margin, scale=0.9)
        # "FIRST CLASS" on one line (was 2) so the big train has
        # vertical room below.
        f_big = _font(int(SS * 2.6))
        ft = f_big.render("FIRST CLASS", True, NEAR_BLACK)
        big.blit(ft, ft.get_rect(
            center=(card.centerx, inner.top + int(SS * 3.5))))
        # Large detailed locomotive centred.
        _locomotive(big, SS, card.centerx,
                    inner.centery + int(SS * 4), scale=1.40)
        # "PULLMAN" small subtext at the bottom.
        f_sub = _font(int(SS * 1.8))
        sb = f_sub.render("PULLMAN", True, INK)
        big.blit(sb, sb.get_rect(
            midbottom=(card.centerx, inner.bottom - int(SS * 1))))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


VARIANTS = [
    ("O1_br_edmondson",     draw_o1_br_edmondson,
     "O1: BR Edmondson cardstock — RAIL TICKET + red corner stripe"),
    ("O2_victorian",        draw_o2_victorian,
     "O2: Victorian engraved — double border + corner pips"),
    ("O3_two_tone",         draw_o3_two_tone,
     "O3: Cream + faded red band — RAIL CO. EXPRESS + FARE 25"),
    ("O4_conductor_punch",  draw_o4_conductor_punch,
     "O4: TRAIN PASS with filigree corners + red OK stamp"),
    ("O5_pullman",          draw_o5_pullman,
     "O5: Pullman first-class with maroon side stripes"),
]


# ── output ──────────────────────────────────────────────────────────────────

def _icon_zoom_png(draw_fn, label):
    base = pygame.Surface((NATIVE_W, NATIVE_H), pygame.SRCALPHA)
    draw_fn(base, NATIVE_W // 2, NATIVE_H // 2, pulse=1.6)
    big = pygame.transform.scale(base, (NATIVE_W * 6, NATIVE_H * 6))
    pygame.draw.rect(big, (255, 215, 0), big.get_rect(), 2)
    return big


def _ingame_png(draw_fn, label):
    world = build_world()
    frame = render_play_scene(world)
    icon_cx = int(world.bird.x) + 110
    icon_cy = int(world.bird.y)
    base = pygame.Surface((NATIVE_W, NATIVE_H), pygame.SRCALPHA)
    draw_fn(base, NATIVE_W // 2, NATIVE_H // 2, pulse=1.6)
    frame.blit(base, base.get_rect(center=(icon_cx, icon_cy)))
    return frame


def main():
    saved = []
    for label, fn, caption in VARIANTS:
        icon_zoom = _icon_zoom_png(fn, label)
        ingame    = _ingame_png(fn, label)
        zoom_path   = os.path.join(_OUT, f"{label}.png")
        ingame_path = os.path.join(_OUT, f"{label}_ingame.png")
        pygame.image.save(icon_zoom, zoom_path)
        pygame.image.save(ingame, ingame_path)
        saved.append((label, caption, icon_zoom))
        print(f"saved {zoom_path}")
        print(f"saved {ingame_path}")

    cell_w = saved[0][2].get_width()
    cell_h = saved[0][2].get_height()
    band_h = 56
    gap    = 12
    sheet_w = len(saved) * cell_w + (len(saved) - 1) * gap + 24
    sheet_h = cell_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, caption, icon) in enumerate(saved):
        x = 12 + idx * (cell_w + gap)
        sheet.blit(icon, (x, 12))
        band = _label_band(cell_w, label, caption, height=band_h)
        sheet.blit(band, (x, 12 + cell_h))
    sheet_path = os.path.join(_OUT, "00_contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/rail_oldschool_ticket_variants")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_ingame.png")


if __name__ == "__main__":
    main()
