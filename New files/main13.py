import os
import argparse
from modules.cv_enhancer import enhance_cv
from modules.job_matcher import match_job_with_cv   # ✅ أضف هذا السطر
from utils.cv_pdf_formatter import format_cv_to_pdf

def main():
    parser = argparse.ArgumentParser(description="AI Assistant for CV and Job Tools")
    parser.add_argument("--cv_enhancer", action="store_true", help="Enhance and generate CV with options")
    parser.add_argument("--job_matcher", action="store_true", help="Match CV with a job description")  # ✅ أضف هذا السطر
    args = parser.parse_args()

    if args.cv_enhancer:
        while True:
            enhance_cv()

    elif args.job_matcher:  # ✅ أضف هذا السطر
        match_job_with_cv()

    else:
        print("\n🔘 Choose a module to run:")
        print("--cv_enhancer   → Enhance and generate CV")
        print("--job_matcher   → Match your CV with a job description")
        print("💡 Example: python main.py --cv_enhancer")

if __name__ == "__main__":
    main()