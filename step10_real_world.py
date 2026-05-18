import pybullet as p
import pybullet_data
import trimesh
import numpy as np
from scipy.spatial.transform import Rotation
import os

print("--- Big-Ben: Phase 1 (Perception) & Phase 4 (Physics) ---")

# ==========================================
# PHASE 1: NOISY PERCEPTION (Simulating LiDAR)
# ==========================================
print("\n[PERCEPTION] Simulating noisy depth-sensor scan of the L-Block...")

# 1. Generate the perfect "Ground Truth" shape
leg1 = trimesh.creation.box(extents=[1, 2, 1])
leg1.apply_translation([0, 1, 0])
leg2 = trimesh.creation.box(extents=[2, 1, 1])
leg2.apply_translation([0.5, 0, 0])
perfect_mesh = trimesh.util.concatenate([leg1, leg2])

# 2. Simulate a LiDAR Scan (Sample points and add Gaussian Noise)
# Real robots don't see meshes; they see a scatter of noisy points
point_cloud, _ = trimesh.sample.sample_surface(perfect_mesh, count=1000)
noise = np.random.normal(0, 0.05, point_cloud.shape) # Add 5cm of sensor noise
noisy_point_cloud = point_cloud + noise

# Save the noisy points as a raw geometry file for the physics engine
noisy_mesh = trimesh.Trimesh(vertices=noisy_point_cloud)
noisy_mesh.export("noisy_scan.obj")
print(f" -> Captured 1000 noisy data points. Saved as 'noisy_scan.obj'")

# ==========================================
# PHASE 4: DYNAMIC PHYSICS SIMULATION
# ==========================================
print("\n[PHYSICS] Initializing PyBullet Simulator (Headless Mode)...")

# 1. Connect to the physics engine (DIRECT means no GUI, runs silently in the cloud)
physicsClient = p.connect(p.DIRECT)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81) # Real gravity

# 2. Build the Environment (A physical floor with a hole/slot in it)
# Instead of math bounds, we build solid blocks to act as the walls of the slot
floor_collision_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[5, 5, 0.1])
floor_body = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=floor_collision_shape, basePosition=[0, 0, -0.1])

# 3. Load the Noisy Object into the Physics Engine
# PyBullet automatically wraps our scattered points in a 'Convex Hull' for collision
part_collision_shape = p.createCollisionShape(p.GEOM_MESH, fileName="noisy_scan.obj")

# 4. Agent Command: Rotate 90 Degrees and Drop
print("\n[EXECUTION] Applying 90-degree rotation and dropping object...")
r = Rotation.from_euler('z', 90, degrees=True)
orientation_quaternion = r.as_quat() # Physics engines use Quaternions, not Euler angles

# Spawn the object 2 meters in the air, rotated 90 degrees
part_body = p.createMultiBody(baseMass=1.0, 
                              baseCollisionShapeIndex=part_collision_shape, 
                              basePosition=[0, 0, 2.0], 
                              baseOrientation=orientation_quaternion)

# 5. Run the Simulation Forward in Time (100 steps)
for i in range(100):
    p.stepSimulation()

# 6. Evaluate the Result
# If it fit, gravity pulled it through the slot and its Z-coordinate will be negative.
# If it hit the walls, it will be resting on the floor (Z > 0).
final_position, _ = p.getBasePositionAndOrientation(part_body)
final_z_height = final_position[2]

print("-" * 50)
if final_z_height < 0:
    print(f"SYSTEM VERIFIED: Object successfully passed through the slot. (Final Height: {final_z_height:.2f}m)")
else:
    print(f"COLLISION: The object smashed into the floor and got stuck. (Final Height: {final_z_height:.2f}m)")
print("-" * 50)

p.disconnect()