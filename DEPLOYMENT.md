# Deployment Guide

## 📦 Deployment Options

### 1. Local Development
See [QUICKSTART.md](QUICKSTART.md)

### 2. Docker / Docker Compose (Recommended for Production)

#### Prerequisites
- Docker Engine 20.10+
- Docker Compose 1.29+

#### Build and Run
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Configuration
Edit `docker-compose.yml` to:
- Change ports
- Add volumes for persistent data
- Set resource limits
- Configure networking

### 3. Kubernetes Deployment (Enterprise)

Create deployment manifests:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aqi-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aqi-backend
  template:
    metadata:
      labels:
        app: aqi-backend
    spec:
      containers:
      - name: backend
        image: aqi-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: WEATHER_API_KEY
          valueFrom:
            secretKeyRef:
              name: aqi-secrets
              key: weather-api-key
```

### 4. Cloud Platforms

#### AWS Deployment
1. Build Docker image
2. Push to ECR (Elastic Container Registry)
3. Create ECS/Fargate task definition
4. Set up ALB (Application Load Balancer)
5. Configure Route 53 for DNS
6. Add RDS for database (future)

#### Google Cloud
1. Push to Artifact Registry
2. Deploy to Cloud Run (serverless)
3. Use Cloud Load Balancer
4. Configure Firestore for data (future)

#### Azure
1. Push to Container Registry
2. Deploy to Container Instances
3. Use App Service for hosting
4. Configure Application Gateway

### 5. Traditional Server (VPS)

#### Prerequisites
- Ubuntu 20.04+ or similar
- Python 3.10+
- Node.js 16+
- Nginx/Apache
- Systemd or Supervisor

#### Setup Steps

1. **Clone Repository**
```bash
git clone <repo-url> /var/www/aqi-system
cd /var/www/aqi-system
```

2. **Backend Setup**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with production values
```

3. **Frontend Setup**
```bash
cd frontend
npm install
npm run build
```

4. **Create Systemd Service**

`/etc/systemd/system/aqi-backend.service`:
```ini
[Unit]
Description=AQI Prediction API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/aqi-system/backend
Environment="PATH=/var/www/aqi-system/backend/venv/bin"
ExecStart=/var/www/aqi-system/backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable aqi-backend
sudo systemctl start aqi-backend
sudo systemctl status aqi-backend
```

5. **Nginx Configuration**

`/etc/nginx/sites-available/aqi`:
```nginx
upstream aqi_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.aqi-example.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.aqi-example.com;

    ssl_certificate /etc/ssl/certs/your-cert.crt;
    ssl_certificate_key /etc/ssl/private/your-key.key;

    # Backend API
    location / {
        proxy_pass http://aqi_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name aqi-example.com;

    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name aqi-example.com;

    ssl_certificate /etc/ssl/certs/your-cert.crt;
    ssl_certificate_key /etc/ssl/private/your-key.key;

    root /var/www/aqi-system/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/aqi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 📊 Monitoring & Logging

### Application Monitoring
```bash
# View backend logs
journalctl -u aqi-backend -f

# View Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Health Checks
```bash
# API health
curl https://api.aqi-example.com/health

# Check frontend
curl https://aqi-example.com/

# Monitor response time
curl -w "@curl-format.txt" -o /dev/null -s https://api.aqi-example.com/health
```

### Automated Monitoring (Future)
- Set up Prometheus for metrics
- Configure Grafana dashboards
- Add alerts for downtime
- Use New Relic or DataDog for APM

## 🔒 Security in Production

### SSL/TLS
```bash
# Use Let's Encrypt for free certificates
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d api.aqi-example.com
```

### Firewall
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Environment Variables
```bash
# NEVER commit .env to git
echo ".env" >> .gitignore

# Use secure secrets management
# - GitHub Secrets for CI/CD
# - AWS Secrets Manager
# - HashiCorp Vault
```

### API Rate Limiting (Future)
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/predict")
@limiter.limit("10/minute")
async def predict_aqi(request: PredictionInput):
    ...
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Run multiple backend instances behind load balancer
- Use sticky sessions if needed
- Ensure database can handle concurrent connections

### Vertical Scaling
- Increase CPU/memory for single instance
- Optimize ML model inference
- Use GPU for LSTM if available

### Database (Future)
- Consider Redis for caching
- Use PostgreSQL for historical data
- Implement data retention policies

## 🚀 CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy AQI System

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker images
        run: docker-compose build
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker-compose push
      
      - name: Deploy to production
        run: |
          # SSH into server and pull latest images
          ssh -i ${{ secrets.SSH_KEY }} user@server 'cd /var/www/aqi-system && git pull && docker-compose up -d'
```

## 📋 Pre-Deployment Checklist

- [ ] All tests pass locally
- [ ] .env configured with production values
- [ ] SSL certificates installed
- [ ] Database backups configured
- [ ] Monitoring alerts set up
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Dependencies audited for security
- [ ] CORS properly configured
- [ ] API rate limiting ready

## 🆘 Rollback Procedures

```bash
# Docker Compose rollback
docker-compose down
git checkout main~1
docker-compose up -d

# Database rollback (if applicable)
# Restore from backup
```

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs`
2. Verify configuration: `docker-compose config`
3. Test connectivity: `curl http://localhost:8000/health`
4. Review troubleshooting in README.md

---

Need help? Create an issue or contact the development team.
