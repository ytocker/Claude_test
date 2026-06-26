"""THE COACH — the sideline candidate (DESIGN 5 of 5, basketball set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
roster is untouched.

Concept: the only TAILORED silhouette in the basketball set — the man on the
bench, not a player. There is no kit and no ball: the read is carried by an
OPEN navy BLAZER over a white shirt whose lighter lapels frame a knotted red
TIE, a pocket square at the near breast, a slim gold lanyard V at the neck, and
— the hero, drawn LAST — a CLIPBOARD held at chest/wing level with a pale paper
showing a tiny X/O/arrow play diagram. Dress-shoe ticks at the feet, never
athletic footwear. Pip's scarlet macaw head/beak/eye stay clear in the open so
it still reads as a parrot in a suit.

The silhouette tell at 40px is the V of the open jacket: two lighter navy
lapels, each hard-edged with a dark break-line, diverging from the neck over a
wide white shirt wedge, with the fattened red tie running down it. The
clipboard sits low on the body, off the face, and breaks the wing so the role
even when the cloth values muddy on a busy sky. Blazer is a mid-dark navy so
the white shirt + gold whistle pop on it and it separates from the scarlet head
above and from a bright day sky.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Tailored, not athletic. Navy carries 3 cloth values; the shirt is near-white
# so the lapel Vee reads; tie red is warm so it stands off both navy and shirt.
_C_NAVY    = (35, 48, 79)            # #23304F blazer navy (mid)
_C_NAVY_D  = (22, 31, 54)            # blazer shadow / inner shade
_C_NAVY_H  = (58, 76, 116)           # blazer highlight seam
_C_LAPEL   = (76, 96, 140)           # #4C608C lapel face — lighter so the V reads
_C_SHIRT   = (244, 244, 248)         # #F4F4F8 white shirt
_C_SHIRT_D = (206, 208, 220)         # shirt fold shadow
_C_TIE     = (194, 57, 43)           # #C2392B tie red
_C_TIE_D   = (150, 40, 30)           # tie shadow
_C_DARK    = (26, 28, 34)            # #1A1C22 lapel edge / shoe
_C_GOLD    = (232, 178, 58)          # #E8B23A lanyard gold
_C_BOARD   = (150, 110, 70)          # clipboard hardboard
_C_BOARD_D = (110, 78, 48)           # clipboard edge shadow
_C_PAPER   = (238, 238, 230)         # clipboard paper
_C_PAPER_D = (200, 200, 192)         # paper shadow
_C_CLIP    = (190, 192, 200)         # metal spring clip
_C_INK     = (40, 52, 90)            # play-diagram ink (navy, not pure black)


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # ── OPEN BLAZER painted over the torso. The jacket is drawn as two front
    #    panels with a wide gap, NOT a closed coat: the gap exposes a white
    #    shirt wedge so the open-jacket V — the tailored silhouette tell — is
    #    explicit at 40px. Hem held inside the footprint (~BCY+14).
    #    Off-side (far) panel.
    _poly(surf, _C_NAVY, [(BCX - 12, BCY - 6), (BCX - 3, BCY - 7),
                          (BCX - 1, BCY + 2), (BCX - 2, BCY + 14),
                          (BCX - 12, BCY + 14), (BCX - 14, BCY + 2)])
    #    Near-side panel — slightly forward so the jacket has front-to-back form.
    _poly(surf, _C_NAVY, [(BCX + 11, BCY - 6), (BCX + 2, BCY - 7),
                          (BCX, BCY + 2), (BCX + 1, BCY + 14),
                          (BCX + 12, BCY + 14), (BCX + 14, BCY + 2)])

    # ── WHITE SHIRT wedge filling the open front so the navy panels read as an
    #    unbuttoned jacket rather than a solid block. Widened ~1.5× into a clear
    #    V so the open-jacket triangle survives the 40px shrink — it tapers from
    #    a broad collar opening down to the belt, with the red tie laid over it.
    _poly(surf, _C_SHIRT, [(BCX - 5, BCY - 7), (BCX + 4, BCY - 7),
                           (BCX + 3, BCY + 13), (BCX - 4, BCY + 13)])
    # Soft fold shadow down the off side of the shirt placket.
    pygame.draw.line(surf, _C_SHIRT_D, (BCX - 3, BCY - 4), (BCX - 3, BCY + 11), 1)

    # 3-value cloth shading on the blazer: a shadow gusset where each panel meets
    # the open front, and a bright seam highlight down each outer fold so the
    # navy reads as tailored cloth, not a flat slab.
    _poly(surf, _C_NAVY_D, [(BCX - 3, BCY - 6), (BCX - 1, BCY + 2),
                            (BCX - 2, BCY + 13), (BCX - 4, BCY + 12)])   # off inner shade
    _poly(surf, _C_NAVY_D, [(BCX + 2, BCY - 6), (BCX, BCY + 2),
                            (BCX + 1, BCY + 13), (BCX + 3, BCY + 12)])    # near inner shade
    pygame.draw.line(surf, _C_NAVY_H, (BCX - 11, BCY - 3), (BCX - 11, BCY + 11), 1)  # off fold light
    pygame.draw.line(surf, _C_NAVY_H, (BCX + 10, BCY - 3), (BCX + 11, BCY + 11), 1)  # near fold light

    # ── LAPELS — the heart of the read. A notched lapel folds back off the
    #    collar on each side, the two of them forming the open-jacket V that
    #    frames the shirt + tie. Painted in a LIGHTER navy than the blazer body
    #    and edged with a hard 1px dark break-line on each inner edge so two
    #    distinct diagonal lapels read at 40px instead of merging into the panel.
    #    Bigger triangles, reaching further down the chest, so the Vee is bold.
    _poly(surf, _C_LAPEL, [(BCX - 5, BCY - 7), (BCX - 11, BCY - 6),
                           (BCX - 5, BCY + 6)])                           # off lapel face
    _poly(surf, _C_LAPEL, [(BCX + 4, BCY - 7), (BCX + 10, BCY - 6),
                           (BCX + 4, BCY + 6)])                           # near lapel face
    pygame.draw.line(surf, _C_DARK, (BCX - 5, BCY - 7), (BCX - 5, BCY + 6), 1)  # off lapel break
    pygame.draw.line(surf, _C_DARK, (BCX + 4, BCY - 7), (BCX + 4, BCY + 6), 1)  # near lapel break
    pygame.draw.line(surf, _C_NAVY_D, (BCX - 11, BCY - 6), (BCX - 5, BCY + 6), 1)  # off outer fold
    pygame.draw.line(surf, _C_NAVY_D, (BCX + 10, BCY - 6), (BCX + 4, BCY + 6), 1)  # near outer fold
    # Tiny notch nick in each lapel — the cut that names it a suit collar.
    pygame.draw.line(surf, _C_DARK, (BCX - 10, BCY - 6), (BCX - 8, BCY - 4), 1)
    pygame.draw.line(surf, _C_DARK, (BCX + 9, BCY - 6), (BCX + 7, BCY - 4), 1)

    # ── KNOTTED TIE sitting in the lapel notch at the neck — the second focal
    #    point after the clipboard. The knot is fattened a px each way and the
    #    blade is widened + lengthened into a CONTINUOUS warm-red stripe running
    #    the full white shirt wedge, so the tie reads as a bold vertical accent
    #    inside the V. Shadowed on its lower-left so the knot folds, edged on the
    #    blade so it has roundness.
    _poly(surf, _C_TIE, [(BCX - 3, BCY - 8), (BCX + 2, BCY - 8),
                         (BCX + 3, BCY - 4), (BCX - 2, BCY - 4),
                         (BCX - 4, BCY - 5)])                              # knot
    _poly(surf, _C_TIE_D, [(BCX - 4, BCY - 5), (BCX - 2, BCY - 4),
                           (BCX, BCY - 4)])                                # knot underfold
    _poly(surf, _C_TIE, [(BCX - 2, BCY - 4), (BCX + 2, BCY - 4),
                         (BCX + 2, BCY + 8), (BCX, BCY + 11),
                         (BCX - 2, BCY + 8)])                              # blade
    pygame.draw.line(surf, _C_TIE_D, (BCX + 1, BCY - 3), (BCX + 1, BCY + 8), 1)  # blade shade
    pygame.draw.line(surf, _C_TIE_D, (BCX - 4, BCY - 5), (BCX - 2, BCY - 4), 1)  # knot edge

    # ── POCKET SQUARE on the near navy breast — a small white triangle peeking
    #    from the jacket above the held clipboard, the tailored flourish that
    #    says "dressed up". Sits on the panel clear of the lapel and the board.
    _poly(surf, _C_SHIRT, [(BCX + 6, BCY - 2), (BCX + 10, BCY - 2),
                           (BCX + 8, BCY + 1)])
    pygame.draw.line(surf, _C_SHIRT_D, (BCX + 6, BCY - 2), (BCX + 10, BCY - 2), 1)

    # ── WHISTLE LANYARD — kept as a slim gold V over the white shirt: two thin
    #    cords from behind each collar meeting at the neck. The whistle DISC
    #    itself is dropped — the clipboard already carries the coach role, and a
    #    whistle body fighting the fattened tie + the chest-height clipboard read
    #    as clutter at 40px. The bare gold V is enough to suggest a lanyard.
    pygame.draw.line(surf, _C_GOLD, (BCX - 6, BCY - 6), (BCX, BCY - 3), 1)        # off cord
    pygame.draw.line(surf, _C_GOLD, (BCX + 6, BCY - 6), (BCX, BCY - 3), 1)        # near cord

    # ── DRESS-SHOE ticks at the feet — flat, dark, narrow oxfords, deliberately
    #    NOT athletic high-tops: a low dark shoe with a thin sole tick and a tiny
    #    toe glint, sitting ON the feet line (~HY+22), never below it.
    for fx in (26, 34):
        _poly(surf, _C_DARK, [(fx - 4, HY + 22), (fx + 5, HY + 22),
                              (fx + 6, HY + 26), (fx - 4, HY + 26)])
        pygame.draw.line(surf, _C_NAVY_H, (fx - 3, HY + 22), (fx + 3, HY + 22), 1)  # toe glint
        pygame.draw.line(surf, _C_BOARD_D, (fx - 4, HY + 26), (fx + 6, HY + 26), 1) # sole tick

    # ── CLIPBOARD held up at chest/wing level — HERO, drawn LAST so it sits in
    #    front of jacket + lanyard and BREAKS the silhouette as a held prop. A
    #    small hardboard with a pale paper, a metal spring clip across the top,
    #    and a tiny play diagram (two X's, an O, and an arrow) so the read is
    #    unmistakably "coach". Anchored LOW (~BCX+15, BCY+3) so the board clears
    #    the head/eye/beak and the X/O diagram lands legibly on the body, not the
    #    face: a held document, never a mask. Held as a prop, so it may cross the
    #    near outline, but nothing balloons the body.
    bx, by = BCX + 15, BCY + 3
    board = [(bx - 4, by - 8), (bx + 8, by - 6),
             (bx + 6, by + 8), (bx - 6, by + 6)]
    _poly(surf, _C_BOARD_D, [(p[0] + 1, p[1] + 1) for p in board])               # board edge
    _poly(surf, _C_BOARD, board)
    # Pale paper inset, slightly smaller than the board.
    paper = [(bx - 3, by - 6), (bx + 6, by - 4),
             (bx + 4, by + 6), (bx - 5, by + 4)]
    _poly(surf, _C_PAPER_D, [(p[0] + 1, p[1] + 1) for p in paper])
    _poly(surf, _C_PAPER, paper)
    # Metal spring clip across the top of the board.
    pygame.draw.line(surf, _C_CLIP, (bx - 4, by - 7), (bx + 7, by - 5), 2)
    pygame.draw.line(surf, _C_BOARD_D, (bx, by - 7), (bx + 1, by - 5), 2)        # clip lever
    # Tiny play diagram on the paper — X's, an O, and a routing arrow.
    pygame.draw.line(surf, _C_INK, (bx - 2, by - 3), (bx, by - 1), 1)            # X
    pygame.draw.line(surf, _C_INK, (bx, by - 3), (bx - 2, by - 1), 1)
    pygame.draw.line(surf, _C_INK, (bx + 2, by), (bx + 4, by + 2), 1)           # X
    pygame.draw.line(surf, _C_INK, (bx + 4, by), (bx + 2, by + 2), 1)
    pygame.draw.circle(surf, _C_INK, (bx - 2, by + 3), 2, 1)                     # O
    pygame.draw.lines(surf, _C_INK, False,
                      [(bx, by - 1), (bx + 2, by + 1), (bx + 1, by + 3)], 1)     # arrow path
    pygame.draw.line(surf, _C_INK, (bx + 1, by + 3), (bx + 2, by + 2), 1)        # arrowhead
    pygame.draw.line(surf, _C_INK, (bx + 1, by + 3), (bx - 1, by + 3), 1)


build = store_skins._make_skin(_paint)
