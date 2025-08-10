import bpy, bmesh
from math import isclose

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


def split_new_edges(context_ov, clone, block_size):
    global BLOCK_SIZE
    BLOCK_SIZE = block_size

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
