# PAPER PLANE redesign — concept CLASSIC DART · Round 2 (production build)

Converged single ship build of the art-director's round-1 winner **v3 ·
DEEP-KEEL RAZOR**. The 5-way exploration collapses to ONE production build with
the round-2 punch list folded in.

**Sheet:** `docs/animals/paper_plane_redesign/dart_classic/round_2.png`
**Build:** `docs/animals/paper_plane_redesign/dart_classic/dart_classic_skins.py`

## Contract held (liftable into game/animal_paper_plane.py)
- `build_dart_classic(wing_angle_deg) -> Surface` on a 64×84 SRCALPHA canvas,
  craft mass centred at (32, 44); collision is a fixed 14px circle there.
- **Nose points RIGHT (forward)** — drawn as-is, no host flip.
- `get_dart_classic = _make_prebuilt_skin(build_dart_classic)`.
- `BUILDERS = {"skin_dart_classic": get_dart_classic}`.
- No wings: the 4 base poses (`_WING_ANGLES=(50,20,-10,-40)`) drive a gentle
  bank-roll + nose-bob via `_flutter`/`_bank`, roll clamped at ±5.5°.
- Baked 1px self-rim from the alpha mask. Procedural only; both build targets
  green; WHY-only comments.

## Punch list — every note addressed
1. **Fuller trailing chord.** The upper wing's back edge now spans
   `tail_top (BCX-14, BCY-10)` → `crease_back (BCX-16, BCY+1)`, and the keel's
   trailing edge sits a touch lower at `keel_back (BCX-15, BCY+4)`, so the rear
   third carries real body (~4px at 40px) — v2's silhouette mass behind a still
   razor-sharp `nose (BCX+30, BCY-1)`. No more thread.
2. **Keel stays DARK; reads as a FOLD on night.** Keel is `(104,116,136)` →
   floor `(84,96,116)` (near-charcoal vs the bright `(248,250,253)` wing), so
   the value step — not the rim — is the fold. A single hard 1px LIGHTER inner
   lip `(150,162,182)` sits just below the crease (top edge of the keel),
   lifting the keel's upper edge so on a dark NIGHT sky it reads as a connected
   fold, not a detached wedge. Because the lip is baked geometry it's correct on
   day AND night with no runtime branch — honouring the single-build contract.
3. **Hard 1px crease.** The crease and the inner lip are drawn with `_hardline`
   (rounded ints, width 1, no AA) — a value step, never a ramp that greys out at
   40px.
4. **Pale-pillar day case verified.** The sheet's third panel renders the 40px
   reads over pale sandstone `(232,214,178)→(210,188,150)`. The dark keel
   carries the separation; the dart does NOT rely on the rim alone against the
   pillar.
5. **Forward read confirmed.** Across the level + dive (`-32°`) frames the
   bright upper facet + nose specular stay up-and-forward (nose-RIGHT); the dart
   never reads as nosing backward mid-flutter.
6. **Cool steel-paper only.** v4's double-fold and v5's warm-cream + pencil
   accent directions are dropped entirely.

## Render
Headless SDL-dummy. Hero 130px plus the 40px gameplay truth-test (level + dive,
smooth AND NEAREST x3) over three sky cases: open DAY, pale PILLAR (hardest day
case), and NIGHT / deep-NIGHT.

```
python docs/animals/paper_plane_redesign/dart_classic/_render_sheet.py
# wrote .../round_2.png (792, 546)
```

Not yet wired into `game/`. This is the final converged build; awaiting the
orchestrator's go to lift `build_dart_classic` / `get_dart_classic` into
`game/animal_paper_plane.py`.
