# Contributing to CyberIntel Platform

Thank you for your interest in contributing to the CyberIntel Platform! We welcome contributions from the community.

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker & Docker Compose (recommended)
- Git

### Development Setup

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/cyberintel-platform.git
   cd cyberintel-platform
   ```

2. **Run automatic installation**
   
   **Linux/Mac:**
   ```bash
   chmod +x scripts/install.sh
   ./scripts/install.sh
   ```
   
   **Windows PowerShell:**
   ```powershell
   .\scripts\install.ps1
   ```
   
   **Windows CMD:**
   ```cmd
   scripts\install.bat
   ```

3. **Configure environment**
   ```bash
   # Edit .env file with your API keys
   cp .env.example .env
   nano .env  # or use your preferred editor
   ```

4. **Start infrastructure**
   ```bash
   docker-compose up -d
   ```

5. **Start development servers**
   ```bash
   npm run dev
   ```

6. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Project Structure

```
cyberintel-platform/
├── frontend/          # React + Vite + Tailwind UI
├── backend/           # Main API server (Fastify)
├── gateway/           # API Gateway with auth
├── orchestrator/      # Task orchestration service
├── ai-router/         # AI provider routing
├── graph-engine/      # Neo4j graph intelligence
├── agents/            # Python AI agents
├── workers/           # Background workers
├── integrations/      # OSINT tool integrations
├── telegram-bot/      # Telegram bot service
├── shared/            # Shared TypeScript library
├── docs/              # Documentation
└── scripts/           # Installation scripts
```

## Code Style

### TypeScript (Node.js Services)
- Use TypeScript strict mode
- Follow existing code formatting
- Use async/await over callbacks
- Add JSDoc comments for public APIs
- Use meaningful variable names
- Prefer interfaces over types for objects

### Python (Agents & Workers)
- Follow PEP 8 style guide
- Use type hints
- Add docstrings for classes and functions
- Use async/await for I/O operations
- Keep functions focused and small

### General Guidelines
- Write self-documenting code
- Add comments for complex logic
- Write meaningful commit messages
- Keep functions under 50 lines when possible
- Use descriptive names for variables and functions

## Testing

### Running Tests
```bash
# Run all tests
npm test

# Run tests for specific service
npm test --workspace=backend

# Run Python tests
cd agents && pytest
cd workers && pytest
```

### Writing Tests
- Write unit tests for new features
- Add integration tests for API endpoints
- Test error handling and edge cases
- Aim for >80% code coverage
- Mock external API calls

### Test Structure
```typescript
// TypeScript example
describe('FeatureName', () => {
  it('should do something', async () => {
    // Arrange
    const input = { ... };
    
    // Act
    const result = await functionUnderTest(input);
    
    // Assert
    expect(result).toBe(expected);
  });
});
```

## Pull Request Process

1. **Update documentation**
   - Update README.md if needed
   - Add/update docs in docs/ folder
   - Update API.md for API changes
   - Add comments in code

2. **Ensure quality**
   - All tests pass
   - No linting errors
   - No TypeScript errors
   - Code follows style guide

3. **Create PR**
   - Use descriptive title
   - Fill out PR template completely
   - Link related issues
   - Add screenshots if UI changes

4. **Review process**
   - Wait for CI/CD to pass
   - Address review comments
   - Keep PR focused and small
   - Squash commits if requested

5. **After merge**
   - Delete your branch
   - Update your fork
   - Close related issues

## Commit Message Guidelines

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples
```
feat(agents): add breach intelligence agent

Implemented new agent for breach data correlation
with HaveIBeenPwned and DeHashed integrations.

Closes #123
```

```
fix(frontend): resolve graph rendering issue

Fixed bug where graph nodes were not displaying
correctly on Safari browser.
```

## Reporting Issues

### Bug Reports
1. Check existing issues first
2. Use bug report template
3. Provide detailed description
4. Include steps to reproduce
5. Add relevant logs/screenshots
6. Specify environment details

### Security Issues
**Do not open public issues for security vulnerabilities!**

Email security issues to: security@cyberintel.platform (or your email)

## Feature Requests

1. Open a GitHub Issue using feature request template
2. Describe the feature clearly
3. Explain the use case
4. Discuss implementation approach
5. Consider alternatives

## Integration Requests

Want to add a new OSINT tool or API?

1. Use integration request template
2. Provide tool/API details
3. Explain data it provides
4. Note API requirements
5. Describe use case

## Areas for Contribution

### High Priority
- [ ] Additional OSINT tool integrations
- [ ] AI agent improvements
- [ ] Graph intelligence algorithms
- [ ] Performance optimizations
- [ ] Documentation improvements

### Good First Issues
- [ ] UI/UX improvements
- [ ] Bug fixes
- [ ] Test coverage
- [ ] Code documentation
- [ ] Example configurations

### Advanced Contributions
- [ ] New AI agents
- [ ] Advanced graph algorithms
- [ ] Real-time data pipelines
- [ ] Security enhancements
- [ ] Scalability improvements

## Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors.

### Standards
- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards others

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Other unprofessional conduct

### Enforcement
Violations may result in temporary or permanent ban from the project.

## Getting Help

### Documentation
- [Quick Start Guide](docs/QUICKSTART.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Agent Documentation](docs/AGENTS.md)

### Community
- GitHub Discussions: Ask questions and share ideas
- GitHub Issues: Report bugs and request features
- Pull Requests: Contribute code

### Contact
- Project maintainers: [Add contact info]
- Security issues: [Add security email]

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to CyberIntel Platform! 🚀
