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
_SUMI    = (150, 86, 24)          # darker red-gold sumi outline — survives 40px
_BUBBLE  = (159, 216, 224)        # #9FD8E0 water-bubble accent
_BUBBLE_H = (224, 248, 252)       # bubble rim shine
_CYAN    = (120, 198, 212)        # cool fin-tip glaze (ties to the bubbles)
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

    # TWO bold fin streamers fanning down-back out of the tail root (was three —
    # fewer + thicker reads better at 40px). k spreads them vertically; each is
    # an S-curve (two control bows pulling the spine opposite ways) so it ripples
    # like a swimming carp's caudal fin.
    def fin_path(k):
        bx, by = 12, HY + 6 + k * 7          # tail-root anchor (left of body)
        c1 = (bx - reach * 0.40, by - 2 + k * 2)              # bow up first
        c2 = (bx - reach * 0.78, by + 8 + k * 5 + droop)      # then down → S
        tip = (bx - reach, by + 13 + k * 7 + droop)
        return _smooth_curve((bx, by), c1, c2, steps=7) + \
            _smooth_curve(c2, ((c2[0] + tip[0]) / 2, tip[1] - 1), tip, steps=5)

    for k in range(2):
        path = fin_path(k)
        n = len(path)
        # Translucent membrane: fill between the spine and an offset lower edge
        # so each fin reads as a soft finned vane, not a wire. Wider band so the
        # fin has body even after the 40px downscale.
        edge = [(x, y + 6 + k * 2) for x, y in path]
        pygame.draw.polygon(surf, (*_ORANGE, 95), path + edge[::-1])
        # Held ≥2px throughout: a dark sumi backing for crisp edges on any sky,
        # a white→orange warm body, then a COOL cyan→gold tip break so the
        # trailing end reads on a dark night sky (warm-on-warm was dying at 40px)
        # and the cool note frames the silhouette, tying to the bubbles.
        pygame.draw.lines(surf, _SUMI, False, path, 5)
        pygame.draw.lines(surf, _WHITE, False, path[:n // 2], 3)
        pygame.draw.lines(surf, _ORANGE, False, path[n // 2 - 1:int(n * 0.78)], 3)
        pygame.draw.lines(surf, _CYAN, False, path[int(n * 0.78) - 1:], 2)
        pygame.draw.circle(surf, _GOLD_H, (int(path[-1][0]), int(path[-1][1])), 2)
        # Soft fin-ray ticks across the membrane sell the carp-fin texture.
        for ti in (0.45, 0.7):
            i = int(n * ti)
            sx, sy = path[i]
            pygame.draw.line(surf, (*_ORANGE_H, 150), (sx, sy), (sx + 2, sy + 6 + k * 2), 1)

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
    darker red-gold sumi line, exactly as hand-painted urushi koi scales are
    outlined. A darker core gives the patch dimension so it doesn't read as a
    flat sticker, and the sumi edge is held at 2px so it survives the 40px
    downscale instead of vanishing."""
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
    # Sumi edge: a 2px DARK red-gold line under a 1px bright gold highlight, so
    # the outline holds at 40px (the bright gold alone washed out against orange)
    # and still glints up close — the signature urushi keyline.
    pygame.draw.polygon(surf, _SUMI, pts, 2)
    pygame.draw.polygon(surf, _GOLD, pts, 1)


def _koi_front(surf, angle_deg):
    """Painted OVER the lacquer body and INSIDE the masked layer (crisp opaque
    detail only): the koi blotch pattern with gold sumi edges, the swept koi-fin
    crest past the crown, and a re-asserted amber-lensed face so Pip survives
    the 40px downscale."""
    # ── koi blotch pattern: exactly THREE bold orange patches over the white
    # body, with clear white-lacquer GAPS between them — the kohaku read comes
    # from negative space, not the quantity of orange, so no flecks and no extra
    # ink patch (both were noise at 1×). Placed back / mid-wing / lower-belly,
    # spaced so a clean white channel runs between each. Coords in composite
    # space (body ellipse roughly x∈[13,53], y∈[38,66]).
    _blotch(surf, [(17, 41), (28, 38), (32, 46), (27, 53), (18, 51)])      # broad back/shoulder
    _blotch(surf, [(37, 48), (47, 47), (48, 55), (41, 60), (36, 54)])      # mid-wing
    _blotch(surf, [(22, 57), (30, 56), (32, 63), (24, 65), (20, 61)])      # lower belly-edge

    # Cheek koi-mark — a single orange teardrop on the head so the face also
    # carries the kohaku pattern, sumi-edged to match.
    cheek = [(HX - 9, HY - 1), (HX - 3, HY - 3), (HX - 2, HY + 3), (HX - 8, HY + 4)]
    pygame.draw.polygon(surf, _ORANGE, cheek)
    pygame.draw.polygon(surf, _ORANGE_D, [(HX - 8, HY), (HX - 4, HY - 1),
                                          (HX - 4, HY + 2), (HX - 7, HY + 3)])
    pygame.draw.polygon(surf, _SUMI, cheek, 1)

    # ── swept koi-FIN crest: a SINGLE broad dorsal-fin membrane sweeping
    # BACKWARD over the crown in the flight direction (toward the tail, i.e.
    # leftward), wider than it is tall, with a WEBBED scalloped trailing edge.
    # The previous two narrow up-and-apart plumes read as antlers; one swept
    # webbed sheet that lies low and back along the skull is unmistakably a koi's
    # soft dorsal fin instead. A leading spine runs root→front-tip; the trailing
    # edge scallops down to the crown so the whole thing reads as one fin, and a
    # slight asymmetry (a longer front lobe) keeps it organic, never a symmetric
    # crown.
    root = (HX + 6, CROWN_Y + 1)             # springs from the FRONT of the crown
    # Leading spine: a low backward arc to the swept rear tip, past the skull.
    front_tip = (HX + 9, CROWN_Y - 9)        # short front lobe, slightly up
    rear_tip = (HX - 16, CROWN_Y - 4)        # long rear sweep, low and back
    lead = _smooth_curve((HX + 7, CROWN_Y - 5), front_tip,
                         (HX + 2, CROWN_Y - 8), steps=5) + \
        _smooth_curve((HX + 2, CROWN_Y - 8), (HX - 8, CROWN_Y - 9), rear_tip, steps=8)
    # Webbed trailing edge scalloping back down to the crown — the fin's webbing.
    web_base = [(HX - 14, CROWN_Y), (HX - 9, CROWN_Y + 3), (HX - 4, CROWN_Y + 1),
                (HX + 1, CROWN_Y + 3), (HX + 6, CROWN_Y + 1)]
    fin = lead + web_base[::-1] + [root]
    # Translucent membrane fill, white→orange from leading edge to webbing.
    pygame.draw.polygon(surf, (*_ORANGE, 150), fin)
    pygame.draw.polygon(surf, (*_WHITE, 110),
                        [front_tip, (HX + 2, CROWN_Y - 7), root, (HX + 6, CROWN_Y)])
    # Sumi-dark leading spine held ≥2px, white root half → orange swept tip, then
    # a cool cyan glaze on the rear tip tying the fin to the bubbles + streamers.
    n = len(lead)
    pygame.draw.lines(surf, _SUMI, False, lead, 3)
    pygame.draw.lines(surf, _WHITE, False, lead[:n // 2], 2)
    pygame.draw.lines(surf, _ORANGE, False, lead[n // 2 - 1:int(n * 0.8)], 2)
    pygame.draw.lines(surf, _CYAN, False, lead[int(n * 0.8) - 1:], 2)
    # Fin rays: a few gold ray lines fanning from the root through the membrane,
    # the urushi-painted detail that sells "fin" up close.
    for tx, ty in ((HX + 6, CROWN_Y - 6), (HX - 1, CROWN_Y - 6), (HX - 9, CROWN_Y - 5)):
        pygame.draw.line(surf, _GOLD, (root[0] - 1, CROWN_Y), (tx, ty), 1)
    # Webbed trailing edge picked out so the scallop reads as webbing, not a blob.
    pygame.draw.lines(surf, _SUMI, False, web_base, 2)
    pygame.draw.circle(surf, _CYAN, (int(rear_tip[0]), int(rear_tip[1])), 2)
    pygame.draw.circle(surf, _GOLD_H, (int(front_tip[0]), int(front_tip[1])), 1)

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
