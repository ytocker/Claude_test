import os, sys, math, random
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
import game.foreground as foreground
from game.foreground_floor import (
    _mix, _shade, _sat, _luma, _clamp, _nightf, _scatter, _flat_slab)
from game.scenes import App

W, H, GROUND_Y = 360, 640, 595


def _poly(rng, cx, cy, hw, hh, n):
    """Irregular convex-ish boulder outline: n vertices marched around the
    bounding ellipse with per-vertex radial jitter, so each shed block reads as
    its own weathered lump rather than a stamped oval."""
    pts = []
    for i in range(n):
        a = (i / n) * math.tau - math.pi * 0.5
        jr = rng.uniform(0.74, 1.0)
        pts.append((cx + math.cos(a) * hw * jr,
                    cy + math.sin(a) * hh * jr))
    return pts


def _night_fill(c, night):
    return _mix(c, (34, 42, 62), 0.72 * night)


def draw_scree(surf, scroll, pal, phase):
    night = _nightf(pal)
    sandstone = _mix(pal.get('stone_dark', (95, 70, 55)), (206, 170, 124), 0.62)
    # Bone-lifted body so the value family stays warm-sandstone, not muddy clay.
    sandstone = _mix(sandstone, (232, 214, 182), 0.16)

    # (a) Opaque value-fall base slab — the clean paving plane the apron sits on.
    back = _shade(_sat(sandstone, 0.88), -22)
    front = _shade(_sat(sandstone, 1.05), 4)
    if _luma(front) * 255.0 > 222:
        front = _mix(front, _shade(sandstone, -8), 0.5)
    back = _mix(back, _shade((34, 42, 62), -8), 0.78 * night)
    front = _mix(front, (34, 42, 62), 0.72 * night)
    _flat_slab(surf, W, H, GROUND_Y, back, front, ease=0.95)

    stone_mid = _mix(pal.get('stone_mid', (150, 118, 88)), (206, 170, 124), 0.5)
    stone_dark = pal.get('stone_dark', (95, 70, 55))

    def boulder(sx, rng, w, hh, cy):
        """One shed block: irregular polygon body with a lit upper-left facet and
        a shadowed lower-right facet, plus a hugging 1px contact shadow. Its crown
        pokes above y=595 so the block bites into the mountain-base silhouette and
        dissolves the hard floor seam."""
        cx = sx + w * 0.5
        fill = _mix(stone_mid, stone_dark, rng.uniform(0.2, 0.6))
        fill = _night_fill(fill, night)
        # Lit upper-left facet, capped under the day white-pool ceiling; at night
        # it sheds warmth toward the plain shaded body so it stops glowing.
        lit = _shade(fill, rng.randint(14, 22))
        if _luma(lit) * 255.0 > 222:
            lit = _mix(lit, _shade(fill, -6), 0.5)
        lit = _mix(lit, _shade(fill, -10), night)
        shadow = _shade(fill, -18)

        body = _poly(rng, cx, cy, w * 0.5, hh * 0.5, rng.randint(5, 7))

        # Contact shadow hugging the underside — sits just below the block foot.
        cs = pygame.Surface((W, H), pygame.SRCALPHA)
        cscol = _shade(back, -16 - int(6 * night))
        foot = max(body, key=lambda p: p[1])[1]
        pygame.draw.line(cs, (*cscol, 90),
                         (cx - w * 0.42, foot), (cx + w * 0.42, foot + 1), 1)
        surf.blit(cs, (0, 0))

        pygame.draw.polygon(surf, fill, body)
        # Facet split: upper-left verts get the lit tone, lower-right the shadow,
        # as a soft interior triangle so the block reads round, not flat.
        ul = [p for p in body if p[0] <= cx and p[1] <= cy]
        lr = [p for p in body if p[0] >= cx and p[1] >= cy]
        if len(ul) >= 2:
            pygame.draw.polygon(surf, lit, [(cx, cy)] + sorted(ul, key=lambda p: p[1]))
        if len(lr) >= 2:
            pygame.draw.polygon(surf, shadow, [(cx, cy)] + sorted(lr, key=lambda p: p[1]))
        # Restate the crisp body outline so the interior facets stay contained.
        pygame.draw.polygon(surf, _shade(fill, -8), body, 1)

    # (b) Large boulders — sparse, ~1 per 64px cell, crowns poking above y=595.
    for sx, k, rng in _scatter(scroll, W, 1.0, 64, 0xA21):
        w = rng.randint(20, 34)
        hh = rng.randint(14, 22)
        crown = rng.randint(3, 8)          # how far the top pokes above y=595
        cy = GROUND_Y - crown + hh * 0.5
        boulder(sx, rng, w, hh, cy)

    # (c) Medium cobbles — sparser mid course, no seam overlap.
    for sx, k, rng in _scatter(scroll, W, 1.0, 96, 0xB33):
        if rng.random() < 0.40:
            continue
        w = rng.randint(10, 16)
        hh = rng.randint(7, 11)
        cy = rng.uniform(612, 628)
        boulder(sx, rng, w, hh, cy)


foreground.draw_foreground_floor = draw_scree

OUT = "/home/user/skybit/docs/ground-redesign/foothill-scree-apron/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
app = App()
app._start_play()
app._render()
pygame.image.save(app.screen, OUT)
print(f"Saved: {OUT}")
