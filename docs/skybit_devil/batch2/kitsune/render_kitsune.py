"""
Kitsune — the nine-tailed fox-spirit shrine devil  [COOL GLOW: MINT-GREEN FOXFIRE]

Review-sheet renderer (headless). Draws the ONE locked concept from
batch2/brainstorm_locked15.md: a small white fox face with a sharp snout
and tall pointed ears over a slim shrine-priestess haori body, fronted by a
WIDE peacock-like FAN of nine bushy coral-tipped tails (the dominant read),
with a tiny MINT-GREEN foxfire orb hovering by one ear — plus its torii-gate
prop mirrored into a repeatable vermilion shrine-pillar; all at large + 32px.

House grammar followed verbatim: chibi proportions, FLAT saturated fills +
hard ink keylines, form via the dark-core -> flat-fill -> top-left rim-sheen
TRIAD, silhouette POP via a 1px outline grown from the alpha mask,
supersampled then smoothscaled down. PINNED PALETTE hexes are used exactly so
the foxfire stays MINT-GREEN — distinct from Yurei's blue-cyan hitodama.
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# ── PINNED PALETTE (verbatim from the locked brief) ──────────────────────────
FUR        = (240, 236, 232)   # snow-white fur base
FUR_SH     = (180, 176, 178)   # cool-grey shade (dark-core)
CORAL      = (238, 120,  72)   # coral-orange ear/tip accent
VERMILION  = (202,  72,  56)   # vermilion torii
MINT       = (150, 224, 196)   # MINT-GREEN foxfire glow (the cool glow)
GOLD       = (224, 186,  84)   # gold haori-trim
INK        = ( 28,  24,  26)   # keyline
SHEEN      = (255, 250, 248)   # top-left rim-sheen

# derived working tones (kept inside the pinned families)
CORAL_SH   = (186,  78,  44)
CORAL_HI   = (250, 168, 120)
VERM_SH    = (150,  46,  38)
VERM_HI    = (228, 112,  92)
GOLD_HI    = (248, 222, 150)
MINT_CORE  = (224, 252, 240)   # near-white foxfire heart
MINT_DEEP  = ( 96, 186, 158)
NOSE       = ( 64,  52,  56)   # dark snout-tip / inner-mouth
HAORI_SH   = (162, 158, 162)

SS = 4   # supersample factor


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def grow_outline(src, color=INK, grow=1):
    """1px (post-downscale) ink keyline grown from the alpha mask, the way
    the house silhouette-POP works. Grown at supersample scale so the
    smoothscale carries it down to a crisp 1px."""
    g = grow * SS
    mask = pygame.mask.from_surface(src)
    out_surf = mask.to_surface(setcolor=(*color, 255), unsetcolor=(0, 0, 0, 0))
    w, h = src.get_size()
    canvas = pygame.Surface((w + 2 * g, h + 2 * g), pygame.SRCALPHA)
    for dx in range(-g, g + 1):
        for dy in range(-g, g + 1):
            if dx * dx + dy * dy <= g * g:
                canvas.blit(out_surf, (g + dx, g + dy))
    canvas.blit(src, (g, g))
    return canvas, g


def radial_glow(radius, color, alpha_center=200, falloff=2.0):
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        pygame.draw.circle(s, (*color, max(0, min(255, a))), (c, c), r)
    return s


def smoothdown(surf, target_h):
    ow, oh = surf.get_size()
    scale = target_h / oh
    return pygame.transform.smoothscale(
        surf, (max(1, int(ow * scale)), max(1, int(oh * scale))))


def _foxfire(surf, ocx, ocy, orr):
    """A small MINT-GREEN foxfire flame-orb: a teardrop wisp + glow halo.
    Drawn warm-mint so it never reads as Yurei's bluer hitodama."""
    glow = radial_glow(orr + 9 * SS, MINT, alpha_center=165, falloff=2.2)
    surf.blit(glow, (ocx - glow.get_width() // 2, ocy - glow.get_height() // 2),
              special_flags=pygame.BLEND_ADD)
    # teardrop flame body (tapered tail pointing up) — hard triad lobes
    flame = [
        (ocx, ocy - int(orr * 2.0)), (ocx + int(orr * 0.8), ocy - int(orr * 0.4)),
        (ocx + int(orr * 0.9), ocy + int(orr * 0.5)),
        (ocx, ocy + orr), (ocx - int(orr * 0.9), ocy + int(orr * 0.5)),
        (ocx - int(orr * 0.8), ocy - int(orr * 0.4)),
    ]
    pygame.draw.polygon(surf, MINT_DEEP, [(x + SS, y + SS) for (x, y) in flame])
    pygame.draw.polygon(surf, MINT, flame)
    pygame.draw.circle(surf, MINT_CORE, (ocx - orr // 4, ocy), int(orr * 0.55))
    pygame.draw.circle(surf, SHEEN, (ocx - orr // 3, ocy - orr // 4), int(orr * 0.22))


# ─────────────────────────────────────────────────────────────────────────────
#  THE CREATURE — built large (supersampled), then outlined + downscaled.
#  Wide read: the nine-tail FAN spreads behind the small fox like a peacock.
# ─────────────────────────────────────────────────────────────────────────────

def build_kitsune(target_h=200):
    U = SS
    W, H = 300 * U, 250 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2
    # nudge the whole creature down so the high tail-fan crowns behind the head
    YOFF = 18

    def P(pts):
        return [(cx + int(x * U), int((y + YOFF) * U)) for (x, y) in pts]

    # ---- THE NINE-TAIL FAN (drawn FIRST, behind the body) ----------------
    # Nine tapering bushy tails radiating like a peacock fan from a low hip
    # anchor. Each is a triad-lit bush (dark-core -> snow fill -> sheen) with
    # a coral tip — the dominant wide silhouette.
    hip_x, hip_y = 0, 118
    n = 9
    spread = 172.0           # total fan arc in degrees (wide peacock spread)
    base_deg = -90           # straight up = -90; we fan symmetric around it
    tail_len = 122
    for i in range(n):
        # symmetric fan: i=0 leftmost ... i=8 rightmost
        frac = i / (n - 1)
        ang = math.radians(base_deg - spread / 2 + spread * frac)
        # outer tails are slightly shorter so the fan reads as a rounded crown
        edge = abs(frac - 0.5) * 2.0
        length = tail_len * (1.0 - 0.10 * edge)
        tipx = hip_x + math.cos(ang) * length
        tipy = hip_y + math.sin(ang) * length
        # perpendicular for tail width
        px_, py_ = -math.sin(ang), math.cos(ang)
        base_w = 15
        mid_w = 13
        # bushy tapered quill: base -> bulge -> tip
        bx, by = hip_x + math.cos(ang) * 14, hip_y + math.sin(ang) * 14
        mx, my = hip_x + math.cos(ang) * length * 0.62, hip_y + math.sin(ang) * length * 0.62
        tail = [
            (bx + px_ * base_w, by + py_ * base_w),
            (mx + px_ * mid_w, my + py_ * mid_w),
            (tipx + px_ * 4, tipy + py_ * 4),
            (tipx - px_ * 4, tipy - py_ * 4),
            (mx - px_ * mid_w, my - py_ * mid_w),
            (bx - px_ * base_w, by - py_ * base_w),
        ]
        # dark-core bed offset down-right
        pygame.draw.polygon(s, FUR_SH, P([(x + 2, y + 2) for (x, y) in tail]))
        pygame.draw.polygon(s, FUR, P(tail))
        # top-left rim-sheen sliver along the leading edge
        pygame.draw.polygon(s, SHEEN, P([
            (bx + px_ * base_w, by + py_ * base_w),
            (mx + px_ * mid_w, my + py_ * mid_w),
            (mx + px_ * (mid_w - 4), my + py_ * (mid_w - 4)),
            (bx + px_ * (base_w - 5), by + py_ * (base_w - 5)),
        ]))
        # coral bushy TIP (the kitsune signature) — flat triad lobe
        tipfrac = 0.72
        tcx = hip_x + math.cos(ang) * length * tipfrac
        tcy = hip_y + math.sin(ang) * length * tipfrac
        tip = [
            (tcx + px_ * 11, tcy + py_ * 11),
            (tipx + px_ * 4, tipy + py_ * 4),
            (tipx - px_ * 4, tipy - py_ * 4),
            (tcx - px_ * 11, tcy - py_ * 11),
        ]
        pygame.draw.polygon(s, CORAL_SH, P([(x + 2, y + 2) for (x, y) in tip]))
        pygame.draw.polygon(s, CORAL, P(tip))
        pygame.draw.polygon(s, CORAL_HI, P([
            (tcx + px_ * 11, tcy + py_ * 11),
            (tipx + px_ * 4, tipy + py_ * 4),
            (tipx + px_ * 1, tipy + py_ * 1),
            (tcx + px_ * 6, tcy + py_ * 6),
        ]))

    # ---- SHRINE-PRIESTESS HAORI BODY (slim, in front of the fan) ---------
    # Small weight-shifted chibi body; white haori with vermilion+gold trim.
    body = P([
        (-22, 120), (-26, 150), (-20, 176), (-24, 190),
        (-6, 194), (0, 196), (6, 194), (24, 190),
        (20, 176), (26, 150), (22, 120),
    ])
    pygame.draw.polygon(s, HAORI_SH, [(x + 2 * U, y + 2 * U) for (x, y) in body])
    pygame.draw.polygon(s, FUR, body)
    # top-left rim-sheen on the left lapel
    pygame.draw.polygon(s, SHEEN, P([
        (-22, 122), (-25, 150), (-21, 176), (-15, 174),
        (-18, 150), (-16, 124),
    ]))
    # left-over-right haori crossover front (vermilion panel)
    pygame.draw.polygon(s, VERM_SH, P([
        (-2, 124), (16, 132), (10, 186), (-2, 190),
    ]))
    pygame.draw.polygon(s, VERMILION, P([
        (-2, 124), (13, 131), (8, 182), (-2, 186),
    ]))
    pygame.draw.polygon(s, VERM_HI, P([
        (-2, 126), (8, 130), (4, 150), (-2, 150),
    ]))
    # gold sash / obi band at the waist (haori-trim)
    obi = P([(-24, 150), (24, 150), (22, 162), (-22, 162)])
    pygame.draw.polygon(s, GOLD, obi)
    pygame.draw.polygon(s, GOLD_HI, P([(-24, 150), (24, 150), (24, 154), (-24, 154)]))
    # gold collar trim down the crossover
    pygame.draw.line(s, GOLD, P([(-2, 124)])[0], P([(16, 132)])[0], int(2.5 * U))
    # little sleeve-paws (white fur) peeking from the sides
    for sx in (-1, 1):
        paw = P([
            (sx * 22, 150), (sx * 30, 156), (sx * 28, 172),
            (sx * 20, 170), (sx * 18, 158),
        ])
        pygame.draw.polygon(s, HAORI_SH, [(x + 2 * U, y + 2 * U) for (x, y) in paw])
        pygame.draw.polygon(s, FUR, paw)
        pygame.draw.polygon(s, CORAL, P([
            (sx * 30, 156), (sx * 28, 172), (sx * 23, 168), (sx * 26, 158),
        ]))

    # ---- THE FOX HEAD (big chibi head over the body) ---------------------
    # Tall pointed EARS first (behind the cranium top), coral inner.
    for sx in (-1, 1):
        ear = P([
            (sx * 12, 56), (sx * 26, 6), (sx * 40, 40), (sx * 28, 56),
        ])
        pygame.draw.polygon(s, FUR_SH, [(x + 2 * U, y + 2 * U) for (x, y) in ear])
        pygame.draw.polygon(s, FUR, ear)
        # coral inner ear
        pygame.draw.polygon(s, CORAL_SH, P([
            (sx * 18, 50), (sx * 26, 18), (sx * 33, 42),
        ]))
        pygame.draw.polygon(s, CORAL, P([
            (sx * 19, 48), (sx * 26, 22), (sx * 31, 41),
        ]))
        if sx == -1:
            pygame.draw.polygon(s, SHEEN, P([
                (sx * 12, 54), (sx * 26, 8), (sx * 20, 30),
            ]))

    # Cranium / cheeks — a rounded fox head.
    head = P([
        (-30, 56), (-34, 36), (-26, 20), (-10, 12), (0, 11),
        (10, 12), (26, 20), (34, 36), (30, 56), (22, 76),
        (10, 90), (0, 94), (-10, 90), (-22, 76),
    ])
    pygame.draw.polygon(s, FUR_SH, [(x + 2 * U, y + 3 * U) for (x, y) in head])
    pygame.draw.polygon(s, FUR, head)
    # top-left rim-sheen on the cranium
    pygame.draw.polygon(s, SHEEN, P([
        (-30, 54), (-33, 36), (-25, 21), (-12, 13), (-14, 24),
        (-24, 32), (-27, 50),
    ]))
    # cool-grey cheek dark-core hollows
    for sx in (-1, 1):
        pygame.draw.polygon(s, FUR_SH, P([
            (sx * 28, 56), (sx * 30, 66), (sx * 20, 78), (sx * 18, 64),
        ]))

    # SHARP SNOUT pointing down-forward (the sharp-snout read).
    snout = P([
        (-12, 70), (12, 70), (8, 92), (0, 100), (-8, 92),
    ])
    pygame.draw.polygon(s, FUR, snout)
    pygame.draw.polygon(s, FUR_SH, P([
        (-8, 92), (0, 100), (8, 92), (4, 96), (0, 98), (-4, 96),
    ]))
    # dark nose tip
    pygame.draw.polygon(s, NOSE, P([
        (-5, 92), (5, 92), (3, 99), (0, 102), (-3, 99),
    ]))
    pygame.draw.circle(s, SHEEN, P([(-2, 93)])[0], int(1.4 * U))

    # eyes — sly upturned almond eyes (trickster squint).
    for sx in (-1, 1):
        eye = P([
            (sx * 8, 56), (sx * 22, 52), (sx * 24, 60), (sx * 12, 64),
        ])
        pygame.draw.polygon(s, INK, eye)
        # coral upper-lid liner (sly)
        pygame.draw.line(s, CORAL, P([(sx * 8, 55)])[0], P([(sx * 22, 51)])[0], int(2 * U))
        # gold-flecked iris glint
        pygame.draw.circle(s, GOLD, P([(sx * 16, 58)])[0], int(2.6 * U))
        pygame.draw.circle(s, SHEEN, P([(sx * 14, 56)])[0], int(1.2 * U))
    # coral cheek/forehead facial markings (kitsune tells)
    for sx in (-1, 1):
        pygame.draw.polygon(s, CORAL, P([
            (sx * 16, 68), (sx * 28, 64), (sx * 27, 70), (sx * 17, 73),
        ]))
    # forehead coral flame-mark
    pygame.draw.polygon(s, CORAL, P([
        (0, 24), (5, 36), (0, 32), (-5, 36),
    ]))

    # ---- THE FOXFIRE ORB hovering by the (viewer-right) ear --------------
    _foxfire(s, cx + int(48 * U), int((28 + YOFF) * U), int(11 * U))

    # ---- ink keyline grown from the alpha mask + downscale ---------------
    outlined, _ = grow_outline(s, INK, grow=1)
    return smoothdown(outlined, target_h)


# ─────────────────────────────────────────────────────────────────────────────
#  THE PROP -> PILLAR — torii-GATE arch / shrine-pillar.
#  Vermilion torii upright = repeatable shaft (post + banding);
#  folded paper-charm (shide) garland + fox-mask plaque = gap-edge cap.
# ─────────────────────────────────────────────────────────────────────────────

def _shide(surf, x, y, P, w=5, h=14, n=4):
    """A zig-zag folded paper-charm (shide) hanging — cream lightning-fold."""
    for i in range(n):
        yy = y + i * h
        step = w if i % 2 == 0 else -w
        pygame.draw.polygon(surf, (236, 230, 222), P([
            (x, yy), (x + step, yy), (x + step, yy + h), (x, yy + h),
        ]))
        pygame.draw.polygon(surf, (200, 192, 182), P([
            (x + step, yy + h - 2), (x, yy + h - 2), (x, yy + h), (x + step, yy + h),
        ]))


def build_torii(target_h=210, as_pillar=False):
    """Render the torii prop. When `as_pillar`, mirror it into a clean
    repeatable shrine-PILLAR: the vermilion post repeats as the body, the
    lintel + shide-garland + fox-mask plaque is the detachable gap-edge cap
    (shown as a TOP cap so the gap sits at the bottom, the way Big Reapy's
    bone-bident mirrors)."""
    U = SS
    W, H = 88 * U, 230 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(pts):
        return [(cx + int(x * U), int(y * U)) for (x, y) in pts]

    post_w = 11
    if as_pillar:
        # cap sits at the TOP, shaft repeats downward toward the gap.
        cap_y = 12          # lintel band center
        shaft_top = 40
        shaft_bot = 224
        gap_dir = 1
    else:
        # the prop as the player meets it: cap up top, post standing on a base.
        cap_y = 28
        shaft_top = 56
        shaft_bot = 222
        gap_dir = 0

    # ---- vermilion POST body (repeatable shaft) --------------------------
    post = P([(-post_w, shaft_top), (post_w, shaft_top),
              (int(post_w * 0.82), shaft_bot), (-int(post_w * 0.82), shaft_bot)])
    pygame.draw.polygon(s, VERM_SH, [(x + 2 * U, y) for (x, y) in post])
    pygame.draw.polygon(s, VERMILION, post)
    # top-left sheen column
    pygame.draw.polygon(s, VERM_HI, P([
        (-post_w, shaft_top), (-post_w + 3, shaft_top),
        (-int(post_w * 0.82) + 3, shaft_bot), (-int(post_w * 0.82), shaft_bot),
    ]))
    # black lacquer banding (the repeatable banding for the pillar body)
    band_start = shaft_top + 14
    for by in range(band_start, shaft_bot - 8, 26):
        pygame.draw.rect(s, INK,
                         (cx - post_w * U, by * U, post_w * 2 * U, int(4 * U)))
        pygame.draw.rect(s, GOLD,
                         (cx - post_w * U, (by + 5) * U, post_w * 2 * U, int(1.5 * U)))

    # ---- LINTEL beams (kasagi top beam + nuki tie-beam) = gap-edge cap ----
    # kasagi: the upward-swept top beam of a torii.
    kasagi = P([
        (-40, cap_y - 9), (40, cap_y - 9), (44, cap_y - 14),
        (40, cap_y - 16), (-40, cap_y - 16), (-44, cap_y - 14),
    ])
    pygame.draw.polygon(s, VERM_SH, [(x + 2 * U, y + 2 * U) for (x, y) in kasagi])
    pygame.draw.polygon(s, VERMILION, kasagi)
    pygame.draw.polygon(s, VERM_HI, P([
        (-40, cap_y - 15), (40, cap_y - 15), (40, cap_y - 13), (-40, cap_y - 13),
    ]))
    # nuki: the lower straight tie-beam
    nuki = P([(-34, cap_y), (34, cap_y), (34, cap_y + 8), (-34, cap_y + 8)])
    pygame.draw.polygon(s, VERM_SH, [(x + 2 * U, y + 2 * U) for (x, y) in nuki])
    pygame.draw.polygon(s, VERMILION, nuki)
    pygame.draw.polygon(s, VERM_HI, P([
        (-34, cap_y + 1), (34, cap_y + 1), (34, cap_y + 3), (-34, cap_y + 3),
    ]))
    # gakuzuka centre strut + gold trim caps on the beam ends
    pygame.draw.polygon(s, VERMILION, P([
        (-4, cap_y - 9), (4, cap_y - 9), (4, cap_y), (-4, cap_y),
    ]))
    for ex in (-42, 42):
        pygame.draw.rect(s, GOLD, P([(ex - 2, cap_y - 16)])[0]
                         + (int(4 * U), int(7 * U)))

    # ---- fox-mask PLAQUE hung on the centre strut (the cap focal) --------
    mask_cy = cap_y + 18
    # white kitsune mask: rounded face + two pointed ears + coral marks
    pygame.draw.polygon(s, FUR_SH, P([(x + 1, y + 2) for (x, y) in [
        (-9, mask_cy - 8), (9, mask_cy - 8), (11, mask_cy + 2),
        (0, mask_cy + 14), (-11, mask_cy + 2)]]))
    pygame.draw.polygon(s, FUR, P([
        (-9, mask_cy - 8), (9, mask_cy - 8), (11, mask_cy + 2),
        (0, mask_cy + 14), (-11, mask_cy + 2)]))
    for sx in (-1, 1):
        pygame.draw.polygon(s, FUR, P([
            (sx * 5, mask_cy - 8), (sx * 11, mask_cy - 18), (sx * 11, mask_cy - 6)]))
        pygame.draw.polygon(s, CORAL, P([
            (sx * 7, mask_cy - 9), (sx * 10, mask_cy - 16), (sx * 10, mask_cy - 8)]))
    pygame.draw.polygon(s, SHEEN, P([
        (-9, mask_cy - 7), (-2, mask_cy - 8), (-5, mask_cy - 1)]))
    # coral mask brows + nose mark
    for sx in (-1, 1):
        pygame.draw.line(s, CORAL, P([(sx * 3, mask_cy - 3)])[0],
                         P([(sx * 8, mask_cy - 1)])[0], int(2 * U))
        pygame.draw.circle(s, INK, P([(sx * 5, mask_cy + 2)])[0], int(1.6 * U))
    pygame.draw.polygon(s, CORAL, P([
        (0, mask_cy + 3), (3, mask_cy + 9), (0, mask_cy + 7), (-3, mask_cy + 9)]))

    # ---- shide paper-charm garland hung from the nuki tie-beam -----------
    for hx in (-26, -13, 13, 26):
        _shide(s, hx, cap_y + 8, P, w=4, h=7, n=3)
    # straw shimenawa rope suggestion between them
    pygame.draw.line(s, GOLD, P([(-30, cap_y + 8)])[0], P([(30, cap_y + 8)])[0], int(2 * U))

    # foxfire spark drifting at the gap edge (mint signature carried to prop)
    if as_pillar:
        _foxfire(s, cx + int(30 * U), int((shaft_bot - 6) * U), int(7 * U))
    else:
        # stone base feet at the bottom of the standing torii
        for sx in (-1, 1):
            base = P([(sx * post_w - 3, shaft_bot - 2), (sx * post_w + 6, shaft_bot - 2),
                      (sx * post_w + 8, shaft_bot + 6), (sx * post_w - 5, shaft_bot + 6)])
            pygame.draw.polygon(s, FUR_SH, base)
            pygame.draw.polygon(s, lerp(FUR_SH, FUR, 0.4), P([
                (sx * post_w - 3, shaft_bot - 2), (sx * post_w + 6, shaft_bot - 2),
                (sx * post_w + 6, shaft_bot), (sx * post_w - 3, shaft_bot)]))

    outlined, _ = grow_outline(s, INK, grow=1)
    return smoothdown(outlined, target_h)


# ─────────────────────────────────────────────────────────────────────────────
#  SHEET COMPOSITION
# ─────────────────────────────────────────────────────────────────────────────

def main():
    SHEET_W, SHEET_H = 820, 600
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    # cool dusk-shrine backdrop so snow-white + coral + mint read honestly
    for y in range(SHEET_H):
        t = y / SHEET_H
        sheet.fill(lerp((44, 46, 58), (26, 28, 38), t), (0, y, SHEET_W, 1))

    font = pygame.font.SysFont("dejavusans", 18, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)
    tiny = pygame.font.SysFont("dejavusans", 11)

    def label(txt, x, y, f=small, col=(238, 234, 230)):
        sheet.blit(f.render(txt, True, (0, 0, 0)), (x + 1, y + 1))
        sheet.blit(f.render(txt, True, col), (x, y))

    label("KITSUNE — nine-tailed fox-spirit shrine devil  [COOL GLOW: MINT-GREEN FOXFIRE]",
          16, 12, font)
    label("snow-white + coral + mint-foxfire  ·  sly fox face, tall coral-inner ears · slim haori body · WIDE peacock fan of nine bushy coral-tipped tails · mint foxfire orb",
          16, 36, tiny, (188, 214, 200))

    # large creature
    big = build_kitsune(target_h=320)
    bx = 30
    by = 68
    sheet.blit(big, (bx, by))
    label("creature (large)", bx + big.get_width() // 2 - 42, by + big.get_height() + 4)

    # 32px creature read (3x nearest zoom + actual 32px)
    small_creat = build_kitsune(target_h=32)
    sy = by + big.get_height() + 26
    zoom = pygame.transform.scale(small_creat,
                                  (small_creat.get_width() * 3,
                                   small_creat.get_height() * 3))
    zx = bx + 8
    sheet.blit(zoom, (zx, sy))
    sheet.blit(small_creat, (zx + zoom.get_width() + 16,
                             sy + zoom.get_height() - small_creat.get_height()))
    label("32px read (3x + actual)", zx, sy + zoom.get_height() + 4, tiny)

    # large torii prop
    torii = build_torii(target_h=360, as_pillar=False)
    stx = 420
    sty = 64
    sheet.blit(torii, (stx, sty))
    label("torii-gate (prop)", stx + torii.get_width() // 2 - 36,
          sty + torii.get_height() + 2, tiny)

    # mirrored pillar
    pill = build_torii(target_h=360, as_pillar=True)
    px = 540
    sheet.blit(pill, (px, sty))
    label("-> PILLAR mirror", px - 2, sty + pill.get_height() + 2, tiny)
    label("(repeatable post +", px - 2, sty + pill.get_height() + 16, tiny,
          (196, 200, 170))
    label(" lintel+shide+mask cap)", px - 2, sty + pill.get_height() + 28, tiny,
          (196, 200, 170))

    # 32px prop / pillar reads
    torii32 = build_torii(target_h=32, as_pillar=False)
    pill32 = build_torii(target_h=32, as_pillar=True)
    z2 = pygame.transform.scale(torii32,
                                (torii32.get_width() * 3, torii32.get_height() * 3))
    z3 = pygame.transform.scale(pill32,
                                (pill32.get_width() * 3, pill32.get_height() * 3))
    zy = 70
    zx2 = 670
    sheet.blit(z2, (zx2, zy))
    sheet.blit(z3, (zx2 + z2.get_width() + 20, zy))
    sheet.blit(torii32, (zx2 + 6, zy + z2.get_height() + 8))
    sheet.blit(pill32, (zx2 + z2.get_width() + 26, zy + z2.get_height() + 8))
    label("32px torii / pillar", zx2, zy + z2.get_height() + 34, tiny)

    # palette swatch strip
    swatches = [
        ("fur", FUR), ("fur-sh", FUR_SH), ("coral", CORAL),
        ("vermilion", VERMILION), ("mint-foxfire", MINT), ("gold", GOLD),
        ("ink", INK), ("sheen", SHEEN),
    ]
    swx, swy = 670, 360
    for i, (nm, col) in enumerate(swatches):
        ry = swy + i * 22
        pygame.draw.rect(sheet, col, (swx, ry, 26, 18))
        pygame.draw.rect(sheet, (10, 10, 14), (swx, ry, 26, 18), 1)
        label(nm, swx + 32, ry + 3, tiny)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
