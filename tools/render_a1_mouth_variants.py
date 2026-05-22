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
# Round-1 mouth variants (kept for reference)
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
# Round-2 mouth variants — all "LARGE smile with teeth, NOT scary".
# User wants the v6 toothy-grin energy back but warmer + softer so it
# doesn't read as menacing.
# ─────────────────────────────────────────────────────────────────────────────

def _smile_arc_band(big, cx, mt_y, half_w, height, tooth_color=None):
    """Helper: stamp a tooth band that curves UPWARD at the corners
    so it reads as a smile, not a flat row of bars."""
    if tooth_color is None:
        tooth_color = P["WHITE"]
    # Build a curved polygon — top edge dips down in the middle,
    # bottom edge rises at the corners (smile curve).
    pts = [
        (cx - half_w, mt_y),                     # top-left
        (cx - half_w + sx(2), mt_y - sx(1)),
        (cx, mt_y - sx(1)),
        (cx + half_w - sx(2), mt_y - sx(1)),
        (cx + half_w, mt_y),                     # top-right
        (cx + half_w - sx(4), mt_y + height - sx(2)),  # bottom curves up
        (cx, mt_y + height),
        (cx - half_w + sx(4), mt_y + height - sx(2)),  # bottom curves up
    ]
    pygame.draw.polygon(big, tooth_color, pts)
    # Soft shadow line just under the top
    pygame.draw.line(big, (230, 230, 235),
                     (cx - half_w + sx(3), mt_y + sx(3)),
                     (cx + half_w - sx(3), mt_y + sx(3)),
                     max(1, sx(1)))


def mouth_6_big_curved_smile(big, cx, head_cy):
    """LARGE smile, single curved white tooth band, soft pink interior,
    NO separator lines between teeth. The most "friendly grin" form."""
    mt_y = head_cy + sx(15)
    # Outer dark-red lip ring (faint)
    pygame.draw.ellipse(big, P["LIP_DK"],
                        (cx - sx(20), mt_y - sx(3), sx(40), sx(22)))
    # Warm pink interior
    pygame.draw.ellipse(big, P["MOUTH_INT"],
                        (cx - sx(18), mt_y - sx(1), sx(36), sx(19)))
    # Big curved tooth band
    _smile_arc_band(big, cx, mt_y + sx(2), half_w=sx(16), height=sx(11))
    # Soft lower lip — large, slightly droopy
    ell(big, P["LIP"], cx, mt_y + sx(20), sx(28), sx(7))
    ell(big, P["LIP_HI"], cx, mt_y + sx(18), sx(20), sx(3))
    draw_goatee(big, cx, mt_y + sx(15))


def mouth_7_friendly_toothy_grin(big, cx, head_cy):
    """LARGE open grin, 6 individual teeth but SOFT light-grey
    separators (not black bars) and rounded tooth tops."""
    mt_y = head_cy + sx(14)
    # Outer mouth shape
    pygame.draw.ellipse(big, P["LIP_DK"],
                        (cx - sx(20), mt_y - sx(3), sx(40), sx(24)))
    pygame.draw.ellipse(big, P["MOUTH_INT"],
                        (cx - sx(18), mt_y - sx(1), sx(36), sx(21)))
    # Tooth band base — one big rounded shape
    tooth_top = mt_y + sx(2)
    tooth_bot = mt_y + sx(15)
    pygame.draw.polygon(big, P["WHITE"],
                        [(cx - sx(17), tooth_top),
                         (cx + sx(17), tooth_top),
                         (cx + sx(14), tooth_bot),
                         (cx - sx(14), tooth_bot)])
    # Round the top corners
    aa_circle(big, P["WHITE"], cx - sx(15), tooth_top + sx(2), sx(2))
    aa_circle(big, P["WHITE"], cx + sx(15), tooth_top + sx(2), sx(2))
    # Soft inner shadow line near the top
    pygame.draw.line(big, (235, 235, 240),
                     (cx - sx(16), tooth_top + sx(2)),
                     (cx + sx(16), tooth_top + sx(2)),
                     max(2, sx(1)))
    # 5 LIGHT-GREY soft separator lines (not black bars)
    for fx in (-sx(11), -sx(5), 0, sx(5), sx(11)):
        pygame.draw.line(big, (215, 220, 225),
                         (cx + fx, tooth_top + sx(3)),
                         (cx + fx, tooth_bot - sx(1)),
                         max(1, sx(1)))
    # Lower lip
    ell(big, P["LIP"], cx, mt_y + sx(20), sx(28), sx(6))
    ell(big, P["LIP_HI"], cx, mt_y + sx(18), sx(20), sx(2))
    draw_goatee(big, cx, mt_y + sx(14))


def mouth_8_laughing_with_tongue(big, cx, head_cy):
    """Wide open laughing grin — visible TOP + BOTTOM teeth, pink
    tongue between. Big toothy + busy but the warm interior tones
    down the scariness."""
    mt_y = head_cy + sx(13)
    # Outer + interior
    pygame.draw.ellipse(big, P["LIP_DK"],
                        (cx - sx(20), mt_y - sx(3), sx(40), sx(28)))
    pygame.draw.ellipse(big, P["MOUTH_INT"],
                        (cx - sx(18), mt_y - sx(1), sx(36), sx(25)))
    # Top teeth band (rounded, curved)
    _smile_arc_band(big, cx, mt_y + sx(1), half_w=sx(17), height=sx(9))
    # Light separators on top teeth
    for fx in (-sx(11), -sx(6), -sx(1), sx(4), sx(9)):
        pygame.draw.line(big, (220, 225, 230),
                         (cx + fx, mt_y + sx(2)),
                         (cx + fx, mt_y + sx(8)),
                         max(1, sx(1)))
    # Tongue (big visible pink bulge)
    ell(big, P["TONGUE"], cx, mt_y + sx(14), sx(24), sx(8))
    ell(big, P["TONGUE_HI"], cx, mt_y + sx(12), sx(18), sx(3))
    # Bottom teeth band (smaller, rounded)
    pygame.draw.polygon(big, P["WHITE"],
                        [(cx - sx(13), mt_y + sx(18)),
                         (cx + sx(13), mt_y + sx(18)),
                         (cx + sx(11), mt_y + sx(22)),
                         (cx - sx(11), mt_y + sx(22))])
    for fx in (-sx(8), -sx(3), sx(2), sx(7)):
        pygame.draw.line(big, (220, 225, 230),
                         (cx + fx, mt_y + sx(19)),
                         (cx + fx, mt_y + sx(22)),
                         max(1, sx(1)))
    # Lower lip
    ell(big, P["LIP"], cx, mt_y + sx(26), sx(28), sx(5))
    draw_goatee(big, cx, mt_y + sx(20))


def mouth_9_chiclet_smile(big, cx, head_cy):
    """Cartoony big-tooth smile — 6 LARGE rounded square teeth like
    Disney/cartoon characters. Each tooth is a separate rounded
    rectangle with its own highlight, NO black-bar separators
    between them — gaps are the pink mouth interior peeking through."""
    mt_y = head_cy + sx(13)
    # Outer mouth + warm interior
    pygame.draw.ellipse(big, P["LIP_DK"],
                        (cx - sx(22), mt_y - sx(3), sx(44), sx(24)))
    pygame.draw.ellipse(big, P["MOUTH_INT"],
                        (cx - sx(20), mt_y - sx(1), sx(40), sx(21)))
    # Pink gum line under teeth (subtle, lighter pink)
    pygame.draw.ellipse(big, (235, 165, 175),
                        (cx - sx(18), mt_y + sx(1), sx(36), sx(5)))
    # 6 chiclet teeth, each a rounded rectangle
    tooth_w = sx(6)
    tooth_h = sx(12)
    tooth_y = mt_y + sx(4)
    gap = sx(1)
    start_x = cx - sx(20)
    for i in range(6):
        tx = start_x + i * (tooth_w + gap) + sx(1)
        # Rounded tooth — base white rect + circles at top corners
        pygame.draw.rect(big, P["WHITE"],
                         (tx, tooth_y + sx(1), tooth_w, tooth_h))
        aa_circle(big, P["WHITE"], tx, tooth_y + sx(2), tooth_w // 2)
        aa_circle(big, P["WHITE"], tx + tooth_w, tooth_y + sx(2),
                  tooth_w // 2)
        # Subtle highlight on upper-left of each tooth
        aa_circle(big, (255, 255, 255), tx + tooth_w // 3,
                  tooth_y + sx(3), max(1, sx(1)))
        # Soft shadow stripe at bottom
        pygame.draw.line(big, (220, 225, 230),
                         (tx, tooth_y + tooth_h - sx(1)),
                         (tx + tooth_w, tooth_y + tooth_h - sx(1)),
                         max(1, sx(1)))
    # Lower lip
    ell(big, P["LIP"], cx, mt_y + sx(20), sx(30), sx(6))
    ell(big, P["LIP_HI"], cx, mt_y + sx(18), sx(22), sx(2))
    draw_goatee(big, cx, mt_y + sx(15))


def mouth_10_dazzling_smile(big, cx, head_cy):
    """Bright big smile with SPARKLE highlights — large curved tooth
    band plus 2 small star sparkles on the teeth (like the
    cartoony 'ding!' shine). Friendly + magical."""
    mt_y = head_cy + sx(14)
    # Outer + interior
    pygame.draw.ellipse(big, P["LIP_DK"],
                        (cx - sx(21), mt_y - sx(3), sx(42), sx(23)))
    pygame.draw.ellipse(big, P["MOUTH_INT"],
                        (cx - sx(19), mt_y - sx(1), sx(38), sx(20)))
    # Big curved tooth band
    _smile_arc_band(big, cx, mt_y + sx(2), half_w=sx(17), height=sx(11))
    # Highlight band along the top
    pygame.draw.line(big, (255, 255, 255),
                     (cx - sx(14), mt_y + sx(4)),
                     (cx + sx(14), mt_y + sx(4)),
                     max(2, sx(1)))
    # Two sparkle stars on the teeth
    for star_x in (cx - sx(8), cx + sx(7)):
        star_y = mt_y + sx(6)
        # Cross + dot
        pygame.draw.line(big, (255, 255, 255),
                         (star_x - sx(3), star_y),
                         (star_x + sx(3), star_y), max(2, sx(1)))
        pygame.draw.line(big, (255, 255, 255),
                         (star_x, star_y - sx(3)),
                         (star_x, star_y + sx(3)), max(2, sx(1)))
        aa_circle(big, (255, 255, 200), star_x, star_y, max(1, sx(1)))
    # 3 very subtle separator dots between groups (not lines)
    for fx in (-sx(6), 0, sx(6)):
        aa_circle(big, (230, 230, 235), cx + fx, mt_y + sx(10),
                  max(1, sx(1)) - 1 if sx(1) > 1 else 1)
    # Lower lip
    ell(big, P["LIP"], cx, mt_y + sx(20), sx(28), sx(6))
    ell(big, P["LIP_HI"], cx, mt_y + sx(18), sx(20), sx(2))
    draw_goatee(big, cx, mt_y + sx(15))


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
    # Round 2 — all "big toothy smile, NOT scary". Round 1
    # alternatives are still defined above for reference.
    MOUTHS = [
        ("6 — Big curved smile",     mouth_6_big_curved_smile),
        ("7 — Friendly toothy grin", mouth_7_friendly_toothy_grin),
        ("8 — Laughing + tongue",    mouth_8_laughing_with_tongue),
        ("9 — Chiclet smile",        mouth_9_chiclet_smile),
        ("10 — Dazzling sparkle",    mouth_10_dazzling_smile),
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
