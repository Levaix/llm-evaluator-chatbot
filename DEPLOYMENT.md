# Deployment Strategy

This document outlines the deployment strategy for the LLM Evaluator Chatbot, including local development setup, production deployment options, and operational considerations.

## Table of Contents
1. [Local Development](#local-development)
2. [Production Deployment Options](#production-deployment-options)
3. [Environment Configuration](#environment-configuration)
4. [Scaling Considerations](#scaling-considerations)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Security Considerations](#security-considerations)
7. [Cost Management](#cost-management)
8. [Disaster Recovery](#disaster-recovery)

---

## Local Development

### Prerequisites
- Python 3.8 or higher
- pip package manager
- OpenAI API key
- (Optional) Virtual environment

### Setup Steps

1. **Clone/Download the Project**
   ```bash
   cd "DAI Assignment Part 2"
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # Linux/macOS
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   ```bash
   # Copy example file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=sk-your-key-here
   ```

5. **Prepare Dataset**
   - Place `Q&A_db_practice.json` in the `data/` directory
   - Ensure valid JSON format with question-answer pairs

6. **Run the Application**
   ```bash
   # Using launcher script
   # Windows
   run_app.bat
   
   # Linux/macOS
   chmod +x run_app.sh
   ./run_app.sh
   
   # Or directly
   streamlit run app/streamlit_app.py
   ```

7. **Access the Application**
   - Open browser to `http://localhost:8501`
   - Application should load with dataset

### Development Workflow

1. **Code Changes**: Edit source files in `src/` or `app/`
2. **Auto-reload**: Streamlit automatically reloads on file changes
3. **Testing**: Run tests with `pytest tests/ -v`
4. **Notebooks**: Use Jupyter for exploration and prototyping

---

## Production Deployment Options

### Option 1: Streamlit Cloud (Recommended for Simple Deployment)

**Pros**:
- Free tier available
- Easy deployment from GitHub
- Automatic HTTPS
- Built-in CI/CD

**Cons**:
- Limited customization
- Resource constraints on free tier
- Vendor lock-in

**Deployment Steps**:
1. Push code to GitHub repository
2. Sign up at [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect GitHub repository
4. Configure environment variables in Streamlit Cloud dashboard
5. Deploy application

**Configuration**:
- Set `OPENAI_API_KEY` in environment variables
- Configure `MASTER_MODEL_NAME` if different from default
- Set resource limits if needed

**Cost**: Free tier available, paid plans for more resources

---

### Option 2: Heroku

**Pros**:
- Easy deployment
- Good documentation
- Add-on ecosystem
- Free tier (limited)

**Cons**:
- Free tier discontinued (as of Nov 2022)
- Dyno sleep on inactivity (free tier)
- Limited resources

**Deployment Steps**:
1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: streamlit run app/streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
   ```
3. Create `setup.sh`:
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [server]\n\
   port = $PORT\n\
   enableCORS = false\n\
   headless = true\n\
   " > ~/.streamlit/config.toml
   ```
4. Deploy:
   ```bash
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your-key
   git push heroku main
   ```

**Cost**: Paid plans start at ~$7/month

---

### Option 3: AWS (EC2, ECS, or Lambda)

**Pros**:
- Highly scalable
- Flexible configuration
- Enterprise-grade infrastructure
- Pay-as-you-go pricing

**Cons**:
- More complex setup
- Requires AWS knowledge
- More expensive for simple use cases

#### AWS EC2 Deployment

1. **Launch EC2 Instance**
   - Choose Ubuntu/Debian AMI
   - t2.micro or t3.small (free tier eligible)
   - Configure security group (port 8501)

2. **Setup on Instance**
   ```bash
   # SSH into instance
   ssh -i your-key.pem ubuntu@your-instance-ip
   
   # Install dependencies
   sudo apt update
   sudo apt install python3-pip
   git clone your-repo
   cd your-repo
   pip3 install -r requirements.txt
   
   # Configure environment
   export OPENAI_API_KEY=your-key
   
   # Run with nohup or use systemd service
   nohup streamlit run app/streamlit_app.py --server.port=8501 &
   ```

3. **Use Nginx as Reverse Proxy** (Recommended)
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

**Cost**: ~$10-50/month depending on instance size

#### AWS Lambda (Serverless)

**Pros**:
- Pay only for usage
- Auto-scaling
- No server management

**Cons**:
- Cold starts
- 15-minute timeout limit
- More complex setup

**Note**: Requires adaptation of Streamlit app for serverless architecture (e.g., using FastAPI instead)

---

### Option 4: Google Cloud Platform (GCP)

**Options**:
- **Cloud Run**: Serverless containers
- **Compute Engine**: VM instances
- **App Engine**: Managed platform

**Deployment Steps** (Cloud Run):
1. Create Dockerfile
2. Build and push container to GCP Container Registry
3. Deploy to Cloud Run
4. Configure environment variables

**Cost**: Pay-per-use, free tier available

---

### Option 5: Docker + Any Cloud Provider

**Pros**:
- Consistent environment
- Easy to deploy anywhere
- Portable

**Steps**:
1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. Build and run:
   ```bash
   docker build -t llm-evaluator .
   docker run -p 8501:8501 -e OPENAI_API_KEY=your-key llm-evaluator
   ```

3. Deploy to any container platform (AWS ECS, GCP Cloud Run, Azure Container Instances, etc.)

---

## Environment Configuration

### Required Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key

# Optional (with defaults)
MASTER_MODEL_NAME=gpt-4o-mini
MASTER_MAX_NEW_TOKENS=512
MASTER_TEMPERATURE=0.2
DATA_PATH=data/Q&A_db_practice.json
LOG_PATH=data/evaluations_log.jsonl
SENTIMENT_MODEL_NAME=distilbert-base-uncased-finetuned-sst-2-english
```

### Production Configuration Recommendations

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables or secret management services
   - Rotate keys periodically
   - Use separate keys for dev/staging/prod

2. **Resource Limits**
   - Set appropriate `MASTER_MAX_NEW_TOKENS` to control costs
   - Monitor API usage and set budget alerts
   - Consider rate limiting for users

3. **Data Storage**
   - For production, consider migrating from JSON files to database
   - Implement log rotation for evaluation logs
   - Backup data regularly

---

## Scaling Considerations

### Horizontal Scaling

**Current Architecture**: Stateless design supports horizontal scaling

**Strategy**:
1. Deploy multiple Streamlit instances
2. Use load balancer (Nginx, AWS ALB, etc.)
3. Share session state via external storage (Redis) if needed
4. Distribute load across instances

**Limitations**:
- Streamlit session state is per-instance
- May need session affinity or external state management

### Vertical Scaling

**Strategy**:
- Increase instance size (CPU, RAM)
- Optimize code for better performance
- Cache frequently accessed data

### Database Migration

**When to Migrate**:
- High evaluation volume (>1000/day)
- Need for complex queries
- Multiple concurrent users
- Data analysis requirements

**Options**:
- **SQLite**: Simple, file-based, good for small scale
- **PostgreSQL**: Production-ready, scalable
- **MongoDB**: If document structure fits better

---

## Monitoring and Maintenance

### Key Metrics to Monitor

1. **Application Metrics**
   - Response time (evaluation latency)
   - Error rates
   - API call success/failure rates
   - User activity (evaluations per day)

2. **Cost Metrics**
   - OpenAI API usage (tokens, requests)
   - Infrastructure costs
   - Cost per evaluation

3. **Quality Metrics**
   - Evaluation consistency
   - User feedback sentiment
   - Score distributions

### Monitoring Tools

1. **Application Logging**
   - Python logging module (already implemented)
   - Log aggregation (ELK stack, CloudWatch, etc.)

2. **APM Tools**
   - New Relic
   - Datadog
   - AWS CloudWatch
   - Google Cloud Monitoring

3. **Error Tracking**
   - Sentry
   - Rollbar
   - Custom error tracking

### Maintenance Tasks

1. **Regular Tasks**
   - Review and rotate API keys
   - Monitor costs and usage
   - Review error logs
   - Update dependencies
   - Backup data

2. **Periodic Tasks**
   - Analyze evaluation quality
   - Review user feedback
   - Optimize prompts if needed
   - Update documentation

3. **As Needed**
   - Scale infrastructure
   - Migrate to database
   - Add new features
   - Security updates

---

## Security Considerations

### API Key Management

1. **Storage**
   - Environment variables (recommended)
   - Secret management services (AWS Secrets Manager, HashiCorp Vault)
   - Never in code or version control

2. **Access Control**
   - Limit API key permissions
   - Use separate keys for different environments
   - Rotate keys regularly

3. **Network Security**
   - Use HTTPS in production
   - Implement rate limiting
   - Consider IP whitelisting for admin functions

### Data Security

1. **Data Privacy**
   - Scrub PII before evaluation
   - Encrypt sensitive data at rest
   - Secure data transmission (HTTPS)

2. **Access Control**
   - Implement user authentication if needed
   - Role-based access control
   - Audit logging

3. **Compliance**
   - GDPR considerations (if handling EU data)
   - Data retention policies
   - User consent for data usage

### Application Security

1. **Input Validation**
   - Validate all user inputs
   - Sanitize data before processing
   - Prevent injection attacks

2. **Dependencies**
   - Keep dependencies updated
   - Scan for vulnerabilities
   - Use trusted sources

---

## Cost Management

### Cost Breakdown

1. **OpenAI API Costs** (Primary Cost)
   - gpt-4o-mini: ~$0.15 per 1M input tokens, $0.60 per 1M output tokens
   - Typical evaluation: ~500-1000 tokens
   - Cost per evaluation: ~$0.0003-0.0006

2. **Infrastructure Costs**
   - Hosting: $0-50/month depending on platform
   - Storage: Minimal (JSON files)
   - Bandwidth: Usually included

### Cost Optimization Strategies

1. **Token Management**
   - Set appropriate `MASTER_MAX_NEW_TOKENS` (default: 512)
   - Optimize prompts to reduce token usage
   - Cache common evaluations if possible

2. **Model Selection**
   - Use gpt-4o-mini (cost-efficient)
   - Consider cheaper models for simple tasks
   - Batch processing for non-interactive use

3. **Infrastructure**
   - Use free tiers where possible
   - Right-size instances
   - Implement auto-scaling

4. **Monitoring**
   - Set budget alerts
   - Track usage patterns
   - Identify cost anomalies

### Budget Estimation

**Example**: 1000 evaluations/month
- API costs: ~$0.30-0.60
- Hosting: $0-10 (free tier or small instance)
- **Total**: ~$1-11/month

**Example**: 10,000 evaluations/month
- API costs: ~$3-6
- Hosting: $10-50
- **Total**: ~$13-56/month

---

## Disaster Recovery

### Backup Strategy

1. **Code**
   - Version control (Git)
   - Regular commits
   - Tagged releases

2. **Data**
   - Regular backups of Q&A database
   - Backup evaluation logs
   - Store backups in separate location

3. **Configuration**
   - Document all configuration
   - Version control configuration templates
   - Secure backup of API keys

### Recovery Procedures

1. **Application Failure**
   - Restart application
   - Check logs for errors
   - Verify API key validity
   - Check dependencies

2. **Data Loss**
   - Restore from backups
   - Replay logs if possible
   - Verify data integrity

3. **API Failure**
   - Implement retry logic
   - Fallback to cached results if available
   - Notify users of service issues

### High Availability

1. **Redundancy**
   - Multiple instances
   - Load balancing
   - Failover mechanisms

2. **Health Checks**
   - Application health endpoints
   - Automated monitoring
   - Alerting on failures

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] API keys secured
- [ ] Dataset prepared and validated
- [ ] Documentation updated
- [ ] Security review completed

### Deployment

- [ ] Deploy to staging environment first
- [ ] Test all functionality
- [ ] Verify API connectivity
- [ ] Check error handling
- [ ] Monitor initial usage

### Post-Deployment

- [ ] Monitor application logs
- [ ] Track API usage and costs
- [ ] Collect user feedback
- [ ] Monitor performance metrics
- [ ] Schedule regular backups

---

## Support and Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify key is set correctly
   - Check key hasn't expired
   - Ensure key has proper permissions

2. **Dataset Loading Issues**
   - Verify file path is correct
   - Check JSON format is valid
   - Ensure file has required fields

3. **Performance Issues**
   - Check network latency
   - Monitor API response times
   - Review resource usage

### Getting Help

- Check application logs
- Review error messages
- Consult documentation
- Check OpenAI API status
- Review GitHub issues (if applicable)


