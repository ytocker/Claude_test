"""DESIGN 3 — THE NÚMERO 10 (Soccer / Football, retro legend).

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted as a vintage international glory legend: a classic
sky-blue, long-sleeve COTTON jersey with a laced V-collar at the CHEST
neckline (the era tell), a small embroidered crest patch on the near chest,
the iconic big retro "10" low on the shirt, and classic high socks with a
single fold-over top band over low retro boots. No headgear (crown stays
open) so the era reads clean — and so NOTHING covers Pip's beak/eye/face.

The jersey is painted OVER the scarlet body (head stays the macaw so Pip
still reads as a parrot). The laced CHEST collar + crest + long sleeves are
what separate this from the modern Striker — it must read as a DIFFERENT ERA
of football. The collar lives at the NECKLINE on the chest (same zone as the
tennis polo collar, ~HY+8..12), never on the face, so it can't be mistaken
for sunglasses. All kit is held INSIDE the base bird footprint: socks +
boots sit on the feet line (~HY+15..27), nothing balloons the torso or
drops below the feet.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Sky-blue retro cotton kit. Three cloth values so the laced collar, crest and
# big "10" still separate from the jersey field after the 40px downscale, and
# the long sleeves read as set-in. Cotton, not satin — the values sit closer
# together than the modern Striker's, which is part of the nostalgic read.
_RET_SKY     = (28, 111, 224)       # #1C6FE0 jersey sky-blue (cotton mid)
_RET_SKY_D   = (16, 66, 142)        # cloth shadow / seams / line work
_RET_SKY_H   = (96, 158, 244)       # sleeve / collar highlight
_RET_SKY_HOLE= (60, 132, 236)       # knocked-out sky-blue inside the "0"
_RET_WHITE   = (248, 250, 255)      # #F8FAFF number / collar trim (lifted for contrast)
_RET_WHITE_D = (206, 218, 240)      # cool white shade so the trim reads rounded
_RET_RED     = (200, 60, 46)        # #C83C2E retro crest field
_RET_RED_D   = (120, 32, 24)        # crest shadow / outline
_RET_GOLD    = (236, 198, 78)       # #ECC64E lace cord / crest rim
_RET_GOLD_H  = (255, 232, 158)      # lace glint
_RET_GOLD_D  = (120, 96, 30)        # crisp dark underline so gold reads as kit
_RET_BOOT    = (35, 37, 46)         # #23252E low retro boot
_RET_BOOT_H  = (78, 84, 102)        # boot upper highlight


# Body centre in composite space (parrot body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52


def _paint(surf, _a):
    # --- Long-sleeve cotton JERSEY over the torso (THE retro read) --------------
    # A clean jersey block clipped to the chest, filled sky-blue. Held inside the
    # footprint (shoulders ~BCY-12, hem ~BCY+12). The hem dips slightly lower than
    # the Striker's so the big "10" has room to sit LOW on the shirt — the retro
    # placement, not high-centre like a modern squad number.
    jersey = [(BCX - 15, BCY - 9), (BCX - 16, BCY - 1), (BCX - 14, BCY + 12),
              (BCX + 13, BCY + 12), (BCX + 15, BCY - 1), (BCX + 13, BCY - 9),
              (BCX + 4, BCY - 12), (BCX - 6, BCY - 12)]
    _poly(surf, _RET_SKY, jersey)

    # Shoulder-seam shadow + re-edge the jersey contour.
    pygame.draw.line(surf, _RET_SKY_D, (BCX - 12, BCY - 8), (BCX + 10, BCY - 8), 1)
    pygame.draw.polygon(surf, _RET_SKY_D, jersey, 1)
    # A soft vertical highlight down the chest so the cotton reads rounded.
    pygame.draw.line(surf, _RET_SKY_H, (BCX - 9, BCY - 6), (BCX - 9, BCY + 6), 1)

    # --- Long SLEEVES — a sky-blue cloth column down each wing root --------------
    # The long-sleeve cotton tell vs the modern short-sleeve Striker: a clear
    # sky-blue sleeve band runs DOWN each wing root with a darker set-in seam, then
    # a contrasting 2px WHITE cuff hoop closes the bottom. A visible cloth column
    # on the wing = "long-sleeve cotton". The cuff hoop is the part that must
    # survive 40px, so it's a full bright band across the sleeve foot.
    for sgn in (-1, 1):
        sx = BCX + sgn * 15           # outer sleeve edge
        ix = BCX + sgn * 10           # inner sleeve edge (toward the chest)
        top, bot = BCY - 8, BCY + 7
        # Sleeve cloth column filled sky-blue so the wing root reads as cloth.
        _poly(surf, _RET_SKY,
              [(ix, top), (sx, top + 1), (sx, bot), (ix, bot - 1)])
        # Set-in seam where the sleeve meets the body + an outer-edge shadow so the
        # column reads as a rounded tube, not a flat patch.
        pygame.draw.line(surf, _RET_SKY_D, (ix, top), (ix, bot - 1), 1)
        pygame.draw.line(surf, _RET_SKY_D, (sx, top + 1), (sx, bot), 1)
        pygame.draw.line(surf, _RET_SKY_H, (ix + sgn, top + 2),
                         (ix + sgn, bot - 3), 1)
        # White cuff hoop closing the long sleeve — a 2px bright band at the foot
        # of the column with a dark under-edge so it reads as a cuff, not a smear.
        pygame.draw.line(surf, _RET_WHITE, (ix, bot - 1), (sx, bot), 2)
        pygame.draw.line(surf, _RET_SKY_D, (ix, bot + 1), (sx, bot + 1), 1)

    # --- Laced V-COLLAR at the CHEST neckline (THE era tell) --------------------
    # A white V opening UPWARD from the shoulders, its point dropping DOWN toward
    # the chest — sitting at the neckline (~HY+8..12 zone), in the SAME band as the
    # tennis polo collar, NOT on the face. Two gold lace rungs lace the placket
    # closed inside the white. High-contrast white on the blue so it can never read
    # as a face element. The collar is two white arms meeting at a low point.
    nx = BCX + 1                      # collar centre on the chest
    sh_y = BCY - 9                    # shoulder line (top of the V arms)
    pt_y = BCY - 1                    # point of the V (drops toward the chest)
    larm = (nx - 7, sh_y)             # left shoulder corner
    rarm = (nx + 7, sh_y)             # right shoulder corner
    pt = (nx, pt_y)                   # V point on the chest
    # Filled white V (two arms meeting at the low point) — a clean bright wedge so
    # the collar reads as cloth opening at the neck, not a line.
    _poly(surf, _RET_WHITE,
          [larm, (nx - 2, sh_y), pt, (nx + 2, sh_y), rarm,
           (nx + 4, sh_y + 3), pt, (nx - 4, sh_y + 3)])
    # Cool shade on the lower-right inner edge so the collar cloth reads rounded.
    pygame.draw.line(surf, _RET_WHITE_D, (nx + 2, sh_y + 1), pt, 1)
    # Dark keyline around the V so the white pops crisp off the blue field.
    pygame.draw.lines(surf, _RET_SKY_D, False,
                      [larm, pt, rarm], 1)
    # Gold lace rungs lacing the placket: 2 short vertical gold ticks straddling
    # the centre slit, inside the white wedge — the unmistakable "laced collar".
    for ry in (sh_y + 2, sh_y + 5):
        pygame.draw.line(surf, _RET_GOLD, (nx - 2, ry), (nx - 2, ry + 2), 2)
        pygame.draw.line(surf, _RET_GOLD, (nx + 2, ry), (nx + 2, ry + 2), 2)
    pygame.draw.line(surf, _RET_GOLD_H, (nx - 2, sh_y + 2), (nx - 2, sh_y + 3), 1)
    # The dark placket slit down the centre, between the gold rungs.
    pygame.draw.line(surf, _RET_SKY_D, (nx, sh_y + 1), (nx, pt_y - 1), 1)

    # --- Embroidered CREST patch on the near chest ------------------------------
    # A simplified shield (woven, not printed): red field, a 1px gold rim, and a
    # SINGLE bold white chevron inside — one mark, not a crowd. Bumped 1px larger
    # and tucked high on the near (right) chest so it doesn't crowd the collar.
    crx, cry = BCX + 9, BCY - 2
    shield = [(crx - 4, cry - 5), (crx + 4, cry - 5), (crx + 5, cry),
              (crx, cry + 6), (crx - 5, cry)]
    _poly(surf, _RET_RED_D, [(p[0], p[1] + 1) for p in shield])   # drop shadow
    _poly(surf, _RET_RED, shield)
    pygame.draw.polygon(surf, _RET_GOLD, shield, 1)               # 1px gold rim
    # Single bold white chevron device inside the shield (the lone "embroidery").
    pygame.draw.line(surf, _RET_WHITE, (crx - 3, cry - 1), (crx, cry + 2), 2)
    pygame.draw.line(surf, _RET_WHITE, (crx + 3, cry - 1), (crx, cry + 2), 2)

    # --- Big retro "10" low on the shirt ----------------------------------------
    # The iconic number — the single loudest footballer signal. Two clean BOLD
    # glyphs read upright on the chest, scaled up so they own the lower shirt, with
    # a clear ~3px gap so the digits never collide after the downscale: a simple
    # blocky "1" (no serif noise) on the LEFT + an open "0" with a 1px sky-blue
    # hole on the RIGHT. Sits LOW on the shirt, below the collar and crest.
    ndy = BCY + 6                     # number baseline-ish centre
    # "1" — a single bold vertical block, crisp dark keyline + white face, no serif.
    onex = BCX - 6
    pygame.draw.line(surf, _RET_SKY_D, (onex, ndy - 8), (onex, ndy + 7), 6)
    pygame.draw.line(surf, _RET_WHITE, (onex, ndy - 8), (onex, ndy + 7), 4)
    pygame.draw.line(surf, _RET_WHITE_D, (onex + 1, ndy - 3), (onex + 1, ndy + 7), 1)
    # "0" — a bold open ring ~3px right of the "1": dark keyline, white body, a 1px
    # sky-blue knocked-out hole so it reads OPEN, not a solid dot.
    ox, oy, ow, oh = onex + 4, ndy - 9, 12, 18
    pygame.draw.ellipse(surf, _RET_SKY_D, (ox, oy, ow, oh))
    pygame.draw.ellipse(surf, _RET_WHITE, (ox + 1, oy + 1, ow - 2, oh - 2))
    pygame.draw.ellipse(surf, _RET_SKY_HOLE, (ox + 4, oy + 5, 4, 8))
    pygame.draw.ellipse(surf, _RET_WHITE_D, (ox + 1, oy + oh // 2, ow - 2, oh // 2), 1)

    # --- High SOCKS with one fold-over band + low retro boots -------------------
    # Classic pulled-up retro socks: a tall SOLID sky-blue sock with ONE chunky
    # 2px WHITE fold-over hoop high on it (the unmistakable retro footballer mark),
    # then a simple dark boot cap hugging the feet line. Everything sits ON the
    # feet line (~HY+15..27), nothing drops below it, so the bird keeps its size.
    for fx in (28, 35):
        # Tall solid sky-blue sock — taller than a band so it reads pulled-up.
        pygame.draw.line(surf, _RET_SKY_D, (fx + 1, HY + 15), (fx + 1, HY + 23), 5)
        pygame.draw.line(surf, _RET_SKY, (fx, HY + 15), (fx, HY + 23), 4)
        pygame.draw.line(surf, _RET_SKY_H, (fx - 1, HY + 17), (fx - 1, HY + 21), 1)
        # ONE chunky white fold-over hoop high on the sock, with a dark under-edge
        # so the turn-down reads as a fold even at 40px.
        pygame.draw.line(surf, _RET_WHITE, (fx - 2, HY + 16), (fx + 2, HY + 16), 2)
        pygame.draw.line(surf, _RET_SKY_D, (fx - 2, HY + 18), (fx + 2, HY + 18), 1)
        # Simple low dark boot cap at the feet line — no high cleats, retro leather.
        pygame.draw.ellipse(surf, _RET_BOOT_H, (fx - 4, HY + 22, 9, 5))
        pygame.draw.ellipse(surf, _RET_BOOT, (fx - 4, HY + 23, 9, 4))
        pygame.draw.line(surf, _RET_BOOT, (fx - 4, HY + 25), (fx + 4, HY + 25), 1)


build = store_skins._make_skin(_paint)
