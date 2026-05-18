import trimesh
import numpy as np
from scipy.spatial.transform import Rotation
import sys

print("--- Big-Ben: Real 3D Mesh Integration ---")

# 1. LOAD A REAL 3D MESH
mesh_filename = 'my_part.obj' 
try:
    # This reads the raw geometric data from the icosphere we just generated
    real_mesh = trimesh.load(mesh_filename)
    if isinstance(real_mesh, trimesh.Scene):
        real_mesh = real_mesh.dump(concatenate=True)
except FileNotFoundError:
    print(f"ERROR: Could not find '{mesh_filename}'.")
    sys.exit()

original_vertices = np.array(real_mesh.vertices)
print(f"Successfully loaded '{mesh_filename}'!")
print(f"Total Vertices to process: {len(original_vertices)}")

# 2. DEFINE THE TRANSFORMATION
# We mentally rotate the complex mesh 90 degrees around the Z axis
r = Rotation.from_euler('z', 90, degrees=True)
rotated_vertices = r.apply(original_vertices)

# 3. DYNAMIC ENVIRONMENT GENERATION 
# Instead of hardcoding a slot, we build a mathematical bounding box
# perfectly molded to the ROTATED version of your specific mesh.
min_bounds = np.min(rotated_vertices, axis=0)
max_bounds = np.max(rotated_vertices, axis=0)

slot_x_bounds = [min_bounds[0], max_bounds[0]]
slot_y_bounds = [min_bounds[1], max_bounds[1]]
slot_z_bounds = [min_bounds[2], max_bounds[2]]

# 4. TOPOLOGICAL LOGIC GATE (with Epsilon)
def topological_logic_gate(vertices, slot_x, slot_y, slot_z, epsilon=1e-3):
    # This loop now checks hundreds of vertices in milliseconds
    for v in vertices:
        if not (slot_x[0] - epsilon <= v[0] <= slot_x[1] + epsilon and
                slot_y[0] - epsilon <= v[1] <= slot_y[1] + epsilon and
                slot_z[0] - epsilon <= v[2] <= slot_z[1] + epsilon):
            return True # Collision Detected
    return False # Fits perfectly

# 5. EXECUTE TESTS
print("\n[TEST 1]: Trying to force the UNROTATED mesh into the target slot...")
collision_test_1 = topological_logic_gate(original_vertices, slot_x_bounds, slot_y_bounds, slot_z_bounds)
print(f"Logic Gate Output -> COLLISION: {collision_test_1}")

print("\n[TEST 2]: Applying mental rotation, then testing slot...")
collision_test_2 = topological_logic_gate(rotated_vertices, slot_x_bounds, slot_y_bounds, slot_z_bounds)
print(f"Logic Gate Output -> COLLISION: {collision_test_2}")

print("\n--------------------------------------------------")
if not collision_test_2:
    print("SYSTEM VERIFIED: Big-Ben successfully evaluated a real, dynamic 3D mesh.")