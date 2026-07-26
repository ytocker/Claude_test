"""
Build the V5 hurt-parrot showcase: 7 panels side by side.

  Panel 0 — ORIGINAL (healthy Pip, frame angle +10°)
  Panel 1 — V3 battle-bloodshot
  Panels 2-6 — V5 round-2 concepts (bandaged-crisis, busted-aviator,
               defiant-snarl, ragged-molt, scorched-afterburn)

Each panel is the outlined 68×64 sprite scaled 8× NEAREST → 544×512 px.
"""
import importlib.util
import os
import sys

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import numpy as np
import pygame
from PIL import Image, ImageDraw, ImageFont

pygame.init()

# ── constants ─────────────────────────────────────────────────────────────────

SCALE     = 8
SPRITE_W  = 68    # outlined frame width (64 + 2px pad each side)
SPRITE_H  = 64    # outlined frame height (60 + 2px pad each side)
PANEL_W   = SPRITE_W * SCALE   # 544
PANEL_H   = SPRITE_H * SCALE   # 512
GAP       = 12
MARGIN    = 20
HDR_H     = 60
FTR_H     = 52
BG        = (8, 8, 20)

N_PANELS  = 7
CANVAS_W  = MARGIN + N_PANELS * PANEL_W + (N_PANELS - 1) * GAP + MARGIN
CANVAS_H  = MARGIN + HDR_H + GAP + PANEL_H + FTR_H + MARGIN


# ── outline helper ────────────────────────────────────────────────────────────

def _add_outline(src, outline_color=(20, 12, 18, 220)):
    pad = 2
    w, h = src.get_size()
    mask = pygame.mask.from_surface(src, threshold=8)
    sil  = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    out  = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == dy == 0:
                continue
            out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


# ── load frame helpers ────────────────────────────────────────────────────────

def _load_module(path):
    spec = importlib.util.spec_from_file_location("design", path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _surf_to_pil(surf):
    """Convert a pygame SRCALPHA surface to a PIL RGBA image."""
    arr = pygame.surfarray.array3d(surf)
    alpha = pygame.surfarray.array_alpha(surf)
    rgba = np.dstack([arr, alpha]).transpose(1, 0, 2)
    return Image.fromarray(rgba, "RGBA")


def _panel_image(outlined_surf):
    """Scale 68×64 outlined sprite by 8× using NEAREST → PIL Image."""
    scaled = pygame.transform.scale(outlined_surf, (PANEL_W, PANEL_H))
    return _surf_to_pil(scaled)


# ── panel definitions ─────────────────────────────────────────────────────────

REPO = "/home/user/skybit"

def _get_original():
    import game.parrot as parrot_mod
    raw = parrot_mod._build_frame(10)
    return _add_outline(raw)


def _get_v3_battle_bloodshot():
    mod = _load_module(f"{REPO}/docs/hurt-parrot-v3/battle-bloodshot/design.py")
    raw = mod._build_hurt_frame(10)
    return _add_outline(raw)


V5_SLUGS = [
    "bandaged-crisis",
    "busted-aviator",
    "defiant-snarl",
    "ragged-molt",
    "scorched-afterburn",
]


def _get_v5(slug):
    mod = _load_module(f"{REPO}/docs/hurt-parrot-v5/{slug}/design.py")
    # ragged-molt uses _build_hurt_frame; defiant-snarl uses build_defiant_snarl_frame
    if hasattr(mod, "_build_hurt_frame"):
        raw = mod._build_hurt_frame(10)
    elif hasattr(mod, "build_defiant_snarl_frame"):
        raw = mod.build_defiant_snarl_frame(10)
    else:
        raise AttributeError(f"No frame builder found in {slug}/design.py")
    return _add_outline(raw)


# ── text helpers ──────────────────────────────────────────────────────────────

def _font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (*BG, 255))
    draw   = ImageDraw.Draw(canvas)

    hdr_font  = _font(26, bold=True)
    slug_font = _font(18, bold=False)
    sub_font  = _font(13, bold=False)

    # Header
    title = "HURT PARROT · LAST LIFE · V5 ALL CONCEPTS"
    bbox  = draw.textbbox((0, 0), title, font=hdr_font)
    tx    = (CANVAS_W - (bbox[2] - bbox[0])) // 2
    ty    = MARGIN + (HDR_H - (bbox[3] - bbox[1])) // 2
    draw.text((tx, ty), title, font=hdr_font, fill=(255, 235, 200, 255))

    panel_top = MARGIN + HDR_H + GAP

    panels = [
        ("original", "ORIGINAL",  _get_original,            (140, 200, 140), ""),
        ("v3",       "battle-\nbloodshot", _get_v3_battle_bloodshot, (200, 200, 200), "V3"),
    ] + [
        (slug, slug, lambda s=slug: _get_v5(s), (255, 210, 80), "V5")
        for slug in V5_SLUGS
    ]

    for idx, (key, label, loader, name_color, version_tag) in enumerate(panels):
        x0 = MARGIN + idx * (PANEL_W + GAP)

        # Render frame
        outlined = loader()
        pil_panel = _panel_image(outlined)

        # Paste on dark bg sub-canvas so transparency shows the BG
        cell = Image.new("RGBA", (PANEL_W, PANEL_H), (*BG, 255))
        cell.paste(pil_panel, (0, 0), pil_panel)
        canvas.paste(cell, (x0, panel_top))

        # Thin separator line after ORIGINAL and after V3
        if idx in (0, 1):
            line_x = x0 + PANEL_W + GAP // 2
            draw.line([(line_x, panel_top - 4), (line_x, panel_top + PANEL_H + 4)],
                      fill=(60, 40, 80, 200), width=2)

        # Footer: slug name
        slug_y = panel_top + PANEL_H + 6
        bbox2  = draw.textbbox((0, 0), label, font=slug_font)
        lw     = bbox2[2] - bbox2[0]
        lines  = label.split("\n")
        line_h = slug_font.size + 2
        for li, ln in enumerate(lines):
            bb = draw.textbbox((0, 0), ln, font=slug_font)
            lw2 = bb[2] - bb[0]
            draw.text((x0 + (PANEL_W - lw2) // 2, slug_y + li * line_h),
                      ln, font=slug_font, fill=(*name_color, 255))

        tag_y = slug_y + len(lines) * line_h + 2
        if version_tag:
            bb3  = draw.textbbox((0, 0), version_tag, font=sub_font)
            draw.text((x0 + (PANEL_W - (bb3[2] - bb3[0])) // 2, tag_y),
                      version_tag, font=sub_font, fill=(120, 120, 150, 255))

    out_path = os.path.join(REPO, "docs", "hurt-parrot-v5-showcase.png")
    canvas.save(out_path)
    print(f"Saved {CANVAS_W}x{CANVAS_H} -> {out_path}")

    # Per-panel opaque-pixel check
    for idx, (key, label, loader, _, _) in enumerate(panels):
        x0 = MARGIN + idx * (PANEL_W + GAP)
        region = canvas.crop((x0, panel_top, x0 + PANEL_W, panel_top + PANEL_H))
        arr  = np.array(region)
        # Count non-background pixels (not exactly BG)
        not_bg = np.any(arr[:, :, :3] != np.array(BG), axis=2)
        count  = int(not_bg.sum())
        status = "OK" if count > 200 else "BLANK"
        print(f"  panel {idx} ({key}): {count} non-bg pixels  [{status}]")

    assert all(
        int(np.any(
            np.array(canvas.crop((MARGIN + i * (PANEL_W + GAP), panel_top,
                                  MARGIN + i * (PANEL_W + GAP) + PANEL_W,
                                  panel_top + PANEL_H)))[:, :, :3]
            != np.array(BG), axis=2
        ).sum()) > 200
        for i in range(N_PANELS)
    ), "One or more panels appear blank"

    print("All panels populated. Done.")


if __name__ == "__main__":
    main()
