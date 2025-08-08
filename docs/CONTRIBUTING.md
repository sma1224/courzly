# Contributing to Courzly

## Welcome Contributors!

Thank you for your interest in contributing to Courzly! This guide will help you get started with contributing to our AI-powered course creation platform.

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### Local Development
```bash
# Clone repository
git clone https://github.com/sma1224/courzly.git
cd courzly

# Setup environment
cp .env.example .env
# Edit .env with your local settings

# Start development environment
docker-compose up -d

# Install backend dependencies
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install frontend dependencies
cd ../frontend
npm install

# Run tests
cd ..
./scripts/test.sh
```

## Code Standards

### Python (Backend)
- **Style**: Black formatter, isort for imports
- **Linting**: flake8, mypy for type checking
- **Testing**: pytest with 80%+ coverage
- **Documentation**: Google-style docstrings

```python
def create_workflow(title: str, config: Dict[str, Any]) -> Workflow:
    """Create a new course workflow.
    
    Args:
        title: The course title
        config: Workflow configuration parameters
        
    Returns:
        Created workflow instance
        
    Raises:
        ValidationError: If title is empty or config is invalid
    """
    pass
```

### TypeScript (Frontend)
- **Style**: Prettier formatter, ESLint
- **Types**: Strict TypeScript configuration
- **Testing**: Jest + React Testing Library
- **Components**: Functional components with hooks

```typescript
interface WorkflowProps {
  workflow: Workflow;
  onUpdate: (workflow: Workflow) => void;
}

const WorkflowCard: React.FC<WorkflowProps> = ({ workflow, onUpdate }) => {
  // Component implementation
};
```

### Git Workflow
- **Branches**: Feature branches from `main`
- **Commits**: Conventional commit messages
- **PRs**: Required for all changes
- **Reviews**: At least one approval required

```bash
# Branch naming
feature/add-export-functionality
bugfix/fix-websocket-connection
hotfix/security-patch

# Commit messages
feat: add PDF export functionality
fix: resolve WebSocket connection issues
docs: update API documentation
test: add integration tests for workflows
```

## Testing Guidelines

### Backend Testing
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# E2E tests
pytest tests/e2e/ -v --slow

# Coverage report
pytest --cov=. --cov-report=html
```

### Frontend Testing
```bash
# Unit tests
npm test

# Coverage
npm test -- --coverage

# E2E tests (if implemented)
npm run test:e2e
```

### Test Requirements
- **Unit Tests**: All new functions/components
- **Integration Tests**: API endpoints and workflows
- **E2E Tests**: Critical user journeys
- **Coverage**: Maintain 80%+ code coverage

## Pull Request Process

### Before Submitting
1. **Run Tests**: Ensure all tests pass
2. **Code Quality**: Run linters and formatters
3. **Documentation**: Update relevant docs
4. **Changelog**: Add entry if user-facing change

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
```

### Review Process
1. **Automated Checks**: CI/CD pipeline must pass
2. **Code Review**: At least one maintainer approval
3. **Testing**: Reviewer tests functionality
4. **Merge**: Squash and merge to main

## Issue Guidelines

### Bug Reports
```markdown
**Bug Description**
Clear description of the issue

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior**
What should happen

**Screenshots**
If applicable

**Environment**
- OS: [e.g. Ubuntu 24.04]
- Browser: [e.g. Chrome 120]
- Version: [e.g. 1.0.0]
```

### Feature Requests
```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this work?

**Alternatives**
Other solutions considered

**Additional Context**
Any other relevant information
```

## Development Guidelines

### API Development
- **RESTful Design**: Follow REST principles
- **Error Handling**: Consistent error responses
- **Validation**: Pydantic models for all inputs
- **Documentation**: OpenAPI/Swagger docs
- **Testing**: Comprehensive endpoint testing

### Frontend Development
- **Component Design**: Reusable, composable components
- **State Management**: React Query for server state
- **Accessibility**: WCAG 2.1 AA compliance
- **Performance**: Lazy loading, code splitting
- **Testing**: Component and integration tests

### Database Changes
- **Migrations**: Alembic migrations for schema changes
- **Indexing**: Proper indexes for query performance
- **Constraints**: Foreign keys and data validation
- **Backup**: Consider backup/restore impact
- **Testing**: Test migrations up and down

## Security Guidelines

### Code Security
- **Input Validation**: Validate all user inputs
- **SQL Injection**: Use parameterized queries
- **XSS Prevention**: Sanitize outputs
- **Authentication**: Secure token handling
- **Authorization**: Proper permission checks

### Dependency Management
- **Updates**: Regular dependency updates
- **Vulnerabilities**: Monitor security advisories
- **Pinning**: Pin dependency versions
- **Auditing**: Regular security audits

### Secrets Management
- **Environment Variables**: Never commit secrets
- **API Keys**: Secure key storage
- **Passwords**: Strong password requirements
- **Encryption**: Encrypt sensitive data

## Performance Guidelines

### Backend Performance
- **Database**: Optimize queries and indexes
- **Caching**: Use Redis for frequently accessed data
- **Async**: Use async/await for I/O operations
- **Monitoring**: Track response times and errors

### Frontend Performance
- **Bundle Size**: Monitor and optimize bundle size
- **Lazy Loading**: Load components on demand
- **Caching**: Cache API responses appropriately
- **Images**: Optimize image sizes and formats

## Documentation

### Code Documentation
- **Docstrings**: All public functions and classes
- **Comments**: Complex logic explanation
- **Type Hints**: Full type annotations
- **Examples**: Usage examples in docstrings

### User Documentation
- **API Docs**: Keep OpenAPI specs updated
- **User Manual**: Update for new features
- **Deployment**: Update deployment guides
- **Changelog**: Document all changes

## Community

### Communication
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Email**: security@courzly.com for security issues

### Code of Conduct
- **Respectful**: Be respectful and inclusive
- **Constructive**: Provide constructive feedback
- **Collaborative**: Work together towards common goals
- **Professional**: Maintain professional standards

## Release Process

### Version Numbering
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Breaking Changes**: Increment major version
- **New Features**: Increment minor version
- **Bug Fixes**: Increment patch version

### Release Checklist
1. **Testing**: All tests pass
2. **Documentation**: Docs updated
3. **Changelog**: Release notes prepared
4. **Deployment**: Staging deployment tested
5. **Tagging**: Git tag created
6. **Production**: Production deployment
7. **Monitoring**: Post-deployment monitoring

## Getting Help

### Resources
- **Documentation**: Check existing docs first
- **Issues**: Search existing issues
- **Discussions**: Community discussions
- **Code**: Review existing code examples

### Contact
- **Maintainers**: @sma1224
- **Security**: security@courzly.com
- **General**: Open a GitHub discussion

Thank you for contributing to Courzly! 🚀