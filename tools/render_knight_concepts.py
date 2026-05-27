"""FIVE completely independent knight concepts — each drawn bottom-up as its own
character (own silhouette, body, pose, composition), NOT a shared base with
swapped parts.  EXPLORATION ONLY.

Run:  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_knight_concepts
"""
import os, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from tools import render_revive_designs as R

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                   "docs", "screenshots", "revive_designs")
os.makedirs(OUT, exist_ok=True)

CW, CH, SS = 300, 380, 5          # native character canvas + supersample


# ── low-level primitives (shared; the ONLY thing the 5 concepts have in common) ─
def ELL(b, c, cx, cy, w, h):
    pygame.draw.ellipse(b, c, (int(cx - w / 2), int(cy - h / 2), int(w), int(h)))


def POLY(b, c, pts):
    pygame.draw.polygon(b, c, pts)


def LINE(b, c, a, z, wd):
    pygame.draw.line(b, c, a, z, max(1, int(wd)))


def qbez(p0, p1, p2, n=20):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (i / n for i in range(n + 1))]


def grad_poly(b, pts, top, bot):
    """Fill a polygon with a vertical gradient."""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, x1, y0, y1 = int(min(xs)), int(max(xs)), int(min(ys)), int(max(ys))
    w, h = b.get_size()
    g = pygame.Surface((w, h), pygame.SRCALPHA)
    span = max(1, y1 - y0)
    for y in range(y0, y1, 2):
        t = (y - y0) / span
        col = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        pygame.draw.rect(g, col, (x0, y, x1 - x0, 2))
    m = pygame.Surface((w, h), pygame.SRCALPHA)
    POLY(m, (255, 255, 255, 255), pts)
    g.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    b.blit(g, (0, 0))


def beak(b, cx, cy, r, face=1):
    """Small hooked macaw beak (orange).  face=1 → points right."""
    OR1, OR2, OR3 = (242, 170, 60), (208, 132, 40), (255, 214, 130)
    POLY(b, OR2, [(cx, cy - r), (cx + face * 2.2 * r, cy - 0.2 * r), (cx + face * 1.7 * r, cy + 0.9 * r), (cx, cy + 0.7 * r)])
    POLY(b, OR1, [(cx, cy - 0.7 * r), (cx + face * 1.7 * r, cy - 0.1 * r), (cx + face * 1.3 * r, cy + 0.7 * r), (cx, cy + 0.5 * r)])
    LINE(b, OR3, (cx, cy - 0.5 * r), (cx + face * 1.4 * r, cy - 0.05 * r), max(1, int(0.18 * r)))


def macaw_tail(b, cx, cy, r, ang=200):
    """Layered red→yellow tail feathers fanning down-left."""
    cols = [(196, 52, 44), (224, 120, 40), (236, 196, 70)]
    for i, col in enumerate(cols):
        a = math.radians(ang + i * 10)
        tip = (cx + r * (1.0 - 0.12 * i) * math.cos(a), cy + r * (1.0 - 0.12 * i) * math.sin(a))
        perp = a + math.pi / 2; wd = r * 0.16
        POLY(b, col, [(cx + wd * math.cos(perp), cy + wd * math.sin(perp)),
                      (cx - wd * math.cos(perp), cy - wd * math.sin(perp)), tip])


def plume(b, sx, sy, col, s, reach=34, up=22):
    clo = tuple(max(0, int(c * 0.6)) for c in col); chi = tuple(min(255, int(c * 1.3 + 30)) for c in col)
    pygame.draw.circle(b, (210, 176, 92), (int(sx), int(sy)), int(2.6 * s))
    for c, off in ((clo, 0), (col, int(2 * s)), (chi, int(4 * s))):
        top = qbez((sx, sy), (sx - reach * 0.4 * s, sy - up * s), (sx - reach * s, sy - 2 * s), 18)
        bot = qbez((sx, sy), (sx - reach * 0.3 * s, sy - up * 0.3 * s), (sx - reach * 0.85 * s, sy + up * 0.6 * s), 18)
        POLY(b, c, [(x - off, y) for x, y in top] + [(x - off, y) for x, y in reversed(bot)])


def rivets(b, pts, s, col=(214, 180, 104), hi=(255, 236, 176)):
    for (x, y) in pts:
        pygame.draw.circle(b, col, (int(x), int(y)), max(1, int(1.6 * s)))
        pygame.draw.circle(b, hi, (int(x - s), int(y - s)), max(1, int(0.8 * s)))


# ═══════════════════════════════════════════════════════════════════════════════
# CONCEPT A — "Sentinel": tall, symmetric, statuesque; both talons on a longsword
# planted point-down; great-helm + tall plume; rounded pauldrons.  Vertical I.
# ═══════════════════════════════════════════════════════════════════════════════
def concept_sentinel(b, s):
    w, h = b.get_size()
    OL, LO, MID, HI = (24, 28, 40), (96, 106, 130), (172, 184, 208), (248, 252, 255)
    BR, BRH, RED = (214, 180, 104), (255, 236, 176), (176, 44, 48)
    cx = w * 0.5
    macaw_tail(b, w * 0.40, h * 0.66, h * 0.16, ang=150)
    # legs / greaves
    for sgn in (-1, 1):
        lx = cx + sgn * w * 0.10
        grad_poly(b, [(lx - w * 0.05, h * 0.70), (lx + w * 0.05, h * 0.70), (lx + w * 0.045, h * 0.92), (lx - w * 0.045, h * 0.92)], MID, LO)
        POLY(b, OL, [(lx - w * 0.07, h * 0.92), (lx + w * 0.07, h * 0.92), (lx + w * 0.06, h * 0.97), (lx - w * 0.085, h * 0.97)])  # sabaton
    # tapered cuirass
    body = [(cx - w * 0.20, h * 0.34), (cx + w * 0.20, h * 0.34), (cx + w * 0.22, h * 0.52),
            (cx + w * 0.13, h * 0.70), (cx - w * 0.13, h * 0.70), (cx - w * 0.22, h * 0.52)]
    POLY(b, OL, [(x + (cx - x) * -0.04, y) for x, y in body])
    grad_poly(b, body, HI, LO)
    LINE(b, HI, (cx, h * 0.36), (cx, h * 0.68), max(1, int(1.8 * s)))            # keel
    for i in range(3):                                                          # fauld lames
        ly = h * (0.60 + i * 0.04)
        LINE(b, OL, (cx - w * 0.18, ly), (cx + w * 0.18, ly), max(1, int(1.2 * s)))
        LINE(b, HI, (cx - w * 0.16, ly + 1.5 * s), (cx + w * 0.16, ly + 1.5 * s), max(1, int(0.8 * s)))
    # big rounded pauldrons
    for sgn in (-1, 1):
        px = cx + sgn * w * 0.21
        ELL(b, OL, px, h * 0.37, w * 0.20, h * 0.16)
        ELL(b, MID, px - sgn * w * 0.01, h * 0.36, w * 0.16, h * 0.12)
        pygame.draw.arc(b, HI, (int(px - w * 0.09), int(h * 0.31), int(w * 0.18), int(h * 0.12)), math.radians(200), math.radians(340), max(1, int(1.4 * s)))
    # great-helm + cross
    hx, hy = cx, h * 0.22
    grad_poly(b, [(hx - w * 0.12, hy - h * 0.08), (hx + w * 0.12, hy - h * 0.08), (hx + w * 0.13, hy + h * 0.09), (hx - w * 0.13, hy + h * 0.09)], HI, LO)
    POLY(b, OL, [(hx - w * 0.135, hy - h * 0.09), (hx + w * 0.135, hy - h * 0.09), (hx - w * 0.135, hy - h * 0.075)])
    ELL(b, OL, hx, hy - h * 0.08, w * 0.27, h * 0.06)
    ELL(b, MID, hx, hy - h * 0.082, w * 0.23, h * 0.045)
    pygame.draw.rect(b, (8, 9, 13), (int(hx - w * 0.12), int(hy - h * 0.005), int(w * 0.24), int(h * 0.022)))   # slit
    LINE(b, BR, (hx, hy - h * 0.075), (hx, hy + h * 0.085), max(2, int(2.6 * s)))   # cross
    LINE(b, BR, (hx - w * 0.12, hy + h * 0.03), (hx + w * 0.12, hy + h * 0.03), max(2, int(2.6 * s)))
    rivets(b, [(hx - w * 0.10, hy + h * 0.07), (hx + w * 0.10, hy + h * 0.07)], s)
    plume(b, hx - w * 0.0, hy - h * 0.085, RED, s, reach=10, up=30)
    pygame.draw.circle(b, RED, (int(hx), int(hy - h * 0.085)), 0)
    # longsword planted point-down, centre-front
    LINE(b, MID, (cx, h * 0.50), (cx, h * 0.86), max(3, int(5 * s)))
    LINE(b, HI, (cx - 1.4 * s, h * 0.50), (cx - 1.4 * s, h * 0.86), max(1, int(1.4 * s)))
    LINE(b, BR, (cx - w * 0.07, h * 0.50), (cx + w * 0.07, h * 0.50), max(3, int(4 * s)))   # quillons
    pygame.draw.circle(b, BR, (int(cx), int(h * 0.46)), int(4 * s))                         # pommel
    pygame.draw.circle(b, BRH, (int(cx - s), int(h * 0.46 - s)), int(2 * s))
    LINE(b, (74, 54, 36), (cx, h * 0.46), (cx, h * 0.50), max(2, int(3 * s)))               # grip
    # two gauntlets clasping the grip (one rounded band, no overlap glitch)
    ELL(b, OL, cx, h * 0.49, w * 0.16, h * 0.07)
    ELL(b, MID, cx, h * 0.485, w * 0.135, h * 0.055)
    pygame.draw.arc(b, HI, (int(cx - w * 0.066), int(h * 0.465), int(w * 0.132), int(h * 0.05)), math.radians(200), math.radians(340), max(1, int(1.2 * s)))
    LINE(b, OL, (cx, h * 0.465), (cx, h * 0.515), max(1, int(1.0 * s)))                      # knuckle split


# ═══════════════════════════════════════════════════════════════════════════════
# CONCEPT B — "Bulwark": short & WIDE; a huge round shield fills the front; the
# knight peeks over the rim under a wide kettle-hat; mace on the shoulder.  Circle.
# ═══════════════════════════════════════════════════════════════════════════════
def concept_bulwark(b, s):
    w, h = b.get_size()
    OL, LO, MID, HI = (26, 30, 40), (84, 92, 112), (158, 170, 196), (242, 248, 255)
    BR, BRH, AZ, GOLD = (214, 180, 104), (255, 236, 176), (54, 96, 178), (232, 196, 90)
    cx, cy = w * 0.5, h * 0.58
    macaw_tail(b, w * 0.22, h * 0.55, h * 0.17, ang=205)
    # stocky legs
    for sgn in (-1, 1):
        lx = cx + sgn * w * 0.16
        grad_poly(b, [(lx - w * 0.07, h * 0.74), (lx + w * 0.07, h * 0.74), (lx + w * 0.06, h * 0.93), (lx - w * 0.06, h * 0.93)], MID, LO)
        ELL(b, OL, lx, h * 0.94, w * 0.18, h * 0.05)
    # head peeking over (helmeted) — kettle hat with wide brim
    hx, hy = cx + w * 0.06, h * 0.26
    beak(b, hx + w * 0.07, hy + h * 0.02, h * 0.022, face=1)
    pygame.draw.circle(b, (20, 22, 30), (int(hx + w * 0.02), int(hy)), int(h * 0.012))  # eye
    grad_poly(b, [(hx - w * 0.10, hy - h * 0.10), (hx + w * 0.10, hy - h * 0.10), (hx + w * 0.10, hy + h * 0.02), (hx - w * 0.10, hy + h * 0.02)], HI, LO)
    ELL(b, OL, hx, hy - h * 0.10, w * 0.22, h * 0.05)                          # dome top
    ELL(b, MID, hx, hy - h * 0.10, w * 0.18, h * 0.038)
    POLY(b, OL, [(hx - w * 0.18, hy + h * 0.0), (hx + w * 0.18, hy + h * 0.0), (hx + w * 0.13, hy + h * 0.05), (hx - w * 0.13, hy + h * 0.05)])  # brim
    LINE(b, BRH, (hx - w * 0.16, hy + h * 0.012), (hx + w * 0.16, hy + h * 0.012), max(1, int(1.4 * s)))
    # mace resting on the (far) shoulder
    LINE(b, (74, 54, 36), (cx - w * 0.22, h * 0.40), (cx - w * 0.30, h * 0.16), max(2, int(3.4 * s)))
    mhx, mhy = cx - w * 0.31, h * 0.13
    for a in range(0, 360, 60):
        ex, ey = mhx + 0.10 * w * math.cos(math.radians(a)), mhy + 0.10 * w * math.sin(math.radians(a))
        LINE(b, OL, (mhx, mhy), (ex, ey), max(2, int(3 * s)))
        LINE(b, MID, (mhx, mhy), (ex, ey), max(1, int(1.4 * s)))
    pygame.draw.circle(b, OL, (int(mhx), int(mhy)), int(0.07 * w))
    pygame.draw.circle(b, MID, (int(mhx), int(mhy)), int(0.055 * w))
    pygame.draw.circle(b, HI, (int(mhx - 2 * s), int(mhy - 2 * s)), int(0.02 * w))
    # HUGE round shield filling the front
    r = w * 0.34
    pygame.draw.circle(b, OL, (int(cx), int(cy)), int(r))
    pygame.draw.circle(b, MID, (int(cx), int(cy)), int(r - 3 * s))
    pygame.draw.circle(b, AZ, (int(cx), int(cy)), int(r - 6 * s))
    LINE(b, GOLD, (cx, cy - r + 8 * s), (cx, cy + r - 8 * s), max(3, int(5 * s)))
    LINE(b, GOLD, (cx - r + 8 * s, cy), (cx + r - 8 * s, cy), max(3, int(5 * s)))
    pygame.draw.circle(b, BR, (int(cx), int(cy)), int(0.08 * w))                # boss
    pygame.draw.circle(b, BRH, (int(cx - 3 * s), int(cy - 3 * s)), int(0.03 * w))
    rivets(b, [(cx + (r - 5 * s) * math.cos(math.radians(a)), cy + (r - 5 * s) * math.sin(math.radians(a))) for a in range(0, 360, 30)], s)
    pygame.draw.arc(b, HI, (int(cx - r + 4 * s), int(cy - r + 4 * s), int(2 * (r - 4 * s)), int(2 * (r - 4 * s))), math.radians(120), math.radians(210), max(1, int(2 * s)))


# ═══════════════════════════════════════════════════════════════════════════════
# CONCEPT C — "Seraph Paladin": huge spread FEATHERED wings dominate; slim gold &
# white body; tall halberd held vertical; radiant halo crest.  Wide triangle.
# ═══════════════════════════════════════════════════════════════════════════════
def concept_seraph(b, s):
    w, h = b.get_size()
    OL, LO, MID, HI = (40, 36, 20), (150, 120, 56), (224, 188, 104), (255, 244, 196)
    WHT, WSH, GOLD = (250, 250, 246), (206, 214, 232), (236, 200, 96)
    cx, cy = w * 0.5, h * 0.5
    # radiant rays behind
    for k in range(16):
        a = k * math.tau / 16
        LINE(b, (255, 240, 180, 70), (cx + 0.18 * w * math.cos(a), cy * 0.9 + 0.18 * w * math.sin(a)),
             (cx + 0.5 * w * math.cos(a), cy * 0.9 + 0.5 * w * math.sin(a)), max(1, int(1.6 * s)))
    # big feathered wings spread wide (drawn behind body)
    for sgn in (-1, 1):
        root = (cx + sgn * w * 0.10, h * 0.40)
        tip = (cx + sgn * w * 0.46, h * 0.16)
        lead = qbez(root, (cx + sgn * w * 0.30, h * 0.16), tip, 20)
        trail = qbez(tip, (cx + sgn * w * 0.30, h * 0.52), root, 20)
        POLY(b, WSH, lead + trail)
        POLY(b, WHT, [(x + (root[0] - x) * 0.12, y + (root[1] - y) * 0.06) for x, y in lead + trail])
        for fk in range(5):
            fb = lead[3 + fk * 3]
            LINE(b, WSH, fb, (fb[0] + sgn * w * 0.05, fb[1] + h * 0.05), max(1, int(1.2 * s)))
        LINE(b, GOLD, root, tip, max(1, int(1.4 * s)))
    macaw_tail(b, cx - w * 0.06, h * 0.72, h * 0.13, ang=160)
    # slim gilded body
    body = [(cx - w * 0.12, h * 0.40), (cx + w * 0.12, h * 0.40), (cx + w * 0.10, h * 0.62), (cx + w * 0.06, h * 0.78), (cx - w * 0.06, h * 0.78), (cx - w * 0.10, h * 0.62)]
    POLY(b, OL, body)
    grad_poly(b, body, HI, LO)
    LINE(b, HI, (cx, h * 0.42), (cx, h * 0.76), max(1, int(1.6 * s)))
    for i in range(3):
        ly = h * (0.64 + i * 0.045)
        LINE(b, OL, (cx - w * 0.10, ly), (cx + w * 0.10, ly), max(1, int(1.0 * s)))
    # head: open helm with halo, beak showing
    hx, hy = cx, h * 0.30
    ELL(b, GOLD, hx, hy, w * 0.16, h * 0.13)
    ELL(b, HI, hx - w * 0.02, hy - h * 0.01, w * 0.10, h * 0.07)
    beak(b, hx + w * 0.07, hy + h * 0.012, h * 0.02, face=1)
    pygame.draw.circle(b, (24, 20, 12), (int(hx + w * 0.02), int(hy)), int(h * 0.011))
    pygame.draw.circle(b, (255, 248, 196), (int(hx), int(hy - h * 0.11)), int(w * 0.10), max(2, int(2.4 * s)))   # halo
    # tall halberd, vertical, right of body
    px = cx + w * 0.22
    LINE(b, (74, 54, 36), (px, h * 0.86), (px, h * 0.10), max(2, int(3.4 * s)))
    POLY(b, MID, [(px, h * 0.06), (px + w * 0.03, h * 0.16), (px, h * 0.20), (px - w * 0.03, h * 0.16)])         # spear point
    POLY(b, MID, [(px, h * 0.18), (px + w * 0.11, h * 0.16), (px + w * 0.08, h * 0.26), (px, h * 0.24)])         # axe blade
    POLY(b, OL, [(px, h * 0.18), (px + w * 0.11, h * 0.16), (px + w * 0.08, h * 0.26), (px, h * 0.24)], )
    POLY(b, MID, [(px, h * 0.185), (px + w * 0.095, h * 0.17), (px + w * 0.07, h * 0.25), (px, h * 0.23)])


# ═══════════════════════════════════════════════════════════════════════════════
# CONCEPT D — "Dread Marauder": hunched, asymmetric, menacing; oversized SPIKED
# pauldrons, horned helm low between them, tattered cape, two-handed greataxe.  Jagged.
# ═══════════════════════════════════════════════════════════════════════════════
def concept_marauder(b, s):
    w, h = b.get_size()
    OL, LO, MID, HI = (8, 9, 14), (44, 40, 48), (96, 96, 110), (180, 184, 200)
    RED, RUST, BONE = (150, 36, 40), (120, 48, 36), (210, 200, 180)
    cx, cy = w * 0.52, h * 0.52
    # tattered cape behind
    cape = [(cx - w * 0.14, h * 0.30), (cx + w * 0.10, h * 0.32), (cx + w * 0.16, h * 0.72),
            (cx + w * 0.04, h * 0.64), (cx - w * 0.02, h * 0.82), (cx - w * 0.12, h * 0.66), (cx - w * 0.22, h * 0.78), (cx - w * 0.26, h * 0.44)]
    POLY(b, (40, 14, 16), cape)
    POLY(b, RED, [(x + (cx - x) * 0.10, y * 0.99) for x, y in cape])
    macaw_tail(b, cx - w * 0.20, h * 0.62, h * 0.15, ang=210)
    # hunched body
    body = [(cx - w * 0.20, h * 0.44), (cx + w * 0.18, h * 0.42), (cx + w * 0.20, h * 0.66), (cx + w * 0.08, h * 0.80), (cx - w * 0.14, h * 0.78), (cx - w * 0.22, h * 0.60)]
    POLY(b, (4, 5, 9), body)
    grad_poly(b, body, MID, LO)
    LINE(b, HI, (cx, h * 0.46), (cx + w * 0.01, h * 0.74), max(1, int(1.4 * s)))
    # horned helm low/forward (between shoulders)
    hx, hy = cx + w * 0.04, h * 0.40
    for sgn in (-1, 1):
        curve = qbez((hx + sgn * w * 0.08, hy - h * 0.02), (hx + sgn * w * 0.18, hy - h * 0.14), (hx + sgn * w * 0.24, hy - h * 0.02), 12)
        pygame.draw.lines(b, OL, False, [(int(x), int(y)) for x, y in curve], max(3, int(4.4 * s)))
        pygame.draw.lines(b, BONE, False, [(int(x - s), int(y)) for x, y in curve], max(1, int(1.4 * s)))
    ELL(b, OL, hx, hy, w * 0.20, h * 0.16)
    ELL(b, MID, hx - w * 0.01, hy - h * 0.005, w * 0.16, h * 0.12)
    ELL(b, HI, hx - w * 0.03, hy - h * 0.02, w * 0.06, h * 0.04)
    LINE(b, (180, 40, 40), (hx - w * 0.06, hy + h * 0.01), (hx + w * 0.07, hy + h * 0.025), max(2, int(2.6 * s)))   # glowing slit
    # oversized spiked pauldrons
    for sgn, sc in ((-1, 1.15), (1, 1.0)):
        px, py = cx + sgn * w * 0.22, h * 0.42
        ELL(b, OL, px, py, w * 0.22 * sc, h * 0.17 * sc)
        ELL(b, LO, px - sgn * w * 0.01, py, w * 0.17 * sc, h * 0.13 * sc)
        for a in (200, 235, 270) if sgn < 0 else (270, 305, 340):
            ex, ey = px + 0.13 * w * sc * math.cos(math.radians(a)), py + 0.11 * h * sc * math.sin(math.radians(a))
            POLY(b, OL, [(px, py - 0.02 * h), (px, py + 0.02 * h), (ex, ey)])
            POLY(b, BONE, [(px, py - 0.012 * h), (px, py + 0.012 * h), (ex * 0.99 + px * 0.01, ey * 0.99 + py * 0.01)])
    # two-handed greataxe to the side
    ax = cx + w * 0.30
    LINE(b, (60, 40, 26), (cx + w * 0.10, h * 0.74), (ax, h * 0.20), max(3, int(4 * s)))
    POLY(b, OL, [(ax, h * 0.16), (ax + w * 0.16, h * 0.12), (ax + w * 0.18, h * 0.30), (ax, h * 0.30)])
    POLY(b, MID, [(ax, h * 0.18), (ax + w * 0.12, h * 0.15), (ax + w * 0.135, h * 0.285), (ax, h * 0.28)])
    pygame.draw.arc(b, HI, (int(ax), int(h * 0.13), int(w * 0.18), int(h * 0.2)), math.radians(300), math.radians(40), max(1, int(1.4 * s)))


# ═══════════════════════════════════════════════════════════════════════════════
# CONCEPT E — "Royal Champion": regal, gilded, symmetric; crowned great-helm, a
# heraldic surcoat over gold plate, ermine cape, ornate sceptre-mace + shield.
# ═══════════════════════════════════════════════════════════════════════════════
def concept_royal(b, s):
    w, h = b.get_size()
    OL, LO, MID, HI = (44, 32, 12), (150, 116, 48), (224, 186, 96), (255, 244, 190)
    GOLD, GOLDH, GUL, ERM = (236, 200, 96), (255, 236, 168), (170, 46, 50), (244, 240, 230)
    cx = w * 0.5
    # ermine cape behind (white w/ black tails)
    cape = [(cx - w * 0.18, h * 0.34), (cx + w * 0.18, h * 0.34), (cx + w * 0.26, h * 0.86), (cx - w * 0.26, h * 0.86)]
    POLY(b, (210, 208, 200), cape)
    POLY(b, ERM, [(x + (cx - x) * 0.08, y * 0.995) for x, y in cape])
    for (ex, ey) in [(cx - w * 0.12, h * 0.5), (cx + w * 0.1, h * 0.52), (cx - w * 0.02, h * 0.66), (cx + w * 0.16, h * 0.7), (cx - w * 0.18, h * 0.72)]:
        pygame.draw.circle(b, (40, 38, 36), (int(ex), int(ey)), max(1, int(2 * s)))
    macaw_tail(b, cx - w * 0.20, h * 0.6, h * 0.13, ang=205)
    # legs
    for sgn in (-1, 1):
        lx = cx + sgn * w * 0.11
        grad_poly(b, [(lx - w * 0.05, h * 0.74), (lx + w * 0.05, h * 0.74), (lx + w * 0.045, h * 0.92), (lx - w * 0.045, h * 0.92)], MID, LO)
        ELL(b, OL, lx, h * 0.93, w * 0.14, h * 0.045)
    # gilded cuirass
    body = [(cx - w * 0.19, h * 0.36), (cx + w * 0.19, h * 0.36), (cx + w * 0.2, h * 0.54), (cx + w * 0.12, h * 0.72), (cx - w * 0.12, h * 0.72), (cx - w * 0.2, h * 0.54)]
    POLY(b, OL, body)
    grad_poly(b, body, HI, LO)
    # heraldic surcoat (per-pale gules / or) over the chest
    sc = [(cx - w * 0.11, h * 0.38), (cx + w * 0.11, h * 0.38), (cx + w * 0.08, h * 0.70), (cx, h * 0.74), (cx - w * 0.08, h * 0.70)]
    tmp = pygame.Surface(b.get_size(), pygame.SRCALPHA)
    POLY(tmp, GUL, [(cx - w * 0.11, h * 0.38), (cx, h * 0.38), (cx, h * 0.74), (cx - w * 0.08, h * 0.70)])
    POLY(tmp, GOLD, [(cx, h * 0.38), (cx + w * 0.11, h * 0.38), (cx + w * 0.08, h * 0.70), (cx, h * 0.74)])
    mm = pygame.Surface(b.get_size(), pygame.SRCALPHA); POLY(mm, (255, 255, 255, 255), sc)
    tmp.blit(mm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN); b.blit(tmp, (0, 0))
    LINE(b, GOLDH, (cx - w * 0.11, h * 0.38), (cx + w * 0.11, h * 0.38), max(2, int(2 * s)))
    # ornate pauldrons w/ gems
    for sgn in (-1, 1):
        px = cx + sgn * w * 0.20
        ELL(b, OL, px, h * 0.39, w * 0.18, h * 0.14)
        ELL(b, GOLD, px - sgn * w * 0.01, h * 0.38, w * 0.14, h * 0.10)
        pygame.draw.circle(b, GUL, (int(px), int(h * 0.39)), int(0.022 * w))
    # crowned great-helm
    hx, hy = cx, h * 0.24
    grad_poly(b, [(hx - w * 0.11, hy - h * 0.07), (hx + w * 0.11, hy - h * 0.07), (hx + w * 0.12, hy + h * 0.09), (hx - w * 0.12, hy + h * 0.09)], HI, LO)
    pygame.draw.rect(b, (40, 30, 12), (int(hx - w * 0.10), int(hy + h * 0.005), int(w * 0.20), int(h * 0.02)))    # slit
    LINE(b, GUL, (hx, hy - h * 0.06), (hx, hy + h * 0.085), max(2, int(2.2 * s)))
    # crown on top
    cy2 = hy - h * 0.075
    POLY(b, GOLD, [(hx - w * 0.12, cy2), (hx + w * 0.12, cy2), (hx + w * 0.10, cy2 - h * 0.02), (hx - w * 0.10, cy2 - h * 0.02)])
    for k in (-1, 0, 1):
        bx = hx + k * w * 0.08
        POLY(b, GOLD, [(bx - w * 0.025, cy2 - h * 0.01), (bx + w * 0.025, cy2 - h * 0.01), (bx, cy2 - h * 0.06)])
        pygame.draw.circle(b, GUL if k == 0 else (70, 170, 110), (int(bx), int(cy2 - h * 0.055)), max(1, int(1.6 * s)))
    # sceptre-mace held right
    px = cx + w * 0.22
    LINE(b, (74, 54, 36), (px, h * 0.74), (px, h * 0.26), max(2, int(3.2 * s)))
    pygame.draw.circle(b, GOLD, (int(px), int(h * 0.22)), int(0.06 * w))
    pygame.draw.circle(b, GOLDH, (int(px - 2 * s), int(h * 0.22 - 2 * s)), int(0.025 * w))
    POLY(b, GOLD, [(px - w * 0.03, h * 0.165), (px + w * 0.03, h * 0.165), (px, h * 0.12)])


CONCEPTS = [
    ("A · Sentinel", concept_sentinel),
    ("B · Bulwark", concept_bulwark),
    ("C · Seraph Paladin", concept_seraph),
    ("D · Dread Marauder", concept_marauder),
    ("E · Royal Champion", concept_royal),
]


def _panel(label, fn, pw, ph):
    surf = pygame.Surface((R.W, R.H)); R.backdrop(surf)
    char = pygame.Surface((CW * SS, CH * SS), pygame.SRCALPHA)
    fn(char, SS)
    small = pygame.transform.smoothscale(char, (CW, CH))
    surf.blit(small, small.get_rect(center=(int(R.W * 0.5), int(R.H * 0.46))).topleft)
    panel = pygame.transform.smoothscale(surf, (pw, ph))
    f = pygame.font.SysFont("Arial", 15, bold=True)
    chip = f.render(label, True, (255, 255, 255))
    bg = pygame.Surface((chip.get_width() + 12, chip.get_height() + 6), pygame.SRCALPHA); bg.fill((0, 0, 0, 190))
    panel.blit(bg, (6, ph - 26)); panel.blit(chip, (12, ph - 23))
    return panel


def main():
    pw, ph, gap = int(R.W * 0.6), int(R.H * 0.6), 12
    th = 44
    sheet = pygame.Surface((pw * 5 + gap * 6, ph + th + gap))
    sheet.fill((16, 18, 26))
    tf = pygame.font.SysFont("Arial", 22, bold=True)
    sheet.blit(tf.render("Knight — 5 INDEPENDENT concepts (each drawn bottom-up)", True, (255, 232, 168)), (gap + 2, 11))
    for i, (label, fn) in enumerate(CONCEPTS):
        sheet.blit(_panel(label, fn, pw, ph), (gap + i * (pw + gap), th))
    out = os.path.join(OUT, "knight_concepts.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet.get_width()}x{sheet.get_height()})")
    # a 5-up zoom strip for detail
    tile, g2 = 320, 8
    z = pygame.Surface((tile * 5 + g2 * 6, tile + 34))
    z.fill((16, 18, 26))
    zf = pygame.font.SysFont("Arial", 14, bold=True)
    for i, (label, fn) in enumerate(CONCEPTS):
        char = pygame.Surface((CW * SS, CH * SS), pygame.SRCALPHA); fn(char, SS)
        small = pygame.transform.smoothscale(char, (tile, tile))
        x = g2 + i * (tile + g2)
        z.blit(small, (x, g2))
        z.blit(zf.render(label, True, (255, 232, 168)), (x + 6, tile + g2 + 6))
    out2 = os.path.join(OUT, "knight_concepts_zoom.png")
    pygame.image.save(z, out2)
    print(f"saved {out2}")


if __name__ == "__main__":
    main()
