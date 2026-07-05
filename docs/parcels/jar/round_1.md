# JAM JAR — parcel cosmetic (LOW tier) — Round 1

The tiny gift Pip carries below him (~22px), built at 2× (44×44) then
smoothscaled to 22. Procedural pygame only, static single surface, mode-agnostic.

## 22px read
A squat rounded-rectangle glass BODY with a distinct dark RIM band and a
wider, domed gingham-red cloth CAP that overhangs the glass — a stout cylinder
with a "hat". The translucent amber core (lighter down the middle, deeper amber
at the walls) plus a single vertical glass-highlight stripe sell glass — the
material no other parcel has. Ruffle skirt is implied with ~5 hem dots, not a
fine scallop grid (fine detail dies at 22px).

## Palette
- DAY glass `#E8A33D` over translucent core `#F6C66E`; gingham-red cap
  `#C23B33`; dark rim `#7A4A1E`.
- Inner highlight `#FFD98A` lifts the cap dome and the glass stripe (also
  carries the soft amber night glow).
- Dark high-value outline `#331812` bakes the silhouette so it holds against
  the bright DAY sky (sky_bot ≈ 170,220,245) and the NIGHT sky.

## Tilt survival
Across the TILT ROW (−25/0/30/60/90°) on day / night / grayscale the
cap-over-cylinder outline stays recognizable at every bank, including the
on-its-side 90° frame. Grayscale shows one bold silhouette with clean value
steps: dark rim/outline vs. bright amber core vs. mid-red cap.

## 22px risk
The gingham cross-dots and meniscus line are near the resolution floor and may
read as noise rather than cloth pattern; if the art director wants the "preserve
jar" cue stronger, options are a bolder/taller cap dome or a more saturated
amber core. The glass-highlight stripe is the load-bearing material cue and
survives well; the ruffle hem dots could merge at the smallest banked frames.
