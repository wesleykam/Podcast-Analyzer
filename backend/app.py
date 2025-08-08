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


app = Flask(__name__)
CORS(app)

# Initialize TranscriptProcessor
transcript_processor = TranscriptProcessor()


@app.route("/analyze-url", methods=["POST"])
def analyze_url():
    data = request.json
    url = data.get("url", "")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    try:
        driver.get(url)

        # Example: Scrape transcript based on class name (adjust as needed)
        transcript_elements = driver.find_elements(
            By.CLASS_NAME, "cfm-transcript-content"
        )
        transcript = " ".join([element.text for element in transcript_elements])

        if not transcript:
            return jsonify({"error": "Transcript not found on the page"}), 404

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
        # Process the text
        result = transcript_processor.process_with_openai(text)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
