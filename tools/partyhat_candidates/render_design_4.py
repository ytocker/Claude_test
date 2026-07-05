"""Render the DESIGN 4 (NYE Top Hat) review sheet — round 2. SCRATCH ONLY."""
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
from tools.partyhat_candidates import design_4  # noqa: E402
from game import biome  # noqa: E402


def _label(surf, text, x, y, col=(235, 235, 245)):
    font = pygame.font.SysFont("arial", 16, bold=True)
    surf.blit(font.render(text, True, col), (x, y))


def _truth_read(panel, size=40):
    w, h = panel.get_size()
    sw, sh = (size, max(1, int(size * h / w))) if w >= h else \
             (max(1, int(size * w / h)), size)
    small = pygame.transform.smoothscale(panel, (sw, sh))
    return pygame.transform.scale(small, (w, h))


def main():
    build = design_4.build
    icon = design_4.icon

    GW_P, GH_P = 168, 250
    HERO = 230
    GP = GH_P
    pad = 16
    title_h = 40

    day = gameplay_panel(build, GW_P, GH_P)

    # Night: override the phase the harness reads (it calls phase 0.0).
    _orig = biome.palette_for_phase
    biome.palette_for_phase = lambda _p: _orig(0.62)
    try:
        night = gameplay_panel(build, GW_P, GH_P)
    finally:
        biome.palette_for_phase = _orig

    hero = hero_panel(build, HERO, tilt=0.0)
    truth = _truth_read(night, 40)  # truth read on the make-or-break NIGHT crop

    bb = icon.get_bounding_rect()
    icon_c = icon.subsurface(bb).copy() if bb.width else icon
    icon_box = pygame.Surface((HERO, GP), pygame.SRCALPHA)
    pygame.draw.rect(icon_box, (30, 28, 42), icon_box.get_rect(), border_radius=14)
    sc = (min(HERO, GP) * 0.78) / max(icon_c.get_width(), icon_c.get_height())
    icon_s = pygame.transform.smoothscale(
        icon_c, (int(icon_c.get_width() * sc), int(icon_c.get_height() * sc)))
    icon_box.blit(icon_s, icon_s.get_rect(center=(HERO // 2, GP // 2)))

    hero_box = pygame.Surface((HERO, GP), pygame.SRCALPHA)
    hero_box.blit(hero, hero.get_rect(center=(HERO // 2, GP // 2)))

    cols = [
        ("Gameplay - DAY", day),
        ("Gameplay - NIGHT", night),
        ("Hero product shot", hero_box),
        ("Store icon", icon_box),
        ("40px truth (NIGHT)", truth),
    ]
    W = pad
    for _, p in cols:
        W += p.get_width() + pad
    H = title_h + pad + GP + pad + 24
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 16, 26))

    _label(sheet, "DESIGN 4  NYE TOP HAT  -  party hat redesign  (round 2)",
           pad, 12, (255, 210, 63))
    x = pad
    for label, panel in cols:
        y = title_h + pad
        sheet.blit(panel, (x, y))
        _label(sheet, label, x, y + GP + 4)
        x += panel.get_width() + pad

    out = os.path.join(_ROOT, "docs/store_redesign/hats/partyhat/design_4/round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
