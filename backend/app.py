import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from groq import Groq
from openai import OpenAI

from pydantic import BaseModel
from transcript_processor import TranscriptProcessor
from transcript_scraper import TranscriptScraper


app = Flask(__name__)
CORS(app)

# Initialize Processor & Scraper
transcript_processor = TranscriptProcessor()
scraper = TranscriptScraper(strip_timestamps=True)


@app.route("/analyze-url", methods=["POST"])
def analyze_url():
    data = request.json
    url = data.get("url", "")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    driver = scraper.new_driver()

    try:
        driver.get(url)

        # Use the OOP scraper (tries basic first, then iframe-in-new-tab)
        transcript = scraper.extract(driver)

        if not transcript:
            return (
                jsonify(
                    {
                        "error": "Transcript not found on the page. Please check the URL or try another source."
                    }
                ),
                404,
            )

        # Process the transcript
        result = transcript_processor.process_with_openai(transcript)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        driver.quit()


@app.route("/analyze-text", methods=["POST"])
def analyze_text():
    data = request.json
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "Text is required"}), 400

    try:
        result = transcript_processor.process_with_openai(text)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Bind to 0.0.0.0 for container use; change port if needed
    app.run(host="0.0.0.0", port=5000)
