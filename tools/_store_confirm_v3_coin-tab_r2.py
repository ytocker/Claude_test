#!/usr/bin/env python3
"""
coin-tab  ·  store buy-confirmation popup v3  ·  round 2

R2 punch list:
  1. Price numeral flipped to dark espresso (52,28,4) on cream — ~10:1 contrast,
     slim light lower-edge keyline for deboss feel instead of compensating dark halo.
  2. Tab drop-shadow removed — the unified rim fuses tab to bar; a cast shadow
     makes it look floating rather than notched in.
  3. Shared continuous 1px (120,74,14) amber rim running from tab top-left arc
     down the left sides, along the bar bottom, up the right sides, and back up to
     the tab top-right arc — the two pieces now read as one moulded object.
  4. BUY-side channel lip warmed to gold (220,180,100) when BUY is active; the
     groove reads as moulded from gold, not painted over it. CANCEL lip stays cool.
  5. 1px dark (80,52,12) outer ring added around the coin before the glyph is
     drawn — coin pops off the cream face cleanly.
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


def _half_bar(big, bar, brad, left_stops, right_stops):
    """BUY + CANCEL as one rounded bar: two flat-cornered gradient halves cut
    to a shared rounded-rect mask so the pair reads as a single object with
    common outer corners, split only by the centre channel drawn later."""
    bw, bh = bar.w, bar.h
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    left = sc.vgrad_stops(bw, bh, 0, left_stops, 255, gamma=1.06)
    right = sc.vgrad_stops(bw, bh, 0, right_stops, 255, gamma=1.04)
    half = bw // 2
    surf.blit(left, (0, 0), area=pygame.Rect(0, 0, half, bh))
    surf.blit(right, (half, 0), area=pygame.Rect(half, 0, bw - half, bh))
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, bw, bh), border_radius=brad)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(surf, bar.topleft)


def _channel(big, cx_d, y0, y1, affordable=True):
    """Recessed vertical bevel channel dividing BUY from CANCEL: a dark valley
    with a bright lip on each side. The BUY-side lip (left of centre) is warm
    gold when BUY is active so the groove reads as moulded from the cell's own
    material; the CANCEL-side lip stays cool purple-grey regardless."""
    lip = max(1, sc.m(1))
    val = max(2, sc.m(2.5))
    off = sc.m(1.8)
    buy_lip = (220, 180, 100) if affordable else (60, 58, 80)
    pygame.draw.line(big, buy_lip,    (cx_d - off, y0), (cx_d - off, y1), lip)
    pygame.draw.line(big, (60, 58, 80), (cx_d + off, y0), (cx_d + off, y1), lip)
    pygame.draw.line(big, (8, 8, 16),  (cx_d, y0),       (cx_d, y1),       val)


def _tab_face(big, tab, top_stops, r_top, border_col):
    """Folder-tab price container: top-rounded corners, near-square bottom that
    overlaps 2 px into the bar so the meeting edge disappears. Border is drawn
    open at the bottom (top + two sides + top corners only) so nothing scores a
    seam line across the join into the bar below."""
    tw, th = tab.w, tab.h
    grad = sc.vgrad_stops(tw, th, 0, top_stops, 255, gamma=1.03)
    surf = pygame.Surface((tw, th), pygame.SRCALPHA)
    surf.blit(grad, (0, 0))
    mask = pygame.Surface((tw, th), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, tw, th),
                     border_top_left_radius=r_top, border_top_right_radius=r_top,
                     border_bottom_left_radius=sc.m(2),
                     border_bottom_right_radius=sc.m(2))
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(surf, tab.topleft)
    sc.top_sheen(big, tab, r_top, sc.m(12), peak=26)

    lw = max(1, sc.m(1))
    x0, y0, x1, y1 = tab.left, tab.top, tab.right, tab.bottom
    r = r_top
    pygame.draw.line(big, border_col, (x0 + r, y0), (x1 - r, y0), lw)
    pygame.draw.line(big, border_col, (x0, y0 + r), (x0, y1), lw)
    pygame.draw.line(big, border_col, (x1, y0 + r), (x1, y1), lw)
    pygame.draw.arc(big, border_col, pygame.Rect(x0, y0, 2 * r, 2 * r),
                    math.pi / 2, math.pi, lw)
    pygame.draw.arc(big, border_col, pygame.Rect(x1 - 2 * r, y0, 2 * r, 2 * r),
                    0, math.pi / 2, lw)


def _unified_rim(big, tab, bar, brad, tab_rad, rim_col):
    """One continuous 1px keyline tracing the outer silhouette of tab + bar —
    tab top-left arc, down left side of tab, across exposed bar top-left,
    bar left side, bar bottom, bar right side, across exposed bar top-right,
    up right side of tab to its top-right arc — so the two shapes read as one
    moulded object rather than two pieces resting against each other."""
    lw = max(1, sc.m(1))
    r = brad

    # Tab side walls continued down to the bar's top edge
    pygame.draw.line(big, rim_col,
                     (tab.left,  tab.top + tab_rad),
                     (tab.left,  bar.top), lw)
    pygame.draw.line(big, rim_col,
                     (tab.right, tab.top + tab_rad),
                     (tab.right, bar.top), lw)

    # Exposed bar-top segments (between bar corner radius and tab edges)
    pygame.draw.line(big, rim_col,
                     (bar.left + r, bar.top),
                     (tab.left,     bar.top), lw)
    pygame.draw.line(big, rim_col,
                     (tab.right,    bar.top),
                     (bar.right - r, bar.top), lw)

    # Bar left and right verticals
    pygame.draw.line(big, rim_col,
                     (bar.left, bar.top    + r),
                     (bar.left, bar.bottom - r), lw)
    pygame.draw.line(big, rim_col,
                     (bar.right, bar.top    + r),
                     (bar.right, bar.bottom - r), lw)

    # Bar bottom horizontal
    pygame.draw.line(big, rim_col,
                     (bar.left  + r, bar.bottom),
                     (bar.right - r, bar.bottom), lw)

    # Bar corner arcs — same angle convention as _tab_face top-corner arcs
    pygame.draw.arc(big, rim_col,
                    pygame.Rect(bar.left, bar.top, r * 2, r * 2),
                    math.pi / 2, math.pi, lw)                         # top-left
    pygame.draw.arc(big, rim_col,
                    pygame.Rect(bar.right - r * 2, bar.top, r * 2, r * 2),
                    0, math.pi / 2, lw)                                # top-right
    pygame.draw.arc(big, rim_col,
                    pygame.Rect(bar.left, bar.bottom - r * 2, r * 2, r * 2),
                    math.pi, math.pi * 3 / 2, lw)                     # bottom-left
    pygame.draw.arc(big, rim_col,
                    pygame.Rect(bar.right - r * 2, bar.bottom - r * 2, r * 2, r * 2),
                    math.pi * 3 / 2, math.pi * 2, lw)                 # bottom-right


def _coin_numeral(big, cx_d, cy_d, price, affordable):
    """Coin glyph + price numeral centred together on the tab face."""
    txt = f"{price:,}"
    coin_r = sc.m(13)
    coin_d = coin_r * 2
    gap = sc.m(4)
    num_font = sc.font(20)
    num_w = num_font.render(txt, True, (255, 255, 255)).get_width()
    total = coin_d + gap + num_w
    left = cx_d - total // 2
    coin_cx = left + coin_r
    num_cx = left + coin_d + gap + num_w // 2

    if affordable:
        # Dark outer ring before the coin fill so it pops off the cream face
        pygame.draw.circle(big, (80, 52, 12), (coin_cx, cy_d),
                           coin_r + max(1, sc.m(1)), width=max(1, sc.m(1)))
        sc.coin_glyph(big, coin_cx, cy_d, coin_r)
        # Espresso numeral on cream — ~10:1 contrast; a slim pale lower-edge
        # keyline gives a deboss feel rather than a heavy compensating halo
        sc.plain_text(big, txt, num_font, (num_cx, cy_d), (52, 28, 4),
                      shadow_a=0, weight=sc.m(0.9),
                      keyline=(255, 244, 220), kw=sc.m(0.6))
    else:
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy_d), coin_r)
        pygame.draw.circle(big, (96, 100, 114), (coin_cx, cy_d), coin_r,
                           width=max(1, sc.m(1)))
        pygame.draw.circle(big, (122, 126, 140), (coin_cx, cy_d),
                           coin_r - sc.m(2), width=max(1, sc.m(1)))
        sc.plain_text(big, txt, num_font, (num_cx, cy_d), (110, 115, 130),
                      shadow_a=0, weight=sc.m(0.6),
                      keyline=(22, 22, 30), kw=sc.m(1.0))


def _padlock(big, cx, cy):
    """Padlock in the inert BUY cell — dark keyline + body so the silhouette
    reads as a lock at 1x screen size."""
    pk_w, pk_h = sc.m(15), sc.m(13)
    body_r = pygame.Rect(cx - pk_w // 2, cy - pk_h // 2 + sc.m(2),
                         pk_w, pk_h - sc.m(3))
    pygame.draw.rect(big, (26, 24, 34), body_r.inflate(sc.m(2), sc.m(2)),
                     border_radius=sc.m(4))
    pygame.draw.rect(big, (108, 110, 128, 230), body_r, border_radius=sc.m(3))
    pygame.draw.rect(big, (58, 60, 76, 255), body_r, width=max(1, sc.m(1)),
                     border_radius=sc.m(3))
    sh_r = pk_w // 2 - sc.m(1)
    arc = pygame.Rect(cx - sh_r, cy - pk_h // 2 - sh_r + sc.m(2), sh_r * 2, sh_r * 2)
    pygame.draw.arc(big, (26, 24, 34), arc.inflate(sc.m(2), sc.m(2)),
                    0, math.pi, max(2, sc.m(3)))
    pygame.draw.arc(big, (108, 110, 128, 220), arc, 0, math.pi, max(2, sc.m(2.5)))
    pygame.draw.circle(big, (52, 54, 68, 255), (cx, cy + sc.m(1)), max(2, sc.m(2.2)))


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

    # ── coin-tab concept metrics (logical) ────────────────────────────────────
    BAR_W, BAR_H, BAR_RAD = 168, 40, 10
    BTN_TOP, BTN_BOT = 250, 290
    BAR_L = CX - BAR_W // 2               # 16
    BUY_CX = BAR_L + BAR_W // 4           # 58
    CAN_CX = BAR_L + (BAR_W * 3) // 4     # 142
    BTN_CY = (BTN_TOP + BTN_BOT) // 2     # 270

    TAB_W, TAB_H, TAB_TOP, TAB_RAD = 96, 42, 210, 8
    TAB_CY = 231
    HIT_H = 40

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

    # ── connected object: BUY|CANCEL bar + folder-tab price container ─────────
    bar = pygame.Rect(m(BAR_L), m(BTN_TOP), m(BAR_W), m(BAR_H))
    brad = m(BAR_RAD)
    sc.drop_shadow(big, bar, brad, blur=m(6), alpha=145, dy=m(3))

    if affordable:
        _half_bar(big, bar, brad, sc.GOLD_A_STOPS,
                  [(0.0, (30, 28, 44)), (1.0, (20, 18, 32))])
        sc.top_sheen(big, bar, brad, m(14), peak=52)
        pygame.draw.rect(big, (14, 11, 4), bar, width=max(1, m(1)), border_radius=brad)
        sc.bevel_rim(big, bar, brad, (40, 28, 8, 220),
                     (255, 232, 162, 220), w=max(1, m(1.5)))
    else:
        _half_bar(big, bar, brad, [(0.0, (42, 40, 50)), (1.0, (28, 26, 36))],
                  [(0.0, (30, 28, 44)), (1.0, (20, 18, 32))])
        sc.top_sheen(big, bar, brad, m(14), peak=16)
        pygame.draw.rect(big, (12, 12, 18), bar, width=max(1, m(1)), border_radius=brad)
        sc.bevel_rim(big, bar, brad, (34, 32, 44, 200),
                     (96, 94, 112, 180), w=max(1, m(1.4)))

    _channel(big, m(CX), m(BTN_TOP) + m(3), m(BTN_BOT) - m(3), affordable)

    if affordable:
        sc.plain_text(big, "BUY", sc.font(13), (m(BUY_CX), m(BTN_CY)),
                      (52, 28, 4), shadow_a=90, weight=m(0.9),
                      keyline=(255, 236, 176), kw=m(0.9))
    else:
        sc.plain_text(big, "BUY", sc.font(13),
                      (m(BUY_CX - 9), m(BTN_CY)), (96, 100, 116),
                      shadow_a=0, weight=m(0.5))
        _padlock(big, m(BUY_CX + 15), m(BTN_CY))
    sc.plain_text(big, "CANCEL", sc.font(11), (m(CAN_CX), m(BTN_CY)),
                  (130, 124, 148), shadow_a=0, weight=m(0.6))

    # folder-tab — drop-shadow removed so the tab reads as notched into the
    # bar rather than floating above it; the unified rim below carries the edge
    tab = pygame.Rect(m(CX - TAB_W // 2), m(TAB_TOP), m(TAB_W), m(TAB_H))
    if affordable:
        _tab_face(big, tab, [(0.0, (235, 220, 175)), (1.0, (205, 190, 145))],
                  m(TAB_RAD), (120, 74, 14))
        rim_col = (120, 74, 14)
    else:
        _tab_face(big, tab, [(0.0, (52, 52, 64)), (1.0, (34, 34, 46))],
                  m(TAB_RAD), (58, 60, 76))
        rim_col = (58, 60, 76)

    # One continuous outer keyline fuses the tab sides into the bar contour
    _unified_rim(big, tab, bar, brad, m(TAB_RAD), rim_col)

    _coin_numeral(big, m(CX), m(TAB_CY), price, affordable)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(9), (m(CX), m(308)),
                      (150, 166, 190), shadow_a=0)

    # ── overhanging disc + spotlight halo (drawn last) ─────────────────────────
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), pal["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    if secret:
        _draw_qmark(big, cx_ss, cy_ss, int(r_ss * 1.17), UI_CREAM, NEAR_BLACK, thick=5)
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
        px + BAR_L, py + BTN_TOP, BAR_W // 2, HIT_H)
    self.confirm_no_rect = pygame.Rect(
        px + BAR_L + BAR_W // 2, py + BTN_TOP, BAR_W // 2, HIT_H)
    if not affordable:
        self.confirm_yes_rect = None


store_mod.StoreScene._draw_confirm = _patched_draw_confirm


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


afford_img = render_state(True)
unafford_img = render_state(False)

SHEET_W, SHEET_H = 460, 400
sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill((8, 8, 20))
sheet.blit(_pil_to_surf(afford_img), (0, 30))
sheet.blit(_pil_to_surf(unafford_img), (220, 30))

hdr = store_mod._font(16, True).render(
    "coin-tab R2 · DARK NUMERAL + FUSED AMBER RIM",
    True, (220, 190, 100))
sheet.blit(hdr, hdr.get_rect(midtop=(SHEET_W // 2, 8)))

lbl_font = store_mod._font(12, True)
la = lbl_font.render("AFFORDABLE", True, (200, 185, 140))
lu = lbl_font.render("UNAFFORDABLE", True, (200, 185, 140))
sheet.blit(la, la.get_rect(midtop=(100, 378)))
sheet.blit(lu, lu.get_rect(midtop=(320, 378)))

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_popup_v3", "coin-tab", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print("saved", OUT, sheet.get_size())
