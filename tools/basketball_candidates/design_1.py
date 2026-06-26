"""THE PRO — basketball candidate DESIGN 1 of 5 (modern NBA), rebuilt.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
roster is untouched. There is NO ball — it ships separately as a parcel, so the
KIT alone has to carry the basketball read.

Why this rebuild exists: the round-1 take filled the tank solid edge-to-edge,
so it read as an orange SOCCER jersey — no bare shoulders, no waistband break,
a mangled number, no high-tops. THE PRO is rebuilt around the four structures
that soccer does NOT share, each made EXPLICIT so the read survives 40px:

  1. a SLEEVELESS TANK whose body panel is deliberately NARROWER than Pip's
     body, so a curved sliver of the scarlet body shows at BOTH shoulders
     outside two thin straps — the bare-shoulder armhole is the loudest hoops
     tell and the one thing soccer never has,
  2. BAGGY KNEE SHORTS with a HARD black waistband break under the tank hem +
     a contrast side stripe, the shorts hem dropping clearly LOWER than a
     soccer kit's short shorts,
  3. a BOLD blocky white "23" on a cleared orange field, rimmed dark so it
     reads on any sky, and
  4. CHUNKY HIGH-TOPS — a cream boot with an ankle-collar bump rising above a
     grey rubber sole slab, an accent stripe on the upper (a sneaker, never a
     cleat).

Supporting cues: a thin brow headband hugging the crown and a wristband on the
near wing. Court-orange / black / white / accent-blue so it can't be confused
with the soccer set's colours either. Pip's scarlet macaw head/beak/eye stay
in the open below the headband, so it still reads as a parrot wearing a kit.

Footprint law: every piece stays inside the base bird footprint — the headband
hugs the crown, the shorts hem sits above the feet line, and the high-tops sit
ON the feet line (~HY+21..27), never below it.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Court palette — orange tank is the hero value, mid-bright so the white number
# and black trim both pop on it and so it separates from the scarlet head above
# and a bright day sky.
_ORANGE    = (224, 99, 43)           # #E0632B court orange (tank + shorts body)
_ORANGE_D  = (168, 64, 22)           # cloth shadow / armhole depth
_ORANGE_H  = (246, 142, 88)          # cloth highlight / near-side sheen
_SCARLET   = (206, 44, 38)           # Pip's body red — drawn to GUARANTEE the
_SCARLET_D = (150, 28, 26)           #   bare shoulder reads outside the straps
_BLACK     = (24, 26, 32)            # #1A1C22 trim / contour / waistband
_WHITE     = (246, 246, 250)         # #F4F4F8 number / piping / high-top
_WHITE_D   = (196, 200, 210)         # number shadow / sneaker shade
_ACCENT    = (59, 107, 214)          # #3B6BD6 stripe accent
_SOLE      = (150, 154, 164)         # #969AA4 grey rubber sole slab
_CREAM     = (240, 236, 224)         # warm sneaker leather


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # ── BAGGY KNEE SHORTS first (behind the tank hem). Drawn WIDE and dropped
    #    to a low knee-length hem so they read clearly LONGER than a soccer
    #    kit's short shorts. Top edge at BCY+6 (the waistband line), hem at
    #    ~BCY+17, with an outward flare to each baggy leg.
    shorts = [(BCX - 12, BCY + 6), (BCX + 13, BCY + 6),
              (BCX + 14, BCY + 17), (BCX + 2, BCY + 16),
              (BCX + 1, BCY + 17), (BCX - 13, BCY + 17)]
    _poly(surf, _ORANGE, shorts)
    # Off-leg shadow + centre vent so each baggy leg reads as loose volume.
    _poly(surf, _ORANGE_D, [(BCX - 13, BCY + 12), (BCX - 6, BCY + 12),
                            (BCX - 7, BCY + 17), (BCX - 13, BCY + 17)])
    pygame.draw.line(surf, _ORANGE_D, (BCX + 1, BCY + 10), (BCX + 1, BCY + 17), 2)
    # Near-leg sheen so the baggy short has form, not a flat block.
    pygame.draw.line(surf, _ORANGE_H, (BCX + 8, BCY + 9), (BCX + 9, BCY + 15), 1)
    # Contrast SIDE STRIPE down the outer seam of the near leg — a black band
    # carrying a thin accent line, the modern uniform side panel.
    pygame.draw.line(surf, _BLACK, (BCX + 12, BCY + 7), (BCX + 13, BCY + 16), 3)
    pygame.draw.line(surf, _ACCENT, (BCX + 12, BCY + 7), (BCX + 13, BCY + 16), 1)
    # Same stripe mirrored faintly on the off leg so the seam reads symmetric.
    pygame.draw.line(surf, _BLACK, (BCX - 12, BCY + 7), (BCX - 13, BCY + 16), 2)
    # Shorts HEM band — a black trim line at ~BCY+16 makes the low hem explicit.
    pygame.draw.line(surf, _BLACK, (BCX - 12, BCY + 16), (BCX - 1, BCY + 16), 1)
    pygame.draw.line(surf, _BLACK, (BCX + 2, BCY + 16), (BCX + 13, BCY + 16), 1)

    # ── BARE SHOULDERS. Before the tank, paint a BROAD wedge of Pip's SCARLET
    #    body at each shoulder root so that — once the NARROW tank panel lands
    #    on top — scarlet is GUARANTEED to fill the armhole gap OUTSIDE the
    #    straps at both shoulders. This is the sleeveless tell and the #1
    #    basketball read, so the patches are drawn deliberately wide + bright.
    _poly(surf, _SCARLET, [(BCX - 15, BCY - 6), (BCX - 6, BCY - 9),
                           (BCX - 3, BCY - 1), (BCX - 13, BCY + 2)])   # off shoulder
    _poly(surf, _SCARLET, [(BCX + 14, BCY - 6), (BCX + 5, BCY - 9),
                           (BCX + 2, BCY - 1), (BCX + 12, BCY + 2)])   # near shoulder
    # A brighter rounded cap on each so the bare shoulder reads as a curved
    # deltoid, not a flat patch.
    pygame.draw.circle(surf, _SCARLET, (BCX + 9, BCY - 4), 3)
    pygame.draw.circle(surf, _SCARLET, (BCX - 10, BCY - 4), 3)
    _poly(surf, _SCARLET_D, [(BCX - 15, BCY - 3), (BCX - 12, BCY - 4),
                             (BCX - 11, BCY + 1), (BCX - 14, BCY + 2)])

    # ── SLEEVELESS TANK over the torso. The body panel is deliberately NARROW
    #    (~BCX-8 .. BCX+6) so it sits INSIDE the shoulders, leaving the scarlet
    #    above visible. Top of the panel is a flat scoop neckline; the bottom
    #    is the tank hem at BCY+5, just above the shorts waistband at BCY+6.
    tank = [(BCX - 8, BCY - 5), (BCX + 6, BCY - 5),
            (BCX + 8, BCY - 1), (BCX + 7, BCY + 5),
            (BCX - 9, BCY + 5), (BCX - 10, BCY - 1)]
    _poly(surf, _ORANGE, tank)
    # Three-value cloth shading on the narrow panel: a shadowed off edge + a
    # near-side sheen so the tank has rounded form.
    _poly(surf, _ORANGE_D, [(BCX - 10, BCY - 1), (BCX - 7, BCY - 2),
                            (BCX - 6, BCY + 4), (BCX - 9, BCY + 5)])
    pygame.draw.line(surf, _ORANGE_H, (BCX + 5, BCY - 3), (BCX + 6, BCY + 4), 1)

    # Two THIN shoulder STRAPS (~3px) bridging the narrow tank up to the
    # near-shoulder line. They are kept narrow on purpose so the scarlet
    # shoulder reads OUTSIDE each strap.
    pygame.draw.line(surf, _ORANGE, (BCX - 7, BCY - 5), (BCX - 9, BCY - 8), 3)   # off strap
    pygame.draw.line(surf, _ORANGE, (BCX + 5, BCY - 5), (BCX + 7, BCY - 8), 3)   # near strap
    pygame.draw.line(surf, _ORANGE_H, (BCX + 5, BCY - 5), (BCX + 6, BCY - 7), 1)

    # ── ARMHOLE SCOOPS — carve an EXPLICIT scarlet sliver in the gap between
    #    each strap and the tank's side panel, so the bare-shoulder cut is
    #    unmistakable: bright scarlet inside, then a curved orange arc edging
    #    the cut so it reads as a scooped armhole, not just exposed skin.
    pygame.draw.line(surf, _SCARLET, (BCX + 8, BCY - 5), (BCX + 9, BCY + 1), 2)   # near gap
    pygame.draw.line(surf, _SCARLET, (BCX - 9, BCY - 5), (BCX - 10, BCY + 1), 2)  # off gap
    pygame.draw.arc(surf, _ORANGE_D, (BCX + 4, BCY - 8, 9, 13), -1.2, 1.4, 2)   # near armhole
    pygame.draw.arc(surf, _ORANGE_D, (BCX - 13, BCY - 8, 9, 13), 1.7, 4.3, 2)   # off armhole

    # Black trim piping along the scoop neckline + the tank hem so the kit reads
    # sharp and the hem separates from the shorts waistband below.
    pygame.draw.lines(surf, _BLACK, False,
                      [(BCX - 5, BCY - 4), (BCX, BCY - 2), (BCX + 4, BCY - 4)], 1)
    pygame.draw.line(surf, _BLACK, (BCX - 8, BCY + 5), (BCX + 6, BCY + 5), 1)

    # ── HARD WAISTBAND BREAK — a 2px BLACK line at BCY+6 across the full hip,
    #    the unmistakable seam separating the orange tank from the orange
    #    shorts (without it the two merge into one soccer-jersey colour block).
    pygame.draw.line(surf, _BLACK, (BCX - 12, BCY + 6), (BCX + 13, BCY + 6), 2)
    pygame.draw.line(surf, _ACCENT, (BCX - 6, BCY + 6), (BCX + 6, BCY + 6), 1)

    # ── BOLD NUMBER "23" across the chest. Two solid blocky digits, white on a
    #    cleared orange field, with a 1px dark rim so the white survives on a
    #    light day sky. Each digit is built from thick bars with EXPLICIT 1px
    #    negative-space gaps so the "2" and "3" stay legible and don't merge
    #    into one block (the round-1 failure).
    _draw_block_2(surf, BCX - 7, BCY - 4)
    _draw_block_3(surf, BCX, BCY - 4)

    # ── CHUNKY HIGH-TOPS on the feet line. Each is a cream leather boot with an
    #    ankle COLLAR BUMP rising above a grey rubber SOLE slab + one accent
    #    stripe — a basketball sneaker, never a cleat. A 1px dark contour around
    #    every boot keeps the two feet from merging into one white blob, and the
    #    collar bump rising above the sole is what reads "high-top". Sits ON the
    #    feet line (~HY+18..27), never below it.
    for fx in (25, 35):
        # Dark contour box first so the boot reads as its own distinct shape.
        pygame.draw.rect(surf, _BLACK, (fx - 4, HY + 17, 9, 11), border_radius=2)
        # Grey rubber sole slab — a thick flat base, the sneaker tell.
        pygame.draw.rect(surf, _SOLE, (fx - 4, HY + 24, 9, 3))
        # Cream boot upper.
        pygame.draw.rect(surf, _CREAM, (fx - 3, HY + 21, 7, 4), border_radius=1)
        # Ankle COLLAR BUMP rising above the upper toward the leg — high-top tell.
        pygame.draw.rect(surf, _CREAM, (fx - 3, HY + 18, 4, 4), border_radius=2)
        pygame.draw.line(surf, _WHITE, (fx - 3, HY + 19), (fx, HY + 19), 1)  # collar glint
        # One accent stripe swooping across the upper + a black lace flash.
        pygame.draw.line(surf, _ACCENT, (fx - 3, HY + 23), (fx + 3, HY + 21), 2)
        pygame.draw.line(surf, _WHITE, (fx - 2, HY + 24), (fx + 3, HY + 24), 1)  # toe cap

    # ── WRISTBAND on the near wing — a bold white sweatband with a thin accent
    #    midline, clearly on the forearm.
    wrx, wry = BCX + 13, BCY + 9
    pygame.draw.line(surf, _WHITE_D, (wrx - 3, wry + 4), (wrx + 5, wry - 2), 6)
    pygame.draw.line(surf, _WHITE, (wrx - 3, wry + 4), (wrx + 5, wry - 2), 4)
    pygame.draw.line(surf, _ACCENT, (wrx - 2, wry + 3), (wrx + 4, wry - 2), 1)

    # ── THIN BROW HEADBAND hugging the CROWN — the iconic non-ball hoops cue.
    #    Kept HIGH (CROWN_Y+3) and slim (3px) so it sits ON the brow ABOVE the
    #    eye, never sliding down over the eye where it would read as shades.
    by = CROWN_Y + 3
    pygame.draw.line(surf, _WHITE_D, (HX - 12, by + 1), (HX + 12, by + 1), 4)  # shadow
    pygame.draw.line(surf, _WHITE, (HX - 12, by), (HX + 12, by), 3)
    pygame.draw.line(surf, _ACCENT, (HX - 11, by), (HX + 11, by), 1)          # colored midline


def _block_digit(surf, segs, x, y):
    """Render a blocky digit from a list of filled (dx, dy, w, h) WHITE cells in
    a 6x9 glyph box. Each cell carries its OWN 1px black rim so the dark gaps
    BETWEEN strokes survive — that negative space is what keeps the digit
    legible instead of collapsing to a solid box."""
    for dx, dy, w, h in segs:
        pygame.draw.rect(surf, _BLACK, (x + dx - 1, y + dy - 1, w + 2, h + 2),
                         border_radius=1)
    for dx, dy, w, h in segs:
        pygame.draw.rect(surf, _WHITE, (x + dx, y + dy, w, h))


# Digits are drawn in a 6-wide x 9-tall box from 2px-thick bars + posts, with a
# 1px dark gap left open between the bars so the open counters read.
def _draw_block_2(surf, x, y):
    """Blocky '2' — top bar, top-right post, mid bar, bottom-left post, base."""
    segs = [
        (0, 0, 6, 2),     # top bar
        (4, 2, 2, 2),     # upper-right post
        (0, 4, 6, 2),     # middle bar (gap at dy 3 keeps it open)
        (0, 6, 2, 1),     # lower-left post
        (0, 7, 6, 2),     # base bar
    ]
    _block_digit(surf, segs, x, y)


def _draw_block_3(surf, x, y):
    """Blocky '3' — top bar, mid bar, base bar, right post (open left counters)."""
    segs = [
        (0, 0, 6, 2),     # top bar
        (4, 1, 2, 7),     # full right post
        (2, 4, 3, 2),     # middle bar (left side open)
        (0, 7, 6, 2),     # base bar
    ]
    _block_digit(surf, segs, x, y)


build = store_skins._make_skin(_paint)
