# Paper Plane redesign — STUNT / FIGHTER FOLD · Round 1

Concept: an angular hot-rod paper JET — the most DYNAMIC of the paper-plane
candidates. Where the current production skin is a calm dollar-bill GLIDER,
this concept leans into a swept-back delta, an aggressive pointed nose, and a
BOLD TWO-TONE LIVERY carried as STRUCTURE (not fussy detail), so it survives
the 40px downscale on day AND night.

Sheet: `round_1.png` — 5 takes + the current dart as the baseline to beat.
Each card: hero 130px (left); 40px NEAREST x3 level/dive on a DAY sky and a
NIGHT sky (right) — the honest gameplay read.

## Contract held
- `build_stunt_fold_v1..v5(wing_angle_deg) -> 64×84 SRCALPHA`, mass centred
  (32,44), fixed 14px collision circle there.
- NOSE POINTS RIGHT (forward) on every take.
- No wings — the 4 base poses (`_WING_ANGLES`) drive a snappy BANK/FLUTTER +
  nose-bob, clamped at `_ROLL_MAX = 7°` (a touch harder than the glider's
  5.5°, but never flattening the delta to a sliver).
- Getter via local `_make_prebuilt_skin`; `LABELS` + `BUILDERS` registry at
  the bottom for the eventual `skin_stunt_fold` lift.
- Procedural only; WHY-only comments; baked 1px self-rim on every frame.

## Shared family geometry
All five draw the SAME swept-delta hull (`_hull_pts` + `_draw_hull`): a bright
lit TOP facet vs a distinctly darker UNDER-fold meeting at a HARD keel crease.
Sweep + nose-reach + livery are the only differences, so the five read as one
fighter family with five paint jobs.

## The 5 takes
- **V1 · RED RACING STRIPE** — white wing, red keel stripe, sharp moderate
  delta. The livery IS the value spine (white/red/shadow). The crowd-pleaser.
- **V2 · NAVY + LIGHTNING** — deep-navy hull, electric-cyan lightning bolt,
  leanest/most-swept fighter, most aggressive nose. PALE rim so the dark hull
  holds on night sky. Bolt is one connected high-value streak.
- **V3 · BLACK + CHEVRON** — matte-stealth hull, fat orange forward-chevron
  band, plus a small CANARD foreplane breaking the nose outline.
- **V4 · BLUEPRINT ROUNDEL** — drafting-white facets, cyan ink leading edge +
  a CYAN ROUNDEL badge (livery as a BADGE, not a keel stripe), widest/most
  readable delta. The technical/collectible look.
- **V5 · RETRO '5' RACER** — warm cream hull, red nose cone + tail band, and a
  chunky race-NUMBER roundel. The number is a deliberate 40px legibility gamble
  drawn FAT. The most characterful/nostalgic take.

## Open questions for the art-director
- Which livery scheme reads hardest at 40px on BOTH skies — keel stripe (V1),
  energy streak (V2), banded chevron (V3), badge (V4), or numeral (V5)?
- Is the V5 "5" glyph surviving the downscale, or collapsing to a blob that
  should drop to a plain roundel?
- Sweep preference: lean fighter (V2) vs wide readable delta (V4)?
- Is the V3 canard adding stunt character or just noise at gameplay scale?
- Dark-hull legibility (V2/V3): is the pale self-rim enough on the day panel?
