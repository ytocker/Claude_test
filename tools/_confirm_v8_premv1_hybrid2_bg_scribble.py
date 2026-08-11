"""Enlarged background scribble for the two matched colourways.

The quatrefoil grows from a dead-zone ornament into a background effect for
the whole upper card. It must sit BEHIND the name, hero disc, and price bar,
so a `_bg_hook(big)` call is injected into the exec-patched base draw right
after the card body — everything the base paints afterwards (gems, name,
hero) covers it naturally, and the overlay elements (bar at cy=300, buttons,
banner) stack above as well. The pattern is hard-clipped at y=337 so it never
touches the BUY/CANCEL band.

Grid: rows = the two matched colourways, columns = three pattern scales.
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
import _confirm_v8_premv1_hybrid2_colorway_matched as matched
import game.store as store_mod
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store import StoreScene
from game.store_cards import m
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
CHIP_CY = 300
BTN_TOP_CLIP = 337
Q_DEEP = (22, 24, 56)

# (label, centre_cy, lobe_offset, lobe_radius)
SCALES = [
    ("Q1 · medium", 242, 40, 44),
    ("Q2 · large", 235, 50, 55),
    ("Q3 · XL", 230, 58, 64),
]

DESIGNS = [
    ("#2 two-metals · silver", matched.variant(
        "two-metals", cw.PALETTES_R2["two-metals"], True)),
    ("#4 ivory-manuscript · ivory", matched.variant(
        "ivory-manuscript", cw.PALETTES_R2["ivory-manuscript"], True)),
]


def _patched_draw_with_hook():
    src = textwrap.dedent(inspect.getsource(StoreScene._draw_confirm))
    src, n1 = re.subn(r"_chip\(m\(CX\), m\(CHIP_CY\)\)", "pass", src)
    src, n2 = re.subn(r'_btn\(buy_r, "BUY", locked=not affordable\)', "pass", src)
    src, n3 = re.subn(r'_btn\(can_r, "CANCEL", is_cancel=True\)', "pass", src)
    src, n4 = re.subn(r"(\n\s*# ── corner gem pair)", r"\n    _bg_hook(big)\1", src)
    assert (n1, n2, n3, n4) == (1, 1, 1, 1), f"patch failed: {n1},{n2},{n3},{n4}"
    ns = {}
    exec(compile(src, "<bg_scribble_draw>", "exec"), store_mod.__dict__, ns)
    return ns["_draw_confirm"]


def make_bg_hook(glint, cy, d, rl):
    def hook(big):
        layer = pygame.Surface(big.get_size(), pygame.SRCALPHA)
        cx = m(130)
        centers = [(cx, m(cy) - m(d)), (cx, m(cy) + m(d)),
                   (cx - m(d), m(cy)), (cx + m(d), m(cy))]
        for lx, ly in centers:
            pygame.draw.circle(layer, (*Q_DEEP, 110), (lx, ly), m(rl),
                               max(2, m(7)))
        for lx, ly in centers:
            pygame.draw.circle(layer, (*glint, 150), (lx, ly), m(rl) - m(1),
                               max(1, m(1)))
        # never below the button band
        clip_y = m(BTN_TOP_CLIP)
        layer.fill((0, 0, 0, 0),
                   rect=pygame.Rect(0, clip_y, layer.get_width(),
                                    layer.get_height() - clip_y))
        big.blit(layer, (0, 0))
    return hook


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: {v: h2.PRICES[k] for k, v in h2.SIDS.items()}.get(sid, 0)
    h2._DRAW_FN[0] = _patched_draw_with_hook()
    h2.overlay_quatrefoil = lambda ov: None
    h2.CHIP_CY = CHIP_CY
    try:
        MARGIN, HEAD, GAP, ROW_FOOT = 20, 46, 12, 26
        strip_w = MARGIN * 2 + len(SCALES) * (POP_W + GAP) - GAP
        strip_h = HEAD + len(DESIGNS) * (POP_H + ROW_FOOT + 24) + MARGIN
        grid = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(grid)
        idr.text((MARGIN, 14),
                 "background scribble scales · bar cy=300 · rows: colourways · EPIC",
                 fill=(236, 214, 160))

        y = HEAD
        for row_label, pal in DESIGNS:
            h2.overlay_bullion_chip = cw.make_chip_fn(pal["bar"])
            h2.overlay_buttons = cw.make_buttons_fn(pal["buy"], pal["can"])
            idr.text((MARGIN, y + 2), row_label, fill=(206, 190, 150))
            y += 20
            for i, (tag, cy, d, rl) in enumerate(SCALES):
                store_mod._bg_hook = make_bg_hook(pal["glint"], cy, d, rl)
                pop = h2.render_popup("EPIC")
                pil = Image.frombytes("RGB", (POP_W, POP_H),
                                      pygame.image.tostring(pop, "RGB"))
                x = MARGIN + i * (POP_W + GAP)
                grid.paste(pil, (x, y))
                idr.text((x + POP_W // 2, y + POP_H + 5),
                         f"{tag} (r={rl})", fill=(170, 170, 195), anchor="mt")
            y += POP_H + ROW_FOOT + 4

        out_img = grid.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "bg_scribble_grid.png")
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
