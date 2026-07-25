"""V3 showcase — battle-bloodshot at 8× NEAREST, isolated panel."""
import os
import sys
import importlib
import numpy as np

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"

import pygame
pygame.init()

from PIL import Image, ImageDraw, ImageFont

BASE = "/home/user/skybit/docs/hurt-parrot-v3"
OUT  = f"{BASE}/showcase_v3.png"

SLUG = "battle-bloodshot"

BG       = (8, 8, 20)
HEADER_H = 60
FOOTER_H = 44
PANEL_W  = 544   # 68 × 8
PANEL_H  = 512   # 64 × 8
MARGIN   = 28

CANVAS_W = MARGIN + PANEL_W + MARGIN
CANVAS_H = MARGIN + HEADER_H + 16 + PANEL_H + FOOTER_H + MARGIN


def _add_outline_fast(src: pygame.Surface) -> pygame.Surface:
    w, h = src.get_size()
    pad = 2
    out_w, out_h = w + pad * 2, h + pad * 2
    out = pygame.Surface((out_w, out_h), pygame.SRCALPHA)

    arr = pygame.surfarray.array_alpha(src)
    big = np.zeros((out_w, out_h), dtype=np.uint8)
    big[pad:pad+w, pad:pad+h] = arr

    shadow = np.zeros_like(big)
    for dx in range(-pad, pad + 1):
        for dy in range(-pad, pad + 1):
            if dx == 0 and dy == 0:
                continue
            shifted = np.roll(np.roll(big, dx, axis=0), dy, axis=1)
            shadow = np.maximum(shadow, (shifted > 8).astype(np.uint8) * 255)

    outline_surf = pygame.Surface((out_w, out_h), pygame.SRCALPHA)
    outline_arr = pygame.surfarray.pixels_alpha(outline_surf)
    outline_arr[:] = shadow
    del outline_arr
    outline_surf.fill((15, 8, 8), special_flags=pygame.BLEND_RGBA_MIN)

    out.blit(outline_surf, (0, 0))
    out.blit(src, (pad, pad))
    return out


# Load design module
mod_dir = f"{BASE}/{SLUG}"
if mod_dir not in sys.path:
    sys.path.insert(0, mod_dir)
if "design" in sys.modules:
    del sys.modules["design"]
design = importlib.import_module("design")

frame    = design._build_hurt_frame(10)   # frame 0, wing slightly raised
outlined = _add_outline_fast(frame)       # 68×64
panel_s  = pygame.transform.scale(outlined, (PANEL_W, PANEL_H))

raw = pygame.image.tostring(panel_s, "RGBA")
panel = Image.frombytes("RGBA", (PANEL_W, PANEL_H), raw).convert("RGB")

# Canvas
canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
draw   = ImageDraw.Draw(canvas)


def _font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans{}.ttf".format("-Bold" if bold else ""),
        "/usr/share/fonts/truetype/liberation/LiberationSans{}-Regular.ttf".format("-Bold" if bold else ""),
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


font_hdr  = _font(26, bold=True)
font_foot = _font(16, bold=True)
font_ver  = _font(13)

# Header
TITLE = "HURT PARROT · LAST LIFE · V3"
bbox  = draw.textbbox((0, 0), TITLE, font=font_hdr)
tx    = (CANVAS_W - (bbox[2] - bbox[0])) // 2
ty    = MARGIN + (HEADER_H - (bbox[3] - bbox[1])) // 2
draw.text((tx, ty), TITLE, font=font_hdr, fill=(255, 235, 200))

# Panel
px = MARGIN
py = MARGIN + HEADER_H + 16
draw.rectangle([px - 2, py - 2, px + PANEL_W + 1, py + PANEL_H + 1],
               outline=(40, 28, 56), width=1)
canvas.paste(panel, (px, py))

# Slug label
slug_bbox = draw.textbbox((0, 0), SLUG, font=font_foot)
sw = slug_bbox[2] - slug_bbox[0]
sx = px + (PANEL_W - sw) // 2
sy = py + PANEL_H + 10
draw.text((sx, sy), SLUG, font=font_foot, fill=(220, 220, 240))

# Version tag
lbl = "ROUND 2 · FINAL"
lbl_bbox = draw.textbbox((0, 0), lbl, font=font_ver)
lw = lbl_bbox[2] - lbl_bbox[0]
lx = px + (PANEL_W - lw) // 2
ly = sy + (slug_bbox[3] - slug_bbox[1]) + 4
draw.text((lx, ly), lbl, font=font_ver, fill=(140, 200, 140))

canvas.save(OUT)
print(f"Saved: {OUT}  {canvas.size}")

# Sanity check
arr = np.array(canvas)
region = arr[py:py+PANEL_H, px:px+PANEL_W]
colored = int(((region[:,:,0] > 100) & (region[:,:,1] < 120)).sum())
status = "PASS" if colored > 500 else "FAIL"
print(f"  {SLUG}: colored={colored}  {status}")
