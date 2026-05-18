import trimesh
import numpy as np
import math
from scipy.spatial.transform import Rotation

print("--- The Neuro-Symbolic God Stack (PoC) ---")

# 1. GENERATE THE DATA (Layer 1)
leg1 = trimesh.creation.box(extents=[1, 2, 1])
leg1.apply_translation([0, 1, 0])
leg2 = trimesh.creation.box(extents=[2, 1, 1])
leg2.apply_translation([0.5, 0, 0])
l_block = trimesh.util.concatenate([leg1, leg2])
original_vertices = np.array(l_block.vertices)

# 2. DEFINE THE ENVIRONMENT (The Gore Constraint)
slot_x_bounds = [-2.5, 1.5]
slot_y_bounds = [-0.5, 1.5]
slot_z_bounds = [-0.5, 0.5]

def topological_logic_gate(vertices, slot_x, slot_y, slot_z):
    for v in vertices:
        if not (slot_x[0] <= v[0] <= slot_x[1] and 
                slot_y[0] <= v[1] <= slot_y[1] and 
                slot_z[0] <= v[2] <= slot_z[1]):
            return True  # Collision Detected!
    return False  # Topologically Consistent

# 3. TEST 1: NO ROTATION
print("\n[TEST 1]: Trying to force the standing block into the flat slot...")
print("Original vertices (first 3):")
for v in original_vertices[:3]:
    print(f"  ({v[0]:.2f}, {v[1]:.2f}, {v[2]:.2f})")
print(f"Slot bounds: X:{slot_x_bounds}, Y:{slot_y_bounds}, Z:{slot_z_bounds}")

collision_test_1 = topological_logic_gate(original_vertices, slot_x_bounds, slot_y_bounds, slot_z_bounds)
print(f"Logic Gate Output -> COLLISION: {collision_test_1}")

# 4. EXECUTE MENTAL ROTATION
r = Rotation.from_euler('z', 90, degrees=True)
rotated_vertices = r.apply(original_vertices)

# 5. TEST 2: ROTATED OBJECT
print("\n[TEST 2]: Applying 90-degree mental rotation around Z-axis...")
print("Rotated vertices (first 3):")
for v in rotated_vertices[:3]:
    print(f"  ({v[0]:.2f}, {v[1]:.2f}, {v[2]:.2f})")

collision_test_2 = topological_logic_gate(rotated_vertices, slot_x_bounds, slot_y_bounds, slot_z_bounds)
print(f"Logic Gate Output -> COLLISION: {collision_test_2}")

print("\n" + "-"*50)
if not collision_test_2:
    print("SYSTEM VERIFIED: AI successfully rotated the object and passed physical validation.")
else:
    print("SYSTEM FAILED: Object still collides after rotation.")
    print("This means either:")
    print("  1. The slot dimensions don't fit the L-block")
    print("  2. The rotation axis is wrong (try rotating around 'x' or 'y' instead)")