"""Full-landing-screen version of the text-clarity ladder for the chosen
marquee sign (option C). Each tile is the complete 360x640 store landing
screen at 1x, so the sign's text can be judged in real gameplay context
rather than a close-up crop.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((8, 8))

from PIL import Image, ImageDraw, ImageFont

import game.store_hub as sh
import tools.stall_variant_showman_marquee as mar
from tools._marquee_text_options import C_PALETTE, LADDER, render

W, H = 360, 640


def main():
    tiles = []
    for name, patch in LADDER:
        big = render(patch)
        full = pygame.transform.smoothscale(big, (W, H))
        pil = Image.frombytes("RGB", full.get_size(),
                              pygame.image.tostring(full, "RGB"))
        tiles.append((name, pil))
        print(f"rendered {name}")

    fnt = ImageFont.truetype("game/assets/LiberationSans-Bold.ttf", 22)
    fnt2 = ImageFont.truetype("game/assets/LiberationSans-Bold.ttf", 28)
    HDR = 34
    COLS = 3
    GAP = 16
    Wf = 20 * 2 + COLS * W + (COLS - 1) * GAP
    ROWS = 2
    Hf = 16 + 46 + ROWS * (HDR + H + 14)
    fig = Image.new("RGB", (Wf, Hf), (8, 8, 20))
    d = ImageDraw.Draw(fig)
    d.text((20, 22), "OPTION C — TEXT CLARITY LADDER (full landing screens)",
           font=fnt2, fill=(244, 214, 128))
    y = 16 + 46
    for i, (name, im) in enumerate(tiles):
        x = 20 + (i % COLS) * (W + GAP)
        if i and i % COLS == 0:
            y += HDR + H + 14
        d.text((x, y + 2), name, font=fnt, fill=(230, 230, 230))
        cy = y + HDR
        fig.paste(im, (x, cy))
        d.rectangle([x - 1, cy - 1, x + W, cy + H], outline=(70, 60, 40))
    out = "docs/stall_sign_item/marquee_text_options_full_v1.png"
    fig.save(out)
    print("saved", out, fig.size)


if __name__ == "__main__":
    main()
