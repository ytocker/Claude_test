"""Round-1 candidate sheet for the greenery CLUSTER FORMATION study (docs-only).

Composition exploration only — the 30 plant designs and the night-cap contract are
unchanged. Reuses the shipped engine background (sky/mountains/foreground floor +
pillars + gold-coin yardstick) from `_family_showcase`, but DROPS the day-arc
promenade pass so each panel stages only the formation under test. Greenery is
drawn STATIC (frozen per-variant pose `variant * 2.39996`, matching the live
wrapper) — no sway. Five formation treatments, stacked into one review sheet.

Pure pygame (draw + transform.scale NEAREST) — pygbag-safe, no numpy/PIL/gfxdraw.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame  # noqa: E402
pygame.init()

from game.config import W, H, GROUND_Y  # noqa: E402
from game import biome as _biome  # noqa: E402
from game import foreground_promenade as fp  # noqa: E402  (registers pools)
from game import foreground_variants as fv  # noqa: E402
from game import foreground as foreground  # noqa: E402
from game import greenery_cast as _green  # noqa: E402
from game.draw import get_sky_surface_biome, draw_mountains, draw_cloud  # noqa: E402

import tools._family_showcase as sc  # noqa: E402  (shared chrome + pillars + coin)

OUT = os.path.join(_ROOT, "docs", "sidewalk_overhaul", "greenery_clusters")
PHASE = 0.33        # golden afternoon — the greenery showcase phase
SCROLL = 210.0
_DAY = _biome.palette_for_phase(PHASE)
_POSE = lambda variant: variant * 2.39996   # the live static pose seed


def _clean_background(surf):
    """Sky + clouds + mountains + the buff sidewalk floor — NO promenade pass, so
    the panel stages only the formation under test."""
    buckets = _biome.PHASE_BUCKETS
    bf = (PHASE % 1.0) * buckets
    a = int(bf) % buckets
    b = (a + 1) % buckets
    tt = bf - int(bf)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, _biome.palette_for_phase(a / buckets), a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y, _biome.palette_for_phase(b / buckets), b)
    sky_a.set_alpha(None)
    surf.blit(sky_a, (0, 0))
    if tt > 0:
        sky_b.set_alpha(int(tt * 255))
        surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)
    for i, (bx, by, scl) in enumerate(sc._CLOUD_SLOTS):
        ox = ((bx - SCROLL * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(0.3 * i) * 3, scl, variant=0, palette=_DAY)
    draw_mountains(surf, SCROLL, GROUND_Y, W, phase=PHASE)
    foreground.draw_foreground_floor(surf, SCROLL, _DAY, PHASE)


def _plant(surf, cx, base_y, variant, scale=1.0):
    """Draw one static greenery design with feet at (cx, base_y). `scale` < 1 sets a
    plant further back on the deck (smaller + higher); rendered to a temp surface
    then NEAREST-scaled so the silhouette stays crisp."""
    v = fv.get("greenery", variant)
    if v is None:
        return
    if abs(scale - 1.0) < 1e-3:
        _green.draw_greenery(surf, cx, base_y, v, 0.0, _POSE(variant))
        return
    tw, th = 150, 220
    tmp = pygame.Surface((tw, th), pygame.SRCALPHA)
    _green.draw_greenery(tmp, tw // 2, th - 4, v, 0.0, _POSE(variant))
    sw, sh = int(tw * scale), int(th * scale)
    scaled = pygame.transform.scale(tmp, (sw, sh))
    # feet of the temp were at (tw//2, th-4); after scale they sit at (sw//2, sh-4*scale)
    surf.blit(scaled, (cx - sw // 2, base_y - (sh - int(4 * scale))))


def _lamp(surf, sx):
    fp.draw_prop_lamp(surf, sx, _DAY, t=0.0, variant=31)


# ── the five formation treatments ────────────────────────────────────────────
# Each places greenery on a frame that already holds the clean background; pillars
# + coin are drawn afterward. All clusters sit in the FAR/mid sidewalk band (feet
# ~GROUND_Y), lifted off the very-bottom near edge the user disliked.

GY = GROUND_Y - 1

def t1_triads(surf):
    """1 · Tight triads — tall centre + 2 short flankers, steady ~130px rhythm."""
    centres = [(64, 9), (196, 13), (328, 17)]      # x, tall-variant
    flank = [(0, 20), (4, 11)]                      # short flanker variants
    for cx, tall in centres:
        _plant(surf, cx - 24, GY, flank[0][1], 0.86)
        _plant(surf, cx + 26, GY, flank[1][1], 0.86)
        _plant(surf, cx, GY, tall, 1.0)

def t2_pairs(surf):
    """2 · Loose alternating pairs — one tall + one low, tall side alternates."""
    pairs = [(52, 13, 80, 4, "L"), (175, 23, 200, 6, "R"), (300, 0, 326, 29, "R")]
    for ax, av, bx, bv, side in pairs:
        # 'side' decides which member is the tall one (drawn last/front)
        _plant(surf, ax, GY, av, 0.92)
        _plant(surf, bx, GY, bv, 1.0)

def t3_fixtures(surf):
    """3 · Clustered against fixtures — 2-3 plants tucked beside lamp posts."""
    for lx in (96, 268):
        _lamp(surf, lx)
    _plant(surf, 72, GY, 4, 0.9); _plant(surf, 118, GY, 9, 1.0)
    _plant(surf, 244, GY, 11, 0.9); _plant(surf, 292, GY, 13, 1.0); _plant(surf, 270, GY, 16, 0.78)

def t4_twodepth(surf):
    """4 · Staggered two-depth — back row higher/smaller, front row lower/larger."""
    for cx, back, front in [(78, 1, 0), (210, 6, 23), (330, 29, 20)]:
        _plant(surf, cx + 14, GY - 8, back, 0.66)    # back row: lifted + small
        _plant(surf, cx - 10, GY + 2, front, 1.05)   # front row: lower + larger

def t5_beds(surf):
    """5 · Raised planter beds — triads with low groundcover between, lamp every
    other bed; reads as deliberate municipal street planting."""
    beds = [(64, 9), (196, 18), (328, 26)]
    low_between = [(130, 16), (262, 8)]
    _lamp(surf, 130)
    for cx, tall in beds:
        _plant(surf, cx - 22, GY, 4, 0.8)
        _plant(surf, cx + 24, GY, 11, 0.8)
        _plant(surf, cx, GY, tall, 1.0)
    for cx, v in low_between:
        _plant(surf, cx, GY + 2, v, 0.72)


TREATMENTS = [
    ("1 · TIGHT TRIADS — tall centre + 2 short flankers, steady street rhythm, set back in the mid band", t1_triads),
    ("2 · ALTERNATING PAIRS — one tall + one low per cluster, tall side alternates down the lane", t2_pairs),
    ("3 · AGAINST FIXTURES — 2-3 plants tucked beside the lamp posts as intentional planting", t3_fixtures),
    ("4 · STAGGERED TWO-DEPTH — a lifted small back-row plant + a lower larger front plant lift the eye", t4_twodepth),
    ("5 · RAISED PLANTER BEDS — triads + low groundcover between, lamp-anchored every other bed", t5_beds),
]

# A single right-edge pillar for real-gameplay context without occluding the
# centre clusters under review (x, gap_y, gap_h).
COLUMNS = [(338, 250, 150)]
CROP = (0, 388, W, 252)     # focus on the sidewalk band + a little sky


def _panel(title, place):
    frame = pygame.Surface((W, H))
    _clean_background(frame)
    sc._draw_pillars(frame, _DAY, PHASE, COLUMNS)
    place(frame)
    sc._gold_coin(frame, int(W * 0.62), int(H * 0.66), r=9)
    cx, cy, cw, ch = CROP
    band = frame.subsurface(pygame.Rect(cx, cy, cw, ch)).copy()
    out = pygame.Surface((cw, ch + 20))
    bar = pygame.Surface((cw, 20)); bar.fill((20, 22, 30))
    out.blit(bar, (0, 0))
    sc._text(out, title, 8, 4, 10, (236, 230, 216), bold=True)
    out.blit(band, (0, 20))
    return out


def run():
    panels = [_panel(t, fn) for t, fn in TREATMENTS]
    pw = panels[0].get_width()
    head = 46
    gap = 8
    ph = panels[0].get_height()
    sheet = pygame.Surface((pw, head + len(panels) * (ph + gap)))
    sheet.fill((232, 226, 214))
    sc._text(sheet, "GREENERY — CLUSTER FORMATION STUDY (round 1)", 10, 10, 17,
             (44, 38, 32), bold=True)
    sc._text(sheet, "Static (scroll-only) plants, raised off the bottom edge, in small "
             "deliberate clusters — 5 arrangement rules. Composition only; 30 designs unchanged.",
             10, 30, 10, (108, 98, 84))
    y = head
    for p in panels:
        sheet.blit(p, (0, y))
        y += p.get_height() + gap
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "round_1.png")
    pygame.image.save(sheet, path)
    print("saved", path, sheet.get_size())
    return path


if __name__ == "__main__":
    run()
