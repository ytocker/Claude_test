"""marquee-hoarding — START v2, concept 2 (re-spec). Standalone renderer.

Fork of launch_perch_start.py (VARIANT=B), structured after its peer
sunburst_medallion_start.py. Touches no game/*.py file.

The re-spec: the first pass filled stall_fronts._cartouche_points with the
game's own GOLD_A_STOPS and framed it in gilt, which is the stall sign
recoloured rather than a control. So the silhouette is a plain rounded-rect
cabinet under a shallow two-step crown authored here, the frame is deep
ink-teal (sunburst-medallion owns gold in this set), and six bulbs carry the
rhythm instead of ten.

Cabinet is authored on a 2x SRCALPHA scratch and downscaled ONCE, because
every helper it calls is written in store_cards' m() units and m() is 2x.
drop_shadow and the bulb haloes bleed outside the cabinet, so they are drawn
at 1x with literal integers around the downscale.

Run under PYTHONHASHSEED=0: draw_signchain seeds plank grain with hash(label),
so an unseeded run re-grains the three hanging signs.

    PYTHONHASHSEED=0 python tools/menu-design/marquee_hoarding_start.py
"""
import os
import sys
import math
import types
import contextlib

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

# ── geometry, 1x menu space ─────────────────────────────────────────────────
# x28-332 and top y546 are the ruled inset: at 91% width the bar read as a
# footer nav strip, and bulb haloes seated on a y538 edge reached into the
# SETTINGS plank's bbox (bottom y530.4).
CROWN_TOP = 546
BODY = pygame.Rect(28, 556, 304, 64)          # y556-620, 4px off the y624 floor
RAD = 12
# Bezel 9 / 11 top / 8 bottom. frame_double_bevel lays four strokes inside
# 5.5px, so a 7px bezel packed them against the plate edge and the cabinet
# read as a striped band rather than a solid ink carcass; the deeper top rail
# is also what a marquee's bulb run is physically mounted on.
PLATE = pygame.Rect(37, 567, 286, 45)         # x37-323, y567-612

# The crown is authored here, and deliberately not _cartouche_points': the
# stall silhouette steps DOWN and OUT from a full-height central block at
# 100/93/86% width, so it reads as a nibbled plaque outline. This one is a
# narrow pediment rising from a plain full-width body at 33/13% — a topper
# sitting ON a control, which is the marquee read.
CROWN = [pygame.Rect(126, 551, 108, 9),       # step 1, base tucked under BODY
         pygame.Rect(156, 546, 48, 10)]       # step 2

WORD_CY = 587                                 # 31px caps span y571.5-602.5
SWASH_Y = 606
BULB_Y = 561
BULB_XS = (48, 82, 116, 244, 278, 312)        # 3 + 3, flanking the crown
BULB_HALO_R = 11
BULB_HALO_PEAK = 32                           # set-wide smooth_aura cap

# ── palette ─────────────────────────────────────────────────────────────────
# Ivory reader board, ink cabinet, warm bulbs: the actual material split of a
# theatre marquee, and the one that separates this from the medallion's gold.
PLATE_TOP = (250, 243, 222)
PLATE_BOT = (232, 220, 192)
INK_TOP   = ( 22,  46,  58)
INK_BOT   = ( 14,  30,  40)
FRAME_DEEP   = (  8,  18,  26)
FRAME_MID    = ( 34,  66,  82)
FRAME_BRIGHT = (112, 156, 172)
HAIRLINE  = (232, 196, 108)     # the ONE warm note on the cabinet
TYPE_INK  = ( 30,  64, 120)     # cobalt — 8.29:1 on the plate
TYPE_LIP  = (255, 252, 244)
CONTACT   = (  8,  20,  28)
SOCKET    = (146, 104,  40)
SOCKET_D  = ( 52,  34,  10)
SOCKET_HI = (206, 166,  96)
GLASS_RIM = (232, 196, 120)
GLASS     = (255, 240, 196)
GLASS_HOT = (255, 253, 240)
HALO      = (255, 226, 150)
# The swash is gilt, but a gilt authored to read on ivory rather than on the
# dark card store_design's engraving constants were tuned against.
SWASH_TONES = dict(_ENG_GLINT=(180, 136,  46), _ENG_BRIGHT=(240, 208, 128),
                   _ENG_SHADOW=(116,  84,  26))

INK_STOPS = [(0.0, INK_TOP), (1.0, INK_BOT)]
PLATE_STOPS = [(0.0, PLATE_TOP), (1.0, PLATE_BOT)]


@contextlib.contextmanager
def _swapped(mod, **kw):
    """Colour is data, geometry is code: the shipped stroke stacks are called
    verbatim with their palette constants rebound, so the ink cabinet gets
    frame_double_bevel's exact bevel and keyline rhythm rather than a
    lookalike reimplementation of it."""
    old = {k: getattr(mod, k) for k in kw}
    for k, v in kw.items():
        setattr(mod, k, v)
    try:
        yield
    finally:
        for k, v in old.items():
            setattr(mod, k, v)


def _ink_at(y):
    """The cabinet gradient sampled in menu space, so the crown steps continue
    the body's ramp instead of restarting it."""
    t = max(0.0, min(1.0, (y - CROWN_TOP) / float(BODY.bottom - CROWN_TOP)))
    return sc.lerp_stops(INK_STOPS, t)


def _dev(rect, ox, oy):
    return pygame.Rect(m(rect.x - ox), m(rect.y - oy), m(rect.w), m(rect.h))


def _swash(ov, cx, y0):
    """_swash_underline's geometry (store_design:374) — the tapered run and its
    curled terminal — restated without the centre _micro_gem, which would be a
    third small bright object after the six bulbs and the hairline."""
    for side in (-1, 1):
        run = [(cx + side * m(1.5), y0),
               (cx + side * m(10), y0 + m(0.5)),
               (cx + side * m(20), y0 - m(0.5))]
        curl = sd._spiral(cx + side * m(26), y0 - m(2.2), m(2.8),
                          turns=1.15, phase=math.pi / 2, mirror=-side, n=20)
        with _swapped(sd, **SWASH_TONES):
            sd._tapered(ov, run + curl, 1.5, 0.9, body_a=205, hi_a=120)


def _bulb(ov, bx, by):
    """r4 seat / r3 glass. The socket is a full collar rather than a ring so
    the bulb reads as MOUNTED on the rail — six unmounted dots across 304px is
    the dotted-noise failure the count was cut from ten to avoid."""
    sc.soft_glow(ov, bx, by, m(8), HALO, 44)
    pygame.draw.circle(ov, SOCKET_D, (bx, by + m(1)), m(4))
    pygame.draw.circle(ov, SOCKET, (bx, by), m(4))
    pygame.draw.arc(ov, SOCKET_HI, pygame.Rect(bx - m(4), by - m(4), m(8), m(8)),
                    0.7, 2.5, max(1, m(1)))
    pygame.draw.circle(ov, GLASS_RIM, (bx, by), m(3))
    pygame.draw.circle(ov, GLASS, (bx, by), m(3) - max(1, m(0.6)))
    pygame.draw.circle(ov, GLASS_HOT, (bx - m(0.7), by - m(0.8)), max(1, m(1.2)))


_cab_cache = {}


def build_cabinet():
    """Authored oversized, then ONE smoothscale down. Everything inside is in
    m() units, so the scratch factor and store_cards.SS must agree."""
    hit = _cab_cache.get("cab")
    if hit is not None:
        return hit
    ox, oy = BODY.x, CROWN_TOP
    w1, h1 = BODY.width, BODY.bottom - CROWN_TOP
    s = pygame.Surface((m(w1), m(h1)), pygame.SRCALPHA)

    # ── crown, under the body so its base is swallowed by the cabinet ──
    for step in CROWN:
        d = _dev(step, ox, oy)
        body = sc.vgrad_stops(d.w, d.h, m(3),
                              [(0.0, _ink_at(step.top)), (1.0, _ink_at(step.bottom))])
        s.blit(body, d.topleft)
        sc.bevel_rim(s, d, m(3), FRAME_DEEP, (*FRAME_BRIGHT, 210), w=max(2, m(1.6)))
        # 2px at 1x, not 1px: ink-on-dark-ground means the warm crest is the
        # only thing carrying the stepped profile at squint distance.
        pygame.draw.line(s, HAIRLINE, (d.left + m(2), d.top + m(1.4)),
                         (d.right - m(2), d.top + m(1.4)), max(1, m(2)))

    # ── cabinet body + the shipped double-bevel frame, rebound to ink ──
    d_body = _dev(BODY, ox, oy)
    s.blit(sc.vgrad_stops(d_body.w, d_body.h, m(RAD), INK_STOPS), d_body.topleft)
    with _swapped(sd, GOLD=dict(sd.GOLD, deep=FRAME_DEEP, mid=FRAME_MID,
                                bright=FRAME_BRIGHT)):
        sd.frame_double_bevel(s, d_body, m(RAD))
    # The warm hairline sits at the INNER edge of the bezel, not the outer:
    # against frame_double_bevel's bright rim it made two lit strokes 2px
    # apart, and as the reader board's mat it is a marquee detail instead.
    pygame.draw.rect(s, (*HAIRLINE, 205), d_body.inflate(-m(15), -m(15)),
                     width=max(1, m(1)), border_radius=m(RAD - 7))

    # ── reader board ──
    d_plate = _dev(PLATE, ox, oy)
    s.blit(sc.vgrad_stops(d_plate.w, d_plate.h, m(7), PLATE_STOPS), d_plate.topleft)
    sc.top_sheen(s, d_plate, m(7), m(14), peak=58)
    sc.contact_shadow(s, d_plate, m(7), m(4), alpha=78)
    pygame.draw.rect(s, (*CONTACT, 235), d_plate, width=max(1, m(1.1)),
                     border_radius=m(7))

    # ── type ──
    base = sc._glyph_base("START", _hud._font(m(42), True), m(2))
    base = sc._stamp_bold(base, m(1.2))
    bb = _ink_bbox(base)
    lip = base.copy()
    lip.fill((*TYPE_LIP, 255), special_flags=pygame.BLEND_RGBA_MULT)
    lip.set_alpha(170)
    body = base.copy()
    body.fill((*TYPE_INK, 255), special_flags=pygame.BLEND_RGBA_MULT)
    tx = m(180 - ox) - bb.centerx
    ty = m(WORD_CY - oy) - bb.centery
    # Letterpress, not drop shadow: the board is recessed and lit upper-left,
    # so the groove's LOWER lip catches the light. A dark shadow under cobalt
    # on ivory only muddies the one pairing that measures 8:1.
    s.blit(lip, (tx + m(1), ty + m(1)))
    s.blit(body, (tx, ty))
    _swash(s, m(180 - ox), m(SWASH_Y - oy))

    for bx in BULB_XS:
        _bulb(s, m(bx - ox), m(BULB_Y - oy))

    out = pygame.transform.smoothscale(s, (w1, h1))
    _cab_cache["cab"] = out
    return out


def _ink_bbox(surf):
    rects = pygame.mask.from_surface(surf, 8).get_bounding_rects()
    r = rects[0]
    for o in rects[1:]:
        r = r.union(o)
    return r


_outline_cache = {}


def _crisp_outline(surf):
    """One dark keyline traced from the downscaled cabinet's own alpha, so it
    follows the crown-plus-body silhouette exactly. Drawing the body rect and
    the step rects separately laid keylines across the joins — a scar through
    the crown and through the outer bulbs, because those edges are interior."""
    pts = _outline_cache.get("pts")
    if pts is None:
        pts = pygame.mask.from_surface(build_cabinet(), 200).outline()
        _outline_cache["pts"] = pts
    if len(pts) > 2:
        pygame.draw.lines(surf, CONTACT, True,
                          [(x + BODY.x, y + CROWN_TOP) for x, y in pts], 1)


def draw_marquee_start(surf):
    """START has left the chain and is planted: a lit hoarding that gives the
    composition the floor it never had. Outer effects are 1x literal integers
    so the downscale cannot clip them."""
    sc.drop_shadow(surf, BODY, RAD, 4, 120, 0)
    surf.blit(build_cabinet(), (BODY.x, CROWN_TOP))
    # Haloes ride OVER the cabinet: the bulbs are seated in the top rail, so a
    # halo blitted underneath would be hidden by the very thing it lights.
    for bx in BULB_XS:
        sd.smooth_aura(surf, bx, BULB_Y, BULB_HALO_R, HALO, peak=BULB_HALO_PEAK)
    _crisp_outline(surf)
    return BODY.union(pygame.Rect(BODY.x, CROWN_TOP, BODY.width,
                                  BODY.bottom - CROWN_TOP))


# ── composition ─────────────────────────────────────────────────────────────
def compose(phase):
    """Builds the scene ONCE and snapshots it immediately before the START
    draw, then branches. Plank identity is then structural: the only pixels
    that can differ are ones the marquee stack itself writes."""
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

    marq = snapshot.copy()
    draw_marquee_start(marq)
    finish(marq)

    # The plank-identity control is the scene with NO START drawn at all: the
    # base's own harbour-post stack writes into the SETTINGS plank (it moors a
    # rope to it), so base-vs-concept would charge that to the concept.
    none = finish(snapshot.copy())

    return base, marq, chain, pip, none


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
import numpy as np                                          # noqa: E402

W, H = 360, 640
PAD, GAP = 18, 16
CAPH, HEADH = 30, 78

INK   = (232, 226, 214)
DIM   = (150, 146, 138)
BOARD = (26, 27, 32)
CARD  = (16, 17, 21)
ACC   = (250, 200, 96)
OK    = (140, 220, 140)
WARN  = (255, 168, 110)


def grey(surf):
    a = pygame.surfarray.array3d(surf).astype(float)
    l = (0.299*a[..., 0] + 0.587*a[..., 1] + 0.114*a[..., 2]).clip(0, 255)
    g = pygame.Surface(surf.get_size())
    pygame.surfarray.blit_array(g, np.dstack([l, l, l]).astype(np.uint8))
    return g


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
                     (x-2, y-2, img.get_width()+4, img.get_height()+4), 2)
    sheet.blit(img, (x, y))
    txt(sheet, cap, (x + img.get_width()//2, y - CAPH), 19, ACC, center=True)
    txt(sheet, sub, (x + img.get_width()//2, y - CAPH + 21), 13, DIM, center=True)


def _lum(c):
    def ch(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126*ch(c[0]) + 0.7152*ch(c[1]) + 0.0722*ch(c[2])


def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def luma(c):
    return 0.299*c[0] + 0.587*c[1] + 0.114*c[2]


base, marq, chain, pip, none = compose(0.0)
_, marq_n, _, _, _ = compose(0.55)
gmarq = grey(marq)

CROP = pygame.Rect(8, 494, 352, 146)
crop_d = marq.subsurface(CROP).copy()
crop_g = gmarq.subsurface(CROP).copy()
ZOOM = pygame.Rect(24, 540, 176, 88)
zoom_d = pygame.transform.scale(marq.subsurface(ZOOM).copy(), (352, 176))

cols = [W, W, W, W, CROP.width]
sheet_w = PAD*2 + sum(cols) + GAP*(len(cols)-1)
sheet_h = HEADH + CAPH + H + PAD + 84
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BOARD)
pygame.draw.rect(sheet, CARD, (0, 0, sheet_w, HEADH - 10))

txt(sheet, "START v2  concept 2  —  MARQUEE-HOARDING  (re-spec)   ·   round 1",
    (PAD, 14), 26, INK)
txt(sheet, "x28-332 / crown y546 / body y556-620  ·  built on a 2x SRCALPHA scratch, ONE smoothscale down, cached  ·  "
           "drop_shadow + 6 bulb haloes at 1x with literal ints  ·  "
           "_cartouche_points CUT (crown authored here) · gilt CUT (ink-teal frame_double_bevel) · 10 bulbs -> 6 · _micro_gem CUT",
    (PAD, 46), 15, DIM)

y = HEADH + CAPH
x = PAD
panel(sheet, base, x, y, "BASE  —  approved VARIANT=B",
      "reference · PHASE 0.0 · shipped scarlet board"); x += W + GAP
panel(sheet, marq, x, y, "MARQUEE-HOARDING  ·  1x",
      "PHASE 0.0  day pole · ground L38.6"); x += W + GAP
panel(sheet, marq_n, x, y, "MARQUEE-HOARDING  ·  1x",
      "PHASE 0.55  night pole · ground L21.7"); x += W + GAP
panel(sheet, gmarq, x, y, "GREYSCALE  /  SQUINT",
      "luma only — does it still win the corner?"); x += W + GAP

panel(sheet, crop_d, x, y, "1x CROP", "x8-360 / y494-640  ·  actual size")
sheet.blit(crop_g, (x, y + CROP.height + 34))
pygame.draw.rect(sheet, (60, 62, 70),
                 (x-2, y+CROP.height+32, CROP.width+4, CROP.height+4), 2)
txt(sheet, "same crop, greyscale", (x + CROP.width//2, y + CROP.height + 12),
    13, DIM, center=True)
sheet.blit(zoom_d, (x, y + CROP.height*2 + 34 + 46))
pygame.draw.rect(sheet, (60, 62, 70),
                 (x-2, y+CROP.height*2+32+46, 352+4, 176+4), 2)
txt(sheet, "2x DETAIL — crown steps + left bulb run (magnified, not shipped size)",
    (x + CROP.width//2, y + CROP.height*2 + 12 + 46), 13, DIM, center=True)

# ── measured facts ──────────────────────────────────────────────────
FOOT = pygame.Rect(28, CROWN_TOP, 304, 640 - CROWN_TOP)
a = pygame.surfarray.array3d(marq).transpose(1, 0, 2).astype(float)
Lm = 0.299*a[..., 0] + 0.587*a[..., 1] + 0.114*a[..., 2]
sub = Lm[FOOT.top:FOOT.bottom, FOOT.left:FOOT.right]
bm = int((sub > 70).sum())

an = pygame.surfarray.array3d(none).transpose(1, 0, 2).astype(int)
am = pygame.surfarray.array3d(marq).transpose(1, 0, 2).astype(int)
diff = np.abs(an - am).max(axis=2)
planks = {"STORE": chain["STORE"], "TOP 10": chain["TOP 10"],
          "SETTINGS": chain["SETTINGS"]}
plank_px = {k: int((diff[r.top:r.bottom, r.left:r.right] > 2).sum())
            for k, r in planks.items()}
ys, xs = (diff > 2).nonzero()
dy0, dy1, dx0, dx1 = int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())
base_px = {}
_ab = pygame.surfarray.array3d(base).transpose(1, 0, 2).astype(int)
_bd = np.abs(an - _ab).max(axis=2)
for k, r in planks.items():
    base_px[k] = int((_bd[r.top:r.bottom, r.left:r.right] > 2).sum())

halo_top = BULB_Y - BULB_HALO_R - 1
set_r = planks["SETTINGS"]
ink_bot = dy1

fy = HEADH + CAPH + H + 20
txt(sheet, "MEASURED", (PAD, fy), 17, ACC)
l1 = ("bright mass luma>70 in x28-332/y546-640 = %s px  =  %.2fx the SKYBIT title (12,351)  =  %.2fx a plank (4,140)"
      % (f"{bm:,}", bm/12351, bm/4140))
txt(sheet, l1, (PAD + 108, fy + 1), 15, OK if bm >= 12351 else WARN)
l2 = ("planks vs the no-START control: STORE %d px · TOP 10 %d px · SETTINGS %d px @tol>2  (the approved base itself "
      "writes %d px into SETTINGS — it moors a rope there)   ·   Pip bbox x%d-%d / y%d-%d   ·   "
      "concept bbox x%d-%d / y%d-%d   ·   tap 304x74 (>=48dp)   ·   nothing below y%d"
      % (plank_px["STORE"], plank_px["TOP 10"], plank_px["SETTINGS"],
         base_px["SETTINGS"], pip[0], pip[1], pip[2], pip[3],
         dx0, dx1, dy0, dy1, ink_bot))
txt(sheet, l2, (PAD, fy + 24), 14, DIM)
l3 = ("bulb haloes: 6 x smooth_aura r%d peak %d at y%d -> top y%d, clears SETTINGS bbox bottom y530.4 by %.1fpx; "
      "SETTINGS right x186.6 vs concept top y546 -> disjoint in y   ·   plate stops L%.0f/L%.0f (floor 77); "
      "ink cabinet L%.0f/L%.0f is the shadow face, NOT counted mass   ·   cobalt (30,64,120) on plate = %.2f:1 / %.2f:1"
      % (BULB_HALO_R, BULB_HALO_PEAK, BULB_Y, halo_top, halo_top - 530.4,
         luma(PLATE_TOP), luma(PLATE_BOT), luma(INK_TOP), luma(INK_BOT),
         contrast(TYPE_INK, PLATE_TOP), contrast(TYPE_INK, PLATE_BOT)))
txt(sheet, l3, (PAD, fy + 44), 14, DIM)

out = os.environ.get("OUT") or os.path.join(
    _ROOT, "docs", "main-menu", "start-v2", "marquee-hoarding", "round_1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
print("bright mass", bm, "= %.3fx title, %.2fx plank" % (bm/12351, bm/4140))
print("planks", plank_px)
print("pip bbox", pip, "diff bbox x%d-%d y%d-%d" % (dx0, dx1, dy0, dy1))
print("contrast top/bot", contrast(TYPE_INK, PLATE_TOP), contrast(TYPE_INK, PLATE_BOT))
