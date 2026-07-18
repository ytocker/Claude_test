#!/usr/bin/env python3
"""Round-2 review render for the `corner-sash-banner` equipped indicator.
Addresses all art-director R1 ITERATE notes:
- Sash shrunk (A→252,8 / B→316,72) so the sash body stays outside the gem.
- Gem punched from the layer so the gem always shows through cleanly.
- Dark-key fill (46,38,18) body with perpendicular gradient (lit facing side,
  dark shadow corner) so the sash breaks value from the gold regalia frame.
- Swallowtail V-notches at A and B mark it as a ribbon award, not a sticker.
- 4px crease (9,9,22), 2px fold-glint cream (255,240,190) on the outer edge.
- EQUIPPED text assembled with dark keyline before rotating, drawn on the layer
  so the gem punch-out clips it cleanly at the gem boundary."""
import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pygame; pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
import game.store_cards as sc
import game.store_data as sd
from game.draw import lerp_color
from game.hud import _font as hud_font
sd.load()

SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324×200
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)   # 8,8,308,184

# Sash geometry — A and B pulled inward so the sash body clears the gem
A      = (252, 8)
CORNER = (316, 8)
B      = (316, 72)

# Gem position, matching store_cards.facet_gem call exactly
GEM_CX = rect.right - sc.m(19)            # 278
GEM_CY = rect.y    + sc.m(19)             # 46
# Punch radius: exactly the gem facet outer edge so the gem face is unobstructed
# while the sash body stays present outside the facet boundary.
GEM_PUNCH_R = sc.m(sc.GEM_R + 3)              # 22 — matches facet_gem radius arg


def _perp_grad_fill(box_x, box_y, bw, a_x, a_y):
    """75×75 surface: perpendicular-to-diagonal gradient that runs ACROSS the
    ribbon band. t=0 on the outer A–B edge (lit facing side), t=1 at the corner
    (shadow side). Conveys fold direction without a vertical ramp."""
    SASH_LIT  = (86,  68, 28)   # facing / outer edge
    SASH_MID  = (46,  38, 18)   # base dark key
    SASH_DARK = (16,  10,  4)   # corner shadow
    surf = pygame.Surface((bw, bw), pygame.SRCALPHA)
    inv_bw = 1.0 / 64.0
    for py in range(bw):
        for px in range(bw):
            gx, gy = box_x + px, box_y + py
            # perpendicular parameter: 0 on A–B, 1 at corner
            t = (gx - gy - (a_x - a_y)) * inv_bw
            t = max(0.0, min(1.0, t))
            pivot = 0.45
            if t < pivot:
                col = lerp_color(SASH_LIT, SASH_MID, t / pivot)
            else:
                col = lerp_color(SASH_MID, SASH_DARK, (t - pivot) / (1.0 - pivot))
            surf.set_at((px, py), (*col, 255))
    return surf


def draw_corner_sash_banner(surf):
    """Dark-key (46,38,18) corner sash with swallowtail ends, perpendicular
    gradient fold, cream fold-glint on the hypotenuse, dark valley crease, and
    a keylined EQUIPPED label — all punched at the gem so the gem always shows
    through cleanly."""
    m = sc.m

    # swallowtail notch dimensions
    nd = m(6)   # notch depth (inward from card edge)
    nw = m(5)   # half notch base width

    # Full sash polygon with V-notches at A and B.
    # At A (top edge): notch tip points downward (into the ribbon band).
    # At B (right edge): notch tip points leftward (into the ribbon band).
    poly = [
        (A[0] - nw, A[1]),          # A_left
        (A[0],      A[1] + nd),     # V_tip_A  ← into ribbon
        (A[0] + nw, A[1]),          # A_right
        CORNER,
        (B[0],      B[1] - nw),     # B_top
        (B[0] - nd, B[1]),          # V_tip_B  ← into ribbon
        (B[0],      B[1] + nw),     # B_bottom
    ]

    layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)

    # ── (1) Sash gradient fill ──────────────────────────────────────────────
    box_x, box_y = A[0] - nw, A[1]         # 242, 8
    bw = B[0] - box_x + 1                  # 75
    bh = B[1] + nw - box_y + 1             # 75
    bw = bh = max(bw, bh)

    grad = _perp_grad_fill(box_x, box_y, bw, A[0], A[1])

    # Clip gradient to the swallowtail polygon via white-fill BLEND_RGBA_MIN mask
    poly_mask = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.polygon(poly_mask, (255, 255, 255, 255), poly)

    temp_fill = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    temp_fill.blit(grad, (box_x, box_y))
    temp_fill.blit(poly_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    layer.blit(temp_fill, (0, 0))

    # ── (2) Valley crease — 4px dark navy, clipped to sash polygon ─────────
    off = 6
    nx, ny = 0.70711, -0.70711
    a_in = (int(A[0] + off * nx), int(A[1] + off * ny))
    b_in = (int(B[0] + off * nx), int(B[1] + off * ny))
    crease_layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.line(crease_layer, (9, 9, 22, 210), a_in, b_in, 4)
    crease_layer.blit(poly_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    layer.blit(crease_layer, (0, 0))

    # ── (3) Cream fold glint on outer A–B hypotenuse ───────────────────────
    pygame.draw.line(layer, (255, 240, 190, 230), A, B, 2)

    # ── (4) "EQUIPPED" label — dark keyline built BEFORE rotating ──────────
    f = sc.font(9)
    base = sc._glyph_base("EQUIPPED", f, m(0.8))
    base = sc._stamp_bold(base, m(0.8))
    bw2, bh2 = base.get_size()
    pad = 4

    # Keyline pass first so the edge crisps even after rotate
    kl_col = (9, 9, 22)
    kl = base.copy()
    kl.fill((*kl_col, 255), special_flags=pygame.BLEND_RGBA_MULT)

    txt_surf = pygame.Surface((bw2 + pad * 2, bh2 + pad * 2), pygame.SRCALPHA)
    for ang in range(0, 360, 45):
        dx = int(round(2 * math.cos(math.radians(ang))))
        dy = int(round(2 * math.sin(math.radians(ang))))
        txt_surf.blit(kl, (pad + dx, pad + dy))

    # Cream text core on top
    cream_txt = base.copy()
    cream_txt.fill((255, 240, 190, 255), special_flags=pygame.BLEND_RGBA_MULT)
    txt_surf.blit(cream_txt, (pad, pad))

    # Rotate: pygame.transform.rotate is CCW; -45 = 45° CW = text along A→B direction
    rot = pygame.transform.rotate(txt_surf, -45)

    # Place along diagonal, offset toward corner from A–B midpoint so text
    # body lands inside the sash triangle and away from the outer edge
    off_corner = 14
    mid_x = (A[0] + B[0]) // 2 + int(off_corner * nx)
    mid_y = (A[1] + B[1]) // 2 + int(off_corner * ny)
    layer.blit(rot, rot.get_rect(center=(mid_x, mid_y)))

    # ── (5) Re-clip everything to card rounded corner ───────────────────────
    cmask = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.rect(cmask, (255, 255, 255, 255), rect,
                     border_radius=sc.m(sc.CARD_RAD))
    layer.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # ── (6) Punch gem circle so the gem always shows through cleanly ────────
    gem_punch = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    gem_punch.fill((255, 255, 255, 255))
    pygame.draw.circle(gem_punch, (0, 0, 0, 0), (GEM_CX, GEM_CY), GEM_PUNCH_R)
    layer.blit(gem_punch, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # ── (7) Composite onto card ─────────────────────────────────────────────
    surf.blit(layer, (0, 0))


# ── build panels ────────────────────────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_corner_sash_banner(p2)


# ── compose review sheet ─────────────────────────────────────────────────────
BG     = (8, 8, 20)
PAD    = 20
LBL_H  = 34
SGAP   = 20
SLBL_H = 24
xs     = [20, 360, 700]
panel_y = 102

GOLD  = (236, 202, 116)
GREY  = (150, 150, 168)
CREAM = (246, 244, 232)

zoom = pygame.transform.smoothscale(p2, (162, 100))
zoom = pygame.transform.scale2x(zoom)

sheet_w = xs[-1] + PANEL_W + PAD
sheet_h = (panel_y + PANEL_H + LBL_H + SGAP + SLBL_H
           + zoom.get_height() + PAD)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)


def label(txt, x, y, w, col, size=18):
    f = hud_font(size, True)
    g = f.render(txt, True, col)
    sheet.blit(g, (x + (w - g.get_width()) // 2, y))


hf = hud_font(22, True)
hg = hf.render(
    "equipped v4c — corner-sash-banner · round 2 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [
    (p0, "UNEQUIPPED",           GREY),
    (p1, "EQUIPPED BASE",        GREY),
    (p2, "+ CORNER SASH BANNER", CREAM),
]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v4c", "corner_sash_banner", "round_2.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
