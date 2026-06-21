# JET redesign — AEROBATIC TEAM JET · Round 1

**Concept:** the priciest secret skin re-imagined as a high-gloss AIR-SHOW
DISPLAY jet (Blue Angels / Thunderbirds / Red Arrows energy) — the flashiest,
most colourful candidate in the store. The bold team LIVERY is the tell, drawn
as STRUCTURE (one high-contrast colour shape) so it survives the 40px downscale
as a clean graphic, not fussy detail.

**Contract held:** each `build_aerobatic_vN(wing_angle_deg)` returns ONE flat
64×84 SRCALPHA frame, fuselage mass centred (32,44), drawn NOSE-RIGHT / UPRIGHT
/ LEVEL. No baked rotation/flip — the render sheet applies the production 205°
secret-skin spin only to preview the in-game inverted nose-high attitude. 4
poses = afterburner pulse + ±1px nose pitch; glow + (v3) smoke baked, no live
particles. Local `_make_prebuilt_skin`; `BUILDERS["skin_aerobatic"]` registered.

## The 5 sub-takes (genuinely different)

- **v1 · BLUE ANGEL** — deep navy gloss, sharp delta. Livery = bold GOLD nose
  cap + a tapering gold SPEAR down the spine to the tail, plus gold delta
  leading edges. Cool blue burner. Navy/gold = classic premium.
- **v2 · THUNDERBIRD** — brilliant white gloss, sharp delta. Livery = a RED→BLUE
  ARROW sweeping down the fuselage (red leading wedge, blue tail band) with red
  wingtip flashes. White reads bright on day AND night; the arrow is the tell.
- **v3 · RED ARROW** — all-red gloss, sharp delta. Livery = a bold WHITE centre
  diamond + white leading edges, with a baked WHITE display SMOKE-TRAIL puff
  aft (the air-show signature). The most "display-team" of the five.
- **v4 · SUNBURST RACER** — SWEPT wing (different planform). Livery = a HARD
  diagonal two-tone split (white fore / hot-magenta aft) with an orange seam
  and a yellow LIGHTNING bolt down the wing. The most graphic / modern racer.
- **v5 · GOLD JACKET** — black gloss, sharp delta. Livery = a bold GOLD CHEVRON
  wrapping the nose + gold spine line + gold tail band + gold leading edges.
  Black/gold = the most "expensive" read; gold holds up day AND night.

## Sheet

`docs/animals/jet_redesign/aerobatic/round_1.png` — per variant: HERO 130px on
a DAY sky and a NIGHT sky, then 40px level/dive reads (smooth + NEAREST x3) on
both a bright day sky and a dark night sky, so the livery's downscale survival
is honest on both backdrops.

## Open questions for the art-director

- Which livery reads most premium AND most legible at 40px — the gold spear
  (v1), the red/blue arrow (v2), or the gold chevron (v5)?
- Does the v3 smoke puff read as a clean contrail or as clutter at 40px?
- Is the v4 swept-wing planform a worthwhile differentiator, or does the delta
  silhouette read more "fighter" and should all converge on delta?
- White-body v2 vs red-body v3: which survives the night sky better?
