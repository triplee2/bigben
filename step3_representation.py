import trimesh
import numpy as np
import torch
from e3nn import o3

print("--- Data Generation ---")
# 1. Generate the L-Block
leg1 = trimesh.creation.box(extents=[1, 2, 1])
leg1.apply_translation([0, 1, 0])
leg2 = trimesh.creation.box(extents=[2, 1, 1])
leg2.apply_translation([0.5, 0, 0])
l_block = trimesh.util.concatenate([leg1, leg2])

# Extract the normals (the directional vectors of the surfaces)
normals = np.array(l_block.vertex_normals)

print("--- Layer 2: SPHC Representation (SO3KRATES) ---")
# 2. Convert the raw numpy data into PyTorch Tensors
normals_tensor = torch.tensor(normals, dtype=torch.float32)

# 3. Define the Spherical Harmonics we want to use.
# l=0 (invariant scalar), l=1 (3D vector), l=2 (5D complex geometry)
# This combined representation gives us a 9-dimensional vector (1 + 3 + 5 = 9)
l_degrees = o3.Irreps("1x0e + 1x1o + 1x2e")

# 4. The Magic: Encode the 3D normals into SPHCs
sphc_tensor = o3.spherical_harmonics(
    l_degrees, 
    normals_tensor, 
    normalize=True, 
    normalization='integral'
)

print(f"Original Data Shape: {normals_tensor.shape} -> (16 corners, 3 dimensions [x,y,z])")
print(f"SPHC Encoded Shape:  {sphc_tensor.shape} -> (16 corners, 9 dimensions [Spherical Harmonics])")
print("-" * 40)
print("Here is the SPHC Vector for the first corner:")
print(sphc_tensor[0])