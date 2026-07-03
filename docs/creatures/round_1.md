# Animal Store Skins — Round 1

Candidate module: `docs/creatures/creature_skins.py`
Review sheet: `docs/creatures/round_1.png`
Render script: `docs/creatures/_render_sheet.py`

NEW from-scratch creatures (NOT the macaw + accessory). Each is a full-body
flappy bird: animates over the 4 base wing poses (`parrot._WING_ANGLES`) and
rotates with the dive/climb tilt via the shared prebuilt-skin factory. Body
mass is kept near the base bird's body centre so the fixed 14px hitbox stays
fair — no oversized creatures.

The sheet shows each creature at HERO 130px plus the in-game 40px read at
level **and** at a dive tilt. The 40px crop is the truth test.

## Per-creature concept + what carries the 40px read

1. **Owl** — plush brown owl; heart-pair facial disc, two enormous white-ringed
   eyes, pointed ear-tufts. *Read: the giant forward eyes + facial disc.*
   Strong — instantly an owl at 40px.

2. **Toucan** — glossy blue-black body, white bib, an oversized banded
   yellow→orange→red beak longer than the head. *Read: the huge orange beak
   jutting forward.* Strong silhouette.

3. **Penguin** — fat egg body, black back / white belly two-tone, orange
   triangle beak, webbed feet, rosy cheek. *Read: the high-contrast B/W split +
   orange beak.* Strong, very clean.

4. **Bat** — purple fuzzy body, two leathery scalloped membrane wings that flap
   wide, pointed ears, cute fangs; the only non-feathered flapper. *Read: the
   membrane wing-span + ears.* Reads, but see weak-notes — the near wing can
   crowd the face on the level frame.

5. **Flamingo** — hot-pink body, iconic S-curve neck rising tall, down-hooked
   black-tipped beak, long folded legs. *Read: the pink S-neck + bent beak.*
   Strongest of the realistic set — colour + neck shape are unmistakable tiny.

6. **Bald Eagle** — dark-brown body, bold white head, fierce angled brow, big
   hooked yellow beak, white tail, talons. *Read: white-head/dark-body two-tone
   + the yellow hooked beak.* Strong, proud read.

7. **Bee** — chubby gold body with bold black abdomen stripes, translucent
   buzzing wings (small damped flutter, not a feather flap), big eyes, tiny
   antennae + stinger. *Read: the gold/black stripes + round body.* Strong; the
   damped-buzz animation is the right call for a bee.

8. **Dragon** *(premium gacha showpiece)* — a COMPACT bird-scale dragon: emerald
   scaled body, pale belly plates, dorsal spike ridge, back-swept horns, a
   snout with a nostril ember, teal membrane wings, gold-tipped spiked tail.
   *Read: horned snout + spiked tail + membrane wing.* Hero 130px feels suitably
   rare; see weak-notes — at 40px the wing dominates and the head/snout detail
   compresses, so it currently reads "small green winged thing" more than
   "dragon."

9. **Phoenix** *(premium gacha showpiece)* — a blazing firebird: molten
   red→gold body with a white-hot inner core, upswept flame crest above the
   crown, flame-feathered wings with ember tips, long upswept fire-plume tail.
   *Read: the flame crest + the red→gold fire gradient.* Strong, the most
   premium-feeling of the batch.

## Where I think the batch is weak (for the art-director)

- **Dragon (40px)** is the softest read. The near membrane wing covers much of
  the body and the horns/snout/spike-ridge are each individually small, so the
  gacha hero doesn't telegraph "dragon" at gameplay size as fast as the others.
  Candidate fixes for next round: bigger/longer horns that clear the crown,
  push the snout further forward as a bold wedge, and thin the near wing so the
  spiky head + tail ridge carry the silhouette.
- **Bat** level-frame: the near wing slightly overlaps the eyes. The dive frame
  reads cleaner. Could anchor the near wing lower or shrink it a touch so the
  face/ears stay clear in all four poses.
- **Toucan** dive-tilt: the long beak swings close to the body outline at steep
  tilt; worth checking it never reads as fused into the chest. Currently OK but
  flag for the tilt sweep.
- **Bee** body is slightly busy (3 stripes + stinger + antennae). Reads fine,
  but a 4th element could be dropped if the art-director wants it cleaner.

Strongest, lowest-risk reads: **Flamingo, Owl, Penguin, Phoenix.**

## Notes on the integration contract

- Each `build_<name>(wing_angle_deg)` returns a flat 64×84 composite (taller
  canvas for crests/tufts), body centred near the base anchor.
- Getters come from a local copy of `store_skins._make_prebuilt_skin` (4 cached
  flat frames + per-(frame, 3°) rotation cache + house outline).
- `BUILDERS` dict at the bottom is the liftable registry for a future
  `game/animal_skins.py` (`skin_owl`, `skin_toucan`, … `skin_phoenix`).
- No production file under `game/` was modified.
