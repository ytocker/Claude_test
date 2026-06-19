"""Store item catalog — pure data, no pygame.

Kept import-light (no pygame, no surface building) so the persistence
layer (game/store_data.py) and the headless unit tests can read prices
and validate inventory without pulling in the rendering stack.

Every entry is ``id -> {name, cost, kind}``:

  - ``kind`` is one of CATALOG_KINDS. New categories (pillar/ground/trail/
    boost) slot in without a schema change.
  - skin ids must each resolve in ``parrot.get_skin_frame``'s dispatch map;
    tests assert that the two stay in sync so a catalog entry can never
    point at a look the renderer can't draw.

``BASE_SKIN`` is the default parrot. It is implicitly owned and never
sold, so it is deliberately absent from CATALOG.
"""
from __future__ import annotations

BASE_SKIN = "skin_base"

CATALOG_KINDS = ("skin", "pillar", "ground", "trail", "boost")

# Costs are first-pass economy seeds — tuned once a full run's coin yield
# is measured against how long we want each unlock to feel like a goal.
CATALOG: dict[str, dict] = {
    "skin_tophat":   {"name": "TOP HAT",  "cost": 120, "kind": "skin"},
    "skin_skeleton": {"name": "SKELETON", "cost": 150, "kind": "skin"},
    "skin_kfc":      {"name": "FRIED",    "cost": 180, "kind": "skin"},
    "skin_ghost":    {"name": "GHOST",    "cost": 200, "kind": "skin"},
    "skin_dollar":   {"name": "DOLLAR",   "cost": 220, "kind": "skin"},
    "skin_knight":   {"name": "KNIGHT",   "cost": 250, "kind": "skin"},
}


def exists(item_id: str) -> bool:
    return item_id in CATALOG


def name(item_id: str) -> str:
    return CATALOG[item_id]["name"]


def cost(item_id: str) -> int:
    return CATALOG[item_id]["cost"]


def kind(item_id: str) -> str:
    return CATALOG[item_id]["kind"]


def ids_of_kind(k: str) -> list[str]:
    return [i for i, v in CATALOG.items() if v["kind"] == k]


def skin_ids() -> list[str]:
    return ids_of_kind("skin")


def cosmetic_ids() -> list[str]:
    """Everything the Prize Machine can hand out — every kind except the
    consumable boost lane (boosts are bought deliberately, never rolled)."""
    return [i for i, v in CATALOG.items() if v["kind"] != "boost"]
