"""Visual design-exploration round for the "survive one hit" powerup
(replacing the fire Phoenix). EXPLORATION ONLY — never touches
game/config.py, world.py, or the powerup effect.

Renders 5 full themed re-skins of Pip and exports a short GAMEPLAY GIF of
each (Pip flaps/jumps twice) so the costume motion can be judged — in
particular whether the ANGEL wing is operative (it's Pip's own wing,
rooted at the shoulder and rotated with the flap), not decoration.

Run:  SDL_VIDEODRIVER=dummy python -m tools.render_revive_designs
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import pygame
from PIL import Image
pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H, GROUND_Y
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground
from game import parrot
from game.entities import Bird

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "revive_designs")
os.makedirs(OUT_DIR, exist_ok=True)

PS = 2.15
CX = 165


def backdrop(surf):
    pal = _biome.palette_for_phase(0.10)
    surf.blit(get_sky_surface_biome(W, H, GROUND_Y, pal, 1), (0, 0))
    for bx, by, sc, v in ((20, 90, 0.9, 0), (235, 120, 1.0, 2), (90, 200, 0.8, 3)):
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
    w, h = sprite.get_size()
    amask = pygame.mask.from_surface(sprite, 40).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(ov, (*top_col, top_a), (int(w * 0.16), int(-h * 0.12), int(w * 0.66), int(h * 0.66)))
    pygame.draw.ellipse(ov, (*bot_col, bot_a), (int(w * 0.10), int(h * 0.52), int(w * 0.82), int(h * 0.6)))
    ov.blit(amask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sprite.blit(ov, (0, 0))
    return sprite


def _body(base, mult, add, top, bot, ta=124, ba=98):
    s = _recolor(base, mult, add)
    _sheen(s, top, bot, ta, ba)
    return s


def _glow(surf, cx, cy, r, color, peak_a=70, layers=7):
    g = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    c = r + 2
    for i in range(layers, 0, -1):
        rr = int(r * i / layers)
        a = int(peak_a * (1 - (i - 1) / layers) ** 1.4)
        pygame.draw.circle(g, (*color, a), (c, c), rr)
    surf.blit(g, (int(cx - c), int(cy - c)))


def _rays(surf, cx, cy, r, color, n=10, a=44, width=2, inner=0.0):
    ray = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    c = r + 2
    for k in range(n):
        ang = k * (math.tau / n)
        x1, y1 = c + math.cos(ang) * r * inner, c + math.sin(ang) * r * inner
        pygame.draw.line(ray, (*color, a), (int(x1), int(y1)), (int(c + math.cos(ang) * r), int(c + math.sin(ang) * r)), width)
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


def _rotate_about(img, piv_frac, piv_screen, deg):
    """Rotate `img` by `deg` keeping the point at `piv_frac` pinned to
    `piv_screen` (so a wing flaps about the shoulder)."""
    w, h = img.get_size()
    rot = pygame.transform.rotate(img, deg)
    pv = pygame.math.Vector2(piv_frac[0] * w - w / 2, piv_frac[1] * h - h / 2).rotate(-deg)
    cx, cy = rot.get_width() / 2, rot.get_height() / 2
    return rot, (int(piv_screen[0] - (cx + pv.x)), int(piv_screen[1] - (cy + pv.y)))


def _pose(pose):
    fidx = int(pose.frame_t) % len(parrot.FRAMES)
    base = _scaled(parrot.get_parrot(fidx, pose.tilt_deg))
    rect = base.get_rect(center=(CX, int(pose.y)))
    return fidx, base, rect


def _scaled(src):
    w, h = src.get_size()
    return pygame.transform.scale(src, (int(w * PS), int(h * PS)))


def _P(rect, fx, fy):
    return (rect.x + fx * rect.w, rect.y + fy * rect.h)


_FLAP_DEG = {0: -16, 1: -3, 2: 12, 3: 22}     # wing sweep per flap frame


# ── slick angel wing (canonical = swept up-and-back / to the left) ───────────
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
        pygame.draw.polygon(big, DEEP, shape)
        pygame.draw.polygon(big, BODY, [(x * 0.95 + 0.03 * w, y * 0.95 + 0.015 * h) for (x, y) in shape])
        for k in range(6):
            f = k / 5
            bx, by = lead[int(8 + f * 16)]
            a = math.radians(150 - f * 18)
            L = h * (0.62 - 0.30 * f)
            tx, ty = bx + math.cos(a) * L, by + math.sin(a) * L
            perp = a + math.pi / 2; wd = h * (0.085 - 0.02 * f)
            pygame.draw.polygon(big, SH, [(bx + math.cos(perp) * wd, by + math.sin(perp) * wd), (tx, ty), (bx - math.cos(perp) * wd, by - math.sin(perp) * wd)])
            pygame.draw.polygon(big, PEARL, [(bx + math.cos(perp) * wd * 0.7, by + math.sin(perp) * wd * 0.7), (tx, ty), (bx, by)])
            pygame.draw.circle(big, PEARL, (int(tx), int(ty)), max(1, int(wd * 0.7)))
            if k < 3:
                pygame.draw.line(big, GOLD, (int((bx + tx) / 2), int((by + ty) / 2)), (int(tx), int(ty)), max(1, int(1.1 * s)))
        pygame.draw.lines(big, PEARL, False, lead, max(2, int(2.6 * s)))
        pygame.draw.lines(big, GOLD, False, lead[:18], max(1, int(1.3 * s)))
    img = _ss(box_w, box_h, fn, 5)
    if mirror:
        img = pygame.transform.flip(img, True, False)
    return img


def build_angel(surf, pose):
    fidx, base, rect = _pose(pose)
    flap = _FLAP_DEG[fidx]
    _glow(surf, CX, int(pose.y) - 4, 92, (255, 250, 224), peak_a=60, layers=8)
    _rays(surf, CX, int(pose.y) - 4, 84, (255, 246, 206), n=14, a=26, width=2, inner=0.25)
    # FAR wing (depth), flaps a little less
    fw, fh = int(rect.w * 0.8), int(rect.h * 0.9)
    far = _angel_wing(fw, fh, mirror=False, bright=0.7)
    rot, tl = _rotate_about(far, (0.86, 0.88), _P(rect, 0.60, 0.43), flap * 0.7)
    surf.blit(rot, tl)
    # pearl body
    surf.blit(_body(base, (255, 250, 246), (60, 58, 62), (255, 255, 255), (196, 206, 230), 130, 90), rect.topleft)
    # NEAR wing = Pip's own wing, rooted at the shoulder, flapping
    nw, nh = int(rect.w * 1.02), int(rect.h * 1.12)
    near = _angel_wing(nw, nh, mirror=False, bright=1.0)
    rot, tl = _rotate_about(near, (0.86, 0.88), _P(rect, 0.50, 0.50), flap)
    surf.blit(rot, tl)
    # halo
    def halo(big, s):
        w, h = big.get_size()
        pygame.draw.ellipse(big, (255, 238, 158, 70), (int(1 * s), int(1 * s), int(w - 2 * s), int(h - 2 * s)))
        pygame.draw.ellipse(big, (255, 214, 96), (int(2 * s), int(2 * s), int(w - 4 * s), int(h - 4 * s)), max(2, int(2.4 * s)))
        pygame.draw.ellipse(big, (255, 252, 224), (int(4 * s), int(3 * s), int(w - 8 * s), int(h - 6 * s)), max(1, int(s)))
    hx, hy = _P(rect, 0.74, 0.05)
    _glow(surf, hx, hy, 20, (255, 232, 150), peak_a=58, layers=4)
    _blit_ss(surf, hx, hy, int(rect.w * 0.46), int(rect.h * 0.17), halo)
    for (fx, fy, r) in ((0.92, 0.42, 3), (0.16, 0.7, 3)):
        _star(surf, *_P(rect, fx, fy), r, (255, 248, 214))


def build_knight(surf, pose):
    fidx, base, rect = _pose(pose)
    OL = (26, 30, 40); D = (72, 80, 98); MID = (140, 150, 172); HI = (236, 242, 254)
    BRASS = (206, 172, 96); CRIM = (150, 42, 46); CREAM = (236, 230, 214)

    def plate(big, s, rx, ry, rw, rh):
        pygame.draw.ellipse(big, OL, (rx, ry, rw, rh))
        pygame.draw.ellipse(big, D, (rx + int(1.5 * s), ry + int(1.5 * s), rw - int(3 * s), rh - int(3 * s)))
        pygame.draw.ellipse(big, MID, (rx + int(3 * s), ry + int(3 * s), rw - int(6 * s), rh - int(6 * s)))
        pygame.draw.arc(big, HI, (rx + int(3 * s), ry + int(2 * s), rw - int(6 * s), rh - int(4 * s)), math.radians(202), math.radians(338), max(1, int(1.6 * s)))

    # body (slick gunmetal)
    surf.blit(_body(base, (140, 150, 174), (6, 9, 16), (236, 242, 254), (44, 50, 66), 118, 100), rect.topleft)

    # breastplate
    def breast(big, s):
        w, h = big.get_size()
        plate(big, s, int(1 * s), int(2 * s), int(w - 2 * s), int(h - 3 * s))
        pygame.draw.line(big, HI, (int(w * 0.5), int(5 * s)), (int(w * 0.5), int(h - 6 * s)), max(1, int(1.3 * s)))
        pygame.draw.circle(big, BRASS, (int(w * 0.5), int(h * 0.58)), int(2.6 * s))
        pygame.draw.circle(big, (255, 235, 170), (int(w * 0.5) - int(s), int(h * 0.58) - int(s)), max(1, int(s)))
    _blit_ss(surf, *_P(rect, 0.45, 0.62), int(rect.w * 0.5), int(rect.h * 0.30), breast)

    # pauldron
    def pauldron(big, s):
        w, h = big.get_size()
        plate(big, s, int(2 * s), int(2 * s), int(w - 4 * s), int(h * 0.86))
    _blit_ss(surf, *_P(rect, 0.42, 0.45), int(rect.w * 0.32), int(rect.h * 0.22), pauldron)

    # helm
    def helm(big, s):
        w, h = big.get_size(); cxg = w // 2
        pygame.draw.ellipse(big, OL, (int(2 * s), int(2 * s), int(w - 4 * s), int(h * 0.9)))
        pygame.draw.ellipse(big, MID, (int(4 * s), int(4 * s), int(w - 8 * s), int(h * 0.86 - 2 * s)))
        pygame.draw.arc(big, D, (int(5 * s), int(7 * s), int(w - 10 * s), int(h * 0.78)), math.radians(18), math.radians(162), max(2, int(2.2 * s)))
        pygame.draw.ellipse(big, HI, (int(7 * s), int(6 * s), int(w * 0.40), int(h * 0.32)))
        vy = int(h * 0.49)
        pygame.draw.rect(big, OL, (int(6 * s), vy, int(w - 12 * s), int(h * 0.17)), border_radius=int(2 * s))
        pygame.draw.rect(big, (8, 9, 13), (int(8 * s), vy + int(2.5 * s), int(w - 16 * s), int(h * 0.08)))
        for bx in range(3):
            x = int(13 * s + bx * (w - 26 * s) / 2)
            pygame.draw.line(big, MID, (x, vy + int(2 * s)), (x, vy + int(h * 0.15)), max(1, int(1.2 * s)))
        pygame.draw.line(big, HI, (int(7 * s), vy - int(1.5 * s)), (int(w - 7 * s), vy - int(1.5 * s)), max(1, int(s)))
        pygame.draw.rect(big, BRASS, (int(cxg - 2 * s), int(-1 * s), int(4 * s), int(7 * s)))
        for k, col in enumerate(((120, 30, 40), CRIM, (222, 98, 90))):
            sp = (k - 1) * int(2 * s)
            pygame.draw.polygon(big, col, [(cxg - int(5 * s) + sp, int(3 * s)), (cxg + int(5 * s) + sp, int(3 * s)), (cxg + sp, int(-15 * s))])
    _blit_ss(surf, *_P(rect, 0.74, 0.17), int(rect.w * 0.46), int(rect.h * 0.54), helm)

    # small HEATER shield HELD on the near wing / in front (not on the tail)
    def shield(big, s):
        w, h = big.get_size(); cxg = w // 2
        out = [(int(3 * s), int(3 * s)), (int(w - 3 * s), int(3 * s)), (int(w - 3 * s), int(h * 0.46)), (cxg, int(h - 3 * s)), (int(3 * s), int(h * 0.46))]
        pygame.draw.polygon(big, OL, out)
        ins = [(int(6 * s), int(6 * s)), (int(w - 6 * s), int(6 * s)), (int(w - 6 * s), int(h * 0.45)), (cxg, int(h - 7 * s)), (int(6 * s), int(h * 0.45))]
        pygame.draw.polygon(big, MID, ins)
        pygame.draw.polygon(big, HI, [(int(6 * s), int(6 * s)), (int(w - 6 * s), int(6 * s)), (cxg, int(h * 0.5))])    # top bevel
        face = [(int(9 * s), int(9 * s)), (int(w - 9 * s), int(9 * s)), (int(w - 9 * s), int(h * 0.44)), (cxg, int(h - 10 * s)), (int(9 * s), int(h * 0.44))]
        pygame.draw.polygon(big, CRIM, face)
        pygame.draw.line(big, CREAM, (cxg, int(11 * s)), (cxg, int(h - 13 * s)), max(2, int(2.2 * s)))
        pygame.draw.line(big, CREAM, (int(11 * s), int(h * 0.30)), (int(w - 11 * s), int(h * 0.30)), max(2, int(2.2 * s)))
        pygame.draw.circle(big, HI, (cxg, int(h * 0.34)), int(3.4 * s))
        pygame.draw.circle(big, BRASS, (cxg, int(h * 0.34)), int(2 * s))
    _blit_ss(surf, *_P(rect, 0.40, 0.60), int(rect.w * 0.38), int(rect.h * 0.46), shield)

    # slim longsword to the side
    def sword(big, s):
        w, h = big.get_size()
        pygame.draw.line(big, OL, (int(w * 0.3), int(h * 0.95)), (int(w * 0.84), int(h * 0.06)), max(2, int(3 * s)))
        pygame.draw.line(big, MID, (int(w * 0.3), int(h * 0.95)), (int(w * 0.84), int(h * 0.06)), max(1, int(1.8 * s)))
        pygame.draw.line(big, HI, (int(w * 0.31), int(h * 0.93)), (int(w * 0.84), int(h * 0.07)), max(1, int(s)))
        pygame.draw.line(big, BRASS, (int(w * 0.16), int(h * 0.84)), (int(w * 0.46), int(h * 1.0)), max(2, int(3 * s)))
        pygame.draw.circle(big, BRASS, (int(w * 0.23), int(h * 0.94)), int(2.2 * s))
    _blit_ss(surf, *_P(rect, 1.0, 0.5), int(rect.w * 0.44), int(rect.h * 0.84), sword)


def build_bubble(surf, pose):
    fidx, base, rect = _pose(pose)
    R = int(rect.w * 0.78); cy = int(pose.y)
    back = pygame.Surface((R * 2 + 8, R * 2 + 8), pygame.SRCALPHA); c = R + 4
    pygame.draw.circle(back, (110, 195, 255, 50), (c, c), R)
    pygame.draw.circle(back, (150, 220, 255, 80), (c, c), R, 3)
    surf.blit(back, (CX - c, cy - c))
    surf.blit(base, rect.topleft)
    front = pygame.Surface((R * 2 + 8, R * 2 + 8), pygame.SRCALPHA)
    pygame.draw.circle(front, (200, 240, 255, 160), (c, c), R, 3)
    pygame.draw.circle(front, (255, 255, 255, 90), (c, c), R - 4, 1)
    rr = pygame.Rect(c - R, c - R, R * 2, R * 2)
    pygame.draw.arc(front, (255, 255, 255, 210), rr, math.radians(60), math.radians(150), 5)
    pygame.draw.arc(front, (255, 180, 255, 90), rr.inflate(-6, -6), math.radians(10), math.radians(80), 3)
    pygame.draw.arc(front, (160, 255, 220, 90), rr.inflate(-8, -8), math.radians(200), math.radians(280), 3)
    pygame.draw.arc(front, (255, 245, 160, 80), rr, math.radians(250), math.radians(310), 4)
    surf.blit(front, (CX - c, cy - c))
    for ang in (50, 130, 215, 300, 350):
        _star(surf, CX + math.cos(math.radians(ang)) * R, cy + math.sin(math.radians(ang)) * R, 4, (235, 248, 255))


def build_gold(surf, pose):
    fidx, base, rect = _pose(pose)
    cy = int(pose.y)
    # tasteful radiance: thin rays only (NO big soft circle/"bubble")
    _rays(surf, CX, cy, 96, (255, 236, 158), n=12, a=30, width=2, inner=0.42)
    _rays(surf, CX, cy, 70, (255, 246, 196), n=12, a=26, width=2, inner=0.55)
    gold = _recolor(base, (236, 186, 74), add=(30, 18, 0))
    _sheen(gold, (255, 246, 196), (150, 104, 26), top_a=140, bot_a=120)
    # engraved feather etch lines (clipped to body)
    iw, ih = gold.get_size()
    etch = pygame.Surface((iw, ih), pygame.SRCALPHA)
    for fy in (0.44, 0.56, 0.68):
        pygame.draw.arc(etch, (255, 240, 180, 150), (int(iw * 0.16), int(ih * fy), int(iw * 0.5), int(ih * 0.2)), math.radians(200), math.radians(340), 2)
    amask = pygame.mask.from_surface(gold, 40).to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    etch.blit(amask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    gold.blit(etch, (0, 0))
    surf.blit(gold, rect.topleft)
    # regal crown on the head
    def crown(big, s):
        w, h = big.get_size()
        pygame.draw.rect(big, (60, 44, 12), (int(2 * s), int(h * 0.5), int(w - 4 * s), int(h * 0.4)))
        pygame.draw.rect(big, (236, 196, 96), (int(3 * s), int(h * 0.52), int(w - 6 * s), int(h * 0.34)))
        pygame.draw.rect(big, (255, 234, 160), (int(3 * s), int(h * 0.52), int(w - 6 * s), int(h * 0.1)))
        for k in range(3):
            x = int(w * (0.22 + 0.28 * k))
            pygame.draw.polygon(big, (236, 196, 96), [(x - int(4 * s), int(h * 0.5)), (x + int(4 * s), int(h * 0.5)), (x, int(2 * s))])
            pygame.draw.circle(big, (90, 220, 170), (x, int(6 * s)), int(1.6 * s))
        pygame.draw.circle(big, (210, 70, 90), (int(w * 0.5), int(h * 0.68)), int(2.4 * s))
    _blit_ss(surf, *_P(rect, 0.72, 0.06), int(rect.w * 0.42), int(rect.h * 0.26), crown)
    # faceted emerald chest gem
    def gem(big, s):
        w, h = big.get_size(); cxg, cyg = w // 2, h // 2
        pygame.draw.polygon(big, (20, 90, 70), [(cxg, int(1 * s)), (int(w - 1 * s), cyg), (cxg, int(h - 1 * s)), (int(1 * s), cyg)])
        pygame.draw.polygon(big, (70, 200, 150), [(cxg, int(4 * s)), (int(w - 4 * s), cyg), (cxg, int(h - 4 * s)), (int(4 * s), cyg)])
        pygame.draw.polygon(big, (170, 245, 215), [(cxg, int(4 * s)), (int(w - 4 * s), cyg), (cxg, cyg)])
        pygame.draw.circle(big, (240, 255, 248), (int(cxg - 1.5 * s), int(cyg - 1.5 * s)), max(1, int(1.4 * s)))
    _blit_ss(surf, *_P(rect, 0.46, 0.6), int(rect.w * 0.2), int(rect.h * 0.2), gem)
    for (fx, fy, r) in ((0.18, 0.18, 4), (0.92, 0.34, 4), (0.86, 0.78, 4)):
        _star(surf, *_P(rect, fx, fy), r, (255, 250, 214))


def build_aegis(surf, pose):
    fidx, base, rect = _pose(pose)
    cy = int(pose.y)
    _glow(surf, CX, cy, 80, (80, 175, 255), peak_a=72, layers=6)
    surf.blit(_recolor(base, (200, 224, 248), add=(18, 22, 34)), rect.topleft)
    hx, hy = _P(rect, 0.58, 0.52); R = int(rect.w * 0.62)

    def hexa(big, s):
        w, h = big.get_size(); cc = (w // 2, h // 2)
        def hp(rad):
            return [(cc[0] + rad * s * math.cos(math.radians(60 * k - 30)), cc[1] + rad * s * math.sin(math.radians(60 * k - 30))) for k in range(6)]
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
    _blit_ss(surf, hx, hy, R * 2 + 8, R * 2 + 8, hexa)
    for k in range(6):
        ang = math.radians(60 * k - 30)
        _star(surf, hx + math.cos(ang) * R, hy + math.sin(ang) * R, 4, (210, 245, 255))


CANDIDATES = [
    ("knight", "1  KNIGHT", build_knight),
    ("angel",  "2  GUARDIAN ANGEL", build_angel),
    ("bubble", "3  FORCE-FIELD BUBBLE", build_bubble),
    ("gold",   "4  GOLDEN GUARDIAN", build_gold),
    ("aegis",  "5  AEGIS RUNE SHIELD", build_aegis),
]


def _label(surf, text):
    f = pygame.font.SysFont("Arial", 15, bold=True)
    t = f.render(text, True, (255, 255, 255))
    bg = pygame.Surface((t.get_width() + 14, t.get_height() + 8), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 180)); surf.blit(bg, (6, H - 32)); surf.blit(t, (13, H - 28))


class _Pose:
    __slots__ = ("frame_t", "vy", "y")

    def __init__(self, frame_t, vy, y):
        self.frame_t, self.vy, self.y = frame_t, vy, y

    @property
    def tilt_deg(self):
        t = max(-0.5, min(0.75, self.vy / 500.0))
        return -t * 55.0


def _poses(n=34, flaps=(3, 19)):
    bird = Bird()
    out = []
    for i in range(n):
        if i in flaps:
            bird.flap()
        bird.update(1 / 30.0)
        bird.y = max(225, min(360, bird.y))
        out.append(_Pose(bird.frame_t, bird.vy, bird.y))
    return out


def _save_gif(frames, path, scale=1.0, fps=22):
    imgs = []
    for f in frames:
        if scale != 1.0:
            f = pygame.transform.smoothscale(f, (int(f.get_width() * scale), int(f.get_height() * scale)))
        imgs.append(Image.frombytes("RGB", f.get_size(), pygame.image.tobytes(f, "RGB")))
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=int(1000 / fps), loop=0, optimize=True)


def main():
    poses = _poses()
    per = {}
    for key, label, fn in CANDIDATES:
        frames = []
        for p in poses:
            s = pygame.Surface((W, H)); backdrop(s); fn(s, p); _label(s, label)
            frames.append(s)
        per[key] = frames
        _save_gif(frames, os.path.join(OUT_DIR, f"revive_{key}.gif"), fps=22)
        print("saved", f"revive_{key}.gif")
    # combined side-by-side animated GIF (scaled to keep size sane)
    sc = 0.5; pw, ph = int(W * sc), int(H * sc); m = 6
    combined = []
    for i in range(len(poses)):
        cw = pw * len(CANDIDATES) + m * (len(CANDIDATES) + 1)
        sheet = pygame.Surface((cw, ph + m * 2))
        sheet.fill((20, 22, 30))
        for j, (key, _, _) in enumerate(CANDIDATES):
            small = pygame.transform.smoothscale(per[key][i], (pw, ph))
            sheet.blit(small, (m + j * (pw + m), m))
        combined.append(sheet)
    _save_gif(combined, os.path.join(OUT_DIR, "revive_anim.gif"), fps=22)
    print("saved revive_anim.gif", combined[0].get_size())
    # static reference (mid-flap frame), full-size side by side
    mid = 8
    margin = 12
    sheet = pygame.Surface((W * len(CANDIDATES) + margin * (len(CANDIDATES) + 1), H + margin * 2))
    sheet.fill((20, 22, 30))
    for j, (key, _, _) in enumerate(CANDIDATES):
        sheet.blit(per[key][mid], (margin + j * (W + margin), margin))
    pygame.image.save(sheet, os.path.join(OUT_DIR, "revive_designs.png"))
    print("saved revive_designs.png")


if __name__ == "__main__":
    main()
