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
    sack, takeout, picnic,
    balloon, bottle,
    chest, lantern, flask,
    comet, snowglobe,
    airmail, love_letter, post_office,
    water_bottle, plastic_bottle, tumbler, coconut,
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


# NO PARCEL — the empty-handed look. The in-game sprite is fully transparent so
# nothing is drawn below Pip. His parcel collision-hitbox (PARCEL_R) is left
# untouched in world.py, so equipping this changes only the look, never the
# difficulty — the same cosmetic-parity rule every other parcel obeys.
def _build_none(mode: str = "normal") -> pygame.Surface:
    return pygame.Surface((parrot.PARCEL_SIZE, parrot.PARCEL_SIZE),
                          pygame.SRCALPHA)


def _none_icon(box: int = 46) -> pygame.Surface:
    """Store-card glyph for NO PARCEL: a faint grey ghost of the kraft box, so
    the card reads as 'the parcel slot, empty'. Parcels are shown by an icon
    (the test contract), so unlike NO SHADES it can't fall back to a blank."""
    ghost = parrot.get_parcel("normal").copy()
    ghost.fill((148, 154, 168, 255), special_flags=pygame.BLEND_RGB_MULT)
    ghost.fill((255, 255, 255, 105), special_flags=pygame.BLEND_RGBA_MULT)
    out = pygame.Surface((box, box), pygame.SRCALPHA)
    s = pygame.transform.smoothscale(ghost, (box - 8, box - 8))
    out.blit(s, s.get_rect(center=(box // 2, box // 2)))
    return out


# id -> design module. Each module's ``build`` is mode-agnostic (the cosmetic
# shows its own look across every power-up); tilt/grow/ghost/snow still apply
# in entities.Bird.draw on top of whatever surface comes back.
_DESIGNS = {
    "parcel_sack":      sack,
    "parcel_takeout":   takeout,
    "parcel_airmail":   airmail,
    "parcel_love":      love_letter,
    "parcel_postmark":  post_office,
    "parcel_water":     water_bottle,
    "parcel_plastic":   plastic_bottle,
    "parcel_tumbler":   tumbler,
    "parcel_coconut":   coconut,
    "parcel_picnic":    picnic,
    "parcel_balloon":   balloon,
    "parcel_bottle":    bottle,
    "parcel_chest":     chest,
    "parcel_lantern":   lantern,
    "parcel_flask":     flask,
    "parcel_comet":     comet,
    "parcel_snowglobe": snowglobe,
}

BUILDERS: "dict[str, object]" = {
    PARCEL_BASE: _build_base,
    "parcel_none": _build_none,
    **{pid: mod.build for pid, mod in _DESIGNS.items()},
}

ICONS: "dict[str, pygame.Surface]" = {
    PARCEL_BASE: _product_shot(parrot.get_parcel("normal")),
    "parcel_none": _none_icon(),
    **{pid: _product_shot(mod.build("normal")) for pid, mod in _DESIGNS.items()},
}
