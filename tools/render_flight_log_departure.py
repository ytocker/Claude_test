"""
Round 1 render: departure_board concept.

Seven phase cards arranged as an airport FIDS (flight information display):
one card per biome phase. Status badges: PASSED / IN FLIGHT / AHEAD.
The death card (DAY) is highlighted amber; subsequent cards are greyed out.
A compact route strip at top anchors the spatial view.
"""
import os, sys, math
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from game.biome import palette_for_phase, PHASE_BOUNDARIES, CYCLE_SECONDS
from game.weather import (
    _phase_for_pillar,
    THERMAL_START_PHASE, THERMAL_PEAK_PHASE, THERMAL_END_PHASE,
    RAIN_DRIZZLE_START, RAIN_DRIZZLE_END,
    SNOW_STORM_CENTER, SNOW_STORM_WIDTH,
)
from game.config import (
    PLATEAU_PIPES, RAMP_PIPES, CLOWN_START_PILLAR, CLOWN_SLOT_PILLARS,
    COIN_RUSH_INTERVAL, CYCLE_FINALE_PHASE_HI,
)
from game.draw import lerp_color

pygame.init()

W, H = 360, 640
surf = pygame.Surface((W, H))
OUT  = "docs/flight_log/departure_board/round_1.png"

DEATH_PILLAR = 25
DEATH_PHASE  = _phase_for_pillar(DEATH_PILLAR)
DEATH_DAY    = 1
TIME_ALIVE   = 47.0

_ramp_end    = _phase_for_pillar(RAMP_PIPES)
_plateau_end = _phase_for_pillar(PLATEAU_PIPES)
_clown_s     = _phase_for_pillar(CLOWN_START_PILLAR)
_clown_e     = _phase_for_pillar(CLOWN_START_PILLAR + CLOWN_SLOT_PILLARS)
_snow_s      = SNOW_STORM_CENTER - SNOW_STORM_WIDTH / 2
_snow_e      = SNOW_STORM_CENTER + SNOW_STORM_WIDTH / 2
_day_end     = CYCLE_FINALE_PHASE_HI

def lc(a, b, t): return lerp_color(a, b, max(0.0, min(1.0, t)))

def desaturate(c, fac=0.25):
    r, g, b = c[0], c[1], c[2]
    grey = int(r*0.299 + g*0.587 + b*0.114)
    return (int(grey+(r-grey)*fac), int(grey+(g-grey)*fac), int(grey+(b-grey)*fac))

GOLD   = (240, 192, 64)
CREAM  = (245, 230, 200)
SCARLET= (220, 40, 40)
BOARD_BG = (14, 12, 28)

def fnt(size, bold=False):
    return pygame.font.SysFont("DejaVu Sans", size, bold=bold)

# Background — very dark, like a transit terminal at night
for y in range(H):
    t = y/H
    c = lc((10, 8, 24), (16, 14, 36), t)
    pygame.draw.line(surf, c, (0, y), (W, y))

# Subtle texture
import random
rng = random.Random(66)
for _ in range(50):
    sx = rng.randint(0, W-1); sy = rng.randint(0, H-1)
    br = rng.randint(30, 80)
    surf.set_at((sx, sy), (br, br, br))

# Header bar
pygame.draw.rect(surf, (22, 18, 44), (0, 0, W, 56))
pygame.draw.line(surf, GOLD, (0, 56), (W, 56), 1)
ttl = fnt(22, True).render("✈  FLIGHT LOG", True, CREAM)
surf.blit(ttl, (W//2-ttl.get_width()//2, 8))
sub = fnt(10).render(f"DEPARTURE BOARD  ·  DAY {DEATH_DAY}", True, (120, 110, 162))
surf.blit(sub, (W//2-sub.get_width()//2, 36))

# ── MINI ROUTE STRIP ──
MSTRIP_X = 12; MSTRIP_Y = 64; MSTRIP_W = W-24; MSTRIP_H = 32

def px(ph): return int(MSTRIP_X + ph * MSTRIP_W)

# Gradient
for xi in range(MSTRIP_W):
    phase = xi / MSTRIP_W
    pal = palette_for_phase(phase)
    for yi in range(MSTRIP_H):
        t = yi/MSTRIP_H
        c = lc(pal['sky_top'], pal['sky_bot'], t)
        if phase > DEATH_PHASE:
            c = desaturate(c)
        surf.set_at((MSTRIP_X+xi, MSTRIP_Y+yi), c)

# Phase ticks on mini strip
for frac, _ in PHASE_BOUNDARIES:
    x = px(frac)
    pygame.draw.line(surf, (200, 185, 235, 120), (x, MSTRIP_Y), (x, MSTRIP_Y+MSTRIP_H), 1)

# Death marker on mini strip
dx = px(DEATH_PHASE)
pygame.draw.line(surf, SCARLET, (dx, MSTRIP_Y-2), (dx, MSTRIP_Y+MSTRIP_H+2), 2)
pygame.draw.line(surf, (255, 200, 200), (dx, MSTRIP_Y-2), (dx, MSTRIP_Y+MSTRIP_H+2), 1)
xg = fnt(11, True).render('×', True, SCARLET)
surf.blit(xg, (dx-xg.get_width()//2, MSTRIP_Y-11))

# Day-end
x_de = px(_day_end)
pygame.draw.line(surf, (255, 215, 0), (x_de, MSTRIP_Y), (x_de, MSTRIP_Y+MSTRIP_H), 2)

# Mini strip border
pygame.draw.rect(surf, (60, 55, 100), (MSTRIP_X-1, MSTRIP_Y-1, MSTRIP_W+2, MSTRIP_H+2), 1)

# Mini strip biome labels
for i, (frac, name) in enumerate(PHASE_BOUNDARIES):
    x = px(frac)
    lt = fnt(7).render(name[:3], True, (160, 148, 200))
    lx = max(MSTRIP_X, min(x, MSTRIP_X+MSTRIP_W-lt.get_width()-1))
    surf.blit(lt, (lx, MSTRIP_Y + MSTRIP_H + 2))

# ── PHASE CARDS ──
# Determine which phase each biome phase occupies at death
# PHASE_BOUNDARIES = [(frac, name), ...]
phases = PHASE_BOUNDARIES  # 7 entries

death_phase_idx = len(phases) - 1  # default: last (shouldn't happen)
for i in range(len(phases)-1):
    if phases[i][0] <= DEATH_PHASE < phases[i+1][0]:
        death_phase_idx = i
        break
if DEATH_PHASE >= phases[-1][0]:
    death_phase_idx = len(phases) - 1

CARD_Y0 = MSTRIP_Y + MSTRIP_H + 20
CARD_X = 12; CARD_W = W - 24; CARD_H = 54; CARD_GAP = 5

# Event tags per phase
phase_events = {
    'DAY':        ['⚡ Geysers', 'Ramp'],
    'GOLDEN HOUR':['⚡ Geysers pk'],
    'SUNSET':     ['\U0001f0cf Clown'],
    'DUSK':       ['\U0001f327 Rain', '\U0001f0cf Clown'],
    'NIGHT':      ['\U0001f327 Storm'],
    'PREDAWN':    ['❄ Snow'],
    'SUNRISE':    ['❄ Snow', '★ Finale'],
}

for i, (frac, name) in enumerate(phases):
    cy = CARD_Y0 + i*(CARD_H + CARD_GAP)
    is_death = (i == death_phase_idx)
    is_passed = (i < death_phase_idx)
    is_ahead  = (i > death_phase_idx)

    # Next phase boundary
    next_frac = phases[i+1][0] if i < len(phases)-1 else 1.0

    # Card background
    if is_death:
        bg = (28, 22, 10)
        border = GOLD
    elif is_passed:
        bg = (18, 18, 32)
        border = (50, 45, 80)
    else:
        bg = (14, 14, 26)
        border = (35, 32, 58)
    pygame.draw.rect(surf, bg, (CARD_X, cy, CARD_W, CARD_H), border_radius=6)
    pygame.draw.rect(surf, border, (CARD_X, cy, CARD_W, CARD_H), 1, border_radius=6)

    # Left colour band: sky colour for this phase
    band_pal = palette_for_phase(frac + 0.01)
    band_col = band_pal['sky_mid'] if not is_ahead else desaturate(band_pal['sky_mid'])
    pygame.draw.rect(surf, band_col, (CARD_X, cy, 8, CARD_H), border_radius=6)
    # Thin separator
    pygame.draw.line(surf, (0, 0, 0), (CARD_X+8, cy), (CARD_X+8, cy+CARD_H), 1)

    # Phase name
    name_col = GOLD if is_death else ((180, 165, 215) if is_passed else (90, 82, 125))
    name_f = fnt(14, True) if is_death else fnt(13, True if is_passed else False)
    nm = name_f.render(name, True, name_col)
    surf.blit(nm, (CARD_X+14, cy+7))

    # Phase fraction
    frac_f = fnt(9)
    fr_col = (140, 128, 175) if not is_ahead else (70, 65, 105)
    fr = frac_f.render(f'{frac:.0%}→{next_frac:.0%}', True, fr_col)
    surf.blit(fr, (CARD_X+14, cy+CARD_H-fr.get_height()-5))

    # Status badge
    if is_death:
        status = 'IN FLIGHT'
        sc = (240, 192, 64); sbg = (60, 46, 10)
    elif is_passed:
        status = 'PASSED'
        sc = (60, 220, 100); sbg = (10, 45, 20)
    else:
        status = 'AHEAD'
        sc = (80, 75, 120); sbg = (18, 16, 32)

    sf = fnt(9, True)
    st = sf.render(status, True, sc)
    sbx = CARD_X + CARD_W - st.get_width() - 16; sby = cy + 8
    pygame.draw.rect(surf, sbg, (sbx-4, sby-2, st.get_width()+8, st.get_height()+4), border_radius=3)
    surf.blit(st, (sbx, sby))

    # Event tags
    evs = phase_events.get(name, [])
    ef = fnt(9)
    ex = CARD_X + nm.get_width() + 20
    for ev in evs[:2]:  # max 2 events per card
        ecol = (160, 150, 200) if not is_death else (200, 188, 140)
        if is_ahead: ecol = (70, 65, 100)
        et = ef.render(ev, True, ecol)
        if ex + et.get_width() < CARD_X + CARD_W - 60:
            surf.blit(et, (ex, cy+8))
            ex += et.get_width() + 8

    # Death card extra: death line indicator
    if is_death:
        local_t = (DEATH_PHASE - frac) / max(0.001, next_frac - frac)
        bar_x = CARD_X + 8; bar_w = CARD_W - 12; bar_h = 4
        bar_y = cy + CARD_H - 11
        pygame.draw.rect(surf, (40, 35, 65), (bar_x, bar_y, bar_w, bar_h), border_radius=2)
        fw = int(bar_w * local_t)
        pygame.draw.rect(surf, GOLD, (bar_x, bar_y, fw, bar_h), border_radius=2)
        # × marker
        mx = bar_x + fw
        pygame.draw.line(surf, SCARLET, (mx, bar_y-2), (mx, bar_y+bar_h+2), 2)
        xm = fnt(10, True).render('×', True, SCARLET)
        surf.blit(xm, (mx - xm.get_width()//2, bar_y - 8))
        # Progress text
        pt = fnt(8).render(f'p{DEATH_PILLAR}  {DEATH_PHASE*100:.0f}%  {local_t*100:.0f}% of phase', True, (160, 148, 110))
        surf.blit(pt, (bar_x, bar_y + 6))

# ── STATS ──
sy = CARD_Y0 + len(phases)*(CARD_H+CARD_GAP) + 8
pl = fnt(15, True).render(f'PILLAR {DEATH_PILLAR}  ·  DAY {DEATH_DAY}', True, GOLD)
surf.blit(pl, (W//2-pl.get_width()//2, sy))
mins = int(TIME_ALIVE//60); secs = int(TIME_ALIVE%60)
ts = fnt(11).render(f'{mins}m {secs:02d}s elapsed', True, (155, 145, 200))
surf.blit(ts, (W//2-ts.get_width()//2, sy+20))

# BACK button
bty = H - 46; btw = 240; bth = 38; btx = W//2-btw//2
pygame.draw.rect(surf, (20, 17, 40), (btx, bty, btw, bth), border_radius=19)
pygame.draw.rect(surf, GOLD, (btx, bty, btw, bth), 2, border_radius=19)
bt = fnt(15, True).render('BACK', True, CREAM)
surf.blit(bt, (W//2-bt.get_width()//2, bty+bth//2-bt.get_height()//2))

pygame.image.save(surf, OUT)
print(f'saved → {OUT}')
