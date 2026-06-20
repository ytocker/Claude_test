"""Round-1 exploration sheet for SKI GOGGLES (shades_ski).

Three wraparound-lens variants differing only in mirror gradient:
  A icy blue->purple   B orange sunset   C gold
Run headless: SDL_VIDEODRIVER=dummy python docs/shades/shades_ski/render.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import math
import pygame
pygame.init()

from game import parrot, store_skins


# ── shared geometry ──────────────────────────────────────────────────────────
# A single wide wraparound lens centred on the eye, taller than sunglasses, a
# chunky foam rim, a hard diagonal mirror-sheen, and a nylon strap toward the
# ear. Only the mirror gradient (top->bottom colours) varies between A/B/C.
_FOAM    = (40, 44, 60)            # dark frame/foam ring
_FOAM_D  = (22, 25, 38)
_FOAM_H  = (104, 110, 138)
_STRAP   = (228, 96, 52)           # bright nylon strap (warm so it never hides)
_STRAP_D = (150, 52, 28)
_STRAP_H = (255, 168, 110)


def _draw_ski(surf, cx, cy, eye_w, facing, mirror_top, mirror_bot, sheen_warm):
    f = facing
    k = lambda v: max(1, int(eye_w * v))
    w   = max(7, int(eye_w * 1.06))      # wide wraparound footprint
    h   = max(6, int(eye_w * 0.74))      # taller than sunglasses
    rim = k(0.13)
    rad = k(0.26)

    rect = pygame.Rect(0, 0, w, h)
    rect.center = (cx, cy)

    # ── nylon strap FIRST so the rim/lens overlap it cleanly at the joint ──
    # Strap leaves the ear-side rim and runs back toward the ear (-facing),
    # angled slightly down. Two bands keep it legible even at 22px.
    band = k(0.20)                       # full strap thickness
    rim_ear  = cx - f * (w // 2)
    rim_beak = cx + f * (w // 2)
    sy = cy + k(0.04)
    ear_x = cx - f * (w // 2 + k(0.50))
    ear_y = sy + k(0.16)
    pygame.draw.line(surf, _STRAP_D, (rim_ear, sy - k(0.02)),
                     (ear_x, ear_y), band + 2)
    pygame.draw.line(surf, _STRAP, (rim_ear, sy), (ear_x, ear_y), band)
    pygame.draw.line(surf, _STRAP_H, (rim_ear - f * k(0.04), sy - k(0.06)),
                     (ear_x - f * k(0.02), ear_y - k(0.05)), max(1, band // 3))
    # Tiny tri-glide buckle near the ear end.
    bx, by = ear_x + f * k(0.10), (sy + ear_y) // 2
    pygame.draw.line(surf, _FOAM_D, (bx, by - band // 2),
                     (bx, by + band // 2), max(1, k(0.05)))

    # ── chunky foam rim (rounded rect a little larger than the lens) ──
    frame = rect.inflate(rim * 2, rim * 2)
    pygame.draw.rect(surf, _FOAM_D, frame.inflate(2, 2),
                     border_radius=rad + rim + 1)
    pygame.draw.rect(surf, _FOAM, frame, border_radius=rad + rim)
    # Bright top-rim edge so the foam reads as a soft padded band, not a slab.
    pygame.draw.line(surf, _FOAM_H, (frame.left + rad, frame.top + 1),
                     (frame.right - rad, frame.top + 1), max(1, rim // 2))

    # ── mirrored lens: vertical gradient clipped to the rounded rect ──
    lens = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = (int(mirror_top[0] + (mirror_bot[0] - mirror_top[0]) * t),
             int(mirror_top[1] + (mirror_bot[1] - mirror_top[1]) * t),
             int(mirror_top[2] + (mirror_bot[2] - mirror_top[2]) * t), 255)
        pygame.draw.line(lens, c, (0, yy), (w, yy))
    clip = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(clip, (255, 255, 255, 255), clip.get_rect(),
                     border_radius=rad)
    lens.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(lens, rect.topleft)

    # Inner shadow at the top so the lens sits INTO the foam (depth read).
    pygame.draw.line(surf, (0, 0, 0, 70), (rect.left + rad, rect.top + 1),
                     (rect.right - rad, rect.top + 1), max(1, k(0.04)))

    # ── hard diagonal mirror-sheen sweep — the signature reflective cue ──
    # A bright wide band and a thin trailing band raked across the lens.
    sw = max(1, k(0.10))
    x0 = rect.left + w * 0.16
    pygame.draw.line(surf, (255, 255, 255), (x0, rect.bottom - 1),
                     (x0 + w * 0.30, rect.top + 1), sw)
    pygame.draw.line(surf, (255, 255, 255, 150),
                     (x0 + w * 0.34, rect.bottom - 1),
                     (x0 + w * 0.56, rect.top + 2), max(1, k(0.05)))
    # A warm/cool spark at the high corner reinforces the mirror tint.
    pygame.draw.circle(surf, sheen_warm,
                       (int(rect.left + w * 0.74), int(rect.top + h * 0.30)),
                       max(1, k(0.06)))


# ── three variants ───────────────────────────────────────────────────────────
def ski_A(surf, cx, cy, eye_w, facing=1):   # icy blue -> purple
    _draw_ski(surf, cx, cy, eye_w, facing,
              (188, 238, 250), (118, 96, 206), (220, 245, 255))


def ski_B(surf, cx, cy, eye_w, facing=1):   # orange sunset
    _draw_ski(surf, cx, cy, eye_w, facing,
              (255, 224, 150), (232, 88, 70), (255, 240, 200))


def ski_C(surf, cx, cy, eye_w, facing=1):   # gold mirror
    _draw_ski(surf, cx, cy, eye_w, facing,
              (255, 238, 160), (188, 130, 30), (255, 250, 210))


VARIANTS = [("A  icy blue->purple", ski_A),
            ("B  orange sunset", ski_B),
            ("C  gold", ski_C)]
PICKED = "A"   # implemented in draw.py


# ── harness helpers (from brief) ─────────────────────────────────────────────
def on_pip(draw_shades, angle=-10):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                          pygame.SRCALPHA)
    comp.blit(parrot._build_frame_bare(angle), (0, store_skins.PARROT_DY))
    draw_shades(comp, 50, 40, 22, 1)
    return parrot._add_outline(comp)


def product(draw_shades, c=160):
    s = pygame.Surface((c, c), pygame.SRCALPHA)
    draw_shades(s, c // 2, c // 2, 96, 1)
    return parrot._add_outline(s)


# ── compose the sheet ────────────────────────────────────────────────────────
def _label(sheet, font, text, x, y, col=(235, 238, 245)):
    sheet.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    sheet.blit(font.render(text, True, col), (x, y))


def main():
    pygame.font.init()
    font = pygame.font.SysFont("DejaVuSans", 15)
    small = pygame.font.SysFont("DejaVuSans", 12)
    big = pygame.font.SysFont("DejaVuSans", 22, bold=True)

    col_w, row_h = 300, 250
    sheet = pygame.Surface((col_w * 3, row_h + 70), pygame.SRCALPHA)
    sheet.fill((24, 28, 44))                     # navy store-card backdrop

    _label(sheet, big, "SKI GOGGLES  (shades_ski)  -  Round 1", 16, 12,
           (255, 255, 255))

    for i, (name, fn) in enumerate(VARIANTS):
        ox = i * col_w
        oy = 56
        picked = name.strip().startswith(PICKED)
        tag = name + ("   [IMPLEMENTED]" if picked else "")
        _label(sheet, font, tag, ox + 14, oy - 2,
               (120, 255, 160) if picked else (220, 224, 235))
        if picked:
            pygame.draw.rect(sheet, (120, 255, 160),
                             (ox + 6, oy + 18, col_w - 12, row_h - 8), 2,
                             border_radius=6)

        # Product shot (eye_w=96).
        prod = product(fn)
        sheet.blit(prod, (ox + 14, oy + 28))
        _label(sheet, small, "product  eye_w=96", ox + 14, oy + 28 + 164,
               (190, 196, 210))

        # On-Pip @22 native.
        pip = on_pip(fn)
        sheet.blit(pip, (ox + 192, oy + 30))
        _label(sheet, small, "@22 native", ox + 192, oy + 30 + 104,
               (190, 196, 210))

        # On-Pip @22 zoomed ~6x (nearest-neighbour).
        zoom = pygame.transform.scale(pip, (pip.get_width() * 5,
                                            pip.get_height() * 5))
        zoom = pygame.transform.scale(  # crop to head area to keep it on-tile
            zoom, (zoom.get_width(), zoom.get_height()))
        zsub = zoom.subsurface(pygame.Rect(180, 140, 110, 110)).copy()
        zbig = pygame.transform.scale(zsub, (118, 118))
        sheet.blit(zbig, (ox + 168, oy + 150))
        _label(sheet, small, "@22 zoom 6x", ox + 168, oy + 150 + 120,
               (190, 196, 210))

    out = os.path.join(os.path.dirname(__file__), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
