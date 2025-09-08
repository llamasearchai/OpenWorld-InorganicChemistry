# 🧪 OpenWorld-InorganicChemistry

<div align="center">

[![CI](https://github.com/llamasearchai/OpenWorld-InorganicChemistry/workflows/CI/badge.svg)](https://github.com/llamasearchai/OpenWorld-InorganicChemistry/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**An AI-Powered Platform for Inorganic Materials Discovery and Analysis**

*Accelerating materials science research through intelligent agents, computational modeling, and automated workflows*

</div>

---

## 🌟 Overview

OpenWorld-InorganicChemistry is a comprehensive, open-source platform that revolutionizes inorganic materials discovery by combining the power of Large Language Models (LLMs) with advanced computational tools. Our modular agent-based architecture enables seamless integration of literature review, synthesis planning, computational simulation, and automated analysis workflows.

### 🎯 Key Capabilities

- **🤖 AI-Powered Research Agents**: Intelligent agents for literature review, synthesis planning, and data analysis
- **⚗️ Computational Modeling**: DFT calculations, molecular dynamics, and property predictions
- **📊 Automated Analysis**: Data processing, visualization, and report generation
- **🔄 Workflow Orchestration**: Multi-agent collaboration and task coordination
- **🌐 Multiple Interfaces**: CLI, REST API, and web interface for different user needs
- **🔍 Literature Integration**: Automated search and synthesis of research papers
- **📈 Visualization Tools**: Interactive plots, crystal structures, and data dashboards

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (recommended: Python 3.11)
- **pip** package manager
- **OpenAI API Key** (optional, for enhanced AI features)

### Installation

#### Option 1: Standard Installation
```bash
# Clone the repository
git clone https://github.com/llamasearchai/OpenWorld-InorganicChemistry.git
cd OpenWorld-InorganicChemistry

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -e .
pip install pytest httpx pytest-asyncio
```

#### Option 2: Development Installation
```bash
# Install with development dependencies
pip install -e ".[dev]"
```

#### Option 3: Docker Installation
```bash
# Build and run with Docker
docker build -t openworld-chemistry .
docker run -p 8000:8000 openworld-chemistry
```

### Configuration

1. **Create environment file:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

2. **Set OpenAI API Key:**
```bash
export OPENAI_API_KEY="your-api-key-here"
# Or add to .env file
```

3. **Verify installation:**
```bash
python -m openinorganicchemistry.cli doctor
```

---

## 💻 Usage Examples

### Command Line Interface

```bash
# Interactive menu
python -m openinorganicchemistry.cli menu

# Literature review
python -m openinorganicchemistry.cli literature "perovskite solar cells"

# Synthesis planning
python -m openinorganicchemistry.cli synth "CH3NH3PbI3"

# Run simulation
python -m openinorganicchemistry.cli simulate "TiO2" --backend emt --supercell 2

# Analyze results
python -m openinorganicchemistry.cli analyze results.csv

# Generate reports
python -m openinorganicchemistry.cli report <run-id>
```

### Python API

```python
from openinorganicchemistry.agents import literature, synthesis, simulation
from openinorganicchemistry.core.settings import Settings

# Configure settings
settings = Settings.load()

# Literature review
run_id = literature.literature_query("quantum dots stability")

# Synthesis planning
run_id = synthesis.propose_synthesis("CsPbBr3")

# Run simulation
run_id = simulation.run_simulation("SiO2", backend="emt", supercell=1)
```

### REST API

Start the server:
```bash
uvicorn openinorganicchemistry.api:app --reload
```

Example requests:
```bash
# Health check
curl http://localhost:8000/health

# Literature search
curl -X POST "http://localhost:8000/literature" \
  -H "Content-Type: application/json" \
  -d '{"text": "metal-organic frameworks"}'

# Synthesis proposal
curl -X POST "http://localhost:8000/synthesis" \
  -H "Content-Type: application/json" \
  -d '{"target": "ZnO"}'

# Run simulation
curl -X POST "http://localhost:8000/simulation" \
  -H "Content-Type: application/json" \
  -d '{"formula": "CuO", "backend": "emt", "supercell": 1}'
```

### Web Interface

```bash
# Start Streamlit dashboard
streamlit run gui/app.py
```

---

## 🏗️ Architecture

### Core Components

```
openinorganicchemistry/
├── agents/           # AI agents for specific tasks
│   ├── literature.py    # Literature review and synthesis
│   ├── synthesis.py     # Synthesis pathway planning
│   ├── simulation.py    # Computational simulations
│   ├── analysis.py      # Data analysis and visualization
│   ├── reporting.py     # Report generation
│   └── orchestration.py # Multi-agent coordination
├── core/            # Core utilities and data structures
│   ├── chemistry.py     # Chemical data structures
│   ├── dft_utils.py     # DFT calculation utilities
│   ├── settings.py      # Configuration management
│   └── storage.py       # Data persistence layer
├── integrations/    # External service integrations
│   ├── websearch.py     # Web search capabilities
│   ├── lit_sources.py   # Literature database APIs
│   └── sgpt.py         # Shell-GPT integration
├── api.py          # FastAPI REST endpoints
└── cli.py          # Command-line interface
```

### Agent System

Our platform uses a modular agent architecture where each agent specializes in specific domain tasks:

- **Literature Agent**: Searches scientific literature and synthesizes insights
- **Synthesis Agent**: Proposes synthesis pathways and reaction conditions
- **Simulation Agent**: Performs computational modeling and predictions
- **Analysis Agent**: Processes experimental data and generates visualizations
- **Orchestration Agent**: Coordinates multi-agent workflows

---

## 🔬 Scientific Features

### Computational Capabilities

- **Density Functional Theory (DFT)**: Electronic structure calculations
- **Molecular Dynamics**: Atomic-scale simulations
- **Machine Learning**: Property predictions and materials screening
- **Thermodynamic Analysis**: Phase diagrams and stability calculations

### Materials Science Tools

- **Crystal Structure Analysis**: Symmetry, defects, and surfaces
- **Electronic Properties**: Band structures, density of states
- **Optical Properties**: Absorption spectra and photoluminescence
- **Mechanical Properties**: Elastic constants and hardness

### Database Integration

- **Materials Project**: High-throughput computational database
- **OQMD**: Open Quantum Materials Database
- **COD**: Crystallography Open Database
- **Literature Sources**: ArXiv, CrossRef, PubMed

---

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=openinorganicchemistry

# Run specific test categories
pytest tests/test_agents_mock.py -v
pytest tests/test_api.py -v
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: Multi-component workflows
- **API Tests**: REST endpoint validation
- **Mock Tests**: External service simulation

---

## 🛠️ Development

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run code formatting
black .
isort .

# Run linting
flake8 .
mypy .
```

### Contributing Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **pytest** for testing

---

## 📈 Performance

### Benchmarks

- **API Response Time**: <100ms (95th percentile)
- **Simulation Performance**: EMT calculations <1s for simple systems
- **Literature Search**: <5s for comprehensive queries
- **Test Coverage**: >90% across all modules

### Scalability

- **Concurrent Users**: Tested up to 100 simultaneous connections
- **Memory Usage**: <512MB for typical workflows
- **Storage**: Efficient SQLite backend with optional MongoDB support

---

## 🔒 Security

### Security Features

- **API Key Management**: Secure credential handling
- **Input Validation**: Comprehensive sanitization
- **Access Control**: Role-based permissions
- **Audit Logging**: Complete operation tracking

### Security Guidelines

Please refer to our [Security Policy](SECURITY.md) for reporting vulnerabilities and security best practices.

---

## 📚 Documentation

### User Guides

- [Installation Guide](docs/installation.md)
- [User Manual](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Tutorial Notebooks](examples/)

### Developer Resources

- [Architecture Overview](docs/architecture.md)
- [Contributing Guide](CONTRIBUTING.md)
- [API Documentation](docs/api-docs.md)
- [Agent Development](docs/agent-development.md)

---

## 🌍 Community

### Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Community Q&A and ideas
- **Email**: nikjois@llamasearch.ai
- **Documentation**: Comprehensive guides and tutorials

### Roadmap

See our [Project Roadmap](ROADMAP.md) for upcoming features and improvements:

- **Q4 2024**: Enhanced ML models and database integration
- **Q1 2025**: Advanced visualization and web interface
- **Q2 2025**: HPC integration and distributed computing
- **Q3 2025**: Mobile applications and cloud deployment

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Materials Project** for computational materials data
- **OpenAI** for advanced language model capabilities  
- **ASE (Atomic Simulation Environment)** for computational chemistry tools
- **FastAPI** for high-performance API framework
- **The scientific Python ecosystem** for foundational libraries

---

## 📖 Citation

If you use OpenWorld-InorganicChemistry in your research, please cite:

```bibtex
@software{jois2024openworld,
  title = {OpenWorld-InorganicChemistry: An AI-Powered Platform for Inorganic Materials Discovery and Analysis},
  author = {Jois, Nikhil},
  year = {2024},
  url = {https://github.com/llamasearchai/OpenWorld-InorganicChemistry},
  version = {1.1.2}
}
```

For detailed citation information, see [CITATION.cff](CITATION.cff).

---

<div align="center">

**[🏠 Homepage](https://llamasearch.ai) • [📚 Documentation](https://github.com/llamasearchai/OpenWorld-InorganicChemistry/wiki) • [🐛 Issues](https://github.com/llamasearchai/OpenWorld-InorganicChemistry/issues) • [💬 Discussions](https://github.com/llamasearchai/OpenWorld-InorganicChemistry/discussions)**

Made with ❤️ by the LlamaSearch AI team

</div>
