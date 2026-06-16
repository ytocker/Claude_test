"""
Round-1 review renderer for KAPPA — the turtle-shelled water-dish imp
(Section 3 Japanese, GREEN-BAND #3 BRIGHT YELLOW-GREEN).

House style: chibi, flat saturated fills, hard ink keylines, the
dark-core -> flat-fill -> top-left rim-sheen TRIAD, a 1px outline grown from
the alpha mask, and supersample -> smoothscale. The creature is drawn once at
a high supersample factor onto a transparent surface, outlined from its own
alpha mask, then downscaled for the crisp large + 32px review tiles.

Standalone headless script: writes round_1.png next to itself. No game imports
so the review sheet stays reproducible in isolation.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import math
import pygame

# ── PINNED PALETTE (exact hexes from the locked Kappa brief) ────────────────
BODY      = (120, 194, 72)    # BRIGHT YELLOW-GREEN — most saturated, yellowest
BODY_D    = (72, 138, 56)     # deep-green shade (dark core)
SHEEN     = (176, 224, 140)   # top-left rim sheen
SHELL     = (150, 108, 52)    # turtle-bronze shell
SHELL_D   = (104, 74, 36)     # shell dark core (derived, same family)
SHELL_RIM = (196, 150, 90)    # shell sheen (derived)
DISH      = (120, 206, 200)   # dish-water turquoise
DISH_D    = (70, 150, 148)    # dish water dark
DISH_RIM  = (188, 238, 234)   # dish ripple highlight
BEAK      = (228, 188, 72)    # beak-gold
BEAK_D    = (176, 138, 44)
BAMBOO    = (196, 178, 110)   # bamboo-tan
BAMBOO_D  = (150, 132, 70)
BAMBOO_RIM= (224, 210, 156)
INK       = (24, 34, 24)      # keyline ink
WHITE     = (244, 248, 242)
CUKE      = (96, 168, 70)     # cucumber (a touch darker/greener than body)
CUKE_D    = (60, 122, 48)
CUKE_RIM  = (160, 210, 120)

SS = 4   # supersample factor for the large render


def _poly(surf, color, pts):
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])


def _ellipse(surf, color, cx, cy, rx, ry):
    pygame.draw.ellipse(surf, color, (int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2)))


def grow_outline(src, ink, px):
    """1px (scaled) ink keyline grown from the sprite's own alpha mask, so the
    silhouette POPs against any biome. We dilate by stamping the alpha mask in
    a ring of offsets behind the art."""
    mask = pygame.mask.from_surface(src)
    out = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    stamp = mask.to_surface(setcolor=(*ink, 255), unsetcolor=(0, 0, 0, 0))
    r = px
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                out.blit(stamp, (dx, dy))
    out.blit(src, (0, 0))
    return out


def draw_kappa(surf, ox, oy, s):
    """Draw the squat froggy kappa centred near (ox, oy). `s` is unit scale.
    Bottom-heavy: shell-hump + dish-crowned beaked head, webbed limbs."""

    def P(x, y):  # local unit coords -> surface px
        return (ox + x * s, oy + y * s)

    # ---- back turtle-shell hump (drawn first so it sits behind the body) ----
    sh_cx, sh_cy = 14, 18
    # shell dark core
    _ellipse(surf, SHELL_D, *P(sh_cx, sh_cy), 22 * s, 19 * s)
    # shell flat fill (offset down-right to leave a top-left rim)
    _ellipse(surf, SHELL, ox + (sh_cx + 1) * s, oy + (sh_cy + 1) * s, 20 * s, 17 * s)

    # ---- body: round, bottom-heavy froggy mass ----
    bx, by = 0, 8
    _ellipse(surf, BODY_D, *P(bx, by + 1), 20 * s, 22 * s)          # dark core
    _ellipse(surf, BODY, ox + (bx + 1.2) * s, oy + (by + 1.2) * s, 18 * s, 20 * s)  # fill
    _ellipse(surf, SHEEN, ox + (bx - 4) * s, oy + (by - 6) * s, 9 * s, 8 * s)       # TL rim sheen
    _ellipse(surf, BODY, ox + (bx + 1.2) * s, oy + (by + 4) * s, 17 * s, 17 * s)    # reclaim belly

    # belly plastron oval (slightly paler core breaks the body up)
    _ellipse(surf, DISH_D, *P(bx + 1, by + 9), 9 * s, 11 * s)
    _ellipse(surf, BAMBOO, ox + (bx + 1) * s, oy + (by + 10) * s, 7 * s, 9 * s)

    # ---- shell hexagon plate facets over the hump's visible upper edge ----
    plate_specs = [
        (7, 6, 5), (20, 4, 5), (28, 11, 5),
        (5, 16, 5), (18, 14, 5), (29, 22, 5),
    ]
    for hx, hy, hr in plate_specs:
        pts = [(sh_cx + hx + hr * math.cos(math.radians(a)),
                sh_cy + hy - 14 + hr * math.sin(math.radians(a)))
               for a in range(0, 360, 60)]
        # only the plates that fall on the body-right shell edge
        cx, cy = P(sh_cx + hx, sh_cy + hy - 14)
        if cx < ox - 1 * s:
            continue
        _poly(surf, SHELL_D, [P(px, py) for px, py in pts])
        pts2 = [(sh_cx + hx + (hr - 1) * math.cos(math.radians(a)) + 0.6,
                 sh_cy + hy - 14 + (hr - 1) * math.sin(math.radians(a)) + 0.6)
                for a in range(0, 360, 60)]
        _poly(surf, SHELL_RIM, [P(px, py) for px, py in pts2])

    # ---- webbed limbs (hard flat triad lobes) ----
    # back foot (further, behind), front foot, two webbed hands
    def web_lobe(cx, cy, rx, ry, ang):
        base = [(-rx, 0), (rx, 0), (rx * 0.6, ry), (0, ry * 1.25), (-rx * 0.6, ry)]
        rot = [(x * math.cos(ang) - y * math.sin(ang),
                x * math.sin(ang) + y * math.cos(ang)) for x, y in base]
        core = [P(cx + x, cy + y) for x, y in rot]
        _poly(surf, BODY_D, core)
        fill = [P(cx + x * 0.82 + 0.6, cy + y * 0.82 + 0.6) for x, y in rot]
        _poly(surf, BODY, fill)
        # web membrane notches as ink slits
        for t in (-0.4, 0.4):
            tip = P(cx + rx * t, cy + ry * 1.05)
            top = P(cx + rx * t * 0.5, cy + ry * 0.4)
            pygame.draw.line(surf, INK, top, tip, max(1, int(s)))

    web_lobe(-13, 27, 7, 6, 0.25)    # back/left foot
    web_lobe(11, 28, 8, 7, -0.2)     # front/right foot
    web_lobe(-19, 9, 6, 5, 1.15)     # left hand
    web_lobe(19, 11, 6, 5, -1.15)    # right hand (will hug cucumber)

    # ---- cucumber tucked in the right hand (signature kappa snack) ----
    cu = [(-9, -2), (10, -8), (12, -4), (-7, 2)]
    cucx, cucy = 22, 4
    _poly(surf, CUKE_D, [P(cucx + x, cucy + y) for x, y in cu])
    cu2 = [(-8, -2.5), (9, -7.5), (10.5, -4.5), (-6, 1)]
    _poly(surf, CUKE, [P(cucx + x, cucy + y) for x, y in cu2])
    pygame.draw.line(surf, CUKE_RIM, P(cucx - 7, cucy - 3), P(cucx + 9, cucy - 6.5), max(1, int(s)))

    # ---- head: chibi, big, sits high on the squat body ----
    hx, hy, hr = 0, -16, 16
    _ellipse(surf, BODY_D, *P(hx, hy), hr * s, (hr - 1) * s)
    _ellipse(surf, BODY, ox + (hx + 1) * s, oy + (hy + 1) * s, (hr - 2) * s, (hr - 3) * s)
    _ellipse(surf, SHEEN, ox + (hx - 6) * s, oy + (hy - 6) * s, 6 * s, 5 * s)

    # cheek/jaw flare — froggy wide lower face
    _ellipse(surf, BODY, ox + (hx) * s, oy + (hy + 6) * s, (hr - 1) * s, 11 * s)

    # ---- big round eyes ----
    for ex in (-7, 7):
        _ellipse(surf, WHITE, *P(hx + ex, hy - 2), 5.2 * s, 6 * s)
        _ellipse(surf, INK, ox + (hx + ex + ex * 0.06) * s, oy + (hy - 1) * s, 3.1 * s, 3.6 * s)
        _ellipse(surf, WHITE, ox + (hx + ex - 1.4) * s, oy + (hy - 3) * s, 1.2 * s, 1.2 * s)
    # heavy brow ridge (a touch of menace — scary-cute)
    pygame.draw.line(surf, BODY_D, P(hx - 12, hy - 7), P(hx - 2, hy - 5), max(2, int(2 * s)))
    pygame.draw.line(surf, BODY_D, P(hx + 12, hy - 7), P(hx + 2, hy - 5), max(2, int(2 * s)))

    # ---- beak (small, yellow, bird-like) ----
    bk = [(-5, 0), (5, 0), (0, 7)]
    bkx, bky = 0, 4
    _poly(surf, BEAK_D, [P(bkx + x, bky + y + 0.6) for x, y in bk])
    _poly(surf, BEAK, [P(bkx + x, bky + y) for x, y in bk])
    pygame.draw.line(surf, BEAK_D, P(bkx - 4, bky + 1.5), P(bkx + 4, bky + 1.5), max(1, int(s)))
    pygame.draw.line(surf, SHEEN, P(bkx - 4, bky - 0.3), P(bkx + 1, bky - 0.3), max(1, int(s)))

    # ---- water DISH on the crown (flat bowl + turquoise water ripple) ----
    dx, dy = 0, -28
    # green dish rim (the fleshy ring of the sara)
    _ellipse(surf, BODY_D, *P(dx, dy + 1), 13 * s, 6 * s)
    _ellipse(surf, BODY, ox + dx * s, oy + dy * s, 12 * s, 5 * s)
    # turquoise water inset
    _ellipse(surf, DISH_D, ox + dx * s, oy + (dy - 0.5) * s, 9.5 * s, 3.8 * s)
    _ellipse(surf, DISH, ox + dx * s, oy + (dy - 1) * s, 9 * s, 3.2 * s)
    # ripple highlight crescent
    pygame.draw.arc(surf, DISH_RIM,
                    (int(ox + (dx - 6) * s), int(oy + (dy - 3) * s), int(12 * s), int(6 * s)),
                    0.4, 2.4, max(1, int(s)))
    _ellipse(surf, DISH_RIM, ox + (dx - 3) * s, oy + (dy - 1.5) * s, 1.4 * s, 0.9 * s)

    # tuft of hair ringing the dish (kappa signature)
    for ang in range(200, 341, 28):
        a = math.radians(ang)
        x0 = dx + 12 * math.cos(a)
        y0 = dy + 5 * math.sin(a)
        pygame.draw.line(surf, BODY_D, P(x0, y0), P(x0 + 2 * math.cos(a), y0 + 3 * math.sin(a) - 2),
                         max(1, int(s)))


def draw_bamboo_pillar(surf, cx, top, bottom, w, cap=True):
    """Prop -> PILLAR mirror: segmented bamboo water-spout (shishi-odoshi).
    Repeatable node-banded shaft body; a tipping dipper pouring a water-ribbon
    is the detachable gap-edge cap. Symmetric on-axis — clean mirror."""
    half = w // 2
    seg_h = w * 1.6
    # shaft body
    pygame.draw.rect(surf, BAMBOO_D, (cx - half - 2, top, w + 4, bottom - top))
    pygame.draw.rect(surf, BAMBOO, (cx - half, top, w, bottom - top))
    # top-left rim sheen stripe
    pygame.draw.rect(surf, BAMBOO_RIM, (cx - half + 2, top, max(2, w // 5), bottom - top))
    # node bands (the repeatable banding)
    y = top + seg_h
    while y < bottom:
        pygame.draw.rect(surf, BAMBOO_D, (cx - half - 3, int(y) - 3, w + 6, 6))
        pygame.draw.line(surf, BAMBOO_RIM, (cx - half + 2, int(y) - 3), (cx - half + 2, int(y) + 3), 2)
        y += seg_h

    if cap:
        # ---- gap-edge cap: tipping bamboo dipper pouring a water-ribbon ----
        dip_y = top - 4
        # dipper arm (a slanted bamboo segment)
        pts = [(cx - half - 14, dip_y - 14), (cx + half + 6, dip_y - 26),
               (cx + half + 10, dip_y - 18), (cx - half - 10, dip_y - 6)]
        _poly(surf, BAMBOO_D, [(x + 2, y + 2) for x, y in pts])
        _poly(surf, BAMBOO, pts)
        pygame.draw.line(surf, BAMBOO_RIM, (cx - half - 12, dip_y - 12),
                         (cx + half + 4, dip_y - 24), 2)
        # poured water ribbon splashing INTO the gap
        rib_x = cx - half - 8
        rib = [(rib_x, dip_y - 4), (rib_x - 6, dip_y + 18), (rib_x + 2, dip_y + 40),
               (rib_x + 8, dip_y + 18), (rib_x + 6, dip_y - 2)]
        _poly(surf, DISH_D, [(x + 2, y) for x, y in rib])
        _poly(surf, DISH, rib)
        pygame.draw.line(surf, DISH_RIM, (rib_x, dip_y - 2), (rib_x - 2, dip_y + 30), 2)
        # splash droplets at the gap line
        for ddx, ddy, dr in [(-10, 44, 3), (8, 46, 2), (0, 52, 2)]:
            _ellipse(surf, DISH, rib_x + ddx, dip_y + ddy, dr, dr)


def build_kappa_sprite(unit_px):
    """Render the kappa at unit_px supersampled, outline from its alpha mask,
    return the high-res surface (caller smoothscales)."""
    s = unit_px * SS
    pad = int(30 * s / unit_px) if False else 0
    W = int(56 * unit_px)
    H = int(62 * unit_px)
    big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    # centre: head/dish near top, body bottom-heavy below
    draw_kappa(big, big.get_width() // 2, int(H * SS * 0.52), unit_px * SS)
    big = grow_outline(big, INK, SS)   # 1px @ final scale
    return big, (W, H)


def build_pillar_sprite(unit_px):
    W = int(40 * unit_px)
    H = int(96 * unit_px)
    big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    draw_bamboo_pillar(big, big.get_width() // 2,
                       int(20 * unit_px * SS), big.get_height(),
                       int(12 * unit_px * SS), cap=True)
    big = grow_outline(big, INK, SS)
    return big, (W, H)


def main():
    pygame.init()

    # checker backdrop so the alpha silhouette + sheen read honestly
    SHEET_W, SHEET_H = 760, 560
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((150, 178, 196))
    sky_a, sky_b = (152, 198, 232), (108, 156, 196)
    for y in range(SHEET_H):
        t = y / SHEET_H
        c = tuple(int(sky_a[i] + (sky_b[i] - sky_a[i]) * t) for i in range(3))
        pygame.draw.line(sheet, c, (0, y), (SHEET_W, y))

    font = pygame.font.SysFont("dejavusans", 18, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)

    def label(text, x, y, col=(20, 28, 24)):
        sheet.blit(font.render(text, True, (250, 252, 248)), (x + 1, y + 1))
        sheet.blit(font.render(text, True, col), (x, y))

    def slabel(text, x, y):
        sheet.blit(small.render(text, True, (250, 252, 248)), (x + 1, y + 1))
        sheet.blit(small.render(text, True, (24, 32, 26)), (x, y))

    title = pygame.font.SysFont("dejavusans", 22, bold=True)
    sheet.blit(title.render("KAPPA — turtle-shelled water-dish imp", True, (250, 252, 248)), (19, 13))
    sheet.blit(title.render("KAPPA — turtle-shelled water-dish imp", True, (22, 36, 24)), (18, 12))
    sheet.blit(small.render("GREEN-BAND #3 BRIGHT YELLOW-GREEN  ·  bottom-heavy froggy / turtle-shell / head-dish",
                            True, (24, 40, 26)), (18, 38))

    # ---- large creature ----
    big_c, _ = build_kappa_sprite(5.0)
    large_c = pygame.transform.smoothscale(big_c, (big_c.get_width() // SS, big_c.get_height() // SS))
    sheet.blit(large_c, (24, 70))
    label("creature", 70, 64 + large_c.get_height())

    # ---- large pillar mirror ----
    big_p, _ = build_pillar_sprite(4.4)
    large_p = pygame.transform.smoothscale(big_p, (big_p.get_width() // SS, big_p.get_height() // SS))
    sheet.blit(large_p, (330, 64))
    label("bamboo water-spout pillar", 300, 64 + large_p.get_height())
    slabel("dipper-cap pours into gap · node-banded shaft repeats", 296, 84 + large_p.get_height())

    # ---- 32px scale strip: creature + pillar shaft tile, on light & dark ----
    def to_32(big, target_h=32):
        w, h = big.get_size()
        scale = (target_h * SS) / h
        return pygame.transform.smoothscale(big, (max(1, int(w * scale / SS)), target_h))

    panel_x = 540
    # light panel
    pygame.draw.rect(sheet, (236, 240, 232), (panel_x, 70, 196, 210), border_radius=8)
    pygame.draw.rect(sheet, (40, 60, 44), (panel_x, 70, 196, 210), 2, border_radius=8)
    # dark panel
    pygame.draw.rect(sheet, (28, 36, 52), (panel_x, 300, 196, 200), border_radius=8)
    pygame.draw.rect(sheet, (90, 110, 130), (panel_x, 300, 196, 200), 2, border_radius=8)

    slabel("32px on day sky", panel_x + 10, 76)
    c32 = to_32(big_c, 36)
    sheet.blit(c32, (panel_x + 30, 100))
    p32 = to_32(big_p, 70)
    sheet.blit(p32, (panel_x + 110, 95))

    slabel("48px detail", panel_x + 10, 200)
    c48 = pygame.transform.smoothscale(big_c, (int(big_c.get_width() / SS * 0.62),
                                               int(big_c.get_height() / SS * 0.62)))
    sheet.blit(c48, (panel_x + 24, 150))

    slabel("32px on night sky", panel_x + 10, 308)
    sheet.blit(to_32(big_c, 36), (panel_x + 30, 340))
    sheet.blit(to_32(big_p, 70), (panel_x + 110, 332))
    # tiny 24px to stress the silhouette read
    slabel("24px silhouette", panel_x + 10, 432)
    sheet.blit(to_32(big_c, 24), (panel_x + 40, 456))
    sheet.blit(to_32(big_p, 48), (panel_x + 120, 450))

    # palette swatches
    swatches = [("body", BODY), ("shade", BODY_D), ("shell", SHELL),
                ("dish", DISH), ("beak", BEAK), ("bamboo", BAMBOO), ("sheen", SHEEN)]
    sx = 24
    sy = 506
    slabel("pinned palette:", sx, sy - 18)
    for name, col in swatches:
        pygame.draw.rect(sheet, col, (sx, sy, 30, 30), border_radius=4)
        pygame.draw.rect(sheet, (20, 28, 24), (sx, sy, 30, 30), 1, border_radius=4)
        sheet.blit(small.render(name, True, (250, 252, 248)), (sx + 1, sy + 31))
        sheet.blit(small.render(name, True, (22, 30, 24)), (sx, sy + 30))
        sx += 68

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
