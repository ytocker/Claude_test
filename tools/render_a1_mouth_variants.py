"""Render 5 mouth-variant heads for the refined A1 (Classic Aladdin).

Keeps the v6 head/brow/eyes/mustache/headband/earrings/topknot and
swaps only the mouth treatment. Saves five labelled head closeups
to docs/screenshots/genie_designs/a1_mouths_{tag}.png.

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_a1_mouth_variants [tag]
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

# Per-head canvas: tight head-only crop so the face fills the frame.
W, H, SS = 180, 230, 6
PW, PH = W * SS, H * SS
SKY = (110, 175, 220)
# Each individual portrait + sheet is saved at this output scale so
# mouth detail is readable.
DISPLAY_SCALE = 3


P = dict(
    SKIN     = ( 70, 175, 220),
    SKIN_HI  = (175, 230, 252),
    SKIN_MID = (110, 200, 235),
    SKIN_LO  = ( 25, 110, 170),
    SKIN_DK  = ( 12,  70, 120),
    GOLD     = (245, 205, 105),
    GOLD_HI  = (255, 240, 175),
    GOLD_MID = (220, 175,  70),
    GOLD_LO  = (160, 115,  30),
    GOLD_DK  = (110,  75,  15),
    RUBY     = (220,  60,  80),
    RUBY_HI  = (255, 175, 195),
    WHITE    = (250, 250, 245),
    HAIR     = ( 28,  22,  20),
    HAIR_HI  = ( 75,  55,  45),
    BLACK    = ( 18,  14,  10),
    # New: warm pink/red for friendly mouth interiors and tongues.
    LIP      = (190,  85, 100),
    LIP_DK   = (135,  50,  65),
    LIP_HI   = (245, 165, 180),
    MOUTH_INT= (160,  60,  80),    # warm interior (vs. v6's near-black)
    TONGUE   = (220,  95, 115),
    TONGUE_HI= (255, 175, 195),
)


def sx(v):
    return int(v * SS)


def aa_circle(surf, color, cx, cy, r):
    pygame.draw.circle(surf, color, (int(cx), int(cy)), int(r))


def ell(surf, color, cx, cy, w, h):
    pygame.draw.ellipse(surf, color,
                        (int(cx - w / 2), int(cy - h / 2),
                         int(w), int(h)))


def gem_facet(surf, cx, cy, r, color, hi_color, lo_color):
    pts_full = [(cx, cy - r), (cx + r, cy),
                (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(surf, lo_color, pts_full)
    inner = int(r * 0.85)
    pygame.draw.polygon(surf, color,
                        [(cx, cy - inner), (cx + inner, cy),
                         (cx, cy + inner), (cx - inner, cy)])
    pygame.draw.polygon(surf, hi_color,
                        [(cx, cy - inner),
                         (cx - int(inner * 0.55), cy),
                         (cx - int(inner * 0.3), cy - int(inner * 0.3))])
    pygame.draw.circle(surf, (255, 255, 255),
                       (int(cx - inner * 0.3), int(cy - inner * 0.5)),
                       max(1, int(r * 0.12)))


# ─────────────────────────────────────────────────────────────────────────────
# Head + face (everything EXCEPT the mouth)
# ─────────────────────────────────────────────────────────────────────────────

def draw_head_base(big, cx, head_cy, head_r):
    aa_circle(big, P["SKIN_DK"], cx + sx(3), head_cy + sx(3), head_r + sx(1))
    aa_circle(big, P["SKIN_LO"], cx, head_cy, head_r)
    aa_circle(big, P["SKIN"], cx, head_cy - sx(1), head_r - sx(2))
    aa_circle(big, P["SKIN_HI"], cx - head_r // 3, head_cy - head_r // 3,
              head_r // 3)
    # Cheek glow
    for offset, alpha in (((sx(4), sx(6)), 80), ((-sx(24), sx(6)), 60)):
        c = pygame.Surface((sx(20), sx(14)), pygame.SRCALPHA)
        pygame.draw.ellipse(c, (255, 180, 200, alpha),
                            (0, 0, sx(20), sx(14)))
        big.blit(c, (cx + offset[0], head_cy + offset[1]))
    # Chin shadow
    pygame.draw.arc(big, P["SKIN_LO"],
                    (cx - head_r + sx(4), head_cy + sx(4),
                     2 * head_r - sx(8), head_r),
                    math.radians(200), math.radians(340), sx(2))
    # Nose
    pygame.draw.polygon(big, P["SKIN_LO"],
                        [(cx, head_cy - sx(2)),
                         (cx + sx(3), head_cy + sx(6)),
                         (cx, head_cy + sx(8)),
                         (cx - sx(3), head_cy + sx(6))])
    pygame.draw.polygon(big, P["SKIN_HI"],
                        [(cx - sx(1), head_cy - sx(1)),
                         (cx, head_cy + sx(2)),
                         (cx - sx(2), head_cy + sx(3))])
    pygame.draw.circle(big, P["SKIN_DK"],
                       (cx - sx(2), head_cy + sx(6)), max(1, sx(1)))
    pygame.draw.circle(big, P["SKIN_DK"],
                       (cx + sx(2), head_cy + sx(6)), max(1, sx(1)))


def draw_topknot_and_headband(big, cx, head_cy, head_r):
    tuft_pts = [
        (cx - head_r + sx(4), head_cy - sx(16)),
        (cx - sx(8), head_cy - sx(20)),
        (cx + sx(8), head_cy - sx(20)),
        (cx + head_r - sx(4), head_cy - sx(16)),
        (cx + sx(14), head_cy - sx(11)),
        (cx, head_cy - sx(8)),
        (cx - sx(14), head_cy - sx(11)),
    ]
    pygame.draw.polygon(big, P["HAIR"], tuft_pts)
    tk_cx, tk_cy = cx, head_cy - head_r - sx(4)
    pygame.draw.rect(big, P["GOLD"],
                     (tk_cx - sx(8), tk_cy + sx(6), sx(16), sx(4)))
    aa_circle(big, P["BLACK"], tk_cx + sx(1), tk_cy + sx(1), sx(14))
    aa_circle(big, P["HAIR"], tk_cx, tk_cy, sx(13))
    aa_circle(big, P["HAIR_HI"], tk_cx - sx(3), tk_cy - sx(3), sx(4))

    band_y = head_cy - sx(18)
    pygame.draw.rect(big, P["GOLD_DK"],
                     (cx - sx(38), band_y - sx(2), sx(76), sx(11)))
    pygame.draw.rect(big, P["GOLD_LO"],
                     (cx - sx(38), band_y - sx(1), sx(76), sx(9)))
    pygame.draw.rect(big, P["GOLD"],
                     (cx - sx(36), band_y, sx(72), sx(7)))
    pygame.draw.line(big, P["GOLD_HI"],
                     (cx - sx(34), band_y + sx(2)),
                     (cx + sx(34), band_y + sx(2)), max(1, sx(1)))
    for fx in (-sx(30), -sx(20), -sx(10), sx(10), sx(20), sx(30)):
        pygame.draw.line(big, P["GOLD_DK"],
                         (cx + fx, band_y + sx(1)),
                         (cx + fx, band_y + sx(6)),
                         max(1, sx(1)))
    gem_facet(big, cx, band_y + sx(3), sx(8),
              P["RUBY"], P["RUBY_HI"], (110, 30, 40))
    for spd in (-sx(12), sx(12)):
        pygame.draw.polygon(big, P["GOLD"],
                            [(cx + spd - sx(2), band_y - sx(2)),
                             (cx + spd, band_y - sx(6)),
                             (cx + spd + sx(2), band_y - sx(2))])


def draw_earrings(big, cx, head_cy, head_r):
    for sdx in (-head_r - sx(2), head_r + sx(2)):
        ex = cx + sdx
        ey = head_cy + sx(4)
        pygame.draw.circle(big, P["GOLD_DK"], (ex, ey), sx(8), sx(2))
        pygame.draw.circle(big, P["GOLD"], (ex, ey), sx(7), sx(2))
        pygame.draw.circle(big, P["GOLD_HI"], (ex - sx(2), ey - sx(2)),
                           max(1, sx(1)))
        py = ey + sx(10)
        pygame.draw.line(big, P["GOLD"], (ex, ey + sx(3)),
                         (ex, py - sx(2)), max(1, sx(1)))
        gem_facet(big, ex, py, sx(3), P["RUBY"], P["RUBY_HI"], (110, 30, 40))


def draw_eyes_and_brows(big, cx, head_cy):
    pygame.draw.polygon(big, P["HAIR"],
                        [(cx - sx(20), head_cy - sx(6)),
                         (cx - sx(5), head_cy - sx(9)),
                         (cx - sx(5), head_cy - sx(4)),
                         (cx - sx(20), head_cy - sx(2))])
    pygame.draw.polygon(big, P["HAIR"],
                        [(cx + sx(20), head_cy - sx(6)),
                         (cx + sx(5), head_cy - sx(9)),
                         (cx + sx(5), head_cy - sx(4)),
                         (cx + sx(20), head_cy - sx(2))])
    for sdx in (-sx(12), sx(12)):
        pygame.draw.ellipse(big, P["WHITE"],
                            (cx + sdx - sx(8), head_cy - sx(4),
                             sx(16), sx(12)))
        aa_circle(big, P["HAIR"], cx + sdx, head_cy + sx(1), sx(5))
        aa_circle(big, P["BLACK"], cx + sdx, head_cy + sx(1), sx(3))
        aa_circle(big, P["WHITE"], cx + sdx - sx(2), head_cy - sx(1), sx(2))
        aa_circle(big, P["WHITE"], cx + sdx + sx(2), head_cy + sx(3),
                  max(1, sx(1)))
        pygame.draw.line(big, P["HAIR"],
                         (cx + sdx - sx(8), head_cy - sx(4)),
                         (cx + sdx + sx(8), head_cy - sx(4)),
                         max(1, sx(1)))


def draw_mustache(big, cx, head_cy):
    pygame.draw.arc(big, P["HAIR"],
                    (cx - sx(20), head_cy + sx(10),
                     sx(20), sx(10)),
                    math.radians(195), math.radians(360), sx(3))
    pygame.draw.arc(big, P["HAIR"],
                    (cx, head_cy + sx(10),
                     sx(20), sx(10)),
                    math.radians(180), math.radians(345), sx(3))
    for sxc in (-sx(20), sx(20)):
        aa_circle(big, P["HAIR"], cx + sxc, head_cy + sx(13), sx(3))
        aa_circle(big, P["HAIR_HI"], cx + sxc - sx(1), head_cy + sx(12),
                  max(1, sx(1)))


def draw_goatee(big, cx, mt_y, extra_offset=0):
    """Goatee drawn below the mouth. `mt_y` is the mouth y, offset
    lets variants shift the goatee down if their mouth is taller."""
    top_y = mt_y + sx(8 + extra_offset)
    pygame.draw.polygon(big, P["HAIR"],
                        [(cx - sx(8), top_y),
                         (cx + sx(8), top_y),
                         (cx + sx(4), top_y + sx(12)),
                         (cx - sx(4), top_y + sx(12))])
    pygame.draw.line(big, P["HAIR_HI"],
                     (cx - sx(2), top_y + sx(2)),
                     (cx - sx(1), top_y + sx(10)),
                     max(1, sx(1)))


# ─────────────────────────────────────────────────────────────────────────────
# Five mouth variants
# ─────────────────────────────────────────────────────────────────────────────

def mouth_1_closed_smile(big, cx, head_cy):
    """Closed warm smile — no teeth, just curve + defined lower lip.
    Friendliest, least busy."""
    mt_y = head_cy + sx(20)
    # Upper lip curve (subtle smile arc)
    pygame.draw.arc(big, P["LIP_DK"],
                    (cx - sx(14), mt_y - sx(2), sx(28), sx(10)),
                    math.radians(190), math.radians(350), max(3, sx(2)))
    # Lower lip (slight ellipse beneath)
    ell(big, P["LIP"], cx, mt_y + sx(6), sx(22), sx(6))
    ell(big, P["LIP_HI"], cx, mt_y + sx(5), sx(18), sx(2))
    # Smile crease ends
    aa_circle(big, P["LIP_DK"], cx - sx(13), mt_y + sx(4), max(1, sx(1)))
    aa_circle(big, P["LIP_DK"], cx + sx(13), mt_y + sx(4), max(1, sx(1)))
    draw_goatee(big, cx, mt_y + sx(4))


def mouth_2_soft_open(big, cx, head_cy):
    """Slightly open with one rounded white tooth band — interior is
    warm pink (not black), no vertical bars."""
    mt_y = head_cy + sx(18)
    # Mouth opening (warm interior)
    pygame.draw.ellipse(big, P["LIP_DK"],
                        (cx - sx(14), mt_y - sx(2), sx(28), sx(14)))
    pygame.draw.ellipse(big, P["MOUTH_INT"],
                        (cx - sx(12), mt_y, sx(24), sx(11)))
    # Single rounded white tooth band on top (no separations)
    pygame.draw.ellipse(big, P["WHITE"],
                        (cx - sx(11), mt_y + sx(1), sx(22), sx(6)))
    pygame.draw.ellipse(big, (235, 235, 240),
                        (cx - sx(11), mt_y + sx(4), sx(22), sx(3)))
    # Soft lower lip
    ell(big, P["LIP"], cx, mt_y + sx(13), sx(20), sx(5))
    ell(big, P["LIP_HI"], cx, mt_y + sx(12), sx(14), sx(2))
    draw_goatee(big, cx, mt_y + sx(8))


def mouth_3_hearty_laugh(big, cx, head_cy):
    """Open laughing mouth — top teeth as rounded band, pink tongue
    visible at the bottom, warm interior (no creepy darkness)."""
    mt_y = head_cy + sx(17)
    # Outer mouth shape (wider, rounded)
    pygame.draw.ellipse(big, P["LIP_DK"],
                        (cx - sx(15), mt_y - sx(2), sx(30), sx(18)))
    # Interior warm red
    pygame.draw.ellipse(big, P["MOUTH_INT"],
                        (cx - sx(13), mt_y, sx(26), sx(15)))
    # Top teeth — single rounded band, gently curved
    pygame.draw.ellipse(big, P["WHITE"],
                        (cx - sx(12), mt_y + sx(1), sx(24), sx(7)))
    pygame.draw.ellipse(big, (235, 235, 240),
                        (cx - sx(12), mt_y + sx(5), sx(24), sx(3)))
    # Just 4 soft tooth separations (not bars — small dimples)
    for fx in (-sx(7), -sx(2), sx(3), sx(8)):
        pygame.draw.line(big, (210, 215, 220),
                         (cx + fx, mt_y + sx(3)),
                         (cx + fx, mt_y + sx(6)),
                         max(1, sx(1)) - 1 if sx(1) > 1 else 1)
    # Tongue
    pygame.draw.ellipse(big, P["TONGUE"],
                        (cx - sx(8), mt_y + sx(8), sx(16), sx(7)))
    pygame.draw.ellipse(big, P["TONGUE_HI"],
                        (cx - sx(6), mt_y + sx(8), sx(12), sx(3)))
    # Lower lip
    ell(big, P["LIP"], cx, mt_y + sx(17), sx(22), sx(5))
    ell(big, P["LIP_HI"], cx, mt_y + sx(16), sx(16), sx(2))
    draw_goatee(big, cx, mt_y + sx(11))


def mouth_4_cheshire_smirk(big, cx, head_cy):
    """Asymmetric half-smile — left corner up, right corner neutral,
    single tooth peeking. Charming/roguish vs. creepy."""
    mt_y = head_cy + sx(20)
    # Curved smirk line (asymmetric arc)
    smirk_pts = [
        (cx - sx(14), mt_y + sx(2)),
        (cx - sx(6), mt_y - sx(2)),
        (cx + sx(2), mt_y + sx(2)),
        (cx + sx(10), mt_y + sx(6)),
        (cx + sx(14), mt_y + sx(8)),
    ]
    pygame.draw.lines(big, P["LIP_DK"], False, smirk_pts, max(3, sx(2)))
    # Single peeking tooth on the raised (left) side
    pygame.draw.polygon(big, P["WHITE"],
                        [(cx - sx(7), mt_y),
                         (cx - sx(3), mt_y),
                         (cx - sx(5), mt_y + sx(4))])
    # Soft lower lip following the smirk
    pygame.draw.lines(big, P["LIP"],
                      False,
                      [(cx - sx(13), mt_y + sx(4)),
                       (cx - sx(2), mt_y + sx(6)),
                       (cx + sx(8), mt_y + sx(10)),
                       (cx + sx(14), mt_y + sx(11))],
                      max(3, sx(2)))
    # Dimple on the raised side
    aa_circle(big, P["SKIN_LO"], cx - sx(18), mt_y + sx(2), max(1, sx(1)))
    draw_goatee(big, cx, mt_y + sx(4))


def mouth_5_open_with_tongue(big, cx, head_cy):
    """Open friendly grin — top teeth as one rounded white band,
    bottom row also visible as a thin band, prominent tongue between.
    Warm pink interior."""
    mt_y = head_cy + sx(18)
    # Outer mouth shape
    pygame.draw.ellipse(big, P["LIP_DK"],
                        (cx - sx(14), mt_y - sx(2), sx(28), sx(16)))
    pygame.draw.ellipse(big, P["MOUTH_INT"],
                        (cx - sx(12), mt_y, sx(24), sx(13)))
    # Top teeth band
    pygame.draw.ellipse(big, P["WHITE"],
                        (cx - sx(11), mt_y + sx(1), sx(22), sx(5)))
    pygame.draw.ellipse(big, (235, 235, 240),
                        (cx - sx(11), mt_y + sx(4), sx(22), sx(2)))
    # Bottom teeth band (thinner)
    pygame.draw.ellipse(big, P["WHITE"],
                        (cx - sx(9), mt_y + sx(9), sx(18), sx(3)))
    pygame.draw.ellipse(big, (220, 220, 225),
                        (cx - sx(9), mt_y + sx(11), sx(18), max(1, sx(1))))
    # Tongue between top and bottom
    pygame.draw.ellipse(big, P["TONGUE"],
                        (cx - sx(7), mt_y + sx(6), sx(14), sx(4)))
    pygame.draw.ellipse(big, P["TONGUE_HI"],
                        (cx - sx(5), mt_y + sx(6), sx(10), sx(2)))
    # Soft lower lip
    ell(big, P["LIP"], cx, mt_y + sx(15), sx(20), sx(4))
    ell(big, P["LIP_HI"], cx, mt_y + sx(14), sx(14), sx(2))
    draw_goatee(big, cx, mt_y + sx(9))


# ─────────────────────────────────────────────────────────────────────────────
# Composer
# ─────────────────────────────────────────────────────────────────────────────

def render_head_with_mouth(mouth_fn):
    big = pygame.Surface((PW, PH), pygame.SRCALPHA)
    big.fill(SKY)
    cx = PW // 2
    # Head centred lower with a generous radius for tight cropping.
    head_cy = sx(110)
    head_r = sx(60)

    draw_head_base(big, cx, head_cy, head_r)
    draw_eyes_and_brows(big, cx, head_cy)
    mouth_fn(big, cx, head_cy)
    # Mustache drawn AFTER mouth so its curl loops don't cover the
    # mouth — they sit alongside it.
    draw_mustache(big, cx, head_cy)
    draw_earrings(big, cx, head_cy, head_r)
    draw_topknot_and_headband(big, cx, head_cy, head_r)

    return pygame.transform.smoothscale(big, (W, H))


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "v1"
    MOUTHS = [
        ("1 — Closed warm smile",   mouth_1_closed_smile),
        ("2 — Soft open + 1 band",  mouth_2_soft_open),
        ("3 — Hearty laugh + tongue", mouth_3_hearty_laugh),
        ("4 — Cheshire smirk",      mouth_4_cheshire_smirk),
        ("5 — Open grin + tongue",  mouth_5_open_with_tongue),
    ]
    DW = W * DISPLAY_SCALE
    DH = H * DISPLAY_SCALE
    margin = 14
    label_h = 28
    sheet_w = DW * len(MOUTHS) + margin * (len(MOUTHS) + 1)
    sheet_h = DH + margin * 2 + label_h
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 22, 30))
    font = pygame.font.SysFont("Arial", 18, bold=True)
    for i, (label, fn) in enumerate(MOUTHS):
        portrait = render_head_with_mouth(fn)
        # Upscale for sheet display.
        portrait_disp = pygame.transform.smoothscale(portrait, (DW, DH))
        x = margin + i * (DW + margin)
        pygame.draw.rect(sheet, (60, 65, 80),
                         (x - 2, margin - 2, DW + 4, DH + 4), 2)
        sheet.blit(portrait_disp, (x, margin))
        text = font.render(label, True, (240, 240, 240))
        sheet.blit(text, (x + (DW - text.get_width()) // 2,
                          margin + DH + 6))
        # Individual portrait — also at display scale.
        pygame.image.save(portrait_disp,
                          os.path.join(OUT_DIR,
                                       f"a1_mouth_{i+1}_{tag}.png"))
    out = os.path.join(OUT_DIR, f"a1_mouths_{tag}.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
