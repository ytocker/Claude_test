"""Round-1 render harness for the item-card redesign: a BEFORE card (the shipped
CONSTELLATION store card) and the AFTER `torn-reveal` concept, both saved at 3x
for review. Headless dummy SDL so it runs in CI/agent contexts without a display.

The torn-reveal concept reframes the card as concealed kraft paper ripped open on
one clean diagonal to reveal the legendary fox behind warm gold light — rarity is
read from ember count + a two-strata tear depth, not a badge/ribbon."""
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
from game.store_cards import vgrad, vgrad_stops, soft_glow, drop_shadow, lerp_stops, font, m
from game.animal_kitsune import build_kitsune, build_kitsune_aura
from game import store_cards


# ── legendary tier ────────────────────────────────────────────────────────────
GEM = (255, 202, 104)
GLOW = (255, 168, 58)
DEEP = (150, 92, 22)

SS = 2                       # author at 2x (324x200), matching store_cards
CARD_W, CARD_H = 162, 100
W, H = CARD_W * SS, CARD_H * SS      # 324 x 200


def kraft_body(w, h, radius):
    """Matte kraft-paper ground: a slightly-warmed vertical value shift over the
    legendary DEEP tint, scuffed with low-contrast value noise so the surface
    reads as something concealed rather than a flat swatch."""
    top = lerp_color(DEEP, WHITE, 0.06)
    bot = lerp_color(DEEP, NEAR_BLACK, 0.30)
    body = vgrad(w, h, radius, top, bot, 255, gamma=1.05)
    # deterministic grain so both build targets render identically.
    rnd = random.Random(4207)
    grain = pygame.Surface((w, h), pygame.SRCALPHA)
    for _ in range(w * h // 22):
        x = rnd.randrange(w)
        y = rnd.randrange(h)
        v = rnd.randint(-16, 16)
        if v >= 0:
            grain.set_at((x, y), (255, 240, 210, min(255, v * 4)))
        else:
            grain.set_at((x, y), (20, 10, 0, min(255, -v * 4)))
    # keep grain inside the rounded body
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
    grain.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    body.blit(grain, (0, 0))
    return body


def jagged_edge(x0, x1, y_at, amp, seed, step=10):
    """One crisp hand-cut jagged line across the card — a sparse random walk of
    vertices (not fractal frizz) sampled along x, offset from the diagonal y_at."""
    rnd = random.Random(seed)
    pts = []
    x = x0
    while x <= x1:
        pts.append((x, y_at(x) + rnd.uniform(-amp, amp)))
        x += step
    pts.append((x1, y_at(x1) + rnd.uniform(-amp, amp)))
    return pts


def render_torn_reveal():
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    rad = m(store_cards.CARD_RAD)

    # soft cast shadow so the card sits on the store grid like the shipped card.
    drop_shadow(surf, pygame.Rect(m(6), m(6), W - m(12), H - m(12)), rad,
                blur=m(6), alpha=150, dy=m(4))
    body_rect = pygame.Rect(m(6), m(6), W - m(12), H - m(12))
    bw, bh = body_rect.size

    # ── kraft-paper concealed ground ─────────────────────────────────────────
    body = kraft_body(bw, bh, rad)

    # The diagonal tear axis: upper-left toward lower-right, y sweeps ~62->128
    # (1x) as x crosses the card, so the rip rakes down toward the price stub.
    def axis(x):
        t = x / W
        return (62 * SS) * (1 - t) + (128 * SS) * t

    # Two torn strata: a deeper peeled layer behind, then the top rip — so the
    # reveal reads TWO paper layers deep (rarity = tear depth).
    upper_top = jagged_edge(0, W, lambda x: axis(x) - 30 * SS, 5 * SS, seed=11)
    upper_bot = jagged_edge(0, W, lambda x: axis(x) - 8 * SS, 5 * SS, seed=12)
    lower_bot = jagged_edge(0, W, lambda x: axis(x) + 20 * SS, 6 * SS, seed=13)

    # The OPENING mask: everything between the top rip lip and the bottom rip lip
    # is torn away, exposing the light + fox behind.
    opening = pygame.Surface((bw, bh), pygame.SRCALPHA)
    open_poly = upper_bot + list(reversed(lower_bot))
    pygame.draw.polygon(opening, (255, 255, 255, 255), open_poly)
    # punch the opening out of the kraft body
    body.blit(opening, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    # keep the kraft body inside the rounded card silhouette
    rmask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(rmask, (255, 255, 255, 255), (0, 0, bw, bh), border_radius=rad)
    body.blit(rmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # ── the warm light behind the rip (drawn onto the card first) ─────────────
    # Per-column vertical gradient centred on the diagonal so the light hugs the
    # tear at every x, brightest at the midline fading over ±60px(1x).
    glow_band = pygame.Surface((bw, bh), pygame.SRCALPHA)
    span = 60 * SS
    for x in range(bw):
        mid = axis(x + body_rect.x) - body_rect.y
        y0 = int(max(0, mid - span))
        y1 = int(min(bh, mid + span))
        for y in range(y0, y1):
            f = abs(y - mid) / span
            a = int(230 * (1 - f) ** 1.7)
            if a <= 0:
                continue
            col = lerp_stops([(0.0, (255, 236, 190)), (0.5, GEM), (1.0, GLOW)], f)
            glow_band.set_at((x, y), (*col, a))
    # clip the light to the opening (a touch WIDER than the top rip) so the warm
    # gold only reads through the rip and along the exposed second stratum.
    open_full = pygame.Surface((bw, bh), pygame.SRCALPHA)
    deep_top = jagged_edge(0, W, lambda x: axis(x) - 22 * SS, 5 * SS, seed=21)
    deep_poly = deep_top + list(reversed(lower_bot))
    pygame.draw.polygon(open_full, (255, 255, 255, 255), deep_poly)
    glow_band.blit(open_full, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Compose: light first, then kraft (with hole) on top so the rip lips frame it.
    plate = pygame.Surface((bw, bh), pygame.SRCALPHA)
    plate.blit(glow_band, (0, 0))
    plate.blit(body, (0, 0))

    # ── the fox composited INTO the opening (aura behind, then sprite) ────────
    sprite = build_kitsune(20)          # 64x84 mid-flap
    aura = build_kitsune_aura()         # 64x84 baked gold aura
    tgt_w, tgt_h = 160, 210
    fox = pygame.transform.smoothscale(sprite, (tgt_w, tgt_h))
    fox_aura = pygame.transform.smoothscale(aura, (tgt_w, tgt_h))
    fx = bw // 2 - tgt_w // 2
    fy = bh // 2 - tgt_h // 2
    # aura is allowed to bloom across the whole card; the sprite stays the hero.
    plate.blit(fox_aura, (fx, fy), special_flags=pygame.BLEND_ADD)
    plate.blit(fox, (fx, fy))

    # ── curled-paper side triangles: thin dark curls at the tear ends so the
    # torn strata read as peeling back into both margins, never crossing the fox.
    curl_l = pygame.Surface((bw, bh), pygame.SRCALPHA)
    ml = axis(body_rect.x) - body_rect.y
    pygame.draw.polygon(curl_l, (40, 22, 4, 200),
                        [(0, ml - 22 * SS), (34 * SS, ml - 4 * SS),
                         (0, ml + 6 * SS)])
    pygame.draw.polygon(curl_l, (90, 54, 14, 180),
                        [(0, ml - 22 * SS), (24 * SS, ml - 8 * SS),
                         (0, ml - 2 * SS)])
    plate.blit(curl_l, (0, 0))
    mr = axis(body_rect.x + bw) - body_rect.y
    curl_r = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(curl_r, (40, 22, 4, 200),
                        [(bw, mr - 6 * SS), (bw - 34 * SS, mr + 8 * SS),
                         (bw, mr + 24 * SS)])
    pygame.draw.polygon(curl_r, (90, 54, 14, 180),
                        [(bw, mr + 2 * SS), (bw - 24 * SS, mr + 12 * SS),
                         (bw, mr + 22 * SS)])
    plate.blit(curl_r, (0, 0))

    # ── the bright legendary rim glowing along the torn lip ───────────────────
    lip_upper = [(px, py) for px, py in upper_bot]
    lip_lower = [(px, py) for px, py in lower_bot]
    rim = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.lines(rim, (*GEM, 235), False, lip_upper, max(1, m(1.3)))
    pygame.draw.lines(rim, (*lerp_color(GEM, WHITE, 0.3), 200), False,
                      [(x, y - 1) for x, y in lip_upper], max(1, m(0.7)))
    pygame.draw.lines(rim, (*GLOW, 200), False, lip_lower, max(1, m(1.2)))
    # keep the rim off the fox silhouette: mask out the fox's opaque area.
    foxmask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    foxmask.fill((255, 255, 255, 255))
    fm = fox.copy()
    fm.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    foxmask.blit(fm, (fx, fy), special_flags=pygame.BLEND_RGBA_SUB)
    rim.blit(foxmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    plate.blit(rim, (0, 0))

    # ── rising ember motes (legendary = 6, large + lazy, soft halo) ───────────
    embers = pygame.Surface((bw, bh), pygame.SRCALPHA)
    rnd = random.Random(88)
    for i in range(6):
        ex = int(bw * (0.18 + 0.64 * (i + rnd.uniform(-0.2, 0.2)) / 6))
        ey = int(axis(ex + body_rect.x) - body_rect.y - (16 + i * 9) * SS)
        er = int((6 + rnd.uniform(0, 4)) * SS)
        soft_glow(embers, ex, ey, er, GEM, 140, layers=6)
        halo = pygame.Surface((er * 2 + 4, er * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(halo, (*lerp_color(GEM, WHITE, 0.4), 210),
                           (er + 2, er + 2), max(1, er // 2))
        embers.blit(halo, (ex - er - 2, ey - er - 2), special_flags=pygame.BLEND_ADD)
    plate.blit(embers, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── price stub: paper tag with punched hole + string, lower-right margin ──
    stub_w, stub_h = 70 * SS // SS, 30  # authored in 1x -> *SS below
    sw, sh = m(70), m(30)
    sx, sy = bw - sw - m(6), bh - sh - m(8)
    stub = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.rect(stub, (232, 218, 178), (0, 0, sw, sh), border_radius=m(3))
    pygame.draw.rect(stub, lerp_color((232, 218, 178), NEAR_BLACK, 0.18),
                     (0, 0, sw, sh), width=max(1, m(1)), border_radius=m(3))
    # punched hole + a small dark ring
    hx, hy = m(9), sh // 2
    pygame.draw.circle(stub, (60, 44, 18), (hx, hy), m(3.2))
    pygame.draw.circle(stub, (150, 128, 82), (hx, hy), m(3.2), max(1, m(0.8)))
    pf = font(11.5)
    ptxt = pf.render("3,500", True, (100, 60, 15))
    stub.blit(ptxt, ptxt.get_rect(center=(m(9) + (sw - m(9)) // 2 + m(3), sh // 2)))
    # string from the tear lip to the punched hole
    lip_x = sx + hx
    lip_y = int(axis(lip_x + body_rect.x) - body_rect.y)
    pygame.draw.line(plate, (60, 44, 18), (lip_x, max(0, lip_y)),
                     (sx + hx, sy + hy), max(1, m(1.4)))
    # drop shadow under the stub so it lifts off the kraft margin
    sh_s = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.rect(sh_s, (0, 0, 0, 120), (0, 0, sw, sh), border_radius=m(3))
    plate.blit(sh_s, (sx + m(2), sy + m(3)))
    plate.blit(stub, (sx, sy))

    # bevel/keyline the card edge so it reads as a finished product card.
    pygame.draw.rect(plate, (30, 16, 2), (0, 0, bw, bh), width=max(1, m(2)),
                     border_radius=rad)
    pygame.draw.rect(plate, (*lerp_color(GEM, DEEP, 0.4), 180),
                     (m(1), m(1), bw - m(2), bh - m(2)), width=max(1, m(1)),
                     border_radius=rad - m(1))

    surf.blit(plate, body_rect.topleft)
    return surf


def main():
    # ── BEFORE: the shipped CONSTELLATION card ────────────────────────────────
    card = store_cards.render_card("skin_kitsune", equipped=False, owned=True)
    before_display = pygame.transform.smoothscale(card, (486, 300))
    os.makedirs("docs/item_card_redesign/before", exist_ok=True)
    pygame.image.save(before_display, "docs/item_card_redesign/before/round_1.png")

    # ── AFTER: torn-reveal concept ────────────────────────────────────────────
    big = render_torn_reveal()                              # 324x200
    final = pygame.transform.smoothscale(big, (CARD_W, CARD_H))    # 162x100
    show = pygame.transform.smoothscale(final, (486, 300))         # 3x showcase
    os.makedirs("docs/item_card_redesign/torn-reveal", exist_ok=True)
    pygame.image.save(show, "docs/item_card_redesign/torn-reveal/round_1.png")

    print("saved before + torn-reveal")


if __name__ == "__main__":
    main()
