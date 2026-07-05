# UFO Store skin REDESIGN — Round 1 (5 concepts)

Re-exploration of `skin_ufo`. The current production look (matte-amber domed
saucer + chasing rim-light ring + pulsing tractor beam) is the right DIRECTION;
this round re-does its EXECUTION across five distinct, individually-shippable
takes — three refined spins on the classic domed saucer, two bolder takes.

All five honour the hard contract: 64×84 SRCALPHA, dominant mass at (32,44),
4 baked life-cycle frames from `_WING_ANGLES`, no wings / no live particles,
drawn upright (tilt is applied outside via rotozoom), procedural-only, bold
silhouette + one tell at 40px on DAY and NIGHT with a baked high-value keyline
for the bright day band.

Sheet: `round_1.png` — per concept: hero 130px (split day|night), 40px NEAREST
×3 truth test on BRIGHT DAY and NIGHT (frames 0·1·2·3 + dive), and the 4 baked
frames. Each row wraps through the production cached-getter pattern so the 40px
read matches in-game exactly.

## Concepts

### 1. CHROME CLASSIC  (refined classic)
The showroom-clean read. A polished mirror-chrome hull whose value runs dark
top → bright equator highlight band → dark belly (the chrome "tell"), with a
crisp mirror streak, a tight cyan glass dome over a deep gradient, and a clean
WHITE rim chase. The most premium, most legible classic silhouette.
- Palette: hull `#283242 → #788CA2 → #E0ECF8` (dark/mid/mirror-hi), shadow
  `#3A465A`; keyline `#F5FAFF`; rim dim `#4660 78` / lit `#EBFAFF`; dome
  `#3A6E96 → #96DCF5`, ring `#465C74`, glint `#FFFFFF`; beam `#AAE6FF`.

### 2. EMBER DRIFTER  (refined classic)
A hand-built, lived-in saucer. Warm copper-bronze hull with radiating riveted
panel seams and a shoulder row of rivets, a deep amber glass dome over a core
that throbs with the beam pulse, an amber rim chase, and an ember tractor beam.
Warmer and more crafted than the flat production amber — steampunk-tinged.
- Palette: hull `#3A1E0E → #965626 → #E09E56`; panel line `#281408`; rivet
  `#FFD696`; keyline `#FFDC96`; rim dim `#603412` / lit `#FFB046`; dome
  `#FF9E40`, deep `#783010`, core `#FFE896`, ring `#5C3216`; beam `#FFA850`.

### 3. AURORA GLASS  (bold-leaning classic)
A jewel-like translucent saucer. An oil-slick hull that shifts violet → teal →
magenta across its face with a bright iridescent equator streak, a prismatic
dome with a rainbow stripe, and a MULTICOLOUR rim chase whose lit pair cycles
hue per frame (cyan → violet → mint → pink). Blooms hardest at night.
- Palette: hull `#2C1E4E / #1C566E / #602864` (violet/teal/magenta) over
  `#100E22`; keyline `#DCEBFF`; rim hues cyan `#78F5FF`, violet `#BE82FF`,
  mint `#78FFBE`, pink `#FF96F0`; dome `#3C3C96 → #B4E6FF`, glint `#FFFFFF`;
  beam `#B4C8FF`.

### 4. SCOUT ORB  (bold / out-there)
No saucer, no dome — a single glowing spherical scout drone. The dominant mass
is a luminous teal orb with a dark IRIS "eye" whose pupil OPENS and THROBS
across the four frames (the life-cycle tell), wrapped by an orbiting halo ring
of guard-lights that advances one notch per frame. Reads as a living floating
eye: alien but instantly legible. A keyline circle holds the dark lower
hemisphere on the day band.
- Palette: orb `#125A6E → #BFFFF0` core, deep `#125A6E`, rim-dark `#08222E`;
  iris `#0A1E28`, pupil `#D2FFFA`; keyline `#DCFFFA`; guard lit `#D2FFFA` /
  dim `#1E6E82`; beam `#78F5EB`.

### 5. CRYSTAL SHARD  (bold / out-there)
A faceted crystalline disc cut from flat amethyst gem planes rather than a
smooth hull. A fan of angular top facets that brighten on alternating frames
(a chasing facet shimmer), a glowing core in the crystal heart that throbs and
sends a light shaft up the central ridge, and a sharp white keyline along every
cut edge so the hard geometry survives a bright sky.
- Palette: facets `#2C1C46 → #6846A2 → #B096EB` (dark/mid/hi); edge `#EBE1FF`;
  core `#DCB4FF`, hot `#FFF0FF`; underside `#180E28`; rim dim `#46326E` / lit
  `#D2AAFF`; beam `#BE96FF`.

## Truth test
Renders confirmed on BOTH a bright DAY sky (sky_bot ≈ (170,220,245)) and a
dark NIGHT sky for all five concepts at 40px NEAREST ×3 (frames 0·1·2·3 + dive).
Dark hulls carry a baked high-value keyline; glows bloom at night.
