# STAR PIÑATA — Round 3

Secret flyer concept, `docs/pinata/star/`. Round 2 verdict was ITERATE: the
silhouette, palette, parcel clearance, de-faced vertical lens, night glow and
cream keyline all landed (all KEPT), but the #1 fix — a true 7-point star with
one apex straight up — did not. A tip-count on the round-2 render found EIGHT
tips with the top two straddling vertical.

## Punch list status

### 1. BLOCKER — true 7-point star, one apex straight up — FIXED

Root cause was NOT the spoke loop count (it already emitted 7 spokes at
`-90° + i·(360/7)`). The bug was the **flat-capped spike tip**: each cone ended
in a blunt trapezoid whose two corners sat ±2.4 px either side of the spoke
axis. At the apex spoke (pointing straight up) those two corners landed at
roughly −101° and −80° — reading as two tips straddling vertical, i.e. the
phantom "8th point / top notch."

Fix: the cone now converges to a **single point** (a true triangle `base-L →
tip → base-R`, no flat cap), with the cream fringe pom centred dead-on the
point. The apex therefore resolves to ONE tip on the vertical axis. The apex
spoke is also grown (`APEX_SPIKE_SCALE = 1.15`, the canvas ceiling at `BCY=30`)
so the up-point is the single longest tip.

**Rendered tip count (measured on the build surface, not the notes):**

```
RENDERED SPIKE TIP COUNT: 7
  reaches sorted (deg, r):
    (-90.0, 30.5)   <-- LONGEST / APEX, straight up
    (218.6, 30.0)
    (167.1, 29.2)
    ( -38.6, 28.7)
    (  12.9, 28.2)
    ( 115.7, 24.9)   <-- splayed bottom pair (shortened)
    (  64.3, 24.2)   <-- splayed bottom pair (shortened)
  any spike straight down? NO
```

Seven tips. The single longest tip is the apex at −90° (straight up). With 7
odd points and the apex up, the bottom resolves to a splayed PAIR (64° and
116°, shortened by `BOTTOM_SPIKE_SCALE`) straddling the vertical — there is no
spike pointing straight down. Confirmed visually in the 3x reference and the
grayscale strip: one tall apex up, a splayed gold/teal pair at the bottom.

### 2. Monotonic, evenly-spaced 4-step crack value swing — FIXED

Round 2's value read dark→bright→mid→bright, collapsing stages 2 and 4 to the
same gray (~3 perceptible steps). The lens brightness was derived from the
non-monotonic crack-width curve, so two stages landed on the same value.

Fix: the lens VALUE is now decoupled from the crack WIDTH. A dedicated
`_LENS_VAL_BY_STAGE = (0.00, 0.34, 1.00, 0.50)` drives the interior luminance
directly. Measured mean luma of the lens region across the four poses:

```
stage 0  luma =  69.6   (sealed dark seam)
stage 1  luma = 140.4   (delta +70.8 — distinctly dim lens)
stage 2  luma = 228.6   (delta +88.1 — white-hot peak)
stage 3  luma = 197.2   (delta -31.4 — a clearly DIFFERENT mid)
```

Four distinct beats: dark → dim → brightest → mid. Stage 3 (197) sits clearly
between stage 1 (140) and stage 2 (228), a 57-point gap from the dim stage, so
they no longer collapse. The grayscale strip in `round_3.png` reads as four
separate value steps.

### 3. Optional — night bloom peak alpha pulled back ~10% — DONE

The additive glow's peak alpha dropped from `190·crack + 36` to
`170·lens_val + 30` (~10% lower peak), and its alpha now tracks `lens_val` so
the brightest beat blooms most. The extra falloff reach is kept (same ellipse
radii), so the seam stays the night focal anchor without bleeding over the
white lens edge at 40px.

## KEEP items — all preserved

Cream fringe keyline; magenta/gold/teal day-safe candy palette; parcel
clearance (`BCY = 30` + `BOTTOM_SPIKE_SCALE`); the de-faced vertical-diamond
candy lens; the night glow as focal anchor. No parcel is drawn by this build —
it is supplied by the staged gameplay frame.

## Verdict artifact

`round_3.png` — the DAY and NIGHT gameplay frames at play-size (~40px) both read
as the non-creature spiky star party-ball: a dominant magenta apex straight up,
the radial ring clearing Pip's parcel below, the candy lens glowing as the
focal seam (night especially). The reference column confirms 7 points and the
4-beat grayscale crack swing.
