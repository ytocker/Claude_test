"""illuminated-codex — confirm-purchase popup, round_1 review render.

An illuminated-manuscript take on the buy prompt: warm parchment body (a full
value inversion from the dark-navy store norm), sealed inside a hard near-black
inner mat + gold regalia frame so the gilt beads never wash out on the cream.
The shock is the inversion itself; tiers cross-hue in Zone A (oxblood/amber for
RARE+EPIC, cool lapis for LEGENDARY so it plays against the amber Zone B).

Review-only: renders three tier fixtures into one labelled strip. Not wired into
the live game.
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


# The production gloss_sweep is BLEND_ADD-only and blows the parchment/amber
# bodies out; swap in a bounded elliptical sheen for the review render.
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


# ── shared metrics (logical px; flow through m()) ─────────────────────────────
SS = 2


def m(v):
    return int(round(v * 2))


POP_W, POP_H = 260, 442
CX, DISC_CY, R_HERO = 130, 135, 53
Y_NAME, NAME_FS, CHIP_CY = 213, 45, 247
BTN_CY, BTN_W, BTN_H, BTN_RAD, BTN_GAP = 360, 99, 31, 12, 10
BUY_CX, CAN_CX = 76, 184
Y_BANNER, GEM_L_X, GEM_R_X = 402, 43, 217

# Hero cabochon well (kept dark so the glass disc reads against the parchment).
CABO_LO = (22, 24, 50)
CABO_HI = (6, 7, 20)

# gem / glow / deep drive the hero cabochon aura + the Zone-B tier ribbon.
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
    """Build one tier's popup onto its own SS canvas (POP*SS) and return it."""
    pal = PAL[tier]
    sid = SIDS[tier]
    name = NAMES[tier]
    price = PRICES[tier]
    legendary = tier == "LEGENDARY"

    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_rect = pygame.Rect(m(6), m(6), m(248), m(430))

    # 1 — grounding drop shadow beneath the whole page.
    sc.drop_shadow(big, card_rect, m(24), blur=m(8), alpha=160, dy=m(4))

    # 2 — parchment ground: the value inversion. Warm cream fading to aged tan.
    body = sc.vgrad_stops(card_rect.w, card_rect.h, m(24),
                          [(0.0, (236, 224, 190)), (0.5, (224, 208, 168)),
                           (1.0, (206, 186, 142))], 255, gamma=1.03)
    big.blit(body, card_rect.topleft)

    # 3 — dark inner mat BEFORE the frame: a near-black ring the gold beads sit
    # over, so the gilt never vanishes into the cream.
    pygame.draw.rect(big, (28, 20, 10), card_rect.inflate(-m(6), -m(6)),
                     width=m(8), border_radius=m(20))

    # 4 — gold regalia frame (constant-lit twin gold beads + corner miters).
    sc._draw_regalia_frame(big, card_rect, m(24))

    # 5 — outer dark keyline to define the page edge against the review ground.
    pygame.draw.rect(big, (20, 14, 6), card_rect, width=m(2), border_radius=m(24))

    # 6 — name plate: dark ink on parchment with a pale embossed keyline.
    nf = _fit_font(name, m(NAME_FS), m(210), tracking=0)
    sc.plain_text(big, name, nf, (m(CX), m(Y_NAME)), (56, 40, 20),
                  shadow_a=90, weight=m(1.1), keyline=(200, 182, 140), kw=m(1.0))

    # 7 — Zone A price bar. RARE/EPIC = amber; LEGENDARY = cool lapis so it
    # cross-hues against the amber Zone B ribbon below.
    chip = pygame.Rect(0, 0, m(104), m(26))
    chip.center = (m(CX), m(CHIP_CY))
    if legendary:
        sc.chip_body_stops(big, chip, m(6),
                           [(0.0, (38, 78, 188)), (1.0, (18, 44, 130))],
                           (12, 24, 72), (150, 190, 255), gloss=34)
        num_col = (224, 236, 255)
    else:
        sc.chip_body_stops(big, chip, m(6),
                           [(0.0, (236, 176, 72)), (0.45, (204, 132, 42)),
                            (1.0, (150, 90, 18))],
                           (78, 44, 8), (255, 226, 150), gloss=30)
        num_col = (52, 28, 4)
    # coin + numeral centred as a group inside the chip's inner width.
    numf = sc._font(m(14), True)
    num_w = sc._glyph_base(price, numf, 0).get_width()
    coin_d = m(9) * 2
    gap = m(4)
    group_w = coin_d + gap + num_w
    gx = m(CX) - group_w // 2
    sc.coin_glyph(big, gx + m(9), m(CHIP_CY), m(9))
    sc.plain_text(big, price, numf, (gx + coin_d + gap + num_w // 2, m(CHIP_CY)),
                  num_col, shadow_a=0, weight=m(0.8))

    # 8 — dead-zone heraldic shield (62px tall): ink field, gold rim + chief
    # band, the tier gem set as the charge.
    pts = [(m(106), m(272)), (m(154), m(272)), (m(154), m(305)),
           (m(130), m(331)), (m(106), m(305))]
    pygame.draw.polygon(big, (24, 16, 8), pts)
    pygame.draw.rect(big, (204, 160, 40), (m(106), m(272), m(48), m(10)))
    pygame.draw.polygon(big, (204, 160, 40), pts, width=max(2, m(2)))
    sc.facet_gem(big, m(130), m(298), m(9), pal["gem"], pal["deep"])

    # 9 — shelf ledge that seats the button row.
    shelf_y = m(330)
    pygame.draw.line(big, (180, 150, 90), (m(30), shelf_y), (m(230), shelf_y),
                     max(1, m(1)))
    pygame.draw.line(big, (60, 42, 18), (m(30), shelf_y + m(1)),
                     (m(230), shelf_y + m(1)), max(1, m(0.6)))

    # BUY — warm burnt-gold enamel, gilt bevel.
    buy = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    buy.center = (m(BUY_CX), m(BTN_CY))
    sc.chip_body_stops(big, buy, m(BTN_RAD),
                       [(0.0, (120, 75, 18)), (1.0, (80, 45, 8))],
                       sc.GOLD_A_RIM_DARK, sc.GOLD_A_RIM_BRIGHT, gloss=28)
    sc.plain_text(big, "BUY", sc._font(m(15), True), buy.center,
                  (255, 248, 220), shadow_a=0, weight=m(1.0),
                  keyline=(8, 6, 20), kw=m(1.0))

    # CANCEL — aged-vellum brown so it recedes into the parchment theme.
    can = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    can.center = (m(CAN_CX), m(BTN_CY))
    sc._dark_chip_body(big, can, m(BTN_RAD),
                       [(0.0, (96, 80, 52)), (1.0, (64, 52, 30))],
                       (48, 38, 18), (200, 182, 140))
    sc.plain_text(big, "CANCEL", sc._font(m(13), True), can.center,
                  (238, 226, 196), shadow_a=0, weight=m(0.9))

    # 10 — Zone B: flank gems + tier ribbon. LEGENDARY keeps amber here to
    # contrast its lapis Zone A; RARE/EPIC flank gems stay muted gilt.
    if legendary:
        fgem, fdeep = (255, 202, 104), (148, 88, 18)
    else:
        fgem, fdeep = (204, 160, 40), (58, 48, 22)
    sc.facet_gem(big, m(GEM_L_X), m(Y_BANNER), m(9), fgem, fdeep)
    sc.facet_gem(big, m(GEM_R_X), m(Y_BANNER), m(9), fgem, fdeep)
    sc._ribbon(big, tier, m(CX), m(Y_BANNER), m(150), pal)

    # 11 — hero seated in an inked medallion so the glass disc reads against the
    # parchment. Dark seat -> gold ring -> cabochon -> skin -> glass dome.
    pygame.draw.circle(big, (40, 30, 14), (m(CX), m(DISC_CY)), m(58))
    pygame.draw.circle(big, (204, 160, 40), (m(CX), m(DISC_CY)), m(56), max(2, m(2)))
    sc.cabochon(big, m(CX), m(DISC_CY), m(R_HERO), CABO_LO, CABO_HI,
                ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, m(CX), m(DISC_CY), int(m(R_HERO) * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (m(CX), m(DISC_CY)),
                           int(m(R_HERO) * 0.7))
    if legendary:
        orig = getattr(sc, "CABO_SPEC_A", 180)
        sc.CABO_SPEC_A = int(orig * 0.8)
    sc.cabochon_glass(big, m(CX), m(DISC_CY), m(R_HERO), tint=pal["gem"])
    if legendary:
        sc.CABO_SPEC_A = orig

    return big


def main():
    tiers = ["RARE", "EPIC", "LEGENDARY"]
    MARGIN, HEAD, GAP = 20, 58, 12
    cards = [render_popup(t) for t in tiers]
    cw, ch = cards[0].get_size()

    strip_w = m(MARGIN) + len(cards) * cw + (len(cards) - 1) * m(GAP) + m(MARGIN)
    strip_h = m(HEAD) + ch + m(MARGIN)
    strip = pygame.Surface((strip_w, strip_h))
    strip.fill((30, 34, 46))

    title = sc._font(m(20), True)
    tsurf = title.render("CONFIRM PURCHASE  —  illuminated-codex", True, (236, 226, 198))
    strip.blit(tsurf, (m(MARGIN), m(14)))

    label = sc._font(m(13), True)
    for i, (t, card) in enumerate(zip(tiers, cards)):
        x = m(MARGIN) + i * (cw + m(GAP))
        y = m(HEAD)
        ls = label.render(t, True, (208, 200, 176))
        strip.blit(ls, (x + cw // 2 - ls.get_width() // 2, m(HEAD) - m(20)))
        strip.blit(card, (x, y))

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "confirm_purchase_v8", "premium-v2",
                       "illuminated-codex", "round_1.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(strip, out)
    print("saved", out, strip.get_size())


if __name__ == "__main__":
    main()
