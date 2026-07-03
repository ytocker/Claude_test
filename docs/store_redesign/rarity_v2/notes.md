# Rarity v2 — louder, premium, unmistakable rarity on the store card

The shipped card whispers rarity: a ~8px corner gem, a 32-alpha aura behind the
dome, a faint cabochon ring tint. At 165×99 grid scale you cannot tell tiers
apart. The sheet `rarity_options.png` explores 4 LOUDER treatments, each drawn
on the REAL assembled card across all 5 tiers (common BLUE MACAW → rare PHARAOH
→ epic DRAGON → legendary KITSUNE → masked MYSTERY/UFO), reusing the shipped
`render_hi` primitives, palette and thumbnails so they look like the live game.
Top row = the CURRENT shipped card for direct comparison. Bottom = a greyscale
value proof.

All four keep the COHESION CANON: obsidian card body, the lane-3 gold edge/ring,
the locked rarity gem/glow/deep hues, the glass cabochon + rim-lit macaw as the
hero, and legendary as the loudest tier (warm gold-orange, brightest glow). None
mutate the shipped renderer — each is a separate `draw_card_*` over an identical
chassis, so the ONLY thing changing between treatments is the rarity language.

## 1 — RARITY NAMEPLATE
The item name sits on a tier-coloured gradient plate (gem→glow→deep ramp) with a
gold keyline, a small tracked TIER WORD on the bright crown, and a hairline gold
divider into the name lane.
- **Noticeability:** the single biggest colour mass on the card is now the tier
  hue itself, holding the name — readable rarity per card in one glance, plus the
  tier is *spelled out*, not inferred.
- **Keeps from canon:** corner gem retained, glass dome hero untouched, gold
  keyline = lane-3 card gold, plate fill uses the exact gem/glow/deep triplet.
- **Premium:** the plate carries the same top-sheen + dark-keyline-under-bright-
  bevel finish as every other store surface, so it reads as cut glass, not a
  flat label.

## 2 — RARITY HALO + RING
A bold tier halo behind the dome (peak 120, legendary 150 — vs the shipped 32)
plus a crisp tier-coloured ring riding the dome rim with a bright top-left arc
kiss, and a small tier-tag pill naming the hue.
- **Noticeability:** the hero itself is haloed in the tier colour — the eye lands
  on the macaw and reads rarity in the same fixation. Legendary's halo is the
  loudest on the sheet.
- **Keeps from canon:** the cabochon recipe and gold bezel are intact; the ring
  sits OUTSIDE the bezel so the two golds never fight; corner gem retained.
- **Premium:** the ring gets a jewelled arc highlight (top-left light), not a
  printed circle; the tag pill carries the card-gold keyline.

## 3 — RARITY FRAME
The whole ticket is framed by rarity: a tier-gradient TOP ACCENT BAR carrying the
tier word, tier-tinted corner brackets (lit top-left / shaded bottom-right), a
tier-tinted inner bezel line replacing the neutral gold tray, and a soft tier
wash bleeding in from the edge.
- **Noticeability:** rarity wraps the entire card — scannable from the periphery
  before you even focus on the item; the accent bar gives a guaranteed
  high-contrast tier read at the top of every card.
- **Keeps from canon:** obsidian body + gold outer edge survive; gem moved to the
  free left corner so the bar+gem both read; gold keylines preserved.
- **Premium:** brackets follow the card radius and obey the single top-left light;
  the wash is an additive tint (never a flat fill), so the body stays obsidian.

## 4 — RADIANT GEM CREST
The corner gem is promoted to a real crest: a larger 8-facet gem on a tight
tier-coloured sunray burst (masked to the card), plus a notched tier RIBBON
banner in its own lane above the name.
- **Noticeability:** the burst makes the gem a focal badge of rank rather than a
  speck; legendary's burst is the brightest/longest-rayed; the ribbon names the
  tier in loud type.
- **Keeps from canon:** the locked 8-facet gem cut + gem/glow/deep hues, the
  glass dome hero, the gold ring; ribbon keyline = lane-3 card gold.
- **Premium:** the burst is bloom-cored and card-masked so it never spills past
  the bevel; the ribbon has a real notched silhouette with a gold edge + sheen.

## Greyscale value proof
The bottom strip desaturates each treatment's representative tier colour (plate
fill / halo glow / frame line / crest gem) to BT.601 luma. Epic is darkest, rare
next, common + legendary sit mid-bright, mystery brightest — so tiers separate by
VALUE, not hue alone (colourblind-safe). Common and legendary are closest in pure
luma per the locked palette; in every treatment they are pulled further apart by
structure (legendary always carries the loudest glow/burst + the warm-gold mass)
and mystery stays the brightest neutral so it claims no tier.

## Status
Selection sheet only — not integrated, not self-critiqued. Saved sheet:
`docs/store_redesign/rarity_v2/rarity_options.png`.
