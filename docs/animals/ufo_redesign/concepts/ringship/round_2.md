# RINGSHIP — Round 2

Concept kept: the torus + travelling comet-arc identity, and the night bloom
(the best part of round 1). Everything else was reworked against the punch list.

Sheet: `round_2.png` (DAY + NIGHT gameplay frames at true play scale are the
verdict; reference column on the right shows 3x, play-size and grayscale).

## Root cause found and fixed (#1 — the gate)

Round 1's hole was punched, but then the bead's additive bloom washed
~alpha-30 amber across the WHOLE hole, and the getter's outline pass
(`pygame.mask.from_surface(threshold=8)`) promoted that low-alpha wash into an
OPAQUE brown ring — the "dark brown bowl with a painted spot." Confirmed by
sampling the round-1 build: hole pixels read `(255,214,96,30)` raw, then
`(48,36,27,255)` opaque after the outline.

Fix: draw EVERYTHING first (tube shading, keylines, gloss, rim-glow, comet
crest, bead + bloom), then **punch the open-sky annulus LAST** with a hard
white/zero-alpha ring mask via `BLEND_RGBA_MULT`. The mask zeroes alpha from
the inner rim inward but spares a small protected centre disc (`PROTECT_R`) so
the bead survives. Because nothing is drawn after the punch and the annulus is
a hard 0-alpha gap wider than the outline's 1px growth, neither the bloom nor
the outline can refill it.

### Transparency verified in-scene at play scale (the gate)

Alpha map of the composited, OUTLINED frame across the hole (`.` = sky/0-alpha,
`B` = bead, `R` = ring):

```
center row : R........RBBBBBBBBBBB........RR
center col : RRR......RBBBBBBBBBBB......RRRR
```

A clean ring of true 0-alpha sky surrounds a small pip on every axis.

- **DAY in-scene frame:** the blue sky gradient shows straight through the hole
  — the annulus around the bead and around the parcel is sky-blue, NOT a brown
  bowl. (Zoom crop confirms it.)
- **NIGHT in-scene frame:** the deep-purple night sky shows through, and a
  **star is visible inside the hole's upper-left annulus** — definitive proof
  the hole is genuinely see-through, not a painted dome.

## The rest of the punch list

2. **Parcel now hosted BY the ring, not stacked under it.** The torus is grown
   ~18% (OUT_RX/RY 26/23 → 30/27) so the ring is the dominant mass, and the
   hole was widened (IN_RX/RY → 15/13, ratio ~0.50) so Pip's parcel seats
   inside the lower arc of the hole with the ring framing it. In both gameplay
   frames it reads as carried within the ring, not a box beneath a small ring.

3. **Inner-rim bevel + thinner gloss.** Added a light upper-left inner bevel arc
   (`INNER_BEVEL`) on the inside of the hole so the tube reads ROUND from the
   inside. The broad gel gloss was cut to roughly half — a slim upper-left
   crescent (`_gloss`, ~60° arc, 2px) instead of the round-1 marble dome.

4. **Comet TRAVELS, not parks.** The crest is now a narrow (~30° span),
   white-hot-tipped head riding the tube mid-line, with a desaturated wake
   pulled a wide angular gap BEHIND it. Across the 4 phases the crest walks the
   mid-line cleanly at 12→3→6→9 o'clock, so frames read as rotation rather than
   a static reflection smear.

5. **Center bead cleaned up.** The muddy brown bowl is gone (it was the artifact
   of the failed hole). The bead is a clean hot-amber pip (`#FFE25A` core /
   white-hot heart) floating in OPEN sky with a tight contained bloom, small
   (r≈4) so the hole reads ANNULAR around it.

6. **Premium polish — day matches night.** Added a specular white sparkle on the
   pip and a restrained 2-3px cyan rim-glow on the OUTER torus only (additive,
   so it shows in day and blooms slightly more at night) — glow restraint, the
   whole ring is not bloomed. The day frame now looks as expensive as the night
   one.

## Confirmations

- `round_2.png` rendered via the shared helper (`render.py` now outputs
  `round_2.png`).
- The hole is TRULY transparent at 40px on BOTH day and night — sky shows
  through it (a star is visible through the night hole).
- It reads day AND night; the parcel reads as hosted by the ring.
