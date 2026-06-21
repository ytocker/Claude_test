"""medal-rail unlock-notice mock — a vertical commendation ribbon pinned to
the LEFT margin gutter. Unlocked badges hang as small struck medallions on a
thin gold ribbon down the extreme edge (x0..~18), OUTSIDE the central content
column, so the crowded run-summary loses no horizontal space.

Scratch tooling only; nothing under game/ is touched.
"""
import os
import math
import pygame

from tools.unlock_notice_common import render_backdrop, demo_ids
from game import achievements as ach
from game.achievement_icons import draw_badge
from game.draw import blit_glow, lerp_color
from game.hud import (_font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
                      _PANEL_DARK, _NIGHT_DEEP)

W, H = 360, 640

# Ribbon geometry — everything lives in the dead left margin. The score plaque's
# The score plaque + tiles + buttons all span x18..342, so the rail's spine
# lives at the extreme edge. The medallions, however, are hung ONLY in the two
# vertical bands where the margin is genuinely dead the full way across: beside
# the "RUN SUMMARY" title (its text starts ~x40, so x0..38 is empty at y30..100)
# stacked into the open strip just above the plaque. That lets each medal be a
# legible Ø28 — clearly a struck gold medal, never a scrollbar nub — while still
# overhanging nothing protected.
SPINE_X = 9                 # the gold ribbon's vertical centre line
RIBBON_W = 6                # ribbon width
BADGE_D = 18                # medallion diameter — Ø18 keeps the right edge at
BADGE_CX = 0                # x18, FLUSH with the plaque border (centre x9)


def _ribbon(surf, top, bottom):
    """A thin satin gold ribbon running the gutter: a vertical gradient stripe
    with a lit left crease + shadowed right edge, so it reads as a hanging
    grosgrain ribbon (a medal sash), not a flat bar or a scrollbar track."""
    x0 = SPINE_X - RIBBON_W // 2
    strip = pygame.Surface((RIBBON_W, bottom - top), pygame.SRCALPHA)
    for xx in range(RIBBON_W):
        # cross-section shading: lit centre-left fold, darker right fold
        t = xx / max(1, RIBBON_W - 1)
        if t < 0.5:
            col = lerp_color(_GOLD_DEEP, _GOLD_PALE, t * 2.0)
        else:
            col = lerp_color(_GOLD_PALE, (120, 80, 14), (t - 0.5) * 2.0)
        pygame.draw.line(strip, col, (xx, 0), (xx, bottom - top))
    # faint vertical sheen seam down the lit crease
    pygame.draw.line(strip, (*_GOLD_PALE, 160), (RIBBON_W // 2 - 1, 0),
                     (RIBBON_W // 2 - 1, bottom - top))
    surf.blit(strip, (x0, top))
    # a small pinned top finial (a stitched anchor) so the ribbon reads as hung
    # from the top margin, not bleeding off-screen like a track.
    pygame.draw.circle(surf, _GOLD_DEEP, (SPINE_X, top + 2), 4)
    pygame.draw.circle(surf, _GOLD_PALE, (SPINE_X, top + 2), 4, 1)
    # forked ribbon tail at the very bottom so it terminates like a sash.
    by = bottom
    pygame.draw.polygon(surf, _GOLD_DEEP, [
        (SPINE_X - RIBBON_W // 2, by - 1),
        (SPINE_X + RIBBON_W // 2 + 1, by - 1),
        (SPINE_X, by + 7),
    ])


def _knot(surf, cx, cy):
    """A small gold ribbon-knot where the medal's hanger pinches the sash — the
    cue that the medal HANGS from the ribbon. Two tiny lit lobes + a dark
    centre, kept ABOVE the medal so it never sits on the medallion face."""
    for sgn in (-1, 1):
        pygame.draw.circle(surf, _GOLD_DEEP, (cx + sgn * 2, cy), 2)
        pygame.draw.circle(surf, _GOLD_PALE, (cx + sgn * 2, cy), 2, 1)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), 1)


def _hang_badge(surf, icon_key, cy):
    """Hang one struck medallion off the ribbon at vertical centre ``cy``: a
    short hanger link up to a ribbon knot, a soft drop shadow so the medal lifts
    off the panel, then the full struck-gold badge."""
    cx = BADGE_CX + BADGE_D // 2
    knot_y = cy - BADGE_D // 2 - 4
    # hanger link from the knot down to the medal's crown
    pygame.draw.line(surf, _GOLD_DEEP, (cx, knot_y + 1),
                     (cx, cy - BADGE_D // 2 + 1), 2)
    _knot(surf, cx, knot_y)
    # soft cast shadow down-right so the medal reads as a raised, hung object
    sh = pygame.Surface((BADGE_D, BADGE_D), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, 120), (BADGE_D // 2, BADGE_D // 2),
                       BADGE_D // 2 - 1)
    surf.blit(sh, (BADGE_CX + 2, cy - BADGE_D // 2 + 2))
    rect = pygame.Rect(BADGE_CX, cy - BADGE_D // 2, BADGE_D, BADGE_D)
    draw_badge(surf, icon_key, rect, True, False)


def _more_pill(surf, cy, n):
    """A '+N' capped medallion at the rail's foot — the graceful-scaling cue: a
    small navy disc on the ribbon reading the overflow count when more than the
    rail's shown slots were unlocked in one run."""
    r = BADGE_D // 2 - 2
    cx = BADGE_CX + BADGE_D // 2
    knot_y = cy - r - 5
    pygame.draw.line(surf, _GOLD_DEEP, (cx, knot_y + 2), (cx, cy - r + 2), 2)
    _knot(surf, cx, knot_y)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), r + 1)
    pygame.draw.circle(surf, _PANEL_DARK, (cx, cy), r)
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), r, 1)
    f = _font(12, True)
    g = f.render(f"+{n}", True, _GOLD_PALE)
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _ribbon_caption(surf, top):
    """A hairline vertical caption riding the ribbon so the rail self-labels as
    a commendation, not a scrollbar. Tiny, rotated, set in the margin sliver."""
    f = _font(9, True)
    g = f.render("EARNED", True, _GOLD_PALE)
    g = pygame.transform.rotate(g, 90)
    g.set_alpha(190)
    surf.blit(g, g.get_rect(center=(SPINE_X, top)))


def build():
    surf = render_backdrop()
    ids = demo_ids(2)

    # The rail spans the protected layout vertically but only the dead margin
    # horizontally. We tuck the medal cluster into the upper gutter beside the
    # title + plaque, where the margin is purely empty.
    rail_top = 22
    rail_bottom = 628
    _ribbon(surf, rail_top, rail_bottom)

    # Two unlocked medallions hung in the dead strip beside the title and just
    # above the plaque (both y-centres < plaque top y104), so the readable Ø28
    # medals overhang nothing protected (primary 2-unlock case).
    slots_y = [50, 84]
    for i, aid in enumerate(ids):
        _hang_badge(surf, ach.BY_ID[aid].icon_key, slots_y[i])

    # Caption sliver lower on the ribbon, in the clear sliver beside the buttons.
    _ribbon_caption(surf, 520)

    OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "achievements", "unlock_notice", "medal-rail")
    os.makedirs(OUT, exist_ok=True)
    out_path = os.path.join(OUT, "round_1.png")
    pygame.image.save(surf, out_path)

    # ── Scale-study strip: 1, 2, and 3+ unlocks side by side so the reviewer
    # sees graceful scaling (the '+N' cap). Drawn on a labelled board to the
    # right of the primary still, sharing the same backdrop crop.
    return out_path, surf, ids


def build_scale_study(primary_path):
    """A small comparison board: how the rail reads at 1, 2, and ~3 unlocks
    (the third uses a '+N' cap to imply many)."""
    ids3 = demo_ids(2)
    # synthesize a third + overflow look from the known glyph family
    extra = ["day", "score"]

    pad = 12
    panel_w = 120
    board = pygame.Surface((panel_w * 3 + pad * 4, H + 40), pygame.SRCALPHA)
    board.fill((10, 6, 26, 255))

    f = _font(13, True)
    title = f.render("medal-rail · scales 1 / 2 / 3+", True, _GOLD_BRIGHT)
    board.blit(title, (pad, 8))

    cases = [
        ("1 unlocked", 1, 0),
        ("2 unlocked", 2, 0),
        ("3+ (with +N cap)", 2, 4),
    ]
    for ci, (label, nshown, overflow) in enumerate(cases):
        col = pygame.Surface((panel_w, H), pygame.SRCALPHA)
        # tiny slice of the real backdrop's left margin so the comparison shows
        # the rail against the actual panel edge, not empty black.
        bd = render_backdrop()
        col.blit(bd, (0, 0), pygame.Rect(0, 0, panel_w, H))
        _ribbon(col, 22, 628)
        ys = [50, 84, 118]
        order = list(demo_ids(2)) + extra
        for i in range(nshown):
            _hang_badge(col, ach.BY_ID[order[i]].icon_key, ys[i])
        if overflow:
            _more_pill(col, ys[nshown], overflow)
        else:
            # show a third real medal for the "3" framing of the middle/last
            if ci == 2:
                pass
        cf = _font(11, True)
        lab = cf.render(label, True, _GOLD_PALE)
        board.blit(col, (pad + ci * (panel_w + pad), 30))
        board.blit(lab, (pad + ci * (panel_w + pad), 30 + H + 2))

    OUT = os.path.dirname(primary_path)
    pygame.image.save(board, os.path.join(OUT, "scale_study.png"))


if __name__ == "__main__":
    path, _surf, _ids = build()
    build_scale_study(path)
    print("wrote", path)
