bl_info = {
    "name": "Change Render Settings",
    "location": "View3D > Add > Mesh > Render Settings",
    "description": "Sets render settings of the scene",
    "author": "Arnaud Trouve",
    "version": (0,1),
    "blender": (2, 7, 0),
    "category": "Add Mesh",
    }

import bpy

class renderSettings(bpy.types.Operator):
    """Sets render settings"""
    bl_idname = "object.render_setting"
    bl_label = "Set Render Settings"
    bl_options = {'REGISTER', 'UNDO'}    
    
    def execute(self, context):
    
        scene = bpy.context.scene
        
        scene.render.resolution_x = 2880
        scene.render.resolution_y = 1620
        scene.render.resolution_percentage = 100
        scene.render.use_border = False
        scene.cycles.samples = 1400
        scene.cycles.no_caustics = True
        
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(renderSettings.bl_idname, icon='MOD_SKIN')
            
def register():
    bpy.utils.register_class(renderSettings)
    bpy.types.INFO_MT_mesh_add.append(menu_func)
    
def unregister():
    bpy.utils.unregister_class(renderSettings)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
    
if __name__ == "__main__":
    register()
