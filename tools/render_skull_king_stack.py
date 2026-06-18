"""Design-only render: a pillar built by STACKING the various small skulls from
the chosen king-skull design (Asthi-Dakini SWITCHED+BIG) one on top of another,
pagoda-style — plus a second version with a skewer threaded down through them.

Reuses the chosen design's own skull functions (crown_skull / palm_skull /
palm_cabochon) + palette + house helpers, imported directly from its render
script. Not wired into the game; produces review sheets under docs/.
"""
import os, sys, math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASTHI = os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye")
sys.path.insert(0, ASTHI)

import pygame
pygame.init()
import render_switchbig as sk   # the chosen design — defines the skull functions + palette

OUT = os.path.join(ROOT, "docs/skull_king_stack")
os.makedirs(OUT, exist_ok=True)

SS = 8                     # supersample, matching the source ELEVATED pipeline
PIPE_W = 58                # the game's pillar width
R = 23                     # skull radius (final px) — ~2.3*R spans the column
S_UNIT = R / 12.0          # the source's r≈12*s convention → correct line weights
PITCH = 34                 # vertical centre-to-centre (skulls overlap → dense totem)

# The 12 various small skulls of the design, interleaved crown / palm so each
# column shows the bare relic skulls AND the jewelled cradled ones (gem colour).
SKULLS = []
for i in range(6):
    SKULLS.append(("crown", i))
    SKULLS.append(("palm", i))


def _draw_skull(big, kind, idx, cx, cy, *, lit=False):
    r = int(R * SS)
    s = S_UNIT * SS
    if kind == "crown":
        sk.crown_skull(big, int(cx), int(cy), r, s, lit=lit, idx=idx)
    else:
        sk.palm_skull(big, int(cx), int(cy), r, s, idx=idx)


_SK_HW = int(4.5 * SS)                       # skewer shaft half-width (inside 58px)


def _rod_seg(big, cx, ya, yb):
    """A short ink-keyed bone rod segment with a gold marrow seam, ya→yb."""
    s = S_UNIT * SS
    hw = _SK_HW
    y, h = int(min(ya, yb)), int(abs(yb - ya))
    pygame.draw.rect(big, sk.INK, (cx - hw - int(1.4 * s), y, 2 * (hw + int(1.4 * s)), h))
    pygame.draw.rect(big, sk.BONE, (cx - hw, y, 2 * hw, h))
    pygame.draw.rect(big, sk.BONE_SH, (cx - hw, y, max(1, int(1.6 * s)), h))
    pygame.draw.rect(big, sk.GOLD_D, (cx - int(1.6 * s), y, int(3.2 * s), h))
    pygame.draw.rect(big, sk.GOLD, (cx - int(0.9 * s), y, int(1.8 * s), h))


def _skewer_bg(big, cx, y_gap, y_far):
    """The full shaft drawn BEHIND the skulls (so it shows in any sky between
    tiers), plus a small bound tail nub at the far end."""
    _rod_seg(big, int(cx), y_gap, y_far)


def _skewer_thread(big, cx, centres, point_y, point_dir):
    """Drawn ON TOP of the skulls: a visible rod nub piercing each inter-skull
    seam (so the skewer reads as threaded through), and a barbed point juts into
    the gap at the near end."""
    s = S_UNIT * SS
    hw = _SK_HW
    cx = int(cx)
    # rod nub at every seam between adjacent skulls + just outside the far skull
    seams = [(centres[i] + centres[i + 1]) / 2.0 for i in range(len(centres) - 1)]
    if centres:
        seams.append(centres[-1] - point_dir * (R * 0.95))   # tail past the far skull
    for ym in seams:
        _rod_seg(big, cx, (ym - 7) * SS, (ym + 7) * SS)
    # barbed point at the gap end (on top of the focal skull's brow)
    tip = (point_y + point_dir * 26) * SS
    base = (point_y + point_dir * 2) * SS
    barb = int(11 * SS)
    pts = [(cx, tip), (cx - hw - barb, base + point_dir * int(9 * SS)),
           (cx - hw, base), (cx + hw, base),
           (cx + hw + barb, base + point_dir * int(9 * SS))]
    sk.triad_blob(big, sk.BONE, [(int(x), int(y)) for x, y in pts], ow=max(1, int(1.4 * s)))
    pygame.draw.line(big, sk.GOLD, (cx, base), (cx, tip), max(1, int(1.8 * s)))
    pygame.draw.circle(big, sk.GOLD_BR, (cx, int(tip)), max(1, int(2.2 * s)))


def render_half(H, *, cap, with_skewer):
    """One pillar half, skulls upright, the lit focal skull at the gap edge.
    cap='bottom' → TOP pillar (gap below); cap='top' → BOTTOM pillar (gap above)."""
    big = pygame.Surface((PIPE_W * SS, H * SS), pygame.SRCALPHA)
    cx = PIPE_W * SS // 2

    margin = int(R * 1.05)
    if cap == "bottom":
        focal_y = H - margin
        step = -PITCH
        point_dir = +1                       # point juts downward into the gap
        gap_edge_y = H * SS
    else:
        focal_y = margin
        step = +PITCH
        point_dir = -1                       # point juts upward into the gap
        gap_edge_y = 0

    # tier centres from the gap edge outward until off the far end
    centres = []
    y = focal_y
    while -R * 0.6 <= y <= H + R * 0.6:
        centres.append(y)
        y += step

    if with_skewer:
        _skewer_bg(big, cx, gap_edge_y, centres[-1] * SS)

    # draw far → near so nearer (lower-index) skulls overlap on top toward the gap
    for i, cy in reversed(list(enumerate(centres))):
        # thin gold bead collar seating each skull on the one below (design's tell)
        sk.bead_strand(big, [(cx - int(R * 0.8 * SS), int((cy + R * 0.72) * SS)),
                             (cx + int(R * 0.8 * SS), int((cy + R * 0.72) * SS))],
                       int(2.6 * S_UNIT * SS), S_UNIT * SS, gold_every=2)
        if i == 0:
            _draw_skull(big, "crown", 2, cx, cy * SS, lit=True)   # lit focal (centre relic)
        else:
            kind, idx = SKULLS[i % len(SKULLS)]
            _draw_skull(big, kind, idx, cx, cy * SS)

    if with_skewer:
        _skewer_thread(big, cx, centres, focal_y, point_dir)

    small = pygame.transform.smoothscale(big, (PIPE_W, H))
    return sk.grow_outline(small, sk.INK + (255,), 1)


# ── compositing the review sheets ─────────────────────────────────────────────
def _sky(w, h, night=False):
    top = sk.NIGHT_T if night else sk.DAY_SKY_T
    bot = sk.lerp(top, (255, 255, 255), 0.0 if night else 0.45)
    if night:
        bot = sk.lerp(top, (60, 70, 110), 0.7)
    surf = pygame.Surface((w, h))
    for yy in range(h):
        surf.fill(sk.lerp(top, bot, yy / max(1, h - 1)), (0, yy, w, 1))
    return surf


def _pair_panel(with_skewer, night, half_h=190, gap=150):
    H = half_h * 2 + gap
    panel = _sky(PIPE_W + 24, H, night=night)
    top = render_half(half_h, cap="bottom", with_skewer=with_skewer)
    bot = render_half(half_h, cap="top", with_skewer=with_skewer)
    x = 12
    panel.blit(top, (x, 0))
    panel.blit(bot, (x, half_h + gap))
    return panel


def _label(surf, text, x, y, night=False):
    f = sk.font(15) if hasattr(sk, "font") else pygame.font.SysFont("sans", 15)
    col = (235, 230, 222) if not night else (220, 224, 240)
    surf.blit(f.render(text, True, (20, 16, 22)), (x + 1, y + 1))
    surf.blit(f.render(text, True, col), (x, y))


def build_variant_sheet(with_skewer, title, fname):
    day = _pair_panel(with_skewer, night=False)
    night = _pair_panel(with_skewer, night=True)
    # a true-58px in-game crop (just the gap region) on day sky
    crop_h = 150
    crop = _sky(PIPE_W + 24, crop_h, night=False)
    top = render_half(crop_h // 2, cap="bottom", with_skewer=with_skewer)
    bot = render_half(crop_h // 2, cap="top", with_skewer=with_skewer)
    crop.blit(top, (12, -crop_h // 2 + 70))
    crop.blit(bot, (12, crop_h - 70))

    pad, head = 24, 56
    W = day.get_width() + night.get_width() + crop.get_width() + pad * 4
    Ht = head + max(day.get_height(), night.get_height(), crop_h) + pad * 2
    sheet = pygame.Surface((W, Ht))
    sheet.fill((26, 24, 30))
    _label(sheet, title, pad, 16)
    x = pad
    y = head
    for cap, surf, n in (("DAY", day, False), ("NIGHT", night, True), ("1x crop", crop, False)):
        sheet.blit(surf, (x, y))
        _label(sheet, cap, x, y + surf.get_height() + 4, night=False)
        x += surf.get_width() + pad
    out = os.path.join(OUT, fname)
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())
    return sheet


def build_showcase(stack_sheet, skewer_sheet):
    pad = 0
    W = max(stack_sheet.get_width(), skewer_sheet.get_width())
    Ht = stack_sheet.get_height() + skewer_sheet.get_height()
    sheet = pygame.Surface((W, Ht))
    sheet.fill((26, 24, 30))
    sheet.blit(stack_sheet, (0, 0))
    sheet.blit(skewer_sheet, (0, stack_sheet.get_height()))
    out = os.path.join(OUT, "showcase.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    a = build_variant_sheet(False, "SKULL-KING STACK  —  the design's various small skulls, stacked pagoda-style", "stack.png")
    b = build_variant_sheet(True, "SKULL-KING SKEWER  —  same stack, skewered down the centre", "skewer.png")
    build_showcase(a, b)
