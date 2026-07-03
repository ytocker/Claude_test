# RED PANDA — Store skin · Round 1

New from-scratch ANIMALS-tab creature (`skin_red_panda`): a round russet
fluffball with a fat cream-and-rust **ringed tail** curling up behind it and a
white **face-mask**. Five genuinely different takes — not five tweaks. Each is
the player's flappy bird, animating over the 4 base wing poses
(`_WING_ANGLES = 50,20,-10,-40`).

There is no red panda flight in nature, so the "flap" is reinterpreted as a
**leap-and-balance**: the big tail sweeps UP on the down-pose (counterweight
for lift) and the forepaws tuck on the up-pose.

Contract honoured for all five: `build_red_panda_vN(angle) -> 64×84 SRCALPHA`,
body mass at **(32,44)**, head near **(44,34)**, ears-only headroom above;
`get_vN = _make_prebuilt_skin(build_red_panda_vN)`. Procedural only; WHY-only
comments. Sheet shows hero 130px + 40px level/dive over **night AND day**
swatches + NEAREST x3 magnification (the honest gameplay read).

Palette: `#C1440E` fur / `#7A2A0C` rings / `#FFF4E6` mask+belly+tail-bands /
`#3A1A0C` eyes+nose / near-black legs `#4A2410`.

---

## v1 — Cozy Curl
The classic cuddly storybook fluffball. Round body, broad white mask, modest
rounded ears with cream interiors, and a fat ringed tail curling UP and over
behind the back in a tight C.
- **40px tell:** the cream-and-rust ringed C-arc hugging the back + the wide
  white mask. Both survive the downscale cleanly.
- **Strength:** the most universally readable, warmest, most "obviously a red
  panda" of the set. Tail-arc + mask both land.
- **Weak spot:** safest/least surprising; the tail arc and body merge slightly
  on the level pose at 40px.

## v2 — Reaching Leaper
Dynamic & athletic. Body leans forward into the dive, forepaws reach ahead, and
the tail whips low-back then high in a long upward S streamer.
- **40px tell:** the forward lean + reaching paws read as a mid-leap; the tail
  whip arcs up.
- **Strength:** the only take that sells *motion*; great dive frame.
- **Weak spot:** the tail whip partly hides behind the body at 40px, so the
  signature ringed-tail read is the weakest of the five. Would need the whip
  pushed further clear of the body to be a frontrunner.

## v3 — Big-Tail Hero
The TAIL is the brand. A huge, fat, six-ring plume looms behind a deliberately
smaller body, filling the upper-left like a question-mark.
- **40px tell:** a giant ringed banana arc over the back — unmissable even at
  40px NEAREST, on both night and day.
- **Strength:** the boldest, most distinctive silhouette; "ringed tail" is the
  first and loudest read at any size.
- **Weak spot:** the body/face shrink to make room, so the charming face is
  less prominent; risks reading as "striped worm" if the body gets any smaller.

## v4 — Chibi Round
Maximum mascot charm. Oversized head, huge sparkly eyes, tiny tucked body and
paws, a short fat tail curling up tight beside the cheek like a comma.
- **40px tell:** the huge-eyed white-mask face + chunky comma tail.
- **Strength:** the cutest, most gacha-charming, most "buy me" face. The big
  eyes read at any scale.
- **Weak spot:** the comma tail is subtle at 40px — the *ringed-tail* signature
  is the least prominent here; this take leans on the face instead.

## v5 — Foxy Bandit
Sleeker, sharper, more fox-like. Big tufted POINTED ears, a bold "bandit" rust
mask-band across the eyes over a cream muzzle, and a slimmer tail with fewer,
bolder rings plus a big bright cream tip "flag".
- **40px tell:** the pointed-ear silhouette + bandit mask + the strong white
  tail-tip flag.
- **Strength:** the most graphic / distinctive; the white tail-tip is a crisp
  high-contrast accent that survives the downscale, and the pointed ears break
  the silhouette differently from the other four.
- **Weak spot:** reads a touch more "fox/lemur" than "red panda" — the pointed
  ears trade some species-accuracy for graphic punch; the bandit band can crowd
  the eyes at 40px.

---

### Cross-cutting notes
- All five keep body mass anchored at (32,44); the fat tail is pure silhouette
  flourish, never collision mass, so no variant cheats the 14px hit circle.
- The cream rings/tip and white mask are the elements doing the most work
  against BOTH sky extremes; the rust body alone can muddy against a warm day
  sky, which is why every take threads cream highlights along the tail.
- The leap-and-balance flap (tail up on down-pose, paws tuck on up-pose) is
  subtle at 40px but gives the hero/130px a lively, non-static feel.
