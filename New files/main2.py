# main.py

import os
import argparse
from modules.cv_enhancer import enhance_cv
from utils.cv_pdf_formatter import format_cv_to_pdf


def main():
    parser = argparse.ArgumentParser(description="AI Assistant for CV and Job Tools")
    parser.add_argument("--cv_enhancer", action="store_true", help="Enhance and generate CV with options")
    args = parser.parse_args()

    if args.cv_enhancer:
        enhance_cv()


def enhance_cv():
    print("\n🧠 CV Enhancer Module is running...")

    cv_path = input("📄 Enter CV file path (PDF or TXT):\n> ").strip()
    if not os.path.exists(cv_path):
        print("❌ File not found. Exiting.")
        return

    from PyPDF2 import PdfReader
    def extract_text_from_pdf(pdf_path):
        reader = PdfReader(pdf_path)
        return "\n".join([page.extract_text() or "" for page in reader.pages])

    if cv_path.endswith(".pdf"):
        cv_content = extract_text_from_pdf(cv_path)
    else:
        with open(cv_path, "r", encoding="utf-8") as f:
            cv_content = f.read()

    print("\n🔘 What would you like to generate?")
    print("1. Enhanced CV")
    print("2. Cover Letter")
    print("3. Summary")
    print("4. Proposal")
    choice_map = {"1": "enhanced cv", "2": "cover letter", "3": "summary", "4": "proposal"}
    choice = input("Choose an option (1–4): ").strip()
    if choice not in choice_map:
        print("❌ Invalid choice. Exiting.")
        return

    instruction_text = ""
    attach_instructions = input("📎 Do you want to attach a TXT or PDF file with extra instructions? (y/n): ").lower()
    if attach_instructions == "y":
        file_path = input("🔍 Enter path to instruction file: ").strip()
        if os.path.exists(file_path):
            if file_path.endswith(".pdf"):
                instruction_text = extract_text_from_pdf(file_path)
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    instruction_text = f.read()

    from utils.gemini_api import ask_gemini
    prompt = f"""
This is a user's {choice_map[choice]} request.
CV:
---
{cv_content}
---
Additional Instructions:
{instruction_text}
---
Please write the best possible {choice_map[choice]} based on the above.
"""

    print("\n🔍 Sending content to Gemini...\n")
    result = ask_gemini(prompt)

    print("\n📄 Preview of result:\n")
    print(result[:1500] + ("...\n" if len(result) > 1500 else ""))

    confirm = input("\n🧾 Is this output ready for final formatting? (y/n): ").lower()
    if confirm == "n":
        correction = input("✍️ Would you like to (1) write changes manually or (2) attach a file? ").strip()
        if correction == "1":
            print("📝 Type your full revision below, then press Enter twice when done:")
            print("(Hint: use Ctrl+Z then Enter to end input on Windows)")
            print("---------------------------------------------------")
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            result = "\n".join(lines)
        elif correction == "2":
            new_file = input("📎 Enter path to updated TXT or PDF file: ").strip()
            if os.path.exists(new_file):
                if new_file.endswith(".pdf"):
                    result = extract_text_from_pdf(new_file)
                else:
                    with open(new_file, "r", encoding="utf-8") as f:
                        result = f.read()
            else:
                print("❌ File not found. Keeping previous result.")

    with open("outputs/final_result.txt", "w", encoding="utf-8") as f:
        f.write(result)
    print("✅ Saved to outputs/final_result.txt")

    # Generate PDF
    generate_pdf = input("📄 Do you want to generate a formatted PDF? (y/n): ").lower()
    if generate_pdf == "y":
        format_cv_to_pdf(result)


if __name__ == "__main__":
    main()