"""V2 showcase — direct sprite import at 8×, isolated panels."""
import os
import sys
import importlib
import numpy as np

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"

import pygame
pygame.init()

from PIL import Image, ImageDraw, ImageFont

BASE = "/home/user/skybit/docs/hurt-parrot-v2"
OUT  = f"{BASE}/showcase_v2.png"

SLUGS = ["hollow", "bloodshot", "fractured", "corrupted", "gaunt"]

BG       = (8, 8, 20)
HEADER_H = 60
FOOTER_H = 40
PANEL_W  = 544   # 68 × 8
PANEL_H  = 512   # 64 × 8
MARGIN   = 20
GAP      = 12

CANVAS_W = MARGIN + len(SLUGS) * PANEL_W + (len(SLUGS) - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HEADER_H + GAP + PANEL_H + FOOTER_H + MARGIN

# ── _add_outline (same as game/parrot.py) ──────────────────────────────────
def _add_outline(src: pygame.Surface) -> pygame.Surface:
    """2px dark silhouette pad around every opaque pixel."""
    w, h = src.get_size()
    pad = 2
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    arr = pygame.surfarray.array_alpha(src)
    outline_color = (15, 8, 8, 255)
    for dx in range(-pad, pad + 1):
        for dy in range(-pad, pad + 1):
            if dx == 0 and dy == 0:
                continue
            xs = max(0, -dx)
            xe = w + min(0, -dx)
            ys = max(0, -dy)
            ye = h + min(0, -dy)
            region = arr[xs:xe, ys:ye]
            mask = region > 8
            ys2 = ys + dy + pad
            xs2 = xs + dx + pad
            for ix in range(region.shape[0]):
                for iy in range(region.shape[1]):
                    if mask[ix, iy]:
                        out.set_at((xs2 + ix, ys2 + iy), outline_color)
    out.blit(src, (pad, pad))
    return out


# Vectorised version (much faster)
def _add_outline_fast(src: pygame.Surface) -> pygame.Surface:
    w, h = src.get_size()
    pad = 2
    out_w, out_h = w + pad * 2, h + pad * 2
    out = pygame.Surface((out_w, out_h), pygame.SRCALPHA)

    arr = pygame.surfarray.array_alpha(src)  # shape (w, h)
    # Expand alpha to padded size
    big = np.zeros((out_w, out_h), dtype=np.uint8)
    big[pad:pad+w, pad:pad+h] = arr

    # Erode: any pixel near an opaque pixel becomes outline
    shadow = np.zeros_like(big)
    for dx in range(-pad, pad + 1):
        for dy in range(-pad, pad + 1):
            if dx == 0 and dy == 0:
                continue
            shifted = np.roll(np.roll(big, dx, axis=0), dy, axis=1)
            shadow = np.maximum(shadow, (shifted > 8).astype(np.uint8) * 255)

    # Draw outline pixels
    outline_surf = pygame.Surface((out_w, out_h), pygame.SRCALPHA)
    outline_arr = pygame.surfarray.pixels_alpha(outline_surf)
    outline_arr[:] = shadow
    del outline_arr
    outline_surf.fill((15, 8, 8), special_flags=pygame.BLEND_RGBA_MIN)

    out.blit(outline_surf, (0, 0))
    out.blit(src, (pad, pad))
    return out


# ── load each design module ────────────────────────────────────────────────
panels = []
for slug in SLUGS:
    mod_dir = f"{BASE}/{slug}"
    if mod_dir not in sys.path:
        sys.path.insert(0, mod_dir)
    # Force re-import in case of name collision
    if "design" in sys.modules:
        del sys.modules["design"]
    design = importlib.import_module("design")

    frame = design._build_hurt_frame(10)   # wing slightly raised, frame 0
    outlined = _add_outline_fast(frame)    # 68×64
    # Scale 8×
    panel_surf = pygame.transform.scale(outlined, (PANEL_W, PANEL_H))

    # Convert to PIL for stitching
    raw = pygame.image.tostring(panel_surf, "RGBA")
    pil = Image.frombytes("RGBA", (PANEL_W, PANEL_H), raw).convert("RGB")
    panels.append(pil)

    sys.path.remove(mod_dir)

# ── build canvas ───────────────────────────────────────────────────────────
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
font_foot = _font(15, bold=True)
font_ver  = _font(12)

# header
TITLE = "HURT PARROT · LAST LIFE · V2"
bbox  = draw.textbbox((0, 0), TITLE, font=font_hdr)
tx    = (CANVAS_W - (bbox[2] - bbox[0])) // 2
ty    = MARGIN + (HEADER_H - (bbox[3] - bbox[1])) // 2
draw.text((tx, ty), TITLE, font=font_hdr, fill=(255, 235, 200))

# panels
for i, (slug, panel) in enumerate(zip(SLUGS, panels)):
    px = MARGIN + i * (PANEL_W + GAP)
    py = MARGIN + HEADER_H + GAP

    # dark panel bg
    draw.rectangle([px - 2, py - 2, px + PANEL_W + 1, py + PANEL_H + 1],
                   outline=(30, 20, 40), width=1)
    canvas.paste(panel, (px, py))

    # slug label
    slug_bbox = draw.textbbox((0, 0), slug, font=font_foot)
    sw = slug_bbox[2] - slug_bbox[0]
    sx = px + (PANEL_W - sw) // 2
    sy = py + PANEL_H + 8
    draw.text((sx, sy), slug, font=font_foot, fill=(220, 220, 240))

    # version tag
    lbl = "ROUND 2"
    lbl_bbox = draw.textbbox((0, 0), lbl, font=font_ver)
    lw = lbl_bbox[2] - lbl_bbox[0]
    lx = px + (PANEL_W - lw) // 2
    ly = sy + (slug_bbox[3] - slug_bbox[1]) + 3
    draw.text((lx, ly), lbl, font=font_ver, fill=(140, 200, 140))

canvas.save(OUT)
print(f"Saved: {OUT}  {canvas.size}")

# sanity: check bird-red pixels per panel
print("\nBird-red pixel check per panel:")
arr = np.array(canvas)
for i, slug in enumerate(SLUGS):
    px = MARGIN + i * (PANEL_W + GAP)
    py = MARGIN + HEADER_H + GAP
    region = arr[py:py+PANEL_H, px:px+PANEL_W]
    # broad red check (R>100, G<120) to catch all concepts
    cnt = int(((region[:,:,0] > 100) & (region[:,:,1] < 120)).sum())
    status = "PASS" if cnt > 200 else "FAIL"
    print(f"  {slug:20s}  colored={cnt:6d}  {status}")
