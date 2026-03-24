"""
RAG pipeline using Haystack 2.x + Gemini 1.5 Pro.
Processes clinical notes → structured SOAP summaries.
"""

from haystack import Pipeline
from haystack.components.builders import PromptBuilder

from app.pipeline.retriever import PgVectorRetriever
from app.pipeline.gemini_node import GeminiGenerator
from app.pipeline.validator import SoapValidator

SOAP_PROMPT_TEMPLATE = """
You are a clinical documentation specialist. Using the retrieved clinical note
excerpts below, generate a structured SOAP note summary.

--- Retrieved Clinical Context ---
{% for doc in documents %}
{{ doc.content }}
{% endfor %}
---------------------------------

Patient Note to Summarize:
{{ note_text }}

Generate a SOAP note with the following sections:
- **Subjective**: Patient-reported symptoms, history, chief complaint
- **Objective**: Vitals, exam findings, lab/imaging results
- **Assessment**: Clinical diagnosis or differential with ICD-10 codes
- **Plan**: Treatment, medications, follow-up, referrals

Return ONLY valid JSON matching this schema:
{
  "subjective": "...",
  "objective": "...",
  "assessment": "...",
  "plan": "..."
}
"""


def build_soap_pipeline(document_store) -> Pipeline:
    """
    Construct and connect the full Haystack SOAP generation pipeline.

    Components:
        retriever      → fetches similar notes from pgvector store
        prompt_builder → formats the prompt template
        llm            → Gemini 1.5 Pro generation
        validator      → multi-step completeness + coherence checks
    """
    retriever = PgVectorRetriever(document_store=document_store, top_k=5)
    prompt_builder = PromptBuilder(template=SOAP_PROMPT_TEMPLATE)
    llm = GeminiGenerator(model="gemini-1.5-pro")
    validator = SoapValidator()

    pipeline = Pipeline()
    pipeline.add_component("retriever", retriever)
    pipeline.add_component("prompt_builder", prompt_builder)
    pipeline.add_component("llm", llm)
    pipeline.add_component("validator", validator)

    pipeline.connect("retriever.documents", "prompt_builder.documents")
    pipeline.connect("prompt_builder.prompt", "llm.prompt")
    pipeline.connect("llm.replies", "validator.replies")

    return pipeline


def run_soap_pipeline(pipeline: Pipeline, note_text: str) -> dict:
    """
    Run the pipeline for a given clinical note.

    Returns validated SOAP dict:
        { subjective, objective, assessment, plan, validation_status }
    """
    result = pipeline.run({
        "retriever": {"query": note_text},
        "prompt_builder": {"note_text": note_text},
    })
    return result["validator"]["soap"]
