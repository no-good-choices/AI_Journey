import os
import urllib.request
import urllib.parse
from google import genai
from dotenv import load_dotenv

# Load local environment security variables
load_dotenv()

def run_live_scraper():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY missing.")
        return

    client = genai.Client(api_key=api_key)

    print("🌐 === Automated AI Data Scraper Engine ===")
    print("-" * 65)
    
    # 📥 Accept a live URL straight from your terminal cursor
    target_url = input("🔗 Enter a URL to scrape (e.g., https://news.ycombinator.com): ")
    if not target_url.strip():
        # Fallback to an easy-to-scrape tech news site if left blank
        target_url = "https://news.ycombinator.com"
        
    print(f"\n📡 Sending HTTP request to: {target_url}...")
    
    try:
        # Configure a standard browser user-agent header so the website doesn't block the script
        req = urllib.request.Request(
            target_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        
        # Open the connection and read the raw HTML text data
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_html = response.read().decode('utf-8', errors='ignore')
            
        print(f"📥 Successfully scraped {len(raw_html)} characters of raw data.")
        print("🧠 Routing messy raw source text to AI pipeline for structured mining...")
        print("-" * 65)

        # 🚀 truncate raw html if it's too massive for a fast free-tier request token limit
        max_characters = 40000 
        source_text = raw_html[:max_characters]

        mining_prompt = f"""
        You are an expert Data Mining Engineer and Web Scraper Assistant.
        Analyze the following raw HTML source code scraped from {target_url}.
        
        Extract the most useful information (such as articles, headlines, pricing lists, phone numbers, emails, or job postings) depending on what the page contains.
        
        Format your response cleanly in Markdown:
        ### 📊 1. Core Data Entities Found
        (Extract and list the key items, headlines, or business assets found on the page)
        
        ### 🔍 2. High-Value Leads / Insights
        (Identify any contact info, names, pricing structures, or specific data gaps an automation tool could capitalize on)
        
        Source Code to Parse:
        {source_text}
        """

        # Route to high-availability endpoint to bypass global traffic loops
        ai_response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=mining_prompt,
        )
        
        print("\n✨ Structured Data Intel Successfully Extracted:")
        print("=" * 65)
        print(ai_response.text.strip())
        print("=" * 65)
        
        # Automatically save the scraped database metrics locally
        output_filename = "scraped_market_intel.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(ai_response.text.strip())
            
        print(f"\n📁 Scraped market intelligence successfully archived to '{output_filename}'")

    except Exception as e:
        print(f"❌ Scraper Interruption: {str(e)}")
        print("💡 Note: Some sites block direct scripts. Try hitting an open-source blog or forum url!")

if __name__ == "__main__":
    run_live_scraper()
