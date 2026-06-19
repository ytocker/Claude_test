# Animal Store Skins — Round 2

Candidate module: `docs/creatures/creature_skins.py`
Review sheet: `docs/creatures/round_2.png`
Render script: `docs/creatures/_render_sheet.py`

Round 1 returned **ITERATE**: 7 creatures ship as-is; the two premium gacha
showpieces (Dragon, Phoenix) failed/weakened at 40px and the Bat near wing
crowded the face. This round implements the art-director punch list and adds
the honest truth test. **No `game/` file was touched.**

## The truth test changed (punch-list item 6)

`round_2.png` now shows, per creature: HERO 130px (left), a smooth 40px
level + dive reference (top-right), and a **NEAREST-NEIGHBOR x3 magnified**
40px level + dive (bottom-right). The 40px read is first smoothscaled DOWN to
the true gameplay pixel grid (down-sampling honestly), then magnified back up
with nearest-neighbor so we inspect exactly those gameplay pixels with no
extra smoothing flattering tiny detail. Dragon + Phoenix lead the sheet with
gold-rimmed cards so the two fixed showpieces are prominent.

## What changed vs round 1

### Dragon (items 1–3)
- **Near wing (item 1):** shrunk ~20% (`scale=0.8`) and rotated far more OPEN
  (`-40` vs `-12`, less horizontal) and re-anchored to `(BCX-11, BCY+1)`. It
  no longer lies flat across the snout + dorsal ridge — it now sits as
  supporting mass behind the spiky head/tail silhouette. The topmost finger
  strut was also pulled off the membrane apex so the open wing doesn't throw a
  thin dark spike up next to the horns.
- **Horns (item 2):** extended from `CROWN_Y-5` to `CROWN_Y-10/-11`, given a
  dark back-flank for contrast and a bright tip glint. The horned crown now
  breaks clearly ABOVE the near wing in all four flap poses — the cheapest
  "dragon" signal at tiny size now owns the top.
- **Snout (item 3):** rebuilt as a bolder, longer forward wedge (out to
  `HCX+17`, chunkier quad with a bright top facet), with a nostril notch and
  the glowing ember moved to the very tip, visually separated from the body
  ellipse. Net 40px read order is now horns → snout → tail spikes, with the
  wing as supporting mass.

### Phoenix (item 4)
- **Crest only** — the red→gold body gradient and the fire-plume tail are
  untouched. The thin single-polygon crest slivers were replaced with three
  **fat rounded flame tongues** (deep-red back, orange centre lick tallest,
  gold forward tongue) plus a bright inner heart and a white-hot core dot. A
  clear flame shape now clears the crown at 40px nearest, where the old thin
  tips disappeared.

### Bat (item 5)
- Near-wing anchor lowered ~4px (`BCY-2` → `BCY+2`) and the wing surface
  shrunk ~15% (`scale=0.85`). Both eyes and both ears now stay fully clear on
  the level frame in every pose, matching the already-clean dive frame.

## The other 7 — unchanged (SHIP)
Owl, Toucan, Penguin, Flamingo, Bald Eagle, Bee are byte-for-byte unchanged
from round 1 per the brief. Bee antennae were left as-is (the optional drop
was non-trivial and not worth disturbing a shipping creature).

## Proposed final names (gameplay store labels)
- **Owl** — "Hoot"
- **Toucan** — "Mango"
- **Penguin** — "Pebble"
- **Bat** — "Echo"
- **Flamingo** — "Coco"
- **Bald Eagle** — "Liberty"
- **Bee** — "Buzz"
- **Dragon** — "Ember" *(gacha showpiece)*
- **Phoenix** — "Blaze" *(gacha showpiece)*

## Ship-readiness (my proposal, not a self-verdict)
All nine now hold their signature read at the 40px nearest-neighbor truth
test. The 7 untouched creatures remain ship-ready; Dragon and Phoenix have had
every flagged note addressed — horns clear the wing, the snout reads as a bold
forward wedge with a tip ember, and the Phoenix crest is now a fat flame that
survives the downscale.

## Integration contract (unchanged)
- Each `build_<name>(wing_angle_deg)` returns a flat 64×84 composite, body
  centred near the base anchor so the fixed 14px hitbox stays fair.
- Getters come from the local copy of `store_skins._make_prebuilt_skin`
  (4 cached flat frames + per-(frame, 3°) rotation cache + house outline).
- `BUILDERS` at the bottom maps `skin_<animal>` → getter, liftable into a
  future `game/animal_skins.py`.
