from openai import OpenAI
import os
import shutil
from pathlib import Path

# Импортируем конфиг из корня
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Добавь в начало файла после других импортов
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL не установлен: pip install Pillow")

# === ВЫБОР СЕРВИСА ===
IMAGE_SERVICE = getattr(config, 'IMAGE_SERVICE', 'dalle')  # "dalle" или "pollinations"

if IMAGE_SERVICE == "dalle":
    from openai import OpenAI
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    print(f"📷 Сервис картинок: DALL-E 3")
elif IMAGE_SERVICE == "pollinations":
    print(f"📷 Сервис картинок: Pollinations.ai (бесплатно)")
else:
    print(f"⚠️  Неизвестный сервис: {IMAGE_SERVICE}, используем pollinations")
    IMAGE_SERVICE = "pollinations"


def get_image_library_path() -> str:
    """Возвращает путь к библиотеке картинок"""
    return os.path.join(config.PATHS["output"], "image_library")


def find_existing_image(description: str) -> str:
    """
    Ищет существующую картинку в библиотеке по описанию.
    """
    
    library_path = get_image_library_path()
    
    if not os.path.exists(library_path):
        return None
    
    # Ищем файлы которые начинаются с этого описания
    for filename in os.listdir(library_path):
        if filename.startswith(f"{description}_") or filename == f"{description}.jpg":
            return os.path.join(library_path, filename)
    
    # Пробуем найти частичное совпадение
    desc_lower = description.lower()
    for filename in os.listdir(library_path):
        if desc_lower in filename.lower():
            return os.path.join(library_path, filename)
    
    return None


def copy_image_to_project(source_path: str, dest_path: str) -> str:
    """Копирует картинку из библиотеки в папку проекта"""
    
    shutil.copy2(source_path, dest_path)
    print(f"📋 Скопировано из библиотеки: {os.path.basename(source_path)}")
    return dest_path


def generate_image_pollinations(
    prompt: str,
    output_path: str,
    width: int = None,
    height: int = None,
    seed: int = None,
    model: str = "flux",
    ratio_mode: str = "square"
) -> str:
    """
    Генерирует картинку через Pollinations.ai (старый URL).
    
    ratio_mode:
    - "square": генерирует 1:1 (1024×1024) ← РЕКОМЕНДУЮ
    - "vertical": генерирует 9:16 (832×1472)
    """
    
    # === Настройки разрешений ===
    if ratio_mode == "square":
        gen_width = getattr(config, 'POLLINATIONS_SQUARE_SIZE', 1024)
        gen_height = gen_width  # 1:1 квадрат
        print(f"🎨 Режим: КВАДРАТ {gen_width}×{gen_height}")
    else:
        gen_width = getattr(config, 'POLLINATIONS_WIDTH', 832)
        gen_height = getattr(config, 'POLLINATIONS_HEIGHT', 1472)
        print(f"🎨 Режим: ВЕРТИКАЛЬ {gen_width}×{gen_height}")
    
    print(f"📐 Модель: {model} | Seed: {seed if seed is not None else 'random'}")
    
    import requests
    from PIL import Image
    import io
    
    # === Промт (для квадрата не форсируем вертикаль) ===
    if ratio_mode == "square":
        aspect_prompt = f"{prompt}, professional photography, high detail, cinematic lighting, centered composition"
    else:
        vertical_keywords = ["vertical portrait", "full body shot", "tall composition"]
        aspect_prompt = f"{prompt}, {', '.join(vertical_keywords)}"
    
    # Кодируем промт
    encoded_prompt = requests.utils.quote(aspect_prompt)
    
    # === ✅ СТАРЫЙ РАБОЧИЙ URL ===
    url = f"{getattr(config, 'POLLINATIONS_BASE_URL', 'https://image.pollinations.ai')}/prompt/{encoded_prompt}"
    
    params = {
        "width": gen_width,
        "height": gen_height,
        "seed": seed if seed is not None else -1,
        "model": model,
        "nologo": "true"
    }
    
    url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    print(f"🔗 URL: {url[:200]}...")
    
    # === Скачиваем ===
    response = requests.get(url, timeout=120)
    
    if response.status_code != 200:
        raise Exception(f"Ошибка API: {response.status_code}")
    
    # === Сохраняем квадрат как есть ===
    img = Image.open(io.BytesIO(response.content))
    print(f"📊 Сгенерировано: {img.width}×{img.height}")
    
    # Для квадрата просто сохраняем (обрезка/зум будет при монтаже)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "JPEG", quality=95)
    
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"✅ Сохранено: {output_path} ({file_size:.1f} MB)")
    
    return output_path


def generate_image_dalle(
    prompt: str,
    output_path: str,
    size: str = "1024x1792",
    quality: str = "standard",
    model: str = "dall-e-3"
) -> str:
    """
    Генерирует картинку через DALL-E 3.
    """
    
    print(f"🎨 DALL-E 3: {prompt[:50]}...")
    print(f"📐 Размер: {size}, Качество: {quality}")
    
    # Создаём папку если нет
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Генерация через DALL-E 3
    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality=quality,
        n=1
    )
    
    # Скачиваем изображение
    image_url = response.data[0].url
    
    import requests
    img_data = requests.get(image_url).content
    
    with open(output_path, 'wb') as f:
        f.write(img_data)
    
    print(f"✅ Картинка сохранена: {output_path}")
    return output_path


def generate_image(
    prompt: str,
    output_path: str,
    size: str = "1080x1920",
    quality: str = "standard",
    model: str = None,
    seed: int = None
) -> str:
    """
    Генерирует картинку через выбранный сервис (DALL-E или Pollinations).
    """
    
    if IMAGE_SERVICE == "pollinations":
        return generate_image_pollinations(
            prompt=prompt,
            output_path=output_path,
            width=None,  # Будет взято из конфига внутри функции
            height=None,
            seed=getattr(config, 'IMAGE_SEED', -1),
            model=getattr(config, 'POLLINATIONS_MODEL', 'flux'),
            ratio_mode=getattr(config, 'IMAGE_RATIO_MODE', 'square')  # ← Новый параметр!
        )
    else:
        # DALL-E настройки
        dalle_model = getattr(config, 'DALL_E_MODEL', 'dall-e-3')
        dalle_quality = getattr(config, 'DALL_E_QUALITY', 'standard')
        
        return generate_image_dalle(
            prompt=prompt,
            output_path=output_path,
            size=size,
            quality=dalle_quality,
            model=dalle_model
        )


def generate_image_with_library(
    prompt: str,
    description: str,
    project_path: str,
    size: str = "1080x1920",
    quality: str = "standard",
    filename: str = None,
    seed: int = None
) -> str:
    """
    Генерирует картинку с проверкой библиотеки.
    """
    
    # Если имя файла не передано — генерируем из описания
    if filename is None:
        safe_description = description[:50].replace(' ', '_').replace('/', '_').replace(':', '')
        filename = f"{safe_description}.jpg"
    
    dest_path = os.path.join(project_path, filename)
    
    # Проверяем библиотеку (ищем по описанию без номера)
    existing_path = find_existing_image(description)
    
    if existing_path:
        print(f"📚 Найдена в библиотеке: {os.path.basename(existing_path)}")
        copy_image_to_project(existing_path, dest_path)
        return dest_path
    
    # Генерируем новую
    print(f"✨ Генерация новой картинки...")
    
    # Улучшаем промт
    if IMAGE_SERVICE == "pollinations":
        full_prompt = f"{prompt}, cinematic lighting, high detail, photorealistic, vertical 9:16"
    else:
        full_prompt = f"{prompt}, vertical 9:16 aspect ratio, cinematic lighting, high detail, photorealistic"
    
    # Путь в библиотеку (сохраняем БЕЗ номера для переиспользования)
    library_path = get_image_library_path()
    os.makedirs(library_path, exist_ok=True)
    library_filename = f"{description.replace(' ', '_')}.jpg"
    library_file = os.path.join(library_path, library_filename)
    
    # Генерируем и сохраняем в библиотеку
    generate_image(full_prompt, library_file, size, quality, seed=seed)
    
    # Копируем в проект (с номером)
    copy_image_to_project(library_file, dest_path)
    
    return dest_path


def generate_all_images(
    prompts: list,
    project_path: str,
    topic: str
) -> list:
    """
    Генерирует все картинки для проекта с нумерацией.
    """
    
    print(f"\n{'='*60}")
    print(f"🎨 ГЕНЕРАЦИЯ КАРТИНОК ДЛЯ: {topic[:50]}")
    print(f"{'='*60}")
    
    generated_paths = []
    
    for i, item in enumerate(prompts, 1):
        description = item.get("description", f"image_{i}")
        prompt = item.get("prompt", "")
        
        # Формируем имя файла с номером: image_1_Описание.jpg
        safe_description = description[:50].replace(' ', '_').replace('/', '_').replace(':', '')
        filename = f"image_{i}_{safe_description}.jpg"
        dest_path = os.path.join(project_path, filename)
        
        print(f"\n[{i}/{len(prompts)}] {filename}")
        
        try:
            path = generate_image_with_library(
                prompt=prompt,
                description=description,
                project_path=project_path,
                filename=filename,
                seed=i  # Seed для воспроизводимости
            )
            generated_paths.append(path)
            
            # Пауза между генерациями (для DALL-E, для Pollinations можно меньше)
            if i < len(prompts):
                pause = 1 if IMAGE_SERVICE == "pollinations" else 3
                print(f"⏸️ Пауза {pause} сек...")
                import time
                time.sleep(pause)
                
        except Exception as e:
            print(f"❌ Ошибка генерации: {e}")
            # Продолжаем с следующей картинкой
    
    print(f"\n✅ Сгенерировано {len(generated_paths)} из {len(prompts)} картинок")
    return generated_paths