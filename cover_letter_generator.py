import os
from google import genai
from dotenv import load_dotenv

# Load local environment security variables
load_dotenv()

def run_cover_letter_generator():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY missing.")
        return

    client = genai.Client(api_key=api_key)

    print("✉️ === Automated Corporate Cover Letter Builder ===")
    print("-" * 65)
    
    # 📥 Gather live job context straight from your terminal cursor
    target_company = input("🏢 Company Name (e.g., QMC Metering Solutions): ")
    target_role = input("💼 Job Title (e.g., AI Engineer): ")
    
    if not target_company.strip() or not target_role.strip():
        print("❌ Error: Company or Role cannot be blank.")
        return

    # Pull the real technical baseline projects you engineered today
    my_technical_baseline = """
    PROJECT WORK COMPLETED IN WORKSPACE:
    - Built a local workspace pipeline using Python and Google's GenAI Core SDK.
    - Engineered robust local security protocols using masked environment layers (.env, .gitignore).
    - Designed operational network resilience logic handling 503 traffic congestions via exponential backoffs and retry loops.
    - Automated text extraction pipelines converting messy, unstructured paragraph forms into production-ready JSON data models.
    """

    print(f"\n🧠 Compiling tailored asset for {target_company}...")
    print("-" * 65)

    letter_prompt = f"""
    You are an expert executive career writer specializing in the B2B tech and automation sectors.
    Write a highly professional, compelling, and corporate-aligned cover letter for me.
    
    Target Company: {target_company}
    Target Role: {target_role}
    My Technical Baseline Projects:
    {my_technical_baseline}
    
    Structure the output naturally as plain text layout ready for a document editor:
    - Maintain a confident, outcome-oriented, and highly capable tone.
    - Frame my local workspace development work not as 'homework assignments', but as concrete engineering architectures.
    - Highlight my focus on building 'fault-tolerant, resilient data systems' rather than just basic scripts.
    - Explicitly emphasize how my focus on automated structured data parsing directly matches their operational need to process large-scale datasets smoothly.
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=letter_prompt,
        )
        
        print("\n📄 Tailored Corporate Cover Letter Generated:")
        print("=" * 65)
        print(response.text.strip())
        print("=" * 65)
        
        # Save filename using a clean automated string
        clean_company_name = target_company.lower().replace(" ", "_")
        output_filename = f"{clean_company_name}_cover_letter.txt"
        
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(response.text.strip())
            
        print(f"\n📁 Document successfully archived locally to: '{output_filename}'")

    except Exception as e:
        print(f"❌ Generation Pipeline Exception: {str(e)}")

if __name__ == "__main__":
    run_cover_letter_generator()
