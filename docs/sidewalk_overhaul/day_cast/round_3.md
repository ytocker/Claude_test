# Day cast — round 3 (VARIETY EXPANSION)

**Sheet:** `docs/sidewalk_overhaul/day_cast/round_3.png` (1300×2762)
**Generator:** `tools/_day_cast_round3.py` (scratch copies of the three drawers; `game/` untouched)

Kids **6 → 10**, elders **6 → 10**, vendors **7 → 10** — each family lands at ten *after*
two nominated retires. 17 new rows, 6 new pose/stance branches, 6 retires.

---

## 1. New pose/stance branches (one or more per family)

### KIDS — `tiptoe`
Heels off the deck, legs dead straight, **both** arms thrown up over a counter edge, with a
slow stretch cycle. A tall thin exclamation mark — the inverse of every crouched or running
kid in the pool.

```python
elif tiptoe:
    stretch = 0.5 + 0.5 * math.sin(t * 1.9)
    body_y = ground - int(total * 0.46) - body_h - int(stretch)
    ...
    for sgn in (-1, 1):                       # straight legs, heels lifted
        lx = cx + sgn * body_w * 0.45
        pygame.draw.line(surf, pants, (lx, body_bot), (lx, ground - 1), 2)
        pygame.draw.line(surf, _shade(pants, -22), (lx - 1, ground - 1), (lx + 1, ground), 1)
    for sgn, off in ((-1, 0.0), (1, 0.35)):   # both arms up over the counter
        pygame.draw.line(surf, skin, (cx + sgn * body_w * 0.5, body_y + 1),
                         (cx + sgn * body_w * 0.9 - body_w * 0.5,
                          hy - head_r * (1.5 + off * 0.4)), 2)
```

### ELDERS — `brush` and `reading`
* **`brush`** (water calligraphy): bent deep over a long brush whose tip **touches the deck
  ahead of the feet** — the only elder whose silhouette reaches the ground away from the
  body. Wet strokes left behind dry (fade) on a slow cycle.
* **`reading`**: an open scroll held wide on both hands — a hard horizontal bar across the
  chest. The one elder read that *widens* the figure instead of extending it. (Widened this
  round to `body_w*2.1` half-width after measuring it too close to the kept rows: max IoU
  vs kept elders dropped 0.81 → 0.74.)

```python
elif brush:
    tip_x = cx - body_w * 2.9 + math.sin(t * 1.5) * body_w * 0.5
    pygame.draw.line(surf, bcol, (hxb, hyb), (tip_x, ground - 1), max(1, body_w // 5))
    for k, wx in enumerate((cx - body_w * 3.4, cx - body_w * 2.2)):   # drying strokes
        fade = 0.4 + 0.4 * math.sin(t * 1.1 + k)
        pygame.draw.line(surf, _mix(wet, (140, 130, 112), fade), (wx, ground),
                         (wx + body_w * 0.8, ground), 1)

elif reading:
    sw2 = int(body_w * 2.1);  sy2 = int(arm_y + torso_h * 0.26)
    r = pygame.Rect(cx - sw2, sy2 - 1, sw2 * 2, max(4, int(torso_h * 0.38)))
    pygame.draw.rect(surf, sc, r);  pygame.draw.rect(surf, _shade(sc, -46), r, 1)
```

### VENDORS — `chop`, `pour`, `wok`
All upper-body, because vendors read chest-up behind a counter.

* **`chop`** — 2-beat cleaver: the arm swings from **above the head** down to the board, so
  the figure's topmost point moves half a head between frames (the loudest motion cue in
  the family).
* **`pour`** — long-spout pot held high beside the head with a hairline thread of tea
  falling into a cup: a tall arm plus a vertical line.
* **`wok`** — both hands on a **wide tilted pan held away from the body**, food arcing above
  it. The only vendor whose outline is a broad horizontal ellipse.

```python
elif pose == "chop":
    beat = max(0.0, math.sin(t * 5.0))
    hyc = arm_y + torso_h * 0.30 - beat * head_r * 3.2      # above the head at the top
    blade = pygame.Rect(hxc - body_w * 0.9, hyc - 1, max(3, int(body_w * 0.9)), max(2, head_r))
    pygame.draw.rect(surf, bl, blade);  pygame.draw.rect(surf, _shade(bl, -50), blade, 1)
    # + a cutting board on the counter line
```

---

## 2. The 17 new rows

**KIDS (6):** K7 tiptoe peek *(new stance)* · K8 kite runner *(uses the drawer's `kite`
branch that **no shipped row ever selected** — free variety from existing code)* ·
K9 ribbon dancer *(new acc `ribbon` — a wavy streamer twice the child's width; new hair
`sidetails`, which widens the head at the **jaw** where buns widen it on top)* ·
K10 lantern on a stick *(new acc `lantern`, carried **forward** at chest height so it can
never double the balloon row's overhead sphere)* · K11 satchel runner *(new acc `satchel`:
a boxy bag squared onto the back — a rectangle among round kids)* · K12 squat + sidetails
*(second squat, younger, different head shape)*.

**ELDERS (6):** E7 water calligrapher *(new stance)* · E8 scroll reader *(new stance)* ·
E9 sword form *(new acc `sword`: taichi stance plus one hard straight edge continuing past
the hand, with a swinging tassel)* · E10 herb gatherer *(new acc `back_basket` — the day
cast carried nothing behind the body before)* · E11 seated + fan *(slim/bald seated mass to
contrast E5's padded/cap/teacup)* · E12 padded upright + tea *(the padded winter mass on its
feet; E5's padding only ever appeared sitting)*.

**VENDORS (5):** V8 cleaver chop *(new pose)* · V9 long-spout tea pour *(new pose)* ·
V10 wok toss *(new pose)* · V11 weighing (heavy) *(V2's action at the opposite end of the
build range, under a cloth hat)* · V12 cloth-bolt stacker (lean/tall, bare-headed, pale
bolts instead of baskets).

E9 / E11 / E12 / V11 / V12 are deliberately **within-branch** rows (the brief's
"rest as palette/accessory rows") and measure 0.70–0.82 IoU against their base branch;
the six new-branch rows measure 0.55–0.74 against the kept pool.

---

## 3. Retire nominations (2 per family)

| Row | Why |
|---|---|
| **K1 toddler run** | Its only note is being small — no prop, no stance break. Next to K3/K12 it is an anonymous blob, and K8/K9/K11 now carry the running read *with* outline events. |
| **K5 candy + cap** | The tanghulu is three 2 px dots that vanish in the far lane, leaving the pool's plainest standing body. |
| **E1 stoop + cane** | A straight duplicate of `ped_cast`'s `A_STOOP` cane elders — the adult pool already walks four of this exact construction down the same street. |
| **E4 hands-behind** | An upright robe with both arms tucked behind it: zero outline breakers, the plainest figure in the day cast. |
| **V1 calling** | The whole action is one short arm to the mouth; cropped at the counter it is an apron torso with no outline event. |
| **V6 skewers** | Four 1 px skewers dissolve in the far lane, and it shares `pose:sign` with V7 — it reads as the sign vendor minus the sign. |

If the AD would rather keep K1's toddler proportion, the next weakest kid is **K6
piggyback**, which draws its own crude adult stand-in inside the kid drawer (a second,
divergent adult construction to maintain).

---

## 4. Night-cap audit (measured, not asserted)

All **30** shipping rows × 3 motion phases rendered onto the night deck, scanning the
**rendered** pixels:

```
hottest day-cast px luma = 135   ·   px over 150 = 0   ·   gold-coin core = 230
PASS — every day-cast px sits under the cap.
```

Every new hot-ish accent (lantern glass, tea thread, cleaver steel, sword blade, wok food,
scroll paper, cloth bolts) goes through `_knock` and/or `_cap_luma` exactly like the round-2
price board and balloon.

---

## 5. Open questions for the art director

1. Vendors gained three new actions in one round — is `wok` one too many next to `ladle`
   (both two-handed and low), or does the wide pan earn its place?
2. K10's lantern is knocked to a warm accent; at festival beats should it be allowed a
   slightly hotter core (still ≤150) so it reads as *lit*?
3. E12 puts the padded mass upright — do we want padded elders at all outside the snow
   weather bucket, or should that row be weather-gated?
