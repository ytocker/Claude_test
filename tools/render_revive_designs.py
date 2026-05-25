"""Visual design-exploration round for the "survive one hit" powerup
(replacing the fire Phoenix). EXPLORATION ONLY — never touches
game/config.py, world.py, or the powerup effect.

3 candidates: KNIGHT, GUARDIAN ANGEL, GOLDEN GUARDIAN. Exports a short
gameplay GIF of each (Pip flaps/jumps twice via real Bird physics) +
a combined GIF + a static mid-flap sheet.

The whole character (body + costume) is composited on ONE layer and
rotated together by the bird's tilt, so the helmet/armour stay attached
to the head as he jumps. The ANGEL wing REPLACES Pip's own wing.

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


def _P(rect, fx, fy):
    return (rect.x + fx * rect.w, rect.y + fy * rect.h)


_FLAP_DEG = {0: -15, 1: -2, 2: 12, 3: 22}


def _base_body(fidx):
    """Untilted base sprite + its rect centred in the char layer's nom."""
    return _scaled(parrot.get_parrot(fidx, 0.0))


# ── slick angel wing ─────────────────────────────────────────────────────────
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
            a = math.radians(150 - f * 18); L = h * (0.62 - 0.30 * f)
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


# ── builders draw the WHOLE character onto `char` (nom = body rect) ──────────
def build_angel(char, nom, fidx):
    flap = _FLAP_DEG[fidx]
    base = _base_body(fidx)
    brect = base.get_rect(center=nom.center)
    # subtle divine rays only — NO white aura circle
    _rays(char, *nom.center, 78, (255, 247, 210), n=16, a=22, width=2, inner=0.42)
    pip = _body(base, (250, 248, 250), (42, 42, 48), (255, 255, 255), (198, 208, 232), 120, 92)
    char.blit(pip, brect.topleft)
    # dim Pip's own wing so the angel wing replaces it (face untouched)
    patch = pygame.Surface(pip.get_size(), pygame.SRCALPHA)
    pw, ph = pip.get_size()
    pygame.draw.ellipse(patch, (238, 242, 250, 175), (int(pw * 0.34), int(ph * 0.36), int(pw * 0.40), int(ph * 0.30)))
    patch.blit(_amask(pip), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    char.blit(patch, brect.topleft)
    # SMALLER angel wing = Pip's own wing, rooted at the shoulder, flapping
    nw, nh = int(nom.w * 0.66), int(nom.h * 0.70)
    wing = _angel_wing(nw, nh, mirror=False, bright=1.0)
    rot, tl = _rotate_about(wing, (0.86, 0.88), _P(nom, 0.52, 0.50), flap)
    char.blit(rot, tl)
    # clean thin halo (no white glow blob)
    def halo(big, s):
        w, h = big.get_size()
        pygame.draw.ellipse(big, (255, 210, 92), (int(2 * s), int(2 * s), int(w - 4 * s), int(h - 4 * s)), max(2, int(2.4 * s)))
        pygame.draw.ellipse(big, (255, 250, 214), (int(4 * s), int(3 * s), int(w - 8 * s), int(h - 6 * s)), max(1, int(s)))
    _blit_ss(char, *_P(nom, 0.74, 0.06), int(nom.w * 0.42), int(nom.h * 0.15), halo)
    for (fx, fy, r) in ((0.95, 0.42, 3), (0.12, 0.7, 3)):
        _star(char, *_P(nom, fx, fy), r, (255, 248, 214))


def build_knight(char, nom, fidx):
    base = _base_body(fidx)
    brect = base.get_rect(center=nom.center)
    OL = (24, 28, 38); D = (70, 78, 96); MID = (146, 156, 178); HI = (238, 244, 255)
    BRASS = (208, 174, 98); BRASS_HI = (255, 232, 168); CRIM = (160, 44, 48); CREAM = (236, 230, 214)

    def plate(big, s, rx, ry, rw, rh):
        pygame.draw.ellipse(big, OL, (rx, ry, rw, rh))
        pygame.draw.ellipse(big, D, (rx + int(1.5 * s), ry + int(1.5 * s), rw - int(3 * s), rh - int(3 * s)))
        pygame.draw.ellipse(big, MID, (rx + int(3 * s), ry + int(3 * s), rw - int(6 * s), rh - int(6 * s)))
        pygame.draw.arc(big, HI, (rx + int(3 * s), ry + int(2 * s), rw - int(6 * s), rh - int(4 * s)), math.radians(202), math.radians(338), max(1, int(1.6 * s)))

    # SHIELD strapped to the FRONT of the chest (drawn IN FRONT after the
    # body + breastplate, on the front-right chest pixels) so it reads clearly.
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

    char.blit(_body(base, (140, 150, 174), (6, 9, 16), (236, 242, 254), (44, 50, 66), 118, 100), brect.topleft)

    def breast(big, s):
        w, h = big.get_size()
        plate(big, s, int(1 * s), int(2 * s), int(w - 2 * s), int(h - 3 * s))
        pygame.draw.line(big, HI, (int(w * 0.5), int(5 * s)), (int(w * 0.5), int(h - 6 * s)), max(1, int(1.3 * s)))
        pygame.draw.circle(big, BRASS, (int(w * 0.5), int(h * 0.58)), int(2.6 * s))
        pygame.draw.circle(big, BRASS_HI, (int(w * 0.5) - int(s), int(h * 0.58) - int(s)), max(1, int(s)))
    _blit_ss(char, *_P(nom, 0.45, 0.62), int(nom.w * 0.5), int(nom.h * 0.30), breast)
    # shield on the FRONT of the chest (front-right chest pixels), in front
    _blit_ss(char, *_P(nom, 0.56, 0.63), int(nom.w * 0.34), int(nom.h * 0.42), shield)

    # SCALED (lamellar) armour over the near (right) wing/shoulder — rows of
    # overlapping metal scales inside a brass-trimmed rounded pauldron.
    def pauldron(big, s):
        w, h = big.get_size()
        SCALE = (152, 162, 184); SC_HI = (226, 234, 248); SC_D = (78, 86, 104); EDGE = (32, 36, 48)
        scs = 4.4 * s
        tmp = pygame.Surface((w, h), pygame.SRCALPHA)
        rows = int(h / (scs * 1.1)) + 2
        for row in range(rows):
            y = int(scs + row * scs * 1.1)
            off = int(scs) if row % 2 else 0
            x = int(scs) + off
            while x < w + scs:
                pygame.draw.circle(tmp, EDGE, (x, y), int(scs + 0.6 * s))
                pygame.draw.circle(tmp, SC_D, (x, y), int(scs))
                pygame.draw.circle(tmp, SCALE, (x, int(y - 0.7 * s)), int(scs * 0.82))
                pygame.draw.circle(tmp, SC_HI, (int(x - 1.1 * s), int(y - 1.7 * s)), max(1, int(scs * 0.34)))
                x += int(scs * 2)
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(mask, (255, 255, 255, 255), (int(2 * s), int(2 * s), int(w - 4 * s), int(h - 4 * s)))
        tmp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        big.blit(tmp, (0, 0))
        # brass rim + rivets + a top sheen arc
        pygame.draw.ellipse(big, BRASS, (int(2 * s), int(2 * s), int(w - 4 * s), int(h - 4 * s)), max(2, int(2 * s)))
        pygame.draw.arc(big, BRASS_HI, (int(3 * s), int(2 * s), int(w - 6 * s), int(h - 4 * s)), math.radians(200), math.radians(340), max(1, int(s)))
        cxg, cyg = w / 2, h / 2
        for ang in range(0, 360, 60):
            rx = int(cxg + (cxg - int(3 * s)) * math.cos(math.radians(ang)))
            ry = int(cyg + (cyg - int(3 * s)) * math.sin(math.radians(ang)))
            pygame.draw.circle(big, BRASS, (rx, ry), max(1, int(1.2 * s)))
    _blit_ss(char, *_P(nom, 0.45, 0.46), int(nom.w * 0.42), int(nom.h * 0.34), pauldron, scale=6)

    # slick, detailed armet helm
    def helm(big, s):
        w, h = big.get_size(); cxg = w // 2
        # gorget / neck guard
        pygame.draw.ellipse(big, D, (int(w * 0.16), int(h * 0.66), int(w * 0.68), int(h * 0.32)))
        pygame.draw.ellipse(big, MID, (int(w * 0.19), int(h * 0.67), int(w * 0.62), int(h * 0.22)))
        pygame.draw.arc(big, HI, (int(w * 0.2), int(h * 0.66), int(w * 0.6), int(h * 0.2)), math.radians(196), math.radians(344), max(1, int(1.2 * s)))
        # skull dome — smooth multi-step gradient
        for i, col in enumerate([OL, (52, 58, 74), (94, 102, 122), MID, (190, 200, 218)]):
            ins = int(i * 1.7 * s)
            pygame.draw.ellipse(big, col, (int(4 * s) + ins, int(4 * s) + ins, int(w - 8 * s) - 2 * ins, int(h * 0.7) - 2 * ins))
        pygame.draw.ellipse(big, HI, (int(10 * s), int(7 * s), int(w * 0.3), int(h * 0.22)))           # specular
        pygame.draw.arc(big, (38, 44, 58), (int(5 * s), int(7 * s), int(w - 10 * s), int(h * 0.64)), math.radians(14), math.radians(166), max(2, int(2 * s)))
        # raised crown comb + brass keel
        pygame.draw.polygon(big, (58, 64, 80), [(cxg - int(2.5 * s), int(5 * s)), (cxg + int(2.5 * s), int(5 * s)), (cxg + int(1.2 * s), int(h * 0.4)), (cxg - int(1.2 * s), int(h * 0.4))])
        pygame.draw.line(big, BRASS, (cxg, int(5 * s)), (cxg, int(h * 0.4)), max(1, int(1.6 * s)))
        pygame.draw.line(big, BRASS_HI, (cxg - int(0.9 * s), int(6 * s)), (cxg - int(0.9 * s), int(h * 0.38)), max(1, int(0.9 * s)))
        # brass brow band
        vy = int(h * 0.4)
        pygame.draw.line(big, BRASS, (int(7 * s), vy), (int(w - 7 * s), vy), max(2, int(2.2 * s)))
        pygame.draw.line(big, BRASS_HI, (int(7 * s), vy - int(0.9 * s)), (int(w - 7 * s), vy - int(0.9 * s)), max(1, int(0.9 * s)))
        # beveled face plate
        pygame.draw.polygon(big, OL, [(int(7 * s), vy), (int(w - 7 * s), vy), (int(w - 10 * s), int(h * 0.72)), (cxg, int(h * 0.8)), (int(10 * s), int(h * 0.72))])
        pygame.draw.polygon(big, (64, 72, 90), [(int(9 * s), vy + int(1.5 * s)), (int(w - 9 * s), vy + int(1.5 * s)), (int(w - 12 * s), int(h * 0.7)), (cxg, int(h * 0.77)), (int(12 * s), int(h * 0.7))])
        pygame.draw.polygon(big, MID, [(int(9 * s), vy + int(1.5 * s)), (int(w - 9 * s), vy + int(1.5 * s)), (int(w - 11 * s), int(h * 0.52)), (int(11 * s), int(h * 0.52))])
        # T eye-slit + breaths
        pygame.draw.rect(big, (6, 7, 11), (int(12 * s), int(vy + h * 0.11), int(w - 24 * s), int(h * 0.05)))
        pygame.draw.rect(big, (6, 7, 11), (int(cxg - 1.3 * s), int(vy + h * 0.11), int(2.6 * s), int(h * 0.22)))
        for bx in range(5):
            if abs(bx - 2) >= 1:
                pygame.draw.circle(big, (6, 7, 11), (int(cxg + (bx - 2) * int(3.0 * s)), int(vy + h * 0.30)), max(1, int(0.85 * s)))
        for rx in (0.2, 0.8):
            pygame.draw.circle(big, BRASS, (int(w * rx), int(h * 0.55)), max(1, int(1.3 * s)))         # cheek rivets
        # plume holder + flowing layered crest
        sock = (cxg - int(2 * s), int(4 * s))
        pygame.draw.circle(big, BRASS, sock, int(2.4 * s))
        pygame.draw.circle(big, BRASS_HI, (sock[0] - int(0.8 * s), sock[1] - int(0.8 * s)), max(1, int(1.0 * s)))
        for col, off in (((108, 26, 38), 0), (CRIM, int(2 * s)), ((232, 112, 104), int(4 * s))):
            top = _qbez(sock, (sock[0] - int(13 * s), sock[1] - int(22 * s)), (sock[0] - int(34 * s), sock[1] - int(2 * s)), 20)
            bot = _qbez(sock, (sock[0] - int(7 * s), sock[1] - int(9 * s)), (sock[0] - int(28 * s), sock[1] + int(13 * s)), 20)
            pygame.draw.polygon(big, col, [(x + off, y) for (x, y) in top] + [(x + off, y) for (x, y) in reversed(bot)])
        for k in range(3):
            strand = _qbez(sock, (sock[0] - int(12 * s), sock[1] - int(16 * s) + k * int(4 * s)), (sock[0] - int(30 * s), sock[1] + int(2 * s) + k * int(5 * s)), 16)
            pygame.draw.lines(big, (246, 150, 140), False, strand, max(1, int(0.8 * s)))
    _blit_ss(char, *_P(nom, 0.73, 0.17), int(nom.w * 0.5), int(nom.h * 0.54), helm, scale=6)

    # SWORD in the main (right/front) hand — hilt at the talon, blade up
    def sword(big, s):
        w, h = big.get_size()
        gx, gy = int(w * 0.42), int(h * 0.80)
        tx, ty = int(w * 0.74), int(h * 0.06)
        ux, uy = (tx - gx), (ty - gy); ln = math.hypot(ux, uy); ux, uy = ux / ln, uy / ln
        px, py = -uy, ux; bw = 3.8 * s
        pygame.draw.polygon(big, OL, [(gx + px * bw, gy + py * bw), (gx - px * bw, gy - py * bw), (tx - px * 0.5 * s, ty - py * 0.5 * s), (tx + px * 0.5 * s, ty + py * 0.5 * s)])
        pygame.draw.polygon(big, MID, [(gx + px * (bw - 1.3 * s), gy + py * (bw - 1.3 * s)), (gx - px * (bw - 1.3 * s), gy - py * (bw - 1.3 * s)), (tx, ty)])
        pygame.draw.line(big, HI, (gx - px * (bw - s), gy - py * (bw - s)), (tx, ty), max(1, int(1.1 * s)))
        pygame.draw.line(big, D, (gx + ux * 5 * s, gy + uy * 5 * s), (tx - ux * 9 * s, ty - uy * 9 * s), max(1, int(0.9 * s)))
        cg = 9 * s
        pygame.draw.line(big, BRASS, (gx + px * cg, gy + py * cg), (gx - px * cg, gy - py * cg), max(2, int(3 * s)))
        pygame.draw.circle(big, BRASS_HI, (int(gx + px * cg), int(gy + py * cg)), max(1, int(1.6 * s)))
        pygame.draw.circle(big, BRASS_HI, (int(gx - px * cg), int(gy - py * cg)), max(1, int(1.6 * s)))
        ge = (gx - ux * 12 * s, gy - uy * 12 * s)
        pygame.draw.line(big, (74, 54, 36), (gx, gy), ge, max(3, int(3.8 * s)))
        for t in (0.3, 0.6, 0.9):
            wx, wy = gx + (ge[0] - gx) * t, gy + (ge[1] - gy) * t
            pygame.draw.line(big, (124, 94, 62), (wx + px * 2.2 * s, wy + py * 2.2 * s), (wx - px * 2.2 * s, wy - py * 2.2 * s), max(1, int(1.1 * s)))
        pygame.draw.circle(big, BRASS, (int(ge[0]), int(ge[1])), int(2.6 * s))
        pygame.draw.circle(big, (210, 70, 90), (int(ge[0]), int(ge[1])), max(1, int(1.2 * s)))
    _blit_ss(char, *_P(nom, 0.74, 0.5), int(nom.w * 0.5), int(nom.h * 0.95), sword)


def build_gold(char, nom, fidx):
    base = _base_body(fidx)
    brect = base.get_rect(center=nom.center)
    _rays(char, *nom.center, 96, (255, 236, 158), n=12, a=30, width=2, inner=0.42)
    _rays(char, *nom.center, 70, (255, 246, 196), n=12, a=26, width=2, inner=0.55)
    gold = _recolor(base, (236, 186, 74), add=(30, 18, 0))
    _sheen(gold, (255, 246, 196), (150, 104, 26), top_a=140, bot_a=120)
    iw, ih = gold.get_size()
    etch = pygame.Surface((iw, ih), pygame.SRCALPHA)
    for fy in (0.44, 0.56, 0.68):
        pygame.draw.arc(etch, (255, 240, 180, 150), (int(iw * 0.16), int(ih * fy), int(iw * 0.5), int(ih * 0.2)), math.radians(200), math.radians(340), 2)
    etch.blit(_amask(gold), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    gold.blit(etch, (0, 0))
    char.blit(gold, brect.topleft)

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
    _blit_ss(char, *_P(nom, 0.72, 0.06), int(nom.w * 0.42), int(nom.h * 0.26), crown)

    def gem(big, s):
        w, h = big.get_size(); cxg, cyg = w // 2, h // 2
        pygame.draw.polygon(big, (20, 90, 70), [(cxg, int(1 * s)), (int(w - 1 * s), cyg), (cxg, int(h - 1 * s)), (int(1 * s), cyg)])
        pygame.draw.polygon(big, (70, 200, 150), [(cxg, int(4 * s)), (int(w - 4 * s), cyg), (cxg, int(h - 4 * s)), (int(4 * s), cyg)])
        pygame.draw.polygon(big, (170, 245, 215), [(cxg, int(4 * s)), (int(w - 4 * s), cyg), (cxg, cyg)])
        pygame.draw.circle(big, (240, 255, 248), (int(cxg - 1.5 * s), int(cyg - 1.5 * s)), max(1, int(1.4 * s)))
    _blit_ss(char, *_P(nom, 0.46, 0.6), int(nom.w * 0.2), int(nom.h * 0.2), gem)
    for (fx, fy, r) in ((0.18, 0.18, 4), (0.92, 0.34, 4), (0.86, 0.78, 4)):
        _star(char, *_P(nom, fx, fy), r, (255, 250, 214))


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


def render_one(label, fn, pose):
    surf = pygame.Surface((W, H)); backdrop(surf)
    nw, nh = _nominal()
    CW, CH = nw + 260, nh + 260
    char = pygame.Surface((CW, CH), pygame.SRCALPHA)
    nom = pygame.Rect(0, 0, nw, nh); nom.center = (CW // 2, CH // 2)
    fidx = int(pose.frame_t) % len(parrot.FRAMES)
    fn(char, nom, fidx)
    # rotate the WHOLE character together (helm stays on the head), then place
    rot = pygame.transform.rotate(char, pose.tilt_deg * 0.85)
    surf.blit(rot, rot.get_rect(center=(CX, int(pose.y))).topleft)
    _label(surf, label)
    return surf


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
        frames = [render_one(label, fn, p) for p in poses]
        per[key] = frames
        _save_gif(frames, os.path.join(OUT_DIR, f"revive_{key}.gif"), fps=22)
        print("saved", f"revive_{key}.gif")
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
    mid, margin = 8, 12
    sheet = pygame.Surface((W * len(CANDIDATES) + margin * (len(CANDIDATES) + 1), H + margin * 2))
    sheet.fill((20, 22, 30))
    for j, (key, _, _) in enumerate(CANDIDATES):
        sheet.blit(per[key][mid], (margin + j * (W + margin), margin))
    pygame.image.save(sheet, os.path.join(OUT_DIR, "revive_designs.png"))
    print("saved revive_designs.png")


if __name__ == "__main__":
    main()
