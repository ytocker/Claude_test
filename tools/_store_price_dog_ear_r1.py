"""Round-1 render sheet for the DOG-EAR store-card price treatment.

Monkey-patches store_cards.price_chip with a bottom-left PEELED CORNER fold:
the price rides a lifted paper flap — a right-triangle whose crease diagonal
runs upper-right — casting a soft shadow onto the card, as if a physical price
sticker were peeling off the corner. The colour FLIPS with affordability: a
warm gold peel when the player can buy it, a cool pewter peel when locked (the
whole flap re-tints, not just the geometry). Renders it in-context on the two
hero cards in both wallet states plus a 4x zoom of the price corner.

Review-only tooling — never imported by the game.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game import store_catalog as cat
from game import store_data
from game.draw import lerp_color, WHITE
from game.hud import _font as hud_font


# ── peel palette ──────────────────────────────────────────────────────────────
# Affordable = warm gold peel (the canonical Ramp-A gold family the card already
# speaks); locked = cool pewter peel — a MANDATORY colour flip so the state reads
# at a glance, not just a geometry change.
GOLD_STOPS   = sc.GOLD_A_STOPS
GOLD_RIM_HI  = sc.GOLD_A_RIM_BRIGHT      # (255,240,190)
GOLD_RIM_LO  = sc.GOLD_A_RIM_DARK        # (86,50,8)
GOLD_NUM     = (52, 28, 4)               # dark relief numerals bitten into gold
GOLD_NUM_HI  = (255, 236, 182)

PEWTER_STOPS = [(0.0, (156, 160, 176)), (0.5, (120, 124, 142)), (1.0, (78, 82, 100))]
PEWTER_RIM_HI = (214, 218, 230)
PEWTER_RIM_LO = (54, 58, 74)
PEWTER_NUM    = (34, 38, 52)             # cool slate numerals
PEWTER_NUM_HI = (198, 204, 220)

ROT = 22                                 # peel lift angle (deg, CCW)
CORNER = (sc.m(6), sc.m(94))             # (12,188): card body bottom-left corner


def _rot_point(p, old, new, deg):
    """Where a point on the pre-rotation flap surface lands after
    pygame.transform.rotate — so the peel tip can be anchored to the card
    corner. pygame rotates CCW about the surface centre (screen y is down)."""
    w, h = old
    w2, h2 = new
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    dx, dy = p[0] - w / 2.0, p[1] - h / 2.0
    return (w2 / 2.0 + dx * c + dy * s,
            h2 / 2.0 - dx * s + dy * c)


def _emboss(surf, text, f, center, dark, hi):
    """Numerals bitten into the fold: a faint top highlight lip under a solid
    dark glyph, so the price reads as pressed INTO the paper, not printed on."""
    base = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(0.7))
    hl = base.copy()
    hl.fill((*hi, 130), special_flags=pygame.BLEND_RGBA_MULT)
    ink = base.copy()
    ink.fill((*dark, 255), special_flags=pygame.BLEND_RGBA_MULT)
    r = ink.get_rect(center=center)
    surf.blit(hl, (r.x, r.y - sc.m(0.8)))
    surf.blit(ink, r.topleft)


def _widest_price():
    """The fold must fit the LONGEST price in the catalog, not this card's — so
    every card's peel is the same size and the grid stays even."""
    f = sc.font(10)
    best, bw = "0", 0
    for v in cat.CATALOG.values():
        t = f"{v['cost']:,}"
        w = sc._glyph_base(t, f, 0).get_width()
        if w > bw:
            bw, best = w, t
    return best, bw


_WIDEST_TXT, _WIDEST_W = _widest_price()


def _label_strip(text, affordable):
    """The coin + price as a compact horizontal strip (transparent ground). It
    is later laid ALONG the flap's crease so a wide price fits a small corner
    triangle — a horizontal band never would (it pinches under the diagonal)."""
    f = sc.font(10)
    coin_r = sc.m(5.5)
    coin_d = coin_r * 2
    gap = sc.m(4)
    nw = sc._glyph_base(text, f, 0).get_width()
    lw = coin_d + gap + nw
    lh = max(coin_d, f.get_height())
    if affordable:
        num, num_hi, coin_rim, coin_tint = GOLD_NUM, GOLD_NUM_HI, sc.GOLD_A_COIN_RIM, None
    else:
        num, num_hi, coin_rim, coin_tint = PEWTER_NUM, PEWTER_NUM_HI, (110, 116, 134), (86, 92, 112, 150)
    lab = pygame.Surface((lw, lh), pygame.SRCALPHA)
    cy = lh // 2
    sc.coin_glyph(lab, coin_r, cy, coin_r, rim=coin_rim)
    if coin_tint:
        tw = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(tw, coin_tint, (coin_r, coin_r), coin_r)
        lab.blit(tw, (0, cy - coin_r))
    _emboss(lab, text, f, (coin_d + gap + nw // 2, cy), num, num_hi)
    return lab


def my_price_chip(surf, cx, cy, text, h, variant=1, affordable=True):
    """DOG-EAR peel: a lifted right-triangle flap in the card's bottom-left
    corner carrying the price along its crease. The whole flap re-tints gold
    (affordable) vs pewter (locked); a soft cast shadow sells the lift."""
    # Flap sized to hold the WIDEST catalog price along its hypotenuse so every
    # card's peel matches. Right angle at the corner tip; the hypotenuse is the
    # lifted crease.
    Hf = sc.m(24)
    Wf = sc.m(67)
    tri = [(0, Hf), (Wf, Hf), (0, 0)]
    hyp = math.hypot(Wf, Hf)
    ang = math.degrees(math.atan2(Hf, Wf))     # crease descends this much (upright)

    if affordable:
        stops, rim_hi, rim_lo = GOLD_STOPS, GOLD_RIM_HI, GOLD_RIM_LO
    else:
        stops, rim_hi, rim_lo = PEWTER_STOPS, PEWTER_RIM_HI, PEWTER_RIM_LO

    flap = pygame.Surface((Wf, Hf), pygame.SRCALPHA)
    grad = sc.vgrad_stops(Wf, Hf, 0, stops, 255, gamma=sc.GOLD_A_GAMMA)
    flap.blit(grad, (0, 0))
    mask = pygame.Surface((Wf, Hf), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), tri)
    flap.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # crease: dark keyline along the fold diagonal with a bright rim just inside,
    # so the lifted free edge catches light over a shaded fold; the two cut card
    # edges get a thin dark contact line for paper thickness.
    pygame.draw.line(flap, (*rim_lo, 235), (0, 0), (Wf, Hf), max(1, sc.m(1.4)))
    pygame.draw.line(flap, (*rim_hi, 225),
                     (sc.m(1.4), sc.m(1.2)), (Wf - sc.m(1.4), Hf), max(1, sc.m(1.0)))
    pygame.draw.line(flap, (*rim_lo, 165), (0, 0), (0, Hf), max(1, sc.m(0.8)))
    pygame.draw.line(flap, (*rim_lo, 165), (0, Hf), (Wf, Hf), max(1, sc.m(0.8)))

    # lay the coin+price along the crease (rotated to descend with it), nudged
    # perpendicular into the flap body so it rides the face, not the fold line.
    lab = _label_strip(text, affordable)
    rlab = pygame.transform.rotate(lab, ang)
    nrm = (-Wf / hyp, Hf / hyp)                 # unit normal toward the tip vertex
    off = lab.get_height() * 0.5 + sc.m(3)
    mid = (Wf / 2 + nrm[0] * off, Hf / 2 + nrm[1] * off)
    flap.blit(rlab, rlab.get_rect(center=mid))

    # locked peels earn a tiny padlock near the crease — a wordless "can't buy".
    if not affordable:
        lx, ly = int(Wf * 0.5), sc.m(4)
        pygame.draw.rect(flap, PEWTER_NUM, (lx, ly, sc.m(6), sc.m(4)),
                         border_radius=max(1, sc.m(1)))
        pygame.draw.arc(flap, PEWTER_NUM,
                        (lx + sc.m(1), ly - sc.m(3), sc.m(4), sc.m(6)),
                        math.radians(20), math.radians(160), max(1, sc.m(1)))

    # ── cast shadow FIRST (flat on the card), then the lifted flap on top ──
    shadow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    sh_tri = [(sc.m(6), sc.m(72)), (sc.m(74), sc.m(94)), (sc.m(6), sc.m(94))]
    pygame.draw.polygon(shadow, (0, 0, 0, 110), sh_tri)
    surf.blit(shadow, (sc.m(2), sc.m(2)))

    # rotate the whole flap up so the crease runs gently upper-right, then anchor
    # the right-angle tip to the card's bottom-left corner.
    rot = pygame.transform.rotate(flap, ROT)
    tip = _rot_point((0, Hf), (Wf, Hf), rot.get_size(), ROT)
    surf.blit(rot, (int(round(CORNER[0] - tip[0])), int(round(CORNER[1] - tip[1]))))
    return pygame.Rect(cx, cy, 1, 1)


sc.price_chip = my_price_chip            # patch BEFORE any draw_card call


# ── render helpers ────────────────────────────────────────────────────────────
def render_card_1x(sid, affordable):
    """Full v5 card at native 162x100: 2x author render then one smoothscale.
    Wallet is stubbed so state_chip resolves the affordability we want."""
    store_data.balance = (lambda: 10 ** 9) if affordable else (lambda: 0)
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       sc.CARD_W * sc.SS - 2 * sc.m(sc._INSET),
                       sc.CARD_H * sc.SS - 2 * sc.m(sc._INSET))
    sc.draw_card(big, sid, rect, equipped=False, secret=False)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def main():
    out_dir = "/home/user/skybit/docs/store_price_redesign/dog-ear"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")

    pad, gap = 20, 16
    header_h = 40
    label_h = 20

    specs = [
        ("skin_mummy",   True,  "MUMMY · EPIC · affordable"),
        ("skin_mummy",   False, "MUMMY · EPIC · locked"),
        ("skin_kitsune", True,  "KITSUNE · LEG · affordable"),
        ("skin_kitsune", False, "KITSUNE · LEG · locked"),
    ]
    cards = [(render_card_1x(sid, aff), lbl) for sid, aff, lbl in specs]
    cw, ch = cards[0][0].get_size()

    # 4x zoom of the price corner (bottom-left ~60x40 logical -> 240x160).
    crop_src = render_card_1x("skin_kitsune", True)
    crop = crop_src.subsurface(pygame.Rect(0, 60, 60, 40)).copy()
    zoom = pygame.transform.scale(crop, (240, 160))
    crop_src2 = render_card_1x("skin_kitsune", False)
    crop2 = crop_src2.subsurface(pygame.Rect(0, 60, 60, 40)).copy()
    zoom2 = pygame.transform.scale(crop2, (240, 160))

    row1_w = cw * 3 + gap * 2
    row2_w = cw + gap + 240 + gap + 240
    canvas_w = pad * 2 + max(row1_w, row2_w)
    row1_y = header_h
    row2_y = row1_y + ch + label_h + gap
    canvas_h = row2_y + max(ch, 160) + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))
    hf = hud_font(26, True)
    lf = hud_font(15)
    canvas.blit(hf.render("store price — dog-ear r1", True, (236, 232, 250)),
                (pad, 8))

    # row 1: three cards
    x = pad
    for card, lbl in cards[:3]:
        canvas.blit(card, (x, row1_y))
        canvas.blit(lf.render(lbl, True, (206, 202, 224)), (x, row1_y + ch + 3))
        x += cw + gap

    # row 2: fourth card + two zoom crops (affordable / locked)
    x = pad
    canvas.blit(cards[3][0], (x, row2_y))
    canvas.blit(lf.render(cards[3][1], True, (206, 202, 224)),
                (x, row2_y + ch + 3))
    x += cw + gap
    canvas.blit(zoom, (x, row2_y))
    canvas.blit(lf.render("4x zoom · affordable", True, (206, 202, 224)),
                (x, row2_y + 160 + 3))
    x += 240 + gap
    canvas.blit(zoom2, (x, row2_y))
    canvas.blit(lf.render("4x zoom · locked", True, (206, 202, 224)),
                (x, row2_y + 160 + 3))

    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())

    # ── sanity: warm gold must land in the affordable card's price corner ──
    probe = render_card_1x("skin_kitsune", True)
    hits = 0
    for yy in range(78, 98):
        for xx in range(6, 46):
            r, g, b, a = probe.get_at((xx, yy))
            if a > 40 and r > 150 and g > 110 and b < 130 and r > b:
                hits += 1
    print("gold peel pixels in affordable corner:", hits)
    assert hits > 60, "gold peel missing from bottom-left corner"
    print("sanity OK — gold dog-ear present in the price corner")


if __name__ == "__main__":
    main()
