#!/usr/bin/env python3
"""
arch-panel  ·  store buy-confirmation popup v3  ·  round 2

Concept: the price sits inside a genuine Romanesque tombstone arch —
a smooth continuous half-ellipse arc (left spring → apex → right spring)
over straight indigo jambs.  R2 replaces the R1 corner-radius rectangle
with a real polygon + trigonometric arc so the top has zero flat plateau.

Why cool indigo, not warm brown: the card body + gems are already jewel-cool;
a warm plate fights them.  The single gold BUY pill owns all the warmth.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from PIL import Image

import game.store as store_mod
import game.store_cards as sc
import game.store_data as sd
import game.store_catalog as store_catalog
from game.config import W, H

_draw_qmark = store_mod._draw_qmark
UI_CREAM = store_mod.UI_CREAM
NEAR_BLACK = store_mod.NEAR_BLACK


# ── arch geometry helpers ─────────────────────────────────────────────────────

def _arch_polygon(cx_d, half_w_d, spring_d, apex_d, base_d, n=40):
    """
    Device-px tombstone polygon: a half-ellipse cap (left spring → apex →
    right spring) joined to straight rectangular jambs (spring → base).
    The ellipse has its centre at (cx_d, spring_d) so spring_d is the bottom
    of the visible cap — guaranteeing continuity with the vertical jamb edges.
    n=40 gives a smooth arc that resolves cleanly after the SS downscale.
    """
    ry = spring_d - apex_d
    pts = []
    for i in range(n + 1):
        angle = math.pi * i / n          # 0 (left spring) → π (right spring)
        ax = cx_d + int(half_w_d * math.cos(math.pi - angle))
        ay = spring_d - int(ry * math.sin(angle))
        pts.append((ax, ay))
    pts += [(cx_d + half_w_d, base_d), (cx_d - half_w_d, base_d)]
    return pts


def _arch_highlight_arc(big, cx_d, half_w_d, spring_d, apex_d, n=40):
    """
    Thin cool arc tracing the inner arch edge — a masonry lip catching
    overhead light so the niche reads as physically recessed rather than
    painted flat.  Drawn on a separate SRCALPHA surface so the
    semi-transparent colour composites cleanly over the gradient face.
    """
    inset = max(1, sc.m(2))
    half_w_i = half_w_d - inset
    ry_i = (spring_d - apex_d) - inset

    hl_pts = []
    for i in range(n + 1):
        angle = math.pi * i / n
        ax = cx_d + int(half_w_i * math.cos(math.pi - angle))
        ay = spring_d - int(ry_i * math.sin(angle))
        hl_pts.append((ax, ay))

    hl_surf = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.lines(hl_surf, (60, 58, 80, 80), False, hl_pts,
                      max(1, sc.m(1.3)))
    big.blit(hl_surf, (0, 0))


# ── price cluster ─────────────────────────────────────────────────────────────

def _price_in_arch(big, cx_d, cy_d, price, affordable):
    """Coin glyph + numeral centred together at the jamb-zone midpoint."""
    txt = f"{price:,}"
    coin_r = sc.m(14)
    coin_d = coin_r * 2
    gap = sc.m(5)
    num_font = sc.font(20)
    num_w = num_font.render(txt, True, (255, 255, 255)).get_width()
    total = coin_d + gap + num_w
    left = cx_d - total // 2
    coin_cx = left + coin_r
    num_cx = left + coin_d + gap + num_w // 2

    if affordable:
        sc.coin_glyph(big, coin_cx, cy_d, coin_r)
        sc.plain_text(big, txt, num_font, (num_cx, cy_d), (248, 238, 210),
                      shadow_a=150, weight=sc.m(1.0),
                      keyline=(12, 10, 22), kw=sc.m(1.1))
    else:
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy_d), coin_r)
        pygame.draw.circle(big, (108, 112, 126), (coin_cx, cy_d), coin_r,
                           width=max(1, sc.m(1.4)))
        pygame.draw.circle(big, (124, 128, 142), (coin_cx, cy_d),
                           coin_r - sc.m(3), width=max(1, sc.m(1)))
        sc.plain_text(big, txt, num_font, (num_cx, cy_d), (110, 115, 130),
                      shadow_a=0, weight=sc.m(0.7),
                      keyline=(18, 16, 26), kw=sc.m(1.0))


# ── padlock badge ─────────────────────────────────────────────────────────────

def _padlock(big, cx, cy):
    """Padlock badge for the inert BUY pill — 1 px keyline so the silhouette
    reads at 1x screen scale."""
    pk_w, pk_h = sc.m(15), sc.m(13)
    body_r = pygame.Rect(cx - pk_w // 2, cy - pk_h // 2 + sc.m(2),
                         pk_w, pk_h - sc.m(3))
    pygame.draw.rect(big, (24, 24, 34), body_r.inflate(sc.m(2), sc.m(2)),
                     border_radius=sc.m(4))
    pygame.draw.rect(big, (104, 108, 126, 230), body_r, border_radius=sc.m(3))
    pygame.draw.rect(big, (54, 56, 72, 255), body_r, width=max(1, sc.m(1)),
                     border_radius=sc.m(3))
    sh_r = pk_w // 2 - sc.m(1)
    arc = pygame.Rect(cx - sh_r, cy - pk_h // 2 - sh_r + sc.m(2),
                      sh_r * 2, sh_r * 2)
    pygame.draw.arc(big, (24, 24, 34), arc.inflate(sc.m(2), sc.m(2)),
                    0, 3.14159, max(2, sc.m(3)))
    pygame.draw.arc(big, (104, 108, 126, 220), arc, 0, 3.14159, max(2, sc.m(2.5)))
    pygame.draw.circle(big, (48, 50, 66, 255),
                       (cx, cy + sc.m(1)), max(2, sc.m(2.0)))


# ── patched confirm draw ──────────────────────────────────────────────────────

def _patched_draw_confirm(self, surf):
    self._confirm_panel = None
    self.confirm_yes_rect = self.confirm_no_rect = None
    sid = self._confirm
    if sid is None:
        return

    scrim = pygame.Surface((W, H), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    surf.blit(scrim, (0, 0))

    secret = store_catalog.is_secret(sid) and not sd.is_owned(sid)
    tier = store_catalog.rarity(sid)
    pal = (sc.MYSTERY if secret
           else sc.RARITY.get(tier, sc.RARITY["common"]))
    tier_word = "MYSTERY" if secret else tier.upper()
    name = "???" if secret else self._disp_name(sid)
    price = store_catalog.cost(sid)
    affordable = sd.balance() >= price

    POP_W, POP_H = 200, 340
    CX = POP_W // 2
    m = sc.m

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
    NAME_FS, Y_NAME = 30, 155
    Y_BANNER, BANNER_W = 175, 120

    # ── genuine tombstone arch metrics (logical px) ───────────────────────────
    # Elliptic cap: centre at (CX, SPRING_Y), rx=ARCH_W//2, ry=SPRING_Y-ARCH_APEX.
    # The visible portion is the UPPER half of the ellipse, so the cap peaks at
    # ARCH_APEX and meets the jambs tangentially at SPRING_Y — zero flat plateau.
    ARCH_W    = 130
    ARCH_APEX = 196   # top of arch (ellipse apex)
    SPRING_Y  = 230   # springline: where cap meets vertical jambs
    ARCH_BOT  = 252   # bottom of panel
    # Price at the midpoint of the straight jamb zone guarantees ≥6 px clearance
    # between the numeral's ascender and the inner arch rim after downscale.
    ARCH_CY   = (SPRING_Y + ARCH_BOT) // 2   # 241

    ARCH_L = CX - ARCH_W // 2   # 35

    cx_d      = m(CX)
    half_w_d  = m(ARCH_W // 2)          # 130 device px  (SS=2)
    apex_d    = m(ARCH_APEX)
    spring_d  = m(SPRING_Y)
    base_d    = m(ARCH_BOT)
    arch_surf_w = half_w_d * 2          # 260 device px
    arch_surf_h = base_d - apex_d       # 112 device px

    # ── two matched pills ─────────────────────────────────────────────────────
    BTN_W, BTN_H, BTN_RAD = 80, 34, 9
    BTN_TOP, BTN_BOT = 266, 300
    BTN_CY = (BTN_TOP + BTN_BOT) // 2   # 283
    PAIR_GAP = 8
    PAIR_W = BTN_W + PAIR_GAP + BTN_W
    PAIR_L = CX - PAIR_W // 2
    BUY_CX = PAIR_L + BTN_W // 2
    CAN_CX = PAIR_L + BTN_W + PAIR_GAP + BTN_W // 2
    HIT_H = 34

    big = pygame.Surface((POP_W * sc.SS, POP_H * sc.SS), pygame.SRCALPHA)

    # ── card body ─────────────────────────────────────────────────────────────
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(sc.vgrad_stops(
        rect.w, rect.h, rad,
        [(0.0, sc.CARD_T), (1.0, sc.CARD_B)], 255, gamma=1.15),
        rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT, 230), w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*sc.CARD_RING_BRIGHT, 55), tray,
                     width=max(1, m(1)), border_radius=rad - m(3))

    # ── corner gem pair ───────────────────────────────────────────────────────
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])

    # ── name ──────────────────────────────────────────────────────────────────
    sc.plain_text(big, name, sc.font(NAME_FS),
                  (m(CX), m(Y_NAME)), (250, 248, 240),
                  shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))

    # ── rarity banner ─────────────────────────────────────────────────────────
    sc._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # ── genuine tombstone arch: price niche ───────────────────────────────────
    arch_pts = _arch_polygon(cx_d, half_w_d, spring_d, apex_d, base_d)
    arch_origin = (cx_d - half_w_d, apex_d)   # top-left of arch bounding box

    if affordable:
        face_stops = [(0.0, (30, 26, 44)), (1.0, (20, 18, 34))]
        rim_dark   = (10, 9, 20)
        rim_bright = (56, 54, 78, 200)
    else:
        face_stops = [(0.0, (32, 30, 44)), (1.0, (20, 18, 32))]
        rim_dark   = (12, 11, 20)
        rim_bright = (50, 50, 66, 190)

    # soft shadow under the arch using its bounding rect
    arch_bnd = pygame.Rect(arch_origin[0], arch_origin[1],
                           arch_surf_w, arch_surf_h)
    sc.drop_shadow(big, arch_bnd, m(28), blur=m(5), alpha=130, dy=m(2))

    # vertical gradient fill, clipped to the arch polygon via an alpha mask —
    # the polygon replaces the old border_radius rect so the top is truly curved
    face_surf = sc.vgrad_stops(arch_surf_w, arch_surf_h, 0,
                               face_stops, 255, gamma=1.05)
    poly_mask = pygame.Surface((arch_surf_w, arch_surf_h), pygame.SRCALPHA)
    local_pts = [(x - arch_origin[0], y - arch_origin[1]) for x, y in arch_pts]
    pygame.draw.polygon(poly_mask, (255, 255, 255, 255), local_pts)
    face_surf.blit(poly_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(face_surf, arch_origin)

    # arc highlight traces the inner edge of the real arch curve
    _arch_highlight_arc(big, cx_d, half_w_d, spring_d, apex_d)

    # keyline: dark outer outline + bright inner bevel, both following arch polygon
    pygame.draw.polygon(big, (*rim_dark, 255), arch_pts,
                        width=max(2, m(1.4)))
    rim_surf = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(rim_surf, rim_bright, arch_pts, width=max(1, m(1)))
    big.blit(rim_surf, (0, 0))

    # price at jamb-zone centre (SPRING_Y + ARCH_BOT) / 2 = 241 logical
    _price_in_arch(big, m(CX), m(ARCH_CY), price, affordable)

    # ── BUY + CANCEL matched pills ────────────────────────────────────────────
    buy_r = pygame.Rect(m(BUY_CX - BTN_W // 2), m(BTN_CY - BTN_H // 2),
                        m(BTN_W), m(BTN_H))
    can_r = pygame.Rect(m(CAN_CX - BTN_W // 2), m(BTN_CY - BTN_H // 2),
                        m(BTN_W), m(BTN_H))
    brad = m(BTN_RAD)

    if affordable:
        sc._dark_chip_body(big, buy_r, brad, sc.GOLD_A_STOPS,
                           sc.GOLD_A_RIM_DARK, sc.GOLD_A_RIM_BRIGHT,
                           gloss=54, gamma=1.06)
        sc.top_sheen(big, buy_r, brad, m(15), peak=54)
        sc.bevel_rim(big, buy_r, brad, (86, 50, 8, 220),
                     (255, 240, 190, 230), w=max(1, m(1.5)))
        sc.plain_text(big, "BUY", sc.font(13), buy_r.center, (52, 28, 4),
                      shadow_a=0, weight=m(1.0),
                      keyline=(255, 236, 176), kw=m(0.8))
    else:
        sc._dark_chip_body(big, buy_r, brad,
                           [(0.0, (42, 40, 50)), (1.0, (28, 26, 36))],
                           (20, 18, 26), (78, 76, 92), gloss=10, gamma=1.04)
        sc.bevel_rim(big, buy_r, brad, (34, 32, 44, 180),
                     (86, 84, 102, 150), w=max(1, m(1.4)))
        sc.plain_text(big, "BUY", sc.font(13),
                      (buy_r.centerx - m(11), buy_r.centery), (96, 100, 116),
                      shadow_a=0, weight=m(0.5))
        _padlock(big, buy_r.centerx + m(16), buy_r.centery)

    # CANCEL — matched slate pill, always available
    sc._dark_chip_body(big, can_r, brad,
                       [(0.0, (30, 28, 44)), (1.0, (20, 18, 32))],
                       (12, 11, 22), (74, 70, 92), gloss=18, gamma=1.04)
    sc.plain_text(big, "CANCEL", sc.font(11), can_r.center, (130, 124, 148),
                  shadow_a=0, weight=m(0.6))

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(8), (m(CX), m(310)),
                      (150, 166, 190), shadow_a=0)

    # ── overhanging disc + spotlight halo (drawn LAST so it overhangs) ────────
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), pal["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    if secret:
        _draw_qmark(big, cx_ss, cy_ss, int(r_ss * 1.17), UI_CREAM, NEAR_BLACK,
                    thick=5)
    else:
        sc.blit_thumb(big, sid, cx_ss, cy_ss, int(r_ss * 1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=pal["gem"])

    # ── downscale + composite ─────────────────────────────────────────────────
    pop = pygame.transform.smoothscale(big, (POP_W, POP_H))
    px = (W - POP_W) // 2
    py = (H - POP_H) // 2
    self._confirm_panel = pygame.Rect(px, py, POP_W, POP_H)
    surf.blit(pop, (px, py))

    self.confirm_yes_rect = pygame.Rect(
        px + BUY_CX - BTN_W // 2, py + BTN_CY - HIT_H // 2, BTN_W, HIT_H)
    self.confirm_no_rect = pygame.Rect(
        px + CAN_CX - BTN_W // 2, py + BTN_CY - HIT_H // 2, BTN_W, HIT_H)
    if not affordable:
        self.confirm_yes_rect = None


store_mod.StoreScene._draw_confirm = _patched_draw_confirm


# ── render both states ────────────────────────────────────────────────────────

def render_state(affordable):
    sd.load()
    sd.balance = (lambda: 999_999) if affordable else (lambda: 0)
    sc.clear_cache()
    scene = store_mod.StoreScene()
    scene.view = "category"
    scene._confirm = "skin_mummy"
    screen = pygame.Surface((W, H))
    screen.fill((6, 7, 18))
    scene.render(screen)

    POP_W, POP_H = 200, 340
    px, py = (W - POP_W) // 2, (H - POP_H) // 2
    raw = pygame.image.tostring(screen, "RGB")
    full = Image.frombytes("RGB", (W, H), raw)
    return full.crop((px, py, px + POP_W, py + POP_H))


def _pil_to_surf(img):
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)


afford_img  = render_state(True)
unafford_img = render_state(False)

# ── composite review sheet ────────────────────────────────────────────────────

SHEET_W, SHEET_H = 460, 400
sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill((8, 8, 20))
sheet.blit(_pil_to_surf(afford_img),   (0,   30))
sheet.blit(_pil_to_surf(unafford_img), (220, 30))

hdr = store_mod._font(16, True).render(
    "arch-panel R2 · REAL ARC · COOL INDIGO NICHE + MATCHED PILLS",
    True, (150, 160, 210))
sheet.blit(hdr, hdr.get_rect(midtop=(SHEET_W // 2, 8)))

lbl_font = store_mod._font(12, True)
la = lbl_font.render("AFFORDABLE",   True, (180, 185, 210))
lu = lbl_font.render("UNAFFORDABLE", True, (180, 185, 210))
sheet.blit(la, la.get_rect(midtop=(100, 378)))
sheet.blit(lu, lu.get_rect(midtop=(320, 378)))

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_popup_v3", "arch-panel", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print("saved", OUT, sheet.get_size())
