import bpy
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

GRID_SUBDIV_DEFAULT = int(GRID_SIZE / BLOCK_SIZE)   # wee're using primitive grid for cuts, so we need to provide it's subdivision amount
GRID_SUBDIV = GRID_SIZE_DEFAULT

CALCULATE_OBJECT_OCTANT_LOCATION = True             # should object's octant in world-space be automatically determined
DIRECTION = Vector([1,1,1])                         # manually set this if you have object not fitting in one octant
                                                    # but beware this also determines on which side each tile origin's will be set (if enabled below)

SET_ORIGINS = True                                  # whether or not we should set each resulting object's origin
                                                    # this is unsupported for objects not contained in single octant

def context_override():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        return {'window': window, 'screen': screen, 'area': area, 'region': region, 'scene': bpy.context.scene}


def perform_ctt_hops(context):
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
    knife_using_hops(context_ov, clone, GRID_SUBDIV, GRID_SIZE)

    split_new_edges(context_ov, clone, BLOCK_SIZE)

    #move loose parts to separate objects
    bpy.ops.mesh.separate(type='LOOSE')

    organize_objects(BLOCK_SIZE, CUT_COLLECTION, DIRECTION, SET_ORIGINS)


class HOPSOperator(bpy.types.Operator):
    """Cut object using HOPS bool knife operator (if installed)"""
    bl_idname = "object.ctthops"
    bl_label = "ctt-using-hops"

    def execute(self, context):
        perform_ctt_hops(context)
        return {'FINISHED'}


def register_ctt():
    bpy.utils.register_class(HOPSOperator)

def unregister_ctt():
    bpy.utils.unregister_class(HOPSOperator)
