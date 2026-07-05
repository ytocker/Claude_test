"""Render the DESIGN 2 (BIRTHDAY CROWN) review sheet — round 2. SCRATCH ONLY.

Proves the reseated crown: band caps the dome above the eye line, five points
fan up into clear sky, gems read at 40px. Gameplay DAY + NIGHT + hero + store
icon + a NEAREST 40px truth read, all composited the same way as round 1.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from tools.ninja_render import gameplay_panel, hero_panel  # noqa: E402
from tools.partyhat_candidates import design_2 as d        # noqa: E402
from game import biome                                      # noqa: E402

FONT = pygame.font.SysFont("sans", 16, bold=True)
SMALL = pygame.font.SysFont("sans", 13)


def label(surf, text, x, y, col=(235, 232, 245)):
    surf.blit(SMALL.render(text, True, col), (x, y))


def truth_read(panel, size=40):
    w, h = panel.get_size()
    sw, sh = (size, max(1, int(size * h / w))) if w >= h else \
             (max(1, int(size * w / h)), size)
    small = pygame.transform.smoothscale(panel, (sw, sh))
    return pygame.transform.scale(small, (w, h))


def main():
    GP_W, GP_H = 196, 290
    HERO = 250
    pad = 18
    title_h = 42

    day = gameplay_panel(d.build, GP_W, GP_H)

    # Night: the harness reads palette_for_phase(0.0); temporarily map it to a
    # night phase so the same scene renders under dark navy sky.
    _orig = biome.palette_for_phase
    biome.palette_for_phase = lambda _p: _orig(0.62)
    try:
        night = gameplay_panel(d.build, GP_W, GP_H)
    finally:
        biome.palette_for_phase = _orig

    hero = hero_panel(d.build, HERO, tilt=0.0)
    truth = truth_read(day, 40)

    # Hero on its own card.
    hero_box = pygame.Surface((HERO, GP_H), pygame.SRCALPHA)
    pygame.draw.rect(hero_box, (22, 20, 32), hero_box.get_rect(), border_radius=14)
    hero_box.blit(hero, hero.get_rect(center=(HERO // 2, GP_H // 2)))

    # Store icon cropped to content on a card.
    icon = d.icon
    ib = icon.get_bounding_rect()
    icon_c = icon.subsurface(ib).copy() if ib.width else icon
    icon_box = pygame.Surface((HERO, GP_H), pygame.SRCALPHA)
    pygame.draw.rect(icon_box, (30, 28, 42), icon_box.get_rect(), border_radius=14)
    isc = (min(HERO, GP_H) * 0.78) / max(icon_c.get_width(), icon_c.get_height())
    icon_s = pygame.transform.smoothscale(
        icon_c, (int(icon_c.get_width() * isc), int(icon_c.get_height() * isc)))
    icon_box.blit(icon_s, icon_s.get_rect(center=(HERO // 2, GP_H // 2)))

    cols = [
        ("Gameplay - DAY", day),
        ("Gameplay - NIGHT", night),
        ("Hero product shot", hero_box),
        ("Store icon", icon_box),
        ("40px truth read", truth),
    ]
    W = pad
    for _, p in cols:
        W += p.get_width() + pad
    H = title_h + pad + GP_H + pad + 24
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 16, 26))

    sheet.blit(FONT.render(
        "DESIGN 2  BIRTHDAY CROWN  -  party hat redesign  (round 2: reseated cap)",
        True, (255, 210, 63)), (pad, 14))

    x = pad
    for lab, panel in cols:
        y = title_h + pad
        sheet.blit(panel, (x, y))
        label(sheet, lab, x, y + GP_H + 4)
        x += panel.get_width() + pad

    out = os.path.join(
        _ROOT, "docs/store_redesign/hats/partyhat/design_2/round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
