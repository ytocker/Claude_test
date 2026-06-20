"""NERD SPECS — thin round wire frames, clear/faintly-tinted lenses.

Side-profile eyewear for Pip. All geometry is proportional to ``eye_w`` so
the single function serves both the big product shot and the 22px in-game
overlay. The bookish read comes from perfectly round thin wire rims with an
only-just-tinted lens, so the macaw's eye stays visible underneath.
"""
import pygame

_WIRE   = (60, 56, 70)
_WIRE_H = (150, 150, 170)
_TINT   = (210, 230, 240, 70)      # barely-there glass
_GLINT  = (255, 255, 255)


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    r = max(2, int(eye_w * 0.30))          # round-lens radius
    sep = max(3, int(eye_w * 0.46))        # centre-to-centre lens spacing
    rim = max(1, int(eye_w * 0.055))       # thin wire

    near = (cx + f * (sep // 2), cy)       # toward the beak
    far  = (cx - f * (sep // 2), cy)       # toward the ear

    # Faint glass fill first so the wire rim sits crisply on top.
    for (lx, ly) in (near, far):
        glass = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glass, _TINT, (r, r), r)
        surf.blit(glass, (lx - r, ly - r))

    # Thin round wire rims.
    for (lx, ly) in (near, far):
        pygame.draw.circle(surf, _WIRE, (lx, ly), r, rim)
    # Top-arc highlight so the wire reads as metal, not a flat ring.
    pygame.draw.arc(surf, _WIRE_H, (near[0] - r, near[1] - r, r * 2, r * 2),
                    0.5, 2.2, rim)

    # Bridge — a shallow keyhole hop between the rims.
    bx0 = far[0] + f * r
    bx1 = near[0] - f * r
    pygame.draw.line(surf, _WIRE, (bx0, cy - r // 2), (bx1, cy - r // 2), rim)

    # Temple arm sweeping back toward the ear.
    pygame.draw.line(surf, _WIRE, (far[0] - f * r, cy),
                     (far[0] - f * (r + max(2, int(eye_w * 0.34))), cy - max(1, int(eye_w * 0.06))),
                     rim)

    # Tiny pinpoint glints sell the glass.
    pygame.draw.circle(surf, _GLINT, (near[0] - f * (r // 2), cy - r // 2),
                       max(1, int(eye_w * 0.05)))
    pygame.draw.circle(surf, _GLINT, (far[0] - f * (r // 2), cy - r // 2),
                       max(1, int(eye_w * 0.045)))
