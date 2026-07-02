"""POP FLY (Variant 5: CHERRY BOMB) — inverted pop-art housefly, SCRATCH candidate.

Design 5's red+yellow primaries flipped and pushed hotter: a chalk-white
thorax stacked over a deep-red abdomen. The value structure is deliberately
reversed from Design 5 so the pair read as a matched light/dark set — same
Lichtenstein construction (flat colour blocks, a uniform 2px comic ink loop on
every element, whisper-sparse halftone) but cherry-hot instead of sunny.

Warmth is pulled UP to the face: smooth warm-pink eye domes and red thorax
setae give the head the energy, so the eye reads the face first and the red
abdomen second — not the other way round. Wing membrane is a cool mid-grey so
it separates cleanly from the chalk-white thorax across the ink seam.

Exploration only — wrapped by the local `_make_prebuilt_skin` and NOT
registered in any production BUILDERS map.
"""
import math

import pygame

try:
    from game.animal_skins import (
        _make_prebuilt_skin, _new, BCX, BCY, HCX, HCY,
    )
except Exception:                       # inline fallback for isolated renders
    import pygame as _pg
    BCX, BCY, HCX, HCY = 32, 44, 44, 34
    _WING = (50, 20, -10, -40)

    def _new():
        return _pg.Surface((64, 84), _pg.SRCALPHA)

    def _make_prebuilt_skin(build_fn):
        cache = {}
        def getter(frame_idx, tilt_deg):
            if not cache:
                cache["f"] = [build_fn(a) for a in _WING]
            fr = cache["f"][frame_idx % 4]
            if tilt_deg:
                return _pg.transform.rotozoom(fr, tilt_deg, 1.0)
            return fr
        return getter

from game.parrot import _aaellipse


# ── CHERRY BOMB palette (Design 5 inverted: white on top, red below) ──────────
INK       = (17, 17, 17)            # #111111 comic ink — the 40px carrier
THORAX    = (245, 245, 245)         # #F5F5F5 chalk-white thorax (was red)
THORAX_D  = (204, 17, 17)           # #CC1111 red polka-shadow on the white dome
ABDOMEN   = (204, 17, 17)           # #CC1111 deep-red abdomen (was yellow)
ABDOMEN_D = (17, 17, 17)            # #111111 black halftone banding on the red
RED       = (204, 17, 17)           # #CC1111 veins + setae + speed-line energy
EYEW      = (255, 202, 204)         # #FFCACC warm-pink eye dome (smooth, no dots)
PUPIL     = (17, 17, 17)            # #111111 black pupil for a focused stare
WHITE     = (255, 255, 255)
WINGGREY  = (214, 219, 224)         # #D6DBE0 cool mid-grey wing — cooler + darker
                                    # than the chalk thorax so they never fuse
WINGDOT   = (34, 34, 34)            # #222222 black halftone in the fan
LABELLUM  = (204, 17, 17)           # #CC1111 deep-red sponge mouth pad


def _ink_outline(layer, thickness=2, color=INK):
    """Grow a uniform closed black comic outline around a layer's silhouette.

    The heavy 2px loop is the brief's stated 40px carrier — applied per
    element so every block reads as its own inked shape after the downscale."""
    w, h = layer.get_size()
    mask = pygame.mask.from_surface(layer, threshold=8)
    sil = mask.to_surface(setcolor=(*color, 255), unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    r = thickness
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r + 1:
                out.blit(sil, (dx, dy))
    out.blit(layer, (0, 0))
    return out


def _benday(target, region_pts_or_mask, color, spacing=4, radius=1, phase=0):
    """Overlay a regular Ben-Day halftone dot grid clipped to a region.

    Odd rows are half-offset so the grid reads as a hex-packed halftone,
    not a plain lattice. `region` is polygon points or a white mask surface.
    On pale blocks the pitch is kept wide so only 2–3 dots survive the 40px
    downscale — a whisper of texture, never noise."""
    w, h = target.get_size()
    if isinstance(region_pts_or_mask, pygame.Surface):
        mask = region_pts_or_mask
    else:
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255), region_pts_or_mask)
    dots = pygame.Surface((w, h), pygame.SRCALPHA)
    row = 0
    y = phase
    while y < h:
        x0 = (spacing // 2) if (row % 2) else 0
        x = x0 + phase
        while x < w:
            pygame.draw.circle(dots, color, (x, y), radius)
            x += spacing
        y += spacing
        row += 1
    dots.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    target.blit(dots, (0, 0))


# ── one smooth membranous fan ─────────────────────────────────────────────────
# Root pivot sits at the left tip; the membrane is a SINGLE convex rounded oval
# so the downscaled outer arc stays clean — no faceted ink spikes — and only
# THEN takes its halftone + ink loop. Reads as a translucent fan, not a
# patterned bowtie.
_WING_ROOT = (8, 24)


def _wing_surface():
    """One rounded pop-art fan: a single smooth cool-grey membrane ellipse, a
    whisper-sparse black halftone, ONE bold red structural vein, then a 2px ink
    loop. The grey membrane stays cooler and darker than the chalk thorax so
    the ink seam between them always reads at 40px."""
    w = pygame.Surface((52, 48), pygame.SRCALPHA)
    membrane = pygame.Rect(0, 0, 36, 26)
    membrane.center = (26, 24)
    pygame.draw.ellipse(w, WINGGREY, membrane)
    # Wide-pitch halftone: only a couple of dots survive downscale — texture,
    # not the busy field the R1 wings drowned in.
    emask = pygame.Surface((52, 48), pygame.SRCALPHA)
    pygame.draw.ellipse(emask, (255, 255, 255, 255), membrane)
    _benday(w, emask, WINGDOT, spacing=9, radius=1)
    # ONE bold red vein down the fan's spine — red is structure here, not clutter.
    pygame.draw.line(w, RED, _WING_ROOT, (40, 22), 2)
    return _ink_outline(w, 2)


def _place_rotated(dst, layer, pivot_local, angle_deg, pivot_dst):
    """Rotate `layer` by `angle_deg` (CCW) and blit it so `pivot_local` lands
    exactly on `pivot_dst` — lets the wing swing about its root, not its box."""
    rot = pygame.transform.rotozoom(layer, angle_deg, 1.0)
    w, h = layer.get_size()
    ox, oy = pivot_local[0] - w / 2.0, pivot_local[1] - h / 2.0
    rad = math.radians(angle_deg)
    rx = ox * math.cos(rad) + oy * math.sin(rad)
    ry = -ox * math.sin(rad) + oy * math.cos(rad)
    px = rot.get_width() / 2.0 + rx
    py = rot.get_height() / 2.0 + ry
    dst.blit(rot, (int(round(pivot_dst[0] - px)), int(round(pivot_dst[1] - py))))


# ── the fly ──────────────────────────────────────────────────────────────────
def build_pop_v5(wing_angle_deg):
    surf = _new()
    f = (wing_angle_deg + 40) / 90.0        # 1 = wings up, 0 = wings down

    # Two short red speed strokes crack off the far back-left on the wing-up
    # beats — kept clearly OUTSIDE the wing silhouette so red stays structure,
    # a bold energy hit that reads at 40px without slashing across the fans.
    if f > 0.6:
        pygame.draw.line(surf, RED, (2, 13), (9, 10), 2)
        pygame.draw.line(surf, RED, (1, 20), (8, 17), 2)

    # Two smooth fans sweep up-and-back off a shoulder anchor near (28,31);
    # the fan opens on the wing-up frames so tips ride from low-wide to a
    # raised spread — never a tall narrow "rabbit-ear" V.
    wing = _wing_surface()
    ang = 3 + f * 30
    left = pygame.transform.flip(wing, True, False)
    left_root = (wing.get_width() - 1 - _WING_ROOT[0], _WING_ROOT[1])
    _place_rotated(surf, wing, _WING_ROOT, ang, (29, 31))
    _place_rotated(surf, left, left_root, -ang, (27, 31))

    # ── one round inked barrel: white thorax fused into deep-red abdomen ──
    body = _new()
    _aaellipse(body, ABDOMEN, (BCX, 49), 13, 11)
    _aaellipse(body, THORAX, (BCX, 41), 13, 9)
    # Wide-pitch red polka under the WHITE thorax dome — a whisper of value,
    # only a couple of dots at 40px.
    tmask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    _aaellipse(tmask, (255, 255, 255, 255), (BCX, 43), 12, 7)
    _benday(body, tmask, THORAX_D, spacing=9, radius=1, phase=1)
    # Black Ben-Day banding rows read as rounded shading on the RED abdomen.
    amask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    _aaellipse(amask, (255, 255, 255, 255), (BCX + 1, 52), 11, 7)
    _benday(body, amask, ABDOMEN_D, spacing=5, radius=1, phase=2)
    # A short waist band, not a full stacked-bands divider — the barrel wins.
    pygame.draw.line(body, INK, (BCX - 8, 45), (BCX + 8, 45), 2)
    surf.blit(_ink_outline(body, 2), (0, 0))

    # Round sponge labellum (mouth pad) below the face, its own 2px ink loop.
    lab = _new()
    lr = pygame.Rect(0, 0, 14, 11)
    lr.center = (46, 47)
    pygame.draw.ellipse(lab, LABELLUM, lr)
    surf.blit(_ink_outline(lab, 2), (0, 0))

    # ── HERO: two big warm-pink goggle eyes that fill the head ──
    # SMOOTH fill (no halftone greying them out) so the warm pink pulls the
    # focal point up to the face. Each dome gets one hard white glint + a black
    # pupil for a focused stare. Centres sit a true 2px apart and a solid ink
    # gutter runs the seam so the pair always read as TWO eyes.
    eyes = _new()
    ecs = ((35, 30), (53, 30))
    for cx, cy in ecs:
        _aaellipse(eyes, EYEW, (cx, cy), 8, 8)
    inked_eyes = _ink_outline(eyes, 2)
    for cx, cy in ecs:
        pygame.draw.circle(inked_eyes, PUPIL, (cx, cy + 1), 3)
        # Single hard specular glint in the upper-left, over the pupil.
        pygame.draw.circle(inked_eyes, WHITE, (cx - 3, cy - 3), 2)
    # Belt-and-braces 2px ink gutter down the seam so the domes never read as
    # one goggle even after the downscale.
    pygame.draw.line(inked_eyes, INK, (44, 22), (44, 38), 2)
    surf.blit(inked_eyes, (0, 0))

    # ── bristly thorax hump: chunky RED setae angled up-back ──
    # Red (not black) so warmth reads at the FACE, matching the pink eyes and
    # balancing the red abdomen — the notch-breaks over the white dome's top
    # still push the body from "ladybug" to "fly".
    for (x0, y0), (x1, y1) in (
            ((28, 34), (23, 28)), ((25, 35), (20, 30)), ((31, 33), (26, 27))):
        pygame.draw.line(surf, RED, (x0, y0), (x1, y1), 2)

    return surf


build = _make_prebuilt_skin(build_pop_v5)
