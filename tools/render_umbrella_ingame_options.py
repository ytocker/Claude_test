"""Umbrella power-up — in-gameplay overlay exploration (round 1).

The umbrella cancels the thunderstorm flap-dampening; while it is active a
small umbrella floats above Pip's head. The chosen pickup ICON is C4 (cream
badge ring) from `render_umbrella_icon_options.py` — the umbrella INSIDE that
ring is a teal/white scalloped canopy + J-hook handle. The in-gameplay
umbrella must read as the SAME umbrella so the player connects pickup ->
buff: same teal/white canopy, ink outline, ferrule, handle. The cream/gold
ring was pickup FRAMING only, so it is deliberately absent here.

Two behaviours this sheet must prove:
  - The umbrella sits ON TOP of Pip's head and stays UPRIGHT (or at a fixed
    per-variant lean) while Pip's body tilts as he flaps/dives — exactly the
    helmet-overlay precedent (`Bird._draw_helmet`): the rotating bird is
    drawn first, the overlay is composed upright on top afterwards.
  - It is a night thunderstorm event, so every cell sits on a dark storm sky
    with faint rain streaks.

We reuse the icon's `_canopy`, `_j_handle`, and the teal/white/ink/ferrule
palette so the in-game umbrella is pixel-consistent with the chosen icon —
no second source of truth for the umbrella look.

Each of the 5 variants is shown across 3 representative Pip poses
(+25deg rising, 0deg level, -25deg diving) so the reviewer can see the
umbrella holding its angle while Pip rotates underneath it.

Output: docs/umbrella_powerup/ingame_round_1.png   (doc-only; not shipped)
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

from game import parrot
# Reuse the chosen icon's exact umbrella geometry + palette so the
# in-gameplay umbrella matches pickup C4 pixel-for-pixel.
from tools.render_umbrella_icon_options import (
    _canopy, _j_handle,
    CANOPY_TEAL, CANOPY_TEAL_HI, CANOPY_CREAM,
    INK, FERRULE, DROP_BLUE, DROP_BLUE_HI,
    _lerp,
)

# Supersample the umbrella overlay then smoothscale down so the ink outline
# and scallops stay crisp at the small on-head footprint (same idiom the icon
# tool uses for the pickup glyph).
SS = 6

# Pip sprite metrics (parrot.SPRITE_W/H = 64x60). The head crown sits high in
# the sprite — the head ellipse is centred ~21px from the sprite top, i.e.
# ~9px above the sprite centre; its top edge is ~25px above centre. The
# umbrella hem is anchored just above that crown.
HEAD_CROWN_DY = -25                     # px above the parrot centre


def _make_umbrella(head_span, *, rise_scale=0.62, panels=6,
                   handle_len=0.0, lean_deg=0.0, ferrule=True,
                   deflect_drops=False):
    """Build one upright (or fixed-lean) umbrella overlay surface sized to
    `head_span` px of half-width, reusing the icon's canopy/handle so it
    matches the chosen pickup. Returns the smoothscaled SRCALPHA surface and
    the (x, y) of the canopy hem-centre within that surface, so the caller can
    seat the hem precisely on Pip's crown regardless of handle length.

    `handle_len` is the J-hook shaft length as a fraction of span (0 = none).
    `lean_deg` is a FIXED tilt applied to the whole umbrella — it never tracks
    Pip's pose. `deflect_drops` adds a couple of raindrops splitting off the
    rim (the rain-protection tell)."""
    span = int(head_span * SS)
    rise = int(span * rise_scale)
    ink = max(3, int(SS * 1.05))

    # Generous canvas: room above for the ferrule, below for any handle, and
    # margin on the sides for the lean rotation + deflection drops.
    handle_px = int(span * handle_len)
    margin = int(span * 0.6)
    w = span * 2 + margin * 2
    h = rise + int(span * 0.5) + handle_px + margin * 2
    big = pygame.Surface((w, h), pygame.SRCALPHA)

    # Hem centre placed so the dome + ferrule fit above and the handle hangs
    # below within the canvas.
    cx = w // 2
    hem_y = margin + rise + int(span * 0.30)

    if handle_len > 0:
        _j_handle(big, cx, hem_y, handle_px, span, ink)
    _canopy(big, cx, hem_y, span, rise, panels,
            (CANOPY_TEAL, CANOPY_CREAM), ink,
            ferrule=ferrule, hi_col=CANOPY_TEAL_HI)

    if deflect_drops:
        # A few drops peeling off both hem corners + sliding down the dome,
        # so the bigger shelter reads as actively shedding rain.
        for dirx in (-1, 1):
            hx = cx + dirx * span
            for k, (ox, oy, dr) in enumerate(
                    ((0.10, 0.16, 0.10), (0.30, 0.42, 0.08))):
                dx = int(hx + dirx * span * ox)
                dy = int(hem_y + span * oy)
                rr = int(span * dr)
                pygame.draw.circle(big, DROP_BLUE, (dx, dy + rr), rr)
                pygame.draw.polygon(big, DROP_BLUE,
                                    [(dx - rr, dy + rr), (dx, dy - rr),
                                     (dx + rr, dy + rr)])
                pygame.draw.circle(big, DROP_BLUE_HI,
                                   (dx - rr // 3, dy + rr - rr // 3),
                                   max(1, rr // 3))
                pygame.draw.circle(big, INK, (dx, dy + rr), rr, ink)

    # Downscale to on-screen size first, then apply the FIXED lean. The hem
    # anchor is tracked through both transforms so the caller seats it right.
    sw, sh = w // SS, h // SS
    small = pygame.transform.smoothscale(big, (sw, sh))
    hem = (cx / SS, hem_y / SS)

    if lean_deg:
        rotated = pygame.transform.rotate(small, lean_deg)
        # rotate pivots about the surface centre; recompute where the hem
        # landed so the umbrella still seats correctly after the lean.
        scx, scy = sw / 2, sh / 2
        rel_x, rel_y = hem[0] - scx, hem[1] - scy
        a = math.radians(-lean_deg)               # pygame rotates CCW for +deg
        rx = rel_x * math.cos(a) - rel_y * math.sin(a)
        ry = rel_x * math.sin(a) + rel_y * math.cos(a)
        rw, rh = rotated.get_size()
        hem = (rw / 2 + rx, rh / 2 + ry)
        small = rotated

    return small, hem


# ---------------------------------------------------------------------------
# Five variants. Each is a builder returning (surface, hem_anchor) plus the
# vertical gap (in px) to float the hem above Pip's head crown.
# ---------------------------------------------------------------------------
def v1_canopy_straight(head_span):
    """V1 — Canopy only, straight: clean teal canopy ~1.0x head-span, no
    handle, 0deg, floating a touch above the crown."""
    surf, hem = _make_umbrella(head_span, handle_len=0.0, lean_deg=0.0)
    return surf, hem, 4


def v2_canopy_jaunty(head_span):
    """V2 — Canopy + short J-hook tucked behind the head, at a FIXED 10deg
    lean (does not track Pip's pose)."""
    surf, hem = _make_umbrella(head_span, handle_len=0.30, lean_deg=10.0)
    return surf, hem, 3


def v3_big_shelter(head_span):
    """V3 — Big shelter + deflection: larger canopy that visibly covers Pip,
    floating a touch higher, with raindrops splitting off the rim."""
    surf, hem = _make_umbrella(int(head_span * 1.28), rise_scale=0.58,
                               handle_len=0.0, deflect_drops=True)
    return surf, hem, 6


def v4_compact_hug(head_span):
    """V4 — Compact hug: smaller canopy sitting close to the crown, no handle,
    minimal and unobtrusive."""
    surf, hem = _make_umbrella(int(head_span * 0.82), rise_scale=0.66,
                               panels=5, handle_len=0.0)
    return surf, hem, 1


def v5_full_handle(head_span):
    """V5 — Full handle (literal icon match): canopy + full visible J-hook
    running down beside the body, upright."""
    surf, hem = _make_umbrella(head_span, handle_len=0.62, lean_deg=0.0)
    return surf, hem, 3


VARIANTS = [
    ("V1", "Canopy only, straight", v1_canopy_straight),
    ("V2", "Canopy + short handle, jaunty", v2_canopy_jaunty),
    ("V3", "Big shelter + deflection", v3_big_shelter),
    ("V4", "Compact hug", v4_compact_hug),
    ("V5", "Full handle (icon match)", v5_full_handle),
]

POSES = [(+25.0, "rising"), (0.0, "level"), (-25.0, "diving")]


# ---------------------------------------------------------------------------
# Night thunderstorm-sky swatch with faint rain streaks (per-cell backdrop).
# Darker than the icon tool's dusk swatch since the umbrella event is night.
# ---------------------------------------------------------------------------
def _night_storm(w, h, seed):
    surf = pygame.Surface((w, h))
    top = (26, 28, 50)                  # deep night indigo
    bot = (12, 14, 28)
    for y in range(h):
        surf.fill(_lerp(top, bot, y / max(1, h - 1)), (0, y, w, 1))
    rng = (seed * 2654435761) & 0xFFFFFFFF

    def rnd():
        nonlocal rng
        rng = (1103515245 * rng + 12345) & 0x7FFFFFFF
        return rng / 0x7FFFFFFF

    streaks = pygame.Surface((w, h), pygame.SRCALPHA)
    for _ in range(int(w * h / 520)):
        x = rnd() * w
        y = rnd() * h
        ln = 8 + rnd() * 14
        pygame.draw.line(streaks, (180, 198, 235, 50),
                         (x, y), (x - 3, y + ln), 1)
    surf.blit(streaks, (0, 0))
    return surf


def _draw_cell(sheet, x, y, cw, ch, build_fn, tilt_deg, seed):
    """Pip at `tilt_deg` with the variant umbrella seated upright on his
    crown, over a night-storm swatch."""
    swatch = _night_storm(cw, ch, seed)
    sheet.blit(swatch, (x, y))
    pygame.draw.rect(sheet, (54, 60, 84), (x, y, cw, ch), 1)

    cx = x + cw // 2
    cy = y + ch // 2 + 6                 # bias down so umbrella has headroom

    # Gentle idle bob baked in so Pip + umbrella read as a live, hovering
    # pickup state rather than pinned dead-centre.
    bob = int(round(math.sin(seed * 0.9) * 3))
    cy += bob

    # Pip first — rotated by his pose tilt (the umbrella must NOT inherit this).
    pip = parrot.get_parrot(0, tilt_deg)
    pr = pip.get_rect(center=(cx, cy))
    sheet.blit(pip, pr.topleft)

    # The head crown rides with Pip's rotation: rotate the crown offset vector
    # by the same tilt so the umbrella seats over the actual head, not a fixed
    # screen point. pygame rotates surfaces CCW for +deg, so the world-space
    # crown rotates by the same sign about Pip's centre.
    a = math.radians(tilt_deg)
    crown_dx = -HEAD_CROWN_DY * math.sin(a)        # (0, HEAD_CROWN_DY) rotated
    crown_dy = HEAD_CROWN_DY * math.cos(a)
    crown_x = cx + crown_dx
    crown_y = cy + crown_dy

    # Build the umbrella sized to Pip's head half-span (~head ellipse rx 12).
    surf, hem, gap = build_fn(20)
    hem_x, hem_y = hem
    # Seat the hem `gap` px above the crown; blit so the hem anchor lands there.
    target_x = crown_x
    target_y = crown_y - gap
    blit_x = int(target_x - hem_x)
    blit_y = int(target_y - hem_y)
    sheet.blit(surf, (blit_x, blit_y))


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "umbrella_powerup")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ingame_round_1.png")

    def font(sz, bold=False):
        return pygame.font.SysFont("Arial", sz, bold=bold)

    cell_w, cell_h = 200, 200
    pad = 14
    header_h = 78
    row_label_w = 150            # left gutter for V-labels
    col_label_h = 26             # pose labels above the grid

    n_rows = len(VARIANTS)
    n_cols = len(POSES)

    grid_x0 = pad + row_label_w
    grid_y0 = header_h + col_label_h

    sheet_w = grid_x0 + n_cols * cell_w + (n_cols - 1) * pad + pad
    sheet_h = grid_y0 + n_rows * cell_h + (n_rows - 1) * pad + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 28))

    title = font(24, bold=True).render(
        "UMBRELLA in-gameplay — round 1", True, (240, 240, 248))
    sheet.blit(title, (pad, pad))
    sub = font(14).render(
        "Teal canopy matches chosen icon C4; floats on Pip's head and stays "
        "upright as Pip tilts. Night thunderstorm sky + rain streaks.",
        True, (172, 182, 200))
    sheet.blit(sub, (pad, pad + 30))
    sub2 = font(13).render(
        "Rows = 5 variants; columns = pose (rising +25deg / level 0deg / "
        "diving -25deg). No cream ring on the parrot (pickup framing only).",
        True, (150, 175, 205))
    sheet.blit(sub2, (pad, pad + 50))

    # Column (pose) labels above the grid.
    for col, (_tilt, pose_name) in enumerate(POSES):
        cx = grid_x0 + col * (cell_w + pad)
        lbl = font(15, bold=True).render(pose_name, True, (210, 220, 236))
        sheet.blit(lbl, (cx + cell_w // 2 - lbl.get_width() // 2,
                         grid_y0 - col_label_h + 4))

    seed = 3
    for row, (tag, name, build_fn) in enumerate(VARIANTS):
        gy = grid_y0 + row * (cell_h + pad)
        # Row (variant) label in the left gutter.
        tag_lbl = font(18, bold=True).render(tag, True, (250, 244, 230))
        sheet.blit(tag_lbl, (pad, gy + cell_h // 2 - 24))
        # Wrap the name across up to two lines in the gutter.
        words = name.split(" ")
        line, lines = "", []
        for wd in words:
            trial = (line + " " + wd).strip()
            if font(13).size(trial)[0] > row_label_w - 8 and line:
                lines.append(line)
                line = wd
            else:
                line = trial
        if line:
            lines.append(line)
        for i, ln in enumerate(lines):
            nlbl = font(13).render(ln, True, (200, 208, 224))
            sheet.blit(nlbl, (pad, gy + cell_h // 2 + i * 16))

        for col, (tilt, _pose) in enumerate(POSES):
            gx = grid_x0 + col * (cell_w + pad)
            _draw_cell(sheet, gx, gy, cell_w, cell_h, build_fn, tilt,
                       seed)
            seed += 1

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
