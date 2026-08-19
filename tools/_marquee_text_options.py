"""Text-clarity ladder for the chosen marquee sign (option C: lacquer red +
cream piping + gold bulbs). Varies font size, stroke weight, char-border width
and the ink-box gold remap; each tile = supersampled PARCELS sign close-up +
a 1x strip of all three stalls' sign bands, labeled with measured contrast.
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

# option C palette, fixed across the ladder
C_PALETTE = dict(CARTOUCHE_TOP=(122, 26, 30), CARTOUCHE_BOT=(74, 12, 18),
                 PIPING_COLOR=(206, 188, 158),
                 INK_TOP=(255, 232, 160), INK_BOT=(216, 166, 84))

LADDER = [
    ("T1 pt11 w1.0 kw1.0 (current)", dict()),
    ("T2 pt11 w1.3 kw1.0 bold", dict(INK_W=1.3)),
    ("T3 pt11 w1.3 kw1.4 heavy border", dict(INK_W=1.3, INK_KW=1.4)),
    ("T4 pt11.5 w1.0 kw1.0 larger", dict(INK_PT=11.5)),
    ("T5 pt11.5 w1.3 kw1.2 larger+bold", dict(INK_PT=11.5, INK_W=1.3, INK_KW=1.2)),
    ("T6 pt11 w1.3 bright ramp", dict(INK_W=1.3, INK_REMAP=True)),
]

W, H = 360, 640
STALLS = {"PARROTS": (51.1, 0.92, 0.788), "PARCELS": (180.0, 0.96, 0.862),
          "COSTUMES": (308.9, 0.92, 0.788)}


def render(patch):
    allp = {**C_PALETTE, **patch}
    saved = {k: getattr(mar, k) for k in allp}
    for k, v in allp.items():
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
    return big


def main():
    tiles = []
    for name, patch in LADDER:
        big = render(patch)
        full = pygame.transform.smoothscale(big, (W, H))
        pil = Image.frombytes("RGB", full.get_size(),
                              pygame.image.tostring(full, "RGB"))
        a = np.asarray(pil.convert("L"), dtype=np.float64)
        worst = 99.0
        for cx, sc, fy in STALLS.values():
            deck = int(H * fy)
            bt = deck - int(64 * sc)
            z = a[bt - 17:bt - 7, int(cx - 28):int(cx + 28)]
            ink = z[z >= np.percentile(z, 90)].mean()
            worst = min(worst, ink / max(1.0, np.percentile(z, 25)))
        # COSTUMES fit check: widest label ink vs cartouche inner width
        f = sh.font(getattr(mar, "INK_PT", 11) * 0.92)
        for k, v in patch.items():
            pass
        ink_w = sh._glyph_base("COSTUMES", sh.font(
            patch.get("INK_PT", 11) * 0.92), sh.m(0.6)).get_width()
        fit = ink_w <= int(sh.m(38) * 0.92) * 2 - 2 * sh.m(2)
        # supersampled PARCELS sign crop
        m = sh.m
        cxd, deckd = int(sh.DW * 0.5), int(sh.DH * 0.862)
        btd = deckd - int(m(64) * 0.96)
        crop = pygame.Rect(cxd - m(50), btd - m(24), m(100), m(26))
        close = big.subsurface(crop.clip(big.get_rect())).copy()
        pc = Image.frombytes("RGB", close.get_size(),
                             pygame.image.tostring(close, "RGB"))
        af = np.asarray(pil, dtype=np.uint8)
        strips = []
        for scx, ssc, sfy in STALLS.values():
            d2 = int(H * sfy)
            sbt = d2 - int(64 * ssc)
            strips.append(af[sbt - 24:sbt + 1, int(scx - 48):int(scx + 48)])
        hmin = min(s.shape[0] for s in strips)
        strip = Image.fromarray(
            np.concatenate([s[:hmin] for s in strips], axis=1))
        tiles.append((name, worst, fit, pc, strip))
        print(f"{name:34s} ink {worst:.2f}:1  COSTUMES-fit={'OK' if fit else 'FAIL'}")

    fnt = ImageFont.truetype("game/assets/LiberationSans-Bold.ttf", 22)
    fnt2 = ImageFont.truetype("game/assets/LiberationSans-Bold.ttf", 28)
    TW = 560
    ch = int(tiles[0][3].height * TW / tiles[0][3].width)
    strip_h = 78
    tile_h = 34 + ch + 6 + strip_h + 14
    COLS = 3
    Wf = 20 * 2 + COLS * TW + (COLS - 1) * 12
    Hf = 16 + 46 + 2 * tile_h
    fig = Image.new("RGB", (Wf, Hf), (8, 8, 20))
    d = ImageDraw.Draw(fig)
    d.text((20, 22), "OPTION C — TEXT CLARITY LADDER (close-up + 1x strips)",
           font=fnt2, fill=(244, 214, 128))
    y = 16 + 46
    for i, (name, c, fit, pc, strip) in enumerate(tiles):
        x = 20 + (i % COLS) * (TW + 12)
        if i and i % COLS == 0:
            y += tile_h
        d.text((x, y + 2), f"{name}  {c:.1f}:1", font=fnt,
               fill=(230, 230, 230) if fit else (255, 120, 120))
        cy = y + 34
        fig.paste(pc.resize((TW, ch), Image.LANCZOS), (x, cy))
        fig.paste(strip.resize((TW, strip_h), Image.LANCZOS),
                  (x, cy + ch + 6))
        d.rectangle([x - 1, cy - 1, x + TW, cy + ch + 6 + strip_h],
                    outline=(70, 60, 40))
    out = "docs/stall_sign_item/marquee_text_options_v1.png"
    fig.save(out)
    print("saved", out, fig.size)


if __name__ == "__main__":
    main()
