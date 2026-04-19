import os
import requests
from pathlib import Path

# Импортируем конфиг из корня
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def generate_image_pollinations(
    prompt: str,
    output_path: str,
    width: int = None,
    height: int = None,
    seed: int = None,
    model: str = "flux",
    ratio_mode: str = "square"  # ← ДОБАВЛЕНО: "square" или "vertical"
) -> str:
    """
    Генерирует картинку через Pollinations.ai.
    
    ratio_mode:
    - "square": генерирует 1:1 (1024×1024), потом добавляет фон для 9:16
    - "vertical": генерирует сразу 9:16 (832×1472)
    """
    
    # === Настройки разрешений ===
    if ratio_mode == "square":
        gen_width = getattr(config, 'POLLINATIONS_SQUARE_SIZE', 1024)
        gen_height = gen_width
        print(f"🎨 Режим: КВАДРАТ {gen_width}×{gen_height} → потом 9:16")
    else:
        gen_width = getattr(config, 'POLLINATIONS_WIDTH', 832)
        gen_height = getattr(config, 'POLLINATIONS_HEIGHT', 1472)
        print(f"🎨 Режим: ВЕРТИКАЛЬ {gen_width}×{gen_height}")
    
    print(f"📐 Модель: {model} | Seed: {seed if seed is not None else 'random'}")
    
    # === Промт ===
    if ratio_mode == "square":
        aspect_prompt = f"{prompt}, professional photography, high detail, cinematic lighting"
    else:
        vertical_keywords = [
            "vertical portrait orientation",
            "full body shot",
            "tall composition",
            "cinematic 9:16 framing"
        ]
        aspect_prompt = f"{prompt}, {', '.join(vertical_keywords)}"
    
    # Кодируем промт
    encoded_prompt = requests.utils.quote(aspect_prompt)
    
    # === Правильный URL ===
    url = f"https://gen.pollinations.ai/image/{encoded_prompt}"
    
    params = {
        "model": model,
        "width": gen_width,
        "height": gen_height,
        "seed": seed if seed is not None else -1,
        "enhance": "true",
        "negative_prompt": "distorted, stretched, squashed, deformed, bad proportions, low quality"
    }
    
    url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    print(f"🔗 URL: {url[:200]}...")
    
    # === Скачиваем ===
    response = requests.get(url, timeout=120)
    
    if response.status_code != 200:
        try:
            error = response.json()
            raise Exception(f"Ошибка API {response.status_code}: {error}")
        except:
            raise Exception(f"Ошибка API: {response.status_code}")
    
    # === Обрабатываем изображение ===
    from PIL import Image, ImageFilter
    import io
    
    img = Image.open(io.BytesIO(response.content))
    print(f"📊 Сгенерировано: {img.width}×{img.height}")
    
    # === Если квадрат → конвертируем в 9:16 для TikTok ===
    if ratio_mode == "square":
        print("🔄 Конвертация квадрата в 9:16 для TikTok...")
        
        target_width = getattr(config, 'TIKTOK_FINAL_WIDTH', 1080)
        target_height = getattr(config, 'TIKTOK_FINAL_HEIGHT', 1920)
        
        # Создаём новый холст 9:16
        final_img = Image.new("RGB", (target_width, target_height), color="black")
        
        # === Размытый фон ===
        if getattr(config, 'TIKTOK_BACKGROUND_BLUR', True):
            print("   🎭 Добавляем размытый фон...")
            bg = img.copy()
            bg = bg.resize((target_width, target_height), Image.Resampling.LANCZOS)
            bg = bg.filter(ImageFilter.GaussianBlur(radius=50))
            final_img.paste(bg, (0, 0))
        
        # === Центрируем основное изображение ===
        img_resized = img.copy()
        img_resized = img_resized.resize((target_width, target_width), Image.Resampling.LANCZOS)
        
        x = 0
        y = (target_height - target_width) // 2
        
        final_img.paste(img_resized, (x, y))
        img = final_img
        print(f"✅ Конвертировано в {target_width}×{target_height}")
    
    else:
        # === Если сразу вертикаль — просто ресайз ===
        target_size = (1080, 1920)
        if img.size != target_size:
            img = img.resize(target_size, Image.Resampling.LANCZOS)
    
    # === Сохраняем ===
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "JPEG", quality=95, dpi=(300, 300))
    
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"✅ Сохранено: {output_path} ({file_size:.1f} MB)")
    
    # Финальная проверка
    final_img = Image.open(output_path)
    ratio = final_img.width / final_img.height
    print(f"📊 Итог: {final_img.width}×{final_img.height} | пропорции: {ratio:.3f}")
    
    return output_path