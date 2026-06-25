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
_EM_TOP     = (34, 42, 68)          # #222A44 deep slate (gradient top, darkened)
_EM_BOT     = (98, 116, 146)        # steel (gradient base, lifted for delta)
_EM_DARK    = (24, 30, 50)          # shadow rim
_EM_BELLY   = (244, 246, 251)       # #F4F6FB belly
_EM_BELLY_D = (212, 216, 226)       # belly undershadow
_EM_BELLY_H = (255, 255, 255)       # belly sheen
_EM_RIM     = (174, 198, 224)       # #AEC6E0 pale-blue flipper / chest rim
_EM_ORANGE  = (240, 153, 44)        # #F0992C ear-patch (cooled, regal)
_EM_AMBER   = (250, 188, 80)        # amber mid-melt
_EM_YELLOW  = (255, 214, 106)       # #FFD66A golden throat bib
_EM_YELLOW_U = (228, 168, 64)       # amber bib underline
_EM_CORAL   = (232, 160, 126)       # #E8A07E muted coral-tan mandible (not pink)
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
    _aaellipse(surf, _EM_DARK, (BCX + 1, BCY + 2), 16, 21)     # shadow rim (taller)
    _grad_ellipse(surf, BCX, BCY + 1, 15, 20, _EM_TOP, _EM_BOT)   # gradient body
    # Faint vertical polish streak down the back-left so "premium" reads at 40px.
    pygame.draw.line(surf, _EM_RIM, (BCX - 9, BCY - 10), (BCX - 10, BCY + 8), 1)
    # Cool chest rim catching light on the upper-left.
    pygame.draw.arc(surf, _EM_RIM, (BCX - 15, BCY - 19, 20, 26), 1.3, 2.9, 2)

    # Far slate flipper.
    _rot_blit(surf, _em_flipper(wing_angle_deg * 0.5 - 16), (BCX + 12, BCY))

    # ── White belly with sheen + undershadow ──
    _aaellipse(surf, _EM_BELLY,   (BCX + 1, BCY + 4), 11, 15)
    _aaellipse(surf, _EM_BELLY_H, (BCX,     BCY - 2),  7,  6)
    _aaellipse(surf, _EM_BELLY_D, (BCX + 1, BCY + 11), 9,  5)

    # Head — neat, smaller crest-less dome (r10) for the stately adult read.
    _aaellipse(surf, _EM_DARK, (HCX,     HCY + 1), 11, 11)
    _grad_ellipse(surf, HCX - 1, HCY, 10, 10, _EM_TOP, _EM_BOT)

    # ── Ear-to-throat melt: ONE clean directional teardrop per side, orange-
    # dense at the ear melting down-forward to yellow, converging into the bib.
    # Symmetric; drawn so the white face only clips the lower (yellow) end. ──
    for sx in (-1, 1):
        ex = HCX + sx * 8
        _aaellipse(surf, _EM_YELLOW, (ex - sx * 2, HCY + 8), 3, 5)   # throat (low/forward)
        _aaellipse(surf, _EM_AMBER,  (ex,          HCY + 3), 4, 5)   # mid
        _aaellipse(surf, _EM_ORANGE, (ex + sx,     HCY - 2), 3, 4)   # ear (high/back)
    # Golden throat bib (convergence) + amber underline vs the white belly.
    _aaellipse(surf, _EM_YELLOW,   (HCX, HCY + 10), 8, 4)
    _aaellipse(surf, _EM_YELLOW_U, (HCX, HCY + 13), 7, 2)

    # White face — smaller (rx7) so it doesn't bite into the orange ear-patches.
    _aaellipse(surf, _EM_BELLY, (HCX, HCY + 3), 7, 7)

    # Symmetric eyes (wider spacing) with a warm catchlight.
    _eye(surf, HCX - 3, HCY, 4, iris=(22, 24, 36))
    _eye(surf, HCX + 4, HCY, 4, iris=(22, 24, 36))

    # ── Long slender NEEDLE beak: slate upper + muted-coral lower, fine tip ──
    pygame.draw.polygon(surf, _EM_BOT,
                        [(HCX + 3, HCY + 4), (HCX + 15, HCY + 6),
                         (HCX + 3, HCY + 6)])
    pygame.draw.polygon(surf, _EM_CORAL,
                        [(HCX + 3, HCY + 6), (HCX + 15, HCY + 6),
                         (HCX + 3, HCY + 8)])
    pygame.draw.line(surf, _EM_RIM, (HCX + 4, HCY + 5), (HCX + 13, HCY + 6), 1)

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
