"""Render 5 SKATEBOARD powerup-icon design candidates in the
in-world kit palette (black + chrome + bone-white + red), all
painted at 4× supersample then smoothscale'd down for crisp
anti-aliased edges.

Each candidate is saved twice:
  * <label>.png         — icon centred on a transparent 56×56
                          surface scaled 6× to 336×336 for review
  * <label>_ingame.png  — composited onto a real gameplay frame
                          via build_world(), so the user can see
                          the icon in context

Plus a horizontal contact sheet `00_contact_sheet.png` with all 5.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_skateboard_icon_variants.py
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

from game.config import W, H
from game.entities import PowerUp
from tools.render_helmet_side_view_variants import (
    build_world, render_play_scene, _label_band,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_icon_variants")
os.makedirs(_OUT, exist_ok=True)


# ── kit palette ─────────────────────────────────────────────────────────────
DOME   = (10, 10, 18)     # near-black: dome fill / outlines / deck fill
SLATE  = (50, 50, 60)     # dome highlight / wheel ring
CHROME = (200, 200, 210)  # rim band / deck outline
BONE   = (240, 240, 230)  # skull / mohawk fin
TRUCK  = (60, 60, 70)     # truck / chinstrap-grey
RED    = (200, 50, 50)    # clip / wheel centre
CREAM  = (245, 240, 230)  # wheel
HALO   = (255, 180, 120)  # halo pulse colour


# ── shared helpers ──────────────────────────────────────────────────────────

def _halo(surf, cx, cy, pulse, r=22):
    """Standard alpha-pulsed warm halo behind the icon."""
    halo = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    a = int(60 + 30 * (0.5 + 0.5 * math.sin(pulse)))
    pygame.draw.circle(halo, (*HALO, a), (r + 2, r + 2), r)
    surf.blit(halo, (cx - r - 2, cy - r - 2))


def _ss_paint(paint_fn, native_w=56, native_h=56, ss=4):
    """Run paint_fn(big_surf, ss) on a 4× supersampled surface,
    then smoothscale down to native size for AA edges."""
    big = pygame.Surface((native_w * ss, native_h * ss), pygame.SRCALPHA)
    paint_fn(big, ss)
    return pygame.transform.smoothscale(big, (native_w, native_h))


# ── 5 icon variants ─────────────────────────────────────────────────────────

def draw_s1_stacked(surf, cx, cy, pulse):
    """S1 — Stacked helmet + mini board in the kit palette.
    Helmet on top with mohawk + chrome rim, board below with skull
    + 2 wheels with red centres."""
    _halo(surf, cx, cy, pulse, r=22)

    def paint(big, SS):
        # Helmet — half-dome at the top of the icon.
        bx = big.get_width() // 2
        by_helm = big.get_height() // 2 - 8 * SS
        hw = 22 * SS
        hh = 11 * SS
        # Top-half dome via blit-half trick.
        full = pygame.Surface((hw, hh * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(full, DOME, pygame.Rect(0, 0, hw, hh * 2))
        big.blit(full, (bx - hw // 2, by_helm), area=pygame.Rect(0, 0, hw, hh))
        # Highlight on forward-upper quadrant.
        hl = pygame.Surface((hw - 6 * SS, hh - 4 * SS), pygame.SRCALPHA)
        pygame.draw.ellipse(hl, SLATE,
                            pygame.Rect(0, 0, hw - 6 * SS, hh - 4 * SS))
        big.blit(hl, (bx - hw // 2 + 3 * SS, by_helm + SS),
                 area=pygame.Rect((hw - 6 * SS) // 2, 0,
                                  (hw - 6 * SS) // 2,
                                  (hh - 4 * SS) // 2 + 1))
        # Bone mohawk fin running front-to-back.
        fin = [
            (bx - hw // 2 + 3 * SS, by_helm + 1 * SS),
            (bx - 2 * SS,           by_helm - 3 * SS),
            (bx + 3 * SS,           by_helm - 2 * SS),
            (bx + hw // 2 - 4 * SS, by_helm + 2 * SS),
        ]
        pygame.draw.polygon(big, BONE, fin)
        pygame.draw.polygon(big, DOME, fin, SS)
        # Chrome rim band at the bottom of the dome.
        pygame.draw.rect(big, CHROME,
                         pygame.Rect(bx - hw // 2 - SS, by_helm + hh - SS,
                                     hw + 2 * SS, 2 * SS))

        # Board — dark deck below the helmet.
        by_board = by_helm + hh + 4 * SS
        deck_w = 26 * SS
        deck_h = 4 * SS
        deck = pygame.Rect(bx - deck_w // 2, by_board, deck_w, deck_h)
        pygame.draw.rect(big, CHROME, deck, border_radius=2 * SS)
        pygame.draw.rect(big, DOME, deck.inflate(-2 * SS, -2 * SS),
                         border_radius=SS)
        # Wheels with red centres.
        for sign in (-1, 1):
            wx = bx + sign * (deck_w // 2 - 3 * SS)
            wy = deck.bottom + 2 * SS
            pygame.draw.circle(big, SLATE, (wx, wy), 3 * SS)
            pygame.draw.circle(big, CREAM, (wx, wy), 2 * SS)
            pygame.draw.circle(big, RED,   (wx, wy), 1 * SS)
        return big

    icon = _ss_paint(paint)
    surf.blit(icon, icon.get_rect(center=(cx, cy)))


def draw_s2_helmet_solo(surf, cx, cy, pulse):
    """S2 — Punk-mohawk helmet alone, drawn larger so the silhouette
    + mohawk fin + side skull decal are all readable."""
    _halo(surf, cx, cy, pulse, r=22)

    def paint(big, SS):
        bx = big.get_width() // 2
        by = big.get_height() // 2 - 2 * SS
        hw = 28 * SS
        hh = 15 * SS
        # Top-half dome.
        full = pygame.Surface((hw, hh * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(full, DOME, pygame.Rect(0, 0, hw, hh * 2))
        big.blit(full, (bx - hw // 2, by - hh),
                 area=pygame.Rect(0, 0, hw, hh))
        # Highlight.
        hl = pygame.Surface((hw - 8 * SS, hh - 4 * SS), pygame.SRCALPHA)
        pygame.draw.ellipse(hl, SLATE,
                            pygame.Rect(0, 0, hw - 8 * SS, hh - 4 * SS))
        big.blit(hl, (bx - hw // 2 + 4 * SS, by - hh + SS),
                 area=pygame.Rect((hw - 8 * SS) // 2, 0,
                                  (hw - 8 * SS) // 2,
                                  (hh - 4 * SS) // 2 + 1))
        # Bone mohawk fin with 2 spikes.
        fin = [
            (bx - hw // 2 + 3 * SS, by - hh + SS),
            (bx - 2 * SS,           by - hh - 4 * SS),
            (bx + 3 * SS,           by - hh - 3 * SS),
            (bx + hw // 2 - 4 * SS, by - hh + 2 * SS),
        ]
        pygame.draw.polygon(big, BONE, fin)
        pygame.draw.polygon(big, DOME, fin, SS)
        for spike_x in (bx - 3 * SS, bx + 2 * SS):
            spike = [(spike_x, by - hh - 2 * SS),
                     (spike_x + SS, by - hh - 6 * SS),
                     (spike_x + 2 * SS, by - hh - 2 * SS)]
            pygame.draw.polygon(big, BONE, spike)
            pygame.draw.polygon(big, DOME, spike, SS)
        # Chrome rim band.
        pygame.draw.rect(big, CHROME,
                         pygame.Rect(bx - hw // 2 - SS, by - SS,
                                     hw + 2 * SS, 2 * SS))
        # Side skull decal.
        sk = pygame.Rect(0, 0, 5 * SS, 4 * SS)
        sk.center = (bx - 5 * SS, by - 4 * SS)
        pygame.draw.ellipse(big, BONE, sk)
        pygame.draw.ellipse(big, DOME, sk, SS)
        # Tiny red chinstrap clip dot.
        pygame.draw.circle(big, RED, (bx + 2 * SS, by + 4 * SS), 2 * SS)
        pygame.draw.circle(big, DOME, (bx + 2 * SS, by + 4 * SS), 2 * SS, SS)
        # Single strap line from rim to clip.
        pygame.draw.line(big, DOME, (bx - 4 * SS, by),
                         (bx + 2 * SS, by + 4 * SS), 2 * SS)
        return big

    icon = _ss_paint(paint)
    surf.blit(icon, icon.get_rect(center=(cx, cy)))


def draw_s3_board_skull(surf, cx, cy, pulse):
    """S3 — Tilted skateboard deck with bone skull + crossbones,
    chrome edge, 2 wheels with red centres. No helmet."""
    _halo(surf, cx, cy, pulse, r=22)

    def paint(big, SS):
        bx = big.get_width() // 2
        by = big.get_height() // 2
        deck_w = 30 * SS
        deck_h = 7 * SS
        # Paint deck horizontally on a sub-surface, then rotate.
        sub = pygame.Surface((deck_w + 12 * SS, deck_h + 8 * SS),
                              pygame.SRCALPHA)
        sx = sub.get_width() // 2
        sy = sub.get_height() // 2
        deck = pygame.Rect(0, 0, deck_w, deck_h)
        deck.center = (sx, sy)
        pygame.draw.rect(sub, CHROME, deck, border_radius=3 * SS)
        pygame.draw.rect(sub, DOME,
                         deck.inflate(-2 * SS, -2 * SS),
                         border_radius=2 * SS)
        # Crossbones diagonals.
        pygame.draw.line(sub, (235, 235, 225),
                         (deck.left + 4 * SS, deck.top + SS),
                         (deck.right - 4 * SS, deck.bottom - SS), SS)
        pygame.draw.line(sub, (235, 235, 225),
                         (deck.left + 4 * SS, deck.bottom - SS),
                         (deck.right - 4 * SS, deck.top + SS), SS)
        # Bone skull at deck centre.
        sk = pygame.Rect(0, 0, 8 * SS, 5 * SS)
        sk.center = (sx, sy)
        pygame.draw.ellipse(sub, BONE, sk)
        pygame.draw.ellipse(sub, DOME, sk, SS)
        # Eye sockets.
        for ex in (sk.centerx - 2 * SS, sk.centerx + SS):
            pygame.draw.circle(sub, DOME, (ex + SS // 2, sk.centery), SS)
        # Trucks + wheels.
        truck_h = 2 * SS
        wheel_r = 3 * SS
        for sign in (-1, 1):
            wx = sx + sign * (deck_w // 2 - 3 * SS)
            wy = deck.bottom + truck_h + wheel_r
            # truck
            tx = wx - 3 * SS
            pygame.draw.rect(sub, TRUCK,
                             (tx, deck.bottom, 6 * SS, truck_h))
            # wheel
            pygame.draw.circle(sub, SLATE, (wx, wy), wheel_r + SS)
            pygame.draw.circle(sub, CREAM, (wx, wy), wheel_r)
            pygame.draw.circle(sub, RED, (wx, wy), SS)
        # Tilt the whole deck a bit so it reads as 3D skateboard.
        rotated = pygame.transform.rotate(sub, 12)
        big.blit(rotated, rotated.get_rect(center=(bx, by)))
        return big

    icon = _ss_paint(paint)
    surf.blit(icon, icon.get_rect(center=(cx, cy)))


def draw_s4_jolly_roger(surf, cx, cy, pulse):
    """S4 — Bone skull centred with 2 crossed skateboard decks behind
    (X shape). Punk-pirate flag composition."""
    _halo(surf, cx, cy, pulse, r=22)

    def paint(big, SS):
        bx = big.get_width() // 2
        by = big.get_height() // 2
        # Two thin crossed decks behind the skull.
        for angle in (35, -35):
            sub_w = 36 * SS
            sub_h = 5 * SS
            sub = pygame.Surface((sub_w + 4 * SS, sub_h + 4 * SS),
                                  pygame.SRCALPHA)
            d = pygame.Rect(0, 0, sub_w, sub_h)
            d.center = (sub.get_width() // 2, sub.get_height() // 2)
            pygame.draw.rect(sub, CHROME, d, border_radius=2 * SS)
            pygame.draw.rect(sub, DOME, d.inflate(-2 * SS, -2 * SS),
                             border_radius=SS)
            # Truck-dot at each end.
            for sign in (-1, 1):
                wx = d.centerx + sign * (sub_w // 2 - 3 * SS)
                pygame.draw.circle(sub, CREAM, (wx, d.centery), 2 * SS)
                pygame.draw.circle(sub, RED, (wx, d.centery), SS)
            rotated = pygame.transform.rotate(sub, angle)
            big.blit(rotated, rotated.get_rect(center=(bx, by)))
        # Big bone skull centred on top.
        sk = pygame.Rect(0, 0, 18 * SS, 14 * SS)
        sk.center = (bx, by - SS)
        pygame.draw.ellipse(big, BONE, sk)
        pygame.draw.ellipse(big, DOME, sk, SS)
        # Eye sockets (big and dramatic).
        for ex in (sk.centerx - 4 * SS, sk.centerx + 2 * SS):
            pygame.draw.circle(big, DOME,
                               (ex + SS, sk.centery - SS), 2 * SS)
        # Nose triangle.
        pygame.draw.polygon(big, DOME, [
            (sk.centerx - SS, sk.centery + 2 * SS),
            (sk.centerx + SS, sk.centery + 2 * SS),
            (sk.centerx, sk.centery + 4 * SS),
        ])
        # Jaw line.
        pygame.draw.line(big, DOME,
                         (sk.centerx - 5 * SS, sk.bottom - 2 * SS),
                         (sk.centerx + 5 * SS, sk.bottom - 2 * SS), SS)
        # Teeth gaps.
        for tx in (-3 * SS, 0, 3 * SS):
            pygame.draw.line(big, DOME,
                             (sk.centerx + tx, sk.bottom - 4 * SS),
                             (sk.centerx + tx, sk.bottom - SS), SS)
        return big

    icon = _ss_paint(paint)
    surf.blit(icon, icon.get_rect(center=(cx, cy)))


def draw_s5_helmeted_pip(surf, cx, cy, pulse):
    """S5 — A tiny dark Pip-silhouette head wearing the punk-mohawk
    helmet. Reads as 'preview of what Pip will look like'."""
    _halo(surf, cx, cy, pulse, r=22)

    def paint(big, SS):
        bx = big.get_width() // 2
        by = big.get_height() // 2

        # Pip's head silhouette — small dark ellipse + tiny beak.
        head = pygame.Rect(0, 0, 14 * SS, 13 * SS)
        head.center = (bx + 2 * SS, by + 4 * SS)
        pygame.draw.ellipse(big, (140, 40, 50), head)  # dim red
        # Beak: small triangle pointing right.
        pygame.draw.polygon(big, (210, 130, 30), [
            (head.right - 2 * SS, head.centery - 2 * SS),
            (head.right + 4 * SS, head.centery + SS),
            (head.right - 2 * SS, head.centery + 3 * SS),
        ])
        # Tiny sunglasses dot.
        pygame.draw.circle(big, DOME,
                           (head.centerx + 4 * SS, head.centery - SS),
                           SS + 1)

        # Helmet on top of the head silhouette.
        helm_w = 18 * SS
        helm_h = 9 * SS
        helm_top_y = head.top - helm_h + 2 * SS
        helm_cx = head.centerx - SS
        # Top-half dome.
        full = pygame.Surface((helm_w, helm_h * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(full, DOME, pygame.Rect(0, 0, helm_w, helm_h * 2))
        big.blit(full, (helm_cx - helm_w // 2, helm_top_y),
                 area=pygame.Rect(0, 0, helm_w, helm_h))
        # Highlight.
        hl_w = helm_w - 6 * SS
        hl_h = helm_h - 3 * SS
        hl = pygame.Surface((hl_w, hl_h), pygame.SRCALPHA)
        pygame.draw.ellipse(hl, SLATE, pygame.Rect(0, 0, hl_w, hl_h))
        big.blit(hl, (helm_cx - helm_w // 2 + 3 * SS, helm_top_y + SS),
                 area=pygame.Rect(hl_w // 2, 0,
                                  hl_w // 2, hl_h // 2 + 1))
        # Bone mohawk fin.
        fin = [
            (helm_cx - helm_w // 2 + 2 * SS, helm_top_y + SS),
            (helm_cx - 2 * SS,                helm_top_y - 3 * SS),
            (helm_cx + 2 * SS,                helm_top_y - 2 * SS),
            (helm_cx + helm_w // 2 - 3 * SS,  helm_top_y + 2 * SS),
        ]
        pygame.draw.polygon(big, BONE, fin)
        pygame.draw.polygon(big, DOME, fin, SS)
        # Chrome rim band.
        pygame.draw.rect(big, CHROME,
                         pygame.Rect(helm_cx - helm_w // 2 - SS,
                                     helm_top_y + helm_h - SS,
                                     helm_w + 2 * SS, 2 * SS))
        # Small red chinstrap clip under the chin.
        pygame.draw.circle(big, RED,
                           (head.centerx + SS, head.bottom - SS), 2 * SS)
        return big

    icon = _ss_paint(paint)
    surf.blit(icon, icon.get_rect(center=(cx, cy)))


VARIANTS = [
    ("S1_stacked",       draw_s1_stacked,
     "S1: stacked helmet + mini board in kit palette"),
    ("S2_helmet_solo",   draw_s2_helmet_solo,
     "S2: punk-mohawk helmet alone (large)"),
    ("S3_board_skull",   draw_s3_board_skull,
     "S3: tilted skateboard deck with skull + crossbones"),
    ("S4_jolly_roger",   draw_s4_jolly_roger,
     "S4: bone skull centred + 2 crossed decks behind (X)"),
    ("S5_helmeted_pip",  draw_s5_helmeted_pip,
     "S5: tiny Pip-silhouette wearing the helmet"),
]


# ── output ──────────────────────────────────────────────────────────────────

def _icon_zoom_png(draw_fn, label):
    """56×56 transparent icon centred, scaled 6× for review."""
    base = pygame.Surface((56, 56), pygame.SRCALPHA)
    draw_fn(base, 28, 28, pulse=1.6)
    big = pygame.transform.scale(base, (56 * 6, 56 * 6))
    # Thin yellow frame so the icon reads as a UI tile.
    pygame.draw.rect(big, (255, 215, 0), big.get_rect(), 2)
    return big


def _ingame_png(draw_fn, label):
    """Render the icon on a real gameplay frame so the user sees it
    at native scale next to Pip."""
    world = build_world()
    frame = render_play_scene(world)
    # Place a single PowerUp at the typical spawn position (right of
    # the bird, mid-screen height) and draw the icon there.
    icon_cx = int(world.bird.x) + 110
    icon_cy = int(world.bird.y)
    base = pygame.Surface((56, 56), pygame.SRCALPHA)
    draw_fn(base, 28, 28, pulse=1.6)
    frame.blit(base, base.get_rect(center=(icon_cx, icon_cy)))
    return frame


def main():
    saved = []
    for label, fn, caption in VARIANTS:
        icon_zoom = _icon_zoom_png(fn, label)
        ingame    = _ingame_png(fn, label)
        zoom_path   = os.path.join(_OUT, f"{label}.png")
        ingame_path = os.path.join(_OUT, f"{label}_ingame.png")
        pygame.image.save(icon_zoom, zoom_path)
        pygame.image.save(ingame, ingame_path)
        saved.append((label, caption, icon_zoom))
        print(f"saved {zoom_path}")
        print(f"saved {ingame_path}")

    # Contact sheet — 5 icons in a row with labels.
    cell_w = saved[0][2].get_width()
    cell_h = saved[0][2].get_height()
    band_h = 56
    gap    = 12
    sheet_w = len(saved) * cell_w + (len(saved) - 1) * gap + 24
    sheet_h = cell_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, caption, icon) in enumerate(saved):
        x = 12 + idx * (cell_w + gap)
        sheet.blit(icon, (x, 12))
        band = _label_band(cell_w, label, caption, height=band_h)
        sheet.blit(band, (x, 12 + cell_h))
    sheet_path = os.path.join(_OUT, "00_contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/skateboard_icon_variants")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_ingame.png")


if __name__ == "__main__":
    main()
