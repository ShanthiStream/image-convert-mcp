# Contributing

Thank you for your interest in contributing to image-convert-mcp!

## Development Setup

1. Clone the repository:

```bash
git clone https://github.com/ShanthiStream/image-convert-mcp.git
cd image-convert-mcp
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:

```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Code Style

This project uses Ruff for linting:

```bash
ruff check .
ruff format .
```

## Making Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `python -m pytest tests/ -v`
5. Run linting: `ruff check .`
6. Commit: `git commit -m "feat: Add your feature"`
7. Push: `git push origin feature/your-feature`
8. Open a Pull Request

## Commit Messages

Use conventional commits:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring

## Pull Request Guidelines

- Include tests for new functionality
- Update documentation as needed
- Keep PRs focused on a single change
- Reference related issues

## Reporting Issues

Use GitHub Issues with the provided templates:

- **Bug Report**: For unexpected behavior
- **Feature Request**: For new functionality ideas

## Support

If you find this project useful, consider supporting its development:

<a href="https://buymeacoffee.com/shanthistream" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50">
</a>
