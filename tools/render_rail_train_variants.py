"""Render 5 train-design variants for the rail-ticket icon.
Each variant paints a different train style onto the same RT2
ticket chassis (sepia paper + thin black perimeter + RAILWAY
caption + inner engraving line) at the live 48×36 / SS=6
footprint.

Variants:
  V1 classic_steam  - full steam loco: chimney + dome + cab
                      + leading wheel + driving pair
  V2 engine_tender  - 2-car: engine + coal tender
  V3 diesel_switcher - modern boxy diesel switcher
  V4 passenger_train - engine + passenger coach with windows
  V5 thomas_cartoon  - cartoon Thomas-style face on the boiler

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_rail_train_variants.py
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

from game.entities import PowerUp
from tools.render_helmet_side_view_variants import (
    build_world, render_play_scene, _label_band,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "rail_train_variants")
os.makedirs(_OUT, exist_ok=True)


# ── palette (matches the live rail icon) ────────────────────────────────────
SEPIA      = (228, 210, 170)
CREAM      = (238, 225, 195)
NEAR_BLACK = ( 18,  14,  10)
INK        = ( 30,  25,  20)
COAL       = ( 40,  30,  25)
COAL_HI    = ( 90,  70,  55)

SS = 6
NATIVE_W, NATIVE_H = 48, 36


# ── shared ticket chassis ───────────────────────────────────────────────────

def _paint_ticket_chassis(big):
    sw, sh = big.get_width(), big.get_height()
    card = pygame.Rect(3 * SS, 3 * SS, sw - 6 * SS, sh - 6 * SS)
    pygame.draw.rect(big, SEPIA, card)
    pygame.draw.rect(big, NEAR_BLACK, card, max(2, int(SS * 1.4)))
    inner = card.inflate(-int(SS * 3.5), -int(SS * 3.5))
    pygame.draw.rect(big, NEAR_BLACK, inner, max(1, int(SS * 0.6)))
    # RAILWAY caption.
    try:
        font = pygame.font.Font(os.path.join(
            _REPO, "game", "assets", "LiberationSans-Bold.ttf"),
            int(SS * 2.8))
    except Exception:
        font = pygame.font.SysFont(None, int(SS * 2.8), bold=True)
    hdr = font.render("RAILWAY", True, NEAR_BLACK)
    big.blit(hdr, hdr.get_rect(
        center=(card.centerx, card.top + int(SS * 5.5))))
    return card


# ── helpers ────────────────────────────────────────────────────────────────

def _spoked_wheel(big, cx, cy, r, scale, spokes=6,
                  rim=INK, hub=CREAM):
    """Spoked driving wheel."""
    pygame.draw.circle(big, rim, (cx, cy), r)
    for i in range(spokes):
        ang = math.radians(i * 360.0 / spokes)
        x2 = cx + math.cos(ang) * (r - SS // 2)
        y2 = cy + math.sin(ang) * (r - SS // 2)
        pygame.draw.line(big, hub, (cx, cy),
                         (int(x2), int(y2)),
                         max(1, int(SS * 0.45 * scale)))
    pygame.draw.circle(big, hub, (cx, cy),
                       max(1, int(SS * 0.7 * scale)))
    pygame.draw.circle(big, rim, (cx, cy), r,
                       max(1, int(SS * 0.35 * scale)))


def _plain_wheel(big, cx, cy, r, rim=INK, hub=CREAM):
    """Small plain wheel (no spokes — for diesel/tender)."""
    pygame.draw.circle(big, rim, (cx, cy), r)
    pygame.draw.circle(big, hub, (cx, cy), max(1, r // 3))


def _cowcatcher(big, boiler_right, ground_y, scale,
                colour=INK, window_col=CREAM):
    cow_top = boiler_right_inner_y = int(boiler_right[1])
    cow_pts = [
        (boiler_right[0], boiler_right[1]),
        (boiler_right[0] + int(SS * 4 * scale),
         ground_y - int(SS * 2 * scale)),
        (boiler_right[0] + int(SS * 4 * scale),
         ground_y - int(SS * 0.5 * scale)),
        (boiler_right[0],
         ground_y - int(SS * 1.5 * scale)),
    ]
    pygame.draw.polygon(big, colour, cow_pts)
    for f in (0.30, 0.55, 0.80):
        vx = cow_pts[0][0] + int(
            (cow_pts[1][0] - cow_pts[0][0]) * f)
        v_top = cow_pts[0][1] + int(SS * 1 * scale * f)
        v_bot = cow_pts[2][1] - max(1, SS // 3)
        pygame.draw.line(big, window_col, (vx, v_top), (vx, v_bot),
                         max(1, SS // 3))


def _coupling_rod(big, cx_a, cx_b, cy, h, colour=INK,
                  pin_col=CREAM, scale=1.0):
    pygame.draw.rect(big, colour, (cx_a, cy - h // 2,
                                    cx_b - cx_a, h))
    for cx in (cx_a, cx_b):
        pygame.draw.circle(big, pin_col, (cx, cy),
                           max(1, int(SS * 0.5 * scale)))


# ── 5 variant painters ─────────────────────────────────────────────────────

def _paint_train_v1_classic_steam(big, scale, cx, cy):
    """Steam loco: cab + boiler + chimney + dome + drivers +
    leading wheel + cowcatcher."""
    boiler_w = int(SS * 18 * scale)
    boiler_h = int(SS * 6.5 * scale)
    boiler = pygame.Rect(0, 0, boiler_w, boiler_h)
    boiler.midright = (cx + int(SS * 8 * scale), cy)
    pygame.draw.rect(big, INK, boiler,
                     border_radius=max(1, int(SS * 0.8 * scale)))
    # Iron hoops.
    for band_t in (0.35, 0.70):
        bx = boiler.left + int(boiler.width * band_t)
        pygame.draw.line(big, CREAM,
                         (bx, boiler.top + SS // 3),
                         (bx, boiler.bottom - SS // 3),
                         max(1, int(SS * 0.4 * scale)))
    # Cab on the left.
    cab_w = int(SS * 6 * scale)
    cab_h = int(SS * 8 * scale)
    cab = pygame.Rect(0, 0, cab_w, cab_h)
    cab.midright = (boiler.left, cy)
    pygame.draw.rect(big, INK, cab,
                     border_radius=max(1, int(SS * 0.6 * scale)))
    roof = pygame.Rect(0, 0, cab_w + int(SS * 1.2 * scale),
                        max(1, int(SS * 0.8 * scale)))
    roof.midbottom = (cab.centerx, cab.top + max(1, SS // 3))
    pygame.draw.rect(big, INK, roof)
    # Cab window.
    win = pygame.Rect(0, 0, int(cab_w * 0.55), int(cab_h * 0.35))
    win.center = (cab.centerx, cab.top + int(cab_h * 0.42))
    pygame.draw.rect(big, CREAM, win)
    pygame.draw.rect(big, INK, win, max(1, SS // 3))
    # Smokestack with flare + 3 smoke puffs.
    stack_w = max(2, int(SS * 1.8 * scale))
    stack_h = max(3, int(SS * 3.5 * scale))
    stack_x = boiler.right - int(SS * 4 * scale) - stack_w // 2
    stack = pygame.Rect(stack_x, boiler.top - stack_h,
                         stack_w, stack_h)
    pygame.draw.rect(big, INK, stack)
    flare = pygame.Rect(0, 0, int(stack_w * 1.8),
                         max(1, int(SS * 0.7 * scale)))
    flare.midbottom = (stack.centerx, stack.top)
    pygame.draw.rect(big, INK, flare)
    # 3 smoke puffs.
    for dx, dy, sr in (
        (0,                       -int(SS * 0.8 * scale), int(SS * 1.4 * scale)),
        (int(SS * -1.4 * scale),  -int(SS * 2.8 * scale), int(SS * 1.6 * scale)),
        (int(SS *  1.4 * scale),  -int(SS * 4.8 * scale), int(SS * 1.2 * scale)),
    ):
        pygame.draw.circle(big, INK,
                            (stack.centerx + dx,
                             stack.top + dy),
                            max(1, sr))
    # Steam dome.
    dome_w = max(2, int(SS * 2.0 * scale))
    dome_h = max(2, int(SS * 1.6 * scale))
    dome_cx = boiler.left + int(boiler.width * 0.30)
    dome_rect = pygame.Rect(0, 0, dome_w, dome_h * 2)
    dome_rect.midbottom = (dome_cx, boiler.top + max(1, SS // 3))
    pygame.draw.ellipse(big, INK, dome_rect)
    # Headlight at front of boiler.
    hl_r = max(2, int(SS * 1.1 * scale))
    pygame.draw.circle(big, INK,
                       (boiler.right - hl_r - int(SS * 0.4 * scale),
                        boiler.top + int(boiler.height * 0.45)),
                       hl_r + max(1, SS // 3))
    pygame.draw.circle(big, CREAM,
                       (boiler.right - hl_r - int(SS * 0.4 * scale),
                        boiler.top + int(boiler.height * 0.45)),
                       max(1, int(hl_r * 0.6)))
    # Wheels — 2 large drivers + 1 small leading.
    wheel_r = max(3, int(SS * 2.4 * scale))
    gap = max(1, int(SS * 0.4 * scale))
    wheel_cy = boiler.bottom + wheel_r + gap
    ground_y = wheel_cy + wheel_r
    drive_xs = (
        boiler.left + int(boiler.width * 0.30),
        boiler.left + int(boiler.width * 0.65),
    )
    rod_h = max(2, int(SS * 0.9 * scale))
    rod_y = wheel_cy - int(wheel_r * 0.30) - rod_h // 2
    pygame.draw.rect(big, INK,
                     (drive_xs[0], rod_y,
                      drive_xs[1] - drive_xs[0], rod_h))
    for wx in drive_xs:
        _spoked_wheel(big, wx, wheel_cy, wheel_r, scale)
        pygame.draw.circle(big, CREAM, (wx, rod_y + rod_h // 2),
                           max(1, int(SS * 0.5 * scale)))
    # Leading wheel.
    lead_r = max(2, int(SS * 1.6 * scale))
    lead_wx = boiler.right - int(SS * 1 * scale) - lead_r
    lead_wy = ground_y - lead_r
    _plain_wheel(big, lead_wx, lead_wy, lead_r)
    # Cowcatcher.
    _cowcatcher(big,
                (boiler.right, boiler.bottom - SS // 3),
                ground_y, scale)


def _paint_train_v2_engine_tender(big, scale, cx, cy):
    """Engine + coal tender. 2 cars connected by coupling."""
    # Engine on the right.
    eng_w = int(SS * 14 * scale)
    eng_h = int(SS * 6 * scale)
    eng = pygame.Rect(0, 0, eng_w, eng_h)
    eng.midright = (cx + int(SS * 9 * scale), cy)
    pygame.draw.rect(big, INK, eng,
                     border_radius=max(1, int(SS * 0.7 * scale)))
    # Cab on the engine.
    cab_w = int(SS * 5 * scale)
    cab_h = int(SS * 7 * scale)
    cab = pygame.Rect(0, 0, cab_w, cab_h)
    cab.midright = (eng.left, cy)
    pygame.draw.rect(big, INK, cab,
                     border_radius=max(1, int(SS * 0.6 * scale)))
    win = pygame.Rect(0, 0, int(cab_w * 0.55), int(cab_h * 0.35))
    win.center = (cab.centerx, cab.top + int(cab_h * 0.45))
    pygame.draw.rect(big, CREAM, win)
    pygame.draw.rect(big, INK, win, max(1, SS // 3))
    # Tender on the left (open coal car).
    ten_w = int(SS * 8 * scale)
    ten_h = int(SS * 5 * scale)
    ten = pygame.Rect(0, 0, ten_w, ten_h)
    ten.midright = (cab.left - int(SS * 1.5 * scale), cy + SS // 2)
    pygame.draw.rect(big, INK, ten,
                     max(1, int(SS * 0.6 * scale)))
    # Coal lumps inside the tender.
    for dx in (-3, 0, 3, 6):
        cx_lump = ten.centerx + dx
        pygame.draw.circle(big, COAL,
                           (cx_lump, ten.top + int(SS * 1.5)),
                           max(1, int(SS * 0.8 * scale)))
        pygame.draw.circle(big, COAL_HI,
                           (cx_lump - 1, ten.top + int(SS * 1.3)),
                           max(1, int(SS * 0.3 * scale)))
    # Coupling between cab and tender.
    pygame.draw.rect(big, INK,
                     (ten.right, cy - SS // 2,
                      cab.left - ten.right, max(1, SS // 2)))
    # Wheels.
    wheel_r = max(2, int(SS * 1.8 * scale))
    wheel_cy = eng.bottom + wheel_r
    ground_y = wheel_cy + wheel_r
    for wx in (eng.left + int(SS * 2 * scale),
               eng.right - int(SS * 2 * scale)):
        _spoked_wheel(big, wx, wheel_cy, wheel_r, scale)
    # Tender wheels (smaller).
    t_wheel_r = max(1, int(SS * 1.3 * scale))
    t_wheel_cy = ten.bottom + t_wheel_r
    for wx in (ten.left + int(SS * 1.5 * scale),
               ten.right - int(SS * 1.5 * scale)):
        _plain_wheel(big, wx, t_wheel_cy, t_wheel_r)
    # Headlight + cowcatcher on the engine.
    hl_r = max(2, int(SS * 1.0 * scale))
    pygame.draw.circle(big, INK,
                       (eng.right - hl_r - SS // 2,
                        eng.top + int(eng.height * 0.45)),
                       hl_r + max(1, SS // 3))
    pygame.draw.circle(big, CREAM,
                       (eng.right - hl_r - SS // 2,
                        eng.top + int(eng.height * 0.45)),
                       max(1, int(hl_r * 0.6)))
    _cowcatcher(big,
                (eng.right, eng.bottom - SS // 3),
                ground_y, scale)


def _paint_train_v3_diesel_switcher(big, scale, cx, cy):
    """Modern boxy diesel with cab on top, 4 small wheels."""
    body_w = int(SS * 22 * scale)
    body_h = int(SS * 6 * scale)
    body = pygame.Rect(0, 0, body_w, body_h)
    body.center = (cx, cy + int(SS * 0.5 * scale))
    pygame.draw.rect(big, INK, body,
                     border_radius=max(1, int(SS * 0.5 * scale)))
    # Cab on top.
    cab_w = int(SS * 7 * scale)
    cab_h = int(SS * 4 * scale)
    cab = pygame.Rect(0, 0, cab_w, cab_h)
    cab.midbottom = (body.centerx - int(SS * 2 * scale), body.top)
    pygame.draw.rect(big, INK, cab,
                     border_radius=max(1, int(SS * 0.5 * scale)))
    # Wraparound window.
    win = pygame.Rect(0, 0, int(cab_w * 0.7), int(cab_h * 0.45))
    win.center = (cab.centerx, cab.top + int(cab_h * 0.4))
    pygame.draw.rect(big, CREAM, win)
    pygame.draw.rect(big, INK, win, max(1, SS // 3))
    # Twin headlights at the front.
    hl_r = max(1, int(SS * 0.9 * scale))
    hl_cx = body.right - hl_r - int(SS * 0.5 * scale)
    for dy_frac in (0.30, 0.70):
        hl_cy = body.top + int(body.height * dy_frac)
        pygame.draw.circle(big, INK, (hl_cx, hl_cy),
                           hl_r + max(1, SS // 3))
        pygame.draw.circle(big, CREAM, (hl_cx, hl_cy),
                           max(1, int(hl_r * 0.6)))
    # Side vent grilles — 3 short horizontal lines.
    for vent_dy in (-2, 0, 2):
        pygame.draw.line(big, CREAM,
                         (body.right - int(SS * 5 * scale),
                          body.centery + vent_dy),
                         (body.right - int(SS * 2 * scale),
                          body.centery + vent_dy),
                         max(1, SS // 3))
    # 4 small wheels in a row.
    wheel_r = max(2, int(SS * 1.4 * scale))
    wheel_cy = body.bottom + wheel_r
    n = 4
    span = body_w - int(SS * 6 * scale)
    for i in range(n):
        t = i / (n - 1)
        wx = body.left + int(SS * 3 * scale) + int(t * span)
        _plain_wheel(big, wx, wheel_cy, wheel_r)


def _paint_train_v4_passenger(big, scale, cx, cy):
    """Engine + passenger coach with 5 windows."""
    coach_w = int(SS * 16 * scale)
    coach_h = int(SS * 7 * scale)
    coach = pygame.Rect(0, 0, coach_w, coach_h)
    coach.midleft = (cx - int(SS * 12 * scale), cy)
    pygame.draw.rect(big, INK, coach,
                     border_radius=max(1, int(SS * 0.6 * scale)))
    # Roof line.
    roof = pygame.Rect(0, 0, coach_w + int(SS * 1.5 * scale),
                        max(1, int(SS * 0.7 * scale)))
    roof.midbottom = (coach.centerx, coach.top + max(1, SS // 3))
    pygame.draw.rect(big, INK, roof)
    # 5 small square windows.
    n_win = 5
    win_w = int(coach_w / (n_win + 1.5))
    win_w = max(2, win_w)
    win_h = int(coach_h * 0.40)
    margin = (coach_w - n_win * win_w) // (n_win + 1)
    for i in range(n_win):
        wx0 = coach.left + margin + i * (win_w + margin)
        wy0 = coach.top + int(coach_h * 0.25)
        win_rect = pygame.Rect(wx0, wy0, win_w, win_h)
        pygame.draw.rect(big, CREAM, win_rect)
        pygame.draw.rect(big, INK, win_rect, max(1, SS // 3))
    # Engine on the right.
    eng_w = int(SS * 8 * scale)
    eng_h = int(SS * 6 * scale)
    eng = pygame.Rect(0, 0, eng_w, eng_h)
    eng.midleft = (coach.right + int(SS * 1.5 * scale), cy)
    pygame.draw.rect(big, INK, eng,
                     border_radius=max(1, int(SS * 0.6 * scale)))
    # Coupling.
    pygame.draw.rect(big, INK,
                     (coach.right, cy - SS // 2,
                      eng.left - coach.right, max(1, SS // 2)))
    # Engine window (single).
    e_win = pygame.Rect(0, 0, int(eng_w * 0.45), int(eng_h * 0.40))
    e_win.center = (eng.left + int(eng_w * 0.35),
                     eng.top + int(eng_h * 0.40))
    pygame.draw.rect(big, CREAM, e_win)
    pygame.draw.rect(big, INK, e_win, max(1, SS // 3))
    # Headlight.
    hl_r = max(1, int(SS * 1.0 * scale))
    pygame.draw.circle(big, CREAM,
                       (eng.right - hl_r - SS // 2,
                        eng.top + int(eng.height * 0.50)),
                       max(1, int(hl_r * 0.7)))
    # Wheels.
    wheel_r = max(2, int(SS * 1.5 * scale))
    wheel_cy = coach.bottom + wheel_r
    ground_y = wheel_cy + wheel_r
    # 4 coach wheels (2 pairs).
    for wx in (coach.left + int(SS * 2 * scale),
               coach.left + int(SS * 5 * scale),
               coach.right - int(SS * 5 * scale),
               coach.right - int(SS * 2 * scale)):
        _plain_wheel(big, wx, wheel_cy, wheel_r)
    # 2 engine wheels.
    for wx in (eng.left + int(SS * 2 * scale),
               eng.right - int(SS * 3 * scale)):
        _spoked_wheel(big, wx, wheel_cy, wheel_r, scale)
    # Cowcatcher on engine front.
    _cowcatcher(big,
                (eng.right, eng.bottom - SS // 3),
                ground_y, scale)


def _paint_train_v5_thomas(big, scale, cx, cy):
    """Cartoon Thomas-style: round face on the smokebox front,
    chimney with a smoke puff, cab on the back, single big
    wheel + small leading wheel."""
    boiler_w = int(SS * 16 * scale)
    boiler_h = int(SS * 7 * scale)
    boiler = pygame.Rect(0, 0, boiler_w, boiler_h)
    boiler.midright = (cx + int(SS * 7 * scale), cy)
    pygame.draw.rect(big, INK, boiler,
                     border_radius=max(1, int(SS * 1.5 * scale)))
    # Cab on the left.
    cab_w = int(SS * 6 * scale)
    cab_h = int(SS * 8 * scale)
    cab = pygame.Rect(0, 0, cab_w, cab_h)
    cab.midright = (boiler.left + int(SS * 0.5 * scale), cy)
    pygame.draw.rect(big, INK, cab,
                     border_radius=max(1, int(SS * 0.6 * scale)))
    win = pygame.Rect(0, 0, int(cab_w * 0.55), int(cab_h * 0.35))
    win.center = (cab.centerx, cab.top + int(cab_h * 0.40))
    pygame.draw.rect(big, CREAM, win)
    pygame.draw.rect(big, INK, win, max(1, SS // 3))
    # Smokebox face on the front (right end of boiler).
    face_r = max(2, int(SS * 2.4 * scale))
    face_cx = boiler.right - int(SS * 0.5 * scale)
    face_cy = boiler.centery
    pygame.draw.circle(big, CREAM, (face_cx, face_cy), face_r)
    pygame.draw.circle(big, INK, (face_cx, face_cy), face_r,
                       max(1, SS // 3))
    # Eyes.
    eye_r = max(1, int(SS * 0.5 * scale))
    for ex in (face_cx - int(SS * 0.9 * scale),
               face_cx + int(SS * 0.9 * scale)):
        pygame.draw.circle(big, INK, (ex, face_cy - SS // 2), eye_r)
    # Smile (small arc).
    smile_rect = pygame.Rect(0, 0, int(face_r * 1.2),
                              int(face_r * 0.6))
    smile_rect.midtop = (face_cx, face_cy + SS // 3)
    pygame.draw.arc(big, INK, smile_rect,
                    math.radians(200), math.radians(340),
                    max(1, SS // 3))
    # Chimney + smoke puff.
    stack_w = max(2, int(SS * 1.8 * scale))
    stack_h = max(3, int(SS * 2.5 * scale))
    stack_x = boiler.left + int(boiler.width * 0.55) - stack_w // 2
    stack = pygame.Rect(stack_x, boiler.top - stack_h,
                         stack_w, stack_h)
    pygame.draw.rect(big, INK, stack)
    flare = pygame.Rect(0, 0, int(stack_w * 1.7),
                         max(1, int(SS * 0.7 * scale)))
    flare.midbottom = (stack.centerx, stack.top)
    pygame.draw.rect(big, INK, flare)
    # 1 round smoke puff.
    pygame.draw.circle(big, INK,
                       (stack.centerx,
                        stack.top - int(SS * 2 * scale)),
                       max(2, int(SS * 1.8 * scale)))
    # 1 big driving wheel + 1 small leading.
    big_wheel_r = max(3, int(SS * 3.0 * scale))
    big_wcy = boiler.bottom + big_wheel_r
    big_wcx = boiler.left + int(boiler.width * 0.42)
    ground_y = big_wcy + big_wheel_r
    _spoked_wheel(big, big_wcx, big_wcy, big_wheel_r, scale)
    # Leading wheel.
    lead_r = max(2, int(SS * 1.5 * scale))
    _plain_wheel(big, boiler.right - int(SS * 3 * scale),
                  ground_y - lead_r, lead_r)


VARIANTS = [
    ("V1_classic_steam",   _paint_train_v1_classic_steam,
     "V1: classic steam loco — cab + chimney + dome + smoke"),
    ("V2_engine_tender",   _paint_train_v2_engine_tender,
     "V2: engine + coal tender (2 cars)"),
    ("V3_diesel_switcher", _paint_train_v3_diesel_switcher,
     "V3: modern diesel switcher (boxy + 4 wheels)"),
    ("V4_passenger",       _paint_train_v4_passenger,
     "V4: engine + passenger coach with 5 windows"),
    ("V5_thomas",          _paint_train_v5_thomas,
     "V5: Thomas-style cartoon with smiling smokebox face"),
]


# ── output ──────────────────────────────────────────────────────────────────

def _build_icon(painter):
    """Paint chassis + train at SS=6, smoothscale down to 48×36."""
    sw, sh = NATIVE_W * SS, NATIVE_H * SS
    big = pygame.Surface((sw, sh), pygame.SRCALPHA)
    card = _paint_ticket_chassis(big)
    # Centre the train roughly at (card.centerx, card.centery + 2*SS)
    # using scale 1.0 — same anchor as the live icon.
    painter(big, 1.0, card.centerx, card.centery + int(SS * 2))
    return pygame.transform.smoothscale(big, (NATIVE_W, NATIVE_H))


def _zoom(icon, factor=8):
    big = pygame.transform.scale(icon,
                                  (NATIVE_W * factor, NATIVE_H * factor))
    pygame.draw.rect(big, (255, 215, 0), big.get_rect(), 2)
    return big


def _ingame(icon):
    world = build_world()
    frame = render_play_scene(world)
    icon_cx = int(world.bird.x) + 110
    icon_cy = int(world.bird.y)
    frame.blit(icon, icon.get_rect(center=(icon_cx, icon_cy)))
    return frame


def main():
    saved = []
    for label, painter, caption in VARIANTS:
        icon = _build_icon(painter)
        zoom_path = os.path.join(_OUT, f"{label}.png")
        ingame_path = os.path.join(_OUT, f"{label}_ingame.png")
        pygame.image.save(_zoom(icon), zoom_path)
        pygame.image.save(_ingame(icon), ingame_path)
        saved.append((label, caption, _zoom(icon, factor=6)))
        print(f"saved {zoom_path}")
        print(f"saved {ingame_path}")

    cell_w = saved[0][2].get_width()
    cell_h = saved[0][2].get_height()
    band_h = 56
    gap = 12
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
            "v5_powerups/docs/screenshots/rail_train_variants")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_ingame.png")


if __name__ == "__main__":
    main()
