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


def draw_lit_frame_filament(surf, body):
    """No added badge or text — the equipped state is signalled by igniting the
    regalia frame's innermost KEY bead into a hot warm-amber filament. The wire
    is a saturated amber hue distinct from the pale regalia cream, so it reads as
    an electrified keyline rather than 'the same cream, brighter'. Its glow spills
    only INBOARD (toward the card face) so the crisp outer beads stay intact, and
    four seated corner nodes read as deliberate beads where the wire concentrates."""
    key_rect = body.inflate(-26, -26)  # Rect(21,21,282,162) — the KEY bead ring
    rad = sc.m(sc.CARD_RAD) - 13       # 21

    # INBOARD-ONLY warmth: concentric amber strokes stepping toward the card
    # centre. Additive + capped low alpha keeps it a directional aura on the
    # interior side of the wire — it never blooms outward past the outer bead.
    halo = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    for i, inset in enumerate(range(4, 15, 2)):  # 4,6,8,10,12,14
        a = max(0, 40 - i * 7)                   # ≤40, fading toward centre
        hr = key_rect.inflate(-inset, -inset)
        hrad = max(1, rad - inset // 2)
        pygame.draw.rect(halo, (240, 180, 80, a), hr, width=2, border_radius=hrad)
    surf.blit(halo, (0, 0), special_flags=pygame.BLEND_ADD)

    # Filament body — saturated WARM amber, a clearly different hue from the pale
    # regalia cream so the lit wire never masquerades as brighter cream.
    pygame.draw.rect(surf, (230, 170, 60), key_rect, width=2,
                     border_radius=max(1, rad))
    # Warm-lemon inner edge (lighter than the amber body) gives the wire a hot
    # core and a warm falloff toward centre.
    inner_r = key_rect.inflate(-2, -2)
    pygame.draw.rect(surf, (255, 240, 160), inner_r, width=1,
                     border_radius=max(1, rad - 1))

    # Corner nodes — a dark seat ring first makes each read as a deliberate,
    # struck bead where the filament pools its energy; the cream fill sits in it.
    off = max(1, sc.m(3))
    corners = [
        (key_rect.left + off, key_rect.top + off),
        (key_rect.right - off, key_rect.top + off),
        (key_rect.left + off, key_rect.bottom - off),
        (key_rect.right - off, key_rect.bottom - off),
    ]
    for cx, cy in corners:
        pygame.draw.circle(surf, (46, 38, 18), (cx, cy), 5, width=1)
        pygame.draw.circle(surf, (255, 248, 224), (cx, cy), 4)


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (regalia frame + check hang-tag, no new indicator)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT. The frame lives physically BEHIND the hanging tag, so the
# lit filament must be occluded by it: suppress the tag during draw_card, ignite
# the frame, then re-stamp the check hang-tag ON TOP so it reads as hung in front.
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
sc.state_chip = orig_chip
draw_lit_frame_filament(p2, rect)
# Re-draw the hang-tag with the exact same slot draw_card uses, on top of the wire.
tag_cx = rect.centerx
tag_cy = rect.y + sc.m(88) - sc._CHIP_DY
sc.state_chip(p2, SID, tag_cx, tag_cy, True, False, sc.m(20), owned=False)

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
tt = title_f.render("equipped v4b — lit-frame-filament · round 2 · skin_mummy", True, GOLD)
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
    "docs", "store_equipped_v4b", "lit_frame_filament", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
