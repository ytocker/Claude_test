#!/usr/bin/env python3
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pygame
import pygame.surfarray as surfarray
import numpy as np
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()
SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS  # 324×200
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2*ri, PANEL_H - 2*ri)


def draw_warm_glow_pip_gold(surf, body):
    """Warm ambient light seated in the equipped frame track — the inboard ring
    just off the cream keyline reads as internally lit, steady and constant,
    never a hover pulse. The glow is confined to that ~20px frame track and never
    fills the card body, so it can't duplicate the store's tier shelf-light bar.
    Gold/cream only. The tier gem badge is masked out so the wash never touches
    it, and premultiplied alpha keeps each stroke a gentle additive lift rather
    than a white blow-out of the cream inner bead."""
    rad = sc.m(sc.CARD_RAD)

    # Concentric rect rings that sit just INBOARD of the cream keyline: the frame's
    # cream inner bead lives at the ~y18-20 band, so the outermost stroke starts a
    # few px further in (body.inflate(-28,-28)) and fades inward to inflate(-40,-40).
    # This keeps the wash strictly in the inner frame track — never on the cream
    # bead (an add there clips it to pure white) and never in the body interior
    # where the tier shelf-light bar already glows.
    bloom = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for inset, w, col in ((28, 4, (248, 220, 140, 150)),
                          (34, 3, (236, 202, 116, 110)),
                          (40, 2, (220, 180,  80,  70))):
        r = body.inflate(-inset, -inset)
        pygame.draw.rect(bloom, col, r, width=w,
                         border_radius=max(1, rad - inset // 2))
    # Premultiply so each stroke's alpha attenuates its additive contribution —
    # a 150-alpha stroke lifts ~59% of its RGB, a 70-alpha one barely warms.
    bloom = bloom.premul_alpha()

    # Gate the additive wash to the frame track's DARK grooves only: wherever the
    # base frame is already bright (the cream inner bead, the gold band, the gold
    # accent line, the white equipped check-tag, the faceted gem) an add would clip
    # to pure white, so zero the bloom there. This confines the warm lift to the
    # dark inset channels — the frame reads internally lit without ever blowing a
    # cream/gold element to white.
    base = surfarray.array3d(surf).astype(np.int16)   # copy — leaves surf unlocked
    dark = base.max(axis=2) < 130           # max-channel keeps the grooves, drops beads
    bl = surfarray.pixels3d(bloom)
    bl[~dark] = 0
    del bl

    # Belt-and-braces: fully exclude the tier gem badge box (~x250-310, y20-80 at
    # SS=2) so no dark facet inside it catches the wash.
    pygame.draw.rect(bloom, (0, 0, 0, 0), pygame.Rect(250, 20, 60, 60))

    surf.blit(bloom, (0, 0), special_flags=pygame.BLEND_ADD)


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (regalia frame + check hang-tag, no new indicator)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + frame-track warm glow, no pip)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_warm_glow_pip_gold(p2, rect)

# Compose review sheet
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
GOLD = (236, 202, 116); GREY = (150, 152, 168); CREAM_LBL = (250, 246, 232)
xs = [20, 360, 700]
panel_y = PAD + HDR_H + LBL_H  # 102
sheet_w = xs[-1] + PANEL_W + PAD
strip_w, strip_h = sc.CARD_W * 2, sc.CARD_H * 2
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H
sheet_h = zoom_y + strip_h + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)
title_f = hud_font(22, True)
tt = title_f.render("equipped v4b — warm-glow-pip-gold · round 2 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))
labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY), ("+ WARM GLOW PIP GOLD", CREAM_LBL)]
panels = [p0, p1, p2]
lbl_f = hud_font(15, True); zlbl_f = hud_font(13, True)
for x, panel, (label, col) in zip(xs, panels, labels):
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(x + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (x, panel_y))
card1x = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
strip = pygame.transform.scale2x(card1x)
zx = xs[-1] + (PANEL_W - strip_w) // 2
zt = zlbl_f.render("@1x (162x100 tile, 2x nearest)", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(xs[-1] + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
sheet.blit(strip, (zx, zoom_y))
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
    "docs", "store_equipped_v4b", "warm_glow_pip_gold", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
