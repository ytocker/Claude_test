"""
V15 smooth-taper-weave — 6 size variants (original + 5 scaled).
Each scale multiplies all geometry offsets from CX by factor s.
"""
import os, sys, math
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
import game.parrot as parrot_mod
import game.hud as hud_module
from game.scenes import App

ROOT    = "/home/user/skybit"
OUT_DIR = f"{ROOT}/docs/lives-display-v15/size-variants"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Palette (unchanged at all scales) ────────────────────────────────────────
PANEL_DARK   = (12, 8, 38)
GOLD_BRIGHT  = (240, 192, 64)
OUTER_SHADOW = (4, 4, 12)
TWIG_BRIGHT  = (160, 110, 55)
TWIG_MID     = (110, 75, 35)
TWIG_DARK    = (70, 45, 18)
STICK_COL    = (130, 90, 42)
STICK_HI     = (170, 120, 60)
STICK_SH     = (80,  55, 22)
COURSE_TOP   = (180, 130, 65)
COURSE_BOT   = (80,  55, 22)
HOLLOW_COL   = (50,  35, 14)

CX      = 31
CY_LIST = [73, 113]
_STICK_X_OFFSET = (-1, 0, 1, 2)

# ── Low-level helpers (scale-agnostic) ───────────────────────────────────────
def _cy_sag(x, x1, x2, base_y, sag):
    half_w = (x2 - x1) / 2.0
    if half_w <= 0:
        return base_y
    t = ((x - x1) / half_w) - 1.0
    return base_y + int(round(sag * (1.0 - t * t)))

def _draw_stick_row(surf, vx, y):
    surf.set_at((vx - 1, y), STICK_HI)
    surf.set_at((vx,     y), STICK_COL)
    surf.set_at((vx + 1, y), STICK_COL)
    surf.set_at((vx + 2, y), STICK_SH)

def _draw_stick_span(surf, vx, y1, y2):
    for y in range(y1, y2 + 1):
        _draw_stick_row(surf, vx, y)

def _draw_course_col(surf, x, x1, x2, base_y, sag, mid_col):
    y = _cy_sag(x, x1, x2, base_y, sag)
    surf.set_at((x, y),     COURSE_TOP)
    surf.set_at((x, y + 1), mid_col)
    surf.set_at((x, y + 2), mid_col)
    surf.set_at((x, y + 3), COURSE_BOT)

def _draw_course_full(surf, x1, x2, base_y, sag, mid_col, skip_xs):
    skip_set = set()
    for sx in skip_xs:
        for dx in _STICK_X_OFFSET:
            skip_set.add(sx + dx)
    for x in range(x1, x2 + 1):
        if x not in skip_set:
            _draw_course_col(surf, x, x1, x2, base_y, sag, mid_col)

def _draw_course_at_vx(surf, vx, x1, x2, base_y, sag, mid_col):
    for dx in _STICK_X_OFFSET:
        x = vx + dx
        if x1 <= x <= x2:
            _draw_course_col(surf, x, x1, x2, base_y, sag, mid_col)

def _draw_stick_at_course(surf, vx, x1, x2, base_y, sag):
    y_top = _cy_sag(vx, x1, x2, base_y, sag)
    for y in range(y_top, y_top + 4):
        _draw_stick_row(surf, vx, y)

def _draw_notches(surf, cy, courses, stick_wins):
    for ci, (offset, col, x1, x2, sag) in enumerate(courses):
        base_y = cy + offset
        for vx in (courses[ci][2] - 1,):   # not needed — loop via stick_wins keys
            pass
        for (cii, vx), wins in stick_wins.items():
            if cii != ci:
                continue
            y_cross = _cy_sag(vx, x1, x2, base_y, sag)
            if wins:   # course under stick
                for x in [vx - 2, vx + 3]:
                    if x1 <= x <= x2:
                        surf.set_at((x, y_cross + 1), TWIG_DARK)
                        surf.set_at((x, y_cross + 2), TWIG_DARK)
            else:      # stick under course
                for dy in (-1, 4):
                    surf.set_at((vx,     y_cross + dy), TWIG_DARK)
                    surf.set_at((vx + 1, y_cross + dy), TWIG_DARK)

def _weave_courses(surf, cy, ci_range, courses, stick_wins):
    for ci in ci_range:
        offset, col, x1, x2, sag = courses[ci]
        base_y = cy + offset
        skip = [vx for (cii, vx), wins in stick_wins.items()
                if cii == ci and wins]
        _draw_course_full(surf, x1, x2, base_y, sag, col, skip_xs=skip)
        for (cii, vx), wins in stick_wins.items():
            if cii == ci and not wins:
                _draw_course_at_vx(surf, vx, x1, x2, base_y, sag, col)


# ── Scaled geometry factory ───────────────────────────────────────────────────
def make_params(s, cx):
    r = lambda v: round(v * s)
    verts = [cx - r(9), cx + r(9)]
    courses = [
        (r(2),  TWIG_BRIGHT, cx - r(21), cx + r(21), max(1, r(2))),
        (r(6),  TWIG_MID,    cx - r(20), cx + r(20), max(1, r(2))),
        (r(10), TWIG_BRIGHT, cx - r(18), cx + r(18), max(1, r(2))),
        (r(14), TWIG_MID,    cx - r(16), cx + r(16), max(1, r(2))),
        (r(18), TWIG_BRIGHT, cx - r(14), cx + r(14), max(1, r(3))),
    ]
    vxL, vxR = verts
    stick_wins = {
        (ci, vxL): (ci % 2 == 0) for ci in range(5)
    }
    stick_wins.update({
        (ci, vxR): (ci % 2 == 1) for ci in range(5)
    })
    rim_rect      = (cx - r(21), -r(5), r(42), max(4, r(12)))
    stick_bottom  = r(18)
    hollow        = (cx - r(11), r(16), r(22), max(2, r(3)))
    bird_h        = 34   # parrot always full size; only nest scales
    return verts, courses, stick_wins, rim_rect, stick_bottom, hollow, bird_h


# ── Per-scale draw function factory ─────────────────────────────────────────
def make_draw_fn(s):
    cx = CX
    verts, courses, stick_wins, rim_rect, stick_bottom, hollow, bird_h = make_params(s, cx)

    src  = parrot_mod._get_frames()[1]
    bird_w = max(1, int(src.get_width() * bird_h / src.get_height()))
    bird = pygame.transform.smoothscale(src, (bird_w, bird_h))

    def draw_slot(surf, cy, alive):
        # back rim arc
        rx, ry_off, rw, rh = rim_rect
        pygame.draw.arc(surf, TWIG_BRIGHT, (rx, cy + ry_off, rw, rh), 0, math.pi, 2)

        # sticks
        for vx in verts:
            _draw_stick_span(surf, vx, cy, cy + stick_bottom)

        # courses 0,1 behind bird
        _weave_courses(surf, cy, (0, 1), courses, stick_wins)

        # bird or hollow
        if alive:
            surf.blit(bird, (cx - bird_w // 2, cy - bird_h // 2 + 5))
        else:
            hx, hy_off, hw, hh = hollow
            pygame.draw.rect(surf, HOLLOW_COL, (hx, cy + hy_off, hw, hh))

        # courses 2,3,4 in front
        _weave_courses(surf, cy, (2, 3, 4), courses, stick_wins)
        for ci in (2, 3, 4):
            offset, col, x1, x2, sag = courses[ci]
            base_y = cy + offset
            for (cii, vx), wins in stick_wins.items():
                if cii == ci and wins:
                    _draw_stick_at_course(surf, vx, x1, x2, base_y, sag)

        _draw_notches(surf, cy, courses, stick_wins)

    def _draw(surf, lives_remaining, lives_total, cy=106):
        pygame.draw.rect(surf, OUTER_SHADOW, (1, 56, 60, 82), 1, border_radius=6)
        pygame.draw.rect(surf, PANEL_DARK,   (2, 57, 58, 80),    border_radius=5)
        pygame.draw.rect(surf, GOLD_BRIGHT,  (2, 57, 58, 80), 1, border_radius=5)
        for i, cy_s in enumerate(CY_LIST[:max(lives_total, 2)]):
            draw_slot(surf, cy_s, i < lives_remaining)

    return _draw


# ── Render all 6 variants ────────────────────────────────────────────────────
VARIANTS = [
    (1.00, "original",  "100%  ORIGINAL"),
    (0.85, "large",     "85%"),
    (0.70, "medium",    "70%"),
    (0.55, "small",     "55%"),
    (0.42, "compact",   "42%"),
    (0.32, "tiny",      "32%"),
]

renders = []
for s, slug, label in VARIANTS:
    out = f"{OUT_DIR}/{slug}.png"
    fn  = make_draw_fn(s)
    hud_module._draw_pip_lives_row = fn
    hud_module._PIP_ICON_ALIVE = None
    hud_module._PIP_ICON_SPENT = None

    app = App()
    app._start_play()
    app.world.lives_remaining = 1
    app._render()
    pygame.image.save(app.screen, out)

    from PIL import Image as PILImage
    img   = PILImage.open(out)
    pix   = img.load()
    count = sum(1 for y in range(58, 92) for x in range(0, 63)
                if pix[x, y][0] > 150 and pix[x, y][1] < 110)
    print(f"{label:20s}  bird-red={count:3d}  {'PASS' if count > 20 else 'FAIL'}")
    renders.append((label, out))

print("\nAll renders done. Stitching showcase...")

# ── Stitch showcase ───────────────────────────────────────────────────────────
from PIL import Image, ImageDraw, ImageFont

CROP   = (0, 53, 64, 143)
SCALE  = 4
PW     = (CROP[2] - CROP[0]) * SCALE   # 256
PH     = (CROP[3] - CROP[1]) * SCALE   # 360
GAP    = 12
MARGIN = 24
HDR_H  = 52
FTR_H  = 32
BG     = (8, 8, 20)
GOLD   = (240, 192, 64)
DIM    = (100, 90, 60)

N  = len(renders)
CW = MARGIN + N * PW + (N-1) * GAP + MARGIN
CH = MARGIN + HDR_H + PH + FTR_H + MARGIN

canvas = Image.new("RGB", (CW, CH), BG)
draw   = ImageDraw.Draw(canvas)

font_path = f"{ROOT}/game/assets/PressStart2P-Regular.ttf"
try:
    fhdr = ImageFont.truetype(font_path, 9)
    flbl = ImageFont.truetype(font_path, 7)
except Exception:
    fhdr = flbl = ImageFont.load_default()

hdr = "SMOOTH-TAPER WEAVE  \xb7  V15  \xb7  SIZE VARIANTS"
try:
    bx = draw.textbbox((0, 0), hdr, font=fhdr)
    tw = bx[2] - bx[0]
except Exception:
    tw = len(hdr) * 7
draw.text(((CW - tw) // 2, MARGIN + (HDR_H - 12) // 2), hdr, font=fhdr, fill=GOLD)

py0 = MARGIN + HDR_H

for idx, (label, path) in enumerate(renders):
    px  = MARGIN + idx * (PW + GAP)
    img = Image.open(path)
    chip   = img.crop(CROP)
    scaled = chip.resize((PW, PH), Image.NEAREST)
    canvas.paste(scaled, (px, py0))

    is_orig = idx == 0
    draw.rectangle([px, py0, px+PW-1, py0+PH-1],
                   outline=(80,70,30) if is_orig else (50,44,80), width=1)

    fy = py0 + PH
    draw.rectangle([px, fy, px+PW-1, fy+FTR_H-1], fill=(14, 10, 38))
    lbl_col = DIM if is_orig else GOLD
    try:
        b2 = draw.textbbox((0, 0), label, font=flbl)
        fw, fh = b2[2]-b2[0], b2[3]-b2[1]
    except Exception:
        fw, fh = len(label)*5, 8
    draw.text((px + (PW-fw)//2, fy + (FTR_H-fh)//2), label, font=flbl, fill=lbl_col)

SHOWCASE = f"{OUT_DIR}/size_compare.png"
canvas.save(SHOWCASE)
print(f"Saved showcase: {SHOWCASE}  ({CW}x{CH})")
