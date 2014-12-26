bl_info = {
    "name": "Set Hair Settings",
    "location": "View3D > Add > Mesh > Hair Settings",
    "description": "Sets render settings of hair (Particles)",
    "author": "Arnaud Trouve",
    "version": (0,1),
    "blender": (2, 7, 0),
    "category": "Add Mesh",
    }

import bpy

class hairSettings(bpy.types.Operator):
    """Sets Hair settings"""
    bl_idname = "object.hair_setting"
    bl_label = "Set Hair Settings"
    bl_options = {'REGISTER', 'UNDO'}    
    
    def execute(self, context):
    
        bpy.types.SpaceProperties.context = 'PARTICLES'

        #Set particle systems: hair_body (0), hair_neck (3), hair_bec (4)
        # hair_body
        bpy.types.ParticleSystem.active_index = 0
        bpy.data.particles["ParticleSettings"].child_nbr = 50
        bpy.data.particles["ParticleSettings"].rendered_child_count = 300
        bpy.data.particles["ParticleSettings"].clump_factor = 0.05
        bpy.data.particles["ParticleSettings"].child_parting_factor = 0.02
        bpy.data.particles["ParticleSettings"].rougness_2 = 0.002
        bpy.context.object.root_width = 0.4
        bpy.context.object.radius_scale = 0.00016

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(hairSettings.bl_idname, icon='MOD_SKIN')
            
def register():
    bpy.utils.register_class(hairSettings)
    bpy.types.INFO_MT_mesh_add.append(menu_func)
    
def unregister():
    bpy.utils.unregister_class(hairSettings)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
    
if __name__ == "__main__":
    register()
