"""Standalone card-render helpers — no game module dependencies.

soft_glow and coin_glyph extracted for use by render_*_v5_r*.py scripts.
"""
import math
import pygame


def soft_glow(surf, cx, cy, radius, color, peak_alpha, layers=8):
    """Feathered additive glow — many layers for smooth falloff."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak_alpha * (1 - (i - 1) / layers) ** 1.8)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


def coin_glyph(surf, cx, cy, r):
    """Procedural gold coin face — rope-rim, gradient body, specular highlight."""
    d = max(2, int(r * 2))
    coin = pygame.Surface((d + 4, d + 4), pygame.SRCALPHA)
    cc = (d + 4) // 2
    rr = d // 2

    OUTLINE_DK = (95, 50, 0)
    OUTLINE_LT = (150, 90, 10)
    GOLD_HI    = (255, 232, 130)
    GOLD_MID   = (240, 195, 55)
    GOLD_LO    = (190, 130, 20)

    # Outline rings
    pygame.draw.circle(coin, OUTLINE_DK, (cc, cc), rr)
    if rr > 2:
        pygame.draw.circle(coin, OUTLINE_LT, (cc, cc), rr - 1)

    # Gradient body
    r_body = max(1, rr - max(1, rr // 5))
    y0, y1 = cc - r_body, cc + r_body
    for yy in range(y0, y1 + 1):
        t = (yy - y0) / max(1, y1 - y0)
        if t < 0.4:
            col = tuple(int(GOLD_HI[k] * (1 - t / 0.4) + GOLD_MID[k] * (t / 0.4)) for k in range(3))
        else:
            tt = (t - 0.4) / 0.6
            col = tuple(int(GOLD_MID[k] * (1 - tt) + GOLD_LO[k] * tt) for k in range(3))
        half = int(math.sqrt(max(0, r_body * r_body - (yy - cc) ** 2)))
        if half > 0:
            pygame.draw.line(coin, col, (cc - half, yy), (cc + half, yy))

    # Rope rim: alternating dark/light segments
    N_ROPE = 24
    rim_r  = rr - 1
    rim_w  = max(1, rim_r // 5)
    for i in range(N_ROPE):
        ang_s = 2 * math.pi * i / N_ROPE
        ang_e = 2 * math.pi * (i + 1) / N_ROPE
        col   = OUTLINE_LT if i % 2 == 0 else OUTLINE_DK
        n_pts = 4
        pts   = []
        for j in range(n_pts + 1):
            a = ang_s + (ang_e - ang_s) * j / n_pts
            pts.append((int(cc + math.cos(a) * (rim_r - rim_w)),
                        int(cc + math.sin(a) * (rim_r - rim_w))))
        for j in range(n_pts, -1, -1):
            a = ang_s + (ang_e - ang_s) * j / n_pts
            pts.append((int(cc + math.cos(a) * rim_r),
                        int(cc + math.sin(a) * rim_r)))
        if len(pts) >= 3:
            pygame.draw.polygon(coin, col, pts)

    # Specular highlight top-left
    if rr >= 4:
        hl = pygame.Surface((d + 4, d + 4), pygame.SRCALPHA)
        hl_r = max(1, rr // 2)
        hcx = cc - rr // 4
        hcy = cc - rr // 4
        pygame.draw.circle(hl, (255, 248, 200, 120), (hcx, hcy), hl_r)
        coin.blit(hl, (0, 0))

    surf.blit(coin, coin.get_rect(center=(cx, cy)))


def real_coin_icon(surf, cx, cy, r=10):
    """Replica of game/hud._coin_icon: dark rim + gold body + embossed parrot glyph."""
    COIN_GOLD = (255, 210,  20)
    COIN_DARK = (200, 140,   0)
    EMBOSS    = (140,  85,   0)
    s = r / 10  # scale from reference r=10
    pygame.draw.circle(surf, COIN_DARK, (cx, cy), r + 1)
    pygame.draw.circle(surf, COIN_GOLD, (cx, cy), r)
    ew = max(1, round(7 * s))
    eh = max(1, round(5 * s))
    pygame.draw.ellipse(surf, EMBOSS, (cx - round(2*s), cy - round(1*s), ew, eh))
    pygame.draw.circle(surf, EMBOSS, (cx - round(s), cy - round(3*s)), max(1, round(3*s)))
    pygame.draw.polygon(surf, EMBOSS, [
        (cx - round(3*s), cy - round(3*s)),
        (cx - round(6*s), cy - round(2*s)),
        (cx - round(3*s), cy - round(s)),
    ])
    pygame.draw.circle(surf, COIN_GOLD, (cx, cy - round(4*s)), 1)
