from mathutils import Vector

def calculate_vertices_median(vertices):
    median = Vector([0,0,0])

    for v in vertices:
        median += v.co

    return median / len(vertices)


def calculate_octant_to_use(clone):
    total_median = calculate_vertices_median(clone.data.vertices)

    new_x = 1.0 if total_median.x >= 0 else -1.0
    new_y = 1.0 if total_median.y >= 0 else -1.0
    new_z = 1.0 if total_median.z >= 0 else -1.0

    return Vector([new_x, new_y, new_z])
