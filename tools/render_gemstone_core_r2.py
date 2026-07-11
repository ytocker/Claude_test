"""Round-2 concept render for the `gemstone-core` item-card redesign.

Headless-only exploration harness (never imported by the game): authors the
legendary GEMSTONE-CORE card on a 2x supersample canvas and tiles a BEFORE /
ROUND-1 / ROUND-2 comparison sheet so the reviewer judges the round-2 fixes on
git.

Round-2 addresses the art-director notes over round 1:
  * Facets no longer read as a single card-centred sunburst. Each facet is a
    FLAT PLANE with its own directional gradient (bright at its own top-left
    edge, dark at its own bottom-right corner) off ONE fixed top-left light, and
    even/odd facets alternate LIGHTER/DARKER albedo so adjacent cut planes carry
    a ~50% luminance step — the read of a cut stone, not a fan of light.
  * Caustics are soft feathered additive streaks (refraction spots), not hard
    scratches, clustered in the upper-left where the light enters.
  * The fox is scaled to sit inside the centre spotlight chamber (no overflow),
    the aura is kept tight, and the chamber is brighter/warmer than the faceted
    edges so the hero reads as spotlit.
  * The price is an engraved horizontal capsule stamp at the bottom centre.
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

from game.draw import lerp_color, NEAR_BLACK, WHITE          # noqa: E402
from game.hud import _font                                    # noqa: E402
from game.parrot import _add_outline                          # noqa: E402
from game.animal_kitsune import build_kitsune, build_kitsune_aura  # noqa: E402


# ── legendary palette (locked: skin_kitsune legendary tier) ──────────────────
GEM = (255, 202, 104)          # #ffca68
GLOW = (255, 168, 58)          # #ffa83a
DEEP = (150, 92, 22)           # #965c16
CARD_BASE = (10, 8, 6)         # deep topaz interior, near-black warm
SPOT_WARM = (255, 224, 150)    # chamber spotlight tint

# 2x author canvas. Card centre (162, 100) is the spotlight chamber origin so
# the facets fan symmetrically outward AROUND the hero, not from an off-centre
# starburst point.
CW, CH = 324, 200
CENTER = (162, 100)
R_INNER = 22           # facet bases carry width so the fan never pinches to a dot
N_FACETS = 10          # 8-10: each plane keeps room to read as its own value

# Light direction: a single fixed top-left source. Every facet is shaded as a
# flat plane lit from here, so brightness comes from the plane's own
# orientation, never from distance to the card centre (which is what made
# round 1 read as a radial sunburst).
LIGHT = (0.70710678, 0.70710678)     # unit vector pointing DOWN-RIGHT into shade


# ── alternating facet albedo ─────────────────────────────────────────────────
# Even facets are a bright topaz plane; odd facets are a deep amber plane. Each
# still ramps bright->dark across ITS OWN span, but the base albedo step between
# neighbours (~50% mid-luminance) is what makes the cut read as separate planes.
LIGHT_HI = lerp_color(GEM, WHITE, 0.30)          # lit top-left lip of a bright plane
LIGHT_LO = lerp_color(GLOW, DEEP, 0.28)          # its shaded bottom-right corner
DARK_HI = lerp_color(DEEP, GLOW, 0.34)           # lit lip of a deep plane
DARK_LO = lerp_color(DEEP, NEAR_BLACK, 0.55)     # its shaded bottom-right corner
SEAM = lerp_color(DEEP, NEAR_BLACK, 0.42)        # thin cut-line between planes


def _ray_to_edge(cx, cy, ang):
    """Cast a ray from the chamber origin to the card rectangle boundary at
    `ang`, returning the perimeter hit point — the outer corner of a facet."""
    dx, dy = math.cos(ang), math.sin(ang)
    ts = []
    if dx > 1e-6:
        ts.append(((CW - 1) - cx) / dx)
    elif dx < -1e-6:
        ts.append((0 - cx) / dx)
    if dy > 1e-6:
        ts.append(((CH - 1) - cy) / dy)
    elif dy < -1e-6:
        ts.append((0 - cy) / dy)
    t = min(t for t in ts if t > 0)
    return (cx + dx * t, cy + dy * t)


def _flat_facet(surf, poly, hi, lo):
    """Fill one facet as a FLAT lit plane: a directional gradient running from
    the polygon's own top-left extent (bright `hi`) to its own bottom-right
    corner (dark `lo`), off the ONE fixed top-left light. Rendered by sweeping
    iso-value lines PERPENDICULAR to the light axis across the facet's own
    projection span, then masking to the polygon — so every facet carries its
    full tonal range regardless of where it sits on the card (no card-centred
    radial, hence no sunburst)."""
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    minx, maxx = int(min(xs)) - 1, int(max(xs)) + 2
    miny, maxy = int(min(ys)) - 1, int(max(ys)) + 2
    w, h = maxx - minx, maxy - miny
    if w <= 0 or h <= 0:
        return
    sub = pygame.Surface((w, h), pygame.SRCALPHA)
    lp = [(p[0] - minx, p[1] - miny) for p in poly]
    projs = [q[0] * LIGHT[0] + q[1] * LIGHT[1] for q in lp]
    pmin, pmax = min(projs), max(projs)
    span = max(1e-3, pmax - pmin)
    perp = (-LIGHT[1], LIGHT[0])           # iso-value lines run along here
    diag = math.hypot(w, h) + 2
    v = pmin
    while v <= pmax:
        t = (v - pmin) / span
        col = lerp_color(hi, lo, t)
        bx, by = v * LIGHT[0], v * LIGHT[1]         # a point whose proj == v
        pygame.draw.line(sub, (*col, 255),
                         (bx - perp[0] * diag, by - perp[1] * diag),
                         (bx + perp[0] * diag, by + perp[1] * diag), 2)
        v += 1.0
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), lp)
    sub.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sub, (minx, miny))


def _add_glow(surf, cx, cy, radius, color, peak, layers=12):
    """Additive feathered radial blob (spotlight warmth / aura)."""
    g = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
    c = radius + 1
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak * (1 - (i - 1) / layers) ** 2.0)
        if r <= 0 or a <= 0:
            continue
        pygame.draw.circle(g, (*color, a), (c, c), r)
    surf.blit(g, (cx - c, cy - c), special_flags=pygame.BLEND_ADD)


def _caustic(surf, cx, cy, length, thick, ang_deg, color, peak):
    """One soft refraction streak: a feathered elongated ellipse (bright core,
    edges fading to nothing), rotated to the light diagonal and blitted
    additively so it only ever brightens the facets it rakes across — a light
    spot, never a scratch line."""
    pad = thick + 4
    s = pygame.Surface((length + pad * 2, thick * 4 + pad * 2), pygame.SRCALPHA)
    cyc = s.get_height() // 2
    for r in range(thick + 4, 0, -1):
        a = int(peak * (1 - r / (thick + 4)) ** 1.4)
        if a <= 0:
            continue
        pygame.draw.ellipse(s, (*color, a),
                            (pad, cyc - r, length, r * 2))
    s = pygame.transform.rotate(s, ang_deg)
    r = s.get_rect(center=(cx, cy))
    surf.blit(s, r.topleft, special_flags=pygame.BLEND_ADD)


def build_card():
    surf = pygame.Surface((CW, CH), pygame.SRCALPHA)
    surf.fill((*CARD_BASE, 255))

    # ── faceted gemstone interior: a fan of flat lit planes around the chamber ─
    cx, cy = CENTER
    perim = [_ray_to_edge(cx, cy, -math.pi / 2 + 2 * math.pi * i / N_FACETS)
             for i in range(N_FACETS)]
    inner = [(cx + math.cos(-math.pi / 2 + 2 * math.pi * i / N_FACETS) * R_INNER,
              cy + math.sin(-math.pi / 2 + 2 * math.pi * i / N_FACETS) * R_INNER)
             for i in range(N_FACETS)]
    for i in range(N_FACETS):
        j = (i + 1) % N_FACETS
        poly = [inner[i], perim[i], perim[j], inner[j]]
        if i % 2 == 0:
            _flat_facet(surf, poly, LIGHT_HI, LIGHT_LO)
        else:
            _flat_facet(surf, poly, DARK_HI, DARK_LO)
    # Thin cut-lines down each shared radial seam so adjacent planes stay crisply
    # separated even where two dark corners meet.
    for i in range(N_FACETS):
        pygame.draw.line(surf, SEAM, inner[i], perim[i], 1)

    # ── centre spotlight chamber: brighter + warmer than the faceted edges ─────
    # A generous warm bloom pooled behind the hero so the fox reads as spotlit in
    # a bright chamber while the cut planes fall away darker to the rim.
    _add_glow(surf, cx, cy - 6, 78, SPOT_WARM, 120)
    _add_glow(surf, cx, cy - 6, 42, (255, 240, 200), 150)

    # ── caustics: soft feathered refraction streaks, upper-left light entry ────
    caust = [
        (96, 44, 70, 8, -34, (255, 246, 214), 58),
        (150, 30, 54, 6, -34, (255, 232, 176), 50),
        (66, 74, 60, 7, -34, (255, 238, 190), 54),
        (216, 40, 46, 6, -34, (255, 240, 200), 46),
        (128, 96, 44, 5, -34, (255, 244, 208), 42),
    ]
    for px, py, length, thick, ang, col, peak in caust:
        _caustic(surf, px, py, length, thick, ang, col, peak)

    # ── kitsune hero — aura BEHIND, sprite on top, fitted to the chamber ───────
    # Fox fitted to ~120x152 (no overflow), lifted slightly so its mass sits in
    # the bright chamber and the tails clear the price capsule below.
    sprite = _add_outline(build_kitsune(20))
    fox = pygame.transform.smoothscale(sprite, (120, 152))
    # Tight aura: scaled BELOW the fox box so its bloom stays within ~20px of the
    # sprite boundary instead of flooding the whole card as in round 1.
    aura = pygame.transform.smoothscale(build_kitsune_aura(), (104, 132))
    fcx, fcy = 162, 86
    surf.blit(aura, aura.get_rect(center=(fcx, fcy)).topleft)
    surf.blit(fox, fox.get_rect(center=(fcx, fcy)).topleft)

    # ── price: engraved horizontal capsule stamp, bottom-centre ────────────────
    _price_stamp(surf, 162, 178, "3,500")

    # thin card keyline so the body reads as a discrete card on the sheet.
    pygame.draw.rect(surf, lerp_color(DEEP, NEAR_BLACK, 0.2),
                     surf.get_rect(), 2, border_radius=6)
    return surf


def _small_coin(surf, cx, cy, r):
    """A tiny procedural gold coin glyph for the price stamp."""
    pygame.draw.circle(surf, (120, 74, 14), (cx, cy), r)          # dark rim
    pygame.draw.circle(surf, (244, 192, 88), (cx, cy), r - 2)     # face
    pygame.draw.circle(surf, (170, 112, 30), (cx, cy), r - 2, 1)  # inner ring
    pygame.draw.circle(surf, (255, 232, 158),
                       (cx - r // 3, cy - r // 3), max(1, r // 3))  # shine


def _price_stamp(surf, cx, cy, text):
    """Engraved horizontal capsule: deep-topaz body, thin gold rim, a small coin
    glyph + cream numerals — the price read at the bottom of the stone."""
    pf = _font(20, True)
    tw = pf.size(text)[0]
    coin_d = 20
    gap = 8
    inner = coin_d + gap + tw
    padx = 20
    pw = inner + padx * 2
    ph = 34
    rect = pygame.Rect(cx - pw // 2, cy - ph // 2, pw, ph)

    plaque = pygame.Surface((pw, ph), pygame.SRCALPHA)
    lr = pygame.Rect(0, 0, pw, ph)
    pygame.draw.rect(plaque, (26, 16, 0, 240), lr, border_radius=ph // 2)
    # engraved top-inner shadow + a thin gold rim for the stamped edge.
    pygame.draw.rect(plaque, (0, 0, 0, 150), lr, width=3, border_radius=ph // 2)
    pygame.draw.rect(plaque, (*GEM, 235), lr, width=2, border_radius=ph // 2)
    pygame.draw.rect(plaque, (255, 236, 176, 120), lr.inflate(-4, -4), width=1,
                     border_radius=ph // 2 - 2)
    surf.blit(plaque, rect.topleft)

    x = rect.x + padx
    _small_coin(surf, x + coin_d // 2, cy, coin_d // 2)
    x += coin_d + gap
    # cream numerals with a soft drop for the engraved read
    sh = pf.render(text, True, (0, 0, 0))
    sh.set_alpha(150)
    surf.blit(sh, sh.get_rect(midleft=(x, cy + 2)).topleft)
    num = pf.render(text, True, (248, 244, 230))
    surf.blit(num, num.get_rect(midleft=(x, cy)).topleft)


def _before_card():
    """The current live CONSTELLATION card for skin_kitsune (162x100)."""
    from game import store_cards
    return store_cards.render_card("skin_kitsune", equipped=False, owned=True)


def _fit(img, box_w, box_h):
    iw, ih = img.get_size()
    s = min(box_w / iw, box_h / ih)
    return pygame.transform.smoothscale(img, (max(1, int(iw * s)),
                                              max(1, int(ih * s))))


def main():
    card = build_card()
    card_1x = pygame.transform.smoothscale(card, (162, 100))

    before = _before_card()
    round1 = pygame.image.load(
        "/home/user/skybit/docs/item_card_redesign/gemstone-core/round_1.png")

    # ── comparison sheet: BEFORE · ROUND-1 · ROUND-2 ──────────────────────────
    SW, SH = 486, 300
    sheet = pygame.Surface((SW, SH))
    sheet.fill((18, 18, 26))
    col_w = SW // 3
    tf = _font(15, True)
    hf = _font(11, True)
    sheet.blit(tf.render("gemstone-core  ·  LEGENDARY  ·  round 2",
                         True, (236, 226, 244)), (14, 8))

    panels = [
        ("BEFORE  (live)", _fit(before, col_w - 24, 130)),
        ("ROUND 1", _fit(round1, col_w - 24, 210)),
        ("ROUND 2", _fit(card_1x, col_w - 24, 130)),
    ]
    for i, (label, img) in enumerate(panels):
        px = i * col_w
        sheet.blit(hf.render(label, True, (210, 202, 224)), (px + 14, 34))
        r = img.get_rect(center=(px + col_w // 2, 170))
        sheet.blit(img, r.topleft)

    # ROUND-2 also gets a 2x author-scale zoom under its panel so facet contrast
    # + caustics are judgeable at full resolution.
    zoom = _fit(card, col_w - 20, 96)
    zx = 2 * col_w
    sheet.blit(hf.render("round 2 · 2x author", True, (150, 150, 168)),
               (zx + 14, 250))
    zr = zoom.get_rect(midtop=(zx + col_w // 2, 264))
    sheet.blit(zoom, zr.topleft)

    out = "/home/user/skybit/docs/item_card_redesign/gemstone-core/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved:", out)


if __name__ == "__main__":
    main()
