import os, sys, math, random
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
import game.foreground as foreground_mod
from game.foreground_floor import (
    _mix, _shade, _sat, _luma, _clamp, _nightf, _scatter, _flat_slab,
    _apply_grain_scroll)
from game.scenes import App

W, H, GROUND_Y = 360, 640, 595
APRON_H = 12                       # y=595..606: the graded cool->warm transition band


def _poly(rng, cx, cy, hw, hh, n):
    """Irregular convex-ish talus outline — n verts marched round the bounding
    ellipse with radial jitter so each shed block reads as its own weathered lump."""
    pts = []
    for i in range(n):
        a = (i / n) * math.tau - math.pi * 0.5
        jr = rng.uniform(0.74, 1.0)
        pts.append((cx + math.cos(a) * hw * jr, cy + math.sin(a) * hh * jr))
    return pts


def _is_foliage(c):
    # Base-of-mountain bushes are the only saturated-green pixels along the seam;
    # skip them so the apron top samples STONE, not a stray leaf.
    r, g, b = c[0], c[1], c[2]
    return g > r + 14 and g > b + 14


def draw_scree(surf, scroll, pal, phase):
    night = _nightf(pal)

    # Warm sand in the mountain colour family: a low-chroma tan pulled off the
    # sandstone keys, kept desaturated so it stays kin to the cool grey mountain.
    sand_warm = _sat(_mix(pal.get('stone_light', (225, 195, 155)),
                          (198, 170, 134), 0.42), 0.9)
    sand_deep = _shade(_sat(sand_warm, 0.9), -26)
    ndk = (34, 42, 62)
    sand_warm_n = _mix(sand_warm, ndk, 0.72 * night)
    sand_deep_n = _mix(sand_deep, _shade(ndk, -8), 0.78 * night)

    # (a) Opaque sand plane under everything — value falls near->far.
    _flat_slab(surf, W, H, GROUND_Y, sand_deep_n, sand_warm_n, ease=0.95)

    # (b) Per-column graded apron y=595..606. Its TOP row is the real mountain-foot
    # pixel sampled one row up, so there is no hard seam in ANY column — boulder or
    # not — and it ramps continuously to the warm sand over 12px. Sampling the live
    # render also carries the biome/night tint for free.
    mcols = []
    acc, n_acc = [0, 0, 0], 0
    for x in range(W):
        c = surf.get_at((x, GROUND_Y - 2))[:3]
        if not _is_foliage(c):
            for i in range(3):
                acc[i] += c[i]
            n_acc += 1
        mcols.append(c)
    # Neutral fallback for foliage columns: the mean stone tone of the seam.
    fb = tuple(acc[i] // max(1, n_acc) for i in range(3)) if n_acc else (200, 210, 205)
    apron = pygame.Surface((W, APRON_H))
    for x in range(W):
        top = mcols[x] if not _is_foliage(mcols[x]) else fb
        for i in range(APRON_H):
            # Smoothstep so the mountain-cool crown eases into the warm sand with
            # no visible banding step at either the top seam or the sand handoff.
            t = i / (APRON_H - 1)
            t = t * t * (3.0 - 2.0 * t)
            apron.set_at((x, i), _mix(top, sand_warm_n, t))
    surf.blit(apron, (0, GROUND_Y))
    # Scroll-locked grain on the sand below the apron so the tooth tracks the dunes.
    _apply_grain_scroll(surf, 0, GROUND_Y + APRON_H, W, H - (GROUND_Y + APRON_H),
                        3, scroll, 1.0)

    # Boulder palette: cool grey-tan mountain family (NOT warm brown), warmed a
    # touch toward the sand at the foot so blocks feel bedded in the apron.
    b_top = _mix((185, 180, 165), ndk, 0.7 * night)
    b_bot = _mix((175, 155, 130), ndk, 0.72 * night)

    def boulder(sx, rng, w, hh, cy):
        """One talus block: irregular body with a lit upper crown and a shadowed
        body (2-tone volume), plus a 1px dark contact shadow at its lowest row. Its
        crown pokes above y=595 so it physically bites the flat mountain seam."""
        cx = sx + w * 0.5
        # Vertical warm-shift: crown sits in the cool grey family, foot warms toward
        # the sand it rests on.
        warm_t = _clamp((cy - GROUND_Y) / 40.0) if isinstance(cy, (int, float)) else 0
        warm_t = max(0.0, min(1.0, (cy - GROUND_Y) / 40.0))
        base = _mix(b_top, b_bot, 0.35 + 0.5 * warm_t + rng.uniform(-0.12, 0.12))
        lit = _shade(base, 18)
        if _luma(lit) * 255.0 > 224:        # never pool toward white in daylight
            lit = _mix(lit, _shade(base, -6), 0.5)
        lit = _mix(lit, _shade(base, -10), night)   # crown stops glowing at night
        shadow = _shade(base, -10)

        body = _poly(rng, cx, cy, w * 0.5, hh * 0.5, rng.randint(5, 7))
        foot = max(body, key=lambda p: p[1])[1]

        # 1px dark contact shadow hugging the block's lowest row — beds it down.
        cs = pygame.Surface((W, H), pygame.SRCALPHA)
        cscol = _shade(sand_deep_n, -22 - int(6 * night))
        pygame.draw.line(cs, (*cscol, 120),
                         (cx - w * 0.44, foot), (cx + w * 0.44, foot + 1), 1)
        surf.blit(cs, (0, 0))

        pygame.draw.polygon(surf, base, body)
        # Lit crown = upper verts; shadow body = lower verts, split at the centre so
        # the block reads round rather than a flat stamp.
        up = [p for p in body if p[1] <= cy]
        dn = [p for p in body if p[1] >= cy]
        if len(up) >= 2:
            pygame.draw.polygon(surf, lit, [(cx - w * 0.5, cy), (cx + w * 0.5, cy)]
                                + sorted(up, key=lambda p: p[0]))
        if len(dn) >= 2:
            pygame.draw.polygon(surf, shadow, [(cx - w * 0.5, cy), (cx + w * 0.5, cy)]
                                + sorted(dn, key=lambda p: p[0]))
        pygame.draw.polygon(surf, base, body)          # re-seat body over facet spill
        # Redraw crown facet as a contained cap only in the top third.
        cap = [p for p in body if p[1] <= cy - hh * 0.12]
        if len(cap) >= 3:
            pygame.draw.polygon(surf, lit, cap)
        low = [p for p in body if p[1] >= cy + hh * 0.06]
        if len(low) >= 3:
            pygame.draw.polygon(surf, shadow, low)
        pygame.draw.polygon(surf, _shade(base, -8), body, 1)

    # (c) Large talus blocks marching world-locked across the FULL width, dense
    # enough (~one per 34px cell) that the seam is broken edge-to-edge — not a few
    # scattered dots. A screen-space presence gate would pop under world scroll, so
    # coverage is kept uniformly dense instead; edges therefore always carry blocks.
    for sx, k, rng in _scatter(scroll, W, 1.0, 34, 0xA21):
        if rng.random() < 0.18:            # a few gaps so it isn't a solid wall
            continue
        w = rng.randint(20, 34)
        hh = rng.randint(14, 22)
        crown = rng.randint(3, 9)
        cy = GROUND_Y - crown + hh * 0.5
        boulder(sx, rng, w, hh, cy)

    # (d) Medium cobbles bedded fully in the sand, filling the mid course.
    for sx, k, rng in _scatter(scroll, W, 1.0, 58, 0xB33):
        if rng.random() < 0.35:
            continue
        w = rng.randint(10, 17)
        hh = rng.randint(7, 12)
        cy = rng.uniform(611, 630)
        boulder(sx, rng, w, hh, cy)


foreground_mod.draw_foreground_floor = draw_scree

OUT = "/home/user/skybit/docs/ground-redesign/foothill-scree-apron/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
app = App()
app._start_play()
app.world.lives_remaining = 1
app._render()
pygame.image.save(app.screen, OUT)
print(f"Saved: {OUT}")

# --- verification: apron ramp + no hard seam ---
scr = app.screen
print("\nApron ramp (column x=8, a boulder-free edge column expected):")
for x in [8, 30, 180, 340]:
    col = [scr.get_at((x, y))[:3] for y in range(593, 610)]
    print(f" x={x}:")
    for i, y in enumerate(range(593, 610)):
        print(f"   y={y}: {col[i]}")
    break
print("\nSeam jump (|y594 - y595|) sampled across width:")
jumps = []
for x in range(0, 360, 12):
    a = scr.get_at((x, 594))[:3]
    b = scr.get_at((x, 595))[:3]
    d = max(abs(a[i] - b[i]) for i in range(3))
    jumps.append(d)
print(" max per-column seam delta:", max(jumps), " mean:", sum(jumps)//len(jumps))
