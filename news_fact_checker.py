
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image
import pytesseract

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch

from langgraph.graph import StateGraph, START, END


# Load API keys
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0,
    google_api_key=GEMINI_API_KEY
)


# Tavily
search = TavilySearch(
    max_results=5,
    topic="news"
)


# Folder containing screenshots
IMAGE_FOLDER = Path("images")


# State used by LangGraph
def create_state():
    return {
        "image": "",
        "text": "",
        "claim": "",
        "evidence": [],
        "verdict": "",
        "explanation": ""
    }


def get_text(response):
    if isinstance(response.content, str):
        return response.content

    text = ""

    for item in response.content:
        if isinstance(item, dict):
            text += item.get("text", "")

    return text


# -----------------------------------------
# 1. Read image using OCR
# -----------------------------------------

def read_image(state):

    image = Image.open(state["image"])

    text = pytesseract.image_to_string(image)

    print("\nOCR Text:")
    print(text)

    state["text"] = text

    return state


# -----------------------------------------
# 2. Get the main news claim
# -----------------------------------------

def get_claim(state):

    prompt = f"""
Read this news text and give me the main factual claim.

News:
{state["text"]}

Return only the claim.
"""

    response = llm.invoke(prompt)

    state["claim"] = get_text(response).strip()

    print("\nClaim:")
    print(state["claim"])

    return state


# -----------------------------------------
# 3. Search the internet
# -----------------------------------------

def search_news(state):

    print("\nSearching web...")

    result = search.invoke({
        "query": state["claim"]
    })

    state["evidence"] = result.get("results", [])

    return state


# -----------------------------------------
# 4. Check the news
# -----------------------------------------

def check_news(state):

    evidence = ""

    for item in state["evidence"]:
        evidence += f"""
Title: {item.get("title")}
Content: {item.get("content")}
URL: {item.get("url")}
"""

    prompt = f"""
You are a fact checker.

Claim:
{state["claim"]}

Web evidence:
{evidence}

Decide:

TRUE = evidence supports the claim
FALSE = evidence contradicts the claim
UNCERTAIN = not enough evidence

Return JSON only:

{{
    "verdict": "TRUE",
    "explanation": "short explanation"
}}
"""

    response = llm.invoke(prompt)

    answer = get_text(response).strip()

    answer = answer.replace("```json", "")
    answer = answer.replace("```", "")

    try:
        data = json.loads(answer)

        state["verdict"] = data["verdict"]
        state["explanation"] = data["explanation"]

    except:
        state["verdict"] = "UNCERTAIN"
        state["explanation"] = "Could not understand the AI response."

    return state


# -----------------------------------------
# LangGraph
# -----------------------------------------

graph = StateGraph(dict)

graph.add_node("read_image", read_image)
graph.add_node("get_claim", get_claim)
graph.add_node("search_news", search_news)
graph.add_node("check_news", check_news)

graph.add_edge(START, "read_image")
graph.add_edge("read_image", "get_claim")
graph.add_edge("get_claim", "search_news")
graph.add_edge("search_news", "check_news")
graph.add_edge("check_news", END)

app = graph.compile()


# -----------------------------------------
# Main
# -----------------------------------------

def main():

    images = list(IMAGE_FOLDER.glob("*"))

    if not images:
        print("Put news screenshots inside the images folder.")
        return

    results = []

    for image in images:

        if image.suffix.lower() not in [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        ]:
            continue

        print("\n================================")
        print("Checking:", image.name)
        print("================================")

        state = create_state()

        state["image"] = str(image)

        result = app.invoke(state)

        print("\nRESULT")
        print("------")
        print("Verdict:", result["verdict"])
        print("Explanation:", result["explanation"])

        results.append({
            "image": image.name,
            "claim": result["claim"],
            "verdict": result["verdict"],
            "explanation": result["explanation"],
            "sources": [
                item.get("url")
                for item in result["evidence"]
            ]
        })

    with open(
        "results.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4
        )

    print("\nResults saved to results.json")


if __name__ == "__main__":
    main()
