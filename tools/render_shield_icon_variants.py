"""Design round for the KNIGHT 'survive one hit' powerup PICKUP ICON — a
medieval shield. Renders 5 distinctive variants (different SHAPE + heraldry)
as a labeled comparison sheet, each shown large (to judge detail) with a
true-pickup-size inset (the real readability test).

EXPLORATION ONLY — imports only the read-only POWERUP_R; touches no gameplay.
Output: docs/screenshots/shield_icon_variants/

Run:  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_shield_icon_variants
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import POWERUP_R

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "shield_icon_variants")
os.makedirs(OUT_DIR, exist_ok=True)

NATIVE = 72
SHOWCASE = 200
INSET = 2 * POWERUP_R + 6        # ≈ true pickup size

# ── palette: steel + heraldic tinctures ─────────────────────────────────────
OL = (24, 28, 38); STD = (70, 78, 96); STM = (150, 160, 182); STH = (238, 244, 255)
BRASS = (208, 174, 98); BRASS_HI = (255, 232, 168)
OR = (226, 182, 72); OR_HI = (255, 224, 150)            # gold
ARG = (238, 232, 216)                                   # argent / cream
GULES = (170, 46, 50); GULES_HI = (208, 74, 78)         # red
AZURE = (46, 80, 152); AZURE_HI = (90, 132, 212)        # blue
VERT = (42, 122, 68)                                    # green
SABLE = (34, 36, 46)                                    # black
WOOD = (122, 88, 54); WOOD_HI = (152, 114, 74)


# ── helpers ──────────────────────────────────────────────────────────────────
def _ss(w, h, fn, scale=6):
    big = pygame.Surface((int(w * scale), int(h * scale)), pygame.SRCALPHA)
    fn(big, scale)
    return pygame.transform.smoothscale(big, (int(w), int(h)))


def _inset(points, k):
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    out = []
    for x, y in points:
        dx, dy = cx - x, cy - y
        d = math.hypot(dx, dy) or 1.0
        out.append((x + dx / d * k, y + dy / d * k))
    return out


def _qbez(p0, p1, p2, n=18):
    return [(((1 - t) ** 2) * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             ((1 - t) ** 2) * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (i / n for i in range(n + 1))]


def _mullet(big, cx, cy, r, col, s, edge=(150, 110, 40)):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    pygame.draw.polygon(big, col, pts)
    if edge:
        pygame.draw.polygon(big, edge, pts, max(1, int(s)))


def _rivet(big, x, y, s):
    pygame.draw.circle(big, STD, (int(x), int(y)), max(1, int(2.2 * s)))
    pygame.draw.circle(big, BRASS, (int(x), int(y)), max(1, int(1.4 * s)))
    pygame.draw.circle(big, BRASS_HI, (int(x - 0.6 * s), int(y - 0.6 * s)), max(1, int(0.6 * s)))


def _clip_circle(big, cx, cy, R):
    """Return a fresh SRCALPHA surface masked to a circle for plank/quarter fills."""
    w, h = big.get_size()
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (int(cx), int(cy)), int(R))
    return mask


def _fleur(big, cx, cy, w, h, col, s):
    band_y = cy + h * 0.12
    # central petal — tall leaf with a round bulb
    pygame.draw.polygon(big, col, [(cx, cy - h * 0.5), (cx + w * 0.17, cy - h * 0.08),
                                   (cx + w * 0.1, band_y), (cx - w * 0.1, band_y), (cx - w * 0.17, cy - h * 0.08)])
    pygame.draw.circle(big, col, (int(cx), int(cy - h * 0.1)), int(w * 0.17))
    # two side arms curling up-and-out (thick curves + rounded tips)
    for sgn in (-1, 1):
        arm = _qbez((cx, band_y - h * 0.02), (cx + sgn * w * 0.58, cy - h * 0.18), (cx + sgn * w * 0.4, cy - h * 0.5), 14)
        pygame.draw.lines(big, col, False, arm, max(2, int(3.4 * s)))
        pygame.draw.circle(big, col, (int(arm[-1][0]), int(arm[-1][1])), int(w * 0.11))
    # horizontal tie band + tapered foot
    pygame.draw.rect(big, col, (int(cx - w * 0.42), int(band_y), int(w * 0.84), int(h * 0.1)))
    pygame.draw.polygon(big, col, [(cx - w * 0.13, band_y + h * 0.1), (cx + w * 0.13, band_y + h * 0.1), (cx, cy + h * 0.46)])


# ── the 5 shield variants (paint on supersampled `big`) ──────────────────────
def draw_crusader_heater(big, s):
    w, h = big.get_size(); cx = w / 2; pad = 3 * s
    outer = [(pad, pad), (w - pad, pad), (w - pad, h * 0.46), (cx, h - pad), (pad, h * 0.46)]
    pygame.draw.polygon(big, OL, outer)
    pygame.draw.polygon(big, STM, _inset(outer, 1.7 * s))
    field = _inset(outer, 4.6 * s)
    pygame.draw.polygon(big, GULES, field)
    pygame.draw.polygon(big, GULES_HI, [field[0], field[1], (cx, h * 0.5)])
    vb = 6 * s
    pygame.draw.rect(big, ARG, (cx - vb / 2, h * 0.16, vb, h * 0.54))
    pygame.draw.rect(big, ARG, (w * 0.17, h * 0.34, w * 0.66, vb))
    for rx, ry in ((0.21, 0.16), (0.79, 0.16), (0.18, 0.45), (0.82, 0.45)):
        _rivet(big, w * rx, h * ry, s)
    pygame.draw.line(big, STH, (pad + 3 * s, pad + 3 * s), (cx, pad + 3 * s), max(1, int(1.4 * s)))


def draw_norman_kite(big, s):
    w, h = big.get_size(); cx = w / 2; pad = 3 * s
    top = _qbez((pad, h * 0.18), (cx, -h * 0.02), (w - pad, h * 0.18), 16)
    outer = top + [(w * 0.86, h * 0.55), (cx, h - pad), (w * 0.14, h * 0.55)]
    pygame.draw.polygon(big, OL, outer)
    pygame.draw.polygon(big, STM, _inset(outer, 1.7 * s))
    field = _inset(outer, 4.6 * s)
    pygame.draw.polygon(big, AZURE, field)
    pygame.draw.polygon(big, AZURE_HI, [top[2], top[len(top) // 2], (cx, h * 0.4)])
    # gold bend UL->LR
    p1, p2 = (w * 0.30, h * 0.18), (w * 0.72, h * 0.64)
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]; dl = math.hypot(dx, dy); ux, uy = dx / dl, dy / dl; px, py = -uy, ux
    bw = 7 * s
    band = [(p1[0] + px * bw, p1[1] + py * bw), (p2[0] + px * bw, p2[1] + py * bw),
            (p2[0] - px * bw, p2[1] - py * bw), (p1[0] - px * bw, p1[1] - py * bw)]
    pygame.draw.polygon(big, OR, band)
    pygame.draw.polygon(big, OR_HI, [(p1[0] + px * bw, p1[1] + py * bw), (p2[0] + px * bw, p2[1] + py * bw),
                                     (p2[0] + px * bw * 0.35, p2[1] + py * bw * 0.35), (p1[0] + px * bw * 0.35, p1[1] + py * bw * 0.35)])
    for t in (0.24, 0.5, 0.76):
        _mullet(big, p1[0] + dx * t, p1[1] + dy * t, 4.2 * s, GULES, s, edge=(120, 30, 34))
    pygame.draw.line(big, STH, (top[2][0], top[2][1] + 2 * s), (top[len(top) // 2][0], top[len(top) // 2][1] + 1 * s), max(1, int(1.2 * s)))


def draw_round_targe(big, s):
    w, h = big.get_size(); cx, cy = w / 2, h / 2; R = min(w, h) / 2 - 2 * s
    pygame.draw.circle(big, OL, (int(cx), int(cy)), int(R + 1.7 * s))
    tmp = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.circle(tmp, WOOD, (int(cx), int(cy)), int(R))
    for i in range(-3, 4):
        x = cx + i * R * 0.3
        pygame.draw.line(tmp, WOOD_HI, (x, cy - R), (x, cy + R), max(1, int(1.4 * s)))
    tmp.blit(_clip_circle(big, cx, cy, R), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(tmp, (0, 0))
    pygame.draw.circle(big, STM, (int(cx), int(cy)), int(R), max(2, int(2.6 * s)))
    off = R * 0.62
    for col, wd in ((ARG, 6 * s), (VERT, 3.2 * s)):
        pygame.draw.line(big, col, (cx - off, cy - off), (cx + off, cy + off), max(2, int(wd)))
        pygame.draw.line(big, col, (cx - off, cy + off), (cx + off, cy - off), max(2, int(wd)))
    pygame.draw.circle(big, STD, (int(cx), int(cy)), int(R * 0.24))
    pygame.draw.circle(big, STM, (int(cx), int(cy)), int(R * 0.17))
    pygame.draw.circle(big, STH, (int(cx - 1.6 * s), int(cy - 1.6 * s)), int(R * 0.07))
    for ang in range(0, 360, 45):
        _rivet(big, cx + math.cos(math.radians(ang)) * R * 0.82, cy + math.sin(math.radians(ang)) * R * 0.82, s * 0.8)


def draw_pavise(big, s):
    w, h = big.get_size(); cx = w / 2; pad = 3 * s
    bw = w * 0.66; x0 = cx - bw / 2
    rect = pygame.Rect(int(x0), int(pad), int(bw), int(h - 2 * pad))
    pygame.draw.rect(big, OL, rect, border_radius=int(7 * s))
    pygame.draw.rect(big, STM, rect.inflate(int(-3 * s), int(-3 * s)), border_radius=int(6 * s))
    field = rect.inflate(int(-7 * s), int(-7 * s))
    pygame.draw.rect(big, SABLE, field, border_radius=int(5 * s))
    pale_w = 13 * s
    pygame.draw.rect(big, OR, (int(cx - pale_w / 2), field.top + int(2 * s), int(pale_w), field.height - int(4 * s)))
    pygame.draw.rect(big, OR_HI, (int(cx - pale_w / 2), field.top + int(2 * s), int(pale_w * 0.3), field.height - int(4 * s)))
    _fleur(big, cx, h * 0.5, pale_w * 1.4, h * 0.42, SABLE, s)
    for ry in range(5):
        y = field.top + field.height * (0.12 + ry * 0.19)
        _rivet(big, x0 + 4 * s, y, s * 0.8); _rivet(big, x0 + bw - 4 * s, y, s * 0.8)


def draw_round_buckler(big, s):
    w, h = big.get_size(); cx, cy = w / 2, h / 2; R = min(w, h) / 2 - 3 * s
    pygame.draw.circle(big, OL, (int(cx), int(cy)), int(R + 1.7 * s))
    tmp = pygame.Surface((w, h), pygame.SRCALPHA)
    for a0, a1, col in ((180, 270, GULES), (270, 360, OR), (0, 90, GULES), (90, 180, OR)):
        pts = [(cx, cy)] + [(cx + math.cos(math.radians(a)) * R, cy + math.sin(math.radians(a)) * R)
                            for a in range(a0, a1 + 1, 5)]
        pygame.draw.polygon(tmp, col, pts)
    tmp.blit(_clip_circle(big, cx, cy, R), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(tmp, (0, 0))
    pygame.draw.circle(big, STM, (int(cx), int(cy)), int(R), max(2, int(2.6 * s)))
    for ang in range(0, 360, 30):
        pygame.draw.circle(big, BRASS, (int(cx + math.cos(math.radians(ang)) * R * 0.9),
                                        int(cy + math.sin(math.radians(ang)) * R * 0.9)), max(1, int(1.3 * s)))
    pygame.draw.circle(big, STD, (int(cx), int(cy)), int(R * 0.3))
    pygame.draw.circle(big, STM, (int(cx), int(cy)), int(R * 0.22))
    spike = [(cx - 3 * s, cy - 2 * s), (cx + 3 * s, cy - 2 * s), (cx, cy - R * 0.5)]
    pygame.draw.polygon(big, STH, spike)
    pygame.draw.polygon(big, OL, spike, max(1, int(s)))
    pygame.draw.circle(big, STH, (int(cx - 1.6 * s), int(cy - 1.6 * s)), int(R * 0.08))


VARIANTS = [
    ("V1_crusader_heater", draw_crusader_heater, "V1  Heater", "gules · argent cross"),
    ("V2_norman_kite", draw_norman_kite, "V2  Norman kite", "azure · gold bend + mullets"),
    ("V3_round_targe", draw_round_targe, "V3  Round targe", "wood · boss · saltire"),
    ("V4_pavise", draw_pavise, "V4  Pavise", "sable · gold pale + fleur"),
    ("V5_round_buckler", draw_round_buckler, "V5  Buckler", "quartered · spiked boss"),
]


def _tile(fn, label, caption):
    pad = 14
    tw, th = SHOWCASE + pad * 2, SHOWCASE + pad * 2 + 46
    t = pygame.Surface((tw, th), pygame.SRCALPHA)
    pygame.draw.rect(t, (20, 22, 32), (0, 0, tw, th), border_radius=12)
    pygame.draw.rect(t, (60, 66, 86), (0, 0, tw, th), 2, border_radius=12)
    show = pygame.transform.smoothscale(_ss(NATIVE, NATIVE, fn, 6), (SHOWCASE, SHOWCASE))
    t.blit(show, (pad, pad))
    # true pickup-size inset, framed, top-right
    ins = _ss(INSET, INSET, fn, 6)
    fx, fy = tw - pad - INSET - 4, pad + 2
    pygame.draw.rect(t, (12, 13, 18), (fx - 3, fy - 3, INSET + 6, INSET + 6), border_radius=4)
    pygame.draw.rect(t, (90, 96, 120), (fx - 3, fy - 3, INSET + 6, INSET + 6), 1, border_radius=4)
    t.blit(ins, (fx, fy))
    f1 = pygame.font.SysFont("Arial", 18, bold=True)
    f2 = pygame.font.SysFont("Arial", 13)
    t.blit(f1.render(label, True, (255, 232, 168)), (pad, SHOWCASE + pad + 6))
    t.blit(f2.render(caption, True, (220, 224, 235)), (pad, SHOWCASE + pad + 28))
    return t


def main():
    tiles = [_tile(fn, lab, cap) for _, fn, lab, cap in VARIANTS]
    # per-variant PNGs (showcase + inset tile)
    for (key, fn, lab, cap), tile in zip(VARIANTS, tiles):
        pygame.image.save(tile, os.path.join(OUT_DIR, f"{key}.png"))
    # comparison sheet: 5 tiles in a row + title
    gap = 12
    tw, th = tiles[0].get_size()
    title_h = 40
    sheet = pygame.Surface((tw * len(tiles) + gap * (len(tiles) + 1), th + title_h + gap), pygame.SRCALPHA)
    sheet.fill((14, 15, 22))
    tf = pygame.font.SysFont("Arial", 22, bold=True)
    sheet.blit(tf.render("Knight powerup — shield pickup-icon options (inset = true size)", True, (255, 232, 168)), (gap + 2, 8))
    for i, tile in enumerate(tiles):
        sheet.blit(tile, (gap + i * (tw + gap), title_h))
    out = os.path.join(OUT_DIR, "shield_icons.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print("per-variant PNGs in", OUT_DIR)


if __name__ == "__main__":
    main()
