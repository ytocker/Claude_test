# ANIMALS category — current roster

21 items across 4 tiers. Secret items display as ??? in the store until purchased.

## Roster

| # | skin id | Name | Cost | Tier | Secret |
|---|---------|------|------|------|--------|
| 1 | `skin_bee` | BEE | 200 | common | |
| 2 | `skin_owl` | OWL | 280 | common | |
| 3 | `skin_toucan` | TOUCAN | 340 | common | |
| 4 | `skin_penguin` | PENGUIN | 420 | rare | |
| 5 | `skin_bat` | BAT | 490 | rare | |
| 6 | `skin_flamingo` | FLAMINGO | 560 | rare | |
| 7 | `skin_pufferfish` | PUFFERFISH | 640 | rare | |
| 8 | `skin_chameleon` | CHAMELEON | 720 | rare | |
| 9 | `skin_eagle` | EAGLE | 900 | epic | |
| 10 | `skin_red_panda` | RED PANDA | 1100 | epic | |
| 11 | `skin_sugar_glider` | SUGAR GLIDER | 1400 | epic | |
| 12 | `skin_mantis_shrimp` | MANTIS SHRIMP | 1800 | epic | |
| 13 | `skin_dragon` | DRAGON | 2300 | epic | |
| 14 | `skin_kitsune` | KITSUNE | 3500 | legendary | |
| 15 | `skin_paper_plane` | PAPER PLANE | 5000 | legendary | ??? |
| 16 | `skin_sun` | SUN | 6000 | legendary | ??? |
| 17 | `skin_pinata_burro` | BURRO PIÑATA | 7000 | legendary | ??? |
| 18 | `skin_pinata_cactus` | CACTUS PIÑATA | 8000 | legendary | ??? |
| 19 | `skin_toaster` | FLYING TOASTER | 9000 | legendary | ??? |
| 20 | `skin_pinata_parrot` | PARROT PIÑATA | 10500 | legendary | ??? |
| 21 | `skin_jet_fighter` | JET FIGHTER | 12000 | legendary | ??? |

Rarity bands (from `store_catalog._RARITY_BANDS`): common < 400 · rare 400–799 · epic 800–2499 · legendary ≥ 2500.

## Tier rationale

**Common (200–340):** BEE, OWL, TOUCAN — simple iconic shapes, accessible within 2–3 runs. The entry hook for new players.

**Rare (420–720):** Five creatures spaced ~70 coins apart. FLAMINGO stays at 560 (natural midpoint). CHAMELEON sits at the rare ceiling (720) — its colour-shifting complexity justifies it.

**Epic (900–2300):** Five aspirational items. EAGLE opens the epic tier (first purple card the player sees). DRAGON at 2300 is the epic capstone — a deliberate trophy before legendary opens.

**Legendary (3500):** KITSUNE is the sole visible legendary, acting as the store's aspiration anchor. Players can see it and aim for it.

**Secret legendary (5000–12000):** Seven items masked as ??? until purchased. Price is always visible. SUN is special — it rolls a random one of two designs (classic / kawaii) at unlock, then locks to that variant. The piñata trio (BURRO, CACTUS, PARROT) forms a thematic collectible set.

## Store pages

- **Page 1:** BEE · OWL · TOUCAN · PENGUIN · BAT · FLAMINGO · PUFFERFISH · CHAMELEON
- **Page 2:** EAGLE · RED PANDA · SUGAR GLIDER · MANTIS SHRIMP · DRAGON · KITSUNE · PAPER PLANE · SUN
- **Page 3:** BURRO PIÑATA · CACTUS PIÑATA · FLYING TOASTER · PARROT PIÑATA · JET FIGHTER

Reference figures (branch `claude/nice-bell-g1p9mm`):
- `docs/store_redesign/animal/animal_store_pages.png` — all 3 pages as players see them
- `docs/store_redesign/animal/animal_store_pages_revealed.png` — same with secrets shown
- `docs/store_redesign/animal/animal_overview.png` — all 21 skins mid-flight

## Removed items

The following were cut to tighten the lineup:

| Name | Reason |
|------|--------|
| AXOLOTL | Overlapped the epic tier without enough visual distinction |
| GRIFFIN | Removed — winged fantasy creature slot owned by DRAGON and KITSUNE |
| PHOENIX | Removed — fire-bird concept too close to DRAGON |
| THUNDERBIRD | Removed — lightning-bird concept; archived under `docs/store_redesign/animal/thunderbird/` |
| COSMIC JELLY | Removed — repositioned as potential future item |
| AURORA STAG | Removed — repositioned as potential future item |
| UFO | Removed from secret tier — repositioned as potential future item |

Builder code for all removed items is retained in the codebase and can be re-registered without rebuilding art.
