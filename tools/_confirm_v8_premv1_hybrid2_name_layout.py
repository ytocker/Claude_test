"""FINAL name layout — zone-centred item name, silver colourway, both cases.

The band between hero disc bottom (~188) and price-bar top (283) is the
name's home zone, centred at NAME_ZONE_C=237. A one-line name sits at the
zone centre (lower than the old 213); a two-line name keeps the same block
centre so line 1 rises and line 2 drops symmetrically. The bar's push-down
mirrors the new geometry — with the zone centred, a 2-line block clears the
bar at cy=300 without pushing.

Output: colorways/final_name_layout.png — silver colourway, EPIC,
panel 1 = one-line name, panel 2 = two-line name.
"""
import os
import sys
import re
import inspect
import textwrap

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _confirm_v8_premv1_hybrid2 as h2
import _confirm_v8_premv1_hybrid2_colorway as cw
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
import game.store as store_mod
import game.store_cards as sc
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store import StoreScene
from game.store_cards import m
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
CHIP_CY = 300
NAME_ZONE_C = 237
BG_DEEP_A, BG_GLINT_A = 110, 100

LONG_NAME = "CELESTIAL PRISM GUARDIAN"


def _patched_draw_final():
    """Base patch set (chip/buttons suppressed, bg hook) + zone-centred name."""
    src = textwrap.dedent(inspect.getsource(StoreScene._draw_confirm))
    subs = [
        (r"_chip\(m\(CX\), m\(CHIP_CY\)\)", "pass"),
        (r'_btn\(buy_r, "BUY", locked=not affordable\)', "pass"),
        (r'_btn\(can_r, "CANCEL", is_cancel=True\)', "pass"),
        (r"(\n\s*# ── corner gem pair)", r"\n    _bg_hook(big)\1"),
        # one-line name drops to the zone centre
        (r"NAME_FS, Y_NAME = 45, 213", f"NAME_FS, Y_NAME = 45, {NAME_ZONE_C}"),
        # two-line block centres on the same point: line 1 up, line 2 down
        (r"_cy1 = _disc_bot_ss \+ _nfnt\.get_height\(\) // 2",
         f"_cy1 = m({NAME_ZONE_C}) - int(_nfnt.get_height() * 1.15) // 2"),
    ]
    for pat, rep in subs:
        src, n = re.subn(pat, rep, src)
        assert n == 1, f"patch failed: {pat}"
    ns = {}
    exec(compile(src, "<final_name_draw>", "exec"), store_mod.__dict__, ns)
    return ns["_draw_confirm"]


def _chip_cy_zone(tier):
    """Push-down mirroring the zone-centred name block."""
    name = h2.NAMES[tier]
    fs = 45
    f = sc.font(fs)
    mw = m(240 - 20)
    while sc._glyph_base(name, f, 0).get_width() > mw and fs > 24:
        fs -= 1
        f = sc.font(fs)
    if sc._glyph_base(name, f, 0).get_width() <= mw:
        return CHIP_CY
    fh = f.get_height()
    gap = int(fh * 1.15)
    cy2 = m(NAME_ZONE_C) + gap // 2
    return max(CHIP_CY, (cy2 + fh // 2) // sc.SS + 10 + 17)


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1400
    h2._DRAW_FN[0] = _patched_draw_final()
    h2.overlay_quatrefoil = lambda ov: None
    h2.CHIP_CY = CHIP_CY
    h2._chip_cy = _chip_cy_zone
    silver_label, silver = DESIGNS[0]
    store_mod._bg_hook = hook_constellation(silver["glint"], BG_DEEP_A, BG_GLINT_A)
    h2.overlay_bullion_chip = cw.make_chip_fn(silver["bar"])
    h2.overlay_buttons = cw.make_buttons_fn(silver["buy"], silver["can"])
    try:
        panels = []
        h2.NAMES["EPIC"] = "PRISM WING"
        panels.append(("1-line · zone-centred low", h2.render_popup("EPIC")))
        h2.NAMES["EPIC"] = LONG_NAME
        panels.append(("2-line · block up & down", h2.render_popup("EPIC")))
        h2.NAMES["EPIC"] = "PRISM WING"

        MARGIN, HEAD, GAP = 20, 58, 12
        strip_w = MARGIN * 2 + len(panels) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 18),
                 f"FINAL name layout · {silver_label} · B5 · zone centre y={NAME_ZONE_C}",
                 fill=(236, 214, 160))
        for i, (label, pop) in enumerate(panels):
            pil = Image.frombytes("RGB", (POP_W, POP_H),
                                  pygame.image.tostring(pop, "RGB"))
            x = MARGIN + i * (POP_W + GAP)
            strip.paste(pil, (x, HEAD))
            idr.text((x + POP_W // 2, HEAD + POP_H + 6), label,
                     fill=(206, 190, 150), anchor="mt")

        out_img = strip.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "final_name_layout.png")
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost
        h2.CHIP_CY = _orig_chip_cy
        if hasattr(store_mod, "_bg_hook"):
            del store_mod._bg_hook


if __name__ == "__main__":
    main()
