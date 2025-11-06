# Email Newsletter Aggregation Agent 📧🤖

An intelligent email processing system that reads your AI newsletter subscriptions, analyzes content using multiple specialized agents, and delivers a single, comprehensive daily brief.

Built with **Microsoft Agent Framework** (autogen) following strict **TDD methodology**.

## 🎯 Project Goals

### The Problem
- Drowning in 50+ AI/tech newsletters
- 2 hours/day spent reading
- 20% information retention
- 0-1 actionable insights per week

### The Solution
- Automated email aggregation and analysis
- Multi-agent AI processing pipeline
- Human-in-the-loop approval workflow
- Single daily digest with key insights

### Success Metrics
- **Time saved**: 2 hours/day → 10 minutes
- **Information retention**: 20% → 80%
- **Actionable insights**: 0-1/week → 5+/week

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Gmail API (OAuth2)                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Email Fetcher & Parser                     │
│  • Fetch last N days of emails                              │
│  • Parse HTML/multipart content                             │
│  • Extract metadata                                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Email Analyzer Agent                        │
│  • Extract key points                                        │
│  • Identify companies/products                              │
│  • Rate importance                                           │
│  • Generate action items                                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Summary Writer Agent                        │
│  • Group related topics                                      │
│  • Create executive summary                                  │
│  • Highlight top insights                                    │
│  • Format for readability                                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                Human-in-the-Loop Review                      │
│  • Preview summary                                           │
│  • Request changes                                           │
│  • Approve and send                                          │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud Project with Gmail API enabled
- Azure OpenAI API access (or OpenAI API)
- Gmail account

### Installation

```bash
# Clone the repository
git clone https://github.com/JustOtherAIGuy/email_aggregation_agent.git
cd email_aggregation_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Gmail API Setup**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download `credentials.json` and place in project root

2. **Environment Variables**:
   ```bash
   # Copy the example env file
   cp .env.example .env

   # Edit .env and add your credentials
   # Required:
   AZURE_OPENAI_API_KEY=your_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   ```

3. **First Run** (Gmail Authentication):
   ```bash
   # This will open a browser for OAuth2 authentication
   jupyter notebook notebooks/day_1_2_gmail_connection.ipynb
   ```

## 📖 Learning Path

This project is designed for educational purposes with a **7-day learning path**:

### Phase 1: Foundation (Days 1-2) ✅
**Notebook**: `notebooks/day_1_2_gmail_connection.ipynb`

**What You'll Build**:
- Gmail OAuth2 authentication
- Email fetching with query support
- Email parsing and content extraction

**Concepts Learned**:
- Gmail API integration
- OAuth2 flow
- Base64 decoding
- HTML to text conversion

**Status**: ✅ Complete (32 tests passing, 76% coverage)

### Phase 2: First Agent (Days 3-4) 🚧
**Notebook**: `notebooks/day_3_4_email_analyzer.ipynb`

**What You'll Build**:
- Email Analyzer Agent with autogen
- Content analysis and key point extraction
- Importance scoring
- Action item generation

**Concepts Learned**:
- Microsoft Agent Framework basics
- Single agent patterns
- Structured outputs
- Prompt engineering

**Status**: 🚧 In Progress

### Phase 3: Multi-Agent (Days 5-6) 📋
**Notebook**: `notebooks/day_5_6_summary_writer.ipynb`

**What You'll Build**:
- Summary Writer Agent
- Agent chaining workflow
- Context management
- Output formatting

**Concepts Learned**:
- Multi-agent orchestration
- Sequential workflows
- Agent communication
- State management

**Status**: 📋 Planned

### Phase 4: Human Loop (Day 7) 📋
**Notebook**: `notebooks/day_7_human_review.ipynb`

**What You'll Build**:
- Human-in-the-loop approval
- Interactive review process
- Email delivery system
- Complete workflow integration

**Concepts Learned**:
- Human-in-the-loop patterns
- Approval workflows
- Error handling
- Production considerations

**Status**: 📋 Planned

## 🧪 Testing

This project follows strict **Test-Driven Development (TDD)**:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_gmail_auth.py

# Run with coverage
pytest --cov=src/email_agent --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/ -m integration
```

**Current Test Coverage**: 76% (32 tests passing)

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_gmail_auth.py   # 12 tests
│   └── test_email_fetcher.py # 20 tests
└── integration/             # Integration tests
    └── (coming soon)
```

## 📁 Project Structure

```
email_aggregation_agent/
├── src/
│   └── email_agent/
│       ├── __init__.py
│       ├── gmail_auth.py        # Gmail authentication
│       ├── email_fetcher.py     # Email fetching
│       ├── email_parser.py      # Email parsing
│       ├── analyzer_agent.py    # (Day 3-4)
│       ├── summary_agent.py     # (Day 5-6)
│       └── workflow.py          # (Day 7)
├── tests/
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── notebooks/
│   ├── day_1_2_gmail_connection.ipynb
│   ├── day_3_4_email_analyzer.ipynb
│   ├── day_5_6_summary_writer.ipynb
│   └── day_7_human_review.ipynb
├── data/
│   ├── checkpoints/             # Saved state
│   └── samples/                 # Sample data
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

## 🎓 Code Philosophy

### Jupyter Notebook Style

All code follows an **educational, step-by-step approach**:

```python
# ✅ GOOD: Clear, educational, runnable
# Step 1: Import what we need
import os
from typing import Dict

# Step 2: Set up configuration
config = {"email": "your_email@gmail.com"}

# Step 3: Initialize connection
client = GmailClient(config)
print(f"Connected to: {config['email']}")

# Step 4: Test connection
result = client.test_connection()
print(f"Status: {result}")
```

```python
# ❌ BAD: Too complex, black box
class EmailProcessor:
    def __init__(self, config):
        self._setup_clients()
        self._initialize_agents()

    def process_all(self):
        return self._complex_internal_method()
```

### Principles

1. Every block should be runnable independently
2. Print intermediate results frequently
3. Use descriptive variable names
4. Add comments before each logical step
5. Test each component before combining

## 🔧 Development

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests with coverage
pytest --cov=src/email_agent --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## 📊 Progress Tracking

### Phase 1 (Days 1-2): ✅ Complete
- [x] Project structure setup
- [x] Gmail authentication
- [x] Email fetching
- [x] Email parsing
- [x] Unit tests (32 passing)
- [x] Day 1-2 Jupyter notebook

### Phase 2 (Days 3-4): 🚧 In Progress
- [ ] Email Analyzer Agent tests
- [ ] Email Analyzer Agent implementation
- [ ] Day 3-4 Jupyter notebook

### Phase 3 (Days 5-6): 📋 Planned
- [ ] Summary Writer Agent tests
- [ ] Summary Writer Agent implementation
- [ ] Day 5-6 Jupyter notebook

### Phase 4 (Day 7): 📋 Planned
- [ ] Human-in-the-loop tests
- [ ] Human-in-the-loop implementation
- [ ] Day 7 Jupyter notebook
- [ ] End-to-end integration

## 🤝 Contributing

This is primarily an educational/portfolio project, but suggestions are welcome!

1. Follow TDD methodology (write tests first)
2. Maintain Jupyter notebook style
3. Add clear documentation
4. Keep code educational and readable

## 📝 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- **Microsoft Agent Framework** (autogen) for agent orchestration
- **Gmail API** for email access
- **OpenAI/Azure OpenAI** for language models

## 📧 Contact

Created by [@JustOtherAIGuy](https://github.com/JustOtherAIGuy)

For questions or feedback, please open an issue!

---

**⭐ Star this repo if you find it helpful for learning AI agent development!**
