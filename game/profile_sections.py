"""Renderers for the Profile's first-level sections (STATS / SHAME / ARCADE)
and the pill-strip section switcher.

Ported from the locked round-3 layout (`tools/profile_layout_mock_r3.py`) but
driven by live data: the STATS modules read store_data stats through
profile_stats, the SHAME grid reads the shame badge registry, and the ARCADE
curios expose tap targets. GEAR (loadout + cosmetics grid) stays in profile.py.

All drawing reuses the shipped "Obsidian & Gold" primitives so the four sections
read as one product. The shared layout law is C's contract: fixed-height modules
spaced by exactly GAP, the stack centred in [COL_TOP, COL_BOT]; SHAME (a grid)
and ARCADE (equal curios) inherit the same GAP + centring.
"""
from __future__ import annotations

import math

import pygame

from game.config import W, H
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP
from game.draw import lerp_color, rounded_rect
from game.store import (
    _vgrad_panel, _drop_shadow, _gem, _gradient_text, _soft_glow, _gold_rule,
    _OBS_TOP, _OBS_BOT,
)
from game import profile_stats as ps
from game import shame as shame_mod
from game import profile_art

# ── shared layout contract (matches the locked mock) ─────────────────────────
SIDE = 12
SWITCH_Y = 48
SWITCH_H = 34
GAP = 14
COL_TOP = 78
BACK_CY = H - 26
COL_BOT = BACK_CY - 28

_HEADER = (255, 226, 150)
_NEMESIS = (236, 86, 64)
_NEMESIS_DEEP = (150, 36, 28)
_BRONZE_TOP = (120, 86, 52)
_BRONZE_BOT = (70, 48, 28)

SECTIONS = ("GEAR", "STATS", "SHAME", "ARCADE")


# ── small shared helpers ─────────────────────────────────────────────────────

def _panel(surf, rect, radius=13, rim=True, top=_OBS_TOP, bot=_OBS_BOT):
    _drop_shadow(surf, rect, radius, blur=6, alpha=130)
    surf.blit(_vgrad_panel(rect.w, rect.h, radius, top, bot, 252), rect.topleft)
    if rim:
        pygame.draw.rect(surf, (*_GOLD_DEEP, 200), rect.inflate(-6, -6),
                         width=2, border_radius=max(2, radius - 4))
        pygame.draw.rect(surf, (*_GOLD_BRIGHT, 150), rect, width=1,
                         border_radius=radius)


def _sheen(surf, rect, h=14):
    s = pygame.Surface((rect.w - 10, h), pygame.SRCALPHA)
    for y in range(h):
        pygame.draw.line(s, (255, 255, 255, int(28 * (1 - y / h))),
                         (0, y), (rect.w - 10, y))
    surf.blit(s, (rect.x + 5, rect.y + 4))


def _cap(surf, cx, y, txt, size=10, col=_GOLD_PALE, alpha=210):
    img = _font(size, True).render(txt, True, col)
    img.set_alpha(alpha)
    surf.blit(img, img.get_rect(center=(cx, y)))


def _module_header(surf, x, y, txt, size=9):
    f = _font(size, True)
    sh = f.render(txt, True, (10, 8, 4))
    sh.set_alpha(150)
    surf.blit(sh, (x + 1, y - sh.get_height() // 2 + 1))
    img = f.render(txt, True, _HEADER)
    surf.blit(img, (x, y - img.get_height() // 2))


def _module_rule(surf, y):
    _gold_rule(surf, SIDE + 4, W - SIDE - 4, y, peak=70)


def _mini_glyph(surf, kind, cx, cy, col, scale=1.0):
    if kind == 0:      # gear
        r = int(5 * scale)
        pygame.draw.circle(surf, col, (cx, cy), r, 2)
        for a in range(0, 360, 60):
            ra = math.radians(a)
            pygame.draw.line(surf, col,
                             (cx + r * math.cos(ra), cy + r * math.sin(ra)),
                             (cx + (r + 3) * math.cos(ra),
                              cy + (r + 3) * math.sin(ra)), 2)
    elif kind == 1:    # bar-chart
        for k, hh in enumerate((4, 8, 6)):
            pygame.draw.rect(surf, col, (cx - 7 + k * 5, cy + 5 - hh, 3, hh))
    elif kind == 2:    # skull
        r = int(5 * scale)
        pygame.draw.circle(surf, col, (cx, cy - 1), r, 2)
        pygame.draw.circle(surf, col, (cx - 2, cy - 1), 1)
        pygame.draw.circle(surf, col, (cx + 2, cy - 1), 1)
        pygame.draw.line(surf, col, (cx - 2, cy + 4), (cx + 2, cy + 4), 2)
    else:              # star
        pts = []
        for k in range(10):
            rr = (7 if k % 2 == 0 else 3) * scale
            a = math.radians(-90 + k * 36)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        pygame.draw.polygon(surf, col, pts, 1)


# ── number formatting for the stat tiles ─────────────────────────────────────

def _compact(n) -> str:
    n = int(n)
    if n < 10000:
        return f"{n:,}"
    if n < 1_000_000:
        return f"{n / 1000:.1f}".rstrip("0").rstrip(".") + "k"
    return f"{n / 1_000_000:.1f}".rstrip("0").rstrip(".") + "m"


def _clock(seconds) -> str:
    s = max(0, int(seconds))
    return f"{s // 60}:{s % 60:02d}"


def _hours(seconds) -> str:
    s = max(0, int(seconds))
    if s >= 3600:
        return f"{s // 3600}h"
    if s >= 60:
        return f"{s // 60}m"
    return f"{s}s"


# ── section switcher (returns the four pill hit-rects) ────────────────────────

def draw_switcher(surf, active: int) -> "list[pygame.Rect]":
    n = len(SECTIONS)
    gap = 6
    total = W - 2 * SIDE
    pw = (total - gap * (n - 1)) // n
    x = SIDE
    rects: "list[pygame.Rect]" = []
    for i, lab in enumerate(SECTIONS):
        r = pygame.Rect(x, SWITCH_Y, pw, SWITCH_H)
        rects.append(r)
        on = (i == active)
        if on:
            _soft_glow(surf, r.centerx, r.centery, 24, (255, 200, 90), 36, layers=4)
            surf.blit(_vgrad_panel(r.w, r.h, 11, (255, 220, 128),
                                   (228, 160, 44), 255), r.topleft)
            pygame.draw.rect(surf, (255, 246, 210), r, width=1, border_radius=11)
            pygame.draw.rect(surf, (*_GOLD_DEEP, 210), r.inflate(-4, -4),
                             width=1, border_radius=9)
            col = (44, 28, 6)
            _mini_glyph(surf, i, r.centerx, r.y + 10, col)
            t = _font(10, True).render(lab, True, col)
            surf.blit(t, t.get_rect(center=(r.centerx, r.bottom - 9)))
        else:
            surf.blit(_vgrad_panel(r.w, r.h, 11, (52, 44, 64), (30, 25, 44),
                                   245), r.topleft)
            pygame.draw.rect(surf, (148, 126, 92), r, width=1, border_radius=11)
            gcol = (206, 188, 150)
            gx = r.x + 13
            _mini_glyph(surf, i, gx, r.centery, gcol, scale=0.8)
            t = _font(9, True).render(lab, True, gcol)
            surf.blit(t, t.get_rect(midleft=(gx + 11, r.centery)))
        x += pw + gap
    return rects


# ── STATS ────────────────────────────────────────────────────────────────────

def _pb_tile(surf, rect, label, value):
    _panel(surf, rect, radius=11)
    _sheen(surf, rect, 10)
    vsize = 23 if rect.h >= 50 else 21
    _gradient_text(surf, value, _font(vsize, True),
                   (rect.centerx, rect.centery - 5),
                   (255, 244, 196), (236, 170, 60), shadow=True)
    _cap(surf, rect.centerx, rect.bottom - 11, label, size=9, col=_GOLD_PALE,
         alpha=220)


def _counter_row(surf, rect, lifetime):
    _panel(surf, rect, radius=11)
    _sheen(surf, rect, 8)
    n = len(lifetime)
    seg = rect.w / n
    for i, (lab, val) in enumerate(lifetime):
        cx = int(rect.x + seg * (i + 0.5))
        if i > 0:
            dx = int(rect.x + seg * i)
            pygame.draw.line(surf, (*_GOLD_DEEP, 120),
                             (dx, rect.y + 8), (dx, rect.bottom - 8), 1)
        vimg = _font(15, True).render(val, True, _GOLD_BRIGHT)
        surf.blit(vimg, vimg.get_rect(center=(cx, rect.y + 15)))
        _cap(surf, cx, rect.bottom - 10, lab, size=8, col=_GOLD_PALE, alpha=195)


def _engraved_strip(surf, rect, txt):
    surf.blit(_vgrad_panel(rect.w, rect.h, 5, (44, 36, 22), (28, 22, 12), 255),
              rect.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 180), rect, width=1, border_radius=5)
    sh = _font(9, True).render(txt, True, (16, 12, 6))
    surf.blit(sh, sh.get_rect(center=(rect.centerx + 1, rect.centery + 1)))
    hd = _font(9, True).render(txt, True, _HEADER)
    surf.blit(hd, hd.get_rect(center=rect.center))


def _safety_board(surf, rect, days_txt):
    plate = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        c = lerp_color((92, 96, 104), (54, 56, 64), y / max(1, rect.h - 1))
        pygame.draw.line(plate, (*c, 255), (0, y), (rect.w, y))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=8)
    plate.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    _drop_shadow(surf, rect, 9, blur=6, alpha=130)
    surf.blit(plate, rect.topleft)
    pygame.draw.rect(surf, (30, 30, 36), rect, width=2, border_radius=8)
    pygame.draw.rect(surf, (140, 144, 152), rect.inflate(-4, -4), width=1,
                     border_radius=6)
    for rx, ry in ((rect.x + 8, rect.y + 8), (rect.right - 8, rect.y + 8),
                   (rect.x + 8, rect.bottom - 8), (rect.right - 8, rect.bottom - 8)):
        pygame.draw.circle(surf, (40, 40, 46), (rx, ry), 3)
        pygame.draw.circle(surf, (170, 174, 182), (rx, ry), 3, 1)

    cap = pygame.Rect(rect.x + 14, rect.y + 10, rect.w - 28, 18)
    _engraved_strip(surf, cap, "DAYS SINCE LAST DIGNIFIED FLIGHT")

    win = pygame.Rect(rect.centerx - 44, cap.bottom + 10, 88,
                      rect.bottom - cap.bottom - 20)
    surf.blit(_vgrad_panel(win.w, win.h, 6, (10, 12, 10), (4, 6, 4), 255),
              win.topleft)
    pygame.draw.rect(surf, (0, 0, 0), win, width=2, border_radius=6)
    led = _NEMESIS
    _soft_glow(surf, win.centerx, win.centery, 20, led, 56, layers=4)
    nf = _font(28, True)
    cw = win.w // 2
    for k, ch in enumerate(days_txt[:2]):
        cell = pygame.Rect(win.x + 2 + k * cw, win.y + 3, cw - 3, win.h - 6)
        surf.blit(_vgrad_panel(cell.w, cell.h, 3, (22, 26, 22), (8, 10, 8), 255),
                  cell.topleft)
        pygame.draw.line(surf, (0, 0, 0), (cell.x, cell.centery),
                         (cell.right, cell.centery), 1)
        d = nf.render(ch, True, led)
        surf.blit(d, d.get_rect(center=cell.center))


def _histogram(surf, rect, deaths, labels, nemesis_pos, nemesis_label):
    _panel(surf, rect, radius=11)
    _sheen(surf, rect, 8)
    _module_header(surf, rect.x + 12, rect.y + 13, "WHERE YOU DIE", size=9)

    if nemesis_label:
        tag = _font(8, True).render(nemesis_label, True, (255, 232, 224))
        chip = pygame.Rect(rect.right - tag.get_width() - 18, rect.y + 6,
                           tag.get_width() + 10, 15)
        _soft_glow(surf, chip.centerx, chip.centery, 12, _NEMESIS, 40, layers=3)
        surf.blit(_vgrad_panel(chip.w, chip.h, 4, (220, 70, 52), _NEMESIS_DEEP,
                               255), chip.topleft)
        pygame.draw.rect(surf, (255, 170, 150), chip, width=1, border_radius=4)
        surf.blit(tag, tag.get_rect(center=chip.center))

    top = rect.y + 28
    plot = pygame.Rect(rect.x + 12, top, rect.w - 24, rect.bottom - top - 16)
    if not deaths or max(deaths) <= 0:
        _cap(surf, rect.centerx, plot.centery, "NO CRASHES LOGGED YET",
             size=11, col=_GOLD_PALE, alpha=180)
        _cap(surf, rect.centerx, plot.centery + 16, "go get some",
             size=8, col=(150, 142, 158), alpha=170)
        return
    n = len(deaths)
    mx = max(deaths)
    bw = plot.w / n
    base = plot.bottom
    pygame.draw.line(surf, (*_GOLD_DEEP, 120), (plot.x, base),
                     (plot.right, base), 1)
    for i, v in enumerate(deaths):
        bh = int((v / mx) * (plot.h - 4))
        bx = int(plot.x + bw * i + 1)
        br = pygame.Rect(bx, base - bh, max(1, int(bw) - 2), bh)
        if i == nemesis_pos:
            _soft_glow(surf, br.centerx, br.centery, 14, _NEMESIS, 60, layers=3)
            surf.blit(_vgrad_panel(br.w, max(2, br.h), 2, (240, 100, 82),
                                   _NEMESIS_DEEP, 255), br.topleft)
            inner = pygame.Rect(0, 0, max(1, br.w - 4), br.h)
            inner.midbottom = br.midbottom
            pygame.draw.rect(surf, (255, 214, 200), inner)
            pygame.draw.rect(surf, (255, 190, 170), br, width=1)
        else:
            surf.blit(_vgrad_panel(br.w, max(2, br.h), 2, (236, 190, 96),
                                   (150, 110, 40), 245), br.topleft)
        if i < len(labels):
            nimg = _font(6, True).render(str(labels[i]), True, (172, 152, 108))
            surf.blit(nimg, nimg.get_rect(center=(br.centerx, base + 7)))


def _histogram_window(stats):
    """Pick a 14-bar window over the death histogram that always includes the
    nemesis bar, with per-bar labels (= the pillar you died at) and the nemesis
    position within the window."""
    hist = [int(x) for x in (stats.get("death_pillar_histogram") or [])]
    if not hist:
        return [], [], None, None
    g = ps.gerald(stats)
    center = g["pillar"] if g else max(range(len(hist)), key=lambda i: hist[i])
    span = 14
    start = max(0, min(center - span // 2, max(0, len(hist) - span)))
    window = hist[start:start + span]
    while len(window) < span:
        window.append(0)
    labels = [start + k + 1 for k in range(span)]
    nem_pos = (g["pillar"] - start) if (g and 0 <= g["pillar"] - start < span) else None
    nem_label = f"NEMESIS  #{g['pillar'] + 1}" if g else None
    return window, labels, nem_pos, nem_label


def draw_stats(surf, t, stats):
    best_nm = int(stats.get("best_near_misses", 0))
    pb = [("BEST SCORE", _compact(stats.get("best_score", 0))),
          ("BEST PILLARS", _compact(stats.get("best_pillars", 0))),
          ("LONGEST FLIGHT", _clock(stats.get("best_time_s", 0))),
          ("BEST NEAR-MISS", f"x{best_nm}")]
    lifetime = [("RUNS", _compact(stats.get("runs_played", 0))),
                ("TIME ALOFT", _hours(stats.get("total_time_s", 0))),
                ("PILLARS", _compact(stats.get("total_pillars", 0))),
                ("COINS", _compact(stats.get("total_coins_earned", 0)))]
    dsd = ps.days_since_dignified(stats)
    days_txt = "--" if dsd is None else f"{min(dsd, 99):02d}"
    deaths, labels, nem_pos, nem_label = _histogram_window(stats)

    tile_h, count_h, board_h, hist_h = 50, 40, 82, 132
    pb_h = 2 * tile_h + 6
    stack_h = pb_h + count_h + board_h + hist_h + GAP * 3
    y = COL_TOP + max(0, (COL_BOT - COL_TOP - stack_h) // 2)

    tw = (W - 2 * SIDE - 8) // 2
    for i, (lab, val) in enumerate(pb):
        r = pygame.Rect(SIDE + (i % 2) * (tw + 8), y + (i // 2) * (tile_h + 6),
                        tw, tile_h)
        _pb_tile(surf, r, lab, val)
    y += pb_h + GAP

    _counter_row(surf, pygame.Rect(SIDE, y, W - 2 * SIDE, count_h), lifetime)
    y += count_h + GAP
    _module_rule(surf, y - GAP // 2)
    _safety_board(surf, pygame.Rect(SIDE, y, W - 2 * SIDE, board_h), days_txt)
    y += board_h + GAP
    _module_rule(surf, y - GAP // 2)
    _histogram(surf, pygame.Rect(SIDE, y, W - 2 * SIDE, hist_h),
               deaths, labels, nem_pos, nem_label)


# ── SHAME ────────────────────────────────────────────────────────────────────

# shame badge id -> glyph kind in profile_art._glyph
_GLYPH_FOR = {
    "goose_egg": "egg", "icarus": "icarus", "hummingbird": "humming",
    "early_checkout": "stopwatch", "denial": "denial", "habit": "loop",
    "kfc_incident": "fry", "scrooge": "scrooge", "the_49er": "tomb",
    "ghost_wall": "ghostwall", "frequent_flyer": "oneway",
}


def _badge_cell(surf, rect, b, stats):
    earned = b.earned(stats)
    top, bot = ((46, 36, 30), (26, 20, 16)) if earned else ((34, 32, 40), (20, 18, 24))
    _drop_shadow(surf, rect, 11, blur=5, alpha=110)
    surf.blit(_vgrad_panel(rect.w, rect.h, 11, top, bot, 252), rect.topleft)
    pygame.draw.rect(surf, (150, 116, 78) if earned else (88, 92, 110), rect,
                     width=1, border_radius=11)
    profile_art.shame_badge(surf, rect.centerx, rect.y + 26, 20, b.tier,
                            _GLYPH_FOR.get(b.id, "denial"), not earned)
    name = b.name.upper()
    f = _font(7, True)
    while f.size(name)[0] > rect.w - 6 and " " in name:
        name = name.rsplit(" ", 1)[0]
    lc = (236, 208, 158) if earned else (152, 162, 186)
    _cap(surf, rect.centerx, rect.y + 52, name, size=7, col=lc,
         alpha=235 if earned else 190)
    if earned:
        return
    cur, tgt = b.progress(stats)
    bar = pygame.Rect(rect.x + 10, rect.bottom - 11, rect.w - 20, 5)
    rounded_rect(surf, bar, 2, (22, 20, 26))
    frac = 0 if tgt <= 0 else max(0.0, min(1.0, cur / tgt))
    if frac > 0:
        rounded_rect(surf, pygame.Rect(bar.x, bar.y, max(2, int(bar.w * frac)),
                                       bar.h), 2, _GOLD_DEEP)
    _cap(surf, rect.centerx, bar.y - 6, f"{cur} / {tgt}", size=7,
         col=(150, 142, 158), alpha=200)


def draw_shame(surf, t, stats):
    chip_txt = shame_mod.current_title(stats).upper()
    cf = _font(11, True)
    _cap(surf, W // 2, COL_TOP + 14, "SADDLED WITH THE TITLE", size=8,
         col=(180, 150, 150), alpha=200)
    cw = cf.size(chip_txt)[0] + 24
    chip = pygame.Rect((W - cw) // 2, COL_TOP + 22, cw, 24)
    surf.blit(_vgrad_panel(chip.w, chip.h, 12, (70, 26, 30), (42, 14, 16), 250),
              chip.topleft)
    pygame.draw.rect(surf, (210, 120, 96), chip, width=1, border_radius=12)
    timg = cf.render(chip_txt, True, (244, 206, 190))
    surf.blit(timg, timg.get_rect(center=chip.center))

    badges = shame_mod.BADGES
    cols = 3
    rows = (len(badges) + cols - 1) // cols
    gx = GAP
    cw2 = (W - 2 * SIDE - gx * (cols - 1)) // cols
    ch = 80
    grid_h = rows * ch + GAP * (rows - 1)
    top0 = chip.bottom + 12
    grid_top = top0 + max(0, (COL_BOT - top0 - grid_h) // 2)
    for i, b in enumerate(badges):
        r = i // cols
        c = i % cols
        cell = pygame.Rect(SIDE + c * (cw2 + gx), grid_top + r * (ch + GAP),
                           cw2, ch)
        _badge_cell(surf, cell, b, stats)


# ── ARCADE (curio tap targets; final art swaps in later) ─────────────────────

def _curio(surf, rect, kind, title, sub, cost):
    _panel(surf, rect, radius=11, top=(38, 30, 50), bot=(22, 16, 34))
    _sheen(surf, rect, 8)
    icx, icy = rect.x + 36, rect.centery
    if kind == 0:      # crystal ball
        _soft_glow(surf, icx, icy, 18, (150, 200, 240), 50, layers=4)
        pygame.draw.circle(surf, (40, 60, 90), (icx, icy), 16)
        pygame.draw.circle(surf, (170, 210, 245), (icx, icy), 16, 2)
        pygame.draw.circle(surf, (220, 240, 255), (icx - 5, icy - 5), 3)
        pygame.draw.polygon(surf, (150, 120, 70),
                            [(icx - 13, icy + 14), (icx + 13, icy + 14),
                             (icx + 8, icy + 19), (icx - 8, icy + 19)])
    elif kind == 1:    # vending machine
        m = pygame.Rect(icx - 14, icy - 18, 28, 36)
        surf.blit(_vgrad_panel(m.w, m.h, 4, (70, 60, 90), (40, 32, 58), 255),
                  m.topleft)
        pygame.draw.rect(surf, (150, 130, 190), m, width=1, border_radius=4)
        pygame.draw.circle(surf, (240, 200, 90), (m.centerx, m.y + 10), 6)
        pygame.draw.rect(surf, (30, 24, 40), (m.x + 5, m.bottom - 8, 18, 4))
    else:              # sage parrot
        _soft_glow(surf, icx, icy, 16, (230, 120, 80), 40, layers=4)
        pygame.draw.circle(surf, (200, 80, 60), (icx, icy), 13)
        pygame.draw.circle(surf, (150, 50, 40), (icx, icy), 13, 1)
        pygame.draw.circle(surf, (240, 240, 245), (icx + 4, icy - 3), 3)
        pygame.draw.circle(surf, (20, 20, 24), (icx + 5, icy - 3), 1)
        pygame.draw.polygon(surf, (240, 180, 70),
                            [(icx + 10, icy), (icx + 17, icy + 2),
                             (icx + 10, icy + 5)])
        pygame.draw.lines(surf, (220, 220, 226), False,
                          [(icx - 3, icy + 7), (icx - 4, icy + 16),
                           (icx, icy + 13), (icx + 3, icy + 16)], 1)
    tx = rect.x + 64
    _module_header(surf, tx, rect.centery - 9, title, size=12)
    sub_img = _font(8, True).render(sub, True, (190, 180, 210))
    sub_img.set_alpha(210)
    surf.blit(sub_img, (tx, rect.centery + 4))
    if cost > 0:
        ct = _font(9, True).render(f"{cost}c", True, _GOLD_BRIGHT)
        surf.blit(ct, ct.get_rect(midright=(rect.right - 14, rect.centery)))
    else:
        ct = _font(9, True).render("FREE", True, (150, 220, 160))
        surf.blit(ct, ct.get_rect(midright=(rect.right - 14, rect.centery)))


def draw_arcade(surf, t, stats) -> "dict[str, pygame.Rect]":
    curios = [("crystal", 0, "CRYSTAL BALL", "PEEK YOUR NEXT RUN", 0),
              ("vending", 1, "VENDING MACHINE", "5 COINS FOR JUNK", 5),
              ("beakon", 2, "MASTER BEAKON", "TIPS FOR LIFE", 20)]
    cm_h = 116
    stack_h = 3 * cm_h + GAP * 2
    y = COL_TOP + max(0, (COL_BOT - COL_TOP - stack_h) // 2)
    rects: "dict[str, pygame.Rect]" = {}
    for key, kind, title, sub, cost in curios:
        r = pygame.Rect(SIDE, y, W - 2 * SIDE, cm_h)
        _curio(surf, r, kind, title, sub, cost)
        rects[key] = r
        y += cm_h + GAP
    return rects
