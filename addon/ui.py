import bpy

class VIEW3D_PT_cut_to_tileset_panel(bpy.types.Panel):

    # where to add the panel in the UI
    bl_space_type = "VIEW_3D"  # 3D Viewport area
    bl_region_type = "UI"  # Sidebar region

    bl_category = "Cut to tileset"  # found in the Sidebar
    bl_label = "Cut to tileset"  # found at the top of the Panel

    def draw(self, context):
        """define the layout of the panel"""
        row = self.layout.row()
        row.operator("mesh.primitive_cube_add", text="Add Cube")
        row = self.layout.row()
        row.operator("mesh.primitive_ico_sphere_add", text="Add Ico Sphere")
        row = self.layout.row()
        row.operator("object.shade_smooth", text="Shade Smooth")


def register_ui():
    bpy.utils.register_class(VIEW3D_PT_cut_to_tileset_panel)


def unregister_ui():
    bpy.utils.unregister_class(VIEW3D_PT_cut_to_tileset_panel)
