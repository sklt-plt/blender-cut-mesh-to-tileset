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
        row.operator("object.ctthops", text="Cut object to tiles (HOPS)")


def register_ui():
    bpy.utils.register_class(VIEW3D_PT_cut_to_tileset_panel)


def unregister_ui():
    bpy.utils.unregister_class(VIEW3D_PT_cut_to_tileset_panel)
