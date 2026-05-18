import trimesh
import numpy as np
from scipy.spatial.transform import Rotation
import os

def check_spatial_fit(mesh_filename, rotation_z_degrees, slot_bounds_x, slot_bounds_y, slot_bounds_z):
    """
    The Big-Ben Spatial Engine.
    Takes a mesh, simulates a rotation, and checks if it fits within the given boundaries.
    Returns a dictionary with the results.
    """
    if not os.path.exists(mesh_filename):
        return {"error": f"Mesh {mesh_filename} not found."}

    # 1. Load Mesh
    real_mesh = trimesh.load(mesh_filename)
    if isinstance(real_mesh, trimesh.Scene):
        real_mesh = real_mesh.dump(concatenate=True)
    
    original_vertices = np.array(real_mesh.vertices)

    # 2. Mental Rotation
    r = Rotation.from_euler('z', rotation_z_degrees, degrees=True)
    rotated_vertices = r.apply(original_vertices)

    # 3. Topological Logic Gate (Epsilon = 1e-3)
    epsilon = 1e-3
    collision = False
    for v in rotated_vertices:
        if not (slot_bounds_x[0] - epsilon <= v[0] <= slot_bounds_x[1] + epsilon and
                slot_bounds_y[0] - epsilon <= v[1] <= slot_bounds_y[1] + epsilon and
                slot_bounds_z[0] - epsilon <= v[2] <= slot_bounds_z[1] + epsilon):
            collision = True
            break # Exit early if we hit a wall to save compute

    if collision:
        return {"status": "FAILURE", "reason": "The object mathematically collided with the boundaries."}
    else:
        return {"status": "SUCCESS", "reason": "The object fits perfectly."}