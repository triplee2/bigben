import os
# CRITICAL HEADLESS FIX: Force MuJoCo to use the CPU software renderer
os.environ['MUJOCO_GL'] = 'osmesa'

import random
import numpy as np
import mujoco
from PIL import Image

def run_procedural_molmo_step():
# ... (the rest of your code stays exactly the same)
import os
import random
import numpy as np
import mujoco
from PIL import Image

def run_procedural_molmo_step():
    print("=== BIG-BEN V3: MOLMOSPACES PROCEDURAL CORE ===")

    # 1. RANDOMIZE THE TARGET ENVIRONMENT
    target_x = round(random.uniform(0.3, 0.6), 3)
    target_y = round(random.uniform(-0.2, 0.2), 3)
    target_z = round(random.uniform(0.1, 0.4), 3)
    
    print(f"[PROCEDURAL] Generating randomized scene topology:")
    print(f"  -> Target Intended Setpoints: X={target_x}, Y={target_y}, Z={target_z}")

    # 2. DEFINE NATIVE MUJOCO GEOMETRY TREE (MJCF)
    mjcf_template = f"""
    <mujoco model="molmo_procedural_workspace">
        <visual>
            <global offwidth="640" offheight="480"/>
        </visual>
        <worldbody>
            <light directional="true" pos="0 0 3" dir="0 0 -1"/>
            
            <camera name="proof_cam" pos="1.0 0.5 0.8" mode="targetbody" target="target_block"/>
            
            <geom name="floor" type="plane" size="1 1 0.1" rgba="0.2 0.2 0.2 1"/>
            
            <body name="target_block" pos="{target_x} {target_y} {target_z}">
                <geom type="box" size="0.05 0.05 0.05" rgba="0.8 0.2 0.2 1"/>
            </body>
            
            <body name="robot_effector" pos="0.0 0.0 0.5">
                <geom type="sphere" size="0.03" rgba="0.2 0.8 0.2 1"/>
            </body>
        </worldbody>
    </mujoco>
    """

    # 3. COMPILE AND BOOT THE REAL PHYSICS STATE
    model = mujoco.MjModel.from_xml_string(mjcf_template)
    data = mujoco.MjData(model)

    mujoco.mj_step(model, data)
    print("[PHYSICS] Engine memory-mapped and stepped forward once.")

    # 4. QUERY PHYSICAL STATE FROM ENGINE MATRICES
    block_body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "target_block")
    effector_body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "robot_effector")
    
    actual_block_pos = data.xpos[block_body_id]
    actual_effector_pos = data.xpos[effector_body_id]
    
    dx = actual_block_pos[0] - actual_effector_pos[0]
    dy = actual_block_pos[1] - actual_effector_pos[1]
    dz = actual_block_pos[2] - actual_effector_pos[2]

    print("\n" + "="*50)
    print("MOLMOSPACES PIPELINE READOUT")
    print("="*50)
    print(f"Required Control Translation Velocities to hit variable target:")
    print(f"  -> X-Drive Command: {dx:+.4f} m/s")
    print(f"  -> Y-Drive Command: {dy:+.4f} m/s")
    print(f"  -> Z-Drive Command: {dz:+.4f} m/s")
    print("="*50)

    # 5. VISUAL PROOF: RENDER THE HEADLESS ENGINE TO DISK
    print("\n[VISUALIZER] Booting MuJoCo Headless Renderer...")
    try:
        renderer = mujoco.Renderer(model, height=480, width=640)
        renderer.update_scene(data, camera="proof_cam")
        pixels = renderer.render()
        
        img = Image.fromarray(pixels)
        img_path = "world_proof.png"
        img.save(img_path)
        print(f"📸 VISUAL PROOF SAVED: Open '{img_path}' in your Codespace file explorer.")
    except Exception as e:
        print(f"[VISUALIZER ERROR] Could not render image: {e}")

if __name__ == "__main__":
    run_procedural_molmo_step()