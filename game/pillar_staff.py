"""Carousel Barker jester-staff pillar art.

A fairground-barker scepter ported from the look-dev tool: a plum/gold
barber-twist shaft spiralling up to a grinning mini-clown under a four-point
cap, jewelled gold ferrule collars and a flared bell foot. Drawn dark-cored so
the silhouette holds value against the day sky. The staff carries its own fixed
jester palette rather than the biome palette so the cartoon read stays loud."""

import math

import pygame

from game.draw import _shade_c, lerp_color  # noqa: F401  (lerp_color kept for parity)
from game.config import PIPE_W

# Guards may spill this far past the 58-px column on each side.
OVERHANG = 12

# Plum & Lime clown world palette (so the staff ties to the hero clown).
PLUM = (96, 44, 150)
PLUM_DK = (66, 28, 110)
LIME = (132, 218, 116)
LIME_DK = (74, 150, 70)
GOLD = (250, 205, 72)
GOLD_HI = (255, 236, 150)
GOLD_DK = (176, 130, 30)
GOLD_SHADOW = (110, 78, 22)
CREAM = (255, 248, 224)
INK = (28, 22, 30)

# Warm clown-face inks ported from the hero recipe (render_jester_variants).
FACE_SHADOW = (212, 198, 168)          # cream head keyline / under-shade
EYE_WHITE = (252, 250, 244)
EYE_PUPIL = (44, 38, 60)
EYE_PUPIL_DK = (14, 12, 22)
BROW_COL = (76, 56, 60)                # soft warm brow (never heavy black)
NOSE_RED = (232, 72, 72)
MOUTH_THROAT = (120, 30, 42)
TEETH = (250, 248, 240)
LIP = (188, 56, 66)
TONGUE = (228, 110, 124)
CHEEK = (255, 150, 150)
DEAD_EYE = (196, 30, 44)               # the blank-stare "mean" variant's pinprick


def _box(H, ss):
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(H)) * ss
    return pygame.Surface((bw, bh), pygame.SRCALPHA), bw, bh


def _mini_clown_face(surf, cx, hy, hr, ss, *, expr="grin", look=None):
    """The hero clown's HAPPY-but-MEAN expression ported into ss-scaled marotte
    space: a cream head, bright open eyes glancing sidelong, lifted SLY brows,
    a warm ball nose, and a wide upturned OPEN grin with a tooth row + one fang.
    `expr` flavours the mouth — "grin" (base), "tongue" (tongue-tip licking the
    corner), or "stare" (the dead-eyed, blank-stare 'mean' read). All geometry
    keys off `hr` so it scales with the bauble, never the clown's fixed 1x grid."""
    # `u` is the DIMENSIONLESS head scale vs the round-6 head (hr already carries
    # the ss factor), so `u * ss` below yields proper supersampled pixels — the
    # face never double-scales by ss.
    u = hr / (11.0 * ss)
    look = (-2.0 * u * ss) if look is None else look
    # Cream head with a soft under-shade keyline (the clown's round face).
    pygame.draw.circle(surf, FACE_SHADOW, (cx, int(hy)), hr)
    pygame.draw.circle(surf, CREAM, (cx, int(hy)), int(hr - ss))
    # Warm cheek flush low + outward on the apple so it reads charming, not a tear.
    for s in (-1, 1):
        blush = pygame.Surface((int(7 * u * ss), int(5 * u * ss)), pygame.SRCALPHA)
        pygame.draw.ellipse(blush, (*CHEEK, 120), blush.get_rect())
        surf.blit(blush, (int(cx + s * hr * 0.46 - 3.5 * u * ss),
                          int(hy + hr * 0.28)))
    ex = hr * 0.42                         # eye spacing
    ew, eh = 2.0 * u, 2.5 * u              # tall round OPEN eye (alive, not hooded)
    # "smirk" shares the dead pinprick eyes with "stare" but carries a sly raised
    # brow + a one-corner-up closed mouth so it reads as a mischievous clown, not an
    # empty doll. `dead` drives the eye treatment; the mouth branch splits below.
    smirk = expr == "smirk"
    stare = expr == "stare" or smirk
    for s in (-1, 1):
        exx = cx + s * ex
        # White sclera — a tall bright open eye.
        rect = pygame.Rect(int(exx - ew * ss), int(hy - eh * ss + ss),
                           int(ew * 2 * ss), int(eh * 2 * ss))
        pygame.draw.ellipse(surf, EYE_WHITE, rect)
        if stare:
            # The 'mean' read: tiny dead pinprick pupils dead-centre — a vacant,
            # unsettling stare instead of the gleeful sidelong glance.
            pygame.draw.circle(surf, DEAD_EYE, (int(exx), int(hy + ss)),
                               max(1, int(1.4 * u * ss)))
            pygame.draw.circle(surf, EYE_PUPIL_DK, (int(exx), int(hy + ss)),
                               max(1, int(1.4 * u * ss)), max(1, int(ss)))
        else:
            px = exx + look
            py = hy + 0.6 * u * ss
            pr = max(2, int(2.0 * u * ss))
            pygame.draw.circle(surf, EYE_PUPIL, (int(px), int(py)), pr)
            pygame.draw.circle(surf, EYE_PUPIL_DK, (int(px), int(py)), pr, max(1, int(ss)))
            pygame.draw.circle(surf, (255, 255, 255),
                               (int(px - 0.7 * u * ss), int(py - 1.0 * u * ss)),
                               max(1, int(0.7 * u * ss)))
        # Thin LIGHT upper lid arched UP (a happy lifted lid), never a hooded bar.
        pygame.draw.arc(surf, INK, (int(exx - ew * ss - ss), int(hy - eh * ss),
                                    int(ew * 2 * ss + 2 * ss), int(eh * ss + 2 * ss)),
                        math.pi * 0.15, math.pi * 0.85, max(1, int(1.4 * ss)))
        # SLY raised brow — inner (nose-side) end HIGH, outer end lower, bowed up
        # at the mid: a lifted "oh-really" arch that can never knit into the angry
        # inner-down V. Drawn as a thin 3-point polyline so it reads arched, not a
        # heavy flat bar.
        inner = (exx - s * 1.0 * u * ss, hy - 5.4 * u * ss)
        mid = (exx + s * 1.8 * u * ss, hy - 5.6 * u * ss)
        outer = (exx + s * 4.6 * u * ss, hy - 3.6 * u * ss)
        if stare and not smirk:
            # A flatter, lower brow for the blank-stare so the calm reads colder.
            inner = (exx - s * 1.0 * u * ss, hy - 4.6 * u * ss)
            mid = (exx + s * 1.8 * u * ss, hy - 4.6 * u * ss)
            outer = (exx + s * 4.6 * u * ss, hy - 4.4 * u * ss)
        elif smirk:
            # ONE sly raised brow (the die-side / LEFT, s == -1) cocks up high; the
            # other stays flat + low — a single cocked brow over dead eyes is the
            # whole "knowing menace-glee" tell of the sinister smirk.
            if s < 0:
                inner = (exx - s * 1.0 * u * ss, hy - 6.4 * u * ss)
                mid = (exx + s * 1.8 * u * ss, hy - 6.8 * u * ss)
                outer = (exx + s * 4.6 * u * ss, hy - 5.0 * u * ss)
            else:
                inner = (exx - s * 1.0 * u * ss, hy - 4.4 * u * ss)
                mid = (exx + s * 1.8 * u * ss, hy - 4.4 * u * ss)
                outer = (exx + s * 4.6 * u * ss, hy - 4.4 * u * ss)
        pygame.draw.lines(surf, BROW_COL, False,
                          [(int(inner[0]), int(inner[1])), (int(mid[0]), int(mid[1])),
                           (int(outer[0]), int(outer[1]))], max(1, int(1.3 * ss)))
    # Red ball nose, lifted up between the eyes so the grin owns the lower face.
    # Bumped up again so the warm dot is the last face cue to survive at 30px, where
    # the eyes/brows dissolve and only "warm nose over dark smile" reads — the dot
    # has to win the silhouette fight against the cap clutter above it.
    nr = max(3, int(3.0 * u * ss))
    pygame.draw.circle(surf, _shade_c(NOSE_RED, -60), (cx, int(hy + 1.4 * u * ss)), nr + 1)
    pygame.draw.circle(surf, NOSE_RED, (cx, int(hy + 1.4 * u * ss)), nr)
    pygame.draw.circle(surf, _shade_c(NOSE_RED, 100),
                       (int(cx - nr * 0.4), int(hy + 1.4 * u * ss - nr * 0.4)),
                       max(1, int(nr * 0.4)))
    if smirk:
        # A closed-mouth SMIRK: a smooth lip curve with the die-side (LEFT) corner
        # cocked UP and the other corner held low — a sliver of menace-glee so the
        # dead eyes read as a sly clown, not a vacant doll. A short dimple tick seats
        # the raised corner so the asymmetry survives shrinking.
        my = hy + 5.0 * u * ss
        l_up = (cx - 4.2 * u * ss, my - 1.8 * u * ss)
        r_lo = (cx + 4.2 * u * ss, my + 1.2 * u * ss)
        smk = []
        for k in range(11):
            t = k / 10.0
            sx = l_up[0] + (r_lo[0] - l_up[0]) * t
            sy = l_up[1] + (r_lo[1] - l_up[1]) * t + (1.0 - (2.0 * t - 1.0) ** 2) * 1.2 * u * ss
            smk.append((int(sx), int(sy)))
        pygame.draw.lines(surf, LIP, False, smk, max(2, int(2.2 * ss)))
        pygame.draw.line(surf, _shade_c(LIP, -40),
                         (int(l_up[0]), int(l_up[1])),
                         (int(l_up[0] + 1.2 * u * ss), int(l_up[1] - 1.6 * u * ss)),
                         max(1, int(1.4 * ss)))
        return
    if stare:
        # A small flat closed line-mouth for the unsettling calm — no toothy grin.
        my = hy + 5.4 * u * ss
        pygame.draw.line(surf, LIP, (int(cx - 4.0 * u * ss), int(my)),
                         (int(cx + 4.0 * u * ss), int(my)), max(2, int(2.0 * ss)))
        pygame.draw.line(surf, _shade_c(LIP, -30),
                         (int(cx - 2.0 * u * ss), int(my + 1.6 * u * ss)),
                         (int(cx + 2.0 * u * ss), int(my + 1.6 * u * ss)), max(1, int(ss)))
        return
    # THE DOMINANT FEATURE: a WIDE OPEN happy grin, die-side (LEFT) corner highest
    # so it stays lopsided/sly, with a tooth row + one pointed fang for the edge.
    mw = 5.0 * u * ss
    my = hy + 4.6 * u * ss
    l_corner = (cx - mw - 0.6 * u * ss, my - 1.0 * u * ss)
    r_corner = (cx + mw, my)
    bottom = (cx, my + 3.6 * u * ss)
    mouth = [l_corner, (cx - 2.3 * u * ss, my + 0.5 * u * ss),
             (cx + 2.3 * u * ss, my + 0.5 * u * ss), r_corner,
             (cx + 2.7 * u * ss, my + 1.8 * u * ss), bottom,
             (cx - 2.7 * u * ss, my + 1.8 * u * ss)]
    # Throat darkened one step so the open grin reads as a solid dark smile-band
    # at route scale (the "dark smile under a warm dot" cue) once the teeth blur.
    pygame.draw.polygon(surf, _shade_c(MOUTH_THROAT, -34),
                        [(int(p[0]), int(p[1])) for p in mouth])
    # Bright tooth band across the top of the open grin + tooth separators.
    teeth = [l_corner, (cx - 2.3 * u * ss, my), (cx + 2.3 * u * ss, my), r_corner,
             (cx + 2.3 * u * ss, my + 1.4 * u * ss), (cx - 2.3 * u * ss, my + 1.4 * u * ss)]
    pygame.draw.polygon(surf, TEETH, [(int(p[0]), int(p[1])) for p in teeth])
    pygame.draw.polygon(surf, _shade_c(TEETH, -70),
                        [(int(p[0]), int(p[1])) for p in teeth], max(1, int(ss)))
    for k in range(-2, 3):
        gx = cx + k * 1.9 * u * ss
        pygame.draw.line(surf, _shade_c(TEETH, -70), (int(gx), int(my)),
                         (int(gx), int(my + 1.4 * u * ss)), max(1, int(ss)))
    # One pointed FANG dropping below the tooth row on the die-side (LEFT). It is the
    # MVP of the "mean" read and the FIRST thing to vanish when shrunk, so it is now
    # seated HIGH into the tooth band (base up at the tooth-band top) with a wider
    # base and a longer drop — a fat triangular spike that reads as a single dark-
    # rimmed tusk even after the tooth separators blur. Drawn against the dark throat
    # FIRST as a fat throat wedge so the fang silhouette persists, then the bright
    # tooth fang over it with a heavy keyline.
    fang = [(cx - 3.4 * u * ss, my), (cx + 0.2 * u * ss, my),
            (cx - 1.6 * u * ss, my + 4.8 * u * ss)]
    pygame.draw.polygon(surf, _shade_c(MOUTH_THROAT, -34),
                        [(int(p[0] - 0.5 * u * ss), int(p[1] + 0.6 * u * ss)) for p in fang])
    pygame.draw.polygon(surf, TEETH, [(int(p[0]), int(p[1])) for p in fang])
    pygame.draw.polygon(surf, _shade_c(TEETH, -70),
                        [(int(p[0]), int(p[1])) for p in fang], max(2, int(1.6 * ss)))
    # The lip line wrapping the grin — a single smooth up-curving crescent.
    lip = []
    for k in range(13):
        t = k / 12.0
        lx = (l_corner[0] - 1.0 * u * ss) + ((r_corner[0] + 1.0 * u * ss)
                                             - (l_corner[0] - 1.0 * u * ss)) * t
        ly = (l_corner[1] - 1.4 * u * ss) + ((r_corner[1] - 1.0 * u * ss)
                                             - (l_corner[1] - 1.4 * u * ss)) * t \
            + (1.0 - (2.0 * t - 1.0) ** 2) * 4.2 * u * ss
        lip.append((int(lx), int(ly)))
    pygame.draw.lines(surf, LIP, False, lip, max(2, int(1.6 * ss)))
    if expr == "tongue":
        # A small tongue-tip licking the raised (die-side) grin corner.
        tr = pygame.Rect(int(l_corner[0] - 1.0 * u * ss), int(my + 1.0 * u * ss),
                         int(3.0 * u * ss), int(2.6 * u * ss))
        pygame.draw.ellipse(surf, TONGUE, tr)
        pygame.draw.ellipse(surf, _shade_c(TONGUE, -60), tr, max(1, int(ss)))


def _marotte_ruff(surf, cx, ny, r, ss, col, *, lobes=9, bell_col=GOLD, fringe=None):
    """A scalloped ruff under the bauble (the clown's neck collar), ported into
    ss space: a row of overlapping lit lobes ringing the neck with a small bell
    dangling at each outer edge, so the mini-clown reads as a costumed head, not
    a bare ball. Drawn dark-cored so it holds value on the day sky. `fringe` (a
    gold) hangs a fat bell off the bottom of each lobe — the jingle density moved
    to the collar so it can't blur the head silhouette into a halo."""
    for i in range(lobes):
        t = i / (lobes - 1)
        lx = cx - r + 2 * r * t
        ly = ny + 2.0 * ss + math.sin(t * math.pi) * -2.0 * ss
        rad = max(3, int(r * 0.30))
        if fringe is not None:
            # A short thread + fat bell hanging off the lobe's lower edge — a tidy
            # belled fringe along the collar reads as "jingles" at any scale.
            by = ly + rad + int(4 * ss)
            pygame.draw.line(surf, _shade_c(fringe, -60), (int(lx), int(ly + rad)),
                             (int(lx), int(by)), max(2, int(2.0 * ss)))
            pygame.draw.circle(surf, _shade_c(fringe, -55), (int(lx), int(by)), max(3, int(3.6 * ss)))
            pygame.draw.circle(surf, fringe, (int(lx), int(by)), max(2, int(2.8 * ss)))
            pygame.draw.circle(surf, _shade_c(fringe, 80),
                               (int(lx - ss), int(by - ss)), max(1, int(1.2 * ss)))
        pygame.draw.circle(surf, _shade_c(col, -55), (int(lx), int(ly)), rad)
        pygame.draw.circle(surf, col, (int(lx), int(ly)), max(2, rad - int(ss)))
        pygame.draw.circle(surf, _shade_c(col, 55),
                           (int(lx - rad * 0.3), int(ly - rad * 0.3)),
                           max(1, int(rad * 0.34)))
    for s in (-1, 1):
        bx, by = int(cx + s * (r + 1.5 * ss)), int(ny + 4 * ss)
        pygame.draw.circle(surf, _shade_c(bell_col, -55), (bx, by), max(2, int(3 * ss)))
        pygame.draw.circle(surf, bell_col, (bx, by), max(2, int(2.4 * ss)))
        pygame.draw.circle(surf, _shade_c(bell_col, 80),
                           (int(bx - ss), int(by - ss)), max(1, int(ss)))


def _shaft_outline(surf, cx, top_y, bot_y, hw, ss, lo, *, taper=0.0):
    """The dark shaft mass + a hard keyline. `taper` pinches the foot so the
    scepter narrows toward the pommel for a finished, balanced read. Returns the
    left/right edge point lists so an ornament can ride the (possibly tapered)
    body without recomputing the silhouette."""
    span = max(1, bot_y - top_y)
    left, right = [], []
    n = 18
    for i in range(n + 1):
        t = i / n
        y = top_y + span * t
        w = hw * (1.0 - taper * t)
        left.append((cx - w, y))
        right.append((cx + w, y))
    body = left + list(reversed(right))
    pygame.draw.polygon(surf, lo, [(int(p[0]), int(p[1])) for p in body])
    pygame.draw.polygon(surf, _shade_c(lo, -45),
                        [(int(p[0]), int(p[1])) for p in body], max(2, int(2.0 * ss)))
    return left, right


def _shaft_twist(surf, cx, top_y, bot_y, hw, ss, col_a, col_b, lo):
    """A BARBER-POLE twist: bold diagonal plum/gold ribbons spiralling up a dark
    pole, clipped to the column so the stripes stay inside the body. The carousel-
    barker shaft."""
    left, right = _shaft_outline(surf, cx, top_y, bot_y, hw, ss, lo)
    clip = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    stripe = max(4, int(7 * ss))
    n = int((bot_y - top_y) / stripe) + 4
    # A 4-band cycle (plum x3, gold x1) so the dark plum dominates ~3:1 and the gold
    # ribbon reads as a bold spiral accent — the old 2:1 strobed/flickered at
    # distance, and the wider plum keeps the route median dark.
    for i in range(-2, n):
        y0 = top_y + i * stripe
        c = col_b if i % 4 == 3 else col_a
        quad = [(cx - hw, y0), (cx + hw, y0 - hw * 1.5),
                (cx + hw, y0 - hw * 1.5 + stripe), (cx - hw, y0 + stripe)]
        pygame.draw.polygon(clip, c, [(int(p[0]), int(p[1])) for p in quad])
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    body = left + list(reversed(right))
    pygame.draw.polygon(mask, (255, 255, 255, 255), [(int(p[0]), int(p[1])) for p in body])
    clip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(clip, (0, 0))
    # A slim lit rail down the lit side reads the pole as round, not flat.
    pygame.draw.line(surf, _shade_c(col_a, 50), (int(cx - hw * 0.45), int(top_y)),
                     (int(cx - hw * 0.45), int(bot_y)), max(1, int(1.4 * ss)))
    pygame.draw.polygon(surf, _shade_c(lo, -45),
                        [(int(p[0]), int(p[1])) for p in body], max(2, int(2.0 * ss)))


def _ferrule(surf, cx, y, hw, ss, col, *, h=8, jewel=None):
    """A rich banded ferrule ring round the shaft: a dark base bead, a lit gold
    rim, an engraved mid-line — far richer than the old two thin lines. Optional
    `jewel` colour sets a centred cabochon for a jewelled collar."""
    hh = int(h * ss)
    over = int(2.0 * ss)
    pygame.draw.rect(surf, _shade_c(col, -45),
                     (int(cx - hw - over), int(y - hh * 0.5), int((hw + over) * 2), hh))
    pygame.draw.rect(surf, col,
                     (int(cx - hw - over), int(y - hh * 0.5), int((hw + over) * 2), hh),
                     max(1, int(1.4 * ss)))
    pygame.draw.line(surf, _shade_c(col, 70), (int(cx - hw - over), int(y - hh * 0.28)),
                     (int(cx + hw + over), int(y - hh * 0.28)), max(1, int(1.4 * ss)))
    pygame.draw.line(surf, _shade_c(col, -70), (int(cx - hw - over), int(y + hh * 0.28)),
                     (int(cx + hw + over), int(y + hh * 0.28)), max(1, int(ss)))
    if jewel is not None:
        jr = max(2, int(hh * 0.36))
        pygame.draw.circle(surf, _shade_c(jewel, -50), (cx, int(y)), jr + 1)
        pygame.draw.circle(surf, jewel, (cx, int(y)), jr)
        pygame.draw.circle(surf, _shade_c(jewel, 90),
                           (int(cx - jr * 0.3), int(y - jr * 0.3)), max(1, int(jr * 0.4)))


def _pommel_finial(surf, cx, bot_y, hw, ss, col, *, kind="ball", gem=None, bead=True):
    """A finished finial/pommel at the foot so the staff reads as a real scepter
    butt, not a sawn-off pole. `kind` picks the silhouette: a knobbed "ball", a
    spike-tipped "spike", or a flared collared "bell". `bead` adds the small
    collar bead above a ball pommel; drop it for a cleaner single-knob foot."""
    if kind == "spike":
        pr = int(hw * 1.5)
        pygame.draw.polygon(surf, _shade_c(col, -50),
                            [(int(cx - hw), int(bot_y - pr)), (int(cx + hw), int(bot_y - pr)),
                             (cx, int(bot_y + pr * 0.5))])
        pygame.draw.polygon(surf, col,
                            [(int(cx - hw + ss), int(bot_y - pr)),
                             (int(cx + hw - ss), int(bot_y - pr)),
                             (cx, int(bot_y + pr * 0.4))])
        pygame.draw.line(surf, _shade_c(col, 60), (int(cx - hw * 0.3), int(bot_y - pr)),
                         (cx, int(bot_y + pr * 0.3)), max(1, int(1.4 * ss)))
        return
    if kind == "bell":
        bw2 = int(hw * 1.7)
        pygame.draw.polygon(surf, _shade_c(col, -50),
                            [(int(cx - hw), int(bot_y - hw * 1.6)),
                             (int(cx + hw), int(bot_y - hw * 1.6)),
                             (int(cx + bw2), int(bot_y)), (int(cx - bw2), int(bot_y))])
        pygame.draw.polygon(surf, col,
                            [(int(cx - hw + ss), int(bot_y - hw * 1.6)),
                             (int(cx + hw - ss), int(bot_y - hw * 1.6)),
                             (int(cx + bw2 - ss), int(bot_y - ss)),
                             (int(cx - bw2 + ss), int(bot_y - ss))])
        pygame.draw.ellipse(surf, _shade_c(col, -40),
                            (int(cx - bw2), int(bot_y - 2 * ss), int(bw2 * 2), int(4 * ss)))
        return
    # Default: a fat knobbed ball pommel with a small bead beneath it.
    pr = int(hw * 1.5)
    pcy = int(bot_y - pr * 0.55)
    pygame.draw.circle(surf, _shade_c(col, -55), (cx, pcy), pr)
    pygame.draw.circle(surf, col, (cx, pcy), int(pr - ss))
    pygame.draw.circle(surf, _shade_c(col, 55),
                       (int(cx - pr * 0.3), int(pcy - pr * 0.3)), max(2, int(pr * 0.36)))
    if gem is not None:
        pygame.draw.circle(surf, _shade_c(gem, -40), (cx, pcy), max(2, int(pr * 0.4)))
        pygame.draw.circle(surf, gem, (cx, pcy), max(2, int(pr * 0.32)))
        pygame.draw.circle(surf, _shade_c(gem, 90),
                           (int(cx - pr * 0.16), int(pcy - pr * 0.16)), max(1, int(pr * 0.14)))
    if bead:
        pygame.draw.circle(surf, _shade_c(col, -45), (cx, int(bot_y - pr * 1.25)),
                           max(2, int(hw * 0.8)))


def prop_14l(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(13 * ss)
    hy = int(50 * ss)                      # seat the head lower so the tall cap +
                                           # its bell tips clear the box top (no clip)
    shaft_top = hy + hr
    hwid = int(7 * ss)
    _shaft_twist(surf, cx, shaft_top, bh - int(7 * ss), hwid, ss, PLUM, GOLD, PLUM_DK)
    _ferrule(surf, cx, bh * 0.5, hwid, ss, GOLD, h=9, jewel=PLUM)
    _ferrule(surf, cx, bh - int(20 * ss), hwid, ss, GOLD, h=8)
    # Foot planted ON the ground line (bot_y == bh): the flared bell ends at the
    # box bottom rather than 4 px above it, so the staff rests on the ground.
    _pommel_finial(surf, cx, bh, hwid, ss, GOLD, kind="bell")
    base_y = hy - hr + int(1 * ss)
    for (dx, dy, col) in [(-30, -8, PLUM_DK), (30, -6, PLUM_DK),
                          (-19, -29, LIME_DK), (19, -27, GOLD_DK)]:
        bxp, byp = cx + int(dx * ss), base_y + int(dy * ss)
        span = int(8 * ss)
        tri = [(cx - span, base_y + int(2 * ss)), (cx + span, base_y + int(2 * ss)), (bxp, byp)]
        pygame.draw.polygon(surf, col, tri)
        pygame.draw.polygon(surf, _shade_c(col, 50),
                            [(cx - span, base_y + int(2 * ss)), (cx, base_y + int(2 * ss)),
                             (bxp, byp)])
        pygame.draw.polygon(surf, _shade_c(col, -60), tri, max(1, int(1.4 * ss)))
        pygame.draw.circle(surf, GOLD, (int(bxp), int(byp)), max(2, int(3.4 * ss)))
        pygame.draw.circle(surf, GOLD_DK, (int(bxp), int(byp)), max(2, int(3.4 * ss)), max(1, int(ss)))
    _marotte_ruff(surf, cx, hy + hr - int(2 * ss), int(hr * 1.05), ss, LIME, lobes=9)
    _mini_clown_face(surf, cx, hy, hr, ss, expr="grin")


def _staff_obstacle(H, ss, *, flip):
    surf, bw, bh = _box(max(1, int(H)), ss)
    prop_14l(surf, bw, bh, ss)
    out_w = PIPE_W + 2 * OVERHANG
    small = pygame.transform.smoothscale(surf, (out_w, max(1, int(H))))
    if flip:
        small = pygame.transform.flip(small, False, True)
    return small


def draw_pillar_pair_staff(surf, top_rect, bot_rect, palette, seed):
    """Draw a TOP + BOTTOM staff obstacle pair (the marotte bauble/head faces the
    gap on each). Matches the pagoda candidate signature so Pipe can cache it.
    `palette`/`seed` are accepted for signature parity; the staff uses its own
    fixed jester colours."""
    ss = 5
    out_w = PIPE_W + 2 * OVERHANG
    if top_rect.height > 0:
        top = _staff_obstacle(top_rect.height, ss, flip=True)   # head points DOWN to gap
        surf.blit(top, (top_rect.x - OVERHANG, top_rect.y))
    if bot_rect.height > 0:
        bot = _staff_obstacle(bot_rect.height, ss, flip=False)  # head points UP to gap
        surf.blit(bot, (bot_rect.x - OVERHANG, bot_rect.y))
