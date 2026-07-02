"""POP FLY — GOLDEN ROYALE (Variant 4), SCRATCH candidate.

A heraldic take on the pop-art housefly: deep navy thorax fused into a
rich gold abdomen, cream goggle eyes with a navy Ben-Day dot fill, and
pale sky-blue wings dotted in gold. The premium read is carried by the
navy/gold contrast plus the uniform 2px black ink loop on every element,
so the two dotted eyes and the two-tone barrel survive the 40px downscale.

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


# ── GOLDEN ROYALE palette ─────────────────────────────────────────────────────
INK       = (17, 17, 17)            # #111111 comic ink — the 40px carrier
THORAX    = (0, 31, 107)            # #001F6B deep navy thorax
ABDOMEN   = (212, 168, 0)           # #D4A800 rich gold abdomen
ABDOMEN_D = (240, 200, 0)           # #F0C800 amber Ben-Day shadow dots
NAVY      = (0, 31, 107)            # #001F6B Ben-Day eye dots
EYEW      = (255, 250, 224)         # #FFFAE0 cream dome
WHITE     = (255, 255, 255)
# Saturated cornflower membrane — a paler wash greyed out at 40px and lost the
# blue wing identity, so this reads as an unmistakable sky-blue instead.
WINGBLUE  = (91, 163, 232)          # #5BA3E8 saturated sky-blue membrane
WINGDOT   = (212, 168, 0)           # #D4A800 gold halftone dots
LABELLUM  = (155, 122, 0)           # #9B7A00 dark-gold sponge pad


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
    """One rounded pop-art fan: a single smooth sky-blue membrane ellipse, a
    chunky gold halftone, two bold black veins, then a clean 2px ink loop.

    The membrane is drawn once as a plain convex ellipse and only THEN inked,
    so the outer arc grows into a smooth crisp loop — no faceted spikes."""
    w = pygame.Surface((52, 48), pygame.SRCALPHA)
    membrane = pygame.Rect(0, 0, 40, 28)
    membrane.center = (26, 24)
    pygame.draw.ellipse(w, WINGBLUE, membrane)
    # A few big chunky gold dots read as true Ben-Day at 40px; the old fine
    # grid dissolved into speckle, so this uses wide spacing + fat radius for
    # roughly three-to-four unmistakable dots per wing at truth scale.
    emask = pygame.Surface((52, 48), pygame.SRCALPHA)
    pygame.draw.ellipse(emask, (255, 255, 255, 255), membrane)
    _benday(w, emask, WINGDOT, spacing=9, radius=2, phase=3)
    # Two bold veins radiate from the root — the only ink inside the fan.
    pygame.draw.line(w, INK, _WING_ROOT, (42, 16), 2)
    pygame.draw.line(w, INK, _WING_ROOT, (42, 33), 2)
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
def build_pop_v4(wing_angle_deg):
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
    _place_rotated(surf, wing, _WING_ROOT, ang, (30, 31))
    _place_rotated(surf, left, left_root, -ang, (26, 31))

    # ── one FAT inked peanut: navy thorax fused into gold abdomen ──
    # Both lobes are ~15% wider/rounder than R1 and overlap deeply so the
    # silhouette reads as one heavy barrel with real mass against the head —
    # not two thin stacked bands.
    body = _new()
    _aaellipse(body, ABDOMEN, (BCX, 52), 15, 14)
    _aaellipse(body, THORAX, (BCX, 40), 15, 12)
    # Amber Ben-Day shadow field on the gold abdomen underside gives it dome
    # value; the navy thorax stays flat so the two-tone contrast reads clean.
    amask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    _aaellipse(amask, (255, 255, 255, 255), (BCX + 1, 55), 12, 8)
    _benday(body, amask, ABDOMEN_D, spacing=4, radius=1, phase=2)
    # A short waist band, not a full stacked-bands divider — the barrel wins.
    pygame.draw.line(body, INK, (BCX - 9, 46), (BCX + 9, 46), 2)
    surf.blit(_ink_outline(body, 2), (0, 0))

    # ── HERO: two big dotted goggle eyes seated LOW on the navy thorax ──
    # Centres sit a true 2px apart so the silhouettes never fuse; dropping them
    # onto the navy lobe is what fires the intended cream-against-navy pop that
    # never landed when the domes floated over the wings/background.
    eyes = _new()
    ecs = ((35, 33), (53, 33))
    for cx, cy in ecs:
        _aaellipse(eyes, EYEW, (cx, cy), 8, 8)
    emask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for cx, cy in ecs:
        _aaellipse(emask, (255, 255, 255, 255), (cx, cy), 8, 8)
    _benday(eyes, emask, NAVY, spacing=3, radius=1)
    inked_eyes = _ink_outline(eyes, 2)
    # Solid white comic glint wedge in each dome's upper-left, over the dots.
    for cx, cy in ecs:
        pygame.draw.polygon(inked_eyes, WHITE, [
            (cx - 6, cy - 4), (cx - 1, cy - 6), (cx - 3, cy)])
    # Belt-and-braces 2px ink gutter down the seam so the domes never read as
    # one goggle even after the downscale.
    pygame.draw.line(inked_eyes, INK, (44, 25), (44, 41), 2)
    surf.blit(inked_eyes, (0, 0))

    # Round sponge labellum (mouth pad) directly below the seated eyes — its
    # own 2px ink loop keeps the dark-gold pad legible against the abdomen.
    lab = _new()
    lr = pygame.Rect(0, 0, 12, 12)
    lr.center = (44, 48)
    pygame.draw.ellipse(lab, LABELLUM, lr)
    surf.blit(_ink_outline(lab, 2), (0, 0))

    # ── bristly thorax hump: chunky black setae angled up-back ──
    # Notch-breaks flicking off the navy shoulder push the body from "ladybug"
    # to "fly"; drawn last so they read on top of the hump and break the clean
    # barrel silhouette on the upper-left.
    for (x0, y0), (x1, y1) in (
            ((27, 35), (21, 28)), ((24, 37), (18, 31)), ((30, 34), (25, 26))):
        pygame.draw.line(surf, INK, (x0, y0), (x1, y1), 2)

    return surf


build = _make_prebuilt_skin(build_pop_v4)
