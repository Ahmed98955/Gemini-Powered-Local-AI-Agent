# 🚀 Gemini-Powered Local AI Agent

A lightweight, local AI-powered command-line assistant designed to **enhance CVs**, **generate cover letters**, **match job descriptions**, and **automate professional documents**.  
Built with **Python**, powered by **Gemini API**, and structured for scalability and offline productivity.

---

## ✨ Features

- ✅ Enhance your existing CV with professional formatting and structure.
- ✅ Generate custom-tailored **Cover Letters**, **Summaries**, or **Proposals**.
- ✅ Match your CV against job descriptions with AI-powered scoring.
- ✅ Fully interactive CLI with editable output.
- ✅ Generate clean PDF or TXT outputs.
- ✅ Local automation — no cloud dependencies (except for Gemini API).
- ✅ Extendable and well-organized project structure.

---

## 📁 Project Structure


Gemini-Powered-Local-AI-Agent/
```│
├── main.py                         # 🔹 Entry point for CLI interface
│
├── config/
│   └── config.json                # (Deprecated) Initial config – replaced by `.env`
│
├── data/                          # 📄 Input files: CVs, job descriptions, notes
│   └── your_cv.pdf
│
├── documents/                     # 📚 Reference materials or docs
│   └── CV_Enhancer_Generator_Documentation.pdf
│
├── modules/                       # ⚙️ Functional logic split into modules
│   ├── cv_enhancer.py             # Enhance and format CVs
│   └── job_matcher.py             # Match CVs with job descriptions
│
├── utils/                         # 🧰 Utilities and helpers
│   ├── gemini_api.py              # Communicate with Gemini API
│   ├── cv_pdf_formatter.py        # Cleanly format CVs to PDF
│   ├── file_utils.py              # File read/write and input handling
│   └── font/                      # Fonts used in formatted PDFs
│       ├── arial.ttf
│       └── ...
│
├── outputs/                       # 📦 All generated outputs (CVs, reports)
│   └── final_cv.pdf
│
├── requirements.txt              # 📦 Python dependencies
├── .env                          # 🔐 Store Gemini API Key (not tracked by git)
├── .gitignore                    # 🛑 Prevent tracking sensitive/system files
└── README.md                     # 📝 You are here
 ```



---

## ⚙️ Setup & Installation

### 1. Clone the repo

```
git clone https://github.com/Ahmed98955/Gemini-Powered-Local-AI-Agent.git
cd Gemini-Powered-Local-AI-Agent
```
### 2. 🧪 Install Required Packages
```
pip install -r requirements.txt
```

### 3. 🔐 Add Your Gemini API Key
Create a .env file in the root directory: env,Copy,Edit
```
GEMINI_API_KEY=your_api_key_here
```
---
## 🧠 Usage
### Show Help
```
python main.py -h
```
### Launch CV Enhancer
```
python main.py --cv_enhancer
```
### Launch Job Matcher
```
python main.py --job_matcher
```
💡 The CLI is fully interactive — it guides you step-by-step and supports customization (instructions, formats, edits).
---
## 📌 Roadmap

🌐 LinkedIn / Glassdoor integration via Puppeteer or Fellou

✉️ Email automation (e.g., reply to recruiters)

🗂️ Smart document storage and history

🧾 AI-powered content auditing and scoring

🎙️ Voice command support (future)

🧠 Pluggable LLM support (OpenAI, Claude, LLaMA, etc.)
---

## 🛡️ Security & Privacy
API Key securely loaded via .env file.

No files uploaded externally (except to Gemini API).

Open-source and customizable by design.
---
## 🧾 License
This project is licensed under the MIT License.

Feel free to use, modify, and share it with credit!


## 👨‍💻 Author
Made with passion by Ahmed Raafat
## 🔗 GitHub: https://github.com/Ahmed98955
## 📧 Email: ahmozee123@gmail.com







