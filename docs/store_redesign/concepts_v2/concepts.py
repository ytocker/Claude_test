"""
The five distinct store concepts for concepts_v2.

Each is a complete, shippable Skybit store look. They differ by structural
motif / material / era / spatial idea, but every one stays loyal to Skybit:
tropical macaw, warm-gold coins, day/night sky, sandstone pillars, casual
arcade joy. Imported by render.py.

Concepts:
  1. LAGOON BOUTIQUE  — tropical sunset, brass & palm, dusk-sky boutique.
  2. NIGHT AVIARY     — indigo constellation jewel-box, gold filigree, glass.
  3. SKY TEMPLE       — sandstone pillar shop, carved gold inlay, warm stone.
  4. CLOUD NINE       — bright day-sky cloud shop, candy-gloss premium, airy.
  5. SKYLINER         — art-deco travel-poster, gold linework, teal/coral.
"""
import math
import pygame

from game.config import W, H
from game.draw import lerp_color, rounded_rect, UI_CREAM, NEAR_BLACK, WHITE
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE
from game.surprise_box_variants import _draw_qmark

import render as R  # the harness primitives + composer
from render import (vgrad_rect, hgrad_rect, soft_glow, drop_shadow,
                    gradient_text, coin_glyph, facet_gem, chip, inset_disc,
                    metal_rim, inner_bevel, gold_rule, thumb,
                    Concept, EQUIPPED_ID, SECRET_ID, BALANCE,
                    header_titlebar, balance_capsule, underline_tabs,
                    back_pill, modal_skeleton, _cost, _rarity, _name)


# =============================================================================
# 1. LAGOON BOUTIQUE — warm tropical sunset / lagoon boutique
#    Loyalty: biome SUNSET/GOLDEN-HOUR sky stops, warm sandstone, gold coins.
#    Motif: brass-railed dusk vitrine shelves; each card a warm cream "menu
#    plaque" on a teak board with a brass top-rail and a hanging palm sprig.
# =============================================================================
class LagoonBoutique(Concept):
    NAME = "LAGOON BOUTIQUE"
    DESC = "Tropical dusk · brass & teak · palm-shaded vitrine"
    # dusk lagoon: indigo top -> rose -> warm amber horizon (biome SUNSET feel)
    BG = ((46, 28, 78), (120, 52, 96), (214, 96, 92), (255, 168, 96))
    STARS = True
    star_t = 1.2
    GOLD = (255, 206, 120)
    GOLD_PALE = (255, 232, 180)
    GOLD_DEEP = (150, 92, 36)
    TITLE_TOP = (255, 244, 200)
    TITLE_BOT = (255, 150, 70)
    TITLE_OUT = (120, 40, 30)
    TABS = ("PARROTS", "ANIMALS", "COSTUMES", "PARCELS")
    # Warm rarity world: sand / lagoon-teal / orchid / sunset-gold.
    RARITY = {
        "common":    {"gem": (224, 192, 140), "glow": (212, 168, 112), "deep": (120, 80, 44)},
        "rare":      {"gem": (96, 210, 198),  "glow": (60, 184, 178),  "deep": (16, 92, 96)},
        "epic":      {"gem": (224, 128, 196), "glow": (208, 96, 178),  "deep": (96, 32, 86)},
        "legendary": {"gem": (255, 176, 72),  "glow": (255, 142, 40),  "deep": (140, 72, 16)},
    }
    MYSTERY = {"gem": (236, 224, 206), "glow": (208, 188, 158), "deep": (96, 80, 64)}

    # teak board + cream plaque tones
    BOARD_T = (96, 58, 34)
    BOARD_B = (60, 34, 20)
    PLAQUE_T = (250, 236, 206)
    PLAQUE_B = (228, 200, 158)

    def bg(self, surf):
        super().bg(surf)
        # warm horizon glow + faint palm silhouettes at the base for the lagoon
        glow = pygame.Surface((W, 160), pygame.SRCALPHA)
        for y in range(160):
            a = int(70 * (y / 160) ** 1.4)
            pygame.draw.line(glow, (255, 180, 110, a), (0, y), (W, y))
        surf.blit(glow, (0, H - 160), special_flags=pygame.BLEND_ADD)
        self._palms(surf)

    def _palms(self, surf):
        for px, ph, sgn in ((38, 70, 1), (W - 34, 84, -1)):
            base_y = H - 8
            pygame.draw.line(surf, (24, 16, 30), (px, base_y), (px - sgn * 8, base_y - ph), 4)
            for k in range(5):
                ang = -0.5 + k * 0.5
                ex = px - sgn * 8 + int(math.cos(ang) * 26) * sgn
                ey = base_y - ph + int(-abs(math.sin(ang)) * 10) - 6
                pygame.draw.line(surf, (20, 14, 26),
                                 (px - sgn * 8, base_y - ph), (ex, ey), 3)

    def header(self, surf):
        # Brass top-rail bar behind the title band for the boutique feel.
        rail = pygame.Rect(0, 0, W, 96)
        band = pygame.Surface((W, 96), pygame.SRCALPHA)
        for y in range(96):
            a = int(150 * (1 - y / 96))
            pygame.draw.line(band, (60, 30, 24, a), (0, y), (W, y))
        surf.blit(band, (0, 0))
        pygame.draw.line(surf, (*self.GOLD, 180), (0, 95), (W, 95), 2)
        pygame.draw.line(surf, (*self.GOLD_PALE, 90), (0, 92), (W, 92), 1)
        f = _font(28, True)
        gradient_text(surf, "STORE", f, (W // 2, 28),
                      self.TITLE_TOP, self.TITLE_BOT, outline=self.TITLE_OUT,
                      tracking=3)
        balance_capsule(self, surf, W // 2, 64,
                        cap_top=(70, 42, 22), cap_bot=(40, 22, 12))
        underline_tabs(self, surf, 112)

    def chip_colors(self, state):
        return {
            "price": ((86, 48, 18), (255, 206, 120), (255, 232, 180)),
            "equip": ((255, 232, 180), (120, 72, 32), (255, 206, 120)),
            "equipped": ((18, 56, 40), (104, 206, 150), (210, 255, 220)),
            "locked": ((120, 96, 78), (70, 52, 40), (130, 100, 76)),
        }[state]

    def card(self, surf, sid, rect, equipped):
        secret = sid == SECRET_ID
        pal = self.tier_pal(sid, secret)
        drop_shadow(surf, rect, 12, blur=6, alpha=140)
        # teak board backing
        surf.blit(vgrad_rect(rect.w, rect.h, 12, self.BOARD_T, self.BOARD_B), rect.topleft)
        metal_rim(surf, rect, 12, (60, 34, 20), (*self.GOLD, 220), w=2)
        # cream plaque inset (the menu plaque)
        plaque = rect.inflate(-14, -14)
        plaque.height = rect.h - 30
        plaque.y = rect.y + 8
        surf.blit(vgrad_rect(plaque.w, plaque.h, 8, self.PLAQUE_T, self.PLAQUE_B),
                  plaque.topleft)
        inner_bevel(surf, plaque, 8, light=(255, 250, 235), dark=(120, 80, 50),
                    la=120, da=70)
        # brass hanging-rail strip at the plaque top (the rarity PRIMARY cue)
        rail_w = plaque.w - 16
        rstrip = pygame.Surface((rail_w, 4), pygame.SRCALPHA)
        for sx in range(rail_w):
            hx = abs(sx - rail_w / 2) / (rail_w / 2)
            c = lerp_color(lerp_color(pal["gem"], WHITE, 0.3), pal["deep"], hx ** 1.3)
            rstrip.set_at((sx, 1), (*c, int(255 * (1 - 0.3 * hx ** 2))))
            rstrip.set_at((sx, 2), (*c, int(180 * (1 - 0.3 * hx ** 2))))
        surf.blit(rstrip, (plaque.x + 8, plaque.y + 5))
        soft_glow(surf, plaque.centerx, plaque.y + 6, 22, pal["glow"], 38, layers=4)
        # thumbnail on a warm inset oval shelf
        disc_cy = rect.y + 34
        self._shelf_disc(surf, rect.centerx, disc_cy, 26)
        if secret:
            _draw_qmark(surf, rect.centerx, disc_cy, 34, (90, 56, 32), (250, 238, 210), thick=2)
            name = "???"
        else:
            t = thumb(sid, 46)
            surf.blit(t, t.get_rect(center=(rect.centerx, disc_cy)))
            name = _name(sid)
        if _rarity(sid) == "legendary" and not secret:
            self._palm_sprig(surf, rect.x + 14, rect.y + 12)
        facet_gem(surf, rect.right - 16, rect.y + 16, 6, pal["gem"], pal["deep"],
                  mystery=secret)
        # name in warm ink on the plaque
        nimg = _font(13, True).render(name, True, (96, 56, 28))
        surf.blit(nimg, nimg.get_rect(center=(rect.centerx, rect.y + 62)))
        self.state_chip(surf, sid, rect.centerx, rect.y + 82, equipped, secret)
        if equipped:
            self._equipped_rim(surf, rect)

    def _shelf_disc(self, surf, cx, cy, r):
        disc = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        for i in range(r, 0, -1):
            c = lerp_color((92, 156, 150), (28, 70, 72), (i / r) ** 1.2)
            pygame.draw.circle(disc, (*c, 255), (r + 1, r + 1), i)
        pygame.draw.circle(disc, (0, 50, 50, 130), (r + 1, r + 1), r, 2)
        pygame.draw.circle(disc, (*self.GOLD, 110), (r + 1, r + 1), r - 1, 1)
        surf.blit(disc, (cx - r - 1, cy - r - 1))

    def _palm_sprig(self, surf, cx, cy):
        for k in range(3):
            ang = -0.9 + k * 0.6
            ex = cx + int(math.cos(ang) * 10)
            ey = cy + int(math.sin(ang) * 8)
            pygame.draw.line(surf, (*self.GOLD, 180), (cx, cy + 4), (ex, ey), 2)

    def _equipped_rim(self, surf, rect):
        halo = pygame.Surface((rect.w + 16, rect.h + 16), pygame.SRCALPHA)
        for k in range(4, 0, -1):
            pygame.draw.rect(halo, (*self.GOLD, int(22 * k / 4)),
                             (8 - k, 8 - k, rect.w + 2 * k, rect.h + 2 * k),
                             width=2, border_radius=12 + k)
        surf.blit(halo, (rect.x - 8, rect.y - 8), special_flags=pygame.BLEND_ADD)
        pygame.draw.rect(surf, self.GOLD, rect, width=2, border_radius=12)

    def back(self, surf):
        back_pill(self, surf, body_top=(80, 46, 26), body_bot=(48, 26, 14))

    def modal(self, surf, sid):
        modal_skeleton(self, surf, sid,
                       panel_top=(84, 50, 28), panel_bot=(48, 26, 14),
                       frame_deep=(60, 34, 20), frame_bright=(*self.GOLD, 230),
                       stage_top=(70, 130, 126), stage_bot=(24, 64, 66),
                       head_col=self.GOLD_PALE)

    def detail_card(self, surf, sid, rect):
        self.card(surf, sid, rect, sid == EQUIPPED_ID)


# =============================================================================
# 2. NIGHT AVIARY — indigo constellation jewel-box
#    Loyalty: night-sky biome (deep indigo, stars), gold-on-red title, gems.
#    Motif: a velvet jewel-box drawer; each card a glass cabochon panel with
#    fine gold FILIGREE corners and a constellation linking the gem.
# =============================================================================
class NightAviary(Concept):
    NAME = "NIGHT AVIARY"
    DESC = "Indigo jewel-box · gold filigree · glass cabochon"
    BG = ((6, 6, 28), (12, 10, 44), (20, 14, 60), (30, 18, 72))
    STARS = True
    star_t = 2.0
    GOLD = _GOLD_BRIGHT
    GOLD_PALE = _GOLD_PALE
    GOLD_DEEP = _GOLD_DEEP
    TITLE_TOP = (255, 240, 180)
    TITLE_BOT = (236, 170, 60)
    TITLE_OUT = _RED_OUTLINE
    RARITY = {
        "common":    {"gem": (210, 196, 226), "glow": (180, 168, 210), "deep": (78, 70, 110)},
        "rare":      {"gem": (98, 178, 248),  "glow": (66, 150, 240),  "deep": (24, 70, 130)},
        "epic":      {"gem": (188, 110, 244), "glow": (168, 84, 240),  "deep": (74, 30, 116)},
        "legendary": {"gem": (255, 196, 96),  "glow": (255, 160, 50),  "deep": (140, 86, 18)},
    }
    MYSTERY = {"gem": (220, 226, 236), "glow": (188, 206, 228), "deep": (86, 94, 116)}

    GLASS_T = (40, 36, 70)
    GLASS_B = (18, 16, 40)

    def header(self, surf):
        # velvet header band + a hairline gold frame around the whole screen
        band = pygame.Surface((W, 98), pygame.SRCALPHA)
        for y in range(98):
            a = int(120 * (1 - y / 98))
            pygame.draw.line(band, (30, 16, 56, a), (0, y), (W, y))
        surf.blit(band, (0, 0))
        pygame.draw.rect(surf, (*self.GOLD, 70), (3, 3, W - 6, H - 6),
                         width=1, border_radius=10)
        header_titlebar(self, surf, "STORE", tab_y=112, balance_y=64)

    def _filigree(self, surf, x, y, sgn_x, sgn_y, col):
        # a small gold scroll flourish at a card corner
        pygame.draw.arc(surf, col, (x - 6, y - 6, 12, 12),
                        0, math.pi / 2, 2)
        pygame.draw.line(surf, col, (x, y), (x + sgn_x * 9, y), 1)
        pygame.draw.line(surf, col, (x, y), (x, y + sgn_y * 9), 1)

    def card(self, surf, sid, rect, equipped):
        secret = sid == SECRET_ID
        pal = self.tier_pal(sid, secret)
        drop_shadow(surf, rect, 14, blur=6, alpha=150)
        # glass body
        surf.blit(vgrad_rect(rect.w, rect.h, 14, self.GLASS_T, self.GLASS_B, 250),
                  rect.topleft)
        # top glass sheen
        sheen = pygame.Surface((rect.w - 12, 18), pygame.SRCALPHA)
        for y in range(18):
            pygame.draw.line(sheen, (255, 255, 255, int(36 * (1 - y / 18))),
                             (0, y), (rect.w - 12, y))
        smask = pygame.Surface((rect.w - 12, 18), pygame.SRCALPHA)
        pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                         border_top_left_radius=12, border_top_right_radius=12)
        sheen.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(sheen, (rect.x + 6, rect.y + 4))
        # rarity cabochon AURA behind the disc + the disc
        disc_cy = rect.y + 34
        soft_glow(surf, rect.centerx, disc_cy, 30, pal["glow"], 60, layers=5)
        inset_disc(surf, rect.centerx, disc_cy, 26)
        if secret:
            _draw_qmark(surf, rect.centerx, disc_cy, 34, self.CREAM, NEAR_BLACK, thick=2)
            name = "???"
        else:
            t = thumb(sid, 46)
            surf.blit(t, t.get_rect(center=(rect.centerx, disc_cy)))
            name = _name(sid)
        # constellation: faint star-line from gem down to disc
        gem_xy = (rect.right - 16, rect.y + 16)
        pygame.draw.line(surf, (*pal["glow"], 90), gem_xy,
                         (rect.centerx + 16, disc_cy - 14), 1)
        for fx, fy in ((rect.right - 30, rect.y + 26), (rect.centerx + 20, disc_cy - 18)):
            pygame.draw.circle(surf, (*pal["gem"], 200), (fx, fy), 1)
        # gold filigree corners (PRIMARY frame ornament) — top two
        self._filigree(surf, rect.x + 8, rect.y + 8, 1, 1, (*self.GOLD_DEEP, 200))
        self._filigree(surf, rect.right - 8, rect.y + 8, -1, 1, (*self.GOLD_DEEP, 200))
        # gem badge (SECONDARY) seated in the top-right corner
        facet_gem(surf, gem_xy[0], gem_xy[1], 6, pal["gem"], pal["deep"], mystery=secret)
        metal_rim(surf, rect, 14, (*self.GOLD_DEEP, 200), (*self.GOLD, 170), w=2)
        nimg = _font(13, True).render(name, True, self.GOLD_PALE)
        nsh = _font(13, True).render(name, True, NEAR_BLACK); nsh.set_alpha(150)
        nr = nimg.get_rect(center=(rect.centerx, rect.y + 62))
        surf.blit(nsh, (nr.x + 1, nr.y + 1)); surf.blit(nimg, nr)
        self.state_chip(surf, sid, rect.centerx, rect.y + 82, equipped, secret)
        if equipped:
            halo = pygame.Surface((rect.w + 16, rect.h + 16), pygame.SRCALPHA)
            for k in range(4, 0, -1):
                pygame.draw.rect(halo, (*self.GOLD, int(20 * k / 4)),
                                 (8 - k, 8 - k, rect.w + 2 * k, rect.h + 2 * k),
                                 width=2, border_radius=14 + k)
            surf.blit(halo, (rect.x - 8, rect.y - 8), special_flags=pygame.BLEND_ADD)
            pygame.draw.rect(surf, self.GOLD, rect, width=2, border_radius=14)

    def back(self, surf):
        back_pill(self, surf)

    def modal(self, surf, sid):
        modal_skeleton(self, surf, sid,
                       panel_top=(34, 28, 60), panel_bot=(14, 12, 32),
                       frame_deep=lerp_color(self.GOLD, NEAR_BLACK, 0.45),
                       frame_bright=(*self.GOLD, 230),
                       stage_top=(26, 22, 48), stage_bot=(10, 9, 24),
                       head_col=self.GOLD_PALE)

    def detail_card(self, surf, sid, rect):
        self.card(surf, sid, rect, sid == EQUIPPED_ID)


# =============================================================================
# 3. SKY TEMPLE — sandstone pillar shop with carved gold inlay
#    Loyalty: the game's own SANDSTONE PILLARS + biome stone palette, warm
#    daylight stone. Motif: each card is a carved stone tablet between two
#    fluted pillar edges, with a sunlit accent band and gold inlay glyphs.
# =============================================================================
class SkyTemple(Concept):
    NAME = "SKY TEMPLE"
    DESC = "Sandstone tablets · fluted pillars · carved gold inlay"
    # warm day sky above warm stone (biome DAY/GOLDEN-HOUR feel)
    BG = ((70, 120, 188), (150, 150, 170), (196, 158, 120), (150, 110, 78))
    STARS = False
    GOLD = (255, 214, 130)
    GOLD_PALE = (255, 236, 188)
    GOLD_DEEP = (146, 96, 38)
    TITLE_TOP = (255, 246, 206)
    TITLE_BOT = (210, 150, 70)
    TITLE_OUT = (96, 54, 28)
    RARITY = {
        "common":    {"gem": (226, 196, 146), "glow": (210, 174, 120), "deep": (120, 84, 46)},
        "rare":      {"gem": (104, 196, 214), "glow": (66, 168, 192),  "deep": (24, 86, 102)},
        "epic":      {"gem": (200, 120, 210), "glow": (180, 92, 200),  "deep": (84, 36, 96)},
        "legendary": {"gem": (255, 184, 72),  "glow": (255, 150, 44),  "deep": (146, 80, 18)},
    }
    MYSTERY = {"gem": (240, 230, 212), "glow": (214, 200, 172), "deep": (110, 94, 70)}

    STONE_L = (224, 196, 156)
    STONE_M = (188, 156, 116)
    STONE_D = (120, 92, 64)

    def bg(self, surf):
        super().bg(surf)
        # a colonnade of faint fluted pillar silhouettes behind the grid
        for px in range(20, W, 70):
            col = pygame.Surface((40, H), pygame.SRCALPHA)
            for x in range(40):
                shade = 1 - abs(x - 20) / 20
                a = int(40 * shade)
                pygame.draw.line(col, (150, 116, 80, a), (x, 120), (x, H - 30))
            surf.blit(col, (px, 0))

    def _stone_panel(self, w, h, radius):
        body = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(h):
            f = y / max(1, h - 1)
            if f < 0.5:
                c = lerp_color(self.STONE_L, self.STONE_M, f * 2)
            else:
                c = lerp_color(self.STONE_M, self.STONE_D, (f - 0.5) * 2)
            pygame.draw.line(body, c, (0, y), (w - 1, y))
        # subtle horizontal carve lines
        for cy in range(10, h, 16):
            pygame.draw.line(body, (110, 84, 56, 70), (6, cy), (w - 6, cy), 1)
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
        body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        return body

    def header(self, surf):
        # carved stone lintel header
        lintel = self._stone_panel(W - 16, 50, 10)
        surf.blit(lintel, (8, 6))
        pygame.draw.rect(surf, (*self.GOLD_DEEP, 220), (8, 6, W - 16, 50),
                         width=2, border_radius=10)
        f = _font(26, True)
        gradient_text(surf, "SKY  STORE", f, (W // 2, 30),
                      self.TITLE_TOP, self.TITLE_BOT, outline=self.TITLE_OUT,
                      tracking=2)
        balance_capsule(self, surf, W // 2, 74,
                        cap_top=(88, 60, 32), cap_bot=(54, 36, 18))
        underline_tabs(self, surf, 114)

    def chip_colors(self, state):
        return {
            "price": ((70, 44, 16), (255, 214, 130), (255, 236, 188)),
            "equip": ((255, 236, 188), (120, 78, 32), (255, 214, 130)),
            "equipped": ((18, 54, 36), (104, 200, 140), (210, 255, 220)),
            "locked": ((120, 100, 80), (78, 60, 44), (140, 110, 82)),
        }[state]

    def card(self, surf, sid, rect, equipped):
        secret = sid == SECRET_ID
        pal = self.tier_pal(sid, secret)
        drop_shadow(surf, rect, 10, blur=6, alpha=130)
        surf.blit(self._stone_panel(rect.w, rect.h, 10), rect.topleft)
        # fluted pillar edges left & right
        for ex, sgn in ((rect.x + 5, 1), (rect.right - 9, -1)):
            for k in range(3):
                pygame.draw.line(surf, (150, 116, 80), (ex + k * 2, rect.y + 6),
                                 (ex + k * 2, rect.bottom - 6), 1)
        metal_rim(surf, rect, 10, (96, 64, 36), (*self.GOLD, 210), w=2)
        # sunlit accent band at top (the carved sunlit edge) — rarity PRIMARY:
        # the inlay band glows the tier colour
        band_w = rect.w - 30
        band = pygame.Surface((band_w, 4), pygame.SRCALPHA)
        for sx in range(band_w):
            hx = abs(sx - band_w / 2) / (band_w / 2)
            c = lerp_color(lerp_color(pal["gem"], WHITE, 0.35), pal["deep"], hx ** 1.3)
            band.set_at((sx, 1), (*c, int(255 * (1 - 0.3 * hx ** 2))))
            band.set_at((sx, 2), (*c, int(170 * (1 - 0.3 * hx ** 2))))
        surf.blit(band, (rect.x + 15, rect.y + 18))
        soft_glow(surf, rect.centerx, rect.y + 19, 24, pal["glow"], 40, layers=4)
        # carved niche disc for the thumbnail
        disc_cy = rect.y + 38
        self._niche(surf, rect.centerx, disc_cy, 25)
        if secret:
            _draw_qmark(surf, rect.centerx, disc_cy, 32, (88, 60, 36), (244, 226, 196), thick=2)
            name = "???"
        else:
            t = thumb(sid, 44)
            surf.blit(t, t.get_rect(center=(rect.centerx, disc_cy)))
            name = _name(sid)
        facet_gem(surf, rect.right - 16, rect.y + 16, 6, pal["gem"], pal["deep"],
                  mystery=secret)
        # engraved name (dark inlay + gold top edge)
        nf = _font(13, True)
        nsh = nf.render(name, True, (84, 54, 30))
        ng = nf.render(name, True, self.GOLD_PALE)
        nr = ng.get_rect(center=(rect.centerx, rect.y + 64))
        surf.blit(nsh, (nr.x, nr.y + 1)); surf.blit(ng, nr)
        self.state_chip(surf, sid, rect.centerx, rect.y + 84, equipped, secret)
        if equipped:
            halo = pygame.Surface((rect.w + 16, rect.h + 16), pygame.SRCALPHA)
            for k in range(4, 0, -1):
                pygame.draw.rect(halo, (*self.GOLD, int(22 * k / 4)),
                                 (8 - k, 8 - k, rect.w + 2 * k, rect.h + 2 * k),
                                 width=2, border_radius=10 + k)
            surf.blit(halo, (rect.x - 8, rect.y - 8), special_flags=pygame.BLEND_ADD)
            pygame.draw.rect(surf, self.GOLD, rect, width=2, border_radius=10)

    def _niche(self, surf, cx, cy, r):
        disc = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        for i in range(r, 0, -1):
            c = lerp_color((150, 116, 82), (74, 52, 34), (i / r) ** 1.3)
            pygame.draw.circle(disc, (*c, 255), (r + 1, r + 1), i)
        pygame.draw.circle(disc, (50, 34, 20, 150), (r + 1, r + 1), r, 2)
        pygame.draw.circle(disc, (*self.GOLD, 110), (r + 1, r + 1), r - 1, 1)
        surf.blit(disc, (cx - r - 1, cy - r - 1))

    def back(self, surf):
        back_pill(self, surf, body_top=(96, 64, 34), body_bot=(58, 38, 20))

    def modal(self, surf, sid):
        # custom stone modal so the temple material reads in the confirm too
        scrim = pygame.Surface((W, H), pygame.SRCALPHA); scrim.fill((10, 6, 4, 180))
        surf.blit(scrim, (0, 0))
        secret = sid == SECRET_ID
        tier = _rarity(sid); pal = self.MYSTERY if secret else self.RARITY[tier]
        pw, ph = 256, 300
        panel = pygame.Rect((W - pw) // 2, (H - ph) // 2, pw, ph)
        drop_shadow(surf, panel, 16, blur=8, alpha=170)
        surf.blit(self._stone_panel(pw, ph, 16), panel.topleft)
        metal_rim(surf, panel, 16, (96, 64, 36), (*self.GOLD, 230), w=2)
        cx = panel.centerx
        head = _font(13, True).render("CONFIRM  PURCHASE", True, (84, 54, 30))
        surf.blit(head, head.get_rect(center=(cx + 1, panel.y + 25)))
        hg = _font(13, True).render("CONFIRM  PURCHASE", True, self.GOLD_PALE)
        surf.blit(hg, hg.get_rect(center=(cx, panel.y + 24)))
        gold_rule(surf, panel.x + 28, panel.right - 28, panel.y + 40, self.GOLD)
        stage = pygame.Rect(cx - 50, panel.y + 54, 100, 100)
        surf.blit(self._stone_panel(stage.w, stage.h, 12), stage.topleft)
        pygame.draw.rect(surf, (60, 40, 22, 180), stage, width=2, border_radius=12)
        disc_cy = stage.y + 42
        soft_glow(surf, cx, disc_cy, 40, pal["glow"], 60, layers=5)
        self._niche(surf, cx, disc_cy, 36)
        if secret:
            _draw_qmark(surf, cx, disc_cy, 48, (244, 226, 196), (60, 40, 22), thick=3)
            name = "???"
        else:
            t = thumb(sid, 62); surf.blit(t, t.get_rect(center=(cx, disc_cy)))
            name = _name(sid)
        facet_gem(surf, stage.right - 6, stage.y + 6, 7, pal["gem"], pal["deep"],
                  mystery=secret)
        ng = _font(17, True).render(name, True, self.GOLD_PALE)
        nsh = _font(17, True).render(name, True, (84, 54, 30))
        nr = ng.get_rect(center=(cx, panel.y + 170))
        surf.blit(nsh, (nr.x + 1, nr.y + 1)); surf.blit(ng, nr)
        rimg = _font(11, True).render("MYSTERY" if secret else tier.upper(),
                                      True, pal["gem"])
        surf.blit(rimg, rimg.get_rect(center=(cx, panel.y + 188)))
        fg, bg, rim = self.chip_colors("price")
        chip(surf, cx, panel.y + 212, f"{_cost(sid):,}", fg, bg, rim, h=28, coin=True)
        self._modal_buttons(surf, panel)

    def _modal_buttons(self, surf, panel):
        cx = panel.centerx
        bw, bh, gut = 102, 38, 16
        by = panel.bottom - 30
        nx = cx - (bw * 2 + gut) // 2
        cancel = pygame.Rect(nx, by - bh // 2, bw, bh)
        buy = pygame.Rect(nx + bw + gut, by - bh // 2, bw, bh)
        surf.blit(vgrad_rect(bw, bh, bh // 2, (110, 86, 58), (74, 54, 34)), cancel.topleft)
        pygame.draw.rect(surf, (150, 118, 82), cancel, width=1, border_radius=bh // 2)
        ct = _font(14, True).render("CANCEL", True, (244, 230, 200))
        surf.blit(ct, ct.get_rect(center=cancel.center))
        bglow = pygame.Surface((bw + 10, bh + 10), pygame.SRCALPHA)
        for k in range(4, 0, -1):
            pygame.draw.rect(bglow, (*self.GOLD, int(24 * k / 4)),
                             (5 - k, 5 - k, bw + 2 * k, bh + 2 * k),
                             border_radius=bh // 2 + k)
        surf.blit(bglow, (buy.x - 5, buy.y - 5), special_flags=pygame.BLEND_ADD)
        surf.blit(vgrad_rect(bw, bh, bh // 2, lerp_color(self.GOLD, WHITE, 0.2),
                             self.GOLD_DEEP), buy.topleft)
        pygame.draw.rect(surf, self.GOLD_PALE, buy, width=1, border_radius=bh // 2)
        yt = _font(15, True).render("BUY", True, (60, 34, 12))
        surf.blit(yt, yt.get_rect(center=buy.center))

    def detail_card(self, surf, sid, rect):
        self.card(surf, sid, rect, sid == EQUIPPED_ID)


# =============================================================================
# 4. CLOUD NINE — bright day-sky cloud shop, candy-gloss premium
#    Loyalty: biome DAY sky (cyan->pale), warm gold, airy casual joy.
#    Motif: each card is a glossy rounded "cloud bubble" floating on a soft
#    cloud shelf; premium candy-gloss highlights; sky-bright but readable.
# =============================================================================
class CloudNine(Concept):
    NAME = "CLOUD NINE"
    DESC = "Day-sky clouds · candy-gloss bubbles · airy premium"
    BG = ((86, 168, 230), (140, 200, 240), (190, 224, 246), (224, 240, 250))
    STARS = False
    GOLD = (255, 196, 70)
    GOLD_PALE = (255, 228, 150)
    GOLD_DEEP = (196, 130, 24)
    TITLE_TOP = (255, 248, 210)
    TITLE_BOT = (255, 168, 60)
    TITLE_OUT = (190, 78, 30)
    CREAM = (255, 252, 244)
    RARITY = {
        "common":    {"gem": (255, 244, 224), "glow": (240, 224, 196), "deep": (150, 122, 86)},
        "rare":      {"gem": (96, 200, 255),  "glow": (60, 172, 244),  "deep": (20, 96, 150)},
        "epic":      {"gem": (200, 130, 255), "glow": (176, 100, 248), "deep": (92, 40, 142)},
        "legendary": {"gem": (255, 188, 64),  "glow": (255, 156, 36),  "deep": (170, 96, 16)},
    }
    MYSTERY = {"gem": (236, 244, 252), "glow": (208, 226, 244), "deep": (110, 128, 152)}

    BUBBLE_T = (255, 255, 255)
    BUBBLE_B = (216, 232, 244)

    def bg(self, surf):
        super().bg(surf)
        # soft cloud puffs
        for cx, cy, s, a in ((70, 200, 1.0, 60), (290, 320, 1.3, 50),
                             (180, 470, 1.6, 55), (60, 540, 1.0, 45),
                             (300, 560, 1.1, 45)):
            self._cloud(surf, cx, cy, s, a)

    def _cloud(self, surf, cx, cy, s, a):
        cloud = pygame.Surface((int(160 * s), int(70 * s)), pygame.SRCALPHA)
        for ox, oy, rr in ((40, 40, 30), (75, 32, 36), (115, 42, 28), (95, 50, 24)):
            pygame.draw.circle(cloud, (255, 255, 255, a),
                               (int(ox * s), int(oy * s)), int(rr * s))
        surf.blit(cloud, (cx - int(80 * s), cy - int(35 * s)))

    def header(self, surf):
        f = _font(28, True)
        gradient_text(surf, "STORE", f, (W // 2, 30),
                      self.TITLE_TOP, self.TITLE_BOT, outline=self.TITLE_OUT,
                      tracking=2)
        balance_capsule(self, surf, W // 2, 66,
                        cap_top=(255, 214, 120), cap_bot=(196, 130, 30))
        underline_tabs(self, surf, 112)

    def chip_colors(self, state):
        return {
            "price": ((120, 70, 12), (255, 212, 110), (255, 238, 170)),
            "equip": ((255, 248, 230), (236, 150, 40), (255, 212, 110)),
            "equipped": ((10, 70, 36), (78, 214, 130), (220, 255, 230)),
            "locked": ((118, 134, 150), (206, 220, 232), (150, 170, 190)),
        }[state]

    def card(self, surf, sid, rect, equipped):
        secret = sid == SECRET_ID
        pal = self.tier_pal(sid, secret)
        # cloud shelf under the bubble
        shelf = pygame.Surface((rect.w + 10, 30), pygame.SRCALPHA)
        for ox, rr in ((30, 16), (60, 20), (95, 18), (130, 15)):
            pygame.draw.circle(shelf, (255, 255, 255, 150), (ox, 20), rr)
        surf.blit(shelf, (rect.x - 5, rect.bottom - 18))
        drop_shadow(surf, rect, 18, blur=6, alpha=70)
        # glossy bubble body
        surf.blit(vgrad_rect(rect.w, rect.h, 18, self.BUBBLE_T, self.BUBBLE_B, 252),
                  rect.topleft)
        # candy top gloss
        gloss = pygame.Surface((rect.w - 16, 22), pygame.SRCALPHA)
        for y in range(22):
            pygame.draw.line(gloss, (255, 255, 255, int(150 * (1 - y / 22))),
                             (0, y), (rect.w - 16, y))
        gm = pygame.Surface((rect.w - 16, 22), pygame.SRCALPHA)
        pygame.draw.rect(gm, (255, 255, 255, 255), gm.get_rect(),
                         border_top_left_radius=16, border_top_right_radius=16)
        gloss.blit(gm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(gloss, (rect.x + 8, rect.y + 5))
        # rarity ring around the disc (PRIMARY cue — a glossy candy ring)
        disc_cy = rect.y + 34
        soft_glow(surf, rect.centerx, disc_cy, 28, pal["glow"], 70, layers=5)
        pygame.draw.circle(surf, pal["glow"], (rect.centerx, disc_cy), 28, 3)
        pygame.draw.circle(surf, lerp_color(pal["gem"], WHITE, 0.5),
                           (rect.centerx, disc_cy), 28, 1)
        self._sky_disc(surf, rect.centerx, disc_cy, 24)
        if secret:
            _draw_qmark(surf, rect.centerx, disc_cy, 32, (90, 110, 130), (245, 250, 255), thick=2)
            name = "???"
        else:
            t = thumb(sid, 44)
            surf.blit(t, t.get_rect(center=(rect.centerx, disc_cy)))
            name = _name(sid)
        facet_gem(surf, rect.right - 16, rect.y + 16, 6, pal["gem"], pal["deep"],
                  mystery=secret)
        # gold rim on the bubble
        pygame.draw.rect(surf, (*self.GOLD, 220), rect, width=2, border_radius=18)
        pygame.draw.rect(surf, (255, 255, 255, 160), rect.inflate(-4, -4),
                         width=1, border_radius=16)
        nimg = _font(13, True).render(name, True, (70, 92, 120))
        surf.blit(nimg, nimg.get_rect(center=(rect.centerx, rect.y + 62)))
        self.state_chip(surf, sid, rect.centerx, rect.y + 82, equipped, secret)
        if equipped:
            halo = pygame.Surface((rect.w + 16, rect.h + 16), pygame.SRCALPHA)
            for k in range(4, 0, -1):
                pygame.draw.rect(halo, (*self.GOLD, int(26 * k / 4)),
                                 (8 - k, 8 - k, rect.w + 2 * k, rect.h + 2 * k),
                                 width=2, border_radius=18 + k)
            surf.blit(halo, (rect.x - 8, rect.y - 8), special_flags=pygame.BLEND_ADD)
            pygame.draw.rect(surf, self.GOLD, rect, width=3, border_radius=18)

    def _sky_disc(self, surf, cx, cy, r):
        disc = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        for i in range(r, 0, -1):
            c = lerp_color((150, 206, 240), (86, 160, 220), (i / r) ** 1.2)
            pygame.draw.circle(disc, (*c, 255), (r + 1, r + 1), i)
        pygame.draw.circle(disc, (255, 255, 255, 160), (r + 1, r + 1), r, 1)
        surf.blit(disc, (cx - r - 1, cy - r - 1))

    def back(self, surf):
        r = pygame.Rect(0, 0, 160, 36); r.center = (W // 2, H - 26)
        drop_shadow(surf, r, 18, blur=4, alpha=60)
        surf.blit(vgrad_rect(r.w, r.h, 18, (255, 255, 255), (210, 228, 242), 250),
                  r.topleft)
        pygame.draw.rect(surf, (*self.GOLD, 220), r, width=2, border_radius=18)
        timg = _font(18, True).render("BACK", True, (190, 120, 28))
        surf.blit(timg, timg.get_rect(center=r.center))

    def modal(self, surf, sid):
        scrim = pygame.Surface((W, H), pygame.SRCALPHA); scrim.fill((30, 60, 90, 150))
        surf.blit(scrim, (0, 0))
        secret = sid == SECRET_ID
        tier = _rarity(sid); pal = self.MYSTERY if secret else self.RARITY[tier]
        pw, ph = 256, 300
        panel = pygame.Rect((W - pw) // 2, (H - ph) // 2, pw, ph)
        drop_shadow(surf, panel, 22, blur=8, alpha=120)
        surf.blit(vgrad_rect(pw, ph, 22, (255, 255, 255), (220, 234, 246), 255),
                  panel.topleft)
        pygame.draw.rect(surf, (*self.GOLD, 230), panel, width=3, border_radius=22)
        pygame.draw.rect(surf, (255, 255, 255, 180), panel.inflate(-6, -6),
                         width=1, border_radius=19)
        cx = panel.centerx
        head = _font(13, True).render("CONFIRM PURCHASE", True, (110, 70, 18))
        surf.blit(head, head.get_rect(center=(cx, panel.y + 24)))
        gold_rule(surf, panel.x + 28, panel.right - 28, panel.y + 40, self.GOLD)
        disc_cy = panel.y + 96
        soft_glow(surf, cx, disc_cy, 44, pal["glow"], 80, layers=6)
        pygame.draw.circle(surf, pal["glow"], (cx, disc_cy), 42, 4)
        pygame.draw.circle(surf, lerp_color(pal["gem"], WHITE, 0.5), (cx, disc_cy), 42, 1)
        self._sky_disc(surf, cx, disc_cy, 38)
        if secret:
            _draw_qmark(surf, cx, disc_cy, 50, (90, 110, 130), (245, 250, 255), thick=3)
            name = "???"
        else:
            t = thumb(sid, 62); surf.blit(t, t.get_rect(center=(cx, disc_cy)))
            name = _name(sid)
        facet_gem(surf, cx + 40, disc_cy - 36, 7, pal["gem"], pal["deep"], mystery=secret)
        nimg = _font(17, True).render(name, True, (70, 92, 120))
        surf.blit(nimg, nimg.get_rect(center=(cx, panel.y + 168)))
        rimg = _font(11, True).render("MYSTERY" if secret else tier.upper(),
                                      True, lerp_color(pal["gem"], (60, 80, 110), 0.4))
        surf.blit(rimg, rimg.get_rect(center=(cx, panel.y + 186)))
        fg, bg, rim = self.chip_colors("price")
        chip(surf, cx, panel.y + 210, f"{_cost(sid):,}", fg, bg, rim, h=28, coin=True)
        # buttons
        bw, bh, gut = 102, 38, 16
        by = panel.bottom - 30
        nx = cx - (bw * 2 + gut) // 2
        cancel = pygame.Rect(nx, by - bh // 2, bw, bh)
        buy = pygame.Rect(nx + bw + gut, by - bh // 2, bw, bh)
        surf.blit(vgrad_rect(bw, bh, bh // 2, (236, 244, 250), (200, 216, 230)), cancel.topleft)
        pygame.draw.rect(surf, (150, 170, 190), cancel, width=1, border_radius=bh // 2)
        ct = _font(14, True).render("CANCEL", True, (90, 110, 130))
        surf.blit(ct, ct.get_rect(center=cancel.center))
        bglow = pygame.Surface((bw + 10, bh + 10), pygame.SRCALPHA)
        for k in range(4, 0, -1):
            pygame.draw.rect(bglow, (*self.GOLD, int(28 * k / 4)),
                             (5 - k, 5 - k, bw + 2 * k, bh + 2 * k),
                             border_radius=bh // 2 + k)
        surf.blit(bglow, (buy.x - 5, buy.y - 5), special_flags=pygame.BLEND_ADD)
        surf.blit(vgrad_rect(bw, bh, bh // 2, (255, 224, 130), (224, 146, 34)), buy.topleft)
        pygame.draw.rect(surf, (255, 244, 200), buy, width=1, border_radius=bh // 2)
        yt = _font(15, True).render("BUY", True, (90, 50, 8))
        surf.blit(yt, yt.get_rect(center=buy.center))

    def detail_card(self, surf, sid, rect):
        self.card(surf, sid, rect, sid == EQUIPPED_ID)


# =============================================================================
# 5. SKYLINER — art-deco travel-poster
#    Loyalty: warm gold, the macaw as the "airline mascot", sky/sunset palette,
#    but expressed as 1930s travel-poster deco linework. Motif: each card a
#    framed deco "ticket" with stepped gold corners, a sunburst behind the
#    thumbnail, and crisp deco rule lines. Teal/coral with gold.
# =============================================================================
class Skyliner(Concept):
    NAME = "SKYLINER"
    DESC = "Art-deco travel poster · sunburst · teal/coral & gold"
    BG = ((16, 44, 58), (22, 70, 84), (30, 96, 104), (40, 120, 120))
    STARS = False
    GOLD = (240, 198, 96)
    GOLD_PALE = (255, 232, 168)
    GOLD_DEEP = (150, 104, 36)
    TITLE_TOP = (255, 240, 184)
    TITLE_BOT = (228, 162, 72)
    TITLE_OUT = (150, 56, 44)
    CREAM = (244, 236, 216)
    # deco rarity world: ivory / teal / coral-rose / gold
    RARITY = {
        "common":    {"gem": (228, 214, 184), "glow": (212, 196, 160), "deep": (124, 110, 80)},
        "rare":      {"gem": (86, 206, 200),  "glow": (52, 180, 178),  "deep": (16, 88, 92)},
        "epic":      {"gem": (240, 120, 130), "glow": (224, 88, 102),  "deep": (110, 30, 44)},
        "legendary": {"gem": (245, 196, 86),  "glow": (240, 162, 52),  "deep": (140, 92, 22)},
    }
    MYSTERY = {"gem": (236, 230, 216), "glow": (212, 206, 188), "deep": (112, 104, 84)}

    PANEL_T = (28, 64, 74)
    PANEL_B = (16, 42, 52)

    def bg(self, surf):
        super().bg(surf)
        # faint deco sunburst rays from the top centre
        cx, cy = W // 2, -40
        rays = pygame.Surface((W, H), pygame.SRCALPHA)
        for k in range(24):
            ang = math.pi * (k / 23)
            ex = cx + int(math.cos(ang) * 600)
            ey = cy + int(math.sin(ang) * 600)
            a = 16 if k % 2 == 0 else 6
            pygame.draw.line(rays, (255, 224, 150, a), (cx, cy), (ex, ey), 6)
        surf.blit(rays, (0, 0), special_flags=pygame.BLEND_ADD)
        # deco horizon rule near the base
        for i, yy in enumerate((H - 60, H - 48, H - 40)):
            pygame.draw.line(surf, (*self.GOLD, 60 - i * 14), (24, yy), (W - 24, yy), 2)

    def header(self, surf):
        # deco header plate with stepped corners + double rule
        plate = pygame.Rect(10, 6, W - 20, 94)
        surf.blit(vgrad_rect(plate.w, plate.h, 6, (24, 58, 68), (14, 38, 48), 235),
                  plate.topleft)
        self._deco_frame(surf, plate, self.GOLD)
        f = _font(24, True)
        gradient_text(surf, "SKYLINER", f, (W // 2, 26),
                      self.TITLE_TOP, self.TITLE_BOT, outline=self.TITLE_OUT,
                      tracking=4)
        # deco subtitle rules flanking a tiny wordmark, clear of the title
        sub = _font(9, True).render("C O I N   S T O R E", True, self.GOLD_PALE)
        sr = sub.get_rect(center=(W // 2, 44))
        surf.blit(sub, sr)
        for sgn in (-1, 1):
            x0 = W // 2 + sgn * (sr.w // 2 + 8)
            x1 = W // 2 + sgn * 100
            pygame.draw.line(surf, (*self.GOLD, 160), (x0, 44), (x1, 44), 1)
        balance_capsule(self, surf, W // 2, 76,
                        cap_top=(56, 40, 18), cap_bot=(34, 24, 12))
        underline_tabs(self, surf, 118)

    def _deco_frame(self, surf, rect, col, step=8):
        # stepped (chamfered) gold corner frame, deco style
        x, y, w, h = rect
        pts = [
            (x + step, y), (x + w - step, y), (x + w, y + step),
            (x + w, y + h - step), (x + w - step, y + h), (x + step, y + h),
            (x, y + h - step), (x, y + step),
        ]
        pygame.draw.polygon(surf, (*col, 230), pts, 2)
        pygame.draw.polygon(surf, (*self.GOLD_PALE, 110),
                            [(px, py - 1) for px, py in pts], 1)

    def chip_colors(self, state):
        return {
            "price": ((60, 40, 14), (240, 198, 96), (255, 232, 168)),
            "equip": ((244, 236, 216), (108, 70, 28), (240, 198, 96)),
            "equipped": ((14, 52, 48), (88, 198, 178), (200, 255, 244)),
            "locked": ((110, 132, 134), (50, 74, 80), (120, 150, 152)),
        }[state]

    def card(self, surf, sid, rect, equipped):
        secret = sid == SECRET_ID
        pal = self.tier_pal(sid, secret)
        drop_shadow(surf, rect, 8, blur=6, alpha=140)
        surf.blit(vgrad_rect(rect.w, rect.h, 8, self.PANEL_T, self.PANEL_B, 252),
                  rect.topleft)
        # restrained deco sunburst rays — short, faint, contained to a halo just
        # behind the disc so they read as a poster motif, not as visual noise.
        disc_cy = rect.y + 34
        burst = pygame.Surface((68, 68), pygame.SRCALPHA)
        for k in range(12):
            ang = 2 * math.pi * k / 12 + math.pi / 12
            ex = 34 + int(math.cos(ang) * 33)
            ey = 34 + int(math.sin(ang) * 33)
            a = 26 if k % 2 == 0 else 11
            pygame.draw.line(burst, (*pal["glow"], a), (34, 34), (ex, ey), 2)
        surf.blit(burst, (rect.centerx - 34, disc_cy - 34), special_flags=pygame.BLEND_ADD)
        soft_glow(surf, rect.centerx, disc_cy, 26, pal["glow"], 44, layers=4)
        # thumbnail on a dark deco disc (drawn on top of the burst so it reads clean)
        inset_disc(surf, rect.centerx, disc_cy, 24, tint=(8, 18, 22))
        if secret:
            _draw_qmark(surf, rect.centerx, disc_cy, 32, self.CREAM, NEAR_BLACK, thick=2)
            name = "???"
        else:
            t = thumb(sid, 44)
            surf.blit(t, t.get_rect(center=(rect.centerx, disc_cy)))
            name = _name(sid)
        facet_gem(surf, rect.right - 16, rect.y + 16, 6, pal["gem"], pal["deep"],
                  mystery=secret)
        # deco stepped gold frame
        self._deco_frame(surf, rect, self.GOLD, step=7)
        nimg = _font(13, True).render(name, True, self.GOLD_PALE)
        nsh = _font(13, True).render(name, True, NEAR_BLACK); nsh.set_alpha(150)
        nr = nimg.get_rect(center=(rect.centerx, rect.y + 64))
        surf.blit(nsh, (nr.x + 1, nr.y + 1)); surf.blit(nimg, nr)
        # rarity DECO RULE flanking the name (PRIMARY tier cue): twin tinted
        # tick-lines either side of the wordmark, classic travel-poster framing.
        for sgn in (-1, 1):
            x0 = rect.centerx + sgn * (nr.w // 2 + 6)
            x1 = rect.centerx + sgn * (rect.w // 2 - 14)
            pygame.draw.line(surf, pal["gem"], (x0, rect.y + 64), (x1, rect.y + 64), 2)
            pygame.draw.line(surf, lerp_color(pal["gem"], pal["deep"], 0.5),
                             (x0, rect.y + 67), (x1, rect.y + 67), 1)
        self.state_chip(surf, sid, rect.centerx, rect.y + 83, equipped, secret)
        if equipped:
            halo = pygame.Surface((rect.w + 16, rect.h + 16), pygame.SRCALPHA)
            for k in range(4, 0, -1):
                pygame.draw.rect(halo, (*self.GOLD, int(22 * k / 4)),
                                 (8 - k, 8 - k, rect.w + 2 * k, rect.h + 2 * k),
                                 width=2, border_radius=8 + k)
            surf.blit(halo, (rect.x - 8, rect.y - 8), special_flags=pygame.BLEND_ADD)
            self._deco_frame(surf, rect, self.GOLD, step=7)
            pygame.draw.rect(surf, self.GOLD, rect.inflate(-4, -4),
                             width=1, border_radius=6)

    def back(self, surf):
        back_pill(self, surf, body_top=(28, 60, 68), body_bot=(16, 40, 48))

    def modal(self, surf, sid):
        scrim = pygame.Surface((W, H), pygame.SRCALPHA); scrim.fill((6, 18, 22, 185))
        surf.blit(scrim, (0, 0))
        secret = sid == SECRET_ID
        tier = _rarity(sid); pal = self.MYSTERY if secret else self.RARITY[tier]
        pw, ph = 256, 300
        panel = pygame.Rect((W - pw) // 2, (H - ph) // 2, pw, ph)
        drop_shadow(surf, panel, 8, blur=8, alpha=170)
        surf.blit(vgrad_rect(pw, ph, 8, (28, 64, 74), (14, 38, 48), 255), panel.topleft)
        self._deco_frame(surf, panel, self.GOLD, step=12)
        pygame.draw.rect(surf, (*self.GOLD_DEEP, 160), panel.inflate(-8, -8),
                         width=1, border_radius=6)
        cx = panel.centerx
        head = _font(13, True).render("CONFIRM  PURCHASE", True, self.GOLD_PALE)
        surf.blit(head, head.get_rect(center=(cx, panel.y + 24)))
        gold_rule(surf, panel.x + 28, panel.right - 28, panel.y + 40, self.GOLD)
        disc_cy = panel.y + 100
        # big deco sunburst behind item
        burst = pygame.Surface((140, 140), pygame.SRCALPHA)
        for k in range(24):
            ang = 2 * math.pi * k / 24
            ex = 70 + int(math.cos(ang) * 66); ey = 70 + int(math.sin(ang) * 66)
            a = 40 if k % 2 == 0 else 16
            pygame.draw.line(burst, (*pal["glow"], a), (70, 70), (ex, ey), 4)
        surf.blit(burst, (cx - 70, disc_cy - 70), special_flags=pygame.BLEND_ADD)
        inset_disc(surf, cx, disc_cy, 38, tint=(8, 18, 22))
        if secret:
            _draw_qmark(surf, cx, disc_cy, 50, self.CREAM, NEAR_BLACK, thick=3)
            name = "???"
        else:
            t = thumb(sid, 62); surf.blit(t, t.get_rect(center=(cx, disc_cy)))
            name = _name(sid)
        facet_gem(surf, cx + 42, disc_cy - 38, 7, pal["gem"], pal["deep"], mystery=secret)
        nimg = _font(17, True).render(name, True, self.GOLD_PALE)
        surf.blit(nimg, nimg.get_rect(center=(cx, panel.y + 176)))
        rimg = _font(11, True).render("MYSTERY" if secret else tier.upper(),
                                      True, pal["gem"])
        surf.blit(rimg, rimg.get_rect(center=(cx, panel.y + 194)))
        fg, bg, rim = self.chip_colors("price")
        chip(surf, cx, panel.y + 216, f"{_cost(sid):,}", fg, bg, rim, h=28, coin=True)
        bw, bh, gut = 102, 38, 16
        by = panel.bottom - 28
        nx = cx - (bw * 2 + gut) // 2
        cancel = pygame.Rect(nx, by - bh // 2, bw, bh)
        buy = pygame.Rect(nx + bw + gut, by - bh // 2, bw, bh)
        surf.blit(vgrad_rect(bw, bh, bh // 2, (40, 78, 84), (24, 56, 62)), cancel.topleft)
        pygame.draw.rect(surf, (110, 150, 152), cancel, width=1, border_radius=bh // 2)
        ct = _font(14, True).render("CANCEL", True, self.CREAM)
        surf.blit(ct, ct.get_rect(center=cancel.center))
        bglow = pygame.Surface((bw + 10, bh + 10), pygame.SRCALPHA)
        for k in range(4, 0, -1):
            pygame.draw.rect(bglow, (*self.GOLD, int(24 * k / 4)),
                             (5 - k, 5 - k, bw + 2 * k, bh + 2 * k),
                             border_radius=bh // 2 + k)
        surf.blit(bglow, (buy.x - 5, buy.y - 5), special_flags=pygame.BLEND_ADD)
        surf.blit(vgrad_rect(bw, bh, bh // 2, lerp_color(self.GOLD, WHITE, 0.2),
                             self.GOLD_DEEP), buy.topleft)
        pygame.draw.rect(surf, self.GOLD_PALE, buy, width=1, border_radius=bh // 2)
        yt = _font(15, True).render("BUY", True, (50, 32, 8))
        surf.blit(yt, yt.get_rect(center=buy.center))

    def detail_card(self, surf, sid, rect):
        self.card(surf, sid, rect, sid == EQUIPPED_ID)


CONCEPTS = [
    LagoonBoutique(),
    NightAviary(),
    SkyTemple(),
    CloudNine(),
    Skyliner(),
]
