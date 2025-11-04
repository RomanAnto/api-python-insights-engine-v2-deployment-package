# DSSAT-py Deployment Guide

## How to Deploy Your DSSAT-py Model Using This Package

This guide walks you through deploying your DSSAT-py model to AWS using our ML Deployment Package. The package will automatically:
- Generate a FastAPI wrapper for your model
- Create CircleCI configuration based on your inputs
- Set up AWS SageMaker, Lambda, and API Gateway/ApigeeX
- Configure auto-scaling and caching

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step 1: Install the Deployment Package](#step-1-install-the-deployment-package)
3. [Step 2: Navigate to Your DSSAT-py Repository](#step-2-navigate-to-your-dssat-py-repository)
4. [Step 3: Initialize the Deployment](#step-3-initialize-the-deployment)
5. [Step 4: Customize Your Model Integration](#step-4-customize-your-model-integration)
6. [Step 5: Test Locally](#step-5-test-locally)
7. [Step 6: Configure CircleCI](#step-6-configure-circleci)
8. [Step 7: Deploy to AWS](#step-7-deploy-to-aws)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:

✅ **Access to DSSAT-py Repository**
- Path: `C:\Users\u836422\OneDrive - Syngenta\Digital Architecture Team\IE2.0\dssat-py`
- Git repository initialized with remote configured

✅ **Python Environment**
```powershell
python --version  # Should be Python 3.11 or higher
```

✅ **AWS Credentials**
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)

✅ **Docker Desktop** (for local testing)
```powershell
docker --version
```

✅ **Git Configured**
```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@syngenta.com"
```

---

## Step 1: Install the Deployment Package

### 1.1 Clone the Deployment Package
```powershell
cd "C:\Users\u836422\OneDrive - Syngenta\Digital Architecture Team\IE2.0"

# Clone the deployment package
git clone https://github.com/RomanAnto/api-python-insights-engine-v2-deployment-package.git

cd api-python-insights-engine-v2-deployment-package
```

### 1.2 Install Dependencies
```powershell
# Create a virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

### 1.3 Verify Installation
```powershell
python deployment_package/deploy.py --help
```

You should see:
```
usage: deploy.py [-1] {init,deploy} ...

ML Deployment Automation for Insight Engine 2.0

positional arguments:
  {init,deploy}
    init         Initialize a new deployment project
    deploy       Deploy to AWS
```

---

## Step 2: Navigate to Your DSSAT-py Repository

```powershell
# Navigate to your DSSAT-py project
cd "C:\Users\u836422\OneDrive - Syngenta\Digital Architecture Team\IE2.0\dssat-py"

# Verify you're in the correct repository
git remote -v
```

---

## Step 3: Initialize the Deployment

### 3.1 Run the Initialization Command

```powershell
# Run from your DSSAT-py directory
python "..\api-python-insights-engine-v2-deployment-package\deployment_package\deploy.py" init dssat-model
```

### 3.2 Answer the Interactive Prompts

The tool will ask you a series of questions. Here's what to provide:

#### **Model Configuration**
```
Enter model name: dssat-model
Enter model version: 1.0.0
Enter model description: DSSAT crop simulation model API for Insight Engine 2.0
```

#### **AWS Region**
```
Enter AWS region: us-east-1
```

#### **Environment Selection**
```
Select deployment environment:
1. dev
2. qa
3. prod
Enter choice (1-3): 1
```

#### **Instance Type Selection**
```
Select SageMaker instance type:
1. ml.t3.medium - 2 vCPU, 4GB RAM ($0.05/hr) - For development/testing
2. ml.m5.large - 2 vCPU, 8GB RAM ($0.115/hr) - Balanced compute/memory
3. ml.c5.xlarge - 4 vCPU, 8GB RAM ($0.204/hr) - Compute optimized
4. ml.m5.xlarge - 4 vCPU, 16GB RAM ($0.23/hr) - Memory optimized
5. ml.c5.2xlarge - 8 vCPU, 16GB RAM ($0.408/hr) - High compute
6. ml.m5.2xlarge - 8 vCPU, 32GB RAM ($0.46/hr) - High memory
7. ml.p3.2xlarge - 8 vCPU, 61GB RAM, 1 GPU ($3.825/hr) - GPU accelerated
8. ml.g4dn.xlarge - 4 vCPU, 16GB RAM, 1 GPU ($0.736/hr) - Cost-effective GPU

Enter choice (1-8): 2  # Recommended for DSSAT workloads
```

#### **Instance Count**
```
Enter initial instance count (1-10): 2  # For high availability
```

#### **Auto-scaling Configuration**
```
Enable auto-scaling? (yes/no): yes
Enter minimum instances (1-10): 2
Enter maximum instances (2-20): 10
Enter target invocations per instance (100-10000): 1000
```

#### **Caching Configuration**
```
Enable Redis caching? (yes/no): yes
Enter cache TTL in seconds (60-3600): 3600  # 1 hour cache for simulation results
```

#### **Machine Size for CircleCI**
```
Select CircleCI machine size:
1. small - 1 vCPU, 2GB RAM
2. medium - 2 vCPU, 4GB RAM
3. large - 4 vCPU, 8GB RAM
4. xlarge - 8 vCPU, 16GB RAM

Enter choice (1-4): 3  # Recommended for building Docker images
```

#### **API Gateway Configuration**
```
Select API platform:
1. API Gateway (for dev environment)
2. ApigeeX (for stage/prod environments)

Enter choice (1-2): 1  # Use API Gateway for dev
```

### 3.3 What Gets Generated

After completing the prompts, the tool will create:

```
dssat-py/
├── fastapi_app/               # Generated FastAPI application
│   ├── app.py                 # Main FastAPI app
│   ├── health.py              # Health check endpoints
│   ├── prediction.py          # Prediction endpoints
│   ├── model_loader.py        # Model loading (YOU CUSTOMIZE THIS)
│   ├── requirements.txt       # FastAPI dependencies
│   └── Dockerfile             # Multi-stage Docker build
├── tests/                     # Generated test files
│   ├── test_health.py
│   └── test_prediction.py
├── .circleci/                 # Generated CircleCI config
│   └── config.yml             # Complete CI/CD pipeline
└── release.yaml               # Generated configuration file
```

The tool will also:
- ✅ Create a feature branch: `feature/dssat-model-deployment`
- ✅ Commit all generated files
- ✅ Display summary of generated files

---

## Step 4: Customize Your Model Integration

### 4.1 Implement Model Loading Logic

Edit `fastapi_app/model_loader.py` to load your DSSAT model:

```python
import os
import pickle
from typing import Any
import logging

logger = logging.getLogger(__name__)

class DSSATModelLoader:
    """Loads and manages the DSSAT crop simulation model."""
    
    def __init__(self, model_dir: str = "/opt/ml/model"):
        self.model_dir = model_dir
        self.model = None
        self.model_metadata = {}
    
    def load_model(self) -> Any:
        """
        Load the DSSAT model from the model directory.
        
        Customize this method based on how your DSSAT model is saved.
        Examples:
        - Pickle files: pickle.load()
        - Joblib files: joblib.load()
        - Custom format: your_custom_loader()
        """
        try:
            # Example: Loading a pickled DSSAT model
            model_path = os.path.join(self.model_dir, "dssat_model.pkl")
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            logger.info(f"Loading DSSAT model from {model_path}")
            
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
            
            # Load metadata if available
            metadata_path = os.path.join(self.model_dir, "metadata.json")
            if os.path.exists(metadata_path):
                import json
                with open(metadata_path, "r") as f:
                    self.model_metadata = json.load(f)
            
            logger.info("DSSAT model loaded successfully")
            logger.info(f"Model metadata: {self.model_metadata}")
            
            return self.model
            
        except Exception as e:
            logger.error(f"Error loading DSSAT model: {str(e)}")
            raise
    
    def get_model(self) -> Any:
        """Return the loaded model instance."""
        if self.model is None:
            self.load_model()
        return self.model
    
    def get_metadata(self) -> dict:
        """Return model metadata."""
        return self.model_metadata


# Global model loader instance
_model_loader = None

def get_model_loader() -> DSSATModelLoader:
    """Get or create the global model loader instance."""
    global _model_loader
    if _model_loader is None:
        _model_loader = DSSATModelLoader()
    return _model_loader
```

### 4.2 Customize Prediction Logic

Edit `fastapi_app/prediction.py` to define your DSSAT input/output schema:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from model_loader import get_model_loader

router = APIRouter()
logger = logging.getLogger(__name__)


class DSSATSimulationInput(BaseModel):
    """Input schema for DSSAT crop simulation."""
    
    # Weather data
    weather_data: Dict[str, List[float]] = Field(
        ...,
        description="Weather data with keys: temperature_max, temperature_min, rainfall, solar_radiation"
    )
    
    # Soil parameters
    soil_type: str = Field(..., description="Soil type code")
    soil_depth: float = Field(..., description="Soil depth in cm", gt=0)
    
    # Crop parameters
    crop_type: str = Field(..., description="Crop type (e.g., maize, wheat, rice)")
    planting_date: str = Field(..., description="Planting date (YYYY-MM-DD)")
    cultivar: str = Field(..., description="Cultivar code")
    
    # Management practices
    irrigation: Optional[str] = Field(None, description="Irrigation strategy")
    fertilizer: Optional[Dict[str, float]] = Field(None, description="Fertilizer amounts")
    
    # Simulation settings
    simulation_start: str = Field(..., description="Simulation start date (YYYY-MM-DD)")
    simulation_end: str = Field(..., description="Simulation end date (YYYY-MM-DD)")


class DSSATSimulationOutput(BaseModel):
    """Output schema for DSSAT crop simulation results."""
    
    # Yield predictions
    grain_yield: float = Field(..., description="Grain yield in kg/ha")
    biomass_yield: float = Field(..., description="Total biomass in kg/ha")
    
    # Growth metrics
    anthesis_date: str = Field(..., description="Anthesis date (YYYY-MM-DD)")
    maturity_date: str = Field(..., description="Maturity date (YYYY-MM-DD)")
    growing_season_days: int = Field(..., description="Length of growing season")
    
    # Resource use
    water_use: float = Field(..., description="Total water use in mm")
    nitrogen_uptake: float = Field(..., description="Total N uptake in kg/ha")
    
    # Performance metrics
    prediction_confidence: float = Field(..., description="Model confidence score (0-1)")
    simulation_time_ms: float = Field(..., description="Simulation time in milliseconds")


@router.post("/invocations", response_model=DSSATSimulationOutput)
async def predict(input_data: DSSATSimulationInput):
    """
    Run DSSAT crop simulation.
    
    This endpoint accepts crop, weather, soil, and management parameters
    and returns yield predictions and growth metrics.
    """
    try:
        logger.info(f"Received prediction request for crop: {input_data.crop_type}")
        
        # Get the model loader
        model_loader = get_model_loader()
        model = model_loader.get_model()
        
        # Convert input to format expected by DSSAT model
        model_input = {
            "weather": input_data.weather_data,
            "soil": {
                "type": input_data.soil_type,
                "depth": input_data.soil_depth
            },
            "crop": {
                "type": input_data.crop_type,
                "planting_date": input_data.planting_date,
                "cultivar": input_data.cultivar
            },
            "management": {
                "irrigation": input_data.irrigation,
                "fertilizer": input_data.fertilizer
            },
            "simulation": {
                "start": input_data.simulation_start,
                "end": input_data.simulation_end
            }
        }
        
        # Run the DSSAT simulation
        import time
        start_time = time.time()
        
        # CUSTOMIZE THIS: Call your actual DSSAT model
        # Example: result = model.run_simulation(model_input)
        result = model.predict(model_input)  # Adjust based on your model's API
        
        simulation_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Format the output
        output = DSSATSimulationOutput(
            grain_yield=result.get("grain_yield", 0.0),
            biomass_yield=result.get("biomass_yield", 0.0),
            anthesis_date=result.get("anthesis_date", ""),
            maturity_date=result.get("maturity_date", ""),
            growing_season_days=result.get("growing_season_days", 0),
            water_use=result.get("water_use", 0.0),
            nitrogen_uptake=result.get("nitrogen_uptake", 0.0),
            prediction_confidence=result.get("confidence", 0.95),
            simulation_time_ms=simulation_time
        )
        
        logger.info(f"Prediction successful: grain_yield={output.grain_yield} kg/ha")
        return output
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/batch-invocations", response_model=List[DSSATSimulationOutput])
async def batch_predict(input_data: List[DSSATSimulationInput]):
    """
    Run batch DSSAT simulations.
    
    Accepts multiple simulation requests and returns results for each.
    """
    try:
        logger.info(f"Received batch prediction request with {len(input_data)} simulations")
        
        results = []
        for idx, simulation_input in enumerate(input_data):
            logger.info(f"Processing simulation {idx + 1}/{len(input_data)}")
            result = await predict(simulation_input)
            results.append(result)
        
        logger.info(f"Batch prediction completed: {len(results)} simulations")
        return results
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")
```

### 4.3 Update Requirements (if needed)

Edit `fastapi_app/requirements.txt` to add DSSAT-specific dependencies:

```txt
# FastAPI dependencies (already included)
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6

# DSSAT-specific dependencies (ADD THESE)
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.11.0
# Add any other DSSAT-py dependencies here
```

### 4.4 Customize Dockerfile (Optional)

If DSSAT has special system dependencies, edit `fastapi_app/Dockerfile`:

```dockerfile
# Builder stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies for DSSAT (if needed)
RUN apt-get update && apt-get install -y \
    gcc \
    gfortran \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Create model directory
RUN mkdir -p /opt/ml/model

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/ping || exit 1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
```

---

## Step 5: Test Locally

### 5.1 Build the Docker Image

```powershell
cd "C:\Users\u836422\OneDrive - Syngenta\Digital Architecture Team\IE2.0\dssat-py"

# Build the Docker image
docker build -t dssat-model:latest fastapi_app/
```

### 5.2 Run the Container Locally

```powershell
# Run the container
docker run -d -p 8080:8080 --name dssat-api dssat-model:latest

# Check if it's running
docker ps
```

### 5.3 Test the Endpoints

```powershell
# Test health endpoint
curl http://localhost:8080/ping

# Test prediction endpoint
curl -X POST http://localhost:8080/invocations `
  -H "Content-Type: application/json" `
  -d '{
    "weather_data": {
      "temperature_max": [30, 31, 29, 28],
      "temperature_min": [18, 19, 17, 18],
      "rainfall": [0, 5, 10, 0],
      "solar_radiation": [20, 22, 21, 23]
    },
    "soil_type": "CLAY_LOAM",
    "soil_depth": 150,
    "crop_type": "maize",
    "planting_date": "2024-03-15",
    "cultivar": "PIONEER_3394",
    "simulation_start": "2024-03-01",
    "simulation_end": "2024-09-30"
  }'
```

### 5.4 Check Logs

```powershell
# View container logs
docker logs dssat-api

# Follow logs in real-time
docker logs -f dssat-api
```

### 5.5 Stop and Clean Up

```powershell
# Stop the container
docker stop dssat-api

# Remove the container
docker rm dssat-api
```

---

## Step 6: Configure CircleCI

### 6.1 Review Generated CircleCI Config

The package has generated `.circleci/config.yml` with your specified settings. Review it:

```powershell
notepad .circleci\config.yml
```

Key sections to verify:
- ✅ Model name: `dssat-model`
- ✅ Machine size: `large` (as specified)
- ✅ AWS region: `us-east-1`
- ✅ Instance type: `ml.m5.large`
- ✅ Auto-scaling: enabled with your min/max values

### 6.2 Push to GitHub

```powershell
# You're already on feature/dssat-model-deployment branch
git status

# If you made additional customizations, commit them
git add .
git commit -m "feat: Customize DSSAT model integration"

# Push to GitHub
git push origin feature/dssat-model-deployment
```

### 6.3 Connect Repository to CircleCI

1. Go to [CircleCI](https://circleci.com/)
2. Click "Projects" → "Set Up Project"
3. Select your `dssat-py` repository
4. Choose "Use existing config"
5. Click "Set Up Project"

### 6.4 Add Environment Variables

In CircleCI project settings, add:

| Variable Name | Value | Source |
|--------------|-------|--------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key | AWS IAM |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | AWS IAM |
| `AWS_DEFAULT_REGION` | `us-east-1` | Your config |
| `AWS_ACCOUNT_ID` | Your 12-digit account ID | AWS Console |
| `DOCKER_USERNAME` | Docker Hub username | Docker Hub (if using) |
| `DOCKER_PASSWORD` | Docker Hub password | Docker Hub (if using) |
| `SONAR_TOKEN` | SonarCloud token | SonarCloud (optional) |

### 6.5 Create CircleCI Contexts

Create the following contexts in CircleCI Organization Settings:

1. **aws-credentials**
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_DEFAULT_REGION

2. **docker-hub** (if applicable)
   - DOCKER_USERNAME
   - DOCKER_PASSWORD

3. **gcp-credentials** (for ApigeeX, if applicable)
   - GCP_SERVICE_ACCOUNT_KEY

---

## Step 7: Deploy to AWS

### 7.1 Trigger Deployment from CircleCI

1. Go to your CircleCI pipeline
2. You'll see the workflow with these jobs:
   - `code-quality-scan` (runs automatically)
   - `build-and-push-image` (runs automatically)
   - `approve-dev-deploy` (MANUAL APPROVAL REQUIRED)
   - `deploy-sagemaker` (runs after approval)
   - `deploy-lambda` (runs after SageMaker)
   - `setup-api-gateway` (runs after Lambda)

3. Click "Approve" on the `approve-dev-deploy` job
4. Watch the deployment progress

### 7.2 Alternative: Deploy from Command Line

```powershell
# Deploy using the deployment package
python "..\api-python-insights-engine-v2-deployment-package\deployment_package\deploy.py" deploy `
  --config release.yaml `
  --environment dev
```

### 7.3 Monitor Deployment

```powershell
# Check SageMaker endpoint status
aws sagemaker describe-endpoint --endpoint-name dssat-model-dev

# Check Lambda function
aws lambda get-function --function-name dssat-model-lambda-dev

# Check API Gateway
aws apigateway get-rest-apis
```

### 7.4 Get API Endpoint

After deployment completes, retrieve your API endpoint:

```powershell
# Get API Gateway URL
aws apigateway get-rest-apis --query 'items[?name==`dssat-model-api-dev`].{id:id}' --output text

# Construct your endpoint URL
# Format: https://{api-id}.execute-api.{region}.amazonaws.com/{stage}/invocations
```

Example:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/dev/invocations
```

### 7.5 Test Production Endpoint

```powershell
# Test the deployed API
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/invocations `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer YOUR_JWT_TOKEN" `
  -d '{
    "weather_data": {
      "temperature_max": [30, 31, 29, 28],
      "temperature_min": [18, 19, 17, 18],
      "rainfall": [0, 5, 10, 0],
      "solar_radiation": [20, 22, 21, 23]
    },
    "soil_type": "CLAY_LOAM",
    "soil_depth": 150,
    "crop_type": "maize",
    "planting_date": "2024-03-15",
    "cultivar": "PIONEER_3394",
    "simulation_start": "2024-03-01",
    "simulation_end": "2024-09-30"
  }'
```

---

## Troubleshooting

### Issue 1: Model Loading Fails

**Error**: `FileNotFoundError: Model file not found`

**Solution**:
1. Ensure your model file is included in the Docker image
2. Update `model_loader.py` to point to the correct path
3. Check Docker build logs: `docker logs dssat-api`

```python
# In model_loader.py, add debug logging
import os
logger.info(f"Model directory contents: {os.listdir(self.model_dir)}")
```

### Issue 2: CircleCI Build Fails

**Error**: `Docker build failed`

**Solution**:
1. Check Dockerfile syntax
2. Verify all files referenced in Dockerfile exist
3. Check CircleCI job logs for specific error
4. Test Docker build locally first

```powershell
# Test build locally
docker build -t dssat-model:test fastapi_app/
```

### Issue 3: SageMaker Deployment Fails

**Error**: `ResourceLimitExceeded`

**Solution**:
1. Check AWS service quotas
2. Try a different instance type
3. Use a different region

```powershell
# Check SageMaker quotas
aws service-quotas get-service-quota `
  --service-code sagemaker `
  --quota-code L-D9E8D9D2
```

### Issue 4: API Gateway Authentication Fails

**Error**: `401 Unauthorized`

**Solution**:
1. Obtain JWT token from Cognito
2. Include token in Authorization header
3. Check token expiration

```powershell
# Get Cognito token
aws cognito-idp initiate-auth `
  --auth-flow USER_PASSWORD_AUTH `
  --client-id YOUR_CLIENT_ID `
  --auth-parameters USERNAME=user@example.com,PASSWORD=yourpassword
```

### Issue 5: Slow Predictions

**Issue**: API responses are slow

**Solution**:
1. Enable Redis caching (already configured)
2. Increase SageMaker instance count
3. Use auto-scaling (already configured)
4. Optimize DSSAT model code

```powershell
# Check cache hit rate in CloudWatch
aws cloudwatch get-metric-statistics `
  --namespace AWS/ElastiCache `
  --metric-name CacheHits `
  --dimensions Name=CacheClusterId,Value=dssat-model-cache
```

### Issue 6: Git Branch Issues

**Error**: `fatal: A branch named 'feature/dssat-model-deployment' already exists`

**Solution**:
```powershell
# Switch to existing branch
git checkout feature/dssat-model-deployment

# Or delete and recreate
git branch -D feature/dssat-model-deployment
git checkout -b feature/dssat-model-deployment
```

---

## Next Steps

### For Development Environment (Dev)
✅ Deploy to dev using CircleCI approval workflow
✅ Test API endpoints with Postman or curl
✅ Monitor CloudWatch metrics and logs
✅ Iterate on model improvements

### For QA Environment
1. Merge feature branch to `qa` branch
2. CircleCI will trigger QA deployment
3. Approve `approve-qa-deploy` job
4. Run integration tests

### For Production Environment
1. Merge `qa` branch to `main` branch
2. CircleCI will trigger prod deployment
3. Approve `approve-prod-deploy` job (requires team lead approval)
4. Monitor production metrics closely
5. Use ApigeeX proxy for production traffic management

---

## Configuration Reference

### Generated `release.yaml` Structure

```yaml
model:
  name: dssat-model
  version: 1.0.0
  description: DSSAT crop simulation model API for Insight Engine 2.0

aws:
  region: us-east-1
  account_id: "123456789012"

sagemaker:
  instance_type: ml.m5.large
  instance_count: 2
  
autoscaling:
  enabled: true
  min_instances: 2
  max_instances: 10
  target_invocations: 1000

cache:
  enabled: true
  ttl: 3600
  instance_type: cache.t3.micro

circleci:
  machine_size: large

api:
  platform: apigateway
  environment: dev
```

### Updating Configuration

To change settings after initialization:

1. Edit `release.yaml` manually
2. Run deployment command with updated config:

```powershell
python "..\api-python-insights-engine-v2-deployment-package\deployment_package\deploy.py" deploy `
  --config release.yaml `
  --environment dev
```

---

## Cost Estimation

Based on your configuration:

| Resource | Type | Cost/Hour | Monthly (730 hrs) |
|----------|------|-----------|-------------------|
| SageMaker | ml.m5.large × 2 | $0.23 | $335.80 |
| Lambda | 512MB, 1M invocations | Pay per use | ~$20 |
| API Gateway | 1M requests | Pay per use | $3.50 |
| ElastiCache | cache.t3.micro | $0.017 | $12.41 |
| **Total** | | | **~$371.71/month** |

> **Note**: Actual costs depend on usage patterns. Auto-scaling will reduce costs during low-traffic periods.

---

## Support

For issues or questions:

1. **Check Documentation**: Review USER_GUIDE.md in deployment package
2. **Check Logs**: CloudWatch Logs for Lambda and SageMaker
3. **CircleCI Support**: Check build logs in CircleCI dashboard
4. **AWS Support**: Use AWS Support Center for quota increases

---

## Appendix: Quick Command Reference

```powershell
# Initialize deployment
python ..\api-python-insights-engine-v2-deployment-package\deployment_package\deploy.py init dssat-model

# Build Docker image
docker build -t dssat-model:latest fastapi_app/

# Run container locally
docker run -d -p 8080:8080 --name dssat-api dssat-model:latest

# Test locally
curl http://localhost:8080/ping

# Push to GitHub
git push origin feature/dssat-model-deployment

# Deploy to AWS
python ..\api-python-insights-engine-v2-deployment-package\deployment_package\deploy.py deploy --config release.yaml --environment dev

# Check SageMaker status
aws sagemaker describe-endpoint --endpoint-name dssat-model-dev

# Check Lambda function
aws lambda get-function --function-name dssat-model-lambda-dev

# View CloudWatch logs
aws logs tail /aws/sagemaker/Endpoints/dssat-model-dev --follow
```

---

**Document Version**: 1.0.0  
**Last Updated**: November 4, 2025  
**Deployment Package Version**: 1.0.0
