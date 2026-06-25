# LinkedIn Buzzword Analyzer

A web app that analyzes LinkedIn captions for corporate jargon and buzzwords.
Paste one or more posts and get a cringe score, buzzword breakdown, and a cleaner rewrite — powered by Google Gemini.

---

## Features

- Detects 80+ corporate buzzwords and LinkedIn-specific phrases
- Rule-based cringe score for instant feedback
- Gemini AI analysis with verdict, reasons, and rewrite suggestion
- Frequency chart across all posts
- Supports multiple posts via paste or `.txt` file upload

---

## Tech stack

- Python 3.11
- Streamlit
- Google Gemini API (`gemini-1.5-flash`)
- Plotly
- Pandas

---

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/Grisha-sketch/linkedin-buzzword-analyzer.git
cd linkedin-buzzword-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and add your Gemini API key:
Get a free key at [aistudio.google.com](https://aistudio.google.com).

### 4. Run the app

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Usage

1. Paste one or more LinkedIn captions into the text area
2. Separate multiple posts with a blank line or `---`
3. Toggle Gemini AI analysis on or off
4. Click **Analyze**

---

## Project structure
linkedin-buzzword-analyzer/

├── app.py               # Streamlit UI

├── analyzer.py          # Buzzword detection and scoring

├── llm.py               # Gemini API integration

├── buzzwords.py         # Curated buzzword list

├── requirements.txt

├── .env.example

├── .github/

│   └── workflows/

│       └── ci.yml

└── README.md

---

## CI/CD

GitHub Actions runs on every push to `main`:
- Validates the buzzword list loads correctly
- Runs the analyzer on a sample post
- Lints with flake8

---

## License

MIT