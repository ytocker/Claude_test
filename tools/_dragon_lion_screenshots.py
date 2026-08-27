"""One real gameplay frame each of the dragon and lion marquee acts.

Dev-only — same headless real-draw-path technique as weekend_filmstrips.py,
but forces `foreground_near_lane._MARQUEE` instead of leaving it to the
per-run coin flip, so both siblings can be captured on demand rather than
waited for.

    SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/_dragon_lion_screenshots.py
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y                      # noqa: E402
from game import biome as _biome                            # noqa: E402
from game import foreground                                 # noqa: E402
from game import foreground_near_lane as _near               # noqa: E402
from tools._family_showcase import _draw_pillars, _gold_coin  # noqa: E402
from tools.weekend_filmstrips import (                       # noqa: E402
    CYCLE, _wetness, _snow_cover, _build_background_pre,
)
from game.sidewalk_crowd import SidewalkCrowd                # noqa: E402

# Mid-beat of the 10.5s dragon/lion act (_DRAGON_BEAT = (0.788, 0.818),
# beat starts at phase*CYCLE = 310.0s) — the same t the filmstrip sheet
# already uses for "THE DRAGON — parade, first flakes", so it's a
# pre-verified moment where the full procession is on screen.
T = 316.0


def _frame(marquee):
    phase = (T / CYCLE) % 1.0
    scroll = T * 160.0
    foreground.reset_street()
    _near._MARQUEE = marquee  # force the sibling instead of the coin flip
    crowd = SidewalkCrowd()
    foreground.set_crowd(crowd)
    sig = dict(clown_active=False, newbie_calm=False, score=int(T),
               near_misses=0, finale_active=False,
               wetness=_wetness(T), snow_cover=_snow_cover(T))
    foreground.set_world_signals(**sig)
    sc = scroll - 25.0 * 160.0
    for i in range(25 * 30):
        sc += 160.0 / 30.0
        crowd.update(sc, 160.0, 1.0 / 30.0, phase, T - 25.0 + i / 30.0)
    surf = pygame.Surface((W, H))
    pal = _biome.palette_for_phase(phase)
    for _ in range(2):
        foreground.draw_promenade(surf, scroll, pal, phase, T)
        foreground.draw_near_lane(surf, scroll, pal, phase, T)
    surf.fill((0, 0, 0))
    _build_background_pre(surf, scroll, phase, T, sig)
    _draw_pillars(surf, pal, phase, [(236, 300, 168)])
    _gold_coin(surf, 168, 300)
    foreground.draw_near_lane(surf, scroll, pal, phase, T)
    return surf


def main():
    out_dir = "docs/sidewalk_overhaul/festival"
    os.makedirs(out_dir, exist_ok=True)
    for marquee, name in (("dragon", "dragon_gameplay.png"),
                           ("lion", "lion_gameplay.png")):
        frame = _frame(marquee)
        # 2x upscale — the native 360x640 frame is too small to read the
        # procession detail in a screenshot.
        big = pygame.transform.smoothscale(frame, (W * 2, H * 2))
        path = os.path.join(out_dir, name)
        pygame.image.save(big, path)
        print("saved", path, big.get_size())


if __name__ == "__main__":
    main()
