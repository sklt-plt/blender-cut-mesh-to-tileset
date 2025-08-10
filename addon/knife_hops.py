import bpy
from .grid_helper import place_grid_mesh


def knife_cut(target, axis):
    place_grid_mesh(axis, GRID_SUBDIV, GRID_SIZE)

    gridcutter = bpy.context.active_object
    gridcutter.name = "gridcutter " + axis
    bpy.ops.object.transform_apply()

    bpy.context.view_layer.objects.active = target

    bpy.ops.hops.bool_knife(knife_project=True, projection=axis)

    bpy.data.objects.remove(gridcutter)


def knife_using_hops(context_ov, target, grid_subdiv, grid_size):
    global GRID_SUBDIV, GRID_SIZE
    GRID_SUBDIV = grid_subdiv
    GRID_SIZE = grid_size

    with bpy.context.temp_override(**context_ov):
        knife_cut(target, 'Z-')
        knife_cut(target, 'X-')
        knife_cut(target, 'Y-')
