"""Visual design-exploration round for the "survive one hit" powerup
(replacing the fire Phoenix). EXPLORATION ONLY — never touches
game/config.py, world.py, or the powerup effect.

Each candidate is a full themed re-skin of Pip: body recoloured
(luminance-preserving grayscale+tint) + a soft sheen pass for a slicker
metallic/pearl finish, then layered procedural costume. The ANGEL wing is
Pip's OWN wing restyled (rooted at the shoulder, swept back like a flying
bird) — not decoration around him.

Run:  SDL_VIDEODRIVER=dummy python -m tools.render_revive_designs
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import random
import pygame
pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H, GROUND_Y
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground
from game import parrot

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "revive_designs")
os.makedirs(OUT_DIR, exist_ok=True)

PS = 2.15
CX, CY = 155, 300


# ── backdrop ─────────────────────────────────────────────────────────────────
def backdrop(surf):
    pal = _biome.palette_for_phase(0.10)
    surf.blit(get_sky_surface_biome(W, H, GROUND_Y, pal, 1), (0, 0))
    for bx, by, sc, v in ((20, 90, 0.9, 0), (220, 130, 1.0, 2), (90, 200, 0.8, 3)):
        draw_cloud(surf, bx, by, sc, variant=v)
    draw_mountains(surf, 0, GROUND_Y, W, pal["mtn_far"], pal["mtn_near"])
    draw_ground(surf, GROUND_Y, W, H, 0, pal["ground_top"], pal["ground_mid"], (60, 40, 25))


# ── helpers ──────────────────────────────────────────────────────────────────
def _ss(w, h, fn, scale=4):
    big = pygame.Surface((int(w * scale), int(h * scale)), pygame.SRCALPHA)
    fn(big, scale)
    return pygame.transform.smoothscale(big, (int(w), int(h)))


def _blit_ss(surf, cx, cy, w, h, fn, scale=4):
    surf.blit(_ss(w, h, fn, scale), (int(cx - w / 2), int(cy - h / 2)))


def _recolor(src, mult, add=(0, 0, 0)):
    g = pygame.transform.grayscale(src)
    g.fill((*mult, 255), special_flags=pygame.BLEND_RGBA_MULT)
    if add != (0, 0, 0):
        g.fill((*add, 0), special_flags=pygame.BLEND_RGB_ADD)
    return g


def _sheen(sprite, top_col, bot_col, top_a=120, bot_a=95):
    """Soft top highlight + bottom shadow, clipped to the sprite silhouette,
    for a slicker rounded-metal / pearl finish."""
    w, h = sprite.get_size()
    amask = pygame.mask.from_surface(sprite, 40).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(ov, (*top_col, top_a), (int(w * 0.16), int(-h * 0.12), int(w * 0.66), int(h * 0.66)))
    pygame.draw.ellipse(ov, (*bot_col, bot_a), (int(w * 0.10), int(h * 0.52), int(w * 0.82), int(h * 0.6)))
    ov.blit(amask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sprite.blit(ov, (0, 0))
    return sprite


def _glow(surf, cx, cy, r, color, peak_a=78, layers=7):
    g = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    c = r + 2
    for i in range(layers, 0, -1):
        rr = int(r * i / layers)
        a = int(peak_a * (1 - (i - 1) / layers) ** 1.3)
        pygame.draw.circle(g, (*color, a), (c, c), rr)
    surf.blit(g, (int(cx - c), int(cy - c)))


def _rays(surf, cx, cy, r, color, n=10, a=46, width=2):
    ray = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    c = r + 2
    for k in range(n):
        ang = k * (math.tau / n)
        pygame.draw.line(ray, (*color, a), (c, c), (int(c + math.cos(ang) * r), int(c + math.sin(ang) * r)), width)
    surf.blit(ray, (int(cx - c), int(cy - c)))


def _star(surf, x, y, rad, color=(255, 255, 255), a=235):
    s = pygame.Surface((rad * 4 + 4, rad * 4 + 4), pygame.SRCALPHA)
    c = rad * 2 + 2
    lo, sh = rad, max(1, rad // 4)
    pygame.draw.polygon(s, (*color, a), [(c, c - lo * 2), (c + sh, c), (c, c + lo * 2), (c - sh, c)])
    pygame.draw.polygon(s, (*color, a), [(c - lo * 2, c), (c, c - sh), (c + lo * 2, c), (c, c + sh)])
    pygame.draw.circle(s, (255, 255, 255, a), (c, c), max(1, sh))
    surf.blit(s, (int(x - c), int(y - c)))


def _qbez(p0, p1, p2, n=26):
    pts = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        pts.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return pts


def _base_pip():
    return parrot.get_parrot(0, 0.0)


def _scaled(src):
    w, h = src.get_size()
    return pygame.transform.scale(src, (int(w * PS), int(h * PS)))


def _rect_for(sprite):
    return sprite.get_rect(center=(CX, CY))


def _P(rect, fx, fy):
    return (rect.x + fx * rect.w, rect.y + fy * rect.h)


# ── slick angel wing (canonical = swept up-and-BACK / to the left) ───────────
def _angel_wing(box_w, box_h, mirror, bright=1.0):
    def fn(big, s):
        w, h = big.get_size()
        def C(c):
            return tuple(min(255, int(v * (0.7 + 0.3 * bright))) for v in c)
        PEARL = C((251, 252, 255)); BODY = C((233, 238, 250)); SH = C((196, 207, 232))
        DEEP = C((168, 180, 212)); GOLD = C((240, 210, 140))
        root = (0.90 * w, 0.92 * h); ctrlL = (0.30 * w, 0.12 * h); tip = (0.07 * w, 0.10 * h); ctrlT = (0.66 * w, 1.00 * h)
        lead = _qbez(root, ctrlL, tip, 30); trail = _qbez(tip, ctrlT, root, 30)
        shape = lead + trail
        pygame.draw.polygon(big, DEEP, shape)                                   # underside
        pygame.draw.polygon(big, BODY, [(x * 0.95 + 0.03 * w, y * 0.95 + 0.015 * h) for (x, y) in shape])
        # primary feathers along the trailing/outer edge (clean rounded blades)
        for k in range(6):
            f = k / 5
            bx = lead[int(8 + f * 16)][0]; by = lead[int(8 + f * 16)][1]      # base walks down the leading edge
            a = math.radians(150 - f * 18)                                     # fan toward trailing
            L = h * (0.62 - 0.30 * f)
            tx, ty = bx + math.cos(a) * L, by + math.sin(a) * L
            perp = a + math.pi / 2; wd = h * (0.085 - 0.02 * f)
            pts = [(bx + math.cos(perp) * wd, by + math.sin(perp) * wd), (tx, ty),
                   (bx - math.cos(perp) * wd, by - math.sin(perp) * wd)]
            pygame.draw.polygon(big, SH, pts)
            pygame.draw.polygon(big, PEARL, [(bx + math.cos(perp) * wd * 0.7, by + math.sin(perp) * wd * 0.7),
                                             (tx, ty), (bx, by)])
            pygame.draw.circle(big, PEARL, (int(tx), int(ty)), max(1, int(wd * 0.7)))
            if k < 3:
                pygame.draw.line(big, GOLD, (int((bx + tx) / 2), int((by + ty) / 2)), (int(tx), int(ty)), max(1, int(1.1 * s)))
        # crisp leading-edge highlight + thin gold trim
        pygame.draw.lines(big, PEARL, False, lead, max(2, int(2.6 * s)))
        pygame.draw.lines(big, GOLD, False, lead[:18], max(1, int(1.3 * s)))
    img = _ss(box_w, box_h, fn, 5)
    if mirror:
        img = pygame.transform.flip(img, True, False)
    return img


# ── candidate: GUARDIAN ANGEL ────────────────────────────────────────────────
def build_angel(surf):
    base = _scaled(_base_pip())
    rect = _rect_for(base)
    _glow(surf, CX, CY - 4, 92, (255, 250, 224), peak_a=66, layers=8)
    _rays(surf, CX, CY - 4, 84, (255, 246, 206), n=14, a=30, width=2)
    # FAR wing — only its tip shows above/behind the back (depth)
    fw, fh = int(rect.w * 0.82), int(rect.h * 0.92)
    far = _angel_wing(fw, fh, mirror=False, bright=0.72)
    fa = _P(rect, 0.60, 0.42)
    surf.blit(far, (int(fa[0] - 0.86 * fw), int(fa[1] - 0.88 * fh)))
    # pearl body + sheen
    pip = _recolor(base, (255, 250, 246), add=(60, 58, 62))
    _sheen(pip, (255, 255, 255), (196, 206, 230), top_a=130, bot_a=90)
    surf.blit(pip, rect.topleft)
    # NEAR wing — Pip's OWN wing, rooted at the shoulder, swept up-and-back
    nw, nh = int(rect.w * 1.02), int(rect.h * 1.12)
    near = _angel_wing(nw, nh, mirror=False, bright=1.0)
    na = _P(rect, 0.50, 0.50)
    surf.blit(near, (int(na[0] - 0.86 * nw), int(na[1] - 0.88 * nh)))
    # slim elegant halo
    def halo(big, s):
        w, h = big.get_size()
        pygame.draw.ellipse(big, (255, 238, 158, 70), (int(1 * s), int(1 * s), int(w - 2 * s), int(h - 2 * s)))
        pygame.draw.ellipse(big, (255, 214, 96), (int(2 * s), int(2 * s), int(w - 4 * s), int(h - 4 * s)), max(2, int(2.4 * s)))
        pygame.draw.ellipse(big, (255, 252, 224), (int(4 * s), int(3 * s), int(w - 8 * s), int(h - 6 * s)), max(1, int(s)))
    hx, hy = _P(rect, 0.74, 0.05)
    _glow(surf, hx, hy, 22, (255, 232, 150), peak_a=64, layers=4)
    _blit_ss(surf, hx, hy, int(rect.w * 0.46), int(rect.h * 0.17), halo)
    for (fx, fy, r) in ((0.92, 0.42, 3), (0.16, 0.7, 3), (0.55, 0.04, 2)):
        _star(surf, *_P(rect, fx, fy), r, (255, 248, 214))


# ── candidate: KNIGHT (slick gunmetal plate) ─────────────────────────────────
def build_knight(surf):
    base = _scaled(_base_pip())
    rect = _rect_for(base)
    OL = (26, 30, 40); D = (72, 80, 98); MID = (140, 150, 172); HI = (236, 242, 254)
    BRASS = (206, 172, 96); CRIM = (150, 42, 46); CREAM = (236, 230, 214)

    def plate(big, s, rx, ry, rw, rh, edge_hi=True):
        pygame.draw.ellipse(big, OL, (rx, ry, rw, rh))
        pygame.draw.ellipse(big, D, (rx + int(1.5 * s), ry + int(1.5 * s), rw - int(3 * s), rh - int(3 * s)))
        pygame.draw.ellipse(big, MID, (rx + int(3 * s), ry + int(3 * s), rw - int(6 * s), rh - int(6 * s)))
        if edge_hi:
            pygame.draw.arc(big, HI, (rx + int(3 * s), ry + int(2 * s), rw - int(6 * s), rh - int(4 * s)),
                            math.radians(202), math.radians(338), max(1, int(1.6 * s)))

    # shield BEHIND (beveled rim, clean heraldry)
    def shield(big, s):
        w, h = big.get_size(); cxg = w // 2
        out = [(cxg, int(2 * s)), (int(w - 3 * s), int(h * 0.30)), (cxg, int(h - 2 * s)), (int(3 * s), int(h * 0.30))]
        pygame.draw.polygon(big, OL, out)
        pygame.draw.polygon(big, MID, [(cxg, int(5 * s)), (int(w - 6 * s), int(h * 0.31)), (cxg, int(h - 5 * s)), (int(6 * s), int(h * 0.31))])
        pygame.draw.polygon(big, HI, [(cxg, int(5 * s)), (int(w - 6 * s), int(h * 0.31)), (cxg, int(h * 0.5)), (int(6 * s), int(h * 0.31))])  # top bevel sheen
        pygame.draw.polygon(big, CRIM, [(cxg, int(9 * s)), (int(w - 9 * s), int(h * 0.33)), (cxg, int(h - 9 * s)), (int(9 * s), int(h * 0.33))])
        pygame.draw.line(big, CREAM, (cxg, int(11 * s)), (cxg, int(h - 11 * s)), max(2, int(2.4 * s)))
        pygame.draw.line(big, CREAM, (int(11 * s), int(h * 0.40)), (int(w - 11 * s), int(h * 0.40)), max(2, int(2.4 * s)))
        pygame.draw.circle(big, HI, (cxg, int(h * 0.46)), int(4.5 * s))
        pygame.draw.circle(big, BRASS, (cxg, int(h * 0.46)), int(2.6 * s))
    sw_, sh_ = int(rect.w * 0.58), int(rect.h * 0.86)
    surf.blit(_ss(sw_, sh_, shield), (int(_P(rect, 0.15, 0.55)[0] - sw_ * 0.5), int(_P(rect, 0.15, 0.55)[1] - sh_ * 0.5)))

    # slick gunmetal body
    body = _recolor(base, (140, 150, 174), add=(6, 9, 16))
    _sheen(body, (236, 242, 254), (40, 46, 62), top_a=120, bot_a=110)
    surf.blit(body, rect.topleft)

    # breastplate (smooth gradient, central ridge, brass boss)
    def breast(big, s):
        w, h = big.get_size()
        plate(big, s, int(1 * s), int(2 * s), int(w - 2 * s), int(h - 3 * s))
        pygame.draw.line(big, HI, (int(w * 0.5), int(5 * s)), (int(w * 0.5), int(h - 6 * s)), max(1, int(1.3 * s)))
        pygame.draw.line(big, D, (int(w * 0.5) + int(1.3 * s), int(5 * s)), (int(w * 0.5) + int(1.3 * s), int(h - 6 * s)), max(1, int(s)))
        pygame.draw.circle(big, BRASS, (int(w * 0.5), int(h * 0.58)), int(2.6 * s))
        pygame.draw.circle(big, (255, 235, 170), (int(w * 0.5) - int(s), int(h * 0.58) - int(s)), max(1, int(s)))
    _blit_ss(surf, *_P(rect, 0.45, 0.62), int(rect.w * 0.5), int(rect.h * 0.30), breast)

    # pauldron
    def pauldron(big, s):
        w, h = big.get_size()
        plate(big, s, int(2 * s), int(2 * s), int(w - 4 * s), int(h * 0.86))
    _blit_ss(surf, *_P(rect, 0.42, 0.45), int(rect.w * 0.32), int(rect.h * 0.22), pauldron)

    # sleek knight helm: light steel dome, clear visor slit, red plume
    def helm(big, s):
        w, h = big.get_size(); cxg = w // 2
        pygame.draw.ellipse(big, OL, (int(2 * s), int(2 * s), int(w - 4 * s), int(h * 0.9)))             # thin outline
        pygame.draw.ellipse(big, MID, (int(4 * s), int(4 * s), int(w - 8 * s), int(h * 0.86 - 2 * s)))   # steel dome (dominant)
        pygame.draw.arc(big, D, (int(5 * s), int(7 * s), int(w - 10 * s), int(h * 0.78)), math.radians(18), math.radians(162), max(2, int(2.2 * s)))  # lower shade
        pygame.draw.ellipse(big, HI, (int(7 * s), int(6 * s), int(w * 0.40), int(h * 0.32)))             # specular
        vy = int(h * 0.49)
        pygame.draw.rect(big, OL, (int(6 * s), vy, int(w - 12 * s), int(h * 0.17)), border_radius=int(2 * s))
        pygame.draw.rect(big, (8, 9, 13), (int(8 * s), vy + int(2.5 * s), int(w - 16 * s), int(h * 0.08)))
        for bx in range(3):
            x = int(13 * s + bx * (w - 26 * s) / 2)
            pygame.draw.line(big, MID, (x, vy + int(2 * s)), (x, vy + int(h * 0.15)), max(1, int(1.2 * s)))
        pygame.draw.line(big, HI, (int(7 * s), vy - int(1.5 * s)), (int(w - 7 * s), vy - int(1.5 * s)), max(1, int(s)))  # brow ridge
        # crest base + layered red plume
        pygame.draw.rect(big, BRASS, (int(cxg - 2 * s), int(-1 * s), int(4 * s), int(7 * s)))
        for k, col in enumerate(((120, 30, 40), CRIM, (222, 98, 90))):
            sp = (k - 1) * int(2 * s)
            pygame.draw.polygon(big, col, [(cxg - int(5 * s) + sp, int(3 * s)), (cxg + int(5 * s) + sp, int(3 * s)), (cxg + sp, int(-15 * s))])
    _blit_ss(surf, *_P(rect, 0.74, 0.17), int(rect.w * 0.46), int(rect.h * 0.54), helm)

    # slim elegant longsword
    def sword(big, s):
        w, h = big.get_size()
        pygame.draw.line(big, OL, (int(w * 0.3), int(h * 0.95)), (int(w * 0.84), int(h * 0.06)), max(2, int(3 * s)))
        pygame.draw.line(big, MID, (int(w * 0.3), int(h * 0.95)), (int(w * 0.84), int(h * 0.06)), max(1, int(1.8 * s)))
        pygame.draw.line(big, HI, (int(w * 0.31), int(h * 0.93)), (int(w * 0.84), int(h * 0.07)), max(1, int(s)))  # edge glint
        pygame.draw.line(big, BRASS, (int(w * 0.16), int(h * 0.84)), (int(w * 0.46), int(h * 1.0)), max(2, int(3 * s)))
        pygame.draw.circle(big, BRASS, (int(w * 0.23), int(h * 0.94)), int(2.2 * s))
    _blit_ss(surf, *_P(rect, 1.02, 0.5), int(rect.w * 0.46), int(rect.h * 0.86), sword)


# ── candidate: FORCE-FIELD BUBBLE (unchanged — already reads well) ───────────
def build_bubble(surf):
    base = _scaled(_base_pip())
    rect = _rect_for(base)
    R = int(rect.w * 0.78)
    back = pygame.Surface((R * 2 + 8, R * 2 + 8), pygame.SRCALPHA); c = R + 4
    pygame.draw.circle(back, (110, 195, 255, 50), (c, c), R)
    pygame.draw.circle(back, (150, 220, 255, 80), (c, c), R, 3)
    surf.blit(back, (CX - c, CY - c))
    surf.blit(base, rect.topleft)
    front = pygame.Surface((R * 2 + 8, R * 2 + 8), pygame.SRCALPHA)
    pygame.draw.circle(front, (200, 240, 255, 160), (c, c), R, 3)
    pygame.draw.circle(front, (255, 255, 255, 90), (c, c), R - 4, 1)
    rr = pygame.Rect(c - R, c - R, R * 2, R * 2)
    pygame.draw.arc(front, (255, 255, 255, 210), rr, math.radians(60), math.radians(150), 5)
    pygame.draw.arc(front, (255, 255, 255, 110), rr.inflate(-10, -10), math.radians(55), math.radians(120), 3)
    pygame.draw.arc(front, (255, 180, 255, 90), rr.inflate(-6, -6), math.radians(10), math.radians(80), 3)
    pygame.draw.arc(front, (160, 255, 220, 90), rr.inflate(-8, -8), math.radians(200), math.radians(280), 3)
    pygame.draw.arc(front, (255, 245, 160, 80), rr, math.radians(250), math.radians(310), 4)
    surf.blit(front, (CX - c, CY - c))
    for ang in (50, 130, 215, 300, 350):
        _star(surf, CX + math.cos(math.radians(ang)) * R, CY + math.sin(math.radians(ang)) * R, 4, (235, 248, 255))


# ── candidate: GOLDEN GUARDIAN (slick polished gold) ─────────────────────────
def build_gold(surf):
    base = _scaled(_base_pip())
    rect = _rect_for(base)
    _glow(surf, CX, CY, 86, (255, 222, 120), peak_a=72, layers=8)
    _rays(surf, CX, CY, 96, (255, 236, 158), n=12, a=34, width=2)
    gold = _recolor(base, (236, 186, 74), add=(30, 18, 0))
    _sheen(gold, (255, 246, 196), (150, 104, 26), top_a=140, bot_a=120)
    # fine filigree on the chest
    iw, ih = gold.get_size()
    pygame.draw.arc(gold, (255, 240, 180), (int(iw * 0.3), int(ih * 0.5), int(iw * 0.3), int(ih * 0.22)), math.radians(200), math.radians(340), 1)
    surf.blit(gold, rect.topleft)
    # faceted emerald chest gem
    def gem(big, s):
        w, h = big.get_size(); cxg, cyg = w // 2, h // 2
        pygame.draw.polygon(big, (20, 90, 70), [(cxg, int(1 * s)), (int(w - 1 * s), cyg), (cxg, int(h - 1 * s)), (int(1 * s), cyg)])
        pygame.draw.polygon(big, (70, 200, 150), [(cxg, int(4 * s)), (int(w - 4 * s), cyg), (cxg, int(h - 4 * s)), (int(4 * s), cyg)])
        pygame.draw.polygon(big, (170, 245, 215), [(cxg, int(4 * s)), (int(w - 4 * s), cyg), (cxg, cyg)])    # facet
        pygame.draw.circle(big, (240, 255, 248), (int(cxg - 1.5 * s), int(cyg - 1.5 * s)), max(1, int(1.4 * s)))
    _blit_ss(surf, *_P(rect, 0.46, 0.6), int(rect.w * 0.2), int(rect.h * 0.2), gem)
    # a few elegant, varied sparkles (not clutter)
    for (fx, fy, r) in ((0.18, 0.16, 5), (0.9, 0.34, 4), (0.62, 0.04, 3), (0.86, 0.76, 5)):
        _star(surf, *_P(rect, fx, fy), r, (255, 250, 214))


# ── candidate: AEGIS RUNE SHIELD (unchanged) ─────────────────────────────────
def build_aegis(surf):
    base = _scaled(_base_pip())
    rect = _rect_for(base)
    _glow(surf, CX, CY, 84, (80, 175, 255), peak_a=80, layers=6)
    surf.blit(_recolor(base, (200, 224, 248), add=(18, 22, 34)), rect.topleft)
    hx, hy = _P(rect, 0.58, 0.52); R = int(rect.w * 0.62)

    def hexa(big, s):
        w, h = big.get_size(); cc = (w // 2, h // 2)
        def hp(rad):
            return [(cc[0] + rad * s * math.cos(math.radians(60 * k - 30)),
                     cc[1] + rad * s * math.sin(math.radians(60 * k - 30))) for k in range(6)]
        fill = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(fill, (70, 165, 255, 70), hp(R - 1)); big.blit(fill, (0, 0))
        pygame.draw.polygon(big, (150, 220, 255, 235), hp(R - 1), int(2.5 * s))
        pygame.draw.polygon(big, (200, 240, 255, 170), hp(R - 6), max(1, int(s)))
        pygame.draw.polygon(big, (120, 200, 255, 120), hp(R - 12), max(1, int(s)))
        for ring in (R * 0.34, R * 0.62):
            for k in range(6):
                ang = math.radians(60 * k)
                ccx = cc[0] + math.cos(ang) * ring * s; ccy = cc[1] + math.sin(ang) * ring * s
                cell = [(ccx + 4 * s * math.cos(math.radians(60 * j - 30)), ccy + 4 * s * math.sin(math.radians(60 * j - 30))) for j in range(6)]
                pygame.draw.polygon(big, (170, 225, 255, 70), cell, 1)
        rc = (225, 248, 255)
        pygame.draw.lines(big, rc, False, [(cc[0] - int(7 * s), cc[1] - int(5 * s)), (cc[0], cc[1] - int(11 * s)), (cc[0] + int(7 * s), cc[1] - int(5 * s))], max(1, int(s)))
        pygame.draw.circle(big, rc, cc, int(4 * s), max(1, int(s)))
        pygame.draw.line(big, rc, (cc[0], cc[1] + int(4 * s)), (cc[0], cc[1] + int(10 * s)), max(1, int(s)))
        pygame.draw.arc(big, rc, (cc[0] - int(9 * s), cc[1] - int(9 * s), int(18 * s), int(18 * s)), math.radians(20), math.radians(160), max(1, int(s)))
    _blit_ss(surf, hx, hy, R * 2 + 8, R * 2 + 8, hexa)
    for k in range(6):
        ang = math.radians(60 * k - 30)
        _star(surf, hx + math.cos(ang) * R, hy + math.sin(ang) * R, 4, (210, 245, 255))


CANDIDATES = [
    ("knight", "1  KNIGHT (slick plate + shield + sword)", build_knight),
    ("angel",  "2  GUARDIAN ANGEL (his wings = angel wings)", build_angel),
    ("bubble", "3  FORCE-FIELD BUBBLE", build_bubble),
    ("gold",   "4  GOLDEN GUARDIAN (polished)", build_gold),
    ("aegis",  "5  AEGIS RUNE SHIELD", build_aegis),
]


def _label(surf, text):
    f = pygame.font.SysFont("Arial", 15, bold=True)
    t = f.render(text, True, (255, 255, 255))
    bg = pygame.Surface((t.get_width() + 14, t.get_height() + 8), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 180)); surf.blit(bg, (6, H - 32)); surf.blit(t, (13, H - 28))


def render_candidate(key, label, fn):
    random.seed(7)
    surf = pygame.Surface((W, H))
    backdrop(surf)
    fn(surf)
    _label(surf, label)
    return surf


def main():
    frames = []
    for key, label, fn in CANDIDATES:
        fr = render_candidate(key, label, fn)
        pygame.image.save(fr, os.path.join(OUT_DIR, f"revive_{key}.png"))
        frames.append(fr)
    margin = 12
    cols = len(frames)
    sheet = pygame.Surface((W * cols + margin * (cols + 1), H + margin * 2))
    sheet.fill((20, 22, 30))
    for i, fr in enumerate(frames):
        sheet.blit(fr, (margin + i * (W + margin), margin))
    out = os.path.join(OUT_DIR, "revive_designs.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
