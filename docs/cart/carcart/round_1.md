# KIDDIE CAR-CART — Round 1

The grocery-store "race car" cart kids drive: a chunky toy car nose stuck on
the front of a small basket. One bold two-mass silhouette + one wing-free tell.

## Read (the 40px verdict)

Two stacked filled masses, no wire:

- **FRONT, LOW:** a long rounded **car body** (capsule hull, candy-red) low to
  the ground on **two fat wheels**, topped by a **bubble glass cabin** with a
  red roof cap. A raised hood scoop + chrome bumper keyline mark the nose.
- **REAR, HIGH:** a small tapered **steel basket box** with a wire-mesh hint, a
  bright top rail, and a short push-handle poking up off the back.

The low-long-rounded car + the high rear box is a profile no tall open trolley
shares — the car nose reads as "toy car" before it reads "shopping," which is
the charm. All masses are FILLED (the safest grayscale build).

## Palette

- Car body candy-red `#E23B3B` / shade `#9C2424`, warm top sheen `#FF847A`.
- Bubble cabin glass `#BFE4F2` / shade `#84BAD2`, bright glint `#F5FCFF`.
- Basket steel `#9FB0BE` / shade `#6C7E8E`, rail keyline `#D6E2EA`.
- Wheels tyre `#2B3138` + rim keyline `#F4F6F8`, red toy hubcap `#E23B3B`.
- Headlight: off dim amber `#78602 8`-ish, on `#FFE278` with a hot `#FFFAE6`
  core and additive halo.

Day: red pops hard. Night: cabin glass glint + white wheel keyline + basket
rail keyline carry the silhouette; the red darkens but the keylines hold.

## Bounce frame map (the tell — NO wings, NO particles)

Driven from `_WING_ANGLES=(50,20,-10,-40)` → phase 0..3. The whole car body
(and the cabin riding on it) squashes/stretches ~2px and drops toward a FIXED
ground line, so the springs read as compressing. The headlight blinks ON at the
bottom of the squash, landing "down-bounce → flash" as one beat. The basket
bounces at HALF the car's drop so the two stacked masses read as separate.

| phase | wing° | body | drop | headlight |
|-------|-------|------|------|-----------|
| 0 | 50  | neutral             | 0     | off |
| 1 | 20  | SQUASH (−2h, +2w)   | +2 px | **ON (blink)** |
| 2 | -10 | neutral             | 0     | off |
| 3 | -40 | STRETCH (+2h, −1w)  | −1 px | off |

Because the tell is silhouette deformation (height/width + body-vs-ground gap),
it survives the grayscale strip, not just colour.

## 40px risk

- The basket is intentionally the smaller, secondary mass — at 40px it could
  flatten into the car's tail. Mitigated by the bright top rail keyline + the
  dark car/basket seam + the up-poking handle; if the art-director finds it
  reads as one blob, the basket can be nudged taller/back or the seam darkened.
- Two same-size fat wheels could merge with the low body at tiny scale; the
  white rim keyline + red hubcap keep them punched out on both skies and in
  grayscale.
- Headlight blink is a single-frame event — at speed it may read as a subtle
  twinkle rather than a clear beat; the silhouette squash is the primary tell
  and does not depend on it.

## Contract compliance

64×84 SRCALPHA; dominant mass centred at (BCX,BCY)=(32,44); wheels extend below
but the car/cabin body stays centred (Pip's parcel hangs just below centre and
reads as cargo under the car). `build(wing_angle_deg)->Surface`, upright with no
baked rotation; local `_make_prebuilt_skin` getter + `BUILDERS` registry mirror
`game/animal_ufo.py`. No wings, no live particles. Reuses `parrot._aaellipse`,
`_add_outline`, `_WING_ANGLES`.
