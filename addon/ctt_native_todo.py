import bpy, bmesh
from mathutils import Vector

from .make_clone import make_a_clone_in_new_collection
from .octant_helper import calculate_octant_to_use
from .organize import organize_objects
from .split_edges import split_new_edges
from .knife_hops import knife_using_hops


CUT_COLLECTION = ""

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

#TODO
def knife_using_native_method(context_ov, target):
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

def perform_ctt_native(context):
    original = bpy.context.active_object
    assert original is not None, "A Target object must be selected"
    assert original.select_get(), "A Target object must be selected"

    context_ov = context_override()

    global CUT_COLLECTION
    clone, CUT_COLLECTION = make_a_clone_in_new_collection()

    global DIRECTION
    if CALCULATE_OBJECT_OCTANT_LOCATION:
        DIRECTION = calculate_octant_to_use(clone)

    #generate edges and split
    knife_using_native_method(context_ov, clone, GRID_SUBDIV, GRID_SIZE)

    split_new_edges(context_ov, clone, BLOCK_SIZE)

    #move loose parts to separate objects
    bpy.ops.mesh.separate(type='LOOSE')

    organize_objects(BLOCK_SIZE, CUT_COLLECTION, DIRECTION, SET_ORIGINS)
