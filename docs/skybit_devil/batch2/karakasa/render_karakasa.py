"""
Round-1 review renderer for KARAKASA — the one-eyed hopping umbrella ghost
(Section 3 Japanese, sole object-spirit / tsukumogami).

House style: chibi, flat saturated fills, hard ink keylines, the
dark-core -> flat-fill -> top-left rim-sheen TRIAD, a 1px outline grown from
the alpha mask, and supersample -> smoothscale. The karakasa is the cleanest
single-object mirror in either batch: the creature IS the prop IS the pillar,
so the same ribbed-canopy + bamboo-shaft language drives both the creature and
its pillar tile.

Standalone headless script: writes round_1.png next to itself. No game imports
so the review sheet stays reproducible in isolation.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import math
import pygame

# ── PINNED PALETTE (exact hexes from the locked Karakasa brief) ─────────────
CANOPY    = (168, 66, 52)     # oxblood-paper canopy base
CANOPY_D  = (110, 40, 34)     # deep-maroon shade (dark core)
SHEEN     = (220, 128, 108)   # top-left rim sheen
RIB       = (204, 168, 96)    # ochre-bamboo ribs accent
RIB_D     = (150, 120, 60)    # rib dark core (derived, same bamboo family)
RIB_RIM   = (228, 200, 140)   # rib sheen (derived)
CREAM     = (232, 216, 182)   # cream oilpaper panel
CREAM_D   = (188, 170, 132)   # cream panel shade (derived)
EYE_WHITE = (244, 240, 230)   # big-eye white (derived warm white)
IRIS      = (244, 196, 72)    # amber iris
IRIS_D    = (188, 142, 40)    # amber iris shade (derived)
TONGUE    = (224, 108, 128)   # tongue-pink
TONGUE_D  = (176, 70, 92)     # tongue dark (derived)
TONGUE_RIM= (244, 158, 174)   # tongue sheen (derived)
INK       = (30, 22, 22)      # keyline ink
GETA      = (150, 108, 64)    # wooden geta clog (bamboo-ochre family)
GETA_D    = (104, 74, 40)
GETA_RIM  = (196, 154, 100)

SS = 4   # supersample factor for the large render


def _poly(surf, color, pts):
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])


def _ellipse(surf, color, cx, cy, rx, ry):
    pygame.draw.ellipse(surf, color, (int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2)))


def grow_outline(src, ink, px):
    """1px (scaled) ink keyline grown from the sprite's own alpha mask, so the
    silhouette POPs against any biome. We dilate by stamping the alpha mask in
    a ring of offsets behind the art."""
    mask = pygame.mask.from_surface(src)
    out = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    stamp = mask.to_surface(setcolor=(*ink, 255), unsetcolor=(0, 0, 0, 0))
    r = px
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                out.blit(stamp, (dx, dy))
    out.blit(src, (0, 0))
    return out


# ── shared canopy primitive (the same ribbed-dome language for both reads) ──

def draw_canopy(surf, P, top_y, half_w, depth, n_ribs=8, accent_panel=True):
    """A ribbed paper-parasol dome: oxblood panels split by ochre-bamboo ribs,
    triad-lit. `P` maps unit coords to surface px. The dome apex sits at
    (0, top_y); it bells out to `half_w` and drops `depth` below the apex —
    the SAME shape both the creature canopy and the pillar cap reuse so the
    mirror reads as one object."""
    rim_y = top_y + depth                # where the canopy hem sits
    # dome silhouette (dark core), a fat near-half-ellipse fanning down
    dome = [(P(-half_w, rim_y)),
            (P(-half_w * 0.96, rim_y - depth * 0.5)),
            (P(-half_w * 0.5, top_y + depth * 0.12)),
            (P(0, top_y)),
            (P(half_w * 0.5, top_y + depth * 0.12)),
            (P(half_w * 0.96, rim_y - depth * 0.5)),
            (P(half_w, rim_y))]
    _poly(surf, CANOPY_D, dome)
    # flat fill, pulled in + down-right so a dark-core rim survives on the
    # lower-right + bottom
    fill = [(P(-half_w * 0.9 + 1, rim_y - 1)),
            (P(-half_w * 0.88 + 1, rim_y - depth * 0.5)),
            (P(-half_w * 0.46 + 1, top_y + depth * 0.16 + 1)),
            (P(0 + 1, top_y + 1.4)),
            (P(half_w * 0.46 + 1, top_y + depth * 0.16 + 1)),
            (P(half_w * 0.88 + 1, rim_y - depth * 0.5)),
            (P(half_w * 0.9 - 1, rim_y - 1))]
    _poly(surf, CANOPY, fill)

    # cream oilpaper panels alternate with oxblood for the wagasa two-tone read.
    # They sit OFF-centre (mid-way out on each side) so the central column stays
    # oxblood for the giant eye to read as the hero focal — alternating wagasa
    # panels, not a central block.
    if accent_panel:
        for k in (-1, 1):
            x0, x1 = k * half_w * 0.30, k * half_w * 0.62
            seg = [(P(0, top_y + 1)),
                   (P(x0, top_y + depth * 0.42)),
                   (P(x0, rim_y - 1)),
                   (P(x1, rim_y - 1)),
                   (P(x1, rim_y - depth * 0.5)),
                   (P(0, top_y + 1))]
            _poly(surf, CREAM_D, [(x, y) for x, y in seg])
            seg2 = [(P(0, top_y + 2.4)),
                    (P(x0 * 0.96, top_y + depth * 0.44)),
                    (P(x0 * 0.96, rim_y - 2)),
                    (P(x1 * 0.96, rim_y - 2)),
                    (P(x1 * 0.96, rim_y - depth * 0.5)),
                    (P(0, top_y + 2.4))]
            _poly(surf, CREAM, [(x, y) for x, y in seg2])

    # top-left rim sheen — a bright crescent on the dome's upper-left shoulder
    sheen = [(P(-half_w * 0.86, rim_y - depth * 0.42)),
             (P(-half_w * 0.5, top_y + depth * 0.16)),
             (P(-half_w * 0.12, top_y + 1.5)),
             (P(-half_w * 0.2, top_y + depth * 0.34)),
             (P(-half_w * 0.5, top_y + depth * 0.5)),
             (P(-half_w * 0.78, rim_y - depth * 0.34))]
    _poly(surf, SHEEN, sheen)

    # radial bamboo ribs splaying from apex to hem (the repeatable banding)
    for i in range(n_ribs + 1):
        t = i / n_ribs
        rx = (-1 + 2 * t) * half_w * 0.94
        # rib tip rides the dome curve: deeper toward the edges
        edge = abs(-1 + 2 * t)
        tip_y = top_y + depth * (0.16 + 0.84 * edge) - depth * 0.04
        ax, ay = P(0, top_y + 1)
        tx, ty = P(rx, tip_y)
        pygame.draw.line(surf, RIB_D, (ax, ay), (tx, ty), max(2, int(1.7 * (P(1, 0)[0] - P(0, 0)[0]))))
        # lit rib hair offset up-left
        pygame.draw.line(surf, RIB, (ax, ay - 1), (tx - 1, ty - 1),
                         max(1, int(1.0 * (P(1, 0)[0] - P(0, 0)[0]))))

    # hem rib-tip beads + a scalloped lower edge (the paper-parasol fringe)
    for i in range(n_ribs + 1):
        t = i / n_ribs
        rx = (-1 + 2 * t) * half_w * 0.94
        edge = abs(-1 + 2 * t)
        tip_y = top_y + depth * (0.16 + 0.84 * edge) - depth * 0.04
        _ellipse(surf, RIB, *P(rx, tip_y), 1.6, 1.6)
        _ellipse(surf, RIB_RIM, *P(rx - 0.4, tip_y - 0.4), 0.7, 0.7)

    # apex bamboo nub (ishizuki ferrule) where the ribs gather
    _ellipse(surf, RIB_D, *P(0, top_y - 1), 3, 2.6)
    _ellipse(surf, RIB, *P(0, top_y - 1.4), 2.2, 1.9)
    _ellipse(surf, RIB_RIM, *P(-0.6, top_y - 2), 1.0, 0.9)
    return rim_y


def draw_karakasa(surf, ox, oy, s):
    """Draw the one-eyed hopping umbrella ghost centred near (ox, oy). `s` is
    unit scale. Tall vertical: ribbed canopy up top, one giant eye where the
    panels meet, a long lolling tongue below the hem, one bare leg + geta clog,
    tiny stick arms. The creature IS the prop."""

    def P(x, y):  # local unit coords -> surface px
        return (ox + x * s, oy + y * s)

    # ---- single bare leg + bamboo shaft descending from the canopy ----
    # (drawn first so the hem + tongue overlap its top)
    leg_x = 1
    # shaft stub the canopy rides (continuous with the bamboo handle)
    pygame.draw.line(surf, RIB_D, P(leg_x - 0.6, 6), P(leg_x - 0.6, 30), max(3, int(3.4 * s)))
    pygame.draw.line(surf, RIB, P(leg_x - 0.6, 6), P(leg_x - 0.6, 30), max(2, int(2.0 * s)))
    pygame.draw.line(surf, RIB_RIM, P(leg_x - 1.4, 7), P(leg_x - 1.4, 26), max(1, int(s)))
    # node bands on the leg-shaft (matches the pillar banding)
    for ny in (12, 21):
        _ellipse(surf, RIB_D, *P(leg_x - 0.6, ny), 2.6, 1.4)
        pygame.draw.line(surf, RIB_RIM, P(leg_x - 1.6, ny - 0.4), P(leg_x + 0.2, ny - 0.4), max(1, int(s)))

    # ---- geta clog (wooden sandal) at the foot, mid-hop tilt ----
    gx, gy = leg_x, 32
    sole = [(-8, -1), (9, -3), (10, 2), (-7, 3.5)]      # tilted plank
    _poly(surf, GETA_D, [P(gx + x, gy + y + 0.8) for x, y in sole])
    sole2 = [(-7, -1), (8, -3), (8.6, 1.4), (-6, 2.6)]
    _poly(surf, GETA, [P(gx + x, gy + y) for x, y in sole2])
    pygame.draw.line(surf, GETA_RIM, P(gx - 6.5, gy - 1.2), P(gx + 7.5, gy - 2.8), max(1, int(s)))
    # two teeth (ha) under the plank
    for tx in (-4, 5):
        _poly(surf, GETA_D, [P(gx + tx - 1.5, gy + 3), P(gx + tx + 1.5, gy + 2.6),
                             P(gx + tx + 1.6, gy + 6.5), P(gx + tx - 1.4, gy + 6.9)])
    # toe-thong V
    pygame.draw.line(surf, INK, P(gx + 0.5, gy - 2.4), P(gx - 4, gy + 0.6), max(1, int(s)))
    pygame.draw.line(surf, INK, P(gx + 0.5, gy - 2.4), P(gx + 5, gy - 0.4), max(1, int(s)))

    # ---- tiny stick arms (spread, hopping-startled pose) ----
    for side in (-1, 1):
        ax0 = P(side * 9, 8)
        ael = P(side * 17, 3 + (2 if side < 0 else -1))   # asymmetric for life
        ahd = P(side * 21, -2 + (3 if side < 0 else -2))
        pygame.draw.line(surf, CANOPY_D, ax0, ael, max(2, int(2.0 * s)))
        pygame.draw.line(surf, CANOPY_D, ael, ahd, max(2, int(2.0 * s)))
        pygame.draw.line(surf, RIB, ax0, ael, max(1, int(s)))
        pygame.draw.line(surf, RIB, ael, ahd, max(1, int(s)))
        # three little finger-twigs
        for fa in (-0.5, 0.0, 0.5):
            fx = ahd[0] + math.cos(-1.2 + fa) * 4.2 * s * side
            fy = ahd[1] + math.sin(-1.2 + fa) * 4.2 * s
            pygame.draw.line(surf, CANOPY_D, ahd, (fx, fy), max(1, int(s)))

    # ---- ribbed paper canopy (the body) ----
    rim_y = draw_canopy(surf, P, top_y=-26, half_w=22, depth=24, n_ribs=8)

    # ---- mouth + long lolling tongue below the hem ----
    mcx, mcy = 1, rim_y - 0.5
    # dark mouth slot tucked under the canopy hem
    _ellipse(surf, INK, *P(mcx, mcy + 1.5), 8, 4)
    _ellipse(surf, CANOPY_D, *P(mcx, mcy + 0.4), 7.5, 3.4)
    # upper row of tiny teeth
    for txx in range(-6, 7, 3):
        _poly(surf, CREAM, [P(mcx + txx - 1, mcy - 0.5), P(mcx + txx + 1, mcy - 0.5),
                            P(mcx + txx, mcy + 1.6)])
    # the long tongue — a tapering pink ribbon that lolls + curls
    tongue = [(-5, 0), (-6.5, 7), (-4.5, 15), (-6, 22), (-2, 27),
              (3, 24), (1.5, 16), (4, 8), (5, 1)]
    _poly(surf, TONGUE_D, [P(mcx + x, mcy + 2.5 + y + 0.6) for x, y in tongue])
    tongue2 = [(-4, 0.4), (-5.4, 7), (-3.6, 14.5), (-4.8, 21), (-2, 25.5),
               (2.2, 23), (0.8, 15.5), (3, 8), (4, 1.2)]
    _poly(surf, TONGUE, [P(mcx + x, mcy + 2.5 + y) for x, y in tongue2])
    # tongue centre-crease + sheen
    pygame.draw.line(surf, TONGUE_D, P(mcx - 1, mcy + 4), P(mcx - 1.5, mcy + 24), max(1, int(s)))
    pygame.draw.line(surf, TONGUE_RIM, P(mcx - 3.4, mcy + 4), P(mcx - 4.2, mcy + 18), max(1, int(s)))

    # ---- one giant central EYE where the panels meet (drawn last = focal) ----
    # Sits high + large so it unmistakably dominates the canopy face; only a
    # light upper-lid arc droops in for scary-cute menace, never burying it.
    ecx, ecy = 1, -7
    _ellipse(surf, INK, *P(ecx, ecy + 0.4), 12.6, 12.6)            # ink ring
    _ellipse(surf, EYE_WHITE, *P(ecx, ecy), 11.4, 11.4)           # huge sclera
    # amber iris + pupil (large — the amber is a focal mass, not a dot)
    _ellipse(surf, IRIS_D, *P(ecx + 0.6, ecy + 1.4), 7.8, 7.8)
    _ellipse(surf, IRIS, *P(ecx, ecy + 0.8), 7.1, 7.1)
    _ellipse(surf, INK, *P(ecx + 0.6, ecy + 1.2), 3.4, 3.4)        # pupil
    # light upper-lid arc only — a thin oxblood crescent skimming the top so the
    # eye keeps its full round read while gaining a hooded glare
    lid = [(-12, -11), (12, -11), (11, -6.5), (4, -8.6), (-3, -8.0),
           (-10, -8.8)]
    _poly(surf, CANOPY_D, [P(ecx + x, ecy + y) for x, y in lid])
    # twin catchlights (top-left, keeps the triad light direction)
    _ellipse(surf, EYE_WHITE, *P(ecx - 2.8, ecy - 2.2), 2.0, 2.0)
    _ellipse(surf, EYE_WHITE, *P(ecx + 2.4, ecy + 3.0), 1.0, 1.0)
    # bloodshot oxblood veins flicking off the sclera (paper-spirit menace)
    for va, vl in ((2.4, 3), (3.0, 2.5)):
        vx = ecx + math.cos(va) * 9
        vy = ecy + math.sin(va) * 9
        pygame.draw.line(surf, CANOPY, P(ecx + math.cos(va) * 6, ecy + math.sin(va) * 6),
                         P(vx, vy), max(1, int(s)))
    # lower lash flick for the hooded look
    pygame.draw.line(surf, INK, P(ecx - 9.5, ecy + 7.5), P(ecx - 4, ecy + 10.5), max(1, int(s)))
    pygame.draw.line(surf, INK, P(ecx + 9.5, ecy + 7.5), P(ecx + 4, ecy + 10.5), max(1, int(s)))


def draw_canopy_pillar(surf, cx, top, bottom, w, cap=True):
    """Prop -> PILLAR mirror: the karakasa's own parasol. The long bamboo
    umbrella-HANDLE is the repeatable rib-banded shaft body; the open ribbed
    CANOPY blooms at the gap as the detachable gap-edge cap. Creature = prop =
    pillar — the cleanest single-object mirror; canopy is round/symmetric
    on-axis."""
    half = w // 2
    u = w / 24.0                     # unit so the banding scales with width
    # ---- bamboo handle shaft body ----
    pygame.draw.rect(surf, RIB_D, (cx - half - 2, top, w + 4, bottom - top))
    pygame.draw.rect(surf, RIB, (cx - half, top, w, bottom - top))
    # top-left rim sheen stripe
    pygame.draw.rect(surf, RIB_RIM, (cx - half + 2, top, max(2, w // 5), bottom - top))
    # node bands (the repeatable banding — same language as the leg-shaft)
    seg_h = w * 1.7
    y = top + seg_h
    while y < bottom:
        pygame.draw.rect(surf, RIB_D, (cx - half - 3, int(y) - 3, w + 6, 6))
        pygame.draw.line(surf, RIB_RIM, (cx - half + 2, int(y) - 3), (cx - half + 2, int(y) + 3), 2)
        y += seg_h

    if cap:
        # ---- gap-edge cap: the open ribbed parasol canopy blooming at the gap.
        # Reuse the creature's canopy primitive so the mirror is literal.
        def P(x, yy):
            return (cx + x * u, top + yy * u)
        # canopy apex above the shaft top, hem flaring out past shaft width
        draw_canopy(surf, P, top_y=-30, half_w=half / u + 8, depth=26, n_ribs=10)


def build_karakasa_sprite(unit_px):
    """Render the karakasa at unit_px supersampled, outline from its alpha
    mask, return the high-res surface (caller smoothscales)."""
    W = int(58 * unit_px)
    H = int(76 * unit_px)
    big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    # centre: canopy near top, tongue + leg + geta trailing below
    draw_karakasa(big, big.get_width() // 2, int(H * SS * 0.46), unit_px * SS)
    big = grow_outline(big, INK, SS)   # 1px @ final scale
    return big, (W, H)


def build_pillar_sprite(unit_px):
    W = int(46 * unit_px)
    H = int(98 * unit_px)
    big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    draw_canopy_pillar(big, big.get_width() // 2,
                       int(30 * unit_px * SS), big.get_height(),
                       int(13 * unit_px * SS), cap=True)
    big = grow_outline(big, INK, SS)
    return big, (W, H)


def main():
    pygame.init()

    SHEET_W, SHEET_H = 760, 560
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sky_a, sky_b = (190, 168, 158), (150, 120, 116)   # warm dusk so oxblood reads honest
    for y in range(SHEET_H):
        t = y / SHEET_H
        c = tuple(int(sky_a[i] + (sky_b[i] - sky_a[i]) * t) for i in range(3))
        pygame.draw.line(sheet, c, (0, y), (SHEET_W, y))

    font = pygame.font.SysFont("dejavusans", 18, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)

    def label(text, x, y, col=(28, 20, 20)):
        sheet.blit(font.render(text, True, (250, 246, 240)), (x + 1, y + 1))
        sheet.blit(font.render(text, True, col), (x, y))

    def slabel(text, x, y):
        sheet.blit(small.render(text, True, (250, 246, 240)), (x + 1, y + 1))
        sheet.blit(small.render(text, True, (30, 22, 22)), (x, y))

    title = pygame.font.SysFont("dejavusans", 22, bold=True)
    sheet.blit(title.render("KARAKASA — one-eyed hopping umbrella ghost", True, (250, 246, 240)), (19, 13))
    sheet.blit(title.render("KARAKASA — one-eyed hopping umbrella ghost", True, (40, 24, 22)), (18, 12))
    sheet.blit(small.render("sole object-spirit (tsukumogami)  ·  oxblood + ochre-bamboo + amber  ·  creature IS prop IS pillar",
                            True, (40, 26, 24)), (18, 38))

    # ---- large creature ----
    big_c, _ = build_karakasa_sprite(5.0)
    large_c = pygame.transform.smoothscale(big_c, (big_c.get_width() // SS, big_c.get_height() // SS))
    sheet.blit(large_c, (20, 66))
    label("creature", 95, 60 + large_c.get_height())

    # ---- large pillar mirror ----
    big_p, _ = build_pillar_sprite(4.4)
    large_p = pygame.transform.smoothscale(big_p, (big_p.get_width() // SS, big_p.get_height() // SS))
    sheet.blit(large_p, (320, 60))
    label("parasol pillar", 312, 60 + large_p.get_height())
    slabel("canopy-cap blooms into gap · rib-banded handle repeats", 296, 80 + large_p.get_height())

    # ---- scale strip: creature + pillar on light & dark panels ----
    def to_h(big, target_h):
        w, h = big.get_size()
        scale = (target_h * SS) / h
        return pygame.transform.smoothscale(big, (max(1, int(w * scale / SS)), target_h))

    panel_x = 540
    pygame.draw.rect(sheet, (240, 232, 222), (panel_x, 66, 200, 214), border_radius=8)
    pygame.draw.rect(sheet, (60, 40, 38), (panel_x, 66, 200, 214), 2, border_radius=8)
    pygame.draw.rect(sheet, (26, 30, 50), (panel_x, 300, 200, 200), border_radius=8)
    pygame.draw.rect(sheet, (90, 96, 124), (panel_x, 300, 200, 200), 2, border_radius=8)

    slabel("32px on dusk sky", panel_x + 10, 72)
    sheet.blit(to_h(big_c, 36), (panel_x + 26, 100))
    sheet.blit(to_h(big_p, 70), (panel_x + 118, 96))

    slabel("48px detail", panel_x + 10, 198)
    c48 = pygame.transform.smoothscale(big_c, (int(big_c.get_width() / SS * 0.6),
                                               int(big_c.get_height() / SS * 0.6)))
    sheet.blit(c48, (panel_x + 18, 148))

    slabel("32px on night sky", panel_x + 10, 308)
    sheet.blit(to_h(big_c, 36), (panel_x + 26, 336))
    sheet.blit(to_h(big_p, 70), (panel_x + 118, 332))
    slabel("24px silhouette", panel_x + 10, 432)
    sheet.blit(to_h(big_c, 24), (panel_x + 36, 456))
    sheet.blit(to_h(big_p, 48), (panel_x + 128, 450))

    # palette swatches
    swatches = [("canopy", CANOPY), ("shade", CANOPY_D), ("rib", RIB),
                ("cream", CREAM), ("amber", IRIS), ("tongue", TONGUE), ("sheen", SHEEN)]
    sx = 24
    sy = 506
    slabel("pinned palette:", sx, sy - 18)
    for name, col in swatches:
        pygame.draw.rect(sheet, col, (sx, sy, 30, 30), border_radius=4)
        pygame.draw.rect(sheet, (28, 20, 20), (sx, sy, 30, 30), 1, border_radius=4)
        sheet.blit(small.render(name, True, (250, 246, 240)), (sx + 1, sy + 31))
        sheet.blit(small.render(name, True, (30, 22, 22)), (sx, sy + 30))
        sx += 68

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
