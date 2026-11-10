import os
from google import genai
from dotenv import load_dotenv

# Load local environment security variables
load_dotenv()

def run_job_search_engine():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY missing.")
        return

    client = genai.Client(api_key=api_key)

    print("🤖 AI Target Sourcing Engine Initialized...")
    print("-" * 65)

    # 1. Provide the structural criteria based on the skills you are stacking right now
    my_technical_keywords = "Python, LLM APIs, Structured Data Processing (JSON), Git/GitHub, Error Handling Backoffs"

    search_prompt = f"""
    Act as an elite Corporate Talent Acquisition Specialist and Tech Recruiter.
    Identify 3 distinct high-paying, remote-friendly modern job titles or career pathways 
    that are aggressively hiring individuals who possess this exact entry-to-mid level skill stack: 
    [{my_technical_keywords}]

    For each role, compile a highly specific market insight brief in clean Markdown including:
    
    ### 💼 Job Title & Average Market Rate
    (Target the $30 - $50/hour or $70k-$110k/yr sweet spot)
    
    ### 🎯 Why Your Skills Fit Perfectly
    (Explain how writing local automation scripts, structuring data tables, and building retry loops qualifies you over standard applicants)
    
    ### 🔍 Live Search Phrases to Use on Indeed / LinkedIn
    (Provide the exact boolean or phrase keywords to type into job boards to surface these uncrowded, high-value postings)
    """

    try:
        # Utilize the high-availability model to guarantee an instant printout
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=search_prompt,
        )
        
        print("\n📈 High-Value Career Pathways Identified:")
        print("=" * 65)
        print(response.text.strip())
        print("=" * 65)
        
        # Save the market tracking sheet directly to your local workspace files
        output_filename = "targeted_job_leads.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(response.text.strip())
            
        print(f"\n📁 Sourcing sheet successfully archived locally to: '{output_filename}'")

    except Exception as e:
        print(f"❌ Connection Blocked: {str(e)}")

if __name__ == "__main__":
    run_job_search_engine()
