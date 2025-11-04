# ML Deployment Package - Insight Engine 2.0

🚀 **Automated ML Model Deployment to AWS SageMaker**

Reusable Python deployment package that automates the entire process of deploying ML inference services to AWS SageMaker using CircleCI. Includes FastAPI wrapper generation, Lambda caching layer, API Gateway setup, and ApigeeX integration for production environments.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [DSSAT-py Deployment Guide](#dssat-py-deployment-guide)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Deployment Workflow](#deployment-workflow)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### Core Capabilities
- ✅ **Automated FastAPI Wrapper Generation** - Creates production-ready FastAPI application for your model
- ✅ **SageMaker Deployment** - Deploy to AWS SageMaker with configurable instance types
- ✅ **Lambda Caching Layer** - Automatic Redis/Valkey caching for inference results
- ✅ **API Gateway Setup** - Cognito-authenticated endpoints for Dev environment
- ✅ **ApigeeX Integration** - Enterprise proxy for Stage/Prod with internal auth
- ✅ **CircleCI Pipeline** - Complete CI/CD with SonarCloud, ECR, and deployment
- ✅ **Auto-scaling Support** - Configure auto-scaling for production workloads
- ✅ **Real-time Progress** - Live deployment status and reporting
- ✅ **Feature Branch Workflow** - Automatic feature branch creation

### Environment Support
- **Dev**: API Gateway + Cognito + API Key generation
- **QA/Staging**: ApigeeX proxy with OAuth/JWT
- **Production**: ApigeeX with internal auth service + high availability

## 🏗️ Architecture

```
Developer → GitHub → CircleCI → ECR → SageMaker
                         ↓              ↓
                    SonarCloud    Lambda + Cache
                                       ↓
                                 API Gateway (Dev)
                                       ↓
                                 Cognito Auth (JWT)
                                       ↓
                              ApigeeX (Stage/Prod)
                                       ↓
                                   End Users
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- AWS Account with appropriate permissions
- CircleCI account linked to GitHub
- Docker Desktop (for local testing)

### Initialize New Model Deployment

```bash
# Clone the repository
git clone <your-repo-url>
cd ie-deployment

# Install dependencies
pip install -r requirements.txt

# Initialize new model deployment
python deployment_package/deploy.py init my-model-name

# Follow the interactive prompts to configure:
# - Environment (dev/qa/staging/prod)
# - Instance type (ml.m5.xlarge recommended)
# - Instance count (1 for dev, 2+ for prod)
# - Auto-scaling settings
# - Cache configuration
# - AWS region
```

This will:
1. Create a feature branch `feature/deploy-my-model-name`
2. Generate complete FastAPI wrapper structure
3. Create `release.yaml` with your configuration
4. Generate CircleCI config
5. Provide next steps for deployment

## 📦 Installation

```bash
# Install the deployment package
pip install -r requirements.txt

# Verify installation
python deployment_package/deploy.py --help
```

## 🎯 DSSAT-py Deployment Guide

**Are you deploying the DSSAT-py model?** We have specific guides for you!

### Quick Start (15 minutes)
📘 **[DSSAT-py Quick Start Guide](docs/DSSAT_PY_QUICK_START.md)**

Perfect for getting started quickly with copy-paste commands and a visual workflow diagram.

### Comprehensive Guide
📗 **[DSSAT-py Deployment Guide](docs/DSSAT_PY_DEPLOYMENT_GUIDE.md)**

Step-by-step guide with:
- ✅ Detailed instructions for DSSAT-py repository at `C:\Users\u836422\OneDrive - Syngenta\Digital Architecture Team\IE2.0\dssat-py`
- ✅ Custom model loading examples for DSSAT
- ✅ Input/output schema examples for crop simulation
- ✅ CircleCI configuration walkthrough
- ✅ Troubleshooting specific to DSSAT models
- ✅ Cost estimation and monitoring

**What you'll build:**
```
DSSAT Model → FastAPI → Docker → SageMaker → Lambda → API Gateway → Production
```

---

## 💻 Usage

### Command-Line Interface

```bash
# Initialize new project
python deployment_package/deploy.py init <model-name> [--output <path>]

# Deploy existing project
python deployment_package/deploy.py deploy --config release.yaml --environment dev
```

### Interactive Configuration

When initializing a new project, you'll be prompted for:

1. **Deployment Environment**
   - dev (Development)
   - qa (Quality Assurance)
   - staging (Staging)
   - prod (Production)

2. **Instance Type** (see [SageMaker Instance Types](#sagemaker-instance-types))
   - ml.t3.medium - Dev/Test
   - ml.m5.xlarge - Recommended
   - ml.c5.xlarge - Compute optimized
   - ml.g4dn.xlarge - GPU accelerated

3. **Instance Count**
   - 1 for dev/qa
   - 2+ for staging/prod (high availability)

4. **Auto-scaling** (Stage/Prod only)
   - Min/Max instances
   - Target invocations per instance

5. **Caching**
   - Enable/disable Redis caching
   - Cache TTL (seconds)

6. **AWS Region**
   - eu-central-1 (Frankfurt) - Default
   - us-east-1, us-west-2, ap-southeast-1, etc.

## ⚙️ Configuration

### release.yaml Structure

```yaml
name: my-model-name
type: sagemaker

instance:
  type: ml.m5.xlarge
  count: 1
  volumeSizeInGB: 50
  region: eu-central-1
  tags:
    managedby: terraform
    project: insight-engine-2.0
    team: ml-team

version:
  major: 1
  minor: 0

deployTimeout: 900

cache:
  enabled: true
  ttl: 3600

autoscaling:
  enabled: false
  minInstances: 1
  maxInstances: 4
  targetInvocationsPerInstance: 100

sagemaker:
  bucket: insights-engine-sagemaker-models
  model_name: my-model-name
  endpoint_name: my-model-name-endpoint
  model_desc: "My ML model description"
  instance_type: ml.m5.xlarge
  instance_count: 1
```

### SageMaker Instance Types

| Instance Type | vCPUs | Memory | Use Case | Cost/hour* |
|--------------|-------|---------|----------|------------|
| ml.t3.medium | 2 | 4 GB | Dev/Test | $0.05 |
| ml.m5.large | 2 | 8 GB | General | $0.115 |
| **ml.m5.xlarge** | 4 | 16 GB | **Recommended** | $0.23 |
| ml.m5.2xlarge | 8 | 32 GB | Medium load | $0.46 |
| ml.c5.xlarge | 4 | 8 GB | Compute optimized | $0.204 |
| ml.r5.xlarge | 4 | 32 GB | Memory intensive | $0.252 |
| ml.g4dn.xlarge | 4 | 16 GB + GPU | Deep learning | $0.736 |

*Approximate pricing for eu-central-1 region

## 🔄 Deployment Workflow

### 1. Local Development

```bash
# Test FastAPI app locally
cd my-model-name
python src/app.py

# Test with curl
curl http://localhost:8080/ping
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"features": {"feature1": 1.0}}'
```

### 2. Docker Build

```bash
# Build container
docker build -t my-model:local .

# Run container
docker run -p 8080:8080 my-model:local

# Test health check
curl http://localhost:8080/ping
```

### 3. Push to GitHub

```bash
git add .
git commit -m "feat: Add my-model deployment"
git push origin feature/deploy-my-model
```

### 4. CircleCI Pipeline

Automatically triggers:
1. ✅ Code quality scan (SonarCloud)
2. ✅ Docker build and push to ECR
3. ⏸️ Manual approval for DEV deployment
4. ✅ SageMaker endpoint creation
5. ✅ Lambda function deployment
6. ✅ API Gateway setup (Dev) or ApigeeX (Prod)
7. ✅ Output API endpoint and credentials

### 5. Test Deployed Endpoint

```bash
# Dev environment (with API key)
curl -X POST https://{api-id}.execute-api.eu-central-1.amazonaws.com/dev/invoke \
  -H "Authorization: Bearer {jwt-token}" \
  -H "Content-Type: application/json" \
  -d '{"features": {"feature1": 1.0}}'
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=deployment_package --cov-report=html
```

### Integration Tests

```bash
# Test complete deployment flow (mock)
pytest tests/integration/ -v
```

## 🔧 Troubleshooting

### Common Issues

**Issue**: SageMaker endpoint stuck in "Creating"
- ✅ Verify ECR image exists
- ✅ Check IAM role permissions
- ✅ Review CloudWatch logs

**Issue**: Lambda timeout
- ✅ Check SageMaker endpoint latency
- ✅ Optimize model inference code
- ✅ Consider async invocation

**Issue**: API Gateway 401 Unauthorized
- ✅ Verify JWT token not expired
- ✅ Check Cognito User Pool configuration
- ✅ Ensure correct Authorization header format

### Logs

```bash
# View SageMaker logs
aws logs tail /aws/sagemaker/Endpoints/my-model-endpoint --follow

# View Lambda logs
aws logs tail /aws/lambda/my-model-lambda-dev --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/sagemaker/Endpoints/my-model-endpoint \
  --filter-pattern "ERROR"
```

## 📚 Documentation

- [Technical Requirements](docs/technical-requirements.md)
- [SageMaker Onboarding Guide](docs/sagemaker-guide.md)
- [API Documentation](docs/api-documentation.md)
- [Deployment Best Practices](docs/best-practices.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

Copyright © 2025 Syngenta Digital - Insight Engine Team

## 📧 Support

For questions or issues:
- Create an issue in this repository
- Contact: Insight Engine Team
- Slack: #insight-engine-support
