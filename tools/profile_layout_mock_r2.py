"""
Round-2 exploration sheet for the Profile screen layout.

Renders three refined full 360x640 Profile mocks (STATS section populated) into
one combined review PNG. All three sit on the locked direction from round 1's
critique — V1 filled-gold pill-strip switcher (flattened active pill, brighter
inactive pills) with V3 section glyphs, V1 2x2 personal-best grid, V4 divided
lifetime counter strip, no enclosing frame (faint gold hairline module rules
only), a rebuilt safety board (engraved caption strip above a smaller LED
window, flip-digit days readout, no ghost layer), and a higher-contrast
NEMESIS tag. The three differ only in how they solve the lower third / vertical
rhythm. Reuses the shipped "Obsidian & Gold" primitives. Run headless.
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

# Shared layout contract every section reuses (locked here so SHAME / ARCADE
# inherit the same skeleton): the content column runs from COL_TOP to COL_BOT,
# the BACK button is bottom-anchored, leaving a fixed bottom margin.
COL_TOP = 88
BACK_CY = H - 24
COL_BOT = BACK_CY - 26          # content must end above the BACK button
SIDE = 12                       # left/right page margin

PB = [("BEST SCORE", "1,284"), ("BEST PILLARS", "312"),
      ("LONGEST FLIGHT", "4:07"), ("BEST NEAR-MISS", "x19")]
LIFETIME = [("RUNS", "2,941"), ("TIME ALOFT", "63h"),
            ("PILLARS", "48.2k"), ("COINS", "271k")]
DEATHS = [4, 9, 14, 22, 31, 27, 41, 19, 12, 8, 5, 3]
NEMESIS_IDX = 6
DAYS = "07"


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


def _module_rule(surf, y):
    """Faint gold hairline between modules — the only internal structure allowed
    (the critique killed the full enclosing frame)."""
    _gold_rule(surf, SIDE + 4, W - SIDE - 4, y, peak=70)


# ── section glyphs (V3) ──────────────────────────────────────────────────────

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


# ── locked switcher: filled-gold pill strip + glyphs ─────────────────────────

def switcher(surf, y, active=1):
    """Four equal-weight pills (GEAR / STATS / SHAME / ARCADE). Active pill is a
    clean solid-gold rounded-rect (no scalloped bump) with icon-above-label.
    Inactive pills carry a brighter rim + label than round 1 so they read as
    tappable, with icon-left of the label."""
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
            # solid bright-gold fill, flat clean rounded-rect
            _soft_glow(surf, r.centerx, r.centery, 24, (255, 200, 90), 36,
                       layers=4)
            surf.blit(_vgrad_panel(r.w, r.h, 11, (255, 220, 128),
                                   (228, 160, 44), 255), r.topleft)
            pygame.draw.rect(surf, (255, 246, 210), r, width=1,
                             border_radius=11)
            pygame.draw.rect(surf, (*_GOLD_DEEP, 210), r.inflate(-4, -4),
                             width=1, border_radius=9)
            col = (44, 28, 6)
            # icon above label on the active pill
            _mini_glyph(surf, glyphs[i], r.centerx, r.y + 10, col)
            t = _font(10, True).render(lab, True, col)
            surf.blit(t, t.get_rect(center=(r.centerx, r.bottom - 9)))
        else:
            surf.blit(_vgrad_panel(r.w, r.h, 11, (52, 44, 64), (30, 25, 44),
                                   245), r.topleft)
            # brighter rim + label (~15% up) so it reads tappable, not disabled
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
    """2x2 grid tile: dominant hero number centred, small-caps label beneath.
    No icon-left treatment (the critique forbids stealing number width)."""
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
    """V4 divided lifetime strip — one obsidian rail split into four counters by
    gold hairlines."""
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
    """Caption on a recessed, embossed gold-on-dark strip — debossed shadow line
    above, gold text, so it reads engraved into the plate and clears the LED."""
    surf.blit(_vgrad_panel(rect.w, rect.h, 5, (44, 36, 22), (28, 22, 12), 255),
              rect.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 180), rect, width=1, border_radius=5)
    # debossed: dark line under a gold line for an engraved bevel
    sh = _font(9, True).render(txt, True, (16, 12, 6))
    surf.blit(sh, sh.get_rect(center=(rect.centerx + 1, rect.centery + 1)))
    hd = _font(9, True).render(txt, True, _GOLD_PALE)
    surf.blit(hd, hd.get_rect(center=rect.center))


def safety_board(surf, rect, caption="DAYS SINCE LAST DIGNIFIED FLIGHT"):
    """Rebuilt 'days since last dignified flight' board: brushed-steel plate, an
    engraved gold caption strip ABOVE a smaller LED window (no overlap), and a
    flip-digit odometer days readout — no red circular-arrow glyph, no ghost
    digit. Stoplight pip kept (unambiguous green-clear/red-recent). Caption is
    abbreviated when the board is too narrow to hold the full line."""
    # brushed steel plate
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

    # engraved caption strip ABOVE the window — clears it entirely. Pick a
    # caption that fits the plate width so it never bleeds past the rivets.
    cap = pygame.Rect(rect.x + 14, rect.y + 10, rect.w - 28, 18)
    txt = caption
    while _font(9, True).size(txt)[0] > cap.w - 12 and "  " not in txt:
        txt = {"DAYS SINCE LAST DIGNIFIED FLIGHT": "DAYS SINCE DIGNIFIED",
               "DAYS SINCE DIGNIFIED": "DAYS SINCE"}.get(txt, "DAYS SINCE")
    _engraved_strip(surf, cap, txt)

    # smaller LED window beneath the caption
    win = pygame.Rect(rect.centerx - 44, cap.bottom + 10, 88,
                      rect.bottom - cap.bottom - 20)
    surf.blit(_vgrad_panel(win.w, win.h, 6, (10, 12, 10), (4, 6, 4), 255),
              win.topleft)
    pygame.draw.rect(surf, (0, 0, 0), win, width=2, border_radius=6)

    # odometer flip-digit days readout: two split cells with a center seam
    led = _NEMESIS
    _soft_glow(surf, win.centerx, win.centery, 20, led, 56, layers=4)
    nf = _font(28, True)
    cw = win.w // 2
    for k, ch in enumerate(DAYS):
        cell = pygame.Rect(win.x + 2 + k * cw, win.y + 3, cw - 3, win.h - 6)
        # flip-card body + horizontal seam through the middle
        surf.blit(_vgrad_panel(cell.w, cell.h, 3, (22, 26, 22), (8, 10, 8),
                               255), cell.topleft)
        pygame.draw.line(surf, (0, 0, 0), (cell.x, cell.centery),
                         (cell.right, cell.centery), 1)
        d = nf.render(ch, True, led)
        surf.blit(d, d.get_rect(center=cell.center))

    # stoplight pip (red = recent shame) — seated beside the window, clear of
    # the caption strip
    px, py = rect.right - 14, win.centery
    pygame.draw.circle(surf, (20, 20, 24), (px, py), 5)
    pygame.draw.circle(surf, led, (px, py), 3)
    pygame.draw.circle(surf, (255, 255, 255), (px - 1, py - 1), 1)


def histogram(surf, rect, compact=False):
    """Death-pillar histogram: obsidian card of bars by pillar number; the
    nemesis bar burns red while the rest stay gold. NEMESIS #7 tag now sits in a
    red chip so the one emotional beat lands."""
    _panel(surf, rect, radius=11)
    _sheen(surf, rect, 8)
    _cap_left(surf, rect.x + 12, rect.y + 11, "WHERE YOU DIE", size=9,
              col=_GOLD_PALE, alpha=205)
    # high-contrast nemesis tag — red chip behind pale text
    tag = _font(8, True).render("NEMESIS  #7", True, (255, 232, 224))
    chip = pygame.Rect(rect.right - tag.get_width() - 18, rect.y + 5,
                       tag.get_width() + 10, 15)
    _soft_glow(surf, chip.centerx, chip.centery, 12, _NEMESIS, 40, layers=3)
    surf.blit(_vgrad_panel(chip.w, chip.h, 4, (220, 70, 52),
                           _NEMESIS_DEEP, 255), chip.topleft)
    pygame.draw.rect(surf, (255, 170, 150), chip, width=1, border_radius=4)
    surf.blit(tag, tag.get_rect(center=chip.center))

    top = rect.y + 26
    plot = pygame.Rect(rect.x + 12, top, rect.w - 24, rect.bottom - top - 14)
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
            _soft_glow(surf, br.centerx, br.centery, 13, _NEMESIS, 56,
                       layers=3)
            surf.blit(_vgrad_panel(br.w, max(2, br.h), 2,
                                   (240, 100, 82), _NEMESIS_DEEP, 255),
                      br.topleft)
            pygame.draw.rect(surf, (255, 190, 170), br, width=1)
        else:
            surf.blit(_vgrad_panel(br.w, max(2, br.h), 2,
                                   (236, 190, 96), (150, 110, 40), 245),
                      br.topleft)
        # pillar-number axis ticks under the bars
        if not compact:
            nimg = _font(6, True).render(str(i + 1), True,
                                         (150, 134, 96))
            surf.blit(nimg, nimg.get_rect(center=(br.centerx, base + 6)))


def _back(surf):
    r = pygame.Rect(0, 0, 150, 32)
    r.center = (W // 2, BACK_CY)
    _drop_shadow(surf, r, 16, blur=4, alpha=90)
    surf.blit(_vgrad_panel(r.w, r.h, 16, (40, 32, 56), (22, 16, 38), 240),
              r.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 185), r, width=1, border_radius=16)
    t = _font(16, True).render("BACK", True, _GOLD_PALE)
    surf.blit(t, t.get_rect(center=r.center))


# ── version composers (differ only in lower-third solution) ──────────────────

def version_A(surf):
    """A — Tall histogram fills the column. PB grid + counters + safety board,
    then the histogram grows to consume all remaining height down to BACK."""
    _bg(surf); _title(surf)
    switcher(surf, 48, active=1)
    y = COL_TOP
    y = pb_grid(surf, y, tile_h=52)
    y += 6
    counter_row(surf, pygame.Rect(SIDE, y, W - 2 * SIDE, 40))
    y += 40 + 8
    _module_rule(surf, y - 2)
    y += 4
    safety_board(surf, pygame.Rect(SIDE, y, W - 2 * SIDE, 84))
    y += 84 + 8
    _module_rule(surf, y - 2)
    y += 4
    # histogram fills the rest of the column down to the BACK margin
    histogram(surf, pygame.Rect(SIDE, y, W - 2 * SIDE, COL_BOT - y))
    _back(surf)


def version_B(surf):
    """B — Safety board + histogram share one base row (board left, histogram
    right), freeing vertical room for a 'NEXT FRONTIER' teaser strip of the
    upcoming module above BACK."""
    _bg(surf); _title(surf)
    switcher(surf, 48, active=1)
    y = COL_TOP
    y = pb_grid(surf, y, tile_h=50)
    y += 6
    counter_row(surf, pygame.Rect(SIDE, y, W - 2 * SIDE, 40))
    y += 40 + 8
    _module_rule(surf, y - 2)
    y += 4
    # shared row: board (left) + histogram (right)
    row_h = 150
    bw = 150
    safety_board(surf, pygame.Rect(SIDE, y, bw, row_h))
    histogram(surf, pygame.Rect(SIDE + bw + 8, y,
                                W - 2 * SIDE - bw - 8, row_h), compact=True)
    y += row_h + 8
    _module_rule(surf, y - 2)
    y += 6
    # teaser strip of the next module fills freed space
    teaser = pygame.Rect(SIDE, y, W - 2 * SIDE, COL_BOT - y)
    _panel(surf, teaser, radius=11, top=(34, 28, 46), bot=(20, 16, 32))
    _sheen(surf, teaser, 8)
    _gem(surf, teaser.x + 26, teaser.centery, 12, "epic", t=T, mystery=True)
    _gradient_text(surf, "NEXT FRONTIER", _font(13, True),
                   (teaser.centerx + 14, teaser.centery - 7),
                   (235, 210, 255), (170, 130, 230), shadow=True)
    _cap(surf, teaser.centerx + 14, teaser.centery + 10,
         "REACH 1,500 TO UNLOCK", size=8, col=(190, 170, 220), alpha=210)
    _back(surf)


def version_C(surf):
    """C — Shorter centered column with deliberate even spacing. Modules sized
    snugly and the whole stack vertically centred in the content column, so the
    gaps are uniform rather than a dead lower third."""
    _bg(surf); _title(surf)
    switcher(surf, 48, active=1)
    # measure the stack, then centre it in [COL_TOP, COL_BOT]
    tile_h = 50
    pb_h = 2 * tile_h + 6
    count_h = 40
    board_h = 82
    hist_h = 92
    gap = 14
    stack_h = pb_h + count_h + board_h + hist_h + 3 * gap
    y = COL_TOP + max(0, (COL_BOT - COL_TOP - stack_h) // 2)
    y = pb_grid(surf, y, tile_h=tile_h)
    y += gap - 6
    counter_row(surf, pygame.Rect(SIDE, y, W - 2 * SIDE, count_h))
    y += count_h + gap
    _module_rule(surf, y - gap // 2)
    safety_board(surf, pygame.Rect(SIDE, y, W - 2 * SIDE, board_h))
    y += board_h + gap
    _module_rule(surf, y - gap // 2)
    histogram(surf, pygame.Rect(SIDE, y, W - 2 * SIDE, hist_h))
    _back(surf)


VERSIONS = [
    ("A  TALL HISTOGRAM", version_A),
    ("B  SHARED ROW + TEASER", version_B),
    ("C  CENTERED EVEN SPACING", version_C),
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
        sheet.blit(frame, (x, pad + label_h))
        pygame.draw.rect(sheet, _GOLD_DEEP,
                         (x - 1, pad + label_h - 1, W + 2, H + 2), 1)
        lbl = lf.render(name, True, _GOLD_PALE)
        sheet.blit(lbl, (x + 4, pad // 2 - 2))
    out = "/home/user/skybit/docs/profile/screen_layout/round_2.png"
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
