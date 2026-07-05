# SPORTS — "pro athlete" costume collection concepts

Brief: dress Pip the scarlet macaw as a **professional player** for 5 different
sports. Each is a distinct full athletic kit (uniform + sport gear + signature
prop). This is a NEW costume COLLECTION — the user will pick which to add as new
store items. Numbers map to design_1…design_5.

## Hard rules
- **Read the SPORT instantly at 40px, day AND night.** Each design has ONE
  unmistakable hero (the ball / helmet / bat / racket) that survives downscale.
  Bold, clean shapes; no fussy 1px detail. The sport must be legible before the
  bird is.
- **Stay Pip.** Keep the macaw recognizable underneath the kit (head/beak/eye) —
  charming "parrot dressed as an athlete," not a generic mascot.
- **Footprint law (gameplay):** the collision hitbox is a fixed ~10px circle and
  never changes. Keep ALL body kit (jersey, pads, balls, props) INSIDE the base
  bird footprint — body centre ~(32,52), feet line ~y65-69 (HY+24..28). Nothing
  hangs below the feet; nothing balloons the body (an American-football pad must
  be SUGGESTED by jersey shape/shading, NOT by making the bird wider). Only
  HEADGEAR (helmet/cap/visor/headband) may rise above CROWN_Y=31. A bat/racket is
  slung diagonally INSIDE the silhouette — only its tip may overshoot (like the
  shipped pirate cutlass).
- **Uniform = a painted jersey over the torso** (keep the macaw head/wings) OR a
  team-colour body recolor via `_build_parrot_with_palette` — designer's call per
  sport; either way keep Pip's head reading as a parrot.

Coord anchors: canvas 64×100; head HX=47 HY=41; CROWN_Y=31; body centre ~(32,52);
feet ~(28,65)/(34,65); a held ball / slung prop reads diagonally across the body.

---

## 1. THE STRIKER — Soccer / Football (skin_soccer)
- **Hero:** the black-&-white **soccer ball** (hexagon-patched) + a bold
  vertical-striped team jersey.
- **Kit:** vertical-striped jersey (e.g. royal-blue + white) with a big number
  painted over the torso; a captain's armband on the near wing; shin-guards +
  cleats at the feet line; (optional thin sweatband). Soccer ball tucked at the
  near foot / lower wing.
- **Palette:** `#2A5BD0` jersey blue, `#F2F2F2` white stripe/ball, `#161616`
  ball patches, `#E8C24A` armband.
- **Body:** paint striped jersey over the torso (keep macaw head).
- **Distinct:** the only black-&-white ball + striped kit — instant "soccer."

## 2. THE BALLER — Basketball (skin_basketball)
- **Hero:** the orange **basketball** (dark seam lines) held at the chest/wing.
- **Kit:** a sleeveless **tank jersey** (bold colour + big number) over the
  torso; a **headband** across the brow; wristbands; high-top sneakers at the
  feet. Orange basketball held high at the near wing.
- **Palette:** `#6A2DA8` jersey purple (or `#C8372C` red), `#E8761E` ball orange
  + `#7A3A12` seams, `#F2F2F2` trim/number.
- **Body:** paint tank jersey over the torso.
- **Distinct:** the only orange ball + sleeveless tank + headband — instant
  "basketball."

## 3. THE GRIDIRON — American Football (skin_football)
- **Hero:** the **helmet with a facemask** — a rounded team-colour shell + a
  2-3 bar grey facemask over the beak — the strongest head silhouette of the set.
- **Kit:** a bulky **padded jersey** with a big number (shoulder pads SUGGESTED
  by the jersey's raised-shoulder shape + shading — NOT extra width); eye-black
  smudge under the eye; a brown **football** (pointed oval + white laces) tucked
  at the near wing.
- **Palette:** `#1B2A6B` helmet/jersey navy, `#B8BEC8` grey facemask, `#F2F2F2`
  number, `#6E4326` football brown + white laces.
- **Body:** paint padded jersey over the torso; helmet over the head.
- **Distinct:** the only helmeted/face-masked athlete — the most armoured,
  boldest head read.

## 4. THE SLUGGER — Baseball (skin_baseball)
- **Hero:** the **cap** (curved brim) + a wooden **bat** slung over the shoulder
  (diagonal, inside the silhouette, tip may overshoot).
- **Kit:** a **pinstripe jersey** (white + thin navy lines) with a number; the
  bat slung from the near wing across the back; a catcher's **mitt** on the near
  wing; cleats at the feet.
- **Palette:** `#1B2A6B` cap/pinstripe navy, `#F2F2F2` jersey white, `#C9A24B`
  bat tan + `#8A6A2E` shadow, `#6E4326` mitt brown.
- **Body:** paint pinstripe jersey over the torso; cap on the head.
- **Distinct:** the only one with a slung wooden bat + classic cap + pinstripes.

## 5. THE ACE — Tennis (skin_tennis)
- **Hero:** the **tennis racket** (oval strung head + handle) held up in the
  near wing + a **visor/sweatband**.
- **Kit:** a white **polo** with a collar + a colour accent; wristbands; a
  bright **tennis ball** at the wing; short white shorts hint at the hip.
- **Palette:** `#F4F4F0` polo white, `#2A9D4A` racket frame + accent, `#F2F2F2`
  strings, `#CBE84A` tennis-ball green, `#1B6B36` visor trim.
- **Body:** paint white polo (collar + trim) over the torso.
- **Distinct:** the only racquet sport — the strung racket + visor + neon ball,
  the brightest/cleanest white kit.

---

## Ranking (best first → maps to design_1…5)
1. **THE GRIDIRON** — boldest, most distinct silhouette (helmet+facemask reads
   instantly at 40px); the most "armoured athlete."
2. **THE BALLER** — the orange ball is the single most legible sport-prop; tank +
   headband is clean and iconic.
3. **THE SLUGGER** — slung bat + cap is a strong, distinct silhouette (and reuses
   the proven pirate-cutlass slung-prop technique).
4. **THE STRIKER** — the b/w ball + striped kit is globally the #1 sport; clean.
5. **THE ACE** — elegant racket + visor; the subtlest silhouette (racket strings
   are the trickiest 40px read), so ranked last but the brightest/cleanest look.
