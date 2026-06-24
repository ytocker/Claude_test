"""Assemble the final 5-up bazaar-landing comparison figure.

Docs-only tooling: tiles each concept's final round_2.png (360x640) side by side
under a titled header band so the five directions can be judged at a glance.
Pure pygame, headless-safe.
"""
import os
import pygame

HERE = os.path.dirname(os.path.abspath(__file__))

# (dir, display title, one-line descriptor)
CONCEPTS = [
    ("sky_bazaar",      "FLOATING SKY-BAZAAR",  "gold-rimmed cloud platforms"),
    ("balloon_caravan", "BALLOON CARAVAN",      "caravan of market balloons"),
    ("sky_galleon",     "SKY-GALLEON MARKET",   "flying merchant airship"),
    ("dock_market",     "GOLDEN-HOUR DOCK",     "tropical harbor boardwalk"),
    ("lagoon_stilt",    "LAGOON STILT-MARKET",  "huts over a golden lagoon"),
]

PANEL_W, PANEL_H = 360, 640
PAD = 22          # outer + inter-panel padding
HEADER = 92       # title band above each panel
NUM_W = 46        # index chip
BG = (16, 14, 34)
BAND = (26, 22, 52)
GOLD = (244, 198, 96)
CREAM = (245, 232, 206)
SUB = (170, 162, 196)


def main():
    pygame.init()
    n = len(CONCEPTS)
    W = PAD + n * (PANEL_W + PAD)
    H = PAD + HEADER + PANEL_H + PAD + 40  # +40 footer
    canvas = pygame.Surface((W, H), pygame.SRCALPHA)
    canvas.fill(BG)

    # top + bottom decorative gold rules
    pygame.draw.line(canvas, GOLD, (PAD, 8), (W - PAD, 8), 3)
    pygame.draw.line(canvas, GOLD, (PAD, H - 8), (W - PAD, H - 8), 3)

    title_font = pygame.font.SysFont("Arial", 24, bold=True)
    sub_font = pygame.font.SysFont("Arial", 17)
    num_font = pygame.font.SysFont("Arial", 30, bold=True)
    foot_font = pygame.font.SysFont("Arial", 18, bold=True)

    for i, (d, title, sub) in enumerate(CONCEPTS):
        x = PAD + i * (PANEL_W + PAD)
        # header band
        band = pygame.Rect(x, PAD, PANEL_W, HEADER)
        pygame.draw.rect(canvas, BAND, band, border_radius=12)
        pygame.draw.rect(canvas, (58, 50, 96), band, width=2, border_radius=12)
        # number chip
        chip = pygame.Rect(x + 12, PAD + 12, NUM_W, NUM_W)
        pygame.draw.rect(canvas, GOLD, chip, border_radius=10)
        ns = num_font.render(str(i + 1), True, (40, 26, 8))
        canvas.blit(ns, ns.get_rect(center=chip.center))
        # title + sub
        ts = title_font.render(title, True, CREAM)
        canvas.blit(ts, (x + 12 + NUM_W + 14, PAD + 14))
        ss = sub_font.render(sub, True, SUB)
        canvas.blit(ss, (x + 12 + NUM_W + 14, PAD + 46))

        # panel image
        img = pygame.image.load(os.path.join(HERE, d, "round_2.png"))
        if img.get_size() != (PANEL_W, PANEL_H):
            img = pygame.transform.smoothscale(img, (PANEL_W, PANEL_H))
        py = PAD + HEADER
        # subtle frame under the panel
        frame = pygame.Rect(x - 2, py - 2, PANEL_W + 4, PANEL_H + 4)
        pygame.draw.rect(canvas, GOLD, frame, width=2, border_radius=6)
        canvas.blit(img, (x, py))

    foot = foot_font.render(
        "Skybit STORE — bazaar-landing concepts (final design-loop sheets; "
        "design exploration only, not yet wired into the game)",
        True, SUB)
    canvas.blit(foot, (PAD, H - 32))

    out = os.path.join(HERE, "compare_final.png")
    pygame.image.save(canvas, out)
    # half-scale companion for quick viewing
    half = pygame.transform.smoothscale(canvas, (W // 2, H // 2))
    pygame.image.save(half, os.path.join(HERE, "compare_final@half.png"))
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    main()
