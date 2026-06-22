"""IRON RONIN — armored samurai-ninja candidate (scratch exploration).

The "heavy/boss" counterweight to the sleek wrap builds: red-lacquer plate
geometry — flaring sode shoulders, a stacked do cuirass, a fanged menpo, and a
gold crescent maedate arcing past the crown — laid over the base macaw so the
gold-on-red lacquer carries the read at 40px. Exploration only; nothing here is
registered in store_skins.BUILDERS and the live skin_ninja is untouched.
"""
import math
import pygame

from game import store_skins, parrot

HX = store_skins.HX
HY = store_skins.HY
CROWN_Y = store_skins.CROWN_Y
_poly = store_skins._poly

# Sanada-style red-lacquer + iron palette. Gold trim is the unifying bright the
# read leans on; it must out-value the scarlet body so plates don't fuse with it.
LAC    = (161, 27, 46)        # #A11B2E red lacquer plate
LAC_D  = (122, 19, 34)        # #7A1322 lacquer shadow
LAC_H  = (198, 70, 84)        # lacquer specular so each slat reads as plate
IRON   = (17, 19, 26)         # #11131A helmet iron + under-cloth
IRON_H = (54, 58, 72)         # iron edge so the black survives day sky
GOLD   = (227, 178, 60)       # #E3B23C crest + lacing dots + menpo trim
GOLD_H = (255, 226, 150)      # gold highlight bead
STEEL  = (217, 220, 227)      # #D9DCE3 blade glint
STEEL_D = (120, 126, 138)


def _slat_plate(surf, x, y, w, rows, *, slat_h=4, gap=1, lace=True):
    """A stacked-lacquer panel: `rows` horizontal red slats, each its own dark
    base + lit lacquer face + a row of gold lacing dots. The shared motif of
    every armored piece (sode, do, tare) so they read as one suit."""
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
    # ── Back: katana slung lower-diagonal — short + heavy, an armored carry, so
    # it reads as "samurai" rather than the shadow-ninja's long corner bar. Sits
    # under the plates so the body mass owns the foreground.
    g_x, g_y = HX - 20, HY + 16          # hilt pommel (low-left, behind shoulder)
    t_x, t_y = HX + 9, CROWN_Y - 4       # blade tip (up-right past the crown)
    ux, uy = t_x - g_x, t_y - g_y
    ln = math.hypot(ux, uy) or 1.0
    px, py = -uy / ln, ux / ln
    # Lacquered black scabbard under a steel blade glint.
    pygame.draw.line(surf, IRON, (g_x, g_y), (t_x, t_y), 6)
    pygame.draw.line(surf, IRON_H, (g_x, g_y), (t_x, t_y), 4)
    pygame.draw.line(surf, STEEL, (g_x + ux * 0.32, g_y + uy * 0.32),
                     (t_x, t_y), 2)
    pygame.draw.line(surf, GOLD_H, (t_x - ux * 0.18, t_y - uy * 0.18),
                     (t_x, t_y), 1)
    # Square tsuba guard + bound hilt + pommel.
    gxr, gyr = g_x + ux * 0.30, g_y + uy * 0.30
    _poly(surf, GOLD, [(gxr + px * 4, gyr + py * 4),
                       (gxr - px * 4, gyr - py * 4),
                       (gxr - px * 4 + ux * 0.06, gyr - py * 4 + uy * 0.06),
                       (gxr + px * 4 + ux * 0.06, gyr + py * 4 + uy * 0.06)])
    pygame.draw.line(surf, IRON, (g_x, g_y), (gxr, gyr), 5)
    for k in (0.08, 0.16, 0.24):
        wx, wy = g_x + ux * k, g_y + uy * k
        pygame.draw.line(surf, GOLD, (wx + px * 2.5, wy + py * 2.5),
                         (wx - px * 2.5, wy - py * 2.5), 1)
    pygame.draw.circle(surf, GOLD, (int(g_x), int(g_y)), 2)

    # ── Shoulders: two sode plates flaring OUT past the wing/body outline — the
    # silhouette-widening "boss" tell. Far shoulder first so the near one stacks
    # in front of the body.
    _slat_plate(surf, HX - 27, HY - 2, 14, 4)        # far (left) sode, flared out
    pygame.draw.line(surf, IRON, (HX - 27, HY - 3), (HX - 13, HY - 3), 1)

    # ── Body: do (chest cuirass) — stacked lacquer rows with bright lacing,
    # the heavy core mass under the head.
    _slat_plate(surf, HX - 13, HY + 7, 24, 4, slat_h=4, gap=1)
    # Obi sash + hanging tassel peeking below the cuirass.
    pygame.draw.rect(surf, IRON, (HX - 12, HY + 28, 22, 4))
    pygame.draw.rect(surf, GOLD, (HX - 12, HY + 28, 22, 1))
    pygame.draw.line(surf, IRON_H, (HX - 4, HY + 32), (HX - 6, HY + 39), 3)
    pygame.draw.circle(surf, GOLD, (HX - 6, HY + 39), 2)

    # Near (right) sode — flares out past the near wing, drawn after the do so it
    # overlaps the body edge like a real pauldron.
    _slat_plate(surf, HX + 11, HY - 1, 16, 4)
    pygame.draw.line(surf, IRON, (HX + 11, HY - 2), (HX + 27, HY - 2), 1)
    pygame.draw.line(surf, GOLD, (HX + 27, HY - 1), (HX + 27, HY + 17), 1)

    # ── Face: menpo half-mask over the lower beak — iron with a gold trim line
    # and a fanged/snarl lower edge, plus a small stacked-slat throat guard (tare).
    menpo = [(HX - 9, HY + 1), (HX + 13, HY - 1), (HX + 14, HY + 7),
             (HX + 4, HY + 12), (HX - 8, HY + 10)]
    _poly(surf, IRON, menpo)
    _poly(surf, IRON_H, [(HX - 9, HY + 1), (HX + 13, HY - 1), (HX + 12, HY + 3),
                         (HX - 8, HY + 4)])
    pygame.draw.line(surf, GOLD, (HX - 8, HY + 2), (HX + 12, HY), 1)
    # Fanged snarl edge — alternating iron teeth tipped with steel glints.
    for i, fx in enumerate(range(HX - 7, HX + 12, 4)):
        fy = HY + (11 if i % 2 else 9)
        _poly(surf, IRON, [(fx, fy - 3), (fx + 3, fy - 3), (fx + 1, fy)])
        pygame.draw.circle(surf, STEEL, (fx + 1, fy - 2), 1)
    # Throat guard (tare): two short lacquer slats below the snarl.
    _slat_plate(surf, HX - 6, HY + 12, 14, 2, slat_h=3, gap=1, lace=False)

    # Warm eye-glints above the mask so the face still reads "alive" under iron.
    pygame.draw.circle(surf, (255, 232, 180), (HX + 8, HY - 3), 2)
    pygame.draw.circle(surf, (210, 150, 70), (HX + 8, HY - 3), 1)

    # ── Head: kabuto brow band + the gold crescent maedate arcing past the crown
    # (the unmistakable samurai tell at 40px). Brow band welds the crest to the
    # head mass so a dive-tilt can't snap it off.
    by = CROWN_Y + 2
    pygame.draw.line(surf, IRON, (HX - 12, by + 1), (HX + 12, by - 1), 5)
    pygame.draw.line(surf, IRON_H, (HX - 11, by), (HX + 11, by - 2), 2)
    for rx in (HX - 8, HX, HX + 8):
        pygame.draw.circle(surf, GOLD, (rx, by), 1)

    # Crescent maedate: an outer gold horn-arc minus an inner cut, rising high
    # above the crown. Built as a thick gold arc with a dark relief inside.
    cx, cy = HX, by - 1
    pygame.draw.circle(surf, GOLD_H, (cx, cy - 2), 1)   # mount stud
    crescent = []
    R, r = 13, 8
    for a in range(150, 391, 10):            # outer sweep, opening downward
        rad = math.radians(a)
        crescent.append((cx + R * math.cos(rad), cy - 13 + R * math.sin(rad)))
    for a in range(390, 149, -10):           # inner sweep back
        rad = math.radians(a)
        crescent.append((cx + r * math.cos(rad), cy - 11 + r * math.sin(rad)))
    _poly(surf, GOLD, crescent)
    # Re-trace the outer rim brighter so the points survive the downscale.
    rim = [crescent[i] for i in range(0, 25)]
    if len(rim) >= 2:
        pygame.draw.lines(surf, GOLD_H, False, rim, 1)
    # Sharpen the two horn tips into bright points past the crown.
    pygame.draw.circle(surf, GOLD_H, (int(cx - R + 1), int(cy - 13)), 2)
    pygame.draw.circle(surf, GOLD_H, (int(cx + R - 1), int(cy - 13)), 2)


build = store_skins._make_skin(_paint)
