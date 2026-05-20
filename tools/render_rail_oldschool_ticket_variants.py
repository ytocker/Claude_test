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
    Cab/back-of-train block omitted per user feedback ("not clear
    what is in the back part") — silhouette is now boiler-only,
    showing the chuffing front section of the loco.

    Components, drawn back-to-front:

      * boiler (horizontal cylinder) with 2 lighter iron-hoop
        bands and a small back-plate cap on the left end
      * smokestack with flared cap
      * steam dome on top of the boiler
      * sand dome (smaller) between steam dome and stack
      * headlight (lamp) on the front of the boiler
      * cowcatcher (slanted pilot) at the front-bottom
      * 2 large spoked driving wheels + 1 small leading wheel,
        connected by a coupling rod
      * 4 stacked smoke puffs above the stack

    All sizes scale with `scale` so the same recipe fits every
    ticket layout."""
    # Boiler-only footprint: width 20 SS × height 7 SS at
    # scale=1.0 (vs the earlier with-cab 28 SS × 14 SS).
    boiler_w = int(SS * 20 * scale)
    boiler_h = int(SS * 7 * scale)

    # ── Boiler — centred at (cx, cy) ──
    boiler = pygame.Rect(0, 0, boiler_w, boiler_h)
    boiler.center = (cx, cy)
    pygame.draw.rect(big, colour, boiler,
                     border_radius=max(1, int(SS * 0.8 * scale)))
    # 2 iron-hoop bands across the boiler (light strokes).
    for band_t in (0.30, 0.65):
        bx = boiler.left + int(boiler.width * band_t)
        pygame.draw.line(big, window_col,
                         (bx, boiler.top + max(1, SS // 3)),
                         (bx, boiler.bottom - max(1, SS // 3)),
                         max(1, int(SS * 0.4 * scale)))
    # Small back-plate cap on the left end so the boiler reads as
    # the cut-off "firebox" face, not as randomly truncated.
    plate_w = max(2, int(SS * 1.2 * scale))
    plate = pygame.Rect(boiler.left - plate_w,
                        boiler.top - max(1, int(SS * 0.5 * scale)),
                        plate_w,
                        boiler.height + max(2, int(SS * 1 * scale)))
    pygame.draw.rect(big, colour, plate,
                     border_radius=max(1, SS // 3))

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

    # Common rail-line — every wheel touches this ground. The
    # cowcatcher floats ABOVE the rail (real pilots are deflectors,
    # not snowploughs).
    big_wheel_r = max(3, int(SS * 2.5 * scale))
    small_wheel_r = max(2, int(SS * 1.5 * scale))
    ground_y = boiler.bottom + int(SS * 2.2 * scale) + big_wheel_r

    # ── Cowcatcher / pilot at the front-bottom ──
    # Inner edge attaches to the bottom-front of the boiler; outer
    # edge slopes forward+down but stops well ABOVE the rail line
    # (and above the leading wheel's bottom) so it reads as a
    # deflector hanging in front of the wheel rather than overlapping
    # with the rail-and-wheel assembly.
    cow_top_inner = boiler.bottom - max(1, int(SS * 0.4 * scale))
    cow_outer_x = boiler.right + int(SS * 4 * scale)
    cow_bot_y = ground_y - int(small_wheel_r * 1.1)
    cow_top_outer_y = cow_top_inner + int(SS * 1.5 * scale)
    cow_pts = [
        (boiler.right, cow_top_inner),
        (cow_outer_x, cow_top_outer_y),
        (cow_outer_x, cow_bot_y),
        (boiler.right, cow_bot_y - int(SS * 0.6 * scale)),
    ]
    pygame.draw.polygon(big, colour, cow_pts)
    # 3 vertical vanes hinting at the pilot grille.
    for f in (0.30, 0.55, 0.80):
        vx = cow_pts[0][0] + int((cow_pts[1][0] - cow_pts[0][0]) * f)
        v_top = cow_top_inner + int(SS * 1 * scale * f)
        v_bot = cow_bot_y - max(1, SS // 3)
        pygame.draw.line(big, window_col, (vx, v_top), (vx, v_bot),
                         max(1, SS // 3))

    # ── Driving wheels (2 big, spoked) + leading wheel (1 small) ──
    # All three wheels share `ground_y`. Drivers spaced 28% / 55%
    # of boiler width so they sit visibly under the boiler centre;
    # leading wheel at 82% so it's clearly between the front driver
    # and the cowcatcher.
    drive_y = ground_y - big_wheel_r
    drive_xs = (
        boiler.left + int(boiler.width * 0.28),
        boiler.left + int(boiler.width * 0.55),
    )
    for wx in drive_xs:
        pygame.draw.circle(big, colour, (wx, drive_y),
                           big_wheel_r)
        # 6 spokes.
        for ang_deg in (0, 60, 120, 180, 240, 300):
            ang = math.radians(ang_deg)
            x2 = wx + math.cos(ang) * (big_wheel_r - SS // 2)
            y2 = drive_y + math.sin(ang) * (big_wheel_r - SS // 2)
            pygame.draw.line(big, window_col, (wx, drive_y),
                             (int(x2), int(y2)),
                             max(1, int(SS * 0.45 * scale)))
        # Hub centre.
        pygame.draw.circle(big, window_col, (wx, drive_y),
                           max(1, int(SS * 0.7 * scale)))
        # Inner tyre edge.
        pygame.draw.circle(big, colour, (wx, drive_y),
                           big_wheel_r,
                           max(1, int(SS * 0.35 * scale)))
    # Leading wheel (pony truck) — clearly between the front
    # driver and the cowcatcher. No spokes (too small to read).
    lead_wx = boiler.left + int(boiler.width * 0.82)
    lead_wy = ground_y - small_wheel_r
    pygame.draw.circle(big, colour, (lead_wx, lead_wy),
                       small_wheel_r)
    pygame.draw.circle(big, window_col, (lead_wx, lead_wy),
                       max(1, int(SS * 0.45 * scale)))

    # ── Coupling rod connecting the driving wheels ──
    rod_h = max(2, int(SS * 0.6 * scale))
    rod_left = drive_xs[0]
    rod_right = drive_xs[1]
    rod_y = drive_y - int(big_wheel_r * 0.20) - rod_h // 2
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
    """RT1 — Edmondson cardstock, simplified for small-scale
    clarity. Cream paper, thick black border, big "TICKET" word
    centred (the only text), red diagonal corner stripe in the
    upper-left, single punch hole upper-right. Everything else
    stripped."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
        _flat_body(big, card, CREAM,
                   border_col=NEAR_BLACK,
                   border_w=max(2, int(SS * 1.0)))
        # First-class red corner stripe (large, visible at small
        # scale).
        pygame.draw.polygon(big, RED_FADE, [
            (card.left, card.top),
            (card.left + int(SS * 14), card.top),
            (card.left, card.top + int(SS * 14)),
        ])
        # Punch hole upper-right (slightly bigger so it reads).
        _punch_hole(big, SS,
                    card.right - int(SS * 5),
                    card.top + int(SS * 5),
                    int(SS * 2.0))
        # "RAIL" + "TICKET" stacked — both big, single hero block.
        f_main = _font(int(SS * 6.5))
        rail = f_main.render("RAIL", True, NEAR_BLACK)
        big.blit(rail, rail.get_rect(
            center=(card.centerx, card.centery - int(SS * 4))))
        f_sub = _font(int(SS * 4.5))
        tk = f_sub.render("TICKET", True, NEAR_BLACK)
        big.blit(tk, tk.get_rect(
            center=(card.centerx, card.centery + int(SS * 5))))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_o2_victorian(surf, cx, cy, pulse):
    """RT2 — Victorian engraved card, simplified. Sepia paper with
    a thick double-line border. One large hero locomotive centred
    on the body. No corner pips, no small text — just the
    silhouette + the engraved border."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
        _flat_body(big, card, SEPIA,
                   border_col=NEAR_BLACK,
                   border_w=max(2, int(SS * 1.0)))
        # Thick inner double border line — 1 thick inner stroke,
        # generously inset so it reads at small scale.
        inner = card.inflate(-int(SS * 3.5), -int(SS * 3.5))
        pygame.draw.rect(big, NEAR_BLACK, inner,
                         max(1, int(SS * 0.6)))
        # Large hero locomotive centred, scale 1.4 — big enough to
        # read at game scale.
        _locomotive(big, SS, card.centerx, card.centery + int(SS * 2),
                    scale=1.40)
        # Single small "RAILWAY" caption at the very top, no other
        # text.
        f_hdr = _font(int(SS * 2.8))
        hdr = f_hdr.render("RAILWAY", True, NEAR_BLACK)
        big.blit(hdr, hdr.get_rect(
            center=(card.centerx, card.top + int(SS * 5.5))))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_o3_two_tone(surf, cx, cy, pulse):
    """RT3 — Two-tone ticket, simplified. Cream upper half + faded
    red lower half. Big "RAIL" centred on the cream half, big
    "PASS" centred on the red half. Strong horizontal band reads
    instantly at small scale."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
        _flat_body(big, card, CREAM,
                   border_col=NEAR_BLACK,
                   border_w=max(2, int(SS * 1.0)))
        # Red lower-half band — strong colour contrast that reads
        # at any scale.
        band = pygame.Rect(card.left, card.centery,
                            card.width, card.height // 2)
        pygame.draw.rect(big, RED_FADE, band)
        # Black rule between the two halves.
        pygame.draw.line(big, NEAR_BLACK,
                         (card.left, band.top),
                         (card.right, band.top),
                         max(2, int(SS * 0.7)))
        # Big "RAIL" on the cream half.
        f_main = _font(int(SS * 5.5))
        rail = f_main.render("RAIL", True, NEAR_BLACK)
        big.blit(rail, rail.get_rect(
            center=(card.centerx,
                     card.top + (band.top - card.top) // 2)))
        # Big "PASS" on the red half (cream text).
        pass_t = f_main.render("PASS", True, CREAM)
        big.blit(pass_t, pass_t.get_rect(
            center=(card.centerx,
                     band.top + (card.bottom - band.top) // 2)))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_o4_conductor_punch(surf, cx, cy, pulse):
    """RT4 — Pullman first-class, simplified. Parchment with two
    THICK maroon vertical side stripes (visible at small scale),
    one huge "1ST" word centred + "CLASS" smaller below. No coach
    / seat / footer text."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
        _flat_body(big, card, PARCH,
                   border_col=NEAR_BLACK,
                   border_w=max(2, int(SS * 1.0)))
        # Two THICK maroon vertical stripes inside the border (3 SS
        # thick — easily visible at small scale).
        stripe_w = int(SS * 3)
        for stripe_x in (card.left + int(SS * 2),
                         card.right - int(SS * 2) - stripe_w):
            pygame.draw.rect(big, RED_DK,
                             (stripe_x, card.top + int(SS * 2),
                              stripe_w, card.height - int(SS * 4)))
        # Big "1ST" hero word.
        f_main = _font(int(SS * 8.0))
        first = f_main.render("1ST", True, NEAR_BLACK)
        big.blit(first, first.get_rect(
            center=(card.centerx, card.centery - int(SS * 3))))
        # "CLASS" smaller below.
        f_sub = _font(int(SS * 3.6))
        cl = f_sub.render("CLASS", True, NEAR_BLACK)
        big.blit(cl, cl.get_rect(
            center=(card.centerx, card.centery + int(SS * 7))))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_o5_pullman(surf, cx, cy, pulse):
    """RT5 — Carnival ride-pass, simplified. Solid red body with a
    cream outer perimeter band, deep serrated notches on the short
    edges, big "ADMIT" + "ONE" stacked in cream. No subhead, no
    rules, no loco."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        # Cream outer band.
        outer = pygame.Rect(2 * SS, 2 * SS, w - 4 * SS, h - 4 * SS)
        _flat_body(big, outer, CREAM,
                   border_col=NEAR_BLACK,
                   border_w=max(2, int(SS * 0.9)))
        # Inner red body.
        inner = outer.inflate(-int(SS * 3.0), -int(SS * 3.0))
        pygame.draw.rect(big, RIDE_RED_INNER := (210, 65, 75), inner)
        pygame.draw.rect(big, NEAR_BLACK, inner, max(1, int(SS * 0.5)))
        # Serrated notches on the SHORT (left + right) edges only.
        # Bigger notches so the silhouette signature reads at small
        # scale.
        notches = 5
        notch_step = inner.height // notches
        notch_w = int(SS * 2.2)
        for i in range(notches):
            cy_n = inner.top + i * notch_step + notch_step // 2
            pygame.draw.polygon(big, CREAM, [
                (inner.left,             cy_n - notch_step // 3),
                (inner.left,             cy_n + notch_step // 3),
                (inner.left + notch_w,   cy_n),
            ])
            pygame.draw.polygon(big, CREAM, [
                (inner.right,            cy_n - notch_step // 3),
                (inner.right,            cy_n + notch_step // 3),
                (inner.right - notch_w,  cy_n),
            ])
        # Big "ADMIT" + "ONE" stacked — only text on the ticket.
        f_main = _font(int(SS * 5.0))
        admit = f_main.render("ADMIT", True, CREAM)
        big.blit(admit, admit.get_rect(
            center=(inner.centerx, inner.centery - int(SS * 5))))
        one = f_main.render("ONE", True, CREAM)
        big.blit(one, one.get_rect(
            center=(inner.centerx, inner.centery + int(SS * 5))))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


VARIANTS = [
    ("O1_br_edmondson",     draw_o1_br_edmondson,
     "RT1: cream RAIL/TICKET + red corner + thick black border"),
    ("O2_victorian",        draw_o2_victorian,
     "RT2: sepia double-border with big centred locomotive"),
    ("O3_two_tone",         draw_o3_two_tone,
     "RT3: cream RAIL over red PASS — strong half/half"),
    ("O4_conductor_punch",  draw_o4_conductor_punch,
     "RT4: thick maroon side stripes + huge 1ST / CLASS"),
    ("O5_pullman",          draw_o5_pullman,
     "RT5: red ADMIT ONE with cream serrated-edge perimeter"),
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
