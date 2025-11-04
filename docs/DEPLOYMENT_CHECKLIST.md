# Deployment Checklist

Use this checklist to ensure your ML model deployment is successful.

## ☑️ Pre-Deployment Checklist

### Prerequisites
- [ ] Python 3.11+ installed
- [ ] Docker Desktop installed and running
- [ ] Git installed and configured
- [ ] AWS CLI v2 installed
- [ ] Access to AWS account
- [ ] Access to CircleCI
- [ ] Access to GitHub/Bitbucket repository

### Model Preparation
- [ ] Model is trained and validated
- [ ] Model artifacts are saved to disk
- [ ] Model file size is reasonable (<500MB recommended)
- [ ] Input/output schema is documented
- [ ] Test data prepared for validation
- [ ] Model performance metrics documented

### Account Access
- [ ] GitHub organization access
- [ ] GitHub repository creation permissions
- [ ] CircleCI account linked to GitHub
- [ ] AWS IAM user or role created
- [ ] SageMaker permissions granted
- [ ] Lambda permissions granted
- [ ] ECR permissions granted
- [ ] API Gateway permissions granted
- [ ] Cognito permissions granted

## ☑️ Project Setup Checklist

### Step 1: Clone Repository
- [ ] Repository cloned to local machine
- [ ] Navigate to `ie-deployment` directory
- [ ] Install dependencies: `pip install -r requirements.txt`

### Step 2: Initialize Project
- [ ] Run: `python deployment_package/deploy.py init <model-name>`
- [ ] Environment selected (dev/qa/staging/prod)
- [ ] Instance type selected
- [ ] Instance count configured
- [ ] Auto-scaling configured (if prod)
- [ ] Cache settings configured
- [ ] AWS region selected
- [ ] Team name provided
- [ ] Volume size set
- [ ] Configuration confirmed

### Step 3: Verify Generated Files
- [ ] `src/` directory created
- [ ] `src/app.py` exists
- [ ] `src/health.py` exists
- [ ] `src/prediction.py` exists
- [ ] `src/model_loader.py` exists
- [ ] `tests/` directory created
- [ ] `Dockerfile` created
- [ ] `requirements.txt` created
- [ ] `release.yaml` created
- [ ] `.circleci/config.yml` created or updated
- [ ] `README.md` created

## ☑️ Code Implementation Checklist

### Model Loading
- [ ] Copy model files to project directory
- [ ] Update `model_loader.py` with model loading logic
- [ ] Test model loading locally
- [ ] Verify model predictions work
- [ ] Add any custom preprocessing logic
- [ ] Update `requirements.txt` with model dependencies

### API Customization
- [ ] Update `prediction.py` input schema (if needed)
- [ ] Update `prediction.py` output schema (if needed)
- [ ] Add input validation logic
- [ ] Add custom error handling
- [ ] Update API documentation in docstrings

### Docker Configuration
- [ ] Update `Dockerfile` to copy model files
- [ ] Add any system dependencies to `Dockerfile`
- [ ] Update Python dependencies in `requirements.txt`
- [ ] Test Docker build: `docker build -t <model>:local .`
- [ ] Verify container size is reasonable (<2GB recommended)

### Configuration Review
- [ ] Review `release.yaml` settings
- [ ] Verify instance type is appropriate
- [ ] Confirm instance count for environment
- [ ] Check cache settings
- [ ] Verify AWS region
- [ ] Confirm volume size is adequate

## ☑️ Local Testing Checklist

### Python Testing
- [ ] Run app locally: `python src/app.py`
- [ ] App starts without errors
- [ ] Health endpoint works: `curl http://localhost:8080/ping`
- [ ] Health returns status: "UP"
- [ ] Inference endpoint accessible: `POST http://localhost:8080/invocations`
- [ ] Sample prediction returns valid result
- [ ] Error handling works with invalid input
- [ ] Logs appear in console

### Docker Testing
- [ ] Build succeeds: `docker build -t <model>:local .`
- [ ] No build errors or warnings
- [ ] Image size is reasonable
- [ ] Container starts: `docker run -p 8080:8080 <model>:local`
- [ ] Health check passes inside container
- [ ] Inference works inside container
- [ ] Test with multiple requests
- [ ] Container logs are visible

### Unit Tests
- [ ] Run tests: `pytest tests/ -v`
- [ ] All health endpoint tests pass
- [ ] All inference endpoint tests pass
- [ ] Code coverage is adequate (>70%)
- [ ] No test failures or errors

## ☑️ CircleCI Configuration Checklist

### Project Setup
- [ ] Navigate to CircleCI dashboard
- [ ] Find repository in project list
- [ ] Click "Set Up Project"
- [ ] CircleCI config detected

### Environment Variables
- [ ] `AWS_ACCESS_KEY_ID` added
- [ ] `AWS_SECRET_ACCESS_KEY` added
- [ ] `AWS_REGION` added (e.g., eu-central-1)
- [ ] `AWS_ECR_REGISTRY` added (format: account-id.dkr.ecr.region.amazonaws.com)
- [ ] `SAGEMAKER_EXECUTION_ROLE` added (ARN format)
- [ ] `LAMBDA_EXECUTION_ROLE` added (ARN format)
- [ ] `SONAR_TOKEN` added
- [ ] `SONAR_HOST_URL` added
- [ ] `FURY_TOKEN` added (if using Gemfury)

### CircleCI Settings
- [ ] Project follows main/develop branches
- [ ] "Only build pull requests" enabled (recommended)
- [ ] Context configured (aws-credentials)
- [ ] SSH keys added (if needed)

## ☑️ AWS Resources Checklist

### IAM Roles
- [ ] SageMaker execution role exists
- [ ] SageMaker role has necessary permissions
- [ ] Lambda execution role exists
- [ ] Lambda role has SageMaker invoke permissions
- [ ] Lambda role has CloudWatch logs permissions
- [ ] Roles have appropriate trust relationships

### ECR Repository
- [ ] ECR repository created for model
- [ ] Repository name matches model name
- [ ] Repository permissions configured
- [ ] Lifecycle policy configured (optional)

### VPC Configuration (if needed)
- [ ] VPC created
- [ ] Private subnets configured
- [ ] Security groups configured
- [ ] NAT Gateway configured (for internet access)

## ☑️ Deployment Checklist

### Pre-Deployment
- [ ] All tests pass locally
- [ ] Docker builds successfully
- [ ] Code committed to Git
- [ ] Commit message follows convention
- [ ] Branch pushed to remote

### Trigger Deployment
- [ ] Push to GitHub: `git push origin feature/deploy-<model>`
- [ ] CircleCI pipeline triggered
- [ ] Pipeline appears in CircleCI dashboard

### Monitor Pipeline
- [ ] Code quality scan starts
- [ ] SonarCloud scan completes
- [ ] Docker build starts
- [ ] Docker push to ECR succeeds
- [ ] Manual approval appears
- [ ] Approve deployment
- [ ] SageMaker deployment starts
- [ ] Monitor deployment progress

### SageMaker Deployment
- [ ] Endpoint status: "Creating"
- [ ] Wait for status: "InService" (5-10 minutes)
- [ ] No errors in CloudWatch logs
- [ ] Endpoint appears in SageMaker console

### Lambda Deployment
- [ ] Lambda function created
- [ ] Function configuration correct
- [ ] Environment variables set
- [ ] Execution role attached
- [ ] No errors in deployment logs

### API Gateway Setup (Dev)
- [ ] API Gateway created
- [ ] Cognito User Pool created/updated
- [ ] App Client created
- [ ] Authorizer configured
- [ ] API deployed to stage
- [ ] API key generated

## ☑️ Post-Deployment Checklist

### Verify Deployment
- [ ] API endpoint URL received
- [ ] API key received (Dev) or auth configured (Prod)
- [ ] SageMaker endpoint in "InService" status
- [ ] Lambda function active
- [ ] API Gateway endpoint accessible

### Test Deployed Endpoint
- [ ] Obtain JWT token from Cognito (Dev)
- [ ] Test health endpoint via API Gateway
- [ ] Test inference endpoint with sample data
- [ ] Verify response format is correct
- [ ] Test with multiple requests
- [ ] Test error handling (invalid input)
- [ ] Check response times are acceptable

### Monitor Resources
- [ ] CloudWatch logs available
- [ ] SageMaker logs show successful invocations
- [ ] Lambda logs show successful executions
- [ ] No error messages in logs
- [ ] Metrics appearing in CloudWatch

### Performance Testing
- [ ] Latency within acceptable range (<500ms recommended)
- [ ] Throughput meets requirements
- [ ] Error rate is low (<1%)
- [ ] Cache hit rate is good (if enabled)
- [ ] Resource utilization is normal (CPU, memory)

## ☑️ Documentation Checklist

### Code Documentation
- [ ] Docstrings added to functions
- [ ] Comments added for complex logic
- [ ] Input/output formats documented
- [ ] Error codes documented

### Project Documentation
- [ ] README.md updated with model-specific info
- [ ] API documentation generated (FastAPI /docs)
- [ ] Deployment notes documented
- [ ] Known issues documented (if any)

### Runbook
- [ ] Deployment steps documented
- [ ] Rollback procedure documented
- [ ] Troubleshooting guide created
- [ ] Contact information added

## ☑️ Production Readiness Checklist

### High Availability
- [ ] Multiple instances configured (2+)
- [ ] Auto-scaling enabled
- [ ] Health checks configured
- [ ] Graceful shutdown implemented

### Security
- [ ] No hardcoded credentials
- [ ] Secrets in environment variables or Secrets Manager
- [ ] VPC isolation configured (if needed)
- [ ] Encryption at rest enabled
- [ ] Encryption in transit enabled
- [ ] IAM roles follow least privilege

### Monitoring & Alerting
- [ ] CloudWatch alarms configured
- [ ] Error rate alerts set
- [ ] Latency alerts set
- [ ] Cost alerts configured
- [ ] Log aggregation configured

### Performance
- [ ] Load testing completed
- [ ] Latency optimized
- [ ] Caching enabled and tuned
- [ ] Request batching implemented (if applicable)
- [ ] Model inference optimized

### Cost Optimization
- [ ] Instance type right-sized
- [ ] Auto-scaling configured
- [ ] Caching enabled
- [ ] Development environments shut down when not in use
- [ ] Resource tagging for cost tracking

## ☑️ Handoff Checklist

### Team Knowledge Transfer
- [ ] Team briefed on deployment
- [ ] Documentation shared with team
- [ ] Access permissions granted to team members
- [ ] On-call rotation established

### Operations
- [ ] Monitoring dashboard created
- [ ] Alerting rules documented
- [ ] Incident response plan documented
- [ ] Escalation contacts defined

### Maintenance
- [ ] Update schedule defined
- [ ] Model retraining plan documented
- [ ] Dependency update process defined
- [ ] Backup and recovery plan documented

## 🎉 Success Criteria

✅ All checklist items completed
✅ Model deployed and accessible
✅ Tests passing in production
✅ Monitoring and alerts active
✅ Documentation complete
✅ Team trained and ready

---

## 📝 Notes

Use this space for deployment-specific notes:

- Deployment Date: _______________
- Deployed By: _______________
- Environment: _______________
- API Endpoint: _______________
- Issues Encountered: _______________
- Resolution: _______________

---

*Keep this checklist for future reference and update as needed.*
