"""Render: approach_plate Flight Log — Round 5"""
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
OUT_DIR = os.path.join(ROOT, "docs", "flight_log_screen", "approach_plate")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Color palette ─────────────────────────────────────────────────────────────
PAPER          = (245, 248, 250)
INK            = (15, 20, 30)
INK_LIGHT      = (60, 70, 90)
FAA_MAGENTA    = (168, 0, 128)
FAA_BLUE       = (0, 80, 160)
FAA_BLUE_LIGHT = (140, 180, 220)
TERRAIN_SHADE  = (210, 220, 200)
FIX_BOX        = (240, 245, 255)
GREASE_GREEN   = (40, 160, 60)
GREASE_RED     = (180, 30, 20)
GREASE_AMBER   = (200, 140, 20)
GOLD           = (240, 192, 64)
APPROACH_GREY  = (180, 190, 200)
SECTOR_FILL    = (230, 235, 245)

# ── Fonts ─────────────────────────────────────────────────────────────────────
def font(size):
    try:
        return pygame.font.Font(FONT_PATH, size)
    except Exception:
        return pygame.font.SysFont("sans", size)

F6  = font(6)
F7  = font(7)
F8  = font(8)
F9  = font(9)
F10 = font(10)
F12 = font(12)
F14 = font(14)

# ── Canvas ────────────────────────────────────────────────────────────────────
SW, SH = 360, 640
surf = pygame.Surface((SW, SH))
surf.fill(PAPER)

# ── Phase / fix geometry ──────────────────────────────────────────────────────
FIXES = [
    (0.000, "ROOST", None),
    (0.231, "GOLDH", "5000"),
    (0.363, "SUNST", "4000"),
    (0.513, "DUSKK", "3000"),
    (0.644, "NYTIM", "2500"),
    (0.794, "PREDN", "2000"),
    (0.906, "SUNRS", "1500"),
]

DEATH_PHASE = 0.184

def fix_y(p):
    return int(410 - p * 350)

death_y_plan = fix_y(DEATH_PHASE)  # ≈ 346

# ── Helper: dashed line ───────────────────────────────────────────────────────
def dash_line(surface, color, x1, y1, x2, y2, dash=4, gap=3, width=1):
    total = math.hypot(x2 - x1, y2 - y1)
    if total == 0:
        return
    dx = (x2 - x1) / total
    dy = (y2 - y1) / total
    pos = 0
    drawing = True
    while pos < total:
        seg = dash if drawing else gap
        end = min(pos + seg, total)
        if drawing:
            pygame.draw.line(surface, color,
                (int(x1 + dx * pos),  int(y1 + dy * pos)),
                (int(x1 + dx * end),  int(y1 + dy * end)), width)
        pos = end
        drawing = not drawing

# ══════════════════════════════════════════════════════════════════════════════
# DOUBLE BORDER
# ══════════════════════════════════════════════════════════════════════════════
pygame.draw.rect(surf, INK, (2, 2, 356, 636), 2)
pygame.draw.rect(surf, INK, (6, 6, 348, 628), 1)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER BLOCK (y=6 to y=50)
# ══════════════════════════════════════════════════════════════════════════════
HDR_COL = (0, 60, 120)
pygame.draw.rect(surf, HDR_COL, (6, 6, 348, 44))

# Airport ID at left
id_txt = F14.render("SKBT", True, (250, 250, 250))
surf.blit(id_txt, (14, 10))

# Procedure number at right
proc_txt = F8.render("PROC NO: FL-001", True, (250, 250, 250))
surf.blit(proc_txt, (280, 10))

# Main title centered
title_txt = F10.render("IFR APPROACH  NDB-A  SKYBIT FIELD", True, (250, 250, 250))
surf.blit(title_txt, ((360 - title_txt.get_width()) // 2, 16))

# Subtitle centered
sub_txt = F8.render("RWY ALL DIRECTIONS  ·  MIN VIS: 1/4SM", True, (250, 250, 250))
surf.blit(sub_txt, ((360 - sub_txt.get_width()) // 2, 33))

# ══════════════════════════════════════════════════════════════════════════════
# PLAN VIEW (y=50 to y=420)
# ══════════════════════════════════════════════════════════════════════════════

# ── Left margin: protected sector polygon ─────────────────────────────────────
sector_pts = [(10, 80), (48, 70), (52, 180), (50, 320), (14, 340), (8, 200)]
sec_surf = pygame.Surface((SW, SH), pygame.SRCALPHA)
pygame.draw.polygon(sec_surf, SECTOR_FILL + (180,), sector_pts)
surf.blit(sec_surf, (0, 0))
pygame.draw.polygon(surf, FAA_BLUE_LIGHT, sector_pts, 1)

# Dashed border over the sector
for i in range(len(sector_pts)):
    x1, y1 = sector_pts[i]
    x2, y2 = sector_pts[(i + 1) % len(sector_pts)]
    dash_line(surf, FAA_BLUE, x1, y1, x2, y2, dash=4, gap=3)

# Sector labels
surf.blit(F7.render("PROT.", True, FAA_BLUE), (12, 100))
surf.blit(F7.render("SECTOR", True, FAA_BLUE), (9, 112))

# ── Right margin: obstacle data box ───────────────────────────────────────────
pygame.draw.rect(surf, PAPER, (308, 120, 44, 60))
pygame.draw.rect(surf, INK_LIGHT, (308, 120, 44, 60), 1)
surf.blit(F7.render("OBST", True, INK_LIGHT), (320, 124))
surf.blit(F8.render("5280'", True, INK), (316, 136))
# Mountain triangle
pygame.draw.polygon(surf, INK_LIGHT, [(330, 148), (324, 158), (336, 158)])

# ── Main magenta route line ───────────────────────────────────────────────────
pygame.draw.line(surf, FAA_MAGENTA, (180, 410), (180, 60), 2)

# ── Unflown portion overlay (lighter) ────────────────────────────────────────
unflown_surf = pygame.Surface((360, 420), pygame.SRCALPHA)
pygame.draw.line(unflown_surf, (168, 0, 128, 80), (180, 60), (180, death_y_plan), 2)
surf.blit(unflown_surf, (0, 0))

# ── Fix markers ───────────────────────────────────────────────────────────────
ALTITUDES = ["5000", "4000", "3000", "2500", "2000", "1500"]
alt_idx = 0
for (p, name, alt) in FIXES:
    if name == "ROOST":
        # Just a dot at the bottom of route
        pygame.draw.circle(surf, FAA_MAGENTA, (180, fix_y(p)), 4)
        surf.blit(F8.render("ROOST", True, INK), (188, fix_y(p) - 6))
        continue

    fy = fix_y(p)

    # Mileage tick on route
    pygame.draw.line(surf, INK, (175, fy), (185, fy), 1)

    # Fix triangle (pointing down)
    tri_pts = [(180, fy + 8), (170, fy - 6), (190, fy - 6)]
    pygame.draw.polygon(surf, PAPER, tri_pts)
    pygame.draw.polygon(surf, FAA_MAGENTA, tri_pts, 1)

    # Fix label box to the RIGHT
    pygame.draw.rect(surf, FIX_BOX, (195, fy - 10, 52, 20))
    pygame.draw.rect(surf, INK_LIGHT, (195, fy - 10, 52, 20), 1)
    surf.blit(F8.render(name, True, INK), (198, fy - 8))

    # Crossing altitude box to the LEFT
    pygame.draw.rect(surf, PAPER, (78, fy - 10, 96, 20))
    pygame.draw.rect(surf, INK_LIGHT, (78, fy - 10, 96, 20), 1)
    surf.blit(F6.render("AT OR ABOVE", True, INK_LIGHT), (80, fy - 10))
    if alt:
        surf.blit(F9.render(alt + "'", True, INK), (80, fy - 2))

    alt_idx += 1

# ── DEATH FIX on plan view ────────────────────────────────────────────────────
dy = death_y_plan  # ≈ 346

# Red grease-pencil circle
pygame.draw.circle(surf, GREASE_RED, (180, dy), 12, 2)

# X mark
pygame.draw.line(surf, GREASE_RED, (180 - 4, dy - 4), (180 + 4, dy + 4), 2)
pygame.draw.line(surf, GREASE_RED, (180 + 4, dy - 4), (180 - 4, dy + 4), 2)

# Labels to the right
surf.blit(F7.render("DR POSN", True, GREASE_RED), (196, dy - 10))
surf.blit(F7.render("TERRAIN CONTACT", True, GREASE_RED), (196, dy + 2))

# Crash trajectory dashes (diagonal right-down)
dash_line(surf, GREASE_RED, 182, dy + 2, 200, 370, dash=3, gap=3, width=1)

# ── Grease pencil flown annotation ───────────────────────────────────────────
# Yellow highlight strip over flown portion (dy to 410)
hl_surf = pygame.Surface((360, 640), pygame.SRCALPHA)
pygame.draw.rect(hl_surf, (255, 240, 80, 90), (176, dy, 8, 410 - dy))
surf.blit(hl_surf, (0, 0))

# Green checkmark at midpoint of flown route (~y=380)
ck_x, ck_y = 185, 380
pygame.draw.line(surf, GREASE_GREEN, (ck_x, ck_y + 3), (ck_x + 3, ck_y + 6), 2)
pygame.draw.line(surf, GREASE_GREEN, (ck_x + 3, ck_y + 6), (ck_x + 7, ck_y), 2)

# ── Event markers ─────────────────────────────────────────────────────────────
# Geyser at 0.15 → y≈358
gy = fix_y(0.15)
pygame.draw.ellipse(surf, PAPER, (145, gy - 7, 20, 14))
pygame.draw.ellipse(surf, INK_LIGHT, (145, gy - 7, 20, 14), 1)
surf.blit(F6.render("GEYSR", True, INK_LIGHT), (132, gy - 2))

# Clown (MOA) at 0.41 → y≈267
cy_ev = fix_y(0.41)
clown_pts = [(188, cy_ev), (188, cy_ev - 10), (196, cy_ev - 5)]
pygame.draw.polygon(surf, INK_LIGHT, clown_pts)
surf.blit(F6.render("MOA-CL", True, INK_LIGHT), (200, cy_ev - 6))

# Storm at 0.44 → y≈256
sy_ev = fix_y(0.44)
bolt = [(190, sy_ev - 4), (194, sy_ev - 4), (192, sy_ev),
        (196, sy_ev), (192, sy_ev + 4), (193, sy_ev + 1), (189, sy_ev + 1)]
pygame.draw.polygon(surf, INK, bolt)
surf.blit(F6.render("CB/TS", True, INK), (200, sy_ev - 4))

# Snow/ice at 0.85 → y≈112
snow_x, snow_y = 165, fix_y(0.85)
for angle in [0, 60, 120]:
    rad = math.radians(angle)
    pygame.draw.line(surf, INK_LIGHT,
        (snow_x - int(6 * math.cos(rad)), snow_y - int(6 * math.sin(rad))),
        (snow_x + int(6 * math.cos(rad)), snow_y + int(6 * math.sin(rad))), 1)
surf.blit(F6.render("ICG/SN", True, INK_LIGHT), (136, snow_y - 8))

# ── Compass rose / NDB symbol at bottom of plan route ─────────────────────────
pygame.draw.circle(surf, FAA_BLUE, (180, 390), 10, 1)
pygame.draw.line(surf, FAA_BLUE, (180, 380), (180, 370), 1)
pygame.draw.line(surf, FAA_BLUE, (170, 390), (160, 390), 1)
pygame.draw.line(surf, FAA_BLUE, (190, 390), (200, 390), 1)

# Airport symbol at bottom of plan view
pygame.draw.circle(surf, INK, (180, 402), 5)
pygame.draw.circle(surf, PAPER, (180, 402), 3)
pygame.draw.line(surf, INK, (175, 402), (185, 402), 1)
pygame.draw.line(surf, INK, (180, 397), (180, 407), 1)

# ── Dividing line ─────────────────────────────────────────────────────────────
pygame.draw.line(surf, INK, (6, 420), (354, 420), 2)

# ══════════════════════════════════════════════════════════════════════════════
# PROFILE SECTION (y=420 to y=628)
# ══════════════════════════════════════════════════════════════════════════════

# Section header strip
pygame.draw.rect(surf, (220, 225, 235), (6, 420, 348, 16))
ma_txt = F7.render("MISSED APPROACH: CLIMB TO 3000'  THEN DIRECT SKBT NDB", True, INK_LIGHT)
surf.blit(ma_txt, (10, 424))

# Profile background
pygame.draw.rect(surf, PAPER, (6, 436, 348, 174))

# ── Terrain silhouette ────────────────────────────────────────────────────────
terrain_pts = [
    (6, 610), (6, 590), (30, 585), (60, 592), (90, 578), (120, 588),
    (150, 572), (180, 580), (210, 568), (240, 576), (270, 562),
    (300, 572), (330, 580), (354, 575), (354, 610)
]
pygame.draw.polygon(surf, TERRAIN_SHADE, terrain_pts)
pygame.draw.lines(surf, INK_LIGHT, False, terrain_pts[1:-1], 1)

# ── Altitude grid lines ───────────────────────────────────────────────────────
alt_lines = [(436, "5000'"), (516, "3000'"), (596, "1000'")]
for ay, alabel in alt_lines:
    pygame.draw.line(surf, INK_LIGHT, (30, ay), (354, ay), 1)
    surf.blit(F7.render(alabel, True, INK_LIGHT), (7, ay - 8))

# ── Descent glidepath ─────────────────────────────────────────────────────────
pygame.draw.line(surf, FAA_MAGENTA, (340, 440), (30, 590), 2)

# Fix ticks on glidepath
profile_fixes = [
    (0.231, "GOLDH"),
    (0.363, "SUNST"),
    (0.513, "DUSKK"),
    (0.644, "NYTIM"),
    (0.794, "PREDN"),
    (0.906, "SUNRS"),
]
for f, fname in profile_fixes:
    px = int(340 - f * 310)
    py = int(440 + f * 150)
    pygame.draw.line(surf, INK, (px, py - 5), (px, py + 5), 1)
    lbl = F6.render(fname, True, INK_LIGHT)
    surf.blit(lbl, (px - lbl.get_width() // 2, py + 6))

# ── Death fix in profile ──────────────────────────────────────────────────────
df = 0.184
dpx = int(340 - df * 310)   # ≈ 283
dpy = int(440 + df * 150)   # ≈ 468

# Red X
pygame.draw.line(surf, GREASE_RED, (dpx - 5, dpy - 5), (dpx + 5, dpy + 5), 2)
pygame.draw.line(surf, GREASE_RED, (dpx + 5, dpy - 5), (dpx - 5, dpy + 5), 2)
# Circle
pygame.draw.circle(surf, GREASE_RED, (dpx, dpy), 8, 2)
# Labels
surf.blit(F7.render("TERRAIN", True, GREASE_RED), (dpx + 10, dpy - 8))
surf.blit(F7.render("CONTACT", True, GREASE_RED), (dpx + 10, dpy + 2))
# Dotted trail down to terrain
dash_line(surf, GREASE_RED, dpx, dpy + 8, dpx - 3, 578, dash=3, gap=3, width=1)

# ── Decision height box ───────────────────────────────────────────────────────
pygame.draw.rect(surf, (240, 243, 248), (6, 600, 348, 20))
pygame.draw.rect(surf, INK, (6, 600, 348, 20), 1)
dh_txt = F7.render("MDA: 800'  ·  DECISION ALT: 600'  ·  VISIBILITY: 1/4SM", True, INK)
surf.blit(dh_txt, ((360 - dh_txt.get_width()) // 2, 607))

# ══════════════════════════════════════════════════════════════════════════════
# STATS & BACK BUTTON (y=619 to y=636)
# ══════════════════════════════════════════════════════════════════════════════
stats_txt = F8.render("PILLAR 25  ·  DAY 1  ·  0:47  ·  18% FLOWN", True, INK_LIGHT)
surf.blit(stats_txt, ((360 - stats_txt.get_width()) // 2, 619))

# BACK button (fits in lower border strip)
pygame.draw.rect(surf, INK, (148, 626, 64, 10), border_radius=3)
back_txt = F7.render("BACK", True, PAPER)
surf.blit(back_txt, (148 + (64 - back_txt.get_width()) // 2,
                     626 + (10 - back_txt.get_height()) // 2))

# ══════════════════════════════════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════════════════════════════════
out = os.path.join(OUT_DIR, "round_1.png")
pygame.image.save(surf, out)
print(f"saved {out}")
