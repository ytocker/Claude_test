"""NERD SPECS — round-1 exploration: three distinct bookish-glasses takes.

All three honour the side-profile contract: near/front lens toward the beak
(+facing), temple arm toward the ear (-facing), everything proportional to
``eye_w`` so it reads at product size (eye_w~96) AND in-game (eye_w=22).

The whole point of "nerd specs" is CLEAR lenses — the eye + its glint must
show through — so every variant keeps the glass to a faint wash and lets the
bare macaw eye carry the read, with the frame doing the dorky/smart talking.

  A · TAPED ROUND   — thick black round rims + the classic tape-wrapped bridge.
  B · HORN-RIM      — thick rounded-rect tortoiseshell horn-rims (chunky geek).
  C · WIRE PROF     — thin gold wire perfect-rounds (academic professor).

`draw_nerd_taped` is the implemented pick (copied into draw.py).
"""
import pygame


# ── shared faint-glass helper ────────────────────────────────────────────────
# A nerd lens is CLEAR. We lay only a whisper of cool tint + a diagonal sheen
# band so the glass reads as glass, never as a dark sunglass lens. The eye
# beneath stays fully visible.

def _clear_lens(surf, rect, tint, sheen=(255, 255, 255), clip="ellipse"):
    """Paint a faint clear lens into `rect`. `tint` is RGBA (low alpha).
    A bright diagonal sheen band sells 'glass' without hiding the eye."""
    w, h = rect.w, rect.h
    if w < 2 or h < 2:
        return
    glass = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(glass, tint, (0, 0, w, h))
    # Diagonal sheen wedge across the upper-left of the lens.
    band = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(band, (*sheen, 70),
                        [(0, h * 0.15), (w * 0.5, 0), (w * 0.72, 0),
                         (0, h * 0.62)])
    # Clip the sheen to the lens shape so it doesn't spill past the rim.
    clipper = pygame.Surface((w, h), pygame.SRCALPHA)
    if clip == "rect":
        pygame.draw.rect(clipper, (255, 255, 255, 255), (0, 0, w, h),
                         border_radius=max(2, h // 4))
    else:
        pygame.draw.ellipse(clipper, (255, 255, 255, 255), (0, 0, w, h))
    band.blit(clipper, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    glass.blit(band, (0, 0))
    if clip == "rect":
        # Re-clip the tint to the rounded-rect too.
        glass.blit(clipper, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(glass, rect.topleft)


# ─────────────────────────────────────────────────────────────────────────────
# A · TAPED ROUND (the pick) — thick BLACK round rims, a faint clear lens, and
#     the hero geek detail: a wad of off-white tape wrapped around the bridge.
#     Round + thick + tape is the most-instant "nerd" read and survives 22px.
# ─────────────────────────────────────────────────────────────────────────────
_TR_RIM    = (28, 28, 34)          # near-black thick rim
_TR_RIM_H  = (96, 100, 116)        # cool top-arc gleam so the black isn't dead
_TR_TINT   = (208, 226, 236, 46)   # barely-there glass
_TR_TAPE   = (236, 232, 214)       # grubby off-white sticking-plaster tape
_TR_TAPE_D = (196, 188, 158)
_TR_GLINT  = (255, 255, 255)


def draw_nerd_taped(surf, cx, cy, eye_w, facing=1):
    f = facing
    r   = max(3, int(eye_w * 0.32))            # round-lens radius
    sep = max(4, int(eye_w * 0.50))            # centre-to-centre spacing
    rim = max(2, int(eye_w * 0.085))           # THICK rim — the geek read

    near = (cx + f * (sep // 2), cy)
    far  = (cx - f * (sep // 2), cy)

    # Faint clear lenses first so the thick rim stamps crisply over them.
    for (lx, ly) in (near, far):
        _clear_lens(surf, pygame.Rect(lx - r, ly - r, r * 2, r * 2), _TR_TINT)

    # Thick black round rims.
    for (lx, ly) in (near, far):
        pygame.draw.circle(surf, _TR_RIM, (lx, ly), r, rim)
    # A cool top-arc gleam on each rim so the black lifts off a dark sky.
    for (lx, ly) in (near, far):
        pygame.draw.arc(surf, _TR_RIM_H, (lx - r, ly - r, r * 2, r * 2),
                        0.6, 2.2, max(1, rim - 1))

    # Temple arm hinged off the far rim, sweeping back to the ear.
    hinge = (far[0] - f * (r - rim // 2), cy - max(1, int(eye_w * 0.02)))
    ear   = (far[0] - f * (r + max(3, int(eye_w * 0.36))),
             cy - max(1, int(eye_w * 0.07)))
    pygame.draw.line(surf, _TR_RIM, hinge, ear, rim)
    pygame.draw.circle(surf, _TR_RIM, hinge, max(1, rim // 2 + 1))  # hinge stud

    # Bridge between the rims — short straight bar at mid-height.
    bx0 = far[0] + f * r
    bx1 = near[0] - f * r
    by = cy - max(1, int(eye_w * 0.04))
    pygame.draw.line(surf, _TR_RIM, (bx0, by), (bx1, by), rim)

    # HERO: a wad of grubby tape wrapped around the bridge — the nerd signature.
    tw = max(2, int(eye_w * 0.10))             # tape half-width
    th = max(2, int(eye_w * 0.16))             # tape height
    bmid = ((bx0 + bx1) // 2, by)
    tape = pygame.Rect(bmid[0] - tw, bmid[1] - th // 2, tw * 2, th)
    pygame.draw.rect(surf, _TR_TAPE_D, tape, border_radius=max(1, tw // 2))
    pygame.draw.rect(surf, _TR_TAPE, tape.inflate(-2, -2),
                     border_radius=max(1, tw // 2))
    # Two horizontal wrap-creases so it reads as wound tape, not a white block.
    for k in (-1, 1):
        yy = bmid[1] + k * max(1, th // 4)
        pygame.draw.line(surf, _TR_TAPE_D, (tape.left + 1, yy),
                         (tape.right - 1, yy), 1)

    # Pinpoint glints sell the clear glass over the visible eye.
    pygame.draw.circle(surf, _TR_GLINT,
                       (near[0] - f * (r // 2), cy - r // 2),
                       max(1, int(eye_w * 0.05)))
    pygame.draw.circle(surf, _TR_GLINT,
                       (far[0] - f * (r // 3), cy - r // 2),
                       max(1, int(eye_w * 0.04)))


# ─────────────────────────────────────────────────────────────────────────────
# B · HORN-RIM — chunky rounded-rectangle tortoiseshell horn-rims. The thick
#     amber-brown plastic + the squarish lens is the studious "intellectual"
#     read; clear lens keeps the eye visible. Heavier brow bar than the rims.
# ─────────────────────────────────────────────────────────────────────────────
_HR_RIM    = (74, 46, 26)          # tortoiseshell amber-brown
_HR_RIM_D  = (44, 26, 14)
_HR_RIM_H  = (150, 104, 60)        # warm plastic gleam
_HR_TINT   = (214, 222, 230, 44)
_HR_GLINT  = (255, 255, 255)


def draw_nerd_horn(surf, cx, cy, eye_w, facing=1):
    f = facing
    lw  = max(4, int(eye_w * 0.40))            # lens width
    lh  = max(4, int(eye_w * 0.34))            # lens height (slightly squat)
    gap = max(2, int(eye_w * 0.07))            # bridge gap between lenses
    rim = max(2, int(eye_w * 0.075))
    rad = max(2, int(eye_w * 0.09))            # rounded corner

    # Near rect sits toward the beak, far rect toward the ear.
    near = pygame.Rect(0, 0, lw, lh)
    far  = pygame.Rect(0, 0, lw, lh)
    near.center = (cx + f * (lw // 2 + gap // 2), cy)
    far.center  = (cx - f * (lw // 2 + gap // 2), cy)

    # Faint clear glass in each lens.
    for rc in (near, far):
        _clear_lens(surf, rc, _HR_TINT, clip="rect")

    # Chunky rims with a darker outer shadow line for plastic depth.
    for rc in (near, far):
        pygame.draw.rect(surf, _HR_RIM_D, rc.inflate(2, 2),
                         rim + 1, border_radius=rad)
        pygame.draw.rect(surf, _HR_RIM, rc, rim, border_radius=rad)
    # Heavier brow bar across the TOP of each lens (horn-rim signature).
    for rc in (near, far):
        pygame.draw.line(surf, _HR_RIM, (rc.left, rc.top + rim // 2),
                         (rc.right, rc.top + rim // 2), rim + 1)
        pygame.draw.line(surf, _HR_RIM_H, (rc.left + rad, rc.top + 1),
                         (rc.right - rad, rc.top + 1), 1)

    # Short thick bridge linking the two brow bars at the inner edges.
    in_near = near.left if f > 0 else near.right
    in_far  = far.right if f > 0 else far.left
    pygame.draw.line(surf, _HR_RIM, (in_near, near.top + rim),
                     (in_far, far.top + rim), rim + 1)

    # Temple arm off the far lens toward the ear.
    pygame.draw.line(surf, _HR_RIM,
                     (far.left if f > 0 else far.right, cy - lh // 4),
                     (far.centerx - f * (lw // 2 + max(3, int(eye_w * 0.34))),
                      cy - max(1, int(eye_w * 0.08))),
                     rim)

    pygame.draw.circle(surf, _HR_GLINT,
                       (near.centerx - f * (lw // 4), near.top + lh // 4),
                       max(1, int(eye_w * 0.05)))
    pygame.draw.circle(surf, _HR_GLINT,
                       (far.centerx - f * (lw // 4), far.top + lh // 4),
                       max(1, int(eye_w * 0.04)))


# ─────────────────────────────────────────────────────────────────────────────
# C · WIRE PROF — thin GOLD wire perfect-rounds, the academic-professor read.
#     Almost-invisible glass + a faint gold rim. Daintier than the taped pair;
#     leans "smart/scholarly" rather than "dorky". A tiny nose-pad arm sells it.
# ─────────────────────────────────────────────────────────────────────────────
_WP_WIRE   = (206, 166, 70)        # warm gold wire
_WP_WIRE_H = (255, 232, 150)
_WP_TINT   = (220, 230, 236, 38)
_WP_GLINT  = (255, 255, 255)


def draw_nerd_wire(surf, cx, cy, eye_w, facing=1):
    f = facing
    r   = max(3, int(eye_w * 0.30))
    sep = max(4, int(eye_w * 0.48))
    rim = max(1, int(eye_w * 0.045))           # THIN wire

    near = (cx + f * (sep // 2), cy)
    far  = (cx - f * (sep // 2), cy)

    for (lx, ly) in (near, far):
        _clear_lens(surf, pygame.Rect(lx - r, ly - r, r * 2, r * 2), _WP_TINT)

    # Thin gold rims + a bright top-arc so the wire reads as metal.
    for (lx, ly) in (near, far):
        pygame.draw.circle(surf, _WP_WIRE, (lx, ly), r, rim)
        pygame.draw.arc(surf, _WP_WIRE_H, (lx - r, ly - r, r * 2, r * 2),
                        0.5, 2.3, rim)

    # Keyhole bridge — a little upward hop between the rims (round-spec idiom).
    bx0 = far[0] + f * r
    bx1 = near[0] - f * r
    midx = (bx0 + bx1) // 2
    top = cy - r - max(1, int(eye_w * 0.04))
    pygame.draw.lines(surf, _WP_WIRE, False,
                      [(bx0, cy - r // 3), (midx, top), (bx1, cy - r // 3)], rim)

    # Thin temple arm to the ear.
    pygame.draw.line(surf, _WP_WIRE, (far[0] - f * r, cy),
                     (far[0] - f * (r + max(3, int(eye_w * 0.34))),
                      cy - max(1, int(eye_w * 0.06))), rim)

    # Tiny nose-pad stub on the near rim — the dainty scholarly tell.
    pygame.draw.line(surf, _WP_WIRE, (near[0] - f * r, cy + r // 3),
                     (near[0] - f * (r + max(1, int(eye_w * 0.04))),
                      cy + r // 2), max(1, rim))

    pygame.draw.circle(surf, _WP_GLINT,
                       (near[0] - f * (r // 2), cy - r // 2),
                       max(1, int(eye_w * 0.05)))
    pygame.draw.circle(surf, _WP_GLINT,
                       (far[0] - f * (r // 2), cy - r // 2),
                       max(1, int(eye_w * 0.04)))


VARIANTS = [
    ("A · TAPED ROUND (pick)", draw_nerd_taped),
    ("B · HORN-RIM",           draw_nerd_horn),
    ("C · WIRE PROF",          draw_nerd_wire),
]
