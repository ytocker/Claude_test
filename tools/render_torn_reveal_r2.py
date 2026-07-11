"""Round-2 render harness for the item-card redesign — `torn-reveal` concept.

Round 1 sat the fox ON a shipped-style card and let a diagonal rip rake off both
card edges. The art-director's structural fix is a LAYER-ORDER inversion: the fox
is REVEALED THROUGH the tear, not composited on top of it. So the build order is
now strictly (1) dark lacquer card, (2) the fox in place behind, (3) its aura,
(4) a torn-paper sheet with a hole PUNCHED over the fox so the paper lips overlap
the fox and it only shows through the gap, (5) a rarity-coloured glow on the torn
lip, (6) embers anchored to the fox's head zone at the top of the gap.

Rarity now reads from exactly two bold signals that survive the 162x100 downscale:
the glowing tear edge in the legendary gold, and the sheer luminance of the fox
behind the rip. Everything micro was dropped.

Headless dummy SDL so it runs in CI/agent contexts without a display."""
import os
import sys
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color, NEAR_BLACK, WHITE
from game.store_cards import soft_glow, drop_shadow, font, m
from game.animal_kitsune import build_kitsune, build_kitsune_aura
from game import store_cards


# ── legendary tier ────────────────────────────────────────────────────────────
GEM = (255, 202, 104)
GLOW = (255, 168, 58)
DEEP = (150, 92, 22)

SS = 2                       # author at 2x (324x200), matching store_cards
CARD_W, CARD_H = 162, 100
W, H = CARD_W * SS, CARD_H * SS      # 324 x 200
RAD = m(store_cards.CARD_RAD)        # 34
INSET = m(6)                         # 12
BODY = pygame.Rect(INSET, INSET, W - INSET * 2, H - INSET * 2)

# ── tear geometry (2x author space, per the AD note) ─────────────────────────
# A gentle diagonal rip that PINCHES shut at both ends so it stays fully on-card:
# widest ~38px in the middle, closing to a point at x=40 (left) and x=284 (right).
TEAR_X0, TEAR_X1 = 40, 284
AXIS_Y0, AXIS_Y1 = 76, 120           # axis drifts down-right (gentle diagonal)
MAX_HALF = 19                        # half-opening at centre -> ~38px gap
FIBER = 6                            # torn paper-core band thickness


def _axis(x):
    t = max(0.0, min(1.0, (x - TEAR_X0) / (TEAR_X1 - TEAR_X0)))
    return AXIS_Y0 + (AXIS_Y1 - AXIS_Y0) * t


def _openf(x):
    """0 at the tear ends, 1 at the middle — the pinch profile."""
    t = (x - TEAR_X0) / (TEAR_X1 - TEAR_X0)
    if t <= 0 or t >= 1:
        return 0.0
    return math.sin(math.pi * t)


def _tear_edges():
    """Ragged top + bottom lips of the opening as vertex lists. The jag amplitude
    scales with the pinch profile so the edges meet cleanly at the two closed
    tips and only get ragged where the rip is actually open."""
    xs = list(range(TEAR_X0, TEAR_X1, 12)) + [TEAR_X1]
    rt = random.Random(71)
    rb = random.Random(72)
    top, bot = [], []
    for x in xs:
        of = _openf(x)
        a = _axis(x)
        h = MAX_HALF * of
        top.append((float(x), a - h + rt.uniform(-4, 4) * of))
        bot.append((float(x), a + h + rb.uniform(-4, 4) * of))
    return top, bot


def _lacquer(w, h):
    """Dark premium lacquer ground: a warm-to-black vertical value shift over the
    legendary DEEP tint, faintly scuffed so the surface reads as a lacquered
    card face rather than a flat swatch. Deterministic grain -> identical on both
    build targets."""
    top = lerp_color(DEEP, NEAR_BLACK, 0.60)
    bot = lerp_color(DEEP, NEAR_BLACK, 0.84)
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        body.fill((*lerp_color(top, bot, (y / max(1, h - 1)) ** 1.05), 255),
                  (0, y, w, 1))
    rnd = random.Random(4207)
    for _ in range(w * h // 30):
        x = rnd.randrange(w)
        y = rnd.randrange(h)
        v = rnd.randint(-12, 12)
        if v >= 0:
            body.set_at((x, y), (*lerp_color((255, 240, 210), (v, v, v), 0.0),
                                 min(255, v * 3)))
        else:
            body.set_at((x, y), (10, 6, 2, min(255, -v * 4)))
    return body


def render_torn_reveal():
    plate = pygame.Surface((W, H), pygame.SRCALPHA)

    # ── 1. dark lacquer card ground ──────────────────────────────────────────
    plate.blit(_lacquer(W, H), (0, 0))

    top, bot = _tear_edges()
    open_poly = [(int(x), int(y)) for x, y in top] + \
                [(int(x), int(y)) for x, y in reversed(bot)]

    # ── 2. the fox, IN PLACE behind the card (scaled to fit, ears+feet clear) ─
    # 130x170 in 2x space centred on (162,100): the tear gap then rakes across
    # the fox's face (top of gap) and body (middle), which is what shows through.
    tgt_w, tgt_h = 130, 170
    fx, fy = 162 - tgt_w // 2, 100 - tgt_h // 2
    fox = pygame.transform.smoothscale(build_kitsune(20), (tgt_w, tgt_h))
    fox_aura = pygame.transform.smoothscale(build_kitsune_aura(), (tgt_w, tgt_h))

    # ── 3. aura + a broad rarity bloom so the LUMINANCE behind the tear is the
    # loud rarity signal (survives the downscale even when detail doesn't). ────
    soft_glow(plate, 162, int(_axis(162)) - 4, 96, GLOW, 70, layers=10)
    soft_glow(plate, 168, int(_axis(168)) - 10, 60, GEM, 60, layers=8)
    plate.blit(fox_aura, (fx, fy), special_flags=pygame.BLEND_ADD)
    plate.blit(fox, (fx, fy))
    # a tight hot core right on the head zone so the revealed fox blazes.
    soft_glow(plate, 172, int(_axis(172)) - 6, 34,
              lerp_color(GEM, WHITE, 0.35), 55, layers=8)

    # ── 4. PUNCH the tear: a torn-paper sheet (same lacquer) with the opening
    # cut out, blitted OVER the fox so the paper lips overlap the fox edges. ───
    paper = _lacquer(W, H)
    # torn paper-core band: a slightly-expanded opening painted a warm light tan,
    # so when the true hole is subtracted a thin lighter torn edge is left behind.
    fiber_col = lerp_color(DEEP, WHITE, 0.42)
    fiber_poly = [(int(x), int(y - FIBER)) for x, y in top] + \
                 [(int(x), int(y + FIBER)) for x, y in reversed(bot)]
    pygame.draw.polygon(paper, fiber_col, fiber_poly)
    # a 1px darker line at the outer torn boundary so the lip reads as an edge.
    pygame.draw.lines(paper, lerp_color(DEEP, NEAR_BLACK, 0.5), False,
                      [(int(x), int(y - FIBER)) for x, y in top], m(0.8))
    pygame.draw.lines(paper, lerp_color(DEEP, NEAR_BLACK, 0.5), False,
                      [(int(x), int(y + FIBER)) for x, y in bot], m(0.8))
    # cut the real hole out of the paper -> the fox shows only through the gap.
    hole = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(hole, (255, 255, 255, 255), open_poly)
    paper.blit(hole, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    plate.blit(paper, (0, 0))

    # inner shadow the top lip casts DOWN into the gap -> "revealed through" depth.
    shade = pygame.Surface((W, H), pygame.SRCALPHA)
    for i, off in enumerate((2, 4, 6)):
        pygame.draw.lines(shade, (0, 0, 0, 70 - i * 20), False,
                          [(int(x), int(y + off)) for x, y in top], m(1))
    clip = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(clip, (255, 255, 255, 255), open_poly)
    shade.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    plate.blit(shade, (0, 0))

    # ── 5. rarity-coloured glow on the torn lip (one of the two bold signals) ─
    rim = pygame.Surface((W, H), pygame.SRCALPHA)
    top_i = [(int(x), int(y)) for x, y in top]
    bot_i = [(int(x), int(y)) for x, y in bot]
    for px, py in top_i[1:-1] + bot_i[1:-1]:
        soft_glow(rim, px, py, 5, GLOW, 55, layers=5)
    pygame.draw.lines(rim, (*GEM, 240), False, top_i, m(1.2))
    pygame.draw.lines(rim, (*lerp_color(GEM, WHITE, 0.4), 220), False,
                      [(x, y - 1) for x, y in top_i], m(0.7))
    pygame.draw.lines(rim, (*GLOW, 220), False, bot_i, m(1.2))
    plate.blit(rim, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── 6. embers anchored to the fox head zone (upper-centre of the gap) ─────
    embers = pygame.Surface((W, H), pygame.SRCALPHA)
    rnd = random.Random(88)
    for i in range(6):
        ex = int(158 + rnd.uniform(-12, 22))
        ey = int(_axis(ex) - 4 - i * 8 - rnd.uniform(0, 6))
        er = int(4 + rnd.uniform(0, 2.5))
        soft_glow(embers, ex, ey, er, GEM, 150, layers=6)
        pygame.draw.circle(embers, lerp_color(GEM, WHITE, 0.5),
                           (ex, ey), max(1, er // 2))
    plate.blit(embers, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── price tag: a plain white-on-dark pill in the lower-right margin ───────
    pw, ph = 92, 34
    px, py = W - INSET - 12 - pw, H - INSET - 12 - ph
    pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(pill, (16, 12, 20, 225), (0, 0, pw, ph), border_radius=m(6))
    pygame.draw.rect(pill, (*lerp_color(GEM, DEEP, 0.5), 150), (0, 0, pw, ph),
                     width=m(0.8), border_radius=m(6))
    # tiny procedural gold coin instead of an emoji glyph (no emoji in the ttf).
    ccx, ccy, cr = m(11), ph // 2, m(6)
    pygame.draw.circle(pill, GLOW, (ccx, ccy), cr)
    pygame.draw.circle(pill, GEM, (ccx, ccy), cr - m(1))
    pygame.draw.circle(pill, lerp_color(GEM, WHITE, 0.6), (ccx - m(1), ccy - m(1)),
                       max(1, m(1.6)))
    pf = font(10)
    ptxt = pf.render("3,500", True, WHITE)
    pill.blit(ptxt, ptxt.get_rect(midleft=(m(19), ph // 2)))
    sh = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120), (0, 0, pw, ph), border_radius=m(6))
    plate.blit(sh, (px + m(2), py + m(3)))
    plate.blit(pill, (px, py))

    # ── clip the full-bleed plate into the rounded card silhouette ───────────
    mask = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), BODY, border_radius=RAD)
    plate.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    out = pygame.Surface((W, H), pygame.SRCALPHA)
    drop_shadow(out, BODY, RAD, blur=m(6), alpha=150, dy=m(4))
    out.blit(plate, (0, 0))
    # dark keyline + inner gold bevel so it reads as a finished product card.
    pygame.draw.rect(out, (24, 12, 2), BODY, width=m(2), border_radius=RAD)
    inner = BODY.inflate(-m(2), -m(2))
    pygame.draw.rect(out, (*lerp_color(GEM, DEEP, 0.4), 170), inner,
                     width=m(1), border_radius=RAD - m(1))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Three-panel display sheet: BEFORE (shipped card) | ROUND-1 | ROUND-2.
# ─────────────────────────────────────────────────────────────────────────────
def _panel_card_before():
    return store_cards.render_card("skin_kitsune", equipped=False, owned=True)


def _label(sheet, text, col_x, col_w):
    lf = font(7)
    t = lf.render(text, True, (232, 224, 236))
    sheet.blit(t, t.get_rect(center=(col_x + col_w // 2, m(24))))


def render_sheet():
    col_w = 162
    sw, sh = col_w * 3, 300
    sheet = pygame.Surface((sw, sh), pygame.SRCALPHA)
    sheet.fill((26, 23, 30, 255))
    for i in range(1, 3):
        pygame.draw.line(sheet, (44, 40, 50), (col_w * i, m(18)),
                         (col_w * i, sh - m(18)))

    card_w, card_h = 150, 93
    cy = 118

    before = pygame.transform.smoothscale(_panel_card_before(), (card_w, card_h))
    r1 = pygame.image.load(
        "docs/item_card_redesign/torn-reveal/round_1.png").convert_alpha()
    r1 = pygame.transform.smoothscale(r1, (card_w, card_h))
    r2 = pygame.transform.smoothscale(render_torn_reveal(), (card_w, card_h))

    for i, (lbl, card) in enumerate((("BEFORE (shipped)", before),
                                     ("ROUND 1", r1),
                                     ("ROUND 2", r2))):
        col_x = i * col_w
        _label(sheet, lbl, col_x, col_w)
        sheet.blit(card, (col_x + (col_w - card_w) // 2, cy))
    return sheet


def main():
    os.makedirs("docs/item_card_redesign/torn-reveal", exist_ok=True)
    sheet = render_sheet()
    out = "docs/item_card_redesign/torn-reveal/round_2.png"
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
