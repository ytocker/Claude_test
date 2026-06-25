# Skeleton costume — v2 (parrot-anatomy pass)

The v1 winners **BONEWHITE** (design_1) and **DEADMAN'S FLAG** (design_4) read as
a generic skull+ribcage cluster, not a *parrot*. v2 keeps those two as unchanged
**reference columns** and explores **5 new designs** that all fix the same two
things and then branch into distinct themes.

## Mandatory anatomy (every new design) — shared via `tools/skeleton_candidates/_v2_anatomy.py`
1. **Hooked bone beak** — a big down-curved upper mandible + scooped lower
   mandible, bone-bright. This is THE tell that it's a *parrot* skeleton; it must
   read at ~40px, not be a small dark nub like the v1 beaks.
2. **Long spine-to-tail** — the vertebral spine runs skull → neck → torso and
   keeps going into a **long bony tail** (pygostyle + splayed tail-feather bones)
   so the skeleton is macaw-long, not stopped at the torso.
3. Bones are the brightest element; 2px minimum; legible on day AND night; a dark
   keyline rims the bone for the day-sky read.

The five designs differ only in palette + theme gear, layered via the shared
module's `pre`/`post` hooks so the parrot anatomy is identical across all five.

## The 5 designs (map to v2_design_1…5)

1. **BONEWHITE-MACAW** — evolves BONEWHITE. Pure white, anatomically-correct
   macaw skeleton; no theme gear. The definitive clean version.
   Palette: `#FFFFFF` bone · `#E4E7EE` under-edge · `#15161C` flesh · `#3A3D47`
   keyline.
2. **PIRATE-MACAW** — evolves DEADMAN'S FLAG. Red bandana wrapping the cranium,
   black eyepatch over the socket, gold hoop earring, steel cutlass slung across
   the back, X crossbones on the chest — on the corrected anatomy.
   Palette: `#F4EFE0` bone · `#C8202B` bandana · `#E8B23A` gold · `#B9C0C9` steel
   · `#1A1410` flesh.
3. **CALAVERA-MACAW** — Día de Muertos sugar-skull. Marigold petal crown spiking
   off the cranium, cyan-ringed eye sockets, magenta forehead heart, marigold
   scroll on the beak.
   Palette: `#FFFCEF` bone · `#FF961C` marigold · `#16C8D8` cyan · `#EC2E88`
   magenta · `#16121E` flesh.
4. **WISP-MACAW** — spectral ghost-fire. Glowing spectral-green bone, additive
   aura bloom (night flex), green flame-pip sockets; day-survivable via opaque
   core-green bone + dark keyline.
   Palette: `#C9FFE3` core bone · `#54F0A0` mid · `#19C8A6` aura · `#062019`
   keyline.
5. **AUREX-MACAW** — cursed gold-lich. Gilded gold bone (gold = brightest mass),
   two hot violet rune-fire socket points, a dark tattered mantle (a dark
   silhouette, not a violet glow), one gold coin at the feet, a gold crown band.
   Palette: `#FFE27A` gold · `#E0A21E` deep gold · `#B878FF` violet socket ·
   `#16121F` mantle.

## Loop notes
- References shown UNCHANGED (`design_1`/`design_4` builders) as the before/anchor
  columns; the 5 new are scratch builders `v2_design_N.py` on `_v2_anatomy.py`,
  never registered in `store_skins.BUILDERS`.
- art-director pass/fail includes the **parrot read** (hooked beak + full
  skeletal length) on top of the usual 40px-in-motion bar.
