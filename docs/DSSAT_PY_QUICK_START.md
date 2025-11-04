# DSSAT-py Quick Start Guide

## 🚀 Deploy Your DSSAT Model in 15 Minutes

This is a streamlined version of the full deployment guide. For detailed instructions, see [DSSAT_PY_DEPLOYMENT_GUIDE.md](./DSSAT_PY_DEPLOYMENT_GUIDE.md).

---

## Visual Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Step 1: Install Deployment Package                                    │
│  ────────────────────────────────────────────────────────────────     │
│  cd C:\...\IE2.0                                                       │
│  git clone https://github.com/RomanAnto/api-python-...                │
│  pip install -r requirements.txt                                       │
│                                                                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Step 2: Navigate to DSSAT-py Repository                              │
│  ────────────────────────────────────────────────────────────────     │
│  cd C:\...\IE2.0\dssat-py                                              │
│                                                                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Step 3: Initialize Deployment (Interactive)                          │
│  ────────────────────────────────────────────────────────────────     │
│  python ..\api-python-...\deploy.py init dssat-model                  │
│                                                                         │
│  Answer prompts:                                                       │
│  ✓ Model name: dssat-model                                            │
│  ✓ Region: us-east-1                                                  │
│  ✓ Instance: ml.m5.large (recommended)                                │
│  ✓ Auto-scaling: Yes (2 min, 10 max)                                  │
│  ✓ Caching: Yes (3600s TTL)                                           │
│                                                                         │
│  Generated:                                                            │
│  ├── fastapi_app/                                                     │
│  ├── .circleci/config.yml                                             │
│  └── release.yaml                                                      │
│                                                                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Step 4: Customize Model Integration                                  │
│  ────────────────────────────────────────────────────────────────     │
│  Edit: fastapi_app/model_loader.py                                    │
│  Edit: fastapi_app/prediction.py                                      │
│  Edit: fastapi_app/requirements.txt (add DSSAT dependencies)          │
│                                                                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Step 5: Test Locally with Docker                                     │
│  ────────────────────────────────────────────────────────────────     │
│  docker build -t dssat-model:latest fastapi_app/                      │
│  docker run -d -p 8080:8080 dssat-model:latest                        │
│  curl http://localhost:8080/ping                                      │
│  curl -X POST http://localhost:8080/invocations -d {...}              │
│                                                                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Step 6: Push to GitHub                                               │
│  ────────────────────────────────────────────────────────────────     │
│  git push origin feature/dssat-model-deployment                        │
│                                                                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Step 7: Configure CircleCI                                           │
│  ────────────────────────────────────────────────────────────────     │
│  1. Connect repository to CircleCI                                    │
│  2. Add environment variables (AWS credentials)                        │
│  3. Create contexts (aws-credentials, docker-hub)                     │
│                                                                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Step 8: Deploy to AWS via CircleCI                                   │
│  ────────────────────────────────────────────────────────────────     │
│  1. Pipeline auto-triggers on push                                    │
│  2. Jobs run: scan → build → approve → deploy                         │
│  3. Approve "approve-dev-deploy" manually                             │
│  4. Watch deployment: SageMaker → Lambda → API Gateway                │
│                                                                         │
│  Result: Live API endpoint! 🎉                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Copy-Paste Commands

### Step 1: Install Deployment Package
```powershell
cd "C:\Users\u836422\OneDrive - Syngenta\Digital Architecture Team\IE2.0"
git clone https://github.com/RomanAnto/api-python-insights-engine-v2-deployment-package.git
cd api-python-insights-engine-v2-deployment-package
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 2-3: Initialize DSSAT Deployment
```powershell
cd "..\dssat-py"
python "..\api-python-insights-engine-v2-deployment-package\deployment_package\deploy.py" init dssat-model
```

**Answer the interactive prompts:**
- Model name: `dssat-model`
- Model version: `1.0.0`
- AWS region: `us-east-1`
- Environment: `1` (dev)
- Instance type: `2` (ml.m5.large)
- Instance count: `2`
- Auto-scaling: `yes`
- Min instances: `2`
- Max instances: `10`
- Target invocations: `1000`
- Enable caching: `yes`
- Cache TTL: `3600`
- CircleCI machine: `3` (large)
- API platform: `1` (API Gateway)

### Step 4: Customize (Example for model_loader.py)
```python
# Edit: fastapi_app/model_loader.py
# Replace the load_model() method with your DSSAT model loading logic

import pickle
import os

class DSSATModelLoader:
    def load_model(self):
        model_path = os.path.join(self.model_dir, "dssat_model.pkl")
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)
        return self.model
```

### Step 5: Test Locally
```powershell
# Build Docker image
docker build -t dssat-model:latest fastapi_app/

# Run container
docker run -d -p 8080:8080 --name dssat-api dssat-model:latest

# Test health endpoint
curl http://localhost:8080/ping

# Test prediction endpoint
curl -X POST http://localhost:8080/invocations `
  -H "Content-Type: application/json" `
  -d '{
    "weather_data": {"temperature_max": [30, 31, 29, 28], "temperature_min": [18, 19, 17, 18], "rainfall": [0, 5, 10, 0], "solar_radiation": [20, 22, 21, 23]},
    "soil_type": "CLAY_LOAM",
    "soil_depth": 150,
    "crop_type": "maize",
    "planting_date": "2024-03-15",
    "cultivar": "PIONEER_3394",
    "simulation_start": "2024-03-01",
    "simulation_end": "2024-09-30"
  }'

# Clean up
docker stop dssat-api ; docker rm dssat-api
```

### Step 6: Push to GitHub
```powershell
# Already on feature/dssat-model-deployment branch
git add .
git commit -m "feat: Customize DSSAT model integration"
git push origin feature/dssat-model-deployment
```

### Step 7-8: Deploy via CircleCI
1. Go to https://circleci.com/
2. Click "Projects" → "Set Up Project"
3. Select `dssat-py` repository
4. Add environment variables:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_DEFAULT_REGION` = `us-east-1`
   - `AWS_ACCOUNT_ID`
5. Watch pipeline run
6. **Click "Approve"** on `approve-dev-deploy` job
7. Get your API endpoint from logs

---

## 🎯 What Gets Deployed?

```
AWS Resources Created:
├── SageMaker Endpoint
│   ├── Model: dssat-model
│   ├── Instance: ml.m5.large (2 instances)
│   └── Auto-scaling: 2-10 instances
│
├── Lambda Function
│   ├── Name: dssat-model-lambda-dev
│   ├── Runtime: Python 3.11
│   ├── Timeout: 15 minutes
│   └── Memory: 512 MB
│
├── ElastiCache (Redis)
│   ├── Instance: cache.t3.micro
│   └── TTL: 3600 seconds (1 hour)
│
└── API Gateway
    ├── Name: dssat-model-api-dev
    ├── Stage: dev
    ├── Auth: Cognito User Pool
    └── Endpoint: https://{api-id}.execute-api.us-east-1.amazonaws.com/dev
```

---

## 🔑 Key Files You'll Customize

| File | Purpose | What to Change |
|------|---------|----------------|
| `fastapi_app/model_loader.py` | Load DSSAT model | Update `load_model()` method with your model loading logic |
| `fastapi_app/prediction.py` | Define API schema | Update `DSSATSimulationInput` and `DSSATSimulationOutput` classes |
| `fastapi_app/requirements.txt` | Python dependencies | Add DSSAT-specific packages (numpy, pandas, etc.) |
| `fastapi_app/Dockerfile` | Container image | Add system dependencies if needed (gfortran, etc.) |

---

## 📊 Monitoring Your Deployment

### Check Deployment Status
```powershell
# SageMaker endpoint
aws sagemaker describe-endpoint --endpoint-name dssat-model-dev

# Lambda function
aws lambda get-function --function-name dssat-model-lambda-dev

# API Gateway
aws apigateway get-rest-apis --query 'items[?name==`dssat-model-api-dev`]'
```

### View Logs
```powershell
# SageMaker logs
aws logs tail /aws/sagemaker/Endpoints/dssat-model-dev --follow

# Lambda logs
aws logs tail /aws/lambda/dssat-model-lambda-dev --follow
```

### CloudWatch Metrics
- Go to AWS Console → CloudWatch → Metrics
- Check:
  - SageMaker: `ModelLatency`, `Invocations`, `ModelSetupTime`
  - Lambda: `Duration`, `Errors`, `Throttles`
  - ElastiCache: `CacheHits`, `CacheMisses`

---

## 💰 Cost Estimate

| Resource | Configuration | Monthly Cost |
|----------|---------------|--------------|
| SageMaker | ml.m5.large × 2 | $335.80 |
| Lambda | 1M invocations, 512MB | $20.00 |
| API Gateway | 1M requests | $3.50 |
| ElastiCache | cache.t3.micro | $12.41 |
| **Total** | | **~$371.71** |

> **Auto-scaling saves costs**: Scales down during low traffic, scales up during peak loads.

---

## 🐛 Common Issues & Quick Fixes

### Issue: "Model file not found"
```powershell
# Fix: Check model file path in model_loader.py
# Ensure model file is copied into Docker image
# Add to Dockerfile: COPY your_model.pkl /opt/ml/model/
```

### Issue: CircleCI build fails
```powershell
# Fix: Test Docker build locally first
docker build -t dssat-model:test fastapi_app/
# Check Dockerfile syntax and file paths
```

### Issue: SageMaker deployment fails with ResourceLimitExceeded
```powershell
# Fix: Request quota increase
aws service-quotas request-service-quota-increase \
  --service-code sagemaker \
  --quota-code L-D9E8D9D2 \
  --desired-value 10
```

### Issue: Slow API responses
```powershell
# Fix 1: Check cache hit rate (already enabled)
# Fix 2: Increase instance count in release.yaml
# Fix 3: Use GPU instance (ml.g4dn.xlarge) for compute-intensive models
```

---

## 🎓 Next Steps

### ✅ Development (Dev)
- You're here! Deploy and test in dev environment
- Iterate on model improvements
- Monitor metrics in CloudWatch

### 🔄 QA Testing
1. Merge feature branch to `qa` branch
2. CircleCI auto-deploys to QA
3. Run integration tests
4. Validate with sample data

### 🚀 Production
1. Merge `qa` to `main` branch
2. CircleCI auto-deploys to prod
3. Requires team lead approval
4. Uses ApigeeX for traffic management
5. Monitor production metrics closely

---

## 📚 Additional Resources

- **Full Guide**: [DSSAT_PY_DEPLOYMENT_GUIDE.md](./DSSAT_PY_DEPLOYMENT_GUIDE.md)
- **User Guide**: [USER_GUIDE.md](./USER_GUIDE.md)
- **Example**: [EXAMPLE_SENTIMENT_CLASSIFIER.md](./EXAMPLE_SENTIMENT_CLASSIFIER.md)
- **Quick Reference**: [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
- **Checklist**: [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)

---

## 🆘 Need Help?

1. **Check logs**: CloudWatch Logs for detailed error messages
2. **Test locally**: Use Docker to debug before deploying
3. **Review config**: Verify `release.yaml` settings
4. **Check quotas**: AWS Service Quotas may need increases

---

**Quick Start Version**: 1.0.0  
**Last Updated**: November 4, 2025  
**Estimated Setup Time**: 15-20 minutes
