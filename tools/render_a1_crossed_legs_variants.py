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
# All five variants are PROPER seated cross-legged poses, modelled on
# how a person actually sits on the ground:
#   * hips at "seat" level (y ≈ 248)
#   * thighs angle OUT AND DOWN from the hips to knees at the outer flanks
#   * shins angle INWARD from the knees back across the body
#   * feet/slippers sit either tucked under the opposite thigh, on top
#     of it, or in front depending on the pose
# Total leg-section height is intentionally compact (~70 px) — that's
# the "save room in gameplay" win from cross-legged sitting.
# ─────────────────────────────────────────────────────────────────────────────

def _draw_thigh(big, hip_in, hip_out, knee_inner, knee_outer):
    """Thigh polygon from a hip seat-edge to a knee, with the OUT side
    forming the leg's outer silhouette."""
    pts = [hip_in, hip_out, knee_outer, knee_inner]
    _pant_polygon(big, pts)
    _pant_pleats(big, pts)


def _draw_shin(big, knee_top, knee_bot, foot_top, foot_bot):
    """Shin polygon — same fabric treatment as the thigh."""
    pts = [knee_top, knee_bot, foot_bot, foot_top]
    _pant_polygon(big, pts)
    _pant_pleats(big, pts)


def _cross_shadow(big, cx, y, w=80, h=20, alpha=130):
    """Soft shadow under the top shin so the cross-over reads."""
    sh = pygame.Surface((s(w), s(h)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (*P["PANT_DK"], alpha), (0, 0, s(w), s(h)))
    big.blit(sh, (cx - s(w // 2), y - s(h // 2)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 1 — Classic sukhasana (easy pose)
# Shins cross loosely in front of the body, feet tucked under the
# opposite thigh, peeking out the sides.
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_full_lotus(big, cx):  # name kept for stable API
    hip_y    = s(248)
    knee_y   = s(282)
    foot_y   = s(304)
    # ── THIGHS (drawn first so shins overlap them) ──────────────────
    _draw_thigh(big,
                hip_in=(cx - s(12), hip_y),
                hip_out=(cx - s(28), hip_y),
                knee_inner=(cx - s(58), knee_y),
                knee_outer=(cx - s(78), knee_y - s(2)))
    _draw_thigh(big,
                hip_in=(cx + s(12), hip_y),
                hip_out=(cx + s(28), hip_y),
                knee_inner=(cx + s(58), knee_y),
                knee_outer=(cx + s(78), knee_y - s(2)))
    # ── RIGHT shin (drawn first — goes UNDER the left shin) ────────
    _draw_shin(big,
               knee_top=(cx + s(70), knee_y - s(2)),
               knee_bot=(cx + s(58), knee_y + s(8)),
               foot_bot=(cx - s(8),  foot_y + s(2)),
               foot_top=(cx - s(20), foot_y - s(8)))
    # Right foot peeking out on the LEFT side
    _slipper(big, cx - s(30), foot_y - s(2), angle_deg=10,
             mirror=True, scale=0.85)
    _gold_ankle_cuff(big, cx - s(18), foot_y - s(4),
                     angle_deg=12, w_native=18)
    # Cross shadow under where LEFT shin will lie
    _cross_shadow(big, cx, knee_y + s(14), w=100, h=20, alpha=140)
    # ── LEFT shin (drawn ON TOP — crosses over the right shin) ─────
    _draw_shin(big,
               knee_top=(cx - s(70), knee_y - s(2)),
               knee_bot=(cx - s(58), knee_y + s(8)),
               foot_bot=(cx + s(8),  foot_y + s(2)),
               foot_top=(cx + s(20), foot_y - s(8)))
    # Left foot peeking out on the RIGHT side
    _slipper(big, cx + s(30), foot_y - s(2), angle_deg=-10,
             scale=0.85)
    _gold_ankle_cuff(big, cx + s(18), foot_y - s(4),
                     angle_deg=-12, w_native=18)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 2 — Full lotus (padmasana)
# Both feet rest ON TOP of the opposite thigh — most ornate yogic
# pose, both slippers prominently visible.
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_ankle_cross(big, cx):
    hip_y    = s(248)
    knee_y   = s(284)
    foot_y   = s(272)   # feet sit ABOVE the knees (on top of thighs)
    # ── THIGHS (wide splay) ─────────────────────────────────────────
    _draw_thigh(big,
                hip_in=(cx - s(12), hip_y),
                hip_out=(cx - s(28), hip_y),
                knee_inner=(cx - s(62), knee_y),
                knee_outer=(cx - s(82), knee_y - s(2)))
    _draw_thigh(big,
                hip_in=(cx + s(12), hip_y),
                hip_out=(cx + s(28), hip_y),
                knee_inner=(cx + s(62), knee_y),
                knee_outer=(cx + s(82), knee_y - s(2)))
    # ── RIGHT shin (loops up over LEFT thigh) ──────────────────────
    _draw_shin(big,
               knee_top=(cx + s(74), knee_y - s(2)),
               knee_bot=(cx + s(62), knee_y + s(6)),
               foot_bot=(cx - s(8),  foot_y + s(6)),
               foot_top=(cx - s(22), foot_y - s(4)))
    # RIGHT foot ON TOP of left thigh
    _slipper(big, cx - s(28), foot_y, angle_deg=8,
             mirror=True, scale=0.9)
    _gold_ankle_cuff(big, cx - s(14), foot_y + s(2),
                     angle_deg=12, w_native=20)
    # ── LEFT shin (loops up over RIGHT thigh) ──────────────────────
    _draw_shin(big,
               knee_top=(cx - s(74), knee_y - s(2)),
               knee_bot=(cx - s(62), knee_y + s(6)),
               foot_bot=(cx + s(8),  foot_y + s(6)),
               foot_top=(cx + s(22), foot_y - s(4)))
    # LEFT foot ON TOP of right thigh
    _slipper(big, cx + s(28), foot_y, angle_deg=-8, scale=0.9)
    _gold_ankle_cuff(big, cx + s(14), foot_y + s(2),
                     angle_deg=-12, w_native=20)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 3 — Half lotus (ardha padmasana)
# Right foot ON TOP of left thigh (visible). Left foot tucked under
# right thigh (peeks out on the left). Asymmetric — the most
# realistic relaxed sitting cross-legged pose.
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_tight_tuck(big, cx):
    hip_y    = s(248)
    knee_y   = s(284)
    # ── THIGHS ──────────────────────────────────────────────────────
    _draw_thigh(big,
                hip_in=(cx - s(12), hip_y),
                hip_out=(cx - s(28), hip_y),
                knee_inner=(cx - s(58), knee_y),
                knee_outer=(cx - s(78), knee_y - s(2)))
    _draw_thigh(big,
                hip_in=(cx + s(12), hip_y),
                hip_out=(cx + s(28), hip_y),
                knee_inner=(cx + s(58), knee_y),
                knee_outer=(cx + s(78), knee_y - s(2)))
    # ── LEFT shin (under, tucked) ──────────────────────────────────
    _draw_shin(big,
               knee_top=(cx - s(70), knee_y - s(2)),
               knee_bot=(cx - s(58), knee_y + s(8)),
               foot_bot=(cx + s(6),  s(312)),
               foot_top=(cx - s(10), s(302)))
    # Left foot peeks under right thigh
    _slipper(big, cx + s(20), s(310), angle_deg=-10, scale=0.75)
    _gold_ankle_cuff(big, cx + s(8), s(306),
                     angle_deg=-8, w_native=16)
    # ── RIGHT shin (drawn last — ON TOP, foot UP on left thigh) ───
    _draw_shin(big,
               knee_top=(cx + s(74), knee_y - s(2)),
               knee_bot=(cx + s(62), knee_y + s(6)),
               foot_bot=(cx - s(10), s(282)),
               foot_top=(cx - s(24), s(270)))
    # Right foot prominently ON TOP of left thigh
    _slipper(big, cx - s(34), s(276), angle_deg=14,
             mirror=True, scale=0.95)
    _gold_ankle_cuff(big, cx - s(18), s(278),
                     angle_deg=16, w_native=22)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 4 — Burmese style (uncrossed sitting)
# Both shins drop down nearly parallel — feet rest flat in front of
# the body, side by side. Less crossed at the shins, more "polite
# seated" pose. Familiar from kids sitting "criss-cross applesauce"
# without actually crossing.
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_half_lotus_smoke(big, cx):
    hip_y    = s(248)
    knee_y   = s(280)
    foot_y   = s(316)
    # ── THIGHS sweep out to knees ──────────────────────────────────
    _draw_thigh(big,
                hip_in=(cx - s(12), hip_y),
                hip_out=(cx - s(28), hip_y),
                knee_inner=(cx - s(48), knee_y),
                knee_outer=(cx - s(70), knee_y - s(2)))
    _draw_thigh(big,
                hip_in=(cx + s(12), hip_y),
                hip_out=(cx + s(28), hip_y),
                knee_inner=(cx + s(48), knee_y),
                knee_outer=(cx + s(70), knee_y - s(2)))
    # ── SHINS drop nearly straight down from knees to feet ────────
    _draw_shin(big,
               knee_top=(cx - s(60), knee_y - s(2)),
               knee_bot=(cx - s(46), knee_y + s(8)),
               foot_bot=(cx - s(8),  foot_y + s(4)),
               foot_top=(cx - s(22), foot_y - s(6)))
    _draw_shin(big,
               knee_top=(cx + s(60), knee_y - s(2)),
               knee_bot=(cx + s(46), knee_y + s(8)),
               foot_bot=(cx + s(8),  foot_y + s(4)),
               foot_top=(cx + s(22), foot_y - s(6)))
    # Feet flat in front, side by side (slightly toes out)
    _slipper(big, cx - s(20), foot_y, angle_deg=15,
             mirror=True, scale=0.95)
    _slipper(big, cx + s(20), foot_y, angle_deg=-15, scale=0.95)
    _gold_ankle_cuff(big, cx - s(15), foot_y - s(8),
                     angle_deg=10, w_native=20)
    _gold_ankle_cuff(big, cx + s(15), foot_y - s(8),
                     angle_deg=-10, w_native=20)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 5 — Aladdin-style floating cross-legged
# Knees splayed even wider, ankles meet at the centre, curl-toe
# slippers point UPWARD like the classic Disney genie. Most stylized.
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_side_recline(big, cx):
    hip_y    = s(248)
    knee_y   = s(280)
    cross_y  = s(312)
    # ── THIGHS — very wide knee splay ──────────────────────────────
    _draw_thigh(big,
                hip_in=(cx - s(10), hip_y),
                hip_out=(cx - s(28), hip_y),
                knee_inner=(cx - s(66), knee_y),
                knee_outer=(cx - s(90), knee_y - s(2)))
    _draw_thigh(big,
                hip_in=(cx + s(10), hip_y),
                hip_out=(cx + s(28), hip_y),
                knee_inner=(cx + s(66), knee_y),
                knee_outer=(cx + s(90), knee_y - s(2)))
    # ── RIGHT shin — long sweep inward, curls UP at the foot ──────
    _draw_shin(big,
               knee_top=(cx + s(82), knee_y - s(2)),
               knee_bot=(cx + s(66), knee_y + s(8)),
               foot_bot=(cx + s(4),  cross_y + s(4)),
               foot_top=(cx - s(10), cross_y - s(6)))
    # Right slipper curling UP at the centre
    _slipper(big, cx - s(8), s(304), angle_deg=55,
             mirror=True, scale=0.95)
    _gold_ankle_cuff(big, cx + s(4), cross_y - s(2),
                     angle_deg=30, w_native=20)
    # Cross shadow at the ankle meet
    _cross_shadow(big, cx, cross_y + s(2), w=60, h=18, alpha=160)
    # ── LEFT shin — overlaps the right, foot curls UP too ─────────
    _draw_shin(big,
               knee_top=(cx - s(82), knee_y - s(2)),
               knee_bot=(cx - s(66), knee_y + s(8)),
               foot_bot=(cx - s(4),  cross_y + s(4)),
               foot_top=(cx + s(10), cross_y - s(6)))
    _slipper(big, cx + s(8), s(304), angle_deg=-55, scale=0.95)
    _gold_ankle_cuff(big, cx - s(4), cross_y - s(2),
                     angle_deg=-30, w_native=20)


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
    ("1 — Sukhasana (easy)",       draw_crossed_legs_full_lotus),
    ("2 — Full lotus",             draw_crossed_legs_ankle_cross),
    ("3 — Half lotus",             draw_crossed_legs_tight_tuck),
    ("4 — Burmese (uncrossed)",    draw_crossed_legs_half_lotus_smoke),
    ("5 — Aladdin floating",       draw_crossed_legs_side_recline),
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
