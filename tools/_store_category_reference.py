"""Reference screenshot: the live store category screen, as-is.

Drives the real StoreScene with view="category" and captures two tabs
(COSTUMES and PARROTS, page 0) so the current item-card grid is visible
exactly as the game renders it. 2× upscale for review.

Output: docs/confirm_purchase_v8/premium-v1/colorways/store_category_reference_v1.png
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game.store_data as store_data
from game.store import StoreScene
from game.config import W, H
from PIL import Image, ImageDraw


def main():
    _orig_bal = store_data.balance
    store_data.balance = lambda: 99999
    try:
        scene = StoreScene()
        scene.view = "category"
        panels = []
        for tab_i, label in ((0, "COSTUMES · page 1"), (1, "PARROTS · page 1")):
            scene.tab = tab_i
            scene.page = 0
            surf = pygame.Surface((W, H))
            scene.render(surf)
            pil = Image.frombytes("RGB", (W, H), pygame.image.tostring(surf, "RGB"))
            panels.append((label, pil))

        MARGIN, HEAD, GAP = 20, 46, 16
        strip_w = MARGIN * 2 + len(panels) * (W + GAP) - GAP
        strip_h = HEAD + H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 14), "store category screen · current live render · reference",
                 fill=(236, 214, 160))
        for i, (label, pil) in enumerate(panels):
            x = MARGIN + i * (W + GAP)
            strip.paste(pil, (x, HEAD))
            idr.text((x + W // 2, HEAD + H + 4), label,
                     fill=(170, 170, 195), anchor="mt")

        out_img = strip.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "store_category_reference_v1.png")
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal


if __name__ == "__main__":
    main()
