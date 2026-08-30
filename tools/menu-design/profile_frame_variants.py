"""Three PROFILE frame/tag placements, compared against the current (buggy)
build. Fork of launch_perch_start.py's draw_profile_frame — none of these
touch game/ or the shipped harness; they render standalone for comparison.

    PLACEMENT=A|B|C PYTHONHASHSEED=0 python3 tools/menu-design/profile_frame_variants.py
"""
import os
import sys
import types

_ROOT = "/home/user/skybit"
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HARNESS = os.path.join(_ROOT, "tools", "menu-design", "launch_perch_start.py")
_src = open(_HARNESS).read()
B = types.ModuleType("_launch_perch_head")
B.__file__ = _HARNESS
exec(compile(_src[:_src.index("def main():")], _HARNESS, "exec"), B.__dict__)

import pygame  # noqa: E402
_hud = B._hud
GOLD_MID, GOLD_BRIGHT, GOLD_PALE, GOLD_DEEP = B.GOLD_MID, B.GOLD_BRIGHT, B.GOLD_PALE, B.GOLD_DEEP


def _plate(surf, rect, label_dx=0):
    pygame.draw.rect(surf, GOLD_DEEP, rect, border_radius=8)
    pygame.draw.rect(surf, GOLD_MID, rect.inflate(-3, -3), border_radius=7)
    pygame.draw.line(surf, GOLD_PALE, (rect.left + 8, rect.top + 3),
                     (rect.right - 8, rect.top + 3), 1)
    pygame.draw.line(surf, (86, 60, 16), (rect.left + 8, rect.bottom - 3),
                     (rect.right - 8, rect.bottom - 3), 1)
    inset = rect.inflate(-8, -8)
    pygame.draw.rect(surf, (52, 34, 14), inset, border_radius=5)
    lx = inset.centerx - 7 + label_dx
    _hud._tracked_label(surf, "PROFILE", (lx, inset.centery + 1), 13,
                        color=(34, 20, 8), track=2, alpha=150)
    _hud._tracked_label(surf, "PROFILE", (lx, inset.centery), 13,
                        color=GOLD_PALE, track=2, alpha=250)
    _hud._profile_tri(surf, inset.right - 9, inset.centery, 4, GOLD_PALE)


def draw_A_sill(surf):
    """sill-plate — frame rests on the cloud's shoulder; tag hangs below on
    two strapped rings, 14px clear of Pip's real feet."""
    cot = B.house_cottage_rect()
    bird_r = pygame.Rect(B.PIP_CX - 31, int(B.PIP_CY) - 27, 64, 51)
    fr = pygame.Rect(23, 208, 118, 98)
    pygame.draw.rect(surf, GOLD_MID, fr, width=1, border_radius=13)
    pygame.draw.rect(surf, GOLD_BRIGHT, fr.inflate(-10, -10), width=1, border_radius=8)
    pygame.draw.line(surf, (*GOLD_PALE, 200), (fr.left + 14, fr.top + 2),
                     (fr.right - 14, fr.top + 2), 1)

    plate = pygame.Rect(0, 0, 110, 28)
    plate.midtop = (104, fr.bottom + 18)
    for sx in (78, 130):
        pygame.draw.line(surf, GOLD_MID, (sx, fr.bottom), (sx, plate.top), 3)
        B.nail(surf, sx, fr.bottom + 2)
        B.nail(surf, sx, plate.top - 2)
    _plate(surf, plate)
    return fr.union(plate)


def draw_B_straddle(surf):
    """portrait-straddle — frame encloses house+Pip+cloud (42px Pip
    clearance); tag straddles the bottom rail museum-plate style. The left
    rope crosses the rail at (42,334) and is claimed as a hanging point with
    an iron ring rather than hidden."""
    fr = pygame.Rect(23, 208, 145, 126)
    pygame.draw.rect(surf, GOLD_MID, fr, width=1, border_radius=13)
    pygame.draw.rect(surf, GOLD_BRIGHT, fr.inflate(-10, -10), width=1, border_radius=8)
    pygame.draw.line(surf, (*GOLD_PALE, 200), (fr.left + 14, fr.top + 2),
                     (fr.right - 14, fr.top + 2), 1)
    B._iron_ring(surf, 42, fr.bottom, 4)

    plate = pygame.Rect(0, 0, 108, 28)
    plate.center = (102, fr.bottom)
    _plate(surf, plate)
    return fr.union(plate)


def draw_C_crown(surf):
    """header-cartouche — open-bottom frame (two legs, no rail to clip Pip
    against at all); tag crowns the top rail instead."""
    top, left, right, leg_bot = 204, 23, 141, 312
    pygame.draw.line(surf, GOLD_MID, (left, top), (right, top), 2)
    pygame.draw.line(surf, (*GOLD_PALE, 200), (left + 10, top + 3), (right - 10, top + 3), 1)
    for lx in (left, right):
        pygame.draw.line(surf, GOLD_MID, (lx, top), (lx, leg_bot), 2)
        pygame.draw.circle(surf, GOLD_BRIGHT, (lx, leg_bot), 4)
        pygame.draw.circle(surf, GOLD_PALE, (lx, leg_bot), 2)

    plate = pygame.Rect(0, 0, 120, 30)
    plate.center = (82, top - 2)
    _plate(surf, plate)
    return pygame.Rect(left, plate.top, right - left, leg_bot - plate.top)


VARIANTS = {"A": draw_A_sill, "B": draw_B_straddle, "C": draw_C_crown,
            "current": B.draw_profile_frame}


def build(phase, fn):
    from game.scenes import App, STATE_MENU
    from game.world import World
    from game import biome as _biome
    from game import foreground
    from game.config import W, H
    import random

    app = App()
    app._cooldown_t = 0.0
    app._fetch_pending = False
    app.state = STATE_MENU
    app.world = World()
    for _ in range(40):
        app.world.world_idle_tick(1 / 60)
    app.world.biome_time = phase * _biome.CYCLE_SECONDS
    app.world.weather.wetness = 0.0
    app.world.bird.frame_t = 0.0
    app.world.bird.x = B.PIP_CX
    app.world.bird.y = B.PIP_CY

    pal = _biome.palette_for_phase(phase)
    surf = app.screen
    app._draw_background(surf)
    foreground.draw_near_lane(surf, app.world.bg_scroll, pal, 0.0,
                              app.world.biome_time)
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 110))
    surf.blit(dim, (0, 0))
    rng = random.Random(42)
    stars = [(rng.randint(8, W - 8), rng.randint(8, H - 180),
              rng.choice((1, 1, 1, 2)), rng.uniform(0, 6.28))
             for _ in range(38)]
    _hud._draw_overlay_stars(surf, stars, 0.0)
    _hud._draw_mountain_silhouette(surf, alpha=180)
    house = B._intro.get_sprite("skyhouse_post")
    surf.blit(house, B.house_topleft())
    app.world.bird.draw(surf)
    chain = B.draw_signchain(surf)
    tails = chain.pop("_tails")
    B.draw_start_B(surf, tails)
    fr = fn(surf)
    _hud._outlined_text(surf, "SKYBIT", (W // 2, 112), size=72, px=3,
                        shadow_offset=(2, 3))
    _hud._outlined_text(surf, "POCKET  SKY  FLYER", (W // 2, 168),
                        size=20, px=2, shadow_offset=(1, 2))
    return surf, fr


if __name__ == "__main__":
    which = os.environ.get("PLACEMENT", "A")
    out = os.environ.get("OUT", f"/tmp/_pf_{which}.png")
    phase = float(os.environ.get("PHASE", "0.20"))
    surf, fr = build(phase, VARIANTS[which])
    pygame.image.save(surf, out)
    print("saved", out, "frame/tag union:", fr)
