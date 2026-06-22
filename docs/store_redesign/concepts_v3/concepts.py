"""
Five distinct EVOLUTIONS of the chosen NIGHT AVIARY store look (concepts_v3).

Every concept keeps the Night Aviary core — deep night world, round glass
CABOCHON thumbnail, faceted rarity GEM, warm-gold coin + balance capsule, the
unified chip, and the colourblind-safe 4-tier + mystery rarity language — and
changes only the MATERIAL / MOTIF / palette-accent, so they read as five
different luxe night jewel-boxes:

  1. CONSTELLATION — star-map ground, fine gold constellation lines threading
                     the rarity gems; celestial, airy, elegant.
  2. ABYSSAL       — bioluminescent deep-sea night; indigo->teal depth, pearl +
                     abalone accents; the cabochon reads as a glowing porthole.
  3. ROYAL VELVET  — regal night; plum/sapphire velvet ground, ornate gold
                     scrollwork frames, tassels; the richest, most opulent.
  4. MOONLIT FROST — cool moonlight; frosted/etched glass, silver-blue +
                     platinum with restrained gold; the most minimal-luxe.
  5. CLOISONNÉ     — jewelled enamel; fine gold cell-work over deep Jingtai-blue
                     enamel panels, gemstone inlays; the most ornate craft look.

All geometry (cabochon / name / chip bands, gem seat, header lanes, page +
back rows) is inherited from render.Concept, which fixes the eight reported
layout defects structurally. Concepts paint material into fixed slots only.
"""
import math
import pygame

from game.config import W, H
from game.draw import lerp_color, rounded_rect, UI_CREAM, NEAR_BLACK, WHITE
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE
from game.surprise_box_variants import _draw_qmark

import render as R
from render import (vgrad_rect, hgrad_rect, soft_glow, drop_shadow,
                    gradient_text, coin_glyph, facet_gem, chip, cabochon,
                    metal_rim, inner_bevel, gold_rule, thumb,
                    Concept, EQUIPPED_ID, SECRET_ID, BALANCE,
                    R_DISC, CY_DISC, GEM_R,
                    header_titlebar, balance_capsule, underline_tabs,
                    back_pill, modal_skeleton, _cost, _rarity, _name, _is_secret)


# =============================================================================
# 1. CONSTELLATION — the purest evolution. A star-map ground, with a faint gold
#    constellation line threading from the corner gem toward the cabochon; cards
#    are clear night-glass plates with a hairline gold map-rule.
# =============================================================================
class Constellation(Concept):
    NAME = "CONSTELLATION"
    DESC = "Star-map night · gold constellation lines · glass cabochon"
    BG = ((5, 6, 26), (9, 11, 40), (15, 16, 56), (22, 22, 70))
    STARS = True
    star_t = 2.0
    GOLD = _GOLD_BRIGHT
    GOLD_PALE = _GOLD_PALE
    GOLD_DEEP = _GOLD_DEEP
    TITLE_TOP = (255, 244, 196)
    TITLE_BOT = (240, 178, 66)
    TITLE_OUT = _RED_OUTLINE
    RARITY = {
        "common":    {"gem": (208, 200, 226), "glow": (176, 170, 210), "deep": (78, 74, 112)},
        "rare":      {"gem": (104, 184, 250),  "glow": (70, 154, 244),  "deep": (24, 74, 136)},
        "epic":      {"gem": (190, 116, 246),  "glow": (170, 90, 242),  "deep": (78, 32, 122)},
        "legendary": {"gem": (255, 200, 100),  "glow": (255, 164, 54),  "deep": (146, 90, 20)},
    }
    MYSTERY = {"gem": (222, 228, 240), "glow": (192, 210, 232), "deep": (88, 96, 120)}
    CARD_T = (20, 22, 54)
    CARD_B = (9, 10, 30)
    CABO_LO = (26, 28, 54)
    CABO_HI = (5, 6, 16)
    CABO_RING = (150, 120, 56)
    FRAME_DEEP = (60, 50, 22)
    FRAME_BRIGHT = (236, 200, 110)
    NAME_COL = (244, 236, 210)

    def bg(self, surf):
        super().bg(surf)
        # faint gold constellation lines drifting across the deep map.
        pts = [(40, 240), (96, 196), (150, 250), (212, 210), (300, 268),
               (60, 470), (140, 520), (250, 480), (320, 540)]
        lines = pygame.Surface((W, H), pygame.SRCALPHA)
        for a, b in zip(pts, pts[1:]):
            pygame.draw.line(lines, (210, 180, 110, 26), a, b, 1)
        for px, py in pts:
            pygame.draw.circle(lines, (255, 226, 160, 60), (px, py), 1)
        surf.blit(lines, (0, 0), special_flags=pygame.BLEND_ADD)

    def header(self, surf):
        band = pygame.Surface((W, 96), pygame.SRCALPHA)
        for y in range(96):
            a = int(110 * (1 - y / 96))
            pygame.draw.line(band, (20, 18, 52, a), (0, y), (W, y))
        surf.blit(band, (0, 0))
        pygame.draw.rect(surf, (*self.GOLD, 60), (3, 3, W - 6, H - 6),
                         width=1, border_radius=10)
        header_titlebar(self, surf, "STORE")

    def ornament(self, surf, rect, pal, secret):
        # a hairline constellation thread from the corner gem toward the disc,
        # ALL inside the safe top-right zone (never touches name/chip lanes).
        gx, gy = rect.right - 15, rect.y + 15
        mid = (rect.centerx + 14, rect.y + CY_DISC - R_DISC - 2)
        thread = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.line(thread, (*pal["glow"], 90),
                         (gx - rect.x, gy - rect.y), (mid[0] - rect.x, mid[1] - rect.y), 1)
        for fx, fy in (((gx + mid[0]) // 2, (gy + mid[1]) // 2),):
            pygame.draw.circle(thread, (*pal["gem"], 200), (fx - rect.x, fy - rect.y), 1)
        surf.blit(thread, rect.topleft, special_flags=pygame.BLEND_ADD)
        # thin gold map-rule under the name lane separating it from the chip.
        gold_rule(surf, rect.x + 30, rect.right - 30, rect.y + R.Y_NAME + 12, self.GOLD, peak=70)

    def back(self, surf):
        back_pill(self, surf, body_top=(28, 26, 60), body_bot=(14, 14, 36))

    def modal(self, surf, sid):
        modal_skeleton(self, surf, sid,
                       panel_top=(24, 24, 58), panel_bot=(10, 10, 30),
                       frame_deep=lerp_color(self.GOLD, NEAR_BLACK, 0.4),
                       frame_bright=(*self.GOLD, 230),
                       head_col=self.GOLD_PALE)


# =============================================================================
# 2. ABYSSAL — bioluminescent deep-sea night. Indigo->teal depth gradient, a
#    drifting current of light motes; cards are deep-water glass with a soft
#    glowing aura and an abalone iridescent rim. The cabochon reads as a lit
#    porthole. Pearl + abalone accents.
# =============================================================================
class Abyssal(Concept):
    NAME = "ABYSSAL"
    DESC = "Bioluminescent deep · indigo→teal · pearl porthole cabochon"
    BG = ((8, 14, 40), (8, 24, 58), (8, 40, 70), (10, 58, 76))
    STARS = True
    star_t = 1.1
    GOLD = (236, 206, 132)
    GOLD_PALE = (252, 234, 184)
    GOLD_DEEP = (132, 96, 40)
    TITLE_TOP = (224, 248, 246)
    TITLE_BOT = (96, 196, 198)
    TITLE_OUT = (10, 46, 60)
    CREAM = (236, 248, 248)
    # abyssal rarity: pearl / aqua / violet-abalone / amber-bioluminescence.
    RARITY = {
        "common":    {"gem": (210, 232, 234), "glow": (176, 214, 218), "deep": (70, 110, 116)},
        "rare":      {"gem": (84, 220, 218),  "glow": (48, 198, 200),  "deep": (10, 96, 104)},
        "epic":      {"gem": (170, 142, 248), "glow": (140, 112, 244), "deep": (62, 44, 124)},
        "legendary": {"gem": (255, 198, 110), "glow": (255, 166, 70),  "deep": (148, 92, 26)},
    }
    MYSTERY = {"gem": (224, 240, 240), "glow": (190, 224, 226), "deep": (78, 112, 120)}
    CARD_T = (14, 36, 64)
    CARD_B = (8, 18, 42)
    CABO_LO = (18, 52, 72)
    CABO_HI = (4, 12, 30)
    CABO_RING = (120, 200, 200)
    FRAME_DEEP = (16, 70, 78)
    FRAME_BRIGHT = (140, 220, 218)
    NAME_COL = (224, 244, 244)

    def bg(self, surf):
        super().bg(surf)
        # caustic light shafts + drifting biolum motes.
        shafts = pygame.Surface((W, H), pygame.SRCALPHA)
        for sx in (70, 180, 300):
            for k in range(40):
                a = int(18 * (1 - k / 40))
                pygame.draw.line(shafts, (120, 220, 220, a),
                                 (sx - 20, 0), (sx - 20 + k, 220), 1)
        surf.blit(shafts, (0, 0), special_flags=pygame.BLEND_ADD)
        for mx, my, mr in ((54, 300, 2), (140, 420, 1), (250, 360, 2),
                           (310, 500, 1), (90, 540, 1), (200, 250, 1)):
            soft_glow(surf, mx, my, mr * 6, (110, 220, 210), 60, layers=4)

    def header(self, surf):
        band = pygame.Surface((W, 96), pygame.SRCALPHA)
        for y in range(96):
            a = int(120 * (1 - y / 96))
            pygame.draw.line(band, (8, 30, 52, a), (0, y), (W, y))
        surf.blit(band, (0, 0))
        pygame.draw.rect(surf, (*self.FRAME_BRIGHT, 60), (3, 3, W - 6, H - 6),
                         width=1, border_radius=10)
        header_titlebar(self, surf, "STORE")

    def chip_colors(self, state):
        return {
            "price": ((60, 42, 16), (236, 206, 132), (252, 234, 184)),
            "equip": ((252, 234, 184), (110, 78, 32), (236, 206, 132)),
            "equipped": ((6, 46, 44), (78, 210, 196), (200, 255, 248)),
            "locked": ((120, 150, 156), (30, 64, 72), (96, 150, 156)),
        }[state]

    def paint_body(self, surf, rect, pal, secret):
        # deep-water glass + an abalone iridescent rim (PRIMARY material cue).
        surf.blit(vgrad_rect(rect.w, rect.h, 16, self.CARD_T, self.CARD_B, 252),
                  rect.topleft)
        sheen = pygame.Surface((rect.w - 12, 16), pygame.SRCALPHA)
        for y in range(16):
            pygame.draw.line(sheen, (180, 240, 238, int(40 * (1 - y / 16))),
                             (0, y), (rect.w - 12, y))
        sm = pygame.Surface((rect.w - 12, 16), pygame.SRCALPHA)
        pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(),
                         border_top_left_radius=12, border_top_right_radius=12)
        sheen.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(sheen, (rect.x + 6, rect.y + 4))
        # abalone rim: shimmer between aqua/violet/pearl along the bezel.
        for i, t in enumerate((0.0, 0.5, 1.0)):
            c = lerp_color(lerp_color((120, 220, 214), (170, 150, 240), t),
                           (236, 244, 244), 0.15)
            pygame.draw.rect(surf, (*c, 150 - i * 30),
                             rect.inflate(-i * 2, -i * 2), width=1,
                             border_radius=16 - i)
        metal_rim(surf, rect, 16, self.FRAME_DEEP, (*self.FRAME_BRIGHT, 150), w=1)

    def paint_cabo(self, surf, cx, cy, pal, secret):
        # lit PORTHOLE: a brass ring + an inner aqua glow behind the glass.
        soft_glow(surf, cx, cy, R_DISC + 2, (90, 200, 200), 70, layers=4)
        cabochon(surf, cx, cy, R_DISC, self.CABO_LO, self.CABO_HI,
                 ring=self.CABO_RING, ring_a=150)
        # brass porthole bolts around the rim.
        for k in range(8):
            ang = 2 * math.pi * k / 8
            bx = cx + int(math.cos(ang) * (R_DISC + 3))
            by = cy + int(math.sin(ang) * (R_DISC + 3))
            pygame.draw.circle(surf, (*self.GOLD, 200), (bx, by), 1)

    def back(self, surf):
        back_pill(self, surf, body_top=(14, 56, 64), body_bot=(8, 30, 44))

    def modal(self, surf, sid):
        modal_skeleton(self, surf, sid,
                       panel_top=(12, 44, 66), panel_bot=(6, 18, 40),
                       frame_deep=(16, 70, 78), frame_bright=(*self.FRAME_BRIGHT, 230),
                       head_col=self.FRAME_BRIGHT)


# =============================================================================
# 3. ROYAL VELVET — regal night. Deep plum/sapphire velvet ground with a soft
#    nap sheen, ornate gold scrollwork frames and a hanging tassel at the
#    legendary tier. The richest, most opulent of the five.
# =============================================================================
class RoyalVelvet(Concept):
    NAME = "ROYAL VELVET"
    DESC = "Plum & sapphire velvet · gold scrollwork · tasselled"
    BG = ((28, 10, 44), (40, 14, 60), (22, 14, 64), (14, 12, 50))
    STARS = True
    star_t = 0.9
    GOLD = (244, 204, 120)
    GOLD_PALE = (255, 232, 174)
    GOLD_DEEP = (138, 92, 32)
    TITLE_TOP = (255, 238, 188)
    TITLE_BOT = (236, 172, 70)
    TITLE_OUT = (74, 18, 44)
    RARITY = {
        "common":    {"gem": (220, 200, 228), "glow": (188, 168, 208), "deep": (92, 70, 110)},
        "rare":      {"gem": (110, 150, 246),  "glow": (78, 118, 240),  "deep": (30, 56, 130)},
        "epic":      {"gem": (208, 110, 224),  "glow": (190, 84, 214),  "deep": (96, 30, 110)},
        "legendary": {"gem": (255, 198, 96),   "glow": (255, 162, 52),  "deep": (146, 88, 18)},
    }
    MYSTERY = {"gem": (228, 222, 236), "glow": (202, 192, 222), "deep": (96, 86, 118)}
    CARD_T = (52, 18, 70)
    CARD_B = (26, 10, 44)
    CABO_LO = (40, 16, 58)
    CABO_HI = (10, 6, 24)
    CABO_RING = (200, 160, 84)
    FRAME_DEEP = (96, 60, 22)
    FRAME_BRIGHT = (248, 212, 130)
    NAME_COL = (255, 236, 188)

    def bg(self, surf):
        super().bg(surf)
        # velvet nap: a soft radial sheen pooling toward the centre.
        nap = pygame.Surface((W, H), pygame.SRCALPHA)
        cx, cy = W // 2, H // 2 - 30
        for r in range(260, 0, -20):
            a = int(20 * (1 - r / 260))
            pygame.draw.circle(nap, (150, 96, 180, a), (cx, cy), r)
        surf.blit(nap, (0, 0), special_flags=pygame.BLEND_ADD)

    def _scroll(self, surf, x, y, sgn_x, sgn_y, col):
        # an ornate gold scroll flourish at a card corner (the velvet frame).
        rect = pygame.Rect(min(x, x + sgn_x * 12), min(y, y + sgn_y * 12), 12, 12)
        a0 = 0 if (sgn_x > 0 and sgn_y > 0) else (
            -math.pi / 2 if (sgn_x > 0) else (math.pi / 2 if sgn_y > 0 else math.pi))
        pygame.draw.arc(surf, col, rect, a0, a0 + math.pi / 2, 2)
        pygame.draw.line(surf, col, (x, y), (x + sgn_x * 11, y), 1)
        pygame.draw.line(surf, col, (x, y), (x, y + sgn_y * 11), 1)
        pygame.draw.circle(surf, col, (x + sgn_x * 11, y), 1)
        pygame.draw.circle(surf, col, (x, y + sgn_y * 11), 1)

    def header(self, surf):
        band = pygame.Surface((W, 98), pygame.SRCALPHA)
        for y in range(98):
            a = int(140 * (1 - y / 98))
            pygame.draw.line(band, (44, 16, 64, a), (0, y), (W, y))
        surf.blit(band, (0, 0))
        pygame.draw.rect(surf, (*self.GOLD, 80), (3, 3, W - 6, H - 6),
                         width=1, border_radius=10)
        # scroll flourishes flanking the title.
        for sx in (W // 2 - 92, W // 2 + 92):
            self._scroll(surf, sx, 30, 1 if sx < W // 2 else -1, 1, (*self.GOLD, 200))
        header_titlebar(self, surf, "STORE")

    def chip_colors(self, state):
        return {
            "price": ((58, 36, 12), (244, 204, 120), (255, 232, 174)),
            "equip": ((255, 232, 174), (112, 70, 28), (244, 204, 120)),
            "equipped": ((14, 50, 30), (96, 200, 134), (210, 255, 222)),
            "locked": ((150, 130, 160), (52, 32, 64), (120, 96, 132)),
        }[state]

    def paint_body(self, surf, rect, pal, secret):
        # velvet panel + a subtle inner nap sheen, then ornate scroll corners.
        surf.blit(vgrad_rect(rect.w, rect.h, 14, self.CARD_T, self.CARD_B, 254),
                  rect.topleft)
        nap = pygame.Surface(rect.size, pygame.SRCALPHA)
        soft_glow(nap, rect.w // 2, 28, 50, (170, 110, 200), 40, layers=4)
        nm = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(nm, (255, 255, 255, 255), nm.get_rect(), border_radius=14)
        nap.blit(nm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(nap, rect.topleft)
        metal_rim(surf, rect, 14, self.FRAME_DEEP, (*self.FRAME_BRIGHT, 200), w=2)

    def ornament(self, surf, rect, pal, secret):
        # gold scrollwork in all four corners (the opulent frame) — corner-safe.
        self._scroll(surf, rect.x + 9, rect.y + 9, 1, 1, (*self.GOLD_DEEP, 230))
        self._scroll(surf, rect.x + 9, rect.bottom - 9, 1, -1, (*self.GOLD_DEEP, 200))
        self._scroll(surf, rect.right - 9, rect.bottom - 9, -1, -1, (*self.GOLD_DEEP, 200))
        # NOTE: top-right corner is the GEM seat — leave it for the gem only.
        # legendary gets a small hanging tassel from the cabochon ring, drawn
        # in the gap between disc and name lane (never on either).
        if not secret and _rarity_safe(rect) and pal is self.RARITY.get("legendary"):
            tx = rect.centerx
            ty = rect.y + CY_DISC + R_DISC
            pygame.draw.line(surf, (*self.GOLD, 200), (tx, ty), (tx, ty + 6), 1)
            pygame.draw.circle(surf, (*self.GOLD, 220), (tx, ty + 8), 2)

    def back(self, surf):
        back_pill(self, surf, body_top=(56, 20, 72), body_bot=(30, 12, 50))

    def modal(self, surf, sid):
        modal_skeleton(self, surf, sid,
                       panel_top=(54, 20, 74), panel_bot=(24, 10, 46),
                       frame_deep=(96, 60, 22), frame_bright=(*self.GOLD, 235),
                       head_col=self.GOLD_PALE)


def _rarity_safe(rect):
    # The tassel cue keys off the legendary palette identity; this helper keeps
    # the ornament hook free of catalog lookups (palette identity is enough).
    return True


# =============================================================================
# 4. MOONLIT FROST — cool moonlight. Frosted / etched glass cards, silver-blue +
#    platinum with restrained gold, a single soft moon glow. The most
#    minimal-luxe: crisp, serene, lots of breathing room.
# =============================================================================
class MoonlitFrost(Concept):
    NAME = "MOONLIT FROST"
    DESC = "Frosted glass · silver-blue & platinum · serene minimal-luxe"
    BG = ((18, 26, 48), (26, 38, 64), (34, 50, 80), (44, 62, 94))
    STARS = True
    star_t = 0.7
    GOLD = (226, 214, 168)        # restrained, pale platinum-gold
    GOLD_PALE = (244, 240, 222)
    GOLD_DEEP = (150, 142, 110)
    TITLE_TOP = (240, 246, 252)
    TITLE_BOT = (176, 198, 224)
    TITLE_OUT = (40, 56, 84)
    CREAM = (240, 246, 252)
    # cool rarity: frost-white / ice-blue / amethyst / pale gold.
    RARITY = {
        "common":    {"gem": (224, 232, 240), "glow": (196, 212, 230), "deep": (96, 112, 134)},
        "rare":      {"gem": (140, 196, 244),  "glow": (104, 168, 234),  "deep": (40, 86, 138)},
        "epic":      {"gem": (186, 156, 230),  "glow": (158, 124, 218),  "deep": (78, 56, 122)},
        "legendary": {"gem": (236, 214, 150),  "glow": (224, 190, 120),  "deep": (138, 110, 56)},
    }
    MYSTERY = {"gem": (236, 242, 248), "glow": (210, 224, 238), "deep": (108, 124, 146)}
    CARD_T = (50, 64, 92)
    CARD_B = (28, 38, 62)
    CABO_LO = (54, 70, 98)
    CABO_HI = (18, 26, 46)
    CABO_RING = (200, 214, 232)
    FRAME_DEEP = (90, 104, 128)
    FRAME_BRIGHT = (224, 234, 246)
    NAME_COL = (236, 242, 250)

    def bg(self, surf):
        super().bg(surf)
        # a single soft moon glow upper-right.
        soft_glow(surf, W - 64, 150, 60, (210, 224, 240), 70, layers=6)
        pygame.draw.circle(surf, (236, 242, 250), (W - 64, 150), 18)
        pygame.draw.circle(surf, (210, 222, 238), (W - 58, 146), 16)

    def header(self, surf):
        band = pygame.Surface((W, 96), pygame.SRCALPHA)
        for y in range(96):
            a = int(90 * (1 - y / 96))
            pygame.draw.line(band, (30, 42, 66, a), (0, y), (W, y))
        surf.blit(band, (0, 0))
        pygame.draw.rect(surf, (*self.FRAME_BRIGHT, 60), (3, 3, W - 6, H - 6),
                         width=1, border_radius=10)
        header_titlebar(self, surf, "STORE")

    def chip_colors(self, state):
        return {
            "price": ((54, 64, 86), (224, 232, 240), (244, 248, 252)),
            "equip": ((244, 248, 252), (96, 112, 134), (224, 232, 240)),
            "equipped": ((12, 48, 44), (96, 206, 184), (210, 255, 246)),
            "locked": ((130, 146, 168), (54, 66, 88), (110, 128, 150)),
        }[state]

    def paint_body(self, surf, rect, pal, secret):
        # frosted glass: translucent panel + a fine etched border + a faint
        # diagonal frost streak (PRIMARY material cue).
        surf.blit(vgrad_rect(rect.w, rect.h, 16, self.CARD_T, self.CARD_B, 235),
                  rect.topleft)
        # etched hatch streak, masked to the rounded rect.
        frost = pygame.Surface(rect.size, pygame.SRCALPHA)
        for k in range(-rect.h, rect.w, 9):
            pygame.draw.line(frost, (235, 244, 252, 16),
                             (k, 0), (k + rect.h, rect.h), 1)
        fm = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(fm, (255, 255, 255, 255), fm.get_rect(), border_radius=16)
        frost.blit(fm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(frost, rect.topleft)
        # crisp double etched rim (silver outer, white inner).
        pygame.draw.rect(surf, (*self.FRAME_DEEP, 220), rect, width=2, border_radius=16)
        pygame.draw.rect(surf, (255, 255, 255, 150), rect.inflate(-4, -4),
                         width=1, border_radius=14)

    def paint_cabo(self, surf, cx, cy, pal, secret):
        cabochon(surf, cx, cy, R_DISC, self.CABO_LO, self.CABO_HI,
                 ring=self.CABO_RING, ring_a=170)
        # a thin frost ring just outside the glass for the etched look.
        pygame.draw.circle(surf, (230, 240, 250, 90), (cx, cy), R_DISC + 2, 1)

    def back(self, surf):
        back_pill(self, surf, body_top=(56, 70, 98), body_bot=(34, 46, 72))

    def modal(self, surf, sid):
        modal_skeleton(self, surf, sid,
                       panel_top=(56, 70, 100), panel_bot=(30, 40, 66),
                       frame_deep=(96, 110, 134), frame_bright=(*self.FRAME_BRIGHT, 230),
                       head_col=self.FRAME_BRIGHT)


# =============================================================================
# 5. CLOISONNÉ — jewelled enamel. Fine gold cell-work (cloisonné) borders over
#    deep Jingtai-blue enamel panels, with gemstone inlays at the corners. The
#    most ornate, craft-jewelry look.
# =============================================================================
class Cloisonne(Concept):
    NAME = "CLOISONNÉ"
    DESC = "Jingtai-blue enamel · gold cell-work · gemstone inlay"
    BG = ((6, 18, 44), (8, 26, 60), (10, 34, 74), (8, 24, 56))
    STARS = True
    star_t = 1.0
    GOLD = (246, 208, 116)
    GOLD_PALE = (255, 234, 168)
    GOLD_DEEP = (150, 102, 34)
    TITLE_TOP = (255, 236, 176)
    TITLE_BOT = (238, 176, 64)
    TITLE_OUT = (18, 40, 78)
    # enamel rarity: white-jade / peacock-blue / imperial-violet / amber-gold.
    RARITY = {
        "common":    {"gem": (224, 226, 220), "glow": (196, 200, 196), "deep": (96, 102, 100)},
        "rare":      {"gem": (72, 188, 220),  "glow": (40, 162, 204),  "deep": (12, 80, 110)},
        "epic":      {"gem": (176, 116, 224),  "glow": (150, 88, 214),  "deep": (74, 34, 110)},
        "legendary": {"gem": (250, 196, 88),   "glow": (246, 160, 48),  "deep": (148, 92, 18)},
    }
    MYSTERY = {"gem": (228, 232, 230), "glow": (200, 210, 210), "deep": (96, 108, 112)}
    CARD_T = (16, 44, 86)
    CARD_B = (8, 24, 56)
    CABO_LO = (18, 50, 92)
    CABO_HI = (6, 16, 40)
    CABO_RING = (246, 208, 116)
    FRAME_DEEP = (120, 80, 24)
    FRAME_BRIGHT = (250, 216, 128)
    NAME_COL = (255, 234, 168)

    def header(self, surf):
        band = pygame.Surface((W, 96), pygame.SRCALPHA)
        for y in range(96):
            a = int(120 * (1 - y / 96))
            pygame.draw.line(band, (8, 28, 60, a), (0, y), (W, y))
        surf.blit(band, (0, 0))
        # a gold cell-work border framing the whole screen.
        pygame.draw.rect(surf, (*self.GOLD, 120), (4, 4, W - 8, H - 8),
                         width=2, border_radius=8)
        pygame.draw.rect(surf, (*self.GOLD_DEEP, 120), (7, 7, W - 14, H - 14),
                         width=1, border_radius=6)
        header_titlebar(self, surf, "STORE")

    def chip_colors(self, state):
        return {
            "price": ((58, 38, 12), (246, 208, 116), (255, 234, 168)),
            "equip": ((255, 234, 168), (112, 74, 28), (246, 208, 116)),
            "equipped": ((8, 48, 42), (84, 206, 178), (200, 255, 244)),
            "locked": ((130, 150, 162), (28, 60, 80), (96, 150, 170)),
        }[state]

    def paint_body(self, surf, rect, pal, secret):
        # deep enamel panel with a vitreous sheen.
        enamel = vgrad_rect(rect.w, rect.h, 14, self.CARD_T, self.CARD_B, 255)
        surf.blit(enamel, rect.topleft)
        # glassy enamel highlight pooled top-left (kiln-fired vitreous tell).
        gloss = pygame.Surface(rect.size, pygame.SRCALPHA)
        soft_glow(gloss, 40, 24, 40, (120, 200, 240), 50, layers=4)
        gm = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(gm, (255, 255, 255, 255), gm.get_rect(), border_radius=14)
        gloss.blit(gm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(gloss, rect.topleft)
        # GOLD CELL-WORK: a fine raised cloisonné wire frame (double keyline).
        pygame.draw.rect(surf, self.FRAME_DEEP, rect, width=3, border_radius=14)
        pygame.draw.rect(surf, (*self.FRAME_BRIGHT, 240), rect.inflate(-2, -2),
                         width=2, border_radius=13)
        pygame.draw.rect(surf, (*self.GOLD_PALE, 150), rect.inflate(-6, -6),
                         width=1, border_radius=11)

    def ornament(self, surf, rect, pal, secret):
        # cloisonné cell partitions: thin gold wires sectioning the enamel into
        # a jewellery cell around the cabochon. All in the upper SAFE zone so
        # the name + chip lanes stay clear.
        cx = rect.centerx
        top = rect.y + 6
        # a small gold petal-cell ring framing the cabochon (cell-work motif).
        ring = pygame.Surface(rect.size, pygame.SRCALPHA)
        rcx, rcy = cx - rect.x, CY_DISC
        for k in range(8):
            ang = 2 * math.pi * k / 8
            ex = rcx + int(math.cos(ang) * (R_DISC + 5))
            ey = rcy + int(math.sin(ang) * (R_DISC + 5))
            ex2 = rcx + int(math.cos(ang) * (R_DISC + 9))
            ey2 = rcy + int(math.sin(ang) * (R_DISC + 9))
            pygame.draw.line(ring, (*self.GOLD, 150), (ex, ey), (ex2, ey2), 1)
        pygame.draw.circle(ring, (*self.GOLD, 110), (rcx, rcy), R_DISC + 9, 1)
        surf.blit(ring, rect.topleft)
        # tiny gemstone inlays at the two top corners (the corner GEM is the
        # right-hand rarity gem; left gets a small fixed turquoise inlay cell).
        facet_gem(surf, rect.x + 15, rect.y + 15, 4, (90, 200, 220), (12, 80, 110))

    def back(self, surf):
        back_pill(self, surf, body_top=(14, 50, 90), body_bot=(8, 26, 58))

    def modal(self, surf, sid):
        modal_skeleton(self, surf, sid,
                       panel_top=(14, 48, 92), panel_bot=(8, 24, 54),
                       frame_deep=(120, 80, 24), frame_bright=(*self.FRAME_BRIGHT, 240),
                       head_col=self.GOLD_PALE)


CONCEPTS = [
    Constellation(),
    Abyssal(),
    RoyalVelvet(),
    MoonlitFrost(),
    Cloisonne(),
]
