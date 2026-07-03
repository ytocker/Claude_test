# AXOLOTL — Round 1 (5 explorations)

Concept: the smiling pink amphibian with a fan of feathery external gills.
Signature 40px tell across all five: the **gill-frill halo + dot-eyed smile** —
the only "headdress" in the roster. The flap is reinterpreted as a frilled
fin-stroke: gills sweep BACK on the down-pose (frame 0, wing 50°) and BLOOM
open on the up-pose (frame 3, wing -40°), like fronds pulsing through water.

Contract honoured: 64×84 SRCALPHA canvas, body mass at (32,44), head at
(44,34), ~24px top headroom for the halo, 4 poses over `_WING_ANGLES`, getter
via `_make_prebuilt_skin`, procedural only. Sheet shows each at hero 130px
(split DAY | NIGHT), 40px smooth, and 40px NEAREST x3 (level + dive) — the
honest gameplay read.

Palette anchor: #FFC8DD body / #FF7AA8 gill cores / #5A2A3E smile+eye dots /
#FFE8F0 belly highlight, varied per morph below.

---

## v1 — CLASSIC PINK
The canonical leucistic look. Six tidy feathery fronds (three per side) on a
plump body, tiny dot eyes + a small upturned-arc mouth, rosy cheeks.
- **40px tell:** clean pink halo of distinct fronds + the dot smile.
- **Weak spots:** the safest read; least "premium" of the five. Fronds can
  blur into a single mass at the very smallest scale — depends on the rim.

## v2 — BUSHY CORAL
Gills are dense bushy pom-pom clusters (overlapping blobs) instead of tidy
stalks; chunkier rounder body; big open happy mouth with a tongue.
- **40px tell:** a fluffy coral halo — the bushiest, most "plush toy" silhouette.
- **Weak spots:** the pom-poms read more like cotton candy than feathery gills
  up close; risk of looking like a different creature at hero scale.

## v3 — ANTLER LEUCISTIC
Gills branch like bold forking ANTLERS rather than soft feathers; crisp
near-white leucistic morph; wide cheerful grin.
- **40px tell:** the strongest branching-crown silhouette — unmistakable
  "headdress", great negative-space read against both skies.
- **Weak spots:** the white body needs the outline to survive the bright-day
  half; antlers can look more deer/coral than axolotl if pushed too hard.

## v4 — MELANOID DARK
Dark slate-plum morph where contrast is carried entirely by GLOWING magenta
gill cores + bright eyes, with a soft glow halo behind the frill.
- **40px tell:** neon frill + bright eyes on a dark silhouette — the "stealth"
  axolotl, pops hardest at night.
- **Weak spots:** the dark body can disappear against the night sky except for
  the neon — may read as just-a-frill; the glow is subtle at 40px.

## v5 — GOLDEN GILD
Golden-albino morph: warm gold body with iridophore sparkles; gills drawn as a
single broad SWEPT FEATHER-FAN per side (dark→core→highlight finny ridge) that
widens on the up-pose.
- **40px tell:** the gold body + coral fan; the most "premium / shiny" of the
  set, fan reads as a continuous fin rather than discrete stalks.
- **Weak spots:** the fan is less obviously "external gills" than v1/v3; gold
  body has lower contrast against the bright-day half than the pinks.

---

### Cross-cutting notes
- The gill cluster anchors just right-of head-centre (near HCX=44) on all five,
  consistent with the head sitting right of the body — keeps the body mass
  honestly centred at (32,44) for the fixed 14px collision circle.
- Down-pose vs up-pose bloom is clearest on v1/v4 (discrete fronds spreading)
  and v5 (fan widening); subtlest on v2 (pom-poms mostly translate, not spread).
- All five keep a permanent smile so the "shouldn't-fly amphibian" charm holds
  even in a steep dive frame.
