#!/usr/bin/env bash
set -euo pipefail

# Deploy Telegram Bot MAN 1 Jember on Ubuntu server
# Pengguna: sudo ./deploy.sh

APP_DIR="/home/angger/majesatelegrambot"
SERVICE_NAME="majesa-bot"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

if [[ $EUID -ne 0 ]]; then
    echo "Jalankan sebagai root: sudo ./deploy.sh" >&2
    exit 1
fi

echo "==> 1/5 Install dependensi sistem"
apt update
apt install -y python3 python3-venv python3-pip git

echo "==> 2/5 Clone repo (jika belum ada)"
if [[ ! -d "$APP_DIR/.git" ]]; then
    git clone https://github.com/gembongangger/majesatelegrambot.git "$APP_DIR"
else
    git -C "$APP_DIR" pull
fi

echo "==> 3/5 Setup venv & install Python dependencies"
su - angger -c "
    cd '$APP_DIR'
    if [[ ! -d venv ]]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
"

echo "==> 4/5 Siapkan .env"
if [[ ! -f "$APP_DIR/.env" ]]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo "⚠️  Isi token di: $APP_DIR/.env  lalu jalankan deploy lagi."
    echo "    nano $APP_DIR/.env"
    exit 1
else
    echo "    .env sudah ada."
fi

echo "==> 5/5 Pasang systemd service"
cp "$APP_DIR/majesa-bot.service" "$SERVICE_FILE"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

echo ""
echo "✅ Deploy selesai."
echo "   Cek status : sudo systemctl status $SERVICE_NAME"
echo "   Lihat log  : sudo journalctl -u $SERVICE_NAME -f"