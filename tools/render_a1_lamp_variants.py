"""Render 5 candidate genie-lamp icons + the current original for
side-by-side review. Saves a 6-up comparison sheet plus individual
portraits to docs/screenshots/genie_designs/.

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_a1_lamp_variants [tag]
"""
import os, sys, math, random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie_designs")
os.makedirs(OUT_DIR, exist_ok=True)

# Higher resolution than the in-game icon (88×88 native, ×6 SS)
W, H, SS = 88, 88, 6
PW, PH = W * SS, H * SS
SKY = (110, 175, 220)
DISPLAY_SCALE = 4   # blow each portrait up so surface detail reads


def s(v):
    return int(v * SS)


def aa_circle(surf, color, cx, cy, r):
    pygame.draw.circle(surf, color, (int(cx), int(cy)), int(r))


def ell(surf, color, cx, cy, w, h):
    pygame.draw.ellipse(surf, color,
                        (int(cx - w / 2), int(cy - h / 2),
                         int(w), int(h)))


def gem_diamond(surf, cx, cy, r, color, hi_color):
    pygame.draw.polygon(surf, color,
                        [(cx, cy - r), (cx + r, cy),
                         (cx, cy + r), (cx - r, cy)])
    pygame.draw.polygon(surf, hi_color,
                        [(cx, cy - r),
                         (cx - int(r * 0.55), cy),
                         (cx - int(r * 0.3),
                          cy - int(r * 0.3))])
    pygame.draw.circle(surf, (255, 255, 255),
                       (int(cx - r * 0.3), int(cy - r * 0.5)),
                       max(1, int(r * 0.18)))


def smoke_ribbon(surf, origin_x, origin_y, palette,
                 n_puffs=12, height_n=44, curl=2.0, t=0.0):
    """Vertical column of puffs rising from (origin_x, origin_y),
    swaying with `t` and getting smaller toward the top."""
    for i in range(n_puffs):
        k = i / max(1, n_puffs - 1)
        x = origin_x + math.sin(t + i * 0.4) * s(curl) * (1 + k)
        y = origin_y - int(s(height_n) * k)
        rad = max(s(1), int(s(3) * (1 - k * 0.6)))
        alpha = int(220 * (1 - k * 0.8))
        col = palette[min(int(k * len(palette)), len(palette) - 1)]
        puff = pygame.Surface((rad * 2 + 4, rad * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(puff, (*col, alpha),
                           (rad + 2, rad + 2), rad)
        surf.blit(puff, (int(x - rad - 2), int(y - rad - 2)))


def glow_halo(surf, cx, cy, w, h, colors):
    """Multi-layer soft alpha glow centred on (cx, cy)."""
    for r_w, r_h, col, alpha in colors:
        srf = pygame.Surface((r_w + 4, r_h + 4), pygame.SRCALPHA)
        pygame.draw.ellipse(srf, (*col, alpha), (2, 2, r_w, r_h))
        surf.blit(srf, (int(cx - r_w / 2), int(cy - r_h / 2)))


def sparkles_around(surf, cx, cy, n=6, radius=s(30), color=(255, 255, 200),
                    rng_seed=11):
    """Tiny 4-point sparkle stars scattered in a ring around (cx, cy)."""
    rng = random.Random(rng_seed)
    for _ in range(n):
        ang = rng.uniform(0, math.tau)
        r = rng.uniform(radius * 0.7, radius)
        sx = cx + math.cos(ang) * r
        sy = cy + math.sin(ang) * r * 0.85
        sr = rng.randint(max(1, s(1) // 2), s(1))
        # Cross + dot
        pygame.draw.line(surf, color,
                         (int(sx - sr * 2), int(sy)),
                         (int(sx + sr * 2), int(sy)),
                         max(1, s(1) // 2))
        pygame.draw.line(surf, color,
                         (int(sx), int(sy - sr * 2)),
                         (int(sx), int(sy + sr * 2)),
                         max(1, s(1) // 2))
        aa_circle(surf, (255, 255, 255), sx, sy, max(1, sr))


# ─────────────────────────────────────────────────────────────────────────────
# Lamp 1 — Disney-Aladdin classic
# ─────────────────────────────────────────────────────────────────────────────

def draw_lamp_1_aladdin(big, cx, cy):
    AMBER_LO  = (110,  60,  10)
    AMBER     = (200, 130,  30)
    AMBER_HI  = (255, 215, 110)
    GOLD      = (255, 235, 140)
    RUBY      = (220,  60,  80)
    RUBY_HI   = (255, 175, 195)
    BLACK     = ( 18,  14,  10)
    SMOKE_LO  = (135,  85, 170)
    SMOKE     = (185, 140, 220)
    SMOKE_HI  = (230, 205, 250)

    # Warm halo
    glow_halo(big, cx, cy + s(8), s(70), s(48), [
        (s(70), s(48), AMBER_HI, 35),
        (s(54), s(36), GOLD,     55),
        (s(38), s(26), GOLD,     80),
    ])

    # Body — wide oval
    body_cy = cy + s(10)
    body_w = s(46)
    body_h = s(20)
    # outline
    ell(big, BLACK, cx, body_cy, body_w + s(2), body_h + s(2))
    # mid tone
    ell(big, AMBER_LO, cx, body_cy, body_w, body_h)
    # main
    ell(big, AMBER, cx, body_cy - s(1), body_w - s(3), body_h - s(3))
    # big curving highlight crescent
    pygame.draw.arc(big, AMBER_HI,
                    (cx - body_w // 2 + s(4), body_cy - body_h // 2 + s(2),
                     body_w - s(8), body_h - s(8)),
                    math.radians(200), math.radians(340), max(2, s(1)))
    # smaller bright dome highlight
    ell(big, GOLD, cx - s(6), body_cy - s(5), s(14), s(5))

    # Foot ring base
    foot_w = s(26)
    foot_h = s(4)
    ell(big, BLACK, cx, body_cy + body_h // 2 + s(2), foot_w + s(1), foot_h)
    ell(big, AMBER, cx, body_cy + body_h // 2 + s(2), foot_w, foot_h - s(1))

    # Spout — curly S-curve with pronounced tip curl
    sp_base_x = cx + s(20)
    sp_base_y = body_cy - s(2)
    sp_pts = [
        (sp_base_x,            sp_base_y + s(4)),
        (sp_base_x + s(8),     sp_base_y - s(2)),
        (sp_base_x + s(12),    sp_base_y - s(12)),
        (sp_base_x + s(10),    sp_base_y - s(22)),   # curl tip
        (sp_base_x + s(4),     sp_base_y - s(26)),
        (sp_base_x + s(2),     sp_base_y - s(20)),
        (sp_base_x + s(6),     sp_base_y - s(15)),
        (sp_base_x + s(7),     sp_base_y - s(5)),
        (sp_base_x - s(2),     sp_base_y + s(2)),
    ]
    pygame.draw.polygon(big, BLACK, [(x + s(1), y + s(1)) for x, y in sp_pts])
    pygame.draw.polygon(big, AMBER, sp_pts)
    # Spout highlight stripe
    pygame.draw.line(big, AMBER_HI,
                     (sp_base_x + s(6), sp_base_y - s(2)),
                     (sp_base_x + s(8), sp_base_y - s(18)),
                     max(2, s(1)))

    # Handle — looped ring on the LEFT
    h_cx = cx - s(22)
    h_cy = body_cy
    h_w  = s(10)
    h_h  = s(18)
    pygame.draw.ellipse(big, BLACK,
                        (h_cx - h_w // 2 - s(1), h_cy - h_h // 2 - s(1),
                         h_w + s(2), h_h + s(2)))
    pygame.draw.ellipse(big, AMBER,
                        (h_cx - h_w // 2, h_cy - h_h // 2, h_w, h_h))
    pygame.draw.ellipse(big, SKY,
                        (h_cx - h_w // 2 + s(2), h_cy - h_h // 2 + s(2),
                         h_w - s(4), h_h - s(4)))
    pygame.draw.ellipse(big, BLACK,
                        (h_cx - h_w // 2 + s(2), h_cy - h_h // 2 + s(2),
                         h_w - s(4), h_h - s(4)), max(1, s(1) // 2))

    # Ruby gem on body
    gem_diamond(big, cx, body_cy, s(4), RUBY, RUBY_HI)

    # Gold rim — top edge of body
    pygame.draw.arc(big, GOLD,
                    (cx - body_w // 2 + s(2), body_cy - body_h // 2,
                     body_w - s(4), body_h - s(6)),
                    math.radians(195), math.radians(345), max(2, s(1)))

    # Smoke ribbon from spout tip
    smoke_ribbon(big, sp_base_x + s(4), sp_base_y - s(26),
                 [SMOKE_HI, SMOKE, SMOKE_LO],
                 n_puffs=11, height_n=42, curl=2.0)

    # Sparkles around the lamp
    sparkles_around(big, cx, cy - s(4), n=5, radius=s(40), color=AMBER_HI)


# ─────────────────────────────────────────────────────────────────────────────
# Lamp 2 — Persian ornate
# ─────────────────────────────────────────────────────────────────────────────

def draw_lamp_2_persian(big, cx, cy):
    BRASS_DK  = ( 75,  50,  20)
    BRASS     = (175, 140,  70)
    BRASS_HI  = (235, 215, 155)
    GOLD      = (255, 230, 150)
    SAPPHIRE  = ( 70, 100, 220)
    SAPPHIRE_HI = (175, 200, 255)
    BLACK     = ( 18,  14,  10)
    SMOKE_LO  = (110, 100, 160)
    SMOKE     = (170, 165, 215)
    SMOKE_HI  = (215, 215, 240)

    # Cool greenish halo (less warm than #1)
    glow_halo(big, cx, cy + s(8), s(64), s(42), [
        (s(64), s(42), BRASS_HI, 30),
        (s(46), s(28), GOLD,     50),
    ])

    # Body
    body_cy = cy + s(10)
    body_w = s(44)
    body_h = s(20)
    ell(big, BLACK, cx, body_cy, body_w + s(2), body_h + s(2))
    ell(big, BRASS_DK, cx, body_cy, body_w, body_h)
    ell(big, BRASS, cx, body_cy - s(1), body_w - s(4), body_h - s(4))
    # subtler dome highlight
    ell(big, BRASS_HI, cx - s(8), body_cy - s(4), s(12), s(4))

    # Engraved horizontal bands across the dome
    for off in (-s(5), -s(1), s(3)):
        pygame.draw.arc(big, BRASS_DK,
                        (cx - body_w // 2 + s(4), body_cy + off,
                         body_w - s(8), s(4)),
                        math.radians(200), math.radians(340), max(1, s(1) // 2))
        pygame.draw.arc(big, GOLD,
                        (cx - body_w // 2 + s(4), body_cy + off - s(1),
                         body_w - s(8), s(4)),
                        math.radians(220), math.radians(320), max(1, s(1) // 2))

    # Arabesque dot pattern in centre band
    for dx in (-s(10), -s(4), s(2), s(8)):
        pygame.draw.circle(big, GOLD, (cx + dx, body_cy + s(2)), max(1, s(1)))

    # Foot ring base — taller, more ornate
    foot_w = s(30)
    foot_h = s(6)
    ell(big, BLACK, cx, body_cy + body_h // 2 + s(2), foot_w + s(1), foot_h + s(1))
    ell(big, BRASS_DK, cx, body_cy + body_h // 2 + s(2), foot_w, foot_h)
    pygame.draw.line(big, GOLD,
                     (cx - foot_w // 2 + s(2), body_cy + body_h // 2 + s(1)),
                     (cx + foot_w // 2 - s(2), body_cy + body_h // 2 + s(1)),
                     max(1, s(1)))

    # Tall narrow spout
    sp_base_x = cx + s(20)
    sp_base_y = body_cy - s(2)
    sp_pts = [
        (sp_base_x,            sp_base_y + s(4)),
        (sp_base_x + s(6),     sp_base_y - s(4)),
        (sp_base_x + s(10),    sp_base_y - s(18)),
        (sp_base_x + s(8),     sp_base_y - s(26)),
        (sp_base_x + s(6),     sp_base_y - s(28)),
        (sp_base_x + s(3),     sp_base_y - s(26)),
        (sp_base_x + s(5),     sp_base_y - s(18)),
        (sp_base_x + s(5),     sp_base_y - s(4)),
        (sp_base_x - s(2),     sp_base_y + s(2)),
    ]
    pygame.draw.polygon(big, BLACK, [(x + s(1), y + s(1)) for x, y in sp_pts])
    pygame.draw.polygon(big, BRASS, sp_pts)
    # gold trim line along spout
    pygame.draw.line(big, GOLD,
                     (sp_base_x + s(5), sp_base_y - s(2)),
                     (sp_base_x + s(7), sp_base_y - s(24)),
                     max(2, s(1)))

    # Handle — round with internal pattern
    h_cx = cx - s(22)
    h_cy = body_cy
    h_w  = s(11)
    h_h  = s(20)
    pygame.draw.ellipse(big, BLACK,
                        (h_cx - h_w // 2 - s(1), h_cy - h_h // 2 - s(1),
                         h_w + s(2), h_h + s(2)))
    pygame.draw.ellipse(big, BRASS,
                        (h_cx - h_w // 2, h_cy - h_h // 2, h_w, h_h))
    pygame.draw.ellipse(big, SKY,
                        (h_cx - h_w // 2 + s(2), h_cy - h_h // 2 + s(2),
                         h_w - s(4), h_h - s(4)))
    pygame.draw.ellipse(big, BRASS_DK,
                        (h_cx - h_w // 2 + s(2), h_cy - h_h // 2 + s(2),
                         h_w - s(4), h_h - s(4)), max(1, s(1) // 2))

    # Sapphire at spout base
    gem_diamond(big, sp_base_x + s(1), sp_base_y, s(3),
                SAPPHIRE, SAPPHIRE_HI)

    # Tassel hanging off the handle
    tassel_x = h_cx
    tassel_y = h_cy + h_h // 2 + s(2)
    aa_circle(big, GOLD, tassel_x, tassel_y, s(2))
    for dx in (-s(2), 0, s(2)):
        pygame.draw.line(big, GOLD,
                         (tassel_x + dx, tassel_y + s(2)),
                         (tassel_x + dx - s(1), tassel_y + s(8)),
                         max(1, s(1) // 2))

    # Smoke
    smoke_ribbon(big, sp_base_x + s(5), sp_base_y - s(28),
                 [SMOKE_HI, SMOKE, SMOKE_LO],
                 n_puffs=10, height_n=36, curl=1.5)

    sparkles_around(big, cx, cy - s(2), n=4, radius=s(36),
                    color=BRASS_HI, rng_seed=21)


# ─────────────────────────────────────────────────────────────────────────────
# Lamp 3 — Steampunk brass
# ─────────────────────────────────────────────────────────────────────────────

def draw_lamp_3_steampunk(big, cx, cy):
    BRASS_DK  = ( 80,  55,  25)
    BRASS     = (170, 125,  55)
    BRASS_HI  = (220, 185,  90)
    COPPER    = (210, 110,  60)
    PATINA    = ( 70, 130, 130)
    GAUGE_RED = (200,  55,  45)
    BLACK     = ( 18,  14,  10)
    STEAM_LO  = (140, 145, 150)
    STEAM     = (190, 200, 210)
    STEAM_HI  = (230, 235, 240)

    # Mild bronze halo
    glow_halo(big, cx, cy + s(8), s(54), s(36), [
        (s(54), s(36), COPPER, 25),
        (s(40), s(26), BRASS,  40),
    ])

    # Body — slightly more cylindrical
    body_cy = cy + s(10)
    body_w = s(44)
    body_h = s(22)
    ell(big, BLACK, cx, body_cy, body_w + s(2), body_h + s(2))
    ell(big, BRASS_DK, cx, body_cy, body_w, body_h)
    ell(big, BRASS, cx, body_cy - s(1), body_w - s(4), body_h - s(4))
    # mechanical seam line down the centre
    pygame.draw.line(big, BRASS_DK,
                     (cx, body_cy - body_h // 2 + s(2)),
                     (cx, body_cy + body_h // 2 - s(2)),
                     max(2, s(1)))

    # Rivets along the seam edges
    for dx in (-s(16), -s(8), s(8), s(16)):
        for dy in (-s(6), s(0), s(6)):
            aa_circle(big, BRASS_DK, cx + dx, body_cy + dy, s(1))
            aa_circle(big, BRASS_HI, cx + dx - s(1) // 2,
                      body_cy + dy - s(1) // 2, max(1, s(1) // 2))

    # Patina in the upper crevice (a small green-blue inset)
    pygame.draw.arc(big, PATINA,
                    (cx - body_w // 2 + s(6), body_cy - body_h // 2 + s(2),
                     body_w - s(12), s(6)),
                    math.radians(210), math.radians(330), max(2, s(1)))

    # Pressure-valve gauge stamped on body
    gauge_cx = cx - s(8)
    gauge_cy = body_cy + s(3)
    aa_circle(big, BLACK, gauge_cx, gauge_cy, s(4))
    aa_circle(big, BRASS_HI, gauge_cx, gauge_cy, s(3))
    pygame.draw.line(big, GAUGE_RED,
                     (gauge_cx, gauge_cy),
                     (gauge_cx + s(2), gauge_cy - s(2)),
                     max(2, s(1) // 2))

    # Thick pipe-style spout
    sp_x = cx + s(18)
    sp_top = body_cy - s(22)
    pygame.draw.rect(big, BLACK,
                     (sp_x - s(1), sp_top - s(1),
                      s(10), body_cy - sp_top + s(2)))
    pygame.draw.rect(big, BRASS,
                     (sp_x, sp_top, s(8), body_cy - sp_top))
    # pipe flange at top of spout
    pygame.draw.rect(big, BRASS_DK,
                     (sp_x - s(2), sp_top - s(3), s(12), s(4)))
    pygame.draw.rect(big, BRASS_HI,
                     (sp_x - s(2), sp_top - s(3), s(12), max(1, s(1))))
    # rivets on flange
    for fx in (s(0), s(8)):
        aa_circle(big, BRASS_DK, sp_x + fx, sp_top - s(1), max(1, s(1) // 2))

    # Spout highlight stripe
    pygame.draw.line(big, BRASS_HI,
                     (sp_x + s(2), sp_top),
                     (sp_x + s(2), body_cy - s(2)),
                     max(1, s(1)))

    # Foot ring (mechanical, with rivets)
    foot_w = s(34)
    foot_h = s(6)
    pygame.draw.rect(big, BLACK,
                     (cx - foot_w // 2 - s(1),
                      body_cy + body_h // 2 - s(1),
                      foot_w + s(2), foot_h + s(2)))
    pygame.draw.rect(big, BRASS_DK,
                     (cx - foot_w // 2,
                      body_cy + body_h // 2,
                      foot_w, foot_h))
    for fx in range(-int(foot_w / 2) + s(3), int(foot_w / 2), s(6)):
        aa_circle(big, BRASS_HI, cx + fx,
                  body_cy + body_h // 2 + s(3), max(1, s(1) // 2))

    # Handle — straight mechanical bar with rivets
    h_top = body_cy - s(4)
    h_bot = body_cy + s(4)
    pygame.draw.rect(big, BLACK,
                     (cx - s(28), h_top - s(1), s(10), h_bot - h_top + s(2)))
    pygame.draw.rect(big, BRASS,
                     (cx - s(27), h_top, s(8), h_bot - h_top))
    aa_circle(big, BRASS_DK, cx - s(23), body_cy, s(1))

    # Steam (greyish, mechanical)
    smoke_ribbon(big, sp_x + s(4), sp_top - s(3),
                 [STEAM_HI, STEAM, STEAM_LO],
                 n_puffs=9, height_n=30, curl=0.8)

    # No magic sparkles — keep the industrial mood


# ─────────────────────────────────────────────────────────────────────────────
# Lamp 4 — Crystal cosmic
# ─────────────────────────────────────────────────────────────────────────────

def draw_lamp_4_cosmic(big, cx, cy):
    NIGHT     = ( 25,  20,  60)
    PURPLE    = (130,  70, 200)
    PINK      = (210,  90, 180)
    BLUE      = ( 80, 150, 240)
    CYAN      = (175, 230, 255)
    GOLD      = (255, 230, 150)
    GOLD_HI   = (255, 245, 195)
    WHITE     = (250, 250, 250)
    BLACK     = ( 18,  14,  10)

    # Strong cosmic halo (multi-layer)
    glow_halo(big, cx, cy + s(6), s(82), s(60), [
        (s(82), s(60), CYAN,   45),
        (s(62), s(44), PURPLE, 60),
        (s(46), s(32), PINK,   65),
        (s(32), s(24), WHITE,  80),
    ])

    # Body — translucent: dark base + nebula clouds inside
    body_cy = cy + s(10)
    body_w = s(44)
    body_h = s(20)
    ell(big, GOLD_HI, cx, body_cy, body_w + s(2), body_h + s(2))
    ell(big, NIGHT, cx, body_cy, body_w, body_h)
    # Nebula clouds inside (clipped to body region by drawing over
    # the night base)
    rng = random.Random(7)
    for _ in range(20):
        nx = cx + rng.randint(-body_w // 2 + s(3), body_w // 2 - s(3))
        ny = body_cy + rng.randint(-body_h // 2 + s(2), body_h // 2 - s(2))
        nr = rng.randint(s(2), s(5))
        nc = rng.choice([PURPLE, PINK, BLUE])
        srf = pygame.Surface((nr * 2 + 4, nr * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(srf, (*nc, 110),
                           (nr + 2, nr + 2), nr)
        big.blit(srf, (nx - nr - 2, ny - nr - 2))
    # Star dots
    rng2 = random.Random(13)
    for _ in range(10):
        sx_p = cx + rng2.randint(-body_w // 2 + s(3), body_w // 2 - s(3))
        sy_p = body_cy + rng2.randint(-body_h // 2 + s(2), body_h // 2 - s(2))
        aa_circle(big, WHITE, sx_p, sy_p, max(1, s(1) // 2))

    # Re-stroke body outline in glowing gold so it reads
    pygame.draw.ellipse(big, GOLD_HI,
                        (cx - body_w // 2, body_cy - body_h // 2,
                         body_w, body_h), max(2, s(1)))
    pygame.draw.ellipse(big, GOLD,
                        (cx - body_w // 2 + s(1),
                         body_cy - body_h // 2 + s(1),
                         body_w - s(2), body_h - s(2)),
                        max(1, s(1) // 2))

    # Foot ring
    foot_w = s(28)
    foot_h = s(4)
    ell(big, GOLD, cx, body_cy + body_h // 2 + s(2), foot_w, foot_h)

    # Spout — translucent, with nebula inside
    sp_base_x = cx + s(20)
    sp_base_y = body_cy - s(2)
    sp_pts = [
        (sp_base_x,            sp_base_y + s(4)),
        (sp_base_x + s(8),     sp_base_y - s(2)),
        (sp_base_x + s(12),    sp_base_y - s(12)),
        (sp_base_x + s(10),    sp_base_y - s(22)),
        (sp_base_x + s(4),     sp_base_y - s(26)),
        (sp_base_x + s(2),     sp_base_y - s(20)),
        (sp_base_x + s(6),     sp_base_y - s(15)),
        (sp_base_x + s(7),     sp_base_y - s(5)),
        (sp_base_x - s(2),     sp_base_y + s(2)),
    ]
    pygame.draw.polygon(big, NIGHT, sp_pts)
    pygame.draw.polygon(big, GOLD, sp_pts, max(2, s(1)))
    # tiny stars in spout
    aa_circle(big, WHITE, sp_base_x + s(6), sp_base_y - s(10),
              max(1, s(1) // 2))
    aa_circle(big, WHITE, sp_base_x + s(7), sp_base_y - s(18),
              max(1, s(1) // 2))

    # Handle — translucent ring with gold trim
    h_cx = cx - s(22)
    h_cy = body_cy
    h_w  = s(10)
    h_h  = s(18)
    pygame.draw.ellipse(big, NIGHT,
                        (h_cx - h_w // 2, h_cy - h_h // 2, h_w, h_h))
    pygame.draw.ellipse(big, GOLD,
                        (h_cx - h_w // 2, h_cy - h_h // 2, h_w, h_h),
                        max(2, s(1)))
    pygame.draw.ellipse(big, SKY,
                        (h_cx - h_w // 2 + s(3), h_cy - h_h // 2 + s(3),
                         h_w - s(6), h_h - s(6)))
    pygame.draw.ellipse(big, GOLD,
                        (h_cx - h_w // 2 + s(3), h_cy - h_h // 2 + s(3),
                         h_w - s(6), h_h - s(6)), max(1, s(1) // 2))

    # Magical smoke (cyan + purple swirl, brighter)
    smoke_ribbon(big, sp_base_x + s(4), sp_base_y - s(26),
                 [WHITE, CYAN, PURPLE, BLUE],
                 n_puffs=14, height_n=46, curl=2.5)

    # Big sparkle ring + star burst
    sparkles_around(big, cx, cy - s(2), n=8, radius=s(44),
                    color=CYAN, rng_seed=11)
    sparkles_around(big, cx, cy - s(2), n=4, radius=s(34),
                    color=GOLD_HI, rng_seed=17)


# ─────────────────────────────────────────────────────────────────────────────
# Lamp 5 — Comic-book pop
# ─────────────────────────────────────────────────────────────────────────────

def draw_lamp_5_comic(big, cx, cy):
    GOLD      = (255, 200,  60)
    GOLD_DK   = (180, 130,  20)
    GOLD_HI   = (255, 230, 120)
    RUBY      = (220,  60,  80)
    BLACK     = ( 15,  10,   5)
    WHITE     = (255, 255, 245)
    SMOKE     = (210, 215, 235)
    OUT_W     = max(3, int(s(1) * 0.85))

    # Comic POW background — radial yellow burst behind lamp
    burst_cy = cy + s(8)
    for ang_deg in range(0, 360, 30):
        ang = math.radians(ang_deg)
        ix = cx + math.cos(ang) * s(20)
        iy = burst_cy + math.sin(ang) * s(20) * 0.85
        ox = cx + math.cos(ang) * s(40)
        oy = burst_cy + math.sin(ang) * s(40) * 0.85
        pygame.draw.polygon(big, GOLD_HI,
                            [(int(cx + math.cos(ang + 0.13) * s(20)),
                              int(burst_cy + math.sin(ang + 0.13) * s(20) * 0.85)),
                             (int(ox), int(oy)),
                             (int(cx + math.cos(ang - 0.13) * s(20)),
                              int(burst_cy + math.sin(ang - 0.13) * s(20) * 0.85))])

    # Body — flat gold with thick outline
    body_cy = cy + s(10)
    body_w = s(46)
    body_h = s(22)
    pygame.draw.ellipse(big, BLACK,
                        (cx - body_w // 2 - OUT_W,
                         body_cy - body_h // 2 - OUT_W,
                         body_w + 2 * OUT_W, body_h + 2 * OUT_W))
    pygame.draw.ellipse(big, GOLD,
                        (cx - body_w // 2, body_cy - body_h // 2,
                         body_w, body_h))
    # Shadow side (right half) — flat darker gold
    s_ovr = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.ellipse(s_ovr, (*GOLD_DK, 200),
                        (cx, body_cy - body_h // 2,
                         body_w // 2, body_h))
    big.blit(s_ovr, (0, 0))
    # Halftone dots on the shadow side
    for dx in range(s(2), body_w // 2, s(3)):
        for dy in range(-body_h // 2 + s(2), body_h // 2 - s(1), s(3)):
            pygame.draw.circle(big, BLACK,
                               (cx + dx, body_cy + dy), max(1, s(1) // 2))
    # Re-stroke ellipse outline
    pygame.draw.ellipse(big, BLACK,
                        (cx - body_w // 2, body_cy - body_h // 2,
                         body_w, body_h), OUT_W)
    # Bright highlight stripe
    pygame.draw.line(big, GOLD_HI,
                     (cx - body_w // 2 + s(6), body_cy - s(6)),
                     (cx - s(4), body_cy - s(8)),
                     max(3, s(1) + s(1) // 2))

    # Spout — exaggerated curl, thick outline
    sp_x = cx + s(18)
    sp_y = body_cy - s(4)
    sp_pts = [
        (sp_x,           sp_y + s(6)),
        (sp_x + s(10),   sp_y - s(2)),
        (sp_x + s(16),   sp_y - s(14)),
        (sp_x + s(10),   sp_y - s(24)),    # extreme curl
        (sp_x - s(2),    sp_y - s(20)),
        (sp_x + s(2),    sp_y - s(14)),
        (sp_x + s(6),    sp_y - s(8)),
        (sp_x + s(4),    sp_y),
        (sp_x - s(2),    sp_y + s(4)),
    ]
    pygame.draw.polygon(big, BLACK, sp_pts)
    inset = [(p[0] - (s(1) if p[0] < sp_x + s(7) else 0),
              p[1] + (s(1) if p[1] > sp_y - s(8) else 0))
             for p in sp_pts]
    pygame.draw.polygon(big, GOLD, sp_pts)
    pygame.draw.polygon(big, BLACK, sp_pts, OUT_W)

    # Handle — thick black outlined ring
    h_cx = cx - s(22)
    h_cy = body_cy
    h_w  = s(12)
    h_h  = s(20)
    pygame.draw.ellipse(big, BLACK,
                        (h_cx - h_w // 2 - OUT_W,
                         h_cy - h_h // 2 - OUT_W,
                         h_w + 2 * OUT_W, h_h + 2 * OUT_W))
    pygame.draw.ellipse(big, GOLD,
                        (h_cx - h_w // 2, h_cy - h_h // 2, h_w, h_h))
    pygame.draw.ellipse(big, SKY,
                        (h_cx - h_w // 2 + s(3), h_cy - h_h // 2 + s(3),
                         h_w - s(6), h_h - s(6)))
    pygame.draw.ellipse(big, BLACK,
                        (h_cx - h_w // 2 + s(3), h_cy - h_h // 2 + s(3),
                         h_w - s(6), h_h - s(6)), OUT_W)
    pygame.draw.ellipse(big, BLACK,
                        (h_cx - h_w // 2, h_cy - h_h // 2, h_w, h_h), OUT_W)

    # Big ruby gem on body
    pygame.draw.polygon(big, BLACK,
                        [(cx, body_cy - s(7)),
                         (cx + s(7), body_cy),
                         (cx, body_cy + s(7)),
                         (cx - s(7), body_cy)])
    pygame.draw.polygon(big, RUBY,
                        [(cx, body_cy - s(5)),
                         (cx + s(5), body_cy),
                         (cx, body_cy + s(5)),
                         (cx - s(5), body_cy)])
    aa_circle(big, WHITE, cx - s(2), body_cy - s(2), max(1, s(1)))

    # Smoke — flat puffs with outlines (comic style)
    for i, (dx_, dy_, r) in enumerate([(s(0), -s(28), s(5)),
                                        (s(4), -s(36), s(4)),
                                        (-s(4), -s(44), s(3)),
                                        (s(2), -s(52), s(2))]):
        cx_p = sp_x + s(4) + dx_
        cy_p = sp_y - s(24) + dy_
        pygame.draw.circle(big, BLACK, (cx_p, cy_p), r + OUT_W)
        pygame.draw.circle(big, SMOKE, (cx_p, cy_p), r)


# ─────────────────────────────────────────────────────────────────────────────
# "ORIGINAL" — re-creates the in-game _draw_genie_icon recipe at the
# same higher resolution so it lines up next to the candidates.
# ─────────────────────────────────────────────────────────────────────────────

def draw_lamp_original(big, cx, cy):
    BRASS_DK = ( 95,  60,  18)
    BRASS    = (185, 130,  45)
    BRASS_HI = (250, 215, 130)
    SMOKE_DK = ( 95,  60, 110)
    SMOKE    = (170, 130, 195)
    SMOKE_HI = (220, 200, 240)
    NEAR_BLK = ( 18,  14,  10)

    # Original used 44×44 with SS=5; here we render the same shapes
    # at 88×88 ×6 so it sits next to candidates at matching scale.
    body_cx = cx
    body_cy = cy + s(8)
    body_w  = s(48)
    body_h  = s(24)
    body_rect = pygame.Rect(0, 0, body_w, body_h)
    body_rect.center = (body_cx, body_cy)
    pygame.draw.ellipse(big, NEAR_BLK, body_rect.inflate(SS, SS))
    pygame.draw.ellipse(big, BRASS_DK, body_rect)
    inner = body_rect.inflate(-int(SS * 1.5), -int(SS * 1.5))
    pygame.draw.ellipse(big, BRASS, inner)
    hi = pygame.Rect(0, 0, int(body_w * 0.55), int(body_h * 0.30))
    hi.center = (body_cx - int(body_w * 0.06),
                 body_cy - int(body_h * 0.22))
    pygame.draw.ellipse(big, BRASS_HI, hi)

    base = pygame.Rect(0, 0, int(body_w * 0.55), int(SS * 1.6))
    base.midtop = (body_cx, body_cy + body_h // 2 - SS)
    pygame.draw.rect(big, BRASS_DK, base, border_radius=SS // 2)

    spout_pts_outer = [
        (body_cx + int(body_w * 0.42), body_cy - int(body_h * 0.15)),
        (body_cx + int(body_w * 0.70), body_cy - int(body_h * 0.55)),
        (body_cx + int(body_w * 0.88), body_cy - int(body_h * 0.95)),
        (body_cx + int(body_w * 0.80), body_cy - int(body_h * 1.10)),
        (body_cx + int(body_w * 0.62), body_cy - int(body_h * 0.78)),
        (body_cx + int(body_w * 0.42), body_cy - int(body_h * 0.45)),
    ]
    pygame.draw.polygon(big, NEAR_BLK, spout_pts_outer)
    inset_pts = [
        (body_cx + int(body_w * 0.45), body_cy - int(body_h * 0.20)),
        (body_cx + int(body_w * 0.68), body_cy - int(body_h * 0.55)),
        (body_cx + int(body_w * 0.83), body_cy - int(body_h * 0.92)),
        (body_cx + int(body_w * 0.78), body_cy - int(body_h * 1.03)),
        (body_cx + int(body_w * 0.62), body_cy - int(body_h * 0.75)),
        (body_cx + int(body_w * 0.45), body_cy - int(body_h * 0.45)),
    ]
    pygame.draw.polygon(big, BRASS, inset_pts)
    pygame.draw.line(big, BRASS_HI,
                     (body_cx + int(body_w * 0.50), body_cy - int(body_h * 0.30)),
                     (body_cx + int(body_w * 0.78), body_cy - int(body_h * 0.90)),
                     max(1, SS // 2))

    handle_cx = body_cx - int(body_w * 0.55)
    handle_cy = body_cy - int(body_h * 0.15)
    handle_w = int(body_w * 0.30)
    handle_h = int(body_h * 0.85)
    handle_outer = pygame.Rect(0, 0, handle_w, handle_h)
    handle_outer.center = (handle_cx, handle_cy)
    pygame.draw.ellipse(big, NEAR_BLK, handle_outer)
    pygame.draw.ellipse(big, BRASS, handle_outer.inflate(-int(SS * 1.2),
                                                          -int(SS * 1.2)))
    cutout = handle_outer.inflate(-int(SS * 3.5), -int(SS * 3.5))
    pygame.draw.ellipse(big, SKY, cutout)
    pygame.draw.ellipse(big, BRASS_DK, cutout, max(1, SS // 2))

    plume_origin_x = body_cx + int(body_w * 0.80)
    plume_origin_y = body_cy - int(body_h * 1.10)
    smoke_ribbon(big, plume_origin_x, plume_origin_y,
                 [SMOKE_HI, SMOKE, SMOKE_DK],
                 n_puffs=10, height_n=30, curl=1.5)
    aa_circle(big, BRASS_HI, body_cx + int(body_w * 0.95),
              body_cy - int(body_h * 0.50), max(2, SS // 2) + SS // 3)
    aa_circle(big, (255, 255, 230), body_cx + int(body_w * 0.95),
              body_cy - int(body_h * 0.50), max(2, SS // 2))


# ─────────────────────────────────────────────────────────────────────────────
LAMPS = [
    ("Original (current)",   draw_lamp_original),
    ("1: Aladdin classic",   draw_lamp_1_aladdin),
    ("2: Persian ornate",    draw_lamp_2_persian),
    ("3: Steampunk brass",   draw_lamp_3_steampunk),
    ("4: Cosmic crystal",    draw_lamp_4_cosmic),
    ("5: Comic-book pop",    draw_lamp_5_comic),
]


def render_one(fn):
    big = pygame.Surface((PW, PH), pygame.SRCALPHA)
    big.fill(SKY)
    cx = PW // 2
    cy = PH // 2
    fn(big, cx, cy)
    out_w = W * DISPLAY_SCALE
    out_h = H * DISPLAY_SCALE
    return pygame.transform.smoothscale(big, (out_w, out_h))


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "v1"
    DW = W * DISPLAY_SCALE
    DH = H * DISPLAY_SCALE
    cols, rows = 3, 2
    margin = 14
    label_h = 26
    sheet_w = DW * cols + margin * (cols + 1)
    sheet_h = (DH + label_h + margin) * rows + margin
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 24, 32))
    font = pygame.font.SysFont("Arial", 16, bold=True)
    for i, (label, fn) in enumerate(LAMPS):
        col, row = i % cols, i // cols
        portrait = render_one(fn)
        x = margin + col * (DW + margin)
        y = margin + row * (DH + label_h + margin)
        pygame.draw.rect(sheet, (60, 65, 80),
                         (x - 2, y - 2, DW + 4, DH + 4), 2)
        sheet.blit(portrait, (x, y))
        text = font.render(label, True, (240, 240, 240))
        sheet.blit(text, (x + (DW - text.get_width()) // 2,
                          y + DH + 4))
        # Individual portrait
        if i == 0:
            ind_path = os.path.join(OUT_DIR, f"lamp_original_{tag}.png")
        else:
            ind_path = os.path.join(OUT_DIR, f"lamp_{i}_{tag}.png")
        pygame.image.save(portrait, ind_path)
    out = os.path.join(OUT_DIR, f"lamp_sheet_{tag}.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
