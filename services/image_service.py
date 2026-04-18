from openai import OpenAI
import os
import shutil
from pathlib import Path

# Импортируем конфиг из корня
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)


def get_image_library_path() -> str:
    """Возвращает путь к библиотеке картинок"""
    return os.path.join(config.PATHS["output"], "image_library")


def find_existing_image(description: str) -> str:
    """
    Ищет существующую картинку в библиотеке по описанию.
    
    Args:
        description: Описание картинки (например "Иван_грозный_троне")
    
    Returns:
        Путь к файлу если найден, иначе None
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


def generate_image(
    prompt: str, 
    output_path: str, 
    size: str = "1024x1792",  # 9:16 для TikTok
    quality: str = "standard",
    model: str = "dall-e-3"
) -> str:
    """
    Генерирует картинку через DALL-E 3.
    
    Args:
        prompt: Промт для генерации
        output_path: Путь для сохранения
        size: Размер (1024x1792 для 9:16)
        quality: "standard" или "hd"
        model: "dall-e-3" или "dall-e-2"
    
    Returns:
        Путь к сохранённому файлу
    """
    
    print(f"🎨 Генерация картинки: {prompt[:50]}...")
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


def generate_image_with_library(
    prompt: str, 
    description: str, 
    project_path: str,
    size: str = "1024x1792",
    quality: str = "standard"
) -> str:
    """
    Генерирует картинку с проверкой библиотеки.
    Если картинка уже есть — копирует из библиотеки.
    
    Args:
        prompt: Промт для генерации
        description: Описание для имени файла
        project_path: Папка проекта куда сохранить
        size: Размер картинки
        quality: Качество
    
    Returns:
        Путь к файлу в папке проекта
    """
    
    # Формируем имя файла
    safe_description = description[:50].replace(' ', '_').replace('/', '_').replace(':', '')
    filename = f"{safe_description}.jpg"
    dest_path = os.path.join(project_path, filename)
    
    # Проверяем библиотеку
    existing_path = find_existing_image(safe_description)
    
    if existing_path:
        print(f"📚 Найдена в библиотеке: {os.path.basename(existing_path)}")
        copy_image_to_project(existing_path, dest_path)
        return dest_path
    
    # Генерируем новую
    print(f"✨ Генерация новой картинки...")
    
    # Добавляем технические требования к промту
    full_prompt = f"{prompt}, vertical 9:16 aspect ratio, cinematic lighting, high detail, photorealistic"
    
    # Путь в библиотеку
    library_path = get_image_library_path()
    os.makedirs(library_path, exist_ok=True)
    library_file = os.path.join(library_path, filename)
    
    # Генерируем и сохраняем в библиотеку
    generate_image(full_prompt, library_file, size, quality)
    
    # Копируем в проект
    copy_image_to_project(library_file, dest_path)
    
    return dest_path


def generate_all_images(
    prompts: list, 
    project_path: str,
    topic: str
) -> list:
    """
    Генерирует все картинки для проекта.
    
    Args:
        prompts: Список промтов [{"description": "...", "prompt": "..."}, ...]
        project_path: Папка проекта
        topic: Тема для логирования
    
    Returns:
        Список путей к картинкам
    """
    
    print(f"\n{'='*60}")
    print(f"🎨 ГЕНЕРАЦИЯ КАРТИНОК ДЛЯ: {topic[:50]}")
    print(f"{'='*60}")
    
    generated_paths = []
    
    for i, item in enumerate(prompts, 1):
        description = item.get("description", f"image_{i}")
        prompt = item.get("prompt", "")
        
        print(f"\n[{i}/{len(prompts)}] {description}")
        
        try:
            path = generate_image_with_library(
                prompt=prompt,
                description=description,
                project_path=project_path
            )
            generated_paths.append(path)
            
            # Пауза между генерациями (DALL-E 3 лимит)
            if i < len(prompts):
                print("⏸️ Пауза 3 секунды...")
                import time
                time.sleep(3)
                
        except Exception as e:
            print(f"❌ Ошибка генерации: {e}")
            # Продолжаем с следующей картинкой
    
    print(f"\n✅ Сгенерировано {len(generated_paths)} из {len(prompts)} картинок")
    return generated_paths