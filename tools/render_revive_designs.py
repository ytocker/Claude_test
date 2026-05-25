"""Visual design-exploration round for the "survive one hit" powerup
(replacing the fire Phoenix). EXPLORATION ONLY — never touches
game/config.py, world.py, or the powerup effect.

3 candidates: KNIGHT, GUARDIAN ANGEL, GOLDEN GUARDIAN. Exports a short
gameplay GIF of each (Pip flaps/jumps twice via real Bird physics) +
a combined GIF + a static mid-flap sheet.

Costume pieces anchor to a CONSTANT nominal rect (not the per-frame
tilt-rotated sprite bbox) so they don't jitter/resize between frames.
The ANGEL wing REPLACES Pip's own wing (covers it), rooted at the
shoulder and rotated with the flap.

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


def _amask(sprite):
    return pygame.mask.from_surface(sprite, 40).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))


def _sheen(sprite, top_col, bot_col, top_a=120, bot_a=95):
    w, h = sprite.get_size()
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(ov, (*top_col, top_a), (int(w * 0.16), int(-h * 0.12), int(w * 0.66), int(h * 0.66)))
    pygame.draw.ellipse(ov, (*bot_col, bot_a), (int(w * 0.10), int(h * 0.52), int(w * 0.82), int(h * 0.6)))
    ov.blit(_amask(sprite), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
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


def _qbez(p0, p1, p2, n=22):
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        out.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return out


def _rotate_about(img, piv_frac, piv_screen, deg):
    w, h = img.get_size()
    rot = pygame.transform.rotate(img, deg)
    pv = pygame.math.Vector2(piv_frac[0] * w - w / 2, piv_frac[1] * h - h / 2).rotate(-deg)
    cx, cy = rot.get_width() / 2, rot.get_height() / 2
    return rot, (int(piv_screen[0] - (cx + pv.x)), int(piv_screen[1] - (cy + pv.y)))


def _scaled(src):
    w, h = src.get_size()
    return pygame.transform.scale(src, (int(w * PS), int(h * PS)))


_NOM = None
def _nominal():
    global _NOM
    if _NOM is None:
        _NOM = _scaled(parrot.get_parrot(0, 0.0)).get_size()
    return _NOM


def _pose(pose):
    """Returns frame idx, the (tilt-rotated) body sprite + its rect, AND a
    CONSTANT-size nominal rect (centred the same) for stable costume anchoring."""
    fidx = int(pose.frame_t) % len(parrot.FRAMES)
    base = _scaled(parrot.get_parrot(fidx, pose.tilt_deg))
    body_rect = base.get_rect(center=(CX, int(pose.y)))
    nw, nh = _nominal()
    nom = pygame.Rect(0, 0, nw, nh); nom.center = (CX, int(pose.y))
    return fidx, base, body_rect, nom


def _P(rect, fx, fy):
    return (rect.x + fx * rect.w, rect.y + fy * rect.h)


_FLAP_DEG = {0: -15, 1: -2, 2: 12, 3: 22}


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
    fidx, base, body_rect, nom = _pose(pose)
    flap = _FLAP_DEG[fidx]
    _glow(surf, CX, int(pose.y) - 4, 80, (255, 250, 224), peak_a=56, layers=8)
    _rays(surf, CX, int(pose.y) - 4, 74, (255, 246, 206), n=14, a=24, width=2, inner=0.3)
    # pearl body (kept defined — gentle recolour so the face still reads)
    pip = _body(base, (250, 248, 250), (42, 42, 48), (255, 255, 255), (198, 208, 232), 120, 92)
    surf.blit(pip, body_rect.topleft)
    # Gently DIM Pip's own wing (upper back) so the angel wing REPLACES it —
    # a soft, semi-transparent pearl patch confined to the wing area and
    # clipped to the silhouette (does not touch the head/face).
    patch = pygame.Surface(pip.get_size(), pygame.SRCALPHA)
    pw, ph = pip.get_size()
    pygame.draw.ellipse(patch, (238, 242, 250, 175), (int(pw * 0.34), int(ph * 0.36), int(pw * 0.40), int(ph * 0.30)))
    patch.blit(_amask(pip), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(patch, body_rect.topleft)
    # ONE angel wing = Pip's wing, smaller, rooted at the shoulder, flapping
    nw, nh = int(nom.w * 0.78), int(nom.h * 0.82)
    wing = _angel_wing(nw, nh, mirror=False, bright=1.0)
    rot, tl = _rotate_about(wing, (0.86, 0.88), _P(nom, 0.52, 0.50), flap)
    surf.blit(rot, tl)
    # halo
    def halo(big, s):
        w, h = big.get_size()
        pygame.draw.ellipse(big, (255, 238, 158, 70), (int(1 * s), int(1 * s), int(w - 2 * s), int(h - 2 * s)))
        pygame.draw.ellipse(big, (255, 214, 96), (int(2 * s), int(2 * s), int(w - 4 * s), int(h - 4 * s)), max(2, int(2.4 * s)))
        pygame.draw.ellipse(big, (255, 252, 224), (int(4 * s), int(3 * s), int(w - 8 * s), int(h - 6 * s)), max(1, int(s)))
    hx, hy = _P(nom, 0.74, 0.05)
    _glow(surf, hx, hy, 18, (255, 232, 150), peak_a=56, layers=4)
    _blit_ss(surf, hx, hy, int(nom.w * 0.44), int(nom.h * 0.16), halo)
    for (fx, fy, r) in ((0.93, 0.42, 3), (0.14, 0.7, 3)):
        _star(surf, *_P(nom, fx, fy), r, (255, 248, 214))


def build_knight(surf, pose):
    fidx, base, body_rect, nom = _pose(pose)
    OL = (24, 28, 38); D = (70, 78, 96); MID = (146, 156, 178); HI = (238, 244, 255)
    BRASS = (208, 174, 98); BRASS_HI = (255, 232, 168); CRIM = (160, 44, 48); CREAM = (236, 230, 214)

    def plate(big, s, rx, ry, rw, rh):
        pygame.draw.ellipse(big, OL, (rx, ry, rw, rh))
        pygame.draw.ellipse(big, D, (rx + int(1.5 * s), ry + int(1.5 * s), rw - int(3 * s), rh - int(3 * s)))
        pygame.draw.ellipse(big, MID, (rx + int(3 * s), ry + int(3 * s), rw - int(6 * s), rh - int(6 * s)))
        pygame.draw.arc(big, HI, (rx + int(3 * s), ry + int(2 * s), rw - int(6 * s), rh - int(4 * s)), math.radians(202), math.radians(338), max(1, int(1.6 * s)))

    # body (slick gunmetal)
    surf.blit(_body(base, (140, 150, 174), (6, 9, 16), (236, 242, 254), (44, 50, 66), 118, 100), body_rect.topleft)

    # breastplate
    def breast(big, s):
        w, h = big.get_size()
        plate(big, s, int(1 * s), int(2 * s), int(w - 2 * s), int(h - 3 * s))
        pygame.draw.line(big, HI, (int(w * 0.5), int(5 * s)), (int(w * 0.5), int(h - 6 * s)), max(1, int(1.3 * s)))
        pygame.draw.circle(big, BRASS, (int(w * 0.5), int(h * 0.58)), int(2.6 * s))
        pygame.draw.circle(big, BRASS_HI, (int(w * 0.5) - int(s), int(h * 0.58) - int(s)), max(1, int(s)))
    _blit_ss(surf, *_P(nom, 0.45, 0.62), int(nom.w * 0.5), int(nom.h * 0.30), breast)

    # pauldron
    def pauldron(big, s):
        w, h = big.get_size()
        plate(big, s, int(2 * s), int(2 * s), int(w - 4 * s), int(h * 0.86))
    _blit_ss(surf, *_P(nom, 0.42, 0.45), int(nom.w * 0.32), int(nom.h * 0.22), pauldron)

    # ── armet helm: light steel dome + visor + flowing red crest ──
    def helm(big, s):
        w, h = big.get_size(); cxg = w // 2
        pygame.draw.ellipse(big, OL, (int(3 * s), int(3 * s), int(w - 6 * s), int(h * 0.74)))
        pygame.draw.ellipse(big, MID, (int(5 * s), int(5 * s), int(w - 10 * s), int(h * 0.70)))
        pygame.draw.arc(big, D, (int(6 * s), int(7 * s), int(w - 12 * s), int(h * 0.64)), math.radians(16), math.radians(164), max(2, int(2 * s)))
        pygame.draw.ellipse(big, HI, (int(9 * s), int(7 * s), int(w * 0.34), int(h * 0.26)))         # specular
        # brass comb along the crown
        pygame.draw.line(big, BRASS, (cxg, int(4 * s)), (cxg, int(h * 0.36)), max(2, int(2 * s)))
        pygame.draw.line(big, BRASS_HI, (cxg - int(s), int(5 * s)), (cxg - int(s), int(h * 0.34)), max(1, int(s)))
        # visor face-plate with eye slit + breaths
        vy = int(h * 0.42)
        pygame.draw.rect(big, OL, (int(7 * s), vy, int(w - 14 * s), int(h * 0.26)), border_radius=int(3 * s))
        pygame.draw.rect(big, D, (int(8 * s), vy + int(s), int(w - 16 * s), int(h * 0.24)), border_radius=int(3 * s))
        pygame.draw.rect(big, MID, (int(8 * s), vy + int(s), int(w - 16 * s), int(h * 0.07)))         # upper sheen band
        pygame.draw.rect(big, (8, 9, 13), (int(11 * s), int(vy + h * 0.10), int(w - 22 * s), int(h * 0.055)))  # eye slit
        pygame.draw.line(big, HI, (int(8 * s), vy + int(s)), (int(w - 8 * s), vy + int(s)), max(1, int(s)))    # brow glint
        for bx in range(4):
            x = int(cxg + (bx - 1.5) * int(3.2 * s))
            pygame.draw.circle(big, (8, 9, 13), (x, int(vy + h * 0.2)), max(1, int(0.9 * s)))
        pygame.draw.line(big, BRASS, (int(8 * s), vy), (int(w - 8 * s), vy), max(2, int(2 * s)))      # brass rim
        # flowing red crest — layered filled ribbon sweeping up-and-back
        sock = (cxg - int(2 * s), int(4 * s))
        pygame.draw.circle(big, BRASS, sock, int(2.2 * s))
        for col, off in (((112, 28, 40), 0), (CRIM, int(2 * s)), ((230, 110, 102), int(4 * s))):
            top = _qbez(sock, (sock[0] - int(12 * s), sock[1] - int(20 * s)), (sock[0] - int(32 * s), sock[1] - int(2 * s)), 18)
            bot = _qbez(sock, (sock[0] - int(7 * s), sock[1] - int(9 * s)), (sock[0] - int(26 * s), sock[1] + int(12 * s)), 18)
            pygame.draw.polygon(big, col, [(x + off, y) for (x, y) in top] + [(x + off, y) for (x, y) in reversed(bot)])
    _blit_ss(surf, *_P(nom, 0.73, 0.18), int(nom.w * 0.46), int(nom.h * 0.5), helm)

    # small heater shield HELD on the near wing / in front
    def shield(big, s):
        w, h = big.get_size(); cxg = w // 2
        pygame.draw.polygon(big, OL, [(int(3 * s), int(3 * s)), (int(w - 3 * s), int(3 * s)), (int(w - 3 * s), int(h * 0.46)), (cxg, int(h - 3 * s)), (int(3 * s), int(h * 0.46))])
        pygame.draw.polygon(big, MID, [(int(6 * s), int(6 * s)), (int(w - 6 * s), int(6 * s)), (int(w - 6 * s), int(h * 0.45)), (cxg, int(h - 7 * s)), (int(6 * s), int(h * 0.45))])
        pygame.draw.polygon(big, HI, [(int(6 * s), int(6 * s)), (int(w - 6 * s), int(6 * s)), (cxg, int(h * 0.5))])
        pygame.draw.polygon(big, CRIM, [(int(9 * s), int(9 * s)), (int(w - 9 * s), int(9 * s)), (int(w - 9 * s), int(h * 0.44)), (cxg, int(h - 10 * s)), (int(9 * s), int(h * 0.44))])
        pygame.draw.line(big, CREAM, (cxg, int(11 * s)), (cxg, int(h - 13 * s)), max(2, int(2.2 * s)))
        pygame.draw.line(big, CREAM, (int(11 * s), int(h * 0.30)), (int(w - 11 * s), int(h * 0.30)), max(2, int(2.2 * s)))
        pygame.draw.circle(big, HI, (cxg, int(h * 0.33)), int(3.2 * s))
        pygame.draw.circle(big, BRASS, (cxg, int(h * 0.33)), int(1.8 * s))
    _blit_ss(surf, *_P(nom, 0.38, 0.60), int(nom.w * 0.36), int(nom.h * 0.44), shield)

    # ── nicer longsword HELD in the talon (hilt overlaps the body) ──
    def sword(big, s):
        w, h = big.get_size()
        gx, gy = int(w * 0.44), int(h * 0.80)
        tx, ty = int(w * 0.74), int(h * 0.06)
        ux, uy = (tx - gx), (ty - gy)
        ln = math.hypot(ux, uy); ux, uy = ux / ln, uy / ln
        px, py = -uy, ux
        bw = 3.8 * s
        pygame.draw.polygon(big, OL, [(gx + px * bw, gy + py * bw), (gx - px * bw, gy - py * bw),
                                      (tx - px * 0.5 * s, ty - py * 0.5 * s), (tx + px * 0.5 * s, ty + py * 0.5 * s)])
        pygame.draw.polygon(big, MID, [(gx + px * (bw - 1.3 * s), gy + py * (bw - 1.3 * s)), (gx - px * (bw - 1.3 * s), gy - py * (bw - 1.3 * s)), (tx, ty)])
        pygame.draw.line(big, HI, (gx - px * (bw - s), gy - py * (bw - s)), (tx, ty), max(1, int(1.1 * s)))   # edge glint
        pygame.draw.line(big, D, (gx + ux * 5 * s, gy + uy * 5 * s), (tx - ux * 9 * s, ty - uy * 9 * s), max(1, int(0.9 * s)))  # fuller
        cg = 9 * s
        pygame.draw.line(big, BRASS, (gx + px * cg, gy + py * cg), (gx - px * cg, gy - py * cg), max(2, int(3 * s)))
        pygame.draw.circle(big, BRASS_HI, (int(gx + px * cg), int(gy + py * cg)), max(1, int(1.6 * s)))
        pygame.draw.circle(big, BRASS_HI, (int(gx - px * cg), int(gy - py * cg)), max(1, int(1.6 * s)))
        grip_end = (gx - ux * 12 * s, gy - uy * 12 * s)
        pygame.draw.line(big, (74, 54, 36), (gx, gy), grip_end, max(3, int(3.8 * s)))
        for t in (0.3, 0.6, 0.9):
            wx, wy = gx + (grip_end[0] - gx) * t, gy + (grip_end[1] - gy) * t
            pygame.draw.line(big, (124, 94, 62), (wx + px * 2.2 * s, wy + py * 2.2 * s), (wx - px * 2.2 * s, wy - py * 2.2 * s), max(1, int(1.1 * s)))
        pygame.draw.circle(big, BRASS, (int(grip_end[0]), int(grip_end[1])), int(2.6 * s))
        pygame.draw.circle(big, (210, 70, 90), (int(grip_end[0]), int(grip_end[1])), max(1, int(1.2 * s)))
    _blit_ss(surf, *_P(nom, 0.6, 0.5), int(nom.w * 0.52), int(nom.h * 0.95), sword)


def build_gold(surf, pose):
    fidx, base, body_rect, nom = _pose(pose)
    cy = int(pose.y)
    _rays(surf, CX, cy, 96, (255, 236, 158), n=12, a=30, width=2, inner=0.42)
    _rays(surf, CX, cy, 70, (255, 246, 196), n=12, a=26, width=2, inner=0.55)
    gold = _recolor(base, (236, 186, 74), add=(30, 18, 0))
    _sheen(gold, (255, 246, 196), (150, 104, 26), top_a=140, bot_a=120)
    iw, ih = gold.get_size()
    etch = pygame.Surface((iw, ih), pygame.SRCALPHA)
    for fy in (0.44, 0.56, 0.68):
        pygame.draw.arc(etch, (255, 240, 180, 150), (int(iw * 0.16), int(ih * fy), int(iw * 0.5), int(ih * 0.2)), math.radians(200), math.radians(340), 2)
    etch.blit(_amask(gold), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    gold.blit(etch, (0, 0))
    surf.blit(gold, body_rect.topleft)

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
    _blit_ss(surf, *_P(nom, 0.72, 0.06), int(nom.w * 0.42), int(nom.h * 0.26), crown)

    def gem(big, s):
        w, h = big.get_size(); cxg, cyg = w // 2, h // 2
        pygame.draw.polygon(big, (20, 90, 70), [(cxg, int(1 * s)), (int(w - 1 * s), cyg), (cxg, int(h - 1 * s)), (int(1 * s), cyg)])
        pygame.draw.polygon(big, (70, 200, 150), [(cxg, int(4 * s)), (int(w - 4 * s), cyg), (cxg, int(h - 4 * s)), (int(4 * s), cyg)])
        pygame.draw.polygon(big, (170, 245, 215), [(cxg, int(4 * s)), (int(w - 4 * s), cyg), (cxg, cyg)])
        pygame.draw.circle(big, (240, 255, 248), (int(cxg - 1.5 * s), int(cyg - 1.5 * s)), max(1, int(1.4 * s)))
    _blit_ss(surf, *_P(nom, 0.46, 0.6), int(nom.w * 0.2), int(nom.h * 0.2), gem)
    for (fx, fy, r) in ((0.18, 0.18, 4), (0.92, 0.34, 4), (0.86, 0.78, 4)):
        _star(surf, *_P(nom, fx, fy), r, (255, 250, 214))


CANDIDATES = [
    ("knight", "1  KNIGHT", build_knight),
    ("angel",  "2  GUARDIAN ANGEL", build_angel),
    ("gold",   "3  GOLDEN GUARDIAN", build_gold),
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
    # combined side-by-side animated GIF
    sc = 0.62; pw, ph = int(W * sc), int(H * sc); m = 8
    combined = []
    for i in range(len(poses)):
        cw = pw * len(CANDIDATES) + m * (len(CANDIDATES) + 1)
        sheet = pygame.Surface((cw, ph + m * 2)); sheet.fill((20, 22, 30))
        for j, (key, _, _) in enumerate(CANDIDATES):
            sheet.blit(pygame.transform.smoothscale(per[key][i], (pw, ph)), (m + j * (pw + m), m))
        combined.append(sheet)
    _save_gif(combined, os.path.join(OUT_DIR, "revive_anim.gif"), fps=22)
    print("saved revive_anim.gif", combined[0].get_size())
    # static mid-flap reference
    mid, margin = 8, 12
    sheet = pygame.Surface((W * len(CANDIDATES) + margin * (len(CANDIDATES) + 1), H + margin * 2))
    sheet.fill((20, 22, 30))
    for j, (key, _, _) in enumerate(CANDIDATES):
        sheet.blit(per[key][mid], (margin + j * (W + margin), margin))
    pygame.image.save(sheet, os.path.join(OUT_DIR, "revive_designs.png"))
    print("saved revive_designs.png")


if __name__ == "__main__":
    main()
