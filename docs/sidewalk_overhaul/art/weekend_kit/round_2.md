# Weekend Street Kit — Round 2

**Sheet:** `docs/sidewalk_overhaul/art/weekend_kit/round_2.png` (1900 × 1916, 509 KB)
**Draft code:** `tools/_weekend_kit_round2.py`
**Run:** `SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/_weekend_kit_round2.py`
**Verify:** `SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/_weekend_kit_round2.py --measure`
**Critique addressed:** `docs/sidewalk_overhaul/art/weekend_kit/critique_1.md` (VERDICT: ITERATE, 14-item punch list)

No file under `game/` was touched. Round 1's drawers are imported live
(`tools/_weekend_kit_round1.py`), so every before/after cell on the sheet and every
R1 number below comes from the actual code the critique measured — not from memory.

---

## The premise correction, measured and adopted

The critique's headline was that this round rested on a false premise about the
backdrop. Reproduced here off real frames (`biome.palette_for_phase` →
`draw.get_sky_surface_biome` → `draw.draw_mountains` →
`foreground.draw_foreground_floor` → `draw_ground_weather`):

| phase | FAR band (y 577–594) | NEAR band (y 620–638) |
|---|---:|---:|
| day 0.06 | **228.3** | 156.2 |
| dusk 0.54 | 169.1 | 59.5 |
| storm 0.63 | **173.2** | 56.2 |
| snow 0.87 | 211.6 | 107.0 |
| sunrise 0.94 | 225.2 | 161.5 |

Far-lane figures are silhouetted against **light** at every hour; the near lane is
the reverse. Every value decision this round is made against that, and **every 1×
context strip on the sheet now shows the piece in both lanes** — far deck
`GROUND_Y` 595 and near deck 638, the latter rendered the way
`foreground_near_lane._scaled_cast` does it (scratch deck → NEAREST footprint
scale → 6% dim → feet on 638). Each strip carries a red lane tick + label.

---

## 1 · `suoyi` — own `arch` key

Punch-list items **1, 2, 4, 7, 8, 14** + critique §3 notes 3 and 7.

| critique item | what changed |
|---|---|
| **1. Give it a head** | Brim lifted 2px clear of the crown (`lift=2` on `_conical_hat`) and the cape shoulder dropped to `torso_top + 1`. The neck notch was pulled up to `sh_y − 1` and narrowed to 3px so it shades the throat instead of eating the jaw. |
| **2. Kill the 1px checkerboard** | `straw_hi` is out of the interior entirely. Three **horizontal** bands: a 2px shoulder catch-light, the body tone, and a `straw_mid` band across the bottom third, broken by two short dark seams. The fringe comb is now uniform `straw_dk` with the tooth read carried by **length** (1–2px, `2 if i % 3 else 1`) instead of by alternating colour. |
| **3. Focal hierarchy inverted** | The hat's lit cone slope is now the figure's brightest pixel; the cape's catch-light sits one step under it. |
| **4. Retint to warm-dark** | `_straw` mixes toward **(58, 46, 38) at 0.52** (was (54,64,96) at 0.34), over a base tan re-pitched to (150,132,84). |
| **7. `cape_h` 10→8, fringe 1–2px** | `cape_h = 7` — 8 would have put the hem back at y+4 once the shoulder dropped 2px for the face. The stated goal (hem at ~y+6, 5–6px of stride) is hit exactly. |
| **8. Crate primary, pole secondary** | `carry` defaults to `"crate"`. The pole is pulled to **±8** (was ±10), raised to `sh_y − 3`, and its bundles shrunk to 5×4 so they hang **above** the hem. |
| **14. `brim_w = head_r * 3`** | Done. |
| **§3.7 own `arch` key** | Adopted — it changes torso shape, hem line, leg exposure and carry constraint at once. Authored as its own drawer; in integration it is `A_SUOYI` in `ped_cast`, not an accessory flag. |

### Measured — storm frame, contrast against the pixels each figure replaces

```
R2 crate (primary)     n= 198  mean|dL|=  97.3   piece mean L= 66.2   max L= 138.1
R2 pole  (secondary)   n= 250  mean|dL|=  88.7   piece mean L= 70.7   max L= 138.1
R1 pole                n= 269  mean|dL|=  66.8   piece mean L= 95.0
SHIPPED pole vendor    n= 225  mean|dL|=  88.3   piece mean L= 72.7
SHIPPED umbrella ped   n= 158  mean|dL|=  80.6   piece mean L= 68.8
```

**Target mean|ΔL| ≥ 85: hit on both carries** (97.3 / 88.7 vs the shipped pole
vendor's 88.3). R1 was 66.8 — the least contrasty figure on the storm street.

### Measured — value bands and hue channel at night = 1.0

```
catch-light     (119,104, 75)  L 105.2   R-B +44
body            (102, 87, 60)  L  88.4   R-B +42   <- target band L 85-95
mid             ( 93, 78, 53)  L  79.6   R-B +40
fringe/outline  ( 80, 66, 44)  L  67.7   R-B +36
hat lit cone    (159,135, 99)  L 138.1   R-B +60   <- brightest pixel on the figure
shipped ochre   (100, 92, 87)  L  93.8   R-B +13   <- the warmest shipped coat
```

Cape body **L 88.4**, inside the requested 85–95. Interior values are **8.8 luma
apart** (body → mid), well inside the ≤22 ceiling, and there is no vertical
alternation left to crawl under a 160px/s scroll. Hue channel holds: R−B +36…+44
against the warmest shipped coat's +13.

### Measured — geometry

```
face rows visible (full skin tone): 2   at y+17, y+16   (R1: 0)
brim span 13px over a 9px shoulder row
fringe bottom y+5;  5 stride rows below it
```

### Measured — both lanes

```
NEAR lane (feet 638, storm deck L 56.2)
  R2 crate             mean|dL| 15.1   piece mean L 66.2
  R1 pole              mean|dL| 38.2   piece mean L 95.0
  SHIPPED pole vendor  mean|dL| 15.7   piece mean L 72.7
```

Reported straight: R1's brighter straw did read *harder* in the near lane. The
round-2 suoyi instead sits **exactly with the shipped cast there** (15.1 vs 15.7)
— it is no worse than every figure that lane already contains — and in the near
lane its separation is carried by the hue channel (R−B +42 vs cloth's +13), which
is the same channel the critique credited as the real reason to keep the warmth.

---

## 2 · `winter` overlay set

Punch-list items **6, 9** + critique §5 notes 3 and 5.

| critique item | what changed |
|---|---|
| **9. Coat hem 2–3px below `torso_bot`** | Hem drops **3px**, ends **square** (`border_top_left_radius`/`border_top_right_radius` only, so the top corners keep their padded roll), with a 1px `c_hi` hem band over a 1px dark lip. |
| **9. Stitch bands 3→2** | Bands at 0.30 / 0.62 (was 0.26 / 0.50 / 0.74). |
| **§5.3 face rows** | Cap raised onto the crown (`hy − head_r*2`, height `head_r*1.5`) with a 1px fur line at its bottom edge; collar dropped from `neck_y − 1` to `neck_y` and thinned 4px → 3px. |
| **6. Breath puffs** | Peak α **150** (was 109); spawned at `hx, hy` — **on** the dark cap/collar — then drifting clear at 9px/life; 1px cool-dark rim (58,74,104) at 0.8× the core alpha, cached on the same (radius, 16-step alpha) key as `_snow_flake`; radius **1 → 3 → 1**, peaking at f≈0.25 and shrinking into the fade (was growing as it died). Dog puff raised to peak α 132 and moved to the muzzle. |
| **§5.5(a) scarf latching** | **Latched at slot entry, no exception.** A scarf that morphed mid-traversal would be the only thing on this street visibly changing state while you watch it. STREAM/DRAPE is picked once from the entry storm value and held. |
| **§5.5(b) `cold` scalar** | Agreed — a single `cold` scalar exposed from `biome`, not derived locally in the promenade. Flagged for integration; not a drawing change. |

### Measured — max IoU vs all 50 shipped pedestrian variants

```
R1 coat DRAPE    0.866      R2 coat DRAPE    0.734      (both vs shipped #17)
R1 coat STREAM   0.740      R2 coat STREAM   0.664
```

**DRAPE 0.866 → 0.734**, STREAM 0.740 → 0.664. (My harness measures R1's DRAPE at
0.866 where the critique measured 0.839 — a small alignment-box difference; the
delta is what matters and it is −0.132 on the same harness.)

### Measured — face rows

```
R1: 0 skin rows      R2: 2 skin rows (+ a third skin-shadow row)
```

### Measured — breath puff, drawn on the figure then drifting onto the 211-luma snow band

```
life f=0.02   n=16   mean|dL| vs what it covers = 25.3   puff mean L 116.7
life f=0.16   n=32   mean|dL|                   = 20.5   puff mean L 120.3
life f=0.42   n=32   mean|dL|                   = 13.1   puff mean L 142.8
life f=0.70   n=12   mean|dL|                   =  4.7   puff mean L 187.2
R1, at spawn, in open air beside the head:  n=4   mean|dL| = 13.8
```

The puff now has **25.3 luma of separation at spawn against 13.8** — and it gets
it by being born on the dark hat rather than by being brighter than a 211-luma
sky. It also covers 16px at spawn where R1 covered 4. It fades into the band by
f≈0.7, which is the intent: contrast where it matters, gone before it can smear.

---

## 3 · 6-rib umbrella — rebuilt

Punch-list item **3** / critique §6.

- **6 ribs** (was 8). At r=8 that is ~2.8px of panel at the hem instead of 2.1
  and 0.
- **Base colour dominant.** Only **two** wedges (1 and 4) take the −20 step;
  four stay base. Two shaded panels flanking a lit centre is also how a
  wind-tilted dome actually takes light.
- **Shaded wedges stop 14% short of the hem**, so the scalloped bottom edge stays
  base and the canopy doesn't go bottom-heavy.
- **4 rib lines, on alternate boundaries only** — the four boundaries of the two
  shaded wedges, so a crease always lands *on* an existing value edge and never
  crosses a panel's interior (which is what erased the panels last round). Each
  runs only over the **outer 45%** of the radius; the inner 55% is where a radial
  fan converges into a blot.
- Hem scallops, 2px finial + spike, and the `crooked` kid variant unchanged.

### Measured — canopy pixel census (night 0, scale 1.0, wind 0.4; the pole excluded)

| idx | shipped mean | R1 mean / base% | **R2 mean / base%** |
|---|---:|---:|---:|
| 0 red | 89.4 | 85.0 / 13.1% | **95.3 / 42.3%** |
| 1 blue | 89.0 | 84.6 / 13.1% | **94.9 / 42.3%** |
| 2 gold | 149.7 | 150.6 / 13.1% | **160.9 / 42.3%** |
| 3 green | 107.7 | 104.9 / 13.1% | **115.2 / 42.3%** |
| 4 violet | 101.4 | 98.1 / 13.1% | **108.4 / 42.3%** |

**Mean luma ≥ shipped on all five colours** (+4.7 to +11.2), and **base colour is
42.3% of canopy pixels**, over the ≥40% target and up from 13.1%. Canopy area is
130px vs the shipped 112 — the +27% the critique flagged is down to +16%, and it
is now brighter rather than muddier.

---

## 4 · `_cart_folded`

Punch-list items **10, 11** / critique §2.

| critique item | what changed |
|---|---|
| **10a. LOADED's load floats** | Pole bundle, rolled awning, binding band and crate all drop 2px onto the bed line. |
| **10b. Kill the wheel spin** | Option (a) taken: `spin` is fixed at 0 in every state. The parameter survives for a future in-transit pose with a real derived `v/r`. |
| **§2.3. Hub is the brightest pixel** | Hub dropped to `_shade(wood, −10)`; the cart's one bright value moves to the **bed's top edge**. |
| **11. HALF** | Bed to `bl=8, br=−6` — **28.3°** over the 26px bed. Raised handle rebuilt as a **2px shaft with its own dark keyline** (mass, not a hairline), shortened to `x1+6`. Basket attached to the **low end of the bed**. |
| **§2.5. Pure prop** | Kept a pure prop; the scene composes the vendor. HALF's vendor lifting the raised handle is the integration note. |
| **EMPTY unchanged** | Silhouette **IoU 1.000** vs round 1 — pixel-identical mask. It inherits only the two cart-wide value fixes (hub tone, bed top edge), which the critique listed as cart-level notes rather than LOADED-only ones. |

### Measured

```
loaded  envelope 36 x 23   max L 134.9     (R1: 36 x 25, max L 154.2)
half    envelope 36 x 27   max L 142.2     (R1: 41 x 24, max L 154.2)
empty   envelope 37 x 17   max L 150.0     (R1: 37 x 17, max L 154.2, silhouette IoU 1.000)
```

HALF's envelope comes back from **41px to 36px** — the same width as the in-transit
cart, i.e. the basket no longer inflates it at all. (36 is the floor for any state:
the bed is 26px and the handle accounts for the other 10 in all three.) The cart's
brightest pixel drops **154.2 → 134.9** on LOADED and now sits on the bed.

---

## 5 · `_stall_tarp`

Punch-list item **12** / critique §1. Everything the critique called ship-ready —
pitch direction, rope turns, guy line, shadow cave, seated arms-folded vendor,
steam + brazier, and the `_clamp_surface_luma` routing — is untouched.

1. **4px sheet with a hard 3-band ramp:** 1px `tarp_hi` top edge / 2px `tarp` body
   / 1px `_shade(tarp, −40)` underside. The lit line and the dark outline no
   longer sit on top of each other, and the low corner gets a real edge against
   the paving it slopes toward.
2. **Runoff tapers.** Dash height 3px → 2px → 1px with falling phase, and alpha
   sheds 30% over the fall (`255 → 179`), so the thread accelerates instead of
   reading as a dashed line. Blitted per-dash on a 1px SRCALPHA strip, which works
   identically on both build targets.
3. **One sheet for all five stall kinds.** Answered as directed. The tarp geometry
   is byte-identical regardless of `kind`; only the cook-top under it varies
   (steamer basket stack / wok / pot). The sheet shows the same tarp over two
   kinds side by side, plus three tarped stalls in the far lane of the strip.

### Measured — composite under a 229.5 coin

```
storm  piece mean L  88.4   max L 145.8      <- the night contract, unchanged from R1
day    piece mean L 107.8   max L 201.8      <- day; the cap is a night contract
```

145.8 under the 146 ceiling, same as round 1 — the extra sheet row and the alpha
dashes both go through the same clamp.

---

## 6 · `_sweeper`

Punch-list items **5, 13** + critique §4 notes 2 and 5.

| critique item | what changed |
|---|---|
| **13. Wrong body idiom** | Rebuilt on **`ped_cast._draw_one`** (`A_TUNIC`, `stoop=0.16`, `acc=('sweep',)`) — a standing figure at full cast scale. The seated `_draw_bench_person` idiom is gone. In integration the besom block lives inside `_draw_one` next to `A_POLE`. |
| **5. Pile too bright** | Pile body **L 201.0 → 143.9**, pile shade L 113.9, against a sunrise deck mean of 160.2. The `_shade(pale, +10)` crest line is **deleted outright**. |
| **§4.2. Pile eating the broom** | Pile moved left and narrowed: besom fan now spans x[−14, +4] and the pile x[−20, −12]. The value relationship is also inverted — the fan's bright twig (L 157.5) is now **brighter** than the pile (143.9), where in R1 the pile (201/211) drew last and brighter over a 118/171 fan. |
| **13. Stroke too small/slow** | Cycle **1.8s → 1.3s**; measured broom-head travel **10px** over one cycle (was ~6). Plus a **1px vertical body bob** on the push half. |
| **§4.5. Slot budget** | **Guaranteed slot**, like the storm holdouts. One per two blocks from 363s is too thin to leave to a personality budget when he *is* the beat that says 6 a.m. |

### Measured

```
R2 pile body (142,144,148)  L 143.9        target band 130-145
R2 pile shade               L 113.9
R1 pile body (198,202,204)  L 201.0
sunrise deck mean (600-639) L 160.2

sweeper own opaque max L 164.1   (skin; well under the 229.5 coin)
broom-head travel over one 1.3s cycle: 10px
besom fan x[-14, +4]   pile x[-20, -12]
```

One note in passing: the dust puff at full extension is now **tinted** (168,158,140)
rather than white. A white particle over a 225-luma sunrise deck *brightens* it —
the composite hit 234 in R1, above the coin. Tinted, the puff composites **darker**
than the paving it lifted off (232.2 → 229.3 on the hottest pixel), which is also
what swept grit actually looks like. The sunrise sidewalk itself peaks at 234.9
before anything is drawn on it; that is a shipped-street property, and this kit no
longer adds to it.

---

## Sheet contents

Every row: thesis + a per-item change list on the left, 3×/6× nearest-neighbour
zoom cells in the middle (never smoothscaled), and a 1× real-game-frame strip on
the right showing **both lanes**, with the gold coin as the brightness yardstick.

Rows 1, 2, 3, 4 and 6 each carry a live **ROUND 1 cell** beside the round-2 one, so
the before/after is on the same sheet at the same zoom.
