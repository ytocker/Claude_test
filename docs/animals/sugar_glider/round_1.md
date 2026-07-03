# Sugar Glider — Animal Store skin · Round 1

Five genuinely different takes on ONE new creature: a **sugar glider** —
a mammal that GLIDES on a wrist-to-ankle patagium membrane. The brand-new
silhouette for the set is the **flat kite** (limbs spread, membrane stretched
corner to corner) rather than the round-body/winged shape every other animal
skin uses. The glide cycle reinterprets the 4 wing poses: membrane TAUT and
wide on the down-pose (full glide), limbs TUCK in on the up-pose (mid-leap) —
the kite breathes between a wide diamond and a tighter dart instead of flapping.

Contract honoured: 64×84 SRCALPHA, body mass centred at (32,44), head near
(44,34), `_make_prebuilt_skin` getter per variant, procedural only, WHY-only
comments. Reviewed on BOTH a bright-day and a night sky (night-eyed creature
that must still pop in daylight).

Sheet: `docs/animals/sugar_glider/round_1.png`.

---

## V1 · CLASSIC GREY KITE
The textbook wild glider: broad **square** patagium kite, soft bluish-grey fur,
a single bold near-black **dorsal stripe nose-to-tail**, cream belly, big round
masked eyes, long balance tail.
- **40px tell:** the wide pale diamond + the dark stripe slicing down its centre
  + two eyes. The most literally "this is a gliding membrane" read.
- **Weak spots:** the stripe thins at 40px and competes with the kite's own
  shading; grey-on-grey body/membrane could use one more value step to separate
  the body mass from the membrane in motion.

## V2 · CARAMEL ROUNDED-WING
Warm caramel/tan morph with a **rounded leaf-shaped** membrane (smooth aerofoil,
no hard corners), soft rust stripe, extra-large cuddly eyes.
- **40px tell:** the warm blob silhouette + huge dark eyes + glowing cream
  belly. Distinct *colour* identity (only warm variant) reads instantly against
  blue day skies.
- **Weak spots:** the rounded membrane reads less obviously as a "glider kite"
  than the square versions — risks looking like a generic furry critter; the
  soft rust stripe nearly disappears at 40px so the silhouette must carry it.

## V3 · WHITE-FACED BOLD-STRIPE
High-contrast leucistic morph: cool white-grey fur, **white face**, a **thick
jet-black dorsal stripe that forks into a dramatic brow mask**, long dark-tipped
whip tail.
- **40px tell:** the single boldest stripe of the set + max-contrast white face
  framing the eyes. Punches hardest on bright-day skies.
- **Weak spots:** white body can wash out against pale/cloud day gradients
  (the outline saves it, but watch the belly-vs-membrane separation); the forked
  mask is busy — risks reading as "angry" rather than "cute" at hero size.

## V4 · TWILIGHT FLYING-SQUIRREL
Deep slate/charcoal night morph: the **membrane is body-colour**, so the SHAPE
(not a colour break) carries the kite, and the hero contrast is the **glowing
cream belly + two oversized glowing eyes** with a faint mint rim. Leading-edge
fur highlight keeps the kite outline legible on dark skies.
- **40px tell:** glowing eyes + bright belly punching out of a dark mass — the
  most "nocturnal creature" read; gorgeous on night skies.
- **Weak spots:** lowest contrast on the body itself — leans entirely on the
  outline + belly to separate from a dark sky; the dorsal stripe is essentially
  invisible here (intentional, but it sheds the concept's signature stripe tell).

## V5 · SCALLOPED-EDGE SHOWPIECE
Most graphically deliberate: **scalloped trailing membrane edge** (finger-strut
scoops, flying-squirrel style) + a contrasting **dark membrane rim** so the kite
outline is razor-sharp even on bright cloud. Warm grey-pink fur, bold stripe.
- **40px tell:** the dark-rimmed kite shape stays crisp at any scale + the bold
  stripe. The most "designed/premium" silhouette.
- **Weak spots:** the scallops nearly smooth out at 40px (the rim does the heavy
  lifting); the dark rim + dark stripe + dark mask risk over-darkening the read
  — could tip muddy if the art-director wants the fur lighter.

---

## Cross-cutting notes for the next round
- **Strongest 40px reads:** V3 (stripe/face contrast) and V4 (glowing eyes on
  dark body). **Most novel silhouette:** V1/V5 square kite. **Most distinct
  colour:** V2 caramel.
- **Shared risk:** grey-on-grey membrane-vs-body separation in the still 40px
  read; the leading-edge highlight (V4) is the cheapest fix and could be ported
  to V1/V3/V5 if the director wants more pop.
- **Stripe legibility** is the concept's named signature but is the first thing
  to thin at 40px on every grey variant — worth a director call on whether to
  fatten it everywhere or lean on the kite shape as the primary tell.
