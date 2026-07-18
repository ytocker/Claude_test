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

m = sc.m
lerp = sc.lerp_color
NEAR_BLACK = sc.NEAR_BLACK


def _wax_polygon(cx, cy, r, n=26, jitter=0.10, seed=7):
    """Organic pressed-wax rim: a near-circle whose radius wobbles per vertex so
    the seal reads as molten wax stamped by hand, never a machined disc. The
    wobble is a fixed sum-of-sines so the silhouette is deterministic (cards are
    cached; a stochastic edge would flicker on rebuild)."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        w = (math.sin(a * 3 + seed) * 0.55
             + math.sin(a * 5 - seed * 2) * 0.30
             + math.sin(a * 7 + seed) * 0.15)
        rr = r * (1.0 + jitter * w)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def draw_wax_seal_medallion(surf):
    """A sculpted gold wax seal pressed into the top inner bead: a domed,
    hand-pressed wax disc (irregular rim, top-left specular, bottom-right contact
    shadow) carrying a recessed intaglio star with a mint lit lip. Reads as a
    physical stamp applied to the frame — categorically not the flat ✓ hang-tag."""
    cx, cy = 162, 20
    r = m(9)                     # ≈18 device px
    pad = m(8)
    S = r * 2 + pad * 2
    c = r + pad                  # seal-local centre
    seal = pygame.Surface((S, S), pygame.SRCALPHA)

    rim = _wax_polygon(c, c, r)

    # ── domed gold body: radial fill along the ONE gold ramp, lit centre biased
    # up-left so the wax bulges toward the top-left light; clipped to the wax rim.
    body = pygame.Surface((S, S), pygame.SRCALPHA)
    lx, ly = c - r * 0.24, c - r * 0.24      # dome apex, up-left
    for i in range(r + 2, 0, -1):
        t = (i / (r + 2)) ** 0.92            # 0 apex → 1 rim
        col = sc.lerp_stops(sc.GOLD_A_STOPS, t)
        pygame.draw.circle(body, (*col, 255), (int(lx), int(ly)), i)
    mask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), rim)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    seal.blit(body, (0, 0))

    # ── bottom-right contact shadow: the far wax rim rolls into shade, selling
    # the dome as raised metal rather than a printed coin.
    ao = pygame.Surface((S, S), pygame.SRCALPHA)
    for k in range(m(4)):
        a = int(120 * (1 - k / m(4)))
        pygame.draw.arc(ao, (44, 24, 4, a),
                        (c - r + k, c - r + k, (r - k) * 2, (r - k) * 2),
                        math.radians(292), math.radians(18), max(1, m(1.4)))
    ao.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    seal.blit(ao, (0, 0))

    # ── top-left specular: a soft bright bloom where the dome catches the light.
    spec = pygame.Surface((S, S), pygame.SRCALPHA)
    for i in range(m(5), 0, -1):
        a = int(150 * (1 - i / m(5)) ** 1.4)
        pygame.draw.circle(spec, (255, 246, 214, a),
                           (int(c - r * 0.34), int(c - r * 0.34)), i)
    spec.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    seal.blit(spec, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── pressed-wax rim: a dark contact keyline all round, then a warm-gold lit
    # bead biased to the top-left arc so the raised edge glints there.
    pygame.draw.polygon(seal, (58, 32, 6), rim, width=max(1, m(1.2)))
    lit = _wax_polygon(c - m(0.5), c - m(0.5), r - m(0.9))
    hi = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.polygon(hi, (255, 236, 180, 210), lit, width=max(1, m(1)))
    grad = pygame.Surface((S, S), pygame.SRCALPHA)
    for y in range(S):
        a = int(255 * (1 - y / S) ** 1.5)
        pygame.draw.line(grad, (255, 255, 255, a), (0, y), (S, y))
    hi.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    seal.blit(hi, (0, 0))

    # ── intaglio 5-point star: a recessed dark carve with a mint lit lip on its
    # top-left edges (sculpted, NOT engraved text and NOT an ink check). The
    # cavity floor is deepest gold; the up-left lip catches cool light.
    def star_pts(scx, scy, ro, ri_, rot=-math.pi / 2):
        p = []
        for k in range(10):
            rr = ro if k % 2 == 0 else ri_
            aa = rot + math.pi * k / 5
            p.append((scx + rr * math.cos(aa), scy + rr * math.sin(aa)))
        return p

    ro, rin = r * 0.62, r * 0.26
    # cast shadow of the cavity, offset down-right (light from up-left)
    pygame.draw.polygon(seal, (40, 22, 4, 200),
                        star_pts(c + m(0.7), c + m(0.7), ro, rin))
    # recessed floor
    floor = lerp(sc.GOLD_A_BOT, NEAR_BLACK, 0.34)
    pygame.draw.polygon(seal, floor, star_pts(c, c, ro, rin))
    # inner deepening toward the pit centre
    pygame.draw.polygon(seal, lerp(floor, NEAR_BLACK, 0.30),
                        star_pts(c, c, ro * 0.5, rin * 0.5))
    # mint lit lip: the carved top-left edge catching cool light
    lip = star_pts(c - m(0.7), c - m(0.7), ro, rin)
    pygame.draw.polygon(seal, (206, 240, 220, 235), lip, width=max(1, m(0.8)))

    # ── the whole seal drops a soft shadow onto the frame so it sits ON the bead
    # like applied wax, not painted into it. Blitted UNDER the seal.
    sh = pygame.Surface((S, S), pygame.SRCALPHA)
    for i in range(m(4), 0, -1):
        a = int(70 * (1 - i / m(4)))
        pygame.draw.polygon(sh, (0, 0, 0, a),
                            _wax_polygon(c, c, r + i * 0.6))
    surf.blit(sh, (cx - c + m(1), cy - c + m(2)))
    surf.blit(seal, (cx - c, cy - c))


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + wax seal on top)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_wax_seal_medallion(p2)

# Compose review sheet
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
GOLD = (236, 202, 116); GREY = (150, 152, 168); CREAM_LBL = (250, 246, 232)
xs = [20, 360, 700]
panel_y = PAD + HDR_H + LBL_H
sheet_w = xs[-1] + PANEL_W + PAD
strip_w, strip_h = sc.CARD_W * 2, sc.CARD_H * 2
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H
sheet_h = zoom_y + strip_h + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)
title_f = hud_font(22, True)
tt = title_f.render("equipped v4 — wax-seal-medallion · round 1 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))
labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY), ("+ WAX SEAL", CREAM_LBL)]
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
    "docs", "store_equipped_v4", "wax_seal_medallion", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
