import os
import sys

from .ui import register_ui
from .ui import unregister_ui

ADDON_FOLDER_PATH = os.path.dirname(__file__)
MODULE_NAME = "cuttotileset"
VERSION = (0, 0, 1)
ADDON_NAME = (f"Cut-to-tileset v{VERSION[0]}.{VERSION[1]}.{VERSION[2]}")

bl_info = {
    "name" : "Cut to tileset",
    "author" : "Jakub Miksa",
    "version" : (0, 0, 1),
    "blender": (4, 5, 0),
    "description" : "An (semi) automated tool to split mesh object into smaller, organized blocks",
    "category" : "Development"
}

def register():
    print(f'Enabled "{ADDON_NAME}"')
    print(f"\t adding {MODULE_NAME} to sys path: {ADDON_FOLDER_PATH}")
    sys.path.append(ADDON_FOLDER_PATH)

    print("REEE")
    ui.register_ui()


def unregister():
    print(f'DISABLE "{ADDON_NAME}" addon')
    ui.unregister_ui()
