# THUNDERBIRD (`skin_thunderbird`) — Round 1

Legendary spectacle skin for the ANIMALS store. Five genuinely distinct takes
on ONE creature: a broad-winged storm raptor wreathed in storm-cloud feathers,
with crackling lightning + electric glow **baked into the 4 sprite frames**
(there is no live particle system feeding the skin). The "thunderclap" is
expressed by scaling the lightning/glow with the down-stroke: forks crackle
biggest on frame 0 (wings down) and fade on the up-pose.

Research grounding (Pacific Northwest Coast + Plains thunderbird myth): broad
outstretched wings, **two curved head plumes/horns** that distinguish it from
an eagle, **eyes that flash lightning**, and **lightning "snakes" hurled from
beneath the wings**. Each variant pulls a different one of these forward.

Sheet: `round_1.png` — hero 130px (down-stroke/clap frame) + 40px smooth
(clap/dive) + **40px NEAREST x3 (clap vs up-pose)** so the honest gameplay
silhouette and the thunderclap beat are both visible, on a night sky.

Palette (brief): `#3A4A6B` plumage / `#1A2238` storm shadow / `#FFE14D`
lightning / `#7FD0FF` electric rim / `#FFFFFF` flash core. v3 swaps to a
storm-purple body (`#544682`/`#BE96FF`) to set it apart hard.

---

## v1 · STORM-RAPTOR  (the "default" read)
- **Concept:** broad eagle silhouette, soft billowy cloud-feather plumage, two
  back-swept **curved head plumes** (the cultural tell), forked lightning off
  **both wingtips**, restrained blue body aura that pulses on the clap.
- **40px tell:** curved twin plumes + glowing storm-blue eye + the two wingtip
  forks. Confirmed legible in NEAREST x3.
- **Weak spots:** the most "expected" of the five; left-wingtip fork can sit
  close to the tail mass on the up-pose — needs an eye to confirm it never
  reads as a tail spike at dive tilt.

## v2 · THUNDERHEAD  (eyes-first)
- **Concept:** sleek predatory silhouette, angular saw-tooth razor primaries,
  a single zig-zag **brow-bolt crest**, almost no wingtip lightning — the whole
  spectacle is two **fierce over-sized glowing eyes** with white cores.
- **40px tell:** the twin blazing blue eyes + brow-bolt. Most distinct *face*.
- **Weak spots:** least "lightning-y" at a glance — risk of reading as a generic
  glowing-eyed bird rather than a *thunder*bird; the brow-bolt is the only fork
  and may crowd the eyes. The sharp wing tips lose definition more than the
  cloud wings at 40px.

## v3 · STORM GOD  (storm-purple, full aura)
- **Concept:** heavy enveloping electric aura (two halo layers), lightning
  **veins webbing across the open wings**, a charged white chest core, a tall
  upright **fan crest**, full **purple** palette. Most "divine/cosmic."
- **40px tell:** the purple charged field + fan crest + the big under-body fork.
- **Weak spots:** the spectacle constraint bites hardest here — the heavy aura
  is closest to burying the silhouette; needs a check that it still reads on a
  **bright-day** sky (blue aura on blue sky). The wing veins are the detail most
  likely to vanish at 40px and become faint noise.

## v4 · LIGHTNING-SNAKE  (Northwest-Coast formline)
- **Concept:** formline-flavoured — bold blocky tail, split-U feather marks, a
  **two-horn curled crown**, a bold **ovoid eye**, and the myth's signature:
  lightning **snakes hanging DOWN from beneath each wing** (not at the tips).
- **40px tell:** lightning *below* the body — the most original silhouette
  break of the five, plus the formline ovoid eye + twin horns.
- **Weak spots:** the down-hanging bolts extend the vertical footprint — confirm
  they don't read as legs/talons; formline split-U arcs are fragile at 40px and
  may flatten to specks.

## v5 · WHITE-FLASH STRIKE  (high-contrast)
- **Concept:** the most dramatic thunderclap beat — on the down-stroke a massive
  **white-core fork fires straight DOWN between the wings**, cloud-feather puffs
  **compress** on the up-pose, a vertical jagged **mohawk crest**. Built on raw
  white-on-dark contrast, not colour, so it survives any sky.
- **40px tell:** the white flash-core eye + the big down-firing fork on the clap
  frame (clearly absent on the up-pose — the beat is unmistakable in NEAREST x3).
- **Weak spots:** the most asymmetric across frames — the down fork adds a lot of
  vertical mass on frame 0 only, so the silhouette "breathes" hard; verify that
  doesn't read as flicker in motion. The mohawk is subtler than v1's curved
  plumes and may need more contrast.

---

## Cross-cutting notes for the next pass
- All five keep the body mass centred at (32,44) for the fixed 14px collision
  circle; lightning/aura reach wider but the body stays put.
- Glow is kept restrained (low peak alpha, additive) so the silhouette stays
  legible — the legendary constraint. v3 pushes this hardest by design.
- Not yet tested against a **bright-day** sky in the sheet (night only) — the
  blue rim + flash core are the at-risk elements there; v5's white core and
  v4's down-bolts are likely the most sky-agnostic.
