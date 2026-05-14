"""Generate the full Pip Scarlet UI set — 8 screens at 720x1280.

The user picked variant #1 (Pip Scarlet). This rolls the same
scarlet/gold/cream system across every non-gameplay screen so the
whole UI reads as one cohesive set.

Every screen shares:
  * Polished v3 night-sky background (gradient + 4-tier stars w/
    soft halos + multi-layer clouds + 3 mountain layers + warm
    horizon haze)
  * Canonical SKYBIT-style title treatment (gold-on-red, beveled)
  * Pip Scarlet pill — scarlet body (240,55,55 → 148,20,20),
    gold border, cream text, deep-red shadow, optional gold glow
    on primary
  * Dark-navy gold-trimmed cards/panels for everything else

Output filenames:
  v3_scarlet_main.png         — main menu (copy of v3_bold_1_pip_scarlet)
  v3_scarlet_pause.png        — pause overlay w/ live score panel
  v3_scarlet_stats.png        — run summary w/ score + 5-row stat card
  v3_scarlet_gameover.png     — game over w/ NEW BEST gold ribbon
  v3_scarlet_name_entry.png   — trophy + nameplate + SUBMIT/SKIP
  v3_scarlet_leaderboard.png  — 10 ranked cards w/ gold/silver/bronze
  v3_scarlet_powerups.png     — 2x3 power-up grid w/ icons
  v3_scarlet_intro.png        — 3 numbered cards + TAP TO BEGIN
"""
import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

SCALE = 2
W, H = 360 * SCALE, 640 * SCALE
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "menu_polish")
os.makedirs(OUT, exist_ok=True)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "game", "assets")
FONT_BOLD = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")
FONT_REG  = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")

# Skybit + Pip Scarlet palette
GOLD_BRIGHT    = (240, 192,  64)
GOLD_MUTED     = (216, 184,  85)
GOLD_DEEP      = (180, 130,  20)
SILVER         = (210, 215, 225)
SILVER_DARK    = (130, 140, 160)
BRONZE         = (200, 130,  64)
BRONZE_DARK    = (130,  76,  30)
RED_OUTLINE    = (168,  32,  16)
SCARLET_TOP    = (240,  55,  55)
SCARLET_BOT    = (148,  20,  20)
SCARLET_SHADOW = ( 60,   8,   8)
PANEL_DARK     = ( 12,   8,  38)
PANEL_LIGHTER  = ( 26,  18,  62)
NIGHT_DEEP     = (  6,   1,  21)
NIGHT_MID      = ( 22,  14,  58)
CREAM          = (250, 238, 210)
NEAR_BLACK     = ( 12,   8,  18)


def font(size, bold=True):
    return pygame.font.Font(FONT_BOLD if bold else FONT_REG, int(size * SCALE))


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def gradient_v(surf, top, bot, rect=None):
    r = rect or surf.get_rect()
    for y in range(r.height):
        t = y / max(1, r.height - 1)
        c = lerp(top, bot, t)
        pygame.draw.line(surf, c, (r.x, r.y + y), (r.x + r.width - 1, r.y + y))


def save(name, surf):
    out = os.path.join(OUT, name)
    pygame.image.save(surf, out)
    print(f"  wrote {out} ({W}x{H})")


# ── Background + atmosphere (identical across every screen) ─────────────────

def sky_with_stars(surf, dim=0):
    gradient_v(surf, NIGHT_DEEP, NIGHT_MID)
    random.seed(42)
    for _ in range(220):
        x = random.randint(0, W - 1)
        y = random.randint(0, int(420 * SCALE))
        tier = random.choices([0, 1, 2, 3], weights=[64, 24, 9, 3])[0]
        r = (1 + tier) * SCALE
        a = random.randint(140, 255)
        if tier >= 2:
            halo = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
            for hr in range(r * 3, 0, -1):
                ha = int(22 * (1 - hr / (r * 3)))
                pygame.draw.circle(halo, (220, 230, 255, ha),
                                   (r * 3, r * 3), hr)
            surf.blit(halo, (x - r * 3, y - r * 3))
        d = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(d, (240, 240, 250, a), (r + 1, r + 1), r)
        surf.blit(d, (x - r - 1, y - r - 1))
    if dim:
        d = pygame.Surface((W, H), pygame.SRCALPHA)
        d.fill((0, 0, 0, dim))
        surf.blit(d, (0, 0))


def clouds(surf):
    for cx, cy, cw in [(60, 90, 110), (260, 70, 120), (320, 165, 86)]:
        cs = pygame.Surface((cw * SCALE, 36 * SCALE), pygame.SRCALPHA)
        for radius, dy in [(cw // 2, 18), (cw // 3, 12), (cw // 4, 8)]:
            for j in range(radius, 0, -2):
                a = int(18 * (1 - j / radius))
                pygame.draw.ellipse(
                    cs, (50, 38, 78, a),
                    (cw * SCALE // 2 - j * SCALE,
                     dy * SCALE - j * SCALE // 2,
                     j * 2 * SCALE, j * SCALE))
        surf.blit(cs, (cx * SCALE - cw * SCALE // 2,
                       cy * SCALE - 18 * SCALE))


def mountains_layered(surf):
    deepest = [(0, 640), (0, 460), (50, 410), (110, 430), (170, 380),
               (230, 415), (290, 380), (360, 410), (360, 640)]
    far = [(0, 640), (0, 490), (60, 420), (120, 450), (200, 375),
           (280, 430), (360, 360), (360, 400), (360, 640)]
    near = [(0, 640), (0, 530), (80, 505), (160, 520), (240, 490),
            (320, 510), (360, 495), (360, 640)]
    m = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(m, (18, 28, 60, 160),
                        [(x * SCALE, y * SCALE) for x, y in deepest])
    pygame.draw.polygon(m, (14, 26, 50, 220),
                        [(x * SCALE, y * SCALE) for x, y in far])
    pygame.draw.polygon(m, (10, 18, 36, 235),
                        [(x * SCALE, y * SCALE) for x, y in near])
    surf.blit(m, (0, 0))
    haze = pygame.Surface((W, 60 * SCALE), pygame.SRCALPHA)
    for yy in range(60 * SCALE):
        a = int(22 * (1 - yy / (60 * SCALE)))
        pygame.draw.line(haze, (60, 90, 140, a), (0, yy), (W, yy))
    surf.blit(haze, (0, 360 * SCALE))


def backdrop(surf, dim=0):
    sky_with_stars(surf, dim=dim)
    clouds(surf)
    mountains_layered(surf)


# ── Title / subtitle / divider ──────────────────────────────────────────────

def big_title(surf, text, center, size=60):
    """Canonical Skybit gold-on-red title treatment."""
    cx, cy = center
    f = font(size, True)
    img = f.render(text, True, GOLD_BRIGHT)
    out = f.render(text, True, RED_OUTLINE)
    sh  = f.render(text, True, NEAR_BLACK)
    r = img.get_rect(center=(cx, cy))
    px = 3 * SCALE
    for ox in (-px, 0, px):
        for oy in (-px, 0, px):
            if ox or oy:
                surf.blit(out, (r.x + ox, r.y + oy))
    sh.set_alpha(170)
    surf.blit(sh, (r.x + 3 * SCALE, r.y + 5 * SCALE))
    surf.blit(img, r.topleft)
    return r


def subtitle(surf, text, center, size=16):
    cx, cy = center
    f = font(size, True)
    img = f.render(text, True, GOLD_BRIGHT)
    out = f.render(text, True, RED_OUTLINE)
    r = img.get_rect(center=(cx, cy))
    px = 2 * SCALE
    for ox in (-px, 0, px):
        for oy in (-px, 0, px):
            if ox or oy:
                surf.blit(out, (r.x + ox, r.y + oy))
    surf.blit(img, r.topleft)


def divider(surf, cy, width=140):
    line = pygame.Surface((width * SCALE, 1 * SCALE), pygame.SRCALPHA)
    line.fill((*GOLD_BRIGHT, 120))
    surf.blit(line, line.get_rect(center=(W // 2, cy)))


# ── Pip Scarlet pill ────────────────────────────────────────────────────────

def pill(surf, center, text, size=22, min_w=234, h=46, primary=False):
    """Scarlet body + gold border + cream text. Optional gold glow on
    primary action button."""
    h *= SCALE
    cx, cy = center
    f = font(size, True)
    img = f.render(text, True, CREAM)
    w = max(min_w * SCALE, img.get_width() + 50 * SCALE)
    x = cx - w // 2
    y = cy - h // 2

    if primary:
        glow = pygame.Surface((w + 28 * SCALE, h + 28 * SCALE),
                              pygame.SRCALPHA)
        for r in range(12 * SCALE, 0, -SCALE):
            a = int(48 * r / (12 * SCALE))
            pygame.draw.rect(glow, (*GOLD_BRIGHT, a // 4),
                             (14 * SCALE - r, 14 * SCALE - r,
                              w + r * 2, h + r * 2),
                             border_radius=(h + r * 2) // 2)
        surf.blit(glow, (x - 14 * SCALE, y - 14 * SCALE))

    # Drop shadow
    sh = pygame.Surface((w + 4 * SCALE, h + 4 * SCALE), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90),
                     (0, 0, w + 4 * SCALE, h + 4 * SCALE),
                     border_radius=(h + 4 * SCALE) // 2)
    surf.blit(sh, (x - 2 * SCALE, y + 6 * SCALE))

    # Body
    p = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = lerp(SCARLET_TOP, SCARLET_BOT, t)
        pygame.draw.line(p, (*c, 255), (0, yy), (w, yy))
    frost = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h // 2):
        a = int(50 * (1 - yy / (h / 2)))
        pygame.draw.line(frost, (255, 245, 220, a), (0, yy), (w, yy))
    p.blit(frost, (0, 0))
    bsh = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h // 2, h):
        a = int(55 * (yy - h // 2) / (h / 2))
        pygame.draw.line(bsh, (0, 0, 0, a), (0, yy), (w, yy))
    p.blit(bsh, (0, 0))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_radius=h // 2)
    p.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(p, GOLD_BRIGHT, (0, 0, w, h),
                     width=2 * SCALE, border_radius=h // 2)
    pygame.draw.line(p, (*GOLD_BRIGHT, 110),
                     (h // 2, 3 * SCALE),
                     (w - h // 2, 3 * SCALE), 1 * SCALE)
    surf.blit(p, (x, y))

    sh_img = f.render(text, True, SCARLET_SHADOW)
    sh_img.set_alpha(220)
    tr = img.get_rect(center=(cx, cy))
    surf.blit(sh_img, (tr.x + 2 * SCALE, tr.y + 2 * SCALE))
    surf.blit(img, tr)
    return pygame.Rect(x, y, w, h)


# ── Dark-navy gold-trimmed card / panel ─────────────────────────────────────

def card(surf, rect, border_alpha=130, accent_alpha=110):
    sh = pygame.Surface((rect.w + 4 * SCALE, rect.h + 4 * SCALE),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90),
                     (0, 0, rect.w + 4 * SCALE, rect.h + 4 * SCALE),
                     border_radius=14 * SCALE)
    surf.blit(sh, (rect.x - 2 * SCALE, rect.y + 4 * SCALE))
    pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(pnl, (*PANEL_DARK, 220),
                     (0, 0, rect.w, rect.h), border_radius=14 * SCALE)
    pygame.draw.rect(pnl, (*GOLD_BRIGHT, border_alpha),
                     (0, 0, rect.w, rect.h),
                     width=1 * SCALE, border_radius=14 * SCALE)
    accent = pygame.Surface((rect.w - 28 * SCALE, 2), pygame.SRCALPHA)
    accent.fill((*GOLD_BRIGHT, accent_alpha))
    pnl.blit(accent, (14 * SCALE, 4))
    pygame.draw.line(pnl, (255, 220, 140, 90),
                     (14 * SCALE, 2),
                     (rect.w - 14 * SCALE, 2), 1 * SCALE)
    surf.blit(pnl, rect.topleft)


def score_panel(surf, rect, label, value, large=False):
    """A card used to show a labelled numeric value (BEST, SCORE, etc.)."""
    card(surf, rect)
    lf = font(12, False).render(label, True, GOLD_MUTED)
    lf.set_alpha(220)
    surf.blit(lf, lf.get_rect(center=(rect.centerx,
                                       rect.y + 14 * SCALE)))
    val_size = 36 if large else 24
    vf = font(val_size, True).render(str(value), True, GOLD_BRIGHT)
    vs = font(val_size, True).render(str(value), True, NEAR_BLACK)
    vs.set_alpha(170)
    vr = vf.get_rect(center=(rect.centerx, rect.y + rect.h - 22 * SCALE))
    surf.blit(vs, (vr.x + 1 * SCALE, vr.y + 2 * SCALE))
    surf.blit(vf, vr)


def score_emblem(surf, cx, cy, r, label, value, with_ribbon=False):
    """Hero score display — circular gold medallion with scarlet accent
    ring, dark-navy interior, radial laurel ticks, label at top, big
    gold value centred. Optional scarlet ribbon tail beneath for the
    celebratory moments. This is the appealing version of the
    rectangular score_panel."""
    # Soft drop shadow
    sh = pygame.Surface((r * 2 + 16, r * 2 + 16), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, 95), (r + 8, r + 8), r + 2)
    surf.blit(sh, (cx - r - 8, cy - r + 4))

    # Dark navy interior
    pygame.draw.circle(surf, PANEL_DARK, (cx, cy), r)

    # Subtle inner radial glow (warm light from inside)
    glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for rr in range(r - 6 * SCALE, 0, -SCALE):
        a = int(14 * (1 - rr / (r - 6 * SCALE)))
        pygame.draw.circle(glow, (255, 220, 140, a),
                           (r, r - r // 4), rr)
    surf.blit(glow, (cx - r, cy - r))

    # Thick outer gold ring
    pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), r, 3 * SCALE)
    # Slim scarlet accent ring just inside (signature theme touch)
    scarlet_r = r - 4 * SCALE
    pygame.draw.circle(surf, SCARLET_TOP, (cx, cy), scarlet_r, 2 * SCALE)
    # Thin gold inner ring
    pygame.draw.circle(surf, GOLD_DEEP, (cx, cy), r - 9 * SCALE, 1 * SCALE)

    # Radial laurel ticks on the gold outer ring
    for ang_deg in range(0, 360, 12):
        a = math.radians(ang_deg - 90)
        x1 = cx + math.cos(a) * (r - 1 * SCALE)
        y1 = cy + math.sin(a) * (r - 1 * SCALE)
        x2 = cx + math.cos(a) * (r + 2 * SCALE)
        y2 = cy + math.sin(a) * (r + 2 * SCALE)
        pygame.draw.line(surf, GOLD_DEEP, (x1, y1), (x2, y2), 1 * SCALE)

    # Label at top
    lbl_y = cy - int(r * 0.42)
    lf = font(13, True).render(label, True, GOLD_MUTED)
    lf.set_alpha(230)
    surf.blit(lf, lf.get_rect(center=(cx, lbl_y)))

    # Value — big, gold, with a soft black shadow
    val_size = max(16, int(r * 0.55 / SCALE))
    vf = font(val_size, True).render(str(value), True, GOLD_BRIGHT)
    vs = font(val_size, True).render(str(value), True, NEAR_BLACK)
    vs.set_alpha(180)
    vr = vf.get_rect(center=(cx, cy + int(r * 0.15)))
    surf.blit(vs, (vr.x + 2 * SCALE, vr.y + 3 * SCALE))
    surf.blit(vf, vr)

    # Optional scarlet ribbon tail beneath
    if with_ribbon:
        ribbon_pts = [
            (cx - int(r * 0.42), cy + r - 2 * SCALE),
            (cx + int(r * 0.42), cy + r - 2 * SCALE),
            (cx + int(r * 0.32), cy + r + 16 * SCALE),
            (cx,                 cy + r + 9 * SCALE),
            (cx - int(r * 0.32), cy + r + 16 * SCALE),
        ]
        pygame.draw.polygon(surf, SCARLET_TOP, ribbon_pts)
        pygame.draw.polygon(surf, SCARLET_SHADOW, ribbon_pts, 1 * SCALE)
        pygame.draw.line(surf, (255, 110, 100),
                         (cx, cy + r - 2 * SCALE),
                         (cx, cy + r + 9 * SCALE), 1 * SCALE)


# ── Trophy + ribbon banner + nameplate ──────────────────────────────────────

def draw_trophy(surf, cx, cy, size):
    s = int(size)
    cup_top_y = int(cy - s + 2)
    cup_bot_y = int(cy + 2)
    pts = [(cx - s, cup_top_y), (cx + s, cup_top_y),
           (cx + s - 3, cup_bot_y), (cx - s + 3, cup_bot_y)]
    pygame.draw.polygon(surf, GOLD_BRIGHT, pts)
    pygame.draw.polygon(surf, GOLD_DEEP, pts, 1)
    h_w = max(4, s // 4)
    pygame.draw.arc(surf, GOLD_BRIGHT,
                    (cx - s - h_w, cup_top_y + 2, h_w * 2, s),
                    math.pi / 2, math.pi * 3 / 2, 2)
    pygame.draw.arc(surf, GOLD_BRIGHT,
                    (cx + s - h_w, cup_top_y + 2, h_w * 2, s),
                    -math.pi / 2, math.pi / 2, 2)
    sw = max(3, s // 5)
    pygame.draw.rect(surf, GOLD_BRIGHT,
                     (cx - sw // 2, cup_bot_y, sw, s // 2))
    bw = s * 2
    pygame.draw.rect(surf, GOLD_BRIGHT,
                     (cx - bw // 2, cup_bot_y + s // 2, bw, max(2, s // 4)))
    pygame.draw.rect(surf, GOLD_BRIGHT,
                     (cx - bw // 2 - 2, cup_bot_y + s // 2 + max(2, s // 4),
                      bw + 4, max(2, s // 5)))


def ribbon_banner(surf, cx, cy, text, w=180):
    """Hanging gold cloth banner with notched ends + scarlet trim."""
    w *= SCALE
    h = 30 * SCALE
    x = cx - w // 2
    y = cy - h // 2
    body_pts = [
        (x + 12 * SCALE, y),
        (x + w - 12 * SCALE, y),
        (x + w, y + h // 2),
        (x + w - 12 * SCALE, y + h),
        (x + 12 * SCALE, y + h),
        (x, y + h // 2),
    ]
    pygame.draw.polygon(surf, GOLD_BRIGHT, body_pts)
    pygame.draw.polygon(surf, GOLD_DEEP, body_pts, 2 * SCALE)
    pygame.draw.line(surf, SCARLET_BOT,
                     (x + 12 * SCALE, y + 3 * SCALE),
                     (x + w - 12 * SCALE, y + 3 * SCALE), 1 * SCALE)
    pygame.draw.line(surf, SCARLET_BOT,
                     (x + 12 * SCALE, y + h - 4 * SCALE),
                     (x + w - 12 * SCALE, y + h - 4 * SCALE), 1 * SCALE)
    tf = font(14, True).render(text, True, NEAR_BLACK)
    surf.blit(tf, tf.get_rect(center=(cx, cy)))


def nameplate(surf, rect, sample_text=""):
    """Engraved gold-rim plate with corner rivets + dark-navy interior."""
    pygame.draw.rect(surf, GOLD_BRIGHT, rect,
                     border_radius=8 * SCALE)
    inner = rect.inflate(-6 * SCALE, -6 * SCALE)
    pygame.draw.rect(surf, PANEL_DARK, inner,
                     border_radius=6 * SCALE)
    pygame.draw.rect(surf, GOLD_DEEP, rect, width=2 * SCALE,
                     border_radius=8 * SCALE)
    pygame.draw.line(surf, (255, 240, 180, 220),
                     (rect.x + 10 * SCALE, rect.y + 3 * SCALE),
                     (rect.right - 10 * SCALE, rect.y + 3 * SCALE), 1 * SCALE)
    for rx, ry in [(rect.x + 8 * SCALE, rect.y + 8 * SCALE),
                   (rect.right - 8 * SCALE, rect.y + 8 * SCALE),
                   (rect.x + 8 * SCALE, rect.bottom - 8 * SCALE),
                   (rect.right - 8 * SCALE, rect.bottom - 8 * SCALE)]:
        pygame.draw.circle(surf, GOLD_DEEP, (rx, ry), 3 * SCALE)
        pygame.draw.circle(surf, GOLD_BRIGHT, (rx, ry), 3 * SCALE, 1 * SCALE)
        pygame.draw.circle(surf, (255, 240, 180),
                           (rx - 1 * SCALE, ry - 1 * SCALE), 1 * SCALE)
    if sample_text:
        tf = font(28, True).render(sample_text, True, GOLD_BRIGHT)
        sh = font(28, True).render(sample_text, True, NEAR_BLACK)
        sh.set_alpha(180)
        tr = tf.get_rect(center=rect.center)
        surf.blit(sh, (tr.x + 1 * SCALE, tr.y + 2 * SCALE))
        surf.blit(tf, tr)


# ── Procedural power-up icons (small enough for a card centre) ──────────────

def icon_triple(surf, cx, cy, r):
    for dx, dy in [(-r * 0.5, r * 0.1), (0, -r * 0.3), (r * 0.5, r * 0.1)]:
        pygame.draw.circle(surf, GOLD_BRIGHT,
                           (int(cx + dx), int(cy + dy)), int(r * 0.35))
        pygame.draw.circle(surf, GOLD_DARK := GOLD_DEEP,
                           (int(cx + dx), int(cy + dy)), int(r * 0.35),
                           1 * SCALE)
        sf = font(11, True).render("$", True, (40, 110, 40))
        surf.blit(sf, sf.get_rect(center=(int(cx + dx), int(cy + dy))))


def icon_magnet(surf, cx, cy, r):
    inner_r = int(r * 0.6)
    outer_r = int(r * 0.95)
    pygame.draw.arc(surf, SCARLET_TOP,
                    (cx - outer_r, cy - outer_r, outer_r * 2, outer_r * 2),
                    math.pi, 2 * math.pi, int(r * 0.3))
    pygame.draw.rect(surf, SILVER,
                     (cx - outer_r, cy - 2,
                      outer_r - inner_r + 1, 6 * SCALE))
    pygame.draw.rect(surf, SILVER,
                     (cx + inner_r - 1, cy - 2,
                      outer_r - inner_r + 1, 6 * SCALE))


def icon_slowmo(surf, cx, cy, r):
    w = int(r * 0.7)
    h = int(r * 1.1)
    top = [(cx - w, cy - h // 2), (cx + w, cy - h // 2),
           (cx + 2 * SCALE, cy), (cx - 2 * SCALE, cy)]
    bot = [(cx - 2 * SCALE, cy), (cx + 2 * SCALE, cy),
           (cx + w, cy + h // 2), (cx - w, cy + h // 2)]
    pygame.draw.polygon(surf, (180, 90, 220), top)
    pygame.draw.polygon(surf, (180, 90, 220), bot)
    pygame.draw.polygon(surf, GOLD_BRIGHT, top, 2 * SCALE)
    pygame.draw.polygon(surf, GOLD_BRIGHT, bot, 2 * SCALE)


def icon_kfc(surf, cx, cy, r):
    bw = int(r * 1.0)
    bh = int(r * 1.0)
    pts = [(cx - bw // 2, cy - bh // 2),
           (cx + bw // 2, cy - bh // 2),
           (cx + bw // 2 - 3 * SCALE, cy + bh // 2),
           (cx - bw // 2 + 3 * SCALE, cy + bh // 2)]
    pygame.draw.polygon(surf, SCARLET_TOP, pts)
    pygame.draw.polygon(surf, NEAR_BLACK, pts, 1 * SCALE)
    for k in range(3):
        y = cy - bh // 2 + (k + 1) * bh // 4
        pygame.draw.line(surf, (250, 240, 230),
                         (cx - bw // 2 + 2 * SCALE, y),
                         (cx + bw // 2 - 2 * SCALE, y), 2 * SCALE)


def icon_ghost(surf, cx, cy, r):
    w = int(r * 1.1)
    h = int(r * 1.2)
    top_arc = pygame.Rect(cx - w // 2, cy - h // 2, w, h * 2 // 3)
    pygame.draw.ellipse(surf, (200, 230, 255), top_arc)
    pygame.draw.rect(surf, (200, 230, 255),
                     (cx - w // 2, cy - h // 4, w, h // 2))
    bw = w // 4
    for i in range(4):
        bx = cx - w // 2 + i * bw
        pygame.draw.ellipse(surf, (200, 230, 255),
                            (bx, cy + h // 4, bw, h // 5))
    pygame.draw.circle(surf, NEAR_BLACK,
                       (cx - w // 4, cy - h // 12), 2 * SCALE)
    pygame.draw.circle(surf, NEAR_BLACK,
                       (cx + w // 4, cy - h // 12), 2 * SCALE)


def icon_grow(surf, cx, cy, r):
    cap_w = int(r * 1.2)
    cap_h = int(r * 0.7)
    pygame.draw.ellipse(surf, (125, 30, 45),
                        (cx - cap_w // 2, cy - cap_h - 1 * SCALE,
                         cap_w, cap_h * 2))
    stem_w = int(r * 0.5)
    stem_h = int(r * 0.6)
    pygame.draw.rect(surf, (245, 230, 200),
                     (cx - stem_w // 2, cy + 2 * SCALE, stem_w, stem_h))
    for dx, dy in [(-cap_w // 4, -cap_h // 3),
                   (0, -cap_h // 4),
                   (cap_w // 5, -cap_h // 3)]:
        pygame.draw.circle(surf, (255, 235, 175),
                           (cx + dx, cy + dy), 2 * SCALE)


def icon_surprise(surf, cx, cy, r):
    w = int(r * 1.2)
    h = int(r * 1.1)
    box = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    pygame.draw.rect(surf, PANEL_LIGHTER, box, border_radius=2 * SCALE)
    pygame.draw.rect(surf, GOLD_BRIGHT, box, width=1 * SCALE,
                     border_radius=2 * SCALE)
    pygame.draw.rect(surf, SCARLET_TOP,
                     (cx - 2 * SCALE, box.y, 4 * SCALE, box.h))
    qf = font(20, True).render("?", True, GOLD_BRIGHT)
    surf.blit(qf, qf.get_rect(center=(cx + 8 * SCALE, cy)))


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 1 — MAIN MENU (Pip Scarlet)
# ─────────────────────────────────────────────────────────────────────────────
def screen_main():
    s = pygame.Surface((W, H))
    backdrop(s)
    big_title(s, "SKYBIT", (W // 2, 130 * SCALE), size=74)
    subtitle(s, "POCKET  SKY  FLYER", (W // 2, 190 * SCALE), size=22)
    divider(s, 216 * SCALE, width=140)

    primary_y = 296 * SCALE
    pitch = 70 * SCALE
    pill(s, (W // 2, primary_y), "TAP TO START",
         size=23, min_w=246, h=54, primary=True)
    pill(s, (W // 2, primary_y + pitch), "HOW TO PLAY",
         size=20, min_w=234, h=46)
    pill(s, (W // 2, primary_y + 2 * pitch), "POWER-UPS",
         size=20, min_w=234, h=46)

    # BEST + TOP 10
    panel_w = 144 * SCALE
    gap = 12 * SCALE
    total = panel_w * 2 + gap
    left_x = (W - total) // 2
    cy = H - 88 * SCALE
    score_panel(s,
                pygame.Rect(left_x, cy - 26 * SCALE, panel_w, 52 * SCALE),
                "B E S T", "42")
    # TOP 10 panel — same as score_panel but renders the trophy instead
    tr = pygame.Rect(left_x + panel_w + gap, cy - 26 * SCALE,
                     panel_w, 52 * SCALE)
    card(s, tr)
    lf = font(12, False).render("T O P  10", True, GOLD_MUTED)
    lf.set_alpha(220)
    s.blit(lf, lf.get_rect(center=(tr.centerx, tr.y + 14 * SCALE)))
    draw_trophy(s, tr.centerx, tr.y + 36 * SCALE, 10 * SCALE)

    save("v3_scarlet_main.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 2 — PAUSE
# ─────────────────────────────────────────────────────────────────────────────
def screen_pause():
    s = pygame.Surface((W, H))
    backdrop(s, dim=100)

    # Live score emblem at top — circular medallion replaces the
    # rectangular block that read as plain.
    score_emblem(s, W // 2, 118 * SCALE, 56 * SCALE,
                 "S C O R E", "12")

    big_title(s, "PAUSED", (W // 2, 220 * SCALE), size=64)
    subtitle(s, "T A K E   A   B R E A T H",
             (W // 2, 268 * SCALE), size=13)
    divider(s, 290 * SCALE, width=110)

    primary_y = 372 * SCALE
    pitch = 64 * SCALE
    pill(s, (W // 2, primary_y), "RESUME",
         size=23, min_w=240, h=52, primary=True)
    pill(s, (W // 2, primary_y + pitch), "RESTART RUN",
         size=18, min_w=230, h=44)
    pill(s, (W // 2, primary_y + 2 * pitch), "MAIN MENU",
         size=18, min_w=230, h=44)

    hint = font(11, True).render("TAP  ·  P  ·  ESC", True, GOLD_MUTED)
    hint.set_alpha(180)
    s.blit(hint, hint.get_rect(center=(W // 2, H - 32 * SCALE)))

    save("v3_scarlet_pause.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 3 — RUN SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
def screen_stats():
    s = pygame.Surface((W, H))
    backdrop(s)

    big_title(s, "RUN  SUMMARY", (W // 2, 70 * SCALE), size=36)
    divider(s, 100 * SCALE, width=140)

    # Hero score emblem — gold medallion with scarlet accent + ribbon
    score_emblem(s, W // 2, 200 * SCALE, 78 * SCALE,
                 "S C O R E", "23", with_ribbon=True)

    # 5-row stats card
    rows = [
        ("TIME  ALIVE",     "1 : 27"),
        ("COINS",           "11"),
        ("PILLARS  CLEARED", "23"),
        ("POWER-UPS",       "3"),
        ("NEAR  MISSES",    "3"),
    ]
    card_rect = pygame.Rect(36 * SCALE, 268 * SCALE,
                            W - 72 * SCALE, 230 * SCALE)
    card(s, card_rect)
    row_h = card_rect.h // len(rows)
    for i, (label, value) in enumerate(rows):
        rcy = card_rect.y + i * row_h + row_h // 2
        if i > 0:
            pygame.draw.line(s, (*GOLD_BRIGHT, 50),
                             (card_rect.x + 14 * SCALE,
                              card_rect.y + i * row_h),
                             (card_rect.right - 14 * SCALE,
                              card_rect.y + i * row_h),
                             1 * SCALE)
        lf = font(13, True).render(label, True, GOLD_MUTED)
        s.blit(lf, (card_rect.x + 18 * SCALE,
                    rcy - lf.get_height() // 2))
        vf = font(16, True).render(value, True, GOLD_BRIGHT)
        s.blit(vf, (card_rect.right - 18 * SCALE - vf.get_width(),
                    rcy - vf.get_height() // 2))

    pill(s, (W // 2, H - 80 * SCALE), "TAP  TO  CONTINUE",
         size=22, min_w=246, h=50, primary=True)

    save("v3_scarlet_stats.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 4 — GAME OVER (NEW BEST)
# ─────────────────────────────────────────────────────────────────────────────
def screen_gameover():
    s = pygame.Surface((W, H))
    backdrop(s, dim=70)

    big_title(s, "GAME  OVER", (W // 2, 90 * SCALE), size=44)
    ribbon_banner(s, W // 2, 156 * SCALE, "NEW  BEST !", w=170)

    # Hero score emblem with gold sparkle burst around it
    emblem_cx, emblem_cy, emblem_r = W // 2, 290 * SCALE, 80 * SCALE
    for i in range(20):
        ang = i * (2 * math.pi / 20) + math.pi / 20
        d = emblem_r + 35 * SCALE
        ex = emblem_cx + math.cos(ang) * d
        ey = emblem_cy + math.sin(ang) * d
        for dx, dy in [(0, -4 * SCALE), (4 * SCALE, 0),
                       (0, 4 * SCALE), (-4 * SCALE, 0)]:
            pygame.draw.line(s, GOLD_BRIGHT, (ex, ey), (ex + dx, ey + dy),
                             1 * SCALE)
        pygame.draw.circle(s, GOLD_BRIGHT, (int(ex), int(ey)), 1 * SCALE)

    score_emblem(s, emblem_cx, emblem_cy, emblem_r,
                 "S C O R E", "23")

    pill(s, (W // 2, 446 * SCALE), "TAP  TO  RETRY",
         size=23, min_w=246, h=54, primary=True)
    pill(s, (W // 2, 514 * SCALE), "MAIN  MENU",
         size=19, min_w=234, h=46)

    save("v3_scarlet_gameover.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 5 — NAME ENTRY
# ─────────────────────────────────────────────────────────────────────────────
def screen_name_entry():
    s = pygame.Surface((W, H))
    backdrop(s, dim=50)

    # Trophy with halo at top
    tcx, tcy = W // 2, 110 * SCALE
    halo = pygame.Surface((140 * SCALE, 140 * SCALE), pygame.SRCALPHA)
    for r in range(60 * SCALE, 0, -2 * SCALE):
        a = int(35 * (1 - r / (60 * SCALE)))
        pygame.draw.circle(halo, (255, 220, 130, a),
                           (70 * SCALE, 70 * SCALE), r)
    s.blit(halo, (tcx - 70 * SCALE, tcy - 70 * SCALE))
    draw_trophy(s, tcx, tcy, 22 * SCALE)

    big_title(s, "YOU  MADE  IT !", (W // 2, 220 * SCALE), size=30)
    subtitle(s, "E N T E R   Y O U R   N A M E",
             (W // 2, 264 * SCALE), size=14)
    divider(s, 288 * SCALE, width=90)

    plate = pygame.Rect(W // 2 - 142 * SCALE, 322 * SCALE,
                        284 * SCALE, 64 * SCALE)
    nameplate(s, plate, sample_text="PIP")

    pill(s, (W // 2, 446 * SCALE), "SUBMIT",
         size=22, min_w=240, h=52, primary=True)
    pill(s, (W // 2, 512 * SCALE), "SKIP",
         size=19, min_w=240, h=46)

    save("v3_scarlet_name_entry.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 6 — LEADERBOARD
# ─────────────────────────────────────────────────────────────────────────────
def screen_leaderboard():
    s = pygame.Surface((W, H))
    backdrop(s, dim=40)

    big_title(s, "TOP  10", (W // 2, 70 * SCALE), size=42)
    for side in (-1, 1):
        tx = W // 2 + side * 110 * SCALE
        draw_trophy(s, tx, 70 * SCALE, 16 * SCALE)
    divider(s, 112 * SCALE, width=90)

    entries = [
        ("Hawkins",   148, False),
        ("Garrick",   132, False),
        ("Atticus",   117, False),
        ("Mira",      104, False),
        ("Quill",      96, False),
        ("Bo",         83, False),
        ("Pip",        42, True),  # player row
        ("Wren",       38, False),
        ("Stilt",      29, False),
        ("Cinder",     18, False),
    ]

    list_top = 160 * SCALE
    list_bot = H - 56 * SCALE
    row_h = (list_bot - list_top) // len(entries)
    for i, (name, score, is_player) in enumerate(entries):
        rect = pygame.Rect(28 * SCALE,
                           list_top + i * row_h + 2 * SCALE,
                           W - 56 * SCALE, row_h - 4 * SCALE)
        if is_player:
            # Subtle scarlet glow halo behind the row
            glow = pygame.Surface((rect.w + 12 * SCALE,
                                   rect.h + 12 * SCALE),
                                  pygame.SRCALPHA)
            for k in range(6 * SCALE, 0, -SCALE):
                a = int(40 * k / (6 * SCALE))
                pygame.draw.rect(glow, (*SCARLET_TOP, a // 4),
                                 (6 * SCALE - k, 6 * SCALE - k,
                                  rect.w + k * 2, rect.h + k * 2),
                                 border_radius=10 * SCALE)
            s.blit(glow, (rect.x - 6 * SCALE, rect.y - 6 * SCALE))
            # Thicker gold border + scarlet underlay
            pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(pnl, (*PANEL_DARK, 240),
                             (0, 0, rect.w, rect.h),
                             border_radius=10 * SCALE)
            pygame.draw.rect(pnl, GOLD_BRIGHT,
                             (0, 0, rect.w, rect.h),
                             width=3 * SCALE, border_radius=10 * SCALE)
            pygame.draw.line(pnl, (*GOLD_BRIGHT, 140),
                             (10 * SCALE, 4 * SCALE),
                             (rect.w - 10 * SCALE, 4 * SCALE), 1 * SCALE)
            s.blit(pnl, rect.topleft)
        else:
            card(s, rect, border_alpha=110, accent_alpha=80)

        # Rank badge
        rcx = rect.x + rect.h // 2 + 4 * SCALE
        rcy = rect.centery
        rank = i + 1
        if rank <= 3:
            if rank == 1:
                ring, interior = GOLD_BRIGHT, lerp(GOLD_BRIGHT, NEAR_BLACK, 0.7)
            elif rank == 2:
                ring, interior = SILVER, lerp(SILVER, NEAR_BLACK, 0.75)
            else:
                ring, interior = BRONZE, lerp(BRONZE, NEAR_BLACK, 0.75)
            br = rect.h // 2 - 6 * SCALE
            pygame.draw.circle(s, interior, (rcx, rcy), br)
            pygame.draw.circle(s, ring, (rcx, rcy), br, 2 * SCALE)
            for ang_deg in range(0, 360, 30):
                a = math.radians(ang_deg)
                x1 = rcx + math.cos(a) * (br - 3 * SCALE)
                y1 = rcy + math.sin(a) * (br - 3 * SCALE)
                x2 = rcx + math.cos(a) * (br - 1 * SCALE)
                y2 = rcy + math.sin(a) * (br - 1 * SCALE)
                pygame.draw.line(s, ring, (x1, y1), (x2, y2), 1 * SCALE)
            rf = font(14, True).render(str(rank), True, ring)
            s.blit(rf, rf.get_rect(center=(rcx, rcy)))
        else:
            br = rect.h // 2 - 7 * SCALE
            pygame.draw.circle(s, PANEL_LIGHTER, (rcx, rcy), br)
            pygame.draw.circle(s, GOLD_BRIGHT, (rcx, rcy), br, 1 * SCALE)
            rf = font(13, True).render(str(rank), True, GOLD_BRIGHT)
            s.blit(rf, rf.get_rect(center=(rcx, rcy)))

        # Name
        name_color = GOLD_BRIGHT if is_player else CREAM
        nf = font(14, True).render(name, True, name_color)
        nr = nf.get_rect(midleft=(rcx + rect.h // 2 + 4 * SCALE, rcy))
        s.blit(nf, nr)

        # YOU tag for player row
        if is_player:
            tag_w = 36 * SCALE
            tag_h = 16 * SCALE
            tag_rect = pygame.Rect(
                nr.right + 8 * SCALE, rcy - tag_h // 2,
                tag_w, tag_h)
            pygame.draw.rect(s, SCARLET_TOP, tag_rect,
                             border_radius=tag_h // 2)
            pygame.draw.rect(s, GOLD_BRIGHT, tag_rect,
                             width=1 * SCALE,
                             border_radius=tag_h // 2)
            tt = font(9, True).render("YOU", True, CREAM)
            s.blit(tt, tt.get_rect(center=tag_rect.center))

        # Score right
        sf = font(16, True).render(str(score), True, GOLD_BRIGHT)
        s.blit(sf, sf.get_rect(midright=(rect.right - 16 * SCALE, rcy)))

    hint = font(11, True).render("TAP  TO  MENU", True, GOLD_MUTED)
    hint.set_alpha(200)
    s.blit(hint, hint.get_rect(center=(W // 2, H - 30 * SCALE)))

    save("v3_scarlet_leaderboard.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 7 — POWER-UPS HELP
# ─────────────────────────────────────────────────────────────────────────────
def screen_powerups():
    s = pygame.Surface((W, H))
    backdrop(s, dim=40)

    big_title(s, "POWER-UPS", (W // 2, 66 * SCALE), size=36)
    subtitle(s, "C O L L E C T   T O   B O O S T",
             (W // 2, 106 * SCALE), size=11)
    divider(s, 124 * SCALE, width=80)

    items = [
        ("TRIPLE",  "3x  COIN  VALUE",  icon_triple),
        ("MAGNET",  "PULL  NEARBY  $",  icon_magnet),
        ("SLOW-MO", "TIME  SLOWS",      icon_slowmo),
        ("KFC",     "FAT-PIPE  GAPS",   icon_kfc),
        ("GHOST",   "PASS  THROUGH",    icon_ghost),
        ("GROW",    "BIG  BIRD",        icon_grow),
    ]
    cols = 2
    cell_w = (W - 56 * SCALE) // cols - 8 * SCALE
    cell_h = 104 * SCALE
    cell_gap_x = 12 * SCALE
    cell_gap_y = 10 * SCALE
    grid_top = 144 * SCALE
    grid_left = 28 * SCALE
    for i, (name, desc, icon_fn) in enumerate(items):
        col = i % cols
        row = i // cols
        x = grid_left + col * (cell_w + cell_gap_x)
        y = grid_top + row * (cell_h + cell_gap_y)
        rect = pygame.Rect(x, y, cell_w, cell_h)
        card(s, rect, border_alpha=160)
        icx = rect.centerx
        icy = rect.y + 32 * SCALE
        pygame.draw.circle(s, PANEL_LIGHTER, (icx, icy), 22 * SCALE)
        pygame.draw.circle(s, GOLD_BRIGHT, (icx, icy), 22 * SCALE, 2 * SCALE)
        icon_fn(s, icx, icy, 18 * SCALE)
        nf = font(13, True).render(name, True, GOLD_BRIGHT)
        s.blit(nf, nf.get_rect(center=(rect.centerx, rect.y + 68 * SCALE)))
        df = font(10, True).render(desc, True, GOLD_MUTED)
        s.blit(df, df.get_rect(center=(rect.centerx, rect.y + 88 * SCALE)))

    sb_y = grid_top + 3 * (cell_h + cell_gap_y) + 2 * SCALE
    sb_rect = pygame.Rect(28 * SCALE, sb_y, W - 56 * SCALE, 56 * SCALE)
    card(s, sb_rect, border_alpha=180)
    icon_surprise(s, sb_rect.x + 28 * SCALE, sb_rect.centery, 16 * SCALE)
    nf = font(13, True).render("SURPRISE  BOX", True, GOLD_BRIGHT)
    s.blit(nf, (sb_rect.x + 60 * SCALE,
                sb_rect.centery - 11 * SCALE))
    df = font(10, True).render("RANDOM  ·  ANY  OF  THE  ABOVE",
                               True, GOLD_MUTED)
    s.blit(df, (sb_rect.x + 60 * SCALE,
                sb_rect.centery + 4 * SCALE))

    ribbon_banner(s, W // 2, sb_y + 80 * SCALE,
                  "EFFECTS  LAST  8  SECONDS", w=200)

    save("v3_scarlet_powerups.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 8 — HOW TO PLAY
# ─────────────────────────────────────────────────────────────────────────────
def screen_intro():
    s = pygame.Surface((W, H))
    backdrop(s)

    big_title(s, "HOW  TO  PLAY", (W // 2, 110 * SCALE), size=38)
    divider(s, 150 * SCALE, width=90)

    steps = [
        ("1", "FLAP",    "TAP  ·  CLICK  ·  SPACE"),
        ("2", "THREAD",  "AVOID  THE  PILLARS"),
        ("3", "COLLECT", "COINS  &  POWER-UPS"),
    ]
    card_top = 200 * SCALE
    card_h = 88 * SCALE
    card_gap = 14 * SCALE
    for i, (num, head, body) in enumerate(steps):
        rect = pygame.Rect(40 * SCALE,
                           card_top + i * (card_h + card_gap),
                           W - 80 * SCALE, card_h)
        card(s, rect, border_alpha=180)
        # Number badge on the left — scarlet body + gold rim
        ncx = rect.x + 38 * SCALE
        ncy = rect.centery
        nb_r = 24 * SCALE
        pygame.draw.circle(s, SCARLET_BOT, (ncx, ncy), nb_r)
        # Subtle inner highlight on a separate surface so alpha blends
        hl = pygame.Surface((nb_r * 2, nb_r * 2), pygame.SRCALPHA)
        for k in range(nb_r - 4, 0, -2):
            a = int(40 * (1 - k / (nb_r - 4)))
            pygame.draw.circle(hl, (255, 200, 160, a),
                               (nb_r, nb_r - 4), k)
        s.blit(hl, (ncx - nb_r, ncy - nb_r))
        pygame.draw.circle(s, GOLD_BRIGHT, (ncx, ncy), nb_r, 2 * SCALE)
        nf = font(22, True).render(num, True, CREAM)
        sh = font(22, True).render(num, True, NEAR_BLACK)
        sh.set_alpha(180)
        nr = nf.get_rect(center=(ncx, ncy))
        s.blit(sh, (nr.x + 1 * SCALE, nr.y + 2 * SCALE))
        s.blit(nf, nr)
        # Head
        hf = font(18, True).render(head, True, GOLD_BRIGHT)
        s.blit(hf, (rect.x + 80 * SCALE, rect.y + 22 * SCALE))
        # Body
        bf = font(13, True).render(body, True, CREAM)
        s.blit(bf, (rect.x + 80 * SCALE, rect.y + 52 * SCALE))

    pill(s, (W // 2, H - 84 * SCALE), "TAP  TO  BEGIN",
         size=22, min_w=246, h=52, primary=True)

    save("v3_scarlet_intro.png", s)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Generating Pip Scarlet UI set at {W}x{H}...")
    screen_main()
    screen_pause()
    screen_stats()
    screen_gameover()
    screen_name_entry()
    screen_leaderboard()
    screen_powerups()
    screen_intro()
    print("Done.")
