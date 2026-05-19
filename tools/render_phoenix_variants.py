"""Render a contact sheet of the 5 phoenix-powerup design variants.

Lays out one row per variant — Classic / Solar / Ember / Mythic / Ashes —
each row showing the Pip sprite, the pickup icon, the HUD glyph, and
a small caption summarizing the variant's accompanying gameplay perk.

The variant being rendered is selected by mutating `game.config` AND
the already-imported copies of `PHOENIX_VARIANT` inside `world.py` and
`entities.py`, mirroring how the live game reads the constant. Outputs
land in `docs/phoenix_design/`.
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
pygame.display.set_mode((1, 1))

import game.config
from game.entities import PowerUp, Bird, get_nightglow_star  # noqa: F401  (warms entity module)
from game import parrot, entities, hud


VARIANTS = ("classic", "solar", "ember", "mythic", "ashes")


PERK_CAPTION = {
    "classic": "Pure revive, no extra perk.",
    "solar":   "Weak coin-magnet while active.",
    "ember":   "Ember trail behind Pip; coins worth 2x.",
    "mythic":  "Egg-crack cinematic on rebirth (0.6 s pause).",
    "ashes":   "Ash + falling egg; respawns in next safe gap.",
}


def _set_variant(v: str) -> None:
    """Update PHOENIX_VARIANT everywhere the live game reads it."""
    game.config.PHOENIX_VARIANT = v
    # `world.py` imports the constant at module load; we patched it via
    # `from game.config import ... PHOENIX_VARIANT` so we have to update
    # the module-level binding too. Same for any other consumer.
    import game.world as _w
    _w.PHOENIX_VARIANT = v


# ── per-cell renderers ─────────────────────────────────────────────

def render_pip_sprite(variant: str, size: int = 120,
                      pip_scale: float = 2.0) -> pygame.Surface:
    """Pip wearing the chosen phoenix skin, with the variant's halo
    behind him. We render onto a transparent surface of `size`x`size`
    and upscale Pip by `pip_scale` so the flame crown / tail ember /
    glow eyes are legible at design-review resolution."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    # Halo first (drawn behind the sprite). Pass a frame_t that lands
    # near the peak of the pulse so the halo reads at full brightness
    # in the still image. sin(0.7 * t) peaks at t ~= 2.24 (pi/(2*0.7)).
    halo_t = math.pi / (2 * 0.7)
    if variant == "solar":
        entities._draw_phoenix_solar_halo(surf, cx, cy, halo_t)
    elif variant == "mythic":
        entities._draw_phoenix_mythic_halo(surf, cx, cy, halo_t)
    else:
        entities._draw_phoenix_fire_halo(surf, cx, cy, halo_t)
    # EMBER: paint a static ember trail behind Pip so the design read
    # holds up in a still image (the live trail is dynamic).
    if variant == "ember":
        for i, (off, sz, alpha) in enumerate((
            (40, 6, 220), (60, 5, 170), (78, 4, 130),
            (92, 3,  90), (104, 2, 50),
        )):
            ember = pygame.Surface((sz * 4, sz * 4), pygame.SRCALPHA)
            er = ember.get_rect().center
            pygame.draw.circle(ember, (255, 180,  60, alpha), er, sz)
            pygame.draw.circle(ember, (255, 240, 160, alpha // 2), er, max(1, sz // 2))
            surf.blit(ember, (cx - off - sz * 2, cy + 8 - sz * 2))
    # Sprite (frame 0, 0° tilt) — explicit variant arg so we don't have
    # to round-trip through the module-level constant.
    img = parrot.get_phoenix_parrot(0, 0.0, variant=variant)
    if abs(pip_scale - 1.0) > 1e-3:
        w, h = img.get_size()
        img = pygame.transform.smoothscale(
            img, (int(w * pip_scale), int(h * pip_scale)))
    irect = img.get_rect(center=(cx, cy))
    surf.blit(img, irect.topleft)
    # ASHES: paint a small egg sketch beside Pip to convey the rebirth
    # mechanic in a still image (the live egg appears only at death).
    if variant == "ashes":
        egg_cx, egg_cy = cx + 56, cy + 40
        pygame.draw.ellipse(surf, (130, 100,  60),
                            pygame.Rect(egg_cx - 9, egg_cy - 12, 18, 24))
        pygame.draw.ellipse(surf, (245, 230, 190),
                            pygame.Rect(egg_cx - 8, egg_cy - 11, 16, 22))
        # Crack line
        pygame.draw.line(surf, ( 80,  60,  30),
                         (egg_cx - 3, egg_cy - 4),
                         (egg_cx + 2, egg_cy + 0), 1)
        pygame.draw.line(surf, ( 80,  60,  30),
                         (egg_cx + 2, egg_cy + 0),
                         (egg_cx - 1, egg_cy + 5), 1)
        # Small ash puff to the left of the egg
        for ox, oy, sz in ((-12, 4, 3), (-16, -2, 2), (-10, -5, 2)):
            pygame.draw.circle(surf, (170, 160, 150, 200),
                               (egg_cx + ox, egg_cy + oy), sz)
    return surf


def render_pickup_icon(variant: str, size: int = 96) -> pygame.Surface:
    """Render the in-world pickup token by spawning a `PowerUp` and
    asking it to draw itself."""
    _set_variant(variant)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    p = PowerUp(cx, cy, kind="phoenix")
    p.update(0.5)   # advance pulse a bit so flicker reads nicely
    p.draw(surf)
    return surf


def render_hud_glyph(variant: str, size: int = 48) -> pygame.Surface:
    """Render the HUD timer-row glyph (a 24×24 button inside a panel)."""
    _set_variant(variant)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    inner = pygame.Rect(0, 0, 24, 24)
    inner.center = (size // 2, size // 2)
    pygame.draw.rect(surf, (15, 25, 60, 220), inner, border_radius=6)
    pygame.draw.rect(surf, (60, 90, 160, 255), inner, width=1, border_radius=6)
    hud._draw_buff_icon(surf, inner.inflate(-4, -4), "phoenix")
    return surf


def _outlined(surf, text, size, fill, outline=(0, 0, 0)):
    font = pygame.font.SysFont(None, size, bold=True)
    img = font.render(text, True, fill)
    out = font.render(text, True, outline)
    canvas = pygame.Surface((img.get_width() + 4, img.get_height() + 4),
                            pygame.SRCALPHA)
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        canvas.blit(out, (2 + ox, 2 + oy))
    canvas.blit(img, (2, 2))
    return canvas


# ── contact sheet layout ───────────────────────────────────────────


def render_contact_sheet() -> pygame.Surface:
    row_h = 200
    sheet_w = 920
    header_h = 64
    sheet_h = header_h + row_h * len(VARIANTS) + 24
    sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
    # Dark velvet background gradient
    for y in range(sheet_h):
        t = y / max(1, sheet_h - 1)
        col = (int(20 + 6 * t), int(14 + 10 * t), int(36 + 14 * t))
        pygame.draw.line(sheet, col, (0, y), (sheet_w, y))

    title = _outlined(sheet, "PHOENIX — 5 design variants",
                      36, (255, 220, 100))
    sheet.blit(title, ((sheet_w - title.get_width()) // 2, 14))

    # Column headers
    header_font = pygame.font.SysFont(None, 18, bold=True)
    for x_label, x in (("PIP", 130), ("PICKUP", 280),
                       ("HUD", 410), ("PERK / NOTES", 615)):
        lbl = header_font.render(x_label, True, (200, 200, 220))
        sheet.blit(lbl, (x - lbl.get_width() // 2, header_h - 6))

    name_font = pygame.font.SysFont(None, 22, bold=True)
    perk_font = pygame.font.SysFont(None, 18)

    for i, variant in enumerate(VARIANTS):
        y0 = header_h + 16 + i * row_h
        # Faint row separator
        if i > 0:
            pygame.draw.line(sheet, (60, 50, 90),
                             (24, y0 - 6), (sheet_w - 24, y0 - 6), 1)
        # Pip sprite + halo (rendered onto a 220×220 transparent surface;
        # Pip himself is upscaled 2.4× via render_pip_sprite).
        pip_box = render_pip_sprite(variant, size=220, pip_scale=2.4)
        sheet.blit(pip_box, (20, y0 - 6))
        # Pickup icon
        pickup = render_pickup_icon(variant, size=110)
        sheet.blit(pickup, (244, y0 + 36))
        # HUD glyph
        hud_g = render_hud_glyph(variant, size=56)
        sheet.blit(hud_g, (388, y0 + 64))
        # Variant label + caption
        title_lbl = name_font.render(variant.upper(), True, (255, 220, 100))
        sheet.blit(title_lbl, (478, y0 + 36))
        perk_lbl = perk_font.render(PERK_CAPTION[variant], True, (210, 210, 230))
        # Word-wrap if needed
        wrap_w = sheet_w - 478 - 24
        if perk_lbl.get_width() <= wrap_w:
            sheet.blit(perk_lbl, (478, y0 + 70))
        else:
            words = PERK_CAPTION[variant].split()
            line = ""
            ly = y0 + 70
            for w in words:
                test = (line + " " + w).strip()
                if perk_font.render(test, True, (210, 210, 230)).get_width() <= wrap_w:
                    line = test
                else:
                    sheet.blit(perk_font.render(line, True, (210, 210, 230)),
                               (478, ly))
                    ly += 20
                    line = w
            if line:
                sheet.blit(perk_font.render(line, True, (210, 210, 230)),
                           (478, ly))
    return sheet


def main():
    out_dir = os.path.join(_REPO, "docs", "phoenix_design")
    os.makedirs(out_dir, exist_ok=True)
    # Per-variant tile renders (300×220 each) so each design can be
    # inspected on its own without cropping the contact sheet.
    for variant in VARIANTS:
        tile = pygame.Surface((300, 220), pygame.SRCALPHA)
        # Velvet background
        for y in range(220):
            t = y / 219
            tile.fill((int(20 + 6 * t), int(14 + 10 * t), int(36 + 14 * t)),
                      pygame.Rect(0, y, 300, 1))
        pip = render_pip_sprite(variant, size=140)
        tile.blit(pip, ((300 - 140) // 2, 12))
        pickup = render_pickup_icon(variant, size=80)
        tile.blit(pickup, (32, 150))
        hud_g = render_hud_glyph(variant, size=44)
        tile.blit(hud_g, (148, 168))
        name = _outlined(tile, variant.upper(), 26, (255, 220, 100))
        tile.blit(name, (200, 160))
        pygame.image.save(tile, os.path.join(out_dir, f"v_{variant}.png"))
        print(f"wrote v_{variant}.png")
    sheet = render_contact_sheet()
    out = os.path.join(out_dir, "_contact_sheet.png")
    pygame.image.save(sheet, out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
