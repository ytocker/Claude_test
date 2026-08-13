"""Live gameplay confirm popup vs the locked CHECKPOINT 5 design, in context.

Every panel is the FULL 360x640 store screen at the same scale, so true
dimensions are directly comparable. The left panel drives the real
StoreScene with a real catalog item confirmed — the byte-for-byte gameplay
draw (category grid behind, scrim, stock popup at (50,40)). The right
panels rebuild the same frame and composite the locked design's popup at
the same position, same item, same real name and price.

Output: colorways/current_vs_checkpoint5_v2.png
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _confirm_v8_premv1_hybrid2 as h2
import _confirm_v8_premv1_hybrid2_colorway as cw
import _confirm_v8_premv1_hybrid2_frames as fr
import _confirm_v8_premv1_hybrid2_outline_compare as oc
from _confirm_v8_premv1_hybrid2_buy_accents import make_buttons_accent
from _confirm_v8_premv1_hybrid2_buy_accents4 import make_inner_keyline
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
from _confirm_v8_premv1_hybrid2_name_layout import CHIP_CY
import game.store as store_mod
import game.store_cards as sc
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store import StoreScene
from game.config import W, H
from game.store import _confirm_tier_banner
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
PX, PY = (W - POP_W) // 2, 40
BG_DEEP_A, BG_GLINT_A = 155, 138
SID = "skin_mummy"


def store_frame(scene, confirm_sid):
    scene._confirm = confirm_sid
    surf = pygame.Surface((W, H))
    scene.render(surf)
    return surf


def render_locked_frame(scene, tier):
    """The locked popup drawn into the real gameplay frame: the patched base
    draw paints the scrim and alpha-blits the card itself, so the store shows
    through around the rounded corners exactly as in game."""
    frame = store_frame(scene, None)

    class _Stub:
        _confirm = SID
        _confirm_panel = None
        confirm_yes_rect = None
        confirm_no_rect = None

        @staticmethod
        def _disp_name(sid):
            return scene._disp_name(sid)

    h2._DRAW_FN[0](_Stub(), frame)

    ov = pygame.Surface((POP_W * sc.SS, POP_H * sc.SS), pygame.SRCALPHA)
    h2.overlay_buttons(ov)
    h2.overlay_bullion_chip(ov, store_catalog.cost(SID), h2._chip_cy(tier))
    pal = sc.RARITY[tier.lower()]
    _confirm_tier_banner(ov, POP_W // 2, 402, 140, 23, tier.upper(), pal)
    frame.blit(pygame.transform.smoothscale(ov, (POP_W, POP_H)), (PX, PY))
    return frame


def main():
    _orig_bal = store_data.balance
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    try:
        scene = StoreScene()
        scene.view = "category"
        scene.tab = 0
        scene.page = 0
        tier = store_catalog.rarity(SID)

        panels = [("CURRENT (live gameplay)", store_frame(scene, SID))]

        h2.CHIP_CY = CHIP_CY
        h2._chip_cy = lambda _tier: _chip_cy_zone_named(scene._disp_name(SID))
        _, silver_pal = DESIGNS[0]
        can_stops, _t, _, _ = silver_pal["can"]
        systems = (("LOCKED · gold", oc.GOLD, oc.PANEL_GOLD, (26, 17, 4)),
                   ("LOCKED · silver", oc.SILVER, oc.PLATINUM, (14, 16, 30)))
        for label, pal, (bar, buy), shadow in systems:
            fr.SIL_DEEP, fr.SIL_MID, fr.SIL_BRIGHT = (pal["deep"], pal["mid"],
                                                      pal["bright"])
            fr.GEM_SIL, fr.GEM_SIL_DEEP = pal["gem"], pal["gem_deep"]
            h2._DRAW_FN[0] = oc._patched_draw(pal["ring"])
            store_mod._bg_hook = hook_constellation(pal["glint"],
                                                    BG_DEEP_A, BG_GLINT_A)
            store_mod._frame_hook = fr.frame_double_bevel
            h2.overlay_bullion_chip = cw.make_chip_fn(bar)
            _bs, buy_text, _rd, _rb = buy
            h2.overlay_buttons = make_buttons_accent(
                can_stops, buy_text, pal["deep"], pal["bright"],
                make_inner_keyline(pal["glint"], pal["bright"], shadow))
            panels.append((label, render_locked_frame(scene, tier)))

        MARGIN, HEAD, GAP = 24, 52, 20
        cell_w, cell_h = W * 2, H * 2
        strip_w = MARGIN * 2 + len(panels) * (cell_w + GAP) - GAP
        strip_h = HEAD + cell_h + 34
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 16),
                 "confirm popup in gameplay · live v5_integration vs CHECKPOINT 5 "
                 f"· {scene._disp_name(SID)} ({tier}) · full screen · 2x",
                 fill=(236, 214, 160))
        for i, (label, surf) in enumerate(panels):
            pil = Image.frombytes("RGB", (W, H), pygame.image.tostring(surf, "RGB"))
            x = MARGIN + i * (cell_w + GAP)
            strip.paste(pil.resize((cell_w, cell_h), Image.LANCZOS), (x, HEAD))
            idr.text((x + cell_w // 2, HEAD + cell_h + 10), label,
                     fill=(206, 190, 150), anchor="mt")
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "current_vs_checkpoint5_v2.png")
        strip.save(out)
        print("saved", out, strip.size)
    finally:
        store_data.balance = _orig_bal
        h2.CHIP_CY = _orig_chip_cy
        for attr in ("_bg_hook", "_frame_hook"):
            if hasattr(store_mod, attr):
                delattr(store_mod, attr)


def _chip_cy_zone_named(name):
    """The checkpoint push-down rule evaluated for a real item name instead of
    the fixture names baked into _chip_cy_zone."""
    fs = 45
    f = sc.font(fs)
    mw = sc.m(240 - 20)
    while sc._glyph_base(name, f, 0).get_width() > mw and fs > 24:
        fs -= 1
        f = sc.font(fs)
    if sc._glyph_base(name, f, 0).get_width() <= mw:
        return CHIP_CY
    words = name.split()
    best = max(1, len(words) // 2)
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if max(sc._glyph_base(a, f, 0).get_width(),
               sc._glyph_base(b, f, 0).get_width()) <= mw:
            best = i
    fh = f.get_height()
    cy1 = sc.m(135 + 53) + sc.m(6) + fh // 2
    cy2 = cy1 + int(fh * 1.15)
    return max(CHIP_CY, (cy2 + fh // 2) // sc.SS + 10 + 14)


if __name__ == "__main__":
    main()
