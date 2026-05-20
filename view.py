import gradio as gr
import trimesh
import numpy as np
from scipy.spatial.transform import Rotation
import os

print("Initializing Big-Ben Web Server...")

# Define the physical constraints of the Slot
SLOT_X = [-2.5, 2.5]
SLOT_Y = [-1.5, 1.5]
SLOT_Z = [-0.5, 0.5]

def evaluate_spatial_topology(rotation_degrees):
    """
    The core Big-Ben math engine. Takes a degree from the web UI, 
    rotates the real mesh, checks the physics, and returns the 3D file and status.
    """
    # 1. Generate the Raw Geometry (L-Block)
    leg1 = trimesh.creation.box(extents=[1, 2, 1])
    leg1.apply_translation([0, 1, 0])
    leg2 = trimesh.creation.box(extents=[2, 1, 1])
    leg2.apply_translation([0.5, 0, 0])
    mesh = trimesh.util.concatenate([leg1, leg2])
    
    # 2. Execute Mental Rotation via Matrix Math
    r = Rotation.from_euler('z', rotation_degrees, degrees=True)
    rotated_vertices = r.apply(mesh.vertices)
    
    # Save the new mental state to a file so the web UI can render it
    rotated_mesh = trimesh.Trimesh(vertices=rotated_vertices, faces=mesh.faces)
    output_file = "latent_state.obj"
    rotated_mesh.export(output_file)
    
    # 3. Execute the Topological Logic Gate (Physics Firewall)
    epsilon = 1e-3
    collision = False
    for v in rotated_vertices:
        if not (SLOT_X[0] - epsilon <= v[0] <= SLOT_X[1] + epsilon and
                SLOT_Y[0] - epsilon <= v[1] <= SLOT_Y[1] + epsilon and
                SLOT_Z[0] - epsilon <= v[2] <= SLOT_Z[1] + epsilon):
            collision = True
            break
            
    # 4. Format the Output
    if collision:
        status = f"❌ COLLISION DETECTED\nRotation: {rotation_degrees}°\nThe object's geometry intersects with the physical boundaries of the slot. Halting execution."
    else:
        status = f"✅ SYSTEM VERIFIED\nRotation: {rotation_degrees}°\nTopology perfectly fits inside the boundaries. Ready to transmit coordinates to Kinematics solver."
        
    return output_file, status

# ==========================================
# FRONTEND UI (Gradio Blocks)
# ==========================================
with gr.Blocks(theme=gr.themes.Monochrome(), title="Big-Ben Spatial AI") as interface:
    gr.Markdown("# 🧠 Big-Ben: Neuro-Symbolic Spatial AI")
    gr.Markdown("**Architecture Showcase:** Adjust the slider to trigger the Wigner-D transformation engine. The backend physics logic gate will evaluate the raw vertices and mathematically verify if the object fits in the Z-axis slot.")
    
    with gr.Row():
        # Left Column: Controls and Readout
        with gr.Column(scale=1):
            rot_slider = gr.Slider(minimum=0, maximum=360, step=15, value=0, label="Z-Axis Mental Rotation (Degrees)")
            execute_btn = gr.Button("Run Spatial Simulation", variant="primary")
            readout = gr.Textbox(label="Big-Ben Output Log", lines=5)
        
        # Right Column: 3D Visualization
        with gr.Column(scale=2):
            model_viewer = gr.Model3D(label="Latent Geometry Viewer", clear_color=[0.1, 0.1, 0.1, 1.0])

    # Wire the button to the Python function
    execute_btn.click(
        fn=evaluate_spatial_topology, 
        inputs=[rot_slider], 
        outputs=[model_viewer, readout]
    )

if __name__ == "__main__":
    # Launch on 0.0.0.0 so GitHub Codespaces can route the port to your browser
    interface.launch(server_name="0.0.0.0", server_port=7860)