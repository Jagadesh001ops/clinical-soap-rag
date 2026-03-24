"""
Haystack component wrapper for Google Gemini 1.5 Pro.
Handles prompt submission and reply extraction.
"""

import os
import google.generativeai as genai
from haystack import component


@component
class GeminiGenerator:
    """
    Wraps the Gemini 1.5 Pro API as a Haystack generator component.
    Leverages the 1M-token context window for long clinical notes.
    """

    def __init__(self, model: str = "gemini-1.5-pro", max_output_tokens: int = 2048):
        self.model_name = model
        self.max_output_tokens = max_output_tokens
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name=model)

    @component.output_types(replies=list[str])
    def run(self, prompt: str) -> dict:
        generation_config = genai.GenerationConfig(
            max_output_tokens=self.max_output_tokens,
            temperature=0.2,  # Low temp for deterministic clinical output
        )
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config,
        )
        replies = [response.text] if response.text else []
        return {"replies": replies}
