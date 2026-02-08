# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2026-02-08

### Added
- **CLI Interface**: Full command-line support with `image-convert` command
- **Presets**: 8 built-in presets (web, thumbnail, social, hd, 4k, archive, lossless, max-compression)
- **Compression Statistics**: `--stats` flag shows detailed savings information
- **Documentation Site**: MkDocs Material documentation with auto-deploy to GitHub Pages
- Tests for presets and stats modules (34 total tests)

### Changed
- Version bumped to 0.3.0
- README updated with CLI documentation and presets table
- Enhanced tool descriptions for better AI agent compatibility

## [0.2.0] - 2026-02-08

### Added
- MCP manifest file (`mcp.json`) for registry submissions
- Agent guide (`AGENT_GUIDE.md`) for AI agent usage
- CI/CD workflow for automated testing
- GitHub issue and PR templates
- Buy Me Coffee support badges

### Changed
- Enhanced tool descriptions with agent-friendly patterns
- Updated pyproject.toml with PyPI metadata

## [0.1.0] - Initial Release

### Added
- WebP and AVIF conversion support
- Single file and batch processing
- Parallel processing with configurable workers
- Docker support
- MCP server with stdio and SSE transports
