import os
import json
from google import genai
from dotenv import load_dotenv

# Load local environment security variables
load_dotenv()

def run_commercial_pipeline():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY missing.")
        return

    # Initialize client to target our standard operational model
    client = genai.Client(api_key=api_key)

    # 1. Simulate a messy, unformatted incoming customer inquiry or intake form
    raw_unstructured_data = """
    Hey, my name is Marcus Vance. I need an intake scheduled for my roof damage. 
    My house is at 1042 Maple Street, Austin TX. Best number to reach me is 512-555-0192. 
    A huge branch fell on the north side during the storm last night and water is leaking in. 
    I'm free for a technician to look at it anytime this Friday morning. Priority level is high.
    """

    print("🚀 Simulated Employee Action: Receiving raw inbound intake phone call notes...")
    print("-" * 50)
    print(raw_unstructured_data.strip())
    print("-" * 50)

    # 2. Engineer a strict, production-ready system instruction for Structured Data extraction
    commercial_prompt = f"""
    You are an automated AI Data Entry and Intake worker. 
    Analyze the following raw customer text and extract the data into a strict JSON format.
    
    Target JSON Structure keys:
    - customer_name
    - phone_number
    - property_address
    - issue_description
    - urgency_level (Low, Medium, High)
    - preferred_appointment_window

    Only return the raw JSON object. Do not wrap it in markdown block characters.
    
    Data to process:
    {raw_unstructured_data}
    """

    print("\n⚡ Processing data via AI Pipeline (Replacing 20 minutes of manual data entry)...")
    
    try:
        # Targeting the stable gemini-3.5-flash pipeline
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=commercial_prompt,
        )
        
        print("\n✨ Structured Database Output Generated in 2 Seconds:")
        print("-" * 50)
        
        # Parse output to ensure clean terminal printing
        clean_json = response.text.strip()
        print(clean_json)
        print("-" * 50)
        
        # Save output straight to a clean data file for database ingestion simulation
        with open("clean_intake_database.json", "w", encoding="utf-8") as f:
            f.write(clean_json)
            
        print("📁 Output automatically synced to CRM/Database simulation layer: 'clean_intake_database.json'")

    except Exception as e:
        print(f"❌ Pipeline Traffic Congestion: {str(e)}")

if __name__ == "__main__":
    run_commercial_pipeline()
