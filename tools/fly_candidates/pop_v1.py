"""POP FLY (pop_v1) — ELECTRIC ZAPPER, SCRATCH candidate.

A high-voltage pop-art housefly: electric-blue thorax fused into a neon-lime
abdomen, cyan halftone wings and two dotted goggle eyes. Same Lichtenstein
grammar as Design 5 — flat colour blocks, uniform 2px black ink loop on every
element, hex-packed Ben-Day dot fills — but tuned to a cold blue/lime charge
instead of the warm red/yellow original.

R3 rework (all four C2 tells): wings rebuilt as SHORT, WIDE, horizontal
paddle-fans that sweep up-and-BACK over the barrel (never the tall vertical
rabbit-ear V); a distinct deep-blue labellum lobe re-seated directly under the
eye pair with its own ink ring; thorax and abdomen fused into one continuous
peanut silhouette (no detached lime droplet); and 2–3 bold 3px setae planted on
the thorax shoulder in ALL four flap frames.

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


# ── ELECTRIC ZAPPER palette ──────────────────────────────────────────────────
INK       = (17, 17, 17)            # #111111 comic ink — the 40px carrier
THORAX    = (0, 87, 255)            # #0057FF electric-blue thorax
ABDOMEN   = (170, 255, 0)           # #AAFF00 neon-lime abdomen
BODY_DOT  = (255, 229, 0)           # #FFE500 yellow Ben-Day shadow dots
BLUE      = (0, 87, 255)            # #0057FF Ben-Day eye dots
EYEW      = (200, 240, 255)         # #C8F0FF cool-white dome
WHITE     = (255, 255, 255)
WINGMEM   = (200, 240, 255)         # #C8F0FF light-cyan wing membrane
WINGDOT   = (170, 255, 0)           # #AAFF00 lime halftone on the fan
LABELLUM  = (0, 68, 204)            # #0044CC deep-blue sponge mouth pad


def _ink_outline(layer, thickness=2, color=INK):
    """Grow a uniform closed black comic outline around a layer's silhouette.

    The heavy 2px loop is the stated 40px carrier — applied per element so
    every block reads as its own inked shape after the downscale."""
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


def _benday(target, region_pts_or_mask, color, spacing=9, radius=2, phase=0):
    """Overlay a regular Ben-Day halftone dot grid clipped to a region.

    Odd rows are half-offset so the grid reads as a hex-packed halftone,
    not a plain lattice. Spacing≥9 / radius 2 keeps the dots readable as
    dots after the shrink instead of dissolving into fuzz. `region` is
    polygon points or a white mask surface."""
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


# ── one short WIDE horizontal paddle-fan ──────────────────────────────────────
# Root on the LEFT (hinge side, closest to body centre); the outer arc sweeps
# to the RIGHT — same geometry as the Design 5 reference so the full rounded
# tip is never clipped at the canvas edge or within the surface padding.
_WING_ROOT = (8, 16)                 # hinge — left edge, canvas-safe pivot


def _wing_surface():
    """Short wide cyan paddle: root on left, 22×16 horizontal ellipse (wider
    than tall) carries the lime dot grid and two veins, then a 2px ink loop.
    Surface padded ≥ 8px on every side so the ink outline is never clipped."""
    w = pygame.Surface((40, 32), pygame.SRCALPHA)
    membrane = pygame.Rect(0, 0, 22, 16)
    membrane.center = (19, 16)
    pygame.draw.ellipse(w, WINGMEM, membrane)
    emask = pygame.Surface((40, 32), pygame.SRCALPHA)
    pygame.draw.ellipse(emask, (255, 255, 255, 255), membrane)
    _benday(w, emask, WINGDOT, spacing=9, radius=2)
    pygame.draw.line(w, INK, _WING_ROOT, (28, 10), 2)
    pygame.draw.line(w, INK, _WING_ROOT, (28, 22), 2)
    return _ink_outline(w, 2)


def _place_rotated(dst, layer, pivot_local, angle_deg, pivot_dst):
    """Rotate `layer` by `angle_deg` (CCW) and blit it so `pivot_local` lands
    exactly on `pivot_dst` — lets the paddle swing about its hinge, not its box."""
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
def build_pop_v1(wing_angle_deg):
    surf = _new()
    f = (wing_angle_deg + 40) / 90.0        # 1 = fully swept up-back, 0 = level

    # Pure-black speed swooshes streak off the back on the wing-up beats — the
    # electric-charge motion pop. Kept low so the wide wings own the top.
    if f > 0.6:
        for k in range(3):
            y = 30 + k * 5
            pygame.draw.line(surf, INK, (4, y + 2), (11, y), 1)
            pygame.draw.line(surf, INK, (11, y), (18, y - 1), 1)

    # Two broad fans sweep up-and-back off the shoulder — root on the body side,
    # outer rounded arc extending away from centre. Mirrored pair (one per side)
    # using the same root-on-left geometry as the Design 5 reference so neither
    # outer arc clips the canvas edge or the body centre.
    wing = _wing_surface()
    ang = 3 + f * 30
    left = pygame.transform.flip(wing, True, False)
    left_root = (wing.get_width() - 1 - _WING_ROOT[0], _WING_ROOT[1])
    _place_rotated(surf, wing, _WING_ROOT, ang, (31, 31))
    _place_rotated(surf, left, left_root, -ang, (29, 31))

    # ── one continuous inked barrel: blue thorax fused into lime abdomen ──
    # Thorax and abdomen overlap heavily and share close radii so the outline
    # closes as ONE rounded peanut — no lime teardrop dangling below the blue.
    body = _new()
    _aaellipse(body, ABDOMEN, (BCX, 50), 12, 11)
    _aaellipse(body, THORAX, (BCX, 41), 12, 10)
    # Yellow Ben-Day shadow field low on the lime dome gives it value without
    # going muddy; kept sparse so it never fights the silhouette.
    amask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    _aaellipse(amask, (255, 255, 255, 255), (BCX + 1, 53), 10, 6)
    _benday(body, amask, BODY_DOT, spacing=6, radius=1, phase=2)
    # One short crisp waist tick where blue meets lime — a single divider inside
    # the barrel, not a stacked ladder that would split the peanut in two.
    pygame.draw.line(body, INK, (BCX - 7, 46), (BCX + 7, 46), 2)
    surf.blit(_ink_outline(body, 2), (0, 0))

    # Distinct spongy labellum: its own round deep-blue lobe seated directly
    # UNDER the eye pair at ~(44,47), carrying a full 2px ink ring so it reads
    # as a separate mouth pad — tell #4 — never a chin fused to the thorax.
    lab = _new()
    lr = pygame.Rect(0, 0, 13, 10)
    lr.center = (44, 47)
    pygame.draw.ellipse(lab, LABELLUM, lr)
    surf.blit(_ink_outline(lab, 2), (0, 0))

    # ── HERO: two big dotted goggle eyes split by a hard ink gutter ──
    # r7 domes pulled apart with a true gap; a solid 2px ink line drives down
    # the centreline so they always read as TWO separate domes at 40px. The
    # brightest element on the fly.
    eyes = _new()
    ecs = ((34, 30), (52, 30))
    for cx, cy in ecs:
        _aaellipse(eyes, EYEW, (cx, cy), 7, 7)
    emask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for cx, cy in ecs:
        _aaellipse(emask, (255, 255, 255, 255), (cx, cy), 7, 7)
    _benday(eyes, emask, BLUE, spacing=6, radius=2)
    inked_eyes = _ink_outline(eyes, 2)
    # One crisp white glint wedge in each dome's upper-left, over the dots.
    for cx, cy in ecs:
        pygame.draw.polygon(inked_eyes, WHITE, [
            (cx - 5, cy - 3), (cx - 1, cy - 5), (cx - 2, cy)])
    # Hard 2px ink gutter down the seam between the domes.
    pygame.draw.line(inked_eyes, INK, (43, 22), (43, 38), 2)
    surf.blit(inked_eyes, (0, 0))

    # ── bristly thorax hump: bold black setae on the shoulder, ALL 4 frames ──
    # Drawn LAST at 3px over the light cyan wing/shoulder so they stay high
    # contrast and never merge into the wing ink — tell #5 holds through the
    # whole flap cycle, not just frame 1.
    for (x0, y0), (x1, y1) in (
            ((30, 33), (24, 24)), ((27, 34), (20, 26)), ((33, 32), (28, 22))):
        pygame.draw.line(surf, INK, (x0, y0), (x1, y1), 3)

    return surf


build = _make_prebuilt_skin(build_pop_v1)
