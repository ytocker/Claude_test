"""Round-2 concept render for the `specimen-jar` item-card redesign.

Headless-only exploration harness (never imported by the game). Round 2 answers
the art-director notes on round 1: the vessel is re-proportioned SQUAT-WIDE (it
now IS the card), the cork/cap/wax-seal assembly is pulled fully below the card
top so only the raw cork breaks the frame, rarity is carried by TWO bold cues
that survive the 1x downscale (a thick gilded neck collar + a warm gold
circumference glow), the legendary preservative fill is pushed dense with a
crisp meniscus and a gold cast bleeding onto the submerged fox, and the museum
niche is lifted to a warm umber "rare-specimen cabinet" rather than a mausoleum.

The judged card is the downscaled 324x200 (2x in-game) surface; authoring at an
extra x2 gives the vessel curves + brass fittings clean AA before the single
downscale. The sheet stacks BEFORE (live store card) / ROUND-1 / ROUND-2.
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
# Lifted, warm-umber cabinet ground (not the round-1 near-black violet) so the
# gold vessel radiates against a "rare-specimen cabinet", not a mausoleum.
NICHE_TOP = (32, 26, 22)
NICHE_BOT = (58, 46, 38)
WARM = (255, 168, 58)             # legendary glow — liquid, rim-glow, bubbles
GEM = (255, 202, 104)             # legendary gem
DEEP = (150, 92, 22)              # legendary deep
GLASS_HI = (224, 232, 255)        # side-edge glass highlight
BRASS = (206, 166, 62)            # neck-collar brass
BRASS_HI = (240, 204, 118)
BRASS_DK = (146, 108, 34)
BASE_RIM = (188, 146, 52)         # foot rim
CORK = (180, 132, 82)
CORK_DK = (140, 98, 58)
WAX = (224, 180, 62)
WAX_DK = (150, 108, 38)
PARCH = (234, 220, 182)
PARCH_INK = (74, 46, 18)


# ── jar geometry (2x-canvas px) ──────────────────────────────────────────────
# SQUAT-WIDE: body ~256w x 142h => 1.80:1, nearly filling the card minus the
# cabinet supports. Big corner radius => a rounded curiosity-dome silhouette.
CXJ = 162
JB_L, JB_R, JB_T, JB_B = 34, 290, 44, 186        # body box (w=256, h=142)
JB_RAD = 52
NK_L, NK_R, NK_T, NK_B = 120, 204, 30, 48        # neck box
NK_RAD = 10
BODY_CY = (JB_T + JB_B) // 2                       # 115

# Side glass highlight strip centres — bubbles are pushed ~10px INWARD of these.
GHI_L, GHI_R = 50, 274

# Legendary fill runs HIGH; the fox reads as genuinely submerged.
LTOP, LBOT = 76, 184


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


def _rim_glow(surf):
    """Rarity cue #2 — a soft warm-gold additive halo hugging the ENTIRE vessel
    circumference. Concentric gold ring-outlines fading outward read as a single
    ~12px bloom at 1x (a chunky signal that survives the downscale)."""
    spread, layers = 12, 10
    g = pygame.Surface((AW, AH), pygame.SRCALPHA)
    for i in range(layers, 0, -1):
        d = spread * i / layers
        a = int(64 * (1 - (i - 1) / layers) ** 1.7)
        if a <= 0:
            continue
        pygame.draw.rect(g, (*WARM, a),
                         (P(JB_L - d), P(JB_T - d),
                          P((JB_R - JB_L) + 2 * d), P((JB_B - JB_T) + 2 * d)),
                         width=max(1, A * 2), border_radius=P(JB_RAD + d))
        pygame.draw.rect(g, (*WARM, a),
                         (P(NK_L - d), P(NK_T - d),
                          P((NK_R - NK_L) + 2 * d), P((NK_B - NK_T) + 2 * d)),
                         width=max(1, A * 2), border_radius=P(NK_RAD + d))
    surf.blit(g, (0, 0), special_flags=pygame.BLEND_ADD)


def build_card():
    surf = pygame.Surface((AW, AH))
    mask = _jar_mask()

    # 1) warm museum-niche gradient — dark umber crown -> lifted shelf floor.
    for yy in range(AH):
        c = lerp_color(NICHE_TOP, NICHE_BOT, yy / (AH - 1))
        pygame.draw.line(surf, c, (0, yy), (AW, yy))

    # 2) recessed-nook supports: faint warm-dark vertical falloffs at the far
    #    margins so the card reads as a cabinet niche, not a flat panel.
    sides = pygame.Surface((AW, AH), pygame.SRCALPHA)
    for xv in range(0, 22):
        a = int(140 * (1 - xv / 22) ** 1.4)
        pygame.draw.line(sides, (14, 10, 8, a), (P(xv), 0), (P(xv), AH))
        pygame.draw.line(sides, (14, 10, 8, a), (P(324 - xv), 0), (P(324 - xv), AH))
    surf.blit(sides, (0, 0))

    # 3) warm-light bloom pooling at the shelf floor where the jar sits + a faint
    #    shelf-front ledge line.
    soft_glow(surf, P(CXJ), P(186), P(150), WARM, 22, layers=9)
    ledge = pygame.Surface((AW, AH), pygame.SRCALPHA)
    pygame.draw.line(ledge, (86, 70, 54, 90), (P(14), P(188)), (P(310), P(188)),
                     max(1, A))
    surf.blit(ledge, (0, 0))

    # 4) soft contact shadow anchoring the wide jar to the shelf.
    csh = pygame.Surface((AW, AH), pygame.SRCALPHA)
    for i in range(P(9), 0, -1):
        a = int(96 * (i / P(9)))
        pygame.draw.ellipse(csh, (0, 0, 0, a),
                            (P(JB_L - 4) - i, P(182) + (P(9) - i),
                             P(JB_R - JB_L + 8) + 2 * i, P(14)))
    surf.blit(csh, (0, 0))

    # 5) rarity cue #2 — warm gold circumference glow (drawn now so the vessel
    #    overwrites its inner half, leaving only the outer bloom).
    _rim_glow(surf)

    # 6) legendary LIQUID — a DENSE warm-gold preservative wash filling HIGH,
    #    densest at the base (alpha peak ~74). Behind the fox. Clipped to vessel.
    liq = pygame.Surface((AW, AH), pygame.SRCALPHA)
    for yy in range(P(LTOP), P(LBOT)):
        f = (yy / A - LTOP) / (LBOT - LTOP)
        a = int(74 * (0.34 + 0.66 * f ** 1.2))
        pygame.draw.line(liq, (255, 176, 66, a), (P(JB_L), yy), (P(JB_R), yy))
    _clip(liq, mask)
    surf.blit(liq, (0, 0))
    # crisp horizontal MENISCUS at the fill top — a bright band over a thin
    # shadow lip so the liquid surface reads as a real waterline.
    men = pygame.Surface((AW, AH), pygame.SRCALPHA)
    pygame.draw.line(men, (60, 34, 10, 90), (P(JB_L), P(LTOP + 1)),
                     (P(JB_R), P(LTOP + 1)), max(1, A))
    pygame.draw.line(men, (255, 230, 158, 190), (P(JB_L), P(LTOP)),
                     (P(JB_R), P(LTOP)), max(1, A))
    _clip(men, mask)
    surf.blit(men, (0, 0))

    # 7) KITSUNE specimen — aura BEHIND, sprite on top; scaled to sit INSIDE the
    #    squat vessel (content ~110x119 in 2x space => ~11px liquid margin all
    #    round; tails/ears verified within the rounded silhouette).
    sprite = build_kitsune(20)
    aura = build_kitsune_aura()
    fw, fh = P(119), P(156)
    fox = pygame.transform.smoothscale(sprite, (fw, fh))
    halo = pygame.transform.smoothscale(aura, (fw, fh))
    # the sprite's content sits high in its 64x84 canvas; nudge the canvas down
    # so the VISIBLE fox centres on the body middle.
    fr = fox.get_rect(center=(P(CXJ), P(BODY_CY + 15)))
    surf.blit(halo, fr.topleft)
    surf.blit(fox, fr.topleft)

    # 8) submerged GOLD CAST — a warm tint bleeding onto the fox BELOW the
    #    meniscus, ramping stronger toward the base, so the lower body reads as
    #    genuinely under the preservative liquid.
    cast = fox.copy()
    cast.fill((255, 176, 74, 255), special_flags=pygame.BLEND_RGBA_MULT)
    grad = pygame.Surface((fw, fh), pygame.SRCALPHA)
    for yy in range(fh):
        wy = (fr.top + yy) / A                       # world y in 2x px
        f = (wy - LTOP) / (LBOT - LTOP)
        a = int(150 * max(0.0, min(1.0, f)) ** 1.15)
        pygame.draw.line(grad, (255, 255, 255, a), (0, yy), (fw, yy))
    cast.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(cast, fr.topleft)
    # a faint additive warm glow at the very base sells the light through liquid.
    glowc = fox.copy()
    glowc.fill((120, 70, 16, 255), special_flags=pygame.BLEND_RGBA_MULT)
    gg = pygame.Surface((fw, fh), pygame.SRCALPHA)
    for yy in range(fh):
        wy = (fr.top + yy) / A
        f = (wy - (LBOT - 34)) / 34
        pygame.draw.line(gg, (255, 255, 255, int(90 * max(0.0, min(1.0, f)))),
                         (0, yy), (fw, yy))
    glowc.blit(gg, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(glowc, fr.topleft, special_flags=pygame.BLEND_ADD)

    # 9) legendary rising BUBBLES — 3-4 per side, LARGER (r=6-8) + well-spaced,
    #    pushed ~10px inward of the glass highlight strip so they never sit on
    #    the sheen. Varied radius => a rising-column rhythm that survives 1x.
    bubbles = [(GHI_L + 12, 168, 5), (GHI_L + 16, 138, 7), (GHI_L + 11, 110, 6),
               (GHI_L + 15, 84, 4),
               (GHI_R - 13, 160, 6), (GHI_R - 16, 130, 8), (GHI_R - 11, 102, 5),
               (GHI_R - 15, 80, 4)]
    for bx, by, br in bubbles:
        soft_glow(surf, P(bx), P(by), P(br + 2), WARM, 70, layers=6)
        pygame.draw.circle(surf, (255, 224, 150), (P(bx), P(by)), P(br),
                           max(1, A))
        pygame.draw.circle(surf, (255, 250, 226), (P(bx - br * 0.4),
                           P(by - br * 0.4)), max(1, A))

    # 10) SIDE-ONLY glass: a dark wall band then a bright vertical highlight on
    #     each curved edge (the whole glass read lives here; the pane over the
    #     fox stays clear). Clipped so the rounded shoulders fade the strips.
    gl = pygame.Surface((AW, AH), pygame.SRCALPHA)
    pygame.draw.rect(gl, (10, 8, 14, 120), (P(JB_L), P(JB_T), P(7), P(JB_B - JB_T)))
    pygame.draw.rect(gl, (10, 8, 14, 120), (P(JB_R - 7), P(JB_T), P(7),
                                            P(JB_B - JB_T)))
    for xi in range(P(GHI_L - 8), P(GHI_L + 8)):
        a = int(104 * max(0.0, 1 - abs(xi / A - GHI_L) / 8.0))
        if a > 0:
            pygame.draw.line(gl, (*GLASS_HI, a), (xi, P(JB_T + 4)), (xi, P(JB_B - 4)))
    for xi in range(P(GHI_R - 8), P(GHI_R + 8)):
        a = int(104 * max(0.0, 1 - abs(xi / A - GHI_R) / 8.0))
        if a > 0:
            pygame.draw.line(gl, (*GLASS_HI, a), (xi, P(JB_T + 4)), (xi, P(JB_B - 4)))
    _clip(gl, mask)
    surf.blit(gl, (0, 0))

    # 11) glass BASE thickness — a darker band + a thin refraction glint, then
    #     the gilded foot rim spanning the full jar width.
    band = pygame.Surface((AW, AH), pygame.SRCALPHA)
    for yy in range(P(172), P(184)):
        f = (yy / A - 172) / 12
        pygame.draw.line(band, (8, 6, 12, int(95 * f)),
                         (P(JB_L), yy), (P(JB_R), yy))
    pygame.draw.line(band, (210, 220, 244, 60), (P(JB_L + 8), P(174)),
                     (P(JB_R - 8), P(174)), max(1, A))
    _clip(band, mask)
    surf.blit(band, (0, 0))
    pygame.draw.rect(surf, BASE_RIM, (P(JB_L), P(184), P(JB_R - JB_L), P(5)),
                     border_radius=P(2))
    pygame.draw.rect(surf, (240, 198, 108), (P(JB_L), P(184), P(JB_R - JB_L),
                                             max(1, A)))
    pygame.draw.rect(surf, (118, 88, 30), (P(JB_L), P(188), P(JB_R - JB_L),
                                           max(1, A)))

    # 12) thin glass RIM outline so the silhouette reads as one form; a pale
    #     top-left kiss + a dark bottom-right contact, plus a shoulder sheen.
    rim = pygame.Surface((AW, AH), pygame.SRCALPHA)
    pygame.draw.rect(rim, (0, 0, 0, 60),
                     (P(JB_L - 1), P(JB_T - 1), P(JB_R - JB_L + 2), P(JB_B - JB_T + 2)),
                     width=max(1, A), border_radius=P(JB_RAD + 1))
    pygame.draw.rect(rim, (196, 206, 230, 70),
                     (P(JB_L), P(JB_T), P(JB_R - JB_L), P(JB_B - JB_T)),
                     width=max(1, A), border_radius=P(JB_RAD))
    surf.blit(rim, (0, 0))
    sh = pygame.Surface((AW, AH), pygame.SRCALPHA)
    pygame.draw.arc(sh, (214, 224, 244, 72),
                    (P(JB_L + 6), P(JB_T + 4), P(150), P(96)),
                    math.radians(82), math.radians(170), max(1, A * 2))
    surf.blit(sh, (0, 0))

    # 13) price-tag STRING + parchment TAG — the string hangs from JUST below the
    #     neck collar down the right gutter (never raking the specimen) to a tag
    #     pinned in the lower-right. Drawn before the collar so the knot tucks
    #     under it.
    string_pts = _bezier((198, 40), (272, 96), (250, 150), 24)
    pygame.draw.lines(surf, (70, 58, 40), False,
                      [(P(x), P(y)) for x, y in string_pts], max(1, A))
    pygame.draw.lines(surf, (140, 122, 88), False,
                      [(P(x), P(y - 0.6)) for x, y in string_pts], max(1, A))
    tx, ty, tw, th = 226, 146, 66, 26
    sh2 = pygame.Surface((AW, AH), pygame.SRCALPHA)
    pygame.draw.rect(sh2, (0, 0, 0, 90), (P(tx + 2), P(ty + 3), P(tw), P(th)),
                     border_radius=P(4))
    surf.blit(sh2, (0, 0))
    pygame.draw.rect(surf, PARCH, (P(tx), P(ty), P(tw), P(th)), border_radius=P(4))
    pygame.draw.rect(surf, (250, 242, 216),
                     (P(tx), P(ty), P(tw), P(th // 2)), border_radius=P(4))
    pygame.draw.rect(surf, (198, 182, 142), (P(tx), P(ty), P(tw), P(th)),
                     width=max(1, A), border_radius=P(4))
    pygame.draw.circle(surf, (150, 132, 96), (P(tx + 7), P(ty + 6)), P(2.4))
    pygame.draw.circle(surf, (60, 48, 30), (P(tx + 7), P(ty + 6)), P(2.4),
                       max(1, A))
    pf = _font(int(13 * A), True)
    price = pf.render("3,500", True, PARCH_INK)
    surf.blit(price, price.get_rect(center=(P(tx + 38), P(ty + 13))))

    # 14) rarity cue #1 — a THICK gilded NECK COLLAR where the jar meets the
    #     cork (strong gold, ~7px, top/bottom metal shading + two rivets). The
    #     single boldest rarity read at 1x.
    cl_x, cl_w, cl_y, cl_h = 114, 96, 27, 8
    pygame.draw.rect(surf, BRASS, (P(cl_x), P(cl_y), P(cl_w), P(cl_h)),
                     border_radius=P(3))
    pygame.draw.rect(surf, BRASS_HI, (P(cl_x), P(cl_y), P(cl_w), P(1.6)),
                     border_top_left_radius=P(3), border_top_right_radius=P(3))
    pygame.draw.rect(surf, BRASS_DK, (P(cl_x), P(cl_y + cl_h - 1.6), P(cl_w),
                                      P(1.6)))
    pygame.draw.rect(surf, (110, 80, 26), (P(cl_x), P(cl_y), P(cl_w), P(cl_h)),
                     width=max(1, A), border_radius=P(3))
    for rx in (cl_x + 12, cl_x + cl_w - 12):
        pygame.draw.circle(surf, BRASS_HI, (P(rx), P(cl_y + cl_h / 2)), P(1.6))
        pygame.draw.circle(surf, BRASS_DK, (P(rx), P(cl_y + cl_h / 2)), P(1.6),
                           max(1, A))

    # 15) CORK STOPPER — only the RAW cork cylinder pokes above y=0 (the
    #     deliberate frame-break). The brass cap + wax seal + monogram assembly
    #     sits INTACT + unclipped on the visible cork shoulder below y=0.
    pygame.draw.rect(surf, CORK, (P(134), P(-22), P(56), P(52)), border_radius=P(8))
    for gy in (-14, -4, 6):                          # cork grain striations
        pygame.draw.line(surf, CORK_DK, (P(140), P(gy)), (P(184), P(gy)),
                         max(1, A))
    pygame.draw.rect(surf, (206, 156, 104), (P(140), P(-18), max(1, A), P(46)))
    pygame.draw.rect(surf, CORK_DK, (P(134), P(-22), P(56), P(52)),
                     width=max(1, A), border_radius=P(8))
    # brass cap band clasping the cork base (intact, below y=0).
    pygame.draw.rect(surf, BRASS, (P(130), P(20), P(64), P(7)), border_radius=P(2))
    pygame.draw.rect(surf, BRASS_HI, (P(130), P(20), P(64), P(1.4)))
    pygame.draw.rect(surf, BRASS_DK, (P(130), P(25.6), P(64), P(1.4)))
    # WAX SEAL — a complete, unclipped emblem (top at y=1) with an impressed
    # fox-ear monogram, demoted to a bold chunky mark that still reads at 1x.
    scx, scy, sr = 162, 12, 11
    pygame.draw.circle(surf, WAX_DK, (P(scx), P(scy + 1)), P(sr + 1))
    pygame.draw.circle(surf, WAX, (P(scx), P(scy)), P(sr))
    pygame.draw.circle(surf, (244, 208, 116), (P(scx - 3), P(scy - 3)), P(3))
    pygame.draw.circle(surf, WAX_DK, (P(scx), P(scy)), P(sr), max(1, A))
    mg = (128, 90, 30)
    pygame.draw.polygon(surf, mg, [(P(157), P(scy + 1)), (P(158), P(scy - 6)),
                                   (P(162), P(scy + 1))])
    pygame.draw.polygon(surf, mg, [(P(162), P(scy + 1)), (P(166), P(scy - 6)),
                                   (P(167), P(scy + 1))])
    pygame.draw.polygon(surf, mg, [(P(158), P(scy)), (P(166), P(scy)),
                                   (P(162), P(scy + 6))])

    # thin card keyline so the body reads as a discrete card on the sheet.
    pygame.draw.rect(surf, (14, 12, 10), surf.get_rect(), max(1, A))

    return pygame.transform.smoothscale(surf, (CW, CH))


# ── comparison sources ────────────────────────────────────────────────────────
def before_card():
    """The live store card for skin_kitsune (BEFORE state)."""
    from game import store_cards, store_data
    # a real balance so the price chip tints as affordable/normal, not error.
    try:
        store_data.balance()
    except Exception:
        pass
    return store_cards.render_card("skin_kitsune", equipped=False, owned=True)


def round1_hero():
    """Crop the ROUND-1 hero card out of its saved sheet for a fair card-to-card
    comparison (the hero was blitted at (26,54), size 648x400)."""
    path = "/home/user/skybit/docs/item_card_redesign/specimen-jar/round_1.png"
    sheet = pygame.image.load(path).convert_alpha()
    return sheet.subsurface(pygame.Rect(26, 54, 648, 400)).copy()


def _panel(sheet, title, card_1x, x, y, cw, ch, tf, lf, note):
    """Draw one before/after panel: label, framed card scaled to cw x ch."""
    sheet.blit(tf.render(title, True, (240, 228, 210)), (x, y))
    scaled = pygame.transform.smoothscale(card_1x, (cw, ch))
    fr = pygame.Rect(x - 2, y + 22 - 2, cw + 4, ch + 4)
    pygame.draw.rect(sheet, (70, 58, 46), fr, width=2, border_radius=4)
    sheet.blit(scaled, (x, y + 22))
    sheet.blit(lf.render(note, True, (150, 138, 120)), (x, y + 22 + ch + 6))


def main():
    card = build_card()                              # 324x200 (2x in-game)
    before = before_card()                           # 162x100
    r1 = round1_hero()                                # 648x400 crop

    sheet_w, sheet_h = 486, 300
    sheet = pygame.Surface((sheet_w, sheet_h))
    for yy in range(sheet_h):
        sheet.fill(lerp_color((26, 22, 18), (18, 15, 12), yy / sheet_h),
                   (0, yy, sheet_w, 1))

    tf = _font(15, True)
    pf = _font(11, True)
    lf = _font(9, True)
    sheet.blit(tf.render("specimen-jar  ·  skin_kitsune  ·  LEGENDARY  ·  "
                         "round 2", True, (244, 232, 214)), (14, 8))

    cw, ch = 146, 90                                  # panel card size (162:100)
    col = sheet_w // 3
    gx = (col - cw) // 2
    y = 42
    _panel(sheet, "BEFORE", before, gx, y, cw, ch, pf, lf,
           "live store card")
    _panel(sheet, "ROUND-1", r1, col + gx, y, cw, ch, pf, lf,
           "tall jar · clipped seal")
    _panel(sheet, "ROUND-2", card, 2 * col + gx, y, cw, ch, pf, lf,
           "squat-wide · intact seal")

    # actual-size row: round-2 at true 1x (162x100) and a half-scale, so the
    # reviewer can judge whether the two bold rarity cues survive the downscale.
    ay = y + 22 + ch + 26
    sheet.blit(pf.render("ROUND-2 at true in-game scale", True, (236, 224, 206)),
               (14, ay - 20))
    one_x = pygame.transform.smoothscale(card, (162, 100))
    sheet.blit(one_x, (16, ay))
    pygame.draw.rect(sheet, (70, 58, 46), (15, ay - 1, 164, 102), width=1)
    sheet.blit(lf.render("162x100 (1x)", True, (150, 138, 120)), (16, ay + 104))
    half = pygame.transform.smoothscale(card, (81, 50))
    sheet.blit(half, (196, ay))
    pygame.draw.rect(sheet, (70, 58, 46), (195, ay - 1, 83, 52), width=1)
    sheet.blit(lf.render("81x50 (grid)", True, (150, 138, 120)), (196, ay + 54))

    # a stacked mini caption of the fixed AD notes.
    nx = 292
    notes = ["1.80:1 squat-wide vessel", "cork breaks frame · seal intact",
             "+ thick gold neck collar", "+ warm gold rim-glow",
             "dense gold fill + meniscus", "submerged gold cast on fox"]
    for i, n in enumerate(notes):
        sheet.blit(lf.render("· " + n, True, (198, 184, 158)),
                   (nx, ay - 4 + i * 15))

    out = "/home/user/skybit/docs/item_card_redesign/specimen-jar/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved:", out)


if __name__ == "__main__":
    main()
