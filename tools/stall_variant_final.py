"""FINAL chosen combination for the lagoon-hub stalls.

Item presentation: mix C — each open stall keeps its own item treatment
(PARROTS = sailcloth-pennant sling, PARCELS = paper-lantern, COSTUMES =
showman-marquee pedestal), per tools/stall_variant_mixed.py.

Sign: the SAME sign on every stall — the showman-marquee cartouche, chosen
awning-matched palette C (lacquer red field, cream piping, gold bulbs) and
text option T4 (pt 11.5), both now the module's own defaults in
tools/stall_variant_showman_marquee.py. The sign choice is independent of
which item concept a given stall carries.
"""
import os

import game.store_hub as sh
import tools.stall_variant_mixed as mixed
import tools.stall_variant_showman_marquee as mar


def install():
    os.environ.setdefault("SKYBIT_STALL_MIX", "C")
    mixed.install()
    item_hook = sh.STALL_ITEM_HOOK
    sh.STALL_SIGN_HOOK = mar._sign
    sh.STALL_ITEM_HOOK = item_hook
