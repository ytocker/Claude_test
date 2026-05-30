"""Round-24 Ruyi-cloud explorations: 8 directions off the round-23 V2.

The round-23 Ruyi (祥云) variant landed SHIP-READY but read too packed in
field — three lobes + base ribbon + arc keylines compress a lot of ink
into a 72-px silhouette. These 8 candidates each pull on ONE knob of
that base: aspect ratio, lobe count, edge treatment, interior structure,
or palette consumption — to find a sparser / more atmospheric Ruyi that
still reads as auspicious-cloud at thumbnail scale.

Drop-in contract is identical to `cloud_variants.draw_cloud_*`:
    `draw_ruyi_<name>(surf, x, y, palette, scale=1.0)`

Shared edge/body tinting is imported from `cloud_variants` — there's
exactly one definitive night-cool branch in the project and it lives
there. Do NOT re-implement those helpers here.
"""
from __future__ import annotations

import math
import pygame

from cloud_variants import (
    _cloud_body_color,
    _ink_shadow_color,
    _lit_edge_color,
)


# ── shared helpers ──────────────────────────────────────────────────────────

def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _lerp_color(a, b, t):
    return (
        int(_lerp(a[0], b[0], t)),
        int(_lerp(a[1], b[1], t)),
        int(_lerp(a[2], b[2], t)),
    )


def _alpha_surf(w: int, h: int) -> pygame.Surface:
    return pygame.Surface((max(2, int(w)), max(2, int(h))), pygame.SRCALPHA)


def _seeded_jit(x: float, y: float, idx: int, amp: int) -> int:
    # Deterministic per-spawn LCG step so silhouette jitter doesn't
    # reshuffle frame-to-frame. Matches the seeding pattern used by the
    # round-23 baseline so jitter "feels" the same across variants.
    seed = (int(x) * 0x9E3779B1) ^ (int(y) * 0x7F4A7C15)
    v = ((seed + idx * 2654435761) & 0xFFFF) / 0xFFFF
    return int((v - 0.5) * 2 * amp)


def _is_night(palette: dict) -> bool:
    # Single luminance test used to gate night-only branches like the
    # ghost-white halos on the Sovereign and Sumi-e variants. Threshold
    # matches `_cloud_body_color`'s 90 split point so the cloud cools
    # in sync with its night-branch body.
    top = palette['sky_top']
    return (top[0] * 299 + top[1] * 587 + top[2] * 114) / 1000 < 90


def _ruyi_lobe(s: pygame.Surface, cx: int, cy: int, r: int,
               body, edge, lit,
               body_a: int = 245, key_a: int = 160,
               lit_arc: bool = False) -> None:
    # One canonical ruyi lobe: filled circle + lower-left calligraphic
    # arc keyline (200°–340°) + inner-curl arc (20°–200°). Pulled out
    # of the round-23 inline code so all 8 variants paint the same lobe
    # vocabulary, only varying count / spacing / palette.
    pygame.draw.circle(s, (*body, body_a), (cx, cy), r)
    pygame.draw.arc(
        s, (*edge, key_a),
        pygame.Rect(cx - r, cy - r, r * 2, r * 2),
        math.radians(200), math.radians(340), 2)
    inner = max(3, r - 5)
    pygame.draw.arc(
        s, (*edge, min(255, key_a + 20)),
        pygame.Rect(cx - inner, cy - inner, inner * 2, inner * 2),
        math.radians(20), math.radians(200), 2)
    if lit_arc and r >= 6:
        pygame.draw.arc(
            s, (*lit, 200),
            pygame.Rect(cx - r + 2, cy - r + 2,
                        max(2, r * 2 - 4), max(2, r * 2 - 4)),
            math.radians(110), math.radians(220), 2)


def _ruyi_heart(s: pygame.Surface, cx: int, cy: int, r: int,
                body, edge, lit,
                body_a: int = 245, key_a: int = 170,
                lit_arc: bool = False) -> None:
    # Two mirrored half-lobes joined at the base — this is the silhouette
    # signature that says "Ruyi" rather than "circle". Cluster of: left
    # lobe + right lobe centred horizontally on cx, vertically tucked so
    # their bottoms meet just under cy, with a downward V-notch between
    # them. The notch is what reads as a heart, not a peanut, at thumb-
    # nail. Used wherever the AD called for "double-lobed heart DNA".
    off = max(2, int(r * 0.55))
    lr = max(3, int(r * 0.78))
    lcx_l = cx - off
    lcx_r = cx + off
    lcy = cy - max(1, int(r * 0.10))
    # Drop-shadow first (under both halves) so it doesn't double-bake
    # in the join seam.
    pygame.draw.circle(s, (*edge, 30), (cx + 1, cy + 3), r)
    # Twin half-lobes — drawn as full discs then welded by a small
    # bridging ellipse at the base so the silhouette reads as one
    # continuous heart rather than two stamped balls.
    pygame.draw.circle(s, (*body, body_a), (lcx_l, lcy), lr)
    pygame.draw.circle(s, (*body, body_a), (lcx_r, lcy), lr)
    bridge_w = off * 2 + 2
    bridge_h = max(3, int(r * 0.55))
    pygame.draw.ellipse(
        s, (*body, body_a),
        pygame.Rect(cx - bridge_w // 2, lcy, bridge_w, bridge_h))
    # V-notch on top centre — small triangle in transparent so the heart
    # cleavage is visible. Achieved by repainting the body's interior
    # gap with the surface's clear-pixel through BLEND_RGBA_MULT mask
    # would be heavier; here a single 1-px tip indent is enough at the
    # scales we render.
    notch_top = (cx, lcy - lr + 2)
    notch_l = (cx - max(1, lr // 4), lcy - lr // 2)
    notch_r = (cx + max(1, lr // 4), lcy - lr // 2)
    pygame.draw.polygon(s, (0, 0, 0, 0), [notch_top, notch_l, notch_r])
    # Calligraphic keyline arcs hugging each half-lobe's outer flank —
    # mirrored so the heart has two flanking curls, the classic Ruyi
    # double-spiral signature.
    pygame.draw.arc(
        s, (*edge, key_a),
        pygame.Rect(lcx_l - lr, lcy - lr, lr * 2, lr * 2),
        math.radians(200), math.radians(350), 2)
    pygame.draw.arc(
        s, (*edge, key_a),
        pygame.Rect(lcx_r - lr, lcy - lr, lr * 2, lr * 2),
        math.radians(190), math.radians(340), 2)
    inner = max(2, lr - 4)
    pygame.draw.arc(
        s, (*edge, min(255, key_a + 20)),
        pygame.Rect(lcx_l - inner, lcy - inner, inner * 2, inner * 2),
        math.radians(40), math.radians(200), 2)
    pygame.draw.arc(
        s, (*edge, min(255, key_a + 20)),
        pygame.Rect(lcx_r - inner, lcy - inner, inner * 2, inner * 2),
        math.radians(340), math.radians(140), 2)
    if lit_arc and lr >= 5:
        pygame.draw.arc(
            s, (*lit, 200),
            pygame.Rect(lcx_l - lr + 2, lcy - lr + 2,
                        max(2, lr * 2 - 4), max(2, lr * 2 - 4)),
            math.radians(120), math.radians(220), 2)
        pygame.draw.arc(
            s, (*lit, 200),
            pygame.Rect(lcx_r - lr + 2, lcy - lr + 2,
                        max(2, lr * 2 - 4), max(2, lr * 2 - 4)),
            math.radians(110), math.radians(210), 2)


def _wisp_dab(s: pygame.Surface, cx: int, cy: int, r: int,
              body, edge, seed: int, n: int = 3) -> None:
    # Ink-wash dry-brush dab — 3-4 small alpha-faded blobs in a short
    # diagonal stagger. Used to replace solid mini-lobes with flying-
    # white wisps so a constellation reads as "1 Ruyi + 2 wisps" rather
    # than "3 same-size circles". Borrowed from the Sumi-e variant's
    # kasure technique so the visual vocabulary stays in-key.
    for k in range(n):
        ox = ((seed >> (k * 3)) & 0x7) - 3
        oy = ((seed >> (k * 3 + 1)) & 0x3) - 1
        rr = max(1, int(r * (1.0 - k * 0.25)))
        a = max(60, 200 - k * 50)
        pygame.draw.circle(s, (*body, a), (cx + ox + k * 2, cy + oy), rr)
        if k == 0:
            pygame.draw.circle(s, (*edge, 110),
                               (cx + ox + k * 2, cy + oy), rr, 1)


def _ribbon_polygon(cx: int, cy: int, w: int, h: int) -> list[tuple[int, int]]:
    # Symmetric S-tapered ribbon outline — used as a trailing streamer
    # behind a head lobe. Cubic-ish poly approximated via 9 control
    # points so the silhouette has visible widening + tapering instead
    # of a flat strip.
    half_w = w // 2
    return [
        (cx - half_w,           cy + h // 6),
        (cx - half_w + w // 6,  cy - h // 4),
        (cx - w // 5,           cy - h // 3),
        (cx + w // 5,           cy + h // 4),
        (cx + half_w,           cy + h // 6),
        (cx + half_w - w // 8,  cy + h // 3),
        (cx + w // 6,           cy + h // 2),
        (cx - w // 4,           cy + h // 3),
        (cx - half_w + w // 8,  cy + h // 3),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Variant 1 — Trailing Ribbon Streamer
# Research:
#   https://news.lenovo.com/pressroom/press-releases/lenovo-designed-olympic-torch-for-beijing-2008-olympic-games-unveiled/
#   https://www.yankodesign.com/2007/04/27/cloud-of-promise-2008-olympic-torch-by-lenovo/
#
# Beijing 2008 "Cloud of Promise" torch motif: one Ruyi lobe HEAD pulling
# a long horizontal silk-ribbon trail behind it. Direct sparser answer to
# "too packed" — most of the silhouette is empty trailing ribbon, the
# auspicious meaning lives in the single head lobe.
# ─────────────────────────────────────────────────────────────────────────────

def draw_ruyi_streamer(surf, x, y, palette, scale=1.0):
    """Heart-headed Ruyi pulling a silk ribbon trail — Olympics 2008 motif."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    # Total length 92 px. AD round 2: anchor head at LEADING edge and
    # flip the ribbon to trail RIGHT so the silhouette reads as motion-
    # into-frame (head punches, ribbon drags). Head radius is the
    # round-23 dominant-lobe radius (~16 px) so the heart reads as a
    # full Ruyi at thumbnail scale, not a punctuation mark.
    length = int(92 * scale)
    head_r = int(15 * scale)
    pad = head_r + 6
    s = _alpha_surf(length + pad * 2, head_r * 3 + 10)
    cx = pad + head_r + 4
    cy = s.get_height() // 2

    # Ribbon trail — taper from full head-height at the join down to
    # zero on the right tip. Drawn as a series of progressively thinner
    # horizontal ellipses with a gentle vertical sine so the ribbon
    # arcs subtly instead of flat-strip slicing the sky.
    n_ribbon = 12
    ribbon_start = cx + head_r
    ribbon_end = pad + length
    for i in range(n_ribbon):
        # t goes 1→0 from head to tail so thickness fades AWAY from the
        # head (head-side has mass, tail-tip wisps off).
        t = 1.0 - (i / (n_ribbon - 1))
        rx = ribbon_start + int((1 - t) * (ribbon_end - ribbon_start))
        # Sine swoop matches the Olympics torch's flowing band.
        ry = cy + int(math.sin((1 - t) * math.pi * 0.8 + 0.4) * 4 * scale)
        # Thickness ramped 0.85 → 1.05 per AD round-2: ribbon was too
        # thin to read against sky_top.
        thick = max(1, int(head_r * 1.05 * t))
        # Alpha bumped 70→110 min, 215→245 max — invisible past head at
        # SUNSET/DUSK in round 1.
        a = int(_lerp(110, 245, t))
        pygame.draw.ellipse(
            s, (*body, a),
            pygame.Rect(rx - thick, ry - thick // 2,
                        thick * 2, max(2, thick)))

    # Ink-shadow underline beneath the ribbon — single long thin
    # ellipse, no full-circumference keyline, so the trail reads as
    # silk in motion rather than a solid heraldic band. Gated off at
    # night per AD cross-cutting A (drop-shadow smudge halo on deep
    # blue): streamer's underline carries the silk read at day/golden
    # so we keep it on those phases.
    if not _is_night(palette):
        pygame.draw.ellipse(
            s, (*edge, 55),
            pygame.Rect(ribbon_start, cy + head_r // 3,
                        ribbon_end - ribbon_start, max(2, int(head_r * 0.5))))

    # Heart-shape head — two mirrored half-lobes joined at base. This
    # is what the AD round-1 critique demanded: replaces the single
    # `_ruyi_lobe` head that read as a comet.
    _ruyi_heart(s, cx, cy, head_r, body, edge, lit,
                body_a=245, key_a=180, lit_arc=True)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 2 — Single Sovereign Lobe
# Research:
#   https://en.wikipedia.org/wiki/Ruyi_(scepter)
#   https://www.pagodared.com/blog/2024/10/11/as-you-wish-the-ruyi-symbol-in-chinese-japanse-decorative-arts/
#
# Minimalist sacred-symbol read: ONE large lobe, sized just under the
# round-23 dominant lobe but standing alone with no companions. The
# ghost-white night halo + gold-rim sunset moves the sovereign lobe
# toward an icon — auspicious-cloud as a single calligraphic dot.
# ─────────────────────────────────────────────────────────────────────────────

def draw_ruyi_sovereign(surf, x, y, palette, scale=1.0):
    """Single 35-px sovereign Ruyi lobe — minimalist icon-grade silhouette."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    r = int(18 * scale)
    pad = r + 8
    s = _alpha_surf(r * 2 + pad * 2, r * 2 + pad * 2)
    cx = pad + r
    cy = pad + r

    # Outer aura — pulled wider at night so the sovereign lobe reads as
    # a moon-lit auspicious sigil. Day-phase aura is thin and warm so
    # the icon doesn't bloom too softly against bright sky.
    if _is_night(palette):
        for ring in range(3):
            ar = r + 3 + ring * 2
            pygame.draw.circle(s, (*lit, 30 - ring * 8), (cx, cy), ar)
    else:
        pygame.draw.circle(s, (*edge, 45), (cx + 1, cy + 2), r + 1)

    # Canonical lobe with stronger keyline alpha — the sovereign read
    # wants a confident inked silhouette.
    _ruyi_lobe(s, cx, cy, r, body, edge, lit,
               body_a=248, key_a=190, lit_arc=True)

    # Inner ruyi tail-mark — single short downward S that mimics the
    # ruyi scepter's handle-attachment glyph, planted just below the
    # lobe centre. This is what makes the sovereign read as "ruyi
    # symbol" rather than "round pebble".
    tail_top = (cx, cy + int(r * 0.30))
    tail_mid = (cx + int(r * 0.35), cy + int(r * 0.65))
    tail_bot = (cx - int(r * 0.10), cy + int(r * 0.95))
    pygame.draw.lines(s, (*edge, 200), False,
                      [tail_top, tail_mid, tail_bot], 2)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 3 — Loose Trinity Cluster
# Research:
#   https://www.chinese-showcase.com/blogs/chinese-symbols/auspicious-clouds-pattern-xiangyun-meaning-symbolism-spiritual-significance
#   https://www.dunhuang.ds.lib.uw.edu/mogao-cave-321-early-tang-dynasty/
#
# Three Ruyi lobes drifting as separate bodies in a loose constellation
# — explicitly NOT joined into one silhouette. Mogao Cave 321's Tang
# Buddhas riding on "auspicious clouds" shows discrete cloud forms
# floating apart; this candidate breaks the round-23 connected stack
# into three independent shapes that the eye groups as a phrase.
# ─────────────────────────────────────────────────────────────────────────────

def draw_ruyi_trinity(surf, x, y, palette, scale=1.0):
    """Three discrete Ruyi lobes in loose constellation — no base ribbon."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    # Wider footprint than round-23 (90 vs 72) but emptier interior —
    # the three lobes float on their own, so most of the surf is sky.
    w = int(90 * scale)
    h = int(48 * scale)
    pad = 8
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # Three lobes in non-aligned layout — leader on right is the
    # dominant one, two trailing companions break the strict diagonal
    # to read as drifting independently.
    lobes = (
        (pad + int(w * 0.15), pad + int(h * 0.62), int(h * 0.26)),
        (pad + int(w * 0.45), pad + int(h * 0.28), int(h * 0.30)),
        (pad + int(w * 0.82), pad + int(h * 0.55), int(h * 0.36)),
    )
    # Per-lobe y jitter so the constellation looks hand-placed.
    lobes = tuple(
        (lx, ly + _seeded_jit(x, y, i, int(h * 0.05)), lr)
        for i, (lx, ly, lr) in enumerate(lobes)
    )

    # No connecting ribbon, no shared base — each lobe carries its own
    # drop-shadow whisper and the dominant lobe gets the sun-kiss.
    for i, (lx, ly, lr) in enumerate(lobes):
        pygame.draw.circle(s, (*edge, 38), (lx + 1, ly + 2), lr + 1)
        _ruyi_lobe(s, lx, ly, lr, body, edge, lit,
                   body_a=242, key_a=155, lit_arc=(i == 2))

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 4 — Sumi-e Ink Brush Ruyi
# Research:
#   https://www.asianbrushpainter.com/blogs/kb/the-use-of-ink
#   https://www.shimizuart.org/post/sumi-e-the-art-of-ink-wash-painting
#
# Pure ink-wash Ruyi: NO outline keyline, NO closed arc. The lobes are
# soft alpha-gradient blobs and the ruyi-coil suggestion comes from a
# single calligraphic dry-brush flying-white (kasure) line draped over
# the top. Most atmospheric of the eight — barely-there Ruyi.
# ─────────────────────────────────────────────────────────────────────────────

def draw_ruyi_sumie(surf, x, y, palette, scale=1.0):
    """Wet-ink Ruyi blobs with one flying-white coil — no closed outline."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    w = int(80 * scale)
    h = int(40 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # 3 soft wet-ink blobs, each painted as stacked alpha discs so the
    # edge dissolves into the sky instead of stopping at a hard
    # circumference. No keyline — sumi-e Ruyi is read purely from
    # silhouette mass and the dry-brush gesture on top.
    blob_centres = (
        (pad + int(w * 0.28), cy + 2, int(h * 0.30)),
        (pad + int(w * 0.55), cy - 5, int(h * 0.34)),
        (pad + int(w * 0.80), cy + 1, int(h * 0.30)),
    )
    for (bx, by, br) in blob_centres:
        for ring in range(4):
            rr = br + ring * 2
            a = max(0, 200 - ring * 55)
            pygame.draw.circle(s, (*body, a), (bx, by), rr)

    # Flying-white coil drape — short broken segments tracing a flat
    # ruyi-curl. Each segment is a stubby ellipse with alpha randomly
    # punched out to suggest dry-brush bristle gaps. Matches the
    # kasure technique from the research source above.
    coil_pts = []
    for k in range(20):
        t = k / 19
        # Coil arcs over the central blob then dips into the right
        # blob — the Ruyi "S" gesture distilled to a single stroke.
        coil_x = pad + int(w * (0.18 + 0.65 * t))
        coil_y = cy - int(h * 0.18) + int(math.sin(t * math.pi * 1.2) * h * 0.16)
        coil_pts.append((coil_x, coil_y))
    for k, (px, py) in enumerate(coil_pts):
        seed = (int(x) ^ (int(y) << 1) ^ (k * 7919)) & 0xFF
        # Skip ~30% of dabs entirely so the line breaks irregularly —
        # this is what makes it read as flying-white, not a dotted ruler.
        if seed > 180:
            continue
        rr = max(1, int(scale * (1.5 + (seed & 3) * 0.4)))
        a = int(_lerp(110, 220, k / 19))
        pygame.draw.circle(s, (*edge, a), (px, py), rr)

    # One soft warm rim where the central blob meets the dry-brush
    # coil — picks up sunset/golden light without re-introducing a
    # closed keyline.
    bx, by, br = blob_centres[1]
    pygame.draw.arc(
        s, (*lit, 180),
        pygame.Rect(bx - br + 2, by - br - 1,
                    max(4, br * 2 - 4), max(4, br + 4)),
        math.radians(200), math.radians(340), 2)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 5 — Goryeo Celadon Jade
# Research:
#   https://smarthistory.org/maebyeong-with-cloud-and-crane-design/
#   https://www.goryeobeauty.com/blogs/korean-culture/goryeo-celadon
#
# Korean Goryeo-dynasty inlaid-celadon cloud motif. Body palette pulls
# toward `foliage_top` and `stone_light` to land on the famous jade
# (bisaek) green. Edge is cracked-glaze (bingyeol craquelure) — short
# orthogonal line fragments tracing the lobe perimeter instead of a
# continuous arc. Inner lines are sanggam-style inlay flourishes.
# ─────────────────────────────────────────────────────────────────────────────

def draw_ruyi_celadon(surf, x, y, palette, scale=1.0):
    """Goryeo jade-cloud Ruyi with cracked-glaze edges and inlay flourishes."""
    body_base = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    # Pull the body toward foliage_top + stone_light so the cloud lands
    # on celadon jade-green. At night the jade naturally cools off
    # because `_cloud_body_color` already shifts the base toward
    # sky_top, so we just blend on top of that.
    fol = palette.get('foliage_top', body_base)
    stl = palette.get('stone_light', body_base)
    jade = (
        int(body_base[0] * 0.30 + fol[0] * 0.25 + stl[0] * 0.45),
        int(body_base[1] * 0.30 + fol[1] * 0.40 + stl[1] * 0.30),
        int(body_base[2] * 0.30 + fol[2] * 0.25 + stl[2] * 0.45),
    )
    # Darker jade for the cracked-glaze line fragments — pulled from
    # `foliage_dark` so the craquelure is in-key with the body.
    fol_dark = palette.get('foliage_dark', edge)
    crack = (
        max(0, int(fol_dark[0] * 0.55 + edge[0] * 0.45) - 5),
        max(0, int(fol_dark[1] * 0.55 + edge[1] * 0.45) - 5),
        max(0, int(fol_dark[2] * 0.55 + edge[2] * 0.45) - 5),
    )

    w = int(76 * scale)
    h = int(44 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # Two-lobe Ruyi — sparser than round-23's three — so the inlay
    # flourishes have room to be legible. The dominant lobe is on the
    # right, smaller companion left.
    lobes = (
        (pad + int(w * 0.32), cy + 1, int(h * 0.32)),
        (pad + int(w * 0.68), cy - 4, int(h * 0.40)),
    )

    # Lobe bodies in jade — no canonical keylines (those would compete
    # with the craquelure). Just the filled shape + drop-shadow whisper.
    for (lx, ly, lr) in lobes:
        pygame.draw.circle(s, (*edge, 40), (lx + 1, ly + 2), lr + 1)
        pygame.draw.circle(s, (*jade, 240), (lx, ly), lr)

    # Cracked-glaze (bingyeol) edge — short orthogonal line fragments
    # along each lobe's perimeter. The crack lines DON'T follow the
    # circle outline; they radiate outward like crackle in a true
    # celadon glaze, then stop. Determined seed so the cracks read as
    # crack-pattern, not random noise.
    for li, (lx, ly, lr) in enumerate(lobes):
        for k in range(7):
            ang = (k / 7) * math.tau + li * 0.4
            # Each crack starts on the perimeter and runs ~3-5 px
            # outward, with a small lateral kink so it reads as
            # branching craquelure, not radial spokes.
            x0 = lx + int(math.cos(ang) * (lr - 1))
            y0 = ly + int(math.sin(ang) * (lr - 1))
            seg_len = 3 + ((k * 17 + li * 11) & 3)
            x1 = lx + int(math.cos(ang) * (lr + seg_len))
            y1 = ly + int(math.sin(ang) * (lr + seg_len))
            pygame.draw.line(s, (*crack, 140), (x0, y0), (x1, y1), 1)
            # 50% of cracks get a small kink branch — that's the
            # signature look of bingyeol craquelure.
            if k & 1:
                kink_x = x1 + int(math.cos(ang + 1.4) * 2)
                kink_y = y1 + int(math.sin(ang + 1.4) * 2)
                pygame.draw.line(s, (*crack, 110), (x1, y1),
                                 (kink_x, kink_y), 1)

    # Sanggam inlay flourish — single white inlay-line ruyi-curl over
    # the dominant lobe, painted in stone_light (the "white slip" of
    # Goryeo inlay).
    lx, ly, lr = lobes[1]
    inlay_r = max(3, lr - 6)
    pygame.draw.arc(
        s, (*stl, 220),
        pygame.Rect(lx - inlay_r, ly - inlay_r, inlay_r * 2, inlay_r * 2),
        math.radians(30), math.radians(210), 2)

    # Single warm sun-kiss on the dominant lobe — sells the curved
    # glaze surface as a 3D vessel form.
    pygame.draw.arc(
        s, (*lit, 200),
        pygame.Rect(lx - lr + 2, ly - lr + 2,
                    max(2, lr * 2 - 4), max(2, lr * 2 - 4)),
        math.radians(110), math.radians(220), 2)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 6 — Dragon-Coil Long-Form
# Research:
#   https://asia.si.edu/explore-art-culture/collections/search/edanmdm:fsg_S1991.142/
#   https://www.suembroidery.com/chinese-silk-embroidery-blog/chinese-silk-embroidery-patterns-and-symbolisms
#
# Chinese imperial dragon-cloud robe motif: elongated horizontal Ruyi-
# bodied silhouette suggesting a dragon's body coiling through the sky.
# 120 × 18 px aspect — by far the longest of the eight, and the
# strongest sparseness answer to "too packed" because the mass spreads
# horizontally across 3× the round-23 footprint.
# ─────────────────────────────────────────────────────────────────────────────

def draw_ruyi_dragon(surf, x, y, palette, scale=1.0):
    """Long horizontal Ruyi-spine dragon-cloud — 120 × 18 px aspect."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    length = int(120 * scale)
    h = int(20 * scale)
    pad = 8
    s = _alpha_surf(length + pad * 2, h * 3 + pad * 2)
    cx = pad + length // 2
    cy = s.get_height() // 2

    # Spine — soft horizontal body painted as stacked low-alpha
    # ellipses with a gentle sinusoidal undulation, mimicking a dragon's
    # coil from imperial robe motifs. The spine is what carries the
    # "elongated Ruyi" read; the lobes punctuate.
    spine_n = 14
    for i in range(spine_n):
        t = i / (spine_n - 1)
        sx = pad + int(t * length)
        # Two-period sine so the coil reads as a true dragon undulation,
        # not a single arc.
        sy = cy + int(math.sin(t * math.pi * 2.2) * h * 0.45)
        sw = max(4, int(h * 1.4 * (1 - abs(t - 0.5))))
        sh = max(2, h - 2)
        a = int(_lerp(160, 220, 1 - abs(t - 0.5) * 2))
        pygame.draw.ellipse(
            s, (*body, a),
            pygame.Rect(sx - sw // 2, sy - sh // 2, sw, sh))

    # Three Ruyi-lobe punctuation points along the spine: head (right),
    # mid-coil, and tail-tip (left). The head is the largest, tail
    # smallest, so the eye reads the cloud as flowing right-to-left
    # like a dragon's body.
    spine_pts = (
        (pad + int(length * 0.10), cy + int(math.sin(0.10 * math.pi * 2.2) * h * 0.45), int(h * 0.45)),
        (pad + int(length * 0.50), cy + int(math.sin(0.50 * math.pi * 2.2) * h * 0.45), int(h * 0.55)),
        (pad + int(length * 0.88), cy + int(math.sin(0.88 * math.pi * 2.2) * h * 0.45), int(h * 0.75)),
    )
    for i, (lx, ly, lr) in enumerate(spine_pts):
        _ruyi_lobe(s, lx, ly, lr, body, edge, lit,
                   body_a=240, key_a=150, lit_arc=(i == 2))

    # Ink-shadow undertow — single very thin long ellipse beneath the
    # spine, alpha softened so it reads as the body's depth shadow.
    pygame.draw.ellipse(
        s, (*edge, 50),
        pygame.Rect(pad + 4, cy + h // 2, length - 8, max(2, h // 3)))

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 7 — Tang Mandala Crest (denser contrast option)
# Research:
#   https://www.dunhuang.ds.lib.uw.edu/mogao-cave-321-early-tang-dynasty/
#   https://www.dunhuang.ds.lib.uw.edu/mogao-cave-420-sui-dynasty/
#
# Dunhuang Tang-dynasty caisson-ceiling cloud canopy: dense radial
# mandala of 5–7 lobes in concentric tiers, often painted as the
# "rotating canopy-like caisson" mentioned in Mogao Cave 420. This is
# the intentional denser-direction control: lets the user see that
# packing MORE into a Ruyi silhouette pushes it further into
# decorative-decal territory, validating the sparser candidates.
# ─────────────────────────────────────────────────────────────────────────────

def draw_ruyi_mandala(surf, x, y, palette, scale=1.0):
    """Radial 6-lobe Tang caisson cloud — the denser contrast direction."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    w = int(78 * scale)
    h = int(56 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # Inner tier — 1 large central lobe.
    centre_r = int(h * 0.22)
    pygame.draw.circle(s, (*edge, 50), (cx + 1, cy + 2), centre_r + 1)

    # Outer tier — 6 satellite lobes in a hexagonal mandala arrangement.
    # The radial layout is what gives the variant its Tang caisson read;
    # exactly six lobes matches the most common Mogao panel.
    outer_r = int(h * 0.16)
    ring_radius = int(h * 0.36)
    for k in range(6):
        ang = (k / 6) * math.tau - math.pi / 2
        ox = cx + int(math.cos(ang) * ring_radius)
        oy = cy + int(math.sin(ang) * ring_radius * 0.78)
        pygame.draw.circle(s, (*edge, 38), (ox + 1, oy + 2), outer_r + 1)
        _ruyi_lobe(s, ox, oy, outer_r, body, edge, lit,
                   body_a=235, key_a=145, lit_arc=False)

    # Centre lobe drawn LAST so it sits on top of the satellite-lobe
    # arc keylines that would otherwise overlap into the middle.
    _ruyi_lobe(s, cx, cy, centre_r, body, edge, lit,
               body_a=250, key_a=180, lit_arc=True)

    # Connecting ring keyline — single thin elliptical arc tying the
    # mandala together, painted at low alpha so it whispers rather than
    # rules the silhouette into a flat badge.
    pygame.draw.ellipse(
        s, (*edge, 90),
        pygame.Rect(cx - ring_radius - 4, cy - int(ring_radius * 0.78) - 3,
                    (ring_radius + 4) * 2, int(ring_radius * 0.78 * 2) + 6),
        1)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 8 — Art-Deco Banded Cloud
# Research:
#   https://awedeco.com/chevron-patterns-in-art-deco/
#   https://en.wikipedia.org/wiki/Chrysler_Building
#
# Modern Art-Deco reinterpretation of the Ruyi: concentric outline bands
# (echoing Chrysler-Building chevron spandrels) wrap the silhouette,
# with a horizontally-banded warm/cool gradient interior recalling the
# Beijing 2008 Olympics emblem's modernized cloud heritage. Graphic and
# bold, but still calligraphic at silhouette level.
# ─────────────────────────────────────────────────────────────────────────────

def draw_ruyi_deco(surf, x, y, palette, scale=1.0):
    """Art-Deco Ruyi — concentric outline rings + horizontally banded fill."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    w = int(70 * scale)
    h = int(40 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # Two-lobe sparser Ruyi: dominant centre + small left companion.
    lobes = (
        (pad + int(w * 0.32), cy + 1, int(h * 0.28)),
        (pad + int(w * 0.62), cy - 3, int(h * 0.40)),
    )

    # Horizontally banded interior fill — 4 stripes per lobe, warm top
    # → cool bottom. Painted onto an inner mask circle so the bands
    # are visually clipped to the lobe silhouette without per-pixel
    # masking work.
    band_top = _lerp_color(body, lit, 0.40)
    band_bot = _lerp_color(body, edge, 0.30)
    for (lx, ly, lr) in lobes:
        # Backing solid so the band stripes don't show sky underneath.
        pygame.draw.circle(s, (*body, 240), (lx, ly), lr)
        # 5 horizontal band rects clipped to a circular scratch surface,
        # then blitted in. The clip is what gives the Art-Deco lozenge
        # silhouette + chevron-stripe interior.
        scratch = _alpha_surf(lr * 2 + 2, lr * 2 + 2)
        n_bands = 5
        for bi in range(n_bands):
            t = bi / (n_bands - 1)
            colb = _lerp_color(band_top, band_bot, t)
            by0 = int(t * (lr * 2))
            by1 = int((t + 1.0 / (n_bands - 1)) * (lr * 2))
            pygame.draw.rect(
                scratch, (*colb, 230),
                pygame.Rect(0, by0, lr * 2 + 2, max(1, by1 - by0)))
        # Circular clip — repaint the scratch onto a circle by drawing
        # the band stack onto a per-lobe alpha surf that only carries
        # the lobe's silhouette.
        mask = _alpha_surf(lr * 2 + 2, lr * 2 + 2)
        pygame.draw.circle(mask, (255, 255, 255, 255),
                           (lr + 1, lr + 1), lr)
        scratch.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        s.blit(scratch, (lx - lr - 1, ly - lr - 1))

    # Concentric outline rings — 2 rings per lobe, the inner ring is
    # bolder (the Art-Deco "primary edge") and the outer is a soft
    # echo at half alpha. Chrysler-style chevron read at thumbnail.
    for (lx, ly, lr) in lobes:
        pygame.draw.circle(s, (*edge, 220), (lx, ly), lr, 2)
        pygame.draw.circle(s, (*edge, 110), (lx, ly), lr + 2, 1)

    # Single sun-kiss highlight on the dominant lobe so the deco
    # banding doesn't go flat-graphic.
    lx, ly, lr = lobes[1]
    pygame.draw.arc(
        s, (*lit, 220),
        pygame.Rect(lx - lr + 3, ly - lr + 3,
                    max(2, lr * 2 - 6), max(2, lr * 2 - 6)),
        math.radians(110), math.radians(220), 2)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ── registries ───────────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_ruyi_streamer,
    2: draw_ruyi_sovereign,
    3: draw_ruyi_trinity,
    4: draw_ruyi_sumie,
    5: draw_ruyi_celadon,
    6: draw_ruyi_dragon,
    7: draw_ruyi_mandala,
    8: draw_ruyi_deco,
}

VARIANT_NAMES = {
    1: "Trailing Ribbon Streamer",
    2: "Single Sovereign Lobe",
    3: "Loose Trinity Cluster",
    4: "Sumi-e Ink Brush Ruyi",
    5: "Goryeo Celadon Jade",
    6: "Dragon-Coil Long-Form",
    7: "Tang Mandala Crest",
    8: "Art-Deco Banded Cloud",
}

VARIANT_SOURCES = {
    1: "yankodesign.com 2008 Olympic 'Cloud of Promise' torch",
    2: "wikipedia.org/wiki/Ruyi_(scepter) + pagodared.com ruyi/lingzhi",
    3: "dunhuang.ds.lib.uw.edu Mogao Cave 321 Early Tang clouds",
    4: "asianbrushpainter.com flying-white kasure ink technique",
    5: "smarthistory.org Goryeo maebyeong cloud-and-crane inlay",
    6: "asia.si.edu palace hanging embroidered dragon-and-lotus",
    7: "dunhuang.ds.lib.uw.edu Mogao Cave 420 rotating caisson canopy",
    8: "awedeco.com chevron patterns + Chrysler Building heritage",
}
