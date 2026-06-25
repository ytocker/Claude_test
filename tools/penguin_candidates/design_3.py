"""EMPEROR penguin — design_3, WAVE 2 from-scratch redraw.

The regal premium adult: tall and stately, carried by a smooth slate→steel
VERTICAL GRADIENT body (the flat fill can't show it) with a narrow orange→yellow
ear-to-throat melt and a long slender bicolor beak. Reuses the project's gradient
helper (``game.draw.make_gradient_surface``) masked to the body ellipse. Scratch-
only — NOT registered in ``animal_skins.BUILDERS``.
"""
import pygame

from game.animal_skins import (
    _make_prebuilt_skin, _new, _aaellipse, _rot_blit, _eye,
    BCX, BCY, HCX, HCY, CROWN_Y,
)
from game.draw import lerp_color

# ── EMPEROR palette ───────────────────────────────────────────────────────────
_EM_TOP     = (44, 53, 80)          # #2C3550 slate (gradient top)
_EM_BOT     = (90, 106, 134)        # #5A6A86 steel (gradient base)
_EM_DARK    = (28, 34, 55)          # shadow rim
_EM_BELLY   = (244, 246, 251)       # #F4F6FB belly
_EM_BELLY_D = (212, 216, 226)       # belly undershadow
_EM_BELLY_H = (255, 255, 255)       # belly sheen
_EM_RIM     = (174, 198, 224)       # #AEC6E0 pale-blue flipper / chest rim
_EM_ORANGE  = (240, 153, 44)        # #F0992C ear-patch (cooled, regal)
_EM_AMBER   = (250, 188, 80)        # amber mid-melt
_EM_YELLOW  = (255, 214, 106)       # #FFD66A golden throat bib
_EM_YELLOW_U = (228, 168, 64)       # amber bib underline
_EM_CORAL   = (255, 156, 176)       # #FF9CB0 coral lower mandible
_EM_FOOT    = (62, 74, 98)          # cool slate feet


def _grad_ellipse(surf, cx, cy, rx, ry, top, bot):
    """A vertical top→bot gradient clipped to an ellipse — premium body shading
    the flat fill can't do. Builds the gradient straight into an SRCALPHA layer
    (no display needed), masks it with an ellipse alpha, then blits at anchor."""
    w, h = rx * 2, ry * 2
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(h):
        pygame.draw.line(grad, lerp_color(top, bot, i / max(1, h - 1)),
                         (0, i), (w - 1, i))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    _aaellipse(mask, (255, 255, 255, 255), (rx, ry), rx - 1, ry - 1)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (cx - rx, cy - ry))


def _em_flipper(angle_deg):
    """Slate flipper with a pale-blue rim."""
    w = pygame.Surface((34, 42), pygame.SRCALPHA)
    pts = [(18, 9), (26, 16), (21, 34), (14, 30)]
    pygame.draw.polygon(w, _EM_DARK, pts)
    pygame.draw.polygon(w, _EM_TOP, [(18, 11), (24, 17), (19, 30), (15, 27)])
    pygame.draw.line(w, _EM_RIM, (18, 12), (24, 18), 1)
    return pygame.transform.rotate(w, angle_deg * 0.7)


def build_emperor(wing_angle_deg):
    surf = _new()

    # Stubby tail.
    pygame.draw.polygon(surf, _EM_DARK,
                        [(13, BCY + 8), (6, BCY + 14), (18, BCY + 13)])

    # ── Body: TALL upright egg with a slate→steel vertical gradient ──
    _aaellipse(surf, _EM_DARK, (BCX + 1, BCY + 1), 17, 20)     # shadow rim
    _grad_ellipse(surf, BCX, BCY, 16, 19, _EM_TOP, _EM_BOT)    # gradient body
    # Cool chest rim catching light on the upper-left.
    pygame.draw.arc(surf, _EM_RIM, (BCX - 15, BCY - 18, 20, 26), 1.3, 2.9, 2)

    # Far slate flipper.
    _rot_blit(surf, _em_flipper(wing_angle_deg * 0.5 - 16), (BCX + 12, BCY))

    # ── White belly with sheen + undershadow ──
    _aaellipse(surf, _EM_BELLY,   (BCX + 1, BCY + 4), 11, 15)
    _aaellipse(surf, _EM_BELLY_H, (BCX,     BCY - 2),  7,  6)
    _aaellipse(surf, _EM_BELLY_D, (BCX + 1, BCY + 11), 9,  5)

    # Head — smooth, crest-less slate dome.
    _aaellipse(surf, _EM_DARK, (HCX,     HCY + 2), 12, 12)
    _grad_ellipse(surf, HCX - 1, HCY + 1, 11, 11, _EM_TOP, _EM_BOT)

    # ── Narrow vertical ear-to-throat melt down each side of the neck ──
    for sx in (-1, 1):
        ex = HCX + sx * 9
        _aaellipse(surf, _EM_YELLOW, (ex - sx, HCY + 9), 4, 6)   # bib tip
        _aaellipse(surf, _EM_AMBER,  (ex,      HCY + 4), 4, 5)   # mid fade
        _aaellipse(surf, _EM_ORANGE, (ex + sx, HCY - 1), 4, 4)   # ear-patch
    # Golden throat bib + amber underline so the collar separates from belly.
    _aaellipse(surf, _EM_YELLOW,   (HCX, HCY + 11), 9, 5)
    _aaellipse(surf, _EM_YELLOW_U, (HCX, HCY + 14), 8, 2)

    # White face over the melt so the eyes sit on white.
    _aaellipse(surf, _EM_BELLY, (HCX, HCY + 3), 8, 8)

    # Symmetric eyes with glint.
    _eye(surf, HCX - 3, HCY, 4, iris=(20, 22, 34))
    _eye(surf, HCX + 3, HCY, 4, iris=(20, 22, 34))

    # ── Long slender bicolor beak: slate upper, coral lower + highlight ──
    pygame.draw.polygon(surf, _EM_BOT,
                        [(HCX + 2, HCY + 3), (HCX + 14, HCY + 6),
                         (HCX + 2, HCY + 7)])
    pygame.draw.polygon(surf, _EM_CORAL,
                        [(HCX + 2, HCY + 7), (HCX + 14, HCY + 6),
                         (HCX + 2, HCY + 9)])
    pygame.draw.line(surf, _EM_RIM, (HCX + 3, HCY + 4), (HCX + 12, HCY + 6), 1)

    # Near slate flipper.
    _rot_blit(surf, _em_flipper(wing_angle_deg), (BCX - 7, BCY + 1))

    # Cool slate feet, toe split.
    for fx in (27, 38):
        foot = [(fx - 3, BCY + 16), (fx + 4, BCY + 16),
                (fx + 5, BCY + 20), (fx - 4, BCY + 20)]
        pygame.draw.polygon(surf, _EM_FOOT, foot)
        pygame.draw.polygon(surf, _EM_DARK, foot, 1)
        pygame.draw.line(surf, _EM_DARK, (fx + 1, BCY + 20), (fx + 1, BCY + 18), 1)
    return surf


build = _make_prebuilt_skin(build_emperor)
