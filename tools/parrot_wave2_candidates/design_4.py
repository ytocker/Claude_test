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
# Lit crown/back highlight, raised ~9% in value so the bird does not sink into
# the navy night sky on the up-flap frames (where this zone faces the camera).
_GREY_HI   = (102, 116, 132)       # top-lit storm-grey highlight
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

def _hard_arc(surf, cx, cy, r, a0, a1, color, width):
    """A CONTINUOUS hard arc stroke from a0→a1 (radians) of radius r, drawn as a
    dense run of connected thick segments capped with dots. pygame.draw.arc's
    width is hollow + ragged at small radii and would dissolve at 40px, so the
    legendary halo ring is built by hand to stay one clean, opaque curved line —
    the day read leans on THIS, not on the additive bloom."""
    steps = 26
    pts = [(cx + math.cos(a0 + (a1 - a0) * (i / steps)) * r,
            cy + math.sin(a0 + (a1 - a0) * (i / steps)) * r)
           for i in range(steps + 1)]
    ipts = [(int(round(x)), int(round(y))) for x, y in pts]
    pygame.draw.lines(surf, color, False, ipts, width)
    # Round caps + seam-fill so the thick stroke never shows facet gaps.
    rad = max(1, width // 2)
    for p in ipts:
        pygame.draw.circle(surf, color, p, rad)


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
    # (angle-off-back°, length, root-w, tip-w, bow). Both forks are raked further
    # DOWN-and-BACK (smaller off-back angle) and the long lower fork is pushed to
    # ~46px with a fatter 2.4px tip so the streamer clears the belly and trails
    # into open sky below-behind the tail root, reading as a forked cyan streamer
    # at 40px instead of a frayed stub tangled in the body.
    spec = (
        (-22, 30, 4.2, 2.0, -7),    # upper fork, bows up
        (-6,  46, 5.0, 2.4,  9),    # lower fork, the long hero tongue, bows down
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
    """ONE bold wind-streak tick trailing the long fork into open sky — a single
    hard cyan dash (NOT soft mist), raked along the streamer's down-back axis.
    The R1 four-tick scatter vanished into noise at 40px and split the lone-cyan
    budget; one bold dash reinforces the wind read without stealing pixels from
    the streamer rim. Fixed (non-random) so the 4 baked frames stay stable;
    drifts a touch wider on the up-beat."""
    phase = _flap_phase(angle_deg)
    drift = phase * 4
    base = ((-7, HY + 30, 8),)
    # (x, y, dash-length); the dash rakes along the streamer's down-back axis.
    return [(x - drift, y + drift * 0.4, ln) for x, y, ln in base]


# Exploration-only switch the round sheet flips to PROVE the day read: when
# True the additive bloom pass is skipped, so the 40px crop shows ONLY the hard
# opaque shapes that must carry the legendary tell on bright blue. Never read on
# the live path (it stays True/normal); it exists purely for the proof crop.
_ADDITIVE = True


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
    # Disc pushed UP-and-BACK off the skull and enlarged so a continuous cyan arc
    # clears the crown + upper-back silhouette on the top-rear flank instead of
    # hiding behind the skull. R1's r=20 centred on the skull left ~80% of the
    # ring occluded — a halo 80% hidden cannot read as a halo at 40px.
    hcx, hcy = HX - 2, HY - 6
    disc_r = 28
    # The exposed top-rear arc — the sky-side span where the ring actually clears
    # the skull and separates head from sky. Pygame's y grows DOWN, so the disc
    # top is 270° and the right (rear, the bird faces right) is 0°/360°. The sweep
    # runs from the upper-back over the CROWN and down the rear flank — a single
    # ~165° span (crown-left → top → right-rear), drawn as ONE bright stroke so it
    # crowns the head instead of dropping a bar down the left wing.
    arc_a0, arc_a1 = math.radians(195), math.radians(360)

    # ── pass 1: additive cyan under-glow (night) ──────────────────────────────
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    # Contained eye-of-storm: a tight central core kept DIM (so the disc still
    # reads as a dark eye, not a flare) ringed by a brighter cyan rim-halo — the
    # light lives on the RING, the way a squall's eye is dark-cored. The bloom is
    # biased onto the exposed arc so the night glow sits where the day ring does.
    blit_glow(glow, hcx, hcy, 12, (90, 150, 170), alpha=36)
    for i in range(13):
        a = arc_a0 + (arc_a1 - arc_a0) * (i / 12)
        blit_glow(glow, int(hcx + math.cos(a) * disc_r),
                  int(hcy + math.sin(a) * disc_r), 6, _CYAN, alpha=80)
    # Vapour-streamer haze along each tongue so the tail glows cyan on navy.
    for poly, spine, tip in streamers:
        for sp in (spine[len(spine) // 2], spine[-1]):
            blit_glow(glow, int(sp[0]), int(sp[1]), 6, _CYAN, alpha=80)
    for tx, ty, _ln in ticks:
        blit_glow(glow, int(tx), int(ty), 4, _CYAN, alpha=95)
    if _ADDITIVE:
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

    # Hard wind-tick — one short opaque cyan dash raked along the streamer axis
    # (down-and-back), so the tail trails a real wind-streak, not soft mist.
    for tx, ty, ln in ticks:
        a = math.radians(150 - 6)
        ex = tx + math.cos(a) * ln
        ey = ty + math.sin(a) * ln
        pygame.draw.line(det, _CYAN_DK, (int(tx), int(ty)), (int(ex), int(ey)), 2)
        pygame.draw.line(det, _CYAN, (int(tx), int(ty)),
                         (int(tx + (ex - tx) * 0.6), int(ty + (ey - ty) * 0.6)), 2)

    # STORM-DISC behind the head — the legendary halo TELL. It MUST read in the
    # 40px DAY read with the additive bloom DISABLED (the bloom does nothing on
    # bright blue), so the read is carried entirely by HARD opaque shapes: a dark
    # slate disc FILL (the contained dark eye, kept small so it never blooms),
    # then the legendary tell — a CONTINUOUS bright-cyan arc swept across the
    # exposed top-rear ~150° as one curved line, ≥4px thick, so it reads as a
    # single hard cyan ring clearing the crown, not a string of dots.
    pygame.draw.circle(det, _DISC_DK, (hcx, hcy), disc_r - 12)
    pygame.draw.circle(det, _DISC, (hcx, hcy), disc_r - 15)
    _hard_arc(det, hcx, hcy, disc_r, arc_a0, arc_a1, _CYAN_DK, 6)
    _hard_arc(det, hcx, hcy, disc_r, arc_a0, arc_a1, _CYAN, 4)
    # A couple of bright glints where the arc crests the crown + tops the rear,
    # to give the continuous ring a hard sparkle without breaking it into beads.
    for fa in (math.radians(255), math.radians(320)):
        bx = int(hcx + math.cos(fa) * disc_r)
        by = int(hcy + math.sin(fa) * disc_r)
        pygame.draw.circle(det, _GLINT, (bx, by), 2)

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
    # (root-dx, tip-dx, tip-dy, root-w, bow). The two roots are spread a touch
    # wider in x so the blades read as a clean swept V at the base instead of
    # merging into one wedge on the day f2 read.
    quills = (
        (-5, -23, -22 - rake, 4.6, -7),   # rear quill, longest hero blade
        (3,  -13, -25 - rake, 4.0, -4),   # front quill, shorter + steeper
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
    _poly(surf, _SLATE, [(cbx - 6, base_y + 3), (cbx + 5, base_y + 3),
                         (cbx + 1, base_y - 3), (cbx - 4, base_y - 3)])

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

    # Single bright-cyan BROW-SPARK — moved LOWER + more FORWARD (down onto the
    # brow over the front of the aviators) so it pulls clear of the crest/halo-arc
    # cluster at the top-rear of the head. At 40px the crest, the halo arc, this
    # brow-spark and the tail streamer then read as 3–4 DISTINCT cyan shapes
    # instead of one merged cyan smudge top-right of the skull.
    bx, by = HX + 7, HY - 3
    pygame.draw.line(surf, _CYAN, (bx - 4, by + 2), (bx + 5, by - 1), 2)
    pygame.draw.circle(surf, _GLINT, (bx + 5, by - 1), 1)

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
