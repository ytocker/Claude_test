"""IFRA — round 1 design sheet (Batch-2 Devilish, smokeless-fire genie devil).

Renders the ONE locked concept: an ifrit cuted to a cocky ember-imp whose legs
dissolve into a billowing smoke-flame curl. Sheet follows the Batch-2 grammar
(brimstone take): (a) BOSS showcase scale, (b) PROP -> PILLAR at true obstacle
scale + a 2x gap zoom, (c) 1x in-game day/night legibility + a grayscale
silhouette check. House style: chibi, FLAT triad fills (dark-core -> flat-fill
-> top-left rim-sheen), hard ink keyline grown 1px from the alpha mask,
supersample -> smoothscale.

Run:  SDL_VIDEODRIVER=dummy python docs/skybit_devil/batch2/ifra/render.py
Out:  docs/skybit_devil/batch2/ifra/round_1.png

Exploration only — nothing is wired into the live game.
"""

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()

# ── PINNED PALETTE (exact hexes from the locked brief) ──────────────────────
EMBER      = (238, 108, 72)    # coral-ember body
RUST       = (176, 62, 42)     # deep-rust shade (dark core)
VIOLET     = (118, 86, 150)    # violet smoke-plume accent — cool counterweight
SAFFRON    = (255, 196, 96)    # hot-saffron flame-core
BRASS      = (214, 168, 72)    # brass lamp + nose-ring
INK        = (34, 20, 24)      # keyline ink
SHEEN      = (255, 182, 138)   # top-left rim sheen

# Derived working tints (value/sat steps of the pinned hues — never new hues).
VIOLET_D   = (76, 54, 104)     # deep smoke core
VIOLET_L   = (164, 134, 196)   # smoke top-left sheen
BRASS_D    = (150, 112, 44)    # lamp shade
BRASS_L    = (244, 214, 140)   # lamp sheen
COAL_GLOW  = (255, 150, 96)    # coal-eye inner glow (still in the fire family)

# ── Supersample kit (mirrors the project's buff-emblem / pillar conventions) ─
_SS = 4
_OW = max(2, 3 * _SS // 2)     # ~1.5px keyline at footprint after downsample


def _lerp(a, b, t):
    return a + (b - a) * t


def _mix(c1, c2, t):
    return (int(_lerp(c1[0], c2[0], t)),
            int(_lerp(c1[1], c2[1], t)),
            int(_lerp(c1[2], c2[2], t)))


def _shade(c, f):
    return (max(0, min(255, int(c[0] * f))),
            max(0, min(255, int(c[1] * f))),
            max(0, min(255, int(c[2] * f))))


def _raw(w, h):
    return pygame.Surface((w * _SS, h * _SS), pygame.SRCALPHA)


def _outline_from_alpha(surf, color, grow=1):
    """Grow a hard keyline OUTSIDE the alpha silhouette — the house POP trick.
    Built from the mask so it traces whatever shape we drew, not per-poly."""
    mask = pygame.mask.from_surface(surf)
    outline_pts = mask.outline()
    if len(outline_pts) < 2:
        return
    line = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(line, color, outline_pts, max(2, grow * _SS))
    # Keep only the grown ring behind the existing art (draw line, then re-blit art).
    base = surf.copy()
    surf.fill((0, 0, 0, 0))
    surf.blit(line, (0, 0))
    surf.blit(base, (0, 0))


def _triad_lobe(surf, pts, fill, core, sheen, core_inset=0.30, sheen_inset=0.22):
    """A hard flat flame-lobe with the dark-core / flat-fill / TL-sheen triad —
    never a soft gradient. Inset polygons keyed off the lobe centroid."""
    pygame.draw.polygon(surf, fill, pts)
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    core = list(core) if isinstance(core, list) else core
    # Dark core: shrink toward centroid, biased DOWN (heat sinks low like brimstone).
    core_pts = [(_lerp(px, cx, core_inset), _lerp(py, cy + (max(p[1] for p in pts) - cy) * 0.25, core_inset))
                for (px, py) in pts]
    pygame.draw.polygon(surf, RUST, core_pts)
    pygame.draw.polygon(surf, fill, [(_lerp(px, cx, 0.02), _lerp(py, cy - 4, 0.05)) for px, py in core_pts][:0] or core_pts) if False else None
    # Saffron flame-core nested deepest (the live-fire heart).
    heart = [(_lerp(px, cx, 0.55), _lerp(py, cy + 6, 0.55)) for (px, py) in pts]
    pygame.draw.polygon(surf, core, heart)
    # Top-left rim sheen: a thin bright shard along the upper-left edge.
    sx, sy = min(p[0] for p in pts), min(p[1] for p in pts)
    sheen_pts = [(_lerp(px, sx, sheen_inset), _lerp(py, sy, sheen_inset)) for (px, py) in pts]
    # only the top-left half reads as sheen
    pygame.draw.polygon(surf, sheen, sheen_pts[:max(3, len(sheen_pts) // 2 + 1)])


# ── IFRA the creature ───────────────────────────────────────────────────────
def build_ifra(W, H, bob=0):
    """Broad crossed-arm ember torso + two back-swept flame-horns tapering into
    a legless billowing smoke-curl base. Drawn in a local SS surface; the hard
    keyline is grown from the final alpha so the silhouette pops."""
    s = _raw(W, H)
    S = _SS
    cx = W * S // 2
    yb = bob * S

    # ---- 1) Smoke-flame plume base (the no-legs blob — the 32px read) -------
    # Violet smoke is the cool counterweight; built as stacked hard flame-lobes
    # billowing wider toward the floor, so the silhouette is a fat curl, not legs.
    plume_top = int(H * 0.52) * S + yb
    plume_bot = int(H * 0.96) * S + yb
    # Big outer billow (violet smoke) — two side curls.
    for sgn in (-1, 1):
        curl = [
            (cx, plume_top),
            (cx + sgn * int(W * 0.30) * S, int(H * 0.70) * S + yb),
            (cx + sgn * int(W * 0.34) * S, int(H * 0.86) * S + yb),
            (cx + sgn * int(W * 0.16) * S, plume_bot),
            (cx, int(H * 0.90) * S + yb),
        ]
        _triad_lobe(s, curl, VIOLET, VIOLET_L, VIOLET_L, core_inset=0.34)
        # re-tint the core to violet-dark (the triad helper paints RUST core for
        # the fire lobes; the smoke wants its own deep-violet core).
        ccx = sum(p[0] for p in curl) / len(curl)
        ccy = sum(p[1] for p in curl) / len(curl)
        core_pts = [(_lerp(px, ccx, 0.36), _lerp(py, ccy + int(H * 0.08) * S, 0.36)) for px, py in curl]
        pygame.draw.polygon(s, VIOLET_D, core_pts)
        # violet sheen shard, top-outer edge
        sh = [(_lerp(px, min(p[0] for p in curl), 0.30), _lerp(py, min(p[1] for p in curl), 0.30)) for px, py in curl]
        pygame.draw.polygon(s, VIOLET_L, sh[:3])
    # Central ember tongue licking up through the smoke (live-fire focal at base).
    tongue = [
        (cx, plume_top),
        (cx + int(W * 0.12) * S, int(H * 0.74) * S + yb),
        (cx, int(H * 0.86) * S + yb),
        (cx - int(W * 0.12) * S, int(H * 0.74) * S + yb),
    ]
    _triad_lobe(s, tongue, EMBER, SAFFRON, SHEEN, core_inset=0.30)

    # ---- 2) Torso — broad chibi ember block, WIDEST at the shoulders, then
    # nipping in hard at the waist so the silhouette reads as a heavy upper body
    # over a slim waist (the genie "V" that makes the crossed arms legible).
    torso_top = int(H * 0.32) * S + yb       # under the chin
    shoulder_y = int(H * 0.38) * S + yb
    waist_y = plume_top + int(H * 0.005) * S
    torso = [
        (cx - int(W * 0.34) * S, shoulder_y),
        (cx - int(W * 0.40) * S, int(H * 0.42) * S + yb),   # WIDE shoulders
        (cx - int(W * 0.13) * S, waist_y),                  # in at the waist
        (cx + int(W * 0.13) * S, waist_y),
        (cx + int(W * 0.40) * S, int(H * 0.42) * S + yb),
        (cx + int(W * 0.34) * S, shoulder_y),
    ]
    pygame.draw.polygon(s, EMBER, torso)
    # dark-core (lower belly, biased low)
    pygame.draw.polygon(s, RUST, [
        (cx - int(W * 0.22) * S, int(H * 0.45) * S + yb),
        (cx + int(W * 0.22) * S, int(H * 0.45) * S + yb),
        (cx + int(W * 0.11) * S, waist_y),
        (cx - int(W * 0.11) * S, waist_y),
    ])
    # TL sheen shard on the chest
    pygame.draw.polygon(s, SHEEN, [
        (cx - int(W * 0.32) * S, shoulder_y + int(H * 0.01) * S),
        (cx - int(W * 0.12) * S, shoulder_y + int(H * 0.02) * S),
        (cx - int(W * 0.18) * S, int(H * 0.44) * S + yb),
        (cx - int(W * 0.36) * S, int(H * 0.41) * S + yb),
    ])

    # ---- 3) Crossed beefy arms (classic genie pose) — fat forearms lying X
    # across the chest, each capped by a round bicep at the shoulders so the
    # crossed-arms read survives at 32px as a horizontal bar over the V-torso.
    arm_y = int(H * 0.45) * S + yb
    # bicep shoulder caps first (the wide shoulders), then the crossing forearms
    for sgn in (-1, 1):
        pygame.draw.circle(s, EMBER, (cx + sgn * int(W * 0.32) * S, int(H * 0.43) * S + yb), int(W * 0.13) * S)
    for sgn in (-1, 1):
        # forearm: thick bar from one shoulder diagonally down to the far waist
        a = [
            (cx + sgn * int(W * 0.34) * S, int(H * 0.42) * S + yb),
            (cx - sgn * int(W * 0.10) * S, arm_y + int(H * 0.07) * S),
            (cx - sgn * int(W * 0.04) * S, arm_y + int(H * 0.13) * S),
            (cx + sgn * int(W * 0.36) * S, int(H * 0.48) * S + yb),
        ]
        col = EMBER if sgn > 0 else _shade(EMBER, 0.9)   # near arm brighter
        pygame.draw.polygon(s, col, a)
        pygame.draw.polygon(s, RUST, [a[1], a[2], a[3]])
        # sheen on the near (front) forearm only
        if sgn > 0:
            pygame.draw.polygon(s, SHEEN, [a[0], (cx + int(W * 0.18) * S, arm_y), a[1]])
        # chunky fist tucked under the opposite bicep
        pygame.draw.circle(s, col, (cx - sgn * int(W * 0.08) * S, arm_y + int(H * 0.10) * S), int(W * 0.07) * S)
        pygame.draw.circle(s, RUST, (cx - sgn * int(W * 0.06) * S, arm_y + int(H * 0.12) * S), int(W * 0.035) * S)
    # bicep sheen
    pygame.draw.circle(s, SHEEN, (cx - int(W * 0.34) * S, int(H * 0.40) * S + yb), int(W * 0.05) * S)

    # ---- 4) Head — square smug face, coal-eyes, nose-ring, two flame-horns --
    hw = int(W * 0.27) * S
    hh = int(H * 0.20) * S
    hcx = cx
    hcy = int(H * 0.20) * S + yb
    # Flame-horns: two flat back-swept lobes BEHIND the head (drawn first).
    for sgn in (-1, 1):
        horn = [
            (hcx + sgn * int(W * 0.16) * S, hcy - int(H * 0.06) * S),
            (hcx + sgn * int(W * 0.40) * S, hcy - int(H * 0.18) * S),
            (hcx + sgn * int(W * 0.34) * S, hcy - int(H * 0.02) * S),
            (hcx + sgn * int(W * 0.18) * S, hcy + int(H * 0.04) * S),
        ]
        _triad_lobe(s, horn, EMBER, SAFFRON, SHEEN, core_inset=0.28)
    # square head block (rounded corners via a rect + circles)
    head_rect = pygame.Rect(hcx - hw, hcy - hh, hw * 2, hh * 2)
    pygame.draw.rect(s, EMBER, head_rect, border_radius=int(W * 0.07) * S)
    # head dark-core (lower jaw) + TL cheek sheen
    pygame.draw.rect(s, RUST, pygame.Rect(hcx - int(hw * 0.8), hcy + int(hh * 0.15), int(hw * 1.6), int(hh * 0.8)),
                     border_radius=int(W * 0.05) * S)
    pygame.draw.polygon(s, SHEEN, [
        (hcx - hw + 2 * S, hcy - hh + 2 * S),
        (hcx - int(hw * 0.2), hcy - hh + 3 * S),
        (hcx - int(hw * 0.5), hcy),
        (hcx - hw + 2 * S, hcy - int(hh * 0.3)),
    ])
    # heavy smug brow
    pygame.draw.line(s, INK, (hcx - int(hw * 0.7), hcy - int(hh * 0.18)),
                     (hcx + int(hw * 0.7), hcy - int(hh * 0.30)), max(2, _OW))
    # glowing coal-eyes (saffron core in a dark socket)
    for sgn in (-1, 1):
        ex = hcx + sgn * int(hw * 0.42)
        ey = hcy + int(hh * 0.05)
        pygame.draw.circle(s, INK, (ex, ey), int(W * 0.075) * S)
        pygame.draw.circle(s, COAL_GLOW, (ex, ey), int(W * 0.055) * S)
        pygame.draw.circle(s, SAFFRON, (ex - 1 * S, ey - 1 * S), int(W * 0.028) * S)
    # cocky smirk
    pygame.draw.lines(s, INK, False, [
        (hcx - int(hw * 0.34), hcy + int(hh * 0.50)),
        (hcx + int(hw * 0.10), hcy + int(hh * 0.58)),
        (hcx + int(hw * 0.40), hcy + int(hh * 0.40)),
    ], max(2, _OW))
    # single gold nose-ring hanging at the septum
    nrx, nry = hcx, hcy + int(hh * 0.34)
    pygame.draw.circle(s, BRASS, (nrx, nry + int(W * 0.05) * S), int(W * 0.05) * S, max(2, _OW))
    pygame.draw.circle(s, BRASS_L, (nrx - 1 * S, nry + int(W * 0.03) * S), int(W * 0.05) * S, max(1, _OW - 1))

    # ---- hard keyline grown from the assembled alpha ------------------------
    _outline_from_alpha(s, INK, grow=1)
    # re-light the coal-eyes + nose-ring ON TOP of the keyline so they stay hot
    for sgn in (-1, 1):
        ex = hcx + sgn * int(hw * 0.42)
        ey = hcy + int(hh * 0.05)
        pygame.draw.circle(s, COAL_GLOW, (ex, ey), int(W * 0.05) * S)
        pygame.draw.circle(s, SAFFRON, (ex - 1 * S, ey - 1 * S), int(W * 0.026) * S)
    return pygame.transform.smoothscale(s, (W, H))


# ── LAMP-PILLAR (the prop -> pillar mirror) ─────────────────────────────────
def build_lamp_shaft(W, H):
    """Fluted oil-lamp body = repeatable shaft. Vertical flutes (banding) read
    as a clean symmetric column that tiles top<->bottom."""
    s = _raw(W, H)
    S = _SS
    cx = W * S // 2
    half = int(W * 0.34) * S
    body = pygame.Rect(cx - half, 0, half * 2, H * S)
    pygame.draw.rect(s, BRASS, body)
    # dark-core down the center seam, fill flanks, TL sheen flute
    pygame.draw.rect(s, BRASS_D, pygame.Rect(cx - int(half * 0.55), 0, int(half * 1.1), H * S))
    # vertical fluting bands (the repeatable banding tell)
    n = 5
    for i in range(n):
        fx = int(_lerp(cx - half + 3 * S, cx + half - 3 * S, i / (n - 1)))
        col = BRASS_L if i % 2 == 0 else BRASS_D
        pygame.draw.line(s, col, (fx, 0), (fx, H * S), max(2, int(W * 0.03) * S))
    # TL sheen flute (the lit edge)
    pygame.draw.line(s, BRASS_L, (cx - half + 3 * S, 0), (cx - half + 3 * S, H * S), max(2, int(W * 0.04) * S))
    _outline_from_alpha(s, INK, grow=1)
    return pygame.transform.smoothscale(s, (W, H))


def build_lamp_cap(W, H, flip=False):
    """Wick-spout puffing a fire-curl = gap-edge cap. Lamp shoulder + curved
    spout + a triad-lit ember curl licking INTO the gap. Symmetric on-axis."""
    s = _raw(W, H)
    S = _SS
    cx = W * S // 2
    half = int(W * 0.34) * S
    # lamp shoulder dome (top of the shaft swelling into the bulbous lamp body)
    dome = pygame.Rect(cx - half, int(H * 0.34) * S, half * 2, int(H * 0.66) * S)
    pygame.draw.rect(s, BRASS, dome)
    shoulder = pygame.Rect(cx - int(half * 1.15), int(H * 0.28) * S, int(half * 2.3), int(H * 0.30) * S)
    pygame.draw.ellipse(s, BRASS, shoulder)
    pygame.draw.ellipse(s, BRASS_D, pygame.Rect(cx - int(half * 0.7), int(H * 0.40) * S, int(half * 1.4), int(H * 0.20) * S))
    pygame.draw.ellipse(s, BRASS_L, pygame.Rect(cx - int(half * 1.0), int(H * 0.29) * S, int(half * 0.8), int(H * 0.12) * S))
    # curved spout (off to one side, classic oil-lamp)
    spout = [
        (cx, int(H * 0.30) * S), (cx + int(half * 1.1), int(H * 0.24) * S),
        (cx + int(half * 1.4), int(H * 0.14) * S), (cx + int(half * 1.15), int(H * 0.18) * S),
        (cx + int(half * 0.6), int(H * 0.30) * S),
    ]
    pygame.draw.polygon(s, BRASS, spout)
    pygame.draw.polygon(s, BRASS_L, [spout[0], spout[1], spout[4]])
    # fire-curl puffing from the spout (the live-fire signature, INTO the gap)
    flame = [
        (cx + int(half * 1.25), int(H * 0.16) * S),
        (cx + int(half * 1.55), int(H * 0.02) * S),
        (cx + int(half * 1.20), int(H * 0.05) * S),
        (cx + int(half * 1.05), int(H * 0.14) * S),
    ]
    _triad_lobe(s, flame, EMBER, SAFFRON, SHEEN, core_inset=0.25)
    # a violet smoke wisp curling off the flame (cool counterweight, even here)
    smoke = [
        (cx + int(half * 1.40), int(H * 0.06) * S),
        (cx + int(half * 1.50), int(H * -0.06) * S),
        (cx + int(half * 1.30), int(H * 0.0) * S),
    ]
    pygame.draw.polygon(s, VIOLET, smoke)
    pygame.draw.polygon(s, VIOLET_L, [smoke[0], smoke[1], (cx + int(half * 1.42), int(H * 0.0) * S)])
    out = pygame.transform.smoothscale(s, (W, H))
    if flip:
        out = pygame.transform.flip(out, False, True)
    return out


# ── Sky helpers (day/night biome legibility) ────────────────────────────────
def day_sky(w, h):
    s = pygame.Surface((w, h))
    top, bot = (118, 196, 246), (206, 240, 252)
    for y in range(h):
        pygame.draw.line(s, _mix(top, bot, y / max(1, h - 1)), (0, y), (w, y))
    return s


def night_sky(w, h):
    import random
    s = pygame.Surface((w, h))
    top, bot = (18, 22, 46), (52, 40, 78)
    for y in range(h):
        pygame.draw.line(s, _mix(top, bot, y / max(1, h - 1)), (0, y), (w, y))
    rnd = random.Random(9)
    for _ in range(60):
        x, y = rnd.randint(0, w - 1), rnd.randint(0, h - 1)
        b = rnd.randint(120, 230)
        s.set_at((x, y), (b, b, min(255, b + 20)))
    return s


def to_grayscale(surf):
    g = surf.copy()
    arr = pygame.surfarray.pixels3d(g)
    lum = (arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587 + arr[:, :, 2] * 0.114).astype('uint8')
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    return g


def _font(sz, bold=True):
    return pygame.font.SysFont("dejavusans", sz, bold=bold)


def main():
    SHEET_W, SHEET_H = 1180, 760
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((30, 32, 40))

    f_title = _font(24)
    f_sub = _font(15, bold=False)
    f_panel = _font(18)
    f_small = _font(14, bold=False)

    sheet.blit(f_title.render("IFRA  —  Batch-2 Devilish  —  smokeless-fire genie devil  —  round 1",
                              True, (240, 240, 248)), (22, 14))
    sheet.blit(f_sub.render("ifrit cuted to a cocky ember-imp: crossed-arm torso + flame-horns "
                            "tapering into a legless violet smoke-curl",
                            True, (190, 190, 200)), (22, 40))

    PANEL_Y = 66
    PANEL_H = 540
    # three panels
    p1 = pygame.Rect(14, PANEL_Y, 384, PANEL_H)
    p2 = pygame.Rect(406, PANEL_Y, 360, PANEL_H)
    p3 = pygame.Rect(774, PANEL_Y, 392, PANEL_H)
    for p in (p1, p2, p3):
        pygame.draw.rect(sheet, (44, 46, 56), p, border_radius=8)
        pygame.draw.rect(sheet, (70, 74, 84), p, 2, border_radius=8)

    # ---- (a) BOSS showcase scale -------------------------------------------
    sheet.blit(f_panel.render("(a) BOSS  showcase scale", True, (230, 220, 160)), (p1.x + 12, p1.y + 8))
    big = build_ifra(170, 220)
    big = pygame.transform.scale(big, (272, 352))
    sheet.blit(big, (p1.centerx - big.get_width() // 2, p1.y + 80))
    sheet.blit(f_small.render("flat triad lobes (dark-core/coral fill/saffron sheen),", True, (200, 200, 210)),
               (p1.x + 12, p1.bottom - 56))
    sheet.blit(f_small.render("violet smoke-curl base = the no-legs blob; gold nose-ring.", True, (200, 200, 210)),
               (p1.x + 12, p1.bottom - 38))

    # ---- (b) PROP -> PILLAR @ true obstacle scale --------------------------
    sheet.blit(f_panel.render("(b) PROP -> PILLAR  @ obstacle scale", True, (230, 220, 160)), (p2.x + 12, p2.y + 8))
    sky_b = night_sky(p2.w - 24, p2.h - 40)
    sheet.blit(sky_b, (p2.x + 12, p2.y + 34))
    # native obstacle column ~82px wide as it scrolls; mirrored top<->bottom.
    COL_W = 82
    cap = build_lamp_cap(COL_W, 90, flip=False)
    shaft = build_lamp_shaft(COL_W, 150)
    cap_top = build_lamp_cap(COL_W, 90, flip=True)
    # bottom pillar: shaft rising, lamp-cap at the gap edge (top of column)
    col_x = p2.x + 40
    base_y = p2.bottom - 18
    sheet.blit(shaft, (col_x, base_y - 150))
    sheet.blit(cap, (col_x, base_y - 150 - 80))   # spout fire licks UP into gap
    # top pillar (mirror): shaft hanging, cap flipped at the gap edge (bottom)
    top_y = p2.y + 44
    sheet.blit(shaft, (col_x, top_y))
    sheet.blit(cap_top, (col_x, top_y + 150 - 10))
    sheet.blit(f_small.render("1x native (~82px). fluted lamp", True, (210, 215, 225)), (col_x - 4, base_y + 2))
    sheet.blit(f_small.render("body = shaft; wick fire-curl = cap", True, (210, 215, 225)), (col_x - 4, base_y + 18) if base_y + 18 < p2.bottom else (col_x - 4, base_y + 2))
    # 2x zoom of the gap-cap
    zoom = pygame.transform.scale(cap, (COL_W * 2, 180))
    zx = p2.right - COL_W * 2 - 24
    zy = p2.centery - 40
    pygame.draw.rect(sheet, (28, 30, 38), (zx - 6, zy - 6, COL_W * 2 + 12, 192), border_radius=8)
    sheet.blit(zoom, (zx, zy))
    sheet.blit(f_small.render("2x cap zoom:", True, (210, 215, 225)), (zx - 4, zy - 24))
    sheet.blit(f_small.render("fire-curl + violet", True, (210, 215, 225)), (zx - 4, zy + 186))
    sheet.blit(f_small.render("wisp puff INTO gap", True, (210, 215, 225)), (zx - 4, zy + 202))

    # ---- (c) 1x in-game legibility + grayscale silhouette ------------------
    sheet.blit(f_panel.render("(c) 1x in-game  —  day / night + silhouette", True, (230, 220, 160)),
               (p3.x + 12, p3.y + 8))
    sprite_day = build_ifra(64, 78)
    sprite_night = build_ifra(64, 78)
    half_w = (p3.w - 36) // 2
    # day swatch
    dsky = day_sky(half_w, 150)
    sheet.blit(dsky, (p3.x + 12, p3.y + 36))
    sheet.blit(f_small.render("DAY", True, (30, 50, 80)), (p3.x + 18, p3.y + 40))
    sheet.blit(pygame.transform.scale(sprite_day, (96, 117)),
               (p3.x + 12 + half_w // 2 - 48, p3.y + 50))
    # night swatch
    nsky = night_sky(half_w, 150)
    sheet.blit(nsky, (p3.x + 24 + half_w, p3.y + 36))
    sheet.blit(f_small.render("NIGHT", True, (200, 210, 230)), (p3.x + 30 + half_w, p3.y + 40))
    sheet.blit(pygame.transform.scale(sprite_night, (96, 117)),
               (p3.x + 24 + half_w + half_w // 2 - 48, p3.y + 50))

    # true 32px row (the silhouette-read verification the brief asked for)
    sheet.blit(f_small.render("true 32px (creature / pillar-cap):", True, (220, 220, 230)),
               (p3.x + 12, p3.y + 200))
    s32 = build_ifra(32, 40)
    cap32 = build_lamp_cap(32, 36)
    shaft32 = build_lamp_shaft(32, 50)
    # tiny day/night chips at native 32
    for i, mk in enumerate((day_sky, night_sky)):
        chip = mk(44, 50)
        cxp = p3.x + 16 + i * 56
        sheet.blit(chip, (cxp, p3.y + 222))
        sheet.blit(s32, (cxp + 6, p3.y + 226))
    # pillar mini at 32 native
    px = p3.x + 16 + 2 * 56 + 14
    nchip = night_sky(48, 110)
    sheet.blit(nchip, (px, p3.y + 222))
    sheet.blit(shaft32, (px + 8, p3.y + 270))
    sheet.blit(cap32, (px + 8, p3.y + 236))
    sheet.blit(f_small.render("pillar", True, (210, 215, 225)), (px, p3.y + 334))

    # grayscale silhouette check
    sheet.blit(f_small.render("grayscale: smoke-curl base + crossed arms carry the read",
                              True, (210, 210, 218)), (p3.x + 12, p3.y + 352))
    gray = to_grayscale(pygame.transform.scale(build_ifra(120, 150), (120, 150)))
    gplate = pygame.Surface((p3.w - 24, 150))
    gplate.fill((150, 150, 156))
    sheet.blit(gplate, (p3.x + 12, p3.y + 374))
    sheet.blit(gray, (p3.centerx - 60, p3.y + 374))
    # grayscale 32px alongside, to confirm small-scale read
    g32 = to_grayscale(build_ifra(32, 40))
    sheet.blit(pygame.transform.scale(g32, (64, 80)), (p3.right - 90, p3.y + 410))
    sheet.blit(f_small.render("32px", True, (60, 60, 66)), (p3.right - 86, p3.y + 492))

    # ---- footer notes -------------------------------------------------------
    fy = PANEL_Y + PANEL_H + 14
    sheet.blit(f_sub.render("scary-cute: cocky genie swagger; coal-eyes glow like quiet embers, "
                            "not glare. Sole live-fire hue (coral+saffron) in the set; violet smoke is the cool counterweight.",
                            True, (200, 200, 210)), (22, fy))
    sheet.blit(f_sub.render("house style: FLAT triad lobes, hard ink keyline grown from the alpha mask, ss=4 -> smoothscale.",
                            True, (200, 200, 210)), (22, fy + 22))
    sheet.blit(f_sub.render("prop->pillar: fluted oil-lamp body = repeatable shaft (vertical flutes); "
                            "wick-spout fire-curl = gap-edge cap. Clean vertical mirror, no top-heavy risk.",
                            True, (200, 200, 210)), (22, fy + 44))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
