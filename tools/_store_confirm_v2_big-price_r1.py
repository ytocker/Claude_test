#!/usr/bin/env python3
"""store_confirm_popup_v2 — big-price — round 1 render.

The buy-confirmation modal reworked so the PRICE is the hero of the lower
panel. Above y195 the fig-E halo-badge is untouched (card body/bevels, corner
gems, item name, rarity lozenge, overhanging cabochon disc + aura, scrim). The
y195-325 lane is rebuilt: a dominant coin+numeral price cluster, a lit tappable
gold BUY pill, and a quiet CANCEL text button. Two states tile side by side —
AFFORDABLE (left) and UNAFFORDABLE (right) — so the affordability read is legible
at a glance.
"""
import os
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
import game.store as store
import game.store_cards as store_cards
import game.store_catalog as store_catalog
import game.store_data as store_data
from game.store import StoreScene, _draw_qmark, UI_CREAM, NEAR_BLACK
from game.hud import _font

SID = "skin_mummy"


def _padlock(big, cx, cy, s, color):
    """A tiny closed padlock: a rounded body under a horseshoe shackle. Reads as
    'locked' at button scale without needing a label."""
    bw, bh = int(s * 1.5), int(s * 1.1)
    body = pygame.Rect(cx - bw // 2, cy - bh // 4, bw, bh)
    sh_r = int(s * 0.5)
    # shackle arc rides above the body
    pygame.draw.arc(big, color, (cx - sh_r, body.top - sh_r, sh_r * 2, sh_r * 2),
                    math.radians(20), math.radians(160), max(1, store_cards.m(1.4)))
    pygame.draw.rect(big, color, body, border_radius=max(1, store_cards.m(2)))
    # keyhole punched dark so the body reads as metal, not a slab
    pygame.draw.circle(big, (20, 20, 28), body.center, max(1, store_cards.m(1.6)))


def new_draw_confirm(self, surf) -> None:
    """big-price rework of the buy-confirmation modal — hero price cluster,
    lit BUY pill, quiet CANCEL, with everything above y195 preserved."""
    self._confirm_panel = None
    self.confirm_yes_rect = self.confirm_no_rect = None
    sid = self._confirm
    if sid is None:
        return

    scrim = pygame.Surface((W, H), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    surf.blit(scrim, (0, 0))

    secret = store_catalog.is_secret(sid) and not store_data.is_owned(sid)
    tier = store_catalog.rarity(sid)
    pal = (store_cards.MYSTERY if secret
           else store_cards.RARITY.get(tier, store_cards.RARITY["common"]))
    tier_word = "MYSTERY" if secret else tier.upper()
    name = "???" if secret else self._disp_name(sid)
    price = store_catalog.cost(sid)
    affordable = store_data.balance() >= price

    POP_W, POP_H = 200, 340
    CX = POP_W // 2
    SS = store_cards.SS
    m = store_cards.m

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
    NAME_FS, Y_NAME = 30, 155
    Y_BANNER, BANNER_W = 175, 120

    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    # ── card body (unchanged fig-E badge) ─────────────────────────────────────
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    store_cards.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(store_cards.vgrad_stops(
        rect.w, rect.h, rad,
        [(0.0, store_cards.CARD_T), (1.0, store_cards.CARD_B)], 255, gamma=1.15),
        rect.topleft)
    store_cards.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    store_cards.bevel_rim(big, rect, rad, store_cards.CARD_RING_DEEP,
                          (*store_cards.CARD_RING_BRIGHT, 230), w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*store_cards.CARD_RING_BRIGHT, 55), tray,
                     width=max(1, m(1)), border_radius=rad - m(3))

    # ── corner gem pair ───────────────────────────────────────────────────────
    store_cards.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R),
                          pal["gem"], pal["deep"])
    store_cards.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R),
                          pal["gem"], pal["deep"])

    # ── name + rarity lozenge ─────────────────────────────────────────────────
    store_cards.plain_text(big, name, store_cards.font(NAME_FS),
                           (m(CX), m(Y_NAME)), (250, 248, 240),
                           shadow_a=160, weight=m(0.9),
                           keyline=(6, 6, 16), kw=m(1.0))
    store_cards._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # ══ big-price lane (y195-325) ═════════════════════════════════════════════
    # Hero price cluster: a large coin glyph + the price numeral, sized as the
    # loudest type below the item name so cost reads before anything else. The
    # pair is optically centred as a unit around CX so it never lists left/right.
    r_coin = m(18)
    gap = m(4)
    cluster_cy = m(225)
    f_num = store_cards.font(26)
    price_str = f"{price:,}"
    tw = f_num.size(price_str)[0]
    total_w = r_coin * 2 + m(2) + tw
    coin_cx = m(CX) - total_w // 2 + r_coin
    num_center_x = coin_cx + r_coin + gap + tw // 2

    if affordable:
        store_cards.coin_glyph(big, coin_cx, cluster_cy, r_coin)
        store_cards.plain_text(big, price_str, f_num,
                               (num_center_x, cluster_cy), (248, 238, 210),
                               shadow_a=170, weight=m(1.0),
                               keyline=(30, 22, 8), kw=m(1.1))
    else:
        # A genuinely greyed disc + slate numeral + strikethrough so the price
        # reads as out-of-reach, not merely restyled.
        pygame.draw.circle(big, (58, 60, 70), (coin_cx, cluster_cy), r_coin + m(1))
        pygame.draw.circle(big, (104, 108, 120), (coin_cx, cluster_cy), r_coin)
        pygame.draw.circle(big, (132, 136, 148), (coin_cx, cluster_cy), r_coin,
                           max(1, m(1.6)))
        pygame.draw.circle(big, (150, 154, 166),
                           (coin_cx - m(5), cluster_cy - m(5)), m(4))
        store_cards.plain_text(big, price_str, f_num,
                               (num_center_x, cluster_cy), (110, 115, 130),
                               shadow_a=120, weight=m(1.0),
                               keyline=(14, 16, 22), kw=m(1.0))
        sx0 = coin_cx + r_coin + gap - m(1)
        sx1 = num_center_x + tw // 2 + m(1)
        pygame.draw.line(big, (150, 158, 176), (sx0, cluster_cy),
                         (sx1, cluster_cy), max(1, m(2)))
        store_cards.plain_text(big, "NOT ENOUGH", store_cards.font(8),
                               (m(CX), m(248)), (150, 166, 190), shadow_a=0)

    # BUY button — the affirmative action, clearly lit + tappable.
    BTN_W, BTN_H, BTN_CY = 120, 28, 270
    btn = pygame.Rect(m(CX) - m(BTN_W) // 2, m(BTN_CY) - m(BTN_H) // 2,
                      m(BTN_W), m(BTN_H))
    btn_rad = m(BTN_H) // 2
    if affordable:
        # soft outer glow so the primary action pops off the dark card
        glow_r = btn.inflate(m(10), m(10))
        for i in range(m(6), 0, -1):
            a = int(70 * (i / m(6)))
            gs = pygame.Surface(glow_r.size, pygame.SRCALPHA)
            pygame.draw.rect(gs, (210, 170, 70, a),
                             (m(6) - i, m(6) - i,
                              glow_r.w - 2 * (m(6) - i), glow_r.h - 2 * (m(6) - i)),
                             border_radius=btn_rad + i)
            big.blit(gs, glow_r.topleft, special_flags=pygame.BLEND_ADD)
        store_cards._dark_chip_body(
            big, btn, btn_rad,
            [(0.0, (65, 52, 20)), (1.0, (38, 30, 10))],
            (50, 38, 12), (200, 170, 80), gloss=20, gamma=1.05)
        store_cards.top_sheen(big, btn, btn_rad, m(12), peak=70)
        store_cards.plain_text(big, "BUY", store_cards.font(15), btn.center,
                               (252, 244, 224), shadow_a=150, weight=m(1.0),
                               keyline=(28, 18, 4), kw=m(1.0))
    else:
        store_cards._dark_chip_body(
            big, btn, btn_rad,
            [(0.0, (22, 20, 18)), (1.0, (14, 13, 12))],
            (34, 30, 26), (70, 64, 54), gloss=10, gamma=1.04)
        _padlock(big, m(CX), m(BTN_CY), m(10), (128, 132, 148))

    # CANCEL — a quiet text button with a generous hit target.
    store_cards.plain_text(big, "CANCEL", store_cards.font(10),
                           (m(CX), m(308)), (130, 124, 148), shadow_a=0)

    # ── overhanging disc + spotlight halo (crowns the card, unchanged) ─────────
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    store_cards._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), pal["glow"],
                            peak=95, layers=24)
    store_cards._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), pal["glow"],
                            peak=70, layers=12)
    store_cards.cabochon(big, cx_ss, cy_ss, r_ss,
                         store_cards.CABO_LO, store_cards.CABO_HI,
                         ring=pal["gem"], ring_a=50)
    if secret:
        _draw_qmark(big, cx_ss, cy_ss, int(r_ss * 1.17), UI_CREAM, NEAR_BLACK,
                    thick=5)
    else:
        store_cards.blit_thumb(big, sid, cx_ss, cy_ss, int(r_ss * 1.5))
    store_cards.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=pal["gem"])

    # ── downscale + composite ─────────────────────────────────────────────────
    pop = pygame.transform.smoothscale(big, (POP_W, POP_H))
    px = (W - POP_W) // 2
    py = (H - POP_H) // 2
    self._confirm_panel = pygame.Rect(px, py, POP_W, POP_H)
    surf.blit(pop, (px, py))

    self.confirm_no_rect = pygame.Rect(px + CX - 40, py + 300, 80, 32)
    if affordable:
        self.confirm_yes_rect = pygame.Rect(
            px + CX - BTN_W // 2, py + BTN_CY - BTN_H // 2, BTN_W, BTN_H)


StoreScene._draw_confirm = new_draw_confirm


def render_state(balance):
    orig_balance = store_data.balance
    store_data.balance = lambda: balance
    try:
        scene = StoreScene()
        scene._confirm = SID
        surf = pygame.Surface((W, H))
        # opaque scene ground so the additive glows land as in-game
        for y in range(H):
            f = y / H
            c = (int(16 + 4 * f), int(17 + 4 * f), int(34 - 8 * f))
            surf.fill(c, (0, y, W, 1))
        scene._draw_confirm(surf)
        return surf.subsurface(pygame.Rect(80, 150, 200, 340)).copy()
    finally:
        store_data.balance = orig_balance


aff = render_state(999_999)
un = render_state(100)

# ── compose the side-by-side review sheet ─────────────────────────────────────
GAP, MARGIN, TOP = 28, 24, 62
PW, PH = 200, 340
CANVAS_W = MARGIN * 2 + PW * 2 + GAP
CANVAS_H = TOP + PH + 40

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
for y in range(CANVAS_H):
    f = y / CANVAS_H
    canvas.fill((int(14 + 6 * f), int(15 + 6 * f), int(30 - 10 * f)), (0, y, CANVAS_W, 1))

title = _font(20, True).render(
    "store_confirm_popup_v2 - big-price - round 1", True, (226, 228, 242))
canvas.blit(title, title.get_rect(midtop=(CANVAS_W // 2, 14)))
sub = _font(11, False).render(
    "item: skin_mummy (EPIC, 1,100)", True, (150, 154, 176))
canvas.blit(sub, sub.get_rect(midtop=(CANVAS_W // 2, 40)))

lab = _font(13, True)
for i, (panel, tag, col) in enumerate([
        (aff, "AFFORDABLE", (150, 220, 160)),
        (un, "UNAFFORDABLE", (220, 150, 150))]):
    px = MARGIN + i * (PW + GAP)
    canvas.blit(panel, (px, TOP))
    t = lab.render(tag, True, col)
    canvas.blit(t, t.get_rect(midtop=(px + PW // 2, TOP + PH + 10)))

out = "/home/user/skybit/docs/store_confirm_popup_v2/big-price/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())

# ── pixel verification (sampled in the AFFORDABLE crop, popup-local coords) ────
def sample(surf, x, y):
    return tuple(surf.get_at((x, y)))[:3]

# coin center of the hero cluster (logical popup coords ~ y225, coin left of CX)
print("coin center       ", sample(aff, 76, 225))
print("numeral region    ", sample(aff, 118, 225))
print("BUY button center ", sample(aff, 100, 270))
print("un coin center    ", sample(un, 76, 225))
