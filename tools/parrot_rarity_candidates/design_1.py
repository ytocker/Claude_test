"""design_1 · STORM MACAW — EPIC parrot rarity-spectrum exploration.

A stormcloud-slate macaw crackling with electricity. The signature is ONE
bold energy zone: a single ASYMMETRIC zig-zag lightning bolt discharging UP
past the crown to break the silhouette, with one short fork, a charged cyan
wingtip glow + tick, a faint cyan back rim-light, and two static spark dots
hugging the bolt. Pip keeps his gold aviators — only the body is re-plumaged.

The 40px truth-read is carried by that one bolt: it kinks hard left-right-left
(with a deliberate lateral zag mid-climb so it reads as lightning, never an
antenna) and tapers thick-root → spark-white tip, so the discharge direction
and the bolt silhouette survive the downscale on both day and night sky. Cyan
is held off the near-black slate by a soft additive head-glow painted BEHIND
the body, so the charge separates from the body mass without smearing — hence
the custom compose (back glow → slate body → front bolt/spark overlay) rather
than the body-first _make_skin.

Scratch only — never registered in store_skins.BUILDERS.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline
from game.draw import blit_glow
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, PARROT_DY


# ── palette: stormcloud slate body, cool pale belly, gold aviators kept ───────
_SLATE      = (70, 80, 110)         # #46506E body main
_SLATE_DEEP = (42, 58, 90)          # #2A3A5A deep shadow / line work
_CYAN       = (127, 227, 255)       # #7FE3FF electric cyan
_SPARK      = (200, 244, 255)       # #C8F4FF spark white
_GOLD       = (255, 210, 74)        # #FFD24A aviator gold (kept)

P_STORM = _pal(
    tail=[(40, 54, 84), (50, 64, 96), (62, 76, 108), (78, 92, 124)],
    tail_line=(28, 40, 64),
    body_shadow=(40, 54, 84),
    body_main=_SLATE,
    body_chest=(92, 104, 138),
    body_belly=(120, 134, 166),     # cool pale belly
    sheen=(190, 220, 255, 80),
    wing_main=(58, 70, 102),
    wing_dark=(34, 46, 72),
    wing_tip=(96, 112, 150),
    wing_secondary=None,
    wing_highlight=(150, 178, 215),
    head_shadow=(40, 54, 84),
    head_main=_SLATE,
    head_cheek=(96, 110, 144),
    head_crown=(82, 96, 130),
    # Gold aviators kept — Pip's signature stays on the storm bird.
    lens_frame=_GOLD,
    lens_body=(18, 24, 44),
    lens_tint=(90, 150, 200, 120),
    lens_glint=(220, 245, 255),
    beak_main=(70, 80, 104),
    beak_dark=(34, 44, 66),
    beak_gloss=(150, 170, 200),
    foot=(54, 62, 84),
)


def _back_glow(surf):
    # Soft additive charge behind the head — keeps the cyan crest/sparks reading
    # off the near-black slate without painting a hard ring on the body. Faint
    # by design so day skies don't blow out and the bolt tips stay the brightest
    # note. Painted FIRST, under the body.
    blit_glow(surf, HX, CROWN_Y + 4, 18, (60, 150, 200), alpha=90)
    blit_glow(surf, HX, CROWN_Y - 4, 11, (110, 200, 240), alpha=80)


def _bolt(surf, pts, *, root_w=3, fork=None):
    # One jagged bolt, drawn segment-by-segment so the stroke TAPERS from a fat
    # 3px root at the crown down to a bright 2px spark tip — the value+width
    # gradient that gives the discharge a direction and reads as lightning, not
    # a fixed-width antenna. A deep-slate keyline under each segment keeps cyan
    # off the slate body; spark-white takes over the final two segments.
    n = len(pts) - 1
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        t = i / max(1, n - 1)              # 0 at root → 1 at tip
        w = max(2, round(root_w - t * (root_w - 2)))
        pygame.draw.line(surf, _SLATE_DEEP, a, b, w + 1)
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        col = _SPARK if i >= n - 2 else _CYAN
        t = i / max(1, n - 1)
        w = max(2, round(root_w - t * (root_w - 2)))
        pygame.draw.line(surf, col, a, b, w)
    # One short fork branching off a mid-bolt vertex — the single permitted fork,
    # thin so it never reads as a second tine.
    if fork is not None:
        f0, f1 = fork
        pygame.draw.line(surf, _SLATE_DEEP, f0, f1, 3)
        pygame.draw.line(surf, _CYAN, f0, f1, 2)
        pygame.draw.circle(surf, _SPARK, f1, 1)
    tip = pts[-1]
    pygame.draw.circle(surf, _SPARK, tip, 2)
    pygame.draw.circle(surf, (255, 255, 255), (tip[0], tip[1] - 1), 1)


def _paint_storm(surf, wing_angle_deg):
    # Faint cyan rim-light tracing the back/underside silhouette that faces open
    # sky, so the slate mass keeps a charged edge against dark night backgrounds.
    pygame.draw.lines(surf, _CYAN, False,
                      [(14, 38), (22, 44), (30, 47), (40, 46), (47, 41)], 1)

    # ONE asymmetric lightning bolt discharging up off the crown. Vertices kink
    # hard left → right → left as it climbs, and the mid-bolt makes a deliberate
    # LATERAL zag (the third vertex jumps right of the root before the tip cuts
    # back left) so the silhouette breaks vertical sameness and reads as a real
    # bolt rather than a straight antenna. Rooted just left of head-centre, the
    # tip overshoots well past CROWN_Y to break the egg outline. A single short
    # fork peels off the lateral elbow — the only branch, kept thin.
    base_y = CROWN_Y + 3
    crest = [
        (HX - 1, base_y),          # root on the crown
        (HX - 6, base_y - 6),      # kink LEFT
        (HX + 3, base_y - 11),     # hard kink RIGHT — the lateral zag
        (HX - 4, base_y - 17),     # cut back LEFT
        (HX + 2, base_y - 27),     # spark tip, overshooting the crown
    ]
    _bolt(surf, crest, root_w=3,
          fork=((HX + 3, base_y - 11), (HX + 10, base_y - 13)))

    # Charged electric-cyan wingtip: the glow carries this zone (a micro-bolt is
    # invisible at 40px), so just a soft cyan glow + one ≥2px cyan tick with a
    # spark core — the second, quieter energy note tying the wing to the crest.
    wtx, wty = 46, 44
    blit_glow(surf, wtx, wty, 8, (80, 180, 220), alpha=130)
    pygame.draw.circle(surf, _CYAN, (wtx, wty), 3)
    pygame.draw.circle(surf, _SPARK, (wtx, wty), 2)
    pygame.draw.circle(surf, (255, 255, 255), (wtx, wty - 1), 1)

    # Two static spark motes hugging the bolt — each a cyan core with a spark-
    # white centre (≥2px) so they survive downscale; placed tight to the crest
    # tips so they read as charge crackling off the bolt, not orbiting noise.
    for sx, sy in ((HX + 7, base_y - 22), (HX - 7, base_y - 13)):
        pygame.draw.circle(surf, _CYAN, (sx, sy), 2)
        pygame.draw.circle(surf, _SPARK, (sx, sy), 1)


def _storm_getter():
    # The head-glow must sit BEHIND the body (so cyan reads off near-black slate),
    # so the body-first order in _make_skin can't be used: glow -> slate body ->
    # bolt/spark overlay -> outline. Mirrors _make_skin's lazy flat-build + per-
    # (frame, 3°-bucket) rotation cache.
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _back_glow(comp)
        comp.blit(_build_parrot_with_palette(wing_angle, P_STORM), (0, PARROT_DY))
        _paint_storm(comp, wing_angle)
        return _add_outline(comp)

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_flat(a) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


build = _storm_getter()
