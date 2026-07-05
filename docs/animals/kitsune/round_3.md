# KITSUNE (`skin_kitsune`, LEGENDARY) — Round 3 (final pass)

Art-director returned **VERDICT: ITERATE** with a minimal must-fix list and the
directive to **freeze** the four wins (moon-disc brow blaze, open eyes +
catchlight, banding step count, dive-mass / flap-spread delta) and apply ONLY
the three fixes below. Round 3 does exactly that — no other changes to the
converged production build.

Sheet: `round_3.png` — the single `build_kitsune` design at **hero 130px** (with
the rebuilt store-card gold aura) + **40px level/dive (smooth)** + **40px
NEAREST x3** (the honest gameplay-pixel read), on **BOTH a night AND a
bright-day backdrop**.

Contract unchanged: 64×84, fox body at `(32,44)` for the fixed 14px collision
circle, head near `(44,34)`, nine-tail fan behind the body, 4 poses,
procedural-only, WHY-only comments, no live particles. Single production API:
`build_kitsune(wing_angle_deg)` + `get_kitsune = _make_prebuilt_skin(build_kitsune)`
+ `BUILDERS = {"skin_kitsune": get_kitsune}`. `build_kitsune_aura()` stays
hero-only and strictly OUT of the 40px frames.

---

## FROZEN (untouched)

- Moon-disc brow blaze — the signature win.
- Open oracle eyes + catchlight pixel.
- Banding step count — still three discrete value STEPS via `_band()`.
- Dive-mass / flap-spread delta — `centre`/`fan` gather logic unchanged; the
  body stays the dominant mass and the down→up vertical spread is the visible
  flap.

## MUST-FIX, applied

1. **Violet back on the CROWN (radial re-anchor).** At true 40px the old fan
   coloured each whole plume by arc-symmetric distance from centre
   (`edge = abs(t-0.5)*2`), so BOTH arc ends went violet — and because the
   back-swept LEFT flank plumes sit low against the body, the violet pooled
   there as a purple wing/paw while gold sat on top, inverting the intended
   read. Round 3 colours each plume **RADIALLY** instead: `_plume` base-coats
   the whole quill GOLD, then over-paints cooling MID/VIOLET wedges
   (`_quill_segment`) only on the outer/upper third, and the spine runs gold at
   the root → violet at the tip. The tip flames are now crowned by **tip
   HEIGHT** (lowest tips stay gold, highest tips get the bright violet flame),
   not arc symmetry. Net: gold owns the base/inner third and violet rings the
   TOP outer tips across the WHOLE arc on every frame — including the dive —
   instead of one flank.

2. **Radiant warm-gold hero aura.** `build_kitsune_aura` was three stacked
   additive amber blobs (`_soft_glow`) that over-summed into a muddy mid-brown
   olive vignette and cheapened the store card. Rebuilt as a single per-pixel
   **monotonic radial**: a bright near-white-gold core (`AURA_CORE`) ramping
   smoothly out through radiant gold (`AURA_MID`) to fully transparent, with an
   ease-out falloff (`(1-f)**1.6`) so there is no hard band edge and the colour
   never passes through brown. Radius bumped to `AURA_R=47` so it blooms
   slightly PAST the fan tips and reads as emitted light. Still baked, still
   composited behind the outlined fox, still strictly OUT of the 40px frames.

3. **Day-sky dive rim.** On the gathered/lifting poses (`g > 0.45`) a 1px dark
   `RIM` arc is now baked along the fan↔body seam, so on the bright-day dive the
   back-swept violet cluster keeps its lower edge instead of losing it into the
   body shadow. Verified on the day panel and a zoomed day-dive crop: the fan
   stays distinct from the body on light sky.

LEGENDARY spectacle constraint honored: no live particles — foxfire tips, body
warmth, and the hero aura remain baked into the 4 frames; the flicker is the
per-frame tail-spread delta.
