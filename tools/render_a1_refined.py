"""Render the refined A1 (Classic Aladdin) genie at high resolution.

Per user feedback: keep the A1 silhouette identity but raise it to
high-end design quality:
  - higher resolution (native 320×460, ×6 supersample)
  - two legs (harem pants + curled-toe slippers) instead of smoke tail
  - properly drawn crossed arms with separately rendered forearms,
    biceps, elbows, fists — clearly readable X
  - more layered shading + multi-tone gradients on every body part
  - finer face: defined nose, layered hair, faceted gems, eye glints
  - decorative details: armbands, anklets, embroidered pants band,
    multi-gem buckle, hair tuft over the headband

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_a1_refined [tag]
"""
import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie_designs")
os.makedirs(OUT_DIR, exist_ok=True)

# Higher canvas + supersample than v5 (240×340 ×5 → 320×460 ×6).
W, H, SS = 320, 460, 6
PW, PH = W * SS, H * SS
SKY = (110, 175, 220)


# ─────────────────────────────────────────────────────────────────────────────
# Palette
# ─────────────────────────────────────────────────────────────────────────────
P = dict(
    # Skin (cyan/teal gradient)
    SKIN     = ( 70, 175, 220),
    SKIN_HI  = (175, 230, 252),
    SKIN_MID = (110, 200, 235),
    SKIN_LO  = ( 25, 110, 170),
    SKIN_DK  = ( 12,  70, 120),
    # Pants (deeper teal so they sit visually below the body)
    PANT     = ( 40, 130, 180),
    PANT_HI  = ( 90, 175, 220),
    PANT_MID = ( 65, 150, 200),
    PANT_LO  = ( 18,  85, 140),
    PANT_DK  = (  8,  55, 100),
    # Gold
    GOLD     = (245, 205, 105),
    GOLD_HI  = (255, 240, 175),
    GOLD_MID = (220, 175,  70),
    GOLD_LO  = (160, 115,  30),
    GOLD_DK  = (110,  75,  15),
    # Gems
    RUBY     = (220,  60,  80),
    RUBY_HI  = (255, 175, 195),
    EMERALD  = ( 65, 180,  95),
    SAPPHIRE = ( 70, 130, 220),
    # Other
    WHITE    = (250, 250, 245),
    HAIR     = ( 28,  22,  20),
    HAIR_HI  = ( 75,  55,  45),
    BLACK    = ( 18,  14,  10),
    CYAN     = (160, 230, 255),
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def s(v):
    """Convenience: scale native px to supersample px."""
    return int(v * SS)


def ell(surf, color, cx, cy, w, h):
    """Centred ellipse."""
    pygame.draw.ellipse(surf, color,
                        (int(cx - w / 2), int(cy - h / 2),
                         int(w), int(h)))


def aa_circle(surf, color, cx, cy, r):
    pygame.draw.circle(surf, color, (int(cx), int(cy)), int(r))


def gradient_ellipse(surf, cx, cy, w, h, colors, alpha=255):
    """Stack 3+ concentric ellipses from outer (lo) to inner (hi)
    for soft volume shading."""
    n = len(colors)
    for i, col in enumerate(colors):
        k = 1.0 - i / n
        ew = int(w * (0.35 + 0.65 * k))
        eh = int(h * (0.35 + 0.65 * k))
        s_off_x = int((w - ew) * 0.15)  # offset highlight slightly up-left
        s_off_y = int((h - eh) * 0.15)
        if alpha < 255:
            srf = pygame.Surface((ew + 2, eh + 2), pygame.SRCALPHA)
            pygame.draw.ellipse(srf, (*col, alpha),
                                (1, 1, ew, eh))
            surf.blit(srf, (int(cx - ew / 2 - s_off_x),
                            int(cy - eh / 2 - s_off_y)))
        else:
            pygame.draw.ellipse(surf, col,
                                (int(cx - ew / 2 - s_off_x),
                                 int(cy - eh / 2 - s_off_y),
                                 ew, eh))


def gem_facet(surf, cx, cy, r, color, hi_color, lo_color):
    """Faceted gem — 4-point diamond with bright facet on upper-left
    and shadow on lower-right."""
    pts_full = [(cx, cy - r), (cx + r, cy),
                (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(surf, lo_color, pts_full)
    # Inner faceted shape
    inner = int(r * 0.85)
    pts_inner = [(cx, cy - inner), (cx + inner, cy),
                 (cx, cy + inner), (cx - inner, cy)]
    pygame.draw.polygon(surf, color, pts_inner)
    # Upper-left highlight facet
    pygame.draw.polygon(surf, hi_color,
                        [(cx, cy - inner),
                         (cx - int(inner * 0.55), cy),
                         (cx - int(inner * 0.3), cy - int(inner * 0.3))])
    # White sparkle dot
    pygame.draw.circle(surf, (255, 255, 255),
                       (int(cx - inner * 0.3), int(cy - inner * 0.5)),
                       max(1, int(r * 0.12)))


def outlined_polygon(surf, points, fill, outline, w=None):
    if w is None:
        w = max(2, int(SS * 0.4))
    pygame.draw.polygon(surf, fill, points)
    pygame.draw.polygon(surf, outline, points, w)


# ─────────────────────────────────────────────────────────────────────────────
# Body parts
# ─────────────────────────────────────────────────────────────────────────────

def draw_smoke_aura(big, cx, t):
    """Atmospheric smoke wisps drifting behind/below the figure —
    just ambience now that the figure has real legs."""
    for i, (dx, dy, w, h, alpha) in enumerate((
            (-90, 380, 130, 70, 60),
            ( 90, 380, 130, 70, 60),
            (  0, 420, 200, 60, 50),
            (-130, 330, 90, 50, 50),
            ( 130, 330, 90, 50, 50),
            )):
        sway = math.sin(t * 1.5 + i * 0.7) * s(3)
        srf = pygame.Surface((s(w + 4), s(h + 4)), pygame.SRCALPHA)
        pygame.draw.ellipse(srf, (*P["SKIN_HI"], alpha),
                            (s(2), s(2), s(w), s(h)))
        big.blit(srf, (s(W // 2 + dx - w / 2) + sway, s(dy - h / 2)))


def draw_pants(big, cx, t):
    """Harem pants with gold ankle cuffs + embroidered waist band."""
    # Hips top
    hip_y = s(248)
    knee_y = s(360)
    ankle_y = s(424)
    # Each pant leg as polygon (baggy on outside, cinched at ankle)
    for side in (-1, 1):
        # Outer + inner boundary
        leg_top_x_out = cx + side * s(38)
        leg_top_x_in  = cx + side * s(8)
        leg_knee_x_out = cx + side * s(48)  # baggy outward
        leg_knee_x_in  = cx + side * s(14)
        leg_ankle_x_out = cx + side * s(26)  # cinched
        leg_ankle_x_in  = cx + side * s(10)
        # Pant leg polygon
        pts = [
            (leg_top_x_in, hip_y),
            (leg_top_x_out, hip_y),
            (leg_knee_x_out, knee_y),
            (leg_ankle_x_out, ankle_y),
            (leg_ankle_x_in, ankle_y),
            (leg_knee_x_in, knee_y),
        ]
        # Shadow polygon
        shadow_pts = [(x + s(2), y + s(2)) for x, y in pts]
        pygame.draw.polygon(big, P["PANT_DK"], shadow_pts)
        pygame.draw.polygon(big, P["PANT"], pts)
        # Outer highlight stripe
        pygame.draw.line(big, P["PANT_HI"],
                         (leg_top_x_out - side * s(4), hip_y + s(6)),
                         (leg_knee_x_out - side * s(4), knee_y - s(8)),
                         s(3))
        # Inner shadow line
        pygame.draw.line(big, P["PANT_LO"],
                         (leg_top_x_in + side * s(3), hip_y + s(8)),
                         (leg_ankle_x_in + side * s(2), ankle_y - s(4)),
                         s(2))
        # Pleat ripple — two faint vertical curves
        for off in (s(8), s(20)):
            pygame.draw.line(big, P["PANT_LO"],
                             (cx + side * (s(18) + off), hip_y + s(12)),
                             (cx + side * (s(14) + off // 2), ankle_y - s(10)),
                             max(1, s(1)))
        # Gold ankle cuff
        cuff_y = ankle_y - s(2)
        cuff_top_x_out = leg_ankle_x_out + side * s(3)
        cuff_top_x_in  = leg_ankle_x_in - side * s(3)
        cuff_pts = [
            (cuff_top_x_in, cuff_y - s(8)),
            (cuff_top_x_out, cuff_y - s(8)),
            (leg_ankle_x_out + side * s(2), cuff_y + s(6)),
            (leg_ankle_x_in - side * s(2), cuff_y + s(6)),
        ]
        pygame.draw.polygon(big, P["GOLD_LO"],
                            [(x + s(1), y + s(1)) for x, y in cuff_pts])
        pygame.draw.polygon(big, P["GOLD"], cuff_pts)
        pygame.draw.line(big, P["GOLD_HI"],
                         (cuff_pts[0][0] + s(2), cuff_pts[0][1] + s(2)),
                         (cuff_pts[1][0] - s(2), cuff_pts[1][1] + s(2)),
                         s(2))
        # Small gem on the cuff
        gx = cx + side * s(18)
        gy = cuff_y - s(1)
        gem_facet(big, gx, gy, s(3), P["RUBY"], P["RUBY_HI"], (110, 30, 40))

    # Pants waist band (gold strip)
    waist_pts = [
        (cx - s(46), hip_y - s(4)),
        (cx + s(46), hip_y - s(4)),
        (cx + s(42), hip_y + s(8)),
        (cx - s(42), hip_y + s(8)),
    ]
    pygame.draw.polygon(big, P["GOLD_LO"],
                        [(x + s(1), y + s(1)) for x, y in waist_pts])
    pygame.draw.polygon(big, P["GOLD"], waist_pts)
    pygame.draw.line(big, P["GOLD_HI"],
                     (waist_pts[0][0] + s(3), waist_pts[0][1] + s(2)),
                     (waist_pts[1][0] - s(3), waist_pts[1][1] + s(2)),
                     s(2))
    # Embroidery dots along the waist band
    for fx in (-s(35), -s(20), -s(5), s(10), s(25), s(40)):
        pygame.draw.circle(big, P["GOLD_DK"],
                           (cx + fx, hip_y + s(2)), max(1, s(1)))


def draw_slippers(big, cx):
    """Curled-toe Arabian slippers in gold + ruby."""
    slipper_y = s(440)
    for side in (-1, 1):
        sx = cx + side * s(18)
        # Sole
        sole_pts = [
            (sx - s(12), slipper_y + s(4)),
            (sx + s(16), slipper_y + s(4)),
            (sx + s(24), slipper_y - s(2)),  # curled toe lifts up
            (sx + s(20), slipper_y - s(8)),
            (sx + s(8), slipper_y - s(4)),
            (sx - s(10), slipper_y - s(4)),
        ]
        if side < 0:
            sole_pts = [(2 * sx - x, y) for x, y in sole_pts]
        pygame.draw.polygon(big, P["GOLD_DK"],
                            [(x + s(1), y + s(1)) for x, y in sole_pts])
        pygame.draw.polygon(big, P["GOLD"], sole_pts)
        # Highlight on top of slipper
        pygame.draw.line(big, P["GOLD_HI"],
                         (sx - s(6), slipper_y - s(2)),
                         (sx + side * s(10), slipper_y - s(5)),
                         s(2))
        # Ruby gem on the toe
        toe_x = sx + side * s(16)
        toe_y = slipper_y - s(4)
        gem_facet(big, toe_x, toe_y, s(3), P["RUBY"], P["RUBY_HI"],
                  (110, 30, 40))


def draw_torso(big, cx):
    """Bare muscular V-torso with multi-tone shading."""
    neck_y     = s(120)
    shoulder_y = s(138)
    waist_y    = s(220)
    base_y     = s(252)
    pts = [
        (cx - s(20), neck_y),
        (cx - s(58), shoulder_y),
        (cx - s(34), waist_y),
        (cx - s(36), base_y),
        (cx + s(36), base_y),
        (cx + s(34), waist_y),
        (cx + s(58), shoulder_y),
        (cx + s(20), neck_y),
    ]
    # Drop shadow
    pygame.draw.polygon(big, P["SKIN_DK"],
                        [(x + s(2), y + s(3)) for x, y in pts])
    # Mid-tone base
    pygame.draw.polygon(big, P["SKIN_LO"], pts)
    # Inner main fill (slightly smaller)
    inner = [
        (cx - s(18), neck_y + s(1)),
        (cx - s(54), shoulder_y + s(1)),
        (cx - s(32), waist_y - s(1)),
        (cx - s(34), base_y - s(1)),
        (cx + s(34), base_y - s(1)),
        (cx + s(32), waist_y - s(1)),
        (cx + s(54), shoulder_y + s(1)),
        (cx + s(18), neck_y + s(1)),
    ]
    pygame.draw.polygon(big, P["SKIN"], inner)
    # Soft top-down highlight gradient (alpha stripe along upper chest)
    srf = pygame.Surface((s(120), s(40)), pygame.SRCALPHA)
    pygame.draw.ellipse(srf, (*P["SKIN_HI"], 100),
                        (0, 0, s(120), s(40)))
    big.blit(srf, (cx - s(60), shoulder_y - s(2)))
    # ── pecs ──
    for sx in (-s(20), s(20)):
        # Pec base (shaded)
        ell(big, P["SKIN_HI"], cx + sx, s(150), s(38), s(22))
        # Pec under-shadow arc
        pygame.draw.arc(big, P["SKIN_LO"],
                        (cx + sx - s(19), s(154), s(38), s(16)),
                        math.radians(0), math.radians(180), s(2))
        # Tiny shaded crease where pec meets sternum
        pygame.draw.arc(big, P["SKIN_DK"],
                        (cx + sx - s(19), s(155), s(38), s(14)),
                        math.radians(20), math.radians(160), max(1, s(1)))
    # Sternum line
    pygame.draw.line(big, P["SKIN_LO"],
                     (cx, s(150)), (cx, s(180)), s(2))
    # ── abs ──
    for ay in (s(184), s(200), s(216)):
        for ax in (-s(8), s(8)):
            ell(big, P["SKIN_HI"], cx + ax, ay, s(14), s(8))
            pygame.draw.line(big, P["SKIN_LO"],
                             (cx + ax, ay - s(2)),
                             (cx + ax, ay + s(2)), max(1, s(1)))
    pygame.draw.line(big, P["SKIN_LO"],
                     (cx, s(178)), (cx, s(225)), max(1, s(1)))
    # Side oblique highlights
    for sx in (-s(28), s(28)):
        pygame.draw.line(big, P["SKIN_HI"],
                         (cx + sx, s(180)), (cx + int(sx * 0.7), s(220)),
                         max(1, s(1)))


def draw_arms(big, cx):
    """Crossed arms drawn as forearm + bicep + hand polygons with
    clear overlap shadow at the centre."""
    L = P
    # ── Arm 1 (lower) — RIGHT arm: right shoulder to LEFT waist ──
    sh1 = (cx + s(56), s(138))
    el1 = (cx + s(28), s(170))
    wr1 = (cx - s(30), s(200))
    # ── Arm 2 (upper) — LEFT arm: left shoulder to RIGHT waist ──
    sh2 = (cx - s(56), s(138))
    el2 = (cx - s(28), s(168))
    wr2 = (cx + s(30), s(198))

    # Draw arm 1 (lower) first
    _draw_one_arm(big, sh1, el1, wr1, side=+1)
    # Cross-shadow under where arm 2 will lay
    s_ovr = pygame.Surface((s(70), s(28)), pygame.SRCALPHA)
    pygame.draw.ellipse(s_ovr, (*L["SKIN_DK"], 130), (0, 0, s(70), s(28)))
    big.blit(s_ovr, (cx - s(35), s(166)))
    # Draw arm 2 (upper) on top
    _draw_one_arm(big, sh2, el2, wr2, side=-1)


def _draw_one_arm(big, shoulder, elbow, wrist, side):
    """One muscular arm with shoulder ball, bicep, forearm, hand."""
    L = P
    sh_x, sh_y = shoulder
    el_x, el_y = elbow
    wr_x, wr_y = wrist

    # ── Upper arm (bicep) drawn as elongated ellipse ──
    mx = (sh_x + el_x) // 2
    my = (sh_y + el_y) // 2
    dx = el_x - sh_x
    dy = el_y - sh_y
    length = math.hypot(dx, dy)
    angle = math.degrees(math.atan2(dy, dx))
    # Bicep ellipse
    bicep_surf = pygame.Surface((int(length * 1.2), s(26)),
                                pygame.SRCALPHA)
    bw, bh = bicep_surf.get_size()
    pygame.draw.ellipse(bicep_surf, L["SKIN_DK"], (s(1), s(2), bw - s(2), bh - s(4)))
    pygame.draw.ellipse(bicep_surf, L["SKIN_LO"], (0, 0, bw, bh))
    pygame.draw.ellipse(bicep_surf, L["SKIN"], (s(2), s(2), bw - s(4), bh - s(6)))
    pygame.draw.ellipse(bicep_surf, L["SKIN_HI"],
                        (s(4), s(2), int(bw * 0.4), s(7)))
    bicep_rot = pygame.transform.rotate(bicep_surf, -angle)
    rect = bicep_rot.get_rect(center=(mx, my))
    big.blit(bicep_rot, rect.topleft)

    # ── Elbow ball ──
    aa_circle(big, L["SKIN_DK"], el_x + s(1), el_y + s(1), s(10))
    aa_circle(big, L["SKIN_LO"], el_x, el_y, s(9))
    aa_circle(big, L["SKIN"], el_x, el_y, s(8))
    aa_circle(big, L["SKIN_HI"], el_x - s(2), el_y - s(2), s(3))

    # ── Forearm (elbow → wrist) ──
    dx2 = wr_x - el_x
    dy2 = wr_y - el_y
    length2 = math.hypot(dx2, dy2)
    angle2 = math.degrees(math.atan2(dy2, dx2))
    fore_w = int(length2 * 1.15)
    fore_h = s(22)
    fore_surf = pygame.Surface((fore_w, fore_h), pygame.SRCALPHA)
    pygame.draw.ellipse(fore_surf, L["SKIN_DK"], (s(1), s(2), fore_w - s(2), fore_h - s(4)))
    pygame.draw.ellipse(fore_surf, L["SKIN_LO"], (0, 0, fore_w, fore_h))
    pygame.draw.ellipse(fore_surf, L["SKIN"], (s(2), s(2), fore_w - s(4), fore_h - s(6)))
    pygame.draw.ellipse(fore_surf, L["SKIN_HI"],
                        (s(4), s(2), int(fore_w * 0.4), s(6)))
    fore_rot = pygame.transform.rotate(fore_surf, -angle2)
    rect = fore_rot.get_rect(center=((el_x + wr_x) // 2, (el_y + wr_y) // 2))
    big.blit(fore_rot, rect.topleft)

    # ── Gold cuff at wrist ──
    aa_circle(big, L["GOLD_DK"], wr_x + s(1), wr_y + s(1), s(12))
    aa_circle(big, L["GOLD_LO"], wr_x, wr_y, s(11))
    aa_circle(big, L["GOLD"], wr_x, wr_y, s(10))
    aa_circle(big, L["GOLD_HI"], wr_x - s(3), wr_y - s(3), s(4))
    # Tiny engraved band ring around the cuff
    pygame.draw.circle(big, L["GOLD_DK"], (wr_x, wr_y), s(10), max(1, s(1)))

    # ── Fist (closed hand) ──
    # Fist sits just past the cuff in the arm direction
    fist_x = wr_x + int(dx2 / length2 * s(11))
    fist_y = wr_y + int(dy2 / length2 * s(11))
    # Fist body
    aa_circle(big, L["SKIN_DK"], fist_x + s(1), fist_y + s(1), s(10))
    aa_circle(big, L["SKIN_LO"], fist_x, fist_y, s(9))
    aa_circle(big, L["SKIN"], fist_x, fist_y, s(8))
    aa_circle(big, L["SKIN_HI"], fist_x - s(2), fist_y - s(2), s(3))
    # Knuckle bumps (3 small ellipses on top)
    for k in (-s(4), 0, s(4)):
        ell(big, L["SKIN_LO"], fist_x + k, fist_y - s(5), s(3), s(2))
    # Tiny shadow line under the knuckles
    pygame.draw.line(big, L["SKIN_DK"],
                     (fist_x - s(5), fist_y - s(3)),
                     (fist_x + s(5), fist_y - s(3)), max(1, s(1)))
    # ── Armband above the wrist cuff ──
    ab_x = el_x + int((wr_x - el_x) * 0.5)
    ab_y = el_y + int((wr_y - el_y) * 0.5)
    # Find tangent perpendicular to arm
    perp = (-(wr_y - el_y) / length2, (wr_x - el_x) / length2)
    ab_surf = pygame.Surface((s(20), s(10)), pygame.SRCALPHA)
    pygame.draw.ellipse(ab_surf, L["GOLD_LO"], (0, 0, s(20), s(10)))
    pygame.draw.ellipse(ab_surf, L["GOLD"], (s(1), s(1), s(18), s(8)))
    pygame.draw.line(ab_surf, L["GOLD_HI"], (s(3), s(3)), (s(17), s(3)), s(1))
    ab_rot = pygame.transform.rotate(ab_surf, -angle2)
    rect = ab_rot.get_rect(center=(ab_x, ab_y))
    big.blit(ab_rot, rect.topleft)


def draw_sash(big, cx):
    """Gold sash at the waist with multi-gem buckle."""
    sash_y = s(245)
    sash_pts = [
        (cx - s(54), sash_y - s(6)),
        (cx + s(54), sash_y - s(5)),
        (cx + s(48), sash_y + s(14)),
        (cx - s(48), sash_y + s(13)),
    ]
    pygame.draw.polygon(big, P["GOLD_DK"],
                        [(x + s(1), y + s(2)) for x, y in sash_pts])
    pygame.draw.polygon(big, P["GOLD_LO"], sash_pts)
    pygame.draw.polygon(big, P["GOLD"],
                        [(x, y + s(1)) for x, y in sash_pts])
    # Top highlight ribbon
    pygame.draw.line(big, P["GOLD_HI"],
                     (sash_pts[0][0] + s(3), sash_pts[0][1] + s(3)),
                     (sash_pts[1][0] - s(3), sash_pts[1][1] + s(3)),
                     s(2))
    # Sash embroidery — small repeated diamond pattern
    for fx in (-s(40), -s(28), -s(16), s(0), s(12), s(24), s(36)):
        cx_p, cy_p = cx + fx, sash_y + s(5)
        pygame.draw.polygon(big, P["GOLD_DK"],
                            [(cx_p, cy_p - s(2)),
                             (cx_p + s(2), cy_p),
                             (cx_p, cy_p + s(2)),
                             (cx_p - s(2), cy_p)])
    # ── Buckle (large gold disc with three gems) ──
    bx, by = cx, sash_y + s(5)
    aa_circle(big, P["GOLD_DK"], bx + s(1), by + s(1), s(16))
    aa_circle(big, P["GOLD_LO"], bx, by, s(15))
    aa_circle(big, P["GOLD"], bx, by, s(13))
    aa_circle(big, P["GOLD_HI"], bx - s(4), by - s(4), s(4))
    # Three faceted gems: ruby centre + emerald left + sapphire right
    gem_facet(big, bx, by, s(7), P["RUBY"], P["RUBY_HI"], (110, 30, 40))
    gem_facet(big, bx - s(10), by, s(3), P["EMERALD"], (180, 245, 200), (20, 100, 50))
    gem_facet(big, bx + s(10), by, s(3), P["SAPPHIRE"], (170, 215, 255), (20, 60, 130))


def draw_head(big, cx, head_cy, head_r):
    """Head with cheek + chin + nose + earlobe shading."""
    # Shadow
    aa_circle(big, P["SKIN_DK"], cx + s(3), head_cy + s(3), head_r + s(1))
    # Base
    aa_circle(big, P["SKIN_LO"], cx, head_cy, head_r)
    # Mid (slightly inset, brighter)
    aa_circle(big, P["SKIN"], cx, head_cy - s(1), head_r - s(2))
    # Highlight on upper-left
    aa_circle(big, P["SKIN_HI"], cx - head_r // 3, head_cy - head_r // 3,
              head_r // 3)
    # Cheek soft glow (right side)
    cheek = pygame.Surface((s(20), s(14)), pygame.SRCALPHA)
    pygame.draw.ellipse(cheek, (255, 180, 200, 80), (0, 0, s(20), s(14)))
    big.blit(cheek, (cx + s(4), head_cy + s(6)))
    cheek2 = pygame.Surface((s(20), s(14)), pygame.SRCALPHA)
    pygame.draw.ellipse(cheek2, (255, 180, 200, 60), (0, 0, s(20), s(14)))
    big.blit(cheek2, (cx - s(24), head_cy + s(6)))
    # Chin shadow
    pygame.draw.arc(big, P["SKIN_LO"],
                    (cx - head_r + s(4), head_cy + s(4),
                     2 * head_r - s(8), head_r),
                    math.radians(200), math.radians(340), s(2))
    # Nose
    nose_pts = [
        (cx, head_cy - s(2)),
        (cx + s(3), head_cy + s(6)),
        (cx, head_cy + s(8)),
        (cx - s(3), head_cy + s(6)),
    ]
    pygame.draw.polygon(big, P["SKIN_LO"], nose_pts)
    pygame.draw.polygon(big, P["SKIN_HI"],
                        [(cx - s(1), head_cy - s(1)),
                         (cx, head_cy + s(2)),
                         (cx - s(2), head_cy + s(3))])
    # Subtle nostrils
    pygame.draw.circle(big, P["SKIN_DK"],
                       (cx - s(2), head_cy + s(6)), max(1, s(1)))
    pygame.draw.circle(big, P["SKIN_DK"],
                       (cx + s(2), head_cy + s(6)), max(1, s(1)))


def draw_topknot_and_headband(big, cx, head_cy, head_r):
    """Black hair tuft + topknot + gold headband + central ruby
    + small hair locks across the forehead."""
    # Hair locks/tuft over the forehead
    tuft_pts = [
        (cx - head_r + s(4), head_cy - s(16)),
        (cx - s(8), head_cy - s(20)),
        (cx + s(8), head_cy - s(20)),
        (cx + head_r - s(4), head_cy - s(16)),
        (cx + s(14), head_cy - s(11)),
        (cx, head_cy - s(8)),
        (cx - s(14), head_cy - s(11)),
    ]
    pygame.draw.polygon(big, P["HAIR"], tuft_pts)
    pygame.draw.line(big, P["HAIR_HI"],
                     (cx - s(20), head_cy - s(17)),
                     (cx + s(20), head_cy - s(17)),
                     max(1, s(1)))

    # Topknot at the top of head
    tk_cx = cx
    tk_cy = head_cy - head_r - s(4)
    # Base of the topknot (small gold tie)
    pygame.draw.rect(big, P["GOLD"],
                     (tk_cx - s(8), tk_cy + s(6), s(16), s(4)))
    pygame.draw.line(big, P["GOLD_HI"],
                     (tk_cx - s(6), tk_cy + s(7)),
                     (tk_cx + s(6), tk_cy + s(7)), max(1, s(1)))
    # Black hair ball
    aa_circle(big, P["BLACK"], tk_cx + s(1), tk_cy + s(1), s(14))
    aa_circle(big, P["HAIR"], tk_cx, tk_cy, s(13))
    aa_circle(big, P["HAIR_HI"], tk_cx - s(3), tk_cy - s(3), s(4))

    # Gold headband (3-layer)
    band_y = head_cy - s(18)
    pygame.draw.rect(big, P["GOLD_DK"],
                     (cx - s(38), band_y - s(2), s(76), s(11)))
    pygame.draw.rect(big, P["GOLD_LO"],
                     (cx - s(38), band_y - s(1), s(76), s(9)))
    pygame.draw.rect(big, P["GOLD"],
                     (cx - s(36), band_y, s(72), s(7)))
    pygame.draw.line(big, P["GOLD_HI"],
                     (cx - s(34), band_y + s(2)),
                     (cx + s(34), band_y + s(2)), max(1, s(1)))
    # Engraved band pattern
    for fx in (-s(30), -s(20), -s(10), s(10), s(20), s(30)):
        pygame.draw.line(big, P["GOLD_DK"],
                         (cx + fx, band_y + s(1)),
                         (cx + fx, band_y + s(6)),
                         max(1, s(1)))
    # Central ruby (diamond cut)
    gem_facet(big, cx, band_y + s(3), s(8),
              P["RUBY"], P["RUBY_HI"], (110, 30, 40))
    # Mini gold spikes flanking the ruby
    for sxd in (-s(12), s(12)):
        pygame.draw.polygon(big, P["GOLD"],
                            [(cx + sxd - s(2), band_y - s(2)),
                             (cx + sxd, band_y - s(6)),
                             (cx + sxd + s(2), band_y - s(2))])


def draw_face(big, cx, head_cy):
    """Brow + eyes + mustache + grin + goatee."""
    # ── Brows (thick angled) ──
    pygame.draw.polygon(big, P["HAIR"],
                        [(cx - s(20), head_cy - s(6)),
                         (cx - s(5), head_cy - s(9)),
                         (cx - s(5), head_cy - s(4)),
                         (cx - s(20), head_cy - s(2))])
    pygame.draw.polygon(big, P["HAIR"],
                        [(cx + s(20), head_cy - s(6)),
                         (cx + s(5), head_cy - s(9)),
                         (cx + s(5), head_cy - s(4)),
                         (cx + s(20), head_cy - s(2))])

    # ── Eyes (whites + iris + pupil + 2 glints) ──
    for sx in (-s(12), s(12)):
        # Whites
        pygame.draw.ellipse(big, P["WHITE"],
                            (cx + sx - s(8), head_cy - s(4),
                             s(16), s(12)))
        # Iris (dark brown)
        aa_circle(big, P["HAIR"], cx + sx, head_cy + s(1), s(5))
        # Pupil
        aa_circle(big, P["BLACK"], cx + sx, head_cy + s(1), s(3))
        # Glints
        aa_circle(big, P["WHITE"], cx + sx - s(2), head_cy - s(1), s(2))
        aa_circle(big, P["WHITE"], cx + sx + s(2), head_cy + s(3),
                  max(1, s(1)))
        # Eyelash hint
        pygame.draw.line(big, P["HAIR"],
                         (cx + sx - s(8), head_cy - s(4)),
                         (cx + sx + s(8), head_cy - s(4)),
                         max(1, s(1)))

    # ── Curled mustache (two arcs ending in spiral curls) ──
    pygame.draw.arc(big, P["HAIR"],
                    (cx - s(20), head_cy + s(10),
                     s(20), s(10)),
                    math.radians(195), math.radians(360), s(3))
    pygame.draw.arc(big, P["HAIR"],
                    (cx, head_cy + s(10),
                     s(20), s(10)),
                    math.radians(180), math.radians(345), s(3))
    # Curl loops at the ends
    for sxc in (-s(20), s(20)):
        aa_circle(big, P["HAIR"], cx + sxc, head_cy + s(13), s(3))
        aa_circle(big, P["HAIR_HI"], cx + sxc - s(1), head_cy + s(12),
                  max(1, s(1)))

    # ── Mouth (confident grin showing teeth) ──
    mt_y = head_cy + s(18)
    # Mouth interior
    pygame.draw.polygon(big, P["HAIR"],
                        [(cx - s(13), mt_y),
                         (cx + s(13), mt_y),
                         (cx + s(10), mt_y + s(8)),
                         (cx - s(10), mt_y + s(8))])
    # Teeth
    pygame.draw.polygon(big, P["WHITE"],
                        [(cx - s(11), mt_y + s(1)),
                         (cx + s(11), mt_y + s(1)),
                         (cx + s(8), mt_y + s(6)),
                         (cx - s(8), mt_y + s(6))])
    for tx in (-s(7), -s(3), s(0), s(3), s(7)):
        pygame.draw.line(big, P["HAIR"],
                         (cx + tx, mt_y + s(1)),
                         (cx + tx, mt_y + s(6)),
                         max(1, s(1)))

    # ── Goatee ──
    pygame.draw.polygon(big, P["HAIR"],
                        [(cx - s(8), mt_y + s(8)),
                         (cx + s(8), mt_y + s(8)),
                         (cx + s(4), mt_y + s(20)),
                         (cx - s(4), mt_y + s(20))])
    pygame.draw.line(big, P["HAIR_HI"],
                     (cx - s(2), mt_y + s(10)),
                     (cx - s(1), mt_y + s(18)),
                     max(1, s(1)))


def draw_earrings(big, cx, head_cy, head_r):
    """Gold hoop earrings with small ruby drops."""
    for sx in (-head_r - s(2), head_r + s(2)):
        ex = cx + sx
        ey = head_cy + s(4)
        # Outer hoop
        pygame.draw.circle(big, P["GOLD_DK"], (ex, ey), s(8), s(2))
        pygame.draw.circle(big, P["GOLD"], (ex, ey), s(7), s(2))
        pygame.draw.circle(big, P["GOLD_HI"], (ex - s(2), ey - s(2)),
                           max(1, s(1)))
        # Ruby drop pendant
        py = ey + s(10)
        pygame.draw.line(big, P["GOLD"], (ex, ey + s(3)),
                         (ex, py - s(2)), max(1, s(1)))
        gem_facet(big, ex, py, s(3), P["RUBY"], P["RUBY_HI"], (110, 30, 40))


def draw_neck(big, cx):
    """Short cylindrical neck connecting head to torso."""
    neck_top = s(100)
    neck_bot = s(120)
    pygame.draw.polygon(big, P["SKIN_DK"],
                        [(cx - s(15), neck_top),
                         (cx + s(15), neck_top),
                         (cx + s(18), neck_bot),
                         (cx - s(18), neck_bot)])
    pygame.draw.polygon(big, P["SKIN_LO"],
                        [(cx - s(14), neck_top),
                         (cx + s(14), neck_top),
                         (cx + s(17), neck_bot - s(1)),
                         (cx - s(17), neck_bot - s(1))])
    pygame.draw.polygon(big, P["SKIN"],
                        [(cx - s(12), neck_top + s(2)),
                         (cx + s(12), neck_top + s(2)),
                         (cx + s(15), neck_bot - s(2)),
                         (cx - s(15), neck_bot - s(2))])
    # Collarbone shadow
    pygame.draw.arc(big, P["SKIN_LO"],
                    (cx - s(40), s(120), s(80), s(20)),
                    math.radians(200), math.radians(340), max(1, s(1)))


def draw_a1_refined(big, cx, t=0.0):
    """Compose the full refined A1 figure in z-order."""
    # 1. Atmosphere behind
    draw_smoke_aura(big, cx, t)
    # 2. Legs/pants/slippers (lowest)
    draw_pants(big, cx, t)
    draw_slippers(big, cx)
    # 3. Torso
    draw_torso(big, cx)
    # 4. Neck
    draw_neck(big, cx)
    # 5. Head (face first, then hair on top)
    head_cy = s(60)
    head_r = s(40)
    draw_head(big, cx, head_cy, head_r)
    draw_face(big, cx, head_cy)
    draw_earrings(big, cx, head_cy, head_r)
    draw_topknot_and_headband(big, cx, head_cy, head_r)
    # 6. Sash + buckle
    draw_sash(big, cx)
    # 7. Arms ON TOP of sash so they read as crossed in front
    draw_arms(big, cx)


# ─────────────────────────────────────────────────────────────────────────────
def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "v6"
    big = pygame.Surface((PW, PH), pygame.SRCALPHA)
    big.fill(SKY)
    cx = PW // 2
    draw_a1_refined(big, cx, t=0.0)
    # Smooth-scale down to native
    portrait = pygame.transform.smoothscale(big, (W, H))
    out = os.path.join(OUT_DIR, f"a1_refined_{tag}.png")
    pygame.image.save(portrait, out)
    print(f"saved {out}")
    # Also a 2× version for higher visual quality
    big2x = pygame.transform.smoothscale(big, (W * 2, H * 2))
    out2 = os.path.join(OUT_DIR, f"a1_refined_{tag}_2x.png")
    pygame.image.save(big2x, out2)
    print(f"saved {out2}")


if __name__ == "__main__":
    main()
