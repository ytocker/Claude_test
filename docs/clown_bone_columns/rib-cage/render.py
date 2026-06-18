"""
Round-1 concept renderer for the RIB-CAGE HYBRID clown-event bone column.

WHY this column: half built monument, half skeletal anatomy. A CONTINUOUS
spine rope (not beaded) runs the shaft; paired curving ribs arc out to the
58px column edge in repeating bands; each half is capped at Pip's gap by the
locked Asthi-Dakini SWITCHED+BIG focal (faceted cyan cut-gem third-eye in a
gold ring, white-hot core, warm-ivory skull).

CRITICAL distinctness fix (per art-director): the column most at risk of
reading as the skewer at 58px. So the ribs are BOLD + GROUPED into clusters
(3 ribs, gap, 3 ribs) that read as chunks of mass, NOT an even fishbone
texture, and the rib arcs are WIDENED so they actually reach the full
PIPE_W=58px edges and fill the column with mass rather than a hairline spine.
The ribs must survive the downscale as readable curved mass.

House grammar (bone roster): warm-ivory bone, hard 1-2px ink keyline (28,22,30),
dark-core -> flat-fill -> top-left rim-sheen triad, gold thin-accent tracing,
faceted cyan wisdom gem, supersample->smoothscale + alpha-grown 1px silhouette
outline. Borrows the Citipati spine grammar + the locked Asthi gem-eye focal.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math inline, not runtime sprite modules.
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

PIPE_W = 58

_FONT_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "game", "assets", "LiberationSans-Bold.ttf"))


def font(sz):
    if os.path.exists(_FONT_PATH):
        return pygame.font.Font(_FONT_PATH, sz)
    return pygame.font.SysFont("DejaVu Sans", sz, bold=True)


# ── PINNED PALETTE (locked Asthi bone-roster house style) ─────────────────────
BONE      = (212, 202, 186)   # warm aged ivory-bone (dominant light field)
BONE_D    = (158, 148, 130)   # bone shade / mid-core
BONE_DD   = ( 96,  88,  76)   # deepest bone hollow
BONE_SH   = (240, 234, 222)   # bone top-left rim-sheen (warm near-white)
CYAN      = ( 86, 214, 226)
CYAN_BR   = (188, 248, 252)
CYAN_D    = ( 40, 132, 150)
GOLD      = (212, 162,  60)   # warm gold thin-accent tracing
GOLD_BR   = (246, 208, 110)
GOLD_D    = (158, 112,  40)
INK       = ( 28,  22,  30)   # hard ink keyline (bone-roster house ink)

BG        = ( 92,  96, 108)
PANEL     = ( 70,  74,  86)
DAY_SKY_T = (120, 196, 236)
DAY_SKY_B = (196, 232, 244)
LABEL     = (238, 240, 246)
LABEL_DIM = (190, 198, 212)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# ── outline grown from the alpha mask (the house keyline) ────────────────────
def grow_outline(surf, color, px):
    mask = pygame.mask.from_surface(surf)
    pts = mask.outline()
    if len(pts) < 2:
        return surf
    base = surf.copy()
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(base, (0, 0))
    return ring


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, ow=2):
    pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.4), sheen_pts)
    pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.4),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, lerp(color, (255, 255, 255), 0.45),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


# ── a FACETED cyan cut-stone GEM — the locked Asthi third-eye focal ───────────
def cyan_gem(surf, c, r, s, focal=False, bg=None, hot=None):
    """A CUT cyan jewel built from FLAT FACET PLANES (a facet rosette): a flat
    angular octagonal TABLE at the crown, ringed by crown facets in stepped cyan
    values meeting at sharp corners. `focal` (the third-eye) alone gets the
    white-hot core + extra glints. Lifted faithfully from the locked Asthi
    SWITCHED+BIG render so the focal matches exactly."""
    cx, cy = int(c[0]), int(c[1])
    show_bg = (not focal) if bg is None else bg
    show_hot = focal if hot is None else hot
    if show_bg:
        pygame.draw.circle(surf, INK, (cx, cy), r + max(1, int(1.4 * s)))

    def gpt(ang_deg, rad):
        a = math.radians(ang_deg)
        return (cx + math.cos(a) * rad, cy + math.sin(a) * rad)
    n_crown = 8
    girdle = [gpt(-90 + i * (360 / n_crown), r) for i in range(n_crown)]
    pygame.draw.polygon(surf, CYAN_D, girdle)

    table_r = r * 0.46
    tcx, tcy = cx, cy - int(r * 0.10)
    table = [(tcx + math.cos(math.radians(-90 + i * (360 / n_crown))) * table_r,
              tcy + math.sin(math.radians(-90 + i * (360 / n_crown))) * table_r)
             for i in range(n_crown)]

    for i in range(n_crown):
        g0, g1 = girdle[i], girdle[(i + 1) % n_crown]
        t0, t1 = table[i], table[(i + 1) % n_crown]
        mx = (g0[0] + g1[0]) * 0.5 - cx
        my = (g0[1] + g1[1]) * 0.5 - cy
        facing = -(mx * 0.7 + my * 0.7) / max(1.0, r)
        if facing > 0.35:
            fc = CYAN_BR
        elif facing > -0.15:
            fc = CYAN
        else:
            fc = lerp(CYAN, CYAN_D, 0.6)
        pygame.draw.polygon(surf, fc, [g0, g1, t1, t0])
        pygame.draw.polygon(surf, INK, [g0, g1, t1, t0], max(1, int(0.9 * s)))

    pygame.draw.polygon(surf, lerp(CYAN, CYAN_BR, 0.55), table)
    pygame.draw.polygon(surf, INK, table, max(1, int(0.9 * s)))
    pygame.draw.line(surf, CYAN_BR, table[0], table[n_crown // 2], max(1, int(0.8 * s)))

    def glint(px, py, sz):
        pygame.draw.polygon(surf, (255, 255, 255),
                            [(px, py - sz), (px + sz, py + sz * 0.5),
                             (px - sz, py + sz * 0.5)])

    g = max(1, int(r * 0.16))
    glint(table[6][0], table[6][1], g)
    if show_hot:
        pygame.draw.polygon(surf, CYAN_BR,
                            [(tcx, tcy - int(r * 0.22)), (tcx + int(r * 0.20), tcy),
                             (tcx, tcy + int(r * 0.20)), (tcx - int(r * 0.20), tcy)])
        pygame.draw.circle(surf, (240, 255, 255), (tcx, tcy), max(2, int(r * 0.15)))
        pygame.draw.circle(surf, (255, 255, 255), (tcx - int(r * 0.04), tcy - int(r * 0.04)),
                           max(1, int(r * 0.08)))
        glint(girdle[1][0], girdle[1][1], max(1, int(r * 0.12)))
        glint(table[3][0], table[3][1], max(1, int(r * 0.11)))


# ── the Asthi gem-eye/gold-ring focal skull (capping each half at the gap) ────
def asthi_skull(surf, cx, cy, r, s, facing_down=True):
    """The locked Asthi SWITCHED+BIG head: warm-ivory cranium with a faceted cyan
    third-eye (white-hot core) seated in a GOLD RING at the brow, two deep cyan-lit
    sockets, nasal pit, tooth row. `facing_down`/up orients the jaw so each half's
    cap stares INTO the gap toward Pip. The single brightest pixel of the whole
    column lives in this gem so the eye lands at the gap, never on the shaft."""
    ow1 = max(2, int(2.0 * s))
    ow_thin = max(1, int(1.2 * s))
    flip = 1 if facing_down else -1

    # cranium dome (jaw points toward the gap) — an ink-keyed bone polygon.
    dome = []
    for ang_deg in range(-180, 1, 16):
        a = math.radians(ang_deg)
        dome.append((cx + math.cos(a) * r * 1.06, cy - flip * math.sin(a) * r * 1.12))
    dome.append((cx + r * 0.80, cy + flip * r * 0.40))
    dome.append((cx + r * 0.52, cy + flip * r * 0.86))
    dome.append((cx - r * 0.52, cy + flip * r * 0.86))
    dome.append((cx - r * 0.80, cy + flip * r * 0.40))
    triad_blob(surf, BONE, [(int(x), int(y)) for x, y in dome], ow=ow1)

    # top-left bone sheen wedge (the triad highlight)
    sheen = [(cx - r * 0.66, cy - flip * r * 0.34),
             (cx - r * 0.14, cy - flip * r * 0.82),
             (cx - r * 0.04, cy - flip * r * 0.44),
             (cx - r * 0.52, cy - flip * r * 0.04)]
    pygame.draw.polygon(surf, BONE_SH, [(int(x), int(y)) for x, y in sheen])

    # cranial suture median line (the carved-bone read)
    pygame.draw.line(surf, BONE_DD, (int(cx), int(cy - flip * r * 0.86)),
                     (int(cx), int(cy - flip * r * 0.18)), ow_thin)

    # deep ink sockets with carved bone rims, dim cyan-lit pupils
    socket_r = r * 0.30
    for sgn in (-1, 1):
        ex = int(cx + sgn * r * 0.42)
        ey = int(cy + flip * r * 0.14)
        pygame.draw.circle(surf, BONE_D, (ex, ey), int(socket_r + max(1, 1.4 * s)))
        pygame.draw.circle(surf, INK, (ex, ey), int(socket_r))
        pygame.draw.circle(surf, CYAN_D, (ex, ey), int(socket_r * 0.46))

    # nasal pit
    pygame.draw.polygon(surf, INK, [
        (int(cx), int(cy + flip * r * 0.40)),
        (int(cx - r * 0.13), int(cy + flip * r * 0.66)),
        (int(cx + r * 0.13), int(cy + flip * r * 0.66))])

    # tooth row — short jaw bar with slits, facing the gap
    ty = cy + flip * r * 0.74
    pygame.draw.line(surf, INK, (int(cx - r * 0.36), int(ty)),
                     (int(cx + r * 0.36), int(ty)), max(2, int(1.6 * s)))
    for j in range(5):
        tx = int(cx - r * 0.30 + j * (r * 0.60 / 4))
        pygame.draw.line(surf, INK, (tx, int(ty - flip * r * 0.02)),
                         (tx, int(ty + flip * r * 0.16)), max(1, int(1.2 * s)))

    # ── the GOLD RING bezel + faceted cyan THIRD-EYE at the brow (the focal) ──
    bx, by = int(cx), int(cy - flip * r * 0.40)
    gem_r = int(r * 0.42)
    ring_r = gem_r + max(2, int(3.2 * s))
    pygame.draw.circle(surf, GOLD_D, (bx, by), ring_r + max(1, int(1.0 * s)))
    pygame.draw.circle(surf, GOLD, (bx, by), ring_r)
    pygame.draw.circle(surf, GOLD_BR, (bx - int(ring_r * 0.30), by - int(ring_r * 0.34)),
                       max(1, int(ring_r * 0.22)))
    pygame.draw.circle(surf, INK, (bx, by), gem_r + max(1, int(1.0 * s)))
    cyan_gem(surf, (bx, by), gem_r, s, focal=True, bg=False, hot=True)


# ── ONE rib pair — a bold curving bone arc reaching the column edge ───────────
def rib_pair(surf, spine_x, y, half_w, droop, th, s, sheen=True):
    """A SINGLE bold rib band: two mirrored arcs springing from the spine and
    sweeping out + down to the column edge, ink-keyed bone with a top sheen and a
    thin gold cap-trace at the tip. WHY filled-quad arcs, not pygame.draw.arc: a
    drawn arc is a hairline that dissolves at 58px — these are MASS, a tapering
    bone wedge per side that holds curved volume through the downscale. `half_w`
    pushes the tip to the full column edge; `droop` sets the downward sweep so
    the band reads as an anatomical rib, not a horizontal ladder rung."""
    ow = max(1, int(1.6 * s))
    for sgn in (-1, 1):
        # sample a quadratic-ish arc from spine -> edge, drooping down
        n = 9
        spine_th = th * 1.15
        tip_th = th * 0.5
        top, bot = [], []
        for i in range(n + 1):
            t = i / n
            # ease the horizontal so ribs cluster mass near the spine then sweep
            ex = spine_x + sgn * half_w * (t ** 0.78)
            ey = y + droop * (t * t)
            # local tangent to set band thickness perpendicular
            t2 = min(1.0, t + 0.06)
            ex2 = spine_x + sgn * half_w * (t2 ** 0.78)
            ey2 = y + droop * (t2 * t2)
            dx, dy = ex2 - ex, ey2 - ey
            L = max(1.0, math.hypot(dx, dy))
            nx, ny = -dy / L, dx / L
            w = (spine_th * (1 - t) + tip_th * t) * 0.5
            top.append((ex + nx * w, ey + ny * w))
            bot.append((ex - nx * w, ey - ny * w))
        poly = top + bot[::-1]
        ipoly = [(int(x), int(y)) for x, y in poly]
        pygame.draw.polygon(surf, INK, ipoly)
        pygame.draw.polygon(surf, BONE, ipoly)
        # dark-core underside (the lower edge of the rib reads in shadow)
        core = [(int(x), int(y)) for x, y in bot]
        if len(core) >= 3:
            core_band = bot + [(top[i][0], top[i][1]) for i in
                               range(len(top) - 1, -1, -1)][:0]
        # underside shade strip
        shade = [(bot[i][0], bot[i][1]) for i in range(len(bot))]
        shade += [(bot[i][0], bot[i][1] - th * 0.30) for i in range(len(bot) - 1, -1, -1)]
        pygame.draw.polygon(surf, BONE_D, [(int(x), int(y)) for x, y in shade])
        # top sheen strip (top-left lit)
        if sheen:
            sh = [(top[i][0], top[i][1]) for i in range(len(top))]
            sh += [(top[i][0], top[i][1] + th * 0.26) for i in range(len(top) - 1, -1, -1)]
            pygame.draw.polygon(surf, BONE_SH, [(int(x), int(y)) for x, y in sh])
        pygame.draw.polygon(surf, INK, ipoly, ow)
        # thin gold cap-trace at the rib tip (the monument accent)
        tipx, tipy = top[-1], bot[-1]
        pygame.draw.line(surf, GOLD, (int(tipx[0]), int(tipx[1])),
                         (int(tipy[0]), int(tipy[1])), max(1, int(1.4 * s)))


# ── the continuous spine rope (NOT beaded) ────────────────────────────────────
def spine_rope(surf, x, y0, y1, th, s):
    """A CONTINUOUS bone spine rope down the shaft — a solid ink-keyed bone
    column, NOT a bead chain. WHY continuous: the brief's distinctness hinges on
    the spine reading as one unbroken built-monument core that the rib clusters
    spring from; a beaded spine would re-read as the skewer concept. Vertebra
    seams are SHALLOW notches carved into the one rope, not gaps between beads."""
    ow = max(2, int(1.8 * s))
    half = th // 2
    pygame.draw.rect(surf, INK, (int(x - half - ow), int(y0), int(th + 2 * ow), int(y1 - y0)))
    pygame.draw.rect(surf, BONE, (int(x - half), int(y0), int(th), int(y1 - y0)))
    # dark-core right side
    pygame.draw.rect(surf, BONE_D, (int(x + half * 0.10), int(y0), int(half * 0.9), int(y1 - y0)))
    # top-left sheen
    pygame.draw.rect(surf, BONE_SH, (int(x - half + ow), int(y0), max(1, int(half * 0.42)), int(y1 - y0)))
    pygame.draw.line(surf, INK, (int(x - half), int(y0)), (int(x - half), int(y1)), ow)
    pygame.draw.line(surf, INK, (int(x + half), int(y0)), (int(x + half), int(y1)), ow)
    # shallow vertebra seam notches carved across the rope (NOT bead gaps)
    seam = int(13 * s)
    yy = int(y0 + seam * 0.5)
    while yy < y1:
        pygame.draw.line(surf, BONE_DD, (int(x - half + ow), yy), (int(x + half - ow), yy),
                         max(1, int(1.4 * s)))
        pygame.draw.line(surf, BONE_SH, (int(x - half + ow), yy + max(1, int(1.4 * s))),
                         (int(x + half - ow), yy + max(1, int(1.4 * s))), max(1, int(1.0 * s)))
        yy += seam


# ── one half of the rib-cage column (top OR bottom) ───────────────────────────
def draw_half(surf, cx, cap_y, shaft_y0, shaft_y1, s, facing_down, w_units):
    """Draw one half: the Asthi focal skull at `cap_y` (the gap edge) + a
    continuous spine rope running the shaft + GROUPED rib clusters. The clusters
    are (3 ribs, gap, 3 ribs, gap, ...) so they read as CHUNKS of mass, not an
    even fishbone texture. Rib `half_w` is pushed near the full half-column so the
    bands fill the 58px width with curved mass."""
    edge = (w_units * 0.5 - 1) * s          # push rib tips to the full half-column
    spine_th = int(12 * s)
    rib_th = int(10.0 * s)

    # spine first (behind ribs)
    spine_rope(surf, cx, shaft_y0, shaft_y1, spine_th, s)

    # GROUPED rib clusters down the shaft. WHY grouped (3 ribs, big gap, 3 ribs):
    # an even rib pitch collapses to the skewer read at 58px; clustering bands
    # tight inside a chunk then leaving a wide empty gap makes the column read as
    # repeating BLOCKS of mass. Within a chunk the three ribs vary slightly in
    # reach (short-long-short) so each cluster has its own bulging silhouette.
    sign = 1 if facing_down else -1          # +1 = shaft runs below the cap
    tight = int(13 * s)                      # pitch INSIDE a chunk (ribs near each other)
    chunk_gap = int(30 * s)                  # the wide empty gap BETWEEN chunks
    group = 3
    reach_mul = (0.82, 1.0, 0.82)            # short-long-short bulge per chunk

    # ribs droop AWAY from the cap (toward the far body end) so each band reads
    # as an anatomical rib springing off the spine, not a horizontal rung.
    droop = sign * int(13 * s)

    # walk from just past the cap to the far end, laying chunks
    start = shaft_y0 + sign * tight if sign > 0 else shaft_y1 + sign * tight
    yy = start
    far = shaft_y1 if sign > 0 else shaft_y0
    while (sign > 0 and yy < far - tight) or (sign < 0 and yy > far + tight):
        for k in range(group):
            if (sign > 0 and yy >= far - tight) or (sign < 0 and yy <= far + tight):
                break
            rib_pair(surf, cx, yy, edge * reach_mul[k], droop, rib_th, s)
            yy += sign * tight
        yy += sign * chunk_gap

    # the focal skull caps the half at the gap edge (drawn last → on top)
    skull_r = int(21 * s)
    asthi_skull(surf, cx, cap_y, skull_r, s, facing_down=facing_down)


# ── render one full column (top half + gap + bottom half) at supersample ──────
def render_column(col_h, gap_top, gap_bot, s):
    """Build a full pillar: a top half hanging from the ceiling and a bottom half
    rising from the floor, framing a gap. Returns a downscaled RGBA surface
    PIPE_W*scale_out wide with a grown 1px silhouette outline."""
    margin = 14
    W = (PIPE_W + 2 * margin) * s
    H = col_h * s
    big = pygame.Surface((int(W), int(H)), pygame.SRCALPHA)
    cx = int(W // 2)

    # TOP half: cap (skull) sits at the gap, jaw facing DOWN into the gap; shaft
    # runs UP to the ceiling.
    top_cap_y = gap_top * s - int(4 * s)
    draw_half(big, cx, top_cap_y, 0, top_cap_y - int(18 * s), s,
              facing_down=True, w_units=PIPE_W)

    # BOTTOM half: cap at the gap facing UP; shaft runs DOWN to the floor.
    bot_cap_y = gap_bot * s + int(4 * s)
    draw_half(big, cx, bot_cap_y, bot_cap_y + int(18 * s), H, s,
              facing_down=False, w_units=PIPE_W)

    return big, margin, top_cap_y, bot_cap_y


def downscale(big, out_w):
    src_w = big.get_width()
    scale = out_w / src_w
    out = pygame.transform.smoothscale(
        big, (int(out_w), int(big.get_height() * scale)))
    out = grow_outline(out, INK, 1)
    return out


def downscale_crop(big, out_w, y0_frac, y1_frac):
    """Downscale to `out_w`, then crop a vertical band (fractions of full height)
    so the hero can show the gap region at high zoom without overflowing."""
    out = downscale(big, out_w)
    h = out.get_height()
    y0, y1 = int(h * y0_frac), int(h * y1_frac)
    return out.subsurface((0, y0, out.get_width(), y1 - y0)).copy()


# ── busy day-sky backdrop (to verify the body reads SOLID at 58px) ────────────
def day_sky(w, h):
    sky = pygame.Surface((w, h))
    for yy in range(h):
        sky.fill(lerp(DAY_SKY_T, DAY_SKY_B, yy / max(1, h)), (0, yy, w, 1))
    # busy clutter: clouds + a distant ridge so the silhouette is tested
    import random
    rng = random.Random(7)
    for _ in range(9):
        cxp = rng.randint(0, w)
        cyp = rng.randint(int(h * 0.08), int(h * 0.7))
        for k in range(5):
            r = rng.randint(10, 24)
            c = lerp(DAY_SKY_T, (255, 255, 255), 0.6)
            puff = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(puff, (*c, 150), (r, r), r)
            sky.blit(puff, (cxp + k * 12 - 24, cyp + (k % 2) * 6))
    ridge = lerp(DAY_SKY_B, (120, 170, 110), 0.5)
    pts = [(0, h)]
    for i in range(0, w + 20, 20):
        pts.append((i, int(h * 0.82 + math.sin(i * 0.05) * 10)))
    pts.append((w, h))
    pygame.draw.polygon(sky, ridge, pts)
    return sky


# ── assemble the review sheet ─────────────────────────────────────────────────
def build_sheet():
    SS = 8
    COL_H = 600          # virtual column height (ceiling -> floor span shown)
    GAP_TOP = 270        # gap upper edge (virtual)
    GAP_BOT = 270 + 150  # gap lower edge

    big, _, top_cap_y, bot_cap_y = render_column(COL_H, GAP_TOP, GAP_BOT, SS)
    big_h = big.get_height()

    # the gap region's fractional band (a couple of rib clusters of each half +
    # both focal caps), used for the hero high-zoom slice.
    gap_lo = max(0.0, (top_cap_y - 150 * SS) / big_h)
    gap_hi = min(1.0, (bot_cap_y + 150 * SS) / big_h)

    # HERO: a tall high-zoom slice of the gap region (both caps + clusters).
    hero = downscale_crop(big, (PIPE_W + 28) * 5, gap_lo, gap_hi)
    # 2x detail of the same slice (full clustering rhythm visible)
    mid = downscale_crop(big, (PIPE_W + 28) * 3, gap_lo, gap_hi)
    # gameplay 1x = the FULL column at true scale (the solidity + tiling test)
    gameplay = downscale(big, PIPE_W + 28)
    gp_full_w = gameplay.get_width()
    crop_x = (gp_full_w - PIPE_W) // 2

    # ── layout ──
    SHEET_W, SHEET_H = 1040, 800
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill(BG)

    title = font(30).render("RIB-CAGE HYBRID — clown-event bone column (round 1)",
                            True, LABEL)
    sheet.blit(title, (28, 18))
    sub = font(15).render(
        "continuous spine rope + GROUPED rib clusters (3 ribs · wide gap · 3 ribs) "
        "reaching the full 58px edge · capped at the gap by the locked Asthi gem-eye focal",
        True, LABEL_DIM)
    sheet.blit(sub, (28, 56))

    def panel(x, y, w, h, label):
        pygame.draw.rect(sheet, PANEL, (x, y, w, h), border_radius=8)
        pygame.draw.rect(sheet, lerp(PANEL, INK, 0.4), (x, y, w, h), 2, border_radius=8)
        lab = font(15).render(label, True, LABEL)
        sheet.blit(lab, (x + 12, y + 8))

    PANEL_Y, PANEL_H = 92, 690

    # 1) HERO (left) — gap region, 5x
    hx, hw = 28, 360
    panel(hx, PANEL_Y, hw, PANEL_H, "HERO 5x — gap + clusters + both focal caps")
    hclip = hero
    if hclip.get_height() > PANEL_H - 50:
        sc = (PANEL_H - 50) / hclip.get_height()
        hclip = pygame.transform.smoothscale(
            hclip, (int(hclip.get_width() * sc), PANEL_H - 50))
    sheet.blit(hclip, hclip.get_rect(center=(hx + hw // 2, PANEL_Y + 36 + (PANEL_H - 50) // 2)))

    # 2) 2x detail (center)
    mx, mw = 408, 210
    panel(mx, PANEL_Y, mw, PANEL_H, "3x detail")
    mclip = mid
    if mclip.get_height() > PANEL_H - 50:
        sc = (PANEL_H - 50) / mclip.get_height()
        mclip = pygame.transform.smoothscale(
            mclip, (int(mclip.get_width() * sc), PANEL_H - 50))
    sheet.blit(mclip, mclip.get_rect(center=(mx + mw // 2, PANEL_Y + 36 + (PANEL_H - 50) // 2)))

    # 3) gameplay 1x FULL column over BUSY DAY SKY (right) — the solidity test
    gx, gw = 638, 200
    pygame.draw.rect(sheet, PANEL, (gx, PANEL_Y, gw, PANEL_H), border_radius=8)
    pygame.draw.rect(sheet, lerp(PANEL, INK, 0.4), (gx, PANEL_Y, gw, PANEL_H), 2, border_radius=8)
    sheet.blit(font(15).render("1x (58px) · busy day sky", True, LABEL), (gx + 12, PANEL_Y + 8))
    sky_w, sky_h = gw - 24, PANEL_H - 64
    sky = day_sky(sky_w, sky_h)
    sky_x, sky_y = gx + 12, PANEL_Y + 40
    sheet.blit(sky, (sky_x, sky_y))
    gp_crop = gameplay.subsurface((crop_x, 0, PIPE_W, gameplay.get_height())).copy()
    gpc = gp_crop
    if gpc.get_height() > sky_h:
        sc = sky_h / gpc.get_height()
        gpc = pygame.transform.smoothscale(gpc, (int(gpc.get_width() * sc), sky_h))
    sheet.blit(gpc, gpc.get_rect(center=(sky_x + sky_w // 2, sky_y + sky_h // 2)))
    cap = font(13).render("← 58px →", True, LABEL_DIM)
    sheet.blit(cap, (gx + gw // 2 - cap.get_width() // 2, PANEL_Y + PANEL_H - 22))

    # 4) far-right: focal close-up + notes
    fx, fw = 858, 156
    panel(fx, PANEL_Y, fw, PANEL_H, "focal")
    fbig = pygame.Surface((240, 240), pygame.SRCALPHA)
    asthi_skull(fbig, 120, 110, 76, 3.4, facing_down=True)
    fsm = grow_outline(pygame.transform.smoothscale(fbig, (132, 132)), INK, 1)
    sheet.blit(fsm, (fx + (fw - 132) // 2, PANEL_Y + 44))
    note = [
        "Asthi SWITCHED",
        "+BIG focal:",
        "faceted cyan",
        "third-eye, white-",
        "hot core, in a",
        "GOLD RING —",
        "the single",
        "brightest point.",
        "",
        "Spine rope is",
        "CONTINUOUS,",
        "not beaded.",
        "",
        "Tiles by repeat-",
        "ing the rib-band",
        "cluster.",
    ]
    ny = PANEL_Y + 188
    for ln in note:
        sheet.blit(font(14).render(ln, True, LABEL_DIM), (fx + 12, ny))
        ny += 19

    return sheet


if __name__ == "__main__":
    sheet = build_sheet()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)
