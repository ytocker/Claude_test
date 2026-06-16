"""IMPLET — chibi Skybit DEVIL boss, take B8 (the pocket gremlin imp).

A teeny acid-GREEN pear-shaped gremlin — the set's scale-FLOOR (smallest,
lightest figure of the ten) — hauling a fire-SPEAR comically too big for it.
Menace through pure gremlin GLEE plus the comedy of scale: a wee winged
trouble-maker that can barely lift its own weapon.

Drawn in the Skybit chibi house style — FLAT saturated fills, 1-2px hard ink
keylines, the dark-core -> fill -> top-left sheen triad (the `_marotte_ruff` /
Grim Sprout recipe), supersampled then smoothscaled for crisp AA, with a grown
1px silhouette outline so the imp pops on any sky.

DISTINCTNESS FROM GRIM SPROUT (the shipped reaper) is load-bearing here: that
one is a hooded orchid-violet imp dragging a great SCYTHE. This is a DEVIL, not
a reaper — a PEAR-shaped acid-green gremlin (no hood, no skull), with DEVIL
BAT-WINGS spread wide behind it (its 1x silhouette anchor), a tiny pointy
horn-nub + big pointed ears (NOT a curved ram pair), a curl tail, and a slim
FIRE-SPEAR (warm flame-fork tip), never a scythe. The palette is acid-green —
distinct from Pyrecrown's green soul-FLAME by being a body-green gremlin, not a
green-flame skull, and from any reaper-grey/violet.

Headless review renderer — not shipped. Imports the real game helpers so the
finish matches house style.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame

from game.draw import _shade_c, lerp_color, blit_glow  # noqa: F401
from game.config import PIPE_W

# ── IMPLET palette ("acid gremlin": acid-green body + plum-black wings) ───────
GREEN      = (120, 196,  72)   # #78C448 acid-green body
GREEN_DK   = ( 78, 142,  46)   # #4E8E2E olive shade
GREEN_HI   = (182, 232,  96)   # #B6E860 chartreuse sheen
CREAM      = (220, 232, 176)   # #DCE8B0 belly-cream
WING       = ( 32,  26,  34)   # near-black bat-wing membrane
WING_HI    = (110,  68, 128)   # #6E4480 plum-wing top-light (devil accent)
WING_DK    = ( 72,  42,  86)   # #482A56 plum wing-shade
HORN       = ( 28,  22,  30)   # ink-black horn-nub + ear-tips
EYE_ORANGE = (248, 168,  52)   # #F8A834 huge glowing gremlin eyes
EYE_HOT    = (255, 226, 150)   # eye hotspot
TONGUE     = (214,  72, 110)   # cheeky little tongue
SHAFT      = (122,  92,  58)   # warm-wood spear shaft
SHAFT_DK   = _shade_c(SHAFT, -55)
SHAFT_HI   = _shade_c(SHAFT, 55)
IRON       = (108, 112, 124)   # the spear's iron collar / socket
FLAME_OUT  = (255, 120,  36)   # warm fire-fork flame (NOT green — own the warm)
FLAME_MID  = (255, 176,  64)
FLAME_CORE = (255, 232, 168)
INK        = ( 28,  22,  30)   # #1C1620 hard keyline


def _triad_circle(surf, cx, cy, r, col, ss):
    """The house FORM recipe: a dark-core ring, the flat fill, and a ~1/3-radius
    top-left sheen — flat shapes that read sculpted without any gradient (the
    shared `_marotte_ruff`/Grim Sprout primitive)."""
    pygame.draw.circle(surf, _shade_c(col, -55), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)), max(2, int(r - ss)))
    pygame.draw.circle(surf, _shade_c(col, 55),
                       (int(cx - r * 0.32), int(cy - r * 0.32)),
                       max(1, int(r * 0.34)))


def _add_outline(src, outline_color=(28, 22, 30, 235)):
    """Grow a 1px dark outline from the alpha mask so the imp keeps a black-shape
    silhouette on any sky (the parrot `_add_outline` recipe)."""
    w, h = src.get_size()
    pad = 2
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


def _flame_fork(surf, cx, ty, w, h, ss):
    """The fire-SPEAR tip: a slim THREE-pronged flame-fork (a fire trident), warm
    not green so it never echoes Pyrecrown's green soul-flame or Glitchfiend's
    neon. Each prong is a tapered teardrop flame with a glow halo; the centre
    prong rides tallest so the silhouette reads 'fork', not 'torch'."""
    blit_glow(surf, int(cx), int(ty - h * 0.45), int(h * 0.6), FLAME_OUT, 130)
    prongs = ((-1, 0.78), (0, 1.0), (1, 0.78))   # (x-dir, height-frac)
    for xd, hf in prongs:
        px = cx + xd * w * 0.62
        ph = h * hf
        # A leaf/teardrop flame: wide base, curl to a point, slight outward lean.
        tip = (px + xd * w * 0.18, ty - ph)
        base_l = (px - w * 0.30, ty)
        base_r = (px + w * 0.30, ty)
        mid_l = (px - w * 0.34 + xd * w * 0.05, ty - ph * 0.45)
        mid_r = (px + w * 0.20 + xd * w * 0.12, ty - ph * 0.5)
        flame = [base_l, mid_l, tip, mid_r, base_r]
        pygame.draw.polygon(surf, FLAME_OUT, flame)
        pygame.draw.polygon(surf, INK, flame, max(1, int(1.6 * ss)))
        # Inner warm core (mid + pale) so the flame reads hot, not a flat orange chip.
        inner = [(px - w * 0.16, ty - ph * 0.08),
                 (px + xd * w * 0.12, ty - ph * 0.7),
                 (px + w * 0.16, ty - ph * 0.08)]
        pygame.draw.polygon(surf, FLAME_MID, inner)
        pygame.draw.polygon(surf, FLAME_CORE,
                            [(px, ty - ph * 0.12),
                             (px + xd * w * 0.06, ty - ph * 0.5),
                             (px + w * 0.07, ty - ph * 0.12)])


def _bat_wing(surf, hinge, scale, ss, *, side):
    """One oversized DEVIL bat-wing fanning out + up behind the body — the imp's
    1x silhouette ANCHOR (AD guardrail: tiny figure, but the bold wing spread must
    still register on a busy sky). A hard membrane: a clawed top spar, 3 finger
    ribs, and scalloped membrane bays between them, with a plum top-light so the
    near-black wing still reads as a lit form. `side` (-1 left, +1 right) mirrors
    it. Wings, not a hood — the core devil/Grim-Sprout separator."""
    hx, hy = hinge
    sgn = side
    L = 86 * scale * ss            # wing reach
    # Finger ribs fan from the hinge: a long top spar plus two shorter fingers,
    # each tipped with a little claw. Tips define the scalloped trailing edge.
    ribs = [
        (-0.18, 1.00),   # top spar (sweeps up + out, the thumb-claw)
        (0.28, 0.96),    # upper finger
        (0.66, 0.78),    # lower finger
    ]
    tips = []
    for ang_f, len_f in ribs:
        a = math.radians(-150 * sgn) + sgn * ang_f * math.radians(118)
        # Bias the whole fan upward+outward so the wings cape the body from behind.
        tx = hx + math.cos(a) * L * len_f
        ty = hy + math.sin(a) * L * len_f - L * 0.18
        tips.append((tx, ty))
    # Membrane polygon: hinge -> top tip -> scalloped down through finger tips ->
    # back to a low anchor near the body so the bottom bay closes cleanly.
    low_anchor = (hx + sgn * L * 0.10, hy + L * 0.34)
    membrane = [(hx, hy)]
    membrane += tips
    membrane.append(low_anchor)
    pygame.draw.polygon(surf, WING_DK, membrane)
    pygame.draw.polygon(surf, WING, [(x - sgn * ss, y + ss) for x, y in membrane])
    pygame.draw.polygon(surf, INK, membrane, max(2, int(2.2 * ss)))
    # Plum top-light skim along the leading (top) spar so the black wing reads lit.
    pygame.draw.line(surf, WING_HI, (hx, hy), tips[0], max(2, int(2.4 * ss)))
    pygame.draw.line(surf, WING_HI, (hx, hy), tips[0], max(1, int(1.2 * ss)))
    # Finger ribs drawn over the membrane so the bat structure reads.
    for tx, ty in tips:
        pygame.draw.line(surf, INK, (hx, hy), (int(tx), int(ty)), max(2, int(2.0 * ss)))
        pygame.draw.line(surf, WING_HI, (hx, hy), (int(tx), int(ty)), max(1, int(ss)))
        # A tiny claw hook at each rib tip (gremlin tell).
        ca = math.atan2(ty - hy, tx - hx)
        claw = (tx + math.cos(ca - sgn * 0.7) * 6 * scale * ss,
                ty + math.sin(ca - sgn * 0.7) * 6 * scale * ss)
        pygame.draw.line(surf, INK, (int(tx), int(ty)),
                         (int(claw[0]), int(claw[1])), max(2, int(2.2 * ss)))


# ── the imp + his oversized fire-spear ───────────────────────────────────────

def build_implet(scale=1.0, ss=3):
    """Render the gremlin + oversized fire-spear onto a tight transparent surface,
    then add a grown outline. The body is sized SMALL and the spear DELIBERATELY
    tall so the prop-to-body ratio reads as the comedy-of-scale gag, while the big
    bat-wings spread wide to anchor the 1x silhouette."""
    BW = int(250 * scale * ss)
    BH = int(420 * scale * ss)
    s = pygame.Surface((BW, BH), pygame.SRCALPHA)

    # Tiny pear body anchored low; the spear towers above it.
    body_cx = int(BW * 0.46)
    feet_y = int(BH * 0.94)
    head_r = int(34 * scale * ss)          # big head (chibi cute lever)
    belly_w = int(30 * scale * ss)         # pear: wide bottom
    belly_h = int(40 * scale * ss)

    # ── 1. THE OVERSIZED FIRE-SPEAR (drawn first; the imp's mitts close over it) ─
    # A slim near-vertical pole far taller than the imp, topped by a small warm
    # flame-fork. Slight lean so it reads "held", and tilted so the tiny imp
    # plainly strains under it.
    spear_top = (int(BW * 0.70), int(BH * 0.10))
    spear_bot = (int(BW * 0.60), feet_y - int(2 * scale * ss))
    sw = int(6 * scale * ss)
    pygame.draw.line(s, SHAFT_DK, spear_top, spear_bot, sw + max(2, int(3 * ss)))
    pygame.draw.line(s, SHAFT, spear_top, spear_bot, sw)
    dx, dy = spear_bot[0] - spear_top[0], spear_bot[1] - spear_top[1]
    plen = math.hypot(dx, dy) or 1
    nx, ny = -dy / plen, dx / plen
    off = int(2 * scale * ss)
    pygame.draw.line(s, SHAFT_HI,
                     (spear_top[0] - nx * off, spear_top[1] - ny * off),
                     (spear_bot[0] - nx * off, spear_bot[1] - ny * off),
                     max(1, int(1.8 * ss)))
    # Iron banding collars (also the pillar-banding cue) at three points.
    for t in (0.30, 0.55, 0.80):
        bxp = int(spear_top[0] + dx * t)
        byp = int(spear_top[1] + dy * t)
        pygame.draw.circle(s, INK, (bxp, byp), max(3, int(5 * scale * ss)))
        pygame.draw.circle(s, IRON, (bxp, byp), max(2, int(4 * scale * ss)))
        pygame.draw.circle(s, _shade_c(IRON, 50),
                           (bxp - int(ss), byp - int(ss)), max(1, int(2 * scale * ss)))
    # Iron socket where the flame-fork seats on the shaft.
    sock = (spear_top[0], spear_top[1] + int(6 * scale * ss))
    pygame.draw.circle(s, IRON, sock, max(3, int(6 * scale * ss)))
    pygame.draw.circle(s, INK, sock, max(3, int(6 * scale * ss)), max(1, int(ss)))
    # The warm flame-fork tip (the gap-edge cap, here at the top of the prop).
    _flame_fork(s, spear_top[0], spear_top[1] + int(2 * scale * ss),
                int(26 * scale * ss), int(58 * scale * ss), ss)

    # ── 2. BAT-WINGS spread wide behind the body (the 1x silhouette anchor) ──────
    wing_hy = feet_y - belly_h - int(4 * scale * ss)
    _bat_wing(s, (body_cx + int(6 * scale * ss), wing_hy), scale, ss, side=1)
    _bat_wing(s, (body_cx - int(6 * scale * ss), wing_hy), scale, ss, side=-1)

    # ── 3. CURL TAIL flicking out behind the lower body ──────────────────────────
    tail = []
    tseg = 16
    t0x, t0y = body_cx - belly_w + int(2 * scale * ss), feet_y - int(8 * scale * ss)
    for i in range(tseg):
        t = i / (tseg - 1)
        # An S that flips out left then curls up into a hooked spade tip.
        tx = t0x - math.sin(t * math.pi * 1.15) * 22 * scale * ss
        ty = t0y - t * 30 * scale * ss + math.sin(t * math.pi) * 6 * scale * ss
        rr = (4.0 - 2.6 * t) * scale * ss
        tail.append((tx, ty, max(1.5, rr)))
    for (tx, ty, rr) in tail:
        pygame.draw.circle(s, GREEN_DK, (int(tx), int(ty)), max(2, int(rr)))
    for (tx, ty, rr) in tail:
        pygame.draw.circle(s, GREEN, (int(tx), int(ty)), max(1, int(rr - ss * 0.6)))
    # Spade tip — a tiny devil arrowhead (devil tell), points up-left.
    spx, spy, _ = tail[-1]
    spade = [(spx - 8 * scale * ss, spy + 2 * scale * ss),
             (spx + 4 * scale * ss, spy + 4 * scale * ss),
             (spx - 4 * scale * ss, spy - 10 * scale * ss)]
    pygame.draw.polygon(s, GREEN_DK, spade)
    pygame.draw.polygon(s, INK, spade, max(1, int(1.6 * ss)))

    # ── 4. CLAWED FEET poking out the bottom (tiny, scale-floor) ─────────────────
    for fx_off in (-12, 11):
        fx = body_cx + int(fx_off * scale * ss)
        fy = feet_y
        fr = int(8 * scale * ss)
        _triad_circle(s, fx, fy, fr, GREEN, ss)
        for k in (-1, 0, 1):
            ca = math.radians(90 + k * 26)
            cx2 = fx + math.cos(ca) * fr * 0.4
            cy2 = fy + fr * 0.5
            tip = (cx2 + math.cos(ca) * fr * 0.6, cy2 + fr * 0.7)
            pygame.draw.line(s, INK, (int(cx2), int(cy2)),
                             (int(tip[0]), int(tip[1])), max(2, int(2.0 * ss)))

    # ── 5. PEAR BODY — wide-bottomed acid-green torso w/ a cream belly patch ─────
    belly_cy = feet_y - belly_h - int(2 * scale * ss)
    # Pear silhouette via an ellipse: narrow up top (toward the head), fat at base.
    pygame.draw.ellipse(s, GREEN_DK,
                        (body_cx - belly_w, belly_cy - belly_h,
                         belly_w * 2, belly_h * 2))
    pygame.draw.ellipse(s, GREEN,
                        (body_cx - belly_w + int(ss), belly_cy - belly_h + int(ss),
                         belly_w * 2 - int(2 * ss), belly_h * 2 - int(2 * ss)))
    # Top-left sheen wedge.
    pygame.draw.ellipse(s, GREEN_HI,
                        (body_cx - belly_w + int(3 * ss), belly_cy - belly_h + int(2 * ss),
                         belly_w, belly_h))
    # Cream belly patch (lower-front).
    pygame.draw.ellipse(s, CREAM,
                        (body_cx - int(belly_w * 0.55), belly_cy - int(belly_h * 0.1),
                         int(belly_w * 1.1), int(belly_h * 1.0)))
    pygame.draw.ellipse(s, _shade_c(CREAM, -34),
                        (body_cx - int(belly_w * 0.55), belly_cy - int(belly_h * 0.1),
                         int(belly_w * 1.1), int(belly_h * 1.0)), max(1, int(ss)))

    # ── 6. STUB MITT ARMS — both straining UP on the too-big spear ───────────────
    up_grip = (int(spear_top[0] + dx * 0.62), int(spear_top[1] + dy * 0.62))
    lo_grip = (int(spear_top[0] + dx * 0.78), int(spear_top[1] + dy * 0.78))
    sh_hi = (body_cx + int(12 * scale * ss), belly_cy - int(10 * scale * ss))
    sh_lo = (body_cx + int(15 * scale * ss), belly_cy + int(4 * scale * ss))
    pygame.draw.line(s, GREEN_DK, sh_hi, up_grip, int(9 * scale * ss))
    pygame.draw.line(s, GREEN, sh_hi, up_grip, int(6 * scale * ss))
    pygame.draw.line(s, GREEN_DK, sh_lo, lo_grip, int(9 * scale * ss))
    pygame.draw.line(s, GREEN, sh_lo, lo_grip, int(6 * scale * ss))
    for grip, gr in ((up_grip, 7), (lo_grip, 7)):
        _triad_circle(s, grip[0], grip[1], int(gr * scale * ss), GREEN, ss)
        pygame.draw.circle(s, INK, grip, int(gr * scale * ss), max(1, int(ss)))

    # ── 7. THE HEAD — round, with big POINTED EARS, a single horn-NUB + huge eyes ─
    head_cy = belly_cy - belly_h - int(2 * scale * ss)
    # Big pointed ears (gremlin signature) BEFORE the head so they tuck behind it.
    for esgn in (-1, 1):
        eb = (body_cx + esgn * head_r * 0.78, head_cy + head_r * 0.06)
        etip = (body_cx + esgn * head_r * 1.7, head_cy - head_r * 0.7)
        ebk = (body_cx + esgn * head_r * 0.7, head_cy + head_r * 0.5)
        ear = [eb, etip, ebk]
        pygame.draw.polygon(s, GREEN_DK, ear)
        # Inner ear-shell so it reads as an ear, not a fin.
        inner = [(body_cx + esgn * head_r * 0.85, head_cy + head_r * 0.04),
                 (body_cx + esgn * head_r * 1.45, head_cy - head_r * 0.5),
                 (body_cx + esgn * head_r * 0.78, head_cy + head_r * 0.36)]
        pygame.draw.polygon(s, GREEN, inner)
        pygame.draw.polygon(s, INK, ear, max(1, int(1.6 * ss)))
    _triad_circle(s, body_cx, head_cy, head_r, GREEN, ss)
    # Single off-centre pointy horn-NUB (tiny imp horn — explicitly NOT a ram
    # pair; the set-wide no-second-ram-horn guardrail).
    hnx = body_cx + int(head_r * 0.30)
    hny = head_cy - head_r + int(2 * scale * ss)
    horn = [(hnx - 5 * scale * ss, hny + 2 * scale * ss),
            (hnx + 5 * scale * ss, hny + 2 * scale * ss),
            (hnx + 1 * scale * ss, hny - 16 * scale * ss)]
    pygame.draw.polygon(s, HORN, horn)
    pygame.draw.polygon(s, _shade_c(HORN, 40), horn, max(1, int(ss)))

    # Huge glowing gremlin eyes (the cute lever) — big, round, asymmetric, with a
    # warm glow. Orange so they pop against acid-green without going green-on-green.
    eyes = ((-0.40, -0.05, 0.36), (0.42, -0.10, 0.30))
    for exf, eyf, erf in eyes:
        ex = int(body_cx + exf * head_r)
        ey = int(head_cy + eyf * head_r)
        blit_glow(s, ex, ey, int(8 * scale * ss), EYE_ORANGE, 120)
    for exf, eyf, erf in eyes:
        ex = int(body_cx + exf * head_r)
        ey = int(head_cy + eyf * head_r)
        er = max(3, int(erf * head_r))
        pygame.draw.circle(s, INK, (ex, ey), er + max(1, int(ss)))
        pygame.draw.circle(s, EYE_ORANGE, (ex, ey), er)
        pygame.draw.circle(s, EYE_HOT, (ex - int(er * 0.3), ey - int(er * 0.3)),
                           max(1, int(er * 0.42)))
        # Tiny dark pupil so the big eye still reads as an eye, not a lamp.
        pygame.draw.circle(s, INK, (ex + int(er * 0.1), ey + int(er * 0.1)),
                           max(1, int(er * 0.32)))

    # Snaggle grin + a cheeky tongue tip (gremlin glee — pure mischief, not grim).
    gy = head_cy + int(head_r * 0.48)
    gx = body_cx - int(head_r * 0.05)
    grin = [(gx - head_r * 0.34, gy),
            (gx - head_r * 0.10, gy + head_r * 0.18),
            (gx + head_r * 0.30, gy + head_r * 0.06)]
    pygame.draw.lines(s, INK, False, [(int(a), int(b)) for a, b in grin],
                      max(2, int(2.2 * ss)))
    # One up-poking snaggle fang.
    fx = gx + int(head_r * 0.14)
    fang = [(fx - 4 * scale * ss, gy + 4 * scale * ss),
            (fx + 4 * scale * ss, gy + 4 * scale * ss),
            (fx, gy - 7 * scale * ss)]
    pygame.draw.polygon(s, CREAM, fang)
    pygame.draw.polygon(s, INK, fang, max(1, int(1.4 * ss)))
    # Cheeky tongue tip at the grin's low corner.
    pygame.draw.circle(s, TONGUE,
                       (int(gx - head_r * 0.06), int(gy + head_r * 0.22)),
                       max(2, int(3 * scale * ss)))

    s = _add_outline(s)
    fw = max(1, s.get_width() // ss)
    fh = max(1, s.get_height() // ss)
    return pygame.transform.smoothscale(s, (fw, fh))


# ── prop -> pillar mirror: the fire-spear is a tileable vertical post ─────────

def _spear_post(surf, cx, top, bot, w, ss):
    """The shared shaft body: a slim warm-wood post, dark-cored + top-left lit
    edge + iron banding collars — the repeatable pillar SHAFT."""
    pygame.draw.line(surf, SHAFT_DK, (cx, top), (cx, bot), w + max(2, int(3 * ss)))
    pygame.draw.line(surf, SHAFT, (cx, top), (cx, bot), w)
    pygame.draw.line(surf, SHAFT_HI, (cx - int(2 * ss), top), (cx - int(2 * ss), bot),
                     max(1, int(2 * ss)))
    span = bot - top
    n = max(2, int(span / (max(1, w) * 6)))
    for i in range(n):
        cy = int(top + span * (i + 0.5) / n)
        pygame.draw.circle(surf, INK, (cx, cy), max(4, int(7 * ss)))
        pygame.draw.circle(surf, IRON, (cx, cy), max(3, int(5 * ss)))
        pygame.draw.circle(surf, _shade_c(IRON, 50),
                           (cx - int(ss), cy - int(ss)), max(2, int(3 * ss)))


def draw_spear_pillar_cap(surf, cx, top, bot, w, ss, *, flip):
    """The TOP CAP pier: the spear shaft runs the full height, the warm flame-fork
    rides the GAP-EDGE (inner end) ONLY, flaring INTO the gap. `flip=True` draws
    the bottom pier as a vertical mirror so a top/bottom pair reads as one matched
    obstacle. The flame is detachable to the gap-edge so the repeatable mid-shaft
    tiles cleanly with no flame in it."""
    if flip:
        h = surf.get_height()
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        draw_spear_pillar_cap(tmp, cx, h - bot, h - top, w, ss, flip=False)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, 0))
        return

    _spear_post(surf, cx, top, bot, w, ss)
    # GAP-EDGE flame-fork at the inner (here BOTTOM) end ONLY, flaring up into the
    # gap. Iron socket where it seats on the shaft.
    gap_y = bot
    pygame.draw.circle(surf, IRON, (cx, gap_y), max(4, int(7 * ss)))
    pygame.draw.circle(surf, INK, (cx, gap_y), max(4, int(7 * ss)), max(1, int(ss)))
    _flame_fork(surf, cx, gap_y - int(2 * ss), int(34 * ss), int(76 * ss), ss)


def draw_spear_pillar_mid(surf, cx, top, bot, w, ss):
    """The REPEATABLE MID segment: pure banded shaft, NO flame — proves the body
    tiles cleanly because the flame is a detachable gap-flourish."""
    _spear_post(surf, cx, top, bot, w, ss)


# ── sheet composition ────────────────────────────────────────────────────────

def _sky_panel(w, h, night):
    """The game's real biome day/night keyframes, so legibility is judged on the
    actual backdrop the boss must read on."""
    surf = pygame.Surface((w, h))
    if night:
        top, bot = (5, 8, 30), (35, 55, 115)
    else:
        top, bot = (40, 110, 200), (170, 220, 245)
    for y in range(h):
        pygame.draw.line(surf, lerp_color(top, bot, y / h), (0, y), (w, y))
    return surf


def _grayscale(src):
    """A B/W silhouette-legibility check: luminance copy so the wings + face must
    read on value alone, not hue."""
    g = src.copy()
    arr = pygame.surfarray.pixels3d(g)
    lum = (arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587 + arr[:, :, 2] * 0.114)
    arr[:, :, 0] = arr[:, :, 1] = arr[:, :, 2] = lum.astype(arr.dtype)
    del arr
    return g


def _label(surf, font, text, x, y):
    sh = font.render(text, True, (0, 0, 0))
    surf.blit(sh, (x + 1, y + 1))
    surf.blit(font.render(text, True, (255, 255, 255)), (x, y))


def main():
    pygame.init()
    ss = 3
    SHEET_W, SHEET_H = 980, 760
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((40, 48, 36))                       # neutral olive-grey board
    font = pygame.font.SysFont("dejavusans", 16, bold=True)
    fbig = pygame.font.SysFont("dejavusans", 22, bold=True)

    _label(sheet, fbig, "IMPLET  -  pocket gremlin imp (take B8)  R1", 20, 14)

    # (a) Showcase boss on a neutral panel — emphasize tiny-imp + oversized
    # fire-spear comedy of scale (but it must read DEVIL, not reaper).
    panel_w, panel_h = 330, 650
    panel = pygame.Surface((panel_w, panel_h))
    panel.fill((56, 64, 48))
    pygame.draw.rect(panel, (84, 96, 70), panel.get_rect(), 3)
    boss = build_implet(scale=1.45, ss=ss)
    panel.blit(boss, (panel_w // 2 - boss.get_width() // 2,
                      panel_h // 2 - boss.get_height() // 2 + 6))
    sheet.blit(panel, (20, 52))
    _label(sheet, font, "(a) showcase  -  spear DWARFS the imp", 24, 60)

    # (b) prop -> pillar mirror: a tall vertical PILLAR pair (flame-tip cap +
    # repeatable shaft mid) proving the spear tiles and the flame stays gap-edge.
    pil_w, pil_h = 170, 600
    pil = pygame.Surface((pil_w * ss, pil_h * ss), pygame.SRCALPHA)
    pil.fill((38, 44, 34))
    pcx = pil_w * ss // 2
    post_w = int(PIPE_W * 0.34 * ss)
    gap_top = int(pil_h * 0.46 * ss)
    gap_bot = int(pil_h * 0.58 * ss)
    draw_spear_pillar_cap(pil, pcx, int(0.04 * pil_h * ss), gap_top, post_w, ss,
                          flip=False)
    draw_spear_pillar_cap(pil, pcx, gap_bot, int(0.96 * pil_h * ss), post_w, ss,
                          flip=True)
    pil = pygame.transform.smoothscale(pil, (pil_w, pil_h))
    sheet.blit(pil, (372, 78))
    _label(sheet, font, "(b) spear -> PILLAR pair", 376, 58)
    _label(sheet, font, "flame = gap-edge only", 376, 686)

    # A standalone repeatable-MID strip beside it, proving the body tiles cleanly.
    mid_w, mid_h = 80, 600
    mid = pygame.Surface((mid_w * ss, mid_h * ss), pygame.SRCALPHA)
    mid.fill((38, 44, 34))
    draw_spear_pillar_mid(mid, mid_w * ss // 2, 0, mid_h * ss, post_w, ss)
    mid = pygame.transform.smoothscale(mid, (mid_w, mid_h))
    sheet.blit(mid, (560, 78))
    _label(sheet, font, "(b') repeat MID", 562, 686)

    # (c) 1x in-game-scale insets on day + night sky + a grayscale check.
    inset_w, inset_h = 132, 230
    small_boss = build_implet(scale=0.62, ss=ss)
    cells = ((False, "DAY"), (True, "NIGHT"))
    for i, (night, name) in enumerate(cells):
        sky = _sky_panel(inset_w, inset_h, night)
        sky.blit(small_boss, (inset_w // 2 - small_boss.get_width() // 2,
                              inset_h // 2 - small_boss.get_height() // 2 + 6))
        pygame.draw.rect(sky, (20, 24, 18), sky.get_rect(), 2)
        x = 672
        y = 80 + i * 250
        sheet.blit(sky, (x, y))
        _label(sheet, font, "(c) 1x  " + name, x + 2, y - 20)

    bw = _grayscale(small_boss)
    bwpanel = pygame.Surface((inset_w, inset_h))
    bwpanel.fill((128, 128, 128))
    bwpanel.blit(bw, (inset_w // 2 - bw.get_width() // 2,
                      inset_h // 2 - bw.get_height() // 2 + 6))
    pygame.draw.rect(bwpanel, (20, 24, 18), bwpanel.get_rect(), 2)
    sheet.blit(bwpanel, (820, 80))
    _label(sheet, font, "(c) 1x  B/W", 822, 60)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "skybit_devil", "devil", "implet")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
