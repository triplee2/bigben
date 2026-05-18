import os
import google.generativeai as genai
from big_ben_tool import check_spatial_fit

print("--- Big-Ben: Live LLM Integration ---")

# 1. SECURELY LOAD API KEY
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable not found.")
    print("Run this in terminal: export GEMINI_API_KEY='your_key_here'")
    exit()

genai.configure(api_key=api_key)

# 2. DEFINE THE TOOL FOR THE LLM
# We wrap your Big-Ben engine in a clean function with clear instructions for the AI.
def simulate_rotation(rotation_z_degrees: int) -> dict:
    """
    Simulates rotating an object mathematically and checks if it fits in a physical slot.
    Use this tool whenever the user asks if an object will fit after a rotation.
    
    Args:
        rotation_z_degrees: The exact number of degrees to rotate the object.
    """
    print(f"\n[SYSTEM] LLM invoked Big-Ben Engine -> Testing {rotation_z_degrees} degrees...")
    
    # We provide the environment parameters so the LLM doesn't have to guess them
    slot_x = [-2.5, 1.5]
    slot_y = [-0.5, 1.5]
    slot_z = [-0.5, 0.5]
    
    # Execute the core physics logic you built earlier
    return check_spatial_fit('l_block.obj', rotation_z_degrees, slot_x, slot_y, slot_z)

# 3. INITIALIZE THE NEURAL NETWORK
# We pass the Gemini model your Python function as a usable 'tool'
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    tools=[simulate_rotation]
)

# We enable automatic function calling so the LLM manages the execution loop natively
chat = model.start_chat(enable_automatic_function_calling=True)

# 4. EXECUTE THE TEST
user_prompt = "I have an L-block. If I don't rotate it at all, will it fit in the slot? What if I rotate it 90 degrees?"

print(f"\nUSER: \"{user_prompt}\"")
print("-" * 50)
print("LLM is processing semantic intent and executing spatial tools...")

# Send the message to the live AI
response = chat.send_message(user_prompt)

print("-" * 50)
print("\nLLM FINAL RESPONSE:")
print(response.text)