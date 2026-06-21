import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
import _gameplay_lib as L
from build import build
L.render_concept_sheet(build, "BLACK TRIANGLE", str(HERE / "round_2.png"))
