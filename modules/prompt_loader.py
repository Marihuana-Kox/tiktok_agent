import os
import random
import config 

def get_prompts_folder() -> str:
    """Возвращает путь к папке с промптами"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "..", "prompts")

def list_available_prompts() -> list:
    """Показывает доступные промпты"""
    prompts_folder = get_prompts_folder()
    files = [f for f in os.listdir(prompts_folder) if f.endswith(".txt")]
    return files

def load_prompt(prompt_name: str = None, random_select: bool = False) -> str:
    """
    Загружает промпт из файла.
    
    Args:
        prompt_name: имя файла (например "prompt_conspiracy.txt")
        random_select: если True — выбирает случайный промпт
    
    Returns:
        Текст промпта
    """
    prompts_folder = get_prompts_folder()
    
    # Получаем список файлов
    available = list_available_prompts()
    
    if not available:
        raise Exception("Нет файлов с промптами в папке prompts/")
    
    # Выбираем промпт
    if random_select:
        selected = random.choice(available)
    elif prompt_name:
        selected = prompt_name if prompt_name.endswith(".txt") else f"{prompt_name}.txt"
        if selected not in available:
            print(f"⚠️ Промпт '{selected}' не найден. Выбираю случайный...")
            selected = random.choice(available)
    else:
        selected = available[0]  # Первый по умолчанию
    
    # Читаем файл
    filepath = os.path.join(prompts_folder, selected)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"📜 Использован промпт: {selected}")
    return content