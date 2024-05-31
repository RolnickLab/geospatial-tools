from pathlib import Path

import geopandas as gpd

APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent
CONFIG = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Set the default I/O engine
gpd.options.io_engine = "pyogrio"
