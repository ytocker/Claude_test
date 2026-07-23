"""onyx-imperial confirm-purchase popup — round_1 review render.

A black-and-gold reliquary CASE: four oversized corner gems clamped by gold
setting-claw arms reaching toward a 2-ring aura'd hero disc, all seated in a
near-black onyx body with a double gold bevel. NO crown — this is a vault/case
aesthetic. Deep-violet Zone A price enamel cross-hues the LEGENDARY tier's
imperial-teal Zone B against its unified warm-gold case.

Headless review tool only (SDL dummy). Draws three tier popups side by side and
saves a labelled strip under docs/. Never shipped in-game.
"""
import os, sys, pygame, math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame.init()
pygame.display.set_mode((1, 1))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game.store_cards as sc


# MANDATORY gloss_sweep patch — the shipped gloss_sweep is BLEND_ADD and blows a
# near-black onyx body to white; this alpha-carry ellipse sweep stays subtle.
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


# ── constants ────────────────────────────────────────────────────────────────
SS = 2
def m(v):
    return int(round(v * SS))

POP_W, POP_H = 260, 442
CX = 130
DISC_CY = 135
R_HERO = 53
Y_NAME = 213
NAME_FS = 45
CHIP_CY = 247
BTN_CY = 360
BTN_W, BTN_H, BTN_RAD, BTN_GAP = 99, 31, 12, 10
BUY_CX, CAN_CX = 76, 184
Y_BANNER = 402
GEM_L_X, GEM_R_X = 43, 217

CARD_RING_DEEP = (58, 48, 22)
CARD_RING_BRIGHT = (236, 202, 116)
GOLD_A_RIM_DARK = (86, 50, 8)
GOLD_A_RIM_BRIGHT = (255, 240, 190)
CLAW_GOLD = (196, 124, 34)
CLAW_SEAM = (86, 50, 8)
CLAW_PRONG = (236, 202, 116)

PALETTES = {
    "RARE":      {"gem": (108, 188, 252), "deep": (28, 68, 128),  "glow": (168, 218, 252)},
    "EPIC":      {"gem": (194, 122, 248), "deep": (88, 38, 168),  "glow": (224, 178, 252)},
    "LEGENDARY": {"gem": (255, 202, 104), "deep": (148, 88, 18),  "glow": (255, 238, 168)},
}
# LEGENDARY Zone B cross-hues the warm-gold case with an imperial teal.
ZONE_B_LEGENDARY = {"gem": (96, 206, 196), "deep": (20, 86, 84), "glow": (150, 236, 224)}

SIDS = {"RARE": "skin_wizard", "EPIC": "skin_prism", "LEGENDARY": "skin_astronaut"}
NAMES = {"RARE": "FROST WING", "EPIC": "PRISM WING", "LEGENDARY": "INFERNO WING"}
PRICES = {"RARE": "720", "EPIC": "1,400", "LEGENDARY": "2,600"}

CABO_LO = (22, 24, 50)
CABO_HI = (6, 7, 20)

# Logical corner-gem anchors: the four case corners the claws clamp from.
CORNERS = [(30, 60), (230, 60), (30, 300), (230, 300)]


def _fit_font(text, start_fs, max_w):
    """Name font shrunk until it clears the case width — the hero name must not
    kiss the gold frame."""
    fs = start_fs
    f = sc.font(fs)
    while sc._glyph_base(text, f, 0).get_width() > max_w and fs > 10:
        fs -= 1
        f = sc.font(fs)
    return f


def _setting_claw(surf, gx, gy):
    """A tapering gold claw arm from a corner gem toward the disc centre — the
    case's setting hardware clamping the hero into place."""
    bx, by = m(gx), m(gy)
    dx, dy = m(CX) - bx, m(DISC_CY) - by
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    tipx, tipy = bx + ux * m(30), by + uy * m(30)
    px, py = -uy, ux
    bw, tw = m(7) / 2, m(2) / 2
    quad = [
        (bx + px * bw, by + py * bw),
        (bx - px * bw, by - py * bw),
        (tipx - px * tw, tipy - py * tw),
        (tipx + px * tw, tipy + py * tw),
    ]
    pygame.draw.polygon(surf, CLAW_GOLD, quad)
    pygame.draw.polygon(surf, CLAW_SEAM, quad, width=max(1, m(1)))
    pygame.draw.circle(surf, CLAW_PRONG, (int(tipx), int(tipy)), m(2))


def render_popup(tier):
    pal = PALETTES[tier]
    zb_pal = ZONE_B_LEGENDARY if tier == "LEGENDARY" else pal
    sid = SIDS[tier]

    big = pygame.Surface((m(POP_W), m(POP_H)), pygame.SRCALPHA)

    # 1 · drop shadow under the case body
    card_rect = pygame.Rect(m(6), m(6), m(248), m(430))
    sc.drop_shadow(big, card_rect, m(24), m(8), 160, m(4))

    # 2 · onyx body — near-black vertical gradient
    body = sc.vgrad_stops(card_rect.w, card_rect.h, m(24),
                          [(0.0, (20, 20, 34)), (1.0, (8, 8, 18))], 255, gamma=1.12)
    big.blit(body, card_rect.topleft)

    # 3 · top sheen + dark defining keyline
    sc.top_sheen(big, card_rect, m(24), m(34), peak=40)
    pygame.draw.rect(big, (3, 3, 10), card_rect, width=m(2), border_radius=m(24))

    # 4 · double gold bevel: heavy outer emboss + a fine inner gold ring
    sc.bevel_rim(big, card_rect, m(24), CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
                 w=max(1, m(2)))
    inner_ring = card_rect.inflate(-m(9), -m(9))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 70), inner_ring,
                     width=max(1, m(1)), border_radius=m(24) - m(9))

    # 5 · setting claws FIRST so the corner gems seat on top of the hardware
    for gx, gy in CORNERS:
        _setting_claw(big, gx, gy)

    # 6 · four oversized corner gems clamped by the claws
    for gx, gy in CORNERS:
        sc.facet_gem(big, m(gx), m(gy), m(15), pal["gem"], pal["deep"])

    # 7 · hero name plate
    name = NAMES[tier]
    nf = _fit_font(name, NAME_FS, m(POP_W) - m(40))
    sc.plain_text(big, name, nf, (m(CX), m(Y_NAME)), (220, 225, 240),
                  shadow_a=150, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))

    # 8 · Zone A — deep-violet enamel price plate
    plate = pygame.Rect(0, 0, m(100), m(26))
    plate.center = (m(CX), m(CHIP_CY))
    sc._dark_chip_body(big, plate, m(7),
                       [(0.0, (52, 30, 78)), (1.0, (26, 14, 44))],
                       (48, 44, 60), (150, 144, 120))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 120), plate.inflate(-m(4), -m(4)),
                     width=max(1, m(1)), border_radius=m(5))
    num = PRICES[tier]
    pf = sc.font(15)
    num_w = sc._glyph_base(num, pf, 0).get_width()
    coin_r, gap = m(9), m(5)
    total = coin_r * 2 + gap + num_w
    gx0 = m(CX) - total // 2
    sc.coin_glyph(big, gx0 + coin_r, m(CHIP_CY), coin_r)
    sc.plain_text(big, num, pf,
                  (gx0 + coin_r * 2 + gap + num_w // 2, m(CHIP_CY)),
                  (246, 222, 150), shadow_a=0, weight=m(0.9),
                  keyline=(6, 5, 14), kw=m(1.0))

    # 9 · dead-zone lozenge medallion between plate and shelf
    diamond = [(m(130), m(282)), (m(145), m(297)), (m(130), m(312)), (m(115), m(297))]
    pygame.draw.polygon(big, (14, 14, 26), diamond)
    pygame.draw.polygon(big, CARD_RING_BRIGHT, diamond, width=max(1, m(1)))
    sc.facet_gem(big, m(130), m(297), m(7), pal["gem"], pal["deep"])

    # 10 · shelf the action buttons mount on + BUY / CANCEL
    buy_rect = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    buy_rect.center = (m(BUY_CX), m(BTN_CY))
    can_rect = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    can_rect.center = (m(CAN_CX), m(BTN_CY))
    shelf = pygame.Rect(buy_rect.left - m(5), buy_rect.top - m(6),
                        (can_rect.right - buy_rect.left) + m(10), buy_rect.height + m(12))
    sc._dark_chip_body(big, shelf, m(14),
                       [(0.0, (20, 18, 30)), (1.0, (10, 9, 18))],
                       (40, 36, 50), (120, 110, 90))
    sc.chip_body_stops(big, buy_rect, m(BTN_RAD),
                       [(0.0, (120, 75, 18)), (1.0, (80, 45, 8))],
                       GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, gloss=26)
    sc.plain_text(big, "BUY", sc.font(16), buy_rect.center, (255, 248, 220),
                  shadow_a=0, weight=m(0.9), keyline=(8, 6, 20), kw=m(1.0))
    sc._dark_chip_body(big, can_rect, m(BTN_RAD),
                       [(0.0, (24, 24, 40)), (1.0, (12, 12, 24))],
                       (40, 38, 52), (120, 116, 96))
    sc.plain_text(big, "CANCEL", sc.font(13), can_rect.center, (140, 138, 158),
                  shadow_a=0, weight=m(0.8))

    # 11 · Zone B — flanking gems + notched imperial-seal ribbon
    sc.facet_gem(big, m(GEM_L_X), m(Y_BANNER), m(9), zb_pal["gem"], zb_pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(Y_BANNER), m(9), zb_pal["gem"], zb_pal["deep"])
    sc._ribbon(big, tier, m(CX), m(Y_BANNER), m(150), zb_pal)

    # 12 · 2-ring aura'd hero — the >=60px statement, drawn just before the dome
    sc._alpha_aura(big, m(CX), m(DISC_CY), m(73), pal["glow"], peak=64, layers=16)
    pygame.draw.circle(big, (3, 3, 10), (m(CX), m(DISC_CY)), m(69), max(1, m(1)))
    pygame.draw.circle(big, (*CARD_RING_BRIGHT, 235), (m(CX), m(DISC_CY)), m(66),
                       max(2, m(2)))
    pygame.draw.circle(big, (*pal["gem"], 170), (m(CX), m(DISC_CY)), m(58),
                       max(1, m(2)))

    # 13 · hero cabochon LAST so the skin sits under polished glass
    sc.cabochon(big, m(CX), m(DISC_CY), m(R_HERO), CABO_LO, CABO_HI,
                ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, m(CX), m(DISC_CY), int(m(R_HERO) * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (m(CX), m(DISC_CY)), int(m(R_HERO) * 0.7))
    if tier == "LEGENDARY":
        orig = getattr(sc, "CABO_SPEC_A", 180)
        sc.CABO_SPEC_A = int(orig * 0.8)
    sc.cabochon_glass(big, m(CX), m(DISC_CY), m(R_HERO), tint=pal["gem"])
    if tier == "LEGENDARY":
        sc.CABO_SPEC_A = orig

    return big


def main():
    tiers = ["RARE", "EPIC", "LEGENDARY"]
    MARGIN, HEAD, GAP = 20, 58, 12
    cards = [render_popup(t) for t in tiers]
    cw, ch = cards[0].get_size()

    strip_w = m(MARGIN) * 2 + cw * len(tiers) + m(GAP) * (len(tiers) - 1)
    strip_h = m(MARGIN) + m(HEAD) + ch
    strip = pygame.Surface((strip_w, strip_h), pygame.SRCALPHA)
    strip.fill((14, 14, 22, 255))

    title_f = pygame.font.Font(None, m(30))
    sub_f = pygame.font.Font(None, m(18))
    title = title_f.render("CONFIRM PURCHASE  ·  onyx-imperial  ·  round_1",
                           True, (236, 202, 116))
    strip.blit(title, title.get_rect(midtop=(strip_w // 2, m(12))))

    for i, (t, card) in enumerate(zip(tiers, cards)):
        x = m(MARGIN) + i * (cw + m(GAP))
        y = m(MARGIN) + m(HEAD)
        lbl = sub_f.render(t, True, (210, 210, 224))
        strip.blit(lbl, lbl.get_rect(midbottom=(x + cw // 2, y - m(4))))
        strip.blit(card, (x, y))

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "confirm_purchase_v8", "premium-v2", "onyx-imperial",
                       "round_1.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(strip, out)
    print("saved", out, strip.get_size())


if __name__ == "__main__":
    main()
