"""
Small per-biome signature motif painters (the one hero structure each biome
places on the near-ridge baseline). Kept tiny — identity comes from silhouette
+ value against the sky_field gradient, not fine detail. Each reads the stage
palette's struct_* colors so it retints across all day-stages automatically.

ctx is a scene_engine.SceneCtx: (surf, w, h, ground_y, phase, scroll, pal, dpal).
"""
import math
import pygame


def _struct(ctx):
    p = ctx.pal
    return (p.get('struct_light', (200, 185, 160)),
            p.get('struct_mid', (165, 140, 110)),
            p.get('struct_dark', (110, 88, 66)),
            p.get('struct_accent', (140, 110, 80)))


def _nightf(ctx):
    """Continuous 0..1 night-ness from sky_top luminance — lets a motif push its
    glow as the stage darkens without a hard phase threshold (keeps the
    cross-fade between stage columns smooth)."""
    r, g, b = ctx.pal.get('sky_top', (60, 120, 200))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return max(0.0, min(1.0, (95.0 - lum) / 75.0))


# ── Group A signatures ────────────────────────────────────────────────────────

def draw_mesa_arch(ctx):
    """A free-standing eroded sandstone arch beside a stepped butte — the
    desert-mesa hero. The arch is drawn as a SILHOUETTE (two tapering legs + a
    spanning lintel in struct_mid/dark with a sunlit struct_light rim) so the
    sky reads straight through the window between the legs."""
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    light, mid, dark, accent = _struct(ctx)

    # ── Stepped butte (right): a tall block with a lower bench shouldering it,
    # so the near silhouette is not a plain rectangle. ──
    bx = int(w * 0.58)
    bw = int(w * 0.26)
    top = gy - int(gy * 0.34)
    bench_top = gy - int(gy * 0.20)
    bench_w = int(bw * 0.42)
    # Lower bench on the left shoulder.
    pygame.draw.polygon(surf, mid, [
        (bx - bench_w, gy), (bx - bench_w + 4, bench_top),
        (bx + 4, bench_top), (bx + 4, gy)])
    pygame.draw.line(surf, light, (bx - bench_w + 4, bench_top),
                     (bx + 4, bench_top), 2)
    # Main block (flat top, slightly battered sides).
    body = [(bx, gy), (bx + 5, top), (bx + bw - 7, top), (bx + bw, gy)]
    pygame.draw.polygon(surf, mid, body)
    # Shadowed right face for volume.
    pygame.draw.polygon(surf, dark, [
        (bx + int(bw * 0.60), top), (bx + bw - 7, top),
        (bx + bw, gy), (bx + int(bw * 0.60), gy)])
    # Sunlit cap rim.
    pygame.draw.line(surf, light, (bx + 5, top), (bx + bw - 7, top), 3)

    # ── Free-standing arch (left of the butte) ──
    # Built as filled polygons: outer outline minus a sky-window means we paint
    # the two legs + the curved lintel band as solid stone, leaving the gap
    # between them as untouched sky.
    ax = int(w * 0.30)            # arch centre x
    span = int(w * 0.18)          # leg-to-leg outer span
    base = gy
    arch_h = int(gy * 0.30)       # height of the opening crown
    leg_w = max(6, int(span * 0.20))
    xl = ax - span // 2           # left outer edge
    xr = ax + span // 2           # right outer edge
    crown_y = base - arch_h       # top of the opening
    band = max(6, int(arch_h * 0.22))  # thickness of the spanning lintel

    # Sample the inner opening as an upward ellipse arc so the window is a clean
    # horseshoe; legs taper slightly outward toward the ground (eroded base).
    inner_l = xl + leg_w
    inner_r = xr - leg_w
    cx = (inner_l + inner_r) / 2.0
    rx = (inner_r - inner_l) / 2.0
    ry = arch_h - band

    def _inner_y(x):
        # half-ellipse roof over the opening; clamp to base below the springline.
        dx = (x - cx) / rx if rx > 0 else 0.0
        if abs(dx) >= 1.0:
            return base
        return base - ry * math.sqrt(1.0 - dx * dx)

    # Outer silhouette walked left→right across the top, then back along the
    # inner opening — one polygon paints both legs + the lintel, hole included.
    outer = [(xl, base)]
    outer.append((xl, crown_y - band))
    # outer crown sweep
    steps = 18
    for i in range(steps + 1):
        x = xl + (xr - xl) * i / steps
        # outer roof: a flatter ellipse riding `band` above the inner opening
        dx = (x - ax) / (span / 2.0)
        oy = crown_y - band * (1.0 - min(1.0, dx * dx)) * 0.0  # near-flat top
        oy = crown_y - band
        outer.append((int(x), int(oy)))
    outer.append((xr, crown_y - band))
    outer.append((xr, base))
    # inner opening walked right→left
    inner = []
    for i in range(steps + 1):
        x = inner_r - (inner_r - inner_l) * i / steps
        inner.append((int(x), int(_inner_y(x))))
    poly = outer + inner
    pygame.draw.polygon(surf, mid, poly)
    # Shadowed right leg + inner-right reveal.
    pygame.draw.polygon(surf, dark, [
        (inner_r, int(_inner_y(inner_r))), (xr, crown_y - band),
        (xr, base), (inner_r, base)])
    # Sunlit rim along the left leg + over the crown.
    pygame.draw.line(surf, light, (xl, base), (xl, crown_y - band), 2)
    pygame.draw.line(surf, light, (xl, crown_y - band),
                     (ax, crown_y - band), 2)
    # A small companion fin further left for depth.
    fx = int(w * 0.13)
    ft = gy - int(gy * 0.16)
    fw = int(w * 0.05)
    pygame.draw.polygon(surf, mid, [(fx, gy), (fx + 3, ft),
                                    (fx + fw - 3, ft), (fx + fw, gy)])
    pygame.draw.line(surf, light, (fx + 3, ft), (fx + fw - 3, ft), 2)


def ember_haze(ctx):
    """A faint ember band hugging the horizon for the volcanic caldera — a warm
    additive smear that intensifies with night-ness so the sky always feels lit
    from below by the magma, strongest once the day light is gone."""
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    glow = ctx.pal.get('glow_color', (255, 120, 50))
    night = _nightf(ctx)
    s = pygame.Surface((w, gy), pygame.SRCALPHA)
    # Two stacked elliptical smears: a broad low one + a tighter brighter core.
    a_lo = int(34 + 70 * night)
    a_hi = int(50 + 110 * night)
    y0 = int(gy * 0.80)
    pygame.draw.ellipse(s, (*glow, a_lo),
                        pygame.Rect(-w // 3, y0 - int(gy * 0.18),
                                    int(w * 1.66), int(gy * 0.40)))
    pygame.draw.ellipse(s, (*glow, a_hi),
                        pygame.Rect(-w // 4, y0 - int(gy * 0.07),
                                    int(w * 1.5), int(gy * 0.20)))
    surf.blit(s, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def karst_mist(ctx):
    """Layered shan-shui haze for the karst water-town, drawn over the sky so the
    towers fade into it. Banks rise (more, higher) as the day cools so dawn/dusk
    feel especially humid and serene."""
    from scene_engine import mist_bands
    night = _nightf(ctx)
    mtint = ctx.pal.get('mist_tint', (210, 222, 220))
    # More bands + higher alpha when cool; midday is clearer.
    n = 4 + int(round(night * 2))
    alpha = int(60 + 35 * night)
    mist_bands(ctx.surf, ctx.w, ctx.ground_y, mtint, y0_frac=0.52, n=n, alpha=alpha)


def draw_summit_shrine(ctx):
    """A tiny ridge-top shrine + a strung line of prayer flags for the alpine
    biome — the ridge snow-caps carry the scene, this just adds a human mark
    that scales the loneliness of the peak."""
    from game.pillar_variants import draw_prayer_flags
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    light, mid, dark, accent = _struct(ctx)
    x = int(w * 0.52)
    y = gy - int(gy * 0.30)
    # Stone base + whitewashed body so it reads as a chorten against dark rock.
    pygame.draw.rect(surf, dark, (x - 9, y + 12, 18, 8))
    pygame.draw.rect(surf, mid, (x - 8, y, 16, 14))
    pygame.draw.line(surf, light, (x - 8, y), (x + 8, y), 2)
    # Tiered roof.
    pygame.draw.polygon(surf, dark, [(x - 11, y), (x + 11, y), (x, y - 11)])
    pygame.draw.line(surf, light, (x - 11, y), (x, y - 11), 2)
    # Finial.
    pygame.draw.line(surf, accent, (x, y - 11), (x, y - 16), 2)
    # Prayer-flag line strung down-slope from the finial.
    draw_prayer_flags(surf, x + 3, y - 14, x + 46, y + 6, n=7)


def draw_basalt_columns(ctx):
    """A palisade of vertical basalt columns with a lava-ember glow that rises
    with the night-ness of the stage — the volcanic-caldera hero. Column tops
    are stepped (real basalt fractures into uneven hexagonal stubs) and the
    seam between them glows molten."""
    from scene_engine import soft_disc
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    light, mid, dark, accent = _struct(ctx)
    glow = ctx.pal.get('glow_color', (255, 110, 40))
    night = _nightf(ctx)

    base = int(w * 0.46)
    n = 9
    cw = int(w * 0.042)
    span = n * cw

    # Ember pool at the column feet — broad additive glow, far stronger at night.
    if night > 0.04:
        s = pygame.Surface((w, gy), pygame.SRCALPHA)
        ga = int(70 + 120 * night)
        pygame.draw.ellipse(s, (*glow, ga),
                            (base - cw * 2, gy - 30, span + cw * 4, 46))
        surf.blit(s, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # Columns: alternating mid/dark faces, each capped by a short bright stub so
    # the tops don't read as one flat saw-edge.
    heights = []
    for i in range(n):
        x = base + i * cw
        # Two-octave height so the palisade crest undulates rather than zig-zags.
        frac = 0.18 + 0.13 * abs(math.sin(i * 0.9)) + 0.05 * abs(math.sin(i * 2.3))
        ch = gy - int(gy * frac)
        heights.append((x, ch))
        col = mid if i % 2 else dark
        pygame.draw.rect(surf, col, (x, ch, cw - 1, gy - ch))
        # Bright fractured cap (a short stub of lighter stone on top).
        pygame.draw.rect(surf, light, (x, ch, cw - 1, 3))
        # Vertical joint shadow on the right edge for column separation.
        pygame.draw.line(surf, dark, (x + cw - 1, ch), (x + cw - 1, gy), 1)

    # Molten seam pooling at the bases, brighter at night.
    seam_col = glow if night > 0.3 else accent
    pygame.draw.line(surf, seam_col, (base - cw, gy - 2),
                     (base + span, gy - 2), 3)
    # A couple of glowing cracks climbing between columns at night.
    if night > 0.25:
        for i in (2, 5, 7):
            x, ch = heights[i]
            ca = int(120 + 110 * night)
            cs = pygame.Surface((6, gy - ch), pygame.SRCALPHA)
            for yy in range(0, gy - ch, 2):
                t = yy / max(1, gy - ch)
                pygame.draw.line(cs, (*glow, int(ca * t)),
                                 (3 + int(math.sin(yy * 0.4) * 1.5), yy),
                                 (3 + int(math.sin(yy * 0.4) * 1.5), yy + 1), 1)
            surf.blit(cs, (x, ch), special_flags=pygame.BLEND_RGB_ADD)


def draw_stilt_houses(ctx):
    """A small cluster of stilt houses standing in a calm water inlet with a
    mirrored reflection — the misty karst water-town hero. A water_tint band
    along the ground line gives the still-water read."""
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    light, mid, dark, accent = _struct(ctx)
    water = ctx.pal.get('water_tint', (90, 120, 130))

    # Still-water band sitting on the ground line — houses + reflections sit on
    # it. Drawn first so the structures overlap its top edge.
    water_h = max(14, int(gy * 0.05))
    wb = pygame.Surface((w, water_h + 24), pygame.SRCALPHA)
    for yy in range(water_h):
        t = yy / max(1, water_h)
        c = (int(water[0] * (1 - 0.25 * t)),
             int(water[1] * (1 - 0.25 * t)),
             int(water[2] * (1 - 0.25 * t)))
        pygame.draw.line(wb, (*c, 200), (0, yy), (w, yy))
    surf.blit(wb, (0, gy - 2))

    cx = int(w * 0.54)
    houses = []
    for i, dx in enumerate((-42, 0, 40)):
        x = cx + dx
        hw = 24 - (i % 2) * 5
        hh = 18
        roof_y = gy - 30 - (i % 2) * 6
        houses.append((x, hw, hh, roof_y))
        # Stilts down into the water.
        for sxp in (x - hw // 2 + 3, x + hw // 2 - 3):
            pygame.draw.line(surf, dark, (sxp, gy + 2), (sxp, roof_y + hh), 2)
        # Body.
        pygame.draw.rect(surf, mid, (x - hw // 2, roof_y, hw, hh))
        # Warm-lit window so the village reads at dusk/night.
        pygame.draw.rect(surf, accent, (x - 2, roof_y + 5, 4, 5))
        # Roof.
        pygame.draw.polygon(surf, dark, [(x - hw // 2 - 3, roof_y),
                                         (x + hw // 2 + 3, roof_y),
                                         (x, roof_y - 11)])
        pygame.draw.line(surf, light, (x - hw // 2 - 3, roof_y),
                         (x, roof_y - 11), 1)

    # Mirrored reflections: dim, vertically squashed, tinted to the water.
    refl = pygame.Surface((w, water_h + 4), pygame.SRCALPHA)
    for (x, hw, hh, roof_y) in houses:
        rh = max(3, water_h - 2)
        pygame.draw.rect(refl, (*mid, 90), (x - hw // 2, 0, hw, rh))
        pygame.draw.polygon(refl, (*dark, 90),
                            [(x - hw // 2 - 3, 0), (x + hw // 2 + 3, 0),
                             (x, rh - 1)])
    surf.blit(refl, (0, gy), special_flags=pygame.BLEND_RGBA_SUB)
    # Two bright horizontal glints on the water surface.
    gl = pygame.Surface((w, water_h), pygame.SRCALPHA)
    pygame.draw.line(gl, (*light, 90), (cx - 50, 3), (cx + 50, 3), 1)
    pygame.draw.line(gl, (*light, 60), (cx - 30, water_h // 2),
                     (cx + 36, water_h // 2), 1)
    surf.blit(gl, (0, gy), special_flags=pygame.BLEND_RGB_ADD)


def draw_alpine_conifers(ctx):
    """A few dark conifers at the base of the snowpeaks — counter-scales the
    huge cold ridges and reads as treeline far below the summits."""
    from game.pillar_variants import draw_pine_trio
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    # Spread two trios across the foreground; ctx.dpal carries foliage_* so the
    # production painter retints to the cold biome greens automatically.
    draw_pine_trio(surf, int(w * 0.16), gy - 6, ctx.dpal, seed=2)
    draw_pine_trio(surf, int(w * 0.82), gy - 2, ctx.dpal, seed=7)


def draw_bamboo_fringe(ctx):
    """Sparse bamboo-ish verticals fringing the karst water-town — thin jade
    culms with a few leaf flicks. Kept airy so the mist still dominates."""
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    dp = ctx.dpal
    dark = dp.get('foliage_dark', (40, 80, 60))
    mid = dp.get('foliage_mid', (70, 120, 85))
    top = dp.get('foliage_top', (120, 170, 120))
    # Two loose clumps at the frame edges so the centre stays open to the houses.
    for bx, n, scale in ((int(w * 0.10), 5, 1.0), (int(w * 0.90), 4, 0.85)):
        for i in range(n):
            off = (i - n // 2) * 5
            ch = int(gy * (0.20 + 0.05 * abs(math.sin(bx + i)))) * scale
            x = bx + off
            top_y = gy - int(ch)
            pygame.draw.line(surf, dark, (x, gy), (x, top_y), 2)
            # A couple of node ticks + a leaf flick near the crown.
            for t in (0.45, 0.72):
                ny = int(gy - ch * t)
                pygame.draw.line(surf, mid, (x - 1, ny), (x + 1, ny), 1)
            pygame.draw.line(surf, mid, (x, top_y + 4),
                             (x + 5 + (i % 2) * 3, top_y - 2), 1)
            pygame.draw.line(surf, top, (x, top_y + 8),
                             (x - 5, top_y + 1), 1)


def draw_autumn_canopy(ctx):
    """A dense band of warm-tinted canopy across the foreground hill — the fiery
    maple read. Pine_trio + wuling_pine are retinted through ctx.dpal's
    foliage_* (set warm in the keyframes) so the whole stand glows."""
    from game.pillar_variants import draw_pine_trio
    from game.draw import draw_wuling_pine
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    dp = ctx.dpal
    # A back rank of softer canopy, then a denser front rank, so the foliage
    # reads as a deep forest rather than a row of trees.
    for x, hgt, lean in ((int(w * 0.06), 40, 6), (int(w * 0.24), 52, -8),
                         (int(w * 0.40), 34, 4), (int(w * 0.72), 46, -6),
                         (int(w * 0.92), 38, 8)):
        draw_wuling_pine(surf, x, gy - 2, hgt, dp, lean=lean, layers=5)
    draw_pine_trio(surf, int(w * 0.16), gy + 4, dp, seed=3)
    draw_pine_trio(surf, int(w * 0.84), gy + 2, dp, seed=9)


def draw_terrace_cairn(ctx):
    """A short dry-stone terrace wall topped by a way-marker cairn — the
    autumn-highlands hero. A human-scaled mark on a forested hillside; warm
    struct_* colors keep it inside the fiery palette."""
    from game.pillar_variants import draw_terrace_wall, draw_cairn
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    light, mid, dark, accent = _struct(ctx)
    cx = int(w * 0.50)
    wall_y = gy - int(gy * 0.16)
    # Retinted terrace: draw_terrace_wall hardcodes earth tones, so lay a
    # struct-tinted bench beneath it to anchor it in the stage palette.
    bw = int(w * 0.30)
    pygame.draw.rect(surf, dark, (cx - bw // 2, wall_y, bw, gy - wall_y))
    pygame.draw.rect(surf, mid, (cx - bw // 2, wall_y, bw, 4))
    pygame.draw.line(surf, light, (cx - bw // 2, wall_y),
                     (cx + bw // 2, wall_y), 2)
    draw_terrace_wall(surf, cx, wall_y, width=min(bw, 58))
    # Way-marker cairn on the terrace lip.
    draw_cairn(surf, cx - bw // 4, wall_y, n=4, pennant=True)
    draw_cairn(surf, cx + bw // 3, wall_y + 2, n=3, pennant=False)
