import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pygame; pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store as store_mod
import game.store_cards as sc
import game.store_data as sd
from game import store_catalog
from game.config import W, H

POP_W, POP_H = 200, 340
PX = (W - POP_W) // 2
PY = (H - POP_H) // 2


def _coin_drop_button(big, affordable):
    """Locked `coin-drop` action button — a single vending pill with a raking
    inset sheen and a proud whole coin on the left, 'BUY' filling the rest.
    Disabled state strikes the coin and drops the whole pill in value."""
    m = sc.m
    CX_D = m(100)
    Y_BTN_D = m(273)
    BTN_H_D = m(30)
    BTN_W_D = m(136)
    btn_x0 = CX_D - BTN_W_D // 2
    btn_y0 = Y_BTN_D - BTN_H_D // 2
    rad = BTN_H_D // 2
    cy = Y_BTN_D
    r = pygame.Rect(btn_x0, btn_y0, BTN_W_D, BTN_H_D)

    if affordable:
        sc._dark_chip_body(big, r, rad,
                           [(0.0, (32, 28, 48)), (1.0, (20, 17, 35))],
                           (15, 12, 28), (110, 100, 145), gloss=30, gamma=1.06)
        sc.bevel_rim(big, r, rad, (55, 48, 80, 220), (140, 128, 175, 200), w=2)
        # Raking inset sheen line — highlight strip suggesting a machined surface.
        sheen_surf = pygame.Surface((BTN_W_D, BTN_H_D), pygame.SRCALPHA)
        sheen_y0 = BTN_H_D // 4
        for sx in range(BTN_W_D - m(4)):
            t = sx / (BTN_W_D - m(4))
            a = int(60 * (1 - abs(t - 0.5) * 2.2))
            if a > 0:
                pygame.draw.line(sheen_surf, (180, 170, 220, a),
                                 (sx + m(2), sheen_y0 - 1),
                                 (sx + m(2), sheen_y0 + 1), 1)
        big.blit(sheen_surf, (btn_x0, btn_y0))
        coin_col = (255, 220, 100)
        label_col = (200, 190, 230)
    else:
        sc._dark_chip_body(big, r, rad,
                           [(0.0, (50, 46, 58)), (1.0, (36, 32, 44))],
                           (26, 24, 34), (75, 70, 88), gloss=8, gamma=1.04)
        sc.bevel_rim(big, r, rad, (46, 42, 56, 180), (95, 88, 110, 150), w=2)
        coin_col = (90, 84, 105)
        label_col = (88, 82, 100)

    # Coin glyph — proud on the pill's left (not sunk), enlarged.
    coin_r = BTN_H_D // 2 - m(5)
    coin_cx = btn_x0 + m(4) + coin_r + m(2)
    coin_cy = cy

    if hasattr(sc, 'coin_glyph'):
        sc.coin_glyph(big, coin_cx, coin_cy, coin_r)
        if not affordable:
            pygame.draw.line(big, (180, 60, 60, 200),
                             (coin_cx - coin_r, coin_cy + coin_r),
                             (coin_cx + coin_r, coin_cy - coin_r),
                             max(2, m(1.5)))
    else:
        pygame.draw.circle(big, coin_col, (coin_cx, coin_cy), coin_r)
        pygame.draw.circle(big, (46, 38, 18), (coin_cx, coin_cy), coin_r, max(1, m(1)))
        sc.plain_text(big, "$", sc.font(8), (coin_cx, coin_cy), (46, 38, 18), shadow_a=0)
        if not affordable:
            pygame.draw.line(big, (180, 60, 60, 200),
                             (coin_cx - coin_r, coin_cy + coin_r),
                             (coin_cx + coin_r, coin_cy - coin_r),
                             max(2, m(1.5)))

    # "BUY" label in the remaining width.
    label_x = coin_cx + coin_r + m(6)
    label_w = btn_x0 + BTN_W_D - label_x
    sc.plain_text(big, "BUY", sc.font(11),
                  (label_x + label_w // 2, cy),
                  label_col, shadow_a=0, weight=m(0.9),
                  tracking=m(1.5))
    return r


def patched_draw_confirm(self, surf):
    """Copy of StoreScene._draw_confirm with only the action button swapped for
    the `coin-drop` pill — every other element stays identical."""
    store_cards = sc
    store_catalog_ = store_catalog
    store_data = sd
    from game.store import _draw_qmark, UI_CREAM, NEAR_BLACK

    self._confirm_panel = None
    self.confirm_yes_rect = self.confirm_no_rect = None
    sid = self._confirm
    if sid is None:
        return

    scrim = pygame.Surface((W, H), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    surf.blit(scrim, (0, 0))

    secret = store_catalog_.is_secret(sid) and not store_data.is_owned(sid)
    tier = store_catalog_.rarity(sid)
    pal = (store_cards.MYSTERY if secret
           else store_cards.RARITY.get(tier, store_cards.RARITY["common"]))
    tier_word = "MYSTERY" if secret else tier.upper()
    name = "???" if secret else self._disp_name(sid)
    price = store_catalog_.cost(sid)
    affordable = store_data.balance() >= price

    POP_W_, POP_H_ = 200, 340
    CX = POP_W_ // 2
    SS = store_cards.SS
    m = store_cards.m

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
    NAME_FS, Y_NAME = 30, 155
    Y_BANNER, BANNER_W = 175, 120
    Y_CHIP, CHIP_H = 229, 28
    Y_BTN, BTN_H, BTN_W = 273, 30, 136
    Y_CANCEL, CANCEL_H, CANCEL_W = 308, 22, 80

    big = pygame.Surface((POP_W_ * SS, POP_H_ * SS), pygame.SRCALPHA)

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

    store_cards.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R),
                          pal["gem"], pal["deep"])
    store_cards.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R),
                          pal["gem"], pal["deep"])

    store_cards.plain_text(big, name, store_cards.font(NAME_FS),
                           (m(CX), m(Y_NAME)), (250, 248, 240),
                           shadow_a=160, weight=m(0.9),
                           keyline=(6, 6, 16), kw=m(1.0))

    store_cards._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    store_cards.price_chip(big, m(CX), m(Y_CHIP), f"{price:,}",
                           m(CHIP_H), affordable=affordable)

    if not affordable:
        store_cards.plain_text(big, "NOT ENOUGH COINS",
                               store_cards.font(9), (m(CX), m(251)),
                               (150, 166, 190), shadow_a=0)

    # ── action button (coin-drop swap) ────────────────────────────────────────
    btn_r = _coin_drop_button(big, affordable)

    h_can = m(CANCEL_H)
    w_can = m(CANCEL_W)
    can_r = pygame.Rect(m(CX) - w_can // 2, m(Y_CANCEL) - h_can // 2,
                        w_can, h_can)
    store_cards._dark_chip_body(big, can_r, h_can // 2,
                                [(0.0, (18, 16, 26)), (1.0, (12, 10, 20))],
                                (30, 28, 42), (70, 66, 82), gloss=14, gamma=1.04)
    store_cards.plain_text(big, "CANCEL", store_cards.font(11),
                           can_r.center, (130, 124, 148), shadow_a=0)

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

    pop = pygame.transform.smoothscale(big, (POP_W_, POP_H_))
    px = (W - POP_W_) // 2
    py = (H - POP_H_) // 2
    self._confirm_panel = pygame.Rect(px, py, POP_W_, POP_H_)
    surf.blit(pop, (px, py))

    self.confirm_no_rect = pygame.Rect(
        px + CX - CANCEL_W // 2, py + Y_CANCEL - CANCEL_H // 2,
        CANCEL_W, CANCEL_H)
    if affordable:
        self.confirm_yes_rect = pygame.Rect(
            px + btn_r.x // SS, py + btn_r.y // SS,
            btn_r.w // SS, btn_r.h // SS)


store_mod.StoreScene._draw_confirm = patched_draw_confirm


def render_popup(sid, bal):
    sd.balance = lambda: bal
    scene = store_mod.StoreScene()
    scene.view = "category"
    scene._confirm = sid
    surf = pygame.Surface((W, H))
    surf.fill((8, 8, 20))
    scene.render(surf)
    crop = pygame.Surface((POP_W, POP_H), pygame.SRCALPHA)
    crop.blit(surf, (0, 0), pygame.Rect(PX, PY, POP_W, POP_H))
    return crop


def main():
    # Paid skin so cost>0 → balance-0 case reads unaffordable.
    ids = sorted(store_catalog.ids_of_group('parrot'), key=store_catalog.cost)
    sid = ids[-1]

    aff = render_popup(sid, 999_999)
    una = render_popup(sid, 0)

    sheet = pygame.Surface((460, 400))
    sheet.fill((8, 8, 20))
    sheet.blit(aff, (0, 30))
    sheet.blit(una, (220, 30))

    hf = pygame.font.Font(None, 22)
    lf = pygame.font.Font(None, 18)
    head = hf.render("coin-drop · VENDING PILL", True, (220, 190, 100))
    sheet.blit(head, (10, 10))
    sheet.blit(lf.render("AFFORDABLE", True, (200, 185, 140)), (30, 380))
    sheet.blit(lf.render("NOT ENOUGH (struck coin)", True, (200, 185, 140)), (232, 380))

    out = os.path.join(os.path.dirname(__file__), "..",
                       "docs", "store_confirm_popup", "coin-drop", "round_1.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
