"""Render 5 LOTTERY powerup-icon design candidates — polished
versions inspired by real-world lottery imagery (scratch-off
cards, numbered balls, wheel of fortune, golden ticket, jackpot
star). All painted at 6× supersample to a 56×42 landscape
footprint, then smoothscale'd down for crisp anti-aliased edges.

Each candidate is saved twice:
  * <label>.png         — icon centred on a transparent 56×42
                          surface scaled 6× to 336×252 for review
  * <label>_ingame.png  — composited onto a real gameplay frame
                          via build_world(), so the user can see
                          the icon in context

Plus a horizontal contact sheet `00_contact_sheet.png` with all 5.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_lottery_icon_variants.py
"""

import math
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
from tools.render_helmet_side_view_variants import (
    build_world, render_play_scene, _label_band,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "lottery_icon_variants")
os.makedirs(_OUT, exist_ok=True)

_FONT_PATH = str(pathlib.Path(_REPO) / "game" / "assets"
                 / "LiberationSans-Bold.ttf")


# ── lottery palette ─────────────────────────────────────────────────────────
GOLD_HI   = (255, 230, 110)
GOLD_MID  = (250, 200,  70)
GOLD_LO   = (220, 175,  50)
GOLD_DEEP = (180, 130,  20)
STROKE    = (110,  75,  10)   # near-brown for outlines on gold
CHROME    = (225, 225, 232)
CHROME_LO = (160, 165, 180)
CREAM     = (255, 245, 200)
NAVY      = ( 30,  40,  80)
WHITE     = (255, 255, 255)
RED       = (200,  50,  60)
TEAL      = ( 90, 175, 175)
MAGENTA   = (225, 130, 175)
CYAN      = (120, 190, 235)
ORANGE    = (240, 150,  60)
SHADOW    = (  0,   0,   0,  90)


# ── shared helpers ──────────────────────────────────────────────────────────

def _ss_paint(paint_fn, native_w=56, native_h=42, ss=6):
    """Run paint_fn(big_surf, ss) on a 6× supersampled surface,
    then smoothscale down to native size for AA edges."""
    big = pygame.Surface((native_w * ss, native_h * ss), pygame.SRCALPHA)
    paint_fn(big, ss)
    return pygame.transform.smoothscale(big, (native_w, native_h))


def _font(size):
    return pygame.font.Font(_FONT_PATH, size)


def _v_gradient_rect(surf, rect, top_col, bot_col, radius=0):
    """Fill `rect` on `surf` with a vertical 2-stop gradient. Honours
    `radius` by masking through a rounded-rect alpha stamp."""
    tmp = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = rect.height
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top_col[0] * (1 - t) + bot_col[0] * t)
        g = int(top_col[1] * (1 - t) + bot_col[1] * t)
        b = int(top_col[2] * (1 - t) + bot_col[2] * t)
        pygame.draw.line(tmp, (r, g, b), (0, y), (rect.width, y))
    if radius:
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                         mask.get_rect(), border_radius=radius)
        tmp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tmp, rect.topleft)


def _star_polygon(cx, cy, r_outer, r_inner, points, rot_deg=0):
    """Return a list of (x, y) vertices for an n-pointed star."""
    pts = []
    for i in range(points * 2):
        ang = math.radians(rot_deg - 90 + i * (180.0 / points))
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    return pts


def _sparkle(surf, cx, cy, r, colour=CREAM):
    """Tiny 4-point sparkle star centred at (cx, cy)."""
    pts = _star_polygon(cx, cy, r, r * 0.32, 4)
    pygame.draw.polygon(surf, colour, pts)


# ── 5 icon variants ─────────────────────────────────────────────────────────

def draw_l1_foil_scratch(surf, cx, cy, pulse):
    """L1 — Premium foil-bordered scratch card. Gold gradient body,
    chrome outer perimeter, dashed dark-gold inner stroke, silver
    scratch panel with cross-hatch, "? ? ?" + 3 sparkles."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        # Card body — rounded-rect with vertical gradient.
        card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
        _v_gradient_rect(big, card, GOLD_HI, GOLD_LO, radius=4 * SS)
        # Top highlight band — laminated sheen along upper third.
        hi_h = card.height // 3
        hi = pygame.Surface((card.width, hi_h), pygame.SRCALPHA)
        for y in range(hi_h):
            a = int(110 * (1.0 - y / hi_h))
            pygame.draw.line(hi, (255, 250, 220, a),
                             (0, y), (hi.get_width(), y))
        big.blit(hi, (card.x, card.y))
        # Outer chrome perimeter ring — 2 SS thick, flush with edge.
        pygame.draw.rect(big, CHROME, card, width=2 * SS,
                         border_radius=4 * SS)
        # Inner dashed dark-gold stroke — inset 2 SS.
        inner = card.inflate(-4 * SS, -4 * SS)
        # Draw the dashes manually by stepping along the rectangle
        # perimeter. Each dash is 4 SS long with a 3 SS gap.
        dash_col = STROKE
        dash, gap = 4 * SS, 3 * SS
        def _dash_line(p0, p1):
            x0, y0 = p0
            x1, y1 = p1
            length = math.hypot(x1 - x0, y1 - y0)
            if length <= 0:
                return
            dx = (x1 - x0) / length
            dy = (y1 - y0) / length
            t = 0.0
            while t < length:
                t2 = min(t + dash, length)
                pygame.draw.line(big, dash_col,
                                 (x0 + dx * t, y0 + dy * t),
                                 (x0 + dx * t2, y0 + dy * t2),
                                 max(1, SS // 2))
                t += dash + gap
        _dash_line((inner.left, inner.top), (inner.right, inner.top))
        _dash_line((inner.right, inner.top), (inner.right, inner.bottom))
        _dash_line((inner.right, inner.bottom), (inner.left, inner.bottom))
        _dash_line((inner.left, inner.bottom), (inner.left, inner.top))

        # Scratch panel — silvery rect, ~60% of card area.
        panel = pygame.Rect(0, 0, card.width - 12 * SS,
                            card.height - 16 * SS)
        panel.center = (card.centerx, card.centery + 2 * SS)
        _v_gradient_rect(big, panel, CHROME, CHROME_LO,
                         radius=2 * SS)
        # Procedural cross-hatch — thin diagonal lines for "scratched"
        # texture.
        for off in range(-panel.height, panel.width, 4 * SS):
            x0 = panel.left + off
            y0 = panel.top
            x1 = x0 + panel.height
            y1 = panel.bottom
            pygame.draw.line(big, (180, 185, 200, 80),
                             (x0, y0), (x1, y1), max(1, SS // 3))
        pygame.draw.rect(big, NAVY, panel, width=SS,
                         border_radius=2 * SS)
        # "? ? ?" — bold navy with a 1-SS cream highlight above.
        f = _font(int(panel.height * 0.78))
        text = f.render("? ? ?", True, NAVY)
        hl   = f.render("? ? ?", True, CREAM)
        tr = text.get_rect(center=panel.center)
        big.blit(hl, hl.get_rect(center=(tr.centerx, tr.centery - SS)))
        big.blit(text, tr)
        # 3 sparkle stars at the upper-right corners of the card.
        _sparkle(big, card.right - 6 * SS, card.top + 6 * SS, 3 * SS)
        _sparkle(big, card.left + 8 * SS, card.bottom - 8 * SS, 2 * SS)
        _sparkle(big, card.right - 10 * SS, card.bottom - 5 * SS, 2 * SS,
                 colour=(255, 230, 120))

    # Light pulse-driven tilt so the card has the same "alive" feel as
    # the current live icon.
    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 6
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_l2_balls(surf, cx, cy, pulse):
    """L2 — Three numbered lottery balls clustered diagonally on a
    cream rounded-rect with chrome perimeter."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        bg = pygame.Rect(2 * SS, 2 * SS, w - 4 * SS, h - 4 * SS)
        _v_gradient_rect(big, bg, (255, 252, 235), (240, 230, 200),
                         radius=4 * SS)
        # Chrome perimeter ring.
        pygame.draw.rect(big, CHROME, bg, width=2 * SS,
                         border_radius=4 * SS)
        pygame.draw.rect(big, GOLD_DEEP, bg, width=SS // 2,
                         border_radius=4 * SS)

        # Thin red ribbon arc at the bottom (banner hint).
        ribbon = pygame.Rect(bg.left + 5 * SS, bg.bottom - 8 * SS,
                             bg.width - 10 * SS, 4 * SS)
        pygame.draw.rect(big, (170, 30, 40), ribbon,
                         border_radius=2 * SS)
        # 2 small stars on the ribbon.
        _sparkle(big, ribbon.left + 6 * SS, ribbon.centery, SS + 1)
        _sparkle(big, ribbon.right - 6 * SS, ribbon.centery, SS + 1)

        # Three balls — cyan, gold, magenta. Front ball largest +
        # centred, others tucked behind.
        ball_specs = [
            # (cx_off, cy_off, radius, fill, num)
            (-10 * SS,  -3 * SS, 7 * SS,  CYAN,    "7"),
            (  0 * SS,  -5 * SS, 8 * SS,  GOLD_MID, "13"),
            ( 10 * SS,  -3 * SS, 7 * SS,  MAGENTA, "21"),
        ]
        for dx, dy, r, fill, num in ball_specs:
            bcx = bg.centerx + dx
            bcy = bg.centery + dy - 2 * SS
            # Drop shadow disc beneath.
            sh = pygame.Surface((r * 2 + 4 * SS, r * 2 + 4 * SS),
                                pygame.SRCALPHA)
            pygame.draw.circle(sh, SHADOW, sh.get_rect().center,
                               r + SS)
            big.blit(sh, sh.get_rect(center=(bcx, bcy + SS + 1)))
            # Ball gradient (smoothshaded sphere).
            for i in range(r, 0, -1):
                t = 1 - i / r
                shade = (int(fill[0] * (1 - 0.35 * t) + 255 * 0.35 * t),
                         int(fill[1] * (1 - 0.35 * t) + 255 * 0.35 * t),
                         int(fill[2] * (1 - 0.35 * t) + 255 * 0.35 * t))
                pygame.draw.circle(big, shade, (bcx, bcy), i)
            # Dark outline.
            pygame.draw.circle(big, NAVY, (bcx, bcy), r, max(1, SS // 2))
            # Specular highlight (upper-left).
            pygame.draw.circle(big, (255, 255, 255, 200),
                               (bcx - r // 2, bcy - r // 2),
                               r // 3)
            # White inner disc — the typical "number panel" on a
            # lottery ball.
            pygame.draw.circle(big, WHITE, (bcx, bcy), int(r * 0.62))
            pygame.draw.circle(big, NAVY, (bcx, bcy),
                               int(r * 0.62), max(1, SS // 2))
            # Number.
            fnum = _font(int(r * 1.15))
            ntxt = fnum.render(num, True, NAVY)
            big.blit(ntxt, ntxt.get_rect(center=(bcx, bcy)))

    icon = _ss_paint(paint)
    surf.blit(icon, icon.get_rect(center=(cx, cy)))


def draw_l3_wheel(surf, cx, cy, pulse):
    """L3 — Wheel-of-fortune coin with 6 pie slices, chrome rim,
    pointer at 12 o'clock, "?" hub."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        # Wheel is circular; sized to fit landscape footprint.
        wheel_r = min(w, h) // 2 - 3 * SS
        bx = w // 2
        by = h // 2 + 1 * SS  # nudge down so pointer fits in frame
        # Drop shadow.
        sh = pygame.Surface((wheel_r * 2 + 4 * SS,
                             wheel_r * 2 + 4 * SS), pygame.SRCALPHA)
        pygame.draw.circle(sh, SHADOW, sh.get_rect().center,
                           wheel_r + SS)
        big.blit(sh, sh.get_rect(center=(bx, by + SS + 1)))

        # 6 wedges in the LOTTERY_TIERS palette.
        slice_cols = [
            GOLD_MID,         # JACKPOT
            RED,              # BUST
            TEAL,             # WIN
            CREAM,            # NOTHING
            ORANGE,           # BIG WIN
            (110, 130, 180),  # LOSS — muted slate-blue
        ]
        # Rotation driven by pulse so the wheel feels "spinning".
        rot = (pulse * 30) % 360
        # Draw wedges as polygons.
        n = len(slice_cols)
        for i, col in enumerate(slice_cols):
            a0 = math.radians(rot + i * (360 / n) - 90)
            a1 = math.radians(rot + (i + 1) * (360 / n) - 90)
            verts = [(bx, by)]
            steps = 8
            for s in range(steps + 1):
                a = a0 + (a1 - a0) * (s / steps)
                verts.append((bx + math.cos(a) * wheel_r,
                              by + math.sin(a) * wheel_r))
            pygame.draw.polygon(big, col, verts)
            # 1-SS spoke line.
            pygame.draw.line(big, NAVY, (bx, by),
                             (bx + math.cos(a0) * wheel_r,
                              by + math.sin(a0) * wheel_r),
                             max(1, SS // 2))

        # Chrome rim — outer ring with peg notches.
        pygame.draw.circle(big, CHROME, (bx, by), wheel_r + 2 * SS,
                           2 * SS)
        # 12 small dark notches around the rim.
        for i in range(12):
            a = math.radians(i * 30)
            nx = bx + math.cos(a) * (wheel_r + 2 * SS)
            ny = by + math.sin(a) * (wheel_r + 2 * SS)
            pygame.draw.circle(big, NAVY, (int(nx), int(ny)), SS)
        # Inner dark ring.
        pygame.draw.circle(big, NAVY, (bx, by), wheel_r,
                           max(1, SS // 2))

        # Centre hub — dark disc with chrome ring + cream "?".
        hub_r = int(wheel_r * 0.32)
        pygame.draw.circle(big, NAVY, (bx, by), hub_r)
        pygame.draw.circle(big, CHROME, (bx, by), hub_r,
                           max(1, SS // 2))
        fq = _font(int(hub_r * 1.6))
        qtxt = fq.render("?", True, CREAM)
        big.blit(qtxt, qtxt.get_rect(center=(bx, by)))

        # Pointer at 12 o'clock — slim dark triangle protruding above
        # the rim.
        pt_top = by - wheel_r - 3 * SS
        pt_w   = 3 * SS
        pygame.draw.polygon(big, NAVY, [
            (bx - pt_w, pt_top),
            (bx + pt_w, pt_top),
            (bx,        by - wheel_r + SS),
        ])
        pygame.draw.polygon(big, CHROME, [
            (bx - pt_w, pt_top),
            (bx + pt_w, pt_top),
            (bx,        by - wheel_r + SS),
        ], max(1, SS // 2))

    icon = _ss_paint(paint)
    surf.blit(icon, icon.get_rect(center=(cx, cy)))


def draw_l4_golden_ticket(surf, cx, cy, pulse):
    """L4 — Vertical golden ticket scroll. Gold gradient body, double
    border (dark-gold outer + chrome inner), perforation row,
    centred "?" emblem, red side margins, sparkle."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        # Ticket body — slightly taller-than-wide to feel "ticket-y".
        body_w = int(w * 0.62)
        body_h = h - 4 * SS
        body = pygame.Rect(0, 0, body_w, body_h)
        body.center = (w // 2, h // 2)
        # Drop shadow.
        sh = pygame.Surface((body.width + 4 * SS, body.height + 4 * SS),
                            pygame.SRCALPHA)
        pygame.draw.rect(sh, SHADOW, sh.get_rect(),
                         border_radius=3 * SS)
        big.blit(sh, sh.get_rect(center=(body.centerx,
                                          body.centery + SS + 1)))
        # Gold gradient fill.
        _v_gradient_rect(big, body, GOLD_HI, GOLD_LO,
                         radius=3 * SS)
        # Red side margins — thin vertical bands inside the body.
        margin = 3 * SS
        left_m = pygame.Rect(body.left + 2 * SS, body.top + 2 * SS,
                             margin, body.height - 4 * SS)
        right_m = pygame.Rect(body.right - 2 * SS - margin,
                              body.top + 2 * SS,
                              margin, body.height - 4 * SS)
        for r in (left_m, right_m):
            pygame.draw.rect(big, (180, 40, 50), r,
                             border_radius=SS)
        # Outer dark-gold stroke.
        pygame.draw.rect(big, STROKE, body, width=2 * SS,
                         border_radius=3 * SS)
        # Inner chrome stroke — inset 2 SS.
        inner = body.inflate(-4 * SS, -4 * SS)
        pygame.draw.rect(big, CHROME, inner, width=SS,
                         border_radius=2 * SS)
        # Perforation row — chrome dots along the top edge of the
        # inner rect.
        perf_y = inner.top + 4 * SS
        n_perf = 5
        for i in range(n_perf):
            t = (i + 0.5) / n_perf
            px = inner.left + int(inner.width * t)
            pygame.draw.circle(big, CHROME, (px, perf_y), SS)
            pygame.draw.circle(big, GOLD_DEEP, (px, perf_y),
                               SS, max(1, SS // 2))
        # Centre emblem — large cream "$" with subtle drop shadow.
        f_emblem = _font(int(body.height * 0.50))
        em_shadow = f_emblem.render("$", True, GOLD_DEEP)
        em        = f_emblem.render("$", True, CREAM)
        ec = (body.centerx, body.centery + 3 * SS)
        big.blit(em_shadow, em_shadow.get_rect(
            center=(ec[0] + SS, ec[1] + SS)))
        big.blit(em, em.get_rect(center=ec))
        # Corner sparkle at upper right.
        _sparkle(big, body.right - 5 * SS, body.top + 5 * SS, 3 * SS)
        # Tiny "TICKET" caption is too small to read at 56×42; skip.

    icon = _ss_paint(paint)
    # Light tilt so the ticket reads as alive.
    tilt = math.sin(pulse * 0.7) * 5
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_l5_jackpot_star(surf, cx, cy, pulse):
    """L5 — Multi-pointed gold star with "?" core. Cream radiating
    beams behind, chrome rim around the inner navy disc, confetti
    dots in the corners."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        bx, by = w // 2, h // 2
        # Background beams — 8 narrow cream rays behind the star.
        beam_len = min(w, h) // 2
        for i in range(8):
            ang = math.radians(i * 45 + (pulse * 6) % 45)
            x1 = bx + math.cos(ang) * beam_len * 1.05
            y1 = by + math.sin(ang) * beam_len * 1.05
            x2 = bx + math.cos(ang) * (beam_len * 0.25)
            y2 = by + math.sin(ang) * (beam_len * 0.25)
            # Tapered ray — draw 3 lines from thick to thin.
            for thick, alpha in ((3 * SS, 50), (2 * SS, 90),
                                  (SS, 140)):
                ray = pygame.Surface(big.get_size(), pygame.SRCALPHA)
                pygame.draw.line(ray, (255, 245, 200, alpha),
                                 (x1, y1), (x2, y2), thick)
                big.blit(ray, (0, 0))
        # 7-point gold star.
        star_r = int(min(w, h) * 0.40)
        star_inner = int(star_r * 0.46)
        pts = _star_polygon(bx, by, star_r, star_inner, 7,
                            rot_deg=(pulse * 4) % 360)
        # Gold fill with a soft gradient — emulate by overlaying 3
        # shrunken stars: deep → mid → hi.
        pygame.draw.polygon(big, GOLD_DEEP, pts)
        for shrink, col in ((0.92, GOLD_LO), (0.80, GOLD_MID),
                            (0.62, GOLD_HI)):
            inner_pts = _star_polygon(bx, by,
                                       int(star_r * shrink),
                                       int(star_inner * shrink),
                                       7,
                                       rot_deg=(pulse * 4) % 360)
            pygame.draw.polygon(big, col, inner_pts)
        # Dark stroke around outer star.
        pygame.draw.polygon(big, STROKE, pts, max(1, SS // 2))
        # Inner navy disc — the "?" badge.
        disc_r = int(star_r * 0.40)
        pygame.draw.circle(big, NAVY, (bx, by), disc_r)
        pygame.draw.circle(big, CHROME, (bx, by), disc_r,
                           max(1, SS // 2))
        fq = _font(int(disc_r * 1.8))
        qtxt = fq.render("?", True, CREAM)
        big.blit(qtxt, qtxt.get_rect(center=(bx, by)))
        # Confetti dots scattered in the corners.
        confetti_specs = [
            ( 4 * SS,  6 * SS,  RED),
            (w - 5 * SS, 8 * SS,  TEAL),
            ( 6 * SS, h - 6 * SS, MAGENTA),
            (w - 7 * SS, h - 5 * SS, ORANGE),
            (w // 2 - 18 * SS, h - 4 * SS, CYAN),
        ]
        for x, y, col in confetti_specs:
            pygame.draw.circle(big, col, (x, y), int(1.5 * SS))
            pygame.draw.circle(big, WHITE, (x, y), int(1.5 * SS),
                               max(1, SS // 3))

    icon = _ss_paint(paint)
    surf.blit(icon, icon.get_rect(center=(cx, cy)))


VARIANTS = [
    ("L1_foil_scratch",    draw_l1_foil_scratch,
     "L1: foil-bordered scratch card (polish of current)"),
    ("L2_balls",           draw_l2_balls,
     "L2: three numbered lottery balls cluster"),
    ("L3_wheel",           draw_l3_wheel,
     "L3: wheel-of-fortune coin with 6 wedges"),
    ("L4_golden_ticket",   draw_l4_golden_ticket,
     "L4: golden ticket scroll with $ emblem"),
    ("L5_jackpot_star",    draw_l5_jackpot_star,
     "L5: jackpot star burst with ? hub"),
]


# ── output ──────────────────────────────────────────────────────────────────

def _icon_zoom_png(draw_fn, label):
    """56×42 transparent icon centred, scaled 6× for review."""
    base = pygame.Surface((56, 42), pygame.SRCALPHA)
    draw_fn(base, 28, 21, pulse=1.6)
    big = pygame.transform.scale(base, (56 * 6, 42 * 6))
    pygame.draw.rect(big, (255, 215, 0), big.get_rect(), 2)
    return big


def _ingame_png(draw_fn, label):
    """Render the icon on a real gameplay frame so the user sees it
    at native pickup scale next to Pip."""
    world = build_world()
    frame = render_play_scene(world)
    icon_cx = int(world.bird.x) + 110
    icon_cy = int(world.bird.y)
    base = pygame.Surface((56, 42), pygame.SRCALPHA)
    draw_fn(base, 28, 21, pulse=1.6)
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

    # Contact sheet — 5 icons in a row with labels.
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
            "v5_powerups/docs/screenshots/lottery_icon_variants")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_ingame.png")


if __name__ == "__main__":
    main()
