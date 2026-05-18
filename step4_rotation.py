import trimesh
import numpy as np
import torch
import math
from e3nn import o3

print("--- Recalculating Layer 2 (Representation) ---")
leg1 = trimesh.creation.box(extents=[1, 2, 1])
leg1.apply_translation([0, 1, 0])
leg2 = trimesh.creation.box(extents=[2, 1, 1])
leg2.apply_translation([0.5, 0, 0])
l_block = trimesh.util.concatenate([leg1, leg2])

normals_tensor = torch.tensor(l_block.vertex_normals, dtype=torch.float32)
l_degrees = o3.Irreps("1x0e + 1x1o + 1x2e")
sphc_tensor = o3.spherical_harmonics(l_degrees, normals_tensor, normalize=True, normalization='integral')

print("--- Layer 3: Mental Rotation (Wigner-D) ---")
# 1. Define a 90-degree rotation (in radians).
# e3nn uses ZYZ Euler angles. We will rotate 90 degrees (pi/2) around the Y axis.
alpha = torch.tensor(0.0)
beta = torch.tensor(math.pi / 2.0)
gamma = torch.tensor(0.0)

# 2. Generate the Wigner-D Matrix for our specific SPHC representation.
# This matrix is the "operator". It knows exactly how to rotate our 9-dimensional geometry.
wigner_D_matrix = l_degrees.D_from_angles(alpha, beta, gamma)

print(f"Wigner-D Matrix Shape: {wigner_D_matrix.shape} -> (9x9 operator)")

# 3. Execute the Mental Rotation in Latent Space
# We simply multiply our SPHC tensor by the Wigner-D matrix. No 3D engine required.
mentally_rotated_sphc = sphc_tensor @ wigner_D_matrix.T

print("\nSuccess! The AI has mentally rotated the object 90 degrees.")
print("-" * 50)
print("Original SPHC (First Corner):")
print(torch.round(sphc_tensor[0], decimals=4))
print("\nMentally Rotated SPHC (First Corner):")
print(torch.round(mentally_rotated_sphc[0], decimals=4))