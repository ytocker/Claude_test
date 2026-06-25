"""design_4 · TEMPEST CONDOR MACAW — LEGENDARY parrot-wave2 exploration.

A storm-grey raptor-scaled Pip caught in a monochrome squall: a brushed
storm-grey body with deep-slate underwing and a cool steel sheen, lit by a
SINGLE saturated cyan that is the only colour in the whole kit. That one cyan
is reserved for the silhouette-breakers so they read as ONE clean shape, not
noise — a swept twin storm-quill crest raked past the crown, a long forked
vapour-streamer tail trailing past the tail, and the legendary tell: a
contained "eye of the storm" halo (a dark slate-blue storm-disc behind the
head, rimmed in hard pale-cyan). Deliberately steered clear of STORM's gold
lightning bolts, of AURORA's multi-hue soft ribbon, and of SOLAR's warm radial
— this storm is monochrome WIND, a cool desaturated value structure no
legendary owns.

Structure mirrors store_skins._aurora_getter / _moonbloom_getter exactly,
because the halo + streamer tail must paint BEHIND the body and their additive
night-glow must live OUTSIDE the house outline (else the dark rim would box the
squall-glow into a dark-edged island):

  _tempest_back  → storm-disc halo + forked vapour-streamer tail + wind-ticks,
                   in TWO passes (an additive cyan under-glow for the night
                   read, then a HARD opaque pale-cyan ring + streamer rims that
                   survive a bright day sky).
  _tempest_base  → storm-grey re-plumaged body (_build_parrot_with_palette).
  _tempest_front → twin swept storm-quill crest past the crown + brow-spark, a
                   steel back/belly rim — all OPAQUE.
  _add_outline   → the house silhouette over the OPAQUE bird only.
  rotation cache → per-(frame, 3°-bucket), aura laid UNDER the outlined bird,
                   padded to the outline grow.

North star is "lives or dies at 40px in motion": the make-or-break is keeping
the grey deep enough that the lone cyan ALWAYS pops, and keeping cyan to the
crest leading-edges / halo ring / streamer rims so the whole signature reads as
one clean cyan shape. The opaque pale-cyan halo ring + crest edges carry the
DAY read against bright blue; the additive cyan radial beneath them is a
night-only bonus that blooms only on navy.

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
_GREY      = (60, 70, 84)          # #3C4654 storm-grey base
_GREY_HI   = (90, 102, 118)        # top-lit storm-grey highlight
_SLATE     = (30, 39, 51)          # #1E2733 deep slate underwing / core shadow
_CYAN      = (127, 227, 240)       # #7FE3F0 bright cyan — the ONLY saturated pop
_CYAN_DK   = (74, 158, 178)        # shaded cyan, for the inner crest body
_STEEL     = (200, 214, 222)       # #C8D6DE pale steel sheen / highlight
_DISC      = (14, 58, 74)          # #0E3A4A storm-disc dark fill
_DISC_DK   = (10, 40, 52)          # deeper disc core so the eye-of-storm reads
_AVIATOR   = (95, 184, 200)        # #5FB8C8 cool steel-cyan aviator tint
_GLINT     = (224, 248, 252)       # cool near-white glint
# Cool steel-slate house outline — holds the grey body off bright blue without
# the graphic-black of the default rim, so the silhouette stays storm-cool.
_OUTLINE   = (18, 26, 36, 235)


# Body re-plumage: a brushed storm-grey raptor with REAL light-to-dark structure
# (not a flat grey wash, which would dissolve the day silhouette AND give the
# cyan nothing to pop against). The crown / chest / upper back stay top-lit
# steel-grey; the belly, underwing and tail-root drop to deep slate (_SLATE) so
# the bird carries a dark anchor against bright blue while staying desaturated.
# Every channel is held STRICTLY grey/slate — NO blue saturation in the body —
# so the lone cyan of crest/tail/halo is the only saturated colour in frame.
# Aviators are KEPT (Pip's signature) and tinted cool steel-cyan with a glint.
P_TEMPEST = _pal(
    tail=[(40, 50, 62), (52, 62, 76), (66, 78, 92), (84, 96, 112)],
    tail_line=_SLATE,
    body_shadow=_SLATE,
    body_main=_GREY,
    body_chest=(82, 94, 110),
    body_belly=(42, 52, 64),
    sheen=(200, 214, 222, 90),
    wing_main=(70, 82, 98),
    wing_dark=_SLATE,
    wing_tip=(96, 110, 126),
    wing_secondary=None,
    wing_highlight=_GREY_HI,
    head_shadow=(44, 54, 66),
    head_main=_GREY,
    head_cheek=(86, 98, 114),
    head_crown=_GREY_HI,
    lens_frame=(46, 58, 72),
    lens_body=(22, 30, 40),
    lens_tint=(95, 184, 200, 150),
    lens_glint=(214, 240, 246),
    beak_main=(58, 68, 82),
    beak_dark=(32, 40, 52),
    beak_gloss=(96, 110, 126),
    foot=(54, 64, 78),
)


def _tempest_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, P_TEMPEST)


# ── shared helpers ────────────────────────────────────────────────────────────

def _flap_phase(angle_deg):
    """0 on the down-stroke (wing 50°) → 1 on the up-stroke (-40°). The vapour
    streamer whips longer + the crest rakes a touch further back on the up-beat,
    and the wind-ticks drift wider, so the baked squall stays alive across the
    4 frames (the halo/streamer should feel like wind is moving through it)."""
    return 1.0 - (angle_deg + 40) / 90.0


def _ribbon_poly(root, tip, w_root, w_tip, bow):
    """A flat tapered ribbon-tongue from `root` to `tip`, bowed sideways by
    `bow` so the forked streamer reads as wind-curled vapour, not a straight rod
    at 40px. Returns (outline_pts, spine_pts) sharing the spine so the additive
    glow and the opaque rim register exactly."""
    dx, dy = tip[0] - root[0], tip[1] - root[1]
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    px, py = -uy, ux                                   # perpendicular
    mid = (root[0] + dx * 0.5 + px * bow, root[1] + dy * 0.5 + py * bow)
    # Quadratic-Bezier spine so the ribbon curves cleanly.
    spine, steps = [], 8
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        spine.append((u * u * root[0] + 2 * u * t * mid[0] + t * t * tip[0],
                      u * u * root[1] + 2 * u * t * mid[1] + t * t * tip[1]))
    left, right = [], []
    n = len(spine) - 1
    for i, (sx, sy) in enumerate(spine):
        t = i / n
        w = w_root + (w_tip - w_root) * t              # linear taper to the tip
        left.append((sx + px * w, sy + py * w))
        right.append((sx - px * w, sy - py * w))
    return left + right[::-1], spine


# ── back layer: storm-disc halo + forked vapour-streamer tail + wind-ticks ────

def _streamer_geo(angle_deg):
    """The forked vapour streamer trailing off the tail root for this flap
    angle — two ribbon-tongues (an upper short fork + a lower long fork) plus a
    handful of hard wind-streak ticks. Shared by the additive and opaque passes.
    Sweeps DOWN-and-BACK off the tail root into open sky; whips longer + lower
    on the up-beat so the tail feels like vapour caught in a gust."""
    phase = _flap_phase(angle_deg)
    droop = (1.0 - phase) * 3                           # dip on the down-beat
    reach = 1.0 + phase * 0.14                          # stream longer up-beat
    troot = (17, HY + 7)
    # (angle-off-back°, length, root-w, tip-w, bow). The lower fork is the long
    # hero tongue; the upper fork is shorter so the fork reads as a clean V.
    spec = (
        (-30, 24, 4.0, 1.6, -6),    # upper fork, bows up
        (-12, 34, 4.6, 1.4,  7),    # lower fork, longest, bows down
    )
    out = []
    for ang_deg, length, wr, wt, bow in spec:
        a = math.radians(150 + ang_deg)
        tip = (troot[0] + math.cos(a) * length * reach,
               troot[1] + math.sin(a) * length * reach + droop)
        poly, spine = _ribbon_poly(troot, tip, wr, wt, bow)
        out.append((poly, spine, tip))
    return out


def _wind_ticks(angle_deg):
    """A few short hard wind-streak ticks trailing the streamer into open sky —
    hard cyan dashes (NOT soft mist) so the wind read survives the 40px
    downscale. Fixed (non-random) scatter so the 4 baked frames stay stable;
    drift wider on the up-beat."""
    phase = _flap_phase(angle_deg)
    drift = phase * 4
    base = (
        (-4, HY + 18, 6),
        (-9, HY + 28, 7),
        (-14, HY + 24, 5),
        (-2, HY + 33, 5),
    )
    # (x, y, dash-length); dashes rake along the streamer's down-back axis.
    return [(x - drift, y + drift * 0.4, ln) for x, y, ln in base]


def _tempest_back(surf, angle_deg):
    """Behind the outlined bird, so the house outline never boxes the squall
    glow into a dark-rimmed island. Two passes:

      1. ADDITIVE cyan under-glow — the storm-disc's contained radial + the
         streamer haze + wind-tick glow (sells the 'eye of the storm' lit by
         cyan on a NAVY night sky; does nothing on bright blue, by design).
      2. OPAQUE detail — the dark slate storm-disc fill, a HARD pale-cyan opaque
         RING around it, the two solid vapour-streamer tongues (steel field,
         bright-cyan rim) and the hard cyan wind-ticks (carry the read on a
         bright DAY sky where the additive washes out — the make-or-break).

    The disc sits BEHIND + LARGER than the skull so the cyan ring clears the
    silhouette on the flanks — the legendary halo tell, contained as a circle
    (the 'eye of the storm'), never a sprawling aura."""
    streamers = _streamer_geo(angle_deg)
    ticks = _wind_ticks(angle_deg)
    hcx, hcy = HX - 1, HY - 2
    disc_r = 20

    # ── pass 1: additive cyan under-glow (night) ──────────────────────────────
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    # Contained eye-of-storm: a tight central core kept DIM (so the disc still
    # reads as a dark eye, not a flare) ringed by a brighter cyan rim-halo — the
    # light lives on the RING, the way a squall's eye is dark-cored.
    blit_glow(glow, hcx, hcy, 11, (90, 150, 170), alpha=40)
    for i in range(12):
        a = math.radians(i * 30)
        blit_glow(glow, int(hcx + math.cos(a) * disc_r),
                  int(hcy + math.sin(a) * disc_r), 6, _CYAN, alpha=85)
    # Vapour-streamer haze along each tongue so the tail glows cyan on navy.
    for poly, spine, tip in streamers:
        for sp in (spine[len(spine) // 2], spine[-1]):
            blit_glow(glow, int(sp[0]), int(sp[1]), 6, _CYAN, alpha=80)
    for tx, ty, _ln in ticks:
        blit_glow(glow, int(tx), int(ty), 4, _CYAN, alpha=95)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── pass 2: opaque detail (day + night) ───────────────────────────────────
    det = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)

    # Vapour-streamer tongues first (lowest), so the body overlaps their roots →
    # they read as tail plumage, not a fan pinned behind. Each: a slate edge for
    # separation, a steel field, a bright-cyan leading rim + tip, and a couple of
    # hard wind-ticks that come from the opaque pass too.
    for poly, spine, tip in streamers:
        pygame.draw.polygon(det, _SLATE, poly)
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        field = [(cx + (x - cx) * 0.70, cy + (y - cy) * 0.74) for x, y in poly]
        pygame.draw.polygon(det, (78, 92, 108), field)
        # Bright-cyan leading rim down the spine + a hard cyan tip pip — the one
        # saturated edge that reads the streamer as ONE cyan shape at 40px.
        pygame.draw.lines(det, _CYAN, False, spine, 2)
        pygame.draw.circle(det, _CYAN, (int(tip[0]), int(tip[1])), 2)
        pygame.draw.circle(det, _GLINT, (int(tip[0]), int(tip[1])), 1)

    # Hard wind-ticks — short opaque cyan dashes raked along the streamer axis
    # (down-and-back), so the tail trails real wind-streaks, not soft mist.
    for tx, ty, ln in ticks:
        a = math.radians(150 - 12)
        ex = tx + math.cos(a) * ln
        ey = ty + math.sin(a) * ln
        pygame.draw.line(det, _CYAN_DK, (int(tx), int(ty)), (int(ex), int(ey)), 2)
        pygame.draw.line(det, _CYAN, (int(tx), int(ty)),
                         (int(tx + (ex - tx) * 0.6), int(ty + (ey - ty) * 0.6)), 1)

    # STORM-DISC behind the head — the legendary halo TELL. It MUST read in the
    # 40px DAY read (the additive bloom does nothing on bright blue), so the read
    # is carried by HARD opaque shapes: a dark slate disc FILL (the dark eye),
    # then a bold opaque pale-cyan RING over a thinner deep-cyan under-ring so
    # the halo reads as a hard contained circle-arc on the flanks behind the
    # head; the additive cyan rim from pass 1 sits on top for the night bloom.
    pygame.draw.circle(det, _DISC_DK, (hcx, hcy), disc_r - 2)
    pygame.draw.circle(det, _DISC, (hcx, hcy), disc_r - 5)
    pygame.draw.circle(det, _CYAN_DK, (hcx, hcy), disc_r + 1, 1)
    pygame.draw.circle(det, _CYAN, (hcx, hcy), disc_r, 3)
    # Brighter beads on the flanks where the disc clears the silhouette — the
    # part of the ring that actually reads as separating head from sky.
    for fa in (math.radians(198), math.radians(214), math.radians(326),
               math.radians(342)):
        bx = int(hcx + math.cos(fa) * disc_r)
        by = int(hcy + math.sin(fa) * disc_r)
        pygame.draw.circle(det, _GLINT, (bx, by), 2)
        pygame.draw.circle(det, (255, 255, 255), (bx, by), 1)

    surf.blit(det, (0, 0))


# ── front overlay: twin swept storm-quill crest + brow-spark + steel rim ──────

def _tempest_front(surf, angle_deg):
    """Crisp OPAQUE detail painted OVER the body and INSIDE the masked layer, so
    only hard pixels that survive the 40px downscale live here (the soft squall
    glow lives in _tempest_back to dodge the outline):

      * the hero TWIN STORM-QUILL crest — two long flat tapered blades raked
        back past the crown, each ≥3px wide with a hard BRIGHT-CYAN leading edge
        (the single saturated pop the whole crest opens around);
      * a single bright-cyan BROW-SPARK above the aviators;
      * a cool steel back/crown rim + a lit belly rim so the desaturated grey
        body is framed by light, not a flat void on either sky;
      * a re-asserted macaw face glint + steel-cyan lens so Pip survives 40px.
    """
    phase = _flap_phase(angle_deg)
    rake = phase * 2                                    # quills sweep further up-beat
    base_y = CROWN_Y + 1
    cbx = HX - 2                                        # crest root x

    # TWIN STORM-QUILLS — two long swept blades springing from the crown, raked
    # back-and-up past the crown so they break the egg at the top-rear corner.
    # The rear quill is longer (the hero), the front quill shorter + steeper, so
    # they read as a swept pair, not symmetric horns. Each blade: a slate body
    # for value separation, a steel inner fill, and a HARD bright-cyan leading
    # edge that carries the whole crest as one cyan shape at 40px.
    # (root-dx, tip-dx, tip-dy, root-w, bow).
    quills = (
        (-3, -22, -22 - rake, 4.6, -7),   # rear quill, longest hero blade
        (1,  -14, -25 - rake, 4.0, -4),   # front quill, shorter + steeper
    )
    for rdx, tdx, tdy, wr, bow in quills:
        root = (cbx + rdx, base_y)
        tip = (cbx + tdx, base_y + tdy)
        poly, spine = _ribbon_poly(root, tip, wr, 1.4, bow)
        pygame.draw.polygon(surf, _SLATE, poly)
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        field = [(cx + (x - cx) * 0.66, cy + (y - cy) * 0.72) for x, y in poly]
        pygame.draw.polygon(surf, (78, 92, 108), field)
        # The leading (upper-rear) edge of each blade gets the bright-cyan rim,
        # so the cyan reads as ONE clean swept line, never scattered noise.
        pygame.draw.lines(surf, _CYAN, False, spine, 2)
        pygame.draw.circle(surf, _CYAN, (int(tip[0]), int(tip[1])), 2)
        pygame.draw.circle(surf, _GLINT, (int(tip[0]), int(tip[1])), 1)

    # A short slate crest-root nub at the crown so the two quills read as
    # springing from ONE swept tuft, not two pins.
    _poly(surf, _SLATE, [(cbx - 5, base_y + 3), (cbx + 4, base_y + 3),
                         (cbx + 1, base_y - 3), (cbx - 3, base_y - 3)])

    # Cool steel RIM wrapping the back+crown, and a lit belly rim — both ≥2px so
    # the desaturated grey body is framed by light on either sky. The belly rim
    # is a MONOTONIC descending diagonal (never a U) so it can't close into a
    # smile. Steel (not cyan) keeps the body's accents desaturated, reserving the
    # lone cyan for the signature silhouette-breakers.
    pygame.draw.lines(surf, _STEEL, False,
                      [(HX - 12, CROWN_Y + 4), (HX - 5, CROWN_Y),
                       (HX + 4, CROWN_Y + 1), (HX + 12, HY - 3)], 2)
    pygame.draw.lines(surf, _STEEL, False, [(16, 46), (15, 52), (18, 40)], 2)
    pygame.draw.lines(surf, (66, 78, 92), False, [(46, 56), (43, 60), (39, 63)], 2)
    pygame.draw.lines(surf, (66, 78, 92), False, [(34, 65), (28, 67), (22, 67)], 1)

    # Raptor-scale ticks — a few fine steel scale-edges fanning along the lit
    # upper back/wing so the grey plumage reads as brushed raptor scale, never
    # blank. A fixed scatter (NOT random) so the 4 baked frames stay stable;
    # kept off the face/shadow so the eyes stay clean and strictly desaturated.
    scales = (
        ((23, 41), (28, 39)),
        ((27, 44), (33, 42)),
        ((31, 47), (38, 45)),
        ((20, 44), (24, 43)),
        ((35, 46), (41, 44)),
    )
    for a, b in scales:
        pygame.draw.line(surf, (*_STEEL, 130), a, b, 1)
    for sx, sy in ((26, 40), (32, 43), (38, 42)):
        pygame.draw.circle(surf, (150, 164, 178), (sx, sy), 1)

    # Single bright-cyan BROW-SPARK above the aviators — the one front cyan tell
    # that ties the face into the crest's cyan without crowding it.
    bx, by = HX + 1, HY - 7
    pygame.draw.line(surf, _CYAN, (bx - 5, by + 1), (bx + 4, by - 2), 2)
    pygame.draw.circle(surf, _GLINT, (bx + 4, by - 2), 1)

    # Relight the EYE/AVIATOR so the lens zone stops reading as a dead hole: a
    # cool steel-cyan top rim over the near frame, a soft glint, and a faint
    # steel-cyan underglow so the eye reads as a glinting lens. Beak top-edge
    # re-asserted so the macaw identity survives the downscale.
    ex, ey = HX + 6, HY - 2
    pygame.draw.line(surf, _AVIATOR, (ex - 6, ey - 4), (ex + 5, ey - 5), 2)
    pygame.draw.line(surf, (40, 52, 66), (ex - 5, ey + 4), (ex + 4, ey + 4), 1)
    pygame.draw.circle(surf, _GLINT, (ex, ey - 1), 2)
    pygame.draw.circle(surf, _AVIATOR, (ex - 3, ey + 1), 1)
    pygame.draw.line(surf, _STEEL, (HX + 8, HY + 1), (HX + 13, HY + 4), 2)


# ── custom compose + getter (halo/streamer need a back layer) ─────────────────

def _tempest_getter():
    """back aura (storm-disc halo + vapour streamer + wind-ticks) → storm-grey
    body → front twin-quill crest/brow-spark/rim → house outline, then the
    per-(frame, 3°-bucket) rotation cache shared by every store skin. The faint
    additive cyan under-glow must NOT be part of the masked layer (else the dark
    outline would wrap the glow and kill it), so the OPAQUE bird (body + front
    overlay) is outlined alone and the soft back-aura is laid UNDER it, padded to
    match the outline's grow so the bird stays centred for the rotation maths."""
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        bird = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        bird.blit(_tempest_base(wing_angle), (0, PARROT_DY))
        _tempest_front(bird, wing_angle)
        bird = _add_outline(bird, outline_color=_OUTLINE)

        aura = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
        pad = (bird.get_width() - COMPOSITE_W) // 2
        back = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _tempest_back(back, wing_angle)
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


build = _tempest_getter()
