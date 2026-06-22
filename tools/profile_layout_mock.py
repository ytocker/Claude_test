"""
Headless exploration sheet for the expanded Profile screen layout.

Renders five full 360x640 Profile mocks (STATS section populated) side by side
into one combined review PNG. Reuses the shipped Store/HUD "Obsidian & Gold"
primitives so the mocks are pixel-consistent with the live screens — the point
of this pass is to lock the section-switcher + STATS frame language, not to
invent new colour. Run headless (SDL dummy driver); writes the sheet only.
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
    _vgrad_panel, _drop_shadow, _inset_disc, _shelf_bar, _gem,
    _gradient_text, _chip, _coin_glyph, _soft_glow, _gold_rule,
    _BG_STOPS, _OBS_TOP, _OBS_BOT,
)

T = 1.2  # frozen animation phase shared by every mock
STARS = _seeded_stars()

# Bronze / tarnished palette for SHAME + nemesis red for the histogram, kept
# inside the locked language (warm metal + the title's rust red).
_BRONZE = (150, 104, 54)
_BRONZE_DEEP = (74, 48, 22)
_NEMESIS = (196, 60, 44)
_LED_GREEN = (96, 220, 130)
_LED_RED = (236, 92, 70)

# Plausible fake telemetry the STATS frame reads from.
PB = [("BEST SCORE", "1,284"), ("BEST PILLARS", "312"),
      ("LONGEST FLIGHT", "4:07"), ("BEST NEAR-MISS", "x19")]
LIFETIME = [("RUNS", "2,941"), ("TIME ALOFT", "63h"),
            ("PILLARS", "48.2k"), ("COINS", "271k")]
# Death-pillar histogram: counts per early pillar number; pillar 7 is the nemesis.
DEATHS = [4, 9, 14, 22, 31, 27, 41, 19, 12, 8, 5, 3]
NEMESIS_IDX = 6
DAYS_SINCE = "007"


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


def _cap_left(surf, x, y, txt, size=10, col=_GOLD_PALE, alpha=210):
    img = _font(size, True).render(txt, True, col)
    img.set_alpha(alpha)
    surf.blit(img, (x, y - img.get_height() // 2))


# ── section switcher treatments (one per version) ────────────────────────────

def switcher_pillstrip(surf, y, active=1):
    """Four full gold-rimmed pills; active one filled bright gold."""
    labels = ["GEAR", "STATS", "SHAME", "ARCADE"]
    n = len(labels)
    gap = 6
    total = W - 24
    pw = (total - gap * (n - 1)) // n
    x = 12
    for i, lab in enumerate(labels):
        r = pygame.Rect(x, y, pw, 28)
        on = (i == active)
        if on:
            _soft_glow(surf, r.centerx, r.centery, 26, (255, 200, 90), 40, layers=4)
            surf.blit(_vgrad_panel(r.w, r.h, 14, (255, 214, 120), _GOLD_DEEP, 255),
                      r.topleft)
            pygame.draw.rect(surf, (*_GOLD_BRIGHT, 230), r, width=1, border_radius=14)
            col = (40, 26, 8)
        else:
            surf.blit(_vgrad_panel(r.w, r.h, 14, (40, 34, 50), (22, 18, 32), 240),
                      r.topleft)
            pygame.draw.rect(surf, (96, 84, 70), r, width=1, border_radius=14)
            col = (170, 158, 140)
        t = _font(11, True).render(lab, True, col)
        surf.blit(t, t.get_rect(center=r.center))
        x += pw + gap


def switcher_underline(surf, y, active=1):
    """Segmented underline tabs — labels evenly spread, active gets a glowing
    gold bar (echoes the Store's category strip but at the top level)."""
    labels = ["GEAR", "STATS", "SHAME", "ARCADE"]
    n = len(labels)
    seg = (W - 24) / n
    track = pygame.Rect(12, y + 14, W - 24, 2)
    pygame.draw.rect(surf, (60, 52, 70), track, border_radius=1)
    for i, lab in enumerate(labels):
        cx = int(12 + seg * (i + 0.5))
        on = (i == active)
        col = _GOLD_BRIGHT if on else (150, 142, 158)
        t = _font(13, True).render(lab, True, col)
        if not on:
            t.set_alpha(180)
        tr = t.get_rect(center=(cx, y + 2))
        surf.blit(t, tr)
        if on:
            ur = pygame.Rect(tr.x - 3, y + 13, tr.w + 6, 3)
            glow = pygame.Surface((ur.w + 14, 10), pygame.SRCALPHA)
            for gy in range(10):
                pygame.draw.line(glow, (255, 200, 80, int(46 * (1 - gy / 10))),
                                 (0, gy), (ur.w + 14, gy))
            surf.blit(glow, (ur.x - 7, ur.y - 3), special_flags=pygame.BLEND_ADD)
            rounded_rect(surf, ur, 2, _GOLD_BRIGHT)


def switcher_iconlabel(surf, y, active=1):
    """Icon + label segmented control inside one obsidian capsule; active cell
    lit. Tiny procedural glyphs (gear / bars / skull / star)."""
    labels = ["GEAR", "STATS", "SHAME", "ARCADE"]
    n = len(labels)
    bar = pygame.Rect(12, y, W - 24, 38)
    _panel(surf, bar, radius=13)
    seg = bar.w / n
    for i, lab in enumerate(labels):
        cell = pygame.Rect(int(bar.x + seg * i), bar.y + 3,
                           int(seg) - 1, bar.h - 6)
        on = (i == active)
        if on:
            surf.blit(_vgrad_panel(cell.w, cell.h, 10, (66, 52, 24), (36, 28, 12), 255),
                      cell.topleft)
            pygame.draw.rect(surf, (*_GOLD_BRIGHT, 210), cell, width=1, border_radius=10)
        gcol = _GOLD_BRIGHT if on else (150, 138, 120)
        gx, gy = cell.centerx, cell.y + 12
        _mini_glyph(surf, i, gx, gy, gcol)
        t = _font(9, True).render(lab, True, gcol)
        if not on:
            t.set_alpha(180)
        surf.blit(t, t.get_rect(center=(cell.centerx, cell.bottom - 8)))


def _mini_glyph(surf, kind, cx, cy, col):
    if kind == 0:  # gear
        pygame.draw.circle(surf, col, (cx, cy), 5, 2)
        for a in range(0, 360, 60):
            ra = math.radians(a)
            x1, y1 = cx + 5 * math.cos(ra), cy + 5 * math.sin(ra)
            x2, y2 = cx + 8 * math.cos(ra), cy + 8 * math.sin(ra)
            pygame.draw.line(surf, col, (x1, y1), (x2, y2), 2)
    elif kind == 1:  # bars
        for k, hh in enumerate((4, 8, 6)):
            pygame.draw.rect(surf, col, (cx - 7 + k * 5, cy + 5 - hh, 3, hh))
    elif kind == 2:  # skull
        pygame.draw.circle(surf, col, (cx, cy - 1), 5, 2)
        pygame.draw.circle(surf, col, (cx - 2, cy - 1), 1)
        pygame.draw.circle(surf, col, (cx + 2, cy - 1), 1)
        pygame.draw.line(surf, col, (cx - 2, cy + 4), (cx + 2, cy + 4), 2)
    else:  # star
        pts = []
        for k in range(10):
            rr = 7 if k % 2 == 0 else 3
            a = math.radians(-90 + k * 36)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        pygame.draw.polygon(surf, col, pts, 1)


def switcher_chip_pill(surf, y, active=1):
    """Compact chip row riding inside a slim obsidian rail — pills are short,
    centred, with a hairline rail behind so the four read as one control."""
    labels = ["GEAR", "STATS", "SHAME", "ARCADE"]
    rail = pygame.Rect(10, y, W - 20, 30)
    surf.blit(_vgrad_panel(rail.w, rail.h, 15, (20, 17, 30), (12, 10, 20), 230),
              rail.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 130), rail, width=1, border_radius=15)
    widths = [_font(11, True).size(l)[0] + 22 for l in labels]
    total = sum(widths) + 6 * (len(labels) - 1)
    x = rail.centerx - total // 2
    for i, lab in enumerate(labels):
        w = widths[i]
        r = pygame.Rect(x, y + 4, w, 22)
        on = (i == active)
        if on:
            _soft_glow(surf, r.centerx, r.centery, 20, (255, 200, 90), 34, layers=3)
            surf.blit(_vgrad_panel(r.w, r.h, 11, (255, 210, 116), _GOLD_DEEP, 255),
                      r.topleft)
            pygame.draw.rect(surf, (*_GOLD_BRIGHT, 220), r, width=1, border_radius=11)
            col = (42, 28, 8)
        else:
            col = (164, 152, 134)
        t = _font(11, True).render(lab, True, col)
        if not on:
            t.set_alpha(190)
        surf.blit(t, t.get_rect(center=r.center))
        x += w + 6


def switcher_ticket(surf, y, active=1):
    """Notched 'ticket' tabs that hang from a top gold rail — playful arcade
    feel; active ticket drops slightly + lights up."""
    labels = ["GEAR", "STATS", "SHAME", "ARCADE"]
    n = len(labels)
    gap = 5
    total = W - 20
    pw = (total - gap * (n - 1)) // n
    x = 10
    _gold_rule(surf, 12, W - 12, y - 2, peak=140)
    for i, lab in enumerate(labels):
        on = (i == active)
        oy = y + (4 if on else 0)
        r = pygame.Rect(x, oy, pw, 26 if on else 22)
        if on:
            _soft_glow(surf, r.centerx, r.centery, 22, (255, 200, 90), 36, layers=4)
            surf.blit(_vgrad_panel(r.w, r.h, 8, (255, 212, 118), _GOLD_DEEP, 255),
                      r.topleft)
            pygame.draw.rect(surf, (*_GOLD_BRIGHT, 230), r, width=1, border_radius=8)
            col = (42, 28, 8)
        else:
            surf.blit(_vgrad_panel(r.w, r.h, 8, (38, 32, 48), (22, 18, 30), 240),
                      r.topleft)
            pygame.draw.rect(surf, (92, 80, 66), r, width=1, border_radius=8)
            col = (168, 156, 138)
        # ticket notches on each side
        pygame.draw.circle(surf, _BG_STOPS[1], (r.left, r.centery), 2)
        pygame.draw.circle(surf, _BG_STOPS[1], (r.right, r.centery), 2)
        t = _font(10, True).render(lab, True, col)
        surf.blit(t, t.get_rect(center=r.center))
        x += pw + gap


# ── STATS building blocks ────────────────────────────────────────────────────

def pb_tile(surf, rect, label, value, chunky=True, accent=_GOLD_BRIGHT):
    _panel(surf, rect, radius=11)
    _sheen(surf, rect, 10)
    vsize = 22 if chunky else 19
    _gradient_text(surf, value, _font(vsize, True),
                   (rect.centerx, rect.y + (rect.h // 2 - 4 if chunky else 22)),
                   (255, 244, 196), (236, 170, 60), shadow=True)
    _cap(surf, rect.centerx, rect.bottom - 11, label, size=9,
         col=accent, alpha=220)


def pb_tile_iconleft(surf, rect, label, value, glyph_idx):
    """Slim tile with a gold disc icon at left and stacked value/label right."""
    _panel(surf, rect, radius=11)
    _sheen(surf, rect, 10)
    dcx, dcy = rect.x + 22, rect.centery
    _inset_disc(surf, dcx, dcy, 14)
    pygame.draw.circle(surf, (*_GOLD_DEEP, 180), (dcx, dcy), 14, 1)
    _mini_glyph(surf, glyph_idx, dcx, dcy, _GOLD_BRIGHT)
    tx = rect.x + 42
    _gradient_text(surf, value, _font(18, True),
                   (tx + 30, rect.y + 16), (255, 244, 196), (236, 170, 60),
                   shadow=True)
    _cap_left(surf, tx, rect.bottom - 12, label, size=8, col=_GOLD_PALE, alpha=210)


def counter_row(surf, rect, slim=False):
    """A single obsidian rail split into four lifetime counters by gold hairlines."""
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
        surf.blit(vimg, vimg.get_rect(center=(cx, rect.y + 16)))
        _cap(surf, cx, rect.bottom - 11, lab, size=8, col=_GOLD_PALE, alpha=190)


def safety_sign(surf, rect, led_red=True):
    """Dented-metal 'DAYS SINCE LAST DIGNIFIED FLIGHT' board: brushed steel plate
    with corner rivets, a recessed dark LED window holding a big flip number,
    and a small red/green stoplight pip — straight from industrial scoreboards."""
    # brushed steel plate
    plate = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        c = lerp_color((92, 96, 104), (54, 56, 64), y / max(1, rect.h - 1))
        pygame.draw.line(plate, (*c, 255), (0, y), (rect.w, y))
    # faint vertical brush streaks + a couple of dents
    for sx in range(0, rect.w, 3):
        a = 18 if (sx // 3) % 2 == 0 else 8
        pygame.draw.line(plate, (255, 255, 255, a), (sx, 0), (sx, rect.h))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=8)
    plate.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    _drop_shadow(surf, rect, 9, blur=6, alpha=130)
    surf.blit(plate, rect.topleft)
    pygame.draw.rect(surf, (30, 30, 36), rect, width=2, border_radius=8)
    pygame.draw.rect(surf, (140, 144, 152), rect.inflate(-4, -4), width=1,
                     border_radius=6)
    # rivets
    for rx, ry in ((rect.x + 8, rect.y + 8), (rect.right - 8, rect.y + 8),
                   (rect.x + 8, rect.bottom - 8), (rect.right - 8, rect.bottom - 8)):
        pygame.draw.circle(surf, (40, 40, 46), (rx, ry), 3)
        pygame.draw.circle(surf, (170, 174, 182), (rx, ry), 3, 1)
        surf.set_at((rx - 1, ry - 1), (220, 224, 230))
    # header strip
    hdr = _font(9, True).render("DAYS SINCE LAST DIGNIFIED FLIGHT", True, (28, 28, 34))
    surf.blit(hdr, hdr.get_rect(center=(rect.centerx, rect.y + 14)))
    # recessed LED window
    win = pygame.Rect(rect.centerx - 54, rect.y + 24, 108, rect.h - 34)
    surf.blit(_vgrad_panel(win.w, win.h, 6, (10, 12, 10), (4, 6, 4), 255), win.topleft)
    pygame.draw.rect(surf, (0, 0, 0), win, width=2, border_radius=6)
    led = _LED_RED if led_red else _LED_GREEN
    # seven-seg-ish flip number
    nf = _font(34, True)
    _soft_glow(surf, win.centerx, win.centery, 26, led, 70, layers=4)
    ghost = nf.render(DAYS_SINCE, True, (40, 50, 44))
    surf.blit(ghost, ghost.get_rect(center=win.center))
    num = nf.render(DAYS_SINCE, True, led)
    surf.blit(num, num.get_rect(center=win.center))
    # stoplight pip
    px, py = rect.right - 18, rect.centery
    pygame.draw.circle(surf, (20, 20, 24), (px, py), 6)
    pygame.draw.circle(surf, led, (px, py), 4)
    pygame.draw.circle(surf, (255, 255, 255), (px - 1, py - 1), 1)


def histogram(surf, rect, horizontal=False, titled=True):
    """Death-pillar histogram: a slim obsidian card of bars by pillar number, the
    nemesis pillar bar burning red while the rest stay gold."""
    _panel(surf, rect, radius=11)
    _sheen(surf, rect, 8)
    top = rect.y + (16 if titled else 8)
    if titled:
        _cap_left(surf, rect.x + 12, rect.y + 11, "WHERE YOU DIE", size=9,
                  col=_GOLD_PALE, alpha=200)
        _cap_left(surf, rect.right - 64, rect.y + 11, "NEMESIS  #7", size=8,
                  col=_NEMESIS, alpha=230)
    plot = pygame.Rect(rect.x + 12, top, rect.w - 24, rect.bottom - top - 12)
    n = len(DEATHS)
    mx = max(DEATHS)
    bw = plot.w / n
    base = plot.bottom
    pygame.draw.line(surf, (*_GOLD_DEEP, 120), (plot.x, base), (plot.right, base), 1)
    for i, v in enumerate(DEATHS):
        bh = int((v / mx) * (plot.h - 4))
        bx = int(plot.x + bw * i + 1)
        br = pygame.Rect(bx, base - bh, int(bw) - 2, bh)
        if i == NEMESIS_IDX:
            _soft_glow(surf, br.centerx, br.centery, 12, _NEMESIS, 50, layers=3)
            surf.blit(_vgrad_panel(br.w, max(2, br.h), 2,
                                   (236, 96, 78), (150, 36, 28), 255), br.topleft)
            pygame.draw.rect(surf, (255, 180, 160), br, width=1)
        else:
            surf.blit(_vgrad_panel(br.w, max(2, br.h), 2,
                                   (236, 190, 96), (150, 110, 40), 245), br.topleft)


# ── version composers ────────────────────────────────────────────────────────

def version_1(surf):
    """V1 — Pill-strip switcher; chunky 2x2 PB tiles, sign + histogram stacked."""
    _bg(surf); _title(surf)
    switcher_pillstrip(surf, 50, active=1)
    y = 90
    # PB 2x2
    tw = (W - 24 - 8) // 2
    for i, (lab, val) in enumerate(PB):
        r = pygame.Rect(12 + (i % 2) * (tw + 8), y + (i // 2) * 56, tw, 50)
        pb_tile(surf, r, lab, val, chunky=True)
    y += 2 * 56 + 6
    counter_row(surf, pygame.Rect(12, y, W - 24, 40))
    y += 48
    safety_sign(surf, pygame.Rect(12, y, W - 24, 78))
    y += 86
    histogram(surf, pygame.Rect(12, y, W - 24, 92))
    _back(surf)


def version_2(surf):
    """V2 — Segmented-underline switcher; slim icon-left PB tiles in one column
    pair, sign + histogram side-by-side to save height."""
    _bg(surf); _title(surf)
    switcher_underline(surf, 52, active=1)
    y = 86
    tw = (W - 24 - 8) // 2
    glyphs = [1, 0, 3, 2]
    for i, (lab, val) in enumerate(PB):
        r = pygame.Rect(12 + (i % 2) * (tw + 8), y + (i // 2) * 48, tw, 42)
        pb_tile_iconleft(surf, r, lab, val, glyphs[i])
    y += 2 * 48 + 6
    counter_row(surf, pygame.Rect(12, y, W - 24, 40))
    y += 48
    # sign (left, taller) + histogram (right) coexist on one row
    safety_sign(surf, pygame.Rect(12, y, 168, 150))
    histogram(surf, pygame.Rect(188, y, W - 200, 150), titled=True)
    _back(surf)


def version_3(surf):
    """V3 — Icon+label segmented capsule switcher; airy single-column PB tiles
    (full-width chunky), generous breathing room, smaller sign + histogram."""
    _bg(surf); _title(surf)
    switcher_iconlabel(surf, 48, active=1)
    y = 96
    # full-width PB pairs (two rows of two wide tiles)
    tw = (W - 24 - 8) // 2
    for i, (lab, val) in enumerate(PB):
        r = pygame.Rect(12 + (i % 2) * (tw + 8), y + (i // 2) * 50, tw, 44)
        pb_tile(surf, r, lab, val, chunky=True, accent=_GOLD_PALE)
    y += 2 * 50 + 8
    counter_row(surf, pygame.Rect(12, y, W - 24, 38))
    y += 48
    safety_sign(surf, pygame.Rect(12, y, W - 24, 72))
    y += 80
    histogram(surf, pygame.Rect(12, y, W - 24, 82))
    _back(surf)


def version_4(surf):
    """V4 — Chip-pill rail switcher; dense dashboard — 4 slim PB tiles in one row,
    counters, then sign + histogram stacked tight with a big board."""
    _bg(surf); _title(surf)
    switcher_chip_pill(surf, 50, active=1)
    y = 86
    # 4 slim PB tiles across one row (chunky number, tiny label)
    n = len(PB)
    gap = 6
    tw = (W - 24 - gap * (n - 1)) // n
    for i, (lab, val) in enumerate(PB):
        r = pygame.Rect(12 + i * (tw + gap), y, tw, 58)
        _panel(surf, r, radius=10)
        _sheen(surf, r, 8)
        _gradient_text(surf, val, _font(16, True), (r.centerx, r.y + 18),
                       (255, 244, 196), (236, 170, 60), shadow=True)
        # two-line label
        words = lab.split()
        _cap(surf, r.centerx, r.bottom - 17, words[0], size=7, col=_GOLD_PALE, alpha=210)
        _cap(surf, r.centerx, r.bottom - 9, words[1] if len(words) > 1 else "",
             size=7, col=_GOLD_PALE, alpha=210)
    y += 66
    counter_row(surf, pygame.Rect(12, y, W - 24, 38))
    y += 46
    safety_sign(surf, pygame.Rect(12, y, W - 24, 92))
    y += 100
    histogram(surf, pygame.Rect(12, y, W - 24, 96))
    _back(surf)


def version_5(surf):
    """V5 — Ticket-tab switcher; framed 'console' — one big STATS panel hosts the
    PB tiles + counters at top and the sign + histogram on a shared base row."""
    _bg(surf); _title(surf)
    switcher_ticket(surf, 50, active=1)
    # one large containing panel for the whole STATS section
    outer = pygame.Rect(10, 88, W - 20, 510)
    _panel(surf, outer, radius=16)
    _cap_left(surf, outer.x + 16, outer.y + 16, "PERSONAL BESTS", size=9,
              col=_GOLD_PALE, alpha=200)
    _gold_rule(surf, outer.x + 14, outer.right - 14, outer.y + 26, peak=140)
    y = outer.y + 36
    tw = (outer.w - 20 - 8) // 2
    for i, (lab, val) in enumerate(PB):
        r = pygame.Rect(outer.x + 10 + (i % 2) * (tw + 8), y + (i // 2) * 50, tw, 44)
        pb_tile(surf, r, lab, val, chunky=True)
    y += 2 * 50 + 8
    counter_row(surf, pygame.Rect(outer.x + 10, y, outer.w - 20, 38))
    y += 48
    _cap_left(surf, outer.x + 16, y + 4, "RECORD OF SHAME", size=9,
              col=_GOLD_PALE, alpha=200)
    _gold_rule(surf, outer.x + 14, outer.right - 14, y + 14, peak=140)
    y += 24
    safety_sign(surf, pygame.Rect(outer.x + 10, y, outer.w - 20, 84))
    y += 92
    histogram(surf, pygame.Rect(outer.x + 10, y, outer.w - 20, 96), titled=True)
    _back(surf)


def _back(surf):
    r = pygame.Rect(0, 0, 150, 32)
    r.center = (W // 2, H - 22)
    _drop_shadow(surf, r, 16, blur=4, alpha=90)
    surf.blit(_vgrad_panel(r.w, r.h, 16, (40, 32, 56), (22, 16, 38), 240), r.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 185), r, width=1, border_radius=16)
    t = _font(16, True).render("BACK", True, _GOLD_PALE)
    surf.blit(t, t.get_rect(center=r.center))


# ── sheet assembly ───────────────────────────────────────────────────────────

VERSIONS = [
    ("V1  PILL-STRIP", version_1),
    ("V2  UNDERLINE", version_2),
    ("V3  ICON+LABEL", version_3),
    ("V4  CHIP-RAIL", version_4),
    ("V5  TICKET / CONSOLE", version_5),
]


def main():
    pad = 16
    label_h = 26
    cols = len(VERSIONS)
    sheet_w = pad + cols * (W + pad)
    sheet_h = pad + label_h + H + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 22))
    lf = pygame.font.Font(None, 24)
    for i, (name, fn) in enumerate(VERSIONS):
        x = pad + i * (W + pad)
        frame = pygame.Surface((W, H))
        fn(frame)
        # gold hairline frame around each mock
        sheet.blit(frame, (x, pad + label_h))
        pygame.draw.rect(sheet, _GOLD_DEEP, (x - 1, pad + label_h - 1, W + 2, H + 2), 1)
        lbl = lf.render(name, True, _GOLD_PALE)
        sheet.blit(lbl, (x + 4, pad // 2 - 2))
    out = "/home/user/skybit/docs/profile/screen_layout/round_1.png"
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
