# main.py
import argparse
from utils.gemini_api import ask_gemini
from modules.job_matcher import match_job_with_cv
from modules.cv_enhancer import enhance_cv  # ✅ مهم علشان نقدر نشغل CV Enhancer

def interactive_mode():
    print("🤖 Welcome to Ahmed's Smart Local Assistant")
    while True:
        try:
            user_input = input("🟢 Enter your question or command (or type 'exit' to quit):\n> ")
            if user_input.lower() == "exit":
                print("👋 Goodbye!")
                break

            response = ask_gemini(user_input)
            print("\n🔵 Gemini Response:")
            print(response)
        except Exception as e:
            print(f"❌ Error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="Ahmed's Smart Assistant")
    parser.add_argument("--job_matcher", action="store_true", help="Run job matcher module")
    parser.add_argument("--cv_enhancer", action="store_true", help="Run CV enhancer module")  # ✅ أضفنا الخيار ده
    args = parser.parse_args()

    if args.job_matcher:
        match_job_with_cv()
    elif args.cv_enhancer:
        enhance_cv()
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
