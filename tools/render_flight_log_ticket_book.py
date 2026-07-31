"""Render: ticket_book Flight Log — Round 5

A vintage multi-coupon airline ticket booklet. 7 coupons (one per biome phase)
stacked vertically. Flown coupons get a torn stub + USED die-stamp. The death
coupon gets a VOID — IRREGULAR OPERATION overprint. Unflown coupons are pristine.

Mock run: death at phase 0.184 (within the DAY phase, row 0).
  Row 0 (DAY):          DEATH coupon (voided mid-use)
  Row 1 (GOLDEN HOUR):  CHAIN CANCEL (downstream cancellation)
  Rows 2-6:             UNFLOWN / pristine
"""
import os
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

pygame.display.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
OUT_DIR = os.path.join(ROOT, "docs", "flight_log_screen", "ticket_book")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Colour palette ────────────────────────────────────────────────────────────
BG             = (8,   8,   20)
KRAFT_BROWN    = (148, 108,  58)
KRAFT_DARK     = (110,  78,  36)
KRAFT_LIGHT    = (180, 140,  80)
COUPON_PAPER   = (252, 248, 238)
COUPON_USED    = (232, 224, 208)
COUPON_DEATH   = (248, 235, 220)
TICKET_NAVY    = (20,   36,  80)
TICKET_RED     = (140,  30,  20)
TICKET_GOLD    = (200, 162,  48)
USED_STAMP     = (80,   80,  90)
VOID_CRIMSON   = (172,  20,  20)
GOLD           = (240, 192,  64)
PERF_HOLE      = (8,    8,  20)
TORN_KRAFT     = (130,  92,  44)
BLUE_STRIPE    = (30,   50, 130)
WHITE_TEXT     = (250, 250, 248)
DARK_TEXT      = (20,   28,  60)
GREY_TEXT      = (120, 118, 130)

# ── Phase data ────────────────────────────────────────────────────────────────
PHASES = [
    (0.000, "DAY",         "ROOST VALLEY",    "MORNING LAUNCH",  "SKBT01"),
    (0.231, "GOLDEN HOUR", "GOLDEN COAST",    "AMBER TERRACES",  "SKBT23"),
    (0.363, "SUNSET",      "SUNSET RIDGE",    "CRIMSON HEIGHTS", "SKBT36"),
    (0.513, "DUSK",        "DUSK RANGE",      "PURPLE PASS",     "SKBT51"),
    (0.644, "NIGHT",       "NIGHTFALL VALE",  "STAR FLATS",      "SKBT64"),
    (0.794, "PREDAWN",     "PREDAWN ISLE",    "FROST PEAK",      "SKBT79"),
    (0.906, "SUNRISE",     "SUNRISE PEAK",    "DESTINATION",     "SKBT91"),
]
DEATH_PHASE = 0.184  # bird died within DAY (row 0)

# Row 0 = DEATH, row 1 = CHAIN_CANCEL (downstream cancellation), rows 2-6 = UNFLOWN
def row_state(i):
    if i == 0:
        return "death"
    if i == 1:
        return "chain_cancel"
    return "unflown"

# ── Fonts ─────────────────────────────────────────────────────────────────────
font_xs  = pygame.font.Font(FONT_PATH,  6)
font_sm  = pygame.font.Font(FONT_PATH,  7)
font_med = pygame.font.Font(FONT_PATH,  9)
font_lrg = pygame.font.Font(FONT_PATH, 14)
font_xl  = pygame.font.Font(FONT_PATH, 22)
font_10  = pygame.font.Font(FONT_PATH, 10)
font_8   = pygame.font.Font(FONT_PATH,  8)

# ── Canvas ────────────────────────────────────────────────────────────────────
surf = pygame.Surface((360, 640))
surf.fill(BG)

# ── Helper: blit centred text ─────────────────────────────────────────────────
def blit_centered(surface, text_surf, cx, cy):
    r = text_surf.get_rect(center=(cx, cy))
    surface.blit(text_surf, r)

def blit_at(surface, text_surf, x, y):
    surface.blit(text_surf, (x, y))

# ─────────────────────────────────────────────────────────────────────────────
# COVER / TITLE BLOCK  (y = 0 → 62)
# ─────────────────────────────────────────────────────────────────────────────
# Kraft cardboard fill
pygame.draw.rect(surf, KRAFT_BROWN, (10, 4, 340, 58))
# Edge/stitching lines
pygame.draw.line(surf, KRAFT_DARK, (10, 6),  (350, 6),  2)
pygame.draw.line(surf, KRAFT_DARK, (10, 60), (350, 60), 2)

# Small airline logo on the left
pygame.draw.circle(surf, (180, 140, 70), (30, 32), 14)
pygame.draw.circle(surf, KRAFT_BROWN,   (30, 32), 10)
sa_surf = font_10.render("SA", True, (255, 240, 180))
blit_centered(surf, sa_surf, 30, 32)

# Cover text
skybit_surf = font_lrg.render("SKYBIT AIRWAYS", True, (255, 240, 180))
blit_centered(surf, skybit_surf, 180, 22)

baggage_surf = font_xs.render("PASSENGER TICKET AND BAGGAGE CHECK", True, (240, 215, 150))
blit_centered(surf, baggage_surf, 180, 40)

# Decorative horizontal rule inside cover
pygame.draw.line(surf, (170, 130, 70), (55, 50), (340, 50), 1)

# ─────────────────────────────────────────────────────────────────────────────
# BOOKLET SPINE LINE
# ─────────────────────────────────────────────────────────────────────────────
pygame.draw.line(surf, (40, 30, 20), (66, 62), (66, 628), 2)

# ─────────────────────────────────────────────────────────────────────────────
# PERFORATION DASHED LINE (subtle, behind holes)
# ─────────────────────────────────────────────────────────────────────────────
for yp in range(65, 625, 4):
    pygame.draw.line(surf, (30, 22, 12), (66, yp), (66, yp + 2), 1)

# ─────────────────────────────────────────────────────────────────────────────
# COUPON LETTERS  A-G
# ─────────────────────────────────────────────────────────────────────────────
COUPON_LETTERS = list("ABCDEFG")

# ─────────────────────────────────────────────────────────────────────────────
# DRAW EACH COUPON
# ─────────────────────────────────────────────────────────────────────────────
for i, (phase_start, phase_name, origin, dest, flight_no) in enumerate(PHASES):
    y = 65 + i * 80
    state = row_state(i)

    # Pick paper colour
    if state == "death":
        coupon_color = COUPON_DEATH
    elif state == "used":
        coupon_color = COUPON_USED
    elif state == "chain_cancel":
        coupon_color = COUPON_PAPER
    else:
        coupon_color = COUPON_PAPER

    # ── Outer border & paper fill ─────────────────────────────────────────────
    pygame.draw.rect(surf, TICKET_NAVY, (10, y, 340, 76), border_radius=2)
    pygame.draw.rect(surf, coupon_color, (11, y + 1, 338, 74))

    # ── Stub (x=10→66) ───────────────────────────────────────────────────────
    pygame.draw.rect(surf, KRAFT_DARK, (10, y + 1, 56, 74))

    # "CPNT" tiny label at top of stub
    cpnt_surf = font_xs.render("CPNT", True, KRAFT_LIGHT)
    blit_at(surf, cpnt_surf, 13, y + 4)

    # Large letter centred in stub
    letter_surf = font_xl.render(COUPON_LETTERS[i], True, TICKET_GOLD)
    blit_centered(surf, letter_surf, 38, y + 38)

    # Stub bottom: flight number micro-text
    fn_micro = font_xs.render(flight_no, True, KRAFT_LIGHT)
    blit_centered(surf, fn_micro, 38, y + 68)

    # ── Decorative header stripe (body top 18px) ──────────────────────────────
    pygame.draw.rect(surf, BLUE_STRIPE, (67, y + 1, 282, 18))

    # "SKYBIT AIRWAYS" left of stripe
    sa_hdr = font_sm.render("SKYBIT AIRWAYS", True, WHITE_TEXT)
    blit_at(surf, sa_hdr, 72, y + 6)

    # Flight number right of stripe
    fl_surf = font_sm.render("FL " + flight_no, True, WHITE_TEXT)
    fl_rect = fl_surf.get_rect()
    blit_at(surf, fl_surf, 349 - fl_rect.width - 2, y + 6)

    # ── Coupon body content (below stripe) ───────────────────────────────────
    # Left side — FROM / TO
    from_lbl = font_sm.render("FROM:", True, GREY_TEXT)
    blit_at(surf, from_lbl, 70, y + 22)

    # Truncate long city names to fit
    origin_disp = origin if len(origin) <= 13 else origin[:13]
    origin_surf = font_med.render(origin_disp, True, DARK_TEXT)
    blit_at(surf, origin_surf, 70, y + 32)

    to_lbl = font_sm.render("TO:", True, GREY_TEXT)
    blit_at(surf, to_lbl, 70, y + 46)

    dest_disp = dest if len(dest) <= 13 else dest[:13]
    dest_surf = font_med.render(dest_disp, True, DARK_TEXT)
    blit_at(surf, dest_surf, 70, y + 56)

    # Right side — CLASS / PHASE
    class_lbl = font_xs.render("CLASS:", True, GREY_TEXT)
    blit_at(surf, class_lbl, 225, y + 22)

    class_val = font_8.render("FIRST", True, DARK_TEXT)
    blit_at(surf, class_val, 225, y + 32)

    phase_lbl = font_xs.render("PHASE:", True, GREY_TEXT)
    blit_at(surf, phase_lbl, 225, y + 46)

    # Phase range string
    if i + 1 < len(PHASES):
        phase_end = PHASES[i + 1][0]
        range_str = f"{phase_start:.3f}–{phase_end:.3f}"
    else:
        range_str = f"{phase_start:.3f}–1.000"
    phase_val = font_xs.render(range_str, True, DARK_TEXT)
    blit_at(surf, phase_val, 225, y + 56)

    # ── Edge vignette — subtle dark gradient top & bottom of each coupon ──────
    vig_top = pygame.Surface((339, 3), pygame.SRCALPHA)
    for dy in range(3):
        alpha_v = 40 - dy * 13  # 40, 27, 14
        pygame.draw.line(vig_top, (*TICKET_NAVY, alpha_v), (0, dy), (338, dy), 1)
    surf.blit(vig_top, (11, y))

    vig_bot = pygame.Surface((339, 2), pygame.SRCALPHA)
    for dy in range(2):
        alpha_v = 30 - dy * 15  # 30, 15
        pygame.draw.line(vig_bot, (*TICKET_NAVY, alpha_v), (0, dy), (338, dy), 1)
    surf.blit(vig_bot, (11, y + 73))

    # ── Death coupon overlays ─────────────────────────────────────────────────
    if state == "death":
        # Bold X pattern across full coupon — 3px lines, alpha=160
        x_surf = pygame.Surface((340, 78), pygame.SRCALPHA)
        pygame.draw.line(x_surf, (172, 20, 20, 160), (0, 0), (340, 78), 3)
        pygame.draw.line(x_surf, (172, 20, 20, 160), (340, 0), (0, 78), 3)
        surf.blit(x_surf, (10, y))

        # "VOID — IRREGULAR OPERATION" at font size 18, ~70% opacity rubber-stamp look
        void_font = pygame.font.Font(FONT_PATH, 18)
        void_surf_base = void_font.render("VOID — IRREGULAR OPERATION", True, VOID_CRIMSON)
        # Use colorkey + set_alpha for reliable semi-transparent blit
        void_surf_base.set_colorkey(void_surf_base.get_at((0, 0)))
        void_rot = pygame.transform.rotate(void_surf_base, -12)
        void_rot.set_alpha(180)  # 70% opacity — authentic rubber-stamp look
        vx = 10 + (340 - void_rot.get_width()) // 2
        vy = y + (78 - void_rot.get_height()) // 2
        surf.blit(void_rot, (vx, vy))

        # Red border on the death coupon
        pygame.draw.rect(surf, VOID_CRIMSON, (10, y, 340, 76), width=2, border_radius=2)

    # ── Chain-cancel overlay (row 1 — downstream cancellation) ───────────────
    elif state == "chain_cancel":
        # Light pink wash on right half of coupon body
        cancel_wash = pygame.Surface((170, 74), pygame.SRCALPHA)
        cancel_wash.fill((172, 40, 32, 20))
        surf.blit(cancel_wash, (180, y + 1))
        # Small "CHAIN CANCEL" label at far right of coupon body
        cc_surf = font_xs.render("CHAIN CANCEL", True, GREY_TEXT)
        blit_at(surf, cc_surf, 285, y + 67)

    # ── Perforation holes along x=66 ─────────────────────────────────────────
    for yp in range(y + 4, y + 74, 8):
        pygame.draw.circle(surf, PERF_HOLE, (66, yp), 3)

# ─────────────────────────────────────────────────────────────────────────────
# PAPER GRAIN TEXTURE (sparse noise — fast approach)
# ─────────────────────────────────────────────────────────────────────────────
noise_surf = pygame.Surface((360, 640), pygame.SRCALPHA)
rng = random.Random(42)
for _ in range(8000):
    nx, ny = rng.randint(10, 349), rng.randint(65, 620)
    alpha = rng.randint(0, 12)
    light = rng.choice([True, False])
    col = (255, 255, 255, alpha) if light else (0, 0, 0, alpha)
    noise_surf.set_at((nx, ny), col)
surf.blit(noise_surf, (0, 0))

# ─────────────────────────────────────────────────────────────────────────────
# BOTTOM STATUS BAR  (moved above BACK pill to fix overlap)
# ─────────────────────────────────────────────────────────────────────────────
status_txt = "PILLAR 25  ·  DAY 1  ·  0:47  ·  FLIGHT VOIDED"
status_surf = font_med.render(status_txt, True, GOLD)
blit_centered(surf, status_surf, 180, 617)

# ─────────────────────────────────────────────────────────────────────────────
# BACK BUTTON
# ─────────────────────────────────────────────────────────────────────────────
pygame.draw.rect(surf, TICKET_NAVY, (135, 627, 90, 12), border_radius=4)
back_surf = font_8.render("BACK", True, GOLD)
blit_centered(surf, back_surf, 180, 633)

# ─────────────────────────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────────────────────────
out = os.path.join(OUT_DIR, "round_2.png")
pygame.image.save(surf, out)
print(f"saved {out}")
