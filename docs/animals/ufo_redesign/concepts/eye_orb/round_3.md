# EYE-ORB — Round 3

Single, surgical fix per the Round 2 `ITERATE` note: **kill the dark annulus on
the day orb.** Everything else (4-beat blink, pinpoint flare, warmed pupil, night
read) was signed off in Round 2 and was preserved — confirmed by the scanline
checks below.

Sheet: `round_3.png` (rendered via the shared `render_concept_sheet` helper).

## Root cause found: the dark ring was the HOUSE OUTLINE bleeding through the soft bloom

The Round 2 dark navy/teal annulus was not (only) the body gradient. The render
pipeline wraps every concept frame in `game/parrot._add_outline`, which is drawn
UNDER the sprite and traces a 1px **dark** contour (`(20,12,18)`) around the
alpha>8 silhouette. The orb's soft *additive* bloom feathered out to a long
low-alpha tail (alpha ~15–50 for many px), so:

- the dark outline was drawn far out at the faint bloom terminus, AND
- where the semi-transparent bloom sat over that dark outline it **bled through**,
  muting the bright cyan rim to grey `(~50–90 luma)` — the "dark ring with a light
  in it" read.

So the fix had to make the orb's whole silhouette read as **opaque light** with a
hard edge, not a soft additive tail the dark outline could show through.

## What changed (edge treatment only)

1. **Opaque glow base (new step 0).** A fully-opaque bright-cyan radial fills the
   entire silhouette out to a tight terminus (`term = ORB_R+9`). Every silhouette
   pixel is now alpha 255 and luminous cyan, so the house outline can only show as
   a single 1px ring OUTSIDE the disc — it can no longer bleed through the corona.

2. **Body gradient bottoms out on luminous mid-cyan, not navy.** `_radial_orb` no
   longer ramps the perimeter toward `IRIS_DEEP`/`RIM`; it bottoms out on
   `IRIS_MID = (60,182,240)` with a widened, outboard mid band. The navy `outer`
   colour is no longer used by the body.

3. **Brightest ring moved to the TRUE outer edge.** A hot cyan-white rim-light
   (`RIMLIGHT = (190,240,255)`) rides the outermost 2–3px of the disc; an opaque
   bright disc-edge cap (step 7) sits on the body edge so the silhouette boundary
   itself is the brightest part.

4. **Dark keyline removed; containment is now LIGHT.** The navy `KEYLINE` is gone
   entirely (no `KEYLINE` reference remains in the module). Containment is the
   bright opaque edge + a 1px light-cyan hairline (`HAIRLINE = (170,235,255)`).

5. **Flare re-baked into the opaque base (day-safe).** Because the corona is now
   opaque, the pinpoint flare is baked as a bright cyan-white FRONT that swells
   OUTWARD through the opaque corona with `k["bloom"]` (calm frames tuck it near
   the body; the pinpoint pushes it out and brightens the corona rim). The additive
   `_glow_dot` was dialled down (`intensity 1.7→0.55×`) so it no longer saturates
   the corona to flat white and swallow that travelling front. The `_PULSE` blink
   table and the core/pupil draw were NOT touched.

## Proof — DAY: no orb pixel at/inside the silhouette is darker than the day sky

Day-sky reference (sampled from the in-play swatch): **luma 155.**

Outlined frame, **downscaled to the ~44px in-play size, composited on the day
sky**, scanned across every pixel within the orb radius:

```
min body luma = 215   (day sky = 155)
body pixels darker than sky: NONE — PASS
```

Every orb pixel is **60+ luma brighter** than the sky. A full 2-D interior scan of
all four outlined frames finds **NO** dark interior pixel — the only dark pixel
anywhere is the legitimate 1px `_add_outline` ring at the very terminus, sitting on
the sky (standard for every skin in the game):

```
dark INTERIOR pixels (excluding terminus outline): NONE — PASS
```

Native outlined edge scan (frame 0), horizontal — the silhouette is luminous cyan
all the way out, then one 1px outline ring on sky:

```
dx=20 (174,255,255) a=255
dx=21 (177,255,255) a=255
dx=22 (180,255,255) a=255
dx=23 (183,255,255) a=255
dx=24 (20,12,18)    a=255   <- single 1px house outline, on sky
dx=25 (0,0,0)       a=0
```

Squinting at the silhouette boundary now reads a will-o'-wisp / spirit-light: the
edge is the brightest part, the glow IS the shape, zero dark containment.

## Signed-off elements — confirmed PRESERVED (not regressed)

- **4-beat blink** — pupil white-run per frame: 12 → 6 → (pinpoint) → 6 px;
  `_PULSE` core_r 5.5 / 3.4 / 0.8 / 2.2 untouched; frames 1 and 3 stay distinct.
- **Pinpoint flare (frame 2)** — re-baked into the opaque corona so it survives the
  opaque-edge fix. Night corona luma per ring shows the pinpoint frame's bright
  (255) front reaching furthest out (dx=ORB_R+6 vs ~ORB_R+4 on calm frames) and the
  highest corona sum (2241 vs 2183 / 2188 / 2219): the orb visibly flares the
  instant the pupil pinches shut.
- **Warmed pupil** — `CORE = (235,250,255)`, unchanged.
- **Night read** — the orb still "glows out of black"; the opaque bright corona +
  baked flare read strongly against the night sky and the 1px dark outline is
  invisible on black. Not regressed (night remains the stronger biome).

## Files

- `build.py` — opaque glow base + baked flare front (steps 0/8); body gradient
  floor to `IRIS_MID`; `HAIRLINE` replaces `KEYLINE`; rim-light + opaque cap on the
  true outer edge; `_glow_dot` intensity reduced (edge treatment only).
- `render.py` — outputs `round_3.png`.
- `round_3.png` — combined day/night/grayscale concept sheet.
