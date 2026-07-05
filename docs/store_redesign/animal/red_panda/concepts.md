# RED PANDA — 5 From-Scratch Redesign Concepts

Store animal rebuild. Current art (flat russet ball + mathematically perfect
arc tail + hard seam circle) is discarded. Each concept below is a complete
character re-interpretation: different mood, proportions, silhouette logic, and
premium craft. Procedural Pygame only on a 64×84 SRCALPHA canvas; the 40px
in-motion read is the truth. Anchors: BCX/BCY 32/44, HCX/HCY 44/34,
`_WING_ANGLES=(50,20,-10,-40)`.

The non-negotiable red-panda tells every concept must carry at 40px: **russet
coat**, **white cheek-mask with rust tear-tracks**, **cream/rust RINGED tail**,
**dark legs**. How each concept stylizes those four is what separates them.

---

## 1. EMBER SCOUT

1. **Name:** EMBER SCOUT
2. **Pitch:** A bright-eyed little forager mid-leap, alert and plucky — the
   "default hero" read: maximally friendly, maximally legible.
3. **Silhouette hero:** A rounded acorn-shaped body with a big plush tail
   sweeping up behind like a question-mark; ears as two clear triangular nubs.
   At 40px the read is "round critter + huge curled tail."
4. **Anatomical choices:** Head ~60% of body width (cute but not chibi),
   pushed forward-and-up at HCX/HCY for an alert tilt. Body a soft teardrop,
   widest low. Tail thick and tapering, curled up and over — **rings drawn as
   stacked soft-edged crescent bands that follow the tail's curve** (not a
   perfect circular arc), each ring slightly fatter toward the base so it reads
   organic. Tail joins the body with an **overlapping fur-tuft, no seam circle**.
   Dark stocky front paws tucked under the chin, just visible.
5. **Premium craft:** 4-layer body shading (base → mid → russet rim-light on the
   sun side → deep AO core under the tail-overlap). Soft gloss sheen blit on the
   forehead and tail-crown. AO shadow under the chin. Fur-stroke edge lines on
   the tail silhouette so the outline looks furred, not vector-clean.
6. **Palette:** body `#C65A2E`, shadow `#7E331A`, highlight `#F2944E`,
   cream `#F6E6CC`, accent (nose/legs) `#3A2418`.
7. **Distinctness:** The safe, sunny "face of the roster" — warm daylight
   palette and classic proportions; every other concept deviates harder in mood
   or build.

---

## 2. DUSK BANDIT

1. **Name:** DUSK BANDIT
2. **Pitch:** A sly, low-slung night-prowler with a mischievous grin — the
   raccoon-cousin energy of the real animal pushed to "cute cat burglar."
3. **Silhouette hero:** Long and low, horizontal — a stretched-loaf body with
   the tail held out STRAIGHT BEHIND like a banded rudder, not curled. The
   silhouette reads as an elongated mammal with a thick striped flag-tail; the
   most distinct outline of the five.
4. **Anatomical choices:** Smaller head relative to body (~50%), set low and
   forward, giving a sneaky lean. Body elongated, belly-heavy and dark. Tail
   horizontal and BOLD — **6 hard alternating rings rendered as clean banded
   blocks with crisp value steps** (the one concept that leans into graphic,
   high-contrast banding rather than soft). Dark legs prominent and gripping —
   front paws planted, reading as a creep-pose.
5. **Premium craft:** Beak/snout-style banding logic applied to the tail (crisp
   value-stepped bands with a thin dark separator line between each — looks
   screen-printed-premium). Strong AO under the belly to seat the low body.
   Eye-surround patches darkened into a true "bandit mask." Cool rim-light along
   the back edge from a moonlit key.
6. **Palette:** body `#A8492B`, shadow `#5A2614`, highlight `#D98C5A`,
   cream `#EAD8BC`, accent (mask/legs) `#241A22` (cool near-black).
7. **Distinctness:** The only horizontal/straight-tail silhouette and the only
   graphic hard-banded tail; cool dusk palette vs. everyone else's warm.

---

## 3. AUTUMN MONK

1. **Name:** AUTUMN MONK
2. **Pitch:** Serene, plush, half-asleep — a contemplative dumpling who flaps
   like it's reluctantly waking up. Maximum cozy, zen calm.
3. **Silhouette hero:** A near-perfect plush SPHERE of a body with a giant
   tail wrapped fully AROUND the front (the real cold-weather curl), framing the
   face like a scarf. At 40px: "round fluffball hugging its own tail."
4. **Anatomical choices:** Head and body nearly merged into one soft mass; ears
   small and low. The tail is the second hero — **wrapped 270° around the front,
   its rings reading as concentric cozy bands of a wrapped scarf**, tip resting
   near the chin. No legs visible (tucked under the fluff) — pure roundness.
   Half-lidded sleepy eyes.
5. **Premium craft:** The richest 4-layer shading of the set — soft radial body
   gradient + broad gloss sheen across the upper sphere for a plush, almost
   velvet read. Heavy AO in the crease where the wrapped tail overlaps the body
   (sells depth, kills any seam). Fine fur-stroke fringe along the tail's leading
   edge. Warm bounce-light in the chin pocket.
6. **Palette:** body `#B95733`, shadow `#6E3019`, highlight `#E89A5E`,
   cream `#F4E3C6`, accent `#33231A`.
7. **Distinctness:** The only "tail-wrapped-forward / sphere" build and the only
   sleepy mood; reads as a ball where others read as a posed critter.

---

## 4. MAPLE SPRITE

1. **Name:** MAPLE SPRITE
2. **Pitch:** Hyper-cute chibi gremlin — enormous head, tiny body, springy and
   excitable. The pure kawaii-mascot play, the most "toy-like" of the five.
3. **Silhouette hero:** A giant round head sitting on a tiny body, with two
   oversized pointed ears spiking up and a small perky tail flicking behind.
   At 40px the read is dominated by HEAD + EARS — an instantly cute lollipop.
4. **Anatomical choices:** Head ~85% of total mass (true chibi), huge forward
   eyes with big cream eye-surround patches and bold rust tear-tracks. Body
   minimal, almost a footnote under the head. Ears oversized with cream inners.
   Tail short and stubby but still ringed — **rings as a few chunky soft hoops**,
   flicked to one side for personality. Tiny dark paw-dots visible.
5. **Premium craft:** Big glossy catch-light gloss-sheen on the eyes (the
   premium kawaii tell) plus a forehead sheen on the head-dome. Crisp white
   eye-surround patches layered over the mask with a soft AO ring so the eyes
   sit IN the face, not on it. Clean fur-stroke ear edges. Sub-surface-style
   warm highlight on the ear inners.
6. **Palette:** body `#CF6234`, shadow `#84371C`, highlight `#FBA85C`,
   cream `#FBEFD8`, accent `#2E1F17`.
7. **Distinctness:** The only chibi (head-dominant) build; charm comes from eyes
   + ears, not the tail, inverting the usual red-panda emphasis.

---

## 5. CINDER GUARDIAN — *legendary-tier showpiece*

1. **Name:** CINDER GUARDIAN
2. **Pitch:** A mythic ember-spirit red panda whose ringed tail glows like a
   slow-burning coal — regal, warm, and a little magical. The flex skin.
3. **Silhouette hero:** A proud upright stance, chest out, with a tall plumed
   tail rising HIGH behind like a torch, tip flaring. The crown-of-the-head ear
   tufts and the lifted glowing tail make a strong vertical, banner-like
   silhouette.
4. **Anatomical choices:** Balanced head (~60%), held high and noble. Body
   upright and slightly slimmer than EMBER SCOUT for a stately read. Tail tall
   and flame-shaped — **rings rendered as glowing bands that intensify toward an
   ember-bright tip**, alternating deep-rust and lit-cream so the rings double as
   the glow gradient. Dark legs firmly planted. Small ear-tip tufts catch light.
5. **Premium craft:** Legendary techniques baked into the art — an
   animated-feel glow halo (additive SRCALPHA blit) around the tail tip, an
   energy-shimmer gradient up the tail rings, hot rim-light along the whole body
   silhouette, and a warm gloss sheen on the chest. Embers can be implied with
   2–3 soft glow dots trailing the tail. AO under the chin keeps the face
   grounded against all the glow. The only concept with self-illumination, so it
   pops against both bright-day and night skies.
6. **Palette:** body `#B14A24`, shadow `#5C2410`, highlight/glow `#FFB347`,
   cream `#FFE9C2`, accent (ember core) `#FF6A1A` + dark legs `#2A1810`.
7. **Distinctness:** The only legendary — self-lit glowing tail + ember shimmer
   + halo. Spectacle justifies the tier; the other four are clean late-game
   goals, this one is a showpiece flex.

---

## Ranking & picks

1. **EMBER SCOUT** — strongest all-rounder and safest 40px read; the one to
   ship if only one lands.
2. **CINDER GUARDIAN** — best legendary showpiece; the glowing ringed tail is a
   genuine flex and the only self-lit option.
3. **DUSK BANDIT** — most distinct silhouette (horizontal, hard-banded tail) and
   only cool palette; great variety pick.
4. **AUTUMN MONK** — premium plush craft and a unique tail-wrapped sphere build;
   highest "expensive" feel up close.
5. **MAPLE SPRITE** — pure chibi charm; lovable but the least red-panda-anatomy
   read, so ranked last on signature-clarity.

**Set balance:** 4 late-game (Scout warm/classic, Bandit cool/graphic, Monk
plush/cozy, Sprite chibi/toy) + 1 legendary (Guardian, glowing). Mood, build,
and tail-treatment all differ — no two are palette swaps.

---

### References that sparked these
- Real red-panda anatomy — tear-track mask, black belly/legs, red-and-buff
  ringed tail with dark tip, cold-weather tail-wrap, raccoon-cousin face.
- Chibi / kawaii mascot conventions — head-dominant proportions and big glossy
  eyes (drove MAPLE SPRITE; informed EMBER SCOUT's friendliness dial).
