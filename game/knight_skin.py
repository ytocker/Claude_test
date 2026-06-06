"""Knight costume for the "survive one hit" power-up. Pip is re-cast in
sculpted steel armour — armet helm with a crimson plume, breastplate, brass-
rimmed pauldron over the near wing, a quarterly gules/or heater shield on the
chest, and a longsword.

Procedural-art only: every piece is drawn from code on top of the base
parrot frames, so the costume flaps with Pip's own wing per frame. The
shield art is shared by the in-world pickup and the HUD timer glyph so
the three reads stay identical.

Built lazily and cached by `parrot._get_knight_frames()`.
"""
import math
import random
import pygame

from game import parrot

# Fried-chicken palette borrowed from the original fried parrot
# (parrot._build_fried_frame) so the FRIED KNIGHT deep-fries with the exact same
# crispy tones + texture recipe, just on the armoured base.
_CRISPY_GOLD = parrot._CRISPY_GOLD
_CRISPY_DARK = parrot._CRISPY_DARK
_CRISPY_LIGHT = parrot._CRISPY_LIGHT
_CRISPY_SPOT = parrot._CRISPY_SPOT

# Steel + heraldry palette (shared across helm / breastplate / shield).
OL = (24, 28, 38); D = (70, 78, 96); MID = (146, 156, 178); HI = (238, 244, 255)
BRASS = (208, 174, 98); BRASS_HI = (255, 232, 168); CRIM = (160, 44, 48)
# Canonical K7 heraldry. STM is the gray steel rim — kept NEUTRAL (no blue
# bias) so neither it nor its anti-aliased edges read as blue pixels.
STM = (162, 163, 164); GULES = (170, 46, 50); ORC = (226, 182, 72)

# Shield on the front of the chest (fx, fy, w-frac, h-frac of the body rect).
_SHIELD_POS = (0.92, 0.58, 0.36, 0.46)
# Near-wing armour: "lames" = articulated overlapping plates, "dome" = single plate.
_WING_STYLE = "lames"
# Padding around the body frame so the helm crest / sword / plume aren't clipped.
_PAD = 16


# ── supersampled-draw helpers (a piece is drawn big then smoothscaled) ───────
def _ss(w, h, fn, scale=4):
    big = pygame.Surface((int(w * scale), int(h * scale)), pygame.SRCALPHA)
    fn(big, scale)
    return pygame.transform.smoothscale(big, (int(w), int(h)))


def _blit_ss(surf, cx, cy, w, h, fn, scale=4):
    surf.blit(_ss(w, h, fn, scale), (int(cx - w / 2), int(cy - h / 2)))


def _amask(sprite):
    return pygame.mask.from_surface(sprite, 40).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))


def _recolor(src, mult, add=(0, 0, 0)):
    g = pygame.transform.grayscale(src)
    g.fill((*mult, 255), special_flags=pygame.BLEND_RGBA_MULT)
    if add != (0, 0, 0):
        g.fill((*add, 0), special_flags=pygame.BLEND_RGB_ADD)
    return g


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


def _qbez(p0, p1, p2, n=22):
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        out.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return out


def _P(rect, fx, fy):
    return (rect.x + fx * rect.w, rect.y + fy * rect.h)


def _plate(big, s, rx, ry, rw, rh):
    pygame.draw.ellipse(big, OL, (rx, ry, rw, rh))
    pygame.draw.ellipse(big, D, (rx + int(1.5 * s), ry + int(1.5 * s), rw - int(3 * s), rh - int(3 * s)))
    pygame.draw.ellipse(big, MID, (rx + int(3 * s), ry + int(3 * s), rw - int(6 * s), rh - int(6 * s)))
    pygame.draw.arc(big, HI, (rx + int(3 * s), ry + int(2 * s), rw - int(6 * s), rh - int(4 * s)), math.radians(202), math.radians(338), max(1, int(1.6 * s)))


def _heater_pts(w, h, pad):
    return [(pad, pad), (w - pad, pad), (w - pad, h * 0.46), (w / 2, h - pad), (pad, h * 0.46)]


def _inset(points, k):
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    out = []
    for x, y in points:
        dx, dy = cx - x, cy - y
        d = math.hypot(dx, dy) or 1.0
        out.append((x + dx / d * k, y + dy / d * k))
    return out


def _shield(big, s):
    """K7 heater: quarterly gules/or inside a gray steel rim (matches the
    design). No dark-navy outline — the rim is the perimeter."""
    w, h = big.get_size(); cx, cy = w / 2, h * 0.45
    pts = _heater_pts(w, h, 2 * s)
    pygame.draw.polygon(big, STM, pts)
    fpts = _inset(pts, 4.5 * s)
    tmp = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(tmp, GULES, (0, 0, int(cx), int(cy)))
    pygame.draw.rect(tmp, ORC, (int(cx), 0, int(w - cx), int(cy)))
    pygame.draw.rect(tmp, ORC, (0, int(cy), int(cx), int(h - cy)))
    pygame.draw.rect(tmp, GULES, (int(cx), int(cy), int(w - cx), int(h - cy)))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), fpts)
    tmp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(tmp, (0, 0))


def _breast(big, s):
    w, h = big.get_size()
    _plate(big, s, int(1 * s), int(2 * s), int(w - 2 * s), int(h - 3 * s))
    pygame.draw.line(big, HI, (int(w * 0.5), int(5 * s)), (int(w * 0.5), int(h - 6 * s)), max(1, int(1.3 * s)))
    pygame.draw.circle(big, BRASS, (int(w * 0.5), int(h * 0.58)), int(2.6 * s))
    pygame.draw.circle(big, BRASS_HI, (int(w * 0.5) - int(s), int(h * 0.58) - int(s)), max(1, int(s)))


def _pauldron(big, s):
    w, h = big.get_size()
    rim = (int(2 * s), int(2 * s), int(w - 4 * s), int(h - 4 * s))
    tmp = pygame.Surface((w, h), pygame.SRCALPHA)
    if _WING_STYLE == "dome":
        _plate(tmp, s, *rim)
        pygame.draw.line(tmp, HI, (int(w * 0.5), int(h * 0.22)), (int(w * 0.5), int(h * 0.8)), max(1, int(1.3 * s)))
    else:
        pygame.draw.ellipse(tmp, OL, rim)
        for i in range(4):
            y0 = h * (0.10 + i * 0.215)
            band = [(int(w * 0.06), int(y0)), (int(w * 0.94), int(y0)),
                    (int(w * 0.86), int(y0 + h * 0.30)), (int(w * 0.14), int(y0 + h * 0.30))]
            pygame.draw.polygon(tmp, D, band)
            pygame.draw.polygon(tmp, MID, [(int(w * 0.10), int(y0 + h * 0.03)), (int(w * 0.90), int(y0 + h * 0.03)),
                                           (int(w * 0.83), int(y0 + h * 0.20)), (int(w * 0.17), int(y0 + h * 0.20))])
            pygame.draw.arc(tmp, HI, (int(w * 0.12), int(y0 - h * 0.02), int(w * 0.76), int(h * 0.22)),
                            math.radians(200), math.radians(340), max(1, int(1.4 * s)))
            pygame.draw.line(tmp, OL, (int(w * 0.08), int(y0)), (int(w * 0.92), int(y0)), max(1, int(1.1 * s)))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), rim)
    tmp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(tmp, (0, 0))
    pygame.draw.ellipse(big, BRASS, rim, max(2, int(2 * s)))
    pygame.draw.arc(big, BRASS_HI, (int(3 * s), int(2 * s), int(w - 6 * s), int(h - 4 * s)), math.radians(200), math.radians(340), max(1, int(s)))
    cxg, cyg = w / 2, h / 2
    for ang in range(0, 360, 60):
        rx = int(cxg + (cxg - int(3 * s)) * math.cos(math.radians(ang)))
        ry = int(cyg + (cyg - int(3 * s)) * math.sin(math.radians(ang)))
        pygame.draw.circle(big, BRASS, (rx, ry), max(1, int(1.2 * s)))


def _helm(big, s):
    w, h = big.get_size(); cxg = w // 2
    pygame.draw.ellipse(big, D, (int(w * 0.16), int(h * 0.66), int(w * 0.68), int(h * 0.32)))
    pygame.draw.ellipse(big, MID, (int(w * 0.19), int(h * 0.67), int(w * 0.62), int(h * 0.22)))
    pygame.draw.arc(big, HI, (int(w * 0.2), int(h * 0.66), int(w * 0.6), int(h * 0.2)), math.radians(196), math.radians(344), max(1, int(1.2 * s)))
    for i, col in enumerate([OL, (52, 58, 74), (94, 102, 122), MID, (190, 200, 218)]):
        ins = int(i * 1.7 * s)
        pygame.draw.ellipse(big, col, (int(4 * s) + ins, int(4 * s) + ins, int(w - 8 * s) - 2 * ins, int(h * 0.7) - 2 * ins))
    pygame.draw.ellipse(big, HI, (int(10 * s), int(7 * s), int(w * 0.3), int(h * 0.22)))
    pygame.draw.arc(big, (38, 44, 58), (int(5 * s), int(7 * s), int(w - 10 * s), int(h * 0.64)), math.radians(14), math.radians(166), max(2, int(2 * s)))
    pygame.draw.polygon(big, (58, 64, 80), [(cxg - int(2.5 * s), int(5 * s)), (cxg + int(2.5 * s), int(5 * s)), (cxg + int(1.2 * s), int(h * 0.4)), (cxg - int(1.2 * s), int(h * 0.4))])
    pygame.draw.line(big, BRASS, (cxg, int(5 * s)), (cxg, int(h * 0.4)), max(1, int(1.6 * s)))
    pygame.draw.line(big, BRASS_HI, (cxg - int(0.9 * s), int(6 * s)), (cxg - int(0.9 * s), int(h * 0.38)), max(1, int(0.9 * s)))
    vy = int(h * 0.4)
    cf = int(w * 0.60)
    pygame.draw.line(big, BRASS, (int(0.22 * w), vy - int(1.5 * s)), (int(w - 5 * s), vy + int(2.5 * s)), max(2, int(2.2 * s)))
    pygame.draw.line(big, BRASS_HI, (int(0.22 * w), vy - int(2.4 * s)), (int(w - 5 * s), vy + int(1.6 * s)), max(1, int(0.9 * s)))
    pygame.draw.polygon(big, OL, [(int(0.22 * w), vy), (int(w - 4 * s), vy + int(3 * s)), (int(w - 8 * s), int(h * 0.7)), (cf, int(h * 0.8)), (int(0.30 * w), int(h * 0.7))])
    pygame.draw.polygon(big, (64, 72, 90), [(int(0.25 * w), vy + int(2.5 * s)), (int(w - 7 * s), vy + int(4.5 * s)), (int(w - 10 * s), int(h * 0.68)), (cf, int(h * 0.77)), (int(0.33 * w), int(h * 0.68))])
    pygame.draw.polygon(big, MID, [(int(0.25 * w), vy + int(2.5 * s)), (int(w - 7 * s), vy + int(4.5 * s)), (int(w - 9 * s), int(h * 0.54)), (int(0.30 * w), int(h * 0.52))])
    pygame.draw.rect(big, (6, 7, 11), (int(cf - w * 0.30), int(vy + h * 0.11), int(w * 0.60), int(h * 0.05)))
    pygame.draw.rect(big, (6, 7, 11), (int(cf - 1.3 * s), int(vy + h * 0.11), int(2.6 * s), int(h * 0.22)))
    for bx in range(5):
        if abs(bx - 2) >= 1:
            pygame.draw.circle(big, (6, 7, 11), (int(cf + (bx - 2) * int(3.0 * s)), int(vy + h * 0.30)), max(1, int(0.85 * s)))
    for rx in (0.34, 0.86):
        pygame.draw.circle(big, BRASS, (int(w * rx), int(h * 0.55)), max(1, int(1.3 * s)))
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


def _sword(big, s):
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


def _build_knight_frame(base_frame, *, body_recolor=True):
    bw, bh = base_frame.get_size()
    char = pygame.Surface((bw + 2 * _PAD, bh + 2 * _PAD), pygame.SRCALPHA)
    nom = base_frame.get_rect(center=(char.get_width() // 2, char.get_height() // 2))
    # body_recolor=True → steel-recolor the plain parrot (the lone-knight skin).
    # body_recolor=False → blit an ALREADY-themed base (fried / spectral) raw so
    # its palette shows through the armour gaps (belly/tail), giving fried-steel
    # / spectral knights as compositions rather than new from-scratch art.
    if body_recolor:
        body = _body(base_frame, (140, 150, 174), (6, 9, 16), (236, 242, 254), (44, 50, 66), 118, 100)
    else:
        body = base_frame
    char.blit(body, nom.topleft)
    _blit_ss(char, *_P(nom, 0.45, 0.62), int(nom.w * 0.5), int(nom.h * 0.30), _breast)
    sfx, sfy, swf, shf = _SHIELD_POS
    _blit_ss(char, *_P(nom, sfx, sfy), int(nom.w * swf), int(nom.h * shf), _shield)
    _blit_ss(char, *_P(nom, 0.45, 0.46), int(nom.w * 0.42), int(nom.h * 0.34), _pauldron, scale=6)
    _blit_ss(char, *_P(nom, 0.73, 0.17), int(nom.w * 0.5), int(nom.h * 0.54), _helm, scale=6)
    _blit_ss(char, *_P(nom, 0.74, 0.5), int(nom.w * 0.5), int(nom.h * 0.95), _sword)
    return char


def build_knight_frames():
    return [_build_knight_frame(f) for f in parrot._get_frames()]


def _deep_fry(frame):
    """Put a whole knight frame through the SAME deep-fry the fried parrot gets
    (parrot._build_fried_frame): recolor its luminance onto the crispy batter
    ramp, then add fried TEXTURE — scattered crispy spots, crackle lines (dark
    valley + light ridge = raised batter) and a golden grease sheen — all clamped
    to the silhouette. So helm, shield, sword, armour and body read battered-
    crispy, not merely gold-tinted. A fixed rng seed keeps the texture identical
    across the 4 wing frames (the parrot's spots/crackle are likewise fixed)."""
    out = _recolor(frame, _CRISPY_GOLD, add=(44, 20, 2))   # rich golden-brown batter
    w, h = out.get_size()
    tex = pygame.Surface((w, h), pygame.SRCALPHA)
    rng = random.Random(0x5C0FFEE)
    for _ in range(12):                                    # dark crispy crust blotches
        pygame.draw.circle(tex, _CRISPY_DARK,
                           (rng.randint(0, w - 1), rng.randint(0, h - 1)), rng.randint(2, 3))
    for _ in range(66):                                    # fine crispy spots
        pygame.draw.circle(tex, _CRISPY_SPOT,
                           (rng.randint(0, w - 1), rng.randint(0, h - 1)), rng.randint(1, 2))
    for _ in range(24):                                    # crackle: dark valley + light ridge
        x1, y1 = rng.randint(2, w - 9), rng.randint(2, h - 9)
        dx, dy = rng.randint(4, 9), rng.randint(-4, 4)
        pygame.draw.line(tex, _CRISPY_DARK, (x1, y1), (x1 + dx, y1 + dy), 1)
        pygame.draw.line(tex, _CRISPY_LIGHT, (x1 - 1, y1 - 1), (x1 + dx - 1, y1 + dy - 1), 1)
    tex.blit(_amask(out), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    out.blit(tex, (0, 0))
    _sheen(out, (255, 225, 145), (235, 180, 90), top_a=52, bot_a=34)
    return out


def build_knight_kfc_frames():
    """THE FRIED KNIGHT — the regular STEEL knight run through the fried-parrot
    deep-fry (crispy batter palette + crackle/spots/grease texture), so the whole
    suit reads battered-crispy."""
    return [_deep_fry(f) for f in build_knight_frames()]


def build_knight_ghost_frames():
    """Spectral knight — cyan spectral body under steel armour (the draw-time
    ghost alpha-breath then makes the whole thing translucent)."""
    return [_build_knight_frame(f, body_recolor=False)
            for f in parrot._ensure_ghost_frames()]


def build_knight_kfc_ghost_frames():
    """Fried + spectral knight — the cyan-tinted fried body under steel armour."""
    return [_build_knight_frame(f, body_recolor=False)
            for f in parrot._ensure_kfc_ghost_frames()]


_SHIELD_ICON_CACHE: dict = {}


def _get_shield_icon(size, scale):
    """Cache the standalone heater-shield icon per (size, scale). `_ss` rebuilds
    a full supersample + smoothscale on every call, so without this the genie's
    knight offer re-rendered its shield every frame."""
    key = (size, scale)
    spr = _SHIELD_ICON_CACHE.get(key)
    if spr is None:
        spr = _ss(int(size * 0.82), size, _shield, scale=scale)
        _SHIELD_ICON_CACHE[key] = spr
    return spr


def draw_shield_icon(surf, cx, cy, size=30):
    """In-world pickup + zoom previews: the heater shield, centred."""
    spr = _get_shield_icon(size, 5)
    surf.blit(spr, (int(cx - spr.get_width() / 2),
                    int(cy - spr.get_height() / 2)))


def draw_shield_glyph(surf, cx, cy, size=22):
    """Compact HUD timer glyph — the same canonical heater shield."""
    spr = _get_shield_icon(size, 6)
    surf.blit(spr, (int(cx - spr.get_width() / 2),
                    int(cy - spr.get_height() / 2)))
