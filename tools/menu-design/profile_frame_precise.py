"""PROFILE frame — size + position only. The general design is the accepted
one: a thin gold double-rule jewel frame with the brass PROFILE tag hanging
BELOW it, clear of the cloud. Nothing about the style changes here.

What changes is geometry. The shipped frame asks for `inflate(18, 18)` and then
clamps its own height against the cloud, which eats the entire bottom pad: the
rule closes at y289 while Pip's real silhouette reaches y291, so 32 opaque bird
pixels sit OUTSIDE his own portrait frame, and his four margins land at
L33 R14 T30 B-2 — jammed into the bottom-right corner.

The crux is that Pip's feet (y291) are only 5px above the cloud (y296), so any
frame closing above the cloud can give him at most ~3px of base margin however
it is padded. Even padding is therefore only reachable if the bottom rule is
allowed to sit ON the cloud — which is the axis these candidates separate.

    OPTION=P1|P2|P3 python3 tools/menu-design/profile_frame_precise.py
    SHOWCASE=1       python3 tools/menu-design/profile_frame_precise.py
"""
import os
import sys
import math

_ROOT = "/home/user/skybit"
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tools", "menu-design"))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame                                        # noqa: E402
import profile_frame_variants as PF                   # noqa: E402

B = PF.B
_hud = B._hud
GOLD_MID, GOLD_BRIGHT, GOLD_PALE = B.GOLD_MID, B.GOLD_BRIGHT, B.GOLD_PALE
GOLD_DEEP = B.GOLD_DEEP
W, H = 360, 640

# Pip's centre is immovable — a fresh Bird respawns on it the instant START is
# tapped — so the frame moves around him, never the other way about.
PIP_CX = 91                    # measured centre of his opaque mask, not BIRD_X


def _rect(l, t, r, b):
    """Inclusive pixel bounds -> Rect, so the tables below read as coordinates."""
    return pygame.Rect(l, t, r - l + 1, b - t + 1)


# slug: (frame rect, thesis)
PRESETS = {
    "current":  (None,
                 "shipped - clips Pip's feet by 32px; margins 33/14/30/-2"),
    # 12px even pad on three sides, closing 3px clear of the cloud: the
    # geometry the frame had before it was clamped, restored exactly.
    "P1": (_rect(23, 209, 139, 293),
           "restored - the original 12px pad, precise; no clip"),
    # P1 recentred on PIP rather than on the cottage. The roof leans left, so
    # centring on its mass is what stranded him against the right rule; the
    # extra width falls into dead sky the cottage never occupied.
    "P2": (_rect(23, 209, 159, 293),
           "centred - same, but centred on the parrot instead of the roof"),
    # The only candidate that can give Pip a real base margin: the bottom rule
    # tucks into the cloud's upper lobes, above the y316 rope exit, so the
    # frame reads as planted on the island rather than hovering over it.
    "P3": (_rect(20, 206, 162, 306),
           "planted - bottom rule set into the cloud; margins finally even"),
}


def tag_rect():
    """The PROFILE tag: below the frame and below the cloud, centred between
    the two rope columns. Shifted 4px left because the right rope angles inward
    faster than the left one moves, so a cloud-centred tag runs out of room on
    that side first."""
    cloud = B.cloud_rect()
    t = pygame.Rect(0, 0, 112, 26)
    t.midtop = (cloud.centerx - 4, cloud.bottom + 8)
    return t


def draw_frame(surf, fr, tag):
    """The accepted construction, verbatim — double rule, top sheen, brass tag.
    Only `fr` and `tag` differ between candidates."""
    pygame.draw.rect(surf, GOLD_MID, fr, width=1, border_radius=13)
    pygame.draw.rect(surf, GOLD_BRIGHT, fr.inflate(-10, -10), width=1,
                     border_radius=8)
    pygame.draw.line(surf, (*GOLD_PALE, 200), (fr.left + 14, fr.top + 2),
                     (fr.right - 14, fr.top + 2), 1)

    pygame.draw.rect(surf, GOLD_DEEP, tag, border_radius=8)
    pygame.draw.rect(surf, GOLD_MID, tag.inflate(-3, -3), border_radius=7)
    pygame.draw.line(surf, GOLD_PALE, (tag.left + 8, tag.top + 3),
                     (tag.right - 8, tag.top + 3), 1)
    pygame.draw.line(surf, (86, 60, 16), (tag.left + 8, tag.bottom - 3),
                     (tag.right - 8, tag.bottom - 3), 1)
    inset = tag.inflate(-8, -8)
    pygame.draw.rect(surf, (52, 34, 14), inset, border_radius=5)
    lx = inset.centerx - 7
    _hud._tracked_label(surf, "PROFILE", (lx, inset.centery + 1), 13,
                        color=(34, 20, 8), track=2, alpha=150)
    _hud._tracked_label(surf, "PROFILE", (lx, inset.centery), 13,
                        color=GOLD_PALE, track=2, alpha=250)
    _hud._profile_tri(surf, inset.right - 9, inset.centery, 4, GOLD_PALE)
    return fr.union(tag)


def build(phase, slug, frame_only=False):
    import random
    from game.scenes import App, STATE_MENU
    from game.world import World
    from game import biome as _biome
    from game import foreground
    from game.config import W as GW, H as GH

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
    surf.blit(B._intro.get_sprite("skyhouse_post"), B.house_topleft())
    app.world.bird.draw(surf)
    chain = B.draw_signchain(surf)
    tails = chain.pop("_tails")
    B.draw_start_B(surf, tails)
    if not frame_only:
        if slug == "current":
            B.draw_profile_frame(surf)
        else:
            draw_frame(surf, PRESETS[slug][0], tag_rect())
    _hud._outlined_text(surf, "SKYBIT", (GW // 2, 112), size=72, px=3,
                        shadow_offset=(2, 3))
    _hud._outlined_text(surf, "POCKET  SKY  FLYER", (GW // 2, 168),
                        size=20, px=2, shadow_offset=(1, 2))
    return surf


def current_frame_rect():
    """Recompute what the shipped draw_profile_frame lands on, so the reference
    panel is measured rather than asserted."""
    cot = B.house_cottage_rect()
    bird_r = pygame.Rect(B.PIP_CX - 31, int(B.PIP_CY) - 27, 64, 51)
    fr = cot.union(bird_r).inflate(18, 18)
    fr.width = min(fr.width, 168 - fr.left)
    cloud = B.cloud_rect()
    fr.height = min(fr.height, (cloud.top - 6) - fr.top)
    return fr


def _pip_pixels():
    """Pip's TRUE opaque silhouette at the menu respawn point. His bounding box
    understates the frame's job by several pixels; only the mask is honest."""
    from game.world import World
    from game.config import H as GH, BIRD_X
    w = World()
    w.bird.x, w.bird.y, w.bird.frame_t = BIRD_X, GH * 0.42, 0.0
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    w.bird.draw(s)
    m = pygame.mask.from_surface(s, threshold=8)
    return [(x, y) for x in range(40, 150) for y in range(220, 320)
            if m.get_at((x, y))]


def _rope_x(sgn, y):
    """draw_signchain's own anchor -> hook interpolation. Colour-matching the
    rope false-positives on Pip's orange plumage, so use the formula."""
    ax = 42 if sgn < 0 else 173
    cx, cy, ang, w, h = 102, 386, -3.0, 172, 44
    rad = math.radians(-ang)
    ox = sgn * (w * 0.36)
    hx = cx + ox * math.cos(rad)
    hy = cy + ox * math.sin(rad) - h * 0.5
    return ax + (y - 316) / (hy - 316) * (hx - ax)


def verify(slug, pip=None):
    fr = current_frame_rect() if slug == "current" else PRESETS[slug][0]
    tag = tag_rect()
    pip = pip if pip is not None else _pip_pixels()
    outside = [p for p in pip if not fr.collidepoint(p)]
    L = min(x for x, y in pip) - fr.left
    R = fr.right - 1 - max(x for x, y in pip)
    T = min(y for x, y in pip) - fr.top
    Bm = fr.bottom - 1 - max(y for x, y in pip)

    worst = float("inf")
    for y in range(max(tag.top, 317), tag.bottom, 2):
        worst = min(worst, tag.left - _rope_x(-1, y), _rope_x(1, y) - (tag.right - 1))
    return dict(clip_px=len(outside), margins=(L, R, T, Bm),
                subtitle_clear=fr.top - 178, tag_gap=tag.top - fr.bottom,
                tag_rope_clear=round(worst, 1), store_clear=359 - tag.bottom)


if __name__ == "__main__":
    order = ["current", "P1", "P2", "P3"]
    pip = _pip_pixels()
    stats = {s: verify(s, pip) for s in order}

    if os.environ.get("SHOWCASE"):
        F = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
        fh = pygame.font.Font(F, 20)
        fl = pygame.font.Font(F, 15)
        fs = pygame.font.Font(F, 12)
        CW, CH = W, H
        PAD, GAP, LAB, HEAD = 22, 14, 66, 52
        n = len(order)
        sheet = pygame.Surface((PAD * 2 + n * CW + (n - 1) * GAP,
                                PAD * 2 + HEAD + CH + LAB))
        sheet.fill((17, 17, 23))
        sheet.blit(fh.render("SKYBIT · PROFILE frame · size + position around Pip",
                             True, (228, 204, 134)), (PAD, PAD))
        sheet.blit(fs.render(
            "same accepted design throughout — thin gold double rule + PROFILE tag hanging below it. "
            "Only the frame's scale and placement change.",
            True, (150, 148, 142)), (PAD, PAD + 26))
        y = PAD + HEAD
        for i, slug in enumerate(order):
            surf = build(0.20, slug)
            x = PAD + i * (CW + GAP)
            sheet.blit(surf, (x, y))
            pygame.draw.rect(sheet, (76, 76, 86), (x, y, CW, CH), 1)
            t = fl.render(slug, True, (240, 240, 246))
            sheet.blit(t, t.get_rect(midtop=(x + CW // 2, y + CH + 8)))
            c = fs.render(PRESETS[slug][1], True, (156, 154, 148))
            sheet.blit(c, c.get_rect(midtop=(x + CW // 2, y + CH + 28)))
            st = stats[slug]
            bad = st["clip_px"] > 0
            m = "Pip margins  L%d  R%d  T%d  B%d      outside frame: %d px" % (
                *st["margins"], st["clip_px"])
            c2 = fs.render(m, True, (214, 106, 96) if bad else (128, 186, 132))
            sheet.blit(c2, c2.get_rect(midtop=(x + CW // 2, y + CH + 46)))
        out = ("/home/user/skybit/docs/main-menu/harbour-post/"
               "profile-frame/precise_showcase.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        pygame.image.save(sheet, out)
        print("saved", out, sheet.get_size())
    else:
        which = os.environ.get("OPTION", "P3")
        out = os.environ.get("OUT", "/tmp/_pfp_%s.png" % which)
        pygame.image.save(build(float(os.environ.get("PHASE", "0.20")), which), out)
        print("saved", out)

    for s in order:
        print("%-8s %s" % (s, stats[s]))
