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

ROUND 2 (per art-director ITERATE): the costume is cut to THREE clear 40px
ideas — (1) ringed braids trailing, (2) teal-rimmed shield front, (3) leather
tunic mass on the chest. Braids are rebuilt as bead-on-a-string VALUE CHUNKS
(alternating 2px dark/sheen blocks) with three gold rings each, splayed wide so
two distinct trailing elements read off the tail. The tunic is raised + widened
to cover the upper chest (front-centre value goes scarlet→leather), its cross-
lacing collapsed to one bold seam + two gold lace-points. The shield gets a
clean 2px bright iron rim, its spokes cut 4→2, a darker + bluer teal face
(#2A6F7E) that won't camouflage on foliage, and a +1px boss hotspot. The
circlet is committed (3px iron + proud gold cabochon); the feather winglet,
seax gold, belt-stud glints and bracer straps are all demoted to texture.
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
# Shield teal pushed COOLER/bluer than #2C7A6B so the disc never camouflages
# against the gameplay foliage greens: a darker blue-green face under a clean
# bright iron rim reads as a painted shield, not a coin or a leaf clump.
TEAL    = (42, 111, 126)      # #2A6F7E shield-paint, the only cool mass
TEAL_D  = (24, 70, 82)        # teal shadow
TEAL_H  = (96, 178, 192)      # teal highlight
SKIN    = (232, 201, 160)     # #E8C9A0 braid sheen + highlight
FUR     = (214, 198, 170)     # pale fur trim on the pauldron
FUR_D   = (150, 134, 110)


def _braid(surf, pts, w):
    """A thick battle-braid drawn as BEAD-ON-A-STRING value chunks, not a smooth
    ribbon: the dark core lays the rope, then alternating wide dark/sheen blocks
    march down it so the plait reads as segmented hair at 40px (the ninja
    headband-tail contrast discipline). Gold rings clamp the chunk joints — the
    rings are the actual "braid" signal once the body downscales. The single
    trailing motion element, so it gets the warmest sheen to stay legible against
    the body or the sky it whips across."""
    pygame.draw.lines(surf, LEATHER_D, False, pts, w + 2)
    pygame.draw.lines(surf, LEATHER, False, pts, w)

    # Walk the polyline at a fixed bead pitch, stamping 2px-wide value blocks that
    # alternate shadow / warm sheen — chunky lumps the downscale keeps, where 1px
    # cross-ticks would dissolve into a flat smear.
    seglens = []
    total = 0.0
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        d = math.hypot(bx - ax, by - ay)
        seglens.append(d)
        total += d

    def _at(dist):
        run = 0.0
        for i in range(len(pts) - 1):
            if run + seglens[i] >= dist or i == len(pts) - 2:
                f = 0.0 if seglens[i] == 0 else (dist - run) / seglens[i]
                ax, ay = pts[i]
                bx, by = pts[i + 1]
                # Perpendicular of this segment, for laying a block across the rope.
                dx, dy = bx - ax, by - ay
                dl = math.hypot(dx, dy) or 1.0
                return (ax + dx * f, ay + dy * f, -dy / dl, dx / dl)
            run += seglens[i]
        ax, ay = pts[-1]
        return (ax, ay, 0.0, 1.0)

    pitch = 4.0                       # bead spacing — lumps wide enough to hold
    half = w / 2.0
    n = max(2, int(total / pitch))
    ring_steps = {n // 4, n // 2, (3 * n) // 4}   # THREE gold rings at the joints
    for s in range(1, n):
        d = s * pitch
        x, y, px, py = _at(d)
        col = LEATHER_D if s % 2 == 0 else SKIN
        pygame.draw.line(surf, col, (int(x - px * half), int(y - py * half)),
                         (int(x + px * half), int(y + py * half)), 2)
        if s in ring_steps:
            pygame.draw.circle(surf, GOLD, (int(x), int(y)), 3)
            pygame.draw.circle(surf, GOLD_H, (int(x - 1), int(y - 1)), 1)


def _paint(surf, wing_angle_deg):
    # Braids flick with the wing beat (the ninja-tail idiom): the base wing
    # angles run negative-on-downbeat, so a small share reads as the plaits
    # whipping behind the dive — the most dynamic element on the bird.
    flick = int(round(wing_angle_deg * 0.16))

    # ── BACK (drawn FIRST so the body overlaps their roots): two long battle-
    # braids streaming back past the tail, away from the body into open sky so
    # they read as motion, not body lines. The two end-points are SPLAYED wide in
    # Y so there are clearly TWO trailing braids, not one smear off the tail — the
    # upper sweeps shallow-up, the lower plunges far down-left and flicks harder,
    # breaking the egg silhouette where nothing else does.
    root_x, root_y = HX - 9, CROWN_Y + 6        # back-of-skull anchor
    upper = [(root_x, root_y - 1),
             (root_x - 13, root_y - 2 + flick),
             (root_x - 25, root_y + 1 + flick * 2),
             (root_x - 35, root_y + 6 + flick * 2)]
    lower = [(root_x + 1, root_y + 5),
             (root_x - 12, root_y + 15 + flick),
             (root_x - 23, root_y + 28 + flick * 2),
             (root_x - 31, root_y + 40 + flick * 3)]
    _braid(surf, lower, 5)
    _braid(surf, upper, 5)

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

    # ── BODY: leather corset-tunic raised + widened to cover the UPPER CHEST, so
    # the front-centre value of the bird turns from scarlet to a solid leather-
    # brown block — the third clear 40px idea (leather tunic mass on the chest)
    # alongside the trailing braids and the forward shield. It's a value block
    # first; detail is demoted to a single bold central seam.
    # Top edge rises to the collarbone (HY-1) and the left edge pushes back over
    # the breast so the whole front-centre mass — not just the belly — turns
    # leather-brown. A slight inward bevel at the top-left reads as the curve of
    # the chest under the corset rather than a flat slab.
    cx, cy, cw, ch = HX - 18, HY - 1, 31, 31
    _poly(surf, LEATHER_D, [(cx + 3, cy + 2), (cx + cw + 1, cy),
                            (cx + cw - 2, cy + ch), (cx + 2, cy + ch)])
    _poly(surf, LEATHER, [(cx + 4, cy + 3), (cx + cw, cy + 1),
                          (cx + cw - 3, cy + ch - 1), (cx + 3, cy + ch - 1)])
    pygame.draw.line(surf, LEATHER_H, (cx + 5, cy + 3), (cx + cw - 2, cy + 1), 1)
    # ONE bold central seam down the chest (dark channel + warm-tan sheen rail) so
    # the leather mass reads as a laced corset front without a busy ladder.
    seam_x = HX - 1
    pygame.draw.line(surf, LEATHER_D, (seam_x, cy + 3), (seam_x, cy + ch - 2), 3)
    pygame.draw.line(surf, SKIN, (seam_x, cy + 4), (seam_x, cy + ch - 3), 1)
    # Two gold lace-points pinning the seam — the chest's only brights, tying to
    # the gold family (rings + boss + buckle) without competing with the boss.
    for ly in (cy + 6, cy + ch - 6):
        pygame.draw.circle(surf, GOLD, (seam_x, ly), 2)
        pygame.draw.circle(surf, GOLD_H, (seam_x - 1, ly - 1), 1)
    # Studded belt + gold buckle at the waist.
    by = cy + ch
    pygame.draw.line(surf, LEATHER_D, (cx + 1, by), (cx + cw - 1, by - 1), 4)
    pygame.draw.line(surf, LEATHER_H, (cx + 2, by - 1), (cx + cw - 2, by - 2), 1)
    # Belt studs demoted to dim texture (mid-iron, not glint) so they don't read as
    # competing brights against the gold family at 40px.
    for sx in range(cx + 4, cx + cw - 2, 5):
        pygame.draw.circle(surf, IRON, (sx, by - 1), 1)
    pygame.draw.rect(surf, GOLD, (HX - 2, by - 3, 5, 5))
    pygame.draw.rect(surf, LEATHER_D, (HX, by - 1, 1, 1))
    pygame.draw.circle(surf, GOLD_H, (HX - 1, by - 2), 1)

    # ── BELT: a short seax knife slung at the waist, fully DEMOTED to texture — a
    # low-value leather sheath with a dim iron pommel, no gold, so it never adds a
    # bright that competes with the three carrying ideas (braids, shield, tunic).
    sx0, sy0 = HX + 6, by + 1
    sx1, sy1 = HX + 13, by + 8
    pygame.draw.line(surf, LEATHER_D, (sx0, sy0), (sx1, sy1), 4)   # sheath
    pygame.draw.line(surf, LEATHER, (sx0, sy0), (sx1, sy1), 2)
    pygame.draw.circle(surf, IRON, (sx0 - 1, sy0 - 1), 2)          # dim pommel

    # ── WING/LEG: leather bracer/vambrace on the near wing root, demoted to a
    # plain warm cuff (strap ticks cut to texture) so the wing reads as a bound
    # forearm without adding lines that compete at 40px.
    brx, bry = 40, 47
    pygame.draw.line(surf, LEATHER_D, (brx - 6, bry + 2), (brx + 7, bry - 2), 6)
    pygame.draw.line(surf, LEATHER, (brx - 6, bry + 2), (brx + 7, bry - 2), 4)
    pygame.draw.line(surf, LEATHER_D, (brx + 1, bry + 1), (brx + 2, bry - 4), 1)
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
    # Teal painted face — sat darker so the bright iron rim and gold boss carry the
    # contrast; the cooler-bluer teal keeps the disc off the foliage greens.
    pygame.draw.circle(surf, TEAL_D, (scx, scy), sr - 2)
    pygame.draw.circle(surf, TEAL, (scx, scy - 1), sr - 4)
    pygame.draw.circle(surf, TEAL_H, (scx - 3, scy - 4), 3)        # upper-left sheen
    # ONE iron cross (two planks, not four) from the boss to the rim — enough to
    # say "painted war-shield" without the spokes muddying the disc at 40px.
    for a in (0, 90, 180, 270):
        rad = math.radians(a)
        ex = scx + (sr - 2) * math.cos(rad)
        ey = scy + (sr - 2) * math.sin(rad)
        pygame.draw.line(surf, IRON_D, (scx, scy), (int(ex), int(ey)), 2)
        pygame.draw.line(surf, IRON_H, (scx, scy), (int(ex), int(ey)), 1)
    # Clean 2px BRIGHT iron rim re-traced so the disc edge reads as a forged shield
    # ring — not a coin or a bubble — and survives the downscale.
    pygame.draw.circle(surf, IRON_H, (scx, scy), sr, 2)
    # Gold boss dome dead-centre — the shield's single brightest note, +1px so the
    # hotspot holds at gameplay size.
    pygame.draw.circle(surf, IRON_D, (scx, scy), 6)
    pygame.draw.circle(surf, GOLD, (scx, scy), 5)
    pygame.draw.circle(surf, GOLD_H, (scx - 1, scy - 1), 2)
    pygame.draw.circle(surf, (255, 252, 240), (scx - 1, scy - 2), 2)

    # ── HEAD: COMMITTED iron circlet / browband across the crown — no horns, and
    # the feather winglet is cut so those pixels go to braid clarity. A solid 3px
    # iron band (dark base + lit band + edge glint) anchored by a proud bright gold
    # cabochon dot dead-centre on the brow — the circlet's single bright, tying the
    # head to the gold family. The face stays fully open so Pip still reads as Pip.
    cyb = CROWN_Y + 3
    pygame.draw.line(surf, IRON_D, (HX - 12, cyb + 1), (HX + 12, cyb), 5)
    pygame.draw.line(surf, IRON, (HX - 12, cyb), (HX + 12, cyb - 1), 3)
    pygame.draw.line(surf, IRON_H, (HX - 10, cyb - 1), (HX + 8, cyb - 2), 1)
    # Proud gold cabochon centred on the circlet brow — anchor of the committed band.
    pygame.draw.circle(surf, IRON_D, (HX, cyb - 1), 3)
    pygame.draw.circle(surf, GOLD, (HX, cyb - 1), 2)
    pygame.draw.circle(surf, GOLD_H, (HX - 1, cyb - 2), 1)
    pygame.draw.circle(surf, (255, 252, 240), (HX - 1, cyb - 2), 1)


build = store_skins._make_skin(_paint)
