# Street animals — round 3 (VARIETY EXPANSION)

**Sheet:** `docs/sidewalk_overhaul/animals/round_3.png` (1240×3363)
**Generator:** `tools/_animals_round3.py` (scratch copy of the drawers; `game/` untouched)

Dogs **5 → 9** (4 new + 2 re-dressed toward stray), critters **4 → 7**.
Dog frequency was already cut separately, so each sighting now has to be a rarer, fresher
look — the pool has to read as a village street, not as five pets on a loop.

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
`ear` gains **`halfflop`**, `muzzle` gains **`flat`**, plus three attrs — **`scruffy`**,
**`mane`**, **`skirtcoat`**.

```python
elif tail == "streetlow":          # hangs almost straight DOWN off the rump
    pygame.draw.lines(surf, tcol, False, [
        (tx - 1, body_cy + 1), (tx + int(sh_h * 0.22), body_cy + int(sh_h * 0.45)),
        (tx + int(sh_h * 0.14) + sway, body_cy + int(sh_h * 0.85))], max(2, sh_h // 6))

if scruffy:                        # RAGGED edge: tufts standing off the back line
    for k, bxp in enumerate(range(body_left + 2, body_right - 1, 3)):
        up = 1 + (k % 2)
        pygame.draw.line(surf, coat_dk, (bxp, body_top + 1), (bxp - 1, body_top - up), 1)
    # + a torn hip and a broken shoulder line

elif ear == "halfflop":            # one up, one folded — the pool's first ASYMMETRIC head
    pygame.draw.polygon(surf, coat_dk, [...prick...])
    pygame.draw.polygon(surf, _shade(coat_dk, -14), [...folded tip...])

if mane:                           # ruff drawn BEHIND the head so the head sits inside it
    mr = max(3, int(head_r * 1.5))
    pygame.draw.circle(surf, _mix(coat, belly, 0.35), (hx + head_r // 2, hy + 1), mr)
    for k in range(8):             # 8 shaggy spikes on the rim
        ...

if skirtcoat:                      # fringed coat to the deck; the legs disappear
    skirt = [(body_right, body_top + body_h // 2)] + zigzag_hem + [(body_left, ...)]
    pygame.draw.polygon(surf, coat, skirt)
```

### Two shipped breeds re-dressed toward stray

* **D1 hound** — coat dulled `(176,150,110) → (150,130,100)`, `tail:low → streetlow`,
  `scruffy` on. Same proportions, now a street dog.
* **D3 spitz** — cream `(214,208,196) → (184,178,164)` dusty, `tail:plume → sickle`
  (carried lower/looser), `scruffy` on. Still fluffy, no longer groomed. (Bonus: the duller
  coat also buys night-cap headroom.)

D2 dash (the height benchmark), D4 shiba and D5 long-ear pup are untouched — D4 is
deliberately left as the one clearly *owned* dog on the street.

### Passed over

* **Spotted village dog** — spots are interior colour and vanish in the far lane; round 2
  cut a spotted mutt for exactly this reason.

### Measured checks

Height (must stay under an adult, PED_H 18; D2 dash is the ceiling at 18):

```
D1 17  D2 18  D3 16  D4 18  D5 15  D6 17  D7 17  D8 17  D9 16
```

(D8 was 20 px on the first pass — the mane was pushing it to adult height; build 1.0 → 0.86,
head 1.0 → 0.95, mane radius 1.7 → 1.5 `head_r` brought it back to 17.)

Silhouette IoU, each new dog against its nearest neighbour in the pool: D6 0.68 (vs D5),
D7 0.66 (vs D5), D8 0.71 (vs D3), D9 0.58 (vs D8) — in the same band as the shipped pool's
own spread, with D9 the most distinct thing in the family.

---

## 2. Critters — three new kinds

Picked for maximum silhouette separation from the sitting cat / pecking hen / pigeon clump /
waddling duck, and from each other:

| Row | Silhouette | 2-beat motion |
|---|---|---|
| **C5 CRANE** | The only **vertical** critter: stilt legs + long S-neck + spear bill, ~2× the duck's height (13 px), dark trailing plumes | neck folds down to preen then unfurls; one leg lifts on the slow half of the cycle |
| **C6 PIGLET** | The **widest-for-its-height** shape: a low tube (19×9) on four stubby legs, blunt snout disc, curl tail | roots the snout down into the deck and lifts; tail flicks off-beat |
| **C7 RABBIT** | A compact ball under **two outsized upright ears**, bright scut behind | nibbling head bob; one ear twitches back on a slower cycle |

**Goose was passed over deliberately:** at 6–10 px a goose is a duck with a longer neck —
the same size-only read that got the sparrows cut in round 2. The crane takes the
long-necked slot instead because its stilt legs make it a different *shape*, not a different
*size*. (Sparrow pair: still cut, nothing has changed at this scale.)

Critter IoU vs the shipped four: crane **0.11–0.31** (completely separate), rabbit
0.30–0.51, piglet 0.33–0.58 (its closest neighbour is the pigeon clump, which is three
separated blobs against the piglet's one solid tube plus snout and curl).

---

## 3. Night-cap audit (measured, not asserted)

All 9 dogs + 7 critters × 3 motion phases rendered onto the night deck; scan over the
**rendered** pixels:

```
hottest ANIMAL px luma = 144   ·   px over 150 = 0   ·   gold-coin core = 230
PASS — all animal px <= cap.
```

Both new pale coats (crane body 188,186,178 and lion-dog 178,156,118) ride the existing
pale-coat second pull in `_retint`, and every derived highlight goes through `_hi`, so
nothing drifts over 150 at any gait phase.

---

## 4. Open questions for the art director

1. Nine dogs may be more than the (now rarer) dog slot can show — should the pool be nine
   with weighting that favours the strays, or trimmed to eight by cutting D5?
2. The lion-dog's skirt coat hides its legs entirely, so it slides rather than walks. Add a
   1 px hem wobble on the gait, or is the loaf-glide the charm?
3. The piglet has no obvious owner on the street yet — should it be beat-gated to
   BEAT_MARKET only (arriving with the produce), rather than appearing at dusk?
