"""MIXED stall-front dispatcher — each open stall carries its OWN concept.

Reads the mix from env SKYBIT_STALL_MIX (A|B|C). One hook pair is installed
that routes per ctx["group"] to the assigned concept module's own sign/item
hooks; every concept's hook pair is captured by letting the module install()
into the seam once and saving what it set.
"""
import os

import game.store_hub as sh

MIXES = {
    "A": {"parrot": "hook_shingle", "parcels": "showman_marquee",
          "costume": "hatch_board"},
    "B": {"parrot": "paper_lantern", "parcels": "sailcloth_pennant",
          "costume": "hook_shingle"},
    "C": {"parrot": "sailcloth_pennant", "parcels": "paper_lantern",
          "costume": "showman_marquee"},
}


def _capture(slug):
    import importlib
    mod = importlib.import_module(f"tools.stall_variant_{slug}")
    mod.install()
    pair = (sh.STALL_SIGN_HOOK, sh.STALL_ITEM_HOOK)
    sh.STALL_SIGN_HOOK = sh.STALL_ITEM_HOOK = None
    return pair


def install():
    mapping = MIXES[os.environ.get("SKYBIT_STALL_MIX", "A")]
    pairs = {g: _capture(slug) for g, slug in mapping.items()}
    default = next(iter(pairs.values()))

    def sign(surf, ctx):
        pairs.get(ctx["group"], default)[0](surf, ctx)

    def item(surf, ctx):
        pairs.get(ctx["group"], default)[1](surf, ctx)

    sh.STALL_SIGN_HOOK = sign
    sh.STALL_ITEM_HOOK = item
