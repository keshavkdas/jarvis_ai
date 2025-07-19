import os
import requests # type: ignore
from dotenv import load_dotenv # type: ignore

def google_search_fallback(query):
    load_dotenv()
    serp_api_key = os.getenv("SERPAPI_KEY")
    params = {
        "engine": "google",
        "q": query,
        "api_key": serp_api_key
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()

        # Try to extract short answer
        if "answer_box" in data:
            box = data["answer_box"]
            if "answer" in box:
                return clean_text(box["answer"])
            if "snippet" in box:
                return clean_text(box["snippet"])
            if "highlighted_words" in box:
                return clean_text(", ".join(box["highlighted_words"]))

        # Try to extract weather from organic results
        if "organic_results" in data:
            for result in data["organic_results"]:
                snippet = result.get("snippet", "")
                if "°C" in snippet or "°F" in snippet or "humidity" in snippet:
                    return clean_text(snippet.split("Forecast")[0].strip())

        # Fall back to first snippet
        if data.get("organic_results"):
            return clean_text(data["organic_results"][0].get("snippet", ""))

        return "Sorry, I couldn't find a reliable answer."

    except Exception as e:
        print("[SerpAPI ERROR]:", e)
        return "Error fetching data."

def clean_text(text: str) -> str:
    """Remove asterisks and trim long endings."""
    text = text.replace("*", "")
    lines = text.strip().split("\n")
    short_lines = [line for line in lines if any(x in line for x in ["°C", "°F", "Clear", "Humidity", "Rain", "Cloud", "Wind"])]
    return ", ".join(short_lines[:3]) or text[:150]
