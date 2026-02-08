# Contributing to Drug Interaction Checker

Thank you for your interest in contributing to the Drug Interaction Checker! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Set up the development environment
4. Create a new branch for your feature or fix

## How to Contribute

### Reporting Bugs

- Check if the bug has already been reported in Issues
- Include detailed steps to reproduce
- Provide system information (OS, Python version, etc.)
- Include error messages and stack traces

### Suggesting Features

- Check if the feature has been suggested before
- Clearly describe the feature and its benefits
- Provide examples of how it would work

### Improving Documentation

- Fix typos, clarify explanations
- Add examples and use cases
- Improve API documentation

### Adding Drug Data

- Follow the existing data format in `backend/data/drugs.json`
- Include proper citations and references
- Ensure medical accuracy (preferably reviewed by healthcare professionals)

### Code Contributions

We welcome:
- Bug fixes
- New features
- Performance improvements
- UI/UX enhancements
- Test coverage improvements

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

### Frontend

```bash
cd frontend
# Open index.html in a browser or use a local server
python -m http.server 3000
```

### Running Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app  # With coverage
```

## Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and small
- Maximum line length: 100 characters

Example:
```python
def check_interaction(drug1: str, drug2: str) -> Dict[str, Any]:
    """
    Check interaction between two drugs.
    
    Args:
        drug1: Name of the first drug
        drug2: Name of the second drug
    
    Returns:
        Dictionary containing interaction details
    """
    pass
```

### JavaScript (Frontend)

- Use ES6+ features
- Use consistent naming conventions
- Add comments for complex logic
- Keep functions pure when possible

### Code Formatting

Run these before committing:

```bash
# Python
black backend/app/
flake8 backend/app/

# JavaScript
# Use prettier or similar formatter
```

## Testing

### Writing Tests

- Write tests for new features
- Maintain or improve code coverage
- Include both unit and integration tests
- Test edge cases and error conditions

### Test Structure

```python
def test_feature_name():
    """Test description"""
    # Arrange
    setup_data = prepare_test_data()
    
    # Act
    result = function_to_test(setup_data)
    
    # Assert
    assert result == expected_outcome
```

## Submitting Changes

### Pull Request Process

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise commit messages
   - Keep commits logical and atomic
   - Include tests for new features

3. **Test your changes**
   ```bash
   pytest tests/
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**
   - Use a clear, descriptive title
   - Reference any related issues
   - Describe what changes you made and why
   - Include screenshots for UI changes

### Commit Message Guidelines

Format:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat: Add drug-food interaction checking

- Implement food interaction detection
- Add new API endpoint
- Update documentation

Closes #123
```

### Pull Request Checklist

Before submitting, ensure:

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New code has test coverage
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] Changes are focused and minimal

## Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged

## Medical Accuracy

**IMPORTANT**: For medical/drug-related contributions:

- Cite reputable sources
- Include PMID references when available
- Prefer peer-reviewed literature
- Have medical information reviewed when possible
- Use conservative severity ratings when uncertain

## Questions?

- Open an issue for questions
- Join our discussion forum
- Contact maintainers

## Recognition

Contributors will be acknowledged in:
- README.md
- Release notes
- Contributors page

Thank you for contributing to making medication management safer! 🙏
