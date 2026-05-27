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
# Knight chest-shield placement (fx, fy, w-frac, h-frac of the nominal rect).
# Overridable by tools/render_knight_shield_pos.py to compare placements.
_SHIELD_POS = (0.56, 0.63, 0.34, 0.42)

# Knight armour FINISH — drives the custom-drawn cuirass/helm/wing/sword.
# Overridable by tools/render_knight_custom.py.  ol=outline/deep shadow,
# lo=shaded sides, mid=base metal, hi=specular.  surcoat=(left,right) tinctures
# for a cloth tabard, or None.
ARMOR = {
    "ol": (20, 24, 34), "lo": (74, 84, 106), "mid": (150, 162, 186), "hi": (236, 244, 255),
    "brass": (212, 178, 102), "brass_hi": (255, 234, 172),
    "fluted": False, "surcoat": None, "filigree": False,
}


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


def _vgrad(w, h, top, bot):
    """A vertical gradient surface (top colour → bottom colour)."""
    g = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(0, h, 2):
        t = i / max(1, h - 1)
        col = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        pygame.draw.rect(g, col, (0, i, w, 2))
    return g


def _poly_grad(big, pts, top, bot):
    """Fill a polygon with a vertical gradient (clipped to the polygon)."""
    w, h = big.get_size()
    g = _vgrad(w, h, top, bot)
    m = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(m, (255, 255, 255, 255), pts)
    g.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(g, (0, 0))


def _pip_keep(base):
    """Keep only Pip's identity bits — head+beak+aviators, tail, talons — so the
    custom armour can replace the body without a recoloured parrot blob showing."""
    w, h = base.get_size()
    keep = base.copy()
    m = pygame.Surface((w, h), pygame.SRCALPHA)
    WH = (255, 255, 255, 255)
    pygame.draw.ellipse(m, WH, (int(w * -0.03), int(h * 0.26), int(w * 0.37), int(h * 0.46)))  # tail
    pygame.draw.ellipse(m, WH, (int(w * 0.34), int(h * 0.66), int(w * 0.26), int(h * 0.26)))  # talons
    keep.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return keep


def build_knight(char, nom, fidx):
    """Pip as a knight — drawn as a custom armoured figure (sculpted cuirass +
    armoured flapping wing + open sallet + K7 shield + sword), keeping Pip's
    head/beak/tail/talons so it still reads as Pip."""
    base = _base_body(fidx)
    brect = base.get_rect(center=nom.center)
    OL = ARMOR["ol"]; LO = ARMOR["lo"]; MID = ARMOR["mid"]; HI = ARMOR["hi"]
    BRASS = ARMOR["brass"]; BRASS_HI = ARMOR["brass_hi"]; CRIM = (160, 44, 48)
    SURCOAT = ARMOR.get("surcoat"); FLUTED = ARMOR.get("fluted"); FILI = ARMOR.get("filigree")
    HELM = ARMOR.get("helm", "greathelm"); WEAPON = ARMOR.get("weapon", "sword")
    SHIELD = ARMOR.get("shield", "heater_k7"); CAPE = ARMOR.get("cape"); PLUME = ARMOR.get("plume", CRIM)
    LIT = (int((MID[0] + HI[0]) / 2), int((MID[1] + HI[1]) / 2), int((MID[2] + HI[2]) / 2))
    MIDMIX = (int((LO[0] + MID[0]) / 2), int((LO[1] + MID[1]) / 2), int((LO[2] + MID[2]) / 2))

    # ── optional flowing CAPE, behind everything ───────────────────────────────
    if CAPE:
        cdk = tuple(max(0, int(c * 0.55)) for c in CAPE); chi = tuple(min(255, int(c * 1.3 + 26)) for c in CAPE)
        def cape(big, s):
            w, h = big.get_size()
            shape = [(0.62 * w, 0.06 * h), (0.78 * w, 0.30 * h), (0.70 * w, 0.62 * h), (0.82 * w, 0.96 * h),
                     (0.54 * w, 0.86 * h), (0.30 * w, 0.96 * h), (0.16 * w, 0.66 * h), (0.30 * w, 0.20 * h)]
            pygame.draw.polygon(big, cdk, shape)
            pygame.draw.polygon(big, CAPE, [(x + (0.5 * w - x) * 0.12, y * 0.99) for (x, y) in shape])
            for fx in (0.34, 0.48, 0.62):                      # folds
                pygame.draw.line(big, cdk, (fx * w, 0.18 * h), (fx * w - 0.04 * w, 0.92 * h), max(2, int(2 * s)))
                pygame.draw.line(big, chi, (fx * w + 0.03 * w, 0.18 * h), (fx * w - 0.01 * w, 0.9 * h), max(1, int(s)))
            pygame.draw.line(big, BRASS, (0.30 * w, 0.14 * h), (0.62 * w, 0.10 * h), max(2, int(2.2 * s)))  # clasp band
        _blit_ss(char, *_P(nom, 0.46, 0.64), int(nom.w * 0.72), int(nom.h * 0.74), cape, scale=5)

    # ── Pip's identity bits behind the armour ──────────────────────────────────
    char.blit(_pip_keep(base), brect.topleft)

    # ── sculpted CUIRASS = the main armoured torso (custom, not a recolour) ─────
    def cuirass(big, s):
        w, h = big.get_size()
        # breastplate silhouette — wide chest tapering to the waist
        body_pts = [(0.22 * w, 0.18 * h), (0.78 * w, 0.18 * h), (0.92 * w, 0.42 * h),
                    (0.74 * w, 0.74 * h), (0.50 * w, 0.84 * h), (0.26 * w, 0.74 * h), (0.08 * w, 0.42 * h)]
        pygame.draw.polygon(big, OL, body_pts)                       # outline
        inner = [(x + (0.5 * w - x) * 0.10, y + (0.5 * h - y) * 0.10) for (x, y) in body_pts]
        _poly_grad(big, inner, HI, LO)                               # lit-from-top gradient
        # side shading for cylindrical volume
        pygame.draw.polygon(big, LO, [(0.08 * w, 0.42 * h), (0.20 * w, 0.30 * h), (0.20 * w, 0.66 * h), (0.16 * w, 0.62 * h)])
        pygame.draw.polygon(big, LO, [(0.92 * w, 0.42 * h), (0.80 * w, 0.30 * h), (0.80 * w, 0.66 * h), (0.84 * w, 0.62 * h)])
        # central keel ridge
        pygame.draw.line(big, HI, (0.5 * w, 0.22 * h), (0.5 * w, 0.78 * h), max(1, int(1.6 * s)))
        pygame.draw.line(big, LO, (0.5 * w + int(1.4 * s), 0.26 * h), (0.5 * w + int(1.4 * s), 0.74 * h), max(1, int(s)))
        if FLUTED:
            for fx in (0.30, 0.40, 0.60, 0.70):
                pygame.draw.line(big, LO, (fx * w, 0.26 * h), (fx * w, 0.74 * h), max(1, int(1.2 * s)))
                pygame.draw.line(big, HI, (fx * w + int(1.1 * s), 0.27 * h), (fx * w + int(1.1 * s), 0.72 * h), max(1, int(0.7 * s)))
        # specular bloom, top-left
        sp = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(sp, (*HI, 120), (int(0.22 * w), int(0.18 * h), int(0.34 * w), int(0.30 * h)))
        big.blit(sp, (0, 0))
        # gorget collar
        pygame.draw.ellipse(big, OL, (int(0.24 * w), int(0.04 * h), int(0.52 * w), int(0.26 * h)))
        pygame.draw.ellipse(big, MID, (int(0.27 * w), int(0.06 * h), int(0.46 * w), int(0.18 * h)))
        pygame.draw.arc(big, HI, (int(0.27 * w), int(0.05 * h), int(0.46 * w), int(0.2 * h)), math.radians(196), math.radians(344), max(1, int(1.2 * s)))
        # fauld lames at the waist (each a sculpted band w/ a top highlight)
        for i in range(3):
            ly = (0.70 + i * 0.075) * h
            band = [(0.22 * w, ly), (0.78 * w, ly), (0.70 * w, ly + 0.075 * h), (0.30 * w, ly + 0.075 * h)]
            pygame.draw.polygon(big, LO, band)
            pygame.draw.line(big, OL, (0.22 * w, ly), (0.78 * w, ly), max(1, int(0.9 * s)))
            pygame.draw.line(big, HI, (0.28 * w, ly + int(1.2 * s)), (0.72 * w, ly + int(1.2 * s)), max(1, int(0.8 * s)))
        # surcoat / tabard (cloth over the plate, per-pale in the K7 tinctures)
        if SURCOAT:
            cl, cr = SURCOAT
            tab = [(0.34 * w, 0.22 * h), (0.66 * w, 0.22 * h), (0.62 * w, 0.86 * h), (0.50 * w, 0.92 * h), (0.38 * w, 0.86 * h)]
            tmp = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.polygon(tmp, cl, [(0.34 * w, 0.22 * h), (0.5 * w, 0.22 * h), (0.5 * w, 0.92 * h), (0.38 * w, 0.86 * h)])
            pygame.draw.polygon(tmp, cr, [(0.5 * w, 0.22 * h), (0.66 * w, 0.22 * h), (0.62 * w, 0.86 * h), (0.5 * w, 0.92 * h)])
            mm = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.polygon(mm, (255, 255, 255, 255), tab)
            tmp.blit(mm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            big.blit(tmp, (0, 0))
            for fx in (0.42, 0.5, 0.58):                              # cloth folds
                pygame.draw.line(big, (0, 0, 0, 60), (fx * w, 0.26 * h), (fx * w, 0.84 * h), max(1, int(0.8 * s)))
            pygame.draw.line(big, BRASS, (0.34 * w, 0.22 * h), (0.66 * w, 0.22 * h), max(1, int(1.4 * s)))
        # gilt filigree + brass studs
        if FILI:
            for fy in (0.40, 0.56):
                pygame.draw.arc(big, BRASS, (int(0.24 * w), int(fy * h), int(0.52 * w), int(0.16 * h)), math.radians(200), math.radians(340), max(1, int(1.3 * s)))
            pygame.draw.line(big, BRASS, (0.5 * w, 0.24 * h), (0.5 * w, 0.7 * h), max(1, int(1.3 * s)))
        for (rx, ry) in ((0.24, 0.24), (0.76, 0.24)):                 # shoulder studs
            pygame.draw.circle(big, BRASS, (int(rx * w), int(ry * h)), max(1, int(1.5 * s)))
            pygame.draw.circle(big, BRASS_HI, (int(rx * w) - int(s), int(ry * h) - int(s)), max(1, int(0.8 * s)))
    _blit_ss(char, *_P(nom, 0.48, 0.58), int(nom.w * 0.70), int(nom.h * 0.66), cuirass, scale=6)

    # ── armoured WING (replaces Pip's wing) — flaps with the frame ─────────────
    def armwing(big, s):
        w, h = big.get_size()
        root = (0.86 * w, 0.88 * h)
        tips = [(0.10, 0.18), (0.07, 0.36), (0.12, 0.54), (0.22, 0.68), (0.36, 0.80)]
        for i, (tfx, tfy) in enumerate(tips):
            tip = (tfx * w, tfy * h)
            dx, dy = tip[0] - root[0], tip[1] - root[1]
            ln = math.hypot(dx, dy) or 1; ux, uy = dx / ln, dy / ln; px, py = -uy, ux
            bw = (0.085 - 0.010 * i) * w
            plate = [(root[0] + px * bw, root[1] + py * bw), (root[0] - px * bw, root[1] - py * bw),
                     (tip[0] - px * 0.03 * w, tip[1] - py * 0.03 * w), (tip[0] + px * 0.03 * w, tip[1] + py * 0.03 * w)]
            pygame.draw.polygon(big, OL, plate)
            plate2 = [(root[0] + px * (bw - 1.4 * s), root[1] + py * (bw - 1.4 * s)), (root[0] - px * (bw - 1.4 * s), root[1] - py * (bw - 1.4 * s)),
                      (tip[0] - px * 0.02 * w, tip[1] - py * 0.02 * w), (tip[0] + px * 0.02 * w, tip[1] + py * 0.02 * w)]
            pygame.draw.polygon(big, MID if i % 2 == 0 else LO, plate2)
            pygame.draw.line(big, HI, (root[0] - px * (bw - 2 * s), root[1] - py * (bw - 2 * s)), tip, max(1, int(0.9 * s)))
        # spaulder cap over the root — layered curved lames (not a plain ball)
        rx0, ry0 = int(root[0]), int(root[1])
        for j, (rw, rh, col) in enumerate(((0.24, 0.20, OL), (0.225, 0.185, LO), (0.20, 0.165, MID))):
            yo = int(j * 1.4 * s)
            pygame.draw.ellipse(big, col, (int(rx0 - rw * w), int(ry0 - rh * w - yo), int(2 * rw * w), int(2 * rh * w)))
        for j in range(3):                                                       # lame seams + highlights
            ay = int(ry0 - 0.10 * w + j * 0.08 * w)
            pygame.draw.arc(big, OL, (int(rx0 - 0.21 * w), int(ay - 0.10 * w), int(0.42 * w), int(0.2 * w)), math.radians(200), math.radians(340), max(1, int(0.9 * s)))
            pygame.draw.arc(big, HI, (int(rx0 - 0.21 * w), int(ay - 0.10 * w) - int(s), int(0.42 * w), int(0.2 * w)), math.radians(210), math.radians(330), max(1, int(0.7 * s)))
        pygame.draw.circle(big, BRASS, (rx0, int(ry0 - 0.12 * w)), max(1, int(1.6 * s)))
    nw2, nh2 = int(nom.w * 0.66), int(nom.h * 0.70)
    awing = _ss(nw2, nh2, armwing, 5)
    rot, tl = _rotate_about(awing, (0.86, 0.88), _P(nom, 0.52, 0.50), _FLAP_DEG[fidx])
    char.blit(rot, tl)

    # ── SHIELD — distinct shape + heraldry per design ──────────────────────────
    def _clip(big, pts):
        w, h = big.get_size()
        m = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(m, (255, 255, 255, 255), pts)
        return m

    def sh_heater_k7(big, s):                                  # quarterly gules/or
        w, h = big.get_size(); cxg = w // 2
        GUL = (170, 46, 50); GOLD = (226, 182, 72)
        outer = [(3 * s, 3 * s), (w - 3 * s, 3 * s), (w - 3 * s, h * 0.46), (cxg, h - 3 * s), (3 * s, h * 0.46)]
        field = [(8 * s, 8 * s), (w - 8 * s, 8 * s), (w - 8 * s, h * 0.44), (cxg, h - 9 * s), (8 * s, h * 0.44)]
        pygame.draw.polygon(big, OL, outer)
        pygame.draw.polygon(big, MID, [(6 * s, 6 * s), (w - 6 * s, 6 * s), (w - 6 * s, h * 0.45), (cxg, h - 7 * s), (6 * s, h * 0.45)])
        qy = h * 0.4
        tmp = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(tmp, GUL, (0, 0, int(cxg), int(qy)))
        pygame.draw.rect(tmp, GOLD, (int(cxg), 0, int(w - cxg), int(qy)))
        pygame.draw.rect(tmp, GOLD, (0, int(qy), int(cxg), int(h - qy)))
        pygame.draw.rect(tmp, GUL, (int(cxg), int(qy), int(w - cxg), int(h - qy)))
        tmp.blit(_clip(big, field), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        big.blit(tmp, (0, 0))
        pygame.draw.line(big, HI, (int(8 * s), int(8 * s)), (int(w - 8 * s), int(8 * s)), max(1, int(1.4 * s)))

    def sh_round(big, s):                                      # azure, a cross or
        w, h = big.get_size(); c = (w // 2, h // 2); r = int(w * 0.46)
        AZ = (52, 86, 168); GOLD = (230, 192, 86)
        pygame.draw.circle(big, OL, c, r)
        pygame.draw.circle(big, MID, c, r - int(2.5 * s))
        pygame.draw.circle(big, AZ, c, r - int(5 * s))
        pygame.draw.line(big, GOLD, (c[0], c[1] - r + int(7 * s)), (c[0], c[1] + r - int(7 * s)), max(2, int(4 * s)))
        pygame.draw.line(big, GOLD, (c[0] - r + int(7 * s), c[1]), (c[0] + r - int(7 * s), c[1]), max(2, int(4 * s)))
        pygame.draw.circle(big, BRASS, c, int(5 * s)); pygame.draw.circle(big, BRASS_HI, (c[0] - int(s), c[1] - int(s)), int(2 * s))
        for a in range(0, 360, 45):
            rx = int(c[0] + (r - int(3 * s)) * math.cos(math.radians(a))); ry = int(c[1] + (r - int(3 * s)) * math.sin(math.radians(a)))
            pygame.draw.circle(big, BRASS, (rx, ry), max(1, int(1.6 * s)))
        pygame.draw.arc(big, HI, (c[0] - r + int(3 * s), c[1] - r + int(3 * s), 2 * (r - int(3 * s)), 2 * (r - int(3 * s))), math.radians(205), math.radians(330), max(1, int(1.4 * s)))

    def sh_bouche(big, s):                                     # sable, a chevron or (lance-rest notch)
        w, h = big.get_size(); cxg = w // 2
        SAB = (40, 42, 52); GOLD = (230, 192, 86)
        outer = [(3 * s, 3 * s), (w * 0.62, 3 * s), (w * 0.62, h * 0.12), (w - 3 * s, h * 0.12), (w - 3 * s, h * 0.46), (cxg, h - 3 * s), (3 * s, h * 0.46)]
        field = [(8 * s, 8 * s), (w * 0.6, 8 * s), (w * 0.6, h * 0.15), (w - 8 * s, h * 0.15), (w - 8 * s, h * 0.44), (cxg, h - 9 * s), (8 * s, h * 0.44)]
        pygame.draw.polygon(big, OL, outer)
        pygame.draw.polygon(big, MID, field)
        tmp = pygame.Surface((w, h), pygame.SRCALPHA); tmp.fill(SAB)
        tmp.blit(_clip(big, field), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        big.blit(tmp, (0, 0))
        pygame.draw.lines(big, GOLD, False, [(int(10 * s), int(h * 0.6)), (cxg, int(h * 0.38)), (int(w - 10 * s), int(h * 0.6))], max(3, int(5 * s)))
        pygame.draw.line(big, HI, (int(8 * s), int(8 * s)), (int(w * 0.58), int(8 * s)), max(1, int(1.4 * s)))

    def sh_kite(big, s):                                       # vert, a bend argent
        w, h = big.get_size()
        VERT = (54, 132, 78); ARG = (228, 232, 238)
        outer = [(int(w * 0.5), int(2 * s)), (int(w - 4 * s), int(h * 0.22)), (int(w - 8 * s), int(h * 0.6)), (int(w * 0.5), int(h - 3 * s)), (int(8 * s), int(h * 0.6)), (int(4 * s), int(h * 0.22))]
        field = [(int(w * 0.5), int(7 * s)), (int(w - 9 * s), int(h * 0.24)), (int(w - 12 * s), int(h * 0.58)), (int(w * 0.5), int(h - 8 * s)), (int(12 * s), int(h * 0.58)), (int(9 * s), int(h * 0.24))]
        pygame.draw.polygon(big, OL, outer)
        pygame.draw.polygon(big, MID, field)
        tmp = pygame.Surface((w, h), pygame.SRCALPHA); tmp.fill(VERT)
        pygame.draw.line(tmp, ARG, (int(w * 0.18), int(h * 0.1)), (int(w * 0.82), int(h * 0.8)), max(3, int(6 * s)))
        tmp.blit(_clip(big, field), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        big.blit(tmp, (0, 0))
        pygame.draw.arc(big, HI, (int(8 * s), int(7 * s), int(w - 16 * s), int(h - 14 * s)), math.radians(120), math.radians(210), max(1, int(1.4 * s)))

    def sh_heater_saltire(big, s):                             # sable, a saltire argent
        w, h = big.get_size(); cxg = w // 2
        SAB = (38, 40, 50); ARG = (228, 232, 238)
        outer = [(3 * s, 3 * s), (w - 3 * s, 3 * s), (w - 3 * s, h * 0.46), (cxg, h - 3 * s), (3 * s, h * 0.46)]
        field = [(8 * s, 8 * s), (w - 8 * s, 8 * s), (w - 8 * s, h * 0.44), (cxg, h - 9 * s), (8 * s, h * 0.44)]
        pygame.draw.polygon(big, OL, outer)
        pygame.draw.polygon(big, MID, [(6 * s, 6 * s), (w - 6 * s, 6 * s), (w - 6 * s, h * 0.45), (cxg, h - 7 * s), (6 * s, h * 0.45)])
        tmp = pygame.Surface((w, h), pygame.SRCALPHA); tmp.fill(SAB)
        pygame.draw.line(tmp, ARG, (int(10 * s), int(10 * s)), (int(w - 10 * s), int(h * 0.5)), max(3, int(5 * s)))
        pygame.draw.line(tmp, ARG, (int(w - 10 * s), int(10 * s)), (int(10 * s), int(h * 0.5)), max(3, int(5 * s)))
        tmp.blit(_clip(big, field), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        big.blit(tmp, (0, 0))
        pygame.draw.line(big, HI, (int(8 * s), int(8 * s)), (int(w - 8 * s), int(8 * s)), max(1, int(1.4 * s)))

    SHIELDS = {"heater_k7": sh_heater_k7, "round": sh_round, "bouche": sh_bouche,
               "kite": sh_kite, "heater_saltire": sh_heater_saltire}
    sfx, sfy, swf, shf = _SHIELD_POS
    _blit_ss(char, *_P(nom, sfx, sfy), int(nom.w * swf), int(nom.h * shf), SHIELDS.get(SHIELD, sh_heater_k7))

    # ── HELM — distinct type per design, all in 3/4 view facing right ──────────
    def _plume(big, s, sx, sy, col):
        clo = tuple(max(0, int(c * 0.6)) for c in col); chi = tuple(min(255, int(c * 1.3 + 30)) for c in col)
        sock = (int(sx), int(sy))
        pygame.draw.circle(big, BRASS, sock, int(2.4 * s))
        pygame.draw.circle(big, BRASS_HI, (sock[0] - int(0.8 * s), sock[1] - int(0.8 * s)), max(1, int(s)))
        for c, off in ((clo, 0), (col, int(2 * s)), (chi, int(4 * s))):
            top = _qbez(sock, (sock[0] - int(12 * s), sock[1] - int(22 * s)), (sock[0] - int(34 * s), sock[1] - int(2 * s)), 20)
            bot = _qbez(sock, (sock[0] - int(7 * s), sock[1] - int(9 * s)), (sock[0] - int(28 * s), sock[1] + int(14 * s)), 20)
            pygame.draw.polygon(big, c, [(x - off, y) for (x, y) in top] + [(x - off, y) for (x, y) in reversed(bot)])

    def hm_greathelm(big, s):                                  # iconic crusader bucket + cross
        w, h = big.get_size()
        def P(a, b): return (int(w * a), int(h * b))
        lw = lambda k: max(1, int(k * s)); DARK = (6, 7, 11)
        pygame.draw.polygon(big, OL, [P(0.22, 0.26), P(0.54, 0.22), P(0.54, 0.80), P(0.24, 0.74), P(0.20, 0.40)])
        pygame.draw.polygon(big, LO, [P(0.25, 0.29), P(0.52, 0.255), P(0.52, 0.76), P(0.27, 0.71), P(0.24, 0.41)])
        pygame.draw.ellipse(big, OL, (int(0.20 * w), int(0.12 * h), int(0.64 * w), int(0.24 * h)))
        pygame.draw.ellipse(big, MIDMIX, (int(0.23 * w), int(0.135 * h), int(0.58 * w), int(0.19 * h)))
        pygame.draw.ellipse(big, LIT, (int(0.28 * w), int(0.15 * h), int(0.26 * w), int(0.10 * h)))
        pygame.draw.polygon(big, OL, [P(0.54, 0.22), P(0.86, 0.28), P(0.86, 0.74), P(0.54, 0.80)])
        _poly_grad(big, [P(0.555, 0.245), P(0.845, 0.30), P(0.845, 0.72), P(0.555, 0.775)], LIT, MIDMIX)
        pygame.draw.line(big, HI, P(0.57, 0.25), P(0.57, 0.78), lw(1.0))
        pygame.draw.rect(big, DARK, (int(0.56 * w), int(0.40 * h), int(0.29 * w), int(0.045 * h)))
        for r in range(2):
            for c in range(4):
                pygame.draw.circle(big, DARK, P(0.60 + c * 0.06, 0.58 + r * 0.07), lw(0.8))
        pygame.draw.line(big, BRASS, P(0.70, 0.24), P(0.70, 0.78), lw(2.4))
        pygame.draw.line(big, BRASS, P(0.55, 0.50), P(0.86, 0.50), lw(2.4))
        pygame.draw.line(big, BRASS_HI, P(0.69, 0.26), P(0.69, 0.76), lw(0.9))
        pygame.draw.line(big, BRASS_HI, P(0.56, 0.49), P(0.85, 0.49), lw(0.9))
        pygame.draw.line(big, OL, P(0.24, 0.74), P(0.86, 0.74), lw(1.4))
        _plume(big, s, 0.34 * w, 0.12 * h, PLUME)

    def hm_frogmouth(big, s):                                  # jousting frog-mouth helm
        w, h = big.get_size()
        def P(a, b): return (int(w * a), int(h * b))
        lw = lambda k: max(1, int(k * s)); DARK = (6, 7, 11)
        # bulky rounded barrel
        pygame.draw.ellipse(big, OL, (int(0.18 * w), int(0.16 * h), int(0.68 * w), int(0.62 * h)))
        _poly_grad(big, [P(0.24, 0.22), P(0.84, 0.26), P(0.86, 0.66), P(0.30, 0.74), P(0.20, 0.44)], LIT, LO)
        pygame.draw.ellipse(big, HI, (int(0.26 * w), int(0.22 * h), int(0.24 * w), int(0.12 * h)))
        # the protruding lower lip (frog-mouth) + the upward eye-slit between
        pygame.draw.polygon(big, OL, [P(0.46, 0.52), P(0.90, 0.50), P(0.90, 0.70), P(0.46, 0.70)])
        pygame.draw.polygon(big, MIDMIX, [P(0.48, 0.55), P(0.88, 0.535), P(0.88, 0.67), P(0.48, 0.67)])
        pygame.draw.rect(big, DARK, (int(0.50 * w), int(0.475 * h), int(0.40 * w), int(0.05 * h)))      # vision slit
        for (yb, col) in ((0.38, BRASS), (0.70, BRASS)):                                                # reinforcing bands
            pygame.draw.line(big, col, P(0.22, yb), P(0.86, yb), lw(2.0))
            pygame.draw.line(big, BRASS_HI, P(0.24, yb - 0.012), P(0.84, yb - 0.012), lw(0.8))
        for (rx, ry) in ((0.30, 0.38), (0.78, 0.38), (0.30, 0.70), (0.80, 0.70)):
            pygame.draw.circle(big, BRASS, P(rx, ry), lw(1.2))
        _plume(big, s, 0.36 * w, 0.16 * h, PLUME)

    def hm_houndskull(big, s):                                 # pig-faced bascinet (pointed snout)
        w, h = big.get_size()
        def P(a, b): return (int(w * a), int(h * b))
        lw = lambda k: max(1, int(k * s)); DARK = (6, 7, 11)
        dome = (int(0.16 * w), int(0.10 * h), int(0.56 * w), int(0.58 * h))
        for i, col in enumerate([OL, LO, MIDMIX, MID, LIT]):
            ins = int(i * 1.7 * s)
            pygame.draw.ellipse(big, col, (dome[0] + ins, dome[1] + ins, dome[2] - 2 * ins, dome[3] - 2 * ins))
        pygame.draw.ellipse(big, HI, (int(0.22 * w), int(0.16 * h), int(0.18 * w), int(0.13 * h)))
        # conical snout visor pointing right
        snout = [P(0.50, 0.34), P(0.70, 0.40), P(0.94, 0.54), P(0.70, 0.64), P(0.50, 0.66)]
        pygame.draw.polygon(big, OL, snout)
        pygame.draw.polygon(big, MIDMIX, [P(0.52, 0.38), P(0.69, 0.43), P(0.86, 0.54), P(0.69, 0.61), P(0.52, 0.63)])
        pygame.draw.line(big, HI, P(0.53, 0.39), P(0.85, 0.54), lw(1.0))
        pygame.draw.line(big, DARK, P(0.54, 0.47), P(0.80, 0.515), lw(2.0))                              # eye-slit
        for k in range(4):
            pygame.draw.circle(big, DARK, P(0.60 + k * 0.06, 0.585), lw(0.8))                            # snout breaths
        _plume(big, s, 0.30 * w, 0.10 * h, PLUME)

    def hm_winged(big, s):                                     # bascinet with a heraldic WING crest
        w, h = big.get_size()
        def P(a, b): return (int(w * a), int(h * b))
        lw = lambda k: max(1, int(k * s)); DARK = (6, 7, 11)
        # crest wings rising from the crown (drawn first, behind the dome)
        for sgn, x0, scale in ((-1, 0.40, 1.0), (1, 0.58, 0.86)):
            base = P(x0, 0.34)
            lead = _qbez(base, (base[0] + sgn * int(0.06 * w), base[1] - int(0.30 * h)), (base[0] + sgn * int(0.26 * w), base[1] - int(0.14 * h)), 18)
            trail = _qbez((base[0] + sgn * int(0.26 * w), base[1] - int(0.14 * h)), (base[0] + sgn * int(0.16 * w), base[1] + int(0.02 * h)), base, 18)
            pygame.draw.polygon(big, OL, lead + trail)
            pygame.draw.polygon(big, LIT, [(x + (base[0] - x) * 0.16, y + (base[1] - y) * 0.10) for (x, y) in lead + trail])
            for fk in range(3):
                fb = lead[5 + fk * 4]
                pygame.draw.line(big, BRASS, fb, (fb[0] + sgn * int(0.05 * w), fb[1] + int(0.04 * h)), lw(0.9))
        # rounded bascinet dome
        dome = (int(0.24 * w), int(0.16 * h), int(0.50 * w), int(0.54 * h))
        for i, col in enumerate([OL, LO, MIDMIX, MID, LIT]):
            ins = int(i * 1.6 * s)
            pygame.draw.ellipse(big, col, (dome[0] + ins, dome[1] + ins, dome[2] - 2 * ins, dome[3] - 2 * ins))
        pygame.draw.ellipse(big, HI, (int(0.30 * w), int(0.22 * h), int(0.16 * w), int(0.12 * h)))
        # short visor + eye-slit, facing right
        pygame.draw.polygon(big, OL, [P(0.46, 0.40), P(0.74, 0.44), P(0.80, 0.56), P(0.66, 0.62), P(0.46, 0.60)])
        pygame.draw.polygon(big, MIDMIX, [P(0.48, 0.43), P(0.72, 0.465), P(0.76, 0.55), P(0.48, 0.575)])
        pygame.draw.line(big, DARK, P(0.50, 0.49), P(0.74, 0.52), lw(2.2))
        pygame.draw.line(big, BRASS, P(0.30, 0.30), P(0.66, 0.40), lw(1.4))                              # brow trim
        _plume(big, s, 0.50 * w, 0.16 * h, PLUME)

    def hm_horned(big, s):                                     # spiked sallet + bevor (black-knight)
        w, h = big.get_size()
        def P(a, b): return (int(w * a), int(h * b))
        lw = lambda k: max(1, int(k * s)); DARK = (6, 7, 11)
        # horns rising from the sides (behind dome)
        for sgn, x0 in ((-1, 0.36), (1, 0.62)):
            tip = (int(x0 * w + sgn * 0.16 * w), int(0.04 * h)); base = P(x0, 0.34)
            curve = _qbez(base, (int(x0 * w + sgn * 0.02 * w), int(0.14 * h)), tip, 14)
            pygame.draw.lines(big, OL, False, curve, lw(4.2))
            pygame.draw.lines(big, MID, False, curve, lw(2.0))
            pygame.draw.lines(big, HI, False, [(x - int(s), y) for (x, y) in curve], lw(0.8))
        # sallet dome with a back tail
        pygame.draw.polygon(big, OL, [P(0.22, 0.34), P(0.46, 0.40), P(0.18, 0.72), P(0.06, 0.56)])      # tail
        pygame.draw.polygon(big, LO, [P(0.25, 0.37), P(0.43, 0.42), P(0.21, 0.66), P(0.12, 0.55)])
        dome = (int(0.20 * w), int(0.14 * h), int(0.56 * w), int(0.52 * h))
        for i, col in enumerate([OL, LO, MIDMIX, MID, LIT]):
            ins = int(i * 1.6 * s)
            pygame.draw.ellipse(big, col, (dome[0] + ins, dome[1] + ins, dome[2] - 2 * ins, dome[3] - 2 * ins))
        pygame.draw.ellipse(big, HI, (int(0.28 * w), int(0.20 * h), int(0.16 * w), int(0.11 * h)))
        pygame.draw.line(big, DARK, P(0.48, 0.46), P(0.78, 0.50), lw(2.4))                               # eye-slit
        # bevor (chin guard) lower-right
        pygame.draw.polygon(big, OL, [P(0.46, 0.54), P(0.82, 0.56), P(0.74, 0.78), P(0.46, 0.78)])
        pygame.draw.polygon(big, MIDMIX, [P(0.48, 0.575), P(0.79, 0.59), P(0.72, 0.755), P(0.48, 0.755)])
        pygame.draw.line(big, HI, P(0.49, 0.585), P(0.78, 0.60), lw(0.9))
        _plume(big, s, 0.30 * w, 0.14 * h, PLUME)

    HELMS = {"greathelm": hm_greathelm, "frogmouth": hm_frogmouth, "houndskull": hm_houndskull,
             "winged": hm_winged, "horned": hm_horned}
    _blit_ss(char, *_P(nom, 0.72, 0.30), int(nom.w * 0.56), int(nom.h * 0.56), HELMS.get(HELM, hm_greathelm), scale=6)

    # ── WEAPON held upright in front of the chest (clear of helm + shield) ─────
    WOOD = (96, 66, 38); WOOD_HI = (140, 100, 60)

    def _haft(big, gx, gy, tx, ty, s, wd):
        pygame.draw.line(big, WOOD, (gx, gy), (tx, ty), max(2, int(wd * s)))
        pygame.draw.line(big, WOOD_HI, (gx - int(wd * 0.3 * s), gy), (tx - int(wd * 0.3 * s), ty), max(1, int(wd * 0.4 * s)))

    def _grip(big, gx, gy, s):
        ge = (gx, gy + int(12 * s))
        pygame.draw.line(big, (74, 54, 36), (gx, gy), ge, max(3, int(3.8 * s)))
        pygame.draw.circle(big, BRASS, (int(ge[0]), int(ge[1])), int(2.6 * s))
        pygame.draw.circle(big, BRASS_HI, (int(ge[0]) - int(s), int(ge[1]) - int(s)), max(1, int(1.2 * s)))

    def wp_sword(big, s):
        w, h = big.get_size(); gx, gy = int(w * 0.50), int(h * 0.80); tx, ty = int(w * 0.47), int(h * 0.08)
        ux, uy = (tx - gx), (ty - gy); ln = math.hypot(ux, uy) or 1; ux, uy = ux / ln, uy / ln; px, py = -uy, ux; bw = 3.8 * s
        pygame.draw.polygon(big, OL, [(gx + px * bw, gy + py * bw), (gx - px * bw, gy - py * bw), (tx - px * 0.5 * s, ty - py * 0.5 * s), (tx + px * 0.5 * s, ty + py * 0.5 * s)])
        pygame.draw.polygon(big, MID, [(gx + px * (bw - 1.3 * s), gy + py * (bw - 1.3 * s)), (gx - px * (bw - 1.3 * s), gy - py * (bw - 1.3 * s)), (tx, ty)])
        pygame.draw.line(big, HI, (gx - px * (bw - s), gy - py * (bw - s)), (tx, ty), max(1, int(1.1 * s)))
        cg = 9 * s
        pygame.draw.line(big, BRASS, (gx + px * cg, gy + py * cg), (gx - px * cg, gy - py * cg), max(2, int(3 * s)))
        pygame.draw.circle(big, BRASS_HI, (int(gx + px * cg), int(gy + py * cg)), max(1, int(1.6 * s)))
        pygame.draw.circle(big, BRASS_HI, (int(gx - px * cg), int(gy - py * cg)), max(1, int(1.6 * s)))
        _grip(big, gx, gy, s)

    def wp_spear(big, s):                                      # long shaft + leaf blade
        w, h = big.get_size(); gx, gy = int(w * 0.50), int(h * 0.92); tx, ty = int(w * 0.47), int(h * 0.16)
        _haft(big, gx, gy, tx, ty, s, 3.2)
        head = [(tx, int(h * 0.02)), (int(tx + 4.5 * s), ty), (tx, int(ty + 3 * s)), (int(tx - 4.5 * s), ty)]
        pygame.draw.polygon(big, OL, head)
        pygame.draw.polygon(big, MID, [(tx, int(h * 0.035)), (int(tx + 3 * s), int(ty - s)), (tx, int(ty + 1.5 * s)), (int(tx - 3 * s), int(ty - s))])
        pygame.draw.line(big, HI, (tx, int(h * 0.04)), (tx, int(ty)), max(1, int(0.9 * s)))
        pygame.draw.line(big, BRASS, (int(tx - 4 * s), int(ty + 2 * s)), (int(tx + 4 * s), int(ty + 2 * s)), max(1, int(1.6 * s)))  # socket

    def wp_lance(big, s):                                      # thick shaft + vamplate guard
        w, h = big.get_size(); gx, gy = int(w * 0.52), int(h * 0.94); tx, ty = int(w * 0.44), int(h * 0.06)
        _haft(big, gx, gy, tx, ty, s, 4.6)
        pygame.draw.polygon(big, OL, [(tx, int(h * 0.0)), (int(tx + 3.2 * s), int(ty + 2 * s)), (tx, int(ty + 5 * s)), (int(tx - 3.2 * s), int(ty + 2 * s))])  # tip
        pygame.draw.polygon(big, MID, [(tx, int(h * 0.015)), (int(tx + 2 * s), int(ty + 2 * s)), (tx, int(ty + 4 * s)), (int(tx - 2 * s), int(ty + 2 * s))])
        gvx, gvy = int(w * 0.505), int(h * 0.62)               # vamplate hand-guard cone
        pygame.draw.circle(big, OL, (gvx, gvy), int(8 * s))
        pygame.draw.circle(big, MID, (gvx, gvy), int(6.5 * s))
        pygame.draw.arc(big, HI, (gvx - int(6.5 * s), gvy - int(6.5 * s), int(13 * s), int(13 * s)), math.radians(200), math.radians(330), max(1, int(1.2 * s)))

    def wp_mace(big, s):                                       # short haft + spiked ball
        w, h = big.get_size(); gx, gy = int(w * 0.50), int(h * 0.84); hx, hy = int(w * 0.47), int(h * 0.30)
        _haft(big, gx, gy, hx, hy, s, 3.4)
        for a in range(0, 360, 45):                            # spikes
            ex, ey = int(hx + 11 * s * math.cos(math.radians(a))), int(hy + 11 * s * math.sin(math.radians(a)))
            pygame.draw.line(big, OL, (hx, hy), (ex, ey), max(2, int(3 * s)))
            pygame.draw.line(big, MID, (hx, hy), (ex, ey), max(1, int(1.4 * s)))
        pygame.draw.circle(big, OL, (hx, hy), int(7 * s))
        pygame.draw.circle(big, MID, (hx, hy), int(5.5 * s))
        pygame.draw.circle(big, HI, (hx - int(2 * s), hy - int(2 * s)), int(2 * s))
        _grip(big, gx, gy, s)

    def wp_axe(big, s):                                        # haft + crescent blade
        w, h = big.get_size(); gx, gy = int(w * 0.50), int(h * 0.92); tx, ty = int(w * 0.46), int(h * 0.12)
        _haft(big, gx, gy, tx, ty, s, 3.4)
        hx, hy = int(w * 0.47), int(h * 0.26)
        blade = [(hx, int(hy - 9 * s)), (int(hx + 17 * s), int(hy - 12 * s)), (int(hx + 20 * s), hy), (int(hx + 17 * s), int(hy + 12 * s)), (hx, int(hy + 9 * s))]
        pygame.draw.polygon(big, OL, blade)
        pygame.draw.polygon(big, MID, [(hx, int(hy - 7 * s)), (int(hx + 14 * s), int(hy - 9 * s)), (int(hx + 16 * s), hy), (int(hx + 14 * s), int(hy + 9 * s)), (hx, int(hy + 7 * s))])
        pygame.draw.arc(big, HI, (hx, int(hy - 11 * s), int(20 * s), int(22 * s)), math.radians(300), math.radians(60), max(1, int(1.2 * s)))
        pygame.draw.line(big, OL, (int(hx - 5 * s), hy), (hx, hy), max(2, int(3 * s)))                   # back spike
        _grip(big, gx, gy, s)

    WEAPONS = {"sword": wp_sword, "spear": wp_spear, "lance": wp_lance, "mace": wp_mace, "axe": wp_axe}
    _blit_ss(char, *_P(nom, 0.52, 0.52), int(nom.w * 0.42), int(nom.h * 1.0), WEAPONS.get(WEAPON, wp_sword))


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
