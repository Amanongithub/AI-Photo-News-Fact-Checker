
# 📰 AI Photo News Fact Checker

An AI-powered application that **checks news from photos and screenshots**.

The user places a **photo/screenshot containing a news article or social-media news post** into the `images/` folder. The application reads the text from the photo using OCR, extracts the main news claim using Gemini, searches the web for supporting or contradicting information using Tavily, and finally uses Gemini to analyze the evidence.

The workflow is orchestrated using **LangGraph**, while **LangChain** connects the Large Language Model (LLM) and external tools.

---

# 🎯 Project Goal

A large amount of news is shared through:

* News screenshots
* WhatsApp images
* Instagram posts
* Facebook posts
* News article photos
* Social media screenshots

The information in these images cannot be directly searched or analyzed as normal text.

This project solves that problem by converting:

```text
📸 NEWS PHOTO
<img width="1220" height="1681" alt="1000029303" src="https://github.com/user-attachments/assets/06baae1c-e043-4dc4-9e9c-2400675f4ae1" />

      ↓
   OCR TEXT
      ↓
   NEWS CLAIM
      ↓
  WEB SEARCH
      ↓
   EVIDENCE
      ↓
   AI ANALYSIS
      ↓
TRUE / FALSE / UNCERTAIN

```

The main focus of this project is therefore **fact-checking news contained inside photos/images**.

---

# 🏗️ Architecture

```text
                  📸 NEWS PHOTO
                       |
                       ↓
                 Tesseract OCR
                       |
                       ↓
                 Extracted Text
                       |
                       ↓
              ┌─────────────────┐
              │     Gemini      │
              │ Claim Extraction│
              └─────────────────┘
                       |
                       ↓
                  News Claim
                       |
                       ↓
              ┌─────────────────┐
              │     Tavily      │
              │   Web Search    │
              └─────────────────┘
                       |
                       ↓
                 Web Evidence
                       |
                       ↓
              ┌─────────────────┐
              │     Gemini      │
              │  Fact Checker   │
              └─────────────────┘
                       |
                       ↓
          ┌────────────┼────────────┐
          ↓            ↓            ↓
        TRUE         FALSE      UNCERTAIN
                       |
                       ↓
                 results.json
```

---

# 🔄 LangGraph Workflow

LangGraph controls the overall workflow.

```text
START
  ↓
read_image
  ↓
get_claim
  ↓
search_news
  ↓
check_news
  ↓
END
```

Each step is implemented as a LangGraph node.

---

# 🧠 Where LangChain Is Used

**LangChain is an important part of this project because it provides the integration layer between the application, Gemini, and Tavily.**

Instead of writing separate low-level API code for every AI service, LangChain provides a common interface for interacting with models and tools.

The project uses:

```text
Python
   ↓
LangChain
   ├── Gemini LLM
   └── Tavily Search
```

---

# 🔗 LangChain Components

## 1. Gemini Integration

The project uses:

```python
from langchain_google_genai import ChatGoogleGenerativeAI
```

This provides the LangChain interface to Google Gemini.

The application creates the model:

```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=GEMINI_API_KEY
)
```

Gemini performs two important tasks.

### Claim extraction

The OCR text is sent to Gemini:

```text
OCR Text
   ↓
Gemini
   ↓
Main factual claim
```

For example, the photo might contain:

```text
Eiffel Tower No More!

The Eiffel Tower is going to be demolished
next year after lease expiry.
```

Gemini extracts the important claim:

```text
The Eiffel Tower will be demolished next year.
```

This is important because the entire OCR text may contain:

* Website names
* Likes
* Comments
* Hashtags
* Advertisements
* Usernames
* Captions

The LLM identifies the actual factual statement that needs verification.

---

# 🔎 2. Tavily Integration

The project uses:

```python
from langchain_tavily import TavilySearch
```

Tavily provides web search functionality through a LangChain-compatible tool.

The claim is sent to Tavily:

```text
News Claim
    ↓
Tavily
    ↓
Web Search Results
```

The results can contain:

* News articles
* Official websites
* Government sources
* Organizations
* Other relevant web pages

These results become the evidence used by the fact-checking step.

---

# 🤖 3. Gemini + Evidence

After Tavily searches the web, the results are passed back to Gemini.

The process becomes:

```text
Claim
  +
Web Evidence
  ↓
Gemini
  ↓
Fact Check
```

Gemini evaluates whether the available evidence:

* Supports the claim
* Contradicts the claim
* Is insufficient

The application returns:

```text
TRUE
FALSE
UNCERTAIN
```

---

# 🕸️ Why LangGraph?

LangChain connects the AI components, but the project also needs to control **the order in which different operations happen**.

This is where LangGraph is used.

LangGraph allows the application to represent the process as a workflow.

```text
Photo
 ↓
OCR
 ↓
Claim Extraction
 ↓
Web Search
 ↓
Fact Checking
```

Each step has its own node.

For example:

```python
graph.add_node("read_image", read_image)

graph.add_node("get_claim", get_claim)

graph.add_node("search_news", search_news)

graph.add_node("check_news", check_news)
```

The nodes are then connected:

```python
graph.add_edge(START, "read_image")

graph.add_edge("read_image", "get_claim")

graph.add_edge("get_claim", "search_news")

graph.add_edge("search_news", "check_news")

graph.add_edge("check_news", END)
```

This creates the complete AI workflow.

---

# 🔗 LangChain vs LangGraph

They have different responsibilities.

| Component | Responsibility          |
| --------- | ----------------------- |
| LangChain | Connects LLMs and tools |
| LangGraph | Controls the workflow   |
| Gemini    | AI reasoning            |
| Tavily    | Web search              |
| Tesseract | OCR                     |
| Pillow    | Image processing        |
| Python    | Application logic       |

A simple way to understand it:

```text
LangChain = Connect the AI tools

LangGraph = Control the AI workflow
```

---

# 🧩 Why Not Just Use Gemini?

Gemini by itself can analyze text, but this project needs more than an LLM.

The application needs to:

1. Read text from a photo.
2. Search current information on the internet.
3. Collect evidence.
4. Analyze the evidence.
5. Produce a structured result.

Therefore:

```text
Tesseract
    ↓
Reads the photo

LangChain + Gemini
    ↓
Understands the claim

LangChain + Tavily
    ↓
Finds web evidence

LangGraph
    ↓
Controls the workflow
```

This makes the project more representative of an **AI application workflow** rather than simply sending a prompt to an LLM.

---

# 📸 Input: News Photo

The primary input is a **photo or screenshot containing news**.

Example:

```text
images/
│
├── news1.png
├── news2.jpg
└── news3.jpeg
```

A photo could contain:

```text
┌─────────────────────────────┐
│                             │
│       BREAKING NEWS         │
│                             │
│  Eiffel Tower to be         │
│  demolished next year      │
│                             │
│       Read More...          │
│                             │
└─────────────────────────────┘
```

The application does not require the user to manually type the news.

It reads the photo automatically.

---

# 👁️ OCR Processing

Tesseract OCR converts the text inside the photo into normal text.

```text
📸 Photo
   ↓
Tesseract
   ↓
" Eiffel Tower will be demolished..."
```

The OCR output is then passed into the LangGraph workflow.

---

# 🔍 Example End-to-End Flow

Suppose the user adds:

```text
images/1000029303.png
```

The photo contains:

```text
EIFFEL TOWER NO MORE!

Most iconic landmark in Paris, Eiffel Tower
is going to be demolished next year...
```

### Step 1 — OCR

Tesseract extracts:

```text
EIFFEL TOWER NO MORE!

Most iconic landmark in Paris, Eiffel Tower
is going to be demolished next year...
```

### Step 2 — Claim Extraction

Gemini identifies:

```text
The Eiffel Tower will be demolished next year.
```

### Step 3 — Web Search

Tavily searches for information related to the claim.

### Step 4 — Evidence

Relevant search results are collected.

### Step 5 — AI Fact Check

Gemini evaluates the claim against the evidence.

### Step 6 — Result

The application produces:

```text
Verdict: FALSE

Explanation:
The available reliable evidence does not support
the claim that the Eiffel Tower is scheduled for demolition.
```

The exact result depends on the web evidence available when the application runs.

---

# 📊 Output

The application creates:

```text
results.json
```

Example:

```json
[
    {
        "image": "news1.png",
        "claim": "The Eiffel Tower will be demolished next year.",
        "verdict": "FALSE",
        "explanation": "The available evidence contradicts the claim.",
        "sources": [
            "source-url-1",
            "source-url-2"
        ]
    }
]
```

---

# 🧠 Verdict System

The application intentionally uses three possible results.

## TRUE

The available reliable evidence supports the claim.

## FALSE

The available reliable evidence directly contradicts the claim.

## UNCERTAIN

There is not enough reliable evidence to determine whether the claim is true or false.

For example:

```text
Claim
 ↓
Search
 ↓
Conflicting information
 ↓
UNCERTAIN
```

This prevents the application from automatically calling something false simply because it could not find enough information.

---

# 📁 Project Structure

```text
news-fact-checker/
│
├── news_fact_checker.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
└── images/
    └── .gitkeep
```

---

# 🛠️ Technologies

### Python

Main programming language.

### Tesseract OCR

Extracts text from news photos and screenshots.

### Pillow

Loads and processes image files.

### LangChain

Provides integrations for:

* Gemini
* Tavily
* LLM interaction
* Tool interaction

### LangGraph

Builds and executes the multi-step AI workflow.

### Google Gemini

Used for:

* Extracting the main claim
* Evaluating evidence
* Generating the final fact-check

### Tavily

Used for web research and finding current evidence.

### python-dotenv

Loads API keys from `.env`.

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/news-fact-checker.git
```

```bash
cd news-fact-checker
```

---

## 2. Create virtual environment

Windows:

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 API Configuration

Create:

```text
.env
```

Add:

```text
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Never upload `.env` to GitHub.

Use `.env.example` instead.

---

# 🖥️ Tesseract Configuration

Install Tesseract OCR on your computer.

On Windows, the executable is commonly:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

The Python application can explicitly point to it:

```python
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
```

Verify installation:

```bash
tesseract --version
```

---

# ▶️ Run

Put a news photo into:

```text
images/
```

Then run:

```bash
python news_fact_checker.py
```

The application processes the image and creates:

```text
results.json
```

---

# 🔐 Security

API keys are stored in environment variables.

The following file should never be committed:

```text
.env
```

The repository only contains:

```text
.env.example
```

---

# 📈 Future Improvements

## Multi-Agent Fact Checking

Future versions can use multiple specialized agents:

```text
                 News Photo
                     ↓
                  OCR Agent
                     ↓
                Claim Agent
                     ↓
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
  News Search   Official Search  Fact Check
       ↓             ↓             ↓
       └─────────────┼─────────────┘
                     ↓
              Evidence Agent
                     ↓
              Final AI Agent
```

---

## GitHub Actions

The project can later be integrated with GitHub Actions to automatically run the fact-checking workflow.

For example:

```text
GitHub Push
     ↓
GitHub Actions
     ↓
Run Python
     ↓
AI Fact Check
     ↓
Generate Report
```

---

## Web Interface

A future version could provide a simple interface:

```text
┌─────────────────────────────┐
│     AI NEWS FACT CHECKER    │
│                             │
│    [ Upload News Photo ]    │
│                             │
│          ↓                  │
│       Analyzing...          │
│                             │
│       Verdict: FALSE        │
│                             │
│       View Evidence         │
└─────────────────────────────┘
```

---

## Human-in-the-Loop

For more sensitive claims, the workflow could ask a human to review the AI result before producing the final verdict.

```text
AI Analysis
     ↓
Human Review
     ↓
Final Result
```

---

# 💼 Skills Demonstrated

This project demonstrates practical experience with:

* Python
* Generative AI
* LLM applications
* LangChain
* LangGraph
* Agentic AI workflows
* OCR
* Image processing
* Web search
* Prompt engineering
* API integration
* JSON
* Environment variables
* Workflow orchestration
* Evidence-based AI analysis
* AI automation

---

# 🎓 What This Project Demonstrates

The project demonstrates how an AI system can combine multiple technologies rather than relying on a single LLM.

```text
Image Processing
       +
OCR
       +
LLM
       +
Web Search
       +
Evidence Analysis
       +
Workflow Orchestration
```

The most important concept is the complete pipeline:

**📸 Photo → OCR → Claim → Search → Evidence → AI Verification → Result**

---

# ⚠️ Limitations

This project is an **AI-assisted fact-checking tool**, not an authoritative source of truth.

Possible limitations include:

* OCR mistakes
* Poor image quality
* Incomplete search results
* Unreliable websites
* Conflicting sources
* AI interpretation errors
* Satire or sarcasm
* Claims requiring specialist knowledge
* Information changing over time

Important information should always be verified against reliable primary sources.



Technologies:

**Python | LangChain | LangGraph | Gemini | Tavily | Tesseract OCR**
