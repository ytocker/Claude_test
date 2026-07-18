#!/usr/bin/env python3
"""
equipped-card v3 — inset-plinth concept, round 2 (final).

The equipped card grows a full-width gold display plinth across its base so the
portrait reads as mounted "on display" — a museum mount. Round 2 hardens the
read at the true 162×100 thumbnail:

  * The tread's lit peak is pulled off near-white so it keeps its gold CHROMA
    after the Lanczos downscale even when a cream/ivory item (skin_mummy) sits
    above it — value drops, saturation holds, so it never resolves as white.
  * A separate cast contact-shadow is smeared under the portrait BASE (tracking
    the item, not the fixed ledge) so every skin reads as seated, not floating.
  * The riser is thicker and its base deepened toward saturated bronze so the
    shadowed face stays chromatic and does not merge into the bottom bevel at 1×.
  * The AO seam where the body meets the tread is thickened + darkened so a hint
    of the shelf edge survives at 1× — separating "3D plinth" from "painted band".

Drawn LAST over an equipped card whose green chip is suppressed, so the plinth is
the sole state signal. The plinth is corner-masked to the card body's radius.
"""
import os
import sys

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

SID = "skin_mummy"                                       # cream/ivory worst case
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324×200
ri = sc.m(sc._INSET)                                      # 8
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
rad = sc.m(sc.CARD_RAD)                                   # body corner radius (34)


# ── Panel 0 — UNEQUIPPED (price tag visible) ─────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)


# ── Panel 1 — STOCK EQUIPPED (green chip, reference) ─────────────────────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False)


# ── Panel 2 — CONCEPT EQUIPPED (chip suppressed, inset plinth) ───────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None          # suppress the green EQUIPPED chip
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()


def _vband(surf, x0, x1, y0, y1, top, bot):
    """A vertical gradient band filled row by row — the tread/riser faces. Kept
    local (no rounded corners) because the whole plinth is masked to the card
    body afterward, so the band can be authored as a plain rectangle."""
    h = max(1, y1 - y0)
    for y in range(y0, y1):
        t = (y - y0) / h
        c = sc.lerp_color(top, bot, t)
        pygame.draw.line(surf, c, (x0, y), (x1 - 1, y))


def _card_mask():
    """A white rounded-rect matching the card body — used with BLEND_RGBA_MIN to
    clip an overlay so its lower corners follow the body's corner radius."""
    mask = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), rect, border_radius=rad)
    return mask


# Portrait base in device px — the dome bottom, where the item art visually ends.
# The cast shadow is anchored here (not to the ledge) so tall/small items alike
# read as seated rather than hovering over the plinth.
ITEM_BASE_X = rect.centerx                                # 162
ITEM_BASE_Y = (rect.y + sc.m(sc.CY_DISC) + sc._DOME_DY) + sc._DOME_R - 8


def draw_item_contact_shadow(surf):
    """A soft warm-dark smear directly under the portrait so every skin grounds
    onto the display. Built from concentric ellipses (faint+wide → dark+tight)
    for a blurred edge, then corner-masked so it can never spill past the body."""
    cast = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    # (half-width, half-height, alpha) — outer rings are large + faint, the core
    # is small + dark so the contact point reads as the item's weight.
    for hw, hh, a in ((40, 11, 26), (32, 9, 42), (24, 7, 62), (15, 5, 86)):
        r = pygame.Rect(ITEM_BASE_X - hw, ITEM_BASE_Y - hh, hw * 2, hh * 2)
        pygame.draw.ellipse(cast, (40, 20, 5, a), r)
    cast.blit(_card_mask(), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(cast, (0, 0))


def draw_inset_plinth(surf):
    """The full-width gold display plinth: an AO seam where the body rests on the
    ledge, a sunlit TREAD, a step-shadow, a taller shadowed RISER whose base is
    deep saturated bronze, and lit/keyline edges. Corner-masked to the body."""
    LX0, LX1 = 14, 310                     # near-full width, inside the bevel

    plinth = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)

    # (1) Contact AO seam above the ledge — ~4px, deepening toward the tread so a
    # hint of the shelf edge survives the 1× downscale (reads as a real step, not
    # a painted band). Darkest row sits right on the tread's top edge.
    for i, y in enumerate(range(162, 166)):
        a = int(40 + 110 * (i / 3))                       # 40 → 150, deepest at ledge
        pygame.draw.line(plinth, (40, 25, 5, a), (LX0, y), (LX1 - 1, y))

    # (2) Top TREAD — sunlit horizontal nosing. Lit peak pulled OFF near-white to
    # ~(245,205,120): value down, gold saturation held, so after Lanczos-blend
    # with a cream item above it still resolves as distinctly GOLD, never white.
    _vband(plinth, LX0, LX1, 166, 176, (245, 205, 120), (228, 186, 102))

    # (3) Nosing cap — the very top lit lip. Warm gold rather than white so it
    # reinforces (not erodes) the tread's chroma at thumbnail scale.
    pygame.draw.line(plinth, (248, 222, 150), (LX0, 166), (LX1 - 1, 166), 1)

    # (4) Step-shadow seam — front edge of the tread meeting the riser.
    pygame.draw.line(plinth, (120, 74, 20), (LX0, 176), (LX1 - 1, 176), 2)

    # (5) RISER — the shadowed vertical front face, now taller (14px) with a deep
    # saturated-bronze base so the shaded face stays chromatic and separates from
    # the card's bright bottom bevel at 1× instead of merging into it.
    _vband(plinth, LX0, LX1, 177, 191, (194, 148, 66), (140, 90, 28))

    # (6) Contact keyline — the crisp seam where the plinth meets the indigo body.
    pygame.draw.line(plinth, (48, 30, 6), (LX0, 165), (LX1 - 1, 165), 1)

    # (7) Mask lower corners to the card body so the ledge follows its radius.
    plinth.blit(_card_mask(), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(plinth, (0, 0))

    # (8) Warm glow rising off the tread — masked to the body so it never spills
    # past the card edge.
    glow = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    g = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.circle(g, (246, 200, 116, 38), (60, 60), 54)
    glow.blit(g, (162 - 60, 168 - 60))
    glow.blit(_card_mask(), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(glow, (0, 0))


draw_item_contact_shadow(p2)
draw_inset_plinth(p2)


# ── Compose the review sheet ─────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
ONE_W, ONE_H = sc.CARD_W, sc.CARD_H          # 162×100 — true 1× card size
ZOOM_W, ZOOM_H = ONE_W * 2, ONE_H * 2        # nearest-neighbour blow-up of 1×

GOLD = (236, 202, 116)
GREY = (150, 152, 168)
CREAM_LBL = (250, 246, 232)

N = 3
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
# rows: header · panels · 1× zoom strip · state-change comparison strip
sheet_h = (PAD + HDR_H + LBL_H + PANEL_H
           + SGAP + SLBL_H + ZOOM_H
           + SGAP + SLBL_H + ZOOM_H + PAD)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v3 — inset-plinth · skin_mummy · round 2", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("STOCK EQUIPPED", GREY),
          ("INSET PLINTH", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)
panel_y = PAD + HDR_H + LBL_H          # = 102
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

    # 1× read: downscale to the true card size, then blow it back up nearest-
    # neighbour so the sheet shows exactly how the plinth resolves at 1×.
    card1x = pygame.transform.smoothscale(panel, (ONE_W, ONE_H))
    zoom = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
    zt = zlbl_f.render("@1× (rendered then 2× nearest)", True, GREY)
    sheet.blit(zt, zt.get_rect(midbottom=(px + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
    sheet.blit(zoom, (px + (PANEL_W - ZOOM_W) // 2, zoom_y))

# ── State-change verification strip — UNEQUIPPED vs INSET PLINTH at true 1× ───
# Confirms the plinth is a distinct STATE cue below the bevel, not default chrome.
cmp_lbl_y = zoom_y + ZOOM_H + SGAP
cmp_y = cmp_lbl_y + SLBL_H
ct = zlbl_f.render("state-change check — same card @1× (×2): price tag  vs  plinth",
                   True, CREAM_LBL)
sheet.blit(ct, ct.get_rect(midtop=(sheet_w // 2, cmp_lbl_y)))

pair = [(p0, "UNEQUIPPED"), (p2, "EQUIPPED")]
pair_gap = 40
pair_w = 2 * ZOOM_W + pair_gap
pair_x0 = (sheet_w - pair_w) // 2
for j, (panel, lab) in enumerate(pair):
    px = pair_x0 + j * (ZOOM_W + pair_gap)
    card1x = pygame.transform.smoothscale(panel, (ONE_W, ONE_H))
    zoom = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
    sheet.blit(zoom, (px, cmp_y))
    lt = zlbl_f.render(lab, True, GREY)
    sheet.blit(lt, lt.get_rect(midtop=(px + ZOOM_W // 2, cmp_y + ZOOM_H + 2)))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3", "inset_plinth", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
