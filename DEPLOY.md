# Platform Deployment Guide

## Architecture

```
[Dashboard VPS] ── port 8443 ──> Workers (remote VPS nodes)
     │
     ├── FastAPI app (dashboard/app.py)
     ├── SQLite DB (dashboard/data/dashboard.db)
     ├── APK auto-seeder
     ├── Local APK workers (optional)
     ├── Adminer tools (/opt/adminer/)
     └── AWS/GCP tools
```

---

## PART 1: Dashboard VPS (Main Server)

### 1.1 System Setup

```bash
apt update && apt install -y python3 python3-pip git wget unzip openjdk-17-jre-headless
```

### 1.2 Install TruffleHog (binary)

```bash
# Download latest trufflehog binary
wget https://github.com/trufflesecurity/trufflehog/releases/download/v3.88.24/trufflehog_3.88.24_linux_amd64.tar.gz
tar xzf trufflehog_3.88.24_linux_amd64.tar.gz
mv trufflehog /usr/local/bin/
chmod +x /usr/local/bin/trufflehog
rm -f trufflehog_3.88.24_linux_amd64.tar.gz
```

### 1.3 Install JADX (APK decompiler)

```bash
wget https://github.com/skylot/jadx/releases/download/v1.5.1/jadx-1.5.1.zip
mkdir -p /opt/jadx && unzip jadx-1.5.1.zip -d /opt/jadx
ln -sf /opt/jadx/bin/jadx /usr/local/bin/jadx
rm jadx-1.5.1.zip
```

### 1.4 Deploy Dashboard App

```bash
# Copy the dashboard-app directory to new VPS
# From your laptop:
scp -r root@OLD_VPS:/opt/dashboard-app /tmp/dashboard-app-backup
scp -r /tmp/dashboard-app-backup root@NEW_VPS:/opt/dashboard-app

# Or if you have it archived:
scp dashboard-app.tar.gz root@NEW_VPS:/opt/
ssh root@NEW_VPS "cd /opt && tar xzf dashboard-app.tar.gz && rm dashboard-app.tar.gz"
```

### 1.5 Install Python Dependencies

```bash
pip3 install fastapi uvicorn[standard] aiosqlite jinja2 python-multipart
pip3 install requests beautifulsoup4 boto3 truffleHog
pip3 install google-cloud-secret-manager google-cloud-storage google-cloud-compute
pip3 install google-cloud-functions google-cloud-run google-cloud-container
pip3 install google-cloud-bigquery google-cloud-firestore google-cloud-logging
pip3 install google-cloud-resource-manager google-api-python-client google-auth
pip3 install google-play-scraper
```

### 1.6 Create Data Directory

```bash
mkdir -p /opt/dashboard-app/dashboard/data
# Copy the DB from old VPS (or start fresh):
scp root@OLD_VPS:/opt/dashboard-app/dashboard/data/dashboard.db /opt/dashboard-app/dashboard/data/
```

### 1.7 Dashboard Systemd Service

```bash
cat > /etc/systemd/system/dashboard.service << 'EOF'
[Unit]
Description=Security Research Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/dashboard-app
Environment=DASHBOARD_DB=/opt/dashboard-app/dashboard/data/dashboard.db
Environment=DASHBOARD_KEY=YOUR_API_KEY_HERE
Environment=DASHBOARD_PASS=YOUR_LOGIN_PASSWORD_HERE
Environment=DASHBOARD_BIND=0.0.0.0
Environment=DASHBOARD_PORT=8443
Environment=TELEGRAM_BOT_TOKEN=YOUR_TG_BOT_TOKEN
Environment=TELEGRAM_CHAT_ID=YOUR_TG_CHAT_ID
Environment=DASHBOARD_URL=http://YOUR_NEW_IP:8443
ExecStart=/usr/bin/python3 -m uvicorn dashboard.app:app --host 0.0.0.0 --port 8443 --workers 1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable dashboard
systemctl start dashboard
```

### 1.8 APK Auto-Seeder Service

Keeps the queue fed with new packages to scan.

```bash
cat > /etc/systemd/system/apk-autoseed.service << 'EOF'
[Unit]
Description=APK Auto-Seeder
After=network.target dashboard.service

[Service]
Type=simple
WorkingDirectory=/opt/dashboard-app
ExecStart=/usr/bin/python3 -u /opt/dashboard-app/apk-autoseed.py
Restart=always
RestartSec=30
Environment=DASHBOARD_URL=http://127.0.0.1:8443
Environment=DASHBOARD_KEY=YOUR_API_KEY_HERE
Environment=SEED_THRESHOLD=50
Environment=CHECK_INTERVAL=120
Environment=BATCH_SIZE=300

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable apk-autoseed
systemctl start apk-autoseed
```

### 1.9 Deploy Adminer Tools (optional)

```bash
scp -r root@OLD_VPS:/opt/adminer root@NEW_VPS:/opt/adminer
```

### 1.10 Crontab — Clean APK temp files

```bash
crontab -e
# Add:
0 * * * * find /opt/apk-worker/apks/ -mindepth 1 -maxdepth 1 -type d -mmin +60 -exec rm -rf {} + 2>/dev/null
```

### 1.11 Verify

```bash
curl http://localhost:8443/
# Should return the login page
systemctl status dashboard
systemctl status apk-autoseed
```

---

## PART 2: Local Workers (on Dashboard VPS)

Run workers on the same VPS that hosts the dashboard. Use `127.0.0.1` as DASHBOARD_URL.

### 2.1 Create Worker Service (repeat for each worker)

```bash
# Worker 1
cat > /etc/systemd/system/apk-worker.service << 'EOF'
[Unit]
Description=APK Worker Agent
After=network.target dashboard.service

[Service]
Type=simple
WorkingDirectory=/opt
ExecStart=/usr/bin/python3 -u /opt/dashboard-app/apk-worker.py
Restart=on-failure
RestartSec=30
Environment=DASHBOARD_URL=http://127.0.0.1:8443
Environment=DASHBOARD_KEY=YOUR_API_KEY_HERE
Environment=WORKER_ID=main-worker-1
Environment=BATCH_SIZE=10
Environment=PARALLEL_WORKERS=4
Environment=POLL_INTERVAL=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable apk-worker
systemctl start apk-worker
```

For additional local workers, copy the service file with different names:

```bash
for i in 2 3 4; do
  sed "s/APK Worker Agent/APK Worker Agent $i/;s/apk-worker.service/apk-worker${i}.service/;s/WORKER_ID=main-worker-1/WORKER_ID=main-worker-${i}/" \
    /etc/systemd/system/apk-worker.service > /etc/systemd/system/apk-worker${i}.service
done
systemctl daemon-reload
for i in 2 3 4; do systemctl enable apk-worker${i} && systemctl start apk-worker${i}; done
```

---

## PART 3: Remote Workers (separate VPS nodes)

### 3.1 System Setup (on each worker VPS)

```bash
apt update && apt install -y python3 python3-pip wget unzip
```

### 3.2 Install TruffleHog

```bash
wget https://github.com/trufflesecurity/trufflehog/releases/download/v3.88.24/trufflehog_3.88.24_linux_amd64.tar.gz
tar xzf trufflehog_3.88.24_linux_amd64.tar.gz
mv trufflehog /usr/local/bin/
chmod +x /usr/local/bin/trufflehog
rm trufflehog_3.88.24_linux_amd64.tar.gz
```

### 3.3 Copy Worker Script

```bash
# From laptop or dashboard VPS:
scp root@DASHBOARD_VPS:/opt/dashboard-app/apk-worker.py root@WORKER_VPS:/opt/apk-worker.py
scp root@DASHBOARD_VPS:/opt/dashboard-app/validators.py root@WORKER_VPS:/opt/validators.py
```

### 3.4 Install Python Dependencies (worker only needs minimal)

```bash
pip3 install requests
```

### 3.5 Create Worker Service

```bash
cat > /etc/systemd/system/apk-worker.service << 'EOF'
[Unit]
Description=APK Worker Agent
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt
ExecStart=/usr/bin/python3 -u /opt/apk-worker.py
Restart=on-failure
RestartSec=30
Environment=DASHBOARD_URL=http://DASHBOARD_IP:8443
Environment=DASHBOARD_KEY=YOUR_API_KEY_HERE
Environment=WORKER_ID=HOSTNAME-worker-1
Environment=BATCH_SIZE=10
Environment=PARALLEL_WORKERS=4
Environment=POLL_INTERVAL=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable apk-worker
systemctl start apk-worker
```

### 3.6 Multiple Workers Per Node

```bash
# Scale based on CPU cores (1 worker per 2 cores recommended)
for i in 2 3 4; do
  cat > /etc/systemd/system/apk-worker${i}.service << WEOF
[Unit]
Description=APK Worker Agent $i
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt
ExecStart=/usr/bin/python3 -u /opt/apk-worker.py
Restart=on-failure
RestartSec=30
Environment=DASHBOARD_URL=http://DASHBOARD_IP:8443
Environment=DASHBOARD_KEY=YOUR_API_KEY_HERE
Environment=WORKER_ID=HOSTNAME-worker-${i}
Environment=BATCH_SIZE=10
Environment=PARALLEL_WORKERS=4
Environment=POLL_INTERVAL=5

[Install]
WantedBy=multi-user.target
WEOF
done
systemctl daemon-reload
for i in 2 3 4; do systemctl enable apk-worker${i} && systemctl start apk-worker${i}; done
```

### 3.7 Crontab for temp cleanup

```bash
crontab -e
# Add:
0 * * * * find /opt/apk-worker/apks/ -mindepth 1 -maxdepth 1 -type d -mmin +60 -exec rm -rf {} + 2>/dev/null
```

---

## PART 4: Quick Deploy Script (One-liner for remote workers)

Save this as `deploy-worker.sh` and run: `bash deploy-worker.sh WORKER_VPS_IP DASHBOARD_IP API_KEY`

```bash
#!/bin/bash
# Usage: bash deploy-worker.sh <worker_ip> <dashboard_ip> <api_key> [num_workers]
WORKER_IP=$1
DASH_IP=$2
API_KEY=$3
NUM=${4:-4}
HOST=$(ssh root@$WORKER_IP hostname)

ssh root@$WORKER_IP "
apt update && apt install -y python3 python3-pip wget
pip3 install requests
wget -q https://github.com/trufflesecurity/trufflehog/releases/download/v3.88.24/trufflehog_3.88.24_linux_amd64.tar.gz
tar xzf trufflehog_3.88.24_linux_amd64.tar.gz && mv trufflehog /usr/local/bin/ && chmod +x /usr/local/bin/trufflehog
rm trufflehog_3.88.24_linux_amd64.tar.gz
mkdir -p /opt/apk-worker/apks
echo '0 * * * * find /opt/apk-worker/apks/ -mindepth 1 -maxdepth 1 -type d -mmin +60 -exec rm -rf {} +' | crontab -
"

scp root@$DASH_IP:/opt/dashboard-app/apk-worker.py root@$WORKER_IP:/opt/apk-worker.py
scp root@$DASH_IP:/opt/dashboard-app/validators.py root@$WORKER_IP:/opt/validators.py

for i in $(seq 1 $NUM); do
  SVC="apk-worker"
  [ $i -gt 1 ] && SVC="apk-worker${i}"
  ssh root@$WORKER_IP "
cat > /etc/systemd/system/${SVC}.service << XEOF
[Unit]
Description=APK Worker Agent $i
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt
ExecStart=/usr/bin/python3 -u /opt/apk-worker.py
Restart=on-failure
RestartSec=30
Environment=DASHBOARD_URL=http://${DASH_IP}:8443
Environment=DASHBOARD_KEY=${API_KEY}
Environment=WORKER_ID=${HOST}-worker-${i}
Environment=BATCH_SIZE=10
Environment=PARALLEL_WORKERS=4
Environment=POLL_INTERVAL=5

[Install]
WantedBy=multi-user.target
XEOF
systemctl daemon-reload && systemctl enable ${SVC} && systemctl start ${SVC}
"
done

echo "Deployed $NUM workers on $WORKER_IP -> dashboard $DASH_IP"
```

---

## PART 5: Backup & Migrate

### Backup everything from current VPS

```bash
# On current VPS (or from laptop via SSH):
cd /opt

# Dashboard app + DB (this is the big one)
tar czf /tmp/dashboard-app.tar.gz \
  --exclude='dashboard-app/dashboard/data/dashboard.db' \
  dashboard-app/

# DB separately (it's 2.3GB)
cp dashboard-app/dashboard/data/dashboard.db /tmp/dashboard.db

# Adminer tools
tar czf /tmp/adminer-tools.tar.gz adminer/
```

### Transfer to new VPS

```bash
# From laptop:
scp root@OLD_VPS:/tmp/dashboard-app.tar.gz .
scp root@OLD_VPS:/tmp/dashboard.db .
scp root@OLD_VPS:/tmp/adminer-tools.tar.gz .

scp dashboard-app.tar.gz root@NEW_VPS:/opt/
scp dashboard.db root@NEW_VPS:/opt/
scp adminer-tools.tar.gz root@NEW_VPS:/opt/

ssh root@NEW_VPS "
cd /opt
tar xzf dashboard-app.tar.gz && rm dashboard-app.tar.gz
mkdir -p dashboard-app/dashboard/data
mv dashboard.db dashboard-app/dashboard/data/
tar xzf adminer-tools.tar.gz && rm adminer-tools.tar.gz
"
```

### Update all remote workers

After moving the dashboard to a new IP, update all workers:

```bash
# For each worker VPS:
ssh root@WORKER_VPS "
sed -i 's|DASHBOARD_URL=http://OLD_IP:8443|DASHBOARD_URL=http://NEW_IP:8443|' /etc/systemd/system/apk-worker*.service
systemctl daemon-reload
systemctl restart apk-worker*
"
```

---

## Environment Variables Reference

### Dashboard
| Variable | Example | Description |
|----------|---------|-------------|
| `DASHBOARD_DB` | `/opt/dashboard-app/dashboard/data/dashboard.db` | SQLite DB path |
| `DASHBOARD_KEY` | `5af4da2bdde5...` | API auth key (64 char hex) |
| `DASHBOARD_PASS` | `atiRaIa7sd...` | Web login password |
| `DASHBOARD_PORT` | `8443` | Listen port |
| `TELEGRAM_BOT_TOKEN` | `8779647338:AAFz...` | Telegram alerts |
| `TELEGRAM_CHAT_ID` | `-1003975740865` | Telegram channel |
| `DASHBOARD_URL` | `http://IP:8443` | Self URL for links |

### Workers
| Variable | Example | Description |
|----------|---------|-------------|
| `DASHBOARD_URL` | `http://DASH_IP:8443` | Dashboard API endpoint |
| `DASHBOARD_KEY` | Same as dashboard | Auth key |
| `WORKER_ID` | `hostname-worker-1` | Unique worker name |
| `BATCH_SIZE` | `10` | Packages per batch |
| `PARALLEL_WORKERS` | `4` | Concurrent scans |
| `POLL_INTERVAL` | `5` | Seconds between polls |

### Auto-Seeder
| Variable | Example | Description |
|----------|---------|-------------|
| `SEED_THRESHOLD` | `50` | Seed when queue drops below this |
| `CHECK_INTERVAL` | `120` | Seconds between checks |
| `BATCH_SIZE` | `300` | Packages to seed per round |
