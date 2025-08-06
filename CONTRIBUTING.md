# Contributing to Courzly

We welcome contributions to the Courzly Dynamic Agent Platform! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/courzly.git
   cd courzly
   ```

2. **Environment Setup**
   ```bash
   # Install dependencies
   npm install
   pip install -r requirements.txt
   
   # Start development environment
   docker-compose up -d
   ```

3. **Branch Strategy**
   - `main`: Production-ready code
   - `develop`: Integration branch for features
   - `feature/*`: Individual feature development
   - `hotfix/*`: Critical bug fixes

## Code Standards

### Python (Backend/CLI)
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write docstrings for all public methods
- Run `black` and `isort` for formatting
- Maintain test coverage above 80%

### JavaScript/TypeScript (Frontend)
- Use ESLint and Prettier for formatting
- Follow React best practices
- Write unit tests for components
- Use TypeScript for type safety

### Docker and Infrastructure
- Use multi-stage builds for optimization
- Include health checks in all services
- Document environment variables
- Follow security best practices

## Commit Guidelines

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(api): add course creation endpoint`
- `fix(frontend): resolve approval workflow bug`
- `docs(readme): update installation instructions`

## Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   npm test
   python -m pytest
   ```

4. **Submit Pull Request**
   - Provide clear description of changes
   - Reference related issues
   - Ensure CI passes
   - Request review from maintainers

## Issue Reporting

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, versions)
- Relevant logs or error messages

## Feature Requests

For new features:
- Check existing issues first
- Provide detailed use case
- Consider implementation approach
- Discuss with maintainers before starting

## Code Review Process

All submissions require review:
- Automated tests must pass
- Code follows style guidelines
- Documentation is updated
- Security considerations addressed
- Performance impact evaluated

## Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Focus on constructive feedback
- Follow the code of conduct

Thank you for contributing to Courzly!