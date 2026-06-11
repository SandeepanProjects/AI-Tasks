from app.rag.generation.prompt_builder import PromptBuilder
from app.rag.generation.llm_client import LLMClient
from app.rag.generation.guardrails import Guardrails


class RAGGenerator:

    def __init__(self):

        self.llm = LLMClient()

    def generate(self, question: str, context: str, sources: list):

        # Step 1: Build prompt
        prompt = PromptBuilder.build(
            question,
            context
        )

        # Step 2: Call LLM
        raw_output = self.llm.generate(prompt)

        # Step 3: Guardrails check
        violations = Guardrails.validate(raw_output)

        # Step 4: Risk classification
        risk_level = self._infer_risk(raw_output)

        return {
            "question": question,
            "answer": raw_output,
            "risk_level": risk_level,
            "compliance_violations": violations,
            "sources": sources
        }

    def _infer_risk(self, text: str):

        text = text.lower()

        if "high volatility" in text:
            return "High"

        if "moderate" in text:
            return "Medium"

        return "Low"