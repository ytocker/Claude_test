"""design_5 · CHROME MACAW — SECRET parrot-wave2 exploration.

The tab's first secret: a mirror-polished, injection-moulded Pip. There is no
local hue anywhere on the body — every "colour" is a hard specular reflection of
the sky, ramped dark-steel → sky-sheen → white hotspot so the bird reads as
liquid chrome rather than a grey bird. The signature stack: a thin oil-slick
HOLO HALO ring hovering behind the head (the secret tell), a swept CHROME
FIN-CREST of polished blades past the crown, a fan of bladed CHROME TAIL-VANES
splaying down-back, panel/seam lines + rivet dots moulding the shell, and the
aviators upgraded to mirror-chrome with an oil-slick glint — the "still Pip"
anchor that sells the joke.

The make-or-break at 40px is the VALUE JUMP: polished metal is sold by a HARD
≥2px white hotspot streak butting against deep steel shadow, not a soft
gradient. The body palette ramp does the bulk; the paint_fn front overlay lays
the crisp spec streaks, panel lines, fin-crest and mirror lenses on top.

Draw order needs a back layer: the holo halo ring + tail-vanes paint BEHIND the
body. Mirroring the aurora/viking pattern, this is a custom getter — back layer
(halo + vanes) → chrome body → front overlay (spec streaks, panels, crest,
lenses) → house outline → per-(frame, 3°-bucket) rotation cache.

Exploration only — NEVER registered in store_skins.BUILDERS.
"""
import math

import pygame

from game.parrot import _WING_ANGLES, _add_outline
from game.draw import blit_glow, lerp_color
from game.store_skins import (
    COMPOSITE_W, COMPOSITE_H, PARROT_DY, HX, HY, CROWN_Y, _poly,
)
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette (brief) ───────────────────────────────────────────────────────────
_STEEL   = (58, 66, 80)            # #3A4250 steel shadow
_MID     = (143, 166, 190)         # #8FA6BE mid chrome
_HOT     = (232, 242, 250)         # #E8F2FA chrome hotspot
_SPEC    = (255, 255, 255)         # #FFFFFF spec highlight
# Oil-slick is now a TWO-hue shift only (magenta↔cyan). R1 cycled a third gold
# hue; at 40px three hues read as chromatic-aberration noise instead of a ring.
# Two hues hold the ring's SHAPE when small while still shimmering at hero size.
_IRID_C  = (124, 240, 224)         # #7CF0E0 oil-slick cyan
_IRID_M  = (255, 138, 216)         # #FF8AD8 oil-slick magenta
_INK     = (26, 30, 40)            # deep reflection shadow / vane backing
_RIM     = (214, 230, 245)         # cool-white bottom rim-light (night read)

# Chrome re-plumage: a tight reflection ramp, NOT a flat grey. The mids are cool
# blue-grey and the hot zones (crown, chest, leading wing) push to near-white so
# the body carries a strong dark→light sweep before the overlay adds the hard
# hotspot streaks. The sheen is a bright sky-blue band so the body reflects
# "sky", reinforcing the mirror read. Beak chromed; lenses dropped — the front
# overlay paints the mirror-chrome aviators so the oil-slick glint lands on top.
#
# Night value FLOOR (R2 must-fix): R1's darkest passages were tuned for bright
# sky and sat only ~1 value-step off the navy night sky (~RGB 5-30), so the
# lower body dissolved at night. The whole shadow floor — body_shadow/belly,
# wing_dark, head_shadow, tail base, foot — is lifted ~15-20% to a cool slate
# that always clears the night sky's value. The value JUMP that sells metal is
# preserved because the white hotspots stay untouched at near-white; only the
# floor rose, so the dark→light span is undiminished.
P_CHROME = _pal(
    tail=[(72, 82, 98), (96, 110, 130), (136, 158, 182), (188, 208, 226)],
    tail_line=(50, 56, 70),
    body_shadow=(76, 86, 102),
    body_main=(106, 122, 144),
    body_chest=(178, 200, 222),
    body_belly=(96, 110, 130),
    sheen=(150, 200, 245, 180),
    wing_main=(98, 112, 134),
    wing_dark=(70, 80, 96),
    wing_tip=(206, 224, 240),
    wing_secondary=None,
    wing_highlight=(244, 250, 255),
    head_shadow=(74, 84, 100),
    head_main=(114, 132, 156),
    head_cheek=(172, 194, 216),
    head_crown=(212, 230, 244),
    lens_frame=(150, 168, 190),
    lens_body=(30, 36, 48),
    lens_tint=None,
    lens_glint=None,
    beak_main=(154, 174, 196),
    beak_dark=(72, 82, 98),
    beak_gloss=(244, 250, 255),
    foot=(130, 148, 170),
)


def _chrome_base(angle_deg):
    # No aviators in the base — the mirror-chrome lenses are painted in the
    # front overlay so the oil-slick glint sits above the panel lines.
    return _build_parrot_with_palette(angle_deg, P_CHROME, draw_lenses=False)


# ── shared helpers ────────────────────────────────────────────────────────────

def _oil_mix(t):
    """Magenta↔cyan oil-slick shift — the holo signature ramp, TWO hues only so
    it reads as a coloured ring (not chromatic-aberration noise) at 40px. t in
    [0,1] ping-pongs magenta→cyan→magenta so adjacent ring segments alternate
    cleanly rather than running a full spectrum."""
    s = 1.0 - abs(2.0 * t - 1.0)            # triangle wave: 0 at ends, 1 mid
    return lerp_color(_IRID_M, _IRID_C, s)


def _flap_phase(angle_deg):
    """0 on the down-stroke (wing 50°) → 1 on the up-stroke (-40°). The crest
    and tail-vanes swing a touch with the beat so the baked metal still feels
    alive across the 4 frames."""
    return 1.0 - (angle_deg + 40) / 90.0


def _arc(cx, cy, r, a0, a1, steps=20):
    return [(cx + math.cos(a0 + (a1 - a0) * i / steps) * r,
             cy + math.sin(a0 + (a1 - a0) * i / steps) * r)
            for i in range(steps + 1)]


# ── back layer: oil-slick holo ring + bladed chrome tail-vanes ────────────────

def _chrome_back(surf, angle_deg):
    """Everything that paints BEHIND the body lives here, outside the masked
    layer, so the house outline never boxes the soft holo bloom into a dark-
    rimmed island. Two passes: an additive oil-slick under-glow for night, then
    an opaque bright-detail pass (ring band + vane spines) so the secret also
    reads on a bright day sky where additive washes out.

    Contents: the HOLO HALO RING arcing behind the head, and the fan of bladed
    CHROME TAIL-VANES splaying down-back past the tail."""
    phase = _flap_phase(angle_deg)
    sway = (phase - 0.5) * 3

    # Halo ring geometry — a thin oil-slick band hovering BEHIND + around the
    # head, larger than the skull (r=20) so its arc clears the silhouette on the
    # flanks and reads as a hovering ring, tilted as an ellipse so it reads as a
    # ring seen at an angle, not a flat disc.
    hcx, hcy = HX - 2, HY - 4
    ring_rx, ring_ry = 21, 13
    ring = [(hcx + math.cos(a) * ring_rx, hcy + math.sin(a) * ring_ry)
            for a in [math.radians(d) for d in range(0, 361, 12)]]

    # Tail-vane fan — angular blades springing from the tail root, splaying
    # down-back into open sky. Each: (tip dx, tip dy, half-width, oil-slick t).
    # The rearmost two (longest reach, drawn against open sky) are flagged `hard`
    # so they get a deep-steel GAP + a razor white spec edge — the same value-
    # jump trick the wing uses — so the bladed FAN separates from the body mass
    # at 40px instead of subtly blending into it (premium tier ≠ subtle).
    vroot = (15, HY + 9)
    #         dx,  dy, hw,  t,    hard
    vanes = (
        (-22, 23, 4, 0.10, True),
        (-27, 14, 5, 0.32, True),
        (-28, 5,  5, 0.55, False),
        (-24, -3, 4, 0.78, False),
        (-17, -9, 3, 1.00, False),
    )

    def vane_poly(dx, dy, hw):
        tip = (vroot[0] + dx, vroot[1] + dy + sway)
        # A slim metal blade: root pivot → razor tip → back edge.
        return [
            (vroot[0] + 2, vroot[1] - hw), (tip[0], tip[1] - 1),
            (tip[0] - 1, tip[1] + 1), (vroot[0], vroot[1] + hw),
        ], tip

    # ── pass 1: additive oil-slick under-glow (night) ─────────────────────────
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for i, (gx, gy) in enumerate(ring):
        blit_glow(glow, int(gx), int(gy), 5, _oil_mix((i % 12) / 12.0), alpha=90)
    for dx, dy, hw, t, hard in vanes:
        _, tip = vane_poly(dx, dy, hw)
        blit_glow(glow, int(tip[0]), int(tip[1]), 5, _oil_mix(t), alpha=85)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── pass 2: opaque bright detail (day + night) ────────────────────────────
    det = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)

    # Bladed chrome tail-vanes FIRST (lowest layer). Each vane: a dark ink
    # backing, a mid-chrome fill, a razor SPEC highlight down the leading edge.
    # The `hard` rearmost vanes additionally get a deep-steel shadow gap on the
    # trailing side so a value JUMP (steel→white spec) splits them clear of the
    # body silhouette at 40px.
    for dx, dy, hw, t, hard in sorted(vanes, key=lambda v: -abs(v[1])):
        poly, tip = vane_poly(dx, dy, hw)
        _poly(det, _INK, [(x - 1, y + 1) for x, y in poly])
        if hard:
            _poly(det, _STEEL, poly)                 # deep-steel gap = the jump
            _poly(det, _MID, [poly[0], poly[1], tip])
        else:
            _poly(det, _MID, poly)
        # razor white highlight along the upper leading edge — 2px so it survives
        pygame.draw.line(det, _SPEC, (vroot[0] + 2, vroot[1] - hw + 1),
                         (tip[0], tip[1] - 1), 2)
        # one oil-slick glint at the very tip ties the vanes to the holo theme
        pygame.draw.circle(det, _oil_mix(t), (int(tip[0]), int(tip[1])), 1)

    # Holo halo RING — the secret tell, RE-SPEC'd for downscale. A SOLID 2px
    # magenta↔cyan arc over a dark ink backing: it must read as a RING, not
    # rainbow pixels, when small. Two hues only (no gold), and each segment runs
    # a 2px clean line so the band keeps its circular SHAPE at 40px. Two white
    # spec glints where the ring crests sell it as a polished holo band.
    pygame.draw.lines(det, _INK, True, ring, 4)
    for i in range(len(ring) - 1):
        seg = _oil_mix((i % 12) / 12.0)
        pygame.draw.line(det, seg, ring[i], ring[i + 1], 2)
    pygame.draw.circle(det, _SPEC, (int(ring[8][0]), int(ring[8][1])), 2)
    pygame.draw.circle(det, _SPEC, (int(ring[24][0]), int(ring[24][1])), 1)

    surf.blit(det, (0, 0))


# ── front overlay: spec streaks, panel lines, rivets, fin-crest, lenses ───────

def _chrome_front(surf, angle_deg):
    """Crisp opaque chrome detail painted OVER the ramped body and INSIDE the
    masked layer: the swept fin-crest past the crown, hard white spec-highlight
    streaks, panel/seam lines + rivet dots moulding the shell, and the upgraded
    mirror-chrome aviators with their oil-slick glint. Everything here is hard
    pixels that survive the 40px downscale — the soft holo glow lives in the
    back layer to dodge the outline."""
    phase = _flap_phase(angle_deg)
    sway = int(round((phase - 0.5) * 3))

    # ── chrome FIN-CREST: 3 swept polished blades rising past the crown. Each is
    # a slim metal fin — deep reflection shadow on the trailing side, a hard
    # white spec streak up the leading edge. Swept back (tips lean toward the
    # tail) so it reads as aerodynamic chrome, breaking the egg outline up top.
    crest = (
        (HX - 2, -1, 22, 0.0),    # (root x, root dx-lean sign baked, height, lean)
    )
    blades = (
        (HX + 4, CROWN_Y + 1, HX - 9 + sway, CROWN_Y - 21),   # tall centre-back
        (HX + 7, CROWN_Y + 2, HX - 3 + sway, CROWN_Y - 16),   # mid
        (HX + 9, CROWN_Y + 4, HX + 3 + sway, CROWN_Y - 10),   # short front
    )
    for rx, ry, tx, ty in blades:
        # blade body: a slim wedge from a 5px root to a sharp tip
        body = [(rx - 3, ry), (rx + 3, ry), (tx + 1, ty + 1), (tx, ty)]
        _poly(surf, _INK, [(x - 1, y) for x, y in body])
        _poly(surf, _STEEL, body)                       # reflection shadow side
        _poly(surf, _MID, [(rx - 2, ry), (rx + 1, ry), (tx, ty)])
        # hard white spec streak up the leading edge — the metal read
        pygame.draw.line(surf, _SPEC, (rx - 2, ry - 1), (tx - 1, ty + 1), 2)
        pygame.draw.circle(surf, _SPEC, (int(tx), int(ty)), 1)

    # ── liquid-chrome BODY spec streaks: hard ≥2px white hotspot bands sitting on
    # the crown, the chest sheen, and the leading wing, each butting deep steel
    # shadow just below so the value JUMPS (the polished-metal tell). These are
    # the make-or-break — kept hard, never feathered.
    # Crown hotspot streak.
    pygame.draw.line(surf, _SPEC, (HX - 6, HY - 9), (HX + 6, HY - 11), 2)
    pygame.draw.line(surf, _STEEL, (HX - 6, HY - 6), (HX + 7, HY - 8), 2)
    # Chest hotspot streak (body chest centre ≈ (30,49) in composite space).
    pygame.draw.line(surf, _SPEC, (24, 46), (38, 43), 3)
    pygame.draw.line(surf, _STEEL, (24, 51), (40, 49), 2)

    # TRAVELLING wing hotspot (R2 juice): the primary white spec streak slides
    # across the leading wing with the flap — `phase` 0→1 walks it ~10px from the
    # shoulder out toward the wing tip, ~2-3px per frame, so in motion the
    # reflection visibly SWEEPS across the metal. A moving hotspot is what reads
    # as liquid chrome rather than a grey bird with a fixed white line.
    hx0 = 28 + int(round(phase * 10))
    pygame.draw.line(surf, _SPEC, (hx0, 38), (hx0 + 12, 35), 2)
    pygame.draw.line(surf, _HOT, (hx0 - 1, 41), (hx0 + 11, 38), 1)
    pygame.draw.line(surf, _STEEL, (hx0 - 1, 43), (hx0 + 11, 40), 1)   # gap below

    # ── moulded SHELL: panel / seam lines suggesting injection-moulded sections,
    # plus bolt/rivet dots at the shoulder. Seams are deep steel (recessed), each
    # given a 1px hot edge so they read as a bevelled panel split, not a scratch.
    seams = (
        [(40, 44), (33, 48), (24, 50)],          # shoulder → belly seam
        [(20, 44), (18, 50), (22, 56)],          # back panel split
        [(34, 56), (28, 58), (22, 57)],          # lower belly seam
    )
    for s in seams:
        pygame.draw.lines(surf, _INK, False, s, 2)
        pygame.draw.lines(surf, (188, 206, 226), False, s, 1)
    # Shoulder rivets — and on the UP-flap (phase high) the lead rivet POPS a
    # bright spec flare, a second beat of moving light catching the metal.
    for i, (rx, ry) in enumerate(((39, 45), (35, 47), (22, 47))):
        pygame.draw.circle(surf, _STEEL, (rx, ry), 2)
        pygame.draw.circle(surf, _SPEC, (rx - 1, ry - 1), 1)
    if phase > 0.66:                                       # up-flap rivet flare
        pygame.draw.circle(surf, _SPEC, (38, 44), 2)
        pygame.draw.circle(surf, _IRID_C, (38, 44), 1)

    # ── bottom RIM-LIGHT (R2 night must-fix): a thin cool-white stroke tracing
    # the UNDERSIDE silhouette (belly + lower wing + tail base) that faces open
    # sky, so the lower mass keeps a crisp lit edge against the dark night sky
    # rather than dissolving into it. Held one step above the lifted shadow floor
    # so it's a rim, not a glow, and the bright-day read is untouched.
    pygame.draw.lines(surf, _RIM, False,
                      [(16, 53), (21, 58), (29, 61), (38, 61), (45, 57)], 2)

    # ── mirror-chrome AVIATORS (the "still Pip" anchor). Drawn last so the oil-
    # slick glint sits above everything. Built like the base _draw_lenses but
    # the lens body is a chrome reflection ramp (dark steel base → sky band →
    # white hotspot) topped by a single oil-slick cyan→magenta glint streak.
    cx, cy = 50, HY - 1
    L = (cx - 4, cy)
    R = (cx + 6, cy - 1)
    r = 6
    for c in (L, R):
        pygame.draw.circle(surf, _MID, c, r + 1)             # chrome frame
        pygame.draw.circle(surf, _STEEL, c, r)               # dark base
        # sky-blue reflection band across the upper lens
        pygame.draw.arc(surf, (110, 170, 220), (c[0] - r, c[1] - r, 2 * r, 2 * r),
                        math.radians(20), math.radians(160), 3)
        # hard white hotspot — the polished mirror tell on the lens
        pygame.draw.circle(surf, _SPEC, (c[0] - 2, c[1] - 2), 2)
        # oil-slick glint streak — the secret tint on the aviators
        pygame.draw.line(surf, _IRID_C, (c[0] - 3, c[1] + 2), (c[0] + 1, c[1] + 3), 1)
        pygame.draw.line(surf, _IRID_M, (c[0] + 1, c[1] + 3), (c[0] + 3, c[1] + 2), 1)
    # Bridge + brow bar in chrome.
    pygame.draw.line(surf, _MID, (L[0] + r, L[1]), (R[0] - r, R[1]), 2)
    pygame.draw.line(surf, _HOT,
                     (L[0] - r + 1, L[1] - r + 2), (R[0] + r - 1, R[1] - r + 2), 1)

    # Chromed beak top-edge glint so the macaw face survives the downscale.
    pygame.draw.line(surf, _SPEC, (55, 41), (59, 43), 1)


# ── custom compose + getter (holo ring + vanes need a back layer) ─────────────

def _chrome_getter():
    """back layer (holo ring + tail-vanes) → chrome body → front overlay (spec
    streaks, panels, crest, mirror lenses) → house outline, then the per-(frame,
    3°-bucket) rotation cache shared by every store skin."""
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        # The house outline grows from the alpha mask, so the soft additive holo
        # glow must NOT be in the masked layer or the dark rim would box it. So
        # outline the OPAQUE bird (body + front overlay) alone, then lay the soft
        # back layer UNDER it, padded to match the outline's 2px grow.
        bird = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        bird.blit(_chrome_base(wing_angle), (0, PARROT_DY))
        _chrome_front(bird, wing_angle)
        bird = _add_outline(bird)

        out = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
        pad = (bird.get_width() - COMPOSITE_W) // 2
        back = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _chrome_back(back, wing_angle)
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


build = _chrome_getter()
