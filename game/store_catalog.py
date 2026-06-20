"""Store item catalog — pure data, no pygame.

Kept import-light (no pygame, no surface building) so the persistence
layer (game/store_data.py) and the headless unit tests can read prices
and validate inventory without pulling in the rendering stack.

Every entry is ``id -> {name, cost, kind, group}``:

  - ``kind`` is one of CATALOG_KINDS. New categories (pillar/ground/trail/
    boost) slot in without a schema change.
  - ``group`` is one of GROUPS — the store's browsing tab (costume / parrot /
    animal). Purely a UI grouping; the renderer and gacha ignore it.
  - skin ids must each resolve in ``parrot.get_skin_frame``'s dispatch map;
    tests assert that the two stay in sync so a catalog entry can never
    point at a look the renderer can't draw.

``BASE_SKIN`` is the default parrot. It is implicitly owned and never
sold, so it is deliberately absent from CATALOG (the store surfaces it as a
free DEFAULT card in the PARROTS tab).
"""
from __future__ import annotations

BASE_SKIN = "skin_base"

CATALOG_KINDS = ("skin", "pillar", "ground", "trail", "boost")

# Store browsing tabs, in display order.
GROUPS = ("costume", "parrot", "animal", "shoes", "hats")

# Cost ladder is tuned so the first unlock is a goal (a few good runs) rather
# than a side effect of session one: entry ~260, mid ~450-550, premium ~650-800,
# fantasy showpieces ~1200-1500. Coin *earn* is left untouched (gameplay feel);
# the daily reward gives a steady drip toward the higher tiers.
CATALOG: dict[str, dict] = {
    # ── COSTUMES (accessories/restyles on the macaw) ──────────────────────────
    "skin_tophat":   {"name": "TOP HAT",   "cost": 260, "kind": "skin", "group": "costume"},
    "skin_pirate":   {"name": "PIRATE",    "cost": 280, "kind": "skin", "group": "costume"},
    "skin_skeleton": {"name": "SKELETON",  "cost": 300, "kind": "skin", "group": "costume"},
    "skin_cowboy":   {"name": "COWBOY",    "cost": 320, "kind": "skin", "group": "costume"},
    "skin_ninja":    {"name": "NINJA",     "cost": 340, "kind": "skin", "group": "costume"},
    "skin_kfc":      {"name": "FRIED",     "cost": 360, "kind": "skin", "group": "costume"},
    "skin_ghost":    {"name": "GHOST",     "cost": 450, "kind": "skin", "group": "costume"},
    "skin_viking":   {"name": "VIKING",    "cost": 450, "kind": "skin", "group": "costume"},
    "skin_zombie":   {"name": "ZOMBIE",    "cost": 480, "kind": "skin", "group": "costume"},
    "skin_wizard":   {"name": "WIZARD",    "cost": 480, "kind": "skin", "group": "costume"},
    "skin_knight":   {"name": "KNIGHT",    "cost": 550, "kind": "skin", "group": "costume"},
    "skin_astronaut": {"name": "ASTRONAUT", "cost": 650, "kind": "skin", "group": "costume"},
    "skin_pharaoh":  {"name": "PHARAOH",   "cost": 700, "kind": "skin", "group": "costume"},
    "skin_crown":    {"name": "CROWN",     "cost": 750, "kind": "skin", "group": "costume"},
    "skin_disco":    {"name": "DISCO",     "cost": 800, "kind": "skin", "group": "costume"},

    # ── PARROTS (full-body species recolours) ─────────────────────────────────
    "skin_bluegold":  {"name": "BLUE MACAW",  "cost": 280, "kind": "skin", "group": "parrot"},
    "skin_amazon":    {"name": "AMAZON",      "cost": 300, "kind": "skin", "group": "parrot"},
    "skin_sunconure": {"name": "SUN CONURE",  "cost": 360, "kind": "skin", "group": "parrot"},
    "skin_hyacinth":  {"name": "HYACINTH",    "cost": 450, "kind": "skin", "group": "parrot"},
    "skin_cockatoo":  {"name": "COCKATOO",    "cost": 520, "kind": "skin", "group": "parrot"},
    "skin_lorikeet":  {"name": "LORIKEET",    "cost": 600, "kind": "skin", "group": "parrot"},

    # ── ANIMALS (from-scratch creatures) ──────────────────────────────────────
    "skin_bee":      {"name": "BEE",       "cost": 400,  "kind": "skin", "group": "animal"},
    "skin_owl":      {"name": "OWL",       "cost": 480,  "kind": "skin", "group": "animal"},
    "skin_toucan":   {"name": "TOUCAN",    "cost": 480,  "kind": "skin", "group": "animal"},
    "skin_penguin":  {"name": "PENGUIN",   "cost": 520,  "kind": "skin", "group": "animal"},
    "skin_bat":      {"name": "BAT",       "cost": 520,  "kind": "skin", "group": "animal"},
    "skin_flamingo": {"name": "FLAMINGO",  "cost": 560,  "kind": "skin", "group": "animal"},
    "skin_eagle":    {"name": "EAGLE",     "cost": 700,  "kind": "skin", "group": "animal"},
    "skin_dragon":   {"name": "DRAGON",    "cost": 1200, "kind": "skin", "group": "animal"},
    "skin_phoenix":  {"name": "PHOENIX",   "cost": 1500, "kind": "skin", "group": "animal"},

    # ── SHOES (stylized procedural sneaker/sandal homages Pip wears) ───────────
    # Priced on desirability: sandals/slides cheap, classics mid, hype premium.
    "skin_shoe_flipflops":  {"name": "FLIP-FLOPS",  "cost": 240, "kind": "skin", "group": "shoes"},
    "skin_shoe_poolslides": {"name": "POOL SLIDES", "cost": 300, "kind": "skin", "group": "shoes"},
    "skin_shoe_courtgreen": {"name": "COURT GREEN", "cost": 420, "kind": "skin", "group": "shoes"},
    "skin_shoe_canvashigh": {"name": "CANVAS HIGH", "cost": 460, "kind": "skin", "group": "shoes"},
    "skin_shoe_checkerslip": {"name": "CHECKER SLIP", "cost": 480, "kind": "skin", "group": "shoes"},
    "skin_shoe_shelltoe":   {"name": "SHELL TOE",   "cost": 540, "kind": "skin", "group": "shoes"},
    "skin_shoe_airflyer":   {"name": "AIR FLYER",   "cost": 620, "kind": "skin", "group": "shoes"},
    "skin_shoe_airbubble":  {"name": "AIR BUBBLE",  "cost": 680, "kind": "skin", "group": "shoes"},
    "skin_shoe_boostknit":  {"name": "BOOST KNIT",  "cost": 760, "kind": "skin", "group": "shoes"},
    "skin_shoe_retro1":     {"name": "RETRO 1",     "cost": 850, "kind": "skin", "group": "shoes"},

    # ── HATS (stylized procedural headwear Pip wears, NY cap as the hero) ──────
    # Priced on desirability: novelty/casual cheap, classics mid-high, the
    # seasonal Santa and the signature NY cap premium.
    "skin_hat_partyhat":  {"name": "PARTY HAT",     "cost": 220, "kind": "skin", "group": "hats"},
    "skin_hat_visor":     {"name": "VISOR",         "cost": 240, "kind": "skin", "group": "hats"},
    "skin_hat_strawhat":  {"name": "STRAW HAT",     "cost": 260, "kind": "skin", "group": "hats"},
    "skin_hat_beanie":    {"name": "BEANIE",        "cost": 300, "kind": "skin", "group": "hats"},
    "skin_hat_beret":     {"name": "BERET",         "cost": 320, "kind": "skin", "group": "hats"},
    "skin_hat_buckethat": {"name": "BUCKET HAT",    "cost": 360, "kind": "skin", "group": "hats"},
    "skin_hat_flatcap":   {"name": "FLAT CAP",      "cost": 380, "kind": "skin", "group": "hats"},
    "skin_hat_propeller": {"name": "PROPELLER CAP", "cost": 420, "kind": "skin", "group": "hats"},
    "skin_hat_trucker":   {"name": "TRUCKER CAP",   "cost": 440, "kind": "skin", "group": "hats"},
    "skin_hat_snapback":  {"name": "SNAPBACK",      "cost": 460, "kind": "skin", "group": "hats"},
    "skin_hat_gradcap":   {"name": "GRAD CAP",      "cost": 500, "kind": "skin", "group": "hats"},
    "skin_hat_chef":      {"name": "CHEF TOQUE",    "cost": 520, "kind": "skin", "group": "hats"},
    "skin_hat_bowler":    {"name": "BOWLER",        "cost": 560, "kind": "skin", "group": "hats"},
    "skin_hat_fedora":    {"name": "FEDORA",        "cost": 600, "kind": "skin", "group": "hats"},
    "skin_hat_sombrero":  {"name": "SOMBRERO",      "cost": 640, "kind": "skin", "group": "hats"},
    "skin_hat_santa":     {"name": "SANTA HAT",     "cost": 700, "kind": "skin", "group": "hats"},
    "skin_hat_nycap":     {"name": "NY CAP",        "cost": 850, "kind": "skin", "group": "hats"},
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


def group(item_id: str) -> str:
    return CATALOG[item_id].get("group", "costume")


def ids_of_group(g: str) -> list[str]:
    """Catalog ids in a store tab (costume / parrot / animal), in catalog order."""
    return [i for i, v in CATALOG.items() if v.get("group", "costume") == g]


def skin_ids() -> list[str]:
    return ids_of_kind("skin")


def cosmetic_ids() -> list[str]:
    """Everything the Prize Machine can hand out — every kind except the
    consumable boost lane (boosts are bought deliberately, never rolled)."""
    return [i for i, v in CATALOG.items() if v["kind"] != "boost"]
