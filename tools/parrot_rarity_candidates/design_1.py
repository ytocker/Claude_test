"""design_1 · STORM MACAW — EPIC parrot rarity-spectrum exploration.

A stormcloud-slate macaw crackling with electricity. The signature is ONE
bold energy zone: a jagged 3-prong cyan lightning crest spiking UP past the
crown to break the silhouette, a charged cyan wingtip with one forked
micro-bolt, a faint cyan back rim-light, and a few static spark dots orbiting
the head. Pip keeps his gold aviators — only the body is re-plumaged slate.

The 40px truth-read is carried by the lightning crest: the highest-value cyan
sits at the prong TIPS (spark-white cores) so the zig-zag silhouette reads as
a bolt against both day and night sky. Cyan is held off the near-black slate
by a soft additive head-glow painted BEHIND the body, so the charge separates
from the body mass without smearing — hence the custom compose (back glow →
slate body → front bolt/spark overlay) rather than the body-first _make_skin.

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


def _bolt(surf, pts):
    # A jagged lightning prong: deep-slate keyline first so cyan never abuts the
    # slate body directly, then a cyan core, brightest spark-white at the TIP —
    # the value gradient that makes the zig-zag read as a charged bolt at 40px.
    pygame.draw.lines(surf, _SLATE_DEEP, False, pts, 4)
    pygame.draw.lines(surf, _CYAN, False, pts, 3)
    pygame.draw.lines(surf, _SPARK, False, pts[-2:], 2)
    tip = pts[-1]
    pygame.draw.circle(surf, _SPARK, tip, 2)
    pygame.draw.circle(surf, (255, 255, 255), (tip[0], tip[1] - 1), 1)


def _paint_storm(surf, wing_angle_deg):
    # Faint cyan rim-light tracing the back/underside silhouette that faces open
    # sky, so the slate mass keeps a charged edge against dark night backgrounds.
    pygame.draw.lines(surf, _CYAN, False,
                      [(14, 38), (22, 44), (30, 47), (40, 46), (47, 41)], 1)

    # 3-prong jagged lightning crest spiking UP past CROWN_Y. The middle prong
    # overshoots highest so the bolt clearly breaks the egg silhouette; the side
    # prongs zig the opposite way so the cluster reads as forked lightning, not
    # three parallel feathers. Roots sit on the crown so the bolt looks rooted in
    # the head, not floating.
    base_y = CROWN_Y + 3
    _bolt(surf, [(HX - 2, base_y), (HX - 7, base_y - 7),
                 (HX - 3, base_y - 9), (HX - 10, base_y - 19)])
    _bolt(surf, [(HX + 1, base_y), (HX + 5, base_y - 9),
                 (HX, base_y - 12), (HX + 4, base_y - 25)])
    _bolt(surf, [(HX + 3, base_y - 1), (HX + 9, base_y - 6),
                 (HX + 6, base_y - 9), (HX + 13, base_y - 16)])

    # Charged electric-cyan wingtip glow + one forked micro-bolt arcing off the
    # LEADING wingtip into open sky — the second energy zone that ties the wing
    # to the crest. Wing leading tip sits up-right of the body in this pose.
    wtx, wty = 46, 44
    blit_glow(surf, wtx, wty, 7, (80, 180, 220), alpha=120)
    pygame.draw.circle(surf, _CYAN, (wtx, wty), 2)
    pygame.draw.circle(surf, _SPARK, (wtx, wty), 1)
    # Forked micro-bolt: a short zig with a single fork, brightest at both tips.
    fork = [(wtx + 1, wty - 1), (wtx + 6, wty - 4), (wtx + 4, wty - 6),
            (wtx + 10, wty - 9)]
    pygame.draw.lines(surf, _SLATE_DEEP, False, fork, 3)
    pygame.draw.lines(surf, _CYAN, False, fork, 2)
    pygame.draw.line(surf, _CYAN, (wtx + 4, wty - 6), (wtx + 8, wty - 3), 2)
    pygame.draw.circle(surf, _SPARK, (wtx + 10, wty - 9), 2)
    pygame.draw.circle(surf, _SPARK, (wtx + 8, wty - 3), 1)

    # 3 static spark dots orbiting the head — small charged motes, each a cyan
    # core with a spark-white centre so they survive downscale (≥2px cores).
    for sx, sy in ((HX - 13, CROWN_Y + 6), (HX + 14, HY - 4), (HX + 4, CROWN_Y - 7)):
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
