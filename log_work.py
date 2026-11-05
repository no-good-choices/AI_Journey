import datetime
import os

def create_proof_of_work_log(automated_project=None, automated_learnings=None, automated_struggles=None):
    # 1. Set up the file name for your portfolio
    log_file = "AI_INDUSTRY_PROOF_OF_WORK.md"
    
    print("📝 AI Industry Proof of Work Logger Initialized...")
    print("-" * 50)
    
    # 2. Gather inputs (Use automated data if passed from another script, otherwise ask the user via terminal)
    project_name = automated_project if automated_project else input("🚀 Project Name -> What project or skill did you work on today?: ")
    key_learnings = automated_learnings if automated_learnings else input("🧠 Key Learnings -> What is the main takeaway or technical concept you learned?: ")
    struggles_fixed = automated_struggles if automated_struggles else input("🛠️ Struggles Fixed -> What broke, and how did you use AI to help you fix it?: ")
    
    github_commit_msg = input("💻 Github Commit Message -> Summarize this session in 5 words or less for your log header: ")
    
    # 3. Set the current timestamp
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 4. Format the entry beautifully into Markdown syntax
    markdown_entry = f"""
## Session: [{current_date}] | ({github_commit_msg})
*   **Core Focus:** {project_name}
*   **Technical Stacking:** {key_learnings}
*   **Problem Solving & AI Collaboration:** {struggles_fixed}
"""
    
    # 5. Check if the file exists. If not, write a professional header first.
    file_exists = os.path.exists(log_file)
    
    with open(log_file, "a", encoding="utf-8") as file:
        if not file_exists:
            file.write("# 📓 My AI Industry Journey & Proof of Work\n")
            file.write("This file serves as a live ledger of my skill-stacking, code development, and engineering journey.\n")
            
        # Append the new entry
        file.write(markdown_entry)
        
    print("-" * 50)
    print(f"🎉 Success! Your proof of work has been logged inside: '{log_file}'")
    print("📂 Next step: Push this file to GitHub to build your green contribution streak!")

if __name__ == "__main__":
    create_proof_of_work_log()
