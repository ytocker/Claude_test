"""Exploration renderer for the dice-results celebration popup.

The clown's floating die settles on a roll N (10..25 pagodas) or a special
GHOST outcome, and a festive popup announces it. This script draws 5 distinct
structural directions for that "you rolled N!" moment over a representative
pale-day-sky tile, then tiles them into one labelled comparison sheet.

Some variants are deliberately built on the hero clown's "Plum & Lime" motif
(plum/lime/gold) per the brief; others explore other festive treatments.

Run (headless):
    python tools/render_dice_celebration.py
Writes docs/dice_results/round_1.png.
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
LIME = (132, 218, 116)
GOLD = (250, 205, 72)


def sky_tile(w, h):
    """A representative pale-day-sky background, slightly lighter toward the
    bottom — the popup sits high (cy~152) where the sky is still fairly bright,
    so we sample a mid-band of the full-screen gradient rather than the top."""
    s = pygame.Surface((w, h))
    for y in range(h):
        # Sample the lower-middle of the day gradient (where the popup lives).
        t = 0.35 + 0.45 * (y / max(1, h - 1))
        col = tuple(int(SKY_TOP[i] + (SKY_BOT[i] - SKY_TOP[i]) * t) for i in range(3))
        pygame.draw.line(s, col, (0, y), (w, y))
    return s


def _num_block(canvas, c, ncy, roll, num_col, edge_col, ss, size=70,
               shadow_a=95, edge_w=3):
    """The hero number — vendored bold font with drop shadow + thick edge ring,
    the shared treatment that keeps the rolled N reading as the dominant element
    rather than a plain score."""
    nf = hud._font(int(size * ss), True)
    num = nf.render(str(roll), True, num_col)
    edge = nf.render(str(roll), True, edge_col)
    shadow = nf.render(str(roll), True, (0, 0, 0))
    shadow.set_alpha(shadow_a)
    canvas.blit(shadow, shadow.get_rect(center=(c + 3 * ss, ncy + 5 * ss)))
    o = edge_w * ss
    for ox, oy in ((-o, 0), (o, 0), (0, -o), (0, o),
                   (-o, -o), (o, -o), (-o, o), (o, o)):
        canvas.blit(edge, edge.get_rect(center=(c + ox, ncy + oy)))
    nb = num.get_rect(center=(c, ncy))
    canvas.blit(num, nb)
    return nb


def _label(canvas, c, lcy, txt, label_col, edge_col, ss, size=26, track=True):
    lf = hud._font(int(size * ss), True)
    spaced = " ".join(txt) if track else txt
    lab = lf.render(spaced, True, label_col)
    labedge = lf.render(spaced, True, edge_col)
    for ox, oy in ((-SS, 0), (SS, 0), (0, -SS), (0, SS)) if (SS := ss) else ():
        canvas.blit(labedge, labedge.get_rect(center=(c + ox, lcy + oy)))
    canvas.blit(lab, lab.get_rect(center=(c, lcy)))


# ── Variant 1: Plum & Lime sunburst rosette ───────────────────────────────────
def var_rosette_clown(roll, ss):
    """Clown-coloured restyle of the current sunburst rosette: plum/lime wedges,
    gold hub, gold number, gold confetti — same proven structure, clown motif."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)
    rose = [PLUM, LIME]
    rays = 24
    step = math.tau / rays
    Rr = int(HD * 0.30)
    for i in range(rays):
        a0 = 0.35 + i * step
        a1 = a0 + step * 0.9
        am = (a0 + a1) * 0.5
        col = rose[i % 2] + (88,)
        pygame.draw.polygon(canvas, col, [
            (c, c),
            (c + math.cos(a0) * Rr, c + math.sin(a0) * Rr),
            (c + math.cos(am) * Rr * 1.05, c + math.sin(am) * Rr * 1.05),
            (c + math.cos(a1) * Rr, c + math.sin(a1) * Rr)])
    hub = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(hub, GOLD + (70,), (c, c), int(HD * 0.185))
    pygame.draw.circle(hub, PLUM + (120,), (c, c), int(HD * 0.185), 4 * ss)
    canvas.blit(hub, (0, 0))
    conf = [GOLD, LIME, (255, 255, 255), PLUM]
    for i in range(18):
        a = (i / 18) * math.tau
        dist = HD * 0.30 + (i % 3) * 9 * ss
        px = c + math.cos(a) * dist
        py = c + math.sin(a) * dist * 0.86
        sz = (5 + (i % 3) * 2) * ss
        d = pygame.Surface((sz, sz), pygame.SRCALPHA)
        pygame.draw.polygon(d, conf[i % 4] + (230,),
                            [(sz // 2, 0), (sz, sz // 2), (sz // 2, sz), (0, sz // 2)])
        d = pygame.transform.rotate(d, (i * 53) % 360)
        canvas.blit(d, (int(px - d.get_width() / 2), int(py - d.get_height() / 2)))
    nb = _num_block(canvas, c, c - int(8 * ss), roll, GOLD, PLUM, ss)
    _label(canvas, c, nb.bottom + int(16 * ss), "PAGODAS", LIME, PLUM, ss)
    return canvas, D


# ── Variant 2: Plum & Lime ribbon banner placard ──────────────────────────────
def var_ribbon_banner(roll, ss):
    """A festive carnival banner: a lime placard with notched ribbon tails and a
    plum rolled-edge frame, gold star toppers. No wheel — the placard itself is
    the festive object, with the number filling its centre. Clown-coloured."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    bw, bh = int(HD * 0.72), int(HD * 0.46)
    bx, by = c - bw // 2, c - bh // 2

    # Ribbon tails flaring left/right behind the placard (plum, with a notch).
    tail_w = int(HD * 0.20)
    for sgn in (-1, 1):
        x0 = c + sgn * (bw // 2 - 4 * ss)
        pts = [
            (x0, by + int(bh * 0.16)),
            (x0 + sgn * tail_w, by + int(bh * 0.04)),
            (x0 + sgn * tail_w * 0.7, by + bh // 2),
            (x0 + sgn * tail_w, by + int(bh * 0.96)),
            (x0, by + int(bh * 0.84)),
        ]
        pygame.draw.polygon(canvas, (66, 28, 110), pts)          # shaded back tail
    # Placard body — lime, rolled plum frame, soft gold inner line.
    rad = int(18 * ss)
    pygame.draw.rect(canvas, PLUM, (bx - 6 * ss, by - 6 * ss, bw + 12 * ss, bh + 12 * ss),
                     border_radius=rad + 6 * ss)
    pygame.draw.rect(canvas, LIME, (bx, by, bw, bh), border_radius=rad)
    pygame.draw.rect(canvas, GOLD, (bx + 6 * ss, by + 6 * ss, bw - 12 * ss, bh - 12 * ss),
                     width=2 * ss, border_radius=rad - 4 * ss)
    # Top highlight band on the lime for a glossy festive sheen.
    gloss = pygame.Surface((bw - 12 * ss, bh // 3), pygame.SRCALPHA)
    gloss.fill((255, 255, 255, 46))
    canvas.blit(gloss, (bx + 6 * ss, by + 6 * ss))
    # Gold star toppers riding the frame's top corners.
    for sx in (bx + int(bw * 0.16), bx + int(bw * 0.84)):
        _star(canvas, sx, by - 2 * ss, 11 * ss, GOLD, PLUM, ss)

    nb = _num_block(canvas, c, c - int(6 * ss), roll, (255, 255, 255), PLUM, ss, size=66)
    _label(canvas, c, by + bh + int(20 * ss), "PAGODAS", GOLD, PLUM, ss)
    return canvas, D


def _star(canvas, cx, cy, r, fill, edge, ss, points=5):
    pts = []
    for i in range(points * 2):
        rr = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / points
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(canvas, edge, pts)
    inner = [(cx + (px - cx) * 0.82, cy + (py - cy) * 0.82) for px, py in pts]
    pygame.draw.polygon(canvas, fill, inner)


# ── Variant 3: Gold medallion plaque (warm/neutral festive) ───────────────────
def var_medallion(roll, ss):
    """A struck gold medallion on a deep-plum field with a fluted bezel and a
    laurel sweep — a "prize" framing. Clown-adjacent (plum field, gold coin) but
    leans neutral-festive. The number is stamped into the coin face."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    # Soft plum backing glow disc.
    disc = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(disc, PLUM + (60,), (c, c), int(HD * 0.40))
    canvas.blit(disc, (0, 0))

    R = int(HD * 0.30)
    # Fluted bezel — alternating gold notches around the rim.
    for i in range(40):
        a = i * math.tau / 40
        rr = R + (6 * ss if i % 2 == 0 else 2 * ss)
        pygame.draw.line(canvas, (200, 150, 30),
                         (c + math.cos(a) * (R - 2 * ss), c + math.sin(a) * (R - 2 * ss)),
                         (c + math.cos(a) * rr, c + math.sin(a) * rr), 3 * ss)
    # Coin body — radial-ish gold with a darker rim ring and inner bright field.
    pygame.draw.circle(canvas, (180, 132, 28), (c, c), R)
    pygame.draw.circle(canvas, GOLD, (c, c), R - 5 * ss)
    pygame.draw.circle(canvas, (255, 232, 150), (c, c), R - 5 * ss, 3 * ss)
    # Top-left specular highlight crescent, clipped to the coin face so the
    # glossy sheen stays inside the bezel (the mask multiply trims the disc).
    hl = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(hl, (255, 255, 255, 90), (c - int(R * 0.32), c - int(R * 0.32)),
                       int(R * 0.55))
    mask = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (c, c), R - 8 * ss)
    hl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    canvas.blit(hl, (0, 0))
    # Laurel sweeps along the lower coin edge (lime leaves).
    for sgn in (-1, 1):
        for k in range(6):
            a = math.pi * 0.5 + sgn * (0.30 + k * 0.13)
            lx = c + math.cos(a) * (R - 14 * ss)
            ly = c + math.sin(a) * (R - 14 * ss)
            leaf = pygame.Surface((14 * ss, 8 * ss), pygame.SRCALPHA)
            pygame.draw.ellipse(leaf, LIME, leaf.get_rect())
            leaf = pygame.transform.rotate(leaf, -math.degrees(a) + 90 * sgn)
            canvas.blit(leaf, leaf.get_rect(center=(lx, ly)))

    nb = _num_block(canvas, c, c - int(8 * ss), roll, PLUM, (255, 240, 190), ss,
                    size=72, edge_w=2)
    _label(canvas, c, nb.bottom + int(14 * ss), "PAGODAS", (120, 60, 20), GOLD, ss)
    return canvas, D


# ── Variant 4: Pure confetti burst — no wheel (warm baseline) ──────────────────
def var_confetti_burst(roll, ss):
    """No rosette, no frame: just a dense radial confetti explosion (streamers +
    diamonds + dots) framing a free-floating number. Keeps the existing warm
    orange→pink/gold confetti direction as a baseline reference point."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    pal = [(255, 208, 88), (255, 118, 150), (118, 200, 255),
           (172, 255, 150), (255, 168, 70)]
    # Streamer curls — short bezier-ish arcs of colour radiating out.
    for i in range(14):
        a = i * math.tau / 14 + 0.2
        r0 = HD * 0.16
        r1 = HD * 0.40 + (i % 3) * 8 * ss
        col = pal[i % len(pal)]
        pts = []
        for t in range(7):
            tt = t / 6
            r = r0 + (r1 - r0) * tt
            aa = a + math.sin(tt * 3.0 + i) * 0.18
            pts.append((c + math.cos(aa) * r, c + math.sin(aa) * r * 0.9))
        pygame.draw.lines(canvas, col, False, pts, 4 * ss)
    # Diamonds + dots scattered along the burst front.
    for i in range(26):
        a = i * math.tau / 26 + 0.5
        dist = HD * 0.22 + (i * 37 % 110) / 110 * HD * 0.22
        px = c + math.cos(a) * dist
        py = c + math.sin(a) * dist * 0.9
        col = pal[i % len(pal)]
        if i % 2 == 0:
            sz = (5 + i % 3 * 2) * ss
            d = pygame.Surface((sz, sz), pygame.SRCALPHA)
            pygame.draw.polygon(d, col, [(sz // 2, 0), (sz, sz // 2),
                                         (sz // 2, sz), (0, sz // 2)])
            d = pygame.transform.rotate(d, (i * 47) % 360)
            canvas.blit(d, d.get_rect(center=(int(px), int(py))))
        else:
            pygame.draw.circle(canvas, col, (int(px), int(py)), 3 * ss + i % 2 * ss)
    nb = _num_block(canvas, c, c - int(6 * ss), roll, (255, 224, 118), (122, 62, 14),
                    ss, size=78)
    _label(canvas, c, nb.bottom + int(16 * ss), "PILLARS", (255, 240, 196),
           (122, 62, 14), ss)
    return canvas, D


# ── Variant 5: Clown-coloured GHOST starburst plaque ──────────────────────────
def var_ghost_clown(roll, ss):
    """The GHOST outcome rendered in a haunted twist of the clown motif: a plum
    night field with lime-edged ectoplasm wisps, a jagged lime/gold starburst,
    and a glowing little ghost mascot beside the number. Shows how GHOST reads
    while still belonging to the clown's family."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    # Jagged spiky starburst (alternating long/short points) in lime over plum.
    pts = []
    spikes = 16
    for i in range(spikes * 2):
        rr = HD * 0.34 if i % 2 == 0 else HD * 0.20
        a = i * math.pi / spikes
        pts.append((c + math.cos(a) * rr, c + math.sin(a) * rr))
    pygame.draw.polygon(canvas, PLUM + (150,), pts)
    pygame.draw.polygon(canvas, GOLD + (150,), pts, 3 * ss)   # gold-rimmed spikes
    inner = [(c + (px - c) * 0.80, c + (py - c) * 0.80) for px, py in pts]
    pygame.draw.polygon(canvas, LIME + (110,), inner)
    pygame.draw.circle(canvas, (40, 18, 70, 180), (c, c), int(HD * 0.20))

    # Rising ectoplasm wisps (lime-tinted), each a vertical column of fading
    # blobs so they read as steam curling up rather than scattered dots.
    for i in range(7):
        wx = int(c - 66 * ss + i * 22 * ss)
        sway = int(math.sin(i * 1.3) * 6 * ss)
        for k in range(3):
            wy = int(c + 40 * ss - k * 18 * ss)
            al = max(0, 150 - k * 45 - (i % 2) * 20)
            pygame.draw.circle(canvas, (180, 255, 200, al),
                               (wx + sway + (k % 2) * 3 * ss, wy), (6 - k) * ss)

    # Little ghost mascot up-right, gold eyes — the friendly spook.
    gx, gy = c + int(HD * 0.20), c - int(HD * 0.22)
    gr = int(HD * 0.085)
    ghost = pygame.Surface((gr * 3, gr * 4), pygame.SRCALPHA)
    gw, gh = gr * 3, gr * 4
    pygame.draw.circle(ghost, (236, 255, 240, 235), (gw // 2, gr), gr)
    pygame.draw.rect(ghost, (236, 255, 240, 235), (gw // 2 - gr, gr, gr * 2, gr * 1.6))
    for k in range(4):  # scalloped hem
        pygame.draw.circle(ghost, (236, 255, 240, 235),
                           (gw // 2 - gr + int(gr * (0.4 + k * 0.55)), int(gr * 2.6)),
                           int(gr * 0.34))
    pygame.draw.circle(ghost, PLUM, (gw // 2 - gr // 2, gr), gr // 4)
    pygame.draw.circle(ghost, PLUM, (gw // 2 + gr // 2, gr), gr // 4)
    canvas.blit(ghost, ghost.get_rect(center=(gx, gy)))

    nb = _num_block(canvas, c, c - int(6 * ss), roll, (236, 255, 240), PLUM, ss, size=72)
    _label(canvas, c, nb.bottom + int(16 * ss), "GHOST!", LIME, PLUM, ss)
    return canvas, D


VARIANTS = [
    ("1  Clown Rosette", "plum/lime sunburst + gold hub", var_rosette_clown, 17, True),
    ("2  Ribbon Banner", "lime placard + plum frame + gold stars", var_ribbon_banner, 22, True),
    ("3  Gold Medallion", "struck coin on plum + lime laurel", var_medallion, 14, True),
    ("4  Confetti Burst", "warm streamer explosion, no wheel", var_confetti_burst, 19, False),
    ("5  Ghost Starburst", "haunted plum/lime spike + mascot", var_ghost_clown, 10, True),
]


def main():
    SS = 3
    tile_w, tile_h = 320, 360
    cols, rows = 3, 2
    pad = 16
    head = 56
    sheet_w = cols * tile_w + (cols + 1) * pad
    sheet_h = head + rows * tile_h + (rows + 1) * pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 34, 42))

    title_f = hud._font(30, True)
    sub_f = hud._font(16, True)
    sheet.blit(title_f.render("Dice-Results Celebration — Round 1 (5 variants)",
                              True, (255, 255, 255)), (pad, 12))
    sheet.blit(sub_f.render("Clown 'Plum & Lime' variants: 1, 2, 3, 5  |  baseline warm: 4",
                            True, (200, 205, 215)), (pad, 38))

    label_f = hud._font(20, True)
    samp_f = hud._font(14, True)

    for idx, (name, desc, fn, roll, clown) in enumerate(VARIANTS):
        col = idx % cols
        row = idx // cols
        tx = pad + col * (tile_w + pad)
        ty = head + pad + row * (tile_h + pad)

        tile = sky_tile(tile_w, tile_h)
        # Faint plum tag on clown variants so the motif grouping reads.
        tag = (LIME if clown else (255, 208, 88))

        canvas, D = fn(roll, SS)
        # Display the popup near its true on-screen scale (264 design px), but
        # fit within the tile with a little headroom for labels.
        disp = min(tile_w - 24, 264)
        out = pygame.transform.smoothscale(canvas, (disp, disp))
        tile.blit(out, out.get_rect(center=(tile_w // 2, tile_h // 2 - 6)))

        # Header strip + footer caption on the tile.
        strip = pygame.Surface((tile_w, 30), pygame.SRCALPHA)
        strip.fill((20, 22, 28, 200))
        tile.blit(strip, (0, 0))
        tile.blit(label_f.render(name, True, tag), (8, 5))
        cap = pygame.Surface((tile_w, 24), pygame.SRCALPHA)
        cap.fill((20, 22, 28, 200))
        tile.blit(cap, (0, tile_h - 24))
        tile.blit(samp_f.render(f"{desc}  (roll {roll})", True, (220, 225, 235)),
                  (8, tile_h - 22))
        sheet.blit(tile, (tx, ty))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "dice_results")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
