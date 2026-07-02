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
EYEW     = (255, 250, 204)          # #FFFACC pale yellow dome
EYE_D    = (255, 29, 120)           # #FF1D78 pink Ben-Day eye dots
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
_WING_ROOT = (8, 24)


def _wing_surface():
    """One rounded pop-art fan: a single smooth lavender membrane ellipse, a
    magenta halftone, two bold black veins, then a 2px ink loop."""
    w = pygame.Surface((52, 48), pygame.SRCALPHA)
    membrane = pygame.Rect(0, 0, 36, 26)
    membrane.center = (26, 24)
    pygame.draw.ellipse(w, WINGMEM, membrane)
    # Sparse magenta halftone reads as translucent venom-tinted membrane
    # without muddying into solid pink at truth scale.
    emask = pygame.Surface((52, 48), pygame.SRCALPHA)
    pygame.draw.ellipse(emask, (255, 255, 255, 255), membrane)
    _benday(w, emask, WINGDOT, spacing=5, radius=1)
    # Two bold veins radiate from the root — the only ink inside the fan.
    pygame.draw.line(w, INK, _WING_ROOT, (40, 16), 2)
    pygame.draw.line(w, INK, _WING_ROOT, (40, 32), 2)
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

    # Two smooth fans sweep up-and-back off a shoulder anchor near (28,31);
    # the fan opens on the wing-up frames so tips ride from low-wide to a
    # raised spread — never a tall narrow "rabbit-ear" V.
    wing = _wing_surface()
    ang = 3 + f * 30
    left = pygame.transform.flip(wing, True, False)
    left_root = (wing.get_width() - 1 - _WING_ROOT[0], _WING_ROOT[1])
    _place_rotated(surf, wing, _WING_ROOT, ang, (29, 31))
    _place_rotated(surf, left, left_root, -ang, (27, 31))

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

    # Round sponge labellum (mouth pad) below the face, its own 2px ink loop.
    lab = _new()
    lr = pygame.Rect(0, 0, 12, 12)
    lr.center = (44, 47)
    pygame.draw.ellipse(lab, LABELLUM, lr)
    surf.blit(_ink_outline(lab, 2), (0, 0))

    # ── HERO: two big dotted goggle eyes that fill the head ──
    # Centres sit a true 2px apart so the silhouettes never fuse; the ink
    # loops meet in the gap to hold a solid vertical gutter → always TWO eyes.
    eyes = _new()
    ecs = ((35, 30), (53, 30))
    for cx, cy in ecs:
        _aaellipse(eyes, EYEW, (cx, cy), 8, 8)
    emask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for cx, cy in ecs:
        _aaellipse(emask, (255, 255, 255, 255), (cx, cy), 8, 8)
    _benday(eyes, emask, EYE_D, spacing=3, radius=1)
    inked_eyes = _ink_outline(eyes, 2)
    # Solid white comic glint wedge in each dome's upper-left, over the dots.
    for cx, cy in ecs:
        pygame.draw.polygon(inked_eyes, WHITE, [
            (cx - 6, cy - 4), (cx - 1, cy - 6), (cx - 3, cy)])
    # Belt-and-braces 2px ink gutter down the seam so the domes never read as
    # one goggle even after the downscale.
    pygame.draw.line(inked_eyes, INK, (44, 22), (44, 38), 2)
    surf.blit(inked_eyes, (0, 0))

    # ── bristly thorax hump: chunky black setae angled up-back ──
    # Notch-breaks over the pink dome's top push the body from "ladybug" to
    # "fly"; drawn last so they read on top of the shoulder, tips clear-left.
    for (x0, y0), (x1, y1) in (
            ((28, 34), (23, 28)), ((25, 35), (20, 30)), ((31, 33), (26, 27))):
        pygame.draw.line(surf, INK, (x0, y0), (x1, y1), 2)

    return surf


build = _make_prebuilt_skin(build_pop_v3)
