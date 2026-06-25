"""design_4 · MOONBLOOM MACAW — LEGENDARY parrot-wave2 exploration.

A night-blooming moonflower given wings: a luminous pearl-white / lilac macaw
wearing a full OPENED moonflower as a crest, haloed by a soft pale-gold
full-moon disc behind the head, and trailing a petal-and-pollen tail. This is
night-FLORA in moonlight — soft pearls + warm moon-gold + drifting pollen — and
is deliberately steered clear of deep-sea biolumen (no abyssal navy, no
lure-stalk, no teal photophores) and of ice (organic petals, warm lilac/gold
cast, never crystal spikes).

Structure mirrors store_skins._aurora_getter exactly, because the halo + petal
tail must paint BEHIND the body and their soft glow must live OUTSIDE the house
outline (else the dark rim would box the bloom into a dark-edged island):

  _moonbloom_back  → moon-disc halo + petal-streamer tail + pollen-motes, in
                     TWO passes (an additive under-glow for night, then opaque
                     pale-rim detail that survives a bright day sky).
  _moonbloom_base  → pearl/lilac re-plumaged body (_build_parrot_with_palette).
  _moonbloom_front → the opened 5-petal moonflower crest past the crown, the
                     petal-vein scatter, and the cool moon rim — all OPAQUE.
  _add_outline     → the house silhouette over the OPAQUE bird only.
  rotation cache   → per-(frame, 3°-bucket), with the aura laid UNDER the
                     outlined bird, padded to the outline grow.

North star is "lives or dies at 40px in motion": the make-or-break is the
DAY-sky read of a bright pearl bird, so the opaque pale-gold moon rim, the
lilac petal cores, and the deep-lilac line work all carry hard value contrast
against bright blue — the additive glow is a night-only bonus on top.

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
_PEARL     = (243, 238, 248)       # #F3EEF8 pearl body
_PEARL_HL  = (252, 250, 254)       # top-lit pearl highlight (crown / upper back)
_LILAC     = (185, 168, 214)       # #B9A8D6 lilac shadow
_LILAC_DK  = (122, 104, 166)       # deepened core-shadow — the day-side dark anchor
_MINT      = (224, 240, 232)       # mint sheen, warmed off greenish toward pearl
_MOONGOLD  = (246, 230, 168)       # #F6E6A8 moon-gold halo / pollen
_DEEPLILAC = (130, 112, 174)       # deep lilac line (a touch darker than #8E7CB8)
_VIOLET    = (198, 184, 224)       # aviator moon-violet tint
_GLINT     = (255, 255, 255)       # white petal / lens glint
# Warm dark-LILAC house outline — holds the pearl body off bright blue without
# the graphic-black of the default rim, so the silhouette stays organic-moonlit.
_OUTLINE   = (56, 42, 80, 235)

# Petal & pollen ramps. Petals run a luminous white at the tip → lilac toward
# the root so each one reads as a curved moonlit petal, never a flat lozenge.
_PETAL_HI  = (250, 247, 252)       # near-white petal tip
_PETAL_LO  = (188, 170, 214)       # lilac petal root
_POLLEN_HI = (255, 247, 200)       # luminous pollen-heart / mote core


def _petal_mix(t):
    """White petal-tip → lilac petal-root, the moonbloom's signature ramp."""
    return lerp_color(_PETAL_HI, _PETAL_LO, t)


# Body re-plumage: a luminous pearl macaw built with REAL light-to-dark
# structure (not an even pearl wash, which is what dissolved the day silhouette).
# The crown / chest / upper back stay top-lit near-white pearl; the belly,
# back-underside, lower wing and tail-root drop to a deep lilac core-shadow
# (_LILAC_DK) so the bird carries a dark anchor against bright blue while still
# reading moonlit. The aviators are KEPT (Pip's signature) and tinted
# moon-violet with a soft white glint; the beak is warmed toward moon-gold so
# the macaw face still reads.
P_MOONBLOOM = _pal(
    tail=[(176, 158, 204), (196, 180, 220), (218, 206, 234), (240, 234, 248)],
    tail_line=_DEEPLILAC,
    body_shadow=_LILAC_DK,
    body_main=_PEARL,
    body_chest=(252, 250, 254),
    body_belly=(200, 184, 222),
    sheen=(228, 240, 234, 110),
    wing_main=(214, 202, 230),
    wing_dark=_LILAC_DK,
    wing_tip=(248, 244, 252),
    wing_secondary=None,
    wing_highlight=_PEARL_HL,
    head_shadow=_LILAC,
    head_main=_PEARL,
    head_cheek=(250, 246, 252),
    head_crown=_PEARL_HL,
    lens_frame=(140, 124, 180),
    lens_body=(70, 58, 100),
    lens_tint=(198, 184, 224, 150),
    lens_glint=(250, 248, 254),
    beak_main=(238, 220, 168),
    beak_dark=(170, 144, 92),
    beak_gloss=(252, 242, 206),
    foot=(170, 152, 196),
)


def _moonbloom_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, P_MOONBLOOM)


# ── shared helpers ────────────────────────────────────────────────────────────

def _flap_phase(angle_deg):
    """0 on the down-stroke (wing 50°) → 1 on the up-stroke (-40°). Petal
    streamers ripple long/loose on the up-beat and drift the pollen-motes wider,
    so the baked bloom still feels alive across the 4 frames."""
    return 1.0 - (angle_deg + 40) / 90.0


def _smooth_curve(p0, p1, p2, steps=10):
    """Quadratic-Bezier sample list so petal streamers render as smooth curves,
    not the 3-point polylines that read as straight rods at 40px."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def _petal_poly(tip, root, width, curve=0.0, blunt=0.0):
    """A petal outline as a smooth bowed lobe from `root` out to `tip`.

    `blunt` (0..1) controls the tip: 0 tapers to a point (teardrop, used for the
    flowing tail streamers); toward 1 the lobe stays WIDE right up to a rounded
    BLUNT tip — a fat flower-petal whose tip survives the 40px downscale ≥3px
    wide. `curve` bows the spine sideways so a fanned cluster reads as petals
    fanning, not a rigid star. Returns (outline_pts, spine_pts)."""
    dx, dy = tip[0] - root[0], tip[1] - root[1]
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    px, py = -uy, ux                                   # perpendicular
    mid = (root[0] + dx * 0.5 + px * curve, root[1] + dy * 0.5 + py * curve)
    spine = _smooth_curve(root, mid, tip, steps=8)
    # Width profile along the spine: narrow at the root (where it springs from
    # the crown), swelling to full `width`, then — for a blunt flower petal —
    # holding near-full width up to the tip instead of pinching to a point.
    left, right = [], []
    n = len(spine) - 1
    for i, (sx, sy) in enumerate(spine):
        t = i / n
        if t < 0.30:                                   # root taper
            w = width * (t / 0.30) ** 0.7
        else:
            tt = (t - 0.30) / 0.70
            # Point tip (blunt=0): sin falloff. Blunt tip (blunt=1): stays wide.
            point = math.sin((1 - tt) * math.pi / 2)
            blunt_w = 1.0 - tt * tt * 0.35             # only a gentle round-off
            w = width * (point * (1 - blunt) + blunt_w * blunt)
        left.append((sx + px * w, sy + py * w))
        right.append((sx - px * w, sy - py * w))
    # Cap a blunt tip with a small rounded arc so it reads as a soft lobe, not a
    # flat-cut edge, at the top of the bloom.
    if blunt > 0.4:
        cap = []
        tipw = width * (1.0 - 0.35) * blunt
        for k in range(5):
            a = math.pi * (k / 4)                       # sweep across the tip
            cap.append((tip[0] + px * math.cos(a) * tipw - ux * math.sin(a) * tipw,
                        tip[1] + py * math.cos(a) * tipw - uy * math.sin(a) * tipw))
        return left + cap + right[::-1], spine
    return left + right[::-1], spine


# ── back layer: moon-disc halo + petal-streamer tail + pollen-motes ───────────

def _streamer_geo(angle_deg):
    """The 3 petal streamers replacing the tail fan for this flap angle — a
    spine + outline + width per streamer, shared by the additive and opaque
    passes so the glow and the petal register exactly. They sweep DOWN-and-BACK
    off the tail root into open sky, longest in the centre."""
    phase = _flap_phase(angle_deg)
    droop = (1.0 - phase) * 3                           # dip on the down-beat
    reach = 1.0 + phase * 0.12                          # stream longer up-beat
    troot = (17, HY + 8)
    spec = (
        (-40, 27, -5),      # upper streamer, bows up
        (-26, 32, 1),       # centre, longest
        (-13, 26, 6),       # lower streamer, bows down
    )
    out = []
    for ang_deg, length, bow in spec:
        a = math.radians(150 + ang_deg)
        tip = (troot[0] + math.cos(a) * length * reach,
               troot[1] + math.sin(a) * length * reach + droop)
        poly, spine = _petal_poly(tip, troot, 4.2, curve=bow)
        out.append((poly, spine, tip))
    return out


def _pollen_motes(angle_deg):
    """3–4 drifting pollen-glow motes shed into open sky off the petal-streamer
    tips. They drift wider + further on the up-beat so the tail feels alive. A
    fixed (non-random) scatter so the 4 baked frames stay stable."""
    phase = _flap_phase(angle_deg)
    drift = phase * 4
    base = (
        (-6, HY + 26, 2),
        (-12, HY + 20, 2),
        (-16, HY + 33, 1),
        (-3, HY + 36, 1),
    )
    return [(x - drift, y + drift * 0.4, r) for x, y, r in base]


def _moonbloom_back(surf, angle_deg):
    """Behind the outlined bird, so the house outline never boxes the moon-glow
    bloom into a dark-rimmed island. Two passes:

      1. ADDITIVE under-glow — the full-moon disc's soft halo + petal-streamer
         haze + pollen-mote glow (sells 'lit by moonlight' on night sky).
      2. OPAQUE pale detail — an opaque pale-gold moon RIM, the 3 solid petal
         streamers (white→lilac, deep-lilac edged), and bright pollen cores
         (carry the read on a bright DAY sky where the additive washes out —
         the make-or-break for this pearl bird).

    The moon disc sits BEHIND + LARGER than the skull so the pale rim clears the
    silhouette on the flanks — the legendary halo tell."""
    streamers = _streamer_geo(angle_deg)
    motes = _pollen_motes(angle_deg)
    hcx, hcy = HX - 1, HY - 2
    moon_r = 20

    # ── pass 1: additive under-glow (night) ──────────────────────────────────
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    # Soft full-moon disc: a broad central bloom + a ring of smaller blooms so
    # the whole disc fills with light, not just its rim.
    blit_glow(glow, hcx, hcy, 18, _MOONGOLD, alpha=70)
    blit_glow(glow, hcx, hcy, 12, (255, 248, 220), alpha=60)
    for i in range(12):
        a = math.radians(i * 30)
        blit_glow(glow, int(hcx + math.cos(a) * moon_r),
                  int(hcy + math.sin(a) * moon_r), 6, _MOONGOLD, alpha=70)
    # Petal-streamer haze along each spine so the tail glows luna-pale.
    for poly, spine, tip in streamers:
        for sp in (spine[len(spine) // 2], spine[-1]):
            blit_glow(glow, int(sp[0]), int(sp[1]), 6, (236, 226, 248), alpha=85)
        blit_glow(glow, int(tip[0]), int(tip[1]), 5, _MINT, alpha=80)
    # Pollen-mote glow drifting into open sky.
    for mx, my, r in motes:
        blit_glow(glow, int(mx), int(my), 4 + r, _MOONGOLD, alpha=110)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── pass 2: opaque pale detail (day + night) ─────────────────────────────
    det = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)

    # Petal streamers first (lowest), so the body overlaps their roots → they
    # read as tail plumage, not a fan pinned behind. Each: a deep-lilac edge, a
    # white→lilac petal field, a pale spine highlight, a soft mint tip glint.
    for poly, spine, tip in streamers:
        pygame.draw.polygon(det, _DEEPLILAC, poly)
        field = []
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        for x, y in poly:
            field.append((cx + (x - cx) * 0.74, cy + (y - cy) * 0.80))
        pygame.draw.polygon(det, _PETAL_LO, field)
        pygame.draw.lines(det, _PETAL_HI, False, spine, 2)
        pygame.draw.circle(det, _MINT, (int(tip[0]), int(tip[1])), 2)
        pygame.draw.circle(det, _GLINT, (int(tip[0]), int(tip[1])), 1)

    # Full-moon DISC behind the head — the legendary halo TELL, which MUST be
    # visible in the 40px DAY read (additive bloom does nothing on bright blue,
    # so the read is carried by HARD opaque rings here): a soft inner moon-face
    # fill, then a bold 2px opaque pale-gold ring (#F6E6A8) over a faint
    # pale-gold under-ring so the halo reads as a hard disc-arc on the flanks
    # behind the head; the additive fill from pass 1 sits on top for night.
    pygame.draw.circle(det, (250, 240, 200, 90), (hcx, hcy), moon_r - 2)
    pygame.draw.circle(det, (255, 248, 214, 200), (hcx, hcy), moon_r + 1, 3)
    pygame.draw.circle(det, _MOONGOLD, (hcx, hcy), moon_r, 2)
    # Brighter beads on the flanks where the disc clears the silhouette — the
    # part of the halo that actually reads as a ring separating head from sky.
    for fa in (math.radians(196), math.radians(212), math.radians(328),
               math.radians(344)):
        bx = int(hcx + math.cos(fa) * moon_r)
        by = int(hcy + math.sin(fa) * moon_r)
        pygame.draw.circle(det, (255, 250, 224), (bx, by), 2)
        pygame.draw.circle(det, _GLINT, (bx, by), 1)

    # Pollen-mote cores — warmed toward moon-gold (not white): a gold halo + a
    # warm pollen core, tying them to the halo + pollen-heart. Gold reads on both
    # skies where a white mote vanishes on day and reads as generic sparkle on
    # night; only a tiny warm pip lifts the core, no pure-white dot.
    for mx, my, r in motes:
        pygame.draw.circle(det, _MOONGOLD, (int(mx), int(my)), r + 1)
        pygame.draw.circle(det, _POLLEN_HI, (int(mx), int(my)), r)

    surf.blit(det, (0, 0))


# ── front overlay: opened moonflower crest + veins + moon rim ─────────────────

def _moonbloom_front(surf, angle_deg):
    """Crisp OPAQUE detail painted OVER the body and INSIDE the masked layer, so
    only hard pixels that survive the 40px downscale live here (the soft moon
    glow lives in _moonbloom_back to dodge the outline):

      * the hero OPENED MOONFLOWER crest — 5 broad rounded petals fanning past
        the crown, each white→lilac with a pale-gold inner rim, around a
        luminous yellow pollen-heart;
      * a cool moon RIM wrapping the back/crown + a lit belly rim so the lifted
        pearl body is framed by light, not a flat void on either sky;
      * a fine petal-VEIN scatter on the lit upper edge;
      * a re-asserted macaw face glint so Pip survives the downscale.
    """
    base_y = CROWN_Y + 2
    cbx = HX - 1                                        # crest root x

    # OPENED MOONFLOWER — 5 FAT, BLUNT-tipped rounded petals springing from ONE
    # crown base. The cluster is now TALLER than it is wide (a vertical bloom, a
    # stronger silhouette-break above the crown) and every petal is a wide lobe
    # with a rounded tip ≥3px after downscale, so it reads as flower MASS, not a
    # spiky crown/star. Drawn longest-first so the centre petal tucks behind the
    # side leans. Each petal: a deep-lilac edge for separation, a white→lilac
    # field, a pale-gold inner rim catching the moonlight.
    #
    # (dx, dy, bow, ramp). dy is the tall reach; the side petals stay near the
    # centre in x (narrow fan) but rise high, so the bloom is upright.
    petals = (
        (-9, -19, -5, 0.10),     # outer left, high, bows left
        (-4, -25, -2, 0.32),     # inner left, taller
        (0, -29, 0, 0.50),       # centre, tallest
        (4, -25, 2, 0.68),       # inner right, taller
        (9, -19, 5, 0.90),       # outer right, high, bows right
    )
    drawn = []
    for dx, dy, bow, t in petals:
        tip = (cbx + dx, base_y + dy)
        root = (cbx + dx * 0.22, base_y + 1)
        poly, spine = _petal_poly(tip, root, 5.2, curve=bow, blunt=0.85)
        drawn.append((poly, spine, tip, t))
    for poly, spine, tip, t in sorted(drawn, key=lambda p: p[2][1], reverse=True):
        pygame.draw.polygon(surf, _DEEPLILAC, poly)
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        field = [(cx + (x - cx) * 0.80, cy + (y - cy) * 0.84) for x, y in poly]
        pygame.draw.polygon(surf, _petal_mix(t * 0.5), field)
        # Pale-gold inner rim up the petal's lit side so each lobe catches the
        # moon and the blunt tip gets a warm cap that survives 40px.
        rim = spine[len(spine) // 2:]
        pygame.draw.lines(surf, _MOONGOLD, False, rim, 2)
        pygame.draw.circle(surf, _MOONGOLD, (int(tip[0]), int(tip[1])), 2)
        pygame.draw.circle(surf, _PETAL_HI, (int(tip[0]), int(tip[1])), 1)

    # Luminous pollen-HEART at the flower centre — a warm gold core with a bright
    # white pip, the single focal pop the whole crest opens around.
    px, py = cbx, base_y - 2
    pygame.draw.circle(surf, _MOONGOLD, (px, py), 4)
    pygame.draw.circle(surf, _POLLEN_HI, (px, py), 3)
    pygame.draw.circle(surf, _GLINT, (px - 1, py - 1), 1)
    for a in range(0, 360, 60):                        # tiny stamen specks
        r = math.radians(a)
        pygame.draw.circle(surf, (255, 240, 180),
                           (int(px + math.cos(r) * 4), int(py + math.sin(r) * 4)), 1)

    # Cool moon RIM wrapping the back+crown, and a lit belly rim — both ≥2px so
    # the lifted pearl body is framed by light on either sky. The belly rim is a
    # MONOTONIC descending diagonal (never a U) so it can't close into a smile.
    pygame.draw.lines(surf, _MINT, False,
                      [(HX - 12, CROWN_Y + 4), (HX - 5, CROWN_Y),
                       (HX + 4, CROWN_Y + 1), (HX + 12, HY - 3)], 2)
    pygame.draw.lines(surf, _MINT, False, [(16, 46), (15, 52), (18, 40)], 2)
    pygame.draw.lines(surf, _LILAC, False, [(46, 56), (43, 60), (39, 63)], 2)
    pygame.draw.lines(surf, _LILAC, False, [(34, 65), (28, 67), (22, 67)], 1)

    # Petal-VEIN scatter — a few fine deep-lilac vein lines fanning along the lit
    # upper body/wing so the pearl plumage reads as petal-soft, never blank. A
    # fixed scatter (NOT random) so the 4 baked frames stay stable; kept off the
    # face/shadow so the eyes stay clean.
    veins = (
        ((23, 41), (28, 38)),
        ((27, 44), (33, 41)),
        ((31, 47), (38, 44)),
        ((20, 44), (24, 42)),
        ((35, 45), (41, 43)),
    )
    for a, b in veins:
        pygame.draw.line(surf, (*_DEEPLILAC, 150), a, b, 1)
    # A couple of pearl-lilac sheen ticks catching the moonlight on the back —
    # warmed off the old greenish mint so the body stays flora-in-moonlight,
    # never sea-glass.
    for sx, sy in ((26, 40), (32, 43), (38, 42)):
        pygame.draw.circle(surf, (236, 230, 246), (sx, sy), 1)

    # Relight the EYE/AVIATOR so the lens zone stops reading as a dark hole that
    # steals focus from the bloom: a pale moon-violet top rim over the near
    # frame, a soft pearl lens glint, and a faint violet underglow so the eye
    # reads as a glinting lens, not a void. Beak top-edge re-asserted so the
    # macaw identity survives the downscale.
    ex, ey = HX + 6, HY - 2
    pygame.draw.line(surf, _VIOLET, (ex - 6, ey - 4), (ex + 5, ey - 5), 2)  # top rim
    pygame.draw.line(surf, (120, 104, 158), (ex - 5, ey + 4), (ex + 4, ey + 4), 1)
    pygame.draw.circle(surf, _GLINT, (ex, ey - 1), 2)                       # lens glint
    pygame.draw.circle(surf, _VIOLET, (ex - 3, ey + 1), 1)
    pygame.draw.line(surf, _PETAL_HI, (HX + 8, HY + 1), (HX + 13, HY + 4), 2)


# ── custom compose + getter (halo/tail need a back layer) ─────────────────────

def _moonbloom_getter():
    """back aura (moon halo + petal streamers + pollen) → pearl body → front
    flower-crest/veins/rim → house outline, then the per-(frame, 3°-bucket)
    rotation cache shared by every store skin. The faint additive moon-glow must
    NOT be part of the masked layer (else the dark outline would wrap the glow
    and kill it), so the OPAQUE bird (body + front overlay) is outlined alone
    and the soft back-aura is laid UNDER it, padded to match the outline's grow
    so the bird stays centred for the rotation maths."""
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        bird = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        bird.blit(_moonbloom_base(wing_angle), (0, PARROT_DY))
        _moonbloom_front(bird, wing_angle)
        bird = _add_outline(bird, outline_color=_OUTLINE)

        aura = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
        pad = (bird.get_width() - COMPOSITE_W) // 2
        back = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _moonbloom_back(back, wing_angle)
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


build = _moonbloom_getter()
