# perceptron-catdog

Учебный pet-проект: классификатор изображений (кошка / собака / не то, не другое) на базе нейросети, с веб-интерфейсом и деплоем в облако.

## Структура репозитория

```
app.py              # Flask-приложение с UI и классификацией (предобученная MobileNetV2)
requirements.txt    # Python-зависимости (flask, pillow)
myapp.service       # systemd-юнит для автозапуска приложения на VM
setup.sh            # Скрипт автоматической установки и деплоя на VM
Dockerfile           # Сборка приложения в Docker-образ
.dockerignore
.github/workflows/docker-build.yml   # CI: автосборка и публикация образа в ghcr.io при push в main
```

## Запуск локально

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

python app.py
```

Открыть в браузере: `http://localhost` (порт 80, нужны права администратора/root; либо поменять порт в `app.py` на 8080 для локального теста).

## Деплой на VM (Yandex Cloud, Ubuntu 24.04)

1. Создать VM с публичным IP, открыть в Security Group порты **22** (SSH) и **80** (HTTP)
2. Скопировать проект на VM (клонировать репозиторий или `scp`)
3. Запустить автоматический скрипт:

```bash
chmod +x setup.sh
./setup.sh
```

Скрипт сам: установит зависимости, поднимет venv, настроит и запустит systemd-сервис `myapp`.

Проверка статуса сервиса:
```bash
sudo systemctl status myapp
sudo journalctl -u myapp -f
```

После этого UI доступен по `http://<белый_IP_VM>`.

## Docker

Собрать и запустить локально:
```bash
docker build -t perceptron-catdog .
docker run -p 80:80 perceptron-catdog
```

Готовый образ также автоматически собирается и публикуется в GitHub Container Registry при каждом push в `main` (см. `.github/workflows/docker-build.yml`):

```bash
docker pull ghcr.io/leshanikolaev/perceptron-catdog:latest
docker run -p 80:80 ghcr.io/leshanikolaev/perceptron-catdog:latest
```

## Как это работает

- Модель: предобученная **MobileNetV2** (обучена на ImageNet), собственное обучение не требуется
- Классификация: по индексу класса ImageNet определяется, порода собаки это или кошки; порог уверенности ниже 30% → "не смогла распознать"
- UI: одна HTML-страница с формой загрузки фото (Flask, без фронтенд-фреймворков)
