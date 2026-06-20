# Skybit Store — all items

Every cosmetic in the coin Store, in one figure: **57 equippable skins** plus the
free **DEFAULT** macaw, grouped by the store's tabs (COSTUMES / PARROTS /
ANIMALS / SHOES / HATS) with each item's name and coin cost. All art is procedural
(drawn from code). Costume/parrot/animal skins animate over the bird's 4 wing
frames; the shoes and hats are shown by their product-shot icon (the item
itself), and Pip wears them — shoes on his feet, hats on his head — in-game.

![All Skybit Store items](all_items.png)

Regenerate after adding skins:

```sh
SDL_VIDEODRIVER=dummy python docs/store/render_gallery.py
```

The roster is data-driven: each item is a catalog entry in
[`game/store_catalog.py`](../../game/store_catalog.py) plus a procedural builder
in [`game/store_skins.py`](../../game/store_skins.py) (costumes + parrot species),
[`game/animal_skins.py`](../../game/animal_skins.py) (animals),
[`game/shoe_skins.py`](../../game/shoe_skins.py) (shoes), or
[`game/hat_skins.py`](../../game/hat_skins.py) (hats), dispatched by
`parrot.get_skin_frame` (and `parrot.get_skin_icon` for shoe/hat product shots).
Design-loop records live in [`docs/store_skins/`](../store_skins),
[`docs/creatures/`](../creatures), [`docs/shoes/`](../shoes), and
[`docs/hats/`](../hats).
