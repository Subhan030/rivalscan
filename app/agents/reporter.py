from typing import cast
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from app.config import settings
from app.prompts import REPORTER_PROMPT

class ReporterOutput(BaseModel):
    executive_summary: str = Field(description="The final executive summary of the report.")
    key_findings: list[str] = Field(description="Bullet points of key findings.")
    next_steps: list[str] = Field(description="Recommended next steps.")

def get_reporter_llm():
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is not set")
    return ChatGroq(temperature=0.3, model="llama-3.3-70b-versatile", api_key=settings.groq_api_key) 

def run_reporter(all_data: str) -> ReporterOutput:
    try:
        llm = get_reporter_llm()
        structured_llm = llm.with_structured_output(ReporterOutput)
        
        prompt = REPORTER_PROMPT.format(
            all_data=all_data
        )
        
        return cast(ReporterOutput, structured_llm.invoke(prompt))
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Reporter failed: {e}")
        return ReporterOutput(executive_summary="Error generating report.", key_findings=[], next_steps=[])
