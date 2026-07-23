"""illuminated-codex — round_2 final render.

Round_2 fix: Zone A was same luminance as Zone B on parchment (both amber ~155).
Replaced narrow 104×26 chip with a WIDE 218×42 gilt bar spanning the card — the
width dominance creates clear visual hierarchy regardless of luminance. Price at
FS=22 for headline readability. LEGENDARY stays lapis cross-hue.
"""
import os
import sys
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame.init()
pygame.display.set_mode((1, 1))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game.store_cards as sc


def _safe_gloss(surf, rect, radius, peak=46):
    w, h = rect[2], rect[3]
    gsurf = pygame.Surface((w, h), pygame.SRCALPHA)
    gsurf.fill((0, 0, 0, 0))
    steps = 10
    for i in range(steps):
        t = i / (steps - 1)
        alpha = int(peak * (1 - t))
        bar_h = max(1, int(h * 0.45 * (1 - t)))
        pygame.draw.ellipse(gsurf, (255, 255, 255, alpha),
            (int(w * 0.1), int(h * 0.04 + i * 1.5), int(w * 0.8), bar_h))
    surf.blit(gsurf, (rect[0], rect[1]))


sc.gloss_sweep = _safe_gloss

m = sc.m

SS = 2
POP_W, POP_H = 260, 442
CX, DISC_CY, R_HERO = 130, 135, 53
Y_NAME, NAME_FS, CHIP_CY = 213, 45, 247
BTN_CY, BTN_W, BTN_H, BTN_RAD = 360, 99, 31, 12
BUY_CX, CAN_CX = 76, 184
Y_BANNER, GEM_L_X, GEM_R_X = 402, 43, 217

CABO_LO = (22, 24, 50)
CABO_HI = (6, 7, 20)

PAL = {
    "RARE": {"gem": (108, 188, 252), "deep": (28, 68, 128), "glow": (168, 218, 252)},
    "EPIC": {"gem": (194, 122, 248), "deep": (88, 38, 168), "glow": (224, 178, 252)},
    "LEGENDARY": {"gem": (255, 202, 104), "deep": (148, 88, 18), "glow": (255, 238, 168)},
}
SIDS = {"RARE": "skin_wizard", "EPIC": "skin_prism", "LEGENDARY": "skin_astronaut"}
NAMES = {"RARE": "FROST WING", "EPIC": "PRISM WING", "LEGENDARY": "INFERNO WING"}
PRICES = {"RARE": "720", "EPIC": "1,400", "LEGENDARY": "2,600"}


def _fit_font(text, start_px, max_w, tracking=0):
    px = start_px
    f = sc._font(px, True)
    while sc._glyph_base(text, f, tracking).get_width() > max_w and px > 12:
        px -= 2
        f = sc._font(px, True)
    return f


def render_popup(tier):
    pal = PAL[tier]
    sid = SIDS[tier]
    name = NAMES[tier]
    price = PRICES[tier]
    legendary = tier == "LEGENDARY"

    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_rect = pygame.Rect(m(6), m(6), m(248), m(430))

    # 1 · shadow
    sc.drop_shadow(big, card_rect, m(24), blur=m(8), alpha=160, dy=m(4))

    # 2 · parchment body (unchanged — the concept's identity)
    body = sc.vgrad_stops(card_rect.w, card_rect.h, m(24),
                          [(0.0, (236, 224, 190)), (0.5, (224, 208, 168)),
                           (1.0, (206, 186, 142))], 255, gamma=1.03)
    big.blit(body, card_rect.topleft)

    # 3 · dark inner mat + regalia frame (unchanged)
    pygame.draw.rect(big, (28, 20, 10), card_rect.inflate(-m(6), -m(6)),
                     width=m(8), border_radius=m(20))
    sc._draw_regalia_frame(big, card_rect, m(24))
    pygame.draw.rect(big, (20, 14, 6), card_rect, width=m(2), border_radius=m(24))

    # 4 · name plate
    nf = _fit_font(name, m(NAME_FS), m(210))
    sc.plain_text(big, name, nf, (m(CX), m(Y_NAME)), (56, 40, 20),
                  shadow_a=90, weight=m(1.1), keyline=(200, 182, 140), kw=m(1.0))

    # 5 · Zone A — WIDE GILT BAR 218×42 (r2 fix: dominant headline element)
    bar = pygame.Rect(m(21), m(CHIP_CY) - m(21), m(218), m(42))
    if legendary:
        # Lapis cross-hue bar for LEGENDARY
        sc.chip_body_stops(big, bar, m(7),
                           [(0.0, (48, 96, 220)), (0.5, (30, 66, 176)),
                            (1.0, (18, 44, 130))],
                           (12, 24, 72), (160, 200, 255), gloss=38)
        num_col = (220, 238, 255)
    else:
        # Rich amber gilt bar spanning full card inner width
        sc.chip_body_stops(big, bar, m(7),
                           [(0.0, (248, 200, 96)), (0.4, (216, 160, 52)),
                            (1.0, (164, 110, 22))],
                           (78, 44, 8), (255, 240, 180), gloss=36)
        num_col = (40, 22, 4)
    # Coin + large numeral centred in bar (FS=22 for headline readability)
    numf = sc._font(m(22), True)
    num_w = sc._glyph_base(price, numf, 0).get_width()
    coin_r = m(12)
    gap = m(6)
    group_w = coin_r * 2 + gap + num_w
    gx = m(CX) - group_w // 2
    sc.coin_glyph(big, gx + coin_r, m(CHIP_CY), coin_r)
    sc.plain_text(big, price, numf, (gx + coin_r * 2 + gap + num_w // 2, m(CHIP_CY)),
                  num_col, shadow_a=0, weight=m(0.9))

    # 6 · dead-zone heraldic shield (unchanged — it's ≥62px tall, bold shape)
    pts = [(m(106), m(272)), (m(154), m(272)), (m(154), m(305)),
           (m(130), m(331)), (m(106), m(305))]
    pygame.draw.polygon(big, (24, 16, 8), pts)
    pygame.draw.rect(big, (204, 160, 40), (m(106), m(272), m(48), m(10)))
    pygame.draw.polygon(big, (204, 160, 40), pts, width=max(2, m(2)))
    sc.facet_gem(big, m(130), m(298), m(9), pal["gem"], pal["deep"])

    # 7 · shelf divider
    shelf_y = m(330)
    pygame.draw.line(big, (180, 150, 90), (m(30), shelf_y), (m(230), shelf_y),
                     max(2, m(2)))
    pygame.draw.line(big, (60, 42, 18), (m(30), shelf_y + m(2)),
                     (m(230), shelf_y + m(2)), max(1, m(1)))

    # BUY — warm burnt-gold enamel (luminance well above dark CANCEL)
    buy = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    buy.center = (m(BUY_CX), m(BTN_CY))
    sc.chip_body_stops(big, buy, m(BTN_RAD),
                       [(0.0, (168, 104, 22)), (1.0, (104, 60, 8))],
                       sc.GOLD_A_RIM_DARK, sc.GOLD_A_RIM_BRIGHT, gloss=28)
    sc.plain_text(big, "BUY", sc._font(m(15), True), buy.center,
                  (255, 248, 220), shadow_a=0, weight=m(1.0),
                  keyline=(8, 6, 20), kw=m(1.0))

    # CANCEL — aged-vellum brown (dark relative to BUY)
    can = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    can.center = (m(CAN_CX), m(BTN_CY))
    sc._dark_chip_body(big, can, m(BTN_RAD),
                       [(0.0, (80, 64, 40)), (1.0, (52, 40, 24))],
                       (48, 38, 18), (200, 182, 140))
    sc.plain_text(big, "CANCEL", sc._font(m(13), True), can.center,
                  (220, 208, 178), shadow_a=0, weight=m(0.9))

    # 8 · Zone B — flank gems + ribbon
    if legendary:
        fgem, fdeep = (255, 202, 104), (148, 88, 18)
    else:
        fgem, fdeep = (204, 160, 40), (58, 48, 22)
    sc.facet_gem(big, m(GEM_L_X), m(Y_BANNER), m(9), fgem, fdeep)
    sc.facet_gem(big, m(GEM_R_X), m(Y_BANNER), m(9), fgem, fdeep)
    sc._ribbon(big, tier, m(CX), m(Y_BANNER), m(150), pal)

    # 9 · hero on inked medallion (unchanged)
    pygame.draw.circle(big, (40, 30, 14), (m(CX), m(DISC_CY)), m(58))
    pygame.draw.circle(big, (204, 160, 40), (m(CX), m(DISC_CY)), m(56), max(2, m(2)))
    sc.cabochon(big, m(CX), m(DISC_CY), m(R_HERO), CABO_LO, CABO_HI,
                ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, m(CX), m(DISC_CY), int(m(R_HERO) * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (m(CX), m(DISC_CY)), int(m(R_HERO) * 0.7))
    if legendary:
        orig = getattr(sc, "CABO_SPEC_A", 180)
        sc.CABO_SPEC_A = int(orig * 0.8)
    sc.cabochon_glass(big, m(CX), m(DISC_CY), m(R_HERO), tint=pal["gem"])
    if legendary:
        sc.CABO_SPEC_A = orig

    return big


def main():
    SS = 2
    MARGIN, HEAD, GAP = 20, 58, 12
    tiers = ["RARE", "EPIC", "LEGENDARY"]
    popups = [render_popup(t) for t in tiers]
    pw, ph = popups[0].get_size()

    strip_w = m(MARGIN) * 2 + pw * len(tiers) + m(GAP) * (len(tiers) - 1)
    strip_h = m(HEAD) + ph + m(MARGIN)
    strip = pygame.Surface((strip_w, strip_h))
    strip.fill((28, 22, 12))

    title_f = pygame.font.Font(None, m(28))
    title = title_f.render("CONFIRM PURCHASE · illuminated-codex · round_2",
                           True, (204, 160, 40))
    strip.blit(title, title.get_rect(midtop=(strip_w // 2, m(10))))

    lbl_f = pygame.font.Font(None, m(18))
    for i, (t, p) in enumerate(zip(tiers, popups)):
        x = m(MARGIN) + i * (pw + m(GAP))
        y = m(HEAD)
        lbl = lbl_f.render(t, True, (220, 210, 180))
        strip.blit(lbl, lbl.get_rect(midbottom=(x + pw // 2, y - m(4))))
        strip.blit(p, (x, y))

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "confirm_purchase_v8", "premium-v2", "illuminated-codex",
                       "round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(strip, out)
    print("wrote", out, strip.get_size())


if __name__ == "__main__":
    main()
