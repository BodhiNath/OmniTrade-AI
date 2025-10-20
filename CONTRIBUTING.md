# Contributing to OmniTrade AI

First off, thank you for considering contributing to OmniTrade AI! It's people like you that make this project better for everyone.

## Important Notice

**⚠️ This software handles real money trading. All contributions must prioritize:**
1. Security
2. Reliability  
3. Safety
4. Compliance

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code.

---

## How Can I Contribute?

### Reporting Bugs

**Before Submitting**:
- Check existing issues to avoid duplicates
- Collect relevant information (logs, screenshots, config)

**Bug Report Should Include**:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Log excerpts (remove sensitive data!)

**Security Vulnerabilities**: See SECURITY.md - DO NOT open public issues

### Suggesting Enhancements

**Enhancement Proposals Should Include**:
- Clear use case
- Expected behavior
- Why it benefits users
- Potential implementation approach

### Pull Requests

**Before Starting**:
1. Open an issue to discuss major changes
2. Check no one else is working on it
3. Fork the repository
4. Create a feature branch

**PR Requirements**:
- [ ] Code follows project style
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests passing
- [ ] No security vulnerabilities introduced
- [ ] Commit messages are clear

**PR Process**:
1. Update README.md if needed
2. Update CHANGELOG.md
3. Ensure CI/CD passes
4. Request review
5. Address feedback
6. Squash commits if requested

---

## Development Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (for frontend)
- Git

### Local Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/omnitrade-ai.git
cd omnitrade-ai

# Create environment file
cp .env.example .env
nano .env  # Add your API keys

# Start services
docker-compose up -d

# Install Python dependencies
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Install frontend dependencies
cd ../frontend
pnpm install

# Run tests
cd ../backend
pytest tests/ -v
```

### Testing

**Always Test With Paper Trading First!**

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests (when implemented)
cd frontend
pnpm test

# Integration tests
pytest tests/integration/ -v

# Linting
ruff check backend/app
eslint frontend/src
```

---

## Coding Standards

### Python (Backend)

**Style**: PEP 8 with Black formatting

```python
# Good
def calculate_position_size(
    entry_price: Decimal,
    stop_loss: Decimal,
    risk_amount: Decimal
) -> Decimal:
    """Calculate position size based on risk.
    
    Args:
        entry_price: Planned entry price
        stop_loss: Stop loss price
        risk_amount: Amount to risk in dollars
        
    Returns:
        Position size in base currency
    """
    price_risk = abs(entry_price - stop_loss)
    return risk_amount / price_risk

# Bad
def calc_size(e, s, r):
    return r / abs(e - s)
```

**Key Principles**:
- Type hints everywhere
- Docstrings for all public functions
- Descriptive variable names
- Error handling with specific exceptions
- Logging for important events
- No magic numbers (use constants)

### JavaScript/React (Frontend)

**Style**: ESLint + Prettier

```javascript
// Good
const TradingDashboard = () => {
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchPositions();
  }, []);
  
  return (
    <div className="dashboard">
      {loading ? <Spinner /> : <PositionsList positions={positions} />}
    </div>
  );
};

// Bad
const dash = () => {
  let p = [];
  // Missing error handling, unclear naming
}
```

### Commit Messages

**Format**: `type(scope): subject`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples**:
```
feat(risk): Add trailing stop loss functionality
fix(alpaca): Handle market closed error gracefully  
docs(readme): Update installation instructions
test(strategy): Add tests for RSI indicator
```

---

## Architecture Guidelines

### Backend Structure

```
backend/
├── app/
│   ├── api/           # API routes
│   ├── brokers/       # Broker integrations
│   ├── core/          # Core business logic
│   ├── models/        # Data models
│   ├── strategies/    # Trading strategies
│   ├── utils/         # Utilities
│   └── main.py        # FastAPI app
├── tests/             # Test suite
└── requirements.txt   # Dependencies
```

### Adding a New Broker

1. Create `backend/app/brokers/new_broker.py`
2. Implement `BaseBroker` interface
3. Add tests in `tests/brokers/test_new_broker.py`
4. Update documentation
5. Add configuration in `config.py`

### Adding a New Strategy

1. Create `backend/app/strategies/new_strategy.py`
2. Implement strategy methods
3. Add comprehensive tests
4. Document parameters and signals
5. Update strategy selection logic

---

## Testing Guidelines

### Test Structure

```python
class TestRiskManager:
    def setup_method(self):
        """Setup test fixtures"""
        self.risk_manager = RiskManager()
        
    def test_circuit_breaker_triggers(self):
        """Test that circuit breaker activates correctly"""
        # Arrange
        self.risk_manager.daily_pnl = Decimal('-1000')
        portfolio_value = Decimal('10000')
        
        # Act
        can_trade, reason = self.risk_manager.check_circuit_breakers(portfolio_value)
        
        # Assert
        assert can_trade is False
        assert 'Daily loss limit' in reason
```

### Test Coverage

- Aim for 80%+ coverage
- Test edge cases
- Test error handling
- Mock external APIs
- Test risk management thoroughly

### Integration Tests

- Use paper trading accounts
- Test full workflows
- Verify broker integrations
- Test error scenarios

---

## Documentation

### Code Documentation

- Docstrings for all public functions
- Inline comments for complex logic
- Type hints for clarity

### User Documentation

- Update README.md for major features
- Add examples for new functionality
- Document configuration options
- Provide troubleshooting tips

---

## Review Process

### PR Review Checklist

**Code Quality**:
- [ ] Follows style guidelines
- [ ] No unnecessary complexity
- [ ] Proper error handling
- [ ] Efficient algorithms

**Security**:
- [ ] No hardcoded credentials
- [ ] Input validation
- [ ] No SQL injection risks
- [ ] No sensitive data in logs

**Testing**:
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Edge cases covered
- [ ] Integration tests if needed

**Documentation**:
- [ ] Code comments
- [ ] Docstrings
- [ ] README updated
- [ ] CHANGELOG updated

### Review Timeline

- Small PRs: 1-2 days
- Medium PRs: 3-5 days  
- Large PRs: 1-2 weeks

---

## Release Process

1. Version bump in `__init__.py`
2. Update CHANGELOG.md
3. Tag release: `git tag v1.0.0`
4. Push tags: `git push --tags`
5. GitHub Actions builds Docker images
6. Create GitHub Release
7. Announce in community channels

---

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open an Issue
- **Security**: Email security@omnitrade.ai
- **Chat**: Join our Discord (link in README)

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Given special Discord role
- Mentioned in project updates

---

## Legal

By contributing, you agree that:
- Your contributions will be licensed under MIT License
- You have rights to contribute the code
- You understand this software handles real money
- You've tested your changes thoroughly

---

**Thank you for contributing to OmniTrade AI!** 🚀

Every contribution makes the project better and safer for traders worldwide.