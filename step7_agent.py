import re
from big_ben_tool import check_spatial_fit

print("--- Big-Ben Neuro-Symbolic Agent ---")
print("Initializing Semantic-to-Spatial Bridge...\n")

def simulate_llm_parsing(user_prompt):
    """
    This simulates what an LLM (like GPT-4 or Gemini) does under the hood 
    when you use 'Function Calling'. It parses English into code arguments.
    """
    print(f"USER: \"{user_prompt}\"")
    print("LLM: Thinking... extracting spatial parameters from text...")
    
    # Simulating the LLM extracting the rotation degree using regex
    rotation_match = re.search(r'rotate it (\d+) degrees', user_prompt.lower())
    rotation = int(rotation_match.group(1)) if rotation_match else 0
    
    # Simulating the LLM knowing the current environment constraints
    # (In a real app, the LLM would read this from the robot's camera payload)
    slot_x = [-2.5, 1.5]
    slot_y = [-0.5, 1.5]
    slot_z = [-0.5, 0.5]
    
    print(f"LLM: Calling Big-Ben API -> check_spatial_fit(my_part.obj, rotation={rotation})")
    spatial_result = check_spatial_fit('l_block.obj', rotation, slot_x, slot_y, slot_z)
    
    # 2. The LLM translates the math output back into human language
    print("\nLLM RESPONSE:")
    if spatial_result.get("status") == "SUCCESS":
        print(f"I ran the spatial simulation. If you rotate the object {rotation} degrees, it fits perfectly within the slot without any collisions.")
    else:
        print(f"I ran the spatial simulation. I cannot recommend rotating it {rotation} degrees because the object will collide with the boundaries.")
    print("-" * 50)

# Run two natural language tests
simulate_llm_parsing("Can you check if the object fits if we don't rotate it at all?")
simulate_llm_parsing("What happens if I rotate it 90 degrees? Will it fit in the slot?")