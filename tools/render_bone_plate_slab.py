"""Round-1 render for the FUSED BONE-PLATE SLAB clown-event column.

The 5th column logic: an honestly SOLID fortress wall built from tessellated
cranial plates / jammed-together skulls — a charnel WALL, not a stack. No tier
rhythm, no taper: an unbroken mortared mass with thin gold seams tracing the
tessellation, capped at Pip's gap by one oversized boss-skull KEYSTONE.

Distinct from the stupa (no separable tiers), from the candle (hard-edged
geometric, not slumped), and the unambiguously-solid mass of the set. Built in
the locked bone-roster idiom (warm-ivory bone, ink keyline, dark-core/flat/
rim-sheen triad, gold thin-accent seams, sparing faceted cyan/purple gems) and
supersampled → smoothscaled with an alpha-grown 1px silhouette outline.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import math
import random
import pygame

pygame.init()

# Bone-roster palette (the locked batch2 house style this set inherits).
INK     = (28, 22, 30)
BONE    = (228, 222, 206)
BONE_DK = (150, 144, 128)
BONE_HI = (250, 247, 236)
MORTAR  = (84, 76, 70)          # the recessed grout in the deepest seam cores
GOLD    = (250, 205, 72)
GOLD_HI = (255, 236, 150)
GOLD_DK = (176, 130, 30)
CYAN    = (120, 214, 222)
CYAN_HI = (224, 252, 252)
PURPLE  = (158, 120, 214)
PURPLE_HI = (224, 200, 252)

PW = 58


def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _grow_outline(surf):
    """Alpha-grown 1px ink silhouette (house finishing pass): dilate the alpha
    mask one ring and paint the new edge ink so the slab carves cleanly out of a
    busy sky regardless of where its plates meet the column edge."""
    mask = pygame.mask.from_surface(surf, 8)
    outline = mask.outline()
    if len(outline) > 1:
        pygame.draw.lines(surf, INK, True, outline, 1)
    return surf


# ── The tessellated cranial-plate pavement ────────────────────────────────────
# A coarse irregular polygon mosaic: a jittered point lattice triangulated into
# fused plates. Coarse on purpose — fine plates collapse at 1x, so the keyline +
# gold seams must carry the tessellation, not interior detail.

def _plate_lattice(x0, x1, y0, y1, step, jitter, rng):
    """A jittered grid of points; alternate rows offset so the cells read as
    irregular jammed plates, not a tidy brick course."""
    cols = max(2, int((x1 - x0) / step) + 1)
    rows = max(2, int((y1 - y0) / step) + 1)
    pts = {}
    for r in range(rows + 1):
        for c in range(cols + 1):
            # Clamp the outer ring to the exact body edge so plates fill the full
            # 58px width edge-to-edge (no inset gutter — it must read SOLID).
            gx = x0 + c * (x1 - x0) / cols
            gy = y0 + r * (y1 - y0) / rows
            on_edge = (c == 0 or c == cols or r == 0 or r == rows)
            jx = 0 if (c == 0 or c == cols) else rng.uniform(-jitter, jitter)
            jy = 0 if (r == 0 or r == rows) else rng.uniform(-jitter, jitter)
            # Stagger interior rows half a cell so quads break into a charnel weave.
            sx = (step * 0.42) if (r % 2 and 0 < c < cols) else 0.0
            pts[(r, c)] = (gx + jx + sx, gy + jy)
    return pts, rows, cols


def _draw_plate(surf, poly, ss, *, rng):
    """One fused cranial plate, triad-lit: ink keyline, flat ivory fill, a
    bottom dark-core band and a top-left rim sheen wedge — the roster recipe
    pushed into an irregular polygon instead of a capsule."""
    ipoly = [(int(p[0]), int(p[1])) for p in poly]
    ys = [p[1] for p in poly]
    xs = [p[0] for p in poly]
    top, bot = min(ys), max(ys)
    left, right = min(xs), max(xs)
    cy = (top + bot) * 0.5

    # Flat ivory body, very slight per-plate tint so the mass reads carved, not flat.
    fill = _shade(BONE, rng.randint(-10, 4))
    pygame.draw.polygon(surf, fill, ipoly)

    # Dark-core: shade the lower portion by overdrawing the plate's bottom half a
    # step darker (clipped to the plate so the seam stays crisp).
    prev = surf.get_clip()
    surf.set_clip(pygame.Rect(left - 1, int(cy), int(right - left) + 2, int(bot - cy) + 2))
    pygame.draw.polygon(surf, _shade(fill, -34), ipoly)
    surf.set_clip(prev)

    # Top-left rim sheen: a short bright stroke along the upper-left edges only.
    n = len(poly)
    for i in range(n):
        a = poly[i]
        b = poly[(i + 1) % n]
        mx, my = (a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5
        if my < cy and mx < (left + right) * 0.5 + (right - left) * 0.15:
            pygame.draw.line(surf, BONE_HI,
                             (int(a[0]), int(a[1])), (int(b[0]), int(b[1])),
                             max(1, int(1.2 * ss)))


def _draw_seams(surf, edges, ss):
    """Trace the tessellation with thin gold seams over a recessed mortar core:
    a dark grout line first (depth), then the gold hairline on top (the focal
    accent that survives downscale and sells 'fused bone-plates')."""
    # Most seams are recessed BONE-SHADOW grout (ivory stays the dominant value);
    # only a SPARSE subset carries the gold hairline so gold reads as a thin
    # tracing accent, not a gilt trellis. Deterministic stride keeps it even.
    for (a, b) in edges:
        pygame.draw.line(surf, _shade(BONE, -56),
                         (int(a[0]), int(a[1])), (int(b[0]), int(b[1])),
                         max(2, int(2.0 * ss)))
        pygame.draw.line(surf, MORTAR,
                         (int(a[0]), int(a[1])), (int(b[0]), int(b[1])),
                         max(1, int(ss)))
    for i, (a, b) in enumerate(edges):
        if i % 3:
            continue
        pygame.draw.line(surf, GOLD_DK,
                         (int(a[0]), int(a[1])), (int(b[0]), int(b[1])),
                         max(1, int(1.4 * ss)))
        pygame.draw.line(surf, GOLD,
                         (int(a[0]), int(a[1])), (int(b[0]), int(b[1])),
                         max(1, int(ss)))


def _gem(surf, cx, cy, r, ss, col, col_hi):
    """A faceted wisdom gem: ink-rimmed kite with a bright top-left facet spark."""
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in pts])
    inner = [(cx, cy - r + ss), (cx + r - ss, cy), (cx, cy + r - ss), (cx - r + ss, cy)]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in inner])
    pygame.draw.line(surf, _shade(col, -50), (int(cx), int(cy)), (int(cx), int(cy + r - ss)), max(1, int(ss)))
    pygame.draw.circle(surf, col_hi, (int(cx - r * 0.3), int(cy - r * 0.3)), max(1, int(r * 0.32)))


def _boss_keystone(surf, cx, cy, R, ss, *, flip):
    """The oversized boss-skull KEYSTONE that caps the slab at Pip's gap: a
    cranium wider than the column plates, gem-eyed, mortared INTO the wall with a
    gold keystone-wedge frame so it reads as set INTO the mass, not perched on it.
    `flip` orients the jaw toward the gap (jaw faces the gap, crown into the wall)."""
    sgn = 1 if not flip else -1     # +1: jaw downward (top half); -1: jaw upward (bottom half)

    # A bone keystone wedge socket framing the boss into the wall, jaw-side wider:
    # an ivory block (so the boss stays seated in the SAME bone mass) with a thin
    # gold outline tracing the wedge — gold stays a hairline accent, not a frame.
    wedge = [
        (cx - R * 1.18, cy - sgn * R * 0.55),
        (cx + R * 1.18, cy - sgn * R * 0.55),
        (cx + R * 0.92, cy + sgn * R * 1.15),
        (cx - R * 0.92, cy + sgn * R * 1.15),
    ]
    pygame.draw.polygon(surf, _shade(BONE, -22), [(int(x), int(y)) for x, y in wedge])
    pygame.draw.polygon(surf, GOLD_DK, [(int(x), int(y)) for x, y in wedge], max(1, int(1.6 * ss)))
    pygame.draw.polygon(surf, GOLD, [(int(x), int(y)) for x, y in wedge], max(1, int(ss)))
    # Bright keystone rim along the wall-side (away from gap) so it seats INTO the slab.
    pygame.draw.line(surf, GOLD_HI,
                     (int(cx - R * 1.16), int(cy - sgn * R * 0.53)),
                     (int(cx + R * 1.16), int(cy - sgn * R * 0.53)), max(1, int(1.4 * ss)))

    # Cranium dome.
    pygame.draw.circle(surf, INK, (int(cx), int(cy)), int(R) + max(1, int(ss)))
    pygame.draw.circle(surf, BONE, (int(cx), int(cy)), int(R))
    # Dark-core lower cranium + top-left dome sheen.
    prev = surf.get_clip()
    surf.set_clip(pygame.Rect(int(cx - R), int(cy), int(2 * R), int(R) + 2))
    pygame.draw.circle(surf, _shade(BONE, -30), (int(cx), int(cy)), int(R))
    surf.set_clip(prev)
    pygame.draw.circle(surf, BONE_HI, (int(cx - R * 0.34), int(cy - R * 0.34)), int(R * 0.34))

    # The cranial-suture seam wandering across the dome in gold (ties it to the wall).
    sut = [(cx - R * 0.7, cy - R * 0.15),
           (cx - R * 0.2, cy - R * 0.5),
           (cx + R * 0.25, cy - R * 0.2),
           (cx + R * 0.72, cy - R * 0.42)]
    pygame.draw.lines(surf, GOLD_DK, False, [(int(x), int(y)) for x, y in sut], max(1, int(1.6 * ss)))
    pygame.draw.lines(surf, GOLD, False, [(int(x), int(y)) for x, y in sut], max(1, int(ss)))

    # Gem eye sockets — the sparing cyan/purple wisdom gems live HERE (keystone only).
    ex = R * 0.46
    ey = cy - sgn * R * 0.02
    for s, col, hi in ((-1, CYAN, CYAN_HI), (1, PURPLE, PURPLE_HI)):
        socket = (int(cx + s * ex), int(ey))
        pygame.draw.circle(surf, INK, socket, int(R * 0.30))
        pygame.draw.circle(surf, _shade(INK, 6), socket, int(R * 0.30), max(1, int(ss)))
        _gem(surf, socket[0], socket[1], int(R * 0.24), ss, col, hi)

    # A small triangular nasal void below the eyes (toward the crown side).
    nz = cy - sgn * R * 0.40
    pygame.draw.polygon(surf, INK, [
        (int(cx), int(nz)),
        (int(cx - R * 0.12), int(nz + sgn * R * 0.22)),
        (int(cx + R * 0.12), int(nz + sgn * R * 0.22)),
    ])

    # The boss JAW — a toothed grin facing the gap, the silhouette tell at scale.
    jy = cy + sgn * R * 0.62
    jaw = pygame.Rect(int(cx - R * 0.78), int(min(jy, jy + sgn * R * 0.6)),
                      int(R * 1.56), int(R * 0.6))
    pygame.draw.rect(surf, INK, jaw.inflate(int(ss), int(ss)), border_radius=int(R * 0.22))
    pygame.draw.rect(surf, BONE, jaw, border_radius=int(R * 0.22))
    pygame.draw.rect(surf, _shade(BONE, -28),
                     (jaw.x, jaw.y + jaw.h // 2, jaw.w, jaw.h // 2),
                     border_radius=int(R * 0.18))
    for i in range(-3, 4):
        tx = int(cx + i * R * 0.22)
        pygame.draw.line(surf, INK, (tx, jaw.y + 1), (tx, jaw.bottom - 1), max(1, int(ss)))


def _build_slab(height_px, ss, *, flip, seed):
    """Render one slab half (top OR bottom) at supersample `ss`, with its boss
    keystone seated at the gap-facing end. Returns the smoothscaled, outlined
    PIPE_W-wide surface."""
    rng = random.Random(seed)
    bw = PW * ss
    H = max(1, int(height_px)) * ss
    surf = pygame.Surface((bw, H), pygame.SRCALPHA)

    x0, x1 = 0, bw
    # The keystone sits at the gap-facing edge. For a TOP half the gap is at the
    # bottom (flip=False here means jaw-down at bottom); for a BOTTOM half the gap
    # is at the top. We reserve a band for the boss and pave the rest with plates.
    boss_R = PW * 0.52 * ss
    boss_band = int(boss_R * 2.1)

    if not flip:
        # TOP half: plates fill from the ceiling down; keystone caps the bottom.
        py0, py1 = 0, H - boss_band
        boss_cy = H - boss_R * 1.05
        boss_flip = False
    else:
        # BOTTOM half: keystone caps the top; plates fill below it to the ground.
        py0, py1 = boss_band, H
        boss_cy = boss_R * 1.05
        boss_flip = True

    # Solid backing fill across the WHOLE body first so any seam jitter never
    # opens a hole to the sky — this is the "honest solid mass" guarantee.
    pygame.draw.rect(surf, _shade(BONE, -18), (0, 0, bw, H))

    # Coarse on purpose: ~22px plates survive the downscale to 58px so the
    # tessellation still reads at 1x instead of mushing into noise.
    step = 22 * ss
    jitter = 4.6 * ss
    pts, rows, cols = _plate_lattice(x0, x1, py0, py1, step, jitter, rng)

    # Build plate polygons by pairing triangles of adjacent lattice cells into
    # quad-ish plates, then collect their edges for the seam pass.
    edges = []
    seen = set()

    def add_edge(a, b):
        key = (min(a, b), max(a, b))
        if key not in seen:
            seen.add(key)
            edges.append((pts[a], pts[b]))

    for r in range(rows):
        for c in range(cols):
            # Two triangles per cell, split on alternating diagonals for irregularity.
            tl, tr = (r, c), (r, c + 1)
            bl, br = (r + 1, c), (r + 1, c + 1)
            if (r + c) % 2 == 0:
                tri_a = [pts[tl], pts[tr], pts[br]]
                tri_b = [pts[tl], pts[br], pts[bl]]
                diag = (tl, br)
            else:
                tri_a = [pts[tl], pts[tr], pts[bl]]
                tri_b = [pts[tr], pts[br], pts[bl]]
                diag = (tr, bl)
            _draw_plate(surf, tri_a, ss, rng=rng)
            _draw_plate(surf, tri_b, ss, rng=rng)
            # Cell border edges + the interior diagonal -> the tessellation seams.
            add_edge(tl, tr)
            add_edge(tr, br)
            add_edge(br, bl)
            add_edge(bl, tl)
            add_edge(*diag)

    _draw_seams(surf, edges, ss)

    # A faint occasional plate-set gem dotting the wall, very sparingly, so the
    # mass reads as a charnel reliquary without rivalling the keystone focal.
    for _ in range(max(1, (rows * cols) // 14)):
        gr = rng.randint(1, rows - 1)
        gc = rng.randint(1, cols - 1)
        gx, gy = pts[(gr, gc)]
        if abs(gy - boss_cy) < boss_band:
            continue
        _gem(surf, gx, gy, int(2.6 * ss), ss,
             CYAN if rng.random() < 0.5 else PURPLE,
             CYAN_HI if rng.random() < 0.5 else PURPLE_HI)

    _boss_keystone(surf, bw // 2, boss_cy, boss_R, ss, flip=boss_flip)

    small = pygame.transform.smoothscale(surf, (PW, max(1, int(height_px))))
    return _grow_outline(small)


# ── Busy day-sky backdrop for the read test ───────────────────────────────────

def _day_sky(w, h):
    sky = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        c = (int(116 + 60 * t), int(186 + 30 * t), int(232 - 20 * t))
        pygame.draw.line(sky, c, (0, y), (w, y))
    # Busy clutter: clouds + a couple of distant ambient shapes so the read test
    # is honest against a real-ish background, not a flat field.
    rng = random.Random(7)
    for _ in range(14):
        cx = rng.randint(0, w)
        cy = rng.randint(int(h * 0.08), int(h * 0.7))
        for k in range(rng.randint(3, 6)):
            r = rng.randint(10, 26)
            pygame.draw.circle(sky, (244, 248, 252),
                               (cx + rng.randint(-22, 22), cy + rng.randint(-6, 6)), r)
    for _ in range(40):
        pygame.draw.circle(sky, (255, 255, 255),
                           (rng.randint(0, w), rng.randint(0, h)), 1)
    return sky


def main():
    SS = 5
    GAP = 150
    TOP_H = 250
    BOT_H = 250

    margin = 28
    # Hero: top + bottom slab framing a gap, at a comfortable ~2.4x view scale so
    # the construction is legible; plus a clean 1x gameplay crop alongside.
    view = 2.4
    col_w = int(PW * view)
    hero_h = int((TOP_H + GAP + BOT_H) * 0.74)

    sheet_w = 720
    sheet_h = hero_h + 120
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((40, 44, 56))

    title_f = pygame.font.SysFont("dejavusans", 19, bold=True)
    sub_f = pygame.font.SysFont("dejavusans", 12)
    sheet.blit(title_f.render("FUSED BONE-PLATE SLAB - round 1", True, (255, 255, 255)), (20, 14))
    sheet.blit(sub_f.render("charnel WALL: tessellated cranial plates, gold seams, one boss-skull keystone - the honestly SOLID column",
                            True, (206, 208, 220)), (20, 38))

    # ── Hero panel: 2.4x top+bottom over busy day sky ────────────────────────
    hero_x = margin
    hero_y = 64
    hero_sky = _day_sky(col_w + 40, hero_h)
    sheet.blit(hero_sky, (hero_x, hero_y))

    top = _build_slab(TOP_H, SS, flip=False, seed=51)
    bot = _build_slab(BOT_H, SS, flip=True, seed=52)
    top_v = pygame.transform.smoothscale(top, (col_w, int(TOP_H * view * 0.74)))
    bot_v = pygame.transform.smoothscale(bot, (col_w, int(BOT_H * view * 0.74)))
    cx_hero = hero_x + 20 + col_w // 2
    sheet.blit(top_v, (cx_hero - col_w // 2, hero_y))
    gap_v = int(GAP * view * 0.74)
    bot_y = hero_y + top_v.get_height() + gap_v
    sheet.blit(bot_v, (cx_hero - col_w // 2, bot_y))

    # Pip's gap marker.
    pip_y = hero_y + top_v.get_height() + gap_v // 2
    pygame.draw.circle(sheet, (250, 196, 60), (cx_hero, pip_y), 9)
    pygame.draw.circle(sheet, INK, (cx_hero, pip_y), 9, 2)
    sheet.blit(sub_f.render("2.4x hero", True, (230, 232, 240)), (hero_x + 4, hero_y + hero_h + 4))

    # ── 1x gameplay-scale crop: true 58px column over the SAME busy sky ──────
    crop_x = hero_x + col_w + 80
    crop_h = TOP_H + GAP + BOT_H
    crop_scale = (sheet_h - 110) / crop_h
    cw = int(crop_h * crop_scale)
    one_sky = _day_sky(PW + 30, crop_h)
    # Composite the true-1x slabs onto the 1x sky, THEN scale the whole strip up
    # for display so the viewer sees exactly the downscaled pixels Pip flies past.
    strip = pygame.Surface((PW + 30, crop_h))
    strip.blit(one_sky, (0, 0))
    sx = 15
    strip.blit(top, (sx, 0))
    strip.blit(bot, (sx, TOP_H + GAP))
    pygame.draw.circle(strip, (250, 196, 60), (sx + PW // 2, TOP_H + GAP // 2), 4)
    pygame.draw.circle(strip, INK, (sx + PW // 2, TOP_H + GAP // 2), 4, 1)
    disp = pygame.transform.scale(strip, (int((PW + 30) * crop_scale), int(crop_h * crop_scale)))
    sheet.blit(disp, (crop_x, hero_y))
    sheet.blit(sub_f.render("1x @ 58px (display-zoomed, real pixels)", True, (230, 232, 240)),
               (crop_x, hero_y + disp.get_height() + 6))

    # ── True-pixel pair, no zoom, on busy sky (the honest read) ──────────────
    truth_x = crop_x + disp.get_width() + 50
    truth_sky = _day_sky(PW + 20, crop_h)
    sheet.blit(truth_sky, (truth_x, hero_y))
    sheet.blit(top, (truth_x + 10, hero_y))
    sheet.blit(bot, (truth_x + 10, hero_y + TOP_H + GAP))
    pygame.draw.circle(sheet, (250, 196, 60),
                       (truth_x + 10 + PW // 2, hero_y + TOP_H + GAP // 2), 4)
    sheet.blit(sub_f.render("1x true", True, (230, 232, 240)), (truth_x, hero_y + crop_h + 6))

    out = "/home/user/skybit/docs/clown_bone_columns/bone-plate-slab/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
