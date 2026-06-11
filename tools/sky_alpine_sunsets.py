"""
Alpine Haze sunset/sunrise study, v3 — 10 sunset→night moods over a frozen day.

The user loves the round-14 "Alpine Haze" DAY: a cool glacial-cyan day. v3 keeps
that day byte-for-byte but re-authors everything from golden hour onward. The v2
sunsets were rejected on real feedback for being "too much blue" (a protected
cyan top on every frame read wrong) and not darkening; the dawns were "a bit
pale". v3's brief: each sunset is WARM and GETS DARKER, then SLOWLY melts into
its own DARK, star-rich night; each dawn is RICH, never pale.

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
    return [(ph, by_phase[ph]) for ph in sorted(by_phase)]


def _spec(name, note, overrides):
    return BiomeSpec(name=name, note=note, keyframes=_compose(overrides), sky=_ALPINE_SKY)


# ── the 10 sunset→night moods (frozen cool-cyan day under every one) ───────────
# Authoring discipline shared by all rows (v3):
#   * DAY (0.06/0.18/0.30): the untouched cool glacial-cyan day — frozen,
#     byte-for-byte identical across every row. Never warmed, never darkened.
#   * SUNSET (golden 0.40 / sunset 0.50, with optional 0.44/0.56 dwell): the
#     astonishing half. WARM and DARKENING — NOT cyan-topped. The top is free to
#     go deep dusky violet / indigo / warm-dark; the warm bloom climbs from the
#     horizon up through the mid. Lower overall VALUE than v2 — a real sunset
#     warms and dims as it falls.
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
# Clean, saturated hues only — cyan→warm and warm→dark are routed through
# saturated midtones so no vertical sample greys to a muddy taupe/olive seam.
# Each row's NIGHT sky_top VALUE is clearly darker than its own SUNSET sky_top.


# 1. Ember Gold — opulent blazing gold→ember sunset → deep bronze-indigo
#    starry night. Sunrise: a rich warm amber-rose dawn.
EMBER_GOLD = _spec(
    'Ember Gold',
    'SUNSET: a blazing gold (H46) sky_bot over a molten ember-orange (H22) horizon under a deepening dusky-bronze top — warm and DARKENING, the fire climbing high. NIGHT: melts to a deep bronze-indigo near-black, star_alpha peaks ~236. SUNRISE: a rich warm amber-rose dawn, never pale.',
    {
        # SUNSET — gold over ember; the TOP warms+darkens (no cyan): a dusky
        # bronze-violet zenith pressing the molten gold down, value falling
        # frame to frame. cyan→gold seam carried by a saturated apricot mid.
        0.40: dict(sky_top=(96, 92, 110),  sky_mid=(224, 162, 104), sky_bot=(255, 184, 70),  horizon=(255, 130, 36)),
        0.44: dict(sky_top=(86, 76, 100),  sky_mid=(228, 150, 92),  sky_bot=(255, 172, 56),  horizon=(252, 114, 30)),
        0.50: dict(sky_top=(72, 58, 88),   sky_mid=(228, 138, 80),  sky_bot=(252, 158, 44),  horizon=(244, 96, 24)),
        0.56: dict(sky_top=(56, 44, 74),   sky_mid=(204, 118, 74),  sky_bot=(236, 138, 44),  horizon=(224, 84, 26)),
        # DUSK→TWILIGHT→NIGHT — slow darken into bronze-indigo; warm amber holds
        # at the base while the top sinks to near-black indigo. Stars emerge.
        0.62: dict(sky_top=(36, 30, 60),   sky_mid=(120, 78, 78),   sky_bot=(178, 110, 64),  horizon=(206, 96, 44),  star_alpha=88),
        0.68: dict(sky_top=(24, 22, 48),   sky_mid=(74, 52, 66),    sky_bot=(120, 80, 64),   horizon=(158, 88, 50),  star_alpha=156),
        0.72: dict(sky_top=(12, 12, 30),   sky_mid=(30, 26, 48),    sky_bot=(56, 46, 56),    horizon=(96, 64, 48),   star_alpha=236),
        0.80: dict(sky_top=(16, 16, 38),   sky_mid=(36, 34, 58),    sky_bot=(64, 56, 64),    horizon=(102, 76, 58),  star_alpha=168),
        # SUNRISE — rich warm amber-rose; clearer and fresher than the dusk fire,
        # full real colour (never pale), the top lifting back toward day.
        0.88: dict(sky_top=(72, 110, 150), sky_mid=(220, 158, 134), sky_bot=(255, 178, 132), horizon=(255, 168, 110)),
        0.94: dict(sky_top=(82, 138, 172), sky_mid=(228, 178, 158), sky_bot=(255, 192, 150), horizon=(255, 182, 132)),
    },
)


# 2. Blood Orange — deep blood-orange sunset → wine-dark starry night.
#    Sunrise: a fresh peach-and-rose dawn.
BLOOD_ORANGE = _spec(
    'Blood Orange',
    'SUNSET: a deep blood-orange (H18) horizon bleeding up into a red-amber mid under a dusky wine-violet top — warm, DARK, weighty. NIGHT: a wine-dark (deep maroon-violet) near-black, star_alpha peaks ~234. SUNRISE: a fresh peach-and-rose dawn, full colour.',
    {
        # SUNSET — blood-orange burning low under a wine-violet top that darkens;
        # red-amber mid bridges cyan→fire without greying.
        0.40: dict(sky_top=(94, 78, 104),  sky_mid=(216, 118, 86),  sky_bot=(250, 120, 52),  horizon=(238, 78, 38)),
        0.44: dict(sky_top=(82, 64, 96),   sky_mid=(218, 104, 76),  sky_bot=(248, 104, 44),  horizon=(228, 64, 34)),
        0.50: dict(sky_top=(68, 48, 82),   sky_mid=(216, 90, 68),   sky_bot=(244, 90, 40),   horizon=(216, 52, 32)),
        0.56: dict(sky_top=(52, 36, 68),   sky_mid=(190, 78, 66),   sky_bot=(226, 82, 44),   horizon=(200, 50, 36)),
        # DUSK→TWILIGHT→NIGHT — slow fall into wine-dark; deep maroon-violet.
        0.62: dict(sky_top=(40, 24, 52),   sky_mid=(126, 56, 70),   sky_bot=(172, 72, 60),   horizon=(192, 64, 48),  star_alpha=86),
        0.68: dict(sky_top=(28, 18, 44),   sky_mid=(78, 38, 56),    sky_bot=(116, 54, 56),   horizon=(146, 62, 52),  star_alpha=154),
        0.72: dict(sky_top=(14, 8, 26),    sky_mid=(34, 18, 38),    sky_bot=(58, 30, 44),    horizon=(86, 44, 48),   star_alpha=234),
        0.80: dict(sky_top=(18, 12, 32),   sky_mid=(40, 24, 46),    sky_bot=(66, 38, 50),    horizon=(94, 52, 54),   star_alpha=166),
        # SUNRISE — fresh peach over a rose horizon; clearer than the blood dusk.
        0.88: dict(sky_top=(74, 116, 154), sky_mid=(224, 162, 148), sky_bot=(255, 176, 144), horizon=(255, 158, 126)),
        0.94: dict(sky_top=(84, 142, 174), sky_mid=(232, 180, 168), sky_bot=(255, 190, 158), horizon=(255, 172, 146)),
    },
)


# 3. Scarlet Crimson — intense scarlet sunset → oxblood→near-black indigo night.
#    Sunrise: a clean rose-pink dawn (cooler, fresher than the dusk).
SCARLET_CRIMSON = _spec(
    'Scarlet Crimson',
    'SUNSET: an intense scarlet (H4) flooding the lower sky and washing the mid smouldering crimson under a deep oxblood-indigo top — the hottest red of the set, darkening. NIGHT: an oxblood that sinks to near-black indigo, star_alpha peaks ~238. SUNRISE: a clean rose-pink dawn, fresher than the fiery dusk.',
    {
        # SUNSET — scarlet sky-filling; the top is a deep oxblood-indigo (not
        # cyan), value dropping. Rose-magenta mid keeps the top blend saturated.
        0.40: dict(sky_top=(82, 56, 84),   sky_mid=(214, 64, 96),   sky_bot=(238, 70, 56),   horizon=(228, 40, 36)),
        0.44: dict(sky_top=(72, 44, 78),   sky_mid=(216, 54, 90),   sky_bot=(236, 60, 50),   horizon=(218, 34, 34)),
        0.50: dict(sky_top=(60, 34, 68),   sky_mid=(214, 46, 86),   sky_bot=(232, 50, 44),   horizon=(206, 28, 32)),
        0.56: dict(sky_top=(48, 26, 58),   sky_mid=(190, 44, 84),   sky_bot=(214, 50, 48),   horizon=(190, 30, 36)),
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


# 4. Fuchsia Dusk — bold fuchsia→magenta sunset → deep plum-violet starry night.
#    Sunrise: a bright cyan-and-blush dawn (clean cool contrast).
FUCHSIA_DUSK = _spec(
    'Fuchsia Dusk',
    'SUNSET: a bold hot-fuchsia (H322) horizon blooming up through a magenta mid under a deep plum-violet top — electric and darkening. NIGHT: a deep plum-violet near-black, star_alpha peaks ~236. SUNRISE [C]: a bright cyan-and-blush dawn, a clean cool counterpoint to the dusk.',
    {
        # SUNSET — fuchsia climbs high; the top is a deepening plum-violet (not
        # cyan). Bright magenta sky_bot bridges the seam.
        0.40: dict(sky_top=(86, 66, 104),  sky_mid=(180, 86, 178),  sky_bot=(232, 84, 176),  horizon=(244, 52, 146)),
        0.44: dict(sky_top=(76, 54, 98),   sky_mid=(168, 70, 176),  sky_bot=(232, 68, 170),  horizon=(242, 40, 138)),
        0.50: dict(sky_top=(64, 42, 88),   sky_mid=(154, 58, 174),  sky_bot=(230, 54, 164),  horizon=(236, 28, 128)),
        0.56: dict(sky_top=(52, 34, 76),   sky_mid=(126, 50, 156),  sky_bot=(212, 54, 158),  horizon=(220, 32, 126)),
        # DUSK→TWILIGHT→NIGHT — plum-violet deepening to near-black.
        0.62: dict(sky_top=(38, 24, 62),   sky_mid=(92, 44, 122),   sky_bot=(166, 60, 142),  horizon=(196, 48, 122),  star_alpha=86),
        0.68: dict(sky_top=(28, 18, 50),   sky_mid=(60, 32, 86),    sky_bot=(108, 46, 100),  horizon=(146, 52, 100),  star_alpha=154),
        0.72: dict(sky_top=(12, 8, 30),    sky_mid=(30, 18, 50),    sky_bot=(52, 28, 62),    horizon=(80, 40, 70),    star_alpha=236),
        0.80: dict(sky_top=(16, 12, 36),   sky_mid=(36, 24, 58),    sky_bot=(60, 36, 70),    horizon=(90, 48, 78),    star_alpha=168),
        # SUNRISE [C] — clean cool cyan-and-blush; plainly a different, fresher
        # moment than the fuchsia dusk (B leads, only a breath of warm at base).
        0.88: dict(sky_top=(78, 142, 174), sky_mid=(156, 198, 210), sky_bot=(206, 200, 210), horizon=(228, 192, 200)),
        0.94: dict(sky_top=(86, 152, 182), sky_mid=(156, 200, 210), sky_bot=(210, 204, 212), horizon=(232, 196, 202)),
    },
)


# 5. Amethyst Nightfall — luxe amethyst-violet sunset → deep indigo starry night.
#    Sunrise: a rich rose-violet dawn (same family, but fresher and lighter).
AMETHYST_NIGHTFALL = _spec(
    'Amethyst Nightfall',
    'SUNSET: a luxe amethyst-violet (H280) sky filling up from a jewel-rose (H338) horizon under a deepening indigo top — rich and darkening. NIGHT: a deep indigo near-black, star_alpha peaks ~238. SUNRISE: a rich rose-violet dawn — the same jewel family reborn fresher and lighter, distinct from the dusk.',
    {
        # SUNSET — amethyst above a rose horizon; the top sinks to deep indigo.
        0.40: dict(sky_top=(78, 64, 116),  sky_mid=(150, 100, 192), sky_bot=(178, 78, 184),  horizon=(236, 80, 140)),
        0.44: dict(sky_top=(68, 54, 110),  sky_mid=(142, 86, 190),  sky_bot=(172, 66, 178),  horizon=(238, 64, 130)),
        0.50: dict(sky_top=(58, 44, 100),  sky_mid=(134, 74, 188),  sky_bot=(166, 56, 172),  horizon=(238, 50, 122)),
        0.56: dict(sky_top=(48, 36, 88),   sky_mid=(112, 64, 164),  sky_bot=(152, 56, 156),  horizon=(220, 50, 122)),
        # DUSK→TWILIGHT→NIGHT — indigo deepening to near-black.
        0.62: dict(sky_top=(34, 26, 74),   sky_mid=(78, 50, 132),   sky_bot=(132, 60, 142),  horizon=(192, 58, 118),  star_alpha=88),
        0.68: dict(sky_top=(24, 20, 58),   sky_mid=(50, 36, 92),    sky_bot=(86, 46, 102),   horizon=(140, 54, 100),  star_alpha=156),
        0.72: dict(sky_top=(10, 8, 34),    sky_mid=(24, 18, 54),    sky_bot=(42, 28, 66),    horizon=(72, 40, 74),    star_alpha=238),
        0.80: dict(sky_top=(14, 12, 40),   sky_mid=(30, 24, 60),    sky_bot=(50, 34, 72),    horizon=(82, 48, 82),    star_alpha=168),
        # SUNRISE — rich rose-violet reborn; fresher, lighter, clearly distinct.
        0.88: dict(sky_top=(78, 132, 168), sky_mid=(190, 158, 210), sky_bot=(228, 168, 204), horizon=(248, 158, 184)),
        0.94: dict(sky_top=(86, 148, 178), sky_mid=(200, 178, 216), sky_bot=(234, 182, 210), horizon=(250, 172, 192)),
    },
)


# 6. Coral Blaze v2 — reborn coral/salmon sunset → deep teal-navy star-rich night.
#    Sunrise: a fresh coral-cream dawn (the loved coral reborn, clearer).
CORAL_BLAZE_V2 = _spec(
    'Coral Blaze v2',
    'SUNSET: a warm coral (H14) blooming up from a salmon-red horizon under a deepening dusky teal-slate top — the loved reef glow reborn, now warm and DARKENING. NIGHT: a deep teal-navy near-black, star_alpha peaks ~234. SUNRISE: a fresh coral-cream dawn, the coral reborn clearer and lighter than the dusk.',
    {
        # SUNSET — salmon-coral over the horizon; the top warms-and-darkens to a
        # dusky teal-slate (a nod to the night's teal-navy) instead of cyan.
        # Saturated coral-rose mid keeps the top blend clean.
        0.40: dict(sky_top=(72, 100, 116), sky_mid=(244, 124, 124), sky_bot=(255, 150, 116), horizon=(255, 108, 80)),
        0.44: dict(sky_top=(58, 86, 104),  sky_mid=(246, 110, 118), sky_bot=(255, 138, 104), horizon=(255, 94, 66)),
        0.50: dict(sky_top=(46, 72, 92),   sky_mid=(244, 96, 112),  sky_bot=(255, 124, 92),  horizon=(252, 78, 54)),
        0.56: dict(sky_top=(38, 60, 80),   sky_mid=(216, 86, 104),  sky_bot=(238, 110, 90),  horizon=(232, 74, 56)),
        # DUSK→TWILIGHT→NIGHT — deep teal-navy; warm coral lingers at the base
        # while the top sinks to a near-black teal-navy. Stars emerge.
        0.62: dict(sky_top=(20, 44, 64),   sky_mid=(96, 70, 96),    sky_bot=(176, 92, 96),   horizon=(214, 86, 70),  star_alpha=86),
        0.68: dict(sky_top=(14, 34, 54),   sky_mid=(48, 56, 80),    sky_bot=(108, 70, 80),   horizon=(160, 80, 68),  star_alpha=154),
        0.72: dict(sky_top=(6, 16, 32),    sky_mid=(16, 38, 56),    sky_bot=(40, 56, 66),    horizon=(86, 66, 60),   star_alpha=234),
        0.80: dict(sky_top=(8, 22, 40),    sky_mid=(20, 46, 66),    sky_bot=(46, 64, 76),    horizon=(94, 76, 68),   star_alpha=166),
        # SUNRISE — fresh coral-cream; the reef glow reborn clear and lighter.
        0.88: dict(sky_top=(76, 124, 158), sky_mid=(244, 168, 152), sky_bot=(255, 184, 158), horizon=(255, 166, 130)),
        0.94: dict(sky_top=(86, 146, 176), sky_mid=(248, 186, 172), sky_bot=(255, 196, 172), horizon=(255, 178, 150)),
    },
)


# 7. Rose-Gold Twilight — hot-pink→gold duotone sunset → dusky mauve-navy night.
#    Sunrise: a quiet warm blush-gold dawn, but with real colour.
ROSE_GOLD_TWILIGHT = _spec(
    'Rose-Gold Twilight',
    'SUNSET: an opulent duotone — a hot-pink (H335) mid band over a rich gold (H42) horizon under a deepening mauve top, pink-above / gold-below, regal and darkening. NIGHT: a dusky mauve-navy near-black, star_alpha peaks ~234. SUNRISE: a quiet warm blush-gold dawn, soft but with real colour — never pale.',
    {
        # SUNSET — hot-pink band over a gold horizon; the top warms+darkens to a
        # dusky mauve (not cyan). Saturated rose mid keeps the blend clean.
        0.40: dict(sky_top=(92, 70, 104),  sky_mid=(232, 96, 176),  sky_bot=(250, 116, 150), horizon=(255, 166, 70)),
        0.44: dict(sky_top=(80, 58, 98),   sky_mid=(232, 84, 178),  sky_bot=(250, 104, 142), horizon=(255, 150, 56)),
        0.50: dict(sky_top=(68, 48, 90),   sky_mid=(230, 74, 178),  sky_bot=(248, 92, 134),  horizon=(252, 136, 46)),
        0.56: dict(sky_top=(54, 38, 78),   sky_mid=(204, 66, 158),  sky_bot=(228, 88, 130),  horizon=(232, 124, 50)),
        # DUSK→TWILIGHT→NIGHT — mauve-navy deepening to near-black.
        0.62: dict(sky_top=(40, 26, 64),   sky_mid=(124, 50, 124),  sky_bot=(176, 78, 116),  horizon=(214, 110, 64),  star_alpha=86),
        0.68: dict(sky_top=(28, 20, 54),   sky_mid=(74, 38, 86),    sky_bot=(116, 56, 86),   horizon=(160, 84, 60),   star_alpha=154),
        0.72: dict(sky_top=(12, 10, 32),   sky_mid=(30, 20, 50),    sky_bot=(54, 32, 56),    horizon=(90, 56, 50),    star_alpha=234),
        0.80: dict(sky_top=(16, 12, 38),   sky_mid=(36, 24, 56),    sky_bot=(60, 38, 62),    horizon=(98, 64, 56),    star_alpha=166),
        # SUNRISE — quiet warm blush-gold; soft but real colour, fresher hue.
        0.88: dict(sky_top=(76, 128, 162), sky_mid=(232, 170, 168), sky_bot=(255, 188, 156), horizon=(255, 178, 130)),
        0.94: dict(sky_top=(86, 148, 178), sky_mid=(238, 186, 182), sky_bot=(255, 198, 170), horizon=(255, 186, 148)),
    },
)


# 8. Indigo & Fire — fiery red-orange horizon under a deep indigo sky → melts to
#    near-black starry indigo (the dark brief now SUITS this row). Sunrise: a
#    cool fresh steel-blue & gold dawn.
INDIGO_FIRE = _spec(
    'Indigo & Fire',
    'SUNSET: the high-contrast jewel — a fiery red-orange (H18) horizon burning beneath a DEEP INDIGO (H250) sky_bot/mid and an ever-darker indigo top, the cool pressing on the flame. NIGHT: near-black starry indigo, star_alpha peaks ~238 — the dark brief now suits it perfectly. SUNRISE: a cool fresh steel-blue and gold dawn.',
    {
        # SUNSET — indigo dominates the sky; a thin fierce flame at the horizon.
        # The top is ALREADY deep indigo and only deepens. Violet sky_bot bridges
        # indigo→flame so it never greys.
        0.40: dict(sky_top=(46, 48, 110),  sky_mid=(74, 70, 148),   sky_bot=(140, 80, 132),  horizon=(248, 116, 56)),
        0.44: dict(sky_top=(40, 42, 104),  sky_mid=(66, 60, 142),   sky_bot=(136, 70, 122),  horizon=(248, 100, 48)),
        0.50: dict(sky_top=(34, 36, 96),   sky_mid=(58, 52, 136),   sky_bot=(130, 62, 112),  horizon=(246, 84, 40)),
        0.56: dict(sky_top=(30, 30, 84),   sky_mid=(50, 46, 122),   sky_bot=(120, 60, 106),  horizon=(232, 80, 42)),
        # DUSK→TWILIGHT→NIGHT — indigo to near-black; flame fades at the base.
        0.62: dict(sky_top=(24, 24, 70),   sky_mid=(42, 40, 100),   sky_bot=(104, 60, 96),   horizon=(206, 84, 48),  star_alpha=90),
        0.68: dict(sky_top=(18, 18, 56),   sky_mid=(32, 30, 76),    sky_bot=(72, 48, 80),    horizon=(150, 66, 50),  star_alpha=158),
        0.72: dict(sky_top=(8, 8, 32),     sky_mid=(18, 18, 50),    sky_bot=(36, 30, 58),    horizon=(78, 44, 48),   star_alpha=238),
        0.80: dict(sky_top=(10, 12, 38),   sky_mid=(24, 24, 56),    sky_bot=(44, 36, 64),    horizon=(86, 52, 52),   star_alpha=168),
        # SUNRISE — cool fresh steel-blue mid lifting to a thin gold horizon; a
        # genuinely different, brighter moment than the indigo-and-flame dusk.
        0.88: dict(sky_top=(78, 142, 178), sky_mid=(160, 192, 216), sky_bot=(206, 204, 204), horizon=(252, 196, 138)),
        0.94: dict(sky_top=(86, 152, 184), sky_mid=(162, 196, 216), sky_bot=(212, 208, 206), horizon=(255, 202, 152)),
    },
)


# 9. Aurora Teal-Magenta — electric teal↔magenta aurora sunset → deep teal-indigo
#    aurora night. Sunrise: a fresh cyan-and-peach dawn.
AURORA_TEAL_MAGENTA = _spec(
    'Aurora Teal-Magenta',
    'SUNSET: an electric aurora — a hot magenta (H320) horizon arcing up into a luminous TEAL (H180) mid under a deepening teal-indigo top, a teal↔magenta charge filling the lower sky. NIGHT: a deep teal-indigo aurora near-black with a faint teal glow, star_alpha peaks ~236. SUNRISE [C]: a fresh cyan-and-peach dawn, calm and clearly different from the electric dusk.',
    {
        # SUNSET — magenta horizon meeting a glowing teal mid; the top is a
        # deepening teal-indigo (the teal nods to the night). The teal IS the
        # cool bridge so nothing greys.
        0.40: dict(sky_top=(40, 88, 116),  sky_mid=(58, 184, 178),  sky_bot=(198, 116, 192), horizon=(244, 72, 162)),
        0.44: dict(sky_top=(34, 80, 110),  sky_mid=(50, 180, 176),  sky_bot=(202, 100, 188), horizon=(246, 56, 156)),
        0.50: dict(sky_top=(28, 70, 104),  sky_mid=(44, 176, 174),  sky_bot=(206, 86, 184),  horizon=(244, 42, 148)),
        0.56: dict(sky_top=(24, 60, 96),   sky_mid=(42, 156, 164),  sky_bot=(194, 84, 176),  horizon=(228, 44, 146)),
        # DUSK→TWILIGHT→NIGHT — teal-indigo deepening to near-black; the magenta
        # cools out and a faint teal glow survives into the night.
        0.62: dict(sky_top=(18, 46, 84),   sky_mid=(36, 118, 134),  sky_bot=(150, 80, 150),  horizon=(204, 56, 134),  star_alpha=88),
        0.68: dict(sky_top=(12, 36, 68),   sky_mid=(26, 78, 100),   sky_bot=(94, 60, 110),   horizon=(150, 56, 104),  star_alpha=156),
        0.72: dict(sky_top=(6, 16, 38),    sky_mid=(14, 40, 60),    sky_bot=(40, 46, 70),    horizon=(78, 44, 76),    star_alpha=236),
        0.80: dict(sky_top=(8, 22, 46),    sky_mid=(18, 50, 70),    sky_bot=(46, 56, 78),    horizon=(86, 52, 80),    star_alpha=168),
        # SUNRISE [C] — fresh cyan-and-peach; cool, calm, plainly a different
        # moment than the electric dusk (B leads, only a breath of peach at base).
        0.88: dict(sky_top=(78, 142, 176), sky_mid=(150, 200, 210), sky_bot=(202, 206, 208), horizon=(232, 192, 176)),
        0.94: dict(sky_top=(86, 152, 182), sky_mid=(152, 202, 210), sky_bot=(206, 210, 210), horizon=(236, 198, 184)),
    },
)


# 10. Sunfire Tangerine — vivid sky-filling tangerine sunset → smoky violet night.
#     Sunrise: a warm fresh peach-gold dawn.
SUNFIRE_TANGERINE = _spec(
    'Sunfire Tangerine',
    'SUNSET: a vivid tangerine (H26) climbing from the horizon through the whole lower-mid frame under a deepening smoky-violet top — a sky-filling inferno that warms and DARKENS. NIGHT: a smoky violet near-black, star_alpha peaks ~236. SUNRISE: a warm fresh peach-gold dawn, full real colour.',
    {
        # SUNSET — tangerine floods the lower frame; the top warms+darkens to a
        # smoky violet (not cyan). Saturated coral/salmon mid bridges the seam.
        0.40: dict(sky_top=(92, 78, 108),  sky_mid=(238, 148, 110), sky_bot=(252, 150, 66),  horizon=(255, 124, 44)),
        0.44: dict(sky_top=(80, 66, 102),  sky_mid=(238, 138, 104), sky_bot=(255, 138, 56),  horizon=(255, 110, 36)),
        0.50: dict(sky_top=(68, 54, 94),   sky_mid=(236, 130, 98),  sky_bot=(255, 126, 48),  horizon=(252, 96, 30)),
        0.56: dict(sky_top=(54, 42, 80),   sky_mid=(214, 116, 92),  sky_bot=(240, 116, 50),  horizon=(236, 90, 32)),
        # DUSK→TWILIGHT→NIGHT — smoky violet deepening to near-black; warm base
        # lingers, top sinks. Stars emerge.
        0.62: dict(sky_top=(40, 28, 66),   sky_mid=(128, 72, 88),   sky_bot=(184, 104, 70),  horizon=(214, 96, 48),  star_alpha=88),
        0.68: dict(sky_top=(28, 22, 56),   sky_mid=(76, 48, 72),    sky_bot=(118, 72, 66),   horizon=(158, 82, 52),  star_alpha=156),
        0.72: dict(sky_top=(12, 10, 32),   sky_mid=(30, 22, 50),    sky_bot=(54, 38, 56),    horizon=(90, 56, 50),   star_alpha=236),
        0.80: dict(sky_top=(16, 14, 38),   sky_mid=(36, 28, 56),    sky_bot=(60, 44, 62),    horizon=(98, 64, 56),   star_alpha=168),
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
    ('fuchsia_dusk', FUCHSIA_DUSK),
    ('amethyst_nightfall', AMETHYST_NIGHTFALL),
    ('coral_blaze_v2', CORAL_BLAZE_V2),
    ('rose_gold_twilight', ROSE_GOLD_TWILIGHT),
    ('indigo_fire', INDIGO_FIRE),
    ('aurora_teal_magenta', AURORA_TEAL_MAGENTA),
    ('sunfire_tangerine', SUNFIRE_TANGERINE),
    ('coral_blaze_orig', CORAL_BLAZE_ORIG),
]
