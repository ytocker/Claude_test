import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "docs" / "animals" / "ufo_redesign"))
sys.path.insert(0, str(HERE))
import _gameplay_lib as L
from build import build
L.render_concept_sheet(build, "BURRO PINATA", str(HERE / "round_1.png"))
