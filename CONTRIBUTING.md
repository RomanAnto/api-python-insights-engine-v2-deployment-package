# Contributing to ML Deployment Package

Thank you for your interest in contributing to the ML Deployment Package! This document provides guidelines and instructions for contributing.

## 🎯 Ways to Contribute

- Report bugs and issues
- Suggest new features or improvements
- Improve documentation
- Submit code changes
- Add examples and tutorials
- Share deployment experiences

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Clear description** of the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs actual behavior
4. **Environment details**:
   - Python version
   - Operating system
   - AWS region
   - Relevant configuration
5. **Error messages** and logs
6. **Screenshots** if applicable

Use the GitHub issue template when available.

## 💡 Suggesting Features

When suggesting features:

1. Check if the feature already exists
2. Search existing issues to avoid duplicates
3. Provide a clear use case
4. Describe the expected behavior
5. Consider backward compatibility

## 📝 Code Contributions

### Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/ie-deployment.git
   cd ie-deployment
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Development Guidelines

#### Code Style

- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

Example:
```python
def deploy_model(config: DeploymentConfig, region: str = "eu-central-1") -> Dict[str, Any]:
    """
    Deploy ML model to SageMaker
    
    Args:
        config: Deployment configuration object
        region: AWS region for deployment
        
    Returns:
        Dictionary containing deployment information
        
    Raises:
        ValueError: If configuration is invalid
        RuntimeError: If deployment fails
    """
    pass
```

#### Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting
- Maintain code coverage above 70%

Run tests:
```bash
pytest tests/ -v --cov=deployment_package
```

#### Documentation

- Update README.md if adding user-facing features
- Add docstrings to all functions
- Update USER_GUIDE.md for major changes
- Add examples for new features

### Commit Messages

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

Examples:
```
feat(sagemaker): add support for multi-model endpoints

Add ability to deploy multiple model variants to a single endpoint
for A/B testing and canary deployments.

Closes #123
```

```
fix(lambda): handle timeout errors gracefully

Previously, Lambda timeout errors would crash the deployment.
Now they are caught and logged properly.

Fixes #456
```

### Pull Request Process

1. **Update your branch** with latest main:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests** and ensure they pass:
   ```bash
   pytest tests/ -v
   ```

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**:
   - Go to GitHub and create a PR
   - Fill out the PR template
   - Link related issues
   - Request review from maintainers

6. **Address review comments**:
   - Make requested changes
   - Push updates to your branch
   - PR will automatically update

7. **Merge**:
   - Maintainers will merge once approved
   - Delete your feature branch after merge

### PR Review Checklist

Before submitting, ensure:

- [ ] Code follows style guidelines
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts with main
- [ ] PR description is clear and complete

## 📚 Documentation Contributions

Documentation improvements are always welcome!

- Fix typos and grammar
- Improve clarity and readability
- Add examples and tutorials
- Update outdated information
- Translate documentation

To contribute docs:

1. Edit markdown files in `docs/` directory
2. Test rendering locally (if possible)
3. Submit PR with clear description

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_config.py -v

# Run with coverage
pytest tests/ --cov=deployment_package --cov-report=html

# Run integration tests
pytest tests/integration/ -v
```

### Writing Tests

Place tests in `tests/` directory:

```python
import pytest
from deployment_package.config import DeploymentConfig

def test_config_creation():
    """Test configuration object creation"""
    config = DeploymentConfig(
        name="test-model",
        type="sagemaker"
    )
    assert config.name == "test-model"
    assert config.type == "sagemaker"

def test_config_validation():
    """Test configuration validation"""
    with pytest.raises(ValueError):
        DeploymentConfig(name="", type="sagemaker")
```

## 🔍 Code Review Guidelines

When reviewing PRs:

- Be respectful and constructive
- Focus on code, not the person
- Explain the reasoning behind suggestions
- Approve when ready or request changes
- Test the changes locally if possible

## 🎨 Design Principles

When contributing, keep these principles in mind:

1. **User-Friendly**: Make it easy for data scientists to use
2. **Production-Ready**: Security, monitoring, and reliability first
3. **Modular**: Keep components independent and reusable
4. **Well-Documented**: Code should be self-explanatory
5. **Tested**: All functionality should have tests
6. **Cost-Conscious**: Optimize for cost efficiency

## 📞 Getting Help

Need help contributing?

- Check the [USER_GUIDE.md](docs/USER_GUIDE.md)
- Read the [IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)
- Ask questions in GitHub discussions
- Contact: insight-engine-team@syngenta.com
- Slack: #insight-engine-support

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:

- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing! 🎉

---

*Syngenta Digital - Insight Engine Team*
