"""SKATEBOARD pickup activation FX — split into two pieces so the
caption can linger at the top of the screen while the spike burst
follows Pip for a short beat without covering gameplay long-term.

* render_caption_overlay(cx, cy, rng_seed) — STATIC (W × H) surface
  with the tilted SKATEBOARD! caption near the top, POW! badge upper-
  right, and 4 corner ink slashes pointing at the original pickup
  position. Lives ~2.5 s.
* render_starburst_surface(rng_seed) — small (~320 × 320) surface
  with the 14-spike yellow/red starburst centered. scenes.py blits
  this each frame at Pip's CURRENT screen position so the burst
  appears to ride with him. Lives ~0.6 s — short by design so the
  game stays visible.

Original mockup: docs/screenshots/skateboard_variants/final/chosen.png
and tools/render_skateboard_final.py.
"""

import math
import random

import pygame

from game.config import W, H
from game.hud import _font


INK = (15, 15, 15)
YELLOW = (255, 220, 30)
RED = (230, 60, 50)
PLATE_RED = (220, 50, 40)
WHITE = (255, 255, 255)

# Self-contained starburst surface size — comfortably bigger than the
# spikes' outer radius (~165 px) so the polygon never clips.
BURST_SIZE = 360


def _gradient_text(text, size, top_col, bot_col, outline, outline_w=3):
    """Vertical-gradient text fill with thick outline (ported from
    tools/render_skateboard_variants.py)."""
    font = _font(size)
    mask = font.render(text, True, WHITE)
    bw, bh = mask.get_size()
    grad = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for y in range(bh):
        t = y / max(1, bh - 1)
        c = tuple(int(top_col[i] + (bot_col[i] - top_col[i]) * t)
                  for i in range(3))
        pygame.draw.line(grad, c, (0, y), (bw, y))
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    out = font.render(text, True, outline)
    pad = outline_w + 2
    surf = pygame.Surface((bw + pad * 2, bh + pad * 2), pygame.SRCALPHA)
    for dx in range(-outline_w, outline_w + 1):
        for dy in range(-outline_w, outline_w + 1):
            if dx * dx + dy * dy <= outline_w * outline_w and (dx or dy):
                surf.blit(out, (pad + dx, pad + dy))
    surf.blit(grad, (pad, pad))
    return surf


def render_caption_overlay(cx: int, cy: int,
                           rng_seed: int = 22) -> pygame.Surface:
    """Top-of-screen caption + POW! badge + 4 ink slashes pointing at
    the original pickup position. Returns a (W × H) surface; caller
    blits at (0, 0) with a decreasing alpha to fade out."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    # 4-corner ink speed-slashes pointing at the original pickup spot.
    for x0, y0 in ((20, 20), (W - 20, 20),
                   (20, H - 80), (W - 20, H - 80)):
        for off in range(3):
            dx = (cx - x0) * 0.18
            dy = (cy - y0) * 0.18
            ox = (-1 if x0 < cx else 1) * (off * 8)
            oy = off * 4
            pygame.draw.line(surf, INK,
                             (x0 + ox, y0 + oy),
                             (x0 + ox + dx, y0 + oy + dy), 4)

    # SKATEBOARD! caption on a red plate, tilted +5°.
    txt = _gradient_text("SKATEBOARD!", 42,
                         top_col=(255, 255, 110),
                         bot_col=(255, 180, 10),
                         outline=INK, outline_w=5)
    bw, bh = txt.get_width() + 30, txt.get_height() + 18
    composite = pygame.Surface((bw + 12, bh + 12), pygame.SRCALPHA)
    ccx = composite.get_width() // 2
    ccy = composite.get_height() // 2
    plate_rect = pygame.Rect(0, 0, bw, bh)
    plate_rect.center = (ccx + 4, ccy + 4)
    pygame.draw.rect(composite, PLATE_RED, plate_rect, border_radius=10)
    pygame.draw.rect(composite, INK, plate_rect, 4, border_radius=10)
    composite.blit(txt, txt.get_rect(center=(ccx, ccy)).topleft)
    rotated = pygame.transform.rotate(composite, 5)
    surf.blit(rotated, rotated.get_rect(center=(W // 2, 75)))

    # POW! badge upper-right, tilted +15°.
    pow_txt = _gradient_text("POW!", 32,
                             top_col=(255, 90, 90),
                             bot_col=(220, 30, 30),
                             outline=INK, outline_w=4)
    pow_rot = pygame.transform.rotate(pow_txt, 15)
    surf.blit(pow_rot, pow_rot.get_rect(center=(W - 60, 130)))

    return surf


# ── comic-inspired add-on overlays ──────────────────────────────────────────
#
# Each returns a screen-space (W × H) surface that callers blit at (0, 0)
# on top of `render_caption_overlay`'s output. Designed to extend (not
# replace) the existing SKATEBOARD! caption + POW! + corner slashes; the
# add-on sits behind the caption in z-order so the caption stays readable.


_PALETTE_KAPOW = (
    # (label, fill, accent, rot_deg, offset_from_pip)
    ("KAPOW!", (255, 220,  30), (230,  60,  50),  -8, (-120, -80)),  # NW
    ("BAM!",   (255, 100, 180), (255, 245, 200),  10, ( 130, -90)),  # NE
    ("SMASH!", ( 95, 200, 220), ( 30,  60, 120),  -6, (-140,  90)),  # SW
    ("WHAM!",  (255, 165,  60), (220,  40,  40),   8, ( 120,  95)),  # SE
)


def _jagged_burst(surf, cx, cy, ro, ri, spikes, fill, outline,
                  outline_w=3, jitter=0):
    rng = random.Random(int(cx) * 31 + int(cy) * 17 + spikes)
    pts = []
    for i in range(spikes * 2):
        ang = i * math.pi / spikes - math.pi / 2
        r = ro if i % 2 == 0 else ri
        if jitter:
            r += rng.randint(-jitter, jitter)
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    pygame.draw.polygon(surf, fill, pts)
    pygame.draw.polygon(surf, outline, pts, outline_w)
    return pts


def render_kapow_chorus_overlay(cx: int, cy: int,
                                  rng_seed: int = 22) -> pygame.Surface:
    """C1 — Onomatopoeia chorus. 4 comic-burst badges (KAPOW! / BAM! /
    SMASH! / WHAM!) placed in the four quadrants around Pip, each in
    its own jagged star burst with a distinct pop-art colorway.
    Stacks on top of the existing single POW! badge."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    for label, fill, accent, rot_deg, (dx, dy) in _PALETTE_KAPOW:
        bx = max(60, min(W - 60, cx + dx))
        by = max(110, min(H - 80, cy + dy))
        # Outer + inner jagged-edge bursts.
        _jagged_burst(surf, bx, by, 56, 30, spikes=10,
                      fill=fill, outline=INK, outline_w=4, jitter=4)
        _jagged_burst(surf, bx, by, 38, 22, spikes=10,
                      fill=accent, outline=INK, outline_w=2)
        # Text on the burst.
        size = 24 if len(label) > 4 else 28
        txt = _gradient_text(label, size,
                             top_col=(255, 250, 240),
                             bot_col=fill,
                             outline=INK, outline_w=3)
        rot = pygame.transform.rotate(txt, rot_deg)
        surf.blit(rot, rot.get_rect(center=(bx, by)))
    return surf


def render_halftone_aura_overlay(cx: int, cy: int,
                                   rng_seed: int = 22) -> pygame.Surface:
    """C2 — Lichtenstein halftone aura. Red+yellow dot field radiating
    from Pip, dots get LARGER toward the rim with a thin ink outline
    so they read as comic-panel pop dots even against bright sky.
    Densest at the rim (the "explosion edge") and sparse in the
    middle so Pip + the existing starburst stay visible."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    inner_r = 130   # start just outside the live 14-spike starburst
    outer_r = 260
    ring_step = 14
    for ring_idx, r in enumerate(range(inner_r, outer_r, ring_step)):
        t = (r - inner_r) / max(1, outer_r - inner_r)
        dot_r = int(4 + t * 5)
        alpha = int(235 - t * 90)  # 235 -> 145, stays punchy
        col = RED if ring_idx % 2 == 0 else YELLOW
        col_a = (*col, alpha)
        circumference = 2 * math.pi * r
        n = max(10, int(circumference / 24))
        phase = (ring_idx * math.pi / 5)
        for k in range(n):
            ang = phase + k * 2 * math.pi / n
            x = cx + math.cos(ang) * r
            y = cy + math.sin(ang) * r
            if -dot_r < x < W + dot_r and -dot_r < y < H + dot_r:
                # Thin ink rim so dots read against the sky.
                pygame.draw.circle(surf, (*INK, alpha),
                                   (int(x), int(y)), dot_r + 1)
                pygame.draw.circle(surf, col_a,
                                   (int(x), int(y)), dot_r)
    return surf


def render_speech_bubble_overlay(cx: int, cy: int,
                                   rng_seed: int = 22) -> pygame.Surface:
    """C3 — Round comic speech bubble tail-pointing from Pip's helmet
    with "SHRED!" gradient text. Cream fill + thick ink outline; the
    tail is a triangle wedge directed back at Pip. Placed upper-left
    so it doesn't overlap the SKATEBOARD! caption strip."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    # Bubble centre — upper-left of Pip, clamped onto the screen.
    bcx = max(110, min(W - 110, cx - 130))
    bcy = max(170, min(H - 110, cy - 90))
    # Tail triangle from the bubble edge toward Pip.
    ang = math.atan2(cy - bcy, cx - bcx)
    rx, ry = 95, 70  # bubble half-axes
    tail_anchor_x = bcx + math.cos(ang) * rx * 0.92
    tail_anchor_y = bcy + math.sin(ang) * ry * 0.92
    perp = ang + math.pi / 2
    spread = 22
    tail = [
        (tail_anchor_x + math.cos(perp) * spread,
         tail_anchor_y + math.sin(perp) * spread),
        (tail_anchor_x - math.cos(perp) * spread,
         tail_anchor_y - math.sin(perp) * spread),
        (cx, cy - 12),
    ]
    pygame.draw.polygon(surf, (255, 248, 220), tail)
    pygame.draw.polygon(surf, INK, tail, 4)
    # Bubble body — ellipse with thick black outline.
    bub_rect = pygame.Rect(bcx - rx, bcy - ry, rx * 2, ry * 2)
    pygame.draw.ellipse(surf, (255, 248, 220), bub_rect)
    pygame.draw.ellipse(surf, INK, bub_rect, 5)
    # SHRED! text inside the bubble.
    txt = _gradient_text("SHRED!", 36,
                          top_col=(255, 220,  50),
                          bot_col=(230,  60,  50),
                          outline=INK, outline_w=4)
    surf.blit(txt, txt.get_rect(center=(bcx, bcy)))
    return surf


def _lightning_bolt(surf, x0, y0, x1, y1, width=14,
                    fill=YELLOW, highlight=WHITE, outline=INK):
    """Jagged 4-point lightning polygon between (x0,y0) and (x1,y1).
    Adds an inner cream highlight stripe down the centre."""
    dx, dy = x1 - x0, y1 - y0
    length = max(1.0, math.hypot(dx, dy))
    ux, uy = dx / length, dy / length          # along axis
    nx, ny = -uy, ux                            # perpendicular
    # Quarter-and-three-quarter offsets create the zig-zag.
    p_q1 = (x0 + ux * length * 0.30 + nx * width * 0.7,
            y0 + uy * length * 0.30 + ny * width * 0.7)
    p_q2 = (x0 + ux * length * 0.55 - nx * width * 0.3,
            y0 + uy * length * 0.55 - ny * width * 0.3)
    p_q3 = (x0 + ux * length * 0.78 + nx * width * 0.6,
            y0 + uy * length * 0.78 + ny * width * 0.6)
    half = width * 0.5
    pts = [
        (x0 + nx * half, y0 + ny * half),
        p_q1,
        p_q2,
        p_q3,
        (x1 + nx * half * 0.2, y1 + ny * half * 0.2),
        (x1 - nx * half * 0.2, y1 - ny * half * 0.2),
        (p_q3[0] - nx * width * 0.5, p_q3[1] - ny * width * 0.5),
        (p_q2[0] - nx * width * 0.4, p_q2[1] - ny * width * 0.4),
        (p_q1[0] - nx * width * 0.5, p_q1[1] - ny * width * 0.5),
        (x0 - nx * half, y0 - ny * half),
    ]
    pygame.draw.polygon(surf, fill, pts)
    pygame.draw.polygon(surf, outline, pts, 3)
    # Centre highlight stripe.
    mid_pts = [
        (x0 + ux * length * 0.05, y0 + uy * length * 0.05),
        p_q1, p_q2, p_q3,
        (x1 - ux * length * 0.05, y1 - uy * length * 0.05),
    ]
    pygame.draw.lines(surf, highlight, False, mid_pts, 2)


def render_lightning_bolts_overlay(cx: int, cy: int,
                                     rng_seed: int = 22) -> pygame.Surface:
    """C4 — Yellow comic lightning bolts radiating outward from Pip,
    with a small ZZAP! badge to the side. Bolts start just OUTSIDE
    the 14-spike starburst (radius ~140 px) and extend further out so
    most of each bolt is visible past the burst. Thick polygon body +
    ink outline + cream highlight stripe so they pop against the
    sky."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    # 6 bolts radiating in a rough sunburst.
    angles_deg = (-145, -100, -55, -10, 35, 80)
    inner_r = 95   # bolt base — just past inner burst
    outer_r = 230  # bolt tip — well past the 14-spike rim (~140)
    for ang_deg in angles_deg:
        ang = math.radians(ang_deg + 90)  # 0 deg -> straight down
        base_x = cx + math.cos(ang) * inner_r
        base_y = cy + math.sin(ang) * inner_r
        tip_x = cx + math.cos(ang) * outer_r
        tip_y = cy + math.sin(ang) * outer_r
        # Clamp into screen with a generous margin.
        tip_x = max(20, min(W - 20, tip_x))
        tip_y = max(165, min(H - 30, tip_y))
        _lightning_bolt(surf, base_x, base_y, tip_x, tip_y,
                        width=22, fill=YELLOW,
                        highlight=(255, 255, 220), outline=INK)
    # ZZAP! badge — small yellow jagged burst to the upper-right.
    bx = max(80, min(W - 60, cx + 110))
    by = max(165, min(H - 100, cy - 70))
    _jagged_burst(surf, bx, by, 44, 24, spikes=12,
                  fill=YELLOW, outline=INK, outline_w=4, jitter=3)
    _jagged_burst(surf, bx, by, 28, 16, spikes=12,
                  fill=RED, outline=INK, outline_w=2)
    zap = _gradient_text("ZZAP!", 24,
                          top_col=(255, 250, 240),
                          bot_col=YELLOW,
                          outline=INK, outline_w=3)
    rot = pygame.transform.rotate(zap, -10)
    surf.blit(rot, rot.get_rect(center=(bx, by)))
    return surf


def render_comic_panel_overlay(cx: int, cy: int,
                                 rng_seed: int = 22) -> pygame.Surface:
    """C5 — Bold black comic-panel frame around the pickup region with
    a yellow narration caption box in the top-left corner reading
    "NEW BOARD!". Frames Pip + the existing FX like a comic snapshot."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    pw, ph = 280, 220
    panel = pygame.Rect(0, 0, pw, ph)
    panel.center = (cx, cy)
    # Keep the panel onscreen with a margin.
    panel.left   = max(8, panel.left)
    panel.top    = max(48, panel.top)
    panel.right  = min(W - 8, panel.right)
    panel.bottom = min(H - 48, panel.bottom)
    # Thick black frame — drawn 4 separate edges so the interior stays
    # see-through.
    border_w = 6
    pygame.draw.rect(surf, INK, panel, border_w)
    # Subtle drop-shadow on the right + bottom edges for depth.
    shadow_w = 4
    shadow_col = (0, 0, 0, 140)
    pygame.draw.rect(surf, shadow_col,
                     pygame.Rect(panel.right, panel.top + shadow_w,
                                 shadow_w, panel.height))
    pygame.draw.rect(surf, shadow_col,
                     pygame.Rect(panel.left + shadow_w, panel.bottom,
                                 panel.width, shadow_w))
    # Yellow narration caption box in the top-left of the panel.
    cap_w, cap_h = 150, 36
    cap = pygame.Rect(panel.left + 8, panel.top + 8, cap_w, cap_h)
    pygame.draw.rect(surf, (255, 225,  60), cap)
    pygame.draw.rect(surf, INK, cap, 3)
    txt = _gradient_text("NEW BOARD!", 22,
                          top_col=(60, 30, 10),
                          bot_col=(20, 10,  5),
                          outline=(255, 245, 200), outline_w=2)
    surf.blit(txt, txt.get_rect(center=cap.center))
    return surf


# ── C1 (kapow chorus) sub-variants — 5 spins on the same idea ───────────────


def _burst_word(surf, bx, by, label, fill, accent, rot_deg,
                ro=56, ri=30, font_size=None):
    """Two-layer jagged burst + tilted gradient text — the building
    block shared by all D-variants below."""
    _jagged_burst(surf, bx, by, ro, ri, spikes=10,
                  fill=fill, outline=INK, outline_w=4, jitter=4)
    _jagged_burst(surf, bx, by, int(ro * 0.68), int(ri * 0.73),
                  spikes=10, fill=accent, outline=INK, outline_w=2)
    if font_size is None:
        font_size = 28 if len(label) <= 5 else 24
    txt = _gradient_text(label, font_size,
                          top_col=(255, 250, 240),
                          bot_col=fill,
                          outline=INK, outline_w=3)
    rot = pygame.transform.rotate(txt, rot_deg)
    surf.blit(rot, rot.get_rect(center=(bx, by)))


def render_kapow_skate_slang_overlay(cx: int, cy: int,
                                       rng_seed: int = 22) -> pygame.Surface:
    """D1 — Same 4-corner KAPOW layout but with SKATE-SPECIFIC slang
    in the bursts: RAD! / GNARLY! / SICK! / SHRED!. Each burst
    keeps a distinct pop-art colorway. Reads as more on-brand for a
    skate powerup than the generic KAPOW/BAM."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    palette = (
        # (label, fill, accent, rot_deg, dx, dy)
        ("RAD!",    (255, 220,  30), (230,  60,  50),  -8, -120, -85),
        ("GNARLY!", (255, 100, 180), (255, 245, 200),  10,  135, -90),
        ("SICK!",   ( 95, 200, 220), ( 30,  60, 120),  -6, -140,  90),
        ("SHRED!",  (255, 165,  60), (220,  40,  40),   8,  125,  95),
    )
    for label, fill, accent, rot_deg, dx, dy in palette:
        bx = max(60, min(W - 60, cx + dx))
        by = max(110, min(H - 80, cy + dy))
        _burst_word(surf, bx, by, label, fill, accent, rot_deg)
    return surf


def render_kapow_hierarchy_overlay(cx: int, cy: int,
                                     rng_seed: int = 22) -> pygame.Surface:
    """D2 — Dominant burst + satellites. One BIG KABOOM! anchors the
    upper-right (replacing the role of the live POW!), with 3
    smaller satellite bursts (BAM!, SMASH!, ZAP!) around Pip. Size
    hierarchy gives a clear focal point instead of 4 equal-weight
    corner bursts."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    # Dominant burst — bigger ro/ri so it visually anchors.
    big_x = min(W - 80, cx + 130)
    big_y = max(170, cy - 70)
    _burst_word(surf, big_x, big_y,
                "KABOOM!", (255, 220, 30), (230, 60, 50),
                rot_deg=-12, ro=80, ri=42, font_size=34)
    # Satellites — smaller bursts at NW, SW, SE.
    sats = (
        ("BAM!",   (255, 100, 180), (255, 245, 200),  12, -130, -75),
        ("SMASH!", ( 95, 200, 220), ( 30,  60, 120),  -8, -135,  90),
        ("ZAP!",   (255, 165,  60), (220,  40,  40),  14,  120, 100),
    )
    for label, fill, accent, rot_deg, dx, dy in sats:
        bx = max(60, min(W - 60, cx + dx))
        by = max(110, min(H - 80, cy + dy))
        _burst_word(surf, bx, by, label, fill, accent, rot_deg,
                    ro=44, ri=24)
    return surf


def render_kapow_radial_ring_overlay(cx: int, cy: int,
                                       rng_seed: int = 22) -> pygame.Surface:
    """D3 — 6 bursts evenly spaced in a circle around Pip, each
    rotated to face outward. Surrounds Pip with onomatopoeia
    instead of pinning bursts to the corners — more dynamic and
    radial in feel."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    words = (
        ("KAPOW!", (255, 220,  30), (230,  60,  50)),
        ("BAM!",   (255, 100, 180), (255, 245, 200)),
        ("SMASH!", ( 95, 200, 220), ( 30,  60, 120)),
        ("WHAM!",  (255, 165,  60), (220,  40,  40)),
        ("ZAP!",   (140, 220, 110), ( 30,  80,  40)),
        ("BOOM!",  (220, 140, 255), ( 80,  30, 120)),
    )
    ring_r = 165
    n = len(words)
    for i, (label, fill, accent) in enumerate(words):
        # Distribute starting from the upper-right (skips the
        # SKATEBOARD! caption strip clamp at the top).
        ang = -math.pi / 2 + (i + 0.5) * (2 * math.pi / n)
        bx = cx + math.cos(ang) * ring_r
        by = cy + math.sin(ang) * ring_r
        bx = max(50, min(W - 50, bx))
        by = max(150, min(H - 60, by))
        # Mild varied tilt — clamped to ±18° so text stays readable
        # all around the ring (true radial alignment makes the side
        # bursts go 90° vertical and lose legibility).
        rot_deg = 18 * math.sin(ang * 2 + i * 0.5)
        _burst_word(surf, int(bx), int(by), label, fill, accent,
                    rot_deg, ro=46, ri=26, font_size=22)
    return surf


def _sticker_burst(surf, cx, cy, ro, ri, spikes, fill, jitter=4):
    """Sticker-style burst — drop shadow + flat fill + thick white
    inner border + black outer border. Looks like a skate-deck sticker
    pinned to the screen."""
    # Drop shadow — same polygon nudged down-right with dark alpha.
    shadow = pygame.Surface((W, H), pygame.SRCALPHA)
    rng = random.Random(int(cx) * 31 + int(cy) * 17 + spikes)
    pts = []
    for i in range(spikes * 2):
        ang = i * math.pi / spikes - math.pi / 2
        r = ro if i % 2 == 0 else ri
        if jitter:
            r += rng.randint(-jitter, jitter)
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    sh_pts = [(p[0] + 4, p[1] + 5) for p in pts]
    pygame.draw.polygon(shadow, (0, 0, 0, 110), sh_pts)
    surf.blit(shadow, (0, 0))
    # Outer black border (drawn as a slightly larger polygon underneath).
    pygame.draw.polygon(surf, INK, pts)
    # Inner fill polygon — same shape, scaled in slightly.
    inner_pts = [(cx + (p[0] - cx) * 0.92,
                  cy + (p[1] - cy) * 0.92) for p in pts]
    pygame.draw.polygon(surf, WHITE, inner_pts)
    inner_pts2 = [(cx + (p[0] - cx) * 0.80,
                   cy + (p[1] - cy) * 0.80) for p in pts]
    pygame.draw.polygon(surf, fill, inner_pts2)


def render_kapow_sticker_overlay(cx: int, cy: int,
                                   rng_seed: int = 22) -> pygame.Surface:
    """D4 — Punk-sticker collage. Same 4-corner KAPOW layout but each
    burst is painted as a skate-deck sticker: drop shadow + thick
    white inner border + thick black outer border, flat fill (no
    nested colored core). Punk-rock zine vibe."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    palette = (
        ("KAPOW!", (230,  60,  50),  -8, -120, -85),
        ("BAM!",   (255, 100, 180),  10,  135, -90),
        ("SMASH!", ( 95, 200, 220),  -6, -140,  90),
        ("WHAM!",  (255, 165,  60),   8,  125,  95),
    )
    for label, fill, rot_deg, dx, dy in palette:
        bx = max(70, min(W - 70, cx + dx))
        by = max(120, min(H - 80, cy + dy))
        _sticker_burst(surf, bx, by, 58, 32, spikes=10, fill=fill)
        font_size = 28 if len(label) <= 5 else 24
        txt = _gradient_text(label, font_size,
                              top_col=(255, 250, 240),
                              bot_col=(20, 20, 20),
                              outline=WHITE, outline_w=2)
        rot = pygame.transform.rotate(txt, rot_deg)
        surf.blit(rot, rot.get_rect(center=(bx, by)))
    return surf


def _halftone_filled_burst(surf, cx, cy, ro, ri, spikes,
                            dot_col, base_col, outline_w=4, jitter=4):
    """Burst polygon filled with Lichtenstein halftone dots instead
    of solid color. Renders the dots onto a sub-surface, then masks
    them with the burst polygon shape so they only show inside."""
    rng = random.Random(int(cx) * 31 + int(cy) * 17 + spikes)
    pts = []
    for i in range(spikes * 2):
        ang = i * math.pi / spikes - math.pi / 2
        r = ro if i % 2 == 0 else ri
        if jitter:
            r += rng.randint(-jitter, jitter)
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    pygame.draw.polygon(surf, base_col, pts)
    # Halftone dots — grid sample inside the burst bbox.
    bbox_l = int(min(p[0] for p in pts)) - 2
    bbox_t = int(min(p[1] for p in pts)) - 2
    bbox_r = int(max(p[0] for p in pts)) + 2
    bbox_b = int(max(p[1] for p in pts)) + 2
    dot_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    step = 8
    for gy in range(bbox_t, bbox_b, step):
        offset = (step // 2) if ((gy // step) % 2 == 1) else 0
        for gx in range(bbox_l + offset, bbox_r, step):
            pygame.draw.circle(dot_surf, dot_col,
                               (gx, gy), 2)
    # Mask the dots to the burst polygon — paint the polygon as
    # opaque alpha onto a mask surface, then RGBA_MIN.
    mask = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    dot_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(dot_surf, (0, 0))
    pygame.draw.polygon(surf, INK, pts, outline_w)


def render_kapow_halftone_filled_overlay(cx: int, cy: int,
                                           rng_seed: int = 22) -> pygame.Surface:
    """D5 — 4-corner KAPOW chorus, each burst FILLED with a halftone
    dot pattern instead of solid color. Combines the C1 onomatopoeia
    layout with the C2 Lichtenstein dot vocabulary inside each
    burst. Most overtly "pop-art comic page" of the bunch."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    palette = (
        # (label, base, dot_col, rot_deg, dx, dy)
        ("KAPOW!", (255, 220,  30), (230,  60,  50),  -8, -120, -85),
        ("BAM!",   (255, 100, 180), ( 90,  20,  90),  10,  135, -90),
        ("SMASH!", ( 95, 200, 220), ( 20,  40,  90),  -6, -140,  90),
        ("WHAM!",  (255, 165,  60), (180,  30,  30),   8,  125,  95),
    )
    for label, base, dot_col, rot_deg, dx, dy in palette:
        bx = max(60, min(W - 60, cx + dx))
        by = max(110, min(H - 80, cy + dy))
        _halftone_filled_burst(surf, bx, by, 58, 32, spikes=10,
                                dot_col=dot_col, base_col=base)
        font_size = 28 if len(label) <= 5 else 24
        txt = _gradient_text(label, font_size,
                              top_col=(255, 250, 240),
                              bot_col=base,
                              outline=INK, outline_w=3)
        rot = pygame.transform.rotate(txt, rot_deg)
        surf.blit(rot, rot.get_rect(center=(bx, by)))
    return surf


def render_starburst_surface(rng_seed: int = 22) -> pygame.Surface:
    """Self-contained 14-spike yellow/red starburst on a transparent
    BURST_SIZE × BURST_SIZE surface, centered. scenes.py blits this
    centered on Pip's current screen position each frame so the
    burst appears to follow him."""
    rng = random.Random(rng_seed)
    surf = pygame.Surface((BURST_SIZE, BURST_SIZE), pygame.SRCALPHA)
    cx = cy = BURST_SIZE // 2

    spikes = 14
    inner_r = 70
    pts = []
    for i in range(spikes * 2):
        ang = i * math.pi / spikes - math.pi / 2
        r = (140 + rng.randint(-20, 25)) if i % 2 == 0 else inner_r
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    pygame.draw.polygon(surf, YELLOW, pts)
    pygame.draw.polygon(surf, INK, pts, 5)
    inner_pts = [(cx + (p[0] - cx) * 0.65, cy + (p[1] - cy) * 0.65)
                 for p in pts]
    pygame.draw.polygon(surf, RED, inner_pts)
    pygame.draw.polygon(surf, INK, inner_pts, 3)
    return surf
