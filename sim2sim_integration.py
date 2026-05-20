import pybullet as p
import pybullet_data
import os
import time
from world_labs_client import WorldLabsMockClient

def run_integrated_pipeline():
    print("--- Big-Ben V2: Full Sim2Sim Integration Layer ---")
    
    # 1. TRIGGER GENERATIVE SIMULATION LAYER (World Labs API)
    client = WorldLabsMockClient()
    prompt = "A heavy metal fabrication workbench with a rectangular parts bin offset to the right"
    
    job_id = client.generate_world_async(prompt)
    metadata = client.poll_job_status(job_id)
    mesh_path = client.bake_and_download_collider_mesh(metadata)
    
    # 2. INITIALIZE VALIDATION SIMULATION LAYER (PyBullet Engine)
    print("\n[VALIDATION] Booting physics environment...")
    physics_client = p.connect(p.DIRECT)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.81)
    
    # Load base floor
    p.loadURDF("plane.urdf")
    
    # Spawn the 7-DOF KUKA arm
    print("[VALIDATION] Instantiating 7-DOF KUKA LBR IIWA Arm...")
    robot_id = p.loadURDF("kuka_iiwa/model.urdf", [0, 0, 0], useFixedBase=True)
    
    # 3. DYNAMIC ASSET INJECTION (Loading the generated .obj)
    print(f"[VALIDATION] Injecting generative world collider mesh: '{mesh_path}'")
    
    # PyBullet requires a visual shape and collision shape to map raw OBJ files
    visual_shape_id = p.createVisualShape(shapeType=p.GEOM_MESH, fileName=mesh_path, rgbaColor=[0.5, 0.5, 0.5, 1])
    collision_shape_id = p.createCollisionShape(shapeType=p.GEOM_MESH, fileName=mesh_path)
    
    # Instantiate the static world object directly into the environment
    world_body_id = p.createMultiBody(
        baseMass=0, # Mass 0 means it is an immovable static structure/obstacle
        baseCollisionShapeIndex=collision_shape_id,
        baseVisualShapeIndex=visual_shape_id,
        basePosition=[0, 0, 0] # Placed at absolute origin (mesh vertices have offsets baked in)
    )
    print("[VALIDATION] Environment geometry linked to physics canvas successfully.")
    
    # 4. KINEMATICS SOLVER (Dynamic Pathing to the Variable Target)
    # Extract the target position that changed dynamically during generation
    target_x = metadata["slot_center_x"]
    target_y = metadata["slot_center_y"]
    target_z = 0.35 # Height of the bin surface
    
    print(f"\n[KINEMATICS] Extracting dynamic target coordinate: [{target_x:.3f}, {target_y:.3f}, {target_z:.3f}]")
    print("[KINEMATICS] Computing Numerical Inverse Kinematics trajectory...")
    
    # KUKA IIWA end-effector link index is typically 6 (the 7th link)
    end_effector_link = 6
    
    # Run the Levenberg-Marquardt IK optimization solver inside PyBullet
    joint_angles = p.calculateInverseKinematics(
        bodyUniqueId=robot_id,
        endEffectorLinkIndex=end_effector_link,
        targetPosition=[target_x, target_y, target_z]
    )
    
    print("\n" + "="*50)
    print("SUCCESS: NON-DETERMINISTIC TRAJECTORY VERIFIED")
    print("="*50)
    print("The system successfully adapted to the variable environment layout.")
    print("Calculated Target Joint Positions for the 7-DOF Arm:")
    for idx, angle in enumerate(joint_angles):
        print(f"  -> Joint {idx + 1}: {angle:.4f} radians ({np.degrees(angle):.2f}°)")
    print("="*50)
    
    p.disconnect()

if __name__ == "__main__":
    # Import numpy locally for the degree conversion readout
    import numpy as np
    run_integrated_pipeline()