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
    """Coin-drop vending pill: a machined coin-slot is cut into the top center;
    a coin hovers at the opening, half above / half inside the pill — the arcade
    vending machine metaphor. 'BUY & EQUIP' centers in the pill body below."""
    m = sc.m
    CX_D = m(100)
    Y_BTN_D = m(273)
    BTN_H_D = m(30)
    BTN_W_D = m(136)
    btn_x0 = CX_D - BTN_W_D // 2
    btn_y0 = Y_BTN_D - BTN_H_D // 2
    rad = BTN_H_D // 2
    r = pygame.Rect(btn_x0, btn_y0, BTN_W_D, BTN_H_D)

    # PILL BODY — dark enamel.  Affordable reads warmer + marginally brighter;
    # disabled is flat dimmed enamel with no sheen.
    if affordable:
        sc._dark_chip_body(big, r, rad,
                           [(0.0, (36, 32, 52)), (1.0, (22, 19, 38))],
                           (18, 15, 32), (120, 110, 155), gloss=35, gamma=1.06)
        sc.bevel_rim(big, r, rad, (55, 48, 80, 220), (140, 128, 175, 200), w=2)
        # Warm amber sheen near the pill crown — suggests a lit metal surface,
        # removes the violet sheen from Round 1.
        sheen_surf = pygame.Surface((BTN_W_D, BTN_H_D), pygame.SRCALPHA)
        sheen_y = BTN_H_D // 4
        for sx in range(BTN_W_D - m(4)):
            t = sx / max(1, BTN_W_D - m(4))
            a = int(55 * (1 - abs(t - 0.5) * 2.2))
            if a > 0:
                pygame.draw.line(sheen_surf, (210, 185, 120, a),
                                 (sx + m(2), sheen_y - 1),
                                 (sx + m(2), sheen_y + 1), 1)
        big.blit(sheen_surf, (btn_x0, btn_y0))
        label_col = (236, 202, 116)   # Skybit gold — warm, not violet
    else:
        sc._dark_chip_body(big, r, rad,
                           [(0.0, (50, 46, 58)), (1.0, (36, 32, 44))],
                           (26, 24, 34), (75, 70, 88), gloss=8, gamma=1.04)
        sc.bevel_rim(big, r, rad, (46, 42, 56, 180), (95, 88, 110, 150), w=2)
        label_col = (88, 82, 100)

    # COIN SLOT — the defining feature of this concept.
    # A rounded-rect well pressed into the pill's top center after the chip body
    # is rendered, so it carves cleanly through all enamel layers.
    # Dark fill = machine-oil well.  Warm lip on the inner top edge = polished
    # machined rim that reads as a deliberate opening, not a chip in the paint.
    #
    # Width is set wider than the coin diameter (coin_r * 2 = m(20)) so the dark
    # slot opening is visible on both sides of the coin; if the slot were narrower
    # the coin would cover it entirely and the slot would disappear from the image.
    slot_w = m(26)          # ~4 logical px wider per side than the coin diameter
    slot_h = m(8)
    slot_x = CX_D - slot_w // 2
    slot_y = btn_y0
    slot_rad = m(3)
    pygame.draw.rect(big, (8, 7, 15),
                     pygame.Rect(slot_x, slot_y, slot_w, slot_h),
                     border_radius=slot_rad)
    # Bright lip: a thin strip at the very inside top of the slot — the
    # polished edge that catches the light at the slot's machined mouth.
    lip_y = slot_y + max(2, m(1))
    pygame.draw.line(big, (60, 55, 45),
                     (slot_x + slot_rad + 1, lip_y),
                     (slot_x + slot_w - slot_rad - 1, lip_y),
                     max(2, m(1)))

    # COIN poised at the slot mouth.
    # Center exactly at the pill's top edge — half above, half inside — as
    # though a player is pressing it into the slot.
    # Drawn AFTER the slot so the coin correctly overlaps the opening.
    coin_r = m(10)
    coin_cx = CX_D
    coin_cy = btn_y0   # pill top edge

    if affordable:
        # Canonical in-game gold coin: identical to the collectible in play.
        sc.coin_glyph(big, coin_cx, coin_cy, coin_r)
    else:
        # Dead coin: bypass coin_glyph (which renders its own gold palette) and
        # draw a pewter disc manually so luma stays well below the gold coin.
        pygame.draw.circle(big, (75, 70, 85), (coin_cx, coin_cy), coin_r)
        pygame.draw.circle(big, (45, 40, 55), (coin_cx, coin_cy), coin_r,
                           max(1, m(1)))

    # LABEL centers in the full pill width, vertically in the body below the
    # coin's footprint (coin occupies the top coin_r device px of the pill).
    label_cy = btn_y0 + coin_r + (BTN_H_D - coin_r) // 2
    label_rect = sc.plain_text(big, "BUY & EQUIP", sc.font(9),
                               (CX_D, label_cy),
                               label_col, shadow_a=0, weight=m(0.9),
                               tracking=m(1))

    # DIAGONAL STRIKE on the disabled path: lower-left → upper-right through the
    # label bounding box — unmistakably signals the unaffordable state at 1× scale.
    if not affordable:
        pygame.draw.line(big, (200, 60, 60),
                         (label_rect.left, label_rect.bottom),
                         (label_rect.right, label_rect.top),
                         m(2))   # 4 device px = 2 logical px at 1×

    return r


def patched_draw_confirm(self, surf):
    """Full confirm popup with the coin-drop action button wired in; every
    other element is identical to the production _draw_confirm."""
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
        # Nudge the hint line up slightly so the coin at the pill's top edge
        # has breathing room above it.
        store_cards.plain_text(big, "NOT ENOUGH COINS",
                               store_cards.font(9), (m(CX), m(244)),
                               (150, 166, 190), shadow_a=0)

    # ── action button (coin-drop) ──────────────────────────────────────────────
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
    # Highest-cost parrot skin so cost > 0 → balance-0 reads unaffordable.
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
    head = hf.render("coin-drop · BUY & EQUIP PILL  Round 2", True, (220, 190, 100))
    sheet.blit(head, (10, 10))
    sheet.blit(lf.render("AFFORDABLE", True, (200, 185, 140)), (30, 380))
    sheet.blit(lf.render("UNAFFORDABLE (grey coin, struck label)", True,
                          (200, 185, 140)), (232, 380))

    out = os.path.join(os.path.dirname(__file__), "..",
                       "docs", "store_confirm_popup", "coin-drop", "round_2.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())

    # ── pixel verification via PIL (never display the PNG) ────────────────────
    # Coordinate mapping (all final 1× logical sheet coords):
    #   Popup at sheet (0,30) [affordable] and (220,30) [unaffordable].
    #   Pill top edge (btn_y0 logical) = 273 - 15 = 258.
    #   Sheet y of pill top = 30 + 258 = 288.
    #   Pill centre x in popup = 100  →  sheet x: 100 [aff], 320 [una].
    #
    # SLOT edge: slot_w logical = 26/2 = 13, so slot left logical = 100-13 = 87.
    # Coin radius logical = 10, coin left = 100-10 = 90.
    # Slot extends 3 logical px LEFT of coin edge (sheet x: 87-90 for aff pane).
    # Sample at x=88, pill-top y → must show dark slot fill, NOT coin/enamel.
    #
    # COIN centre: at pill top edge → affordable=gold, unaffordable=grey.
    # ENAMEL: left pill body well away from coin → dark enamel colour.
    from PIL import Image
    img = Image.open(out)
    px_map = img.load()

    def luma(c):
        return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

    pill_top_y = 30 + 258   # = 288  (pill top edge in sheet)
    pill_mid_y = 30 + 273   # = 303  (pill vertical centre)

    # Slot LEFT EDGE (3px left of coin, still inside the slot rect).
    aff_slot  = px_map[88, pill_top_y + 2][:3]
    una_slot  = px_map[308, pill_top_y + 2][:3]

    # Coin UPPER BODY — 6 logical px above coin centre avoids the "$" glyph
    # at the coin centre and hits the bright gold rim (luma ~200+).
    aff_coin  = px_map[100, pill_top_y - 6][:3]
    # Grey coin: sample at coin centre (unaffordable) — the grey disc has no
    # "$" glyph so the centre IS the flat pewter fill.
    una_coin  = px_map[320, pill_top_y][:3]

    # Pill body enamel (left zone, well away from coin/slot) — must be dark.
    aff_enamel = px_map[40, pill_mid_y][:3]

    print("\nPixel verification (all in final 1× sheet):")
    print(f"  Slot left edge (affordable,   y+2): {aff_slot}  "
          f"luma={luma(aff_slot):.1f}  (target < 60, dark)")
    print(f"  Slot left edge (unaffordable, y+2): {una_slot}  "
          f"luma={luma(una_slot):.1f}  (target < 60, dark)")
    print(f"  Coin upper body (affordable, -6):   {aff_coin}  "
          f"luma={luma(aff_coin):.1f}  (target > 130, bright gold rim)")
    print(f"  Coin centre (unaffordable, grey):   {una_coin}  "
          f"luma={luma(una_coin):.1f}  (target < 100, dead pewter)")
    print(f"  Pill left enamel (affordable):      {aff_enamel}  "
          f"luma={luma(aff_enamel):.1f}  (coin NOT at left)")

    assert luma(aff_slot) < 80,   f"Slot edge not dark (affordable): {aff_slot}"
    assert luma(una_slot) < 80,   f"Slot edge not dark (unaffordable): {una_slot}"
    assert luma(aff_coin) > 130,  f"Gold coin rim not bright enough: {aff_coin}"
    assert luma(una_coin) < 100,  f"Grey coin not dead enough: {una_coin}"
    # Gold vs grey contrast: bright gold rim must read clearly above grey disc.
    assert luma(aff_coin) > luma(una_coin) + 50, \
        f"Gold/grey coin contrast too low: {luma(aff_coin):.0f} vs {luma(una_coin):.0f}"
    # Coin must be at TOP not left: left pill body must be dark enamel.
    assert luma(aff_enamel) < 120, \
        f"Left pill body too bright (coin appears to be at left): {aff_enamel}"
    print("All pixel checks passed.")


if __name__ == "__main__":
    main()
