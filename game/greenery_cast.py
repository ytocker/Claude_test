"""Promenade PLANTS & GREENERY — a varied potted-plant / tree pool.

Replaces the single shrub-planter / conifer-planter / wish-tree with a 10-design
pool built as VESSEL × SPECIES over one shared draw_greenery (data rows = palette
+ vessel/species/attrs flags). Art-director SHIP-READY
(docs/sidewalk_overhaul/greenery/round_3.png), sibling to the ped_cast / day_cast
/ food_stalls / animals families.

Variety lives in the OUTLINE (vessel shape + canopy shape): terracotta / glazed
urn / wooden tub / bamboo planter / stone trough × shrub, conifer-cone, clipped
topiary (1 or 3 tier), flowering dome, cascading flowering-vine, bamboo canes,
draping vine/fern, kumquat fruiting-tree, weeping wish-tree. Blossom/fruit/ribbon
accents are muted and held well under the gold coin; night-cooled toward
(54,64,96) ≤150 luma (measured hottest greenery 138.5 vs coin 229.5). Greenery is
beat- and weather-neutral (it persists across the day-arc). Pure-Pygame /
pygbag-safe.
"""
from __future__ import annotations

import math

import pygame

from game.foreground_props import _mix, _shade, _clamp
from game import foreground_variants as fv

NIGHT_GLOW_CAP = 150
VESSEL_H = 14      # height of a 1.0 terracotta pot (px) — shorter than an adult


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _retint(col, night):
    """Cool toward the night ground band (matches ped_cast._retint_person), with a
    stronger pull on anything still above the cap so no leaf/pot/blossom out-glows
    the coin at night."""
    if night <= 0.05:
        return col
    out = _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))
    if _luma(out) > NIGHT_GLOW_CAP:
        over = (_luma(out) - NIGHT_GLOW_CAP) / max(1.0, 255 - NIGHT_GLOW_CAP)
        out = _mix(out, (66, 76, 104), min(0.78, 0.5 + over))
    return out


def _hi(c, d, night):
    out = _shade(c, d)
    if night > 0.05 and _luma(out) > NIGHT_GLOW_CAP:
        out = _mix(out, (66, 76, 104), 0.65)
    return out


def _accent(col, night, *, day_ceil=188):
    """A blossom/fruit/ribbon accent: muted, held well under the coin (hard 132
    ceiling at night, softer day ceiling) so warm pops read as seasonal colour
    without becoming the brightest thing on the street."""
    out = _retint(col, night)
    ceil = 132 if night > 0.05 else day_ceil
    if _luma(out) > ceil:
        out = _mix(out, (70, 60, 64) if night <= 0.05 else (66, 72, 96),
                   min(0.7, (_luma(out) - ceil) / 120.0 + 0.3))
    return out


def _night_lift(col, night, frac):
    """Lift a too-dark vessel toward a cool grey on NIGHT only, so a low granite
    trough doesn't merge into the dark ground band."""
    if night <= 0.05:
        return col
    return _mix(col, (104, 112, 132), frac * night)


def draw_greenery(surf, cx, base_y, v, night, t):
    A = v.attrs
    rim_y = _draw_vessel(surf, cx, base_y, v, night, A.get("vessel", "terracotta"))
    {
        "shrub": _sp_shrub, "conifer": _sp_conifer, "topiary": _sp_topiary,
        "flowering": _sp_flowering, "bamboo": _sp_bamboo, "vine": _sp_vine,
        "flovine": _sp_flovine, "kumquat": _sp_kumquat, "wishtree": _sp_wishtree,
    }[A.get("species", "shrub")](surf, cx, rim_y, v, night, t)


# ── vessels — each a distinct outline; returns the rim y the canopy plants into ─

def _draw_vessel(surf, cx, base_y, v, night, kind):
    P, A = v.palette, v.attrs
    vlift = A.get("vlift", 0.0)
    pf = lambda c: _night_lift(_retint(c, night), night, vlift)
    body = pf(P.get("vessel", (170, 104, 72)))
    dk = pf(P.get("vessel_dk", _shade(P.get("vessel", (170, 104, 72)), -34)))
    lt = _hi(body, 18, night)
    g = int(base_y)

    if kind == "terracotta":
        h = VESSEL_H
        top_w, bot_w = 18, 12
        rim_h = 3
        ty = g - h
        pygame.draw.polygon(surf, dk, [
            (cx - top_w // 2, ty + rim_h), (cx + top_w // 2, ty + rim_h),
            (cx + bot_w // 2, g), (cx - bot_w // 2, g)])
        pygame.draw.polygon(surf, body, [
            (cx - top_w // 2 + 1, ty + rim_h), (cx + top_w // 2 - 1, ty + rim_h),
            (cx + bot_w // 2, g - 1), (cx - bot_w // 2, g - 1)])
        pygame.draw.rect(surf, dk, (cx - top_w // 2, ty, top_w, rim_h))
        pygame.draw.rect(surf, body, (cx - top_w // 2 + 1, ty, top_w - 2, rim_h - 1))
        pygame.draw.rect(surf, lt, (cx - top_w // 2 + 1, ty, top_w - 2, 1))
        pygame.draw.line(surf, lt, (cx - top_w // 2 + 2, ty + rim_h + 1), (cx - bot_w // 2 + 1, g - 1), 1)
        return ty + 1

    if kind == "urn":
        h = VESSEL_H + 4
        ty = g - h
        belly_w = 19
        glaze = _retint(P.get("glaze", (96, 120, 170)), night)
        pygame.draw.ellipse(surf, dk, (cx - belly_w // 2, ty + 5, belly_w, h - 4))
        pygame.draw.ellipse(surf, body, (cx - belly_w // 2 + 1, ty + 6, belly_w - 2, h - 6))
        pygame.draw.arc(surf, lt, (cx - belly_w // 2 + 1, ty + 6, belly_w - 2, h - 6),
                        math.radians(40), math.radians(150), 1)
        neck_w = 9
        pygame.draw.rect(surf, body, (cx - neck_w // 2, ty + 2, neck_w, 5))
        pygame.draw.rect(surf, dk, (cx - neck_w // 2, ty + 2, neck_w, 5), 1)
        pygame.draw.ellipse(surf, dk, (cx - neck_w // 2, ty, neck_w, 4))
        pygame.draw.ellipse(surf, _shade(body, -8), (cx - neck_w // 2 + 1, ty + 1, neck_w - 2, 2))
        gby = ty + 9
        pygame.draw.line(surf, glaze, (cx - belly_w // 2 + 2, gby), (cx + belly_w // 2 - 2, gby), 1)
        for dxp in range(-belly_w // 2 + 3, belly_w // 2 - 1, 3):
            pygame.draw.circle(surf, glaze, (cx + dxp, gby + 3), 1)
        return ty + 2

    if kind == "tub":
        h = VESSEL_H + 1
        w = 20
        ty = g - h
        pygame.draw.rect(surf, dk, (cx - w // 2, ty, w, h))
        pygame.draw.rect(surf, body, (cx - w // 2 + 1, ty, w - 2, h - 1))
        for sxp in range(cx - w // 2 + 3, cx + w // 2 - 1, 4):
            pygame.draw.line(surf, _shade(body, -20), (sxp, ty + 1), (sxp, g - 2), 1)
        pygame.draw.line(surf, lt, (cx - w // 2 + 1, ty + 1), (cx + w // 2 - 2, ty + 1), 1)
        hoop = pf(P.get("vessel_dk", (90, 70, 50)))
        for hy in (ty + 2, g - 3):
            pygame.draw.rect(surf, _shade(hoop, -18), (cx - w // 2, hy, w, 2))
            pygame.draw.line(surf, _shade(hoop, 26), (cx - w // 2, hy), (cx + w // 2 - 1, hy), 1)
        return ty + 1

    if kind == "bamboo":
        h = VESSEL_H - 2
        w = 18
        ty = g - h
        cane = pf(P.get("vessel", (150, 160, 96)))
        cane_dk = _shade(cane, -32)
        pygame.draw.rect(surf, _shade(cane, -22), (cx - w // 2, ty, w, h))
        for i, sxp in enumerate(range(cx - w // 2, cx + w // 2 - 1, 3)):
            cc = cane if i % 2 == 0 else _shade(cane, -10)
            pygame.draw.rect(surf, cc, (sxp, ty, 3, h - 1))
            pygame.draw.line(surf, _shade(cc, 22), (sxp, ty), (sxp, g - 1), 1)
            pygame.draw.line(surf, cane_dk, (sxp + 2, ty), (sxp + 2, g - 1), 1)
        for ny in (ty + h // 3, g - 3):
            pygame.draw.line(surf, cane_dk, (cx - w // 2, ny), (cx + w // 2 - 1, ny), 1)
        cord = _retint((150, 120, 70), night)
        pygame.draw.line(surf, cord, (cx - w // 2, ty + 2), (cx + w // 2 - 1, ty + 2), 2)
        return ty

    if kind == "trough":
        h = 9
        w = 22
        ty = g - h
        stone = pf(P.get("vessel", (150, 142, 124)))
        pygame.draw.rect(surf, _shade(stone, -22), (cx - w // 2, ty, w, h))
        pygame.draw.rect(surf, stone, (cx - w // 2 + 1, ty, w - 2, h - 2))
        pygame.draw.rect(surf, _shade(stone, 16), (cx - w // 2 + 1, ty, w - 2, 1))
        pygame.draw.rect(surf, _shade(stone, -14), (cx - w // 2 + 1, ty + 2, w - 2, 1))
        for dxp in (-6, 2, 7):
            pygame.draw.circle(surf, _shade(stone, -18), (cx + dxp, ty + 5), 1)
        return ty

    return g - VESSEL_H


# ── species — each a distinct canopy shape, planted on rim_y ──────────────────

def _foliage(P, night):
    pf = lambda c: _retint(c, night)
    return (pf(P.get("foliage_dark", (40, 80, 55))),
            pf(P.get("foliage_mid", (60, 110, 75))),
            pf(P.get("foliage_top", (96, 150, 100))))


def _dome(surf, cx, cy, rw, rh, dark, mid, lt=None):
    pygame.draw.ellipse(surf, dark, (cx - rw, cy - rh, rw * 2, rh * 2))
    pygame.draw.ellipse(surf, mid, (cx - rw + 1, cy - rh + 1, rw * 2 - 3, rh * 2 - 2))
    if lt is not None:
        pygame.draw.arc(surf, lt, (cx - rw + 1, cy - rh + 1, rw * 2 - 3, rh * 2 - 2),
                        math.radians(35), math.radians(140), 1)


def _leaf_tuft(surf, ox, oy, ang, length, col, *, n=4, spread=0.5):
    for i in range(n):
        a = ang + (i - (n - 1) / 2) * spread / max(1, n - 1)
        ex = ox + int(math.cos(a) * length)
        ey = oy - int(math.sin(a) * length)
        mx = ox + int(math.cos(a) * length * 0.5)
        my = oy - int(math.sin(a) * length * 0.5) - 1
        pygame.draw.lines(surf, col, False, [(ox, oy), (mx, my), (ex, ey)], 1)


def _sp_shrub(surf, cx, rim_y, v, night, t):
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    m = A.get("mass", 1.0)
    sway = math.sin(t * 1.4) * 0.6
    base = rim_y
    for dx, dy, rw, rh in (
            (-int(6 * m), -3, int(7 * m), int(6 * m)),
            (int(6 * m), -4, int(7 * m), int(6 * m)),
            (0, -int(9 * m), int(8 * m), int(7 * m))):
        _dome(surf, cx + dx + int(sway * (dy < -6)), base + dy, rw, rh, dark, mid, top)
    bloom = P.get("accent")
    if bloom:
        ac = _accent(bloom, night)
        for bx, by in ((-5, -6), (4, -8), (0, -12), (6, -4)):
            pygame.draw.circle(surf, ac, (cx + bx, base + by), 1)


def _sp_conifer(surf, cx, rim_y, v, night, t):
    P = v.palette
    dark, mid, top = _foliage(P, night)
    base = rim_y
    tiers = ((9, 0, 6), (7, -6, 6), (5, -12, 5), (3, -17, 4), (2, -21, 3))
    for hw, dy, th in tiers:
        ty = base + dy
        pygame.draw.polygon(surf, dark, [(cx - hw, ty), (cx + hw, ty), (cx, ty - th - 1)])
        pygame.draw.polygon(surf, mid, [(cx - hw + 1, ty - 1), (cx + hw - 1, ty - 1), (cx, ty - th)])
    pygame.draw.line(surf, top, (cx - 1, base - 14), (cx, base - 23), 1)


def _sp_topiary(surf, cx, rim_y, v, night, t):
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    trunk = _retint(P.get("trunk", (110, 84, 56)), night)
    tiers = A.get("tiers", 2)
    base = rim_y
    if tiers == 1:
        ball_r = 7
        stem_h = 15
        cy = base - stem_h - ball_r
        pygame.draw.line(surf, _shade(trunk, -22), (cx + 1, base + 1), (cx + 1, cy + ball_r - 1), 3)
        pygame.draw.line(surf, trunk, (cx, base + 1), (cx, cy + ball_r - 1), 2)
        pygame.draw.line(surf, _shade(trunk, 16), (cx, base + 1), (cx, cy + ball_r - 2), 1)
        pygame.draw.line(surf, dark, (cx - 2, base), (cx + 2, base), 2)
        pygame.draw.circle(surf, dark, (cx, cy), ball_r)
        pygame.draw.circle(surf, mid, (cx, cy), ball_r - 1)
        pygame.draw.circle(surf, top, (cx - ball_r // 3, cy - ball_r // 3), max(1, ball_r // 3))
        return
    radii = {2: (7, 5), 3: (6, 5, 4)}[tiers]
    total_h = sum(r * 2 - 2 for r in radii) + 4
    pygame.draw.line(surf, trunk, (cx, base + 1), (cx, base - total_h), 2)
    pygame.draw.line(surf, _shade(trunk, 16), (cx, base + 1), (cx, base - total_h), 1)
    cy = base - 2
    for i, r in enumerate(radii):
        cy -= r
        pygame.draw.circle(surf, dark, (cx, cy), r)
        pygame.draw.circle(surf, mid, (cx, cy), r - 1)
        pygame.draw.circle(surf, top, (cx - r // 3, cy - r // 3), max(1, r // 3))
        cy -= r - 2


def _sp_flowering(surf, cx, rim_y, v, night, t):
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    sway = math.sin(t * 1.6) * 0.6
    for dx, dy, rw, rh in ((-5, -3, 6, 5), (5, -4, 6, 5), (0, -8, 7, 6)):
        _dome(surf, cx + dx, base + dy, rw, rh, dark, mid)
    bloom = P.get("accent", (210, 130, 150))
    dc = A.get("day_chroma", 188)
    ac = _accent(bloom, night, day_ceil=dc)
    ac_lt = _accent(_shade(bloom, 26), night, day_ceil=dc)
    spots = ((-6, -5), (-2, -9), (3, -7), (6, -3), (1, -12), (-5, -10),
             (5, -9), (-1, -4), (4, -11))
    for i, (bx, byp) in enumerate(spots):
        px, py = cx + bx + int(sway * (byp < -8)), base + byp
        col = ac if i % 3 else ac_lt
        pygame.draw.circle(surf, _accent(_shade(bloom, -28), night, day_ceil=dc), (px, py), 2)
        pygame.draw.circle(surf, col, (px, py), 1)


def _sp_bamboo(surf, cx, rim_y, v, night, t):
    P = v.palette
    dark, mid, top = _foliage(P, night)
    cane = _retint(P.get("trunk", (150, 178, 108)), night)
    cane_dk = _shade(cane, -34)
    cane_lt = _shade(cane, 16)
    base = rim_y
    for dx, htop, lean in ((-4, 26, -1), (0, 34, 0), (4, 29, 2), (7, 22, 2)):
        cxp = cx + dx
        segs = 5
        for s in range(segs):
            y0 = base - htop * s // segs
            y1 = base - htop * (s + 1) // segs
            nx0 = cxp + int(lean * (s / segs))
            nx1 = cxp + int(lean * ((s + 1) / segs))
            pygame.draw.line(surf, cane, (nx0, y0), (nx1, y1 + 1), 2)
            pygame.draw.line(surf, cane_lt, (nx0, y0), (nx1, y1 + 1), 1)
            pygame.draw.line(surf, cane_dk, (nx1 - 1, y1), (nx1 + 1, y1), 1)
        tipx = cxp + lean
        _leaf_tuft(surf, tipx, base - htop, 1.6, 7, mid, n=3, spread=0.7)
        _leaf_tuft(surf, tipx, base - htop, 2.0, 6, top, n=2, spread=0.5)
        _leaf_tuft(surf, tipx, base - htop + 4, 1.2, 5, dark, n=2, spread=0.6)


def _sp_vine(surf, cx, rim_y, v, night, t):
    P = v.palette
    dark, mid, top = _foliage(P, night)
    web = _mix(dark, (0, 0, 0), 0.18)
    base = rim_y
    sway = math.sin(t * 1.8)
    _dome(surf, cx - 4, base - 3, 6, 4, dark, mid)
    _dome(surf, cx + 4, base - 3, 6, 4, dark, mid)
    _dome(surf, cx, base - 5, 7, 5, dark, mid, top)
    for ang in (2.5, 2.1, 1.7, 1.3, 0.9, 0.5):
        _leaf_tuft(surf, cx, base - 5, ang, 7, mid, n=2, spread=0.5)
    for ang in (2.3, 1.6, 0.9):
        _leaf_tuft(surf, cx, base - 5, ang, 8, top, n=1, spread=0.0)
    strands = ((-7, 16, -3, 1.4), (-3, 19, -1, 1.8), (1, 20, 1, 2.0), (5, 17, 3, 1.6))
    paths = []
    for hx, ln, fan, swv in strands:
        pts = [(cx + hx, base - 1)]
        for i in range(1, ln + 1):
            tt = i / ln
            px = cx + hx + int(fan * tt * tt) - int(math.sin(tt * 1.6) * (swv * 0.4)) \
                + int(sway * tt * 1.3)
            py = base - 1 + int(tt * (ln + 2))
            pts.append((px, py))
        paths.append(pts)
    for a, b in zip(paths, paths[1:]):
        n = min(len(a), len(b))
        poly = a[:n] + list(reversed(b[:n]))
        if len(poly) >= 3:
            pygame.draw.polygon(surf, web, poly)
    hem = [p[-1] for p in paths]
    hem_full = [paths[0][-3] if len(paths[0]) >= 3 else paths[0][0]] + hem \
        + [paths[-1][-3] if len(paths[-1]) >= 3 else paths[-1][0]]
    pygame.draw.lines(surf, dark, False, hem_full, 2)
    for pts in paths:
        pygame.draw.lines(surf, dark, False, pts, 2)
        pygame.draw.lines(surf, mid, False, pts, 1)
    for k, pts in enumerate(paths):
        ln = len(pts)
        for ni in (max(2, ln // 3), max(3, (2 * ln) // 3), ln - 1):
            if ni >= ln:
                continue
            px, py = pts[ni]
            side = -1 if k < 2 else 1
            pygame.draw.polygon(surf, mid, [(px, py - 1), (px + side * 3, py), (px, py + 2)])
            pygame.draw.polygon(surf, dark, [(px, py - 1), (px + side * 3, py), (px, py + 2)], 1)
        pygame.draw.circle(surf, top, pts[-1], 1)


def _sp_flovine(surf, cx, rim_y, v, night, t):
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    sway = math.sin(t * 1.7)
    _dome(surf, cx - 5, base - 4, 6, 4, dark, mid)
    _dome(surf, cx + 5, base - 4, 6, 4, dark, mid)
    _dome(surf, cx, base - 6, 7, 5, dark, mid, top)
    bloom = P.get("accent", (200, 132, 170))
    dc = A.get("day_chroma", 172)
    ac = _accent(bloom, night, day_ceil=dc)
    ac_dk = _accent(_shade(bloom, -30), night, day_ceil=dc)
    ac_lt = _accent(_shade(bloom, 22), night, day_ceil=dc)
    falls = ((-8, 4, -3, 7, 3), (8, 4, 3, 7, 3), (0, 6, 0, 9, 4))
    for fi, (ox, slen, drift, ch, cw) in enumerate(falls):
        sx = cx + ox
        stem_pts = []
        for i in range(slen + 1):
            tt = i / slen
            px = sx + int(drift * tt) + int(sway * tt * 1.0)
            py = base - 2 + int(tt * slen)
            stem_pts.append((px, py))
        if len(stem_pts) >= 2:
            pygame.draw.lines(surf, dark, False, stem_pts, 1)
        topx, topy = stem_pts[-1]
        for j in range(ch):
            jt = j / max(1, ch - 1)
            half = max(0, int(round(cw * (1 - jt) * 0.5 + 0.5)))
            yy = topy + j + int(sway * jt * 1.2)
            xx = topx + int(drift * jt * 0.4)
            pygame.draw.line(surf, ac_dk, (xx - half, yy), (xx + half, yy), 1)
            if half >= 1:
                pygame.draw.circle(surf, ac, (xx - half, yy), 1 if half >= 2 else 0)
                pygame.draw.circle(surf, ac, (xx + half, yy), 1 if half >= 2 else 0)
            if j == 1:
                pygame.draw.circle(surf, ac_lt, (xx, yy), 0)
        pygame.draw.circle(surf, ac, (topx + int(drift * 0.4), topy + ch), 0)


def _sp_kumquat(surf, cx, rim_y, v, night, t):
    P = v.palette
    dark, mid, top = _foliage(P, night)
    trunk = _retint(P.get("trunk", (120, 88, 56)), night)
    base = rim_y
    th = 8
    pygame.draw.line(surf, _shade(trunk, -18), (cx + 1, base + 1), (cx + 1, base - th), 2)
    pygame.draw.line(surf, trunk, (cx, base + 1), (cx, base - th), 2)
    cy = base - th
    for dx, dy, rw, rh in ((-6, 1, 5, 5), (6, 1, 5, 5), (0, -5, 6, 6), (-3, -3, 4, 4), (4, -4, 4, 4)):
        _dome(surf, cx + dx, cy + dy, rw, rh, dark, mid, top)
    fruit = P.get("accent", (224, 146, 56))
    fc = _accent(fruit, night)
    fc_lt = _accent(_shade(fruit, 26), night)
    for bx, byp in ((-6, 1), (-1, -3), (4, -1), (6, -6), (-4, -6),
                    (1, -8), (7, 1), (-7, -2), (2, -5)):
        px, py = cx + bx, cy + byp
        pygame.draw.circle(surf, _accent(_shade(fruit, -30), night), (px, py), 2)
        pygame.draw.circle(surf, fc, (px, py), 1)
        pygame.draw.circle(surf, fc_lt, (px - 1, py - 1), 0)


def _sp_wishtree(surf, cx, rim_y, v, night, t):
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    trunk = _retint(P.get("trunk", (96, 66, 42)), night)
    m = A.get("mass", 1.1)
    nrib = A.get("ribbons", 5)
    base = rim_y
    th = int(13 * m)
    pygame.draw.line(surf, _shade(trunk, -20), (cx, base + 1), (cx - 1, base - th // 2), 3)
    pygame.draw.line(surf, trunk, (cx, base + 1), (cx - 1, base - th // 2), 2)
    pygame.draw.line(surf, trunk, (cx - 1, base - th // 2), (cx + 1, base - th), 2)
    cy = base - th - int(4 * m)
    span = int(11 * m)
    crown = (((-7, 2), 6), ((7, 2), 6), ((0, -3), 8), ((-4, -4), 5), ((5, -4), 5), ((0, 4), 6))
    for (ox, oy), r in crown:
        rr = int(r * m)
        _dome(surf, cx + int(ox * m), cy + oy, rr, int(rr * 0.82), dark, mid)
    pygame.draw.circle(surf, top, (cx - 2, cy - 3), int(2 * m))
    for a in (-1.0, -0.6, -0.2, 0.2, 0.6, 1.0):
        fx = cx + int(a * span)
        fy = cy + int(3 + abs(a) * 3)
        droop = int(round(math.sin(t * 1.6 + a * 2.0) * 1.0))
        pts = [(fx, fy), (fx + droop, fy + 4), (fx + droop, fy + 7)]
        pygame.draw.lines(surf, dark, False, pts, 2)
        pygame.draw.lines(surf, mid, False, pts, 1)
    nc = A.get("night_chroma_drop", 0)
    rib_col = P.get("accent", (200, 60, 56))
    rib = _accent(rib_col, night)
    if night > 0.05 and nc:
        rib = _mix(rib, (66, 72, 96), nc)
    rib_l = _accent(_shade(rib_col, 24), night)
    if night > 0.05 and nc:
        rib_l = _mix(rib_l, (66, 72, 96), nc)
    for i in range(nrib):
        a = (i / max(1, nrib - 1)) * 2 - 1
        rx = cx + int(a * span * 0.8)
        ry = cy + int(4 + abs(a) * 3)
        flut = int(round(math.sin(t * 2.2 + i * 1.3) * 1.5))
        pygame.draw.line(surf, rib, (rx, ry), (rx + flut, ry + 6), 2)
        pygame.draw.line(surf, rib_l, (rx, ry), (rx + flut, ry + 2), 1)


# ── the 10-design pool → foreground_variants rows ─────────────────────────────

_TERRA = dict(vessel=(176, 104, 70), vessel_dk=(120, 64, 42))
_URN = dict(vessel=(228, 230, 234), vessel_dk=(170, 176, 188), glaze=(72, 104, 168))
_TUB = dict(vessel=(140, 100, 62), vessel_dk=(92, 62, 38))
_BAMBOO_V = dict(vessel=(156, 166, 100), vessel_dk=(96, 108, 60))
_STONE = dict(vessel=(156, 148, 130), vessel_dk=(104, 98, 86))
_FOL_LEAFY = dict(foliage_dark=(40, 84, 54), foliage_mid=(62, 116, 74), foliage_top=(104, 158, 100))
_FOL_DARK = dict(foliage_dark=(30, 64, 48), foliage_mid=(44, 88, 62), foliage_top=(74, 122, 86))
_FOL_CLIP = dict(foliage_dark=(46, 86, 56), foliage_mid=(72, 120, 78), foliage_top=(118, 162, 110))


def _row(*banks, **attrs):
    pal = {}
    for b in banks:
        pal.update(b)
    return fv.Variant(palette=pal, attrs=dict(attrs))


def _build_greenery():
    return [
        _row(_TERRA, _FOL_LEAFY, dict(accent=(206, 120, 138)),
             vessel="terracotta", species="shrub", mass=1.0),
        _row(_STONE, _FOL_DARK, vessel="trough", species="conifer", vlift=0.10),
        _row(_URN, _FOL_CLIP, vessel="urn", species="topiary", tiers=3, trunk=(96, 84, 66)),
        _row(_TERRA, _FOL_CLIP, vessel="terracotta", species="topiary", tiers=1, trunk=(110, 84, 56)),
        _row(_URN, _FOL_DARK, dict(accent=(204, 122, 142)),
             vessel="urn", species="flowering", day_chroma=170),
        _row(_URN, _FOL_LEAFY, dict(accent=(192, 120, 168)),
             vessel="urn", species="flovine", day_chroma=172),
        _row(_BAMBOO_V, _FOL_LEAFY, dict(trunk=(150, 178, 108)), vessel="bamboo", species="bamboo"),
        _row(_STONE, _FOL_LEAFY, dict(vlift=0.10), vessel="trough", species="vine"),
        _row(_TERRA, _FOL_DARK, dict(accent=(222, 142, 52), trunk=(120, 88, 56)),
             vessel="terracotta", species="kumquat"),
        _row(_URN, _FOL_DARK, dict(trunk=(96, 66, 42), accent=(192, 64, 60)),
             vessel="urn", species="wishtree", mass=1.15, ribbons=6, night_chroma_drop=0.22),
    ]


fv.register("greenery", _build_greenery())
