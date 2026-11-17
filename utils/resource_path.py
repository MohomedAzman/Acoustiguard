"""
utils/resource_path.py
Cross-environment resource-path resolution.

Resolves asset paths correctly both when running from source (python main.py)
and when running from a PyInstaller bundle (onefile or onedir), where data
files are unpacked to sys._MEIPASS.
"""

import os
import sys


def resource_path(relative_path):
    """
    Return an absolute path to a bundled resource.

    - PyInstaller (onefile/onedir): files extracted to sys._MEIPASS
    - Development: anchored to this file's project root (one level up from
      this module: utils/ -> project root), independent of the current
      working directory.

    Args:
        relative_path: Path relative to the project root, e.g.
                       "assets/AcoustiGuard logo.png"

    Returns:
        Absolute filesystem path. The file may not exist; callers should
        verify with os.path.isfile() before using.
    """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller sets sys._MEIPASS to the folder where bundled
        # data files are unpacked at runtime.
        base_path = sys._MEIPASS
    else:
        # Running from source. Anchor to the directory containing main.py
        # (this file lives in <root>/utils/, so go up one level), not to
        # the current working directory, which can vary depending on how
        # the app is launched.
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)
