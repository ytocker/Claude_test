"""arched-niche card concept — cathedral/tombstone aperture replacing circular dome.

Draws a rounded-rect-base + semicircular-crown (arch) in gold, fills the hero
thumbnail inside that silhouette, delivering BOTH a larger character AND a
larger/more architectural rim than the baseline circle.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
import math
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

CARD_W_SS, CARD_H_SS = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS  # 324, 200
inset = sc.m(sc._INSET)
rect_ss = pygame.Rect(inset, inset, CARD_W_SS - 2 * inset, CARD_H_SS - 2 * inset)


def render_baseline():
    sc._card_cache.clear()
    surf = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    sc.draw_card(surf, 'skin_mummy', rect_ss, equipped=False, secret=False)
    return surf


def draw_arch_niche_on(surf):
    """Draw a cathedral-arch character niche over the dome area.

    Arch geometry (SS coords):
    - Total niche: 120 wide × 150 tall
    - Crown: semicircle r=60 springing from shoulders at y=50 → apex at y=-10 (cropped to card)
    - Rect base: y=50..150, 120 wide → rect-base height = 100
    - Center x = 162 (card horizontal center)
    - Sill at y = 150 SS (fits above ribbon at y≈117? No — shifts ribbon down in this concept)
    - We target: crown apex y≈10, shoulders y≈70, sill y≈160
    """
    CX = 162
    ARCH_W = 120
    CROWN_R = 60          # semicircle at top
    SHOULDER_Y = 70       # where the arch curve meets the vertical sides
    SILL_Y = 160          # bottom of the niche
    BASE_H = SILL_Y - SHOULDER_Y   # 90 px rect portion

    # ── 1. Build arch silhouette mask ──────────────────────────────────────
    mask = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))

    # Rect base
    base_rect = pygame.Rect(CX - ARCH_W // 2, SHOULDER_Y, ARCH_W, BASE_H)
    pygame.draw.rect(mask, (255, 255, 255, 255), base_rect)

    # Semicircle crown (top half of circle centered at (CX, SHOULDER_Y))
    pygame.draw.circle(mask, (255, 255, 255, 255),
                       (CX, SHOULDER_Y), CROWN_R)

    # ── 2. Fill the niche body with gradient (CABO_C_HI at top → CABO_C_LO at bottom) ──
    body = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    body.fill((0, 0, 0, 0))

    LO = sc.CABO_C_LO   # (30, 33, 64)
    HI = sc.CABO_C_HI   # (9, 11, 30)  ← actually darker; use reversed for dome feel
    # Dome: center lit, edges dark. Use soft radial fill via scan-lines.
    arch_top = SHOULDER_Y - CROWN_R    # topmost pixel of arch
    arch_bot = SILL_Y
    total_h = arch_bot - arch_top
    for y in range(arch_top, arch_bot):
        frac = (y - arch_top) / total_h   # 0 = top, 1 = bottom
        # Radial feel: lightest at center-top (dome interior), darkest at edges/bottom
        c = tuple(int(LO[i] * (1 - frac) + HI[i] * frac) for i in range(3))
        # horizontal extent at this y
        if y < SHOULDER_Y:
            # in crown semicircle
            dy = SHOULDER_Y - y
            if dy > CROWN_R:
                continue
            half_w = int(math.sqrt(max(0, CROWN_R**2 - dy**2)))
        else:
            half_w = ARCH_W // 2
        if half_w > 0:
            pygame.draw.line(body, (*c, 255),
                             (CX - half_w, y), (CX + half_w, y))

    # Clip body to mask shape
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, (0, 0))

    # ── 3. Soft glow behind the arch (tier aura) ──────────────────────────
    glow = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    glow_cx = CX
    glow_cy = (arch_top + arch_bot) // 2
    glow_r = max(CROWN_R, BASE_H // 2) + 10
    for i in range(glow_r, 0, -3):
        alpha = int(35 * i / glow_r)
        pygame.draw.circle(glow, (100, 80, 40, alpha), (glow_cx, glow_cy), i)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)

    # ── 4. Hero thumbnail clipped to arch shape ───────────────────────────
    HERO_PX = 104
    hero_surf = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    hero_cy = (SHOULDER_Y + SILL_Y) // 2   # center in the rect base
    sc.blit_thumb(hero_surf, 'skin_mummy', CX, hero_cy, HERO_PX)
    # Clip to arch mask
    hero_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(hero_surf, (0, 0))

    # ── 5. Glass sheen on arch (top-left bright arc) ──────────────────────
    sheen = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    for angle_deg in range(-180, 0, 2):
        angle = math.radians(angle_deg)
        # Top-left quadrant brighter
        brightness = max(0, -math.cos(angle - math.pi * 1.3))
        alpha = int(80 * brightness)
        if alpha < 4:
            continue
        sx = int(CX + (CROWN_R - 8) * math.cos(angle))
        sy = int(SHOULDER_Y + (CROWN_R - 8) * math.sin(angle))
        pygame.draw.circle(sheen, (255, 248, 220, alpha), (sx, sy), 3)
    surf.blit(sheen, (0, 0))

    # ── 6. Gold arch bezel (3 strokes: keyline, gold, pale glint) ─────────
    def draw_arch_outline(target, cx, shoulder_y, crown_r, arch_w, base_h, color, width):
        # Crown arc
        crown_rect = pygame.Rect(cx - crown_r, shoulder_y - crown_r,
                                 crown_r * 2, crown_r * 2)
        pygame.draw.arc(target, color, crown_rect, 0, math.pi, width)
        # Left vertical side
        pygame.draw.line(target, color,
                         (cx - arch_w // 2, shoulder_y),
                         (cx - arch_w // 2, shoulder_y + base_h), width)
        # Right vertical side
        pygame.draw.line(target, color,
                         (cx + arch_w // 2, shoulder_y),
                         (cx + arch_w // 2, shoulder_y + base_h), width)
        # Bottom sill
        pygame.draw.line(target, color,
                         (cx - arch_w // 2, shoulder_y + base_h),
                         (cx + arch_w // 2, shoulder_y + base_h), width)

    # Keyline (dark contact)
    draw_arch_outline(surf, CX, SHOULDER_Y, CROWN_R + 3, ARCH_W + 6, BASE_H,
                      (*sc.CARD_RING_DEEP, 200), 2)
    # Gold band
    draw_arch_outline(surf, CX, SHOULDER_Y, CROWN_R + 1, ARCH_W + 2, BASE_H,
                      (*sc.CARD_RING_BRIGHT, 220), 3)
    # Pale glint (inner highlight)
    draw_arch_outline(surf, CX, SHOULDER_Y, CROWN_R - 2, ARCH_W - 4, BASE_H,
                      (255, 246, 200, 100), 1)


def render_concept():
    """Render the full card but replace the cabochon dome with the arch niche."""
    sc._card_cache.clear()

    # Suppress circle dome primitives, keep everything else
    orig_cabochon = sc.cabochon
    orig_cabochon_glass = sc.cabochon_glass
    orig_soft_glow = sc.soft_glow

    sc.cabochon = lambda *a, **kw: None
    sc.cabochon_glass = lambda *a, **kw: None
    sc.soft_glow = lambda *a, **kw: None

    # Also keep blit_thumb suppressed (we draw our own clipped thumb)
    orig_blit_thumb = sc.blit_thumb
    sc.blit_thumb = lambda *a, **kw: None

    surf = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    sc.draw_card(surf, 'skin_mummy', rect_ss, equipped=False, secret=False)

    sc.cabochon = orig_cabochon
    sc.cabochon_glass = orig_cabochon_glass
    sc.soft_glow = orig_soft_glow
    sc.blit_thumb = orig_blit_thumb
    sc._card_cache.clear()

    # Now draw the arch niche on top
    draw_arch_niche_on(surf)

    return surf


# ── Render ────────────────────────────────────────────────────────────────────
baseline_ss = render_baseline()
concept_ss = render_concept()

# ── Comparison sheet ──────────────────────────────────────────────────────────
GAP, PAD, LABEL_H, HEADER_H = 8, 16, 28, 40
sheet_w = PAD * 2 + 2 * CARD_W_SS + GAP
sheet_h = PAD * 2 + HEADER_H + LABEL_H + CARD_H_SS + GAP + LABEL_H + sc.CARD_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

fl = hud_font(14)
fh = hud_font(17)

title = fh.render("arched-niche  ·  baseline vs concept (skin_mummy)", True, (240, 224, 180))
sheet.blit(title, (sheet_w // 2 - title.get_width() // 2,
                   (HEADER_H - title.get_height()) // 2))

for i, (lbl_text, surf) in enumerate([
    ("BASELINE (2×)", baseline_ss),
    ("ARCHED-NICHE (2×)", concept_ss),
]):
    x = PAD + i * (CARD_W_SS + GAP)
    lbl = fl.render(lbl_text, True, (200, 210, 228))
    sheet.blit(lbl, (x + CARD_W_SS // 2 - lbl.get_width() // 2, PAD + HEADER_H))
    sheet.blit(surf, (x, PAD + HEADER_H + LABEL_H))

y1x = PAD + HEADER_H + LABEL_H + CARD_H_SS + GAP + LABEL_H
row_lbl = fl.render("at 1×  (162×100 final size)", True, (180, 180, 200))
sheet.blit(row_lbl, (PAD, y1x - LABEL_H))
for i, surf in enumerate([baseline_ss, concept_ss]):
    x = PAD + i * (CARD_W_SS + GAP)
    small = pygame.transform.smoothscale(surf, (sc.CARD_W, sc.CARD_H))
    sheet.blit(small, (x, y1x))

out = "docs/store_card_size/arched_niche/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
