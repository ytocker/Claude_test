"""Round-1 review render for the gold-seal-medallion owned-card state.

A fully intact cream hang-tag whose hero is a bold gold embossed medallion
struck across the lower face — a wax-seal read in the gold/cream palette, NOT
the dark equipped tick. Headless (SDL dummy) so it renders identically to the
offline build tooling on either target.
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


def gold_seal_face(face):
    """Strike a fat gold wax-seal medallion across the lower tag face. Warm
    additive glow + scalloped rim + embossed disc + sunburst boss so at ~40px
    final it reads as premium struck gold, not a flat sticker."""
    m = sc.m
    cx = sc._TAG_W // 2
    cy = int(sc._TAG_H * 0.55)

    disc_r = m(11)
    rim_r = m(13)

    # warm underglow so the seal reads additive/glowing against the cream.
    sc.soft_glow(face, cx, cy, rim_r + m(3), (255, 224, 150), 44, layers=8)

    # scalloped wax edge: overlapping bumps ringed around the disc.
    n_scallop = 10
    for i in range(n_scallop):
        a = 2 * math.pi * i / n_scallop
        sx = cx + rim_r * math.cos(a)
        sy = cy + rim_r * math.sin(a)
        pygame.draw.circle(face, (236, 202, 116), (int(round(sx)), int(round(sy))), m(5))

    # main disc — radial gradient bright centre -> deeper gold rim for volume.
    for i in range(disc_r, 0, -1):
        t = (i / disc_r) ** 1.15
        col = sc.lerp_color((248, 224, 150), (214, 176, 96), t)
        pygame.draw.circle(face, col, (cx, cy), i)

    # emboss: lit top-left arc + shaded bottom-right arc give the struck relief.
    er = disc_r - m(1)
    box = (cx - er, cy - er, er * 2, er * 2)
    pygame.draw.arc(face, (255, 248, 210), box,
                    math.radians(70), math.radians(210), max(2, m(1.4)))
    pygame.draw.arc(face, (110, 80, 30), box,
                    math.radians(250), math.radians(390), max(2, m(1.4)))

    # raised sunburst boss — an 8-spike star radiating from the centre.
    spikes = 8
    r_out = m(6)
    r_in = m(3)
    pts = []
    for k in range(spikes * 2):
        rr = r_out if k % 2 == 0 else r_in
        ang = math.pi * k / spikes - math.pi / 2
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    pygame.draw.polygon(face, (255, 240, 160), pts)
    # tiny dark seat under the boss's lower-right so it reads raised, not printed.
    pygame.draw.circle(face, (150, 116, 54), (cx, cy), m(1))

    # crisp outer gold ring stroke to seal the disc edge.
    pygame.draw.circle(face, (236, 202, 116), (cx, cy), disc_r, max(1, m(1)))


# ── review sheet ──────────────────────────────────────────────────────────────
CW, CH = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324 x 200 author canvas
rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                   CW - 2 * sc.m(sc._INSET), CH - 2 * sc.m(sc._INSET))


def new_panel():
    s = pygame.Surface((CW, CH), pygame.SRCALPHA)
    return s


p0 = new_panel()
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

p1 = new_panel()
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

p2 = new_panel()
_saved_state_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
try:
    sc.draw_card(p2, SID, rect, equipped=False, secret=False, owned=False)
finally:
    sc.state_chip = _saved_state_chip
# the hang-tag anchors itself at a fixed (44,60) inside the surface.
sc._draw_hang_tag(p2, rect.centerx, rect.centery, draw_face_fn=gold_seal_face)

# zoom strip: honest downscale to live 1x, then integer 2x so pixels read true.
zoom = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
zoom = pygame.transform.scale2x(zoom)

# ── compose ────────────────────────────────────────────────────────────────────
xs = [20, 360, 700]
panel_y = 102
BG = (8, 8, 20)

sheet_w = xs[2] + CW + 20
sheet_h = panel_y + CH + 30 + zoom.get_height() + 40
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(26, True)
lab_f = hud_font(17, True)

sheet.blit(title_f.render("OWNED CARD STATE — gold-seal-medallion (round 1)",
                          True, (246, 224, 150)), (20, 30))
sheet.blit(lab_f.render("skin_mummy  •  legendary  •  concept = intact cream "
                        "tag, struck gold wax seal (NOT the dark tick)",
                        True, (150, 150, 175)), (20, 66))

labels = ["UNOWNED (price tag)", "EQUIPPED (dark tick)", "CONCEPT — gold seal"]
for x, p, lab in zip(xs, (p0, p1, p2), labels):
    sheet.blit(p, (x, panel_y))
    sheet.blit(lab_f.render(lab, True, (200, 200, 220)), (x, panel_y - 24))

zy = panel_y + CH + 30
sheet.blit(zoom, (xs[2], zy))
sheet.blit(lab_f.render("CONCEPT @ 1x -> 2x (true in-game pixels)",
                        True, (200, 200, 220)), (xs[2], zy - 24))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_owned_v1", "gold_seal_medallion", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out, sheet.get_size())
