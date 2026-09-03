"""Three size/position variants of the H `apron-step` connected frame — same
construction, deliberately larger and better-proportioned geometry.

The shipped H (23,198,138,110 / 54,296,107,40) is technically safe (17px real
Pip-silhouette margin) but lopsided: 44px of headroom above Pip against 17px
below, because the frame was grown just enough to stop clipping rather than
composed for balance. These three keep H's exact construction and grow/
reposition it, verified the same way (real Bird() mask, not the bbox, and the
same rope-anchor formula draw_signchain uses).

    OPTION=H1|H2|H3 python3 tools/menu-design/profile_frame_sized.py
    SHOWCASE=1      python3 tools/menu-design/profile_frame_sized.py
"""
import os
import sys

_ROOT = "/home/user/skybit"
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tools", "menu-design"))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame                                       # noqa: E402
import profile_frame_connected as C                  # noqa: E402
import profile_frame_variants as PF                  # noqa: E402

B = PF.B
_hud = B._hud
GOLD_MID, GOLD_BRIGHT, GOLD_PALE = C.GOLD_MID, C.GOLD_BRIGHT, C.GOLD_PALE
GOLD_SHADE = C.GOLD_SHADE
W, H = 360, 640

PRESETS = {
    # slug: (frame rect, apron rect, one-line thesis)
    "shipped": (pygame.Rect(23, 198, 138, 110), pygame.Rect(54, 296, 107, 40),
                "current — 17px Pip margin, 44px top / 17px bottom (lopsided)"),
    "H1": (pygame.Rect(18, 193, 146, 121), pygame.Rect(50, 304, 114, 34),
           "balanced — grown ~8% each way, margins evened out"),
    "H2": (pygame.Rect(14, 188, 152, 132), pygame.Rect(46, 308, 118, 38),
           "grand — the biggest of the three, most Pip headroom"),
    "H3": (pygame.Rect(20, 196, 144, 116), pygame.Rect(52, 300, 112, 36),
           "tallframe — closest to shipped's spacing, scaled up"),
}


def draw_apron(surf, fr, ap):
    """Identical construction to draw_H_apron, parametrized by geometry."""
    def shapes(s, c):
        pygame.draw.rect(s, c, fr, border_radius=13)
        pygame.draw.rect(s, c, ap, border_radius=13)

    C._body(surf, ap, 13, clip_top=fr.bottom - 2)
    surf.blit(C.union_outline(shapes, GOLD_MID, 2), (0, 0))
    C._sight(surf, fr.inflate(-8, -8), 8)
    pygame.draw.line(surf, GOLD_PALE, (ap.left + 12, fr.bottom + 2),
                     (ap.right - 10, fr.bottom + 2), 1)
    pygame.draw.line(surf, GOLD_SHADE, (ap.left + 12, ap.bottom - 3),
                     (ap.right - 10, ap.bottom - 3), 1)
    label_w, label_h = 88, 16
    label = pygame.Rect(0, 0, label_w, label_h)
    label.center = (ap.centerx + 4, ap.bottom - 14)
    C._label(surf, label)
    return fr.union(ap)


def build(phase, slug):
    fr, ap, _ = PRESETS[slug]
    from game.scenes import App, STATE_MENU
    from game.world import World
    from game import biome as _biome
    from game import foreground
    from game.config import W as GW, H as GH
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
    dim = pygame.Surface((GW, GH), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 110))
    surf.blit(dim, (0, 0))
    rng = random.Random(42)
    stars = [(rng.randint(8, GW - 8), rng.randint(8, GH - 180),
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
    if slug == "shipped":
        B.draw_profile_frame(surf)
    else:
        draw_apron(surf, fr, ap)
    _hud._outlined_text(surf, "SKYBIT", (GW // 2, 112), size=72, px=3,
                        shadow_offset=(2, 3))
    _hud._outlined_text(surf, "POCKET  SKY  FLYER", (GW // 2, 168),
                        size=20, px=2, shadow_offset=(1, 2))
    return surf


def verify(slug):
    import math
    from game.entities import Bird
    fr, ap, _ = PRESETS[slug]
    b = Bird(); b.frame_t = 0.0
    pip_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    b.draw(pip_surf, 0, 0)
    mask = pygame.mask.from_surface(pip_surf, threshold=8)
    opaque = [(x, y) for x in range(50, 140) for y in range(230, 300)
             if mask.get_at((x, y))]
    outside = [p for p in opaque if not fr.collidepoint(p)]
    if outside:
        return {"clip_px": len(outside)}
    margin = min(min(x - fr.left for x, y in opaque),
                min(fr.right - x for x, y in opaque),
                min(y - fr.top for x, y in opaque),
                min(fr.bottom - y for x, y in opaque))

    def rope_x(sgn, y):
        ax = 42 if sgn < 0 else 174
        cx, cy, ang, w, h = 102, 386, -3.0, 172, 44
        rad = math.radians(-ang)
        ox = sgn * (w * 0.36)
        hx = cx + ox * math.cos(rad); hy = cy + ox * math.sin(rad) - h * 0.5
        t = (y - 316) / (hy - 316); return ax + t * (hx - ax)

    worst_rope = float("inf")
    y0 = max(ap.top, 316)
    for y in range(y0, ap.bottom + 1, 2):
        worst_rope = min(worst_rope, ap.left - rope_x(-1, y), rope_x(1, y) - ap.right)
    return dict(pip_margin=margin, subtitle_clear=fr.top - 178,
               right_unused=168 - max(fr.right, ap.right),
               rope_clear=worst_rope, store_clear=359 - ap.bottom)


if __name__ == "__main__":
    if os.environ.get("SHOWCASE"):
        F = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
        fh = pygame.font.Font(F, 20); fl = pygame.font.Font(F, 15); fs = pygame.font.Font(F, 12)
        order = ["shipped", "H1", "H2", "H3"]
        CW, CH = W, H
        PAD, GAP, LAB, HEAD = 22, 14, 46, 50
        n = len(order)
        sw = PAD * 2 + n * CW + (n - 1) * GAP
        sh = PAD * 2 + HEAD + CH + LAB
        sheet = pygame.Surface((sw, sh)); sheet.fill((17, 17, 23))
        sheet.blit(fh.render("SKYBIT · PROFILE frame · size + position, same H construction",
                             True, (228, 204, 134)), (PAD, PAD))
        sheet.blit(fs.render("apron-step construction kept throughout; only the frame's scale and placement change",
                             True, (150, 148, 142)), (PAD, PAD + 26))
        y = PAD + HEAD
        for i, slug in enumerate(order):
            surf = build(0.20, slug)
            x = PAD + i * (CW + GAP)
            sheet.blit(surf, (x, y))
            pygame.draw.rect(sheet, (76, 76, 86), (x, y, CW, CH), 1)
            _, _, thesis = PRESETS[slug]
            t = fl.render(slug, True, (240, 240, 246))
            sheet.blit(t, t.get_rect(midtop=(x + CW // 2, y + CH + 8)))
            c = fs.render(thesis, True, (156, 154, 148))
            sheet.blit(c, c.get_rect(midtop=(x + CW // 2, y + CH + 28)))
        out = "/home/user/skybit/docs/main-menu/harbour-post/profile-frame/sized_showcase.png"
        pygame.image.save(sheet, out)
        print("saved", out, sheet.get_size())
        for slug in order:
            print(slug, verify(slug) if slug != "shipped" else "(reference)")
    else:
        which = os.environ.get("OPTION", "H1")
        out = os.environ.get("OUT", f"/tmp/_pfs_{which}.png")
        surf = build(float(os.environ.get("PHASE", "0.20")), which)
        pygame.image.save(surf, out)
        print("saved", out, verify(which))
