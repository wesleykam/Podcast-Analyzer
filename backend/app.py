import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from groq import Groq

from pydantic import BaseModel


app = Flask(__name__)
CORS(app)

# Initialize Groq API
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

@app.route('/analyze-url', methods=['POST'])
def analyze_url():
    data = request.json
    url = data.get('url', '')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)

        # Example: Scrape transcript based on class name (adjust as needed)
        transcript_elements = driver.find_elements(By.CLASS_NAME, 'cfm-transcript-content')
        transcript = " ".join([element.text for element in transcript_elements])

        if not transcript:
            return jsonify({"error": "Transcript not found on the page"}), 404

        # Process the transcript
        result = process_transcript_with_groq(transcript)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        driver.quit()

@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "Text is required"}), 400

    try:
        # Process the text
        result = process_transcript_with_groq(text)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


class TranscriptAnalysis(BaseModel):
    summary: list[str]
    mentioned_organizations: list[str]
    actionable_insights: list[str]


def process_transcript_with_groq(transcript):
    prompt = (
        "You are a healthcare technology analyst. Given the following transcript from a health tech podcast, perform the following tasks:\n\n"
        "1. Generate a concise list of 3 key takeaways that captures the key points or themes discussed in the episode.\n\n"
        "2. Extract and list all healthcare organizations, companies, and technologies that are mentioned, including startups, hospital systems, software platforms, devices, and standards (e.g., Epic, Mayo Clinic, HL7, AI triage tools).\n\n"
        "3. Identify a list of 2-3 actionable insights or strategic recommendations for healthcare IT leaders based on the discussion. These should be practical takeaways they can apply to improve digital transformation, data strategy, cybersecurity, patient experience, or operational efficiency.\n\n"
        "Format your response in JSON format:\n\n"
        "{\n"
        "    \"summary\": [\"...\", \"...\", \"...\"],\n"
        "    \"mentioned_organizations\": [\"...\", \"...\"],\n"
        "    \"actionable_insights\": [\"...\", \"...\"]\n"
    "}"
)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}\n\nTranscript:\n{transcript}",
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "transcript_analysis",
                    "schema": TranscriptAnalysis.model_json_schema()
                }
            },
            model="openai/gpt-oss-20b",
        )
        
        return chat_completion.choices[0].message.content

    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
