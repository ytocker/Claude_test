"""Headless 10x12 exploration sheet for the fresh sky concepts.

Renders the 10 `tools.sky_concepts.CONCEPTS` (rows) across 12 day-phase samples
in natural day order (columns), sky-only via `paint_sky` with stars kept on,
into `docs/biome_redesign/round_10.png`. Larger cells than the old port-check
sheet for the requested high-quality read. Dev aid only — the game never
imports this; the live `ACTIVE_SKY_DESIGN` is untouched.

    python tools/preview_sky_concepts.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y          # noqa: E402
from game.biome_sky import paint_sky            # noqa: E402
from tools.sky_concepts import CONCEPTS         # noqa: E402


# Local 12-phase day-ordered sampling — intentionally NOT the shared STAGES, so
# this exploration can show a finer arc (predawn through night) without touching
# the live keyframe tables.
PHASES = [
    ("predawn", 0.80),
    ("dawn", 0.88),
    ("sunrise", 0.94),
    ("early-morning", 0.02),
    ("morning", 0.10),
    ("midday", 0.20),
    ("afternoon", 0.32),
    ("golden", 0.42),
    ("sunset", 0.50),
    ("dusk", 0.60),
    ("twilight", 0.68),
    ("night", 0.74),
]

# Larger cells than the old sheet (was 151x268) for the requested quality.
CW, CH = 280, 500
GUT = 220          # left gutter for concept name
HEAD = 34          # top strip for phase labels
PAD = 4

f_title = pygame.font.SysFont("dejavusans", 20, bold=True)
f_phase = pygame.font.SysFont("dejavusans", 15, bold=True)
f_name = pygame.font.SysFont("dejavusans", 19, bold=True)
f_note = pygame.font.SysFont("dejavusans", 12)


def _wrap(text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.size(trial)[0] <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    cols = len(PHASES)
    rows = len(CONCEPTS)
    sheet_w = GUT + cols * (CW + PAD) + PAD
    sheet_h = HEAD + rows * (CH + PAD) + PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    # Title rides in the top-left gutter corner above the rows.
    title = f_title.render("Skybit sky concepts — round 10 (polish)", True, (245, 246, 250))
    sheet.blit(title, (10, 6))

    # Column labels (phase names) along the top strip.
    for c, (label, _phase) in enumerate(PHASES):
        x = GUT + c * (CW + PAD)
        lbl = f_phase.render(label, True, (250, 232, 184))
        sheet.blit(lbl, (x + (CW - lbl.get_width()) // 2, HEAD - 22))

    for r, (cid, spec) in enumerate(CONCEPTS):
        y = HEAD + r * (CH + PAD)
        nm = f_name.render(spec.name, True, (248, 248, 252))
        sheet.blit(nm, (10, y + 8))
        ny = y + 8 + nm.get_height() + 6
        for line in _wrap(spec.note, f_note, GUT - 18):
            ln = f_note.render(line, True, (176, 180, 190))
            sheet.blit(ln, (10, ny))
            ny += ln.get_height() + 2
        for c, (_label, phase) in enumerate(PHASES):
            x = GUT + c * (CW + PAD)
            tile = pygame.Surface((W, H))
            paint_sky(tile, spec, W, H, phase, stars=True, ground_y=GROUND_Y)
            sheet.blit(pygame.transform.smoothscale(tile, (CW, CH)), (x, y))

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "biome_redesign", "round_10.png")
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()}, "
          f"{rows} rows x {cols} cols, cell {CW}x{CH})")


if __name__ == "__main__":
    main()
