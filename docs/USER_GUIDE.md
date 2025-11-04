# ML Deployment Package - User Guide

## Overview

This guide walks you through deploying your ML model to AWS SageMaker using the automated deployment package.

## Step-by-Step Guide

### Step 1: Prepare Your Model

Before using the deployment package, ensure you have:
- A trained ML model (scikit-learn, PyTorch, TensorFlow, etc.)
- Model artifacts saved to disk
- Input/output schema defined
- Test data for validation

### Step 2: Initialize Deployment Project

```bash
cd ie-deployment
python deployment_package/deploy.py init my-sentiment-model
```

This will ask you a series of questions:

#### Environment Selection
```
Select deployment environment:
  1. dev (Development)
  2. qa (Quality Assurance)
  3. staging (Staging)
  4. prod (Production)
Enter choice [1-4] (default: 1): 1
```

**Recommendation**: Start with `dev` for initial deployment.

#### Instance Type Selection
```
Select SageMaker instance type:
  1. ml.t3.medium      - Dev/Test - 2 vCPU, 4GB RAM
  2. ml.m5.large       - General Purpose - 2 vCPU, 8GB RAM
  3. ml.m5.xlarge      - Recommended - 4 vCPU, 16GB RAM
  4. ml.m5.2xlarge     - Medium Load - 8 vCPU, 32GB RAM
  5. ml.c5.xlarge      - Compute Optimized - 4 vCPU, 8GB RAM
  6. ml.c5.2xlarge     - High Performance - 8 vCPU, 16GB RAM
  7. ml.r5.xlarge      - Memory Optimized - 4 vCPU, 32GB RAM
  8. ml.g4dn.xlarge    - GPU Accelerated - 4 vCPU, 16GB RAM, 1 GPU

Enter choice [1-8] (default: 3): 3
```

**Recommendation**: 
- Dev: `ml.t3.medium` (lowest cost)
- Production: `ml.m5.xlarge` or higher
- Deep Learning: `ml.g4dn.xlarge` (GPU)

#### Instance Count
```
Number of instances (default: 1): 1
```

**Recommendation**:
- Dev/QA: 1 instance
- Staging: 2 instances
- Production: 2-4 instances (for high availability)

#### Auto-scaling (Production only)
```
Enable auto-scaling? (y/n, default: n): y
  Minimum instances (default: 1): 2
  Maximum instances (default: 4): 6
  Target invocations per instance (default: 100): 150
```

**Recommendation**: Enable for production to handle variable load.

#### Cache Configuration
```
Enable Redis caching? (y/n, default: y): y
  Cache TTL in seconds (default: 3600): 3600
```

**Recommendation**: Enable caching to reduce costs and improve latency.

#### AWS Region
```
AWS Region (common options):
  1. eu-central-1 (Frankfurt)
  2. us-east-1 (N. Virginia)
  3. us-west-2 (Oregon)
  4. ap-southeast-1 (Singapore)

Enter choice [1-4] or custom region (default: 1): 1
```

**Recommendation**: Choose region closest to your users.

#### Team Name
```
Team name (for tagging, default: ml-team): data-science
```

This is used for resource tagging and cost tracking.

#### Volume Size
```
EBS volume size in GB (default: 50): 50
```

**Recommendation**: 50 GB is sufficient for most models. Increase if your model is very large.

### Step 3: Review Generated Files

After initialization, you'll have:

```
my-sentiment-model/
├── .circleci/
│   └── config.yml          # CircleCI pipeline
├── src/
│   ├── app.py             # FastAPI application
│   ├── health.py          # Health check endpoint
│   ├── prediction.py      # Inference endpoint
│   └── model_loader.py    # Model loading logic
├── tests/
│   ├── test_health.py
│   └── test_inference.py
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
├── release.yaml          # Deployment configuration
└── README.md
```

### Step 4: Implement Model Logic

#### 4.1 Update `src/model_loader.py`

```python
import joblib
import os

class ModelLoader:
    def __init__(self):
        self.model = None
        self.model_path = os.getenv("MODEL_PATH", "/opt/ml/model")
        self.is_loaded = False
    
    def load_model(self):
        """Load your model"""
        model_file = os.path.join(self.model_path, "model.pkl")
        self.model = joblib.load(model_file)
        self.is_loaded = True
    
    def predict(self, input_data):
        """Make prediction"""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        # Extract features from input
        features = [
            input_data.get("feature1"),
            input_data.get("feature2")
        ]
        
        # Make prediction
        prediction = self.model.predict([features])[0]
        confidence = self.model.predict_proba([features])[0].max()
        
        return {
            "prediction": prediction,
            "confidence": float(confidence)
        }
```

#### 4.2 Update `src/prediction.py` (optional)

Customize input validation and output format:

```python
class PredictionInput(BaseModel):
    """Input schema for predictions"""
    text: str = Field(..., description="Input text for sentiment analysis")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "This product is amazing!"
            }
        }
```

### Step 5: Add Your Model Files

Copy your trained model to the project:

```bash
# Create model directory
mkdir -p my-sentiment-model/model

# Copy your model
cp /path/to/trained/model.pkl my-sentiment-model/model/

# Update Dockerfile to copy model
# Add this line before ENTRYPOINT:
# COPY model/ /opt/ml/model/
```

### Step 6: Test Locally

```bash
cd my-sentiment-model

# Install dependencies
pip install -r requirements.txt

# Run locally
python src/app.py

# In another terminal, test
curl http://localhost:8080/ping
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"text": "This is great!"}'
```

### Step 7: Test Docker Build

```bash
# Build container
docker build -t my-sentiment-model:local .

# Run container
docker run -p 8080:8080 my-sentiment-model:local

# Test endpoints
curl http://localhost:8080/ping
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"text": "Test input"}'
```

### Step 8: Configure CircleCI

1. Go to CircleCI dashboard
2. Find your repository
3. Click "Set Up Project"
4. Add environment variables:

```
AWS_ACCESS_KEY_ID       = <your-key-id>
AWS_SECRET_ACCESS_KEY   = <your-secret-key>
AWS_REGION              = eu-central-1
AWS_ECR_REGISTRY        = <account-id>.dkr.ecr.eu-central-1.amazonaws.com
SAGEMAKER_EXECUTION_ROLE = arn:aws:iam::<account>:role/SageMakerRole
LAMBDA_EXECUTION_ROLE   = arn:aws:iam::<account>:role/LambdaRole
SONAR_TOKEN             = <sonar-token>
SONAR_HOST_URL          = <sonar-url>
FURY_TOKEN              = <fury-token> (optional)
```

### Step 9: Deploy

```bash
# Commit changes
git add .
git commit -m "feat: Add sentiment model deployment"
git push origin feature/deploy-my-sentiment-model

# Create pull request
# Or push to main to trigger deployment
```

### Step 10: Monitor Deployment

1. Go to CircleCI dashboard
2. Watch pipeline progress:
   - ✅ Code quality scan
   - ✅ Docker build and push
   - ⏸️ Wait for approval
3. Click "Approve" for DEV deployment
4. Monitor deployment logs:
   - SageMaker endpoint creation (5-10 minutes)
   - Lambda deployment
   - API Gateway setup
5. Copy API endpoint and API key from logs

### Step 11: Test Deployed Endpoint

#### Get JWT Token (Dev environment)

```bash
# Install AWS CLI
aws cognito-idp admin-initiate-auth \
  --user-pool-id <user-pool-id> \
  --client-id <app-client-id> \
  --auth-flow ADMIN_NO_SRP_AUTH \
  --auth-parameters USERNAME=<user>,PASSWORD=<password>
```

#### Test Inference

```bash
API_URL="https://<api-id>.execute-api.eu-central-1.amazonaws.com/dev/invoke"
TOKEN="<jwt-token>"

curl -X POST $API_URL \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is excellent!"}'
```

Expected response:
```json
{
  "prediction": "positive",
  "confidence": 0.95,
  "model_version": "1.0.0",
  "inference_time_ms": 45.2,
  "timestamp": "2025-11-03T10:30:00.000Z"
}
```

### Step 12: Promote to Production

Once validated in Dev:

1. Update `release.yaml`:
   - Increase instance count to 2+
   - Enable auto-scaling
   - Update version number

2. Push changes to trigger production deployment

3. Approve production deployment in CircleCI

4. Production will use ApigeeX instead of API Gateway

## Best Practices

### Model Development
- ✅ Version your models (semantic versioning)
- ✅ Include model metadata (training date, metrics)
- ✅ Test with edge cases locally
- ✅ Validate input schemas strictly

### Cost Optimization
- ✅ Start with smaller instances (ml.t3.medium)
- ✅ Enable caching to reduce SageMaker calls
- ✅ Use auto-scaling for variable load
- ✅ Monitor costs with AWS Cost Explorer

### Security
- ✅ Never commit AWS credentials
- ✅ Use IAM roles with least privilege
- ✅ Enable encryption at rest and in transit
- ✅ Rotate API keys regularly

### Performance
- ✅ Load models once at startup
- ✅ Implement request batching when possible
- ✅ Monitor p95/p99 latency
- ✅ Set appropriate timeout values

### Monitoring
- ✅ Set up CloudWatch alarms for errors
- ✅ Monitor SageMaker metrics (latency, invocations)
- ✅ Track Lambda execution time
- ✅ Review logs regularly

## Troubleshooting Tips

### Build Failures
- Check Dockerfile syntax
- Verify all dependencies in requirements.txt
- Test Docker build locally first

### Deployment Failures
- Check IAM permissions
- Verify ECR image exists
- Review CloudWatch logs
- Check resource quotas

### Inference Errors
- Validate input format
- Check model loading logic
- Review error logs in CloudWatch
- Test with curl/Postman

## Support

For help:
- Check logs in CloudWatch
- Review this guide
- Contact: insight-engine-team@syngenta.com
- Slack: #insight-engine-support
