import os
from google import genai
from dotenv import load_dotenv

# Load local environment security variables
load_dotenv()

def run_resume_tailor():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY missing.")
        return

    client = genai.Client(api_key=api_key)

    # 1. Your current practical engineering baseline skill stack
    my_resume_profile = """
    TECHNICAL SKILLS:
    - Python Scripting & Local Engineering Workspace
    - API Integration Pipelines (Google GenAI Core SDK)
    - Structural Environment Security & Masking Management (.env, .gitignore)
    - Source Control Registry Systems (Git, GitHub Repositories)
    - Automated Data Structuring (JSON Modelling, Text Extraction)
    - Operational Network Resilience Engineering (Exponential Backoff, Retry Loops, Error Catching)
    """

    # 2. The live QMC job description requirements we are targeting
    target_job_post = """
    Company: QMC Metering Solutions
    Role: AI Engineer - Intelligent Systems & Analytics
    Core Needs:
    - Transforming large-scale datasets into predictive insights, automation tools, and intelligent workflows.
    - Strong Python experience.
    - Develop scalable data pipelines for processing and structured ingestion.
    - Implement secure backend architectures and monitor system reliability/handling failures.
    - Strong analytical and problem-solving skills to work independently on non-routine challenges.
    """

    print("📋 Engineering live resume alignment for QMC Metering Solutions...")
    print("-" * 65)

    tailor_prompt = f"""
    You are an elite Tech Recruiter specializing in Applied AI Engineering and Automation systems.
    Analyze my local Python workspace skills against the core needs of QMC Metering Solutions.
    
    Compile a high-value resume enhancement blueprint in clean Markdown including:
    
    ### 🎯 1. The Trojan Horse Zoom Hook (Word-for-Word)
    (A 60-second verbal opening pitch tailored for QMC's hiring manager explaining why your local Python pipeline work qualifies you to automate their data flows over textbook applicants)
    
    ### ⚙️ 2. Skill Translation Matrix
    (Translate my local project skills into enterprise corporate keywords that match their listing exactly)
    
    ### 💼 3. High-Impact Portfolio Bullet Points
    (Draft 3 professional, result-oriented bullet points describing the local scripts I just built, framed as high-availability data infrastructure assets)
    
    My Technical Baseline:
    {my_resume_profile}
    
    QMC Requirements:
    {target_job_post}
    """

    try:
        # Route to high-availability endpoint to bypass the 503 traffic queues
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=tailor_prompt,
        )
        
        print("\n📈 QMC Application Strategy Successfully Compiled:")
        print("=" * 65)
        print(response.text.strip())
        print("=" * 65)
        
        output_filename = "qmc_application_brief.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(response.text.strip())
            
        print(f"\n📁 Strategy document archived to: '{output_filename}'")

    except Exception as e:
        print(f"❌ Tailor Pipeline Exception: {str(e)}")

if __name__ == "__main__":
    run_resume_tailor()
