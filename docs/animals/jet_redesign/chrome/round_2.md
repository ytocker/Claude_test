# Secret JET FIGHTER redesign — RETRO CHROME · Round 2 (ship-ready)

Convergence round. Art-director picked **V3 · BLUE-ANGEL TRIM**; this round
folds the whole punch list into ONE production build, `build_chrome`, exposed
as `get_chrome` under the key `skin_chrome`.

Sheet: `docs/animals/jet_redesign/chrome/round_2.png`
Build: `docs/animals/jet_redesign/chrome/chrome_skins.py`

## Punch list — how each note landed

1. **Value-band chrome locked as the body method.** The hot top-highlight is
   compressed into the top ~25% of the fuselage with a HARD lower edge (a drawn
   `_AL_EDGE` seam), a mid `_AL_BODY` band, then a genuinely dark `_AL_LO`
   belly drawn as its own polygon below the centreline. At 40px the top edge
   glints and the belly drops to near-silhouette — the CHROME tell, not flat
   grey. The wings carry the same swing (hot leading-edge facet → dark trailing
   edge).
2. **ONE accent.** Kept the blue spine stripe riding the value break.
   DELETED the yellow pinstripe (was sub-pixel and flickered), the blue wing
   leading-edge flash, and the yellow fin tip flashes. The fins now read by
   value alone (a single lit facet line), no colour.
3. **V4 anti-glare panel stolen.** A small dark matte block (`_MATTE`, a flat
   non-specular value, slightly warmer than the shadow edge) sits immediately
   ahead of the canopy — it frames the cool canopy and plants hard value
   contrast at the focal point.
4. **Belly-to-sky contrast raised for DAY.** `_AL_LO` pushed ~18% darker than
   round 1 (104,112,128 → 74,80,96) so the silhouette holds on bright day sky.
   Re-checked at night: it stays clearly above the self-rim outline value, so
   the underside still reads as metal rather than crushing to a hole.
5. **Burner discipline.** Flame length and halo radius trimmed (`12 + p*9`,
   halo `9 + p*4`) and the hot core kept a narrow seed, so the warm burner
   never out-values the bright metal nose top-band. The metal nose stays the
   dominant read on both skies.
6. **Canopy anchor.** A 1px saturated cool-blue dot (`_CANOPY_DOT`) is drawn
   last over the bubble canopy so nothing overpaints it; it is the only cool
   constant against the warm burner and holds at 40px.
7. **Accessibility.** The jet is identified by silhouette (swept arrowhead +
   big bubble canopy + twin aft burner) and the value swing (bright top / dark
   belly), never by the blue hue alone.

## Contract (lifts straight into game/animal_jet_fighter.py)

- `build_chrome(wing_angle_deg) -> Surface` — one flat 64×84 SRCALPHA frame,
  nose-RIGHT, upright, level, NO baked rotation (the game applies the inverted
  nose-up spin). Fuselage mass centred at (32,44); collision is a fixed 14px
  circle there.
- `get_chrome = _make_prebuilt_skin(build_chrome)` — cached
  `(frame_idx, tilt_deg)` getter: 4 flat poses + per-(frame,3°) rotation cache,
  each run through the house silhouette outline (baked self-rim).
- `BUILDERS = {"skin_chrome": get_chrome}`.
- Procedural-only, WHY-only comments.

## Truth test

The sheet shows two 130px heroes on a split day | night ground, a 130px DAY
dive for the belly-to-sky contrast check, then a DAY row and a NIGHT row each
with smooth 40px + NEAREST x3 (level / dive) — the honest gameplay-pixel read.
The chrome value swing, blue spine, anti-glare panel, and canopy dot all
survive the downscale on both skies.

Headless render confirmed: `round_2.png` (736×576) written.
No game/ code touched — exploration only; integration happens once chosen.
