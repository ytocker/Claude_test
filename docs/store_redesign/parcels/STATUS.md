# PARCELS category — status tracker

Tracking doc for the **PARCELS** store tab (the gift Pip carries below him).
Branch: `v5_store_parcels`. Last updated: 2026-06-26.

A parcel is a mode-agnostic ~22px sprite carried below Pip that rotates with his
bank. Builders live in `game/parcel_designs/<name>.py` (each exposes
`build(mode="normal") -> Surface`), are registered in `game/parcel_skins.py`
(`BUILDERS` + `ICONS`), dispatched by `parrot.get_parcel(mode, parcel_id)`, and
catalogued in `game/store_catalog.py`. Rarity is **derived from price**
(`_RARITY_BANDS`): common `<400`, rare `400–799`, epic `800–2499`, legendary
`≥2500`.

## Current roster — 20 items (+ free DEFAULT)

| Item | id | Price | Tier | Builder | Notes |
|---|---|---|---|---|---|
| DEFAULT (kraft box) | `parcel_base` | free | common | `parrot.get_parcel` (legacy) | implicitly owned, never sold |
| NO PARCEL | `parcel_none` | 120 | common | `parcel_skins._build_none` | empty look; hitbox unchanged (cosmetic parity) |
| AIRMAIL | `parcel_airmail` | 200 | common | `airmail.py` | mail set |
| LOVE LETTER | `parcel_love` | 240 | common | `love_letter.py` | mail set |
| POSTMARK | `parcel_postmark` | 260 | common | `post_office.py` | mail set |
| TAKEOUT PAIL | `parcel_takeout` | 290 | common | `takeout.py` | |
| WATER BOTTLE | `parcel_plastic` | 320 | common | `plastic_bottle.py` | PET bottle (id stayed `parcel_plastic`) |
| PICNIC BASKET | `parcel_picnic` | 370 | common | `picnic.py` | |
| TUMBLER | `parcel_tumbler` | 440 | rare | `tumbler.py` | drink set |
| COCONUT | `parcel_coconut` | 500 | rare | `coconut.py` | drink set |
| SOCCER BALL | `parcel_soccer` | 560 | rare | `ball_soccer.py` | sports set (26px / 6× SS) |
| BASKETBALL | `parcel_basketball` | 600 | rare | `ball_basketball.py` | sports set |
| TENNIS BALL | `parcel_tennis` | 640 | rare | `ball_tennis.py` | sports set |
| BASEBALL | `parcel_baseball` | 690 | rare | `ball_baseball.py` | sports set |
| FOOTBALL | `parcel_football` | 740 | rare | `ball_football.py` | sports set (oval silhouette) |
| GOLD COIN | `parcel_coin` | 900 | epic | `coin.py` | reuses the EXACT in-game coin (`entities._get_coin_face`) |
| DIAMOND | `parcel_diamond` | 1500 | epic | `diamond.py` | brilliant-cut gem |
| TREASURE CHEST | `parcel_chest` | 2200 | epic | `chest.py` | |
| MINI PIP | `parcel_minipip` | 3500 | legendary | `mini_pip.py` | baby Pip; hi-res 168px → 28px |
| FINEST WHISKEY | `parcel_whiskey` | 9000 | legendary · **secret** | `parcel_whiskey.py` | mystery: rolls 1-of-4 drams at unlock |
| SNOWGLOBE | `parcel_snowglobe` | 9500 | legendary · **secret** | `snowglobe.py` | masked ??? until bought |

**Tier distribution:** 7 common · 7 rare · 3 epic · 3 legendary (2 of the
legendaries are secret/masked).

## Special mechanics

- **NO PARCEL** (`parcel_none`): renders a transparent sprite so nothing shows,
  but Pip's parcel collision circle (`PARCEL_R`) is left intact — equipping it
  changes only the look, never difficulty (the cosmetic-parity rule).
- **FINEST WHISKEY** (`parcel_whiskey`): a single SECRET item whose look is a
  random 1-of-4 dram — **CRYSTAL DECANTER / SCOTCH FIFTH / SQUARE BOURBON /
  CASKED DRAM** — rolled uniformly at purchase and locked for good. Mirrors the
  `skin_jet_fighter` pattern: `store_data._roll_skin_variant` rolls + persists
  the index; `parcel_whiskey.sync_from_store()` (called from
  `store._commit_purchase`) binds the rolled dram for the card + run. The four
  looks (`whiskey_decanter/scotch/bourbon/cask.py`) are NOT separately
  catalogued, so the surprise holds.
- **GOLD COIN** (`parcel_coin`): not a new design — reuses `entities._get_coin_face()`
  (rope rim, gold gradient, embossed parrot, specular), scaled to 22px.
- **Secret items** (`secret: True`): FINEST WHISKEY + SNOWGLOBE show as masked
  **???** mystery cards in the store until purchased.

## Code map

- Catalog entries + tier comments: `game/store_catalog.py` (PARCELS block).
- Builder/icon registry: `game/parcel_skins.py` (`_DESIGNS`, `BUILDERS`, `ICONS`).
- Dispatch: `parrot.get_parcel(mode, parcel_id)` → `parcel_skins.BUILDERS`.
- Mystery dispatcher: `game/parcel_whiskey.py` (`POOL_SIZE`, `sync_from_store`).
- Per-item builders: `game/parcel_designs/*.py`.

## Figures (committed under `docs/store_redesign/parcels/`)

- `parcels_gallery.png` — every parcel carried by Pip mid-flight.
- `parcels_store_cards.png` — all store cards (3 pages stitched).
- Per-design exploration sheets under `docs/store_redesign/parcels/<item>/`
  (envelope, whiskey, sports_balls, parrot_child, coin, diamond, …) and the
  parcel render harness `docs/parcels/_parcel_lib.py`.

## Design provenance

Built via the `item-design` skill loop (graphics-designer ↔ art-director) where
applicable; sports balls were authored at the 2-designer/1-critic cap then bumped
to 6× supersample. Exploration scratch (round sheets, candidates) lives under
`docs/store_redesign/parcels/` and is excluded from the pygbag bundle.

## Removed along the way (history)

Original kraft ENVELOPE (superseded by AIRMAIL/LOVE LETTER/POSTMARK), MACHINE GUN
(too small to read at parcel size), squeeze-bottle WATER BOTTLE (name reused by
the PET bottle), JAM JAR, DIM SUM STEAMER, MINI UFO, BURLAP SACK, GENIE FLASK,
PAPER LANTERN, MESSAGE BOTTLE, HOT-AIR BALLOON, COMET.

## Verification

- `SDL_VIDEODRIVER=dummy python -m pytest tests/` → green (incl. the parcel
  contract tests in `tests/test_store.py`: every parcel resolves to a square
  ≥`PARCEL_SIZE` builder + a product-shot icon).
- Both build targets unaffected (procedural art only; no `pygame.mixer` / web
  paths touched).
