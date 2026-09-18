import io
import torch
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
from flask import Flask, request, render_template_string

app = Flask(__name__)

# -----------------------------------------------------------------
# Загружаем предобученную модель один раз при старте сервера
# -----------------------------------------------------------------
print("Загружаю модель (при первом запуске скачает веса, нужен интернет)...")
model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
model.eval()

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                          std=[0.229, 0.224, 0.225]),
])

# Индексы классов ImageNet (модель обучена на 1000 классов).
# Диапазон 151-268 - это разные породы собак.
# 281-285 - разные породы/окрасы кошек.
DOG_CLASSES = set(range(151, 269))
CAT_CLASSES = {281, 282, 283, 284, 285}

# Порог уверенности: ниже него считаем, что модель не смогла распознать
CONFIDENCE_THRESHOLD = 0.30

HTML_PAGE = """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Кошка или собака?</title>
  <style>
    body { font-family: sans-serif; max-width: 500px; margin: 60px auto; text-align: center; padding: 0 20px; }
    .result { font-size: 22px; margin-top: 20px; padding: 20px; border-radius: 10px; }
    .ok { background: #e6ffe6; }
    .unknown { background: #fff3cd; }
    input[type=file] { margin-bottom: 15px; }
    button {
      padding: 10px 24px; font-size: 16px; cursor: pointer;
      border-radius: 8px; border: none; background: #4a90d9; color: white;
    }
    img { max-width: 100%; margin-top: 20px; border-radius: 10px; }
  </style>
</head>
<body>
  <h1>Кошка или собака? 🐱🐶</h1>
  <form method="POST" enctype="multipart/form-data">
    <input type="file" name="photo" accept="image/*" required>
    <br>
    <button type="submit">Распознать</button>
  </form>
  {% if result %}
    <div class="result {{ 'ok' if is_confident else 'unknown' }}">
      {{ result }}
    </div>
  {% endif %}
</body>
</html>
"""


def classify_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = preprocess(img).unsqueeze(0)

    with torch.no_grad():
        outputs = model(tensor)
        probs = F.softmax(outputs[0], dim=0)

    top_prob, top_idx = torch.max(probs, dim=0)
    top_prob = top_prob.item()
    top_idx = top_idx.item()

    if top_prob < CONFIDENCE_THRESHOLD:
        return "Не смогла распознать 🤷", False

    if top_idx in DOG_CLASSES:
        return f"Это собака 🐶 (уверенность {top_prob:.0%})", True
    elif top_idx in CAT_CLASSES:
        return f"Это кошка 🐱 (уверенность {top_prob:.0%})", True
    else:
        return f"Это не то, и не другое (уверенность {top_prob:.0%})", False


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    is_confident = False
    if request.method == "POST":
        file = request.files.get("photo")
        if file and file.filename:
            image_bytes = file.read()
            result, is_confident = classify_image(image_bytes)

    return render_template_string(HTML_PAGE, result=result, is_confident=is_confident)


if __name__ == "__main__":
    # 0.0.0.0 - слушаем на всех интерфейсах, чтобы был доступ по внешнему IP
    app.run(host="0.0.0.0", port=80)
