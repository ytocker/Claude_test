"""EGG HATCHLING — Pip's just-hatched chick poking out of a cracked egg.

The parcel Pip carries is his newborn: a cream/white EGG cup broken open
along a jagged zig-zag rim, with a tiny red baby parrot rising out of the
top — same scarlet-macaw family as the parent (Pip-red head, blue wing
buds, a yellow hooked beak) so it reads as his offspring. The identity is
the two-mass contrast: a pale lower shell and a bright Pip-red head, kept
hard value-separated so they never fuse into one dark blob at true size.

22px read tradeoffs (WHY): at gameplay size the egg collapses to ONE bold
pale cup with a single jagged crack rim — fine speckles just turn to mud,
so the shell is sold by a flat cream fill, one darker rim crescent for
volume, and a 3-tooth zig-zag top edge that carries the "cracked open"
read on its own. The baby is a single bold red dome (head) seated in the
cup with a yellow beak wedge and two stubby blue wing nubs flanking it;
the wings are pushed darker than the head so grayscale shows head-vs-wing
separation, and the cream shell is the brightest mass so the chick never
sinks into it. A baked dark outline (inflated, drawn first) carries every
mass on bright DAY sky; a warm cream keyline rim inside is the NIGHT
lifeline. Everything is held off the surface edges so the head crown and
shell rim never clip as the parcel swings across Pip's bank arc.
"""
import pygame

# Palette mirrors Pip's own (game.draw) so the chick reads as his kin, but
# IDENTITY RIDES ON VALUE: the egg is engineered to be the BRIGHTEST mass
# (cream desaturates near-white), the baby HEAD is mid-bright Pip-red, and
# the wing nubs are pushed clearly DARKER than the head so grayscale shows
# three stacked values — pale shell, lit red head, dark wing buds.
SHELL = (246, 240, 226)        # cream egg shell (the bright value anchor)
SHELL_HI = (255, 253, 247)     # near-white top highlight band on the shell
SHELL_SHADE = (208, 196, 174)  # lower rim crescent — gives the cup volume
SHELL_RIM = (188, 174, 150)    # crack-edge shadow under the zig-zag teeth

HEAD = (240, 55, 55)           # Pip-red baby head (mid value)
HEAD_HI = (255, 120, 120)      # lit crown highlight so the dome reads round
HEAD_SHADE = (170, 25, 25)     # head underside shade into the shell line

WING = (40, 100, 255)          # Pip-blue wing nub — clearly darker than head
WING_D = (20, 55, 180)         # wing-nub shade (the darkest baby value)

BEAK = (255, 185, 0)           # Pip-yellow hooked beak wedge
BEAK_D = (200, 130, 0)
TIP = (50, 220, 100)           # Pip-green primary fleck — macaw signature

EYE = (40, 26, 30)             # dark eye + white glint, same as the parent
GLINT = (255, 255, 255)

OUTLINE = (44, 30, 22)         # warm-dark, high-contrast: reads on day sky
KEYLINE = (236, 222, 196)      # cream rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static hatchling sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # --- Egg-shell cup geometry. A broad bowl held LOW on the surface so the
    # baby's head + crown have room to rise above without clipping the edge
    # under the gameplay rotozoom.
    shell_cy = 30                  # shell centre y (biased low)
    shell_rx, shell_ry = 14, 13    # the bottom half of the egg = a cup
    rim_y = shell_cy - 4           # the broken-open crack line

    # Baked dark outline for the whole shell cup (drawn first, inflated).
    pygame.draw.ellipse(surf, OUTLINE,
                        pygame.Rect(cx - shell_rx - 2, shell_cy - shell_ry - 2,
                                    (shell_rx + 2) * 2, (shell_ry + 2) * 2))

    # Shell fill, then mask off everything above the crack rim so only the
    # lower cup remains — the baby will seat in the opening.
    pygame.draw.ellipse(surf, SHELL,
                        pygame.Rect(cx - shell_rx, shell_cy - shell_ry,
                                    shell_rx * 2, shell_ry * 2))
    # Lower-right shade crescent gives the cup volume (a darker ellipse nudged
    # off-centre, clipped to the shell so only the rim darkens).
    shade = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.ellipse(shade, SHELL_SHADE,
                        pygame.Rect(cx - shell_rx + 4, shell_cy - shell_ry + 5,
                                    shell_rx * 2, shell_ry * 2))
    mask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255),
                        pygame.Rect(cx - shell_rx, shell_cy - shell_ry,
                                    shell_rx * 2, shell_ry * 2))
    shade.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, 0))

    # --- BABY PARROT seated in the opening, drawn BEFORE the jagged rim teeth
    # so the teeth overlap and pin the head into the shell (newly hatched).
    head_cx, head_cy = cx + 1, rim_y - 5
    head_r = 8
    # Head outline halo so the red dome reads on bright day sky.
    pygame.draw.circle(surf, OUTLINE, (head_cx, head_cy), head_r + 2)

    # Wing nubs FIRST, flanking the head and seated LOWER (near the shell rim)
    # so they frame the head without crowding the beak; pushed darker so
    # grayscale separates them from the head. Stubby half-formed macaw wings.
    for sx in (-1, 1):
        wnx = head_cx + sx * 8
        pygame.draw.circle(surf, OUTLINE, (wnx, head_cy + 5), 5)
    pygame.draw.circle(surf, WING, (head_cx - 8, head_cy + 5), 4)
    pygame.draw.circle(surf, WING, (head_cx + 8, head_cy + 5), 4)
    pygame.draw.circle(surf, WING_D, (head_cx - 8, head_cy + 7), 3)
    pygame.draw.circle(surf, WING_D, (head_cx + 8, head_cy + 7), 3)
    # A green primary fleck on each wing — the scarlet-macaw signature, kept to
    # one dot per side so it survives the downscale.
    pygame.draw.circle(surf, TIP, (head_cx - 9, head_cy + 3), 1)
    pygame.draw.circle(surf, TIP, (head_cx + 9, head_cy + 3), 1)

    # Head dome (the hero red mass).
    pygame.draw.circle(surf, HEAD, (head_cx, head_cy), head_r)
    # Lit crown highlight so the head reads as a round volume, not a flat disc.
    pygame.draw.circle(surf, HEAD_HI, (head_cx - 3, head_cy - 3), 3)
    # Underside shade where the head meets the shell line.
    pygame.draw.arc(surf, HEAD_SHADE,
                    pygame.Rect(head_cx - head_r, head_cy - head_r + 2,
                                head_r * 2, head_r * 2), 3.6, 5.8, 2)

    # Eye + glint, same family as the parent's plain eye.
    pygame.draw.circle(surf, EYE, (head_cx + 2, head_cy - 1), 2)
    pygame.draw.circle(surf, GLINT, (head_cx + 1, head_cy - 2), 1)

    # Beak — a small hooked yellow wedge below the eye, outlined so it reads as
    # a distinct jut against the red head.
    beak = [(head_cx + 5, head_cy + 1), (head_cx + 10, head_cy + 3),
            (head_cx + 6, head_cy + 5)]
    pygame.draw.polygon(surf, OUTLINE, [(p[0], p[1]) for p in
                        [(head_cx + 5, head_cy), (head_cx + 11, head_cy + 3),
                         (head_cx + 6, head_cy + 6)]])
    pygame.draw.polygon(surf, BEAK, beak)
    pygame.draw.line(surf, BEAK_D, (head_cx + 5, head_cy + 3),
                     (head_cx + 9, head_cy + 3), 1)

    # --- JAGGED CRACK RIM: a zig-zag tooth row sitting ACROSS the shell mouth,
    # drawn over the head base so the chick reads as poking THROUGH the broken
    # opening. Three teeth carry the "cracked egg" read at 22px; finer cracks
    # turn to mud. Outlined dark, then filled cream with a shadow under each
    # tooth so the rim reads as broken shell, not a flat line.
    teeth = []
    n_teeth = 5
    span = shell_rx + 1
    for i in range(n_teeth * 2 + 1):
        tx = cx - span + (2 * span) * i / (n_teeth * 2)
        ty = rim_y + (3 if i % 2 == 0 else -4)
        teeth.append((tx, ty))
    # Close the polygon down around the shell bottom so it fills as a cup band.
    rim_poly = teeth + [(cx + span, shell_cy + 2), (cx - span, shell_cy + 2)]
    # Outline pass (slightly taller teeth) for the day read.
    out_poly = [(tx, ty - 1 if ty < rim_y else ty + 1) for tx, ty in teeth] + \
               [(cx + span, shell_cy + 3), (cx - span, shell_cy + 3)]
    pygame.draw.polygon(surf, OUTLINE, out_poly)
    pygame.draw.polygon(surf, SHELL, rim_poly)
    # Bright top band tracing the saw-tooth crest so the cracked rim catches
    # light and the zig-zag silhouette reads as broken shell, not a flat band.
    pygame.draw.lines(surf, SHELL_HI, False,
                      [(tx, ty) for tx, ty in teeth], 2)
    # A dark notch dropped into each valley so the teeth separate as cracks.
    for tx, ty in teeth:
        if ty > rim_y:
            pygame.draw.line(surf, SHELL_RIM, (tx, ty), (tx, ty + 2), 1)
    # Shadow under the rim where it meets the cup interior.
    pygame.draw.line(surf, SHELL_RIM, (cx - span + 1, rim_y + 4),
                     (cx + span - 1, rim_y + 4), 1)

    # --- Cream keyline rim INSIDE the shell outline — the NIGHT lifeline that
    # glows on dark sky while staying subtle on day. Traces the cup.
    pygame.draw.arc(surf, KEYLINE,
                    pygame.Rect(cx - shell_rx, shell_cy - shell_ry,
                                shell_rx * 2, shell_ry * 2), 3.3, 6.1, 1)

    return pygame.transform.smoothscale(surf, (22, 22))
