# PILOT PARROT — Costume Concepts (`skin_pilot`)

Five distinct pilot/aviator archetypes for the scarlet-macaw base. The bird
faces **right**; head sits upper-right, belly lower-left, and each wing is a
separate polygon rotated through the 4 flap poses. Every concept must read as a
PILOT at ~40px from **3+ overlapping tells** — a hat alone is disqualified.

Numbers map to `design_1` … `design_5`.

Geometry cheat-sheet (base `parrot.py`, 64×60 canvas):
- Head/eye cluster ≈ (x 40–52, y 18–26). Beak points right off the head.
- Nape/back-of-neck ≈ (x 34–42, y 20–30) — good real estate for goggle straps,
  caps, scarves.
- Chest/belly ≈ (x 24–40, y 30–46) — big flat block for jacket fronts, badges.
- Wing shoulder anchor ≈ (x 24, y 24); wing sweeps up-right when flapping.
- Feet/legs tuck ≈ (x 26–34, y 44–52).

---

## 1. THE CAPTAIN — golden-age airline commander

- **Hero silhouette** — A crisp **peaked officer's cap** breaks the round head
  into a flat-topped wedge with a hard horizontal brim shadow; below, the body
  is a squared-off **double-breasted navy block** instead of soft red feathers.
  Reads as "uniform" before you see any detail.
- **Pilot tells**
  1. **Peaked cap** — filled polygon crown (navy `#1B2A4A`) sitting as a
     flat-topped dome over the head top (y ≈ 12–20), with a separate thin
     **black patent brim** rect angled forward off the beak-side (y ≈ 20).
     Purpose: instant "officer".
  2. **Gold wings cap-badge** — a small bright `#F5C542` horizontal wings glyph
     (two swept triangles + a center circle) centered on the cap band. The one
     spot of high-value gold on a dark cap = the airline tell.
  3. **Four gold sleeve stripes** — 4 stacked short horizontal lines
     (`#F5C542`, 1–2px, spaced) banded across the **lower wing / cuff** so they
     ride every flap pose. Purpose: captain's rank, and they animate with the
     wing.
  4. **White shirt-front wedge + dark tie** — a white `#F4F1EA` triangle down
     the chest center with a thin navy `#14213D` tie stripe splitting it.
     Purpose: fills the belly block as a shirt, sells the suit.
- **Palette** — `#14213D` navy-dark, `#1B2A4A` navy, `#F4F1EA` shirt-white,
  `#F5C542` badge-gold, `#0B0F1C` patent-black.
- **Distinctness** — Only concept with a hard-brimmed **peaked service cap** and
  gold **sleeve stripes** banding the wing: pure commercial-airline command.

---

## 2. ACE — WW1/WW2 open-cockpit dogfighter

- **Hero silhouette** — A **brown leather flight helmet** hugs the whole head
  as a rounded skullcap with a chin-strap lump, and a **silk scarf streams off
  the nape into the wind** — a long ragged trailing pennant that no groundling
  costume has. Head-blob + trailing tail = heroism in motion.
- **Pilot tells**
  1. **Leather flight helmet** — a filled `#6B4A2B` rounded-cap polygon over the
     head (covering ear area to brow), with a thin `#3E2A17` seam line arcing
     over the crown and a small strap nub at the jaw. Purpose: the aviator head.
  2. **Goggles pushed up on the forehead** — two `#2E2A26` circles joined by a
     bridge, ringed in brass `#B98A3C`, sitting **above** the eyes on the helmet
     brow (not over the eyes). Purpose: "just landed / heroic" read; distinct
     from goggles-on-eyes in concept 5.
  3. **Trailing silk scarf** — a long tapering polygon ribbon (`#E8E2D4` cream
     or optional `#C0392B` red) knotted at the throat and streaming
     back-and-down off the nape (x ≈ 34→18, y ≈ 26→40), with a lighter highlight
     edge. Purpose: the signature motion tell — the only trailing element.
  4. **Fur-collar bomber jacket** — a bumpy `#8A5A32` collar arc across the upper
     chest with a `#C9A876` fleece-fur lump at the neckline, over a
     darker-brown jacket body. Purpose: cold open-cockpit gear.
- **Palette** — `#6B4A2B` leather, `#3E2A17` leather-dark, `#C9A876` fur,
  `#E8E2D4` scarf-cream, `#B98A3C` brass, `#C0392B` optional-red-scarf.
- **Distinctness** — Only concept with a **wind-trailing scarf pennant** and
  goggles worn **up on the brow**: romantic open-cockpit hero.

---

## 3. RED BARON — biplane ace

- **Hero silhouette** — Head-to-tail **crimson leather** flips the whole
  value/hue away from the base bird, topped by a tall **fur-trimmed leather
  flying helmet**, and a single **glint monocle** disc on one eye. The all-red
  body + gold monocle spark is unmistakable and aristocratic.
- **Pilot tells**
  1. **Crimson leather coat** — recolor the body block to deep `#8E1B1B`
     lacquered red with a `#5E0F0F` shadow underside and a vertical row of 3–4
     tiny `#E0B84C` brass buttons down the chest center. Purpose: the Baron's
     signature red kit.
  2. **Tall fur-trimmed helmet** — a `#4A2E1A` dark-leather cap over the head
     with a thick pale `#D8C7A8` fur band around its lower edge (a lumpy arc).
     Purpose: Teutonic winter-ace headgear, taller than concept 2's snug cap.
  3. **Brass monocle + glint** — a single `#E8C766` ring circle over the
     forward eye with a bright white 1px glint and a thin dangling chain line
     down to the collar. Purpose: the aristocrat tell — no other concept has a
     monocle.
  4. **Iron-cross insignia** — a small high-contrast **black cross-pattée**
     (`#111` with white outline) on the shoulder/upper-wing. Purpose: the ace's
     squadron mark, rides the flap.
- **Palette** — `#8E1B1B` baron-red, `#5E0F0F` red-dark, `#4A2E1A` leather,
  `#D8C7A8` fur-cream, `#E8C766` brass-gold, `#111111` cross-black.
- **Distinctness** — Only **all-red-leather** body with a **monocle + black
  cross** — the villainous-aristocrat biplane ace.

---

## 4. VIPER — modern jet fighter pilot

- **Hero silhouette** — The head becomes a smooth **helmet + dropped oxygen
  mask + mirror visor** — a hard-edged gray dome with a green mirrored band and
  a chunky mask block over the beak — while the body is an angular
  **olive/gray G-suit** with a bright emergency-orange collar. Sci-fi hard
  edges vs. everyone else's soft leather.
- **Pilot tells**
  1. **Flight helmet + mirrored visor** — a rounded `#7A8087` gray helmet
     covering the whole head, with a horizontal **mirror-visor band** across the
     eyes: a `#1CE0A0`→`#0A6E58` green gradient strip with a bright specular
     streak. Purpose: the modern-pilot face, high-contrast glowy tell.
  2. **Oxygen mask** — a blocky `#2B2F33` dark polygon clamped over the
     beak/lower face with a `#4A4F55` corrugated **hose** curving down to the
     chest. Purpose: silhouette-breaking lump = "jet pilot", not vintage.
  3. **G-suit / survival vest** — olive `#5B6B3A` torso block with an
     **emergency-orange `#F26522` collar arc** and two small gray buckle rects.
     Purpose: readable modern flight-suit color story.
  4. **Rank/flag shoulder patch** — a small bright rectangle patch
     (`#F26522` or subdued flag colors) on the upper wing/shoulder, plus a thin
     Velcro line. Purpose: squadron patch, animates on flap.
- **Palette** — `#7A8087` helmet-gray, `#2B2F33` mask-charcoal, `#1CE0A0`
  visor-green (glow), `#5B6B3A` g-suit-olive, `#F26522` safety-orange,
  `#4A4F55` hose-gray.
- **Distinctness** — Only concept with a **mirrored visor + oxygen-mask lump**
  and hard sci-fi edges: the sole modern/high-tech pilot.

---

## 5. BUSH RUNNER — barnstormer / bush pilot

- **Hero silhouette** — A battered soft **cloth flight cap** with round
  **goggles ON the eyes** (big brass rings sitting over the face, not the brow),
  and a **rolled map tucked under the wing** poking out as a pale cylinder — a
  scruffy, gear-laden, working-pilot look distinct from the polished uniforms.
- **Pilot tells**
  1. **Round goggles over the eyes** — two big `#C9A24A` brass rings with
     `#3A4A55` tinted-glass fill sitting **directly over the eye cluster**
     (unlike concept 2's brow goggles), joined by a leather bridge, each with a
     white glint. Purpose: the core barnstormer face — goggles down, ready.
  2. **Soft weathered flight cap** — a floppy `#7A6A4A` canvas cap over the
     head with a `#5C4E36` shadow crease and a little strap flap at the ear,
     softer/saggier than the rigid caps above. Purpose: worn field gear.
  3. **Rolled map under the wing** — a pale `#E7DBB8` cylinder (rounded rect +
     end-circle) with 2 thin `#B85C38` route lines, tucked at the wing-root
     (x ≈ 22, y ≈ 34) so it peeks out during flap. Purpose: unique "on a
     mission" prop — only this concept carries cargo.
  4. **Khaki shirt + leather harness** — a `#B8A66C` khaki chest block crossed
     by a diagonal `#5C4028` leather strap with a small brass buckle square.
     Purpose: bush-pilot rig, adds body detail.
- **Palette** — `#7A6A4A` cap-canvas, `#5C4E36` cap-shadow, `#C9A24A`
  goggle-brass, `#3A4A55` goggle-glass, `#B8A66C` khaki, `#B85C38` map-route.
- **Distinctness** — Only concept with **goggles worn down over the eyes** and a
  **rolled map prop** under the wing: the scruffy adventuring bush pilot.

---

## Ranking / notes

Strongest single-read at 40px: **#1 THE CAPTAIN** (peaked cap is the most
universal "pilot" shape) and **#4 VIPER** (the visor glow + mask lump are the
boldest silhouette break and give the store a modern option). **#2 ACE** brings
the best *motion* tell with its trailing scarf. **#3 RED BARON** and **#5 BUSH
RUNNER** widen the archetype spread (aristocrat villain vs. scruffy adventurer)
so the five never blur into "hat + jacket."

Watch-outs for the design loop:
- Keep tells as **big filled blocks**, not thin outlines — thin sleeve stripes
  (#1) and route lines (#5) are the riskiest at 40px; make them 2px min and
  high-contrast or drop to fewer, fatter marks.
- The **oxygen hose (#4)** and **scarf (#2)** must not read as collision hazards
  or clutter the belly — keep them tight to the body silhouette.
- Preserve the base eye glint where the face is visible (#1, #3, #5) for charm.
