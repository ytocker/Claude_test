"""DISCO MIRROR-BALL SAUCER — party saucer scattering coloured light. R3.

At 22px, the premium read is a clean silver disc plus 4 hard saturated sparkle
dots and 3 bright light-ray spikes from the underside. No complex facet grid —
that resolution budget goes to the sparkle dots instead, which are the whole
identity of this design.
"""
import math

import pygame

SIZE = 22
SS   = 44

DISC_HI  = (210, 206, 238)   # mirror silver-violet (bright top)
DISC_MID = (178, 172, 215)   # mid disc
DISC_LO  = (138, 132, 175)   # belly shadow
DOME     = (230, 227, 248)   # dome cap
PINK     = (255, 80, 210)    # vivid pink glint
CYAN     = (50, 220, 255)    # vivid cyan glint
GOLD     = (255, 208, 40)    # vivid gold glint
OUTLINE  = (30, 22, 44)      # dark outline for sky contrast


def build(mode="normal"):
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)

    cx = SS // 2 + 1
    # Disc sits lower so its mass falls into the visible carry band rather than
    # the tail-occluded zone.
    cy = 33
    disc_rx, disc_ry = 17, 6
    dome_cy = cy - disc_ry - 3

    # ---- Dome cap on top ----
    pygame.draw.ellipse(s, OUTLINE,
        pygame.Rect(cx - 7, dome_cy - 5, 14, 10))
    pygame.draw.ellipse(s, DOME,
        pygame.Rect(cx - 6, dome_cy - 4, 12, 8))
    # Dome specular — mirror ball hot spot
    pygame.draw.circle(s, (255, 255, 255), (cx - 2, dome_cy - 2), 2)

    # ---- Dark outline halo around disc ----
    pygame.draw.ellipse(s, OUTLINE,
        pygame.Rect(cx - disc_rx - 2, cy - disc_ry - 2,
                    (disc_rx+2)*2, (disc_ry+2)*2))

    # ---- 3-value disc (top-lit mirror ball) via per-scanline fill ----
    for iy in range(-disc_ry, disc_ry + 1):
        t = (iy + disc_ry) / (disc_ry * 2)   # 0=top, 1=bottom
        col = (
            int(DISC_HI[0] + (DISC_LO[0] - DISC_HI[0]) * t),
            int(DISC_HI[1] + (DISC_LO[1] - DISC_HI[1]) * t),
            int(DISC_HI[2] + (DISC_LO[2] - DISC_HI[2]) * t),
        )
        frac = 1.0 - (iy / disc_ry) ** 2
        if frac < 0:
            continue
        hw = disc_rx * (frac ** 0.5)
        yy = cy + iy
        pygame.draw.line(s, col, (int(cx - hw), yy), (int(cx + hw), yy))

    # ---- 3 vertical facet column seams — the only "grid" element ----
    for gx in (cx - 7, cx + 1, cx + 9):
        gy_top = cy - disc_ry + 1
        gy_bot = cy + disc_ry - 1
        pygame.draw.line(s, OUTLINE, (gx, gy_top), (gx, gy_bot), 1)

    # ---- Premium focal glint at the lower rim (nearest point to viewer) ----
    rim_x = cx + disc_rx - 3
    rim_y = cy + 2
    pygame.draw.circle(s, (255, 255, 255), (rim_x, rim_y), 3)
    pygame.draw.circle(s, GOLD, (rim_x, rim_y), 2)
    pygame.draw.circle(s, (255, 255, 255), (rim_x, rim_y), 1)
    pygame.draw.line(s, (255, 240, 180), (rim_x - 5, rim_y), (rim_x + 5, rim_y), 1)
    pygame.draw.line(s, (255, 240, 180), (rim_x, rim_y - 5), (rim_x, rim_y + 5), 1)

    # ---- 4 hard saturated sparkle glints in the lower face ----
    # These are the TELL — bright solid dots with white cores
    glints = [
        (cx - 9, cy + 2, PINK),
        (cx - 2, cy + 3, CYAN),
        (cx + 5, cy + 2, GOLD),
        (cx + 11, cy + 1, PINK),
    ]
    for gx, gy, gc in glints:
        # Glow halo
        g = pygame.Surface((SS, SS), pygame.SRCALPHA)
        pygame.draw.circle(g, (*gc, 120), (gx, gy), 5)
        s.blit(g, (0, 0))
        # Solid saturated circle
        pygame.draw.circle(s, gc, (gx, gy), 3)
        # White spark core
        pygame.draw.circle(s, (255, 255, 255), (gx, gy), 1)

    # ---- 3 bright coloured light-rays from underside (mirror-ball scatter) ----
    # Fanned to different angles/lengths so they read as scattered beams, not a
    # symmetrical tripod. Each ray: white taper core + saturated colour tint.
    ray_base_y = cy + disc_ry - 1
    rays = [
        # (start_x, start_y, end_x, end_y, color, core_w)
        # Left ray: angled left, longer
        (cx - 5, ray_base_y,
         cx - 5 + int(14 * math.sin(math.radians(25))),
         ray_base_y + int(14 * math.cos(math.radians(25))),
         PINK, 3),
        # Center ray: straight down, medium
        (cx, ray_base_y, cx + 2, ray_base_y + 11, CYAN, 2),
        # Right ray: angled right, shorter
        (cx + 5, ray_base_y,
         cx + 5 + int(9 * math.sin(math.radians(-20))),
         ray_base_y + int(9 * math.cos(math.radians(-20))),
         GOLD, 2),
    ]
    for x1, y1, x2, y2, col, cw in rays:
        # White thick core with taper
        pygame.draw.line(s, (255, 255, 255), (x1, y1), (x2, y2), cw + 1)
        ray_s = pygame.Surface((SS, SS), pygame.SRCALPHA)
        pygame.draw.line(ray_s, (*col, 200), (x1, y1), (x2, y2), cw)
        s.blit(ray_s, (0, 0))

    # ---- Star-cross glints off the rim (2 floating) ----
    def star(px, py, col):
        pygame.draw.line(s, col, (px-4, py), (px+4, py), 1)
        pygame.draw.line(s, col, (px, py-4), (px, py+4), 1)
        pygame.draw.circle(s, (255, 255, 255), (px, py), 1)

    star(cx - disc_rx - 2, cy - 1, GOLD)
    star(cx + disc_rx + 2, cy + 1, PINK)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
