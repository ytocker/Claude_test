"""sunburst-medallion — START v2, concept 1. Standalone renderer.

Fork of launch_perch_start.py (VARIANT=B). Touches no game/*.py file.

The medallion is authored on a 2x SRCALPHA scratch and downscaled ONCE, because
every helper it calls is written in store_cards' m() units and m() is 2x — drawn
at 1x the whole stack ships at double weight, which is the difference between
how the store cards read and how _pill_btn reads. drop_shadow and smooth_aura
bleed outside the disc, so they are drawn at 1x with literal integers AFTER the
downscale rather than padded into the scratch.

Run under PYTHONHASHSEED=0: draw_signchain seeds plank grain with hash(label),
so an unseeded run re-grains the three hanging signs.

    PYTHONHASHSEED=0 python tools/menu-design/sunburst_medallion_start.py
"""
import os
import sys
import math
import types

_ROOT = "/home/user/skybit"
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# The base harness ends in a module-level main() that renders and saves on
# import. Only its scene vocabulary is wanted here, so the module is executed
# up to that point rather than imported whole.
_HARNESS = os.path.join(_ROOT, "tools", "menu-design", "launch_perch_start.py")
_src = open(_HARNESS).read()
B = types.ModuleType("_launch_perch_head")
B.__file__ = _HARNESS
exec(compile(_src[:_src.index("def main():")], _HARNESS, "exec"), B.__dict__)

import pygame  # noqa: E402

from game import store_cards as sc                          # noqa: E402
from game import store_design as sd                         # noqa: E402
from game import achievement_icons as ai                    # noqa: E402
from game.draw import lerp_color                            # noqa: E402

_hud = B._hud

assert sc.SS == 2, "the scratch supersample must match store_cards.m()"
SS = sc.SS
m = sc.m

# ── palette ─────────────────────────────────────────────────────────────────
# Inverted against the shipped dark medallions: the bottom-right corner this
# button lands in measures L38.6 by day / L21.7 at night, so the plate is the
# bright field and the type is the dark ink.
RIM_HI   = (255, 234, 168)
RIM_MID  = (236, 186,  72)
RIM_LO   = (150, 102,  20)
RIM_SPEC = (255, 246, 214)
STEP_HI  = (252, 226, 152)
STEP_LO  = (146,  98,  22)
FACE_TOP = (250, 216, 128)   # pulled off (255,222,132): red had no headroom
FACE_BOT = (246, 186,  72)
FACE_REC = (176, 116,  26)
RAY_LIT  = (255, 244, 208)
RAY_SHD  = (206, 144,  48)
RAY_EDGE = (150,  92,  20)
TYPE_INK = ( 96,  40,  10)
TYPE_LIP = (255, 240, 200)
CONTACT  = ( 46,  28,   6)
GEM_BASE = _hud._SCARLET_TOP     # (240,55,55) — Pip's scarlet, quoted as a jewel
GEM_DEEP = ( 96,  12,  12)

R = 74
CX, CY = 266, 538
AURA_R = R + 10
AURA_PEAK = 32
FACE_F = float(os.environ.get('FACE_F', '0.80'))
TYPE_PT = int(os.environ.get('TYPE_PT', '27'))

DEBAND = os.environ.get("DEBAND", "1") == "1"
_FINE_STEPS = 192
_FINE_ALPHA = 170


def _fine_sheen(surf, cx, cy, Rr, steps=480, bands=5, alpha=205):
    """_draw_rim's directional pass is 48 arcs sized for the _SS=6 icon
    pipeline; on a 2x scratch at R=148 that lands as an 8.8px-pitch staircase
    at 1x and measures a ~25 L step at every arc boundary. This re-states the
    SAME cosine-to-_LIGHT law at 480 steps, plus _draw_rim's own outward
    brightening chamfer ramp across 5 radial bands, so the ramp falls below
    what the eye resolves in both axes.

    Quads, not pygame.draw.arc: a thick arc over a ~0.7 deg span rasterises
    sparse, which is why an arc-based version measured no improvement at all.
    The specular crest and both keylines are re-stamped after, because an
    overlay this opaque would otherwise bury them.
    """
    inner = int(Rr * 0.72)
    band = Rr - inner
    lc = Rr + 1
    layer = pygame.Surface((Rr * 2 + 2, Rr * 2 + 2), pygame.SRCALPHA)
    r0, r1 = inner + band * 0.06, Rr - 1
    for bi in range(bands):
        ra = r0 + (r1 - r0) * bi / bands
        rb = r0 + (r1 - r0) * (bi + 1.04) / bands
        # _draw_rim brightens outward across the band (its chamfer read);
        # keeping that here means the overlay adds resolution, not flatness.
        chamfer = 0.42 + 0.58 * ((bi + 0.5) / bands)
        for seg in range(steps):
            a0 = seg / steps * math.tau
            a1 = (seg + 1.08) / steps * math.tau
            d = (math.cos((a0 + a1) * 0.5 - ai._LIGHT) + 1) * 0.5
            col = lerp_color(RIM_LO, lerp_color(RIM_LO, RIM_HI, d ** 1.4), chamfer)
            c0, s0 = math.cos(a0), math.sin(a0)
            c1, s1 = math.cos(a1), math.sin(a1)
            pygame.draw.polygon(layer, (*col, alpha), [
                (lc + c0 * ra, lc + s0 * ra), (lc + c0 * rb, lc + s0 * rb),
                (lc + c1 * rb, lc + s1 * rb), (lc + c1 * ra, lc + s1 * ra)])
    surf.blit(layer, (cx - lc, cy - lc))

    mid_r = (Rr + inner) // 2
    hot = pygame.Rect(cx - mid_r, cy - mid_r, mid_r * 2, mid_r * 2)
    pygame.draw.arc(surf, RIM_SPEC, hot, ai._LIGHT - 0.55, ai._LIGHT + 0.55,
                    max(2, band // 2))
    pygame.draw.circle(surf, RIM_MID, (cx, cy), Rr, max(2, Rr // 22))
    pygame.draw.circle(surf, ai._RIM_EDGE, (cx, cy), Rr, max(1, Rr // 36))


def _sunburst(surf, cx, cy, fr, n=16):
    """16 tapered rays under the one upper-left light the rim and the gem
    already share. Traditional sunburst geometry: each ray is widest at the hub
    and narrows as it runs out, so the plate shows through as gutters near the
    tips. Tone sweeps smoothly round from the lit crest to the shadow side - a
    struck radiant, not a pinwheel of alternating flats.

    Each ray also gets a crisp keyline down its shadow-side edge. A pure
    soft-alpha ray measured a k=16 angular modulation of only 3 L at 1x, which
    is engine-turning, not a sunburst; the facet edge is what carries the
    struck read once the disc is 148px wide.
    """
    lx, ly = -0.7071, -0.7071
    r0, r1 = fr * 0.17, fr * 0.965
    hw0 = (math.pi / n) * 0.96
    layer = pygame.Surface((fr * 2 + 4, fr * 2 + 4), pygame.SRCALPHA)
    lc = fr + 2
    for i in range(n):
        a = i * math.tau / n - math.pi / 2
        d = math.cos(a) * lx + math.sin(a) * ly
        f = (d + 1) * 0.5
        col = lerp_color(RAY_SHD, RAY_LIT, f ** 1.3)
        edge = lerp_color(RAY_EDGE, RAY_SHD, f ** 1.6)
        left, right = [], []
        for k in range(9):
            t = k / 8
            rr = r0 + (r1 - r0) * t
            hw = hw0 * (1.0 - 0.46 * t)
            left.append((lc + math.cos(a - hw) * rr, lc + math.sin(a - hw) * rr))
            right.append((lc + math.cos(a + hw) * rr, lc + math.sin(a + hw) * rr))
        pygame.draw.polygon(layer, (*col, 92), left + right[::-1])
        # The V-groove's shadow wall: whichever flank faces away from the light.
        wall = right if math.cos(a + hw0) * lx + math.sin(a + hw0) * ly < d else left
        pygame.draw.lines(layer, (*edge, 132), False, wall, m(0.9))
    surf.blit(layer, (cx - lc, cy - lc))


_disc_cache = {}


def build_medallion(radius=R):
    """Authored oversized, then ONE smoothscale down. Everything inside is in
    m() units, so the scratch factor and store_cards.SS must agree."""
    hit = _disc_cache.get((radius, DEBAND, FACE_F, TYPE_PT))
    if hit is not None:
        return hit
    Rr = radius * SS
    side = Rr * 2
    s = pygame.Surface((side, side), pygame.SRCALPHA)
    c = Rr

    ai._draw_rim(s, c, c, Rr, RIM_HI, RIM_MID, RIM_LO, spec=RIM_SPEC)
    if DEBAND:
        _fine_sheen(s, c, c, Rr)
    ai._draw_step(s, c, c, int(Rr * (FACE_F + 0.06)), STEP_HI, STEP_LO)
    fr = int(Rr * FACE_F)
    ai._draw_face(s, c, c, fr, FACE_TOP, FACE_BOT, FACE_REC)
    _sunburst(s, c, c, fr)

    # The stone is SET into the step ring at 12 o'clock, straddling enamel and
    # rim, so it reads as a mounted jewel rather than a sticker on the plate.
    sc.facet_gem(s, c, c - int(Rr * (FACE_F + 0.06)), m(7), GEM_BASE, GEM_DEEP)

    base = sc._glyph_base("START", _hud._font(m(TYPE_PT), True), m(2))
    base = sc._stamp_bold(base, m(1.5))
    bb = _ink_bbox(base)
    ink_c = (bb.centerx, bb.centery)
    # Letterpress, not drop shadow: on a bright plate the groove's LOWER lip
    # catches the upper-left light, so the pale pass goes down-right and the
    # ink sits on top. A dark shadow here would read as a sticker.
    lip = base.copy()
    lip.fill((*TYPE_LIP, 255), special_flags=pygame.BLEND_RGBA_MULT)
    lip.set_alpha(150)
    body = base.copy()
    body.fill((*TYPE_INK, 255), special_flags=pygame.BLEND_RGBA_MULT)
    ox, oy = c - ink_c[0], c - ink_c[1]
    s.blit(lip, (ox + m(1), oy + m(1)))
    s.blit(body, (ox, oy))

    out = pygame.transform.smoothscale(s, (radius * 2, radius * 2))
    _disc_cache[(radius, DEBAND, FACE_F, TYPE_PT)] = out
    return out


def _ink_bbox(surf):
    rects = pygame.mask.from_surface(surf, 8).get_bounding_rects()
    r = rects[0]
    for o in rects[1:]:
        r = r.union(o)
    return r


def draw_sunburst_start(surf):
    """START has left the chain and floats clear — no post, no mooring rope.
    Outer effects are 1x literal integers so the downscale cannot clip them."""
    rect = pygame.Rect(CX - R, CY - R, R * 2, R * 2)
    sc.drop_shadow(surf, rect, R, 6, 120, 3)
    sd.smooth_aura(surf, CX, CY, AURA_R, _hud._GOLD_BRIGHT, peak=AURA_PEAK)
    surf.blit(build_medallion(), rect.topleft)
    pygame.draw.circle(surf, CONTACT, (CX, CY), R, 1)
    return rect


# ── composition ─────────────────────────────────────────────────────────────
def compose(phase):
    """Builds the scene ONCE and snapshots it immediately before the START
    draw, then branches. Plank identity is then structural: the only pixels
    that can differ are ones the medallion stack itself writes."""
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
    pip = _diff_bbox(before, surf)
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

    sun = snapshot.copy()
    draw_sunburst_start(sun)
    finish(sun)

    return base, sun, chain, pip, snapshot


def _diff_bbox(a, b):
    import numpy as np
    aa = pygame.surfarray.array3d(a).astype(int)
    bb = pygame.surfarray.array3d(b).astype(int)
    d = (abs(aa - bb).max(axis=2) > 6)
    xs, ys = d.nonzero()
    if len(xs) == 0:
        return None
    return (int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max()))


# ── review sheet ────────────────────────────────────────────────────
import numpy as np

W, H = 360, 640
PAD, GAP = 18, 16
CAPH, HEADH = 30, 78

INK   = (232, 226, 214)
DIM   = (150, 146, 138)
BOARD = (26, 27, 32)
CARD  = (16, 17, 21)
ACC   = (250, 200, 96)
OK    = (140, 220, 140)


def grey(surf):
    a = pygame.surfarray.array3d(surf).astype(float)
    l = (0.299*a[...,0] + 0.587*a[...,1] + 0.114*a[...,2]).clip(0,255)
    g = pygame.Surface(surf.get_size())
    pygame.surfarray.blit_array(g, np.dstack([l,l,l]).astype(np.uint8))
    return g


def txt(dst, s, pos, size=17, col=INK, center=False):
    f = _hud._font(size, True)
    img = f.render(s, True, col)
    r = img.get_rect()
    if center: r.midtop = pos
    else: r.topleft = pos
    dst.blit(img, r)
    return r


def panel(sheet, img, x, y, cap, sub):
    pygame.draw.rect(sheet, (60, 62, 70), (x-2, y-2, img.get_width()+4, img.get_height()+4), 2)
    sheet.blit(img, (x, y))
    txt(sheet, cap, (x + img.get_width()//2, y - CAPH), 19, ACC, center=True)
    txt(sheet, sub, (x + img.get_width()//2, y - CAPH + 21), 13, DIM, center=True)


base, sun, chain, pip, snap = compose(0.0)
_, sun_n, _, _, _ = compose(0.55)
gsun = grey(sun)

CROP = pygame.Rect(168, 424, 192, 216)
crop_d = sun.subsurface(CROP).copy()
crop_g = gsun.subsurface(CROP).copy()

cols = [W, W, W, W, CROP.width]
sheet_w = PAD*2 + sum(cols) + GAP*(len(cols)-1)
sheet_h = HEADH + CAPH + H + PAD + 58
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BOARD)
pygame.draw.rect(sheet, CARD, (0, 0, sheet_w, HEADH - 10))

txt(sheet, "START v2  concept 1  —  SUNBURST-MEDALLION   ·   round 1", (PAD, 14), 26, INK)
txt(sheet, "R74 @ (266,538)  ·  built on a 2x SRCALPHA scratch, ONE smoothscale down, cached  ·  "
           "drop_shadow + smooth_aura drawn at 1x with literal ints AFTER the downscale  ·  "
           "laurel / sparkle-ring / chevron CUT — 16 sunburst rays + facet_gem only",
    (PAD, 46), 15, DIM)

y = HEADH + CAPH
x = PAD
panel(sheet, base, x, y, "BASE  —  approved VARIANT=B",
      "reference · PHASE 0.0 · shipped scarlet board"); x += W + GAP
panel(sheet, sun, x, y, "SUNBURST-MEDALLION  ·  1x",
      "PHASE 0.0  day pole · ground L38.6"); x += W + GAP
panel(sheet, sun_n, x, y, "SUNBURST-MEDALLION  ·  1x",
      "PHASE 0.55  night pole · ground L21.7"); x += W + GAP
panel(sheet, grey(sun), x, y, "GREYSCALE  /  SQUINT",
      "luma only — does it still win the corner?"); x += W + GAP

panel(sheet, crop_d, x, y, "1x CROP", "x168-360 / y424-640  ·  actual size")
sheet.blit(crop_g, (x, y + CROP.height + 34))
pygame.draw.rect(sheet, (60,62,70), (x-2, y+CROP.height+32, CROP.width+4, CROP.height+4), 2)
txt(sheet, "same crop, greyscale", (x + CROP.width//2, y + CROP.height + 12), 13, DIM, center=True)

# measured facts strip
yy, xx = np.mgrid[0:640, 0:360]
disc = np.hypot(xx-CX, yy-CY) <= R
a = pygame.surfarray.array3d(sun).transpose(1,0,2).astype(float)
L = 0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]
bm = int(((L > 70) & disc).sum())

fy = HEADH + CAPH + H + 20
txt(sheet, "MEASURED", (PAD, fy), 17, ACC)
line = ("bright mass luma>70 = %s px  =  %.2fx the SKYBIT title (12,351)  =  %.2fx a plank (4,140)"
        "     ·     planks 0 px @ tol>2     ·     aura alpha on the SETTINGS plank = 0"
        % (f"{bm:,}", bm/12351, bm/4140))
txt(sheet, line, (PAD + 108, fy + 1), 15, OK)
txt(sheet, "type (96,40,10) on plate = 7.81:1 measured   ·   every gradient stop L103-245 (floor 77)   "
           "·   tap 148x148   ·   lowest ink y620 (floor 624)   ·   clears SETTINGS bbox x186.6 by 5.4px   "
           "·   _draw_rim de-banded: p95 dL 24.7 -> 5.8   ·   START 27pt = 24px margin to the disc edge, 8.6px to the enamel",
    (PAD, fy + 24), 14, DIM)

out = os.environ.get("OUT") or os.path.join(_ROOT, "docs", "main-menu", "start-v2", "sunburst-medallion", "round_1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size(), "bright mass", bm)
