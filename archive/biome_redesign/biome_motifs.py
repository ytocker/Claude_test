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
    towers fade into it FROM THE FEET UP. Anchored low (tower bases + waterline)
    so the upper half of the canvas keeps a readable jade gradient — a mist that
    sat high washed the whole sky near-white and was washiest exactly at midday,
    backwards from how the air actually clears in strong light. Banks only rise
    and thicken as the day cools, so predawn/dusk read as the humid, serene
    stages while day stays clear."""
    from scene_engine import mist_bands
    night = _nightf(ctx)
    mtint = ctx.pal.get('mist_tint', (210, 222, 220))
    # ONE thin low band by day, a couple more (and higher) only as the day cools.
    # y0_frac anchored in the lower third so the upper half of canvas keeps a
    # readable jade gradient — heavy banks belong to predawn/dusk, not midday.
    n = 1 + int(round(night * 2))
    alpha = int(26 + 16 * night)
    mist_bands(ctx.surf, ctx.w, ctx.ground_y, mtint, y0_frac=0.76, n=n, alpha=alpha)


def draw_summit_shrine(ctx):
    """A tiny ridge-top shrine + a strung line of prayer flags for the alpine
    biome — the ridge snow-caps carry the scene, this just adds a human mark
    that scales the loneliness of the peak."""
    from game.pillar_variants import draw_prayer_flags
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    light, mid, dark, accent = _struct(ctx)
    # Sat against the near ridge (the tallest jagged hero teeth) and scaled ~50%
    # so the human mark is legible from the play area; the prayer flags carry the
    # only saturated color in an otherwise cold scene, so they pop hardest.
    x = int(w * 0.50)
    y = gy - int(gy * 0.34)
    # Stone base + whitewashed body so it reads as a chorten against dark rock.
    pygame.draw.rect(surf, dark, (x - 13, y + 18, 27, 11))
    pygame.draw.rect(surf, mid, (x - 12, y, 24, 21))
    pygame.draw.line(surf, light, (x - 12, y - 1), (x + 12, y - 1), 3)
    # Tiered roof.
    pygame.draw.polygon(surf, dark, [(x - 16, y), (x + 16, y), (x, y - 16)])
    pygame.draw.line(surf, light, (x - 16, y), (x, y - 16), 3)
    # Finial.
    pygame.draw.line(surf, accent, (x, y - 16), (x, y - 24), 3)
    # Prayer-flag line strung down-slope from the finial — saturated flag blocks.
    draw_prayer_flags(surf, x + 5, y - 21, x + 64, y + 8, n=7)


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

    # Push the column faces ~1 value step lighter than the stage struct tones so
    # the palisade silhouette stays crisp against the (now darker) caldera hills
    # behind it even at small size.
    def _lift(c, d=14):
        return (min(255, c[0] + d), min(255, c[1] + d), min(255, c[2] + d))
    mid, dark = _lift(mid), _lift(dark)

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

    # Warm window value floored even higher than struct_accent so the lit panes
    # carry the village by dusk even when the stage accent is a muted day tone —
    # the hero must stay legible, the lights are its whole charm. Floor lifted so
    # dusk windows glow rather than sitting at a dim daytime accent.
    win = (max(accent[0], 245), max(accent[1], 188), max(accent[2], 110))

    cx = int(w * 0.54)
    houses = []
    # Cluster scaled up ~35% over the bric-a-brac version (wider spacing, taller
    # bodies + roofs + thicker stilts) so the hero holds the eye against the
    # towers instead of reading as a row of tiny boxes.
    for i, dx in enumerate((-74, 0, 72)):
        x = cx + dx
        hw = 42 - (i % 2) * 8
        hh = 32
        roof_y = gy - 52 - (i % 2) * 10
        houses.append((x, hw, hh, roof_y))
        # Stilts down into the water.
        for sxp in (x - hw // 2 + 5, x + hw // 2 - 5):
            pygame.draw.line(surf, dark, (sxp, gy + 2), (sxp, roof_y + hh), 3)
        # Body.
        pygame.draw.rect(surf, mid, (x - hw // 2, roof_y, hw, hh))
        # Warm-lit window so the village reads at dusk/night.
        pygame.draw.rect(surf, win, (x - 4, roof_y + 9, 8, 9))
        # Roof.
        pygame.draw.polygon(surf, dark, [(x - hw // 2 - 5, roof_y),
                                         (x + hw // 2 + 5, roof_y),
                                         (x, roof_y - 20)])
        pygame.draw.line(surf, light, (x - hw // 2 - 5, roof_y),
                         (x, roof_y - 20), 2)

    # Mirrored reflections: dim, vertically squashed, tinted to the water. Kept
    # faint (subtractive, low alpha) so the bright waterline glint above it still
    # separates land from water rather than the reflection swallowing the edge.
    refl = pygame.Surface((w, water_h + 4), pygame.SRCALPHA)
    for (x, hw, hh, roof_y) in houses:
        rh = max(3, water_h - 2)
        pygame.draw.rect(refl, (*mid, 70), (x - hw // 2, 0, hw, rh))
        pygame.draw.polygon(refl, (*dark, 70),
                            [(x - hw // 2 - 4, 0), (x + hw // 2 + 4, 0),
                             (x, rh - 1)])
    surf.blit(refl, (0, gy), special_flags=pygame.BLEND_RGBA_SUB)
    # Two bright horizontal glints on the water surface.
    gl = pygame.Surface((w, water_h), pygame.SRCALPHA)
    pygame.draw.line(gl, (*light, 90), (cx - 64, 3), (cx + 64, 3), 1)
    pygame.draw.line(gl, (*light, 60), (cx - 38, water_h // 2),
                     (cx + 44, water_h // 2), 1)
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
    """A FOREST read, not a bead-string of equal trees: first a single continuous
    dark canopy band (foliage_dark) rolls across the foreground as one mass, then
    a few brighter clumps (foliage_top/accent) sit on top ONLY as sparse sunlit
    highlights. Strung individual bright trees made every trunk an equal hotspot;
    a dark mass with scattered glints reads as deep fiery woodland instead."""
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    dp = ctx.dpal
    dark = dp.get('foliage_dark', (60, 40, 40))
    mid = dp.get('foliage_mid', (130, 70, 45))
    top = dp.get('foliage_top', (236, 162, 66))
    accent = dp.get('foliage_accent', (252, 200, 100))
    # Knock the bright top ~20% so the highlight clumps stop reading as equal
    # blown-out hotspots against the dark mass.
    top = (int(top[0] * 0.80), int(top[1] * 0.80), int(top[2] * 0.80))

    # 1. Continuous dark canopy band as the dominant mass — a lumpy upper edge
    # (summed sines, irregular periods so no two crowns repeat) over a tall solid
    # fill to the ground, so the whole foreground reads as one woodland silhouette
    # first and the brights only sit ON it. A second mid-tone crest just below the
    # rim gives the mass internal depth without breaking it into beads.
    base = gy - int(gy * 0.06)

    def _crest_y(x):
        return int(base - 18
                   - (math.sin(x * 0.037) * 13 + math.sin(x * 0.083 + 1.3) * 8
                      + math.sin(x * 0.19 + 0.6) * 4 + math.sin(x * 0.31 + 2.1) * 2))

    crest = [(x, _crest_y(x)) for x in range(0, w + 1, 5)]
    pygame.draw.polygon(surf, dark, [(0, gy)] + crest + [(w, gy)])
    # Mid-tone scumble band hugging the crest — a continuous lumpy line of small
    # discs, not isolated dots, so the rim still reads as one rolling canopy.
    for (x, y) in crest[::2]:
        pygame.draw.circle(surf, mid, (x, y + 6), 4)

    # 2. Sparse sunlit clumps: irregular x-spacing + varied size/value break the
    # repeat period. Only a handful — most of the canopy stays dark — and each
    # clump rides the actual crest height so it nestles into the mass.
    clumps = [(0.08, 8, top), (0.19, 5, accent), (0.34, 9, top),
              (0.55, 6, accent), (0.72, 8, top), (0.88, 5, accent)]
    for fx, r, col in clumps:
        x = int(w * fx)
        cy = _crest_y(x) - 1
        pygame.draw.circle(surf, mid, (x, cy + 3), r + 1)
        pygame.draw.circle(surf, col, (x, cy), r)
        pygame.draw.circle(surf, col, (x - r + 2, cy + 2), max(2, r - 3))


def draw_terrace_cairn(ctx):
    """A short dry-stone terrace wall topped by a way-marker cairn — the
    autumn-highlands hero. A human-scaled mark on a forested hillside; warm
    struct_* colors keep it inside the fiery palette."""
    from game.pillar_variants import draw_terrace_wall, draw_cairn
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    light, mid, dark, accent = _struct(ctx)
    cx = int(w * 0.50)
    # Lifted clear of the now-taller dark canopy mass so the human mark sits in a
    # cut pocket ABOVE the woodland rim instead of being swallowed by it.
    wall_y = gy - int(gy * 0.30)
    bw = int(w * 0.30)
    # A struct-dark notch dropped behind the wall gives the terrace a darker
    # pocket to read against, then a bright struct_light coping line crowns it so
    # the masonry rim is the lightest mark on the hillside.
    pygame.draw.rect(surf, dark, (cx - bw // 2, wall_y, bw, gy - wall_y))
    pygame.draw.rect(surf, mid, (cx - bw // 2, wall_y, bw, 5))
    pygame.draw.line(surf, light, (cx - bw // 2, wall_y - 1),
                     (cx + bw // 2, wall_y - 1), 3)
    draw_terrace_wall(surf, cx, wall_y, width=min(bw, 58))
    # Way-marker cairn on the terrace lip.
    draw_cairn(surf, cx - bw // 4, wall_y, n=4, pennant=True)
    draw_cairn(surf, cx + bw // 3, wall_y + 2, n=3, pennant=False)


# ── Group B (ink / shan-shui) signatures + atmospheres ────────────────────────

def gorge_mist(ctx):
    """Vertical ink-wash haze for the misty gorge: many overlapping low-alpha
    bands stacked from the tower feet UP through the ranks, so each karst finger
    dissolves into negative-space void between ranks — the hero of this look. The
    veil thickens toward predawn/dusk but stays present all day (a gorge is humid
    in any light), and is anchored low enough that the upper sky stays a readable
    celadon for the HUD."""
    from scene_engine import mist_bands
    night = _nightf(ctx)
    mtint = ctx.pal.get('mist_tint', (210, 224, 224))
    # A tall stack of soft bands so towers fade rank-by-rank into the wash; the
    # count + alpha both rise as the day cools so the void deepens at dusk.
    n = 4 + int(round(night * 2))
    alpha = int(40 + 26 * night)
    mist_bands(ctx.surf, ctx.w, ctx.ground_y, mtint, y0_frac=0.50, n=n, alpha=alpha)
    # One extra high, very faint sheet that catches the tower shoulders so even
    # the tallest fingers read as half-dissolved rather than hard silhouettes.
    mist_bands(ctx.surf, ctx.w, ctx.ground_y, mtint, y0_frac=0.34, n=2,
               alpha=int(20 + 14 * night))


def draw_gorge_pine(ctx):
    """The misty-gorge hero: a lone wuling pine clinging to the nearest karst
    tower, with a tiny stupa perched on a mid tower behind it. Sparse on purpose
    — the negative-space mist is the subject, the pine is just the scale mark."""
    from game.draw import draw_wuling_pine
    from game.pillar_variants import draw_stupa
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    # Stupa on a mid-tower shoulder (drawn first so the near pine overlaps it).
    draw_stupa(surf, int(w * 0.62), gy - int(gy * 0.30))
    # Lone pine on the near tower — the horizontal peacock-tail reads instantly
    # as shan-shui; ctx.dpal carries foliage_* so it retints across stages.
    draw_wuling_pine(surf, int(w * 0.30), gy - int(gy * 0.26), 54, ctx.dpal,
                     lean=12, direction='up', layers=6)
    draw_wuling_pine(surf, int(w * 0.22), gy - int(gy * 0.10), 30, ctx.dpal,
                     lean=-6, direction='up', layers=4)


def draw_snow_temple_sig(ctx):
    """Winter-ink hero: a whitewashed stupa beside a terrace wall, with the one
    warm note in the whole austere scene — a single hung paper lantern. The cold
    monochrome ridges carry the mood; this is the human warmth against them."""
    from game.pillar_variants import (draw_stupa, draw_terrace_wall,
                                       draw_paper_lantern)
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    light, mid, dark, accent = _struct(ctx)
    cx = int(w * 0.52)
    wall_y = gy - int(gy * 0.20)
    # Dark pocket + bright coping so the terrace masonry reads against the snow.
    bw = int(w * 0.26)
    pygame.draw.rect(surf, dark, (cx - bw // 2, wall_y, bw, gy - wall_y))
    pygame.draw.line(surf, light, (cx - bw // 2, wall_y - 1),
                     (cx + bw // 2, wall_y - 1), 3)
    draw_terrace_wall(surf, cx, wall_y, width=min(bw, 54))
    # Whitewashed stupa on the terrace lip — reads as the temple's reliquary.
    draw_stupa(surf, cx - bw // 4, wall_y)
    draw_stupa(surf, cx + bw // 3, wall_y + 2)
    # The single warm lantern hung from a post — the lone warm accent.
    px = cx + bw // 2 + 6
    pygame.draw.line(surf, mid, (px, wall_y + 6), (px, wall_y - 22), 2)
    draw_paper_lantern(surf, px, wall_y - 22, strand=4, scale=1.0, color='gold')


def draw_maple_monastery_sig(ctx):
    """Autumn-ink hero: a hillside monastery — terrace wall + whitewashed stupa +
    a warm red lantern — set apart from Group A's naturalistic autumn by being
    architectural and ink-framed. The maple warmth lives in the foliage callback;
    here the masonry is the human mark on the slope."""
    from game.pillar_variants import (draw_terrace_wall, draw_stupa,
                                       draw_paper_lantern, draw_prayer_flags)
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    light, mid, dark, accent = _struct(ctx)
    cx = int(w * 0.50)
    wall_y = gy - int(gy * 0.27)
    bw = int(w * 0.30)
    pygame.draw.rect(surf, dark, (cx - bw // 2, wall_y, bw, gy - wall_y))
    pygame.draw.rect(surf, mid, (cx - bw // 2, wall_y, bw, 5))
    pygame.draw.line(surf, light, (cx - bw // 2, wall_y - 1),
                     (cx + bw // 2, wall_y - 1), 3)
    draw_terrace_wall(surf, cx, wall_y, width=min(bw, 58))
    # Stupa cluster on the terrace — the monastery reliquaries.
    draw_stupa(surf, cx - bw // 4, wall_y)
    draw_stupa(surf, cx + bw // 4, wall_y + 1)
    # Warm red lantern hung off the near corner + a flag line for festivity.
    px = cx - bw // 2 - 4
    pygame.draw.line(surf, mid, (px, wall_y), (px, wall_y - 18), 2)
    draw_paper_lantern(surf, px, wall_y - 18, strand=4, scale=1.1, color='red')
    draw_prayer_flags(surf, cx - bw // 4, wall_y - 6, cx + bw // 2, wall_y + 4, n=6)


def draw_maple_canopy(ctx):
    """Maple-tinted wuling pines + a pine trio at the frame edges — the warm
    autumn foliage that surrounds the ink monastery. foliage_* are pushed to
    red/orange in the keyframes so the production pine retints to fiery maple."""
    from game.draw import draw_wuling_pine
    from game.pillar_variants import draw_pine_trio
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    draw_pine_trio(surf, int(w * 0.14), gy - 4, ctx.dpal, seed=3)
    draw_wuling_pine(surf, int(w * 0.84), gy - int(gy * 0.06), 50, ctx.dpal,
                     lean=-10, direction='up', layers=6)
    draw_wuling_pine(surf, int(w * 0.92), gy - 2, 32, ctx.dpal,
                     lean=8, direction='up', layers=4)


def cloud_sea(ctx):
    """The sea-of-clouds identity for cloud_sea_peaks: a dense, continuous
    white-grey band massed across the LOWER third of the scene that the karst
    peaks poke up through — horizontal, billowing, unmistakably different from
    misty_gorge's vertical veil. Drawn over the sky (peaks/ground paint after, so
    near towers still rise in front of the cloud feet for depth). Built from many
    overlapping production clouds tinted by the stage so dawn flushes it warm and
    night sinks it to a cold moonlit grey."""
    from game.draw import draw_cloud
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    night = _nightf(ctx)
    # Cloud tint tracks the stage horizon so the sea catches the same light as the
    # sky meeting it — warm at dawn, cool blue-grey at night.
    base = ctx.pal.get('cloud_tint', ctx.pal.get('horizon', (236, 238, 244)))
    top = int(gy * 0.60)            # the cloud-sea surface line
    # 1. A solid base sheet so the sea reads as opaque mass, not a few puffs.
    sheet = pygame.Surface((w, gy - top), pygame.SRCALPHA)
    for yy in range(gy - top):
        t = yy / max(1, gy - top)
        # Slightly darker toward the trough so the sea has body.
        c = (int(base[0] * (1 - 0.18 * t)),
             int(base[1] * (1 - 0.18 * t)),
             int(base[2] * (1 - 0.18 * t)))
        a = int(150 + 95 * t)
        pygame.draw.line(sheet, (*c, a), (0, yy), (w, yy))
    surf.blit(sheet, (0, top))
    # 2. Billowing crest of overlapping production clouds along the surface line
    # so the top edge rolls instead of cutting flat. Deterministic layout keyed
    # to width so adjacent stage columns share the same sea.
    import random as _r
    rng = _r.Random(w * 104729)
    n = 9
    for i in range(n):
        cx = int(w * (i + 0.5) / n) + rng.randint(-12, 12)
        cy = top + rng.randint(-6, 10)
        sc = 0.9 + rng.random() * 0.7
        draw_cloud(surf, cx, cy, scale=sc, variant=i % 5)
    # 3. A low second swell of clouds deeper in the sea for layered depth.
    for i in range(n - 2):
        cx = int(w * (i + 1.0) / n) + rng.randint(-10, 10)
        cy = top + int(gy * 0.14) + rng.randint(-4, 8)
        draw_cloud(surf, cx, cy, scale=0.7 + rng.random() * 0.5, variant=(i + 2) % 5)


def draw_cloud_sea_pine(ctx):
    """A lone wuling pine on the nearest peak emerging from the cloud sea — the
    only structure, so the cloud-sea stays the subject."""
    from game.draw import draw_wuling_pine
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    draw_wuling_pine(surf, int(w * 0.30), gy - int(gy * 0.40), 46, ctx.dpal,
                     lean=10, direction='up', layers=5)
    draw_wuling_pine(surf, int(w * 0.24), gy - int(gy * 0.30), 26, ctx.dpal,
                     lean=-5, direction='up', layers=4)


def moon_over(ctx):
    """The moonlit-pine-cliff hero light: a large soft moon disc placed over the
    sky (before the ridges, so the dark cliff silhouette eclipses its lower
    edge). Sits high-left of the play band so it never crowds the HUD/score, and
    rides a faint additive wash so the whole indigo sky reads moonlit. Present
    even at 'day' for this perpetually-nocturnal biome, brightest at true night."""
    from scene_engine import soft_disc
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    night = _nightf(ctx)
    glow = ctx.pal.get('glow_color', (224, 232, 255))
    moon = ctx.pal.get('moon_tint', (236, 240, 250))
    mx, my = int(w * 0.26), int(gy * 0.26)
    r = int(gy * 0.085)
    # A broad low-alpha moon-wash across the upper sky so the indigo feels lit.
    wash = pygame.Surface((w, gy), pygame.SRCALPHA)
    pygame.draw.ellipse(wash, (*glow, int(20 + 30 * night)),
                        pygame.Rect(int(mx - w * 0.5), int(my - gy * 0.4),
                                    w, int(gy * 0.8)))
    surf.blit(wash, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    # The disc itself with its soft halo — the hero light.
    soft_disc(surf, mx, my, r, moon, glow_alpha=int(120 + 80 * night))


def draw_moonlit_pine_cliff_sig(ctx):
    """Night-ink hero: a wuling pine gripping the cliff edge with a raven or two
    riding the dark air beside it. The cliff silhouette + moon carry the drama;
    this is the lonely living mark on the rock."""
    from game.draw import draw_wuling_pine
    from game.pillar_variants import draw_raven
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    # Pine on the near cliff lip — leaning out over the void, classic ink framing.
    draw_wuling_pine(surf, int(w * 0.58), gy - int(gy * 0.42), 52, ctx.dpal,
                     lean=16, direction='up', layers=6)
    draw_wuling_pine(surf, int(w * 0.50), gy - int(gy * 0.30), 30, ctx.dpal,
                     lean=-8, direction='up', layers=4)
    # Ravens crossing the moonlit sky beside the pine.
    draw_raven(surf, int(w * 0.40), int(gy * 0.34))
    draw_raven(surf, int(w * 0.34), int(gy * 0.42))
