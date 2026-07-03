"""5 visual design proposals for the UFO colour-picker popup.

Each design is drawn over the same blurred gameplay background, then
stitched side-by-side into a comparison strip.

Saves to docs/store_redesign/parcels/ufo/picker_designs_comparison.png.
"""
import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pygame
pygame.init()

from game.config import W, H, GROUND_Y
from game import biome, parrot
from game.draw import (get_sky_surface_biome, draw_mountains, draw_ground,
                       draw_cloud, lerp_color, NEAR_BLACK, WHITE, UI_CREAM)
from game.entities import Pipe
from game import store_data
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP
from game.store import (
    _vgrad_panel, _drop_shadow, _inset_disc, _shelf_bar,
    _gem, _gold_rule, _soft_glow,
    _UFO_VARIANTS,
)
from game import store_cards
from game.parcel_designs.ufo import _build, _PALETTES

store_data.load()

# ── Gameplay background ───────────────────────────────────────────────────────
scene = pygame.Surface((W, H))
palette = biome.palette_for_phase(0.0)
scene.blit(get_sky_surface_biome(W, H, GROUND_Y, palette, 0), (0, 0))
for bx, by, sc, var in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
    draw_cloud(scene, bx, by, sc, variant=var)
draw_mountains(scene, 40.0, GROUND_Y, W, palette["mtn_far"], palette["mtn_near"])
Pipe(x=12,  gap_y=250, gap_h=185).draw(scene, palette)
Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
draw_ground(scene, GROUND_Y, W, H, 40.0,
            palette["ground_top"], palette["ground_mid"], (60, 40, 25))
bf = parrot.get_skin_frame("skin_parrot", 2, 10.0)
scene.blit(bf, bf.get_rect(center=(96, 270)))

# ── Pre-rendered UFO variant surfaces ─────────────────────────────────────────
def _ufo(key, size):
    return pygame.transform.smoothscale(_build(_PALETTES[key]), (size, size))

_SELECTED = "sapphire"

# ── Shared drawing helpers ────────────────────────────────────────────────────
def _scrim(surf):
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    s.fill((4, 4, 10, 180))
    surf.blit(s, (0, 0))


def _panel(surf, pw, ph, r=18):
    """Obsidian vgrad panel centred on screen; returns pygame.Rect."""
    panel = pygame.Rect((W - pw) // 2, (H - ph) // 2, pw, ph)
    _drop_shadow(surf, panel, r, blur=8, alpha=170)
    surf.blit(_vgrad_panel(pw, ph, r, (28, 24, 38), (12, 10, 22), 255),
              panel.topleft)
    pygame.draw.rect(surf, lerp_color(_GOLD_BRIGHT, NEAR_BLACK, 0.45), panel,
                     width=2, border_radius=r)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 230), panel.inflate(-2, -2),
                     width=1, border_radius=r - 2)
    return panel


def _header(surf, pcx, py0, title, subtitle):
    h1 = _font(17, True).render(title, True, _GOLD_BRIGHT)
    surf.blit(h1, h1.get_rect(center=(pcx, py0 + 22)))
    h2 = _font(11).render(subtitle, True, (140, 132, 160))
    surf.blit(h2, h2.get_rect(center=(pcx, py0 + 41)))
    _gold_rule(surf, pcx - 130, pcx + 130, py0 + 56)


def _buttons(surf, pcx, by0, bw=118, bh=40, gutter=14):
    """Draw CANCEL + CONFIRM buttons. Returns (cancel_rect, confirm_rect)."""
    nx = pcx - (bw * 2 + gutter) // 2
    cancel  = pygame.Rect(nx, by0, bw, bh)
    confirm = pygame.Rect(nx + bw + gutter, by0, bw, bh)

    surf.blit(_vgrad_panel(bw, bh, bh // 2, (70, 62, 80), (44, 38, 56)),
              cancel.topleft)
    pygame.draw.rect(surf, (126, 116, 138), cancel, 1, border_radius=bh // 2)
    ct = _font(14, True).render("CANCEL", True, UI_CREAM)
    surf.blit(ct, ct.get_rect(center=cancel.center))

    glow = pygame.Surface((bw + 10, bh + 10), pygame.SRCALPHA)
    for k in range(4, 0, -1):
        pygame.draw.rect(glow, (255, 200, 80, int(22 * k / 4)),
                         (5 - k, 5 - k, bw + 2 * k, bh + 2 * k),
                         border_radius=bh // 2 + k)
    surf.blit(glow, (confirm.x - 5, confirm.y - 5), special_flags=pygame.BLEND_ADD)
    surf.blit(_vgrad_panel(bw, bh, bh // 2,
                           lerp_color(_GOLD_BRIGHT, WHITE, 0.2), _GOLD_DEEP),
              confirm.topleft)
    pygame.draw.rect(surf, _GOLD_PALE, confirm, 1, border_radius=bh // 2)
    cft = _font(14, True).render("CONFIRM  ✓", True, (40, 24, 8))
    surf.blit(cft, cft.get_rect(center=confirm.center))
    return cancel, confirm


def _accent_gem(surf, cx, cy, r, accent, dim):
    """Small 4-facet gem badge in variant accent colour."""
    seat = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
    sc = r + 4
    pygame.draw.circle(seat, (0, 0, 0, 140), (sc, sc), r + 3)
    pygame.draw.circle(seat, (*_GOLD_DEEP, 70), (sc, sc), r + 3, 1)
    surf.blit(seat, (cx - sc, cy - sc))
    _soft_glow(surf, cx, cy, r + 3, accent, 55, layers=3)
    hi  = lerp_color(accent, WHITE, 0.50)
    sh  = lerp_color(accent, dim,   0.50)
    dk  = lerp_color(dim, NEAR_BLACK, 0.30)
    top_p = (cx, cy - r); bot_p = (cx, cy + r)
    lft_p = (cx - r, cy); rgt_p = (cx + r, cy)
    ctr_p = (cx, cy)
    pygame.draw.polygon(surf, hi,     [top_p, lft_p, ctr_p])
    pygame.draw.polygon(surf, accent, [top_p, rgt_p, ctr_p])
    pygame.draw.polygon(surf, sh,     [lft_p, bot_p, ctr_p])
    pygame.draw.polygon(surf, dk,     [rgt_p, bot_p, ctr_p])
    pygame.draw.polygon(surf, lerp_color(dim, NEAR_BLACK, 0.45),
                        [top_p, rgt_p, bot_p, lft_p], width=1)
    pr = max(1, r // 4)
    pip = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 245), (pr + 1, pr + 1), pr)
    surf.blit(pip, (cx - pr - r // 3, cy - pr - r // 3), special_flags=pygame.BLEND_ADD)


def _accent_shelf(surf, rect_or_x, y_bottom, w, accent, dim):
    """Custom shelf-bar glow in variant accent colour."""
    wash_h = 12
    wash = pygame.Surface((w, wash_h), pygame.SRCALPHA)
    for ly in range(wash_h):
        f = 1.0 - ly / wash_h
        a = int(60 * f ** 2.4)
        if a > 0:
            pygame.draw.line(wash, (*accent, a), (0, wash_h - 1 - ly),
                             (w - 1, wash_h - 1 - ly))
    mid = w // 2
    core = pygame.Surface((w, 2), pygame.SRCALPHA)
    for lx in range(w):
        hx = abs(lx - mid) / max(1, mid)
        col = lerp_color(lerp_color(accent, WHITE, 0.35), dim, hx ** 1.5)
        a = int(215 * (1.0 - 0.4 * hx ** 2))
        core.set_at((lx, 0), (*col, a))
        core.set_at((lx, 1), (*accent, a // 2))
    x = rect_or_x if isinstance(rect_or_x, int) else rect_or_x.x
    surf.blit(wash, (x, y_bottom - wash_h + 1), special_flags=pygame.BLEND_ADD)
    surf.blit(core, (x, y_bottom))


# =============================================================================
# DESIGN 1 — CONSTELLATION CARDS
# Each swatch is a proper mini card: vgrad body, bevel rim, cabochon dome,
# facet gem badge — speaks the CONSTELLATION DNA directly.
# =============================================================================
def draw_design_1(surf):
    _scrim(surf)
    PW, PH = 342, 374
    p = _panel(surf, PW, PH)
    px0, py0, pcx = p.x, p.y, p.centerx

    _header(surf, pcx, py0, "MINI UFO", "Choose your colour  —  one-time pick")

    CW, CH = 57, 98
    GAP = 7
    n = len(_UFO_VARIANTS)
    row_w = n * CW + (n - 1) * GAP
    sx0 = pcx - row_w // 2
    sy0 = py0 + 66

    for i, v in enumerate(_UFO_VARIANTS):
        sx = sx0 + i * (CW + GAP)
        cr = pygame.Rect(sx, sy0, CW, CH)
        sel = (v["key"] == _SELECTED)
        accent, dim = v["accent"], v["dim"]

        # Card body (CONSTELLATION indigo gradient + top sheen)
        body_t = (38, 40, 84) if sel else store_cards.CARD_T
        body_b = (16, 17, 46) if sel else store_cards.CARD_B
        surf.blit(_vgrad_panel(CW, CH, 9, body_t, body_b), cr.topleft)
        store_cards.top_sheen(surf, cr, 9, CH // 3, peak=32)

        # Double bevel rim — gold when selected, dim when not
        if sel:
            pygame.draw.rect(surf, _GOLD_DEEP, cr, 2, border_radius=9)
            inner = cr.inflate(-2, -2)
            pygame.draw.rect(surf, (*_GOLD_BRIGHT, 190), inner, 1, border_radius=7)
            _soft_glow(surf, cr.centerx, cr.centery, 36, _GOLD_BRIGHT, 24, layers=4)
        else:
            store_cards.bevel_rim(surf, cr, 9, store_cards.CARD_RING_DEEP,
                                  (*store_cards.CARD_RING_BRIGHT, 55), 2)

        # Cabochon dome  (r=19 gives a 38px diameter well)
        r_c = 19
        cabo_cx = cr.centerx
        cabo_cy = sy0 + 10 + r_c
        store_cards.cabochon(surf, cabo_cx, cabo_cy, r_c)
        img = _ufo(v["key"], 32)
        surf.blit(img, img.get_rect(center=(cabo_cx, cabo_cy)))
        store_cards.cabochon_glass(surf, cabo_cx, cabo_cy, r_c)

        # Accent shelf bar at bottom of the cabochon area
        _accent_shelf(surf, sx + 8, cabo_cy + r_c + 6, CW - 16, accent, dim)

        # Facet gem badge (top-right corner, 8-facet brilliant from store_cards)
        gem_r = 7
        store_cards.facet_gem(surf, cr.right + 1, cr.y + 1, gem_r, accent, dim)

        # Name label
        lbl_col = _GOLD_BRIGHT if sel else (158, 150, 182)
        lbl = _font(9, True).render(v["name"], True, lbl_col)
        surf.blit(lbl, lbl.get_rect(center=(cr.centerx, cr.bottom - 10)))

    # Selected-variant detail strip
    sel_v = next(v for v in _UFO_VARIANTS if v["key"] == _SELECTED)
    dy = sy0 + CH + 10
    sn = _font(15, True).render(sel_v["name"], True, _GOLD_BRIGHT)
    surf.blit(sn, sn.get_rect(center=(pcx, dy)))
    sd = _font(11).render(sel_v["desc"], True, UI_CREAM)
    surf.blit(sd, sd.get_rect(center=(pcx, dy + 18)))
    _gold_rule(surf, px0 + 28, p.right - 28, dy + 36)
    _buttons(surf, pcx, dy + 44)


# =============================================================================
# DESIGN 2 — SHOWCASE STAGE
# Large single-item hero spotlight dominates; accent dots for selection.
# =============================================================================
def draw_design_2(surf):
    _scrim(surf)
    PW, PH = 302, 356
    p = _panel(surf, PW, PH)
    px0, py0, pcx = p.x, p.y, p.centerx

    _header(surf, pcx, py0, "MINI UFO", "One-time colour pick")

    # Hero inset disc  (r=46 ≈ 92px diameter)
    disc_r = 46
    disc_cy = py0 + 62 + disc_r          # = py0 + 108
    sel_v = next(v for v in _UFO_VARIANTS if v["key"] == _SELECTED)
    _inset_disc(surf, pcx, disc_cy, disc_r)
    _soft_glow(surf, pcx, disc_cy, disc_r + 20, sel_v["accent"], 70, layers=6)
    img = _ufo(_SELECTED, 74)
    surf.blit(img, img.get_rect(center=(pcx, disc_cy)))
    # Gold bezel
    pygame.draw.circle(surf, (0, 0, 0, 190), (pcx, disc_cy), disc_r, 2)
    pygame.draw.circle(surf, (*_GOLD_BRIGHT, 200), (pcx, disc_cy), disc_r - 1, 1)

    # Variant name + desc below disc
    name_y = disc_cy + disc_r + 18
    vname = _font(17, True).render(sel_v["name"], True, _GOLD_BRIGHT)
    surf.blit(vname, vname.get_rect(center=(pcx, name_y)))
    vdesc = _font(11).render(sel_v["desc"], True, UI_CREAM)
    surf.blit(vdesc, vdesc.get_rect(center=(pcx, name_y + 18)))

    # 5 accent selection dots
    dot_r = 13
    dot_gap = 10
    n = len(_UFO_VARIANTS)
    dots_w = n * dot_r * 2 + (n - 1) * dot_gap
    dot_x0 = pcx - dots_w // 2
    dot_y = name_y + 46

    _gold_rule(surf, px0 + 24, p.right - 24, dot_y - 14)

    for i, v in enumerate(_UFO_VARIANTS):
        cx = dot_x0 + i * (dot_r * 2 + dot_gap) + dot_r
        sel = (v["key"] == _SELECTED)
        acc = v["accent"]
        if sel:
            _soft_glow(surf, cx, dot_y, dot_r + 8, acc, 75, layers=4)
            pygame.draw.circle(surf, acc, (cx, dot_y), dot_r)
            pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, dot_y), dot_r + 2, 2)
        else:
            pygame.draw.circle(surf, (22, 20, 34), (cx, dot_y), dot_r)
            pygame.draw.circle(surf, (*acc, 170), (cx, dot_y), dot_r, 2)
        # Tiny variant shortname below dot
        word = v["name"].split()[0]
        tiny = _font(8, True).render(word, True,
                                     _GOLD_BRIGHT if sel else (100, 96, 122))
        surf.blit(tiny, tiny.get_rect(center=(cx, dot_y + dot_r + 9)))

    rule_y = dot_y + dot_r + 24
    _gold_rule(surf, px0 + 24, p.right - 24, rule_y)
    _buttons(surf, pcx, rule_y + 12)


# =============================================================================
# DESIGN 3 — VERTICAL COLUMNS
# Panel divided into 5 equal accent-tinted strips; selected column glows gold.
# =============================================================================
def draw_design_3(surf):
    _scrim(surf)
    PW, PH = 342, 326
    p = _panel(surf, PW, PH)
    px0, py0, pcx = p.x, p.y, p.centerx

    # Compact title
    h1 = _font(15, True).render("MINI UFO  —  Choose your colour", True, _GOLD_BRIGHT)
    surf.blit(h1, h1.get_rect(center=(pcx, py0 + 18)))
    _gold_rule(surf, px0 + 24, p.right - 24, py0 + 32)

    COL_TOP = py0 + 38
    COL_BOT = py0 + PH - 88
    col_h   = COL_BOT - COL_TOP
    MARGIN  = 3
    n = len(_UFO_VARIANTS)
    col_w   = (PW - 2 * MARGIN) // n
    col_x0  = px0 + MARGIN

    for i, v in enumerate(_UFO_VARIANTS):
        cx0 = col_x0 + i * col_w
        cr = pygame.Rect(cx0, COL_TOP, col_w - 1, col_h)
        sel = (v["key"] == _SELECTED)
        acc, dim = v["accent"], v["dim"]

        # Column background tint (additive accent on dark base)
        col_bg = pygame.Surface((col_w - 1, col_h), pygame.SRCALPHA)
        col_bg.fill((*acc, 50 if sel else 18))
        cmask = pygame.Surface((col_w - 1, col_h), pygame.SRCALPHA)
        pygame.draw.rect(cmask, (255, 255, 255, 255), (0, 0, col_w - 1, col_h))
        col_bg.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(col_bg, (cx0, COL_TOP))

        # Left edge accent bar (4 px)
        bar_a = 220 if sel else 100
        bar = pygame.Surface((4, col_h), pygame.SRCALPHA)
        bar.fill((*acc, bar_a))
        surf.blit(bar, (cx0, COL_TOP))

        # Selected: gold border + inner glow
        if sel:
            pygame.draw.rect(surf, _GOLD_BRIGHT, cr, 1)
            _soft_glow(surf, cx0 + col_w // 2, COL_TOP + col_h // 2,
                       24, acc, 30, layers=3)
        else:
            pygame.draw.line(surf, (44, 40, 60),
                             (cx0, COL_TOP), (cx0, COL_BOT), 1)

        # UFO parcel centred in column
        parcel_cy = COL_TOP + col_h // 2 - 8
        img = _ufo(v["key"], 36)
        surf.blit(img, img.get_rect(center=(cx0 + col_w // 2, parcel_cy)))

        # Name label
        lbl_col = _GOLD_BRIGHT if sel else (130, 124, 152)
        lbl = _font(9, True).render(v["name"], True, lbl_col)
        surf.blit(lbl, lbl.get_rect(center=(cx0 + col_w // 2, parcel_cy + 27)))

        # Accent shelf at bottom of column
        shelf_w = col_w - 10
        _accent_shelf(surf, cx0 + 5, COL_BOT - 2, shelf_w, acc, dim)

    # Selected-variant detail
    sel_v = next(v for v in _UFO_VARIANTS if v["key"] == _SELECTED)
    dy = COL_BOT + 6
    _gold_rule(surf, px0 + 24, p.right - 24, dy)
    det = _font(13, True).render(
        sel_v["name"] + "   " + sel_v["desc"], True, _GOLD_BRIGHT)
    surf.blit(det, det.get_rect(center=(pcx, dy + 14)))
    _gold_rule(surf, px0 + 24, p.right - 24, dy + 30)
    _buttons(surf, pcx, dy + 38)


# =============================================================================
# DESIGN 4 — ORBIT ARC
# 5 parcels in a downward-opening arc; selected elevated + glowing.
# =============================================================================
def draw_design_4(surf):
    _scrim(surf)
    PW, PH = 322, 366
    p = _panel(surf, PW, PH)
    px0, py0, pcx = p.x, p.y, p.centerx

    _header(surf, pcx, py0, "MINI UFO", "One-time colour pick")

    # Arc geometry: pivot near top, items hang in a downward arc
    arc_cx = pcx
    arc_cy = py0 + 68          # pivot row
    arc_r  = 90
    n      = len(_UFO_VARIANTS)
    spread = 130               # degrees total
    start_a = 90 - spread // 2  # 90 = straight down; spread around it

    for i, v in enumerate(_UFO_VARIANTS):
        angle_deg = start_a + i * spread / (n - 1)
        angle_rad = math.radians(angle_deg)
        ix = int(arc_cx + arc_r * math.cos(angle_rad))
        iy = int(arc_cy + arc_r * math.sin(angle_rad))
        sel = (v["key"] == _SELECTED)
        acc, dim = v["accent"], v["dim"]
        r_c = 23 if sel else 20

        if sel:
            iy -= 8  # elevate selected item

        # Dark dome well
        for rr in range(r_c, 0, -1):
            t = 1.0 - rr / r_c
            col = lerp_color((28, 30, 56), (8, 8, 20), t ** 1.2)
            pygame.draw.circle(surf, (*col, 255), (ix, iy), rr)

        if sel:
            _soft_glow(surf, ix, iy, r_c + 14, acc, 72, layers=5)
            pygame.draw.circle(surf, _GOLD_BRIGHT, (ix, iy), r_c + 1, 2)
        else:
            pygame.draw.circle(surf, (*_GOLD_DEEP, 100), (ix, iy), r_c, 1)

        # UFO parcel
        sz = 38 if sel else 32
        img = _ufo(v["key"], sz)
        surf.blit(img, img.get_rect(center=(ix, iy)))

        # Translucent glass crescent overlay
        over = pygame.Surface((r_c * 2 + 4, r_c * 2 + 4), pygame.SRCALPHA)
        oc = r_c + 2
        sr = int(r_c * 0.72)
        spec = pygame.Surface(over.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(spec, (255, 255, 255, 88),
                           (oc - int(r_c * 0.18), oc - int(r_c * 0.18)), sr)
        cut = pygame.Surface(over.get_size(), pygame.SRCALPHA)
        cut.fill((255, 255, 255, 255))
        pygame.draw.circle(cut, (0, 0, 0, 0),
                           (oc + int(r_c * 0.12), oc + int(r_c * 0.12)),
                           int(r_c * 0.82))
        spec.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        mask = pygame.Surface(over.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (oc, oc), r_c - 1)
        spec.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        over.blit(spec, (0, 0), special_flags=pygame.BLEND_ADD)
        surf.blit(over, (ix - oc, iy - oc), special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(surf, (*_GOLD_BRIGHT, 140), (ix, iy), r_c, 1)

        # Gem badge top-right
        _accent_gem(surf, ix + r_c - 2, iy - r_c + 2, 6, acc, dim)

    # Central detail area
    sel_v = next(v for v in _UFO_VARIANTS if v["key"] == _SELECTED)
    dy = py0 + 200
    vname = _font(15, True).render(sel_v["name"], True, _GOLD_BRIGHT)
    surf.blit(vname, vname.get_rect(center=(pcx, dy)))
    vdesc = _font(11).render(sel_v["desc"], True, UI_CREAM)
    surf.blit(vdesc, vdesc.get_rect(center=(pcx, dy + 18)))
    note = _font(10).render("one-time pick — cannot be changed later", True,
                             (110, 104, 130))
    surf.blit(note, note.get_rect(center=(pcx, dy + 36)))
    _gold_rule(surf, px0 + 28, p.right - 28, dy + 52)
    _buttons(surf, pcx, dy + 60)


# =============================================================================
# DESIGN 5 — GLASS TABLETS
# 5 stacked horizontal rows; colour-coded left bar; inline name + desc.
# =============================================================================
def draw_design_5(surf):
    _scrim(surf)
    PW, PH = 302, 376
    p = _panel(surf, PW, PH)
    px0, py0, pcx = p.x, p.y, p.centerx

    _header(surf, pcx, py0, "MINI UFO", "Choose your colour  —  one-time pick")

    TAB_H   = 48
    TAB_GAP = 4
    TAB_W   = PW - 24
    tab_x0  = px0 + 12
    tab_y0  = py0 + 63

    for i, v in enumerate(_UFO_VARIANTS):
        ty = tab_y0 + i * (TAB_H + TAB_GAP)
        tr = pygame.Rect(tab_x0, ty, TAB_W, TAB_H)
        sel = (v["key"] == _SELECTED)
        acc, dim = v["accent"], v["dim"]

        # Tablet body
        bg = (26, 22, 42) if not sel else (30, 26, 48)
        body = _vgrad_panel(TAB_W, TAB_H, 8, lerp_color(bg, WHITE, 0.06), bg)
        surf.blit(body, tr.topleft)

        # Selected accent tint overlay
        if sel:
            tint = pygame.Surface((TAB_W, TAB_H), pygame.SRCALPHA)
            tint.fill((*acc, 28))
            tmask = pygame.Surface((TAB_W, TAB_H), pygame.SRCALPHA)
            pygame.draw.rect(tmask, (255, 255, 255, 255), (0, 0, TAB_W, TAB_H),
                             border_radius=8)
            tint.blit(tmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surf.blit(tint, tr.topleft)
            pygame.draw.rect(surf, _GOLD_BRIGHT, tr, 1, border_radius=8)
        else:
            pygame.draw.rect(surf, (40, 37, 58), tr, 1, border_radius=8)

        # Left accent edge bar (5 px, rounded left corners)
        bar_a = 235 if sel else 120
        bar   = pygame.Surface((5, TAB_H - 2), pygame.SRCALPHA)
        bar.fill((*acc, bar_a))
        bm    = pygame.Surface((5, TAB_H - 2), pygame.SRCALPHA)
        pygame.draw.rect(bm, (255, 255, 255, 255), (0, 0, 5, TAB_H - 2),
                         border_top_left_radius=8, border_bottom_left_radius=8)
        bar.blit(bm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(bar, (tab_x0, ty + 1))

        # Small parcel in a well (34×34)
        well = pygame.Rect(tab_x0 + 8, ty + (TAB_H - 34) // 2, 34, 34)
        pygame.draw.rect(surf, (10, 10, 22), well, border_radius=5)
        pygame.draw.rect(surf, (*_GOLD_DEEP, 90), well, 1, border_radius=5)
        img = _ufo(v["key"], 28)
        surf.blit(img, img.get_rect(center=well.center))

        # Name + desc text inline right
        text_x = well.right + 9
        nm = _font(12, True).render(v["name"], True,
                                     _GOLD_BRIGHT if sel else (196, 188, 220))
        surf.blit(nm, nm.get_rect(midleft=(text_x, ty + TAB_H // 2 - 8)))
        dc = _font(10).render(v["desc"], True, (128, 122, 152))
        surf.blit(dc, dc.get_rect(midleft=(text_x, ty + TAB_H // 2 + 8)))

        # Selection indicator: accent dot right
        dot_x = tab_x0 + TAB_W - 16
        dot_y = ty + TAB_H // 2
        if sel:
            pygame.draw.circle(surf, acc, (dot_x, dot_y), 7)
            pygame.draw.circle(surf, _GOLD_BRIGHT, (dot_x, dot_y), 7, 1)
            ck = [(dot_x - 4, dot_y), (dot_x - 1, dot_y + 3),
                  (dot_x + 4, dot_y - 3)]
            pygame.draw.lines(surf, (20, 16, 8), False, ck, 2)
        else:
            pygame.draw.circle(surf, (28, 26, 42), (dot_x, dot_y), 7)
            pygame.draw.circle(surf, (*acc, 110), (dot_x, dot_y), 7, 1)

    rule_y = tab_y0 + 5 * (TAB_H + TAB_GAP) + 4
    _gold_rule(surf, px0 + 24, p.right - 24, rule_y)
    _buttons(surf, pcx, rule_y + 12)


# =============================================================================
# Render comparison strip
# =============================================================================
DESIGNS = [
    ("DESIGN 1", "CONSTELLATION CARDS", draw_design_1),
    ("DESIGN 2", "SHOWCASE STAGE",       draw_design_2),
    ("DESIGN 3", "VERTICAL COLUMNS",     draw_design_3),
    ("DESIGN 4", "ORBIT ARC",            draw_design_4),
    ("DESIGN 5", "GLASS TABLETS",        draw_design_5),
]

N     = len(DESIGNS)
GAP   = 6
LABEL = 30
TOTAL_W = N * W + (N - 1) * GAP + 40
TOTAL_H = H + LABEL + 16

comparison = pygame.Surface((TOTAL_W, TOTAL_H))
comparison.fill((4, 4, 14))

for i, (d_num, d_name, draw_fn) in enumerate(DESIGNS):
    canvas = scene.copy()
    draw_fn(canvas)
    x_off = 20 + i * (W + GAP)
    comparison.blit(canvas, (x_off, LABEL))

    # Label above panel
    f1 = _font(13, True).render(d_num, True, _GOLD_BRIGHT)
    f2 = _font(11, True).render(d_name, True, UI_CREAM)
    comparison.blit(f1, f1.get_rect(center=(x_off + W // 2, 9)))
    comparison.blit(f2, f2.get_rect(center=(x_off + W // 2, 24)))

    # Thin gold separator
    if i < N - 1:
        sep_x = x_off + W + GAP // 2
        pygame.draw.line(comparison, (*_GOLD_DEEP, 100),
                         (sep_x, LABEL), (sep_x, LABEL + H), 1)

# ── Save ──────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "..", "..",
                   "docs", "store_redesign", "parcels", "ufo",
                   "picker_designs_comparison.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(comparison, out)
print(f"saved → {out}")
