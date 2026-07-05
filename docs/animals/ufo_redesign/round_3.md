# UFO Store skin REDESIGN — Round 3 (final surgical pass)

Round 3 applies the art-director ROUND-2 ITERATE verdict. CHROME CLASSIC,
EMBER DRIFTER and AURORA GLASS were LOCKED (shippable — silhouettes + palettes
untouched). Only SCOUT ORB and CRYSTAL SHARD needed surgical fixes; this round
changes ONLY those two. Same hard contract: 64×84 SRCALPHA, dominant mass at
(32,44), 4 baked life-cycle frames from `_WING_ANGLES`, no wings / no live
particles, drawn upright (tilt outside via rotozoom), procedural-only, bold
silhouette + one 40px tell on DAY and NIGHT.

Sheet: `round_3.png` — per concept: hero 130px (split day|night), 40px NEAREST
×3 truth test on BRIGHT DAY and NIGHT (frames 0·1·2·3 + dive), and the 4 baked
frames. Same layout as Round 2; all five concepts shown.

## What changed (Scout + Crystal only)

### 4. SCOUT ORB — capped the pupil so the iris never blows out
The dilation tell is kept (it was the best on the sheet), but the peak pupil is
now CLAMPED so a dark iris well always survives as a ring at 40px — the tell
reads as an EYE OPENING, not a lamp switching on.
- The pupil radius is capped at `iris_r - 4`, guaranteeing a ≥3px dark rim of
  iris around the bright pupil even on the wide-open peak frame (frame 2). The
  pupil's glow halo was also tightened (`halo=1.5 → 1.25`) so the bloom can't
  erode that surviving ring.
- The dark iris well is re-stamped just outside the pupil footprint each frame,
  so the surviving ring stays genuinely DARK on the peak-open frame rather than
  fading to mid-grey.
- The two side guard-lamps now sit in a dark socket ring (`C4_ORB_DARK` disc
  under each lamp), holding their value ABOVE the orb/aura bloom on the peak
  frame so they never wash out into the dome glow.

No change to the orb silhouette, the 3D top-lit sphere shading, the specular
hotspot, or the palette.

### 5. CRYSTAL SHARD — unified into ONE faceted mass
The bright top-ridge keyline had detached as a glowing wishbone floating over a
dark mid-hull (read as arc + wedge). Fixed purely via value structure — the
traveling-facet tell and the core throb are unchanged.
- The top-ridge keyline brightness dropped ~28% (`C5_EDGE` 236,226,255 →
  170,152,210) and the ridge silhouette lines now use a still-dimmer `C5_RIDGE`
  (150,134,188) so the ridge sits ON the body as a cut edge, not a floating
  wishbone.
- The mid-hull facet bases were lifted hard (`C5_FACET_DARK` 52,34,82 →
  118,90,168; `C5_FACET_MID` 104,72,162 → 148,116,204) so there is no dark
  dead-band between the ridge and the glowing core.
- A solid mid→high-value filled disc is now drawn UNDER the facet triangles, so
  no dark sky shows in the crescents between the triangular facet fan and the
  elliptical keyline — the gem reads as one filled mass and the facets only score
  cut detail over it. This closed the dark top-cap crescent.
- The crystalline underside was lifted off pure black (`C5_UNDER` 28,18,48 →
  52,36,84) so the belly→hull is a single value falloff, not a third dark band.

The core throb (r5 + halo2.9 hot / r2 + halo1.6 cold) and the one traveling lit
facet per frame are kept exactly as Round 2.

### 3. AURORA GLASS — frozen
Left exactly as Round 2 (locked). No detail added, no highlight band removed.

### 1. CHROME / 2. EMBER — frozen
Left exactly as Round 2 (locked). No edits.

## Grayscale truth test on the two changed concepts

Verified on a desaturated (luminance) copy of the 40px NEAREST×3 read, DAY and
NIGHT:

- **SCOUT frame 2 (peak-open) reads as an EYE.** In grayscale the bright pupil
  is surrounded by a clearly darker iris ring on every frame including the
  wide-open peak — it is an eye opening, never a solid white disc. Guard lamps
  survive as distinct bright dots on both sides, above the bloom.
- **CRYSTAL day silhouette reads as ONE connected faceted disc.** In grayscale
  the hull is a continuous mid-to-high value gem with the core as a single value
  peak — no dark dead-band, no detached wishbone. The dark belly is a smooth
  bottom falloff of one form. The traveling lit facet is visible on the cold
  (odd) frames; the core throb is visible across the cycle.

## Truth test (all five)
All five clear the 40px NEAREST ×3 read on BOTH the brightest DAY band
(sky_bot ≈ (170,220,245)) and a dark NIGHT sky — frames 0·1·2·3 + dive — each
with a distinct grayscale-surviving tell: Chrome's lower-lip rim chase, Ember's
plate seams + core throb, Aurora's grow-paired multicolour chase, Scout's capped
pupil dilation, Crystal's traveling facet + core throb.

Render headless:
`SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python docs/animals/ufo_redesign/_render_sheet.py 3`
