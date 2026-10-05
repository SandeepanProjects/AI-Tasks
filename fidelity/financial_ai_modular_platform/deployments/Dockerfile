FROM python:3.12-slim
WORKDIR /workspace
COPY . .
RUN pip install --no-cache-dir fastapi uvicorn pydantic sqlalchemy asyncpg redis celery
ENV PYTHONPATH=/workspace/packages/platform-core/src:/workspace/packages/platform-auth/src:/workspace/packages/platform-observability/src:/workspace/packages/ai-llm/src:/workspace/packages/ai-rag/src:/workspace/packages/ai-agents/src:/workspace/packages/ai-guardrails/src
CMD ["uvicorn", "financial_compliance.main:app", "--host", "0.0.0.0", "--port", "8000"]
