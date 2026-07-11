"""Radial-spotlight store-card concept (item-card redesign v2, round 2).

A zero-structure take: no bars, no trays. The item sits inside a soft radial
bloom and the rarity is carried by a single faceted pip badge, top-right.
Authored at 2x (324x200) and smoothscaled to the live 162x100 for validation.
Review-only; not wired into the live store.

Round-2 folds in art-director notes:
  - Lift the card base off the obsidian store bg so the silhouette reads, plus
    a 1px inset rarity border as a subtle frame.
  - Promote the pip to a proper badge: a deep-amber plate behind a larger
    faceted diamond so the rarity token stops vanishing at 1x.
  - Clamp the glow low and tight so it lights the base plate under the art
    rather than washing through the kitsune and tinting it.
  - Give the pip a non-colour signal: an inner facet diamond that survives a
    colourblind desaturation.
"""
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
CORNER = 16

# Legendary rarity palette.
gem = (255, 202, 104)
glow = (255, 168, 58)
deep = (150, 92, 22)
plate = (100, 60, 14)   # deep-amber badge plate seats the pip as a token


def _rounded(surf, radius):
    """Clip to rounded corners without touching interior pixels."""
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), surf.get_rect(),
                     border_radius=radius)
    out = surf.convert_alpha()
    out.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return out


def _diamond(cx, cy, r):
    return [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]


def render_card():
    # Base lifted well off the obsidian store bg (8,8,24) so the card
    # silhouette stays visible against the grid, while still dark enough to let
    # the glow read as atmosphere.
    card = pygame.Surface((W, H))
    card.fill((18, 16, 26))

    # Radial glow clamped low and tight: it lights the base plate under the art
    # instead of washing through the silhouette and tinting the kitsune.
    glow_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx, cy = 162, 190
    max_r = 110
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

    # Rarity badge: a deep-amber plate seats a faceted pip so the token reads
    # as a proper badge, not a floating speck. Top-right, clear of the corner.
    plate_sz = 36
    plate_x = W - plate_sz - 8
    plate_y = 8
    pygame.draw.rect(card, plate, (plate_x, plate_y, plate_sz, plate_sz))

    pip_cx = plate_x + plate_sz // 2
    pip_cy = plate_y + plate_sz // 2
    pip_r = 14
    pygame.draw.polygon(card, gem, _diamond(pip_cx, pip_cy, pip_r))
    pygame.draw.polygon(card, deep, _diamond(pip_cx, pip_cy, pip_r), 1)
    # Inner facet: a non-colour shape signal that survives a colourblind filter.
    facet_r = int(pip_r * 0.6)
    pygame.draw.polygon(card, deep, _diamond(pip_cx, pip_cy, facet_r))

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

    # 1px inset rarity border: a subtle frame just inside the card edge that
    # reinforces the rarity read and crisps the silhouette.
    bordered = _rounded(card, CORNER)
    pygame.draw.rect(bordered, deep, (1, 1, W - 2, H - 2), 1,
                     border_radius=CORNER - 1)
    return bordered


def main():
    out_dir = "/home/user/skybit/docs/item_card_redesign_v2/radial-spotlight"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")

    card = render_card()
    pygame.image.save(card, out_path)
    print(f"saved {out_path} {card.get_size()}")


if __name__ == "__main__":
    main()
