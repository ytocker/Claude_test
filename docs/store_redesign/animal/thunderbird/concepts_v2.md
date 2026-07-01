# Thunderbird — Electric-Core Concepts (Designs 6–10)

Second batch of 5. Core direction: **electricity IS the bird** — lightning as
body/feathers/bones, not accessory. **Electric yellow is the PRIMARY color**,
not an accent. Each design uses a DIFFERENT electricity metaphor.

Canvas: 64×84 SRCALPHA. Body centered (32,44), head near (44,34). Ellipses,
polygons, arcs, lines, glow blits — no PNGs. 4-frame flap. Must read at 40px on
bright-day AND night sky.

**Off the table (batch 1 — do not echo):** STORM HERALD (cloud body, cold
blue), TOTEM THUNDERBIRD (flat formline), SOLAR WAR CHIEF (gold war-bonnet +
sun-disc), NIGHT THUNDER (dark indigo, violet scars), ANCESTRAL SPIRIT
(spectral teal-lilac shimmer).

Reference sparks: plasma-globe tentacles (neon/argon discharge), Tesla-coil
corona arcs, PCB copper traces + solder-mask glow, ball-lightning fireballs
(white-yellow core), high-voltage power-line arc-flash (white-hot yellow arc).

---

## Ranked #6 (BEST) — PLASMA SURGE  ·  `skin_thunderbird_plasma`

- **Metaphor:** Plasma-globe bird. The body is a glowing ionized-gas core and
  the feathers are the crackling plasma tentacles that reach for the glass.
- **Hero silhouette:** A compact bright-cored bird whose wing and tail feathers
  are individual jagged lightning bolts fanning outward — no solid feather
  edges, the outline is all forked arcs.
- **Objects + placement:**
  - **Head/crest:** small round white-hot head at (44,34); crest = 3 thin bolts
    zig-zagging up-back like raised antennae, brightest at the tips.
  - **Body:** radial-gradient ellipse, white core → yellow → thin amber rim; a
    faint inner nucleus dot so it reads as "charged."
  - **Wings:** each of the 4 flap poses is drawn as 3–4 forked polyline bolts
    (not a filled wing), thick near the body, splitting into thinner branches at
    the tips. Flap = the bolts sweep and re-fork, so the bird visibly crackles.
  - **Tail:** 2–3 trailing bolts.
  - **Talons:** two tiny bright arc-hooks.
  - **Atmosphere:** soft yellow radial glow blit under the whole body + a couple
    of stray spark dots that flicker per frame.
- **Palette:** Core White `#FFFFFF` · Electric Yellow `#FFE81A` (dominant) ·
  Voltage Gold `#FFB300` · Arc Amber rim `#FF7A00` · faint Ion Violet
  branch-tips `#B36BFF`.
- **Distinctness:** The ONLY concept where feathers don't exist as shapes at
  all — the whole bird is forked bolts radiating from a core. Batch 1 all kept
  solid bird bodies; this one is pure discharge. Reads instantly at 40px because
  the jagged bolt-fan is the silhouette.

---

## Ranked #7 — BALL LIGHTNING  ·  `skin_thunderbird_orb`

- **Metaphor:** Ball-lightning fireball. A hovering sphere of white-yellow
  charge that has *just barely* organized itself into bird form.
- **Hero silhouette:** A dominant glowing orb (the body) with short stubby
  bolt-wings — reads as a comet/fireball with a face, round and heavy.
- **Objects + placement:**
  - **Head/crest:** the head is a smaller satellite orb fused to the main body
    at (44,34); two spark-eyes. Crest = a lick of flame-like bolt curling up.
  - **Body:** big central orb, layered radial gradient (white nucleus → yellow →
    gold halo), with 4–5 tiny electric arcs skittering across its surface
    (short curved polylines) that reposition each frame — the "crawling"
    ball-lightning tell.
  - **Wings:** short, thick, blunt bolt-stubs — more like flame flares than full
    wings; the 4 poses pulse them out and in (a throb, not a sweep).
  - **Tail:** a short comet-like ember trail of 3–4 fading dots.
  - **Talons:** implied — two sparks hanging below.
  - **Atmosphere:** strong bloom halo; occasional full-orb brightness pulse.
- **Palette:** Nucleus White `#FFFFFF` · Fireball Yellow `#FFD400` (dominant) ·
  Ember Gold `#FFA000` · Scorch Orange `#FF6A00` · thin Corona `#FFF3B0`.
- **Distinctness:** The round, heavy, orb-dominant silhouette — a *ball*, not a
  spread-wing bird. Metaphor is contained/pulsing energy vs #6's radiating
  discharge. Nothing in batch 1 was orb-shaped; the surface-crawling arcs are
  unique to this one.

---

## Ranked #8 — CIRCUIT RAPTOR  ·  `skin_thunderbird_circuit`

- **Metaphor:** Overloaded PCB. The bird is a printed circuit board — feathers
  are copper traces, joints are solder pads, and current lights up the paths.
- **Hero silhouette:** A crisp hard-edged bird whose body and wings are paneled
  into geometric segments, veined with glowing right-angle trace-lines.
- **Objects + placement:**
  - **Head/crest:** angular faceted head; eye = a round glowing solder pad.
    Crest = two straight antenna-traces ending in bright node dots.
  - **Body:** dark board-green base ellipse overlaid with bright yellow trace
    polylines that branch in 90°/45° steps, with small filled pad-dots at the
    junctions (nodes pulse brighter in sequence across frames = current flowing).
  - **Wings:** each wing is a flat angular panel with 3–4 parallel traces running
    to the tip; flap = the traces "energize" tip-to-root so the wing looks like
    it's conducting the flap.
  - **Tail:** a bus of 3 parallel traces.
  - **Talons:** two bright right-angle bracket hooks.
  - **Atmosphere:** faint yellow trace-glow bloom; a couple of drifting data
    sparks.
- **Palette:** Board Dark `#0E2A1E` (structure/value anchor) · Trace Yellow
  `#FFE81A` (dominant) · Bright Node `#FFFFFF` · Solder Gold `#C8A032` · Signal
  Green-glow `#9CFF57` (sparingly, for one accent trace).
- **Distinctness:** The only HARD-EDGED, geometric, man-made-tech reading in
  either batch — right angles and pads vs everyone else's organic bolts. The
  dark board base gives it a killer value structure against bright-day skies.
  Sequenced node-pulsing is a flap tell no other design has.

---

## Ranked #9 — TESLA CROWN  ·  `skin_thunderbird_tesla`

- **Metaphor:** Tesla coil. The bird's head is the coil terminal and arcs leap
  continuously off its crown and wingtips like a corona discharge.
- **Hero silhouette:** A sleek dark-bodied bird crowned and haloed by an arc of
  jumping bolts — the electricity rings the top edge like a diadem.
- **Objects + placement:**
  - **Head/crest:** the standout — a bright toroid/knob terminal on the head
    (44,34) with a fan of thin arcs leaping upward and curling back to the
    shoulders, forming a lightning halo above the bird.
  - **Body:** smooth dark-charcoal bird body with a subtle yellow rim-light, so
    the arcs read as brilliant against it. Chest carries one bright vertical
    conduction line down the sternum.
  - **Wings:** solid dark wings but each wingtip sheds a small corona arc that
    reconnects to the halo; flap = the halo arcs stretch and snap as the wings
    move (the discharge follows the motion).
  - **Tail:** dark, with two bright arc-tips.
  - **Talons:** two small charged claws.
  - **Atmosphere:** tight yellow-white corona glow ringing only the top half.
- **Palette:** Charcoal body `#1A1D24` (dark anchor) · Coil Yellow `#FFE81A`
  (dominant on arcs) · Corona White `#FFFFFF` · Terminal Gold `#FFC01A` · thin
  Ozone Blue arc-cores `#7FD8FF`.
- **Distinctness:** Inverts the batch — a DARK solid body used as a stage for a
  bright TOP-crowning arc halo, vs #6/#7 which are bright all over. Distinct
  from NIGHT THUNDER (batch 1) because that was violet-scarred menace; this is
  clean yellow corona spectacle. The halo is the read at 40px.

---

## Ranked #10 — LIVE WIRE  ·  `skin_thunderbird_livewire`

- **Metaphor:** Snapped high-voltage power line. The bird is a whipping,
  arc-flashing cable — sinuous, industrial, dangerous.
- **Hero silhouette:** A long lean bird whose body and neck read as a thick
  cable, with a blinding arc-flash burst where the "break" is (the chest/head).
- **Objects + placement:**
  - **Head/crest:** head is the frayed cable end — a splayed burst of short
    bright filaments (the arc flash) at (44,34); a single spark-eye. No feather
    crest; the fray IS the crest.
  - **Body:** elongated cable-like body with a subtle segmented/insulated banding
    (2–3 darker rings) so it reads as wire; a super-bright arc-flash bloom at the
    chest where current jumps.
  - **Wings:** each wing is a whipping cable-loop that trails a thin arc; flap =
    the cables lash (sine-whip) and the arc-flash pulses brightest on the down
    pose — a strobing overload feel.
  - **Tail:** a long trailing wire with a sparking severed tip.
  - **Talons:** two hook-clamps (like line-grips).
  - **Atmosphere:** hard white arc-flash bloom at the break + falling molten
    spark dots.
- **Palette:** Arc-Flash White `#FFFFFF` · High-Voltage Yellow `#FFDD00`
  (dominant) · Live Gold `#F5A300` · Insulation Dark `#2B2620` (banding/value) ·
  Molten Spark `#FF5500`.
- **Distinctness:** The only ELONGATED, sinuous, industrial-hazard silhouette —
  a whipping cable vs everyone else's classic bird proportions. The banded
  insulation + strobing arc-flash break is a unique tell; danger/overload mood
  no batch-1 design carries.

---

## Director's picks

- **Strongest overall / lead:** **#6 PLASMA SURGE.** Purest expression of the
  brief — the bird literally *is* forked lightning, no feather shapes at all,
  maximal electric yellow, unmistakable 40px silhouette. This is the flagship.
- **Best showpiece runner-up:** **#7 BALL LIGHTNING** for its bold non-bird orb
  read and #8 CIRCUIT RAPTOR for the freshest metaphor + best day-sky value
  structure (dark board base).
- **Spread check:** radiating discharge (#6) · contained pulsing orb (#7) ·
  hard-edged tech/PCB (#8) · dark-body top-crown corona (#9) · elongated
  industrial cable (#10). Five different silhouettes, five different electricity
  metaphors, yellow primary throughout.

Sources / reference sparks:
- Plasma globe / Tesla-coil discharge & gas colors —
  https://scienceandnature.com/plasma-ball/ ,
  https://www.arborsci.com/products/8-plasma-globe
- Electric arc / corona / arc-flash colors —
  https://en.wikipedia.org/wiki/Electric_arc ,
  https://en.wikipedia.org/wiki/Arc_flash
- PCB trace / neon circuit aesthetic —
  https://medium.com/@pcbsync/how-i-made-custom-led-art-with-pcbs-eeacf7ca033b
