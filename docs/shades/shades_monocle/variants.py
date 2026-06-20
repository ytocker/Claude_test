"""Round-1 MONOCLE explorations (3 variants).

Each is a self-contained `draw_shades(surf, cx, cy, eye_w, facing=1)` matching
the SHADES contract: a SINGLE round lens over the FRONT/beak-side eye, with a
fine chain dangling DOWN. The classic monocle read is the thick metal ring +
glassy glint + the dangling chain (and a tiny knurled adjuster screw).

All geometry is proportional to eye_w via max(1,int(eye_w*k)) so the ring still
reads at eye_w=22 (in-game) where the rim radius lands ~6px, and at eye_w=96
(product shot).
"""
import pygame


# ── A · CLASSIC GOLD — thin gold rim, fine 2-segment chain, knurled adjuster ──
A_RIM   = (242, 202, 92)
A_RIM_D = (188, 146, 38)
A_RIM_H = (255, 246, 184)
A_GLASS = (196, 214, 224, 64)
A_CHAIN = (214, 180, 84)
A_CHAIN_D = (168, 134, 52)
A_GLINT = (255, 255, 255)


def draw_shades_A(surf, cx, cy, eye_w, facing=1):
    f = facing
    r = max(6, int(eye_w * 0.34))
    rim = max(2, int(eye_w * 0.095))

    # Single lens over the NEAR (beak-side) eye.
    lx = cx + f * max(3, int(eye_w * 0.16))
    ly = cy

    # Faint cool glass.
    glass = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(glass, A_GLASS, (r, r), r)
    surf.blit(glass, (lx - r, ly - r))

    # Gold ring: shaded underside, bright top-arc for roundness.
    pygame.draw.circle(surf, A_RIM_D, (lx, ly), r, rim)
    pygame.draw.circle(surf, A_RIM, (lx, ly), r, max(1, rim - 1))
    pygame.draw.arc(surf, A_RIM_H, (lx - r, ly - r, r * 2, r * 2), 0.5, 2.3,
                    max(1, rim - 1))

    # Knurled adjuster screw on the ear-side of the ring.
    kn = (lx - f * r, ly)
    pygame.draw.circle(surf, A_RIM_D, kn, max(2, int(eye_w * 0.07)))
    pygame.draw.circle(surf, A_RIM_H, (kn[0], kn[1] - 1), max(1, int(eye_w * 0.03)))

    # Glassy glints.
    pygame.draw.circle(surf, A_GLINT, (lx - f * (r // 2), ly - r // 2),
                       max(1, int(eye_w * 0.07)))
    pygame.draw.circle(surf, (255, 255, 255, 200),
                       (lx + f * (r // 3), ly + r // 3), max(1, int(eye_w * 0.04)))

    # Fine 2-segment chain dropping straight down from the lower-ear anchor.
    anchor = (lx - f * (r - max(1, int(eye_w * 0.04))), ly + r // 2)
    drop = max(4, int(eye_w * 0.55))
    cw = max(1, int(eye_w * 0.045))
    p_mid = (anchor[0] - f * max(1, int(eye_w * 0.04)), anchor[1] + drop // 2)
    p_end = (anchor[0] - f * max(1, int(eye_w * 0.10)), anchor[1] + drop)
    pygame.draw.line(surf, A_CHAIN_D, anchor, p_mid, cw)
    pygame.draw.line(surf, A_CHAIN, anchor, p_mid, max(1, cw - 1))
    pygame.draw.line(surf, A_CHAIN_D, p_mid, p_end, cw)
    pygame.draw.line(surf, A_CHAIN, p_mid, p_end, max(1, cw - 1))
    pygame.draw.circle(surf, A_CHAIN, p_end, max(1, int(eye_w * 0.05)))


# ── B · SILVER + BEADED CHAIN — cool platinum rim, link-bead chain (ball-link) ─
B_RIM   = (216, 222, 232)
B_RIM_D = (138, 146, 160)
B_RIM_H = (255, 255, 255)
B_GLASS = (180, 200, 214, 72)
B_BEAD  = (200, 206, 218)
B_BEAD_D = (132, 140, 154)
B_GLINT = (255, 255, 255)


def draw_shades_B(surf, cx, cy, eye_w, facing=1):
    f = facing
    r = max(6, int(eye_w * 0.34))
    rim = max(2, int(eye_w * 0.10))

    lx = cx + f * max(3, int(eye_w * 0.16))
    ly = cy

    glass = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(glass, B_GLASS, (r, r), r)
    surf.blit(glass, (lx - r, ly - r))

    pygame.draw.circle(surf, B_RIM_D, (lx, ly), r, rim)
    pygame.draw.circle(surf, B_RIM, (lx, ly), r, max(1, rim - 1))
    pygame.draw.arc(surf, B_RIM_H, (lx - r, ly - r, r * 2, r * 2), 0.5, 2.3,
                    max(1, rim - 1))

    # Glints.
    pygame.draw.circle(surf, B_GLINT, (lx - f * (r // 2), ly - r // 2),
                       max(1, int(eye_w * 0.07)))
    pygame.draw.circle(surf, (255, 255, 255, 200),
                       (lx + f * (r // 3), ly + r // 3), max(1, int(eye_w * 0.04)))

    # Ball-link beaded chain: a column of small beads down the ear-side.
    anchor = (lx - f * (r - max(1, int(eye_w * 0.03))), ly + r // 2)
    drop = max(4, int(eye_w * 0.58))
    bead_r = max(1, int(eye_w * 0.05))
    step = max(2, bead_r * 2 + 1)
    n = max(2, drop // step)
    for i in range(n + 1):
        t = i / n
        bx = anchor[0] - f * int(max(1, int(eye_w * 0.10)) * t)
        by = anchor[1] + int(drop * t)
        pygame.draw.circle(surf, B_BEAD_D, (bx, by), bead_r)
        pygame.draw.circle(surf, B_BEAD, (bx, by - 1 if bead_r > 1 else by),
                           max(1, bead_r - 1))


# ── C · TYCOON — thick double-band gold rim, heavier 3-link chain + fob ───────
C_RIM   = (246, 206, 96)
C_RIM_D = (176, 132, 30)
C_RIM_H = (255, 248, 196)
C_GLASS = (210, 192, 150, 70)        # warm amber tint — the "rich" read
C_CHAIN = (224, 188, 88)
C_CHAIN_D = (168, 128, 44)
C_GLINT = (255, 255, 255)


def draw_shades_C(surf, cx, cy, eye_w, facing=1):
    f = facing
    r = max(6, int(eye_w * 0.36))
    rim = max(3, int(eye_w * 0.15))     # thick tycoon band

    lx = cx + f * max(3, int(eye_w * 0.15))
    ly = cy

    # Warm amber glass.
    glass = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(glass, C_GLASS, (r, r), r)
    surf.blit(glass, (lx - r, ly - r))

    # Thick double-band ring (outer dark bevel + inner bright band).
    pygame.draw.circle(surf, C_RIM_D, (lx, ly), r, rim)
    pygame.draw.circle(surf, C_RIM, (lx, ly), r - max(1, rim // 3),
                       max(2, rim - max(1, rim // 3)))
    pygame.draw.arc(surf, C_RIM_H, (lx - r, ly - r, r * 2, r * 2), 0.6, 2.2,
                    max(2, rim - 2))

    # Glints.
    pygame.draw.circle(surf, C_GLINT, (lx - f * (r // 2), ly - r // 2),
                       max(1, int(eye_w * 0.08)))
    pygame.draw.circle(surf, (255, 255, 255, 200),
                       (lx + f * (r // 3), ly + r // 3), max(1, int(eye_w * 0.045)))

    # Anchor loop where the chain bolts onto the ring.
    anchor = (lx - f * r, ly + r // 3)
    pygame.draw.circle(surf, C_CHAIN_D, anchor, max(2, int(eye_w * 0.07)))
    pygame.draw.circle(surf, C_RIM_H, (anchor[0], anchor[1] - 1),
                       max(1, int(eye_w * 0.03)))

    # Heavier 3-link chain swinging down + a small round fob at the end.
    drop = max(4, int(eye_w * 0.55))
    cw = max(1, int(eye_w * 0.06))
    pts = [anchor]
    for i in range(1, 4):
        t = i / 3
        px = anchor[0] - f * int(max(1, int(eye_w * 0.12)) * t)
        py = anchor[1] + int(drop * t)
        pts.append((px, py))
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, C_CHAIN_D, pts[i], pts[i + 1], cw)
        pygame.draw.line(surf, C_CHAIN, pts[i], pts[i + 1], max(1, cw - 1))
    # Coin-like fob.
    fob = pts[-1]
    pygame.draw.circle(surf, C_CHAIN, fob, max(2, int(eye_w * 0.08)))
    pygame.draw.circle(surf, C_CHAIN_D, fob, max(2, int(eye_w * 0.08)), 1)
    pygame.draw.circle(surf, C_RIM_H, (fob[0], fob[1] - 1), max(1, int(eye_w * 0.03)))


VARIANTS = [
    ("A  Classic Gold", draw_shades_A),
    ("B  Silver Bead",  draw_shades_B),
    ("C  Tycoon",       draw_shades_C),
]
