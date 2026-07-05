# KITSUNE (`skin_kitsune`) — Round 1

Top-ranked legendary showpiece for the ANIMALS store: a celestial nine-tailed
fox (NON-bird). The flying "wings" are the **nine-tail fan** — it sweeps wide
on the down-pose and gathers on the up-pose across the 4 base wing poses
(`_WING_ANGLES = 50,20,-10,-40`). No live particle system: the foxfire glow,
gold aura, and wisp accents are **baked into each of the 4 frames**, with the
flicker expressed by varying tail spread + wisp positions between frames.

Sheet: `round_1.png` — hero 130px (down-pose, full fan) + 40px level/dive
smooth + 40px NEAREST x3 (the honest gameplay read), on a night backdrop.

Contract held by every variant: body mass centred at `(32,44)` for the fixed
14px collision circle; head near `(44,34)`; tail-fan spreads behind/around but
the body stays put. Palette per brief — `#FFF4D6` fur / `#FF7A1A` ear+tail
tips / `#FFFFFF` blaze / `#B86BFF` foxfire / `#FFD24D` aura.

These are 5 genuinely different takes — different fur colour, fan direction,
tail-tip flame colour, fox pose, blaze style, and foxfire amount — not 5
tweaks of one idea.

---

## v1 · TENKO ASCENDANT
Celestial **white** fur, leaping pose, full **nine** tails in a wide back-
swept halo fan with **violet** flame tips, warm gold aura. Teardrop violet-
glowing forehead blaze.
- **40px tell:** white fox + wide violet-tipped tail-halo bursting back-left;
  blaze glows on the brow.
- **Why:** the clean, balanced "default legendary" — regal + cute, maximum
  desirability. Reads on both day and night.
- **Weak spots:** the most conventional of the five; the violet tips are small
  — could lose punch on a busy day sky.

## v2 · KYUBI EMBER
Classic **russet** fox, **gold-fire** tail tips, aggressive forward-pounce
pose, dense gold foxfire wreath, upswept gold flame blaze, fierce angled eyes.
- **40px tell:** orange fox wreathed in a gold-flame tail-burst; the warmest,
  most "fire-spirit" read.
- **Why:** the fierce Kyūbi archetype — distinct in silhouette and colour from
  the white variants; a strong contrast partner to the phoenix.
- **Weak spots:** russet fan vs russet body needs the lighter-fur separation
  it now has; on a warm day sky the gold-on-orange could flatten — relies on
  the baked outline + tips. Less "cute," more "fierce."

## v3 · CURLED ORACLE
Curled-regal seated fox, tails sweeping **UP** as a tall **white-fire peacock
fan**, a round **moon-disc** blaze, gentle closed eyes, a single curled tail
wrapping the front paws.
- **40px tell:** the vertical peacock-fan silhouette (unique among the five) +
  serene face; moon-disc blaze.
- **Why:** the serene shrine-spirit pole — its upward fan gives the store a
  genuinely different silhouette to choose between.
- **Weak spots:** the up-fan pushes more mass above the body, so the dive-tilt
  read is the tightest of the set; calm face is less expressive at 40px.

## v4 · VIOLET WISP
**Implied** fan — 5 bold foreground tails + 2 ghost tails imply the nine —
**violet-dominant** foxfire, white body, comet-like wisp embers; violet diamond
blaze + glowing violet eyes. The aura sits behind so the body reads on top.
- **40px tell:** the spookiest read — a white fox half-dissolved into a violet
  foxfire burst with drifting embers.
- **Why:** mythic/eerie prestige; the "fewer-but-bolder tails + ghosts" trick
  keeps the fan crisp at 40px while still implying nine.
- **Weak spots:** heaviest glow — risks muddiness on a dark night sky; the
  implied (not literal nine) count is a deliberate gamble for the director.

## v5 · PRISM TENKO
White body, a **gold→violet gradient** tail fan (warm inner tips → cool outer
tips), diamond blaze with gold core + violet glow ring, dual gold/violet aura,
two-tone embers.
- **40px tell:** the prismatic warm-to-cool tail-burst — the most jewel-like,
  "most expensive" read; gold centre, violet edges.
- **Why:** combines v1's clean fox read with a premium colour story unique to a
  top-tier gacha skin; balances mythic prestige + charm.
- **Weak spots:** the gradient is subtle at 40px (the gold core dominates) —
  may need stronger violet edge tips to sell the prism at gameplay scale.

---

### Cross-cutting notes for the director
- All five hold the body at the collision centre; fans spread without moving
  the body mass.
- Flame-tip puffs are kept small and bright on purpose — the tapering PLUME is
  the read, the puff is the spark. Earlier oversized puffs clumped into a
  "pompom crown"; that's fixed.
- The down-pose (frame 0) shows the widest fan; the up-pose (frame 3) gathers
  it — that spread delta is the "flap." Wisp embers also shift per frame for
  the foxfire flicker, since there's no live particle feed.
