# MANTIS SHRIMP — full from-scratch redesign (`skin_mantis_shrimp`, animal, 980 coins)

**What we're replacing.** The current "DUOTONE BRUISER": teal torpedo carapace,
two bold orange vertical stripes + a thin gold/cyan mid-stripe, twin iridescent
jewel eyes on tall periscope stalks, 3-segment teal abdomen → orange tail-fan,
and the hero gag — oversized orange "boxing-glove" raptorial clubs that cock back
then PUNCH forward with the flap. Competent but flat (only two colors, very
"swimsuit-stripe" carapace). The user wants a genuinely fresh direction.

**Identity anchors** every concept must still hit at the 40px in-motion truth
read: (a) the raptorial **CLUBS** = hero feature, must read + carry the punch
gag; (b) the **stalked compound EYES** (paired periscope read); (c) the
**segmented armored body + tail-fan**. Bird faces RIGHT. Canvas 64×84, body
centre ≈(32,44), head ≈(44,34), crown top ≈y=24. 2px-minimum detail, day AND
night legible. Procedural pygame only (ellipses, polygons, circles, lines, glow
caches). Numbers map to design_1…design_5.

Reference grounding: peacock mantis shrimp (*Odontodactylus scyllarus*) — green
carapace, leopard-spot anterior, orange-red somite margins, metallic-blue tail
fan with red setae, stalked independently-mobile eyes, clubs folded under body
that strike at .22-bullet acceleration; ~450 species span technicolor reef to
deep-sea. (NatGeo / Monterey Bay / Wikipedia / National Marine Sanctuary.)

---

## 1. PEACOCK PRISM — the technicolor reef jewel  `skin_mantis_shrimp` (keeps id)
The signature species, turned all the way up. This is THE mantis shrimp everyone
pictures, and it answers the current design's biggest weakness (only two colors)
with a full reef-rainbow that still holds a clean value structure.
- **Hero silhouette:** a stout emerald carapace whose **front rim glows
  orange-red** while a **metallic-blue tail-fan flares behind** — a rainbow
  torpedo with two cocked clubs up front. The warm-front / cool-back colour split
  is the read even when shrunk.
- **Parts:** **stalked eyes** as two short candy-striped stalks at crown
  (~y=24–32) topped with **half-green / half-magenta split spheres** + white
  highlight dot (the famous bicoloured eye). **Carapace** a rounded emerald dome
  over head/shoulders (28–46,30–48) carrying **3–4 leopard spots** (dark blob +
  white ring, ≥3px so they survive). **Body somites**: 3 segment bands, each with
  an **orange-red trailing edge** stripe. **Tail-fan** behind (left, ~18–24,46) a
  blue iridescent fan with 3 red setae ribs. **Clubs**: paired stubby
  green-to-orange raptorials folded forward under the head.
- **Palette:** `#1FA86A` emerald body / `#0C5C3E` rim+spots (dark anchor) /
  `#FF6A2B` orange-red somite edges / `#2BC7E8` tail-fan blue / `#E8338C` eye-magenta
  / `#FFF4D6` highlight. Strong dark green rim keeps it legible on bright day sky.
- **Flap/strike gag:** clubs **cock back as the wings raise**, snap forward on the
  down-flap with a tiny cyan **impact spark**; tail-fan + leopard carapace stay
  steady so the punch reads cleanly.
- **Distinct:** the only FULL-spectrum design — multi-hue reef jewel vs. the old
  two-colour stripe job; biology-accurate leopard spots + split eyes nobody else has.

## 2. ABYSS GLOWER — deep-sea bioluminescent stalker  `skin_mantis_shrimp`
The dark, premium-feeling opposite of #1. Near-black armoured body that reads by
its **glow alone** — perfect night-sky pop, and a great "expensive 980-coin"
feel.
- **Hero silhouette:** a **black torpedo defined entirely by cyan glow lines** —
  two glowing eye-orbs up top, glowing seams between every segment, and **two
  clubs whose tips burn hot like charged hammers**. Reads as a dark shape wearing
  light.
- **Parts:** **Eyes** two short dark stalks topped with **glowing cyan orbs**
  (radial glow cache, white-hot core) at crown. **Carapace/body** deep blue-black
  with **thin electric-cyan seam lines** tracing each of 3–4 segment joints (the
  bioluminescent photophore rows). A faint row of **glow dots** down the side.
  **Tail-fan** behind: dark fan with cyan rib-glow. **Clubs** forward, dark with
  **molten orange-white glowing knuckle tips** — the only warm accent, so the
  punch is the brightest event on screen.
- **Palette:** `#0A1424` black-body / `#13314E` segment shade / `#23E0FF` cyan
  glow / `#9BF6FF` glow core / `#FF8A1E` hot club-tip (warm contrast) / `#FFE7B0`
  tip-core. Built around glow caches so it blooms on night sky and still reads as a
  dark silhouette on day sky.
- **Flap/strike gag:** on the down-flap the **club tips flare from orange to
  white-hot** and throw a short ember trail; the body seam-glow pulses brighter in
  sync (charge → discharge), so the whole creature "powers up" each punch.
- **Distinct:** the dark/glow design — value read carried by light not pigment;
  opposite end of the spectrum from the bright #1, and the only one engineered for
  night-sky bloom.

## 3. KO GLADIATOR — heavy armored mecha brawler  `skin_mantis_shrimp`
Leans all the way into "the punch is its identity." A riveted gladiator/mecha
shrimp where the clubs are comically oversized **wrecking-ball gauntlets**. Most
toy-like and aggressive — pure casual-game charm.
- **Hero silhouette:** a chunky **plated battle-tank body dwarfed by two huge
  banded boxing gauntlets** out front. The gauntlets ARE the silhouette; the body
  is the handle.
- **Parts:** **Eyes** two stubby armoured periscope stalks with **amber visor
  orbs** (single bright lens look) at crown. **Carapace** segmented steel plates
  (cool grey-blue) with **2px rivet dots** along each plate edge and a **gold
  collar plate** at the neck. **Body** 3 stacked armour bands. **Tail-fan** a
  bladed metal fan behind. **Clubs**: oversized **red-and-cream banded gauntlets**
  (think boxing-glove + knuckle plate), each ~1/3 of the canvas, cocked forward.
- **Palette:** `#5A6B7E` steel body / `#2E3947` plate shadow (dark anchor) /
  `#C9D4DE` plate highlight / `#E03B3B` gauntlet red / `#F4E3C2` gauntlet cream /
  `#FFC836` gold collar. High-contrast metal value range reads on both skies.
- **Flap/strike gag:** the big gauntlets **wind back + rotate on the up-wing**,
  then **slam forward with a white star-burst impact + 3 speed-line streaks** on
  the down-flap. Biggest, most theatrical punch of the five.
- **Distinct:** the metal/mecha design — riveted steel + giant gauntlets vs. the
  organic others; the only one where the body shrinks and the CLUBS become the
  whole hero shape.

## 4. CHIBI POW — adorable big-head pocket shrimp  `skin_mantis_shrimp`
The cute play. Big round head, oversized sparkly eyes, tiny stubby body, and
**little mitten clubs** that do an eager pat-pat punch. Highest friendly/funny
appeal — the "aww" tier.
- **Hero silhouette:** a **giant round head topped by two oversized goggle-eyes**,
  a tiny tapering body trailing behind, and **two small round mitten-clubs** held
  up ready. Head-heavy = instantly cute, instantly readable.
- **Parts:** **Eyes** two big bubble orbs on short stubby stalks at crown
  (~y=24), each a teal sphere + **large white sparkle + small catch-light** (anime
  shine). **Head/carapace** an oversized rounded coral-pink dome (head≈44,34) with
  one tiny leopard spot + a **blush mark**. **Body** a small 2-segment tail tucked
  behind with a tiny heart-shaped tail-fan. **Clubs**: two **small round
  cream-and-coral mittens** held forward, comically undersized.
- **Palette:** `#FF9EB5` coral-pink head/body / `#E06A8A` rim (dark-enough
  anchor) / `#FFD9C2` mitten cream / `#3FD0D8` eye-teal / `#FFFFFF` sparkle /
  `#7A2F46` spot+blush-line. Pastel but with a saturated rim so it doesn't wash
  out on bright sky.
- **Flap/strike gag:** the little mittens do a quick eager **double pat-pat**
  forward on the down-flap with a tiny pink star + a bounce of the big head; eyes
  do a 1-frame happy squash. Punch reads as adorable, not deadly.
- **Distinct:** the chibi design — head-to-body ratio inverted, sparkle eyes, mini
  clubs; the only one optimised for "cute" over "fierce," opposite the gladiator.

## 5. EMBER FORGE — molten lava brawler  `skin_mantis_shrimp`
A warm legendary-flavoured showpiece: a charcoal carapace cracked with **glowing
lava veins**, clubs forged like **hot iron hammers**. Distinct from #2's cool
glow by being all-warm fire, and from #3's clean metal by being molten/rough.
- **Hero silhouette:** a **dark cracked-rock torpedo seamed with orange lava
  light**, two ember-eyes, and two clubs that look like **white-hot anvil heads**.
  Reads as a smouldering coal that punches.
- **Parts:** **Eyes** two short basalt stalks topped with **smouldering orange
  ember orbs** (dark ring, glowing core) at crown. **Carapace/body** charcoal
  plates with **branching lava-crack veins** (2–3px orange-to-yellow gradient
  lines) along each segment seam. A faint **heat-shimmer** band over the back.
  **Tail-fan** behind: dark fan with glowing orange rib edges, faint ember spark
  particles. **Clubs**: forged **iron hammer-heads**, dark base fading to a
  **white-hot striking face**.
- **Palette:** `#2A2320` charcoal body / `#120D0B` deep crack-shadow (anchor) /
  `#FF5A1E` lava orange / `#FFC233` lava yellow / `#FFF0C0` white-hot core /
  `#7A2A12` rust-rim. Warm glow cache makes the veins pulse on night sky; dark
  charcoal holds the silhouette on day sky.
- **Flap/strike gag:** on the down-flap the **club faces flash white-hot** and
  scatter a few rising ember sparks while the **lava cracks pulse brighter**
  (forge "strike" + sparks); a faint heat-shimmer ripples on the back each beat.
- **Distinct:** the fire design — molten rock + lava veins, all-warm palette;
  contrasts #2's cold-cyan glow and #3's clean steel, and gives the lineup its
  showpiece-grade animated-glow option.

---

### Ranking rationale
1. **PEACOCK PRISM** — the iconic, instantly-recognizable species; biggest upgrade
   over the dull two-tone original; full spectrum with disciplined value structure.
2. **ABYSS GLOWER** — premium dark/glow feel, best night-sky pop, strong
   charge→punch gag; the cool counterweight to #1.
3. **KO GLADIATOR** — leans hardest into the punch identity; most theatrical gag and
   strongest toy/arcade charm.
4. **CHIBI POW** — broadest "aww" appeal and a great tonal outlier, but softens the
   fierce mantis read more than the others.
5. **EMBER FORGE** — gorgeous warm showpiece, but tonally overlaps the glow concept
   of #2 and the brawler concept of #3, so it ranks behind them as the variant.

**Best legendary-grade showpiece:** ABYSS GLOWER or EMBER FORGE (animated glow).
**Safest crowd-pleaser:** PEACOCK PRISM.

Sources: [NatGeo](https://www.nationalgeographic.com/animals/invertebrates/facts/mantis-shrimp),
[Monterey Bay Aquarium](https://www.montereybayaquarium.org/stories/meet-the-mantis-shrimp),
[Wikipedia — O. scyllarus](https://en.wikipedia.org/wiki/Odontodactylus_scyllarus),
[National Marine Sanctuary Foundation](https://marinesanctuary.org/blog/sea-wonder-peacock-mantis-shrimp/).
