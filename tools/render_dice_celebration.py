"""Exploration renderer for the dice-results celebration popup.

The clown's floating die settles on a roll N (10..25 pagodas) or a special
GHOST outcome, and a festive popup announces it. This script draws the
surviving structural directions for that "you rolled N!" moment at their TRUE
on-screen size (the popup is ~264 design px wide on the 360 canvas), composited
over a pale-day-sky swatch, with a small actual-size inset per cell so real
small-screen legibility is judged honestly — no flattering zoom-only cells.

Every survivor is built on the hero clown's "Plum & Lime" motif (plum/lime/gold)
and shares one number treatment: cream fill + thick plum outline + drop shadow,
the proven combo. Lime is a panel/backing colour only, never the number or
body text on the sky (it vibrates against cyan).

Run (headless):
    python tools/render_dice_celebration.py
Writes docs/dice_results/round_2.png.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import hud  # vendored bold TTF + cache

# Real canvas width — the popup is centred on a 360-wide portrait canvas.
W = 360
# Day-sky keyframe (game/biome.py): bright cyan top → pale bottom.
SKY_TOP = (40, 110, 200)
SKY_BOT = (170, 220, 245)

# Hero clown "Plum & Lime" palette (from the brief).
PLUM = (96, 44, 150)
PLUM_DK = (66, 28, 110)
LIME = (132, 218, 116)
GOLD = (250, 205, 72)
CREAM = (255, 248, 224)
# GHOST sibling re-skin: same silhouette, dark navy/plum body.
NAVY = (38, 24, 74)
NAVY_LT = (60, 40, 104)


def sky_tile(w, h):
    """A representative pale-day-sky background. The popup sits high (cy~152)
    where the sky is still fairly bright, so we sample a mid-band of the
    full-screen gradient rather than the top."""
    s = pygame.Surface((w, h))
    for y in range(h):
        t = 0.35 + 0.45 * (y / max(1, h - 1))
        col = tuple(int(SKY_TOP[i] + (SKY_BOT[i] - SKY_TOP[i]) * t) for i in range(3))
        pygame.draw.line(s, col, (0, y), (w, y))
    return s


def _num_block(canvas, c, ncy, roll, ss, size=88, num_col=CREAM, edge_col=PLUM,
               shadow_a=110, edge_w=4):
    """The hero number — vendored bold font with a soft drop shadow + thick
    plum outline ring. Standardised cream-on-plum-outline across every survivor
    so the rolled N is unmistakably the dominant element, never a plain score."""
    nf = hud._font(int(size * ss), True)
    num = nf.render(str(roll), True, num_col)
    edge = nf.render(str(roll), True, edge_col)
    shadow = nf.render(str(roll), True, (0, 0, 0))
    shadow.set_alpha(shadow_a)
    canvas.blit(shadow, shadow.get_rect(center=(c + 3 * ss, ncy + 5 * ss)))
    o = edge_w * ss
    ring = []
    for ang in range(0, 360, 30):
        ring.append((math.cos(math.radians(ang)) * o, math.sin(math.radians(ang)) * o))
    for ox, oy in ring:
        canvas.blit(edge, edge.get_rect(center=(c + ox, ncy + oy)))
    nb = num.get_rect(center=(c, ncy))
    canvas.blit(num, nb)
    return nb


def _label_plate(canvas, c, cy, txt, ss, plate_col, text_col, edge_col,
                 size=27, track=True, pad_x=18, pad_y=7, plate_alpha=255):
    """Seat the label on a rounded plate so it never drops out against the sky,
    with the same cream/outline lettering as the number for one read."""
    lf = hud._font(int(size * ss), True)
    spaced = " ".join(txt) if track else txt
    lab = lf.render(spaced, True, text_col)
    pw = lab.get_width() + int(pad_x * 2 * ss)
    ph = lab.get_height() + int(pad_y * 2 * ss)
    plate = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pc = plate_col + (plate_alpha,) if len(plate_col) == 3 else plate_col
    pygame.draw.rect(plate, pc, plate.get_rect(), border_radius=int(ph * 0.5))
    pygame.draw.rect(plate, GOLD + (180,), plate.get_rect(),
                     width=max(1, 2 * ss), border_radius=int(ph * 0.5))
    pr = plate.get_rect(center=(c, cy))
    canvas.blit(plate, pr)
    # Thin outline under the lettering for crisp edges on the plate.
    edge = lf.render(spaced, True, edge_col)
    for ox, oy in ((-ss, 0), (ss, 0), (0, -ss), (0, ss)):
        canvas.blit(edge, edge.get_rect(center=(c + ox, cy + oy)))
    canvas.blit(lab, lab.get_rect(center=(c, cy)))
    return pr


def _star(canvas, cx, cy, r, fill, edge, ss, points=5):
    pts = []
    for i in range(points * 2):
        rr = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / points
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(canvas, edge, pts)
    inner = [(cx + (px - cx) * 0.82, cy + (py - cy) * 0.82) for px, py in pts]
    pygame.draw.polygon(canvas, fill, inner)


def _keyline_halo(canvas, rect_pts_fn, ss):
    """A 2px plum keyline drawn just outside the banner silhouette to kill the
    lime/sky edge vibration — the eye reads a hard plum frame, not a buzzing
    lime/cyan boundary."""
    pass  # banners draw their own plum rolled-edge; halo handled inline.


def _confetti_layer(canvas, c, ss, spread=0.46, n=22, behind=True):
    """Recoloured (plum/lime/gold) pop-in confetti burst FX — diamonds, dots and
    short streamers radiating out behind the frame so the ease-out-back scale
    gets its juice without a competing structure."""
    HD = canvas.get_width()
    pal = [GOLD, LIME, PLUM, CREAM, GOLD, LIME]
    # Short streamer curls.
    for i in range(12):
        a = i * math.tau / 12 + 0.3
        r0 = HD * 0.30
        r1 = HD * spread + (i % 3) * 7 * ss
        col = pal[i % len(pal)]
        pts = []
        for t in range(6):
            tt = t / 5
            r = r0 + (r1 - r0) * tt
            aa = a + math.sin(tt * 3.0 + i) * 0.16
            pts.append((c + math.cos(aa) * r, c + math.sin(aa) * r * 0.92))
        pygame.draw.lines(canvas, col, False, pts, max(2, 3 * ss))
    # Diamonds + dots scattered along the burst front.
    for i in range(n):
        a = i * math.tau / n + 0.5
        dist = HD * 0.30 + (i * 37 % 110) / 110 * HD * 0.16
        px = c + math.cos(a) * dist
        py = c + math.sin(a) * dist * 0.92
        col = pal[i % len(pal)]
        if i % 2 == 0:
            sz = (5 + i % 3 * 2) * ss
            d = pygame.Surface((sz, sz), pygame.SRCALPHA)
            pygame.draw.polygon(d, col + (235,), [(sz // 2, 0), (sz, sz // 2),
                                                  (sz // 2, sz), (0, sz // 2)])
            d = pygame.transform.rotate(d, (i * 47) % 360)
            canvas.blit(d, d.get_rect(center=(int(px), int(py))))
        else:
            pygame.draw.circle(canvas, col, (int(px), int(py)), 3 * ss + i % 2 * ss)


def _banner_body(canvas, c, ss, body_col, frame_col, tail_col, gloss_a=46):
    """Shared ribbon-banner silhouette: flared plum ribbon tails behind a
    rounded placard with a rolled plum frame, a soft gold inner keyline, a glossy
    top sheen, and gold star toppers. The normal roll and the GHOST sibling are
    two skins of THIS one shape — only the body/tail colours differ."""
    HD = canvas.get_width()
    bw, bh = int(HD * 0.74), int(HD * 0.50)
    bx, by = c - bw // 2, c - bh // 2

    tail_w = int(HD * 0.19)
    for sgn in (-1, 1):
        x0 = c + sgn * (bw // 2 - 4 * ss)
        pts = [
            (x0, by + int(bh * 0.18)),
            (x0 + sgn * tail_w, by + int(bh * 0.05)),
            (x0 + sgn * tail_w * 0.7, by + bh // 2),
            (x0 + sgn * tail_w, by + int(bh * 0.95)),
            (x0, by + int(bh * 0.82)),
        ]
        pygame.draw.polygon(canvas, tail_col, pts)

    rad = int(20 * ss)
    # Plum keyline halo + rolled frame: a hard plum boundary that kills the
    # body/sky edge vibration.
    pygame.draw.rect(canvas, frame_col,
                     (bx - 8 * ss, by - 8 * ss, bw + 16 * ss, bh + 16 * ss),
                     border_radius=rad + 8 * ss)
    pygame.draw.rect(canvas, body_col, (bx, by, bw, bh), border_radius=rad)
    pygame.draw.rect(canvas, GOLD, (bx + 6 * ss, by + 6 * ss, bw - 12 * ss, bh - 12 * ss),
                     width=2 * ss, border_radius=rad - 4 * ss)
    gloss = pygame.Surface((bw - 12 * ss, bh // 3), pygame.SRCALPHA)
    gloss.fill((255, 255, 255, gloss_a))
    canvas.blit(gloss, (bx + 6 * ss, by + 6 * ss))
    for sx in (bx + int(bw * 0.14), bx + int(bw * 0.86)):
        _star(canvas, sx, by - 1 * ss, 11 * ss, GOLD, frame_col, ss)
    return bx, by, bw, bh


# ── LEAD: Ribbon Banner (refined) — normal roll ──────────────────────────────
def var_ribbon_banner(roll, ss):
    """Refined lead. Larger number with the dead lime above/below it killed,
    "PAGODAS" seated on a plum plate riding the lower frame, a 2px plum keyline
    halo around the whole banner. Clown lime body, plum frame, gold stars."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)
    bx, by, bw, bh = _banner_body(canvas, c, ss, LIME, PLUM, PLUM_DK)
    # Number sits high in the body; label plate straddles the lower frame so the
    # lime real-estate is the number's, not dead air.
    _num_block(canvas, c, c - int(10 * ss), roll, ss, size=96)
    _label_plate(canvas, c, by + bh + int(2 * ss), "PAGODAS", ss, PLUM, CREAM, PLUM_DK)
    return canvas, D


# ── GHOST sibling re-skin — same banner, dark navy/plum body ──────────────────
def var_ghost_sibling(roll, ss):
    """GHOST as a SIBLING of the lead, not a new shape: the exact ribbon-banner
    silhouette re-skinned to a dark navy/plum body, a friendly ghost mascot
    peeking centred above the panel, "GHOST!" on the same plum plate. No
    ectoplasm columns. The normal roll and this read as two skins of one popup."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    # Ghost mascot centred above, peeking from behind the panel top edge.
    gr = int(HD * 0.115)
    gx = c
    gy = c - int(HD * 0.30)
    gw, gh = gr * 3, int(gr * 3.4)
    ghost = pygame.Surface((gw, gh), pygame.SRCALPHA)
    pygame.draw.circle(ghost, (240, 250, 255, 240), (gw // 2, gr), gr)
    pygame.draw.rect(ghost, (240, 250, 255, 240),
                     (gw // 2 - gr, gr, gr * 2, int(gr * 1.5)))
    for k in range(4):  # scalloped hem
        pygame.draw.circle(ghost, (240, 250, 255, 240),
                           (gw // 2 - gr + int(gr * (0.45 + k * 0.55)), int(gr * 2.45)),
                           int(gr * 0.32))
    # Soft body shade for volume.
    sh = pygame.Surface((gw, gh), pygame.SRCALPHA)
    pygame.draw.circle(sh, (150, 170, 210, 70), (int(gw * 0.62), int(gr * 1.2)),
                       int(gr * 0.8))
    ghost.blit(sh, (0, 0))
    for ex in (-1, 1):
        pygame.draw.circle(ghost, NAVY, (gw // 2 + ex * gr // 2, gr), gr // 4)
    # Rosy cheeks for friendliness.
    for ex in (-1, 1):
        pygame.draw.circle(ghost, (255, 170, 190, 150),
                           (gw // 2 + ex * int(gr * 0.78), int(gr * 1.35)), int(gr * 0.18))
    canvas.blit(ghost, ghost.get_rect(center=(gx, gy)))

    bx, by, bw, bh = _banner_body(canvas, c, ss, NAVY, PLUM, NAVY_LT)
    _num_block(canvas, c, c - int(10 * ss), roll, ss, size=96, edge_col=PLUM)
    _label_plate(canvas, c, by + bh + int(2 * ss), "GHOST!", ss, PLUM, CREAM, PLUM_DK)
    return canvas, D


# ── B-direction: Gold Medallion (refined) ─────────────────────────────────────
def var_medallion(roll, ss):
    """Refined B-direction. Clean symmetric 2-sprig laurel with a real
    silhouette, "PAGODAS" on a cream/plum band off the bezel shadow, gold
    confetti flecks for "festive roll" not "trophy", warmer/tighter plum field
    so the disc feels framed not floating on a bruise."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    # Tighter, warmer framed plum field (ring, not a flat bruise).
    field = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(field, PLUM + (235,), (c, c), int(HD * 0.40))
    pygame.draw.circle(field, GOLD + (210,), (c, c), int(HD * 0.40), max(2, 3 * ss))
    pygame.draw.circle(field, PLUM_DK + (235,), (c, c), int(HD * 0.345))
    canvas.blit(field, (0, 0))

    # Festive gold confetti flecks over the field (reads "roll", not "award").
    for i in range(16):
        a = i * math.tau / 16 + 0.4
        dist = HD * 0.345 + (i % 3) * 6 * ss
        px = c + math.cos(a) * dist
        py = c + math.sin(a) * dist
        col = [GOLD, LIME, CREAM][i % 3]
        if i % 2 == 0:
            sz = (5 + i % 2 * 2) * ss
            d = pygame.Surface((sz, sz), pygame.SRCALPHA)
            pygame.draw.polygon(d, col + (235,),
                                [(sz // 2, 0), (sz, sz // 2), (sz // 2, sz), (0, sz // 2)])
            d = pygame.transform.rotate(d, (i * 51) % 360)
            canvas.blit(d, d.get_rect(center=(int(px), int(py))))
        else:
            pygame.draw.circle(canvas, col, (int(px), int(py)), 3 * ss)

    R = int(HD * 0.275)
    for i in range(40):  # fluted bezel
        a = i * math.tau / 40
        rr = R + (6 * ss if i % 2 == 0 else 2 * ss)
        pygame.draw.line(canvas, (200, 150, 30),
                         (c + math.cos(a) * (R - 2 * ss), c + math.sin(a) * (R - 2 * ss)),
                         (c + math.cos(a) * rr, c + math.sin(a) * rr), max(2, 3 * ss))
    pygame.draw.circle(canvas, (180, 132, 28), (c, c), R)
    pygame.draw.circle(canvas, GOLD, (c, c), R - 5 * ss)
    pygame.draw.circle(canvas, (255, 232, 150), (c, c), R - 5 * ss, max(2, 3 * ss))
    # Clipped top-left specular crescent.
    hl = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(hl, (255, 255, 255, 90), (c - int(R * 0.32), c - int(R * 0.32)),
                       int(R * 0.55))
    mask = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (c, c), R - 8 * ss)
    hl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    canvas.blit(hl, (0, 0))

    # CLEAN symmetric 2-sprig laurel framing the lower disc — each sprig a stem
    # with paired leaves, a real silhouette rather than a smear.
    def sprig(sgn):
        base_a = math.pi * 0.5 + sgn * 0.62
        stem = []
        for t in range(7):
            tt = t / 6
            ar = base_a - sgn * tt * 0.62
            rr = (R - 9 * ss) + tt * 14 * ss
            stem.append((c + math.cos(ar) * rr, c + math.sin(ar) * rr))
        pygame.draw.lines(canvas, (70, 150, 60), False, stem, max(2, 3 * ss))
        for k, (sx, sy) in enumerate(stem):
            if k == 0:
                continue
            la = math.atan2(sy - stem[k - 1][1], sx - stem[k - 1][0])
            for side in (-1, 1):
                lw, lh = int(13 * ss), int(7 * ss)
                leaf = pygame.Surface((lw, lh), pygame.SRCALPHA)
                pygame.draw.ellipse(leaf, LIME, leaf.get_rect())
                pygame.draw.ellipse(leaf, (70, 150, 60), leaf.get_rect(), max(1, ss))
                leaf = pygame.transform.rotate(
                    leaf, -math.degrees(la) + side * 42)
                canvas.blit(leaf, leaf.get_rect(center=(int(sx), int(sy))))
    sprig(-1)
    sprig(1)
    # Tie ribbon knot at the laurel base.
    pygame.draw.circle(canvas, GOLD, (c, c + R + int(2 * ss)), int(6 * ss))
    pygame.draw.circle(canvas, PLUM, (c, c + R + int(2 * ss)), int(6 * ss), max(1, 2 * ss))

    nb = _num_block(canvas, c, c - int(14 * ss), roll, ss, size=80,
                    num_col=CREAM, edge_col=PLUM, edge_w=3)
    _label_plate(canvas, c, c + int(28 * ss), "PAGODAS", ss, CREAM, PLUM, PLUM,
                 size=22)
    return canvas, D


# ── Ribbon Banner + recoloured confetti-burst FX (the "juice" frame) ──────────
def var_ribbon_juice(roll, ss):
    """The lead frame with the recoloured (plum/lime/gold) confetti-burst pop-in
    FX layer firing behind it — shows the ease-out-back scale's juice without a
    competing structure. Same number/label treatment as the lead."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)
    _confetti_layer(canvas, c, ss, spread=0.48, n=24)
    bx, by, bw, bh = _banner_body(canvas, c, ss, LIME, PLUM, PLUM_DK)
    _num_block(canvas, c, c - int(10 * ss), roll, ss, size=96)
    _label_plate(canvas, c, by + bh + int(2 * ss), "PAGODAS", ss, PLUM, CREAM, PLUM_DK)
    return canvas, D


# ── 5th option: framed plaque / starburst-pop alternative ─────────────────────
def var_starburst_plaque(roll, ss):
    """A legitimate alternative that still makes the number the hero: a gold
    pointed-star plaque on a plum sunray field, number stamped on the gold,
    "PAGODAS" on a plum plate beneath. Clown-coloured, different silhouette from
    the banner so we keep a real 5th choice."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    # Plum sunray field behind (alternating shade) so the plaque sits framed.
    rays = 20
    for i in range(rays):
        a0 = i * math.tau / rays
        a1 = a0 + math.tau / rays
        col = PLUM if i % 2 == 0 else PLUM_DK
        pygame.draw.polygon(canvas, col + (210,), [
            (c, c),
            (c + math.cos(a0) * HD * 0.42, c + math.sin(a0) * HD * 0.42),
            (c + math.cos(a1) * HD * 0.42, c + math.sin(a1) * HD * 0.42)])
    # Big rounded-point gold star plaque.
    R = int(HD * 0.32)
    pts = []
    pn = 12
    for i in range(pn * 2):
        rr = R if i % 2 == 0 else R * 0.78
        a = -math.pi / 2 + i * math.pi / pn
        pts.append((c + math.cos(a) * rr, c + math.sin(a) * rr))
    pygame.draw.polygon(canvas, PLUM, [(c + (px - c) * 1.07, c + (py - c) * 1.07)
                                       for px, py in pts])  # plum keyline
    pygame.draw.polygon(canvas, (200, 150, 30), pts)
    inner = [(c + (px - c) * 0.92, c + (py - c) * 0.92) for px, py in pts]
    pygame.draw.polygon(canvas, GOLD, inner)
    # Inner cream disc field for the number to read against.
    pygame.draw.circle(canvas, (255, 240, 200), (c, c), int(R * 0.62))
    pygame.draw.circle(canvas, PLUM, (c, c), int(R * 0.62), max(1, 2 * ss))
    # Lime gem accents at the four cardinal star tips.
    for k in range(4):
        a = -math.pi / 2 + k * math.pi / 2
        gx2, gy2 = c + math.cos(a) * R * 0.92, c + math.sin(a) * R * 0.92
        pygame.draw.circle(canvas, LIME, (int(gx2), int(gy2)), int(5 * ss))
        pygame.draw.circle(canvas, PLUM, (int(gx2), int(gy2)), int(5 * ss), max(1, ss))

    nb = _num_block(canvas, c, c - int(10 * ss), roll, ss, size=82,
                    num_col=PLUM, edge_col=CREAM, edge_w=3)
    _label_plate(canvas, c, c + int(R * 0.62) + int(16 * ss), "PAGODAS", ss,
                 PLUM, CREAM, PLUM_DK, size=22)
    return canvas, D


VARIANTS = [
    ("1  Ribbon Banner (LEAD)", "refined lead, normal roll", var_ribbon_banner, 22),
    ("2  Ribbon Banner — GHOST", "SIBLING re-skin: navy body + mascot", var_ghost_sibling, 10),
    ("3  Gold Medallion", "refined: clean laurel + cream band", var_medallion, 14),
    ("4  Ribbon + Confetti FX", "lead + recoloured pop-in burst (juice)", var_ribbon_juice, 17),
    ("5  Starburst Plaque", "gold star on plum sunrays (alt)", var_starburst_plaque, 23),
]


def main():
    SS = 4  # supersample for crisp downscale to true size
    # True on-screen size: popup is 264 design px on the 360 canvas.
    TRUE = 264
    INSET = 116  # the actual-size inset shows the popup at ~half real size again
    cols = 3
    rows = 2
    pad = 20
    head = 64
    tile_w = TRUE + INSET + 40   # room for the inset to sit clear of the popup
    tile_h = TRUE + 96
    sheet_w = cols * tile_w + (cols + 1) * pad
    sheet_h = head + rows * tile_h + (rows + 1) * pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 34, 42))

    title_f = hud._font(30, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render("Dice-Results Celebration — Round 2 (true on-screen size)",
                              True, (255, 255, 255)), (pad, 12))
    sheet.blit(sub_f.render(
        "Each popup at its real 264px size over day-sky + a tiny actual-size inset. "
        "Cell 2 = GHOST sibling.",
        True, (200, 205, 215)), (pad, 40))

    label_f = hud._font(19, True)
    samp_f = hud._font(13, True)

    for idx, (name, desc, fn, roll) in enumerate(VARIANTS):
        col = idx % cols
        row = idx // cols
        tx = pad + col * (tile_w + pad)
        ty = head + pad + row * (tile_h + pad)

        tile = sky_tile(tile_w, tile_h)
        canvas, D = fn(roll, SS)

        # True on-screen size render, sitting left so the inset stays clear.
        out = pygame.transform.smoothscale(canvas, (TRUE, TRUE))
        tile.blit(out, out.get_rect(center=(16 + TRUE // 2, 36 + TRUE // 2)))

        # Actual-size inset in the clear right column (the popup as it really
        # sits, framed on a mini sky chip) so small-screen legibility is judged
        # honestly without overlapping the true-size render.
        chip = sky_tile(INSET + 16, INSET + 16)
        ins = pygame.transform.smoothscale(canvas, (INSET, INSET))
        chip.blit(ins, ins.get_rect(center=((INSET + 16) // 2, (INSET + 16) // 2)))
        pygame.draw.rect(chip, (255, 255, 255), chip.get_rect(), 2)
        cr = chip.get_rect()
        cr.bottomright = (tile_w - 8, tile_h - 34)
        tile.blit(chip, cr)
        ilab = samp_f.render("actual size", True, (255, 255, 255))
        ib = pygame.Surface((ilab.get_width() + 6, ilab.get_height() + 2),
                            pygame.SRCALPHA)
        ib.fill((20, 22, 28, 200))
        ib.blit(ilab, (3, 1))
        tile.blit(ib, (cr.left, cr.top - ib.get_height() - 1))

        strip = pygame.Surface((tile_w, 30), pygame.SRCALPHA)
        strip.fill((20, 22, 28, 205))
        tile.blit(strip, (0, 0))
        tag = (255, 210, 110) if "GHOST" in name else LIME
        tile.blit(label_f.render(name, True, tag), (8, 6))
        cap = pygame.Surface((tile_w, 24), pygame.SRCALPHA)
        cap.fill((20, 22, 28, 205))
        tile.blit(cap, (0, tile_h - 24))
        tile.blit(samp_f.render(f"{desc}  (roll {roll})", True, (220, 225, 235)),
                  (8, tile_h - 21))
        sheet.blit(tile, (tx, ty))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "dice_results")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
