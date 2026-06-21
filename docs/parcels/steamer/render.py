import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0]))
sys.path.insert(0, str(HERE))
import _parcel_lib as L
from build import build
L.render_concept_sheet(build, "BAMBOO STEAMER", str(HERE / "round_3.png"))
