"""PARCEL skins — swappable looks for the gift Pip carries below him.

The default parcel (the kraft box + red bow) lives in ``parrot.get_parcel``;
this module adds the purchasable parcel cosmetics for the PARCELS store tab.

Each builder returns a ``PARCEL_SIZE`` square sprite, built procedurally and
**mode-agnostic** — the cosmetic shows its own look across every power-up while
the existing draw code (entities.Bird.draw) still applies the tilt rotation,
grow-scale, ghost alpha-breath and snow overlay on top. Mirrors the
shoe/hat/glasses cosmetic modules so it auto-merges via parrot:

  * ``BUILDERS = {parcel_id: build(mode="normal") -> Surface}``  (in-game look)
  * ``ICONS    = {parcel_id: Surface}``                          (store card)

Designed parcel looks (Sack, Takeout, Jar, … Comet, Snowglobe) fold in here as
``build_<name>`` once their design loops land.
"""
import pygame

from game import parrot
from game.store_catalog import PARCEL_BASE


def _product_shot(sprite: pygame.Surface, box: int = 46) -> pygame.Surface:
    """Centre a parcel sprite on a transparent square for the store thumbnail
    (the card shows the parcel itself, like the shoe cards show the sneaker)."""
    out = pygame.Surface((box, box), pygame.SRCALPHA)
    s = pygame.transform.smoothscale(sprite, (box - 8, box - 8))
    out.blit(s, s.get_rect(center=(box // 2, box // 2)))
    return out


# The default kraft box reuses parrot's legacy palette parcel.
def _build_base(mode: str = "normal") -> pygame.Surface:
    return parrot.get_parcel(mode)


BUILDERS: "dict[str, object]" = {
    PARCEL_BASE: _build_base,
}

ICONS: "dict[str, pygame.Surface]" = {
    PARCEL_BASE: _product_shot(parrot.get_parcel("normal")),
}
