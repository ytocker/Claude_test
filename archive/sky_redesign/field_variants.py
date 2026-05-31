"""
Sky COLOR-FIELD exploration — 8 high-end treatments of the pure atmosphere.

Scope: the sky's own color field only — the blue that grades to night and back.
NO objects (no clouds / sun / moon / stars / god-rays); those are composited by
the rest of the game. Each treatment is judged purely on how gorgeous the
gradient itself reads across the full day cycle.

Every treatment is built on `game.sky_field` (OKLab perceptual interpolation +
non-uniform eased stops + Bayer dither) so they share the "stop looking like a
PowerPoint gradient" foundation and differ only in palette philosophy. Each
synthesizes its richer 5–7 stop ramp from the four existing biome anchors
(`sky_top / sky_mid / sky_bot / horizon`) via OKLab ops, so it renders against
the current keyframes with no biome.py edit.

Contract (consumed by render_field_variants.py and the design loop):
    draw_<name>(w, h, palette) -> opaque pygame.Surface of size (w, h)
    VARIANTS:      {name: func}
    VARIANT_NAMES: [name, ...]            # display order
    VARIANT_NOTES: {name: one-line intent}
"""
import pygame

from game.sky_field import (
    make_sky_field, oklab_ramp, oklab_lerp, srgb_to_oklab,
    with_value, shift_temperature, radial_glow,
)


def _luma(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def _nightf(palette):
    """Continuous night-ness in [0,1] from zenith luminance — 1 at deep night,
    0 by full day. Lets a treatment morph smoothly across the cross-faded
    buckets instead of switching on a hard phase gate."""
    lum = _luma(palette['sky_top'])
    return max(0.0, min(1.0, (95.0 - lum) / 75.0))


def _pastelize(rgb, amt):
    """Lift toward a soft tint: raise OKLab lightness, ease saturation down."""
    L, a, b = srgb_to_oklab(rgb)
    from game.sky_field import oklab_to_srgb
    return oklab_to_srgb((min(1.0, L + 0.10 * amt), a * (1 - 0.35 * amt),
                          b * (1 - 0.35 * amt)))


def _grain(w, h, amp):
    """A reusable high-frequency dither/grain pair for the riso & watercolor
    looks — same Bayer machinery, cranked, applied add+sub."""
    from game.sky_field import _dither_overlays
    return _dither_overlays(w, h, amp)


# ── 1. Atmospheric True — physical Rayleigh/Mie realism ──────────────────────
def draw_atmospheric_true(w, h, palette):
    top, mid, bot, hor = (palette['sky_top'], palette['sky_mid'],
                          palette['sky_bot'], palette['horizon'])
    nf = _nightf(palette)
    # Deepest, most-saturated value sits at the zenith; the change compresses
    # toward the horizon where you look through the most air. A pale Mie haze
    # band sits just above the warm horizon.
    haze = oklab_lerp(bot, (255, 255, 255), 0.22 * (1 - nf))
    stops = [
        (0.00, with_value(top, -0.05)),
        (0.26, top),
        (0.52, mid),
        (0.74, oklab_lerp(mid, bot, 0.55)),
        (0.88, haze),
        (1.00, hor),
    ]
    surf = make_sky_field(w, h, stops)
    # Soft Mie forward-glow blooming up from the horizon — a broad, low wash
    # (center pushed well below frame so only the faint tail enters) so it lifts
    # the horizon warmth without ever reading as a sun disc. Warmer & stronger
    # at low sun, gone at night.
    g = (1 - nf)
    glow = radial_glow(w, h, w * 0.5, h * 1.22, int(h * 0.7),
                       shift_temperature(hor, 0.6), int(34 * g))
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    return surf


# ── 2. Hiroshige Bokashi — ukiyo-e graded Prussian-blue band ─────────────────
def draw_hiroshige_bokashi(w, h, palette):
    top, mid, bot, hor = (palette['sky_top'], palette['sky_mid'],
                          palette['sky_bot'], palette['horizon'])
    # Prussian-blue lineage: cool the zenith, fade to a pale band low, hold the
    # warm horizon as the futa-iro second ink. Most of the grade lives in the
    # bottom third like a hand-pulled ichimonji bokashi.
    deep = shift_temperature(with_value(top, -0.03), -0.5)
    pale = oklab_lerp(bot, (245, 245, 235), 0.30)
    stops = [
        (0.00, deep),
        (0.42, oklab_lerp(deep, mid, 0.7)),
        (0.66, mid),
        (0.82, oklab_lerp(mid, pale, 0.6)),
        (0.93, pale),
        (1.00, hor),
    ]
    # Slightly stronger dither for the printed-ink tooth.
    return make_sky_field(w, h, stops, dither_amp=2.6)


# ── 3. Alto Plum — stylized non-literal pastel ───────────────────────────────
def draw_alto_plum(w, h, palette):
    top, mid, bot, hor = (palette['sky_top'], palette['sky_mid'],
                          palette['sky_bot'], palette['horizon'])
    nf = _nightf(palette)
    # Push the whole field toward a plum/rose register and pastel it — premium,
    # non-literal "Alto's Odyssey" mood that leans on palette curation, not
    # gradient complexity.
    plum = shift_temperature(oklab_lerp(top, (120, 70, 130), 0.30 * (1 - nf)),
                             0.15)
    stops = [
        (0.00, _pastelize(plum, 0.25 * (1 - nf))),
        (0.40, _pastelize(mid, 0.45 * (1 - nf))),
        (0.68, _pastelize(oklab_lerp(mid, bot, 0.5), 0.5 * (1 - nf))),
        (0.86, _pastelize(bot, 0.55 * (1 - nf))),
        (1.00, _pastelize(hor, 0.35 * (1 - nf))),
    ]
    return make_sky_field(w, h, stops)


# ── 4. Gris Watercolor — soft painterly wash, broken color ───────────────────
def draw_gris_watercolor(w, h, palette):
    top, mid, bot, hor = (palette['sky_top'], palette['sky_mid'],
                          palette['sky_bot'], palette['horizon'])
    # Lower the contrast and desaturate slightly (a wash, not a poster), then
    # inject micro temperature counter-change between bands for "broken color".
    def wash(c):
        L, a, b = srgb_to_oklab(c)
        from game.sky_field import oklab_to_srgb
        return oklab_to_srgb((0.20 + L * 0.72, a * 0.8, b * 0.8))
    stops = [
        (0.00, shift_temperature(wash(top), -0.25)),
        (0.30, shift_temperature(wash(oklab_lerp(top, mid, 0.6)), 0.15)),
        (0.55, wash(mid)),
        (0.78, shift_temperature(wash(oklab_lerp(mid, bot, 0.6)), 0.20)),
        (0.92, wash(bot)),
        (1.00, shift_temperature(wash(hor), 0.10)),
    ]
    surf = make_sky_field(w, h, stops)
    # Faint paper grain so the flat washes read hand-laid rather than digital.
    pos, neg = _grain(w, h, 1.4)
    surf.blit(pos, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    surf.blit(neg, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
    return surf


# ── 5. Mesh Glow — multi-point field, light not ramp ─────────────────────────
def draw_mesh_glow(w, h, palette):
    top, mid, bot, hor = (palette['sky_top'], palette['sky_mid'],
                          palette['sky_bot'], palette['horizon'])
    nf = _nightf(palette)
    # A cool, simple base vertical field, then one large soft warm glow pool low
    # and off-center so the sky reads as lit rather than a literal top-to-bottom
    # ramp.
    stops = [
        (0.00, with_value(top, -0.02)),
        (0.45, mid),
        (0.80, oklab_lerp(mid, bot, 0.7)),
        (1.00, oklab_lerp(bot, hor, 0.5)),
    ]
    surf = make_sky_field(w, h, stops)
    # One broad, soft warm light pool with its center pushed off the lower-left
    # corner so only the falloff tail washes diagonally across the frame — the
    # sky reads as lit from a direction, never as a disc or a hard arc. Low
    # alpha keeps it from clipping to white over the already-bright horizon.
    g = 0.35 + 0.65 * (1 - nf)
    pool = radial_glow(w, h, w * 0.12, h * 1.08, int(h * 1.05),
                       shift_temperature(hor, 0.4), int(44 * g))
    surf.blit(pool, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    return surf


# ── 6. Riso Posterized — tasteful hard bands + print grain ───────────────────
def draw_riso_posterized(w, h, palette):
    top, mid, bot, hor = (palette['sky_top'], palette['sky_mid'],
                          palette['sky_bot'], palette['horizon'])
    nf = _nightf(palette)
    levels = 5 if nf < 0.6 else 4
    stops = [
        (0.00, with_value(top, -0.03)),
        (0.45, mid),
        (0.78, oklab_lerp(mid, bot, 0.6)),
        (0.92, bot),
        (1.00, hor),
    ]
    cols = oklab_ramp(stops, levels, ease=False)
    surf = pygame.Surface((w, h))
    for i, c in enumerate(cols):
        y0 = int(i * h / levels)
        y1 = int((i + 1) * h / levels)
        pygame.draw.rect(surf, c, (0, y0, w, y1 - y0))
    # 1–2-ink riso grain over the flat bands.
    pos, neg = _grain(w, h, 3.2)
    surf.blit(pos, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    surf.blit(neg, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
    return surf


# ── 7. Belt-of-Venus Twilight — counter-change + horizon ember ───────────────
def draw_belt_of_venus(w, h, palette):
    top, mid, bot, hor = (palette['sky_top'], palette['sky_mid'],
                          palette['sky_bot'], palette['horizon'])
    nf = _nightf(palette)
    # Maximize the warm/cool vertical axis: cool the upper sky, then a luminous
    # pink/peach ember band sits ABOVE a slightly darker horizon (the real
    # belt-of-Venus), strongest at dusk/dawn.
    bv = 0.5 + 0.5 * (1 - abs(nf - 0.5) * 2)  # peaks at twilight
    ember = shift_temperature(oklab_lerp(hor, (255, 190, 200), 0.45 * bv), 0.3)
    stops = [
        (0.00, shift_temperature(with_value(top, -0.03), -0.4)),
        (0.40, shift_temperature(mid, -0.15)),
        (0.66, oklab_lerp(mid, bot, 0.5)),
        (0.82, ember),
        (0.92, with_value(ember, -0.04)),
        (1.00, with_value(hor, -0.05)),
    ]
    return make_sky_field(w, h, stops)


# ── 8. Deep-Space Night-led — jaw-dropping night, calm by day ────────────────
def draw_deep_space(w, h, palette):
    top, mid, bot, hor = (palette['sky_top'], palette['sky_mid'],
                          palette['sky_bot'], palette['horizon'])
    nf = _nightf(palette)
    # Authored around night: a graded navy depth with a faint milky temperature
    # band drifting through the mid sky (a hue shift, NOT stars). By day the
    # same structure collapses to a calm, rich high-altitude blue.
    navy = shift_temperature(with_value(top, -0.06 * nf), -0.3 * nf)
    milky = shift_temperature(oklab_lerp(mid, (190, 200, 225), 0.25 * nf),
                              0.15 * nf)
    stops = [
        (0.00, navy),
        (0.30, oklab_lerp(navy, mid, 0.6)),
        (0.50, milky),
        (0.74, oklab_lerp(milky, bot, 0.7)),
        (0.90, bot),
        (1.00, hor),
    ]
    surf = make_sky_field(w, h, stops, dither_amp=2.4)
    return surf


VARIANTS = {
    "atmospheric_true":  draw_atmospheric_true,
    "hiroshige_bokashi": draw_hiroshige_bokashi,
    "alto_plum":         draw_alto_plum,
    "gris_watercolor":   draw_gris_watercolor,
    "mesh_glow":         draw_mesh_glow,
    "riso_posterized":   draw_riso_posterized,
    "belt_of_venus":     draw_belt_of_venus,
    "deep_space":        draw_deep_space,
}
VARIANT_NAMES = list(VARIANTS.keys())
VARIANT_NOTES = {
    "atmospheric_true":  "Rayleigh/Mie realism: deep zenith, pale Mie haze, warm horizon bloom",
    "hiroshige_bokashi": "Ukiyo-e graded Prussian-blue ichimonji bokashi + futa-iro warm ink",
    "alto_plum":         "Stylized non-literal pastel plum/rose — palette curation over math",
    "gris_watercolor":   "Soft low-contrast wash, broken-color counter-change, paper grain",
    "mesh_glow":         "Off-vertical light pools — reads as lit, not a literal ramp",
    "riso_posterized":   "Tasteful 4–5 flat bands + 1–2-ink riso grain",
    "belt_of_venus":     "Counter-change axis + luminous pink ember above a darker horizon",
    "deep_space":        "Night-led graded navy + milky hue band; calm rich blue by day",
}
