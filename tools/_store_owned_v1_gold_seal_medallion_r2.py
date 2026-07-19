"""Round-2 review render for the gold-seal-medallion owned-card state.

An intact cream hang-tag whose hero is a gold wax seal PRESSED INTO the lower
face — matte struck gold, seated with a hard dark edge + inward occlusion, so it
reads as claimed/sealed rather than a glowing coin pickup. Headless (SDL dummy)
so it renders identically to the offline build tooling on either target.

R2 answers the R1 art-director notes: seal-vs-cream contrast pushed to a pressed
read, additive bloom removed for AO + a cast drop-shadow, scallops thinned and
valley-darkened to survive downscale, the sunburst boss replaced by a seated
domed pip, and the emboss rebalanced to carry relief by value, not a bright line.
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
    """Press a matte gold wax seal into the lower tag face. A cast drop-shadow +
    a deep radial gradient + a hard dark-bronze edge + an inward occlusion ring
    seat the disc INTO the cream; a valley-darkened scallop band and a seated
    domed boss read as a genuine struck seal at ~40px final — NOT the dark tick,
    NOT an additive coin glow."""
    m = sc.m
    cx = sc._TAG_W // 2
    cy = int(sc._TAG_H * 0.55)

    disc_r = m(10)                 # pulled in from R1's m(11) to expose a rim band
    scallop_r = m(13)              # scallop centres ride a ~3px band off the disc
    bump_r = m(3)
    sil_r = scallop_r + int(bump_r * 0.5)   # medallion silhouette for the cast shadow

    # CAST DROP-SHADOW onto the cream (replaces the R1 additive underglow): a
    # 1px bottom-right offset dark disc, drawn FIRST so only the lower-right
    # crescent survives once the seal covers it — the seal sits ON the tag with
    # weight, it does not float or glow.
    sh = pygame.Surface((sc._TAG_W, sc._TAG_H), pygame.SRCALPHA)
    pygame.draw.circle(sh, (52, 36, 16, 105), (cx + m(1), cy + m(1)), sil_r)
    pygame.draw.circle(sh, (52, 36, 16, 55), (cx + m(1.6), cy + m(1.6)), sil_r + m(1))
    face.blit(sh, (0, 0))

    # SCALLOP BAND — a dark-bronze valley disc first, then ~8 lit bumps on top so
    # the gaps read as an intentional rhythm (not one merged bump band) at scale.
    pygame.draw.circle(face, (104, 74, 34), (cx, cy), scallop_r + bump_r)
    n_scallop = 8
    for i in range(n_scallop):
        a = 2 * math.pi * i / n_scallop
        bx = int(round(cx + scallop_r * math.cos(a)))
        by = int(round(cy + scallop_r * math.sin(a)))
        pygame.draw.circle(face, (150, 108, 52), (bx, by), bump_r)
        # a top-left lit cap gives each bump volume so the band reads dimensional.
        pygame.draw.circle(face, (224, 192, 120),
                           (bx - m(1), by - m(1)), max(1, bump_r - m(1)))

    # MAIN DISC — matte gold radial gradient, a warm-but-restrained centre falling
    # to a DEEP bronze rim (ΔL* ~56 vs the cream) so the disc seats dark, not
    # bright. Gamma keeps most of the face gold while the rim darkens hard.
    for i in range(disc_r, 0, -1):
        t = (i / disc_r) ** 1.25
        col = sc.lerp_color((214, 178, 106), (100, 70, 30), t)
        pygame.draw.circle(face, col, (cx, cy), i)

    # HARD OUTER EDGE — a thin dark-bronze ring so the disc boundary is crisp and
    # unambiguous against the cream (no soft merge into the tag).
    pygame.draw.circle(face, (120, 88, 40), (cx, cy), disc_r, max(1, m(1)))

    # INWARD AMBIENT-OCCLUSION RING — a dark halo hugging the INSIDE of the edge.
    # A pressed seat is dark where the tag lip overhangs it: this is what sells
    # "stamped into" over "stuck on top."
    ao = pygame.Surface((sc._TAG_W, sc._TAG_H), pygame.SRCALPHA)
    ao_w = max(1, m(3))
    for k in range(ao_w):
        a = int(90 * (1 - k / ao_w) ** 1.4)
        pygame.draw.circle(ao, (46, 30, 12, a), (cx, cy), disc_r - k, max(1, m(0.8)))
    face.blit(ao, (0, 0))

    # EMBOSS — relief carried by VALUE contrast: a WIDE dark shadow arc bottom-
    # right, a restrained (not blinding) lit arc top-left. On the matte gold face
    # the value step reads at 1x where R1's bright line vanished.
    er = disc_r - m(1.6)
    box = (cx - er, cy - er, er * 2, er * 2)
    pygame.draw.arc(face, (78, 52, 20), box,
                    math.radians(250), math.radians(400), max(2, m(2.4)))
    pygame.draw.arc(face, (240, 214, 150), box,
                    math.radians(72), math.radians(206), max(2, m(1.3)))

    # SEATED DOMED BOSS — replaces R1's collapsing 8-spike star. A real dark
    # recessed seat ring, then a small radial dome pip with a top-left specular:
    # one clean struck pip survives 40px where 8 spikes blurred to a blob.
    seat_r = m(4.5)
    seat = pygame.Surface((sc._TAG_W, sc._TAG_H), pygame.SRCALPHA)
    pygame.draw.circle(seat, (60, 40, 16, 200), (cx, cy), seat_r)
    face.blit(seat, (0, 0))
    pip_r = m(3)
    for i in range(pip_r, 0, -1):
        t = (i / pip_r) ** 1.1
        col = sc.lerp_color((236, 204, 138), (168, 122, 52), t)
        pygame.draw.circle(face, col, (cx, cy), i)
    pygame.draw.circle(face, (250, 234, 186),
                       (cx - m(0.8), cy - m(0.8)), max(1, m(1)))


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

sheet.blit(title_f.render("OWNED CARD STATE — gold-seal-medallion (round 2)",
                          True, (246, 224, 150)), (20, 30))
sheet.blit(lab_f.render("skin_mummy  •  legendary  •  seal PRESSED into cream "
                        "(matte gold, AO seat, hard edge — no additive glow)",
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
                   "docs", "store_owned_v1", "gold_seal_medallion", "round_2.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out, sheet.get_size())
