import os, sys, math
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
import game.foreground as foreground
from game.foreground_floor import (_mix, _shade, _sat, _luma, _clamp, _nightf,
                                    _scatter, _flat_slab, _apply_grain_scroll)
from game.scenes import App

W, H, GROUND_Y = 360, 640, 595


def draw_erosion(surf, scroll, pal, phase):
    night = _nightf(pal)
    sandstone = _mix(pal.get('stone_dark', (95, 70, 55)), (206, 170, 124), 0.62)

    # (a) Smooth vertical value-gradient. Top matches the mountain-foot value so
    # the material reads as one continuous stone across the y=595 seam; the foot
    # cools + darkens as weathered paving further from the light.
    top_col = _shade(_sat(sandstone, 0.96), +6)
    bot_col = _shade(_sat(sandstone, 0.90), -20)
    # Night retints the whole plane cool+dark so it sits under the night sky.
    night_dk = (34, 42, 62)
    top_col = _mix(top_col, night_dk, 0.72 * night)
    bot_col = _mix(bot_col, _shade(night_dk, -8), 0.72 * night)
    _flat_slab(surf, W, H, GROUND_Y, top_col, bot_col, ease=1.0)

    # Gradient value at any screen-y, matching _flat_slab's linear fall — so
    # every carved mark reads as a value shift OF the stone it sits on, never a
    # foreign colour laid over it.
    depth = H - GROUND_Y
    span = max(1, depth - 1)

    def grad_at(y):
        t = (y - GROUND_Y) / span
        t = max(0.0, min(1.0, t))
        return _mix(top_col, bot_col, t)

    # Warm-lit contact lip AT y=595 — the topmost opaque row reads as a lit bevel
    # meeting the mountains, cooling toward night so nothing glows at the seam.
    lip = pygame.Surface((W, 1), pygame.SRCALPHA)
    lit = _mix(top_col, (255, 244, 224), 0.45)
    alpha = 60 * (1.0 - 0.55 * night)
    lip.fill((*lit, int(alpha)))
    surf.blit(lip, (0, GROUND_Y))

    # (b) Carved erosion runnels — vertical grooves cut by water down the foot.
    for sx, k, rng in _scatter(scroll, W, 1.0, 90, 0xF11):
        rw = rng.randint(2, 4)                      # 2..4px wide
        depth_dn = rng.randint(628, 632)            # runs to ~y=632
        for y in range(GROUND_Y, depth_dn):
            g = grad_at(y)
            # Value-only shadow darker than the surrounding gradient; deepens at
            # night. Waver over the length so the cut looks water-carved.
            core = _shade(g, -14 - int(6 * night))
            xoff = int(math.sin((y - GROUND_Y) / 15.0) * 1.0)
            gx = sx + xoff
            pygame.draw.line(surf, core, (gx, y), (gx + rw - 1, y))
            # Lit bevel on the LEFT edge so the groove catches the warm light.
            bevel = _shade(g, +10)
            surf.set_at((_clamp2(gx), y), bevel)

    # (c) Light scatter of shed grit — dense in the top ~10px, thinning to zero by
    # y=615, so the freshly weathered material collects just below the seam.
    for sx, k, rng in _scatter(scroll, W, 1.0, 5, 0xF22):
        sy = GROUND_Y + rng.randint(0, 20)
        if sy > 615:
            continue
        if sy > 605 and rng.random() < 0.5:
            continue                                # thin the y=605..615 band
        g = grad_at(sy)
        # Value-only fleck, contrast dropping toward night.
        d = rng.choice([-6, +6])
        d = int(d * (1.0 - 0.5 * night))
        surf.set_at((_clamp2(sx), sy), _shade(g, d))

    # (d) Subtle scroll-locked surface tooth over the whole foot.
    _apply_grain_scroll(surf, 0, GROUND_Y, W, 45, 3, scroll, 1.0)


def _clamp2(x):
    return max(0, min(W - 1, int(x)))


foreground.draw_foreground_floor = draw_erosion

OUT = "/home/user/skybit/docs/ground-redesign/sandstone-erosion-wash/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
app = App()
app._start_play()
app._render()
pygame.image.save(app.screen, OUT)
print(f"Saved: {OUT}")
