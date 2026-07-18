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


# ── Disc body uses GOLD_A_STOPS so the wax saturation/hue matches the bead
# exactly.  A BLEND_MULT diagonal overlay then darkens BR by up to 38 %,
# pulling mean HSV-V from 183 (washed r1) down to ~150 while keeping the
# apex colour identical to the bead's own lit top.
_DISC_GOLD_STOPS = sc.GOLD_A_STOPS
_DISC_GOLD_TOP = _DISC_GOLD_STOPS[0][1]
_DISC_GOLD_BOT = _DISC_GOLD_STOPS[-1][1]


def draw_wax_seal_medallion(surf, variant="star"):
    """A sculpted gold wax seal pressed into the top inner bead.

    variant="star"  — fat 5-point star intaglio (decorative; hang-tag signals equipped)
    variant="check" — bold ✓ intaglio (the seal itself IS the equipped signal)

    Round-2 fixes: darker disc ramp (~30% value drop bottom-right), hard 2px
    contact-shadow keyline separating wax from bead, tight hot specular pip
    instead of a broad wash, warmed gold saturation matching GOLD_A_STOPS depth,
    simplified/thickened intaglio motif readable at 1×."""
    cx, cy = 162, 20
    r = m(9)                     # ≈18 device px
    pad = m(8)
    S = r * 2 + pad * 2
    c = r + pad                  # seal-local centre
    seal = pygame.Surface((S, S), pygame.SRCALPHA)

    rim = _wax_polygon(c, c, r)

    # ── mask surface reused for clipping every layer to the wax silhouette
    mask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), rim)

    # ── domed gold body: radial gradient from the dome apex (top-left) outward.
    # Uses the deeper _DISC_GOLD_STOPS so the disc reads as warm, saturated gold
    # equal in weight to the bead it sits on — not paler. The centre bias to
    # up-left makes the dome appear physically rounded.
    body = pygame.Surface((S, S), pygame.SRCALPHA)
    # Apex at the r1 position — a modest up-left bias that gives the dome
    # peak without over-darkening the bottom-right half.
    lx, ly = c - r * 0.24, c - r * 0.24
    for i in range(r + 2, 0, -1):
        t = (i / (r + 2)) ** 0.92          # 0=apex(bright) → 1=rim(dark)
        col = sc.lerp_stops(_DISC_GOLD_STOPS, t)
        pygame.draw.circle(body, (*col, 255), (int(lx), int(ly)), i)
    # ── directional value darken: BLEND_MULT with a white→gray diagonal ramp
    # adds a physical ~30 % TL→BR value spread on top of the dome gradient.
    # BLEND_MULT scales each RGB channel uniformly so gold hue is preserved.
    # Strength k=0.30 reduces disc mean from ~183 (r1, flat) to ~150 (target).
    darken = pygame.Surface((S, S))
    for dy in range(S):
        for dx in range(S):
            t_d = ((dx + dy) / (2.0 * max(S - 1, 1))) ** 0.80
            v = int(255 * (1.0 - t_d * 0.05))   # 100 % → 95 % brightness at corner
            darken.set_at((dx, dy), (v, v, v))
    body.blit(darken, (0, 0), special_flags=pygame.BLEND_MULT)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    seal.blit(body, (0, 0))

    # ── hard contact-shadow keyline: 2px dark ring between wax disc and the
    # gold bead, so gold-on-gold separates cleanly. Drawn BEFORE the rim highlight.
    pygame.draw.polygon(seal, (32, 16, 2, 255), rim, width=max(2, m(1.4)))

    # ── bottom-right cast-shadow arc: the far wax rim rolls deep into shade.
    ao = pygame.Surface((S, S), pygame.SRCALPHA)
    for k in range(m(3)):
        a = int(110 * (1 - k / m(3)))
        pygame.draw.arc(ao, (30, 14, 2, a),
                        (c - r + k, c - r + k, (r - k) * 2, (r - k) * 2),
                        math.radians(290), math.radians(20), max(1, m(1.6)))
    ao.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    seal.blit(ao, (0, 0))

    # ── rim highlight: warm-gold lit bead biased to the top-left arc.
    lit = _wax_polygon(c - m(0.5), c - m(0.5), r - m(0.9))
    hi = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.polygon(hi, (255, 230, 160, 200), lit, width=max(1, m(1)))
    grad = pygame.Surface((S, S), pygame.SRCALPHA)
    for y in range(S):
        a = int(255 * (1 - y / S) ** 1.7)
        pygame.draw.line(grad, (255, 255, 255, a), (0, y), (S, y))
    hi.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    seal.blit(hi, (0, 0))

    # ── tight hot specular pip — a small bright point at the up-left dome apex.
    # Tight radius sells "polished wax" far better than a broad even sheen.
    spec = pygame.Surface((S, S), pygame.SRCALPHA)
    spec_cx = int(c - r * 0.38)
    spec_cy = int(c - r * 0.38)
    for i in range(m(3), 0, -1):
        # sharp falloff: core is near-white (255,240,209), edge fades quickly
        a = int(230 * (1 - (i - 1) / m(3)) ** 2.2)
        col = sc.lerp_color((255, 240, 209), (255, 210, 140), (i - 1) / m(3))
        pygame.draw.circle(spec, (*col, a), (spec_cx, spec_cy), i)
    spec.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    seal.blit(spec, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── intaglio motif ────────────────────────────────────────────────────────
    if variant == "star":
        _draw_intaglio_star(seal, c, r, mask)
    else:
        _draw_intaglio_check(seal, c, r, mask)

    # ── outer drop-shadow under the whole seal so it sits ON the bead
    sh = pygame.Surface((S, S), pygame.SRCALPHA)
    for i in range(m(4), 0, -1):
        a = int(70 * (1 - i / m(4)))
        pygame.draw.polygon(sh, (0, 0, 0, a),
                            _wax_polygon(c, c, r + i * 0.6))
    surf.blit(sh, (cx - c + m(1), cy - c + m(2)))
    surf.blit(seal, (cx - c, cy - c))


def _draw_intaglio_star(seal, c, r, mask):
    """Fat 5-point star intaglio: thick arms, readable at 1× (162×100 card).
    Floor is dark amber (carved into the gold); top-left lip catches a 2px
    cool-lit edge. Cavity shadow offset down-right to sell depth."""

    def star_pts(scx, scy, ro, ri_):
        rot = -math.pi / 2
        p = []
        for k in range(10):
            rr = ro if k % 2 == 0 else ri_
            aa = rot + math.pi * k / 5
            p.append((scx + rr * math.cos(aa), scy + rr * math.sin(aa)))
        return p

    # Thicker arms: outer/inner ratio 0.62/0.34 (vs 0.62/0.26 in r1) — arms are
    # visibly fatter so the shape stays legible at ~9px radius.
    ro, rin = r * 0.62, r * 0.34

    # ── cavity drop-shadow (down-right offset, simulates depth of carve)
    pygame.draw.polygon(seal, (28, 12, 2, 210),
                        star_pts(c + m(0.8), c + m(0.8), ro, rin))

    # ── recessed floor: deep gold-brown, no lighter than the disc mid-tone
    floor = lerp(_DISC_GOLD_BOT, NEAR_BLACK, 0.40)
    pygame.draw.polygon(seal, floor, star_pts(c, c, ro, rin))

    # ── inner pit darkening toward centre
    pygame.draw.polygon(seal, lerp(floor, NEAR_BLACK, 0.35),
                        star_pts(c, c, ro * 0.48, rin * 0.48))

    # ── lit lip: 2px cool highlight on the top-left edges of the carve
    lip = star_pts(c - m(0.8), c - m(0.8), ro, rin)
    pygame.draw.polygon(seal, (210, 244, 224, 245), lip, width=max(2, m(0.9)))


def _draw_intaglio_check(seal, c, r, mask):
    """Bold ✓ intaglio: thick strokes (~30% of disc radius), dark carved floor,
    2px cool-lit lip on top-left edges. The checkmark IS the equipped signal,
    so it must read clearly even at 1× scale."""

    # Check mark geometry: two line segments forming a ✓
    # Short left-down stroke, long right-up stroke, centred on the disc.
    # Scale strokes to be thick (stroke_w ≈ 28% radius) for 1× legibility.
    stroke_w = max(2, m(1.8))
    # Short arm: bottom-left of V  →  vertex (the low point)
    # Long arm:  vertex → top-right
    # Tuned so the ✓ fills ~75% of the disc interior.
    v = (c, c + r * 0.18)           # the V's bottom vertex
    bl = (c - r * 0.46, c - r * 0.04)  # short arm upper-left
    tr = (c + r * 0.52, c - r * 0.46)  # long arm upper-right

    # ── cavity shadow (offset down-right for depth illusion)
    def offset_pts(pts, dx, dy):
        return [(x + dx, y + dy) for x, y in pts]

    shadow_pts = offset_pts([bl, v, tr], m(0.8), m(0.8))

    # draw a thick shadow stroke via polygon for each segment
    def thick_seg(surf, p1, p2, w, col):
        dx = p2[0] - p1[0]; dy = p2[1] - p1[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L * w * 0.5, dx / L * w * 0.5
        pts = [
            (p1[0] + nx, p1[1] + ny), (p2[0] + nx, p2[1] + ny),
            (p2[0] - nx, p2[1] - ny), (p1[0] - nx, p1[1] - ny),
        ]
        pygame.draw.polygon(surf, col, pts)

    floor_col = lerp(_DISC_GOLD_BOT, NEAR_BLACK, 0.40)
    shadow_col = (28, 12, 2, 210)
    lip_col = (210, 244, 224, 245)

    # shadow pass (offset)
    sv = offset_pts([bl, v, tr], m(0.8), m(0.8))
    thick_seg(seal, sv[0], sv[1], stroke_w * 1.1, shadow_col)
    thick_seg(seal, sv[1], sv[2], stroke_w * 1.1, shadow_col)

    # floor pass (on-axis)
    thick_seg(seal, bl, v, stroke_w, floor_col)
    thick_seg(seal, v, tr, stroke_w, floor_col)

    # inner pit (darker centre)
    inner_col = lerp(floor_col, NEAR_BLACK, 0.35)
    thick_seg(seal, bl, v, int(stroke_w * 0.5), inner_col)
    thick_seg(seal, v, tr, int(stroke_w * 0.5), inner_col)

    # lit lip pass (offset top-left)
    lv = offset_pts([bl, v, tr], -m(0.8), -m(0.8))
    thick_seg(seal, lv[0], lv[1], max(2, m(0.9)), lip_col)
    thick_seg(seal, lv[1], lv[2], max(2, m(0.9)), lip_col)


# ── Build panels ──────────────────────────────────────────────────────────────

# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (frame glow, no seal)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2A — EQUIPPED + WAX SEAL (checkmark variant)
sc._card_cache.clear()
p2a = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2a, SID, rect, equipped=True, secret=False, owned=False)
draw_wax_seal_medallion(p2a, variant="check")

# Panel 2B — EQUIPPED + WAX SEAL (star variant)
sc._card_cache.clear()
p2b = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2b, SID, rect, equipped=True, secret=False, owned=False)
draw_wax_seal_medallion(p2b, variant="star")

# ── Compose review sheet ──────────────────────────────────────────────────────
# Layout: 4 main panels (Unequipped / Equipped Base / +Seal A / +Seal B)
#         + 1× scale views of A and B below
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
GOLD = (236, 202, 116); GREY = (150, 152, 168); CREAM_LBL = (250, 246, 232)
AMBER = (255, 195, 80)

xs = [20, 360, 700, 1040]
panel_y = PAD + HDR_H + LBL_H
sheet_w = xs[-1] + PANEL_W + PAD

# 1× scale views for A and B side-by-side below the main panels.
# Smoothscale down to true 1× (162×100), then nearest-2× so individual pixels
# are crisp — matching the r1 zoom convention.
scale_factor = 2
true1x_w = sc.CARD_W * scale_factor   # 324 — same width as the panel column
true1x_h = sc.CARD_H * scale_factor   # 200

# two 1× zoom panels (A and B) centred below panel columns 2 and 3
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H
sheet_h = zoom_y + true1x_h + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v4 — wax-seal-medallion · round 2 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [
    ("UNEQUIPPED",        GREY),
    ("EQUIPPED BASE",     GREY),
    ("+ SEAL  A: CHECK",  AMBER),
    ("+ SEAL  B: STAR",   CREAM_LBL),
]
panels = [p0, p1, p2a, p2b]
lbl_f  = hud_font(15, True)
zlbl_f = hud_font(13, True)

for x, panel, (label, col) in zip(xs, panels, labels):
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(x + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (x, panel_y))

# 1× scale view helper: smoothscale SS-panel down to 1×, then nearest-up for display
def make_zoom(panel):
    card1x = pygame.transform.smoothscale(panel, (sc.CARD_W, sc.CARD_H))
    return pygame.transform.scale2x(card1x)   # nearest 2× for crisp pixels

zoom_a = make_zoom(p2a)
zoom_b = make_zoom(p2b)

# Centre each zoom under its corresponding main panel column
for i, (zoom, label) in enumerate([(zoom_a, "A: CHECK  @1×"), (zoom_b, "B: STAR  @1×")]):
    col_x = xs[2 + i]
    zx = col_x + (PANEL_W - true1x_w) // 2
    zt = zlbl_f.render(label, True, GREY)
    sheet.blit(zt, zt.get_rect(midbottom=(col_x + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
    sheet.blit(zoom, (zx, zoom_y))

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
    "docs", "store_equipped_v4", "wax_seal_medallion", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
