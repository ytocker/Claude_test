"""barely-attached-rip — store_owned_v2 concept, round 1 headless render.

An OWNED card-state chip built from TWO connected pieces — the only concept in
the set that is two joined fragments. A jagged torn UPPER piece still hangs on
the cord, and a fully-separated LOWER fragment dangles just below it, held by
ONE surviving fiber strand under tension. Story: "just ripped, still dangling."

Construction (custom-draw, not _draw_hang_tag, because there are two separate
pieces). Cord + knot replicate _draw_hang_tag exactly.

  Upper piece  — a cream face (_TAG_W x _TAG_H*0.50) with the affordable-tag
                 gradient + bevel + grommet at (30,13), rotated -7 and hung at
                 anchor (44,60). Its bottom edge is a hand-torn asymmetric
                 zigzag seam: fiber-core highlight on the up-peaks, dark shadow
                 in the valleys.
  Lower frag   — an irregular cream piece (~_TAG_W*0.7 x _TAG_H*0.4) below and
                 offset to the side (it broke free and swings), rotated -3 so it
                 hangs free; its top is a matching (not mirrored) torn seam.
  Fiber strand — a single taut 1px cream thread with a 1px dark key beside it,
                 the one surviving fibre bridging an upper-seam peak to the
                 fragment's aligned top point.

Headless (SDL dummy) -> a 3-up review sheet (UNOWNED price tag / EQUIPPED base
check tag / the concept) at SS (324x200 panels, no downscale) plus a scale2x
zoom of the concept's real-scale (1x) render below Panel 2. Not wired into the
live store; writes docs/store_owned_v2/barely_attached_rip/round_1.png.
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()
SID = "skin_mummy"

CARD_W, CARD_H = sc.CARD_W, sc.CARD_H
_TAG_W, _TAG_H = sc._TAG_W, sc._TAG_H

# Fixed swing-tag anchor on the 324x200 SS panel — the same anchor the
# owned/equipped tags use, so the concept lands where the check tag would.
_TAG_CENTER = (44, 60)
_KNOT = (22, 13)
_GROMMET = (30, 13)

_CORD = (190, 165, 115)
_FIBER = (255, 240, 190)             # lit fibre core catching the top-left light
_SEAM_SHADOW = (46, 38, 18)          # dark valley ink of the torn edge

# Two pieces, each shorter than the full tag so together they read as one ripped
# swing-tag whose lower fragment has torn free.
_H_UP = int(_TAG_H * 0.50)           # upper piece height
_FW, _FH = int(_TAG_W * 0.70), int(_TAG_H * 0.40)   # lower fragment box
_FRAG_TILT = -3                      # hangs a touch straighter than the upper -7
# Fragment centre: below the anchor by ~0.6*_TAG_H and offset to the side, so it
# looks like it swung free after the tear.
_FRAG_CENTER = (58, 116)


def _rot_point(px, py, center, w, h, tilt):
    """Face-space point -> surface coords for a piece of size (w,h) rotated
    `tilt` and blitted centred at `center`. Same sign convention as the module's
    _tag_rot_point, generalised so each torn piece maps with its OWN centre."""
    th = math.radians(tilt)
    dx, dy = px - w / 2, py - h / 2
    rx = dx * math.cos(th) + dy * math.sin(th)
    ry = -dx * math.sin(th) + dy * math.cos(th)
    return (center[0] + rx, center[1] + ry)


def _gen_seam(width, base_y, up, down, seg, seed):
    """A hand-torn asymmetric zigzag across `width`. Even vertices are up-peaks
    (fibre catches light), odd vertices are valley notches (shadow). Segment
    width + amplitude jitter per vertex so no two teeth match — a real tear, not
    a sawtooth."""
    rnd = random.Random(seed)
    pts, x, i = [], 0.0, 0
    while x < width:
        if i % 2 == 0:
            y = base_y - up * rnd.uniform(0.55, 1.0)
        else:
            y = base_y + down * rnd.uniform(0.45, 1.0)
        pts.append((x, y))
        x += seg * rnd.uniform(0.6, 1.4)
        i += 1
    # anchor the final vertex exactly on the far edge so the mask closes clean
    last_peak = (len(pts) % 2 == 0)
    pts.append((float(width), base_y - up * 0.35 if last_peak else base_y + down * 0.35))
    return pts


def _build_body(w, h):
    """The exact affordable-tag cream body + gold bevel from _draw_hang_tag, so
    both torn pieces read as the same swing-tag stock."""
    rad = sc.m(3)
    face = pygame.Surface((w, h), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, w, h)
    body = sc.vgrad_stops(w, h, rad,
                          [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                          255, gamma=1.04)
    face.blit(body, (0, 0))
    sc.bevel_rim(face, brect, rad, (80, 52, 12, 200),
                 (255, 240, 190, 200), w=max(1, sc.m(1.2)))
    return face


def _paint_seam(face, seam, mask_poly):
    """Ink the torn edge into `face`, then re-clip to `mask_poly` so no fibre or
    shadow bleeds past the silhouette: a continuous dark valley edge, plus a
    bright fibre tick standing up off every peak."""
    ipts = [(int(round(x)), int(round(y))) for x, y in seam]
    pygame.draw.lines(face, _SEAM_SHADOW, False, ipts, max(1, sc.m(0.8)))
    for i, (x, y) in enumerate(seam):
        if i % 2 == 0:                                   # up-peak: lit fibre core
            ix = int(round(x))
            pygame.draw.line(face, _FIBER, (ix, int(round(y))),
                             (ix, int(round(y + sc.m(1.4)))), max(1, sc.m(0.6)))
    mask = pygame.Surface(face.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), mask_poly)
    face.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


def _build_upper():
    """Upper piece: cream body, bottom torn seam, grommet ring. Returns the
    unrotated face + its bottom-seam vertices (face space) for the fibre root."""
    face = _build_body(_TAG_W, _H_UP)
    base_y = _H_UP - sc.m(3)
    seam = _gen_seam(_TAG_W, base_y, up=sc.m(4), down=sc.m(2.4),
                     seg=sc.m(11), seed=41)
    poly = [(0, 0), (_TAG_W, 0)] + [(x, y) for x, y in reversed(seam)]
    _paint_seam(face, seam, poly)
    # grommet: punch the hole then ring it, exactly as _draw_hang_tag
    pygame.draw.circle(face, (0, 0, 0, 0), _GROMMET, sc.m(5))
    pygame.draw.circle(face, (110, 80, 30), _GROMMET, sc.m(5) + 1, width=max(1, sc.m(1)))
    return face, seam


def _build_fragment():
    """Lower fragment: cream body with a matching (different-seed, not mirrored)
    torn TOP seam; material kept BELOW the tear. Returns face + top-seam verts."""
    face = _build_body(_FW, _FH)
    base_y = sc.m(4)
    seam = _gen_seam(_FW, base_y, up=sc.m(3.4), down=sc.m(2.2),
                     seg=sc.m(9), seed=88)
    poly = [(x, y) for x, y in seam] + [(_FW, _FH), (0, _FH)]
    _paint_seam(face, seam, poly)
    return face, seam


def draw_barely_attached(surf):
    """The two-piece owned chip: fragment behind, cord + upper piece on the
    grommet, then the single fibre strand bridging the gap under tension."""
    upper, up_seam = _build_upper()
    frag, frag_seam = _build_fragment()

    # fragment first — it hangs BEHIND, revealed in the gap under the upper piece
    rotF = pygame.transform.rotate(frag, _FRAG_TILT)
    surf.blit(rotF, rotF.get_rect(center=_FRAG_CENTER))

    # cord tucks under the upper cream head, then the upper piece over it
    gx, gy = _rot_point(*_GROMMET, _TAG_CENTER, _TAG_W, _H_UP, sc._TAG_TILT)
    lw = sc.m(1.5)
    pygame.draw.line(surf, _CORD, (gx, gy), (_KNOT[0] - 1, _KNOT[1] - 1), lw)
    pygame.draw.line(surf, _CORD, (gx, gy), (_KNOT[0] + 2, _KNOT[1] + 2), lw)
    rotU = pygame.transform.rotate(upper, sc._TAG_TILT)
    surf.blit(rotU, rotU.get_rect(center=_TAG_CENTER))
    pygame.draw.circle(surf, _CORD, _KNOT, sc.m(1.5))
    pygame.draw.circle(surf, (min(_CORD[0] + 30, 255), min(_CORD[1] + 30, 255),
                              min(_CORD[2] + 30, 255)), _KNOT, max(1, sc.m(0.6)))

    # THE surviving thread: root it at an upper-seam peak, land it on whichever
    # fragment top vertex sits most directly beneath so the strand pulls taut.
    up_peaks = [(x, y) for i, (x, y) in enumerate(up_seam)
                if i % 2 == 0 and 0.45 * _TAG_W <= x <= 0.78 * _TAG_W]
    px_f, py_f = up_peaks[len(up_peaks) // 2]
    p_up = _rot_point(px_f, py_f, _TAG_CENTER, _TAG_W, _H_UP, sc._TAG_TILT)
    frag_pts = [_rot_point(x, y, _FRAG_CENTER, _FW, _FH, _FRAG_TILT)
                for x, y in frag_seam]
    p_frag = min(frag_pts, key=lambda p: abs(p[0] - p_up[0]))

    x0, y0 = int(round(p_up[0])), int(round(p_up[1]))
    x1, y1 = int(round(p_frag[0])), int(round(p_frag[1]))
    pygame.draw.line(surf, _SEAM_SHADOW, (x0 + 1, y0), (x1 + 1, y1), 1)  # key
    pygame.draw.line(surf, _FIBER, (x0, y0), (x1, y1), 1)               # fibre


# ── panels ──────────────────────────────────────────────────────────────────────
def _new_panel():
    return pygame.Surface((CARD_W * sc.SS, CARD_H * sc.SS), pygame.SRCALPHA)


def _rect():
    return pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       CARD_W * sc.SS - 2 * sc.m(sc._INSET),
                       CARD_H * sc.SS - 2 * sc.m(sc._INSET))


p0 = _new_panel()
sc.draw_card(p0, SID, _rect(), equipped=False, secret=False, owned=False)

p1 = _new_panel()
sc.draw_card(p1, SID, _rect(), equipped=True, secret=False, owned=False)

p2 = _new_panel()
_orig_state_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
try:
    sc.draw_card(p2, SID, _rect(), equipped=False, secret=False, owned=False)
finally:
    sc.state_chip = _orig_state_chip
draw_barely_attached(p2)


# ── review sheet ──────────────────────────────────────────────────────────────
PANEL_W, PANEL_H = CARD_W * sc.SS, CARD_H * sc.SS
BG = (8, 8, 20)
xs = [20, 360, 700]
panel_y = 102
labels = ["UNOWNED (price tag)", "EQUIPPED base (check tag)",
          "CONCEPT: barely-attached-rip"]

zoom = pygame.transform.scale2x(
    pygame.transform.smoothscale(p2, (CARD_W, CARD_H)))
zoom_label_y = panel_y + PANEL_H + 24
zoom_y = zoom_label_y + 22

sheet_w = xs[-1] + PANEL_W + 20
sheet_h = zoom_y + zoom.get_height() + 24
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title = hud_font(24, True).render(
    "store_owned_v2 — barely-attached-rip — round 1", True, (238, 232, 214))
sheet.blit(title, (20, 34))
sub = hud_font(15, True).render(
    "owned card-state chip: torn upper piece on the cord + a free lower "
    "fragment held by ONE fibre strand", True, (168, 172, 196))
sheet.blit(sub, (20, 68))

lf = hud_font(16, True)
for x, panel, lab in zip(xs, (p0, p1, p2), labels):
    sheet.blit(panel, (x, panel_y))
    lt = lf.render(lab, True, (210, 214, 232))
    sheet.blit(lt, (x + (PANEL_W - lt.get_width()) // 2, panel_y + PANEL_H + 4))

zl = hud_font(15, True).render(
    "concept @ real scale (1x render, magnified 2x for inspection):",
    True, (200, 204, 220))
sheet.blit(zl, (xs[2], zoom_label_y))
sheet.blit(zoom, (xs[2], zoom_y))

out = "/home/user/skybit/docs/store_owned_v2/barely_attached_rip/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
