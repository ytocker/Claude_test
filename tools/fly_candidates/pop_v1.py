"""POP FLY (pop_v1) — ELECTRIC ZAPPER, SCRATCH candidate.

A high-voltage pop-art housefly: electric-blue thorax fused into a neon-lime
abdomen, cyan halftone wings and two dotted goggle eyes. Same Lichtenstein
grammar as Design 5 — flat colour blocks, uniform 2px black ink loop on every
element, hex-packed Ben-Day dot fills — but tuned to a cold blue/lime charge
instead of the warm red/yellow original.

R2 rework: eyes split by a solid ink gutter into two unmistakable domes; wings
rebuilt as short, wide convex paddle-fans that visibly sweep through an arc;
the deep-blue labellum re-seated as a squat sponge pad clearly below the face;
one clean thorax/abdomen seam with bold setae breaking the hump silhouette.

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
EYEW      = (232, 244, 255)         # #E8F4FF cool-white dome
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


# ── one short wide convex paddle-fan ─────────────────────────────────────────
# A single broad ellipse — clearly WIDER than tall — hinged at its inner end so
# the whole paddle swings about one pivot. No tapered blade, no faceted tip: the
# outer arc stays a smooth convex sweep after the downscale. Lime dots are big
# and sparse so a few survive at truth scale; the two short veins live only near
# the hinge so they never spike the silhouette.
_WING_ROOT = (7, 22)                 # inner hinge end of the paddle


def _wing_surface():
    """One rounded pop-art paddle-fan: a broad cyan membrane ellipse, a chunky
    lime halftone, two short hinge veins, then a 2px ink loop."""
    w = pygame.Surface((54, 44), pygame.SRCALPHA)
    membrane = pygame.Rect(0, 0, 42, 22)     # wide-and-short → paddle, not blade
    membrane.center = (28, 22)
    pygame.draw.ellipse(w, WINGMEM, membrane)
    # Fewer, larger lime dots ride the fan so the pop accent survives shrink
    # instead of dissolving into cyan fuzz.
    emask = pygame.Surface((54, 44), pygame.SRCALPHA)
    pygame.draw.ellipse(emask, (255, 255, 255, 255), membrane)
    _benday(w, emask, WINGDOT, spacing=7, radius=2)
    # Two short veins fan off the hinge only — the outer half stays a clean arc.
    pygame.draw.line(w, INK, _WING_ROOT, (22, 15), 2)
    pygame.draw.line(w, INK, _WING_ROOT, (22, 29), 2)
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
    f = (wing_angle_deg + 40) / 90.0        # 1 = wings up-back, 0 = wings up-fwd

    # Pure-black speed swooshes streak off the back on the wing-up beats — the
    # electric-charge motion pop.
    if f > 0.6:
        for k in range(3):
            y = 20 + k * 6
            pygame.draw.line(surf, INK, (5, y + 2), (12, y), 1)
            pygame.draw.line(surf, INK, (12, y), (19, y - 1), 1)

    # Two broad paddle-fans hinge at one shoulder anchor and SWEEP through a
    # ~44° arc across the four frames: up-forward on the down-beat, raked
    # up-and-back on the up-beat. The paddle keeps its area — it rotates, it
    # never collapses to a line — so the motion always reads.
    wing = _wing_surface()
    ang = 18 + f * 44
    left = pygame.transform.flip(wing, True, False)
    left_root = (wing.get_width() - 1 - _WING_ROOT[0], _WING_ROOT[1])
    _place_rotated(surf, wing, _WING_ROOT, ang, (30, 30))
    _place_rotated(surf, left, left_root, -ang, (28, 30))

    # ── one round inked barrel: blue thorax fused into lime abdomen ──
    body = _new()
    _aaellipse(body, ABDOMEN, (BCX, 49), 13, 11)
    _aaellipse(body, THORAX, (BCX, 41), 13, 9)
    # Yellow Ben-Day shadow field on the abdomen's lower/shadow side gives the
    # lime dome its value without going muddy.
    amask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    _aaellipse(amask, (255, 255, 255, 255), (BCX + 1, 52), 11, 7)
    _benday(body, amask, BODY_DOT, spacing=4, radius=1, phase=2)
    # One clean 2px ink edge at the waist where blue meets lime — a single
    # crisp divider, not a stacked-bands ladder, so the barrel silhouette wins.
    pygame.draw.line(body, INK, (BCX - 9, 46), (BCX + 9, 46), 2)
    surf.blit(_ink_outline(body, 2), (0, 0))

    # Squat round sponge labellum, seated CLEARLY below the face with its own
    # full 2px ink loop so it reads as a mouth pad, never a chin fused to the
    # thorax.
    lab = _new()
    lr = pygame.Rect(0, 0, 14, 10)
    lr.center = (46, 44)
    pygame.draw.ellipse(lab, LABELLUM, lr)
    surf.blit(_ink_outline(lab, 2), (0, 0))

    # ── HERO: two big dotted goggle eyes split by a hard ink gutter ──
    # Domes shrunk to r7 and pulled apart so a true gap sits between them; a
    # solid 2px ink line then drives down the centreline. Two crisp separate
    # domes at 40px, never one fused goggle.
    eyes = _new()
    ecs = ((34, 30), (52, 30))
    for cx, cy in ecs:
        _aaellipse(eyes, EYEW, (cx, cy), 7, 7)
    emask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for cx, cy in ecs:
        _aaellipse(emask, (255, 255, 255, 255), (cx, cy), 7, 7)
    _benday(eyes, emask, BLUE, spacing=4, radius=1)
    inked_eyes = _ink_outline(eyes, 2)
    # One crisp white glint wedge in each dome's upper-left, over the dots.
    for cx, cy in ecs:
        pygame.draw.polygon(inked_eyes, WHITE, [
            (cx - 5, cy - 3), (cx - 1, cy - 5), (cx - 2, cy)])
    # Hard 2px ink gutter down the seam between the domes — the guarantee that
    # they read as TWO eyes after the downscale.
    pygame.draw.line(inked_eyes, INK, (43, 22), (43, 38), 2)
    surf.blit(inked_eyes, (0, 0))

    # ── bristly thorax hump: chunky black setae breaking the top silhouette ──
    # Tall enough to notch the top of the blue hump — pushes the read from
    # "beetle" to "fly"; drawn last so they sit on top of the shoulder.
    for (x0, y0), (x1, y1) in (
            ((26, 34), (22, 25)), ((30, 33), (28, 24)), ((22, 35), (17, 27))):
        pygame.draw.line(surf, INK, (x0, y0), (x1, y1), 2)

    return surf


build = _make_prebuilt_skin(build_pop_v1)
