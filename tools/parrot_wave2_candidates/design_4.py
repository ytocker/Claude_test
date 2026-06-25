"""design_4 · STAINED-GLASS MACAW — LEGENDARY parrot-wave2 exploration.

A cathedral window given wings: every feather is a leaded jewel pane lit as if
back-lit, crowned by a rose-window halo and trailing a fan of cathedral-tall
glass tail-panes. The legendary tell is the back-lit ROSE-WINDOW HALO plus the
silhouette-breaking GLASS TAIL — a clear tier above the single-zone epics. The
art-object language (hard black lead lines binding flat opaque jewel facets) is
the opposite of feathers, and the opposite of PRISM's clear refracting shards.

Draw order matters: the halo and the glass tail must paint BEHIND the body and
glow OUTSIDE the house outline, so this can't use store_skins._make_skin's
body-first _compose. Mirroring the aurora/viking back-layer pattern, this is a
custom getter — back layer (halo + tail: additive light-spill glow buffer then
an opaque leaded-glass detail buffer) → jewel-recoloured body → front overlay
(gothic-arch crest, leaded pane plumage, wing light-shaft, smoky aviators) →
house outline → per-(frame, 3°-bucket) rotation cache.

Two-buffer back layer is deliberate: additive glow sells "lit from behind" on a
dark NIGHT sky where additive shines, while the opaque leaded panes carry the
read on a bright DAY sky where additive washes out. A legendary must read on
both. Lead lines are kept crisp and FEW (bigger panes, not finer subdivision)
so they survive the 40px downscale instead of mudding into a grey smear.

Exploration only — NEVER registered in store_skins.BUILDERS.
"""
import math

import pygame

from game.parrot import _WING_ANGLES, _add_outline
from game.draw import blit_glow, lerp_color
from game.store_skins import (
    COMPOSITE_W, COMPOSITE_H, PARROT_DY, HX, HY, CROWN_Y,
)
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette (brief) ───────────────────────────────────────────────────────────
_RUBY    = (215, 38, 61)           # #D7263D
_SAPPH   = (31, 95, 196)           # #1F5FC4
_EMERALD = (31, 168, 115)          # #1FA873
_AMBER   = (242, 178, 62)          # #F2B23E
_LEAD    = (21, 19, 26)            # #15131A lead line / dark
_LEAD_HI = (54, 50, 64)            # a lifted lead so the came catches a glint
_GLINT   = (255, 250, 235)         # the back-light shaft hotspot

# Lighter pane cores (the centre of each facet reads brighter, as if a light
# source sits behind the glass — flat panes, but the middle glows).
_RUBY_LIT    = (255, 96, 116)
_SAPPH_LIT   = (96, 158, 248)
_EMERALD_LIT = (96, 232, 176)
_AMBER_LIT   = (255, 224, 150)

# Body re-plumage: a deep jewel mosaic. Every slot is a saturated jewel tone and
# the LEAD owns ALL the line work (tail_line / wing_dark / shadows), so the base
# bird already reads as panes bound by black came before the front overlay adds
# the crisp lead grid. Cores are lifted toward the *_LIT hues so the body glows
# from within rather than reading as flat paint; the crown is amber so the
# gothic crest springs from a warm window-top. Lenses are kept (Pip's aviators)
# but the front overlay re-tints them smoky cathedral grey.
P_GLASS = _pal(
    tail=[_RUBY, _AMBER, _EMERALD, _SAPPH],   # alternating jewel tail-panes
    tail_line=_LEAD,
    body_shadow=_LEAD,
    body_main=(150, 30, 52),                  # ruby field, lead-deep
    body_chest=_RUBY,
    body_belly=(120, 24, 44),
    sheen=(255, 220, 200, 70),
    wing_main=(26, 78, 162),                  # sapphire wing field
    wing_dark=_LEAD,
    wing_tip=_SAPPH_LIT,
    wing_secondary=None,
    wing_highlight=(150, 200, 255),
    head_shadow=_LEAD,
    head_main=(150, 30, 52),
    head_cheek=_RUBY_LIT,
    head_crown=(196, 138, 40),                # amber crown → window-top
    lens_frame=(70, 66, 80),
    lens_body=(20, 19, 26),
    lens_tint=(120, 124, 138, 150),           # smoky cathedral grey
    lens_glint=(228, 230, 238),
    beak_main=(214, 176, 96),                 # warm leaded came
    beak_dark=_LEAD,
    beak_gloss=(248, 226, 168),
    foot=(70, 66, 80),
)


def _glass_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, P_GLASS)


# ── shared helpers ────────────────────────────────────────────────────────────

def _flap_phase(angle_deg):
    """0 on the down-stroke (wing 50°) → 1 on the up-stroke (-40°). The glass
    tail-panes fan a touch wider on the up-beat so the baked window still feels
    alive across the 4 frames."""
    return 1.0 - (angle_deg + 40) / 90.0


def _jewel(i):
    """Cycle the four jewel hues so panes/wedges alternate around the window."""
    return (_RUBY, _SAPPH, _EMERALD, _AMBER)[i % 4]


def _jewel_lit(i):
    return (_RUBY_LIT, _SAPPH_LIT, _EMERALD_LIT, _AMBER_LIT)[i % 4]


# ── back layer: rose-window halo + cathedral glass tail-panes ─────────────────

def _glass_back(surf, angle_deg):
    """Every back-lit element lives here, BEHIND the outlined bird, so the house
    outline (grown from the bird's alpha mask) never boxes the back-light bloom
    into its own dark-rimmed island. Two passes, both un-outlined:

      1. an ADDITIVE light-spill buffer — the warm/jewel glow seeping out from
         behind the halo and from under the tail-panes, selling "lit from
         behind" on a dark night sky where additive shines.
      2. an OPAQUE leaded-glass buffer alpha-blitted ON TOP — the rose-window's
         concentric jewel wedges + lead spokes and the elongated tail-panes as
         solid colour bound by black came, so the window ALSO reads on a bright
         day sky where the additive spill washes out.

    Contents: the rose-window HALO behind the head and the cathedral TAIL-PANES
    fanning down-back well past the body."""
    phase = _flap_phase(angle_deg)

    hcx, hcy = HX - 2, HY - 2                      # rose-window centre, behind head
    R_OUT = 19                                     # outer rim of the rose window
    fan = 1.0 + phase * 0.12                       # tail spreads on the up-beat

    # Cathedral TAIL-PANES — five elongated pointed glass lancets springing from
    # the tail root and fanning DOWN-BACK into open sky, each lead-edged with a
    # lit jewel core. Built long (well past the body) so they break the egg
    # silhouette the way a legendary must. Each: (spread angle from straight-down
    # in degrees, length, jewel index).
    troot = (15, HY + 9)
    panes = (
        (-46, 30, 0),     # ruby, swept far back
        (-28, 35, 1),     # sapphire
        (-12, 38, 2),     # emerald, longest centre lancet
        (4,   34, 3),     # amber
        (20,  29, 0),     # ruby, swept down-forward
    )

    def pane_poly(ang_deg, length, width):
        a = math.radians(150 + ang_deg * fan)      # 150° base ≈ down-and-back
        ca, sa = math.cos(a), math.sin(a)
        tip = (troot[0] + ca * length, troot[1] + sa * length)
        # perpendicular for the lancet width, tapering to a point at the tip
        pa = a + math.pi / 2
        px, py = math.cos(pa) * width, math.sin(pa) * width
        base_in = (troot[0] - px, troot[1] - py)
        base_out = (troot[0] + px, troot[1] + py)
        mid = (troot[0] + ca * length * 0.5, troot[1] + sa * length * 0.5)
        mid_in = (mid[0] - px * 0.7, mid[1] - py * 0.7)
        mid_out = (mid[0] + px * 0.7, mid[1] + py * 0.7)
        return [base_in, mid_in, tip, mid_out, base_out], tip

    # ── pass 1: additive light-spill (night) ─────────────────────────────────
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    # Rose-window halo bloom — a ring of jewel glow stamps so the whole disc
    # back-lights, brightest where it clears the silhouette on the flanks.
    for i in range(10):
        a = math.radians(i * 36)
        gx = hcx + math.cos(a) * (R_OUT - 3)
        gy = hcy + math.sin(a) * (R_OUT - 3)
        blit_glow(glow, int(gx), int(gy), 7, _jewel_lit(i), alpha=120)
    blit_glow(glow, hcx, hcy, 11, _GLINT, alpha=70)      # warm centre lamp
    # Tail-pane spill — a jewel bloom beneath each lancet so the glass looks lit.
    for ang, length, ji in panes:
        poly, tip = pane_poly(ang, length, 4)
        blit_glow(glow, int(tip[0]), int(tip[1]), 6, _jewel_lit(ji), alpha=115)
        mid = poly[1]
        blit_glow(glow, int(mid[0]), int(mid[1]), 5, _jewel(ji), alpha=95)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── pass 2: opaque leaded glass (day + night) ────────────────────────────
    det = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)

    # Cathedral TAIL-PANES — drawn first (lowest layer of the bright detail) so
    # the body later overlaps their roots and they read as plumage, not a fan
    # pinned behind. Each lancet: a thick lead came border, a flat jewel field,
    # a brighter lit core stripe up the spine, and a glint at the tip.
    for ang, length, ji in panes:
        poly, tip = pane_poly(ang, length, 4)
        pygame.draw.polygon(det, _LEAD, poly)
        inner = [(poly[0][0], poly[0][1]), poly[1], tip, poly[3],
                 (poly[4][0], poly[4][1])]
        # shrink the field slightly toward the centre so the lead shows as a rim
        cx = sum(p[0] for p in inner) / len(inner)
        cy = sum(p[1] for p in inner) / len(inner)
        field = [(cx + (x - cx) * 0.72, cy + (y - cy) * 0.78) for x, y in inner]
        pygame.draw.polygon(det, _jewel(ji), field)
        pygame.draw.line(det, _jewel_lit(ji), (troot[0], troot[1]),
                         (int(tip[0]), int(tip[1])), 2)
        pygame.draw.circle(det, _GLINT, (int(tip[0]), int(tip[1])), 2)

    # Rose-window HALO — a concentric leaded disc behind the head: a dark came
    # ground, a ring of alternating jewel wedges split by lead spokes, an inner
    # ring of smaller jewel lights, and a lit centre boss. Sized larger than the
    # skull so the jewelled ring clears OUTSIDE the silhouette on the flanks —
    # the part that actually reads as a halo separating bird from sky.
    pygame.draw.circle(det, _LEAD, (hcx, hcy), R_OUT)
    seg = 10
    for i in range(seg):
        a0 = math.radians(i * (360 / seg) + 4)
        a1 = math.radians((i + 1) * (360 / seg) - 4)
        wedge = [(hcx, hcy)]
        for a in (a0, (a0 + a1) / 2, a1):
            wedge.append((hcx + math.cos(a) * (R_OUT - 2),
                          hcy + math.sin(a) * (R_OUT - 2)))
        pygame.draw.polygon(det, _jewel(i), wedge)
        # a lit chip near the rim so each wedge glows from behind
        ma = (a0 + a1) / 2
        pygame.draw.circle(det, _jewel_lit(i),
                           (int(hcx + math.cos(ma) * (R_OUT - 6)),
                            int(hcy + math.sin(ma) * (R_OUT - 6))), 2)
    # Inner lead ring + a quatrefoil of small jewel lights round the centre.
    pygame.draw.circle(det, _LEAD, (hcx, hcy), 8)
    for i in range(4):
        a = math.radians(i * 90 + 45)
        pygame.draw.circle(det, _jewel_lit(i + 1),
                           (int(hcx + math.cos(a) * 5), int(hcy + math.sin(a) * 5)), 2)
    pygame.draw.circle(det, _GLINT, (hcx, hcy), 3)        # centre lamp
    pygame.draw.circle(det, _AMBER, (hcx, hcy), 2)

    surf.blit(det, (0, 0))


# ── front overlay: gothic-arch crest, leaded pane plumage, wing shaft ─────────

def _front_pane(surf, pts, jewel, lit):
    """One leaded glass facet: a flat jewel field, a brighter lit centre dot,
    bound by a crisp ≥1px lead came border. The came IS the signature, so it's
    always drawn — kept thin so the panes stay big and read at 40px."""
    pygame.draw.polygon(surf, jewel, pts)
    pygame.draw.polygon(surf, _LEAD, pts, 1)
    cx = int(sum(p[0] for p in pts) / len(pts))
    cy = int(sum(p[1] for p in pts) / len(pts))
    pygame.draw.circle(surf, lit, (cx, cy), 1)


def _glass_front(surf, angle_deg):
    """Painted OVER the jewel body and INSIDE the masked layer, so only crisp
    opaque detail belongs here (the soft back-light lives in _glass_back to
    dodge the outline): the gothic-arch crest past the crown, a few BIG leaded
    panes redrawing the wing/chest as a window, the wing light-shaft glint, and
    the smoky-grey aviators re-asserted so Pip's identity survives the
    downscale."""
    # Gothic-arch CREST — three tall pointed glass lancets rising past the crown
    # like a window top, lead-edged, ruby/sapphire/emerald left→right, each a
    # pointed-arch silhouette (the legendary's crown-breaking shape). The centre
    # lancet is tallest. Drawn over a thin lead plinth so they share a base.
    base_y = CROWN_Y + 2
    pygame.draw.line(surf, _LEAD, (HX - 11, base_y), (HX + 11, base_y - 2), 3)
    lancets = (
        (-8, 13, _RUBY, _RUBY_LIT),
        (0, 19, _SAPPH, _SAPPH_LIT),
        (8, 13, _EMERALD, _EMERALD_LIT),
    )
    for dx, h, jw, lit in lancets:
        bx = HX + dx
        ty = base_y - h
        # pointed-arch lancet: two straight jambs rising to a point
        pts = [(bx - 4, base_y), (bx - 4, ty + 5), (bx, ty),
               (bx + 4, ty + 5), (bx + 4, base_y)]
        pygame.draw.polygon(surf, jw, pts)
        pygame.draw.polygon(surf, _LEAD, pts, 1)
        pygame.draw.line(surf, lit, (bx, ty + 3), (bx, base_y - 2), 1)
        pygame.draw.circle(surf, _GLINT, (bx, ty + 1), 1)   # leaded apex bead

    # Leaded WING panes — a few BIG facets over the sapphire wing, each a flat
    # jewel bound by came, so the wing reads as a window pane fan rather than
    # feathers. Kept to four large panes (not fine subdivision) so the lead grid
    # survives 40px. Wing field spans roughly x∈[24,48], y∈[40,52].
    _front_pane(surf, [(25, 45), (33, 41), (35, 47), (27, 50)], _SAPPH, _SAPPH_LIT)
    _front_pane(surf, [(35, 41), (44, 41), (45, 47), (36, 47)], _EMERALD, _EMERALD_LIT)
    _front_pane(surf, [(27, 50), (35, 47), (40, 51), (31, 54)], _AMBER, _AMBER_LIT)
    _front_pane(surf, [(36, 47), (45, 47), (47, 52), (40, 51)], _RUBY, _RUBY_LIT)

    # A bright diagonal LIGHT-SHAFT glint across the wing — the back-light
    # catching the glass, the moment that sells "lit from behind" up close.
    shaft = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.line(shaft, (*_GLINT, 150), (27, 52), (44, 41), 3)
    pygame.draw.line(shaft, (*_GLINT, 90), (31, 54), (48, 43), 2)
    surf.blit(shaft, (0, 0))

    # Leaded CHEST panes — two big ruby/amber facets over the breast so the
    # body front also reads as a window, not a painted blob.
    _front_pane(surf, [(40, 47), (50, 46), (51, 54), (42, 56)], _RUBY, _RUBY_LIT)
    _front_pane(surf, [(42, 56), (51, 54), (49, 61), (41, 61)], _AMBER, _AMBER_LIT)

    # Re-assert the smoky-grey aviators + a sharp came line on the beak so Pip's
    # macaw identity survives the downscale and the lenses don't drown in jewels.
    pygame.draw.circle(surf, (228, 230, 238), (HX + 6, HY - 3), 2)   # near-lens glint
    pygame.draw.line(surf, _LEAD_HI, (HX + 8, HY + 1), (HX + 13, HY + 4), 1)
    # A single horizontal came strip across the brow ties the crest plinth into
    # the head so the window-top springs from the skull, not floats above it.
    pygame.draw.line(surf, _LEAD, (HX - 11, base_y + 2), (HX + 12, base_y), 2)
    pygame.draw.line(surf, _AMBER, (HX - 9, base_y + 1), (HX + 9, base_y - 1), 1)


# ── custom compose + getter (halo/tail need a back layer) ─────────────────────

def _glass_getter():
    """back layer (halo + glass tail) → jewel body → front (crest, panes,
    shaft, aviators) → house outline, then the per-(frame, 3°-bucket) rotation
    cache shared by every store skin."""
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        # The house outline is grown from the alpha mask, so the faint additive
        # back-light must NOT be part of the masked layer — else the dark rim
        # would wrap the glow and kill the "lit from behind". So outline the
        # OPAQUE bird (jewel body + front overlay) alone, then lay the soft
        # back layer UNDER it. The outline pads by 2px; the back surface is
        # padded to match before the under-blit so the bird stays centred for
        # the rotation maths.
        bird = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        bird.blit(_glass_base(wing_angle), (0, PARROT_DY))
        _glass_front(bird, wing_angle)
        bird = _add_outline(bird)

        full = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
        pad = (bird.get_width() - COMPOSITE_W) // 2
        back = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _glass_back(back, wing_angle)
        full.blit(back, (pad, pad))
        full.blit(bird, (0, 0))
        return full

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


build = _glass_getter()
