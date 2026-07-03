# UFO Store skin REDESIGN — Round 2 (5 concepts)

Round 2 applies the art-director ITERATE critique. All five concepts are kept
(the user picks one). Same hard contract: 64×84 SRCALPHA, dominant mass at
(32,44), 4 baked life-cycle frames from `_WING_ANGLES`, no wings / no live
particles, drawn upright (tilt outside via rotozoom), procedural-only, bold
silhouette + one 40px tell on DAY and NIGHT.

Sheet: `round_2.png` — per concept: hero 130px (split day|night), 40px NEAREST
×3 truth test on BRIGHT DAY and NIGHT (frames 0·1·2·3 + dive), and the 4 baked
frames. Each row wraps through the production cached-getter pattern so the 40px
read matches in-game exactly.

## The gate fix (critique #1, #6) — applied to every dark hull

A new shared `_keyline_full()` bakes a CONTINUOUS high-value keyline around the
WHOLE silhouette: a bright top arc PLUS a (dimmer, hue-matched) lower-lip arc.
The lower lip is darker than the top so the disc still reads as top-lit metal,
but it never goes pure black. This is what makes a near-black hull read as ONE
connected craft on the bright day band (sky_bot ≈ (170,220,245)) instead of a
bright crown floating over a black blob (Crystal) or a dark blob with one
glowing dot (Aurora), and it keeps every belly edge alive on the night sky.

`_rim_chase()` gained a `lip_drop` arg so a chase can be pushed DOWN onto the
darker lower lip (Chrome) instead of being swallowed by a bright equator band,
and the lit pair now uses a wider size swing (lit r=3 / mid r=2 / dim r=1) so
the rotation tracks on value alone — not hue — for a colourblind/grayscale read.

## Per-concept changes

### 1. CHROME CLASSIC  (closest to ship — tightened)
- Chase moved onto the DARK lower lip (`lip_drop=3`) so the lit pair punches
  against the bright mirror equator band instead of disappearing into it; lit
  dots are bigger now, so frames 0–2 visibly differ.
- Dome glint pushed high-left with a short streak tail so it reads as a sky
  REFLECTION catching the glass, not a centred painted stripe.
- Full continuous keyline (bright top + cooler steel lower lip) so the whole
  mirror disc is one hard shape day and night.

### 2. EMBER DRIFTER  (on probation → cleared)
- Riveted PLATE seams are now HIGH-VALUE: each radial seam is a bright
  catch-light edge paired with a 1px dark shadow, so the disc reads as bolted
  copper plates/facets at 40px — not a smooth shell.
- Dome core THROB pushed hard: a wide bright→dim swing (r 4 + halo 2.8 on frames
  0/2 → r 2 + halo 1.6 on 1/3), matching the production beam's ~0.26 pulse
  energy. The throb is the clearest "alive" tell and survives grayscale.
- Full keyline (bright top + warm lower lip) so the copper belly survives night.

**How EMBER now beats the rejected production amber UFO:** the production skin
is a SMOOTH matte amber ellipse — at 40px it's a featureless amber lozenge whose
only motion is the rim chase. EMBER bakes a riveted-PLATE identity that survives
40px: high-value seams radiate from the dome and read as distinct bolted facets
(grayscale-confirmed), a warm rivet row sits on the shoulder, and a SECOND tell —
a hard core throb — runs in parallel with the chase. So EMBER is legibly a
hand-built, lived-in copper craft (two tells, faceted shell) where the production
amber is a smooth one-tell saucer. It is warmer, more textured, and unmistakably
not the old shell at thumbnail size.

### 3. AURORA GLASS  (gate concept → cleared the day read)
- The DAY collapse is fixed: a continuous bright top arc + cool lower-lip
  keyline now closes the translucent hull into one connected craft on the bright
  band (previously a dark blob with one glowing dot).
- Hull base values lifted (violet/teal/magenta) for day legibility.
- The multicolour rim chase keeps its per-frame hue cycle, but every hue step is
  now PAIRED with a size step (the lit dot grows), so the "alive" tell survives
  desaturation instead of relying on hue alone.

### 4. SCOUT ORB  (the bold one — lifted to a premium drone)
- Added a clearly DARK lower hemisphere (vertical lift in the shader) so the orb
  reads as a 3D sphere lit from the top — a drone shell, not a flat pearl/ball.
- Added a hard white specular HOTSPOT high-left on the glass shell — the
  "glass eye" premium read.
- The dark IRIS is now a solid eye-well and the bright PUPIL DILATES across the
  cycle: a tight pupil on frame 0 → wide open on frame 2 → back (a blink /
  breathe). The pupil is a contained light, not a bloom that swallows the iris,
  so it reads as an EYE; the dilation is the strongest grayscale tell of the five.
- Guard ring replaced with TWO bold high-contrast lamps that swap sides per
  frame (lit r=3 / dim) so they actually read at 40px instead of vanishing.
- Full keyline (top crown + lower lip) holds the dark belly on day and night.

### 5. CRYSTAL SHARD  (on probation → cleared)
- The DAY collapse is fixed: a continuous bright top-ridge keyline + a lower-lip
  arc, PLUS explicit bright keylines along the underside trapezoid's two cut
  edges and belly edge, so the faceted gem reads as one connected shape (the
  ellipse arc alone could not trace the hard prism belly point).
- "All facets shimmer" (which read as flicker/noise) is replaced by ONE bright
  facet highlight that travels one step around the crown per frame.
- The glowing CORE is now the PRIMARY tell and throbs HARD: r 5 + halo 2.9 +
  ridge light-shaft on frames 0/2 → r 2 + halo 1.6 on 1/3. Core throb is the
  grayscale-safe motion read.

## Colourblind / grayscale pass (critique #7)
Every life-cycle tell was verified on a desaturated copy of the DAY truth panels.
No tell relies on hue: Chrome/Aurora/Crystal chases use a size+value swing, the
Aurora hue cycle is backed by a grow step, Ember & Crystal cores throb on a wide
size/halo swing, and Scout's pupil dilation is a pure size+value cue. All five
pass.

## Truth test
All five clear the 40px NEAREST ×3 read on BOTH the brightest DAY band
(sky_bot ≈ (170,220,245)) and a dark NIGHT sky — frames 0·1·2·3 + dive. The two
gate concepts (Aurora, Crystal) now render as ONE connected craft on day, and
all bellies survive night via the lower-lip keyline.

Render headless:
`SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python docs/animals/ufo_redesign/_render_sheet.py 2`
