"""Render docs/flight_log/sky_dial/round_1.png — the SKY DIAL flight-log screen.

SKY DIAL reads the whole day as a clock face: 12 o'clock is phase 0.0 and one
clockwise revolution is one full day cycle. The colour annulus is sampled
straight from `biome.palette_for_phase`, and every event arc is derived from the
live `weather` / `config` constants rather than hand-placed, so the dial is a
truthful instrument for the day the player actually flew.

Curved geometry is built as polygon quad fans on a x3 supersampled disc and
smoothscaled down — `pygame.draw.arc` has no width/AA control we can trust and
`gfxdraw` is off-limits on the WASM target. Only the disc is supersampled (not
the whole 360x640 screen) so the peak surface stays ~1008^2 and every glyph is
rendered once, crisply, at final size.

The unflown sweep is desaturated at the COLOUR SOURCE (each quad picks a
chroma-reduced tone when its phase is past the death phase) instead of by
post-processing the raster: numpy is not a dependency here, and source-side
desaturation also gives a clean edge exactly on the death angle.
"""
import math
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import COIN_RUSH_INTERVAL, CLOWN_START_PILLAR, CYCLE_FINALE_RUSH_PILLARS
from game.biome import PHASE_BOUNDARIES, palette_for_phase
from game.draw import NEAR_BLACK, UI_CREAM, WHITE
from game.hud import _GOLD_BRIGHT, _GOLD_MUTED, _font, _na_plate, _outlined_text
from game import weather as _weather


ROOT = pathlib.Path(__file__).parent.parent
OUT = ROOT / "docs" / "flight_log" / "sky_dial" / "round_1.png"

W, H = 360, 640

# ── mock run ─────────────────────────────────────────────────────────────────
RUN_PILLARS = 25
RUN_SCORE = 25
RUN_COINS = 34
RUN_TIME_S = 47
RUN_DAY = 1
DEATH_PHASE = _weather._phase_for_pillar(RUN_PILLARS)

DAY_PILLARS = 175

# ── dial geometry (final-screen px) ──────────────────────────────────────────
DIAL_C = (180, 280)
R_HUB = 70
R_PLAY_IN, R_PLAY_OUT = 77, 86       # gameplay sub-track
R_WX_IN, R_WX_OUT = 90, 99           # weather sub-track
R_SKY_IN, R_SKY_OUT = 101, 129       # colour annulus (3 stacked sky bands)
R_TICK_OUT = 137
# A near-horizontal phase name is as wide as the whole margin between the tick
# ring and the canvas edge, so the ring is sized to let those names start just
# PAST the tick tip (R_LAB_ORTHO, edge-anchored) instead of centred on top of
# it. Diagonal names have slack and sit centred further out.
R_LAB_ORTHO = 139
R_LAB_DIAG = 149
R_ART = 168                          # everything baked on the disc fits inside

SS = 3
SS_SIDE = R_ART * 2 * SS
CX = CY = SS_SIDE // 2
# Quads are grown a sliver past their end angle so neighbouring steps overlap;
# without it the fan shows hairline seams that survive the downscale.
_SEAM = math.radians(0.14)

# ── palette ──────────────────────────────────────────────────────────────────
BG_TOP = (15, 15, 30)
BG_BOT = (24, 22, 44)
DISC_BASE = (18, 18, 32)
CHANNEL_BG = (30, 30, 46)
C_THERMAL = (220, 160, 40)
C_RAIN = (80, 100, 130)
C_SNOW = (220, 225, 235)
C_CLOWN = (100, 60, 180)
C_DEATH = (232, 58, 58)

UNFLOWN_CHROMA = 0.40


def _desat(c, k=UNFLOWN_CHROMA):
    """Pull a colour toward its own luminance — the unflown sweep loses chroma
    but keeps its value, so the ring never reads as 'switched off'."""
    lum = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    return tuple(max(0, min(255, int(round(lum + (ch - lum) * k)))) for ch in c[:3])


def _rad(phase):
    return math.radians(-90.0 + 360.0 * phase)


def _pt(phase, r, cx=DIAL_C[0], cy=DIAL_C[1]):
    a = _rad(phase)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def _quad(surf, r_in, r_out, p0, p1, color, alpha=255):
    a0, a1 = _rad(p0), _rad(p1) + _SEAM
    ri, ro = r_in * SS, r_out * SS
    pts = [
        (CX + ri * math.cos(a0), CY + ri * math.sin(a0)),
        (CX + ro * math.cos(a0), CY + ro * math.sin(a0)),
        (CX + ro * math.cos(a1), CY + ro * math.sin(a1)),
        (CX + ri * math.cos(a1), CY + ri * math.sin(a1)),
    ]
    pygame.draw.polygon(surf, (*color, alpha), pts)


def _band(surf, r_in, r_out, p0, p1, color, alpha=255, step_deg=2.0):
    n = max(1, int(math.ceil((p1 - p0) * 360.0 / step_deg)))
    for i in range(n):
        _quad(surf, r_in, r_out,
              p0 + (p1 - p0) * i / n, p0 + (p1 - p0) * (i + 1) / n,
              color, alpha)


def _event_arc(surf, r_in, r_out, p0, p1, color, cap=True):
    """Event arc, split at the death phase so the unflown remainder renders in
    its desaturated tone with a hard edge exactly on the needle."""
    for a, b, flown in ((p0, min(p1, DEATH_PHASE), True),
                        (max(p0, DEATH_PHASE), p1, False)):
        if b <= a:
            continue
        _band(surf, r_in, r_out, a, b, color if flown else _desat(color),
              step_deg=1.0)
    _band(surf, r_in, r_in + 1, p0, p1, NEAR_BLACK, step_deg=1.5)
    _band(surf, r_out - 1, r_out, p0, p1, NEAR_BLACK, step_deg=1.5)
    if cap:
        for p in (p0, p1):
            _quad(surf, r_in, r_out, p - 0.0005, p + 0.0005, NEAR_BLACK)


# ── event spans, read off the live simulation constants ──────────────────────

def _span(fn, thr=0.05, lo=0.0, hi=1.0, n=2000):
    on = [i / n for i in range(int(lo * n), int(hi * n)) if fn(i / n) > thr]
    return (min(on), max(on)) if on else None


THERMAL_SPAN = _span(_weather.thermal_intensity)
RAIN_SPAN = _span(_weather.rain_intensity)
# Snow is not its own intensity curve — it builds inside the late storm, gated
# on both the storm level and a phase floor, so its span is read the same way
# the simulation gates it.
_snow_on = [i / 2000 for i in range(2000)
            if i / 2000 >= _weather._SNOW_LOWER_EDGE
            and _weather.storm_intensity(i / 2000) >= _weather.WEATHER_SNOW_ON_WI]
SNOW_SPAN = (min(_snow_on), max(_snow_on))
CLOWN_SPAN = (_weather._phase_for_pillar(CLOWN_START_PILLAR),
              _weather._phase_for_pillar(CLOWN_START_PILLAR + 25))
RUSH_PHASES = [_weather._phase_for_pillar(p)
               for p in range(COIN_RUSH_INTERVAL, DAY_PILLARS, COIN_RUSH_INTERVAL)]
FINALE_SPAN = (_weather._phase_for_pillar(DAY_PILLARS - CYCLE_FINALE_RUSH_PILLARS),
               1.0)

_SHORT = {"GOLDEN HOUR": "GOLDEN"}


# ── the baked disc ───────────────────────────────────────────────────────────

def _build_disc():
    ss = pygame.Surface((SS_SIDE, SS_SIDE), pygame.SRCALPHA)

    pygame.draw.circle(ss, DISC_BASE, (CX, CY), R_SKY_IN * SS)

    # Colour annulus. Stepping at 2 deg keeps the gradient smooth at final size;
    # the death phase is forced in as a step edge so the flown/unflown boundary
    # lands on the needle rather than on the nearest 2-deg tick.
    edges = sorted(set([i / 180.0 for i in range(181)] + [DEATH_PHASE]))
    for p0, p1 in zip(edges, edges[1:]):
        mid = 0.5 * (p0 + p1)
        pal = palette_for_phase(mid)
        flown = mid <= DEATH_PHASE
        for r_in, r_out, key in ((R_SKY_IN, 108, "sky_bot"),
                                 (108, 118, "sky_mid"),
                                 (118, R_SKY_OUT, "sky_top")):
            col = tuple(int(v) for v in pal[key])
            _quad(ss, r_in, r_out, p0, p1, col if flown else _desat(col))

    # Two concentric channels always drawn full-circle, so an empty stretch
    # still reads as "a track with nothing in it" rather than as blank disc.
    for r_in, r_out in ((R_PLAY_IN, R_PLAY_OUT), (R_WX_IN, R_WX_OUT)):
        _band(ss, r_in, r_out, 0.0, 1.0, CHANNEL_BG)
        _band(ss, r_in, r_in + 1, 0.0, 1.0, NEAR_BLACK)
        _band(ss, r_out - 1, r_out, 0.0, 1.0, NEAR_BLACK)

    _event_arc(ss, R_WX_IN, R_WX_OUT, *THERMAL_SPAN, C_THERMAL)
    _event_arc(ss, R_WX_IN, R_WX_OUT, *RAIN_SPAN, C_RAIN)
    _event_arc(ss, R_WX_IN, R_WX_OUT, *SNOW_SPAN, C_SNOW)

    _event_arc(ss, R_PLAY_IN, R_PLAY_OUT, *CLOWN_SPAN, C_CLOWN)
    for ph in RUSH_PHASES:
        _event_arc(ss, R_PLAY_IN, R_PLAY_OUT,
                   ph - 0.0044, ph + 0.0044, _GOLD_BRIGHT)
    _event_arc(ss, R_PLAY_IN, R_PLAY_OUT, *FINALE_SPAN, _GOLD_BRIGHT)

    # Phase hairlines across the sky annulus make the seven segments countable
    # inside an otherwise continuous gradient.
    for frac, _name in PHASE_BOUNDARIES:
        _quad(ss, R_SKY_IN, R_SKY_OUT, frac - 0.0007, frac + 0.0007,
              (255, 255, 255), 62)

    # Warm bloom on the flown arc only: the "lit" half of the instrument.
    for i in range(9):
        _band(ss, R_SKY_OUT + i, R_SKY_OUT + i + 1, 0.0, DEATH_PHASE,
              _GOLD_BRIGHT, int(78 * (1.0 - i / 9.0)))

    # Tick spurs stay full-white through the unflown sweep — structure must not
    # dim, or the later phase names stop reading as reachable places.
    for frac, _name in PHASE_BOUNDARIES:
        a = _rad(frac)
        p0 = (CX + R_SKY_OUT * SS * math.cos(a), CY + R_SKY_OUT * SS * math.sin(a))
        p1 = (CX + R_TICK_OUT * SS * math.cos(a), CY + R_TICK_OUT * SS * math.sin(a))
        pygame.draw.line(ss, WHITE, p0, p1, 2 * SS)

    # Hub well.
    for r in range(R_HUB, 0, -1):
        t = r / R_HUB
        col = tuple(int(round(a + (b - a) * t))
                    for a, b in zip((36, 38, 54), NEAR_BLACK))
        pygame.draw.circle(ss, col, (CX, CY), r * SS)
    pygame.draw.circle(ss, (*_GOLD_MUTED, 110), (CX, CY), R_HUB * SS, 2 * SS)

    _draw_needle(ss)

    out = pygame.transform.smoothscale(ss, (SS_SIDE // SS, SS_SIDE // SS))
    del ss
    return out


def _draw_needle(ss):
    a = _rad(DEATH_PHASE)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux

    def at(r, off=0.0):
        return (CX + (r * SS) * ux + (off * SS) * px,
                CY + (r * SS) * uy + (off * SS) * py)

    # Red halo built from stacked wide strokes: alpha accumulates toward the
    # core, giving a soft falloff without a per-pixel blur. The white core is
    # kept wide enough that the downscale can't dilute it into the halo — value,
    # not hue, is what has to carry the marker in greyscale.
    for w, alpha in ((12, 30), (9, 42), (6.5, 58), (4.5, 78)):
        pygame.draw.line(ss, (*C_DEATH, alpha), at(R_HUB + 2), at(R_TICK_OUT),
                         int(w * SS))
    pygame.draw.line(ss, WHITE, at(R_HUB + 2), at(R_TICK_OUT), int(3 * SS))

    kite_red = [at(135), at(141, 8), at(158), at(141, -8)]
    kite_white = [at(138.5), at(143.5, 3.8), at(153), at(143.5, -3.8)]
    for w, alpha in ((5, 40), (3, 60)):
        pygame.draw.polygon(ss, (*C_DEATH, alpha), kite_red, int(w * SS))
    pygame.draw.polygon(ss, C_DEATH, kite_red)
    pygame.draw.polygon(ss, NEAR_BLACK, kite_red, SS)
    pygame.draw.polygon(ss, WHITE, kite_white)

    # Exact death point, sitting on the sky band it happened under.
    dot = at(115)
    pygame.draw.circle(ss, NEAR_BLACK, dot, int(5.0 * SS))
    pygame.draw.circle(ss, WHITE, dot, int(3.6 * SS))


# ── final-size text helpers ──────────────────────────────────────────────────

def _txt(surf, msg, size, color, shadow=True, **anchor):
    f = _font(size, True)
    img = f.render(msg, True, color)
    r = img.get_rect(**anchor)
    if shadow:
        sh = f.render(msg, True, NEAR_BLACK)
        sh.set_alpha(190)
        surf.blit(sh, (r.x + 1, r.y + 1))
    surf.blit(img, r.topleft)
    return r


def _label_anchor(frac):
    """Quadrant anchoring for a phase name — no rotated text, just the right
    rect edge pinned outside the tick tip."""
    a = _rad(frac)
    ca, sa = math.cos(a), math.sin(a)
    ortho = tuple(round(v) for v in _pt(frac, R_LAB_ORTHO))
    if ca > 0.6:
        return dict(midleft=ortho)
    if ca < -0.6:
        return dict(midright=ortho)
    if sa < -0.6:
        return dict(midbottom=ortho)
    if sa > 0.6:
        return dict(midtop=ortho)
    return dict(center=tuple(round(v) for v in _pt(frac, R_LAB_DIAG)))


def _legend_chip(surf, x, y, color, label, outline=None):
    pygame.draw.rect(surf, color, (x, y - 4, 9, 9), border_radius=2)
    pygame.draw.rect(surf, outline or NEAR_BLACK, (x, y - 4, 9, 9), 1,
                     border_radius=2)
    r = _txt(surf, label, 8, (188, 194, 214), midleft=(x + 13, y))
    return r.right


# ── the screen ───────────────────────────────────────────────────────────────

def build_screen():
    s = pygame.Surface((W, H))
    for y in range(H):
        t = y / (H - 1)
        s.fill(tuple(int(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOT)),
               (0, y, W, 1))

    # Faint halo so the disc sits in light rather than on a flat field.
    glow = pygame.Surface((W, H), pygame.SRCALPHA)
    for i in range(26):
        pygame.draw.circle(glow, (70, 90, 150, 4), DIAL_C, R_ART + 26 - i)
    s.blit(glow, (0, 0))

    disc = _build_disc()
    s.blit(disc, (DIAL_C[0] - R_ART, DIAL_C[1] - R_ART))

    _outlined_text(s, "FLIGHT LOG", (W // 2, 42), 18, px=2, shadow_offset=(2, 3))
    _txt(s, f"DAY {RUN_DAY}", 9, _GOLD_MUTED, midleft=(14, 42))

    # Phase names ride outside the tick ring, anchored by quadrant so no name is
    # ever centred on its own spur. Unflown names lose chroma but not value —
    # all seven have to stay readable as places the player could still get to.
    for frac, name in PHASE_BOUNDARIES:
        col = UI_CREAM if frac <= DEATH_PHASE else _desat(UI_CREAM)
        f = _font(8, True)
        txt = _SHORT.get(name, name)
        img = f.render(txt, True, col)
        r = img.get_rect(**_label_anchor(frac))
        r.clamp_ip(pygame.Rect(4, 0, W - 8, H))
        sh = f.render(txt, True, NEAR_BLACK)
        sh.set_alpha(200)
        s.blit(sh, (r.x + 1, r.y + 1))
        s.blit(img, r.topleft)

    # Hub readout.
    _txt(s, f"PILLAR {RUN_PILLARS}", 9, _GOLD_MUTED, center=(180, 254))
    _txt(s, str(RUN_SCORE), 36, _GOLD_BRIGHT, center=(180, 281))
    _txt(s, f"{round(DEATH_PHASE * 100)}% OF THE DAY", 10, UI_CREAM,
         center=(180, 306))

    # Needle callout, parked in the free top-right corner and led back along the
    # OUTSIDE of the disc so the "~2 o'clock = early morning" reading is
    # explicit without the leader ever crossing the ring.
    tip = tuple(round(v) for v in _pt(DEATH_PHASE, 158))
    _txt(s, "EARLY MORNING", 8, UI_CREAM, midright=(352, 118))
    pygame.draw.lines(s, (150, 158, 182), False, [tip, (344, 160), (344, 128)], 1)
    pygame.draw.circle(s, C_DEATH, (344, 127), 2)

    _stat_plates(s)
    _legend(s)
    _back_pill(s)
    return s


def _stat_plates(s):
    labels = (("TIME", f"0:{RUN_TIME_S:02d}"),
              ("COINS", str(RUN_COINS)),
              ("PILLARS", str(RUN_PILLARS)))
    x, y, w, h, gap = 18, 452, 102, 68, 9
    for i, (cap, val) in enumerate(labels):
        rect = pygame.Rect(x + i * (w + gap), y, w, h)
        _na_plate(s, rect, cut=7, round_r=8)
        _txt(s, cap, 9, _GOLD_BRIGHT, center=(rect.centerx, rect.y + 17))
        _txt(s, val, 24, (252, 244, 220), center=(rect.centerx, rect.y + 44))


def _legend(s):
    rows = (
        ((C_THERMAL, "THERMAL"), (C_RAIN, "RAIN"), (C_SNOW, "SNOW")),
        ((C_CLOWN, "CLOWN"), (_GOLD_BRIGHT, "COIN RUSH"), (C_DEATH, "YOU FELL")),
    )
    for ri, row in enumerate(rows):
        y = 534 + ri * 15
        x = 30
        for col, lab in row:
            x = _legend_chip(s, x, y, col, lab) + 16
    _txt(s, "OUTER RING = WEATHER   INNER RING = EVENTS", 7, (120, 126, 148),
         midright=(348, 541), shadow=False)


def _back_pill(s):
    rect = pygame.Rect(0, 0, 112, 32)
    rect.center = (180, 590)
    pygame.draw.rect(s, (26, 26, 46), rect, border_radius=16)
    pygame.draw.rect(s, _GOLD_BRIGHT, rect, 2, border_radius=16)
    _txt(s, "BACK", 14, UI_CREAM, center=rect.center)


# ── review sheet ─────────────────────────────────────────────────────────────

SHEET_BG = (18, 18, 26)
PANEL_EDGE = (58, 62, 84)
SHEET_HI = (236, 240, 250)
SHEET_LO = (156, 164, 186)


def _sheet_txt(sheet, msg, size, color, **anchor):
    f = _font(size, True)
    img = f.render(msg, True, color)
    r = img.get_rect(**anchor)
    sheet.blit(img, r.topleft)
    return r


def _framed(sheet, surf, x, y, label):
    pygame.draw.rect(sheet, PANEL_EDGE,
                     (x - 2, y - 2, surf.get_width() + 4, surf.get_height() + 4), 2)
    sheet.blit(surf, (x, y))
    _sheet_txt(sheet, label, 13, SHEET_LO,
               midbottom=(x + surf.get_width() // 2, y - 8))


NOTES = [
    "CONSTRUCTION  x3 supersampled disc (1008px), polygon quad fans only - no draw.arc, no gfxdraw; smoothscaled to 336px and freed. Every glyph is drawn once at final size, so no text passes through the downscale.",
    "ANNULUS  180 x 2deg steps, three stacked sky bands (sky_bot / sky_mid / sky_top) sampled from biome.palette_for_phase. 12 o'clock = phase 0.0, clockwise = one full day.",
    "TWO SUB-TRACKS  weather r90-99 (thermal / rain / snow) and gameplay r77-86 (clown gauntlet / 11 coin rushes / finale). Radius separation resolves the clown-vs-rain overlap; both channels are drawn full-circle so an empty stretch still reads as a track with nothing in it.",
    "DATA  every arc is derived from live constants - weather.thermal_intensity / rain_intensity / storm_intensity spans, CLOWN_START_PILLAR, COIN_RUSH_INTERVAL, CYCLE_FINALE_RUSH_PILLARS - not hand-placed.",
    "UNFLOWN SWEEP  chroma x0.40 applied at the colour source, value untouched: nothing darkens, tick spurs stay full white and all seven phase names stay legible.",
    "DEATH MARKER  angular needle plus kite pennant, white core inside a red halo. Shape and value carry the read - see the greyscale panel. Its ~2 o'clock angle is what the EARLY MORNING callout names.",
    "LABELS  phase names are quadrant-anchored (midleft / midright / midtop / midbottom outside the tick tip, centred on the diagonals) rather than centred on the ring - a centred GOLDEN or PREDAWN would sit on its own spur or run off the 360px edge.",
]


def build_sheet(screen):
    sw, sh = 1256, 1030
    sheet = pygame.Surface((sw, sh))
    sheet.fill(SHEET_BG)

    _sheet_txt(sheet, "SKY DIAL", 30, _GOLD_BRIGHT, topleft=(48, 30))
    _sheet_txt(sheet, "Flight Log concept  -  round 1", 15, SHEET_LO,
               topleft=(48, 68))
    _sheet_txt(sheet, "run: pillar 25  -  phase 0.184  -  47s  -  day 1",
               13, SHEET_LO, topright=(sw - 48, 40))
    _sheet_txt(sheet, "no current design - first pass", 13, (110, 116, 138),
               topright=(sw - 48, 62))
    pygame.draw.line(sheet, PANEL_EDGE, (48, 100), (sw - 48, 100), 1)

    _framed(sheet, screen, 48, 130, "FULL SCREEN - 360x640 @1x")
    _framed(sheet, pygame.transform.grayscale(screen), 448, 130,
            "GREYSCALE - value / shape check")

    def crop2x(rect):
        sub = screen.subsurface(pygame.Rect(rect)).copy()
        return pygame.transform.scale(sub, (rect[2] * 2, rect[3] * 2))

    _framed(sheet, crop2x((180, 104, 180, 155)), 848, 130,
            "@2x - needle, pennant, callout")
    _framed(sheet, crop2x((100, 200, 180, 155)), 848, 460,
            "@2x - hub, event sub-tracks")

    y = 800
    f = _font(12, True)
    for line in NOTES:
        cur = ""
        for wd in line.split(" "):
            trial = (cur + " " + wd).strip()
            if f.size(trial)[0] > sw - 96:
                _sheet_txt(sheet, cur, 12, SHEET_LO, topleft=(48, y))
                y += 15
                cur = wd
            else:
                cur = trial
        _sheet_txt(sheet, cur, 12, SHEET_LO, topleft=(48, y))
        y += 19
    return sheet


def main():
    screen = build_screen()
    sheet = build_sheet(screen)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, str(OUT))
    print(f"wrote {OUT}  {sheet.get_size()}")
    print(f"thermal {THERMAL_SPAN}  rain {RAIN_SPAN}  snow {SNOW_SPAN}")
    print(f"clown {CLOWN_SPAN}  finale {FINALE_SPAN}  death {DEATH_PHASE:.4f}")


if __name__ == "__main__":
    main()
