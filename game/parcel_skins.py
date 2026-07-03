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
from game.parcel_designs import (
    sack, takeout, jar, envelope, picnic,
    steamer, balloon, bottle,
    chest, lantern, flask,
    ufo, comet, snowglobe,
)


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


# id -> design module. Each module's ``build`` is mode-agnostic (the cosmetic
# shows its own look across every power-up); tilt/grow/ghost/snow still apply
# in entities.Bird.draw on top of whatever surface comes back.
_DESIGNS = {
    "parcel_sack":      sack,
    "parcel_takeout":   takeout,
    "parcel_jar":       jar,
    "parcel_envelope":  envelope,
    "parcel_picnic":    picnic,
    "parcel_steamer":   steamer,
    "parcel_balloon":   balloon,
    "parcel_bottle":    bottle,
    "parcel_chest":     chest,
    "parcel_lantern":   lantern,
    "parcel_flask":     flask,
    "parcel_ufo":       ufo,
    "parcel_comet":     comet,
    "parcel_snowglobe": snowglobe,
}

BUILDERS: "dict[str, object]" = {
    PARCEL_BASE: _build_base,
    **{pid: mod.build for pid, mod in _DESIGNS.items()},
}

ICONS: "dict[str, pygame.Surface]" = {
    PARCEL_BASE: _product_shot(parrot.get_parcel("normal")),
    **{pid: _product_shot(mod.build("normal")) for pid, mod in _DESIGNS.items()},
}
