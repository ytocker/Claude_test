import os, sys, math
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
import game.foreground as foreground
from game.foreground_floor import _mix, _shade, _sat, _luma, _clamp, _nightf, _scatter, _flat_slab
from game.scenes import App

W, H, GROUND_Y = 360, 640, 595


def draw_mist(surf, scroll, pal, phase):
    night = _nightf(pal)

    # (a) Opaque value-fall sandstone slab: solid ground beneath the haze so the
    # tinted band reads as atmosphere over a real surface, not a see-through wash.
    sandstone = _mix(pal.get('stone_dark', (95, 70, 55)), (206, 170, 124), 0.62)
    top = _shade(_sat(sandstone, 0.94), -18)          # darker/cooler at the seam
    bot = _shade(sandstone, 14)                        # warmer/lighter at the foot
    _flat_slab(surf, W, H, GROUND_Y, top, bot, ease=0.95)
    sandstone_front = bot

    # (b) Tinted mist band — a dusty warm-sand haze, NEVER white. It cools and
    # thins toward night so the mountain silhouettes above stay legible after
    # dark instead of being buried under a bright fog.
    mist_day = _mix(pal.get('horizon', (220, 210, 190)),
                    pal.get('sky_bot', (160, 195, 230)), 0.4)
    mist_color = _mix(mist_day, (46, 54, 74), night)
    band_h = 28
    haze_surf = pygame.Surface((W, band_h), pygame.SRCALPHA)
    inv = 1.0 / (band_h - 1)
    for dy in range(band_h):
        base_a = 120 * (1.0 - dy * inv) * (1.0 - 0.45 * night)
        for x in range(W):
            # World-locked density wave: the haze breathes thicker/thinner in
            # slow rolls anchored to world-x, so it drifts with the scroll rather
            # than shimmering in screen space.
            wave = 20.0 * math.sin((x + scroll) / 220.0 * 2 * math.pi)
            a = int(_clamp(base_a + wave))
            haze_surf.set_at((x, dy), (*mist_color, a))
    surf.blit(haze_surf, (0, GROUND_Y))

    # (c) 1px warm-lit contact lip at the seam: the topmost opaque row reads as a
    # softly lit bevel meeting the mountains; cools/darkens toward night so it
    # never glows at the seam after dark.
    lit = _mix(sandstone_front, (255, 244, 224), 0.45)
    lit = _mix(lit, _shade(sandstone_front, -10), night)
    lip = pygame.Surface((W, 1), pygame.SRCALPHA)
    lip.fill((*lit, 60))
    surf.blit(lip, (0, GROUND_Y))

    # (d) Faint value-only ground mottle below the haze so the exposed lower slab
    # carries a little tooth without introducing colour noise.
    for sx, k, rng in _scatter(scroll, W, 1.0, 60, 0xC44):
        d = rng.randint(-5, 5)
        y = rng.randint(624, H - 2)
        col = _shade(sandstone_front, d)
        surf.set_at((int(sx) % W, y), col)


foreground.draw_foreground_floor = draw_mist

OUT = "/home/user/skybit/docs/ground-redesign/lowland-mist-shelf/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
app = App()
app._start_play()
app._render()
pygame.image.save(app.screen, OUT)
print(f"Saved: {OUT}")
