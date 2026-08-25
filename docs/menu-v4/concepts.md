# menu-v4 — five holistic main-menu concepts (brainstorm, no renders)

## Two findings that reframe the brief

**A. Three value zones, not one.** Sampling the real composite
(`_draw_mountain_silhouette` alpha 180 over the veiled sky):

| band | day L | night L | swing |
|---|---|---|---|
| y < 360 — always open sky | 106 | 20 | 86 |
| y 360-490 — the ridgeline crosses here | mixed 106 AND 46 in one plate | mixed 20/21 | worst case |
| y > 490 — always ink ridge | 41-46 | 16-21 | 25 |

"Polarity inverts twice per cycle" is true only ABOVE y~360. Below y~490 the
field is a near-constant dark ink plate: a fixed light CTA there clears 50-200
at both poles with no trickery.

**The current START pill (cy 430 => y402-458) sits exactly in the straddle
band** — by day its top half is a dark figure on L106 sky and its bottom half a
light figure on L46 ink, within one 240px shape. That is a large part of why it
reads muddy, and it is independent of its colour. Thumb-reach points the same
way: START wants y~495-545. Every concept either does that or draws its own
opaque ground plane behind the CTA.

**B. Four secondaries, not three.** PROFILE (the frame around Pip, -> achievements)
is an entry point too. And `best` is passed into `draw_menu` and never drawn —
VERIFIED by the orchestrator: zero references in the method body. The player's
high score is absent from the menu. Every concept below places PROFILE and
surfaces BEST.

## Shared craft rules
- Two-step contour everywhere: outer hue-matched near-black keyline (L14-26,
  never pure black) + inner pale crown (L185-232). Day separates on the dark
  step, night on the pale step. Reuse `store_design`'s `bevel_rim` stack.
- No blur, no bloom. Light is banded stepped rings + hard specular slivers.
- Build once, blit per frame: author at SS=2 (720x1280), one `smoothscale` down,
  cache module-level. Only the CTA pulse redraws. Proven on WASM.
- Saturation is an accent, not a field. The one saturated thing is START.

## Strategic gap being aimed at
Themed concepts died as "unrelated to the game's style"; world-built concepts
died as "too much like current in-game design." The seam between them is
**Skybit's own UI/ornament craft language** — the `store_design`/`store_hub`
metalwork (rim-shine gold stacks, double-bevel perimeters, facet gems, gradient
type, the `_CROWN` medallion build) plus the material vocabulary of
`pillar_pagodas` (cinnabar lacquer, gilt, patinated bronze, cedar, plaster,
jade). Unmistakably this game's, at the highest craft bar the project has
shipped, and NOT gameplay furniture. All five are built from it.

---

## 1. `cinnabar-gate` — the threshold
**Thesis.** The menu is a lacquered temple gate seen head-on; START is the lit
doorway you tap to walk through. The CTA is a *place*, not an object.

**START.** Vertical doorway plate between two columns, inner rect ~150x86 at
(180,505). Cinnabar lacquer, vertical gradient, horizontal specular at 38% height.
face top `(236,88,52)` L128 · face mid `(206,52,34)` L96 · face bot `(138,28,20)` L60
keyline `(44,12,8)` L21 · gilt frame `(240,192,64)`->`(255,232,168)` L192->232.
Plate is RECESSED — gilt frame catches light top and left inner edges, lacquer
sits 3px behind, contact shade under the frame. Nine gilt door-studs 3x3 flank
the type. Type `_GOLD_PALE` L232 with `(44,12,8)` engrave-shadow at +1/+1.

**Separation.** Entirely below y~490 on ink (day 41-46, night 16-21). Lacquer
L60-128 = delta 14-87 day, 39-112 night. Gilt frame L192 = delta 146-176 day,
171-176 night. **The frame holds the silhouette; the lacquer makes it expensive.**

**Construction.** Post-and-lintel. Two lacquer columns from stone plinths to a
crown beam at y~300-330 with upswept eave curls and a tile-ridge cap.
Rectilinear with two calligraphic exceptions — how a paifang reads. Secondaries
are three cedar plaques hung from the beam's underside on short chains at y~355,
74x40, gilt hairline + struck icon: signage, not buttons, so they cannot compete
with a glowing doorway. BEST is a gilt cartouche in the lintel centre. PROFILE is
the left column's upper niche.

**Pip.** Sits above-left of the crown beam's left eave curl — arriving at the
gate. The eave upsweep points at him; the beam's shadow falls beneath him so he
reads in front. He is the diagonal counterweight to a rigidly symmetric gate.

**Delight.** On tap the doorway flares from lacquer to warm interior light for
200ms before the cut — you go through the door.

**Cross-screen.** NONE. Stays in the `_RED_OUTLINE` family, so TAP TO GAME and
PLAY AGAIN are unchanged. Lowest-risk option.

---

## 2. `jade-seal` — the artifact
**Thesis.** The screen is a collector's presentation case holding one carved jade
seal; START is the seal's face. The CTA is a precious object, the menu is the
velvet it sits on.

**START.** Chamfered jade slab ~186x74 at (180,512), corners cut 45° — an
octagonal footprint, the anti-pill. 5-band vertical gradient + diagonal internal
cloudiness (two low-alpha polygons) so it reads as stone, not plastic.
face top `(168,224,192)` L204 · mid `(96,178,146)` L150 · bot `(44,116,96)` L92
engrave groove `(198,54,36)` cinnabar L95 · keyline `(10,34,30)` L26.
"START" is INTAGLIO — cut into the jade, groove filled with cinnabar seal-paste
(real 朱文 construction), 1px `(255,240,225)` catch-light on the groove's
upper-left wall. Thin gilt band wraps the chamfer.

**Separation.** Jade is the one hue not in the gold/red family (H146-163 vs title
H44, engraving H7) — pre-attentively the CTA. L92-204 vs day ink 41-46 =
delta 46-163; vs night 16-21 = delta 71-188. Never inverts polarity: a permanently
light figure on a permanently dark plinth. **Strongest raw-contrast answer of the
five and the cleanest literal answer to "what colour should START be."**

**Construction.** Chamfered blocks, no curves. A shallow open lacquer
presentation case at y~420-620: black-lacquer walls, mitred gilt inlay 6px in
from every edge, brocade-red felt bed as fine cross-hatch. Seal lies in the upper
well; a lower tray holds three recessed tool niches for the secondaries — sunken
squares, icon struck into the felt, gilt hairline lip. **Secondaries are holes;
START is the one thing standing proud.** That figure/ground split, not size, is
what stops them competing. BEST engraved into the case's front lip in gilt.
PROFILE is the raised lid.

**Pip.** The case's lid stands OPEN, hinged left, raked back, inner face a
gold-leaf panel. Pip flies in front of the lid's upper-left corner — the gold
panel is the bright ground that makes his silhouette read at both poles, and the
lid frames him as the case's crest. He is the only curved, organic, moving thing
against a screen of hard chamfers.

**Delight.** On tap the seal presses down 3px and stamps a cinnabar impression of
the Skybit mark onto the felt beside it. Most "premium object" screenshot.

**Cross-screen.** Breaks the `dim` family. Recommend scoping the menu as
deliberately special — the pause/game-over pills sit on live gameplay, are
utilitarian, never seen beside the menu. Fallback if full coherence wanted: a
small jade badge on the two overlays, ~20 lines.

---

## 3. `cloisonne-gong` — the instrument
**Thesis.** A bronze gong hanging in a timber frame; START is the gong's face — a
big round enamelled disc you strike, replacing the pill silhouette entirely.

**START.** Cloisonné disc r=66 at (180,500). 景泰蓝 construction: flat enamel
colour cells separated by 1px gilt wire. Concentric rings — outer ring of 16
ruyi-lobe petals, middle ring of 8, plain central boss carrying the type.
enamel highlight `(140,214,236)` L194 · body `(46,150,190)` L124 ·
deep `(22,96,134)` L78 · gilt wire `(226,180,86)` L183 · keyline `(8,26,38)` L22.
Kingfisher blue (点翠) is a genuine imperial palette colour and makes START the
only cool-saturated thing on a warm screen. Each petal cell gets a 2-step
gradient (deep at rim, body at centre) so the disc has spherical volume with no
blur. Boss: "START" gilt L183 on enamel-deep L78, internal delta 105.

**Separation.** Disc mean L~124 vs day ink 41-46 = delta 78-83; vs night 16-21 =
delta 103-108. Gilt wire mesh L183 adds a second step at delta 137-167. A circle
also wins on SHAPE — the only closed curve among ridgelines and rectangles — so
it survives a bad value moment.

**Construction.** Suspension. A cedar A-frame — two raked posts meeting a
crossbeam at y~330. Gong hangs on two braided cords with visible knot and tassel.
Shape language is arcs, catenaries, radial symmetry: everything hangs or is round.
Secondaries are three small bronze bells strung along the crossbeam at y~365,
26px each, struck icon on the skirt, label on a wooden tag below — round-adjacent
but a fifth of the area, so hierarchy is unambiguous. BEST branded into the
crossbeam. PROFILE a carved medallion on the left post.

**Pip.** The A-frame's left post crosses y242-292 exactly where Pip is. Put the
joinery notch and a short perch peg there: Pip sits in the crook where post meets
beam, where a real bird would sit. **Most naturally motivated Pip placement of
the five** — his fixed position becomes the reason the frame is shaped that way.

**Delight.** On tap the gong swings on its cords, the tassel lags, and the three
bells ring in sequence as the transition fires. Motion is the hook.

**Cross-screen.** Breaks the `dim` family. Blue is furthest from the title's rust,
so weakest fit if CTA/title kinship (`hud.py:41-47`) is to be preserved — though
that kinship is arguably what made the current CTA disappear.

---

## 4. `silk-noren` — the soft goods
**Thesis.** The menu is cloth, not architecture — a scalloped silk valance with
hanging panels. START is the widest panel in imperial amber: no straight edges,
no metal.

**START.** A hanging noren panel ~196w x 96h, top edge y~470, hanging to y~566.
It is CLOTH: straight rod-pocket top, shallow catenary hem sag, left/right edges
bow out 4px, two low-alpha fold-shadings at 28% and 72% width for drape.
silk top `(248,196,86)` L199 · silk bottom `(206,140,44)` L149 ·
ink type `(40,22,12)` L26 · hem keyline `(58,30,10)` L36.
**"START" is dark ink on bright silk** — the only concept inverting type
polarity, correct here because that is how dyed cloth signage works. Internal
contrast delta 123-173, highest type contrast of the five. Hand-brushed weight
variation (2px taper at terminals) sells dye rather than print.

**Separation.** A large uniformly BRIGHT field: L149-199 vs day ink 41-46 =
delta 103-158; vs night 16-21 = delta 128-183. **Most robust separation of any
concept** because it depends on value mass, not on a rim. Amber H36-41 sits close
to the title's gold H44 — resolved by value and saturation: the title is a thin
gold outline-stroke at S85 on a dark rim, START is a solid S65-92 field. One is
line, one is mass; they never read as the same object.

**Construction.** Catenaries, scallops, fringe. A scalloped valance across
y~300-340, five lobes whose profile is the `_ruyi_lobe` silhouette already in
`cloud_variants.py`, deep indigo silk with gold-thread border and a knotted
tassel at each lobe's low point. From its rod hang four panels: the amber START
panel centred and low, and three narrower indigo panels for the secondaries
hanging shorter and higher (y~390-450) with pale-gold embroidered icons.
**Secondaries are the same KIND of object as START, differentiated purely by
width, length and dye** — a proportional hierarchy, the most elegant CTA/secondary
relationship of the five and the hardest to get right. BEST embroidered on the
centre lobe. PROFILE a circular embroidered badge on the left lobe.

**Pip.** The valance's left lobe dips into a notch at x~90, y~300; Pip sits in
that notch with a tassel beside him — perched on the cloth. He is silhouetted
against open sky at y242-292 (full-swing zone) but he is the game's own sprite
with its own internal contrast, and the indigo valance directly under him gives a
permanent dark base for his lower edge at both poles.

**Delight.** Everything sways — panels on independent out-of-phase pendulum
motion, tassels lagging; a 3-line sine per panel that makes the screen feel alive
in a way no rigid menu can. On tap the START panel lifts as though you pushed
through it.

**Cross-screen.** Breaks the `dim` family AND inverts type polarity, so a badge
fallback does not translate. Menu-only scoping, firmly.

---

## 5. `ridge-cut` — the negative space
**Thesis.** The whole UI is one sheet of ink-black paper cut away in the 剪纸 /
window-lattice tradition, lit from behind. START is not an object with a colour,
it is **a hole with light coming through it** — structurally immune to the
day/night polarity flip.

**START.** A cut-out cartouche at (180,508), a 200x80 lozenge with ruyi-lobed
ends. The paper is removed; behind it sits a warm lantern light plane. The
letters are BRIDGED CUT-OUTS IN REVERSE — paper retained as the letterforms so
type reads dark against the glowing aperture, with the paper-cut tabs (the
bridges keeping counters attached in a real paper-cut) left visible as signature
detail.
paper `(18,12,26)` L15 · paper lit edge `(30,22,42)` L27 ·
light `(255,228,168)` L229 · light hot centre `(255,248,224)` L247.
The light plane is a stepped radial ramp — 5 hard concentric bands, no blur —
plus a 1px `(255,248,224)` bevel on the aperture's lower-right cut edge and 1px
`(8,4,12)` upper-left. **That single asymmetry is what makes it read as cut paper
rather than a glowing rectangle.**

**Separation.** THE POINT OF THE CONCEPT. Paper fixed L15, aperture fixed
L229-247, so the CTA carries an internal delta 214 that never changes. By day the
paper is a delta 26-91 dark figure and the aperture a delta 183-188 light one; at
night the paper is delta 0-5 (it merges with the sky — intentional; the paper
dissolves and only the light remains) and the aperture delta 208-213. **At no
phase does either step fall below delta 180 for the CTA itself.** Most
technically bulletproof answer to the brief's hardest constraint.

**Construction.** Figure/ground inversion; everything is a void. One black sheet
covers y~290-640. **Its top edge is cut as a shan-shui skyline** — layered ridge
profiles and ruyi cloud scrolls — so the paper's own upper boundary is the
composition's most beautiful line rather than a rectangle. Below START, three
small circular apertures (window-lattice roundels, r=22) for the secondaries,
each with its icon retained as paper inside the light: same construction at a
ninth of the area and a dimmer light plane (`light` at alpha 190, no hot centre).
**Hierarchy by aperture size and lamp brightness — a lighting hierarchy, not a
colour one.** BEST in a narrow slot-cut above START. PROFILE a lobed aperture at
the sheet's upper-left corner.

**Pip.** Pip flies in the open sky above the paper's cut top edge, and the
skyline is shaped so a cut ruyi-cloud scroll rises to meet him at exactly
x~60-125 — **the paper's cloud IS his cloud, in silhouette**, directly under his
bbox at y292. He appears to be flying over paper mountains. His fixed position
dictates where the cloud-cut goes, so nothing looks worked around.

**Delight.** The light behind the paper flickers gently like a lamp; all five
apertures breathe slightly out of phase. On tap, START's aperture blooms out to
fill the screen and the paper burns away into the game.

**Cross-screen.** Breaks the `dim` family completely — the CTA has no pigment.
But it offers the CLEANEST propagation: TAP TO GAME and PLAY AGAIN become the
same aperture treatment on their existing dark scrim, which they already draw.
Arguably the EASIEST of the four departures to carry across all three CTAs.

---

## Designer's picks
1. **`ridge-cut`** — only concept that SOLVES the hardest constraint by
   construction rather than managing it; furthest from anything rejected (not
   themed-foreign: paper-cut ridges and ruyi scrolls are this game's shape
   vocabulary; cannot be "too much like in-game" because it is that shape
   language rendered as ABSENCE). Answers "what colour is START" with "warm
   lantern light, not pigment" — a real professional answer, not a dodge.
2. **`jade-seal`** — most literal satisfaction of the ask; safest bet on craft
   because the lacquer-and-gilt case leans on `store_design`'s shipped
   `frame_double_bevel` and rim-shine stacks, so round 1 starts at a high floor.
3. **`silk-noren`** — best composition; only purely proportional CTA/secondary
   hierarchy, which is what top-grossing menus actually do; brings motion.
   Risk: amber sits near the title's gold, dark-type CTA is unconventional.

`cinnabar-gate` is the low-risk hedge — zero cross-screen consequence, keeps the
CTA/title kinship — but most exposed to "too close to what we have."
`cloisonne-gong` has the boldest silhouette and best Pip solution, but blue is
the largest palette leap and the A-frame most risks reading as world scenery.
