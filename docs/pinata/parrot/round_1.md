# LOTERÍA PARROT PIÑATA — "El Perico" — Round 1

Sheet: `docs/pinata/parrot/round_1.png`
(GAMEPLAY — DAY | GAMEPLAY — NIGHT | REFERENCE: 3x / play-size / grayscale)

## Read
A fat round-bellied perched bird: a dominant green body mass with a chunky RED
head colour-block high-right and an oversized HOOKED-DOWN cream beak, trailing a
long down-sweeping banded crepe-fringe tail. The two headline tells are the
hooked beak and the big swinging tail. It reads as "parrot piñata" — a crepe
party-bird, not a real macaw — at play size on both skies.

## Palette
- Body green `#34B24A` (`BODY_GREEN`), shade `#207E34`, sheen `#60D674`.
- Head red `#E23A2E` (`HEAD_RED`), shade `#AA241E`, crown highlight `#FF7668`.
- Wing-band stripe: yellow `#F4C12E` (`BAND_YELLOW`) + blue `#2E6FD6`
  (`BAND_BLUE`) — a folded chevron across the flank and alternating ribs banding
  the tail blade.
- Beak cream `#F7E9C8` (`BEAK_CREAM`), shade `#CEB88A`.
- Cream crepe-fringe rim `#FFF6DE` keylines the body, head, and the whole tail
  blade. At NIGHT the yellow/blue bands + cream beak + cream keyline are the
  high-value anchors that carry the silhouette out of the dark; the tail tip is
  fringe-scalloped (cream poms) so it never vanishes.

## Tail-wag frame map (`_WING_ANGLES = (50, 20, -10, -40)` → stage 0..3)
The tail is a horizontal pendulum; the head gives a small counter-bob. No wings,
no particles — the tail is the largest moving silhouette element.

| stage | wing° | tail sweep (deg from down, +right) | head bob (px, +down) |
|------:|------:|-----------------------------------:|---------------------:|
| 0     | 50    | +26 (swung RIGHT)                  | -1 (up)              |
| 1     | 20    | +4  (near centre)                  | 0                    |
| 2     | -10   | -26 (swung LEFT)                   | -1 (up)              |
| 3     | -40   | +4  (near centre)                  | +1 (down)            |

Loop reads right → centre → left → centre: a clean side-to-side wag. The blade
stays BOLD and wide (half-width ~9px, length 22px) so it doesn't mush at 40px,
and its alternating yellow/blue ribs read as a rhythmic light/dark ladder in
grayscale as it swings.

## 40px risk + mitigation
- **Tail mushing to a needle** → kept the blade fat and wide with a 2px cream
  keyline and a 3-pom fringe-scalloped tip; it survives as a pale-edged blade.
- **Head block lost against the body** → head set high-right with its own cream
  rim keyline; the bob is only ±1px so the red colour-block never drifts.
- **Beak reading flat (toucan risk)** → the upper mandible juts then hooks
  sharply DOWN past a short lower mandible, with a dark hook-tip notch and a
  cere nostril, so the hook curve is unmistakable even tiny.
- **Parcel occlusion** → tail pivots at y≈56 and sweeps around/behind where the
  parcel hangs; the body+beak read sits at/above centre, clear of the parcel.

## How it differs from the toucan and the flamingo
- **vs toucan:** the toucan's tell is a LONG FLAT beak. El Perico's beak is
  SHORT and HOOKED-DOWN — a fat parrot hook, not a flat blade — over a rounder,
  shorter head.
- **vs flamingo:** the flamingo's tell is LONG LEGS + a long curved neck. El
  Perico has NO long legs (only tiny tucked perch-claw nubs) and NO long neck;
  its long line is the SWINGING TAIL hanging below the body, not standing legs.
