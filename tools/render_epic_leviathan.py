"""Scratch renderer for the `deep-leviathan` epic-boss concept (round 1).

A bloated abyssal whale-GOD dragging itself out of a drowned world: the only
bulbous/organic-blob mass in the boss set, made epic by rounded BULK and
bioluminescence rather than spikes. Headless-safe (SDL_VIDEODRIVER=dummy).

Palette is the locked three-tone brief: abyss blue-black body, jade-green
bioluminescence as the day+night focal (light against dark, so it holds on
either sky without leaning on hue), and pale-flesh barnacle for the bone-crust
mass that catches rim light.

PROP DECISION (proven with a mirrored pillar-fit thumbnail): the signature
prop is NOT a single harpoon. A lone barbed shaft reads generic, and a barbed
TIP can't mirror into a symmetric top/bottom column — the barb would point the
wrong way on the flipped half. Instead the prop is a CHAIN-OF-LURE-STALKS: a
barnacled bone column studded with a rhythmic stack of jade lure-bulbs on
curved stalks. The rhythm (node / lit bulb / gap) is what carries the pillar,
and because every lure arcs OUTWARD off a straight central spine, the column
flips top-to-bottom into a clean mirrored pair with the lit bulbs always
fanning toward the open gap.
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

# ── locked brief palette ─────────────────────────────────────────────────────
ABYSS      = (18, 30, 52)      # abyss blue-black — the body's deep mass
ABYSS_DK   = (10, 18, 34)      # darkest occlusion / under-belly
ABYSS_DKR  = (6, 11, 22)       # deepest core shadow, the maw + belly hollow
ABYSS_HI   = (38, 58, 92)      # lifted top of the dome where ambient catches
ABYSS_RIM  = (58, 86, 128)     # cool wet rim along the crown
JADE       = (72, 236, 176)    # bioluminescent jade — THE focal (light v dark)
JADE_DIM   = (40, 150, 116)    # jade in shadow / stalk cores
JADE_PALE  = (190, 255, 230)   # hottest lure centre, near-white bloom
FLESH      = (200, 196, 184)   # pale-flesh barnacle crust
FLESH_DK   = (132, 128, 118)   # barnacle shade
FLESH_DKR  = (88, 86, 80)      # deepest barnacle occlusion
FLESH_HI   = (238, 236, 228)   # barnacle rim light

DAY_BG  = ((96, 168, 214), (158, 210, 234))   # bright sky → the jade still pops
NIGHT_BG = ((9, 13, 32), (24, 34, 66))         # dark sky → flesh reads, jade glows


def _lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _vgrad(surf, rect, top, bot):
    x, y, w, h = rect
    for i in range(h):
        pygame.draw.line(surf, _lerp(top, bot, i / max(1, h - 1)),
                         (x, y + i), (x + w - 1, y + i))


def _glow(surf, cx, cy, r, color, alpha=150, falloff=2.4):
    """Additive radial bloom — jade lures read as LIGHT, not paint. Rings are
    drawn onto a scratch surface with per-ring MAX (not additive) so the centre
    can't saturate to a solid disc; only the final composite is blitted ADD, so
    a big halo stays a soft falloff rather than a hard ball."""
    if r < 1:
        return
    g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    for rr in range(r, 0, -1):
        t = (rr / r) ** falloff
        a = int(alpha * (1 - t))
        pygame.draw.circle(g, (*color, max(0, a)), (r + 1, r + 1), rr)
    surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


# ── shaded blob primitive: the wet rounded bulk ──────────────────────────────

def _wet_dome(surf, cx, cy, rw, rh):
    """A bottom-heavy water-logged dome rendered as nested ellipses so the mass
    reads as ROUND wet bulk, not a flat cut-out. Dark occluded belly, mid body,
    a lifted ambient crown and a thin cool rim down the top edge — the value
    ramp is what sells 'epic rounded GOD' instead of 'cauldron'."""
    # Deepest belly hollow first (slung low + forward of centre).
    pygame.draw.ellipse(surf, ABYSS_DKR,
                        (cx - rw, cy - rh + int(rh * 0.12), rw * 2, rh * 2))
    pygame.draw.ellipse(surf, ABYSS_DK,
                        (cx - rw + 3, cy - rh, rw * 2 - 6, rh * 2 - 4))
    pygame.draw.ellipse(surf, ABYSS,
                        (cx - rw + 8, cy - rh - 2, rw * 2 - 16, int(rh * 1.7)))
    # Ambient sky-catch on the upper third only — the round read.
    crown = pygame.Surface((rw * 2, rh * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(crown, (*ABYSS_HI, 200),
                        (10, -int(rh * 0.10), rw * 2 - 20, int(rh * 0.92)))
    pygame.draw.ellipse(crown, (*ABYSS_RIM, 150),
                        (16, -int(rh * 0.14), rw * 2 - 32, int(rh * 0.46)))
    surf.blit(crown, (cx - rw, cy - rh))
    # A thin bright wet rim hugging the very top arc — catches sky on both skies.
    rim = pygame.Surface((rw * 2, rh), pygame.SRCALPHA)
    pygame.draw.arc(rim, (*ABYSS_RIM, 220),
                    (4, 2, rw * 2 - 8, rh * 2 - 4), 0.55, math.pi - 0.35, 2)
    surf.blit(rim, (cx - rw, cy - rh))


# ── barnacle crust primitive (shared by body back + lure column) ─────────────

def _barnacle(surf, cx, cy, r):
    """A pale conical barnacle: a stacked volcano-ring of calcified bone-crust
    with a dark open maw, rim-lit top-left so the flesh tone catches light on a
    dark sky. Reads as a fused shell cluster, not a flat dot."""
    pygame.draw.ellipse(surf, FLESH_DKR, (cx - r, cy - r + r // 3, r * 2, r * 2 - r // 2))
    pygame.draw.circle(surf, FLESH_DK, (cx, cy), r)
    pygame.draw.circle(surf, FLESH, (cx, cy), max(1, r - 1))
    pygame.draw.arc(surf, FLESH_HI,
                    (cx - r + 1, cy - r + 1, r * 2 - 2, r * 2 - 2),
                    0.5, 2.3, max(1, r // 3))
    pygame.draw.circle(surf, ABYSS_DKR, (cx, cy), max(1, r - 2))  # open maw


def _lure(surf, cx, cy, r, pulse=1.0):
    """A single bioluminescent lure-bulb: jade core + layered additive halo.
    `pulse` scales the outer bloom so a column reads as a living, breathing
    chain. The hot near-white centre is the focal that survives on both skies."""
    _glow(surf, cx, cy, int(r * 4.6 * pulse), JADE, alpha=85)
    _glow(surf, cx, cy, int(r * 2.2), JADE_PALE, alpha=110)
    pygame.draw.circle(surf, JADE_DIM, (cx, cy), r + 1)
    pygame.draw.circle(surf, JADE, (cx, cy), r)
    pygame.draw.circle(surf, JADE_PALE, (cx - max(1, r // 3), cy - max(1, r // 3)),
                       max(1, r // 2))


# ── THE CREATURE ─────────────────────────────────────────────────────────────

def draw_leviathan(surf, cx, base_y, scale=1.0, t=0.0):
    """The abyssal whale-GOD, facing left, hauling itself onto the ground line at
    `base_y`. Built bottom-heavy: a vast wet rounded dome of abyss-mass slung
    low, a HARD predatory underbite of interlocking barnacle fangs, a sunken
    dead-jade slit eye under a heavy brow, and a forehead esca-lure. Bulk +
    bioluminescence, never cute."""
    s = scale

    # — drowned-world drip: stranded under-belly tendrils trailing to the ground
    #   (drawn FIRST so the body mass overlaps and roots them). —
    for i in range(7):
        dx = cx - int(70 * s) + int(i * 24 * s)
        dy0 = base_y - int(2 * s)
        wob = int(math.sin(i * 1.3 + t) * 5 * s)
        pygame.draw.line(surf, ABYSS_DKR,
                         (dx, base_y - int(58 * s)), (dx + wob, dy0),
                         max(1, int(3 * s)))
        pygame.draw.circle(surf, ABYSS_DK, (dx + wob, dy0), max(1, int(2 * s)))

    # — looming wet dome of body-mass (the only blob in the set) —
    body_rw = int(96 * s)
    body_rh = int(70 * s)
    bx = cx + int(16 * s)
    by = base_y - int(52 * s)
    _wet_dome(surf, bx, by, body_rw, body_rh)

    # — twin ragged dorsal flukes (the brainstorm's "ears"), leaned back —
    for sgn, lean in ((-1, 0.0), (1, 0.0)):
        fx = bx + sgn * int(58 * s)
        fy = by - int(54 * s)
        pygame.draw.polygon(surf, ABYSS_DKR, [
            (fx, fy + int(20 * s)),
            (fx + sgn * int(26 * s), fy - int(34 * s)),
            (fx + sgn * int(40 * s), fy - int(2 * s)),
        ])
        pygame.draw.polygon(surf, ABYSS, [
            (fx + sgn * int(3 * s), fy + int(16 * s)),
            (fx + sgn * int(24 * s), fy - int(28 * s)),
            (fx + sgn * int(34 * s), fy - int(2 * s)),
        ])

    # — barnacle reef riding the back, like crust on a drowned hull —
    for (ox, oy, r) in (
            (-58, -56, 7), (-30, -70, 9), (2, -76, 8),
            (34, -70, 7), (58, -52, 6), (-14, -50, 5), (22, -54, 5)):
        _barnacle(surf, bx + int(ox * s), by + int(oy * s), max(2, int(r * s)))

    # — HEAD / underbite jaw (faces LEFT). This is where 'mean' lives. The whole
    #   head is built much larger + thrust forward so it commands the silhouette.
    hx = bx - int(78 * s)
    hy = by + int(26 * s)

    # Upper snout (recessed, blunt) — the RECESS is what makes the under-jaw mean.
    snout = [
        (hx + int(52 * s), hy - int(26 * s)),
        (hx - int(30 * s), hy - int(18 * s)),
        (hx - int(20 * s), hy + int(2 * s)),
        (hx + int(50 * s), hy + int(4 * s)),
    ]
    pygame.draw.polygon(surf, ABYSS_DK, snout)
    pygame.draw.polygon(surf, ABYSS,
                        [(p[0] + 2, p[1] + 1) for p in snout[:3]] + [snout[3]])

    # Black gaping maw between the jaws — the cavernous throat.
    pygame.draw.polygon(surf, ABYSS_DKR, [
        (hx + int(44 * s), hy - int(6 * s)),
        (hx - int(34 * s), hy - int(8 * s)),
        (hx - int(46 * s), hy + int(20 * s)),
        (hx + int(40 * s), hy + int(16 * s)),
    ])

    # Lower jaw: a massive slab jutting forward AND up past the snout — the
    # under-jaw is heavier + longer than the upper, the core of the underbite.
    jaw = [
        (hx + int(46 * s), hy + int(14 * s)),       # hinge under the body
        (hx + int(44 * s), hy + int(34 * s)),
        (hx - int(40 * s), hy + int(36 * s)),
        (hx - int(54 * s), hy + int(16 * s)),       # the forward up-jut
        (hx - int(40 * s), hy + int(20 * s)),
        (hx - int(20 * s), hy + int(22 * s)),
    ]
    pygame.draw.polygon(surf, ABYSS_DK, jaw)
    pygame.draw.polygon(surf, ABYSS,
                        [(p[0], p[1] + 2) for p in jaw])
    # A chin highlight ridge so the slab reads as forward, heavy bone.
    pygame.draw.line(surf, ABYSS_RIM,
                     (hx - int(50 * s), hy + int(18 * s)),
                     (hx - int(12 * s), hy + int(30 * s)), max(1, int(2 * s)))

    # — interlocking barnacle FANGS ringing the maw: the underbite's teeth. The
    #   lower row juts UP from the heavy jaw; the upper row drops from the snout,
    #   and they interlock like a deep-sea gulper's trap. —
    n_low = 8
    for i in range(n_low):
        tt = i / (n_low - 1)
        lx = hx + int((40 - 88 * tt) * s)
        ly = hy + int((14 + 6 * tt) * s)
        th = int((13 + 4 * math.sin(tt * math.pi)) * s)
        pygame.draw.polygon(surf, FLESH_DK, [
            (lx - int(4 * s), ly + int(2 * s)), (lx + int(4 * s), ly + int(2 * s)),
            (lx, ly - th)])
        pygame.draw.polygon(surf, FLESH, [
            (lx - int(3 * s), ly + int(1 * s)), (lx + int(2 * s), ly + int(1 * s)),
            (lx, ly - th + int(1 * s))])
        pygame.draw.line(surf, FLESH_HI, (lx - int(1 * s), ly),
                         (lx, ly - th + int(2 * s)), max(1, int(s)))
    n_up = 6
    for i in range(n_up):
        tt = i / (n_up - 1)
        ux = hx + int((34 - 66 * tt) * s)
        uy = hy - int((6 + 1 * tt) * s)
        th = int((10 + 3 * math.sin(tt * math.pi)) * s)
        pygame.draw.polygon(surf, FLESH_DK, [
            (ux - int(3 * s), uy - int(1 * s)), (ux + int(3 * s), uy - int(1 * s)),
            (ux, uy + th)])
        pygame.draw.polygon(surf, FLESH, [
            (ux - int(2 * s), uy - int(1 * s)), (ux + int(2 * s), uy - int(1 * s)),
            (ux, uy + th - int(1 * s))])

    # — sunken dead-jade eye with a vertical predator slit, set DEEP in a socket
    #   under a heavy bony brow ridge. Small + cold, never a big friendly disc. —
    ex, ey = hx + int(20 * s), hy - int(34 * s)
    # Dark sunken socket so the eye reads recessed (depth = menace).
    pygame.draw.ellipse(surf, ABYSS_DKR,
                        (ex - int(16 * s), ey - int(12 * s), int(32 * s), int(24 * s)))
    _glow(surf, ex, ey, int(12 * s), JADE, alpha=70)
    pygame.draw.circle(surf, JADE_DIM, (ex, ey), int(8 * s))
    pygame.draw.circle(surf, JADE, (ex, ey), int(6 * s))
    # Vertical reptilian slit pupil — the single coldest 'mean' tell.
    pygame.draw.ellipse(surf, ABYSS_DKR,
                        (ex - int(2 * s), ey - int(6 * s), max(2, int(3 * s)), int(12 * s)))
    pygame.draw.circle(surf, JADE_PALE,
                       (ex - int(2 * s), ey - int(2 * s)), max(1, int(2 * s)))
    # Heavy hooded brow ridge angled DOWN toward the snout — a permanent glower.
    pygame.draw.polygon(surf, ABYSS_DKR, [
        (ex - int(20 * s), ey - int(6 * s)),
        (ex + int(22 * s), ey - int(14 * s)),
        (ex + int(24 * s), ey - int(6 * s)),
        (ex - int(18 * s), ey + int(2 * s)),
    ])
    pygame.draw.line(surf, ABYSS_RIM,
                     (ex - int(18 * s), ey - int(6 * s)),
                     (ex + int(22 * s), ey - int(13 * s)), max(1, int(2 * s)))

    # — the ESCA: a single long forehead lure-stalk rooting between the brows and
    #   arcing FORWARD over the snout so its bright bulb dangles out in front of
    #   the maw — the anglerfish lure that tells the abyssal story at a glance,
    #   kept clear of the eye so the slit stays the cold focal of the face. —
    sx, sy = ex + int(20 * s), ey - int(20 * s)
    stalk = []
    for k in range(16):
        kt = k / 15
        wob = math.sin(kt * 2.4 + t * 2.0) * 5 * kt
        # rises off the brow, sweeps FORWARD past the snout tip, then dangles the
        # bulb low in front of the open maw (well clear of the eye on the right)
        px = sx - int((96 * kt + wob) * s)
        py = sy - int(math.sin(kt * math.pi * 0.45) * 26 * s) + int(74 * kt * kt * s)
        stalk.append((px, py))
    pygame.draw.lines(surf, JADE_DIM, False, stalk, max(1, int(3 * s)))
    pygame.draw.lines(surf, JADE, False, stalk, max(1, int(s)))
    tip = stalk[-1]
    _lure(surf, tip[0], tip[1], max(3, int(5 * s)),
          pulse=0.85 + 0.3 * math.sin(t * 2.5))

    # — a few secondary belly lures glowing along the dark under-mass —
    for i, (ox, oy, r) in enumerate(((-50, 18, 3), (-22, 30, 2), (10, 34, 3),
                                     (44, 26, 2))):
        _lure(surf, bx + int(ox * s), by + int(oy * s), max(2, int(r * s)),
              pulse=0.7 + 0.3 * math.sin(t * 1.7 + i))


# ── PROP → PILLAR: chain-of-lure-stalks ──────────────────────────────────────

def draw_lure_column(surf, x, y_top, y_bot, t=0.0):
    """A vertical barnacled bone-spine studded with a RHYTHMIC stack of jade
    lure-bulbs on outward-curving stalks. This is the signature prop and the
    obstacle pillar. The straight central spine + alternating outward lures is
    what makes it mirror cleanly: flip it top-to-bottom and the lures still fan
    off the column with the bright bulbs facing the gap."""
    h = y_bot - y_top
    # Bone spine with a slight calcified swell every node — never a plain bar.
    seg = max(34, h // 5)
    for yy in range(y_top, y_bot, 2):
        kt = (yy - y_top) / max(1, h)
        swell = int(3 + 3 * abs(math.sin(kt * math.pi * (h / seg))))
        w = 9 + swell
        pygame.draw.line(surf, ABYSS_DKR, (x - w, yy), (x + w, yy))
        pygame.draw.line(surf, ABYSS, (x - w + 2, yy), (x + w - 2, yy))
        pygame.draw.line(surf, ABYSS_HI, (x - w + 3, yy), (x - w + 5, yy))
    # Cool wet rim down one edge so the bone-spine has a round read.
    pygame.draw.line(surf, ABYSS_RIM, (x - 8, y_top), (x - 8, y_bot), 1)

    # Barnacle nodes + alternating jade lure-stalks at a fixed rhythm.
    side = -1
    node = 0
    yy = y_top + seg // 2
    while yy < y_bot - 8:
        _barnacle(surf, x, yy, 7)
        # lure-stalk arcs OUT to one side, the bulb hanging toward the gap.
        sx, sy = x + side * 11, yy
        stalk = []
        for k in range(7):
            kt = k / 6
            px = sx + side * int(18 * kt)
            py = sy - int(13 * kt * kt)
            stalk.append((px, py))
        pygame.draw.lines(surf, JADE_DIM, False, stalk, 3)
        pygame.draw.lines(surf, JADE, False, stalk, 1)
        tip = stalk[-1]
        _lure(surf, tip[0], tip[1], 5, pulse=0.85 + 0.3 * math.sin(t * 2 + node))
        side *= -1
        node += 1
        yy += seg


def render_pillar_pair(w, gap_top, gap_bot, total_h, t=0.0):
    """Build a top + bottom obstacle pillar from ONE column builder, proving the
    prop mirrors. The bottom pillar is drawn head-up; the top is the SAME
    surface flipped vertically — the abyss convention. Lures always face the
    gap because they arc outward off a symmetric spine."""
    col_w = w
    bot = pygame.Surface((col_w, total_h - gap_bot), pygame.SRCALPHA)
    draw_lure_column(bot, col_w // 2, 0, bot.get_height(), t=t)
    top_src = pygame.Surface((col_w, gap_top), pygame.SRCALPHA)
    draw_lure_column(top_src, col_w // 2, 0, top_src.get_height(), t=t)
    top = pygame.transform.flip(top_src, False, True)
    return top, bot


# ── compose review sheet ──────────────────────────────────────────────────────

def main():
    pygame.init()
    W, H = 820, 660
    panel_w = W // 2
    ground_y = 540

    body = pygame.Surface((W, H))
    body.fill((20, 24, 36))

    big = pygame.font.SysFont("dejavusans", 19, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)

    for i, (bg, label) in enumerate(((DAY_BG, "DAY SKY"), (NIGHT_BG, "NIGHT SKY"))):
        px = i * panel_w
        panel = pygame.Surface((panel_w, H))
        _vgrad(panel, (0, 0, panel_w, H), bg[0], bg[1])
        # abyss ground line the GOD hauls itself over
        _vgrad(panel, (0, ground_y, panel_w, H - ground_y), ABYSS_DK, (5, 8, 16))
        pygame.draw.line(panel, JADE_DIM, (0, ground_y), (panel_w, ground_y), 2)
        # faint floor bloom under the belly — small + low alpha so it reads as a
        # damp halo on the wet ground, never a solid jade ball
        _glow(panel, panel_w // 2 + 12, ground_y + 2, 46, JADE, alpha=18)
        draw_leviathan(panel, panel_w // 2 - 6, ground_y, scale=1.35, t=0.7)
        body.blit(panel, (px, 0))
        lab = big.render(label, True, JADE)
        body.blit(lab, (px + 16, 14))

    pygame.draw.line(body, (6, 8, 16), (panel_w, 0), (panel_w, H), 2)

    # ── pillar-fit thumbnail (bottom strip) proving the prop mirrors ──────────
    strip_h = 210
    th = pygame.Surface((W, strip_h))
    _vgrad(th, (0, 0, W, strip_h), (12, 16, 28), (22, 28, 44))
    col_w = 96
    pillar_total = strip_h
    gap_top, gap_bot = 78, 132
    top, bot = render_pillar_pair(col_w, gap_top, gap_bot, pillar_total, t=0.4)
    tx = 70
    th.blit(top, (tx, 0))
    th.blit(bot, (tx, gap_bot))
    # gap markers
    for gy in (gap_top, gap_bot):
        pygame.draw.line(th, JADE, (tx - 12, gy), (tx + col_w + 12, gy), 1)
    glab = small.render("GAP", True, JADE)
    th.blit(glab, (tx + col_w // 2 - 14, (gap_top + gap_bot) // 2 - 8))

    cx = tx + col_w + 50
    th.blit(big.render("PILLAR-FIT", True, FLESH_HI), (cx, 16))
    lines = [
        "One chain-of-lure-stalks builder. The TOP pillar is the",
        "SAME surface flipped vertically (top = flip(bottom)) —",
        "lures always fan toward the GAP because they arc outward",
        "off a straight central spine.",
        "",
        "PROP = lure-stalk column, NOT a barbed harpoon: a barbed",
        "TIP can't mirror, but a rhythmic bulb/gap stack carries",
        "the vertical AND flips clean.",
    ]
    for k, ln in enumerate(lines):
        col = JADE if ln.startswith("PROP") else FLESH
        th.blit(small.render(ln, True, col), (cx, 46 + k * 19))

    # ── title band + assemble ─────────────────────────────────────────────────
    band_h = 48
    final = pygame.Surface((W, band_h + H + strip_h))
    band = pygame.Surface((W, band_h))
    band.fill((8, 10, 18))
    title = big.render("deep-leviathan  —  round 1  —  abyssal whale-GOD", True,
                       (235, 240, 245))
    band.blit(title, (12, 6))
    sub = small.render("bulk + bioluminescence  ·  hard predatory underbite  ·  "
                       "lure-stalk prop → mirrored pillar", True, JADE)
    band.blit(sub, (12, 29))
    final.blit(band, (0, 0))
    final.blit(body, (0, band_h))
    final.blit(th, (0, band_h + H))

    dst = os.path.join(os.path.dirname(__file__), "..",
                       "docs", "epic_boss", "deep-leviathan", "round_1.png")
    dst = os.path.abspath(dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    pygame.image.save(final, dst)
    print("saved", dst)


if __name__ == "__main__":
    main()
