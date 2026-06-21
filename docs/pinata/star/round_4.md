# STAR PIÑATA — Round 4 (FINAL pass)

Secret flyer concept, `docs/pinata/star/`. Round 3 verdict carried ONE persistent
blocker: the apex spike still ended in a FLAT CAP (a plateau ~7px wide at 1x /
~21px at 3x straddling vertical), so the rendered silhouette forked at the top
and read as an 8-point star with a notch. Prior "tip count 7" claims counted the
spoke LOOP, not the rendered pixels. This round the blocker is fixed AND verified
on the rendered surface, not in the math.

## 1. KILL the flat apex cap — FIXED & VERIFIED ON PIXELS

Root cause was the cream pom: a radius-2 disc drawn **centred ON the tip** put a
4–5px flat plateau over the cone vertex, and the apex tip sat at `y≈1` (jammed
against the canvas ceiling), so the disc was clipped into the flat top the
director saw.

Two changes:
- The pom NUB is pulled BACK 2.6px along the spike axis toward the hull, so the
  cone's true single point pokes above it as the topmost pixel instead of a disc
  capping the tip. Applied to ALL SEVEN spikes — no tip forks.
- `SPIKE_LEN` pulled to 10 and `APEX_SPIKE_SCALE` set to 1.30 so the apex vertex
  lands a few px below the ceiling (headroom for a clean point) while staying the
  single longest tip.

**ACCEPTANCE TEST — topmost occupied rows of the apex spike (measured on the
rendered 1x build surface, `build(50)`):**

```
row  3  width 1   <-- first occupied row, ≤3px (a single vertex)
row  4  width 3
row  5  width 4
row  6  width 5
row  7  width 6
row  8  width 7
row  9  width 8
row 10  width 9
row 11  width 10
row 12  width 11
row 13  width 12
row 14  width 13
```

The first occupied row is **1px wide** (≤3px) and the width widens **monotonically**
downward (1 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13). No plateau, no
flat cap. The round-3 plateau (7px at 1x / 21px at 3x) is gone.

**Rendered tip count (radial-reach local-maxima scan on the rendered silhouette,
NOT the spoke loop):**

```
RENDERED TIP COUNT: 7
  tip at  12.5 deg, reach 24.0
  tip at  64.0 deg, reach 21.0   <-- splayed bottom pair
  tip at 118.0 deg, reach 21.7   <-- splayed bottom pair
  tip at 168.0 deg, reach 25.0
  tip at 216.5 deg, reach 24.0
  tip at 269.5 deg, reach 27.0   <-- APEX, straight up, SINGLE LONGEST
  tip at 319.5 deg, reach 23.3
```

Exactly **7 tips**. ONE point straight up (269.5°≈ −90°) and a splayed PAIR at the
bottom (64° / 118°) straddling the vertical — no spike points straight down.

## 3. Apex is the single LONGEST tip — CONFIRMED

The apex reach is **27.0** vs the next-longest 25.0; it is the single longest tip
in rendered pixels. No further growth was needed after the cap fix (growing it
more would re-clip the vertex against the ceiling).

## 2. Re-separated 4 crack value steps + distinct geometry per stage — FIXED

Each stage now carries a UNIQUE crack GEOMETRY (a non-value secondary cue) as
well as its own value:

- stage 0 — **sealed seam**: a thin dark vertical groove, no lens (darkest).
- stage 1 — **hairline crack**: a narrow DIM lens just parted (thin).
- stage 2 — **wide jagged gash**: a wide WHITE-HOT lens with candy spilling
  (brightest).
- stage 3 — **shattered web**: a LARGER spiderweb fracture (six radiating dark
  cracks) at a clearly LOWER value than stage 2.

Measured mean luma of the lens region across the four poses, sampled on the
rendered **grayscale strip** (same `smoothscale → grayscale` pipeline as the
sheet):

```
stage 0  luma = 103.8   (sealed dark seam)
stage 1  luma = 168.0   (delta +64.2  — distinctly dim lens)
stage 2  luma = 229.4   (delta +61.4  — white-hot peak)
stage 3  luma = 136.1   (delta -93.3  — clearly lower, shattered web)
```

Every ADJACENT step exceeds the ≥40 luma target (+64.2, +61.4, −93.3). The
closest non-adjacent pair (sealed 103.8 vs shattered 136.1, gap ~32) is still
separated by an unmistakable shape cue — a single dark groove vs a six-armed
spiderweb fracture — so all four stages are distinguishable on the grayscale
strip. Confirmed visually in `round_4.png`'s grayscale row: dark / dim-narrow /
bright-wide / mid-with-web-cracks.

## KEEP items — all preserved

Magenta/gold/teal candy palette; cream crepe fringe keyline + cone outline;
parcel clearance (`BCY = 30` + `BOTTOM_SPIKE_SCALE`); the night additive seam
glow; the de-faced vertical-diamond candy lens. No parcel is drawn by this build
— it is supplied by the staged gameplay frame.

## Verdict artifact

`round_4.png` — DAY and NIGHT gameplay frames at play-size (~40px) both read as
the non-creature spiky star party-ball: a single dominant magenta apex straight
UP, a splayed bottom pair clearing Pip's parcel below, and the candy lens as the
focal seam (night especially). The reference column confirms a clean single-point
apex, 7 tips, and the 4-beat / 4-shape grayscale crack swing.
