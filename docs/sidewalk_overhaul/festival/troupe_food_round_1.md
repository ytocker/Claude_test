# FIRE-TREE NIGHT — round 1 · THE MONKEY KING'S TROUPE + FOOD THEATRE

**Sheet:** `docs/sidewalk_overhaul/festival/troupe_food_round_1.png` (1500 × 1897)
**Generator:** `tools/_festival_troupe_round1.py` (scratch; touches no `game/` file)
**Covers:** FESTIVAL_PLAN.md §4 (the third act), §5 (crowd behaviours) and
build-list rows **A9 A10 A11 A12 A14**.

Panels are literal screen slices — world y 500 → 647 at 1×, with the far deck
(595), the near deck (638) and the **560 cast/prop band ceiling** drawn in as
blue dashes. Nothing on this sheet is allowed above 560; the fire sheet's spark
FX is the plan's one sanctioned exception.

---

## 1. A9 · The Monkey King's troupe

### Why masked humans, restated because it is the whole justification

耍猴 street monkey performance is in steep decline (Xinye County trainers ~10,000
→ ~300), is legally unprotected, and is actively contested on welfare grounds. A
costumed macaque on a leash would read to a modern casual audience as *sad*, not
charming — the one beat in the whole day the player would feel bad about. It also
fails the festival's razor outright: **a monkey on a chain looks down.**

Three masked acrobats as Sun Wukong are a temple-fair staple alongside stilts,
yangge and lion dance, and a direct sibling of the shipped bian-lian
mask-changer, so the family already exists in the codebase's idiom.

### The mask — the entire act's read at 22 px

Gold face, red-brown fur ruff, **two long swept phoenix plumes off the brow**,
a red brow band and two dark eye slits. The plumes are the silhouette event: no
other head in the game has two long curved antennae, so the troupe is
identifiable from outline alone, at any of the three beats, on any of the three
figures. The plumes lag the body on the spin and the somersault, which is where
most of the act's motion actually lives.

Team uniform: a diagonal **red-and-yellow sash** dealt identically to all three,
so the trio reads as one troupe while the three poses stay unrelated.

### Three beats, three shape languages — the distinct-variants rule applied

The rule is applied to **shape language, not to costume**. These are not one pose
re-dressed:

| Beat | Shape event | Measured envelope | Construction |
|---|---|---|---|
| **1 · Staff spin** (2.0 s) | **WIDE HORIZONTAL lens** | 22 × 32 px | A 20 px bar at 3 Hz cannot read as a rotating stick at this pixel size, so it is drawn as the swept **blur arc** plus the instantaneous bar and two trailing samples, with two gold cuffs on the Ruyi Jingu Bang. Legs wide, feet planted. |
| **2 · Shoulder tower** (2.4 s) | **TALL VERTICAL column** | 30 × 44 px | Two-high, the tallest human shape in the festival, locked on a gong hit. The **third acrobat climbs the base's left side**, so the column is crossed by one diagonal limb — the detail that stops it reading as one very tall person. |
| **3 · Dismount somersault** (1.5 s) | **ROUND, AIRBORNE ball** | 21 × 25 px, **off the ground** | A tucked ball rolling across the front of the ring with a visible gap of paving under it and a compressed shadow keeping it anchored. **Nothing else in the cast is ever off the ground**, so this beat is unmistakable in a single frame. |

The sheet also shows the routine as one 6-phase loop, and the mask at 6×.

Ring of 5 spectators on the near deck, turned inward, desynced clapping.

---

## 2. A10 · The paper monkey mask — the payoff

In the two blocks after the square, **~1 kid in 3 wears one**. They bought it. It
is the only visible cause-and-effect on the street all day, and it costs one
accessory sprite hung off the head circle `day_cast.draw_kid` already computes
(`head_r ≈ 34 % of total`, `total = KID_H × (0.62 + 0.38·age)`), so the overlay
needs no new anatomy.

Two states, and they had to differ in **outline**, not just position, or at 10 px
they are the same blob:

- **WORN** — the mask covers the head circle entirely, so the child's own
  features vanish. That *absence* is the read: a smooth gold disc where a face
  should be.
- **PUSHED UP** — the same sprite 4 px higher with a dangling chin strap, giving
  a **two-lobed head** (mask above, hair below) and the kid's face showing
  beneath.

The plumes read on both. Kids point rather than wave inside the window, so the
sheet shows both states with and without the point.

---

## 3. A11 · Food theatre — three overlays, not three new stalls

All three keep the shipped `food_stalls` metrics (`HALF_W` 22, counter at
base−15, post top at base−34) and add nothing above the awning, so they drop onto
the existing shell without re-deriving anatomy or disturbing the awning
colour-pair deck. The awning pairs are **bamboo/cream (noodle) · rust/cream
(sugar) · indigo/cream (tanghulu)**, so the three theatre stalls are also three
different colour-pairs in a row.

The thesis of density crest #2 is that the market gets **more interesting as it
gets slightly less crowded** — and it does that by making three stalls perform.
The queues form at these three, because people queue for the show, not the food.

- **A11a NOODLE-PULLER.** Arms thrown **wide** with the dough strung between them
  — the widest arm span on the street. The ribbon doubles **1 → 2 → 4 → 8** on a
  4-step 0.9 s cycle, each fold tighter and higher than the last, with a
  slap-puff of flour on folds 2 and 4. The dough is thrown **up** on every fold,
  so the beat obeys the razor. All four steps are on the sheet.
- **A11b SUGAR-PAINTER.** Seated, leaning in, a wand over a pale 10 px stone
  slab, an amber thread falling onto it, resolving into a finished disc on a
  stick. **The pour is the one downward motion of the entire night**, which is
  exactly why it earns its contrast against every rising thing around it. Three
  phases on the sheet. The act sits down specifically to buy the vertical budget
  the lifted disc needs.
- **A11c TANGHULU RACK.** Research: skewers are displayed bristling off a
  straw/foam **pole**. That gives the stall row a spiky, radially symmetric
  outline it does not otherwise contain — **a new shape, not a new colour**. Ten
  skewers × three beads. Pole height is set *by* the band ceiling, not by taste:
  the cap ellipse lands on exactly 560 and the splay is tuned so no bead crosses
  it either.

---

## 4. A12 · Walk-and-eat props ×4

The festival's **dominant** crowd behaviour: night-market seating is sparse, so
supper is a grazing stroll rather than a seated effort. `reach_up` retargets to
**chest height** and the four items hang off that one hand; gait is dialled −15 %.

At 14 px a held object gets roughly 4 × 5 px. That is enough for exactly one
silhouette idea each, so the four were chosen to be **orthogonal**:

| Prop | Shape event | Note |
|---|---|---|
| **skewer** | horizontal **BAR** | 3 dark meat blocks on a 1 px stick |
| **steam bun** | pale **DOME** | pinched crown + one steam wisp; the only round item |
| **tanghulu** | vertical **STACK** | 3 red beads; deliberately the hottest of the four (capped 120) — the plan calls it the brightest non-gold object in the flood beat, and it still sits ~110 luma under the coin |
| **cup** | squat **BLOCK** + steam | lid line, tapered body |

Put any two side by side in a crowd and they are still distinguishable; put the
same two in the same colour and they still are. The sheet proves all four at
**14 px near-deck figures and again on 18 px far-deck adults**.

---

## 5. A14 · The vendor step-out — the market pause

§4 calls this *"the single most important beat in the plan."* For the ten seconds
the dragon occupies the block, every stall goes non-working: the vendor comes out
from **behind** the counter to **beside** it, faces the parade, and puts a hand
up. Steam thins **3 wisps → 1**. Calls stop. The market withdraws its own
signature and gives it back when the tail passes.

The sheet shows working / stepped-out at day and at night. The read is not
primarily the pose — it is the **change in mass**: behind the counter the vendor
is a half-figure (the counter owns the lower body, only head and one calling arm
clear it); stepped out, **a whole figure appears where there was half of one**.
That registers before the raised arm does.

---

## 6. Measured night-cap + band audit — **PASS**

Measured on **rendered pixels of label-free panels** across every pose and phase
on this sheet.

| Metric | Value |
|---|---|
| **Hottest pixel on this sheet** | **132.8** luma |
| Pixels over the 150 cap | **0** |
| Gold coin core | **229.5** luma — sole brightest, **73 % hotter** |
| **Highest pixel any NEW piece reached** | **y 560** — exactly on the band ceiling, 0 px over |
| Needs the spark exception? | No |

**Per-piece hottest (night = 0.95):**

```
M.spin        119   M.tower       119   M.somersault  119
A11.noodle    133   A11.sugar     122   A11.tanghulu  130
A12.walk+eat  131   A10.kid mask  119
A14.working   132   A14.step-out  124
```

**Per-piece topmost NEW pixel (world y):**

```
A11.noodle 560   A11.sugar 560   A11.tanghulu 560
A14.working 565  A14.step-out 575
M.spin 609       M.tower 596     M.somersault 615
A12.walk-and-eat 620             A10.kid mask 613
```

### On how the band number is measured

For the pieces that sit on the shipped `food_stalls` shell (A11, A14), the band
figure is the topmost pixel that **differs from a bare shell** — i.e. what *this
round* adds — not the topmost pixel in the panel. The shipped shell itself
already tops out at **y 555** (its awning crossbar) and its steam column climbs
past that; both are unchanged by these overlays. A14's figure extent is measured
on the vendor alone for the same reason: this pose *thins* the stall's steam, it
never adds to it, so folding steam into the vendor's band number would be
measuring someone else's art.

Three pieces (noodle, sugar, tanghulu) land at exactly 560 because their heights
were **set by the ceiling** — the tanghulu pole and the sugar-painter's seated
stance are both consequences of the budget, not decorated afterwards.

---

## 7. Deliberately not done in round 1

- No live-animal monkey act (§4).
- No text, no HUD marker, no cheer sting, no confetti.
- Stilt-walkers are untouched: §4 retargets the existing act A3 from a square act
  to a travelling one, which is **pure placement and zero new art**.


---

## ROUND 2 REVISION (art-director punch list, verified on rendered pixels)

7. Beat 1 is now genuinely WIDE: staff sweep over a crouched acrobat ->
   envelope 36x29 (aspect 0.81) vs tower 30x43 (1.43) vs somersault 20x33.
   Pairwise silhouette IoU: spin|tower 0.346, spin|somersault 0.250,
   tower|somersault 0.179 — all under the 0.35 distinctness bar.
8. Theatre overlays freed to the SHIPPED apparatus budget (steamer already
   tops at y518): tanghulu is a freestanding pole at the stall edge topping
   y546 — the spiky ball finally clears the y555 awning crossbar and reads as
   a silhouette; the noodle dough breaks the awning line on folds 2 and 4
   (tops y518); the sugar-painter stays low (y560) — the downward beat.
6. Troupe spectator ring rescaled to 31px near-lane height.
12. "Tallest human shape" claim corrected (the shipped stilt-walker is 52px;
    the tower's distinguishing feature is its WIDTH and the climber diagonal).

AUDIT (round 2): hottest 132.4, 0 px over cap; theatre overlays top y518
(= shipped steamer, no new maximum), cast figures top y565 (inside the 560
band rule's intent: topmost FIGURE pixel 565 <= band with the 5px brush of
the step-out's raised arm — measured, stated); coin sole-brightest.
