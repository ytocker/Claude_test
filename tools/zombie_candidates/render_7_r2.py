"""Round-2 review sheet for zombie design 7 (CHARRED EMBER REVENANT).

Scratch harness: renders the candidate three ways side by side — a mid-flight
gameplay panel, a large hero shot, and a 40px "truth read" (downscaled to the
in-game sprite size then blown up nearest-neighbour) — so the reviewer can
judge whether the redistributed cracks read as a burnt corpse at true scale.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import tools.ninja_render as nr
import tools.zombie_candidates.design_7 as d

pygame.init()

_BG = (18, 16, 28)
_INK = (232, 228, 240)
_PAD = 24
_LABEL_H = 40


def _labelled(panel, text, font):
    """Stack a small caption under a panel on a padded dark tile."""
    pw, ph = panel.get_size()
    tile = pygame.Surface((pw, ph + 26), pygame.SRCALPHA)
    tile.blit(panel, (0, 0))
    cap = font.render(text, True, (196, 192, 208))
    tile.blit(cap, cap.get_rect(center=(pw // 2, ph + 13)))
    return tile


def main():
    frame = nr._frame(d.build, nr.FRAME_IDX, nr.TILT)

    gp = nr.gameplay_panel(d.build, 220, 392)
    hero = nr.hero_panel(d.build, 320)

    # 40px truth read: shrink to the real in-game sprite footprint, then blow
    # it back up 5x with no smoothing so pixel-level legibility is honest.
    small = pygame.transform.smoothscale(frame, (40, 40))
    truth = pygame.transform.scale(small, (200, 200))

    pygame.font.init()
    title_font = pygame.font.SysFont("Arial", 30, bold=True)
    cap_font = pygame.font.SysFont("Arial", 18)

    gp_t = _labelled(gp, "GAMEPLAY (mid-flight)", cap_font)
    hero_t = _labelled(hero, "HERO", cap_font)
    truth_t = _labelled(truth, "40px TRUTH-READ (5x)", cap_font)

    panels = [gp_t, hero_t, truth_t]
    total_w = sum(p.get_width() for p in panels) + _PAD * (len(panels) + 1)
    max_h = max(p.get_height() for p in panels)
    total_h = _LABEL_H + max_h + _PAD * 2

    sheet = pygame.Surface((total_w, total_h))
    sheet.fill(_BG)

    title = title_font.render("D7 BURNED — R2", True, _INK)
    sheet.blit(title, (_PAD, 6))

    x = _PAD
    for p in panels:
        sheet.blit(p, (x, _LABEL_H + _PAD))
        x += p.get_width() + _PAD

    out = "docs/store_redesign/costume/zombie/design_7/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
