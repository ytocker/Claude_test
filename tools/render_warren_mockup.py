"""Look-dev mockup for the "Pagoda Warren" concept.

The corridor is STRUCTURAL: neighbouring pagoda-pillars are packed so tight
that their curved eaves and bodies abut / overlap, fusing the top pagodas
into ONE continuous serrated wall and the bottom pagodas into another. The
only negative space left is the single winding central slot — so the
warren read survives with every highlight turned OFF (see the bottom
"structure check" strip, which renders the route from silhouette alone).

This script renders a candidate sheet — 5 corridor archetypes (rows) x 3
times of day (columns) — and overlays the REAL parrot sprite plus a
parabolic dotted flight path so a reviewer can SEE the corridor is
threadable by a one-button flapper.

The single goal is to prove PASSABILITY: every corridor is generated from a
small set of gap centres, and the asserts below reject any layout that the
real bird physics couldn't fly. No game/ files are touched and no game
state is mutated — we only call the existing draw entry points and pass
locally-tinted copies of the biome palette.

    PYTHONPATH=. python tools/render_warren_mockup.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import (
    W, H, GROUND_Y, PIPE_W, GAP_START, BIRD_R, PIPE_HITBOX_SHRINK,
    FLAP_V, GRAVITY, SCROLL_BASE,
)
from game.biome import palette_for_phase, lerp_color
from game.pillar_pagodas import draw_pillar_pair
from game.parrot import get_parrot


# ── physics-derived passability budget ───────────────────────────────────────
# One flap rises FLAP_V**2 / (2*GRAVITY) px before gravity wins. That is the
# hard ceiling on how much altitude the bird can buy per tap, and it anchors
# every "is this slope flyable" check below.
FLAP_RISE = (FLAP_V * FLAP_V) / (2.0 * GRAVITY)          # ~84 px
EFFECTIVE_R = BIRD_R - PIPE_HITBOX_SHRINK                # forgiven hitbox = 10 px
PARROT_H = 2 * BIRD_R                                    # ~28 px scale ruler

GAP_H_MIN, GAP_H_MAX = 150, 185        # per-pagoda gap height window
DRIFT_MAX = 56                         # per-pagoda gap-centre vertical step
# Spacing is now driven DOWN toward / below the eave span. A pagoda body is
# ~0.94*PIPE_W (~54 px) and each cached tier-eave overhangs ~10-15 px, so the
# painted silhouette is ~78-84 px wide. Centre-to-centre below that forces
# neighbours' eaves to abut / overlap into one fused wall, pooling all sky
# into the single central slot — the corridor becomes carved negative space
# instead of a faked paint ribbon.
SPACING_MIN, SPACING_MAX = 62, 84

# The flight channel must stay a generous, near-constant tube as it winds —
# never pinching below ~2.5 parrot-heights even where neighbours overlap most.
CHANNEL_MIN = int(2.5 * PARROT_H)      # ~70 px clear threadable width

# Keep the threaded corridor off the sky ceiling and off the ground band so
# the parrot always has real estate above and below the path.
CEIL_PAD = 72
FLOOR_PAD = 72
GAP_CY_MIN = CEIL_PAD + GAP_H_MAX // 2
GAP_CY_MAX = GROUND_Y - FLOOR_PAD - GAP_H_MAX // 2


# ── corridor archetypes ──────────────────────────────────────────────────────
# Each returns a list of pagodas: (x_centre, gap_cy, gap_h, seed). x_centre is
# the pillar centre; spacing is tight enough that the eaves of neighbouring
# towers touch, so the union of [gap_cy-gap_h/2, gap_cy+gap_h/2] is the ONLY
# open space — the winding passage. Seeds pick the pagoda variant (seed % 11)
# so each row owns a coherent architectural family.

def _gentle_sine_tube(x0):
    """LEAD design — one smooth rounded tube, the welcoming intro warren.

    Instantly-readable designed route (chevron's clarity) but every apex is
    a soft cosine crest, so the path is a sequence of fair parabolic hops a
    one-button flapper can actually fly. Wide gaps, gentle sweep, fused
    masonry above and below.
    """
    out, x = [], x0
    base = 312
    n = 9
    for i in range(n):
        # Cosine crest gives rounded tops/bottoms (no kinked apex) and the
        # per-step delta stays well under one flap's climb.
        cy = base + math.cos(i * 0.62) * 52        # 52 px sweep < DRIFT_MAX
        out.append((x, cy, 184, 0))                # stupa_canopy family, big gaps
        x += 70
    return out


def _terraced_staircase(x0):
    """Re-cut stepped landings: gap descends to a mid plateau then climbs,
    in fair treads inside one flap. Tight spacing fuses every tread's towers
    into a continuous stepped wall, so the staircase reads from silhouette."""
    out, x = [], x0
    # Each step ≤ DRIFT_MAX and ≤ FLAP_RISE so a single tap buys the climb.
    treads = [248, 248, 300, 300, 352, 352, 300, 300, 248]
    for i, cy in enumerate(treads):
        out.append((x, cy, 174, 3))                # horyuji family
        x += 74
    return out


def _chevron_zigzag(x0):
    """Alternating diagonal designed route — the clearest 'go here' read.
    Apexes are softened by a 1-pagoda landing so the corridor rounds over
    each peak instead of kinking. Tight spacing welds the legs into a single
    saw-tooth wall."""
    out, x = [], x0
    lo, mid, hi = 276, 308, 340               # 64 px swing < drift ceiling
    pattern = [lo, mid, hi, hi, mid, lo, lo, mid, hi]
    for i, cy in enumerate(pattern):
        out.append((x, cy, 168, 5))                # toji family
        x += 76
    return out


def _woven_offset(x0):
    """Re-cut 'braided' as a tightly WOVEN tube — alternating high/low towers
    overlap heavily so their eaves interlace into one wall, while the gap
    centre wanders gently on a single sine so the flight channel stays a
    constant generous width. Parrot gets clear air above and below."""
    out, x = [], x0
    base = 318
    n = 9
    for i in range(n):
        cy = base + math.sin(i * 0.78) * 44        # smooth 44 px wander
        out.append((x, cy, 176, 8))                # baoen family
        x += 66                                    # tightest weave spacing
    return out


def _straight_undulating(x0):
    """Tight near-uniform corridor with a slight wander — the classic
    'thread the needle' tunnel, now built from fully fused masonry."""
    out, x = [], x0
    base = 322
    n = 10
    for i in range(n):
        cy = base + math.sin(i * 1.05) * 26        # shallow 26 px wander
        out.append((x, cy, 168, 10))               # palsangjeon family
        x += 64                                    # snug uniform spacing
    return out


DESIGNS = [
    ("Gentle Sine Tube", _gentle_sine_tube),
    ("Terraced Staircase", _terraced_staircase),
    ("Chevron Zig-Zag", _chevron_zigzag),
    ("Woven Offset", _woven_offset),
    ("Straight Undulating Tunnel", _straight_undulating),
]

TIMES = [("DAY", 0.05), ("SUNSET", 0.36), ("NIGHT", 0.64)]


# ── passability proof ────────────────────────────────────────────────────────

def assert_passable(name, pagodas):
    """Reject any corridor the real bird physics couldn't fly. Asserts mirror
    the brief's budget exactly so the rendered sheet is provably fair. The
    tighter (fused) spacing means fewer taps between pillars, so the per-step
    climb stays inside one flap and the channel never pinches below the
    minimum threadable width."""
    prev = None
    for i, (x, cy, gap_h, _seed) in enumerate(pagodas):
        assert GAP_H_MIN <= gap_h <= GAP_H_MAX, \
            f"{name}: gap_h {gap_h} outside [{GAP_H_MIN},{GAP_H_MAX}]"
        assert GAP_CY_MIN <= cy <= GAP_CY_MAX, \
            f"{name}: gap centre {cy} too close to ceiling/ground"
        if prev is not None:
            px, pcy, pgap_h, _ = prev
            spacing = x - px
            assert SPACING_MIN <= spacing <= SPACING_MAX, \
                f"{name}: spacing {spacing} outside fused-warren window"
            drift = abs(cy - pcy)
            assert drift <= DRIFT_MAX, \
                f"{name}: drift {drift} > {DRIFT_MAX}"
            # Consecutive gaps must share enough vertical room that the union
            # is one continuous tube the bird never has to leave AND that the
            # narrowest point stays a generous threadable channel.
            top = max(cy - gap_h / 2, pcy - pgap_h / 2)
            bot = min(cy + gap_h / 2, pcy + pgap_h / 2)
            overlap = bot - top
            assert overlap >= CHANNEL_MIN + 2 * EFFECTIVE_R, \
                f"{name}: channel pinch {overlap:.0f}px < " \
                f"{CHANNEL_MIN + 2 * EFFECTIVE_R}px between gaps {i-1}->{i}"
            # The centre-line climb between two pillars must be buyable inside
            # the travel time (spacing / SCROLL_BASE). Tighter spacing yields
            # FEWER taps, so this is the binding constraint now.
            travel_s = spacing / SCROLL_BASE
            taps = max(1, math.floor(travel_s / 0.34))   # ~0.34 s per useful tap
            climb_budget = FLAP_RISE * taps
            rise = max(0.0, pcy - cy)                     # upward demand
            assert rise <= climb_budget, \
                f"{name}: needs {rise:.0f}px climb, budget {climb_budget:.0f}px"
        prev = (x, cy, gap_h, _seed)
    return True


# ── palette shaping per time-of-day ──────────────────────────────────────────
# The corridor must read from the carved silhouette, so we nudge the REAL
# biome palette per phase before handing it to draw_pillar_pair: SUNSET goes
# a value cooler/darker so pale stone doesn't wash into the pink sky; NIGHT
# keeps its moonlit stone (we add an explicit rim-light pass on top).

def _shift(c, dr, dg, db):
    return (max(0, min(255, c[0] + dr)),
            max(0, min(255, c[1] + dg)),
            max(0, min(255, c[2] + db)))


def shaped_palette(phase):
    """A local copy of the biome palette tuned so the carved corridor reads
    at every time of day. Never mutates the cached biome dict."""
    pal = dict(palette_for_phase(phase))
    if 0.30 < phase < 0.45:        # SUNSET — darken + cool the stone
        for k in ('stone_light', 'stone_mid', 'stone_dark', 'stone_accent'):
            r, g, b = pal[k]
            pal[k] = _shift((r, g, b), -28, -14, +8)
    return pal


# ── rendering ────────────────────────────────────────────────────────────────

def draw_sky_ground(surf, w, h, palette):
    """Self-contained vertical sky gradient + ground band, sized to the wide
    strip cell (the cached helpers assume the 360px canvas width)."""
    top = palette['sky_top']
    mid = palette['sky_mid']
    bot = palette['sky_bot']
    for y in range(GROUND_Y):
        t = y / GROUND_Y
        if t < 0.5:
            c = lerp_color(top, mid, t * 2)
        else:
            c = lerp_color(mid, bot, (t - 0.5) * 2)
        pygame.draw.line(surf, c, (0, y), (w, y))
    # Ground band.
    for y in range(GROUND_Y, h):
        t = (y - GROUND_Y) / max(1, h - GROUND_Y)
        c = lerp_color(palette['ground_top'], palette['ground_mid'], t)
        pygame.draw.line(surf, c, (0, y), (w, y))
    # Soft horizon seam so the ground reads as grounded, not pasted.
    pygame.draw.line(surf, palette['ground_top'], (0, GROUND_Y), (w, GROUND_Y))


def _channel_polys(pagodas):
    """Top + bottom rims of the threadable channel, densely sampled along a
    smoothstep so the carved tube has soft parabolic walls (no kinks)."""
    xs = [p[0] for p in pagodas]
    tops = [p[1] - p[2] / 2 + EFFECTIVE_R for p in pagodas]
    bots = [p[1] + p[2] / 2 - EFFECTIVE_R for p in pagodas]
    pts_top, pts_bot = [], []
    steps = 12
    for i in range(len(pagodas) - 1):
        for s in range(steps):
            t = s / steps
            tt = t * t * (3 - 2 * t)
            x = xs[i] + (xs[i + 1] - xs[i]) * t
            pts_top.append((x, tops[i] + (tops[i + 1] - tops[i]) * tt))
            pts_bot.append((x, bots[i] + (bots[i + 1] - bots[i]) * tt))
    pts_top.append((xs[-1], tops[-1]))
    pts_bot.append((xs[-1], bots[-1]))
    return pts_top, pts_bot


def draw_corridor_glow(surf, pagodas, phase):
    """Subtle INNER glow that reads as light pooling on the carved channel
    floor — not a pasted ribbon. We feather a soft band hugging the lower
    wall of the slot, brightest near the floor and fading up, so the route
    feels lit from inside the passage. SUNSET gets a cooler tint to separate
    from the warm sky; NIGHT pushes the interior value up so the ROUTE is the
    brightest thing on screen."""
    pts_top, pts_bot = _channel_polys(pagodas)
    band = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)

    # Tint + strength per phase.
    if 0.30 < phase < 0.45:           # SUNSET — cool cyan-white separation
        tint = (200, 235, 245)
        layers = 5
        base_a = 18
    elif 0.55 < phase < 0.75:         # NIGHT — bright moonlit channel floor
        tint = (200, 230, 255)
        layers = 7
        base_a = 26
    else:                              # DAY — gentle warm pooling
        tint = (255, 248, 210)
        layers = 4
        base_a = 14

    # Stack progressively thinner polys hugging the floor: each layer fills
    # from the bottom rim up to a fraction of the channel height, so alpha
    # accumulates toward the floor — an inner glow, not a flat fill.
    for li in range(layers):
        f = (li + 1) / layers            # 1.0 = whole channel, small = near floor
        # Upper edge of this layer rides 'f' of the way up from the floor rim;
        # closing back along the floor rim makes each layer a band that hugs
        # the floor, so stacked alpha brightens toward the channel bottom.
        upper = [(xb, yb + (yt - yb) * f)
                 for (xt, yt), (xb, yb) in zip(pts_top, pts_bot)]
        floor = [(xb, yb) for (xt, yt), (xb, yb)
                 in zip(pts_top[::-1], pts_bot[::-1])]
        poly = upper + floor
        a = base_a if li == layers - 1 else base_a + 6
        if len(poly) >= 3:
            pygame.draw.polygon(band, (*tint, a), poly)
    surf.blit(band, (0, 0))


def draw_rim_light(surf, pagodas, palette):
    """Cool moonlit rim along the carved channel walls — a 2 px lit edge that
    traces the serrated silhouette so the corridor walls read crisply at
    NIGHT instead of dissolving into the dark sky."""
    pts_top, pts_bot = _channel_polys(pagodas)
    rim = palette.get('stone_accent', (200, 225, 255))
    rim = _shift(rim, 0, 6, 20)
    if len(pts_top) >= 2:
        pygame.draw.lines(surf, rim, False,
                          [(int(x), int(y)) for x, y in pts_top], 2)
        pygame.draw.lines(surf, rim, False,
                          [(int(x), int(y)) for x, y in pts_bot], 2)


def draw_flight_path(surf, pagodas):
    """Cyan dotted centre-line — parabolic hops between gap centres so it
    matches what a one-button flapper actually flies. Colourblind-safe cyan
    over a white core, drawn at every time of day."""
    xs = [p[0] for p in pagodas]
    cys = [p[1] for p in pagodas]
    samples = []
    steps = 16
    for i in range(len(pagodas) - 1):
        x0, x1 = xs[i], xs[i + 1]
        y0, y1 = cys[i], cys[i + 1]
        for s in range(steps):
            t = s / steps
            x = x0 + (x1 - x0) * t
            # A real flap is a parabola: rise fast off the tap, ease at the
            # crest, fall under gravity. Blend a smoothstep base with a small
            # parabolic sag so the dotted line reads as a hop, not a ramp.
            tt = t * t * (3 - 2 * t)
            sag = math.sin(t * math.pi) * (-10 if y1 >= y0 else 10) * 0.45
            y = y0 + (y1 - y0) * tt + sag
            samples.append((x, y))
    samples.append((xs[-1], cys[-1]))
    for i, (x, y) in enumerate(samples):
        if i % 2 == 0:
            pygame.draw.circle(surf, (240, 255, 255), (int(x), int(y)), 3)
            pygame.draw.circle(surf, (0, 200, 230), (int(x), int(y)), 2)


def _path_y_at(pagodas, bx):
    """Smoothstep-interpolated channel-centre y at world x — used to seat the
    parrot ON the flight line with clear air above and below."""
    xs = [p[0] for p in pagodas]
    cys = [p[1] for p in pagodas]
    for i in range(len(pagodas) - 1):
        if xs[i] <= bx <= xs[i + 1]:
            t = (bx - xs[i]) / (xs[i + 1] - xs[i])
            tt = t * t * (3 - 2 * t)
            return cys[i] + (cys[i + 1] - cys[i]) * tt
    return cys[-1]


def render_cell(cell_w, cell_h, design_fn, phase, *, highlight=True):
    """One gameplay strip: sky/ground + fused pagoda walls + (optional) carved
    inner glow + parabolic dotted path + the real parrot threading the slot.

    `highlight=False` is the structure-check mode: glow, rim-light and path
    are suppressed so the corridor must read from silhouette alone."""
    palette = shaped_palette(phase)
    is_night = 0.55 < phase < 0.75
    surf = pygame.Surface((cell_w, cell_h))
    draw_sky_ground(surf, cell_w, cell_h, palette)

    # First pagoda offset in from the left so the warren reads as on-screen.
    pagodas = design_fn(64)
    assert_passable(design_fn.__name__, pagodas)

    for idx, (x, cy, gap_h, seed) in enumerate(pagodas):
        top_h = cy - gap_h / 2
        bot_y = cy + gap_h / 2
        top_rect = pygame.Rect(int(x - PIPE_W / 2), 0, PIPE_W, int(top_h))
        bot_rect = pygame.Rect(int(x - PIPE_W / 2), int(bot_y),
                               PIPE_W, int(GROUND_Y - bot_y))
        draw_pillar_pair(surf, top_rect, bot_rect, palette, seed,
                         phase=phase, is_rush=False, pillar_index=idx + 1)

    if highlight:
        draw_corridor_glow(surf, pagodas, phase)
        if is_night:
            draw_rim_light(surf, pagodas, palette)
        draw_flight_path(surf, pagodas)

    # Parrot seated ON the path near mid-corridor, with deliberate clear
    # daylight above and below it so it reads as a scale ruler with room to
    # manoeuvre. We pick a pillar whose gap is roomy and centre the bird in it.
    px_idx = len(pagodas) // 2
    bx = (pagodas[px_idx][0] + pagodas[px_idx + 1][0]) / 2 \
        if px_idx + 1 < len(pagodas) else pagodas[px_idx][0]
    by = _path_y_at(pagodas, bx)
    if highlight:
        nxt = _path_y_at(pagodas, bx + 24)
        tilt = -12 if nxt > by else 12
        bird = get_parrot(1, tilt)
        surf.blit(bird, (int(bx - bird.get_width() / 2),
                         int(by - bird.get_height() / 2)))
    return surf


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((W, H))   # video context for convert/blit paths

    CELL_W, CELL_H = 960, 640
    SCALE = 0.42                      # shrink wide strips into a tidy grid
    sw, sh = int(CELL_W * SCALE), int(CELL_H * SCALE)
    # The structure-check strip uses smaller tiles so it stays a compact band.
    cw, ch = int(sw * 0.78), int(sh * 0.78)

    cols = len(TIMES)
    rows = len(DESIGNS)
    PAD = 22
    GAP = 12
    ROW_LBL = 150     # left gutter for design names
    COL_LBL = 26
    TITLE_H = 46
    STRIP_GAP = 30    # breathing room before the structure-check band
    STRIP_LBL = 24

    grid_h = rows * sh + (rows - 1) * GAP
    strip_h = STRIP_LBL + ch

    canvas_w = ROW_LBL + cols * sw + (cols - 1) * GAP + PAD * 2
    canvas_h = (TITLE_H + COL_LBL + grid_h + STRIP_GAP + strip_h + PAD * 2)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((22, 24, 32))

    f_title = pygame.font.SysFont(None, 36, bold=True)
    f_col = pygame.font.SysFont(None, 24, bold=True)
    f_row = pygame.font.SysFont(None, 22, bold=True)
    f_strip = pygame.font.SysFont(None, 26, bold=True)
    f_cap = pygame.font.SysFont(None, 18, bold=True)

    title = f_title.render(
        "PAGODA WARREN — fused-masonry corridor look-dev", True,
        (240, 240, 245))
    canvas.blit(title, (PAD, PAD - 4))

    x0 = PAD + ROW_LBL
    y0 = PAD + TITLE_H + COL_LBL

    for c, (tname, _phase) in enumerate(TIMES):
        cx = x0 + c * (sw + GAP)
        lbl = f_col.render(tname, True, (210, 215, 225))
        canvas.blit(lbl, (cx + (sw - lbl.get_width()) // 2,
                          y0 - COL_LBL + 2))

    for r, (dname, design_fn) in enumerate(DESIGNS):
        ry = y0 + r * (sh + GAP)
        # design name in the left gutter, vertically centred on the row
        for li, line in enumerate(_wrap(dname, 14)):
            lbl = f_row.render(line, True, (235, 225, 160))
            canvas.blit(lbl, (PAD, ry + sh // 2 - 12 + li * 18))
        for c, (tname, phase) in enumerate(TIMES):
            cell = render_cell(CELL_W, CELL_H, design_fn, phase)
            scaled = pygame.transform.smoothscale(cell, (sw, sh))
            cx = x0 + c * (sw + GAP)
            pygame.draw.rect(canvas, (70, 78, 100),
                             pygame.Rect(cx - 1, ry - 1, sw + 2, sh + 2), 1)
            canvas.blit(scaled, (cx, ry))

    # ── structure-check strip — DAY, highlight OFF ──────────────────────────
    # Proves the winding route reads from the carved silhouette alone: no
    # glow, no rim-light, no dotted path, no parrot.
    strip_y = y0 + grid_h + STRIP_GAP
    strip_lbl = f_strip.render("STRUCTURE CHECK — highlight off (DAY)", True,
                               (255, 210, 150))
    canvas.blit(strip_lbl, (PAD, strip_y))
    sy = strip_y + STRIP_LBL
    strip_x0 = PAD + ROW_LBL
    day_phase = TIMES[0][1]
    for r, (dname, design_fn) in enumerate(DESIGNS):
        scol = strip_x0 + r * (cw + GAP)
        if scol + cw > canvas_w - PAD:
            break
        cell = render_cell(CELL_W, CELL_H, design_fn, day_phase,
                           highlight=False)
        scaled = pygame.transform.smoothscale(cell, (cw, ch))
        pygame.draw.rect(canvas, (70, 78, 100),
                         pygame.Rect(scol - 1, sy - 1, cw + 2, ch + 2), 1)
        canvas.blit(scaled, (scol, sy))
        cap = f_cap.render(dname[:16], True, (200, 205, 215))
        canvas.blit(cap, (scol + (cw - cap.get_width()) // 2, sy + ch + 2))

    out_dir = os.path.join("docs", "pagoda_warren")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")
    print("all passability asserts passed")


def _wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


if __name__ == "__main__":
    main()
