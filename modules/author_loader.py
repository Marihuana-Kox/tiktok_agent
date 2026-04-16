import json
import os

def load_author_style() -> dict:
    """Загружает стиль автора из файла"""
    
    filepath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "..", 
        "author_style.json"
    )
    
    if not os.path.exists(filepath):
        raise Exception("Файл author_style.json не найден!")
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def format_author_prompt(style: dict) -> str:
    """Форматирует стиль в промпт для модели"""
    
    prompt = f"""
=== СТИЛЬ АВТОРА ===
Имя: {style['name']}
Канал: {style['channel']}

ОПИСАНИЕ СТИЛЯ:
{style['style_description']}

ТОН ПОВЕСТВОВАНИЯ:
{style['tone']}

❌ ЗАПРЕЩЁННЫЕ ФРАЗЫ (никогда не использовать):
{chr(10).join('- ' + p for p in style['forbidden_phrases'])}

✅ ОБЯЗАТЕЛЬНЫЕ ЭЛЕМЕНТЫ (должны быть в каждом тексте):
{chr(10).join('- ' + e for e in style['required_elements'])}

=== СТРУКТУРА СТАТЬИ ===

ХУК:
{style['structure']['hook']}

ОСНОВНАЯ ЧАСТЬ:
{style['structure']['body']}

АЛЬТЕРНАТИВНАЯ ВЕРСИЯ:
{style['structure']['alternative']}

ФИНАЛ:
{style['structure']['final']}

=== ПРИМЕРЫ ===

❌ ПЛОХО: {style['examples']['bad']}
✅ ХОРОШО: {style['examples']['good']}

Используй этот стиль во ВСЕХ текстах. Это не рекомендация — это требование.
"""
    
    return prompt