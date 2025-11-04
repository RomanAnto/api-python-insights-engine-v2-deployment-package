# ML Deployment Package - Quick Reference

## 🚀 Quick Start Commands

```bash
# Initialize new model deployment
python deployment_package/deploy.py init <model-name>

# Deploy existing project
python deployment_package/deploy.py deploy --config release.yaml --environment dev

# Get help
python deployment_package/deploy.py --help
```

## 📋 Project Structure

```
<model-name>/
├── src/
│   ├── app.py              # Main FastAPI app
│   ├── health.py           # Health endpoints
│   ├── prediction.py       # Inference endpoint
│   └── model_loader.py     # Model loading logic (CUSTOMIZE THIS)
├── tests/
├── Dockerfile
├── requirements.txt
└── release.yaml            # Configuration
```

## ⚙️ Configuration (release.yaml)

```yaml
name: my-model
type: sagemaker

instance:
  type: ml.m5.xlarge        # Instance type
  count: 1                  # Number of instances
  volumeSizeInGB: 50        # EBS volume size
  region: eu-central-1      # AWS region

cache:
  enabled: true             # Enable Redis caching
  ttl: 3600                # Cache TTL (seconds)

autoscaling:
  enabled: false            # Enable auto-scaling
  minInstances: 1
  maxInstances: 4
```

## 🏗️ Instance Types

| Type | vCPUs | Memory | Use Case | $/hour |
|------|-------|--------|----------|--------|
| ml.t3.medium | 2 | 4GB | Dev/Test | $0.05 |
| **ml.m5.xlarge** | 4 | 16GB | **Recommended** | $0.23 |
| ml.c5.xlarge | 4 | 8GB | Compute | $0.204 |
| ml.g4dn.xlarge | 4 | 16GB+GPU | Deep Learning | $0.736 |

## 🔧 Customize Your Model

### 1. Update model_loader.py

```python
def load_model(self):
    """Load your model"""
    model_file = os.path.join(self.model_path, "model.pkl")
    self.model = joblib.load(model_file)
    self.is_loaded = True

def predict(self, input_data):
    """Make prediction"""
    prediction = self.model.predict([input_data])
    return {"prediction": prediction}
```

### 2. Update prediction.py (optional)

```python
class PredictionInput(BaseModel):
    """Define your input schema"""
    feature1: float
    feature2: str
```

### 3. Update Dockerfile

```dockerfile
# Add model files
COPY model/ /opt/ml/model/
```

## 🧪 Local Testing

```bash
# Run locally
python src/app.py

# Test health
curl http://localhost:8080/ping

# Test inference
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"feature1": 1.0}'

# Build Docker
docker build -t my-model:local .
docker run -p 8080:8080 my-model:local
```

## 🚀 Deploy to AWS

```bash
# Commit and push
git add .
git commit -m "feat: Add model deployment"
git push origin feature/deploy-my-model

# CircleCI will:
# 1. Run code quality scan
# 2. Build and push Docker image
# 3. Wait for manual approval
# 4. Deploy to SageMaker
# 5. Deploy Lambda
# 6. Setup API Gateway
# 7. Return API endpoint + key
```

## 🔍 Monitor Deployment

```bash
# View SageMaker logs
aws logs tail /aws/sagemaker/Endpoints/my-model-endpoint-dev --follow

# View Lambda logs
aws logs tail /aws/lambda/my-model-lambda-dev --follow

# Check endpoint status
aws sagemaker describe-endpoint --endpoint-name my-model-endpoint-dev
```

## 🌐 Test Deployed Endpoint

```bash
# Set variables
API_URL="https://<api-id>.execute-api.eu-central-1.amazonaws.com/dev/invoke"
JWT_TOKEN="<token-from-cognito>"

# Make request
curl -X POST $API_URL \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feature1": 1.0}'
```

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Endpoint stuck "Creating" | Check ECR image exists, verify IAM permissions |
| Lambda timeout | Check SageMaker latency, optimize model |
| 401 Unauthorized | Verify JWT token, check Cognito config |
| Docker build fails | Check Dockerfile syntax, verify dependencies |

## 📊 Environment Variables (CircleCI)

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
AWS_ECR_REGISTRY
SAGEMAKER_EXECUTION_ROLE
LAMBDA_EXECUTION_ROLE
SONAR_TOKEN
FURY_TOKEN (optional)
```

## 🔐 API Authentication

### Dev Environment
- Uses AWS Cognito
- JWT token required
- API key returned for testing

### Production Environment
- Uses ApigeeX
- Internal auth service (OAuth/JWT)
- No API key needed

## 📈 Performance Tips

✅ Enable caching (reduces costs by 60-70%)
✅ Start with smaller instances
✅ Use auto-scaling for variable load
✅ Load model once at startup
✅ Implement request batching

## 💰 Cost Estimation

### Dev (ml.m5.xlarge, 8 hours/day)
- SageMaker: ~$1.84/day
- Lambda: ~$0.10/day
- **Total**: ~$60/month

### Prod (ml.m5.xlarge, 2 instances, 24/7)
- SageMaker: ~$330/month
- Lambda: Usage-based
- **Total**: ~$400+/month

## 📚 Documentation

- [README.md](../README.md) - Overview
- [USER_GUIDE.md](USER_GUIDE.md) - Complete guide
- [EXAMPLE_SENTIMENT_CLASSIFIER.md](EXAMPLE_SENTIMENT_CLASSIFIER.md) - Example
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical details

## 🆘 Get Help

- Check logs in CloudWatch
- Review error messages
- Consult USER_GUIDE.md
- Contact: insight-engine-team@syngenta.com
- Slack: #insight-engine-support

---

## 🎯 Typical Workflow

1. **Initialize**: `python deployment_package/deploy.py init my-model`
2. **Customize**: Update `model_loader.py` and `prediction.py`
3. **Test Locally**: Run with Python and Docker
4. **Deploy**: Push to GitHub
5. **Approve**: Approve in CircleCI
6. **Test**: Use returned API endpoint
7. **Monitor**: Check CloudWatch metrics

**Total Time**: 2-3 hours from start to production! 🚀

---

*Syngenta Digital - Insight Engine Team*
*Version 1.0.0 - November 2025*
