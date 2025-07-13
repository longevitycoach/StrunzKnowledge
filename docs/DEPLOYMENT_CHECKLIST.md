# Deployment Checklist - Dr. Strunz Knowledge Base MCP Server

## Pre-Deployment Checklist

### 1. Code Quality ✓
- [ ] All tests pass locally
- [ ] No linting errors (`flake8`, `mypy`)
- [ ] Code review completed
- [ ] Security scan passed
- [ ] Dependencies updated and audited

### 2. Docker Testing ✓
- [ ] Build Docker image locally
  ```bash
  docker build -t strunz-mcp:test .
  ```
- [ ] Run comprehensive tests against Docker container
  ```bash
  docker run -d -p 8000:8000 --name test-mcp strunz-mcp:test
  python test_comprehensive_docker.py
  ```
- [ ] Verify resource usage < 512MB
  ```bash
  docker stats test-mcp
  ```
- [ ] Test with memory limits
  ```bash
  docker run -d -p 8000:8000 --memory="512m" --memory-swap="512m" strunz-mcp:test
  ```

### 3. Staging Environment ✓
- [ ] Deploy to staging
  ```bash
  docker-compose -f docker-compose.staging.yml up -d
  ```
- [ ] Run integration tests against staging
- [ ] Monitor resources for 24 hours
- [ ] Check Grafana dashboards at http://localhost:3000
- [ ] Verify all MCP tools work correctly
- [ ] Test SSE endpoint stability
- [ ] Load test with concurrent users

### 4. Configuration ✓
- [ ] Environment variables documented
- [ ] Secrets stored securely (not in code)
- [ ] Railway environment configured
- [ ] Domain configured correctly
- [ ] SSL certificates valid
- [ ] CORS settings appropriate

### 5. Data Integrity ✓
- [ ] FAISS indices backed up
- [ ] Database migrations tested
- [ ] Rollback plan documented
- [ ] Data recovery tested

### 6. Monitoring Setup ✓
- [ ] Prometheus metrics exposed
- [ ] Grafana dashboards configured
- [ ] Alert rules defined:
  - Memory > 400MB
  - CPU > 80%
  - Response time > 2s
  - Error rate > 5%
- [ ] Log aggregation working
- [ ] Health checks configured

## Deployment Steps

### 1. Pre-Deployment
```bash
# 1. Tag the release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 2. Build production image
docker build -t strunz-mcp:v1.0.0 .

# 3. Run final tests
./scripts/run_deployment_tests.sh

# 4. Check resource usage
docker run --rm -it strunz-mcp:v1.0.0 python -m src.monitoring.check_resources
```

### 2. Railway Deployment
- [ ] Push to main branch
- [ ] Monitor Railway build logs
- [ ] Wait for health check to pass
- [ ] Verify deployment at https://strunz.up.railway.app/
- [ ] Check memory usage in Railway dashboard
- [ ] Test all endpoints

### 3. Post-Deployment Verification
- [ ] Health check passes
  ```bash
  curl https://strunz.up.railway.app/
  ```
- [ ] MCP tools available
  ```bash
  curl https://strunz.up.railway.app/mcp/tools
  ```
- [ ] SSE endpoint working
  ```bash
  curl https://strunz.up.railway.app/sse
  ```
- [ ] Search functionality verified
- [ ] Resource monitoring active
- [ ] Error rate < 1%
- [ ] Response time < 500ms (p95)

### 4. Rollback Plan
If deployment fails:
1. Railway automatic rollback to previous version
2. Manual rollback:
   ```bash
   railway rollback
   ```
3. Restore from backup if data corruption
4. Notify team via Slack/Discord

## Performance Targets

| Metric | Target | Critical |
|--------|--------|----------|
| Memory Usage | < 400MB | < 512MB |
| CPU Usage | < 60% | < 80% |
| Response Time (p50) | < 200ms | < 500ms |
| Response Time (p95) | < 500ms | < 2s |
| Error Rate | < 0.1% | < 1% |
| Uptime | > 99.9% | > 99% |

## Monitoring Endpoints

- Health Check: `GET /`
- Metrics: `GET /metrics`
- MCP Tools: `GET /mcp/tools`
- SSE Stream: `GET /sse`

## Emergency Contacts

- **On-Call Engineer**: [Phone/Email]
- **Railway Support**: support@railway.app
- **Escalation**: Team Lead

## Known Issues & Workarounds

1. **High Memory Usage**
   - Fallback to simple server
   - Use lightweight embeddings
   - Reduce FAISS index size

2. **Slow Startup**
   - Increase health check timeout
   - Use lazy loading for indices

3. **API Compatibility**
   - FastMCP resource() → tool()
   - Check version compatibility

## Sign-off

- [ ] Development Team Lead
- [ ] Operations Engineer
- [ ] Product Owner
- [ ] Security Review

**Deployment Date**: _______________
**Deployed By**: _______________
**Version**: _______________