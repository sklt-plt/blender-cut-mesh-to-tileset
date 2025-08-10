import bpy
from mathutils import Vector

from .octant_helper import calculate_vertices_median

# CUT_COLLECTION = ""
# DIRECTION = Vector(0,0,0)
# ORIGIN_ORDER = {}

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


def organize_objects(block_size, cut_collection_name, direction, set_origins):
    global BLOCK_SIZE
    global DIRECTION
    global CUT_COLLECTION
    global SET_ORIGINS
    global ORIGIN_ORDER

    BLOCK_SIZE = block_size
    DIRECTION = direction
    CUT_COLLECTION = cut_collection_name
    SET_ORIGINS = set_origins

    ORIGIN_ORDER = generate_naming_order_and_origins()

    organize_object_names()

    connect_split_objects_in_same_block()

    notify_about_missing_blocks()


def organize_object_names():
    bpy.ops.object.mode_set(mode='OBJECT')

    for object in bpy.data.collections[CUT_COLLECTION].objects:

        median = calculate_vertices_median(object.data.vertices)

        for key in ORIGIN_ORDER:
            origin = ORIGIN_ORDER[key]
            end_origin = origin + Vector([BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE])

            if origin.x <= abs(median.x) <= end_origin.x and origin.y <= abs(median.y) <= end_origin.y and origin.z <= abs(median.z) <= end_origin.z:
                object.name = str(key)
                break

def set_origin_to_offset(origin_offset, obj):
    bpy.data.scenes['Scene'].cursor.location= origin_offset * DIRECTION
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')


def connect_split_objects_in_same_block():
    #some meshes in same NxNxN "block" may have been separated due to lack of common edges
    #if we find two that should have same name (i.e. occupy same block, like 'aaa' and 'aaa.001') we should join them
    cut_object_collection = bpy.data.collections[CUT_COLLECTION].objects

    for key in ORIGIN_ORDER:
        maybe_duplicates = []
        for obj in cut_object_collection:
            if key in obj.name:
                maybe_duplicates.append(obj)

                if SET_ORIGINS:
                    set_origin_to_offset(ORIGIN_ORDER[key], obj)


        if len(maybe_duplicates) > 1:
            bpy.ops.object.select_all(action='DESELECT')
            for dup in maybe_duplicates:
                dup.select_set(True)

            bpy.context.view_layer.objects.active = maybe_duplicates[0]
            bpy.ops.object.join()


def notify_about_missing_blocks():
    #some blocks may not exist if there were no faces in there (for example inside enclosed larger model) - we should notify about that
    cut_object_collection = bpy.data.collections[CUT_COLLECTION].objects
    for key in ORIGIN_ORDER:
        if cut_object_collection.keys().count(key) == 0:
            print("Missing " + str(key))
