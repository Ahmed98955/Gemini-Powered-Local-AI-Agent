# modules/job_matcher.py
import os
from utils.gemini_api import ask_gemini
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return text.strip()
    except Exception as e:
        return f"❌ Could not read PDF file: {str(e)}"

def match_job_with_cv():
    print("\n🧠 Job Matching Module is now running...")

    cv_path = input("📄 Enter your CV path (PDF or TXT):\n> ").strip()
    job_desc = input("📝 Paste the job description:\n> ").strip()

    if not os.path.exists(cv_path):
        print("❌ File not found. Please check the path.")
        return

    if cv_path.endswith(".pdf"):
        cv_content = extract_text_from_pdf(cv_path)
    else:
        with open(cv_path, "r", encoding="utf-8") as f:
            cv_content = f.read()

    if not cv_content or "❌" in cv_content:
        print(cv_content)
        return

    prompt = f"""
    You have the following CV:
    ---
    {cv_content}
    ---
    And this job description:
    ---
    {job_desc}
    ---
    Is this CV a good fit for the job? Rate the match from 0 to 100, explain why, and suggest improvements.
    """

    print("\n🔍 Processing with Gemini...")
    result = ask_gemini(prompt)
    print("\n📊 Result:")
    print(result)

    save = input("\n💾 Do you want to save the result to a file? (y/n): ").lower()
    if save == "y":
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/job_match_result.txt", "w", encoding="utf-8") as out:
            out.write(result)
        print("✅ Saved to outputs/job_match_result.txt")
