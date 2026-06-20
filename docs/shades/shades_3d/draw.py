"""SHADES style `shades_3d` — retro anaglyph cinema glasses (CARDBOARD).

The two-colour lens pair is the whole read: the EAR-side (far/back) lens is
RED, the BEAK-side (front/near) lens is CYAN, matching how anaglyph glasses
sit on a face. Pip faces RIGHT (facing=1) so cyan is to the right and the
flat paper temple arm runs left toward the ear.

Round-1 pick: the cheap-and-cheerful white-cardboard look — a continuous cut
brow-bar, square-ish cut-out lenses with a visible fold shadow, and a soft
translucent gel wash over each colour so the film reads as lit cellophane
rather than flat paint. Everything scales off `eye_w` (via max(1,int(...)))
so the red/cyan pair stays distinct from the product size down to eye_w=22.
"""
import pygame

# Anaglyph film — vivid so red vs cyan never collapse at 22px.
_RED      = (235, 42, 56)
_RED_H    = (255, 120, 124)
_RED_GEL  = (255, 70, 84, 150)
_CYAN     = (30, 198, 222)
_CYAN_H   = (165, 246, 250)
_CYAN_GEL = (90, 224, 240, 150)
_GLINT    = (255, 255, 255)

# White cardboard frame + two darkening edge tones for the cut/fold shadows.
_CARD    = (247, 244, 234)
_CARD_D  = (198, 192, 176)
_CARD_DD = (150, 144, 128)


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    lw = max(5, int(eye_w * 0.42))
    lh = max(5, int(eye_w * 0.40))
    sep = max(5, int(eye_w * 0.46))
    rad = max(1, int(eye_w * 0.05))    # barely rounded — it is cut paper
    thick = max(2, int(eye_w * 0.10))

    near = (cx + f * (sep // 2), cy)      # BEAK side -> cyan
    far = (cx - f * (sep // 2), cy)       # EAR side  -> red

    # One continuous card brow-bar so the frame reads as a single cut sheet.
    brow = pygame.Rect(0, 0, sep + lw + thick, max(2, int(eye_w * 0.12)))
    brow.center = (cx, cy - lh // 2 - thick // 2)
    pygame.draw.rect(surf, _CARD_D, brow.move(0, 1))
    pygame.draw.rect(surf, _CARD, brow)

    for (lx, ly), lens_c, lens_h, gel in (
            (far, _RED, _RED_H, _RED_GEL), (near, _CYAN, _CYAN_H, _CYAN_GEL)):
        outer = pygame.Rect(0, 0, lw + thick * 2, lh + thick * 2)
        outer.center = (lx, ly)
        pygame.draw.rect(surf, _CARD_DD, outer.move(0, 1), border_radius=rad)
        pygame.draw.rect(surf, _CARD, outer, border_radius=rad)
        # Inner fold shadow so the lens reads as a punched-out card window.
        pygame.draw.rect(surf, _CARD_D, outer.inflate(-thick, -thick),
                         max(1, thick // 2), border_radius=rad)
        # Coloured film: flat base + translucent gel wash for the glow.
        inner = pygame.Rect(0, 0, lw, lh)
        inner.center = (lx, ly)
        pygame.draw.rect(surf, lens_c, inner, border_radius=max(1, rad))
        gel_s = pygame.Surface(inner.size, pygame.SRCALPHA)
        pygame.draw.rect(gel_s, gel, gel_s.get_rect(), border_radius=max(1, rad))
        surf.blit(gel_s, inner.topleft)
        # Diagonal sheen + corner glint so the film looks lit, not printed.
        pygame.draw.line(surf, lens_h,
                         (lx - lw * 0.30, ly + lh * 0.10),
                         (lx + lw * 0.10, ly - lh * 0.28),
                         max(1, int(eye_w * 0.05)))
        pygame.draw.circle(surf, _GLINT,
                           (int(lx - lw * 0.26), int(ly - lh * 0.26)),
                           max(1, int(eye_w * 0.045)))

    # Card bridge dipping between the lenses (the paper nose notch).
    pygame.draw.line(surf, _CARD, (far[0] + f * (lw // 2), cy + lh // 6),
                     (near[0] - f * (lw // 2), cy + lh // 6), thick + 1)
    pygame.draw.line(surf, _CARD_D, (far[0] + f * (lw // 2), cy + lh // 6 + 1),
                     (near[0] - f * (lw // 2), cy + lh // 6 + 1), 1)

    # Flat folded paper temple arm toward the ear.
    arm_x = far[0] - f * (lw // 2 + thick)
    arm_end = (far[0] - f * (lw // 2 + max(3, int(eye_w * 0.34))),
               cy - max(2, int(eye_w * 0.11)))
    pygame.draw.line(surf, _CARD_D, (arm_x, cy - lh // 6 + 1),
                     (arm_end[0], arm_end[1] + 1), thick)
    pygame.draw.line(surf, _CARD, (arm_x, cy - lh // 6),
                     arm_end, max(1, thick - 1))
