"""Visual design-exploration round for the "survive one hit / second life"
powerup (replacing the fire Phoenix look). EXPLORATION ONLY — never
touches game/config.py, world.py, or the powerup effect.

Each candidate is a FULL re-skin of Pip: his body is recoloured to match
the theme (luminance-preserving tint via pygame.transform.grayscale +
tint) and then layered with detailed procedural costume (full plate
armour, big feathered wings, ornate energy shields, etc.). Rendered on a
clean gameplay backdrop, character enlarged so the detail reads, laid out
side by side for picking.

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_revive_designs
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
from game.hud import HUD

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "revive_designs")
os.makedirs(OUT_DIR, exist_ok=True)

PS = 2.15                      # Pip showcase scale (so costume detail reads)
CX, CY = 155, 300              # character centre on the frame
_HUD = HUD()


# ── backdrop (scenery + HUD, NO bird/parcel so we fully control the look) ────
def backdrop(surf):
    class _W:  # minimal stand-in for HUD.draw_play
        pass
    pal = _biome.palette_for_phase(0.10)
    surf.blit(get_sky_surface_biome(W, H, GROUND_Y, pal, 1), (0, 0))
    for bx, by, sc, v in ((20, 90, 0.9, 0), (220, 130, 1.0, 2), (90, 200, 0.8, 3)):
        draw_cloud(surf, bx, by, sc, variant=v)
    draw_mountains(surf, 0, GROUND_Y, W, pal["mtn_far"], pal["mtn_near"])
    draw_ground(surf, GROUND_Y, W, H, 0, pal["ground_top"], pal["ground_mid"], (60, 40, 25))


# ── shared helpers ───────────────────────────────────────────────────────────
def _ss(w, h, fn, scale=4):
    big = pygame.Surface((int(w * scale), int(h * scale)), pygame.SRCALPHA)
    fn(big, scale)
    return pygame.transform.smoothscale(big, (int(w), int(h)))


def _blit_ss(surf, cx, cy, w, h, fn, scale=4):
    img = _ss(w, h, fn, scale)
    surf.blit(img, (int(cx - w / 2), int(cy - h / 2)))


def _recolor(src, mult, add=(0, 0, 0)):
    """Luminance-preserving recolour: grayscale → multiply by `mult` →
    optional additive lift. Keeps shading + dark sunglasses readable."""
    g = pygame.transform.grayscale(src)
    g.fill((*mult, 255), special_flags=pygame.BLEND_RGBA_MULT)
    if add != (0, 0, 0):
        g.fill((*add, 0), special_flags=pygame.BLEND_RGB_ADD)
    return g


def _glow(surf, cx, cy, r, color, peak_a=80, layers=6):
    g = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    c = r + 2
    for i in range(layers, 0, -1):
        rr = int(r * i / layers)
        a = int(peak_a * (1 - (i - 1) / layers))
        pygame.draw.circle(g, (*color, a), (c, c), rr)
    surf.blit(g, (int(cx - c), int(cy - c)))


def _rays(surf, cx, cy, r, color, n=12, a=70, rot=0.0):
    ray = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    c = r + 2
    for k in range(n):
        ang = rot + k * (math.tau / n)
        x2 = c + math.cos(ang) * r
        y2 = c + math.sin(ang) * r
        pygame.draw.line(ray, (*color, a), (c, c), (int(x2), int(y2)), 3)
    surf.blit(ray, (int(cx - c), int(cy - c)))


def _star(surf, x, y, rad, color=(255, 255, 255), a=240):
    s = pygame.Surface((rad * 2 + 4, rad * 2 + 4), pygame.SRCALPHA)
    c = rad + 2
    lo, sh = rad, max(1, rad // 3)
    pygame.draw.polygon(s, (*color, a), [(c, c - lo), (c + sh, c), (c, c + lo), (c - sh, c)])
    pygame.draw.polygon(s, (*color, a), [(c - lo, c), (c, c - sh), (c + lo, c), (c, c + sh)])
    pygame.draw.circle(s, (255, 255, 255, a), (c, c), max(1, sh))
    surf.blit(s, (int(x - c), int(y - c)))


def _base_pip():
    return parrot.get_parrot(0, 0.0)


def _scaled(src):
    w, h = src.get_size()
    return pygame.transform.scale(src, (int(w * PS), int(h * PS)))


def _rect_for(sprite):
    return sprite.get_rect(center=(CX, CY))


def _P(rect, fx, fy):
    return (rect.x + fx * rect.w, rect.y + fy * rect.h)


# ── detailed feathered angel wing ────────────────────────────────────────────
def _angel_wing(box_w, box_h, mirror):
    """A layered feathered wing (canonical = left wing: root bottom-right,
    feathers fanning UP-and-LEFT). Three rows — secondaries behind,
    primaries (gold-tipped) on top, small coverts at the root — each
    feather a rounded blade so it reads as plumage, not spikes."""
    def fn(big, s):
        w, h = big.get_size()
        rx, ry = 0.86 * w, 0.90 * h
        WHITE = (252, 252, 255); FILL = (236, 240, 251); SH = (196, 205, 228); GOLD = (255, 224, 130)

        def feather(ang_deg, L, wd, fill, edge, tip=None):
            a = math.radians(ang_deg)
            tx, ty = rx + math.cos(a) * L, ry + math.sin(a) * L
            perp = a + math.pi / 2
            ox, oy = math.cos(perp) * wd, math.sin(perp) * wd
            b1 = (rx + ox * 0.5, ry + oy * 0.5); b2 = (rx - ox * 0.5, ry - oy * 0.5)
            mx, my = rx + math.cos(a) * L * 0.58, ry + math.sin(a) * L * 0.58
            m1 = (mx + ox * 0.5, my + oy * 0.5); m2 = (mx - ox * 0.5, my - oy * 0.5)
            pygame.draw.polygon(big, edge, [b1, m1, (tx, ty), m2, b2])
            pygame.draw.circle(big, edge, (int(tx), int(ty)), max(1, int(wd * 0.55)))
            pygame.draw.polygon(big, fill, [b1, m1, (tx, ty), m2, b2])
            pygame.draw.circle(big, fill, (int(tx), int(ty)), max(1, int(wd * 0.42)))
            if tip:
                pygame.draw.circle(big, tip, (int(tx), int(ty)), max(1, int(wd * 0.24)))

        # Feathers arc around "straight out to the side" (≈180°), from
        # up-and-out down to down-and-out, so it reads as one side wing.
        n = 7                                   # secondaries (behind)
        for i in range(n):
            t = i / (n - 1)
            feather(150 + t * 70, h * 0.58 * (0.7 + 0.3 * math.sin(math.pi * t)), h * 0.115, FILL, SH)
        n = 8                                   # primaries (front, longest, gold tips)
        for i in range(n):
            t = i / (n - 1)
            feather(142 + t * 82, h * 0.84 * (0.6 + 0.4 * math.sin(math.pi * t)), h * 0.125, WHITE, SH, GOLD)
        n = 5                                   # coverts (small, near the root)
        for i in range(n):
            t = i / (n - 1)
            feather(162 + t * 54, h * 0.32, h * 0.10, WHITE, SH)
    img = _ss(box_w, box_h, fn, 4)
    if mirror:
        img = pygame.transform.flip(img, True, False)
    return img


# ── candidate builders: each draws onto `surf`, returns nothing ──────────────
def build_angel(surf):
    rect = _rect_for(_scaled(_base_pip()))
    # heavenly backlight
    _glow(surf, CX, CY - 6, 96, (255, 250, 220), peak_a=70, layers=7)
    _rays(surf, CX, CY - 6, 86, (255, 245, 200), n=16, a=42)
    # big feathered wings behind body, rooted at the shoulders. Canonical
    # wing sweeps up-LEFT (= left wing); mirror it for the right wing.
    ww, wh = int(rect.w * 0.95), int(rect.h * 1.05)
    lw = _angel_wing(ww, wh, mirror=False)              # Pip's left  (screen left)
    rw = _angel_wing(ww, wh, mirror=True)               # Pip's right (screen right)
    la = _P(rect, 0.42, 0.56)
    surf.blit(lw, (int(la[0] - 0.86 * ww), int(la[1] - 0.90 * wh)))
    ra = _P(rect, 0.58, 0.56)
    surf.blit(rw, (int(ra[0] - 0.14 * ww), int(ra[1] - 0.90 * wh)))
    # ivory + soft-gold recolour of Pip
    pip = _recolor(_scaled(_base_pip()), (255, 248, 236), add=(70, 64, 58))
    surf.blit(pip, rect.topleft)
    # golden sash across the chest
    def sash(big, s):
        w, h = big.get_size()
        pygame.draw.polygon(big, (235, 195, 90),
                            [(0, int(h * 0.2)), (w, int(h * 0.55)), (w, int(h * 0.78)), (0, int(h * 0.43))])
        pygame.draw.line(big, (255, 235, 160), (0, int(h * 0.32)), (w, int(h * 0.66)), int(2 * s))
    _blit_ss(surf, *_P(rect, 0.5, 0.62), int(rect.w * 0.62), int(rect.h * 0.34), sash)
    # halo ring above head
    def halo(big, s):
        w, h = big.get_size()
        pygame.draw.ellipse(big, (255, 240, 160, 80), (int(2 * s), int(2 * s), int(w - 4 * s), int(h - 4 * s)))
        pygame.draw.ellipse(big, (255, 210, 80), (int(3 * s), int(3 * s), int(w - 6 * s), int(h - 6 * s)), int(3 * s))
        pygame.draw.ellipse(big, (255, 252, 220), (int(5 * s), int(4 * s), int(w - 10 * s), int(h - 8 * s)), max(1, int(s)))
    hx, hy = _P(rect, 0.72, 0.06)
    _glow(surf, hx, hy, 26, (255, 235, 150), peak_a=70, layers=4)
    _blit_ss(surf, hx, hy, int(rect.w * 0.5), int(rect.h * 0.2), halo)
    for (fx, fy, r) in ((0.2, 0.2, 5), (0.9, 0.5, 4), (0.15, 0.7, 4), (0.85, 0.85, 5), (0.5, 0.05, 4)):
        _star(surf, *_P(rect, fx, fy), r, (255, 248, 210))


def build_knight(surf):
    base = _scaled(_base_pip())
    rect = _rect_for(base)
    STEEL_OL = (40, 44, 56); STEEL_D = (96, 104, 122); STEEL = (158, 166, 184)
    STEEL_HI = (224, 230, 244); BRASS = (210, 170, 80); HERALD = (176, 52, 50)

    # 1) kite shield BEHIND Pip, peeking out on the tail (left) side
    def shield(big, s):
        w, h = big.get_size(); cxg = w // 2
        out = [(cxg, int(2 * s)), (int(w - 3 * s), int(h * 0.30)), (cxg, int(h - 2 * s)), (int(3 * s), int(h * 0.30))]
        pygame.draw.polygon(big, STEEL_OL, out)
        pygame.draw.polygon(big, STEEL, [(cxg, int(5 * s)), (int(w - 6 * s), int(h * 0.31)), (cxg, int(h - 5 * s)), (int(6 * s), int(h * 0.31))])
        pygame.draw.polygon(big, HERALD, [(cxg, int(9 * s)), (int(w - 9 * s), int(h * 0.33)), (cxg, int(h - 9 * s)), (int(9 * s), int(h * 0.33))])
        pygame.draw.line(big, (235, 228, 210), (cxg, int(11 * s)), (cxg, int(h - 11 * s)), int(3 * s))
        pygame.draw.line(big, (235, 228, 210), (int(11 * s), int(h * 0.40)), (int(w - 11 * s), int(h * 0.40)), int(3 * s))
        pygame.draw.circle(big, STEEL_HI, (cxg, int(h * 0.46)), int(5 * s))
        pygame.draw.circle(big, BRASS, (cxg, int(h * 0.46)), int(3 * s))
        for (rx, ry) in ((0.5, 0.16), (0.2, 0.34), (0.8, 0.34), (0.5, 0.84)):
            pygame.draw.circle(big, BRASS, (int(w * rx), int(h * ry)), int(1.5 * s))
    sw_, sh_ = int(rect.w * 0.60), int(rect.h * 0.88)
    surf.blit(_ss(sw_, sh_, shield), (int(_P(rect, 0.14, 0.54)[0] - sw_ * 0.5), int(_P(rect, 0.14, 0.54)[1] - sh_ * 0.5)))

    # 2) steel-recoloured Pip body (the "armoured" base; stays visible)
    surf.blit(_recolor(base, (150, 160, 182), add=(8, 10, 16)), rect.topleft)

    # 3) curved breastplate fitted to the chest (flatter, not a stack)
    def breast(big, s):
        w, h = big.get_size()
        pygame.draw.ellipse(big, STEEL_OL, (int(1 * s), int(2 * s), int(w - 2 * s), int(h - 3 * s)))
        pygame.draw.ellipse(big, STEEL, (int(3 * s), int(3 * s), int(w - 6 * s), int(h - 6 * s)))
        pygame.draw.ellipse(big, STEEL_HI, (int(6 * s), int(4 * s), int(w * 0.36), int(h * 0.34)))   # shine
        pygame.draw.line(big, STEEL_D, (int(w * 0.5), int(4 * s)), (int(w * 0.5), int(h - 5 * s)), max(1, int(1.5 * s)))  # ridge
        for rx in (0.26, 0.74):
            pygame.draw.circle(big, STEEL_D, (int(w * rx), int(h * 0.3)), int(1.6 * s))
        pygame.draw.circle(big, BRASS, (int(w * 0.5), int(h * 0.58)), int(3 * s))                     # emblem boss
    _blit_ss(surf, *_P(rect, 0.45, 0.62), int(rect.w * 0.52), int(rect.h * 0.30), breast)

    # 4) pauldron on the shoulder (layered lames)
    def pauldron(big, s):
        w, h = big.get_size()
        for i, col in enumerate((STEEL_OL, STEEL_D, STEEL)):
            o = i * 2 * s
            pygame.draw.ellipse(big, col, (int(2 * s + o), int(2 * s + o), int(w - 4 * s - 2 * o), int(h * 0.8 - 2 * o)))
        pygame.draw.arc(big, STEEL_HI, (int(4 * s), int(3 * s), int(w - 8 * s), int(h * 0.7)), math.radians(200), math.radians(340), int(2 * s))
    _blit_ss(surf, *_P(rect, 0.42, 0.45), int(rect.w * 0.34), int(rect.h * 0.24), pauldron)

    # 5) great helm fitted over the head (head ≈ (0.74,0.22))
    def helm(big, s):
        w, h = big.get_size(); cxg = w // 2
        pygame.draw.ellipse(big, STEEL_OL, (int(2 * s), int(3 * s), int(w - 4 * s), int(h * 0.86)))
        pygame.draw.ellipse(big, STEEL, (int(4 * s), int(5 * s), int(w - 8 * s), int(h * 0.82 - 2 * s)))
        pygame.draw.ellipse(big, STEEL_HI, (int(7 * s), int(7 * s), int(w * 0.40), int(h * 0.30)))
        vy = int(h * 0.50)
        pygame.draw.rect(big, STEEL_D, (int(5 * s), vy, int(w - 10 * s), int(h * 0.26)))
        pygame.draw.rect(big, (10, 10, 14), (int(7 * s), vy + int(3 * s), int(w - 14 * s), int(4 * s)))
        for bx in range(4):
            x = int(11 * s + bx * (w - 22 * s) / 3)
            pygame.draw.line(big, STEEL_HI, (x, vy), (x, vy + int(h * 0.26)), max(1, int(s)))
        pygame.draw.rect(big, BRASS, (int(cxg - 2 * s), int(0), int(4 * s), int(5 * s)))               # crest base
        for k, col in enumerate(((130, 30, 38), HERALD, (224, 96, 86))):
            sp = (k - 1) * 2 * s
            pygame.draw.polygon(big, col, [(cxg - int(5 * s) + sp, int(2 * s)), (cxg + int(5 * s) + sp, int(2 * s)), (cxg + sp, int(-12 * s))])
    _blit_ss(surf, *_P(rect, 0.74, 0.20), int(rect.w * 0.48), int(rect.h * 0.50), helm)

    # 6) longsword held to the right, angled
    def sword(big, s):
        w, h = big.get_size()
        pygame.draw.line(big, STEEL_HI, (int(w * 0.3), int(h * 0.95)), (int(w * 0.82), int(h * 0.08)), int(3 * s))
        pygame.draw.line(big, STEEL, (int(w * 0.3), int(h * 0.95)), (int(w * 0.82), int(h * 0.08)), int(1.4 * s))
        pygame.draw.line(big, BRASS, (int(w * 0.16), int(h * 0.84)), (int(w * 0.44), int(h * 1.0)), int(3 * s))   # crossguard
        pygame.draw.circle(big, BRASS, (int(w * 0.24), int(h * 0.94)), int(2.4 * s))                              # pommel
    _blit_ss(surf, *_P(rect, 1.02, 0.5), int(rect.w * 0.46), int(rect.h * 0.85), sword)


def build_bubble(surf):
    base = _scaled(_base_pip())
    rect = _rect_for(base)
    R = int(rect.w * 0.78)
    # back fill + back rim BEHIND Pip
    back = pygame.Surface((R * 2 + 8, R * 2 + 8), pygame.SRCALPHA); c = R + 4
    pygame.draw.circle(back, (110, 195, 255, 50), (c, c), R)
    pygame.draw.circle(back, (150, 220, 255, 80), (c, c), R, 3)
    surf.blit(back, (CX - c, CY - c))
    # faint cool tint on Pip
    surf.blit(_recolor(base, (210, 228, 248), add=(24, 24, 30)).convert_alpha() if False else base, rect.topleft)
    # front shell: layered rims + specular + iridescence + honeycomb energy
    front = pygame.Surface((R * 2 + 8, R * 2 + 8), pygame.SRCALPHA)
    pygame.draw.circle(front, (200, 240, 255, 160), (c, c), R, 3)
    pygame.draw.circle(front, (255, 255, 255, 90), (c, c), R - 4, 1)
    rr = pygame.Rect(c - R, c - R, R * 2, R * 2)
    pygame.draw.arc(front, (255, 255, 255, 210), rr, math.radians(60), math.radians(150), 5)   # top specular
    pygame.draw.arc(front, (255, 255, 255, 110), rr.inflate(-10, -10), math.radians(55), math.radians(120), 3)
    pygame.draw.arc(front, (255, 180, 255, 90), rr.inflate(-6, -6), math.radians(10), math.radians(80), 3)
    pygame.draw.arc(front, (160, 255, 220, 90), rr.inflate(-8, -8), math.radians(200), math.radians(280), 3)
    pygame.draw.arc(front, (255, 245, 160, 80), rr, math.radians(250), math.radians(310), 4)    # bottom caustic
    # faint hex energy cells
    for k in range(8):
        ang = k * math.tau / 8
        hx = c + math.cos(ang) * R * 0.62; hy = c + math.sin(ang) * R * 0.62
        pts = [(hx + math.cos(ang2) * 6, hy + math.sin(ang2) * 6) for ang2 in [math.radians(60 * j - 30) for j in range(6)]]
        pygame.draw.polygon(front, (180, 230, 255, 40), pts, 1)
    surf.blit(front, (CX - c, CY - c))
    for ang in (50, 130, 215, 300, 350):
        _star(surf, CX + math.cos(math.radians(ang)) * R, CY + math.sin(math.radians(ang)) * R, 5, (235, 248, 255))


def build_gold(surf):
    base = _scaled(_base_pip())
    rect = _rect_for(base)
    _glow(surf, CX, CY, 88, (255, 220, 110), peak_a=80, layers=7)
    _rays(surf, CX, CY, 92, (255, 235, 150), n=14, a=46)
    gold = _recolor(base, (240, 188, 70), add=(34, 22, 0))
    # engraved highlight/shadow
    sh = pygame.Surface(gold.get_size(), pygame.SRCALPHA)
    iw, ih = gold.get_size()
    pygame.draw.ellipse(sh, (255, 245, 180, 130), (int(iw * 0.5), int(ih * 0.16), int(iw * 0.22), int(ih * 0.15)))
    pygame.draw.ellipse(sh, (255, 240, 160, 90), (int(iw * 0.32), int(ih * 0.46), int(iw * 0.26), int(ih * 0.16)))
    pygame.draw.ellipse(sh, (150, 105, 25, 90), (int(iw * 0.30), int(ih * 0.66), int(iw * 0.40), int(ih * 0.18)))
    gold.blit(sh, (0, 0))
    surf.blit(gold, rect.topleft)
    # chest gem + filigree
    def gem(big, s):
        w, h = big.get_size(); cxg, cyg = w // 2, h // 2
        pygame.draw.polygon(big, (40, 120, 90), [(cxg, int(2 * s)), (int(w - 2 * s), cyg), (cxg, int(h - 2 * s)), (int(2 * s), cyg)])
        pygame.draw.polygon(big, (90, 220, 170), [(cxg, int(5 * s)), (int(w - 5 * s), cyg), (cxg, int(h - 5 * s)), (int(5 * s), cyg)])
        pygame.draw.circle(big, (235, 255, 245), (cxg - s, cyg - s), int(1.6 * s))
    _blit_ss(surf, *_P(rect, 0.46, 0.6), int(rect.w * 0.2), int(rect.h * 0.2), gem)
    for (fx, fy, r) in ((0.2, 0.15, 6), (0.85, 0.3, 5), (0.1, 0.55, 4), (0.9, 0.7, 6), (0.5, 0.0, 5), (0.7, 0.92, 4)):
        _star(surf, *_P(rect, fx, fy), r, (255, 250, 210))


def build_aegis(surf):
    base = _scaled(_base_pip())
    rect = _rect_for(base)
    _glow(surf, CX, CY, 84, (80, 175, 255), peak_a=80, layers=6)
    surf.blit(_recolor(base, (200, 224, 248), add=(18, 22, 34)), rect.topleft)
    # large layered hex shield in front
    hx, hy = _P(rect, 0.58, 0.52); R = int(rect.w * 0.62)

    def hexa(big, s):
        w, h = big.get_size(); cc = (w // 2, h // 2)
        def hexpts(rad):
            return [(cc[0] + rad * s * math.cos(math.radians(60 * k - 30)),
                     cc[1] + rad * s * math.sin(math.radians(60 * k - 30))) for k in range(6)]
        fill = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(fill, (70, 165, 255, 70), hexpts(R - 1)); big.blit(fill, (0, 0))
        pygame.draw.polygon(big, (150, 220, 255, 235), hexpts(R - 1), int(2.5 * s))
        pygame.draw.polygon(big, (200, 240, 255, 170), hexpts(R - 6), max(1, int(s)))
        pygame.draw.polygon(big, (120, 200, 255, 120), hexpts(R - 12), max(1, int(s)))
        # honeycomb cells
        for ring in (R * 0.34, R * 0.62):
            for k in range(6):
                ang = math.radians(60 * k)
                ccx = cc[0] + math.cos(ang) * ring * s; ccy = cc[1] + math.sin(ang) * ring * s
                cell = [(ccx + 4 * s * math.cos(math.radians(60 * j - 30)),
                         ccy + 4 * s * math.sin(math.radians(60 * j - 30))) for j in range(6)]
                pygame.draw.polygon(big, (170, 225, 255, 70), cell, 1)
        # runes around centre
        rc = (225, 248, 255)
        pygame.draw.lines(big, rc, False, [(cc[0] - int(7 * s), cc[1] - int(5 * s)), (cc[0], cc[1] - int(11 * s)), (cc[0] + int(7 * s), cc[1] - int(5 * s))], max(1, int(s)))
        pygame.draw.circle(big, rc, cc, int(4 * s), max(1, int(s)))
        pygame.draw.line(big, rc, (cc[0], cc[1] + int(4 * s)), (cc[0], cc[1] + int(10 * s)), max(1, int(s)))
        pygame.draw.arc(big, rc, (cc[0] - int(9 * s), cc[1] - int(9 * s), int(18 * s), int(18 * s)), math.radians(20), math.radians(160), max(1, int(s)))
    _blit_ss(surf, hx, hy, R * 2 + 8, R * 2 + 8, hexa)
    # corner emitter sparks
    for k in range(6):
        ang = math.radians(60 * k - 30)
        _star(surf, hx + math.cos(ang) * R, hy + math.sin(ang) * R, 4, (210, 245, 255))


CANDIDATES = [
    ("knight", "1  KNIGHT (full plate + shield + sword)", build_knight),
    ("angel",  "2  GUARDIAN ANGEL (ivory + wings + halo)", build_angel),
    ("bubble", "3  FORCE-FIELD BUBBLE", build_bubble),
    ("gold",   "4  GOLDEN GUARDIAN", build_gold),
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
