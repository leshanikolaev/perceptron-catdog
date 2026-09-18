FROM python:3.11-slim

WORKDIR /app

# Ставим torch/torchvision отдельно - им нужен специальный CPU-индекс
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 80

CMD ["python", "app.py"]
