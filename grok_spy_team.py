import os
from google import genai
from dotenv import load_dotenv

# Load local environment security variables
load_dotenv()

def run_spy_bot():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY missing.")
        return

    client = genai.Client(api_key=api_key)

    print("🕵️‍♂️ Bot 1 & 2 Active: Scraping outlier data and customer anxieties...")
    print("-" * 65)

    # Simulated raw data scraped from competitor comments and industry complaints
    scraped_market_data = """
    [Competitor Post Outlier - 500k views]: "Most companies are losing $10k a month letting their staff manually clean spreadsheets. Here is the 3-line python script we use to automate it."
    [Customer Complaint 1]: "We tried hiring a data entry clerk on Upwork but they keep making typos in the phone numbers and our CRM is a total mess now."
    [Customer Complaint 2]: "I looked at setting up Zapier to fix our intake forms but the monthly task fees are getting insanely expensive and it keeps breaking on large text paragraphs."
    """

    spy_prompt = f"""
    You are a specialized AI Research Agent analyzing high-performing social hooks and consumer pain points.
    Analyze the following scraped market text:
    
    {scraped_market_data}
    
    Extract and compile an algorithmic content brief in clean Markdown:
    
    ### ⚡ 1. The Psychological Trigger
    (Isolate why the outlier post went viral and break down its opening line hook structure)
    
    ### 🧠 2. The 2 AM Buyer Anxiety
    (Identify the exact, raw business frustrations and cost complaints mentioned by the buyers)
    
    ### 📝 3. High-Value "Bookmark Bribe" Draft
    (Write a 280-character post draft engineered for X. It must start with a broad hook to trigger 2-minute dwell time, pivot immediately to solving the messy data/Zapier cost bottleneck, and instruct them to bookmark it for their team)
    """

    try:
        # Route to high-availability endpoint
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=spy_prompt,
        )
        
        print("\n📈 Algorithmic Content Strategy Compiled by Spy Team:")
        print("=" * 65)
        print(response.text.strip())
        print("=" * 65)
        
        output_filename = "spy_team_brief.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(response.text.strip())
            
        print(f"\n📁 Content brief successfully archived to: '{output_filename}'")

    except Exception as e:
        print(f"❌ Spy Bot Interruption: {str(e)}")

if __name__ == "__main__":
    run_spy_bot()
