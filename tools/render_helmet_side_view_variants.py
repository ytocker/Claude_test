"""Render 5 side-view SKATEBOARD helmet design variants over a real
in-game scene.

The live ``Bird._draw_helmet`` (game/entities.py:1112) reads as a
top-down/front-view dome — full ellipse, symmetric chinstraps,
front-facing skull. Pip is a side-view sprite facing screen-right,
so the helmet looks wrong on him.

This script renders 5 SIDE-VIEW alternatives. The live
``_draw_helmet`` is NOT touched — we monkey-patch
``world.bird._draw_helmet`` per variant, render a real play frame,
and save to ``docs/screenshots/skateboard_variants/side_view_v2/``.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_helmet_side_view_variants.py
"""

import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y, PIPE_W
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game.world import World
from game.entities import PowerUp, Pipe, Coin


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_variants", "side_view_v2")
os.makedirs(_OUT, exist_ok=True)


# ── shared helpers ──────────────────────────────────────────────────────────

def _new_helm(s):
    """Allocate the same-shape helm surface as the live _draw_helmet."""
    hw = int(24 * s)
    hh = int(15 * s)
    pad = 4
    drop = int(12 * s)
    helm = pygame.Surface(
        (hw + pad * 2, hh + pad * 2 + drop), pygame.SRCALPHA)
    return helm, hw, hh, pad, drop


def _half_dome(helm, hw, hh, pad, fill, highlight=None):
    """Paint the TOP HALF of an ellipse onto helm — flat horizontal
    rim at y=pad+hh. Optional forward-upper highlight."""
    full = pygame.Surface((hw, hh * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(full, fill, pygame.Rect(0, 0, hw, hh * 2))
    helm.blit(full, (pad, pad), area=pygame.Rect(0, 0, hw, hh))
    if highlight is not None and hw > 9 and hh > 5:
        hl = pygame.Surface((hw - 8, hh - 4), pygame.SRCALPHA)
        pygame.draw.ellipse(hl, highlight,
                            pygame.Rect(0, 0, hw - 8, hh - 4))
        # Forward (right) upper quadrant only — Pip faces right.
        helm.blit(hl, (pad + 4, pad + 1),
                  area=pygame.Rect((hw - 8) // 2, 0,
                                   (hw - 8) // 2, (hh - 4) // 2 + 1))


def _chinstrap(helm, hw, hh, pad, drop,
               strap=(60, 60, 70), buckle=(200, 50, 50)):
    """Single diagonal strap from REAR-temple → buckle just in front
    of (and below) the jaw."""
    rear = (pad + 3, pad + hh + 1)
    bk = (pad + hw - 3, pad + hh + drop - 3)
    pygame.draw.line(helm, strap, rear, bk, 2)
    pygame.draw.circle(helm, buckle, bk, 2)


def _anchor_and_blit(bird, surf, helm, cx, cy, flipped):
    """Mirror entities.py:1182-1191 — anchor +15,-11 with tilt
    rotation and reverse-gravity flip."""
    s = bird.shrink_scale
    tilt = -bird.tilt_deg if flipped else bird.tilt_deg
    y_off = 11 * s if flipped else -11 * s
    offset = pygame.math.Vector2(15 * s, y_off).rotate(-tilt)
    rotated = pygame.transform.rotate(helm, tilt)
    if flipped:
        rotated = pygame.transform.flip(rotated, False, True)
    r = rotated.get_rect(center=(int(cx + offset.x),
                                 int(cy + offset.y)))
    surf.blit(rotated, r.topleft)


# ── 5 variant functions ─────────────────────────────────────────────────────

def variant_classic_skater(bird, surf, cx, cy, flipped):
    """Short round half-dome + chrome rim + side skull decal + rear
    neck-skirt. Kit-matched palette."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _half_dome(helm, hw, hh, pad, (10, 10, 18), (50, 50, 60))
    # Front lip (brow) over Pip's sunglasses.
    pygame.draw.polygon(helm, (10, 10, 18), [
        (pad + hw - 3, pad + hh - 3),
        (pad + hw + 1, pad + hh - 1),
        (pad + hw - 1, pad + hh + 1),
    ])
    # Rear neck skirt — back drops below the rim.
    pygame.draw.polygon(helm, (10, 10, 18), [
        (pad - 1, pad + hh - 3),
        (pad - 2, pad + hh + 3),
        (pad + 4, pad + hh + 1),
    ])
    # Side vent — three short vertical slits stacked on the side panel.
    vx = pad + int(hw * 0.42)
    vy = pad + hh // 2 - 1
    for dx in (-2, 0, 2):
        pygame.draw.line(helm, (10, 10, 18),
                         (vx + dx, vy), (vx + dx, vy + 3))
    # Chrome rim band — straight horizontal at the rim line.
    pygame.draw.rect(helm, (200, 200, 210),
                     pygame.Rect(pad - 1, pad + hh - 1, hw + 2, 2))
    # Side skull decal.
    s = bird.shrink_scale
    sk_w = max(4, int(7 * s))
    sk_h = max(3, int(5 * s))
    sk = pygame.Rect(0, 0, sk_w, sk_h)
    sk.center = (pad + hw // 2 - 1, pad + hh - 5)
    pygame.draw.ellipse(helm, (240, 240, 230), sk)
    pygame.draw.ellipse(helm, (10, 10, 18), sk, 1)
    pygame.draw.circle(helm, (10, 10, 18),
                       (sk.centerx - 1, sk.centery), 1)
    pygame.draw.circle(helm, (10, 10, 18),
                       (sk.centerx + 1, sk.centery), 1)
    _chinstrap(helm, hw, hh, pad, drop)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def variant_aero_bike(bird, surf, cx, cy, flipped):
    """Teardrop silhouette with pointed rear spoiler + 3 long
    front-to-back slot vents + cyan accent stripe."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _half_dome(helm, hw, hh, pad, (10, 10, 18))
    # Aero tail — pointed rear extension that drops below the rim.
    pygame.draw.polygon(helm, (10, 10, 18), [
        (pad - 1, pad + hh - 2),
        (pad - 3, pad + hh + 2),
        (pad - 1, pad + hh + 1),
        (pad + 4, pad + hh),
    ])
    # Three slot vents running front-to-back along the centreline.
    for vy in (pad + 3, pad + 6, pad + 9):
        pygame.draw.line(helm, (10, 10, 18),
                         (pad + hw // 2 - 6, vy),
                         (pad + hw // 2 + 4, vy), 1)
    # Forward arc highlight.
    pygame.draw.arc(helm, (90, 90, 110),
                    pygame.Rect(pad + 1, pad + 1, hw - 4, hh * 2 - 4),
                    2.6, 3.4, 1)
    # Chrome rim band — extends back along the aero tail.
    pygame.draw.rect(helm, (200, 200, 210),
                     pygame.Rect(pad - 3, pad + hh - 1, hw + 5, 2))
    # Cyan accent stripe forward of the vents.
    pygame.draw.line(helm, (90, 200, 220),
                     (pad + hw - 7, pad + 4),
                     (pad + hw - 2, pad + 6), 1)
    _chinstrap(helm, hw, hh, pad, drop)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def variant_moto_visor(bird, surf, cx, cy, flipped):
    """Half-dome with forward-projecting smoked-glass brow visor,
    chin-bar hint, and a lightning bolt decal on the side panel."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _half_dome(helm, hw, hh, pad, (20, 20, 30), (60, 60, 75))
    # Brow visor — black rect sticks forward past the front of the head.
    pygame.draw.rect(helm, (10, 10, 18),
                     pygame.Rect(pad + hw - 5, pad + hh - 4, 8, 3))
    # Smoked-glass cyan glint along the bottom edge of the visor.
    pygame.draw.line(helm, (80, 160, 200),
                     (pad + hw - 4, pad + hh - 2),
                     (pad + hw + 2, pad + hh - 2), 1)
    # Side intake vent — D-shaped ellipse.
    pygame.draw.ellipse(helm, (10, 10, 18),
                        pygame.Rect(pad + hw // 2 - 3, pad + hh - 6, 6, 3))
    # Chrome rim band.
    pygame.draw.rect(helm, (200, 200, 210),
                     pygame.Rect(pad - 1, pad + hh - 1, hw + 2, 2))
    # Chin-bar hint — short strut suggesting moto coverage.
    pygame.draw.line(helm, (10, 10, 18),
                     (pad + hw - 3, pad + hh + 1),
                     (pad + hw - 1, pad + hh + drop - 5), 2)
    # Lightning bolt decal on the side panel.
    bx = pad + hw // 2
    by = pad + hh - 6
    pygame.draw.polygon(helm, (230, 210, 80), [
        (bx - 2, by + 1),
        (bx,     by - 3),
        (bx - 1, by - 1),
        (bx + 2, by + 1),
        (bx,     by + 4),
        (bx + 1, by + 1),
    ])
    _chinstrap(helm, hw, hh, pad, drop)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def variant_punk_mohawk_side(bird, surf, cx, cy, flipped):
    """Half-dome with a SINGLE bone fin running front-to-back along
    the top — the correct side-profile mohawk shape."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _half_dome(helm, hw, hh, pad, (10, 10, 18), (50, 50, 60))
    # Side-profile mohawk fin — one long sail running front to back.
    fin = [
        (pad + 3,           pad + 1),
        (pad + hw // 2 - 2, pad - 3),
        (pad + hw // 2 + 3, pad - 2),
        (pad + hw - 4,      pad + 2),
    ]
    pygame.draw.polygon(helm, (240, 240, 230), fin)
    pygame.draw.polygon(helm, (10, 10, 18), fin, 1)
    # Two small spike peaks rising from the crest top.
    for sx in (pad + hw // 2 - 3, pad + hw // 2 + 2):
        pygame.draw.polygon(helm, (240, 240, 230), [
            (sx, pad - 2),
            (sx + 1, pad - 5),
            (sx + 2, pad - 2),
        ])
        pygame.draw.polygon(helm, (10, 10, 18), [
            (sx, pad - 2),
            (sx + 1, pad - 5),
            (sx + 2, pad - 2),
        ], 1)
    # Single side vent.
    pygame.draw.line(helm, (10, 10, 18),
                     (pad + hw // 2 - 2, pad + hh - 3),
                     (pad + hw // 2 + 2, pad + hh - 3), 1)
    # Chrome rim band.
    pygame.draw.rect(helm, (200, 200, 210),
                     pygame.Rect(pad - 1, pad + hh - 1, hw + 2, 2))
    # Small side skull decal near rear.
    s = bird.shrink_scale
    sk_w = max(3, int(5 * s))
    sk_h = max(2, int(4 * s))
    sk = pygame.Rect(0, 0, sk_w, sk_h)
    sk.center = (pad + hw // 2 - 5, pad + hh - 4)
    pygame.draw.ellipse(helm, (240, 240, 230), sk)
    pygame.draw.ellipse(helm, (10, 10, 18), sk, 1)
    _chinstrap(helm, hw, hh, pad, drop)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def variant_wide_brim(bird, surf, cx, cy, flipped):
    """Steel-blue half-dome with a flat FRONT-ONLY brim (cap-visor
    fused into the helmet), cyan rim stripe, side star decal."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _half_dome(helm, hw, hh, pad, (30, 90, 140), (90, 160, 200))
    # Front brim — flat trapezoid extending forward only.
    pygame.draw.polygon(helm, (20, 60, 100), [
        (pad + hw - 3, pad + hh - 2),
        (pad + hw + 5, pad + hh - 1),
        (pad + hw + 5, pad + hh + 1),
        (pad + hw - 3, pad + hh + 1),
    ])
    # Highlight band across the upper dome.
    pygame.draw.line(helm, (140, 200, 230),
                     (pad + 4, pad + 3),
                     (pad + hw - 6, pad + 3), 1)
    # Side vent — short rectangle.
    pygame.draw.rect(helm, (10, 10, 18),
                     pygame.Rect(pad + hw // 2 - 3, pad + hh - 5, 6, 2))
    # Cyan stripe wrapping the rim line.
    pygame.draw.rect(helm, (90, 200, 220),
                     pygame.Rect(pad - 1, pad + hh - 2, hw + 2, 1))
    # 5-point star decal on the side panel.
    sx = pad + hw // 2 - 1
    sy = pad + hh - 6
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = 3 if i % 2 == 0 else 1
        pts.append((sx + math.cos(ang) * r, sy + math.sin(ang) * r))
    pygame.draw.polygon(helm, (240, 240, 230), pts)
    pygame.draw.polygon(helm, (10, 10, 18), pts, 1)
    _chinstrap(helm, hw, hh, pad, drop,
               strap=(20, 30, 50), buckle=(200, 200, 210))
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


VARIANTS = [
    ("classic_skater",   variant_classic_skater,
     "Short round half-dome, chrome rim, side skull, rear neck skirt"),
    ("aero_bike",        variant_aero_bike,
     "Teardrop + pointed aero tail, 3 slot vents, cyan accent"),
    ("moto_visor",       variant_moto_visor,
     "Forward brow visor + chin-bar hint, lightning decal"),
    ("punk_mohawk_side", variant_punk_mohawk_side,
     "Side-profile bone mohawk fin (front-to-back, not symmetric)"),
    ("wide_brim",        variant_wide_brim,
     "Steel-blue + flat front brim, cyan stripe, star decal"),
]


# ── scene backdrop ──────────────────────────────────────────────────────────

def draw_bg(surf, scroll=0, phase=0.62):
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    b = (a + 1) % buckets
    t = bucket_f - int(bucket_f)
    pal_a = _biome.palette_for_phase(a / buckets)
    pal_b = _biome.palette_for_phase(b / buckets)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)
    sky_a.set_alpha(None)
    surf.blit(sky_a, (0, 0))
    if t > 0:
        sky_b.set_alpha(int(t * 255))
        surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)
    for i, (bx, by, sc, variant) in enumerate(
            ((20, 90, 0.9, 0), (180, 140, 1.1, 2),
             (60, 220, 0.8, 3), (230, 60, 0.7, 1),
             (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(1.2 + i) * 3, sc, variant=variant)
    pal = pal_a
    draw_mountains(surf, scroll, GROUND_Y, W,
                   pal['mtn_far'], pal['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                pal['ground_top'], pal['ground_mid'], (60, 40, 25))


def build_world():
    """A representative gameplay frame — Pip mid-flight tilting up
    after a fresh flap, pillars flanking him."""
    random.seed(11)
    world = World()
    world.ready_t = 0
    # Settle backdrop / clouds.
    for _ in range(40):
        world.world_idle_tick(1 / 60)
    # Stage two pillars so the helmet shows against real terrain.
    world.pipes = [
        Pipe(40 - PIPE_W // 2, 220, 130),
        Pipe(280, 360, 130),
    ]
    # Activate skateboard — flips bird.skateboard_active so _draw_helmet
    # fires from Bird.draw.
    world._activate_skateboard(PowerUp(0, 0, kind="skateboard"))
    # Mid-flap pose: rising, slight nose-up tilt.
    world.bird.y = H * 0.42
    world.bird.vy = -180
    # Force the pose so backflip/spin doesn't activate mid-render.
    world.bird.flap_boost = 0.0
    return world


def render_play_scene(world):
    """Real in-game layer order, minus the live skateboard overlay.
    Particles + pickup burst are skipped so the helmet reads clean."""
    surf = pygame.Surface((W, H))
    draw_bg(surf, scroll=world.bg_scroll,
            phase=getattr(world, "biome_phase", 0.62))
    pipe_palette = world.biome_palette
    for p in world.pipes:
        p.draw(surf, pipe_palette, kfc_visual=False)
    world.weather.draw(surf)
    for c in world.coins:
        c.draw(surf, kfc_active=False, triple_active=False)
    for m in world.powerups:
        m.draw(surf)
    world.bird.draw(surf, 0, 0)
    return surf


def render_zoom(world, zoom=6, crop=60):
    """Tight crop on Pip's head + helmet, then upscale `zoom`× so the
    silhouette is legible. `crop` is the pre-zoom region size in
    game pixels."""
    full = render_play_scene(world)
    cx = int(world.bird.x)
    cy = int(world.bird.y) - 10  # bias up — helmet sits above bird centre
    rect = pygame.Rect(cx - crop // 2, cy - crop // 2, crop, crop)
    rect.clamp_ip(full.get_rect())
    crop_surf = full.subsurface(rect).copy()
    out = pygame.transform.scale(crop_surf,
                                 (crop * zoom, crop * zoom))
    # Thin yellow frame so the zoom panel reads as a UI inset.
    pygame.draw.rect(out, (255, 215, 0), out.get_rect(), 2)
    return out


# ── label band ──────────────────────────────────────────────────────────────

def _label_band(width, line1, line2=None, height=56):
    band = pygame.Surface((width, height), pygame.SRCALPHA)
    band.fill((0, 0, 0, 220))
    pygame.draw.line(band, (255, 215, 0), (0, 0), (width, 0), 1)
    f1 = pygame.font.SysFont(None, 26)
    t1 = f1.render(line1, True, (255, 240, 200))
    band.blit(t1, t1.get_rect(midtop=(width // 2, 6)))
    if line2:
        f2 = pygame.font.SysFont(None, 18)
        t2 = f2.render(line2, True, (180, 200, 220))
        band.blit(t2, t2.get_rect(midtop=(width // 2, 32)))
    return band


# ── main ────────────────────────────────────────────────────────────────────

def main():
    saved = []
    for i, (label, fn, caption) in enumerate(VARIANTS, start=1):
        world = build_world()
        # Monkey-patch the helmet draw for this variant only.
        world.bird._draw_helmet = (
            lambda surf, cx, cy, flipped, b=world.bird, _fn=fn:
                _fn(b, surf, cx, cy, flipped)
        )
        # Two outputs per variant — gameplay frame for context AND a
        # zoomed close-up so the helmet silhouette is actually
        # readable. The variant_N_<label>.png is a composite of
        # both (gameplay on the left, zoom inset on the right).
        frame = render_play_scene(world)
        zoom = render_zoom(world, zoom=6, crop=60)
        composite = pygame.Surface((W + zoom.get_width() + 8, H))
        composite.fill((10, 12, 24))
        composite.blit(frame, (0, 0))
        # Centre the zoom panel vertically next to the gameplay frame.
        composite.blit(zoom, (W + 8, (H - zoom.get_height()) // 2))
        path = os.path.join(_OUT, f"variant_{i}_{label}.png")
        pygame.image.save(composite, path)
        # Also save the standalone zoom for finer inspection.
        zoom_path = os.path.join(_OUT, f"variant_{i}_{label}_zoom.png")
        pygame.image.save(zoom, zoom_path)
        saved.append((label, caption, path, composite, zoom))
        print(f"saved {path}")
        print(f"saved {zoom_path}")

    # ── Contact sheet: 5 zoom panels in a row, labelled. ────────────────
    zoom_w, zoom_h = saved[0][4].get_size()
    band_h = 56
    gap = 12
    cols = 5
    sheet_w = cols * zoom_w + (cols - 1) * gap + 24
    sheet_h = zoom_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, caption, _path, _composite, zoom) in enumerate(saved):
        x = 12 + idx * (zoom_w + gap)
        y = 12
        sheet.blit(zoom, (x, y))
        band = _label_band(zoom_w, f"{idx + 1}. {label}", caption,
                           height=band_h)
        sheet.blit(band, (x, y + zoom_h))
    sheet_path = os.path.join(_OUT, "00_contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    # ── Pretty-print raw GitHub URLs. ───────────────────────────────────
    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/skateboard_variants/"
            "side_view_v2")
    print()
    print(f"{base}/00_contact_sheet.png")
    for i, (label, caption, *_rest) in enumerate(saved, start=1):
        print(f"{base}/variant_{i}_{label}.png  -- {caption}")
        print(f"{base}/variant_{i}_{label}_zoom.png")


if __name__ == "__main__":
    main()
