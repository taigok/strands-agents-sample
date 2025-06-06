# Strands Multi-Agent System

A production-ready multi-agent system built with AWS Strands Agents SDK that orchestrates specialized AI agents to handle complex business workflows collaboratively.

## 🎯 Overview

This system combines four specialized agents working together to solve complex business problems:

- **🔍 Data Analyst Agent**: Processes and analyzes data files (CSV, Excel), performs statistical analysis, and generates insights
- **🌐 Research Agent**: Conducts web research, market analysis, fact-checking, and gathers external information
- **📝 Report Generator Agent**: Creates professional reports, presentations, and documents in multiple formats
- **🎯 Coordinator Agent**: Orchestrates multi-agent workflows and manages task distribution

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- AWS Account with Bedrock access
- Docker (optional, for containerized deployment)

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd strands-multi-agent-system

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your AWS credentials and configuration
# At minimum, set:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - AWS_DEFAULT_REGION
```

### 3. Run the Application

```bash
# Start the Streamlit interface
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f strands-app

# Stop services
docker-compose down
```

### Using Docker Only

```bash
# Build the image
docker build -t strands-multi-agent .

# Run the container
docker run -p 8501:8501 --env-file .env strands-multi-agent
```

## 📋 Usage Examples

### 1. Data Analysis & Report Generation

1. Upload CSV/Excel files through the web interface
2. Select analysis types (statistical summary, trends, correlations)
3. Choose report sections and output format
4. The system automatically:
   - Analyzes data with the Data Analyst Agent
   - Conducts related market research
   - Generates a comprehensive report

### 2. Market Research

1. Enter your research topic (e.g., "Electric Vehicle Market")
2. Select research aspects (market size, competitors, trends)
3. Choose data sources and geographic focus
4. Get a detailed market analysis report

### 3. Competitive Intelligence

1. Enter your company/product and competitors
2. Select analysis criteria (features, pricing, market share)
3. Upload internal data for comparison (optional)
4. Receive competitive positioning analysis

### 4. Custom Multi-Agent Tasks

1. Describe your complex task in natural language
2. Select which agents to use
3. Upload relevant files
4. Get coordinated results from multiple agents

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Streamlit UI   │    │   Coordinator   │    │  Data Analyst   │
│                 │◄──►│     Agent       │◄──►│     Agent       │
│  - File Upload  │    │                 │    │                 │
│  - Task Config  │    │ - Workflow Mgmt │    │ - Data Analysis │
│  - Results View │    │ - Agent2Agent   │    │ - Statistics    │
└─────────────────┘    │ - Coordination  │    │ - Insights      │
                       └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Research      │    │ Report Generator│
                       │     Agent       │    │     Agent       │
                       │                 │    │                 │
                       │ - Web Search    │    │ - PDF Reports   │
                       │ - Market Data   │    │ - Word Docs     │
                       │ - Fact Check    │    │ - HTML Output   │
                       └─────────────────┘    └─────────────────┘
```

## 🛠️ Core Components

### Agents

- **CoordinatorAgent** (`src/agents/coordinator.py`): Orchestrates workflows
- **DataAnalystAgent** (`src/agents/data_analyst.py`): Data processing and analysis
- **ResearchAgent** (`src/agents/research_agent.py`): External information gathering
- **ReportGeneratorAgent** (`src/agents/report_generator.py`): Document creation

### Tools

- **Data Tools** (`src/tools/data_tools.py`): CSV/Excel processing, statistical analysis
- **Search Tools** (`src/tools/search_tools.py`): Web search, content extraction
- **Document Tools** (`src/tools/document_tools.py`): Report generation, file handling

### Configuration

- **Settings** (`src/config/settings.py`): Centralized configuration management
- **Environment Variables**: AWS credentials, API keys, agent parameters

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Required |
| `AWS_DEFAULT_REGION` | AWS region | us-east-1 |
| `BEDROCK_MODEL_ID` | Bedrock model to use | claude-3-5-sonnet |
| `AGENT_MAX_ITERATIONS` | Max agent iterations | 10 |
| `AGENT_TIMEOUT_SECONDS` | Agent timeout | 300 |
| `LOG_LEVEL` | Logging level | INFO |
| `ENABLE_TRACING` | Enable observability | true |

### Agent Configuration

Agents can be customized through the settings file:

```python
# Example: Modify agent behavior
settings.agent_max_iterations = 15
settings.agent_timeout_seconds = 600
```

## 📊 Monitoring & Observability

### Built-in Monitoring

- **Agent Dashboard**: Real-time agent status and performance
- **Task History**: Complete workflow tracking
- **Results Management**: Organized output storage

### Optional: Langfuse Integration

Enable detailed tracing by setting:

```bash
LANGFUSE_PUBLIC_KEY=your_key
LANGFUSE_SECRET_KEY=your_secret
ENABLE_TRACING=true
```

### Optional: Prometheus & Grafana

Included in docker-compose.yml for advanced monitoring:

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_data_analyst.py
```

## 📁 Project Structure

```
strands-multi-agent-system/
├── src/
│   ├── agents/           # Agent implementations
│   ├── tools/            # Custom tools
│   └── config/           # Configuration
├── tests/                # Test files
├── app.py               # Streamlit interface
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
├── docker-compose.yml  # Multi-service deployment
└── README.md           # This file
```

## 🚀 Production Deployment

### AWS ECS/Fargate

1. Build and push image to ECR
2. Create ECS task definition
3. Deploy to Fargate cluster
4. Configure load balancer

### AWS Lambda (Serverless)

For event-driven execution:
1. Package application
2. Deploy as Lambda function
3. Configure triggers (S3, API Gateway)

### Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/
```

## 🔒 Security

- **IAM Roles**: Use IAM roles instead of access keys in production
- **Secrets Management**: Use AWS Secrets Manager for sensitive data
- **Network Security**: Deploy in private subnets with proper security groups
- **Encryption**: Enable encryption at rest and in transit

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **AWS Credentials Error**
   ```bash
   # Verify credentials
   aws configure list
   aws bedrock list-foundation-models --region us-east-1
   ```

2. **Port Already in Use**
   ```bash
   # Find and kill process using port 8501
   lsof -ti:8501 | xargs kill -9
   ```

3. **Memory Issues**
   ```bash
   # Increase Docker memory allocation
   # Or reduce AGENT_MAX_ITERATIONS in .env
   ```

### Getting Help

- Check the logs: `docker-compose logs -f strands-app`
- Review agent outputs in the Streamlit interface
- Enable debug logging: `LOG_LEVEL=DEBUG`

## 🎯 Roadmap

- [ ] Voice interface integration
- [ ] Additional agent types (Legal, Financial)
- [ ] Real-time collaboration features
- [ ] Advanced workflow designer
- [ ] Cloud-native deployment templates
- [ ] Mobile application support

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

Built with ❤️ using AWS Strands Agents SDK
