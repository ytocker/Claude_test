"""MARROW-SKEWER clown-event bone column — matured round-1 render.

A single central gold-cored marrow-spike runs the full pillar height; loose
vertebra discs (with wing-process side-nubs) and the occasional small skull are
threaded onto it like beads, with VISIBLE AIR between them. The cadence repeats
so the column tiles, and the spike emerges past the last bead as a barbed
bone-point aimed INTO the gap — the threading hardware is the cap/focal.

Identity rule (the art-director's distinctness fix): the daylight BETWEEN beads
is the whole read. The air-gap-to-bead ratio is exaggerated and the beads
ALTERNATE vertebra-disc vs. small-skull on a coarse cadence so the column never
drifts toward a solid bone stack. The honest collision edge is the spine itself.

Bone-roster house style: warm-ivory bone, hard 1-2px ink keyline, dark-core ->
flat-fill -> top-left rim-sheen triad, gold thin-accent tracing (the spike core
is gold), faceted cyan/purple wisdom gems, supersample -> smoothscale, plus a
1px alpha-grown silhouette outline. Borrows the Nagaraja vertebral grammar and
the staff/skewer idiom.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import math
import pygame

pygame.init()

# ── Bone-roster palette (locked batch2 house style) ──────────────────────────
INK     = (28, 22, 30)
BONE    = (228, 222, 206)
BONE_DK = (150, 144, 128)
BONE_CORE = (108, 102, 90)          # deepest under-shade for the dark-cored read
BONE_HI = (250, 247, 236)
GOLD    = (250, 205, 72)
GOLD_HI = (255, 236, 150)
GOLD_DK = (176, 130, 30)
GOLD_SHADOW = (110, 78, 22)
CYAN    = (120, 214, 222)
CYAN_HI = (224, 252, 252)
PURPLE  = (158, 120, 214)
PURPLE_HI = (224, 206, 250)

PW = 58                              # PIPE_W gameplay column width
OVERHANG = 7                         # wing-process nubs may spill past the column


def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


# ── The threaded hardware: a gold-cored marrow spike ─────────────────────────

def marrow_spike(surf, cx, top_y, bot_y, ss):
    """The full-height central spike the beads are threaded on. A dark bone rod
    cored gold so the spine reads as the honest collision edge AND as the gold
    thread of the bead string. Drawn FIRST so beads seat over it; the air gaps
    expose this rod, which is the whole 'threaded' tell."""
    hw = int(4 * ss)                 # rod half-width — the honest collision spine
    # Dark bone casing with a hard keyline so the rod holds value in the gaps.
    pygame.draw.line(surf, INK, (cx, top_y), (cx, bot_y), hw * 2 + int(2 * ss))
    pygame.draw.line(surf, BONE_DK, (cx, top_y), (cx, bot_y), hw * 2)
    pygame.draw.line(surf, BONE, (cx - int(ss), top_y), (cx - int(ss), bot_y),
                     max(1, int(1.4 * ss)))
    # The molten gold marrow core threading the whole string.
    pygame.draw.line(surf, GOLD_DK, (cx, top_y), (cx, bot_y), max(2, int(2.6 * ss)))
    pygame.draw.line(surf, GOLD, (cx, top_y), (cx, bot_y), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, GOLD_HI, (cx - int(0.6 * ss), top_y),
                     (cx - int(0.6 * ss), bot_y), max(1, int(ss)))


def _bone_triad_ellipse(surf, rect, ss):
    """A vertebra disc body in the dark-core -> flat-fill -> top-left rim-sheen
    triad, with the hard ink keyline."""
    pygame.draw.ellipse(surf, INK, rect.inflate(int(2 * ss), int(2 * ss)))
    pygame.draw.ellipse(surf, BONE_CORE, rect)
    # Flat ivory fill lifted off the bottom so the lower lip stays dark-cored.
    fill = rect.inflate(-int(2 * ss), -int(2 * ss))
    fill.y -= int(ss)
    pygame.draw.ellipse(surf, BONE, fill)
    # Top-left rim sheen.
    sheen = pygame.Rect(rect.x + int(4 * ss), rect.y + int(2 * ss),
                        int(rect.w * 0.5), int(rect.h * 0.42))
    pygame.draw.ellipse(surf, BONE_HI, sheen)


def vertebra_bead(surf, cx, cy, ss, *, gem_col):
    """A loose vertebra DISC threaded on the spike: a wide flat centrum with a
    pair of wing-process side-nubs and a faceted wisdom-gem foramen at its core.
    Wider than the column so the bead reads as hardware slid onto the rod, not as
    column mass. The gap above/below it is left as bare spike (the air read)."""
    half_w = int((PW * 0.5 + OVERHANG - 2) * ss)   # spills to the wing nubs
    half_h = int(8 * ss)

    # Wing-process side-nubs FIRST (behind the centrum) — the transverse processes
    # that make a vertebra read as a vertebra, not a generic bead.
    for s in (-1, 1):
        wx = cx + s * (half_w - int(3 * ss))
        nub = pygame.Rect(0, 0, int(10 * ss), int(8 * ss))
        nub.center = (wx, cy)
        pygame.draw.ellipse(surf, INK, nub.inflate(int(2 * ss), int(2 * ss)))
        pygame.draw.ellipse(surf, BONE_DK, nub)
        pygame.draw.ellipse(surf, BONE, nub.inflate(-int(3 * ss), -int(3 * ss)))
        pygame.draw.circle(surf, BONE_HI,
                           (wx - int(2 * ss), cy - int(2 * ss)), max(1, int(1.6 * ss)))

    # The flat centrum disc.
    body = pygame.Rect(0, 0, half_w * 2 - int(8 * ss), half_h * 2)
    body.center = (cx, cy)
    _bone_triad_ellipse(surf, body, ss)

    # A faint pinch-line each side reads the disc as a stacked vertebral plate.
    for s in (-1, 1):
        px = cx + s * int(half_w * 0.46)
        pygame.draw.line(surf, _shade(BONE_DK, -16),
                         (px, cy - int(4 * ss)), (px, cy + int(4 * ss)),
                         max(1, int(ss)))

    # The neural foramen at the core: a small faceted wisdom gem the spike pierces.
    _gem(surf, cx, cy, int(4.4 * ss), ss, col=gem_col)


def skull_bead(surf, cx, cy, ss, *, eye=CYAN):
    """A small SKULL threaded on the spike — the alternate bead on the coarse
    cadence so the string never reads as a uniform disc stack. Narrower than the
    discs (skulls are round, not winged), which further varies the silhouette
    rhythm and keeps the air gaps obvious."""
    r = int(11 * ss)
    # Cranium triad.
    pygame.draw.circle(surf, INK, (cx, cy), r + int(ss))
    pygame.draw.circle(surf, BONE_CORE, (cx, cy), r)
    pygame.draw.circle(surf, BONE, (cx, cy - int(ss)), r - int(1.5 * ss))
    pygame.draw.circle(surf, BONE_HI, (cx - r // 3, cy - r // 3), r // 3)

    # Eye sockets cored dark with a soul-light pin so the bead reads "alive".
    for s in (-1, 1):
        ex = cx + s * int(r * 0.46)
        ey = cy - int(r * 0.18)
        pygame.draw.circle(surf, INK, (ex, ey), int(r * 0.34))
        pygame.draw.circle(surf, eye, (ex, ey), max(1, int(r * 0.2)))
        pygame.draw.circle(surf, CYAN_HI, (ex - int(ss), ey - int(ss)),
                           max(1, int(r * 0.09)))
    # Small triangular nasal aperture.
    pygame.draw.polygon(surf, INK,
                        [(cx, cy + int(r * 0.12)),
                         (cx - int(r * 0.16), cy + int(r * 0.42)),
                         (cx + int(r * 0.16), cy + int(r * 0.42))])
    # The jaw teeth — short ink ticks so the skull reads at size.
    jy = cy + int(r * 0.5)
    pygame.draw.line(surf, _shade(BONE_DK, -10),
                     (cx - int(r * 0.5), jy), (cx + int(r * 0.5), jy),
                     max(1, int(1.4 * ss)))
    for i in range(-2, 3):
        tx = cx + i * int(r * 0.26)
        pygame.draw.line(surf, INK, (tx, jy), (tx, jy + int(r * 0.34)),
                         max(1, int(ss)))


def _gem(surf, cx, cy, r, ss, *, col):
    """A faceted wisdom gem (cyan/purple) with the ink keyline + bright glint —
    the diamond cabochon the marrow spike threads through."""
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in pts])
    inner = [(cx, cy - r + ss), (cx + r - ss, cy),
             (cx, cy + r - ss), (cx - r + ss, cy)]
    pygame.draw.polygon(surf, _shade(col, -40), [(int(x), int(y)) for x, y in inner])
    # Lit left facet so the gem reads cut, not a flat lozenge.
    pygame.draw.polygon(surf, col,
                        [(int(cx), int(cy - r + ss)), (int(cx), int(cy + r - ss)),
                         (int(cx - r + ss), int(cy))])
    pygame.draw.circle(surf, CYAN_HI if col is CYAN else PURPLE_HI,
                       (int(cx - r * 0.3), int(cy - r * 0.3)), max(1, int(r * 0.3)))


def barbed_point(surf, cx, tip_y, base_y, ss):
    """The spike emerges past the last bead as a barbed bone-point aimed INTO the
    gap — the threading hardware is the cap. A tapered ivory blade with two
    rear-swept barbs and a thin gold marrow seam running to the tip."""
    hw = int(7 * ss)
    # The barbs (rear-swept hooks) at the blade root.
    for s in (-1, 1):
        barb = [(cx + s * int(2 * ss), base_y - int(10 * ss)),
                (cx + s * int(13 * ss), base_y - int(2 * ss)),
                (cx + s * int(5 * ss), base_y + int(2 * ss))]
        pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in barb])
        pygame.draw.polygon(surf, BONE,
                            [(int(x - s * ss), int(y)) for x, y in barb])
        pygame.draw.polygon(surf, BONE_HI,
                            [(int(cx + s * int(2 * ss)), int(base_y - int(9 * ss))),
                             (int(cx + s * int(8 * ss)), int(base_y - int(3 * ss))),
                             (int(cx + s * int(4 * ss)), int(base_y))])
    # The blade body — a long tapered triangle from base to tip.
    blade = [(cx - hw, base_y), (cx + hw, base_y), (cx, tip_y)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in blade])
    pygame.draw.polygon(surf, BONE_CORE,
                        [(int(cx - hw + ss), int(base_y)),
                         (int(cx + hw - ss), int(base_y)), (int(cx), int(tip_y))])
    pygame.draw.polygon(surf, BONE,
                        [(int(cx - hw + int(2 * ss)), int(base_y - int(ss))),
                         (int(cx + hw - int(2 * ss)), int(base_y - int(ss))),
                         (int(cx), int(tip_y + int(2 * ss)))])
    # Lit left bevel reads the point as faceted, not flat.
    pygame.draw.polygon(surf, BONE_HI,
                        [(int(cx - hw + int(2 * ss)), int(base_y - int(ss))),
                         (int(cx - int(ss)), int(base_y - int(ss))),
                         (int(cx), int(tip_y + int(3 * ss)))])
    # The gold marrow seam runs out to (but not through) the very tip.
    pygame.draw.line(surf, GOLD_DK, (cx, base_y), (cx, tip_y + int(5 * ss)),
                     max(1, int(1.8 * ss)))
    pygame.draw.line(surf, GOLD, (cx, base_y), (cx, tip_y + int(7 * ss)),
                     max(1, int(ss)))


# ── Cadence: alternate disc / skull with exaggerated air gaps ─────────────────
# A coarse 3-step pattern so the bead identity alternates legibly and the daylight
# between beads dominates. The pitch is deliberately large vs. the bead height.
BEAD_PITCH = 46                      # 1x px between bead centres (big air gap)
# Pattern read top->gap: disc, skull, disc  (repeats). Wing discs and round skulls
# alternate so the silhouette rhythm reads "threaded beads", never a solid stack.
CADENCE = ("disc", "skull", "disc")


def _bead_at(surf, cx, cy, idx, ss):
    kind = CADENCE[idx % len(CADENCE)]
    if kind == "skull":
        skull_bead(surf, cx, cy, ss, eye=CYAN if idx % 2 == 0 else CYAN)
    else:
        # Discs alternate gem colour on a slow beat for a little life.
        gem_col = PURPLE if (idx // 2) % 2 else CYAN
        vertebra_bead(surf, cx, cy, ss, gem_col=gem_col)


def render_column(H, ss, *, flip):
    """Render ONE half-column `H` px tall at supersample `ss`, beads threaded down
    the spike with the barbed point seated at the GAP end. `flip` mirrors so the
    point can aim up (bottom pillar) or down (top pillar)."""
    box_w = (PW + 2 * OVERHANG) * ss
    box_h = max(1, int(H)) * ss
    surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    cx = box_w // 2

    # The spike spans the full height (it is the spine / collision edge). It stops
    # short of the gap end where the barbed point takes over.
    point_base = box_h - int(34 * ss)
    spike_top = -int(6 * ss)         # run off the far end so tiling is seamless
    marrow_spike(surf, cx, spike_top, point_base, ss)

    # Thread beads down the spike from the far end toward the gap, on the cadence.
    pitch = int(BEAD_PITCH * ss)
    # First bead centre sits a half-pitch in so a partial gap sits at the tile seam.
    y = int(box_h - 34 * ss - 18 * ss)   # nearest bead just above the point base
    idx = 0
    while y > int(10 * ss):
        _bead_at(surf, cx, y, idx, ss)
        y -= pitch
        idx += 1

    # The barbed bone-point at the gap end — the threading hardware is the cap.
    barbed_point(surf, cx, box_h - int(2 * ss), point_base, ss)

    # Supersample down with a 1px alpha-grown silhouette outline (house finish).
    small = pygame.transform.smoothscale(surf, (PW + 2 * OVERHANG, max(1, int(H))))
    small = _grow_outline(small)
    if flip:
        small = pygame.transform.flip(small, False, True)
    return small


def _grow_outline(surf):
    """Grow a 1px ink silhouette outline by alpha-dilating the sprite — the
    roster's finishing pass so the bone reads crisp against any sky."""
    w, h = surf.get_size()
    mask = pygame.mask.from_surface(surf, 8)
    outline = pygame.Surface((w, h), pygame.SRCALPHA)
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        shifted = pygame.Surface((w, h), pygame.SRCALPHA)
        shifted.blit(mask.to_surface(setcolor=(*INK, 255), unsetcolor=(0, 0, 0, 0)),
                     (ox, oy))
        outline.blit(shifted, (0, 0))
    outline.blit(surf, (0, 0))
    return outline


# ── Review sheet ──────────────────────────────────────────────────────────────

def _sky(w, h, top, bot):
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        s.fill((int(top[0] + (bot[0] - top[0]) * t),
                int(top[1] + (bot[1] - top[1]) * t),
                int(top[2] + (bot[2] - top[2]) * t)), (0, y, w, 1))
    return s


def _pair_on_sky(panel_w, panel_h, sky_top, sky_bot, gap_h):
    """A top + bottom MARROW-SKEWER pair framing a gap, on a sky gradient — the
    barbed point of each half aims into the gap."""
    panel = _sky(panel_w, panel_h, sky_top, sky_bot)
    gap_top = (panel_h - gap_h) // 2
    gap_bot = gap_top + gap_h
    cx = panel_w // 2
    top = render_column(gap_top, 4, flip=True)        # point aims DOWN into gap
    bot = render_column(panel_h - gap_bot, 4, flip=False)  # point aims UP into gap
    panel.blit(top, (cx - (PW + 2 * OVERHANG) // 2, 0))
    panel.blit(bot, (cx - (PW + 2 * OVERHANG) // 2, gap_bot))
    # Honest collision-edge guide: the 58px column footprint.
    pygame.draw.rect(panel, (255, 255, 255, 60),
                     (cx - PW // 2, 0, PW, panel_h), 1)
    return panel


def main():
    pygame.font.init()
    title_f = pygame.font.SysFont("dejavusans", 22, bold=True)
    head_f = pygame.font.SysFont("dejavusans", 15, bold=True)
    body_f = pygame.font.SysFont("dejavusans", 12)

    BG = (32, 34, 44)
    SHEET_W, SHEET_H = 980, 740
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill(BG)
    sheet.blit(title_f.render("MARROW-SKEWER  —  clown-event bone column  —  round 1",
                              True, (255, 255, 255)), (20, 14))
    sheet.blit(body_f.render(
        "Vertebra discs + small skulls THREADED on a gold-cored marrow spike, "
        "with exaggerated AIR between beads.  Barbed bone-point caps the gap.",
        True, (206, 208, 218)), (20, 42))

    # Day + night hero pairs framing a gap.
    PANEL_W, PANEL_H = 250, 560
    GAP_H = 150
    day = _pair_on_sky(PANEL_W, PANEL_H, (150, 205, 235), (210, 235, 245), GAP_H)
    night = _pair_on_sky(PANEL_W, PANEL_H, (20, 26, 52), (40, 30, 64), GAP_H)
    sheet.blit(head_f.render("DAY", True, (255, 255, 255)), (24, 66))
    sheet.blit(head_f.render("NIGHT", True, (255, 255, 255)), (288, 66))
    sheet.blit(day, (20, 92))
    sheet.blit(night, (284, 92))

    # 1x in-game scale crop — verify it reads at true PIPE_W width.
    cx3 = 560
    sheet.blit(head_f.render("1x  IN-GAME SIZE (player view)", True, (255, 255, 255)),
               (cx3, 66))
    crop = _pair_on_sky(PANEL_W, PANEL_H, (150, 205, 235), (210, 235, 245), GAP_H)
    # Show it boxed at exactly the on-route footprint width.
    sheet.blit(crop, (cx3, 92))
    sheet.blit(body_f.render("(rendered at true 58px column width)",
                             True, (206, 208, 218)), (cx3, 656))

    # Detail callout: a single isolated tile of the bead cadence, magnified.
    cx4 = 820
    sheet.blit(head_f.render("BEAD CADENCE (3x detail)", True, (255, 255, 255)),
               (cx4, 66))
    tile_h = 240
    tile = render_column(tile_h, 6, flip=False)
    big = pygame.transform.scale(
        tile, ((PW + 2 * OVERHANG) * 2, tile_h * 2))
    tile_panel = _sky(big.get_width() + 8, big.get_height() + 8,
                      (60, 68, 86), (44, 50, 66))
    tile_panel.blit(big, (4, 4))
    sheet.blit(tile_panel, (cx4, 92))
    sheet.blit(body_f.render("disc / skull / disc + air",
                             True, (206, 208, 218)), (cx4, 92 + big.get_height() + 14))

    sheet.blit(body_f.render(
        "Collision edge = the central spike (honest spine). Air gaps are part of "
        "the silhouette; beads read solid bone at 58px.",
        True, (188, 190, 200)), (20, 712))

    out = "/home/user/skybit/docs/clown_bone_columns/marrow-skewer/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
