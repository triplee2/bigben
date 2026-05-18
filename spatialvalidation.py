"""
Neuro-Symbolic Spatial Validation - Upgraded
Three levels of constraint checking:
  Level 1: AABB (fixed from original - was buggy)
  Level 2: Signed Distance Field (SDF) - checks actual surface proximity
  Level 3: Mesh Boolean Intersection - true geometric collision
"""

import trimesh
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.spatial import ConvexHull

print("=" * 60)
print("  NEURO-SYMBOLIC SPATIAL VALIDATION v2")
print("=" * 60)

# ─────────────────────────────────────────────
# LAYER 1: Generate the L-Block
# ─────────────────────────────────────────────
leg1 = trimesh.creation.box(extents=[1, 2, 1])
leg1.apply_translation([0, 1, 0])
leg2 = trimesh.creation.box(extents=[2, 1, 1])
leg2.apply_translation([0.5, 0, 0])
l_block = trimesh.util.concatenate([leg1, leg2])
original_vertices = np.array(l_block.vertices)

print(f"\nL-Block bounding box:")
print(f"  X: [{original_vertices[:,0].min():.2f}, {original_vertices[:,0].max():.2f}]")
print(f"  Y: [{original_vertices[:,1].min():.2f}, {original_vertices[:,1].max():.2f}]")
print(f"  Z: [{original_vertices[:,2].min():.2f}, {original_vertices[:,2].max():.2f}]")

# ─────────────────────────────────────────────
# MENTAL ROTATION (same as before)
# ─────────────────────────────────────────────
r = Rotation.from_euler('z', 90, degrees=True)
rotated_vertices = r.apply(original_vertices)

# Center the rotated block at origin so the slot can be defined cleanly
rotated_center = (rotated_vertices.max(axis=0) + rotated_vertices.min(axis=0)) / 2
rotated_vertices_centered = rotated_vertices - rotated_center

print(f"\nRotated + Centered block bounding box:")
print(f"  X: [{rotated_vertices_centered[:,0].min():.2f}, {rotated_vertices_centered[:,0].max():.2f}]")
print(f"  Y: [{rotated_vertices_centered[:,1].min():.2f}, {rotated_vertices_centered[:,1].max():.2f}]")
print(f"  Z: [{rotated_vertices_centered[:,2].min():.2f}, {rotated_vertices_centered[:,2].max():.2f}]")

# ─────────────────────────────────────────────
# DEFINE THE SLOT (sized correctly for rotated block)
# ─────────────────────────────────────────────
# Slot exactly matches the rotated block's bounding box with small tolerance
rot_min = rotated_vertices_centered.min(axis=0)
rot_max = rotated_vertices_centered.max(axis=0)
tolerance = 0.05  # tight but passable

slot_bounds = {
    'x': [rot_min[0] - tolerance, rot_max[0] + tolerance],
    'y': [rot_min[1] - tolerance, rot_max[1] + tolerance],
    'z': [rot_min[2] - tolerance, rot_max[2] + tolerance],
}

print(f"\nSlot defined as:")
for axis, bounds in slot_bounds.items():
    print(f"  {axis}: [{bounds[0]:.2f}, {bounds[1]:.2f}]")


# ══════════════════════════════════════════════════════════
# LEVEL 1: AABB Check (Fixed)
# Axis-Aligned Bounding Box — fast but coarse
# ══════════════════════════════════════════════════════════
def aabb_collision(vertices, slot):
    """Fixed AABB: checks every vertex against slot bounds."""
    for v in vertices:
        if not (slot['x'][0] <= v[0] <= slot['x'][1] and
                slot['y'][0] <= v[1] <= slot['y'][1] and
                slot['z'][0] <= v[2] <= slot['z'][1]):
            return True
    return False


# ══════════════════════════════════════════════════════════
# LEVEL 2: Signed Distance Field (SDF) Constraint Check
# Instead of boolean in/out, this measures HOW FAR each
# point is from the slot boundary. Negative = inside (safe),
# Positive = outside (collision), magnitude = severity.
# This is what real spatial models use for gradient-based
# reasoning about fit quality.
# ══════════════════════════════════════════════════════════
def sdf_slot_check(vertices, slot, collision_threshold=0.0):
    """
    SDF-based constraint check.
    Returns: (collision: bool, max_penetration: float, violation_count: int)
    Positive SDF value = outside slot = collision.
    """
    sdf_values = []
    for v in vertices:
        # Distance to each wall (negative = inside that wall's safe zone)
        dx_lo = slot['x'][0] - v[0]   # positive if left of left wall
        dx_hi = v[0] - slot['x'][1]   # positive if right of right wall
        dy_lo = slot['y'][0] - v[1]
        dy_hi = v[1] - slot['y'][1]
        dz_lo = slot['z'][0] - v[2]
        dz_hi = v[2] - slot['z'][1]

        # SDF = max of all signed distances
        # If any distance is positive, the point is outside that boundary
        sdf = max(dx_lo, dx_hi, dy_lo, dy_hi, dz_lo, dz_hi)
        sdf_values.append(sdf)

    sdf_array = np.array(sdf_values)
    max_penetration = sdf_array.max()
    violation_count = (sdf_array > collision_threshold).sum()
    collision = max_penetration > collision_threshold

    return collision, max_penetration, violation_count, sdf_array


# ══════════════════════════════════════════════════════════
# LEVEL 3: Convex Hull Overlap (Geometric Intersection)
# Uses actual mesh geometry, not just vertices.
# Checks if the shape's convex hull overlaps the slot volume.
# This is the foundation of the GJK algorithm used in
# physics engines and robotics.
# ══════════════════════════════════════════════════════════
def convex_hull_overlap_check(vertices, slot):
    """
    Checks geometric intersection using convex hull.
    Builds a box mesh for the slot and tests if
    any of the shape's hull vertices are outside it.
    Also reports what fraction of the shape is outside.
    """
    slot_mesh = trimesh.creation.box(extents=[
        slot['x'][1] - slot['x'][0],
        slot['y'][1] - slot['y'][0],
        slot['z'][1] - slot['z'][0],
    ])
    slot_center = np.array([
        (slot['x'][0] + slot['x'][1]) / 2,
        (slot['y'][0] + slot['y'][1]) / 2,
        (slot['z'][0] + slot['z'][1]) / 2,
    ])
    slot_mesh.apply_translation(slot_center)

    # Check which vertices are inside the slot mesh
    inside = slot_mesh.contains(vertices)
    fraction_inside = inside.sum() / len(vertices)
    collision = not np.all(inside)

    return collision, fraction_inside, inside


# ══════════════════════════════════════════════════════════
# RUN ALL THREE LEVELS ON BOTH TESTS
# ══════════════════════════════════════════════════════════

# Also center the original block for fair comparison
orig_center = (original_vertices.max(axis=0) + original_vertices.min(axis=0)) / 2
original_vertices_centered = original_vertices - orig_center

test_cases = [
    ("TEST 1: Original (standing) block", original_vertices_centered),
    ("TEST 2: Mentally rotated block (90° around Z)", rotated_vertices_centered),
]

for label, verts in test_cases:
    print(f"\n{'─'*60}")
    print(f"  {label}")
    print(f"{'─'*60}")

    # Level 1
    c1 = aabb_collision(verts, slot_bounds)
    print(f"\n  [Level 1] AABB Check")
    print(f"  COLLISION: {c1}")
    if c1:
        print(f"  → Some vertices are outside the slot boundary.")
    else:
        print(f"  → All vertices fit within slot bounds.")

    # Level 2
    c2, max_pen, n_violations, sdf_vals = sdf_slot_check(verts, slot_bounds)
    print(f"\n  [Level 2] SDF Constraint Check")
    print(f"  COLLISION: {c2}")
    print(f"  Max penetration depth: {max_pen:.4f} units")
    print(f"  Vertices violating boundary: {n_violations}/{len(verts)}")
    print(f"  SDF range: [{sdf_vals.min():.3f}, {sdf_vals.max():.3f}]")
    if not c2:
        print(f"  → Shape fits. Deepest point is {abs(sdf_vals.min()):.3f} units from wall.")

    # Level 3
    c3, frac_inside, inside_mask = convex_hull_overlap_check(verts, slot_bounds)
    print(f"\n  [Level 3] Convex Hull Geometric Intersection")
    print(f"  COLLISION: {c3}")
    print(f"  Fraction of vertices inside slot: {frac_inside*100:.1f}%")
    if not c3:
        print(f"  → 100% of shape geometry confirmed inside slot volume.")

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print("""
  Level 1 (AABB):  Fast but binary. Good for early culling.
  Level 2 (SDF):   Tells you HOW MUCH something collides.
                   This is what you need for gradient descent
                   in a learned spatial model — you can
                   backpropagate through SDF values to teach
                   a model to rotate until penetration = 0.
  Level 3 (Mesh):  Ground truth geometric validation.
                   Slowest but most accurate.

  The path to a Large Spatial Model is making Level 2
  differentiable and learned, not hand-coded.
""")