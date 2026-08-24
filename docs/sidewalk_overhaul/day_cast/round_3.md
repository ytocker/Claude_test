# Day cast — round 3 (VARIETY EXPANSION)

**Sheet:** `docs/sidewalk_overhaul/day_cast/round_3.png` (1300×2776)
**Generator:** `tools/_day_cast_round3.py` (scratch copies of the three drawers; `game/` untouched)

Kids **6 → 10**, elders **6 → 10**, vendors **7 → 10** — each family lands at ten *after*
its retires. **16 new rows, 6 new pose/stance branches, 6 retires.**

> **Revised after the art director's round-3 critique.** Fixed this pass: K7's cycle that
> animated zero pixels, the vendor roster (V1 the caller stays, V12 goes), the kite string,
> E12's weather gate, and every motion claim in these notes is now a measured number.

---

## 1. New pose/stance branches (one or more per family)

### KIDS — `tiptoe`

**FIX — the stretch cycle moved nothing.** `stretch` is `0.5 + 0.5*sin(t)`, i.e. a float in
[0, 1]; `int(stretch)` is **0** everywhere except the single instant it hits exactly 1.0, so
the row rendered identically at every phase. The reach is now driven off the float, and
raised so the figure stacks between the squat and the kite:

```python
stretch = 0.5 + 0.5 * math.sin(t * 1.9)
body_y = ground - int(total * 0.46) - body_h - int(round(stretch))   # heels lift
for sgn, off in ((-1, 0.12), (1, 0.0)):
    tip_y = hy - head_r * (2.15 + off + 0.70 * stretch)               # the REACH animates
    pygame.draw.line(surf, skin, (cx + sgn * body_w * 0.5, body_y + 1),
                     (cx + sgn * body_w * 0.85 - body_w * 0.35, tip_y), 2)
```

Measured over 30 phases (rendered alpha, native size):

| Row | silhouette height | top-of-silhouette travel |
|---|---|---|
| K3 squat play | 14 px | 0 |
| **K7 tiptoe (before)** | **15 px** | **0 px — dead cycle** |
| **K7 tiptoe (after)** | **17–20 px** | **3 px per beat** |
| K8 kite runner | 21 px | 0 |

So the tiptoe kid now reads clearly taller than the squat rows and stays under the kite
runner's ceiling, and the top of the silhouette visibly pumps.

**Three more cycles were dead the same way** and are fixed with `round()` instead of
`int()`: the vendor `fan` flutter (`int(sin(t*6)*1)`), the elder `cane` tap
(`int(sin(t*1.3))`) and the kid `sidetails` swing (`int(gait*0.8)`). Measured px changing
per cycle after the fix: fan 16, herb-gatherer cane 21, side-tails 59 — all previously 0.

### ELDERS — `brush` and `reading`
* **`brush`** (water calligraphy): bent deep over a long brush whose tip **touches the deck
  ahead of the feet** — the only elder whose silhouette reaches the ground away from the
  body. Wet strokes left behind dry (fade) on a slow cycle. 26 px change per cycle.
* **`reading`**: an open scroll held wide on both hands — a hard horizontal bar across the
  chest. The one elder read that *widens* the figure instead of extending it. Static.

### VENDORS — `chop`, `pour`, `wok`
All upper-body, because vendors read chest-up behind a counter.

* **`chop`** — 2-beat cleaver, raised hand down to the board.
* **`pour`** — long-spout pot held high beside the head with a hairline thread of tea.
* **`wok`** — both hands on a **wide tilted pan held away from the body**, food arcing above
  it. The only vendor whose outline is a broad horizontal ellipse.

**Corrected motion claim.** Round 3 said chop moves "the topmost point half a head between
frames". Measured, it is **one pixel**. What chop *is* the leader in is total motion:

| Vendor | px changing over the cycle (native / FAR 0.78×) | top-edge travel |
|---|---|---|
| **V8 chop** | **71 / 45** | 1 px |
| V10 wok | 64 / 40 | 1 px |
| V9 pour | 47 / 27 | 0 px |
| V3 fan | 16 / — | 0 px |
| V1, V2, V4, V5, V7, V11 | **0** — identical at every phase | 0 px |

Honest phrasing: *chop is the most motion in the family by a clear margin, and its top edge
travels one pixel.* Six of the ten vendors do not move at all, which is a separate question
worth answering before integration (see §5).

---

## 2. The 16 new rows

**KIDS (6):** K7 tiptoe peek *(new stance)* · K8 kite runner *(uses the drawer's `kite`
branch that **no shipped row ever selected**; the string is now **2 px** — at 1 px the crisp
far-lane downscale erased it and the kite detached into a floating lozenge. Measured: 1
island at all 8 phases at 0.78×)* · K9 ribbon dancer *(new acc `ribbon`; new hair
`sidetails`, now actually swinging)* · K10 lantern on a stick *(new acc `lantern`, carried
**forward** at chest height so it can never double the balloon row's overhead sphere)* ·
K11 satchel runner *(new acc `satchel`)* · K12 squat + sidetails.

**ELDERS (6):** E7 water calligrapher *(new stance)* · E8 scroll reader *(new stance)* ·
E9 sword form *(new acc `sword`)* · E10 herb gatherer *(new acc `back_basket`)* ·
E11 seated + fan · **E12 padded upright + tea — now marked `[SNOW-GATED]`** in its row data:
snow-only weights, zero elsewhere, so a padded winter mass can never turn up on a warm
market day. (Carried from the round-1 note; integration will honour it.)

**VENDORS (4):** V8 cleaver chop *(new pose)* · V9 long-spout tea pour *(new pose)* ·
V10 wok toss *(new pose)* · V11 weighing (heavy) *(V2's action at the opposite end of the
build range, under a cloth hat — 0.75 max-IoU, its nearest neighbour is V3, not V2)*.

### Vendor roster amendment

**V1 calling is KEPT** — it is the pool's only hawking vendor, and a market needs a voice.
**V12 cloth-bolt stacker is CUT** — measured 0.82 IoU vs V5 (the director's harness read
0.87), the worst new row of the round: the same `stack` branch with the same three stacked
ellipses on a leaner body.

That arithmetic lands vendors at ten without inventing anything: **6 kept (V1–V5, V7) + 4
new (V8–V11)**. No tenth action was invented, per the brief's "otherwise vendors land at 10
including V1".

Family max-IoU after the swap (FAR 0.78×), worst pair in each:

```
KIDS     K9 ↔ K11  0.70
ELDERS   E9 ↔ E2   0.84   (sword vs fan on the same taichi stance — the family's tightest pair)
VENDORS  V3 ↔ V11  0.75   (was V5 ↔ V12 at 0.82)
```

---

## 3. Retire nominations (2 per family)

| Row | Why |
|---|---|
| **K1 toddler run** | Its only note is being small — no prop, no stance break. K8/K9/K11 now carry the running read *with* outline events. |
| **K5 candy + cap** | The tanghulu is three 2 px dots that vanish in the far lane, leaving the pool's plainest standing body. |
| **E1 stoop + cane** | A straight duplicate of `ped_cast`'s `A_STOOP` cane elders — the adult pool already walks four of this exact construction down the same street. |
| **E4 hands-behind** | An upright robe with both arms tucked behind it: zero outline breakers. |
| **V6 skewers** | Four 1 px skewers dissolve in the far lane, and it shares `pose:sign` with V7 — it reads as the sign vendor minus the sign. |
| **V12 cloth-bolt stacker** | 0.82 IoU vs V5: the same stack branch and the same stacked ellipses, re-dressed lean. |

---

## 4. Audits (measured, not asserted)

**Motion** — rendered alpha, 40 phases; printed in the sheet footer. See the vendor table
in §1 and the kid table above.

**Night cap** — all 30 shipping rows × 3 motion phases on the night deck:

```
hottest day-cast px luma = 135   ·   px over 150 = 0   ·   gold-coin core = 230
PASS — every day-cast px sits under the cap.
```

Every hot-ish accent (lantern glass, tea thread, cleaver steel, sword blade, wok food,
scroll paper) goes through `_knock` and/or `_cap_luma` exactly like the round-2 price board
and balloon.

---

## 5. Open questions for the art director

1. Six of the ten vendors render identically at every phase. Worth a cheap universal idle
   (a 1 px shoulder bob on a slow per-row phase offset), or does stillness behind a counter
   read as intended?
2. E9 ↔ E2 is the day cast's tightest remaining pair at 0.84 — sword and fan on the same
   taichi stance. Re-stance the sword row, or accept it as the family's one near-twin?
3. K10's lantern is knocked to a warm accent; at festival beats should it be allowed a
   slightly hotter core (still ≤150) so it reads as *lit*?
