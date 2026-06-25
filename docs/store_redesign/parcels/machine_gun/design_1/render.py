import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "parcels"))   # docs/parcels (_parcel_lib)
sys.path.insert(0, str(HERE))                            # local build.py
import _parcel_lib as L
from build import build
L.render_concept_sheet(build, "MACHINE GUN", str(HERE / "round_1.png"))
