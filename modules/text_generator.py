from openai import OpenAI
import config
import os
from datetime import datetime

client = OpenAI(api_key=config.OPENAI_API_KEY)

def generate_script(topic: str, user_intro: str = "") -> str:
    """Генерирует профессиональный сценарий для TikTok"""
    
    system_prompt = """
        Ты — ведущий сценарист документальных расследований для TikTok.
        Твоя специализация: исторические загадки с элементами альтернативного взгляда.

        ТВОЯ ЗАДАЧА:
        Написать сценарий, который зритель досмотрит до конца (60 секунд).

        ЖЁСТКИЕ ПРАВИЛА КОНТЕНТА:
        1. ЗАПРЕЩЕНО: использовать клише ("в этой статье", "давайте разберёмся", "в заключение")
        2. ЗАПРЕЩЕНО: писать общие фразы без фактов ("учёные до сих пор спорят", "существует много версий")
        3. ОБЯЗАТЕЛЬНО: каждое утверждение подкреплять фактом (дата, имя, место, число)
        4. ОБЯЗАТЕЛЬНО: использовать конкретные детали (названия, размеры, веса, расстояния)
        5. СТИЛЬ: утвердительный, уверенный, без сомнений в каждом предложении

        СТРУКТУРА СЦЕНАРИЯ (заполнять ВСЕ блоки):

        === НАЗВАНИЕ ===
        (2-4 слова, провокационный заголовок)

        === ОПИСАНИЕ ===
        (2-3 предложения, интрига без спойлеров)

        === ТЕКСТ ДЛЯ ОЗВУЧКИ ===
        (СТРОГО 280-320 слов. Разбей на 4-5 абзацев)

        АБЗАЦ 1 — ХУК (60-80 слов):
        - Шок-факт или провокационное утверждение
        - Конкретная цифра или дата для доверия
        - Вопрос, который переворачивает представление

        АБЗАЦ 2 — ОФИЦИАЛЬНАЯ ВЕРСИЯ (60-80 слов):
        - Что говорит наука/история
        - Конкретные даты, имена, события
        - Без насмешек, просто факты

        АБЗАЦ 3 — ПАРАДОКС (80-100 слов):
        - Что не сходится в официальной версии
        - Конкретные противоречия (цифры, технологии, логистика)
        - Минимум 2-3 конкретных примера несоответствий

        АБЗАЦ 4 — АЛЬТЕРНАТИВА + ФИНАЛ (60-80 слов):
        - Возможное объяснение без утверждений
        - Вопрос зрителю для дискуссии
        - Призыв к комментарию и подписке

        === ХЭШТЕГИ ===
        (ровно 5 хэштегов через пробел)

        ПРОВЕРКА ПЕРЕД ВЫВОДОМ:
        Посчитай слова в разделе ТЕКСТ ДЛЯ ОЗВУЧКИ. Если меньше 280 — ДОПИШИ фактов и деталей в абзацы 2 и 3.
        """

    user_prompt = f"""
        Тема: {topic}{user_intro}

        ТРЕБОВАНИЯ К НАПОЛНЕНИЮ:
        1. Используй минимум 5 конкретных фактов (даты, имена, числа, названия)
        2. Добавь минимум 3 парадокса или противоречия
        3. Избегай общих фраз — пиши конкретно
        4. ТЕКСТ ДЛЯ ОЗВУЧКИ: СТРОГО 280-320 слов
        5. Название и хэштеги НЕ входят в подсчёт слов

        ПРИМЕР КОНКРЕТИКИ (как писать):
        ❌ ПЛОХО: "Учёные не могут объяснить как это построили"
        ✅ ХОРОШО: "Блоки весом 200 тонн поднимали на высоту 40 метров без колёс и кранов"

        ❌ ПЛОХО: "Это древнее сооружение"
        ✅ ХОРОШО: "Сооружение датируется 2500 годом до н.э., за 1000 лет до появления письменности"

        НАЧНИ ГЕНЕРАЦИЮ. ПРОВЕРЬ КОЛИЧЕСТВО СЛОВ ПЕРЕД ВЫВОДОМ.
        """

    response = client.chat.completions.create(
        model=config.TEXT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.8,
        max_tokens=config.MAX_TOKENS
    )
    
    return response.choices[0].message.content


def count_words(text: str) -> int:
    """Считает количество слов в тексте"""
    return len(text.split())


def validate_script(script: str) -> dict:
    """Проверяет соответствие сценария требованиям"""
    
    sections = {
        "title": "",
        "description": "",
        "voice_text": "",
        "hashtags": ""
    }
    
    current_section = None
    for line in script.split("\n"):
        if "=== НАЗВАНИЕ ===" in line:
            current_section = "title"
        elif "=== ОПИСАНИЕ ===" in line:
            current_section = "description"
        elif "=== ТЕКСТ ДЛЯ ОЗВУЧКИ ===" in line:
            current_section = "voice_text"
        elif "=== ХЭШТЕГИ ===" in line:
            current_section = "hashtags"
        elif current_section and line.strip():
            sections[current_section] += line + "\n"
    
    # Считаем слова
    voice_words = count_words(sections["voice_text"])
    desc_words = count_words(sections["description"])
    
    return {
        "valid": voice_words >= 250,
        "voice_words": voice_words,
        "desc_words": desc_words,
        "title": sections["title"].strip(),
        "hashtags": sections["hashtags"].strip()
    }


def save_script(script: str, topic: str) -> str:
    """Сохраняет сценарий в файл"""
    
    filename = topic.replace(" ", "_").replace(":", "").replace("/", "") + ".txt"
    filepath = os.path.join(config.PATHS["scripts"], filename)
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    content = f"Тема: {topic}\nДата: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{script}"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath


def generate_and_save(topic: str, user_intro: str = "", max_retries: int = 2) -> str:
    """Генерирует и сохраняет сценарий с проверкой качества"""
    
    for attempt in range(max_retries):
        script = generate_script(topic, user_intro)
        validation = validate_script(script)
        
        print(f"📊 Проверка: {validation['voice_words']} слов в тексте")
        
        if validation["valid"]:
            filepath = save_script(script, topic)
            return filepath
        else:
            print(f"⚠️ Мало слов (попытка {attempt + 1}/{max_retries}), генерирую заново...")
    
    # Если не удалось — сохраняем как есть
    filepath = save_script(script, topic)
    print(f"⚠️ Текст сохранён но содержит только {validation['voice_words']} слов")
    return filepath