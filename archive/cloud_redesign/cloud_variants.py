"""Round-1 cloud-renderer explorations for the shan-shui sky.

The shipped `game.draw.draw_cloud` paints a stack of white circles with
fixed RGB and no biome coupling — that reads as Eurocentric cumulus puffs
and breaks the East-Asian ink-wash contract that V14 backdrop + pagoda
pillars already enforce. Each variant here brings a distinct calligraphic
silhouette family (wash / scroll / bank / streak / curl) and tints itself
from the live biome palette so dawn warm, dusk cool, and night ghostly
read consistently with the rest of the scene.

Drop-in: every variant matches `draw_cloud_<name>(surf, x, y, palette,
scale=1.0)`. The harness adapts the existing `draw_cloud` signature
(x, y, scale, variant) by injecting `palette` from the phase being
rendered, so live-game integration only swaps the call wrapper, never
the call sites.
"""
from __future__ import annotations

import math
import pygame


# ── shared palette / colour helpers ──────────────────────────────────────────
#
# All variants ask the biome for a sky-aware cloud tint instead of the
# hard-coded white the legacy renderer uses. The cloud body lerps between
# horizon (warm at sunset, cool at dawn) and sky_bot (cooler base) so the
# cloud sits ON the sky band it's drawn over rather than punching a hole
# through it. Night phases lean toward sky_bot + a touch of horizon so the
# cloud reads as a luminous-pale shape, never a daylight blob.


def _cloud_body_color(palette: dict) -> tuple[int, int, int]:
    horizon = palette['horizon']
    sky_bot = palette['sky_bot']
    # Mostly horizon (warm/cool tinted) with a softener pulled from
    # sky_bot — keeps the cloud reading as lit air, not paint.
    return (
        min(255, int(horizon[0] * 0.70 + sky_bot[0] * 0.30) + 25),
        min(255, int(horizon[1] * 0.70 + sky_bot[1] * 0.30) + 25),
        min(255, int(horizon[2] * 0.70 + sky_bot[2] * 0.30) + 25),
    )


def _ink_shadow_color(palette: dict) -> tuple[int, int, int]:
    # The "wet ink" edge of a calligraphic wash — pulls from the deepest
    # palette key around (mtn_far → sky_top) so it stays in-key.
    far = palette['mtn_far']
    top = palette['sky_top']
    return (
        max(0, int(far[0] * 0.55 + top[0] * 0.45) - 10),
        max(0, int(far[1] * 0.55 + top[1] * 0.45) - 10),
        max(0, int(far[2] * 0.55 + top[2] * 0.45) - 10),
    )


def _lit_edge_color(palette: dict) -> tuple[int, int, int]:
    # The single bright sliver on the cloud's sunlit side — picked from
    # horizon and pushed brighter so it pops even in dusk/night phases.
    h = palette['horizon']
    return (
        min(255, h[0] + 30),
        min(255, h[1] + 30),
        min(255, h[2] + 30),
    )


def _lerp(a, b, t):
    return a + (b - a) * t


def _lerp_color(a, b, t):
    return (
        int(_lerp(a[0], b[0], t)),
        int(_lerp(a[1], b[1], t)),
        int(_lerp(a[2], b[2], t)),
    )


def _alpha_surf(w, h) -> pygame.Surface:
    return pygame.Surface((max(2, int(w)), max(2, int(h))), pygame.SRCALPHA)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 1 — Sumi-e Ink-Wash Wisp
# Research:
#   https://www.asianbrushpainter.com/blogs/kb/the-use-of-ink
#   https://www.shimizuart.org/post/sumi-e-the-art-of-ink-wash-painting
#
# Single calligraphic stroke: loaded-brush "head" with wet pooled ink,
# tapering into a dry-brush "flying-white" (kasure) tail of broken ink
# specks. Direction is near-horizontal with a subtle downward swoop so
# the body weight reads on the leading edge, exactly how a sumi-e cloud
# is laid down in one motion.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_sumie(surf, x, y, palette, scale=1.0):
    """Calligraphic single-stroke wisp — wet head, flying-white tail."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    # Stroke length and head radius scale together.
    length = int(80 * scale)
    head_r = int(14 * scale)
    pad = head_r + 6
    surf_w = length + pad * 2
    surf_h = head_r * 3 + 8
    s = _alpha_surf(surf_w, surf_h)

    cy = surf_h // 2

    # Wet head — overlapping discs of decreasing radius give the
    # "loaded brush touching down" lozenge silhouette.
    for i, (dx, ry, rad, a) in enumerate((
            (0, 0, head_r, 235),
            (head_r // 2, -2, head_r - 2, 220),
            (head_r, 2, head_r - 4, 210),
            (-2, 4, head_r - 5, 200),
    )):
        pygame.draw.ellipse(
            s, (*body, a),
            pygame.Rect(pad + dx - rad, cy + ry - rad,
                        rad * 2, int(rad * 1.6)))

    # Tapered body — line of ellipses shrinking toward the tail, with
    # a slight downward arc so the stroke looks brushed, not stamped.
    n_body = 9
    for i in range(n_body):
        t = i / (n_body - 1)
        bx = pad + head_r + int(t * (length - head_r))
        by = cy + int(math.sin(t * math.pi * 0.6) * 2 * scale)
        rad = max(2, int((head_r - 3) * (1 - t * 0.85)))
        a = int(_lerp(210, 120, t))
        pygame.draw.ellipse(
            s, (*body, a),
            pygame.Rect(bx - rad, by - rad // 2,
                        rad * 2, max(3, int(rad * 1.1))))

    # Flying-white kasure tail — broken ink specks scattered past the
    # body end, alpha falling to zero. Pseudo-random but seeded off the
    # spawn coords so the pattern is stable per cloud.
    rng_seed = (int(x) * 73856093) ^ (int(y) * 19349663)
    for k in range(14):
        t = 0.55 + (k / 14) * 0.55
        if t > 1.0:
            break
        tx = pad + head_r + int(t * (length - head_r))
        jitter = ((rng_seed >> (k % 16)) & 0x7) - 3
        ty = cy + int(math.sin(t * math.pi * 0.7) * 2 * scale) + jitter
        rad = max(1, int(3 * scale * (1 - t * 0.7)))
        a = int(_lerp(160, 0, t))
        if a <= 0:
            continue
        pygame.draw.circle(s, (*body, a), (tx, ty), rad)

    # Single ink-shadow underline along the bottom of the wet head — the
    # "pooled" edge where the brush sat longest. Thin, low-alpha.
    pygame.draw.ellipse(
        s, (*edge, 90),
        pygame.Rect(pad - 2, cy + head_r // 2 - 1,
                    head_r * 3, max(3, int(head_r * 0.6))))

    # Sunlit highlight kiss on the top-left of the head.
    pygame.draw.ellipse(
        s, (*lit, 140),
        pygame.Rect(pad - 4, cy - head_r + 2,
                    head_r + 4, max(3, head_r // 2)))

    surf.blit(s, (int(x - pad), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 2 — Ruyi Auspicious Scroll (祥云)
# Research:
#   https://en.wikipedia.org/wiki/Xiangyun_(Auspicious_clouds)
#   https://www.chinese-showcase.com/blogs/chinese-symbols/auspicious-clouds-pattern-xiangyun-meaning-symbolism-spiritual-significance
#
# Vector-clean 4-lobe scroll silhouette descended from the Beijing 2008
# torch "Cloud of Promise" and the Tang/Ming porcelain motif. Distinct
# coiled spirals on each lobe + a wide base ribbon. Outlined in a soft
# darker keyline so it reads as a heraldic / decorative shape, not a
# puff of vapour.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_ruyi(surf, x, y, palette, scale=1.0):
    """Tang/Ming auspicious-cloud scroll — 4 lobes + coiled spirals."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    w = int(96 * scale)
    h = int(46 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # The four lobes — descending radii right-to-left mimic the Ming
    # "trailing 3-cloud" scroll layout, with the dominant lobe on the
    # leading (right) side. Coordinates are fractions of the cell.
    lobes = (
        (int(w * 0.18), cy - int(h * 0.05), int(h * 0.36)),
        (int(w * 0.40), cy - int(h * 0.18), int(h * 0.42)),
        (int(w * 0.62), cy - int(h * 0.10), int(h * 0.38)),
        (int(w * 0.82), cy - int(h * 0.02), int(h * 0.32)),
    )

    # 1. Soft ink-shadow halo offset down-right, sells the scroll as a
    #    flat decorative object rather than a vapour ball.
    for (lx, ly, lr) in lobes:
        pygame.draw.circle(
            s, (*edge, 70), (lx + pad + 2, ly + 3), lr + 1)
    # Base ribbon connecting the lobes — Tang-style wide trailing band.
    base_pts = [
        (pad + int(w * 0.10), cy + int(h * 0.05)),
        (pad + int(w * 0.30), cy + int(h * 0.18)),
        (pad + int(w * 0.55), cy + int(h * 0.20)),
        (pad + int(w * 0.78), cy + int(h * 0.14)),
        (pad + int(w * 0.90), cy + int(h * 0.04)),
        (pad + int(w * 0.78), cy + int(h * 0.22)),
        (pad + int(w * 0.55), cy + int(h * 0.28)),
        (pad + int(w * 0.30), cy + int(h * 0.26)),
        (pad + int(w * 0.12), cy + int(h * 0.18)),
    ]
    pygame.draw.polygon(s, (*edge, 60),
                        [(px + 2, py + 3) for px, py in base_pts])
    pygame.draw.polygon(s, (*body, 240), base_pts)

    # 2. Lobe fills.
    for (lx, ly, lr) in lobes:
        pygame.draw.circle(s, (*body, 245), (lx + pad, ly), lr)

    # 3. Coiled spiral keyline on each lobe — the signature ruyi curl.
    for (lx, ly, lr) in lobes:
        cx_l = lx + pad
        # Outline ring.
        pygame.draw.circle(s, (*edge, 150), (cx_l, ly), lr, 2)
        # Inner spiral arc — quarter sweep done as a short arc rect.
        inner = max(3, lr - 5)
        rect = pygame.Rect(cx_l - inner, ly - inner, inner * 2, inner * 2)
        pygame.draw.arc(s, (*edge, 170), rect,
                        math.radians(20), math.radians(200), 2)
        # Pinpoint at the spiral's heart.
        pygame.draw.circle(s, (*edge, 200), (cx_l - 1, ly + 1), 1)

    # 4. Base-ribbon keyline.
    pygame.draw.lines(s, (*edge, 170), False, base_pts[:5], 2)
    pygame.draw.lines(s, (*edge, 130), False, base_pts[4:], 1)

    # 5. Sunlit crescents on top-left of each lobe.
    for (lx, ly, lr) in lobes:
        cx_l = lx + pad
        pygame.draw.arc(s, (*lit, 200),
                        pygame.Rect(cx_l - lr + 2, ly - lr + 2,
                                    lr * 2 - 4, lr * 2 - 4),
                        math.radians(110), math.radians(220), 2)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 3 — Yúnhǎi Cloud-Sea Bank (雲海)
# Research:
#   https://learnjapanese123.com/unkai-japans-top-sea-of-clouds-spots/
#   https://www.1000museums.com/shop/art/hiroshi-yoshida-sea-of-clouds-unkai-ho-o-san/
#
# Horizontal banded cloud-sea like Hiroshi Yoshida's "Unkai" or the
# distant cloud bands in Tang-era shan-shui. Long elliptical strata
# stacked in 3 tiers, gradient fade top-to-bottom so the bottom edge
# dissolves into the sky. Reads as a far-off ridge of cloud, not a
# discrete puff — anchors the horizon line in shan-shui style.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_yunhai(surf, x, y, palette, scale=1.0):
    """Horizontal cloud-sea bank — stacked strata reading as distance."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    w = int(110 * scale)
    h = int(42 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)

    # 3 stacked strata, each a flattened ellipse. Centre band is widest;
    # top is narrower and brighter (lit ridge), bottom is thinner and
    # fades to zero (dissolves into sky_bot).
    strata = (
        # (centre_y_frac, half_w_frac, half_h, alpha)
        (0.22, 0.78, 5, 210),  # top ridge — bright, narrower
        (0.50, 1.00, 7, 235),  # mid bank — densest, widest
        (0.78, 0.88, 6, 175),  # bottom fade
    )

    cy = pad + h // 2
    cx = pad + w // 2

    # Shadow halo under the densest stratum first.
    pygame.draw.ellipse(
        s, (*edge, 50),
        pygame.Rect(pad + 4, cy + 2, w - 8, int(h * 0.55)))

    for (yfrac, wfrac, hh, a) in strata:
        band_y = pad + int(h * yfrac)
        half_w = int(w * 0.5 * wfrac)
        bx = cx - half_w
        # Slight irregular silhouette: 3 overlapping ellipses per band
        # so the top edge has a soft lump structure (3 distant peaks).
        for k, (ox, ow) in enumerate((
                (-half_w + half_w // 6, int(half_w * 0.95)),
                (0, half_w),
                (half_w - half_w // 6 - int(half_w * 0.9),
                 int(half_w * 0.95)),
        )):
            rect = pygame.Rect(cx + ox - ow // 2 + 0, band_y - hh,
                               ow, hh * 2)
            pygame.draw.ellipse(s, (*body, a), rect)

    # Lit crest along the top ridge — a thin highlight stroke.
    top_y = pad + int(h * 0.22) - 4
    pygame.draw.arc(s, (*lit, 200),
                    pygame.Rect(cx - int(w * 0.40), top_y,
                                int(w * 0.80), 10),
                    math.radians(190), math.radians(350), 2)

    # Calligraphic ink underline beneath the mid bank — sells the
    # horizon as ink-painted, not airbrushed.
    line_y = pad + int(h * 0.62)
    pygame.draw.line(s, (*edge, 140),
                     (cx - int(w * 0.42), line_y),
                     (cx + int(w * 0.42), line_y + 2), 1)
    pygame.draw.line(s, (*edge, 90),
                     (cx - int(w * 0.30), line_y + 3),
                     (cx + int(w * 0.30), line_y + 4), 1)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 4 — Cirrus Silk Streaks
# Research:
#   https://asiasociety.org/new-york/exhibitions/clouds-stretching-thousand-miles-ink-asian-art
#   https://www.asianbrushpainter.com/blogs/kb/brush-techniques-2
#
# Tang-poet phrase "clouds stretching a thousand miles" — the primary
# horizontal calligraphic stroke. Long thin tapered cirrus with a single
# loaded mid-belly + dry tapered tails on both sides. Near-horizontal,
# very thin, ideal for the upper sky band where wisps add motion without
# stealing focus from the V14 ridge.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_cirrus(surf, x, y, palette, scale=1.0):
    """Long thin silk streak — calligraphic "thousand-miles" stroke."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    length = int(120 * scale)
    thickness = max(4, int(8 * scale))
    pad = 8
    s = _alpha_surf(length + pad * 2, thickness * 4 + pad * 2)
    cy = s.get_height() // 2

    # The streak rises very gently then falls — captures the "flying"
    # arc of a flicked brush. Sample along a quadratic.
    n = 36
    pts = []
    for i in range(n):
        t = i / (n - 1)
        # Bell curve gives a fat belly + skinny tails.
        bell = math.sin(t * math.pi)
        x_px = pad + int(t * length)
        y_px = cy - int(math.sin(t * math.pi - 0.2) * 3 * scale)
        rad = max(1, int(thickness * 0.5 * bell + 0.5))
        a = int(_lerp(0, 230, bell ** 0.6))
        pts.append((x_px, y_px, rad, a))

    # First a low-alpha shadow trail offset 1-2 px down, gives the
    # streak weight without filling.
    for (px, py, rad, a) in pts:
        if a < 40:
            continue
        pygame.draw.circle(s, (*edge, max(0, a // 3)),
                           (px, py + 2), rad)

    # Main streak — fat in the middle, dry tails.
    for (px, py, rad, a) in pts:
        if a <= 0:
            continue
        pygame.draw.circle(s, (*body, a), (px, py), rad)

    # Lit crest along the top of the belly.
    belly_x = pad + length // 2
    belly_y = cy - 3
    pygame.draw.arc(s, (*lit, 200),
                    pygame.Rect(belly_x - 30, belly_y - 6, 60, 14),
                    math.radians(200), math.radians(340), 2)

    # Add a couple of breakaway specks beyond the front tail to
    # suggest the brush leaving the paper.
    rng_seed = (int(x) * 2654435761) ^ (int(y) * 40503)
    for k in range(5):
        offx = pad + length + 4 + (k * 7) + ((rng_seed >> k) & 0x3)
        offy = cy - 1 + ((rng_seed >> (k * 2)) & 0x3) - 1
        if offx >= s.get_width():
            break
        pygame.draw.circle(s, (*body, max(0, 90 - k * 18)),
                           (offx, offy), max(1, 2 - k // 3))

    surf.blit(s, (int(x - pad - length // 2),
                  int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 5 — Hokusai Curl-and-Claw
# Research:
#   https://store.kyotohandicraftcenter.com/products/as026
#   https://en.wikipedia.org/wiki/The_Great_Wave_off_Kanagawa
#
# Stylised stacked cumulus borrowing the Great-Wave curl: a heavy
# undercarriage of overlapping mounds with a single signature spiral
# "claw" curl peeling off the lit side. Outlined in a thin ink keyline
# in the same family as the Edo woodblock cloud / wave silhouette.
# Distinct from sumi-e because the keyline is HARD and decorative, and
# distinct from ruyi because the curl is asymmetric, not a heraldic
# 4-lobe scroll.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_hokusai(surf, x, y, palette, scale=1.0):
    """Edo-curl cumulus — stacked mounds + asymmetric spiral claw."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    w = int(90 * scale)
    h = int(54 * scale)
    pad = 8
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    base_y = pad + int(h * 0.72)

    # Layered mounds — fat anchor on the right, ascending and shrinking
    # to the left where the curl peels off.
    mounds = (
        # (cx_frac, cy_offset, rx, ry)
        (0.78, 0, int(w * 0.28), int(h * 0.42)),
        (0.55, -int(h * 0.10), int(w * 0.26), int(h * 0.40)),
        (0.34, -int(h * 0.18), int(w * 0.22), int(h * 0.34)),
        (0.18, -int(h * 0.10), int(w * 0.16), int(h * 0.26)),
    )

    # Cast shadow — a flat dark ribbon along the bottom that anchors
    # the cloud as if lit from above.
    shadow_pts = []
    for (cxf, _co, rx, _ry) in mounds:
        shadow_pts.append((pad + int(w * cxf) - rx + 4, base_y + 4))
        shadow_pts.append((pad + int(w * cxf) + rx + 4, base_y + 4))
    if shadow_pts:
        pygame.draw.polygon(
            s, (*edge, 50),
            [(px, base_y + 3) for (px, _py) in shadow_pts] +
            [(shadow_pts[-1][0], base_y + 8),
             (shadow_pts[0][0], base_y + 8)])

    # Mound fills.
    for (cxf, co, rx, ry) in mounds:
        cx_l = pad + int(w * cxf)
        cy_l = base_y + co
        pygame.draw.ellipse(
            s, (*body, 240),
            pygame.Rect(cx_l - rx, cy_l - ry, rx * 2, ry * 2))

    # Hard ink keyline along the top arcs only — Edo woodblock look.
    for (cxf, co, rx, ry) in mounds:
        cx_l = pad + int(w * cxf)
        cy_l = base_y + co
        pygame.draw.arc(
            s, (*edge, 200),
            pygame.Rect(cx_l - rx, cy_l - ry, rx * 2, ry * 2),
            math.radians(20), math.radians(160), 2)

    # The signature curl — a small spiral peeling left-up off the
    # leading lit mound. Drawn as two concentric arcs + a centre dot.
    curl_cx = pad + int(w * 0.10)
    curl_cy = base_y - int(h * 0.28)
    curl_r = int(min(w, h) * 0.16)
    pygame.draw.circle(s, (*body, 240), (curl_cx, curl_cy), curl_r)
    pygame.draw.circle(s, (*edge, 200), (curl_cx, curl_cy), curl_r, 2)
    pygame.draw.arc(
        s, (*edge, 220),
        pygame.Rect(curl_cx - curl_r + 3, curl_cy - curl_r + 3,
                    (curl_r - 3) * 2, (curl_r - 3) * 2),
        math.radians(40), math.radians(300), 2)
    pygame.draw.circle(s, (*edge, 220),
                       (curl_cx - 1, curl_cy + 1), 1)

    # Sweep connecting the curl back to the main mass — a single
    # tapered crescent that reads as the cloud reaching out a "claw".
    sweep_pts = [
        (curl_cx + curl_r - 1, curl_cy + 2),
        (pad + int(w * 0.22), base_y - int(h * 0.30)),
        (pad + int(w * 0.30), base_y - int(h * 0.20)),
        (pad + int(w * 0.24), base_y - int(h * 0.12)),
        (pad + int(w * 0.14), base_y - int(h * 0.18)),
    ]
    pygame.draw.polygon(s, (*body, 240), sweep_pts)
    pygame.draw.lines(s, (*edge, 180), False, sweep_pts[:3], 2)

    # A single lit crescent on the topmost mound.
    top_mound = mounds[2]
    cx_l = pad + int(w * top_mound[0])
    cy_l = base_y + top_mound[1]
    pygame.draw.arc(
        s, (*lit, 220),
        pygame.Rect(cx_l - top_mound[2] + 2, cy_l - top_mound[3] + 2,
                    (top_mound[2] - 2) * 2, (top_mound[3] - 2) * 2),
        math.radians(110), math.radians(220), 2)

    surf.blit(s, (int(x - pad - w // 2), int(y - pad - h // 2)))


# ── registries ───────────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_cloud_sumie,
    2: draw_cloud_ruyi,
    3: draw_cloud_yunhai,
    4: draw_cloud_cirrus,
    5: draw_cloud_hokusai,
}

VARIANT_NAMES = {
    1: "Sumi-e Ink-Wash Wisp",
    2: "Ruyi Auspicious Scroll",
    3: "Yunhai Cloud-Sea Bank",
    4: "Cirrus Silk Streaks",
    5: "Hokusai Curl-and-Claw",
}

VARIANT_SOURCES = {
    1: "asianbrushpainter.com/blogs/kb/the-use-of-ink",
    2: "en.wikipedia.org/wiki/Xiangyun_(Auspicious_clouds)",
    3: "1000museums.com Yoshida 'Sea of Clouds (Unkai)'",
    4: "asiasociety.org 'Clouds Stretching for a Thousand Miles'",
    5: "en.wikipedia.org/wiki/The_Great_Wave_off_Kanagawa",
}
