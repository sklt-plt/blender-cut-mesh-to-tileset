import bpy, bmesh
from mathutils import *; from math import *

CUT_COLLECTION = "cuts"
CUT_INSTANCE_SUFFIX = "_cut"

def knife_cut(target, axis):
    # place grid mesh in appropriate location and rotation
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
    cut_collection = bpy.data.collections.new(CUT_COLLECTION)
    bpy.data.scenes['Scene'].collection.children.link(cut_collection)
    
    #clone target to keep original untouched
    bpy.ops.object.duplicate()
    clone = bpy.context.active_object
    clone.name = clone.name + CUT_INSTANCE_SUFFIX
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # remove from current collection(s)
    for col in bpy.data.collections:
        if clone.name in col.objects:
            col.objects.unlink(clone)
            
    # and into the new one
    cut_collection.objects.link(clone)
    
    return clone

def generate_naming_order_and_origins():
    # this could be hardcoded or in config for some custom locations
    # but just shifting by 2 works for default case
    
    # names need to be in sequential pattern (z-location, y-location, x-location) for the Godot script
    # but we can't use plain numbers like for ex. '001' due to blender naming auto-correction
    # this is because we may end up with two objects that should have same name because they occupy same 2x2x2 block
    # but were split because they didn't have a single common edge
    origins = {}
    for z in range(0,3):
        for y in range(0,3):
            for x in range(0,3):
                ASCII_OFFSET = ord('a')
                z_index = chr(ASCII_OFFSET + z)
                y_index = chr(ASCII_OFFSET + y)
                x_index = chr(ASCII_OFFSET + x)
                
                lexico_name = ''.join([z_index, y_index, x_index])
                
                posMin = Vector([x*2,y*2,z*2])    
                
                origins[lexico_name] = posMin
                
    return origins


def organize_object_names(origin_order):
    bpy.ops.object.mode_set(mode='OBJECT') 

    for object in bpy.data.collections[CUT_COLLECTION].objects:
        median = Vector([0,0,0])
        
        for v in object.data.vertices:
            median += v.co
            
        median = median / len(object.data.vertices)
            
        for key in origin_order:
            origin = origin_order[key]
            end_origin = origin + Vector([2,2,2])
                
            if origin.x <= abs(median.x) <= end_origin.x and origin.y <= abs(median.y) <= end_origin.y and origin.z <= abs(median.z) <= end_origin.z:
                object.name = str(key)
                break
            
def connect_split_objects_in_same_block(origin_order):
    #some meshes in same 2x2x2 "block" may have been separated due to lack of common edges
    #if we find two that should have same name (i.e. occupy same block, like 'aaa' and 'aaa.001') we should join them
    cut_object_collection = bpy.data.collections[CUT_COLLECTION].objects

    for key in origin_order:
        maybe_duplicates = []
        for obj in cut_object_collection:
            if key in obj.name:
                maybe_duplicates.append(obj)
                
        if len(maybe_duplicates) > 1:
            bpy.ops.object.select_all(action='DESELECT')
            for dup in maybe_duplicates:
                dup.select_set(True)
                
            bpy.context.view_layer.objects.active = maybe_duplicates[0]
            bpy.ops.object.join()
            
def notify_about_missing_blocks(origin_order):
    #some blocks may not exist if there were no faces in there (for example inside enclosed larger model) - we should notify about that
    cut_object_collection = bpy.data.collections[CUT_COLLECTION].objects
    for key in origin_order:
        if cut_object_collection.keys().count(key) == 0:
            print("Missing " + str(key))


def main(context):
    original = bpy.context.active_object
    assert original is not None, "A Target object must be selected"

    context_ov = context_override()

    clone = make_a_clone_in_new_collection()

    #generate edges and split
    cut_new_edges(context_ov, clone)

    split_new_edges(context_ov, clone)

    #move loose parts to separate objects
    bpy.ops.mesh.separate(type='LOOSE')

    #organize objects + set origins
    origin_order = generate_naming_order_and_origins()
    
    organize_object_names(origin_order)

    connect_split_objects_in_same_block(origin_order)

    notify_about_missing_blocks(origin_order)


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
