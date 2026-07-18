#!/usr/bin/env python3
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pygame
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
    """Warm ambient bloom radiating inward from the card's cream inner-bead
    keyline, so the equipped frame reads as internally lit — steady and
    constant, never a hover pulse. A single compact cream pip seated on the top
    inner bead is the 'power source' node feeding that glow. Gold/cream only;
    the bloom is masked to the card body so it never spills past the frame."""
    rad = sc.m(sc.CARD_RAD)

    # Soft interior bloom: thick gold strokes hugging the cream inner bead, then
    # a heavy down/up-scale blur bleeds that light INWARD — a steady falloff that
    # is hottest at the keyline and fades toward the card centre. Premultiplied
    # down (BLEND_RGB_ADD adds RGB at full strength regardless of surface alpha)
    # so it lifts the obsidian body to a warm amber instead of blowing it out.
    bloom = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for inset, w, col in ((10, sc.m(9), (248, 220, 140)),
                          (18, sc.m(8), (236, 202, 116))):
        r = body.inflate(-2 * inset, -2 * inset)
        pygame.draw.rect(bloom, (*col, 255), r, width=w,
                         border_radius=max(1, rad - inset))
    # cheap Gaussian: collapse to a fifth and smooth back for a wide soft bleed.
    small = pygame.transform.smoothscale(bloom, (surf.get_width() // 5,
                                                 surf.get_height() // 5))
    bloom = pygame.transform.smoothscale(small, surf.get_size())
    # dim to a gentle additive lift so the interior warms, never washes to white.
    bloom.fill((60, 60, 60, 255), special_flags=pygame.BLEND_RGB_MULT)
    # clip the blurred bleed to the card body so light stays inside the frame.
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), body, border_radius=rad)
    bloom.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(bloom, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # Cream pip on the top inner bead — a warm lit bulb, the glow's source node.
    cx, cy = 162, 20
    # dark seat, slightly elliptical so the bulb reads as inset into the frame.
    pygame.draw.ellipse(surf, (9, 9, 22),
                        pygame.Rect(cx - 9, cy - 7, 18, 14))
    # cream-gold bead body.
    pygame.draw.circle(surf, (248, 238, 210), (cx, cy), 6)
    # hot specular top-left — brightest allowed cream, ADD-blit so it truly pops.
    spec = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(spec, (255, 240, 190, 230), (cx - 1, cy - 1), 2)
    surf.blit(spec, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (regalia frame + check hang-tag, no new indicator)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + warm glow pip on top)
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
tt = title_f.render("equipped v4b — warm-glow-pip-gold · round 1 · skin_mummy", True, GOLD)
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
    "docs", "store_equipped_v4b", "warm_glow_pip_gold", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
