"""Headless exploration sheet for shoe-placement candidates.

Visualises 5 ways to position a worn shoe (lowered below the belly + a short
ankle stem) on Pip so the cosmetic reads as feet rather than being lost up in
the belly silhouette. ONE representative shoe (shelltoe) drives V1..V5; the
lead variant is re-checked with airflyer to confirm it generalises.

NOT production: composes its own paint_fn over store_skins._compose so nothing
in game/ changes. Run:  SDL_VIDEODRIVER=dummy python tools/shoe_placement_sheet.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game import parrot, shoe_shelltoe, shoe_airflyer
from game.store_skins import _compose, COMPOSITE_W, COMPOSITE_H
from game.draw import make_gradient_surface

# Base foot-red the bare feet-tucks use (parrot BIRD_BEAK_D-ish), per brief.
_STEM = (150, 15, 20)

# Sky behind the bird so shoe contrast is judged against real gameplay, not a
# flat swatch. Two bands (upper navy-blue, lower brighter day-blue) so both the
# dark sole-edge and the off-white upper have something to fight.
_SKY = [(0.0, (44, 96, 170)), (1.0, (96, 168, 224))]


def _dim(surf, factor):
    """Return a darkened copy — the cheap "one value back" for the FAR shoe so
    near/far depth reads without authoring a second palette."""
    out = surf.copy()
    shade = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, int(255 * (1.0 - factor))))
    out.blit(shade, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return out


def _make_paint(draw_shoe, back, front, *, stem_len=0, far_dim=None):
    """paint_fn that drops two shoes (+ optional stems) at the variant coords.

    `back`/`front` are (x, y, w, h). Stems are 2px foot-red lines from the belly
    underside (~y68) down to each shoe top, drawn BEFORE the shoes. `far_dim`
    dims the back (far) shoe by that factor for depth.
    """
    def paint(comp, _wing_angle_deg):
        bx, by, bw, bh = back
        fx, fy, fw, fh = front
        if stem_len:
            # Stem rises from the belly underside to each shoe's top-centre.
            pygame.draw.line(comp, _STEM, (bx + bw // 2, by - stem_len),
                             (bx + bw // 2, by + 1), 2)
            pygame.draw.line(comp, _STEM, (fx + fw // 2, fy - stem_len),
                             (fx + fw // 2, fy + 1), 2)
        if far_dim is not None:
            # Draw the far shoe on a scratch layer so it can be dimmed alone.
            scratch = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
            draw_shoe(scratch, bx, by, bw, bh, 1)
            comp.blit(_dim(scratch, far_dim), (0, 0))
        else:
            draw_shoe(comp, bx, by, bw, bh, 1)
        draw_shoe(comp, fx, fy, fw, fh, 1)
    return paint


def _worn_frame(draw_shoe, back, front, *, stem_len=0, far_dim=None,
                frame_idx=0, tilt=0.0):
    """Build ONE flat worn composite (outlined) for the given variant/tilt,
    mirroring _make_skin's compose -> _add_outline -> rotozoom pipeline."""
    angle = parrot._WING_ANGLES[frame_idx % len(parrot._WING_ANGLES)]
    paint = _make_paint(draw_shoe, back, front, stem_len=stem_len, far_dim=far_dim)
    flat = parrot._add_outline(_compose(angle, paint))
    if tilt:
        flat = pygame.transform.rotozoom(flat, tilt, 1.0)
    return flat


# ── the 5 candidates (composite space; belly bottom y≈69) ────────────────────
# Each: (label, caption, draw kwargs).  draw kwargs -> back/front (x,y,w,h).
VARIANTS = [
    ("V1  PURE DROP", "flat control, no stem",
     dict(back=(17, 68, 17, 11), front=(31, 70, 17, 11), stem_len=0)),
    ("V2  DROP+STEM", "LEAD — short 4px ankle",
     dict(back=(17, 70, 17, 11), front=(31, 72, 17, 11), stem_len=4)),
    ("V3  SPLIT+DEPTH", "wide split, far shoe dimmed",
     dict(back=(16, 70, 16, 10), front=(32, 72, 18, 11), stem_len=3,
          far_dim=0.78)),
    ("V4  SIZE BUMP", "bigger shoes, 3px stem",
     dict(back=(16, 72, 19, 12), front=(32, 72, 19, 12), stem_len=3)),
    ("V5  LONG DANGLE", "too-far bookend, 8px stem",
     dict(back=(17, 76, 18, 12), front=(31, 78, 18, 12), stem_len=8)),
]

# ── layout metrics ───────────────────────────────────────────────────────────
GAME_H = 40                 # true gameplay bird height
ZOOM = 3.6                  # zoom factor for the inspection + tilt copies
TILT = -20                  # dive-tilt copy (pendulum / rotation behaviour)

COL_W = 200
TITLE_H = 56
HDR_H = 38                  # per-column label + caption
CELL_PAD = 14
GAME_BAND = 96              # row that hosts the true-scale bird
ZOOM_BAND = 168
BOT_H = 150                 # bottom "generalises?" strip

BG = (22, 26, 38)
INK = (236, 240, 248)
SUB = (150, 162, 184)
ACCENT = (255, 206, 80)
RULE = (54, 62, 84)

FONT_T = pygame.font.SysFont("Arial", 26, bold=True)
FONT_L = pygame.font.SysFont("Arial", 16, bold=True)
FONT_C = pygame.font.SysFont("Arial", 13)
FONT_S = pygame.font.SysFont("Arial", 12)


def _scaled(flat, target_h):
    """Smooth-scale a flat composite so its bird is `target_h` px tall.
    The composite is 64x100; scale by height to keep aspect."""
    s = target_h / float(flat.get_height())
    w = max(1, int(round(flat.get_width() * s)))
    h = max(1, int(round(flat.get_height() * s)))
    return pygame.transform.smoothscale(flat, (w, h))


def _blit_on_sky(dest, sprite, cx, cy, sky):
    """Drop a sky tile behind the sprite (so contrast is realistic) then the
    sprite centred at (cx, cy)."""
    pad = 8
    tile = pygame.Rect(0, 0, sprite.get_width() + pad * 2,
                       sprite.get_height() + pad * 2)
    tile.center = (cx, cy)
    dest.blit(sky.subsurface(pygame.Rect(0, 0, tile.w, tile.h)
                             if tile.w <= sky.get_width()
                             and tile.h <= sky.get_height()
                             else pygame.Rect(0, 0, sky.get_width(),
                                              sky.get_height())), tile.topleft)
    r = sprite.get_rect(center=(cx, cy))
    dest.blit(sprite, r.topleft)


def main():
    cols = len(VARIANTS)
    W = cols * COL_W
    body_h = GAME_BAND + ZOOM_BAND
    H = TITLE_H + HDR_H + body_h + BOT_H + 24

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    # One tall sky tile reused for every sprite background.
    sky = make_gradient_surface(COL_W, max(body_h, BOT_H),
                                _SKY)

    # ── title strip ──
    pygame.draw.rect(sheet, (14, 17, 26), (0, 0, W, TITLE_H))
    t = FONT_T.render("SHOE PLACEMENT — pick one  (shelltoe shown)", True, INK)
    sheet.blit(t, (16, (TITLE_H - t.get_height()) // 2))
    pygame.draw.line(sheet, ACCENT, (0, TITLE_H - 1), (W, TITLE_H - 1), 2)

    hdr_y = TITLE_H
    game_cy = TITLE_H + HDR_H + GAME_BAND // 2
    zoom_cy = TITLE_H + HDR_H + GAME_BAND + ZOOM_BAND // 2

    for i, (label, caption, kw) in enumerate(VARIANTS):
        x0 = i * COL_W
        cx = x0 + COL_W // 2
        if i:
            pygame.draw.line(sheet, RULE, (x0, TITLE_H), (x0, TITLE_H + HDR_H
                             + body_h), 1)

        # column header
        ls = FONT_L.render(label, True, ACCENT)
        cs = FONT_C.render(caption, True, SUB)
        sheet.blit(ls, (cx - ls.get_width() // 2, hdr_y + 4))
        sheet.blit(cs, (cx - cs.get_width() // 2, hdr_y + 22))

        # true-scale worn bird on sky
        flat = _worn_frame(shoe_shelltoe.draw_shoe, kw["back"], kw["front"],
                           stem_len=kw.get("stem_len", 0),
                           far_dim=kw.get("far_dim"))
        game_sprite = _scaled(flat, GAME_H)
        _blit_on_sky(sheet, game_sprite, cx, game_cy, sky)
        cap = FONT_S.render("~40px gameplay scale", True, SUB)
        sheet.blit(cap, (cx - cap.get_width() // 2,
                         game_cy + GAME_BAND // 2 - 16))

        # zoom (upright) + zoom (dive tilt), side by side
        zoom_sprite = _scaled(flat, int(GAME_H * ZOOM))
        flat_tilt = _worn_frame(shoe_shelltoe.draw_shoe, kw["back"],
                                kw["front"], stem_len=kw.get("stem_len", 0),
                                far_dim=kw.get("far_dim"), tilt=TILT)
        tilt_sprite = _scaled(flat_tilt, int(GAME_H * ZOOM))

        zx_a = x0 + COL_W // 2 - 44
        zx_b = x0 + COL_W // 2 + 46
        _blit_on_sky(sheet, zoom_sprite, zx_a, zoom_cy, sky)
        _blit_on_sky(sheet, tilt_sprite, zx_b, zoom_cy, sky)
        z1 = FONT_S.render("zoom", True, SUB)
        z2 = FONT_S.render("dive -20deg", True, SUB)
        sheet.blit(z1, (zx_a - z1.get_width() // 2,
                        zoom_cy + ZOOM_BAND // 2 - 18))
        sheet.blit(z2, (zx_b - z2.get_width() // 2,
                        zoom_cy + ZOOM_BAND // 2 - 18))

    # ── bottom strip: LEAD (V3 split+depth) on airflyer, to confirm it ports ──
    by = TITLE_H + HDR_H + body_h + 12
    pygame.draw.line(sheet, RULE, (0, by - 6), (W, by - 6), 1)
    head = FONT_L.render("GENERALISES?  V3 placement on AIR FLYER", True, INK)
    sheet.blit(head, (16, by))

    af = VARIANTS[2][2]  # V3 coords
    af_flat = _worn_frame(shoe_airflyer.draw_shoe, af["back"], af["front"],
                          stem_len=af["stem_len"], far_dim=af.get("far_dim"))
    af_tilt = _worn_frame(shoe_airflyer.draw_shoe, af["back"], af["front"],
                          stem_len=af["stem_len"], far_dim=af.get("far_dim"),
                          tilt=TILT)
    row_cy = by + 70
    _blit_on_sky(sheet, _scaled(af_flat, GAME_H), 60, row_cy, sky)
    _blit_on_sky(sheet, _scaled(af_flat, int(GAME_H * ZOOM)), 200, row_cy, sky)
    _blit_on_sky(sheet, _scaled(af_tilt, int(GAME_H * ZOOM)), 320, row_cy, sky)
    for tx, lbl in ((60, "~40px"), (200, "zoom"), (320, "dive -20deg")):
        s = FONT_S.render(lbl, True, SUB)
        sheet.blit(s, (tx - s.get_width() // 2, row_cy + 56))

    out_dir = "/home/user/skybit/docs/shoes"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out)
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
