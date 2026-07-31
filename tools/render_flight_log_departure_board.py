"""
Flight Log screen concept — `departure_board`.

A vintage Solari split-flap airline departure board — the black flip-card
boards found in airports. Pure industrial aviation aesthetic. 7 destination
rows (one per biome phase). The HERO MECHANIC is the death row showing a
frozen mid-flip: the card is split horizontally at the midpoint with the
top half showing the old "DEPARTED" face and the bottom half showing the
new "CANCELLED" face, as if the board froze mid-rotation.
"""
import os
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

pygame.display.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
OUT_DIR = os.path.join(ROOT, "docs", "flight_log_screen", "departure_board")
os.makedirs(OUT_DIR, exist_ok=True)

SW, SH = 360, 640

# ── palette ──────────────────────────────────────────────────────────────────
BG            = (8,   8,  20)
BOARD_BLACK   = (14,  14,  22)
CARD_BG       = (18,  18,  28)
CARD_TEXT     = (240, 240, 245)
CARD_FLIP_TOP = (40,  40,  58)
CARD_FLIP_BOT = (30,  30,  46)
DEPART_GREEN  = (80,  200, 100)
CANCEL_AMBER  = (240, 165,  20)
SCHED_GREY    = (120, 120, 140)
RAIL_LIGHT    = (165, 170, 175)
RAIL_MID      = (130, 135, 140)
RAIL_DARK     = ( 95, 100, 105)
RIVET         = (100, 108, 118)
RIVET_HI      = (180, 188, 195)
HAIRLINE      = ( 60,  60,  80)
TICKER_RED    = (220,  60,  50)
GOLD          = (240, 192,  64)
DEATH_RED     = (172,  40,  32)
COL_RULE      = ( 35,  35,  55)
DEPART_AMBER  = (240, 165,  20)

# ── phase data ───────────────────────────────────────────────────────────────
PHASES = [
    (0.000, "DAY",        "MORNING LAUNCH", "GY-15", "06:00", "CANCELLED"),  # death row
    (0.231, "GOLDEN HOUR","GOLDEN COAST",   "GL-23", "08:31", "SCHEDULED"),
    (0.363, "SUNSET",     "SUNSET TERRACE", "SS-37", "09:43", "SCHEDULED"),
    (0.513, "DUSK",       "DUSK RANGE",     "DK-51", "11:23", "SCHEDULED"),
    (0.644, "NIGHT",      "NIGHTFALL",      "NT-64", "12:54", "SCHEDULED"),
    (0.794, "PREDAWN",    "PREDAWN ISLE",   "PD-79", "14:24", "SCHEDULED"),
    (0.906, "SUNRISE",    "SUNRISE PEAK",   "SR-91", "15:36", "SCHEDULED"),
]

# ── helpers ───────────────────────────────────────────────────────────────────
def lerp_c(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def blit_center_x(surf, text_surf, cy, x0, x1):
    """Blit text_surf centred horizontally within [x0, x1] at vertical y=cy."""
    x = x0 + (x1 - x0 - text_surf.get_width()) // 2
    surf.blit(text_surf, (x, cy))


# ── fonts ─────────────────────────────────────────────────────────────────────
font_7  = pygame.font.Font(FONT_PATH,  7)
font_8  = pygame.font.Font(FONT_PATH,  8)
font_9  = pygame.font.Font(FONT_PATH,  9)
font_10 = pygame.font.Font(FONT_PATH, 10)
font_11 = pygame.font.Font(FONT_PATH, 11)
font_12 = pygame.font.Font(FONT_PATH, 12)
font_14 = pygame.font.Font(FONT_PATH, 14)
font_16 = pygame.font.Font(FONT_PATH, 16)
font_18 = pygame.font.Font(FONT_PATH, 18)

# ── surface ───────────────────────────────────────────────────────────────────
surf = pygame.Surface((SW, SH))
surf.fill(BG)

# ─────────────────────────────────────────────────────────────────────────────
# BRUSHED ALUMINUM RAILS
# ─────────────────────────────────────────────────────────────────────────────

def draw_rail(surf, y0, y1, rivet_cy):
    """Draw a brushed aluminum rail with scan lines and rivets."""
    h = y1 - y0
    # Gradient fill (top lighter → bottom darker)
    for dy in range(h):
        t = dy / max(h - 1, 1)
        c = lerp_c(RAIL_LIGHT, RAIL_DARK, t)
        pygame.draw.line(surf, c, (0, y0 + dy), (SW - 1, y0 + dy))

    # Subtle horizontal brushing — alternating lighter/darker scan lines
    for dy in range(0, h, 2):
        pygame.draw.line(surf, RAIL_LIGHT, (0, y0 + dy), (SW - 1, y0 + dy))

    # Bottom edge shadow
    pygame.draw.line(surf, (70, 74, 78), (0, y1 - 1), (SW - 1, y1 - 1))

    # Rivets
    rivet_xs = [20, 72, 124, 180, 236, 288, 340]
    r = 5
    for rx in rivet_xs:
        # Shadow
        pygame.draw.circle(surf, (80, 85, 90), (rx + 1, rivet_cy + 1), r)
        # Body
        pygame.draw.circle(surf, RIVET, (rx, rivet_cy), r)
        # Highlight dot
        pygame.draw.circle(surf, RIVET_HI, (rx - 1, rivet_cy - 1), 2)


draw_rail(surf, 0, 45, 22)
draw_rail(surf, 595, 640, 617)

# ─────────────────────────────────────────────────────────────────────────────
# LED TICKER STRIP  y=45..68
# ─────────────────────────────────────────────────────────────────────────────
pygame.draw.rect(surf, (10, 10, 18), (0, 45, SW, 18))
# LED indicator blobs left
for bx, by in [(8, 50), (16, 50)]:
    pygame.draw.rect(surf, (60, 10, 10), (bx, by, 5, 5))     # dim background
pygame.draw.rect(surf, TICKER_RED, (8, 50, 5, 5))            # active LED

ticker_text = "FLT 001   DAY 1   18% FLOWN   0:47 ELAPSED"
t_surf = font_10.render(ticker_text, True, TICKER_RED)
surf.blit(t_surf, (28, 53))

# ─────────────────────────────────────────────────────────────────────────────
# COLUMN HEADER STRIPE  y=68..80
# ─────────────────────────────────────────────────────────────────────────────
pygame.draw.rect(surf, (28, 28, 40), (0, 68, SW, 12))
# Subtle bottom rule
pygame.draw.line(surf, COL_RULE, (0, 79), (SW - 1, 79), 1)

# Column header labels
headers = [
    ("DESTINATION", 6,   0, 180),
    ("GATE",       180, 180, 240),
    ("DEPT",       240, 240, 300),
    ("STATUS",     300, 300, 360),
]
for label, lx, cx0, cx1 in headers:
    h_surf = font_7.render(label, True, SCHED_GREY)
    surf.blit(h_surf, (lx + 4, 70))

# ─────────────────────────────────────────────────────────────────────────────
# CARD ROWS
# ─────────────────────────────────────────────────────────────────────────────
ROW_H   = 64   # visible card height
ROW_GAP = 4    # gap between rows (BG colour shows through)
ROW_START = 80

# Full-height column dividers (drawn once, behind all cards)
col_xs = [180, 240, 300]

# Column x-ranges for centering:
COL_DEST_X0,  COL_DEST_X1  =   0, 180
COL_GATE_X0,  COL_GATE_X1  = 180, 240
COL_DEPT_X0,  COL_DEPT_X1  = 240, 300
COL_STAT_X0,  COL_STAT_X1  = 300, 360

for i, (phase_t, phase_name, dest, gate, dept_time, status) in enumerate(PHASES):
    row_y = ROW_START + i * (ROW_H + ROW_GAP)
    is_death = (i == 0)

    # ── card background ──────────────────────────────────────────────────────
    pygame.draw.rect(surf, CARD_BG, (0, row_y, SW, ROW_H))

    # Column divider rules
    for cx in col_xs:
        pygame.draw.line(surf, COL_RULE, (cx, row_y), (cx, row_y + ROW_H), 1)

    if is_death:
        # ── HERO: FROZEN MID-FLIP CARD ───────────────────────────────────────
        flip_y = row_y + ROW_H // 2    # midpoint = row_y + 32

        # Font for STATUS column — size 9 across all rows
        font_status = font_9
        status_h = font_status.size("DEPARTED")[1]

        # Pre-compute bisection y positions — text vertically centered at flip_y
        d_surf_top = font_11.render(dest, True, CARD_TEXT)
        dest_bisect_y = flip_y - d_surf_top.get_height() // 2

        gate_surf_top = font_11.render(gate, True, CANCEL_AMBER)
        gate_bisect_y = flip_y - gate_surf_top.get_height() // 2

        dept_surf_top = font_11.render(dept_time, True, CARD_TEXT)
        dept_bisect_y = flip_y - dept_surf_top.get_height() // 2

        departed_y = flip_y - status_h // 2

        # ---- TOP HALF: old face (DEPARTED) ----------------------------------
        surf.set_clip(pygame.Rect(0, row_y, SW, ROW_H // 2))

        pygame.draw.rect(surf, CARD_FLIP_TOP, (0, row_y, SW, ROW_H))

        # Top-half column dividers
        for cx in col_xs:
            pygame.draw.line(surf, (50, 50, 70), (cx, row_y), (cx, flip_y), 1)

        # DESTINATION — bisected at flip_y; phase label sits at top of card
        surf.blit(d_surf_top, (8, dest_bisect_y))
        ph_surf = font_8.render(phase_name, True, (160, 160, 180))
        surf.blit(ph_surf, (8, row_y + 4))

        # GATE — bisected at flip_y
        blit_center_x(surf, gate_surf_top, gate_bisect_y, COL_GATE_X0, COL_GATE_X1)

        # DEPT TIME — bisected at flip_y
        blit_center_x(surf, dept_surf_top, dept_bisect_y, COL_DEPT_X0, COL_DEPT_X1)

        # STATUS top half — "DEPARTED" in green, bisected at flip_y
        dep_label = font_status.render("DEPARTED", True, DEPART_GREEN)
        blit_center_x(surf, dep_label, departed_y, COL_STAT_X0, COL_STAT_X1)

        # Glare highlight along the top edge of the top half
        for gx in range(0, SW, 4):
            pygame.draw.line(surf, (60, 60, 80), (gx, flip_y - 3), (gx, flip_y - 1))

        # ---- BOTTOM HALF: new face (CANCELLED) ------------------------------
        surf.set_clip(pygame.Rect(0, flip_y, SW, ROW_H - ROW_H // 2))

        # Slightly different shade — freshly fallen card
        pygame.draw.rect(surf, CARD_FLIP_BOT, (0, row_y, SW, ROW_H))

        # Bottom-half column dividers
        for cx in col_xs:
            pygame.draw.line(surf, (50, 50, 70), (cx, flip_y), (cx, row_y + ROW_H), 1)

        # DESTINATION bottom half — same bisect position as top (clip shows lower half)
        d2_surf = font_11.render(dest, True, CARD_TEXT)
        surf.blit(d2_surf, (8, dest_bisect_y))
        # "CANCELLED" sub-label sits below flip_y on the new card face
        can_dest = font_8.render("CANCELLED", True, CANCEL_AMBER)
        surf.blit(can_dest, (8, flip_y + 2))

        # GATE bottom half — dash, bisected at flip_y
        dash = font_11.render("—", True, (60, 60, 80))
        dash_y = flip_y - dash.get_height() // 2
        blit_center_x(surf, dash, dash_y, COL_GATE_X0, COL_GATE_X1)

        # DEPT TIME bottom half — dash, bisected at flip_y
        blit_center_x(surf, dash, dash_y, COL_DEPT_X0, COL_DEPT_X1)

        # STATUS bottom half — "CANCELLED" in amber, bisected at flip_y
        cancel_y = flip_y - status_h // 2
        can_surf = font_status.render("CANCELLED", True, CANCEL_AMBER)
        blit_center_x(surf, can_surf, cancel_y, COL_STAT_X0, COL_STAT_X1)

        # ---- Release clip ------------------------------------------------
        surf.set_clip(None)

        # ---- Left-margin accent stripe (full row height) ----------------
        pygame.draw.rect(surf, DEATH_RED, (0, row_y, 4, ROW_H))

        # ---- Hairline split line -----------------------------------------
        # Main split
        pygame.draw.line(surf, HAIRLINE, (0, flip_y), (SW - 1, flip_y), 2)
        # Subtle shadow below split
        pygame.draw.line(surf, (20, 20, 35), (0, flip_y + 2), (SW - 1, flip_y + 2), 1)
        # Subtle highlight above split
        pygame.draw.line(surf, (50, 50, 70), (0, flip_y - 1), (SW - 1, flip_y - 1), 1)

        # ---- Amber warning glow on split line ----------------------------
        glow_surf = pygame.Surface((SW, 6), pygame.SRCALPHA)
        for gy in range(6):
            alpha = int(60 * (1 - abs(gy - 2) / 4))
            pygame.draw.line(glow_surf, (*CANCEL_AMBER, alpha), (0, gy), (SW - 1, gy))
        surf.blit(glow_surf, (0, flip_y - 1))

        # ---- Death indicator in left margin ----------------------------
        # Small red triangle / exclamation in the gap to the left
        pygame.draw.polygon(surf, DEATH_RED, [
            (2, flip_y - 8),
            (9, flip_y - 8),
            (5, flip_y - 16),
        ])
        warn_surf = font_7.render("!", True, (255, 220, 180))
        surf.blit(warn_surf, (4, flip_y - 13))

    else:
        # ── NORMAL SCHEDULED ROW ─────────────────────────────────────────────
        dim = SCHED_GREY

        # Phase name (small, above destination)
        ph_surf = font_7.render(phase_name, True, SCHED_GREY)
        surf.blit(ph_surf, (8, row_y + 4))

        # Destination name
        d_surf = font_11.render(dest, True, dim)
        surf.blit(d_surf, (8, row_y + 18))

        # GATE
        g_surf = font_10.render(gate, True, dim)
        blit_center_x(surf, g_surf, row_y + 18, COL_GATE_X0, COL_GATE_X1)

        # DEPT TIME
        t_surf_s = font_10.render(dept_time, True, dim)
        blit_center_x(surf, t_surf_s, row_y + 18, COL_DEPT_X0, COL_DEPT_X1)

        # STATUS — "SCHEDULED" with a leading dot indicator
        stat_surf = font_9.render("SCHEDULED", True, dim)
        blit_center_x(surf, stat_surf, row_y + 16, COL_STAT_X0, COL_STAT_X1)

        # Small status dot
        dot_x = COL_STAT_X0 + (COL_STAT_X1 - COL_STAT_X0) // 2 - stat_surf.get_width() // 2 - 4
        pygame.draw.circle(surf, (60, 60, 80), (dot_x, row_y + 20), 3)

        # Dim slot-number in bottom-right corner of card
        slot_txt = font_8.render(f"{i+1:02d}", True, (45, 45, 65))
        surf.blit(slot_txt, (SW - 16, row_y + ROW_H - 14))

# ─────────────────────────────────────────────────────────────────────────────
# FULL-HEIGHT COLUMN DIVIDERS (drawn over everything)
# ─────────────────────────────────────────────────────────────────────────────
total_rows = len(PHASES)
board_end = ROW_START + total_rows * (ROW_H + ROW_GAP) - 6
for cx in col_xs:
    pygame.draw.line(surf, (45, 45, 68), (cx, 80), (cx, board_end - ROW_GAP), 1)

# ─────────────────────────────────────────────────────────────────────────────
# STATUS BAR  (below last row, above bottom rail)
# ─────────────────────────────────────────────────────────────────────────────
stats_y = board_end
stats_h = 595 - stats_y
if stats_h > 0:
    pygame.draw.rect(surf, (12, 12, 20), (0, stats_y, SW, stats_h))
    # Thin top rule
    pygame.draw.line(surf, (40, 40, 60), (0, stats_y), (SW - 1, stats_y), 1)

stats_text = "PILLAR 25  ·  DAY 1  ·  18% FLOWN  ·  FLIGHT CANCELLED"
st_surf = font_9.render(stats_text, True, CANCEL_AMBER)
st_x = (SW - st_surf.get_width()) // 2
st_y = stats_y + max((stats_h - st_surf.get_height()) // 2, 2)
surf.blit(st_surf, (st_x, st_y))

# ─────────────────────────────────────────────────────────────────────────────
# BACK BUTTON  (inside bottom rail)
# ─────────────────────────────────────────────────────────────────────────────
btn_x, btn_y, btn_w, btn_h = 130, 613, 100, 22
pygame.draw.rect(surf, RAIL_MID, (btn_x, btn_y, btn_w, btn_h), border_radius=6)
pygame.draw.rect(surf, RAIL_LIGHT, (btn_x, btn_y, btn_w, btn_h), width=1, border_radius=6)
back_surf = font_12.render("BACK", True, BOARD_BLACK)
bx_c = btn_x + (btn_w - back_surf.get_width()) // 2
by_c = btn_y + (btn_h - back_surf.get_height()) // 2
surf.blit(back_surf, (bx_c, by_c))

# ─────────────────────────────────────────────────────────────────────────────
# TITLE in top rail
# ─────────────────────────────────────────────────────────────────────────────
title_surf = font_12.render("FLIGHT LOG", True, BOARD_BLACK)
t_x = (SW - title_surf.get_width()) // 2
surf.blit(title_surf, (t_x, 14))

# Thin etched underline
pygame.draw.line(surf, (80, 85, 90), (t_x - 2, 29), (t_x + title_surf.get_width() + 2, 29), 1)

# ─────────────────────────────────────────────────────────────────────────────
# VIGNETTE — subtle darkness at edges
# ─────────────────────────────────────────────────────────────────────────────
vignette = pygame.Surface((SW, SH), pygame.SRCALPHA)
for vx in range(0, 40):
    alpha = int(80 * (1 - vx / 40))
    pygame.draw.line(vignette, (0, 0, 0, alpha), (vx, 45), (vx, 595))
    pygame.draw.line(vignette, (0, 0, 0, alpha), (SW - 1 - vx, 45), (SW - 1 - vx, 595))
surf.blit(vignette, (0, 0))

# ─────────────────────────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────────────────────────
out = os.path.join(OUT_DIR, "round_2.png")
pygame.image.save(surf, out)
print(f"saved {out}")
