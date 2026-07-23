"""premium-v2 showcase — BEFORE + 5 round_2 panels, ID badges #1-#5."""
import os
import sys
import pygame
import numpy as np

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame.init()
pygame.display.set_mode((1, 1))

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game.store_cards as sc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREMV2 = os.path.join(ROOT, "docs", "confirm_purchase_v8", "premium-v2")

SLUGS = [
    "stellar-crown",
    "divine-radiance",
    "onyx-imperial",
    "illuminated-codex",
    "aurora-chromatic",
]

PANEL_W, PANEL_H = 200, 355
MARGIN, GAP, HEAD, FOOT = 20, 8, 40, 32
BG = (8, 8, 20)

# EPIC crop from 1688×1040 strip (panel index 1 out of RARE/EPIC/LEGENDARY)
EPIC_CROP = (584, 116, 1104, 1000)  # x0, y0, x1, y1


def _load_panel(png_path):
    """Load a 1688×1040 strip, crop EPIC region, scale to PANEL_W×PANEL_H."""
    surf = pygame.image.load(png_path)
    w, h = surf.get_size()
    # crop EPIC region
    x0, y0, x1, y1 = EPIC_CROP
    crop_w, crop_h = x1 - x0, y1 - y0
    crop = pygame.Surface((crop_w, crop_h))
    crop.blit(surf, (0, 0), (x0, y0, crop_w, crop_h))
    # scale to panel size
    panel = pygame.transform.smoothscale(crop, (PANEL_W, PANEL_H))
    return panel


def _render_before_panel():
    """Render the current _draw_confirm EPIC popup as a panel."""
    import game.store as store
    import game.store_catalog as catalog
    import game.store_data as sdata
    try:
        sdata.init()
    except Exception:
        pass
    try:
        catalog.init()
    except Exception:
        pass

    # render the real popup for skin_prism (EPIC)
    try:
        skin = catalog.get_skin("skin_prism")
    except Exception:
        skin = None

    # fallback: render using direct call
    big = pygame.Surface((260 * 2, 442 * 2), pygame.SRCALPHA)
    try:
        store._draw_confirm(big, "skin_prism", price=1400, owned=False)
    except Exception:
        big.fill((28, 30, 70))
        f = sc.font(14)
        sc.plain_text(big, "BEFORE", f, (260, 442), (255, 255, 255), shadow_a=0)
    panel = pygame.transform.smoothscale(big, (PANEL_W, PANEL_H))
    return panel


def _draw_badge(surf, cx, cy, label, is_before=False):
    f = sc.font(11)
    col = (160, 160, 180) if is_before else (240, 220, 100)
    sc.plain_text(surf, label, f, (cx, cy), col, shadow_a=0, weight=sc.m(0.8))


def main():
    n_before = 1
    n_panels = n_before + len(SLUGS)

    canvas_w = MARGIN * 2 + n_panels * PANEL_W + (n_panels - 1) * GAP
    canvas_h = HEAD + PANEL_H + FOOT + MARGIN * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill(BG)

    title_f = sc.font(14)
    sc.plain_text(canvas, "CONFIRM PURCHASE  ·  premium-v2  ·  round_2",
                  title_f, (canvas_w // 2, MARGIN + HEAD // 2),
                  (220, 210, 190), shadow_a=0, weight=sc.m(0.8))

    # BEFORE panel
    before = _render_before_panel()
    px = MARGIN
    py = MARGIN + HEAD
    canvas.blit(before, (px, py))
    _draw_badge(canvas, px + PANEL_W // 2, py + PANEL_H + 16, "BEFORE", is_before=True)
    px += PANEL_W + GAP

    # concept panels
    for i, slug in enumerate(SLUGS):
        png = os.path.join(PREMV2, slug, "round_2.png")
        panel = _load_panel(png)
        canvas.blit(panel, (px, py))
        _draw_badge(canvas, px + PANEL_W // 2, py + PANEL_H + 16, f"#{i+1}", is_before=False)
        # slug name below badge
        sf = sc.font(9)
        sc.plain_text(canvas, slug, sf, (px + PANEL_W // 2, py + PANEL_H + 28),
                      (140, 140, 160), shadow_a=0, weight=sc.m(0.4))
        px += PANEL_W + GAP

    out = os.path.join(PREMV2, "showcase_v1.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("wrote", out, canvas.get_size())


if __name__ == "__main__":
    main()
