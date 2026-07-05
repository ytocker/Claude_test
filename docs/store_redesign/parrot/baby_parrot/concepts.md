# BABY PARROT — 5 concepts

Pip "de-aged" into a baby macaw. The whole read is **"awww, it's a baby"** —
but it stays recognizably **PIP** (always the aviator shades) and it is an
equippable cosmetic recolour of the player bird, **not** a new creature.

## Hard constraints (apply to all 5)

- **Same sprite size.** Geometry is the fixed macaw build
  (`dollar_parrot_ghost._build_parrot_with_palette`). Hitbox + composite
  dimensions unchanged. "Baby" is sold by **palette + overlay styling inside
  the same silhouette**, never by shrinking the bird.
- **Buildable from code only** — `pygame.draw` polygons / lines / circles /
  `_aaellipse` over the macaw body, the same way every existing skin paints
  (head centre composite ~(47,41) = `HX,HY`; crown top ~31 = `CROWN_Y`; body
  centre ~(32,52)). No PNG sprites, no raster textures.
- **Aviators always stay.** They are Pip's tell. Each concept gives an
  aviator-tint note; lenses are kept (the base call's `draw_lenses=True`), and
  the big-eye cuteness is sold *around/under* the frames or as huge eyes
  *reflected in* the lenses — never by removing them.
- **Cuteness cues must survive 40px on BOTH day and night sky.** Every "baby"
  tell (big eyes, down-tuft, fluff) is a hard **≥2px shape** with its own
  value contrast, not a soft wash that mushes when small.

## Shared "baby" toolkit (how the cute reads are faked at fixed size)

- **Downy fluff** = short stray wisps drawn as 2–3px tapered triangles/lines
  poking *just past* the body+head silhouette (chest, crown, cheek, lower
  belly). Breaks the sleek macaw outline into a fuzzy one — the No.1 baby tell.
- **Big baby eyes** = an oversized round white catch-light dome + dark pupil
  drawn so it reads under/around the aviator lens, or two huge glossy
  "eyes-reflected-in-the-lens" highlights inside the dark lens body. Neoteny.
- **Down-tuft / cowlick** = a single sprout of fuzzy down off the crown
  (cockatoo-crest idiom but *soft*, not a feather), breaking the crown outline.
- **Stubby-wing illusion** = wing styled rounder/shorter with a bright rounded
  highlight blob at the wing's mid + a soft dark tuck at the tip, faking a
  pudgy half-grown wing without touching geometry.
- **Pastel re-plumage** = a lighter, lower-saturation `_pal` than any adult.

## Palette-collision guardrails (do NOT land near these)

Adult species: blue-gold (`#2D5AAA`+gold), amazon (green+red flash), sun
conure (orange-yellow), hyacinth (deep cobalt), cockatoo (near-white +
yellow crest), lorikeet (red/green/orange). Rarity skins: PRISM, AURORA,
THORNCREST, EMBERMOTH, MOONBLOOM (lilac/pearl), TEMPEST, CHROME. **Avoid
white-ish (cockatoo/cockatoo-crest), lilac/pearl (moonbloom), and deep cobalt
(hyacinth).** Each concept below states the axis that keeps it clear.

---

## 1 · HATCHLING — "just broke out of the egg"  *(rare)*

**Hero silhouette.** A cracked **eggshell cap** sits jauntily on the crown
(zig-zag broken rim + a shard slipping over one aviator lens), with a few wet
down-wisps escaping the cracks — the egg-break is a silhouette no other skin
owns.

**Layered object stack (composite-space):**
- **Crown:** half-eggshell cap (domed off-white ellipse, hard zig-zag broken
  lower rim) tilted ~15°, breaking the crown outline; one tiny shell shard
  perched on top.
- **Face:** a loose shell shard hanging over the upper-left aviator lens (so
  the egg literally hatched onto Pip); a single 2px wet down-curl off the cheek.
- **Chest:** two short damp down-wisps poking past the belly silhouette (newly
  hatched = stuck-down fluff, not fluffy yet).
- **Back/tail:** a couple of speckled shell-fleck dots and one stray shard
  by the tail root (debris from the break).
- **Wing:** rounded bright mid-highlight blob for the stubby-wing illusion;
  damp-fluff tuck at the tip.

**Palette (3–5).** Body warm cream-yellow `#F4E3A8` / shadow `#D8B86A` /
soft peach belly `#F6C9A0` / shell off-white `#F2EDE0` / shell-crack shadow
`#C8B98A`. **Aviator tint:** warm amber `#E8B86A` glint.

**Distinctness line.** The only **egg/hatch** concept — props (broken shell +
shards + shell flecks) carry it, not pure fluff. Warm cream-yellow stays clear
of cockatoo white, hyacinth blue, and the lilac MOONBLOOM; the egg cap reads
totally different from cockatoo's yellow feather-crest.

---

## 2 · DOWNBALL — "maximum fuzz"  *(common)*

**Hero silhouette.** Pip as a round **ball of down** — the entire body+head
outline is feathered into a soft halo of short fluff wisps all the way around,
turning the sleek egg-shape into an unmistakable fuzzy puff. The fuzz IS the
silhouette-breaker.

**Layered object stack (composite-space):**
- **Crown:** a triple **down-tuft cowlick** (three short soft sprouts) off the
  top of the head — the hero crown break.
- **Face:** big-baby-eye treatment — oversized white catch-light domes sitting
  under each aviator so the round eyes read huge below the frames; rosy 2px
  cheek-blush dot under the near lens.
- **Chest / belly:** a dense ring of 2–3px fluff wisps around the whole lower
  silhouette (the puffball edge).
- **Back / tail:** the tail wedges softened with fluff tufts at each tip so
  even the tail reads downy, not sleek-feathered.
- **Wing:** rounded stubby highlight + a fluff fringe along the trailing edge.

**Palette (3–5).** Soft buttermilk `#FBF1C9` body / warm tan shadow `#E0C079`
/ honey belly `#F7DB9B` / fluff-tip highlight `#FFFBE8` / cheek-blush
`#F2A6A0`. **Aviator tint:** soft gold `#F2D27A`.

**Distinctness line.** The **pure-fuzz** take — all-over down halo + cowlick,
no props at all. Buttermilk/honey is warmer and lower-contrast than sun
conure's saturated orange-yellow and reads softer than cockatoo white; it's
the "fluff axis" sibling to Hatchling's "prop axis."

---

## 3 · BIG-EYES — "neoteny dialed to 11"  *(rare)*

**Hero silhouette.** The signature aviators become **enormous baby eyes** —
the lenses are tinted glassy and filled with two huge glossy cartoon eyes
(big white catch-lights + tiny pupils), so the whole face reads as gigantic
shiny eyes behind the shades. The face, not the fluff, is the tell.

**Layered object stack (composite-space):**
- **Face (hero):** inside each aviator lens, a huge glossy eye — oversized
  white highlight dome (≥3px), small dark pupil low in the lens, a 1px
  starry glint; the frames stay but the lens body lifts to a glassy
  baby-blue so the eyes pop. Soft rosy cheek-blush under the near lens.
- **Crown:** a single soft **down-curl** cowlick (one sprout) so the crown
  still breaks, but understated — the eyes own the read.
- **Chest:** light, sparse fluff wisps (a few only) so it still feels baby
  without competing with the face.
- **Mouth:** tiny 2px open-beak "peep" highlight so it reads as a chirping
  baby, not a stern adult beak.
- **Wing:** rounded stubby highlight; otherwise clean to keep attention up top.

**Palette (3–5).** Body soft mint-cream `#DDEFD6` / sage shadow `#9FC79A` /
pale belly `#EFF8EA` / lens glassy sky `#BFE3F2` / pupil ink `#2A3540` /
cheek-blush `#F0A8A0`. **Aviator tint:** glassy aqua `#9FD4E8` (lets the eyes
read through).

**Distinctness line.** The **eyes-in-the-lens** take — uses the aviators
themselves as the cuteness engine, which none of the other 4 do. Mint-cream is
a fresh hue not used by any adult (amazon green is far darker/saturated) and
nowhere near moonbloom lilac or hyacinth cobalt.

---

## 4 · NEST-BABY — "still in the nest"  *(rare)*

**Hero silhouette.** Pip nestled in a little **twig nest** ruff that rings the
lower body, with a wide-open **chirping beak** and two stubby down-wings — the
woven nest collar is a silhouette-breaker nothing else has.

**Layered object stack (composite-space):**
- **Body/lower:** a woven **twig-nest collar** — short crossing brown
  twig-strokes + dry-grass wisps ringing the belly silhouette (the nest Pip
  sits in), breaking the lower outline.
- **Crown:** one soft down-tuft cowlick + a tiny stray twig caught in it
  (fell from the nest rim).
- **Face:** big-baby eyes as white catch-light domes under the aviators; a
  wide-open **peeping beak** (small bright inner-mouth wedge) — "feed me!".
- **Chest:** a couple of pale natal-down wisps over the warm body.
- **Wing:** rounded stubby highlight + a soft down fringe; the wings read like
  not-yet-grown flight feathers.

**Palette (3–5).** Body warm fawn `#E9C98C` / deep-tan shadow `#B98A4E` /
cream belly `#F6E6BE` / nest-twig brown `#8A5A32` / dry-grass straw `#CBA760`
/ peep-mouth coral `#E87A66`. **Aviator tint:** warm tan `#D8A860`.

**Distinctness line.** The **nature/nest** take — twig + grass props + open
peep-beak tell a *whole baby-bird scene*, distinct from Hatchling's egg and
Downball's bare fuzz. The earthy fawn/twig browns are a palette lane no adult
or rarity skin occupies (none of them are brown-based).

---

## 5 · BINKY — "pacifier-and-bib cartoon baby"  *(common)*

**Hero silhouette.** A cheeky human-baby read: a big round **pacifier** plugged
at the beak + a scalloped **bib** across the chest + a curl of hair, so Pip
reads as a literal swaddled baby. The pacifier ring is the front tell.

**Layered object stack (composite-space):**
- **Face (hero):** an oversized **pacifier** — pastel ring + button held at
  the beak base (front-and-centre, breaks the lower-face silhouette); big-baby
  white catch-light domes under the aviators.
- **Crown:** a single bold **curl cowlick** sprout off the crown (the classic
  cartoon-baby hair-curl), breaking the crown outline.
- **Chest:** a scalloped **bib** across the upper chest (pastel with a 2px
  trim line + one tiny heart/star motif) — the body object.
- **Belly:** a small milk-spot highlight + a couple of soft fluff wisps so the
  costume still reads downy, not just propped.
- **Wing:** rounded stubby highlight; a tiny rattle could ride the wingtip but
  keep it optional so the puffy wing read stays clean.

**Palette (3–5).** Body soft powder-blue `#BFE0EA` body / teal shadow
`#7FB4C2` / pale belly `#E4F3F7` / pacifier + bib pastel pink `#F6B8C8` /
bib trim cream `#FBF4DA` / curl-tan `#C9A86A`. **Aviator tint:** cool
sky-aqua `#A8D6E6`.

**Distinctness line.** The **human-baby props** take (binky + bib + hair-curl)
— the only concept reading as a swaddled infant rather than a baby *bird*.
Powder-blue + pink is a cool pastel pairing that deliberately steers clear of
hyacinth's deep cobalt and moonbloom's lilac (it's a light cyan-pink, not a
violet-pearl), and the pink props keep it from reading cockatoo-white.

---

# Ranking (best baby read first)

1. **DOWNBALL** — the cleanest, most universal "awww baby" at 40px: an
   all-over fuzz halo + crown cowlick + big eyes hits every neoteny lever at
   once, needs no prop the eye must parse, and is the cheapest/most buildable.
   Strongest pure baby read; ideal common anchor.
2. **HATCHLING** — the most *charming and shareable* hook (the egg-cap with a
   shard over the lens is instantly legible and funny), and the broken-shell
   silhouette is genuinely novel against the roster. Best "wow, cute" pick.
3. **BIG-EYES** — the boldest *concept* (turning the aviators into giant baby
   eyes is the smartest reuse of Pip's own tell), but the read lives entirely
   in the lens interior, so it's the highest-risk at 40px and on bright day
   sky — worth building, watch the lens contrast closely.
4. **NEST-BABY** — adorable scene with the open peep-beak, but the woven-twig
   collar is the most detail-dependent element and the one most likely to mush
   small; reads best if the twigs stay chunky (≥2px, few strokes).
5. **BINKY** — the funniest *idea* but the most prop-stacked (pacifier + bib +
   curl) and the human-baby read is the least "Pip"; keep as a cheeky common,
   but it's the busiest to keep clean at downscale.

**Best baby read overall:** **DOWNBALL** (No.1) — maximum cuteness with the
fewest moving parts and the safest downscale. **Best showpiece / hero card:**
**HATCHLING** (No.2) for store-card charm and a one-of-a-kind silhouette.

Numbers map to `design_1..5` under `tools/baby_parrot_candidates/`
(`design_1` = HATCHLING … `design_5` = BINKY).
