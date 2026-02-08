# Contributing to Image Convert MCP Server

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ShanthiStream/image-convert-mcp.git
   cd image-convert-mcp
   ```

2. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Run tests**
   ```bash
   python -m pytest tests/ -v
   ```

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Add docstrings for all public functions and classes
- Keep functions focused and single-purpose

## Testing

- Write tests for all new features
- Ensure all tests pass before submitting PR
- Aim for high code coverage
- Test both success and error cases

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure everything works
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Commit Message Guidelines

Use clear, descriptive commit messages:
- `feat: Add support for JPEG XL format`
- `fix: Handle corrupted image files gracefully`
- `docs: Update README with new examples`
- `test: Add tests for validation functions`
- `refactor: Simplify image loading logic`

## Areas for Contribution

### High Priority
- [ ] Support for additional formats (JPEG XL, HEIC)
- [ ] Metadata preservation options
- [ ] Progress callbacks for long operations
- [ ] Performance optimizations

### Medium Priority
- [ ] Caching mechanism for frequently converted images
- [ ] CLI interface for easier direct usage
- [ ] Configuration file support
- [ ] Better error messages

### Low Priority
- [ ] Web UI for the MCP server
- [ ] Conversion presets (thumbnail, web, print)
- [ ] Batch operation queuing

## Questions?

Feel free to open an issue for any questions or suggestions!
