import pybullet as p
import pybullet_data
import os

def initialize_validation_space():
    """
    Initializes a headless physics simulation workspace
    and dynamically verifies file paths before instantiation.
    """
    print("[INIT] Connecting to headless PyBullet physics server...")
    physics_client = p.connect(p.DIRECT)
    
    # Configure and verify search paths
    data_path = pybullet_data.getDataPath()
    p.setAdditionalSearchPath(data_path)
    
    p.setGravity(0, 0, -9.81)
    print("[INIT] Generating zero-state ground plane...")
    plane_id = p.loadURDF("plane.urdf")
    
    # Use the guaranteed KUKA IIWA model path
    relative_urdf_path = "kuka_iiwa/model.urdf"
    full_urdf_path = os.path.join(data_path, relative_urdf_path)
    
    print(f"[CHECK] Verifying asset path locally: {full_urdf_path}")
    if not os.path.exists(full_urdf_path):
        p.disconnect()
        raise FileNotFoundError(f"Asset missing from pybullet_data installation: {relative_urdf_path}")
        
    print("[INIT] Spawning virtual 7-DOF KUKA LBR IIWA Arm...")
    base_position = [0, 0, 0]
    base_orientation = p.getQuaternionFromEuler([0, 0, 0])
    
    # Load the verified URDF asset
    robot_id = p.loadURDF(relative_urdf_path, base_position, base_orientation, useFixedBase=True)
    
    num_joints = p.getNumJoints(robot_id)
    print(f"[METRICS] Robot successfully instantiated with {num_joints} active joints/links.")
    
    return physics_client, robot_id

def inspect_joint_states(robot_id):
    """Queries the simulator to read the active degree-of-freedom mapping."""
    print("\n[INSPECTION] Reading live joint status maps:")
    for i in range(p.getNumJoints(robot_id)):
        joint_info = p.getJointInfo(robot_id, i)
        joint_name = joint_info[1].decode('utf-8')
        joint_type = joint_info[2]
        
        # Joint types: 0=Revolute, 1=Prismatic, 4=Fixed
        type_str = "Revolute" if joint_type == 0 else "Fixed" if joint_type == 4 else "Other"
        print(f"  -> Joint Index {i}: Name = {joint_name} | Type = {type_str}")

if __name__ == "__main__":
    print("--- Big-Ben V2: Sim2Sim Foundation Layer ---")
    try:
        client, robot = initialize_validation_space()
        inspect_joint_states(robot)
        p.stepSimulation()
        print("\n[STATUS] Base simulation layer initialized successfully.")
    except Exception as e:
        print(f"\n[CRITICAL FAILURE] {e}")
    finally:
        p.disconnect()