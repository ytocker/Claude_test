"""V4 showcase — bandaged-crisis at 8×, side by side with the original."""
import os
import sys
import importlib
import numpy as np

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"

sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()

from PIL import Image, ImageDraw, ImageFont

BASE = "/home/user/skybit/docs/hurt-parrot-v4"
OUT  = f"{BASE}/showcase_v4.png"

BG       = (8, 8, 20)
PANEL_W  = 544   # 68 × 8
PANEL_H  = 512   # 64 × 8
MARGIN   = 24
GAP      = 20
HEADER_H = 60
FOOTER_H = 48

CANVAS_W = MARGIN + 2 * PANEL_W + GAP + MARGIN
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
    oa = pygame.surfarray.pixels_alpha(outline_surf)
    oa[:] = shadow
    del oa
    outline_surf.fill((15, 8, 8), special_flags=pygame.BLEND_RGBA_MIN)
    out.blit(outline_surf, (0, 0))
    out.blit(src, (pad, pad))
    return out


def make_panel(frame_surf):
    outlined = _add_outline_fast(frame_surf)
    scaled   = pygame.transform.scale(outlined, (PANEL_W, PANEL_H))
    raw      = pygame.image.tostring(scaled, "RGBA")
    return Image.frombytes("RGBA", (PANEL_W, PANEL_H), raw).convert("RGB")


# Original healthy parrot
import game.parrot as parrot_mod
orig_panel = make_panel(parrot_mod._build_frame(10))

# V4 bandaged-crisis
mod_dir = f"{BASE}/bandaged-crisis"
sys.path.insert(0, mod_dir)
if "design" in sys.modules:
    del sys.modules["design"]
design = importlib.import_module("design")
hurt_panel = make_panel(design._build_hurt_frame(10))
sys.path.remove(mod_dir)

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


font_hdr   = _font(26, bold=True)
font_label = _font(15, bold=True)
font_sub   = _font(12)

# Header
TITLE = "HURT PARROT · LAST LIFE · V4"
bbox  = draw.textbbox((0, 0), TITLE, font=font_hdr)
tx    = (CANVAS_W - (bbox[2] - bbox[0])) // 2
ty    = MARGIN + (HEADER_H - (bbox[3] - bbox[1])) // 2
draw.text((tx, ty), TITLE, font=font_hdr, fill=(255, 235, 200))

py = MARGIN + HEADER_H + 16

panels = [
    (orig_panel,  "original",         (140, 200, 140), "BASELINE"),
    (hurt_panel,  "bandaged-crisis",  (255, 210, 80),  "ROUND 2 · FINAL"),
]

for i, (panel_img, slug, label_color, sub) in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GAP)

    # Separator between panels
    if i == 1:
        sep_x = px - GAP // 2
        draw.line([(sep_x, py - 6), (sep_x, py + PANEL_H + 6)], fill=(50, 35, 70), width=2)

    draw.rectangle([px - 1, py - 1, px + PANEL_W, py + PANEL_H], outline=(30, 20, 40), width=1)
    canvas.paste(panel_img, (px, py))

    slug_bbox = draw.textbbox((0, 0), slug, font=font_label)
    sw = slug_bbox[2] - slug_bbox[0]
    sx = px + (PANEL_W - sw) // 2
    sy = py + PANEL_H + 10
    draw.text((sx, sy), slug, font=font_label, fill=label_color)

    sub_bbox = draw.textbbox((0, 0), sub, font=font_sub)
    svw = sub_bbox[2] - sub_bbox[0]
    svx = px + (PANEL_W - svw) // 2
    svy = sy + (slug_bbox[3] - slug_bbox[1]) + 4
    draw.text((svx, svy), sub, font=font_sub, fill=(120, 120, 150))

canvas.save(OUT)
print(f"Saved: {OUT}  {canvas.size}")

# Sanity
arr = np.array(canvas)
for i, (_, slug, *_rest) in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GAP)
    region = arr[py:py+PANEL_H, px:px+PANEL_W]
    colored = int(((region[:,:,0] > 80) & (region[:,:,1] < 150)).sum())
    print(f"  [{i}] {slug:22s}  colored={colored:6d}  {'PASS' if colored > 200 else 'FAIL'}")
