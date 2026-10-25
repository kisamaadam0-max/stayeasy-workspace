# Tools

Scripts Codex writes to collect or clean research data. One script per data source, with a short header comment: what it collects, from where, and the terms that allow it.

- Read credentials from environment variables only. Never commit them.
- Write output to `research/data/` with `source` and `collected_at` columns.
- Respect the collection rules in `AGENTS.md` (official APIs, public pages within their terms, files Adam provides).
