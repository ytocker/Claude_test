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


# ── 5 MORE from other sources (ancient / cultural / fantasy) ─────────────────
BRZ = (196, 150, 70); BRZ_HI = (246, 212, 132); BRZ_D = (120, 86, 34)
SIL = (224, 230, 244); SIL_D = (168, 178, 200)


def draw_greek_hoplon(big, s):
    w, h = big.get_size(); cx, cy = w / 2, h / 2; R = min(w, h) / 2 - 2 * s
    pygame.draw.circle(big, OL, (int(cx), int(cy)), int(R + 1.7 * s))
    pygame.draw.circle(big, BRZ_D, (int(cx), int(cy)), int(R))
    pygame.draw.circle(big, BRZ, (int(cx), int(cy)), int(R * 0.9))
    pygame.draw.circle(big, BRZ_D, (int(cx), int(cy)), int(R), max(2, int(2.6 * s)))
    pygame.draw.circle(big, BRZ_HI, (int(cx), int(cy)), int(R * 0.9), max(1, int(1.2 * s)))
    pygame.draw.circle(big, BRZ_D, (int(cx), int(cy)), int(R * 0.72), max(1, int(1.4 * s)))
    apex = (cx, cy - R * 0.52)                              # Spartan lambda Λ
    pygame.draw.line(big, OL, apex, (cx - R * 0.44, cy + R * 0.5), max(3, int(5.5 * s)))
    pygame.draw.line(big, OL, apex, (cx + R * 0.44, cy + R * 0.5), max(3, int(5.5 * s)))
    pygame.draw.circle(big, BRZ_HI, (int(cx - R * 0.34), int(cy - R * 0.34)), int(R * 0.12))


def draw_roman_scutum(big, s):
    w, h = big.get_size(); cx = w / 2; pad = 3 * s
    GLD = (226, 182, 72); GLD_HI = (255, 224, 150)
    bw = w * 0.6; x0 = cx - bw / 2
    rect = pygame.Rect(int(x0), int(pad), int(bw), int(h - 2 * pad))
    pygame.draw.rect(big, OL, rect, border_radius=int(11 * s))
    inner = rect.inflate(int(-3 * s), int(-3 * s))
    pygame.draw.rect(big, GULES, inner, border_radius=int(10 * s))
    pygame.draw.rect(big, GULES_HI, (int(cx - bw * 0.13), inner.top, int(bw * 0.26), inner.height))  # barrel sheen
    for sx in (inner.left, inner.right - int(bw * 0.13)):
        pygame.draw.rect(big, (128, 32, 36), (sx, inner.top, int(bw * 0.13), inner.height))
    wy = h * 0.42                                          # gold eagle wings
    for sgn in (-1, 1):
        pygame.draw.polygon(big, GLD, [(cx, wy - 4 * s), (cx + sgn * bw * 0.42, wy - 11 * s),
                                       (cx + sgn * bw * 0.48, wy), (cx + sgn * bw * 0.42, wy + 11 * s), (cx, wy + 4 * s)])
        for k in range(3):
            fx = cx + sgn * bw * (0.16 + k * 0.11)
            pygame.draw.line(big, (160, 120, 40), (fx, wy - 7 * s), (fx, wy + 7 * s), max(1, int(s)))
    pygame.draw.polygon(big, GLD_HI, [(cx - 3 * s, h * 0.18), (cx + 4 * s, h * 0.3), (cx - 1 * s, h * 0.3),  # thunderbolt
                                      (cx + 3 * s, h * 0.5), (cx - 4 * s, h * 0.34), (cx + 1 * s, h * 0.34)])
    pygame.draw.circle(big, (94, 100, 118), (int(cx), int(h * 0.62)), int(6 * s))                  # umbo boss
    pygame.draw.circle(big, STH, (int(cx - 1.6 * s), int(h * 0.62 - 1.6 * s)), int(2.4 * s))
    for ry in (0.1, 0.9):
        for fx in (0.32, 0.68):
            _rivet(big, inner.left + bw * fx, h * ry, s * 0.8)


def draw_viking_round(big, s):
    w, h = big.get_size(); cx, cy = w / 2, h / 2; R = min(w, h) / 2 - 2 * s
    pygame.draw.circle(big, OL, (int(cx), int(cy)), int(R + 1.7 * s))
    tmp = pygame.Surface((w, h), pygame.SRCALPHA)
    cols = [(158, 42, 46), (232, 226, 210)]
    seg = 8
    for i in range(seg):
        a0, a1 = i * 360 / seg, (i + 1) * 360 / seg
        pts = [(cx, cy)] + [(cx + math.cos(math.radians(a)) * R, cy + math.sin(math.radians(a)) * R) for a in range(int(a0), int(a1) + 1, 4)]
        pygame.draw.polygon(tmp, cols[i % 2], pts)
    tmp.blit(_clip_circle(big, cx, cy, R), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(tmp, (0, 0))
    pygame.draw.circle(big, STM, (int(cx), int(cy)), int(R), max(2, int(2.6 * s)))
    for ang in range(0, 360, 30):
        pygame.draw.circle(big, STD, (int(cx + math.cos(math.radians(ang)) * R * 0.9), int(cy + math.sin(math.radians(ang)) * R * 0.9)), max(1, int(1.5 * s)))
    pygame.draw.circle(big, STD, (int(cx), int(cy)), int(R * 0.22))
    pygame.draw.circle(big, STM, (int(cx), int(cy)), int(R * 0.15))
    pygame.draw.circle(big, STH, (int(cx - 1.5 * s), int(cy - 1.5 * s)), int(R * 0.06))


def draw_heraldic_lion(big, s):
    w, h = big.get_size(); cx = w / 2; pad = 3 * s
    outer = ([(pad, pad), (w - pad, pad), (w - pad, h * 0.45)]
             + _qbez((w - pad, h * 0.45), (w - pad, h - pad), (cx, h - pad), 12)[1:]
             + _qbez((cx, h - pad), (pad, h - pad), (pad, h * 0.45), 12)[1:])
    pygame.draw.polygon(big, OL, outer)
    pygame.draw.polygon(big, STM, _inset(outer, 1.7 * s))
    field = _inset(outer, 4.6 * s)
    pygame.draw.polygon(big, GULES, field)
    pygame.draw.polygon(big, GULES_HI, [field[0], field[1], (cx, h * 0.5)])
    lx, ly, lr = cx, h * 0.46, w * 0.15                    # gold lion mask (sun-lion)
    for k in range(12):
        a = math.radians(k * 30)
        p = (lx + math.cos(a) * lr * 1.7, ly + math.sin(a) * lr * 1.7)
        b1 = (lx + math.cos(a - 0.22) * lr, ly + math.sin(a - 0.22) * lr)
        b2 = (lx + math.cos(a + 0.22) * lr, ly + math.sin(a + 0.22) * lr)
        pygame.draw.polygon(big, OR_HI if k % 2 else OR, [b1, p, b2])
    pygame.draw.circle(big, OR, (int(lx), int(ly)), int(lr))
    pygame.draw.circle(big, OR_HI, (int(lx - lr * 0.3), int(ly - lr * 0.3)), int(lr * 0.4))
    pygame.draw.circle(big, OL, (int(lx - lr * 0.38), int(ly - lr * 0.08)), max(1, int(1.8 * s)))
    pygame.draw.circle(big, OL, (int(lx + lr * 0.38), int(ly - lr * 0.08)), max(1, int(1.8 * s)))
    pygame.draw.polygon(big, OL, [(lx - lr * 0.2, ly + lr * 0.2), (lx + lr * 0.2, ly + lr * 0.2), (lx, ly + lr * 0.5)])
    for rx, ry in ((0.2, 0.14), (0.8, 0.14)):
        _rivet(big, w * rx, h * ry, s)


def draw_winged_crest(big, s):
    w, h = big.get_size(); cx = w / 2

    def wing(sgn):
        rootx, rooty = cx + sgn * w * 0.13, h * 0.46
        for k in range(4):
            t = k / 3
            ang = math.radians(196 - t * 62) if sgn < 0 else math.radians(-16 + t * 62)
            L = (34 - k * 5) * s
            tx, ty = rootx + math.cos(ang) * L, rooty + math.sin(ang) * L
            perp = ang + math.pi / 2; wd = 6.5 * s
            pygame.draw.polygon(big, SIL_D, [(rootx + math.cos(perp) * wd, rooty + math.sin(perp) * wd), (tx, ty), (rootx - math.cos(perp) * wd, rooty - math.sin(perp) * wd)])
            pygame.draw.circle(big, SIL, (int(tx), int(ty)), int(wd * 0.7))
    wing(-1); wing(1)
    pad = w * 0.28                                         # central azure heater
    outer = [(pad, h * 0.3), (w - pad, h * 0.3), (w - pad, h * 0.6), (cx, h * 0.86), (pad, h * 0.6)]
    pygame.draw.polygon(big, OL, outer)
    pygame.draw.polygon(big, STM, _inset(outer, 1.6 * s))
    pygame.draw.polygon(big, AZURE, _inset(outer, 4 * s))
    _mullet(big, cx, h * 0.52, 6 * s, OR, s, edge=(160, 120, 40))
    cw, cyc = w * 0.24, h * 0.24                           # crown on top
    pygame.draw.rect(big, OR, (int(cx - cw / 2), int(cyc), int(cw), int(h * 0.055)))
    for k in range(3):
        x = cx + (k - 1) * cw * 0.42
        pygame.draw.polygon(big, OR, [(x - 3 * s, cyc), (x + 3 * s, cyc), (x, cyc - h * 0.07)])
        pygame.draw.circle(big, GULES, (int(x), int(cyc - h * 0.055)), max(1, int(1.4 * s)))


# ── round 3: 10 AUTHENTIC-KNIGHT shields (heater / kite / bouché + heraldry) ──
def _clip_poly(big, points):
    w, h = big.get_size()
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), points)
    return mask


def _heater_pts(w, h, pad):
    return [(pad, pad), (w - pad, pad), (w - pad, h * 0.46), (w / 2, h - pad), (pad, h * 0.46)]


def _kite_pts(w, h, pad):
    top = _qbez((pad, h * 0.18), (w / 2, -h * 0.02), (w - pad, h * 0.18), 16)
    return top + [(w * 0.86, h * 0.55), (w / 2, h - pad), (w * 0.14, h * 0.55)]


def _bouche_pts(w, h, pad):
    # heater with a stepped notch at the top-right = the lance rest (bouché)
    return [(pad, pad), (w * 0.58, pad), (w * 0.58, h * 0.15), (w - pad, h * 0.15),
            (w - pad, h * 0.5), (w / 2, h - pad), (pad, h * 0.5)]


def _base(big, s, pts, field, field_hi=None):
    """Outline → steel rim → field; returns the field polygon (for clipping)."""
    pygame.draw.polygon(big, OL, pts)
    pygame.draw.polygon(big, STM, _inset(pts, 1.7 * s))
    fpts = _inset(pts, 4.6 * s)
    pygame.draw.polygon(big, field, fpts)
    if field_hi:
        pygame.draw.polygon(big, field_hi, [fpts[0], fpts[1], (big.get_width() / 2, big.get_height() * 0.5)])
    return fpts


def _ordinary(big, fpts, draw_fn):
    """Draw an ordinary/division via draw_fn onto a temp, clipped to the field."""
    w, h = big.get_size()
    tmp = pygame.Surface((w, h), pygame.SRCALPHA)
    draw_fn(tmp)
    tmp.blit(_clip_poly(big, fpts), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(tmp, (0, 0))


def _cross_pattee(big, cx, cy, R, col, s):
    for ang in (0, 90, 180, 270):
        a = math.radians(ang); perp = a + math.pi / 2
        tip = (cx + math.cos(a) * R, cy + math.sin(a) * R)
        nar, wide = R * 0.16, R * 0.5
        pygame.draw.polygon(big, col, [
            (cx + math.cos(perp) * nar, cy + math.sin(perp) * nar),
            (tip[0] + math.cos(perp) * wide, tip[1] + math.sin(perp) * wide),
            (tip[0] - math.cos(perp) * wide, tip[1] - math.sin(perp) * wide),
            (cx - math.cos(perp) * nar, cy - math.sin(perp) * nar)])


def _lion_rampant(big, cx, cy, w, h, col, s):
    # stylized rearing lion facing dexter (left)
    pygame.draw.ellipse(big, col, (int(cx + w * 0.0), int(cy + h * 0.04), int(w * 0.26), int(h * 0.34)))   # haunch
    pygame.draw.line(big, col, (cx + w * 0.14, cy + h * 0.3), (cx + w * 0.14, cy + h * 0.46), max(4, int(5 * s)))  # hind leg
    pygame.draw.circle(big, col, (int(cx + w * 0.14), int(cy + h * 0.47)), max(2, int(3 * s)))             # paw
    pygame.draw.polygon(big, col, [(cx + w * 0.12, cy + h * 0.16), (cx + w * 0.02, cy - h * 0.16),         # body rising
                                   (cx - w * 0.1, cy - h * 0.3), (cx - w * 0.04, cy - h * 0.02), (cx, cy + h * 0.18)])
    pygame.draw.line(big, col, (cx - w * 0.05, cy - h * 0.1), (cx - w * 0.27, cy - h * 0.16), max(3, int(4 * s)))   # upper foreleg
    pygame.draw.line(big, col, (cx - w * 0.03, cy - h * 0.02), (cx - w * 0.24, cy + h * 0.06), max(3, int(4 * s)))  # lower foreleg
    hx, hy, hr = cx - w * 0.14, cy - h * 0.34, h * 0.1                                                     # head facing left
    for adeg in (250, 292, 334, 16, 58):                                                                  # partial mane (top/back)
        a = math.radians(adeg)
        pygame.draw.polygon(big, col, [(hx + math.cos(a - 0.26) * hr, hy + math.sin(a - 0.26) * hr),
                                       (hx + math.cos(a) * hr * 1.8, hy + math.sin(a) * hr * 1.8),
                                       (hx + math.cos(a + 0.26) * hr, hy + math.sin(a + 0.26) * hr)])
    pygame.draw.circle(big, col, (int(hx), int(hy)), int(hr))
    pygame.draw.polygon(big, col, [(hx - hr * 1.4, hy - hr * 0.1), (hx - hr * 0.2, hy - hr * 0.3), (hx - hr * 0.2, hy + hr * 0.5)])  # snout
    pygame.draw.circle(big, OL, (int(hx - hr * 0.35), int(hy - hr * 0.05)), max(1, int(1.5 * s)))         # eye
    tail = _qbez((cx + w * 0.2, cy + h * 0.0), (cx + w * 0.5, cy - h * 0.24), (cx + w * 0.3, cy - h * 0.48), 12)
    pygame.draw.lines(big, col, False, tail, max(2, int(3.4 * s)))
    pygame.draw.circle(big, col, (int(tail[-1][0]), int(tail[-1][1])), max(2, int(3.2 * s)))              # tail tuft


def _eagle_displayed(big, cx, cy, w, h, col, s):
    pygame.draw.ellipse(big, col, (cx - w * 0.09, cy - h * 0.3, w * 0.18, h * 0.55))            # body
    pygame.draw.circle(big, col, (int(cx), int(cy - h * 0.34)), int(h * 0.08))                  # head
    pygame.draw.polygon(big, col, [(cx + h * 0.06, cy - h * 0.37), (cx + h * 0.17, cy - h * 0.34), (cx + h * 0.06, cy - h * 0.3)])  # beak
    for sgn in (-1, 1):
        pygame.draw.polygon(big, col, [(cx, cy - h * 0.22), (cx + sgn * w * 0.5, cy - h * 0.3),
                                       (cx + sgn * w * 0.46, cy - h * 0.12), (cx + sgn * w * 0.52, cy - h * 0.04),
                                       (cx + sgn * w * 0.4, cy + h * 0.05), (cx + sgn * w * 0.46, cy + h * 0.12),
                                       (cx + sgn * w * 0.28, cy + h * 0.1), (cx, cy - h * 0.02)])
        pygame.draw.line(big, col, (cx + sgn * w * 0.05, cy + h * 0.16), (cx + sgn * w * 0.1, cy + h * 0.3), max(2, int(2.6 * s)))
    pygame.draw.polygon(big, col, [(cx - w * 0.1, cy + h * 0.16), (cx + w * 0.1, cy + h * 0.16),
                                   (cx + w * 0.06, cy + h * 0.44), (cx - w * 0.06, cy + h * 0.44)])  # tail fan


def draw_kn_cross(big, s):
    w, h = big.get_size(); cx = w / 2
    _base(big, s, _heater_pts(w, h, 3 * s), GULES, GULES_HI)
    vb = 7 * s
    pygame.draw.rect(big, ARG, (int(cx - vb / 2), int(h * 0.15), int(vb), int(h * 0.58)))
    pygame.draw.rect(big, ARG, (int(w * 0.16), int(h * 0.33), int(w * 0.68), int(vb)))
    for rx, ry in ((0.2, 0.15), (0.8, 0.15)):
        _rivet(big, w * rx, h * ry, s)


def draw_kn_france(big, s):
    w, h = big.get_size()
    _base(big, s, _heater_pts(w, h, 3 * s), AZURE, AZURE_HI)
    fw, fh = w * 0.2, h * 0.24
    _fleur(big, w * 0.35, h * 0.3, fw, fh, OR, s)
    _fleur(big, w * 0.65, h * 0.3, fw, fh, OR, s)
    _fleur(big, w * 0.5, h * 0.6, fw, fh, OR, s)


def draw_kn_chevron(big, s):
    w, h = big.get_size(); cx = w / 2
    f = _base(big, s, _heater_pts(w, h, 3 * s), SABLE)
    _ordinary(big, f, lambda t: (pygame.draw.line(t, OR, (w * 0.16, h * 0.64), (cx, h * 0.34), max(3, int(8 * s))),
                                 pygame.draw.line(t, OR, (cx, h * 0.34), (w * 0.84, h * 0.64), max(3, int(8 * s)))))
    _mullet(big, w * 0.3, h * 0.22, 4.5 * s, OR, s)
    _mullet(big, w * 0.7, h * 0.22, 4.5 * s, OR, s)
    _mullet(big, w * 0.5, h * 0.64, 4.5 * s, OR, s)


def draw_kn_pattee(big, s):
    w, h = big.get_size()
    _base(big, s, _heater_pts(w, h, 3 * s), ARG)
    _cross_pattee(big, w / 2, h * 0.42, w * 0.3, GULES, s)


def draw_kn_bend(big, s):
    w, h = big.get_size()
    f = _base(big, s, _kite_pts(w, h, 3 * s), AZURE, AZURE_HI)
    p1, p2 = (w * 0.18, h * 0.1), (w * 0.82, h * 0.78)
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]; dl = math.hypot(dx, dy); ux, uy = dx / dl, dy / dl; px, py = -uy, ux
    bw = 7 * s

    def band(t):
        pygame.draw.polygon(t, OR, [(p1[0] + px * bw, p1[1] + py * bw), (p2[0] + px * bw, p2[1] + py * bw),
                                    (p2[0] - px * bw, p2[1] - py * bw), (p1[0] - px * bw, p1[1] - py * bw)])
        for off in (bw + 2.6 * s, -(bw + 2.6 * s)):
            pygame.draw.line(t, ARG, (p1[0] + px * off, p1[1] + py * off), (p2[0] + px * off, p2[1] + py * off), max(1, int(1.7 * s)))
    _ordinary(big, f, band)


def draw_kn_lion(big, s):
    w, h = big.get_size()
    _base(big, s, _heater_pts(w, h, 3 * s), GULES, GULES_HI)
    _lion_rampant(big, w / 2, h * 0.46, w * 0.42, h * 0.5, OR, s)


def draw_kn_quarterly(big, s):
    w, h = big.get_size(); cx, cy = w / 2, h * 0.45
    pts = _heater_pts(w, h, 3 * s)
    pygame.draw.polygon(big, OL, pts)
    pygame.draw.polygon(big, STM, _inset(pts, 1.7 * s))
    f = _inset(pts, 4.6 * s)

    def quarters(t):
        pygame.draw.rect(t, GULES, (0, 0, int(cx), int(cy)))
        pygame.draw.rect(t, OR, (int(cx), 0, int(w - cx), int(cy)))
        pygame.draw.rect(t, OR, (0, int(cy), int(cx), int(h - cy)))
        pygame.draw.rect(t, GULES, (int(cx), int(cy), int(w - cx), int(h - cy)))
    _ordinary(big, f, quarters)


def draw_kn_eagle(big, s):
    w, h = big.get_size()
    _base(big, s, _bouche_pts(w, h, 3 * s), OR)
    _eagle_displayed(big, w / 2, h * 0.45, w * 0.6, h * 0.52, SABLE, s)


def draw_kn_saltire(big, s):
    w, h = big.get_size(); cx, cy = w / 2, h * 0.42; off = w * 0.32
    f = _base(big, s, _kite_pts(w, h, 3 * s), VERT)
    _ordinary(big, f, lambda t: (pygame.draw.line(t, ARG, (cx - off, cy - off), (cx + off, cy + off), max(3, int(7 * s))),
                                 pygame.draw.line(t, ARG, (cx - off, cy + off), (cx + off, cy - off), max(3, int(7 * s)))))


def draw_kn_bendy(big, s):
    w, h = big.get_size()
    pts = _heater_pts(w, h, 3 * s)
    pygame.draw.polygon(big, OL, pts)
    pygame.draw.polygon(big, STM, _inset(pts, 1.7 * s))
    f = _inset(pts, 4.6 * s)

    def stripes(t):
        pygame.draw.rect(t, OR, (0, 0, w, h))
        bw = w / 3.4; o = -h
        while o < w:
            pygame.draw.polygon(t, AZURE, [(o, 0), (o + bw, 0), (o + bw + h, h), (o + h, h)])
            o += bw * 2
    _ordinary(big, f, stripes)


VARIANTS = [
    ("V1_crusader_heater", draw_crusader_heater, "V1  Heater", "gules · argent cross"),
    ("V2_norman_kite", draw_norman_kite, "V2  Norman kite", "azure · gold bend + mullets"),
    ("V3_round_targe", draw_round_targe, "V3  Round targe", "wood · boss · saltire"),
    ("V4_pavise", draw_pavise, "V4  Pavise", "sable · gold pale + fleur"),
    ("V5_round_buckler", draw_round_buckler, "V5  Buckler", "quartered · spiked boss"),
]

VARIANTS_NEW = [
    ("V6_greek_hoplon", draw_greek_hoplon, "V6  Greek hoplon", "bronze · Spartan lambda"),
    ("V7_roman_scutum", draw_roman_scutum, "V7  Roman scutum", "gules · eagle wings + bolt"),
    ("V8_viking_round", draw_viking_round, "V8  Viking round", "segmented · iron boss"),
    ("V9_heraldic_lion", draw_heraldic_lion, "V9  Heraldic lion", "gules · gold lion mask"),
    ("V10_winged_crest", draw_winged_crest, "V10  Winged crest", "azure · wings + crown"),
]

# Round 3 — 10 shields a REAL medieval knight would carry (heater/kite/bouché).
VARIANTS_KNIGHT = [
    ("K1_cross", draw_kn_cross, "K1  Heater", "gules · cross argent"),
    ("K2_france", draw_kn_france, "K2  Heater", "azure · 3 fleurs-de-lis or"),
    ("K3_chevron", draw_kn_chevron, "K3  Heater", "sable · chevron + 3 mullets or"),
    ("K4_pattee", draw_kn_pattee, "K4  Heater", "argent · cross pattée gules"),
    ("K5_bend", draw_kn_bend, "K5  Kite", "azure · bend or cotised"),
    ("K6_lion", draw_kn_lion, "K6  Heater", "gules · lion rampant or"),
    ("K7_quarterly", draw_kn_quarterly, "K7  Heater", "quarterly gules & or"),
    ("K8_eagle", draw_kn_eagle, "K8  Bouché", "or · eagle displayed sable"),
    ("K9_saltire", draw_kn_saltire, "K9  Kite", "vert · saltire argent"),
    ("K10_bendy", draw_kn_bendy, "K10  Heater", "bendy or & azure"),
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
    allv = VARIANTS + VARIANTS_NEW + VARIANTS_KNIGHT
    tiles = {key: _tile(fn, lab, cap) for key, fn, lab, cap in allv}
    for key, tile in tiles.items():
        pygame.image.save(tile, os.path.join(OUT_DIR, f"{key}.png"))
    gap, title_h = 12, 44
    tw, th = next(iter(tiles.values())).get_size()
    tf = pygame.font.SysFont("Arial", 22, bold=True)

    # original-5 sheet
    sheet5 = pygame.Surface((tw * 5 + gap * 6, th + title_h + gap))
    sheet5.fill((14, 15, 22))
    sheet5.blit(tf.render("Knight powerup — shield icons (inset = true size)", True, (255, 232, 168)), (gap + 2, 10))
    for i, (key, *_ ) in enumerate(VARIANTS):
        sheet5.blit(tiles[key], (gap + i * (tw + gap), title_h))
    pygame.image.save(sheet5, os.path.join(OUT_DIR, "shield_icons.png"))

    # combined 10 sheet — row 1 = original 5, row 2 = new 5
    rows = [VARIANTS, VARIANTS_NEW]
    sheetw = tw * 5 + gap * 6
    sheeth = title_h + 2 * th + 3 * gap
    sheet = pygame.Surface((sheetw, sheeth))
    sheet.fill((14, 15, 22))
    sheet.blit(tf.render("Knight shield icons — all 10 (row 1: medieval set · row 2: other sources)", True, (255, 232, 168)), (gap + 2, 10))
    for r, row in enumerate(rows):
        for i, (key, *_ ) in enumerate(row):
            sheet.blit(tiles[key], (gap + i * (tw + gap), title_h + r * (th + gap)))
    out = os.path.join(OUT_DIR, "shield_icons_all10.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet.get_width()}x{sheet.get_height()})")

    # round-3 deliverable: 10 AUTHENTIC-KNIGHT shields (2 rows × 5)
    kn = pygame.Surface((tw * 5 + gap * 6, title_h + 2 * th + 3 * gap))
    kn.fill((14, 15, 22))
    kn.blit(tf.render("Knight shields — 10 a real medieval knight would carry (inset = true size)", True, (255, 232, 168)), (gap + 2, 10))
    for r in range(2):
        for i, (key, *_ ) in enumerate(VARIANTS_KNIGHT[r * 5:r * 5 + 5]):
            kn.blit(tiles[key], (gap + i * (tw + gap), title_h + r * (th + gap)))
    knout = os.path.join(OUT_DIR, "shield_icons_knight10.png")
    pygame.image.save(kn, knout)
    print(f"saved {knout}  ({kn.get_width()}x{kn.get_height()})")
    print("per-variant PNGs (V1..V10, K1..K10) in", OUT_DIR)


if __name__ == "__main__":
    main()
