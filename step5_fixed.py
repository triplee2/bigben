import trimesh
import numpy as np
from scipy.spatial.transform import Rotation

print("--- Big-Ben Architecture (PoC) ---")

# 1. GENERATE THE DATA
leg1 = trimesh.creation.box(extents=[1, 2, 1])
leg1.apply_translation([0, 1, 0])
leg2 = trimesh.creation.box(extents=[2, 1, 1])
leg2.apply_translation([0.5, 0, 0])
l_block = trimesh.util.concatenate([leg1, leg2])
original_vertices = np.array(l_block.vertices)

# 2. DEFINE THE ENVIRONMENT 
slot_x_bounds = [-2.5, 1.5]
slot_y_bounds = [-0.5, 1.5] 
slot_z_bounds = [-0.5, 0.5]

# We add 'epsilon' to give a 0.001 margin of error for floating-point math
def topological_logic_gate(vertices, slot_x, slot_y, slot_z, epsilon=1e-3):
    for v in vertices:
        # We expand the acceptable bounds by an atomic fraction
        if not (slot_x[0] - epsilon <= v[0] <= slot_x[1] + epsilon and
                slot_y[0] - epsilon <= v[1] <= slot_y[1] + epsilon and
                slot_z[0] - epsilon <= v[2] <= slot_z[1] + epsilon):
            return True # Collision
    return False # Fits perfectly

# 3. TEST 1: NO ROTATION 
print("\n[TEST 1]: Trying to force the standing block into the flat slot...")
collision_test_1 = topological_logic_gate(original_vertices, slot_x_bounds, slot_y_bounds, slot_z_bounds)
print(f"Logic Gate Output -> COLLISION: {collision_test_1}")

# 4. EXECUTE MENTAL ROTATION 
r = Rotation.from_euler('z', 90, degrees=True)
rotated_vertices = r.apply(original_vertices)

# 5. TEST 2: ROTATED OBJECT 
print("\n[TEST 2]: Applying 90-degree mental rotation, then testing slot...")
collision_test_2 = topological_logic_gate(rotated_vertices, slot_x_bounds, slot_y_bounds, slot_z_bounds)
print(f"Logic Gate Output -> COLLISION: {collision_test_2}")

print("\n--------------------------------------------------")
if not collision_test_2:
    print("SYSTEM VERIFIED: Big-Ben successfully rotated the object and passed physical validation.")