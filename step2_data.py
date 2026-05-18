import trimesh
import numpy as np

print("Generating 3D L-Block...")

# Create the vertical leg of the 'L'
leg1 = trimesh.creation.box(extents=[1, 2, 1])
leg1.apply_translation([0, 1, 0])

# Create the horizontal leg of the 'L'
leg2 = trimesh.creation.box(extents=[2, 1, 1])
leg2.apply_translation([0.5, 0, 0])

# Concatenate them into a single L-shaped mesh
l_block = trimesh.util.concatenate([leg1, leg2])

print(f"L-Block successfully generated!")
print(f"Total Vertices (Corners): {len(l_block.vertices)}")
print(f"Total Faces (Triangles): {len(l_block.faces)}")
print("-" * 30)

# Extract the geometric ground truth to feed into our neural network
vertices = np.array(l_block.vertices)
normals = np.array(l_block.vertex_normals)

print("Geometry successfully extracted for Layer 2.")
print("Sample Vertex (x, y, z):", vertices[0])
print("Sample Normal (x, y, z):", normals[0])