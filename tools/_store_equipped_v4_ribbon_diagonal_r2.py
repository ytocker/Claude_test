#!/usr/bin/env python3
import os, sys, math
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
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
RAD = sc.m(sc.CARD_RAD)

# Palette hierarchy: the BAND FACE is the dominant, brightest element — a rich
# mint-emerald ramp. Under-fold and crease are the true shadow family, purely
# value-driven so depth reads in grayscale (colorblind-safe by construction).
BAND_LIT    = (100, 230, 148)   # outer lit diagonal — the hero colour, max sat
BAND_SHADOW = (24,   88,  52)   # inner shadow edge (toward the fold crease)
UNDERFOLD   = (6,   14,  10)    # reverse-fold face — TRUE shadow, darker than indigo body
CREASE      = (3,    8,   5)    # 1px darkest line at the fold (luma ≈6), value jump
MINT_SPECULAR = (200, 255, 220) # demoted to 1px lit outer edge ONLY (not a fat bevel)
PIP_RIM     = (8,   28,  16)    # outer dark emerald ring of enamel gem
PIP_FILL    = (220, 248, 220)   # cream dot centre — high contrast against dark band area


def draw_ribbon_diagonal(surf):
    """A folded corner SASH across the lower-left apex — read as fabric/enamel
    at phone scale. The emerald face is the dominant element; the dark fold
    crease + under-fold sell the physical turn purely through value contrast
    so the indicator reads in grayscale (colorblind-safe). The sash apex is
    pushed 2 logical px inboard from the raw corner tangent so the band
    emerges cleanly from the card body, on top of the gold frame beads, with
    an unambiguous front-to-back z relationship."""

    # 2 lx inboard so the sash sits clearly on the card body face rather than
    # disappearing into the dark rounded-corner void behind the gold beads.
    C   = (ri + sc.m(2), PANEL_H - ri - sc.m(2))

    # Band ~50% wider than r1: outer span o1, inner span o2 along each edge.
    # Perpendicular band width = (o2-o1)/sqrt(2) ≈ 21px at 1x live (≈14px was target).
    o1  = sc.m(16)   # outer endpoints — where band emerges from corner
    o2  = sc.m(46)   # inner endpoints — where band tucks under (fold crease)

    L_out = (C[0],        C[1] - o1)   # left-edge outer
    B_out = (C[0] + o1,   C[1])        # bottom-edge outer
    L_in  = (C[0],        C[1] - o2)   # left-edge inner (crease end)
    B_in  = (C[0] + o2,   C[1])        # bottom-edge inner (crease end)
    face  = [L_out, B_out, B_in, L_in]

    layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)

    # ── 1) Under-fold flaps ────────────────────────────────────────────────────
    # True shadow (6,14,10): clearly darker than the indigo body (12–28 range)
    # so the value jump at the crease reads without needing hue cues.
    flap = sc.m(11)
    pygame.draw.polygon(layer, UNDERFOLD,
                        [B_in, (B_in[0] + flap, B_in[1]),
                         (B_in[0], B_in[1] - flap)])
    pygame.draw.polygon(layer, UNDERFOLD,
                        [L_in, (L_in[0], L_in[1] - flap),
                         (L_in[0] + flap, L_in[1])])

    # ── 2) AO shadow: fold onto card body ─────────────────────────────────────
    # A 3-step graduated dark bloom on the card-body side of the crease line,
    # offset by (+k/√2, −k/√2) (toward card interior = upper-right). This is
    # the ambient-occlusion darkening the paper body receives from the raised fold.
    ao_surf = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    steps = max(1, sc.m(3))
    for k in range(1, steps + 1):
        a = int(80 * ((steps - k + 1) / steps) ** 1.5)
        ox, oy = k * 0.707, -k * 0.707
        pygame.draw.line(ao_surf, (0, 0, 0, a),
                         (int(L_in[0] + ox), int(L_in[1] + oy)),
                         (int(B_in[0] + ox), int(B_in[1] + oy)),
                         max(1, sc.m(1)))
    layer.blit(ao_surf, (0, 0))

    # ── 3) Band face — bright emerald ramp, dominant + saturated ──────────────
    # Lit outer edge (100,230,148) → darker inner edge toward crease.
    # This is the widest, most vivid element — band hierarchy is now correct.
    band = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    c_out = L_out[0] - L_out[1]
    c_in  = L_in[0]  - L_in[1]
    span  = max(1, c_in - c_out)
    for c in range(int(c_out), int(c_in) + 1):
        t   = (c - c_out) / span
        col = sc.lerp_color(BAND_LIT, BAND_SHADOW, t)
        pygame.draw.line(band, col, (0, -c), (PANEL_W, PANEL_W - c), 2)
    qmask = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.polygon(qmask, (255, 255, 255, 255), face)
    band.blit(qmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    layer.blit(band, (0, 0))

    # ── 4) Hard fold crease — darkest-emerald 1px line ────────────────────────
    # Luma ≈ 6: the single hardest value in the indicator, landing between
    # the lit band face and the deep under-fold. Sells the turn in grayscale.
    pygame.draw.line(layer, CREASE,
                     (int(L_in[0]), int(L_in[1])),
                     (int(B_in[0]), int(B_in[1])),
                     max(1, sc.m(0.6)))

    # ── 5) Outer lit edge — demoted to 1px specular ONLY ─────────────────────
    # The mint highlight is now a single crisp pixel along the outer diagonal;
    # it reads as light catching the raised enamel edge, not a fat competing band.
    pygame.draw.line(layer, MINT_SPECULAR,
                     (int(L_out[0]), int(L_out[1])),
                     (int(B_out[0]), int(B_out[1])),
                     max(1, sc.m(0.7)))

    # ── 6) Cast shadow of sash onto card body ─────────────────────────────────
    # A 2-step dark bloom along the outer diagonal offset toward the corner
    # (−k/√2, +k/√2), showing the sash elevated above the card surface —
    # the z-order read that says "this band is sitting ON the card, not behind it."
    cs_surf = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    cs_steps = max(1, sc.m(2))
    for k in range(1, cs_steps + 1):
        a_cs = int(60 * ((cs_steps - k + 1) / cs_steps) ** 1.6)
        ox2, oy2 = -k * 0.707, k * 0.707
        pygame.draw.line(cs_surf, (0, 0, 0, a_cs),
                         (int(L_out[0] + ox2), int(L_out[1] + oy2)),
                         (int(B_out[0] + ox2), int(B_out[1] + oy2)),
                         max(1, sc.m(1)))
    layer.blit(cs_surf, (0, 0))

    # ── 7) Pip — round enamel gem (replaces 5-point star) ─────────────────────
    # A small disc: dark emerald ring, cream fill. 3–4px at 1x live.
    # High contrast reads against both the bright and shadowed portions of the band.
    # Centroid of the face quad, shifted one step toward the lit outer edge.
    ctr_x = sum(p[0] for p in face) / 4 - sc.m(1)
    ctr_y = sum(p[1] for p in face) / 4 - sc.m(1)
    pip_outer = sc.m(3.5)
    pip_inner = sc.m(2.0)
    pip_spec  = max(1, sc.m(0.8))
    pygame.draw.circle(layer, PIP_RIM, (int(ctr_x), int(ctr_y)), pip_outer)
    pygame.draw.circle(layer, PIP_FILL, (int(ctr_x), int(ctr_y)), pip_inner)
    # tiny top-left specular pip on the cream face
    sx = int(ctr_x - pip_inner * 0.4)
    sy = int(ctr_y - pip_inner * 0.4)
    pygame.draw.circle(layer, (255, 255, 255), (sx, sy), pip_spec)

    # ── 8) Clip to card body rounded rect ─────────────────────────────────────
    clip = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.rect(clip, (255, 255, 255, 255), rect, border_radius=RAD)
    layer.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(layer, (0, 0))


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (regalia frame + check hang-tag, no new indicator)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + ribbon on top)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_ribbon_diagonal(p2)

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
tt = title_f.render("equipped v4 — ribbon-diagonal · round 2 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))
labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY), ("+ RIBBON DIAGONAL", CREAM_LBL)]
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
    "docs", "store_equipped_v4", "ribbon_diagonal", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
