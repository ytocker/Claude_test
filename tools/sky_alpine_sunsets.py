"""
Alpine Haze sunset/sunrise study — 10 variants over ONE shared day/night spine.

The user loves the round-14 "Alpine Haze" look: a cool glacial-cyan day and a
clean cool-cyan blue-hour night. A later restyle pushed its sunrise/sunset too
brown/yellow and muddy. This module keeps the Alpine day + night arc EXACTLY
and varies ONLY the sunset and sunrise colour story, so each variant reads as a
different beautiful moment without disturbing the beloved spine.

Provably-identical spine: the Alpine keyframes are authored ONCE in
`_ALPINE_HAZE_KF`. Each design `_compose`s its BiomeSpec by CLONING that base
list and overriding ONLY the sunset/sunrise RGB at the named phases (plus any
optional hold/onset frames it inserts to widen dwell on the dramatic ones).
The day anchors (0.06 / 0.18 / 0.30), the deep-night (0.72) and predawn (0.80)
blue-hour frames, and EVERY frame's `star_alpha`, pass through untouched — so
day/night timing and star onset stay byte-for-byte identical across all 10.

Preview-only data. Nothing on the live render path imports this module — it is
reached solely through `tools/preview_sky_alpine_sunsets.py`. Pure-Pygame /
pygbag-safe (the keyframes are just colour tables; the OKLab bake lives in the
engine).
"""
from __future__ import annotations

from game.biome_sky import BiomeSpec, SkyParams


# ── the shared Alpine Haze spine (authored once) ──────────────────────────────
# Phase clock matches the calm sets so the preview columns line up:
#   morning 0.06 · midday 0.18 · afternoon 0.30 · golden 0.40 · sunset 0.50 ·
#   dusk 0.62 · deep-night 0.72 · predawn 0.80 · dawn 0.88 · sunrise 0.94
# `make_palette` wraps 0.94 -> 0.06 through 1.0 so the night side is continuous.
#
# Frames flagged SPINE below are KEPT byte-for-byte on every variant. Frames
# flagged VARY are the only ones a design overrides (golden 0.40, sunset 0.50,
# dusk 0.62 for the sunset cluster; dawn 0.88, sunrise 0.94 for the sunrise
# cluster), and designs may additionally INSERT hold/onset frames at 0.44/0.56
# (sunset) and 0.86/0.90 (sunrise) to widen the dwell on the dramatic ones.
_ALPINE_HAZE_KF = [
    (0.06, dict(sky_top=(86, 158, 186),  sky_mid=(150, 192, 202), sky_bot=(196, 212, 210), horizon=(214, 218, 212), star_alpha=0)),   # SPINE morning
    (0.18, dict(sky_top=(76, 168, 192),  sky_mid=(144, 198, 208), sky_bot=(196, 214, 212), horizon=(216, 220, 212), star_alpha=0)),   # SPINE midday
    (0.30, dict(sky_top=(86, 160, 188),  sky_mid=(152, 192, 204), sky_bot=(198, 212, 208), horizon=(216, 218, 210), star_alpha=0)),   # SPINE afternoon
    (0.40, dict(sky_top=(88, 152, 178),  sky_mid=(156, 186, 196), sky_bot=(202, 208, 202), horizon=(220, 214, 204), star_alpha=0)),   # VARY golden
    (0.50, dict(sky_top=(74, 126, 160),  sky_mid=(146, 168, 184), sky_bot=(202, 200, 196), horizon=(230, 204, 184), star_alpha=12)),  # VARY sunset
    (0.62, dict(sky_top=(34, 76, 116),   sky_mid=(76, 126, 160),  sky_bot=(134, 172, 186), horizon=(190, 204, 200), star_alpha=80)),  # VARY dusk
    (0.72, dict(sky_top=(8, 28, 62),     sky_mid=(16, 64, 104),   sky_bot=(34, 104, 136),  horizon=(70, 144, 164),  star_alpha=210)), # SPINE deep night
    (0.80, dict(sky_top=(12, 38, 78),    sky_mid=(26, 84, 124),   sky_bot=(54, 126, 156),  horizon=(108, 166, 186), star_alpha=130)), # SPINE predawn
    (0.88, dict(sky_top=(76, 146, 176),  sky_mid=(140, 186, 200), sky_bot=(190, 210, 208), horizon=(214, 218, 210), star_alpha=20)),  # VARY dawn
    (0.94, dict(sky_top=(84, 156, 184),  sky_mid=(148, 192, 202), sky_bot=(196, 212, 210), horizon=(214, 218, 212), star_alpha=0)),   # VARY sunrise
]

# Shared bake params for all 10 — keeps the grade placement identical too.
_ALPINE_SKY = SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.14)

# star_alpha for any INSERTED hold/onset frame, interpolated from the Alpine
# neighbours so star timing never shifts (0.40->0.50 and 0.50->0.62 spans on
# the sunset side; 0.80->0.88 and 0.88->0.94 spans on the sunrise side).
_INSERT_STAR_ALPHA = {
    0.44: 5,    # between golden 0.40 (0) and sunset 0.50 (12)
    0.56: 30,   # between sunset 0.50 (12) and dusk 0.62 (80)
    0.86: 48,   # between predawn 0.80 (130) and dawn 0.88 (20) -> closer to dawn
    0.90: 13,   # between dawn 0.88 (20) and sunrise 0.94 (0)
}

# Phases a design is ALLOWED to override (anything else stays spine).
_VARY_PHASES = {0.40, 0.50, 0.62, 0.88, 0.94}
_INSERT_PHASES = {0.44, 0.56, 0.86, 0.90}


def _compose(overrides: dict) -> list:
    """Clone the Alpine spine and apply a design's sunset/sunrise overrides.

    `overrides` maps phase -> dict(sky_top/mid/bot/horizon). For a VARY phase
    we replace only those four RGB keys, preserving the spine's star_alpha. For
    an INSERT phase we add a brand-new frame, giving it the interpolated
    star_alpha so the star arc is unchanged. Any phase NOT listed (the day
    anchors, deep night, predawn) is copied verbatim — this is what guarantees
    the spine is identical with zero hand-transcription."""
    by_phase = {ph: dict(d) for ph, d in _ALPINE_HAZE_KF}
    for ph, rgb in overrides.items():
        assert ph in _VARY_PHASES or ph in _INSERT_PHASES, f"phase {ph} is not overridable"
        frame = dict(rgb)
        if ph in by_phase:
            # VARY: keep the spine star_alpha, swap only the four sky colours.
            frame['star_alpha'] = by_phase[ph]['star_alpha']
        else:
            # INSERT: new dwell frame gets the interpolated star_alpha.
            frame['star_alpha'] = _INSERT_STAR_ALPHA[ph]
        by_phase[ph] = frame
    return [(ph, by_phase[ph]) for ph in sorted(by_phase)]


def _spec(name, note, overrides):
    return BiomeSpec(name=name, note=note, keyframes=_compose(overrides), sky=_ALPINE_SKY)


# ── the 10 sunset/sunrise stories (Alpine day + night under every one) ─────────
# Authoring discipline shared by all rows:
#   * The TOP ~25-30% (sky_top) stays cool Alpine cyan even on the dramatic
#     rows, so white/gold HUD text and the scarlet bird keep reading — warmth
#     is pushed into mid/bot/horizon, never the zenith.
#   * Clean, saturated hues only. No muddy brown/olive (the round-17 failure).
#   * DRAMATIC: colour climbs from the horizon up THROUGH sky_bot into sky_mid,
#     and the dwell is widened with 0.44/0.56 (sunset) + 0.86/0.90 (sunrise).
#   * MODERATE/NATURAL: rich colour kept to a horizon-to-low band; the mid stays
#     closer to Alpine cool so the moment reads as a clean horizon glow.
#   * DECOUPLED moments — the rule that drives this whole set: the SUNSET is the
#     magnificent, emotional half — bolder, deeper, more saturated, pushed for
#     grandeur. The SUNRISE is a genuinely DIFFERENT moment, never a softer
#     mirror of the same colour. It is EITHER:
#       [C] a CONTRASTING, cooler/quieter hue family from the sunset (dove-blue,
#           cyan-peach, pink-grey, soft gold, gentle peach), so dawn and dusk
#           read as plainly different times of day; OR
#       [S] the SAME hue family as the sunset but at a FRACTION of its chroma —
#           a low, restrained whisper, far quieter in saturation AND value, kept
#           to a thin near-horizon band so it never twins the sunset's bloom.
#     Either way the sunrise must read CALMER and lower-energy than that row's
#     sunset. (Real dawn skies are clearer, paler and cooler; dusk holds the
#     richer, weary, more saturated colour — the study leans into that truth.)


# 1. Molten Gold & Ember — grand blazing gold->ember sunset, DRAMATIC.
#    Dawn [S]: pale apricot whisper (same warm family, a fraction of the chroma).
MOLTEN_GOLD_EMBER = _spec(
    'Molten Gold & Ember',
    'SUNSET: a grand blazing gold (H46) sky_bot deepening to a molten ember-orange (H22) horizon, the fire climbing up through the mid to ~40% of the frame, widened dwell — the most opulent gold row. SUNRISE [S]: a pale apricot whisper, same warm family at a fraction of the chroma, kept to a thin low band. DRAMATIC.',
    {
        # SUNSET — gold sky_bot over an ember horizon, the warm bloom lifted high
        # into a buttery sky_mid so it reads sky-filling and magnificent, not a
        # low band; cyan retreats to the zenith only. Ember horizon saturation
        # nudged up a further ~5% (G/B pulled in) so the fire reads hotter at the
        # base. The cyan->gold meeting is carried by a warmer, more saturated
        # apricot mid so the top blend never greys.
        0.40: dict(sky_top=(92, 148, 174), sky_mid=(220, 176, 120), sky_bot=(255, 188, 74),  horizon=(255, 136, 38)),
        0.44: dict(sky_top=(88, 140, 170), sky_mid=(230, 168, 106), sky_bot=(255, 180, 60),  horizon=(255, 120, 28)),
        0.50: dict(sky_top=(80, 126, 160), sky_mid=(238, 162, 92),  sky_bot=(255, 170, 44),  horizon=(252, 100, 20)),
        0.56: dict(sky_top=(60, 102, 144), sky_mid=(224, 150, 94),  sky_bot=(252, 156, 46),  horizon=(244, 88, 22)),
        # dusk mid routed through a warm amber rather than the old neutral 150/130/130
        # so no vertical sample greys out at the cyan->ember meeting line.
        0.62: dict(sky_top=(36, 78, 116),  sky_mid=(178, 120, 96),  sky_bot=(230, 148, 76),  horizon=(238, 108, 42)),
        # SUNRISE [S] — same warm family, but a soft pale apricot kept low and pale:
        # far lower chroma than the sunset's molten gold, the mid barely tinted.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(176, 192, 188), sky_bot=(238, 204, 176), horizon=(252, 192, 152)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(166, 196, 196), sky_bot=(226, 206, 192), horizon=(248, 198, 170)),
    },
)


# 2. Volcanic Crimson — deep scarlet-red, sky-filling, DRAMATIC.
#    Dawn [C]: calm dove-blue / soft lilac (a contrasting cool, quiet hue).
VOLCANIC_CRIMSON = _spec(
    'Volcanic Crimson',
    'SUNSET: a deep volcanic scarlet-red (H4) flooding the lower sky and washing the mid a smouldering crimson, cyan only at the zenith — the most intense red of the set, widened dwell. SUNRISE [C]: a calm dove-blue mid melting into a soft lilac horizon, a cool contrasting hue clearly different from the fiery dusk. DRAMATIC.',
    {
        # SUNSET — scarlet horizon, the red bloom carried up through a hot-crimson
        # sky_bot into a dusky-red mid so the whole lower frame burns. The
        # cyan->scarlet meeting is routed through a deeper, more saturated
        # rose-magenta mid (R far above G/B) so the top blend never collapses to
        # the grey-mauve seam — no vertical sample drops below ~0.30 sat.
        0.40: dict(sky_top=(90, 140, 166), sky_mid=(228, 76, 124),  sky_bot=(244, 88, 70),   horizon=(232, 46, 38)),
        0.44: dict(sky_top=(86, 130, 162), sky_mid=(234, 66, 120),  sky_bot=(244, 74, 60),   horizon=(224, 38, 34)),
        0.50: dict(sky_top=(78, 116, 152), sky_mid=(238, 56, 116),  sky_bot=(242, 60, 50),   horizon=(214, 30, 30)),
        0.56: dict(sky_top=(58, 96, 138),  sky_mid=(220, 54, 112),  sky_bot=(234, 58, 52),   horizon=(204, 32, 34)),
        0.62: dict(sky_top=(36, 76, 114),  sky_mid=(176, 50, 116),  sky_bot=(204, 70, 72),   horizon=(196, 42, 48)),
        # SUNRISE [C] — a cool, quiet dove-blue / lilac dawn: nothing red at all, so
        # the morning reads as an entirely different, calmer moment.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(168, 184, 204), sky_bot=(196, 192, 214), horizon=(214, 196, 216)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(160, 188, 206), sky_bot=(190, 196, 216), horizon=(206, 198, 216)),
    },
)


# 3. Magenta Storm — intense magenta->purple, DRAMATIC.
#    Dawn [S]: a low mauve mist (same family, far quieter).
MAGENTA_STORM = _spec(
    'Magenta Storm',
    'SUNSET: an intense storm-magenta (H322) horizon blooming up through a hot-magenta sky_bot into a brooding purple mid (~40% of the frame), widened dwell — electric and tempestuous. SUNRISE [S]: a low mauve mist, the same magenta family bled down to a pale whisper kept near the horizon. DRAMATIC.',
    {
        # SUNSET — the magenta climbs high; sky_mid goes deep storm-purple while the
        # horizon stays the hottest magenta, the meeting routed through a bright
        # sky_bot so it never greys out.
        0.40: dict(sky_top=(92, 142, 172), sky_mid=(168, 110, 184), sky_bot=(228, 92, 184),  horizon=(244, 56, 152)),
        0.44: dict(sky_top=(84, 130, 168), sky_mid=(156, 94, 184),  sky_bot=(230, 74, 178),  horizon=(244, 40, 144)),
        0.50: dict(sky_top=(74, 114, 158), sky_mid=(142, 80, 182),  sky_bot=(230, 58, 172),  horizon=(240, 28, 134)),
        0.56: dict(sky_top=(54, 94, 142),  sky_mid=(120, 72, 168),  sky_bot=(216, 60, 166),  horizon=(228, 32, 132)),
        0.62: dict(sky_top=(34, 74, 112),  sky_mid=(86, 66, 146),   sky_bot=(184, 70, 158),  horizon=(214, 44, 130)),
        # SUNRISE [S] — same magenta family, a soft low mauve mist: distinctly
        # MAUVE (violet-pink, B held slightly ABOVE R so the hue reads purple, not
        # warm-pink) — hue-separated from row 4's cyan, row 5's lavender and row 6's
        # pink-grey neighbours; value held low so it stays a whisper.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(196, 170, 208), sky_bot=(212, 168, 212), horizon=(214, 162, 214)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(190, 178, 210), sky_bot=(208, 174, 212), horizon=(210, 168, 214)),
    },
)


# 4. Tropical Fuchsia-Cyan — bold fuchsia under a kept Alpine-cyan band, MODERATE.
#    Dawn [C]: clean pale cyan-peach (a cool contrasting hue).
TROPICAL_FUCHSIA_CYAN = _spec(
    'Tropical Fuchsia-Cyan',
    'SUNSET: the duotone clash IS the feature — a bold hot-fuchsia (H322) horizon band held cleanly beneath a KEPT Alpine-cyan sliver in the mid: magenta-below / cyan-above, vivid and intentional. SUNRISE [C]: a clean pale cyan-peach dawn — cool cyan mid warming to the faintest peach horizon, a different and calmer hue than the dusk. MODERATE.',
    {
        # SUNSET — the cyan retention is the signature: sky_mid stays strongly
        # Alpine-cyan while sky_bot/horizon push to true fuchsia, so the clash is
        # sharp and deliberate, kept to a horizon-to-low band (MODERATE).
        0.40: dict(sky_top=(90, 152, 180), sky_mid=(136, 192, 204), sky_bot=(232, 116, 188), horizon=(252, 70, 162)),
        0.50: dict(sky_top=(80, 132, 166), sky_mid=(124, 184, 202), sky_bot=(240, 86, 180),  horizon=(250, 38, 144)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(76, 138, 172),  sky_bot=(190, 90, 172),  horizon=(232, 52, 142)),
        # SUNRISE [C] — distinctly COOL-CYAN dawn: mid AND bot hold a clear Alpine
        # cyan (B leads strongly) and even the horizon keeps B >= R so the whole
        # dawn reads plainly cyan, not warm — hue-separated from row 3's mauve,
        # row 5's lavender and row 6's pink-grey, and clearly cooler than the dusk.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(148, 200, 212), sky_bot=(184, 210, 214), horizon=(200, 210, 210)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(150, 202, 212), sky_bot=(182, 212, 214), horizon=(196, 212, 212)),
    },
)


# 5. Amethyst & Rose — luxe violet->rose, MODERATE.
#    Dawn [S]: subtle lavender haze (same family, far quieter).
AMETHYST_ROSE = _spec(
    'Amethyst & Rose',
    'SUNSET: a luxe amethyst-violet (H280) sky_bot melting into a jewel-rose (H338) horizon — a rich violet-to-rose duotone kept to a horizon-to-low band, the cyan mid breathing above. SUNRISE [S]: a subtle lavender haze, the same violet family pared to a pale low whisper. MODERATE.',
    {
        # SUNSET — amethyst above, rose at the horizon; MODERATE but the violet
        # VALUE is deepened a further ~15% (mid/bot pulled darker and more
        # saturated) so the amethyst has real presence instead of reading timid.
        # Zenith stays cool.
        0.40: dict(sky_top=(94, 146, 176), sky_mid=(146, 112, 192), sky_bot=(172, 84, 188),  horizon=(240, 86, 146)),
        0.50: dict(sky_top=(84, 126, 164), sky_mid=(138, 96, 192),  sky_bot=(166, 66, 184),  horizon=(244, 58, 132)),
        0.62: dict(sky_top=(38, 78, 118),  sky_mid=(90, 78, 152),   sky_bot=(140, 76, 168),  horizon=(222, 70, 132)),
        # SUNRISE [S] — same violet family, a pale lavender-VIOLET haze: distinctly
        # BLUER/cooler than row 3's mauve (B clearly leads R), separated from row 4's
        # cyan (which is greener) and row 6's pink-grey; value held low.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(176, 178, 212), sky_bot=(192, 178, 216), horizon=(198, 174, 218)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(168, 184, 212), sky_bot=(188, 180, 216), horizon=(194, 176, 218)),
    },
)


# 6. Tangerine Inferno — vivid sky-filling orange, DRAMATIC.
#    Dawn [C]: cool pink-grey calm (a contrasting muted cool hue).
TANGERINE_INFERNO = _spec(
    'Tangerine Inferno',
    'SUNSET: a vivid tangerine (H26) that climbs from the horizon through the whole lower-mid frame, cyan held only at the zenith — a sky-filling inferno, widened dwell. SUNRISE [C]: a cool pink-grey calm — a desaturated dove-pink mid over a faint grey-pink horizon, plainly quieter and cooler than the blazing dusk. DRAMATIC.',
    {
        # SUNSET — tangerine floods the lower frame and washes the mid warm; the
        # bloom reaches ~40% of the frame for a true inferno. sky_mid is held a
        # hotter, more saturated apricot-orange (G/B pulled well under R) so the
        # cyan->tangerine top blend never greys to a neutral seam.
        0.40: dict(sky_top=(92, 146, 172), sky_mid=(238, 150, 92),  sky_bot=(252, 152, 70),  horizon=(255, 128, 46)),
        0.44: dict(sky_top=(88, 138, 168), sky_mid=(244, 140, 80),  sky_bot=(255, 142, 60),  horizon=(255, 114, 38)),
        0.50: dict(sky_top=(80, 124, 158), sky_mid=(248, 130, 70),  sky_bot=(255, 130, 50),  horizon=(255, 100, 32)),
        0.56: dict(sky_top=(60, 100, 142), sky_mid=(234, 120, 70),  sky_bot=(252, 122, 52),  horizon=(252, 94, 34)),
        # dusk mid held a saturated amber-orange (not a neutral) so the
        # cyan->tangerine meeting never greys out.
        0.62: dict(sky_top=(36, 78, 116),  sky_mid=(204, 106, 64),  sky_bot=(230, 118, 64),  horizon=(248, 98, 40)),
        # SUNRISE [C] — genuinely COOL pink-grey: B held clearly >= R (R-B negative)
        # so it commits to cool rather than reading neutral-warm, but with R and B
        # both lifted over G for a faint MAGENTA-grey cast that distinguishes it from
        # row 4's greener cyan and the deeper dove-blues of rows 2/8 — a calm, cool
        # counterpoint to the inferno, kept desaturated and low-value.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(184, 184, 204), sky_bot=(198, 184, 210), horizon=(202, 182, 214)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(178, 188, 206), sky_bot=(194, 186, 212), horizon=(196, 184, 214)),
    },
)


# 7. Coral Blaze — warm coral->salmon, MODERATE.
#    Dawn [S]: soft blush whisper (same coral family, far quieter).
CORAL_BLAZE = _spec(
    'Coral Blaze',
    'SUNSET: a warm coral (H14) melting up from a salmon-red horizon, sat lifted so it reads unmistakably coral; the mid stays a cool blush for a clean reef glow, kept to a horizon-to-low band. SUNRISE [S]: a soft blush whisper, the same coral family pared to a pale low band. MODERATE.',
    {
        # SUNSET — salmon-coral; MODERATE, the rich coral held low. The mid carries
        # a more saturated coral-rose (R pushed well above G/B) so the cyan->coral
        # top blend routes through a held warm hue and never greys to a seam.
        0.40: dict(sky_top=(92, 148, 174), sky_mid=(246, 116, 130), sky_bot=(255, 158, 124), horizon=(255, 112, 86)),
        0.50: dict(sky_top=(82, 128, 160), sky_mid=(250, 100, 134), sky_bot=(255, 138, 108), horizon=(255, 78, 56)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(212, 88, 118),  sky_bot=(232, 118, 112), horizon=(252, 98, 86)),
        # SUNRISE [S] — same coral family but pushed COOLER toward blush-GREY /
        # cool-rose: B lifted to near or just past R so the dawn reads a quiet, calm
        # moment plainly cooler than the warm coral dusk — never twinning it; kept to
        # a faint low band.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(190, 184, 202), sky_bot=(214, 186, 204), horizon=(220, 182, 210)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(182, 188, 204), sky_bot=(210, 188, 206), horizon=(214, 184, 210)),
    },
)


# 8. Indigo & Fire — fiery red-orange horizon under a DEEP INDIGO sky, DRAMATIC.
#    Dawn [C]: cool dove/steel-blue (a genuinely cooler hue, B-leaning).
INDIGO_FIRE = _spec(
    'Indigo & Fire',
    'SUNSET: the high-contrast jewel of the set — a fiery red-orange (H18) horizon burning beneath a DEEP INDIGO (H250) sky_bot/mid, the cool indigo pressing down on the flame within a single sky, widened dwell. SUNRISE [C]: a genuinely COOL dove / pale steel-blue dawn (B leads, R-B negative), echoing the indigo coolness at low key so dawn reads as a clearly different, calmer moment than the fiery dusk. DRAMATIC.',
    {
        # SUNSET — the drama is the COLLISION inside one sky: indigo dominates the
        # mid/bot while the horizon holds a thin, fierce red-orange flame. Route the
        # indigo->flame meeting through a violet sky_bot so it doesn't grey out.
        0.40: dict(sky_top=(86, 132, 168), sky_mid=(96, 96, 168),   sky_bot=(150, 92, 152),  horizon=(248, 120, 64)),
        0.44: dict(sky_top=(78, 120, 162), sky_mid=(82, 84, 164),   sky_bot=(146, 80, 142),  horizon=(250, 104, 52)),
        0.50: dict(sky_top=(66, 104, 152), sky_mid=(68, 72, 158),   sky_bot=(142, 70, 132),  horizon=(250, 88, 44)),
        0.56: dict(sky_top=(50, 86, 138),  sky_mid=(58, 66, 146),   sky_bot=(134, 70, 128),  horizon=(244, 84, 46)),
        0.62: dict(sky_top=(32, 70, 112),  sky_mid=(48, 60, 128),   sky_bot=(120, 72, 122),  horizon=(232, 92, 56)),
        # SUNRISE [C] — a genuinely COOL dove / pale steel-blue dawn: B leads
        # clearly (R-B distinctly negative across the whole gradient), echoing the
        # indigo's coolness at low key so the morning reads as an entirely different,
        # calmer moment than the indigo-and-flame dusk. Pushed bluer than before so
        # there is no warm cast left at the horizon.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(162, 188, 212), sky_bot=(182, 200, 220), horizon=(188, 204, 224)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(156, 192, 214), sky_bot=(176, 202, 220), horizon=(182, 204, 224)),
    },
)


# 9. Rose-Gold Royale — opulent hot-pink->gold duotone, MODERATE.
#    Dawn [S]: quiet rose-gold haze (same family, far quieter).
ROSE_GOLD_ROYALE = _spec(
    'Rose-Gold Royale',
    'SUNSET: an opulent duotone — a hot-pink (H335) mid-band sitting over a rich gold (H42) horizon, pink-above / gold-below, celebratory and regal, kept to a horizon-to-low band. SUNRISE [S]: a quiet rose-gold haze, the same pink-gold family pared to a pale low whisper. MODERATE.',
    {
        # SUNSET — explicit two-tone: a hot-pink sky_bot/mid band over a gold
        # horizon core; MODERATE, held low so it reads as a clean rose-gold glow. The
        # mid is a more saturated hot-pink (R/B lifted over G) so the cyan->rose top
        # blend never greys, and the dusk mid is held a saturated rose (not the old
        # grey-blue 120/120/158) so no vertical sample collapses to the mauve seam.
        0.40: dict(sky_top=(92, 148, 174), sky_mid=(236, 102, 184), sky_bot=(252, 120, 160), horizon=(255, 170, 74)),
        0.50: dict(sky_top=(82, 128, 160), sky_mid=(238, 92, 190),  sky_bot=(252, 96, 148),  horizon=(255, 152, 54)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(182, 80, 158),  sky_bot=(214, 106, 148), horizon=(250, 148, 80)),
        # SUNRISE [S] — same rose-gold family but pushed COOLER toward a blush-GREY /
        # cool-rose haze: chroma dropped, value lifted, B lifted to near R so the dawn
        # reads a quiet, calm moment plainly cooler than the warm rose-gold dusk —
        # never twinning it.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(194, 182, 198), sky_bot=(220, 186, 202), horizon=(224, 184, 206)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(182, 188, 200), sky_bot=(216, 188, 204), horizon=(218, 184, 206)),
    },
)


# 10. Aurora Teal-Magenta — bold teal<->magenta "electric" aurora sky, DRAMATIC.
#     Dawn [C]: gentle peach calm (a warm, quiet contrast to the electric dusk).
AURORA_TEAL_MAGENTA = _spec(
    'Aurora Teal-Magenta',
    'SUNSET: an electric aurora sky — a bold magenta (H320) horizon arcing up into a luminous TEAL (H180) mid that ties to the Alpine cyan, a teal<->magenta charge filling the lower-mid frame, widened dwell. SUNRISE [C]: a gentle peach calm, a soft warm low glow that reads quiet and different from the electric dusk. DRAMATIC.',
    {
        # SUNSET — the aurora charge: a hot magenta horizon meeting a glowing teal
        # mid (the teal is on-brand with the Alpine cyan), the bloom lifted high so
        # the electric clash fills the lower-mid frame.
        0.40: dict(sky_top=(88, 152, 182), sky_mid=(80, 188, 184),  sky_bot=(196, 132, 196), horizon=(244, 78, 168)),
        0.44: dict(sky_top=(82, 146, 180), sky_mid=(66, 188, 182),  sky_bot=(202, 116, 194), horizon=(246, 60, 162)),
        0.50: dict(sky_top=(72, 134, 174), sky_mid=(54, 186, 180),  sky_bot=(208, 100, 192), horizon=(246, 44, 154)),
        0.56: dict(sky_top=(54, 110, 158), sky_mid=(52, 168, 174),  sky_bot=(198, 96, 184),  horizon=(236, 48, 152)),
        0.62: dict(sky_top=(34, 78, 120),  sky_mid=(52, 130, 158),  sky_bot=(172, 92, 174),  horizon=(222, 58, 146)),
        # SUNRISE [C] — a COOL cyan-peach dawn (like row 4): the mid AND bot hold a
        # clear Alpine cyan with B leading, and even the horizon keeps B >= R, so the
        # dawn reads genuinely cool (R-B negative) with only the faintest warm breath
        # — a calm, plainly different counterpoint to the electric dusk, never a
        # softer warm mirror of it.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(160, 196, 206), sky_bot=(192, 206, 210), horizon=(204, 204, 212)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(158, 198, 208), sky_bot=(190, 208, 212), horizon=(200, 206, 214)),
    },
)


# Sheet order matches the 10 fresh directions in the brief.
CONCEPTS = [
    ('molten_gold_ember', MOLTEN_GOLD_EMBER),
    ('volcanic_crimson', VOLCANIC_CRIMSON),
    ('magenta_storm', MAGENTA_STORM),
    ('tropical_fuchsia_cyan', TROPICAL_FUCHSIA_CYAN),
    ('amethyst_rose', AMETHYST_ROSE),
    ('tangerine_inferno', TANGERINE_INFERNO),
    ('coral_blaze', CORAL_BLAZE),
    ('indigo_fire', INDIGO_FIRE),
    ('rose_gold_royale', ROSE_GOLD_ROYALE),
    ('aurora_teal_magenta', AURORA_TEAL_MAGENTA),
]
