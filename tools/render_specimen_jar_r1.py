"""Round-1 concept render for the `specimen-jar` item-card redesign.

Headless-only exploration harness (never imported by the game): authors the
legendary SPECIMEN-JAR card on a 2x supersample author canvas so the reviewer
can judge the squat curiosity-vessel, the CLEAR front pane (zero glass over the
fox), the side-only glass language, and the brass/wax/tag apothecary dressing
on git.

The card the review sheet judges is the downscaled 324x200 (2x in-game) surface;
authoring at an extra x2 gives the vessel curves + brass fittings clean AA, and
the cork stopper is drawn into negative-y headroom so it clips at the card's top
edge — the "breaking the frame" read the brief asks for.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")

import math
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color                                  # noqa: E402
from game.hud import _font                                        # noqa: E402
from game.store_cards import soft_glow                            # noqa: E402
from game.animal_kitsune import build_kitsune, build_kitsune_aura  # noqa: E402


# ── canvas ───────────────────────────────────────────────────────────────────
# CW,CH = the 2x in-game card. A is the EXTRA author supersample on top of that
# (curves + brass fittings resolve crisp before the single downscale).
CW, CH = 324, 200
A = 2
AW, AH = CW * A, CH * A


def P(v):
    """2x-canvas px -> author px (integer)."""
    return int(round(v * A))


# ── museum palette ───────────────────────────────────────────────────────────
NICHE_TOP = (22, 20, 30)
NICHE_BOT = (40, 36, 50)
WARM = (255, 202, 104)            # legendary warm-light + liquid + bubbles
GLASS_HI = (220, 230, 255)        # side-edge glass highlight
BRASS = (200, 162, 60)            # neck ring / cap brass
BRASS_HI = (232, 196, 110)
BRASS_DK = (150, 112, 36)
BASE_RIM = (180, 140, 50)         # foot rim
CORK = (178, 130, 80)
WAX = (220, 180, 60)
PARCH = (232, 218, 178)
PARCH_INK = (80, 50, 20)


# ── jar geometry (2x-canvas px) ──────────────────────────────────────────────
CXJ = 162                          # jar centre x
JB_L, JB_R, JB_T, JB_B = 52, 272, 24, 190     # body box (w=220, h=166)
JB_RAD = 46                        # big radius => rounded shoulders into margins
NK_L, NK_R, NK_T, NK_B = 123, 201, 6, 34      # neck box
NK_RAD = 12
BODY_CY = (JB_T + JB_B) // 2       # 107 — fox centres here


def _lin(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def _bezier(p0, p1, p2, n):
    out = []
    for t in _lin(0.0, 1.0, n):
        u = 1 - t
        x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
        out.append((x, y))
    return out


def _jar_mask():
    """White alpha silhouette of body+neck — the clip for every interior wash so
    liquid / side glass / base band never leak past the vessel edge."""
    m = pygame.Surface((AW, AH), pygame.SRCALPHA)
    pygame.draw.rect(m, (255, 255, 255, 255),
                     (P(JB_L), P(JB_T), P(JB_R - JB_L), P(JB_B - JB_T)),
                     border_radius=P(JB_RAD))
    pygame.draw.rect(m, (255, 255, 255, 255),
                     (P(NK_L), P(NK_T), P(NK_R - NK_L), P(NK_B - NK_T)),
                     border_radius=P(NK_RAD))
    return m


def _clip(wash, mask):
    wash.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


def build_card():
    surf = pygame.Surface((AW, AH))
    mask = _jar_mask()

    # 1) museum-niche gradient — dark crown, lighter shelf floor.
    for yy in range(AH):
        c = lerp_color(NICHE_TOP, NICHE_BOT, yy / (AH - 1))
        pygame.draw.line(surf, c, (0, yy), (AW, yy))

    # 2) cabinet-niche shelf supports: faint dark vertical gradients at the far
    #    margins so the card reads as a recessed nook, not a flat panel.
    sides = pygame.Surface((AW, AH), pygame.SRCALPHA)
    for xv in range(0, 30):
        a = int(150 * (1 - xv / 30) ** 1.4)
        pygame.draw.line(sides, (6, 6, 12, a), (P(xv), 0), (P(xv), AH))
        pygame.draw.line(sides, (6, 6, 12, a), (P(324 - xv), 0), (P(324 - xv), AH))
    surf.blit(sides, (0, 0))

    # 3) warm-light bloom pooling at the shelf floor where the jar sits + a faint
    #    shelf-front ledge highlight.
    soft_glow(surf, P(CXJ), P(190), P(126), WARM, 24, layers=9)
    ledge = pygame.Surface((AW, AH), pygame.SRCALPHA)
    pygame.draw.line(ledge, (70, 66, 84, 90), (P(20), P(188)), (P(304), P(188)),
                     max(1, A))
    surf.blit(ledge, (0, 0))

    # 4) soft contact shadow anchoring the jar to the shelf.
    csh = pygame.Surface((AW, AH), pygame.SRCALPHA)
    for i in range(P(9), 0, -1):
        a = int(90 * (i / P(9)))
        pygame.draw.ellipse(csh, (0, 0, 0, a),
                            (P(JB_L - 6) - i, P(184) + (P(9) - i),
                             P(JB_R - JB_L + 12) + 2 * i, P(14)))
    surf.blit(csh, (0, 0))

    # 5) price-tag STRING — drawn UNDER the fox + jar so it only shows where it
    #    emerges (tucked down the right margin to the tag); the fox and the neck
    #    ring cover the crossing so no string ever rakes the specimen.
    string_pts = _bezier((206, 30), (300, 82), (263, 161), 26)
    pygame.draw.lines(surf, (66, 56, 40), False,
                      [(P(x), P(y)) for x, y in string_pts], max(1, A))
    pygame.draw.lines(surf, (128, 112, 82), False,
                      [(P(x), P(y - 0.6)) for x, y in string_pts], max(1, A))

    # 6) parchment PRICE TAG in the lower-right corner (NOT on the jar); its left
    #    edge tucks under the jar's right glass so it reads pinned to the vessel.
    tx, ty, tw, th = 256, 158, 60, 22
    pygame.draw.rect(surf, PARCH, (P(tx), P(ty), P(tw), P(th)), border_radius=P(4))
    pygame.draw.rect(surf, (250, 242, 214),
                     (P(tx), P(ty), P(tw), P(th // 2)), border_radius=P(4))
    pygame.draw.rect(surf, (198, 182, 142), (P(tx), P(ty), P(tw), P(th)),
                     width=max(1, A), border_radius=P(4))
    pygame.draw.circle(surf, (140, 126, 92), (P(tx + 6), P(ty + 5)), P(2))
    pf = _font(int(11 * A), True)
    price = pf.render("3,500", True, PARCH_INK)
    surf.blit(price, price.get_rect(center=(P(tx + 34), P(ty + 11))))

    # 7) legendary LIQUID — a warm golden preservative wash; legendary fills it
    #    HIGH (from y=128), densest at the base. Behind the fox so the clear pane
    #    over the specimen silhouette stays untouched.
    liq = pygame.Surface((AW, AH), pygame.SRCALPHA)
    ltop, lbot = 128, 186
    for yy in range(P(ltop), P(lbot)):
        f = (yy / A - ltop) / (lbot - ltop)
        a = int(34 * f ** 1.25)
        pygame.draw.line(liq, (*WARM, a), (P(JB_L), yy), (P(JB_R), yy))
    pygame.draw.line(liq, (255, 224, 150, 46), (P(64), P(ltop)),
                     (P(260), P(ltop)), max(1, A))
    _clip(liq, mask)
    surf.blit(liq, (0, 0))

    # 8) KITSUNE specimen — aura BEHIND, sprite on top; the brightest element,
    #    read clean through the invisible front pane. Filled to the jar height.
    sprite = build_kitsune(20)
    aura = build_kitsune_aura()
    fw, fh = P(160), P(195)
    fox = pygame.transform.smoothscale(sprite, (fw, fh))
    halo = pygame.transform.smoothscale(aura, (fw, fh))
    fr = fox.get_rect(center=(P(CXJ), P(BODY_CY)))
    surf.blit(halo, fr.topleft)
    surf.blit(fox, fr.topleft)

    # 9) legendary rising BUBBLES in the side margins only (never over the fox).
    for bx, by, br in [(63, 150, 5), (71, 116, 4), (66, 84, 3),
                       (258, 140, 4), (254, 100, 5), (261, 70, 3)]:
        soft_glow(surf, P(bx), P(by), P(br + 2), WARM, 90, layers=6)
        pygame.draw.circle(surf, (255, 226, 150), (P(bx), P(by)), P(br),
                           max(1, A))
        pygame.draw.circle(surf, (255, 250, 224), (P(bx - 1), P(by - 1)),
                           max(1, A))

    # 10) SIDE-ONLY glass: a dark wall band then a bright vertical highlight on
    #     each curved edge (the entire glass read lives here; the pane over the
    #     fox stays clear). Clipped to the vessel so the rounded shoulders fade
    #     the strips naturally.
    gl = pygame.Surface((AW, AH), pygame.SRCALPHA)
    pygame.draw.rect(gl, (8, 10, 18, 120), (P(JB_L), P(JB_T), P(6), P(JB_B - JB_T)))
    pygame.draw.rect(gl, (8, 10, 18, 120), (P(JB_R - 6), P(JB_T), P(6),
                                            P(JB_B - JB_T)))
    for xi in range(P(56), P(72)):
        a = int(100 * max(0.0, 1 - abs(xi / A - 60) / 8.0))
        if a > 0:
            pygame.draw.line(gl, (*GLASS_HI, a), (xi, P(28)), (xi, P(184)))
    for xi in range(P(252), P(268)):
        a = int(100 * max(0.0, 1 - abs(xi / A - 264) / 8.0))
        if a > 0:
            pygame.draw.line(gl, (*GLASS_HI, a), (xi, P(28)), (xi, P(184)))
    _clip(gl, mask)
    surf.blit(gl, (0, 0))

    # 11) glass BASE thickness — a darker horizontal band + a thin refraction
    #     glint, then the gilded foot rim spanning the full jar width.
    band = pygame.Surface((AW, AH), pygame.SRCALPHA)
    for yy in range(P(174), P(186)):
        f = (yy / A - 174) / 12
        pygame.draw.line(band, (6, 8, 16, int(95 * f)),
                         (P(JB_L), yy), (P(JB_R), yy))
    pygame.draw.line(band, (200, 214, 240, 60), (P(70), P(176)), (P(254), P(176)),
                     max(1, A))
    _clip(band, mask)
    surf.blit(band, (0, 0))
    pygame.draw.rect(surf, BASE_RIM, (P(JB_L), P(186), P(JB_R - JB_L), P(4)),
                     border_radius=P(2))
    pygame.draw.rect(surf, (232, 190, 100), (P(JB_L), P(186), P(JB_R - JB_L),
                                             max(1, A)))
    pygame.draw.rect(surf, (120, 90, 30), (P(JB_L), P(189), P(JB_R - JB_L),
                                           max(1, A)))

    # 12) thin glass RIM outline so the vessel silhouette reads as one form; a
    #     pale top-left kiss + a dark bottom-right contact.
    rim = pygame.Surface((AW, AH), pygame.SRCALPHA)
    pygame.draw.rect(rim, (0, 0, 0, 55),
                     (P(JB_L - 1), P(JB_T - 1), P(JB_R - JB_L + 2), P(JB_B - JB_T + 2)),
                     width=max(1, A), border_radius=P(JB_RAD + 1))
    pygame.draw.rect(rim, (190, 200, 225, 70),
                     (P(JB_L), P(JB_T), P(JB_R - JB_L), P(JB_B - JB_T)),
                     width=max(1, A), border_radius=P(JB_RAD))
    surf.blit(rim, (0, 0))
    # shoulder sheen — a faint glass highlight riding the top-left shoulder only.
    sh = pygame.Surface((AW, AH), pygame.SRCALPHA)
    pygame.draw.arc(sh, (210, 220, 240, 70),
                    (P(JB_L), P(JB_T), P(220), P(120)),
                    math.radians(78), math.radians(168), max(1, A * 2))
    surf.blit(sh, (0, 0))

    # 13) gilded brass NECK RING (a rarity fitting) with top/bottom metal shading.
    pygame.draw.rect(surf, BRASS, (P(116), P(27), P(92), P(7)), border_radius=P(3))
    pygame.draw.rect(surf, BRASS_HI, (P(116), P(27), P(92), max(1, A)))
    pygame.draw.rect(surf, BRASS_DK, (P(116), P(32), P(92), max(1, A)))

    # 14) CORK STOPPER poking above the card top edge (clips => breaks the frame)
    #     + a brass cap ring + a gilded wax seal with a dark fox-ear monogram.
    pygame.draw.rect(surf, CORK, (P(130), P(-12), P(64), P(24)), border_radius=P(8))
    pygame.draw.line(surf, (200, 156, 104), (P(140), P(-8)), (P(140), P(9)),
                     max(1, A))
    pygame.draw.rect(surf, (150, 106, 62), (P(130), P(-12), P(64), P(24)),
                     width=max(1, A), border_radius=P(8))
    pygame.draw.rect(surf, BRASS, (P(126), P(6), P(72), P(7)), border_radius=P(3))
    pygame.draw.rect(surf, BRASS_HI, (P(126), P(6), P(72), max(1, A)))
    pygame.draw.rect(surf, BRASS_DK, (P(126), P(11), P(72), max(1, A)))
    # wax seal disc + impressed monogram (kitsune ears + muzzle).
    pygame.draw.circle(surf, (150, 110, 40), (P(CXJ), P(3)), P(10))
    pygame.draw.circle(surf, WAX, (P(CXJ), P(3)), P(9))
    pygame.draw.circle(surf, (240, 205, 110), (P(CXJ - 3), P(0)), P(2))
    mg = (118, 82, 28)
    pygame.draw.polygon(surf, mg, [(P(158), P(5)), (P(159), P(-2)), (P(162), P(4))])
    pygame.draw.polygon(surf, mg, [(P(162), P(4)), (P(165), P(-2)), (P(166), P(5))])
    pygame.draw.polygon(surf, mg, [(P(159), P(4)), (P(165), P(4)), (P(162), P(9))])

    # thin card keyline so the body reads as a discrete card on the sheet.
    pygame.draw.rect(surf, (12, 12, 22), surf.get_rect(), max(1, A))

    return pygame.transform.smoothscale(surf, (CW, CH))


def main():
    card = build_card()

    pad = 26
    small = pygame.transform.smoothscale(card, (162, 100))
    hero = pygame.transform.smoothscale(card, (CW * 2, CH * 2))
    hw, hh = hero.get_size()

    sheet_w = hw + pad * 2
    sheet_h = pad + 28 + hh + 30 + 100 + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 26))

    tf = _font(17, True)
    lf = _font(12, True)
    sheet.blit(tf.render("specimen-jar  ·  LEGENDARY  ·  round 1",
                         True, (236, 226, 244)), (pad, 8))
    y = pad + 28
    sheet.blit(hero, (pad, y))
    sheet.blit(lf.render("648x400 preview · card authored at 324x200 (2x in-game) "
                         "· cork clips the top edge", True, (150, 150, 168)),
               (pad, y + hh + 6))
    y2 = y + hh + 34
    sheet.blit(small, (pad, y2))
    sheet.blit(lf.render("1x in-game grid scale (162x100)", True, (150, 150, 168)),
               (pad + 172, y2 + 42))

    out = "/home/user/skybit/docs/item_card_redesign/specimen-jar/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved:", out)


if __name__ == "__main__":
    main()
