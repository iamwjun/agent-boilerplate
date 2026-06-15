# Repository Guidelines

## Project Structure & Module Organization
This repository is a multi-service agent boilerplate. Runtime services live under `services/`: `agent-core-service` exposes the FastAPI chat API, `rag-search-service` handles retrieval and reranking, and `data-pipeline-job` prepares documents. Shared code belongs in `libs/`, currently `agent-security-sdk` and protobuf definitions in `agent-common-proto`. Deployment assets are split between `docker-compose.yml`, service `Dockerfile`s, Helm charts in `charts/`, Nginx/web assets in `web/`, and environment templates under `config/`. Architecture notes belong in `docs/`.

## Build, Test, and Development Commands
- `docker compose up --build`: build and run Elasticsearch, Redis, the API services, and web container locally.
- `docker compose down`: stop the local stack while keeping named volumes.
- `pip install -r services/agent-core-service/requirements.txt`: install dependencies for one service; repeat with the matching path as needed.
- `cd services/agent-core-service && python src/main.py`: run the core API locally on port `8000`.
- `cd services/rag-search-service && python main.py`: run the search service locally on port `8010`.
- `cd services/data-pipeline-job && python src/job_scheduler.py`: execute the sample ingestion pipeline.

## Coding Style & Naming Conventions
Use Python 3 with 4-space indentation, typed Pydantic models, and FastAPI route functions named by action, such as `chat_stream_endpoint` or `search_endpoint`. Keep service-local modules inside each service’s `src/` package, and use snake_case for Python files, functions, and variables. Prefer environment variables already used in Compose, such as `OPENAI_API_KEY`, `REDIS_URL`, and `ES_HOST`. Do not commit caches, virtual environments, or secrets.

## Testing Guidelines
No automated tests are currently committed. Add tests under a service-local `tests/` directory, for example `services/agent-core-service/tests/test_health.py`, and use `pytest` naming conventions (`test_*.py`, `test_*` functions). Focus coverage on FastAPI endpoints, Elasticsearch/Redis boundaries, document transformation, masking, and guardrail behavior. When tests are added, document the exact command here.

## Commit & Pull Request Guidelines
Recent history uses concise Conventional Commit-style prefixes: `feat:`, `chore:`, and `docs:`. Continue that pattern, for example `feat: add search health probe` or `docs: update deployment notes`. Pull requests should include a short purpose statement, affected services or charts, local commands run, and any configuration changes. Include screenshots only for web UI changes, and link related issues when available.

## Security & Configuration Tips
Keep production secrets out of `config/` and `.env` files committed to Git. Treat `docker-compose.yml` defaults as development-only; Elasticsearch security is disabled there and must be enabled for production. Review CORS, model endpoints, and tenant-specific data handling before deploying changes.
