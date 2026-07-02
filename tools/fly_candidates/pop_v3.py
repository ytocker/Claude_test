"""POP FLY (Variant 3 — VELVET VENOM), SCRATCH candidate.

A hot-pink-and-purple pop-art housefly: flat magenta/violet colour blocks,
fat comic ink lines on every element, and Ben-Day halftone dot fills. The
read at 40px is carried by the uniform 2px black ink loop on every shape
plus the two enormous dotted goggle eyes — same structural rules as
Design 5, dressed in a venomous velvet palette.

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


# ── VELVET VENOM palette ──────────────────────────────────────────────────────
INK      = (17, 17, 17)             # #111111 comic ink — the 40px carrier
THORAX   = (255, 29, 120)           # #FF1D78 hot pink thorax
ABDOMEN  = (102, 0, 204)            # #6600CC deep purple abdomen
BODY_D   = (255, 0, 170)            # #FF00AA magenta Ben-Day shadow dots
# Warm pale yellow — the complement of the magenta thorax, so the domes POP
# instead of drifting toward the pink mass. Kept as the hero tell.
EYEW     = (255, 243, 155)          # #FFF39B warm pale yellow dome
# Dome halftone lightened toward pink-cream and thinned out: at 40px a dense
# hot-pink grid muddied the yellow, so the domes must stay the brightest mark.
EYE_D    = (255, 198, 208)          # pale pink-cream Ben-Day eye dots
WHITE    = (255, 255, 255)
WINGMEM  = (224, 200, 255)          # #E0C8FF soft lavender wing membrane
WINGDOT  = (255, 0, 170)            # #FF00AA magenta wing halftone
LABELLUM = (204, 0, 170)            # #CC00AA deep magenta sponge mouth pad


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


# ── one smooth membranous fan ─────────────────────────────────────────────────
# Root pivot sits at the left tip; the membrane is a SINGLE convex rounded oval
# so the downscaled outer arc stays clean — no faceted ink spikes — and only
# THEN takes its halftone + ink loop. Reads as a translucent fan, not a
# patterned bowtie.
_WING_ROOT = (8, 16)


def _wing_surface():
    """One rounded pop-art fan: a flat lavender membrane ellipse carrying only
    a clean magenta Ben-Day dot grid, then a 2px ink loop.

    No interior veins/streaks — flat #E0C8FF must dominate and the halftone
    reads as dots-as-dots, so the wing never competes with the hero eyes."""
    w = pygame.Surface((40, 32), pygame.SRCALPHA)
    membrane = pygame.Rect(0, 0, 22, 16)
    membrane.center = (19, 16)
    pygame.draw.ellipse(w, WINGMEM, membrane)
    # Flat lavender under a single clean dot grid — the only mark on the fan.
    emask = pygame.Surface((40, 32), pygame.SRCALPHA)
    pygame.draw.ellipse(emask, (255, 255, 255, 255), membrane)
    _benday(w, emask, WINGDOT, spacing=5, radius=1)
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
def build_pop_v3(wing_angle_deg):
    surf = _new()
    f = (wing_angle_deg + 40) / 90.0        # 1 = wings up, 0 = wings down

    # Comic speed lines streak off the back on the wing-up beats.
    if f > 0.6:
        for k in range(3):
            y = 20 + k * 6
            pygame.draw.line(surf, INK, (5, y + 2), (12, y), 1)
            pygame.draw.line(surf, INK, (12, y), (19, y - 1), 1)

    # One mirrored pair of fans sweep up-and-back off the shoulder — root on the
    # body side, rounded outer arc on the away side. Design-5 geometry (root at
    # left in the surface) so neither outer tip clips the canvas or each other.
    wing = _wing_surface()
    ang = 5 + f * 28
    left = pygame.transform.flip(wing, True, False)
    left_root = (wing.get_width() - 1 - _WING_ROOT[0], _WING_ROOT[1])
    _place_rotated(surf, wing, _WING_ROOT, ang, (31, 31))
    _place_rotated(surf, left, left_root, -ang, (29, 31))

    # ── one round inked barrel: hot-pink thorax fused into purple abdomen ──
    body = _new()
    _aaellipse(body, ABDOMEN, (BCX, 49), 13, 11)
    _aaellipse(body, THORAX, (BCX, 41), 13, 9)
    # Magenta Ben-Day shadow field on the thorax underside gives the dome value.
    tmask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    _aaellipse(tmask, (255, 255, 255, 255), (BCX, 43), 12, 7)
    _benday(body, tmask, BODY_D, spacing=4, radius=1, phase=1)
    # Belly Ben-Day rows read as rounded abdomen banding on the shadow side.
    amask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    _aaellipse(amask, (255, 255, 255, 255), (BCX + 1, 52), 11, 7)
    _benday(body, amask, BODY_D, spacing=5, radius=1, phase=2)
    # A short waist band, not a full stacked-bands divider — the barrel wins.
    pygame.draw.line(body, INK, (BCX - 8, 45), (BCX + 8, 45), 2)
    surf.blit(_ink_outline(body, 2), (0, 0))

    # Small round sponge labellum (mouth pad) tucked centrally right under the
    # eye pair — a compact #CC00AA chin-pad with its own 2px ink ring. Kept
    # small and slit-free so at 40px it reads as a spongy pad below the face,
    # never a second detached coin off to the side.
    lab = _new()
    lr = pygame.Rect(0, 0, 10, 9)
    lr.center = (43, 47)
    pygame.draw.ellipse(lab, LABELLUM, lr)
    surf.blit(_ink_outline(lab, 2), (0, 0))

    # ── HERO: two big dotted goggle eyes that fill the head ──
    # Fills leave a 4px trench that the two 2px ink loops fill from both sides,
    # then an explicit black bar seals it — the domes NEVER fuse into one blob.
    eyes = _new()
    # A tight, level, symmetric pair centred on the face at x=43: left/right
    # domes share one clean 2px ink gutter so they read as PAIRED eyes, not a
    # dome plus a detached coin drifting off the side.
    ecs = ((34, 30), (52, 30))
    for cx, cy in ecs:
        _aaellipse(eyes, EYEW, (cx, cy), 8, 8)
    emask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for cx, cy in ecs:
        _aaellipse(emask, (255, 255, 255, 255), (cx, cy), 8, 8)
    # Sparse, pale pink-cream dots so the warm yellow dome stays dominant.
    _benday(eyes, emask, EYE_D, spacing=6, radius=1)
    inked_eyes = _ink_outline(eyes, 2)
    # Solid closed #111 valley down the shared seam at x=43 — belt-and-braces
    # so the two domes survive the 40px downscale as TWO eyes, never one mass.
    pygame.draw.line(inked_eyes, INK, (43, 23), (43, 37), 2)
    # Solid white comic glint wedge in each dome's upper-left, over the dots.
    for cx, cy in ecs:
        pygame.draw.polygon(inked_eyes, WHITE, [
            (cx - 6, cy - 4), (cx - 1, cy - 6), (cx - 3, cy)])
    surf.blit(inked_eyes, (0, 0))

    # ── bristly thorax hump: crisp 1px setae breaking the top silhouette ──
    # Rooted on the exposed pink crown between the eyes and the back wings, the
    # spikes stand clear off the outline into the sky so they still register as
    # bristles at 40px — the tell that pushes the read from "ladybug" to "fly".
    for (x0, y0), (x1, y1) in (
            ((36, 23), (34, 14)), ((43, 23), (43, 13)), ((50, 23), (52, 14))):
        pygame.draw.line(surf, INK, (x0, y0), (x1, y1), 1)

    return surf


build = _make_prebuilt_skin(build_pop_v3)
