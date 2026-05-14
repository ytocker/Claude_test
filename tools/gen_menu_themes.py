"""Generate v4 menu redesign mockups — 5 candidate themes.

Each mockup is a 360x640 PNG matching the game's window size. The
content is functionally identical to v3 (TAP TO START / HOW TO PLAY /
POWER-UPS pills + BEST + TOP 10 panels + title) so the user can
compare the *visual treatment* head-to-head and pick one for the
actual redesign.
"""
import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()
pygame.display.set_mode((1, 1))  # off-screen ctx; we draw to SRCALPHA surfaces

W, H = 360, 640
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "menu_redesign_v4")
os.makedirs(OUT, exist_ok=True)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "game", "assets")
FONT_BOLD = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")
FONT_REG  = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")


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


def stroked_text(surf, txt, center, size, fill, outline, px=2, shadow=(2, 3), shadow_alpha=170, bold=True):
    f = font(size, bold)
    img = f.render(txt, True, fill)
    out = f.render(txt, True, outline)
    r = img.get_rect(center=center)
    for ox in range(-px, px + 1):
        for oy in range(-px, px + 1):
            if ox or oy:
                surf.blit(out, (r.x + ox, r.y + oy))
    if shadow:
        sh = f.render(txt, True, (0, 0, 0))
        sh.set_alpha(shadow_alpha)
        surf.blit(sh, (r.x + shadow[0], r.y + shadow[1]))
    surf.blit(img, r.topleft)
    return r


def glow_text(surf, txt, center, size, color, glow_color, glow_radius=6, bold=True):
    f = font(size, bold)
    img = f.render(txt, True, color)
    r = img.get_rect(center=center)
    # Build a glow layer
    glow = pygame.Surface((img.get_width() + glow_radius * 4, img.get_height() + glow_radius * 4), pygame.SRCALPHA)
    g_text = f.render(txt, True, glow_color)
    for dx in range(-glow_radius, glow_radius + 1, 2):
        for dy in range(-glow_radius, glow_radius + 1, 2):
            if dx * dx + dy * dy <= glow_radius * glow_radius:
                tmp = g_text.copy()
                tmp.set_alpha(40)
                glow.blit(tmp, (glow_radius * 2 + dx, glow_radius * 2 + dy))
    surf.blit(glow, (r.x - glow_radius * 2, r.y - glow_radius * 2), special_flags=pygame.BLEND_PREMULTIPLIED)
    surf.blit(img, r.topleft)
    return r


def save(name, surf):
    out = os.path.join(OUT, name)
    pygame.image.save(surf, out)
    print(f"  wrote {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Theme 1: NEON ARCADE (cyberpunk synthwave)
# ─────────────────────────────────────────────────────────────────────────────
def theme_neon_arcade():
    s = pygame.Surface((W, H))
    # Deep purple to magenta gradient
    gradient_v(s, (8, 4, 28), (40, 6, 56))

    # Horizontal sun behind the grid
    sun = pygame.Surface((W, H), pygame.SRCALPHA)
    sx, sy, sr = W // 2, 280, 110
    for i in range(sr, 0, -2):
        a = max(0, 220 - int(220 * (i / sr)))
        c = lerp((255, 70, 130), (255, 210, 60), 1 - i / sr)
        pygame.draw.circle(sun, (*c, a), (sx, sy), i)
    s.blit(sun, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)

    # Sun stripes (retrowave horizontal cut-outs)
    for i in range(6):
        y = sy + 30 + i * 14
        a = 200 - i * 25
        pygame.draw.rect(s, (8, 4, 28), (sx - sr, y, sr * 2, 4))

    # Synthwave grid floor
    horizon = 360
    for i in range(0, 16):
        y = horizon + i * (i + 1) * 1.3
        if y >= H: break
        alpha = max(30, 180 - i * 14)
        line = pygame.Surface((W, 2), pygame.SRCALPHA)
        line.fill((255, 60, 200, alpha))
        s.blit(line, (0, int(y)))
    # Vertical grid lines converging at center
    vp_x, vp_y = W // 2, horizon
    for col in range(-7, 8):
        x_bot = vp_x + col * 80
        a = max(40, 180 - abs(col) * 18)
        pygame.draw.aaline(s, (255, 60, 200, a), (vp_x, vp_y), (x_bot, H))

    # Sparse stars (cyan dots)
    random.seed(7)
    for _ in range(28):
        x = random.randint(0, W - 1)
        y = random.randint(0, 280)
        r = random.choice([1, 1, 2])
        pygame.draw.circle(s, (180, 230, 255), (x, y), r)

    # Cloud silhouettes (dark pink wisps)
    for cx, cy, cw in [(60, 100, 80), (250, 60, 100), (320, 160, 70)]:
        pygame.draw.ellipse(s, (60, 12, 70), (cx - cw // 2, cy - 14, cw, 28))

    # ── Title ── hot pink with cyan glow
    title_overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    # cyan glow halo
    for r in range(28, 0, -4):
        a = int(60 * r / 28)
        f = font(72, True)
        g = f.render("SKYBIT", True, (60, 220, 255))
        rect = g.get_rect(center=(W // 2 + r * 0, 130))
        g.set_alpha(a)
        for dx, dy in [(-r, 0), (r, 0), (0, -r), (0, r)]:
            title_overlay.blit(g, (rect.x + dx, rect.y + dy))
    s.blit(title_overlay, (0, 0))
    stroked_text(s, "SKYBIT", (W // 2, 130), 72,
                 fill=(255, 70, 170), outline=(120, 10, 80), px=2, shadow=(3, 4))
    # Subtitle with cyan
    sub = font(18, True).render("POCKET  SKY  FLYER", True, (110, 230, 255))
    sr = sub.get_rect(center=(W // 2, 184))
    s.blit(sub, sr)
    # Pink underline
    pygame.draw.line(s, (255, 70, 170), (W // 2 - 80, 204), (W // 2 + 80, 204), 2)

    # ── Buttons (3 neon pills) ──
    def neon_pill(center, text, accent, sz=22, w=240, h=52):
        pill = pygame.Surface((w + 24, h + 24), pygame.SRCALPHA)
        # Outer glow
        for i in range(10, 0, -2):
            a = int(110 * (i / 10))
            pygame.draw.rect(pill, (*accent, a), (12 - i, 12 - i, w + i * 2, h + i * 2), border_radius=h // 2 + i)
        # Body
        pygame.draw.rect(pill, (16, 6, 38, 240), (12, 12, w, h), border_radius=h // 2)
        # Inner stroke
        pygame.draw.rect(pill, (*accent, 230), (12, 12, w, h), width=2, border_radius=h // 2)
        # Inside highlight
        pygame.draw.line(pill, (*accent, 110), (24, 16), (w, 16))
        # Text
        tf = font(sz, True)
        ti = tf.render(text, True, (240, 250, 255))
        s.blit(pill, (center[0] - pill.get_width() // 2, center[1] - pill.get_height() // 2))
        tr = ti.get_rect(center=center)
        s.blit(ti, tr)

    neon_pill((W // 2, 360), "TAP TO START", (255, 70, 170), 22, 240, 54)
    neon_pill((W // 2, 425), "HOW TO PLAY",  (90, 220, 255), 18, 240, 46)
    neon_pill((W // 2, 482), "POWER-UPS",    (180, 110, 255), 18, 240, 46)

    # ── BEST + TOP 10 panels with corner brackets ──
    def neon_panel(x, y, w, h, accent, label, value):
        pygame.draw.rect(s, (10, 4, 30), (x, y, w, h), border_radius=10)
        pygame.draw.rect(s, accent, (x, y, w, h), width=1, border_radius=10)
        # Corner brackets
        L = 10
        for cx, cy, dx, dy in [(x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)]:
            pygame.draw.line(s, accent, (cx, cy), (cx + L * dx, cy), 2)
            pygame.draw.line(s, accent, (cx, cy), (cx, cy + L * dy), 2)
        lf = font(11, False).render(label, True, lerp(accent, (255, 255, 255), 0.3))
        s.blit(lf, lf.get_rect(center=(x + w // 2, y + 14)))
        vf = font(22, True).render(value, True, accent)
        s.blit(vf, vf.get_rect(center=(x + w // 2, y + 34)))

    neon_panel(50, H - 110, 124, 52, (90, 220, 255), "B E S T", "42")
    # TOP 10 with trophy
    px_, py_ = 186, H - 110
    pygame.draw.rect(s, (10, 4, 30), (px_, py_, 124, 52), border_radius=10)
    pygame.draw.rect(s, (255, 70, 170), (px_, py_, 124, 52), width=1, border_radius=10)
    L = 10
    for cx, cy, dx, dy in [(px_, py_, 1, 1), (px_ + 124, py_, -1, 1), (px_, py_ + 52, 1, -1), (px_ + 124, py_ + 52, -1, -1)]:
        pygame.draw.line(s, (255, 70, 170), (cx, cy), (cx + L * dx, cy), 2)
        pygame.draw.line(s, (255, 70, 170), (cx, cy), (cx, cy + L * dy), 2)
    lf = font(11, False).render("T O P  10", True, (255, 160, 220))
    s.blit(lf, lf.get_rect(center=(px_ + 62, py_ + 14)))
    # Pixel trophy in pink
    tcx, tcy = px_ + 62, py_ + 36
    pygame.draw.rect(s, (255, 200, 80), (tcx - 8, tcy - 6, 16, 10))
    pygame.draw.rect(s, (255, 200, 80), (tcx - 2, tcy + 4, 4, 6))
    pygame.draw.rect(s, (255, 200, 80), (tcx - 7, tcy + 10, 14, 3))

    # Scanlines overlay
    sl = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(0, H, 3):
        pygame.draw.line(sl, (255, 255, 255, 8), (0, y), (W, y))
    s.blit(sl, (0, 0))

    save("theme1_neon_arcade.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# Theme 2: STORYBOOK PAPERCRAFT
# ─────────────────────────────────────────────────────────────────────────────
def theme_storybook():
    s = pygame.Surface((W, H))
    # Cream parchment gradient
    gradient_v(s, (252, 240, 210), (240, 220, 178))

    # Paper noise texture
    random.seed(3)
    for _ in range(2500):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        c = random.randint(180, 230)
        if random.random() < 0.15:
            pygame.draw.circle(s, (c, c - 20, c - 50), (x, y), 1)
    # Vignette
    vig = pygame.Surface((W, H), pygame.SRCALPHA)
    for r in range(0, 240, 12):
        a = int(60 * (r / 240))
        pygame.draw.rect(vig, (110, 60, 20, a), (r, r, W - r * 2, H - r * 2), width=1)
    s.blit(vig, (0, 0))

    # Watercolor cloud (light blue wash)
    for cx, cy, cw, ch in [(W // 2, 90, 260, 90), (80, 240, 140, 50)]:
        wc = pygame.Surface((cw, ch), pygame.SRCALPHA)
        for r in range(min(cw, ch) // 2, 0, -2):
            a = int(40 * (1 - r / (min(cw, ch) / 2)))
            pygame.draw.ellipse(wc, (130, 180, 220, a), (cw // 2 - r, ch // 2 - r // 2, r * 2, r))
        s.blit(wc, (cx - cw // 2, cy - ch // 2))

    # Hand-drawn sketch mountains at bottom
    for pts, fill in [
        ([(0, 560), (40, 500), (90, 530), (140, 460), (200, 510), (260, 470), (320, 530), (360, 510), (360, 640), (0, 640)], (170, 145, 110)),
        ([(0, 605), (50, 580), (100, 600), (160, 575), (220, 590), (280, 570), (360, 595), (360, 640), (0, 640)], (130, 100, 70)),
    ]:
        pygame.draw.polygon(s, fill, pts)
        # Pencil sketch outline
        for i in range(len(pts) - 2):
            pygame.draw.line(s, (90, 60, 30), pts[i], pts[i + 1], 2)

    # Hand-drawn doodle stars
    for cx, cy, sz in [(60, 150, 6), (300, 110, 8), (40, 280, 5), (310, 250, 7)]:
        for k in range(5):
            a = k * 2 * math.pi / 5 - math.pi / 2
            x1 = cx + math.cos(a) * sz
            y1 = cy + math.sin(a) * sz
            x2 = cx + math.cos(a + 2 * math.pi / 5) * sz
            y2 = cy + math.sin(a + 2 * math.pi / 5) * sz
            pygame.draw.line(s, (180, 120, 40), (x1, y1), (x2, y2), 2)

    # ── Title — ink-style with watercolor accent ──
    # Watercolor splotch behind
    wb = pygame.Surface((280, 90), pygame.SRCALPHA)
    for r in range(140, 20, -10):
        a = int(60 * (1 - r / 140))
        pygame.draw.ellipse(wb, (220, 130, 80, a), (140 - r, 45 - r // 3, r * 2, (r * 2) // 3))
    s.blit(wb, (W // 2 - 140, 90))
    stroked_text(s, "Skybit", (W // 2, 130), 68,
                 fill=(70, 38, 20), outline=(150, 90, 40), px=1, shadow=(2, 3), shadow_alpha=80, bold=True)
    # Sub-line with washi tape effect
    tape_w = 220
    tape = pygame.Surface((tape_w, 28), pygame.SRCALPHA)
    pygame.draw.rect(tape, (220, 170, 110, 200), (0, 0, tape_w, 28))
    # tape stripes
    for x in range(0, tape_w, 10):
        pygame.draw.line(tape, (180, 130, 70, 100), (x, 0), (x, 28), 1)
    s.blit(tape, (W // 2 - tape_w // 2, 178))
    sub = font(16, True).render("POCKET  SKY  FLYER", True, (80, 45, 20))
    s.blit(sub, sub.get_rect(center=(W // 2, 192)))

    # ── Buttons — card-like with stitched border ──
    def card_btn(center, text, fill_c, sz=20, w=240, h=54):
        b = pygame.Surface((w + 18, h + 18), pygame.SRCALPHA)
        # Drop shadow
        pygame.draw.rect(b, (60, 30, 10, 80), (12, 14, w, h), border_radius=8)
        # Card body
        pygame.draw.rect(b, fill_c, (8, 8, w, h), border_radius=8)
        # Darker outline
        pygame.draw.rect(b, (90, 55, 25), (8, 8, w, h), width=2, border_radius=8)
        # Stitched dashed inner border
        for x in range(14, w + 2, 8):
            pygame.draw.line(b, (250, 245, 220), (x, 14), (x + 4, 14), 2)
            pygame.draw.line(b, (250, 245, 220), (x, 8 + h - 6), (x + 4, 8 + h - 6), 2)
        for y in range(14, h + 2, 8):
            pygame.draw.line(b, (250, 245, 220), (14, y), (14, y + 4), 2)
            pygame.draw.line(b, (250, 245, 220), (8 + w - 6, y), (8 + w - 6, y + 4), 2)
        s.blit(b, (center[0] - b.get_width() // 2, center[1] - b.get_height() // 2))
        ti = font(sz, True).render(text, True, (252, 246, 220))
        s.blit(ti, ti.get_rect(center=center))

    card_btn((W // 2, 350), "TAP TO START", (200, 110, 50), 22, 240, 56)
    card_btn((W // 2, 420), "HOW TO PLAY",  (130, 85, 45),  18, 240, 48)
    card_btn((W // 2, 480), "POWER-UPS",    (160, 95, 45),  18, 240, 48)

    # ── BEST + TOP 10 — paper tickets ──
    def ticket(x, y, w, h, label, value, fill=(244, 220, 165), stroke=(140, 95, 50)):
        # Perforations along left edge
        pygame.draw.rect(s, fill, (x, y, w, h), border_radius=8)
        pygame.draw.rect(s, stroke, (x, y, w, h), width=2, border_radius=8)
        for yy in range(y + 6, y + h, 8):
            pygame.draw.circle(s, (232, 200, 140), (x + 8, yy), 2)
        lf = font(11, False).render(label, True, (110, 70, 30))
        s.blit(lf, lf.get_rect(center=(x + w // 2 + 4, y + 12)))
        vf = font(22, True).render(value, True, (80, 40, 10))
        s.blit(vf, vf.get_rect(center=(x + w // 2 + 4, y + 34)))

    ticket(50, H - 110, 124, 52, "B E S T", "42")
    # TOP 10 ticket with hand-drawn trophy
    ticket(186, H - 110, 124, 52, "T O P  10", "")
    # mini ink trophy
    tcx, tcy = 186 + 62 + 2, H - 110 + 36
    pygame.draw.polygon(s, (200, 160, 70), [(tcx - 9, tcy - 8), (tcx + 9, tcy - 8), (tcx + 7, tcy + 2), (tcx - 7, tcy + 2)])
    pygame.draw.rect(s, (200, 160, 70), (tcx - 2, tcy + 2, 4, 5))
    pygame.draw.rect(s, (200, 160, 70), (tcx - 7, tcy + 7, 14, 3))
    pygame.draw.polygon(s, (90, 55, 25), [(tcx - 9, tcy - 8), (tcx + 9, tcy - 8), (tcx + 7, tcy + 2), (tcx - 7, tcy + 2)], width=1)

    save("theme2_storybook.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# Theme 3: 8-BIT RETRO CRT
# ─────────────────────────────────────────────────────────────────────────────
def theme_retro_crt():
    s = pygame.Surface((W, H))
    # Pure black
    s.fill((6, 6, 14))

    # Faux CRT bezel — rounded rect inset
    bezel_in = pygame.Rect(0, 0, W, H)
    # Inner screen area (we let everything draw inside the full W×H)
    # Outer dark frame
    pygame.draw.rect(s, (16, 16, 30), bezel_in, width=6, border_radius=8)

    # Big "stars" as pixel dots
    random.seed(11)
    for _ in range(60):
        x = random.randint(8, W - 9)
        y = random.randint(8, 280)
        c = random.choice([(255, 255, 255), (200, 230, 255), (160, 160, 200)])
        pygame.draw.rect(s, c, (x, y, 2, 2))

    # Pixel mountain at bottom (NES-style chunky stairs)
    def pix(x, y, w, h, c):
        pygame.draw.rect(s, c, (x, y, w, h))
    # Far ridge
    blocks_far = [(0, 540), (16, 528), (32, 520), (52, 528), (72, 516), (96, 504), (124, 512), (152, 500), (180, 508), (208, 496), (236, 508), (264, 516), (296, 500), (324, 512), (348, 520)]
    for bx, by in blocks_far:
        pix(bx, by, 28, H - by, (40, 32, 80))
    # Near ridge
    near_pts = [(0, 580), (24, 564), (60, 572), (96, 556), (140, 568), (180, 552), (220, 564), (264, 552), (304, 568), (336, 556), (360, 564)]
    for bx, by in near_pts:
        pix(bx, by, 30, H - by, (30, 24, 60))

    # NES-palette title — pixel bricks
    # Block-style "SKYBIT" — render text big and then quantize via downscale
    big = pygame.Surface((W, 110), pygame.SRCALPHA)
    bf = font(80, True)
    fg = bf.render("SKYBIT", True, (250, 100, 80))
    out_red = bf.render("SKYBIT", True, (180, 30, 30))
    fg_rect = fg.get_rect(center=(W // 2, 55))
    # Outer black blocks
    out_black = bf.render("SKYBIT", True, (8, 8, 14))
    for d in [(-3, 0), (3, 0), (0, -3), (0, 3), (-3, -3), (3, -3), (-3, 3), (3, 3)]:
        big.blit(out_black, (fg_rect.x + d[0], fg_rect.y + d[1]))
    for d in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        big.blit(out_red, (fg_rect.x + d[0], fg_rect.y + d[1]))
    big.blit(fg, fg_rect.topleft)
    # Downscale & up-scale for chunky pixel feel
    small = pygame.transform.scale(big, (W // 2, 55))
    chunky = pygame.transform.scale(small, (W, 110))
    s.blit(chunky, (0, 86))

    # Subtitle (mono cyan, blinky tone)
    sub = font(16, True).render("POCKET  SKY  FLYER", True, (100, 220, 220))
    sr = sub.get_rect(center=(W // 2, 200))
    s.blit(sub, sr)

    # Blinking ▶ cursor next to TAP TO START
    def nes_btn(center, text, accent, sz=20, w=240, h=46, selected=False):
        x = center[0] - w // 2
        y = center[1] - h // 2
        # Outer 3-color bevel
        pygame.draw.rect(s, (255, 255, 255), (x, y, w, h))
        pygame.draw.rect(s, (8, 8, 14), (x + 2, y + 2, w - 4, h - 4))
        pygame.draw.rect(s, accent, (x + 4, y + 4, w - 8, h - 8))
        # Inner pixel border
        pygame.draw.rect(s, (8, 8, 14), (x + 4, y + 4, w - 8, h - 8), width=2)
        ti = font(sz, True).render(text, True, (250, 250, 250))
        sh = font(sz, True).render(text, True, (8, 8, 14))
        tr = ti.get_rect(center=center)
        for d in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            s.blit(sh, (tr.x + d[0], tr.y + d[1]))
        s.blit(ti, tr)
        if selected:
            # Pixel arrow on left
            ax = x - 16
            ay = center[1]
            pygame.draw.polygon(s, (250, 200, 60), [(ax, ay - 6), (ax + 10, ay), (ax, ay + 6)])

    nes_btn((W // 2, 280), "TAP TO START", (200, 50, 50), 18, 220, 42, selected=True)
    nes_btn((W // 2, 336), "HOW TO PLAY",  (40, 120, 200), 16, 220, 36)
    nes_btn((W // 2, 388), "POWER-UPS",    (40, 160, 80),  16, 220, 36)

    # "INSERT COIN" blink hint
    ins = font(11, True).render("- PRESS  ANY  KEY  TO  PLAY -", True, (250, 200, 60))
    s.blit(ins, ins.get_rect(center=(W // 2, 432)))

    # ── HUD-bar at bottom in arcade style — score readout ──
    # HiScore left, TOP 10 right, retro-style
    pygame.draw.rect(s, (8, 8, 14), (0, H - 86, W, 64))
    pygame.draw.line(s, (250, 200, 60), (8, H - 86), (W - 8, H - 86), 1)
    pygame.draw.line(s, (250, 200, 60), (8, H - 22),  (W - 8, H - 22),  1)
    hs = font(11, True).render("HI - BEST", True, (250, 200, 60))
    s.blit(hs, (24, H - 76))
    big = font(28, True).render("000042", True, (250, 100, 80))
    s.blit(big, (24, H - 60))
    t = font(11, True).render("TOP - 10", True, (250, 200, 60))
    s.blit(t, t.get_rect(topright=(W - 24, H - 76)))
    # Pixel trophy
    tcx = W - 60
    tcy = H - 44
    for px_, py_ in [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (0, 1), (4, 1), (1, 2), (2, 2), (3, 2), (2, 3), (1, 4), (2, 4), (3, 4)]:
        pygame.draw.rect(s, (250, 200, 60), (tcx + px_ * 3, tcy + py_ * 3, 3, 3))

    # CRT scanlines + curvature glow
    sl = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(0, H, 2):
        pygame.draw.line(sl, (0, 0, 0, 60), (0, y), (W, y))
    s.blit(sl, (0, 0))
    # Slight vignette
    vig = pygame.Surface((W, H), pygame.SRCALPHA)
    for r in range(0, 80, 4):
        a = int(80 * (r / 80))
        pygame.draw.rect(vig, (0, 0, 0, a), (r, r, W - r * 2, H - r * 2), width=2, border_radius=4)
    s.blit(vig, (0, 0))

    save("theme3_retro_crt.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# Theme 4: CRYSTAL AURORA (glassmorphism, premium)
# ─────────────────────────────────────────────────────────────────────────────
def theme_aurora():
    s = pygame.Surface((W, H))
    # Deep midnight to royal blue gradient
    gradient_v(s, (8, 12, 38), (24, 38, 86))

    # Aurora ribbons
    aurora = pygame.Surface((W, H), pygame.SRCALPHA)
    bands = [
        ((30, 240, 180), 130, 60, 0.85),   # green
        ((140, 90, 230), 200, 50, 1.1),   # purple
        ((255, 90, 180), 280, 40, 0.95),  # pink
    ]
    for col, base_y, amp, freq in bands:
        for w_ in range(18, 0, -2):
            pts_top = []
            pts_bot = []
            for x in range(0, W + 1, 4):
                y_off = math.sin((x / W) * math.pi * freq) * amp
                pts_top.append((x, base_y + y_off - w_ * 4))
                pts_bot.append((x, base_y + y_off + w_ * 4))
            pts = pts_top + list(reversed(pts_bot))
            a = max(2, 22 - w_)
            pygame.draw.polygon(aurora, (*col, a), pts)
    s.blit(aurora, (0, 0))

    # Bright stars
    random.seed(5)
    for _ in range(80):
        x = random.randint(0, W - 1)
        y = random.randint(0, 320)
        r = random.choice([1, 1, 1, 2])
        a = random.randint(100, 255)
        pygame.draw.circle(s, (240, 245, 255), (x, y), r)
    # A few "big" sparkle stars with cross
    for cx, cy in [(40, 80), (290, 150), (60, 250), (310, 90), (200, 60)]:
        pygame.draw.circle(s, (240, 250, 255), (cx, cy), 2)
        pygame.draw.line(s, (240, 250, 255, 220), (cx - 4, cy), (cx + 4, cy), 1)
        pygame.draw.line(s, (240, 250, 255, 220), (cx, cy - 4), (cx, cy + 4), 1)

    # Floating particles (soft glow)
    for cx, cy, r in [(70, 320, 14), (290, 380, 10), (40, 460, 8), (320, 500, 12), (140, 410, 6)]:
        ptc = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
        for rr in range(r, 0, -1):
            a = int(40 * (1 - rr / r))
            pygame.draw.circle(ptc, (180, 220, 255, a), (r * 3 // 2, r * 3 // 2), rr)
        s.blit(ptc, (cx - r * 3 // 2, cy - r * 3 // 2))

    # ── Title — frosted, blue-glow ──
    glow_text(s, "SKYBIT", (W // 2, 130), 72,
              color=(245, 250, 255), glow_color=(140, 200, 255), glow_radius=10)
    sub = font(16, True).render("P O C K E T   S K Y   F L Y E R", True, (180, 220, 255))
    s.blit(sub, sub.get_rect(center=(W // 2, 190)))
    # Crystal underline gradient
    line = pygame.Surface((180, 2), pygame.SRCALPHA)
    for x in range(180):
        c = lerp((140, 90, 230), (30, 240, 200), x / 180)
        pygame.draw.line(line, c, (x, 0), (x, 2))
    s.blit(line, line.get_rect(center=(W // 2, 210)))

    # ── Glass buttons ──
    def glass_btn(center, text, sz=22, w=240, h=54, primary=False):
        x = center[0] - w // 2
        y = center[1] - h // 2
        b = pygame.Surface((w, h), pygame.SRCALPHA)
        if primary:
            # Gradient fill (purple → teal)
            for yy in range(h):
                t = yy / max(1, h - 1)
                c = lerp((140, 90, 230), (30, 200, 200), t)
                pygame.draw.line(b, (*c, 230), (0, yy), (w, yy))
        else:
            # Frosted dark glass
            pygame.draw.rect(b, (255, 255, 255, 28), (0, 0, w, h), border_radius=h // 2)
            pygame.draw.rect(b, (40, 60, 110, 140), (0, 0, w, h), border_radius=h // 2)
        # Mask to rounded
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=h // 2)
        b.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # Border + top highlight
        pygame.draw.rect(b, (200, 230, 255, 220), (0, 0, w, h), width=2, border_radius=h // 2)
        pygame.draw.line(b, (255, 255, 255, 120), (h // 2, 2), (w - h // 2, 2))
        s.blit(b, (x, y))
        ti = font(sz, True).render(text, True, (255, 255, 255))
        sh = font(sz, True).render(text, True, (10, 30, 60))
        tr = ti.get_rect(center=center)
        sh.set_alpha(160)
        s.blit(sh, (tr.x + 1, tr.y + 2))
        s.blit(ti, tr)

    glass_btn((W // 2, 360), "TAP TO START", 22, 240, 56, primary=True)
    glass_btn((W // 2, 425), "HOW TO PLAY", 18, 240, 46)
    glass_btn((W // 2, 482), "POWER-UPS",   18, 240, 46)

    # ── BEST + TOP 10 glass tiles ──
    def glass_tile(x, y, w, h, label, value, accent):
        b = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(b, (255, 255, 255, 24), (0, 0, w, h), border_radius=14)
        pygame.draw.rect(b, (40, 60, 110, 130), (0, 0, w, h), border_radius=14)
        # Border
        pygame.draw.rect(b, (200, 230, 255, 200), (0, 0, w, h), width=1, border_radius=14)
        # Top sheen
        pygame.draw.line(b, (255, 255, 255, 90), (12, 3), (w - 12, 3))
        s.blit(b, (x, y))
        lf = font(11, False).render(label, True, accent)
        s.blit(lf, lf.get_rect(center=(x + w // 2, y + 14)))
        if value:
            vf = font(22, True).render(value, True, (245, 250, 255))
            s.blit(vf, vf.get_rect(center=(x + w // 2, y + 34)))

    glass_tile(50, H - 110, 124, 52, "B E S T", "42", (140, 220, 255))
    glass_tile(186, H - 110, 124, 52, "T O P  10", "", (255, 180, 220))
    # Crystal trophy on right
    tcx, tcy = 186 + 62, H - 110 + 34
    # body
    pygame.draw.polygon(s, (220, 240, 255), [(tcx - 8, tcy - 8), (tcx + 8, tcy - 8), (tcx + 6, tcy + 2), (tcx - 6, tcy + 2)])
    pygame.draw.polygon(s, (140, 200, 240), [(tcx - 8, tcy - 8), (tcx, tcy - 8), (tcx - 2, tcy + 2), (tcx - 6, tcy + 2)])
    pygame.draw.rect(s, (220, 240, 255), (tcx - 2, tcy + 2, 4, 5))
    pygame.draw.rect(s, (220, 240, 255), (tcx - 7, tcy + 7, 14, 3))

    save("theme4_crystal_aurora.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# Theme 5: TROPICAL MIAMI SUNSET
# ─────────────────────────────────────────────────────────────────────────────
def theme_miami_sunset():
    s = pygame.Surface((W, H))
    # Sunset gradient: deep purple → magenta → orange → peach
    stops = [(36, 16, 80), (130, 30, 110), (210, 70, 120), (255, 130, 90), (255, 200, 130)]
    seg = H // (len(stops) - 1)
    for i in range(len(stops) - 1):
        for y in range(seg):
            t = y / max(1, seg - 1)
            c = lerp(stops[i], stops[i + 1], t)
            pygame.draw.line(s, c, (0, i * seg + y), (W, i * seg + y))

    # Sun disc
    sun_cx, sun_cy = W // 2, 320
    for r in range(110, 0, -2):
        t = 1 - r / 110
        c = lerp((255, 100, 80), (255, 240, 180), t)
        pygame.draw.circle(s, c, (sun_cx, sun_cy), r)
    # Sun horizontal stripes (retrowave)
    for i in range(6):
        y = sun_cy - 20 + i * 14
        pygame.draw.rect(s, lerp(stops[2], stops[3], 0.5), (sun_cx - 110, y, 220, 3))

    # Reflections on water (bottom half)
    water = pygame.Surface((W, 200), pygame.SRCALPHA)
    # Water gradient
    for y in range(200):
        t = y / 199
        c = lerp((180, 60, 110), (60, 18, 80), t)
        pygame.draw.line(water, c, (0, y), (W, y))
    # Sun reflection bars
    for i in range(0, 24):
        yy = i * 9
        a = max(20, 200 - i * 8)
        ww = 40 + i * 6
        pygame.draw.rect(water, (255, 200, 130, a), (sun_cx - ww // 2, yy, ww, 2))
    s.blit(water, (0, 440))

    # Palm tree silhouettes
    def palm(base_x, base_y, scale=1.0):
        # trunk
        trunk_h = int(120 * scale)
        for i in range(8):
            x_off = int(math.sin(i / 8 * math.pi) * 8 * scale)
            pygame.draw.line(s, (12, 4, 28), (base_x + x_off, base_y - i * trunk_h // 8),
                             (base_x + x_off, base_y - (i + 1) * trunk_h // 8), max(3, int(7 * scale)))
        # fronds
        top_x = base_x + int(math.sin(math.pi) * 8 * scale)
        top_y = base_y - trunk_h
        for ang in [-1.2, -0.6, 0.0, 0.6, 1.2, -1.8, 1.8]:
            for k in range(0, 50, 2):
                p = k / 50
                x = top_x + math.cos(ang) * 65 * scale * p
                y = top_y + math.sin(ang) * 25 * scale * p - 30 * (1 - (2 * p - 1) ** 2) * scale
                pygame.draw.circle(s, (12, 4, 28), (int(x), int(y)), max(2, int(4 * (1 - p) * scale)))

    palm(30, 540, 0.9)
    palm(330, 555, 1.0)
    palm(80, 580, 0.6)

    # Stars in upper portion
    random.seed(13)
    for _ in range(30):
        x = random.randint(0, W - 1)
        y = random.randint(0, 200)
        a = random.randint(60, 220)
        pygame.draw.circle(s, (255, 250, 220), (x, y), 1)

    # ── Title — chrome with pink-orange gradient ──
    title_text = "SKYBIT"
    tf = font(78, True)
    base = tf.render(title_text, True, (255, 255, 255))
    title_w, title_h = base.get_width(), base.get_height()
    title = pygame.Surface((title_w, title_h), pygame.SRCALPHA)
    # Gradient fill (top peach → bottom pink)
    grad = pygame.Surface((title_w, title_h), pygame.SRCALPHA)
    for y in range(title_h):
        t = y / max(1, title_h - 1)
        c = lerp((255, 220, 150), (255, 80, 160), t)
        pygame.draw.line(grad, c, (0, y), (title_w, y))
    title.blit(base, (0, 0))
    title.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    # Chrome strip in middle
    chrome = pygame.Surface((title_w, title_h), pygame.SRCALPHA)
    pygame.draw.rect(chrome, (255, 255, 255, 120), (0, title_h // 2 - 4, title_w, 8))
    title.blit(chrome, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    # Outline (dark purple)
    out = tf.render(title_text, True, (60, 10, 70))
    out_rect = base.get_rect(center=(W // 2, 130))
    for d in [(-3, 0), (3, 0), (0, -3), (0, 3), (-3, -3), (3, -3), (-3, 3), (3, 3)]:
        s.blit(out, (out_rect.x + d[0], out_rect.y + d[1]))
    s.blit(title, out_rect.topleft)

    # Subtitle — italic-feel uppercase pink
    sub = font(18, True).render("POCKET  SKY  FLYER", True, (255, 240, 200))
    sr = sub.get_rect(center=(W // 2, 186))
    # Dark drop
    sh = font(18, True).render("POCKET  SKY  FLYER", True, (60, 10, 70))
    s.blit(sh, (sr.x + 2, sr.y + 2))
    s.blit(sub, sr)
    # Underline gradient
    line = pygame.Surface((180, 3), pygame.SRCALPHA)
    for x in range(180):
        c = lerp((255, 220, 150), (255, 80, 160), x / 180)
        pygame.draw.line(line, c, (x, 0), (x, 3))
    s.blit(line, line.get_rect(center=(W // 2, 206)))

    # ── Tropical buttons ──
    def trop_btn(center, text, sz=22, w=240, h=54, primary=False):
        x = center[0] - w // 2
        y = center[1] - h // 2
        b = pygame.Surface((w, h), pygame.SRCALPHA)
        if primary:
            for yy in range(h):
                t = yy / max(1, h - 1)
                c = lerp((255, 200, 130), (255, 80, 160), t)
                pygame.draw.line(b, (*c, 255), (0, yy), (w, yy))
        else:
            for yy in range(h):
                t = yy / max(1, h - 1)
                c = lerp((250, 250, 250), (220, 200, 230), t)
                pygame.draw.line(b, (*c, 245), (0, yy), (w, yy))
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=h // 2)
        b.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # Gold border
        pygame.draw.rect(b, (255, 220, 130), (0, 0, w, h), width=3, border_radius=h // 2)
        # Top sheen
        pygame.draw.line(b, (255, 255, 255, 180), (h // 2, 4), (w - h // 2, 4), 2)
        s.blit(b, (x, y))
        col = (60, 10, 70) if not primary else (250, 250, 250)
        ti = font(sz, True).render(text, True, col)
        if primary:
            sh = font(sz, True).render(text, True, (140, 30, 80))
            tr = ti.get_rect(center=center)
            s.blit(sh, (tr.x + 1, tr.y + 2))
        else:
            tr = ti.get_rect(center=center)
        s.blit(ti, tr)

    trop_btn((W // 2, 380), "TAP TO START", 22, 240, 56, primary=True)
    trop_btn((W // 2, 445), "HOW TO PLAY", 18, 240, 46)
    trop_btn((W // 2, 502), "POWER-UPS",   18, 240, 46)

    # ── BEST + TOP 10 pastel tiles ──
    def pastel_tile(x, y, w, h, label, value, accent):
        b = pygame.Surface((w, h), pygame.SRCALPHA)
        for yy in range(h):
            t = yy / max(1, h - 1)
            c = lerp((255, 240, 240), (255, 210, 230), t)
            pygame.draw.line(b, (*c, 235), (0, yy), (w, yy))
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=14)
        b.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        pygame.draw.rect(b, accent, (0, 0, w, h), width=2, border_radius=14)
        s.blit(b, (x, y))
        lf = font(11, False).render(label, True, (140, 30, 80))
        s.blit(lf, lf.get_rect(center=(x + w // 2, y + 14)))
        if value:
            vf = font(22, True).render(value, True, (200, 40, 100))
            s.blit(vf, vf.get_rect(center=(x + w // 2, y + 34)))

    pastel_tile(50, H - 80, 124, 52, "B E S T", "42", (255, 130, 90))
    pastel_tile(186, H - 80, 124, 52, "T O P  10", "", (255, 220, 130))
    # gold trophy
    tcx, tcy = 186 + 62, H - 80 + 34
    pygame.draw.polygon(s, (255, 220, 130), [(tcx - 8, tcy - 8), (tcx + 8, tcy - 8), (tcx + 6, tcy + 2), (tcx - 6, tcy + 2)])
    pygame.draw.polygon(s, (180, 130, 50), [(tcx - 8, tcy - 8), (tcx + 8, tcy - 8), (tcx + 6, tcy + 2), (tcx - 6, tcy + 2)], width=1)
    pygame.draw.rect(s, (255, 220, 130), (tcx - 2, tcy + 2, 4, 5))
    pygame.draw.rect(s, (255, 220, 130), (tcx - 7, tcy + 7, 14, 3))

    save("theme5_miami_sunset.png", s)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating menu redesign mockups...")
    theme_neon_arcade()
    theme_storybook()
    theme_retro_crt()
    theme_aurora()
    theme_miami_sunset()
    print("Done.")
