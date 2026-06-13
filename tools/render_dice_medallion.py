"""Look-dev renderer: 5 JESTER-CLOWN takes on the RARE dice-results medallion.

The user picked the round-3 cell-5 Medallion (a plum field ring + fluted gold
bezel + cream disc + laurel + "PAGODAS" plate) as the base, and asked to push
it much further into the hero clown's mischievous JESTER identity — "a bit
mean" — and to RECENTRE the rolled number on the cream disc.

This sheet ports the jester vocabulary (bells, fanged grin, cocked brow, imp
horns, scalloped/belled framing, shoulder poms) DOWN onto the medallion at
bezel scale, reusing the base renderer's proven number/label/sky/confetti/sheet
machinery so the explorations look like the real game and are judged at TRUE
264px on the day sky WITH an actual-size inset.

The five span the mischief spectrum (cheeky → devilish → menacing-leaning) and
the reward ramp (a plainer LOW roll vs a loaded HIGH/JACKPOT roll in one shared
design language), so the art director can see how far the "mean" edge can go on
an upbeat "you rolled N!" moment.

Run (headless):
    PYTHONPATH=. python tools/render_dice_medallion.py
Writes docs/dice_results/medallion/round_1.png.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import hud  # noqa: E402  vendored bold TTF + cache

# Reuse the base renderer's machinery so these explorations are pixel-faithful
# to the real popup pipeline (number treatment, label plate, confetti keepout,
# sky swatch, SS-supersample compositing, the sheet builder's actual-size inset).
from tools.render_dice_celebration import (  # noqa: E402
    SKY_TOP, SKY_BOT, NIGHT_TOP, NIGHT_BOT,
    PLUM, PLUM_DK, LIME, GOLD, CREAM,
    sky_tile, _num_block, _label_plate, _star,
)

# Local copy of the jester _shade so this module needn't pull the whole clown
# body kit (and its game.config / parrot imports) into a UI-only renderer.
def _shade(c, d):
    return (max(0, min(255, int(c[0] + d))),
            max(0, min(255, int(c[1] + d))),
            max(0, min(255, int(c[2] + d))))


# Gold tones for the bezel metal (matching the base medallion's metal ramp).
GOLD_DK = (180, 132, 28)
GOLD_MD = (200, 150, 30)
INK = (28, 22, 30)
MOUTH_DK = (120, 30, 42)


# ── ported jester ornaments, re-implemented at MEDALLION (bezel) scale ───────
# The jester kit was authored at ~22px head scale; here every primitive is
# rebuilt to ride the ~166px-radius bezel of a 264px medallion (supersampled),
# so it reads as the SAME mischief vocabulary scaled UP to a hero frame.

def _bell(canvas, x, y, r, *, col=(245, 240, 200)):
    """3-layer specular gold bell — a dark seat, the body, a hot top-left dot —
    so it reads as a struck gold sphere, not a flat disc. The jester signature."""
    pygame.draw.circle(canvas, _shade(col, -55), (int(x), int(y)), int(r + 1))
    pygame.draw.circle(canvas, col, (int(x), int(y)), int(r))
    pygame.draw.circle(canvas, _shade(col, 80), (int(x - r * 0.35), int(y - r * 0.35)),
                       max(1, int(r * 0.5)))
    # Tiny crossbar slit so the bell reads as a jingle bell, not just a bead.
    pygame.draw.line(canvas, _shade(col, -70),
                     (int(x - r * 0.6), int(y + r * 0.45)),
                     (int(x + r * 0.6), int(y + r * 0.45)), max(1, int(r * 0.22)))


def _dangler(canvas, cx, cy, ang, R, ss, *, length, bell_r, col=(245, 240, 200),
             cord=PLUM_DK):
    """A jester BELL hanging off the bezel rim on a short cord at angle `ang`.
    The cord roots just inside the rim and the bell swings out past it so the
    medallion reads fringed with jingle bells."""
    rx = cx + math.cos(ang) * (R - 2 * ss)
    ry = cy + math.sin(ang) * (R - 2 * ss)
    bx = cx + math.cos(ang) * (R + length)
    by = cy + math.sin(ang) * (R + length)
    pygame.draw.line(canvas, cord, (int(rx), int(ry)), (int(bx), int(by)),
                     max(2, int(2 * ss)))
    _bell(canvas, bx, by, bell_r, col=col)


def _imp_horn(canvas, cx, cy, R, ss, *, sgn, col, length=1.0):
    """A soft IMP HORN cresting the medallion — a stubby rounded nub curling
    gently outward+up, finished with a small bell-lit tip. Devilish but impish,
    never a sharp menace spike (the jester kit's cap_imp_hood read)."""
    base_a = -math.pi / 2 + sgn * 0.42
    bx = cx + math.cos(base_a) * (R + 2 * ss)
    by = cy + math.sin(base_a) * (R + 2 * ss)
    tipx = bx + sgn * 18 * ss * length
    tipy = by - 30 * ss * length
    midx = bx + sgn * 6 * ss
    midy = by - 18 * ss * length
    pts = [(bx - sgn * 9 * ss, by + 2 * ss), (bx + sgn * 9 * ss, by),
           (midx + sgn * 7 * ss, midy), (tipx, tipy), (midx - sgn * 5 * ss, midy)]
    pygame.draw.polygon(canvas, col, pts)
    pygame.draw.polygon(canvas, _shade(col, 40),
                        [(bx - sgn * 9 * ss, by + 2 * ss),
                         (bx + sgn * 2 * ss, by - 6 * ss), (midx - sgn * 5 * ss, midy)])
    pygame.draw.polygon(canvas, _shade(col, -60), pts, max(2, int(2 * ss)))
    pygame.draw.circle(canvas, _shade(col, 30), (int(tipx), int(tipy)), int(4 * ss))


def _scalloped_ring(canvas, cx, cy, R, ss, *, n, col, bell_every=0,
                    bell_col=(240, 235, 200)):
    """A SCALLOPED collar framing the bezel — a ring of overlapping lobes hugging
    the metal rim (the jester's `_collar_scalloped` ported to a full circle).
    Optionally drops a small bell on every `bell_every`-th lobe (belled collar)."""
    rad = 9 * ss
    for i in range(n):
        a = i * math.tau / n - math.pi / 2
        lx = cx + math.cos(a) * (R + rad * 0.6)
        ly = cy + math.sin(a) * (R + rad * 0.6)
        pygame.draw.circle(canvas, _shade(col, -50), (int(lx), int(ly)), int(rad))
        pygame.draw.circle(canvas, col, (int(lx), int(ly)), int(rad - ss))
        pygame.draw.circle(canvas, _shade(col, 55),
                           (int(lx - rad * 0.3), int(ly - rad * 0.3)), int(rad * 0.35))
        if bell_every and i % bell_every == 0:
            bx = cx + math.cos(a) * (R + rad * 1.7)
            by = cy + math.sin(a) * (R + rad * 1.7)
            _bell(canvas, bx, by, 4 * ss, col=bell_col)


def _pointed_collar_ring(canvas, cx, cy, R, ss, *, n, col, bell_col=(240, 235, 200)):
    """A DAGGED pointed collar ring (the jester's `_collar_belled`): a fan of
    triangle points radiating off the bezel, a bell at each tip — a loud,
    festive frame for the loaded/jackpot end of the ramp."""
    for i in range(n):
        a = i * math.tau / n - math.pi / 2
        ca, sa = math.cos(a), math.sin(a)
        # Tangent for the point's base width.
        tx, ty = -sa, ca
        base_r = R + 3 * ss
        tip_r = R + 17 * ss
        b0 = (cx + ca * base_r - tx * 7 * ss, cy + sa * base_r - ty * 7 * ss)
        b1 = (cx + ca * base_r + tx * 7 * ss, cy + sa * base_r + ty * 7 * ss)
        tip = (cx + ca * tip_r, cy + sa * tip_r)
        pygame.draw.polygon(canvas, col, [b0, b1, tip])
        pygame.draw.polygon(canvas, _shade(col, 45),
                            [b0, ((b0[0] + tip[0]) / 2, (b0[1] + tip[1]) / 2), tip])
        pygame.draw.polygon(canvas, _shade(col, -60), [b0, b1, tip], max(2, int(2 * ss)))
        _bell(canvas, tip[0], tip[1], 4 * ss, col=bell_col)


def _shoulder_pom(canvas, x, y, ss, *, gold=GOLD, lobes=3):
    """A belled gold POM tuft bridging an ornament seam (the jester's
    `_shoulder_pom`) — a fan of lit lobes crowned by a cream bell, native to the
    bell/gold-accent costume language."""
    spread = (lobes - 1) / 2
    for i in range(lobes):
        s = i - spread
        lx = int(x + s * 7 * ss)
        ly = int(y + abs(s) * 3 * ss)
        pygame.draw.circle(canvas, _shade(gold, -55), (lx, ly), int(7 * ss))
        pygame.draw.circle(canvas, gold, (lx, ly), int(6 * ss))
        pygame.draw.circle(canvas, _shade(gold, 70), (lx - int(2 * ss), ly - int(2 * ss)),
                           int(2 * ss))
    _bell(canvas, x, y - 5 * ss, 4 * ss, col=(245, 240, 200))


# ── the medallion's JESTER FACE motif (embossed around / framing the disc) ───
# The naughty-face grammar from the jester kit (wide fanged grin, cocked brow,
# sidelong sly eyes) rebuilt to FRAME the cream disc: eyes ride the upper bezel
# arc and the grin rides the lower bezel arc, so the rolled NUMBER sits in the
# "mouth" of a sly clown face without any feature out-shouting it.

def _sly_eye(canvas, x, y, ss, *, look, r=7, cocked=False, glint=False,
            sclera=CREAM, pupil=(44, 38, 60)):
    """A bright sly eye glancing sidelong (toward `look`<0 = inward/left). Used
    on the bezel arc above the disc. `cocked` lifts the inner brow higher;
    `glint` swaps in a gold sidelong catch-glint for the devilish read."""
    ew, eh = int(r * 0.85), int(r)
    pygame.draw.ellipse(canvas, sclera, (x - ew, y - eh, ew * 2, eh * 2))
    pygame.draw.ellipse(canvas, _shade(sclera, -70), (x - ew, y - eh, ew * 2, eh * 2),
                        max(1, int(ss)))
    px = int(x + look)
    py = int(y + 1 * ss)
    pygame.draw.circle(canvas, pupil, (px, py), int(r * 0.55))
    pygame.draw.circle(canvas, INK, (px, py), int(r * 0.55), max(1, int(ss)))
    cl = GOLD if glint else (255, 255, 255)
    pygame.draw.circle(canvas, cl, (px - int(r * 0.3), py - int(r * 0.4)), max(1, int(r * 0.22)))
    # Happy-squint lower lid arc.
    pygame.draw.arc(canvas, _shade(sclera, -90),
                    (x - ew, y - int(ss), ew * 2, eh + int(2 * ss)),
                    math.pi * 1.1, math.tau * 0.95, max(1, int(ss)))


def _sly_brow(canvas, x, y, ss, *, sgn, cocked=False, col=(76, 56, 60), thick=1.0):
    """A raised cheeky 'oh-really' brow: inner end HIGH, outer end low — never the
    angry inner-down V. `cocked` rides the whole brow higher (one-up asymmetry)."""
    inner = (x - sgn * 3 * ss, y - 6 * ss - (4 * ss if cocked else 0))
    outer = (x + sgn * 13 * ss, y + 2 * ss)
    pygame.draw.line(canvas, col, inner, outer, max(2, int(3 * ss * thick)))


def _fanged_grin(canvas, cx, gy, ss, *, w, fang_sgn=-1, tongue=False,
                 lip_col=(188, 56, 66)):
    """The dominant mischief cue ported to bezel scale: a wide upturned OPEN grin
    with a tooth band and ONE pointed fang, riding the lower bezel arc beneath the
    disc. `fang_sgn` picks the fang side; `tongue` licks the raised corner."""
    l_corner = (cx - w, gy - 2 * ss)
    r_corner = (cx + w, gy)
    bottom = (cx, gy + 13 * ss)
    mouth = [l_corner, (cx - w * 0.45, gy + 2 * ss), (cx + w * 0.45, gy + 2 * ss),
             r_corner, (cx + w * 0.5, gy + 7 * ss), bottom, (cx - w * 0.5, gy + 7 * ss)]
    pygame.draw.polygon(canvas, MOUTH_DK, mouth)
    teeth = [l_corner, (cx - w * 0.45, gy), (cx + w * 0.45, gy), r_corner,
             (cx + w * 0.45, gy + 5 * ss), (cx - w * 0.45, gy + 5 * ss)]
    pygame.draw.polygon(canvas, (250, 248, 240), teeth)
    pygame.draw.polygon(canvas, _shade((250, 248, 240), -80), teeth, max(1, int(ss)))
    for k in range(-2, 3):
        gx = cx + k * w * 0.22
        pygame.draw.line(canvas, _shade((250, 248, 240), -80),
                         (gx, gy), (gx, gy + 5 * ss), max(1, int(ss)))
    # The single mean FANG dropping into the dark mouth.
    fx = cx + fang_sgn * w * 0.36
    fang = [(fx - 3 * ss, gy + 5 * ss), (fx + 3 * ss, gy + 5 * ss), (fx, gy + 12 * ss)]
    pygame.draw.polygon(canvas, (252, 250, 244), fang)
    pygame.draw.polygon(canvas, _shade((252, 250, 244), -80), fang, max(1, int(ss)))
    # Smooth up-curving lip crescent (parabola: corners high, centre dipped).
    lip = []
    for k in range(13):
        t = k / 12.0
        lx = (l_corner[0] - 2 * ss) + ((r_corner[0] + 2 * ss) - (l_corner[0] - 2 * ss)) * t
        ly = (l_corner[1] - 3 * ss) + ((r_corner[1] - 2 * ss) - (l_corner[1] - 3 * ss)) * t \
            + (1.0 - (2.0 * t - 1.0) ** 2) * 13 * ss
        lip.append((lx, ly))
    pygame.draw.lines(canvas, lip_col, False, lip, max(2, int(3 * ss)))
    if tongue:
        tx0 = l_corner[0]
        ty0 = gy + 4 * ss
        pygame.draw.ellipse(canvas, (228, 110, 124),
                            (tx0 - 4 * ss, ty0, 9 * ss, 7 * ss))
        pygame.draw.ellipse(canvas, _shade((228, 110, 124), -60),
                            (tx0 - 4 * ss, ty0, 9 * ss, 7 * ss), max(1, int(ss)))


# ── shared medallion shell (field, bezel, disc, specular) ────────────────────
# All five variants build on ONE shell so the family reads consistent and the
# differences are purely the jester treatment + tier loading. `tone` warms the
# field plum toward a darker bruise for the menacing end.

def _medallion_shell(canvas, c, R, ss, *, field_plum=PLUM, field_dk=PLUM_DK,
                     bezel_segs=44, fleck_n=16, disc_inner=0.74, gold_face=GOLD):
    """Plum field ring → fluted gold bezel → gold disc → cream inner field →
    clipped top-left specular crescent. Returns the cream-field radius so callers
    seat the number on its optical centre. `bezel_segs`/`fleck_n` scale the
    "loaded" read for the high-roll tier."""
    HD = canvas.get_width()
    # Plum field ring (not a flat bruise) with a gold keyline.
    field = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(field, field_plum + (235,), (c, c), int(HD * 0.42))
    pygame.draw.circle(field, GOLD + (210,), (c, c), int(HD * 0.42), max(2, int(3 * ss)))
    pygame.draw.circle(field, field_dk + (235,), (c, c), int(HD * 0.365))
    canvas.blit(field, (0, 0))
    # Festive flecks (reads "roll", not "award").
    for i in range(fleck_n):
        a = i * math.tau / fleck_n + 0.4
        dist = HD * 0.365 + (i % 3) * 6 * ss
        px = c + math.cos(a) * dist
        py = c + math.sin(a) * dist
        col = [GOLD, LIME, CREAM][i % 3]
        if i % 2 == 0:
            sz = (5 + i % 2 * 2) * ss
            d = pygame.Surface((int(sz), int(sz)), pygame.SRCALPHA)
            pygame.draw.polygon(d, col + (235,),
                                [(sz // 2, 0), (sz, sz // 2), (sz // 2, sz), (0, sz // 2)])
            d = pygame.transform.rotate(d, (i * 51) % 360)
            canvas.blit(d, d.get_rect(center=(int(px), int(py))))
        else:
            pygame.draw.circle(canvas, col, (int(px), int(py)), int(3 * ss))
    # Fluted gold bezel.
    for i in range(bezel_segs):
        a = i * math.tau / bezel_segs
        rr = R + (6 * ss if i % 2 == 0 else 2 * ss)
        pygame.draw.line(canvas, GOLD_MD,
                         (c + math.cos(a) * (R - 2 * ss), c + math.sin(a) * (R - 2 * ss)),
                         (c + math.cos(a) * rr, c + math.sin(a) * rr), max(2, int(3 * ss)))
    pygame.draw.circle(canvas, GOLD_DK, (c, c), R)
    pygame.draw.circle(canvas, gold_face, (c, c), R - 5 * ss)
    # Cream inner field — the number's home.
    cr = int(R * disc_inner)
    pygame.draw.circle(canvas, (255, 244, 212), (c, c), cr)
    pygame.draw.circle(canvas, PLUM, (c, c), cr, max(2, int(2 * ss)))
    # Clipped top-left specular crescent.
    hl = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(hl, (255, 255, 255, 90), (c - int(R * 0.32), c - int(R * 0.32)),
                       int(R * 0.55))
    mask = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (c, c), R - 8 * ss)
    hl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    canvas.blit(hl, (0, 0))
    return cr


def _ribbon_banderole(canvas, c, cy, txt, ss, *, plate_col=PLUM, text_col=CREAM,
                      edge_col=PLUM_DK, size=20, curve=True):
    """The label relocated OFF the disc onto a curved banderole hugging the bezel
    bottom, so the rolled NUMBER can own the disc centre. A shallow plum ribbon
    with notched ends + a gold keyline + tracked cream lettering."""
    lf = hud._font(int(size * ss), True)
    spaced = " ".join(txt)
    lab = lf.render(spaced, True, text_col)
    pw = lab.get_width() + int(34 * ss)
    ph = lab.get_height() + int(12 * ss)
    rib = pygame.Surface((pw, ph), pygame.SRCALPHA)
    notch = int(ph * 0.5)
    body = [(notch, 0), (pw - notch, 0), (pw, ph // 2), (pw - notch, ph),
            (notch, ph), (0, ph // 2)]
    pygame.draw.polygon(rib, plate_col, body)
    pygame.draw.polygon(rib, GOLD, body, max(1, int(2 * ss)))
    edge = lf.render(spaced, True, edge_col)
    cxp, cyp = pw // 2, ph // 2
    for ox, oy in ((-ss, 0), (ss, 0), (0, -ss), (0, ss)):
        rib.blit(edge, edge.get_rect(center=(cxp + ox, cyp + oy)))
    rib.blit(lab, lab.get_rect(center=(cxp, cyp)))
    # Folded ribbon tails behind the notched ends for the banderole read.
    for sgn in (-1, 1):
        tx = c + sgn * (pw // 2 - int(4 * ss))
        tail = [(tx, cy - int(ph * 0.3)), (tx + sgn * int(16 * ss), cy - int(ph * 0.5)),
                (tx + sgn * int(13 * ss), cy), (tx + sgn * int(16 * ss), cy + int(ph * 0.5)),
                (tx, cy + int(ph * 0.3))]
        pygame.draw.polygon(canvas, _shade(plate_col, -30), tail)
    canvas.blit(rib, rib.get_rect(center=(c, cy)))


# ── the five jester medallion variants ───────────────────────────────────────
# NUMBER CENTRING (all five): the base anchored N at c-12*ss (12px ABOVE disc
# centre) to clear the PAGODAS plate below. Every variant here drops that anchor
# to ~c-3*ss (the cream field's optical centre, allowing for the bold font's
# baseline sitting low) and relocates the label onto a banderole / shrinks it, so
# N reads dead-centre on the disc and stays the dominant hero.

NCTR = lambda ss: -int(3 * ss)  # optical-centre anchor for the bold number  # noqa: E731


def var_cheeky(roll, ss):
    """CHEEKY — the friendliest mischief. A sly winking grin with a tongue-tip
    and a ring of dangling jester BELLS round the bezel. Brightest, most playful;
    the safe end of "a bit mean" — a wink, not a threat. Shown at a LOW roll."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)
    R = int(HD * 0.315)
    cr = _medallion_shell(canvas, c, R, ss)

    # Dangling bells fringing the lower 2/3 of the bezel (skip the very top where
    # the number's head-room is, and skip the bottom where the banderole sits).
    for i in range(12):
        a = i * math.tau / 12 - math.pi / 2
        if math.sin(a) < -0.55 or abs(math.cos(a)) < 0.18 and math.sin(a) > 0.6:
            continue
        _dangler(canvas, c, c, a, R + 6 * ss, ss, length=14 * ss, bell_r=5 * ss)

    # Sly eyes peeking over the top of the disc, glancing inward; a winking pair.
    ey = c - int(cr * 0.72)
    for sgn in (-1, 1):
        ex = c + sgn * int(cr * 0.52)
        if sgn < 0:  # the wink — a closed happy arc instead of an open eye
            pygame.draw.arc(canvas, INK, (ex - 7 * ss, ey - 4 * ss, 14 * ss, 10 * ss),
                            math.pi * 1.05, math.tau * 0.95, max(2, int(3 * ss)))
        else:
            _sly_eye(canvas, ex, ey, ss, look=-int(2 * ss), r=int(6 * ss))
        _sly_brow(canvas, ex, ey - int(9 * ss), ss, sgn=sgn)

    # Number dead-centre on the cream disc.
    _num_block(canvas, c, c + NCTR(ss), roll, ss, size=92,
               num_col=PLUM, edge_col=CREAM, edge_w=4)

    # Tongue-tipped grin riding the lower bezel arc, beneath the disc.
    _fanged_grin(canvas, c, c + int(cr * 0.78), ss, w=int(cr * 0.36), tongue=True)

    # Shrunk label on a banderole hugging the bezel bottom.
    _ribbon_banderole(canvas, c, c + R + int(13 * ss), "PAGODAS", ss, size=17)
    return canvas, D


def var_devilish(roll, ss):
    """DEVILISH — imp HORNS crest the medallion, a fanged grin and glinting
    sidelong GOLD eyes. Cocked brow for the up-to-no-good asymmetry. Mid-warm,
    clearly a little devil but still grinning. Shown at a mid HIGH roll."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)
    R = int(HD * 0.315)
    cr = _medallion_shell(canvas, c, R, ss, bezel_segs=48)

    # Soft imp horns cresting the top of the bezel.
    _imp_horn(canvas, c, c, R, ss, sgn=-1, col=PLUM_DK)
    _imp_horn(canvas, c, c, R, ss, sgn=1, col=PLUM_DK)

    # A few danglers low + sides for festivity without crowding the horns.
    for i in range(10):
        a = i * math.tau / 10 - math.pi / 2
        if math.sin(a) < 0.1:
            continue
        _dangler(canvas, c, c, a, R + 6 * ss, ss, length=12 * ss, bell_r=4 * ss)

    # Glinting gold sidelong eyes + one cocked brow.
    ey = c - int(cr * 0.72)
    for sgn in (-1, 1):
        ex = c + sgn * int(cr * 0.52)
        _sly_eye(canvas, ex, ey, ss, look=-int(2 * ss), r=int(6 * ss), glint=True)
        _sly_brow(canvas, ex, ey - int(9 * ss), ss, sgn=sgn, cocked=(sgn < 0))

    _num_block(canvas, c, c + NCTR(ss), roll, ss, size=92,
               num_col=PLUM, edge_col=CREAM, edge_w=4)

    _fanged_grin(canvas, c, c + int(cr * 0.78), ss, w=int(cr * 0.38))
    _ribbon_banderole(canvas, c, c + R + int(13 * ss), "PAGODAS", ss, size=17)
    return canvas, D


def var_menacing(roll, ss):
    """MENACING-LEANING — the far edge of "a bit mean": a DARKER plum field, a
    SHARPER pointed-collar crest, a tighter fanged grin and harder cocked brows.
    Still a clown (bells, gold), but the coldest, sliest read so the AD can call
    whether it's too far for an upbeat moment. Shown at a high roll."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)
    R = int(HD * 0.315)
    # Darker bruise field + a desaturated gold face for the colder metal.
    cr = _medallion_shell(canvas, c, R, ss, field_plum=(70, 30, 118),
                          field_dk=(46, 18, 84), bezel_segs=52,
                          gold_face=_shade(GOLD, -18))

    # Sharper pointed (dagged) collar crest — the loud, slightly threatening ring.
    _pointed_collar_ring(canvas, c, c, R, ss, n=22, col=_shade(GOLD, -10))

    # Harder, narrower eyes with a deeper sidelong shove; both brows cocked low-out.
    ey = c - int(cr * 0.72)
    for sgn in (-1, 1):
        ex = c + sgn * int(cr * 0.52)
        _sly_eye(canvas, ex, ey, ss, look=-int(3 * ss), r=int(5.5 * ss), glint=True,
                 pupil=(30, 24, 46))
        _sly_brow(canvas, ex, ey - int(9 * ss), ss, sgn=sgn, cocked=True,
                  col=(58, 40, 46), thick=1.15)

    _num_block(canvas, c, c + NCTR(ss), roll, ss, size=92,
               num_col=PLUM, edge_col=CREAM, edge_w=4)

    # Tighter, meaner grin (narrower, longer fang reach).
    _fanged_grin(canvas, c, c + int(cr * 0.80), ss, w=int(cr * 0.34), fang_sgn=1)
    _ribbon_banderole(canvas, c, c + R + int(13 * ss), "PAGODAS", ss, size=17,
                      plate_col=(70, 30, 118))
    return canvas, D


# ── the escalating-tier pair (SAME design language, low vs jackpot) ──────────
# Two cells in ONE language — a "Belled Imp" — so the reward ramp reads: a
# PLAINER low roll vs a LOADED jackpot. The jackpot gets denser bells, a brighter
# belled-scallop crest, more flecks/bezel flutes, shoulder poms bridging the
# seams, and a "JACKPOT" banderole instead of "PAGODAS".

def _belled_imp(roll, ss, *, tier):
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)
    R = int(HD * 0.315)
    loaded = tier == "jackpot"
    cr = _medallion_shell(canvas, c, R, ss,
                          bezel_segs=56 if loaded else 40,
                          fleck_n=24 if loaded else 12)

    # Crest: a scalloped collar ring, belled densely on the jackpot, sparse on low.
    _scalloped_ring(canvas, c, c, R, ss, n=24 if loaded else 16,
                    col=_shade(GOLD, 4) if loaded else _shade(LIME, 6),
                    bell_every=2 if loaded else 6)

    # Soft imp horns on both; only the jackpot gets gold poms bridging the
    # horn/crest seam.
    _imp_horn(canvas, c, c, R, ss, sgn=-1, col=PLUM, length=1.1 if loaded else 0.85)
    _imp_horn(canvas, c, c, R, ss, sgn=1, col=PLUM, length=1.1 if loaded else 0.85)
    if loaded:
        for sgn in (-1, 1):
            ax = c + sgn * int(R * 0.34)
            ay = c - int(R * 0.86)
            _shoulder_pom(canvas, ax, ay, ss)

    # Eyes + brow: plainer on low (no glint, gentle brow), loaded on jackpot
    # (gold glint, one cocked brow — the face "reacts" bigger to the big roll).
    ey = c - int(cr * 0.72)
    for sgn in (-1, 1):
        ex = c + sgn * int(cr * 0.52)
        _sly_eye(canvas, ex, ey, ss, look=-int(2 * ss), r=int(6 * ss), glint=loaded)
        _sly_brow(canvas, ex, ey - int(9 * ss), ss, sgn=sgn, cocked=(loaded and sgn < 0))

    _num_block(canvas, c, c + NCTR(ss), roll, ss, size=92,
               num_col=PLUM, edge_col=CREAM, edge_w=4)

    # The grin grows + gains a tongue on the jackpot (the payoff reaction).
    _fanged_grin(canvas, c, c + int(cr * 0.78), ss,
                 w=int(cr * (0.40 if loaded else 0.32)), tongue=loaded)

    # Star toppers crowning the jackpot for the payoff flourish.
    if loaded:
        for sgn in (-1, 1):
            _star(canvas, c + sgn * int(R * 0.62), c - int(R * 0.62), int(11 * ss),
                  GOLD, PLUM, ss)

    label = "JACKPOT" if loaded else "PAGODAS"
    _ribbon_banderole(canvas, c, c + R + int(13 * ss), label, ss,
                      size=17 if loaded else 16,
                      plate_col=PLUM if loaded else _shade(PLUM, 8))
    return canvas, D


def var_imp_low(roll, ss):
    """ESCALATION (LOW) — the Belled Imp at a plain low roll: sparse crest bells,
    short horns, thinner bezel + fewer flecks, gentle grin, no glint, PAGODAS."""
    return _belled_imp(roll, ss, tier="low")


def var_imp_jackpot(roll, ss):
    """ESCALATION (JACKPOT 25) — the SAME Belled Imp loaded for the payoff: dense
    belled crest, taller horns + shoulder poms, denser bezel/flecks, a wider
    tongue-out grin, gold star toppers, a JACKPOT banderole. The reward ramp."""
    return _belled_imp(roll, ss, tier="jackpot")


VARIANTS = [
    ("1  CHEEKY — wink + bell fringe", "sly wink, tongue grin, dangling bells", "day",
     var_cheeky, 11),
    ("2  DEVILISH — imp horns + glint", "imp horns, gold-glint eyes, cocked brow, fang", "day",
     var_devilish, 19),
    ("3  MENACING — dark + dagged crest", "dark plum, pointed collar, hard brows, fang", "day",
     var_menacing, 22),
    ("4  BELLED IMP — LOW (ramp)", "plain: sparse bells, short horns, gentle grin", "day",
     var_imp_low, 14),
    ("5  BELLED IMP — JACKPOT (ramp)", "loaded: dense bells, poms, stars, tongue grin", "day",
     var_imp_jackpot, 25),
]


def main():
    SS = 4
    TRUE = 264
    INSET = 116
    cols = 3
    rows = 2
    pad = 20
    head = 78
    tile_w = TRUE + INSET + 40
    tile_h = TRUE + 96
    sheet_w = cols * tile_w + (cols + 1) * pad
    sheet_h = head + rows * tile_h + (rows + 1) * pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 34, 42))

    title_f = hud._font(30, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(
        "RARE Dice Medallion — Jester/Clown takes (Round 1): N recentred on the cream disc",
        True, (255, 255, 255)), (pad, 12))
    sheet.blit(sub_f.render(
        "True 264px on day sky + actual-size inset. Mischief spans cheeky -> devilish -> "
        "menacing; cells 4/5 = SAME language at a LOW vs JACKPOT roll (reward ramp).",
        True, (200, 205, 215)), (pad, 40))
    sheet.blit(sub_f.render(
        "Number anchored at the cream-field optical centre; label moved onto a curved "
        "banderole hugging the bezel bottom.",
        True, (170, 178, 190)), (pad, 58))

    label_f = hud._font(18, True)
    samp_f = hud._font(13, True)

    for idx, (name, desc, sky, fn, roll) in enumerate(VARIANTS):
        col = idx % cols
        row = idx // cols
        tx = pad + col * (tile_w + pad)
        ty = head + pad + row * (tile_h + pad)

        if sky == "night":
            tile = sky_tile(tile_w, tile_h, NIGHT_TOP, NIGHT_BOT, lo=0.10, hi=0.55)
            chip_top, chip_bot, chip_lo, chip_hi = NIGHT_TOP, NIGHT_BOT, 0.10, 0.55
        else:
            tile = sky_tile(tile_w, tile_h)
            chip_top, chip_bot, chip_lo, chip_hi = SKY_TOP, SKY_BOT, 0.35, 0.80
        canvas, D = fn(roll, SS)

        out = pygame.transform.smoothscale(canvas, (TRUE, TRUE))
        tile.blit(out, out.get_rect(center=(16 + TRUE // 2, 36 + TRUE // 2)))

        chip = sky_tile(INSET + 16, INSET + 16, chip_top, chip_bot, chip_lo, chip_hi)
        ins = pygame.transform.smoothscale(canvas, (INSET, INSET))
        chip.blit(ins, ins.get_rect(center=((INSET + 16) // 2, (INSET + 16) // 2)))
        pygame.draw.rect(chip, (255, 255, 255), chip.get_rect(), 2)
        cr = chip.get_rect()
        cr.bottomright = (tile_w - 8, tile_h - 34)
        tile.blit(chip, cr)
        ilab = samp_f.render("actual size", True, (255, 255, 255))
        ib = pygame.Surface((ilab.get_width() + 6, ilab.get_height() + 2),
                            pygame.SRCALPHA)
        ib.fill((20, 22, 28, 200))
        ib.blit(ilab, (3, 1))
        tile.blit(ib, (cr.left, cr.top - ib.get_height() - 1))

        strip = pygame.Surface((tile_w, 30), pygame.SRCALPHA)
        strip.fill((20, 22, 28, 205))
        tile.blit(strip, (0, 0))
        tile.blit(label_f.render(name, True, LIME), (8, 6))
        cap = pygame.Surface((tile_w, 24), pygame.SRCALPHA)
        cap.fill((20, 22, 28, 205))
        tile.blit(cap, (0, tile_h - 24))
        tile.blit(samp_f.render(f"{desc}  (roll {roll})", True, (220, 225, 235)),
                  (8, tile_h - 21))
        sheet.blit(tile, (tx, ty))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "dice_results", "medallion")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
