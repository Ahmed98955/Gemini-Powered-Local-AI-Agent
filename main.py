import os
import argparse
import sys
import json
from pathlib import Path
from utils.cv_pdf_formatter import format_cv_to_pdf

# ألوان وجرافيك طرفية (لو الطرفية تدعم)
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
except ImportError:
    class Dummy:
        def __getattr__(self, x): return ""
    Fore = Style = Dummy()

def print_logo_job_matcher():
    art = r"""
     ██╗ ██████╗ ██████╗     ███╗   ███╗ █████╗ ████████╗ ██████╗██╗  ██╗███████╗██████╗ 
     ██║██╔═══██╗██╔══██╗    ████╗ ████║██╔══██╗╚══██╔══╝██╔════╝██║  ██║██╔════╝██╔══██╗
     ██║██║   ██║██████╔╝    ██╔████╔██║███████║   ██║   ██║     ███████║█████╗  ██████╔╝
██   ██║██║   ██║██╔═══╝     ██║╚██╔╝██║██╔══██║   ██║   ██║     ██╔══██║██╔══╝  ██╔══██╗
╚█████╔╝╚██████╔╝██║         ██║ ╚═╝ ██║██║  ██║   ██║   ╚██████╗██║  ██║███████╗██║  ██║
 ╚════╝  ╚═════╝ ╚═╝         ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                                                                                         
"""
    print(Fore.CYAN + art + Style.RESET_ALL)

def print_logo_cv_enhancer():
    art = r"""
 ██████╗██╗   ██╗    ███████╗███╗   ██╗██╗  ██╗ █████╗ ███╗   ██╗ ██████╗███████╗██████╗ 
██╔════╝██║   ██║    ██╔════╝████╗  ██║██║  ██║██╔══██╗████╗  ██║██╔════╝██╔════╝██╔══██╗
██║     ██║   ██║    █████╗  ██╔██╗ ██║███████║███████║██╔██╗ ██║██║     █████╗  ██████╔╝
██║     ╚██╗ ██╔╝    ██╔══╝  ██║╚██╗██║██╔══██║██╔══██║██║╚██╗██║██║     ██╔══╝  ██╔══██╗
╚██████╗ ╚████╔╝     ███████╗██║ ╚████║██║  ██║██║  ██║██║ ╚████║╚██████╗███████╗██║  ██║
 ╚═════╝  ╚═══╝      ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝  ╚═╝
                                                                                         
"""
    print(Fore.LIGHTYELLOW_EX + art + Style.RESET_ALL)

def print_banner(text):
    print(Fore.CYAN + "\n" + "★" * 60)
    print(" " * ((60 - len(text)) // 2) + Fore.YELLOW + text.upper())
    print(Fore.CYAN + "★" * 60 + Style.RESET_ALL)

def print_divider():
    print(Fore.MAGENTA + "\n" + "="*60 + Style.RESET_ALL)

def print_choice_bar():
    print(Fore.GREEN + "\n" + "-"*60 + Style.RESET_ALL)

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
        print_banner("AI CV Assistant")
        print("--cv_enhancer   → Enhance and generate CV")
        print("--job_matcher   → Match your CV with a job description (single or multiple jobs, with score & missing skills)")
        print("💡 Example: python main.py --job_matcher")

# استخراج النص من PDF
def extract_text_from_pdf(pdf_path):
    from PyPDF2 import PdfReader
    reader = PdfReader(pdf_path)
    return "\n".join([page.extract_text() or "" for page in reader.pages])

# رسم بار ASCII
def ascii_bar(score, outof=100, width=20):
    filled = int(round(score / outof * width))
    return Fore.YELLOW + "[" + Fore.GREEN + "█" * filled + Fore.RED + "-" * (width - filled) + Fore.YELLOW + f"] {score:.0f}/{outof}" + Style.RESET_ALL

# استخراج النسبة والمهارات
def extract_score_and_missing_skills(text):
    import re
    score = None
    match = re.search(r"(\d{1,3})\s*/\s*100", text)
    if match:
        score = int(match.group(1))
    else:
        match = re.search(r"(\d{1,3})\s*%", text)
        if match:
            score = int(match.group(1))
    missing_skills = []
    ms_match = re.search(r"(Missing Skills|Areas for Improvement|To reach [\d]+/100.*?:|To increase your score.*?:)(.*?)(\n\n|\Z)", text, re.IGNORECASE | re.DOTALL)
    if ms_match:
        ms_block = ms_match.group(2)
        ms_lines = [line.strip("-*• \t") for line in ms_block.strip().splitlines() if line.strip("-*• \t")]
        missing_skills = [line for line in ms_lines if len(line) > 2]
    return score, missing_skills

# مكان الحفظ الافتراضي
def get_default_save_dir():
    home = str(Path.home())
    return os.path.join(home, "Desktop")

# قراءة آخر مكان حفظ من ملف إعدادات
def load_user_save_dir():
    settings_file = "user_settings.json"
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("save_dir") or get_default_save_dir()
        except Exception:
            return get_default_save_dir()
    else:
        return get_default_save_dir()

def save_user_save_dir(path):
    settings_file = "user_settings.json"
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump({"save_dir": path}, f)

def job_matcher_multi_jobs():
    print_logo_job_matcher()
    print(Fore.LIGHTCYAN_EX + "🚀 Welcome to the Job Matcher module! Let's help you shine! 🚀" + Style.RESET_ALL)

    # 1. طلب ملف CV
    while True:
        print_choice_bar()
        cv_path = input(Fore.LIGHTCYAN_EX + "📄 Enter CV file path (PDF or TXT):\n> " + Style.RESET_ALL).strip()
        if not os.path.exists(cv_path):
            print(Fore.RED + "❌ File not found. Please try again." + Style.RESET_ALL)
        else:
            break
    if cv_path.endswith(".pdf"):
        cv_content = extract_text_from_pdf(cv_path)
    else:
        with open(cv_path, "r", encoding="utf-8") as f:
            cv_content = f.read()

    while True:
        print_divider()
        print(Fore.LIGHTMAGENTA_EX + "🔘 What would you like to do?" + Style.RESET_ALL)
        print("1. 🎯 Match CV with a single job description")
        print("2. 📚 Match CV with multiple job descriptions")
        print("3. 🧠 General CV Assessment (no specific job)")
        print("4. 🔙 Return to main menu")
        print("5. ❌ Exit")
        option = input(Fore.CYAN + "Choose (1–5): " + Style.RESET_ALL).strip()
        if option == "5":
            print(Fore.YELLOW + "👋 Exiting." + Style.RESET_ALL)
            exit()
        if option == "4":
            print(Fore.YELLOW + "↩️ Returning to main menu..." + Style.RESET_ALL)
            return

        job_descs = []
        job_desc_labels = []
        if option == "1":
            print_choice_bar()
            print("How would you like to provide the job description?")
            print("1. 📝 Paste job description manually")
            print("2. 📄 Load from TXT or PDF file")
            job_input = input(Fore.CYAN + "Choose (1–2): " + Style.RESET_ALL).strip()
            if job_input == "1":
                print(Fore.LIGHTGREEN_EX + "✍️ Paste the job description below. (Ctrl+Z then Enter to finish on Windows)" + Style.RESET_ALL)
                print("-" * 60)
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
                job_file = input(Fore.LIGHTCYAN_EX + "📄 Enter job description file path (TXT or PDF):\n> " + Style.RESET_ALL).strip()
                if not os.path.exists(job_file):
                    print(Fore.RED + "❌ File not found. Returning to previous menu." + Style.RESET_ALL)
                    continue
                if job_file.endswith(".pdf"):
                    job_descs = [extract_text_from_pdf(job_file)]
                else:
                    with open(job_file, "r", encoding="utf-8") as f:
                        job_descs = [f.read()]
                job_desc_labels = [os.path.basename(job_file)]
        elif option == "2":
            print_choice_bar()
            print("How many job descriptions do you want to compare?")
            try:
                count = int(input(Fore.CYAN + "Number of jobs: " + Style.RESET_ALL).strip())
            except Exception:
                print(Fore.RED + "❌ Invalid number. Try again." + Style.RESET_ALL)
                continue
            for i in range(count):
                print_choice_bar()
                print(f"Job description #{i+1} input method:")
                print("1. 📝 Paste job description manually")
                print("2. 📄 Load from TXT or PDF file")
                job_input = input(Fore.CYAN + "Choose (1–2): " + Style.RESET_ALL).strip()
                if job_input == "1":
                    print(Fore.LIGHTGREEN_EX + f"✍️ Paste the job description for Job #{i+1} below. (Ctrl+Z then Enter to finish)" + Style.RESET_ALL)
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
                    job_file = input(Fore.LIGHTCYAN_EX + f"📄 Enter job description file path (TXT or PDF) for Job #{i+1}:\n> " + Style.RESET_ALL).strip()
                    if not os.path.exists(job_file):
                        print(Fore.RED + "❌ File not found. Skipping this job." + Style.RESET_ALL)
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
            print(Fore.RED + "❌ Invalid choice. Try again." + Style.RESET_ALL)
            continue

        # تعليمات إضافية
        print_choice_bar()
        instruction_text = ""
        print("📎 Do you want to add extra instructions?")
        print("1. ✏️ Write instructions now")
        print("2. 📎 Attach a TXT or PDF file")
        print("3. 🚫 No instructions")
        instruction_choice = input(Fore.CYAN + "Choose (1–3): " + Style.RESET_ALL).strip()

        if instruction_choice == "1":
            print(Fore.LIGHTGREEN_EX + "✍️ Write your instructions below." + Style.RESET_ALL)
            instruction_text = input("Your instructions: \n> ").strip()
        elif instruction_choice == "2":
            file_path = input(Fore.LIGHTCYAN_EX + "📎 Enter path to instruction file: " + Style.RESET_ALL).strip()
            if os.path.exists(file_path):
                if file_path.endswith(".pdf"):
                    instruction_text = extract_text_from_pdf(file_path)
                else:
                    with open(file_path, "r", encoding="utf-8") as f:
                        instruction_text = f.read()
        else:
            instruction_text = ""

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
            print_choice_bar()
            print(Fore.LIGHTBLUE_EX + f"\n🔍 Sending content to Gemini for {job_desc_labels[idx]}...\n" + Style.RESET_ALL)
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
            print_divider()
            print(Fore.LIGHTYELLOW_EX + f"⭐ Result for: {res['label']}" + Style.RESET_ALL)
            print_choice_bar()
            # جرافيك النتيجة
            if res["score"] is not None:
                print("📊 Match Score:", ascii_bar(res["score"], 100, 20))
            else:
                print("Match Score: N/A")
            # المهارات المفقودة
            if res["missing_skills"]:
                print(Fore.LIGHTRED_EX + "🛠️ Missing Skills to reach 90/100:" + Style.RESET_ALL)
                for skill in res["missing_skills"]:
                    print(Fore.RED + f"   - {skill}" + Style.RESET_ALL)
            print_choice_bar()
            print("📝 Full Analysis:\n")
            print(res["result"][:1500] + ("...\n" if len(res["result"]) > 1500 else ""))
            print_divider()

        # واجهة الحفظ الجديدة
        while True:
            save_dir = load_user_save_dir()
            print(Fore.LIGHTMAGENTA_EX + "\n💾 How would you like to save the results?" + Style.RESET_ALL)
            print("1. 💼 Choose location and filename manually")
            print(f"2. 🖥️ Save all in Desktop ({get_default_save_dir()})")
            print(f"3. 📂 Save all in preferred folder (currently: {save_dir})")
            print("4. 🔙 Return to main menu")
            print("5. ⚙️ Set/change preferred save folder")
            print("6. ❌ Exit")
            save_choice = input(Fore.CYAN + "Choose (1–6): " + Style.RESET_ALL).strip()
            if save_choice == "1":
                for i, res in enumerate(results):
                    label = res['label'].replace(' ', '_')
                    fmt = input(f"Result {i+1}/{len(results)} – Save as [1] TXT, [2] PDF? ").strip()
                    path = input("Enter full file path (or Enter for Desktop): ").strip()
                    if not path:
                        path = os.path.join(get_default_save_dir(), f"jobmatch_{i+1}_{label}.{'txt' if fmt == '1' else 'pdf'}")
                    if fmt == "1":
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(res["result"])
                        print(Fore.GREEN + f"✅ Saved to {path}" + Style.RESET_ALL)
                    elif fmt == "2":
                        try:
                            format_cv_to_pdf(res["result"], filename=path)
                            print(Fore.GREEN + f"✅ Saved to {path}" + Style.RESET_ALL)
                        except Exception as e:
                            print(Fore.RED + f"❌ Error saving PDF {path}: {e}" + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "❌ Invalid format." + Style.RESET_ALL)
                break
            elif save_choice == "2":
                for i, res in enumerate(results):
                    label = res['label'].replace(' ', '_')
                    txt_path = os.path.join(get_default_save_dir(), f"jobmatch_{i+1}_{label}.txt")
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(res["result"])
                    print(Fore.GREEN + f"✅ Saved TXT to {txt_path}" + Style.RESET_ALL)
                    pdf_path = os.path.join(get_default_save_dir(), f"jobmatch_{i+1}_{label}.pdf")
                    try:
                        format_cv_to_pdf(res["result"], filename=pdf_path)
                        print(Fore.GREEN + f"✅ Saved PDF to {pdf_path}" + Style.RESET_ALL)
                    except Exception as e:
                        print(Fore.RED + f"❌ Error saving PDF {pdf_path}: {e}" + Style.RESET_ALL)
                break
            elif save_choice == "3":
                for i, res in enumerate(results):
                    label = res['label'].replace(' ', '_')
                    txt_path = os.path.join(save_dir, f"jobmatch_{i+1}_{label}.txt")
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(res["result"])
                    print(Fore.GREEN + f"✅ Saved TXT to {txt_path}" + Style.RESET_ALL)
                    pdf_path = os.path.join(save_dir, f"jobmatch_{i+1}_{label}.pdf")
                    try:
                        format_cv_to_pdf(res["result"], filename=pdf_path)
                        print(Fore.GREEN + f"✅ Saved PDF to {pdf_path}" + Style.RESET_ALL)
                    except Exception as e:
                        print(Fore.RED + f"❌ Error saving PDF {pdf_path}: {e}" + Style.RESET_ALL)
                break
            elif save_choice == "4":
                break
            elif save_choice == "5":
                new_dir = input("Enter full path to preferred save folder: ").strip()
                if os.path.isdir(new_dir):
                    save_user_save_dir(new_dir)
                    print(Fore.GREEN + "Changed preferred folder successfully." + Style.RESET_ALL)
                else:
                    print(Fore.RED + "❌ Invalid directory. Try again." + Style.RESET_ALL)
            elif save_choice == "6":
                print(Fore.YELLOW + "👋 Done. Exiting." + Style.RESET_ALL)
                exit()
            else:
                print(Fore.RED + "❌ Invalid choice. Try again." + Style.RESET_ALL)

def enhance_cv():
    print_logo_cv_enhancer()
    print(Fore.LIGHTYELLOW_EX + "🌟 Welcome to the CV Enhancer! Let's build your best version! 🌟" + Style.RESET_ALL)

    from PyPDF2 import PdfReader
    def extract_text_from_pdf(pdf_path):
        reader = PdfReader(pdf_path)
        return "\n".join([page.extract_text() or "" for page in reader.pages])

    while True:
        print_choice_bar()
        cv_path = input(Fore.LIGHTCYAN_EX + "📄 Enter CV file path (PDF or TXT):\n> " + Style.RESET_ALL).strip()
        if not os.path.exists(cv_path):
            print(Fore.RED + "❌ File not found. Please try again." + Style.RESET_ALL)
        else:
            break

    if cv_path.endswith(".pdf"):
        cv_content = extract_text_from_pdf(cv_path)
    else:
        with open(cv_path, "r", encoding="utf-8") as f:
            cv_content = f.read()

    while True:
        print_divider()
        print(Fore.LIGHTMAGENTA_EX + "🔘 What would you like to generate?" + Style.RESET_ALL)
        print("1. 📝 Enhanced CV")
        print("2. 🎯 Cover Letter")
        print("3. 🧾 Summary")
        print("4. 💼 Proposal")
        print("5. 🔙 Exit")
        choice_map = {"1": "enhanced cv", "2": "cover letter", "3": "summary", "4": "proposal"}
        choice = input(Fore.CYAN + "Choose an option (1–5): " + Style.RESET_ALL).strip()
        if choice == "5":
            print(Fore.YELLOW + "👋 Exiting." + Style.RESET_ALL)
            exit()
        if choice not in choice_map:
            print(Fore.RED + "❌ Invalid choice. Returning to main menu." + Style.RESET_ALL)
            continue

        instruction_text = ""
        print_choice_bar()
        print("📎 Do you want to add extra instructions?")
        print("1. ✏️ Write instructions now")
        print("2. 📎 Attach a TXT or PDF file")
        print("3. 🚫 No instructions")
        instruction_choice = input(Fore.CYAN + "Choose (1–3): " + Style.RESET_ALL).strip()

        if instruction_choice == "1":
            print(Fore.LIGHTGREEN_EX + "✍️ Write your instructions below." + Style.RESET_ALL)
            instruction_text = input("Your instructions: \n> ").strip()

        elif instruction_choice == "2":
            file_path = input(Fore.LIGHTCYAN_EX + "📎 Enter path to instruction file: " + Style.RESET_ALL).strip()
            if os.path.exists(file_path):
                if file_path.endswith(".pdf"):
                    instruction_text = extract_text_from_pdf(file_path)
                else:
                    with open(file_path, "r", encoding="utf-8") as f:
                        instruction_text = f.read()
        else:
            instruction_text = ""

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
            print_choice_bar()
            print(Fore.LIGHTBLUE_EX + "\n🔍 Sending content to Gemini...\n" + Style.RESET_ALL)
            return ask_gemini(prompt)

        result = generate_output()

        while True:
            print_divider()
            print(Fore.LIGHTYELLOW_EX + "📄 Preview of result:" + Style.RESET_ALL)
            print(result[:1500] + ("...\n" if len(result) > 1500 else ""))

            confirm = input(Fore.LIGHTGREEN_EX + "\n🧾 Is this output ready for final formatting? (y/n): " + Style.RESET_ALL).lower()
            if confirm == "y":
                break

            print_choice_bar()
            print("✍️ Would you like to:")
            print("1. 📝 Write changes manually")
            print("2. 📎 Attach a TXT or PDF file with updated content")
            print("3. ♻️ Regenerate result using the same inputs")
            print("4. 🔙 Return to main menu")
            print("5. ❌ Exit")
            correction = input(Fore.CYAN + "Choose (1–5): " + Style.RESET_ALL).strip()

            if correction == "1":
                print(Fore.LIGHTGREEN_EX + "📝 Type your full revision below, then press Enter twice when done:" + Style.RESET_ALL)
                print("(Hint: use Ctrl+Z then Enter to end input on Windows)")
                print("-" * 60)
                lines = []
                while True:
                    try:
                        line = input()
                        lines.append(line)
                    except EOFError:
                        break
                result = "\n".join(lines)
            elif correction == "2":
                new_file = input(Fore.LIGHTCYAN_EX + "📎 Enter path to updated TXT or PDF file: " + Style.RESET_ALL).strip()
                if os.path.exists(new_file):
                    if new_file.endswith(".pdf"):
                        result = extract_text_from_pdf(new_file)
                    else:
                        with open(new_file, "r", encoding="utf-8") as f:
                            result = f.read()
                else:
                    print(Fore.RED + "❌ File not found. Keeping previous result." + Style.RESET_ALL)
            elif correction == "3":
                result = generate_output()
            elif correction == "4":
                print(Fore.YELLOW + "↩️ Returning to main menu..." + Style.RESET_ALL)
                return
            elif correction == "5":
                print(Fore.YELLOW + "👋 Exiting." + Style.RESET_ALL)
                exit()
            else:
                print(Fore.RED + "❌ Invalid choice. Try again." + Style.RESET_ALL)
        else:
            continue  # stay in correction loop

        # ✅ Only save if confirmed "y"
        while True:
            print_choice_bar()
            print(Fore.LIGHTMAGENTA_EX + "💾 Save as:" + Style.RESET_ALL)
            print("1. 💼 TXT")
            print("2. 🖨️ PDF")
            save_format = input(Fore.CYAN + "Choose (1 or 2): " + Style.RESET_ALL).strip()
            if save_format == "1":
                default_path = os.path.join(get_default_save_dir(), "final_result.txt")
                custom_path = input(Fore.LIGHTCYAN_EX + f"📁 Save path? Press Enter to use default ({default_path}) or type custom path:\n> " + Style.RESET_ALL).strip()
                path = custom_path if custom_path else default_path
                with open(path, "w", encoding="utf-8") as f:
                    f.write(result)
                print(Fore.GREEN + f"✅ Saved to {path}" + Style.RESET_ALL)
            elif save_format == "2":
                default_pdf = os.path.join(get_default_save_dir(), "final_cv.pdf")
                while True:
                    custom_pdf = input(Fore.LIGHTCYAN_EX + f"📁 PDF save path? Press Enter to use default ({default_pdf}) or type custom path:\n> " + Style.RESET_ALL).strip()
                    path = custom_pdf if custom_pdf else default_pdf
                    if os.path.isdir(path):
                        print(Fore.RED + "❌ Please include a full filename with extension (e.g., D:\\MyCV.pdf)" + Style.RESET_ALL)
                        continue
                    try:
                        format_cv_to_pdf(result, filename=path)
                        print(Fore.GREEN + f"✅ Saved to {path}" + Style.RESET_ALL)
                        break
                    except Exception as e:
                        print(Fore.RED + f"❌ Error saving PDF: {e}" + Style.RESET_ALL)
                        continue
            else:
                print(Fore.RED + "❌ Invalid choice. Try again." + Style.RESET_ALL)
                continue

            again = input(Fore.LIGHTGREEN_EX + "↩️ Do you want to return to the main menu? (y/n): " + Style.RESET_ALL).lower()
            if again == "y":
                break  # back to generation menu
            else:
                print(Fore.YELLOW + "👋 Done. Exiting." + Style.RESET_ALL)
                exit()

if __name__ == "__main__":
    main()