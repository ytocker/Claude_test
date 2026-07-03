# PAPER LANTERN — Round 2

HIGH-tier parcel cosmetic. The first GLOWING parcel. Round 1 verdict ITERATE:
night glow absent, vermilion body melting into Pip's red, caps carrying it alone.
Round 2 makes the night glow the showpiece and opens the cap/body value gap.

## What changed (against the R1 critique)

1. **Night glow is now the showpiece (EMITS at 22px).** The baked additive halo
   was widened to ~1.7× the body footprint, given a hot pale-gold heart
   (`#FFC98A` core) plus a second tight inner core, and a higher peak alpha with
   a non-zero rim floor so the warm skirt carries onto the sky instead of dying
   inside the silhouette. To let the bloom actually spill, the sprite surface was
   enlarged (SIZE 22→34 / SS 44→68): the lantern body still draws at the same
   ~22px pixel scale, but the extra margin holds the halo so it blooms out onto
   the open sky. Verified in the night carry crop: a warm orange halo visibly
   spills onto the purple night sky and kisses Pip's underside with a warm rim.
   In daylight it stays a gentle warm halo — the glow blooms at NIGHT.
   (Collision still uses `PARCEL_R`, independent of sprite size — cosmetic only.)

2. **Cap/body value gap opened (fixes red-on-red + grayscale mush).** Gold caps
   pushed lighter — the cap now rides the LIGHT sheen colour (`#FBDF8E`) across
   its top ~45% so it reads as a bright disc, not a mid band. Body walls deepened
   toward `#8E1E16` (mid-dark). GRAYSCALE row now reads caps clearly LIGHT, body
   clearly MID-DARK — the gap is unambiguous, which is the single move that stops
   the lantern red merging into Pip's red.

3. **Cool dark keyline** (`#2A0A0C`) added on the body's upper-left arc where it
   meets Pip's warm red, so the silhouette pops off the bird instead of melting.

4. **Lower gold cap + ribs thickened ~1px.** The bottom cap (the primary
   identifier — the top is occluded by Pip) is a touch wider and taller and now
   carries its own short gold ribs.

5. **Ribbing resolved to 2 clean catch-light bands** flanking the spine (paired
   with a soft wall shadow for panel roundness), not 4 faint seams. The tassel
   gained one clear gold bead on the cord plus a darker fringe tuft below it.

KEPT: gold caps as the naming keyline, the clean symmetric rotation across the
tilt row, the charming pinched-orb silhouette. Identity weighted to the
lower/visible half (bottom cap + tassel + bead).

## 22px read — confirmation
- **Night glow obviously EMITS at 22px:** the night carry crop shows the warm
  halo blooming onto the dark sky and warming Pip's underside; the NIGHT tilt
  swatch shows a visible halo around each banked frame.
- **Caps/body value gap reads in grayscale:** the GRAYSCALE tilt row shows the
  caps as the lightest element and the body as a distinct mid-dark mass — they no
  longer collapse to one value.
- Reads as a GLOWING lantern carried day AND night: gold caps + tassel bead name
  it in both; the glow stays a quiet warm halo by day and blooms by night.

## Tilt survival
Near-symmetric orb with no "up" — clean across the full bank row
(−25 / 0 / 30 / 60 / 90°). Caps, tassel, and bead stay centred and narrow so
nothing smears into a tail when the sprite banks.
