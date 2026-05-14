"""Generate v4 menu redesign mockups — 5 story-driven candidate themes.

Each mockup is a 360x640 PNG matching the game's window size. Every
theme is a *moment, place, or artifact from Pip's delivery journey*:
the dispatch desk, the courier's logbook, the route map, the cockpit,
and arrival at the starlit cottage. The functional layout (title,
three buttons, BEST + TOP 10 tiles) is preserved across all five so
the user can compare them head-to-head.

Palette and font are pulled from Skybit's canonical UI colors
(`game/hud.py:29-37`) and the bundled Liberation Sans family.
"""
import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

W, H = 360, 640
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "menu_redesign_v4")
os.makedirs(OUT, exist_ok=True)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "game", "assets")
FONT_BOLD = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")
FONT_REG  = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")

# ── Skybit canonical palette (mirrors game/hud.py:29-37) ────────────────────
GOLD_BRIGHT   = (240, 192,  64)
GOLD_MUTED    = (216, 184,  85)
RED_OUTLINE   = (168,  32,  16)
ORANGE_BORDER = (232, 104,  40)
BTN_TOP       = (200,  64,  24)
BTN_BOT       = (126,  28,   2)
PANEL_DARK    = ( 12,   8,  38)
NIGHT_DEEP    = (  6,   1,  21)
PARCEL_TAN    = (180, 130,  80)
PARCEL_HI     = (220, 175, 120)
RIBBON_RED    = (200,  50,  60)
COTTAGE_TEAL  = ( 38, 140, 120)
COTTAGE_RED   = (200,  53,  30)

WHITE      = (245, 245, 245)
NEAR_BLACK = ( 12,   8,  18)


# ── Helpers ─────────────────────────────────────────────────────────────────

def font(size, bold=True):
    return pygame.font.Font(FONT_BOLD if bold else FONT_REG, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def gradient_v(surf, top, bot, rect=None):
    r = rect or surf.get_rect()
    for y in range(r.height):
        t = y / max(1, r.height - 1)
        c = lerp(top, bot, t)
        pygame.draw.line(surf, c, (r.x, r.y + y), (r.x + r.width - 1, r.y + y))


def stroked_text(surf, txt, center, size, fill, outline, px=2,
                 shadow=(2, 3), shadow_alpha=170, bold=True):
    """The canonical Skybit gold-on-red title treatment."""
    f = font(size, bold)
    img = f.render(txt, True, fill)
    out = f.render(txt, True, outline)
    r = img.get_rect(center=center)
    for ox in (-px, 0, px):
        for oy in (-px, 0, px):
            if ox or oy:
                surf.blit(out, (r.x + ox, r.y + oy))
    if shadow:
        sh = f.render(txt, True, NEAR_BLACK)
        sh.set_alpha(shadow_alpha)
        surf.blit(sh, (r.x + shadow[0], r.y + shadow[1]))
    surf.blit(img, r.topleft)
    return r


def skybit_title(surf, cx, cy, size=72, px=3):
    """Reuse the v3 title treatment so every mockup keeps the brand mark."""
    return stroked_text(surf, "SKYBIT", (cx, cy), size,
                        fill=GOLD_BRIGHT, outline=RED_OUTLINE,
                        px=px, shadow=(3, 5))


def draw_parcel(surf, cx, cy, size=22):
    """Pip's kraft-tan parcel with red ribbon + bow. Mini version of
    game/intro.py:_build_parcel."""
    s = size
    rect = pygame.Rect(cx - s, cy - s + 3, s * 2, s * 2 - 4)
    pygame.draw.rect(surf, (26, 10, 12), rect.inflate(3, 3), border_radius=4)
    pygame.draw.rect(surf, PARCEL_TAN, rect, border_radius=4)
    pygame.draw.line(surf, PARCEL_HI, (rect.x + 2, rect.y + 2),
                     (rect.right - 3, rect.y + 2), 1)
    # ribbon cross
    rv_w = max(3, s // 4)
    pygame.draw.rect(surf, RIBBON_RED, (cx - rv_w // 2, rect.y, rv_w, rect.h))
    rh_w = max(3, s // 4)
    pygame.draw.rect(surf, RIBBON_RED,
                     (rect.x, cy - rh_w // 2 + 1, rect.w, rh_w))
    # bow
    bow_r = max(2, s // 4)
    pygame.draw.ellipse(surf, RIBBON_RED,
                        (cx - bow_r * 2, rect.y - bow_r * 2,
                         bow_r * 2, bow_r * 2))
    pygame.draw.ellipse(surf, RIBBON_RED,
                        (cx, rect.y - bow_r * 2,
                         bow_r * 2, bow_r * 2))


def draw_garrick(surf, cx, cy, scale=1.0):
    """Mr. Garrick — pale-pink pelican silhouette in a white shirt,
    holding a parcel. Simple but unambiguous."""
    s = scale
    # Body (egg-shape)
    body_w, body_h = int(56 * s), int(72 * s)
    body = pygame.Rect(cx - body_w // 2, cy - body_h // 2, body_w, body_h)
    pygame.draw.ellipse(surf, (240, 200, 195), body)
    pygame.draw.ellipse(surf, (200, 150, 145), body, 2)
    # White shirt / chest
    shirt = pygame.Rect(cx - int(20 * s), cy + int(2 * s),
                        int(40 * s), int(36 * s))
    pygame.draw.ellipse(surf, (250, 250, 245), shirt)
    pygame.draw.ellipse(surf, (180, 160, 155), shirt, 1)
    # Head
    head_r = int(20 * s)
    pygame.draw.circle(surf, (240, 200, 195), (cx, cy - body_h // 2 - head_r // 2 + 2), head_r)
    pygame.draw.circle(surf, (200, 150, 145), (cx, cy - body_h // 2 - head_r // 2 + 2), head_r, 2)
    # Beak — long pelican beak
    beak_y = cy - body_h // 2 - head_r // 2 + 4
    pygame.draw.polygon(surf, (255, 200, 90),
                        [(cx + int(6 * s), beak_y - int(3 * s)),
                         (cx + int(36 * s), beak_y + int(2 * s)),
                         (cx + int(6 * s), beak_y + int(5 * s))])
    pygame.draw.polygon(surf, (200, 140, 50),
                        [(cx + int(6 * s), beak_y - int(3 * s)),
                         (cx + int(36 * s), beak_y + int(2 * s)),
                         (cx + int(6 * s), beak_y + int(5 * s))], 1)
    # Eye
    pygame.draw.circle(surf, (20, 20, 30),
                       (cx + int(3 * s), cy - body_h // 2 - int(2 * s)),
                       max(2, int(2 * s)))


def draw_cottage(surf, cx, cy, scale=1.0, roof_col=COTTAGE_TEAL,
                 wall_col=(240, 220, 180), with_lantern=True):
    """A small cottage with shingled roof, chimney, door, window.
    cx/cy is the centre of the cottage body."""
    s = scale
    body_w, body_h = int(90 * s), int(60 * s)
    body = pygame.Rect(cx - body_w // 2, cy - body_h // 2, body_w, body_h)
    # Wall
    pygame.draw.rect(surf, wall_col, body)
    pygame.draw.rect(surf, NEAR_BLACK, body, 2)
    # Roof (triangular)
    roof_pts = [
        (body.x - int(8 * s), body.y),
        (body.right + int(8 * s), body.y),
        (cx, body.y - int(36 * s)),
    ]
    pygame.draw.polygon(surf, roof_col, roof_pts)
    pygame.draw.polygon(surf, NEAR_BLACK, roof_pts, 2)
    # Shingle stripes
    for i in range(1, 4):
        y = body.y - int(36 * s) + int(i * 9 * s)
        x_in = int(36 * s) * (i / 4)
        pygame.draw.line(surf, lerp(roof_col, NEAR_BLACK, 0.3),
                         (cx - x_in, y), (cx + x_in, y), 1)
    # Chimney
    chim_x = body.x + int(15 * s)
    chim_y = body.y - int(24 * s)
    pygame.draw.rect(surf, (140, 70, 50),
                     (chim_x, chim_y, int(10 * s), int(18 * s)))
    pygame.draw.rect(surf, NEAR_BLACK,
                     (chim_x, chim_y, int(10 * s), int(18 * s)), 1)
    # Door
    door_w, door_h = int(20 * s), int(34 * s)
    door = pygame.Rect(cx - door_w // 2, body.bottom - door_h, door_w, door_h)
    pygame.draw.rect(surf, (120, 70, 40), door)
    pygame.draw.rect(surf, NEAR_BLACK, door, 1)
    pygame.draw.circle(surf, GOLD_BRIGHT,
                       (door.right - int(4 * s), door.centery),
                       max(1, int(2 * s)))
    # Window
    win = pygame.Rect(body.x + int(12 * s), body.y + int(14 * s),
                      int(20 * s), int(18 * s))
    pygame.draw.rect(surf, (255, 230, 130), win)
    pygame.draw.rect(surf, NEAR_BLACK, win, 1)
    pygame.draw.line(surf, NEAR_BLACK, (win.centerx, win.y),
                     (win.centerx, win.bottom), 1)
    pygame.draw.line(surf, NEAR_BLACK, (win.x, win.centery),
                     (win.right, win.centery), 1)
    # Optional hanging paper lantern
    if with_lantern:
        lx, ly = body.right - int(6 * s), body.y + int(4 * s)
        pygame.draw.line(surf, NEAR_BLACK, (lx, body.y - int(4 * s)),
                         (lx, ly + int(2 * s)), 1)
        pygame.draw.ellipse(surf, (255, 180, 80),
                            (lx - int(6 * s), ly + int(2 * s),
                             int(12 * s), int(14 * s)))
        pygame.draw.ellipse(surf, (140, 70, 30),
                            (lx - int(6 * s), ly + int(2 * s),
                             int(12 * s), int(14 * s)), 1)


def save(name, surf):
    out = os.path.join(OUT, name)
    pygame.image.save(surf, out)
    print(f"  wrote {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Theme A — THE DISPATCH DESK (Mr. Garrick's Post Office)
# ─────────────────────────────────────────────────────────────────────────────
def theme_a_dispatch_desk():
    s = pygame.Surface((W, H))
    # Wood-panel wall (warm tan, vertical planks)
    gradient_v(s, (130, 88, 52), (94, 60, 36))
    for x in range(0, W, 40):
        pygame.draw.line(s, (70, 44, 24), (x, 0), (x, H), 1)
        pygame.draw.line(s, (150, 100, 64), (x + 1, 0), (x + 1, H), 1)

    # Window upper-left showing a slice of teal-roof cottage on cloud
    win_rect = pygame.Rect(20, 30, 100, 78)
    pygame.draw.rect(s, (170, 210, 230), win_rect)
    pygame.draw.rect(s, (40, 22, 10), win_rect, 3)
    # Sky inside window
    sky = pygame.Surface(win_rect.size)
    gradient_v(sky, (200, 230, 245), (140, 200, 230))
    s.blit(sky, win_rect.topleft)
    # Cloud puff
    pygame.draw.ellipse(s, (250, 250, 250),
                        (win_rect.x + 14, win_rect.bottom - 24, 70, 22))
    # Tiny teal cottage in window
    draw_cottage(s, win_rect.centerx, win_rect.centery + 6, scale=0.4,
                 roof_col=COTTAGE_TEAL, with_lantern=False)
    # Window cross
    pygame.draw.line(s, (40, 22, 10), (win_rect.centerx, win_rect.y),
                     (win_rect.centerx, win_rect.bottom), 2)
    pygame.draw.line(s, (40, 22, 10), (win_rect.x, win_rect.centery),
                     (win_rect.right, win_rect.centery), 2)

    # Cork pin-board on the right wall with route-map
    cork = pygame.Rect(180, 30, 160, 100)
    pygame.draw.rect(s, (190, 145, 90), cork)
    pygame.draw.rect(s, (90, 60, 30), cork, 3)
    # Cork speckles
    random.seed(7)
    for _ in range(40):
        pygame.draw.circle(s, (160, 115, 65),
                           (random.randint(cork.x + 3, cork.right - 3),
                            random.randint(cork.y + 3, cork.bottom - 3)), 1)
    # Pinned route map
    map_r = pygame.Rect(cork.x + 12, cork.y + 12, cork.w - 24, cork.h - 24)
    pygame.draw.rect(s, (245, 226, 180), map_r)
    pygame.draw.rect(s, (130, 90, 40), map_r, 1)
    # Dotted route on map
    pts = [(map_r.x + 8, map_r.bottom - 12),
           (map_r.x + 40, map_r.bottom - 30),
           (map_r.centerx, map_r.y + 22),
           (map_r.right - 12, map_r.y + 16)]
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        steps = 10
        for k in range(0, steps, 2):
            xa = x1 + (x2 - x1) * k / steps
            ya = y1 + (y2 - y1) * k / steps
            pygame.draw.circle(s, (200, 50, 50), (int(xa), int(ya)), 1)
    # Start (teal) & end (red) markers
    pygame.draw.circle(s, COTTAGE_TEAL, pts[0], 3)
    pygame.draw.circle(s, COTTAGE_RED, pts[-1], 3)
    # Red pushpins
    for px_, py_ in [(map_r.x + 4, map_r.y + 4),
                     (map_r.right - 4, map_r.y + 4)]:
        pygame.draw.circle(s, (200, 60, 60), (px_, py_), 3)
        pygame.draw.circle(s, WHITE, (px_ - 1, py_ - 1), 1)

    # Desk surface — large wooden plane across the bottom
    desk = pygame.Rect(0, 410, W, H - 410)
    gradient_v(s, (110, 72, 42), (70, 42, 22), desk)
    pygame.draw.line(s, (160, 110, 64), (0, 410), (W, 410), 2)
    # Wood grain on desk
    for y in range(420, H, 18):
        pygame.draw.line(s, (90, 56, 30), (10, y), (W - 10, y), 1)

    # Title sign hanging from chains over the desk
    sign_rect = pygame.Rect(W // 2 - 130, 130, 260, 70)
    # Chains
    for cxh in (sign_rect.x + 22, sign_rect.right - 22):
        for k in range(0, 6):
            yy = sign_rect.y - 26 + k * 5
            pygame.draw.circle(s, (170, 170, 175), (cxh, yy), 3, 1)
    pygame.draw.rect(s, (130, 86, 52), sign_rect, border_radius=8)
    pygame.draw.rect(s, (50, 30, 16), sign_rect, 3, border_radius=8)
    # Inner highlight
    pygame.draw.line(s, (200, 160, 100),
                     (sign_rect.x + 8, sign_rect.y + 6),
                     (sign_rect.right - 8, sign_rect.y + 6), 1)
    # SKYBIT stencilled
    skybit_title(s, W // 2, sign_rect.centery - 4, size=48, px=2)
    # Subtitle stamped beneath
    stamp_w, stamp_h = 200, 22
    stamp_rect = pygame.Rect(W // 2 - stamp_w // 2, 218, stamp_w, stamp_h)
    pygame.draw.rect(s, (200, 60, 50), stamp_rect, 2)
    sub = font(13, True).render("AIR  MAIL  ·  POCKET  SKY  FLYER",
                                True, (200, 60, 50))
    s.blit(sub, sub.get_rect(center=stamp_rect.center))

    # Stack of parcels on the left of the desk
    for i, (px_, py_, ds) in enumerate([(38, 510, 22), (32, 470, 20), (52, 490, 16)]):
        draw_parcel(s, px_, py_, ds)
    # Ink-stamp rack — three round stamps on the right
    for i, (sx, sy) in enumerate([(310, 470), (288, 490), (332, 488)]):
        pygame.draw.circle(s, (60, 36, 20), (sx, sy), 9)
        pygame.draw.circle(s, (220, 180, 120), (sx, sy - 3), 6)
        pygame.draw.rect(s, (220, 180, 120), (sx - 5, sy - 16, 10, 12))
    # Open ledger on the desk — supports the BEST stamp
    led = pygame.Rect(150, 478, 120, 80)
    pygame.draw.rect(s, (245, 232, 195), led)
    pygame.draw.rect(s, (130, 80, 40), led, 1)
    pygame.draw.line(s, (200, 175, 130), (led.centerx, led.y),
                     (led.centerx, led.bottom), 1)
    for k in range(4):
        yy = led.y + 12 + k * 12
        pygame.draw.line(s, (150, 110, 70), (led.x + 6, yy), (led.centerx - 4, yy), 1)
        pygame.draw.line(s, (150, 110, 70), (led.centerx + 4, yy), (led.right - 6, yy), 1)

    # ── BUTTONS — parcel-tag labels tied with twine ─────────────────────
    def tag_btn(center, text, big=False):
        w, h = (240, 50) if big else (240, 40)
        x = center[0] - w // 2
        y = center[1] - h // 2
        # Twine going up to the sign
        pygame.draw.line(s, (200, 175, 130),
                         (center[0] - 60, y), (center[0] - 60, y - 18), 1)
        pygame.draw.line(s, (200, 175, 130),
                         (center[0] + 60, y), (center[0] + 60, y - 18), 1)
        # Tag body — manila card with notched left side
        tag = pygame.Surface((w, h), pygame.SRCALPHA)
        notch = 14
        pts = [(notch, 0), (w, 0), (w, h), (notch, h), (0, h // 2)]
        pygame.draw.polygon(tag, (235, 215, 165), pts)
        pygame.draw.polygon(tag, (110, 70, 30), pts, 2)
        # Eyelet hole
        pygame.draw.circle(tag, (110, 70, 30), (notch + 6, h // 2), 4, 1)
        # Inner ink underline
        pygame.draw.line(tag, (180, 130, 70),
                         (notch + 18, h - 8), (w - 8, h - 8), 1)
        s.blit(tag, (x, y))
        ti = font(18 if big else 16, True).render(text, True, (60, 30, 10))
        s.blit(ti, ti.get_rect(center=(center[0] + 6, center[1])))
        return pygame.Rect(x, y, w, h)

    tag_btn((W // 2, 270), "DISPATCH NOW", big=True)
    tag_btn((W // 2, 325), "ROUTE GUIDE")
    tag_btn((W // 2, 372), "CARGO MANIFEST")

    # ── BEST + TOP 10 on the desk ───────────────────────────────────────
    # BEST — wax-seal stamp on the ledger
    bsx, bsy = led.centerx, led.centery + 10
    pygame.draw.circle(s, (160, 30, 30), (bsx, bsy), 18)
    pygame.draw.circle(s, (200, 50, 50), (bsx, bsy), 16)
    pygame.draw.circle(s, (110, 20, 20), (bsx, bsy), 18, 2)
    lbl = font(8, True).render("B E S T", True, (250, 220, 180))
    s.blit(lbl, lbl.get_rect(center=(bsx, bsy - 6)))
    vl = font(16, True).render("42", True, (250, 220, 180))
    s.blit(vl, vl.get_rect(center=(bsx, bsy + 5)))

    # TOP 10 — small brass trophy on the desk
    tx, ty = 312, 540
    # Plaque
    plaque = pygame.Rect(tx - 36, ty + 18, 72, 32)
    pygame.draw.rect(s, (90, 56, 30), plaque, border_radius=4)
    pygame.draw.rect(s, NEAR_BLACK, plaque, 1, border_radius=4)
    tl = font(9, True).render("TOP 10", True, GOLD_BRIGHT)
    s.blit(tl, tl.get_rect(center=(plaque.centerx, plaque.centery - 6)))
    tn = font(11, True).render("COURIERS", True, GOLD_BRIGHT)
    s.blit(tn, tn.get_rect(center=(plaque.centerx, plaque.centery + 6)))
    # Trophy on top of plaque
    cup_pts = [(tx - 8, ty), (tx + 8, ty), (tx + 6, ty + 12), (tx - 6, ty + 12)]
    pygame.draw.polygon(s, GOLD_BRIGHT, cup_pts)
    pygame.draw.polygon(s, (140, 90, 8), cup_pts, 1)
    pygame.draw.arc(s, GOLD_BRIGHT, (tx - 14, ty, 8, 12), math.pi / 2, math.pi * 1.5, 2)
    pygame.draw.arc(s, GOLD_BRIGHT, (tx + 6, ty, 8, 12), -math.pi / 2, math.pi / 2, 2)
    pygame.draw.rect(s, GOLD_BRIGHT, (tx - 2, ty + 12, 4, 5))
    pygame.draw.rect(s, GOLD_BRIGHT, (tx - 8, ty + 17, 16, 3))

    # Mr. Garrick peeking from behind the counter (right edge)
    draw_garrick(s, W - 50, 540, scale=0.65)

    save("theme_a_dispatch_desk.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# Theme B — PIP'S LOGBOOK (The Courier's Journal)
# ─────────────────────────────────────────────────────────────────────────────
def theme_b_logbook():
    s = pygame.Surface((W, H))
    # Dark wood desk background with candle glow
    gradient_v(s, (52, 32, 18), (24, 14, 8))

    # Candle-lit halo behind the book
    halo = pygame.Surface((W, H), pygame.SRCALPHA)
    for r in range(280, 0, -10):
        a = int(80 * (1 - r / 280))
        pygame.draw.circle(halo, (255, 200, 110, a), (W // 2, H // 2), r)
    s.blit(halo, (0, 0))

    # Open journal — leather cover edges around two cream pages
    book_rect = pygame.Rect(20, 70, W - 40, H - 130)
    # Leather backing
    pygame.draw.rect(s, (66, 38, 20), book_rect.inflate(12, 12), border_radius=10)
    pygame.draw.rect(s, (30, 16, 8), book_rect.inflate(12, 12), 3, border_radius=10)
    # Two pages (left/right) joined at spine
    spine_x = book_rect.centerx
    page_l = pygame.Rect(book_rect.x, book_rect.y,
                          spine_x - book_rect.x, book_rect.h)
    page_r = pygame.Rect(spine_x, book_rect.y,
                          book_rect.right - spine_x, book_rect.h)
    for p in (page_l, page_r):
        gradient_v(s, (250, 238, 210), (235, 218, 175), p)
    # Spine shadow
    sh = pygame.Surface((26, book_rect.h), pygame.SRCALPHA)
    for x in range(26):
        a = int(120 * (1 - abs(x - 13) / 13))
        pygame.draw.line(sh, (40, 20, 10, a), (x, 0), (x, book_rect.h))
    s.blit(sh, (spine_x - 13, book_rect.y))

    # Ruled lines on both pages (light brown)
    for y in range(book_rect.y + 60, book_rect.bottom - 20, 16):
        pygame.draw.line(s, (200, 175, 130), (page_l.x + 14, y),
                         (page_l.right - 8, y), 1)
        pygame.draw.line(s, (200, 175, 130), (page_r.x + 8, y),
                         (page_r.right - 14, y), 1)

    # Title — ink-styled "Skybit" using gold-on-red recipe (smaller for journal feel)
    stroked_text(s, "Skybit", (W // 2, 120),
                 size=58, fill=(60, 30, 16),
                 outline=(120, 70, 30), px=1,
                 shadow=(2, 3), shadow_alpha=80)
    # Subtitle stamp
    stamp = pygame.Rect(W // 2 - 92, 156, 184, 22)
    pygame.draw.rect(s, (180, 50, 50), stamp, 2)
    # Faint stamp imprint
    impr = pygame.Surface(stamp.size, pygame.SRCALPHA)
    impr.fill((180, 50, 50, 30))
    s.blit(impr, stamp.topleft)
    ssub = font(12, True).render("CERTIFIED  SKY  COURIER  ·  POCKET  SKY  FLYER",
                                 True, (180, 50, 50))
    s.blit(ssub, ssub.get_rect(center=stamp.center))

    # Marginal sketches: little pillar landmarks down the left margin
    def margin_sketch(cx, cy, kind):
        if kind == "flag":
            # Prayer-flag pole
            pygame.draw.line(s, (90, 50, 24), (cx, cy + 10), (cx, cy - 14), 1)
            for i, c in enumerate([(200, 60, 60), (60, 140, 200), (240, 200, 80)]):
                pygame.draw.polygon(s, c,
                                    [(cx, cy - 12 + i * 5),
                                     (cx + 8, cy - 10 + i * 5),
                                     (cx, cy - 8 + i * 5)])
        elif kind == "lantern":
            pygame.draw.line(s, (60, 30, 16), (cx, cy - 14), (cx, cy - 8), 1)
            pygame.draw.ellipse(s, (200, 60, 60), (cx - 7, cy - 8, 14, 16))
            pygame.draw.ellipse(s, (90, 30, 30), (cx - 7, cy - 8, 14, 16), 1)
            pygame.draw.line(s, (255, 220, 140), (cx - 4, cy - 4), (cx + 4, cy - 4), 1)
        elif kind == "monastery":
            pygame.draw.rect(s, (200, 170, 130), (cx - 9, cy - 4, 18, 14))
            pygame.draw.polygon(s, (140, 90, 50),
                                [(cx - 11, cy - 4), (cx + 11, cy - 4), (cx, cy - 14)])
        elif kind == "bucket":
            pygame.draw.polygon(s, (220, 60, 60),
                                [(cx - 10, cy - 8), (cx + 10, cy - 8),
                                 (cx + 7, cy + 8), (cx - 7, cy + 8)])
            for y in range(cy - 6, cy + 8, 3):
                pygame.draw.line(s, (250, 240, 230), (cx - 9, y), (cx + 9, y), 1)
        elif kind == "menhir":
            pygame.draw.rect(s, (130, 120, 100), (cx - 5, cy - 12, 10, 22))
            pygame.draw.line(s, (40, 20, 10), (cx - 4, cy - 10), (cx + 4, cy + 6), 1)

    for k, kind in enumerate(["flag", "lantern", "monastery", "bucket", "menhir"]):
        margin_sketch(page_l.x + 22, 230 + k * 38, kind)
        cap = font(9, False).render(
            {"flag": "lungta", "lantern": "lantern", "monastery": "monastery",
             "bucket": "kfc!", "menhir": "menhir"}[kind],
            True, (90, 60, 30))
        s.blit(cap, (page_l.x + 36, 226 + k * 38))

    # Pressed feather across the gutter
    feather_pts = [(spine_x - 14, 360), (spine_x + 18, 348), (spine_x + 30, 338),
                   (spine_x + 22, 360), (spine_x + 14, 380)]
    pygame.draw.polygon(s, (200, 60, 60), feather_pts)
    pygame.draw.polygon(s, (140, 25, 25), feather_pts, 1)
    pygame.draw.line(s, (90, 20, 20), (spine_x - 14, 360), (spine_x + 26, 344), 1)

    # ── BUTTONS — bookmark ribbon tabs ──────────────────────────────────
    def ribbon_btn(center, text, color):
        w, h = 220, 44
        x = center[0] - w // 2
        y = center[1] - h // 2
        # Ribbon body with notched right end
        pts = [(0, 0), (w - 14, 0), (w, h // 2), (w - 14, h), (0, h)]
        rib = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(rib, color, pts)
        pygame.draw.polygon(rib, lerp(color, NEAR_BLACK, 0.55), pts, 2)
        # Fabric weave highlights
        pygame.draw.line(rib, lerp(color, WHITE, 0.5), (6, 3), (w - 20, 3), 1)
        pygame.draw.line(rib, lerp(color, NEAR_BLACK, 0.35),
                         (6, h - 4), (w - 20, h - 4), 1)
        s.blit(rib, (x, y))
        ti = font(17, True).render(text, True, WHITE)
        sh = font(17, True).render(text, True, NEAR_BLACK)
        sh.set_alpha(140)
        tr = ti.get_rect(center=(x + (w - 8) // 2, center[1]))
        s.blit(sh, (tr.x + 1, tr.y + 2))
        s.blit(ti, tr)

    ribbon_btn((W // 2 - 4, 408), "TAKE FLIGHT", (200, 60, 50))
    ribbon_btn((W // 2 - 4, 458), "FIELD GUIDE", (60, 110, 160))
    ribbon_btn((W // 2 - 4, 508), "POWER-UPS",   (140, 90, 30))

    # ── BEST + TOP 10 inset on the right page ───────────────────────────
    # "Personal Best" in cursive (italic-feel) with quill
    pb_x, pb_y = page_r.right - 88, page_r.bottom - 60
    cap = font(12, True).render("Personal Best", True, (80, 40, 16))
    s.blit(cap, cap.get_rect(center=(pb_x, pb_y - 14)))
    pygame.draw.line(s, (120, 60, 30), (pb_x - 36, pb_y - 4),
                     (pb_x + 36, pb_y - 4), 1)
    val = font(28, True).render("42", True, (140, 30, 20))
    s.blit(val, val.get_rect(center=(pb_x, pb_y + 12)))
    # Tiny quill
    pygame.draw.line(s, (90, 30, 16), (pb_x - 44, pb_y + 26),
                     (pb_x - 28, pb_y + 6), 2)
    pygame.draw.polygon(s, (200, 60, 60),
                        [(pb_x - 44, pb_y + 26),
                         (pb_x - 50, pb_y + 32),
                         (pb_x - 38, pb_y + 22)])

    # "TOP 10 RANK" pressed ribbon on the left page bottom
    tr_cx, tr_cy = page_l.x + 70, page_l.bottom - 36
    ribbon = pygame.Rect(tr_cx - 50, tr_cy - 14, 100, 28)
    pygame.draw.polygon(s, GOLD_BRIGHT,
                        [(ribbon.x, ribbon.y), (ribbon.right, ribbon.y),
                         (ribbon.right + 6, ribbon.centery),
                         (ribbon.right, ribbon.bottom),
                         (ribbon.x, ribbon.bottom),
                         (ribbon.x - 6, ribbon.centery)])
    pygame.draw.polygon(s, (140, 90, 8),
                        [(ribbon.x, ribbon.y), (ribbon.right, ribbon.y),
                         (ribbon.right + 6, ribbon.centery),
                         (ribbon.right, ribbon.bottom),
                         (ribbon.x, ribbon.bottom),
                         (ribbon.x - 6, ribbon.centery)], 2)
    rl = font(11, True).render("TOP 10", True, NEAR_BLACK)
    s.blit(rl, rl.get_rect(center=(ribbon.centerx, ribbon.centery - 4)))
    rsub = font(8, True).render("LEAGUE", True, NEAR_BLACK)
    s.blit(rsub, rsub.get_rect(center=(ribbon.centerx, ribbon.centery + 8)))

    save("theme_b_logbook.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# Theme C — THE CARTOGRAPHER'S CHART (Sky-Route Map)
# ─────────────────────────────────────────────────────────────────────────────
def theme_c_route_map():
    s = pygame.Surface((W, H))
    # Parchment background
    gradient_v(s, (242, 222, 175), (218, 192, 138))
    # Paper texture
    random.seed(11)
    for _ in range(2200):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        c = random.randint(160, 220)
        if random.random() < 0.2:
            pygame.draw.circle(s, (c, c - 25, c - 60), (x, y), 1)
    # Tea-stain blotches
    for cx, cy, r in [(60, 80, 50), (300, 200, 40), (90, 530, 35), (310, 510, 30)]:
        for k in range(r, 0, -3):
            a = int(30 * (1 - k / r))
            blot = pygame.Surface((k * 2, k * 2), pygame.SRCALPHA)
            pygame.draw.circle(blot, (140, 80, 30, a), (k, k), k)
            s.blit(blot, (cx - k, cy - k))
    # Fold creases (vertical thirds + horizontal middle)
    for x in (W // 3, 2 * W // 3):
        line = pygame.Surface((1, H), pygame.SRCALPHA)
        line.fill((90, 60, 30, 50))
        s.blit(line, (x, 0))
    line = pygame.Surface((W, 1), pygame.SRCALPHA)
    line.fill((90, 60, 30, 50))
    s.blit(line, (0, H // 2))

    # Title scroll banner at top
    title_y = 80
    scroll = pygame.Rect(W // 2 - 140, title_y - 36, 280, 72)
    pygame.draw.rect(s, (238, 212, 162), scroll, border_radius=8)
    pygame.draw.rect(s, (130, 80, 40), scroll, 2, border_radius=8)
    # Scroll roll edges
    pygame.draw.rect(s, (180, 130, 70), (scroll.x - 10, scroll.y, 10, scroll.h))
    pygame.draw.rect(s, (180, 130, 70), (scroll.right, scroll.y, 10, scroll.h))
    pygame.draw.rect(s, (90, 60, 30), (scroll.x - 10, scroll.y, 10, scroll.h), 2)
    pygame.draw.rect(s, (90, 60, 30), (scroll.right, scroll.y, 10, scroll.h), 2)
    skybit_title(s, W // 2, title_y - 4, size=44, px=2)
    sub = font(11, True).render("SKY  COURIER  ROUTE  ·  POCKET  SKY  FLYER",
                                True, (90, 50, 20))
    s.blit(sub, sub.get_rect(center=(W // 2, title_y + 22)))

    # Map field — middle area
    map_top, map_bot = 160, 470
    # Faint compass rose lower right
    cr_cx, cr_cy = W - 50, map_bot - 30
    for ang_deg in range(0, 360, 45):
        a = math.radians(ang_deg)
        x1 = cr_cx + math.cos(a) * 4
        y1 = cr_cy + math.sin(a) * 4
        x2 = cr_cx + math.cos(a) * 22
        y2 = cr_cy + math.sin(a) * 22
        pygame.draw.line(s, (90, 50, 20), (x1, y1), (x2, y2), 1)
    pygame.draw.circle(s, (90, 50, 20), (cr_cx, cr_cy), 4)
    pygame.draw.polygon(s, (140, 30, 20),
                        [(cr_cx, cr_cy - 22), (cr_cx - 4, cr_cy),
                         (cr_cx + 4, cr_cy)])
    nlab = font(9, True).render("N", True, (90, 50, 20))
    s.blit(nlab, nlab.get_rect(center=(cr_cx, cr_cy - 30)))

    # Pencil-shaded mountains across the map field
    for pts, fill in [
        ([(0, 460), (40, 410), (90, 430), (140, 380), (200, 420), (260, 390), (320, 430), (360, 410), (360, 470), (0, 470)],
         (200, 170, 120)),
    ]:
        pygame.draw.polygon(s, fill, pts)
        for i in range(len(pts) - 2):
            pygame.draw.line(s, (110, 70, 30), pts[i], pts[i + 1], 1)

    # Route — dotted red line snaking from bottom-left (pickup) to top-right (delivery)
    route_pts = [(50, 440), (90, 410), (130, 350), (180, 310),
                 (230, 270), (270, 230), (310, 200)]
    for i in range(len(route_pts) - 1):
        x1, y1 = route_pts[i]
        x2, y2 = route_pts[i + 1]
        steps = 14
        for k in range(0, steps):
            t = k / steps
            xa = x1 + (x2 - x1) * t
            ya = y1 + (y2 - y1) * t
            if k % 2 == 0:
                pygame.draw.circle(s, (200, 50, 40), (int(xa), int(ya)), 2)

    # Start cottage (teal)
    draw_cottage(s, route_pts[0][0] + 6, route_pts[0][1] - 14, scale=0.4,
                 roof_col=COTTAGE_TEAL, with_lantern=False)
    sl = font(9, True).render("PICKUP", True, (40, 90, 70))
    s.blit(sl, (route_pts[0][0] - 24, route_pts[0][1] + 4))

    # End cottage (red)
    draw_cottage(s, route_pts[-1][0] - 4, route_pts[-1][1] - 4, scale=0.4,
                 roof_col=COTTAGE_RED, with_lantern=True)
    el = font(9, True).render("DROP-OFF", True, (120, 30, 20))
    s.blit(el, (route_pts[-1][0] - 24, route_pts[-1][1] + 18))

    # Pillar landmarks along the route (mini icons + ink labels)
    landmarks = [
        (route_pts[1][0] + 18, route_pts[1][1] - 8, "flag",      "PRAYER FLAGS"),
        (route_pts[2][0] - 20, route_pts[2][1] - 18, "lantern",  "LANTERN PEAK"),
        (route_pts[3][0] + 24, route_pts[3][1] - 22, "monastery","MONASTERY"),
        (route_pts[4][0] - 10, route_pts[4][1] - 18, "bucket",   "KFC HAZARD!"),
    ]
    for lx, ly, kind, label in landmarks:
        # Same margin_sketch palette as theme B (inline)
        if kind == "flag":
            pygame.draw.line(s, (90, 50, 24), (lx, ly + 8), (lx, ly - 12), 1)
            for i, c in enumerate([(200, 60, 60), (60, 140, 200), (240, 200, 80)]):
                pygame.draw.polygon(s, c, [(lx, ly - 10 + i * 4),
                                            (lx + 7, ly - 8 + i * 4),
                                            (lx, ly - 6 + i * 4)])
        elif kind == "lantern":
            pygame.draw.line(s, (60, 30, 16), (lx, ly - 12), (lx, ly - 6), 1)
            pygame.draw.ellipse(s, (200, 60, 60), (lx - 6, ly - 6, 12, 14))
            pygame.draw.ellipse(s, (90, 30, 30), (lx - 6, ly - 6, 12, 14), 1)
        elif kind == "monastery":
            pygame.draw.rect(s, (200, 170, 130), (lx - 8, ly - 2, 16, 12))
            pygame.draw.polygon(s, (140, 90, 50),
                                [(lx - 10, ly - 2), (lx + 10, ly - 2), (lx, ly - 12)])
        elif kind == "bucket":
            pygame.draw.polygon(s, (220, 60, 60),
                                [(lx - 9, ly - 7), (lx + 9, ly - 7),
                                 (lx + 6, ly + 7), (lx - 6, ly + 7)])
            for y in range(ly - 5, ly + 7, 3):
                pygame.draw.line(s, (250, 240, 230), (lx - 8, y), (lx + 8, y), 1)
        # Label
        lab = font(9, True).render(label, True, (110, 30, 20) if "HAZARD" in label else (60, 30, 10))
        s.blit(lab, (lx + 12, ly - 4))

    # ── BUTTONS — wooden signposts ──────────────────────────────────────
    def signpost(center, text, big=False):
        w, h = (220, 42) if big else (220, 36)
        x = center[0] - w // 2
        y = center[1] - h // 2
        # Post
        pygame.draw.rect(s, (90, 60, 30), (center[0] - 2, y + h, 4, 16))
        # Arrow plank
        pts = [(0, 4), (w - 18, 4), (w - 2, h // 2), (w - 18, h - 4), (0, h - 4)]
        sp = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(sp, (190, 140, 80), pts)
        pygame.draw.polygon(sp, (90, 50, 20), pts, 2)
        # Wood grain
        for k in range(8, h - 6, 5):
            pygame.draw.line(sp, (160, 110, 60), (10, k), (w - 26, k), 1)
        # Nail heads
        pygame.draw.circle(sp, (60, 40, 20), (16, h // 2), 2)
        pygame.draw.circle(sp, (60, 40, 20), (w - 30, h // 2), 2)
        s.blit(sp, (x, y))
        ti = font(16 if big else 14, True).render(text, True, (40, 22, 10))
        s.blit(ti, ti.get_rect(center=(x + (w - 12) // 2, center[1])))

    signpost((W // 2 - 10, 500), "TO TAKEOFF →", big=True)
    signpost((W // 2 - 10, 548), "TO BRIEFING →")
    signpost((W // 2 - 10, 590), "TO CARGO LIST →")

    # ── BEST wax seal + TOP 10 scroll in top-left margin ────────────────
    # Wax seal
    wsx, wsy = 50, 130
    pygame.draw.circle(s, (140, 20, 20), (wsx, wsy), 24)
    pygame.draw.circle(s, (200, 50, 40), (wsx, wsy), 22)
    pygame.draw.circle(s, (100, 10, 10), (wsx, wsy), 24, 2)
    bl = font(8, True).render("BEST", True, (245, 220, 180))
    s.blit(bl, bl.get_rect(center=(wsx, wsy - 7)))
    vl = font(18, True).render("42", True, (250, 220, 180))
    s.blit(vl, vl.get_rect(center=(wsx, wsy + 6)))
    # Ribbon tails
    pygame.draw.polygon(s, (140, 20, 20),
                        [(wsx - 6, wsy + 22), (wsx - 2, wsy + 22), (wsx - 14, wsy + 40)])
    pygame.draw.polygon(s, (140, 20, 20),
                        [(wsx + 2, wsy + 22), (wsx + 6, wsy + 22), (wsx + 18, wsy + 40)])

    # TOP 10 rolled scroll at top-right
    tsx, tsy = W - 50, 130
    sc = pygame.Rect(tsx - 30, tsy - 18, 60, 36)
    pygame.draw.rect(s, (245, 222, 170), sc, border_radius=6)
    pygame.draw.rect(s, (130, 80, 40), sc, 2, border_radius=6)
    # Roll ends
    pygame.draw.circle(s, (180, 130, 70), (sc.x, sc.centery), 6)
    pygame.draw.circle(s, (180, 130, 70), (sc.right, sc.centery), 6)
    pygame.draw.circle(s, (90, 50, 20), (sc.x, sc.centery), 6, 1)
    pygame.draw.circle(s, (90, 50, 20), (sc.right, sc.centery), 6, 1)
    tlab = font(9, True).render("TOP 10", True, (90, 30, 10))
    s.blit(tlab, tlab.get_rect(center=(tsx, tsy - 4)))
    # Tiny trophy doodle
    pygame.draw.polygon(s, (180, 130, 30),
                        [(tsx - 5, tsy + 4), (tsx + 5, tsy + 4),
                         (tsx + 4, tsy + 10), (tsx - 4, tsy + 10)])
    pygame.draw.rect(s, (180, 130, 30), (tsx - 5, tsy + 11, 10, 2))
    # Ribbon
    pygame.draw.line(s, (200, 50, 40), (tsx - 12, tsy + 18), (tsx + 12, tsy + 18), 2)

    save("theme_c_route_map.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# Theme D — THE COCKPIT DASHBOARD (Captain's View)
# ─────────────────────────────────────────────────────────────────────────────
def theme_d_cockpit():
    s = pygame.Surface((W, H))
    # Polished-wood panel covers most of the screen
    gradient_v(s, (88, 56, 32), (50, 32, 18))
    # Wood grain horizontal streaks
    for y in range(0, H, 8):
        a = random.randint(20, 50)
        line = pygame.Surface((W, 1), pygame.SRCALPHA)
        line.fill((30, 18, 8, a))
        s.blit(line, (0, y))

    # Brass rivets in corners of the panel
    for rx in (16, W - 16):
        for ry in (200, H - 16):
            pygame.draw.circle(s, GOLD_BRIGHT, (rx, ry), 4)
            pygame.draw.circle(s, (140, 90, 8), (rx, ry), 4, 1)
            pygame.draw.circle(s, (255, 240, 180), (rx - 1, ry - 1), 1)

    # WINDSHIELD — curved glass at the top showing biome-sky horizon
    ws_top = 10
    ws_h = 200
    ws_rect = pygame.Rect(20, ws_top, W - 40, ws_h)
    # Sky in the windshield (Skybit twilight: deep blue to peach near horizon)
    ws = pygame.Surface(ws_rect.size)
    sky_colors = [(12, 18, 55), (40, 60, 120), (180, 100, 80), (255, 200, 110)]
    seg_h = ws_h // (len(sky_colors) - 1)
    for i in range(len(sky_colors) - 1):
        for y in range(seg_h):
            t = y / max(1, seg_h - 1)
            c = lerp(sky_colors[i], sky_colors[i + 1], t)
            pygame.draw.line(ws, c, (0, i * seg_h + y),
                             (ws_rect.w, i * seg_h + y))
    # Stars near top
    random.seed(19)
    for _ in range(30):
        x = random.randint(0, ws_rect.w - 1)
        y = random.randint(0, 60)
        pygame.draw.circle(ws, (250, 250, 240), (x, y), 1)
    # Distant mountain silhouette
    pygame.draw.polygon(ws, (50, 30, 56),
                        [(0, ws_h - 30), (40, ws_h - 50),
                         (90, ws_h - 35), (140, ws_h - 60),
                         (200, ws_h - 40), (260, ws_h - 55),
                         (320, ws_h - 38), (ws_rect.w, ws_h - 45),
                         (ws_rect.w, ws_h), (0, ws_h)])
    # Tiny incoming pillar silhouette
    pygame.draw.rect(ws, (60, 40, 80), (ws_rect.w - 80, ws_h - 90, 14, 60))
    pygame.draw.rect(ws, (60, 40, 80), (ws_rect.w - 80, 0, 14, ws_h - 130))
    # Tiny Pip flying — small dark dot with red tail
    pip_x, pip_y = 70, 100
    pygame.draw.circle(ws, (240, 55, 55), (pip_x, pip_y), 4)
    pygame.draw.polygon(ws, (40, 100, 255),
                        [(pip_x + 1, pip_y - 4), (pip_x + 6, pip_y - 1),
                         (pip_x + 2, pip_y + 2)])
    # Place the windshield with a black bezel
    pygame.draw.rect(s, (10, 6, 4), ws_rect.inflate(8, 8), border_radius=24)
    s.blit(ws, ws_rect.topleft)
    # Mask windshield to rounded
    mask = pygame.Surface(ws_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=20)
    # Overdraw a glass sheen
    sheen = pygame.Surface(ws_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(sheen, (255, 255, 255, 35),
                        [(20, 6), (90, 6), (50, 60), (10, 50)])
    s.blit(sheen, ws_rect.topleft)
    # Bezel ring
    pygame.draw.rect(s, (20, 14, 8), ws_rect, 4, border_radius=20)
    pygame.draw.rect(s, GOLD_BRIGHT, ws_rect, 1, border_radius=20)

    # Title plaque mounted under the windshield
    plaque = pygame.Rect(W // 2 - 110, 218, 220, 44)
    pygame.draw.rect(s, (130, 84, 44), plaque, border_radius=6)
    pygame.draw.rect(s, (40, 22, 10), plaque, 2, border_radius=6)
    pygame.draw.line(s, (200, 160, 100),
                     (plaque.x + 6, plaque.y + 4),
                     (plaque.right - 6, plaque.y + 4), 1)
    skybit_title(s, plaque.centerx, plaque.centery, size=30, px=2)
    psub = font(9, True).render("CAPT. PIP · POCKET SKY FLYER", True, GOLD_BRIGHT)
    s.blit(psub, psub.get_rect(center=(plaque.centerx, plaque.bottom + 10)))

    # ── DASHBOARD GAUGES ────────────────────────────────────────────────
    # Altimeter (left) — round brass dial
    def gauge(cx, cy, r, label, value, accent=GOLD_BRIGHT, with_needle=True, needle_ang_deg=-30):
        # Outer rim
        pygame.draw.circle(s, (160, 110, 30), (cx, cy), r + 4)
        pygame.draw.circle(s, (60, 40, 12), (cx, cy), r + 4, 2)
        # Inner face
        pygame.draw.circle(s, (245, 232, 195), (cx, cy), r)
        pygame.draw.circle(s, (60, 40, 12), (cx, cy), r, 1)
        # Tick marks
        for ang_deg in range(0, 360, 30):
            a = math.radians(ang_deg - 90)
            x1 = cx + math.cos(a) * (r - 4)
            y1 = cy + math.sin(a) * (r - 4)
            x2 = cx + math.cos(a) * (r - 1)
            y2 = cy + math.sin(a) * (r - 1)
            pygame.draw.line(s, (60, 40, 12), (x1, y1), (x2, y2), 1)
        # Center hub
        pygame.draw.circle(s, (60, 40, 12), (cx, cy), 3)
        # Needle
        if with_needle:
            a = math.radians(needle_ang_deg - 90)
            nx = cx + math.cos(a) * (r - 6)
            ny = cy + math.sin(a) * (r - 6)
            pygame.draw.line(s, (180, 30, 30), (cx, cy), (nx, ny), 2)
        # Label inside dial
        lb = font(8, True).render(label, True, (60, 40, 12))
        s.blit(lb, lb.get_rect(center=(cx, cy + r - 8)))
        # Value
        if value:
            vf = font(13, True).render(value, True, (140, 30, 20))
            s.blit(vf, vf.get_rect(center=(cx, cy - r + 14)))

    # Two flanking gauges left and right of the title plaque, lower
    gauge(50, 318, 30, "ALT", "320 ft", needle_ang_deg=60)
    gauge(W - 50, 318, 30, "COIN", "x7", needle_ang_deg=110)

    # ── BUTTONS — chrome push-buttons / toggle switches mounted on panel ─
    def chrome_btn(center, text, big=False, glow=False):
        w, h = (240, 50) if big else (200, 40)
        x = center[0] - w // 2
        y = center[1] - h // 2
        # Recessed panel cutout
        pygame.draw.rect(s, (28, 16, 8), (x - 4, y - 4, w + 8, h + 8), border_radius=h // 2 + 4)
        # Chrome body — light vertical gradient
        b = pygame.Surface((w, h), pygame.SRCALPHA)
        for yy in range(h):
            t = yy / max(1, h - 1)
            c = lerp((240, 240, 250), (130, 130, 145), t)
            pygame.draw.line(b, (*c, 255), (0, yy), (w, yy))
        # Top sheen
        pygame.draw.line(b, (255, 255, 255, 230), (h // 2, 3), (w - h // 2, 3), 2)
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=h // 2)
        b.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # Brass rim
        pygame.draw.rect(b, GOLD_BRIGHT, (0, 0, w, h), width=2, border_radius=h // 2)
        s.blit(b, (x, y))
        # Engraved text
        sz = 19 if big else 16
        ti = font(sz, True).render(text, True, (40, 22, 12))
        sh = font(sz, True).render(text, True, (220, 220, 230))
        sr = ti.get_rect(center=center)
        s.blit(sh, (sr.x + 1, sr.y + 1))
        s.blit(ti, sr)
        if glow:
            # Green "ARMED" LED on the right
            led_x = x + w - 16
            led_y = center[1]
            pygame.draw.circle(s, (40, 200, 90), (led_x, led_y), 4)
            pygame.draw.circle(s, (200, 255, 220), (led_x - 1, led_y - 1), 1)

    chrome_btn((W // 2, 390), "FLIGHT  START", big=True, glow=True)
    chrome_btn((W // 2, 448), "MANUAL")
    chrome_btn((W // 2, 498), "POWER-UPS")

    # ── BEST = odometer ─────────────────────────────────────────────────
    odo = pygame.Rect(28, 548, 130, 56)
    pygame.draw.rect(s, (16, 8, 4), odo, border_radius=6)
    pygame.draw.rect(s, GOLD_BRIGHT, odo, 2, border_radius=6)
    olab = font(9, True).render("BEST  RUN", True, GOLD_BRIGHT)
    s.blit(olab, (odo.x + 10, odo.y + 6))
    # Six digit rolls
    for i, ch in enumerate("000042"):
        cell = pygame.Rect(odo.x + 10 + i * 19, odo.y + 22, 17, 26)
        pygame.draw.rect(s, (245, 232, 195), cell)
        pygame.draw.rect(s, (50, 30, 14), cell, 1)
        ti = font(18, True).render(ch, True, (170, 30, 20))
        s.blit(ti, ti.get_rect(center=cell.center))

    # ── TOP 10 = brass radio dial ───────────────────────────────────────
    dial_cx, dial_cy = W - 70, 576
    pygame.draw.circle(s, (160, 110, 30), (dial_cx, dial_cy), 32)
    pygame.draw.circle(s, (220, 180, 90), (dial_cx, dial_cy), 28)
    pygame.draw.circle(s, (60, 40, 12), (dial_cx, dial_cy), 32, 2)
    # Knurled edge
    for ang_deg in range(0, 360, 18):
        a = math.radians(ang_deg)
        x1 = dial_cx + math.cos(a) * 28
        y1 = dial_cy + math.sin(a) * 28
        x2 = dial_cx + math.cos(a) * 32
        y2 = dial_cy + math.sin(a) * 32
        pygame.draw.line(s, (60, 40, 12), (x1, y1), (x2, y2), 1)
    # Indicator notch
    pygame.draw.polygon(s, (180, 30, 20),
                        [(dial_cx - 3, dial_cy - 30), (dial_cx + 3, dial_cy - 30),
                         (dial_cx, dial_cy - 22)])
    # Label plaque
    pl = pygame.Rect(dial_cx - 36, dial_cy + 24, 72, 14)
    pygame.draw.rect(s, (20, 12, 6), pl, border_radius=3)
    tlab = font(8, True).render("TOP  COURIERS", True, GOLD_BRIGHT)
    s.blit(tlab, tlab.get_rect(center=pl.center))

    save("theme_d_cockpit.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# Theme E — ARRIVAL AT THE STARLIT COTTAGE (Journey's End)
# ─────────────────────────────────────────────────────────────────────────────
def theme_e_arrival_cottage():
    s = pygame.Surface((W, H))
    # Deep night gradient
    gradient_v(s, NIGHT_DEEP, (16, 8, 44))

    # Twinkly stars
    random.seed(17)
    for _ in range(110):
        x = random.randint(0, W - 1)
        y = random.randint(0, 380)
        r = random.choice([1, 1, 1, 2])
        a = random.randint(120, 255)
        pygame.draw.circle(s, (240, 245, 255), (x, y), r)

    # Big sparkle stars forming the Pip+trophy constellation
    constellation_pts = [
        (W // 2 - 70, 90),
        (W // 2 - 40, 70),
        (W // 2,      60),
        (W // 2 + 32, 76),
        (W // 2 + 60, 100),
        # tail
        (W // 2 + 90, 130),
        (W // 2 + 50, 140),
        # trophy beside
        (W // 2 - 110, 130),
        (W // 2 - 95, 150),
        (W // 2 - 80, 130),
    ]
    for cx, cy in constellation_pts:
        pygame.draw.circle(s, (255, 255, 220), (cx, cy), 2)
        pygame.draw.line(s, (255, 255, 220), (cx - 6, cy), (cx + 6, cy), 1)
        pygame.draw.line(s, (255, 255, 220), (cx, cy - 6), (cx, cy + 6), 1)
    # Connecting lines (Pip body)
    for a, b in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (4, 6), (7, 8), (8, 9)]:
        pygame.draw.aaline(s, (255, 255, 220, 120),
                           constellation_pts[a], constellation_pts[b])

    # Moon — soft glow
    moon_cx, moon_cy = 80, 80
    moon_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
    for r in range(58, 0, -2):
        a = int(40 * (1 - r / 58))
        pygame.draw.circle(moon_glow, (255, 245, 200, a), (60, 60), r)
    s.blit(moon_glow, (moon_cx - 60, moon_cy - 60))
    pygame.draw.circle(s, (250, 245, 220), (moon_cx, moon_cy), 18)
    pygame.draw.circle(s, (220, 220, 200), (moon_cx + 5, moon_cy - 3), 14)

    # Mountain silhouette deep in the back
    pygame.draw.polygon(s, (20, 14, 48),
                        [(0, 450), (60, 380), (120, 410), (180, 360),
                         (240, 400), (300, 370), (360, 410), (360, 470), (0, 470)])
    pygame.draw.polygon(s, (10, 6, 30),
                        [(0, 490), (80, 460), (160, 480), (240, 450),
                         (320, 470), (360, 460), (360, 540), (0, 540)])

    # Title sign — wooden plaque hanging from a chain at top
    title_y = 220
    plaque = pygame.Rect(W // 2 - 140, title_y - 40, 280, 80)
    # Chain from top
    for k in range(0, 18, 3):
        pygame.draw.circle(s, (170, 170, 175), (W // 2, k), 3, 1)
    pygame.draw.rect(s, (88, 50, 24), plaque, border_radius=10)
    pygame.draw.rect(s, (30, 14, 8), plaque, 3, border_radius=10)
    pygame.draw.line(s, (200, 160, 100),
                     (plaque.x + 8, plaque.y + 6),
                     (plaque.right - 8, plaque.y + 6), 1)
    skybit_title(s, plaque.centerx, plaque.centery - 8, size=46, px=2)
    sub = font(11, True).render("DELIVERY  CONFIRMED  ·  POCKET  SKY  FLYER",
                                True, GOLD_BRIGHT)
    s.blit(sub, sub.get_rect(center=(plaque.centerx, plaque.bottom - 14)))

    # The red-roofed delivery cottage (centre, larger)
    draw_cottage(s, W // 2, 470, scale=1.05,
                 roof_col=COTTAGE_RED, with_lantern=True)
    # Smoke puffs from chimney
    for i, (dx, dy, r) in enumerate([(-26, 380, 6), (-22, 366, 7), (-14, 350, 8), (-4, 336, 9)]):
        smoke = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(smoke, (220, 220, 235, 130 - i * 20), (r + 1, r + 1), r)
        s.blit(smoke, (W // 2 + dx, dy))

    # Parcel on the doorstep
    draw_parcel(s, W // 2, 510, size=16)

    # Ground
    pygame.draw.rect(s, (8, 18, 14), (0, 530, W, H - 530))
    # Grass tufts
    for x in range(0, W, 14):
        pygame.draw.line(s, (12, 36, 22), (x, 530), (x - 2, 524), 1)
        pygame.draw.line(s, (12, 36, 22), (x + 4, 530), (x + 6, 524), 1)

    # ── BUTTONS — wood-burnished door plaques ───────────────────────────
    def door_plaque(center, text, big=False):
        w, h = (240, 46) if big else (220, 38)
        x = center[0] - w // 2
        y = center[1] - h // 2
        pl = pygame.Surface((w, h), pygame.SRCALPHA)
        # Wood
        for yy in range(h):
            t = yy / max(1, h - 1)
            c = lerp((130, 86, 52), (70, 42, 22), t)
            pygame.draw.line(pl, (*c, 255), (0, yy), (w, yy))
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=8)
        pl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # Brass border
        pygame.draw.rect(pl, GOLD_BRIGHT, (0, 0, w, h), width=2, border_radius=8)
        # Top sheen
        pygame.draw.line(pl, (220, 180, 110, 150), (10, 3), (w - 10, 3))
        # Corner nails
        for nx, ny in [(8, 8), (w - 8, 8), (8, h - 8), (w - 8, h - 8)]:
            pygame.draw.circle(pl, (255, 230, 150), (nx, ny), 2)
            pygame.draw.circle(pl, (90, 60, 8), (nx, ny), 2, 1)
        s.blit(pl, (x, y))
        # Engraved gold text
        sz = 18 if big else 16
        ti = font(sz, True).render(text, True, GOLD_BRIGHT)
        sh = font(sz, True).render(text, True, NEAR_BLACK)
        tr = ti.get_rect(center=center)
        s.blit(sh, (tr.x + 1, tr.y + 2))
        s.blit(ti, tr)

    # Positioned to the side of the cottage, like signs nailed to the wall
    door_plaque((W // 2, 320), "RING  THE  BELL", big=True)
    door_plaque((W // 2 + 4, 372), "READ  THE  LETTER")
    door_plaque((W // 2 + 4, 422), "OPEN  THE  BOX")

    # ── BEST = engraved mailbox plate (bottom-left) ────────────────────
    mb_rect = pygame.Rect(28, 568, 120, 50)
    # Mailbox post
    pygame.draw.rect(s, (40, 24, 12), (mb_rect.x - 6, mb_rect.bottom - 4, 4, 22))
    # Body
    pygame.draw.rect(s, (60, 50, 60), mb_rect)
    pygame.draw.rect(s, (16, 12, 16), mb_rect, 2)
    # Brass plate
    plate = pygame.Rect(mb_rect.x + 6, mb_rect.y + 6, mb_rect.w - 12, mb_rect.h - 12)
    pygame.draw.rect(s, GOLD_BRIGHT, plate, border_radius=3)
    pygame.draw.rect(s, (140, 90, 8), plate, 1, border_radius=3)
    bl = font(9, True).render("BEST", True, NEAR_BLACK)
    s.blit(bl, bl.get_rect(center=(plate.centerx, plate.y + 10)))
    vl = font(20, True).render("42", True, NEAR_BLACK)
    s.blit(vl, vl.get_rect(center=(plate.centerx, plate.y + 26)))
    # Mailbox flag (raised)
    pygame.draw.polygon(s, (200, 50, 40),
                        [(mb_rect.right, mb_rect.y + 4),
                         (mb_rect.right + 14, mb_rect.y + 10),
                         (mb_rect.right, mb_rect.y + 16)])

    # ── TOP 10 = constellation badge (bottom-right) ────────────────────
    badge_rect = pygame.Rect(W - 148, 568, 120, 50)
    pygame.draw.rect(s, PANEL_DARK, badge_rect, border_radius=12)
    pygame.draw.rect(s, GOLD_BRIGHT, badge_rect, 2, border_radius=12)
    # Tiny constellation inside
    inset_pts = [(20, 26), (40, 18), (60, 12), (80, 18), (100, 28),
                 (76, 38), (40, 38)]
    for px_, py_ in inset_pts:
        pygame.draw.circle(s, (255, 250, 220), (badge_rect.x + px_, badge_rect.y + py_), 2)
    for a, b in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]:
        pygame.draw.aaline(s, (255, 250, 220, 130),
                           (badge_rect.x + inset_pts[a][0], badge_rect.y + inset_pts[a][1]),
                           (badge_rect.x + inset_pts[b][0], badge_rect.y + inset_pts[b][1]))
    tl = font(9, True).render("TOP 10", True, GOLD_BRIGHT)
    s.blit(tl, tl.get_rect(center=(badge_rect.centerx, badge_rect.bottom - 8)))

    save("theme_e_arrival_cottage.png", s)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating Skybit story-themed menu mockups...")
    theme_a_dispatch_desk()
    theme_b_logbook()
    theme_c_route_map()
    theme_d_cockpit()
    theme_e_arrival_cottage()
    print("Done.")
