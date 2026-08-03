#!/usr/bin/env python3
"""
cinema round 2 — HORIZON BURN (art-director revisions).

Changes from round 1:
  1. BACK pill ghosted: 1px GOLD@50 border, transparent fill, CREAM label
  2. Unlit hairline raised to SLATE@27, held flat to x=240, tapering by x=260
  3. Event ticks: COOL@70, 2px wide × 6px tall; positions adjusted:
       - x=60 (geyser) → skipped (inside bloom radius 55 from x=66)
       - x=145 → kept
       - x=155 → x=165 (enforce 20px min separation)
       - x=295 → skipped (beyond hairline tone at x=240)
  4. Burn ramp flattened: starts ~27% at x=0, eases up via t^0.6 curve
  5. Burn span given body: 3-row soft underglow below horizon (native res)
  6. Atmospheric terminus bloom:
       - Radial soft glow radius=55 GOLD peak=140
       - Wide warm haze 200×180px peak=22
       - Hot core layers (18px, 10px)
       - Vertical light shaft 3px wide, y=300→430
  7. Headline centered on x=180 (was effectively at x≈240)
  8. Sky gradient: faint warmth added at top, fades to INK by y=250
  9. Cinematic stat text below headline rule
"""
import os
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

W, H = 360, 640
SS = 3
ROOT = "/home/user/skybit"
FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"

INK   = (6,   8,  14)
GOLD  = (255, 206, 92)
CREAM = (246, 240, 230)
COOL  = (150, 168, 196)
SLATE = (58,  62,  82)
SCRIM = (26,  22,  34)

DEATH_PHASE = 0.184
DEATH_X     = int(DEATH_PHASE * W)   # 66 px, linear mapping
HORIZON_Y   = 430

DEATH_PILLAR = 25
DAY_N        = 1
TIME_ALIVE   = 47

# Adjusted event tick x-positions (note 2):
#   x=60  → skipped: inside bloom radius 55 centred at x=66 (66-55=11, 66+55=121)
#   x=145 → kept
#   x=155 → x=165: enforce ≥20px separation from x=145
#   x=295 → skipped: beyond hairline tone at x=240
EVENT_XS = (145, 165)

_fonts: dict = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


# ── text helpers ─────────────────────────────────────────────────────────────

def text(surf, s, size, center=None, midleft=None, midright=None,
         color=CREAM, shadow=(0, 0, 0, 150), track=0):
    f = font(size)
    if track:
        glyphs = [f.render(ch, True, color) for ch in s]
        tw = sum(g.get_width() for g in glyphs) + track * (len(s) - 1)
        th = f.get_height()
        img = pygame.Surface((max(1, tw), th), pygame.SRCALPHA)
        x = 0
        for ch, g in zip(s, glyphs):
            img.blit(g, (x, 0))
            x += g.get_width() + track
    else:
        img = f.render(s, True, color)
    rect = img.get_rect()
    if center:
        rect.center = center
    elif midleft:
        rect.midleft = midleft
    elif midright:
        rect.midright = midright
    if shadow:
        sh = img.copy()
        sh.fill((*shadow[:3], 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(shadow[3])
        surf.blit(sh, (rect.x + 1, rect.y + 1))
    surf.blit(img, rect)
    return rect


def chip(surf, rect, radius=6, fill=(18, 15, 24), alpha=234,
         border=CREAM, border_a=54):
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(s, (*fill, alpha), s.get_rect(), border_radius=radius)
    if border_a:
        pygame.draw.rect(s, (*border, border_a), s.get_rect(), width=1,
                         border_radius=radius)
    surf.blit(s, rect.topleft)


def soft_glow(radius, color, peak=110, falloff=2.0):
    """Additive glow with falloff baked into RGB (BLEND_ADD ignores src alpha).

    Premultiplying RGB keeps the ramp: blit with BLEND_ADD."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        f = (1 - (r / radius) ** falloff) * (peak / 255.0)
        s_col = (int(color[0] * f), int(color[1] * f), int(color[2] * f), 255)
        pygame.draw.circle(s, s_col, (c, c), r)
    return s


def alpha_line(surf, rgba, p0, p1, width=1):
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


# ── horizon (supersampled) ────────────────────────────────────────────────────

def draw_horizon(ss):
    """Supersampled horizon pass. Downscale cleans the aliasing."""
    k  = SS
    y  = HORIZON_Y * k

    # --- BURN RAMP (note 3): flattened, starts ~27%, eases up via t^0.6 ---
    # t^0.6 curve: at t=0 → 27%, at t=0.5 → ~75%, at t=1 → 100%.
    # Body is added as a native-res underglow after the SS blit (see render_screen).
    for i in range(DEATH_X):
        t    = i / max(1, DEATH_X - 1)
        f    = 0.27 + 0.73 * (t ** 0.6)
        r_c  = int(GOLD[0] * f)
        g_c  = int(GOLD[1] * f)
        b_c  = int(GOLD[2] * f)
        pygame.draw.line(ss, (r_c, g_c, b_c, 255),
                         (i * k, y), ((i + 1) * k, y), k)

    # --- UNLIT HAIRLINE (note 2): SLATE@27, flat to x=240, taper to x=260 ---
    for i in range(DEATH_X, W):
        if i <= 240:
            a = 27
        elif i <= 260:
            a = int(27 * (1.0 - (i - 240) / 20.0))
        else:
            break
        if a <= 0:
            continue
        pygame.draw.line(ss, (*SLATE, a), (i * k, y), ((i + 1) * k, y), k)

    # --- EVENT TICKS (note 2): COOL@70, 2px wide × 6px tall ---
    for ex in EVENT_XS:
        pygame.draw.line(ss, (*COOL, 70),
                         (ex * k, (HORIZON_Y + 1) * k),
                         (ex * k, (HORIZON_Y + 7) * k),  # 6 native px tall
                         2 * k)                           # 2 native px wide

    # Light column REMOVED — replaced by atmospheric bloom in render_screen().


# ── full screen ───────────────────────────────────────────────────────────────

def render_screen():
    surf = pygame.Surface((W, H))
    surf.fill(INK)

    # --- SKY GRADIENT (note 6): hint of depth in the upper void ---
    # Adds (8,6,4) at y=0, decays to zero by y=250 via a 1.5-power curve.
    sky_ug = pygame.Surface((W, 250), pygame.SRCALPHA)
    for iy in range(250):
        t = (1.0 - iy / 250) ** 1.5
        sky_ug.fill((int(8 * t), int(6 * t), int(4 * t), 255),
                    pygame.Rect(0, iy, W, 1))
    surf.blit(sky_ug, (0, 0), special_flags=pygame.BLEND_ADD)

    # --- HORIZON (supersampled then downscale) ---
    ss = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    draw_horizon(ss)
    surf.blit(pygame.transform.smoothscale(ss, (W, H)), (0, 0))

    # --- BURN UNDERGLOW (note 3): 3-px soft body below the horizon ---
    # Native-res, additive. Gives the flown span weight vs the 1px unlit hairline.
    ug = pygame.Surface((DEATH_X, 3), pygame.SRCALPHA)
    for i in range(DEATH_X):
        t = i / max(1, DEATH_X - 1)
        f = 0.27 + 0.73 * (t ** 0.6)
        for dy, af in enumerate([0.50, 0.28, 0.12]):
            ug.fill((int(GOLD[0] * f * af),
                     int(GOLD[1] * f * af),
                     int(GOLD[2] * f * af), 255),
                    pygame.Rect(i, dy, 1, 1))
    surf.blit(ug, (0, HORIZON_Y + 1), special_flags=pygame.BLEND_ADD)

    # --- ATMOSPHERIC TERMINUS BLOOM (note 4) ---

    # Main radial bloom: 55px radius, GOLD peak=140
    g_main = soft_glow(radius=55, color=GOLD, peak=140, falloff=2.0)
    surf.blit(g_main, (DEATH_X - 56, HORIZON_Y - 56),
              special_flags=pygame.BLEND_ADD)

    # Wide warm sky haze: 200×180px footprint, very low peak (22)
    g_haze_raw = soft_glow(radius=100, color=GOLD, peak=22, falloff=2.0)
    g_haze = pygame.transform.scale(g_haze_raw, (200, 180))
    surf.blit(g_haze, (DEATH_X - 100, HORIZON_Y - 90),
              special_flags=pygame.BLEND_ADD)

    # Hot core layers
    for rad, col, pk in ((18, (255, 220, 120), 80),
                         (10, (255, 240, 160), 120)):
        g = soft_glow(rad, col, peak=pk, falloff=2.0)
        surf.blit(g, (DEATH_X - rad - 1, HORIZON_Y - rad - 1),
                  special_flags=pygame.BLEND_ADD)

    # Vertical light shaft: 3px wide, fading from (180,160,80) at y=430 → zero at y=300
    shaft_h = HORIZON_Y - 300   # 130 px
    shaft   = pygame.Surface((3, shaft_h), pygame.SRCALPHA)
    for iy in range(shaft_h):
        t = iy / max(1, shaft_h - 1)   # 0=top (dim), 1=bottom (bright)
        shaft.fill((int(180 * t), int(160 * t), int(80 * t), 255),
                   pygame.Rect(0, iy, 3, 1))
    surf.blit(shaft, (DEATH_X - 1, 300), special_flags=pygame.BLEND_ADD)

    # --- BANNER ──────────────────────────────────────────────────────────────
    pygame.draw.rect(surf, SCRIM, (0, 0, W, 74))
    fade = pygame.Surface((W, 10), pygame.SRCALPHA)
    for i in range(10):
        fade.fill((*SCRIM, int(238 * (1 - i / 10) ** 1.4)),
                  pygame.Rect(0, i, W, 1))
    surf.blit(fade, (0, 74))
    alpha_line(surf, (255, 206, 92, 150), (0, 74), (W - 1, 74), 1)

    text(surf, f"FLIGHT LOG  ·  DAY {DAY_N}", 21,
         center=(W // 2, 28), color=GOLD, track=3, shadow=None)
    text(surf, f"PILLAR {DEATH_PILLAR}   ·   0:{TIME_ALIVE:02d}", 12,
         center=(W // 2, 55), color=CREAM, shadow=None)

    # --- HEADLINE centered on x=180 (note 5) ────────────────────────────────
    pct    = f"{DEATH_PHASE * 100:.0f}%"
    f_big  = font(21)
    f_sml  = font(11)
    w_pct  = f_big.size(pct)[0]
    w_tail = f_sml.size("  OF THE DAY FLOWN")[0]
    total_headline_w  = w_pct + w_tail
    headline_start_x  = 180 - total_headline_w // 2

    r_pct = text(surf, pct, 21,
                 midleft=(headline_start_x, 104), color=GOLD, shadow=None)
    text(surf, "  OF THE DAY FLOWN", 11,
         midleft=(r_pct.right, 106), color=CREAM, shadow=None)
    rule_end = headline_start_x + total_headline_w
    alpha_line(surf, (255, 206, 92, 96),
               (headline_start_x, 120), (rule_end, 120), 1)

    # --- CINEMATIC STAT TEXT (note 7) ────────────────────────────────────────
    text(surf,
         f"DAY {DAY_N}  ·  PILLAR {DEATH_PILLAR}  ·  0:{TIME_ALIVE:02d}",
         10, center=(180, 136), color=CREAM, shadow=None, track=2)

    # --- DEATH CALLOUT CHIP ──────────────────────────────────────────────────
    f10, f8 = font(10), font(8)
    cw = max(f10.size("ENDED HERE")[0],
             f8.size(f"PILLAR {DEATH_PILLAR}  ·  0:{TIME_ALIVE:02d}")[0]) + 20
    cr = pygame.Rect(0, 0, cw, 34)
    cr.bottomleft = (DEATH_X + 20, 415)   # ≥20px clearance from x=66
    chip(surf, cr, radius=7, alpha=234, border_a=54)
    text(surf, "ENDED HERE", 10,
         midleft=(cr.x + 10, cr.y + 11), color=GOLD, shadow=None)
    text(surf, f"PILLAR {DEATH_PILLAR}  ·  0:{TIME_ALIVE:02d}", 8,
         midleft=(cr.x + 10, cr.y + 24), color=CREAM, shadow=None)

    # --- BACK PILL — ghost/outline version (note 1) ──────────────────────────
    pr = pygame.Rect(0, 0, 122, 36)
    pr.center = (W // 2, 597)
    # Transparent fill, 1px GOLD@50 border
    pill = pygame.Surface(pr.size, pygame.SRCALPHA)
    pygame.draw.rect(pill, (*GOLD, 50), pill.get_rect(), width=1,
                     border_radius=18)
    surf.blit(pill, pr.topleft)
    # CREAM label — must outshine nothing
    text(surf, "BACK", 13, center=(pr.centerx, pr.centery),
         color=CREAM, shadow=None, track=2)

    return surf


OUT_SLUG  = "cinema"
OUT_ROUND = "round_2"


def main():
    screen = render_screen()
    out = os.path.join(ROOT, "docs", "flight_log_arc_v2",
                       OUT_SLUG, f"{OUT_ROUND}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(screen, out)
    img = pygame.image.load(out)
    print(f"saved {out}  {img.get_size()}")


if __name__ == "__main__":
    main()
