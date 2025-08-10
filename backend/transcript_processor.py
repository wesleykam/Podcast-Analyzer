import os
from pydantic import BaseModel
from groq import Groq
from openai import OpenAI


class ActionableInsight(BaseModel):
    header: str
    detail: str

class TranscriptAnalysis(BaseModel):
    summary: list[str]
    mentioned_organizations: list[str]
    actionable_insights: list[ActionableInsight]


class TranscriptProcessor:
    def __init__(self):
        # Uncomment to enable Groq processing
        # self.groq_client = Groq(
        #     api_key=os.environ.get("GROQ_API_KEY"),
        # )
        self.openai_client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        
        self.prompt = (
                "You are a healthcare technology analyst. Given the following transcript from a health tech podcast, perform the following tasks:\n\n"
                "1. Generate a concise list of 3 key takeaways that capture the key points or themes discussed in the episode.\n\n"
                "2. Extract and list all healthcare organizations, companies, and technologies that are mentioned, including startups, hospital systems, software platforms, devices, and standards (e.g., Epic, Mayo Clinic, HL7, AI triage tools).\n\n"
                "3. Identify a list of 2-3 actionable insights or strategic recommendations for healthcare IT leaders based on the discussion. These should be practical takeaways they can apply to improve digital transformation, data strategy, cybersecurity, patient experience, or operational efficiency.\n"
                "   - For each actionable insight, include a short, descriptive header that summarizes the main point, followed by a brief explanation.\n\n"
                "Format your response in JSON format:\n\n"
                "{\n"
                '    "summary": ["...", "...", "..."],\n'
                '    "mentioned_organizations": ["...", "..."],\n'
                '    "actionable_insights": [\n'
                '        {\n'
                '            "header": "...",\n'
                '            "detail": "..." \n'
                '        },\n'
                '        {\n'
                '            "header": "...",\n'
                '            "detail": "..." \n'
                '        }\n'
                '    ]\n'
                "}"
            )

    def process_with_groq(self, transcript: str):
        """
        Process the transcript using the Groq API.

        WARNING: Groq API does not guarantee json model output. It only errors out when json is not outputted.
        """
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"{self.prompt}\n\nTranscript:\n{transcript}",
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "transcript_analysis",
                        "schema": TranscriptAnalysis.model_json_schema(),
                    },
                },
                model="openai/gpt-oss-20b",
            )

            return chat_completion.choices[0].message.content

        except Exception as e:
            return {"error": str(e)}

    def process_with_openai(self, transcript: str):
        """
        Process the transcript using the OpenAI API.
        """
        try:
            response = self.openai_client.responses.parse(
                model="gpt-4o-mini",
                input=[
                    # Prioritize Prompt Instruction
                    {"role": "developer", "content": f"{self.prompt}"},
                    # User Provides Transcript
                    {"role": "user", "content": f"Transcript:\n\n{transcript}"},
                ],
                text_format=TranscriptAnalysis,
            )

            response_model = response.output_parsed
            response_str = response_model.model_dump_json(indent=4)

            return response_str

        except Exception as e:
            return {"error": str(e)}
