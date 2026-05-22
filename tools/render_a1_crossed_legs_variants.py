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
# v3 — all five variants are FULL LOTUS with progressively fuller /
# bagger / more decorated pants. User feedback: the v2 legs were too
# thin compared to the standing pose. v3 widens the polygons + adds
# fabric drapery + pleats so the lotus reads as a real harem-pants
# silhouette instead of skinny triangles.
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


def _baggy_thigh(big, cx, side, hip_w=20, top_y=248,
                 widest_y=280, widest_w=58,
                 knee_y=300, knee_w=42):
    """Curved/billowing thigh polygon: narrow at the hip, bulges out
    near `widest_y`, then comes back in toward the knee. Multiple
    polygon points make it look like fabric instead of a triangle."""
    pts = [
        (cx + side * s(8),               top_y),                 # inner hip
        (cx + side * s(hip_w),           top_y),                 # outer hip
        (cx + side * s(hip_w + 14),      top_y + s(14)),         # shoulder of bulge
        (cx + side * s(widest_w),        widest_y),              # widest point (knee outer)
        (cx + side * s(widest_w - 6),    widest_y + s(14)),
        (cx + side * s(knee_w + 4),      knee_y),                # knee bottom outer
        (cx + side * s(knee_w - 16),     knee_y + s(4)),         # knee inner
        (cx + side * s(2),               widest_y - s(2)),       # back up inner
    ]
    _pant_polygon(big, pts)
    # Pleat ripples down the thigh — soft inner shadow lines
    for off_x, off_y_top, off_y_bot in (
            (side * s(-4),  s(14), s(40)),
            (side * s(-12), s(10), s(38)),
            (side * s(-22), s(6),  s(34))):
        pygame.draw.line(big, P["PANT_LO"],
                         (cx + side * s(20) + off_x, top_y + off_y_top),
                         (cx + side * s(34) + off_x, top_y + off_y_bot),
                         max(2, s(1)))
    # Outer-flank gloss highlight
    pygame.draw.line(big, P["PANT_HI"],
                     (cx + side * s(hip_w + 8), top_y + s(10)),
                     (cx + side * s(widest_w - 2), widest_y),
                     s(3))
    pygame.draw.line(big, P["PANT_HI"],
                     (cx + side * s(widest_w - 2), widest_y),
                     (cx + side * s(knee_w), knee_y - s(2)),
                     s(2))


def _full_shin(big, cx, side, knee_x, knee_y, foot_x, foot_y,
               knee_width=44, mid_width=40, ankle_width=22):
    """BAGGY shin polygon — bulges out near the knee + mid-shin so the
    lower leg reads as harem-pant fabric rather than a stick, then
    tapers to a cinched ankle. Six anchor points along each side."""
    # Direction vector along the shin (knee → foot)
    dx, dy = foot_x - knee_x, foot_y - knee_y
    length = max(1.0, math.hypot(dx, dy))
    # Perpendicular unit vector
    px, py = -dy / length, dx / length

    # 4 sample points along the shin centreline.
    def along(t):
        return (knee_x + dx * t, knee_y + dy * t)
    pts_centre = [along(0.0), along(0.35), along(0.7), along(1.0)]
    widths = [s(knee_width), s(mid_width), s(mid_width - 6), s(ankle_width)]

    # Outer side (away from body)
    outer = [(c[0] + px * w / 2, c[1] + py * w / 2)
             for c, w in zip(pts_centre, widths)]
    # Inner side
    inner = [(c[0] - px * w / 2, c[1] - py * w / 2)
             for c, w in zip(pts_centre, widths)]
    pts = outer + list(reversed(inner))
    _pant_polygon(big, [(int(x), int(y)) for x, y in pts])

    # Knee bulge — extra darker ellipse at the knee end for volume
    kb = pygame.Surface((s(knee_width + 4), s(knee_width // 2 + 4)),
                        pygame.SRCALPHA)
    pygame.draw.ellipse(kb, (*P["PANT_LO"], 200),
                        (0, 0, s(knee_width + 4), s(knee_width // 2 + 4)))
    angle_deg = math.degrees(math.atan2(dy, dx)) - 90
    kb_rot = pygame.transform.rotate(kb, angle_deg)
    rect = kb_rot.get_rect(center=(int(knee_x), int(knee_y)))
    big.blit(kb_rot, rect.topleft)

    # Pleat ripples down the shin (3 lines parallel to centreline)
    for off in (-s(8), 0, s(8)):
        p_start = (along(0.15)[0] + px * off, along(0.15)[1] + py * off)
        p_end   = (along(0.85)[0] + px * off * 0.5,
                   along(0.85)[1] + py * off * 0.5)
        pygame.draw.line(big, P["PANT_LO"],
                         (int(p_start[0]), int(p_start[1])),
                         (int(p_end[0]), int(p_end[1])),
                         max(2, s(1)))

    # Outer-flank gloss highlight
    pygame.draw.line(big, P["PANT_HI"],
                     (int(outer[0][0]), int(outer[0][1])),
                     (int(outer[2][0]), int(outer[2][1])),
                     s(3))
    pygame.draw.line(big, P["PANT_HI"],
                     (int(outer[2][0]), int(outer[2][1])),
                     (int(outer[3][0]), int(outer[3][1])),
                     s(2))


# ─────────────────────────────────────────────────────────────────────────────
# All 5 variants below are FULL LOTUS (padmasana) — both feet rest on
# top of opposite thighs. They vary in how FULL / BAGGY / DECORATED the
# pants are. Variant 1 is the most modest; variant 5 is maximum poof.
# ─────────────────────────────────────────────────────────────────────────────


def _full_lotus_pose(big, cx, hip_w=20, widest_w=60, knee_w=44,
                     hip_y_n=248, widest_y_n=278, knee_y_n=302,
                     foot_y_n=270, slipper_scale=1.0,
                     extra_pleats=False, extra_drape=False,
                     gold_trim=False, embroidery=False):
    """Compose a full-lotus seat with configurable fullness.

    `hip_w`, `widest_w`, `knee_w` are *half-widths* in native px:
        - hip_w     = how wide the hip seat-edge is
        - widest_w  = how far the thigh bulges out at its widest
        - knee_w    = how wide the knee/ankle edge is
    `extra_pleats`, `extra_drape`, `gold_trim`, `embroidery` flip
    additional decorations on.
    """
    hip_y    = s(hip_y_n)
    widest_y = s(widest_y_n)
    knee_y   = s(knee_y_n)
    foot_y   = s(foot_y_n)

    # ── THIGHS (drawn first, very baggy) ────────────────────────────
    for side in (-1, +1):
        _baggy_thigh(big, cx, side,
                     hip_w=hip_w, top_y=hip_y,
                     widest_y=widest_y, widest_w=widest_w,
                     knee_y=knee_y, knee_w=knee_w)

    # ── Optional extra fabric drape: a hanging fold below each thigh
    if extra_drape:
        for side in (-1, +1):
            drape = [
                (cx + side * s(knee_w + 6),  knee_y + s(4)),
                (cx + side * s(knee_w - 12), knee_y + s(20)),
                (cx + side * s(knee_w - 32), knee_y + s(24)),
                (cx + side * s(knee_w - 28), knee_y + s(8)),
            ]
            _pant_polygon(big, drape)
            pygame.draw.line(big, P["PANT_LO"],
                             ((drape[0][0] + drape[3][0]) // 2,
                              (drape[0][1] + drape[3][1]) // 2),
                             ((drape[1][0] + drape[2][0]) // 2,
                              (drape[1][1] + drape[2][1]) // 2),
                             max(2, s(1)))

    # ── Optional extra pleats
    if extra_pleats:
        for side in (-1, +1):
            for px_off, py_top, py_bot in (
                    (s(-2), s(8), s(38)),
                    (s(-10), s(6), s(36)),
                    (s(-20), s(4), s(32)),
                    (s(-28), s(2), s(28))):
                pygame.draw.line(big, (35, 95, 145),
                                 (cx + side * (s(widest_w - 8) + px_off),
                                  hip_y + py_top),
                                 (cx + side * (s(widest_w - 14) + px_off),
                                  hip_y + py_bot),
                                 max(1, s(1)))

    # ── SHINS (lotus — feet curve UP on top of opposite thigh) ──────
    # Steeper angle now so the shin reads as bent UP, not horizontal.
    # RIGHT shin: from right knee outer-down to ankle resting on LEFT
    # thigh outer-upper. Wider and tapered.
    _full_shin(big, cx, side=+1,
               knee_x=cx + s(widest_w - 4), knee_y=widest_y + s(8),
               foot_x=cx - s(widest_w - 20), foot_y=foot_y + s(2),
               knee_width=46, mid_width=40, ankle_width=24)
    # LEFT shin mirrored
    _full_shin(big, cx, side=-1,
               knee_x=cx - s(widest_w - 4), knee_y=widest_y + s(8),
               foot_x=cx + s(widest_w - 20), foot_y=foot_y + s(2),
               knee_width=46, mid_width=40, ankle_width=24)

    # ── Slippers + ankle cuffs ON TOP of opposite thighs ───────────
    # Pushed further out so they sit on the thigh bulge, not over
    # the central sash buckle. Bigger scale so they balance the
    # fuller pants.
    big_sl_scale = slipper_scale * 1.15
    big_cuff_w   = 26
    # Right foot on left thigh outer
    _slipper(big, cx - s(widest_w - 22), foot_y - s(2),
             angle_deg=12, mirror=True, scale=big_sl_scale)
    _gold_ankle_cuff(big, cx - s(widest_w - 12), foot_y + s(2),
                     angle_deg=22, w_native=big_cuff_w)
    # Left foot on right thigh outer
    _slipper(big, cx + s(widest_w - 22), foot_y - s(2),
             angle_deg=-12, scale=big_sl_scale)
    _gold_ankle_cuff(big, cx + s(widest_w - 12), foot_y + s(2),
                     angle_deg=-22, w_native=big_cuff_w)

    # ── Optional gold trim along the knee bulge ─────────────────────
    if gold_trim:
        for side in (-1, +1):
            pygame.draw.arc(big, P["GOLD_LO"],
                            (cx + side * s(widest_w - 16) - s(20),
                             widest_y - s(10),
                             s(40), s(28)),
                            math.radians(20 if side > 0 else 110),
                            math.radians(160 if side > 0 else 250),
                            max(3, s(2)))
            pygame.draw.arc(big, P["GOLD"],
                            (cx + side * s(widest_w - 16) - s(20),
                             widest_y - s(10),
                             s(40), s(28)),
                            math.radians(20 if side > 0 else 110),
                            math.radians(160 if side > 0 else 250),
                            max(2, s(1)))

    # ── Optional embroidery: gem-dotted line along the lower edge
    if embroidery:
        for side in (-1, +1):
            for fx in range(0, 35, 6):
                ex = cx + side * s(widest_w - fx - 4)
                ey = widest_y + s(20)
                pygame.draw.circle(big, P["GOLD"],
                                   (ex, ey), max(1, s(1)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 1 — Full lotus, fuller pants (baseline upgrade from v2)
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_full_lotus(big, cx):
    _full_lotus_pose(big, cx,
                     hip_w=22, widest_w=58, knee_w=42,
                     extra_pleats=False)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 2 — Full lotus, baggy + pleated
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_ankle_cross(big, cx):
    _full_lotus_pose(big, cx,
                     hip_w=24, widest_w=66, knee_w=46,
                     extra_pleats=True)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 3 — Full lotus, gold trim along knees
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_tight_tuck(big, cx):
    _full_lotus_pose(big, cx,
                     hip_w=22, widest_w=64, knee_w=44,
                     extra_pleats=True,
                     gold_trim=True,
                     embroidery=True)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 4 — Full lotus, EXTRA baggy with drape hanging below
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_half_lotus_smoke(big, cx):
    _full_lotus_pose(big, cx,
                     hip_w=26, widest_w=70, knee_w=50,
                     extra_pleats=True,
                     extra_drape=True)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 5 — Full lotus, MAXIMUM poof MC-Hammer / Disney genie style
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_side_recline(big, cx):
    _full_lotus_pose(big, cx,
                     hip_w=28, widest_w=78, knee_w=54,
                     hip_y_n=246, widest_y_n=280, knee_y_n=308,
                     foot_y_n=270,
                     extra_pleats=True,
                     extra_drape=True,
                     gold_trim=True,
                     embroidery=True,
                     slipper_scale=1.05)


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
    ("1 — Fuller lotus",            draw_crossed_legs_full_lotus),
    ("2 — Baggy + pleated",         draw_crossed_legs_ankle_cross),
    ("3 — Gold trim + embroidery",  draw_crossed_legs_tight_tuck),
    ("4 — Extra baggy + drape",     draw_crossed_legs_half_lotus_smoke),
    ("5 — Max poof Disney-genie",   draw_crossed_legs_side_recline),
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
