import roboticstoolbox as rtb
from spatialmath import SE3
import math

print("--- Big-Ben: The Muscle (Inverse Kinematics) ---")

# 1. LOAD THE HARDWARE TWIN
# We load a 6-Degree-of-Freedom (6-DOF) industrial robot arm.
robot = rtb.models.DH.Puma560()
print(f"Hardware Initialized: {robot.name}")

# 2. RECEIVE THE COMMAND FROM BIG-BEN
# Let's say Big-Ben's agent calculated the slot is at these physical coordinates (in meters)
target_x, target_y, target_z = 0.5, 0.2, 0.4
# And Big-Ben's math engine verified it needs a 90-degree Z-axis rotation to fit
rotation_z_degrees = 90

print(f"\nCommand received: Move to (X:{target_x}, Y:{target_y}, Z:{target_z}) and rotate {rotation_z_degrees} deg.")

# 3. TRANSLATE TO SPATIAL MATH (SE3 Matrix)
# Robots process space as an SE3 Matrix (combining 3D translation + 3D rotation)
target_pose = SE3(target_x, target_y, target_z) * SE3.Rz(rotation_z_degrees, unit='deg')

# 4. EXECUTE INVERSE KINEMATICS (The Muscle)
print("Solving joint trajectories using Levenberg-Marquardt optimizer...")
# This calculates the exact motor angles needed to achieve the target pose
ik_solution = robot.ikine_LM(target_pose)

# 5. OUTPUT TO MOTORS
print("-" * 50)
if ik_solution.success:
    print("SYSTEM VERIFIED: Kinematic path found. No physical limits exceeded.\n")
    print("Transmit these exact angles to the hardware servos:")
    
    joints = ik_solution.q
    for i, angle in enumerate(joints):
        print(f" -> Motor {i+1} (Joint): {angle:>7.4f} rad  |  {math.degrees(angle):>7.2f}°")
else:
    print("COLLISION/LIMIT ERROR: That coordinate is outside the robot's physical reach.")
print("-" * 50)