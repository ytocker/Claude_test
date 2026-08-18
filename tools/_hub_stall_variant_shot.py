"""Render a stall-front variant (sign + item presentation) for the design loop.

Usage: python _hub_stall_variant_shot.py <variant_module|-> <out.png>

<variant_module> is a module under tools/ (e.g. "stall_variant_lantern") that
exposes install() -> sets game.store_hub.STALL_SIGN_HOOK / STALL_ITEM_HOOK.
Pass "-" to render the stock in-game stall (the BEFORE baseline).

Output figure: LEFT = the full 360x640 landing (in-context read), RIGHT = a
supersampled close-up of the PARCELS hero stall (detail read). Fresh process
per run — the lagoon base is module-cached.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

VARIANT, OUT = sys.argv[1], sys.argv[2]

import pygame
pygame.init()
pygame.display.set_mode((8, 8))

import game.store_hub as sh

if VARIANT != "-":
    import importlib
    importlib.import_module(f"tools.{VARIANT}").install()

big = sh._render_static_device()

from game.config import W, H
full = pygame.transform.smoothscale(big, (W, H))

m = sh.m
DW, DH = sh.DW, sh.DH
cx, deck_y = int(DW * 0.5), int(DH * 0.862)
crop = pygame.Rect(cx - m(95), deck_y - m(135), m(190), m(170))
crop = crop.clip(big.get_rect())
close = big.subsurface(crop).copy()

GAP, MARG = 16, 16
ch = full.get_height()
cw = int(close.get_width() * ch / close.get_height())
close = pygame.transform.smoothscale(close, (cw, ch))
out = pygame.Surface((MARG * 2 + full.get_width() + GAP + cw, ch + MARG * 2))
out.fill((10, 9, 20))
out.blit(full, (MARG, MARG))
out.blit(close, (MARG + full.get_width() + GAP, MARG))
pygame.image.save(out, OUT)
print(f"saved {OUT} {out.get_size()}")
