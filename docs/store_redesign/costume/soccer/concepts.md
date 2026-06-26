# Soccer Costume — Redesign Concepts (v2)

## Why v2?
Previous designs were rejected: jersey anchored at BCX,BCY (too far left / too
high, covering the face) and every design had a forbidden forehead sweatband.
All v2 designs fix these at the root: jersey anchored at HX,HY with top at
HY+8 and hem at HY+23 (same polygon as baseball design_4.py + tennis design_5.py).
No forehead bands of any kind.

---

**Previous content below (v1, archived):**

**Why v1:** the current scratch soccer build
(`tools/sports_candidates/design_1.py` — royal-blue/white striped jersey +
squad number + brow sweatband + knee socks/cleats) reads almost identically to
the current basketball build (jersey block + big white number + brow band +
footwear). The two SPORTS must read as obviously different things. So this set
diversifies soccer hard by **role + era + silhouette** — not five recolored
jerseys. Each must still scream FOOTBALL at the 40px truth read (day + night),
obey the footprint law (kit painted over the scarlet body; head stays the
macaw; nothing balloons the torso or drops below the feet line), and the
soccer BALL ships separately as a parcel — the kit alone carries the read.

Anchors (composite space): `HX=47, HY=41, CROWN_Y=31`; body centre
`BCX=32, BCY=52`; feet `(28,65)/(34,65)` i.e. ~`HY+24`; feet-line kit lives
~`HY+15..27`. Build with the layered pirate/tennis technique: background
elements first, then fill→shade→outline→highlight per element so each survives
the downscale. Props that should sit IN FRONT (gloves, scarf ends, whistle)
are drawn LAST.

The five read as five different football people, so the SET can't be mistaken
for "one jersey, five colours."

---

## DESIGN 1 — THE STRIKER (modern outfield, refined)
- **Hero read:** the clean modern outfield kit — a bold solid-colour jersey
  with a diagonal team SASH + crisp squad number, tucked into shorts, **tall
  knee-high socks + cleats** at the feet. The "legs" silhouette (socks + boots)
  is what makes it instantly soccer and NOT basketball.
- **Object list + placement:** crew-collar jersey over torso (`BCY-12..BCY+11`)
  with a single diagonal sash; bold white squad number "9" on a cleared plate;
  short shorts hem at `BCY+11..+14`; **knee-high socks** each leg with a white
  hoop band (`HY+15..+22`); dark cleats with a white sole + stud ticks at the
  feet line; thin brow sweatband (crown stays open).
- **Palette:** `#E23B45` scarlet-red kit · `#F4F4F8` white · `#1B2A6B` navy
  trim · `#FFCE54` captain gold · `#23252E` cleat.
- **Distinctness:** the only full LEG-KIT design (socks+boots dominate the lower
  silhouette) — the textbook outfield striker.

## DESIGN 2 — THE GOALKEEPER (the glove design)
- **Hero read:** a totally different silhouette — **oversized padded keeper
  GLOVES** on both wing-hands (the hero shapes, drawn LAST so they sit proud of
  the body), a lurid high-vis keeper jersey (the one kit that's deliberately a
  different colour from the team), and a soft cap with a short brim.
- **Object list + placement:** big rounded gloves at both wing roots
  (`BCX±14, BCY±2`) with finger ridges + a wrist-strap; long-sleeve high-vis
  jersey over torso with a dark shoulder yoke; shorts hem `BCY+11`; short socks
  + cleats at the feet; soft-brim cap at the crown (`CROWN_Y`).
- **Palette:** `#19C37D` high-vis green · `#0E1A14` dark yoke/gloves trim ·
  `#F4F4F8` white glove · `#1B2A6B` cap navy · `#23252E` cleat.
- **Distinctness:** the GLOVES own the silhouette — unmistakable goalkeeper, the
  furthest possible read from a basketball tank.

## DESIGN 3 — THE NÚMERO 10 (retro legend, laced collar)
- **Hero read:** vintage international glory kit — a classic **laced V-collar**
  long-sleeve cotton jersey, an old-school embroidered crest, the iconic "10",
  pulled-up retro socks. Warm nostalgia; reads as a different *era* of football.
- **Object list + placement:** long-sleeve jersey over torso with a **laced
  collar** at the neck (`BCY-12..-8`); woven crest patch on the near chest
  (`BCX+6, BCY-3`); big retro "10" low on the shirt; classic high socks with a
  fold-over top band; low retro boots; no headgear (hair/crown open) so the era
  reads clean.
- **Palette:** `#1C6FE0` sky-blue · `#F4F4F8` white · `#C2392B` retro red crest ·
  `#E7C24A` gold lace/crest · `#23252E` boot.
- **Distinctness:** the LACED COLLAR + crest + long sleeves = retro icon, an era
  apart from the modern Striker.

## DESIGN 4 — THE REFEREE (the authority kit)
- **Hero read:** the man in the middle — an all-**BLACK officials kit** with a
  **whistle on a lanyard** (hero, drawn LAST over the chest) and a **yellow +
  red CARD** peeking from the breast pocket. A completely different role and
  colour-story from any player.
- **Object list + placement:** black collared ref shirt over torso with white
  collar piping; whistle + lanyard cord looping the neck and resting at
  `BCX, BCY+2` (metal whistle catches a glint); a yellow card + a sliver of red
  card stacked at the near breast (`BCX+7, BCY-4`); black shorts + socks + boots;
  optional thin black cap.
- **Palette:** `#1A1C22` referee black · `#F4F4F8` white piping · `#FFD23B`
  yellow card · `#E0382C` red card · `#C8CCD4` whistle steel.
- **Distinctness:** the only BLACK kit + the whistle/cards prop set — pure
  officials silhouette, can't be confused with a player or a hooper.

## DESIGN 5 — THE ULTRA (supporter / fan)
- **Hero read:** the terrace fan — a long **team SCARF wrapped at the neck with
  both ends streaming down** (hero, drawn LAST, the ends break the lower
  silhouette), a striped jersey, and a **bobble beanie** on the crown. Festive,
  loud, instantly "match-day fan" rather than player.
- **Object list + placement:** horizontal-striped jersey over torso; thick
  knit **scarf** looped at the neck (`BCY-10`) with two fringed tails dropping
  to ~`BCY+10` over the chest; **bobble hat** on the crown (`CROWN_Y-2`) with a
  pompom; mittened wing optionally raised; cheeks dab of face paint.
- **Palette:** `#7A1FA2` club purple · `#F4C20D` club gold · `#F4F4F8` white ·
  `#2A1340` deep purple knit · `#E8A0B4` cheek paint.
- **Distinctness:** the SCARF + bobble hat (knitwear silhouette) — the only
  non-player, the loudest break from the clean athletic kits.
