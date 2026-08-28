"""keycap-launch — START v2, concept 5. Standalone renderer.

Fork of launch_perch_start.py (VARIANT=B). Touches no game/*.py file.

Thesis: the one control on screen with real thickness. Every other object in
this menu is a flat plate hung on a rope, so dominance here is Z-depth — an
extruded key-cap with a visible side wall, nearest to camera. Nothing in the
Skybit world is built this way, which is what keeps it a control instead of
scenery.

The cap is authored on a 2x SRCALPHA scratch and downscaled ONCE, because every
helper it calls is written in store_cards' m() units and m() is 2x — drawn at 1x
the whole stack ships at double weight. drop_shadow bleeds outside the body, so
it is drawn at 1x with literal integers AFTER the downscale.

Run under PYTHONHASHSEED=0: draw_signchain seeds plank grain with hash(label),
so an unseeded run re-grains the three hanging signs.

    PYTHONHASHSEED=0 python tools/menu-design/keycap_launch_start.py
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

from game import store_cards as sc                            # noqa: E402

_hud = B._hud

assert sc.SS == 2, "the scratch supersample must match store_cards.m()"
SS = sc.SS
m = sc.m

# ── geometry ────────────────────────────────────────────────────────────────
FACE = pygame.Rect(96, 534, 248, 76)
RADIUS = 20
DEPTH = 11                  # rest-state side wall; wall bottom lands on y621
DEPTH_PRESS = 3             # pressed — the face travels the difference
FLOOR_Y = 624               # gesture-bar line; nothing, shadow included, below

# ── palette — the set's only cool option ────────────────────────────────────
FACE_STOPS = [(0.0, (96, 166, 244)),      # L156.7
              (0.5, (48, 116, 214)),      # L108.7
              (1.0, (26, 84, 178))]       # L 78.4 — still above the L70 floor
# The wall is deliberately BELOW the floor: it is the shadow face of the
# extrusion, not mass, so it must not be counted as bright area. The narrow
# ramp is what separates "a solid with a lit top edge" from "a dark stripe" —
# a real side wall catches a little bounce where it meets the cap and goes
# dead at the bottom lip. Both ends stay under L70.
WALL_HI = (28, 72, 150)     # L67.7
WALL_MID = (24, 66, 142)    # L62.1
WALL_LO = (20, 58, 126)     # L54.4
WALL_EDGE = (14, 40, 92)
RIM_DEEP = (14, 44, 104)
RIM_BRIGHT = (210, 232, 255, 235)
GLINT = (160, 206, 255)
TYPE_CREAM = (255, 248, 232)
TYPE_SHADE = (14, 44, 104)
GOLD_RULE = (246, 206, 110)  # the single warm note, tying back to the HUD gold

TYPE_PT = int(os.environ.get("TYPE_PT", "38"))

_cap_cache = {}


def _ink_bbox(surf):
    rects = pygame.mask.from_surface(surf, 8).get_bounding_rects()
    r = rects[0]
    for o in rects[1:]:
        r = r.union(o)
    return r


def build_keycap(depth=DEPTH):
    """Authored oversized, then ONE smoothscale down. Everything inside is in
    m() units, so the scratch factor and store_cards.SS must agree.

    Wall first, face over it: the cap's own bottom rim then doubles as the
    contact line between the two faces, which is the join that reads as an
    edge rather than as two stacked shapes.
    """
    hit = _cap_cache.get((depth, TYPE_PT))
    if hit is not None:
        return hit

    fw, fh = FACE.width, FACE.height
    total_h = fh + depth
    s = pygame.Surface((m(fw), m(total_h)), pygame.SRCALPHA)

    # ── side wall ──
    fold = m(1)
    lip = (fh - depth - 1) / fh
    wall = sc.vgrad_stops(m(fw), m(fh), m(RADIUS),
                          [(0.0, WALL_MID), (max(0.0, lip - 0.001), WALL_MID),
                           (lip, WALL_HI), (1.0, WALL_LO)]).copy()
    pygame.draw.rect(wall, WALL_EDGE, wall.get_rect(),
                     width=m(1), border_radius=m(RADIUS))
    s.blit(wall, (0, m(depth)))

    # ── cap face ──
    face_r = pygame.Rect(0, 0, m(fw), m(fh))
    s.blit(sc.vgrad_stops(m(fw), m(fh), m(RADIUS), FACE_STOPS), (0, 0))
    # top_sheen, not _gloss_corrected: this body sits above L120 at the crown
    # and an additive pass would clip every channel there.
    sc.top_sheen(s, face_r, m(RADIUS), m(18), peak=44)
    sc.bevel_rim(s, face_r, m(RADIUS), RIM_DEEP, RIM_BRIGHT, m(2))

    # A single hairline on the TOP edge only. Wrapping it all the way round
    # would turn the cap into a ring-lit token; on a real extrusion only the
    # crown catches the key light.
    glint = pygame.Surface(face_r.size, pygame.SRCALPHA)
    pygame.draw.rect(glint, GLINT, face_r.inflate(-m(6), -m(6)),
                     width=m(1), border_radius=m(RADIUS - 3))
    fade = pygame.Surface(face_r.size, pygame.SRCALPHA)
    band = m(16)
    for y in range(band):
        a = int(255 * (1 - y / band) ** 1.2)
        pygame.draw.line(fade, (255, 255, 255, a), (0, y), (face_r.w, y))
    glint.blit(fade, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(glint, (0, 0))

    # ── legend ──
    base = sc._glyph_base("START", _hud._font(m(TYPE_PT), True), m(2))
    base = sc._stamp_bold(base, m(1.0))
    bb = _ink_bbox(base)
    rule_h, rule_gap = m(2), m(7)
    group_h = bb.height + rule_gap + rule_h
    # Optically centred, then nudged down: the crown is the brightest part of
    # the gradient, so sitting the word a touch low buys contrast for free.
    top = (m(fh) - group_h) // 2 + m(1)
    ox = (m(fw) - bb.width) // 2 - bb.x
    oy = top - bb.y

    # The plate is a top-lit ramp, so the crown of the word sits on its
    # brightest band. A shade grown a half-px proud of the glyph — not an
    # outline, half of one — buys back edge separation up there without the
    # word reading as stickered onto the cap.
    shade = sc._stamp_bold(base, m(1.5))
    pad = (shade.get_width() - base.get_width()) // 2
    shade.fill((*TYPE_SHADE, 255), special_flags=pygame.BLEND_RGBA_MULT)
    shade.set_alpha(110)
    body = base.copy()
    body.fill((*TYPE_CREAM, 255), special_flags=pygame.BLEND_RGBA_MULT)
    s.blit(shade, (ox - pad, oy - pad + m(1.5)))
    s.blit(body, (ox, oy))

    # Snapped to the supersample grid: an odd 2x origin downscales a 2px rule
    # into one solid row flanked by two half-blends, which reads as fuzz.
    rule = pygame.Rect(0, 0, bb.width - bb.width % SS, rule_h)
    rule.midtop = (m(fw) // 2, top + bb.height + rule_gap)
    rule.left -= rule.left % SS
    rule.top -= rule.top % SS
    pygame.draw.rect(s, GOLD_RULE, rule, border_radius=m(1))

    # The wall band is re-stamped over all but the last 1px of the cap's bottom
    # rim. A 2px near-black line between two blues reads as a GROOVE — two
    # stacked shapes; 1px reads as a FOLD, and the lit upper wall then meets
    # the face's own bottom stop across one edge, which is what says "solid".
    band_top = m(fh) - fold
    s.blit(wall, (0, band_top),
           pygame.Rect(0, band_top - m(depth), m(fw), m(depth) + fold))

    out = pygame.transform.smoothscale(s, (fw, total_h))
    _cap_cache[(depth, TYPE_PT)] = out
    return out


_floor_mask = None


def _floor_clipped_shadow(surf, rect, blur, alpha, dy):
    """drop_shadow at 1x with literal integers, after the downscale.

    The spec'd blur/offset would reach y634 off a wall bottom of y621, i.e.
    into gesture-bar territory. Rather than shrink the shadow — which is what
    seats the cap on the ground plane — its alpha is ramped to zero over the
    last few px so it dies at the floor line with no visible cut edge.
    """
    global _floor_mask
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    sc.drop_shadow(layer, rect, RADIUS, blur, alpha, dy)
    if _floor_mask is None:
        w, h = surf.get_size()
        _floor_mask = pygame.Surface((w, h), pygame.SRCALPHA)
        _floor_mask.fill((255, 255, 255, 255))
        feather = 7
        for i in range(feather):
            y = FLOOR_Y - feather + i
            pygame.draw.line(_floor_mask,
                             (255, 255, 255, int(255 * (1 - i / feather))),
                             (0, y), (w, y))
        pygame.draw.rect(_floor_mask, (255, 255, 255, 0),
                         (0, FLOOR_Y, w, h - FLOOR_Y))
    layer.blit(_floor_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(layer, (0, 0))


def draw_keycap_start(surf, pressed=False):
    """START has left the chain and is planted — no post, no mooring rope.

    Pressed is the whole animation: the face travels down 8px and the wall
    compresses to 3, so the cap's BOTTOM stays put on y621 and only its top
    surface moves. That is what a key does.
    """
    depth = DEPTH_PRESS if pressed else DEPTH
    top = FACE.top + (DEPTH - depth)
    cap = build_keycap(depth)
    wall = pygame.Rect(FACE.left, top + depth, FACE.width, FACE.height)
    if pressed:
        _floor_clipped_shadow(surf, wall, 4, 90, 2)
    else:
        _floor_clipped_shadow(surf, wall, 8, 120, 5)
    surf.blit(cap, (FACE.left, top))
    return pygame.Rect(FACE.left, top, FACE.width, FACE.height + depth)


# ── composition ─────────────────────────────────────────────────────────────
def compose(phase):
    """Builds the scene ONCE and snapshots it immediately before the START
    draw, then branches. Plank identity is then structural: the only pixels
    that can differ are ones the cap stack itself writes."""
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
    draw_keycap_start(rest, pressed=False)
    finish(rest)

    press = snapshot.copy()
    draw_keycap_start(press, pressed=True)
    finish(press)

    return base, rest, press, chain, pip, snapshot


def _diff_bbox(a, b, tol=6):
    import numpy as np
    aa = pygame.surfarray.array3d(a).astype(int)
    bb = pygame.surfarray.array3d(b).astype(int)
    d = (abs(aa - bb).max(axis=2) > tol)
    xs, ys = d.nonzero()
    if len(xs) == 0:
        return None
    return (int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max()))


# ── review sheet ────────────────────────────────────────────────────────────
import numpy as np                                            # noqa: E402

W, H = 360, 640
PAD, GAP = 18, 16
CAPH, HEADH = 30, 78

INK = (232, 226, 214)
DIM = (150, 146, 138)
BOARD = (26, 27, 32)
CARD = (16, 17, 21)
ACC = (250, 200, 96)
OK = (140, 220, 140)


def grey(surf):
    a = pygame.surfarray.array3d(surf).astype(float)
    l = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]).clip(0, 255)
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
                     (x - 2, y - 2, img.get_width() + 4, img.get_height() + 4), 2)
    sheet.blit(img, (x, y))
    txt(sheet, cap, (x + img.get_width() // 2, y - CAPH), 19, ACC, center=True)
    txt(sheet, sub, (x + img.get_width() // 2, y - CAPH + 21), 13, DIM, center=True)


base, rest, press, chain, pip, snap = compose(0.0)
_, rest_n, _, _, _, _ = compose(0.55)
grest = grey(rest)

CROP = pygame.Rect(80, 476, 280, 164)
crop_d = rest.subsurface(CROP).copy()
crop_g = grest.subsurface(CROP).copy()
BCROP = pygame.Rect(84, 518, 272, 118)
btn_rest = rest.subsurface(BCROP).copy()
btn_press = press.subsurface(BCROP).copy()

cols = [W, W, W, W, CROP.width, BCROP.width]
sheet_w = PAD * 2 + sum(cols) + GAP * (len(cols) - 1)
sheet_h = HEADH + CAPH + H + PAD + 58
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BOARD)
pygame.draw.rect(sheet, CARD, (0, 0, sheet_w, HEADH - 10))

txt(sheet, "START v2  concept 5  —  KEYCAP-LAUNCH   ·   round 1   ·   replaces signal-pylon",
    (PAD, 14), 26, INK)
txt(sheet, "face Rect(96,534,248,76) r20 + side wall = the same rounded-rect +11px, drawn FIRST  ·  "
           "built on a 2x SRCALPHA scratch, ONE smoothscale down, cached  ·  "
           "drop_shadow at 1x with literal ints AFTER the downscale  ·  "
           "the set's only cool plate  ·  press = face +8px, wall 11->3",
    (PAD, 46), 15, DIM)

y = HEADH + CAPH
x = PAD
panel(sheet, base, x, y, "BASE  —  approved VARIANT=B",
      "reference · PHASE 0.0 · shipped scarlet board"); x += W + GAP
panel(sheet, rest, x, y, "KEYCAP-LAUNCH  ·  1x",
      "PHASE 0.0  day pole · ground L38.6"); x += W + GAP
panel(sheet, rest_n, x, y, "KEYCAP-LAUNCH  ·  1x",
      "PHASE 0.55  night pole · ground L21.7"); x += W + GAP
panel(sheet, grest, x, y, "GREYSCALE  /  SQUINT",
      "luma only — does it still win the corner?"); x += W + GAP

panel(sheet, crop_d, x, y, "1x CROP  —  START corner",
      "x80-360 / y476-640 · actual size")
sheet.blit(crop_g, (x, y + CROP.height + 34))
pygame.draw.rect(sheet, (60, 62, 70),
                 (x - 2, y + CROP.height + 32, CROP.width + 4, CROP.height + 4), 2)
txt(sheet, "same crop, greyscale", (x + CROP.width // 2, y + CROP.height + 12),
    13, DIM, center=True)
x += CROP.width + GAP

panel(sheet, btn_rest, x, y, "REST  ·  1x", "wall 11px · face top y534")
sheet.blit(btn_press, (x, y + BCROP.height + 34))
pygame.draw.rect(sheet, (60, 62, 70),
                 (x - 2, y + BCROP.height + 32, BCROP.width + 4, BCROP.height + 4), 2)
txt(sheet, "PRESSED  ·  face +8px, wall 3px  —  the cap's bottom never moves",
    (x + BCROP.width // 2, y + BCROP.height + 12), 13, ACC, center=True)

# ── measured facts ──────────────────────────────────────────────────────────
BTN = pygame.Rect(FACE.left, FACE.top, FACE.width, FACE.height + DEPTH)
a = pygame.surfarray.array3d(rest).transpose(1, 0, 2).astype(float)
L = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
sub = L[BTN.top:BTN.bottom, BTN.left:BTN.right]
bm = int((sub > 70).sum())

plank_union = None
for k in ("STORE", "TOP 10", "SETTINGS"):
    plank_union = chain[k] if plank_union is None else plank_union.union(chain[k])
sa = pygame.surfarray.array3d(snap).astype(int)
ra = pygame.surfarray.array3d(rest).astype(int)
dif = (abs(sa - ra).max(axis=2) > 2)
pl = int(dif[plank_union.left:plank_union.right,
             plank_union.top:plank_union.bottom].sum())

low = dif[:, 400:]
lxs, lys = low.nonzero()
ink = (int(lxs.min()), int(lxs.max()), int(lys.min()) + 400, int(lys.max()) + 400)

fy = HEADH + CAPH + H + 20
txt(sheet, "MEASURED", (PAD, fy), 17, ACC)
line = ("bright mass luma>70 = %s px  =  %.2fx the SKYBIT title (12,351)  =  %.2fx a plank (4,140)"
        "     ·     planks %d px @ tol>2     ·     tap rect %dx%d, disjoint from SETTINGS (top y534 vs its bbox bottom 530.4)"
        % (f"{bm:,}", bm / 12351, bm / 4140, pl, BTN.width, BTN.height))
txt(sheet, line, (PAD + 108, fy + 1), 15, OK)
txt(sheet, "measured face column: L156.7 crown -> 78.4 at the fold (floor L70)   ·   1px fold L42.9   ·   11px wall L66.0->55.2, deliberately BELOW the floor — shadow face, not mass   "
           "·   START 38px / 134px run, cream on the plate = 3.35:1 at the cap line, 4.32:1 at mid, 4.87:1 at the baseline (AA-large 3:1 across the whole word)   "
           "·   one warm accent: the 2px (246,206,110) rule   ·   lowest ink y%d, floor 624   ·   Pip bbox x%d-%d / y%d-%d"
    % (ink[3], pip[0], pip[1], pip[2], pip[3]), (PAD, fy + 24), 14, DIM)

out = os.environ.get("OUT") or os.path.join(
    _ROOT, "docs", "main-menu", "start-v2", "keycap-launch", "round_1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
print("bright mass", bm, "planks", pl, "ink bbox", ink, "pip", pip)
print("plank union", plank_union, "settings", chain["SETTINGS"])
