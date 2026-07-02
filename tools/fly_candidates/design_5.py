"""POP FLY (Design 5) — retro pop-art housefly, SCRATCH candidate.

Late-game showpiece styled like a panel torn from a Lichtenstein canvas:
flat primary colour blocks, fat comic ink lines on every element, and
Ben-Day halftone dot fills. The read at 40px is carried entirely by the
heavy black outline + the two enormous dotted compound eyes.

Exploration only — wrapped by the local `_make_prebuilt_skin` and NOT
registered in any production BUILDERS map.
"""
import pygame

from game.animal_skins import (
    _make_prebuilt_skin, _new, BCX, BCY, HCX, HCY,
)
from game.parrot import _aaellipse


# ── pop-art palette ──────────────────────────────────────────────────────────
INK      = (17, 17, 17)             # #111111 comic ink
THORAX   = (229, 32, 43)            # #E5202B flat red thorax
THORAX_D = (204, 26, 34)            # #CC1A22 Ben-Day shadow dots
ABDOMEN  = (255, 194, 30)           # #FFC21E flat yellow abdomen
BLUE     = (46, 91, 255)            # #2E5BFF Ben-Day eye dots
EYEW     = (234, 246, 255)          # #EAF6FF cyan-white dome / wing sheen
WHITE    = (255, 255, 255)
WINGDOT  = (255, 176, 184)          # #FFB0B8 Ben-Day wing dots
LABELLUM = (255, 143, 176)          # #FF8FB0 sponge mouth pad


def _ink_outline(layer, thickness=2, color=INK):
    """Grow a bold black comic outline around a layer's silhouette.

    The whole sprite gets a thin house outline later; this is the FAT ink
    line the pop-art look lives on — applied per element so every block
    reads as its own inked shape even at 40px."""
    w, h = layer.get_size()
    mask = pygame.mask.from_surface(layer, threshold=8)
    sil = mask.to_surface(setcolor=(*color, 255), unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    r = thickness
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                out.blit(sil, (dx, dy))
    out.blit(layer, (0, 0))
    return out


def _benday(target, region_pts_or_mask, color, spacing=4, radius=1, phase=0):
    """Overlay a regular Ben-Day halftone dot grid clipped to a region.

    `region` is either a list of polygon points or a pre-drawn white mask
    surface. Odd rows are half-offset so the grid reads as a proper
    hex-packed halftone, not a plain lattice."""
    w, h = target.get_size()
    if isinstance(region_pts_or_mask, pygame.Surface):
        mask = region_pts_or_mask
    else:
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255), region_pts_or_mask)
    dots = pygame.Surface((w, h), pygame.SRCALPHA)
    row = 0
    y = phase
    while y < h:
        x0 = (spacing // 2) if (row % 2) else 0
        x = x0 + phase
        while x < w:
            pygame.draw.circle(dots, color, (x, y), radius)
            x += spacing
        y += spacing
        row += 1
    dots.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    target.blit(dots, (0, 0))


# ── wide dotted comic wings ──────────────────────────────────────────────────
def _wing_surface():
    """A rounded pop-art wing pointing up-right: white membrane, full red
    Ben-Day dot field, two bold black veins, then its own fat ink outline."""
    w = pygame.Surface((52, 40), pygame.SRCALPHA)
    pts = [(12, 28), (22, 11), (38, 8), (48, 16), (45, 26), (31, 32), (16, 32)]
    pygame.draw.polygon(w, WHITE, pts)
    # Cool sheen band up the leading edge before the halftone drops in.
    _aaellipse(w, EYEW, (26, 16), 10, 5)
    _benday(w, pts, WINGDOT, spacing=4, radius=1)
    pygame.draw.line(w, INK, (14, 27), (45, 16), 2)
    pygame.draw.line(w, INK, (16, 30), (39, 22), 2)
    return _ink_outline(w, 2)


def _blit_center(surf, layer, center):
    surf.blit(layer, layer.get_rect(center=center).topleft)


# ── the fly ──────────────────────────────────────────────────────────────────
def build_pop_fly(wing_angle_deg):
    surf = _new()
    f = (wing_angle_deg + 40) / 90.0        # 1 = wings up, 0 = wings down

    # Comic speed lines streak off the back on the wing-up beats.
    if f > 0.6:
        for k in range(3):
            y = 20 + k * 6
            pygame.draw.line(surf, INK, (6, y + 2), (13, y), 1)
            pygame.draw.line(surf, INK, (13, y), (20, y - 1), 1)

    # Two wings fan symmetrically behind the body; higher on wing-up frames.
    wing = _wing_surface()
    ang = 6 + f * 30
    right = pygame.transform.rotate(wing, ang)
    left = pygame.transform.rotate(pygame.transform.flip(wing, True, False), -ang)
    lift = int(f * 4)
    _blit_center(surf, right, (44, 20 - lift))
    _blit_center(surf, left, (22, 22 - lift))

    # Thorax bristles: three bold black comic ticks off the shoulder.
    for i, (ex, ey) in enumerate(((24, 27), (26, 26), (28, 26))):
        pygame.draw.line(surf, INK, (28, 33), (ex, ey), 2)

    # ── two-zone inked body ──
    body = _new()
    # Upper thorax (flat red) + lower abdomen (flat yellow), overlapped so
    # the inked silhouette is one bold peanut with a waist divider.
    _aaellipse(body, THORAX, (BCX, 39), 12, 7)
    _aaellipse(body, ABDOMEN, (BCX, 50), 12, 8)
    # Curved Ben-Day shadow field on the underside of the thorax.
    tmask = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    _aaellipse(tmask, (255, 255, 255, 255), (BCX, 40), 12, 6)
    _benday(body, tmask, THORAX_D, spacing=4, radius=1, phase=1)
    # Belly Ben-Day highlight rows read as rounded abdomen banding.
    amask = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    _aaellipse(amask, (255, 255, 255, 255), (BCX + 2, 52), 10, 6)
    _benday(body, amask, (230, 168, 20), spacing=5, radius=1, phase=2)
    # Waist divider between the two colour zones.
    pygame.draw.line(body, INK, (BCX - 11, 45), (BCX + 11, 45), 2)
    surf.blit(_ink_outline(body, 2), (0, 0))

    # Round sponge labellum (mouth pad, not a needle) at the head underside.
    lab = pygame.Rect(0, 0, 10, 8)
    lab.center = (46, 45)
    pygame.draw.ellipse(surf, LABELLUM, lab)
    pygame.draw.ellipse(surf, INK, lab, 2)

    # ── HERO: two big dotted compound eyes ──
    eyes = _new()
    for cx in (38, 50):
        _aaellipse(eyes, EYEW, (cx, HCY - 2), 8, 8)
    emask = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    for cx in (38, 50):
        _aaellipse(emask, (255, 255, 255, 255), (cx, HCY - 2), 8, 8)
    _benday(eyes, emask, BLUE, spacing=3, radius=1)
    inked_eyes = _ink_outline(eyes, 2)
    # Solid white comic glint wedge in each eye's upper-left, over the dots.
    for cx in (38, 50):
        pygame.draw.polygon(inked_eyes, WHITE, [
            (cx - 6, HCY - 6), (cx - 1, HCY - 7), (cx - 4, HCY - 1)])
    # A 2px ink seam so the touching eyes read as two domes, not a blob.
    pygame.draw.line(inked_eyes, INK, (44, HCY - 9), (44, HCY + 4), 2)
    surf.blit(inked_eyes, (0, 0))

    return surf


build = _make_prebuilt_skin(build_pop_fly)
