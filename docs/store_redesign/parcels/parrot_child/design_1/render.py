import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, "/home/user/skybit/docs/parcels")
import _parcel_lib as L
from build import build
L.render_concept_sheet(build, "MINI-PIP", str(HERE / "round_2.png"))
