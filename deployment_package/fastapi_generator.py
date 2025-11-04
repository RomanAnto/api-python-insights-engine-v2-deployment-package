"""
FastAPI wrapper generator for ML models.
Creates a complete FastAPI application structure for SageMaker deployment.
"""

import os
from pathlib import Path
from typing import Dict, Any

class FastAPIGenerator:
    """Generate FastAPI wrapper for ML model deployment"""
    
    def __init__(self, model_name: str, base_path: str = "."):
        self.model_name = model_name
        self.base_path = Path(base_path)
        self.src_path = self.base_path / "src"
        self.tests_path = self.base_path / "tests"
    
    def generate_all(self):
        """Generate complete FastAPI structure"""
        self._create_directories()
        self._generate_app_py()
        self._generate_health_py()
        self._generate_prediction_py()
        self._generate_model_loader_py()
        self._generate_dockerfile()
        self._generate_requirements_txt()
        self._generate_dockerignore()
        self._generate_tests()
        self._generate_readme()
        print(f"✅ FastAPI wrapper generated successfully for {self.model_name}")
    
    def _create_directories(self):
        """Create project directory structure"""
        self.src_path.mkdir(parents=True, exist_ok=True)
        self.tests_path.mkdir(parents=True, exist_ok=True)
        (self.src_path / "__init__.py").touch()
        (self.tests_path / "__init__.py").touch()
    
    def _generate_app_py(self):
        """Generate main FastAPI application"""
        content = '''"""
Main FastAPI application for {model_name}
SageMaker BYOC deployment
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import sys

from health import router as health_router
from prediction import router as prediction_router
from model_loader import ModelLoader

# Initialize FastAPI
app = FastAPI(
    title="{model_name} API",
    description="SageMaker BYOC Model Inference Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Global model loader
model_loader = ModelLoader()

# Include routers
app.include_router(health_router, tags=["Health"])
app.include_router(prediction_router, tags=["Prediction"])

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    logger.info("🚀 Starting {model_name} service...")
    try:
        model_loader.load_model()
        logger.info("✅ Model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {{str(e)}}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down {model_name} service...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {{
        "service": "{model_name}",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {{
            "health": "/ping or /health",
            "inference": "/invocations",
            "docs": "/docs"
        }}
    }}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info",
        access_log=True
    )
'''.format(model_name=self.model_name)
        
        with open(self.src_path / "app.py", "w") as f:
            f.write(content)
    
    def _generate_health_py(self):
        """Generate health check endpoint"""
        content = '''"""
Health check endpoint for SageMaker container
Must return 200 for container to be considered healthy
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import psutil
import os

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/ping")
@router.get("/health")
async def health_check():
    """
    SageMaker health check endpoint
    Returns 200 if container is ready to serve predictions
    """
    try:
        # Check if model is loaded (implement your check)
        model_loaded = True  # TODO: Implement actual model loading check
        
        if not model_loaded:
            logger.warning("Health check failed: Model not loaded")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "DOWN",
                    "message": "Model not loaded",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "UP",
                "model_loaded": True,
                "timestamp": datetime.utcnow().isoformat(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "pid": os.getpid()
                }
            }
        )
    
    except Exception as e:
        logger.error(f"Health check error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "status": "DOWN",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@router.get("/readiness")
async def readiness_check():
    """Kubernetes-style readiness check"""
    return await health_check()

@router.get("/liveness")
async def liveness_check():
    """Kubernetes-style liveness check"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "ALIVE",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
'''
        
        with open(self.src_path / "health.py", "w") as f:
            f.write(content)
    
    def _generate_prediction_py(self):
        """Generate prediction endpoint"""
        content = '''"""
Main inference endpoint for ML predictions
Handles POST requests to /invocations
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import time

from model_loader import ModelLoader

router = APIRouter()
logger = logging.getLogger(__name__)
model_loader = ModelLoader()

# Input schema (customize based on your model)
class PredictionInput(BaseModel):
    """Input schema for predictions"""
    features: Dict[str, Any] = Field(..., description="Input features for prediction")
    
    class Config:
        schema_extra = {
            "example": {
                "features": {
                    "feature1": 1.0,
                    "feature2": 2.0,
                    "feature3": "category_a"
                }
            }
        }

# Output schema (customize based on your model)
class PredictionOutput(BaseModel):
    """Output schema for predictions"""
    prediction: Any = Field(..., description="Model prediction")
    confidence: Optional[float] = Field(None, description="Prediction confidence score")
    model_version: str = Field(..., description="Model version")
    inference_time_ms: float = Field(..., description="Inference time in milliseconds")
    timestamp: str = Field(..., description="Prediction timestamp")

@router.post("/invocations", response_model=PredictionOutput)
async def invoke(request: Request):
    """
    Main inference endpoint
    Accepts JSON input and returns model predictions
    """
    start_time = time.time()
    
    try:
        # Parse input
        input_data = await request.json()
        logger.info(f"Received inference request: {type(input_data)}")
        
        # Validate input
        if not input_data:
            raise HTTPException(status_code=400, detail="Empty input data")
        
        # TODO: Implement your preprocessing logic
        processed_input = preprocess_input(input_data)
        
        # Make prediction
        # TODO: Replace with actual model inference
        prediction_result = model_loader.predict(processed_input)
        
        # Calculate inference time
        inference_time = (time.time() - start_time) * 1000
        
        # Format response
        response = PredictionOutput(
            prediction=prediction_result.get("prediction"),
            confidence=prediction_result.get("confidence"),
            model_version="1.0.0",
            inference_time_ms=round(inference_time, 2),
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Prediction successful (took {inference_time:.2f}ms)")
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

def preprocess_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Preprocess input data before prediction
    TODO: Implement your preprocessing logic
    """
    # Example preprocessing
    features = input_data.get("features", input_data)
    
    # Validate required features
    # if "required_feature" not in features:
    #     raise ValueError("Missing required feature: required_feature")
    
    return features

@router.post("/batch-invocations")
async def batch_invoke(request: Request):
    """
    Batch inference endpoint for processing multiple predictions
    """
    start_time = time.time()
    
    try:
        input_batch = await request.json()
        
        if not isinstance(input_batch, list):
            raise HTTPException(status_code=400, detail="Input must be a list")
        
        results = []
        for item in input_batch:
            processed_input = preprocess_input(item)
            prediction = model_loader.predict(processed_input)
            results.append(prediction)
        
        inference_time = (time.time() - start_time) * 1000
        
        return ORJSONResponse(content={
            "predictions": results,
            "count": len(results),
            "inference_time_ms": round(inference_time, 2),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Batch prediction failed")
'''
        
        with open(self.src_path / "prediction.py", "w") as f:
            f.write(content)
    
    def _generate_model_loader_py(self):
        """Generate model loader module"""
        content = '''"""
Model loader module
Handles loading and initializing the ML model
"""

import logging
import os
from typing import Dict, Any
import joblib
import pickle

logger = logging.getLogger(__name__)

class ModelLoader:
    """Load and manage ML model"""
    
    def __init__(self):
        self.model = None
        self.model_path = os.getenv("MODEL_PATH", "/opt/ml/model")
        self.is_loaded = False
    
    def load_model(self):
        """
        Load model from disk
        TODO: Implement your model loading logic
        """
        try:
            logger.info(f"Loading model from {self.model_path}")
            
            # Example: Load scikit-learn model
            # model_file = os.path.join(self.model_path, "model.pkl")
            # self.model = joblib.load(model_file)
            
            # Example: Load PyTorch model
            # import torch
            # model_file = os.path.join(self.model_path, "model.pt")
            # self.model = torch.load(model_file)
            # self.model.eval()
            
            # Example: Load TensorFlow model
            # import tensorflow as tf
            # self.model = tf.keras.models.load_model(self.model_path)
            
            # For now, just mark as loaded
            self.is_loaded = True
            logger.info("✅ Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}", exc_info=True)
            raise
    
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction with loaded model
        TODO: Implement your prediction logic
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            # TODO: Implement actual prediction logic
            # Example for scikit-learn:
            # prediction = self.model.predict([input_data])
            
            # Example for PyTorch:
            # import torch
            # with torch.no_grad():
            #     prediction = self.model(torch.tensor(input_data))
            
            # Placeholder response
            prediction_result = {
                "prediction": "placeholder_prediction",
                "confidence": 0.95
            }
            
            return prediction_result
        
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}", exc_info=True)
            raise
    
    def unload_model(self):
        """Unload model from memory"""
        self.model = None
        self.is_loaded = False
        logger.info("Model unloaded")
'''
        
        with open(self.src_path / "model_loader.py", "w") as f:
            f.write(content)
    
    def _generate_dockerfile(self):
        """Generate Dockerfile"""
        content = '''# Multi-stage build for optimized image size
FROM python:3.11-slim-bullseye AS builder

# Build arguments
ARG FURY_URL=https://pypi.fury.io/syngenta-digital/
ARG FURY_TOKEN
ENV FURY_AUTH=$FURY_TOKEN

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim-bullseye

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \\
    libgomp1 \\
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/

# Create model directory
RUN mkdir -p /opt/ml/model

# Set environment variables
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=/opt/ml/model

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8080/ping')"

# Run application
ENTRYPOINT ["python", "src/app.py"]
'''
        
        with open(self.base_path / "Dockerfile", "w") as f:
            f.write(content)
    
    def _generate_requirements_txt(self):
        """Generate requirements.txt"""
        content = '''# FastAPI and web framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6

# HTTP and JSON
httpx==0.25.1
orjson==3.9.10
requests==2.31.0

# ML libraries (uncomment as needed)
# scikit-learn==1.3.2
# numpy==1.26.2
# pandas==2.1.3
# torch==2.1.0
# tensorflow==2.14.0

# Monitoring and utilities
psutil==5.9.6
python-json-logger==2.0.7

# AWS SDK (if needed)
boto3==1.29.7
botocore==1.32.7

# Model serialization
joblib==1.3.2
'''
        
        with open(self.base_path / "requirements.txt", "w") as f:
            f.write(content)
    
    def _generate_dockerignore(self):
        """Generate .dockerignore"""
        content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# Testing
.pytest_cache/
.coverage
htmlcov/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# Git
.git/
.gitignore

# CI/CD
.circleci/
.github/

# Documentation
*.md
docs/

# Tests
tests/
'''
        
        with open(self.base_path / ".dockerignore", "w") as f:
            f.write(content)
    
    def _generate_tests(self):
        """Generate test files"""
        test_health = '''"""
Unit tests for health endpoint
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_ping_endpoint():
    """Test /ping endpoint returns 200"""
    response = client.get("/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "timestamp" in data

def test_health_endpoint():
    """Test /health endpoint returns 200"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"

def test_readiness_endpoint():
    """Test /readiness endpoint"""
    response = client.get("/readiness")
    assert response.status_code == 200

def test_liveness_endpoint():
    """Test /liveness endpoint"""
    response = client.get("/liveness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ALIVE"
'''
        
        test_inference = '''"""
Unit tests for inference endpoint
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_invocations_endpoint():
    """Test /invocations endpoint with valid input"""
    payload = {
        "features": {
            "feature1": 1.0,
            "feature2": 2.0
        }
    }
    response = client.post("/invocations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "timestamp" in data

def test_invocations_empty_input():
    """Test /invocations with empty input"""
    response = client.post("/invocations", json={})
    # Should handle gracefully

def test_batch_invocations():
    """Test batch predictions"""
    payload = [
        {"features": {"feature1": 1.0}},
        {"features": {"feature1": 2.0}}
    ]
    response = client.post("/batch-invocations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert data["count"] == 2
'''
        
        with open(self.tests_path / "test_health.py", "w") as f:
            f.write(test_health)
        
        with open(self.tests_path / "test_inference.py", "w") as f:
            f.write(test_inference)
    
    def _generate_readme(self):
        """Generate README.md"""
        content = f'''# {self.model_name} - SageMaker Deployment

ML model inference service deployed on AWS SageMaker using BYOC (Bring Your Own Container).

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run locally:**
```bash
python src/app.py
```

3. **Test health endpoint:**
```bash
curl http://localhost:8080/ping
```

4. **Test inference:**
```bash
curl -X POST http://localhost:8080/invocations \\
  -H "Content-Type: application/json" \\
  -d '{{"features": {{"feature1": 1.0}}}}'
```

### Docker Build

```bash
docker build -t {self.model_name}:local .
docker run -p 8080:8080 {self.model_name}:local
```

## 📁 Project Structure

```
.
├── src/
│   ├── app.py              # Main FastAPI application
│   ├── health.py           # Health check endpoints
│   ├── prediction.py       # Inference endpoints
│   └── model_loader.py     # Model loading logic
├── tests/
│   ├── test_health.py      # Health endpoint tests
│   └── test_inference.py   # Inference tests
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
└── release.yaml           # Deployment configuration
```

## 🔧 Configuration

Edit `release.yaml` to configure deployment settings:
- Instance type and count
- Auto-scaling settings
- Cache configuration
- AWS region

## 🧪 Testing

```bash
pytest tests/
```

## 📦 Deployment

Push to main branch to trigger CircleCI pipeline:
```bash
git add .
git commit -m "Update model"
git push origin main
```

## 📊 API Documentation

Once running, visit:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## 🔍 Monitoring

- CloudWatch Logs: `/aws/sagemaker/Endpoints/{self.model_name}-endpoint`
- Metrics: SageMaker Console > Endpoints > {self.model_name}-endpoint
'''
        
        with open(self.base_path / "README.md", "w") as f:
            f.write(content)


def generate_fastapi_wrapper(model_name: str, output_path: str = "."):
    """
    Generate complete FastAPI wrapper for ML model
    
    Args:
        model_name: Name of the model
        output_path: Output directory path
    """
    generator = FastAPIGenerator(model_name, output_path)
    generator.generate_all()
    return generator
