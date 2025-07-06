import os
import argparse
from modules.cv_enhancer import enhance_cv
from modules.job_matcher import match_job_with_cv  # لو عندك logic إضافي
from utils.cv_pdf_formatter import format_cv_to_pdf

def main():
    parser = argparse.ArgumentParser(description="AI Assistant for CV and Job Tools")
    parser.add_argument("--cv_enhancer", action="store_true", help="Enhance and generate CV with options")
    parser.add_argument("--job_matcher", action="store_true", help="Match CV with a job description")
    args = parser.parse_args()

    if args.cv_enhancer:
        while True:
            enhance_cv()

    elif args.job_matcher:
        while True:
            job_matcher_interactive()

    else:
        print("\n🔘 Choose a module to run:")
        print("--cv_enhancer   → Enhance and generate CV")
        print("--job_matcher   → Match your CV with a job description")
        print("💡 Example: python main.py --cv_enhancer")

def extract_text_from_pdf(pdf_path):
    from PyPDF2 import PdfReader
    reader = PdfReader(pdf_path)
    return "\n".join([page.extract_text() or "" for page in reader.pages])

def job_matcher_interactive():
    print("\n🧠 Job Matcher Module is running...")

    # 1. طلب ملف CV
    while True:
        cv_path = input("📄 Enter CV file path (PDF or TXT):\n> ").strip()
        if not os.path.exists(cv_path):
            print("❌ File not found. Please try again.")
        else:
            break
    if cv_path.endswith(".pdf"):
        cv_content = extract_text_from_pdf(cv_path)
    else:
        with open(cv_path, "r", encoding="utf-8") as f:
            cv_content = f.read()

    while True:
        print("\n🔘 What would you like to do?")
        print("1. Match CV with a job description (paste manually)")
        print("2. Match CV with job description from a file (TXT or PDF)")
        print("3. General CV Assessment (no specific job)")
        print("4. Return to main menu")
        print("5. Exit")
        option = input("Choose (1–5): ").strip()
        if option == "5":
            print("👋 Exiting.")
            exit()
        if option == "4":
            print("↩️ Returning to main menu...")
            return

        job_desc = ""
        if option == "1":
            print("✍️ Paste the job description below. (Ctrl+Z then Enter to finish on Windows)")
            print("---------------------------------------------------")
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            job_desc = "\n".join(lines)
        elif option == "2":
            job_file = input("📄 Enter job description file path (TXT or PDF):\n> ").strip()
            if not os.path.exists(job_file):
                print("❌ File not found. Returning to previous menu.")
                continue
            if job_file.endswith(".pdf"):
                job_desc = extract_text_from_pdf(job_file)
            else:
                with open(job_file, "r", encoding="utf-8") as f:
                    job_desc = f.read()
        elif option == "3":
            job_desc = None
        else:
            print("❌ Invalid choice. Try again.")
            continue

        # تعليمات إضافية
        instruction_text = ""
        print("\n📎 Do you want to add extra instructions?")
        print("1. Write instructions now")
        print("2. Attach a TXT or PDF file")
        print("3. No instructions")
        instruction_choice = input("Choose (1–3): ").strip()

        if instruction_choice == "1":
            print("✍️ Write your instructions below.")
            instruction_text = input("Your instructions: \n> ").strip()
        elif instruction_choice == "2":
            file_path = input("📎 Enter path to instruction file: ").strip()
            if os.path.exists(file_path):
                if file_path.endswith(".pdf"):
                    instruction_text = extract_text_from_pdf(file_path)
                else:
                    with open(file_path, "r", encoding="utf-8") as f:
                        instruction_text = f.read()
        else:
            instruction_text = ""

        # تجهيز البرومبت حسب الاختيار
        from utils.gemini_api import ask_gemini
        if option == "1" or option == "2":
            prompt = f"""
This is a user's CV/job matching request.
CV:
---
{cv_content}
---
Job Description:
---
{job_desc}
---
Additional Instructions:
{instruction_text}
---
Compare the CV and the job description. Highlight strengths, weaknesses, and give actionable recommendations to improve the CV for this job.
"""
        elif option == "3":
            prompt = f"""
This is a general CV assessment request.
CV:
---
{cv_content}
---
Additional Instructions:
{instruction_text}
---
Please provide a detailed, constructive assessment of this CV, including strengths, weaknesses, and recommendations.
"""
        else:
            continue

        print("\n🔍 Sending content to Gemini...\n")
        result = ask_gemini(prompt)

        # مراجعة النتيجة
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
                result = ask_gemini(prompt)
            elif correction == "4":
                print("↩️ Returning to main menu...")
                return
            elif correction == "5":
                print("👋 Exiting.")
                exit()
            else:
                print("❌ Invalid choice. Try again.")
        else:
            continue

        # حفظ النتيجة
        while True:
            save_format = input("💾 Save as: [1] TXT or [2] PDF\nChoose (1 or 2): ").strip()
            if save_format == "1":
                default_path = "outputs/final_jobmatch_result.txt"
                custom_path = input(f"📁 Save path? Press Enter to use default ({default_path}) or type custom path: \n> ").strip()
                path = custom_path if custom_path else default_path
                with open(path, "w", encoding="utf-8") as f:
                    f.write(result)
                print(f"✅ Saved to {path}")
            elif save_format == "2":
                default_pdf = "outputs/final_jobmatch.pdf"
                while True:
                    custom_pdf = input(f"📁 PDF save path? Press Enter to use default ({default_pdf}) or type custom path: \n> ").strip()
                    path = custom_pdf if custom_pdf else default_pdf
                    if os.path.isdir(path):
                        print("❌ Please include a full filename with extension (e.g., D:\\JobMatch.pdf)")
                        continue
                    try:
                        format_cv_to_pdf(result, filename=path)
                        break
                    except Exception as e:
                        print(f"❌ Error saving PDF: {e}")
                        continue
            else:
                print("❌ Invalid choice. Try again.")
                continue

            again = input("↩️ Do you want to return to the main menu? (y/n): ").lower()
            if again == "y":
                break
            else:
                print("👋 Done. Exiting.")
                exit()

if __name__ == "__main__":
    main()