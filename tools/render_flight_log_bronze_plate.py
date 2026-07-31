"""
Flight Log screen concept — `bronze_plate`.

Renders a review sheet, not game code: the whole screen is drawn at 2x and
downscaled, because the concept leans on sub-pixel cues (a 1.5 px oxidised
bed hairline, a 1 px gold engraving bevel) that integer-only Pygame drawing
would otherwise destroy.

Material logic worth stating up front, since the pixels alone don't explain it:
champlevé — the day is a routed trough in cast bronze. Flown time is fired
enamel, stoned back so it sits slightly *below* the plate. Unflown time is
raw opal frit, heaped so it sits *above*. That height inversion is what makes
the white read as "not yet fired", i.e. not yet lived.
"""
import os
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame

pygame.display.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
OUT_DIR = os.path.join(ROOT, "docs", "flight_log_screen", "bronze_plate")
os.makedirs(OUT_DIR, exist_ok=True)

SW, SH = 360, 640
SS = 2  # supersample factor

GOLD = (240, 192, 64)
SCARLET = (172, 40, 32)
AMBER_MAX = (204, 104, 56)
WALL = (8, 8, 20)
BED = (18, 16, 14)

PHASE_BOUNDARIES = [
    (0.000, "DAY"),
    (0.231, "GOLDEN HOUR"),
    (0.363, "SUNSET"),
    (0.513, "DUSK"),
    (0.644, "NIGHT"),
    (0.794, "PREDAWN"),
    (0.906, "SUNRISE"),
]
EVENT_MARKERS = [
    (0.15, "GEYSER"),
    (0.41, "CLOWN"),
    (0.44, "STORM"),
    (0.85, "SNOW"),
]


# ── colour helpers ───────────────────────────────────────────────────────────

def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)


def rgb(c):
    return (max(0, min(255, int(round(c[0])))),
            max(0, min(255, int(round(c[1])))),
            max(0, min(255, int(round(c[2])))))


def shade(c, f):
    return rgb((c[0] * f, c[1] * f, c[2] * f))


def tint(c, target, t):
    return rgb(lerp(c, target, t))


# Sky keyframes lifted from game/biome.py — only the three sky stops matter here.
_SKY_KEYS = [
    (0.00, (40, 110, 200), (90, 170, 230), (170, 220, 245)),
    (0.18, (80, 120, 200), (220, 175, 140), (255, 210, 160)),
    (0.32, (90, 50, 130), (230, 95, 120), (255, 160, 90)),
    (0.48, (25, 20, 70), (70, 45, 130), (170, 95, 140)),
    (0.62, (5, 8, 30), (15, 25, 70), (35, 55, 115)),
    (0.78, (30, 30, 80), (70, 60, 140), (200, 130, 180)),
    (0.90, (50, 100, 180), (255, 150, 150), (255, 220, 170)),
    (1.00, (40, 110, 200), (90, 170, 230), (170, 220, 245)),
]


def sky_stops(phase, snap=0.0):
    """`snap` biases t away from 0.5. Straight RGB interpolation between two
    near-complementary skies (cyan day → amber golden hour) passes through a
    dead grey; enamel is a saturated material and cannot afford that, so the
    crossover is compressed into a narrow band instead of spread over the whole
    phase. Hue interpolation can't fix it — every arc from cyan to amber runs
    through a colour the sky never is."""
    phase = phase % 1.0
    for i in range(len(_SKY_KEYS) - 1):
        t0, a_top, a_mid, a_bot = _SKY_KEYS[i]
        t1, b_top, b_mid, b_bot = _SKY_KEYS[i + 1]
        if t0 <= phase <= t1:
            span = t1 - t0
            t = (phase - t0) / span if span > 0 else 0.0
            if snap > 0.0:
                d = 2.0 * t - 1.0
                t = 0.5 + 0.5 * (1.0 if d >= 0 else -1.0) * abs(d) ** snap
            t = t * t * (3 - 2 * t)  # smoothstep, matching biome.py
            return lerp(a_top, b_top, t), lerp(a_mid, b_mid, t), lerp(a_bot, b_bot, t)
    return _SKY_KEYS[0][1], _SKY_KEYS[0][2], _SKY_KEYS[0][3]


def vibrance(c, amount=0.45):
    """Low-chroma stops get the most lift, so hazy phases still read as glass."""
    chroma = max(c) - min(c)
    lum = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    k = 1.0 + amount * max(0.0, 1.0 - chroma / 120.0)
    return (lum + (c[0] - lum) * k, lum + (c[1] - lum) * k, lum + (c[2] - lum) * k)


def amber_clamp(c):
    """Scarlet is reserved for the death drop, so any sky stop that drifts into
    red territory is pulled toward amber before it can be mistaken for one."""
    redness = c[0] - max(c[1], c[2])
    if redness <= 55:
        return rgb(c)
    t = min(1.0, (redness - 55) / 55.0)
    out = lerp(c, AMBER_MAX, t)
    if out[0] > 218:
        out = (218, out[1], out[2])
    return rgb(out)


def enamel_raw(phase):
    _, mid, bot = sky_stops(phase, snap=0.5)
    return rgb(vibrance(lerp(mid, bot, 0.35)))


def enamel_color(phase):
    return amber_clamp(enamel_raw(phase))


# ── supersampled draw wrappers (arguments are in 360x640 design units) ───────

def dcircle(surf, col, x, y, r):
    pygame.draw.circle(surf, col, (int(round(x * SS)), int(round(y * SS))),
                       max(1, int(round(r * SS))))


def dline(surf, col, x1, y1, x2, y2, w=1.0):
    pygame.draw.line(surf, col, (int(round(x1 * SS)), int(round(y1 * SS))),
                     (int(round(x2 * SS)), int(round(y2 * SS))),
                     max(1, int(round(w * SS))))


def drect(surf, col, x, y, w, h, width=0):
    pygame.draw.rect(surf, col, pygame.Rect(int(round(x * SS)), int(round(y * SS)),
                                            max(1, int(round(w * SS))),
                                            max(1, int(round(h * SS)))),
                     0 if width == 0 else max(1, int(round(width * SS))))


def dpoly(surf, col, pts, width=0):
    pygame.draw.polygon(surf, col, [(int(round(p[0] * SS)), int(round(p[1] * SS)))
                                    for p in pts],
                        0 if width == 0 else max(1, int(round(width * SS))))


def dround(surf, col, x, y, w, h, r, width=0):
    pygame.draw.rect(surf, col, pygame.Rect(int(round(x * SS)), int(round(y * SS)),
                                            max(1, int(round(w * SS))),
                                            max(1, int(round(h * SS)))),
                     0 if width == 0 else max(1, int(round(width * SS))),
                     border_radius=max(1, int(round(r * SS))))


_FONTS = {}


def font(size):
    key = int(round(size * SS))
    if key not in _FONTS:
        _FONTS[key] = pygame.font.Font(FONT_PATH, key)
    return _FONTS[key]


def engrave(surf, text, size, x, y, align="left", ink=(44, 40, 26),
            bevel=GOLD, depth=1.0, spacing=0.0):
    """Deep-cut lettering: patina-dark stroke with a gold sliver on the lower
    wall, which is the only face a top light can reach inside a cut letter."""
    f = font(size)
    if spacing:
        imgs_i, imgs_b, widths = [], [], []
        for ch in text:
            imgs_i.append(f.render(ch, True, ink))
            imgs_b.append(f.render(ch, True, bevel))
            widths.append(f.size(ch)[0] + spacing * SS)
        total = sum(widths)
    else:
        img_i = f.render(text, True, ink)
        img_b = f.render(text, True, bevel)
        total = img_i.get_width()

    px = x * SS
    if align == "center":
        px -= total / 2.0
    elif align == "right":
        px -= total
    py = y * SS
    dz = depth * SS

    if spacing:
        cx = px
        for i in range(len(imgs_i)):
            surf.blit(imgs_b[i], (int(round(cx)), int(round(py + dz))))
            cx += widths[i]
        cx = px
        for i in range(len(imgs_i)):
            surf.blit(imgs_i[i], (int(round(cx)), int(round(py))))
            cx += widths[i]
    else:
        surf.blit(img_b, (int(round(px)), int(round(py + dz))))
        surf.blit(img_i, (int(round(px)), int(round(py))))
    return total / SS


def text_w(text, size, spacing=0.0):
    f = font(size)
    if spacing:
        return sum(f.size(ch)[0] + spacing * SS for ch in text) / SS
    return f.size(text)[0] / SS


def blur(surf, factor=6):
    w, h = surf.get_size()
    small = pygame.transform.smoothscale(surf, (max(1, w // factor), max(1, h // factor)))
    return pygame.transform.smoothscale(small, (w, h))


def rounded_mask(w_d, h_d, radius):
    m = pygame.Surface((int(w_d * SS), int(h_d * SS)), pygame.SRCALPHA)
    pygame.draw.rect(m, (255, 255, 255, 255), m.get_rect(),
                     border_radius=int(round(radius * SS)))
    return m


# ── plate geometry (coordinates are local to the bronze plate) ───────────────

PLATE_W, PLATE_H = 304, 520
ROW_Y = [106, 166, 226, 286, 346, 406]
X_L, X_R = 50.0, 254.0
TURN_R = 30.0
HALF_W = 10.0
STRAIGHT = X_R - X_L
ARC_LEN = math.pi * TURN_R
TOTAL_LEN = 6 * STRAIGHT + 5 * ARC_LEN


def build_path(step=0.5):
    """Boustrophedon centreline sampled densely enough that stamped circles
    fuse into a clean stroke at 2x."""
    pts = []
    s = 0.0
    for row in range(6):
        y = ROW_Y[row]
        left_to_right = (row % 2 == 0)
        n = int(STRAIGHT / step)
        for i in range(n):
            d = i * step
            x = X_L + d if left_to_right else X_R - d
            pts.append((x, y, s + d))
        s += STRAIGHT
        if row == 5:
            break
        cy = y + TURN_R
        cx = X_R if left_to_right else X_L
        n = int(ARC_LEN / step)
        for i in range(n):
            d = i * step
            t = d / ARC_LEN
            ang = math.radians(-90 + 180 * t) if left_to_right else math.radians(-90 - 180 * t)
            pts.append((cx + TURN_R * math.cos(ang), cy + TURN_R * math.sin(ang), s + d))
        s += ARC_LEN
    return pts


PATH = build_path()


def point_at(s):
    s = max(0.0, min(TOTAL_LEN - 0.01, s))
    idx = int(s / TOTAL_LEN * (len(PATH) - 1))
    idx = max(0, min(len(PATH) - 2, idx))
    # index is approximate because arc and straight sampling densities differ
    while idx < len(PATH) - 2 and PATH[idx][2] < s:
        idx += 1
    while idx > 0 and PATH[idx][2] > s:
        idx -= 1
    return PATH[idx][0], PATH[idx][1]


def tangent_at(s):
    x0, y0 = point_at(max(0.0, s - 1.0))
    x1, y1 = point_at(min(TOTAL_LEN - 0.1, s + 1.0))
    dx, dy = x1 - x0, y1 - y0
    m = math.hypot(dx, dy) or 1.0
    return dx / m, dy / m


def normal_at(s):
    tx, ty = tangent_at(s)
    return -ty, tx


# ── bronze substrate ─────────────────────────────────────────────────────────

def make_bronze(w_d, h_d, seed=7):
    """Cast bronze: warm vertical gradient, anisotropic brushed grain, and the
    pebbled sand-cast tooth that keeps a large flat face from reading as vinyl."""
    rnd = random.Random(seed)
    w, h = int(w_d * SS), int(h_d * SS)
    surf = pygame.Surface((w, h))
    top, bot = (180, 140, 70), (140, 100, 50)
    for i in range(h):
        pygame.draw.line(surf, rgb(lerp(top, bot, i / max(1, h - 1))), (0, i), (w, i))

    # sand-cast tooth first, so the brushed grain rides over it
    for _ in range(int(w * h * 0.055)):
        x = rnd.randrange(w)
        y = rnd.randrange(h)
        d = rnd.randint(-6, 6)
        base = surf.get_at((x, y))
        pygame.draw.circle(surf, rgb((base[0] + d, base[1] + d * 0.9, base[2] + d * 0.7)),
                           (x, y), rnd.choice((1, 1, 2)))

    for _ in range(int(h * 9)):
        y = rnd.randrange(h)
        x = rnd.randrange(w)
        ln = rnd.randint(int(14 * SS), int(90 * SS))
        d = rnd.randint(-8, 8)
        base = surf.get_at((min(w - 1, x), y))
        pygame.draw.line(surf, rgb((base[0] + d, base[1] + d, base[2] + d * 0.8)),
                         (x, y), (min(w - 1, x + ln), y), SS)

    # broad top-left sheen: a cast face is never evenly lit
    sheen = pygame.Surface((w, h))
    for i in range(h):
        v = max(0.0, 1.0 - i / (h * 0.62))
        c = int(26 * v * v)
        pygame.draw.line(sheen, (c, int(c * 0.85), int(c * 0.5)), (0, i), (w, i))
    surf.blit(sheen, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # patina always settles at the rim first
    vig = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(int(16 * SS)):
        a = int(70 * (1 - i / (16 * SS)) ** 2)
        pygame.draw.rect(vig, (24, 30, 18, a), pygame.Rect(i, i, w - 2 * i, h - 2 * i), SS)
    surf.blit(vig, (0, 0))
    return surf


def apply_patina_step(surf, blotch_seed=3):
    """One step of ageing: overall darkening plus green-black bloom, used to
    push a previous day behind the current one."""
    w, h = surf.get_size()
    mul = pygame.Surface((w, h))
    mul.fill((206, 198, 180))
    surf.blit(mul, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    rnd = random.Random(blotch_seed)
    blotch = pygame.Surface((w, h), pygame.SRCALPHA)
    for _ in range(90):
        x, y = rnd.randrange(w), rnd.randrange(h)
        r = rnd.randint(int(4 * SS), int(20 * SS))
        pygame.draw.circle(blotch, (46, 62, 44, rnd.randint(10, 30)), (x, y), r)
    surf.blit(blur(blotch, 3), (0, 0))


# ── channel ──────────────────────────────────────────────────────────────────

# A stamped stroke ends in a cap of its own radius, so the enamel and frit runs
# are cut back by that much to leave a real gap of bare bed at the seam.
DROP_LEN = 15.0
ENAMEL_CUT = 22.0
FRIT_CUT = 12.5


def draw_channel(plate, s_death, frit_val=242, dim=1.0, seed=11):
    rnd = random.Random(seed)

    # routed walls: light from the top, so the upper shoulder is in shadow
    for (x, y, s) in PATH:
        dcircle(plate, shade((92, 66, 36), dim), x - 1.0, y - 1.4, 11.4)
    for (x, y, s) in PATH:
        dcircle(plate, shade((216, 176, 104), dim), x + 1.0, y + 1.4, 11.4)
    for (x, y, s) in PATH:
        dcircle(plate, BED, x, y, 10.0)

    # oxidised bed mottle, only ever glimpsed at the wall hairline
    for _ in range(1400):
        s = rnd.uniform(0, TOTAL_LEN)
        x, y = point_at(s)
        nx, ny = normal_at(s)
        off = rnd.uniform(8.3, 10.0) * rnd.choice((-1, 1))
        g = rnd.choice(((26, 40, 30), (34, 50, 36), (12, 20, 16), (40, 56, 40)))
        dcircle(plate, g, x + nx * off, y + ny * off, rnd.uniform(0.5, 1.1))

    enamel_pts = [p for p in PATH if p[2] < s_death - ENAMEL_CUT]
    frit_pts = [p for p in PATH if p[2] > s_death + FRIT_CUT]

    # --- fired enamel: recessed, wet, domed
    for (x, y, s) in enamel_pts:
        c = enamel_color(s / TOTAL_LEN)
        dcircle(plate, shade(c, 0.60 * dim), x, y, 8.5)
    for (x, y, s) in enamel_pts:
        c = enamel_color(s / TOTAL_LEN)
        dcircle(plate, shade(c, 0.92 * dim), x, y + 0.6, 7.0)
    for (x, y, s) in enamel_pts:
        c = enamel_color(s / TOTAL_LEN)
        dcircle(plate, shade(tint(c, (255, 255, 255), 0.14), dim), x, y - 1.4, 5.0)
    for (x, y, s) in enamel_pts:
        c = enamel_color(s / TOTAL_LEN)
        dcircle(plate, shade(tint(c, (255, 255, 255), 0.50), dim), x, y - 4.2, 1.9)
    for (x, y, s) in enamel_pts:
        c = enamel_color(s / TOTAL_LEN)
        dcircle(plate, shade(tint(c, (255, 255, 255), 0.88), dim), x, y - 4.6, 0.9)

    # --- raw frit: proud, matte, hueless
    fv = frit_val * dim
    for (x, y, s) in frit_pts:
        dcircle(plate, rgb((fv - 16, fv - 16, fv - 18)), x, y, 9.0)
    for (x, y, s) in frit_pts:
        dcircle(plate, rgb((fv, fv - 2, fv - 4)), x, y - 0.4, 7.6)
    for (x, y, s) in frit_pts:
        dcircle(plate, rgb((fv + 7, fv + 6, fv + 4)), x, y - 1.6, 4.6)
    for _ in range(5200):
        p = frit_pts[rnd.randrange(len(frit_pts))] if frit_pts else None
        if p is None:
            break
        s = p[2]
        x, y = p[0], p[1]
        nx, ny = normal_at(s)
        off = rnd.uniform(-8.2, 8.2)
        d = rnd.randint(-11, 7)
        dcircle(plate, rgb((fv + d, fv + d - 2, fv + d - 4)),
                x + nx * off, y + ny * off, rnd.uniform(0.4, 0.95))

    # Unfired frit stands above the plate, so it bounces light onto the bronze.
    # The halo is punched out over the channel itself — added there it would
    # clip the frit to pure white and destroy the matte read the concept needs.
    if frit_pts:
        w, h = plate.get_size()
        bloom = pygame.Surface((w, h))
        for (x, y, s) in frit_pts[::4]:
            dcircle(bloom, (255, 250, 242), x, y, 14.0)
        bloom = blur(bloom, 7)
        for (x, y, s) in PATH:
            dcircle(bloom, (0, 0, 0), x, y, 10.6)
        bloom = blur(bloom, 2)
        bloom.fill((34 if dim >= 1.0 else 22,) * 3, special_flags=pygame.BLEND_RGB_MULT)
        plate.blit(bloom, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def draw_cell_dividers(plate, s_death, dim=1.0):
    """Champlevé cells need walls: each phase change is bronze left un-routed,
    which also stops the enamel gradient from reading as one undivided smear."""
    for ph, name in PHASE_BOUNDARIES[1:]:
        s = ph * TOTAL_LEN
        x, y = point_at(s)
        nx, ny = normal_at(s)
        for w, c, off in ((3.4, shade((150, 114, 54), dim), 0.0),
                          (1.2, shade((226, 188, 116), dim), -1.3),
                          (1.0, shade((72, 50, 24), dim), 1.5)):
            dline(plate, c,
                  x + nx * -10.2 + (-ny) * off, y + ny * -10.2 + nx * off,
                  x + nx * 10.2 + (-ny) * off, y + ny * 10.2 + nx * off, w)


def draw_ferrule(plate, label, dim=1.0):
    """Machined gold collar capping the channel head — a turned part, not cast,
    so it gets concentric tool rings the plate never has."""
    x0, y0 = point_at(0.0)
    for i in range(22):
        d = i * 0.5
        x, y = point_at(d)
        dcircle(plate, shade((150, 112, 34), dim), x, y, 11.2)
    for i in range(22):
        d = i * 0.5
        x, y = point_at(d)
        dcircle(plate, shade(GOLD, dim), x, y, 10.0)
    for i in range(22):
        d = i * 0.5
        x, y = point_at(d)
        dcircle(plate, shade((255, 226, 140), dim), x, y - 2.6, 5.4)
        dcircle(plate, shade((146, 104, 30), dim), x, y + 6.4, 2.6)
    for ring in (2.0, 5.0, 8.0):
        x, y = point_at(ring)
        nx, ny = normal_at(ring)
        dline(plate, shade((176, 132, 44), dim), x + nx * -9.4, y + ny * -9.4,
              x + nx * 9.4, y + ny * 9.4, 0.8)
    # domed end cap
    dcircle(plate, shade((150, 112, 34), dim), x0, y0, 10.2)
    dcircle(plate, shade((248, 208, 108), dim), x0 + 0.4, y0 - 0.6, 8.6)
    dcircle(plate, shade((255, 232, 158), dim), x0 + 0.2, y0 - 2.4, 4.4)

    # engraved leader out to the rarity stamp
    lx = 38.0
    ly = 72.0
    for col, off in ((shade(GOLD, dim), 1.0), (shade((52, 44, 28), dim), 0.0)):
        dline(plate, col, lx, ly + off, 46.0, ly + off, 1.0)
        dline(plate, col, 46.0, ly + off, 50.0, 94.0 + off, 1.0)
    engrave(plate, label, 12, 36, 64, align="right",
            ink=shade((52, 44, 28), dim), bevel=shade(GOLD, dim), depth=1.0)


def draw_death(plate, s_death, dim=1.0):
    """The run ends twice over: enamel stops (a colour event) and the metal is
    chisel-nicked (a physical event). Two channels of the same news."""
    drop_len = 13.0
    s0 = s_death - drop_len
    n = int(drop_len / 0.5)
    for i in range(n):
        s = s0 + i * 0.5
        x, y = point_at(s)
        t = i / max(1, n - 1)
        r = 8.5 * (1.0 - 0.20 * t * t)
        dcircle(plate, shade((84, 16, 14), dim), x, y, r)
    for i in range(n):
        s = s0 + i * 0.5
        x, y = point_at(s)
        t = i / max(1, n - 1)
        r = 7.2 * (1.0 - 0.24 * t * t)
        dcircle(plate, shade(SCARLET, dim), x, y + 0.5, r)
    for i in range(n):
        s = s0 + i * 0.5
        x, y = point_at(s)
        t = i / max(1, n - 1)
        r = 4.6 * (1.0 - 0.34 * t * t)
        dcircle(plate, shade((208, 62, 44), dim), x, y - 1.4, r)
    hx, hy = point_at(s0 + drop_len * 0.34)
    dcircle(plate, shade((255, 170, 150), dim), hx, hy - 3.6, 1.9)
    dcircle(plate, shade((255, 240, 232), dim), hx - 0.3, hy - 4.0, 0.9)

    # chisel nick chased across the wall — struck by hand, so it overruns
    x, y = point_at(s_death + 1.4)
    nx, ny = normal_at(s_death + 1.4)
    tx, ty = tangent_at(s_death + 1.4)
    skew = 2.6
    ax, ay = x + nx * -14.5 - tx * skew, y + ny * -14.5 - ty * skew
    bx, by = x + nx * 14.5 + tx * skew, y + ny * 14.5 + ty * skew
    dline(plate, shade((30, 22, 12), dim), ax, ay, bx, by, 2.6)
    dline(plate, shade((250, 214, 138), dim), ax + tx * 1.5, ay + ty * 1.5,
          bx + tx * 1.5, by + ty * 1.5, 1.0)
    dline(plate, shade((66, 46, 22), dim), ax - tx * 1.6, ay - ty * 1.6,
          bx - tx * 1.6, by - ty * 1.6, 0.8)
    # burr where the chisel lifted
    dcircle(plate, shade((236, 198, 124), dim), bx + tx * 1.2, by + ty * 1.2, 1.3)


# ── event rivets ─────────────────────────────────────────────────────────────

def _punch(plate, pts, cx, cy, dim, closed=False, w=1.1):
    for col, off in ((shade((252, 214, 140), dim), 0.9), (shade((44, 30, 14), dim), 0.0)):
        seq = [(cx + p[0], cy + p[1] + off) for p in pts]
        for i in range(len(seq) - 1):
            dline(plate, col, seq[i][0], seq[i][1], seq[i + 1][0], seq[i + 1][1], w)
        if closed:
            dline(plate, col, seq[-1][0], seq[-1][1], seq[0][0], seq[0][1], w)


def draw_rivet(plate, s, kind, dim=1.0):
    x, y = point_at(s)
    dcircle(plate, shade((26, 18, 10), dim), x + 0.7, y + 1.0, 7.2)
    dcircle(plate, shade((118, 86, 38), dim), x, y, 6.7)
    dcircle(plate, shade((198, 158, 80), dim), x - 0.4, y - 0.6, 6.1)
    dcircle(plate, shade((230, 194, 118), dim), x - 0.9, y - 1.2, 4.3)
    dcircle(plate, shade((250, 224, 160), dim), x - 1.7, y - 2.1, 2.0)

    if kind == "GEYSER":
        _punch(plate, [(-2.8, 3.2), (2.8, 3.2)], x, y, dim)
        _punch(plate, [(0, 3.0), (0, -1.0)], x, y, dim, w=1.3)
        _punch(plate, [(0, -0.6), (-2.6, -3.2)], x, y, dim)
        _punch(plate, [(0, -0.6), (2.6, -3.2)], x, y, dim)
    elif kind == "CLOWN":
        _punch(plate, [(-3.0, -0.4), (-2.0, -2.6), (0, -3.4), (2.0, -2.6), (3.0, -0.4)],
               x, y, dim)
        _punch(plate, [(-2.8, 0.6), (-1.4, 3.0), (1.4, 3.0), (2.8, 0.6)], x, y, dim)
        _punch(plate, [(-1.5, -0.9), (-1.5, -0.2)], x, y, dim, w=1.3)
        _punch(plate, [(1.5, -0.9), (1.5, -0.2)], x, y, dim, w=1.3)
    elif kind == "STORM":
        _punch(plate, [(1.4, -3.6), (-1.9, 0.2), (0.3, 0.2), (-1.2, 3.6)], x, y, dim, w=1.3)
    elif kind == "SNOW":
        for k in range(3):
            a = math.radians(k * 60)
            dxp, dyp = math.cos(a) * 3.4, math.sin(a) * 3.4
            _punch(plate, [(-dxp, -dyp), (dxp, dyp)], x, y, dim)
        for k in range(3):
            a = math.radians(k * 60)
            dxp, dyp = math.cos(a) * 3.4, math.sin(a) * 3.4
            _punch(plate, [(dxp * 0.72 - dyp * 0.26, dyp * 0.72 + dxp * 0.26),
                           (dxp, dyp)], x, y, dim, w=0.8)


# ── phase labels + extent brackets ───────────────────────────────────────────

# Each phase is labelled once, under the row where most of it lies; the bracket
# under the channel states the extent so a name can't drift off its own segment.
LABEL_PLAN = [
    ("DAY", 0, X_L, X_R, 9),
    ("GOLDEN HOUR", 1, 50.0, 160.6, 9),
    ("SUNSET", 2, 68.9, X_R, 9),
    ("DUSK", 3, 57.0, X_R, 9),
    ("NIGHT", 4, X_L, 202.9, 9),
    ("PREDAWN", 5, 209.5, X_R, 8),
    ("SUNRISE", 5, X_L, 209.5, 9),
]


def draw_labels(plate, s_death, dim=1.0):
    flown_phase = s_death / TOTAL_LEN
    for name, row, x0, x1, size in LABEL_PLAN:
        y = ROW_Y[row]
        by = y + 15.0
        ph = None
        for p, n in PHASE_BOUNDARIES:
            if n == name:
                ph = p
        flown = ph is not None and ph < flown_phase
        ink = shade((48, 42, 26), dim)
        bev = shade(GOLD if flown else (206, 166, 74), dim)
        for col, off in ((bev, 0.9), (ink, 0.0)):
            dline(plate, col, x0, by + off, x1, by + off, 0.9)
            dline(plate, col, x0, by + off - 2.6, x0, by + off, 0.9)
            dline(plate, col, x1, by + off - 2.6, x1, by + off, 0.9)
        engrave(plate, name, size, (x0 + x1) / 2.0, y + 21.0, align="center",
                ink=ink, bevel=bev, depth=0.9, spacing=0.5)


# ── plate assembly ───────────────────────────────────────────────────────────

def render_plate(run, patina=False):
    plate = make_bronze(PLATE_W, PLATE_H, seed=run.get("seed", 7))
    dim = 1.0
    s_death = run["phase"] * TOTAL_LEN

    # header
    engrave(plate, "SKYBIT", 9, PLATE_W / 2, 10, align="center",
            ink=(52, 46, 30), bevel=GOLD, depth=0.9, spacing=3.2)
    engrave(plate, "FLIGHT LOG", 27, PLATE_W / 2, 22, align="center",
            ink=(38, 32, 20), bevel=GOLD, depth=2.0, spacing=1.4)
    for col, off in ((GOLD, 1.0), ((56, 46, 28), 0.0)):
        dline(plate, col, 24, 58 + off, PLATE_W - 24, 58 + off, 0.9)
    for cx in (20.0, PLATE_W - 20.0):
        dpoly(plate, (58, 46, 28), [(cx, 55), (cx + 3.4, 58.4), (cx, 61.8), (cx - 3.4, 58.4)])
        dpoly(plate, GOLD, [(cx, 56.4), (cx + 2.2, 58.6), (cx, 60.8), (cx - 2.2, 58.6)])

    engrave(plate, run["day_label"], 11, PLATE_W - 16, 64, align="right",
            ink=(48, 42, 26), bevel=GOLD, depth=1.0, spacing=1.2)

    draw_channel(plate, s_death, frit_val=run.get("frit", 242))
    draw_cell_dividers(plate, s_death)
    draw_ferrule(plate, run["rarity"])
    draw_death(plate, s_death)
    for ph, kind in EVENT_MARKERS:
        draw_rivet(plate, ph * TOTAL_LEN, kind)
    draw_labels(plate, s_death)

    # footer: a raised cast band carrying the run's three hard numbers
    fy, fh = 452, 56
    drect(plate, (168, 128, 62), 16, fy, PLATE_W - 32, fh)
    drect(plate, (222, 182, 108), 16, fy, PLATE_W - 32, 1.2)
    drect(plate, (86, 60, 28), 16, fy + fh - 1.2, PLATE_W - 32, 1.2)
    drect(plate, (222, 182, 108), 16, fy, 1.2, fh)
    drect(plate, (86, 60, 28), PLATE_W - 17.2, fy, 1.2, fh)
    grain = pygame.Surface((int((PLATE_W - 32) * SS), int(fh * SS)), pygame.SRCALPHA)
    rnd = random.Random(21)
    for _ in range(1400):
        gx, gy = rnd.randrange(grain.get_width()), rnd.randrange(grain.get_height())
        d = rnd.randint(0, 22)
        pygame.draw.line(grain, (255, 235, 190, d), (gx, gy),
                         (gx + rnd.randint(6, 40), gy), SS)
    plate.blit(grain, (int(16 * SS), int(fy * SS)))

    cells = [("PILLARS", str(run["pillars"])),
             ("TIME", run["time"]),
             ("DAY FLOWN", "%.1f%%" % (run["phase"] * 100.0))]
    inner = PLATE_W - 32
    for i, (lab, val) in enumerate(cells):
        cx = 16 + inner * (i + 0.5) / 3.0
        engrave(plate, lab, 8, cx, fy + 8, align="center",
                ink=(56, 46, 28), bevel=(228, 186, 108), depth=0.8, spacing=1.0)
        engrave(plate, val, 18, cx, fy + 21, align="center",
                ink=(36, 30, 18), bevel=GOLD, depth=1.4)
    for i in (1, 2):
        dx = 16 + inner * i / 3.0
        dline(plate, (86, 60, 28), dx, fy + 8, dx, fy + fh - 8, 0.9)
        dline(plate, (226, 188, 116), dx + 0.9, fy + 8, dx + 0.9, fy + fh - 8, 0.9)

    # cast rim bevel
    drect(plate, (226, 190, 120), 0, 0, PLATE_W, 1.6)
    drect(plate, (226, 190, 120), 0, 0, 1.6, PLATE_H)
    drect(plate, (74, 50, 22), 0, PLATE_H - 1.6, PLATE_W, 1.6)
    drect(plate, (74, 50, 22), PLATE_W - 1.6, 0, 1.6, PLATE_H)

    if patina:
        apply_patina_step(plate)

    plate = plate.convert_alpha()
    plate.blit(rounded_mask(PLATE_W, PLATE_H, 5), (0, 0),
               special_flags=pygame.BLEND_RGBA_MULT)
    return plate


# ── walnut board + hardware ──────────────────────────────────────────────────

def make_walnut(w_d, h_d, seed=5, patina=False):
    rnd = random.Random(seed)
    w, h = int(w_d * SS), int(h_d * SS)
    surf = pygame.Surface((w, h))
    top, bot = (96, 55, 25), (64, 36, 16)
    for i in range(h):
        pygame.draw.line(surf, rgb(lerp(top, bot, i / max(1, h - 1))), (0, i), (w, i))
    # vertical grain with slow wander, plus a couple of cathedral figures
    for _ in range(int(w_d * 3.2)):
        x = rnd.uniform(0, w)
        d = rnd.randint(-26, 16)
        amp = rnd.uniform(0.6, 3.0) * SS
        per = rnd.uniform(90, 320) * SS
        ph = rnd.uniform(0, 6.28)
        col = rgb((top[0] + d, top[1] + d * 0.7, top[2] + d * 0.5))
        prev = None
        for y in range(0, h, int(3 * SS)):
            xx = x + math.sin(y / per * 6.28 + ph) * amp
            if prev:
                pygame.draw.line(surf, col, prev, (xx, y), SS)
            prev = (xx, y)
    gloss = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(h):
        v = max(0.0, 1.0 - abs(i - h * 0.22) / (h * 0.42))
        pygame.draw.line(gloss, (255, 208, 150, int(30 * v)), (0, i), (w, i))
    surf.blit(gloss, (0, 0))
    # outer chamfer
    drect(surf, (128, 78, 38), 0, 0, w_d, 1.4)
    drect(surf, (128, 78, 38), 0, 0, 1.4, h_d)
    drect(surf, (38, 20, 8), 0, h_d - 1.4, w_d, 1.4)
    drect(surf, (38, 20, 8), w_d - 1.4, 0, 1.4, h_d)
    if patina:
        mul = pygame.Surface((w, h))
        mul.fill((202, 196, 190))
        surf.blit(mul, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    return surf


def draw_hex_screw(surf, cx, cy, r=7.0, dim=1.0):
    dcircle(surf, shade((24, 12, 5), dim), cx + 0.6, cy + 0.9, r + 1.0)
    dcircle(surf, shade((150, 112, 34), dim), cx, cy, r)
    dcircle(surf, shade((246, 206, 108), dim), cx - 0.5, cy - 0.7, r - 0.9)
    dcircle(surf, shade((255, 234, 168), dim), cx - 1.4, cy - 1.9, r * 0.42)
    hexs = [(cx + math.cos(math.radians(a)) * r * 0.52,
             cy + math.sin(math.radians(a)) * r * 0.52) for a in range(0, 360, 60)]
    dpoly(surf, shade((172, 132, 44), dim), [(p[0], p[1] + 0.8) for p in hexs])
    dpoly(surf, shade((40, 26, 10), dim), hexs)
    dcircle(surf, shade((70, 48, 18), dim), cx, cy, r * 0.20)


# ── whole screen ─────────────────────────────────────────────────────────────

BOARD = pygame.Rect(14, 14, 332, 560)   # design units
PLATE_AT = (28, 34)


def render_screen(run, addendum=None):
    W, H = SW * SS, SH * SS
    scr = pygame.Surface((W, H))
    scr.fill(WALL)

    # warm bounce off the plaque so the wall reads as a lit surface, not a void
    bounce = pygame.Surface((W, H))
    pygame.draw.ellipse(bounce, (86, 62, 34),
                        pygame.Rect(int(-40 * SS), int(40 * SS),
                                    int(440 * SS), int(600 * SS)))
    bounce = blur(bounce, 10)
    bounce.fill((58, 58, 58), special_flags=pygame.BLEND_RGB_MULT)
    scr.blit(bounce, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    patina = run.get("patina", False)

    def hang(rect, plate_off, plate_surf, radius, seed, board_patina):
        shadow = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 210),
                         pygame.Rect(int((rect.x + 2) * SS), int((rect.y + 5) * SS),
                                     int(rect.w * SS), int(rect.h * SS)),
                         border_radius=int(radius * SS))
        scr.blit(blur(shadow, 5), (0, 0))
        board = make_walnut(rect.w, rect.h, seed=seed, patina=board_patina)
        board = board.convert_alpha()
        board.blit(rounded_mask(rect.w, rect.h, radius), (0, 0),
                   special_flags=pygame.BLEND_RGBA_MULT)
        scr.blit(board, (int(rect.x * SS), int(rect.y * SS)))
        pshadow = pygame.Surface((W, H), pygame.SRCALPHA)
        pw, ph = plate_surf.get_size()
        pygame.draw.rect(pshadow, (0, 0, 0, 190),
                         pygame.Rect(int((plate_off[0] + 1) * SS), int((plate_off[1] + 2.5) * SS),
                                     pw, ph), border_radius=int(5 * SS))
        scr.blit(blur(pshadow, 3), (0, 0))
        scr.blit(plate_surf, (int(plate_off[0] * SS), int(plate_off[1] * SS)))

    plate = render_plate(run, patina=patina)
    hang(BOARD, PLATE_AT, plate, 7, 5, patina)

    draw_hex_screw(scr, BOARD.centerx, BOARD.y + 10, 7.0, 0.86 if patina else 1.0)
    draw_hex_screw(scr, BOARD.centerx, BOARD.bottom - 10, 7.0, 0.86 if patina else 1.0)

    if addendum:
        draw_addendum(scr, addendum)

    return pygame.transform.smoothscale(scr, (SW, SH))


def draw_addendum(scr, add):
    """A new day is a new casting; it hangs off the old one rather than
    replacing it, so the record accumulates instead of resetting."""
    px = BOARD.centerx
    py = BOARD.bottom
    # single gold pin
    drect(scr, (24, 14, 6), px - 2.2, py - 1, 4.4, 12)
    drect(scr, (150, 112, 34), px - 2.0, py - 1, 4.0, 12)
    drect(scr, (240, 200, 104), px - 1.6, py - 1, 1.6, 12)
    dcircle(scr, (150, 112, 34), px, py + 11.5, 3.4)
    dcircle(scr, (248, 210, 116), px - 0.4, py + 10.8, 2.6)
    dcircle(scr, (255, 236, 176), px - 1.0, py + 10.0, 1.1)

    sw_, sh_ = 204, 54
    sx, sy = px - sw_ / 2, py + 8

    shadow = pygame.Surface((SW * SS, SH * SS), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 200),
                     pygame.Rect(int((sx + 2) * SS), int((sy + 4) * SS),
                                 int(sw_ * SS), int(sh_ * SS)),
                     border_radius=int(6 * SS))
    scr.blit(blur(shadow, 5), (0, 0))
    board = make_walnut(sw_, sh_, seed=9).convert_alpha()
    board.blit(rounded_mask(sw_, sh_, 6), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    scr.blit(board, (int(sx * SS), int(sy * SS)))

    bw, bh = sw_ - 16, sh_ - 16
    bx, by = sx + 8, sy + 8
    strip = make_bronze(bw, bh, seed=31)

    engrave(strip, add["day_label"], 11, 8, 5, ink=(46, 40, 26), bevel=GOLD,
            spacing=1.4, depth=1.0)
    engrave(strip, "%d PILLARS  %s" % (add["pillars"], add["time"]), 8, 8, 22,
            ink=(56, 48, 30), bevel=(224, 182, 104), depth=0.8, spacing=0.4)

    # short single-row channel: an addendum states a fraction, not a whole day
    cx0, cx1, cy = 96.0, bw - 12.0, bh / 2.0
    clen = cx1 - cx0
    hw = 6.5
    for x in [cx0 + i * 0.5 for i in range(int(clen / 0.5) + 1)]:
        dcircle(strip, (92, 66, 36), x - 0.8, cy - 1.1, hw + 1.4)
    for x in [cx0 + i * 0.5 for i in range(int(clen / 0.5) + 1)]:
        dcircle(strip, (216, 176, 104), x + 0.8, cy + 1.1, hw + 1.4)
    for x in [cx0 + i * 0.5 for i in range(int(clen / 0.5) + 1)]:
        dcircle(strip, BED, x, cy, hw)
    s_d = cx0 + clen * add["phase"]
    for x in [cx0 + i * 0.5 for i in range(int(clen / 0.5) + 1)]:
        if x < s_d - 5:
            c = enamel_color((x - cx0) / clen)
            dcircle(strip, shade(c, 0.62), x, cy, hw - 1.4)
            dcircle(strip, c, x, cy + 0.4, hw - 2.6)
            dcircle(strip, tint(c, (255, 255, 255), 0.55), x, cy - 2.6, 1.2)
        elif x > s_d + 2:
            dcircle(strip, (226, 224, 221), x, cy, hw - 0.9)
            dcircle(strip, (242, 240, 238), x, cy - 0.4, hw - 2.2)
            dcircle(strip, (249, 248, 246), x, cy - 1.2, hw - 4.0)
    rnd = random.Random(77)
    for _ in range(900):
        x = rnd.uniform(s_d + 2, cx1)
        yy = cy + rnd.uniform(-5.2, 5.2)
        d = rnd.randint(-11, 6)
        dcircle(strip, rgb((242 + d, 240 + d, 238 + d)), x, yy, rnd.uniform(0.4, 0.9))
    # scarlet drop + nick, same grammar as the main plate
    for i in range(11):
        x = s_d - 5 + i * 0.5
        dcircle(strip, (84, 16, 14), x, cy, hw - 1.4)
        dcircle(strip, SCARLET, x, cy + 0.4, hw - 2.6)
        dcircle(strip, (208, 62, 44), x, cy - 1.0, hw - 4.2)
    dcircle(strip, (255, 180, 158), s_d - 3.4, cy - 2.4, 1.2)
    dline(strip, (30, 22, 12), s_d + 1.0 - 1.6, cy - 9.5, s_d + 1.0 + 1.6, cy + 9.5, 2.0)
    dline(strip, (250, 214, 138), s_d + 2.2 - 1.6, cy - 9.5, s_d + 2.2 + 1.6, cy + 9.5, 0.9)
    # ferrule cap
    for i in range(8):
        dcircle(strip, (150, 112, 34), cx0 + i * 0.5, cy, hw + 0.6)
        dcircle(strip, GOLD, cx0 + i * 0.5, cy, hw - 0.4)
        dcircle(strip, (255, 228, 146), cx0 + i * 0.5, cy - 1.8, 2.6)
    engrave(strip, add["rarity"], 8, cx0 - 3, cy - 15, align="right",
            ink=(52, 44, 28), bevel=GOLD, depth=0.8)

    drect(strip, (226, 190, 120), 0, 0, bw, 1.4)
    drect(strip, (74, 50, 22), 0, bh - 1.4, bw, 1.4)
    strip = strip.convert_alpha()
    strip.blit(rounded_mask(bw, bh, 4), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    scr.blit(strip, (int(bx * SS), int(by * SS)))


# ── review sheet ─────────────────────────────────────────────────────────────

RUN_A = dict(phase=0.184, pillars=25, time="0:47", day_label="DAY 1",
             rarity="3%", seed=7)
RUN_DEEP = dict(phase=0.720, pillars=118, time="3:36", day_label="DAY 1",
                rarity="0.4%", seed=13)
RUN_A_OLD = dict(RUN_A, patina=True, frit=232)
ADD_B = dict(phase=0.061, pillars=12, time="0:19", day_label="DAY 2", rarity="41%")


def sheet_font(size):
    return pygame.font.Font(FONT_PATH, size)


def label(surf, text, size, x, y, col=(232, 228, 220), align="left"):
    f = sheet_font(size)
    img = f.render(text, True, col)
    px = x
    if align == "center":
        px -= img.get_width() // 2
    elif align == "right":
        px -= img.get_width()
    surf.blit(img, (int(px), int(y)))
    return img.get_width()


def scarlet_audit_tile(w, h):
    t = pygame.Surface((w, h))
    t.fill((16, 16, 19))
    pad = 10
    bar_h = 30
    label(t, "RAW SKY", 11, pad, 6, (150, 150, 158))
    for i in range(w - pad * 2):
        ph = i / float(w - pad * 2 - 1)
        pygame.draw.line(t, enamel_raw(ph), (pad + i, 22), (pad + i, 22 + bar_h))
    label(t, "CLAMPED ENAMEL", 11, pad, 58, (150, 150, 158))
    worst = 1e9
    for i in range(w - pad * 2):
        ph = i / float(w - pad * 2 - 1)
        c = enamel_color(ph)
        d = math.dist(c, SCARLET)
        worst = min(worst, d)
        pygame.draw.line(t, c, (pad + i, 74), (pad + i, 74 + bar_h))
    chip = 26
    cy = 112
    for i, (c, name) in enumerate(((SCARLET, "DROP"), (AMBER_MAX, "AMBER CAP"))):
        cx = pad + i * 108
        pygame.draw.rect(t, c, pygame.Rect(cx, cy, chip, chip))
        pygame.draw.rect(t, (70, 70, 76), pygame.Rect(cx, cy, chip, chip), 1)
        label(t, name, 10, cx + chip + 6, cy + 3, (176, 176, 184))
        label(t, "%d,%d,%d" % c, 9, cx + chip + 6, cy + 15, (120, 120, 128))
    label(t, "min RGB dist to drop: %d" % int(worst), 10, w - pad, cy + 3,
          (240, 200, 120), align="right")
    label(t, "no enamel enters scarlet", 10, w - pad, cy + 15, (120, 120, 128),
          align="right")
    pygame.draw.rect(t, (52, 52, 58), t.get_rect(), 1)
    return t


def zoom_tile(src, rect, w, h, zoom=3):
    crop = src.subsurface(pygame.Rect(rect)).copy()
    z = pygame.transform.scale(crop, (rect[2] * zoom, rect[3] * zoom))
    t = pygame.Surface((w, h))
    t.fill((16, 16, 19))
    t.blit(z, ((w - z.get_width()) // 2, (h - z.get_height()) // 2))
    pygame.draw.rect(t, (52, 52, 58), t.get_rect(), 1)
    return t


def main():
    screen_a = render_screen(RUN_A)
    screen_deep = render_screen(RUN_DEEP)
    screen_day2 = render_screen(RUN_A_OLD, addendum=ADD_B)

    SHEET_W, SHEET_H = 1208, 984
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((22, 22, 26))
    pygame.draw.rect(sheet, (44, 44, 50), sheet.get_rect(), 2)

    label(sheet, "SKYBIT — FLIGHT LOG SCREEN", 15, 28, 22, (150, 150, 158))
    label(sheet, "CONCEPT: BRONZE PLATE", 30, 28, 42, (240, 192, 64))
    label(sheet, "ROUND 1", 15, SHEET_W - 28, 24, (150, 150, 158), align="right")
    label(sheet, "champlevé day-channel · fired enamel = flown · raw opal frit = unflown",
          13, SHEET_W - 28, 46, (200, 196, 188), align="right")
    label(sheet, "360x640 · procedural · LiberationSans-Bold only",
          12, SHEET_W - 28, 64, (120, 120, 128), align="right")
    pygame.draw.line(sheet, (60, 60, 68), (28, 88), (SHEET_W - 28, 88))

    xs = [28, 424, 820]
    caps = [
        ("RUN A — 1:1", "phase 0.184 · 25 pillars · 0:47 · DAY 1"),
        ("SCALE VIEW — deep run", "phase 0.720 · 118 pillars · 3:36 (palette + amber clamp)"),
        ("DAY 2 — addendum", "day 1 darkened one patina step · strip on a single gold pin"),
    ]
    for i, (scr, (c1, c2)) in enumerate(zip((screen_a, screen_deep, screen_day2), caps)):
        pygame.draw.rect(sheet, (56, 56, 62),
                         pygame.Rect(xs[i] - 1, 103, SW + 2, SH + 2), 1)
        sheet.blit(scr, (xs[i], 104))
        label(sheet, c1, 14, xs[i], 752, (238, 234, 226))
        label(sheet, c2, 11, xs[i], 770, (140, 140, 148))

    tw, th = 270, 152
    ty = 800
    txs = [28, 322, 616, 910]
    tiles = [
        (zoom_tile(screen_a, (223, 175, 90, 50), tw, th),
         "DEATH — 3x", "scarlet drop · chisel nick · bed seam"),
        (zoom_tile(screen_a, (36, 96, 90, 50), tw, th),
         "CHANNEL HEAD — 3x", "10 px machined ferrule · engraved \"3%\" leader"),
        (zoom_tile(screen_a, (170, 244, 90, 50), tw, th),
         "RIVETS + ENGRAVING — 3x", "punched glyphs on frit · extent bracket"),
        (scarlet_audit_tile(tw, th),
         "SCARLET AUDIT", "sunset stops pulled to amber (204,104,56)"),
    ]
    for i, (tile, c1, c2) in enumerate(tiles):
        sheet.blit(tile, (txs[i], ty))
        label(sheet, c1, 13, txs[i], ty + th + 8, (238, 234, 226))
        label(sheet, c2, 10, txs[i], ty + th + 25, (140, 140, 148))

    out = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())

    probes = [
        ("wall", screen_a.get_at((6, 620))),
        ("walnut border", screen_a.get_at((20, 300))),
        ("bronze face", screen_a.get_at((320, 300))),
        ("enamel row0", screen_a.get_at((160, 140))),
        ("frit row3", screen_a.get_at((160, 320))),
        ("drop", screen_a.get_at((262, 200))),
        ("footer value", screen_a.get_at((100, 508))),
    ]
    for name, c in probes:
        print("  %-16s %s" % (name, tuple(c)[:3]))
    print("  channel length %.1f px, death at %.1f px (%.1f%%)"
          % (TOTAL_LEN, RUN_A["phase"] * TOTAL_LEN, RUN_A["phase"] * 100))


if __name__ == "__main__":
    main()
