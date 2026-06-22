"""SHIELDMAIDEN FREYA — braided warrior-maiden candidate (scratch exploration).

The agile counterweight to the bulky horned raiders. The read is carried by a
hard left/right break no other viking take has: two long battle-braids
streaming BACK past the tail (animated off the wing beat, like the shipped
ninja's headband tails) under a slim iron circlet — and a round teal shield
held up FRONT past the near wing. Braids-back + shield-front gives a fast,
forward-leaning body language the wide raiders can't. The teal shield-paint is
the cool pop that separates this maiden from the warm brown raiders at 40px.

The face stays OPEN (no horns, no full helm) so Pip still reads as Pip; the
silhouette breakers are the trailing braids and the forward disc, kept 2px-min
and value-separated from the scarlet body. Exploration only; nothing here is
registered in store_skins.BUILDERS and the live skin_viking is untouched.
"""
import math
import pygame

from game import store_skins

HX = store_skins.HX
HY = store_skins.HY
CROWN_Y = store_skins.CROWN_Y
_poly = store_skins._poly

# Palette per brief. Iron is the cool circlet/shield-rim metal; leather is the
# warm tunic + pauldron; gold ties the braid-rings + boss + buckle into one
# bright family; teal is the single cool shield-paint pop; skin is the warm
# braid-sheen / highlight. Each object leans on ONE bright so the stack of
# many small pieces survives the downscale.
IRON    = (138, 144, 153)     # #8A9099 circlet + shield rim (lifted a touch)
IRON_D  = (86, 92, 102)       # iron shadow
IRON_H  = (206, 212, 222)     # iron edge glint so metal survives day sky
LEATHER = (107, 74, 46)       # #6B4A2E tunic + pauldron
LEATHER_D = (66, 45, 28)      # leather shadow / lacing channel
LEATHER_H = (150, 110, 72)    # leather highlight
GOLD    = (201, 162, 75)      # #C9A24B braid-rings + boss + buckle
GOLD_H  = (245, 214, 140)     # gold highlight bead
TEAL    = (44, 122, 107)      # #2C7A6B shield-paint, the cool pop
TEAL_D  = (26, 82, 72)        # teal shadow
TEAL_H  = (92, 178, 160)      # teal highlight
SKIN    = (232, 201, 160)     # #E8C9A0 braid sheen + highlight
FUR     = (214, 198, 170)     # pale fur trim on the pauldron
FUR_D   = (150, 134, 110)


def _braid(surf, pts, w, ring_ys):
    """A thick rope-braid drawn as a tapering dark core + a lit warm sheen,
    with gold braid-rings clamped at given indices. The single trailing motion
    element, so it gets the warmest highlight to stay legible against the body
    or the sky it whips across."""
    pygame.draw.lines(surf, LEATHER_D, False, pts, w + 2)
    pygame.draw.lines(surf, LEATHER, False, pts, w)
    # Warm sheen up the leading edge so the braid reads as hair, not a strap.
    sheen = [(x, y - 1) for x, y in pts]
    pygame.draw.lines(surf, SKIN, False, sheen, max(1, w - 3))
    # Cross-hatch ticks suggest the plait without 1px noise (2px so they hold).
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        for t in (0.4, 0.8):
            mx = int(ax + (bx - ax) * t)
            my = int(ay + (by - ay) * t)
            pygame.draw.line(surf, LEATHER_D, (mx, my - w // 2),
                             (mx, my + w // 2), 1)
    # Gold braid-rings — the bright that ties the trailing mass to the gold family.
    for i in ring_ys:
        rx, ry = pts[i]
        pygame.draw.circle(surf, GOLD, (int(rx), int(ry)), 2)
        pygame.draw.circle(surf, GOLD_H, (int(rx - 1), int(ry - 1)), 1)


def _paint(surf, wing_angle_deg):
    # Braids flick with the wing beat (the ninja-tail idiom): the base wing
    # angles run negative-on-downbeat, so a small share reads as the plaits
    # whipping behind the dive — the most dynamic element on the bird.
    flick = int(round(wing_angle_deg * 0.16))

    # ── BACK (drawn FIRST so the body overlaps their roots): two long battle-
    # braids streaming back past the tail, away from the body into open sky so
    # they read as motion, not body lines. The lower braid trails further and
    # flicks harder, breaking the egg silhouette down-left where nothing else does.
    root_x, root_y = HX - 9, CROWN_Y + 6        # back-of-skull anchor
    upper = [(root_x, root_y),
             (root_x - 12, root_y + 3 + flick),
             (root_x - 24, root_y + 9 + flick * 2),
             (root_x - 33, root_y + 18 + flick * 2)]
    lower = [(root_x + 1, root_y + 4),
             (root_x - 11, root_y + 12 + flick),
             (root_x - 22, root_y + 23 + flick * 2),
             (root_x - 30, root_y + 35 + flick * 3)]
    _braid(surf, lower, 5, ring_ys=(1, 3))
    _braid(surf, upper, 5, ring_ys=(1, 3))

    # ── SHOULDERS: fur-trimmed leather pauldron over the NEAR shoulder. A solid
    # leather cap with a pale fur roll on top so the warm shoulder mass is the
    # anchor the forward shield springs from. Fur roll is the only pale on the
    # warm side, keeping the cool shield distinct.
    pauld = [(HX - 16, HY + 8), (HX - 1, HY + 5), (HX + 2, HY + 14),
             (HX - 15, HY + 18)]
    _poly(surf, LEATHER_D, pauld)
    _poly(surf, LEATHER, [(HX - 15, HY + 9), (HX - 2, HY + 6),
                          (HX + 1, HY + 13), (HX - 14, HY + 16)])
    pygame.draw.line(surf, LEATHER_H, (HX - 14, HY + 10), (HX - 3, HY + 8), 1)
    # Fur roll capping the pauldron — short tufts so it reads furry at size.
    for fx in range(HX - 17, HX, 3):
        pygame.draw.circle(surf, FUR_D, (fx, HY + 8), 2)
        pygame.draw.circle(surf, FUR, (fx, HY + 7), 2)

    # ── BODY: leather corset-tunic with cross-lacing down the front + a studded
    # belt. The lacing is the warm vertical read on the chest; the gold buckle
    # is the body's single bright so it ties to the gold family without competing
    # with the boss.
    cx, cy, cw, ch = HX - 13, HY + 12, 24, 18
    _poly(surf, LEATHER_D, [(cx - 1, cy), (cx + cw + 1, cy),
                            (cx + cw - 2, cy + ch), (cx + 2, cy + ch)])
    _poly(surf, LEATHER, [(cx, cy + 1), (cx + cw, cy + 1),
                          (cx + cw - 3, cy + ch - 1), (cx + 3, cy + ch - 1)])
    pygame.draw.line(surf, LEATHER_H, (cx + 2, cy + 1), (cx + cw - 2, cy + 1), 1)
    # Cross-lacing: two leather rails + X rungs in warm gold-tan so it reads as
    # corset cording, not a ladder. Rungs are 2px so they survive downscale.
    lx0, lx1 = HX - 4, HX + 4
    for i in range(4):
        ry = cy + 3 + i * 3
        pygame.draw.line(surf, LEATHER_D, (lx0, ry), (lx1, ry + 2), 2)
        pygame.draw.line(surf, LEATHER_D, (lx1, ry), (lx0, ry + 2), 2)
        pygame.draw.line(surf, SKIN, (lx0, ry), (lx1, ry + 2), 1)
    pygame.draw.line(surf, LEATHER_D, (lx0, cy + 3), (lx0, cy + 14), 1)
    pygame.draw.line(surf, LEATHER_D, (lx1, cy + 3), (lx1, cy + 14), 1)
    # Studded belt + gold buckle at the waist.
    by = cy + ch
    pygame.draw.line(surf, LEATHER_D, (cx + 1, by), (cx + cw - 1, by - 1), 4)
    pygame.draw.line(surf, LEATHER_H, (cx + 2, by - 1), (cx + cw - 2, by - 2), 1)
    for sx in range(cx + 4, cx + cw - 2, 5):
        pygame.draw.circle(surf, IRON_H, (sx, by - 1), 1)
    pygame.draw.rect(surf, GOLD, (HX - 2, by - 3, 5, 5))
    pygame.draw.rect(surf, LEATHER_D, (HX, by - 1, 1, 1))
    pygame.draw.circle(surf, GOLD_H, (HX - 1, by - 2), 1)

    # ── BELT: a short seax knife slung at the waist — a small dark blade with
    # an iron edge + gold pommel, angled forward under the belt so it reads as a
    # sidearm, not a strap. Kept low-value so it never out-shouts the shield.
    sx0, sy0 = HX + 6, by + 1
    sx1, sy1 = HX + 13, by + 8
    pygame.draw.line(surf, LEATHER_D, (sx0, sy0), (sx1, sy1), 4)   # sheath
    pygame.draw.line(surf, LEATHER, (sx0, sy0), (sx1, sy1), 2)
    pygame.draw.line(surf, IRON_H, (sx0, sy0 - 1), ((sx0 + sx1) // 2, (sy0 + sy1) // 2), 1)
    pygame.draw.circle(surf, GOLD, (sx0 - 1, sy0 - 1), 2)          # pommel
    pygame.draw.circle(surf, GOLD_H, (sx0 - 2, sy0 - 2), 1)

    # ── WING/LEG: leather bracer/vambrace on the near wing root with strap
    # lines, so the wing reads as a bound forearm — a warm cuff that visually
    # links the shield-holding arm to the body without bright accents.
    brx, bry = 40, 47
    pygame.draw.line(surf, LEATHER_D, (brx - 6, bry + 2), (brx + 7, bry - 2), 6)
    pygame.draw.line(surf, LEATHER, (brx - 6, bry + 2), (brx + 7, bry - 2), 4)
    for st in (-3, 1, 5):
        pygame.draw.line(surf, LEATHER_D,
                         (brx + st, bry + 2), (brx + st + 1, bry - 3), 1)
    pygame.draw.line(surf, LEATHER_H, (brx - 5, bry), (brx + 5, bry - 3), 1)

    # ── FRONT (drawn LAST so it sits over the near wing): a round shield held up
    # out past the wing — a face-on teal disc with an iron rim, a bright gold
    # boss centre, and a radial chevron rune motif. This is the focal hero: the
    # only cool mass on the bird, pushed out front-low so it breaks the
    # silhouette to the right/down — the exact opposite side from the braids.
    scx, scy, sr = HX + 14, HY + 16, 13
    # Iron rim ring (drawn as a slightly larger disc the teal face sits inside).
    pygame.draw.circle(surf, IRON_D, (scx, scy), sr + 1)
    pygame.draw.circle(surf, IRON, (scx, scy), sr)
    # Teal painted face.
    pygame.draw.circle(surf, TEAL_D, (scx, scy), sr - 2)
    pygame.draw.circle(surf, TEAL, (scx, scy - 1), sr - 3)
    pygame.draw.circle(surf, TEAL_H, (scx - 3, scy - 4), 3)        # upper-left sheen
    # Radial chevron rune motif: four planks of iron banding from the boss out
    # to the rim, so the face reads as a painted war-shield even at size.
    for a in range(0, 360, 90):
        rad = math.radians(a + 45)
        ex = scx + (sr - 2) * math.cos(rad)
        ey = scy + (sr - 2) * math.sin(rad)
        pygame.draw.line(surf, IRON_D, (scx, scy), (int(ex), int(ey)), 2)
        pygame.draw.line(surf, IRON_H, (scx, scy), (int(ex), int(ey)), 1)
    # Bright iron rim re-traced so the disc edge survives the downscale.
    pygame.draw.circle(surf, IRON_H, (scx, scy), sr, 2)
    pygame.draw.arc(surf, IRON_H, (scx - sr, scy - sr, sr * 2, sr * 2),
                    math.radians(140), math.radians(250), 2)
    # Gold boss dome dead-centre — the shield's single brightest note.
    pygame.draw.circle(surf, IRON_D, (scx, scy), 5)
    pygame.draw.circle(surf, GOLD, (scx, scy), 4)
    pygame.draw.circle(surf, GOLD_H, (scx - 1, scy - 1), 2)
    pygame.draw.circle(surf, (255, 252, 240), (scx - 1, scy - 2), 1)

    # ── HEAD: slim iron circlet / browband across the crown — no horns. A single
    # feather tuft winglet at the far side gives an asymmetric flick that echoes
    # the trailing braids without bulking the helm. The face stays fully open.
    cyb = CROWN_Y + 3
    pygame.draw.line(surf, IRON_D, (HX - 12, cyb + 1), (HX + 12, cyb), 4)
    pygame.draw.line(surf, IRON, (HX - 12, cyb), (HX + 12, cyb - 1), 2)
    pygame.draw.line(surf, IRON_H, (HX - 10, cyb - 1), (HX + 8, cyb - 2), 1)
    # A small gold cabochon centred on the circlet brow.
    pygame.draw.circle(surf, GOLD, (HX, cyb - 1), 2)
    pygame.draw.circle(surf, GOLD_H, (HX - 1, cyb - 2), 1)
    # Feather tuft winglet at the far (left) side, swept up off the circlet.
    tip = (HX - 16, CROWN_Y - 7)
    _poly(surf, IRON_D, [(HX - 11, cyb - 1), (HX - 13, cyb - 4), tip])
    _poly(surf, IRON, [(HX - 11, cyb - 2), (HX - 12, cyb - 4),
                       (tip[0] + 1, tip[1] + 1)])
    pygame.draw.line(surf, IRON_H, (HX - 12, cyb - 3), tip, 1)


build = store_skins._make_skin(_paint)
