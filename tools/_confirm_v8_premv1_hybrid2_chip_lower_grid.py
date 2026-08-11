"""Lower-price-bar grid for the two matched colourways.

The dead zone around the quatrefoil reads as unused real estate; the scribble
is a background effect, so the bar may slide down over it. Grid: rows are the
two selected colour systems (#2 two-metals matched, #4 ivory-manuscript
matched), columns are bar centre positions from the current cy=247 down to
cy=300 (deep in the dead zone, seated over the scribble). Quatrefoil stays at
cy=297 underneath in every panel. EPIC tier.
"""
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
import _confirm_v8_premv1_hybrid2_colorway_matched as matched
import game.store_data as store_data
import game.store_catalog as store_catalog
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
CY_OPTIONS = [247, 265, 283, 300]

DESIGNS = [
    ("#2 two-metals · silver/silver",
     matched.variant("two-metals", cw.PALETTES_R2["two-metals"], True)),
    ("#4 ivory-manuscript · ivory/ivory",
     matched.variant("ivory-manuscript", cw.PALETTES_R2["ivory-manuscript"], True)),
]


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: {v: h2.PRICES[k] for k, v in h2.SIDS.items()}.get(sid, 0)
    h2._DRAW_FN[0] = btn._patched_draw()
    try:
        MARGIN, HEAD, GAP, ROW_FOOT = 20, 46, 12, 26
        strip_w = MARGIN * 2 + len(CY_OPTIONS) * (POP_W + GAP) - GAP
        strip_h = HEAD + len(DESIGNS) * (POP_H + ROW_FOOT + 24) + MARGIN
        grid = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(grid)
        idr.text((MARGIN, 14),
                 "lower price bar · rows: matched colourways · cols: bar centre y · EPIC",
                 fill=(236, 214, 160))

        y = HEAD
        for row_label, pal in DESIGNS:
            h2.overlay_buttons = cw.make_buttons_fn(pal["buy"], pal["can"])
            h2.overlay_quatrefoil = cw.make_quatrefoil_fn(pal["glint"])
            idr.text((MARGIN, y + 2), row_label, fill=(206, 190, 150))
            y += 20
            for i, cy in enumerate(CY_OPTIONS):
                h2.CHIP_CY = cy
                h2.overlay_bullion_chip = cw.make_chip_fn(pal["bar"])
                pop = h2.render_popup("EPIC")
                pil = Image.frombytes("RGB", (POP_W, POP_H),
                                      pygame.image.tostring(pop, "RGB"))
                x = MARGIN + i * (POP_W + GAP)
                grid.paste(pil, (x, y))
                tag = f"cy={cy}" + ("  (current)" if cy == 247 else "")
                idr.text((x + POP_W // 2, y + POP_H + 5), tag,
                         fill=(170, 170, 195), anchor="mt")
            y += POP_H + ROW_FOOT + 4

        out_img = grid.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "chip_lower_grid.png")
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost
        h2.CHIP_CY = _orig_chip_cy


if __name__ == "__main__":
    main()
