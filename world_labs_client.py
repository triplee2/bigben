import os
import random
import time
import trimesh

class WorldLabsMockClient:
    """
    Simulates the exact architecture of World Labs' Marble-1.1 Text-to-World API.
    Enforces asynchronous orchestration, polling loops, and multi-mesh collider asset delivery.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("WORLD_LABS_API_KEY", "mock_key_12345")
        
    def generate_world_async(self, text_prompt: str) -> str:
        """Simulates initiating a text-to-world generation job on remote servers."""
        print(f"[WORLD_LABS] Dispatching text payload to generative network...")
        print(f"  -> Prompt: '{text_prompt}'")
        # Generate a unique job identifier
        job_id = f"job_marble_{random.randint(100000, 999999)}"
        print(f"[WORLD_LABS] Job accepted. Tracking ID: {job_id}")
        return job_id

    def poll_job_status(self, job_id: str, max_retries: int = 3) -> dict:
        """Simulates polling the API until the 3D generation is cooked and ready."""
        print("[WORLD_LABS] Polling remote compute status...")
        for i in range(1, max_retries + 1):
            time.sleep(0.5) # Simulate processing delay
            print(f"  -> Progress Check {i}/{max_retries}: STATUS = RUNNING (Cooking NerF/Splat meshes)")
            
        print(f"[WORLD_LABS] Job {job_id} COMPLETE. Generating download signatures...")
        
        # Build a dynamic world state to completely destroy hardcoding
        # The slot location and block dimensions change every single time this is triggered
        dynamic_scene_metadata = {
            "slot_width": random.uniform(0.3, 0.6),   # Meters
            "slot_length": random.uniform(0.7, 1.2),  # Meters
            "slot_center_x": random.uniform(0.4, 0.8), # Placement relative to robot base
            "slot_center_y": random.uniform(-0.3, 0.3)
        }
        return dynamic_scene_metadata

    def bake_and_download_collider_mesh(self, metadata: dict, output_filename: str = "world_collider.obj") -> str:
        """
        Takes the generative metadata and creates a real 3D mesh asset.
        This provides a true geometric file to feed into PyBullet.
        """
        print(f"[WORLD_LABS] Streaming generated geometric assets down to workspace...")
        
        # 1. Create a dynamic workbench table mesh
        table = trimesh.creation.box(extents=[1.5, 1.5, 0.4])
        table.apply_translation([0.5, 0, -0.2]) # Put it in front of the robot
        
        # 2. Create the target container box based on the random metadata
        w = metadata["slot_width"]
        l = metadata["slot_length"]
        container = trimesh.creation.box(extents=[w, l, 0.3])
        container.apply_translation([metadata["slot_center_x"], metadata["slot_center_y"], 0.15])
        
        # Merge geometries into a single environment scene
        world_scene = trimesh.util.concatenate([table, container])
        
        # Export as a hard physical file in the workspace
        world_scene.export(output_filename)
        print(f"[WORLD_LABS] 3D Asset stored locally: '{output_filename}' ({len(world_scene.vertices)} vertices)")
        return output_filename

if __name__ == "__main__":
    print("--- Big-Ben V2: World Labs Generative Handler ---")
    
    client = WorldLabsMockClient()
    
    # Trigger the pipeline with a prompt
    prompt = "A heavy metal fabrication workbench with a rectangular parts bin offset to the right"
    job = client.generate_world_async(prompt)
    scene_data = client.poll_job_status(job)
    mesh_path = client.bake_and_download_collider_mesh(scene_data)
    
    print("\n[STATUS] Generative mesh handler executed cleanly.")