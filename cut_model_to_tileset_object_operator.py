import bpy, bmesh
from math import isclose

def knife_cut(target, axis):
    match axis:
        case 'Z-':
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=5, y_subdivisions=5, size=10, enter_editmode=False, align='WORLD', location=(5, 5, -10), scale=(1, 1, 1))
        case 'X-':
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=5, y_subdivisions=5, size=10, enter_editmode=False, align='WORLD', location=(-10, -5, 5), scale=(1, 1, 1), rotation=(0, 1.5708, 0))
        case 'Y-':
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=5, y_subdivisions=5, size=10, enter_editmode=False, align='WORLD', location=(5, -10, 5), scale=(1, 1, 1), rotation=(1.5708, 0, 0))
        
            
    gridcutter = bpy.context.active_object
    gridcutter.name = "gridcutter " + axis
    bpy.ops.object.transform_apply()
    
    bpy.context.view_layer.objects.active = target
    
    bpy.ops.hops.bool_knife(knife_project=True, projection=axis)
    
    bpy.data.objects.remove(gridcutter)  
    
    
def context_override():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        return {'window': window, 'screen': screen, 'area': area, 'region': region, 'scene': bpy.context.scene} 
                    
                    
def cut_new_edges(context_ov, target):
    with bpy.context.temp_override(**context_ov): 
        knife_cut(target, 'Z-')
        knife_cut(target, 'X-')
        knife_cut(target, 'Y-')
        

def are_edge_verts_on_glob_axis(edge, axis, glob_axis):
    PRECISION = 0.01
    return isclose(abs(edge.verts[0].co[axis]), glob_axis, rel_tol=PRECISION) and isclose(abs(edge.verts[1].co[axis]), glob_axis, rel_tol=PRECISION)
            
            
def split_along_an_axis(clone_bmesh, axis):
    CUT_AXIS_GL_0 = 2.0
    CUT_AXIS_GL_1 = 4.0
    
    edges_to_split = []
    for e in clone_bmesh.edges:
        if are_edge_verts_on_glob_axis(e, axis, CUT_AXIS_GL_0) or are_edge_verts_on_glob_axis(e, axis, CUT_AXIS_GL_1):
            edges_to_split.append(e)
            
    bmesh.ops.split_edges(clone_bmesh,edges=edges_to_split)
    

def split_new_edges(context_ov, clone):
    bpy.ops.object.mode_set(mode = 'EDIT') 
    
    # deselect all
    with bpy.context.temp_override(**context_ov): 
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action = 'DESELECT') 
        bpy.ops.mesh.select_mode(type="EDGE")
        
    
    clone_bmesh = bmesh.from_edit_mesh(clone.data)
    
    split_along_an_axis(clone_bmesh, 0)
    split_along_an_axis(clone_bmesh, 1)
    split_along_an_axis(clone_bmesh, 2)
    
           
def make_a_clone_in_new_collection():
    # create new collection for exporting
    cut_collection = bpy.data.collections.new("cuts")
    bpy.data.scenes['Scene'].collection.children.link(cut_collection)
    
    #clone target for operation safety
    bpy.ops.object.duplicate()
    clone = bpy.context.active_object
    clone.name = clone.name + "_cut"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    for col in bpy.data.collections:
        if clone.name in col.objects:
            col.objects.unlink(clone)
            
    cut_collection.objects.link(clone)
    
    return clone

def main(context):
    original = bpy.context.active_object
    assert original is not None, "A Target object must be selected"
    
    context_ov = context_override()

    clone = make_a_clone_in_new_collection()

    cut_new_edges(context_ov, clone)
    
    split_new_edges(context_ov, clone)
    

class SimpleOperator(bpy.types.Operator):
    """Cut object into tileset of 2x2x2 piece size"""
    bl_idname = "object.cut_to_tileset"
    bl_label = "Cut To Tileset"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(SimpleOperator.bl_idname, text=SimpleOperator.bl_label)


# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
def register():
    bpy.utils.register_class(SimpleOperator)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(SimpleOperator)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    #register()

    # test call
    main(bpy.context)
