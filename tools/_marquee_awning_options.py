"""Awning-themed colorway options for the ORIGINAL showman-marquee sign.

Renders the marquee sign (stepped cartouche + six bulbs) in several red/cream
awning-matched palettes over the chosen mix-C items, and composes a grid of
full landing screens. Each cell is labeled with its measured ink-vs-field
contrast; a per-option bulb-vs-item peak check is printed.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((8, 8))

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import game.store_hub as sh
import tools.stall_variant_showman_marquee as mar
from game.store_hub import lerp_color

AWN_RED = (212, 56, 50)
AWN_RED_D = (150, 30, 32)
AWN_CREAM = (244, 232, 206)
AWN_CREAM_D = (206, 188, 158)
GOLD_INK = dict(INK_TOP=(255, 232, 160), INK_BOT=(216, 166, 84))

# every option: uniform bulb glass (alternating glass reads as burnt-out
# bulbs), field dark enough to hold gold ink and beat the lit thatch
OPTIONS = [
    ("A LACQUER RED + GOLD BULBS", dict(
        CARTOUCHE_TOP=(122, 26, 30), CARTOUCHE_BOT=(74, 12, 18), **GOLD_INK)),
    ("B OXBLOOD + WARM-WHITE BULBS", dict(
        CARTOUCHE_TOP=(88, 26, 28), CARTOUCHE_BOT=(52, 16, 18),
        BULB_GLASS=lerp_color(AWN_CREAM, AWN_CREAM_D, 0.35), **GOLD_INK)),
    ("C RED + CREAM PIPING", dict(
        CARTOUCHE_TOP=(122, 26, 30), CARTOUCHE_BOT=(74, 12, 18),
        PIPING_COLOR=AWN_CREAM_D, **GOLD_INK)),
    ("D OXBLOOD + ROSE BULBS", dict(
        CARTOUCHE_TOP=(88, 26, 28), CARTOUCHE_BOT=(52, 16, 18),
        BULB_GLASS=lerp_color(AWN_RED, (255, 244, 224), 0.55),
        GOLD=lerp_color(AWN_RED, (255, 214, 160), 0.45), **GOLD_INK)),
    ("E RED + PORCELAIN SEATS", dict(
        CARTOUCHE_TOP=(122, 26, 30), CARTOUCHE_BOT=(74, 12, 18),
        BULB_SEAT=AWN_CREAM_D, **GOLD_INK)),
    ("F RED-BROWN QUIET + GOLD", dict(
        CARTOUCHE_TOP=(86, 32, 26), CARTOUCHE_BOT=(50, 24, 16), **GOLD_INK)),
]

W, H = 360, 640
STALLS = {"PARROTS": (51.1, 0.92, 0.788), "PARCELS": (180.0, 0.96, 0.862),
          "COSTUMES": (308.9, 0.92, 0.788)}


def render(patch):
    saved = {k: getattr(mar, k) for k in patch}
    for k, v in patch.items():
        setattr(mar, k, v)
    try:
        from tools import stall_variant_mixed
        stall_variant_mixed.install()
        sh.STALL_SIGN_HOOK = mar._sign
        big = sh._render_static_device()
    finally:
        for k, v in saved.items():
            setattr(mar, k, v)
        sh.STALL_SIGN_HOOK = sh.STALL_ITEM_HOOK = None
    return pygame.transform.smoothscale(big, (W, H))


def measure(pil):
    a = np.asarray(pil.convert("L"), dtype=np.float64)
    worst_c, worst_head = 99.0, 99.0
    for cx, sc, fy in STALLS.values():
        deck = int(H * fy)
        bt = deck - int(64 * sc)
        z = a[bt - 17:bt - 7, int(cx - 28):int(cx + 28)]
        ink = z[z >= np.percentile(z, 90)].mean()
        field = np.percentile(z, 25)
        worst_c = min(worst_c, ink / max(1.0, field))
        sign = a[bt - 22:bt, int(cx - 46):int(cx + 46)].max() / 255.0
        item = a[bt + int(15 * sc):deck - 6,
                 int(cx - 46):int(cx + 46)].max() / 255.0
        worst_head = min(worst_head, item - sign)
    return worst_c, worst_head


def main():
    cells = []
    for name, patch in OPTIONS:
        full = render(patch)
        pil = Image.frombytes("RGB", full.get_size(),
                              pygame.image.tostring(full, "RGB"))
        c, head = measure(pil)
        cells.append((name, c, pil))
        print(f"{name:32s} ink {c:.2f}:1  worst item-minus-sign peak "
              f"{head:+.3f}")

    f = ImageFont.truetype("game/assets/LiberationSans-Bold.ttf", 22)
    f2 = ImageFont.truetype("game/assets/LiberationSans-Bold.ttf", 28)
    CW, CH, GAP, HDR, SEC = 360, 640, 12, 34, 46
    COLS = 3
    Wf = 20 * 2 + COLS * CW + (COLS - 1) * GAP
    Hf = 16 + SEC + 2 * (HDR + CH + 14)
    fig = Image.new("RGB", (Wf, Hf), (8, 8, 20))
    d = ImageDraw.Draw(fig)
    d.text((20, 22), "MARQUEE SIGN — RED/CREAM AWNING OPTIONS "
                     "(items = chosen mix C)", font=f2, fill=(244, 214, 128))
    y = 16 + SEC
    for i, (name, c, im) in enumerate(cells):
        x = 20 + (i % COLS) * (CW + GAP)
        if i and i % COLS == 0:
            y += HDR + CH + 14
        d.text((x, y + 2), f"{name}  {c:.1f}:1", font=f, fill=(230, 230, 230))
        fig.paste(im, (x, y + HDR))
        d.rectangle([x - 1, y + HDR - 1, x + CW, y + HDR + CH],
                    outline=(70, 60, 40))
    out = "docs/stall_sign_item/marquee_awning_options_v1.png"
    fig.save(out)
    print("saved", out, fig.size)


if __name__ == "__main__":
    main()
