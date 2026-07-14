"""Headless round-2 render for the `backlight-glow` store tab-strip concept.

Round-1 failure: bloom core and active label were within ~5 luminance values in
R/G, so the text read as a bright-gold smear rather than lit glyphs.  Round-2
creates value separation through five concurrent changes:
  • cooler near-white-gold label above a warmer amber bloom
  • warm-dark drop shadow carves glyph edges out of the halo
  • core ellipse alphas halved so bloom sits below label luminance
  • bloom height trimmed to 30 px so soft outer ring completes inside the strip
  • thin non-additive underlay keeps the active state readable on lighter backdrops
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((360, 640), pygame.NOFRAME)

import sys
sys.path.insert(0, "/home/user/skybit")

from game.config import W, H
from game.hud import _font, _GOLD_PALE
from game.draw import NEAR_BLACK, WHITE
from game.store import _vgrad_panel, _drop_shadow, _gradient_text, _TAB_Y, _TABS, \
    _draw_chevron
import game.store_data as sd
import game.store as st

sd.load()
sd._STATE["wallet"] = 12340

# Label sits in cooler near-white-gold; bloom base is warmer amber — hue + value
# separation ensures the text reads crisp rather than melting into the halo.
_LABEL_ACTIVE = (255, 242, 205)
_SHADOW_COL   = (60,  35,  10)   # warm-dark silhouettes glyph edges against the bloom


def my_draw_tabs(self, surf):
    f = _font(12, True)
    pad, gap = 11, 6
    widths = [f.size(label)[0] + 2 * pad for label, _g in _TABS]
    content_w = sum(widths) + gap * (len(_TABS) - 1)
    full_vp = pygame.Rect(12, _TAB_Y - 13, W - 24, 26)
    overflow = content_w > full_vp.width
    chev = 18 if overflow else 0
    vp = pygame.Rect(full_vp.x + chev, full_vp.y, full_vp.width - 2 * chev, 26)
    max_scroll = max(0, content_w - vp.width)
    self.tab_scroll = max(0.0, min(self.tab_scroll, float(max_scroll)))
    self._tab_vp, self._tab_widths, self._tab_gap = vp, widths, gap

    prev_clip = surf.get_clip()
    surf.set_clip(vp)
    self.tab_rects = []
    cx = 0
    for i, (label, _g) in enumerate(_TABS):
        w = widths[i]
        r = pygame.Rect(round(vp.x + cx - self.tab_scroll), _TAB_Y - 13, w, 26)
        self.tab_rects.append(r)
        active = (i == self.tab)

        if active:
            # gh trimmed to 30 so the soft outer falloff ring completes inside
            # the 26 px strip rather than being clipped into a rectangle of light.
            gw, gh = r.w + 20, 30
            bloom_x = r.centerx - gw // 2
            bloom_y = _TAB_Y - gh // 2

            # Non-additive warm underlay drawn first at normal blend so the
            # active indicator survives any future brightening of the panel bg.
            underlay = pygame.Surface((gw, gh), pygame.SRCALPHA)
            underlay.fill((255, 200, 80, 25))
            surf.blit(underlay, (bloom_x, bloom_y))

            # Five stacked ellipses simulate radial falloff: outermost alphas
            # unchanged for halo softness; inner two core alphas cut ~50 % so
            # peak bloom luminance stays below label luminance (target ≥40 R gap).
            # Base hue shifted to warmer amber to contrast cooler label color.
            glow_surf = pygame.Surface((gw, gh), pygame.SRCALPHA)
            gcx, gcy = gw / 2, gh / 2
            rings = (
                ((gw,          gh        ), (255, 180,  55,  12)),   # outer halo — alpha unchanged
                ((gw * 0.78,   gh * 0.72), (255, 185,  65,  28)),   # second ring — alpha unchanged
                ((gw * 0.56,   gh * 0.52), (255, 192,  75,  55)),   # mid ring — alpha unchanged
                ((gw * 0.36,   gh * 0.34), (255, 200,  85,  55)),   # second-inner — was 90, now 55
                ((gw * 0.18,   gh * 0.18), (255, 218, 115,  70)),   # core — was 140, now 70
            )
            for (ew, eh), col in rings:
                erect = pygame.Rect(0, 0, round(ew), round(eh))
                erect.center = (round(gcx), round(gcy))
                pygame.draw.ellipse(glow_surf, col, erect)
            surf.blit(glow_surf, (bloom_x, bloom_y), special_flags=pygame.BLEND_ADD)

            # Drop shadow offset (+1, +1) in warm-dark so glyph edges are
            # silhouetted against the bloom even at its brightest center point.
            shadow_img = f.render(label, True, _SHADOW_COL)
            shadow_img.set_alpha(150)
            surf.blit(shadow_img, shadow_img.get_rect(center=(r.centerx + 1, r.centery + 1)))

            # Active label: cool near-white-gold on top — clearly separates from
            # the warmer amber halo both in hue and in value.
            timg = f.render(label, True, _LABEL_ACTIVE)
            surf.blit(timg, timg.get_rect(center=r.center))
        else:
            timg = f.render(label, True, _GOLD_PALE)
            timg.set_alpha(185)
            surf.blit(timg, timg.get_rect(center=r.center))
        cx += w + gap
    surf.set_clip(prev_clip)

    self.tab_chev_l = self.tab_chev_r = None
    if overflow and self.tab_scroll > 1:
        self.tab_chev_l = pygame.Rect(full_vp.x, full_vp.y, chev, 26)
        _draw_chevron(surf, self.tab_chev_l, -1)
    if overflow and self.tab_scroll < max_scroll - 1:
        self.tab_chev_r = pygame.Rect(full_vp.right - chev, full_vp.y, chev, 26)
        _draw_chevron(surf, self.tab_chev_r, 1)


st.StoreScene._draw_tabs = my_draw_tabs
scene = st.StoreScene()
scene.view = "category"
scene.tab = 0
scene.page = 0
surf = pygame.Surface((W, H))
scene.render(surf)

strip = surf.subsurface(pygame.Rect(0, 70, W, 42))
strip_tall = pygame.transform.smoothscale(strip, (W, 126))
lf = _font(11, True)
lt = lf.render("BACKLIGHT-GLOW  round_2", True, (255, 220, 80))
canvas = pygame.Surface((W, H + 16 + lt.get_height() + 4 + 126))
canvas.fill((8, 8, 20))
canvas.blit(surf, (0, 0))
canvas.blit(lt, (8, H + 8))
canvas.blit(strip_tall, (0, H + 16 + lt.get_height() + 4))

os.makedirs("/home/user/skybit/docs/store_tab_strip_redesign/backlight-glow", exist_ok=True)
out = "/home/user/skybit/docs/store_tab_strip_redesign/backlight-glow/round_2.png"
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
