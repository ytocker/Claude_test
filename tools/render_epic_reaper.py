"""Look-dev mockup: the `reaper-shade` EPIC EVENT-BOSS, round 1.

WHY: a clean-sheet late-game boss that must out-class the chibi clown and stay
distinct from its sibling concepts. Reaper-shade's thesis is "Death itself" — a
faceless HOODED specter whose lower body DISSOLVES into smoke (no feet, the only
legless read in the set), gliding rather than standing, with a huge curved
GREAT-SCYTHE arcing overhead.

Palette discipline is the separation lever: a sibling lich owns teal/cyan, so
this stays VOID-VIOLET dominant with the spectral pale-green as a THIN, cold,
low-luminance ACCENT only (soul-light in the hood, a hairline blade gleam, a
sparse ember or two) — never a lime wash.

The signature prop is a GREAT-SCYTHE that must later mirror into a vertical
PILLAR pair. The decision this round: the SNATH (the long straight shaft) is the
pillar body, and the curved blade rides the GAP-EDGE as a flourish — so a
top/bottom mirror reads as a clean vertical post with a hooked blade flourishing
INTO the gap, not a confusing horizontal claw. The sheet proves this with a
small pillar-fit thumbnail beside the full-scale held figure on day + night sky.

Nothing under `game/` is touched; we import the real colour kit only. Headless +
deterministic. Output: docs/epic_boss/reaper-shade/round_1.png.

    PYTHONPATH=. python tools/render_epic_reaper.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color


pygame.init()

# ── reaper-shade palette ──────────────────────────────────────────────────────
# Void black-violet DOMINATES; spectral pale-green is a THIN cold accent only;
# bone-white is reserved for the blade edge + skeletal grip. All desaturated and
# low-luminance so the green can never read as the clown's lime or the lich's
# cyan.
VOID        = (34, 28, 46)        # robe core — the dominant mass
VOID_DK     = (20, 16, 30)        # deepest folds / hood cavity rim
VOID_HEM    = (44, 36, 60)        # raised fold / shoulder catchlight (still dark)
SOUL        = (176, 236, 180)     # spectral soul-light — used SPARINGLY
SOUL_DIM    = (96, 140, 104)      # desaturated soul, for the wider inner glow
BONE        = (228, 224, 212)     # blade + skeletal fingers
BONE_DK     = (150, 146, 136)     # bone underside / blade spine shadow
SMOKE       = (52, 44, 70)        # dissolving-hem wisp (violet-grey, never grey)


# ── builder ───────────────────────────────────────────────────────────────────

def _blit_glow(surf, cx, cy, r, col, alpha):
    """A soft additive halo — used only for the faint soul-light bleed so the
    hood reads as lit-from-within without a bright disc. Kept tiny on purpose so
    violet stays dominant."""
    g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for i in range(4):
        rr = int(r * (1 - i / 4.0))
        a = int(alpha * (i + 1) / 4.0)
        pygame.draw.circle(g, (*col, a), (r, r), rr)
    surf.blit(g, (cx - r, cy - r), special_flags=pygame.BLEND_RGBA_ADD)


def _smoke_dissolve(surf, cx, base_y, width, ss, rng_seed=0):
    """The lower body breaking into wispy smoke instead of feet — the distinct
    LEGLESS read. A spread of softening violet-grey tongues licking down + out,
    each fading to transparent, so the silhouette has NO hard bottom edge and no
    hint of legs. Drawn on a scratch so the alpha falloff composites cleanly."""
    import random
    rng = random.Random(rng_seed)
    h = int(58 * ss)
    scratch = pygame.Surface((width * 3, h), pygame.SRCALPHA)
    ox = width * 3 // 2
    n = 9
    for i in range(n):
        t = i / (n - 1)
        # Tongues fan from the robe column outward; outer ones reach lower + wider
        # so the hem frays apart rather than ending in a flat skirt.
        spread = (t - 0.5) * 2.0
        x0 = ox + int(spread * width * 0.42)
        length = int(h * (0.55 + 0.45 * (1 - abs(spread))))
        sway = rng.uniform(2.0, 5.0) * ss
        w0 = max(2, int((6 - 4 * abs(spread)) * ss))
        prev = (x0, 0)
        steps = 14
        for s in range(1, steps + 1):
            ft = s / steps
            px = x0 + int(math.sin(ft * 3.0 + i) * sway * ft) + int(spread * width * 0.30 * ft)
            py = int(length * ft)
            a = int(150 * (1 - ft) ** 1.4)
            w = max(1, int(w0 * (1 - ft * 0.7)))
            col = lerp_color(VOID, SMOKE, ft)
            pygame.draw.line(scratch, (*col, a), prev, (px, py), w)
            prev = (px, py)
    surf.blit(scratch, (cx - ox, base_y))


def draw_reaper(surf, cx, feet_y, scale=1.0, ss=1):
    """The reaper-shade specter, head-to-smoke, built on its own geometry.

    Construction (all keyed off `H`, the hood-to-hem figure height, so the figure
    scales as one mass):
      - a tall draped ROBE column, narrow at the cowl, flaring slightly at the
        chest, then NOT resolving into a hem — it frays into smoke;
      - a PEAKED, forward-drooping HOOD whose cavity is pure VOID with two thin
        SOUL pinpricks (the faceless stare) + a faint inner soul bleed;
      - one BONE skeletal hand emerging from a sleeve to grip the snath;
      - the GREAT-SCYTHE held: a long straight SNATH planted past the figure, a
      huge bone BLADE sweeping in an arc overhead, lit by a hairline soul gleam.
    `feet_y` is where the smoke dissolves to nothing (the glide line)."""
    H = int(300 * scale * ss)
    W = int(120 * scale * ss)
    top_y = feet_y - H

    # — Robe column: a tapered draped mass, widest at the chest, pinching toward
    #   the cowl and again toward the dissolving hem. Built as a silhouette polygon
    #   so the violet body is one solid dark shape (the legibility carrier).
    chest_y = top_y + int(H * 0.30)
    waist_y = top_y + int(H * 0.68)
    hem_y   = feet_y - int(H * 0.16)            # smoke takes over below this
    cowl_w  = int(W * 0.30)
    chest_w = int(W * 0.52)
    waist_w = int(W * 0.40)
    hem_w   = int(W * 0.30)
    body = [
        (cx - cowl_w, top_y + int(H * 0.10)),
        (cx - chest_w, chest_y),
        (cx - waist_w, waist_y),
        (cx - hem_w, hem_y),
        (cx + hem_w, hem_y),
        (cx + waist_w, waist_y),
        (cx + chest_w, chest_y),
        (cx + cowl_w, top_y + int(H * 0.10)),
    ]
    pygame.draw.polygon(surf, VOID, body)
    pygame.draw.polygon(surf, VOID_DK, body, max(1, int(2 * ss)))

    # Vertical drape folds — a few long dark grooves so the robe reads as cloth,
    # not a flat blob, without lifting the value (folds stay at/under VOID).
    for fx in (-0.55, -0.18, 0.18, 0.55):
        x = cx + int(fx * chest_w * 1.2)
        pygame.draw.line(surf, VOID_DK, (x, chest_y + int(8 * ss)),
                         (x + int(fx * 6 * ss), hem_y), max(1, int(1.6 * ss)))
    # One raised lit fold catch on the chest so the cloth has a hint of form.
    pygame.draw.line(surf, VOID_HEM, (cx - int(chest_w * 0.2), chest_y),
                     (cx - int(waist_w * 0.1), waist_y), max(1, int(2 * ss)))

    # — Shoulders / cowl drape: two dark cloth lobes pulled up to the hood so the
    #   silhouette shoulders read broad and ominous, sloping down off the cowl.
    for s in (-1, 1):
        sh = [
            (cx + s * cowl_w, top_y + int(H * 0.11)),
            (cx + s * int(W * 0.50), top_y + int(H * 0.20)),
            (cx + s * chest_w, chest_y),
            (cx + s * int(chest_w * 0.55), top_y + int(H * 0.22)),
        ]
        pygame.draw.polygon(surf, VOID, sh)
        pygame.draw.polygon(surf, VOID_DK, sh, max(1, int(1.6 * ss)))

    # — The dissolving smoke hem (drawn before the hood so the hood layers clean).
    _smoke_dissolve(surf, cx, hem_y, W, ss, rng_seed=7)

    # — PEAKED HOOD: a forward-drooping cowl, the strongest silhouette hook. Built
    #   as a pointed cloth shape leaning slightly toward the held scythe, with a
    #   deep VOID cavity for the faceless interior.
    peak_y  = top_y - int(H * 0.02)
    hood_top = top_y + int(H * 0.02)
    hood = [
        (cx - int(W * 0.22), top_y + int(H * 0.18)),    # left jaw of the cowl
        (cx - int(W * 0.26), top_y + int(H * 0.09)),
        (cx - int(W * 0.04), peak_y),                   # the peak, leaning right
        (cx + int(W * 0.10), peak_y - int(H * 0.02)),   # forward droop tip
        (cx + int(W * 0.30), top_y + int(H * 0.10)),
        (cx + int(W * 0.24), top_y + int(H * 0.20)),    # right jaw
        (cx, top_y + int(H * 0.26)),                    # chin of the cowl
    ]
    pygame.draw.polygon(surf, VOID, hood)
    pygame.draw.polygon(surf, VOID_DK, hood, max(1, int(2 * ss)))

    # Hood cavity: a pure-VOID inner oval — the FACELESS dark — with a faint cold
    # soul bleed and two thin SOUL pinprick eyes. This is the only place the green
    # appears on the body, kept tiny so violet stays dominant.
    cav_cx, cav_cy = cx + int(W * 0.01), top_y + int(H * 0.165)
    cav = pygame.Rect(0, 0, int(W * 0.30), int(H * 0.13))
    cav.center = (cav_cx, cav_cy)
    pygame.draw.ellipse(surf, VOID_DK, cav)
    pygame.draw.ellipse(surf, (8, 6, 14), cav.inflate(-int(4 * ss), -int(4 * ss)))
    _blit_glow(surf, cav_cx, cav_cy + int(H * 0.01), int(W * 0.16), SOUL_DIM, 60)
    for s in (-1, 1):
        ex = cav_cx + s * int(W * 0.07)
        ey = cav_cy - int(H * 0.005)
        pygame.draw.line(surf, SOUL, (ex, ey - int(H * 0.018)),
                         (ex, ey + int(H * 0.018)), max(1, int(1.6 * ss)))
        _blit_glow(surf, ex, ey, max(3, int(4 * ss)), SOUL, 110)

    # — GREAT-SCYTHE, held across the body. The SNATH is the future pillar body:
    #   a long straight bone-grey shaft running top-to-bottom on the figure's left,
    #   gripped by a skeletal hand. The huge curved BLADE sweeps overhead as the
    #   gap-edge FLOURISH.
    snath_x = cx - int(W * 0.62)
    snath_top = top_y - int(H * 0.26)
    snath_bot = feet_y + int(H * 0.02)
    sw = max(2, int(5 * ss))
    # Shaft: dark-cored with a bone rail so it reads round and holds value.
    pygame.draw.line(surf, VOID_DK, (snath_x, snath_top), (snath_x, snath_bot), sw + max(1, int(2 * ss)))
    pygame.draw.line(surf, BONE_DK, (snath_x, snath_top), (snath_x, snath_bot), sw)
    pygame.draw.line(surf, BONE, (snath_x - int(1 * ss), snath_top),
                     (snath_x - int(1 * ss), snath_bot), max(1, int(2 * ss)))
    # A binding collar where the blade socket meets the snath.
    pygame.draw.circle(surf, VOID_DK, (snath_x, snath_top + int(6 * ss)), max(3, int(5 * ss)))
    pygame.draw.circle(surf, BONE_DK, (snath_x, snath_top + int(6 * ss)), max(2, int(3.5 * ss)))

    # The BLADE: a great curved bone hook arcing up + across from the snath top,
    # sweeping rightward overhead — the second unmistakable silhouette hook. Built
    # as a filled crescent (outer arc + inner arc) so it reads as a solid scythe
    # blade, with a hairline SOUL gleam tracing the cutting edge.
    bx, by = snath_x, snath_top + int(4 * ss)
    outer, inner, edge = [], [], []
    span = int(W * 1.15)
    rise = int(H * 0.30)
    for i in range(25):
        t = i / 24.0
        # A swept arc bowing up then curling forward to a tapered point.
        ax = bx + int(span * t)
        ay = by - int(rise * math.sin(t * math.pi * 0.92))
        thick = (1 - t) * int(W * 0.16) + int(3 * ss)
        outer.append((ax, ay - thick))
        inner.append((ax, ay))
        edge.append((ax, ay - thick))
    blade = outer + list(reversed(inner))
    pygame.draw.polygon(surf, BONE, blade)
    pygame.draw.polygon(surf, BONE_DK, blade, max(1, int(2 * ss)))
    # Spine shadow along the back of the blade for form.
    pygame.draw.lines(surf, BONE_DK, False, [(p[0], p[1] + int(3 * ss)) for p in outer],
                      max(1, int(2 * ss)))
    # Hairline cold SOUL gleam tracing the cutting (outer) edge — a thin accent.
    pygame.draw.lines(surf, SOUL, False, edge, max(1, int(1.4 * ss)))

    # — Skeletal BONE HAND gripping the snath at chest height (one strong shape +
    #   a couple of dark grooves; anatomy fizzes small, so keep it sparse).
    hx, hy = snath_x, chest_y + int(H * 0.02)
    # Wrist/sleeve cuff (void cloth) the hand emerges from.
    pygame.draw.polygon(surf, VOID, [
        (cx - chest_w + int(4 * ss), chest_y + int(6 * ss)),
        (hx + int(10 * ss), hy - int(8 * ss)),
        (hx + int(12 * ss), hy + int(12 * ss)),
        (cx - waist_w + int(2 * ss), waist_y - int(6 * ss)),
    ])
    # Palm + four bony fingers curling around the front of the shaft.
    pygame.draw.circle(surf, BONE_DK, (hx + int(2 * ss), hy), max(3, int(5 * ss)))
    pygame.draw.circle(surf, BONE, (hx + int(1 * ss), hy - int(1 * ss)), max(2, int(3.5 * ss)))
    for k in range(4):
        fy = hy - int(6 * ss) + k * int(4 * ss)
        pygame.draw.line(surf, BONE, (hx - int(3 * ss), fy), (hx + int(4 * ss), fy + int(1 * ss)),
                         max(1, int(2 * ss)))
        pygame.draw.line(surf, BONE_DK, (hx - int(3 * ss), fy + int(1 * ss)),
                         (hx + int(4 * ss), fy + int(2 * ss)), max(1, int(1 * ss)))

    # A few sparse drifting soul EMBERS rising off the figure — the only other
    # green, kept to 3 tiny additive motes so it stays an accent.
    for ex, ey in [(cx + int(W * 0.34), top_y + int(H * 0.30)),
                   (cx - int(W * 0.30), top_y + int(H * 0.50)),
                   (cx + int(W * 0.20), top_y + int(H * 0.66))]:
        _blit_glow(surf, ex, ey, max(2, int(3 * ss)), SOUL, 90)


# ── pillar-fit thumbnail ──────────────────────────────────────────────────────

def draw_snath_pillar(surf, cx, top, bot, w, ss, *, flip):
    """Prove the SNATH-as-pillar decision: the straight shaft is the vertical post
    that runs the full obstacle height; the curved blade is a GAP-EDGE FLOURISH at
    the inner (gap) end only — a readable hooked crescent flourishing INTO the gap,
    NOT a horizontal claw. `flip` mirrors it for the opposing (top vs bottom) pier
    so a top/bottom pair reads as one matched vertical obstacle."""
    # Shaft: full-height bone-grey post, dark-cored.
    pygame.draw.line(surf, VOID_DK, (cx, top), (cx, bot), w + max(1, int(2 * ss)))
    pygame.draw.line(surf, BONE_DK, (cx, top), (cx, bot), w)
    pygame.draw.line(surf, BONE, (cx - int(1 * ss), top), (cx - int(1 * ss), bot), max(1, int(2 * ss)))
    # Binding collars banding the post so it reads as a worked snath, not a stick.
    for cy in (top + int((bot - top) * 0.30), top + int((bot - top) * 0.62)):
        pygame.draw.circle(surf, VOID_DK, (cx, cy), max(3, int(4 * ss)))
        pygame.draw.circle(surf, BONE_DK, (cx, cy), max(2, int(2.6 * ss)))

    # The blade flourish at the GAP end (here the TOP end before any flip). It
    # curls FORWARD over the gap as a crescent hook — the same blade as the held
    # figure, now reading as a finial that frames the gap edge.
    gap_y = top
    bx = cx
    outer, inner = [], []
    span = int(34 * ss)
    rise = int(26 * ss)
    for i in range(20):
        t = i / 19.0
        ax = bx + int(span * t)
        ay = gap_y - int(rise * math.sin(t * math.pi * 0.9))
        thick = (1 - t) * int(9 * ss) + int(2 * ss)
        outer.append((ax, ay - thick))
        inner.append((ax, ay))
    blade = outer + list(reversed(inner))

    work = surf
    pygame.draw.polygon(work, BONE, blade)
    pygame.draw.polygon(work, BONE_DK, blade, max(1, int(1.6 * ss)))
    pygame.draw.lines(work, SOUL, False, outer, max(1, int(1.2 * ss)))
    # Socket collar where the blade meets the shaft top.
    pygame.draw.circle(work, VOID_DK, (cx, gap_y + int(4 * ss)), max(3, int(4 * ss)))
    pygame.draw.circle(work, BONE_DK, (cx, gap_y + int(4 * ss)), max(2, int(2.6 * ss)))


# ── sheet composition ─────────────────────────────────────────────────────────

def _sky_panel(w, h, night):
    """A day/night sky gradient + ground line matching the game's value range, so
    the reaper is judged against the real backdrop it must read on."""
    surf = pygame.Surface((w, h))
    if night:
        stops = [(0.0, (18, 20, 44)), (0.55, (40, 36, 70)), (1.0, (78, 60, 92))]
    else:
        stops = [(0.0, (150, 196, 232)), (0.55, (196, 222, 240)), (1.0, (228, 232, 224))]
    for y in range(h):
        t = y / h
        col = lerp_color(stops[0][1], stops[1][1], min(1.0, t / 0.55)) if t < 0.55 \
            else lerp_color(stops[1][1], stops[2][1], (t - 0.55) / 0.45)
        pygame.draw.line(surf, col, (0, y), (w, y))
    return surf


def main():
    ss = 3
    PANEL_W, PANEL_H = 460, 720
    ground_y = PANEL_H - 90
    GAP = 30
    THUMB_W = 300
    SHEET_W = PANEL_W * 2 + GAP * 3 + THUMB_W
    SHEET_H = PANEL_H + 120

    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((26, 24, 32))

    title_f = pygame.font.SysFont("dejavusans", 30, bold=True)
    label_f = pygame.font.SysFont("dejavusans", 19, bold=True)
    note_f = pygame.font.SysFont("dejavusans", 14)

    sheet.blit(title_f.render("EPIC EVENT-BOSS  —  reaper-shade  —  round 1", True, (236, 236, 240)), (28, 22))
    sheet.blit(note_f.render(
        "Death itself: faceless peaked HOOD, robe DISSOLVING into smoke (no feet), great-scythe overhead. "
        "Void-violet dominant; spectral green a thin accent only.",
        True, (170, 170, 184)), (28, 60))

    # Two big panels: day + night, full boss scale over a ground line.
    for i, (night, name) in enumerate([(False, "DAY SKY"), (True, "NIGHT SKY")]):
        px = GAP + i * (PANEL_W + GAP)
        py = 92
        # Render the specter at ss into an oversized scratch, then downscale for AA.
        big = pygame.Surface((PANEL_W * ss, PANEL_H * ss), pygame.SRCALPHA)
        draw_reaper(big, int(PANEL_W * 0.50 * ss), int(ground_y * ss), scale=0.78, ss=ss)
        small = pygame.transform.smoothscale(big, (PANEL_W, PANEL_H))

        panel = _sky_panel(PANEL_W, PANEL_H, night)
        # Ground line + a soft cast shadow under the gliding hem.
        pygame.draw.rect(panel, (40, 34, 30) if not night else (22, 20, 30),
                         (0, ground_y, PANEL_W, PANEL_H - ground_y))
        pygame.draw.line(panel, (60, 52, 44) if not night else (50, 44, 58),
                         (0, ground_y), (PANEL_W, ground_y), 2)
        sh = pygame.Surface((PANEL_W, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 70), (PANEL_W // 2 - 90, 6, 180, 22))
        panel.blit(sh, (0, ground_y - 8))
        panel.blit(small, (0, 0))

        sheet.blit(panel, (px, py))
        pygame.draw.rect(sheet, (70, 64, 80), (px, py, PANEL_W, PANEL_H), 1)
        lab = label_f.render(name, True, (236, 236, 240))
        sheet.blit(lab, (px + (PANEL_W - lab.get_width()) // 2, py + PANEL_H + 8))

    # Blackout silhouette strip overlaid on the day panel as a 1x read check.
    blk_w, blk_h = 150, 300
    blk = pygame.Surface((blk_w * ss, blk_h * ss), pygame.SRCALPHA)
    # Render in solid black to test the silhouette only.
    tmp = pygame.Surface((blk_w * ss, blk_h * ss), pygame.SRCALPHA)
    draw_reaper(tmp, int(blk_w * 0.52 * ss), int((blk_h - 18) * ss), scale=0.42, ss=ss)
    mask = pygame.mask.from_surface(tmp)
    sil = mask.to_surface(setcolor=(12, 10, 16, 255), unsetcolor=(0, 0, 0, 0))
    blk.blit(sil, (0, 0))
    blk_small = pygame.transform.smoothscale(blk, (blk_w, blk_h))
    bx = GAP + 6
    by = 92 + 6
    bsurf = pygame.Surface((blk_w + 12, blk_h + 30), pygame.SRCALPHA)
    bsurf.fill((230, 232, 236, 235))
    bsurf.blit(blk_small, (6, 24))
    bsurf.blit(note_f.render("blackout @1x", True, (40, 40, 48)), (8, 4))
    sheet.blit(bsurf, (bx, by))

    # — Pillar-fit thumbnail column on the right: a TOP + BOTTOM snath pillar pair
    #   over a sky strip, proving the mirror reads as a vertical obstacle.
    tx = GAP * 2 + PANEL_W * 2 + GAP
    ty = 92
    th = PANEL_H
    tw = THUMB_W
    thumb = _sky_panel(tw, th, False)
    # A gameplay gap: top pier hangs from the ceiling, bottom pier rises from floor.
    gap_top = int(th * 0.42)
    gap_bot = int(th * 0.62)
    col_x = tw // 2
    post_w = max(3, int(6 * ss))

    big_t = pygame.Surface((tw * ss, th * ss), pygame.SRCALPHA)
    # Bottom pier: post rises from the ground, blade flourishes UP into the gap.
    draw_snath_pillar(big_t, col_x * ss, gap_bot * ss, (th - 10) * ss, post_w, ss, flip=False)
    # Top pier: a mirror — post hangs from the ceiling, blade flourishes DOWN into
    # the gap. Built by drawing the same pillar then flipping the whole scratch.
    top_scratch = pygame.Surface((tw * ss, th * ss), pygame.SRCALPHA)
    draw_snath_pillar(top_scratch, col_x * ss, (th - gap_top) * ss, (th - 10) * ss, post_w, ss, flip=False)
    top_scratch = pygame.transform.flip(top_scratch, False, True)
    big_t.blit(top_scratch, (0, 0))

    small_t = pygame.transform.smoothscale(big_t, (tw, th))
    thumb.blit(small_t, (0, 0))
    # Mark the gap lane.
    pygame.draw.line(thumb, (90, 160, 110), (8, gap_top), (tw - 8, gap_top), 1)
    pygame.draw.line(thumb, (90, 160, 110), (8, gap_bot), (tw - 8, gap_bot), 1)
    thumb.blit(note_f.render("flap gap", True, (40, 80, 50)), (10, gap_top + 4))

    sheet.blit(thumb, (tx, ty))
    pygame.draw.rect(sheet, (70, 64, 80), (tx, ty, tw, th), 1)
    lab = label_f.render("PILLAR-FIT (snath=post)", True, (236, 236, 240))
    sheet.blit(lab, (tx + (tw - lab.get_width()) // 2, ty + th + 8))
    sheet.blit(note_f.render("blade = gap-edge flourish, not a claw", True, (170, 170, 184)),
               (tx + 4, ty + th + 32))

    out = "/home/user/skybit/docs/epic_boss/reaper-shade/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
