import trimesh

print("Generating a complex 3D mesh...")
# Create a high-density sphere with hundreds of vertices
mesh = trimesh.creation.icosphere(subdivisions=3, radius=1.5)

# Save it directly to your codespace as an .obj file
mesh.export('my_part.obj')

print(f"Success! 'my_part.obj' created with {len(mesh.vertices)} vertices.")