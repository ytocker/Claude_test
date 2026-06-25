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
_IRID_C  = (124, 240, 224)         # #7CF0E0 oil-slick cyan
_IRID_M  = (255, 138, 216)         # #FF8AD8 oil-slick magenta
_IRID_G  = (255, 224, 140)         # gold cap of the oil-slick shift
_INK     = (26, 30, 40)            # deep reflection shadow / vane backing

# Chrome re-plumage: a tight reflection ramp, NOT a flat grey. The shadow zones
# go nearly black-steel, the mids are cool blue-grey, and the hot zones (crown,
# chest, leading wing) push to near-white so the body already carries a strong
# dark→light value sweep before the overlay adds the hard hotspot streaks. The
# sheen is a bright sky-blue band so the body reflects "sky", reinforcing the
# mirror read. Beak chromed; lenses dropped — the front overlay paints the
# mirror-chrome aviators so the oil-slick glint lands on top of everything.
P_CHROME = _pal(
    tail=[(40, 46, 58), (70, 82, 100), (120, 142, 166), (180, 200, 220)],
    tail_line=(24, 28, 38),
    body_shadow=(44, 50, 62),
    body_main=(96, 112, 134),
    body_chest=(176, 198, 220),
    body_belly=(70, 82, 100),
    sheen=(150, 200, 245, 180),
    wing_main=(80, 94, 116),
    wing_dark=(38, 44, 56),
    wing_tip=(206, 224, 240),
    wing_secondary=None,
    wing_highlight=(244, 250, 255),
    head_shadow=(46, 52, 66),
    head_main=(104, 122, 146),
    head_cheek=(170, 192, 214),
    head_crown=(210, 228, 242),
    lens_frame=(150, 168, 190),
    lens_body=(30, 36, 48),
    lens_tint=None,
    lens_glint=None,
    beak_main=(150, 170, 192),
    beak_dark=(48, 56, 70),
    beak_gloss=(244, 250, 255),
    foot=(120, 138, 160),
)


def _chrome_base(angle_deg):
    # No aviators in the base — the mirror-chrome lenses are painted in the
    # front overlay so the oil-slick glint sits above the panel lines.
    return _build_parrot_with_palette(angle_deg, P_CHROME, draw_lenses=False)


# ── shared helpers ────────────────────────────────────────────────────────────

def _oil_mix(t):
    """Cyan→magenta→gold oil-slick shift — the holo signature ramp. t in [0,1]."""
    if t < 0.5:
        return lerp_color(_IRID_C, _IRID_M, t / 0.5)
    return lerp_color(_IRID_M, _IRID_G, (t - 0.5) / 0.5)


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
    vroot = (15, HY + 9)
    vanes = (
        (-20, 22, 4, 0.10),
        (-24, 14, 4, 0.30),
        (-26, 5,  5, 0.52),
        (-23, -3, 4, 0.74),
        (-17, -9, 3, 0.95),
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
        blit_glow(glow, int(gx), int(gy), 5, _oil_mix((i % 10) / 10.0), alpha=90)
    for dx, dy, hw, t in vanes:
        _, tip = vane_poly(dx, dy, hw)
        blit_glow(glow, int(tip[0]), int(tip[1]), 5, _oil_mix(t), alpha=85)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── pass 2: opaque bright detail (day + night) ────────────────────────────
    det = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)

    # Bladed chrome tail-vanes FIRST (lowest layer): a dark ink backing, a mid-
    # chrome fill, and a razor SPEC highlight down the leading edge so each vane
    # reads as a mirror-bright metal feather even at 40px.
    for dx, dy, hw, t in sorted(vanes, key=lambda v: -abs(v[1])):
        poly, tip = vane_poly(dx, dy, hw)
        _poly(det, _INK, [(x - 1, y + 1) for x, y in poly])
        _poly(det, _MID, poly)
        # razor highlight along the upper leading edge
        pygame.draw.line(det, _SPEC, (vroot[0] + 2, vroot[1] - hw + 1),
                         (tip[0], tip[1] - 1), 2)
        # one oil-slick glint at the very tip ties the vanes to the holo theme
        pygame.draw.circle(det, _oil_mix(t), (int(tip[0]), int(tip[1])), 1)

    # Holo halo RING — the secret tell. A thin oil-slick band: a dark ink backing
    # so it reads on bright sky, then the ring drawn as short coloured segments
    # cycling cyan→magenta→gold so the whole band shimmers like an oil slick,
    # with two white spec glints where the ring crosses the top edge.
    pygame.draw.lines(det, _INK, True, ring, 4)
    for i in range(len(ring) - 1):
        seg = _oil_mix(((i * 1.7) % 10) / 10.0)
        pygame.draw.line(det, seg, ring[i], ring[i + 1], 3)
    pygame.draw.circle(det, _SPEC, (int(ring[7][0]), int(ring[7][1])), 2)
    pygame.draw.circle(det, _SPEC, (int(ring[22][0]), int(ring[22][1])), 1)

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
    # Leading-wing razor hotspot.
    pygame.draw.line(surf, _SPEC, (30, 38), (44, 35), 2)
    pygame.draw.line(surf, _HOT, (29, 41), (43, 38), 1)

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
    for rx, ry in ((39, 45), (35, 47), (22, 47)):       # shoulder rivets
        pygame.draw.circle(surf, _STEEL, (rx, ry), 2)
        pygame.draw.circle(surf, _SPEC, (rx - 1, ry - 1), 1)

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
