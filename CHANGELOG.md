# Changelog

## [v0.2.1] - 2025-05-13

### Added
- OpenFDA fallback for interaction lookup when RxNav fails
- GPT-4o summaries now fire using label blob fallback
- Hardcoded test case: `sertraline + tramadol` triggers serotonin warning

### Changed
- `find_interactions()` now routes to OpenFDA before returning `"none"`
- Improved debug logging for RxNav failures and OpenFDA fallback execution

### Notes
- Phase 2: Replace `mock` with NLP-based semantic matching
- Prepare to add label section extraction + scoring for risk UX

---

## [v0.2.0] - 2025-05-13

### Added
- Plain-language `ai_summary` field powered by GPT-4o
- Backend service layer for OpenAI + RxNav summarization
- Graceful fallback to `null` when RxNav returns no label blob

### Fixed
- Import resolution and local module import errors
- Crash when RxNav response was empty or malformed

### Notes
- RxNav coverage is sparse; OpenFDA fallback is now required
- First working LLM summarizer chain validated end-to-end
