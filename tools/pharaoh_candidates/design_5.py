"""DESIGN 5 — CLEOPATRA (the royal queen) — scratch costume exploration.

The feminine/regal Egyptian read, cool where the others are warm: a rounded
gold VULTURE/MODIUS crown (domed skullcap + slim sun-disk between two upright
plumes + a small uraeus) hugging the head, the signature swept CLEOPATRA KOHL
EYES (long upturned liner tail + a teal lid accent), a wide BEADED COLLAR in
teal / carnelian-red / gold rows, a warm linen-white SHEATH DRESS painted OVER
the scarlet body (red macaw kept only as thin trim), a golden LOTUS scepter
slung in the wing, and gold anklets + sandal straps at the feet.

This skin PAINTS OVER the scarlet body (no base recolor), so it uses the plain
``_make_skin(_paint)`` factory. The read at 40px is carried by the gold dome +
kohl eyes + the cool teal/carnelian collar — distinct from the warm-gold nemes
and the pointed-ear Anubis. Everything below the head stays strictly INSIDE the
base bird footprint (nothing below the feet line); only the crown rises above
CROWN_Y.

Exploration only — NOT registered in store_skins.BUILDERS.
Render: tools/pharaoh_candidates/render_design_5.py.
"""
from __future__ import annotations

import math

import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# ── palette (cool teal-carnelian queen vs the warm-gold king) ─────────────────
_CL_GOLD    = (233, 196, 106)   # #E9C46A regal gold
_CL_GOLD_D  = (168, 130, 52)    # bronzed shadow so the gold dome holds value
_CL_GLINT   = (255, 244, 198)   # pale gold glint highlight
_CL_TEAL    = (42, 157, 143)    # #2A9D8F signature cool bead
_CL_TEAL_D  = (24, 104, 94)
_CL_CARN    = (193, 69, 59)     # #C1453B carnelian red bead
_CL_CARN_D  = (140, 44, 38)
_CL_KOHL    = (28, 28, 34)      # #1C1C22 kohl black
_CL_LINEN   = (242, 232, 213)   # #F2E8D5 linen sheath
_CL_LINEN_D = (206, 192, 166)   # sheath shadow / fold
_CL_REDTRIM = (176, 52, 48)     # the macaw red kept only as dress trim


def _paint(surf, _a):
    cy = CROWN_Y

    # ── golden LOTUS scepter, slung diagonally INSIDE the wing ────────────────
    # Painted first so the body covers the shaft mid-section; only the gold
    # lotus head and the base knob peek inside the silhouette. The whole staff
    # is tucked above the feet line so nothing dangles past the true footprint.
    lo_top = (HX - 17, HY + 2)    # lotus bloom up near the back shoulder
    lo_bot = (HX - 8, HY + 19)    # base inside the lower body
    pygame.draw.line(surf, _CL_GOLD_D, lo_top, lo_bot, 4)
    pygame.draw.line(surf, _CL_GOLD, lo_top, lo_bot, 2)
    pygame.draw.line(surf, _CL_GLINT, (lo_top[0] + 1, lo_top[1] + 2),
                     (lo_bot[0] + 1, lo_bot[1] - 2), 1)
    # Lotus bloom — a small gold cup of three upright petals so it reads as a
    # flower, not a spearhead. A teal seed-bead at the heart ties it to the
    # collar palette.
    lx, ly = lo_top
    _poly(surf, _CL_GOLD_D, [(lx - 4, ly), (lx + 4, ly), (lx, ly - 7)])      # centre petal
    _poly(surf, _CL_GOLD, [(lx - 3, ly), (lx, ly - 6), (lx - 5, ly - 3)])    # left petal
    _poly(surf, _CL_GOLD, [(lx + 3, ly), (lx, ly - 6), (lx + 5, ly - 3)])    # right petal
    _poly(surf, _CL_GLINT, [(lx - 1, ly - 1), (lx + 1, ly - 1), (lx, ly - 5)])
    pygame.draw.circle(surf, _CL_TEAL, (lx, ly), 1)                          # seed bead
    pygame.draw.circle(surf, _CL_GOLD, (lo_bot[0], lo_bot[1] + 1), 2)        # base knob

    # ── linen SHEATH DRESS painted OVER the scarlet body ──────────────────────
    # A fitted column gown hugging the body, hem held INSIDE the base footprint
    # (~HY+23) so the figure reads at the bird's true size. The macaw red is
    # left only as a thin hem + side trim so the costume still nods to the
    # scarlet skin beneath. Linen is the brightest mass low on the body, which
    # anchors the day read; the bronze fold keeps the value on night.
    sheath = [(HX - 13, HY + 7), (HX - 14, HY + 17), (HX - 10, HY + 23),
              (HX + 7, HY + 23), (HX + 11, HY + 17), (HX + 9, HY + 7)]
    _poly(surf, _CL_LINEN, sheath)
    # Soft central fold + back-edge shadow give the flat gown a little form.
    _poly(surf, _CL_LINEN_D, [(HX - 13, HY + 7), (HX - 14, HY + 17),
                              (HX - 10, HY + 23), (HX - 8, HY + 22),
                              (HX - 11, HY + 16), (HX - 10, HY + 8)])
    pygame.draw.line(surf, _CL_LINEN_D, (HX - 2, HY + 9), (HX - 1, HY + 22), 1)
    # Thin gold shoulder straps framing the linen front into a clear V band.
    pygame.draw.line(surf, _CL_GOLD, (HX - 6, HY + 7), (HX - 3, HY + 22), 2)
    pygame.draw.line(surf, _CL_GOLD, (HX + 6, HY + 7), (HX + 2, HY + 22), 2)
    pygame.draw.line(surf, _CL_GLINT, (HX - 6, HY + 8), (HX - 4, HY + 14), 1)
    # Red macaw kept only as a thin carnelian hem + a side seam — the trim.
    pygame.draw.line(surf, _CL_REDTRIM, (HX - 10, HY + 23), (HX + 7, HY + 23), 2)
    pygame.draw.line(surf, _CL_REDTRIM, (HX + 9, HY + 8), (HX + 11, HY + 17), 1)

    # ── wide BEADED CLEOPATRA COLLAR — teal / carnelian / gold rows ───────────
    # Sits INSIDE the body footprint over the top of the sheath (top ~HY+4,
    # bottom ~HY+13). Concentric arcs of cool teal + carnelian + gold read as a
    # rich usekh gorget at 40px; the cool teal carries the read on a night sky
    # where the gold king's collar would wash to a smear.
    col_cx, col_cy = HX - 2, HY + 4
    for r, col in ((11, _CL_GOLD_D), (10, _CL_GOLD), (8, _CL_CARN),
                   (6, _CL_TEAL), (4, _CL_GOLD)):
        pygame.draw.arc(surf, col, (col_cx - r, col_cy - r + 2, r * 2, r * 2),
                        3.45, 6.1, 2)
    # Bead dots punctuating the outermost row — alternating teal/carnelian so
    # the cool jewelled read survives the downscale.
    for k in range(6):
        a = 3.6 + k * 0.42
        bx = col_cx + 10 * math.cos(a)
        by = col_cy + 10 * math.sin(a) + 2
        bead = _CL_TEAL if k % 2 == 0 else _CL_CARN
        pygame.draw.circle(surf, bead, (int(bx), int(by)), 1)
    # A single carnelian drop pendant at the collar's heart.
    pygame.draw.circle(surf, _CL_CARN, (col_cx, col_cy + 12), 2)
    pygame.draw.circle(surf, _CL_GOLD, (col_cx, col_cy + 12), 2, 1)

    # ── signature CLEOPATRA KOHL EYES on the near eye ─────────────────────────
    # Heavy black liner wrapping the near eye with a long upturned tail flicking
    # back toward the crown, plus a teal lid accent above it — the read that
    # makes her unmistakably the QUEEN. Drawn over the bare macaw eye region.
    ex, ey = HX + 7, HY - 1
    # Teal eyeshadow lid accent (the cool signature) just above the eye.
    pygame.draw.line(surf, _CL_TEAL, (ex - 4, ey - 3), (ex + 3, ey - 4), 2)
    pygame.draw.line(surf, _CL_TEAL_D, (ex - 4, ey - 2), (ex + 2, ey - 3), 1)
    # Kohl rim under + over the eye.
    pygame.draw.line(surf, _CL_KOHL, (ex - 4, ey + 2), (ex + 4, ey + 1), 2)
    pygame.draw.line(surf, _CL_KOHL, (ex - 4, ey - 1), (ex + 3, ey - 2), 1)
    # The long upturned liner tail sweeping back and up toward the temple.
    pygame.draw.lines(surf, _CL_KOHL, False,
                      [(ex + 4, ey + 1), (ex + 8, ey - 2), (ex + 12, ey - 6)], 2)
    pygame.draw.line(surf, _CL_KOHL, (ex + 10, ey - 5), (ex + 13, ey - 7), 1)  # flick tip

    # ── rounded gold VULTURE / MODIUS crown (above CROWN_Y) ───────────────────
    # A domed gold skullcap hugging the head — the hero silhouette, distinct
    # from a flaring nemes or pointed jackal ears by being ROUND. Bronze base
    # dome keeps the gold off a bright sky; a fine glint arc lifts the dome.
    pygame.draw.ellipse(surf, _CL_GOLD_D, (HX - 13, cy - 4, 27, 18))
    pygame.draw.ellipse(surf, _CL_GOLD, (HX - 12, cy - 4, 25, 15))
    pygame.draw.ellipse(surf, _CL_GLINT, (HX - 8, cy - 3, 12, 5), 1)        # dome sheen
    # A jewelled modius band of teal + carnelian beads ringing the cap base.
    for i in range(7):
        bx = HX - 11 + i * 4
        bead = _CL_TEAL if i % 2 == 0 else _CL_CARN
        pygame.draw.circle(surf, bead, (bx, cy + 9), 2)
        pygame.draw.circle(surf, _CL_GOLD_D, (bx, cy + 9), 2, 1)

    # Modius platform on top of the dome carrying the disk + plumes.
    pygame.draw.rect(surf, _CL_GOLD_D, (HX - 7, cy - 7, 14, 4), border_radius=1)
    pygame.draw.rect(surf, _CL_GOLD, (HX - 6, cy - 7, 12, 2), border_radius=1)

    # Two slim upright plumes flanking a central sun-disk — the regal crest that
    # gives the rounded crown a tall, unmistakably royal finial.
    for px, lean in ((HX - 5, -2), (HX + 5, 2)):
        pygame.draw.line(surf, _CL_GOLD_D, (px, cy - 6), (px + lean, cy - 16), 3)
        pygame.draw.line(surf, _CL_GOLD, (px, cy - 6), (px + lean, cy - 16), 1)
        pygame.draw.circle(surf, _CL_GLINT, (px + lean, cy - 16), 1)
    # Central sun-disk between the plumes.
    pygame.draw.circle(surf, _CL_GOLD_D, (HX, cy - 9), 4)
    pygame.draw.circle(surf, _CL_GOLD, (HX, cy - 9), 3)
    pygame.draw.circle(surf, _CL_GLINT, (HX - 1, cy - 10), 1)

    # Small uraeus cobra at the very front of the dome — the brow jewel.
    pygame.draw.line(surf, _CL_GOLD_D, (HX, cy + 5), (HX, cy - 1), 3)
    _poly(surf, _CL_GOLD, [(HX - 3, cy - 1), (HX + 3, cy - 1), (HX, cy - 5)])
    pygame.draw.circle(surf, _CL_GLINT, (HX, cy - 4), 1)
    pygame.draw.circle(surf, _CL_CARN, (HX, cy - 3), 1)                     # cobra eye

    # ── gold anklets + sandal straps at the feet line ─────────────────────────
    # At the base bird's feet (~HY+22), kept ON the feet line so nothing hangs
    # below it. A bright glint + a crossed strap reads as a jewelled sandal.
    for fx in (HX - 21, HX - 14):
        pygame.draw.line(surf, _CL_GOLD_D, (fx, HY + 22), (fx + 5, HY + 22), 3)
        pygame.draw.line(surf, _CL_GOLD, (fx, HY + 22), (fx + 5, HY + 22), 1)
        pygame.draw.line(surf, _CL_GLINT, (fx + 1, HY + 21), (fx + 4, HY + 21), 1)
        pygame.draw.line(surf, _CL_GOLD, (fx + 2, HY + 22), (fx + 3, HY + 25), 1)  # strap


build = store_skins._make_skin(_paint)
