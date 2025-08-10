import bpy

CUT_INSTANCE_SUFFIX = "_cut"

def make_a_clone_in_new_collection():
    old_name = bpy.context.active_object.name

    collection_name = old_name + "_tileset"

    #clone target to keep original untouched
    bpy.ops.object.duplicate()
    clone = bpy.context.active_object
    clone.name = old_name + CUT_INSTANCE_SUFFIX
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # create new collection for exporting
    collection_name = clone.name
    cut_collection = bpy.data.collections.new(collection_name)
    bpy.data.scenes['Scene'].collection.children.link(cut_collection)

    # remove from current collection(s)
    for col in bpy.data.collections:
        if clone.name in col.objects:
            col.objects.unlink(clone)

    # and into the new one
    cut_collection.objects.link(clone)

    return {clone, collection_name}
