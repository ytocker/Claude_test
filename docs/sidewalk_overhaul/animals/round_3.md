# Street animals — round 3 (VARIETY EXPANSION)

**Sheet:** `docs/sidewalk_overhaul/animals/round_3.png` (1240×3377)
**Generator:** `tools/_animals_round3.py` (scratch copy of the drawers; `game/` untouched)

Dogs **5 → 9** (4 new + 2 re-dressed toward stray), critters **4 → 7**.
Dog frequency was already cut separately, so each sighting now has to be a rarer, fresher
look — the pool has to read as a village street, not as five pets on a loop.

> **Revised after the art director's round-3 critique.** Fixed this pass: D3 read as a
> dimmer D3, D6's distinctness claim was resting on a sub-pixel ear, D9's coat slid like a
> dropped sack, the rabbit was too close to the cat, and the ragged-stray edge was being
> erased by the far-lane downscale.

---

## 1. Dogs — four new looks

Research shaped the shape language: free-ranging village/pariah dogs are spitz-ish (wedge
head, pointed muzzle, erect ears, tail carried curled over the back **or** hanging free) and
come in every size and colour — so the give-away of a street dog is the **ragged outline**,
never the coat.

| Row | Look | Construction (all data rows on the parametric drawer) |
|---|---|---|
| **D6** | scruffy **STRAY** | `scruffy` + `ear:halfflop` + `tail:streetlow`, ribby dust-grey, build 0.92 / chest 0.86 |
| **D7** | lean **STREET MUTT** | `tail:sickle`, leg 1.30 (tallest legs), chest **0.72** (shallowest in the pool), fine head, long muzzle |
| **D8** | **CHOW-type** | `mane` + `tail:tightcurl` + `muzzle:short`, build 0.86 / leg 0.70 / chest 1.22 |
| **D9** | **LION-DOG** | `skirtcoat` + `muzzle:flat` + `tail:plume`, build 0.72 / leg 0.45 — smallest, roundest thing in the cast |

New outline enums (everything else is data): `tail` gains **`sickle`** and **`streetlow`**,
`ear` gains **`halfflop`**, `muzzle` gains **`flat`**, plus four attrs — **`scruffy`**,
**`ruffcrop`** (new this pass), **`mane`**, **`skirtcoat`**.

### FIX — the ragged edge was being erased at far-lane scale

`scruffy` tufts were 1 px: the first thing a nearest downscale throws away. Measured as the
IoU of a scruffy dog against the same dog with `scruffy=False`, at FAR 0.78× (lower = the
raggedness actually registers):

| Row | 1 px tufts | 2 px tufts |
|---|---|---|
| D1 | 0.94 | **0.91** |
| D3 | 0.97 | **0.94** |
| D6 | 0.95 | **0.91** |

### FIX — D3 was "a dimmer D3"

Re-dressing the spitz with a duller coat and a lower tail changed **19 %** of its outline
(0.81 IoU against the shipped spitz) — colour did the rest of the work, and colour dies
first. It now carries a second outline event, a new `ruffcrop` attr:

```python
if ruffcrop:
    # A stray's ruff wears away unevenly — thick over the withers, rubbed back
    # to the skin on the throat side. The flat-bottomed, back-heavy collar is an
    # ASYMMETRIC outline event.
    rr = max(3, int(head_r * 1.35))
    collar = [(rx - rr * 0.55, ry - rr * 0.85), (rx + rr * 0.85, ry - rr * 0.75),
              (rx + rr * 0.75, ry + rr * 0.25), (rx - rr * 0.15, ry + rr * 0.35),
              (rx - rr * 0.95, ry - rr * 0.05)]
    pygame.draw.polygon(surf, _mix(coat, belly, 0.30), collar)
    ...three 2px standing tufts on the upper rim
```

```
D3 vs the SHIPPED spitz outline:   0.81  →  0.74
D3 max-IoU inside the pool:        0.71  →  0.73 (vs D8)
```

The small rise against D8 is the cost of any ruff; 0.73 is inside the pool's normal band
(D4 ↔ D5 also measure 0.73) and D8 still owns the full mane disc, the tight curl tail and
the short legs.

### CORRECTED — what actually makes D6 the stray

Round 3 sold D6 on "the pool's first asymmetric head". Measured, the half-flopped ear is
**sub-pixel** at this size:

```
D6 with halfflop  vs  D6 with a plain prick ear   =  0.97 IoU   (native AND at 0.78x)
D6 with streetlow vs  D6 with a sabre tail        =  0.89 IoU
D6 ragged         vs  D6 smooth-backed (FAR)      =  0.91 IoU
```

So D6's read is the **tail hung straight down, the dust-grey coat and the broken back
line**. The ear is a 4× zoom bonus and is now described as one — in the row note, the
module docstring and the sheet.

### FIX — D9's coat was a dropped sack

The `skirtcoat` hem was a static zigzag, so a legless dog slid along the deck. The zigzag
now flips phase with the gait:

```python
# The fringe alternates phase with the stride: without it a legless coat slides
# along like a dropped sack instead of walking under its own fur.
wob = 1 if gait > 0 else 0
skirt.append((xx, hem - ((k + wob) % 2)))
```

```
D9 px changing along the bottom 3 rows per cycle:  0  →  21
```

### Two shipped breeds re-dressed toward stray

* **D1 hound** — coat dulled `(176,150,110) → (150,130,100)`, `tail:low → streetlow`,
  `scruffy` on (now 2 px).
* **D3 spitz** — dusty coat, `tail:plume → sickle`, `scruffy` + the new `ruffcrop`.

D2 dash (the height benchmark), D4 shiba and D5 long-ear pup are untouched — D4 is
deliberately left as the one clearly *owned* dog on the street.

### Measured checks

Height (must stay under an adult, PED_H 18; D2 dash is the ceiling at 18):

```
D1 17  D2 18  D3 16  D4 18  D5 15  D6 17  D7 17  D8 17  D9 16
```

Silhouette max-IoU inside the pool: D1 0.66 · D2 0.63 · D3 0.73 · D4 0.73 · D5 0.73 ·
D6 0.68 · D7 0.66 · D8 0.73 · **D9 0.58** (the most distinct thing in the family).

---

## 2. Critters — three new kinds

| Row | Silhouette | 2-beat motion |
|---|---|---|
| **C5 CRANE** | The only **vertical** critter: stilt legs + long S-neck + spear bill, ~2× the duck's height (13 px), dark trailing plumes | neck folds down to preen then unfurls; one leg lifts on the slow half of the cycle |
| **C6 PIGLET** | The **widest-for-its-height** shape: a low tube on four stubby legs, blunt snout disc, curl tail | roots the snout down into the deck and lifts; tail flicks off-beat |
| **C7 RABBIT** | A compact ball under **two outsized upright ears**, bright scut behind | nibbling head bob; one ear twitches back on a slower cycle |

**FIX — the rabbit was too close to the cat.** The ears are the only thing separating the
two silhouettes, so they gained 1 px of length and 1 px of gap:

```
C7 rabbit vs C1 cat:   0.51  →  0.45      (identical at native and at 0.78x)
```

**C6 PIGLET is now marked `[BEAT-GATED: BEAT_MARKET only]`** in its row data note — it
arrives with the produce and must not turn up at dusk with nobody to own it. (Carried from
the round-1 note; integration will honour it.)

**Goose was passed over deliberately:** at 6–10 px a goose is a duck with a longer neck —
the same size-only read that got the sparrows cut in round 2. The crane takes the
long-necked slot instead because its stilt legs make it a different *shape*, not a different
*size*. **Spotted village dog** was passed over too: spots are interior colour and vanish in
the far lane, exactly why round 2 cut a spotted mutt.

---

## 3. Audits (measured on rendered pixels, not asserted)

**Outline** (printed in the sheet footer):

```
D3 vs shipped spitz      = 0.74   (tail swap alone was 0.81 — 'a dimmer D3')
D6 ragged vs smooth FAR  = 0.91   (1px tufts measured 0.95 — the downscale erased them)
D6 streetlow vs sabre    = 0.89   ·   D6 halfflop vs prick = 0.97  (SUB-PIXEL — not the read)
D9 hem px moving/cycle   = 21     (was 0)
rabbit vs cat            = 0.45   (was 0.51)
```

**Night cap** — all 9 dogs + 7 critters × 3 motion phases on the night deck:

```
hottest ANIMAL px luma = 144   ·   px over 150 = 0   ·   gold-coin core = 230
PASS — all animal px <= cap.
```

The new `ruffcrop` collar is mixed from the already-cooled `coat`/`belly`, so it inherits
the pale-coat second pull in `_retint` and cannot drift over the cap.

---

## 4. Open questions for the art director

1. Nine dogs may be more than the (now rarer) dog slot can show — nine with weighting that
   favours the strays, or trim to eight by cutting D5?
2. D3's cropped ruff pushes it from 0.71 to 0.73 against the chow. Keep the full collar, or
   shrink it to `head_r*1.2` (0.72 vs D8, but only 0.76 vs the shipped spitz)?
3. The half-flop ear is honest 4× detail that costs nothing — keep it as a zoom reward, or
   drop it so the enum list stays small?
