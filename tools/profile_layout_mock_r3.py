"""
Round-3 FINAL Profile screen layout sheet — the C-chassis merge.

Builds on mock C (Centered Even Spacing) and folds in A + B strengths per the
art-director verdict:
  * C's contract is the shared layout law — fixed-height modules, the whole
    stack vertically centred in the content column, a single UNIFORM inter-
    module gap (GAP, named once below). SHAME and ARCADE inherit it.
  * A's full-height death histogram returns (height reclaimed from the top by
    halving the switcher->first-tile slack), with A's 1-12 axis ticks and A's
    red nemesis-bar treatment (red fill + white inner highlight + NEMESIS chip),
    kept the tallest bar so it reads by value alone (colorblind-safe).
  * B-level header contrast on the two captioned modules.
  * Flip-counter stays at C's proportion.

The sheet renders THREE section shapes side by side to prove the centred /
uniform-gap chassis is reusable: the full STATS tab (hero), a SHAME badge-grid
stub, and an ARCADE three-curio stub — all on the same GAP and centring law.
Reuses the shipped "Obsidian & Gold" primitives. Run headless with
PYTHONPATH=/home/user/skybit.
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
from game.hud import _font, _draw_overlay_stars, \
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE
from game.draw import NEAR_BLACK, WHITE, UI_CREAM, rounded_rect, lerp_color
from game.powerup_help import _seeded_stars
from game.store import (
    _vgrad_panel, _drop_shadow, _inset_disc, _gem,
    _gradient_text, _soft_glow, _gold_rule,
    _BG_STOPS, _OBS_TOP, _OBS_BOT,
)

T = 1.2
STARS = _seeded_stars()

_NEMESIS = (236, 86, 64)          # bright nemesis red — must read as THE beat
_NEMESIS_DEEP = (150, 36, 28)
_BRONZE_TOP = (120, 86, 52)       # tarnished bronze for SHAME badge cells
_BRONZE_BOT = (70, 48, 28)

# ── shared layout contract (the locked law every section reuses) ─────────────
# The content column runs COL_TOP..COL_BOT; BACK is bottom-anchored. GAP is the
# single canonical inter-module gap — STATS / SHAME / ARCADE all space modules
# by exactly this, and each centres its fixed-height stack inside the column.
GAP = 14
COL_TOP = 78                      # raised: switcher->first-row slack halved (d6)
BACK_CY = H - 24
COL_BOT = BACK_CY - 26
SIDE = 12
SWITCH_Y = 48

PB = [("BEST SCORE", "1,284"), ("BEST PILLARS", "312"),
      ("LONGEST FLIGHT", "4:07"), ("BEST NEAR-MISS", "x19")]
LIFETIME = [("RUNS", "2,941"), ("TIME ALOFT", "63h"),
            ("PILLARS", "48.2k"), ("COINS", "271k")]
DEATHS = [4, 9, 14, 22, 31, 27, 41, 19, 12, 8, 5, 3]
NEMESIS_IDX = 6
DAYS = "07"

# higher-contrast module-header colour (B-level): brighter + lifted off the
# panel fill so captions stop sinking into the obsidian.
_HEADER = (255, 226, 150)
_HEADER_ALPHA = 250


def _bg(surf):
    n = len(_BG_STOPS)
    for y in range(H):
        f = y / (H - 1)
        seg = min(n - 2, int(f * (n - 1)))
        local = (f * (n - 1)) - seg
        pygame.draw.line(surf, lerp_color(_BG_STOPS[seg], _BG_STOPS[seg + 1],
                                          local), (0, y), (W - 1, y))
    _draw_overlay_stars(surf, STARS, T + 1.4)


def _title(surf):
    _gradient_text(surf, "PROFILE", _font(28, True), (W // 2, 28),
                   (255, 240, 180), (236, 170, 60),
                   outline=_RED_OUTLINE, shadow=True)


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
    """High-contrast module caption (B-level) — a faint dark backing keeps the
    bright gold lifted off the obsidian fill so the header never sinks in."""
    f = _font(size, True)
    sh = f.render(txt, True, (10, 8, 4))
    sh.set_alpha(150)
    surf.blit(sh, (x + 1, y - sh.get_height() // 2 + 1))
    img = f.render(txt, True, _HEADER)
    img.set_alpha(_HEADER_ALPHA)
    surf.blit(img, (x, y - img.get_height() // 2))


def _module_rule(surf, y):
    _gold_rule(surf, SIDE + 4, W - SIDE - 4, y, peak=70)


# ── section glyphs ───────────────────────────────────────────────────────────

def _mini_glyph(surf, kind, cx, cy, col, scale=1.0):
    if kind == 0:  # gear
        r = int(5 * scale)
        pygame.draw.circle(surf, col, (cx, cy), r, 2)
        for a in range(0, 360, 60):
            ra = math.radians(a)
            x1, y1 = cx + r * math.cos(ra), cy + r * math.sin(ra)
            x2, y2 = cx + (r + 3) * math.cos(ra), cy + (r + 3) * math.sin(ra)
            pygame.draw.line(surf, col, (x1, y1), (x2, y2), 2)
    elif kind == 1:  # bar-chart
        for k, hh in enumerate((4, 8, 6)):
            pygame.draw.rect(surf, col,
                             (cx - 7 + k * 5, cy + 5 - hh, 3, hh))
    elif kind == 2:  # skull
        r = int(5 * scale)
        pygame.draw.circle(surf, col, (cx, cy - 1), r, 2)
        pygame.draw.circle(surf, col, (cx - 2, cy - 1), 1)
        pygame.draw.circle(surf, col, (cx + 2, cy - 1), 1)
        pygame.draw.line(surf, col, (cx - 2, cy + 4), (cx + 2, cy + 4), 2)
    else:  # star
        pts = []
        for k in range(10):
            rr = (7 if k % 2 == 0 else 3) * scale
            a = math.radians(-90 + k * 36)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        pygame.draw.polygon(surf, col, pts, 1)


# ── pill-strip switcher (active tab driven by arg) ───────────────────────────

def switcher(surf, y, active=1):
    labels = ["GEAR", "STATS", "SHAME", "ARCADE"]
    glyphs = [0, 1, 2, 3]
    n = len(labels)
    gap = 6
    total = W - 2 * SIDE
    pw = (total - gap * (n - 1)) // n
    x = SIDE
    ph = 34
    for i, lab in enumerate(labels):
        r = pygame.Rect(x, y, pw, ph)
        on = (i == active)
        if on:
            _soft_glow(surf, r.centerx, r.centery, 24, (255, 200, 90), 36,
                       layers=4)
            surf.blit(_vgrad_panel(r.w, r.h, 11, (255, 220, 128),
                                   (228, 160, 44), 255), r.topleft)
            pygame.draw.rect(surf, (255, 246, 210), r, width=1,
                             border_radius=11)
            pygame.draw.rect(surf, (*_GOLD_DEEP, 210), r.inflate(-4, -4),
                             width=1, border_radius=9)
            col = (44, 28, 6)
            _mini_glyph(surf, glyphs[i], r.centerx, r.y + 10, col)
            t = _font(10, True).render(lab, True, col)
            surf.blit(t, t.get_rect(center=(r.centerx, r.bottom - 9)))
        else:
            surf.blit(_vgrad_panel(r.w, r.h, 11, (52, 44, 64), (30, 25, 44),
                                   245), r.topleft)
            pygame.draw.rect(surf, (148, 126, 92), r, width=1,
                             border_radius=11)
            gcol = (206, 188, 150)
            gx = r.x + 13
            _mini_glyph(surf, glyphs[i], gx, r.centery, gcol, scale=0.8)
            t = _font(9, True).render(lab, True, gcol)
            surf.blit(t, t.get_rect(midleft=(gx + 11, r.centery)))
        x += pw + gap


# ── STATS building blocks ────────────────────────────────────────────────────

def pb_tile(surf, rect, label, value):
    _panel(surf, rect, radius=11)
    _sheen(surf, rect, 10)
    vsize = 23 if rect.h >= 50 else 21
    _gradient_text(surf, value, _font(vsize, True),
                   (rect.centerx, rect.centery - 5),
                   (255, 244, 196), (236, 170, 60), shadow=True)
    _cap(surf, rect.centerx, rect.bottom - 11, label, size=9,
         col=_GOLD_PALE, alpha=220)


def pb_grid(surf, top, tile_h):
    tw = (W - 2 * SIDE - 8) // 2
    for i, (lab, val) in enumerate(PB):
        r = pygame.Rect(SIDE + (i % 2) * (tw + 8),
                        top + (i // 2) * (tile_h + 6), tw, tile_h)
        pb_tile(surf, r, lab, val)
    return top + 2 * tile_h + 6


def counter_row(surf, rect):
    _panel(surf, rect, radius=11)
    _sheen(surf, rect, 8)
    n = len(LIFETIME)
    seg = rect.w / n
    for i, (lab, val) in enumerate(LIFETIME):
        cx = int(rect.x + seg * (i + 0.5))
        if i > 0:
            dx = int(rect.x + seg * i)
            pygame.draw.line(surf, (*_GOLD_DEEP, 120),
                             (dx, rect.y + 8), (dx, rect.bottom - 8), 1)
        vimg = _font(15, True).render(val, True, _GOLD_BRIGHT)
        surf.blit(vimg, vimg.get_rect(center=(cx, rect.y + 15)))
        _cap(surf, cx, rect.bottom - 10, lab, size=8, col=_GOLD_PALE,
             alpha=195)


def _engraved_strip(surf, rect, txt):
    surf.blit(_vgrad_panel(rect.w, rect.h, 5, (44, 36, 22), (28, 22, 12), 255),
              rect.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 180), rect, width=1, border_radius=5)
    sh = _font(9, True).render(txt, True, (16, 12, 6))
    surf.blit(sh, sh.get_rect(center=(rect.centerx + 1, rect.centery + 1)))
    # B-level header brightness on the engraved caption too
    hd = _font(9, True).render(txt, True, _HEADER)
    surf.blit(hd, hd.get_rect(center=rect.center))


def safety_board(surf, rect, caption="DAYS SINCE LAST DIGNIFIED FLIGHT"):
    plate = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        c = lerp_color((92, 96, 104), (54, 56, 64), y / max(1, rect.h - 1))
        pygame.draw.line(plate, (*c, 255), (0, y), (rect.w, y))
    for sx in range(0, rect.w, 3):
        a = 18 if (sx // 3) % 2 == 0 else 8
        pygame.draw.line(plate, (255, 255, 255, a), (sx, 0), (sx, rect.h))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=8)
    plate.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    _drop_shadow(surf, rect, 9, blur=6, alpha=130)
    surf.blit(plate, rect.topleft)
    pygame.draw.rect(surf, (30, 30, 36), rect, width=2, border_radius=8)
    pygame.draw.rect(surf, (140, 144, 152), rect.inflate(-4, -4), width=1,
                     border_radius=6)
    for rx, ry in ((rect.x + 8, rect.y + 8), (rect.right - 8, rect.y + 8),
                   (rect.x + 8, rect.bottom - 8),
                   (rect.right - 8, rect.bottom - 8)):
        pygame.draw.circle(surf, (40, 40, 46), (rx, ry), 3)
        pygame.draw.circle(surf, (170, 174, 182), (rx, ry), 3, 1)
        surf.set_at((rx - 1, ry - 1), (220, 224, 230))

    cap = pygame.Rect(rect.x + 14, rect.y + 10, rect.w - 28, 18)
    txt = caption
    while _font(9, True).size(txt)[0] > cap.w - 12 and "  " not in txt:
        txt = {"DAYS SINCE LAST DIGNIFIED FLIGHT": "DAYS SINCE DIGNIFIED",
               "DAYS SINCE DIGNIFIED": "DAYS SINCE"}.get(txt, "DAYS SINCE")
    _engraved_strip(surf, cap, txt)

    win = pygame.Rect(rect.centerx - 44, cap.bottom + 10, 88,
                      rect.bottom - cap.bottom - 20)
    surf.blit(_vgrad_panel(win.w, win.h, 6, (10, 12, 10), (4, 6, 4), 255),
              win.topleft)
    pygame.draw.rect(surf, (0, 0, 0), win, width=2, border_radius=6)

    led = _NEMESIS
    _soft_glow(surf, win.centerx, win.centery, 20, led, 56, layers=4)
    nf = _font(28, True)
    cw = win.w // 2
    for k, ch in enumerate(DAYS):
        cell = pygame.Rect(win.x + 2 + k * cw, win.y + 3, cw - 3, win.h - 6)
        surf.blit(_vgrad_panel(cell.w, cell.h, 3, (22, 26, 22), (8, 10, 8),
                               255), cell.topleft)
        pygame.draw.line(surf, (0, 0, 0), (cell.x, cell.centery),
                         (cell.right, cell.centery), 1)
        d = nf.render(ch, True, led)
        surf.blit(d, d.get_rect(center=cell.center))

    px, py = rect.right - 14, win.centery
    pygame.draw.circle(surf, (20, 20, 24), (px, py), 5)
    pygame.draw.circle(surf, led, (px, py), 3)
    pygame.draw.circle(surf, (255, 255, 255), (px - 1, py - 1), 1)


def histogram(surf, rect):
    """A's full-height death histogram. Nemesis bar burns red (white inner
    highlight) and stays the tallest bar so it reads by value alone; 1-12 axis
    ticks at A's weight; NEMESIS #7 red chip top-right; B-level header."""
    _panel(surf, rect, radius=11)
    _sheen(surf, rect, 8)
    _module_header(surf, rect.x + 12, rect.y + 13, "WHERE YOU DIE", size=9)

    tag = _font(8, True).render("NEMESIS  #7", True, (255, 232, 224))
    chip = pygame.Rect(rect.right - tag.get_width() - 18, rect.y + 6,
                       tag.get_width() + 10, 15)
    _soft_glow(surf, chip.centerx, chip.centery, 12, _NEMESIS, 40, layers=3)
    surf.blit(_vgrad_panel(chip.w, chip.h, 4, (220, 70, 52),
                           _NEMESIS_DEEP, 255), chip.topleft)
    pygame.draw.rect(surf, (255, 170, 150), chip, width=1, border_radius=4)
    surf.blit(tag, tag.get_rect(center=chip.center))

    top = rect.y + 28
    plot = pygame.Rect(rect.x + 12, top, rect.w - 24, rect.bottom - top - 16)
    n = len(DEATHS)
    mx = max(DEATHS)
    bw = plot.w / n
    base = plot.bottom
    pygame.draw.line(surf, (*_GOLD_DEEP, 120), (plot.x, base),
                     (plot.right, base), 1)
    for i, v in enumerate(DEATHS):
        bh = int((v / mx) * (plot.h - 4))
        bx = int(plot.x + bw * i + 1)
        br = pygame.Rect(bx, base - bh, int(bw) - 2, bh)
        if i == NEMESIS_IDX:
            _soft_glow(surf, br.centerx, br.centery, 14, _NEMESIS, 60,
                       layers=3)
            surf.blit(_vgrad_panel(br.w, max(2, br.h), 2,
                                   (240, 100, 82), _NEMESIS_DEEP, 255),
                      br.topleft)
            # white inner highlight carried over from A
            inner = br.inflate(-max(2, br.w - 4), 0)
            inner.h = br.h
            inner.bottom = br.bottom
            inner.centerx = br.centerx
            pygame.draw.rect(surf, (255, 214, 200), inner)
            pygame.draw.rect(surf, (255, 190, 170), br, width=1)
        else:
            surf.blit(_vgrad_panel(br.w, max(2, br.h), 2,
                                   (236, 190, 96), (150, 110, 40), 245),
                      br.topleft)
        # 1-12 axis ticks at A's weight
        nimg = _font(6, True).render(str(i + 1), True, (172, 152, 108))
        surf.blit(nimg, nimg.get_rect(center=(br.centerx, base + 7)))


def _back(surf):
    r = pygame.Rect(0, 0, 150, 32)
    r.center = (W // 2, BACK_CY)
    _drop_shadow(surf, r, 16, blur=4, alpha=90)
    surf.blit(_vgrad_panel(r.w, r.h, 16, (40, 32, 56), (22, 16, 38), 240),
              r.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 185), r, width=1, border_radius=16)
    t = _font(16, True).render("BACK", True, _GOLD_PALE)
    surf.blit(t, t.get_rect(center=r.center))


# ── HERO: full STATS tab on the locked centred / uniform-GAP chassis ─────────

def stats_tab(surf, teaser=False):
    """The merged STATS hero. Fixed-height modules spaced by exactly GAP, the
    whole stack centred in [COL_TOP, COL_BOT]. A's histogram returns at full
    height — the top slack reclaimed by COL_TOP keeps it tall. NEXT FRONTIER
    is an OPTIONAL centred slot (B's teaser) toggled by `teaser`."""
    _bg(surf); _title(surf)
    switcher(surf, SWITCH_Y, active=1)

    tile_h = 50
    pb_h = 2 * tile_h + 6
    count_h = 40
    board_h = 82
    teaser_h = 40
    hist_h = 132                     # A's value range reclaimed

    mods = [pb_h, count_h, board_h, hist_h]
    if teaser:
        mods.append(teaser_h)
    stack_h = sum(mods) + GAP * (len(mods) - 1)
    y = COL_TOP + max(0, (COL_BOT - COL_TOP - stack_h) // 2)

    y = pb_grid(surf, y, tile_h=tile_h)
    y += GAP - 6                     # pb_grid already adds its own 6 of trailing
    counter_row(surf, pygame.Rect(SIDE, y, W - 2 * SIDE, count_h))
    y += count_h + GAP
    _module_rule(surf, y - GAP // 2)
    safety_board(surf, pygame.Rect(SIDE, y, W - 2 * SIDE, board_h))
    y += board_h + GAP
    _module_rule(surf, y - GAP // 2)
    histogram(surf, pygame.Rect(SIDE, y, W - 2 * SIDE, hist_h))
    y += hist_h + GAP
    if teaser:
        _module_rule(surf, y - GAP // 2)
        t = pygame.Rect(SIDE, y, W - 2 * SIDE, teaser_h)
        _panel(surf, t, radius=11, top=(34, 28, 46), bot=(20, 16, 32))
        _sheen(surf, t, 8)
        _soft_glow(surf, t.x + 24, t.centery, 14, (170, 130, 230), 46,
                   layers=4)
        _gem(surf, t.x + 24, t.centery, 11, "epic", t=T, mystery=True)
        _gradient_text(surf, "NEXT FRONTIER", _font(12, True),
                       (t.centerx + 12, t.centery - 6),
                       (235, 210, 255), (170, 130, 230), shadow=True)
        _cap(surf, t.centerx + 12, t.centery + 9, "REACH 1,500 TO UNLOCK",
             size=8, col=(190, 170, 220), alpha=210)
    _back(surf)


# ── PROOF stub: SHAME = uniform tarnished-bronze badge grid ──────────────────

_SHAME = [("FIRST PILLAR", True), ("RAGE QUIT", True), ("FELL ASLEEP", False),
          ("UPSIDE DOWN", True), ("ZERO COINS", False), ("WRONG WAY", True),
          ("AFK DEATH", False), ("FAT FINGER", True), ("COMEBACK", False)]


def _badge_cell(surf, rect, label, earned):
    """One tarnished-bronze badge cell. Earned cells get a struck medallion;
    locked cells stay dim. Same fixed cell shape across the grid."""
    top = _BRONZE_TOP if earned else (58, 50, 44)
    bot = _BRONZE_BOT if earned else (34, 30, 26)
    _drop_shadow(surf, rect, 11, blur=5, alpha=110)
    surf.blit(_vgrad_panel(rect.w, rect.h, 11, top, bot, 252), rect.topleft)
    rim = (188, 142, 86) if earned else (96, 86, 76)
    pygame.draw.rect(surf, rim, rect, width=1, border_radius=11)
    cy = rect.y + rect.h // 2 - 6
    # struck medallion disc
    pygame.draw.circle(surf, (28, 20, 12), (rect.centerx, cy), 15)
    mt = (210, 156, 92) if earned else (92, 82, 72)
    pygame.draw.circle(surf, mt, (rect.centerx, cy), 14, 2)
    _mini_glyph(surf, 2, rect.centerx, cy, mt, scale=1.0)
    if not earned:
        lock = _font(8, True).render("LOCKED", True, (120, 110, 100))
        surf.blit(lock, lock.get_rect(center=(rect.centerx, cy + 1)))
    lc = (236, 208, 158) if earned else (140, 130, 120)
    _cap(surf, rect.centerx, rect.bottom - 10, label, size=8, col=lc,
         alpha=235 if earned else 180)


def shame_tab(surf):
    """PROOF: a 3x3 badge grid centred in the SAME column on the SAME GAP. The
    grid's row spacing IS GAP, proving the law works for a uniform grid, not
    just a column of bespoke modules."""
    _bg(surf); _title(surf)
    switcher(surf, SWITCH_Y, active=2)

    cols, rows = 3, 3
    gx = GAP
    cw = (W - 2 * SIDE - gx * (cols - 1)) // cols
    ch = 86
    grid_w = cols * cw + gx * (cols - 1)
    grid_h = rows * ch + GAP * (rows - 1)
    x0 = SIDE + (W - 2 * SIDE - grid_w) // 2
    y0 = COL_TOP + max(0, (COL_BOT - COL_TOP - grid_h) // 2)
    for i, (lab, earned) in enumerate(_SHAME):
        r = i // cols
        c = i % cols
        cell = pygame.Rect(x0 + c * (cw + gx), y0 + r * (ch + GAP), cw, ch)
        _badge_cell(surf, cell, lab, earned)
    _back(surf)


# ── PROOF stub: ARCADE = three equal curio modules ───────────────────────────

def _curio(surf, rect, kind, title, sub):
    _panel(surf, rect, radius=11, top=(38, 30, 50), bot=(22, 16, 34))
    _sheen(surf, rect, 8)
    icx = rect.x + 34
    icy = rect.centery
    if kind == 0:      # crystal ball
        _soft_glow(surf, icx, icy, 18, (150, 200, 240), 50, layers=4)
        pygame.draw.circle(surf, (40, 60, 90), (icx, icy), 15)
        pygame.draw.circle(surf, (170, 210, 245), (icx, icy), 15, 2)
        pygame.draw.circle(surf, (220, 240, 255), (icx - 5, icy - 5), 3)
        pygame.draw.polygon(surf, (90, 78, 60),
                            [(icx - 12, icy + 13), (icx + 12, icy + 13),
                             (icx + 8, icy + 18), (icx - 8, icy + 18)])
    elif kind == 1:    # vending machine
        m = pygame.Rect(icx - 13, icy - 16, 26, 32)
        surf.blit(_vgrad_panel(m.w, m.h, 4, (70, 60, 90), (40, 32, 58), 255),
                  m.topleft)
        pygame.draw.rect(surf, (150, 130, 190), m, width=1, border_radius=4)
        for gy in range(m.y + 5, m.bottom - 8, 7):
            pygame.draw.line(surf, (120, 150, 200), (m.x + 4, gy),
                             (m.right - 4, gy), 1)
        pygame.draw.rect(surf, (30, 24, 40), (m.x + 4, m.bottom - 7, 18, 4))
    else:              # sage parrot
        _soft_glow(surf, icx, icy, 16, (120, 220, 160), 44, layers=4)
        pygame.draw.circle(surf, (70, 180, 120), (icx, icy), 11)
        pygame.draw.circle(surf, (40, 130, 90), (icx, icy), 11, 1)
        pygame.draw.circle(surf, (240, 240, 245), (icx + 4, icy - 3), 3)
        pygame.draw.circle(surf, (20, 20, 24), (icx + 5, icy - 3), 1)
        pygame.draw.polygon(surf, (240, 180, 70),
                            [(icx + 9, icy), (icx + 16, icy + 2),
                             (icx + 9, icy + 5)])
    tx = rect.x + 60
    _module_header(surf, tx, rect.centery - 8, title, size=11)
    sub_img = _font(8, True).render(sub, True, (190, 180, 210))
    sub_img.set_alpha(210)
    surf.blit(sub_img, (tx, rect.centery + 6))


def arcade_tab(surf):
    """PROOF: three equal curio modules centred on the SAME GAP — proving the
    law holds for a small set of equal feature tiles."""
    _bg(surf); _title(surf)
    switcher(surf, SWITCH_Y, active=3)

    curios = [(0, "ORACLE", "PEEK YOUR NEXT RUN"),
              (1, "VENDING", "SPEND COINS ON SKINS"),
              (2, "SAGE PARROT", "DAILY WISDOM")]
    cm_h = 116
    stack_h = 3 * cm_h + GAP * 2
    y = COL_TOP + max(0, (COL_BOT - COL_TOP - stack_h) // 2)
    for kind, title, sub in curios:
        _curio(surf, pygame.Rect(SIDE, y, W - 2 * SIDE, cm_h), kind, title, sub)
        y += cm_h + GAP
    _back(surf)


# ── compose the final proof sheet ────────────────────────────────────────────

PANELS = [
    ("STATS  (hero — C-chassis merge)", lambda s: stats_tab(s, teaser=False)),
    ("SHAME  (badge-grid proof)", shame_tab),
    ("ARCADE  (curio proof)", arcade_tab),
]


def main():
    pad = 16
    label_h = 26
    cols = len(PANELS)
    sheet_w = pad + cols * (W + pad)
    sheet_h = pad + label_h + H + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 22))
    lf = pygame.font.Font(None, 22)
    for i, (name, fn) in enumerate(PANELS):
        x = pad + i * (W + pad)
        frame = pygame.Surface((W, H))
        fn(frame)
        sheet.blit(frame, (x, pad + label_h))
        pygame.draw.rect(sheet, _GOLD_DEEP,
                         (x - 1, pad + label_h - 1, W + 2, H + 2), 1)
        lbl = lf.render(name, True, _GOLD_PALE)
        sheet.blit(lbl, (x + 4, pad // 2 - 2))
    out = "/home/user/skybit/docs/profile/screen_layout/round_3.png"
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
