"""Round 1 review sheet for the `punched-void-cord` owned card-state concept.

The owned/redeemed read is carried subtractively: an intact cream tag with two
bold PUNCHED holes through its lower face (the universal "voided" mark) plus a
gold coin token above them, hung on a SLACK drooping cord. The slack posture is
what separates "done / released" from the taut cord on the price+equipped tags —
so this script replicates the sibling hang-tag geometry but sags the cord.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()
SID = "skin_mummy"


# ── slack cord + punched-void chip ────────────────────────────────────────────
def _slack_cord(surf, g, knot, cord, sag, lw):
    """A sagging two-ply cord from the grommet up to the knot. A parabolic droop
    on the mid-span (peaks at t=0.5) gives the tag a released, weight-hanging
    posture — the opposite of the taut straight cord on the price/equipped tags."""
    n = 7
    strand_a, strand_b = [], []
    for i in range(n + 1):
        t = i / n
        x = g[0] + (knot[0] - g[0]) * t
        y = g[1] + (knot[1] - g[1]) * t
        droop = sag * 4 * t * (1 - t)
        strand_a.append((x - 1, y + droop - 1))
        strand_b.append((x + 2, y + droop + 2))
    pygame.draw.lines(surf, cord, False, strand_a, lw)
    pygame.draw.lines(surf, cord, False, strand_b, lw)


def punched_void_face(face):
    """Subtractive redeemed mark: two bold holes punched clean through the lower
    face (alpha 0), each ringed with a lit-TL / shaded-BR inner bevel so it reads
    as punched through real card stock, plus a gold coin token above/between them."""
    W, H = sc._TAG_W, sc._TAG_H
    hr = sc.m(6)
    holes = [(int(W * 0.35), int(H * 0.62)), (int(W * 0.65), int(H * 0.62))]
    for hx, hy in holes:
        # pygame.draw writes colour+alpha directly on an SRCALPHA surface (no
        # blend), so a (0,0,0,0) disc cuts a true transparent hole — same trick
        # the tag grommet uses.
        pygame.draw.circle(face, (0, 0, 0, 0), (hx, hy), hr)
        box = (hx - hr, hy - hr, hr * 2, hr * 2)
        pygame.draw.arc(face, (255, 248, 224), box,
                        math.radians(108), math.radians(192), max(1, sc.m(1.4)))
        pygame.draw.arc(face, (110, 80, 30), box,
                        math.radians(288), math.radians(372), max(1, sc.m(1.4)))
    cr = sc.m(8)
    cx0, cy0 = W // 2, int(H * 0.40)
    pygame.draw.circle(face, (110, 80, 30), (cx0, cy0), cr + 1)
    pygame.draw.circle(face, (236, 202, 116), (cx0, cy0), cr)
    pygame.draw.circle(face, (255, 248, 224), (cx0 - sc.m(2), cy0 - sc.m(2)), cr // 2)
    pygame.draw.circle(face, (110, 80, 30), (cx0, cy0), cr, width=max(1, sc.m(1)))


def punched_void_chip(surf, cx, cy, h):
    """Owned/redeemed hang-tag: the shared cream tag geometry, but with the
    punched-void face and a SLACK cord instead of the taut price/equipped cord."""
    rad = sc.m(3)
    grommet = (30, 13)

    face = pygame.Surface((sc._TAG_W, sc._TAG_H), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, sc._TAG_W, sc._TAG_H)
    body = sc.vgrad_stops(sc._TAG_W, sc._TAG_H, rad,
                          [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                          255, gamma=1.04)
    face.blit(body, (0, 0))
    sc.bevel_rim(face, brect, rad, (80, 52, 12, 200),
                 (255, 240, 190, 200), w=max(1, sc.m(1.2)))

    punched_void_face(face)

    pygame.draw.circle(face, (0, 0, 0, 0), grommet, sc.m(5))
    pygame.draw.circle(face, (110, 80, 30), grommet, sc.m(5) + 1, width=max(1, sc.m(1)))

    rot = pygame.transform.rotate(face, sc._TAG_TILT)
    cord = (190, 165, 115)
    tag_center = (44, 60)
    knot = (22, 13)
    gx, gy = sc._tag_rot_point(*grommet, tag_center)
    _slack_cord(surf, (gx, gy), knot, cord, sag=sc.m(5), lw=sc.m(1.5))
    surf.blit(rot, rot.get_rect(center=tag_center))
    pygame.draw.circle(surf, cord, knot, sc.m(1.5))
    pygame.draw.circle(surf, (min(cord[0] + 30, 255), min(cord[1] + 30, 255),
                              min(cord[2] + 30, 255)), knot, max(1, sc.m(0.6)))


# ── review sheet ──────────────────────────────────────────────────────────────
CARD_W, CARD_H = sc.CARD_W, sc.CARD_H
big_size = (CARD_W * sc.SS, CARD_H * sc.SS)
rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                   CARD_W * sc.SS - 2 * sc.m(sc._INSET),
                   CARD_H * sc.SS - 2 * sc.m(sc._INSET))


def new_big():
    return pygame.Surface(big_size, pygame.SRCALPHA)


p0 = new_big()
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

p1 = new_big()
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

p2 = new_big()
_orig_state_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc.draw_card(p2, SID, rect, equipped=False, secret=False, owned=False)
sc.state_chip = _orig_state_chip
punched_void_chip(p2, 0, 0, sc.m(20))

# compose
BG = (8, 8, 20)
xs = [20, 360, 700]
panel_y = 102
W, H = 1060, 560
sheet = pygame.Surface((W, H))
sheet.fill(BG)

title_f = hud_font(20, True)
lbl_f = hud_font(15, True)


def label(txt, cx, y, col=(236, 230, 210)):
    img = lbl_f.render(txt, True, col)
    sheet.blit(img, img.get_rect(center=(cx, y)))


sheet.blit(title_f.render("store_owned_v1 — punched-void-cord — round 1", True,
                          (244, 226, 170)), (20, 22))
sheet.blit(lbl_f.render("2 punched holes + gold coin token on a slack drooping cord "
                        "(subtractive 'voided/redeemed' mark; no dark check)",
                        True, (150, 160, 190)), (20, 52))

panels = [
    (p0, "UNOWNED (price tag)"),
    (p1, "EQUIPPED base"),
    (p2, "CONCEPT: punched-void-cord"),
]
for (surf_big, name), x in zip(panels, xs):
    disp = pygame.transform.smoothscale(surf_big, (CARD_W, CARD_H))
    sheet.blit(disp, (x, panel_y))
    label(name, x + CARD_W // 2, panel_y - 12)

# zoom of the concept below panel 2
zoom_src = pygame.transform.smoothscale(p2, (CARD_W, CARD_H))
zoom = pygame.transform.scale2x(zoom_src)
zy = panel_y + CARD_H + 34
sheet.blit(zoom, (xs[2], zy))
label("2x zoom — punched-void detail", xs[2] + zoom.get_width() // 2, zy - 12)

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_owned_v1", "punched_void_cord", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
