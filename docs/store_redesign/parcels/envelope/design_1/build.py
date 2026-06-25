"""AIRMAIL — par-avion ENVELOPE parcel (LOW-tier cosmetic).

The classic airmail envelope. A ~22px slab carried below Pip that rotates with
his bank, so the read must survive the rotozoom on DAY and NIGHT sky. The
IDENTITY is the red+blue dashed candy-stripe perimeter border — no other
envelope concept has the candy edge — so the stripe is drawn bold and full-
perimeter, the one thing that must register before any detail. A small red
postage stamp (top-right), a blue "PAR AVION" label bar (lower-left), and a
faint flap V (top) layer on so the body is never a blank card.

Drawn on a 44px work surface then smoothscaled to 22 so the thin stripe segments
and the keyline antialias cleanly. A baked dark outline is drawn first (slightly
inflated) so the white body still reads as a shape on bright day sky; a warm
night keyline rim rides just inside the body so the white slab also reads on dark
night sky without a per-mode sprite. The body is kept off the surface edges so
the in-game rotozoom never clips the corners.
"""
import pygame

# DAY airmail palette + a NIGHT-friendly cool keyline so the white slab still
# reads against a dark sky without a per-mode sprite.
PAPER = (242, 239, 230)        # ~#F2EFE6 warm white body
PAPER_SHADE = (222, 218, 206)  # gentle lower-body shade for a hint of volume
RED = (210,  67,  58)          # ~#D2433A airmail red
BLUE = ( 46,  95, 168)         # ~#2E5FA8 airmail blue
INK = ( 42,  46,  58)          # ~#2A2E3A dark ink / stamp lines
OUTLINE = ( 30,  33,  44)      # dark, high-value: reads on bright day sky
KEYLINE = (221, 230, 240)      # cool rim (~#DDE6F0) — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static airmail slab for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)

    # Slab body. Kept off the surface edges so the gameplay rotozoom never clips
    # the corners; a touch wider than tall for a letter feel.
    BW, BH = 34, 26
    cx, cy = S // 2, S // 2
    rect = pygame.Rect(cx - BW // 2, cy - BH // 2, BW, BH)
    rad = 3

    # Baked outline frame (drawn first, slightly inflated) — the dark silhouette
    # that survives on the (170,220,245) day sky.
    pygame.draw.rect(surf, OUTLINE, rect.inflate(6, 6), border_radius=rad + 2)

    # Paper body: faint top-to-bottom shade for a slab-of-paper feel, not a flat
    # fill. The candy stripe + stamp carry the read, so the body stays quiet.
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        c = (
            int(PAPER[0] + (PAPER_SHADE[0] - PAPER[0]) * t),
            int(PAPER[1] + (PAPER_SHADE[1] - PAPER[1]) * t),
            int(PAPER[2] + (PAPER_SHADE[2] - PAPER[2]) * t),
        )
        body.fill(c + (255,), pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)

    # Faint flap V on top — two ink strokes from the upper corners meeting at the
    # top-centre. Kept thin/low-contrast so it suggests the closed flap without
    # competing with the stripe border.
    apex = (cx, rect.y + BH // 2 - 1)
    pygame.draw.line(surf, INK, (rect.x + 2, rect.y + 2), apex, 1)
    pygame.draw.line(surf, INK, (rect.right - 3, rect.y + 2), apex, 1)

    # The IDENTITY: red+blue dashed candy-stripe perimeter border. A strict
    # red / blue alternation marched clockwise around the inset edge — the one
    # mark that must read before anything else. A single shared phase counter
    # runs continuously across all four sides so dashes don't clump or double-up
    # at the corners (red was piling up top-right otherwise), giving an even
    # candy alternation that survives the smoothscale to 22px and the rotozoom.
    border = rect.inflate(-4, -4)
    seg = 5                       # dash pitch along the run
    colors = (RED, BLUE)
    ci = [0]

    def _march(start, end):
        x0, y0 = start
        x1, y1 = end
        dx, dy = x1 - x0, y1 - y0
        length = max(abs(dx), abs(dy))
        steps = max(1, round(length / seg))
        ux, uy = dx / steps, dy / steps
        for k in range(steps):
            col = colors[ci[0] % 2]
            ci[0] += 1
            # Tiny paper gap between dashes keeps red and blue from bleeding into
            # one purple smear once smoothscaled.
            a = (x0 + ux * k, y0 + uy * k)
            b = (x0 + ux * (k + 1) - ux * 0.18, y0 + uy * (k + 1) - uy * 0.18)
            pygame.draw.line(surf, col, a, b, 3)

    tl = (border.x, border.y)
    tr = (border.right, border.y)
    brc = (border.right, border.bottom)
    bl = (border.x, border.bottom)
    _march(tl, tr)
    _march(tr, brc)
    _march(brc, bl)
    _march(bl, tl)

    # Small red postage stamp, top-right corner — a saturated block with a thin
    # ink edge so it reads as a stamp, not a smudge, even at true size. A 1px
    # paper halo lifts it clear of the candy border so the two don't merge into
    # a red corner clump.
    st = pygame.Rect(rect.right - 11, rect.y + 4, 7, 8)
    pygame.draw.rect(surf, PAPER, st.inflate(2, 2))
    pygame.draw.rect(surf, RED, st)
    pygame.draw.rect(surf, INK, st, 1)
    # Tiny ink tick inside = a postmark hint, the one detail that survives.
    pygame.draw.line(surf, INK, (st.x + 1, st.centery),
                     (st.right - 2, st.centery), 1)

    # Blue "PAR AVION" label bar, lower-left — a solid blue bar (legible block
    # over micro-text) with a lighter centre line standing in for the wording.
    lb = pygame.Rect(rect.x + 4, rect.bottom - 9, 14, 5)
    pygame.draw.rect(surf, BLUE, lb)
    pygame.draw.line(surf, PAPER, (lb.x + 1, lb.centery),
                     (lb.right - 2, lb.centery), 1)

    # Warm/cool keyline rim INSIDE the outline — a glowing edge on night sky that
    # stays subtle on day, so the slab reads on both skies from one sprite. Drawn
    # last so it sits cleanly above the body but under nothing that matters.
    pygame.draw.rect(surf, KEYLINE, rect, width=1, border_radius=rad)

    return pygame.transform.smoothscale(surf, (22, 22))
