"""POP FLY (Variant 2) — MIDNIGHT NOIR, monochrome pop-art fly, SCRATCH candidate.

A stark black-ink take on the pop-art housefly: the body is drawn in the same
jet-black as the ink, so the whole barrel reads as one inked silhouette and its
form is carried purely by the outline loop and a white polka-dot halftone on the
shadow side. Every bright element (white domes, white labellum, grey fans, white
setae) pops off the dark. Where Design 5 leans on flat primary colour, this
leans on maximum white-on-black contrast — and a faint cool rim so the noir
silhouette still survives on the night biome, not only a lit day sky.

Exploration only — wrapped by the local `_make_prebuilt_skin` and NOT registered
in any production BUILDERS map.
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


# ── midnight-noir palette ─────────────────────────────────────────────────────
INK      = (17, 17, 17)             # #111111 comic ink — the 40px carrier
THORAX   = (17, 17, 17)             # #111111 jet-black thorax = ink (shape by loop+dots)
ABDOMEN  = (42, 42, 42)             # #2A2A2A dark-charcoal abdomen — a value step off black
BODY_DOT = (255, 255, 255)          # #FFFFFF white Ben-Day polka on the shadow side
EYEW     = (255, 255, 255)          # #FFFFFF white dome — the brightest note
EYEDOT   = (150, 150, 150)          # #969696 grey Ben-Day eye dots (sparse, so white wins)
WHITE    = (255, 255, 255)
WINGGREY = (204, 204, 204)          # #CCCCCC mid-grey wing membrane
WINGDOT  = (255, 255, 255)          # #FFFFFF white halftone → sparkles on the grey fan
LABELLUM = (245, 245, 245)          # near-white sponge pad — a shade under the eye domes
SPEEDLN  = (255, 255, 255)          # #FFFFFF speed lines → pop on the dark body
NIGHTRIM = (168, 178, 196, 120)     # faint cool rim so the black blob reads on night skies


def _ink_outline(layer, thickness=2, color=INK):
    """Grow a uniform closed black comic outline around a layer's silhouette.

    The heavy 2px loop is the brief's stated 40px carrier — applied per
    element so every block reads as its own inked shape after the downscale.
    On the jet-black body the loop merges with the fill, so the outline's job
    there is to fatten the silhouette into one clean noir blob."""
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


def _light_rim(layer, color=NIGHTRIM):
    """Wrap a finished layer in a faint 1px cool rim beneath its silhouette.

    Jet-black ink on a jet-black body evaporates against the night biome, so
    the outermost contour gets one dilation step of a low-alpha cool grey UNDER
    the artwork — invisible enough on a lit day sky, just enough separation on
    a dark one for the silhouette to survive."""
    w, h = layer.get_size()
    mask = pygame.mask.from_surface(layer, threshold=8)
    sil = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.blit(sil, (dx, dy))
    out.blit(layer, (0, 0))
    return out


def _benday(target, region_pts_or_mask, color, spacing=4, radius=1, phase=0):
    """Overlay a regular Ben-Day halftone dot grid clipped to a region.

    Odd rows are half-offset so the grid reads as a hex-packed halftone,
    not a plain lattice. `region` is polygon points or a white mask surface."""
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


# ── one squat membranous fan ──────────────────────────────────────────────────
# A single WIDE-than-tall convex ellipse (a squat dome), not a tall pointed
# blade — the R1 "rabbit-ear" read came from a steep egg. Root sits at the
# bottom centre so the dome swings out and up about its shoulder; the pair
# opens into a broad rounded fan, never a narrow V.
_WING_ROOT = (26, 32)


def _wing_surface():
    """One rounded pop-art fan: a squat grey membrane ellipse (wider than tall),
    a white sparse halftone that sparkles, two bold black fan veins, then a 2px
    ink loop. Kept small enough that the PAIR splays into two readable fans
    around a central notch — not one big grey hood over the black hero."""
    w = pygame.Surface((52, 36), pygame.SRCALPHA)
    membrane = pygame.Rect(0, 0, 38, 20)        # squat: wider than tall
    membrane.center = (26, 14)
    pygame.draw.ellipse(w, WINGGREY, membrane)
    # White, sparse halftone on the mid-grey fan: reads as glinting membrane and
    # keeps the wing bright enough to separate from the near-black body.
    emask = pygame.Surface((52, 36), pygame.SRCALPHA)
    pygame.draw.ellipse(emask, (255, 255, 255, 255), membrane)
    _benday(w, emask, WINGDOT, spacing=6, radius=1)
    # Two bold veins fan out from the root — the only ink inside the membrane.
    pygame.draw.line(w, INK, _WING_ROOT, (13, 10), 2)
    pygame.draw.line(w, INK, _WING_ROOT, (40, 10), 2)
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
def build_pop_v2(wing_angle_deg):
    surf = _new()
    f = (wing_angle_deg + 40) / 90.0        # 1 = wings up, 0 = wings down

    # White comic speed lines streak off the back on the wing-up beats — chosen
    # over ink so they carry against the near-black body instead of vanishing.
    if f > 0.6:
        for k in range(3):
            y = 20 + k * 6
            pygame.draw.line(surf, SPEEDLN, (5, y + 2), (12, y), 1)
            pygame.draw.line(surf, SPEEDLN, (12, y), (19, y - 1), 1)

    # Two squat fans splay up-and-out off a shoulder anchor near (28,31); the
    # dome leans further out on the wing-up frames so the pair rides from a low
    # spread to a raised broad fan — never a tall narrow "rabbit-ear" V.
    wing = _wing_surface()
    ang = 30 + f * 14
    left = pygame.transform.flip(wing, True, False)
    left_root = (wing.get_width() - 1 - _WING_ROOT[0], _WING_ROOT[1])
    _place_rotated(surf, wing, _WING_ROOT, -ang, (34, 31))
    _place_rotated(surf, left, left_root, ang, (22, 31))

    # ── one round inked barrel: black thorax fused into charcoal abdomen ──
    body = _new()
    _aaellipse(body, ABDOMEN, (BCX, 49), 13, 11)
    _aaellipse(body, THORAX, (BCX, 41), 13, 9)
    # Coarse white Ben-Day polka on the shadow side (lower-left) is the ONLY
    # thing that models the black barrel — fewer, larger, evenly-gridded dots
    # read as an intentional halftone at 40px, not as grain.
    smask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    _aaellipse(smask, (255, 255, 255, 255), (BCX - 4, 48), 9, 8)
    _benday(body, smask, BODY_DOT, spacing=6, radius=2, phase=1)
    # A couple of sparse white belly dots read as rounded abdomen banding.
    amask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    _aaellipse(amask, (255, 255, 255, 255), (BCX + 1, 53), 10, 6)
    _benday(body, amask, BODY_DOT, spacing=7, radius=2, phase=3)
    # Short waist band: ink lands on the charcoal side as a value dip, splitting
    # the two-tone barrel without a full stacked-bands divider.
    pygame.draw.line(body, INK, (BCX - 8, 45), (BCX + 8, 45), 2)
    surf.blit(_ink_outline(body, 2), (0, 0))

    # Round sponge labellum (mouth pad) below the face — a bright pad kept a
    # touch smaller and a shade under white so it never out-whites the eyes.
    lab = _new()
    lr = pygame.Rect(0, 0, 11, 9)
    lr.center = (44, 48)
    pygame.draw.ellipse(lab, LABELLUM, lr)
    surf.blit(_ink_outline(lab, 2), (0, 0))

    # ── HERO: two big pure-white goggle eyes that fill the head ──
    # Centres sit 4px apart so a solid ink gutter can live between them; the
    # domes stay PURE white — the sparse grey halftone only whispers form, so
    # the eyes win the brightness fight against every other bright note.
    eyes = _new()
    ecs = ((34, 29), (54, 29))
    for cx, cy in ecs:
        _aaellipse(eyes, EYEW, (cx, cy), 8, 8)
    emask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for cx, cy in ecs:
        _aaellipse(emask, (255, 255, 255, 255), (cx, cy), 8, 8)
    # Sparse, light halftone — the dome stays overwhelmingly white.
    _benday(eyes, emask, EYEDOT, spacing=5, radius=1)
    inked_eyes = _ink_outline(eyes, 2)
    # A small, thin ink pupil plus a bold white glint wedge: the pupil is kept
    # tiny so it never greys the dome, the white wedge is the top highlight.
    for cx, cy in ecs:
        pygame.draw.circle(inked_eyes, INK, (cx + 1, cy + 1), 2)
        pygame.draw.polygon(inked_eyes, WHITE, [
            (cx - 6, cy - 4), (cx - 1, cy - 6), (cx - 3, cy - 1)])
    # Hard 2-3px ink gutter down the seam so the two domes never fuse into one
    # goggle lump after the downscale.
    pygame.draw.line(inked_eyes, INK, (44, 22), (44, 37), 3)
    surf.blit(inked_eyes, (0, 0))

    # ── bristly thorax hump: chunky WHITE setae angled up-back ──
    # 2-3 bold white flicks over a fatter black core, rising off the black
    # thorax to CLEAR the top of the silhouette — they must read as spikes even
    # at 40px, so the invisible speckle is gone and the flicks are thick white.
    for (x0, y0), (x1, y1) in (
            ((28, 32), (26, 12)), ((30, 32), (33, 14)), ((27, 33), (20, 15))):
        pygame.draw.line(surf, INK, (x0, y0), (x1, y1), 4)
        pygame.draw.line(surf, WHITE, (x0, y0), (x1, y1), 2)

    return _light_rim(surf)


build = _make_prebuilt_skin(build_pop_v2)
