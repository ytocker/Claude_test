"""Render 5 palm-shine variants on the locked v4/v5 lotus body.

Each portrait shows the same A1 full-lotus genie with palms-up arms,
but swaps the shine style above each palm. Lets the user pick which
shine treatment to lock in before the in-game cinematic wiring.

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_a1_shine_variants [tag]
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
from tools.render_a1_arms_variants import (
    _segment, _joint, _open_palm, _wrist_cuff,
)
from tools.render_a1_crossed_legs_variants import (
    _smoke_aura_below, draw_crossed_legs_ankle_cross,  # variant 2 — locked
)

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie_designs")
os.makedirs(OUT_DIR, exist_ok=True)

DISPLAY_SCALE = 2


# ─────────────────────────────────────────────────────────────────────────────
# 5 shine designs. Each takes (big, palm_x, palm_y) and draws ONE shine
# above the palm at the given location.
# ─────────────────────────────────────────────────────────────────────────────

def shine_1_classic_pixie(big, px, py):
    """Classic Disney-pixie 4-point sparkle. Long thin gold arms with
    a sharp white-gold diamond centre. NO halo — crisp & graphic."""
    GOLD = (255, 220, 130)
    GOLD_LO = (200, 165, 70)
    WHITE = (255, 255, 245)
    # Long thin star arms
    for dx, dy in ((s(16), 0), (-s(16), 0),
                   (0, s(16)), (0, -s(16))):
        # Arm shape: wide near centre, thin at tip
        pygame.draw.polygon(big, GOLD_LO,
                            [(px, py),
                             (px + dx // 4 - dy // 8, py + dy // 4 + dx // 8),
                             (px + dx, py + dy),
                             (px + dx // 4 + dy // 8, py + dy // 4 - dx // 8)])
        pygame.draw.polygon(big, GOLD,
                            [(px, py),
                             (px + dx // 4 - dy // 12, py + dy // 4 + dx // 12),
                             (px + int(dx * 0.92), py + int(dy * 0.92)),
                             (px + dx // 4 + dy // 12, py + dy // 4 - dx // 12)])
    # Central white diamond (4-point inner shape)
    pygame.draw.polygon(big, WHITE,
                        [(px, py - s(7)), (px + s(7), py),
                         (px, py + s(7)), (px - s(7), py)])
    pygame.draw.polygon(big, GOLD,
                        [(px, py - s(4)), (px + s(4), py),
                         (px, py + s(4)), (px - s(4), py)])
    # Tiny accent dots at the arm tips
    for dx, dy in ((s(18), 0), (-s(18), 0),
                   (0, s(18)), (0, -s(18))):
        pygame.draw.circle(big, WHITE, (px + dx, py + dy), max(1, s(1)))


def shine_2_radial_burst(big, px, py):
    """8-ray radial burst — like a magical 'pop' going outward.
    Each ray is a thin triangle wedge fading from bright gold to
    translucent at the tip. Bright white core."""
    GOLD = (255, 225, 140)
    GOLD_HI = (255, 245, 200)
    WHITE = (255, 255, 250)
    n_rays = 8
    ray_len = s(20)
    base_w = s(4)
    for i in range(n_rays):
        ang = math.radians(i * (360 / n_rays))
        cx_o = math.cos(ang)
        cy_o = math.sin(ang)
        # Perpendicular for base width
        px_o = -cy_o
        py_o = cx_o
        # Wedge polygon: wide at base near centre, point at tip
        tip = (px + cx_o * ray_len, py + cy_o * ray_len)
        b_left = (px + px_o * base_w / 2, py + py_o * base_w / 2)
        b_right = (px - px_o * base_w / 2, py - py_o * base_w / 2)
        # Draw shadow wedge (slightly larger, darker)
        pygame.draw.polygon(big, GOLD,
                            [(int(b_left[0]), int(b_left[1])),
                             (int(tip[0]), int(tip[1])),
                             (int(b_right[0]), int(b_right[1]))])
        # Inner bright wedge
        tip2 = (px + cx_o * ray_len * 0.85,
                py + cy_o * ray_len * 0.85)
        pygame.draw.polygon(big, GOLD_HI,
                            [(int(b_left[0]), int(b_left[1])),
                             (int(tip2[0]), int(tip2[1])),
                             (int(b_right[0]), int(b_right[1]))])
    # Bright white core
    aa_circle(big, GOLD_HI, px, py, s(6))
    aa_circle(big, WHITE, px, py, s(4))
    aa_circle(big, (255, 255, 255), px - s(1), py - s(1), s(2))


def shine_3_orb_of_light(big, px, py):
    """Soft glowing orb — no star points, just a luminous sphere of
    magical energy with internal sparkles. Reads as 'contained
    magic' rather than 'bursting magic'."""
    CYAN = (160, 230, 255)
    CYAN_HI = (220, 245, 255)
    WHITE = (255, 255, 250)
    # Outer glow layers
    for r_n, alpha in ((22, 50), (16, 90), (12, 140)):
        srf = pygame.Surface((s(r_n) * 2 + 4, s(r_n) * 2 + 4),
                             pygame.SRCALPHA)
        pygame.draw.circle(srf, (*CYAN, alpha),
                           (s(r_n) + 2, s(r_n) + 2), s(r_n))
        big.blit(srf, (px - s(r_n) - 2, py - s(r_n) - 2))
    # Solid inner orb
    aa_circle(big, CYAN, px, py, s(9))
    aa_circle(big, CYAN_HI, px, py, s(7))
    aa_circle(big, WHITE, px - s(2), py - s(2), s(3))
    # Internal mini-sparkles ("stars inside the orb")
    for dx, dy in ((s(3), s(2)), (-s(3), -s(1)), (s(1), -s(4))):
        aa_circle(big, WHITE, px + dx, py + dy, max(1, s(1)))
    # Tiny outer satellite dot above the orb (highlight reflection)
    aa_circle(big, WHITE, px + s(2), py - s(6), max(1, s(1)))


def shine_4_twinkle_cluster(big, px, py):
    """Three twinkle stars in a cluster — main star + 2 smaller
    satellites. Asymmetric, feels like magical pixie dust rather
    than a single discrete spark."""
    GOLD = (255, 225, 140)
    GOLD_HI = (255, 245, 200)
    WHITE = (255, 255, 250)

    def _star(cx_s, cy_s, arm_len, arm_w):
        """Thin 4-point star centred at (cx_s, cy_s)."""
        for dx, dy in ((arm_len, 0), (-arm_len, 0),
                       (0, arm_len), (0, -arm_len)):
            pygame.draw.line(big, GOLD,
                             (cx_s, cy_s),
                             (cx_s + dx, cy_s + dy),
                             arm_w + s(1))
            pygame.draw.line(big, GOLD_HI,
                             (cx_s, cy_s),
                             (cx_s + dx, cy_s + dy),
                             arm_w)
        aa_circle(big, WHITE, cx_s, cy_s, max(1, arm_w // 2))

    # Main star — bigger, at the cluster centre
    _star(px, py, arm_len=s(11), arm_w=s(2))
    # Two smaller satellite stars at offsets
    _star(px + s(11), py - s(8), arm_len=s(6), arm_w=s(1))
    _star(px - s(10), py + s(7), arm_len=s(5), arm_w=s(1))
    # A 4th tiny dot for fullness
    aa_circle(big, WHITE, px + s(7), py + s(10), max(1, s(1)))


def shine_5_crystal_gem(big, px, py):
    """A faceted magical crystal hovering above the palm — tall
    diamond shape with internal gradient + a soft halo. Reads as
    'wish gem' — most thematic for a genie offering wishes."""
    CYAN = (160, 230, 255)
    CYAN_HI = (220, 245, 255)
    BLUE_DK = (40, 90, 150)
    BLUE_MID = (80, 150, 220)
    GOLD = (255, 225, 140)
    WHITE = (255, 255, 250)
    # Soft halo behind the gem
    for r_n, alpha in ((18, 70), (14, 110)):
        srf = pygame.Surface((s(r_n) * 2 + 4, s(r_n) * 2 + 4),
                             pygame.SRCALPHA)
        pygame.draw.circle(srf, (*CYAN, alpha),
                           (s(r_n) + 2, s(r_n) + 2), s(r_n))
        big.blit(srf, (px - s(r_n) - 2, py - s(r_n) - 2))
    # Crystal shape (tall diamond with faceted middle)
    top = (px, py - s(12))
    bot = (px, py + s(10))
    left = (px - s(7), py - s(1))
    right = (px + s(7), py - s(1))
    mid_left = (px - s(5), py + s(3))
    mid_right = (px + s(5), py + s(3))
    # Dark shadow side (right)
    pygame.draw.polygon(big, BLUE_DK,
                        [top, right, mid_right, bot])
    # Mid-tone fill (left bright side)
    pygame.draw.polygon(big, BLUE_MID,
                        [top, left, mid_left, bot])
    # Top-left highlight facet
    pygame.draw.polygon(big, CYAN_HI,
                        [top, left, (px - s(2), py - s(5))])
    # Centre bright stripe
    pygame.draw.line(big, WHITE,
                     (px - s(1), py - s(10)),
                     (px - s(1), py + s(8)),
                     max(2, s(1)))
    # Top vertex sparkle
    pygame.draw.line(big, GOLD,
                     (px - s(4), py - s(12)),
                     (px + s(4), py - s(12)),
                     s(2))
    aa_circle(big, WHITE, px, py - s(12), s(2))
    # Tiny satellite sparkles flanking the gem
    for sat_dx, sat_dy in ((s(12), -s(6)), (-s(11), s(2))):
        sxp = px + sat_dx
        syp = py + sat_dy
        pygame.draw.line(big, GOLD,
                         (sxp - s(3), syp), (sxp + s(3), syp),
                         max(1, s(1)))
        pygame.draw.line(big, GOLD,
                         (sxp, syp - s(3)), (sxp, syp + s(3)),
                         max(1, s(1)))
        aa_circle(big, WHITE, sxp, syp, max(1, s(1)))


# ─────────────────────────────────────────────────────────────────────────────
# Arms helper that takes a shine_fn so we don't duplicate the rest of
# the offering pose. (Copy of draw_arms_2_offering with the inline
# shine swapped for a callback.)
# ─────────────────────────────────────────────────────────────────────────────

def draw_offering_arms_with_shine(big, cx, shine_fn):
    L = P
    for side in (-1, +1):
        sh = (cx + side * s(54), s(140))
        el = (cx + side * s(34), s(186))
        wr = (cx + side * s(54), s(214))
        _segment(big, sh, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=11)
        _joint(big, sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
        _joint(big, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
        _segment(big, el, wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=10)
        _wrist_cuff(big, wr, w=11)
        palm_x = wr[0] + side * s(4)
        palm_y = wr[1] - s(4)
        _open_palm(big, (palm_x, palm_y),
                   L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
                   r_w=10, r_h=8, side=side)
        # Shine ABOVE the palm — caller provides the design
        shine_fn(big, palm_x, palm_y - s(28))


# ─────────────────────────────────────────────────────────────────────────────
# Composer + sheet
# ─────────────────────────────────────────────────────────────────────────────

def render_figure(shine_fn):
    big = pygame.Surface((PW, PH), pygame.SRCALPHA)
    big.fill(SKY)
    cx = PW // 2
    _smoke_aura_below(big, cx, s(330))
    # Locked v4/v5 lotus body (variant 2 from crossed_legs)
    draw_crossed_legs_ankle_cross(big, cx)
    draw_torso(big, cx)
    draw_neck(big, cx)
    head_cy = s(60)
    head_r = s(40)
    draw_head(big, cx, head_cy, head_r)
    draw_face(big, cx, head_cy)
    draw_earrings(big, cx, head_cy, head_r)
    draw_topknot_and_headband(big, cx, head_cy, head_r)
    draw_sash(big, cx)
    draw_offering_arms_with_shine(big, cx, shine_fn)
    return pygame.transform.smoothscale(big, (W, H))


SHINES = [
    ("1 — Classic pixie star",  shine_1_classic_pixie),
    ("2 — Radial burst",        shine_2_radial_burst),
    ("3 — Orb of light",        shine_3_orb_of_light),
    ("4 — Twinkle cluster",     shine_4_twinkle_cluster),
    ("5 — Crystal gem",         shine_5_crystal_gem),
]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "v1"
    DW = W * DISPLAY_SCALE
    DH = H * DISPLAY_SCALE
    margin = 14
    label_h = 28
    sheet_w = DW * len(SHINES) + margin * (len(SHINES) + 1)
    sheet_h = DH + margin * 2 + label_h
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 22, 30))
    font = pygame.font.SysFont("Arial", 18, bold=True)
    for i, (label, fn) in enumerate(SHINES):
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
                                       f"a1_shine_{i+1}_{tag}.png"))
    out = os.path.join(OUT_DIR, f"a1_shines_{tag}.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
