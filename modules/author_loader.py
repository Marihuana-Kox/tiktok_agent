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
    
    # === БЛОК ФОРМАТИРОВАНИЯ ЧИСЕЛ ===
    number_block = ""
    if "number_formatting" in style:
        num_fmt = style["number_formatting"]
        examples = num_fmt.get("examples", {})
        
        examples_text = "\n".join(f'  "{k}" → "{v}"' for k, v in examples.items())
        
        number_block = f"""
=== ФОРМАТИРОВАНИЕ ЧИСЕЛ (КРИТИЧНО ДЛЯ ОЗВУЧКИ) ===

ПРАВИЛО: {num_fmt.get('rule', 'Все числа писать словами')}

ПРИМЕРЫ ПРЕОБРАЗОВАНИЯ:
{examples_text}

❌ ЗАПРЕЩЕНО в тексте для озвучки:
- Цифры: 1763, 2560, 20000
- Сокращения: тыс., млн, млрд, мм, см, кг
- Форматы: $5, 3.14, 1/2

✅ ОБЯЗАТЕЛЬНО:
- "тысяча семьсот шестьдесят третий год" вместо "1763 год"
- "двадцать тысяч" вместо "20 000"
- "три миллиметра" вместо "3 мм"
- "полторы тысячи лет" вместо "1500 лет"

Это критично для правильной озвучки русским голосом!

"""
    
    # === БЛОК ХУКА (если есть) ===
    hook_block = ""
    if "hook_examples" in style:
        hook = style["hook_examples"]
        hook_block = f"""
=== ПРАВИЛА ХУКА (ПЕРВЫЕ 3 СЕКУНДЫ) ===

Первое предложение: {hook.get('first_sentence', 'Шок-факт с цифрой')}
Второе предложение: {hook.get('second_sentence', 'Парадокс или сравнение')}
Третье предложение: {hook.get('third_sentence', 'Вопрос который переворачивает')}

❌ ЗАПРЕЩЁННЫЕ ОТКРЫТИЯ:
- "Знали ли вы что..."
- "Представьте себе..."
- "В этой статье мы рассмотрим..."
- "Давайте поговорим о..."

✅ ПРИМЕР СИЛЬНОГО ХУКА:
{style.get('examples', {}).get('good', '')}

ВАЖНО: Если первое предложение не шокирует — перепиши его.

"""
    
    # === БЛОК СТРУКТУРЫ (если есть) ===
    structure_block = ""
    if "structure" in style:
        struct = style["structure"]
        structure_block = f"""
=== СТРУКТУРА СТАТЬИ ===

ХУК:
{struct.get('hook', '')}

ОСНОВНАЯ ЧАСТЬ:
{struct.get('body', '')}

АЛЬТЕРНАТИВНАЯ ВЕРСИЯ:
{struct.get('alternative', '')}

ФИНАЛ:
{struct.get('final', '')}

"""
    
    # === СОБИРАЕМ ВСЁ ВМЕСТЕ ===
    prompt = f"""
=== СТИЛЬ АВТОРА ===
Имя: {style['name']}
Канал: {style['channel']}

ОПИСАНИЕ СТИЛЯ:
{style['style_description']}

ТОН ПОВЕСТВОВАНИЯ:
{style['tone']}

{number_block}

{hook_block}

{structure_block}

❌ ЗАПРЕЩЁННЫЕ ФРАЗЫ (никогда не использовать):
{chr(10).join('- ' + p for p in style['forbidden_phrases'])}

✅ ОБЯЗАТЕЛЬНЫЕ ЭЛЕМЕНТЫ (должны быть в каждом тексте):
{chr(10).join('- ' + e for e in style['required_elements'])}

=== ПРИМЕРЫ ===

❌ ПЛОХО: {style['examples']['bad']}
✅ ХОРОШО: {style['examples']['good']}

Используй этот стиль во ВСЕХ текстах. Это не рекомендация — это требование.
"""
    
    return prompt


def format_angle_prompt(angle: str) -> str:
    """Форматирует вектор темы в промпт"""
    
    if not angle:
        return ""
    
    prompt = f"""
=== ВЕКТОР СТАТЬИ (ПРИОРИТЕТ) ===
Подача материала: {angle}

ВАЖНО:
- Все факты подбирай под этот вектор
- Не бойся острых формулировок в рамках этого угла
- Если вектор негативный — акцентируй противоречия
- Если вектор позитивный — акцентируй достижения
- Это не цензура — это редакторская позиция

Используй этот вектор как главный ориентир при написании.
"""
    
    return prompt