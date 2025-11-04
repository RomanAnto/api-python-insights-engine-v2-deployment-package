# Example: Deploy Sentiment Analysis Model

This example demonstrates deploying a sentiment analysis model using the ML deployment package.

## Scenario

Deploy a scikit-learn sentiment classifier trained on product reviews.

## Step 1: Initialize Project

```bash
python deployment_package/deploy.py init sentiment-classifier
```

Configuration choices:
- Environment: `dev`
- Instance type: `ml.m5.xlarge`
- Instance count: `1`
- Caching: `enabled` (3600s TTL)
- Region: `eu-central-1`

## Step 2: Implement Model Logic

### model_loader.py

```python
"""
Sentiment analysis model loader
"""

import joblib
import numpy as np
import os
from typing import Dict, Any

class ModelLoader:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.model_path = os.getenv("MODEL_PATH", "/opt/ml/model")
        self.is_loaded = False
    
    def load_model(self):
        """Load sentiment classifier and vectorizer"""
        model_file = os.path.join(self.model_path, "classifier.pkl")
        vectorizer_file = os.path.join(self.model_path, "vectorizer.pkl")
        
        self.model = joblib.load(model_file)
        self.vectorizer = joblib.load(vectorizer_file)
        self.is_loaded = True
        
        print("✅ Sentiment classifier loaded successfully")
    
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict sentiment from text
        
        Input: {"text": "This product is amazing!"}
        Output: {"prediction": "positive", "confidence": 0.95}
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        # Extract text
        text = input_data.get("text", "")
        
        if not text:
            raise ValueError("Text field is required")
        
        # Vectorize input
        features = self.vectorizer.transform([text])
        
        # Predict
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        confidence = float(probabilities.max())
        
        # Map to sentiment labels
        sentiment_map = {0: "negative", 1: "neutral", 2: "positive"}
        sentiment = sentiment_map.get(prediction, "unknown")
        
        return {
            "prediction": sentiment,
            "confidence": confidence,
            "probabilities": {
                "negative": float(probabilities[0]),
                "neutral": float(probabilities[1]),
                "positive": float(probabilities[2])
            }
        }
```

### prediction.py (customized)

```python
"""
Sentiment prediction endpoint
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Dict, Any
import logging
from datetime import datetime
import time

from model_loader import ModelLoader

router = APIRouter()
logger = logging.getLogger(__name__)
model_loader = ModelLoader()

class SentimentInput(BaseModel):
    """Input schema for sentiment analysis"""
    text: str = Field(..., min_length=1, max_length=5000, 
                     description="Text to analyze for sentiment")
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "text": "This product exceeded my expectations! Highly recommended."
            }
        }

class SentimentOutput(BaseModel):
    """Output schema for sentiment analysis"""
    sentiment: str = Field(..., description="Predicted sentiment (positive/neutral/negative)")
    confidence: float = Field(..., description="Confidence score (0-1)")
    probabilities: Dict[str, float] = Field(..., description="Probability for each class")
    model_version: str = Field(..., description="Model version")
    inference_time_ms: float = Field(..., description="Inference time in milliseconds")
    timestamp: str = Field(..., description="Prediction timestamp")

@router.post("/invocations", response_model=SentimentOutput)
async def analyze_sentiment(input_data: SentimentInput):
    """
    Analyze sentiment of input text
    """
    start_time = time.time()
    
    try:
        logger.info(f"Analyzing sentiment for text of length: {len(input_data.text)}")
        
        # Make prediction
        result = model_loader.predict({"text": input_data.text})
        
        # Calculate inference time
        inference_time = (time.time() - start_time) * 1000
        
        # Format response
        response = SentimentOutput(
            sentiment=result["prediction"],
            confidence=result["confidence"],
            probabilities=result["probabilities"],
            model_version="1.0.0",
            inference_time_ms=round(inference_time, 2),
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Sentiment: {result['prediction']} (confidence: {result['confidence']:.2f})")
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Step 3: Update Dockerfile

Add model files to container:

```dockerfile
# ... existing Dockerfile content ...

# Copy model files
COPY model/classifier.pkl /opt/ml/model/classifier.pkl
COPY model/vectorizer.pkl /opt/ml/model/vectorizer.pkl

# ... rest of Dockerfile ...
```

## Step 4: Update requirements.txt

Add ML dependencies:

```txt
# ... existing requirements ...

# ML libraries
scikit-learn==1.3.2
numpy==1.26.2
```

## Step 5: Test Locally

```bash
# Run application
cd sentiment-classifier
python src/app.py
```

Test with curl:

```bash
# Test health
curl http://localhost:8080/ping

# Test inference
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This product is absolutely fantastic! Best purchase ever."
  }'
```

Expected response:
```json
{
  "sentiment": "positive",
  "confidence": 0.95,
  "probabilities": {
    "negative": 0.02,
    "neutral": 0.03,
    "positive": 0.95
  },
  "model_version": "1.0.0",
  "inference_time_ms": 12.5,
  "timestamp": "2025-11-03T10:30:00.000Z"
}
```

## Step 6: Test with Docker

```bash
# Build
docker build -t sentiment-classifier:local .

# Run
docker run -p 8080:8080 sentiment-classifier:local

# Test
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"text": "Terrible product, waste of money"}'
```

Expected response:
```json
{
  "sentiment": "negative",
  "confidence": 0.92,
  "probabilities": {
    "negative": 0.92,
    "neutral": 0.05,
    "positive": 0.03
  },
  "model_version": "1.0.0",
  "inference_time_ms": 11.8,
  "timestamp": "2025-11-03T10:31:00.000Z"
}
```

## Step 7: Deploy to AWS

```bash
# Commit and push
git add .
git commit -m "feat: Add sentiment classifier deployment"
git push origin feature/deploy-sentiment-classifier

# Wait for CircleCI pipeline
# Approve DEV deployment
# Monitor logs
```

## Step 8: Test Deployed Endpoint

```bash
# Set variables
API_URL="https://abc123.execute-api.eu-central-1.amazonaws.com/dev/invoke"
JWT_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."

# Test positive sentiment
curl -X POST $API_URL \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Amazing product! Would definitely buy again."
  }'

# Test negative sentiment
curl -X POST $API_URL \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Poor quality, broke after one week."
  }'

# Test neutral sentiment
curl -X POST $API_URL \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The product works as described."
  }'
```

## Step 9: Batch Predictions

```bash
curl -X POST $API_URL/batch \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {"text": "Excellent service!"},
    {"text": "Not worth the price."},
    {"text": "Average quality product."}
  ]'
```

## Monitoring

### CloudWatch Metrics

Monitor these metrics:
- `ModelLatency` - Inference time
- `Invocations` - Number of requests
- `ModelInvocation4XXErrors` - Client errors
- `ModelInvocation5XXErrors` - Server errors

### CloudWatch Logs

```bash
# View SageMaker logs
aws logs tail /aws/sagemaker/Endpoints/sentiment-classifier-endpoint-dev --follow

# View Lambda logs
aws logs tail /aws/lambda/sentiment-classifier-lambda-dev --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/sagemaker/Endpoints/sentiment-classifier-endpoint-dev \
  --filter-pattern "ERROR"
```

## Cost Estimation

### Dev Environment (ml.m5.xlarge, 1 instance)

- SageMaker: $0.23/hour × 24 hours = $5.52/day
- Lambda: $0.0000002/request + $0.0000166667/GB-second
- API Gateway: $3.50/million requests
- Redis cache (if enabled): ~$15/month

**Monthly estimate**: ~$180 (assuming 8 hours/day usage)

### Production Environment (ml.m5.xlarge, 2 instances, auto-scaling)

- SageMaker: $0.23/hour × 2 instances × 24 hours = $11.04/day
- Lambda: Higher usage
- ApigeeX: Enterprise pricing

**Monthly estimate**: ~$360+

## Performance Benchmarks

### Local (MacBook Pro M1)
- Cold start: ~2 seconds
- Warm inference: ~10-15ms
- Throughput: ~100 requests/second

### SageMaker (ml.m5.xlarge)
- Cold start: ~60 seconds (endpoint creation)
- Warm inference: ~20-30ms (including Lambda overhead)
- Throughput: ~200 requests/second (per instance)

### With Caching
- Cache hit: ~5ms
- Cache miss: ~30ms (then cached)
- Cache hit rate: ~60-70% (typical)

## Next Steps

1. **Add monitoring alerts**: Set up CloudWatch alarms for errors and latency
2. **Implement A/B testing**: Deploy multiple model versions
3. **Add explainability**: Integrate SHAP or LIME for model explanations
4. **Scale to production**: Enable auto-scaling and multi-region deployment
5. **Optimize costs**: Right-size instances based on actual usage

## Additional Examples

See also:
- [Image Classification Example](examples/image-classifier/)
- [NER Model Example](examples/ner-model/)
- [Recommendation System Example](examples/recommender/)
