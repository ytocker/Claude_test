# Store Skins — Round 1 candidates

Exploration sheet: `docs/store_skins/round_1.png`
Candidate code: `docs/store_skins/candidate_skins.py` (8 real procedural builders,
all `(frame_idx, tilt_deg) -> Surface`, animation- + tilt-correct, cached,
outlined via `parrot._add_outline` — directly liftable into `game/parrot.py`).

The sheet shows every new skin twice: a **store-hero (130px)** render and a
**40px in-game** chip, on the store's dark night-sky card, plus a comparison
strip of the 6 currently-shipping skins.

## New concepts (8)

| Skin | One-line rationale | Proposed catalog id / name | Suggested cost |
|------|--------------------|----------------------------|----------------|
| **Pirate** | Tricorn + eyepatch over the far lens + gold hoop earring + tiny skull cockade — the universal "rogue" read; eyepatch keeps one aviator lens, marrying skin to base. | `skin_pirate` / "PIRATE" | 150 |
| **Ninja** | Black cowl with a glinting eye-slit (covers the shades) + crimson headband whose knot-tails stream back off the head — adds motion to a flapping bird. | `skin_ninja` / "NINJA" | 170 |
| **Wizard** | Tall midnight-blue cone with a curled droopy starred tip + flowing white beard under the beak + scattered stars — the most "costume", high silhouette change. | `skin_wizard` / "WIZARD" | 220 |
| **Astronaut** | Translucent blue bubble dome + gold reflective visor band + side antenna with a glowing red tip + white EVA collar — premium, instantly recognisable. | `skin_astronaut` / "ASTRONAUT" | 280 |
| **Pharaoh** | Gold-and-blue striped nemes headdress with side lappets + a rearing uraeus cobra on the brow — regal, the boldest colour-on-head read. | `skin_pharaoh` / "PHARAOH" | 300 |
| **Viking** | Iron dome helm with riveted brow band + nose-guard + two curved horns + braided golden beard with beads — chunky, high-fantasy fan favourite. | `skin_viking` / "VIKING" | 200 |
| **Cowboy** | Tan curled-brim stetson with a cattleman crease + leather band & silver buckle + red kerchief bandana — warm, friendly, casual-arcade staple. | `skin_cowboy` / "COWBOY" | 160 |
| **Disco** | Whole body recoloured to a rainbow shimmer (built from the from-scratch parrot palette, not a tint), masked light streaks, mirror-ball twinkles + star party-shades — the one full-body skin, premium "rare" energy. | `skin_disco` / "DISCO" | 320 |

Costing rationale: cheap/silhouette-light skins (Pirate, Cowboy, Ninja) sit in
the existing 150–180 band; heavier costume changes (Viking, Wizard) at 200–220;
the three "premium/rare" reads (Astronaut, Pharaoh, Disco) extend the range
upward to 280–320 to give the store a high-end aspirational tier.

## Implementation notes (for the art-director read)

- All 8 compose over the 4 base wing frames, so the flap animation and the tilt
  rotation are preserved exactly like the shipped skins.
- 7 layer an **accessory** onto the unmodified scarlet macaw (so the aviator
  shades stay where they make sense — Pirate keeps one lens under the eyepatch,
  Disco stamps star-shades over them). **Disco** instead recolours the whole
  body via the from-scratch `_build_parrot_with_palette` path, then overlays
  shimmer — the only full-body restyle, justifying its premium price.
- Tall headgear (wizard cone, viking horns) is drawn onto a taller composite
  canvas with the parrot kept vertically centred, mirroring `dollar_parrot_hat`,
  so nothing clips before rotation.

## Proposed revisions to the WEAKEST current skins

Reviewing the shipped 6 via their `get_*` builders:

1. **TOP HAT (`get_hat_parrot`)** — weakest. It is literally the *triple
   power-up* stovepipe (gold cylinder + green `$`) reused as a cosmetic, so it
   reads as "money buff," not a character, and the green `$` clashes on the
   night card. **Revision:** drop the `$`, switch to a classier black-felt
   top hat with a satin band + a small red rose or a monocle on the near eye,
   so it reads as a distinct "dapper gentleman" skin rather than a recycled
   buff prop. (Keeps the silhouette, changes the palette + front motif.)

2. **SKELETON (`get_skeleton_parrot`)** — second weakest *as a store skin*. It
   is the X-Ray Sparks electrocution sprite (baked cyan crackle ticks + a flat
   dark silhouette), so as a cosmetic it looks "mid-getting-zapped" and is very
   dark/low-contrast at 40px against a night sky. **Revision:** make a
   store-dedicated calmer variant — warm bone-ivory bones (not stark white)
   on a deep-navy body, remove the cyan sparks, add small hollow eye-sockets
   with a pinpoint pupil glint so it reads as a charming Day-of-the-Dead
   skeleton rather than a hazard flash; bump the bone value so it survives the
   downscale.

(If the director wants, ZOMBIE could also get a lighter once-over — the
chartreuse KO sprite is a *death* frame; a happier "undead but jaunty" pose
with a stitched grin would sell better as a purchase.)

## File paths

- Sheet: `/home/user/skybit/docs/store_skins/round_1.png`
- Candidate builders: `/home/user/skybit/docs/store_skins/candidate_skins.py`
- Renderer: `/home/user/skybit/docs/store_skins/render_round_1.py`
