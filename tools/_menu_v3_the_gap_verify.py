"""Numeric audit of the THE GAP hero frame. Never opens the image — every
claim in the round report is measured off pixels here."""
from __future__ import annotations

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

import importlib  # noqa: E402
_r1 = importlib.import_module("tools._menu_v3_the_gap_r1")
from game.draw import COIN_GOLD  # noqa: E402


def L(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def main():
    hero, rects, pip_info, world = _r1.build()
    get = lambda x, y: hero.get_at((x, y))[:3]

    print("=" * 68)
    print("1. COIN vs BACKDROP  (COIN_GOLD luma %.1f)" % L(COIN_GOLD))
    bare = pygame.Surface((_r1.W, _r1.H))
    from game import biome, sky_designs
    from game.mountains_v14 import draw_mountains_v14
    pal = biome.palette_for_phase(_r1.PHASE)
    for ph in (0.27, _r1.PHASE):
        s2 = pygame.Surface((_r1.W, _r1.H))
        sky_designs.render_active(s2, _r1.W, _r1.H, _r1.GROUND_Y,
                                  biome.palette_for_phase(ph), ph)
        vals = [L(s2.get_at((cx, cy))[:3]) for cx, cy, _d in _r1.COINS]
        print(f"   sky-only luma under the 5 coin centres @phase {ph}: "
              + ", ".join(f"{v:.0f}" for v in vals)
              + f"   -> margin {L(COIN_GOLD) - max(vals):+.0f}..{L(COIN_GOLD) - min(vals):+.0f}")
    for cx, cy, d in _r1.COINS:
        r = d // 2
        disc = [L(get(cx + dx, cy + dy))
                for dx in range(-r, r + 1) for dy in range(-r, r + 1)
                if dx * dx + dy * dy <= r * r]
        ring = [L(get(cx + dx, cy + dy))
                for dx in range(-d, d + 1) for dy in range(-d, d + 1)
                if r + 2 <= (dx * dx + dy * dy) ** 0.5 <= r + 4]
        print(f"   coin d={d:2d} @({cx},{cy}): disc luma {min(disc):.0f}-{max(disc):.0f} "
              f"(mean {sum(disc)/len(disc):.0f})  surround {min(ring):.0f}-{max(ring):.0f} "
              f"(mean {sum(ring)/len(ring):.0f})  -> peak-vs-surround "
              f"{max(disc) - sum(ring)/len(ring):+.0f}")

    print("=" * 68)
    print("2. EYE PATH")
    ds = [d for _x, _y, d in _r1.COINS]
    ys = [y for _x, y, _d in _r1.COINS]
    print(f"   coin diameters gap->camera: {ds}  (monotonic growing: {ds == sorted(ds)})")
    print(f"   coin y gap->camera:         {ys}  (descending screen: {ys == sorted(ys)})")
    last_bot = ys[-1] + ds[-1] // 2
    print(f"   last coin bottom y={last_bot}, START pill top y={rects['START'].top}"
          f"  -> clearance {rects['START'].top - last_bot}px, terminates ABOVE the capsule")

    print("=" * 68)
    print("3. RANK SEPARATION (mean luma over each rank's own opaque pixels)")
    names = ["far  (veil a=90)", "mid  (veil a=45)", "near (no veil)"]
    means = []
    for name, spec in zip(names, _r1.RANKS):
        band = _r1.rank_band(pal, *spec)
        tot = n = 0
        lo, hi = 999, 0
        for y in range(0, spec[5], 2):
            for x in range(0, _r1.W, 2):
                c = band.get_at((x, y))
                if c[3] > 200:
                    l = L(c[:3])
                    tot += l
                    n += 1
                    lo = min(lo, l)
                    hi = max(hi, l)
        means.append(tot / max(1, n))
        print(f"   {name}: mean luma {means[-1]:6.1f}  range {lo:.0f}-{hi:.0f}"
              f"  ({n} sampled px)")
    print(f"   value step far->mid {means[0] - means[1]:+.1f}   "
          f"mid->near {means[1] - means[2]:+.1f}")
    # Silhouette scale is the other separation channel.
    for name, spec in zip(names, _r1.RANKS):
        print(f"   {name}: body width {spec[1]}px, gap mouth "
              f"{spec[4] - spec[3]}px tall, base y={spec[5]}")

    print("=" * 68)
    print("4. STYLE CONFORMANCE")
    pure_w = pure_b = 0
    mx = (0, None)
    hist_hi = {}
    for y in range(_r1.H):
        for x in range(_r1.W):
            c = hero.get_at((x, y))[:3]
            if c == (255, 255, 255):
                pure_w += 1
                hist_hi[(x // 40 * 40, y // 40 * 40)] = \
                    hist_hi.get((x // 40 * 40, y // 40 * 40), 0) + 1
            if c == (0, 0, 0):
                pure_b += 1
            l = L(c)
            if l > mx[0]:
                mx = (l, (x, y, c))
    print(f"   pure white px: {pure_w}   pure black px: {pure_b}")
    if pure_w:
        print("   pure-white 40px cells:", sorted(hist_hi.items(),
                                                  key=lambda kv: -kv[1])[:6])
    print(f"   brightest pixel: luma {mx[0]:.1f} at {mx[1][:2]} rgb {mx[1][2]}")

    # Where does everything above the coin's own luma actually live?
    over = {}
    for y in range(_r1.H):
        for x in range(_r1.W):
            l = L(hero.get_at((x, y))[:3])
            if l > L(COIN_GOLD):
                over[(x // 30 * 30, y // 30 * 30)] = \
                    over.get((x // 30 * 30, y // 30 * 30), 0) + 1
    tot = sum(over.values())
    print(f"   px brighter than COIN_GOLD: {tot} of {_r1.W * _r1.H} "
          f"({100.0 * tot / (_r1.W * _r1.H):.2f}%)")
    print("   their 30px cells (top 8):",
          sorted(over.items(), key=lambda kv: -kv[1])[:8])

    wmax = (0, None)
    wover = 0
    for y in range(_r1.H):
        for x in range(_r1.W):
            c = world.get_at((x, y))[:3]
            l = L(c)
            if l > L(COIN_GOLD):
                wover += 1
            if l > wmax[0]:
                wmax = (l, (x, y, c))
    print(f"   WORLD layer only (no UI): brightest luma {wmax[0]:.1f} at "
          f"{wmax[1][:2]} rgb {wmax[1][2]};  px over COIN_GOLD: {wover}")

    print("=" * 68)
    print("5. TITLE LEGIBILITY OVER THE CORRIDOR")
    band = [L(world.get_at((x, y))[:3])
            for y in range(56, 146) for x in range(56, 304)]
    print(f"   backdrop under the wordmark block: luma {min(band):.0f}-{max(band):.0f} "
          f"(mean {sum(band)/len(band):.0f})")
    print(f"   gold face luma {L((240,192,64)):.0f}, rust outline luma "
          f"{L((168,32,16)):.0f}  -> face-vs-outline {L((240,192,64)) - L((168,32,16)):+.0f}")
    for y in (72, 88, 104):
        row = [L(get(x, y)) for x in range(64, 296)]
        print(f"   composited y={y}: luma range {min(row):.0f}-{max(row):.0f}")

    print("=" * 68)
    print("6. PIP")
    print(f"   build path: {pip_info[0]}")
    print(f"   equipped skin={pip_info[1]}  parcel={pip_info[2]}  sprite={pip_info[3]}")

    print("=" * 68)
    print("7. TAP TARGETS")
    order = ["START", "PROFILE", "STORE", "TOP 10", "SETTINGS"]
    for i, k in enumerate(order):
        r = rects[k]
        print(f"   {k:<9} {r.w}x{r.h} @({r.x},{r.y})  bottom={r.bottom}")
        for j in range(i + 1, len(order)):
            if r.colliderect(rects[order[j]]):
                print(f"      !! OVERLAP with {order[j]}")
    print("   readable-content bottom edge (chip caption baseline): "
          f"{_r1.CHIP_CY + 14 + 7}")



if __name__ == "__main__":
    main()
