"""
CLOSED-STALL treatments for the LAGOON STILT-MARKET hub — docs-only exploration.

The hub launches with 3 stalls OPEN (COSTUMES, PARROTS, PARCELS) and 4 SHUT
(ANIMALS, SHOES, HATS, SHADES). A shut stall must read as CLOSED with ZERO text
and NO category preview dome — purely by a physical "shut front" (blind, boards,
dark box, shutter, or curtain) hung where the awning + dome + label board sit on
an open hut. Everything else about the hut (roof, body, stilts, deck, reflection,
footprint) is IDENTICAL to an open stall so the village silhouette never moves.

This harness REUSES the shipped lagoon render module verbatim for the sky, water,
palms, planks, stilts and the three open huts — so those pixels are unchanged —
and only forks the FRONT composition of a closed hut into five candidate styles.

Both build targets safe: pure pygame, no numpy, headless (SDL dummy), SS=4.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import docs.store_bazaar.lagoon_stilt.render as L
from docs.store_bazaar.lagoon_stilt.render import (
    STALLS, LAYOUT, LABELS,
    draw_water, draw_plank, draw_stilts, draw_hut, hut_reflection,
    draw_pip, draw_header,
    WOOD_HI, WOOD_MID, WOOD_LO, WOOD_EDGE, STALL_DARK,
    THATCH_HI, THATCH_MID, THATCH_LO, THATCH_EDGE,
    AWN_RED, AWN_RED_D, AWN_CREAM, AWN_CREAM_D,
)
from docs.store_redesign.constellation_hi.render_hi import (
    SS, DW, DH, m, mf, font, vgrad, vgrad_stops, drop_shadow, top_sheen,
    bevel_rim, downscale, gradient_text, _glyph_base,
    GOLD, GOLD_PALE, GOLD_A_TOP, GOLD_A_BOT,
)
from game.draw import lerp_color, NEAR_BLACK, WHITE


# The 4 groups launching SHUT. The 3 launching OPEN keep the shipped draw_hut.
CLOSED_GROUPS = {"animal", "shoes", "hats", "shades"}

# Cool "dormant" grade — a shut hut is desaturated a touch toward dusk slate so
# it reads as sleeping vs the warm open stalls (precedent: the store's locked
# cool-slate chip). Applied as a low-alpha cool veil over the shut FRONT only,
# never the roof/stilts, so the village silhouette stays warm + coherent.
DORMANT_TINT = (70, 84, 118)


def _dormant_veil(surf, rect, amount=0.15):
    """A soft cool veil over a closed FRONT so it sits back asleep while the three
    open stalls pop warm. Kept in the 12-18% band — enough to cool the plane, not
    so much it goes muddy blue-grey. A gentle top-down deepening so the covered
    plane also reads a touch darker than the warm thatch roof above it (a closed
    front must be a DISTINCT covered plane, not merge into the roof's brown mass)."""
    v = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    a = int(255 * amount)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        # stronger just under the eave so the front separates from the roof value,
        # easing to the base veil lower down where the deck light lifts it
        aa = int(a * (1.0 + 0.35 * (1.0 - t)))
        v.fill((*DORMANT_TINT, min(255, aa)), (0, y, rect.w, 1))
    surf.blit(v, rect.topleft)


def _contact_shadow(surf, rect, scale, strength=150):
    """A soft dark contact line where a drawn-DOWN cover meets the deck/opening
    lip, so the blind/shutter/curtain reads as hung over the opening with a lip
    (not painted flat on the wall). A short upward-fading band riding the bottom
    edge + a crisp hairline at the lip."""
    h = max(m(3), int(m(6) * scale))
    band = pygame.Surface((rect.w, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h - 1)
        a = int(strength * t ** 1.4)
        band.fill((6, 6, 12, a), (0, y, rect.w, 1))
    surf.blit(band, (rect.left, rect.bottom - h))
    pygame.draw.line(surf, (0, 0, 0, 175), (rect.left, rect.bottom - max(1, m(1))),
                     (rect.right, rect.bottom - max(1, m(1))), max(1, m(1)))


# =============================================================================
# The five "shut front" treatments. Each is handed the SAME geometry the open
# awning + dome + label occupy so it drops in without moving the hut:
#   cx, body_top, half_w, body_h, deck_y, scale.
# The dark interior box (behind whatever covers it) is already painted by the
# shared draw_hut body pass — these draw the COVER over that opening.
# =============================================================================
def _shut_interior(surf, cx, body_top, half_w, body_h, deep=True):
    """Deepen the stall opening to a black shadow box so any gaps in the cover
    read as an unlit, empty interior (nobody home) rather than the warm timber
    the open stalls show. Returns the opening rect for veils/covers."""
    op = pygame.Rect(cx - half_w + m(6), body_top + m(2),
                     half_w * 2 - m(12), body_h - m(4))
    fill = (10, 9, 14) if deep else (20, 17, 24)
    surf.blit(vgrad(op.w, op.h, 0, lerp_color(fill, (26, 24, 36), 0.5), fill),
              op.topleft)
    return op


def front_bamboo(surf, cx, body_top, half_w, body_h, deck_y, scale):
    """1 ROLLED BAMBOO BLIND — a woven reed shade pulled DOWN over the front:
    stacked thin horizontal reed slats (each a lit-top rounded dowel), a heavier
    bottom weight bar, and two side cords running to a small cleat. Warm cane."""
    op = _shut_interior(surf, cx, body_top, half_w, body_h)
    # the blind hangs from just under the eave to a little above the deck lip
    bl = pygame.Rect(cx - half_w + m(4), body_top + m(3),
                     half_w * 2 - m(8), body_h - m(8))
    # cane values pulled a touch DEEPER + more saturated than the thatch roof so
    # the pulled-down reed plane separates from the straw above it at hub size.
    CANE_HI = (200, 158, 96)
    CANE = (156, 116, 64)
    CANE_LO = (104, 72, 36)
    CANE_EDGE = (64, 42, 20)
    # a faint back panel so slat gaps read against wood, not pure black
    surf.blit(vgrad(bl.w, bl.h, 0, (52, 38, 24), (28, 20, 12)), bl.topleft)
    slat_h = max(m(4), int(m(6) * scale))
    y = bl.top
    row = 0
    while y < bl.bottom - slat_h:
        r = pygame.Rect(bl.left, y, bl.w, slat_h - max(1, m(1)))
        # each reed: lit dowel top easing to a shaded underside, tiny value jitter
        j = 0.06 * math.sin(row * 1.7)
        top = lerp_color(CANE_HI, CANE, min(1.0, 0.15 + abs(j)))
        surf.blit(vgrad(r.w, r.h, 0, top, CANE_LO), r.topleft)
        pygame.draw.line(surf, lerp_color(CANE_HI, WHITE, 0.30),
                         (r.left, r.top), (r.right, r.top), max(1, m(0.8)))
        # DEEPER groove shadow between reeds (+~14%): a dark hairline plus a thin
        # cast band below it so each reed reads as a rounded rod, not a flat stripe
        pygame.draw.line(surf, CANE_EDGE, (r.left, r.bottom),
                         (r.right, r.bottom), max(1, m(1.1)))
        groove = pygame.Surface((r.w, max(1, m(1.6))), pygame.SRCALPHA)
        groove.fill((10, 7, 4, 105))
        surf.blit(groove, (r.left, r.bottom))
        y += slat_h
        row += 1
    # vertical binding cords woven through the reeds (three tracks)
    for fx in (0.22, 0.5, 0.78):
        vx = bl.left + int(bl.w * fx)
        pygame.draw.line(surf, CANE_EDGE, (vx, bl.top), (vx, bl.bottom),
                         max(1, m(1.2)))
        pygame.draw.line(surf, lerp_color(CANE_HI, WHITE, 0.2),
                         (vx - m(1), bl.top), (vx - m(1), bl.bottom), max(1, m(0.6)))
    # heavier bottom weight bar (a rounded darker dowel), sitting proud of the
    # reeds — the "pulled all the way down" tell
    wb = pygame.Rect(bl.left - m(1), bl.bottom - int(slat_h * 1.4),
                     bl.w + m(2), int(slat_h * 1.4) + m(1))
    # a soft cast shadow of the weight bar onto the reeds just above it
    wbsh = pygame.Surface((wb.w, m(4)), pygame.SRCALPHA)
    for yy in range(m(4)):
        wbsh.fill((8, 6, 4, int(90 * (1 - yy / m(4)))), (0, yy, wb.w, 1))
    surf.blit(wbsh, (wb.left, wb.top - m(4)))
    surf.blit(vgrad(wb.w, wb.h, m(2), CANE, CANE_EDGE), wb.topleft)
    pygame.draw.line(surf, lerp_color(CANE, WHITE, 0.35),
                     (wb.left, wb.top + m(1)), (wb.right, wb.top + m(1)), max(1, m(1.2)))
    pygame.draw.rect(surf, CANE_EDGE, wb, width=max(1, m(1)), border_radius=m(2))
    # side pull-cords looping down from the eave to a little cleat on the right
    for side, sx in ((-1, bl.left + m(3)), (1, bl.right - m(3))):
        pygame.draw.line(surf, (54, 40, 24), (sx, bl.top - m(2)),
                         (sx, bl.bottom + m(4)), max(1, m(1)))
    # a small toggle knot at the base of each cord
    for sx in (bl.left + m(3), bl.right - m(3)):
        pygame.draw.circle(surf, CANE_LO, (sx, bl.bottom + m(4)), max(1, m(2)))
    _dormant_veil(surf, bl, 0.15)
    # eave shadow across the top of the blind so it hangs UNDER the roof
    pygame.draw.line(surf, (0, 0, 0, 150), (bl.left, bl.top),
                     (bl.right, bl.top), max(1, m(1.4)))
    # bottom contact/edge shadow so the blind reads as drawn DOWN over the opening
    _contact_shadow(surf, bl, scale)


def front_boarded(surf, cx, body_top, half_w, body_h, deck_y, scale):
    """2 BOARDED UP — neat weathered timber shop-boards nailed HORIZONTALLY across
    the opening (no diagonal X — that reads condemned/broken; horizontal reads
    'boarded up for the season'), with clean hammered nail heads at each end, thin
    dark gaps showing the unlit interior between boards, contained inside the
    opening frame so the shared silhouette never changes. Premium-shut, not ruined."""
    op = _shut_interior(surf, cx, body_top, half_w, body_h)
    PLK_HI = (172, 134, 88)
    PLK = (132, 98, 58)
    PLK_LO = (90, 64, 36)
    PLK_EDGE = (56, 38, 18)

    # the boarding sits fully inside the opening frame (never overshoots)
    L_ = op.left + m(3)
    R_ = op.right - m(3)
    field_t = op.top + m(4)
    field_b = op.bottom - m(4)
    field_h = field_b - field_t
    n_boards = 5
    gap = max(m(1.5), int(m(2) * scale))          # thin dark gap between boards
    pw = (field_h - gap * (n_boards - 1)) / n_boards
    for b in range(n_boards):
        by = field_t + b * (pw + gap)
        r = pygame.Rect(int(L_), int(by), int(R_ - L_), int(pw))
        # a slight per-board value jitter so five boards read as reclaimed timber,
        # not a single flat panel; each board a lit-top -> shaded-base gradient
        jt = 0.10 * math.sin(b * 1.9)
        surf.blit(vgrad(r.w, r.h, 0, lerp_color(PLK, PLK_HI, 0.5 + jt), PLK_LO),
                  r.topleft)
        # lit top edge + dark seated base so each board has round
        pygame.draw.line(surf, lerp_color(PLK_HI, WHITE, 0.22),
                         (r.left, r.top + max(1, m(0.6))),
                         (r.right, r.top + max(1, m(0.6))), max(1, m(1)))
        pygame.draw.line(surf, PLK_EDGE, (r.left, r.bottom - max(1, m(0.6))),
                         (r.right, r.bottom - max(1, m(0.6))), max(1, m(1)))
        # a faint lengthwise grain streak
        gy = r.top + int(r.h * 0.6)
        pygame.draw.line(surf, PLK_LO, (r.left + m(4), gy), (r.right - m(4), gy),
                         max(1, m(0.7)))
        # clean hammered nail heads near each end (steel dot + tiny highlight)
        for nxp in (r.left + m(6), r.right - m(6)):
            nyp = r.centery
            pygame.draw.circle(surf, (34, 30, 28), (int(nxp), int(nyp)), max(1, m(2)))
            pygame.draw.circle(surf, (170, 172, 180),
                               (int(nxp - m(0.6)), int(nyp - m(0.6))), max(1, m(1)))
    # a light frame lip around the boarded field so the boards sit INSET in the
    # opening, reinforcing "sealed shut" over "planks slapped on the wall"
    pygame.draw.rect(surf, (44, 30, 16), op, width=max(1, m(2)))
    pygame.draw.line(surf, lerp_color(WOOD_HI, WHITE, 0.15),
                     (op.left + m(1), op.top + m(1)),
                     (op.right - m(1), op.top + m(1)), max(1, m(1)))
    _dormant_veil(surf, op, 0.14)


def front_dormant(surf, cx, body_top, half_w, body_h, deck_y, scale):
    """3 FURLED + DORMANT — the most minimal 'nobody home': the striped awning is
    ROLLED UP and tied in a tight bundle at the eave, the dome is gone, and the
    stall interior is a deep unlit empty shadow box. A few tie-cords + the furled
    roll are the only front features; the emptiness does the talking."""
    # a deeper, emptier box than the others — this read leans on darkness. The
    # fill is cooled toward the dormant slate (not neutral black) so the whole
    # opening reads "sealed behind, asleep" rather than an open unlit shelf.
    op = _shut_interior(surf, cx, body_top, half_w, body_h, deep=True)
    coolfill = pygame.Surface((op.w, op.h), pygame.SRCALPHA)
    coolfill.fill((*DORMANT_TINT, 60))
    surf.blit(coolfill, op.topleft)
    # inner ambient occlusion: darken the top + sides of the box so it reads as a
    # deep recess with light only barely reaching the near lip
    ao = pygame.Surface((op.w, op.h), pygame.SRCALPHA)
    for y in range(op.h):
        t = y / op.h
        a = int(130 * (1 - t) ** 1.3)
        pygame.draw.line(ao, (4, 5, 12, a), (0, y), (op.w, y))
    surf.blit(ao, op.topleft)
    for x in range(op.w):
        d = abs(x - op.w / 2) / (op.w / 2)
        a = int(115 * d ** 2.0)
        pygame.draw.line(surf, (4, 5, 12, a), (op.left + x, op.top),
                         (op.left + x, op.bottom))
    # a pulled-across MEMBRANE sealing the lower opening: a taut dark canvas panel
    # with a slack sag seam, so the box reads "sealed behind" — not an open shelf.
    memb_t = op.top + int(op.h * 0.44)
    for y in range(memb_t, op.bottom):
        t = (y - memb_t) / max(1, op.bottom - memb_t)
        col = lerp_color((26, 26, 38), (12, 13, 22), t)
        pygame.draw.line(surf, col, (op.left, y), (op.right, y))
    # the slack sag seam of the membrane (a shallow catenary dip) with a faint
    # lit crest above it so the taut cloth reads as a physical pulled panel
    seam_pts = []
    for k in range(0, op.w + 1, max(1, m(3))):
        xx = op.left + k
        dip = math.sin(math.pi * k / op.w) * m(4)
        seam_pts.append((xx, memb_t + int(dip)))
    if len(seam_pts) > 1:
        pygame.draw.lines(surf, (8, 8, 16), False, seam_pts, max(1, m(1.4)))
        crest = [(px, py - m(1)) for px, py in seam_pts]
        pygame.draw.lines(surf, (48, 50, 66), False, crest, max(1, m(0.8)))
    # the FURLED, OFF-DUTY awning: a tight rolled bundle tied under the eave, but
    # DIMMED + desaturated toward the dormant slate so it reads as a tied-off,
    # not-in-use awning — never an active red/cream valance.
    roll_h = int(m(11) * scale)
    roll = pygame.Rect(cx - half_w + m(2), body_top - m(1), half_w * 2 - m(4), roll_h)
    # muted stripe hues: red -> dusty maroon-slate, cream -> greyed sand
    RED_OFF = lerp_color(lerp_color(AWN_RED_D, DORMANT_TINT, 0.42), NEAR_BLACK, 0.18)
    CREAM_OFF = lerp_color(lerp_color(AWN_CREAM_D, DORMANT_TINT, 0.38), NEAR_BLACK, 0.10)
    surf.blit(vgrad(roll.w, roll.h, roll_h // 2,
                    lerp_color(CREAM_OFF, NEAR_BLACK, 0.15), RED_OFF), roll.topleft)
    stripe_w = max(m(7), int(roll.w / 11))
    s = 0
    x = roll.left
    while x < roll.right:
        c = RED_OFF if s % 2 == 0 else CREAM_OFF
        band = pygame.Rect(x, roll.top + m(1), stripe_w - max(1, m(1)), roll.h - m(2))
        bs = pygame.Surface((band.w, band.h), pygame.SRCALPHA)
        for by in range(band.h):
            t = by / max(1, band.h - 1)
            shade = 0.64 - 0.30 * abs(t - 0.35)
            col = lerp_color(NEAR_BLACK, c, min(1.0, shade + 0.30))
            bs.fill((*col, 220), (0, by, band.w, 1))
        surf.blit(bs, band.topleft)
        x += stripe_w
        s += 1
    # a restrained (dimmer) lit top of the roll + dark seated underside
    pygame.draw.line(surf, lerp_color(CREAM_OFF, WHITE, 0.22),
                     (roll.left + m(2), roll.top + m(1)),
                     (roll.right - m(2), roll.top + m(1)), max(1, m(1.0)))
    pygame.draw.rect(surf, (0, 0, 0, 165), roll, width=max(1, m(1.2)),
                     border_radius=roll_h // 2)
    # two tie-cords cinching the furled roll to the eave
    for fx in (0.30, 0.70):
        tx = roll.left + int(roll.w * fx)
        pygame.draw.line(surf, (48, 38, 24), (tx, roll.top - m(2)),
                         (tx, roll.bottom + m(2)), max(1, m(1.4)))
        pygame.draw.circle(surf, (62, 50, 32), (tx, roll.bottom + m(2)), max(1, m(2)))
    _dormant_veil(surf, op, 0.15)


def front_shutter(surf, cx, body_top, half_w, body_h, deck_y, scale):
    """4 LOUVERED WOODEN SHUTTER — a horizontal-slat louver drawn down over the
    front: angled slats each catching a thin top light, a center vertical seam
    splitting a two-leaf shutter, and a frame around the opening. Crisp + premium."""
    op = _shut_interior(surf, cx, body_top, half_w, body_h)
    # louver values pulled COOLER + DARKER than the warm thatch so the drawn-down
    # shutter reads as a distinct shaded plane, not another brown roof mass.
    FR_HI = (128, 104, 74)
    FR = (92, 72, 50)
    FR_LO = (58, 44, 28)
    SLAT_HI = (140, 118, 86)
    SLAT = (98, 82, 60)
    SLAT_LO = (54, 44, 32)
    # frame around the shutter opening
    fr = pygame.Rect(cx - half_w + m(4), body_top + m(3),
                     half_w * 2 - m(8), body_h - m(8))
    fw = max(m(4), int(m(6) * scale))
    surf.blit(vgrad(fr.w, fr.h, 0, FR, FR_LO), fr.topleft)
    inner = fr.inflate(-fw * 2, -fw * 2)
    # the two-leaf louver field inside the frame
    surf.blit(vgrad(inner.w, inner.h, 0, (34, 28, 22), (18, 14, 12)), inner.topleft)
    slat_h = max(m(5), int(m(7) * scale))
    y = inner.top
    while y < inner.bottom - m(1):
        h = min(slat_h, inner.bottom - y)
        r = pygame.Rect(inner.left, y, inner.w, h)
        # angled slat: bright thin catch on the tilted-up top lip, body shading
        # to a dark gap-shadow at its lower edge (the classic louver read)
        surf.blit(vgrad(r.w, r.h, 0, SLAT, SLAT_LO), r.topleft)
        pygame.draw.line(surf, lerp_color(SLAT_HI, WHITE, 0.45),
                         (r.left, r.top + max(1, m(1))),
                         (r.right, r.top + max(1, m(1))), max(1, m(1.2)))
        pygame.draw.line(surf, (12, 9, 8), (r.left, r.bottom - max(1, m(0.6))),
                         (r.right, r.bottom - max(1, m(0.6))), max(1, m(1)))
        y += slat_h
    # center seam splitting the two leaves + a small handle catch on each
    seam_x = inner.centerx
    pygame.draw.line(surf, FR_LO, (seam_x, inner.top), (seam_x, inner.bottom),
                     max(1, m(1.8)))
    pygame.draw.line(surf, lerp_color(FR_HI, WHITE, 0.2),
                     (seam_x - m(1), inner.top), (seam_x - m(1), inner.bottom),
                     max(1, m(0.6)))
    for hx in (seam_x - m(4), seam_x + m(4)):
        pygame.draw.circle(surf, (46, 34, 20),
                           (hx, inner.centery), max(1, m(2)))
        pygame.draw.circle(surf, lerp_color(GOLD, NEAR_BLACK, 0.3),
                           (hx, inner.centery), max(1, int(m(1.2))))
    # frame emboss + a lit top rail so the shutter sits proud of the opening
    pygame.draw.rect(surf, FR_LO, fr, width=max(1, m(1.4)))
    pygame.draw.line(surf, lerp_color(FR_HI, WHITE, 0.3),
                     (fr.left + m(1), fr.top + m(1)),
                     (fr.right - m(1), fr.top + m(1)), max(1, m(1.4)))
    _dormant_veil(surf, fr, 0.16)
    # bottom contact/edge shadow so the shutter reads as drawn DOWN with a lip
    _contact_shadow(surf, fr, scale)


def front_curtain(surf, cx, body_top, half_w, body_h, deck_y, scale):
    """5 CANVAS / TARP CURTAIN — a heavy canvas sheet tied + draped across the
    front: soft vertical folds shaded by a per-column sine, a grommet-and-tie
    header at the eave, and a slight sag/scallop at the hem. Warm oiled canvas."""
    op = _shut_interior(surf, cx, body_top, half_w, body_h)
    cv = pygame.Rect(cx - half_w + m(4), body_top + m(2),
                     half_w * 2 - m(8), body_h - m(6))
    # WARM sun-bleached sand/ochre canvas (the cold grey read like corrugated
    # metal) — a low-saturation warm sand that catches the golden hour.
    CANVAS_HI = (224, 198, 148)      # sunlit sand crest
    CANVAS = (196, 166, 116)         # body ochre
    CANVAS_LO = (150, 120, 80)       # fold trough
    # broad, soft folds (fewer, wider than before) so the cloth reads as hanging
    # fabric, not tight ribs. A raised-cosine fold profile gives rounded crests.
    n = cv.w
    n_folds = 4
    fold_f = 2.0 * math.pi * n_folds / n
    for xi in range(n):
        x = cv.left + xi
        # rounded fold value: soft crest, softer trough (avoids the metal-rib look)
        fold = math.sin(xi * fold_f)
        crest = (0.5 + 0.5 * fold) ** 1.4
        top = lerp_color(CANVAS_LO, CANVAS_HI, crest)
        bot = lerp_color(CANVAS_LO, CANVAS, crest * 0.7)
        # sag: the hem dips lower toward the middle of the span + a per-fold wobble
        mid = (xi / n - 0.5)
        sag = int((1.0 - 4 * mid * mid) * m(7)) + int((0.5 + 0.5 * fold) * m(2))
        col_h = cv.h - m(2) + sag
        strip = vgrad(1, col_h, 0, top, bot)
        surf.blit(strip, (x, cv.top))
    # 3 soft vertical fold HIGHLIGHTS catching the low sun on the crest ridges so
    # the sheet reads as draped cloth. Placed on the fold crests, feathered.
    for hk in range(n_folds):
        # crest of fold hk sits three-quarters of a period in
        hxp = cv.left + int((hk * n / n_folds) + (n / n_folds) * 0.75)
        if hxp >= cv.right:
            continue
        hw = max(m(2), int(m(4) * scale))
        hl = pygame.Surface((hw * 2, cv.h), pygame.SRCALPHA)
        for gx in range(hw * 2):
            fall = 1.0 - abs(gx - hw) / hw
            a = int(90 * fall ** 1.6)
            hl.fill((*lerp_color(CANVAS_HI, WHITE, 0.35), a), (gx, 0, 1, cv.h))
        surf.blit(hl, (hxp - hw, cv.top))
    # heavy header band at the eave with grommets + short ties
    hdr = pygame.Rect(cv.left - m(1), cv.top - m(1), cv.w + m(2), int(m(9) * scale))
    surf.blit(vgrad(hdr.w, hdr.h, 0, lerp_color(CANVAS, WOOD_LO, 0.35),
                    lerp_color(CANVAS_LO, WOOD_LO, 0.4)), hdr.topleft)
    pygame.draw.line(surf, lerp_color(CANVAS_HI, WHITE, 0.3),
                     (hdr.left, hdr.top + m(1)), (hdr.right, hdr.top + m(1)),
                     max(1, m(1)))
    pygame.draw.line(surf, (60, 46, 28), (hdr.left, hdr.bottom),
                     (hdr.right, hdr.bottom), max(1, m(1.2)))
    ng = 5
    for g in range(ng):
        gx = hdr.left + int(hdr.w * (g + 0.5) / ng)
        # brass grommet
        pygame.draw.circle(surf, (52, 40, 22), (gx, hdr.centery), max(1, m(2)))
        pygame.draw.circle(surf, lerp_color(GOLD, NEAR_BLACK, 0.35),
                           (gx, hdr.centery), max(1, int(m(1.4))))
        pygame.draw.circle(surf, (14, 12, 16), (gx, hdr.centery), max(1, int(m(0.6))))
        # a short lashing cord looping up over the eave rail
        pygame.draw.line(surf, (66, 50, 30), (gx, hdr.top),
                         (gx + m(1), hdr.top - m(3)), max(1, m(1)))
    # soft warm fold-trough seams painted over the field for extra cloth read
    for k in range(1, n_folds):
        fx = cv.left + int(cv.w * k / n_folds)
        seam = pygame.Surface((max(1, m(1.4)), cv.h + m(8)), pygame.SRCALPHA)
        seam.fill((72, 54, 34, 60))
        surf.blit(seam, (fx, cv.top))
    _dormant_veil(surf, cv, 0.15)
    # a soft sagging hem shadow along the bottom so the hanging cloth reads as a
    # weighted drape meeting the deck, not a flat sheet. A prebuilt fading column
    # shifted down by the mid-span sag so the shadow follows the hem's dip.
    hh = m(7)
    hemcol = pygame.Surface((1, hh), pygame.SRCALPHA)
    for yy in range(hh):
        hemcol.fill((8, 7, 12, int(140 * (yy / hh) ** 1.5)), (0, yy, 1, 1))
    for xi in range(cv.w):
        mid = (xi / cv.w - 0.5)
        dip = int((1.0 - 4 * mid * mid) * m(3))
        surf.blit(hemcol, (cv.left + xi, cv.bottom - hh + dip))


CLOSED_FRONTS = {
    "bamboo":  front_bamboo,
    "boarded": front_boarded,
    "dormant": front_dormant,
    "shutter": front_shutter,
    "curtain": front_curtain,
}
CLOSED_ORDER = ["bamboo", "boarded", "dormant", "shutter", "curtain"]
CLOSED_TITLES = {
    "bamboo":  "1  BAMBOO BLIND",
    "boarded": "2  BOARDED",
    "dormant": "3  DORMANT",
    "shutter": "4  SHUTTER",
    "curtain": "5  CURTAIN",
}


def draw_hut_closed(surf, cx, deck_y, scale, style):
    """A SHUT hut: identical roof/body/stilts/deck to draw_hut, but the awning +
    dome + label region is replaced by one of the five "shut front" covers. No
    text, no preview dome. Mirrors draw_hut's geometry (L568+) exactly so the
    silhouette + footprint match an open hut to the pixel."""
    half_w = int(m(58) * scale)
    body_h = int(m(64) * scale)
    roof_h = int(m(40) * scale)
    eave = int(m(10) * scale)
    body_top = deck_y - body_h
    roof_apex_y = body_top - roof_h

    # ── soft seat under the whole hut (same as open) ──
    L.soft_glow(surf, cx, deck_y, half_w + eave, (0, 0, 0), 110, layers=6)

    # ── stall body (shaded interior box) — same as open ──
    body_rect = pygame.Rect(cx - half_w, body_top, half_w * 2, body_h)
    surf.blit(vgrad(body_rect.w, body_rect.h, 0,
                    lerp_color(STALL_DARK, WOOD_MID, 0.25), STALL_DARK),
              body_rect.topleft)
    for px in (body_rect.left, body_rect.right - m(8)):
        pygame.draw.rect(surf, WOOD_LO, (px, body_top, m(8), body_h))
        pygame.draw.line(surf, WOOD_HI, (px + m(1), body_top),
                         (px + m(1), deck_y), max(1, m(1)))

    # ── thatched roof (verbatim from draw_hut) ──
    rl = (cx - half_w - eave, body_top)
    rr = (cx + half_w + eave, body_top)
    apex = (cx, roof_apex_y)
    shs = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pygame.draw.polygon(shs, (0, 0, 0, 80),
                        [(rl[0], rl[1] + m(6)), (rr[0], rr[1] + m(6)),
                         (apex[0], apex[1] + m(6))])
    surf.blit(shs, (0, 0))
    courses = 9
    for i in range(courses):
        t0 = i / courses
        t1 = (i + 1) / courses
        y_lo = body_top - (body_top - roof_apex_y) * t0
        y_hi = body_top - (body_top - roof_apex_y) * t1
        xl0 = rl[0] + (apex[0] - rl[0]) * t0
        xr0 = rr[0] + (apex[0] - rr[0]) * t0
        xl1 = rl[0] + (apex[0] - rl[0]) * t1
        xr1 = rr[0] + (apex[0] - rr[0]) * t1
        col = lerp_color(THATCH_LO, THATCH_HI, 1.0 - t0)
        pygame.draw.polygon(surf, col, [(xl0, y_lo), (xr0, y_lo),
                                        (xr1, y_hi), (xl1, y_hi)])
        fringe_n = 18
        for f in range(fringe_n):
            ft = f / fringe_n
            fx = xl0 + (xr0 - xl0) * ft
            drop = m(3) * scale * (0.5 + 0.5 * math.sin(f * 2.3 + i))
            pygame.draw.line(surf, lerp_color(col, THATCH_EDGE, 0.5),
                             (fx, y_lo), (fx, y_lo + drop), max(1, m(0.8)))
    lit = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pygame.draw.polygon(lit, (*lerp_color(THATCH_HI, WHITE, 0.25), 90),
                        [rl, apex, (cx, body_top)])
    surf.blit(lit, (0, 0))
    pygame.draw.line(surf, THATCH_EDGE, rl, apex, max(1, m(1.6)))
    pygame.draw.line(surf, THATCH_EDGE, rr, apex, max(1, m(1.6)))
    pygame.draw.line(surf, lerp_color(THATCH_HI, WHITE, 0.4),
                     rl, apex, max(1, m(1.0)))
    pygame.draw.circle(surf, THATCH_EDGE, apex, m(4))
    pygame.draw.circle(surf, THATCH_HI, (apex[0] - m(1), apex[1] - m(1)), m(2))

    # ── deck (front lip) — drawn AFTER the front cover so the deck sits on top,
    # but we need it under the cover's hem shadow; draw it here as in open, then
    # the cover hem overlaps into it slightly like the awning valance does. ──
    # ── the SHUT FRONT replaces awning + dome + label ──
    CLOSED_FRONTS[style](surf, cx, body_top, half_w, body_h, deck_y, scale)

    # ── deck the hut stands on (front lip) — same as open, drawn last so the
    # deck plane reads in front of the cover hem ──
    deck_rect = pygame.Rect(cx - half_w - m(4), deck_y - m(8),
                            half_w * 2 + m(8), m(10))
    surf.blit(vgrad(deck_rect.w, deck_rect.h, 0, WOOD_HI, WOOD_LO),
              deck_rect.topleft)
    pygame.draw.rect(surf, WOOD_EDGE, deck_rect, width=max(1, m(1)))
    for s in range(1, 8):
        sx = deck_rect.left + deck_rect.w * s // 8
        pygame.draw.line(surf, WOOD_LO, (sx, deck_rect.top),
                         (sx, deck_rect.bottom), max(1, m(0.8)))

    return half_w, roof_apex_y


def render_hub(style):
    """Full lagoon hub with COSTUMES/PARROTS/PARCELS open and the four closed
    groups shut in `style`. Sky/water/palms/planks/stilts/open-huts are drawn by
    the shipped lagoon primitives so they're pixel-identical to the live hub."""
    surf = pygame.Surface((DW, DH))
    surf.blit(L._static_sky, (0, 0))
    horizon = draw_water(surf)

    huts = []
    for group, fx, fy, scale, hero in LAYOUT:
        cx = int(DW * fx)
        deck_y = int(DH * fy)
        huts.append(dict(group=group, label=LABELS[group], cx=cx, deck_y=deck_y,
                         scale=scale, hero=hero))

    order = sorted(range(len(huts)), key=lambda i: huts[i]["deck_y"])

    plank_links = [(0, 3), (1, 5), (2, 4), (3, 5), (4, 5), (5, 6)]
    for a, b in plank_links:
        ha, hb = huts[a], huts[b]
        draw_plank(surf, ha["cx"], ha["deck_y"] - m(2),
                   hb["cx"], hb["deck_y"] - m(2), int(m(16)))

    for i in order:
        h = huts[i]
        half_w = int(m(58) * h["scale"])
        hut_reflection(surf, h["cx"], h["deck_y"], int(half_w * 1.7),
                       h["scale"], horizon)
        post_len = max(m(26), int(m(70) * h["scale"]))
        depth_t = max(0.0, min(1.0, (h["deck_y"] / DH - 0.55) / 0.31))
        ring_scale = 1.0 + 0.45 * depth_t
        draw_stilts(surf, h["cx"], h["deck_y"], half_w, post_len, ring_scale)
        if h["group"] in CLOSED_GROUPS:
            draw_hut_closed(surf, h["cx"], h["deck_y"], h["scale"], style)
        else:
            draw_hut(surf, h["cx"], h["deck_y"], h["scale"], h["group"],
                     h["label"], hero=h["hero"])
            if h["hero"]:
                L._hut_label(surf, h["label"], h["cx"],
                             h["deck_y"] - int(m(16) * h["scale"]), h["scale"], True)

    draw_pip(surf, int(DW * 0.50), int(DH * 0.285))
    draw_header(surf)

    vig = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for y in range(DH):
        f = y / DH
        a = 0
        if f < 0.10:
            a += int(70 * (1 - f / 0.10) ** 1.4)
        pygame.draw.line(vig, (8, 6, 24, a), (0, y), (DW, y))
    surf.blit(vig, (0, 0))
    side = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for x in range(DW):
        d = abs(x - DW / 2) / (DW / 2)
        a = int(48 * d ** 2.4)
        pygame.draw.line(side, (8, 6, 24, a), (x, 0), (x, DH))
    surf.blit(side, (0, 0))
    return surf


# =============================================================================
# Comparison sheet: 5 full hubs in a row + a bottom strip of a zoomed close-up
# of one closed stall per candidate.
# =============================================================================
def main():
    L._build_static_sky()

    # Render the 5 full hubs at device res, downscale each to 360x640.
    tiles = {}
    for style in CLOSED_ORDER:
        dev = render_hub(style)
        tiles[style] = downscale(dev, 1)          # 360x640 each

    tw, th = tiles[CLOSED_ORDER[0]].get_size()    # 360 x 640

    # Layout: a row of 5 hubs, a title chip band above the row, and a bottom
    # strip with one zoomed closed-stall crop per candidate.
    n = len(CLOSED_ORDER)
    gap = 24
    margin = 34
    title_h = 64
    # zoom strip + a grayscale (colorblind) check strip below it
    zoom_h = 300
    zoom_gap = 20
    gray_h = 200
    gray_gap = 16

    row_w = n * tw + (n - 1) * gap
    sheet_w = margin * 2 + row_w
    sheet_h = (margin + title_h + th + zoom_gap + zoom_h
               + gray_gap + gray_h + margin)

    # Build the sheet at 1x logical then supersample text via the SS font at m().
    # Simpler: build the sheet at device scale for crisp chrome, then this is the
    # deliverable directly (no further downscale needed — it's already 1x tiles).
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((14, 12, 26))
    # subtle vertical grade on the sheet backdrop
    for y in range(sheet_h):
        t = y / sheet_h
        col = lerp_color((16, 14, 30), (8, 7, 18), t)
        pygame.draw.line(sheet, col, (0, y), (sheet_w, y))

    # For crisp chrome we need SS text; render chips onto a small SS surface and
    # blit down. Build a helper surface per chip at device scale.
    def chip(text):
        f = font(11)
        cw = _glyph_base(text, f, m(1.2)).get_width() + m(28)
        ch = int(m(24))
        cs = pygame.Surface((cw, ch), pygame.SRCALPHA)
        rr = cs.get_rect()
        surf_rad = ch // 2
        cs.blit(vgrad(cw, ch, surf_rad, (44, 30, 18), (24, 15, 8)), (0, 0))
        top_sheen(cs, rr, surf_rad, ch // 2, peak=46)
        pygame.draw.rect(cs, (0, 0, 0, 190), rr, width=max(1, m(1.4)),
                         border_radius=surf_rad)
        bevel_rim(cs, rr, surf_rad, (60, 38, 14), (*GOLD_PALE, 230), w=max(1, m(1.2)))
        gradient_text(cs, text, f, rr.center, GOLD_A_TOP, GOLD_A_BOT,
                      weight=m(1.0), keyline=(40, 22, 12), kw=m(1.0), shadow=False,
                      tracking=m(1.2))
        # downscale chip to 1x-ish (SS=4) so it matches the tile scale
        return pygame.transform.smoothscale(
            cs, (cw // SS, ch // SS))

    # zoom crops: pick the closed stall to feature per style. ANIMALS is back-
    # centre (0.5, 0.548) — a clean isolated hut. Crop around its front.
    # Compute the crop box in 1x tile space from the LAYOUT fraction.
    crop_group_fx, crop_group_fy, crop_scale = 0.500, 0.548, 0.80
    # a wider stall for the crop reads better on the mid row: use SHADES
    # (0.5, 0.704, 0.86) — larger + more front detail.
    crop_group_fx, crop_group_fy, crop_scale = 0.500, 0.704, 0.86
    cxp = int(tw * crop_group_fx)
    deckp = int(th * crop_group_fy)
    half_wp = int(58 * crop_scale)          # 1x logical half width
    body_hp = int(64 * crop_scale)
    crop = pygame.Rect(cxp - half_wp - 14, deckp - body_hp - 46,
                       (half_wp + 14) * 2, body_hp + 60)
    crop.clamp_ip(pygame.Rect(0, 0, tw, th))

    def grayscale(src):
        """Luminance-desaturate a surface so the AD can confirm each closed stall
        still reads as CLOSED with colour stripped (pattern/value, not hue). Uses
        pygame's built-in transform so the harness stays numpy-free."""
        return pygame.transform.grayscale(src)

    x = margin
    y = margin + title_h
    for style in CLOSED_ORDER:
        tile = tiles[style]
        # frame the tile
        fr = pygame.Rect(x - 4, y - 4, tw + 8, th + 8)
        pygame.draw.rect(sheet, (*GOLD, 70), fr, width=2, border_radius=8)
        sheet.blit(tile, (x, y))
        # title chip centered above
        c = chip(CLOSED_TITLES[style])
        sheet.blit(c, (x + tw // 2 - c.get_width() // 2,
                       margin + (title_h - c.get_height()) // 2))
        # zoom crop below, scaled up to fill the zoom strip width of one column
        sub = tile.subsurface(crop).copy()
        zoom_scale = min((tw) / crop.w, zoom_h / crop.h)
        zw = int(crop.w * zoom_scale)
        zh = int(crop.h * zoom_scale)
        zimg = pygame.transform.smoothscale(sub, (zw, zh))
        zx = x + (tw - zw) // 2
        zy = y + th + zoom_gap
        zfr = pygame.Rect(zx - 3, zy - 3, zw + 6, zh + 6)
        pygame.draw.rect(sheet, (*GOLD_PALE, 90), zfr, width=2, border_radius=8)
        sheet.blit(zimg, (zx, zy))
        # grayscale (colorblind) check of the same crop below the zoom
        gsub = grayscale(sub)
        gscale = min(tw / crop.w, gray_h / crop.h)
        gw = int(crop.w * gscale)
        gh = int(crop.h * gscale)
        gimg = pygame.transform.smoothscale(gsub, (gw, gh))
        gxp = x + (tw - gw) // 2
        gyp = zy + zoom_h + gray_gap
        gfr = pygame.Rect(gxp - 2, gyp - 2, gw + 4, gh + 4)
        pygame.draw.rect(sheet, (150, 150, 158, 120), gfr, width=1, border_radius=6)
        sheet.blit(gimg, (gxp, gyp))
        x += tw + gap

    pygame.image.save(sheet, os.path.join(_HERE, "round_2@2x.png"))
    half = pygame.transform.smoothscale(
        sheet, (sheet.get_width() // 2, sheet.get_height() // 2))
    pygame.image.save(half, os.path.join(_HERE, "round_2.png"))
    print("SS =", SS, "tile =", tw, "x", th, "sheet =", sheet_w, "x", sheet_h)
    print("saved round_2.png +  round_2@2x.png")


if __name__ == "__main__":
    main()
