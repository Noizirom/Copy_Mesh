# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Copy Select Faces to New Object",
    "description": "Adds a New Object from Selected Faces",
    "author": "Noizirom",
    "version": (1, 0, 0),
    "blender": (3, 00, 0),
    "location": "View3D",
    "warning": "", 
    "wiki_url": "",
    "tracker_url": "",
    "category": "Copy Mesh"
}

if "bpy" in locals():
    import importlib
    importlib.reload(copy_mesh)
    importlib.reload(object_utils)
    importlib.reload(panel)
else:
    from . import copy_mesh
    from . import object_utils
    from . import panel

import bpy

def register():
    panel.register()

def unregister():
    panel.unregister()


if __name__ == "__main__":
    register()