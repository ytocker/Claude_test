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


def draw_top_center_banner(surf):
    """Emerald 'clasp' pill pinned to the card's top edge: a short enamel pill
    whose lower third bites over the inner gold bead so it reads as a physical
    fastener gripping the frame.

    Three-step value hierarchy — only 'ON' owns the top value:
      brightest (~luma 238): 'ON' near-white mint fill
      mid       (~luma 160): circular power-dot hardware signal
      absent:               rivets removed; tone-on-tone detail would compete

    Keyline (10,45,25) on 'ON' is a 1-SS-px dark-emerald outline that crisps
    edges at 1× and reads as engraved metal. weight=0 keeps the O counter hole
    open; tracking m(4) gives O and N clear separation at live card size."""
    cx, cy = 162, 26
    W, H = 86, 22
    rad = H // 2
    x0, y0 = cx - W // 2, cy - H // 2
    pr = pygame.Rect(x0, y0, W, H)

    # Enamel body — equipped-green ramp, single smooth gradient.
    body = sc.vgrad_stops(W, H, rad, [(0.0, (18, 32, 24)), (1.0, (12, 22, 16))],
                          255, gamma=1.04)
    # Soft seat shadow so the pill lifts off the frame it clasps.
    sh = pygame.Surface((W + sc.m(6), H + sc.m(6)), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 150), sh.get_rect(), border_radius=rad + sc.m(3))
    surf.blit(sh, (x0 - sc.m(3), y0 - sc.m(2) + sc.m(3)))
    surf.blit(body, pr.topleft)

    # Dark contact keyline UNDER a bright mint bevel — the defined emerald edge.
    pygame.draw.rect(surf, (6, 20, 12), pr, width=max(1, sc.m(1.4)), border_radius=rad)
    sc.bevel_rim(surf, pr, rad, (20, 88, 44, 235), (100, 230, 148, 220),
                 w=max(1, sc.m(1.4)))

    # Circular power-dot: a filled circle sits clearly in hardware territory at
    # mid value (~luma 160) and can never be misread as a letter.  A dark seat
    # ring separates it from the enamel body.
    pip_cx = x0 + sc.m(10)
    pip_r_px = sc.m(3)
    pygame.draw.circle(surf, (8, 24, 14), (pip_cx, cy), pip_r_px + 1)
    pygame.draw.circle(surf, (100, 195, 135), (pip_cx, cy), pip_r_px)

    # 'ON' — near-white mint (~luma 238) is the single brightest element.
    # weight=0 skips the faux-bold stamp so counter holes stay open at 1×.
    # Tracking m(4) separates O and N visually even at 5–6 final px per glyph.
    # Keyline (10,45,25) delivers a 1-SS-px emboss outline that reads engraved.
    f = sc.font(11)
    gap = sc.m(3)   # ≥3 live px between pip right edge and text left edge
    tok_cx = (pip_cx + pip_r_px + gap + pr.right - sc.m(6)) // 2
    sc.plain_text(surf, "ON", f, (tok_cx, cy), (220, 248, 232),
                  shadow_a=0, tracking=sc.m(4), weight=0,
                  keyline=(10, 45, 25), kw=max(1, sc.m(1.0)))


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (regalia frame + check hang-tag, no new indicator)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + banner on top)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_top_center_banner(p2)

# Compose review sheet
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
GOLD = (236, 202, 116); GREY = (150, 152, 168); CREAM_LBL = (250, 246, 232)
xs = [20, 360, 700]
panel_y = PAD + HDR_H + LBL_H  # 102
sheet_w = xs[-1] + PANEL_W + PAD  # 1044

# Bottom: 2× nearest-neighbour zoom and a true 1× inset panel side-by-side,
# centred under the sheet so the value hierarchy and O-counter survival can
# both be judged without hunting between panels.
strip_w, strip_h = sc.CARD_W * 2, sc.CARD_H * 2    # 324×200
inset_w, inset_h = sc.CARD_W, sc.CARD_H              # 162×100
ZPAIR_GAP = 20
zoom_pair_w = strip_w + ZPAIR_GAP + inset_w           # 506
zoom_pair_x0 = (sheet_w - zoom_pair_w) // 2          # centre in sheet

zlbl_y = panel_y + PANEL_H + SGAP
zoom_y  = zlbl_y + SLBL_H
sheet_h = zoom_y + strip_h + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v4 — top-center-banner · round 2 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY), ("+ TOP-CENTER BANNER", CREAM_LBL)]
panels = [p0, p1, p2]
lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)
for x, panel, (label, col) in zip(xs, panels, labels):
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(x + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (x, panel_y))

# Generate both zoom surfaces from the same 1× smoothscale so both panels
# represent the exact same rendering path the live store uses.
card1x = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
strip  = pygame.transform.scale2x(card1x)

zx = zoom_pair_x0
ix = zoom_pair_x0 + strip_w + ZPAIR_GAP
# Vertically centre the shorter 1× inset alongside the 2× strip.
inset_vc_y = zoom_y + (strip_h - inset_h) // 2

zt_2x = zlbl_f.render("2× nearest-nbr", True, GREY)
zt_1x = zlbl_f.render("true 1× (162×100)", True, CREAM_LBL)
sheet.blit(zt_2x, zt_2x.get_rect(midbottom=(zx + strip_w // 2, zoom_y - 4)))
sheet.blit(zt_1x, zt_1x.get_rect(midbottom=(ix + inset_w // 2, zoom_y - 4)))

sheet.blit(strip, (zx, zoom_y))
sheet.blit(card1x, (ix, inset_vc_y))

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
    "docs", "store_equipped_v4", "top_center_banner", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
