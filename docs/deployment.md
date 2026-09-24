# Production Deployment Guide

This document outlines the deployment architecture, server provisioning, container management, reverse proxy configuration, and monitoring procedures for Uzum Review Intelligence (URI).

---

## 1. Deployment Topology

In production, services run inside isolated Docker containers behind a host-level reverse proxy (such as Nginx):

```
Internet (HTTPS)
       │
       ▼
 [ Nginx / Caddy ]  (Ports 80, 443 with SSL/TLS)
   ├───► /api/*         ───► Gateway Service (Port 8000)
   │                           ├───► sentiment-svc (Port 8001, Internal Network)
   │                           ├───► aspect-svc    (Port 8002, Internal Network)
   │                           └───► postgres       (Port 5432, Internal Network)
   └───► /*             ───► Dashboard Frontend (Static SPA / Port 5173)
```

Microservices (`sentiment-svc`, `aspect-svc`, and `postgres`) should remain internal to the Docker network and not be exposed directly to the public internet.

---

## 2. Server Provisioning

### 2.1 System Requirements
- Operating System: Ubuntu 22.04 LTS or 24.04 LTS.
- Hardware: Minimum 2 CPU cores, 4 GB RAM, 20 GB SSD storage.
- Software: Docker Engine version 24+ and Docker Compose v2+.

### 2.2 Host Firewall (UFW)
Only open necessary incoming ports:
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 3. Production Deployment Steps

### Step 1: Clone Repository
```bash
git clone https://github.com/BekmurodGofurov/uri.git /opt/uri
cd /opt/uri
```

### Step 2: Configure Environment
Create a hardened `.env` file:
```bash
cp .env.example .env
nano .env
```
Key production settings:
- `POSTGRES_PASSWORD`: Use a strong, random password.
- `API_KEY`: Set a secure secret key to protect administrative and write endpoints.
- `CORS_ORIGINS`: Set strictly to your production domain (e.g. `https://uri.yourdomain.com`).

### Step 3: Build and Launch Containers
```bash
docker compose -f docker-compose.yml up -d --build
```

### Step 4: Verify Container Health
Check that all services show healthy status:
```bash
docker compose ps
```
The Gateway container will not enter ready state until PostgreSQL passes its internal healthcheck (`pg_isready`).

---

## 4. Reverse Proxy and SSL Configuration

### 4.1 Sample Nginx Configuration
Place the following configuration in `/etc/nginx/sites-available/uri.conf`:

```nginx
server {
    listen 80;
    server_name uri.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name uri.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/uri.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/uri.yourdomain.com/privkey.pem;

    # Frontend Single Page App
    location / {
        root /opt/uri/dashboard/dist;
        try_files $uri $uri/ /index.html;
    }

    # Gateway API Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4.2 SSL Certificate via Certbot
```bash
sudo certbot --nginx -d uri.yourdomain.com
```

---

## 5. Operations and Maintenance

### 5.1 Viewing Container Logs
To inspect logs across all or specific services:
```bash
# View Gateway logs
docker compose logs -f gateway

# View Sentiment Service logs
docker compose logs -f sentiment-svc
```

### 5.2 Log Rotation Configuration
Prevent Docker log files from filling disk storage by configuring `/etc/docker/daemon.json`:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "3"
  }
}
```

### 5.3 Automated Database Backups
Schedule daily PostgreSQL backups via cron:
```bash
0 2 * * * docker exec uri-postgres pg_dump -U postgres uzum_reviews | gzip > /opt/backups/uzum_reviews_$(date +\%F).sql.gz
```

### 5.4 Instant Model Rollback
If a newly deployed model exhibits degraded performance in production, execute the registry rollback command without restarting the service:
```bash
docker compose exec gateway python -m gateway.registry.cli rollback --service sentiment --to sentiment-v1
```
