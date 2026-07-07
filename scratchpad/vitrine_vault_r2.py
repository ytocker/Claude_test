import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys, random
sys.path.insert(0, "/home/user/skybit")
import pygame, math
pygame.init()
pygame.display.set_mode((1, 1))

from game import store_cards as sc
from game.store_cards import (
    soft_glow, cabochon, cabochon_glass, blit_thumb, _ribbon, _name_on,
    price_chip, facet_gem, gold_a_fill, top_sheen, drop_shadow, contact_shadow,
    bevel_rim, plain_text, m, RARITY, CABO_LO, CABO_HI,
    GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, GOLD_A_NUM,
)
from game.hud import _font, _GOLD_PALE, _GOLD_BRIGHT, _GOLD_DEEP

W, H = 360, 640
OBSIDIAN = (8, 6, 16)
DISC_X, DISC_Y, DISC_R = 180, 240, 70
PAL = RARITY["legendary"]

surf = pygame.Surface((W, H))
surf.fill(OBSIDIAN)

# ── Starfield ─────────────────────────────────────────────────────────────────
# Deterministic so the mockup is reproducible; two sizes give the vault depth
# without competing with the lit hero.
random.seed(42)
for _ in range(120):
    x = random.randint(0, W - 1)
    y = random.randint(0, H - 1)
    big = random.random() < 0.28
    v = random.randint(70, 150) + (35 if big else 0)
    col = (int(v * 0.9), int(v * 0.94), v)          # faint cool blue-white
    if big:
        pygame.draw.circle(surf, col, (x, y), 2)
    else:
        surf.set_at((x, y), col)

# ── God-rays (BEHIND the disc) ─────────────────────────────────────────────────
# Deep-amber additive layers: overlap only saturates UNDER the opaque disc, so
# the visible halo just outside the rim reads warm gold (~255,214,155) and
# feathers to pure obsidian — never a white blowout.
soft_glow(surf, DISC_X, DISC_Y, 225, (14, 11, 7), 60, layers=4)
soft_glow(surf, DISC_X, DISC_Y, 158, (48, 38, 26), 60, layers=6)
soft_glow(surf, DISC_X, DISC_Y, 108, (30, 23, 14), 60, layers=3)

# faint vertical shaft above the crown so the light reads as a beam from above
shaft = pygame.Surface((70, 200), pygame.SRCALPHA)
for yy in range(200):
    a = int(30 * (yy / 200) ** 1.4)
    pygame.draw.line(shaft, (58, 46, 30, a), (0, yy), (70, yy))
shaft_mask = pygame.Surface((70, 200), pygame.SRCALPHA)
for xx in range(70):
    a = int(255 * (1 - abs(xx - 35) / 35) ** 1.6)
    pygame.draw.line(shaft_mask, (255, 255, 255, a), (xx, 0), (xx, 199))
shaft.blit(shaft_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
surf.blit(shaft, (DISC_X - 35, DISC_Y - 200), special_flags=pygame.BLEND_ADD)

# ── Hero disc (ON TOP of the glow) ─────────────────────────────────────────────
cabochon(surf, DISC_X, DISC_Y, DISC_R, CABO_LO, CABO_HI, ring=PAL["gem"], ring_a=60)
blit_thumb(surf, "skin_lorikeet", DISC_X, DISC_Y, int(DISC_R * 1.5))
cabochon_glass(surf, DISC_X, DISC_Y, DISC_R, tint=PAL["gem"])

# ── Tier crown (gem + ribbon) floating above the disc ──────────────────────────
facet_gem(surf, DISC_X, 100, 16, PAL["gem"], PAL["deep"])
_ribbon(surf, "LEGENDARY", DISC_X, 138, 220, PAL)

# ── Name + price block below the disc ──────────────────────────────────────────
_name_on(surf, "RAINBOW LORIKEET", DISC_X, 338, 260)

# The price chip's in-game coin carries a hot specular that reads as raw white
# blocks at 1x; the store authors every chip at 2x and smoothscales down so the
# glint blends into gold. Mirror that here: draw the chip on a 2x scratch canvas,
# then one smoothscale down lands it as crisp gold, not a blown coin.
_cbw, _cbh = 260, 60
_cbig = pygame.Surface((_cbw * 2, _cbh * 2), pygame.SRCALPHA)
price_chip(_cbig, _cbw, _cbh, "12,000", 80, affordable=True)
_csmall = pygame.transform.smoothscale(_cbig, (_cbw, _cbh))
surf.blit(_csmall, (DISC_X - _cbw // 2, 392 - _cbh // 2))

# subtitle divider so the lower third reads as a product line, not a void
sub_f = _font(13, True)
plain_text(surf, "PERMANENT  ·  WARDROBE UNLOCK", sub_f, (DISC_X, 438),
           (150, 128, 78), shadow_a=0, tracking=1, weight=m(0.4))
for side in (-1, 1):
    x0 = DISC_X + side * 118
    pygame.draw.line(surf, (110, 88, 40), (x0, 438), (x0 + side * 40, 438), 1)

# ── Bottom action zone ─────────────────────────────────────────────────────────
# CANCEL: a ghost pill with a hairline gold keyline, clearly above the primary.
cancel = pygame.Rect(0, 0, 156, 46)
cancel.center = (DISC_X, 520)
ghost = pygame.Surface(cancel.size, pygame.SRCALPHA)
pygame.draw.rect(ghost, (20, 18, 34, 210), ghost.get_rect(), border_radius=23)
pygame.draw.rect(ghost, (255, 226, 150, 70), ghost.get_rect(), width=1,
                 border_radius=23)
surf.blit(ghost, cancel.topleft)
pygame.draw.rect(surf, (150, 128, 78), cancel, width=1, border_radius=23)
plain_text(surf, "CANCEL", _font(17, True), cancel.center, (214, 200, 168),
           shadow_a=120, tracking=1, weight=m(0.5))

# Solid dark bottom bar strip anchoring the primary action.
bar = pygame.Rect(0, 558, W, H - 558)
pygame.draw.rect(surf, (12, 10, 22), bar)
pygame.draw.line(surf, (120, 96, 44), (0, 558), (W, 558), 1)
pygame.draw.line(surf, (40, 34, 26), (0, 559), (W, 559), 1)

# BUY: the wide gold primary. Canonical Ramp-A gold fill; a top-third sheen
# capped low so the crown lightens without clipping to white; a double rim.
buy = pygame.Rect(0, 0, 300, 62)
buy.center = (DISC_X, 600)
drop_shadow(surf, buy, 31, blur=m(4), alpha=120, dy=m(2))
surf.blit(gold_a_fill(buy.w, buy.h, 31), buy.topleft)
top_sheen(surf, buy, 31, int(buy.h * 0.34), peak=46)
contact_shadow(surf, buy, 31, m(3), alpha=70)
pygame.draw.rect(surf, GOLD_A_RIM_DARK, buy, width=2, border_radius=31)
bevel_rim(surf, buy, 31, GOLD_A_RIM_DARK, (*GOLD_A_RIM_BRIGHT, 235), w=2)
plain_text(surf, "BUY", _font(26, True), buy.center, GOLD_A_NUM, shadow_a=0,
           tracking=2, weight=m(0.9), keyline=(255, 240, 196), kw=1)

pygame.image.save(surf, "/home/user/skybit/docs/confirm_purchase/vitrine-vault/round_2.png")
print("saved")
