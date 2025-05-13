# Changelog

## [v0.2.0] - 2025-05-13
### Added
- Plain-language `ai_summary` field powered by GPT-4o
- Backend service layer for OpenAI + RxNav summarization
- Auto-fallback to `null` when RxNav returns no label blob

### Fixed
- Import issues and module resolution path errors
- Graceful handling of RxNav 404 / empty cases

### Notes
- RxNav API found unreliable for many real-world drug interactions
- MVP LLM summarization chain validated, ready to extend via OpenFDA label fallback
