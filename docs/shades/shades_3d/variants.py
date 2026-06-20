"""ROUND 1 explorations for SHADES style `shades_3d` — retro anaglyph
cinema glasses. Three takes on the white/cardboard frame + RED (ear-side)
/ CYAN (beak-side) lens pair. Each exposes a `draw_shades` matching the
production contract so the render sheet can stamp them straight onto Pip.

Pip faces RIGHT (facing=1): the near/front lens (BEAK side, +facing) is
CYAN, the far/back lens (EAR side, -facing) is RED, the temple arm runs
toward the ear (-facing). The red/cyan pair is the whole read, so both
colours are pushed to stay distinct down at eye_w=22.
"""
import pygame

# Shared anaglyph palette — kept vivid so red vs cyan never collapse at 22px.
_RED      = (235, 42, 56)
_RED_H    = (255, 120, 124)
_RED_GEL  = (255, 70, 84, 150)
_CYAN     = (30, 198, 222)
_CYAN_H   = (165, 246, 250)
_CYAN_GEL = (90, 224, 240, 150)
_GLINT    = (255, 255, 255)


# ─────────────────────────────────────────────────────────────────────────────
# V1 · CARDBOARD — the cheap-and-cheerful paper-cinema look. Flat matte white
#     frame with a visible card seam, square-ish lenses, and a soft gel wash so
#     the colours read as translucent film rather than paint.
# ─────────────────────────────────────────────────────────────────────────────
_CARD    = (247, 244, 234)
_CARD_D  = (198, 192, 176)         # card edge / fold shadow
_CARD_DD = (150, 144, 128)


def draw_shades_cardboard(surf, cx, cy, eye_w, facing=1):
    f = facing
    lw = max(5, int(eye_w * 0.42))
    lh = max(5, int(eye_w * 0.40))
    sep = max(5, int(eye_w * 0.46))
    rad = max(1, int(eye_w * 0.05))   # only barely-rounded — it's paper
    thick = max(2, int(eye_w * 0.10))

    near = (cx + f * (sep // 2), cy)      # BEAK side -> cyan
    far = (cx - f * (sep // 2), cy)       # EAR side  -> red

    # One continuous card brow-bar across the top so it reads as one cut sheet.
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
        # Inner fold shadow inside the card rim so the cut-out reads.
        pygame.draw.rect(surf, _CARD_D, outer.inflate(-thick, -thick),
                         max(1, thick // 2), border_radius=rad)
        # Coloured film: flat base + a translucent gel wash for the glow.
        inner = pygame.Rect(0, 0, lw, lh)
        inner.center = (lx, ly)
        pygame.draw.rect(surf, lens_c, inner, border_radius=max(1, rad))
        gel_s = pygame.Surface(inner.size, pygame.SRCALPHA)
        pygame.draw.rect(gel_s, gel, gel_s.get_rect(),
                         border_radius=max(1, rad))
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
    pygame.draw.line(surf, _CARD_D, (arm_x, cy - lh // 6 + 1),
                     (far[0] - f * (lw // 2 + max(3, int(eye_w * 0.34))),
                      cy - max(2, int(eye_w * 0.11)) + 1), thick)
    pygame.draw.line(surf, _CARD, (arm_x, cy - lh // 6),
                     (far[0] - f * (lw // 2 + max(3, int(eye_w * 0.34))),
                      cy - max(2, int(eye_w * 0.11))), max(1, thick - 1))


# ─────────────────────────────────────────────────────────────────────────────
# V2 · PLASTIC — sleeker injection-moulded look. Glossy white frame with
#     rounded corners, a crisp bright top rim, deeper saturated lenses behind
#     glass with a hard specular streak. Reads more "premium toy" than paper.
# ─────────────────────────────────────────────────────────────────────────────
_PLAS    = (252, 250, 246)
_PLAS_H  = (255, 255, 255)
_PLAS_D  = (206, 206, 214)
_PLAS_DD = (150, 152, 164)


def draw_shades_plastic(surf, cx, cy, eye_w, facing=1):
    f = facing
    lw = max(5, int(eye_w * 0.44))
    lh = max(5, int(eye_w * 0.40))
    sep = max(5, int(eye_w * 0.46))
    rad = max(2, int(eye_w * 0.13))   # generous radius — moulded plastic
    thick = max(2, int(eye_w * 0.09))

    near = (cx + f * (sep // 2), cy)
    far = (cx - f * (sep // 2), cy)

    for (lx, ly), lens_c, lens_h, gel in (
            (far, _RED, _RED_H, _RED_GEL), (near, _CYAN, _CYAN_H, _CYAN_GEL)):
        outer = pygame.Rect(0, 0, lw + thick * 2, lh + thick * 2)
        outer.center = (lx, ly)
        # Moulded frame: dark seat under a glossy white shell + bright top rim.
        pygame.draw.rect(surf, _PLAS_DD, outer.move(0, 1), border_radius=rad)
        pygame.draw.rect(surf, _PLAS, outer, border_radius=rad)
        pygame.draw.line(surf, _PLAS_H, (outer.left + rad, outer.top + 1),
                         (outer.right - rad, outer.top + 1),
                         max(1, int(eye_w * 0.03)))
        # Glass lens: deep saturated film + translucent gel for the glow.
        inner = pygame.Rect(0, 0, lw, lh)
        inner.center = (lx, ly)
        irad = max(1, rad - 1)
        pygame.draw.rect(surf, lens_c, inner, border_radius=irad)
        gel_s = pygame.Surface(inner.size, pygame.SRCALPHA)
        pygame.draw.rect(gel_s, gel, gel_s.get_rect(), border_radius=irad)
        surf.blit(gel_s, inner.topleft)
        pygame.draw.rect(surf, lens_h, inner, max(1, int(eye_w * 0.03)),
                         border_radius=irad)
        # Hard specular streak sweeping the glass + a bright corner spark.
        pygame.draw.line(surf, _GLINT,
                         (lx - lw * 0.30, ly + lh * 0.18),
                         (lx + lw * 0.02, ly - lh * 0.30),
                         max(1, int(eye_w * 0.055)))
        pygame.draw.circle(surf, _GLINT,
                           (int(lx - lw * 0.28), int(ly - lh * 0.28)),
                           max(1, int(eye_w * 0.05)))

    # Sculpted bridge bar with a glossy top edge.
    by = cy - lh // 6
    pygame.draw.line(surf, _PLAS_DD, (far[0] + f * (lw // 2), by + 1),
                     (near[0] - f * (lw // 2), by + 1), thick + 1)
    pygame.draw.line(surf, _PLAS, (far[0] + f * (lw // 2), by),
                     (near[0] - f * (lw // 2), by), thick)
    pygame.draw.line(surf, _PLAS_H, (far[0] + f * (lw // 2), by - 1),
                     (near[0] - f * (lw // 2), by - 1), 1)

    # Rounded temple arm hinging back toward the ear.
    hinge = (far[0] - f * (lw // 2 + thick // 2), cy - lh // 6)
    ear = (far[0] - f * (lw // 2 + max(3, int(eye_w * 0.32))),
           cy - max(2, int(eye_w * 0.10)))
    pygame.draw.line(surf, _PLAS_DD, (hinge[0], hinge[1] + 1),
                     (ear[0], ear[1] + 1), thick)
    pygame.draw.line(surf, _PLAS, hinge, ear, max(1, thick - 1))
    pygame.draw.circle(surf, _PLAS_D, hinge, max(1, int(eye_w * 0.045)))


# ─────────────────────────────────────────────────────────────────────────────
# V3 · GLITCH OFFSET — leans into the anaglyph idea itself: the white frame is
#     RGB-split, each lens is doubled with a chromatic-aberration ghost, and a
#     few scanline ticks sell the "stereo mis-register" read. Loudest, most
#     game-y of the three.
# ─────────────────────────────────────────────────────────────────────────────
_FRAME   = (250, 248, 242)
_FRAME_D = (188, 184, 172)


def draw_shades_glitch(surf, cx, cy, eye_w, facing=1):
    f = facing
    lw = max(5, int(eye_w * 0.42))
    lh = max(5, int(eye_w * 0.40))
    sep = max(5, int(eye_w * 0.46))
    rad = max(1, int(eye_w * 0.07))
    thick = max(2, int(eye_w * 0.09))
    off = max(1, int(eye_w * 0.06))   # chromatic-aberration split distance

    near = (cx + f * (sep // 2), cy)
    far = (cx - f * (sep // 2), cy)

    # RGB-split frame ghosts: a red-shifted and a cyan-shifted copy of the
    # white frame bleed out behind the crisp white one — the glitch signature.
    for ghost_c, gx in ((_RED, -off), (_CYAN, off)):
        for (lx, ly) in (far, near):
            r = pygame.Rect(0, 0, lw + thick * 2, lh + thick * 2)
            r.center = (lx + gx, ly)
            pygame.draw.rect(surf, ghost_c, r, max(1, thick // 2),
                             border_radius=rad)
        pygame.draw.line(surf, ghost_c,
                         (far[0] + f * (lw // 2) + gx, cy - lh // 5),
                         (near[0] - f * (lw // 2) + gx, cy - lh // 5),
                         max(1, thick // 2))

    for (lx, ly), lens_c, lens_h, gel in (
            (far, _RED, _RED_H, _RED_GEL), (near, _CYAN, _CYAN_H, _CYAN_GEL)):
        # Crisp white frame on top of the ghosts.
        outer = pygame.Rect(0, 0, lw + thick * 2, lh + thick * 2)
        outer.center = (lx, ly)
        pygame.draw.rect(surf, _FRAME_D, outer.move(0, 1), border_radius=rad)
        pygame.draw.rect(surf, _FRAME, outer, border_radius=rad)
        inner = pygame.Rect(0, 0, lw, lh)
        inner.center = (lx, ly)
        # Doubled lens: an offset ghost of the OPPOSITE colour behind it sells
        # the mis-registered stereo image.
        other = _CYAN if lens_c is _RED else _RED
        ghost = pygame.Surface(inner.size, pygame.SRCALPHA)
        pygame.draw.rect(ghost, (*other, 120), ghost.get_rect(),
                         border_radius=max(1, rad))
        surf.blit(ghost, (inner.x - f * off, inner.y))
        pygame.draw.rect(surf, lens_c, inner, border_radius=max(1, rad))
        gel_s = pygame.Surface(inner.size, pygame.SRCALPHA)
        pygame.draw.rect(gel_s, gel, gel_s.get_rect(),
                         border_radius=max(1, rad))
        surf.blit(gel_s, inner.topleft)
        # Scanline ticks across the lens — the CRT/glitch read.
        for i in range(1, 3):
            yy = inner.top + i * inner.h // 3
            pygame.draw.line(surf, (*lens_h, 150),
                             (inner.left + 1, yy), (inner.right - 1, yy), 1)
        pygame.draw.circle(surf, _GLINT,
                           (int(lx - lw * 0.26), int(ly - lh * 0.26)),
                           max(1, int(eye_w * 0.045)))

    # Crisp white bridge over the ghosts.
    pygame.draw.line(surf, _FRAME, (far[0] + f * (lw // 2), cy - lh // 5),
                     (near[0] - f * (lw // 2), cy - lh // 5), thick)

    # Jagged glitch temple arm toward the ear (stepped, not straight).
    ax = far[0] - f * (lw // 2 + thick)
    p0 = (ax, cy - lh // 6)
    p1 = (ax - f * max(2, int(eye_w * 0.14)), cy - lh // 6)
    p2 = (ax - f * max(2, int(eye_w * 0.16)), cy - max(2, int(eye_w * 0.10)))
    p3 = (ax - f * max(3, int(eye_w * 0.32)), cy - max(2, int(eye_w * 0.11)))
    pygame.draw.lines(surf, _FRAME, False, [p0, p1, p2, p3], max(1, thick - 1))
    pygame.draw.circle(surf, _RED, p1, max(1, int(eye_w * 0.04)))
    pygame.draw.circle(surf, _CYAN, p2, max(1, int(eye_w * 0.04)))
