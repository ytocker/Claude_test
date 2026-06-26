"""DESIGN 4 — THE REFEREE (Soccer / Football, v3).

Scratch exploration only — NOT registered in store_skins.BUILDERS, so
production is untouched. Pip the scarlet macaw kitted as the match official:
a near-BLACK referee kit that — unlike the player jerseys before it — wraps
the FULL visible body (x=20..58), not just the right chest patch. A peaked
officials cap sits forward on the crown, knee-high black socks + boots fill
the legs, and the hero props are drawn last and large: a steel WHISTLE on a
lanyard at chest centre and a YELLOW CARD (with a red sliver behind it) held
on the left breast.

The jersey must read BLACK at the 40px downscale, not charcoal-blue: the lit
zone is a single 2px sliver on the near edge, never a big grey chest plane.
White is reserved for the collar piping, sock hoop, sole stripe and card
field so the steel whistle + yellow card always win the eye; a neutral grey
rim keeps the black kit from dissolving into the night sky.

Headless render: tools/soccer_candidates/render_design_4.py.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
BCX, BCY = 32, 52

# Near-black referee kit. The chest lit zone is kept dark on purpose so the
# read is BLACK, not a charcoal-blue plane; white + steel + yellow are the
# only high-value notes, reserved for collar/socks and the hero props.
_REF_BLACK   = (26, 28, 34)    # #1A1C22 referee black (full jersey body)
_REF_GREY    = (38, 40, 46)    # lit sliver (kept narrow so it never reads grey)
_REF_RIM     = (90, 92, 96)    # neutral rim so the kit holds against night sky
_REF_WHITE   = (244, 244, 248) # collar / sock piping / card field
_REF_YELLOW  = (255, 221, 70)  # yellow card
_REF_YEL_H   = (255, 240, 150) # card glint
_REF_RED     = (224, 56, 44)   # red card sliver behind the yellow
_REF_RED_D   = (150, 30, 24)
_REF_STEEL   = (200, 204, 212) # whistle steel
_REF_STEEL_H = (244, 246, 250)
_REF_STEEL_D = (96, 102, 116)
_REF_CORD    = (220, 222, 228) # lanyard cord
_CAP_BLACK   = (20, 22, 28)


def _paint(surf, _a):
    # Full-body referee jersey polygon — the v3 change. Left edge anchored on
    # BCX so the kit wraps the WHOLE visible body (x=20..58), not just the
    # right chest patch the earlier player jerseys covered.
    jersey = [
        (BCX - 10, HY + 7),   # left shoulder  (22, 48)
        (BCX - 12, HY + 17),  # left hip       (20, 58)
        (BCX - 8,  HY + 23),  # left hem       (24, 64)
        (HX + 8,   HY + 23),  # right hem      (55, 64)
        (HX + 11,  HY + 18),  # right hip      (58, 59)
        (HX + 9,   HY + 8),   # right shoulder (56, 49)
    ]

    # --- PEAKED OFFICIALS CAP (drawn before the jersey so the jersey overlaps
    #     the cap base). A forward-brimmed dome on the crown — NOT a headband —
    #     so it never crosses the brow and the face stays the open macaw.
    cy = CROWN_Y - 3
    pygame.draw.ellipse(surf, _REF_BLACK, (HX - 11, cy - 1, 22, 9))     # dome
    pygame.draw.ellipse(surf, _REF_GREY, (HX - 6, cy, 9, 4))           # top sheen
    pygame.draw.line(surf, _REF_RIM, (HX - 5, cy), (HX + 4, cy), 1)    # rim light
    # A 1px mid-grey gap under the dome stops the dome+brim collapsing into one
    # black blob at 40px — it carves the two shapes apart.
    pygame.draw.line(surf, (70, 72, 76), (HX + 3, cy + 5), (HX + 10, cy + 5), 1)
    _poly(surf, _REF_BLACK, [(HX + 3, cy + 6), (HX + 19, cy + 5),
                             (HX + 20, cy + 8), (HX + 4, cy + 9)])      # brim (forward, +2px reach)
    _poly(surf, _REF_GREY, [(HX + 4, cy + 8), (HX + 20, cy + 8),
                            (HX + 19, cy + 9), (HX + 4, cy + 9)])       # brim underside
    pygame.draw.line(surf, _REF_WHITE, (HX + 5, cy + 5), (HX + 19, cy + 5), 2)  # leading edge (2px)

    # --- BLACK SOCK PILLARS (knee-high) with a white hoop near the top. A grey
    #     under-pillar gives the black sock an edge against the night sky.
    for fx in (HX - 9, HX + 1):
        pygame.draw.line(surf, _REF_GREY, (fx + 1, HY + 13), (fx + 1, HY + 25), 6)
        pygame.draw.line(surf, _REF_BLACK, (fx, HY + 13), (fx, HY + 25), 5)
        pygame.draw.line(surf, _REF_WHITE, (fx - 1, HY + 15), (fx + 2, HY + 15), 2)  # hoop

    # --- BOOTS at the feet line — dark shoes with a white sole stripe.
    for fx in (HX - 9, HX + 1):
        pygame.draw.ellipse(surf, _REF_GREY, (fx - 4, HY + 23, 9, 5))
        pygame.draw.ellipse(surf, _REF_BLACK, (fx - 4, HY + 24, 9, 4))
        pygame.draw.line(surf, _REF_WHITE, (fx - 3, HY + 25), (fx + 2, HY + 25), 1)  # sole

    # --- BLACK SHORTS just under the jersey hem.
    pygame.draw.line(surf, _REF_GREY, (BCX - 8, HY + 24), (HX + 8, HY + 24), 4)
    pygame.draw.line(surf, _REF_BLACK, (BCX - 8, HY + 26), (HX + 8, HY + 26), 2)

    # --- FULL JERSEY (true black). The lit zone is a single 2px sliver on the
    #     near edge — NOT a big grey chest plane — so the kit reads BLACK, with
    #     a neutral rim on the far contour so it survives the night sky.
    _poly(surf, _REF_BLACK, jersey)
    pygame.draw.line(surf, _REF_GREY, (HX - 12, HY + 9), (HX - 13, HY + 18), 2)   # lit sliver
    # Dual rim-lights are the ONLY thing that separates a true-black kit from the
    # night sky AND from Pip's own scarlet body — 2px and cool, both contours.
    pygame.draw.line(surf, (120, 124, 130), (HX + 9, HY + 8), (HX + 11, HY + 18), 2)   # far-right rim
    pygame.draw.line(surf, (120, 124, 130), (HX + 11, HY + 18), (HX + 8, HY + 23), 2)  # far-right hem
    pygame.draw.lines(surf, (100, 102, 108), False,
                      [(BCX - 10, HY + 7), (BCX - 12, HY + 17), (BCX - 8, HY + 23)], 2)  # left-back rim
    pygame.draw.polygon(surf, _REF_BLACK, jersey, 1)                              # outline

    # --- WHITE COLLAR PIPING at the jersey top — a clean V + centre placket so
    #     the official's shirt reads at hero scale without a big white plane.
    pygame.draw.line(surf, _REF_WHITE, (HX - 6, HY + 8), (HX - 1, HY + 13), 3)
    pygame.draw.line(surf, _REF_WHITE, (HX + 5, HY + 8), (HX, HY + 13), 3)
    pygame.draw.line(surf, _REF_WHITE, (HX - 1, HY + 12), (HX - 1, HY + 22), 1)

    # --- HERO PROPS (drawn LAST, in front of everything) ------------------------
    # WHISTLE on a lanyard, slid DOWN to lower-centre chest so it owns its own
    # quadrant clear of the booking cards — the single brightest steel note, the
    # tell that says "referee" at 40px.
    wy = HY + 17
    pygame.draw.line(surf, _REF_CORD, (HX - 5, HY + 8), (HX, wy - 2), 2)    # lanyard V
    pygame.draw.line(surf, _REF_CORD, (HX + 5, HY + 8), (HX, wy - 2), 2)
    pygame.draw.ellipse(surf, _REF_STEEL_D, (HX - 6, wy, 12, 10))          # disc shadow
    pygame.draw.ellipse(surf, _REF_STEEL, (HX - 5, wy + 1, 11, 9))         # disc body
    _poly(surf, _REF_STEEL, [(HX + 5, wy + 4), (HX + 8, wy + 5), (HX + 5, wy + 7)])  # mouthpiece
    pygame.draw.rect(surf, _REF_STEEL_H, (HX - 3, wy + 2, 2, 2))           # glint
    pygame.draw.ellipse(surf, _REF_STEEL_D, (HX - 6, wy, 12, 10), 1)       # rim

    # YELLOW CARD on the UPPER-LEFT breast (its own quadrant, HY+9..16) with a red
    # sliver behind it — widened to an unmistakable bright rectangle at 40px.
    _poly(surf, _REF_RED, [(HX - 11, HY + 9), (HX - 6, HY + 8),
                           (HX - 5, HY + 15), (HX - 10, HY + 16)])         # red sliver behind
    yl, yr, yt, yb = HX - 9, HX - 1, HY + 9, HY + 16
    pygame.draw.rect(surf, _REF_BLACK, (yl - 1, yt - 1, yr - yl + 2, yb - yt + 2))  # dark backing
    _poly(surf, _REF_YELLOW, [(yl, yt), (yr, yt), (yr, yb), (yl, yb)])      # yellow card
    pygame.draw.line(surf, _REF_YEL_H, (yl + 1, yt + 1), (yl + 1, yb - 1), 1)  # glint


build = store_skins._make_skin(_paint)
