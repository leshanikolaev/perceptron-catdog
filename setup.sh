#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/myapp"
REPO_URL="https://github.com/leshanikolaev/perceptron-catdog.git"

echo "==> Устанавливаю системные зависимости"
sudo apt update
sudo apt install -y python3-pip python3-venv git

echo "==> Готовлю директорию приложения"
sudo mkdir -p "$APP_DIR"
sudo chown "$USER:$USER" "$APP_DIR"

if [ -d "$APP_DIR/.git" ]; then
    echo "==> Репозиторий уже есть, обновляю"
    cd "$APP_DIR"
    git pull
else
    echo "==> Клонирую репозиторий"
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

echo "==> Создаю виртуальное окружение"
python3 -m venv venv
source venv/bin/activate

echo "==> Устанавливаю Python-зависимости"
pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install flask pillow

echo "==> Настраиваю systemd-сервис"
sudo cp "$APP_DIR/myapp.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable myapp
sudo systemctl restart myapp

echo "==> Готово! Проверка статуса:"
sudo systemctl status myapp --no-pager
