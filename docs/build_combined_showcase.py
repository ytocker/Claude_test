"""Combined hurt-parrot showcase: original + 5 V2 concepts + V3 battle-bloodshot."""
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

BASE_V2 = "/home/user/skybit/docs/hurt-parrot-v2"
BASE_V3 = "/home/user/skybit/docs/hurt-parrot-v3"
OUT     = "/home/user/skybit/docs/hurt-parrot-showcase.png"

BG       = (8, 8, 20)
PANEL_W  = 544   # 68 × 8
PANEL_H  = 512   # 64 × 8
MARGIN   = 20
GAP      = 12
HEADER_H = 60
FOOTER_H = 44

N_PANELS = 7
CANVAS_W = MARGIN + N_PANELS * PANEL_W + (N_PANELS - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HEADER_H + 12 + PANEL_H + FOOTER_H + MARGIN


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


def load_panel(frame_surf: pygame.Surface) -> Image.Image:
    outlined = _add_outline_fast(frame_surf)
    scaled   = pygame.transform.scale(outlined, (PANEL_W, PANEL_H))
    raw      = pygame.image.tostring(scaled, "RGBA")
    return Image.frombytes("RGBA", (PANEL_W, PANEL_H), raw).convert("RGB")


# ── Panel 0: original healthy parrot ──────────────────────────────────────
import game.parrot as parrot_mod
orig_frame = parrot_mod._build_frame(10)
panels = [("original", "ORIGINAL", (140, 200, 140), None, load_panel(orig_frame))]

# ── Panels 1–5: V2 concepts ───────────────────────────────────────────────
V2_SLUGS = ["hollow", "bloodshot", "fractured", "corrupted", "gaunt"]
for slug in V2_SLUGS:
    mod_dir = f"{BASE_V2}/{slug}"
    for p in list(sys.path):
        if p.startswith("/home/user/skybit/docs/"):
            sys.path.remove(p)
    sys.path.insert(0, mod_dir)
    if "design" in sys.modules:
        del sys.modules["design"]
    design = importlib.import_module("design")
    frame  = design._build_hurt_frame(10)
    panels.append((slug, slug, (220, 220, 240), "V2", load_panel(frame)))
    sys.path.remove(mod_dir)

# ── Panel 6: V3 battle-bloodshot ──────────────────────────────────────────
mod_dir = f"{BASE_V3}/battle-bloodshot"
sys.path.insert(0, mod_dir)
if "design" in sys.modules:
    del sys.modules["design"]
design = importlib.import_module("design")
frame  = design._build_hurt_frame(10)
panels.append(("battle-bloodshot", "battle-bloodshot", (255, 210, 80), "V3", load_panel(frame)))
sys.path.remove(mod_dir)

# ── Build canvas ───────────────────────────────────────────────────────────
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


font_hdr  = _font(24, bold=True)
font_foot = _font(14, bold=True)
font_ver  = _font(11)

# Header
TITLE = "HURT PARROT · LAST LIFE · ALL CONCEPTS"
bbox  = draw.textbbox((0, 0), TITLE, font=font_hdr)
tx    = (CANVAS_W - (bbox[2] - bbox[0])) // 2
ty    = MARGIN + (HEADER_H - (bbox[3] - bbox[1])) // 2
draw.text((tx, ty), TITLE, font=font_hdr, fill=(255, 235, 200))

# Panels
py = MARGIN + HEADER_H + 12
for i, (slug, label, label_color, version_tag, panel_img) in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GAP)

    # Separator lines
    if i == 1:  # between ORIGINAL and V2
        sep_x = px - GAP // 2
        draw.line([(sep_x, py - 8), (sep_x, py + PANEL_H + 8)], fill=(60, 40, 80), width=3)
    if i == 6:  # between V2 and V3
        sep_x = px - GAP // 2
        draw.line([(sep_x, py - 8), (sep_x, py + PANEL_H + 8)], fill=(80, 65, 20), width=2)

    draw.rectangle([px - 1, py - 1, px + PANEL_W, py + PANEL_H], outline=(30, 20, 40), width=1)
    canvas.paste(panel_img, (px, py))

    # Slug label
    slug_bbox = draw.textbbox((0, 0), label, font=font_foot)
    sw = slug_bbox[2] - slug_bbox[0]
    sx = px + (PANEL_W - sw) // 2
    sy = py + PANEL_H + 8
    draw.text((sx, sy), label, font=font_foot, fill=label_color)

    # Version tag
    if version_tag:
        vtag_bbox = draw.textbbox((0, 0), version_tag, font=font_ver)
        vw = vtag_bbox[2] - vtag_bbox[0]
        vx = px + (PANEL_W - vw) // 2
        vy = sy + (slug_bbox[3] - slug_bbox[1]) + 3
        draw.text((vx, vy), version_tag, font=font_ver, fill=(120, 120, 150))

canvas.save(OUT)
print(f"Saved: {OUT}  {canvas.size}")

# Sanity check
arr = np.array(canvas)
print("\nPanel pixel check:")
all_ok = True
for i, (slug, label, *_rest) in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GAP)
    region = arr[py:py+PANEL_H, px:px+PANEL_W]
    colored = int(((region[:,:,0] > 80) & (region[:,:,1] < 150)).sum())
    ok = colored > 200
    all_ok = all_ok and ok
    print(f"  [{i}] {label:22s}  colored={colored:6d}  {'PASS' if ok else 'FAIL'}")

assert all_ok, "One or more panels failed the pixel check"
print("\nAll panels OK.")
