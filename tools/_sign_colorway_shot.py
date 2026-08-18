"""Render the 10 sign colorways (5 pennant-based, 5 marquee-based) and compose
the comparison figure docs/stall_sign_item/sign_colorways_v1.png.

Each colorway monkeypatches ONLY module-level color/weight seams on the base
concept module — the sign construction never moves. Every tile shows the
supersampled sign zone of the PARCELS hero stall plus a 1x strip of all three
open stalls, labeled with the measured ink-vs-field contrast ratio at 1x.
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
import tools.stall_variant_sailcloth_pennant as pen
import tools.stall_variant_showman_marquee as mar

GOLD_INK = dict(INK_TOP=(255, 232, 160), INK_BOT=(216, 166, 84))

PENNANT = [
    ("P1 MACAW RED", pen, dict(
        CLOTH_HI=(188, 58, 42), CLOTH_LO=(140, 36, 26),
        TRIM_LIT=(244, 228, 198), TRIM_SHD=(198, 178, 146),
        TRIM_CATCH=(252, 242, 216), **GOLD_INK)),
    ("P2 LAGOON TEAL", pen, dict(
        CLOTH_HI=(22, 118, 118), CLOTH_LO=(10, 80, 82),
        TRIM_LIT=(246, 208, 120), TRIM_SHD=(176, 138, 70),
        TRIM_CATCH=(252, 232, 168), **GOLD_INK)),
    ("P3 ROYAL PURPLE", pen, dict(
        CLOTH_HI=(102, 56, 148), CLOTH_LO=(64, 32, 100),
        TRIM_LIT=(246, 208, 120), TRIM_SHD=(176, 138, 70),
        TRIM_CATCH=(252, 232, 168), **GOLD_INK)),
    ("P4 FESTIVAL GREEN", pen, dict(
        CLOTH_HI=(38, 124, 58), CLOTH_LO=(20, 84, 40),
        TRIM_LIT=(244, 228, 198), TRIM_SHD=(198, 178, 146),
        TRIM_CATCH=(252, 242, 216), **GOLD_INK)),
    ("P5 SUNSET AMBER", pen, dict(
        CLOTH_HI=(212, 96, 36), CLOTH_LO=(150, 52, 24),
        TRIM_LIT=(250, 236, 205), TRIM_SHD=(204, 176, 138),
        TRIM_CATCH=(254, 246, 222),
        INK_TOP=(255, 250, 234), INK_BOT=(244, 222, 178))),
]
MARQUEE = [
    ("M1 CRIMSON LACQUER", mar, dict(
        CARTOUCHE_TOP=(122, 26, 30), CARTOUCHE_BOT=(74, 12, 18), **GOLD_INK)),
    ("M2 MIDNIGHT BLUE", mar, dict(
        CARTOUCHE_TOP=(38, 54, 112), CARTOUCHE_BOT=(18, 28, 66), **GOLD_INK)),
    ("M3 EMERALD", mar, dict(
        CARTOUCHE_TOP=(18, 104, 70), CARTOUCHE_BOT=(8, 62, 42), **GOLD_INK)),
    ("M4 BLACK CHERRY", mar, dict(
        CARTOUCHE_TOP=(88, 26, 48), CARTOUCHE_BOT=(50, 12, 28),
        INK_TOP=(255, 240, 190), INK_BOT=(232, 186, 104), INK_W=1.3)),
    ("M5 CARVED + PANEL", mar, dict(
        PANEL_INSET=(28, 16, 9),
        INK_TOP=(255, 236, 168), INK_BOT=(224, 172, 88), INK_W=1.3)),
]

DW, DH, m = sh.DW, sh.DH, sh.m
W, H = 360, 640
STALLS_1X = {"PARROTS": (51.1, 0.92, 0.788), "PARCELS": (180.0, 0.96, 0.862),
             "COSTUMES": (308.9, 0.92, 0.788)}


def render(mod, patch):
    saved = {k: getattr(mod, k) for k in patch}
    for k, v in patch.items():
        setattr(mod, k, v)
    try:
        mod.install()
        big = sh._render_static_device()
    finally:
        for k, v in saved.items():
            setattr(mod, k, v)
        sh.STALL_SIGN_HOOK = sh.STALL_ITEM_HOOK = None
    return big


def sign_zone_1x(arr, cx, sc, fy):
    # tight window inside the sign FIELD (cloth / cartouche) on both bases, so
    # thatch around the board never pollutes the ink-vs-field measurement
    deck = int(H * fy)
    bt = deck - int(64 * sc)
    return arr[bt - 17:bt - 7, int(cx - 28):int(cx + 28)]


def contrast(full_1x):
    """Ink-vs-field ratio in the 1x text band, worst stall. The band is mostly
    wordmark, so the FIELD is what shows BETWEEN the glyphs: ink = mean of the
    brightest decile, field = the 25th percentile (the sign ground)."""
    a = np.asarray(full_1x.convert("L"), dtype=np.float64)
    worst = 99.0
    for cx, sc, fy in STALLS_1X.values():
        z = sign_zone_1x(a, cx, sc, fy)
        ink = z[z >= np.percentile(z, 90)].mean()
        field = np.percentile(z, 25)
        worst = min(worst, ink / max(1.0, field))
    return worst


def main():
    tiles = []
    for name, mod, patch in PENNANT + MARQUEE:
        big = render(mod, patch)
        full = pygame.transform.smoothscale(big, (W, H))
        pil_full = Image.frombytes(
            "RGB", full.get_size(), pygame.image.tostring(full, "RGB"))
        c = contrast(pil_full)

        # supersampled sign-zone crop of the PARCELS hero stall
        cx, deck_y = int(DW * 0.5), int(DH * 0.862)
        bt = deck_y - int(m(64) * 0.96)
        crop = pygame.Rect(cx - m(52), bt - m(32), m(104), m(36))
        close = big.subsurface(crop.clip(big.get_rect())).copy()
        pil_close = Image.frombytes(
            "RGB", close.get_size(), pygame.image.tostring(close, "RGB"))

        # 1x strip: the three open stalls' sign bands side by side
        strips = []
        af = np.asarray(pil_full, dtype=np.uint8)
        for scx, ssc, sfy in STALLS_1X.values():
            deck = int(H * sfy)
            sbt = deck - int(64 * ssc)
            strips.append(af[sbt - 30:sbt + 2, int(scx - 50):int(scx + 50)])
        hmin = min(s.shape[0] for s in strips)
        strip = np.concatenate([s[:hmin] for s in strips], axis=1)
        tiles.append((name, c, pil_close, Image.fromarray(strip)))
        print(f"{name:20s} contrast {c:.2f}:1")

    fnt = ImageFont.truetype("game/assets/LiberationSans-Bold.ttf", 24)
    fnt2 = ImageFont.truetype("game/assets/LiberationSans-Bold.ttf", 30)
    TW = 460
    close_h = int(tiles[0][2].height * TW / tiles[0][2].width)
    strip_h = 64
    tile_h = 40 + close_h + 6 + strip_h + 14
    COLS = 5
    sec_hdr = 52
    fig = Image.new("RGB", (20 + COLS * (TW + 12), 16 + 2 * (sec_hdr + tile_h)),
                    (8, 8, 20))
    d = ImageDraw.Draw(fig)
    y = 16
    for si, (sec, group) in enumerate((("PENNANT COLORWAYS (base: design 4)",
                                        tiles[:5]),
                                       ("MARQUEE COLORWAYS (base: design 5)",
                                        tiles[5:]))):
        d.text((20, y + 8), sec, font=fnt2, fill=(244, 214, 128))
        y += sec_hdr
        for i, (name, c, close, strip) in enumerate(group):
            x = 20 + i * (TW + 12)
            d.text((x, y + 6), f"{name}   {c:.1f}:1", font=fnt,
                   fill=(230, 230, 230))
            cy = y + 40
            fig.paste(close.resize((TW, close_h), Image.LANCZOS), (x, cy))
            st = strip.resize((TW, strip_h), Image.LANCZOS)
            fig.paste(st, (x, cy + close_h + 6))
            d.rectangle([x - 1, cy - 1, x + TW, cy + close_h + 6 + strip_h],
                        outline=(70, 60, 40))
        y += tile_h
    out = "docs/stall_sign_item/sign_colorways_v1.png"
    fig.save(out)
    print("saved", out, fig.size)


if __name__ == "__main__":
    main()
