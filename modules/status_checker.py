import os

def check_topic_status(topic_path: str) -> dict:
    """Проверяет какие компоненты уже есть в папке темы"""
    
    status = {
        "script": False,
        "voice": False,
        "prompts": False,
        "images": [],
        "images_count": 0,
        "video": False  # ← ДОБАВЛЕНО
    }
    
    if not os.path.exists(topic_path):
        return status
    
    if os.path.exists(os.path.join(topic_path, "script.txt")):
        status["script"] = True
    
    if os.path.exists(os.path.join(topic_path, "voice.mp3")):
        status["voice"] = True
    
    if os.path.exists(os.path.join(topic_path, "prompts.json")):
        status["prompts"] = True
    
    # Проверка видео ← ДОБАВЛЕНО
    if os.path.exists(os.path.join(topic_path, "video.mp4")):
        status["video"] = True
    
    for filename in os.listdir(topic_path):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            status["images"].append(filename)
    
    status["images_count"] = len(status["images"])
    
    return status


def print_status(status: dict, topic_id: int):
    """Выводит статус темы в консоль"""
    
    print(f"\n{'='*60}")
    print(f"📊 СТАТУС ТЕМЫ #{topic_id}")
    print(f"{'='*60}")
    
    if status["script"]:
        print("✅ Сценарий: готов")
    else:
        print("❌ Сценарий: нужен")
    
    if status["voice"]:
        print("✅ Озвучка: готова")
    else:
        print("❌ Озвучка: нужна")
    
    if status["prompts"]:
        print("✅ Промты: готовы")
    else:
        print("❌ Промты: нужны")
    
    if status["images_count"] >= 6:
        print(f"✅ Картинки: готовы ({status['images_count']} шт)")
    elif status["images_count"] > 0:
        print(f"⚠️  Картинки: частично ({status['images_count']} из 6)")
    else:
        print("❌ Картинки: нужны")
    
    # Проверка видео ← ДОБАВЛЕНО
    if status["video"]:
        print("✅ Видео: готово")
    else:
        print("❌ Видео: нужно")
    
    all_ready = (
        status["script"] and 
        status["voice"] and 
        status["prompts"] and 
        status["images_count"] >= 6 and
        status["video"]  # ← ДОБАВЛЕНО
    )
    
    if all_ready:
        print("\n🎉 ВСЁ ГОТОВО! Можно загружать в TikTok")
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
    
    if not status["video"]:  # ← ДОБАВЛЕНО
        missing.append("video")
    
    return missing