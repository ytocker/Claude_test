"""3D GLASSES — cardboard/white frame, anaglyph red + cyan lenses.

The two-colour lens pair is the whole read: the EAR-side (far/back) lens is
red, the BEAK-side (front/near) lens is cyan, matching how anaglyph glasses
sit on a face. White cardboard frame keeps it cheap-and-cheerful.
"""
import pygame

_CARD    = (248, 246, 240)         # white cardboard
_CARD_D  = (205, 200, 188)
_RED     = (235, 45, 60)
_RED_H   = (255, 120, 120)
_CYAN    = (40, 200, 220)
_CYAN_H  = (160, 245, 250)
_GLINT   = (255, 255, 255)


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    lw = max(4, int(eye_w * 0.40))
    lh = max(4, int(eye_w * 0.38))
    sep = max(4, int(eye_w * 0.44))
    rad = max(1, int(eye_w * 0.06))
    thick = max(1, int(eye_w * 0.08))

    near = (cx + f * (sep // 2), cy)       # beak-side -> cyan
    far  = (cx - f * (sep // 2), cy)       # ear-side  -> red

    specs = ((far, _RED, _RED_H), (near, _CYAN, _CYAN_H))
    for (lx, ly), lens_c, lens_h in specs:
        outer = pygame.Rect(0, 0, lw + thick * 2, lh + thick * 2)
        outer.center = (lx, ly)
        pygame.draw.rect(surf, _CARD_D, outer.move(0, 1), border_radius=rad)
        pygame.draw.rect(surf, _CARD, outer, border_radius=rad)
        inner = pygame.Rect(0, 0, lw, lh)
        inner.center = (lx, ly)
        pygame.draw.rect(surf, lens_c, inner, border_radius=max(1, rad - 1))
        # translucent colour gel sheen
        pygame.draw.line(surf, lens_h, (lx - f * lw * 0.28, ly - lh * 0.26),
                         (lx + f * lw * 0.05, ly + lh * 0.04),
                         max(1, int(eye_w * 0.05)))
        pygame.draw.circle(surf, _GLINT,
                           (int(lx - f * lw * 0.26), int(ly - lh * 0.26)),
                           max(1, int(eye_w * 0.04)))

    # Cardboard bridge.
    pygame.draw.line(surf, _CARD, (far[0] + f * (lw // 2), cy - lh // 4),
                     (near[0] - f * (lw // 2), cy - lh // 4), thick + 1)
    pygame.draw.line(surf, _CARD_D, (far[0] + f * (lw // 2), cy - lh // 4 + 1),
                     (near[0] - f * (lw // 2), cy - lh // 4 + 1), 1)

    # Temple arm toward the ear.
    pygame.draw.line(surf, _CARD, (far[0] - f * (lw // 2 + thick), cy - lh // 5),
                     (far[0] - f * (lw // 2 + max(2, int(eye_w * 0.30))),
                      cy - max(1, int(eye_w * 0.09))), thick)
