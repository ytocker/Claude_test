"""Render 5 LOTTERY scratch-card design candidates. All five are
the foil-bordered scratch-card family (user picked L1 as the
direction); each varies the panel shape, decorative elements, and
composition while keeping the chrome perimeter + dark-gold inner
stroke + sparkle vocabulary. Painted at 6× supersample to a
56×42 footprint, smoothscaled down.

Each candidate is saved twice:
  * <label>.png         — icon centred on a transparent 56×42
                          surface scaled 6× to 336×252 for review
  * <label>_ingame.png  — composited onto a real gameplay frame
                          via build_world(), so the user can see
                          the icon in context

Plus a horizontal contact sheet `00_contact_sheet.png` with all 5.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_lottery_scratch_variants.py
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

from tools.render_helmet_side_view_variants import (
    build_world, render_play_scene, _label_band,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "lottery_scratch_variants")
os.makedirs(_OUT, exist_ok=True)

_FONT_PATH = str(pathlib.Path(_REPO) / "game" / "assets"
                 / "LiberationSans-Bold.ttf")


# ── shared scratch-card palette ─────────────────────────────────────────────
GOLD_HI   = (255, 230, 110)
GOLD_MID  = (250, 200,  70)
GOLD_LO   = (220, 175,  50)
GOLD_DEEP = (180, 130,  20)
STROKE    = (110,  75,  10)
CHROME    = (225, 225, 232)
CHROME_LO = (160, 165, 180)
SILVER_HI = (245, 245, 252)
SILVER_LO = (175, 180, 195)
CREAM     = (255, 245, 200)
NAVY      = ( 30,  40,  80)
WHITE     = (255, 255, 255)
RED       = (190,  40,  55)
RED_HI    = (230,  80,  90)
SHADOW    = (  0,   0,   0,  90)


# ── shared helpers ──────────────────────────────────────────────────────────

def _ss_paint(paint_fn, native_w=56, native_h=42, ss=6):
    big = pygame.Surface((native_w * ss, native_h * ss), pygame.SRCALPHA)
    paint_fn(big, ss)
    return pygame.transform.smoothscale(big, (native_w, native_h))


def _font(size):
    return pygame.font.Font(_FONT_PATH, size)


def _v_gradient_rect(surf, rect, top_col, bot_col, radius=0):
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
    pts = []
    for i in range(points * 2):
        ang = math.radians(rot_deg - 90 + i * (180.0 / points))
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    return pts


def _sparkle(surf, cx, cy, r, colour=CREAM):
    pts = _star_polygon(cx, cy, r, r * 0.32, 4)
    pygame.draw.polygon(surf, colour, pts)


def _dashed_rect(surf, rect, colour, dash, gap, width):
    """Walk the rect perimeter and stamp dashed segments."""
    def seg(p0, p1):
        x0, y0 = p0
        x1, y1 = p1
        L = math.hypot(x1 - x0, y1 - y0)
        if L <= 0:
            return
        dx = (x1 - x0) / L
        dy = (y1 - y0) / L
        t = 0.0
        while t < L:
            t2 = min(t + dash, L)
            pygame.draw.line(surf, colour,
                             (x0 + dx * t,  y0 + dy * t),
                             (x0 + dx * t2, y0 + dy * t2),
                             width)
            t += dash + gap
    seg((rect.left, rect.top), (rect.right, rect.top))
    seg((rect.right, rect.top), (rect.right, rect.bottom))
    seg((rect.right, rect.bottom), (rect.left, rect.bottom))
    seg((rect.left, rect.bottom), (rect.left, rect.top))


def _gold_card_base(big, SS):
    """Paint the standard gold card body + sheen + chrome perimeter
    + dashed dark-gold inner stroke. Returns (card_rect, inner_rect)
    for the variant to fill its content into."""
    w, h = big.get_width(), big.get_height()
    card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
    # Drop shadow.
    sh = pygame.Surface((card.width + 4 * SS, card.height + 4 * SS),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, SHADOW, sh.get_rect(),
                     border_radius=4 * SS)
    big.blit(sh, sh.get_rect(center=(card.centerx,
                                      card.centery + SS + 1)))
    # Gradient body.
    _v_gradient_rect(big, card, GOLD_HI, GOLD_LO, radius=4 * SS)
    # Top sheen.
    hi_h = card.height // 3
    hi = pygame.Surface((card.width, hi_h), pygame.SRCALPHA)
    for y in range(hi_h):
        a = int(110 * (1.0 - y / hi_h))
        pygame.draw.line(hi, (255, 250, 220, a),
                         (0, y), (hi.get_width(), y))
    big.blit(hi, (card.x, card.y))
    # Chrome outer perimeter (2 SS).
    pygame.draw.rect(big, CHROME, card, width=2 * SS,
                     border_radius=4 * SS)
    # Dashed dark-gold inner stroke.
    inner = card.inflate(-4 * SS, -4 * SS)
    _dashed_rect(big, inner, STROKE, dash=4 * SS, gap=3 * SS,
                 width=max(1, SS // 2))
    return card, inner


def _silver_panel(big, rect, radius=None):
    """Standard silver scratch-panel fill with cross-hatch + navy
    outline."""
    if radius is None:
        radius = max(1, rect.height // 8)
    _v_gradient_rect(big, rect, SILVER_HI, SILVER_LO, radius=radius)
    # Cross-hatch.
    for off in range(-rect.height, rect.width, max(8, rect.height // 6)):
        x0 = rect.left + off
        x1 = x0 + rect.height
        pygame.draw.line(big, (180, 185, 200, 90),
                         (x0, rect.top),
                         (x1, rect.bottom),
                         max(1, rect.height // 60))
    pygame.draw.rect(big, NAVY, rect, width=max(1, rect.height // 18),
                     border_radius=radius)


# ── 5 scratch-card variants ─────────────────────────────────────────────────

def draw_c1_classic_seal(surf, cx, cy, pulse):
    """C1 — L1 polished further: a starburst foil seal in the
    upper-right corner replacing the small sparkle, plus a "PRIZE"
    micro-stamp at the lower-left."""

    def paint(big, SS):
        card, inner = _gold_card_base(big, SS)
        # Scratch panel — slightly narrower than L1 so the seal +
        # stamp have room.
        panel = pygame.Rect(0, 0,
                            card.width - 16 * SS,
                            card.height - 18 * SS)
        panel.center = (card.centerx - 2 * SS, card.centery + 2 * SS)
        _silver_panel(big, panel, radius=2 * SS)
        # "? ? ?" — bold navy with a 1-SS cream highlight above.
        f = _font(int(panel.height * 0.78))
        text = f.render("? ? ?", True, NAVY)
        hl   = f.render("? ? ?", True, CREAM)
        tr = text.get_rect(center=panel.center)
        big.blit(hl, hl.get_rect(center=(tr.centerx, tr.centery - SS)))
        big.blit(text, tr)
        # Starburst foil seal at upper-right corner — a small 8-point
        # red disc with cream star + "★" suggesting an official stamp.
        seal_r = 6 * SS
        scx = card.right - 7 * SS
        scy = card.top + 7 * SS
        burst_pts = _star_polygon(scx, scy, seal_r, seal_r * 0.7, 8)
        pygame.draw.polygon(big, RED_HI, burst_pts)
        pygame.draw.polygon(big, STROKE, burst_pts, max(1, SS // 2))
        pygame.draw.circle(big, CREAM, (scx, scy), int(seal_r * 0.55))
        _sparkle(big, scx, scy, int(seal_r * 0.45), colour=RED)
        # "PRIZE" micro-stamp at lower-left: small dark plaque with
        # cream serif text.
        stamp = pygame.Rect(0, 0, 16 * SS, 4 * SS)
        stamp.midleft = (card.left + 5 * SS, card.bottom - 5 * SS)
        pygame.draw.rect(big, NAVY, stamp, border_radius=SS)
        pygame.draw.rect(big, CHROME, stamp, width=max(1, SS // 2),
                         border_radius=SS)
        fst = _font(int(stamp.height * 0.85))
        sttxt = fst.render("PRIZE", True, CREAM)
        big.blit(sttxt, sttxt.get_rect(center=stamp.center))

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 6
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_c2_triple_cell(surf, cx, cy, pulse):
    """C2 — Triple-cell match-3 scratch ticket. Three small silver
    panels in a row, each with a single "?". Classic real-world
    scratch-ticket layout."""

    def paint(big, SS):
        card, inner = _gold_card_base(big, SS)
        # 3 cells in a horizontal row.
        cell_w = (inner.width - 6 * SS) // 3
        cell_h = inner.height - 10 * SS
        gap_x  = (inner.width - 3 * cell_w) // 2
        # Header strip — small red "MATCH 3" band at the top of the
        # inner area.
        header = pygame.Rect(inner.left + 2 * SS, inner.top + SS,
                             inner.width - 4 * SS, 4 * SS)
        pygame.draw.rect(big, RED, header, border_radius=SS)
        pygame.draw.rect(big, STROKE, header,
                         width=max(1, SS // 2),
                         border_radius=SS)
        fh = _font(int(header.height * 0.85))
        ht = fh.render("MATCH 3", True, CREAM)
        big.blit(ht, ht.get_rect(center=header.center))

        # 3 cells below the header.
        y0 = header.bottom + 2 * SS
        for i in range(3):
            x0 = inner.left + i * (cell_w + gap_x)
            cell = pygame.Rect(x0, y0, cell_w, cell_h - 6 * SS)
            _silver_panel(big, cell, radius=2 * SS)
            fq = _font(int(cell.height * 0.85))
            qtxt = fq.render("?", True, NAVY)
            hl   = fq.render("?", True, CREAM)
            qr = qtxt.get_rect(center=cell.center)
            big.blit(hl, hl.get_rect(center=(qr.centerx,
                                              qr.centery - SS)))
            big.blit(qtxt, qr)
        # Two small sparkles at the bottom corners.
        _sparkle(big, card.left + 5 * SS, card.bottom - 4 * SS, 2 * SS)
        _sparkle(big, card.right - 5 * SS, card.bottom - 4 * SS, 2 * SS)

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 5
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_c3_diamond_panel(surf, cx, cy, pulse):
    """C3 — Rhombus/diamond-shaped scratch panel rotated 45° in the
    centre, with 4 corner sparkles arranged like card pips."""

    def paint(big, SS):
        card, inner = _gold_card_base(big, SS)
        # Diamond panel — paint a square panel on a sub-surface then
        # rotate 45°.
        d_side = int(inner.height * 0.96)
        sub = pygame.Surface((d_side + 6 * SS, d_side + 6 * SS),
                              pygame.SRCALPHA)
        panel = pygame.Rect(0, 0, d_side, d_side)
        panel.center = (sub.get_width() // 2, sub.get_height() // 2)
        _silver_panel(sub, panel, radius=2 * SS)
        # "?" centred on the unrotated panel.
        fq = _font(int(panel.height * 0.62))
        qtxt = fq.render("?", True, NAVY)
        hl   = fq.render("?", True, CREAM)
        qr = qtxt.get_rect(center=panel.center)
        sub.blit(hl, hl.get_rect(center=(qr.centerx,
                                           qr.centery - SS)))
        sub.blit(qtxt, qr)
        # Rotate 45° to form a diamond.
        rotated = pygame.transform.rotate(sub, 45)
        big.blit(rotated, rotated.get_rect(center=card.center))

        # 4 sparkle pips at the 4 corners of the card.
        margin = 5 * SS
        for px, py in (
            (card.left + margin,  card.top + margin),
            (card.right - margin, card.top + margin),
            (card.left + margin,  card.bottom - margin),
            (card.right - margin, card.bottom - margin),
        ):
            _sparkle(big, px, py, 3 * SS)

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_c4_lucky_banner(surf, cx, cy, pulse):
    """C4 — Red "LUCKY" arch banner across the top, larger scratch
    panel below with "$ ?" and stars."""

    def paint(big, SS):
        card, inner = _gold_card_base(big, SS)
        # Banner — red rounded rect across the top inside `inner`,
        # with small triangular notches at the ends (ribbon tails).
        banner = pygame.Rect(inner.left + 4 * SS, inner.top + SS,
                             inner.width - 8 * SS, 7 * SS)
        # Gradient red.
        _v_gradient_rect(big, banner, RED_HI, RED, radius=2 * SS)
        pygame.draw.rect(big, STROKE, banner,
                         width=max(1, SS // 2),
                         border_radius=2 * SS)
        # Ribbon notches at the ends.
        notch_w = 2 * SS
        pygame.draw.polygon(big, RED, [
            (banner.left, banner.top),
            (banner.left - notch_w, banner.centery),
            (banner.left, banner.bottom),
        ])
        pygame.draw.polygon(big, RED, [
            (banner.right, banner.top),
            (banner.right + notch_w, banner.centery),
            (banner.right, banner.bottom),
        ])
        fb = _font(int(banner.height * 0.92))
        bt = fb.render("LUCKY", True, CREAM)
        big.blit(bt, bt.get_rect(center=banner.center))

        # Scratch panel below the banner.
        panel = pygame.Rect(inner.left + 2 * SS,
                            banner.bottom + 2 * SS,
                            inner.width - 4 * SS,
                            inner.bottom - banner.bottom - 4 * SS)
        _silver_panel(big, panel, radius=2 * SS)
        # "$ ?" — paired emblem.
        ftxt = _font(int(panel.height * 0.85))
        txt = ftxt.render("$ ?", True, NAVY)
        hl  = ftxt.render("$ ?", True, CREAM)
        tr = txt.get_rect(center=panel.center)
        big.blit(hl, hl.get_rect(center=(tr.centerx,
                                          tr.centery - SS)))
        big.blit(txt, tr)
        # 2 small stars at the panel corners.
        _sparkle(big, panel.left + 3 * SS, panel.top + 3 * SS,
                 int(SS * 1.8))
        _sparkle(big, panel.right - 3 * SS, panel.bottom - 3 * SS,
                 int(SS * 1.8))

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 5
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_c5_coin_sealed(surf, cx, cy, pulse):
    """C5 — Gold coin seal on the left with "$", scratch panel on
    the right with "?", small ribbon corner at lower-right."""

    def paint(big, SS):
        card, inner = _gold_card_base(big, SS)
        # Coin seal — left-hand side circle, gold with chrome rim.
        coin_r = int(inner.height * 0.42)
        coin_cx = inner.left + coin_r + 2 * SS
        coin_cy = inner.centery
        # Soft shadow.
        pygame.draw.circle(big, (0, 0, 0, 60),
                           (coin_cx, coin_cy + SS + 1),
                           coin_r + SS)
        # Gold gradient sphere — 3 concentric circles for shading.
        for shrink, col in ((1.00, GOLD_DEEP),
                            (0.86, GOLD_LO),
                            (0.70, GOLD_MID),
                            (0.52, GOLD_HI)):
            pygame.draw.circle(big, col, (coin_cx, coin_cy),
                               int(coin_r * shrink))
        # Chrome rim.
        pygame.draw.circle(big, CHROME, (coin_cx, coin_cy),
                           coin_r, max(1, SS // 2))
        pygame.draw.circle(big, STROKE, (coin_cx, coin_cy),
                           coin_r, max(1, SS // 3))
        # "$" emblem on the coin.
        fc = _font(int(coin_r * 1.6))
        ctxt = fc.render("$", True, STROKE)
        hl   = fc.render("$", True, CREAM)
        cr = ctxt.get_rect(center=(coin_cx, coin_cy))
        big.blit(hl, hl.get_rect(center=(cr.centerx,
                                           cr.centery - SS)))
        big.blit(ctxt, cr)

        # Scratch panel on the right side — taller than wide.
        panel_left = coin_cx + coin_r + 3 * SS
        panel = pygame.Rect(panel_left,
                            inner.top + 2 * SS,
                            inner.right - panel_left,
                            inner.height - 4 * SS)
        _silver_panel(big, panel, radius=2 * SS)
        # "?" centred.
        fq = _font(int(panel.height * 0.78))
        qtxt = fq.render("?", True, NAVY)
        hl2  = fq.render("?", True, CREAM)
        qr = qtxt.get_rect(center=panel.center)
        big.blit(hl2, hl2.get_rect(center=(qr.centerx,
                                             qr.centery - SS)))
        big.blit(qtxt, qr)

        # Small red ribbon corner at lower-right (triangle flap).
        rb = [
            (card.right - 8 * SS, card.bottom - 2 * SS),
            (card.right - 2 * SS, card.bottom - 2 * SS),
            (card.right - 2 * SS, card.bottom - 8 * SS),
        ]
        pygame.draw.polygon(big, RED, rb)
        pygame.draw.polygon(big, STROKE, rb, max(1, SS // 2))
        # Small star on the ribbon corner.
        _sparkle(big, card.right - 4 * SS, card.bottom - 4 * SS,
                 int(SS * 1.4), colour=CREAM)

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 5
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


VARIANTS = [
    ("C1_classic_seal",   draw_c1_classic_seal,
     "C1: foil seal + PRIZE stamp polish of L1"),
    ("C2_triple_cell",    draw_c2_triple_cell,
     "C2: triple-cell match-3 with MATCH 3 banner"),
    ("C3_diamond_panel",  draw_c3_diamond_panel,
     "C3: diamond scratch panel + 4 corner pip stars"),
    ("C4_lucky_banner",   draw_c4_lucky_banner,
     "C4: red LUCKY arch banner + $ ? panel"),
    ("C5_coin_sealed",    draw_c5_coin_sealed,
     "C5: gold $ coin seal + side scratch panel"),
]


# ── output ──────────────────────────────────────────────────────────────────

def _icon_zoom_png(draw_fn, label):
    base = pygame.Surface((56, 42), pygame.SRCALPHA)
    draw_fn(base, 28, 21, pulse=1.6)
    big = pygame.transform.scale(base, (56 * 6, 42 * 6))
    pygame.draw.rect(big, (255, 215, 0), big.get_rect(), 2)
    return big


def _ingame_png(draw_fn, label):
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
            "v5_powerups/docs/screenshots/lottery_scratch_variants")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_ingame.png")


if __name__ == "__main__":
    main()
