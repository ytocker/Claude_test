"""Capture the live STORE → PARROTS tab exactly as a player sees it, both pages,
and stitch them into one side-by-side figure.

Renders the real ``StoreScene`` to the game canvas (no scratch builders, no
mock cards) so the figure reflects the shipped catalog: rarity ribbons, tier
gems, prices and the secret ``???`` mask all derive from store_catalog. Writes
the two raw page captures plus the combined figure under the wave2 docs dir.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))            # StoreScene thumbnails need a display

from game.config import W, H
from game.store import StoreScene

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.normpath(os.path.join(
    HERE, "..", "..", "docs", "store_redesign", "parrot", "wave2"))

PARROT_TAB = 1                             # ("COSTUMES", "PARROTS", ...) order


def _capture_pages():
    scene = StoreScene()
    scene.view = "category"
    scene.tab = PARROT_TAB
    pages = []
    for p in range(scene.n_pages):
        scene.page = p
        surf = pygame.Surface((W, H))
        scene.render(surf)
        out = os.path.join(DOCS, f"store_parrots_page{p + 1}.png")
        pygame.image.save(surf, out)
        pages.append(surf)
    return pages


def _stitch(pages):
    pad, title = 20, 40
    fig = pygame.Surface((W * len(pages) + pad * (len(pages) + 1), H + title + pad))
    fig.fill((12, 12, 20))
    f = pygame.font.SysFont("DejaVuSans", 22, bold=True)
    fig.blit(f.render("STORE — PARROTS tab (live), all pages", True,
                      (240, 240, 245)), (pad, 8))
    for i, page in enumerate(pages):
        fig.blit(page, (pad + i * (W + pad), title))
    out = os.path.join(DOCS, "store_parrots_live.png")
    pygame.image.save(fig, out)
    return out


pages = _capture_pages()
out = _stitch(pages)
print("wrote", out, "+", len(pages), "page captures")
