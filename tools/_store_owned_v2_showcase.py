#!/usr/bin/env python3
"""store_owned_v2 showcase — 6 R2 concept panels + zoom strips"""
from PIL import Image, ImageDraw, ImageFont
import os

CONCEPTS = [
    ("cord_stub_only",      "CORD-STUB",     314),
    ("top_strip_retained",  "TOP-STRIP",     315),
    ("diagonal_yank",       "DIAGONAL-YANK", 315),
    ("barely_attached_rip", "BARELY-RIP",    309),
    ("grommet_rip_down",    "GROMMET-RIP",   309),
    ("top_left_gem",        "GEM-BADGE",     316),
]

BASE = "docs/store_owned_v2"
BG = (8, 8, 20)
PANEL_W, PANEL_H = 324, 200
GAP = 8
MARGIN = 20
HEADER_H = 44
FOOTER_H = 36

N = len(CONCEPTS)
canvas_w = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
canvas_h = MARGIN + HEADER_H + GAP + PANEL_H + GAP + PANEL_H + FOOTER_H + MARGIN

canvas = Image.new("RGB", (canvas_w, canvas_h), BG)
draw = ImageDraw.Draw(canvas)

try:
    font_hdr = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    font_lbl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
except Exception:
    font_hdr = ImageFont.load_default()
    font_lbl = font_hdr
    font_sub = font_hdr

GOLD   = (220, 190, 100)
CREAM  = (200, 185, 140)
DIM    = (90, 85, 70)

draw.text(
    (canvas_w // 2, MARGIN + HEADER_H // 2),
    "STORE OWNED V2 — 6 CONCEPTS — R2 FINAL",
    fill=GOLD, font=font_hdr, anchor="mm",
)

for i, (slug, label, zoom_y) in enumerate(CONCEPTS):
    x0 = MARGIN + i * (PANEL_W + GAP)
    sheet = Image.open(os.path.join(BASE, slug, "round_2.png")).convert("RGB")

    # Panel 2 (concept state) crop: xs[2]=700, panel_y=102
    concept = sheet.crop((700, 102, 700 + PANEL_W, 102 + PANEL_H))
    panel_top = MARGIN + HEADER_H + GAP
    canvas.paste(concept, (x0, panel_top))

    # Thin separator
    draw.line([(x0, panel_top + PANEL_H + 1), (x0 + PANEL_W - 1, panel_top + PANEL_H + 1)], fill=DIM, width=1)

    # Zoom strip (true 1× read, scale2x'd by the render script)
    zoom = sheet.crop((700, zoom_y, 700 + PANEL_W, zoom_y + PANEL_H))
    zoom_top = panel_top + PANEL_H + GAP
    canvas.paste(zoom, (x0, zoom_top))

    # Footer: slug label
    footer_cy = zoom_top + PANEL_H + FOOTER_H // 2 + 2
    draw.text((x0 + PANEL_W // 2, footer_cy - 8), label, fill=CREAM, font=font_lbl, anchor="mm")
    draw.text((x0 + PANEL_W // 2, footer_cy + 8), "FINAL", fill=DIM, font=font_sub, anchor="mm")

out = os.path.join(BASE, "showcase.png")
canvas.save(out)
print(f"saved {out} ({canvas.width}x{canvas.height})")
