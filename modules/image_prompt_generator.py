from openai import OpenAI
import config
import os
import re
import json

client = OpenAI(api_key=config.OPENAI_API_KEY)


def extract_key_scenes(article: str) -> list:
    """Извлекает ключевые сцены из статьи для визуализации"""
    
    paragraphs = [p.strip() for p in article.split('\n') if p.strip()]
    
    key_scenes = []
    for para in paragraphs:
        if re.search(r'\d{4}|тысяч|миллион|год|век|царь|император|король', para, re.IGNORECASE):
            if len(para) > 50:
                key_scenes.append(para[:200])
    
    if len(key_scenes) < 6:
        for para in paragraphs:
            if len(para) > 50 and para not in key_scenes:
                key_scenes.append(para[:200])
            if len(key_scenes) >= 8:
                break
    
    return key_scenes[:8]


def generate_image_prompts(topic: str, article: str, angle: str = "") -> list:
    """
    Генерирует промты для картинок на основе статьи.
    
    Returns:
        Список словарей: [{"description": "Иван_грозный", "prompt": "..."}, ...]
    
    Raises:
        Exception: Если не удалось сгенерировать промты
    """
    
    scenes = extract_key_scenes(article)
    
    if len(scenes) < 3:
        raise Exception(f"Не удалось извлечь ключевые сцены из статьи (найдено: {len(scenes)})")
    
    print(f"\n🎨 Найдено {len(scenes)} ключевых сцен для визуализации")
    
    system_prompt = """
Ты — режиссёр визуального контента для TikTok.
Твоя задача: создать 6-9 детальных промтов для генерации картинок по статье.

ТРЕБОВАНИЯ К ПРОМТАМ:
1. ФОРМАТ: 9:16 (вертикальный для TikTok)
2. СТИЛЬ: Кинематографичный, драматичный, с контрастным освещением
3. ДЕТАЛИ: Описывай конкретных людей, объекты, действия
4. АТМОСФЕРА: Соответствует вектору статьи (негативный/позитивный/загадочный)
5. ЯЗЫК: Промт на английском для лучшего качества генерации

ФОРМАТ ОТВЕТА (строго JSON массив):
[
  {
    "description": "Краткое_описание_на_русском_для_имени_файла",
    "prompt": "Detailed cinematic prompt in English..."
  }
]

ПРАВИЛА ДЛЯ description:
- 3-5 слов на русском
- Без пробелов (подчёркивания вместо пробелов)
- Уникальное для каждой картинки
- Конкретное описание сцены
- Примеры: "Иван_грозный_троне", "Петергоф_фонтаны_вид", "Екатерина_манифест_подпись"
- ЗАПРЕЩЕНО: "Сцена_1", "Картинка_1", "image_1"

ПРАВИЛА ДЛЯ prompt:
- Минимум 50 слов
- Детальное описание сцены
- Указание ракурса, освещения, атмосферы
- Обязательно: "vertical 9:16 aspect ratio"
"""

    user_prompt = f"""
Тема статьи: {topic}
Вектор: {angle}

Текст статьи для анализа:
{article[:4000]}

Ключевые сцены для визуализации:
{chr(10).join(f'- {s}' for s in scenes)}

Создай 6-9 промтов для картинок 9:16.
Верни ТОЛЬКО JSON массив без дополнительного текста.
"""

    response_text = ""
    
    try:
        response = client.chat.completions.create(
            model=config.TEXT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        response_text = response.choices[0].message.content.strip()
        
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        
        if json_match:
            response_text = json_match.group()
        
        prompts_data = json.loads(response_text)
        
        if not prompts_data or len(prompts_data) == 0:
            raise Exception("Пустой ответ от модели")
        
        for i, item in enumerate(prompts_data):
            desc = item.get("description", "")
            prompt_text = item.get("prompt", "")
            
            if "сцена" in desc.lower() or "scene" in desc.lower():
                raise Exception(f"Промт #{i+1} содержит заглушку в description: {desc}")
            
            if len(prompt_text) < 30:
                raise Exception(f"Промт #{i+1} слишком короткий: {prompt_text[:50]}")
        
        print(f"✅ Сгенерировано {len(prompts_data)} валидных промтов")
        return prompts_data
        
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        print(f"Ответ модели: {response_text[:500] if response_text else 'пустой'}")
        raise Exception("Не удалось распарсить ответ модели как JSON")
        
    except Exception as e:
        print(f"❌ Ошибка генерации промтов: {e}")
        raise Exception(f"Генерация промтов не удалась: {e}")


def save_prompts_to_file(prompts: list, output_path: str):
    """Сохраняет промты в JSON файл"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Промты сохранены: {output_path}")