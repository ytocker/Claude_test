"""Umbrella power-up — icon exploration round 1 (5 concepts).

The Umbrella cancels the thunderstorm flap-dampening, so the icon must
read "umbrella / rain protection / keeps me dry" the instant the pickup
flies into view. Each candidate is a self-contained procedural draw:
supersampled at SS then smoothscaled down, matching the lottery/knight
icon family in game/entities.py (3-5 colour palette, thick ink outline,
gentle float-bob baked in).

Five distinct directions:
  U1  Canopy in a rain-bubble  — hero "umbrella in a soap bubble".
  U2  Bold pop canopy          — no bubble, jaunty tilt, two-tone panels.
  U3  Umbrella + deflected rain — drops splitting off the canopy edges.
  U4  Domed bubble-shield      — canopy over a Pip silhouette under a dome.
  U5  Handle-forward charm     — badge ring, barber-pole grip, compact top.

Each cell shows the icon at the true pickup footprint (POWERUP_R = 14 ->
~48 px) AND a 2x zoom for detail, on a dusk thunderstorm-sky swatch with
faint rain streaks so legibility is judged in context.

Output: docs/umbrella_powerup/round_1.png   (doc-only; not shipped)
"""
from __future__ import annotations

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

pygame.init()
pygame.display.set_mode((1, 1))

# ---------------------------------------------------------------------------
# Footprint + palette
# ---------------------------------------------------------------------------
# POWERUP_R = 14 in game/config.py; the visible pickup glyph reads a touch
# wider than the collision radius, so 48 px is the honest on-screen target.
PICKUP_PX = 48
SS = 7                                   # supersample factor (lottery uses 6)

# Canonical float-bob phase so every candidate sits like a real pickup
# rather than dead-centred (matches the sin(pulse*0.8)*2 idiom in-game).
BOB_PULSE = 1.15

INK        = (22, 18, 34)                # thick outer ink, shared family
INK_SOFT   = (46, 40, 64)
CANOPY_RED = (224,  68,  74)
CANOPY_RED_HI = (244, 120, 122)
CANOPY_RED_LO = (176,  40,  48)
CANOPY_CREAM = (250, 244, 222)
CANOPY_TEAL = ( 60, 176, 188)
CANOPY_TEAL_HI = (120, 214, 222)
CANOPY_TEAL_LO = ( 36, 128, 142)
HANDLE     = (118,  80,  46)
HANDLE_HI  = (164, 122,  78)
FERRULE    = (246, 222, 120)
DROP_BLUE  = (140, 196, 240)
DROP_BLUE_HI = (208, 236, 252)
BUBBLE_RIM = (210, 236, 250)
BUBBLE_FILL = (180, 214, 240)
SHIELD_AQUA = (150, 222, 232)
PIP_TEAL   = ( 70, 178, 110)
PIP_BELLY  = (236, 226, 140)
PIP_BEAK   = (244, 168,  60)
DRY_SHADOW = (30, 24, 48)


def _lerp(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# ---------------------------------------------------------------------------
# Shared canopy builder — a scalloped open umbrella on a supersampled surf.
# Returns nothing; draws into `big` centred on (cx, cy) in SS-space.
# ---------------------------------------------------------------------------
def _canopy(big, cx, cy, span, rise, panels, cols, ink_w,
            ferrule=True, hi_col=None):
    """Open canopy: an arched dome split into `panels` scalloped segments
    that alternate through `cols`. `span` = half-width, `rise` = dome height.
    Scallops drop below the rib line so the hem reads as fabric, not a bowl."""
    n = panels
    hem_y = cy
    # Rib tips along the hem, plus the scalloped dips between them.
    rib_x = [cx - span + (2 * span) * (i / n) for i in range(n + 1)]
    scallop_drop = span * 0.16

    for i in range(n):
        x0, x1 = rib_x[i], rib_x[i + 1]
        xm = (x0 + x1) / 2
        col = cols[i % len(cols)]
        # Dome top follows a circular arc; sample apex of this panel.
        def arc_y(x):
            t = (x - cx) / span                      # -1..1 across the dome
            return cy - rise * max(0.0, math.cos(t * math.pi / 2))
        poly = [
            (x0, hem_y),
            (xm, hem_y + scallop_drop),               # scalloped dip
            (x1, hem_y),
            (x1, arc_y(x1)),
            (xm, arc_y(xm) - rise * 0.05),
            (x0, arc_y(x0)),
        ]
        pygame.draw.polygon(big, col, poly)
        # Per-panel sheen near the apex.
        if hi_col:
            sh = [(x0, arc_y(x0)),
                  (xm, arc_y(xm) - rise * 0.05),
                  (xm, arc_y(xm) + rise * 0.22),
                  (x0, arc_y(x0) + rise * 0.22)]
            pygame.draw.polygon(big, hi_col, sh)
        pygame.draw.polygon(big, INK, poly, ink_w)

    # Apex highlight cap to seat the dome roundness.
    pygame.draw.line(big, INK, (cx - span, hem_y), (cx + span, hem_y), ink_w)

    if ferrule:
        tip_top = cy - rise - span * 0.30
        pygame.draw.line(big, INK, (cx, cy - rise + 2), (cx, tip_top),
                         max(ink_w, int(span * 0.07)))
        pygame.draw.circle(big, FERRULE, (int(cx), int(tip_top)),
                           int(span * 0.085))
        pygame.draw.circle(big, INK, (int(cx), int(tip_top)),
                           int(span * 0.085), ink_w)


def _j_handle(big, cx, top_y, length, span, ink_w, tilt=0.0):
    """Vertical shaft from the canopy apex down to a J-hook crook."""
    shaft_w = max(ink_w, int(span * 0.09))
    bx = cx + math.sin(tilt) * length * 0.4
    by = top_y + length
    pygame.draw.line(big, HANDLE_HI, (cx, top_y), (bx, by), shaft_w + ink_w)
    pygame.draw.line(big, HANDLE, (cx, top_y), (bx, by), shaft_w)
    # J-hook: a small arc curling back up.
    hook_r = span * 0.20
    rect = pygame.Rect(0, 0, int(hook_r * 2), int(hook_r * 2))
    rect.center = (int(bx - hook_r), int(by))
    pygame.draw.arc(big, HANDLE, rect, math.radians(-95), math.radians(180),
                    shaft_w)
    pygame.draw.arc(big, INK, rect, math.radians(-95), math.radians(180),
                    ink_w)
    pygame.draw.line(big, INK, (cx, top_y), (bx, by), ink_w)


def _bubble(big, cx, cy, r, ink_w, drops=True):
    """Translucent soap-bubble sphere with a rim + arc highlight and a
    couple of beading raindrops sliding off it."""
    # Soft fill via a stack of fading rings (cheap radial wash).
    for k in range(6):
        t = k / 5
        rr = int(r * (1 - t * 0.16))
        a = int(60 * (1 - t))
        s = pygame.Surface((rr * 2, rr * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*BUBBLE_FILL, a), (rr, rr), rr)
        big.blit(s, (cx - rr, cy - rr))
    # Rim.
    pygame.draw.circle(big, BUBBLE_RIM, (cx, cy), r, max(ink_w, int(r * 0.05)))
    pygame.draw.circle(big, INK, (cx, cy), r, ink_w)
    # Curved specular highlight, upper-left.
    hr = int(r * 0.74)
    hrect = pygame.Rect(0, 0, hr * 2, hr * 2)
    hrect.center = (cx, cy)
    pygame.draw.arc(big, (255, 255, 255), hrect,
                    math.radians(115), math.radians(168),
                    max(ink_w, int(r * 0.06)))
    # Small round glint.
    pygame.draw.circle(big, (255, 255, 255),
                       (int(cx - r * 0.42), int(cy - r * 0.46)),
                       int(r * 0.10))
    if drops:
        for (ox, oy, dr) in ((0.92, -0.30, 0.14), (0.80, 0.55, 0.10)):
            dx, dy = int(cx + r * ox), int(cy + r * oy)
            ddr = int(r * dr)
            pygame.draw.circle(big, DROP_BLUE, (dx, dy + ddr), ddr)
            pygame.draw.polygon(big, DROP_BLUE,
                                [(dx - ddr, dy + ddr), (dx, dy - ddr),
                                 (dx + ddr, dy + ddr)])
            pygame.draw.circle(big, DROP_BLUE_HI,
                               (dx - ddr // 3, dy + ddr - ddr // 3),
                               max(1, ddr // 3))
            pygame.draw.circle(big, INK, (dx, dy + ddr), ddr, ink_w)


def _raindrop(big, x, y, r, ink_w, col=DROP_BLUE):
    pygame.draw.circle(big, col, (int(x), int(y + r)), int(r))
    pygame.draw.polygon(big, col,
                        [(x - r, y + r), (x, y - r * 1.1), (x + r, y + r)])
    pygame.draw.circle(big, DROP_BLUE_HI,
                       (int(x - r / 3), int(y + r - r / 3)), max(1, int(r / 3)))
    pygame.draw.circle(big, INK, (int(x), int(y + r)), int(r), ink_w)
    pygame.draw.line(big, INK, (x - r, y + r), (x, y - r * 1.1), ink_w)
    pygame.draw.line(big, INK, (x + r, y + r), (x, y - r * 1.1), ink_w)


# ---------------------------------------------------------------------------
# The five candidate icon draws. Each returns a PICKUP_PX-square SRCALPHA
# surface (the icon already smoothscaled to footprint).
# ---------------------------------------------------------------------------
def _finish(big):
    w = big.get_width() // SS
    return pygame.transform.smoothscale(big, (w, w))


def icon_u1():
    """U1 — Classic canopy inside a rain-bubble (hero read)."""
    px = PICKUP_PX * SS
    big = pygame.Surface((px, px), pygame.SRCALPHA)
    c = px // 2
    ink = max(2, int(SS * 0.8))
    r = int(px * 0.43)
    _bubble(big, c, c, r, ink, drops=True)
    # Umbrella sits inside, slightly high so the handle has room.
    span = int(px * 0.27)
    rise = int(px * 0.22)
    uy = c - int(px * 0.02)
    _j_handle(big, c, uy, int(px * 0.30), span, ink)
    _canopy(big, c, uy, span, rise, 6,
            (CANOPY_RED, CANOPY_CREAM), ink,
            hi_col=CANOPY_RED_HI)
    return _finish(big)


def icon_u2():
    """U2 — Bold pop canopy, no bubble, jaunty tilt, two-tone panels."""
    px = PICKUP_PX * SS
    big = pygame.Surface((px, px), pygame.SRCALPHA)
    c = px // 2
    ink = max(3, int(SS * 1.05))
    span = int(px * 0.40)
    rise = int(px * 0.34)
    uy = c - int(px * 0.04)
    # Dry-spot shadow beneath.
    sh = pygame.Surface((px, px), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (*DRY_SHADOW, 110),
                        (c - span * 0.7, c + int(px * 0.30),
                         span * 1.4, int(px * 0.10)))
    big.blit(sh, (0, 0))
    big2 = pygame.Surface((px, px), pygame.SRCALPHA)
    cc = c
    _j_handle(big2, cc, uy, int(px * 0.40), span, ink)
    _canopy(big2, cc, uy, span, rise, 6,
            (CANOPY_RED, CANOPY_CREAM), ink, hi_col=CANOPY_RED_HI)
    rot = pygame.transform.rotate(big2, 12)
    big.blit(rot, rot.get_rect(center=(c, c)))
    return _finish(big)


def icon_u3():
    """U3 — Umbrella + rain visibly deflecting off the canopy edges."""
    px = PICKUP_PX * SS
    big = pygame.Surface((px, px), pygame.SRCALPHA)
    c = px // 2
    ink = max(2, int(SS * 0.85))
    span = int(px * 0.34)
    rise = int(px * 0.28)
    uy = c + int(px * 0.02)
    # Incoming streaks above the dome.
    for fx in (-0.22, 0.06, 0.30):
        x = c + px * fx
        pygame.draw.line(big, DROP_BLUE,
                         (x, c - px * 0.46), (x - px * 0.05, c - px * 0.30),
                         max(2, int(SS * 0.5)))
    _j_handle(big, c, uy, int(px * 0.30), span, ink)
    _canopy(big, c, uy, span, rise, 5,
            (CANOPY_TEAL, CANOPY_CREAM), ink, hi_col=CANOPY_TEAL_HI)
    # Drops splitting + bouncing off the two hem corners with motion ticks.
    for (hx, hy, dirx) in ((c - span, uy, -1), (c + span, uy, 1)):
        _raindrop(big, hx + dirx * px * 0.10, hy + px * 0.02,
                  int(px * 0.055), ink)
        _raindrop(big, hx + dirx * px * 0.20, hy + px * 0.16,
                  int(px * 0.045), ink)
        # motion ticks
        pygame.draw.line(big, DROP_BLUE_HI,
                         (hx + dirx * px * 0.05, hy - px * 0.02),
                         (hx + dirx * px * 0.13, hy + px * 0.04),
                         max(1, int(SS * 0.35)))
    return _finish(big)


def icon_u4():
    """U4 — Domed bubble-shield: canopy over a Pip silhouette under a dome."""
    px = PICKUP_PX * SS
    big = pygame.Surface((px, px), pygame.SRCALPHA)
    c = px // 2
    ink = max(2, int(SS * 0.8))
    # Faint hemispherical shield arc sheltering the lower half.
    shield_r = int(px * 0.42)
    srect = pygame.Rect(0, 0, shield_r * 2, shield_r * 2)
    srect.center = (c, c + int(px * 0.10))
    sh = pygame.Surface((px, px), pygame.SRCALPHA)
    pygame.draw.circle(sh, (*SHIELD_AQUA, 70),
                       (c, c + int(px * 0.10)), shield_r)
    big.blit(sh, (0, 0))
    pygame.draw.arc(big, SHIELD_AQUA, srect,
                    math.radians(8), math.radians(172),
                    max(2, int(SS * 0.55)))
    # Pip silhouette (tiny) sheltering underneath.
    py = c + int(px * 0.18)
    pygame.draw.circle(big, PIP_TEAL, (c, py), int(px * 0.12))
    pygame.draw.circle(big, PIP_BELLY, (c, py + int(px * 0.03)),
                       int(px * 0.07))
    pygame.draw.polygon(big, PIP_BEAK,
                        [(c + int(px * 0.10), py),
                         (c + int(px * 0.18), py + int(px * 0.02)),
                         (c + int(px * 0.10), py + int(px * 0.05))])
    pygame.draw.circle(big, INK, (c + int(px * 0.04), py - int(px * 0.02)),
                       max(1, int(SS * 0.4)))
    pygame.draw.circle(big, PIP_TEAL, (c, py), int(px * 0.12), ink)
    # Canopy up top, smaller, acting as the dome's crown.
    span = int(px * 0.30)
    rise = int(px * 0.20)
    uy = c - int(px * 0.18)
    _canopy(big, c, uy, span, rise, 6,
            (CANOPY_RED, CANOPY_CREAM), ink, hi_col=CANOPY_RED_HI,
            ferrule=True)
    return _finish(big)


def icon_u5():
    """U5 — Handle-forward charm: ringed badge, barber-pole grip, compact top."""
    px = PICKUP_PX * SS
    big = pygame.Surface((px, px), pygame.SRCALPHA)
    c = px // 2
    ink = max(2, int(SS * 0.85))
    # Badge ring.
    ring_r = int(px * 0.44)
    pygame.draw.circle(big, (250, 238, 206), (c, c), ring_r)
    pygame.draw.circle(big, FERRULE, (c, c), ring_r, max(2, int(SS * 0.7)))
    pygame.draw.circle(big, INK, (c, c), ring_r, ink)
    pygame.draw.circle(big, INK, (c, c), int(ring_r * 0.82), max(1, int(SS * 0.4)))
    # Compact canopy in the upper third.
    span = int(px * 0.24)
    rise = int(px * 0.15)
    uy = c - int(px * 0.10)
    _canopy(big, c, uy, span, rise, 5,
            (CANOPY_TEAL, CANOPY_CREAM), ink, hi_col=CANOPY_TEAL_HI,
            ferrule=True)
    # Prominent barber-pole curved handle below, dominating the read.
    sx, top_y = c, uy + int(px * 0.02)
    length = int(px * 0.34)
    shaft_w = max(ink, int(px * 0.10))
    bx, by = c - int(px * 0.02), top_y + length
    pygame.draw.line(big, HANDLE_HI, (sx, top_y), (bx, by), shaft_w + ink)
    pygame.draw.line(big, CANOPY_CREAM, (sx, top_y), (bx, by), shaft_w)
    # Barber-pole stripes along the shaft.
    steps = 5
    for k in range(steps):
        t0 = k / steps
        t1 = (k + 0.5) / steps
        ax, ay = sx + (bx - sx) * t0, top_y + (by - top_y) * t0
        bx2, by2 = sx + (bx - sx) * t1, top_y + (by - top_y) * t1
        pygame.draw.line(big, CANOPY_RED, (ax, ay), (bx2, by2),
                         shaft_w - ink)
    # J-hook crook.
    hook_r = int(px * 0.13)
    hrect = pygame.Rect(0, 0, hook_r * 2, hook_r * 2)
    hrect.center = (int(bx - hook_r), int(by))
    pygame.draw.arc(big, CANOPY_CREAM, hrect,
                    math.radians(-95), math.radians(180), shaft_w - ink)
    pygame.draw.arc(big, INK, hrect,
                    math.radians(-95), math.radians(180), ink)
    pygame.draw.line(big, INK, (sx, top_y), (bx, by), ink)
    return _finish(big)


CANDIDATES = [
    ("U1", "Canopy in rain-bubble", icon_u1),
    ("U2", "Bold pop canopy", icon_u2),
    ("U3", "Deflected rain", icon_u3),
    ("U4", "Domed bubble-shield", icon_u4),
    ("U5", "Handle charm", icon_u5),
]


# ---------------------------------------------------------------------------
# Dusk thunderstorm-sky swatch with faint rain streaks (context backdrop).
# ---------------------------------------------------------------------------
def _storm_swatch(w, h, seed):
    surf = pygame.Surface((w, h))
    top = (52, 50, 78)                  # bruised dusk indigo
    bot = (30, 30, 50)
    for y in range(h):
        surf.fill(_lerp(top, bot, y / max(1, h - 1)), (0, y, w, 1))
    # A muted ground band at the foot so it reads as a sky, not a void.
    pygame.draw.rect(surf, (38, 44, 46), (0, int(h * 0.88), w, h))
    rng = (seed * 2654435761) & 0xFFFFFFFF
    def rnd():
        nonlocal rng
        rng = (1103515245 * rng + 12345) & 0x7FFFFFFF
        return rng / 0x7FFFFFFF
    streaks = pygame.Surface((w, h), pygame.SRCALPHA)
    for _ in range(int(w * h / 900)):
        x = rnd() * w
        y = rnd() * h * 0.9
        ln = 6 + rnd() * 10
        pygame.draw.line(streaks, (190, 205, 235, 42),
                         (x, y), (x - 2, y + ln), 1)
    surf.blit(streaks, (0, 0))
    return surf


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "umbrella_powerup")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")

    # Bake float-bob: shift each finished icon a couple px on its swatch.
    bob = int(round(math.sin(BOB_PULSE * 0.8) * 2))

    cell_w, cell_h = 300, 320
    cols = 5
    pad = 16
    header_h = 84
    footer_h = 34

    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * pad
    sheet_h = header_h + cell_h + footer_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 30))

    def font(sz, bold=False):
        return pygame.font.SysFont("Arial", sz, bold=bold)

    title = font(26, bold=True).render(
        "UMBRELLA power-up — icon exploration  (round 1)", True,
        (240, 240, 246))
    sheet.blit(title, (pad, pad))
    sub = font(14).render(
        "Cancels thunderstorm flap-dampening. Each cell: dusk storm sky + "
        "rain streaks. Left = true pickup size (~48 px, POWERUP_R 14, "
        "float-bobbed); right = 2x zoom.",
        True, (170, 178, 192))
    sheet.blit(sub, (pad, pad + 32))
    sub2 = font(13).render(
        "U1 & U4 carry the umbrella-in-a-bubble idea.", True, (150, 175, 205))
    sheet.blit(sub2, (pad, pad + 52))

    for col, (tag, name, fn) in enumerate(CANDIDATES):
        x = pad + col * (cell_w + pad)
        y = header_h + pad
        swatch = _storm_swatch(cell_w, cell_h, seed=col + 3)
        sheet.blit(swatch, (x, y))
        pygame.draw.rect(sheet, (60, 66, 84), (x, y, cell_w, cell_h), 1)

        icon = fn()

        # True pickup size on the upper-left of the cell.
        true_cx = x + cell_w // 2 - PICKUP_PX // 2 - 8
        true_cy = y + cell_h // 2 - PICKUP_PX // 2 + bob
        sheet.blit(icon, (true_cx, true_cy))
        # ring + caption marking the honest footprint
        pygame.draw.circle(sheet, (255, 255, 255),
                           (true_cx + PICKUP_PX // 2,
                            true_cy + PICKUP_PX // 2 - bob),
                           PICKUP_PX // 2 + 4, 1)
        lbl = font(12).render("real pickup ~48px", True, (210, 220, 235))
        sheet.blit(lbl, (x + 10, y + cell_h - 24))

        # 2x zoom lower-right for detail.
        zoom = pygame.transform.smoothscale(icon, (PICKUP_PX * 3,
                                                    PICKUP_PX * 3))
        zx = x + cell_w - PICKUP_PX * 3 - 14
        zy = y + cell_h - PICKUP_PX * 3 - 30
        sheet.blit(zoom, (zx, zy))
        zl = font(12).render("3x zoom", True, (210, 220, 235))
        sheet.blit(zl, (zx + PICKUP_PX * 3 - 48, zy - 2))

        # Caption strip.
        cap = font(16, bold=True).render(f"{tag}  {name}", True,
                                         (245, 240, 230))
        sheet.blit(cap, (x + 8, header_h + pad + cell_h + 6))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
