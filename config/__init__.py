import importlib
import sys

try:
    config = importlib.import_module("config.config")
except ModuleNotFoundError:
    print("\n\nERROR: config/config.py was not found, please make sure it exists\n\n",
          file=sys.stderr)
