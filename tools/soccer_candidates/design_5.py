"""DESIGN 5 — THE ULTRA FAN (Soccer / Football) — supporter.

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted not as a player but as a die-hard supporter in the
terraces — the set's only NON-player. The read is carried by a FULL-BODY
horizontally-striped team jersey (red/white/red), knitted bobble HAT, and a
two-tone team SCARF.

The key departure from the player kits (designs 1-4): the jersey is no longer a
narrow right-chest bib (old x=33-58). The polygon spans the FULL visible body
(x=20-58, ~36px wide) and is filled with three horizontal stripes clipped to
the jersey silhouette, so the supporter's club colours read as bold club bands
at 40px on day and night.

A bobble HAT domes over the crown (NOT a band across the brow), and a
gold/purple SCARF loops the neck then V-splits into two fringed tails across the
chest — the hero prop, drawn LAST so it sits proud over the stripes. Knee-high
dark socks + boots ground the kit; grey shorts peek at the hem.

Headless render: tools/soccer_candidates/render_design_5.py.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
BCX, BCY = 32, 52

# Striped club kit. Red/white/red bands are the supporter's colours — the white
# stripe is the bright separator that keeps the bands reading on a scarlet body
# at 40px. The dark-red outline pulls the full-body wrap contour off the body.
_STRIPE_RED  = (204, 34, 34)        # #CC2222 club red band
_STRIPE_WHT  = (240, 240, 240)      # #F0F0F0 white band
_JERSEY_OUT  = (140, 20, 20)        # dark red jersey outline
_HAT_RED     = (160, 20, 20)        # dark red bobble hat dome
_HAT_RIM     = (100, 12, 12)        # hat/head separation ring
_HAT_POM     = (240, 240, 245)      # white pompom
_HAT_POM_H   = (255, 255, 255)
_SCARF_GOLD  = (240, 190, 30)       # gold scarf
_SCARF_PUR   = (100, 40, 160)       # purple scarf
_SCARF_FRNG  = (220, 170, 20)       # fringe
_SOCK_D      = (40, 44, 52)         # dark socks
_BOOT_D      = (26, 24, 32)
_BOOT_SOLE   = (200, 200, 210)
_SHORTS_GREY = (130, 134, 150)


# Full-body jersey polygon — wraps most of the visible torso (x=20-58, ~36px
# wide), NOT the old narrow right-chest bib. The stripes below are clipped to
# this shape via _jersey_x_at_y so each band stops exactly at the cloth contour.
_JERSEY = [
    (BCX - 10, HY + 7),   # left shoulder  (22, 48)
    (BCX - 12, HY + 17),  # left hip       (20, 58)
    (BCX - 8,  HY + 23),  # left hem       (24, 64)
    (HX + 8,   HY + 23),  # right hem      (55, 64)
    (HX + 11,  HY + 18),  # right hip      (58, 59)
    (HX + 9,   HY + 8),   # right shoulder (56, 49)
]


def _jersey_x_at_y(y):
    """Left and right x of the jersey polygon at a given y — interpolated along
    the two side edges so a horizontal stripe band fills the full body width but
    stops exactly at the angled jersey contour (no rectangular overhang)."""
    # Left edge: (22,48) -> (20,58) -> (24,64).
    if y <= HY + 17:                       # y <= 58
        t = (y - (HY + 7)) / 10.0
        lx = int(22 + (20 - 22) * t)
    else:
        t = (y - (HY + 17)) / 6.0
        lx = int(20 + (24 - 20) * t)
    # Right edge: (56,49) -> (58,59) -> (55,64).
    if y <= HY + 18:                       # y <= 59
        t = (y - (HY + 8)) / 10.0
        rx = int(56 + (58 - 56) * t)
    else:
        t = (y - (HY + 18)) / 5.0
        rx = int(58 + (55 - 58) * t)
    return lx, rx


def _paint(surf, _a):
    # --- 1 · DARK SOCK PILLARS (knee-high) --------------------------------------
    # Drawn first so the shorts + jersey overlap their tops; a white sock-top hoop
    # is the club kit tell.
    for fx in (HX - 9, HX + 1):
        pygame.draw.line(surf, _SOCK_D, (fx, HY + 13), (fx, HY + 25), 5)
        pygame.draw.line(surf, (200, 205, 220), (fx - 1, HY + 13), (fx + 2, HY + 13), 2)

    # --- 2 · BOOTS --------------------------------------------------------------
    # A lighter toe highlight just above the boot keeps the boot from fusing into
    # the dark sock above it at 40px.
    for fx in (HX - 9, HX + 1):
        pygame.draw.ellipse(surf, _BOOT_D, (fx - 4, HY + 23, 9, 5))
        pygame.draw.line(surf, (120, 124, 140), (fx - 3, HY + 23), (fx + 3, HY + 23), 1)
        pygame.draw.line(surf, _BOOT_SOLE, (fx - 3, HY + 25), (fx + 3, HY + 25), 1)

    # --- 3 · GREY SHORTS --------------------------------------------------------
    pygame.draw.line(surf, _SHORTS_GREY, (BCX - 8, HY + 24), (HX + 8, HY + 24), 4)

    # --- 4 · HORIZONTAL-STRIPED FULL-BODY JERSEY --------------------------------
    # Three red/white/red bands, each a trapezoid clipped to the jersey contour at
    # its top/bottom y so the bands fill the full torso width but never overhang.
    stripe_defs = [
        (_STRIPE_RED, HY + 7,  HY + 13),
        (_STRIPE_WHT, HY + 13, HY + 18),
        (_STRIPE_RED, HY + 18, HY + 23),
    ]
    for color, y0, y1 in stripe_defs:
        lx0, rx0 = _jersey_x_at_y(y0)
        lx1, rx1 = _jersey_x_at_y(y1)
        band = [(lx0, y0), (rx0, y0), (rx1, y1), (lx1, y1)]
        _poly(surf, color, band)
    # 1px dark-red outline pulls the full-body wrap off the scarlet body.
    pygame.draw.polygon(surf, _JERSEY_OUT, _JERSEY, 1)

    # --- 5 · BOBBLE HAT on the crown --------------------------------------------
    # A knitted supporter's hat — a low dome with a white pompom, NOT a band across
    # the brow. The dark-red separation ring lifts it off the scarlet macaw head.
    pygame.draw.ellipse(surf, _HAT_RIM, (HX - 10, CROWN_Y - 2, 20, 8), 2)
    pygame.draw.ellipse(surf, _HAT_RED, (HX - 9, CROWN_Y - 5, 18, 9))
    pygame.draw.line(surf, (200, 60, 60), (HX - 5, CROWN_Y - 4), (HX + 2, CROWN_Y - 4), 2)
    pygame.draw.circle(surf, _HAT_POM, (HX - 2, CROWN_Y - 9), 4)
    pygame.draw.circle(surf, _HAT_POM_H, (HX - 3, CROWN_Y - 10), 2)

    # --- 6 · TEAM SCARF — hero prop, drawn LAST ---------------------------------
    # A two-tone scarf loops the neck, then V-splits into two FAT fringed tails
    # that fan outward PAST the body silhouette — the supporter's defining
    # accessory. Each tail is a 5px gold fill on a 7px dark outline so it stands
    # proud of the red striped jersey; a purple neck loop reads against the red
    # better than gold-on-red did.
    pygame.draw.line(surf, _SCARF_PUR, (HX - 6, HY + 8), (HX + 6, HY + 8), 5)    # purple neck loop
    pygame.draw.line(surf, _SCARF_GOLD, (HX - 5, HY + 10), (HX + 5, HY + 10), 3)  # gold under-loop

    _SCARF_DK = (60, 20, 80)  # dark outline that frames each fat tail off the jersey

    # LEFT TAIL — fans down-left past the body, dark-outlined gold with fat ticks.
    pygame.draw.line(surf, _SCARF_DK,   (HX - 4, HY + 10), (HX - 14, HY + 22), 7)
    pygame.draw.line(surf, _SCARF_GOLD, (HX - 4, HY + 10), (HX - 14, HY + 22), 5)
    # Perpendicular purple band ticks (fat 3px) across the tail.
    for t in (0.30, 0.65):
        tx = int((HX - 4) + ((HX - 14) - (HX - 4)) * t)
        ty = int((HY + 10) + (22 - 10) * t)
        pygame.draw.line(surf, _SCARF_PUR, (tx - 3, ty - 1), (tx + 3, ty + 1), 3)
    for j in (0, 3, 6):
        pygame.draw.line(surf, _SCARF_FRNG, (HX - 11 - j, HY + 22), (HX - 12 - j, HY + 25), 1)

    # RIGHT TAIL — fans down-right past the body, same fat ticks + fringe.
    pygame.draw.line(surf, _SCARF_DK,   (HX + 1, HY + 10), (HX + 11, HY + 22), 7)
    pygame.draw.line(surf, _SCARF_GOLD, (HX + 1, HY + 10), (HX + 11, HY + 22), 5)
    for t in (0.30, 0.65):
        tx = int((HX + 1) + ((HX + 11) - (HX + 1)) * t)
        ty = int((HY + 10) + (22 - 10) * t)
        pygame.draw.line(surf, _SCARF_PUR, (tx - 3, ty + 1), (tx + 3, ty - 1), 3)
    for j in (0, 3, 6):
        pygame.draw.line(surf, _SCARF_FRNG, (HX + 8 + j, HY + 22), (HX + 9 + j, HY + 25), 1)


build = store_skins._make_skin(_paint)
