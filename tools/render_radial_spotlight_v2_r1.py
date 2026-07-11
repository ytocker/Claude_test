import sys
import os

# Headless so the same draw path runs on native + CI without a display.
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.animal_kitsune import build_kitsune

# 2x device resolution so the smoothscale down to 162x100 stays crisp.
W, H = 324, 200

# Legendary rarity palette.
gem = (255, 202, 104)
glow = (255, 168, 58)
deep = (150, 92, 22)


def render_card():
    # Near-black base keeps the glow reading as atmosphere, not a wash.
    card = pygame.Surface((W, H))
    card.fill((6, 6, 14))

    # Radial glow rises from the center-bottom so the art sits inside light.
    glow_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx, cy = W // 2, H * 3 // 4
    max_r = 150
    for r in range(max_r, 0, -2):
        # Superlinear fall-off keeps the bloom subtle, bright only at the core.
        alpha = int(55 * (1 - r / max_r) ** 1.5)
        pygame.draw.circle(glow_surf, (*glow, alpha), (cx, cy), r)
    card.blit(glow_surf, (0, 0))

    # Full-bleed art — prominent but proportional to the source 64x84.
    art = build_kitsune(0)
    art_h = int(H * 0.88)
    art_w = int(art_h * 64 / 84)
    art_big = pygame.transform.smoothscale(art, (art_w, art_h))
    ax = (W - art_w) // 2
    ay = H - art_h - 4
    card.blit(art_big, (ax, ay))

    # Faceted pip: the only geometry, a colorblind-safe rarity token.
    pip_cx, pip_cy = W - 14, 14
    pip_r = 9
    pts = [
        (pip_cx, pip_cy - pip_r),
        (pip_cx + pip_r, pip_cy),
        (pip_cx, pip_cy + pip_r),
        (pip_cx - pip_r, pip_cy),
    ]
    pygame.draw.polygon(card, gem, pts)
    pygame.draw.polygon(card, deep, pts, 1)

    # Floating labels ride the art with a hard dark shadow for legibility.
    fnt = pygame.font.SysFont("DejaVu Sans", 24, bold=True)
    shadow = (0, 0, 0)

    name_s = fnt.render("KITSUNE", True, (255, 255, 255))
    name_sh = fnt.render("KITSUNE", True, shadow)
    card.blit(name_sh, (10, H - 34 + 2))
    card.blit(name_s, (10, H - 34))

    price_s = fnt.render("3 500", True, gem)
    price_sh = fnt.render("3 500", True, shadow)
    px = W - price_s.get_width() - 10
    card.blit(price_sh, (px, H - 34 + 2))
    card.blit(price_s, (px, H - 34))

    return card


def main():
    out_dir = "/home/user/skybit/docs/item_card_redesign_v2/radial-spotlight"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")

    card = render_card()
    pygame.image.save(card, out_path)
    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
