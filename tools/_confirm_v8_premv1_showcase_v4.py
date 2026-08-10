"""premium-v1 showcase v4: BEFORE + 5 concepts + hybrids #6 and #7."""

import os
import sys
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame.init()
pygame.display.set_mode((1, 1))

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game.store_cards as sc
def _safe_gloss(surf, rect, radius, peak=46):
    w, h = rect[2], rect[3]
    gsurf = pygame.Surface((w, h), pygame.SRCALPHA)
    gsurf.fill((0, 0, 0, 0))
    steps = 10
    for i in range(steps):
        t = i / (steps - 1)
        alpha = int(peak * (1 - t))
        bar_h = max(1, int(h * 0.45 * (1 - t)))
        pygame.draw.ellipse(gsurf, (255, 255, 255, alpha),
            (int(w * 0.1), int(h * 0.04 + i * 1.5), int(w * 0.8), bar_h))
    surf.blit(gsurf, (rect[0], rect[1]))
sc.gloss_sweep = _safe_gloss

from PIL import Image, ImageDraw, ImageFont

SLUGS = [
    "sovereign-seal",
    "midnight-enamel",
    "obsidian-forge",
    "lacquer-nacre",
    "lapidary-vault",
    "hybrid-1",
    "hybrid-2",
]
BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "docs", "confirm_purchase_v8", "premium-v1")
OUT_PNG = os.path.join(BASE, "showcase_v4.png")

PANEL_W, PANEL_H = 200, 355
MARGIN = 20
GAP = 8
HEADER_H = 40
FOOTER_H = 48
N_PANELS = 1 + len(SLUGS)

CANVAS_W = MARGIN + N_PANELS * PANEL_W + (N_PANELS - 1) * GAP + MARGIN
CANVAS_H = HEADER_H + MARGIN + PANEL_H + FOOTER_H + MARGIN
BG = (8, 8, 20)

EPIC_X0, EPIC_X1 = 584, 1104
EPIC_Y0_1040, EPIC_Y1_1040 = 116, 1000
EPIC_Y0_1080, EPIC_Y1_1080 = 156, 1040


def render_before() -> Image.Image:
    import game.store_data as _dat
    import game.store_catalog as _cat
    from game.store import StoreScene

    SID = "skin_baseball"
    _orig_bal = _dat.balance
    _dat.balance = lambda: 99999
    try:
        class _Stub:
            _confirm = SID
            _confirm_panel = None
            confirm_yes_rect = None
            confirm_no_rect = None

            @staticmethod
            def _disp_name(sid):
                try:
                    return _cat.name(sid)
                except Exception:
                    return sid.replace("skin_", "").upper()

        surf = pygame.Surface((360, 640))
        surf.fill((8, 8, 20))
        StoreScene._draw_confirm(_Stub(), surf)
        crop = surf.subsurface(pygame.Rect(50, 40, 260, 442)).copy()
        raw = pygame.image.tostring(crop, "RGB")
        return Image.frombytes("RGB", (260, 442), raw)
    finally:
        _dat.balance = _orig_bal


def epic_crop(path: str) -> Image.Image:
    strip = Image.open(path)
    w, h = strip.size
    if h >= 1075:
        y0, y1 = EPIC_Y0_1080, EPIC_Y1_1080
    else:
        y0, y1 = EPIC_Y0_1040, EPIC_Y1_1040
    region = strip.crop((EPIC_X0, y0, EPIC_X1, y1))
    return region.resize((PANEL_W, PANEL_H), Image.LANCZOS)


def make_showcase():
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
    draw = ImageDraw.Draw(canvas)

    try:
        font_hdr = ImageFont.truetype("game/assets/bold.ttf", 18)
        font_lbl = ImageFont.truetype("game/assets/bold.ttf", 11)
        font_id = ImageFont.truetype("game/assets/bold.ttf", 16)
    except Exception:
        font_hdr = font_lbl = font_id = ImageFont.load_default()

    draw.text((CANVAS_W // 2, HEADER_H // 2),
              "CONFIRM POPUP · PREMIUM ENHANCE v1 · + HYBRIDS",
              fill=(200, 190, 240), font=font_hdr, anchor="mm")

    panels = [("BEFORE", render_before().resize((PANEL_W, PANEL_H), Image.LANCZOS))]
    for slug in SLUGS:
        panels.append((slug, epic_crop(os.path.join(BASE, slug, "round_2.png"))))

    ID_LABELS = ["BEFORE", "#1", "#2", "#3", "#4", "#5", "#6", "#7"]
    for i, (label, panel) in enumerate(panels):
        x = MARGIN + i * (PANEL_W + GAP)
        y = HEADER_H + MARGIN
        canvas.paste(panel, (x, y))
        footer_top = y + PANEL_H
        id_col = (240, 220, 100) if i > 0 else (160, 160, 180)
        draw.text((x + PANEL_W // 2, footer_top + 14),
                  ID_LABELS[i], fill=id_col, font=font_id, anchor="mm")
        draw.text((x + PANEL_W // 2, footer_top + 34),
                  label, fill=(150, 140, 190), font=font_lbl, anchor="mm")

    canvas.save(OUT_PNG)
    print(f"saved {OUT_PNG}  {canvas.size}")


if __name__ == "__main__":
    make_showcase()
