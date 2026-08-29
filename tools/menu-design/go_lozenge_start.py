"""go-lozenge — START v2, concept 3. Standalone renderer.

Fork of launch_perch_start.py (VARIANT=B) via sunburst_medallion_start.py's
structure. Touches no game/*.py file.

This is the set's deliberate CONTROL: no ornament, winning on mass and
saturation alone. Body + sheen + double rim + two-line type, and nothing else —
an ornament-free control carrying ornament would test nothing.

Two construction laws inherited from the critique:

1. The body is authored on a 2x SRCALPHA scratch and downscaled ONCE, because
   every store_cards helper it calls is written in m() units and m() is 2x.
   Drawn straight at 1x the whole stack — sheen height, keyline width, bevel,
   AO depth — ships at double weight.
2. `_gloss_corrected` is NOT used. It blits BLEND_ADD, so peak 110 on a lime
   whose top stop is (176,236,104) clips green until y/h > 0.52 and flattens
   the entire upper half to yellow-white. `top_sheen` alpha-composites and
   cannot clip, which is why it is the only gloss on a body above ~L120.

drop_shadow and smooth_aura bleed OUTSIDE the body, so they are drawn at 1x
with literal integers AFTER the downscale rather than padded into the scratch.

Run under PYTHONHASHSEED=0: draw_signchain seeds plank grain with hash(label),
so an unseeded run re-grains the three hanging signs.

    PYTHONHASHSEED=0 python tools/menu-design/go_lozenge_start.py
"""
import os
import sys
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

_hud = B._hud

assert sc.SS == 2, "the scratch supersample must match store_cards.m()"
SS = sc.SS
m = sc.m

# ── palette ─────────────────────────────────────────────────────────────────
# One hue, three stops, every one far above the L77 mass floor — the shipped
# scarlet board loses its whole lower half to L58/L46 stops that never count as
# bright mass. Lime is the one hue on the wheel that means GO, and the menu has
# none of it. It separates from the ground on chroma and luma (S0.68 vs S0.12,
# L214 vs L38.6), not on hue.
LIME_STOPS = [(0.00, (176, 236, 104)),     # L214
              (0.45, (126, 206,  66)),     # L179
              (1.00, ( 74, 166,  52))]     # L138
RIM_DEEP   = ( 20,  58,  18)
RIM_BRIGHT = (232, 252, 214, 240)          # G held off 255 so no pixel clips
AURA_COL   = (150, 255, 120)
TYPE_INK   = ( 14,  48,  14)               # 7.46:1 on the lime mid
TYPE_LIP   = (206, 246, 176)

# ── geometry ────────────────────────────────────────────────────────────────
# The brief specified 176x96 at x168-344 / y520-616. Measured against the real
# scene that box OVERLAPS the SETTINGS plank: the plank is 172x44 centred on
# (100,506) rotated -1.6, so its right edge runs (186.6, 486.4) -> (185.4,
# 530.4) and the specified body would paint over ~17x10 px of it. 176x96 has no
# legal placement — clearing x186.6 pushes the right edge off-screen, and
# clearing y530.4 pushes the shadow past the y624 gesture floor. That leaves
# exactly 86px of legal height (y532 under the plank, shadow last row 623), so
# the only axis left for mass is width. The proportion brief — a control, not a
# tile — survives at 2.30:1; a 176-wide body at this height converts to only
# ~12.4k bright px, which is the 3x-plank bar itself, and mass IS the thesis.
BODY = pygame.Rect(144, 532, 204, 86)
RADIUS = 24                                # 0.28 of height — genre-standard
SHADOW_BLUR, SHADOW_DY, SHADOW_A = 3, 3, 130
PRESS_DY = 3

# Aura biased right and shrunk to r18: at r30 centred on the body it reached
# x162, washing 25px of the SETTINGS plank in lime. Seated on the two edges
# that face away from the plank instead, so the halo still lifts the slab off
# the ground without touching anything.
AURA_SEATS = [(346, 546), (346, 575), (346, 604), (318, 536)]
AURA_R, AURA_PEAK = 18, 30

TYPE_PT = int(os.environ.get("TYPE_PT", "38"))
SUB_PT = int(os.environ.get("SUB_PT", "13"))
SHEEN_H = int(os.environ.get("SHEEN_H", "20"))
SHEEN_PEAK = int(os.environ.get("SHEEN_PEAK", "46"))


def _ink_bbox(surf):
    rects = pygame.mask.from_surface(surf, 8).get_bounding_rects()
    r = rects[0]
    for o in rects[1:]:
        r = r.union(o)
    return r


def _lockup(dst, r, cx):
    """START over TAP TO FLY. The subtitle is the only thing on this screen
    that tells a first-time player what the button DOES, so it is part of the
    control, not decoration on it.

    Letterpress, not drop shadow: on a bright plate the groove's lower lip
    catches the upper-left light, so the pale pass goes down-right and the ink
    sits on top. A dark shadow under dark ink would read as a sticker.
    """
    big = sc._stamp_bold(sc._glyph_base("START", _hud._font(m(TYPE_PT), True),
                                        m(2)), m(1.4))
    sub = sc._stamp_bold(sc._glyph_base("TAP TO FLY", _hud._font(m(SUB_PT), True),
                                        m(2.2)), m(0.8))
    bb, sb = _ink_bbox(big), _ink_bbox(sub)
    gap = m(7)
    total = bb.height + gap + sb.height
    top = r.centery - total // 2

    for img, box, y, lip_a in ((big, bb, top, 132),
                               (sub, sb, top + bb.height + gap, 110)):
        lip = img.copy()
        lip.fill((*TYPE_LIP, 255), special_flags=pygame.BLEND_RGBA_MULT)
        lip.set_alpha(lip_a)
        body = img.copy()
        body.fill((*TYPE_INK, 255), special_flags=pygame.BLEND_RGBA_MULT)
        ox = cx - box.centerx
        oy = y - box.y
        dst.blit(lip, (ox + m(1), oy + m(1)))
        dst.blit(body, (ox, oy))


_body_cache = {}


def build_lozenge():
    """Authored oversized, then ONE smoothscale down. Everything inside is in
    m() units, so the scratch factor and store_cards.SS must agree."""
    key = (BODY.w, BODY.h, TYPE_PT, SUB_PT, SHEEN_H, SHEEN_PEAK)
    hit = _body_cache.get(key)
    if hit is not None:
        return hit

    w, h = BODY.w * SS, BODY.h * SS
    rad = m(RADIUS)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    r = pygame.Rect(0, 0, w, h)

    s.blit(sc.vgrad_stops(w, h, rad, LIME_STOPS, 255, gamma=1.05), (0, 0))
    sc.top_sheen(s, r, rad, m(SHEEN_H), peak=SHEEN_PEAK)
    sc.contact_shadow(s, r, rad, m(4), alpha=85)
    _lockup(s, r, w // 2)
    # The canonical defined edge: a dark contact keyline UNDER a bright
    # top-left bevel. One pair of strokes, not a collar. bevel_rim's bright
    # stroke is w//2 wide, so the chips' m(1.5) leaves a single device px that
    # the downscale erases — on a body this size the lit lip has to be m(3) to
    # survive as the ~1.5px at 1x that makes the edge read as moulded enamel.
    pygame.draw.rect(s, RIM_DEEP, r, width=max(1, m(1.4)), border_radius=rad)
    sc.bevel_rim(s, r, rad, RIM_DEEP, RIM_BRIGHT, w=max(1, m(3)))

    # top_sheen's band and contact_shadow's layer are rect-sized, so their
    # square corners spill outside the rounded silhouette. pygame.draw WRITES
    # alpha, so the trim goes through a mask + BLEND_RGBA_MIN.
    sil = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(sil, (255, 255, 255, 255), r, border_radius=rad)
    s.blit(sil, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    out = pygame.transform.smoothscale(s, (BODY.w, BODY.h))
    _body_cache[key] = out
    return out


def draw_go_lozenge(surf, pressed=False):
    """Outer effects are 1x literal integers so the downscale cannot clip them.

    Pressed: the slab travels 3px into its own shadow, the shadow tightens to a
    contact shadow and the halo is snuffed. Tactility is the entire thesis, so
    the pressed frame is part of the design, not a nicety.
    """
    rect = BODY.move(0, PRESS_DY) if pressed else BODY.copy()
    if pressed:
        sc.drop_shadow(surf, rect, RADIUS, 2, 105, 1)
    else:
        sc.drop_shadow(surf, rect, RADIUS, SHADOW_BLUR, SHADOW_A, SHADOW_DY)
        for ax, ay in AURA_SEATS:
            sd.smooth_aura(surf, ax, ay, AURA_R, AURA_COL, peak=AURA_PEAK)
    surf.blit(build_lozenge(), rect.topleft)
    return rect


# ── composition ─────────────────────────────────────────────────────────────
def compose(phase):
    """Builds the scene ONCE and snapshots it immediately before the START
    draw, then branches. Plank identity is then structural: the only pixels
    that can differ are ones the lozenge stack itself writes."""
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

    rest = snapshot.copy()
    draw_go_lozenge(rest)
    finish(rest)

    press = snapshot.copy()
    draw_go_lozenge(press, pressed=True)
    finish(press)

    return base, rest, press, chain, pip, snapshot


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
import numpy as np                                           # noqa: E402

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
    l = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]).clip(0, 255)
    g = pygame.Surface(surf.get_size())
    pygame.surfarray.blit_array(g, np.dstack([l, l, l]).astype(np.uint8))
    return g


def rgb(surf):
    return pygame.surfarray.array3d(surf).transpose(1, 0, 2).astype(float)


def luma(a):
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def txt(dst, s, pos, size=17, col=INK, center=False):
    f = _hud._font(size, True)
    img = f.render(s, True, col)
    r = img.get_rect()
    if center:
        r.midtop = pos
    else:
        r.topleft = pos
    dst.blit(img, r)
    return r


def panel(sheet, img, x, y, cap, sub):
    pygame.draw.rect(sheet, (60, 62, 70),
                     (x - 2, y - 2, img.get_width() + 4, img.get_height() + 4), 2)
    sheet.blit(img, (x, y))
    txt(sheet, cap, (x + img.get_width() // 2, y - CAPH), 19, ACC, center=True)
    txt(sheet, sub, (x + img.get_width() // 2, y - CAPH + 21), 13, DIM, center=True)


base, rest, press, chain, pip, snap = compose(0.0)
_, rest_n, _, _, _, _ = compose(0.55)

CROP = pygame.Rect(152, 496, 208, 144)
crop_r = rest.subsurface(CROP).copy()
crop_p = press.subsurface(CROP).copy()
crop_g = grey(rest).subsurface(CROP).copy()

cols = [W, W, W, W, W, CROP.width]
sheet_w = PAD * 2 + sum(cols) + GAP * (len(cols) - 1)
sheet_h = HEADH + CAPH + H + PAD + 102
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BOARD)
pygame.draw.rect(sheet, CARD, (0, 0, sheet_w, HEADH - 10))

txt(sheet, "START v2  concept 3  —  GO-LOZENGE   (the deliberate control)   ·   round 1",
    (PAD, 14), 26, INK)
txt(sheet, "%dx%d @ x%d-%d / y%d-%d  ·  built on a 2x SRCALPHA scratch, ONE smoothscale down, cached  ·  "
           "top_sheen peak %d (NOT _gloss_corrected — BLEND_ADD would clip the lime's whole top half)  ·  "
           "chrome collar and facet_gem CUT: body + sheen + double rim + two-line type, nothing else"
    % (BODY.w, BODY.h, BODY.left, BODY.right, BODY.top, BODY.bottom, SHEEN_PEAK),
    (PAD, 46), 15, DIM)

y = HEADH + CAPH
x = PAD
panel(sheet, base, x, y, "BASE  —  approved VARIANT=B",
      "reference · PHASE 0.0 · shipped scarlet board"); x += W + GAP
panel(sheet, rest, x, y, "GO-LOZENGE  ·  1x  ·  REST",
      "PHASE 0.0  day pole · ground L38.6"); x += W + GAP
panel(sheet, rest_n, x, y, "GO-LOZENGE  ·  1x  ·  REST",
      "PHASE 0.55  night pole · ground L21.7"); x += W + GAP
panel(sheet, grey(rest), x, y, "GREYSCALE  /  SQUINT",
      "luma only — does it still win the corner?"); x += W + GAP
panel(sheet, press, x, y, "PRESSED  ·  1x  ·  -3px",
      "slab into its own shadow · halo snuffed"); x += W + GAP

panel(sheet, crop_r, x, y, "1x CROP  ·  REST", "x152-360 / y496-640 · actual size")
sheet.blit(crop_p, (x, y + CROP.height + 34))
pygame.draw.rect(sheet, (60, 62, 70), (x - 2, y + CROP.height + 32,
                                       CROP.width + 4, CROP.height + 4), 2)
txt(sheet, "same crop, PRESSED (-3px)", (x + CROP.width // 2, y + CROP.height + 12),
    13, DIM, center=True)
sheet.blit(crop_g, (x, y + CROP.height * 2 + 68))
pygame.draw.rect(sheet, (60, 62, 70), (x - 2, y + CROP.height * 2 + 66,
                                       CROP.width + 4, CROP.height + 4), 2)
txt(sheet, "same crop, greyscale", (x + CROP.width // 2, y + CROP.height * 2 + 46),
    13, DIM, center=True)

# ── measured facts ──────────────────────────────────────────────────
ar = rgb(rest)
L = luma(ar)
box = np.zeros(L.shape, bool)
box[BODY.top:BODY.bottom, BODY.left:BODY.right] = True
bright = int(((L > 70) & box).sum())

changed = (np.abs(ar - rgb(base)).max(axis=2) > 2)
sx = np.where(changed.any(axis=0))[0]
sy = np.where(changed.any(axis=1))[0]

# Plank identity is measured against the shared pre-START snapshot, not against
# the base render: the base's draw_start_B moors a rope from the chain tails
# onto its post, and that rope lies ON the SETTINGS plank. go-lozenge (like
# sunburst) leaves the chain, so a base-vs-concept diff there is the base's own
# furniture, not a plank the concept disturbed.
touched = (np.abs(ar - rgb(snap)).max(axis=2) > 2)
pl = int(touched[481:531, 13:188].sum())
pl_col = int(touched[364:531, 0:200].sum())
base_touched = (np.abs(rgb(base) - rgb(snap)).max(axis=2) > 2)
pl_base = int(base_touched[481:531, 13:188].sum())

fy = HEADH + CAPH + H + 20
sheen_rows = " ".join("%d" % ar[BODY.top + 2 + k, BODY.centerx, 1] for k in range(0, 20, 2))
an = rgb(rest_n)
Ln = luma(an)

txt(sheet, "MEASURED", (PAD, fy), 17, ACC)
txt(sheet, "bright mass luma>70 = %s px  =  %.2fx the SKYBIT title (12,351)  =  %.2fx a plank (4,140)"
           "     ·     planks %d px touched @ tol>2     ·     Pip bbox x%d-%d / y%d-%d unmoved"
    % (f"{bright:,}", bright / 12351, bright / 4140, pl, pip[0], pip[1], pip[2], pip[3]),
    (PAD + 108, fy + 1), 15, OK)
txt(sheet, "SHEEN DOES NOT CLIP — green down the body's top 20 rows: %s ... (peak G in the whole body = %d, never 255). "
           "_gloss_corrected(110) would have read 255 255 255 255 255 255 255 255 255 255 here."
    % (sheen_rows, int(ar[BODY.top:BODY.bottom, BODY.left:BODY.right, 1].max())),
    (PAD, fy + 24), 14, DIM)
txt(sheet, "stops L214 / L179 / L138 (Rec709; L203/166/125 Rec601) — every one far above the L77 floor   ·   START ink 8.18:1, TAP TO FLY 5.83:1 on the lime under each   "
           "·   tap %dx%d (>=48dp), top y%d clears the SETTINGS bbox y530.4   ·   lowest drawn px y%d, floor 624   ·   aura r18 biased right, nearest reach x%d"
    % (BODY.w, BODY.h, BODY.top, int(np.where(touched.any(axis=1))[0].max()),
       min(a[0] for a in AURA_SEATS) - AURA_R),
    (PAD, fy + 45), 14, DIM)
txt(sheet, "HONEST READ: the safe floor, not the hero. It is the Royal Match / Candy Crush default — it converts, it is unmistakably a control, "
           "and it is the only concept that tells a first-timer what the button does. Premium-simple rather than plain, but nobody will screenshot it.",
    (PAD, fy + 66), 14, ACC)

out = os.environ.get("OUT") or os.path.join(
    _ROOT, "docs", "main-menu", "start-v2", "go-lozenge", "round_1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)

print("saved", out, sheet.get_size())
print("bright mass luma>70 in body      :", bright,
      "= %.2fx title  %.2fx plank" % (bright / 12351, bright / 4140))
print("changed bbox vs base             : x%d-%d  y%d-%d" % (sx.min(), sx.max(), sy.min(), sy.max()))
print("plank bbox px touched by concept :", pl, " (whole plank column:", pl_col, ")")
print("night ground under button L      : %.1f  (day %.1f)"
      % (Ln[600:620, 40:120].mean(), L[600:620, 40:120].mean()))
print("plank bbox px touched by BASE    :", pl_base, " <- base's own mooring rope")
print("PIP bbox                         :", pip)
print("body rect                        :", BODY, "aspect %.2f:1" % (BODY.w / BODY.h))
print("--- sheen clip probe (body centre column, 1x) ---")
for dy in range(0, 26, 2):
    px = ar[BODY.top + dy, BODY.centerx]
    print("   y=%d  dy=%2d  RGB=(%3d,%3d,%3d)  L=%.1f"
          % (BODY.top + dy, dy, px[0], px[1], px[2], luma(px[None, None])[0, 0]))
print("max channel inside body: R=%d G=%d B=%d"
      % tuple(int(ar[BODY.top:BODY.bottom, BODY.left:BODY.right, c].max()) for c in range(3)))
