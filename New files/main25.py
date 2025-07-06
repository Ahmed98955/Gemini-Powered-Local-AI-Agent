import os
import argparse
from utils.cv_pdf_formatter import format_cv_to_pdf

def main():
    parser = argparse.ArgumentParser(description="AI Assistant for CV and Job Tools")
    parser.add_argument("--cv_enhancer", action="store_true", help="Enhance and generate CV with options")
    parser.add_argument("--job_matcher", action="store_true", help="Match CV with a job description (single or multiple jobs, with score & missing skills)")
    args = parser.parse_args()

    if args.cv_enhancer:
        while True:
            enhance_cv()

    elif args.job_matcher:
        while True:
            job_matcher_multi_jobs()

    else:
        print("\n🔘 Choose a module to run:")
        print("--cv_enhancer   → Enhance and generate CV")
        print("--job_matcher   → Match your CV with a job description (single or multiple jobs, with score & missing skills)")
        print("💡 Example: python main.py --job_matcher")



def extract_text_from_pdf(pdf_path):
    from PyPDF2 import PdfReader
    reader = PdfReader(pdf_path)
    return "\n".join([page.extract_text() or "" for page in reader.pages])

def ascii_bar(score, outof=100, width=20):
    """Display a bar of hashes and dashes for the score."""
    filled = int(round(score / outof * width))
    return "[" + "#" * filled + "-" * (width - filled) + f"] {score:.0f}/{outof}"

def extract_score_and_missing_skills(text):
    """
    Tries to extract a score (percentage or X/100) and missing skills (list) from Gemini's response.
    If not found, returns None.
    """
    import re
    score = None
    # Try to find percentage or 'score: 80/100' or 'match: 75%'
    match = re.search(r"(\d{1,3})\s*/\s*100", text)
    if match:
        score = int(match.group(1))
    else:
        match = re.search(r"(\d{1,3})\s*%", text)
        if match:
            score = int(match.group(1))
    # Try to extract missing skills section/list
    missing_skills = []
    ms_match = re.search(r"(Missing Skills|Areas for Improvement|To reach [\d]+/100.*?:|To increase your score.*?:)(.*?)(\n\n|\Z)", text, re.IGNORECASE | re.DOTALL)
    if ms_match:
        # Extract possible bullet points
        ms_block = ms_match.group(2)
        ms_lines = [line.strip("-*• \t") for line in ms_block.strip().splitlines() if line.strip("-*• \t")]
        missing_skills = [line for line in ms_lines if len(line) > 2]
    return score, missing_skills

def job_matcher_multi_jobs():
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
        print("1. Match CV with a single job description")
        print("2. Match CV with multiple job descriptions")
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

        job_descs = []
        job_desc_labels = []
        if option == "1":
            print("\nChoose job description input method:")
            print("1. Paste job description manually")
            print("2. Load from TXT or PDF file")
            job_input = input("Choose (1–2): ").strip()
            if job_input == "1":
                print("✍️ Paste the job description below. (Ctrl+Z then Enter to finish on Windows)")
                print("---------------------------------------------------")
                lines = []
                while True:
                    try:
                        line = input()
                        lines.append(line)
                    except EOFError:
                        break
                job_descs = ["\n".join(lines)]
                job_desc_labels = ["Job 1"]
            else:
                job_file = input("📄 Enter job description file path (TXT or PDF):\n> ").strip()
                if not os.path.exists(job_file):
                    print("❌ File not found. Returning to previous menu.")
                    continue
                if job_file.endswith(".pdf"):
                    job_descs = [extract_text_from_pdf(job_file)]
                else:
                    with open(job_file, "r", encoding="utf-8") as f:
                        job_descs = [f.read()]
                job_desc_labels = [os.path.basename(job_file)]
        elif option == "2":
            print("\nHow many job descriptions do you want to compare?")
            try:
                count = int(input("Number of jobs: ").strip())
            except Exception:
                print("❌ Invalid number. Try again.")
                continue
            for i in range(count):
                print(f"\nJob description #{i+1} input method:")
                print("1. Paste job description manually")
                print("2. Load from TXT or PDF file")
                job_input = input("Choose (1–2): ").strip()
                if job_input == "1":
                    print(f"✍️ Paste the job description for Job #{i+1} below. (Ctrl+Z then Enter to finish)")
                    lines = []
                    while True:
                        try:
                            line = input()
                            lines.append(line)
                        except EOFError:
                            break
                    job_descs.append("\n".join(lines))
                    job_desc_labels.append(f"Job {i+1}")
                else:
                    job_file = input(f"📄 Enter job description file path (TXT or PDF) for Job #{i+1}:\n> ").strip()
                    if not os.path.exists(job_file):
                        print("❌ File not found. Skipping this job.")
                        continue
                    if job_file.endswith(".pdf"):
                        job_descs.append(extract_text_from_pdf(job_file))
                    else:
                        with open(job_file, "r", encoding="utf-8") as f:
                            job_descs.append(f.read())
                    job_desc_labels.append(os.path.basename(job_file))
        elif option == "3":
            job_descs = [None]
            job_desc_labels = ["General CV Assessment"]
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

        # تجهيز البرومبتات وإرسالها لـ Gemini
        from utils.gemini_api import ask_gemini
        results = []
        for idx, job_desc in enumerate(job_descs):
            if job_desc is None:
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
Also, estimate a match score for a generic SOC Analyst role out of 100, and list missing skills/certifications for reaching 90/100.
Show the score on a single line as 'Match Score: X/100'. List missing skills as bullet points.
"""
            else:
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
Estimate a match score out of 100, and show it as 'Match Score: X/100' on a single line at the top.
List missing skills/certifications needed to reach a score of 90/100 as bullet points, under a heading 'Missing Skills to reach 90/100:'.
"""
            print(f"\n🔍 Sending content to Gemini for {job_desc_labels[idx]}...\n")
            result = ask_gemini(prompt)
            score, missing_skills = extract_score_and_missing_skills(result)
            results.append({
                "label": job_desc_labels[idx],
                "result": result,
                "score": score if score is not None else 0,
                "missing_skills": missing_skills
            })

        # ترتيب النتائج بالأعلى أولاً
        results = sorted(results, key=lambda x: x["score"], reverse=True)

        # عرض النتائج في شكل منظم
        for i, res in enumerate(results):
            print("\n" + "=" * 60)
            print(f"Result for: {res['label']}")
            print("-" * 60)
            # جرافيك النتيجة
            if res["score"] is not None:
                print("Match Score:", ascii_bar(res["score"], 100, 20))
            else:
                print("Match Score: N/A")
            # المهارات المفقودة
            if res["missing_skills"]:
                print("Missing Skills to reach 90/100:")
                for skill in res["missing_skills"]:
                    print(f" - {skill}")
            print("-" * 60)
            print("Full Analysis:\n")
            print(res["result"][:1500] + ("...\n" if len(res["result"]) > 1500 else ""))
            print("=" * 60)

        # سؤال المستخدم عن الحفظ
        while True:
            print("\n💾 Do you want to save any result?")
            print("1. Save all as TXT")
            print("2. Save all as PDF")
            print("3. Save a specific result")
            print("4. Return to main menu")
            print("5. Exit")
            save_choice = input("Choose (1–5): ").strip()
            if save_choice == "1":
                for i, res in enumerate(results):
                    filename = f"outputs/jobmatch_{i+1}_{res['label'].replace(' ', '_')}.txt"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(res["result"])
                    print(f"✅ Saved to {filename}")
                break
            elif save_choice == "2":
                for i, res in enumerate(results):
                    filename = f"outputs/jobmatch_{i+1}_{res['label'].replace(' ', '_')}.pdf"
                    try:
                        format_cv_to_pdf(res["result"], filename=filename)
                        print(f"✅ Saved to {filename}")
                    except Exception as e:
                        print(f"❌ Error saving PDF {filename}: {e}")
                break
            elif save_choice == "3":
                idx = int(input(f"Which result? (1-{len(results)}): ").strip()) - 1
                if 0 <= idx < len(results):
                    fmt = input("Save as [1] TXT or [2] PDF? ").strip()
                    label = results[idx]['label'].replace(' ', '_')
                    if fmt == "1":
                        filename = f"outputs/jobmatch_{idx+1}_{label}.txt"
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(results[idx]["result"])
                        print(f"✅ Saved to {filename}")
                    elif fmt == "2":
                        filename = f"outputs/jobmatch_{idx+1}_{label}.pdf"
                        try:
                            format_cv_to_pdf(results[idx]["result"], filename=filename)
                            print(f"✅ Saved to {filename}")
                        except Exception as e:
                            print(f"❌ Error saving PDF {filename}: {e}")
                    else:
                        print("❌ Invalid format.")
                else:
                    print("❌ Invalid index.")
                break
            elif save_choice == "4":
                break
            elif save_choice == "5":
                print("👋 Done. Exiting.")
                exit()
            else:
                print("❌ Invalid choice. Try again.")

def enhance_cv():
    # نفس دالة enhance_cv المفصلة عندك (بدون تغيير)
    # ...
    pass

if __name__ == "__main__":
    main()