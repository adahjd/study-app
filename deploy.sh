#!/bin/bash
# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# 闃块噷浜戣交閲忎簯 / Ubuntu 22.04 涓€閿儴缃茶剼鏈?# 浣跨敤鏂规硶: chmod +x deploy.sh && sudo ./deploy.sh
# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

set -e

APP_DIR="/opt/study-app"
DOMAIN=""   # 鐣欑┖浣跨敤 IP锛屽～鍐欏煙鍚嶅垯鑷姩閰嶇疆 SSL

echo "========================================"
echo "  涓汉瀛︿範搴?- 閮ㄧ讲鑴氭湰"
echo "========================================"

# 1. 鏇存柊绯荤粺
echo "[1/7] 鏇存柊绯荤粺..."
apt update && apt upgrade -y

# 2. 瀹夎渚濊禆
echo "[2/7] 瀹夎绯荤粺渚濊禆..."
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

# 3. 鍒涘缓搴旂敤鐩綍
echo "[3/7] 鍒涘缓搴旂敤鐩綍..."
mkdir -p $APP_DIR
cp -r ./* $APP_DIR/

# 4. 鍒涘缓 Python 铏氭嫙鐜骞跺畨瑁呬緷璧?echo "[4/7] 瀹夎 Python 渚濊禆..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. 鍒涘缓 systemd 鏈嶅姟
echo "[5/7] 鍒涘缓 systemd 鏈嶅姟..."
cat > /etc/systemd/system/study-app.service << EOF
[Unit]
Description=Study App - Streamlit
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
Environment="PYTHONUNBUFFERED=1"
ExecStart=$APP_DIR/venv/bin/streamlit run app.py --server.port 8501 --server.headless true --server.enableCORS false --server.enableXsrfProtection false
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable study-app
systemctl start study-app

# 6. 閰嶇疆 Nginx 鍙嶅悜浠ｇ悊
echo "[6/7] 閰嶇疆 Nginx..."

if [ -z "$DOMAIN" ]; then
    # 浣跨敤 IP
    cat > /etc/nginx/sites-available/study-app << 'NGINX_EOF'
server {
    listen 80;
    server_name _;
    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_buffering off;
    }
}
NGINX_EOF
else
    cat > /etc/nginx/sites-available/study-app << NGINX_EOF
server {
    listen 80;
    server_name $DOMAIN;
    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_buffering off;
    }
}
NGINX_EOF
fi

ln -sf /etc/nginx/sites-available/study-app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 7. SSL (if domain provided)
if [ -n "$DOMAIN" ]; then
    echo "[7/7] 閰嶇疆 SSL 璇佷功..."
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
else
    echo "[7/7] 璺宠繃 SSL锛堟湭閰嶇疆鍩熷悕锛?
fi

echo ""
echo "========================================"
echo "  閮ㄧ讲瀹屾垚锛?
echo "========================================"
echo ""
echo "  搴旂敤宸插惎鍔? http://$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')"
echo "  鏌ョ湅鐘舵€? sudo systemctl status study-app"
echo "  鏌ョ湅鏃ュ織: sudo journalctl -u study-app -f"
echo "  閲嶅惎鏈嶅姟: sudo systemctl restart study-app"
