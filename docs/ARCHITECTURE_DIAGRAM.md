# Architecture Diagram - DSSAT-py Deployment

## Complete Deployment Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DEVELOPER WORKSTATION                                 │
│                                                                               │
│  C:\...\dssat-py Repository                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                       │   │
│  │  1. Run: python ..\deployment_package\deploy.py init dssat-model    │   │
│  │                                                                       │   │
│  │  Generated Files:                                                    │   │
│  │  ├── fastapi_app/                                                   │   │
│  │  │   ├── app.py                    (FastAPI main application)       │   │
│  │  │   ├── health.py                 (Health check endpoints)         │   │
│  │  │   ├── prediction.py             (DSSAT inference logic)          │   │
│  │  │   ├── model_loader.py           (Load DSSAT model)               │   │
│  │  │   ├── requirements.txt          (Python dependencies)            │   │
│  │  │   └── Dockerfile                (Multi-stage container)          │   │
│  │  ├── .circleci/config.yml          (CI/CD pipeline)                 │   │
│  │  └── release.yaml                  (Deployment configuration)       │   │
│  │                                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    │ git push                                 │
│                                    ▼                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              GITHUB REPOSITORY                                │
│                                                                               │
│  github.com/your-org/dssat-py                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                       │   │
│  │  Branch: feature/dssat-model-deployment                             │   │
│  │  ├── fastapi_app/                                                   │   │
│  │  ├── .circleci/config.yml                                           │   │
│  │  └── release.yaml                                                    │   │
│  │                                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    │ Webhook trigger                          │
│                                    ▼                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              CIRCLECI PIPELINE                                │
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Job 1: Code Quality Scan                                             │  │
│  │ ├── Checkout code                                                    │  │
│  │ ├── SonarCloud analysis                                              │  │
│  │ └── Quality gate check                                               │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                          │
│                                    ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Job 2: Build & Push Docker Image                                     │  │
│  │ ├── Build: docker build -t dssat-model:1.0.0 .                       │  │
│  │ ├── Tag: dssat-model:1.0.0 → {account}.dkr.ecr.us-east-1...         │  │
│  │ └── Push to AWS ECR                                                  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                          │
│                                    ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Job 3: Approve Dev Deploy (MANUAL APPROVAL)                          │  │
│  │ └── ⏸️  Waiting for approval...                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                          │
│                                    │ ✅ Approved                              │
│                                    ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Job 4: Deploy SageMaker Endpoint                                     │  │
│  │ ├── Create SageMaker Model                                           │  │
│  │ ├── Create Endpoint Config (ml.m5.large × 2)                         │  │
│  │ ├── Create/Update Endpoint                                           │  │
│  │ └── Wait for InService status                                        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                          │
│                                    ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Job 5: Deploy Lambda Function                                        │  │
│  │ ├── Create Lambda deployment package                                 │  │
│  │ ├── Deploy function (Python 3.11, 512MB, 15min timeout)              │  │
│  │ └── Configure Redis caching layer                                    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                          │
│                                    ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Job 6: Setup API Gateway (Dev) / ApigeeX (Stage/Prod)                │  │
│  │ ├── Create REST API                                                  │  │
│  │ ├── Create Cognito User Pool + Authorizer                            │  │
│  │ ├── Create /invocations endpoint                                     │  │
│  │ └── Deploy to dev stage                                              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ Deployment complete
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AWS INFRASTRUCTURE                               │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ AWS ECR (Container Registry)                                         │   │
│  │ └── Image: 123456789.dkr.ecr.us-east-1.amazonaws.com/dssat:1.0.0   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    │ Pulls image                              │
│                                    ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ AWS SageMaker Endpoint                                               │   │
│  │ ┌──────────────────────────────────────────────────────────────────┐ │   │
│  │ │ Endpoint: dssat-model-dev                                        │ │   │
│  │ │ ├── Instance 1: ml.m5.large                                      │ │   │
│  │ │ │   └── Container: dssat-model:1.0.0                             │ │   │
│  │ │ │       ├── FastAPI app (port 8080)                              │ │   │
│  │ │ │       ├── DSSAT model loaded                                   │ │   │
│  │ │ │       └── Health checks: /ping, /health                        │ │   │
│  │ │ └── Instance 2: ml.m5.large                                      │ │   │
│  │ │     └── Container: dssat-model:1.0.0                             │ │   │
│  │ │         ├── FastAPI app (port 8080)                              │ │   │
│  │ │         ├── DSSAT model loaded                                   │ │   │
│  │ │         └── Health checks: /ping, /health                        │ │   │
│  │ │                                                                    │ │   │
│  │ │ Auto-scaling Configuration:                                       │ │   │
│  │ │ ├── Min: 2 instances                                             │ │   │
│  │ │ ├── Max: 10 instances                                            │ │   │
│  │ │ └── Target: 1000 invocations/instance                            │ │   │
│  │ └──────────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    │ Invokes                                  │
│                                    ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ AWS Lambda Function                                                  │   │
│  │ ┌──────────────────────────────────────────────────────────────────┐ │   │
│  │ │ Function: dssat-model-lambda-dev                                 │ │   │
│  │ │ Runtime: Python 3.11                                             │ │   │
│  │ │ Memory: 512 MB                                                   │ │   │
│  │ │ Timeout: 15 minutes                                              │ │   │
│  │ │                                                                    │ │   │
│  │ │ Logic Flow:                                                       │ │   │
│  │ │ 1. Receive request                                               │ │   │
│  │ │ 2. Generate cache key (SHA256 of input)                          │ │   │
│  │ │ 3. Check Redis cache                                             │ │   │
│  │ │    ├── Cache hit → Return cached result                          │ │   │
│  │ │    └── Cache miss → Invoke SageMaker                             │ │   │
│  │ │ 4. Store result in cache (TTL: 3600s)                            │ │   │
│  │ │ 5. Return result                                                 │ │   │
│  │ └──────────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                │                                  │                           │
│                │ Cache lookup                     │ Cache store               │
│                ▼                                  ▼                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ AWS ElastiCache (Redis)                                              │   │
│  │ ├── Instance: cache.t3.micro                                        │   │
│  │ ├── TTL: 3600 seconds (1 hour)                                      │   │
│  │ └── Cache keys: SHA256(input_json)                                  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    ▲                                          │
│                                    │ Triggered by                             │
│                                    │                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ AWS API Gateway (Dev Environment)                                    │   │
│  │ ┌──────────────────────────────────────────────────────────────────┐ │   │
│  │ │ REST API: dssat-model-api-dev                                    │ │   │
│  │ │ Stage: dev                                                       │ │   │
│  │ │                                                                    │ │   │
│  │ │ Endpoints:                                                        │ │   │
│  │ │ ├── POST /invocations                                            │ │   │
│  │ │ │   ├── Authorizer: Cognito JWT                                 │ │   │
│  │ │ │   ├── Integration: Lambda Proxy                               │ │   │
│  │ │ │   └── Target: dssat-model-lambda-dev                          │ │   │
│  │ │ │                                                                  │ │   │
│  │ │ └── GET /health                                                  │ │   │
│  │ │     └── Integration: Lambda Proxy                               │ │   │
│  │ │                                                                    │ │   │
│  │ │ URL: https://{api-id}.execute-api.us-east-1.amazonaws.com/dev   │ │   │
│  │ └──────────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    │ Authenticated via                        │
│                                    ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ AWS Cognito User Pool                                                │   │
│  │ ├── User Pool: dssat-model-users-dev                                │   │
│  │ ├── App Client: dssat-model-client                                  │   │
│  │ └── JWT Token validation                                            │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ API requests
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT APPLICATIONS                              │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ Python Client Example:                                               │   │
│  │                                                                        │   │
│  │ import requests                                                       │   │
│  │                                                                        │   │
│  │ # Get JWT token from Cognito                                         │   │
│  │ token = get_cognito_token(username, password)                        │   │
│  │                                                                        │   │
│  │ # Make prediction request                                            │   │
│  │ response = requests.post(                                            │   │
│  │     "https://abc123.execute-api.us-east-1.amazonaws.com/dev/invocations",│  │
│  │     headers={"Authorization": f"Bearer {token}"},                    │   │
│  │     json={                                                            │   │
│  │         "weather_data": {...},                                       │   │
│  │         "soil_type": "CLAY_LOAM",                                    │   │
│  │         "crop_type": "maize",                                        │   │
│  │         ...                                                           │   │
│  │     }                                                                 │   │
│  │ )                                                                     │   │
│  │                                                                        │   │
│  │ # Get DSSAT simulation results                                       │   │
│  │ result = response.json()                                             │   │
│  │ print(f"Grain yield: {result['grain_yield']} kg/ha")                │   │
│  │ print(f"Simulation time: {result['simulation_time_ms']} ms")        │   │
│  │                                                                        │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Request Flow - Step by Step

### 1️⃣ Client Makes Request

```
Client Application
    │
    │ POST /invocations
    │ Authorization: Bearer {jwt_token}
    │ Content-Type: application/json
    │ Body: {weather_data, soil_type, crop_type, ...}
    │
    ▼
API Gateway
```

### 2️⃣ API Gateway Validates Authentication

```
API Gateway
    │
    │ Validates JWT token with Cognito
    │
    ├──[Token Invalid]──► 401 Unauthorized
    │
    └──[Token Valid]──┐
                      │
                      ▼
                  Lambda Function
```

### 3️⃣ Lambda Checks Cache

```
Lambda Function
    │
    │ 1. Generate cache key: SHA256(request_body)
    │ 2. Query Redis: GET cache_key
    │
    ├──[Cache Hit]──┐
    │               │ Return cached result (fast! <10ms)
    │               └──► Client receives result
    │
    └──[Cache Miss]─┐
                    │
                    ▼
              SageMaker Endpoint
```

### 4️⃣ SageMaker Processes Request

```
SageMaker Endpoint
    │
    │ POST /invocations to ml.m5.large instance
    │
    ▼
FastAPI Container
    │
    ├── Load DSSAT model (if not loaded)
    ├── Parse input (weather, soil, crop parameters)
    ├── Run DSSAT simulation
    ├── Format output (yield, dates, metrics)
    │
    └──► Return prediction
         │
         ▼
    Lambda Function
```

### 5️⃣ Lambda Stores Result & Returns

```
Lambda Function
    │
    │ 1. Store in Redis: SET cache_key result TTL 3600
    │ 2. Return result to client
    │
    ▼
API Gateway
    │
    ▼
Client receives result
```

---

## Data Flow Example

### Input (from Client)

```json
{
  "weather_data": {
    "temperature_max": [30, 31, 29, 28, 30, 32, 31],
    "temperature_min": [18, 19, 17, 18, 19, 20, 19],
    "rainfall": [0, 5, 10, 0, 15, 20, 5],
    "solar_radiation": [20, 22, 21, 23, 22, 24, 23]
  },
  "soil_type": "CLAY_LOAM",
  "soil_depth": 150,
  "crop_type": "maize",
  "planting_date": "2024-03-15",
  "cultivar": "PIONEER_3394",
  "simulation_start": "2024-03-01",
  "simulation_end": "2024-09-30"
}
```

### Processing in SageMaker

```
FastAPI App → model_loader.py → DSSAT Model
                                     │
                                     │ Run simulation
                                     │
                                     ▼
                              Simulation Results
```

### Output (to Client)

```json
{
  "grain_yield": 8542.5,
  "biomass_yield": 15234.8,
  "anthesis_date": "2024-06-15",
  "maturity_date": "2024-09-10",
  "growing_season_days": 179,
  "water_use": 650.3,
  "nitrogen_uptake": 185.2,
  "prediction_confidence": 0.94,
  "simulation_time_ms": 245.3
}
```

---

## Monitoring & Observability

### CloudWatch Metrics

```
┌─────────────────────────────────────────────────────────┐
│ AWS CloudWatch Dashboards                                │
│                                                           │
│ ┌───────────────────────────────────────────────────┐   │
│ │ SageMaker Metrics                                 │   │
│ │ ├── ModelLatency: 200-500ms                       │   │
│ │ ├── Invocations: 1,234/hour                       │   │
│ │ ├── CPUUtilization: 45%                           │   │
│ │ └── MemoryUtilization: 62%                        │   │
│ └───────────────────────────────────────────────────┘   │
│                                                           │
│ ┌───────────────────────────────────────────────────┐   │
│ │ Lambda Metrics                                    │   │
│ │ ├── Duration: 250ms (avg)                         │   │
│ │ ├── Invocations: 1,500/hour                       │   │
│ │ ├── Errors: 2 (0.13%)                             │   │
│ │ └── Throttles: 0                                  │   │
│ └───────────────────────────────────────────────────┘   │
│                                                           │
│ ┌───────────────────────────────────────────────────┐   │
│ │ ElastiCache Metrics                               │   │
│ │ ├── CacheHits: 980 (65%)                          │   │
│ │ ├── CacheMisses: 520 (35%)                        │   │
│ │ ├── CPUUtilization: 15%                           │   │
│ │ └── NetworkBytesOut: 2.5 MB                       │   │
│ └───────────────────────────────────────────────────┘   │
│                                                           │
│ ┌───────────────────────────────────────────────────┐   │
│ │ API Gateway Metrics                               │   │
│ │ ├── Count: 1,500 requests/hour                    │   │
│ │ ├── Latency: 300ms (avg)                          │   │
│ │ ├── 4XXError: 5                                   │   │
│ │ └── 5XXError: 1                                   │   │
│ └───────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### CloudWatch Logs

```
Log Groups:
├── /aws/sagemaker/Endpoints/dssat-model-dev
│   └── [Container logs, model loading, predictions]
│
├── /aws/lambda/dssat-model-lambda-dev
│   └── [Lambda invocations, cache operations, errors]
│
└── /aws/apigateway/dssat-model-api-dev
    └── [API requests, authentication, throttling]
```

---

## Scaling Behavior

### Auto-scaling in Action

```
Time    │ Requests/Min │ Instances │ Action
────────┼──────────────┼───────────┼────────────────────────
09:00   │     500      │     2     │ Normal load
09:15   │   1,200      │     2     │ Approaching target
09:20   │   2,500      │     3     │ ⬆️ Scale up (+1)
09:25   │   4,000      │     5     │ ⬆️ Scale up (+2)
09:30   │   8,000      │     8     │ ⬆️ Scale up (+3)
10:00   │   9,500      │    10     │ ⬆️ Max capacity
11:00   │   3,000      │    10     │ High load continues
12:00   │   1,500      │     8     │ ⬇️ Scale down (-2)
13:00   │     800      │     4     │ ⬇️ Scale down (-4)
14:00   │     400      │     2     │ ⬇️ Min capacity
```

### Cache Performance

```
Request Pattern │ Cache Hit Rate │ Avg Latency │ Cost Savings
────────────────┼────────────────┼─────────────┼─────────────
Repeated queries│      85%       │   15ms      │    $42/day
Unique queries  │      20%       │  280ms      │    $8/day
Mixed workload  │      65%       │   95ms      │    $28/day
```

---

## Cost Breakdown

### Monthly Costs (Dev Environment)

```
┌─────────────────────────────────────────────────────────┐
│ Resource          │ Configuration    │ Monthly Cost     │
├───────────────────┼──────────────────┼──────────────────┤
│ SageMaker         │ ml.m5.large × 2  │ $335.80          │
│ Lambda            │ 1M invocations   │  $20.00          │
│ API Gateway       │ 1M requests      │   $3.50          │
│ ElastiCache       │ cache.t3.micro   │  $12.41          │
│ CloudWatch        │ Logs + Metrics   │   $5.00          │
├───────────────────┼──────────────────┼──────────────────┤
│ Total (Fixed)     │                  │ $376.71          │
└─────────────────────────────────────────────────────────┘

With Auto-scaling (variable load):
├── Low traffic hours (off-peak): $200/month
├── Normal traffic: $377/month
└── Peak traffic (max scale): $1,200/month
```

---

**Document Version**: 1.0.0  
**Last Updated**: November 4, 2025  
**Deployment Package Version**: 1.0.0
