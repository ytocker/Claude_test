# Skybit Store — all items

Every cosmetic in the coin Store, in one figure: **40 equippable skins** plus the
free **DEFAULT** macaw, grouped by the store's tabs (COSTUMES / PARROTS /
ANIMALS / SHOES) with each item's name and coin cost. All art is procedural
(drawn from code). Costume/parrot/animal skins animate over the bird's 4 wing
frames; the shoes are shown by their product-shot icon (the sneaker itself),
and Pip wears them on his feet in-game.

![All Skybit Store items](all_items.png)

Regenerate after adding skins:

```sh
SDL_VIDEODRIVER=dummy python docs/store/render_gallery.py
```

The roster is data-driven: each item is a catalog entry in
[`game/store_catalog.py`](../../game/store_catalog.py) plus a procedural builder
in [`game/store_skins.py`](../../game/store_skins.py) (costumes + parrot species),
[`game/animal_skins.py`](../../game/animal_skins.py) (animals), or
[`game/shoe_skins.py`](../../game/shoe_skins.py) (shoes), dispatched by
`parrot.get_skin_frame` (and `parrot.get_skin_icon` for shoe product shots).
Design-loop records live in [`docs/store_skins/`](../store_skins),
[`docs/creatures/`](../creatures), and [`docs/shoes/`](../shoes).
