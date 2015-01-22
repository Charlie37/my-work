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
    "name": "Move Modifier",
    "author": "Arnaud Trouve",
    "version": (0,1,1),
    "blender": (2, 70, 0),
    "location": "View3D > Add > Mesh",
    "description": "Move modifier up",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
        "Scripts/",
    "tracker_url": "https://developer.blender.org/",
    "category": "Add Mesh"}

"""
Modifier Move Up
"""

# import modules
import bpy
from bpy.props import *
from mathutils import *
from math import *

# Moves the modifier "Armature" to the top of modifiers' list.
# Can be updated with modifier's name as parameter.

# path: Applications/blender/Content/MacOS/2.70/scripts/addons
# in Blender: add using User Preferences > Addons, then refresh list and select addon.
# in 3D view: Shift+A > Mesh


###------------------------------------------------------------
# Move modifier
class modifier_move(bpy.types.Operator):
    """Move up the mesh modifier"""
    bl_idname = "mesh.modifier_move"
    bl_label = "Modifier"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    bl_description = "Move modifier up"

    # properties
    AutoUpdate = BoolProperty(name="Mesh update",
                default=True,
                description="Update mesh")


    ###------------------------------------------------------------
    # Execute
    def execute(self, context):
        print("Action")

        for obj in bpy.context.scene.objects:
            bpy.context.scene.objects.active = obj
            length = len(obj.modifiers)
            for num in range(length):
                bpy.ops.object.modifier_move_up(modifier="Armature")

        #mesh update
        if self.AutoUpdate != 0:

            # turn off undo
            undo = bpy.context.user_preferences.edit.use_global_undo
            bpy.context.user_preferences.edit.use_global_undo = False

            # deselect all objects when in object mode
            if bpy.ops.object.select_all.poll():
                bpy.ops.object.select_all(action='DESELECT')

            # restore pre operator undo state
            bpy.context.user_preferences.edit.use_global_undo = undo

            return {'FINISHED'}
        else:
            return {'PASS_THROUGH'}


###------------------------------------------------------------
# Register

# Define "Move Modifier" menu
def menu_func_move_modifier(self, context):
    self.layout.operator(modifier_move.bl_idname, text="Move Modifier", icon="PLUGIN")

def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_mesh_add.append(menu_func_move_modifier)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_mesh_add.remove(menu_func_move_modifier)

if __name__ == "__main__":
    register()
