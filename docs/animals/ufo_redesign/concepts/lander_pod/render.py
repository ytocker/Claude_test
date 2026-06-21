import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))   # docs/animals/ufo_redesign -> _gameplay_lib
sys.path.insert(0, str(HERE))               # build.py
import _gameplay_lib as L
from build import build
L.render_concept_sheet(build, "LANDER POD", str(HERE / "round_1.png"))
