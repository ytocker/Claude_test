"""colorways showcase: CURRENT (gold-on-gold) + 5 round_2 colourways."""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _confirm_v8_premv1_hybrid2 as h2
import _confirm_v8_premv1_hybrid2_button_options as btn
import _confirm_v8_premv1_hybrid2_colorway as cw
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store_cards import GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "docs", "confirm_purchase_v8", "premium-v1", "colorways")
OUT_PNG = os.path.join(BASE, "showcase_v1.png")

SLUGS = ["gold-reserve", "two-metals", "emerald-commerce",
         "ivory-manuscript", "midnight-royal"]

PANEL_W, PANEL_H = 200, 355
MARGIN, GAP, HEADER_H, FOOTER_H = 20, 8, 40, 48
N_PANELS = 1 + len(SLUGS)
CANVAS_W = MARGIN * 2 + N_PANELS * PANEL_W + (N_PANELS - 1) * GAP
CANVAS_H = HEADER_H + MARGIN + PANEL_H + FOOTER_H + MARGIN
BG = (8, 8, 20)

EPIC_CROP = (584, 116, 1104, 1000)

CURRENT = dict(
    bar=(cw.G2, (52, 28, 4), GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT),
    buy=(cw.Z1, cw.CREAM, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT),
    can=(cw.INDIGO_CAN, (150, 155, 200),
         cw.CARD_RING_DEEP, cw.CARD_RING_BRIGHT),
    glint=(200, 165, 90))


def render_current():
    h2.overlay_bullion_chip = cw.make_chip_fn(CURRENT["bar"])
    h2.overlay_buttons = cw.make_buttons_fn(CURRENT["buy"], CURRENT["can"])
    h2.overlay_quatrefoil = cw.make_quatrefoil_fn(CURRENT["glint"])
    pop = h2.render_popup("EPIC")
    pil = Image.frombytes("RGB", (260, 442), pygame.image.tostring(pop, "RGB"))
    return pil.resize((PANEL_W, PANEL_H), Image.LANCZOS)


def epic_crop(path):
    region = Image.open(path).crop(EPIC_CROP)
    return region.resize((PANEL_W, PANEL_H), Image.LANCZOS)


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: {v: h2.PRICES[k] for k, v in h2.SIDS.items()}.get(sid, 0)
    h2._DRAW_FN[0] = btn._patched_draw()
    try:
        canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
        draw = ImageDraw.Draw(canvas)
        try:
            font_hdr = ImageFont.truetype("game/assets/bold.ttf", 18)
            font_lbl = ImageFont.truetype("game/assets/bold.ttf", 11)
            font_id = ImageFont.truetype("game/assets/bold.ttf", 16)
        except Exception:
            font_hdr = font_lbl = font_id = ImageFont.load_default()

        draw.text((CANVAS_W // 2, HEADER_H // 2),
                  "HYBRID-2 COLOURWAYS · holistic colour systems",
                  fill=(200, 190, 240), font=font_hdr, anchor="mm")

        panels = [("current gold-on-gold", render_current())]
        for slug in SLUGS:
            panels.append((slug, epic_crop(os.path.join(BASE, slug, "round_2.png"))))

        ids = ["CURRENT", "#1", "#2", "#3", "#4", "#5"]
        for i, (label, panel) in enumerate(panels):
            x = MARGIN + i * (PANEL_W + GAP)
            y = HEADER_H + MARGIN
            canvas.paste(panel, (x, y))
            ft = y + PANEL_H
            col = (240, 220, 100) if i > 0 else (160, 160, 180)
            draw.text((x + PANEL_W // 2, ft + 14), ids[i],
                      fill=col, font=font_id, anchor="mm")
            draw.text((x + PANEL_W // 2, ft + 34), label,
                      fill=(150, 140, 190), font=font_lbl, anchor="mm")

        canvas.save(OUT_PNG)
        print("saved", OUT_PNG, canvas.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost


if __name__ == "__main__":
    main()
