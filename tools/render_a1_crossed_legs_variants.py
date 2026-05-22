"""Render 5 crossed-legs variants of the refined A1 genie.

Keeps the v6 head + face + torso + sash + palms-up offering arms
(pose #2 from the previous round) and ONLY replaces the lower body
(draw_pants + draw_slippers) with five crossed-legs treatments:

  1 Full lotus           — wide knee splay, ankles tucked under
  2 Casual ankle-cross   — legs hang, ankles cross at the bottom
  3 Tight tuck           — knees close, ankles meet under sash
  4 Half-lotus + smoke   — one foot on knee, other fades into smoke
  5 Side-leaning recline — both legs angled to one side

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_a1_crossed_legs_variants [tag]
"""
import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from tools.render_a1_refined import (
    W, H, SS, PW, PH, SKY, P, s,
    aa_circle, ell, gem_facet,
    draw_torso, draw_neck, draw_head, draw_face,
    draw_earrings, draw_topknot_and_headband, draw_sash,
)
from tools.render_a1_arms_variants import draw_arms_2_offering

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie_designs")
os.makedirs(OUT_DIR, exist_ok=True)

DISPLAY_SCALE = 2


# ─────────────────────────────────────────────────────────────────────────────
# Shared low-level helpers for the leg drawings
# ─────────────────────────────────────────────────────────────────────────────

def _pant_polygon(big, pts, shadow_offset=(2, 2)):
    """Pant fabric — drop shadow + mid + base + flank highlight."""
    sx_off, sy_off = shadow_offset
    pygame.draw.polygon(big, P["PANT_DK"],
                        [(x + s(sx_off), y + s(sy_off)) for x, y in pts])
    pygame.draw.polygon(big, P["PANT_LO"], pts)
    inner = [(int(x * 0.97 + sum(p[0] for p in pts) / len(pts) * 0.03),
              int(y * 0.97 + sum(p[1] for p in pts) / len(pts) * 0.03))
             for x, y in pts]
    pygame.draw.polygon(big, P["PANT"], inner)


def _pant_pleats(big, pts):
    """Two faint pleat ripples down the centre of a pant polygon."""
    cx_p = sum(p[0] for p in pts) // len(pts)
    cy_p = sum(p[1] for p in pts) // len(pts)
    for off_x in (-s(4), s(4)):
        pygame.draw.line(big, P["PANT_LO"],
                         (cx_p + off_x, cy_p - s(12)),
                         (cx_p + off_x, cy_p + s(12)),
                         max(1, s(1)))


def _gold_ankle_cuff(big, cx_a, cy_a, angle_deg=0, w_native=18):
    """Gold cuff around an ankle. Rendered as a rotated rounded
    band so it works for legs at any angle."""
    cuff = pygame.Surface((s(w_native), s(10)), pygame.SRCALPHA)
    cw, ch = cuff.get_size()
    pygame.draw.rect(cuff, P["GOLD_LO"], (0, 0, cw, ch))
    pygame.draw.rect(cuff, P["GOLD"], (s(1), s(1), cw - s(2), ch - s(2)))
    pygame.draw.line(cuff, P["GOLD_HI"], (s(2), s(2)),
                     (cw - s(2), s(2)), max(1, s(1)))
    cuff_rot = pygame.transform.rotate(cuff, angle_deg)
    rect = cuff_rot.get_rect(center=(int(cx_a), int(cy_a)))
    big.blit(cuff_rot, rect.topleft)


def _slipper(big, cx_s, cy_s, angle_deg=0, mirror=False, scale=1.0):
    """Curled-toe slipper rotated by angle_deg around (cx_s, cy_s).
    `mirror=True` flips it left-right so the curl points the other
    way."""
    sw = int(s(40) * scale)
    sh = int(s(20) * scale)
    sl = pygame.Surface((sw, sh), pygame.SRCALPHA)
    base_pts = [
        (s(2), s(13)),
        (sw - s(14), s(13)),
        (sw - s(2), s(9)),
        (sw - s(6), s(3)),
        (sw - s(14), s(7)),
        (s(2), s(7)),
    ]
    if mirror:
        base_pts = [(sw - x, y) for x, y in base_pts]
    pygame.draw.polygon(sl, P["GOLD_DK"],
                        [(x + s(1), y + s(1)) for x, y in base_pts])
    pygame.draw.polygon(sl, P["GOLD"], base_pts)
    # Highlight stripe
    pygame.draw.line(sl, P["GOLD_HI"],
                     (s(6) if not mirror else sw - s(6), s(8)),
                     (s(14) if not mirror else sw - s(14), s(8)),
                     max(2, s(1)))
    # Ruby gem on the curled toe
    gem_x = sw - s(6) if not mirror else s(6)
    gem_y = s(6)
    pygame.draw.polygon(sl, P["RUBY"],
                        [(gem_x, gem_y - s(2)),
                         (gem_x + s(2), gem_y),
                         (gem_x, gem_y + s(2)),
                         (gem_x - s(2), gem_y)])
    pygame.draw.circle(sl, (255, 200, 220),
                       (gem_x - s(1), gem_y - s(1)), max(1, s(1)))
    sl_rot = pygame.transform.rotate(sl, angle_deg)
    rect = sl_rot.get_rect(center=(int(cx_s), int(cy_s)))
    big.blit(sl_rot, rect.topleft)


def _smoke_aura_below(big, cx, top_y):
    """Atmospheric smoke cloud filling the space below the crossed
    legs — replaces v6's draw_smoke_aura behind the standing figure."""
    for i, (dx, dy, w, h, alpha) in enumerate((
            (-100, 380, 140, 70, 70),
            ( 100, 380, 140, 70, 70),
            (   0, 410, 230, 60, 60),
            (-140, 340, 90, 50, 55),
            ( 140, 340, 90, 50, 55),
            (-60, 365, 80, 40, 50),
            ( 60, 365, 80, 40, 50))):
        srf = pygame.Surface((s(w + 4), s(h + 4)), pygame.SRCALPHA)
        pygame.draw.ellipse(srf, (*P["SKIN_HI"], alpha),
                            (s(2), s(2), s(w), s(h)))
        big.blit(srf, (s(W // 2 + dx - w / 2), s(dy - h / 2)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 1 — Full lotus
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_full_lotus(big, cx):
    """Both legs crossed at the shins, knees pushed out wide,
    ankles tucked under the opposite thigh. Slippers visible at the
    outer flanks."""
    hip_y = s(248)
    # Two thigh polygons sweeping outward to wide knees, then inward
    # to ankles tucked under the opposite thigh.
    for side in (-1, +1):
        hip_x = cx + side * s(28)
        knee_x = cx + side * s(72)
        knee_y = s(290)
        # Inner ankle tucked toward the centre
        ank_x = cx + side * s(-20)
        ank_y = s(320)
        thigh = [
            (hip_x - side * s(4), hip_y),
            (hip_x + side * s(20), hip_y),
            (knee_x, knee_y - s(6)),
            (knee_x - side * s(4), knee_y + s(6)),
            (cx + side * s(4), s(326)),
            (ank_x, ank_y),
        ]
        _pant_polygon(big, thigh)
        _pant_pleats(big, thigh)
    # Outer-edge slippers at each knee position
    for side in (-1, +1):
        sl_x = cx + side * s(78)
        sl_y = s(308)
        _slipper(big, sl_x, sl_y, angle_deg=10 * side,
                 mirror=(side > 0))
        # Ankle cuff between thigh and slipper
        _gold_ankle_cuff(big, cx + side * s(62), s(306),
                         angle_deg=20 * side, w_native=22)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 2 — Casual ankle-cross
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_ankle_cross(big, cx):
    """Legs hang naturally down from the sash but cross at the
    ankles — slippers point outward in opposite directions."""
    hip_y = s(248)
    cross_y = s(370)
    # Two pant legs descending and crossing near the bottom
    for side in (-1, +1):
        hip_in = cx + side * s(8)
        hip_out = cx + side * s(36)
        ank_in = cx + -side * s(14)        # crosses to opposite side
        ank_out = cx + -side * s(2)
        leg = [
            (hip_in, hip_y),
            (hip_out, hip_y),
            (ank_out, cross_y),
            (ank_in, cross_y),
        ]
        _pant_polygon(big, leg)
        _pant_pleats(big, leg)
    # Cross shadow at the ankle crossover
    sh = pygame.Surface((s(60), s(20)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (*P["PANT_DK"], 150),
                        (0, 0, s(60), s(20)))
    big.blit(sh, (cx - s(30), s(362)))
    # Slippers angled outward at the ankle-cross
    _slipper(big, cx - s(18), s(382), angle_deg=20,
             mirror=True)
    _slipper(big, cx + s(18), s(382), angle_deg=-20)
    # Gold ankle cuffs above each slipper
    _gold_ankle_cuff(big, cx - s(10), s(370), angle_deg=-12,
                     w_native=20)
    _gold_ankle_cuff(big, cx + s(10), s(370), angle_deg=12,
                     w_native=20)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 3 — Tight tuck
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_tight_tuck(big, cx):
    """Legs crossed and pulled up toward the body — knees come
    closer together, ankles meet just below the sash."""
    hip_y = s(248)
    knee_y = s(280)
    ankle_y = s(310)
    for side in (-1, +1):
        hip_in = cx + side * s(8)
        hip_out = cx + side * s(34)
        knee_x = cx + side * s(46)
        # Ankles tuck WAY in (cross past centre)
        ank_x = cx + -side * s(10)
        leg = [
            (hip_in, hip_y),
            (hip_out, hip_y),
            (knee_x, knee_y),
            (cx + side * s(20), s(298)),
            (ank_x, ankle_y),
            (cx + -side * s(2), ankle_y),
        ]
        _pant_polygon(big, leg)
        _pant_pleats(big, leg)
    # Compact slippers tucked under the body
    _slipper(big, cx - s(28), s(320), angle_deg=15,
             mirror=True, scale=0.9)
    _slipper(big, cx + s(28), s(320), angle_deg=-15, scale=0.9)
    _gold_ankle_cuff(big, cx - s(16), s(308), angle_deg=8,
                     w_native=18)
    _gold_ankle_cuff(big, cx + s(16), s(308), angle_deg=-8,
                     w_native=18)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 4 — Half-lotus + smoke
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_half_lotus_smoke(big, cx):
    """One foot rests on the opposite knee (visible), the other
    lower leg tucks under and FADES into the smoke trail."""
    hip_y = s(248)
    # LEFT thigh — clearly visible, knee out wide
    knee_x = cx - s(54)
    knee_y = s(298)
    thigh_L = [
        (cx - s(28), hip_y),
        (cx + s(4), hip_y),
        (cx, s(280)),
        (knee_x + s(10), knee_y),
        (knee_x, knee_y + s(8)),
        (cx - s(34), s(308)),
    ]
    _pant_polygon(big, thigh_L)
    _pant_pleats(big, thigh_L)
    # RIGHT foot resting ON TOP of LEFT knee
    foot_x = cx + s(12)
    foot_y = s(294)
    _slipper(big, foot_x, foot_y, angle_deg=-8, scale=0.95)
    _gold_ankle_cuff(big, foot_x - s(14), s(292), angle_deg=-5,
                     w_native=22)
    # RIGHT thigh fading into smoke (alpha gradient by drawing 3
    # progressively less-opaque polygons)
    for alpha, off in ((220, 0), (160, s(4)), (100, s(8))):
        pts = [
            (cx + s(4), hip_y),
            (cx + s(28), hip_y),
            (cx + s(52), s(298) + off),
            (cx + s(20), s(330) + off),
            (cx - s(14), s(316) + off),
        ]
        srf = pygame.Surface((PW, PH), pygame.SRCALPHA)
        pygame.draw.polygon(srf, (*P["PANT"], alpha), pts)
        big.blit(srf, (0, 0))
    # LEFT outer slipper at the knee position
    _slipper(big, cx - s(62), s(308), angle_deg=12, mirror=True)
    _gold_ankle_cuff(big, cx - s(46), s(306), angle_deg=18,
                     w_native=22)
    # Extra smoke wisp where the fading leg dissolves
    for r, alpha in ((s(28), 110), (s(22), 90), (s(16), 70)):
        srf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(srf, (*P["SKIN_HI"], alpha),
                           (r + 2, r + 2), r)
        big.blit(srf, (cx + s(22) - r, s(346) - r))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 5 — Side-leaning recline
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_side_recline(big, cx):
    """Both legs crossed and angled to the LEFT side. One slipper
    forward, one tucked behind. Like sitting on a couch armrest."""
    hip_y = s(248)
    # Both pant legs slope down-left
    # Front leg (the visible top one)
    front_leg = [
        (cx - s(8), hip_y),
        (cx + s(28), hip_y),
        (cx + s(10), s(296)),
        (cx - s(46), s(324)),
        (cx - s(60), s(310)),
        (cx - s(20), s(282)),
    ]
    _pant_polygon(big, front_leg)
    _pant_pleats(big, front_leg)
    # Back leg (partially hidden behind front leg)
    back_leg = [
        (cx - s(28), hip_y),
        (cx - s(8), hip_y),
        (cx - s(34), s(282)),
        (cx - s(70), s(308)),
        (cx - s(82), s(298)),
        (cx - s(44), s(260)),
    ]
    # Draw the back leg first so the front overlaps it
    pygame.draw.polygon(big, P["PANT_DK"],
                        [(x + s(2), y + s(2)) for x, y in back_leg])
    pygame.draw.polygon(big, P["PANT_LO"], back_leg)
    inner_back = [(int(x * 0.97 + cx * 0.03),
                   int(y * 0.97 + (hip_y + s(40)) * 0.03))
                  for x, y in back_leg]
    pygame.draw.polygon(big, P["PANT"], inner_back)
    # Redraw front leg ON TOP so it overlaps the back one
    _pant_polygon(big, front_leg)
    _pant_pleats(big, front_leg)
    # Front slipper pointing forward-left
    _slipper(big, cx - s(58), s(322), angle_deg=18, mirror=True)
    _gold_ankle_cuff(big, cx - s(40), s(316), angle_deg=24,
                     w_native=22)
    # Back slipper tucked behind, smaller + angled the other way
    _slipper(big, cx - s(78), s(304), angle_deg=8, mirror=True,
             scale=0.85)
    _gold_ankle_cuff(big, cx - s(62), s(298), angle_deg=14,
                     w_native=18)


# ─────────────────────────────────────────────────────────────────────────────
# Composer
# ─────────────────────────────────────────────────────────────────────────────

def render_figure(legs_fn):
    big = pygame.Surface((PW, PH), pygame.SRCALPHA)
    big.fill(SKY)
    cx = PW // 2
    # Smoke fills the bottom space where legs no longer extend.
    _smoke_aura_below(big, cx, s(330))
    # Legs / pants / slippers first
    legs_fn(big, cx)
    # Torso + sash + head stack
    draw_torso(big, cx)
    draw_neck(big, cx)
    head_cy = s(60)
    head_r = s(40)
    draw_head(big, cx, head_cy, head_r)
    draw_face(big, cx, head_cy)
    draw_earrings(big, cx, head_cy, head_r)
    draw_topknot_and_headband(big, cx, head_cy, head_r)
    draw_sash(big, cx)
    # Palms-up offering arms last so palms read clearly
    draw_arms_2_offering(big, cx)
    return pygame.transform.smoothscale(big, (W, H))


VARIANTS = [
    ("1 — Full lotus",            draw_crossed_legs_full_lotus),
    ("2 — Casual ankle-cross",    draw_crossed_legs_ankle_cross),
    ("3 — Tight tuck",            draw_crossed_legs_tight_tuck),
    ("4 — Half-lotus + smoke",    draw_crossed_legs_half_lotus_smoke),
    ("5 — Side-leaning recline",  draw_crossed_legs_side_recline),
]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "v1"
    DW = W * DISPLAY_SCALE
    DH = H * DISPLAY_SCALE
    margin = 14
    label_h = 28
    sheet_w = DW * len(VARIANTS) + margin * (len(VARIANTS) + 1)
    sheet_h = DH + margin * 2 + label_h
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 22, 30))
    font = pygame.font.SysFont("Arial", 18, bold=True)
    for i, (label, fn) in enumerate(VARIANTS):
        portrait = render_figure(fn)
        disp = pygame.transform.smoothscale(portrait, (DW, DH))
        x = margin + i * (DW + margin)
        pygame.draw.rect(sheet, (60, 65, 80),
                         (x - 2, margin - 2, DW + 4, DH + 4), 2)
        sheet.blit(disp, (x, margin))
        text = font.render(label, True, (240, 240, 240))
        sheet.blit(text, (x + (DW - text.get_width()) // 2,
                          margin + DH + 6))
        pygame.image.save(disp,
                          os.path.join(OUT_DIR,
                                       f"a1_crossed_legs_{i+1}_{tag}.png"))
    out = os.path.join(OUT_DIR, f"a1_crossed_legs_{tag}.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
