"""
Alpine Haze sunset/sunrise study, v3 — 10 MULTI-HUE sunset→night moods.

The user loves the round-14 "Alpine Haze" DAY: a cool glacial-cyan day. v3 keeps
that day byte-for-byte but re-authors everything from golden hour onward.

Earlier v3 sunsets each held ONE dominant warm hue across the whole sunset and
merely darkened it (Row 1 all gold, Row 2 all blood-orange, …), which read flat.
THE NEW INTENT: each SUNSET TRAVELS THROUGH A FEW COLOURS — the canonical path is
"orange then red then purple" — not one held hue. A real clear-sky sunset stacks
warm at the horizon, rose/magenta in the mid, and violet/indigo up top; the same
palette migrates warm→cool as the sun sinks. We exploit BOTH axes, in three
arrangements spread across the set so the journeys stay distinct:

  (a) OVER-TIME SWEEP  — the dominant warm hue MIGRATES frame to frame: golden
      reads orange, sunset reads red/scarlet, the 0.56 dwell reads purple/magenta,
      then twilight falls into the dark starry night. The hue PATH OVER TIME is
      the row's identity.
  (b) TOP-TO-BOTTOM BANDS — at the peak sunset frame the single sky stacks a clear
      three-zone vertical gradient (orange horizon → red mid → purple top), then
      darkens as a unit over time.
  (c) BOTH — banded AND the bands migrate over time (the richest rows; the
      crossing seams are watched so no vertical sample greys).

The set spreads the three arrangements ~4/3/3 so the journeys stay distinct:
(a) over-time sweep = rows 1 Ember Gold, 4 Blood Scarlet, 6 Coral Blaze v2,
10 Sunfire Tangerine; (b) banded = rows 2 Blood Orange, 3 Scarlet Crimson,
7 Rose-Gold Twilight; (c) both = rows 5 Amethyst Nightfall, 8 Indigo & Fire,
9 Aurora Teal-Magenta. Row 4 (Blood Scarlet) is the ROW 2×3 CROSS — the Blood
Orange × Scarlet Crimson blend, seeded by averaging/interleaving their two
sunset override tables, then refined into an orange→scarlet over-time journey.

Whichever arrangement, the orange↔purple handoff is ALWAYS routed through a hot
rose/magenta bridge in the mid — the saturated midtone that keeps a purple-over-
orange column from greying to taupe through the middle.

Provably-identical DAY spine: the cool-cyan day anchors (0.06 / 0.18 / 0.30) are
authored ONCE in `_ALPINE_HAZE_KF` and copied verbatim into every design — they
are the identity anchor and never move. Everything else (golden → sunset → dusk
→ twilight → night → predawn → dawn → sunrise) is per-design, so each row gets
its own designed darken-into-night and its own flavoured dark night.

Night darkness comes from LOW palette RGB on the dusk/twilight/night/predawn
frames (0.62/0.68/0.72/0.80), NOT from per-design `SkyParams` — `zenith_dark`
stays shared so the day is never darkened.

Preview-only data. Nothing on the live render path imports this module — it is
reached solely through `tools/preview_sky_alpine_sunsets.py`. Pure-Pygame /
pygbag-safe (the keyframes are just colour tables; the OKLab bake lives in the
engine).
"""
from __future__ import annotations

from game.biome_sky import BiomeSpec, SkyParams


# ── the shared frame (DAY frozen; sunset→night→sunrise authored per design) ───
# Phase clock matches the calm sets so the preview columns line up:
#   morning 0.06 · midday 0.18 · afternoon 0.30 · golden 0.40 · sunset 0.50 ·
#   dusk 0.62 · twilight 0.68 · deep-night 0.72 · predawn 0.80 · dawn 0.88 ·
#   sunrise 0.94. `make_palette` wraps 0.94 -> 0.06 so the night side is
#   continuous.
#
# Only the three DAY frames (0.06/0.18/0.30) are SPINE — kept byte-for-byte on
# every variant; they are the loved cool glacial-cyan day and the v3 identity
# anchor. Every other frame is VARY (golden 0.40, sunset 0.50, dusk 0.62,
# twilight 0.68, deep-night 0.72, predawn 0.80, dawn 0.88, sunrise 0.94), and
# designs may additionally INSERT dwell frames at 0.44/0.56/0.68 (sunset→night)
# and 0.86/0.90 (sunrise) to grade the slow darken / lead-out. The spine's
# non-day frames below are only the fallback for rows that don't author them —
# in v3 every row authors its own night.
_ALPINE_HAZE_KF = [
    (0.06, dict(sky_top=(86, 158, 186),  sky_mid=(150, 192, 202), sky_bot=(196, 212, 210), horizon=(214, 218, 212), star_alpha=0)),   # SPINE morning  (FROZEN day)
    (0.18, dict(sky_top=(76, 168, 192),  sky_mid=(144, 198, 208), sky_bot=(196, 214, 212), horizon=(216, 220, 212), star_alpha=0)),   # SPINE midday   (FROZEN day)
    (0.30, dict(sky_top=(86, 160, 188),  sky_mid=(152, 192, 204), sky_bot=(198, 212, 208), horizon=(216, 218, 210), star_alpha=0)),   # SPINE afternoon(FROZEN day)
    (0.40, dict(sky_top=(88, 152, 178),  sky_mid=(156, 186, 196), sky_bot=(202, 208, 202), horizon=(220, 214, 204), star_alpha=0)),   # VARY golden
    (0.50, dict(sky_top=(74, 126, 160),  sky_mid=(146, 168, 184), sky_bot=(202, 200, 196), horizon=(230, 204, 184), star_alpha=12)),  # VARY sunset
    (0.62, dict(sky_top=(34, 76, 116),   sky_mid=(76, 126, 160),  sky_bot=(134, 172, 186), horizon=(190, 204, 200), star_alpha=80)),  # VARY dusk
    (0.68, dict(sky_top=(22, 52, 92),    sky_mid=(46, 96, 140),   sky_bot=(92, 150, 174),  horizon=(150, 188, 196), star_alpha=150)), # VARY twilight
    (0.72, dict(sky_top=(8, 28, 62),     sky_mid=(16, 64, 104),   sky_bot=(34, 104, 136),  horizon=(70, 144, 164),  star_alpha=210)), # VARY deep night
    (0.80, dict(sky_top=(12, 38, 78),    sky_mid=(26, 84, 124),   sky_bot=(54, 126, 156),  horizon=(108, 166, 186), star_alpha=130)), # VARY predawn
    (0.88, dict(sky_top=(76, 146, 176),  sky_mid=(140, 186, 200), sky_bot=(190, 210, 208), horizon=(214, 218, 210), star_alpha=20)),  # VARY dawn
    (0.94, dict(sky_top=(84, 156, 184),  sky_mid=(148, 192, 202), sky_bot=(196, 212, 210), horizon=(214, 218, 212), star_alpha=0)),   # VARY sunrise
]

# Shared bake params for all rows — keeps the grade placement identical too.
# zenith_dark stays SHARED (0.14): night darkness lives in the LOW palette RGB
# on 0.62/0.68/0.72/0.80, never in per-design SkyParams (that would also darken
# the loved day).
_ALPINE_SKY = SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.14)

# Fallback star_alpha for any INSERTED dwell frame a design doesn't author —
# interpolated from the slow-darken arc so star onset reads continuous:
#   golden 0.40 (0) → sunset 0.50 (12) → 0.56 → dusk 0.62 (80) → twilight 0.68
#   (150) → night 0.72 (210). 0.68 sits between dusk≈80 and night≈210.
_INSERT_STAR_ALPHA = {
    0.44: 5,    # between golden 0.40 (0) and sunset 0.50 (12)
    0.56: 30,   # between sunset 0.50 (12) and dusk 0.62 (80)
    0.68: 150,  # twilight dwell — between dusk 0.62 (80) and night 0.72 (210)
    0.86: 48,   # between predawn 0.80 (130) and dawn 0.88 (20) -> closer to dawn
    0.90: 13,   # between dawn 0.88 (20) and sunrise 0.94 (0)
}

# Phases a design is ALLOWED to override. DAY (0.06/0.18/0.30) is the only spine
# now; the whole sunset→night→sunrise arc is overridable so each row authors its
# own slow darken into its own dark, starry night.
_VARY_PHASES = {0.40, 0.50, 0.62, 0.68, 0.72, 0.80, 0.88, 0.94}
_INSERT_PHASES = {0.44, 0.56, 0.68, 0.86, 0.90}


# ── night-balanced retiming (study) ──────────────────────────────────────────
# The cycle's keyframe phases were lopsided: a long day + a long evening descent,
# then only ~26 s of genuinely-dark night (the lone 0.72 anchor) before predawn
# 0.80 already lifted toward dawn. This remaps every frame's PHASE — colours are
# untouched — onto a timeline where the dark, starry night HOLDS about as long as
# the sunset arc, and inserts a flat repeat of the night frame so the sky sits
# dark instead of immediately climbing back. Approx durations (×320 s cycle):
#   day ~74 s · evening descent ~93 s · dark night hold ~96 s · dawn ~57 s.
# Applied in `_compose`, so all 11 rows shift identically; ported to the live
# game/biome keyframes only once a design is chosen.
_RETIME = [
    (0.06, 0.04), (0.18, 0.12), (0.30, 0.20),                                    # day (compressed)
    (0.40, 0.27), (0.50, 0.37), (0.62, 0.47), (0.68, 0.52), (0.72, 0.56),        # descent -> night
    (0.80, 0.86), (0.88, 0.92), (0.94, 0.97),                                    # predawn -> dawn -> sunrise
]
_NIGHT_HOLD_PHASE = 0.82   # flat repeat of the 0.72 night frame — holds the dark


def _retime(ph):
    """Piecewise-linear remap of an old keyframe phase onto the balanced timeline."""
    a = _RETIME
    if ph <= a[0][0]:
        return a[0][1]
    if ph >= a[-1][0]:
        (o0, n0), (o1, n1) = a[-2], a[-1]
        return n1 + (ph - o1) * (n1 - n0) / (o1 - o0)
    for (o0, n0), (o1, n1) in zip(a, a[1:]):
        if o0 <= ph <= o1:
            return n0 + (ph - o0) * (n1 - n0) / (o1 - o0)
    return ph



def _compose(overrides: dict) -> list:
    """Clone the frozen day + spine and apply a design's sunset→night→sunrise.

    `overrides` maps phase -> dict(sky_top/mid/bot/horizon[, star_alpha]). For a
    VARY phase we replace the four RGB keys; an override MAY also carry its own
    `star_alpha` (so a design can make its night "full of stars" and time star
    emergence through dusk/twilight) — if absent we keep the spine's value. For
    an INSERT phase we add a new dwell frame; it likewise uses an authored
    `star_alpha` if given, else the interpolated `_INSERT_STAR_ALPHA` fallback.
    The three DAY anchors are never overridable and pass through verbatim —
    that is what guarantees the loved cool-cyan day is identical with zero
    hand-transcription."""
    by_phase = {ph: dict(d) for ph, d in _ALPINE_HAZE_KF}
    for ph, rgb in overrides.items():
        assert ph in _VARY_PHASES or ph in _INSERT_PHASES, f"phase {ph} is not overridable"
        frame = dict(rgb)
        if 'star_alpha' in rgb:
            # Design authored its own star alpha for this frame — honour it.
            frame['star_alpha'] = rgb['star_alpha']
        elif ph in by_phase:
            # VARY without an authored alpha: keep the spine's star_alpha.
            frame['star_alpha'] = by_phase[ph]['star_alpha']
        else:
            # INSERT without an authored alpha: interpolated fallback.
            frame['star_alpha'] = _INSERT_STAR_ALPHA[ph]
        by_phase[ph] = frame
    # Remap every frame onto the night-balanced timeline (colours unchanged) and
    # add the flat dark hold so the night sits dark rather than climbing at once.
    out = [(round(_retime(ph), 4), pal) for ph, pal in sorted(by_phase.items())]
    night = by_phase.get(0.72)
    if night is not None:
        out.append((_NIGHT_HOLD_PHASE, dict(night)))
    out.sort(key=lambda kv: kv[0])
    return out


def _spec(name, note, overrides):
    return BiomeSpec(name=name, note=note, keyframes=_compose(overrides), sky=_ALPINE_SKY)


# ── the 10 MULTI-HUE sunset→night moods (frozen cool-cyan day under every one) ─
# Authoring discipline shared by all rows (v3):
#   * DAY (0.06/0.18/0.30): the untouched cool glacial-cyan day — frozen,
#     byte-for-byte identical across every row. Never warmed, never darkened.
#   * SUNSET (golden 0.40 / sunset 0.50, with 0.44/0.56 dwell): the astonishing
#     half, and now a JOURNEY THROUGH A FEW COLOURS rather than one held hue. A
#     row reaches its multi-hue character one of three ways (noted per row, and
#     spread ~4/3/3 across the set so the journeys stay distinct):
#       (a) over-time sweep — the dominant warm hue MIGRATES frame to frame
#           (orange@0.40 → red@0.50 → purple/magenta@0.56), the hue PATH being the
#           identity; the per-frame vertical gradient stays fairly tight.
#       (b) top-to-bottom bands — at the peak sunset frame ONE sky stacks a clear
#           orange horizon → red mid → purple top, then darkens as a unit.
#       (c) both — banded AND the bands migrate over time (richest; watch seams).
#     Either way the sky is WARM-led and DARKENING (not cyan-topped); the top is
#     free to go deep violet / indigo. The orange↔purple handoff is ALWAYS bridged
#     by a hot rose/magenta MID so no vertical sample greys to taupe/olive.
#   * DUSK → TWILIGHT → NIGHT (0.62 / 0.68 / 0.72, then predawn 0.80): a DESIGNED
#     slow smoothstep darken — golden→sunset→0.56→dusk→twilight→night, not one
#     fast snap. RGB deepens toward a near-black FLAVOURED tint (each row its own:
#     bronze-indigo, wine, oxblood, plum, indigo, teal-navy, mauve-navy, …) but
#     all genuinely DARK. star_alpha rises monotonically and stars EMERGE through
#     twilight: ~80 at dusk → ~150 at twilight → ~230-240 at deep night, so each
#     night reads "full of stars". Predawn 0.80 holds the dark, starry night as
#     the lead-out before dawn.
#   * SUNRISE (dawn 0.88 / sunrise 0.94, with optional 0.86/0.90 lead-out): RICH,
#     never pale. Designer's discretion per row on calm-vs-bold, but invest real
#     colour — and keep it a genuinely DIFFERENT moment from that row's sunset
#     (a clearer, fresher hue family, not a tired echo of the dusk).
#
# Clean, saturated hues only — cyan→warm and the orange→purple mid are routed
# through saturated rose/magenta so no vertical sample greys to a muddy taupe/
# olive seam. Each row's NIGHT sky_top VALUE is clearly darker than its own
# SUNSET sky_top.


# 1. Ember Gold — ARRANGEMENT (a) OVER-TIME SWEEP. The whole-sky hue MIGRATES
#    over time: golden gold → sunset scarlet-ember → 0.56 plum-magenta, then falls
#    to a deep bronze-indigo starry night. Sunrise: a rich warm amber-rose dawn.
EMBER_GOLD = _spec(
    'Ember Gold',
    'SUNSET [a · over-time sweep, multi-hue]: gold→orange→plum TRAVELS over time AND stacks vertically — golden 0.40 reads molten GOLD; by sunset 0.50 the horizon rotates BURNT-ORANGE and a CORAL-RED pushes into the MID; by the 0.56 dwell VIOLET bleeds into the TOP, so a dusk column reads gold/ember horizon → coral mid → violet top. WARM and DARKENING throughout. NIGHT: a deep bronze-indigo near-black, star_alpha peaks ~236. SUNRISE: a rich warm amber-rose dawn, never pale.',
    {
        # SUNSET (a) over-time sweep — REWORKED so it is unmistakably MULTI-HUE on
        # both axes (the round-1 row read mono gold with only a value-darken). golden
        # 0.40 is now PURE molten gold (top warmed off taupe so even golden hour is
        # gold, not grey); by sunset 0.50 the horizon has swept to a deep BURNT-ORANGE
        # while a saturated CORAL-RED owns the MID band and a clear VIOLET has entered
        # the TOP; by the 0.56 dwell the TOP is full PLUM-VIOLET, the mid coral-rose,
        # the horizon ember-orange — so a vertical dusk sample reads gold/ember horizon
        # → coral mid → violet top, AND across columns the dominant hue travels
        # gold→orange→plum. The coral-red mid is the saturated bridge that keeps the
        # gold→violet column from greying to taupe.
        0.40: dict(sky_top=(124, 96, 70),   sky_mid=(244, 174, 78),  sky_bot=(255, 192, 64),  horizon=(255, 150, 36)),
        0.44: dict(sky_top=(104, 70, 96),   sky_mid=(238, 138, 86),  sky_bot=(255, 168, 54),  horizon=(252, 110, 32)),
        0.50: dict(sky_top=(82, 48, 116),   sky_mid=(232, 94, 90),   sky_bot=(252, 134, 50),  horizon=(238, 80, 30)),
        0.56: dict(sky_top=(78, 40, 124),   sky_mid=(210, 72, 116),  sky_bot=(230, 92, 70),   horizon=(218, 66, 48)),
        # DUSK→TWILIGHT→NIGHT — slow darken into bronze-indigo; a warm ember holds
        # at the base while the top sinks to near-black indigo. Stars emerge.
        0.62: dict(sky_top=(38, 28, 70),   sky_mid=(126, 70, 90),   sky_bot=(184, 108, 64),  horizon=(210, 96, 44),  star_alpha=88),
        0.68: dict(sky_top=(26, 20, 54),   sky_mid=(78, 48, 72),    sky_bot=(124, 78, 64),   horizon=(160, 88, 50),  star_alpha=156),
        0.72: dict(sky_top=(12, 12, 30),   sky_mid=(30, 26, 48),    sky_bot=(56, 46, 56),    horizon=(96, 64, 48),   star_alpha=236),
        0.80: dict(sky_top=(16, 16, 38),   sky_mid=(36, 34, 58),    sky_bot=(64, 56, 64),    horizon=(102, 76, 58),  star_alpha=168),
        # SUNRISE — rich warm amber-rose; clearer and fresher than the dusk fire,
        # full real colour (never pale), the top lifting back toward day.
        0.88: dict(sky_top=(72, 110, 150), sky_mid=(220, 158, 134), sky_bot=(255, 178, 132), horizon=(255, 168, 110)),
        0.94: dict(sky_top=(82, 138, 172), sky_mid=(228, 178, 158), sky_bot=(255, 192, 150), horizon=(255, 182, 132)),
    },
)


# 2. Blood Orange — ARRANGEMENT (b) TOP-TO-BOTTOM BANDS. At the peak sunset the
#    one sky stacks a deliberate three-zone vertical gradient: ORANGE horizon →
#    RED mid → deep VIOLET top, then darkens as a unit into a wine-dark starry
#    night. Sunrise: a fresh peach-and-rose dawn.
BLOOD_ORANGE = _spec(
    'Blood Orange',
    'SUNSET [b · top-to-bottom bands]: ONE banded sky — a blood-orange (H18) horizon, a hot rose-red mid bridge, and a deep wine-VIOLET top, stacked as a clear three-zone gradient that then darkens as a unit. NIGHT: a wine-dark near-black that joins the dark family — the wine survives only as a LOW horizon glow, star_alpha peaks ~234. SUNRISE: a fresh peach-and-rose dawn, full colour.',
    {
        # SUNSET (b) banded — a DELIBERATE three-zone vertical stack held across the
        # peak: blood-orange horizon, a hot rose-red mid (the saturated bridge that
        # keeps the orange→violet column from greying through the middle), and a
        # deep wine-violet top. The whole stack then darkens as a UNIT over time —
        # the bands stay put, the values fall. sky_top violet leads R≈B over G so it
        # never reads slate; horizon stays pure orange; the mid carries real red.
        0.40: dict(sky_top=(84, 52, 112),  sky_mid=(214, 96, 110),  sky_bot=(250, 124, 56),  horizon=(255, 118, 40)),
        0.44: dict(sky_top=(76, 46, 104),  sky_mid=(214, 84, 100),  sky_bot=(248, 110, 48),  horizon=(250, 98, 34)),
        0.50: dict(sky_top=(66, 40, 96),   sky_mid=(212, 72, 92),   sky_bot=(244, 96, 42),   horizon=(240, 76, 32)),
        0.56: dict(sky_top=(54, 34, 80),   sky_mid=(192, 66, 86),   sky_bot=(226, 86, 46),   horizon=(218, 64, 34)),
        # DUSK→TWILIGHT→NIGHT — slow fall into wine-dark; deep maroon-violet. The
        # night (0.72) value is dropped ~15-20% across mid/bot/horizon so it joins
        # rows 1/3/8 in the dark family — the wine no longer washes the whole sky
        # as a brighter blue-hour, it survives ONLY as a low horizon glow while
        # the mid/top sink to near-black. 0.80 lead-out held equally dark.
        0.62: dict(sky_top=(34, 20, 44),   sky_mid=(112, 48, 60),   sky_bot=(158, 62, 50),   horizon=(184, 58, 42),  star_alpha=86),
        0.68: dict(sky_top=(22, 12, 36),   sky_mid=(60, 28, 44),    sky_bot=(94, 42, 44),    horizon=(130, 52, 44),  star_alpha=154),
        0.72: dict(sky_top=(8, 4, 18),     sky_mid=(20, 10, 24),    sky_bot=(34, 16, 26),    horizon=(64, 28, 32),   star_alpha=234),
        0.80: dict(sky_top=(10, 6, 22),    sky_mid=(24, 12, 28),    sky_bot=(40, 20, 30),    horizon=(72, 34, 36),   star_alpha=166),
        # SUNRISE — fresh peach over a rose horizon; clearer than the blood dusk.
        # Carries REAL saturation into sunrise (rose horizon and peach base given
        # fuller chroma) so it reads saturated-SOFT, never a pale whisper.
        0.88: dict(sky_top=(72, 116, 156), sky_mid=(232, 158, 140), sky_bot=(255, 168, 132), horizon=(255, 146, 112)),
        0.94: dict(sky_top=(82, 142, 176), sky_mid=(240, 176, 158), sky_bot=(255, 182, 146), horizon=(255, 160, 130)),
    },
)


# 3. Scarlet Crimson — ARRANGEMENT (b) TOP-TO-BOTTOM BANDS. The hottest banded
#    sky of the set: SCARLET horizon → smouldering CRIMSON mid → deep oxblood-
#    INDIGO top, stacked clearly then darkening as a unit into a near-black indigo
#    night. Sunrise: a clean rose-pink dawn (cooler, fresher than the dusk).
SCARLET_CRIMSON = _spec(
    'Scarlet Crimson',
    'SUNSET [b · top-to-bottom bands]: ONE banded sky — a scarlet (H4) horizon, a smouldering crimson mid, and a deep oxblood-INDIGO top, the hottest red of the set stacked as a clear three-zone gradient that darkens as a unit. NIGHT: an oxblood that sinks to near-black indigo, star_alpha peaks ~238. SUNRISE: a clean rose-pink dawn, fresher than the fiery dusk.',
    {
        # SUNSET (b) banded — a deliberate vertical stack: scarlet horizon, a
        # smouldering crimson mid (carries the saturated red bridge), and a deep
        # oxblood-indigo top. The top leans indigo (B≳R, both over G) so the
        # scarlet→top column resolves through crimson, never greys; the stack
        # darkens as a UNIT over time, bands fixed, values falling.
        0.40: dict(sky_top=(64, 36, 96),   sky_mid=(206, 52, 84),   sky_bot=(236, 64, 52),   horizon=(232, 40, 36)),
        0.44: dict(sky_top=(56, 32, 88),   sky_mid=(206, 46, 80),   sky_bot=(234, 56, 48),   horizon=(222, 34, 34)),
        0.50: dict(sky_top=(50, 28, 78),   sky_mid=(206, 40, 78),   sky_bot=(230, 48, 44),   horizon=(210, 28, 32)),
        0.56: dict(sky_top=(44, 26, 66),   sky_mid=(186, 40, 78),   sky_bot=(212, 48, 46),   horizon=(192, 30, 36)),
        # DUSK→TWILIGHT→NIGHT — oxblood deepening to near-black indigo.
        0.62: dict(sky_top=(36, 18, 48),   sky_mid=(128, 38, 70),   sky_bot=(160, 50, 56),   horizon=(176, 44, 48),  star_alpha=90),
        0.68: dict(sky_top=(26, 14, 42),   sky_mid=(74, 28, 54),    sky_bot=(104, 40, 52),   horizon=(130, 46, 52),  star_alpha=158),
        0.72: dict(sky_top=(12, 8, 24),    sky_mid=(32, 14, 32),    sky_bot=(52, 22, 38),    horizon=(78, 34, 44),   star_alpha=238),
        0.80: dict(sky_top=(16, 10, 30),   sky_mid=(38, 20, 40),    sky_bot=(58, 30, 44),    horizon=(86, 42, 50),   star_alpha=168),
        # SUNRISE — clean rose-pink, cooler and fresher than the scarlet dusk.
        0.88: dict(sky_top=(76, 124, 160), sky_mid=(224, 158, 168), sky_bot=(252, 168, 168), horizon=(255, 154, 152)),
        0.94: dict(sky_top=(86, 146, 176), sky_mid=(232, 176, 184), sky_bot=(252, 184, 182), horizon=(255, 168, 168)),
    },
)


# 4. Blood Scarlet — the ROW 2 × ROW 3 CROSS (Blood Orange × Scarlet Crimson),
#    seeded by averaging/interleaving their two sunset override tables then refined
#    into ARRANGEMENT (a) OVER-TIME SWEEP: golden reads blood-ORANGE (row 2's
#    horizon), sunset migrates to SCARLET (row 3's red), the 0.56 dwell tips into
#    crimson-oxblood — an orange→scarlet journey over time. → deep oxblood-wine
#    starry night. Sunrise: a fresh peach-rose dawn.
BLOOD_SCARLET = _spec(
    'Blood Scarlet',
    'SUNSET [a · over-time sweep · ROW 2×3 CROSS]: the Blood Orange × Scarlet Crimson blend — golden 0.40 reads blood-ORANGE, sunset 0.50 migrates to hot SCARLET, the 0.56 dwell tips CRIMSON-oxblood. The orange→scarlet hue PATH over time is the identity. NIGHT: a deep oxblood-wine near-black, star_alpha peaks ~236. SUNRISE: a fresh peach-rose dawn, full colour.',
    {
        # SUNSET (a) over-time sweep — SEEDED by averaging row 2 (Blood Orange) and
        # row 3 (Scarlet Crimson), then refined to SHARPEN THE CROSS so it doesn't
        # read as a third interpolation step between 2 and 3. The CROSS identity is
        # the warm-bottom/cool-top SPREAD: the horizon is given a slightly ORANGER
        # cast than row 3's scarlet (more green in the warm end → a blood-orange that
        # has caught fire, not a pure scarlet), AND the top is pushed slightly more
        # PURPLE than row 2's wine (more blue up top → a deeper violet), so a vertical
        # sample crosses oranger-warm → more-violet-cool than either parent. The whole
        # sky still migrates orange→scarlet over time; the mid holds a hot rose-red
        # bridge so the warm→violet column never greys.
        0.40: dict(sky_top=(76, 42, 116),  sky_mid=(212, 82, 96),   sky_bot=(246, 106, 50),  horizon=(252, 104, 40)),
        0.44: dict(sky_top=(68, 38, 108),  sky_mid=(212, 64, 86),   sky_bot=(244, 90, 46),   horizon=(244, 78, 34)),
        0.50: dict(sky_top=(60, 32, 98),   sky_mid=(212, 52, 82),   sky_bot=(240, 76, 42),   horizon=(232, 60, 32)),
        0.56: dict(sky_top=(50, 28, 82),   sky_mid=(192, 48, 80),   sky_bot=(220, 68, 44),   horizon=(208, 50, 36)),
        # DUSK→TWILIGHT→NIGHT — oxblood-wine deepening to near-black; the average of
        # the two parents' nights, a touch warmer than row 3's pure indigo so the
        # cross reads as its own flavour. Stars emerge.
        0.62: dict(sky_top=(36, 20, 48),   sky_mid=(122, 44, 66),   sky_bot=(160, 56, 52),   horizon=(182, 50, 44),  star_alpha=88),
        0.68: dict(sky_top=(24, 14, 38),   sky_mid=(68, 28, 50),    sky_bot=(100, 42, 48),   horizon=(132, 50, 48),  star_alpha=156),
        0.72: dict(sky_top=(10, 6, 20),    sky_mid=(28, 12, 28),    sky_bot=(46, 20, 32),    horizon=(72, 32, 38),   star_alpha=236),
        0.80: dict(sky_top=(14, 8, 26),    sky_mid=(34, 18, 34),    sky_bot=(54, 28, 38),    horizon=(80, 38, 44),   star_alpha=168),
        # SUNRISE — a fresh peach-rose; clearer and cooler than the fiery dusk, the
        # two parents' dawns averaged into a saturated-soft morning, never pale.
        0.88: dict(sky_top=(74, 120, 158), sky_mid=(228, 158, 154), sky_bot=(255, 168, 150), horizon=(255, 150, 132)),
        0.94: dict(sky_top=(84, 144, 176), sky_mid=(236, 176, 172), sky_bot=(255, 184, 164), horizon=(255, 164, 148)),
    },
)


# 5. Amethyst Nightfall — ARRANGEMENT (c) BOTH (banded AND migrating). At golden
#    the sky is a clear jewel-rose horizon → magenta mid → amethyst-VIOLET top
#    band stack; over time those bands BOTH darken AND climb — the rose recedes,
#    the violet floods down — so the banded sky also sweeps cooler frame to frame.
#    → deep indigo starry night. Sunrise: a rich rose-violet dawn (fresher, lighter).
AMETHYST_NIGHTFALL = _spec(
    'Amethyst Nightfall',
    'SUNSET [c · both — banded AND migrating]: a banded jewel sky (rose H338 horizon → magenta mid → amethyst-VIOLET H280 top) whose bands ALSO sweep over time — the rose horizon recedes and the violet floods downward frame to frame, so it is banded at every step yet travelling rose→violet as it darkens. NIGHT: a deep indigo near-black, star_alpha peaks ~238. SUNRISE: a rich rose-violet dawn — the jewel family reborn fresher and lighter.',
    {
        # SUNSET (c) both — at 0.40 a clear three-band stack: jewel-rose horizon,
        # magenta mid (the saturated bridge), amethyst-violet top. Frame to frame
        # the bands BOTH darken AND migrate: the rose horizon cools toward magenta
        # and the violet top floods down, so the column stays banded while the
        # whole stack sweeps rose→violet over time. No grey — the mid is always a
        # saturated magenta between the rose and violet.
        0.40: dict(sky_top=(70, 50, 122),  sky_mid=(160, 70, 178),  sky_bot=(206, 70, 168),  horizon=(240, 84, 138)),
        0.44: dict(sky_top=(62, 44, 116),  sky_mid=(150, 62, 176),  sky_bot=(196, 60, 160),  horizon=(236, 68, 132)),
        0.50: dict(sky_top=(54, 38, 106),  sky_mid=(138, 56, 172),  sky_bot=(182, 54, 152),  horizon=(228, 54, 126)),
        0.56: dict(sky_top=(46, 34, 92),   sky_mid=(116, 52, 156),  sky_bot=(160, 54, 140),  horizon=(208, 52, 124)),
        # DUSK→TWILIGHT→NIGHT — indigo deepening to near-black. The night is
        # nudged decisively COOLER (a true deep-indigo lean: blue clearly leads,
        # red pulled well down) so it is unmistakably separate from the warmer
        # oxblood/plum nights of the red rows at 0.72 — the cool indigo is this
        # row's own flavoured near-black.
        # Dusk (0.62) mid held a touch MORE SATURATED (a cleaner violet-magenta, red
        # nudged up, green pulled down) so where it meets the mountain silhouette at
        # this one phase it never edges to a muddy plum-grey seam.
        0.62: dict(sky_top=(28, 24, 90),   sky_mid=(66, 46, 150),   sky_bot=(110, 56, 156),  horizon=(172, 54, 132),  star_alpha=88),
        0.68: dict(sky_top=(18, 20, 70),   sky_mid=(36, 36, 106),   sky_bot=(62, 46, 116),   horizon=(112, 54, 112),  star_alpha=156),
        0.72: dict(sky_top=(6, 8, 42),     sky_mid=(14, 18, 64),    sky_bot=(26, 28, 78),    horizon=(46, 40, 90),    star_alpha=238),
        0.80: dict(sky_top=(8, 12, 48),    sky_mid=(18, 24, 70),    sky_bot=(32, 34, 84),    horizon=(56, 48, 98),    star_alpha=168),
        # SUNRISE — rich rose-violet reborn; fresher, lighter, clearly distinct.
        0.88: dict(sky_top=(78, 132, 168), sky_mid=(190, 158, 210), sky_bot=(228, 168, 204), horizon=(248, 158, 184)),
        0.94: dict(sky_top=(86, 148, 178), sky_mid=(200, 178, 216), sky_bot=(234, 182, 210), horizon=(250, 172, 192)),
    },
)


# 6. Coral Blaze v2 — ARRANGEMENT (a) OVER-TIME SWEEP. The reborn reef glow now
#    TRAVELS over time: golden reads warm CORAL, sunset cools to a deep ROSE, the
#    0.56 dwell tips dusky PLUM-magenta. → deep warm-navy (plum-indigo) star-rich
#    night. Sunrise: a fresh coral-cream dawn (the loved coral reborn, clearer).
CORAL_BLAZE_V2 = _spec(
    'Coral Blaze v2',
    'SUNSET [a · over-time sweep]: the reef glow TRAVELS — golden 0.40 reads warm CORAL (H14), sunset 0.50 cools to a deep ROSE, the 0.56 dwell tips dusky PLUM-magenta. The coral→rose→plum path over time is the identity. NIGHT: a deep warm-navy (plum-indigo) near-black, star_alpha peaks ~234. SUNRISE: a fresh coral-cream dawn, the coral reborn clearer and lighter than the dusk.',
    {
        # SUNSET (a) over-time sweep — the WHOLE sky migrates coral→rose→plum over
        # time: golden 0.40 is warm salmon-coral, by sunset 0.50 the bloom has
        # cooled to a deep rose, and the 0.56 dwell tips dusky plum-magenta as the
        # top deepens. Each frame stays one hue FAMILY; the JOURNEY is over time.
        # The rose-plum only arrives once the coral has cooled, so no taupe seam.
        # The horizon line carries a thin SATURATED EMBER/CORAL bridge at every warm
        # frame so this cool-leaning row still reads as a SUNSET's few-colour journey
        # (a hot ember kissing the ridge), never an early blue-hour twilight — the
        # horizon is given fuller chroma (a brighter, redder coral-ember) than the
        # cooler rose mid above it, keeping the warm story alive at the base.
        0.40: dict(sky_top=(96, 76, 100),  sky_mid=(244, 124, 124), sky_bot=(255, 150, 116), horizon=(255, 100, 64)),
        0.44: dict(sky_top=(84, 64, 94),   sky_mid=(246, 110, 118), sky_bot=(255, 138, 104), horizon=(255, 86, 54)),
        0.50: dict(sky_top=(70, 52, 84),   sky_mid=(238, 96, 124),  sky_bot=(252, 120, 100), horizon=(252, 76, 58)),
        0.56: dict(sky_top=(58, 42, 78),   sky_mid=(204, 80, 120),  sky_bot=(228, 96, 102),  horizon=(226, 64, 66)),
        # DUSK→TWILIGHT→NIGHT — the v2 cyan-top survivor is fully killed: the
        # upper-mid band now descends through a WARM plum-navy (red-leaning, blue
        # pulled down so it never reads teal), with the coral/salmon kept hot and
        # high at the horizon so the whole evening darkens warm like Row 3. Stars
        # emerge. (Pushed warmer and dimmer than r1 so it is NOT the row nearest
        # the cool reference baseline.)
        0.62: dict(sky_top=(46, 26, 54),   sky_mid=(154, 70, 80),   sky_bot=(204, 100, 82),  horizon=(228, 92, 60),  star_alpha=86),
        0.68: dict(sky_top=(34, 18, 42),   sky_mid=(98, 46, 56),    sky_bot=(140, 70, 62),   horizon=(180, 82, 54),  star_alpha=154),
        0.72: dict(sky_top=(12, 8, 24),    sky_mid=(34, 20, 36),    sky_bot=(60, 34, 44),    horizon=(98, 56, 46),   star_alpha=234),
        0.80: dict(sky_top=(14, 10, 28),   sky_mid=(40, 24, 42),    sky_bot=(66, 40, 50),    horizon=(106, 64, 50),  star_alpha=166),
        # SUNRISE — fresh coral-cream; the reef glow reborn clear and lighter.
        0.88: dict(sky_top=(76, 124, 158), sky_mid=(244, 168, 152), sky_bot=(255, 184, 158), horizon=(255, 166, 130)),
        0.94: dict(sky_top=(86, 146, 176), sky_mid=(248, 186, 172), sky_bot=(255, 196, 172), horizon=(255, 178, 150)),
    },
)


# 7. Rose-Gold Twilight — ARRANGEMENT (b) TOP-TO-BOTTOM BANDS. The opulent
#    three-band stack: a rich GOLD horizon → hot-PINK mid → deep mauve-VIOLET top,
#    gold-below / pink-mid / violet-above, held across the peak then darkening as
#    a unit. → dusky mauve-navy night. Sunrise: a quiet warm blush-gold dawn.
ROSE_GOLD_TWILIGHT = _spec(
    'Rose-Gold Twilight',
    'SUNSET [b · top-to-bottom bands]: ONE opulent banded sky — a rich gold (H42) horizon, a hot-pink (H335) mid band, and a deep mauve-VIOLET top, gold-below / pink-mid / violet-above, stacked as a clear three-zone gradient that darkens as a unit. NIGHT: a dusky mauve-navy near-black, star_alpha peaks ~234. SUNRISE: a quiet warm blush-gold dawn, soft but with real colour — never pale.',
    {
        # SUNSET (b) banded — row 7 now OWNS the DESATURATED DUSTY-ROSE identity (its
        # separator from the hot rows 8/9): a soft rose-gold horizon, a muted
        # MAUVE-ROSE mid (chroma pulled well down from a hot pink — R and B closer,
        # greyer), and a dusty plum top. Still a clear three-zone band stack that
        # darkens as a unit, but the whole mood is the quiet, powdery dusty-rose
        # option rather than the electric magenta of row 8 or the tangerine of 9.
        0.40: dict(sky_top=(86, 66, 116),  sky_mid=(214, 124, 164), sky_bot=(238, 152, 130), horizon=(248, 168, 110)),
        0.44: dict(sky_top=(76, 58, 108),  sky_mid=(206, 112, 156), sky_bot=(230, 138, 116), horizon=(242, 152, 98)),
        0.50: dict(sky_top=(66, 50, 98),   sky_mid=(198, 102, 150), sky_bot=(222, 126, 104), horizon=(234, 140, 88)),
        0.56: dict(sky_top=(56, 44, 86),   sky_mid=(172, 92, 134),  sky_bot=(198, 112, 96),  horizon=(212, 124, 84)),
        # DUSK→TWILIGHT→NIGHT — mauve-navy deepening to near-black. The dusk (0.62)
        # mid is held MORE SATURATED still (a clear rose-mauve, red lifted and green
        # pulled down, not a plum-grey) so where the violet mid meets the mountain
        # silhouette at this one phase it never edges to muddy plum-grey — it stays a
        # dusty-rose evening.
        0.62: dict(sky_top=(40, 28, 64),   sky_mid=(148, 62, 120),  sky_bot=(190, 92, 112),  horizon=(218, 118, 74),  star_alpha=86),
        0.68: dict(sky_top=(28, 20, 54),   sky_mid=(80, 44, 84),    sky_bot=(120, 62, 84),   horizon=(162, 88, 62),   star_alpha=154),
        0.72: dict(sky_top=(12, 10, 32),   sky_mid=(30, 20, 50),    sky_bot=(54, 32, 56),    horizon=(90, 56, 50),    star_alpha=234),
        0.80: dict(sky_top=(16, 12, 38),   sky_mid=(36, 24, 56),    sky_bot=(60, 38, 62),    horizon=(98, 64, 56),    star_alpha=166),
        # SUNRISE — quiet warm blush-gold; soft but real colour, fresher hue.
        # Saturation carried into sunrise (blush mid and gold horizon given fuller
        # chroma) so "quiet" reads saturated-SOFT, never pale.
        0.88: dict(sky_top=(74, 128, 164), sky_mid=(238, 164, 162), sky_bot=(255, 182, 144), horizon=(255, 170, 116)),
        0.94: dict(sky_top=(84, 148, 180), sky_mid=(244, 182, 176), sky_bot=(255, 192, 158), horizon=(255, 178, 134)),
    },
)


# 8. Indigo & Fire — ARRANGEMENT (c) BOTH (banded AND migrating). The high-
#    contrast jewel: a fiery red-orange horizon → magenta-violet mid bridge →
#    DEEP INDIGO top — a clear three-band stack whose bands ALSO migrate over
#    time: the flame recedes at the horizon while the indigo floods downward frame
#    to frame, the cool pressing harder on the flame as it darkens. → near-black
#    starry indigo. Sunrise: a cool fresh steel-blue & gold dawn.
INDIGO_FIRE = _spec(
    'Indigo & Fire',
    'SUNSET [c · both — banded AND migrating · HOT-MAGENTA-VIOLET point of the 7/8/9 cluster]: the high-contrast jewel — a magenta-RED (H348) horizon, a hot PURPLE-MAGENTA mid bridge (orange driven out), and a DEEP INDIGO (H250) top, banded AND migrating: over time the flame recedes and the indigo floods downward, the cool pressing on the flame as it darkens. NIGHT: near-black starry indigo, star_alpha peaks ~238 — the dark brief suits it perfectly. SUNRISE: a cool fresh steel-blue and gold dawn.',
    {
        # SUNSET (c) both — row 8 now owns the HOT-MAGENTA-VIOLET point of the
        # 7/8/9 cluster (its separator from dusty-rose 7 and tangerine 9): the mid
        # is pulled COOLER and more VIOLET (a hot purple-magenta, the orange driven
        # OUT of it), the deep indigo top floods harder, and the horizon flame is
        # cooled from pure tangerine toward a magenta-RED so the warm end leans
        # toward the magenta family, not the orange one. Still a three-band stack
        # (flame-magenta horizon, purple-magenta mid bridge, deep indigo top) that
        # MIGRATES indigo-down over time. The purple-magenta mid is the saturated
        # bridge keeping the flame→indigo column from greying.
        0.40: dict(sky_top=(50, 44, 124),  sky_mid=(128, 52, 176),  sky_bot=(196, 60, 144),  horizon=(234, 80, 116)),
        0.44: dict(sky_top=(44, 38, 118),  sky_mid=(114, 46, 172),  sky_bot=(186, 52, 136),  horizon=(228, 66, 104)),
        0.50: dict(sky_top=(38, 32, 110),  sky_mid=(98, 42, 166),   sky_bot=(174, 46, 128),  horizon=(222, 54, 96)),
        0.56: dict(sky_top=(34, 28, 98),   sky_mid=(80, 40, 150),   sky_bot=(154, 46, 122),  horizon=(208, 50, 98)),
        # DUSK→TWILIGHT→NIGHT — indigo to near-black; the magenta-flame fades at the
        # base, the horizon kept magenta-leaning (not orange) so row 8 stays the cool
        # purple-magenta of the cluster right through dusk.
        0.62: dict(sky_top=(26, 24, 78),   sky_mid=(54, 38, 114),   sky_bot=(116, 52, 116),  horizon=(192, 64, 100), star_alpha=90),
        0.68: dict(sky_top=(18, 18, 60),   sky_mid=(36, 30, 86),    sky_bot=(78, 44, 92),    horizon=(142, 56, 80),  star_alpha=158),
        0.72: dict(sky_top=(8, 8, 32),     sky_mid=(18, 18, 50),    sky_bot=(36, 30, 58),    horizon=(78, 44, 48),   star_alpha=238),
        0.80: dict(sky_top=(10, 12, 38),   sky_mid=(24, 24, 56),    sky_bot=(44, 36, 64),    horizon=(86, 52, 52),   star_alpha=168),
        # SUNRISE — cool fresh steel-blue mid lifting to a thin gold horizon; a
        # genuinely different, brighter moment than the indigo-and-flame dusk.
        0.88: dict(sky_top=(78, 142, 178), sky_mid=(160, 192, 216), sky_bot=(206, 204, 204), horizon=(252, 196, 138)),
        0.94: dict(sky_top=(86, 152, 184), sky_mid=(162, 196, 216), sky_bot=(212, 208, 206), horizon=(255, 202, 152)),
    },
)


# 9. Aurora Teal-Magenta — ARRANGEMENT (c) BOTH (banded AND migrating). Owns the
#    WARM TANGERINE end of the 7/8/9 magenta cluster: a banded aurora — a tangerine-
#    coral horizon → warm magenta-rose mid → indigo top with a teal sliver at the
#    horizon edge — and over time the bands BOTH darken AND migrate: the warm end
#    cools upward, the teal re-enters as a TWILIGHT accent, so the banded aurora
#    sweeps tangerine→magenta→indigo→teal-glow frame to frame. → deep indigo night
#    with one signature low teal-green glow. Sunrise: fresh cyan-peach.
AURORA_TEAL_MAGENTA = _spec(
    'Aurora Teal-Magenta',
    'SUNSET [c · both — banded AND migrating · WARM-TANGERINE end of the 7/8/9 cluster]: a banded aurora — a TANGERINE-coral (H14) horizon, a warm magenta-rose mid, an indigo top, with a thin TEAL sliver at the horizon edge — whose bands ALSO migrate: over time the warm end cools upward and the teal re-blooms as the TWILIGHT (0.68) accent, so the banded sky sweeps tangerine→magenta→indigo→teal-glow. NIGHT: a deep indigo near-black carrying ONE signature low teal-green star-glow at the horizon (its separator from rows 5/8), star_alpha peaks ~236. SUNRISE [C]: a fresh cyan-and-peach dawn, calm and clearly different from the electric dusk.',
    {
        # SUNSET (c) both — a banded aurora that MIGRATES, now pulled to OWN THE WARM
        # TANGERINE END of the 7/8/9 magenta sweep (its separator: 7 dusty-rose, 8
        # hot-magenta-violet, 9 warm-tangerine-magenta). The horizon/bot are warmed
        # decisively toward tangerine-coral (orange driven INTO the warm end), while
        # the mid stays a warm magenta-rose bridge and the top an indigo, with a
        # luminous teal sliver kept at the very edge. Frame to frame the warm end
        # cools upward and the indigo presses down — banded yet sweeping cool — but
        # the WARM anchor is now plainly tangerine, not the cool hot-magenta of row 8.
        0.40: dict(sky_top=(60, 50, 108),  sky_mid=(228, 110, 158), sky_bot=(252, 110, 116), horizon=(255, 110, 78)),
        0.44: dict(sky_top=(52, 44, 102),  sky_mid=(226, 92, 152),  sky_bot=(252, 92, 104),  horizon=(255, 94, 64)),
        0.50: dict(sky_top=(44, 36, 94),   sky_mid=(224, 78, 148),  sky_bot=(250, 78, 96),   horizon=(252, 80, 56)),
        0.56: dict(sky_top=(36, 30, 84),   sky_mid=(200, 66, 138),  sky_bot=(232, 66, 96),   horizon=(228, 66, 60)),
        # DUSK→TWILIGHT→NIGHT — indigo deepening to near-black; magenta cools out,
        # and TEAL re-enters as the unmistakable TWILIGHT (0.68) accent (its real
        # feature moment, pushed brighter/greener here) before settling into the
        # night's one signature low cool teal-GREEN star-glow at the horizon —
        # deepened and greened so it clearly separates this row's night from the
        # pure-indigo nights of rows 5/8.
        0.62: dict(sky_top=(28, 24, 78),   sky_mid=(108, 54, 122),  sky_bot=(180, 68, 116),  horizon=(214, 76, 96),   star_alpha=88),
        0.68: dict(sky_top=(14, 26, 64),   sky_mid=(34, 80, 110),   sky_bot=(70, 116, 128),  horizon=(64, 150, 142),  star_alpha=156),
        0.72: dict(sky_top=(6, 14, 32),    sky_mid=(12, 36, 52),    sky_bot=(24, 56, 60),    horizon=(38, 104, 86),   star_alpha=236),
        0.80: dict(sky_top=(8, 18, 40),    sky_mid=(16, 46, 64),    sky_bot=(32, 64, 72),    horizon=(46, 112, 92),   star_alpha=168),
        # SUNRISE [C] — fresh cyan-and-peach; cool, calm, plainly a different
        # moment than the electric dusk (B leads, only a breath of peach at base).
        # Re-SATURATED so "calm" reads saturated-SOFT, not pale: the cyan carries
        # real chroma and the base a real peach, never a washed whisper.
        0.88: dict(sky_top=(72, 150, 190), sky_mid=(120, 194, 212), sky_bot=(190, 198, 200), horizon=(236, 174, 152)),
        0.94: dict(sky_top=(80, 158, 196), sky_mid=(124, 198, 214), sky_bot=(196, 202, 202), horizon=(240, 180, 158)),
    },
)


# 10. Sunfire Tangerine — ARRANGEMENT (a) OVER-TIME SWEEP. The inferno TRAVELS:
#     golden reads vivid TANGERINE, sunset cools to a deep RED-amber, the 0.56
#     dwell tips smoky PLUM-magenta. → smoky violet night. Sunrise: a warm fresh
#     peach-gold dawn.
SUNFIRE_TANGERINE = _spec(
    'Sunfire Tangerine',
    'SUNSET [a · over-time sweep, explicit migration]: a sky-filling inferno that TRAVELS coral→rose→indigo — golden 0.40 reads vivid TANGERINE (H26), sunset 0.50 a true CORAL, then the 0.56 dwell drives the horizon to MAGENTA-ROSE while a real BLUE-VIOLET pulls DOWN into the mid (not just coral over blue). NIGHT: a smoky violet near-black, star_alpha peaks ~236. SUNRISE: a warm fresh peach-gold dawn, full real colour.',
    {
        # SUNSET (a) over-time sweep — migration made EXPLICIT so the sweep is no
        # longer near-invisible (round-1 read near-mono coral over blue across the
        # warm columns). golden 0.40 reads vivid TANGERINE; sunset 0.50 a true CORAL;
        # by the 0.56 dwell the horizon has driven to MAGENTA-ROSE while a real
        # BLUE-VIOLET is pulled DOWN into the mid — so over time the column reads
        # coral → rose → INDIGO, not just "coral over blue". The horizon's rose and
        # the mid's blue-violet now arrive earlier (0.50 mid cooled, 0.56 horizon
        # deep magenta-rose) so the journey is visible even on the warm columns.
        0.40: dict(sky_top=(90, 76, 112),  sky_mid=(240, 150, 104), sky_bot=(252, 150, 60),  horizon=(255, 122, 40)),
        0.44: dict(sky_top=(76, 58, 116),  sky_mid=(238, 118, 110), sky_bot=(255, 124, 52),  horizon=(252, 90, 44)),
        0.50: dict(sky_top=(58, 44, 118),  sky_mid=(214, 86, 120),  sky_bot=(250, 104, 62),  horizon=(246, 70, 58)),
        0.56: dict(sky_top=(48, 38, 128),  sky_mid=(118, 64, 158),  sky_bot=(214, 76, 110),  horizon=(220, 56, 116)),
        # DUSK→TWILIGHT→NIGHT — the migration continues into dusk: the horizon holds
        # a MAGENTA-ROSE glow (its travelled warm end) while the mid keeps a real
        # blue-violet so the coral→rose→indigo story stays legible, then both sink
        # to a smoky violet near-black. Saturation is HELD up across the handoff so
        # no vertical sample greys, the way rows 1/3 stay clean. Stars emerge.
        0.62: dict(sky_top=(34, 26, 96),   sky_mid=(88, 56, 128),   sky_bot=(196, 86, 108),  horizon=(218, 70, 100),  star_alpha=88),
        0.68: dict(sky_top=(22, 20, 70),   sky_mid=(54, 40, 96),    sky_bot=(126, 64, 84),   horizon=(168, 64, 80),   star_alpha=156),
        0.72: dict(sky_top=(12, 10, 32),   sky_mid=(34, 22, 44),    sky_bot=(60, 38, 48),    horizon=(102, 56, 44),  star_alpha=236),
        0.80: dict(sky_top=(16, 14, 38),   sky_mid=(40, 28, 50),    sky_bot=(66, 44, 54),    horizon=(110, 64, 48),  star_alpha=168),
        # SUNRISE — warm fresh peach-gold; full colour, clearer than the dusk.
        0.88: dict(sky_top=(74, 118, 156), sky_mid=(226, 166, 138), sky_bot=(255, 184, 136), horizon=(255, 174, 112)),
        0.94: dict(sky_top=(84, 142, 174), sky_mid=(234, 184, 158), sky_bot=(255, 196, 152), horizon=(255, 186, 134)),
    },
)


# 11. Coral Blaze (original · ref) — the EXACT current committed Coral Blaze
#     override table, verbatim and unchanged (no star_alpha overrides), so the
#     user can compare the liked v2 look directly against Coral Blaze v2 and the
#     rest of the v3 set. Authored against the new frame, this row's night/dawn
#     fall back to the spine (the reference is the dusk/dawn warmth, not a night).
CORAL_BLAZE_ORIG = _spec(
    'Coral Blaze (original · ref)',
    'REFERENCE: the exact committed v2 Coral Blaze — a warm coral melting up from a salmon-red horizon with a cool blush mid and the protected cyan top, plus its soft blush-grey dawn. Carried verbatim so the liked v2 look can be compared side-by-side with the v3 treatments.',
    {
        0.40: dict(sky_top=(92, 148, 174), sky_mid=(246, 116, 130), sky_bot=(255, 158, 124), horizon=(255, 112, 86)),
        0.50: dict(sky_top=(82, 128, 160), sky_mid=(250, 100, 134), sky_bot=(255, 138, 108), horizon=(255, 78, 56)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(212, 88, 118),  sky_bot=(232, 118, 112), horizon=(252, 98, 86)),
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(190, 184, 202), sky_bot=(214, 186, 204), horizon=(220, 182, 210)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(182, 188, 204), sky_bot=(210, 188, 206), horizon=(214, 184, 210)),
    },
)


# Sheet order matches the 10 fresh v3 directions, with the original Coral Blaze
# reference row last for comparison.
CONCEPTS = [
    ('ember_gold', EMBER_GOLD),
    ('blood_orange', BLOOD_ORANGE),
    ('scarlet_crimson', SCARLET_CRIMSON),
    ('blood_scarlet', BLOOD_SCARLET),
    ('amethyst_nightfall', AMETHYST_NIGHTFALL),
    ('coral_blaze_v2', CORAL_BLAZE_V2),
    ('rose_gold_twilight', ROSE_GOLD_TWILIGHT),
    ('indigo_fire', INDIGO_FIRE),
    ('aurora_teal_magenta', AURORA_TEAL_MAGENTA),
    ('sunfire_tangerine', SUNFIRE_TANGERINE),
    ('coral_blaze_orig', CORAL_BLAZE_ORIG),
]
