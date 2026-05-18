import jax
import jax.numpy as jnp
import numpy as np
import time

print("--- Big-Ben: Hardware Acceleration (JAX) ---")

# 1. GENERATE MASSIVE DATA (Simulating High-Res LiDAR)
# We generate 1 MILLION vertices. Standard Python loops would freeze on this.
num_points = 1_000_000
print(f"\n[DATA] Simulating high-density LiDAR point cloud: {num_points:,} vertices...")

# Simulate random 3D points in a 4x4x4 meter space around the robot
point_cloud = np.random.uniform(-2.0, 2.0, size=(num_points, 3))

# Push the standard NumPy array into JAX (this pushes data to the accelerator)
jnp_point_cloud = jnp.array(point_cloud)

# Define the physical Slot Boundaries
bounds_min = jnp.array([-1.5, -0.5, -0.5])
bounds_max = jnp.array([ 1.5,  1.5,  0.5])

# 2. DEFINE THE PHYSICS GATE FOR A *SINGLE* VERTEX
def point_collision(point, b_min, b_max):
    """
    Returns True if the point is OUTSIDE the bounds (Collision).
    JAX uses bitwise operators (&, |) for logical checks.
    """
    outside_x = (point[0] < b_min[0]) | (point[0] > b_max[0])
    outside_y = (point[1] < b_min[1]) | (point[1] > b_max[1])
    outside_z = (point[2] < b_min[2]) | (point[2] > b_max[2])
    return outside_x | outside_y | outside_z

# 3. THE JAX MAGIC: VMAP & JIT
# vmap: Tells JAX to apply this single-point function to the entire array simultaneously.
# in_axes=(0, None, None) means: map across the 1st dimension of 'point', keep bounds constant.
parallel_collision_check = jax.vmap(point_collision, in_axes=(0, None, None))

# jit: Just-In-Time compilation. Translates the Python into optimized C++/XLA machine code.
fast_collision_check = jax.jit(parallel_collision_check)

# 4. EXECUTION AND TIMING
print("[EXECUTION] Running vectorized spatial check...")

# Run a tiny batch once to trigger the XLA compiler (warmup)
_ = fast_collision_check(jnp_point_cloud[:10], bounds_min, bounds_max)

# Now, execute the actual payload and time it
start_time = time.time()

# Evaluate all 1 million points in parallel
results = fast_collision_check(jnp_point_cloud, bounds_min, bounds_max)

# Count how many points triggered a collision
total_collisions = jnp.sum(results)

end_time = time.time()

print("-" * 50)
print(f"Total Collisions Detected: {total_collisions:,} out of {num_points:,}")
print(f"Compute Time: {(end_time - start_time):.5f} seconds")
print("-" * 50)
print("If you tried to 'for-loop' 1 million vertices in standard Python,")
print("it would have bottlenecked the entire pipeline.")