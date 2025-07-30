import bpy, bmesh
from mathutils import *; from math import *

CUT_COLLECTION = "name_for_the_collection__target_objects_name_goes_here"
CUT_INSTANCE_SUFFIX = "_cut"

BLOCK_SIZE_DEFAULT = 2                              # size of block, or spacing between cuts, in Blender units
BLOCK_SIZE = BLOCK_SIZE_DEFAULT

GRID_SIZE_DEFAULT = BLOCK_SIZE * 10                 # total grid size used for cuts, in Blender units
GRID_SIZE = GRID_SIZE_DEFAULT

GRID_SUBDIV_DEFAULT = int(GRID_SIZE / BLOCK_SIZE)   # we're using primitive grid for cuts, so we need to provide it's subdivision amount
GRID_SUBDIV = GRID_SIZE_DEFAULT

CALCULATE_OBJECT_OCTANT_LOCATION = True             # should object's octant in world-space be automatically determined
DIRECTION = Vector([1,1,1])                         # manually set this if you have object not fitting in one octant
                                                    # but beware this also determines on which side each tile origin's will be set

SET_ORIGINS = True                                  # whether or not we should set each resulting object's origin
                                                    # this is unsupported for objects not contained in single octan

def place_grid_mesh(axis):
    offset = Vector([0, 0, 0])
    match axis:
        case 'Z-':
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=GRID_SUBDIV, y_subdivisions=GRID_SUBDIV, size=GRID_SIZE, enter_editmode=False, align='WORLD', location=offset)
        case 'X-':
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=GRID_SUBDIV, y_subdivisions=GRID_SUBDIV, size=GRID_SIZE, enter_editmode=False, align='WORLD', location=offset, rotation=(0, 1.5708, 0))
        case 'Y-':
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=GRID_SUBDIV, y_subdivisions=GRID_SUBDIV, size=GRID_SIZE, enter_editmode=False, align='WORLD', location=offset, rotation=(1.5708, 0, 0))
        
        
def rotate_viewport(context, axis):
    # position view to ortho from side to have visible grid
    VIEW_TOP_DOWN = Quaternion((1, 0, 0, 0))
    VIEW_FRONT_BACK = Quaternion((0.7071067690849304, 0.7071067690849304, -0.0, -0.0))
    VIEW_LEFT_RIGHT = Quaternion((0.5, 0.5, 0.5, 0.5))
    
    match axis:
        case 'Z-':
            context["region"].data.view_rotation = VIEW_TOP_DOWN
        case 'X-':
            context["region"].data.view_rotation = VIEW_LEFT_RIGHT
        case 'Y-':
            context["region"].data.view_rotation = VIEW_FRONT_BACK
            

def prepare_gridcutter(axis):
    place_grid_mesh(axis)
            
    gridcutter = bpy.context.active_object
    gridcutter.name = "gridcutter " + axis
    
    # remove all faces but keep edges
    
    bpy.ops.object.mode_set(mode = 'EDIT')
    bmesh_grid = bmesh.from_edit_mesh(bpy.context.active_object.data)
    for face in bmesh_grid.faces:
        bmesh_grid.faces.remove(face)
        
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    return gridcutter

def knife_cut(context, target, axis):
    target.select_set(False)
    
    gridcutter = prepare_gridcutter(axis)
   
    # why this does not affect knife_project?
    #rotate_viewport(context, axis)

    gridcutter.select_set(False)
    target.select_set(True)
    bpy.context.view_layer.objects.active = target

    bpy.ops.object.mode_set(mode = 'EDIT')
  
    gridcutter.select_set(True)
  
    bpy.ops.mesh.knife_project()

    bpy.data.objects.remove(gridcutter)  
    
    
def context_override():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        cont = {'window': window, 'screen': screen, 'area': area, 'region': region, 'scene': bpy.context.scene} 
                        return cont
                    
                    
def cut_new_edges(context_ov, target):
    with bpy.context.temp_override(**context_ov): 
        #we need to put 3d view into position for knife tool to work
        #so let's remember original settings
        original_view_matrix = context_ov["region"].data.view_matrix
        original_persp = context_ov["region"].data.view_perspective
        
        context_ov["region"].data.view_perspective = 'ORTHO'
        
        rotate_viewport(context_ov, 'Z-')
        knife_cut(context_ov, target, 'Z-')
        #knife_cut(context_ov, target, 'X-')
        #knife_cut(context_ov, target, 'Y-')
        
        #restore original 3d view
        #context_ov["region"].data.view_matrix = original_view_matrix
        #context_ov["region"].data.view_perspective = original_persp
        

def are_edge_verts_on_glob_axis(edge, axis, glob_axis):
    PRECISION = 0.01
    return isclose(abs(edge.verts[0].co[axis]), glob_axis, rel_tol=PRECISION) and isclose(abs(edge.verts[1].co[axis]), glob_axis, rel_tol=PRECISION)
            
            
def split_along_an_axis(clone_bmesh, axis):
    CUT_AXIS_GL_0 = BLOCK_SIZE
    CUT_AXIS_GL_1 = BLOCK_SIZE * 2
    
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
    old_name = bpy.context.active_object.name
    
    global CUT_COLLECTION 
    CUT_COLLECTION = old_name + "_tileset"
    
    #clone target to keep original untouched
    bpy.ops.object.duplicate()
    clone = bpy.context.active_object
    clone.name = old_name + CUT_INSTANCE_SUFFIX
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # create new collection for exporting
    CUT_COLLECTION = clone.name
    cut_collection = bpy.data.collections.new(CUT_COLLECTION)
    bpy.data.scenes['Scene'].collection.children.link(cut_collection)
    
    # remove from current collection(s)
    for col in bpy.data.collections:
        if clone.name in col.objects:
            col.objects.unlink(clone)
            
    # and into the new one
    cut_collection.objects.link(clone)
    
    return clone

def generate_naming_order_and_origins():
    # this could be hardcoded or in config for some custom locations
    # but just shifting by N works for default case
    
    # names need to be in sequential pattern (z-location, y-location, x-location) for the Godot script
    # but we can't use plain numbers like for ex. '001' due to blender naming auto-correction
    # this is because we may end up with two objects that should have same name because they occupy same NxNxN block
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
                
                posMin = Vector([x*BLOCK_SIZE,y*BLOCK_SIZE,z*BLOCK_SIZE])    
                
                origins[lexico_name] = posMin
                
    return origins

def calculate_vertices_median(vertices):
    median = Vector([0,0,0])
    
    for v in vertices:
        median += v.co
        
    return median / len(vertices)

def organize_object_names(origin_order):
    bpy.ops.object.mode_set(mode='OBJECT') 

    for object in bpy.data.collections[CUT_COLLECTION].objects:

        median = calculate_vertices_median(object.data.vertices)
            
        for key in origin_order:
            origin = origin_order[key]
            end_origin = origin + Vector([BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE])
                
            if origin.x <= abs(median.x) <= end_origin.x and origin.y <= abs(median.y) <= end_origin.y and origin.z <= abs(median.z) <= end_origin.z:
                object.name = str(key)
                break
            
def set_origin_to_offset(origin_offset, obj):
    bpy.data.scenes['Scene'].cursor.location= origin_offset * DIRECTION
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

            
def connect_split_objects_in_same_block(origin_order):
    #some meshes in same NxNxN "block" may have been separated due to lack of common edges
    #if we find two that should have same name (i.e. occupy same block, like 'aaa' and 'aaa.001') we should join them
    cut_object_collection = bpy.data.collections[CUT_COLLECTION].objects

    for key in origin_order:
        maybe_duplicates = []
        for obj in cut_object_collection:
            if key in obj.name:
                maybe_duplicates.append(obj)
                
                if SET_ORIGINS:
                    set_origin_to_offset(origin_order[key], obj)

                
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

def calculate_octant_to_use(clone):
    global DIRECTION
    
    total_median = calculate_vertices_median(clone.data.vertices)

    new_x = 1.0 if total_median.x >= 0 else -1.0
    new_y = 1.0 if total_median.y >= 0 else -1.0
    new_z = 1.0 if total_median.z >= 0 else -1.0
    
    DIRECTION = Vector([new_x, new_y, new_z])

def main(context):
    original = bpy.context.active_object
    assert original is not None, "A Target object must be selected"
    
    context_ov = context_override()

    clone = make_a_clone_in_new_collection()
    
    calculate_octant_to_use(clone)

    #generate edges and split
    cut_new_edges(context_ov, clone)

#    split_new_edges(context_ov, clone)

#    #move loose parts to separate objects
#    bpy.ops.mesh.separate(type='LOOSE')

#    #organize objects
#    origin_order = generate_naming_order_and_origins()
#    
#    organize_object_names(origin_order)

#    connect_split_objects_in_same_block(origin_order)

#    notify_about_missing_blocks(origin_order)
    
def test_grids(context):
    context_ov = context_override()
    
    with bpy.context.temp_override(**context_ov): 
        place_grid_mesh('Z-')
        place_grid_mesh('X-')
        place_grid_mesh('Y-')

if __name__ == "__main__":
    #test_grids(bpy.context)
    main(bpy.context)
