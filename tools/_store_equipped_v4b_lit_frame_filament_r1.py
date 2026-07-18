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


def draw_lit_frame_filament(surf):
    """No added badge or text — the equipped state is signalled by igniting the
    regalia frame's innermost KEY bead into a hot cream→amber filament, with
    four brighter corner nodes where the 'wire' concentrates energy. Reads as an
    electrified keyline rather than a diffuse glow, so the card face stays clean
    and the frame itself carries the meaning."""
    body = rect  # Rect(8,8,308,184) at SS=2
    key_rect = body.inflate(-26, -26)  # Rect(21,21,282,162) — the KEY bead ring
    rad = sc.m(sc.CARD_RAD) - 13

    # Outer soft warmth halo FIRST so the crisp core strokes sit on top of it —
    # additive + wide + low alpha keeps it a faint aura, never a diffuse bloom.
    halo = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.rect(halo, (248, 220, 140, 60), key_rect.inflate(6, 6),
                     width=6, border_radius=max(1, rad + 3))
    surf.blit(halo, (0, 0), special_flags=pygame.BLEND_ADD)

    # Filament core — crisp saturated cream wire on the KEY bead position.
    pygame.draw.rect(surf, (255, 240, 190), key_rect, width=2,
                     border_radius=max(1, rad))
    # Amber inner edge gives the wire depth and a warm falloff toward centre.
    inner_r = key_rect.inflate(-2, -2)
    pygame.draw.rect(surf, (236, 202, 116), inner_r, width=1,
                     border_radius=max(1, rad - 1))

    # Corner nodes — brighter cream glints where the filament pools its energy;
    # inset from the true corner so they sit ON the rounded arc, not off it.
    nd = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    off = max(1, sc.m(3))
    corners = [
        (key_rect.left + off, key_rect.top + off),
        (key_rect.right - off, key_rect.top + off),
        (key_rect.left + off, key_rect.bottom - off),
        (key_rect.right - off, key_rect.bottom - off),
    ]
    for cx, cy in corners:
        pygame.draw.circle(nd, (255, 248, 224, 220), (cx, cy), 4)
        pygame.draw.circle(nd, (255, 255, 250, 255), (cx - 1, cy - 1),
                           max(1, sc.m(0.8)))
    surf.blit(nd, (0, 0))


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (regalia frame + check hang-tag, no new indicator)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + lit filament on top)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_lit_frame_filament(p2)

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
tt = title_f.render("equipped v4b — lit-frame-filament · round 1 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))
labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY), ("+ LIT FRAME FILAMENT", CREAM_LBL)]
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
    "docs", "store_equipped_v4b", "lit_frame_filament", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
