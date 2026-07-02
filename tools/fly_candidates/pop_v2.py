"""POP FLY (Variant 2) — MIDNIGHT NOIR, monochrome pop-art fly, SCRATCH candidate.

A stark black-ink take on the pop-art housefly: the barrel body is drawn in the
same jet-black/charcoal as the ink, so the whole silhouette reads as one inked
noir blob. To survive the night biome — where black-on-dark-navy evaporates —
the entire barrel is wrapped in a light #CCCCCC rim so its edges separate on BOTH
a lit day sky and a dark night sky. The hero is a symmetric PAIR of huge pure-
white domes with a hard ink gutter: they are the brightest note, and every other
bright element (labellum, wing membranes, setae halos) is deliberately dimmed to
#CCCCCC so nothing out-brights the eyes.

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
THORAX   = (17, 17, 17)             # #111111 jet-black thorax
ABDOMEN  = (42, 42, 42)             # #2A2A2A dark-charcoal abdomen — a value step
BODY_DOT = (255, 255, 255)          # #FFFFFF white Ben-Day polka on shadow side
EYEW     = (255, 255, 255)          # #FFFFFF pure-white dome — brightest note
WHITE    = (255, 255, 255)
GREY     = (136, 136, 136)          # #888888 mid-grey
LIGHT    = (204, 204, 204)          # #CCCCCC — rim, labellum, setae halo, wings
WINGGREY = (204, 204, 204)          # #CCCCCC wing membrane
WINGDOT  = (255, 255, 255)          # #FFFFFF white Ben-Day sparkle on the fan
LABELLUM = (204, 204, 204)          # #CCCCCC sponge pad — always dimmer than eyes
SPEEDLN  = (255, 255, 255)          # #FFFFFF speed lines → pop on the dark body
RIMLT    = (204, 204, 204, 235)     # #CCCCCC night-survival halo under the body


def _ink_outline(layer, thickness=2, color=INK):
    """Grow a uniform closed black comic outline around a layer's silhouette.

    The heavy 2px loop is the brief's stated 40px carrier — applied per element
    so every block reads as its own inked shape after the downscale."""
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


def _rim(layer, color=RIMLT, r=1):
    """Wrap a finished layer in an r-px light halo UNDER its silhouette.

    The body's own outline is jet-black, so on the night biome its edge merges
    into the dark-navy sky. Dilating the silhouette one step in #CCCCCC and
    laying it BENEATH the artwork leaves a thin light contour that only peeks out
    past the black loop — invisible-ish on a lit sky, a clean separating edge on
    a dark one. This is the night-survivability gate."""
    w, h = layer.get_size()
    mask = pygame.mask.from_surface(layer, threshold=8)
    sil = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r + 1:
                out.blit(sil, (dx, dy))
    out.blit(layer, (0, 0))
    return out


def _benday(target, region_pts_or_mask, color, spacing=9, radius=2, phase=0):
    """Overlay a regular Ben-Day halftone dot grid clipped to a region.

    Odd rows are half-offset so the grid reads as a hex-packed halftone, not a
    plain lattice. `region` is polygon points or a white mask surface."""
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


# ── one short, wide fan swept behind/below the body ───────────────────────────
# The R2 grey dot mass out-massed the black hero. Here the wing is a small squat
# ellipse (wider than tall) rooted at its base so the PAIR tucks behind and below
# the barrel, peeking out rather than hooding over it. The round body must stay
# the biggest silhouette on screen.
_WING_ROOT = (17, 21)


def _wing_surface():
    """One short, wide pop-art fan: a squat #CCCCCC membrane ellipse (wider than
    tall), a sparse white Ben-Day sparkle, two small ink veins, then a 2px ink
    loop. Deliberately kept small so the pair reads as swept-back wings BEHIND
    the barrel, never a grey hood over the black hero."""
    w = pygame.Surface((34, 24), pygame.SRCALPHA)
    membrane = pygame.Rect(0, 0, 24, 13)        # squat: wider than tall
    membrane.center = (17, 11)
    pygame.draw.ellipse(w, WINGGREY, membrane)
    emask = pygame.Surface((34, 24), pygame.SRCALPHA)
    pygame.draw.ellipse(emask, (255, 255, 255, 255), membrane)
    _benday(w, emask, WINGDOT, spacing=9, radius=2)
    pygame.draw.line(w, INK, _WING_ROOT, (7, 7), 2)
    pygame.draw.line(w, INK, _WING_ROOT, (24, 7), 2)
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

    # White comic speed lines streak off the back on the wing-up beats — white,
    # not ink, so they carry against the near-black body instead of vanishing.
    if f > 0.6:
        for k in range(3):
            y = 20 + k * 6
            pygame.draw.line(surf, SPEEDLN, (4, y + 2), (11, y), 1)
            pygame.draw.line(surf, SPEEDLN, (11, y), (18, y - 1), 1)

    # Two short squat fans tuck behind and below the barrel off a low shoulder
    # anchor; they lift a little on the wing-up frames but never rise into a hood
    # over the body — the black barrel stays the largest shape.
    wing = _wing_surface()
    ang = 16 + f * 22
    left = pygame.transform.flip(wing, True, False)
    left_root = (wing.get_width() - 1 - _WING_ROOT[0], _WING_ROOT[1])
    _place_rotated(surf, wing, _WING_ROOT, -ang, (33, 37))
    _place_rotated(surf, left, left_root, ang, (23, 37))

    # ── HERO SILHOUETTE: one round inked barrel, rimmed for night survival ──
    body = _new()
    _aaellipse(body, ABDOMEN, (BCX, 49), 13, 12)
    _aaellipse(body, THORAX, (BCX, 40), 13, 10)
    # Coarse white Ben-Day polka on the shadow side (lower-left) is the only
    # thing that models the black barrel — sparse, large, evenly gridded so it
    # reads as an intentional halftone at 40px, not as grain.
    smask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    _aaellipse(smask, (255, 255, 255, 255), (BCX - 3, 49), 10, 9)
    _benday(body, smask, BODY_DOT, spacing=9, radius=2, phase=1)
    # Short waist band: ink lands on the charcoal side as a value dip, splitting
    # the two-tone barrel without a full stacked-bands divider.
    pygame.draw.line(body, INK, (BCX - 8, 45), (BCX + 8, 45), 2)
    inked_body = _ink_outline(body, 2)
    # The #CCCCCC halo lives OUTSIDE the black loop → the barrel edge survives on
    # a dark night sky as well as a lit day sky. This is the survivability gate.
    surf.blit(_rim(inked_body, RIMLT, r=1), (0, 0))

    # ── bristly thorax setae: black spikes with a light halo backing ──
    # Black-on-black setae vanished in R2. Each spike now gets a #CCCCCC halo
    # laid down first (fat), then the black seta over it — so 2-3 bold bristles
    # register against the jet-black thorax on all four frames.
    for (x0, y0), (x1, y1) in (
            ((29, 33), (27, 16)), ((31, 33), (34, 17)), ((27, 34), (20, 18))):
        pygame.draw.line(surf, LIGHT, (x0, y0), (x1, y1), 4)
        pygame.draw.line(surf, INK, (x0, y0), (x1, y1), 2)

    # Round sponge labellum (mouth pad) below the face — small (r4) and #CCCCCC
    # so it is a clearly dimmer grey pad that NEVER out-brights the white eyes.
    lab = _new()
    lr = pygame.Rect(0, 0, 8, 7)
    lr.center = (44, 46)
    pygame.draw.ellipse(lab, LABELLUM, lr)
    surf.blit(_ink_outline(lab, 2), (0, 0))

    # ── HERO: a symmetric PAIR of huge pure-white domes, front-and-centre ──
    # r8 domes 18px apart leave a hard 2px ink gutter down the seam. The domes
    # are PURE flat white with no internal texture — no target, no spiral, no
    # halftone — so they are unambiguously the brightest element in the sprite.
    eyes = _new()
    ecs = ((35, 31), (53, 31))
    for cx, cy in ecs:
        _aaellipse(eyes, EYEW, (cx, cy), 8, 8)
    inked_eyes = _ink_outline(eyes, 2)
    # A crisp white glint wedge in each dome's upper-left reads as wet shine
    # without denting the overall whiteness.
    for cx, cy in ecs:
        pygame.draw.polygon(inked_eyes, WHITE, [
            (cx - 6, cy - 3), (cx - 2, cy - 6), (cx - 2, cy - 1)])
    # Hard 3px ink gutter down the seam so the two domes never fuse into one
    # goggle lump after the downscale — always reads as TWO eyes.
    pygame.draw.line(inked_eyes, INK, (44, 23), (44, 39), 3)
    surf.blit(inked_eyes, (0, 0))

    return surf


build = _make_prebuilt_skin(build_pop_v2)
