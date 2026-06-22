"""IRON RONIN — armored samurai-ninja candidate (scratch exploration).

The "heavy/boss" counterweight to the sleek wrap builds. The whole bird is
re-plumaged to dark oxblood/iron via a darkened base palette so no scarlet
macaw leaks through to fight the costume; over that sit deep-lacquer plates
(darker than native scarlet), a welded iron+gold kabuto bowl crowned by the
gold crescent maedate, and flared sode pauldrons that throw the shoulder line
wider than the belly. Gold lacing dots + the crescent are the only brights, so
the 40px read is WIDE-SHOULDERED + GOLD-CROWNED + DARK — not "red bird with a
hat". Exploration only; nothing here is registered in store_skins.BUILDERS and
the live skin_ninja is untouched.
"""
import math
import pygame

from game import store_skins
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette

HX = store_skins.HX
HY = store_skins.HY
CROWN_Y = store_skins.CROWN_Y
_poly = store_skins._poly

# Sanada-style red-lacquer + iron palette. Deep oxblood, pushed well below
# native macaw scarlet so the plates read as iron-backed armor laid over the
# body rather than fusing with it; gold trim is the unifying bright the read
# leans on — gold-on-dark survives the downscale far better than gold-on-red.
LAC    = (110, 22, 34)        # #6E1622 deep oxblood lacquer plate
LAC_D  = (61, 14, 24)         # #3D0E18 lacquer shadow
LAC_H  = (150, 44, 54)        # muted lacquer specular so each slat still reads
IRON   = (17, 19, 26)         # #11131A helmet iron + under-cloth
IRON_H = (54, 58, 72)         # iron edge so the black survives day sky
GOLD   = (227, 178, 60)       # #E3B23C crest + lacing dots + menpo trim
GOLD_H = (255, 226, 150)      # gold highlight bead
STEEL  = (217, 220, 227)      # #D9DCE3 blade glint

# Darkened macaw under-body. Oxblood-on-iron everywhere so the bird that shows
# between the plates is the same dark armor value, never bright scarlet plumage.
# Beak kept iron so the gold trim owns the only warm-bright on the head.
P_RONIN = _pal(
    tail=[(40, 14, 20), (54, 16, 24), (70, 20, 30), (88, 26, 36)],
    tail_line=(28, 10, 16),
    body_shadow=(34, 12, 18), body_main=(70, 20, 30),
    body_chest=(86, 26, 36), body_belly=(64, 18, 26),
    sheen=(150, 60, 70, 60),
    wing_main=(48, 16, 24), wing_dark=(26, 10, 16), wing_tip=(70, 22, 30),
    wing_secondary=None, wing_highlight=(110, 40, 48),
    head_shadow=(34, 12, 18), head_main=(72, 22, 32),
    head_cheek=(92, 30, 38), head_crown=(58, 18, 26),
    lens_frame=(40, 30, 18), lens_body=(14, 12, 16),
    lens_tint=None, lens_glint=None,
    beak_main=(36, 34, 40), beak_dark=(16, 16, 20), beak_gloss=(86, 86, 96),
    foot=(30, 26, 24),
)


def _ronin_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, P_RONIN, draw_lenses=False)


def _slat_plate(surf, x, y, w, rows, *, slat_h=4, gap=1, lace=True):
    """A stacked-lacquer panel: `rows` horizontal oxblood slats, each its own
    dark base + lit lacquer face + a row of gold lacing dots. The shared motif
    of every armored piece (sode, do, tare) so they read as one suit."""
    for r in range(rows):
        ry = y + r * (slat_h + gap)
        pygame.draw.rect(surf, LAC_D, (x, ry, w, slat_h))
        pygame.draw.rect(surf, LAC, (x, ry, w, slat_h - 1))
        pygame.draw.line(surf, LAC_H, (x + 1, ry), (x + w - 2, ry), 1)
        if lace:
            n = max(2, w // 6)
            for i in range(n):
                dx = x + 3 + int((w - 6) * (i / max(1, n - 1)))
                pygame.draw.circle(surf, GOLD, (dx, ry + slat_h - 2), 1)


def _paint(surf, _wing_angle_deg):
    # ── Back: katana as a short, clearly-anchored diagonal dark bar with a
    # single steel tip crossing the back plate — no floating pommel circle that
    # reads as a loose gold coin. It tucks behind the body mass.
    g_x, g_y = HX - 14, HY + 14         # hilt root, behind the near shoulder
    t_x, t_y = HX + 6, CROWN_Y - 2      # steel tip, just past the crown
    ux, uy = t_x - g_x, t_y - g_y
    pygame.draw.line(surf, IRON, (g_x, g_y), (t_x, t_y), 5)
    pygame.draw.line(surf, IRON_H, (g_x, g_y), (t_x, t_y), 3)
    # One short bound-hilt gold wrap at the root + a steel tip cap (no pommel).
    pygame.draw.line(surf, GOLD, (g_x, g_y), (g_x + ux * 0.18, g_y + uy * 0.18), 2)
    pygame.draw.line(surf, STEEL, (t_x - ux * 0.22, t_y - uy * 0.22), (t_x, t_y), 2)

    # ── Wing/back as a dark LACQUER PLATE, not a flame: the brightest motion
    # element is armor. A small dark slat panel tucked high behind the far sode
    # with a single gold rim so it never out-shouts the crest or droops the mass
    # below the shoulder line.
    _slat_plate(surf, HX - 22, HY - 1, 13, 3, slat_h=4, gap=1)
    pygame.draw.line(surf, GOLD, (HX - 22, HY - 2), (HX - 22, HY + 11), 1)

    # ── Shoulders: two sode pauldrons FLARED hard past the body outline — the
    # silhouette-widening "boss" tell. Anchors are pushed outboard and the top
    # edge angles UP so the shoulder line rises above the body crown, making the
    # 40px silhouette visibly wider at the shoulders than at the belly. Both are
    # lifted to shoulder height (top ~HY-8) so the widest mass is up top.
    # Far (left) sode — flared out to ~HX-32.
    _slat_plate(surf, HX - 33, HY - 8, 18, 4)
    pygame.draw.line(surf, IRON, (HX - 33, HY - 9), (HX - 15, HY - 11), 2)
    pygame.draw.line(surf, GOLD, (HX - 33, HY - 9), (HX - 33, HY + 7), 1)

    # ── Body: do (chest cuirass) — stacked lacquer rows with bright lacing,
    # the heavy core mass under the head; kept narrower than the flared sode.
    _slat_plate(surf, HX - 13, HY + 7, 24, 4, slat_h=4, gap=1)
    # Obi sash peeking below the cuirass (dark, with one gold edge line).
    pygame.draw.rect(surf, IRON, (HX - 12, HY + 28, 22, 4))
    pygame.draw.rect(surf, GOLD, (HX - 12, HY + 28, 22, 1))

    # Near (right) sode — flared out to ~HX+31, lifted to shoulder height, drawn
    # after the do so it overlaps the body edge like a real pauldron.
    _slat_plate(surf, HX + 13, HY - 7, 18, 4)
    pygame.draw.line(surf, IRON, (HX + 13, HY - 8), (HX + 31, HY - 10), 2)
    pygame.draw.line(surf, GOLD, (HX + 31, HY - 8), (HX + 31, HY + 10), 1)

    # ── Face: a single dark menpo block over the lower beak with one horizontal
    # gold trim line — no fang detail (it dissolves at 40px). A small tare slat
    # below grounds it to the throat.
    menpo = [(HX - 9, HY + 1), (HX + 14, HY - 1), (HX + 13, HY + 9),
             (HX - 8, HY + 10)]
    _poly(surf, IRON, menpo)
    _poly(surf, IRON_H, [(HX - 9, HY + 1), (HX + 14, HY - 1), (HX + 13, HY + 3),
                         (HX - 8, HY + 4)])
    pygame.draw.line(surf, GOLD, (HX - 8, HY + 3), (HX + 12, HY + 1), 1)
    _slat_plate(surf, HX - 6, HY + 11, 14, 2, slat_h=3, gap=1, lace=False)

    # Warm eye-glints above the mask so the face still reads "alive" under iron.
    pygame.draw.circle(surf, (255, 232, 180), (HX + 8, HY - 3), 2)
    pygame.draw.circle(surf, (210, 150, 70), (HX + 8, HY - 3), 1)

    # ── Head: a WELDED kabuto. A solid iron+gold helmet bowl rises from the brow
    # band up to the crest mount with NO sky between band and crest, so the gold
    # arc + dark dome read as one helmeted head at 40px.
    by = CROWN_Y + 2
    # Iron bowl: a filled dome from the brow up over the crown.
    pygame.draw.ellipse(surf, IRON, (HX - 13, CROWN_Y - 7, 26, 20))
    pygame.draw.ellipse(surf, IRON_H, (HX - 11, CROWN_Y - 6, 22, 9))
    # Gold brow band riveted across the bowl front.
    pygame.draw.line(surf, GOLD, (HX - 12, by), (HX + 12, by - 2), 3)
    pygame.draw.line(surf, GOLD_H, (HX - 10, by - 1), (HX + 4, by - 2), 1)
    for rx in (HX - 8, HX, HX + 8):
        pygame.draw.circle(surf, GOLD_H, (rx, by - 1), 1)
    # A short gold mount stem from the bowl top up to the crescent, so the crest
    # sits ON the dome (no floating gap).
    mount_y = CROWN_Y - 6
    pygame.draw.line(surf, GOLD, (HX, CROWN_Y - 2), (HX, mount_y), 3)
    pygame.draw.line(surf, GOLD_H, (HX, CROWN_Y - 2), (HX, mount_y), 1)

    # Crescent maedate: an outer gold horn-arc minus an inner cut, rising high
    # above the welded bowl. Built as a thick gold arc with a dark relief inside.
    cx, cy = HX, mount_y
    crescent = []
    R, r = 13, 8
    for a in range(150, 391, 10):            # outer sweep, opening downward
        rad = math.radians(a)
        crescent.append((cx + R * math.cos(rad), cy - 9 + R * math.sin(rad)))
    for a in range(390, 149, -10):           # inner sweep back
        rad = math.radians(a)
        crescent.append((cx + r * math.cos(rad), cy - 7 + r * math.sin(rad)))
    _poly(surf, GOLD, crescent)
    # Re-trace the outer rim brighter so the points survive the downscale.
    rim = [crescent[i] for i in range(0, 25)]
    if len(rim) >= 2:
        pygame.draw.lines(surf, GOLD_H, False, rim, 1)
    # Sharpen the two horn tips into bright points.
    pygame.draw.circle(surf, GOLD_H, (int(cx - R + 1), int(cy - 9)), 2)
    pygame.draw.circle(surf, GOLD_H, (int(cx + R - 1), int(cy - 9)), 2)


build = store_skins._make_skin(_paint, base_fn=_ronin_base)
