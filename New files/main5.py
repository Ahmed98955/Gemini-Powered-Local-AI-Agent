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
    while True:
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
        print("5. Exit")
        choice_map = {"1": "enhanced cv", "2": "cover letter", "3": "summary", "4": "proposal"}
        choice = input("Choose an option (1–5): ").strip()
        if choice == "5":
            print("👋 Exiting.")
            return
        if choice not in choice_map:
            print("❌ Invalid choice. Returning to main menu.")
            continue

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

        def generate_output():
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
            return ask_gemini(prompt)

        result = generate_output()

        while True:
            print("\n📄 Preview of result:\n")
            print(result[:1500] + ("...\n" if len(result) > 1500 else ""))

            confirm = input("\n🧾 Is this output ready for final formatting? (y/n): ").lower()
            if confirm == "y":
                break

            print("✍️ Would you like to:")
            print("1. Write changes manually")
            print("2. Attach a TXT or PDF file with updated content")
            print("3. Regenerate result using the same inputs")
            print("4. Return to main menu")
            print("5. Exit")
            correction = input("Choose (1–5): ").strip()

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
            elif correction == "3":
                result = generate_output()
            elif correction == "4":
                continue
            elif correction == "5":
                print("👋 Exiting.")
                return
            else:
                print("❌ Invalid choice. Try again.")

        while True:
            save_format = input("💾 Save as: [1] TXT or [2] PDF\nChoose (1 or 2): ").strip()
            if save_format == "1":
                with open("outputs/final_result.txt", "w", encoding="utf-8") as f:
                    f.write(result)
                print("✅ Saved to outputs/final_result.txt")
            elif save_format == "2":
                format_cv_to_pdf(result)
            else:
                print("❌ Invalid choice. Try again.")
                continue

            again = input("↩️ Do you want to return to the main menu? (y/n): ").lower()
            if again == "y":
                break
            else:
                print("👋 Done. Exiting.")
                return


if __name__ == "__main__":
    main()
