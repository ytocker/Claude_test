"""Round-1 exploration sheet: 5 metallic CROWN crests for the knight+3x combo.

Each crown is drawn procedurally and composited onto the REAL knight frame
(parrot.get_knight_parrot) so we judge it at gameplay scale. Headless/dummy
SDL so it runs in CI and on any target. Output: docs/knight_crown/round_1.png.
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

# ── crown palette — anchored to the knight's existing BRASS trim ────────────
# Deepen below BRASS for shadow, lift above BRASS_HI for the rim glint so the
# crown reads as the same metal family as the pauldron/visor brass.
G_DK = (150, 116, 52)
G_MID = BRASS                 # (208, 174, 98) — the knight's brass base
G_HI = BRASS_HI               # (255, 232, 168)
G_GLINT = (255, 248, 214)
# Two jewel tones only, drawn from the heraldry gules/azure so the crown stays
# armour, not candy: a deep ruby and a single emerald (the 3x "coins" hint).
RUBY = (196, 44, 58); RUBY_HI = (255, 150, 160)
EMER = (46, 168, 110); EMER_HI = (170, 245, 205)
SAPPH = (60, 96, 196); SAPPH_HI = (165, 195, 255)


def _gem(surf, cx, cy, r, base, hi):
    """Faceted round jewel: dark seat, body, top-left glint."""
    pygame.draw.circle(surf, (max(0, base[0] - 70), max(0, base[1] - 40), max(0, base[2] - 50)), (cx, cy), r + 1)
    pygame.draw.circle(surf, base, (cx, cy), r)
    pygame.draw.circle(surf, hi, (cx - max(1, r // 3), cy - max(1, r // 3)), max(1, r // 2))
    surf.set_at((cx - r // 3, cy - r // 3), (255, 255, 255))


def _band(surf, x0, x1, y, h, with_studs=True):
    """Curved coronet band hugging the dome: gold core + dark seat + rim glint."""
    w = x1 - x0
    pygame.draw.rect(surf, G_DK, (x0, y, w, h))
    pygame.draw.rect(surf, G_MID, (x0, y, w, h - 1))
    pygame.draw.line(surf, G_HI, (x0 + 1, y + 1), (x1 - 1, y + 1), 1)
    pygame.draw.line(surf, (90, 66, 28), (x0, y + h - 1), (x1, y + h - 1), 1)
    if with_studs:
        for sx in range(x0 + 3, x1 - 1, 5):
            surf.set_at((sx, y + h // 2), G_HI)


def _point_tri(surf, cx, base_y, top_y, half):
    """A single gold spike/point with a lit left face."""
    pygame.draw.polygon(surf, G_DK, [(cx - half, base_y), (cx + half, base_y), (cx, top_y)])
    pygame.draw.polygon(surf, G_MID, [(cx - half + 1, base_y - 1), (cx + half - 1, base_y - 1), (cx, top_y + 1)])
    pygame.draw.line(surf, G_HI, (cx - half + 1, base_y - 2), (cx, top_y + 1), 1)


# ── V1 — banded coronet, 3 points ───────────────────────────────────────────
def draw_v1(surf, cx, cy):
    """Simple coronet: one gold band hugging the dome + three short triangular
    points, a ruby centred over the brow. The minimal, unmistakable read."""
    half = 11
    by = cy
    _band(surf, cx - half, cx + half, by, 5)
    for dx, top in ((-7, by - 5), (0, by - 8), (7, by - 5)):
        _point_tri(surf, cx + dx, by + 1, top, 3)
    _gem(surf, cx, by + 2, 2, RUBY, RUBY_HI)


# ── V2 — fleur-de-lis points + centre gem ───────────────────────────────────
def draw_v2(surf, cx, cy):
    """Tall fleur-de-lis points springing from a slim band, a sapphire boss at
    centre. The most regal/royal silhouette."""
    half = 11
    by = cy
    _band(surf, cx - half, cx + half, by, 4, with_studs=False)

    def fleur(fx, scale):
        topy = by - int(9 * scale)
        # centre lobe
        pygame.draw.polygon(surf, G_DK, [(fx - 2, by - 1), (fx + 2, by - 1), (fx, topy)])
        pygame.draw.polygon(surf, G_MID, [(fx - 1, by - 2), (fx + 1, by - 2), (fx, topy + 1)])
        # side lobes curling out
        pygame.draw.line(surf, G_MID, (fx, by - 2), (fx - int(4 * scale), by - int(5 * scale)), 2)
        pygame.draw.line(surf, G_MID, (fx, by - 2), (fx + int(4 * scale), by - int(5 * scale)), 2)
        pygame.draw.line(surf, G_HI, (fx, by - 2), (fx, topy + 1), 1)
        surf.set_at((fx, topy), G_GLINT)

    fleur(cx, 1.0)
    fleur(cx - 8, 0.7)
    fleur(cx + 8, 0.7)
    _gem(surf, cx, by + 1, 2, SAPPH, SAPPH_HI)


# ── V3 — jeweled circlet hugging the dome ────────────────────────────────────
def draw_v3(surf, cx, cy):
    """Low jeweled circlet: a fat gold band wrapped tight to the dome curve,
    alternating ruby/emerald gems set into it, no tall points. Reads cleanly
    as 'rich armour ring', least likely to clip the plume."""
    half = 12
    by = cy + 1
    # band follows the dome arc rather than a flat rect
    pygame.draw.arc(surf, G_DK, (cx - half, by - 4, half * 2, 12), math.radians(190), math.radians(350), 6)
    pygame.draw.arc(surf, G_MID, (cx - half, by - 4, half * 2, 12), math.radians(192), math.radians(348), 4)
    pygame.draw.arc(surf, G_HI, (cx - half + 1, by - 5, half * 2 - 2, 12), math.radians(200), math.radians(340), 1)
    # gems set along the brow
    _gem(surf, cx, by, 2, RUBY, RUBY_HI)
    _gem(surf, cx - 7, by + 1, 2, EMER, EMER_HI)
    _gem(surf, cx + 7, by + 1, 2, EMER, EMER_HI)
    _gem(surf, cx - 11, by + 3, 1, RUBY, RUBY_HI)
    _gem(surf, cx + 11, by + 3, 1, RUBY, RUBY_HI)


# ── V4 — spiked imperial crown ───────────────────────────────────────────────
def draw_v4(surf, cx, cy):
    """Imperial crown: tall banded coronet, many sharp spikes each tipped with
    a tiny pearl, a ruby cross-boss at the very centre. The most aggressive,
    'battle-king' read to pair with the longsword."""
    half = 12
    by = cy
    _band(surf, cx - half, cx + half, by, 5, with_studs=False)
    spikes = [-10, -6, -2, 2, 6, 10]
    for dx in spikes:
        h = 9 if abs(dx) <= 2 else (7 if abs(dx) <= 6 else 5)
        _point_tri(surf, cx + dx, by + 1, by - h, 2)
        surf.set_at((cx + dx, by - h), G_GLINT)
    # central ruby boss over the brow
    _gem(surf, cx, by + 2, 2, RUBY, RUBY_HI)


# ── V5 — laurel-meets-crown wreath ───────────────────────────────────────────
def draw_v5(surf, cx, cy):
    """Gold victory laurel fused with a coronet: two sprigs of gilded leaves
    sweeping up from a thin band toward a central emerald, evoking a crowned
    champion. Softer, organic silhouette."""
    half = 11
    by = cy
    _band(surf, cx - half, cx + half, by, 4, with_studs=False)

    def sprig(sign):
        x = cx
        y = by - 1
        for i in range(5):
            lx = x + sign * (2 + i * 2)
            ly = y - 1 - i * 2
            # each leaf: small lit gold blade angled outward-up
            pygame.draw.polygon(surf, G_DK, [
                (lx, ly + 1), (lx + sign * 3, ly - 2), (lx + sign * 1, ly - 3)])
            pygame.draw.polygon(surf, G_MID, [
                (lx, ly), (lx + sign * 2, ly - 2), (lx + sign * 1, ly - 2)])
            surf.set_at((lx + sign, ly - 1), G_HI)

    sprig(-1)
    sprig(1)
    _gem(surf, cx, by - 3, 2, EMER, EMER_HI)
    surf.set_at((cx, by - 6), G_GLINT)


CANDIDATES = [
    ("1  CORONET",   draw_v1),
    ("2  FLEUR-DE-LIS", draw_v2),
    ("3  CIRCLET",   draw_v3),
    ("4  IMPERIAL",  draw_v4),
    ("5  LAUREL",    draw_v5),
]


# ── helm-crown anchor on the real knight frame ───────────────────────────────
# Knight char surface is (SPRITE_W+2*PAD, SPRITE_H+2*PAD) = 96x92. The base
# parrot rect is centred in it; the armet helm is blitted at _P(nom,0.73,0.17)
# at size (nom.w*0.5, nom.h*0.54). The dome top sits a little above the helm
# centre — these fractions place the crown band right on the dome crest.
PAD = 16
NOM_X = PAD; NOM_Y = PAD
HELM_CX = NOM_X + 0.73 * parrot.SPRITE_W
HELM_TOP = NOM_Y + 0.17 * parrot.SPRITE_H - 0.54 * parrot.SPRITE_H * 0.5
CROWN_CX = int(HELM_CX)
CROWN_CY = int(HELM_TOP + 5)   # band sits just below the dome apex


def _knight_with_crown(crown_fn):
    """Real knight frame 0 (flat tilt) with the candidate crown drawn on the
    helm crown. Returns the full char surface."""
    base = parrot.get_knight_parrot(0, 0.0)
    surf = base.copy()
    crown_fn(surf, CROWN_CX, CROWN_CY)
    return surf


def main():
    pygame.font.init()
    label_font = pygame.font.SysFont("dejavusans", 13, bold=True)
    sub_font = pygame.font.SysFont("dejavusans", 10)

    BG = (38, 44, 58)
    PANEL = (28, 33, 44)
    INK = (232, 238, 250)
    DIM = (150, 160, 180)

    cols = 5
    cell_w = 200
    cell_h = 470
    head_h = 56
    sheet = pygame.Surface((cols * cell_w, head_h + cell_h), pygame.SRCALPHA)
    sheet.fill(BG)

    title = pygame.font.SysFont("dejavusans", 22, bold=True).render(
        "Knight + 3x  —  METALLIC CROWN crest  (round 1)", True, INK)
    sheet.blit(title, (16, 12))
    subtitle = sub_font.render(
        "drawn on the real knight armet helm  ·  left tile = ~2x play scale  ·  right tile = 5x detail",
        True, DIM)
    sheet.blit(subtitle, (18, 38))

    for i, (name, fn) in enumerate(CANDIDATES):
        x0 = i * cell_w
        panel = pygame.Rect(x0 + 6, head_h + 6, cell_w - 12, cell_h - 12)
        pygame.draw.rect(sheet, PANEL, panel, border_radius=8)
        pygame.draw.rect(sheet, (60, 70, 90), panel, width=1, border_radius=8)

        lab = label_font.render(name, True, (255, 226, 150))
        sheet.blit(lab, (panel.x + 10, panel.y + 8))

        composed = _knight_with_crown(fn)

        # ~2x play-scale tile (no smoothing — show the real native read)
        s2 = pygame.transform.scale(
            composed, (composed.get_width() * 2, composed.get_height() * 2))
        sheet.blit(s2, (panel.centerx - s2.get_width() // 2, panel.y + 30))

        cap = sub_font.render("~2x", True, DIM)
        sheet.blit(cap, (panel.centerx - s2.get_width() // 2, panel.y + 30 + s2.get_height() + 1))

        # 5x detail crop — zoom the head/helm region only
        crop = pygame.Rect(int(CROWN_CX - 26), int(CROWN_CY - 14), 50, 52)
        crop = crop.clamp(composed.get_rect())
        head = composed.subsurface(crop).copy()
        s5 = pygame.transform.scale(head, (head.get_width() * 5, head.get_height() * 5))
        sub_x = panel.centerx - s5.get_width() // 2
        sub_y = panel.y + 30 + s2.get_height() + 22
        # checker backing so transparency + gold both read
        pygame.draw.rect(sheet, (20, 24, 32), (sub_x - 2, sub_y - 2, s5.get_width() + 4, s5.get_height() + 4))
        sheet.blit(s5, (sub_x, sub_y))
        cap2 = sub_font.render("5x detail", True, DIM)
        sheet.blit(cap2, (sub_x, sub_y + s5.get_height() + 2))

    out_dir = pathlib.Path("/home/user/skybit/docs/knight_crown")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "round_1.png"
    pygame.image.save(sheet, str(out))
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
