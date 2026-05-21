"""Render 5 megamagnet icon variants + the current production magnet
as a reference. Design exploration only — does NOT touch game code.

Run from repo root:

    python tools/snapshot_megamagnet_icon_variants.py

Outputs under docs/screenshots/powerups/megamagnet/:
    icon_NN_<name>.png       (5 per-variant cells)
    icon_variants.png        (combined 3x2 sheet with original + 5)
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import sys
import pygame
pygame.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.entities import PowerUp


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "screenshots", "powerups", "megamagnet",
)
os.makedirs(OUT_DIR, exist_ok=True)


# Cell + zoom dimensions
CELL_RAW = 80          # native sprite cell
ZOOM = 3
CELL_W = CELL_RAW * ZOOM
CELL_H = CELL_RAW * ZOOM

# Static pulse phase — chosen so the cyan arc + tip bolts sit
# mid-discharge in every variant. Matches the typical idle-bob of
# PowerUp.pulse in game.
PULSE = 1.6


# ── shared "thick magnet" primitive ─────────────────────────────────────────
# Mirrors PowerUp._draw_magnet (game/entities.py:1282-1393) with the
# dimensions scaled by ~1.4: outer_r 13→18, inner_r 6→8. Arm thickness
# grows from 7 px to 10 px; pole tips + bolts scale proportionally.
def _draw_thick_body(surf, cx, cy, *, body_alpha=255,
                     outer_r=18, inner_r=8,
                     arch_offset=4, leg_offset=17,
                     scratch_size=58):
    """Draw a thicker horseshoe at (cx, cy). Returns
    (leg_bot, left_cx, right_cx) so callers can position pole tips
    and bolts consistently."""
    arch_cy = cy - arch_offset
    leg_bot = cy + leg_offset

    sz = scratch_size
    scx = sz // 2
    scy = outer_r + 4

    scratch = pygame.Surface((sz, sz), pygame.SRCALPHA)

    pygame.draw.circle(scratch, (80, 5, 8), (scx, scy), outer_r + 2)
    pygame.draw.rect(scratch, (80, 5, 8),
                     (scx - outer_r - 2, scy,
                      (outer_r + 2) * 2, leg_bot - arch_cy + 4))

    RED_HI = (235, 35, 45)
    pygame.draw.circle(scratch, RED_HI, (scx, scy), outer_r + 1)
    pygame.draw.rect(scratch, RED_HI,
                     (scx - outer_r - 1, scy,
                      (outer_r + 1) * 2, leg_bot - arch_cy + 3))

    pygame.draw.circle(scratch, (255, 95, 95), (scx, scy), inner_r + 1, 2)
    pygame.draw.circle(scratch, (255, 85, 85), (scx, scy), outer_r, 2)

    pygame.draw.circle(scratch, (0, 0, 0, 0), (scx, scy), inner_r)
    pygame.draw.rect(scratch, (0, 0, 0, 0),
                     (scx - inner_r, scy, inner_r * 2, sz - scy))

    if body_alpha < 255:
        scratch.set_alpha(body_alpha)
    surf.blit(scratch, (cx - scx, arch_cy - scy))

    # Chrome pole tips (proportionally larger).
    left_cx = cx - inner_r - (outer_r - inner_r) // 2
    right_cx = cx + inner_r + (outer_r - inner_r) // 2
    arm_w = outer_r - inner_r
    for tip_cx in (left_cx, right_cx):
        pygame.draw.rect(surf, (40, 42, 60),
                         (tip_cx - arm_w // 2 - 1, leg_bot - 5, arm_w + 2, 11),
                         border_radius=5)
        pygame.draw.rect(surf, (195, 210, 232),
                         (tip_cx - arm_w // 2,     leg_bot - 4, arm_w,     9),
                         border_radius=4)
        pygame.draw.rect(surf, (238, 246, 255),
                         (tip_cx - arm_w // 2 + 1, leg_bot - 4, arm_w - 2, 4),
                         border_radius=2)

    return leg_bot, left_cx, right_cx


def _draw_arc_and_bolts(surf, leg_bot, left_cx, right_cx, pulse):
    """Cyan arc between poles + yellow tip-bolts. Same patterns as the
    live magnet; carries the magnet family identity into every variant."""
    arc_y0 = leg_bot + 6
    arc_pts = [(left_cx, arc_y0)]
    for i in range(1, 6):
        t = i / 6
        x = int(left_cx + (right_cx - left_cx) * t)
        y = int(arc_y0 + math.sin(pulse * 11 + i * 1.7) * 4)
        arc_pts.append((x, y))
    arc_pts.append((right_cx, arc_y0))
    arc_surf = pygame.Surface(
        (right_cx - left_cx + 8, 16), pygame.SRCALPHA)
    shifted = [(p[0] - left_cx + 4, p[1] - arc_y0 + 4) for p in arc_pts]
    if len(shifted) >= 2:
        pygame.draw.lines(arc_surf, (100, 195, 255, 200), False, shifted, 3)
    surf.blit(arc_surf, (left_cx - 4, arc_y0 - 4))

    YELLOW = (255, 220, 60)
    WHITE = (255, 250, 220)
    for sign, tip_cx in ((-1, left_cx), (+1, right_cx)):
        tip_y = leg_bot + 1
        jitter = math.sin(pulse * 9 + (0 if sign < 0 else math.pi / 3))
        for pts in (
                [(tip_cx, tip_y),
                 (tip_cx + sign * 5, tip_y + 2),
                 (tip_cx + sign * 1, tip_y + 5 + int(jitter)),
                 (tip_cx + sign * 6, tip_y + 7)],
                [(tip_cx + sign * 1, tip_y - 1),
                 (tip_cx + sign * 5, tip_y),
                 (tip_cx + sign * 2, tip_y + 2),
                 (tip_cx + sign * 7, tip_y + 1)]):
            pygame.draw.lines(surf, YELLOW, False, pts, 2)
            pygame.draw.lines(surf, WHITE, False, pts, 1)
        pygame.draw.circle(surf, WHITE, (tip_cx, tip_y), 2)
        pygame.draw.circle(surf, YELLOW, (tip_cx, tip_y), 1)


# ── variant 1: thick_plain ──────────────────────────────────────────────────
def render_thick_plain(cell):
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 4
    leg_bot, lcx, rcx = _draw_thick_body(cell, cx, cy)
    _draw_arc_and_bolts(cell, leg_bot, lcx, rcx, PULSE)


# ── variant 2: thick_plus (gold "++" badge in the arch hollow) ──────────────
def render_thick_plus(cell):
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 4
    leg_bot, lcx, rcx = _draw_thick_body(cell, cx, cy)
    _draw_arc_and_bolts(cell, leg_bot, lcx, rcx, PULSE)

    # "++" centred in the hollow ring above the legs.
    badge_font = pygame.font.SysFont(None, 22, bold=True)
    shadow = badge_font.render("++", True, (60, 30, 8))
    main = badge_font.render("++", True, (255, 210, 70))
    rect = main.get_rect(center=(cx, cy - 8))
    cell.blit(shadow, rect.move(1, 1))
    cell.blit(main, rect)


# ── variant 3: thick_aura (warm-gold halo behind the body) ──────────────────
def render_thick_aura(cell):
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 4
    # Halo first, body on top.
    halo_r = 30
    halo = pygame.Surface((halo_r * 2 + 6, halo_r * 2 + 6),
                          pygame.SRCALPHA)
    hcx = hcy = halo_r + 3
    for i in range(halo_r, 0, -1):
        t = i / halo_r
        bell = math.exp(-((t - 0.6) ** 2) / 0.18)
        a = int(120 * bell)
        if a > 0:
            pygame.draw.circle(halo, (255, 200, 80, a), (hcx, hcy), i)
    cell.blit(halo, (cx - hcx, cy - hcy))

    leg_bot, lcx, rcx = _draw_thick_body(cell, cx, cy)
    _draw_arc_and_bolts(cell, leg_bot, lcx, rcx, PULSE)


# ── variant 4: thick_bolt (yellow lightning bolt across the front) ──────────
def render_thick_bolt(cell):
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 4
    leg_bot, lcx, rcx = _draw_thick_body(cell, cx, cy)

    # Big lightning bolt drawn across the magnet body, in front of
    # the red but behind the chrome tips. A simple zig-zag from
    # upper-left to lower-right.
    bolt_pts = [
        (cx - 10, cy - 14),
        (cx + 2,  cy - 6),
        (cx - 4,  cy),
        (cx + 10, cy + 6),
        (cx + 2,  cy + 12),
        (cx + 12, cy + 18),
    ]
    pygame.draw.lines(cell, (90, 50, 0), False, bolt_pts, 6)
    pygame.draw.lines(cell, (255, 220, 60), False, bolt_pts, 4)
    pygame.draw.lines(cell, (255, 250, 220), False, bolt_pts, 2)

    _draw_arc_and_bolts(cell, leg_bot, lcx, rcx, PULSE)


# ── variant 5: twin_horseshoe (back magnet peeks behind the front) ──────────
def render_twin_horseshoe(cell):
    front_cx = CELL_RAW // 2 + 4
    cy = CELL_RAW // 2 - 4

    # Back magnet — dimmer + offset behind-left.
    back_cx = front_cx - 14
    _draw_thick_body(cell, back_cx, cy - 1, body_alpha=200)
    # No bolts / arc for the back one so it doesn't compete.

    # Front magnet — full bright.
    leg_bot, lcx, rcx = _draw_thick_body(cell, front_cx, cy)
    _draw_arc_and_bolts(cell, leg_bot, lcx, rcx, PULSE)


# ── reference: live production magnet sprite ────────────────────────────────
def render_reference(cell):
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 4
    p = PowerUp(cx, cy, "magnet")
    p.pulse = PULSE
    p.draw(cell)


VARIANTS = (
    ("00_reference",     render_reference,       "Original"),
    ("01_thick_plain",   render_thick_plain,     "Thick plain"),
    ("02_thick_plus",    render_thick_plus,      'Thick + "++"'),
    ("03_thick_aura",    render_thick_aura,      "Thick + aura"),
    ("04_thick_bolt",    render_thick_bolt,      "Thick + bolt"),
    ("05_twin_horseshoe", render_twin_horseshoe, "Twin horseshoe"),
)


def _make_cell_backdrop():
    """Subtle dark backdrop so the icons read on the comparison sheet."""
    surf = pygame.Surface((CELL_RAW, CELL_RAW))
    # Vertical gradient: deeper at top, lighter at bottom.
    for y in range(CELL_RAW):
        t = y / (CELL_RAW - 1)
        c = int(28 + t * 18)
        pygame.draw.line(surf, (c, c, c + 6), (0, y), (CELL_RAW - 1, y))
    return surf


def _render_cell(render_fn):
    backdrop = _make_cell_backdrop()
    render_fn(backdrop)
    return pygame.transform.scale(backdrop, (CELL_W, CELL_H))


def main():
    rendered = []
    for name, fn, label in VARIANTS:
        zoomed = _render_cell(fn)
        rendered.append((name, label, zoomed))

        # Also save each cell as its own PNG (skip the reference —
        # it duplicates the existing magnet snapshot).
        if name != "00_reference":
            out_path = os.path.join(OUT_DIR, f"icon_{name}.png")
            pygame.image.save(zoomed, out_path)
            print(f"saved {out_path}")

    _write_combined_sheet(rendered)


def _write_combined_sheet(rendered):
    """3-column / 2-row sheet, original magnet (#0) in the top-left
    and the 5 variants filling cells #1-#5. Each cell has a label
    strip above the rendered icon."""
    cell_label_h = 36
    pad = 16
    margin = 24
    header_h = 56

    cell_full_h = CELL_H + cell_label_h
    cols, rows = 3, 2
    sheet_w = cols * CELL_W + (cols - 1) * pad + 2 * margin
    sheet_h = header_h + rows * cell_full_h + (rows - 1) * pad + 2 * margin

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 22, 28))

    title_font = pygame.font.SysFont(None, 32, bold=True)
    label_font = pygame.font.SysFont(None, 26, bold=True)

    title = title_font.render(
        "Megamagnet icon — original + 5 design variants",
        True, (240, 240, 245))
    sheet.blit(title, (margin, margin + 6))

    for i, (name, label, surf) in enumerate(rendered):
        col = i % cols
        row = i // cols
        x = margin + col * (CELL_W + pad)
        y = margin + header_h + row * (cell_full_h + pad)

        pygame.draw.rect(sheet, (40, 40, 50),
                         (x, y, CELL_W, cell_label_h))
        # Highlight the reference cell so the user can see what
        # they're comparing against.
        idx = name.split("_", 1)[0]
        if idx == "00":
            badge_col = (180, 200, 230)
            text = f"#0  {label}  (reference)"
        else:
            badge_col = (250, 220, 130)
            text = f"#{int(idx)}  {label}"
        lbl = label_font.render(text, True, badge_col)
        sheet.blit(lbl, (x + 12, y + 6))

        sheet.blit(surf, (x, y + cell_label_h))

    out_path = os.path.join(OUT_DIR, "icon_variants.png")
    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
