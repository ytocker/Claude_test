# FLYING TOASTER (`skin_toaster`) — Round 2

**Verdict to address:** Round-1 ITERATE, winner **V5 NOIR CHROME** (the only
candidate that reads as a toaster at 40px). Round 2 converges to ONE production
build and folds in every art-director directive.

Sheet: `docs/animals/toaster/round_2.png`
Build: `docs/animals/toaster/toaster_skins.py` →
`build_toaster(wing_angle_deg)`, `get_toaster = _make_prebuilt_skin(...)`,
`BUILDERS = {"skin_toaster": get_toaster}`.

Contract unchanged: 64×84 canvas, body mass at (32,44), procedural-only,
WHY-only comments.

## MUST-FIX directives → what changed

1. **Soft feathered "After Dark" wings (was swept STEEL).** Dropped
   `_steel_wing` entirely. The build now uses V1's `_feather_wing` shape
   language — three rounded primary lobes fanning out, no swept-jet rake — but
   recoloured to chrome-white at V5's value contrast (`_WING (224,230,240)` /
   `_WINGD (138,146,162)` / `_WINGH` near-white) so the soft span still pops on
   a night sky. The read is now *soft bird wings on a chrome box*, not
   premium-aero.

2. **Thicker, warmer ember bar.** The ember is a 2px hot bar warmed toward gold
   (`_EMBER (255,176,70)` core + `_EMBERH` highlight) over a tight 1px bloom
   edge (`_EMBERG`), inside a dark slot mouth. At 40px it reads as ONE
   continuous hot bar — the night-side signature. Glow restraint kept: 1px
   bloom, no halo.

3. **Wings inside the body silhouette; body is the dominant mass.** Wing scale
   pulled to 0.88 and anchored lower/narrower on the flank (near wing at
   `(BCX-13, BCY+2)`, far at `(BCX+14, BCY-2)`), spread softened from ±32 to
   ±26. The black/chrome two-tone body now carries the read at every scale.

4. **Toast clamped fully inside the top edge across all 4 frames + dive.** Toast
   height trimmed to 14 and tops driven from `TOP_Y-7` with a clamped pop/bob
   (`max(0, bob)` per side, `pop = int(f*2)`). Worst-case crown sits at y≈20 on
   a 0-top canvas — both gold slices stay fully on-sprite in every flap frame
   and in the dive pose (verified on the DAY/NIGHT level+dive reads and the
   4-frame flap strip).

5. **Darker, cooler day belly.** `_chrome_body` now takes an explicit `belly`
   colour; the underbody is `_BLKB (20,22,30)` — ~12% darker/cooler than the
   lit body — so the lower silhouette stays crisp against the brightest
   pale-blue day sky (see the "HERO 130px · brightest day" panel).

6. **Deuteranope safety.** The crust was pushed cool-dark (`_CRST (104,64,30)`)
   and a dedicated 1px dark crust seam is drawn between the toast bases and the
   ember bar. The bottom-left DEUTERANOPE panel simulates green-blind vision:
   the gold toast and orange ember stay separated by that dark seam rather than
   merging into one warm band.

7. **Mid-pop charm.** On the flap apex (`f > 0.6`) the toast jumps ~2px higher
   (`pop`) and the ember highlight brightens (`_EMBERH` vs `_GLDH`). Motion is
   kept tight (1–2px) so it reads as a *flying* toaster, not a floating one —
   visible across the FLAP CYCLE strip.

## Review reads on the sheet

- HERO 130px on night + on the brightest day band (silhouette stress test).
- 40px NEAREST x3, level + dive, on DAY and NIGHT.
- 4-frame flap strip (toast mid-pop + ember).
- Deuteranope simulation of the level 40px read (normal vs deuter).

All reads procedural, headless-rendered (SDL dummy) so the sheet rebuilds in
CI. The review PNG lives under `docs/` (out of the shipped pygbag bundle).
