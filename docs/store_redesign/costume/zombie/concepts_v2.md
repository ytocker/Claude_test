# Zombie Parrot Concepts — Batch v2 (design_6 → design_10)

Five NEW undead sub-genres, none overlapping the shipped batch
(Roadkill / Crypt Rot / Voodoo Hex / Lab Specimen / Bloated Gas-Bag).
All read as a ~64×64 parrot skin shown at **40px** in flight, so every
tell below is a **big high-contrast block** — filled voids, thick lines,
silhouette-breaking lumps, or a single hard glow. Fine texture is banned;
it turns to mush at size.

Ranked 1–5 by strength of zombie read at 40px.

---

## RANK 1 — design_6 · `skin_zombie_fungal`
### "SPORE-BURST HOST BODY"
*(fungal / cordyceps infection)*

- **HERO SILHOUETTE:** The parrot's own outline is broken by 3 fat
  mushroom caps sprouting off the back and skull — the shape no longer
  reads as "clean bird," it reads as "something growing OUT of a bird."
  That silhouette break is the single most zombie-legible thing in the set.
- **ZOMBIE ELEMENTS (draw calls):**
  1. **Cap fruiting bodies:** 3 filled half-circle domes (`pygame.draw.ellipse`
     clipped to top half) at skull, mid-back, tail base — sizes ~14/11/8px,
     each with a 2px darker rim arc so it reads as a mushroom, not a bump.
  2. **Glowing gill-slit under each cap:** one short thick `draw.line`
     (3px) in luminous cyan across the cap's underside — the only bright
     accent, pops against the dull host body.
  3. **Mycelium veins on the body:** 3–4 thick branching `draw.line`
     segments (2px, pale grey-green) radiating from each cap root — read
     as infection spread, not detail noise, because they're few and thick.
  4. **Dead eye:** single filled dark ellipse with a tiny fungal dot pupil
     (2 concentric filled circles), glassy and clouded.
- **PALETTE:** body `#6E7A5A` (sickly infected olive), decay `#3B4230`
  (deep shadow / cap rims), cap flesh `#C9BFA2` (pale bone-mushroom),
  spore glow `#8CF2D0` (cyan-green accent), vein `#A9B58C`.
- **DISTINCTNESS:** The only concept that *breaks the parrot outline* with
  growths — a fungus theme none of the 10 prior/peer designs touch (Gas-Bag
  swelled the body but kept it smooth; this erupts through it).

---

## RANK 2 — design_7 · `skin_zombie_burned`
### "CHARRED EMBER REVENANT"
*(burned / ash-crust zombie)*

- **HERO SILHOUETTE:** A near-black parrot cracked open by molten orange
  seams — extreme value contrast that survives ANY sky, day or night. Reads
  instantly as "burnt thing still moving."
- **ZOMBIE ELEMENTS (draw calls):**
  1. **Charcoal crust body:** base fill in near-black, then 4–5 thick jagged
     `draw.line` "crack" seams (3px) in ember orange running down the chest
     and wing — like cooling lava lines. Big and few, not hatching.
  2. **Ember glow core:** one filled orange circle + a larger low-alpha halo
     circle (glow cache) at the chest crack junction — a single hot heart
     that pulses. This is the concept's beacon tell.
  3. **Peeled-jaw beak:** the beak drawn as two split charred polygons with an
     ember line between (`draw.polygon` ×2 + `draw.line`) — a crisped, hanging
     mouth read.
  4. **Ash-flake shimmer:** 3–4 tiny drifting light-grey particles rising off
     the back (reuse particle system) — subtle motion tell, drops cleanly if
     perf-limited.
- **PALETTE:** char `#1C1A18` (body), cooling grey `#4A4340` (crust highs),
  ember `#FF6A1E` (crack accent), hot core `#FFC24A` (glow), ash `#C6C0B8`.
- **DISTINCTNESS:** Pure fire-death theme with the highest value contrast in
  the set; where design_9 (nuclear alternative was cut) and Fungal use cool
  glows, this owns hot orange — and no prior design was charred.

---

## RANK 3 — design_8 · `skin_zombie_drowned`
### "BARNACLE DROWNED WRETCH"
*(deep-sea / waterlogged zombie)*

- **HERO SILHOUETTE:** A bloated, sagging blue-grey parrot draped in a heavy
  seaweed shawl, one glowing anglerfish lure dangling in front of its face —
  the dangling light bulb over a dead face is the money read.
- **ZOMBIE ELEMENTS (draw calls):**
  1. **Anglerfish lure:** a thin stalk `draw.line` from the forehead ending in
     a filled glow circle + halo (bioluminescent bulb) hanging in front of the
     beak — the one bright point, unmistakable and unique.
  2. **Barnacle clusters:** 4–5 small filled concentric-ring circles
     (`draw.circle` ×2 each, off-white on grey) clumped on shoulder and cheek —
     chunky crustacean lumps, big enough to read.
  3. **Seaweed drape:** 3 thick wavy `draw.line` / thin-polygon ribbons (green)
     hanging off the back and tail — sway with the flap, reads as waterlogged
     drift.
  4. **Milky drowned eye:** filled pale-blue-white ellipse, no visible pupil —
     the classic dead-fish stare.
- **PALETTE:** waterlogged flesh `#5C7A82` (body), deep decay `#2E4048`
  (shadow), pale bloat `#9FB6B4`, seaweed `#3C6B3A` (accent), lure glow
  `#B9F0FF`.
- **DISTINCTNESS:** The only aquatic-death concept; cool teal palette + a
  dangling front-of-face light give it a silhouette no land zombie shares.

---

## RANK 4 — design_9 · `skin_zombie_soldier`
### "TRENCH-DEAD WAR PARROT"
*(zombie soldier / war dead)*

- **HERO SILHOUETTE:** A dull green parrot under a dented steel helmet, with a
  clear dark bullet-hole void punched through the chest — the helmet dome
  changes the head outline enough to shout "soldier" from 3 feet.
- **ZOMBIE ELEMENTS (draw calls):**
  1. **Helmet:** a filled steel half-ellipse dome over the skull + a wide
     `draw.rect` brim, with one 2px rivet dot — reshapes the silhouette, the
     primary tell.
  2. **Bullet wound:** one filled near-black circle on the chest with a thin
     dark ring around it (`draw.circle` ×2) — a clean punched hole, high
     contrast on the pallid body.
  3. **Dog tags:** two tiny filled rounded rects on a thin `draw.line` chain
     across the chest — small but the metallic accent sells the theme.
  4. **Rotting jaw + one white eye:** exposed lower-beak polygon in bone tone,
     single milky eye — keeps it undead, not just a costume.
- **PALETTE:** field-drab flesh `#6B7350` (body), rot shadow `#3A3E2A`,
  helmet steel `#5A6066` (accent), wound black `#14120E`, bone `#CBC3A6`.
- **DISTINCTNESS:** Only human-artifact concept — hard-edged manufactured gear
  (helmet/tags) against organic rot is a contrast none of the other nine use.

---

## RANK 5 — design_10 · `skin_zombie_clown`
### "GREASEPAINT GRAVE JESTER"
*(zombie carnival / horror clown)*

- **HERO SILHOUETTE:** A parrot with a big torn ruffle collar and a stark
  white greasepaint face split by a too-wide dark grin — the collar breaks the
  neckline and the white face is a bright block that reads on any sky.
- **ZOMBIE ELEMENTS (draw calls):**
  1. **Ruffle collar:** a scalloped ring of 6–7 overlapping filled triangles /
     arcs (`draw.polygon` ×n) around the neck in faded red — silhouette-widening
     tell, sways with the flap.
  2. **Greasepaint face + rot:** filled off-white face patch, then a jagged
     grey `draw.polygon` where paint has flaked to show rot beneath — the
     "makeup peeling off a corpse" read.
  3. **Horror grin:** one thick dark curved `draw.line` (3px) far too long, with
     2 small dark tooth-gap rects — an unsettling stitched smile.
  4. **X-eye + sunken socket:** one eye a filled dark X (`draw.line` ×2), the
     other a hollow filled circle — the classic dead-clown asymmetry.
- **PALETTE:** greasepaint `#EDE6DE` (face), rot grey `#7C7266` (flaked flesh),
  faded blood-red `#A83A3A` (collar/grin accent), body `#4E4A52` (dusty
  costume), shadow `#232026`.
- **DISTINCTNESS:** The only carnival-horror concept; its bright white face +
  red collar make it the most saturated, "friendly-turned-wrong" read — nothing
  else in the set trades on that uncanny cuteness.

---

## Ranking rationale (zombie read @ 40px)

1. **Fungal (design_6)** — wins because it *breaks the parrot silhouette* with
   caps; body-horror is legible before color even registers.
2. **Burned (design_7)** — highest raw value contrast (black + ember), reads on
   any background, but is a surface tell rather than a shape change.
3. **Drowned (design_8)** — strong unique palette + the dangling lure, though
   the theme leans on color more than outline.
4. **Soldier (design_9)** — helmet reshapes the head well, but the wound/tags
   are smaller tells that lose a little at 40px.
5. **Clown (design_10)** — vivid and fresh, but "clown" competes with "zombie"
   for the read; ranked last only because the undead cue is a hair softer than
   the top four. Still a strong showpiece for variety.

**Best silhouette flex:** Fungal (caps) and Clown (collar) both alter the
outline — pick Fungal if you want the clearest infection horror, Clown if you
want the most distinct store-shelf thumbnail.
