"""Look-dev mockup: the EVOLVED "Demon Jester" boss pushed into FIVE distinct
DEMON variations — all MORE REDDISH, MORE MASSIVE and MEANER (round 1).

The user loved boss #3 of `render_jester_boss.py` ("The Demon Jester": horns via
`cap_demon`, plum/lime pulled back under a fiery-corrupted palette, glowing
YELLOW eyes, long fangs, the round-4 amorphous dark fiery shadow-pool aura, scale
1.40). This sheet keeps that DNA and explores five climactic demons, each clearly
heavier than the original Demon and clearly different from each other:

  1. INFERNO DEMON   — bright fiery orange-red, the biggest flaming aura + most
                       embers; the classic fire-demon.
  2. CRIMSON BRUTE   — hulking oxblood MASS (broadest shoulders, biggest scale),
                       huge blunt horns; the heaviest of the set.
  3. ARCHFIEND       — dark blood-red + black, big curved crown-horns, regal
                       boss-of-bosses; the climactic one.
  4. MOLTEN / MAGMA  — body cracked with glowing red-orange MAGMA seams, a
                       smouldering volcanic read.
  5. SHADOWFLAME     — dark red-black, sleeker but sinister, cold-edged smoke +
                       hot red glowing eyes/fangs; "quiet but deadly".

Panel 0 is the UNCHANGED original Demon Jester (boss #3 verbatim) for the side-
by-side comparison.

Three DIE ("cube") fixes the user asked for, applied to EVERY panel:
  1. The die is REPOSITIONED UP + LEFT to meet the ENLARGED raised arm. The
     figure is scaled ABOUT THE FEET, so the raised LEFT mitt lands at
     ~`jester_cx - 60*scale` in x (further left + higher) as the boss grows — the
     die now tracks there instead of staying at its base seat, so the big arm
     CRADLES the die rather than reaching past it. Bigger scale ⇒ die further
     up-left.
  2. The die is BIGGER — `size≈54` (the friendly die hardcodes 40), keeping the
     3D isometric cube + foreshortened pips.
  3. The die aura is MEANER — re-tinted from the friendly YELLOW toward a CRIMSON
     → ember-orange falloff and widened so it reads as a DANGEROUS reward, not a
     friendly power-up.

All of that lives in a LOCAL `draw_boss_die` here — the friendly #13 die in
`render_jester_variants.py` is left untouched.

Nothing under `game/` is touched; we import the real kit and the boss kit and
mutate no state. Headless + deterministic. Output: docs/jester/demon_round_1.png.

    PYTHONPATH=. python tools/render_demon_variants.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H
from game.draw import lerp_color, blit_glow
from game.parrot import get_parrot
from tools.render_warren_mockup import shaped_palette

from tools.render_clown_dice import (
    _shade, DAY_PHASE, SS, VIEW_W, VIEW_H, HERO_PIPS,
)

# Reuse the approved jester body kit + the friendly die machinery so the demons
# stay in the SAME family and the boss die is pixel-derived from the real prop.
from tools.render_jester_variants import (
    build_jester, cap_four_point, _bell, _cap_point,
    _draw_die_face_noshadow,
)

# Reuse the whole boss kit verbatim: the round-4 amorphous shadow-pool aura, the
# palette-corruption helpers, the menace face/eyes/fangs, the demon cap, the
# brawler-mass shoulders, the corruption seams and the boss build path. We only
# ADD reddish/massive demon flavour on top — we don't fork the boss code.
from tools.render_jester_boss import (
    BASE, corrupt,
    silhouette_aura, build_boss, _add_seams,
    _horn,
    PANEL_W, PANEL_H, FEET_Y, _scene_bg, _blit_parrot,
    BOSSES,
)


# ── reddish-massive demon cap variants ───────────────────────────────────────
# Each demon owns a distinct HORN silhouette so the five read apart at a glance,
# all rooted on the approved four-point fool's cap so they stay demon-JESTERS.

def cap_demon_blunt(surf, cx, base_y, hr, cols):
    """The Brute's cap: two THICK BLUNT horns — short, heavy, brawler-cattle
    horns sweeping low and out, far chunkier than the slim `cap_demon` spikes."""
    cap_four_point(surf, cx, base_y, hr, cols)
    horn = (34, 16, 18)
    for s in (-1, 1):
        bx, by = cx + s * 13, base_y - 2
        tx, ty = cx + s * 30, base_y - 16
        midx, midy = cx + s * 26, base_y - 4
        pts = [(bx - 6, by + 3), (bx + 6, by - 3), (midx, midy),
               (tx, ty), (tx - s * 5, ty + 7)]
        pygame.draw.polygon(surf, horn, pts)
        pygame.draw.polygon(surf, _shade(horn, 40),
                            [(bx - 6, by + 3), (bx + 4, by - 2),
                             (midx, midy)])
        pygame.draw.polygon(surf, _shade(horn, -70), pts, 2)
        # A bone-pale tip so the blunt horn reads heavy + solid, not a dark blob.
        pygame.draw.circle(surf, (196, 150, 120), (tx, ty), 3)


def cap_crown_horns(surf, cx, base_y, hr, cols):
    """The Archfiend's CROWN of horns: a big pair of curved horns arcing UP and
    OUT like a hell-king's crown, plus two short inner prongs — regal menace."""
    cap_four_point(surf, cx, base_y, hr, cols)
    horn = (30, 10, 12)
    # Big outer crown-horns sweeping up + out then curling back inward.
    for s in (-1, 1):
        bx, by = cx + s * 14, base_y - 3
        tip = (cx + s * 22, base_y - 40)
        mid = (cx + s * 30, base_y - 18)
        pts = [(bx - 5, by + 2), (bx + 5, by - 2), mid, tip,
               (tip[0] - s * 6, tip[1] + 8)]
        pygame.draw.polygon(surf, horn, pts)
        pygame.draw.polygon(surf, _shade(horn, 45),
                            [(bx - 5, by + 2), (bx + 3, by - 1), mid])
        pygame.draw.polygon(surf, _shade(horn, -75), pts, 2)
        pygame.draw.circle(surf, (170, 60, 48), tip, 3)
    # Short inner prongs flanking the centre for the crowned, three-tier read.
    for s in (-1, 1):
        _horn(surf, (cx + s * 5, base_y - 4), (cx + s * 9, base_y - 22), horn)


def cap_demon_tall(surf, cx, base_y, hr, cols):
    """The Inferno/Shadowflame slim-but-TALLER horns: the demon spikes of
    `cap_demon` lengthened + raked back so they read sharper and meaner."""
    cap_four_point(surf, cx, base_y, hr, cols)
    horn = (32, 12, 16)
    _horn(surf, (cx - 13, base_y - 4), (cx - 26, base_y - 34), horn)
    _horn(surf, (cx + 13, base_y - 4), (cx + 26, base_y - 34), horn)


# ── the reddish, MASSIVE, mean BOSS die ──────────────────────────────────────
# The friendly #13 die (and the boss sheet's reused die) wear a YELLOW power-up
# aura at `size=40`. The demon boss presents a DANGEROUS reward: a BIGGER cube in
# a CRIMSON → ember-orange aura that is also WIDER/more massive. This is a local
# routine so the friendly die in render_jester_variants stays untouched.

def _boss_aura_surface(radius, breathe, *, core, mid, edge):
    """A crimson→ember power-up halo, same alpha-stop construction as the friendly
    `_aura_surface` but re-tinted toward danger: a hot ember core → crimson body →
    deep-red edge. Reads on VALUE (bright core) so it survives the day sky, but
    the HUE now says 'dangerous reward', not 'friendly pickup'. Bigger radius is
    passed in by the caller so the whole aura reads more massive."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    stops = [
        (1.00, edge, 0),                  # deep-red edge fades to nothing
        (0.86, edge, 140),                # deep crimson body
        (0.60, mid, 220),                 # SATURATED ember-red (dominant)
        (0.34, mid, 248),                 # bright ember-orange
        (0.16, core, 255),               # hot ember-yellow core (the heat)
    ]
    for t_out, col, a_in in stops:
        r = max(1, int(radius * t_out))
        steps = max(3, r // 4)
        for k in range(steps):
            rr = int(r * (1 - k / steps))
            if rr < 1:
                break
            a = int(a_in * (k / steps) ** 0.4)
            a = min(255, int(a * (0.78 + 0.22 * breathe)))
            pygame.draw.circle(s, (*col, a), (c, c), rr)
    return s


def draw_boss_die(surf, cx, base_y, pulse, *, size=54,
                  core=(255, 226, 120), mid=(255, 120, 36),
                  edge=(150, 16, 16), spark=(255, 196, 120)):
    """The demon's presented die: a BIGGER 3D isometric cube (`size≈54` vs the
    friendly 40) inside a MASSIVE crimson→ember aura, with red-hot orbiting
    sparkles. Per-demon `core`/`mid`/`edge` let each version's die echo its own
    fire (oxblood Brute, blood-red Archfiend, magma, cold-shadow red…)."""
    cy = int(base_y + math.sin(pulse * 1.1) * 3)
    breathe = 0.5 + 0.5 * math.sin(pulse * 1.3)
    pr = 1.0 + 0.10 * breathe
    # MORE MASSIVE than the friendly die's ~50px: ~1.5x the bigger cube footprint
    # so the reddish aura looms as a dangerous heat-bloom around the reward.
    aura_r = int(size * 1.55 * pr)
    aura = _boss_aura_surface(aura_r, breathe, core=core, mid=mid, edge=edge)
    surf.blit(aura, (cx - aura_r - 1, cy - aura_r - 1))
    # A tight additive ember core bloom so the centre reads as EMITTING heat
    # without washing the broad crimson halo to flat white on the day sky.
    blit_glow(surf, cx, cy, int(16 * pr), core,
              alpha=60 + int(34 * breathe))

    # The 3D isometric cube prop — same form as the friendly die, just bigger.
    _draw_die_face_noshadow(surf, cx, cy, size, pips=HERO_PIPS)

    # Red-hot orbiting embers replace the friendly cream sparkles.
    for i in range(5):
        a = i * math.tau / 5 + pulse * 0.4
        rr = (size * 0.78) + 5 * math.sin(pulse * 0.9 + i)
        sx = int(cx + math.cos(a) * rr)
        sy = int(cy + math.sin(a) * rr * 0.85)
        tw = 0.5 + 0.5 * math.sin(pulse * 2.0 + i * 1.7)
        al = int(120 + 120 * tw)
        sz = 3 + int(2 * tw)
        s = pygame.Surface((sz * 4, sz * 4), pygame.SRCALPHA)
        col = (*spark, al)
        pygame.draw.line(s, col, (sz * 2, 0), (sz * 2, sz * 4), 1)
        pygame.draw.line(s, col, (0, sz * 2), (sz * 4, sz * 2), 1)
        pygame.draw.circle(s, (255, 230, 180, al), (sz * 2, sz * 2), sz)
        surf.blit(s, (sx - sz * 2, sy - sz * 2),
                  special_flags=pygame.BLEND_ADD)


# ── magma seams (fiery re-tint of the Corrupted's glitch cracks) ─────────────

def _add_magma_seams(surf, cx, feet_y):
    """Glowing red-orange MAGMA cracks across the Molten boss's torso — the
    Corrupted `_add_seams` idea re-tinted fiery: a deep-red fissure with a hot
    orange-yellow molten core glowing along it, so the body reads as cracked
    cooling lava rather than glitched corruption."""
    hip_y = feet_y - 84
    top = hip_y - 50
    rng = __import__('random').Random(909)
    for _ in range(5):
        x0 = cx + rng.randint(-24, 24)
        y0 = top + rng.randint(2, 10)
        pts = [(x0, y0)]
        for _ in range(3):
            x0 += rng.randint(-7, 7)
            y0 += rng.randint(8, 16)
            pts.append((x0, y0))
        # Dark fissure walls, then a hot molten core line glowing inside them.
        pygame.draw.lines(surf, (60, 8, 4), False, pts, 4)
        pygame.draw.lines(surf, (236, 92, 20), False, pts, 2)
        pygame.draw.lines(surf, (255, 220, 120), False, pts, 1)


# ── the demon palette helper ─────────────────────────────────────────────────
# All five share the Demon DNA — plum/lime pulled back, RED-shifted — but each
# is anchored to its own red so the costumes read apart. Built like boss #3's
# palette (a fire/red corruption, then a light plum/lime re-tint so it never
# drifts olive/khaki), parameterised per demon by its `red` anchor + amounts.

def demon_palette(red, *, deep, desat, tint, plum_back=0.26, lime_back=0.30,
                  gold_lift=0.0):
    """A RED-shifted demon costume: corrupt #13's plum/lime/gold toward `red`,
    then pull the dark back toward plum and the light back toward lime a touch so
    the harlequin DNA still reads under the red wash."""
    dark = lerp_color(corrupt(BASE["dark"], red, deep=deep, desat=desat,
                              tint=tint), (96, 44, 150), plum_back)
    light = lerp_color(corrupt(BASE["light"], red, deep=deep * 0.7,
                               desat=desat * 0.8, tint=tint * 0.9),
                       (132, 218, 116), lime_back)
    gold = corrupt(BASE["gold"], red, deep=deep * 0.6, desat=desat * 0.5,
                   tint=tint * 0.7)
    if gold_lift:
        gold = lerp_color(gold, (236, 184, 56), gold_lift)
    return {"dark": dark, "light": light, "gold": gold}


# ── the five reddish/massive demons ──────────────────────────────────────────
# Every entry keeps the Demon DNA (horns, RED-shifted plum/lime, fangs, glowing
# eyes, the amorphous reddish shadow-pool aura) and is CLEARLY more massive than
# the original Demon (scale 1.40) and distinct from the others. `die` carries the
# per-demon crimson→ember die tint so the dangerous reward echoes each fire.

INFERNO = (236, 84, 18)
OXBLOOD = (138, 22, 22)
BLOOD = (120, 12, 16)
MAGMA = (210, 64, 14)
SHADOWRED = (96, 18, 24)

DEMONS = [
    # 1 — INFERNO DEMON: bright fiery orange-red, the BIGGEST flaming aura + most
    # embers. The classic fire-demon — hot, loud, all flame.
    dict(name="Inferno Demon",
         vibe="bright fire orange-red · biggest flame aura · most embers",
         pal=demon_palette(INFERNO, deep=0.20, desat=0.16, tint=0.34),
         aura_hue=(248, 120, 24), aura_dark=(40, 10, 4), rim=(255, 150, 40),
         glow=(255, 196, 40), cap=cap_demon_tall, scale=1.50, fang_xtra=5,
         mass=1.08, aura_bulk=1.35, ember_boost=True,
         die=dict(core=(255, 236, 150), mid=(255, 138, 30),
                  edge=(190, 40, 8), spark=(255, 206, 120))),
    # 2 — CRIMSON BRUTE: hulking oxblood MASS — the broadest shoulders + biggest
    # scale of the set, huge blunt horns, the heaviest. A wall of red muscle.
    dict(name="Crimson Brute",
         vibe="hulking oxblood MASS · broadest · biggest · blunt horns",
         pal=demon_palette(OXBLOOD, deep=0.42, desat=0.30, tint=0.40),
         aura_hue=(196, 26, 30), aura_dark=(28, 4, 6), rim=(200, 30, 40),
         glow=(255, 84, 56), cap=cap_demon_blunt, scale=1.60, fang_xtra=4,
         mass=1.30, head_tilt=-3, aura_bulk=1.15,
         die=dict(core=(255, 206, 120), mid=(230, 70, 30),
                  edge=(120, 12, 12), spark=(255, 150, 90))),
    # 3 — ARCHFIEND (HELL-KING): dark blood-red + black, big curved CROWN-horns,
    # regal boss-of-bosses. Upright, commanding, the climactic demon.
    dict(name="Archfiend",
         vibe="blood-red + black · CROWN-horns · regal boss-of-bosses",
         pal=demon_palette(BLOOD, deep=0.50, desat=0.34, tint=0.46,
                           gold_lift=0.30),
         aura_hue=(168, 16, 22), aura_dark=(20, 2, 4), rim=(180, 24, 32),
         glow=(255, 64, 48), cap=cap_crown_horns, scale=1.52, fang_xtra=3,
         mass=1.14, head_tilt=-2, aura_bulk=1.2,
         die=dict(core=(255, 196, 110), mid=(220, 48, 24),
                  edge=(108, 6, 10), spark=(255, 130, 80))),
    # 4 — MOLTEN / MAGMA: body cracked with glowing red-orange MAGMA seams,
    # smouldering volcanic. The cracked-lava demon.
    dict(name="Molten Magma",
         vibe="cracked MAGMA seams · smouldering volcanic · glowing core",
         pal=demon_palette(MAGMA, deep=0.46, desat=0.40, tint=0.42),
         aura_hue=(228, 78, 16), aura_dark=(34, 8, 4), rim=(244, 110, 26),
         glow=(255, 170, 36), cap=cap_demon_tall, scale=1.46, fang_xtra=4,
         mass=1.10, magma=True, aura_bulk=1.25, ember_boost=True,
         die=dict(core=(255, 230, 140), mid=(244, 110, 24),
                  edge=(150, 28, 6), spark=(255, 184, 100))),
    # 5 — SHADOWFLAME DEMON: dark red-black, sleeker but sinister, cold-edged
    # smoke + HOT red glowing eyes/fangs. The quiet-but-deadly one.
    dict(name="Shadowflame Demon",
         vibe="dark red-black · sleek + sinister · cold smoke · hot red eyes",
         pal=demon_palette(SHADOWRED, deep=0.60, desat=0.50, tint=0.48),
         aura_hue=(150, 20, 28), aura_dark=(10, 2, 6), rim=(150, 24, 34),
         glow=(255, 60, 70), cap=cap_demon_tall, scale=1.44, fang_xtra=5,
         narrow_eyes=True, skin=(150, 110, 110), head_tilt=2, aura_bulk=1.1,
         die=dict(core=(255, 170, 120), mid=(206, 40, 32),
                  edge=(86, 6, 14), spark=(255, 110, 90))),
]


# ── per-cell scene (mirrors render_jester_boss.render_boss, demon die + dies) ─
# Same taller day-clearing panel + un-scaled parrot ruler as the boss sheet, but
# the die is repositioned UP-LEFT to track the ENLARGED raised arm and drawn with
# the bigger reddish boss die.

def _die_seat(scale):
    """Where the BIGGER die should sit so the SCALED raised LEFT mitt cradles it.
    The figure is scaled about the feet, so the raised hand (built at base
    `jester_cx + (hand_up_x - jester_cx)`) lands at `jester_cx - ~60*scale` in x
    and proportionally HIGHER in y. We seat the die there: bigger scale ⇒ die
    further UP + LEFT to meet the reaching mitt."""
    jester_cx = PANEL_W // 2 + 12
    die_x = int(jester_cx - 60 * scale)            # tracks the scaled mitt x
    # Base die_base_y was 36 with the hand at y≈76+(PANEL_H-VIEW_H). As the figure
    # grows about the feet the hand rises; raise the die proportionally so it stays
    # in the cup of the mitt rather than below the enlarged reach.
    die_base_y = int(36 - 30 * (scale - 1.0))
    return jester_cx, die_x, die_base_y


def render_original(idx):
    """Panel 0: the UNCHANGED original Demon Jester (boss #3 verbatim), drawn so
    its FEET land on FEET_Y, with its ORIGINAL die placement + yellow-ish boss
    die — the comparison baseline."""
    spec = next(b for b in BOSSES if b["name"] == "The Demon Jester")
    return _render_demon(spec, idx, original=True)


def render_demon(spec, idx):
    return _render_demon(spec, idx, original=False)


def _render_demon(spec, idx, *, original):
    bw, bh = PANEL_W * SS, PANEL_H * SS
    big = pygame.Surface((bw, bh))
    _scene_bg(big, bw, bh, idx)

    breathe = 0.5 + 0.5 * math.sin((idx * 1.7 + 2.0) * 1.3)
    scale = spec["scale"]
    jester_cx, die_x, die_base_y = _die_seat(scale)
    base_feet = FEET_Y

    # The raised LEFT arm reaches to the (now repositioned) die. Built at base,
    # the hand seat must point at the die's pre-scale position so that AFTER the
    # about-the-feet scale it lands on the die. Solve the inverse: a point P on the
    # figure maps to jester_cx + (P - jester_cx)*scale; we want that to equal the
    # die, so P = jester_cx + (die - jester_cx)/scale.
    hand_x = int(jester_cx + (die_x + 6 - jester_cx) / scale)
    hand_y = int(base_feet + (die_base_y + 34 - base_feet) / scale)
    hand_up = (hand_x, hand_y)

    fig = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pal = spec["pal"]
    build_boss(fig, jester_cx, base_feet, hand_up,
               dark=pal["dark"], light=pal["light"], gold=pal["gold"],
               cap_fn=spec["cap"], glow_col=spec["glow"],
               fang_xtra=spec.get("fang_xtra", 0),
               narrow_eyes=spec.get("narrow_eyes", False),
               skin=spec.get("skin", (200, 150, 140)),
               shadow_face=spec.get("shadow_face", False),
               mass=spec.get("mass", 1.0), lean=spec.get("lean", 0.0),
               head_extra_tilt=spec.get("head_tilt", 0))
    if spec.get("magma"):
        _add_magma_seams(fig, jester_cx, base_feet)
    if spec.get("seams"):
        _add_seams(fig, jester_cx, base_feet, spec["glow"])

    # Scale the figure UP about the FEET so it looms taller/broader yet stays
    # planted, then grow the amorphous reddish shadow-pool aura from its own
    # silhouette (the round-4 approved look, just reddish hues).
    sw, sh = int(PANEL_W * scale), int(PANEL_H * scale)
    fig_big = pygame.transform.smoothscale(fig, (sw, sh))
    off_x = int(jester_cx - jester_cx * scale)
    off_y = int(base_feet - base_feet * scale)
    boss_layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    boss_layer.blit(fig_big, (off_x, off_y))

    boss_ss = pygame.transform.smoothscale(boss_layer, (bw, bh))
    torso_x = int(jester_cx * SS)
    torso_y = int((FEET_Y - 70) * SS)
    # `aura_bulk` widens the dark pool per demon — Inferno/Brute/Archfiend read
    # MORE MASSIVE than the original Demon's pool.
    silhouette_aura(big, boss_ss, torso_x, torso_y, spec["aura_hue"], breathe,
                    dark=spec["aura_dark"], rim=spec.get("rim"),
                    embers=True, smoke=True, seed=idx, scl=SS,
                    bulk=spec.get("aura_bulk", 1.0))
    if spec.get("ember_boost"):
        # Inferno/Molten smoulder hardest — a second ember pass for the most
        # flame, seeded apart so the two passes don't overlap.
        silhouette_aura(big, boss_ss, torso_x, torso_y, spec["aura_hue"],
                        breathe, dark=spec["aura_dark"], rim=spec.get("rim"),
                        embers=True, smoke=False, seed=idx + 97, scl=SS,
                        bulk=spec.get("aura_bulk", 1.0))

    big.blit(boss_ss, (0, 0))

    # The reddish, MASSIVE, mean BOSS die — repositioned UP-LEFT into the cup of
    # the enlarged mitt. The original-Demon panel keeps the SMALLER die at the
    # base seat (its yellow-leaning tint) so the comparison is fair; the five new
    # demons get the bigger reddish die.
    overlay = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    if original:
        # Original Demon: baseline die placement + the original yellow-warm aura
        # at the smaller base size, so panel 0 shows the BEFORE die.
        draw_boss_die(overlay, die_x, die_base_y, idx * 1.7 + 2.0, size=40,
                      core=(255, 240, 150), mid=(255, 196, 60),
                      edge=(232, 150, 30), spark=(255, 236, 140))
    else:
        dk = spec["die"]
        draw_boss_die(overlay, die_x, die_base_y, idx * 1.7 + 2.0, size=54,
                      core=dk["core"], mid=dk["mid"], edge=dk["edge"],
                      spark=dk["spark"])
    _blit_parrot(overlay)
    big.blit(pygame.transform.smoothscale(overlay, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (PANEL_W, PANEL_H))


# ── sheet layout ──────────────────────────────────────────────────────────────

def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((W, H))

    cells = []
    captions = []
    cells.append(render_original(0))
    captions.append(("ORIGINAL Demon Jester",
                     "boss #3 verbatim · scale 1.40 · base die placement "
                     "(the BEFORE)"))
    for i, spec in enumerate(DEMONS, start=1):
        cells.append(render_demon(spec, i))
        captions.append((spec["name"], spec["vibe"]))

    cols, rows = 3, 2
    sw, sh = int(PANEL_W * 3.1), int(PANEL_H * 3.1)

    PAD = 48
    GAP = 26
    TITLE_H = 100
    CAP_H = 70
    FOOT_H = PANEL_H + 40

    canvas_w = PAD * 2 + cols * sw + (cols - 1) * GAP
    canvas_h = (PAD * 2 + TITLE_H + rows * (sh + CAP_H) + (rows - 1) * GAP
                + FOOT_H)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((16, 10, 12))

    f_title = pygame.font.SysFont(None, 74, bold=True)
    f_sub = pygame.font.SysFont(None, 32, bold=True)
    f_cap = pygame.font.SysFont(None, 40, bold=True)
    f_caps = pygame.font.SysFont(None, 28, bold=True)

    title = f_title.render(
        "DEMON JESTER — 5 reddish · massive · meaner variations (round 1)",
        True, (255, 214, 200))
    canvas.blit(title, (PAD, PAD - 2))
    sub = f_sub.render(
        "Panel 0 = the ORIGINAL Demon Jester (the BEFORE). Panels 1-5 push it "
        "MORE REDDISH + MORE MASSIVE + MEANER: Inferno (fire) · Brute (oxblood "
        "MASS) · Archfiend (blood-red crown-horns) · Molten (magma seams) · "
        "Shadowflame (red-black, hot eyes). Each keeps the Demon DNA — horns, "
        "RED-shifted plum/lime, fangs, glowing eyes, the amorphous reddish "
        "shadow-pool aura. DIE FIXES: repositioned UP-LEFT into the enlarged "
        "mitt · bigger cube (54 vs 40) · MASSIVE crimson->ember aura.",
        True, (210, 184, 184))
    canvas.blit(sub, (PAD, PAD + 54))

    y0 = PAD + TITLE_H
    STRONG = {1, 2, 3}            # the loudest fire/mass demons get a red border
    strong_cell = None
    for i, cell in enumerate(cells):
        r, c = divmod(i, cols)
        cx = PAD + c * (sw + GAP)
        cy = y0 + r * (sh + CAP_H + GAP)
        scaled = pygame.transform.smoothscale(cell, (sw, sh))
        border = (220, 60, 40) if i in STRONG else (80, 50, 50)
        pygame.draw.rect(canvas, border,
                         pygame.Rect(cx - 2, cy - 2, sw + 4, sh + 4), 2)
        canvas.blit(scaled, (cx, cy))
        name, vibe = captions[i]
        tag = "0. " + name if i == 0 else f"{i}. {name}"
        cap = f_cap.render(tag, True, (252, 220, 200))
        canvas.blit(cap, (cx + (sw - cap.get_width()) // 2, cy + sh + 8))
        sub2 = f_caps.render(vibe, True, (206, 178, 178))
        canvas.blit(sub2, (cx + (sw - sub2.get_width()) // 2, cy + sh + 42))
        if i == 2:                # Crimson Brute — the strongest demon for 1x
            strong_cell = cell

    # ONE 1x inset of the strongest demon — the alignment + reddish-die GATE. At
    # in-game scale the enlarged mitt must CRADLE the bigger die and the die aura
    # must read CRIMSON/ember (dangerous), not friendly yellow.
    foot_y = y0 + rows * (sh + CAP_H) + (rows - 1) * GAP + 16
    cap_intro = f_cap.render(
        "1x in-game scale — does the enlarged mitt CRADLE the bigger die, and "
        "does the die aura read CRIMSON/ember (dangerous)?",
        True, (252, 200, 190))
    canvas.blit(cap_intro, (PAD, foot_y - 4))
    iy = foot_y + 40
    if strong_cell is not None:
        ix = PAD
        pygame.draw.rect(canvas, (220, 60, 40),
                         pygame.Rect(ix - 2, iy - 2, PANEL_W + 4,
                                     PANEL_H + 4), 2)
        canvas.blit(strong_cell, (ix, iy))
        lab = f_caps.render(
            "Crimson Brute — the heaviest · die up-left in the mitt",
            True, (216, 188, 188))
        canvas.blit(lab, (ix + PANEL_W + 16, iy + PANEL_H // 2 - 30))
        lab2 = f_caps.render(
            "reddish shadow-pool aura · crimson->ember die aura · long fangs",
            True, (186, 162, 162))
        canvas.blit(lab2, (ix + PANEL_W + 16, iy + PANEL_H // 2 + 2))

    out_dir = os.path.join("docs", "jester")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "demon_round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
