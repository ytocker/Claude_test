"""design_2 · KOI MACAW — EPIC parrot-wave2 exploration.

A lacquer-white "lucky carp" Pip: a kohaku koi recoloured body marbled with
bold orange/black blotches edged in a thin gold sumi line, a soft swept
koi-FIN crest arcing past the crown, and long trailing fin-like tail
STREAMERS rippling out behind the tail so the bird reads like a carp swimming
through air. Warm but never fiery — the energy is paint + water, not glow,
which keeps it clear of MAGMA/SOLAR; the orange-on-white organic marbling and
finned streamers keep it clear of GLACIER's cold ice geometry too.

Draw order matters: the trailing fin streamers (and their drifting water
bubbles) must paint BEHIND the body so they ripple out from under the tail,
not over it. That rules out store_skins._make_skin's body-first `_compose`,
so — mirroring the AURORA / viking-axe pattern — this is a custom getter:
back layer (streamers + bubbles) → lacquer-recoloured body → front overlay
(koi marbling + gold sumi edge + fin crest + amber lenses re-glint) → house
outline → per-(frame, 3°-bucket) rotation cache.

The streamers sweep with the wing beat so the baked frames still feel alive.
Exploration only — NEVER registered in store_skins.BUILDERS.
"""
import math

import pygame

from game.parrot import _WING_ANGLES, _add_outline
from game.draw import lerp_color
from game.store_skins import (
    COMPOSITE_W, COMPOSITE_H, PARROT_DY, HX, HY, CROWN_Y,
)
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette (brief) ───────────────────────────────────────────────────────────
_WHITE   = (255, 255, 255)        # #FFFFFF lacquer white
_ORANGE  = (242, 99, 43)          # #F2632B koi orange
_ORANGE_D = (196, 64, 22)         # deeper orange for marbling cores / shadow
_ORANGE_H = (255, 150, 96)        # lit orange edge
_INK     = (28, 28, 34)           # #1C1C22 ink black markings
_GOLD    = (232, 196, 90)         # #E8C45A gold sumi edge
_GOLD_H  = (255, 232, 160)        # bright gold glint
_BUBBLE  = (159, 216, 224)        # #9FD8E0 water-bubble accent
_BUBBLE_H = (224, 248, 252)       # bubble rim shine
_IVORY_SH = (226, 218, 204)       # warm ivory shadow line

# Lacquer-white (kohaku) re-plumage. The white body is the canvas the painted
# blotches sit on, so every slot is a warm-leaning white with a soft ivory
# shadow doing the line work — kept off pure grey so it never reads as plastic
# on a bright day sky, yet bright enough to never be swallowed by night. The
# wing is the one slot pre-tinted orange so the wing-tip already carries koi
# colour before the marbling overlay lands. Aviators stay, tinted warm amber.
_KOI_PAL = _pal(
    tail=[(236, 228, 214), (244, 238, 226), (250, 246, 238), (255, 253, 248)],
    tail_line=_IVORY_SH,
    body_shadow=(228, 218, 202),
    body_main=(252, 250, 244),
    body_chest=_WHITE,
    body_belly=(246, 242, 234),
    sheen=(255, 255, 255, 150),
    wing_main=(250, 244, 234),
    wing_dark=(214, 198, 180),
    wing_tip=_ORANGE,
    wing_secondary=None,
    wing_highlight=_WHITE,
    head_shadow=(228, 218, 202),
    head_main=(252, 250, 244),
    head_cheek=_WHITE,
    head_crown=(255, 253, 248),
    lens_frame=(214, 170, 96),
    lens_body=(40, 28, 18),
    lens_tint=(255, 176, 92, 150),       # warm amber lens tint
    lens_glint=(255, 244, 222),
    beak_main=(244, 180, 110),
    beak_dark=(176, 110, 56),
    beak_gloss=(255, 230, 188),
    foot=(208, 150, 96),
)


def _koi_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _KOI_PAL)


# ── shared helpers ────────────────────────────────────────────────────────────

def _flap_phase(angle_deg):
    """0 on the down-stroke (wing 50°) → 1 on the up-stroke (-40°). The fin
    streamers stream long/loose on the up-beat and bunch on the down-beat so
    the baked four frames still feel like the carp is rippling through air."""
    return 1.0 - (angle_deg + 40) / 90.0


def _smooth_curve(p0, p1, p2, steps=10):
    """Quadratic-Bezier sample list — fin streamers and the crest must read as
    smooth flowing curves, not the straight 3-point rods a polyline gives at
    40px."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


# ── back layer: trailing fin streamers + drifting water bubbles ───────────────

def _koi_back(surf, angle_deg):
    """Long flowing fin-like tail streamers rippling out behind the tail, plus
    a few water bubbles drifting up — all BEHIND the body so they read as the
    carp's trailing fins, not body paint. Each streamer is a tapering white→
    orange membrane (a filled translucent band) over a thin opaque spine, so it
    survives both a bright day sky (the opaque spine carries it) and a dark
    night sky (the white root stays high-value). The fins sway with the flap."""
    phase = _flap_phase(angle_deg)
    reach = 26 + int(phase * 8)              # fins extend on the up-beat
    droop = (1.0 - phase) * 4                # and dip on the down-beat

    # Three overlapping fin streamers fanning down-back out of the tail root.
    # k spreads them vertically; each is an S-curve (two control bows pulling
    # the spine opposite ways) so it ripples like a swimming carp's caudal fin.
    def fin_path(k):
        bx, by = 12, HY + 6 + k * 5          # tail-root anchor (left of body)
        c1 = (bx - reach * 0.40, by - 2 + k * 2)              # bow up first
        c2 = (bx - reach * 0.78, by + 8 + k * 4 + droop)      # then down → S
        tip = (bx - reach, by + 13 + k * 6 + droop)
        return _smooth_curve((bx, by), c1, c2, steps=7) + \
            _smooth_curve(c2, ((c2[0] + tip[0]) / 2, tip[1] - 1), tip, steps=5)

    for k in range(3):
        path = fin_path(k)
        # White at the root → koi orange at the trailing tip, the lucky-carp ramp.
        tipcol = lerp_color(_ORANGE_H, _ORANGE, k / 2.0)
        # Translucent membrane: fill between the spine and an offset lower edge
        # so each fin reads as a soft finned vane, not a wire.
        edge = [(x, y + 5 + k) for x, y in path]
        pygame.draw.polygon(surf, (*tipcol, 90), path + edge[::-1])
        # Thin ivory backing keeps a crisp edge on a bright sky; bright spine
        # over it; orange tip glint so the trailing end reads as koi colour.
        pygame.draw.lines(surf, (*_IVORY_SH, 200), False, path, 4)
        pygame.draw.lines(surf, _WHITE, False, path[:len(path) // 2], 3)
        pygame.draw.lines(surf, tipcol, False, path[len(path) // 2 - 1:], 2)
        pygame.draw.circle(surf, _ORANGE, (int(path[-1][0]), int(path[-1][1])), 2)
        # A few soft fin-ray ticks across the membrane sell the carp-fin texture.
        for ti in (0.45, 0.7):
            i = int(len(path) * ti)
            sx, sy = path[i]
            pygame.draw.line(surf, (*tipcol, 150), (sx, sy), (sx + 2, sy + 5 + k), 1)

    # Water bubbles drifting up off the back — the watery signature tell. A
    # cool cyan rim + bright shine so they read as water, the only cool accent
    # on an otherwise warm skin. Fixed scatter so the 4 frames stay stable.
    for bx, by, r in ((6, HY - 8, 3), (16, HY - 16, 2), (3, HY + 2, 2),
                      (11, HY - 2, 2)):
        pygame.draw.circle(surf, (*_BUBBLE, 150), (bx, by), r)
        pygame.draw.circle(surf, _BUBBLE, (bx, by), r, 1)
        pygame.draw.circle(surf, _BUBBLE_H, (bx - 1, by - 1), 1)


# ── front overlay: koi marbling + gold sumi + fin crest + face re-assert ──────

def _blotch(surf, pts, *, ink=False):
    """One painted koi patch: a bold orange (or ink) marbled blob edged with a
    thin gold sumi line, exactly as hand-painted urushi koi scales are outlined.
    A darker core gives the patch dimension so it doesn't read as a flat sticker."""
    main = _INK if ink else _ORANGE
    core = (12, 12, 16) if ink else _ORANGE_D
    pygame.draw.polygon(surf, main, pts)
    # Inner darker core, inset toward the centroid so the patch has a lit edge.
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    inner = [(cx + (x - cx) * 0.5, cy + (y - cy) * 0.5) for x, y in pts]
    pygame.draw.polygon(surf, core, inner)
    if not ink:
        pygame.draw.polygon(surf, _ORANGE_H, inner, 1)
    # Thin gold sumi edge tracing the patch — the signature urushi outline.
    pygame.draw.polygon(surf, _GOLD, pts, 1)


def _koi_front(surf, angle_deg):
    """Painted OVER the lacquer body and INSIDE the masked layer (crisp opaque
    detail only): the koi blotch pattern with gold sumi edges, the swept koi-fin
    crest past the crown, and a re-asserted amber-lensed face so Pip survives
    the 40px downscale."""
    # ── koi blotch pattern: 3 bold orange patches + 1 ink patch over the white
    # body. Placed on the back/wing/cheek so the white belly stays clean and the
    # marbling reads as a hand-painted kohaku koi, not noise. Coords in composite
    # space (body ellipse roughly x∈[13,53], y∈[38,66]).
    _blotch(surf, [(18, 42), (27, 39), (31, 46), (26, 52), (18, 50)])      # back/shoulder
    _blotch(surf, [(34, 47), (44, 45), (47, 53), (40, 58), (33, 54)])      # mid-wing
    _blotch(surf, [(24, 55), (31, 54), (33, 61), (26, 63), (21, 59)])      # lower belly-edge
    _blotch(surf, [(40, 41), (47, 42), (45, 47), (39, 46)], ink=True)      # small ink patch on the back

    # A small ink fleck + an orange fleck near the wing root add the marbled
    # broken-edge look real koi have, without becoming busy.
    pygame.draw.circle(surf, _INK, (49, 49), 2)
    pygame.draw.polygon(surf, _GOLD, [(47, 49), (51, 47), (51, 51), (47, 51)], 1)

    # Cheek koi-mark — a single orange teardrop on the head so the face also
    # carries the kohaku pattern, gold-edged to match.
    cheek = [(HX - 9, HY - 1), (HX - 3, HY - 3), (HX - 2, HY + 3), (HX - 8, HY + 4)]
    pygame.draw.polygon(surf, _ORANGE, cheek)
    pygame.draw.polygon(surf, _ORANGE_D, [(HX - 8, HY), (HX - 4, HY - 1),
                                          (HX - 4, HY + 2), (HX - 7, HY + 3)])
    pygame.draw.polygon(surf, _GOLD, cheek, 1)

    # ── swept koi-FIN crest past the crown: two flowing orange-and-white finned
    # plumes arcing UP and slightly back off the crown (soft, never spikes). Each
    # is a white→orange tapering fin with a couple of gold ray lines, so it reads
    # as a carp's dorsal fin breaking the silhouette, not a cockatoo crest.
    crest_root = (HX - 2, CROWN_Y + 2)
    for dx, lean, t in ((-7, -6, 0.0), (4, 7, 1.0)):
        tip = (crest_root[0] + dx, CROWN_Y - 16)
        ctrl = (crest_root[0] + dx * 0.4 + lean, CROWN_Y - 8)
        spine = _smooth_curve(crest_root, ctrl, tip, steps=9)
        col = lerp_color(_ORANGE_H, _ORANGE, t)
        # Membrane fin: a filled vane between the spine and an offset trailing edge.
        edge = [(x + lean * 0.18, y + 4) for x, y in spine]
        pygame.draw.polygon(surf, (*col, 170), spine + edge[::-1])
        pygame.draw.lines(surf, _ORANGE_D, False, spine, 3)
        pygame.draw.lines(surf, _WHITE, False, spine[:len(spine) // 2], 2)
        pygame.draw.lines(surf, col, False, spine[len(spine) // 2 - 1:], 2)
        # Gold sumi ray + tip glint.
        pygame.draw.line(surf, _GOLD, spine[2], (spine[2][0] + lean * 0.3, spine[2][1] - 6), 1)
        pygame.draw.circle(surf, _GOLD_H, (int(tip[0]), int(tip[1])), 1)
    # A small gold root knot ties the two plumes into one crest base.
    pygame.draw.circle(surf, _GOLD, crest_root, 2)
    pygame.draw.circle(surf, _GOLD_H, (crest_root[0], crest_root[1] - 1), 1)

    # ── re-assert Pip's face at 40px: a bright specular glint on the near amber
    # lens and a sharpened beak top edge so the macaw identity survives downscale.
    pygame.draw.circle(surf, (255, 244, 222), (HX + 6, HY - 3), 2)
    pygame.draw.line(surf, _GOLD_H, (HX + 8, HY + 1), (HX + 13, HY + 4), 1)  # beak top edge


# ── custom compose + getter (streamers/bubbles need a back layer) ─────────────

def _koi_getter():
    """back fins+bubbles → lacquer body → front marbling/crest/face → house
    outline, then the per-(frame, 3°-bucket) rotation cache shared by every
    store skin.

    The house outline is grown from the alpha mask, so the soft translucent fin
    membranes + bubbles must NOT be in the masked layer — else the dark rim
    would box each fin into its own island. So outline the OPAQUE bird (body +
    front overlay) alone, then lay the back layer UNDER it, padded to match the
    outline growth so the bird stays centred for the rotation maths."""
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        bird = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        bird.blit(_koi_base(wing_angle), (0, PARROT_DY))
        _koi_front(bird, wing_angle)
        bird = _add_outline(bird)

        out = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
        pad = (bird.get_width() - COMPOSITE_W) // 2
        back = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _koi_back(back, wing_angle)
        out.blit(back, (pad, pad))
        out.blit(bird, (0, 0))
        return out

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


build = _koi_getter()
