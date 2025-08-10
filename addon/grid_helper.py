import bpy
from mathutils import Vector

def place_grid_mesh(axis, grid_subdiv, grid_size):
    offset = Vector([0, 0, 0])
    match axis:
        case 'Z-':
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=grid_subdiv, y_subdivisions=grid_subdiv, size=grid_size, enter_editmode=False, align='WORLD', location=offset)
        case 'X-':
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=grid_subdiv, y_subdivisions=grid_subdiv, size=grid_size, enter_editmode=False, align='WORLD', location=offset, rotation=(0, 1.5708, 0))
        case 'Y-':
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=grid_subdiv, y_subdivisions=grid_subdiv, size=grid_size, enter_editmode=False, align='WORLD', location=offset, rotation=(1.5708, 0, 0))
