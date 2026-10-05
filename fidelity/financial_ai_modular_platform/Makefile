PYTHON ?= python

install:
	$(PYTHON) -m pip install -e packages/platform-core
	$(PYTHON) -m pip install -e packages/platform-auth
	$(PYTHON) -m pip install -e packages/platform-db
	$(PYTHON) -m pip install -e packages/platform-cache
	$(PYTHON) -m pip install -e packages/platform-messaging
	$(PYTHON) -m pip install -e packages/platform-observability
	$(PYTHON) -m pip install -e packages/ai-llm
	$(PYTHON) -m pip install -e packages/ai-rag
	$(PYTHON) -m pip install -e packages/ai-agents
	$(PYTHON) -m pip install -e packages/ai-guardrails
	$(PYTHON) -m pip install -e applications/financial-compliance
	$(PYTHON) -m pip install -e applications/investment-intelligence
	$(PYTHON) -m pip install pytest pytest-asyncio httpx ruff

test:
	pytest -q

lint:
	ruff check packages applications tests

run-compliance:
	uvicorn financial_compliance.main:app --reload --port 8001

run-investment:
	uvicorn investment_intelligence.main:app --reload --port 8002

docker-up:
	docker compose -f deployments/docker-compose.yml up --build

docker-down:
	docker compose -f deployments/docker-compose.yml down
