"""Skateboard pickup redesign — original-mouth BEFORE/AFTER sheet.

Each of the round-3 candidates wears oversized BONE buck teeth, a
stylistic break from the shipped Jolly Roger sticker, which uses a
single horizontal DOME jaw line (closed mouth, no teeth). This sheet
shows every candidate side-by-side with its teeth dropped and only the
canonical jaw line remaining, so the user can pick the mouth idiom that
ships.

Implementation: reuse the round-3 candidate renderers verbatim. For the
AFTER column we monkey-patch the module-level _draw_buck_teeth to a
no-op so the buck-teeth call inside each render_concept_* function
becomes inert; the jaw line is drawn by a separate pygame.draw.line
call that's untouched.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \\
        python3 tools/render_skateboard_redesign_before_after.py
"""

import math
import os
import sys
import pygame

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_skateboard_redesign_round_3 as r3  # noqa: E402


PAL = r3.PAL
DOME, CHROME, BONE, CREAM, RED = (
    r3.DOME, r3.CHROME, r3.BONE, r3.CREAM, r3.RED,
)
CARD_BG = r3.CARD_BG
SHEET_BG = r3.SHEET_BG
LABEL = r3.LABEL
SUBLABEL = r3.SUBLABEL
NATIVE = r3.NATIVE
ZOOM = r3.ZOOM


CONCEPTS = [
    ("A", "PUNK STUDDED SKULL-BUNNY"),
    ("B", "SKULL-BUNNY HYBRID + MOHAWK"),
    ("C", "PUNK PATCH BUNNY"),
    ("D", "SHRED-DECK GRAFFITI BUNNY"),
]


def render_with_mouth(letter, apply_original_mouth):
    real_buck = r3._draw_buck_teeth
    if apply_original_mouth:
        r3._draw_buck_teeth = lambda *a, **k: None
    try:
        renderer = {
            "A": r3.render_concept_a,
            "B": r3.render_concept_b,
            "C": r3.render_concept_c,
            "D": r3.render_concept_d,
        }[letter]
        return renderer()
    finally:
        r3._draw_buck_teeth = real_buck


def _font(size, bold=False):
    try:
        return pygame.font.SysFont("DejaVu Sans", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)


def _draw_cell(sheet, x, y, label_text, sub_tag, icon_96, panel_w, panel_h):
    """One cell: charcoal card, 2-line label header, 96 px native + 4x zoom."""
    PAD = 16
    NATIVE_W = NATIVE
    ZOOM_W = NATIVE * ZOOM

    card = pygame.Rect(x, y, panel_w, panel_h)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=10)
    pygame.draw.rect(sheet, (44, 50, 60), card, 1, border_radius=10)

    head_font = _font(18, bold=True)
    head = head_font.render(label_text, True, LABEL)
    sheet.blit(head, (card.left + PAD, card.top + 8))

    tag_font = _font(13)
    tag = tag_font.render(sub_tag, True, SUBLABEL)
    sheet.blit(tag, (card.left + PAD,
                     card.top + 8 + head.get_height() + 2))

    header_h = 8 + head.get_height() + 2 + tag.get_height() + 6

    native_x = card.left + PAD
    native_y = card.top + header_h + PAD + (ZOOM_W - NATIVE_W) // 2
    sheet.blit(icon_96, (native_x, native_y))
    sub_font = _font(12)
    sub = sub_font.render("96 px native", True, SUBLABEL)
    sheet.blit(sub, (native_x + (NATIVE_W - sub.get_width()) // 2,
                     native_y + NATIVE_W + 4))

    zoom = pygame.transform.scale(icon_96, (ZOOM_W, ZOOM_W))
    zoom_x = native_x + NATIVE_W + PAD
    zoom_y = card.top + header_h + PAD
    sheet.blit(zoom, (zoom_x, zoom_y))
    sub2 = sub_font.render(f"{ZOOM}x zoom (review detail)", True, SUBLABEL)
    sheet.blit(sub2, (zoom_x + (ZOOM_W - sub2.get_width()) // 2,
                      zoom_y + ZOOM_W + 4))

    return card


def _nearest_palette(rgb):
    best = None
    best_d = 1e9
    for name, ref in PAL.items():
        d = sum((a - b) ** 2 for a, b in zip(rgb, ref))
        if d < best_d:
            best_d = d
            best = (name, ref)
    return best, math.sqrt(best_d)


def main():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()

    shipped = r3.render_shipped()
    before_icons = {l: render_with_mouth(l, False) for l, _n in CONCEPTS}
    after_icons = {l: render_with_mouth(l, True) for l, _n in CONCEPTS}

    PAD = 16
    TITLE_H = 96
    NATIVE_W = NATIVE
    ZOOM_W = NATIVE * ZOOM

    HEADER_H = 8 + 24 + 2 + 18 + 6
    PANEL_H = HEADER_H + ZOOM_W + PAD * 2 + 20
    PANEL_W = ZOOM_W + NATIVE_W + PAD * 3
    COL_GAP = 24

    n_rows = 1 + len(CONCEPTS)
    sheet_w = PANEL_W * 2 + COL_GAP + PAD * 2
    sheet_h = TITLE_H + PAD + (PANEL_H + PAD) * n_rows

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(SHEET_BG)

    title_text = "SKATEBOARD redesign  —  original-mouth before/after"
    sub_text = ("Buck teeth (round 3, LEFT) vs. original Jolly Roger jaw "
                "line (RIGHT). Mouth swap only; every other element is "
                "identical.")
    target_title_w = sheet_w - PAD * 4
    title_pt = 28
    title_font = _font(title_pt, bold=True)
    title = title_font.render(title_text, True, LABEL)
    if title.get_width() > target_title_w:
        title_pt = 22
        title_font = _font(title_pt, bold=True)
        title = title_font.render(title_text, True, LABEL)
        print(f"title fallback: dropped to {title_pt} pt "
              f"(width now {title.get_width()})")
    sub_font = _font(15)
    sub = sub_font.render(sub_text, True, SUBLABEL)
    sheet.blit(title, (PAD * 2, PAD + 4))
    sheet.blit(sub, (PAD * 2, PAD + 4 + title.get_height() + 4))

    y = TITLE_H + PAD
    x_left = PAD
    x_right = PAD + PANEL_W + COL_GAP

    _draw_cell(sheet, x_left, y,
               "SHIPPED (S4 Jolly Roger)",
               "SHIPPED (canonical) — left",
               shipped, PANEL_W, PANEL_H)
    _draw_cell(sheet, x_right, y,
               "SHIPPED (S4 Jolly Roger)",
               "SHIPPED (canonical) — right",
               shipped, PANEL_W, PANEL_H)
    y += PANEL_H + PAD

    for letter, name in CONCEPTS:
        _draw_cell(sheet, x_left, y,
                   f"{letter}.  {name}",
                   "BEFORE — buck teeth (round 3)",
                   before_icons[letter], PANEL_W, PANEL_H)
        _draw_cell(sheet, x_right, y,
                   f"{letter}.  {name}",
                   "AFTER — original Jolly Roger mouth",
                   after_icons[letter], PANEL_W, PANEL_H)
        y += PANEL_H + PAD

    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs", "skateboard_redesign", "before_after.png",
    )
    pygame.image.save(sheet, out_path)
    print(f"wrote {out_path} ({sheet.get_width()}x{sheet.get_height()})")

    teeth_probes = {
        "A": [(44, 68), (52, 68), (44, 74), (52, 74)],
        "B": [(44, 64), (52, 64), (44, 70), (52, 70)],
        "C": [(44, 56), (52, 56), (44, 62), (52, 62)],
        "D": [(40, 56), (48, 60), (56, 64), (44, 70)],
    }
    print("\n--- BEFORE column tooth probes (BONE/CREAM expected) ---")
    for letter, probes in teeth_probes.items():
        icon = before_icons[letter]
        hits = 0
        for px, py in probes:
            rgba = icon.get_at((px, py))
            rgb = (rgba.r, rgba.g, rgba.b)
            (pname, _ref), dist = _nearest_palette(rgb)
            is_tooth = pname in ("BONE", "CREAM") and dist <= 30 \
                and rgba.a > 0
            if is_tooth:
                hits += 1
        print(f"  BEFORE {letter}: {hits}/{len(probes)} tooth hits")

    print("\n--- AFTER column tooth probes (lower is better — buck "
          "teeth absent, only jaw line remains) ---")
    for letter, probes in teeth_probes.items():
        icon = after_icons[letter]
        hits = 0
        for px, py in probes:
            rgba = icon.get_at((px, py))
            rgb = (rgba.r, rgba.g, rgba.b)
            (pname, _ref), dist = _nearest_palette(rgb)
            is_tooth = pname in ("BONE", "CREAM") and dist <= 30 \
                and rgba.a > 0
            if is_tooth:
                hits += 1
        print(f"  AFTER  {letter}: {hits}/{len(probes)} tooth hits")

    # Sanity: did the patch take? Sample a row just below each jaw line
    # in both columns and count non-transparent pixels. AFTER should
    # show fewer opaque pixels there because the teeth aren't drawn.
    print("\n--- Below-jaw opacity diff (BEFORE - AFTER, higher = more "
          "tooth pixels removed) ---")
    below_jaw_y = {"A": 80, "B": 76, "C": 70, "D": 76}
    for letter, name in CONCEPTS:
        b = before_icons[letter]
        a = after_icons[letter]
        py = below_jaw_y[letter]
        b_opaque = sum(1 for px in range(NATIVE)
                       if b.get_at((px, py)).a > 16)
        a_opaque = sum(1 for px in range(NATIVE)
                       if a.get_at((px, py)).a > 16)
        print(f"  {letter} at y={py}: before={b_opaque} opaque, "
              f"after={a_opaque} opaque, diff={b_opaque - a_opaque}")

    print("\nDONE — before/after sheet saved.")


if __name__ == "__main__":
    main()
