"""One real gameplay frame each of the dragon and lion marquee acts.

Dev-only — same headless real-draw-path technique as weekend_filmstrips.py.
Both acts are now unconditional per-run beats (`_DRAGON_BEAT`/`_LION_BEAT` in
foreground_near_lane.py), so each is simply captured at its own real
timestamp through the live `_festival_bill` dispatch — no flag to force.

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
from tools._family_showcase import _draw_pillars, _gold_coin  # noqa: E402
from tools.weekend_filmstrips import (                       # noqa: E402
    CYCLE, _wetness, _snow_cover, _build_background_pre,
)
from game.sidewalk_crowd import SidewalkCrowd                # noqa: E402

# _LION_BEAT = (0.762, 0.774) starts at 299.8s, dur 6.0s -> mid-beat ~302.8s.
# _DRAGON_BEAT = (0.788, 0.818) starts at 310.0s, dur 10.5s; 316.0s is the
# same mid-beat moment the filmstrip sheet already uses for "THE DRAGON —
# parade, first flakes", a pre-verified frame with the full procession on
# screen.
TIMES = {"lion": 302.8, "dragon": 316.0}


def _frame(t):
    phase = (t / CYCLE) % 1.0
    scroll = t * 160.0
    foreground.reset_street()
    crowd = SidewalkCrowd()
    foreground.set_crowd(crowd)
    sig = dict(clown_active=False, newbie_calm=False, score=int(t),
               near_misses=0, finale_active=False,
               wetness=_wetness(t), snow_cover=_snow_cover(t))
    foreground.set_world_signals(**sig)
    sc = scroll - 25.0 * 160.0
    for i in range(25 * 30):
        sc += 160.0 / 30.0
        crowd.update(sc, 160.0, 1.0 / 30.0, phase, t - 25.0 + i / 30.0)
    surf = pygame.Surface((W, H))
    pal = _biome.palette_for_phase(phase)
    for _ in range(2):
        foreground.draw_promenade(surf, scroll, pal, phase, t)
        foreground.draw_near_lane(surf, scroll, pal, phase, t)
    surf.fill((0, 0, 0))
    _build_background_pre(surf, scroll, phase, t, sig)
    _draw_pillars(surf, pal, phase, [(236, 300, 168)])
    _gold_coin(surf, 168, 300)
    foreground.draw_near_lane(surf, scroll, pal, phase, t)
    return surf


def main():
    out_dir = "docs/sidewalk_overhaul/festival"
    os.makedirs(out_dir, exist_ok=True)
    for marquee, name in (("dragon", "dragon_gameplay.png"),
                           ("lion", "lion_gameplay.png")):
        frame = _frame(TIMES[marquee])
        # 2x upscale — the native 360x640 frame is too small to read the
        # procession detail in a screenshot.
        big = pygame.transform.smoothscale(frame, (W * 2, H * 2))
        path = os.path.join(out_dir, name)
        pygame.image.save(big, path)
        print("saved", path, big.get_size())


if __name__ == "__main__":
    main()
