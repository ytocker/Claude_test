"""
Five candidate ACHIEVEMENTS star emblems for the main-menu "AWARDS" tile.

Each star is the sibling of ``hud._draw_trophy`` on the TOP 10 tile, so it must
read at the same tiny scale (~18-20 px tall) yet stay razor-sharp. The whole
family is drawn SUPERSAMPLED — composited on a surface ``_SS``× the target box
with clean geometry, then ``smoothscale``d down — because raw polygon draws at
tile scale alias into jaggy edges. Same discipline the badge family uses.

Palette is locked to the menu's gold-on-navy family so the emblem sits with the
trophy as one set. Lighting is one fixed upper-left source across all five.
"""
import math
import pygame

_SS = 4  # supersample factor: draw big, smoothscale down for crisp rims

# Menu gold family (mirrors hud + trophy).
_GOLD        = (240, 192,  64)   # body gold  (_GOLD_BRIGHT)
_GOLD_HI     = (255, 230, 150)   # pale sheen / lit crest
_GOLD_HOT    = (255, 248, 222)   # specular hot-spot
_GOLD_LO     = (188, 138,  28)   # shadowed gold
_RIM         = (140,  90,   8)   # dark keyline rim
_RIM_DEEP    = (110,  72,   8)   # deepest recess


def _lerp(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _star_pts(cx, cy, R, r, n=5, rot_deg=-90):
    """2n vertices alternating outer radius R / inner radius r, first at `rot`."""
    pts = []
    for i in range(n * 2):
        ang = math.radians(rot_deg + i * 180.0 / n)
        rad = R if i % 2 == 0 else r
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    return pts


def _chaikin(pts, iters):
    """Corner-cutting subdivision — rounds a polygon while keeping silhouette."""
    for _ in range(iters):
        out = []
        n = len(pts)
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            out.append((0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]))
            out.append((0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]))
        pts = out
    return pts


def _grad_star(box, poly, top_col, bot_col):
    """A vertical top→bottom gradient clipped to `poly` on a box×box surface."""
    grad = pygame.Surface((box, box), pygame.SRCALPHA)
    ys = [p[1] for p in poly]
    y0, y1 = min(ys), max(ys)
    span = max(1.0, y1 - y0)
    for yy in range(box):
        t = min(1.0, max(0.0, (yy - y0) / span))
        pygame.draw.line(grad, (*_lerp(top_col, bot_col, t), 255),
                         (0, yy), (box, yy))
    mask = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return grad


def _blit_ss(surf, ss, box, cx, cy):
    small = pygame.transform.smoothscale(ss, (box, box))
    surf.blit(small, (int(round(cx - box / 2)), int(round(cy - box / 2))))


# ── 1. Classic sharp 5-point ────────────────────────────────────────────────
# Clean iconic gold star: dark keyline rim, soft top-lit body gradient, one
# crisp upper-left specular streak. The plain, unmistakable "star".
def draw_classic(surf, cx, cy, R=10):
    box = int(R * 2 + 8)
    B = box * _SS
    c = B / 2
    Rs, rs = R * _SS, R * _SS * 0.42
    k = (Rs + 2.2 * _SS) / Rs  # rim = uniformly scaled dark star behind gold
    ss = pygame.Surface((B, B), pygame.SRCALPHA)

    pygame.draw.polygon(ss, _RIM, _star_pts(c, c, Rs * k, rs * k))
    body = _star_pts(c, c, Rs, rs)
    pygame.draw.polygon(ss, _GOLD, body)
    ss.blit(_grad_star(B, body, _GOLD_HI, _GOLD_LO), (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT)
    # Upper-left specular streak: the top point's left edge catches the light.
    top = body[0]
    left_inner = body[-1]
    mid = ((top[0] + left_inner[0]) / 2, (top[1] + left_inner[1]) / 2)
    pygame.draw.line(ss, _GOLD_HOT, top, mid, int(1.6 * _SS))
    pygame.draw.line(ss, _GOLD_HI, top, left_inner, int(1.0 * _SS))
    _blit_ss(surf, ss, box, cx, cy)


# ── 2. Struck-metal beveled ─────────────────────────────────────────────────
# An embossed medal star: each arm is split by a central ridge into a lit and a
# shadowed facet, shaded by the shared upper-left light — reads as raised metal.
def draw_beveled(surf, cx, cy, R=10):
    box = int(R * 2 + 8)
    B = box * _SS
    c = (B / 2, B / 2)
    Rs, rs = R * _SS, R * _SS * 0.46
    ss = pygame.Surface((B, B), pygame.SRCALPHA)

    # Dark rim first (scaled-up star behind the facets).
    k = (Rs + 2.2 * _SS) / Rs
    pygame.draw.polygon(ss, _RIM, _star_pts(c[0], c[1], Rs * k, rs * k))

    light = (-0.55, -0.83)  # upper-left (screen y down → up is negative)
    outer = [(c[0] + Rs * math.cos(math.radians(-90 + 72 * i)),
              c[1] + Rs * math.sin(math.radians(-90 + 72 * i))) for i in range(5)]
    inner = [(c[0] + rs * math.cos(math.radians(-54 + 72 * i)),
              c[1] + rs * math.sin(math.radians(-54 + 72 * i))) for i in range(5)]
    for i in range(5):
        o = outer[i]
        il, ir = inner[(i - 1) % 5], inner[i]
        for tri in ((c, il, o), (c, o, ir)):
            mx = (tri[1][0] + tri[2][0]) / 2 - c[0]
            my = (tri[1][1] + tri[2][1]) / 2 - c[1]
            n = math.hypot(mx, my) or 1.0
            d = (mx / n) * light[0] + (my / n) * light[1]
            t = (d + 1) / 2
            pygame.draw.polygon(ss, _lerp(_GOLD_LO, _GOLD_HI, t), tri)
    # Ridge keylines from centre to each tip sharpen the emboss.
    for o in outer:
        pygame.draw.line(ss, _RIM_DEEP, c, o, max(1, int(0.6 * _SS)))
    # Raised centre boss catches the light.
    pygame.draw.circle(ss, _GOLD_HI, (int(c[0]), int(c[1])), int(rs * 0.5))
    pygame.draw.circle(ss, _GOLD_HOT,
                       (int(c[0] - rs * 0.18), int(c[1] - rs * 0.18)),
                       int(rs * 0.22))
    _blit_ss(surf, ss, box, cx, cy)


# ── 3. Rounded / soft 5-point ───────────────────────────────────────────────
# A friendlier, chunkier star: Chaikin-rounded points, fatter arms, a soft
# top-lit body and a broad upper sheen. The "gummy" award star.
def draw_rounded(surf, cx, cy, R=10):
    box = int(R * 2 + 8)
    B = box * _SS
    c = B / 2
    Rs, rs = R * _SS, R * _SS * 0.56  # fatter inner radius → chunky arms
    ss = pygame.Surface((B, B), pygame.SRCALPHA)

    base = _star_pts(c, c, Rs, rs)
    body = _chaikin(base, 3)
    rim = _chaikin(_star_pts(c, c, Rs + 2.0 * _SS, rs + 2.0 * _SS), 3)
    pygame.draw.polygon(ss, _RIM, rim)
    pygame.draw.polygon(ss, _GOLD, body)
    ss.blit(_grad_star(B, body, _GOLD_HI, _GOLD_LO), (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT)
    # Broad soft sheen: a pale rounded blob on the upper-left lobe.
    sheen = pygame.Surface((B, B), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (*_GOLD_HOT, 150),
                        (c - Rs * 0.62, c - Rs * 0.78, Rs * 0.7, Rs * 0.62))
    mask = pygame.Surface((B, B), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), body)
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss.blit(sheen, (0, 0))
    _blit_ss(surf, ss, box, cx, cy)


# ── 4. Sparkle / four-glint star ────────────────────────────────────────────
# A shine, not a badge: a slender 4-point sparkle with a bright core and four
# short diagonal glints radiating out — reads as "twinkle / new".
def draw_sparkle(surf, cx, cy, R=10):
    box = int(R * 2 + 8)
    B = box * _SS
    c = B / 2
    Rs = R * _SS
    ss = pygame.Surface((B, B), pygame.SRCALPHA)

    # Thin diagonal glints behind the main sparkle.
    for i in range(4):
        ang = math.radians(-45 + 90 * i)
        gl = Rs * 0.66
        p = (c + gl * math.cos(ang), c + gl * math.sin(ang))
        pygame.draw.line(ss, (*_GOLD_HI, 210), (c, c), p, max(1, int(0.9 * _SS)))

    # Slender 4-point body: long thin arms via a very small inner radius.
    body = _star_pts(c, c, Rs, Rs * 0.14, n=4, rot_deg=-90)
    rim_k = (Rs + 1.6 * _SS) / Rs
    pygame.draw.polygon(ss, _RIM,
                        _star_pts(c, c, Rs * rim_k, Rs * 0.14 * rim_k,
                                  n=4, rot_deg=-90))
    pygame.draw.polygon(ss, _GOLD, body)
    ss.blit(_grad_star(B, body, _GOLD_HI, _GOLD_LO), (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT)
    # Bright core hotspot sells the sparkle.
    pygame.draw.circle(ss, _GOLD_HI, (int(c), int(c)), int(Rs * 0.24))
    pygame.draw.circle(ss, _GOLD_HOT,
                       (int(c - Rs * 0.05), int(c - Rs * 0.05)), int(Rs * 0.12))
    _blit_ss(surf, ss, box, cx, cy)


# ── 5. Star medallion ───────────────────────────────────────────────────────
# A mounted medal: a gold coin/disc with a beveled 5-point star struck on it —
# the most "official" of the set, a star you were awarded.
def draw_medallion(surf, cx, cy, R=10):
    box = int(R * 2 + 8)
    B = box * _SS
    c = B / 2
    Rs = R * _SS
    ss = pygame.Surface((B, B), pygame.SRCALPHA)

    # Disc: dark rim ring, top-lit gold gradient body, upper-left sheen.
    pygame.draw.circle(ss, _RIM_DEEP, (int(c), int(c)), int(Rs))
    disc = pygame.Surface((B, B), pygame.SRCALPHA)
    dr = Rs - 1.4 * _SS
    for yy in range(B):
        t = min(1.0, max(0.0, (yy - (c - dr)) / (2 * dr)))
        pygame.draw.line(disc, (*_lerp(_GOLD_HI, _GOLD_LO, t), 255),
                         (0, yy), (B, yy))
    dmask = pygame.Surface((B, B), pygame.SRCALPHA)
    pygame.draw.circle(dmask, (255, 255, 255, 255), (int(c), int(c)), int(dr))
    disc.blit(dmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss.blit(disc, (0, 0))
    # Beaded inner keyline of the coin.
    pygame.draw.circle(ss, _RIM, (int(c), int(c)), int(dr), max(1, int(0.7 * _SS)))
    # Upper-left coin sheen.
    sheen = pygame.Surface((B, B), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (*_GOLD_HOT, 120),
                        (c - dr * 0.8, c - dr * 0.85, dr * 0.85, dr * 0.7))
    smask = pygame.Surface((B, B), pygame.SRCALPHA)
    pygame.draw.circle(smask, (255, 255, 255, 255), (int(c), int(c)), int(dr))
    sheen.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss.blit(sheen, (0, 0))

    # Struck star on the coin — beveled two-tone arms, upper-left lit.
    sR = Rs * 0.62
    srr = sR * 0.46
    light = (-0.55, -0.83)
    outer = [(c + sR * math.cos(math.radians(-90 + 72 * i)),
              c + sR * math.sin(math.radians(-90 + 72 * i))) for i in range(5)]
    inner = [(c + srr * math.cos(math.radians(-54 + 72 * i)),
              c + srr * math.sin(math.radians(-54 + 72 * i))) for i in range(5)]
    # Slight drop-shadow so the star sits raised on the coin.
    pygame.draw.polygon(ss, (*_RIM_DEEP, 180),
                        _star_pts(c + 0.6 * _SS, c + 0.9 * _SS, sR, srr))
    cc = (c, c)
    for i in range(5):
        o = outer[i]
        il, ir = inner[(i - 1) % 5], inner[i]
        for tri in ((cc, il, o), (cc, o, ir)):
            mx = (tri[1][0] + tri[2][0]) / 2 - c
            my = (tri[1][1] + tri[2][1]) / 2 - c
            n = math.hypot(mx, my) or 1.0
            d = (mx / n) * light[0] + (my / n) * light[1]
            pygame.draw.polygon(ss, _lerp(_GOLD_LO, _GOLD_HOT, (d + 1) / 2), tri)
    for o in outer:
        pygame.draw.line(ss, _RIM, cc, o, max(1, int(0.5 * _SS)))
    _blit_ss(surf, ss, box, cx, cy)


STARS = [
    ("Classic sharp",   draw_classic),
    ("Struck bevel",    draw_beveled),
    ("Rounded soft",    draw_rounded),
    ("Sparkle glint",   draw_sparkle),
    ("Star medallion",  draw_medallion),
]
