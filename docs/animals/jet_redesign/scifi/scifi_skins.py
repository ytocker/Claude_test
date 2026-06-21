"""SCI-FI ENERGY FIGHTER jet skin — round-2 production build.

The winner: v5 · GOLD SOVEREIGN, the faceted diamond cruiser — converged to a
single ship-ready build. The round-1 take read as a warm gold gem that sat too
close to the DRAGON/PHOENIX legendaries; this build re-leads on PLATINUM /
ICY-CYAN cool neon TECH and demotes gold to a SECONDARY accent (the plasma core
and one hero keel seam only). The result is a hard-edged cut-crystal hull that
reads as cool machine, not warm creature.

Concept: an angular FACETED diamond hull with cool neon seam-piping and ONE
white-hot plasma core — part jet, part starship.

Contract (mirrors game/animal_jet_fighter.py so it lifts straight in):

  * `build_scifi(wing_angle_deg) -> pygame.Surface` draws ONE flat frame on a
    64×84 SRCALPHA canvas, hull mass centred at (32,44). Drawn NOSE-RIGHT,
    UPRIGHT, LEVEL — rotation is NOT baked; the game spins it inverted nose-up.
  * The 4 poses are a baked PLASMA PULSE + a 1-frame bright-seam CHARGE sweep +
    a ±1px pitch. ALL glow (rim, seams, plasma core) is baked per frame — no
    live particle system, so both build targets render identically.
  * `get_scifi = _make_prebuilt_skin(build_scifi)` — 4 flat frames + per-(frame,
    3°) rotation cache, each outlined with the house silhouette outline.
  * `BUILDERS = {"skin_scifi": get_scifi}`.

North star: reads at 40px day AND night — one bold faceted hull silhouette with
an UNAMBIGUOUS forward point and a single brightest plasma cluster, the geometry
carried on VALUE (crisp cut planes) so it survives even when the neon is washed
flat by a bright day sky.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline


# ── canvas + hull anchor (mirror animal_jet_fighter composite layout) ────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY          # hull centre → (32, 44)


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a full-body
    build_fn(angle): lazy 4-frame build + per-(frame, 3°) rotation cache,
    each frame outlined with the house silhouette outline."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _pulse(angle_deg):
    """Plasma pulse phase from the wing angle: the 4 poses (50→-40) map to a
    0..1 'throttle' so the baked plasma flares brightest on the middle two
    frames and shrinks at the ends — a heartbeat the eye reads as thrust.

    Triangle-wrapped (bright in the centre, dim at the ends): a perceptible
    throttle pulse at 40px without strobing."""
    t = (50 - angle_deg) / 90.0          # 50→0, 20→.33, -10→.67, -40→1
    return 1.0 - abs(t * 2.0 - 1.0)


def _charge_frame(angle_deg):
    """Which of the 4 poses carries the 1-frame bright-seam CHARGE sweep.

    Only the 3rd pose (-10°, the throttle peak) lights the hero keel + cockpit
    seams to full white-hot; the others keep them at their resting neon. One
    discrete frame is enough to read as a 'charge' tick without the seam ever
    strobing, and — crucially — the hull OUTLINE is identical on every frame,
    so the silhouette never shimmers into noise as it animates."""
    return abs(angle_deg - (-10)) < 1e-6


def _pitch(angle_deg):
    """Tiny nose pitch (px) across the 4 frames so the hull visibly 'breathes'
    with the engine instead of sitting dead-still. ±1px is enough at 40px.
    Applied only to the plasma/core, NOT the hull verts — the silhouette must
    stay frame-stable so the baked outline never wobbles."""
    return int(round((_pulse(angle_deg) - 0.5) * 2.4))


def _blit_add(surf, src, center):
    surf.blit(src, src.get_rect(center=center).topleft,
              special_flags=pygame.BLEND_RGBA_ADD)


def _glow(radius, color, alpha=120):
    """Soft radial halo baked once — the core bloom behind the plasma eye.
    Concentric fading rings so the bloom supports the silhouette, never
    swallows it. ADD-blended so it reads as hot light, not paint."""
    d = max(2, radius * 2)
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    steps = 8
    for i in range(steps, 0, -1):
        a = int(alpha * (i / steps) ** 2)
        r = max(1, int(radius * i / steps))
        pygame.draw.circle(s, (*color, a), (d // 2, d // 2), r)
    return s


# ── palette: PLATINUM / ICY-CYAN primary, GOLD secondary accent only ─────────
# The hull is cool steel-blue cut crystal. Interior facet values are pushed
# ~20% apart vs round-1 so the cut planes read on VALUE alone under a bright
# day sky, not on hue. Gold appears ONLY in the plasma core and the single hero
# keel seam — the secondary accent that keeps a whiff of 'sovereign' premium
# without dragging the read back toward warm DRAGON/PHOENIX.
_HULL_LO   = (26, 38, 54)        # deepest shadow facet (lower hull)
_HULL_MID  = (52, 74, 96)        # mid facet
_HULL_HI   = (132, 168, 196)     # top-lit upper facet (light from upper-left)
_HULL_PEAK = (196, 222, 240)     # brightest cut-plane sliver near the spine
_EDGE      = (12, 18, 28)        # facet keyline

_CYAN      = (60, 210, 255)      # primary icy-cyan neon
_CYAN_HOT  = (208, 250, 255)     # cyan filament hotline
_RIM       = (224, 244, 255)     # cool near-white baked self-rim (NOT warm)

_GOLD      = (255, 206, 90)      # SECONDARY accent: core ring + hero seam
_GOLD_HOT  = (255, 246, 214)     # gold filament hotline
_CORE_WHT  = (255, 255, 255)     # the single brightest pixel cluster


def _neon_seam(surf, edges, color, hot, width=1, bloom_a=(60, 120)):
    """Trace (p0,p1) segments as glowing neon piping: a TIGHT bloom underlay
    (deliberately only +2px so it HUGS the seam and the faceted edge never
    softens) + a crisp filament on top. ADD-blended so crossing seams bloom."""
    lo, hi = bloom_a
    bloom = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for p0, p1 in edges:
        pygame.draw.line(bloom, (*color, lo), p0, p1, width + 2)
    for p0, p1 in edges:
        pygame.draw.line(bloom, (*color, hi), p0, p1, width + 1)
    surf.blit(bloom, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    for p0, p1 in edges:
        pygame.draw.line(surf, hot, p0, p1, width)


def _baked_rim(surf):
    """Bake a TIGHT 1px cool near-white self-rim that HUGS the hull outline —
    a hard specular catch, NOT a soft aura — so the faceted edge stays crisp and
    the hull pops on a bright day sky. Light is from the upper-left (matching
    shipped art: crown highlight + top sheen), so the rim is brightest along the
    top/leading edges and only faintly catches the lower-rear.

    Built as a RING that sits strictly OUTSIDE the painted hull: the silhouette
    is offset-stamped onto a scratch layer, the original silhouette is then
    erased from it, and only the surviving 1px outer fringe is composited back —
    so the rim never paints over the interior facets, seams, or plasma core."""
    mask = pygame.mask.from_surface(surf, threshold=8)
    w, h = surf.get_size()

    ring = pygame.Surface((w, h), pygame.SRCALPHA)
    # Up-left offsets carry the lit edges (bright); down-right is a faint
    # reflected catch so the rim isn't a flat keyline.
    lit = mask.to_surface(setcolor=(*_RIM, 240), unsetcolor=(0, 0, 0, 0))
    dim = mask.to_surface(setcolor=(*_RIM, 70), unsetcolor=(0, 0, 0, 0))
    for off in ((-1, -1), (-1, 0), (0, -1)):
        ring.blit(lit, off)
    ring.blit(dim, (1, 1))
    # Erase the hull's own footprint so only the outer fringe remains.
    cut = mask.to_surface(setcolor=(0, 0, 0, 255), unsetcolor=(0, 0, 0, 0))
    ring.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    surf.blit(ring, (0, 0))


def build_scifi(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    charge = _charge_frame(wing_angle_deg)
    pit = _pitch(wing_angle_deg)

    # Nose-RIGHT. ASYMMETRIC diamond: the front point is ~15% longer & narrower
    # and the rear is blunted, so "forward" is unambiguous at 40px even in the
    # inverted night-dive pose — the long sharp tip always reads as the lead.
    nose_x = 58 + pit
    tail_x = 18
    spine_x = 33                       # widest cross-section, biased forward

    # ── Faceted diamond hull silhouette (asymmetric: sharp front, blunt rear) ─
    diamond = [
        (nose_x, BCY),                 # long sharp nose
        (spine_x, BCY - 13),           # upper shoulder (widest point, forward)
        (tail_x + 6, BCY - 8),         # blunt upper rear
        (tail_x, BCY - 4),             # blunt rear corner (cropped, not pointed)
        (tail_x, BCY + 4),
        (tail_x + 6, BCY + 8),
        (spine_x, BCY + 13),           # lower shoulder
    ]

    # Hull base + interior facets, top-lit from upper-left. Value spread is
    # widened vs round-1 so the cut planes read crisp even when neon is dim.
    pygame.draw.polygon(surf, _HULL_LO, diamond)
    # Upper hull facet (lit) — bounded by the spine keel.
    pygame.draw.polygon(surf, _HULL_MID, [
        (nose_x, BCY), (spine_x, BCY - 13), (tail_x + 6, BCY - 8),
        (tail_x, BCY - 4), (tail_x + 2, BCY)])
    # Brightest top cut-plane sliver hugging the leading upper chine.
    pygame.draw.polygon(surf, _HULL_HI, [
        (nose_x - 2, BCY - 1), (spine_x, BCY - 11), (tail_x + 7, BCY - 6),
        (spine_x + 1, BCY - 5)])
    # A narrow PEAK glint where the upper facet meets the nose — the hardest
    # specular catch, reinforcing the lit upper-left light direction.
    pygame.draw.polygon(surf, _HULL_PEAK, [
        (nose_x - 4, BCY - 1), (spine_x + 3, BCY - 9), (spine_x - 2, BCY - 6)])
    # Lower hull stays in shadow value (the dark underside facet).
    pygame.draw.polygon(surf, _HULL_LO, [
        (nose_x, BCY), (spine_x, BCY + 13), (tail_x + 6, BCY + 8),
        (tail_x, BCY + 4), (tail_x + 2, BCY)])
    pygame.draw.polygon(surf, _EDGE, diamond, 1)

    # ── Asymmetric COCKPIT facet near the nose (the forward tell) ────────────
    # A single dark canopy wedge set forward of the spine — its tilt is biased
    # toward the nose so the eye reads it as a windscreen pointing the way.
    cock = [(spine_x + 6, BCY - 2), (nose_x - 14, BCY - 5),
            (nose_x - 10, BCY), (nose_x - 16, BCY + 3), (spine_x + 6, BCY + 2)]
    pygame.draw.polygon(surf, (18, 28, 42), cock)
    pygame.draw.polygon(surf, (40, 60, 84), [
        (spine_x + 6, BCY - 2), (nose_x - 14, BCY - 5), (nose_x - 12, BCY - 2)])
    # Cyan energy glint inside the canopy — the cool 'eye' near the nose.
    pygame.draw.line(surf, _CYAN, (spine_x + 8, BCY - 1), (nose_x - 13, BCY - 3), 1)
    pygame.draw.line(surf, _CYAN_HOT, (nose_x - 16, BCY - 1), (nose_x - 12, BCY - 2), 1)

    # ── PRIMARY icy-cyan seam-piping on the facet chines ─────────────────────
    # Hugs the leading/trailing chines and the aft spine. Cool primary read.
    cyan_edges = [
        ((nose_x, BCY), (spine_x, BCY - 13)),          # upper leading chine
        ((spine_x, BCY - 13), (tail_x + 6, BCY - 8)),  # upper trailing chine
        ((nose_x, BCY), (spine_x, BCY + 13)),          # lower leading chine
        ((spine_x, BCY + 13), (tail_x + 6, BCY + 8)),  # lower trailing chine
        ((tail_x + 6, BCY - 8), (tail_x + 6, BCY + 8)),# aft spine seam
    ]
    seam_w = 2 if charge else 1
    _neon_seam(surf, cyan_edges, _CYAN, _CYAN_HOT, 1,
               bloom_a=(90, 160) if charge else (55, 110))

    # ── SECONDARY gold accent: ONE hero keel seam down the centreline ────────
    # The single gold line is the only warm note on the hull — a 'sovereign'
    # keel. On the charge frame it flares white-hot; otherwise it rests gold.
    keel = [((nose_x, BCY), (tail_x + 2, BCY))]
    if charge:
        _neon_seam(surf, keel, _GOLD, _CORE_WHT, 1, bloom_a=(140, 210))
    else:
        _neon_seam(surf, keel, _GOLD, _GOLD_HOT, 1, bloom_a=(60, 120))

    # ── THE single plasma core: the unambiguous brightest pixel cluster ──────
    # Tight gold bloom (secondary accent) wrapping a white-hot core. Kept small
    # and dense so the eye locks onto ONE bright spot at 40px by a clear margin;
    # nothing else on the hull approaches its brightness.
    cx_core = tail_x + 2
    bloom = _glow(int(6 + p * 3), _GOLD, alpha=int(80 + p * 80))
    _blit_add(surf, bloom, (cx_core, BCY))
    core_r = 3 if p > 0.5 else 2
    pygame.draw.circle(surf, _GOLD, (cx_core, BCY), core_r + 1)
    pygame.draw.circle(surf, _CYAN_HOT, (cx_core, BCY), core_r)
    # The white-hot centre is the single brightest pixel cluster on the whole
    # hull by a clear margin — the eye locks onto it instantly at 40px.
    pygame.draw.circle(surf, _CORE_WHT, (cx_core, BCY), max(1, core_r - 1))
    # A 1px aft spit of white at the very rear so the plasma reads as exhaust.
    pygame.draw.line(surf, _CORE_WHT, (tail_x - 2, BCY), (tail_x, BCY), 1)

    # ── Bake the tight cool self-rim LAST so it hugs the final silhouette ────
    _baked_rim(surf)
    return surf


# ── getter + production registry ──────────────────────────────────────────────
get_scifi = _make_prebuilt_skin(build_scifi)

# Single production build (lifts straight to skin_scifi).
BUILDERS = {"skin_scifi": get_scifi}

# label → (getter, read-tell) for the review sheet (single converged build).
VARIANTS = [
    ("v5 · GOLD SOVEREIGN (refined)", get_scifi,
     "platinum/icy-cyan faceted diamond · cool primary, gold core+keel accent · "
     "asymmetric sharp nose · 1 brightest plasma core"),
]
