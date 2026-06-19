import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

TITLE = "P9 barbed-fang-harpoon"

# The ONLY pillar that POINTS. Every other skewered/totem column reads as a static
# stack; this one is a downward LUNGE into the gap. WHY sabertooth-maw is the focal
# (not just any skull): it is the single skull in the set whose own features plunge
# BELOW the jawline — its two sabre fangs hook down exactly where the engine's
# `barbed` long-harpoon tip juts into the gap. Fangs + harpoon point fuse into one
# recurved spear gesture at the gap edge, which no other pillar can claim.
#
# WHY this stays distinct from the horned-warband (P2): that pillar throws bone
# OUTWARD/UP (antlers up, ram curls wide) for a ragged horizontal silhouette. Here
# the read is VERTICAL and front-heavy — longjaw-relic's long muzzle wedge rhymes
# the maw's downward thrust, so the whole column drives the eye DOWN the spear.
# horned-ram is demoted to a SUPPORT tier: a single C-curl breath partway up that
# breaks the taper without ever owning the silhouette — horns as accent, not lead.
#
# Rhythm A-B-A-C-B: maw(A, the plunge) -> longjaw(B, down-rhyme) -> maw(A, the
# plunge recurs as the spit's repeating motif) -> horned-ram(C, lone wide breath)
# -> longjaw(B, far cap whose muzzle still points back down the column). The two
# down-plungers (A,B) dominate; the ram is the only sideways note.
#
# COLLAR=False: the barbed bone rod with its seam nubs is the sole joinery — bead
# collars would soften the brutal harpoon read and add horizontal pips that fight
# the vertical spear gesture. LEAN=0.0 keeps the shaft dead-straight so the point
# lunges true into the gap.
RECIPE = [
    "new:sabertooth-maw",   # focal at the gap — fangs + the barbed tip plunge as one spear
    "new:longjaw-relic",    # long muzzle wedge rhymes the downward thrust right above it
    "new:sabertooth-maw",   # the plunging maw recurs as the harpoon's repeating motif
    "new:horned-ram",       # lone support tier — one wide C-curl breath breaks the taper
    "new:longjaw-relic",    # far cap: muzzle points back down the column, sealing the lunge
]
WITH_SKEWER = True
SKEWER_STYLE = "barbed"
COLLAR = False
LEAN = 0.0


def _render():
    day = PE.render_pair(RECIPE, with_skewer=WITH_SKEWER, skewer_style=SKEWER_STYLE, collar=COLLAR, lean=LEAN, night=False)
    night = PE.render_pair(RECIPE, with_skewer=WITH_SKEWER, skewer_style=SKEWER_STYLE, collar=COLLAR, lean=LEAN, night=True)
    pad = 22
    W = day.get_width() + night.get_width() + pad*3; H = day.get_height() + 52
    sheet = pygame.Surface((W, H)); sheet.fill((26,24,30))
    sheet.blit(PE.sk.font(20).render(TITLE, True, PE.sk.LABEL), (pad, 12))
    sheet.blit(day, (pad, 44)); sheet.blit(night, (pad*2+day.get_width(), 44))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out); print("WROTE", out)


if __name__ == "__main__":
    _render()
