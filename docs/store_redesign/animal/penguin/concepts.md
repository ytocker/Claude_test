# PENGUIN Animal-Skin Redesign — WAVE 2: FROM-SCRATCH REDRAWS

**Direction change.** Wave 1 (rockhopper / emperor / explorer / diver / aurora,
kept in git history) reused the flat `build_penguin` chassis and layered themed
accessories on top — a beanie, a snorkel, an aurora crown. That misread the
brief. The **original penguin art itself is badly drawn**; the ask is **new
versions that simply look much better AS penguins** — no props.

**Root cause.** The current `build_penguin` (`game/animal_skins.py:291`) is a
2-layer body (shadow + main), a plain 2-ellipse belly, tiny r=3 dot eyes, a flat
2-color beak, and texture-less flippers. The project's best animals are far more
crafted — eagle's chest-highlight ellipse + outlined beak, toucan's gloss-sheen
overlay + color-banded beak + eye-surround patch, phoenix's 4-layer concentric
shading. Wave 2 rebuilds the penguin from scratch using those techniques.

**The premium build kit every redraw applies** (borrowed from the master
animals):
- **3–4 layer body shading**: shadow `(+1,+1)` → main → small chest-highlight
  ellipse `(-3,-3)` → optional inner core, for real 3D depth.
- **Gloss sheen**: a small SRCALPHA ellipse (alpha ~150) blitted top-left of the
  body — the wet/premium toucan touch.
- **AO shadow**: a darker ellipse where the head meets the body.
- **Better eyes**: r≥4 with a surround patch and the built-in glint.
- **Crafted beak**: ≥2 colours + 1px dark outline + a bright highlight line.
- **Flipper texture**: 1px feather/edge lines instead of a flat fill.

All five preserve the dark-back / light-belly penguin split and read at the 40px
in-motion truth read. Numbers map to design_1…design_5.

---

## 1. ADÉLIE — Classic Tuxedo, Done Beautifully  `skin_penguin` (keeps the id)
The definitive penguin, simply drawn really well. Crisp black-back / white-front
with the signature **white eye-ring** on a glossy blue-black head.
- **Body**: glossy blue-black, 3-layer (deep shadow → blue-black main → a cool
  blue **chest-highlight ellipse**), plus a **gloss-sheen** overlay top-left so
  the back reads wet and rounded, not flat.
- **Belly**: clean off-white oval with a soft lower shadow and a faint warm
  upper sheen; a subtle AO shadow under the chin where head meets belly.
- **Head**: blue-black dome with the **white eye-ring** (a pale ring around each
  eye — the Adélie tell), bigger r4 eyes with glint.
- **Beak**: neat short dark beak with a small orange base wash + a bright
  highlight line (stubby Adélie bill).
- **Flippers**: blue-black with a 1px cool leading-edge highlight.
- **Feet**: tidy orange webbed feet with a toe split + 1px outline.
- **Palette**: `#1B2436` blue-black, `#0F1626` deep shadow, `#46557A` cool
  highlight, `#F6F7FB` belly, `#2A2230` beak, `#FF9A3C` foot orange.
- **Distinctness**: the only pure classic tuxedo + white eye-ring; the "perfect
  ordinary penguin," premium by craft alone.

## 2. GENTOO — Chubby Cutie  `skin_penguin_gentoo`
Maximum charm: a plump round casual-mascot penguin with the gentoo **white
bonnet stripe** across the eyes and big friendly eyes.
- **Body**: rounder, plumper egg (wider than tall) in slate-black, 3-layer with
  a generous **belly gloss sheen** and a soft AO shadow under the chin.
- **Head**: slate dome with the gentoo **white bonnet** — a white band sweeping
  over the crown and wrapping behind each eye (the species tell).
- **Eyes**: oversized r4–5 with a pale surround patch — the cuteness hero.
- **Beak**: bright **orange banded** beak (deep-orange root → bright-orange tip)
  with an outline + highlight line; the gentoo orange-red bill.
- **Feet**: chunky bright-orange webbed feet, toe splits.
- **Palette**: `#23283A` slate, `#12151F` shadow, `#5566`-ish cool highlight,
  `#FAFAF4` belly/bonnet, `#FF7A1E`→`#FFB347` banded beak, `#FF8A2A` feet.
- **Distinctness**: the rounded chibi proportion + white bonnet + huge eyes;
  the cuddly casual-mascot read.

## 3. EMPEROR — Regal Premium  `skin_penguin_emperor`
The handsome stately adult, carried by a smooth **vertical gradient** body the
flat fill can't show.
- **Body**: taller, upright egg with a slate→steel **vertical gradient**
  (reuse `draw.make_gradient_surface` / `lerp_color_multi`), masked to the body
  ellipse, plus a cool chest highlight.
- **Ear-to-throat melt**: a narrow vertical **orange teardrop down each side of
  the neck**, fading orange→amber→pale-yellow into a soft golden throat bib —
  the king/emperor signature, small and elegant (not a big cheek patch).
- **Head**: smooth crest-less slate dome; symmetric r3–4 eyes with glint.
- **Beak**: long slender **bicolor** beak — slate upper, **coral-pink** lower
  mandible stripe + a pale highlight line.
- **Flippers**: slate with a thin **pale-blue rim**; cool slate feet.
- **Palette**: `#2C3550`→`#5A6A86` body gradient, `#F4F6FB` belly, `#F0992C`→
  `#FFD66A` ear-to-throat melt, `#FF9CB0` coral mandible, `#AEC6E0` rim.
- **Distinctness**: the only gradient body + elegant ear melt; upscale and
  slender vs the chibi #2.

## 4. ROCKHOPPER — Crested, Rebuilt Right  `skin_penguin_rockhopper`
The punk crested penguin, this time drawn from scratch with full craft (wave 1's
version was the crest bolted onto the flat chassis).
- **Body**: navy 3-layer with a chest highlight + a faint sheen; **textured
  flippers** (1px feather lines).
- **Crest**: a **bold integrated spiky golden brow-fan** — 4 fat, wide-splayed
  plumes (3-value yellow ramp) rising past the crown and crossing the head edge.
- **Eyes**: **fiery red** r4 on a pale face bed so they read against the dark
  head; bold brow above.
- **Beak**: chunky **outlined orange beak** with a filled lower-mandible wedge +
  highlight line (the thick rockhopper bill).
- **Feet**: wide-set pink-orange webbed feet with toe splits (hopping stance).
- **Palette**: `#262B40` navy, `#15192A` shadow, `#5A6486` highlight, `#F7F4EC`
  belly, `#FFD21E`/`#D6A20E`/`#FFEC82` crest ramp, `#FF8A1E` beak/feet,
  `#F2402E` red eye.
- **Distinctness**: the only crested + red-eyed punk; same hero as wave 1 but on
  a properly crafted body.

## 5. BABY CHICK — Fluffy  `skin_penguin_chick`
A totally different adorable proportion: a fuzzy down-covered baby penguin.
- **Body**: **fuzzy silver-grey down** — a soft rounded body with a **textured
  fuzzy edge** (short radial fur ticks around the silhouette) and a paler grey
  belly; soft AO under the chin.
- **Head**: **oversized round head** (bigger than the body proportion) with a
  paler grey face mask and a faint darker grey "cap."
- **Eyes**: **huge sparkly** r5 eyes with a big glint + a small lower catch — the
  whole charm of the design.
- **Beak**: tiny stubby dark-grey beak (chicks have small dark bills).
- **Feet**: tiny stubby pale-grey feet.
- **Palette**: `#9AA3B2` down, `#6E7686` shadow, `#C3CAD6` belly, `#EDEFF4`
  highlight, `#3A3F4C` beak, `#7C8494` feet.
- **Distinctness**: the only fuzzy-textured + big-head baby; a soft monochrome
  grey palette no adult uses, and a completely different silhouette.

---

## Distinctness matrix
| # | Name | Hero read | Proportion | Palette pop |
|---|------|-----------|------------|-------------|
| 1 | ADÉLIE | white eye-ring + gloss | rounded adult | blue-black + orange feet |
| 2 | GENTOO | white bonnet + huge eyes | chubby chibi | bright orange beak |
| 3 | EMPEROR | gradient body + ear melt | tall slender | orange→yellow + coral |
| 4 | ROCKHOPPER | spiky gold crest + red eye | chunky | yellow + red |
| 5 | BABY CHICK | fuzzy down + giant eyes | big-head baby | soft greys |

Each is a full from-scratch build applying the premium kit — visibly better drawn
than the flat original, and distinct from the other four in species, proportion,
and palette.
