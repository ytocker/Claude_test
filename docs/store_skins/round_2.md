# Store Skins — Round 2

Sheet: `docs/store_skins/round_2.png`
Builders: `docs/store_skins/candidate_skins.py` (liftable `(frame_idx, tilt_deg) -> Surface`
getters — animation- + tilt-correct, cached, `parrot._add_outline`-wrapped).
Renderer: `docs/store_skins/render_round_2.py`

Round-2 north star from the critique: **a skin lives or dies at 40px in motion.**
Every signature shape is now pushed UP and OUTWARD past the crown so it breaks
the bird's outline, given a value floor (no near-black on the navy card), made
2px-minimum, and kept off the dark head where it muddied. Each NEW card shows a
130px hero plus TWO 40px reads — level and a steep dive-tilt — because the 40px
crop is the truth test.

## What changed per skin (vs round 1)

### Dark-on-dark trio (priority 1)
- **PIRATE** — felt lightened from near-black brown to a **mid-value slate**
  that lifts off the scarlet head; tricorn raised a row so the brim breaks the
  crown outline; gold rope replaced by **one continuous 2px bright band**
  carrying the read; skull cockade enlarged to a **~4px white skull dead-centre-
  front**; eyepatch moved to the **near eye**. (On standby — see Crown.)
- **NINJA** — the **crimson headband is now the hero**: a solid 4px bright band
  sitting ABOVE a slimmed dark cowl so it pops; streaming knot-tails cut to a
  single thick 3px tail + knot; blue eye-glints recoloured to **warm amber** so
  they stop fighting the scarlet.
- **ASTRONAUT** — dome is now **opaque** with a **crisp 2px bright rim** + one
  strong specular hot-spot so it reads as a hard sphere, not "out of focus";
  visor **cooled to blue-steel with a hard dark edge** so it never doubles the
  gold beak; antenna committed to a 2px stalk + 2px bright tip.

### Push above the crown / kill 1px noise (priorities 2-3)
- **PHARAOH** — kept the gold cap (2nd-best silhouette); stripes simplified to
  **fewer, 2px-wide** bands (killed the 1px shimmer noise); **uraeus cobra
  enlarged** so it reads as a clear hero accent above the brow.
- **DISCO** — star-shaped shades collapsed to **one clean gold star-lens** over
  the near eye (dropped the doubled per-lens stamping); kept the full-body
  rainbow recolour, shimmer streaks, and wide value contrast for colourblind
  safety.

### Same-hue separation + tall-headgear anchoring (priorities 4-5)
- **VIKING** (ship-candidate) — horn **tips widened ~1px + bright tip caps** so
  the points survive downscale; braided beard **cooled/darkened** off the
  scarlet so the bright helmet carries the read; horns rooted in the brow band
  so the rotated dive composite keeps them on the head mass.
- **WIZARD** (keeper) — beard reduced ~25% and given a **warm under-shadow tying
  it to the red chest** so the high-value white stops detaching; cone anchored
  **lower & wider** on the crown so a steep dive can't snap it off the body;
  kept the 5-point star-tip beacon.
- **COWBOY** (benchmark) — minor only: kerchief nudged to a **cooler wine-red**
  so it separates from the scarlet chest.

### New standby (priority 7)
- **CROWN / KING** — added as the Pirate replacement: a tall **bright-gold
  five-spike crown** with jewelled band + bead finials. Breaks the outline
  hard, never dark fabric — a guaranteed 40px read.

## Current-skin redraws (approved — new liftable builders)
- **TOP HAT** — was the Triple-buff gold-`$` cylinder (read as a buff prop).
  Redrawn as a **dapper black-felt topper + bright red satin band + crisp light
  top rim** (so the black survives 40px on navy) **+ a near-eye monocle**.
- **SKELETON** — was the X-Ray electrocution sprite (looked mid-death). Redrawn
  as **warm bone-ivory on a deep-navy body**, cyan crackle dropped, **hollow
  sockets + a pinpoint glint** for Day-of-the-Dead charm; bones are the
  brightest element at 2px min.
- **ZOMBIE** — was the chartreuse KO death frame. Redrawn as **"undead but
  happy"**: friendly green body, **stitched grin**, mismatched googly eyes,
  belly seam stitches, and a cheek scar — alive-feeling, purchase-worthy.

## Final proposed names + coin costs

| Skin      | Name      | Cost | Notes |
|-----------|-----------|------|-------|
| skin_pirate    | PIRATE    | 150 | recovered; or swap for Crown |
| skin_cowboy    | COWBOY    | 160 | benchmark |
| skin_ninja     | NINJA     | 170 | headband hero |
| skin_viking    | VIKING    | 200 | ship-candidate |
| skin_wizard    | WIZARD    | 220 | keeper |
| skin_crown     | CROWN     | 260 | standby / premium |
| skin_astronaut | ASTRONAUT | 280 | premium tier |
| skin_pharaoh   | PHARAOH   | 300 | premium tier |
| skin_disco     | DISCO     | 320 | rare full-body |

Redrawn current skins keep their existing catalog ids (`skin_tophat`,
`skin_skeleton`, `skin_zombie`).

## Ship-ready (my read — director decides)

Now reading cleanly at 40px level + dive: **Cowboy, Viking, Wizard, Pharaoh,
Disco, Astronaut, Crown**, plus the three redraws (**Top Hat, Skeleton,
Zombie**). **Pirate** and **Ninja** are the two that most depend on the
director's call — both recovered their read, but Crown is the safer premium
swap if Pirate's slate tricorn is judged still too quiet at 40px.

## File paths
- Sheet: `/home/user/skybit/docs/store_skins/round_2.png`
- Builders: `/home/user/skybit/docs/store_skins/candidate_skins.py`
- Renderer: `/home/user/skybit/docs/store_skins/render_round_2.py`
