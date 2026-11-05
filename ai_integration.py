import os
from google import genai
from dotenv import load_dotenv

# 1. Load local environment security variables
load_dotenv()

def generate_ai_response():
    # Retrieve the API Key from your local environment layer
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in your environment.")
        print("Please ensure your .env file is saved properly in this folder.")
        return

    print("⚡ Connecting to the AI Engine pipeline...")
    
    # 2. Initialize the GenAI client with your secured key
    client = genai.Client(api_key=api_key)
    
    # 3. Gather user prompt input straight from the terminal interface
    user_prompt = input("\n💬 Enter a prompt for the AI: ")
    
    print("\n🧠 Thinking...")
    print("-" * 50)
    
    try:
        # 4. Target the required gemini-3.8-flash endpoint
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=user_prompt,
        )
        
        # 5. Stream the output safely back to your terminal window
        print("✨ AI Response:")
        print(response.text)
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("-" * 50)

if __name__ == "__main__":
    generate_ai_response()
