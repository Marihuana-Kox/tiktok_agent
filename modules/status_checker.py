import os

def check_topic_status(topic_path: str) -> dict:
    """
    Проверяет какие компоненты уже есть в папке темы.
    
    Returns:
        Словарь со статусом каждого компонента
    """
    
    status = {
        "script": False,
        "voice": False,
        "prompts": False,
        "images": [],
        "images_count": 0
    }
    
    if not os.path.exists(topic_path):
        return status
    
    # Проверяем сценарий
    if os.path.exists(os.path.join(topic_path, "script.txt")):
        status["script"] = True
    
    # Проверяем аудио
    if os.path.exists(os.path.join(topic_path, "voice.mp3")):
        status["voice"] = True
    
    # Проверяем промты
    if os.path.exists(os.path.join(topic_path, "prompts.json")):
        status["prompts"] = True
    
    # Проверяем картинки (ищем файлы .jpg кроме voice.mp3)
    for filename in os.listdir(topic_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            status["images"].append(filename)
    
    status["images_count"] = len(status["images"])
    
    return status


def print_status(status: dict, topic_id: int):
    """Выводит статус темы в консоль"""
    
    print(f"\n{'='*60}")
    print(f"📊 СТАТУС ТЕМЫ #{topic_id}")
    print(f"{'='*60}")
    
    # Сценарий
    if status["script"]:
        print("✅ Сценарий: готов")
    else:
        print("❌ Сценарий: нужен")
    
    # Озвучка
    if status["voice"]:
        print("✅ Озвучка: готова")
    else:
        print("❌ Озвучка: нужна")
    
    # Промты
    if status["prompts"]:
        print("✅ Промты: готовы")
    else:
        print("❌ Промты: нужны")
    
    # Картинки
    if status["images_count"] >= 6:
        print(f"✅ Картинки: готовы ({status['images_count']} шт)")
    elif status["images_count"] > 0:
        print(f"⚠️  Картинки: частично ({status['images_count']} из 6)")
    else:
        print("❌ Картинки: нужны")
    
    # Итог
    all_ready = (
        status["script"] and 
        status["voice"] and 
        status["prompts"] and 
        status["images_count"] >= 6
    )
    
    if all_ready:
        print("\n🎉 ВСЁ ГОТОВО! Можно монтировать видео")
    else:
        print("\n⚙️  ТРЕБУЕТСЯ ГЕНЕРАЦИЯ недостающих компонентов")
    
    print(f"{'='*60}")
    
    return all_ready


def get_missing_components(status: dict) -> list:
    """Возвращает список компонентов которые нужно сгенерировать"""
    
    missing = []
    
    if not status["script"]:
        missing.append("script")
    
    if not status["voice"]:
        missing.append("voice")
    
    if not status["prompts"]:
        missing.append("prompts")
    
    if status["images_count"] < 6:
        missing.append("images")
    
    return missing