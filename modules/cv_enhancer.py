import os
from utils.gemini_api import ask_gemini
from PyPDF2 import PdfReader
from utils.cv_pdf_formatter import format_cv_to_pdf

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return text.strip()
    except Exception as e:
        return f"❌ Error reading PDF file: {str(e)}"

def enhance_cv():
    print("\n🧠 CV Enhancer Module is running...")

    cv_path = input("📄 Enter CV file path (PDF or TXT):\n> ").strip()

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
This is the current CV content:
---
{cv_content}
---
Please rewrite and enhance this CV to make it more professional, clean, and effective.
"""

    print("\n🔍 Sending CV to Gemini for enhancement...")
    result = ask_gemini(prompt)

    print("\n📄 Preview:")
    print(result[:1000] + "\n...\n✅ Processed.")

    choice = input("\n💾 Choose output format: [1] TXT or [2] PDF:\n> ").strip()

    os.makedirs("outputs", exist_ok=True)
    if choice == "2":
        format_cv_to_pdf(result)
    else:
        with open("outputs/enhanced_cv.txt", "w", encoding="utf-8") as f:
            f.write(result)
        print("✅ Enhanced CV saved as TXT at: outputs/enhanced_cv.txt")
