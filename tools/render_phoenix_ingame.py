"""Render in-game screenshots of the 5 fire-fenghuang phoenix variants.

Each screenshot shows Pip mid-flight with the chosen phoenix skin
active, flying past pipes and coins — i.e. exactly what the player
sees during gameplay. Then composes them into a contact sheet.

Usage:
    python tools/render_phoenix_ingame.py

Outputs to docs/phoenix_design/ingame/:
    ingame_blaze.png    ... ingame_grand.png
    _ingame_contact_sheet.png
"""

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))   # any display so pygame init works

import game.config
from game.config import W, H, GROUND_Y, BIRD_X, PIPE_W
from game.entities import PowerUp, Pipe, Coin


VARIANTS = ("blaze", "sunburst", "twin", "swift", "grand")

CAPTIONS = {
    "blaze":    "Balanced fan + curling crest",
    "sunburst": "9-plume radial spread + tall crown",
    "twin":     "Minimal fan + twin trailing crest",
    "swift":    "All plumes trailing back (motion)",
    "grand":    "Wide majestic fan + 5-feather crown",
}


def _set_variant(v: str) -> None:
    game.config.PHOENIX_VARIANT = v
    import game.world as _w
    _w.PHOENIX_VARIANT = v


def render_ingame_shot(variant: str) -> pygame.Surface:
    """Render one frame of gameplay with the chosen phoenix variant
    active. Returns a 360×640 surface (the full game viewport)."""
    _set_variant(variant)
    # Fresh App + World per variant so we can tweak state without
    # cross-contamination.
    from game.scenes import App, STATE_PLAY
    app = App()
    app.state = STATE_PLAY
    app.intro = None
    app.powerup_help = None
    w = app.world
    # Skip the ready prompt — pretend the player has already tapped.
    w.ready_t = 0
    w.ready_pulse = 0.0
    # Position Pip at a recognizable spot mid-air with a small forward tilt.
    # X is forward of the standard BIRD_X so the post-house cluster is
    # already behind him; y is high enough that the phoenix silhouette
    # paints against clear sky rather than a pipe.
    w.bird.x = BIRD_X + 60
    w.bird.y = H * 0.32
    w.bird.vy = -180.0   # mid-flap-rise
    # Activate phoenix manually (skip the pickup animation so the
    # screenshot is clean; the actual buff state is identical).
    pu = PowerUp(0, 0, kind="phoenix")
    w._on_powerup(pu)
    # Tick the world a few frames so the parallax background / weather
    # / ambient settle into a steady state.
    for _ in range(45):
        w.update(1 / 60)
    # Spawn ONE upcoming pipe well to the right so the screenshot
    # shows the bird heading toward an obstacle (gameplay context)
    # without obscuring the phoenix silhouette.
    w.pipes = []
    gap_h = 180
    gap_y = int(H * 0.55) - gap_h // 2
    w.pipes.append(Pipe(W - 80, gap_y, gap_h))
    # Park bird's y at flight altitude so the timer freeze on rendering
    # doesn't put him underground (we ticked w.update which moves him).
    w.bird.y = H * 0.32
    w.bird.vy = -120.0
    # Render one frame.
    app._render()
    # Return a COPY (app.screen will be reused by the next variant).
    out = pygame.Surface((W, H))
    out.blit(app.screen, (0, 0))
    return out


def render_contact_sheet(shots: dict) -> pygame.Surface:
    """Compose all 5 screenshots into a single contact sheet."""
    # Game viewport is 360x640 — too tall to stack 5 in a row, so we
    # use a 5-column layout with the screenshots scaled to 60% width.
    shot_w, shot_h = 240, 420  # scaled gameplay viewport
    gap = 12
    margin = 16
    header_h = 56
    caption_h = 50
    sheet_w = margin * 2 + shot_w * 5 + gap * 4
    sheet_h = margin + header_h + shot_h + caption_h + margin

    sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
    # Velvet background gradient
    for y in range(sheet_h):
        t = y / max(1, sheet_h - 1)
        col = (int(20 + 6 * t), int(14 + 10 * t), int(36 + 14 * t))
        pygame.draw.line(sheet, col, (0, y), (sheet_w, y))

    # Title
    title_font = pygame.font.SysFont(None, 36, bold=True)
    title_img = title_font.render(
        "PHOENIX — 5 fire-fenghuang variants (in-game)",
        True, (255, 220, 100))
    title_out = title_font.render(
        "PHOENIX — 5 fire-fenghuang variants (in-game)",
        True, (0, 0, 0))
    tx = (sheet_w - title_img.get_width()) // 2
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        sheet.blit(title_out, (tx + ox, 14 + oy))
    sheet.blit(title_img, (tx, 14))

    label_font = pygame.font.SysFont(None, 22, bold=True)
    caption_font = pygame.font.SysFont(None, 16)

    for i, variant in enumerate(VARIANTS):
        x0 = margin + i * (shot_w + gap)
        y0 = margin + header_h
        # Scale the gameplay shot down to fit the cell
        scaled = pygame.transform.smoothscale(shots[variant],
                                              (shot_w, shot_h))
        sheet.blit(scaled, (x0, y0))
        # Frame the shot
        pygame.draw.rect(sheet, (140, 100, 40),
                         pygame.Rect(x0 - 1, y0 - 1, shot_w + 2, shot_h + 2),
                         width=2, border_radius=4)
        # Label + caption
        label = label_font.render(variant.upper(), True, (255, 220, 100))
        lbx = x0 + (shot_w - label.get_width()) // 2
        sheet.blit(label, (lbx, y0 + shot_h + 6))
        caption = caption_font.render(CAPTIONS[variant], True, (220, 220, 240))
        cbx = x0 + (shot_w - caption.get_width()) // 2
        sheet.blit(caption, (cbx, y0 + shot_h + 28))
    return sheet


def main():
    out_dir = os.path.join(_REPO, "docs", "phoenix_design", "ingame")
    os.makedirs(out_dir, exist_ok=True)
    shots = {}
    for variant in VARIANTS:
        shot = render_ingame_shot(variant)
        path = os.path.join(out_dir, f"ingame_{variant}.png")
        pygame.image.save(shot, path)
        shots[variant] = shot
        print(f"wrote {os.path.relpath(path, _REPO)}")
    sheet = render_contact_sheet(shots)
    sheet_path = os.path.join(out_dir, "_ingame_contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"wrote {os.path.relpath(sheet_path, _REPO)}")


if __name__ == "__main__":
    main()
