# Skybit Store — Full Status

**Branch:** `v5_store` · **HEAD:** `e034ae11`

This is the single source of truth for the coin store: the landing screen, which
stalls are active vs. reserved for future work, the card design, and every
category's full roster (prices, tiers, secrets). Figures are procedural captures.

---

## Landing screen — Lagoon Stilt-Market hub

The store opens onto the **lagoon stilt-market hub** (`game/store_hub.py`): a
tropical, over-water golden-hour village where each of the 7 categories is a
thatched stall on stilts. Pip banks across the upper sky; a gold balance capsule
and a "TAP A STALL" chip sit up top. The palette dissolves into the dark-indigo +
gold **constellation** jewel store the stalls open into.

**Navigation** (`game/store.py:StoreScene`):
- Land on the hub → tap an **open** stall → that category's card grid.
- **BACK** on a category → returns to the hub. **BACK** on the hub → exits the store.
- Device-back mirrors this (category → hub → exit).

**Reference:** `docs/store_bazaar/lagoon_stilt/hub_ingame.png` (live in-game) ·
`docs/store_bazaar/lagoon_stilt/round_4@2x.png` (design).

---

## Active vs. future stalls (launch gating)

| Stall | State | On tap |
|---|---|---|
| **COSTUMES** | 🟢 Open | opens the category grid |
| **PARROTS** | 🟢 Open | opens the category grid |
| **PARCELS** | 🟢 Open | opens the category grid |
| ANIMALS | 🔒 Closed (future) | silent no-op |
| SHOES | 🔒 Closed (future) | silent no-op |
| HATS | 🔒 Closed (future) | silent no-op |
| SHADES | 🔒 Closed (future) | silent no-op |

Closed stalls render as an **anonymous rolled bamboo blind** (no label, no preview
dome, no text) with a cool "dormant" veil so they read asleep while the open three
stay warm (`game/store_hub_closed.py`). A tap on a closed stall does nothing.

**Re-opening is a one-line change** — the shut set is a single config:

```python
# game/store_hub.py
CLOSED_GROUPS = frozenset({"animal", "shoes", "hats", "shades"})
```

Remove a group to open its stall (renders normally + becomes clickable); empty the
set to restore the full all-open 7-stall hub. The full open hub art is untouched
and kept for the future. **Reference:** `docs/store_bazaar/closed_stalls/round_2@2x.png`.

---

## Category card design

Tapping an open stall shows a paged grid of **constellation "crest, no-burst" jewel
cards** (`game/store_cards.py`): indigo body + gold bevel, a glass cabochon thumb
disc with the real item preview, a faceted **tier gem** rank badge, a notched
**rarity ribbon** (COMMON / RARE / EPIC / LEGENDARY / MYSTERY), a cream item name,
and a gold **price** chip / green **EQUIPPED** chip. Secret items are masked as
`??? MYSTERY` until purchased. A buy-confirm modal gates every coin spend.

**Reference:** `docs/store_redesign/constellation_hi/store.png`.

**Rarity tiers** (by price): `< 500 = common · < 900 = rare · < 2000 = epic · ≥ 2000 = legendary`.

**Free DEFAULT card:** PARROTS, SHADES, and PARCELS are fronted by a free "DEFAULT"
card (`skin_base` / `parcel_base`) to revert to the base look. It is implicitly
owned and not part of the paid catalog below.

---

## COSTUMES (14) — 🟢 open

| Name | ID | Cost | Tier |
|---|---|---|---|
| PIRATE | skin_pirate | 280 | common |
| COWBOY | skin_cowboy | 320 | common |
| PHARAOH | skin_pharaoh | 380 | common |
| CROWN | skin_crown | 450 | common |
| GENTLEMAN | skin_tophat | 520 | rare |
| NINJA | skin_ninja | 560 | rare |
| VIKING | skin_viking | 600 | rare |
| WIZARD | skin_wizard | 720 | rare |
| BASEBALL | skin_baseball | 950 | epic |
| BASKETBALL | skin_basketball | 950 | epic |
| TENNIS | skin_tennis | 1,000 | epic |
| MUMMY | skin_mummy | 1,100 | epic |
| CAPTAIN | skin_pilot | 2,200 | legendary |
| ASTRONAUT | skin_astronaut | 2,600 | legendary |

---

## PARROTS (17, + free DEFAULT) — 🟢 open

Full-body recolored macaws. (SKELETON, ZOMBIE, DISCO currently live here as
recolor skins.)

| Name | ID | Cost | Tier | Secret |
|---|---|---|---|---|
| SKELETON | skin_skeleton | 300 | common | |
| ZOMBIE | skin_zombie | 480 | common | |
| BLUE MACAW | skin_bluegold | 280 | common | |
| AMAZON | skin_amazon | 300 | common | |
| SUN CONURE | skin_sunconure | 360 | common | |
| HYACINTH | skin_hyacinth | 450 | common | |
| COCKATOO | skin_cockatoo | 520 | rare | |
| LORIKEET | skin_lorikeet | 600 | rare | |
| DISCO | skin_disco | 800 | rare | |
| PRISM | skin_prism | 1,400 | epic | |
| THORNCREST | skin_thorncrest | 1,700 | epic | |
| EMBERMOTH | skin_embermoth | 1,900 | epic | |
| AURORA MACAW | skin_aurora | 2,800 | legendary | |
| MOONBLOOM | skin_moonbloom | 3,200 | legendary | |
| TEMPEST CONDOR | skin_tempest | 3,600 | legendary | |
| BINKY ⭐ | skin_binky | 6,000 | legendary | secret |
| CHROME MACAW ⭐ | skin_chrome | 9,500 | legendary | secret |

---

## ANIMALS (21) — 🔒 closed (future)

From-scratch creatures (full bird replacement).

| Name | ID | Cost | Tier | Secret |
|---|---|---|---|---|
| BEE | skin_bee | 200 | common | |
| OWL | skin_owl | 280 | common | |
| TOUCAN | skin_toucan | 340 | common | |
| PENGUIN | skin_penguin | 420 | common | |
| BAT | skin_bat | 490 | common | |
| FLAMINGO | skin_flamingo | 560 | rare | |
| PUFFERFISH | skin_pufferfish | 640 | rare | |
| CHAMELEON | skin_chameleon | 720 | rare | |
| EAGLE | skin_eagle | 900 | epic | |
| RED PANDA | skin_red_panda | 1,100 | epic | |
| SUGAR GLIDER | skin_sugar_glider | 1,400 | epic | |
| MANTIS SHRIMP | skin_mantis_shrimp | 1,800 | epic | |
| DRAGON | skin_dragon | 2,300 | legendary | |
| KITSUNE | skin_kitsune | 3,500 | legendary | |
| PAPER PLANE ⭐ | skin_paper_plane | 5,000 | legendary | secret |
| SUN ⭐ | skin_sun | 6,000 | legendary | secret |
| BURRO PIÑATA ⭐ | skin_pinata_burro | 7,000 | legendary | secret |
| CACTUS PIÑATA ⭐ | skin_pinata_cactus | 8,000 | legendary | secret |
| FLYING TOASTER ⭐ | skin_toaster | 9,000 | legendary | secret |
| PARROT PIÑATA ⭐ | skin_pinata_parrot | 10,500 | legendary | secret |
| JET FIGHTER ⭐ | skin_jet_fighter | 12,000 | legendary | secret |

---

## SHOES (15) — 🔒 closed (future)

| Name | ID | Cost | Tier |
|---|---|---|---|
| FLIP-FLOPS | skin_shoe_flipflops | 240 | common |
| POOL SLIDES | skin_shoe_poolslides | 300 | common |
| COURT GREEN | skin_shoe_courtgreen | 420 | common |
| CANVAS HIGH | skin_shoe_canvashigh | 460 | common |
| CHECKER SLIP | skin_shoe_checkerslip | 480 | common |
| SHELL TOE | skin_shoe_shelltoe | 540 | rare |
| AIR FLYER | skin_shoe_airflyer | 620 | rare |
| AIR BUBBLE | skin_shoe_airbubble | 680 | rare |
| BOOST KNIT | skin_shoe_boostknit | 760 | rare |
| MEGA DAD | skin_shoe_megadad | 780 | rare |
| RETRO 1 | skin_shoe_retro1 | 850 | rare |
| JELLYCORE | skin_shoe_jellycore | 1,200 | epic |
| NEON CIRCUIT | skin_shoe_neoncircuit | 1,800 | epic |
| WING BOOTS | skin_shoe_wingboots | 3,200 | legendary |
| AFTERBURNER | skin_shoe_afterburner | 4,800 | legendary |

---

## HATS (17) — 🔒 closed (future)

| Name | ID | Cost | Tier |
|---|---|---|---|
| PARTY HAT | skin_hat_partyhat | 220 | common |
| VISOR | skin_hat_visor | 240 | common |
| STRAW HAT | skin_hat_strawhat | 260 | common |
| BEANIE | skin_hat_beanie | 300 | common |
| BERET | skin_hat_beret | 320 | common |
| BUCKET HAT | skin_hat_buckethat | 360 | common |
| FLAT CAP | skin_hat_flatcap | 380 | common |
| PROPELLER CAP | skin_hat_propeller | 420 | common |
| TRUCKER CAP | skin_hat_trucker | 440 | common |
| SNAPBACK | skin_hat_snapback | 460 | common |
| GRAD CAP | skin_hat_gradcap | 500 | rare |
| CHEF TOQUE | skin_hat_chef | 520 | rare |
| BOWLER | skin_hat_bowler | 560 | rare |
| FEDORA | skin_hat_fedora | 600 | rare |
| SOMBRERO | skin_hat_sombrero | 640 | rare |
| SANTA HAT | skin_hat_santa | 700 | rare |
| NY CAP | skin_hat_nycap | 850 | rare |

---

## SHADES (12, + free DEFAULT) — 🔒 closed (future)

`NO SHADES` is a paid option that removes eyewear (bare-eyed Pip).

| Name | ID | Cost | Tier |
|---|---|---|---|
| NO SHADES | skin_shades_none | 120 | common |
| NERD SPECS | skin_shades_nerd | 180 | common |
| ROUND SHADES | skin_shades_round | 220 | common |
| HEART SHADES | skin_shades_heart | 240 | common |
| STAR SHADES | skin_shades_star | 260 | common |
| BLACK SHADES | skin_shades_black | 300 | common |
| WHITE RETRO | skin_shades_white | 320 | common |
| 3D GLASSES | skin_shades_3d | 360 | common |
| PIXEL SHADES | skin_shades_pixel | 400 | common |
| SKI GOGGLES | skin_shades_ski | 440 | common |
| MONOCLE | skin_shades_monocle | 480 | common |
| CYBER VISOR | skin_shades_cyber | 560 | rare |

---

## PARCELS (20, + free DEFAULT) — 🟢 open

The gift Pip carries below him. `NO PARCEL` is a paid option that hides the parcel.

| Name | ID | Cost | Tier | Secret |
|---|---|---|---|---|
| NO PARCEL | parcel_none | 120 | common | |
| AIRMAIL | parcel_airmail | 200 | common | |
| LOVE LETTER | parcel_love | 240 | common | |
| POSTMARK | parcel_postmark | 260 | common | |
| TAKEOUT PAIL | parcel_takeout | 290 | common | |
| WATER BOTTLE | parcel_plastic | 320 | common | |
| PICNIC BASKET | parcel_picnic | 370 | common | |
| TUMBLER | parcel_tumbler | 440 | common | |
| COCONUT | parcel_coconut | 500 | rare | |
| SOCCER BALL | parcel_soccer | 560 | rare | |
| BASKETBALL | parcel_basketball | 600 | rare | |
| TENNIS BALL | parcel_tennis | 640 | rare | |
| BASEBALL | parcel_baseball | 690 | rare | |
| FOOTBALL | parcel_football | 740 | rare | |
| GOLD COIN | parcel_coin | 900 | epic | |
| DIAMOND | parcel_diamond | 1,500 | epic | |
| TREASURE CHEST | parcel_chest | 2,200 | legendary | |
| MINI PIP | parcel_minipip | 3,500 | legendary | |
| FINEST WHISKEY ⭐ | parcel_whiskey | 9,000 | legendary | secret |
| SNOWGLOBE ⭐ | parcel_snowglobe | 9,500 | legendary | secret |

⭐ = masked as `??? MYSTERY` in the store until purchased.

---

## Totals

| Category | Items | Secret | Stall |
|---|---|---|---|
| Costumes | 14 | 0 | 🟢 open |
| Parrots | 17 (+DEFAULT) | 2 | 🟢 open |
| Animals | 21 | 7 | 🔒 closed |
| Shoes | 15 | 0 | 🔒 closed |
| Hats | 17 | 0 | 🔒 closed |
| Shades | 12 (+DEFAULT) | 0 | 🔒 closed |
| Parcels | 20 (+DEFAULT) | 2 | 🟢 open |
| **Total** | **116 paid** | **11** | **3 open / 4 closed** |

Plus 2 free DEFAULT cards (`skin_base`, `parcel_base`).

---

## Source of truth (code)

| Concern | File |
|---|---|
| Item roster (names, costs, groups, tiers, secrets) | `game/store_catalog.py` |
| Store scene: hub↔category nav, card grid, buy-confirm, wallet UI | `game/store.py` |
| Landing hub (lagoon stilt-market) + open/closed gating config | `game/store_hub.py` |
| Closed-stall bamboo blind | `game/store_hub_closed.py` |
| Constellation crest cards | `game/store_cards.py` |
| Wallet / ownership / equip / daily (native + web) | `game/store_data.py` |
| Per-category reference galleries (store card + on-Pip gameplay) | `docs/store_gallery/*.png` |

> Note: some `docs/store_gallery/*.png` figures lag the latest catalog after the
> recent category-expansion merges (parcels, parrots, shoes, animals, costumes).
> Regenerate via `tools/capture_store_galleries.py` when a refresh is wanted.
