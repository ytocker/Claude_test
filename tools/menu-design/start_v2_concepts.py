"""START v2 — four premium CTA concepts on the frozen VARIANT=B menu.

Each button is authored on a 2x SRCALPHA scratch and downscaled ONCE, because
store_cards.m() is 2x: drawn straight at 1x every stroke, inset, sheen height
and shadow blur ships at double weight, which is exactly why _pill_btn looks
cheap next to the store cards. store_cards.py:1150 states the contract --
"Author oversized, then ONE smoothscale down turns the geometry crisp."

drop_shadow and smooth_aura bleed OUTSIDE the rect, so they are drawn at 1x
after the downscale rather than padded into the scratch.

Run under PYTHONHASHSEED=0: draw_signchain seeds plank grain with hash(label),
which Python salts per process.

    PYTHONHASHSEED=0 python3 tools/menu-design/start_v2_concepts.py
"""
import os
import sys
import math
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
from game import store_cards as sc      # noqa: E402
from game import store_design as sd     # noqa: E402

_hud = B._hud
assert sc.SS == 2, "the scratch supersample must match store_cards.m()"
m = sc.m


def _scratch(w, h):
    return pygame.Surface((m(w), m(h)), pygame.SRCALPHA)


def _down(s, w, h):
    return pygame.transform.smoothscale(s, (w, h))


def _label(surf, txt, size, center, color, tracking=0, weight=None,
           keyline=None, kw=None, shadow_a=150):
    sc.plain_text(surf, txt, sc.font(size), center, color,
                  shadow_a=shadow_a, tracking=tracking, weight=weight,
                  keyline=keyline, kw=kw)


# ── 1 · marquee-hoarding ────────────────────────────────────────────────────
# Ivory plate in a deep ink-teal frame with six warm bulbs. The gilt and the
# stall cartouche are deliberately gone: filling stall_fronts._cartouche_points
# with the game's own GOLD_A ramp was rebuilding the game's stall sign in ivory,
# and a player reads silhouette and bulb rhythm before plate colour.
MQ = pygame.Rect(28, 546, 304, 72)
_INK_T, _INK_B = (22, 46, 58), (14, 30, 40)
_IVORY_T, _IVORY_B = (250, 243, 222), (232, 220, 192)
_COBALT = (30, 64, 120)
_BULB_SEAT, _BULB_GLASS = (120, 84, 30), (255, 240, 196)
_WARM_HAIR = (232, 196, 108)


def draw_marquee(dst):
    w, h = MQ.size
    s = _scratch(w, h)
    body = pygame.Rect(0, 0, m(w), m(h))

    # Shallow two-step crown, authored here rather than borrowed from the
    # stall silhouette.
    crown = pygame.Rect(m(52), 0, m(w - 104), m(10))
    s.blit(sc.vgrad_stops(crown.w, crown.h, m(5),
                          [(0.0, _INK_T), (1.0, _INK_B)]), crown.topleft)
    frame = pygame.Rect(0, m(8), m(w), m(h - 8))
    s.blit(sc.vgrad_stops(frame.w, frame.h, m(11),
                          [(0.0, _INK_T), (1.0, _INK_B)]), frame.topleft)
    sd.frame_double_bevel(s, frame, m(11))
    pygame.draw.rect(s, _WARM_HAIR, frame.inflate(-m(5), -m(5)),
                     width=max(1, m(0.8)), border_radius=m(9))

    plate = frame.inflate(-m(16), -m(16))
    s.blit(sc.vgrad_stops(plate.w, plate.h, m(7),
                          [(0.0, _IVORY_T), (1.0, _IVORY_B)], gamma=1.04),
           plate.topleft)
    sc.top_sheen(s, plate, m(7), m(9), peak=52)
    sc.contact_shadow(s, plate, m(7), m(3), alpha=76)
    sc.bevel_rim(s, plate, m(7), (150, 138, 108), (255, 250, 236, 220), m(1.2))

    _label(s, "START", 42, (plate.centerx, plate.centery - m(3)), _COBALT,
           tracking=m(1), weight=m(1.4), keyline=(12, 24, 46), kw=m(0.9))
    sd._swash_underline(s, pygame.Rect(plate.centerx, plate.bottom - m(7),
                                       0, 0), m(50))

    out = _down(s, w, h)
    sc.drop_shadow(dst, MQ, 11, blur=6, alpha=120, dy=3)
    dst.blit(out, MQ.topleft)

    # Bulbs and their halos at 1x, after the downscale.
    for i in range(6):
        bx = MQ.left + 34 + i * ((MQ.w - 68) // 5)
        by = MQ.top + 15
        sd.smooth_aura(dst, bx, by, 9, _BULB_GLASS, peak=30, layers=12)
        pygame.draw.circle(dst, _BULB_SEAT, (bx, by), 4)
        pygame.draw.circle(dst, _BULB_GLASS, (bx, by), 3)
    return MQ.copy()


# ── 2 · go-lozenge ──────────────────────────────────────────────────────────
# The deliberate control: no ornament at all. The chrome collar and the gem the
# brainstorm ended on were themselves ornament, so an ornament-free control
# carrying two ornaments would have tested nothing.
GL = pygame.Rect(158, 532, 198, 88)
_LIME = [(0.0, (176, 236, 104)), (0.45, (126, 206, 66)), (1.0, (74, 166, 52))]
_LIME_DEEP, _LIME_BRIGHT = (20, 58, 18), (232, 255, 214, 240)
_LIME_INK = (14, 48, 14)


def draw_lozenge(dst, pressed=False):
    r = GL.copy()
    if pressed:
        r.y += 3
    w, h = r.size
    s = _scratch(w, h)
    body = pygame.Rect(0, 0, m(w), m(h))
    s.blit(sc.vgrad_stops(body.w, body.h, m(30), _LIME, gamma=1.05), (0, 0))
    # top_sheen, not _gloss_corrected: the latter blits BLEND_ADD, and at
    # peak 110 on this lime the green channel stays clipped until y/h > 0.52,
    # blowing the whole upper half to a flat yellow-white.
    sc.top_sheen(s, body, m(30), m(20), peak=46)
    sc.contact_shadow(s, body, m(30), m(4), alpha=85)
    pygame.draw.rect(s, _LIME_DEEP, body, width=m(2), border_radius=m(30))
    sc.bevel_rim(s, body, m(30), _LIME_DEEP, _LIME_BRIGHT, m(2))

    _label(s, "START", 38, (body.centerx, body.centery - m(9)), _LIME_INK,
           tracking=m(1), weight=m(1.4))
    _label(s, "TAP TO FLY", 13, (body.centerx, body.centery + m(19)),
           (40, 92, 40), tracking=m(1.6), shadow_a=90)

    out = _down(s, w, h)
    sd.smooth_aura(dst, r.centerx + 14, r.centery, 18, (150, 255, 120),
                   peak=26, layers=12)
    sc.drop_shadow(dst, r, 30, blur=7, alpha=130 if not pressed else 90,
                   dy=4 if not pressed else 2)
    dst.blit(out, r.topleft)
    return GL.copy()


# ── 3 · boarding-pass ───────────────────────────────────────────────────────
# -8 deg, not -3: the three frozen planks sit at -3.0 / +2.4 / -1.6, so a
# ticket at -3 is the STORE plank's exact rotation and reads as a fourth rung.
BP_W, BP_H = 240, 58
BP_C = (190, 578)
BP_ANG = -8.0
_TANG = [(0.0, (255, 178, 92)), (0.5, (252, 158, 66)), (1.0, (234, 120, 44))]
_CREAM = (250, 238, 214)
_STUB = [(0.0, (244, 104, 168)), (1.0, (206, 64, 128))]
_TICKET_INK = (150, 26, 70)
_PERF_D, _PERF_L = (180, 72, 20), (255, 214, 160)


def draw_ticket(dst):
    w, h = BP_W, BP_H
    s = _scratch(w, h)
    body = pygame.Rect(0, 0, m(w), m(h))
    s.blit(sc.vgrad_stops(body.w, body.h, m(6), _TANG), (0, 0))

    stub_w = m(52)
    stub = pygame.Rect(body.right - stub_w, 0, stub_w, body.h)
    s.blit(sc.vgrad_stops(stub.w, stub.h, m(6), _STUB), stub.topleft)

    panel = pygame.Rect(m(10), m(8), body.w - stub_w - m(22), body.h - m(16))
    s.blit(sc.vgrad_stops(panel.w, panel.h, m(4),
                          [(0.0, _CREAM), (1.0, (232, 216, 186))]),
           panel.topleft)
    sc.top_sheen(s, panel, m(4), m(7), peak=44)
    sc.contact_shadow(s, panel, m(4), m(3), alpha=70)

    _label(s, "START", 32, (panel.centerx, panel.centery - m(4)), _TICKET_INK,
           tracking=m(1), weight=m(1.4))
    _label(s, "ADMIT ONE  -  SKY LINE", 9,
           (panel.centerx, panel.bottom - m(5)), _PERF_D, tracking=m(1.0),
           shadow_a=70)

    # perforation
    px = stub.left
    for yy in range(m(4), body.h - m(4), m(6)):
        pygame.draw.line(s, _PERF_D, (px, yy), (px, yy + m(3)), m(1))
        pygame.draw.line(s, _PERF_L, (px - m(1), yy), (px - m(1), yy + m(3)),
                         max(1, m(0.6)))
    _label(s, "No 0001", 11, (stub.centerx, stub.centery), (255, 226, 240),
           tracking=m(1), shadow_a=80)

    sc.bevel_rim(s, body, m(6), (140, 52, 12), (255, 232, 190, 235), m(2))

    # Die-cut notches: pygame.draw WRITES alpha, so the punch has to go
    # through a mask + BLEND_RGBA_MIN or it paints instead of cutting.
    mask = pygame.Surface(body.size, pygame.SRCALPHA)
    mask.fill((255, 255, 255, 255))
    for cy in (0, body.h):
        pygame.draw.circle(mask, (0, 0, 0, 0), (stub.left, cy), m(7))
    s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    out = _down(s, w, h)
    rot = pygame.transform.rotozoom(out, BP_ANG, 1.0)
    rr = rot.get_rect(center=BP_C)
    sc.drop_shadow(dst, rr.inflate(-10, -10), 8, blur=5, alpha=115, dy=3)
    dst.blit(rot, rr.topleft)
    return rr


# ── 4 · keycap-launch ───────────────────────────────────────────────────────
# The one control on screen with real thickness. Dominance is Z-depth, a
# construction the world has no counterpart for, which is why it cannot be
# mistaken for scenery.
KC = pygame.Rect(96, 534, 248, 76)
KC_WALL = 11
_AZ = [(0.0, (96, 166, 244)), (0.5, (48, 116, 214)), (1.0, (26, 84, 178))]
_AZ_WALL = (24, 66, 142)
_AZ_DEEP, _AZ_BRIGHT = (14, 44, 104), (210, 232, 255, 235)
_AZ_GLINT = (160, 206, 255)
_KEY_CREAM = (255, 248, 232)
_KEY_GOLD = (246, 206, 110)


def draw_keycap(dst, pressed=False):
    face = KC.copy()
    wall = KC_WALL if not pressed else 3
    if pressed:
        face.y += 8
    w, h = face.w, face.h + wall
    s = _scratch(w, h)

    wall_r = pygame.Rect(0, m(wall), m(face.w), m(face.h))
    s.blit(sc.vgrad_stops(wall_r.w, wall_r.h, m(20),
                          [(0.0, _AZ_WALL), (1.0, (18, 52, 112))]),
           wall_r.topleft)

    fr = pygame.Rect(0, 0, m(face.w), m(face.h))
    s.blit(sc.vgrad_stops(fr.w, fr.h, m(20), _AZ), fr.topleft)
    sc.top_sheen(s, fr, m(20), m(18), peak=44)
    sc.bevel_rim(s, fr, m(20), _AZ_DEEP, _AZ_BRIGHT, m(2))
    pygame.draw.line(s, _AZ_GLINT, (fr.left + m(22), m(2)),
                     (fr.right - m(22), m(2)), max(1, m(0.8)))

    _label(s, "START", 38, (fr.centerx, fr.centery - m(4)), _KEY_CREAM,
           tracking=m(1), weight=m(1.4), keyline=(10, 34, 82), kw=m(0.9))
    pygame.draw.line(s, _KEY_GOLD, (fr.centerx - m(38), fr.bottom - m(14)),
                     (fr.centerx + m(38), fr.bottom - m(14)), m(2))

    out = _down(s, w, h)
    shadow_r = pygame.Rect(face.x, face.y + wall, face.w, face.h)
    sc.drop_shadow(dst, shadow_r, 20, blur=8, alpha=120, dy=5)
    dst.blit(out, face.topleft)
    return pygame.Rect(face.x, face.y, face.w, face.h + wall)


CONCEPTS = {
    "marquee-hoarding": draw_marquee,
    "go-lozenge": draw_lozenge,
    "boarding-pass": draw_ticket,
    "keycap-launch": draw_keycap,
}


# ── scene ───────────────────────────────────────────────────────────────────
def build(phase, draw_fn, **kw):
    """Builds the scene ONCE and snapshots it immediately before the START
    draw, then branches. Plank identity is then structural: the only pixels
    that can differ are ones the concept's own stack writes."""
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
    before = surf.copy()
    app.world.bird.draw(surf)
    pip = _bbox_of_diff(before, surf)
    chain = B.draw_signchain(surf)
    tails = chain.pop("_tails")
    snapshot = surf.copy()

    def finish(dst):
        B.draw_profile_frame(dst)
        _hud._outlined_text(dst, "SKYBIT", (W // 2, 112), size=72, px=3,
                            shadow_offset=(2, 3))
        _hud._outlined_text(dst, "POCKET  SKY  FLYER", (W // 2, 168),
                            size=20, px=2, shadow_offset=(1, 2))
        return dst

    base = snapshot.copy()
    B.draw_start_B(base, tails)
    finish(base)

    cand = snapshot.copy()
    rect = draw_fn(cand, **kw)
    finish(cand)
    return base, cand, snapshot, chain, pip, rect


def _bbox_of_diff(a, b):
    W, H = a.get_size()
    xs, ys = [], []
    for y in range(H):
        for x in range(W):
            if a.get_at((x, y))[:3] != b.get_at((x, y))[:3]:
                xs.append(x); ys.append(y)
    if not xs:
        return None
    return pygame.Rect(min(xs), min(ys), max(xs) - min(xs) + 1,
                       max(ys) - min(ys) + 1)
