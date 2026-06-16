"""
Round-1 review renderer for RAIJIN — the thunder-drum ring demon
(Section 3 Japanese, GREY RECEDES; GOLD+CRIMSON FOCAL).

House style: chibi, flat saturated fills, hard ink keylines, the
dark-core -> flat-fill -> top-left rim-sheen TRIAD, a 1px outline grown from
the alpha mask, and supersample -> smoothscale. The creature is drawn once at
a high supersample factor onto a transparent surface, outlined from its own
alpha mask, then downscaled for the crisp large + 32px review tiles.

The key brief constraint: the storm-grey-blue BODY is low-contrast and is
designed to RECEDE into a dark-blue night sky; the GOLD lightning-zags and
CRIMSON drum-rims are the brightest, highest-contrast masses so they read
FIRST. The drum-ring halo (a circular crown of taiko drums arcing overhead)
is the wholly-unique read; the accessibility tell is the drum-ring CIRCLE +
zag SHAPE, carrying the read where the grey body can't. The sheet verifies
the focal pop against a dedicated dark-blue NIGHT swatch.

Standalone headless script: writes round_1.png next to itself. No game imports
so the review sheet stays reproducible in isolation.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import math
import pygame

# ── PINNED PALETTE (exact hexes from the locked Raijin brief) ───────────────
BODY      = (108, 124, 144)   # storm-grey-blue body — RECEDES, low chroma/mid value
BODY_D    = (66, 80, 100)     # deep-slate shade (dark core)
SHEEN     = (168, 184, 204)   # top-left rim sheen
GOLD      = (248, 212, 96)    # thunder-gold lightning FOCAL
GOLD_D    = (196, 156, 52)    # gold dark core (derived, same family)
GOLD_RIM  = (255, 240, 168)   # gold sheen (derived)
CRIMSON   = (206, 62, 52)     # drum-crimson rim FOCAL
CRIMSON_D = (150, 34, 30)     # crimson dark core (derived)
CRIMSON_R = (236, 116, 96)    # crimson sheen (derived)
CLOUD     = (232, 236, 240)   # cloud-white
CLOUD_D   = (188, 196, 210)   # cloud shade (derived)
TOMOE_INK = (34, 30, 38)      # tomoe comma-swirl ink on drum heads
INK       = (24, 28, 34)      # keyline ink
DRUM_SKIN = (224, 206, 176)   # taiko drum head (vellum) — neutral, sits under focal
DRUM_SK_D = (180, 158, 124)
DRUM_BODY = (120, 78, 52)     # drum wood barrel body (warm brown, low key)
DRUM_BD_D = (84, 52, 34)
DRUM_BD_R = (160, 112, 78)
TIGER     = (216, 178, 96)    # tiger-print wrap base (muted ochre, NOT a focal)
TIGER_D   = (150, 116, 56)

SS = 4   # supersample factor for the large render


def _poly(surf, color, pts):
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])


def _ellipse(surf, color, cx, cy, rx, ry):
    pygame.draw.ellipse(surf, color, (int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2)))


def grow_outline(src, ink, px):
    """1px (scaled) ink keyline grown from the sprite's own alpha mask, so the
    silhouette POPs against any biome. We dilate by stamping the alpha mask in
    a ring of offsets behind the art."""
    mask = pygame.mask.from_surface(src)
    out = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    stamp = mask.to_surface(setcolor=(*ink, 255), unsetcolor=(0, 0, 0, 0))
    r = px
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                out.blit(stamp, (dx, dy))
    out.blit(src, (0, 0))
    return out


def _zag(surf, x0, y0, x1, y1, w, body=GOLD, core=GOLD_D, rim=GOLD_RIM):
    """A jagged lightning bolt between two endpoints — the gold FOCAL. Drawn as
    a dark-core stroke, a flat-fill stroke, then a thin top-left rim sheen, so
    it carries the same triad as the solid masses but stays the brightest."""
    n = 3
    pts = [(x0, y0)]
    for i in range(1, n):
        t = i / n
        mx = x0 + (x1 - x0) * t
        my = y0 + (y1 - y0) * t
        # alternate the kink side for the classic zag
        off = (w * 1.7) * (1 if i % 2 else -1)
        # perpendicular offset
        dx, dy = (x1 - x0), (y1 - y0)
        ln = max(1.0, math.hypot(dx, dy))
        px, py = -dy / ln, dx / ln
        pts.append((mx + px * off, my + py * off))
    pts.append((x1, y1))
    pygame.draw.lines(surf, core, False, [(int(a), int(b)) for a, b in pts], int(w * 2.0))
    pygame.draw.lines(surf, body, False, [(int(a), int(b)) for a, b in pts], int(w))
    pygame.draw.lines(surf, rim, False,
                      [(int(a - w * 0.4), int(b - w * 0.4)) for a, b in pts], max(1, int(w * 0.4)))


def _taiko_drum(surf, cx, cy, r, ang, s, head_to_viewer=True):
    """One den-den-daiko / taiko drum in the halo ring. CRIMSON laced rim is the
    focal; vellum head carries a TOMOE comma-swirl. `ang` tilts the head so the
    ring reads as drums facing outward around the halo."""
    # wood barrel body peeking behind the head (low-key brown, recedes)
    bw, bh = r * 1.05, r * 1.18
    _ellipse(surf, DRUM_BD_D, cx + 1.5 * s, cy + 1.5 * s, bw, bh)
    _ellipse(surf, DRUM_BODY, cx, cy, bw - 1.0 * s, bh - 1.0 * s)
    _ellipse(surf, DRUM_BD_R, cx - bw * 0.32, cy - bh * 0.34, bw * 0.30, bh * 0.30)

    # CRIMSON rim ring — the focal. Drawn as a fat crimson disc, then the vellum
    # head inset leaves the crimson as a bold ring.
    _ellipse(surf, CRIMSON_D, cx + 0.8 * s, cy + 0.8 * s, r + 0.5 * s, r + 0.5 * s)
    _ellipse(surf, CRIMSON, cx, cy, r, r)
    _ellipse(surf, CRIMSON_R, cx - r * 0.42, cy - r * 0.42, r * 0.34, r * 0.34)
    # vellum head inset
    hr = r * 0.70
    _ellipse(surf, DRUM_SK_D, cx + 0.5 * s, cy + 0.5 * s, hr + 0.4 * s, hr + 0.4 * s)
    _ellipse(surf, DRUM_SKIN, cx, cy, hr, hr)
    _ellipse(surf, (240, 226, 200), cx - hr * 0.4, cy - hr * 0.4, hr * 0.30, hr * 0.30)

    # tomoe comma-swirl ink on the head (two-comma mitsudomoe-lite)
    for k in range(2):
        a = ang + k * math.pi
        tx = cx + math.cos(a) * hr * 0.30
        ty = cy + math.sin(a) * hr * 0.30
        # comma head
        _ellipse(surf, TOMOE_INK, tx, ty, hr * 0.30, hr * 0.30)
        # comma tail curling
        tpts = []
        for j in range(5):
            tt = j / 4
            aa = a + tt * 2.1
            rr = hr * 0.30 * (1 - tt)
            tpts.append((tx + math.cos(aa) * (hr * 0.42 * tt) ,
                         ty + math.sin(aa) * (hr * 0.42 * tt)))
        if len(tpts) > 1:
            pygame.draw.lines(surf, TOMOE_INK, False,
                              [(int(a2), int(b2)) for a2, b2 in tpts], max(1, int(s * 1.4)))

    # crimson lacing ropes (tatemimi) — short crimson ticks around the rim
    for a in range(0, 360, 60):
        ar = math.radians(a)
        x0 = cx + math.cos(ar) * r * 0.86
        y0 = cy + math.sin(ar) * r * 0.86
        x1 = cx + math.cos(ar) * (r + 1.6 * s)
        y1 = cy + math.sin(ar) * (r + 1.6 * s)
        pygame.draw.line(surf, CRIMSON_D, (int(x0), int(y0)), (int(x1), int(y1)), max(1, int(s)))


def draw_raijin(surf, ox, oy, s):
    """Draw the chibi storm-god centred near (ox, oy). `s` is unit scale.
    Drum-ring halo arcs OVERHEAD; grey body sits low-contrast below; gold zags
    + crimson rims are the focal."""

    def P(x, y):  # local unit coords -> surface px
        return (ox + x * s, oy + y * s)

    # ---- cloud-puff perch (drawn first, behind feet) ----
    cl_y = 30
    for cdx, cw, ch in [(-12, 13, 7), (12, 13, 7), (0, 16, 8), (-6, 11, 6), (7, 11, 6)]:
        _ellipse(surf, CLOUD_D, ox + (cdx) * s, oy + (cl_y + 1) * s, cw * s, ch * s)
        _ellipse(surf, CLOUD, ox + (cdx) * s, oy + cl_y * s, (cw - 1) * s, (ch - 1) * s)

    # ---- drum-ring HALO arcing overhead (the unique read) ----
    # 5 drums arc across the top in a semicircle behind the head. Drawn BEFORE
    # the head/body so the figure overlaps the lower drums and reads as centred
    # inside the ring. Radius + angular sweep give the crown-of-drums silhouette.
    ring_cx, ring_cy = 0, -10
    ring_r = 30
    drum_r = 8.5
    # sweep from lower-left up over the top to lower-right
    sweep = [200, 234, 270, 306, 340]   # degrees, screen coords (y down)
    for i, deg in enumerate(sweep):
        a = math.radians(deg)
        dx = ring_cx + math.cos(a) * ring_r
        dy = ring_cy + math.sin(a) * ring_r
        # head faces roughly outward along the ring radius
        _taiko_drum(surf, ox + dx * s, oy + dy * s, drum_r * s, a + math.pi / 2, s)

    # ---- wild spiky flame-hair behind the head (grey-blue, recedes) ----
    hair_cx, hair_cy = 0, -14
    spikes = [(-12, -10, -20, -22), (-7, -13, -11, -28), (0, -14, 0, -30),
              (7, -13, 11, -28), (12, -10, 20, -22),
              (-15, -4, -26, -10), (15, -4, 26, -10)]
    for bx, by, tx, ty in spikes:
        pts = [P(bx - 3, by), P(tx, ty), P(bx + 3, by)]
        _poly(surf, BODY_D, [(x + 1.5, y + 1.5) for x, y in pts])
        _poly(surf, BODY, pts)
    # a couple of hair spikes tipped with a tiny gold static-flash (focal accent)
    for tx, ty in [(-26, -10), (0, -30), (26, -10)]:
        _ellipse(surf, GOLD, ox + tx * s, oy + ty * s, 1.6 * s, 1.6 * s)
        _ellipse(surf, GOLD_RIM, ox + (tx - 0.5) * s, oy + (ty - 0.5) * s, 0.7 * s, 0.7 * s)

    # ---- muscular storm-grey torso (chibi, short + wide, weight-shifted) ----
    tx, ty = 0, 12
    _ellipse(surf, BODY_D, *P(tx, ty + 1), 16 * s, 17 * s)            # dark core
    _ellipse(surf, BODY, ox + (tx + 1) * s, oy + (ty + 1) * s, 14.5 * s, 15.5 * s)  # fill
    _ellipse(surf, SHEEN, ox + (tx - 6) * s, oy + (ty - 6) * s, 6 * s, 5 * s)       # TL rim sheen

    # pectoral / muscle seams (triad-lit grooves, very low contrast — recede)
    pygame.draw.line(surf, BODY_D, P(-7, 6), P(-2, 9), max(1, int(s)))
    pygame.draw.line(surf, BODY_D, P(7, 6), P(2, 9), max(1, int(s)))
    pygame.draw.line(surf, BODY_D, P(0, 9), P(0, 18), max(1, int(s)))

    # ---- tiger-print loincloth wrap (muted ochre, NOT a focal) ----
    wrap = [(-12, 18), (12, 18), (10, 28), (-10, 28)]
    _poly(surf, TIGER_D, [P(x + 1, y + 1) for x, y in wrap])
    _poly(surf, TIGER, [P(x, y) for x, y in wrap])
    # tiger stripes (dark slashes)
    for sx in (-7, -1, 5):
        pygame.draw.line(surf, TIGER_D, P(sx, 19), P(sx - 2, 27), max(1, int(s * 1.2)))
    # belt
    pygame.draw.rect(surf, BODY_D, (int(P(-12, 17)[0]), int(P(-12, 17)[1]), int(24 * s), int(2.2 * s)))

    # ---- legs perched cross/squat on the cloud ----
    for lx, sign in [(-7, -1), (7, 1)]:
        leg = [(lx - 3, 27), (lx + 3, 27), (lx + 5 * (1 if sign > 0 else 1), 33),
               (lx + sign * 2, 35), (lx - 3, 33)]
        _poly(surf, BODY_D, [P(x + 1, y + 1) for x, y in leg])
        _poly(surf, BODY, [P(x, y) for x, y in leg])

    # ---- arms raised, each gripping a mallet (bachi) ----
    def arm_and_mallet(shoulder, elbow, hand, head_pos):
        sx, sy = shoulder
        ex, ey = elbow
        hx, hy = hand
        # upper + fore arm as tapered grey limbs
        pygame.draw.line(surf, BODY_D, P(sx, sy + 0.5), P(ex, ey + 0.5), max(2, int(4.2 * s)))
        pygame.draw.line(surf, BODY, P(sx, sy), P(ex, ey), max(2, int(3.4 * s)))
        pygame.draw.line(surf, BODY_D, P(ex, ey + 0.5), P(hx, hy + 0.5), max(2, int(3.8 * s)))
        pygame.draw.line(surf, BODY, P(ex, ey), P(hx, hy), max(2, int(3.0 * s)))
        # fist
        _ellipse(surf, BODY_D, *P(hx, hy + 0.4), 3 * s, 3 * s)
        _ellipse(surf, BODY, ox + hx * s, oy + hy * s, 2.6 * s, 2.6 * s)
        # mallet shaft (banded) from fist toward head
        pygame.draw.line(surf, (150, 116, 70), P(hx, hy), head_pos, max(2, int(2.4 * s)))
        pygame.draw.line(surf, (196, 158, 100), P(hx + 0.4, hy - 0.4),
                         (head_pos[0] + 0.4, head_pos[1] - 0.4), max(1, int(1.2 * s)))
        # mallet knob
        _ellipse(surf, DRUM_BD_D, head_pos[0] + 0.8 * s, head_pos[1] + 0.8 * s, 3.4 * s, 3.4 * s)
        _ellipse(surf, DRUM_BODY, *head_pos, 3.0 * s, 3.0 * s)
        _ellipse(surf, DRUM_BD_R, head_pos[0] - 1.2 * s, head_pos[1] - 1.2 * s, 1.1 * s, 1.1 * s)

    arm_and_mallet((-12, 6), (-19, -2), (-22, -8), P(-26, -16))
    arm_and_mallet((12, 6), (19, -2), (22, -8), P(26, -16))

    # ---- a bold GOLD lightning zag arcing between the raised mallets (focal) ----
    _zag(surf, ox - 24 * s, oy - 17 * s, ox + 24 * s, oy - 17 * s, 2.6 * s)
    # a second short zag forking down toward the figure (more focal mass low)
    _zag(surf, ox + 2 * s, oy - 13 * s, ox - 4 * s, oy + 4 * s, 2.0 * s)

    # ---- head: chibi, big, fierce ----
    hx, hy, hr = 0, -13, 13
    _ellipse(surf, BODY_D, *P(hx, hy), hr * s, (hr - 0.5) * s)
    _ellipse(surf, BODY, ox + (hx + 1) * s, oy + (hy + 1) * s, (hr - 1.5) * s, (hr - 2) * s)
    _ellipse(surf, SHEEN, ox + (hx - 5) * s, oy + (hy - 5) * s, 5 * s, 4.5 * s)
    # jaw flare / wide shout
    _ellipse(surf, BODY, ox + hx * s, oy + (hy + 5) * s, (hr - 2) * s, 9 * s)

    # ---- fierce round eyes (whites with gold-amber glow ring) ----
    for ex in (-6, 6):
        _ellipse(surf, CLOUD, *P(hx + ex, hy - 2), 4.2 * s, 4.6 * s)
        # gold iris ring — small focal sparks in the eyes
        _ellipse(surf, GOLD, ox + (hx + ex) * s, oy + (hy - 1.5) * s, 2.6 * s, 2.8 * s)
        _ellipse(surf, INK, ox + (hx + ex + ex * 0.08) * s, oy + (hy - 1) * s, 1.5 * s, 1.7 * s)
        _ellipse(surf, CLOUD, ox + (hx + ex - 1.1) * s, oy + (hy - 2.6) * s, 0.9 * s, 0.9 * s)
    # furious angled brows (dark, low-contrast)
    pygame.draw.line(surf, BODY_D, P(hx - 10, hy - 6), P(hx - 2, hy - 3), max(2, int(2 * s)))
    pygame.draw.line(surf, BODY_D, P(hx + 10, hy - 6), P(hx + 2, hy - 3), max(2, int(2 * s)))

    # ---- wide open shout mouth (dark hollow + tiny fangs) ----
    mpts = [(-5, 4), (5, 4), (4, 9), (0, 11), (-4, 9)]
    _poly(surf, INK, [P(x, y) for x, y in mpts])
    _poly(surf, CRIMSON_D, [P(x * 0.7, y * 0.7 + 4) for x, y in mpts])  # red maw interior
    # fangs
    _poly(surf, CLOUD, [P(-4, 4), P(-2.5, 4), P(-3.2, 6.5)])
    _poly(surf, CLOUD, [P(4, 4), P(2.5, 4), P(3.2, 6.5)])


def draw_mallet_drum_pillar(surf, cx, top, bottom, w, s, cap=True):
    """Prop -> PILLAR mirror: a banded drum-MALLET (bachi) shaft is the
    repeatable body; a single modest FRONT-ON taiko drum with a lightning-zag
    cracking it is the detachable gap-edge cap.

    TOP-HEAVY FIX (per AD): the cap drum is rendered front-on and MODEST
    (~shaft-width +30%, NOT the full creature drum-ring), seated tight on the
    haft axis, with the CRIMSON rim + a short GOLD zag dropping INTO the gap so
    the visual mass falls toward the gap line — balanced like Big Reapy's
    bone-bident."""
    half = w // 2
    # ---- mallet-shaft body (banded wood) ----
    pygame.draw.rect(surf, DRUM_BD_D, (cx - half - int(2 * s), top, w + int(4 * s), bottom - top))
    pygame.draw.rect(surf, DRUM_BODY, (cx - half, top, w, bottom - top))
    # top-left rim sheen stripe
    pygame.draw.rect(surf, DRUM_BD_R, (cx - half + int(2 * s), top, max(2, w // 5), bottom - top))
    # rope-grip banding (the repeatable banding)
    seg_h = w * 1.7
    y = top + seg_h
    while y < bottom:
        pygame.draw.rect(surf, DRUM_BD_D, (cx - half - int(3 * s), int(y) - int(2 * s),
                                           w + int(6 * s), int(4 * s)))
        # crimson lacing tick on the band (echoes the creature's drum rims)
        pygame.draw.line(surf, CRIMSON, (cx - half, int(y)), (cx + half, int(y)), max(1, int(s)))
        y += seg_h

    if cap:
        # ---- gap-edge cap: modest front-on taiko drum cracked by a zag ----
        # Drum diameter ~ shaft +30% — deliberately NOT the full halo ring.
        dr = (w * 1.30) / 2
        dcx = cx
        dcy = top - dr - int(1 * s)
        # wood barrel behind
        _ellipse(surf, DRUM_BD_D, dcx + 1.5 * s, dcy + 1.5 * s, dr * 1.06, dr * 1.18)
        _ellipse(surf, DRUM_BODY, dcx, dcy, dr * 0.98, dr * 1.10)
        # CRIMSON rim ring (focal)
        _ellipse(surf, CRIMSON_D, dcx + 0.8 * s, dcy + 0.8 * s, dr + 0.6 * s, dr + 0.6 * s)
        _ellipse(surf, CRIMSON, dcx, dcy, dr, dr)
        _ellipse(surf, CRIMSON_R, dcx - dr * 0.42, dcy - dr * 0.42, dr * 0.32, dr * 0.32)
        # vellum head
        hr = dr * 0.72
        _ellipse(surf, DRUM_SK_D, dcx + 0.5 * s, dcy + 0.5 * s, hr + 0.4 * s, hr + 0.4 * s)
        _ellipse(surf, DRUM_SKIN, dcx, dcy, hr, hr)
        # tomoe swirl
        for k in range(2):
            a = (k * math.pi) - 0.6
            tx = dcx + math.cos(a) * hr * 0.30
            tyy = dcy + math.sin(a) * hr * 0.30
            _ellipse(surf, TOMOE_INK, tx, tyy, hr * 0.30, hr * 0.30)
            tpts = []
            for j in range(5):
                tt = j / 4
                aa = a + tt * 2.1
                tpts.append((tx + math.cos(aa) * (hr * 0.42 * tt),
                             tyy + math.sin(aa) * (hr * 0.42 * tt)))
            pygame.draw.lines(surf, TOMOE_INK, False,
                              [(int(a2), int(b2)) for a2, b2 in tpts], max(1, int(s * 1.4)))
        # crimson lacing ticks
        for a in range(0, 360, 60):
            ar = math.radians(a)
            x0 = dcx + math.cos(ar) * dr * 0.86
            y0 = dcy + math.sin(ar) * dr * 0.86
            x1 = dcx + math.cos(ar) * (dr + 1.6 * s)
            y1 = dcy + math.sin(ar) * (dr + 1.6 * s)
            pygame.draw.line(surf, CRIMSON_D, (int(x0), int(y0)), (int(x1), int(y1)), max(1, int(s)))
        # short GOLD zag cracking the drum head and DROPPING INTO the gap — a
        # clean 3-kink fork (not a swirl), pulling the visual mass down toward
        # the gap line so the cap stays balanced on the haft.
        zpts = [(dcx + dr * 0.18, dcy - dr * 0.34),
                (dcx - dr * 0.20, dcy + dr * 0.10),
                (dcx + dr * 0.14, dcy + dr * 0.42),
                (dcx - w * 0.10, top + int(3 * s))]
        zpts = [(int(a), int(b)) for a, b in zpts]
        pygame.draw.lines(surf, GOLD_D, False, zpts, int(3.0 * s))
        pygame.draw.lines(surf, GOLD, False, zpts, int(1.8 * s))
        pygame.draw.lines(surf, GOLD_RIM, False,
                          [(a - int(0.8 * s), b - int(0.8 * s)) for a, b in zpts], max(1, int(0.8 * s)))


def build_raijin_sprite(unit_px):
    """Render raijin at unit_px supersampled, outline from its alpha mask,
    return the high-res surface (caller smoothscales)."""
    W = int(64 * unit_px)
    H = int(72 * unit_px)
    big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    draw_raijin(big, big.get_width() // 2, int(H * SS * 0.50), unit_px * SS)
    big = grow_outline(big, INK, SS)
    return big, (W, H)


def build_pillar_sprite(unit_px):
    W = int(34 * unit_px)
    H = int(98 * unit_px)
    big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    draw_mallet_drum_pillar(big, big.get_width() // 2,
                            int(26 * unit_px * SS), big.get_height(),
                            int(12 * unit_px * SS), unit_px * SS, cap=True)
    big = grow_outline(big, INK, SS)
    return big, (W, H)


def main():
    pygame.init()

    SHEET_W, SHEET_H = 860, 760
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    # a mid day-sky gradient for the large views (the brief wants the focal to
    # pop on a DARK-BLUE NIGHT swatch too — that lives in its own panel below)
    sky_a, sky_b = (150, 176, 210), (110, 142, 184)
    for y in range(SHEET_H):
        t = y / SHEET_H
        c = tuple(int(sky_a[i] + (sky_b[i] - sky_a[i]) * t) for i in range(3))
        pygame.draw.line(sheet, c, (0, y), (SHEET_W, y))

    font = pygame.font.SysFont("dejavusans", 18, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)
    title = pygame.font.SysFont("dejavusans", 22, bold=True)

    def label(text, x, y, col=(20, 24, 30)):
        sheet.blit(font.render(text, True, (250, 252, 248)), (x + 1, y + 1))
        sheet.blit(font.render(text, True, col), (x, y))

    def slabel(text, x, y, col=(24, 28, 34), light=(250, 252, 248)):
        sheet.blit(small.render(text, True, light), (x + 1, y + 1))
        sheet.blit(small.render(text, True, col), (x, y))

    sheet.blit(title.render("RAIJIN — thunder-drum ring demon", True, (250, 252, 248)), (19, 13))
    sheet.blit(title.render("RAIJIN — thunder-drum ring demon", True, (24, 30, 38)), (18, 12))
    sheet.blit(small.render("GREY RECEDES; GOLD+CRIMSON FOCAL  ·  drum-ring halo  ·  chibi storm-god on a cloud",
                            True, (24, 30, 40)), (18, 38))

    # ---- large creature ----
    big_c, _ = build_raijin_sprite(4.6)
    large_c = pygame.transform.smoothscale(big_c, (big_c.get_width() // SS, big_c.get_height() // SS))
    sheet.blit(large_c, (16, 64))
    label("creature", 110, 66 + large_c.get_height())
    slabel("drum-ring halo overhead · gold zag + crimson rims read first", 24, 88 + large_c.get_height())

    # ---- large pillar mirror ----
    big_p, _ = build_pillar_sprite(4.2)
    large_p = pygame.transform.smoothscale(big_p, (big_p.get_width() // SS, big_p.get_height() // SS))
    sheet.blit(large_p, (366, 64))
    label("mallet + drum pillar", 338, 66 + large_p.get_height())
    slabel("MODEST front-on cap (~shaft+30%);", 338, 88 + large_p.get_height())
    slabel("crimson rim + gold zag drop INTO gap", 338, 104 + large_p.get_height())

    # ---- scale strip: creature + pillar on DAY and on DARK-BLUE NIGHT ----
    def to_h(big, target_h):
        w, h = big.get_size()
        scale = (target_h * SS) / h
        return pygame.transform.smoothscale(big, (max(1, int(w * scale / SS)), target_h))

    panel_x = 560
    pw = 240
    # DAY panel
    pygame.draw.rect(sheet, (192, 210, 234), (panel_x, 64, pw, 232), border_radius=8)
    pygame.draw.rect(sheet, (44, 56, 72), (panel_x, 64, pw, 232), 2, border_radius=8)
    slabel("on DAY sky", panel_x + 12, 70)
    sheet.blit(to_h(big_c, 96), (panel_x + 14, 96))
    sheet.blit(to_h(big_p, 150), (panel_x + 150, 90))
    slabel("48px", panel_x + 30, 250)
    slabel("48px", panel_x + 156, 250)
    sheet.blit(to_h(big_c, 48), (panel_x + 14, 200))
    sheet.blit(to_h(big_p, 70), (panel_x + 110, 200))
    sheet.blit(to_h(big_c, 32), (panel_x + 178, 214))

    # NIGHT panel — dark-blue night biome swatch; verifies grey RECEDES + focal pops
    ny = 312
    nh = 252
    pygame.draw.rect(sheet, (18, 24, 46), (panel_x, ny, pw, nh), border_radius=8)
    pygame.draw.rect(sheet, (60, 78, 120), (panel_x, ny, pw, nh), 2, border_radius=8)
    # a few stars to sell the night biome
    import random as _r
    rng = _r.Random(99)
    for _ in range(46):
        sx = rng.randint(panel_x + 6, panel_x + pw - 6)
        sy = rng.randint(ny + 26, ny + nh - 6)
        pygame.draw.circle(sheet, (210, 220, 240), (sx, sy), rng.choice((1, 1, 2)))
    slabel("DARK-BLUE NIGHT — grey recedes, gold+crimson pop",
           panel_x + 10, ny + 6, col=(200, 214, 240), light=(8, 12, 28))
    sheet.blit(to_h(big_c, 100), (panel_x + 12, ny + 28))
    sheet.blit(to_h(big_p, 156), (panel_x + 150, ny + 24))
    # tiny stress reads
    sheet.blit(to_h(big_c, 32), (panel_x + 150, ny + 188))
    sheet.blit(to_h(big_c, 24), (panel_x + 196, ny + 196))
    slabel("32 / 24px", panel_x + 150, ny + 224, col=(200, 214, 240), light=(8, 12, 28))

    # ---- 32px row on a flat dark-blue strip below the large creature/pillar ----
    strip_y = 64 + max(large_c.get_height(), large_p.get_height()) + 50
    pygame.draw.rect(sheet, (20, 26, 48), (16, strip_y, 520, 100), border_radius=8)
    pygame.draw.rect(sheet, (60, 78, 120), (16, strip_y, 520, 100), 2, border_radius=8)
    slabel("32px read on night biome — drum-ring CIRCLE + zag SHAPE carry the read where grey can't",
           24, strip_y + 6, col=(200, 214, 240), light=(8, 12, 28))
    sheet.blit(to_h(big_c, 38), (44, strip_y + 32))
    sheet.blit(to_h(big_c, 32), (118, strip_y + 36))
    sheet.blit(to_h(big_p, 74), (200, strip_y + 22))
    sheet.blit(to_h(big_p, 50), (270, strip_y + 36))
    # creature + pillar side-by-side at true 32 to confirm they pair as a set
    sheet.blit(to_h(big_c, 32), (360, strip_y + 36))
    sheet.blit(to_h(big_p, 56), (430, strip_y + 32))

    # ---- palette swatches (bottom strip, clear of everything) ----
    swatches = [("body recedes", BODY), ("shade", BODY_D), ("GOLD focal", GOLD),
                ("CRIMSON focal", CRIMSON), ("cloud", CLOUD), ("drum wood", DRUM_BODY),
                ("sheen", SHEEN)]
    sx = 24
    sy = strip_y + 124
    slabel("pinned palette:", sx, sy - 18)
    for name, col in swatches:
        pygame.draw.rect(sheet, col, (sx, sy, 26, 26), border_radius=4)
        pygame.draw.rect(sheet, (18, 22, 28), (sx, sy, 26, 26), 1, border_radius=4)
        sheet.blit(small.render(name, True, (250, 252, 248)), (sx + 1, sy + 28))
        sheet.blit(small.render(name, True, (22, 26, 32)), (sx, sy + 27))
        sx += small.size(name)[0] + 22

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
