import os
import time
from google import genai
from dotenv import load_dotenv

# Load local environment security variables
load_dotenv()

def run_blueprint_generator():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY missing.")
        return

    # Initialize client targeting our active workspace configuration
    client = genai.Client(api_key=api_key)

    sample_job_posting = """
    Job Title: Operations & Logistics Assistant
    Salary: $55,000 / year
    Responsibilities:
    - Manually monitoring incoming transport schedules and updating internal Excel sheets.
    - Answering customer inquiry emails regarding arrival windows and delivery statuses.
    - Sorting and archiving scanned delivery tickets and digital receipts into appropriate shared folders daily.
    - Compiling weekly productivity numbers and copy-pasting them into email reports for senior management.
    """

    blueprint_prompt = f"""
    You are an expert AI Operations Architect specializing in B2B corporate efficiency automation.
    Analyze the following job description text and extract a precise, high-value consulting proposal blueprint.
    
    Format the response cleanly with the following sections using clear Markdown:
    
    ### ⏱️ 1. Core Heavy-Lifting Tasks
    (Identify the computer tasks eating up 80% of this seat's active work week)
    
    ### ⚡ 2. Automated Pipeline Solution Architecture
    (Provide a concrete explanation of how a script using Python, APIs, and LLMs can replace each task end-to-end)
    
    ### 💰 3. Financial Metrics & ROI Profile
    (Calculate the approximate financial savings if the employer chooses a one-time software setup fee instead of a $55,000 continuous annual base salary, factoring in estimated payroll taxes and benefits overhead)
    
    Job Post to Audit:
    {sample_job_posting}
    """

    # 🔄 Robust Retry / Backoff Strategy Configuration
    max_retries = 4
    delay = 3 # Start with a 3-second delay
    response = None

    print("📁 Processing Live Indeed Job Listing Requirements...")
    print("-" * 60)
    print(sample_job_posting.strip())
    print("-" * 60)

    for attempt in range(max_retries):
        try:
            print(f"🧠 Compiling Strategy & Financial ROI Metrics (Attempt {attempt + 1}/{max_retries})...")
            
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=blueprint_prompt,
            )
            # Break the loop if successful
            break
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                if attempt < max_retries - 1:
                    print(f"⚠️ Server busy (503). Pausing {delay} seconds before automatic retry...")
                    time.sleep(delay)
                    delay *= 2 # Double the wait time for the next attempt
                else:
                    print("❌ Max retries reached. Google's public servers are heavily congested right now.")
                    print("💡 Tip: Running this in a paid API account instantly clears this hurdle.")
                    return
            else:
                print(f"❌ Blueprint Pipeline Exception: {str(e)}")
                return

    if response:
        print("\n📈 Commercial Proposal Document Generated Successfully:")
        print("=" * 60)
        print(response.text.strip())
        print("=" * 60)
        
        # Save the consulting template automatically to a local document file
        with open("client_pitch_blueprint.md", "w", encoding="utf-8") as f:
            f.write(response.text.strip())
            
        print("\n📁 Sales presentation asset successfully archived to 'client_pitch_blueprint.md'")

if __name__ == "__main__":
    run_blueprint_generator()
