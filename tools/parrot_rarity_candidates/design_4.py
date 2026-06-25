"""design_4 · AURORA MACAW — LEGENDARY parrot-rarity exploration.

Night sky given wings: a midnight-galaxy Pip haloed by a bright additive
teal/blue ring, crowned with a fanned green↔magenta nebula plume, trailing
wide flowing aurora ribbons where the tail-fan was. The legendary tell is the
luminous halo PLUS the silhouette-breaking ribbon tail — a clear tier above the
single-zone epics. Round 2 thickens every tell to survive the 40px truth read:
the plume fans (no antennae bulbs), the halo is a ≥3px rim-separating ring, the
ribbons are gradient bands, and the body is rim-lit + value-lifted off the void.

Draw order matters: the halo and the ribbon tail must paint BEHIND the body,
so this can't use store_skins._make_skin's body-first `_compose`. Mirroring
the viking-axe pattern, this is a custom getter — back-aura (halo + ribbons)
→ recoloured galaxy body → front overlay (nebula crest, star flecks, rim
light) → house outline → per-(frame, 3°-bucket) rotation cache.

Exploration only — NEVER registered in store_skins.BUILDERS. The aurora is
BAKED into each of the 4 frames (no runtime particle hook); the ribbons sweep
with the wing beat so the flap still reads alive.
"""
import pygame

from game.parrot import _WING_ANGLES, _add_outline
from game.draw import blit_glow, lerp_color
from game.store_skins import (
    COMPOSITE_W, COMPOSITE_H, PARROT_DY, HX, HY, CROWN_Y,
)
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette (brief) ───────────────────────────────────────────────────────────
_INDIGO   = (28, 27, 58)          # #1C1B3A midnight indigo
_GREEN    = (63, 224, 166)        # #3FE0A6 aurora green
_MAGENTA  = (196, 92, 232)        # #C45CE8 aurora magenta
_STARBLU  = (111, 168, 255)       # #6FA8FF star blue
_GLINT    = (255, 255, 255)       # #FFFFFF star glint

# Body re-plumage: a deep midnight-indigo galaxy. The R1 body read as a flat
# void against night sky, so the core values are lifted ~15% (a brighter, more
# saturated indigo with a clear blue-violet sheen) and the crown/back are cooled
# toward aurora teal, the belly toward magenta — unmistakably cosmic, not dark.
# Lenses keep Pip's aviators but tint to aurora teal so the signature shades
# read on the night palette; the beak is brightened so the macaw face survives.
_AURORA_PAL = _pal(
    tail=[(30, 28, 60), (40, 38, 80), (54, 56, 110), (74, 90, 150)],
    tail_line=(20, 19, 42),
    body_shadow=(26, 24, 54),
    body_main=(40, 38, 82),
    body_chest=(58, 58, 116),
    body_belly=(54, 46, 96),
    sheen=(150, 180, 255, 95),
    wing_main=(44, 44, 92),
    wing_dark=(22, 21, 46),
    wing_tip=(92, 124, 196),
    wing_secondary=None,
    wing_highlight=(128, 184, 250),
    head_shadow=(26, 24, 54),
    head_main=(42, 40, 86),
    head_cheek=(62, 64, 122),
    head_crown=(54, 74, 130),
    lens_frame=(96, 110, 168),
    lens_body=(12, 16, 36),
    lens_tint=(70, 210, 180, 150),
    lens_glint=(235, 255, 250),
    beak_main=(150, 160, 210),
    beak_dark=(52, 56, 100),
    beak_gloss=(225, 238, 255),
    foot=(76, 80, 130),
)


def _aurora_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _AURORA_PAL)


# ── shared helpers ────────────────────────────────────────────────────────────

def _aurora_mix(t):
    """Green→star-blue→magenta light band, the aurora's signature ramp."""
    if t < 0.5:
        return lerp_color(_GREEN, _STARBLU, t / 0.5)
    return lerp_color(_STARBLU, _MAGENTA, (t - 0.5) / 0.5)


def _flap_phase(angle_deg):
    """0 on the down-stroke (wing 50°) → 1 on the up-stroke (-40°). The ribbons
    stream long/loose on the up-beat and bunch tight on the down-beat so the
    baked aurora still feels alive across the 4 frames."""
    return 1.0 - (angle_deg + 40) / 90.0


# ── back layer: halo ring + aurora ribbon tail ───────────────────────────────

def _smooth_curve(p0, p1, p2, steps=10):
    """Quadratic-Bezier sample list so wisps/ribbons render as smooth curves
    rather than the 3-point polylines that read as straight rods at 40px."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def _aurora_back(surf, angle_deg):
    """Every glowing element lives here, BEHIND the outlined bird, so the house
    outline (grown from the bird's alpha mask) never boxes a bloom into its own
    dark-rimmed island. Two passes, both un-outlined:

      1. an ADDITIVE under-glow buffer — gives the halo/crest/ribbons a soft
         lit bloom on dark night skies, where additive shines.
      2. an OPAQUE bright-detail buffer alpha-blitted ON TOP — the ring annulus,
         crest cores and ribbon spines as solid bright pixels with a thin dark
         indigo backing, so they ALSO survive a bright-blue day/dusk sky where
         additive washes out. A legendary has to read on both.

    Contents: the legendary HALO ring framing the head, the NEBULA PLUME crest
    past the crown, and the AURORA RIBBON tail replacing the feather fan."""
    phase = _flap_phase(angle_deg)
    cbx, cby = HX - 1, CROWN_Y + 2                  # plume root, set into the crown
    hcx, hcy = HX - 1, HY - 2                       # halo centre, behind head
    sway = (phase - 0.5) * 3

    # Nebula PLUME — an asymmetric fan of 3 wisps of differing height that curve
    # OUTWARD and taper to nothing (no terminal bulbs). Each entry is the tip
    # offset + an outward control bow + colour-ramp position. The two tall wisps
    # lean apart; the short one fills the gap so the group reads as ONE crest.
    plume = (
        (-9, -22, -7, 0.12),   # left, tall, bows further left
        (-1, -28, -3, 0.50),   # centre, tallest, leans+bows so it never reads as a rod
        (7, -20, 6, 0.92),     # right, medium, bows right
    )

    def wisp_path(dx, dy, bow):
        tip = (cbx + dx + sway, cby + dy)
        ctrl = (cbx + dx * 0.5 + bow + sway * 0.5, cby + dy * 0.55)
        root = (cbx + dx * 0.18, cby + 1)
        return _smooth_curve(root, ctrl, tip)

    # Aurora RIBBON tail — three overlapping S-curve curtains sweeping down-back
    # into open sky. Built wide (a tapering band, not a sliver) with a clear
    # green→magenta gradient across the three; the S comes from the two control
    # bows pulling the spine opposite ways.
    def ribbon_path(k):
        reach = 22 + int(phase * 7)
        droop = (1.0 - phase) * 4                    # tail dips on the down-beat
        bx, by = 14, HY + 7 + k * 4
        c1 = (bx - reach * 0.42, by + 1 + k * 2 - 3)        # bow up first
        c2 = (bx - reach * 0.82, by + 9 + k * 5 + droop)    # then down → S
        tip = (bx - reach, by + 16 + k * 7 + droop)
        return _smooth_curve((bx, by), c1, c2, steps=6) + \
            _smooth_curve(c2, ((c2[0] + tip[0]) / 2, tip[1] - 1), tip, steps=5)

    # ── pass 1: additive under-glow (night) ──────────────────────────────────
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    # Halo glow halo — bright teal/blue ring bloom rim-separating the head.
    blit_glow(glow, hcx, hcy, 22, _STARBLU, alpha=120)
    blit_glow(glow, hcx, hcy, 16, _GREEN, alpha=70)
    for dx, dy, bow, t in plume:                     # plume bloom, hot at the base
        path = wisp_path(dx, dy, bow)
        blit_glow(glow, int(path[1][0]), int(path[1][1]), 5, _aurora_mix(t), alpha=140)
        blit_glow(glow, int(path[len(path) // 2][0]), int(path[len(path) // 2][1]),
                  3, _aurora_mix(t), alpha=90)
    for k in range(3):
        path = ribbon_path(k)
        blit_glow(glow, int(path[len(path) // 2][0]), int(path[len(path) // 2][1]),
                  5, _aurora_mix(k / 2.0), alpha=110)
        blit_glow(glow, int(path[-1][0]), int(path[-1][1]), 4, _aurora_mix(k / 2.0), alpha=100)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── pass 2: opaque bright detail (day + night) ───────────────────────────
    det = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _INK = (18, 16, 36)                             # thin dark backing for bright sky

    # Halo ring — the legendary tell. Thick (≥3px) additive-bright teal→blue
    # annulus over a dark backing ring, with a magenta accent arc and a white
    # glint so it reads as a luminous RING on any sky, set behind the head.
    pygame.draw.circle(det, _INK, (hcx, hcy), 18, 4)
    pygame.draw.circle(det, _STARBLU, (hcx, hcy), 17, 3)
    pygame.draw.circle(det, _GREEN, (hcx, hcy), 18, 2)
    pygame.draw.circle(det, _MAGENTA, (hcx, hcy), 15, 1)
    pygame.draw.circle(det, _GLINT, (hcx, hcy), 18, 1)

    # Nebula PLUME — smooth tapering wisps: a 4px dark backing, a 3px coloured
    # core that thins toward a 1px tip (no bulb), brightest where it meets the
    # crown. Drawn longest-first so the tall centre wisp sits behind the leans.
    for dx, dy, bow, t in sorted(plume, key=lambda p: p[1]):
        path = wisp_path(dx, dy, bow)
        col = _aurora_mix(t)
        base = _aurora_mix(max(0.0, t - 0.25))      # greener at the hot base
        pygame.draw.lines(det, _INK, False, path, 4)
        pygame.draw.lines(det, base, False, path[:len(path) // 2], 3)
        pygame.draw.lines(det, col, False, path[len(path) // 2 - 1:], 2)
        pygame.draw.circle(det, col, (int(path[0][0]), int(path[0][1])), 2)

    # Aurora RIBBON tail — wide green→magenta curtains: a soft translucent band
    # filling between the spine and an offset edge, a 4px ink backing and a 3px
    # bright spine, ending in a glint. The S-curve + width make it read as
    # flowing aurora, the lower silhouette break that sells the legendary.
    for k in range(3):
        path = ribbon_path(k)
        col = _aurora_mix(k / 2.0)
        edge = [(x, y + 4 + k) for x, y in path]    # widen into a band
        pygame.draw.polygon(det, (*col, 120), path + edge[::-1])
        pygame.draw.lines(det, _INK, False, path, 5)
        pygame.draw.lines(det, col, False, path, 3)
        pygame.draw.circle(det, _GLINT, (int(path[-1][0]), int(path[-1][1])), 2)

    surf.blit(det, (0, 0))


# ── front overlay: nebula crest, star flecks, rim light ──────────────────────

def _aurora_front(surf, angle_deg):
    """Painted OVER the body and INSIDE the masked layer, so only crisp opaque
    detail belongs here (soft glow lives in _aurora_back to dodge the outline):
    a ≥2px aurora rim-light wrapping the full back+belly edge, the crown-band
    blended into the crest's hot base, a re-asserted face, and star flecks
    crowded onto the LIT edge. These survive the downscale as hard pixels."""
    # Aurora rim-light wrapping the WHOLE silhouette — a ≥2px teal/blue band over
    # the back+crown and a green band under the belly, so the lifted indigo body
    # is framed by light rather than reading as a flat void on either sky. Body
    # ellipse spans roughly x∈[13,53], y∈[38,66] in composite space.
    pygame.draw.lines(surf, _STARBLU, False,
                      [(HX - 12, CROWN_Y + 3), (HX - 5, CROWN_Y - 1),
                       (HX + 4, CROWN_Y), (HX + 12, HY - 3)], 2)
    pygame.draw.lines(surf, _STARBLU, False,
                      [(16, 46), (15, 52), (18, 40)], 2)            # back-of-body edge
    pygame.draw.lines(surf, _GREEN, False,
                      [(16, 56), (24, 62), (34, 64), (44, 61)], 2)  # lit belly underline

    # Crown-band ↔ crest blend: a short green→magenta wash sitting where the
    # crown meets the plume root, so the headband stripe dissolves into the
    # crest's cosmic base instead of reading as a separate stripe.
    for i in range(5):
        t = i / 4.0
        cx = HX - 6 + i * 3
        pygame.draw.circle(surf, _aurora_mix(0.15 + t * 0.6), (cx, CROWN_Y + 3), 2)

    # Re-assert Pip's face at 40px: a bright specular glint on the near lens and
    # a sharpened beak edge so the macaw identity survives the downscale.
    pygame.draw.circle(surf, _GLINT, (HX + 6, HY - 3), 2)
    pygame.draw.line(surf, _GLINT, (HX + 8, HY + 1), (HX + 13, HY + 4), 2)  # beak top edge

    # Star flecks CROWDED on the lit back/upper edge (where they catch the rim
    # light) — a fixed scatter (NOT random, so frames are stable) of small
    # white/blue twinkles, each a dot + a tiny cross. Off the face/shadow so the
    # eyes stay clean and the flecks never vanish into the dark belly.
    stars = (
        (24, 42, 1, _GLINT),
        (20, 40, 1, _STARBLU),
        (28, 38, 1, _GLINT),
        (34, 40, 1, _STARBLU),
        (18, 45, 1, _GLINT),
        (30, 44, 1, _STARBLU),
        (39, 43, 1, _GLINT),
    )
    for sx, sy, r, col in stars:
        pygame.draw.circle(surf, col, (sx, sy), r)
        if col is _GLINT:                  # only the brightest get a twinkle cross
            pygame.draw.line(surf, (*col, 160), (sx - 2, sy), (sx + 2, sy), 1)
            pygame.draw.line(surf, (*col, 160), (sx, sy - 2), (sx, sy + 2), 1)


# ── custom compose + getter (halo/ribbons need a back layer) ──────────────────

def _aurora_getter():
    """back aura (halo + ribbons) → galaxy body → front nebula/stars/rim →
    house outline, then the per-(frame, 3°-bucket) rotation cache shared by
    every store skin."""
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        # The house outline is grown from the alpha mask, so the faint additive
        # halo + ribbons must NOT be part of the masked layer — else the dark
        # rim would wrap the glow and kill it. So outline the OPAQUE bird (body
        # + front overlay) alone, then lay the soft back-aura UNDER it. The
        # outline pads by 2px; the aura surface is padded to match before the
        # under-blit so the bird stays centred for the rotation maths.
        bird = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        bird.blit(_aurora_base(wing_angle), (0, PARROT_DY))
        _aurora_front(bird, wing_angle)
        bird = _add_outline(bird)

        aura = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
        pad = (bird.get_width() - COMPOSITE_W) // 2
        back = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _aurora_back(back, wing_angle)
        aura.blit(back, (pad, pad))
        aura.blit(bird, (0, 0))
        return aura

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


build = _aurora_getter()
