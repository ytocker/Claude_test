# START as one object — five concepts (brainstorm, no renders)

Base: `harbour-post` (variant B), user-approved. Pip on a cloud upper-left;
three timber sign-boards (STORE / TOP 10 / SETTINGS) hang from that cloud on
ropes at cy 386 / 446 / 506, each 172x44; START currently a scarlet enamel
rectangle on a timber board at rect(208,494,136,100), on a post at x264 with a
diagonal brace and the chain's last rope mooring to it.

**The user rejected the two-layer construction.** START must become ONE object
where control and sign are the same thing, and it must belong to the chain.
**The three planks stay exactly as they look in the original B** — not
restyled, not re-laddered. Everything else is open.

## Colour gate
Separate from gold `_GOLD_BRIGHT (240,192,64)` H43.6 chroma 0.690 and rust
`_SCARLET_TOP (240,55,55)` H0.0 chroma 0.725 by **dH >= 110** OR
**chroma-ratio >= 3x with dLuma >= 35**. Shipped scarlet fails both (43.6 deg,
0.86x). Passing hue window for the dH arm: **H 154-250**.

| colour | RGB | H | chroma | luma | dH gold/rust | ratio gold/rust |
|---|---|---|---|---|---|---|
| bronze patina | (40,120,116) | 177.0 | 0.314 | 95.6 | 133.4 / 177.0 | 2.20x / 2.31x |
| signal teal | (20,132,146) | 186.7 | 0.494 | 100.1 | 143.0 / 173.3 | 1.40x / 1.47x |
| arc cyan | (120,236,238) | 181.0 | 0.463 | 201.5 | 137.4 / 179.0 | 1.49x / 1.57x |
| lacquer ink | (26,28,34) | 225.0 | 0.031 | 28.1 | 178.6 / 135.0 | **22.0x / 23.1x** |
| bone band | (240,236,226) | 42.9 | 0.055 | 236.1 | 0.8 / 42.9 | **12.6x / 13.2x** |
| collar iron | (66,70,80) | 215 | 0.047 | 76.0 | 172 / 144 | **~15x** |

---

## 1. `ring-out` — the harbour bell
**Thesis.** A rope run exists to end in a bell; make START the thing the chain
was always falling toward.

**What it is.** A cast-bronze harbour bell, hung by its iron crown-staple from
the chain's last rope, START struck in gold across its flared skirt, a hemp
bell-rope dropping to a monkey's-fist knot at thumb height.

**Relation to the planks.** Same `rope()` catenary, same `IRON`/`IRON_HI`
hardware — the bronze is the plank nails and rings grown up and given a job.
Same `_tracked_label` gold-over-dark-twin at 30px instead of 17px. It is the
chain's terminal *weight*: the planks hang, this is what they hang toward.

**Construction.** One closed polygon, no rectangle: crown staple (two arcs +
iron ring) -> shoulder (flattened dome) -> concave waist -> convex flare to a
wide lip -> thicker brighter sound-bow with five shallow scallops. "Sign-bell"
proportion ~120 across the lip, ~76 tall, so the skirt is a broad trapezoid
type field. Five-stop bronze gradient + two speculars (hot vertical left of
centre, cool bounce down the right). Two incised reeding lines above the type.
START **struck in relief** on a ~6 deg downward arc. Iron clapper pear below
the lip; bell-rope width 3, sag 4, to a three-loop monkey's fist — the visible
"grab here". Hangs 4-6 deg off true like the planks. Lip x200-320, body
y500-580, knot y<=600.

**Colour.** Body `(40,120,116)`, shade `(18,64,66)`, polished lip + reeding
`(96,196,180)`, patina flecks `(120,206,180)` a~40.

**Elsewhere.** Post and brace deleted. A **bell-cot** replaces them: two raked
timber legs meeting a cross-head, planted around x250 with stone footing pads.
The last rope stops being a mooring line and becomes the bell's hanger — one
continuous run, cloud to bell.

**Delight.** Tap swings the bell 8 deg and throws two expanding bronze
ring-arcs off the lip. Idle sway +-1.5 deg.

**Feasibility.** Polygons + ellipse arcs; cache body per biome key, rotozoom a
~130x110 surface for sway. Scallops via scratch surface + BLEND_RGBA_MIN (the
pattern `timber_board` already uses). Arced type = 5 cached glyph rotozooms.

---

## 2. `beacon` — the lantern whose light spells the word
**Thesis.** START isn't painted on anything; it is cut out of the glass, so the
word IS the light.

**What it is.** A six-sided glazed harbour lantern hanging on an iron bail from
the chain's last rope, its lit panel reserved to read START, throwing a cyan
pool onto the timber below.

**Relation to the planks.** Same twin-rope suspension, same iron ring bail. Its
**roof cap is a miniature of the plank silhouette** — the identical chamfer +
V-notch cut profile, in timber, folded into a hexagonal pyramid. Cage ribs are
the plank nails drawn out into iron. It is the only light source on screen,
which makes the warm side-light already falling on the three planks *diegetic*
rather than assumed.

**Construction.** Iron ring bail -> timber roof pyramid with chamfered eave lip
and gold finial -> glazed drum of five visible facets (wide centre, two
narrowing each side, so it reads round without a circle) divided by iron corner
posts -> heavy iron base collar with drip lip and three vent slots. ~124w x
104h at x210-334, y480-584. Build order: flame ellipse -> smoked glass over it
-> punch the word out of the glass with a text mask so the flame reads full
brightness -> bloom pass around the letters. Plus a diagonal specular sweep
(`store_cards.gloss_sweep` is the shipped precedent), one glazing bar at the
panel's third, and a light pool cast down on the bracket and up onto the
SETTINGS plank's underside.

**Colour.** Glass `(20,68,84)`, lit letters `(120,236,238)` with a
`(236,252,250)` hot core, halo low-alpha.

**Elsewhere.** The timber post becomes a **cranked iron lamp bracket** off a
stone footing — slim standard, scrolled top, small stay — so no second timber
competes with the planks. The brace becomes the scroll. Last rope ties to the
bracket hook: cloud -> planks -> hook -> lantern. Glow alpha keys off `biome`
phase so the lantern earns the 5-minute cycle.

**Delight.** The word breathes — +-6% flame flicker at ~1.2 Hz with jitter. At
night, when the plate drops to L16.5-21.3, it is the brightest thing on screen
and pulls the eye exactly where the thumb belongs. Tap = flare washing the
bottom band for 0.2 s.

**Feasibility.** One cached body per biome key; per-frame flicker is a single
`fill(..., BLEND_RGBA_MULT)` on a 124x104 layer. Glow on a scratch SRCALPHA
layer since `pygame.draw` writes alpha.
**FLAG FOR THE DIRECTOR:** `lantern-street` was rejected in round 6. This is a
*single lantern as the control object*, not a lantern-lit street, but it shares
the motif and deserves an explicit ruling.

---

## 3. `clear-arm` — the launch signal
**Thesis.** Make the chain do work: the rope that hangs the menu is the wire
that pulls the signal to clear.

**What it is.** A lower-quadrant signal arm on a riveted iron post — a tapered
blade with a fishtail end, pivoted on a spectacle casting with two glazed
lenses, carrying START in gold along its length, that drops to 45 deg "clear"
when tapped.

**Relation to the planks.** The blade's **fishtail is the planks' V-notch
promoted from decoration to silhouette** — the same cut, at full size, as the
defining feature. Identical gold tracked lettering. The post is the same timber,
hooped with the same iron. And the chain's last rope becomes the **operating
wire**: it leaves SETTINGS, runs through a guide pulley on the post, and ties to
the arm's crank. The sign chain literally works the control.

**Construction.** Slim timber standard at x~300 with three iron hoops and a cast
finial; a **lattice stay** (zigzag of 2px iron struts) triangulating to the
ground on the right. At the head a figure-eight **spectacle plate** holding two
lenses. The **blade** cantilevers left from the pivot, ~96 x 28, slightly
tapered, fishtail bitten out of the free end, rolled top edge, -6 deg at rest,
-45 deg on tap. Ink lacquer body, **bone band** across the outer third, 1px bone
keyline, two rivet rows. START in gold-pale tracked +2 at 22px with the dark
twin, horizontal at rest. Below the pivot a counterweight lever and cast weight
— the one heavy round note. Blade x200-296, y505-535 at rest; tap rect
x196-346 x y498-560 (150x62), disjoint from SETTINGS (right edge ~196, bottom
~529).

**Colour.** Blade `(26,28,34)` — passes BOTH arms. Band `(240,236,226)` passes
the desaturated arm. Lit lens `(120,236,238)`, dark lens `(20,60,70)`.

**Elsewhere.** The fat diagonal brace is deleted — the lattice stay replaces it,
thin enough that the corner stops feeling boxed in. Stone base block with a bolt
ring; pulley bracket halfway up. The last rope changes *line quality*: taut and
straight with one kink at the pulley, against three sagging hangs above. The
utilities hang; START is rigged.

**Delight.** Tap drops the arm to 45 deg with a small overshoot and flips the
lens dark->lit. "Line clear, proceed" is the literal semantic of the button.
Idle: 0.5 deg tremor keyed off the existing `weather` gust state.

**Feasibility.** Blade cached, rotozoom per frame. Lattice ~12 draw.line calls.
**KNOWN RISK:** a long horizontal blade could read as a fourth plank at
thumbnail size. The post, spectacle, counterweight and lattice should prevent
it; if not, shorten the blade to ~88 and deepen the fishtail. Masthead sits near
y468 so the spectacle plate needs the two-step contour — the design carries both.

---

## 4. `colours-up` — the launch flag
**Thesis.** One soft thing in a world of timber, iron and rope — and it's the
only thing that moves, so the eye goes straight to it.

**What it is.** A swallowtail signal flag bent onto a halyard and hoisted up a
raked mast, its fly carrying START in gold on a teal field, the halyard's fall
coiled on a cleat at thumb height.

**Relation to the planks.** The **swallowtail is the planks' V-notch rendered in
cloth** — the same bite out of the end face, softened by material. The chain's
last rope IS the halyard, run through an iron block at the masthead, so the
flag's hoist edge is where the whole run terminates. Iron grommets down the luff
are the plank nails. Identical gold tracked type.

**Construction.** Raked timber mast (~8px, 6 deg right) with iron truck, masthead
block, two hoops, and a **cleat** at y~560 with a figure-eight hemp coil. Flag
flies left, ~112 x 72 at the hoist, tapering to a shallow swallowtail; left tip
kept at x>=204 to clear SETTINGS. Drawn as a **warped quad grid**: 12 vertical
strips whose top and bottom edges follow a travelling sine (amp 4px, lambda 70,
phase = t*1.6), each strip shaded by its local normal — crests bright, troughs
18% darker — so the cloth ripples with no per-pixel work. Darker hoist band with
three grommets down the luff. START rendered flat once, then **sampled through
the same warp** (column-by-column blit with a per-column y offset) so the type
rides the cloth. 2px gold border follows the warped outline, swallowtail included.

**Colour.** Field `(20,132,146)`, crest `(58,178,190)`, trough `(12,86,98)`,
hoist band `(14,74,84)`. Gold on teal is the most legible pairing available and,
being complementary, reads as the *same* gold the planks use.

**Elsewhere.** Post and brace become the raked mast plus two thin **shroud**
lines to iron eyes in the ground band — diagonals instead of a fat timber, which
opens the corner. Small timber mast-step at the foot. The last rope becomes
rigging with a real termination: block, fall, cleat, coil.

**Delight.** The flag ripples continuously — a living primary CTA. On tap it
snaps taut and two-blocks up 6px with a cloth crack. On first launch it could run
*up* from half-mast over 0.4 s: colours up, we're flying.

**Feasibility.** 12 quads + 12 subsurface blits per frame over 112x72 — trivial,
identical on both targets, no numpy. Cache the flat flag+type; only the warp runs
per frame. **RISK:** warped type softening — keep amplitude <=4px and set the word
in the flag's flattest third near the hoist.

---

## 5. `the-drop` — the sky-well
**Thesis.** The button shouldn't say "start", it should BE the way in — and in a
flyer, the way in is falling.

**What it is.** Not an object but an opening: an iron-collared circular well cut
through a cloud floor, its hinged deck-leaf standing open, cyan light and vapour
pouring up, START struck in gold around the collar's near rim.

**Relation to the planks.** The collar is the plank family's iron at the largest
size on screen, and its eight **dogs** (wing-bolts round the rim) are the plank
nails scaled up and put to work. The open leaf is a timber plate cut with the
**identical chamfer + V-notch profile** as the three planks — so the one
plank-shaped element is the one that's been *lifted out of the way*. And the
chain's last rope belays to a ring on the raised leaf and takes its weight: the
sign chain is what's holding the door open.

**Construction.** An ellipse, never a rectangle. Outer collar ~136x54 (24 deg
view angle) centred (272,556), x204-340. Bevelled iron rim, bright top-left, dark
bottom-right; eight dogs; an inner ellipse that is the **void**, a vertical ramp
from near-black at the far lip to cyan-white at the near lip, with three vapour
arcs curling over the front edge and a few drifting motes. The hinged leaf stands
back at ~70 deg, a foreshortened timber ellipse-plate on a strap hinge, underside
in shade, top edge catching cyan rim-light off the well. START runs as an **arc of
tracked gold glyphs** along the near rim, each rotozoomed to its tangent,
gold-pale over a dark cast twin — a manhole legend curving toward the reader. Soft
elliptical light wash on the ground beneath.

**Colour.** Collar `(66,70,80)` with `(150,156,166)` highlight. Well light
`(120,236,238)` -> `(14,74,84)` -> `(10,14,20)`.

**Elsewhere.** Changes the most, deliberately. Post, brace and mooring ring all
go. In their place a low **cloud bank** across the bottom band, drawn with the
game's own cloud lobe vocabulary rather than an invented material, through which
the well is cut. That gives the menu a *floor* it currently lacks: the chain
hangs from a cloud and lands on a cloud, closing the composition, with START the
only thing below the planks and real emptiness around it.

**Delight.** The strongest metaphor of the five, and it prefigures the first
second of gameplay. Vapour curls upward continuously; on tap the leaf slams shut
behind you as the scene cuts.

**Feasibility.** Ellipse arcs + polygons; vapour is three cached puffs on sine
paths. Light wash on a scratch SRCALPHA layer. The cloud bank must be menu
furniture, not the scrolling near-lane, or it will slide.
**KNOWN RISK:** arced 5-glyph type at 18-20px is the weakest type-carrier of the
five. Mitigation — flatten the arc to +-8 deg total, or move the word to a struck
flat chord on the collar's front face.

---

## Distinctness

| | material class | silhouette class | relationship to the chain | how START is carried |
|---|---|---|---|---|
| `ring-out` | cast bronze | convex resonant body | rope becomes the bell's hanger | struck in relief, arced |
| `beacon` | glass + iron + flame | glazed faceted vessel | rope becomes hanging tackle | reserved out of the glass, backlit |
| `clear-arm` | iron lacquer + bone | articulated kinetic blade | rope becomes the operating wire | painted along a rigid blade |
| `colours-up` | woven cloth | soft warped swallowtail | rope becomes a halyard, hoisted | printed on cloth, warped |
| `the-drop` | void + iron collar | aperture — a hole, not an object | rope belays and holds the leaf open | struck around a ring |

## Designer's picks
1. **`clear-arm`** — most complete answer. Control, sign and mechanism are
   genuinely one object; the fishtail is a real structural inheritance rather
   than a shared colour; the chain becomes rigging; the tap animation IS the
   button's meaning; passes the colour gate on both arms with the largest margin.
2. **`colours-up`** — most elegant holistic tie (V-notch -> swallowtail in a new
   material), the only continuous motion, gold-on-teal the strongest legibility
   pairing while still reading as the planks' own gold. Cheapest to render.
3. **`beacon`** — biggest day/night payoff by a distance, the only concept that
   makes the existing lighting diegetic. Held at three only because of the
   `lantern-street` adjacency.

`ring-out` is the most charming and most non-rectangular but has the thinnest
type field. `the-drop` is the boldest and the weakest type-carrier — worth
maturing precisely because it stops being a button at all.

**Bench alternate:** `the-windlass` — START as a timber windlass drum between two
iron cheeks, the chain's tail visibly wound onto it in turns, with a crank and
pawl; the word rides the barrel's horizontal shading band. Excellent type
surface, most literal "this is what the chain was for", a sixth distinct
relationship to the rope.
