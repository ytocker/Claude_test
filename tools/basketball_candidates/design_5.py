"""THE COACH — the sideline candidate (DESIGN 5 of 5, basketball set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
roster is untouched.

Concept: the only TAILORED silhouette in the basketball set — the man on the
bench, not a player. There is no kit and no ball: the read is carried by an
OPEN navy BLAZER over a white shirt whose lapels frame a knotted red TIE, a
pocket square at the near breast, a gold WHISTLE on a lanyard looped round the
neck, and — the hero, drawn LAST — a CLIPBOARD held up in the near wing with a
pale paper showing a tiny X/O/arrow play diagram. Dress-shoe ticks at the feet,
never athletic footwear. Pip's scarlet macaw head/beak/eye stay in the open so
it still reads as a parrot in a suit.

The silhouette tell at 40px is the V of the open jacket: two dark navy lapels
diverging from the neck over a bright white shirt wedge, with the red tie knot
sitting in the notch. The clipboard breaks the wing outline so the role reads
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
_C_SHIRT   = (244, 244, 248)         # #F4F4F8 white shirt
_C_SHIRT_D = (206, 208, 220)         # shirt fold shadow
_C_TIE     = (194, 57, 43)           # #C2392B tie red
_C_TIE_D   = (150, 40, 30)           # tie shadow
_C_DARK    = (26, 28, 34)            # #1A1C22 lapel edge / shoe
_C_GOLD    = (232, 178, 58)          # #E8B23A whistle + lanyard gold
_C_GOLD_H  = (255, 226, 150)         # whistle glint
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
    #    unbuttoned jacket rather than a solid block. Narrow V from the collar
    #    down to the belt.
    _poly(surf, _C_SHIRT, [(BCX - 3, BCY - 7), (BCX + 2, BCY - 7),
                           (BCX + 2, BCY + 13), (BCX - 3, BCY + 13)])
    # Soft fold shadow down the off side of the shirt placket.
    pygame.draw.line(surf, _C_SHIRT_D, (BCX - 2, BCY - 4), (BCX - 2, BCY + 11), 1)

    # 3-value cloth shading on the blazer: a shadow gusset where each panel meets
    # the open front, and a bright seam highlight down each outer fold so the
    # navy reads as tailored cloth, not a flat slab.
    _poly(surf, _C_NAVY_D, [(BCX - 3, BCY - 6), (BCX - 1, BCY + 2),
                            (BCX - 2, BCY + 13), (BCX - 4, BCY + 12)])   # off inner shade
    _poly(surf, _C_NAVY_D, [(BCX + 2, BCY - 6), (BCX, BCY + 2),
                            (BCX + 1, BCY + 13), (BCX + 3, BCY + 12)])    # near inner shade
    pygame.draw.line(surf, _C_NAVY_H, (BCX - 11, BCY - 3), (BCX - 11, BCY + 11), 1)  # off fold light
    pygame.draw.line(surf, _C_NAVY_H, (BCX + 10, BCY - 3), (BCX + 11, BCY + 11), 1)  # near fold light

    # ── LAPELS — the heart of the read. A dark notched lapel folds back off the
    #    collar on each side, the two of them forming the open-jacket V that
    #    frames the shirt + tie. Drawn as filled triangles so they survive the
    #    40px shrink, edged darker on the inner break line.
    _poly(surf, _C_NAVY_H, [(BCX - 3, BCY - 7), (BCX - 9, BCY - 6),
                            (BCX - 4, BCY + 3)])                          # off lapel face
    _poly(surf, _C_NAVY_H, [(BCX + 2, BCY - 7), (BCX + 8, BCY - 6),
                            (BCX + 3, BCY + 3)])                          # near lapel face
    pygame.draw.line(surf, _C_DARK, (BCX - 3, BCY - 7), (BCX - 4, BCY + 3), 1)  # off lapel break
    pygame.draw.line(surf, _C_DARK, (BCX + 2, BCY - 7), (BCX + 3, BCY + 3), 1)  # near lapel break
    # Tiny notch nick in each lapel — the cut that names it a suit collar.
    pygame.draw.line(surf, _C_DARK, (BCX - 8, BCY - 6), (BCX - 6, BCY - 4), 1)
    pygame.draw.line(surf, _C_DARK, (BCX + 7, BCY - 6), (BCX + 5, BCY - 4), 1)

    # ── KNOTTED TIE sitting in the lapel notch at the neck (BCY-9..) and a thin
    #    blade running down the shirt. The knot is the warm-red focal point in
    #    the V; shadowed on its lower-left so it reads as a folded knot.
    _poly(surf, _C_TIE, [(BCX - 2, BCY - 8), (BCX + 1, BCY - 8),
                         (BCX + 2, BCY - 5), (BCX - 1, BCY - 5),
                         (BCX - 3, BCY - 6)])                              # knot
    _poly(surf, _C_TIE_D, [(BCX - 3, BCY - 6), (BCX - 1, BCY - 5),
                           (BCX, BCY - 5)])                                # knot underfold
    _poly(surf, _C_TIE, [(BCX - 1, BCY - 5), (BCX + 1, BCY - 5),
                         (BCX + 1, BCY + 6), (BCX - 1, BCY + 8),
                         (BCX - 2, BCY + 6)])                              # blade
    pygame.draw.line(surf, _C_TIE_D, (BCX - 1, BCY - 4), (BCX - 1, BCY + 6), 1)  # blade shade

    # ── POCKET SQUARE at the near breast — a small white triangle peeking from
    #    the jacket, the tailored flourish that says "dressed up".
    _poly(surf, _C_SHIRT, [(BCX + 5, BCY - 1), (BCX + 9, BCY - 1),
                           (BCX + 7, BCY + 2)])
    pygame.draw.line(surf, _C_SHIRT_D, (BCX + 5, BCY - 1), (BCX + 9, BCY - 1), 1)

    # ── WHISTLE on a gold LANYARD looping the neck and dropping onto the chest.
    #    The cord runs from behind each collar down to a small whistle resting
    #    on the shirt; the whistle catches a glint so it reads as metal.
    pygame.draw.line(surf, _C_GOLD, (BCX - 6, BCY - 6), (BCX - 2, BCY + 4), 2)   # off cord
    pygame.draw.line(surf, _C_GOLD, (BCX + 6, BCY - 6), (BCX + 3, BCY + 3), 2)   # near cord
    wx, wy = BCX + 2, BCY + 5                                                     # whistle body
    pygame.draw.ellipse(surf, _C_GOLD, (wx - 3, wy - 2, 7, 5))
    pygame.draw.ellipse(surf, _C_GOLD_H, (wx - 2, wy - 1, 3, 2))                  # glint
    pygame.draw.line(surf, _C_GOLD, (wx + 3, wy - 1), (wx + 5, wy - 2), 2)        # mouthpiece

    # ── DRESS-SHOE ticks at the feet — flat, dark, narrow oxfords, deliberately
    #    NOT athletic high-tops: a low dark shoe with a thin sole tick and a tiny
    #    toe glint, sitting ON the feet line (~HY+22), never below it.
    for fx in (26, 34):
        _poly(surf, _C_DARK, [(fx - 4, HY + 22), (fx + 5, HY + 22),
                              (fx + 6, HY + 26), (fx - 4, HY + 26)])
        pygame.draw.line(surf, _C_NAVY_H, (fx - 3, HY + 22), (fx + 3, HY + 22), 1)  # toe glint
        pygame.draw.line(surf, _C_BOARD_D, (fx - 4, HY + 26), (fx + 6, HY + 26), 1) # sole tick

    # ── CLIPBOARD held up in the near wing — HERO, drawn LAST so it sits in
    #    front of jacket + lanyard and BREAKS the silhouette as a held prop. A
    #    small hardboard with a pale paper, a metal spring clip across the top,
    #    and a tiny play diagram (two X's, an O, and an arrow) so the read is
    #    unmistakably "coach". Held angled in the wing (~BCX+15, BCY-2); a held
    #    prop, so it may cross the outline, but nothing balloons the body.
    bx, by = BCX + 14, BCY - 4
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
