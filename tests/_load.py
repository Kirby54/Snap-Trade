"""Load a module script from skills/snap-and-trade/scripts/."""

import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "snap-and-trade", "scripts")
FIX = os.path.join(ROOT, "tests", "fixtures")


def load(folder, name):
    """`folder` is kept for compatibility with the original tests; every script now lives in scripts/."""
    path = os.path.join(SCRIPTS, name + ".py")
    spec = importlib.util.spec_from_file_location("trader_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
