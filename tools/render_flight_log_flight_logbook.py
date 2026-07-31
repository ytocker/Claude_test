"""Round-2 review render of the `flight_logbook` Flight Log concept.

The screen is a pilot's ledger page rendered in Skybit's own night palette
rather than beige parchment — the page is a lifted indigo-black plate, the
ink is warm cream, and gold carries all structure. The run is told twice:
once as a hand-drawn route through the unruled remarks box at the top (with
doodles marking the landmarks the player actually reached), and once as
ruled ledger entries at the bottom, where the pillar count is written huge
and circled so a glance lands on the only number that matters.

Offline tool — writes docs/flight_log_screen/flight_logbook/round_2.png.
Nothing here is imported by the game.
"""
from __future__ import annotations

import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

W, H = 360, 640

BG = (8, 8, 20)
PAGE_TOP = (32, 30, 62)
PAGE_BOT = (24, 22, 48)
PAGE_LIP = (52, 48, 90)
GOLD = (240, 192, 64)
GOLD_MUTED = (240, 192, 64)
INK = (228, 218, 198)
RULE_BLUE = (108, 112, 156)
SCARLET = (172, 40, 32)

_FONT_BOLD = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          os.pardir, "game", "assets",
                          "LiberationSans-Bold.ttf")

# ── page geometry ────────────────────────────────────────────────────────────
PAGE = pygame.Rect(8, 10, 344, 620)
MARGIN_X = PAGE.x + 66            # the ledger's vertical margin rule
CONTENT_X0 = MARGIN_X + 10
CONTENT_X1 = PAGE.right - 16

HEAD_RULE_Y = 52
REMARKS = pygame.Rect(CONTENT_X0, 86, CONTENT_X1 - CONTENT_X0, 182)
ENTRY_DIV_Y = 300
RULE_Y0, RULE_STEP, RULE_N = 320, 30, 10

PHASE_TOP, PHASE_BOT = 66, 606    # margin column maps phase 0..1 down the page

PHASE_MARKS = [
    (0.231, ["GOLDEN", "HOUR"]),
    (0.363, ["SUNSET"]),
    (0.513, ["DUSK"]),
    (0.644, ["NIGHT"]),
    (0.794, ["PREDAWN"]),
]

GEYSER_PHASE = 0.156
LANDMARKS = [                     # (gate kind, gate value, doodle)
    ("phase", GEYSER_PHASE, "geyser"),
    ("pillar", 50, "coins"),
    ("pillar", 65, "clown"),
    ("pillar", 70, "rain"),
    ("pillar", 139, "snow"),
]

RUNS = [
    dict(tag="RUN A", pillars=25, phase=0.184, day=1, time="0:47",
         cause="GEYSER", seed=4021),
    dict(tag="RUN B", pillars=180, phase=0.031, day=2, time="5:30",
         cause="SNOW", seed=9137),
]

_fonts: dict = {}


def _font(size):
    f = _fonts.get(size)
    if f is None:
        f = pygame.font.Font(_FONT_BOLD, size)
        _fonts[size] = f
    return f


def _fade(img, alpha):
    """Scale a rendered glyph's alpha. set_alpha on a per-pixel-alpha surface
    is unreliable across SDL builds; a multiply blit is not."""
    out = img.convert_alpha()
    out.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    return out


def _caps(surf, txt, x, y, size, color, tracking=1, anchor="left", alpha=255):
    """Letter-spaced caps; `y` is the vertical centre. Tracking is what keeps
    7px ledger labels reading as lettering rather than a smudge."""
    f = _font(size)
    glyphs = [f.render(c, True, color) for c in txt]
    total = sum(g.get_width() for g in glyphs) + tracking * (len(glyphs) - 1)
    gx = x if anchor == "left" else (x - total if anchor == "right"
                                     else x - total // 2)
    gy = y - (glyphs[0].get_height() // 2 if glyphs else 0)
    for img in glyphs:
        surf.blit(_fade(img, alpha) if alpha < 255 else img, (gx, gy))
        gx += img.get_width() + tracking
    return total


def _caps_w(txt, size, tracking=1):
    f = _font(size)
    return sum(f.size(c)[0] for c in txt) + tracking * (len(txt) - 1)


def _mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ── the page itself ──────────────────────────────────────────────────────────

def _page(surf, seed):
    shadow = pygame.Surface((PAGE.w + 8, PAGE.h + 8), pygame.SRCALPHA)
    for i in range(4):
        pygame.draw.rect(shadow, (0, 0, 0, 46 - i * 10),
                         (4 - i, 4 - i, PAGE.w + i * 2, PAGE.h + i * 2),
                         border_radius=3)
    surf.blit(shadow, (PAGE.x - 2, PAGE.y + 1))
    for i in range(PAGE.h):
        pygame.draw.line(surf, _mix(PAGE_TOP, PAGE_BOT, i / (PAGE.h - 1)),
                         (PAGE.x, PAGE.y + i), (PAGE.right - 1, PAGE.y + i))
    # Paper tooth: without it the plate reads as flat vector fill instead of a
    # sheet with a surface.
    rnd = random.Random(seed)
    grain = pygame.Surface((PAGE.w, PAGE.h), pygame.SRCALPHA)
    for _ in range(2600):
        gx, gy = rnd.randrange(PAGE.w), rnd.randrange(PAGE.h)
        if rnd.random() < 0.55:
            grain.set_at((gx, gy), (150, 150, 210, rnd.randint(6, 16)))
        else:
            grain.set_at((gx, gy), (0, 0, 14, rnd.randint(10, 26)))
    surf.blit(grain, PAGE.topleft)
    lip = pygame.Surface((PAGE.w, PAGE.h), pygame.SRCALPHA)
    pygame.draw.line(lip, (*PAGE_LIP, 190), (0, 0), (PAGE.w - 1, 0))
    pygame.draw.line(lip, (*PAGE_LIP, 140), (0, 0), (0, PAGE.h - 1))
    pygame.draw.line(lip, (0, 0, 10, 160), (0, PAGE.h - 1),
                     (PAGE.w - 1, PAGE.h - 1))
    pygame.draw.line(lip, (0, 0, 10, 120), (PAGE.w - 1, 0),
                     (PAGE.w - 1, PAGE.h - 1))
    surf.blit(lip, PAGE.topleft)


def _binding(surf):
    """Stitches down the gutter. Six is enough to read as a sewn signature
    without turning the margin into a zip."""
    crease = pygame.Surface((3, PAGE.h - 24), pygame.SRCALPHA)
    crease.fill((0, 0, 12, 70))
    crease.fill((40, 40, 74, 60), (2, 0, 1, PAGE.h - 24))
    surf.blit(crease, (PAGE.x + 20, PAGE.y + 12))
    x = PAGE.x + 9
    for i in range(6):
        y = PAGE.y + 46 + i * 104
        slit = pygame.Surface((7, 19), pygame.SRCALPHA)
        slit.fill((0, 0, 10, 120))
        surf.blit(slit, (x - 2, y - 3))
        st = pygame.Surface((4, 14), pygame.SRCALPHA)
        st.fill((*GOLD_MUTED, 190))
        st.fill((*_mix(GOLD_MUTED, GOLD, 0.5), 210), (0, 0, 4, 4))
        surf.blit(st, (x, y))


def _margin_rule(surf):
    lay = pygame.Surface((4, PAGE.h), pygame.SRCALPHA)
    pygame.draw.line(lay, (*GOLD_MUTED, 175), (1, 0), (1, PAGE.h - 1))
    pygame.draw.line(lay, (0, 0, 12, 90), (2, 0), (2, PAGE.h - 1))
    surf.blit(lay, (MARGIN_X - 1, PAGE.y + 14), (0, 0, 4, PAGE.h - 28))


def _ruled_lines(surf):
    """Rules live only in the ledger half — the blank top third is what makes
    the remarks box read as a place to draw rather than a place to write."""
    lay = pygame.Surface((PAGE.w, PAGE.h), pygame.SRCALPHA)
    for i in range(RULE_N):
        y = RULE_Y0 + i * RULE_STEP - PAGE.y
        pygame.draw.line(lay, (*RULE_BLUE, 100), (MARGIN_X - PAGE.x - 6, y),
                         (PAGE.right - 16 - PAGE.x, y))
    surf.blit(lay, PAGE.topleft)


def _header(surf, run):
    _caps(surf, "FLIGHT LOG", PAGE.x + 14, 32, 18, GOLD, tracking=3)
    _caps(surf, "SKYBIT", PAGE.right - 16, 34, 8, GOLD_MUTED, tracking=3,
          anchor="right", alpha=170)
    rule = pygame.Surface((PAGE.w - 30, 1), pygame.SRCALPHA)
    span = PAGE.w - 30
    for i in range(span):
        t = min(i, span - 1 - i) / 40.0
        rule.set_at((i, 0), (*GOLD_MUTED, int(160 * min(1.0, t))))
    surf.blit(rule, (PAGE.x + 14, HEAD_RULE_Y))
    _caps(surf, "REMARKS", REMARKS.x, 70, 7, GOLD_MUTED, tracking=3, alpha=185)
    _caps(surf, "DAY %d" % run["day"], CONTENT_X1, 70, 7, GOLD_MUTED,
          tracking=3, anchor="right", alpha=185)


def _margin_notes(surf, run):
    """Phase labels sit at their true fraction of the day, tilted like notes
    scrawled sideways in a margin. They double as the page's time axis."""
    death_total = min(1.0, (run["day"] - 1) + run["phase"])
    for phase, lines in PHASE_MARKS:
        reached = phase <= death_total
        alpha = 150 if reached else 60
        y = PHASE_TOP + (PHASE_BOT - PHASE_TOP) * phase
        blk_h = 9 * len(lines)
        blk_w = max(_caps_w(t, 7, 1) for t in lines)
        blk = pygame.Surface((blk_w + 2, blk_h + 2), pygame.SRCALPHA)
        for i, t in enumerate(lines):
            _caps(blk, t, blk_w, 5 + i * 9, 7, INK, tracking=1, anchor="right")
        blk = _fade(blk, alpha)
        rot = pygame.transform.rotate(blk, 15)
        r = rot.get_rect()
        r.right, r.centery = MARGIN_X - 7, int(y)
        surf.blit(rot, r.topleft)
        tick = pygame.Surface((5, 1), pygame.SRCALPHA)
        tick.fill((*GOLD_MUTED, 110 if reached else 50))
        surf.blit(tick, (MARGIN_X - 4, int(y)))

    # Gold span bracket at the death position.
    y = int(PHASE_TOP + (PHASE_BOT - PHASE_TOP) * death_total)
    bracket = pygame.Surface((12, 10), pygame.SRCALPHA)
    pygame.draw.line(bracket, (*GOLD, 240), (0, 0), (0, 9), 2)
    pygame.draw.line(bracket, (*GOLD, 240), (0, 0), (10, 0), 2)
    pygame.draw.line(bracket, (*GOLD, 240), (0, 9), (10, 9), 2)
    surf.blit(bracket, (MARGIN_X - 13, y - 5))


# ── the route through the remarks box ────────────────────────────────────────

def _wobble(s, ph):
    """A confident pen line drifts; it does not vibrate. Two long harmonics
    (16px and 41px) keep the total under 1.5px of deviation."""
    return (0.92 * math.sin(s / 16.0 * math.tau + ph[0])
            + 0.5 * math.sin(s / 41.0 * math.tau + ph[1]))


def build_route(rows, seed):
    """Boustrophedon pen run that always fills the remarks box: more pillars
    buy more fold-back rows, never a shorter line."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, math.tau) for _ in range(2)]
    # The row ends are inset so the fold-back arcs and the death mark struck
    # on the last point both stay inside the remarks box.
    x0, x1 = REMARKS.x + 16, REMARKS.right - 16
    if rows == 1:
        ys = [REMARKS.y + REMARKS.h * 0.5]
    else:
        # Inset far enough that a doodle hung off the first or last row stays
        # inside the remarks box instead of climbing into the header.
        top, bot = REMARKS.y + 30, REMARKS.bottom - 30
        ys = [top + (bot - top) * i / (rows - 1) for i in range(rows)]
    pts, s = [], 0.0
    for i, ry in enumerate(ys):
        ltr = i % 2 == 0
        ax, bx = (x0, x1) if ltr else (x1, x0)
        step = 2.0 if ltr else -2.0
        x = ax
        while (x <= bx) if ltr else (x >= bx):
            pts.append((x, ry + _wobble(s, ph)))
            s += 2.0
            x += step
        pts.append((bx, ry + _wobble(s, ph)))
        if i < len(ys) - 1:
            ny = ys[i + 1]
            cy, r = (ry + ny) / 2.0, (ny - ry) / 2.0
            sgn = 1 if ltr else -1
            for k in range(1, 19):
                a = -math.pi / 2 + math.pi * k / 18
                pts.append((bx + sgn * (r * 0.4) * math.cos(a) + _wobble(s, ph),
                            cy + r * math.sin(a)))
                s += r * math.pi / 18
    return pts


def _arc_table(pts):
    tab, d = [0.0], 0.0
    for i in range(1, len(pts)):
        d += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        tab.append(d)
    return tab


def sample(pts, tab, t):
    """Point + unit tangent at fraction `t` of the pen run."""
    target = max(0.0, min(1.0, t)) * tab[-1]
    lo, hi = 0, len(tab) - 1
    while lo < hi - 1:
        mid = (lo + hi) // 2
        if tab[mid] <= target:
            lo = mid
        else:
            hi = mid
    seg = max(1e-6, tab[hi] - tab[lo])
    f = (target - tab[lo]) / seg
    ax, ay = pts[lo]
    bx, by = pts[hi]
    px, py = ax + (bx - ax) * f, ay + (by - ay) * f
    tx, ty = bx - ax, by - ay
    n = max(1e-6, math.hypot(tx, ty))
    return px, py, tx / n, ty / n


def _draw_route(surf, pts, death_frac=1.0):
    tab = _arc_table(pts)
    total_len = tab[-1]
    death_len = total_len * min(1.0, death_frac)

    # Split pts into reached and ghost segments
    reached_pts = []
    ghost_pts = []
    for i, pt in enumerate(pts):
        d = tab[i]
        if d <= death_len:
            reached_pts.append(pt)
        else:
            if not ghost_pts and reached_pts:
                ghost_pts.append(reached_pts[-1])
            ghost_pts.append(pt)

    lay = pygame.Surface((W, H), pygame.SRCALPHA)
    if len(reached_pts) >= 2:
        pygame.draw.lines(lay, (0, 0, 12, 120), False,
                          [(x + 1, y + 2) for x, y in reached_pts], 2)
        pygame.draw.lines(lay, (*INK, 232), False, reached_pts, 2)

    # Ghost dashed continuation for portion ahead
    if len(ghost_pts) >= 2:
        period = 8
        acc = 0.0
        for i in range(1, len(ghost_pts)):
            ax, ay = ghost_pts[i - 1]
            bx, by = ghost_pts[i]
            seg = math.hypot(bx - ax, by - ay)
            drawn = 0.0
            while drawn < seg:
                phase_in_period = acc % period
                remaining = seg - drawn
                if phase_in_period < 4:
                    step = min(4 - phase_in_period, remaining)
                    t0 = drawn / seg
                    t1 = (drawn + step) / seg
                    pygame.draw.line(lay, (*INK, 150),
                                     (int(ax + (bx - ax) * t0), int(ay + (by - ay) * t0)),
                                     (int(ax + (bx - ax) * t1), int(ay + (by - ay) * t1)), 2)
                    drawn += step
                    acc += step
                else:
                    step = min(period - phase_in_period, remaining)
                    drawn += step
                    acc += step

    surf.blit(lay, (0, 0))

    # Macaw head glyph at route start
    sx, sy = pts[0]
    body_r = 6
    pygame.draw.circle(surf, (0, 0, 12, 200), (int(sx) + 1, int(sy) + 1), body_r)
    pygame.draw.circle(surf, GOLD, (int(sx), int(sy)), body_r)
    pygame.draw.circle(surf, (8, 8, 20), (int(sx), int(sy)), body_r - 2)
    # Tiny beak
    pygame.draw.polygon(surf, GOLD, [
        (int(sx) + body_r - 1, int(sy) - 1),
        (int(sx) + body_r + 3, int(sy)),
        (int(sx) + body_r - 1, int(sy) + 2),
    ])


# ── doodles (all ≥2px stroke so they read as pen, not hairline) ──────────────

def _d_geyser(surf, cx, cy, c):
    # Stem
    pygame.draw.line(surf, c, (int(cx), int(cy + 10)), (int(cx), int(cy - 4)), 2)
    # 5 spray rays
    for i, (adeg, length) in enumerate(
            [(-55, 11), (-25, 13), (0, 14), (25, 13), (55, 11)]):
        a = math.radians(-90 + adeg)
        ex = cx + length * math.cos(a)
        ey = cy - 4 + length * math.sin(a)
        pygame.draw.line(surf, c, (int(cx), int(cy - 4)), (int(ex), int(ey)), 2)
    # 2 spatter dots
    for dx, dy in ((-9, -16), (10, -12)):
        pygame.draw.circle(surf, c, (int(cx + dx), int(cy + dy)), 2)


def _d_coins(surf, cx, cy, c):
    for i in range(3):
        a = math.radians(210 + i * 60)
        px = cx + 10 * math.cos(a)
        py = cy + 10 * math.sin(a)
        pygame.draw.circle(surf, c, (int(px), int(py)), 4, 2)


def _d_clown(surf, cx, cy, c):
    pygame.draw.circle(surf, c, (int(cx), int(cy)), 9, 2)
    pygame.draw.circle(surf, c, (int(cx - 3), int(cy - 3)), 2)
    pygame.draw.circle(surf, c, (int(cx + 3), int(cy - 3)), 2)
    pygame.draw.arc(surf, c, pygame.Rect(int(cx - 5), int(cy - 1), 11, 9),
                    math.pi, math.tau, 2)
    pygame.draw.circle(surf, c, (int(cx), int(cy + 2)), 2)
    for sgn in (-1, 1):
        pygame.draw.line(surf, c, (cx + sgn * 7, cy - 6),
                         (cx + sgn * 12, cy - 10), 2)


def _d_rain(surf, cx, cy, c):
    for i in range(4):
        x = cx - 9 + i * 6
        pygame.draw.line(surf, c, (x + 3, cy - 8), (x - 2, cy + 6), 2)


def _d_snow(surf, cx, cy, c):
    r = 9
    for ang in range(0, 360, 60):
        dx = math.cos(math.radians(ang)) * r
        dy = math.sin(math.radians(ang)) * r
        pygame.draw.line(surf, c, (int(cx - dx), int(cy - dy)),
                         (int(cx + dx), int(cy + dy)), 2)


DOODLES = {"geyser": _d_geyser, "coins": _d_coins, "clown": _d_clown,
           "rain": _d_rain, "snow": _d_snow}


def _place_doodles(surf, run, pts, tab):
    """Each landmark the run actually reached gets a doodle hung off the route
    at the point it happened, with a short leader so it reads as annotation."""
    total = run["pillars"]
    per_day = total / max(1e-6, run["day"] - 1 + run["phase"])
    placed = []
    for i, (kind, gate, name) in enumerate(LANDMARKS):
        pillar = gate * per_day if kind == "phase" else gate
        if pillar > total:
            continue
        t = pillar / total
        px, py, _, _ = sample(pts, tab, t)
        # Hung straight above or below the line rather than perpendicular to
        # it: on a fold-back the perpendicular points sideways and throws the
        # doodle clean out of the box.
        side = -1 if i % 2 == 0 else 1
        for _ in range(7):
            cx = min(max(px, REMARKS.x + 13), REMARKS.right - 13)
            cy = py + side * 21
            if cy < REMARKS.y + 12 or cy > REMARKS.bottom - 12:
                side = -side
                cy = py + side * 21
            if all(math.hypot(cx - ox, cy - oy) > 27 for ox, oy in placed):
                break
            t = min(0.985, t + 0.022)
            px, py, _, _ = sample(pts, tab, t)
        placed.append((cx, cy))
        lay = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.line(lay, (*INK, 130), (px, py), (cx, py + side * 10), 2)
        surf.blit(lay, (0, 0))
        sh = pygame.Surface((W, H), pygame.SRCALPHA)
        DOODLES[name](sh, cx + 1, cy + 2, (0, 0, 12, 110))
        surf.blit(sh, (0, 0))
        DOODLES[name](surf, cx, cy, INK)


SCARLET_LIT = (226, 84, 66)


def _death_mark(surf, pts, tab, death_frac=1.0):
    """Struck onto the route where the run ended. Scarlet appears nowhere else
    on the page, so the eye finds it without a legend."""
    px, py, _, _ = sample(pts, tab, min(1.0, death_frac))
    rnd = random.Random(77)
    glow = pygame.Surface((34, 34), pygame.SRCALPHA)
    for r in range(13, 0, -1):
        pygame.draw.circle(glow, (*SCARLET_LIT, int(34 * (1 - r / 13.0) ** 1.4)),
                           (17, 17), r)
    surf.blit(glow, (px - 17, py - 17))
    for a0, a1 in ((-0.72, 2.42), (2.42, -0.72), (0.85, 3.99), (3.99, 0.85)):
        for k in range(2):
            r0 = 10 + rnd.uniform(-1.5, 1.5)
            r1 = 10 + rnd.uniform(-1.5, 1.5)
            j = rnd.uniform(-1.4, 1.4)
            pygame.draw.line(surf, SCARLET_LIT,
                             (px + math.cos(a0) * r0 + j,
                              py + math.sin(a0) * r0 + j * 0.6),
                             (px + math.cos(a1) * r1 - j,
                              py + math.sin(a1) * r1), 2 + (k == 0))


# ── ledger entries ───────────────────────────────────────────────────────────

def _hand_ellipse(surf, cx, cy, rx, ry, seed, color, width=3):
    """A pen circle drawn round a number: slightly out of round, and it
    overshoots its own start rather than closing cleanly."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, math.tau) for _ in range(3)]
    n = 190
    pts = []
    for i in range(n + 1):
        a = -2.35 + 1.11 * math.tau * i / n
        k = (1 + 0.020 * math.sin(3 * a + ph[0])
             + 0.013 * math.sin(5 * a + ph[1])) * (1 + 0.030 * i / n)
        pts.append((cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k))
    lay = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.lines(lay, (0, 0, 12, 130), False,
                      [(x + 1, y + 2) for x, y in pts], width)
    pygame.draw.lines(lay, (*color, 236), False, pts, width)
    surf.blit(lay, (0, 0))


def _hero(surf, run, cy):
    """The pillar count is the only thing a player looks for, so it is written
    at four times the size of anything else and circled. The caption sits
    under the ring rather than beside it — beside it, a 3-digit count would
    push the group off the page."""
    txt = str(run["pillars"])
    f = _font(92)
    num = f.render(txt, True, GOLD)
    nr = num.get_rect(center=(int((CONTENT_X0 + CONTENT_X1) / 2), int(cy)))
    _hand_ellipse(surf, nr.centerx, cy, 73, 54, run["seed"], GOLD)
    sh = f.render(txt, True, (0, 0, 12))
    surf.blit(_fade(sh, 150), (nr.x + 3, nr.y + 4))
    surf.blit(num, nr.topleft)
    _caps(surf, "PILLARS CLEARED", nr.centerx, cy + 68, 11, GOLD, tracking=4,
          anchor="center")


def _entry_row(surf, y, label, value):
    lx = _caps(surf, label, CONTENT_X0, y - 9, 10, GOLD_MUTED, tracking=2,
               alpha=225)
    vw = _caps_w(value, 13, 1)
    lay = pygame.Surface((W, H), pygame.SRCALPHA)
    x = CONTENT_X0 + lx + 8
    while x < CONTENT_X1 - vw - 8:
        lay.fill((*INK, 120), (int(x), y - 4, 2, 2))
        x += 6
    surf.blit(lay, (0, 0))
    _caps(surf, value, CONTENT_X1, y - 9, 13, INK, tracking=1, anchor="right")


def render_screen(run):
    surf = pygame.Surface((W, H))
    surf.fill(BG)
    _page(surf, run["seed"])
    _binding(surf)
    _ruled_lines(surf)
    _margin_rule(surf)
    _header(surf, run)
    _margin_notes(surf, run)

    death_frac = min(1.0, (run["day"] - 1) + run["phase"])
    rows = 1 if run["pillars"] < 60 else (2 if run["pillars"] < 120 else 3)
    pts = build_route(rows, run["seed"])
    tab = _arc_table(pts)
    _draw_route(surf, pts, death_frac=death_frac)
    _place_doodles(surf, run, pts, tab)
    _death_mark(surf, pts, tab, death_frac=death_frac)

    div = pygame.Surface((CONTENT_X1 - MARGIN_X + 10, 1), pygame.SRCALPHA)
    div.fill((*GOLD_MUTED, 95))
    surf.blit(div, (MARGIN_X - 6, ENTRY_DIV_Y))
    _caps(surf, "FLIGHT ENTRY", MARGIN_X - 6, ENTRY_DIV_Y - 10, 8, GOLD_MUTED,
          tracking=3, alpha=200)

    _hero(surf, run, RULE_Y0 + 2.6 * RULE_STEP)
    _entry_row(surf, RULE_Y0 + 6 * RULE_STEP, "DAY", str(run["day"]))
    _entry_row(surf, RULE_Y0 + 7 * RULE_STEP, "TIME", run["time"])
    _entry_row(surf, RULE_Y0 + 8 * RULE_STEP, "CAUSE OF DEATH", run["cause"])
    return surf


# ── review sheet ─────────────────────────────────────────────────────────────

SHEET_W, SHEET_H = 736, 700


def build_sheet(screens):
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill(BG)
    _caps(sheet, "FLIGHT LOGBOOK  ·  ROUND 2", 12, 20, 16, GOLD, tracking=3)
    caps = ["RUN A  ·  PILLAR 25  ·  DAY 1  ·  GEYSER",
            "RUN B  ·  PILLAR 180  ·  DAY 2  ·  SNOW"]
    for i, (scr, cap) in enumerate(zip(screens, caps)):
        x = 4 + i * (W + 8)
        _caps(sheet, cap, x, 42, 9, (168, 160, 142), tracking=1)
        sheet.blit(scr, (x, 52))
    return sheet


def main():
    screens = [render_screen(r) for r in RUNS]
    sheet = build_sheet(screens)
    out = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), os.pardir, "docs",
        "flight_log_screen", "flight_logbook"))
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "round_3.png")
    pygame.image.save(sheet, path)
    print("saved", path, sheet.get_size())
    for name, pos in (("sheet bg", (2, 690)), ("page A", (200, 200)),
                      ("page B", (560, 200)), ("gutter gap", (368, 400))):
        print("  %-11s %s -> %s" % (name, pos, sheet.get_at(pos)[:3]))


if __name__ == "__main__":
    main()
