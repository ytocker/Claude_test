"""Final comparison figure for the SHOES roster expansion (5 new shoes).

These are 5 NEW shoes spanning the rarity ladder, not variants of one item, so
there is no single 'original' to anchor against. The figure instead shows the
current top shoe (RETRO 1) as a reference ceiling on the left, then the five new
designs in ascending price / escalating wildness. Each column is TWO rows: the
store product-shot icon (the sneaker itself) on top, and Pip wearing it
mid-flight over a real gameplay biome below. The tier is colour-coded to match
the store card rarity outline so the rare->legendary climb reads at a glance.

Pure capture; touches no production art (the five candidates are scratch
builders under tools/shoe_candidates/, RETRO 1 is the live game/shoe_retro1).

Run headless from repo root:
  SDL_VIDEODRIVER=dummy python tools/render_shoes_compare.py
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import importlib
import pygame
pygame.init()

from game import shoe_skins, shoe_retro1
from game.store_skins import _make_skin
from game.hud import _font, _GOLD_PALE
import tools.ninja_render as nr

# Tier outline colours mirror store_cards.RARITY so the ladder reads as the store
# will draw it (rare->blue, epic->purple, legendary->orange).
TIER_COL = {
    "common":    (180, 174, 214),
    "rare":      (108, 188, 252),
    "epic":      (194, 122, 248),
    "legendary": (255, 184, 72),
}


def rarity_for(cost):
    for ceiling, tier in ((400, "common"), (800, "rare"), (2500, "epic")):
        if cost < ceiling:
            return tier
    return "legendary"


# (tag, name, cost, source). Source "retro1" = live builder, else design module.
COLUMNS = [
    ("CURRENT CEILING", "RETRO 1",      850, "retro1"),
    ("DESIGN 1",        "MEGA DAD",     780, "design_1"),
    ("DESIGN 2",        "JELLYCORE",   1200, "design_2"),
    ("DESIGN 3",        "NEON CIRCUIT", 1800, "design_3"),
    ("DESIGN 4",        "WING BOOTS",  3200, "design_4"),
    ("DESIGN 5",        "AFTERBURNER", 4800, "design_5"),
]


def _draw_shoe(spec):
    if spec == "retro1":
        return shoe_retro1.draw_shoe
    return importlib.import_module(f"tools.shoe_candidates.{spec}").draw_shoe


def _icon_panel(draw_shoe, w, h, bg=(26, 24, 36)):
    """The store product-shot (the sneaker itself), cropped to content and fit
    onto a rounded dark card — the same _build_icon the store card uses."""
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(panel, bg, panel.get_rect(), border_radius=12)
    icon = shoe_skins._build_icon(draw_shoe)
    bb = icon.get_bounding_rect()
    if bb.width and bb.height:
        icon = icon.subsurface(bb).copy()
    sw, sh = icon.get_size()
    scale = min((w * 0.86) / sw, (h * 0.86) / sh)
    icon = pygame.transform.smoothscale(
        icon, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    panel.blit(icon, icon.get_rect(center=(w // 2, h // 2)))
    return panel


COL_W = 224
ICON_H = 132
GAME_W, GAME_H = 190, 300
PAD, GUTTER = 28, 16
TITLE_H = 80
CAP_H = 66
n = len(COLUMNS)
GAME_X_OFF = (COL_W - GAME_W) // 2

sheet_w = PAD * 2 + n * COL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + ICON_H + 14 + GAME_H + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(30, True).render(
    "SHOES — ROSTER EXPANSION: 5 NEW SHOES ACROSS THE RARITY LADDER",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 20)))
sub = _font(15, False).render(
    "current ceiling (RETRO 1) + five new designs, wilder as the tier climbs"
    "   —   product shot (top) and in-gameplay (bottom)",
    True, (170, 162, 190))
sheet.blit(sub, sub.get_rect(midtop=(sheet_w // 2, 54)))

name_font = _font(18, True)
tag_font = _font(12, True)
cost_font = _font(15, True)

for i, (tag, name, cost, spec) in enumerate(COLUMNS):
    x = PAD + i * (COL_W + GUTTER)
    y = TITLE_H
    ds = _draw_shoe(spec)
    tier = rarity_for(cost)
    tcol = TIER_COL[tier]
    is_ref = (spec == "retro1")

    sheet.blit(_icon_panel(ds, COL_W, ICON_H), (x, y))

    gy = y + ICON_H + 14
    panel = nr.gameplay_panel(_make_skin(shoe_skins._foot_paint(ds)), GAME_W, GAME_H)
    gx = x + GAME_X_OFF
    border = (150, 142, 168) if is_ref else tcol
    pygame.draw.rect(sheet, border,
                     pygame.Rect(gx - 2, gy - 2, GAME_W + 4, GAME_H + 4), width=2)
    sheet.blit(panel, (gx, gy))

    cy = gy + GAME_H + 8
    sheet.blit(tag_font.render(tag, True, (150, 142, 168) if is_ref
                               else (170, 162, 190)), (x + 4, cy))
    sheet.blit(name_font.render(name, True, (200, 196, 210) if is_ref
                                else _GOLD_PALE), (x + 4, cy + 16))
    sheet.blit(cost_font.render(f"{cost}  -  {tier.upper()}", True, tcol),
               (x + 4, cy + 38))

out = os.path.join("docs", "store_redesign", "shoes", "final_comparison.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
