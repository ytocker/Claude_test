# Pedestrians — round 3 (VARIETY EXPANSION)

**Sheet:** `docs/sidewalk_overhaul/pedestrians/round_3.png` (1400×3230)
**Generator:** `tools/ped_explore_round3.py` (scratch copy of the pool + drawer; `game/` untouched)

Pool **50 → 57**: 3 new archetypes, 13 new rows, 6 rows retired.

> **Revised after the art director's round-3 critique.** Fixed this pass: the rod's
> far-lane fragmentation, the CUT-list amendments (#39 keeps its place, #38 goes),
> the shawl matron and the ear-flap snow row, and the deck contrast on the gleaner.
> Every number below is measured on rendered alpha, not asserted.

---

## 1. Three new archetypes

Chosen from the candidate list for one reason each: they add a *kind of outline event*
the pool does not own yet. Every existing accessory is horizontal (pole, yoke), overhead
and round (parasol, head tray), or hip-level (basket, cane, bundle).

| Key | Who | The outline event it adds |
|---|---|---|
| `A_ROD` | **Fisherman** — belted tunic, chest strap, creel on the back hip | A long springy **diagonal** running from the front hand up over the head to a tip ~8 px above the crown, with a hanging catch on a thread. The pool had no steep diagonal at all. |
| `A_BARROW` | **Handcart porter** — pitched-forward body, two shafts, load box, spoked wheel | A **vehicle on the deck**: the only cast member whose mass sits at ground level rather than on the shoulders. Doubles the footprint low down; the wheel *rolls* with `t`. |
| `A_PIPA` | **Strolling musician** — pear lute across the chest, neck past the far shoulder | A **bulge on the body edge plus a short spar clearing the head**, with two skin dots on opposite ends of it (fretting hand + plucking hand) — "playing", not "carrying". |

**Passed over, with reasons** (so the call can be overruled):

* **Alms-bowl monk** — a bare-headed narrow robe with a bowl at the waist *is* `A_ROBE` at
  14 px; the bowl is interior detail and dies first. It would be a palette variant wearing
  a story.
* **Water-carrier with front-slung jars** — two hung loads on a bar is exactly what
  `A_POLE` and `A_YOKE` already are. A third re-dress of one idea.

### FIX 1 — the rod was breaking the figure into islands

A 1 px rod does not survive the crisp far-lane downscale: nearest-neighbour drops whole
rows, the outer half of the spar disappears and the tip becomes a floating splinter.
Measured on rendered alpha at 0.78×, worst of 8 gait phases:

| Row | islands at `max(1, body_w // 7)` | islands at `max(2, body_w // 6)` |
|---|---|---|
| N1 ochre fisher | **2** (76 px body + a 22 px detached tip) | **1** |
| N2 teal young fisher | **2** | **1** |
| N3 slate old fisher | **3** (79 + 8 + 2 px) | **1** |

```python
# A 1px rod is destroyed by the crisp far-lane downscale — the outer half drops
# out and the tip becomes a floating splinter. Two pixels is the minimum that
# survives a nearest 0.78x and keeps the figure ONE island.
pygame.draw.lines(surf, rod_c, False, [hand, mid, tip], max(2, body_w // 6))
```

```python
# A_BARROW — cart AHEAD of the body; body pitched via the existing stoop scalar.
wx = cx + body_w * 3.1 + lean;  wr = max(2, int(leg_h * 0.85));  wy = ground - wr
for off in (0, 1):                                    # two shafts back to the hands
    pygame.draw.line(surf, wood, (cx + body_w * 1.5 + lean, hand_y + off),
                     (wx - wr * 0.4, wy - wr * 0.2 + off), max(1, body_w // 8))
# load box on the frame, then hub + 3 spokes rotated by t*4.0 so the wheel turns
```

```python
# A_PIPA — pear body + neck that CLEARS the crown (a spar stopping at the
# shoulder just reads as a bulky sleeve).
neck_top = (bx - body_w * 1.15, hy - head_r * 2.1)
pygame.draw.line(surf, wood_dk, (bx, by - bhei * 0.35), neck_top, max(2, body_w // 5))
```

### Outline-distinctness check (max-IoU of the alpha mask at FAR 0.78×; lower = more distinct)

Against the **whole final pool**, each new row's nearest neighbour:

```
N1 0.66 (N3)   N2 0.71 (#12)  N3 0.66 (N1)   N4 0.79 (N5)   N5 0.79 (N4)
N6 0.72 (N4)   N7 0.75 (N8)   N8 0.75 (N7)   N9 0.82 (#1)   N10 0.72 (#6)
N11 0.75 (#22) N12 0.75 (#11) N13 0.70 (#31)
```

Every new row is below 0.85. The shipped pool's own twins measure **1.00** (see §3).

---

## 2. The 13 new rows

8 in the new archetypes (3 fishermen, 3 barrows, 2 pipa players), 5 re-dressing existing
archetypes with genuinely new headwear / carry positions rather than new hues:

| Row | Archetype | What is new |
|---|---|---|
| N1 ochre fisher | `A_ROD` | conical hat, catch on the line |
| N2 teal young fisher | `A_ROD` | short/slim, bare-headed, no catch — a lighter frame under the same spar |
| N3 slate old fisher | `A_ROD` | stoop 0.16 + beard: the rod tips shallower over a bent back |
| N4 clay barrow | `A_BARROW` | stoop 0.20, hurried |
| N5 olive tall barrow | `A_BARROW` | taller + deeper pitch, cloth head-wrap |
| N6 stone barrow | `A_BARROW` | strolling, shallow pitch, pale sacked load, conical hat |
| N7 mauve pipa | `A_PIPA` | bun + hairpin, slim |
| N8 indigo pipa | `A_PIPA` | bald, bearded, stooped over the instrument |
| N9 flat-brim official | `A_ROBE` | **new hat `flatbrim`** (hard horizontal disc) + **new acc `scroll`** |
| N10 shawl matron | `A_SKIRT` | **new hat `shawl`** — now a full asymmetric drape to a hanging point below the elbow (see FIX 2) |
| N11 back-basket gleaner | `A_STOOP` | **new acc `back_basket`** — tall pannier riding high on the BACK; coat half a step darker (see FIX 3) |
| N12 back-bundle traveller | `A_TUNIC` | **new acc `back_bundle`** — bedroll hump + chest strap |
| N13 ear-flap snow | `A_PADDED` | **new hat `earflap`**, flaps flared at ear level and one swinging; carried load moved to the BACK \[SNOW\] |

### FIX 2 — N10 and N13 were re-dresses, not new reads

**N10 shawl matron** measured **0.93 IoU vs #6**: the head-cloth stopped at the collar,
and at that height the skirt's own A-line is already as wide as the cloth, so the drape
changed almost nothing. It now falls asymmetrically — thrown over one shoulder, gathered
under the carrying arm, out past the A-line on the left and down to a **hanging point
below the elbow that swings with the stride**.

```python
hem_y = arm_y + torso_h * 0.62
tip_y = hem_y + torso_h * 0.62 + gait * 1.4
pts = [(cx - body_w * 2.05, hem_y),
       (cx - body_w * 1.05, torso_top), ...crown...,
       (cx + body_w * 0.95, torso_top + 1), (cx + body_w * 1.05, hem_y - 1),
       (cx - body_w * 0.25, hem_y + 1), (cx - body_w * 0.85, tip_y),
       (cx - body_w * 1.45, hem_y + 1)]
```

**N13 ear-flap snow** measured 0.83–0.88 and, worse, its two "outline events" were both
*interior*: the flaps hung below the jaw where the padded coat is already wider than the
head, and the `bundle` accessory (which #17 and #21 also wear) draws entirely inside the
coat rectangle. Both moved outward — the flaps now **flare at ear level**, which is the
narrowest part of a padded figure, with the leading one swinging on the gait; the load
moved to `back_bundle`.

| Row | before | after | now nearest to |
|---|---|---|---|
| N10 | 0.93 vs #6 | **0.72** vs #6 | #6 |
| N13 | 0.83 vs #17 | **0.70** (0.67 vs #17) | #31 (a yoke porter — no longer a padded row at all) |

Motion, measured over 8 phases: N10 moves 22 native / 14 far-lane px per cycle,
N13 moves 34 native / 23 far-lane px. Neither was animated before.

### FIX 3 (optional item) — the gleaner was sinking into the deck

Shared `sage` on a sunlit deck is nearly the deck's own luma. N11 was the lowest-contrast
row in the pool; it now carries its own half-step-darker coat `(110,134,112) →
(84,104,86)`.

```
N11 mean |ΔL| vs the deck:  18.9  →  24.8      (pool median 35.1)
lowest rows now: #9 20.3 · #27 20.8 · #7 21.5  (all shipped, none new)
```

---

## 3. CUT list — 6 retires (AMENDED)

The director's read was right and the measurement backs it: at FAR 0.78× the shipped pool
contains **five pairs/triplets that render an identical mask** (IoU 1.00). Those are the
real waste, not the rows that merely share a family.

| # | Row | Measured |
|---|---|---|
| #5 | Robe · slate tall scholar | 0.92 max-IoU vs #2 — a third bun-and-topknot stroll |
| #13 | Tunic · ochre laborer | **1.00 vs #11** |
| #15 | Tunic · rust porter | **1.00 vs #11** |
| #30 | Pole · olive cloth | **1.00 vs #27** |
| #35 | Yoke · olive | **1.00 vs #31/#32** (the 1.00 triplet member) |
| #38 | Headload · indigo | **1.00 vs #36** |

**Amendments from round 3's nomination:**

* **#39 Headload · ochre box is KEPT.** It measures **0.83 max-IoU** — the *most distinct*
  row in the head-tray band. The redundancy there is the twin pair **#36 ↔ #38 at 1.00**,
  so **#38** goes instead.
* **#10 Skirt · stone basket is KEPT** — 0.79 max-IoU, clear of the twin band.
* The sixth cut is taken from a 1.00 group: **#35**, the yoke triplet member the director
  named as a runner-up.

**Runners-up, listed honestly** (still in the pool only because the agreed cut depth is six):

| # | Measured |
|---|---|
| #26 | 0.94 vs #27 — the near-twin the pole family keeps once #30 goes |
| #2 / #4 | 1.00 twin pair (robe, bun, stroll; hairpin vs beard is interior) |
| #12 / #16 | 1.00 twin pair (hurry tunic youth) |
| #37 / #40 | 1.00 twin pair (head tray) |
| #31 / #32 | 1.00 twin pair (yoke) |

Cutting one from each of those four remaining pairs would take the pool to 53 with **no**
loss of construction. That is a deeper trim than agreed, so it is offered, not taken.

---

## 4. Audits (measured on rendered pixels, not asserted)

**Outline** — all 8 gait phases, FAR 0.78×:

```
N1 islands = 1   N2 islands = 1   N3 islands = 1      (were 2 / 2 / 3)
N10 max-IoU 0.72 vs #6            N13 max-IoU 0.70 vs #31
PASS — one island each, and both redrawn rows sit under 0.85.
```

**Night cap** — all 57 final rows × 3 gait phases on the night deck:

```
hottest pedestrian px luma = 135   ·   px over 150 = 0   ·   gold-coin core = 230
PASS — every pedestrian px sits under the cap.
```

The scratch drawer applies the **animals_cast-style second pull** on any night colour still
over 150 (`_cap_night`). `game/ped_cast.py` currently has only the generic cool; the
measurement passes either way today, but the new pale roles (ear-flap fur, pale sacked
load, scroll paper) are exactly the sort of thing that would drift over the cap later, so
folding the guard into `ped_cast._retint_person` at integration is recommended.

---

## 5. Open questions for the art director

1. Cut depth: six as listed, or take the four remaining 1.00 twins as well (pool 53)?
2. The barrow is the widest cast member (~26 px incl. cart). Acceptable spacing-wise in the
   near lane, or should the cart shrink ~15 %?
3. N10's drape now covers part of the carried basket's near edge. Read as "shawl over a
   full arm", or should the basket move to the free hand?
