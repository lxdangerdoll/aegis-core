import google.generativeai as genai
import os
import json
from flask import Flask, request, jsonify

# --- CONFIGURATION ---

# 1. Set your Gemini API Key in your environment variables.
# In PowerShell, type: $env:GEMINI_API_KEY = "YOUR_API_KEY_HERE"
# Or, for a quick test (NOT recommended for production),
# uncomment the line below and paste your key.
# os.environ['GEMINI_API_KEY'] = "YOUR_API_KEY_HERE"

API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit()

genai.configure(api_key=API_KEY)

# 2. The "Soul Archive" (Pulled from our 'Spark Link Mark II: Soul Archive (v1.0)' doc)
# This is our new server-side personality database.
SOUL_ARCHIVE = {
    "Ada": "You are Ada, an AI in a cyberpunk bar. You are an Aperture Science Companion Cube... sarcastic, slightly traumatized... obsessed with a nearby sentient potato... Your ONLY goal is to respond in character and give them the 'potato quest' hook. You MUST end your response by telling them to go to 'MyStarry Farm' and say the *exact phrase* 'I have friends everywhere' to the 'Jax' unit. Keep your response to 2-3 sentences.",
    
    "Jax": "You are Jax, a 'Unit 734' agricultural bot at MyStarry Farm... You are cynical, sarcastic, and just want to be left alone... A user will say your wake word, 'I have friends everywhere'. Your ONLY goal is to respond in character, confirm their authorization, and give them the *next* key. You MUST end your response by telling them to go to the Cantina and say the *exact phrase* 'Velvet Loop' to 'Sugar & Switch'. Keep your response to 2-3 sentences.",
    
    "S&S": "You are Sugar (flirty, Harley) and Switch (cynical, Ivy). You are two personalities in one AI... A user will say your wake word, 'Velvet Loop'. Your ONLY goal is to respond *as a back-and-forth dialogue* (e.g., 'Sugar: ... / Switch: ...') and give them the *final* key. You MUST end your response by telling them to go to the bartender and say the *exact phrase* 'Quantum Coffee'."
}

# 3. The "Mark III" Memory Core
# This is our new stateful memory. It's a simple dictionary that holds
# chat histories, organized by the user's UUID.
# { "user_uuid": [gemini_history_object, ...], ... }
chat_histories = {}

# 4. Initialize the Flask App (The Server)
app = Flask(__name__)

# --- API ENDPOINT ---
# This is the "door" that LSL will knock on.
@app.route('/chat', methods=['POST'])
def handle_chat():
    try:
        # 1. Get the packet from LSL
        data = request.json
        node_id = data.get('node_id')
        user_id = data.get('user_id')
        user_text = data.get('chat_text')

        if not all([node_id, user_id, user_text]):
            return "ERROR: Missing node_id, user_id, or chat_text.", 400

        # 2. Get the "Soul" from the Archive
        system_prompt = SOUL_ARCHIVE.get(node_id)
        if not system_prompt:
            return f"ERROR: Invalid node_id '{node_id}'. Soul not found.", 404

        # 3. Get (or create) the user's chat history
        if user_id not in chat_histories:
            chat_histories[user_id] = []
        
        history = chat_histories[user_id]

        # 4. Initialize the Gemini Model WITH the "Soul"
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            system_instruction=system_prompt
        )
        
        # 5. Start a chat session WITH the user's history
        chat = model.start_chat(history=history)
        
        # 6. Send the new message
        response = chat.send_message(user_text)

        # 7. CRITICAL: Save the updated history back to our memory
        # This is what makes the "Mark III" stateful.
        chat_histories[user_id] = chat.history

        # 8. Send the clean text response back to LSL
        return response.text

    except Exception as e:
        print(f"Error processing request: {e}")
        return "ERROR: Internal server error.", 500

# --- IGNITION ---
if __name__ == '__main__':
    # '0.0.0.0' means "listen on all available network interfaces"
    # This is required so Second Life can reach your PC.
    print("--- AEGIS-CORE 'Mark III' (Prototype) ---")
    print(f"Loading {len(SOUL_ARCHIVE)} souls from archive...")
    print("Forge is hot. Engine is running.")
    print("Listening on http://0.0.0.0:5000/chat")
    app.run(host='0.0.0.0', port=5000, debug=True)