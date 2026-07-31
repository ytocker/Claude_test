"""Render: nav_log Flight Log — Round 2

IFR navigation log (kneeboard form) on a dark leather clipboard.
7 phase rows; death row (DAY) has a red line-through, not a stamp.
"""
import math
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame  # noqa: E402

pygame.display.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
OUT_DIR = os.path.join(ROOT, "docs", "flight_log_screen", "nav_log")
os.makedirs(OUT_DIR, exist_ok=True)

# ── colour palette ─────────────────────────────────────────────────────────────
BG             = (8,   8,  20)
CLIPBOARD_DARK = (42,  28,  18)
CLIPBOARD_MID  = (58,  38,  22)
CLIPBOARD_EDGE = (72,  50,  30)
PAPER_WHITE    = (250, 250, 248)
PAPER_RULE     = (180, 195, 220)
INK_DARK       = (15,  25,  50)
INK_GREY       = (140, 140, 150)
INK_CHECK      = (20, 100,  40)
DEATH_RED      = (172,  40,  32)
GOLD           = (240, 192,  64)
SILVER         = (180, 188, 200)

# ── canvas ─────────────────────────────────────────────────────────────────────
CW, CH = 360, 640
surf = pygame.Surface((CW, CH))

# ── font cache ─────────────────────────────────────────────────────────────────
_FONT_CACHE: dict = {}


def fnt(px: int) -> pygame.font.Font:
    f = _FONT_CACHE.get(px)
    if f is None:
        f = pygame.font.Font(FONT_PATH, px)
        _FONT_CACHE[px] = f
    return f


def draw_text(surface: pygame.Surface, msg: str, x: int, y: int,
              px: int, col: tuple, align: str = "left") -> int:
    """Render antialiased text; return rendered pixel width."""
    t = fnt(px).render(msg, True, col)
    if align == "center":
        x -= t.get_width() // 2
    elif align == "right":
        x -= t.get_width()
    surface.blit(t, (x, y))
    return t.get_width()


def alpha_rect(surface: pygame.Surface, col_rgba: tuple,
               x: int, y: int, w: int, h: int) -> None:
    """Blit a solid SRCALPHA rectangle onto surface."""
    tmp = pygame.Surface((w, h), pygame.SRCALPHA)
    tmp.fill(col_rgba)
    surface.blit(tmp, (x, y))


# ── phase data ─────────────────────────────────────────────────────────────────
PHASE_BOUNDARIES = [
    (0.000, "DAY",         "ROOST", "GOLHR"),
    (0.231, "GOLDEN HOUR", "GOLHR", "SUNST"),
    (0.363, "SUNSET",      "SUNST", "DUSKK"),
    (0.513, "DUSK",        "DUSKK", "NYTIM"),
    (0.644, "NIGHT",       "NYTIM", "PREDN"),
    (0.794, "PREDAWN",     "PREDN", "SUNRS"),
    (0.906, "SUNRISE",     "SUNRS", "ROOST"),
]

# Display names for unflown rows (1-6)
PHASE_SHORT = ["GOLDEN", "SUNSET", "DUSK", "NIGHT", "PREDWN", "SUNRS"]

# Short FROM→TO nav leg labels — abbreviated to fit 80px column (index 0 = DAY row)
NAV_LEGS = ["RST→GLD", "GLD→SUN", "SUN→DSK", "DSK→NGT", "NGT→PRD", "PRD→SRS", "SRS→RST"]

# Estimated time en-route for each phase row (index 0 = DAY)
ETE_LIST = ["27:00", "42:00", "48:00", "40:00", "37:00", "45:00", "28:00"]

# Notes for unflown rows (indices 0-5 map to rows 1-6)
UNFLOWN_NOTES = ["", "CLWN/STM", "", "", "SNOW SQN", ""]

DEATH_FRAC = 0.184  # fraction of day; falls in row 0 (DAY: 0.000-0.231)

# ── layout constants ───────────────────────────────────────────────────────────
PAPER_X    = 22
PAPER_Y    = 50
PAPER_W    = 316
PAPER_H    = 560
PAPER_R    = PAPER_X + PAPER_W   # 338
PAPER_BOT  = PAPER_Y + PAPER_H   # 610

FORM_HDR_BOT = 108   # bottom of header block
COL_HDR_BOT  = 130   # bottom of column-header strip

ROW_H       = 46     # tighter rows (was 62); 7 rows × 46 = 322px
ROW_START_Y = COL_HDR_BOT
N_ROWS      = 7
STATS_Y     = ROW_START_Y + N_ROWS * ROW_H  # 130 + 322 = 452

# Column x boundaries on canvas
COL_X = [22, 72, 152, 192, 232, 338]  # left edge of each col; last = right edge

# ╔══════════════════════════════════════════════════════════════╗
# ║  1. BACKGROUND                                               ║
# ╚══════════════════════════════════════════════════════════════╝
surf.fill(BG)

# ╔══════════════════════════════════════════════════════════════╗
# ║  2. LEATHER CLIPBOARD FRAME                                  ║
# ╚══════════════════════════════════════════════════════════════╝
# Body fill — dark brown leather
pygame.draw.rect(surf, CLIPBOARD_DARK, (12, 20, 336, 608), border_radius=6)

# Subtle inner edge highlight — lighter strip to suggest leather bevel
inner = pygame.Surface((334, 606), pygame.SRCALPHA)
for depth, alpha in [(0, 60), (1, 35), (2, 18)]:
    pygame.draw.rect(inner, CLIPBOARD_MID + (alpha,),
                     (depth, depth, 334 - depth * 2, 606 - depth * 2),
                     1, border_radius=max(1, 5 - depth))
surf.blit(inner, (13, 21))

# Outer edge highlight
pygame.draw.rect(surf, CLIPBOARD_EDGE, (12, 20, 336, 608), width=2, border_radius=6)

# Leather grain — subtle diagonal texture lines
grain = pygame.Surface((336, 608), pygame.SRCALPHA)
for gx in range(0, 336 + 608, 18):
    pygame.draw.line(grain, (80, 55, 32, 22), (gx, 0), (gx - 608, 608), 1)
surf.blit(grain, (12, 20))

# ╔══════════════════════════════════════════════════════════════╗
# ║  3. METAL CLIP BAR + RIVETS                                  ║
# ╚══════════════════════════════════════════════════════════════╝
# Clip bar body
pygame.draw.rect(surf, SILVER, (130, 18, 100, 22), border_radius=4)
# Highlight on top edge
pygame.draw.line(surf, (210, 218, 228), (132, 19), (228, 19), 1)
# Shadow on bottom edge
pygame.draw.line(surf, (130, 138, 150), (132, 38), (228, 38), 1)

# Rivet bolts
for bolt_x in (165, 195):
    pygame.draw.circle(surf, (120, 128, 140), (bolt_x, 29), 4)
    pygame.draw.circle(surf, (200, 208, 218), (bolt_x, 28), 2)  # highlight
    pygame.draw.circle(surf, (80,  88,  96),  (bolt_x, 29), 4, 1)  # rim

# ╔══════════════════════════════════════════════════════════════╗
# ║  4. PAPER FORM (white kneeboard stock)                       ║
# ╚══════════════════════════════════════════════════════════════╝
pygame.draw.rect(surf, PAPER_WHITE, (PAPER_X, PAPER_Y, PAPER_W, PAPER_H))

# Very subtle drop shadow on paper right + bottom edges
for s_off, s_alpha in [(1, 40), (2, 22), (3, 10)]:
    alpha_rect(surf, (0, 0, 0, s_alpha),
               PAPER_X + PAPER_W, PAPER_Y + s_off, 3, PAPER_H)
    alpha_rect(surf, (0, 0, 0, s_alpha),
               PAPER_X + s_off, PAPER_Y + PAPER_H, PAPER_W, 3)

# ╔══════════════════════════════════════════════════════════════╗
# ║  5. FORM HEADER                                              ║
# ╚══════════════════════════════════════════════════════════════╝
draw_text(surf, "PILOT NAVIGATION LOG", CW // 2, 58, 12, INK_DARK, align="center")

# Row 2: aircraft + date
draw_text(surf, "AIRCRAFT:", 30, 76, 8, INK_GREY)
draw_text(surf, "SKYBIT PARROT-1", 78, 76, 8, INK_DARK)
draw_text(surf, "DATE:", 190, 76, 8, INK_GREY)
draw_text(surf, "DAY 1", 218, 76, 8, INK_DARK)

# Row 3: route
draw_text(surf, "FROM:", 30, 90, 8, INK_GREY)
draw_text(surf, "ROOST", 58, 90, 8, INK_DARK)
draw_text(surf, "TO:", 130, 90, 8, INK_GREY)
draw_text(surf, "DESTINATION", 148, 90, 8, INK_DARK)

# Header-bottom rule
pygame.draw.line(surf, INK_DARK, (PAPER_X, FORM_HDR_BOT), (PAPER_R, FORM_HDR_BOT), 1)

# ╔══════════════════════════════════════════════════════════════╗
# ║  6. COLUMN HEADERS                                           ║
# ╚══════════════════════════════════════════════════════════════╝
draw_text(surf, "PHASE",   COL_X[0] + 3, 112, 8, INK_DARK)
draw_text(surf, "FROM→TO", COL_X[1] + 3, 112, 8, INK_DARK)
draw_text(surf, "ETE",     COL_X[2] + 3, 112, 8, INK_DARK)
draw_text(surf, "ATE",     COL_X[3] + 3, 112, 8, INK_DARK)
draw_text(surf, "NOTES",   COL_X[4] + 3, 112, 8, INK_DARK)

# Column-header bottom rule
pygame.draw.line(surf, INK_DARK, (PAPER_X, COL_HDR_BOT), (PAPER_R, COL_HDR_BOT), 1)

# ── vertical column rules (faint blue, span header + all rows) ─────────────────
v_rule_h = STATS_Y - FORM_HDR_BOT   # from header rule down to stats line
v_rule_surf = pygame.Surface((PAPER_W, v_rule_h), pygame.SRCALPHA)
for rule_x in [COL_X[1] - PAPER_X,
               COL_X[2] - PAPER_X,
               COL_X[3] - PAPER_X,
               COL_X[4] - PAPER_X]:
    pygame.draw.line(v_rule_surf, (0, 60, 140, 38),
                     (rule_x, 0), (rule_x, v_rule_h), 1)
surf.blit(v_rule_surf, (PAPER_X, FORM_HDR_BOT))

# ╔══════════════════════════════════════════════════════════════╗
# ║  7. PHASE ROWS                                               ║
# ╚══════════════════════════════════════════════════════════════╝
for i in range(N_ROWS):
    y_top = ROW_START_Y + i * ROW_H
    y_bot = y_top + ROW_H

    # Subtle mid-row ruling — makes empty space read as intentional writing lines
    alpha_rect(surf, (180, 195, 220, 60), PAPER_X, y_top + 24, PAPER_W, 1)

    if i == 0:
        # ── DEATH ROW (DAY phase, death at 18.4%) ─────────────────────────────
        # Red wash — boosted alpha for clear visibility
        alpha_rect(surf, (172, 40, 32, 55), PAPER_X + 1, y_top, PAPER_W - 2, ROW_H)

        # Row content — filled in as if pilot was logging
        draw_text(surf, "DAY",        COL_X[0] + 3, y_top + 8, 9, INK_DARK)
        draw_text(surf, NAV_LEGS[0],  COL_X[1] + 3, y_top + 8, 8, INK_DARK)
        draw_text(surf, ETE_LIST[0],  COL_X[2] + 3, y_top + 8, 8, INK_DARK)
        draw_text(surf, "0:47",       COL_X[3] + 3, y_top + 8, 8, INK_DARK)
        draw_text(surf, "GEYSR ACTV", COL_X[4] + 3, y_top + 8, 7, INK_DARK)

        # STRIKETHROUGH — two parallel red lines (moved UP to before annotation)
        pygame.draw.line(surf, DEATH_RED, (24, y_top + 14), (336, y_top + 14), 2)
        pygame.draw.line(surf, DEATH_RED, (24, y_top + 22), (336, y_top + 22), 2)

        # Third shorter line at 50% alpha — adds depth beneath the main strikes
        alpha_rect(surf, (172, 40, 32, 128), 60, y_top + 28, 250, 2)

        # "BIRD DOWN" annotation — placed BELOW both strike lines
        draw_text(surf, "BIRD DOWN", COL_X[4] + 3, y_top + 36, 7, DEATH_RED)

        # Red X in left margin
        x_cx, x_cy = 30, y_top + 24
        pygame.draw.line(surf, DEATH_RED,
                         (x_cx - 4, x_cy - 4), (x_cx + 4, x_cy + 4), 2)
        pygame.draw.line(surf, DEATH_RED,
                         (x_cx + 4, x_cy - 4), (x_cx - 4, x_cy + 4), 2)

    else:
        # ── UNFLOWN ROW ────────────────────────────────────────────────────────
        idx       = i - 1                # 0-based index into PHASE_SHORT etc.
        ph_short  = PHASE_SHORT[idx]
        ete_str   = ETE_LIST[i]
        note_str  = UNFLOWN_NOTES[idx]

        draw_text(surf, ph_short,     COL_X[0] + 3, y_top + 8, 9, INK_GREY)
        draw_text(surf, NAV_LEGS[i],  COL_X[1] + 3, y_top + 8, 8, INK_GREY)
        draw_text(surf, ete_str,      COL_X[2] + 3, y_top + 8, 8, INK_GREY)
        # ATE left blank
        if note_str:
            draw_text(surf, note_str, COL_X[4] + 3, y_top + 8, 7, INK_GREY)

    # Row divider
    pygame.draw.line(surf, INK_GREY, (PAPER_X, y_bot), (PAPER_R, y_bot), 1)

# ╔══════════════════════════════════════════════════════════════╗
# ║  8. STATS BLOCK                                              ║
# ╚══════════════════════════════════════════════════════════════╝
# Double rule at top of stats
pygame.draw.line(surf, INK_DARK, (PAPER_X, STATS_Y),     (PAPER_R, STATS_Y),     2)
pygame.draw.line(surf, INK_DARK, (PAPER_X, STATS_Y + 4), (PAPER_R, STATS_Y + 4), 1)

draw_text(surf, "PILLAR 25  ·  DAY 1  ·  0:47  ·  18% FLOWN",
          CW // 2, STATS_Y + 11, 9, INK_DARK, align="center")
draw_text(surf, "PHASE: DAY  ·  STATUS: MAYDAY",
          CW // 2, STATS_Y + 27, 8, DEATH_RED, align="center")

# ╔══════════════════════════════════════════════════════════════╗
# ║  9. BACK BUTTON                                              ║
# ╚══════════════════════════════════════════════════════════════╝
# Gold outline pill
pygame.draw.rect(surf, GOLD, (105, 617, 150, 24), width=2, border_radius=8)
draw_text(surf, "BACK", 180, 622, 12, GOLD, align="center")

# ╔══════════════════════════════════════════════════════════════╗
# ║  10. EVENT MARKER STRIP (slim vertical timeline, left margin)║
# ╚══════════════════════════════════════════════════════════════╝
EV_Y_TOP = 130
EV_Y_BOT = 564

# Thin vertical timeline line at x=36, inside left paper margin
pygame.draw.line(surf, (180, 195, 220), (36, EV_Y_TOP), (36, EV_Y_BOT), 1)

# Event markers mapped to y proportional within the row block
EVENT_MARKS = [
    (0.15, "geyser"),   # Geysers — gold (active event, caused death)
    (0.41, "clown"),    # Clown — death red diamond
    (0.44, "storm"),    # Storm — orange lightning bolt
    (0.85, "snow"),     # Snow — blue asterisk
]

for frac, kind in EVENT_MARKS:
    ey = int(EV_Y_TOP + frac * (EV_Y_BOT - EV_Y_TOP))
    if kind == "geyser":
        # Small circle radius=4 in warm gold
        pygame.draw.circle(surf, (240, 180, 60), (36, ey), 4, 1)
    elif kind == "clown":
        # Small diamond (4-point rotated square) in DEATH_RED
        pts = [(36, ey - 4), (36 + 4, ey), (36, ey + 4), (36 - 4, ey)]
        pygame.draw.polygon(surf, DEATH_RED, pts, 1)
    elif kind == "storm":
        # Lightning bolt — 3 connected line segments
        c = (180, 80, 20)
        pygame.draw.line(surf, c, (38, ey - 4), (34, ey),     1)
        pygame.draw.line(surf, c, (34, ey),     (37, ey),     1)
        pygame.draw.line(surf, c, (37, ey),     (33, ey + 4), 1)
    elif kind == "snow":
        # Asterisk — 3 lines at 0°, 60°, 120° (radius 4)
        c = (140, 180, 220)
        for angle in [0, 60, 120]:
            rad = math.radians(angle)
            dx = int(round(4 * math.cos(rad)))
            dy = int(round(4 * math.sin(rad)))
            pygame.draw.line(surf, c, (36 - dx, ey - dy), (36 + dx, ey + dy), 1)

# ── save ───────────────────────────────────────────────────────────────────────
out = os.path.join(OUT_DIR, "round_2.png")
pygame.image.save(surf, out)
print(f"saved {out}")
