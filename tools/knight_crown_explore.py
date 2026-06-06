"""Round-2 exploration sheet: the LEAD HYBRID crown (CORONET silhouette ×
CIRCLET metal) for the knight+3x combo, plus two tight tunings of that one
idea — NOT five new types.

The art-director picked #1 CORONET refined toward a CORONET×CIRCLET hybrid:
three fat triangular points on a thick, rounder-bevelled warm-gold band with a
single centred ruby, seated low/back so the crimson plume rises behind it.
This round shows that hybrid in slot 1 and varies only point height and the
gem socket (ruby vs. a tiny green-$).

Each crown is drawn procedurally and composited onto the REAL knight frame
(parrot.get_knight_parrot) so we judge it at gameplay scale. Headless/dummy
SDL so it runs in CI and on any target. Output: docs/knight_crown/round_2.png.
"""
import math
import os
import pathlib

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import parrot
from game.knight_skin import BRASS, BRASS_HI

# ── crown palette — a half-step warmer/brighter than the helm brass ──────────
# The helm trim is BRASS/BRASS_HI. The crown is the same gold-on-steel family
# but pushed a notch richer/royal so it reads as a crown, not just more trim:
# the mid is warmer and lighter than BRASS, the highlight a touch hotter than
# BRASS_HI. Deep seat below for the rounded bevel's shadow side.
G_DK = (150, 112, 44)            # bevel shadow / band underside
G_MID = (224, 184, 96)           # warm royal gold core (> BRASS 208,174,98)
G_HI = (255, 238, 176)           # rim light (> BRASS_HI 255,232,168)
G_GLINT = (255, 250, 224)        # hottest specular pip
G_SEAT = (96, 68, 26)            # contact shadow where the band meets the dome
RUBY = (198, 40, 56); RUBY_DK = (120, 18, 30); RUBY_HI = (255, 158, 168)
# The $-socket option: green tied to the 3x/wealth read (kept OUT of slot 1 so
# the colourblind-safe ruby stays the lead).
DOL = (74, 196, 116); DOL_DK = (24, 96, 56); DOL_HI = (188, 250, 210)


def _ruby_gem(surf, cx, cy, r):
    """Faceted ruby set into the band face: dark bezel, body, upper-left glint
    + a single white spark. Light from upper-left to match the helm."""
    pygame.draw.circle(surf, RUBY_DK, (cx, cy), r + 1)
    pygame.draw.circle(surf, RUBY, (cx, cy), r)
    pygame.draw.circle(surf, RUBY_HI, (cx - max(1, r // 3), cy - max(1, r // 3)), max(1, r // 2))
    surf.set_at((cx - r // 3, cy - r // 3), (255, 255, 255))


def _dollar_gem(surf, cx, cy, r):
    """Same socket as the ruby but a tiny green '$' coin: green disc, dark
    bezel, a crisp light-green stroke. The alternate 'wealth' read."""
    pygame.draw.circle(surf, DOL_DK, (cx, cy), r + 1)
    pygame.draw.circle(surf, DOL, (cx, cy), r)
    # vertical bar + two short serif tails reads as '$' even at 2-3px radius
    pygame.draw.line(surf, DOL_HI, (cx, cy - r), (cx, cy + r), 1)
    surf.set_at((cx - 1, cy - r + 1), DOL_HI)
    surf.set_at((cx + 1, cy + r - 1), DOL_HI)
    surf.set_at((cx, cy), DOL_HI)


def _band(surf, x0, x1, y, h):
    """Thick coronet band with CIRCLET-grade rounded bevel: a dark contact
    seat under the dome, a warm gold core, then a bright rim-light arc along
    the upper-left edge so the band reads as a rounded armour ring, not a flat
    painted strip. Band is ~1.3x the round-1 height (h>=6)."""
    w = x1 - x0
    # contact shadow where gold meets the steel dome
    pygame.draw.rect(surf, G_SEAT, (x0, y + h - 1, w, 2))
    # dark bevel underside (the part curving away from the light)
    pygame.draw.rect(surf, G_DK, (x0, y, w, h))
    # warm gold core inset from the underside so G_DK shows as a lower bevel
    pygame.draw.rect(surf, G_MID, (x0 + 1, y + 1, w - 2, h - 2))
    # rounded rim-light hugging ONLY the upper edge (upper-left brightest) — a
    # short arc whose ellipse extends well below the band so just its top crown
    # is drawn, giving a curved rather than flat-painted highlight.
    pygame.draw.arc(surf, G_HI, (x0, y, w, h * 4), math.radians(40), math.radians(140), 1)
    pygame.draw.line(surf, G_HI, (x0 + 1, y + 1), (x0 + w // 2, y + 1), 1)
    surf.set_at((x0 + 2, y + 1), G_GLINT)


def _fat_point(surf, cx, base_y, top_y, half):
    """A fat, clearly triangular gold point (base width = 2*half, kept >=3px).
    Dark bevel body + warm core + an upper-left lit edge so the points read as
    the same rounded metal as the band. No thin spikes."""
    # dark full triangle (bevel/shadow)
    pygame.draw.polygon(surf, G_DK, [(cx - half, base_y), (cx + half, base_y), (cx, top_y)])
    # warm core, inset on the right/underside so the dark shows as edge bevel
    pygame.draw.polygon(surf, G_MID, [(cx - half + 1, base_y - 1), (cx + half - 1, base_y - 1), (cx, top_y + 2)])
    # lit upper-left face + a glint at the tip
    pygame.draw.line(surf, G_HI, (cx - half + 1, base_y - 1), (cx, top_y + 1), 1)
    surf.set_at((cx, top_y + 1), G_GLINT)


def _coronet(surf, cx, cy, point_dh=0, gem="ruby"):
    """LEAD HYBRID: thick warm-gold band + three fat triangular points (centre
    tallest), one centred gem in the band face. `point_dh` nudges point height
    (-1/0/+1 native px); `gem` is 'ruby' or 'dollar'."""
    half = 11
    h = 6                       # ~1.3x the round-1 band (was 5, mostly 4)
    by = cy
    _band(surf, cx - half, cx + half, by, h)
    # three fat points: outer pair shorter, centre tallest, all base>=3px
    ch = 9 + point_dh           # centre point height above the band top
    sh = 6 + point_dh           # side point height
    for dx, ph, hw in ((-7, sh, 2), (0, ch, 2), (7, sh, 2)):
        _fat_point(surf, cx + dx, by + 1, by - ph, hw)
    # gem seated in the band face, centred over the brow
    if gem == "ruby":
        _ruby_gem(surf, cx, by + h // 2 + 1, 2)
    else:
        _dollar_gem(surf, cx, by + h // 2 + 1, 2)


# ── the three round-2 tunings (one idea, tight variations) ───────────────────
def draw_a(surf, cx, cy):
    """A — LEAD HYBRID, baseline: centre point 9px, ruby socket."""
    _coronet(surf, cx, cy, point_dh=0, gem="ruby")


def draw_b(surf, cx, cy):
    """B — points +1px taller (more regal silhouette), ruby socket."""
    _coronet(surf, cx, cy, point_dh=1, gem="ruby")


def draw_c(surf, cx, cy):
    """C — baseline points, green-$ socket instead of the ruby (wealth read)."""
    _coronet(surf, cx, cy, point_dh=0, gem="dollar")


CANDIDATES = [
    ("A  HYBRID · ruby",        draw_a),
    ("B  +1px points · ruby",   draw_b),
    ("C  $-socket",             draw_c),
]


# ── helm-crown anchor on the real knight frame ───────────────────────────────
# Knight char surface is (SPRITE_W+2*PAD, SPRITE_H+2*PAD). The armet helm is
# blitted at _P(nom,0.73,0.17) at size (nom.w*0.5, nom.h*0.54). Round 1 seated
# the band at HELM_TOP+5; the director asked to drop ~2px LOWER and slightly
# BACK onto the dome so the plume clears behind the crown.
PAD = 16
NOM_X = PAD; NOM_Y = PAD
HELM_CX = NOM_X + 0.73 * parrot.SPRITE_W
HELM_TOP = NOM_Y + 0.17 * parrot.SPRITE_H - 0.54 * parrot.SPRITE_H * 0.5
CROWN_CX = int(HELM_CX) - 1        # ~1px back toward the dome crest
CROWN_CY = int(HELM_TOP + 7)       # ~2px lower than round 1 (was +5)


def _knight_with_crown(crown_fn):
    """Real knight frame 0 (flat tilt) with the candidate crown drawn on the
    helm dome. Returns the full char surface."""
    base = parrot.get_knight_parrot(0, 0.0)
    surf = base.copy()
    crown_fn(surf, CROWN_CX, CROWN_CY)
    return surf


def main():
    pygame.font.init()
    label_font = pygame.font.SysFont("dejavusans", 14, bold=True)
    sub_font = pygame.font.SysFont("dejavusans", 10)

    BG = (38, 44, 58)
    PANEL = (28, 33, 44)
    INK = (232, 238, 250)
    DIM = (150, 160, 180)

    cols = 3
    cell_w = 250
    cell_h = 500
    head_h = 60
    sheet = pygame.Surface((cols * cell_w, head_h + cell_h), pygame.SRCALPHA)
    sheet.fill(BG)

    title = pygame.font.SysFont("dejavusans", 22, bold=True).render(
        "Knight + 3x  —  METALLIC CROWN  ·  round 2  (CORONET x CIRCLET hybrid)", True, INK)
    sheet.blit(title, (16, 12))
    subtitle = sub_font.render(
        "lead hybrid + tight tunings  ·  real knight armet helm  ·  top = ~2x play scale  ·  bottom = 5x detail",
        True, DIM)
    sheet.blit(subtitle, (18, 40))

    for i, (name, fn) in enumerate(CANDIDATES):
        x0 = i * cell_w
        panel = pygame.Rect(x0 + 8, head_h + 6, cell_w - 16, cell_h - 12)
        pygame.draw.rect(sheet, PANEL, panel, border_radius=8)
        pygame.draw.rect(sheet, (60, 70, 90), panel, width=1, border_radius=8)

        lab = label_font.render(name, True, (255, 226, 150))
        sheet.blit(lab, (panel.x + 12, panel.y + 8))

        composed = _knight_with_crown(fn)

        # ~2x play-scale tile (no smoothing — show the real native read)
        s2 = pygame.transform.scale(
            composed, (composed.get_width() * 2, composed.get_height() * 2))
        sheet.blit(s2, (panel.centerx - s2.get_width() // 2, panel.y + 32))

        cap = sub_font.render("~2x play scale", True, DIM)
        sheet.blit(cap, (panel.centerx - s2.get_width() // 2, panel.y + 32 + s2.get_height() + 2))

        # 5x detail crop — zoom the head/helm region only
        crop = pygame.Rect(int(CROWN_CX - 27), int(CROWN_CY - 16), 52, 54)
        crop = crop.clamp(composed.get_rect())
        head = composed.subsurface(crop).copy()
        s5 = pygame.transform.scale(head, (head.get_width() * 5, head.get_height() * 5))
        sub_x = panel.centerx - s5.get_width() // 2
        sub_y = panel.y + 32 + s2.get_height() + 24
        pygame.draw.rect(sheet, (20, 24, 32), (sub_x - 2, sub_y - 2, s5.get_width() + 4, s5.get_height() + 4))
        sheet.blit(s5, (sub_x, sub_y))
        cap2 = sub_font.render("5x detail", True, DIM)
        sheet.blit(cap2, (sub_x, sub_y + s5.get_height() + 2))

    out_dir = pathlib.Path("/home/user/skybit/docs/knight_crown")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "round_2.png"
    pygame.image.save(sheet, str(out))
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
