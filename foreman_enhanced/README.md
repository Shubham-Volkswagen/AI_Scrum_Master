# Foreman Enhanced

End-to-end Streamlit + CrewAI prototype for the i.mobilithon Foreman challenge.

## Capabilities
- TXT, PDF, DOCX and raw-text intake
- CrewAI-assisted Epic -> Feature -> Story/Task backlog generation
- Structured clarification and human review
- Excel synthetic-dataset loading
- Existing-board health checks
- Dependency validation, cycle detection and dependency-safe ordering
- Holiday-adjusted capacity and sprint planning
- Semantic/fuzzy duplicate detection
- Mid-sprint change recommendation with explicit confirmation
- JSON/CSV exports
- Human-triggered Jira publishing with local-to-Jira key mapping

## Setup
1. Copy `.env.example` to `.env` and fill the values you use.
2. Install Python 3.11+.
3. Run `pip install -e .`
4. Start with `streamlit run app.py`

The deterministic board-health and planning features work without an LLM key. CrewAI backlog generation requires `GEMINI_API_KEY`. Jira publishing requires the Jira variables.

Important: The application ignores the workbook `AnswerKey` sheet. It finds issues using joins, graph checks and similarity logic.
