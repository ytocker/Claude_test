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


def _locomotive(big, SS, cx, cy, scale=1.0, colour=INK):
    """Tiny classic steam-locomotive silhouette anchored at its
    centre. Composed of: cab (left tall block), boiler (right
    horizontal cylinder), smokestack (small chimney on top of
    boiler), 3 driving wheels, small smoke puff above the stack.
    Period-appropriate for an old-school train ticket."""
    w = int(SS * 14 * scale)
    h = int(SS * 6.5 * scale)
    # Boiler — horizontal cylinder body on the right.
    boiler = pygame.Rect(0, 0, int(w * 0.62), int(h * 0.55))
    boiler.midright = (cx + w // 2, cy + int(SS * 0.4 * scale))
    pygame.draw.rect(big, colour, boiler,
                     border_radius=max(1, int(SS * 0.6 * scale)))
    # Cab — taller block on the left.
    cab_w = int(w * 0.32)
    cab_h = int(h * 0.85)
    cab = pygame.Rect(0, 0, cab_w, cab_h)
    cab.midleft = (cx - w // 2, cy + int(SS * 0.10 * scale))
    pygame.draw.rect(big, colour, cab,
                     border_radius=max(1, int(SS * 0.6 * scale)))
    # Cab window — small lighter rectangle.
    win = pygame.Rect(0, 0, int(cab_w * 0.5), int(cab_h * 0.35))
    win.center = (cab.centerx, cab.top + int(cab_h * 0.30))
    pygame.draw.rect(big, CREAM, win)
    # Smokestack — small chimney on top of the boiler near the
    # front.
    stack_w = max(1, int(SS * 1.6 * scale))
    stack_h = max(1, int(SS * 2.4 * scale))
    stack_x = boiler.right - int(SS * 2.5 * scale) - stack_w // 2
    pygame.draw.rect(big, colour,
                     (stack_x, boiler.top - stack_h,
                      stack_w, stack_h))
    # Stack flare (slight widening at the top).
    flare_w = int(stack_w * 1.5)
    flare = pygame.Rect(0, 0, flare_w, max(1, int(SS * 0.6 * scale)))
    flare.midbottom = (stack_x + stack_w // 2, boiler.top - stack_h)
    pygame.draw.rect(big, colour, flare)
    # Smoke puff above the stack (3 small circles).
    smoke_x = stack_x + stack_w // 2
    smoke_y = boiler.top - stack_h - int(SS * 2 * scale)
    for dx, dy, sr in (
        (0,                    0,                       int(SS * 1.2 * scale)),
        (int(SS * -1.2 * scale), int(SS * -1.5 * scale), int(SS * 1.0 * scale)),
        (int(SS *  1.2 * scale), int(SS * -2.5 * scale), int(SS * 0.9 * scale)),
    ):
        pygame.draw.circle(big, colour,
                            (smoke_x + dx, smoke_y + dy),
                            max(1, sr))
    # 3 driving wheels along the bottom.
    wheel_r = max(1, int(SS * 1.6 * scale))
    wheel_y = boiler.bottom + wheel_r - int(SS * 0.5 * scale)
    wheel_xs = (cab.right + int(SS * 1 * scale),
                boiler.left + int(boiler.width * 0.35),
                boiler.right - int(SS * 2 * scale))
    for wx in wheel_xs:
        pygame.draw.circle(big, colour, (wx, wheel_y), wheel_r)
        # Small cream hub.
        pygame.draw.circle(big, CREAM, (wx, wheel_y),
                           max(1, int(wheel_r * 0.35)))
    # Cowcatcher — small triangle at the front of the boiler.
    cow_pts = [
        (boiler.right, boiler.bottom - int(SS * 0.5 * scale)),
        (boiler.right + int(SS * 2 * scale),
         wheel_y - int(SS * 0.5 * scale)),
        (boiler.right, wheel_y - int(SS * 0.5 * scale)),
    ]
    pygame.draw.polygon(big, colour, cow_pts)


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
        # Big "RAIL" wordmark.
        f_big = _font(int(SS * 7))
        rail = f_big.render("RAIL", True, NEAR_BLACK)
        big.blit(rail, rail.get_rect(
            center=(card.centerx, card.top + int(SS * 11))))
        # "TICKET" smaller underneath.
        f_sub = _font(int(SS * 3.4))
        tk = f_sub.render("TICKET", True, NEAR_BLACK)
        big.blit(tk, tk.get_rect(
            center=(card.centerx, card.top + int(SS * 17))))
        # Locomotive silhouette at the bottom.
        _locomotive(big, SS,
                    card.centerx, card.bottom - int(SS * 7),
                    scale=0.95)
        # Tiny "ADULT" subtext under the loco.
        f_tiny = _font(int(SS * 1.8))
        ad = f_tiny.render("ADULT", True, INK)
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
        # "RAILWAY" header — bold, with letter-spacing implied via
        # plain render.
        f_hdr = _font(int(SS * 4.8))
        hdr = f_hdr.render("RAILWAY", True, NEAR_BLACK)
        big.blit(hdr, hdr.get_rect(
            center=(card.centerx, card.top + int(SS * 9))))
        # Locomotive centre.
        _locomotive(big, SS,
                    card.centerx,
                    card.centery + int(SS * 2),
                    scale=1.05)
        # "ONE PASSAGE" small caps below the loco.
        f_sub = _font(int(SS * 2.4))
        sub = f_sub.render("ONE PASSAGE", True, INK)
        big.blit(sub, sub.get_rect(
            midbottom=(card.centerx, card.bottom - int(SS * 4))))

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
        # Top "RAIL CO." caption.
        f_hdr = _font(int(SS * 3.6))
        hdr = f_hdr.render("RAIL CO.", True, NEAR_BLACK)
        big.blit(hdr, hdr.get_rect(
            center=(card.centerx, card.top + int(SS * 5.5))))
        # "EXPRESS" in cream on the red band.
        f_express = _font(int(SS * 3.4))
        ex = f_express.render("EXPRESS", True, CREAM)
        big.blit(ex, ex.get_rect(center=band.center))
        # Locomotive lower-left.
        _locomotive(big, SS,
                    card.left + int(SS * 11),
                    card.bottom - int(SS * 5),
                    scale=0.75)
        # "FARE 25" on the lower-right.
        f_fare = _font(int(SS * 2.6))
        fare = f_fare.render("FARE 25", True, NEAR_BLACK)
        big.blit(fare, fare.get_rect(
            midright=(card.right - int(SS * 3),
                       card.bottom - int(SS * 4))))
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
        # "TRAIN PASS" big bold wordmark.
        f_hdr = _font(int(SS * 4.8))
        hdr = f_hdr.render("TRAIN PASS", True, NEAR_BLACK)
        big.blit(hdr, hdr.get_rect(
            center=(card.centerx, card.top + int(SS * 9))))
        # Locomotive centre.
        _locomotive(big, SS, card.centerx,
                    card.centery + int(SS * 4),
                    scale=0.95)
        # Date stamp lower-right.
        f_date = _font(int(SS * 2.2))
        dt = f_date.render("OCT 26", True, INK)
        big.blit(dt, dt.get_rect(
            midright=(card.right - int(SS * 4),
                       card.bottom - int(SS * 3))))
        # Red rubber stamp in upper-right.
        _rubber_stamp(big, SS,
                      card.right - int(SS * 8),
                      card.top + int(SS * 9),
                      int(SS * 5),
                      "OK")

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
        # "FIRST" + "CLASS" on two lines.
        f_big = _font(int(SS * 3.4))
        ft = f_big.render("FIRST", True, NEAR_BLACK)
        big.blit(ft, ft.get_rect(
            center=(card.centerx, inner.top + int(SS * 4.5))))
        cl = f_big.render("CLASS", True, NEAR_BLACK)
        big.blit(cl, cl.get_rect(
            center=(card.centerx, inner.top + int(SS * 8))))
        # Locomotive centred just below the header.
        _locomotive(big, SS, card.centerx,
                    inner.top + int(SS * 14), scale=0.85)
        # "PULLMAN" small subtext at the bottom.
        f_sub = _font(int(SS * 2.2))
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
