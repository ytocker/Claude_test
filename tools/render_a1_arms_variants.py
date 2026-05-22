"""Render 5 arm-pose variants of the refined A1 genie for review.

Keeps everything in `tools/render_a1_refined.py` (head, face, torso,
pants, slippers, sash, smoke) and ONLY swaps the arms. The current
X-cross diagonal arms are replaced with five natural / welcoming
postures:

  1. Folded forearms (relaxed cool)
  2. Palms-up offering ("what's your wish?")
  3. Hands clasped at waist (butler / dignitary)
  4. Hand on heart + extended (Middle Eastern welcome)
  5. Open arms wide (ta-da welcome)

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_a1_arms_variants [tag]
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
    draw_smoke_aura, draw_pants, draw_slippers,
    draw_torso, draw_neck, draw_head, draw_face,
    draw_earrings, draw_topknot_and_headband, draw_sash,
)

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie_designs")
os.makedirs(OUT_DIR, exist_ok=True)

# Display scale for individual portraits + sheet.
DISPLAY_SCALE = 2


# ─────────────────────────────────────────────────────────────────────────────
# Local arm primitives (mirror _draw_one_arm but unbundled so each pose
# can compose its own geometry)
# ─────────────────────────────────────────────────────────────────────────────

def _segment(big, p0, p1, color, color_lo, color_hi, w=10,
             tapered=False):
    """Limb segment from p0 → p1 as a rotated ellipse with shadow +
    base + highlight stripe. `tapered` thins one end (used for the
    forearm)."""
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    length = max(1.0, math.hypot(dx, dy))
    ang = math.degrees(math.atan2(dy, dx))
    w_px = s(w)
    sw = int(length * 1.15)
    sh = w_px + s(4)
    seg = pygame.Surface((sw, sh), pygame.SRCALPHA)
    # Shadow + base + main fill
    pygame.draw.ellipse(seg, color_lo, (s(1), s(2), sw - s(2), sh - s(4)))
    pygame.draw.ellipse(seg, color, (s(2), s(2), sw - s(4), sh - s(6)))
    pygame.draw.ellipse(seg, color_hi,
                        (s(4), s(2), int(sw * 0.4), s(6)))
    if tapered:
        # Trim the far end to thin the tip (used when a forearm
        # meets a hand directly).
        # No-op for now; ellipse already tapers visually.
        pass
    rot = pygame.transform.rotate(seg, -ang)
    rect = rot.get_rect(center=((x0 + x1) // 2, (y0 + y1) // 2))
    big.blit(rot, rect.topleft)


def _joint(big, center, color, color_lo, color_hi, r=8):
    """Spherical joint (shoulder / elbow)."""
    cx, cy = center
    aa_circle(big, color_lo, cx + s(1), cy + s(1), s(r + 1))
    aa_circle(big, color, cx, cy, s(r))
    aa_circle(big, color_hi, cx - s(r // 3), cy - s(r // 3),
              max(2, s(r // 3)))


def _fist(big, center, color, color_lo, color_hi, r=9):
    """Closed fist with knuckle bumps."""
    cx, cy = center
    aa_circle(big, color_lo, cx + s(1), cy + s(1), s(r + 1))
    aa_circle(big, color, cx, cy, s(r))
    aa_circle(big, color_hi, cx - s(2), cy - s(2), s(r // 3))
    for k in (-s(4), 0, s(4)):
        ell(big, color_lo, cx + k, cy - s(5), s(3), s(2))


def _open_palm(big, center, color, color_lo, color_hi,
               r_w=12, r_h=14, palm_up=True, side=+1):
    """Open palm — wider than tall when palm-up, with 4 finger
    ridges along the top and a thumb on one side."""
    cx, cy = center
    # Palm base ellipse
    aa_circle(big, color_lo, cx + s(1), cy + s(1), s(r_w))
    ell(big, color_lo, cx + s(1), cy + s(1), s(r_w) * 2, s(r_h) * 2)
    ell(big, color, cx, cy, s(r_w) * 2, s(r_h) * 2)
    ell(big, color_hi, cx - s(2), cy - s(3),
        int(s(r_w) * 1.4), s(4))
    # 4 finger ridges along the top edge (small ellipses)
    finger_y = cy - s(r_h - 1)
    for fx, fw in ((-s(8), s(3)), (-s(3), s(3)),
                   (s(2), s(3)), (s(7), s(3))):
        ell(big, color, cx + fx, finger_y, fw * 2, s(8))
        ell(big, color_hi, cx + fx - s(1), finger_y - s(1),
            fw * 2 - s(1), s(2))
        # Finger crease
        pygame.draw.line(big, color_lo,
                         (cx + fx, finger_y + s(2)),
                         (cx + fx, finger_y + s(4)),
                         max(1, s(1)))
    # Thumb on the outer side
    thumb_x = cx + side * s(r_w + 2)
    thumb_y = cy + s(2)
    ell(big, color_lo, thumb_x + s(1), thumb_y + s(1), s(6), s(10))
    ell(big, color, thumb_x, thumb_y, s(5), s(9))
    ell(big, color_hi, thumb_x - s(1), thumb_y - s(1), s(3), s(3))


def _wrist_cuff(big, center, w=11):
    """Gold wrist cuff — 3-layer with engraved band."""
    cx, cy = center
    aa_circle(big, P["GOLD_DK"], cx + s(1), cy + s(1), s(w + 1))
    aa_circle(big, P["GOLD_LO"], cx, cy, s(w))
    aa_circle(big, P["GOLD"], cx, cy, s(w - 1))
    aa_circle(big, P["GOLD_HI"], cx - s(3), cy - s(3), s(4))
    pygame.draw.circle(big, P["GOLD_DK"], (cx, cy), s(w - 1),
                       max(1, s(1)))


def _armband(big, anchor, perp, color=None, color_hi=None):
    """Small gold armband above the wrist cuff. `perp` is the unit
    vector perpendicular to the arm direction."""
    if color is None:
        color = P["GOLD"]
    if color_hi is None:
        color_hi = P["GOLD_HI"]
    ax, ay = anchor
    ab = pygame.Surface((s(20), s(10)), pygame.SRCALPHA)
    pygame.draw.ellipse(ab, P["GOLD_LO"], (0, 0, s(20), s(10)))
    pygame.draw.ellipse(ab, color, (s(1), s(1), s(18), s(8)))
    pygame.draw.line(ab, color_hi, (s(3), s(3)), (s(17), s(3)), s(1))
    ang = math.degrees(math.atan2(perp[1], perp[0]))
    ab_rot = pygame.transform.rotate(ab, -ang + 90)
    rect = ab_rot.get_rect(center=anchor)
    big.blit(ab_rot, rect.topleft)


# ─────────────────────────────────────────────────────────────────────────────
# Pose 1 — Folded forearms (relaxed cool)
# ─────────────────────────────────────────────────────────────────────────────

def draw_arms_1_folded(big, cx):
    """Forearms held HORIZONTAL across the upper chest. The right
    forearm sits on top of the left. Each hand rests visibly on the
    opposite bicep."""
    L = P
    chest_y = s(170)

    # Left arm (drawn first, will be partially behind the right)
    L_sh = (cx - s(54), s(140))          # left shoulder
    L_el = (cx - s(42), s(168))          # left elbow (drops + outward)
    L_wr = (cx + s(28), s(160))          # left wrist — across to RIGHT bicep
    # Bicep (shoulder → elbow)
    _segment(big, L_sh, L_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
             w=11)
    _joint(big, L_sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
    _joint(big, L_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
    # Forearm (elbow → wrist) — horizontal across the chest
    _segment(big, L_el, L_wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
             w=10)
    # Soft shadow under where the right forearm will lie
    shadow = pygame.Surface((s(70), s(22)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (*L["SKIN_DK"], 130),
                        (0, 0, s(70), s(22)))
    big.blit(shadow, (cx - s(35), s(167)))
    # Left hand resting on right bicep
    _wrist_cuff(big, L_wr, w=10)
    _fist(big, (L_wr[0] + s(4), L_wr[1] - s(2)),
          L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)

    # Right arm (drawn on top)
    R_sh = (cx + s(54), s(140))
    R_el = (cx + s(42), s(172))
    R_wr = (cx - s(28), s(178))          # right wrist — across to LEFT bicep
    _segment(big, R_sh, R_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
             w=11)
    _joint(big, R_sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
    _joint(big, R_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
    _segment(big, R_el, R_wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
             w=10)
    _wrist_cuff(big, R_wr, w=10)
    _fist(big, (R_wr[0] - s(4), R_wr[1] - s(2)),
          L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)


# ─────────────────────────────────────────────────────────────────────────────
# Pose 2 — Palms-up offering ("what's your wish?")
# ─────────────────────────────────────────────────────────────────────────────

def draw_arms_2_offering(big, cx):
    """Both arms bent at the elbow, forearms angled forward + outward
    with PALMS UP. The classic genie 'what's your wish?' gesture."""
    L = P
    for side in (-1, +1):
        # Shoulder is on the outer flank, elbow tucks closer to body
        # and slightly DOWN, hands flare outward + slightly forward.
        sh = (cx + side * s(54), s(140))
        el = (cx + side * s(34), s(186))
        wr = (cx + side * s(54), s(214))
        # Bicep
        _segment(big, sh, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=11)
        _joint(big, sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
        # Elbow
        _joint(big, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
        # Forearm extending out and slightly forward — palm up
        _segment(big, el, wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=10)
        # Gold wrist cuff
        _wrist_cuff(big, wr, w=11)
        # Open palm UP — palm just past the cuff, slightly above
        palm_x = wr[0] + side * s(4)
        palm_y = wr[1] - s(4)
        _open_palm(big, (palm_x, palm_y),
                   L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
                   r_w=10, r_h=8, side=side)
        # Sparkle above the palm to sell the "offering magic" read
        sparkle_y = palm_y - s(18)
        pygame.draw.line(big, P["GOLD_HI"],
                         (palm_x - s(4), sparkle_y),
                         (palm_x + s(4), sparkle_y), s(2))
        pygame.draw.line(big, P["GOLD_HI"],
                         (palm_x, sparkle_y - s(4)),
                         (palm_x, sparkle_y + s(4)), s(2))
        aa_circle(big, (255, 255, 230), palm_x, sparkle_y, s(2))


# ─────────────────────────────────────────────────────────────────────────────
# Pose 3 — Hands clasped at waist (butler / dignitary)
# ─────────────────────────────────────────────────────────────────────────────

def draw_arms_3_clasped(big, cx):
    """Both forearms angle down toward the centre of the belly.
    Hands meet above the sash with fingers interlaced."""
    L = P
    clasp_x = cx
    clasp_y = s(230)
    for side in (-1, +1):
        sh = (cx + side * s(54), s(140))
        el = (cx + side * s(46), s(186))
        wr = (cx + side * s(14), s(224))
        _segment(big, sh, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=11)
        _joint(big, sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
        _joint(big, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
        _segment(big, el, wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=10)
        _wrist_cuff(big, wr, w=10)
    # Clasped hands — single rounded shape in the middle
    aa_circle(big, L["SKIN_DK"], clasp_x + s(1), clasp_y + s(1), s(15))
    aa_circle(big, L["SKIN_LO"], clasp_x, clasp_y, s(14))
    aa_circle(big, L["SKIN"], clasp_x, clasp_y - s(1), s(13))
    aa_circle(big, L["SKIN_HI"], clasp_x - s(3), clasp_y - s(4), s(4))
    # Interlaced finger lines
    for fx in (-s(8), -s(3), s(2), s(7)):
        pygame.draw.line(big, L["SKIN_LO"],
                         (clasp_x + fx, clasp_y - s(8)),
                         (clasp_x + fx, clasp_y + s(8)),
                         max(2, s(1)))
    # Thumb ridges on each side
    for sx_off in (-s(12), s(12)):
        ell(big, L["SKIN_LO"], clasp_x + sx_off, clasp_y - s(2),
            s(5), s(9))
        ell(big, L["SKIN"], clasp_x + sx_off, clasp_y - s(2),
            s(4), s(7))


# ─────────────────────────────────────────────────────────────────────────────
# Pose 4 — Hand on heart + extended (Middle Eastern welcome)
# ─────────────────────────────────────────────────────────────────────────────

def draw_arms_4_heart_extended(big, cx):
    """Left hand pressed flat on chest over the heart; right arm
    extended forward + down with palm up."""
    L = P
    # LEFT arm — hand on heart
    L_sh = (cx - s(54), s(140))
    L_el = (cx - s(46), s(180))
    L_wr = (cx - s(10), s(174))       # wrist near the centre-chest
    _segment(big, L_sh, L_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=11)
    _joint(big, L_sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
    _joint(big, L_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
    _segment(big, L_el, L_wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=10)
    _wrist_cuff(big, L_wr, w=10)
    # Open palm pressed on chest — fingers splayed
    hand_x = L_wr[0] + s(6)
    hand_y = L_wr[1] - s(2)
    aa_circle(big, L["SKIN_DK"], hand_x + s(1), hand_y + s(1), s(13))
    aa_circle(big, L["SKIN_LO"], hand_x, hand_y, s(12))
    ell(big, L["SKIN"], hand_x, hand_y, s(22), s(20))
    ell(big, L["SKIN_HI"], hand_x - s(2), hand_y - s(3), s(10), s(4))
    # 4 finger ridges spreading upward
    for fx in (-s(8), -s(3), s(2), s(7)):
        ell(big, L["SKIN_LO"], hand_x + fx, hand_y - s(7), s(3), s(8))
        ell(big, L["SKIN"], hand_x + fx, hand_y - s(8), s(2), s(7))
    # Thumb sweeping inward
    ell(big, L["SKIN"], hand_x - s(11), hand_y, s(5), s(8))

    # RIGHT arm — extended forward and slightly down, palm up
    R_sh = (cx + s(54), s(140))
    R_el = (cx + s(58), s(180))
    R_wr = (cx + s(68), s(220))
    _segment(big, R_sh, R_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=11)
    _joint(big, R_sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
    _joint(big, R_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
    _segment(big, R_el, R_wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=10)
    _wrist_cuff(big, R_wr, w=11)
    palm_x = R_wr[0] + s(4)
    palm_y = R_wr[1] - s(4)
    _open_palm(big, (palm_x, palm_y),
               L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
               r_w=10, r_h=8, side=+1)


# ─────────────────────────────────────────────────────────────────────────────
# Pose 5 — Open arms wide (ta-da welcome)
# ─────────────────────────────────────────────────────────────────────────────

def draw_arms_5_open_wide(big, cx):
    """Both arms extended outward horizontally, slightly above the
    shoulder line. Palms facing forward + slightly up."""
    L = P
    for side in (-1, +1):
        sh = (cx + side * s(54), s(140))
        el = (cx + side * s(82), s(132))
        wr = (cx + side * s(110), s(120))
        _segment(big, sh, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=11)
        _joint(big, sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
        _joint(big, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
        _segment(big, el, wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=10)
        _wrist_cuff(big, wr, w=11)
        # Open palm facing forward
        palm_x = wr[0] + side * s(4)
        palm_y = wr[1] - s(2)
        _open_palm(big, (palm_x, palm_y),
                   L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
                   r_w=10, r_h=8, side=side)
        # Tiny sparkle near each open palm — sells the "ta-da"
        sparkle_x = palm_x + side * s(14)
        sparkle_y = palm_y - s(6)
        pygame.draw.line(big, P["GOLD_HI"],
                         (sparkle_x - s(3), sparkle_y),
                         (sparkle_x + s(3), sparkle_y), s(2))
        pygame.draw.line(big, P["GOLD_HI"],
                         (sparkle_x, sparkle_y - s(3)),
                         (sparkle_x, sparkle_y + s(3)), s(2))


# ─────────────────────────────────────────────────────────────────────────────
# Composer — render a full A1 figure with a swapped-in arm pose
# ─────────────────────────────────────────────────────────────────────────────

def render_figure_with_arms(arms_fn):
    big = pygame.Surface((PW, PH), pygame.SRCALPHA)
    big.fill(SKY)
    cx = PW // 2
    # Body z-order matches render_a1_refined.draw_a1_refined,
    # but with arms_fn substituted for draw_arms.
    draw_smoke_aura(big, cx, t=0.0)
    draw_pants(big, cx, t=0.0)
    draw_slippers(big, cx)
    draw_torso(big, cx)
    draw_neck(big, cx)
    head_cy = s(60)
    head_r = s(40)
    draw_head(big, cx, head_cy, head_r)
    draw_face(big, cx, head_cy)
    draw_earrings(big, cx, head_cy, head_r)
    draw_topknot_and_headband(big, cx, head_cy, head_r)
    draw_sash(big, cx)
    arms_fn(big, cx)
    return pygame.transform.smoothscale(big, (W, H))


POSES = [
    ("1 — Folded forearms",    draw_arms_1_folded),
    ("2 — Palms-up offering",  draw_arms_2_offering),
    ("3 — Hands clasped",      draw_arms_3_clasped),
    ("4 — Heart + extended",   draw_arms_4_heart_extended),
    ("5 — Open arms wide",     draw_arms_5_open_wide),
]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "v1"
    DW = W * DISPLAY_SCALE
    DH = H * DISPLAY_SCALE
    margin = 14
    label_h = 28
    sheet_w = DW * len(POSES) + margin * (len(POSES) + 1)
    sheet_h = DH + margin * 2 + label_h
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 22, 30))
    font = pygame.font.SysFont("Arial", 18, bold=True)
    for i, (label, fn) in enumerate(POSES):
        portrait = render_figure_with_arms(fn)
        disp = pygame.transform.smoothscale(portrait, (DW, DH))
        x = margin + i * (DW + margin)
        pygame.draw.rect(sheet, (60, 65, 80),
                         (x - 2, margin - 2, DW + 4, DH + 4), 2)
        sheet.blit(disp, (x, margin))
        text = font.render(label, True, (240, 240, 240))
        sheet.blit(text, (x + (DW - text.get_width()) // 2,
                          margin + DH + 6))
        # Individual portrait at display scale
        pygame.image.save(disp,
                          os.path.join(OUT_DIR,
                                       f"a1_arms_{i+1}_{tag}.png"))
    out = os.path.join(OUT_DIR, f"a1_arms_{tag}.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
