import json
from modules.research_module import gather_facts
from modules.plan_module import create_plan
from modules.write_module import write_article
from modules.text_generator import save_script
from modules.topic_manager import TopicManager
from modules.author_loader import load_author_style
from modules.image_prompt_generator import generate_image_prompts, save_prompts_to_file
from modules.status_checker import check_topic_status, print_status, get_missing_components
from services.voice_service import generate_voice_from_script
from services.image_service import generate_all_images
from datetime import datetime
import os
import config
import time

def process_single_topic(manager: TopicManager, topic_data: dict, prompt_style: str = None):
    """Обрабатывает одну тему с проверкой существующих файлов"""
    
    topic_id = topic_data["id"]
    topic = topic_data["topic"]
    angle = topic_data.get("angle", "")
    notes = topic_data.get("notes", "")
    
    # Загружаем стиль автора
    try:
        author = load_author_style()
        author_name = author["name"]
    except:
        author_name = "Автор"
    
    print(f"\n{'='*60}")
    print(f"📝 ОБРАБОТКА ТЕМЫ #{topic_id}")
    print(f"{'='*60}")
    print(f"Тема: {topic}")
    print(f"Заметки: {notes[:60]}..." if notes else "Заметки: нет")
    print(f"Стиль автора: {author_name}")
    
    # === СОЗДАЁМ ПАПКУ ДЛЯ ТЕМЫ ===
    safe_topic = topic[:30].replace(' ', '_').replace(':', '').replace('/', '').replace('"', '')
    topic_folder = f"topic_{topic_id}_{safe_topic}"
    topic_path = os.path.join(config.PATHS["output"], topic_folder)
    os.makedirs(topic_path, exist_ok=True)
    print(f"📁 Папка темы: {topic_path}")
    
    # === ПРОВЕРЯЕМ СТАТУС ===
    status = check_topic_status(topic_path)
    print_status(status, topic_id)
    
    missing = get_missing_components(status)
    
    if not missing:
        print("✅ Все компоненты готовы! Пропускаем генерацию.")
        manager.mark_completed(topic_id, os.path.join(topic_path, "script.txt"))
        return True
    
    print(f"⚙️  Будет сгенерировано: {', '.join(missing)}")
    try: 
        # Загружаем статью если есть (для генерации промтов и картинок)
        article = ""
        script_filepath = os.path.join(topic_path, "script.txt")
        
        if status["script"]:
            with open(script_filepath, "r", encoding="utf-8") as f:
                full_content = f.read()
                # Извлекаем статью из файла (после метаданных)
                parts = full_content.split("\n\n", 1)
                if len(parts) > 1:
                    article = parts[1].strip()
                else:
                    article = full_content
            print("📄 Статья загружена из файла")
        else:
            # Генерируем статью (ЭТАП 1-3)
            print("\n🔍 ЭТАП 1: Сбор информации...")
            facts = gather_facts(topic, notes)
            print("✅ Факты собраны")
            
            print("\n📋 ЭТАП 2: Создание плана статьи...")
            plan = create_plan(topic, facts)
            print("✅ План готов")
            
            print("\n✍️ ЭТАП 3: Написание статьи...")
            article = write_article(topic, facts, plan, notes, prompt_style, angle)
            print("✅ Статья написана")
            
            # === СОХРАНЕНИЕ СЦЕНАРИЯ ===
            script_filename = "script.txt"
            script_filepath = os.path.join(topic_path, script_filename)
            
            content = f"""Тема: {topic}
            ID: {topic_id}
            Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Автор: {author_name}
            Вектор: {angle}

            {article}
            """
            with open(script_filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"\n💾 Сценарий сохранён: {script_filepath}")
            print(f"📊 Слов в тексте: {len(article.split())}")
        
        # === ЭТАП 4: ОЗВУЧКА ===
        if "voice" in missing:
            print("\n🎙️ ЭТАП 4: Генерация голоса...")
            
            audio_filename = "voice.mp3"
            audio_filepath = os.path.join(topic_path, audio_filename)
            
            audio_path = generate_voice_from_script(
                script_path=script_filepath,
                output_path=audio_filepath
            )
            print(f"✅ Аудио сохранено: {audio_path}")
        else:
            print("\n✅ Озвучка: уже готова (пропущено)")
        
            # === ЭТАП 5: ГЕНЕРАЦИЯ ПРОМТОВ ===
        if "prompts" in missing:
            print("\n🎨 ЭТАП 5: Генерация промтов для картинок...")
            
            try:
                prompts = generate_image_prompts(topic, article, angle)
            except Exception as e:
                print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
                print("⛔ Генерация остановлена. Промты не созданы.")
                manager.mark_failed(topic_id)
                return False
            
            # Сохраняем промты в файл
            prompts_filepath = os.path.join(topic_path, "prompts.json")
            save_prompts_to_file(prompts, prompts_filepath)
        else:
            print("\n✅ Промты: уже готовы (пропущено)")
            # Загружаем существующие промты
            prompts_filepath = os.path.join(topic_path, "prompts.json")
            with open(prompts_filepath, "r", encoding="utf-8") as f:
                prompts = json.load(f)
        
        # === ЭТАП 6: ГЕНЕРАЦИЯ КАРТИНОК ===
        if "images" in missing:
            print("\n🖼️ ЭТАП 6: Генерация картинок...")
            
            image_paths = generate_all_images(prompts, topic_path, topic)
            
            print(f"📊 Всего картинок: {len(image_paths)}")
        else:
            print("\n✅ Картинки: уже готовы (пропущено)")
        
        # Отмечаем тему как выполненную
        manager.mark_completed(topic_id, script_filepath)
        
        # Примерная длительность
        word_count = len(article.split())
        duration = word_count / 2.5
        print(f"⏱️ Длительность аудио: ~{duration:.0f} секунд")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        manager.mark_failed(topic_id)
        return False


def main():
    print("🚀 TikTok Agent — пакетная генерация\n")
    
    # Загружаем стиль автора
    try:
        author = load_author_style()
        print(f"👤 Автор: {author['name']}")
        print(f"📺 Канал: {author['channel']}")
    except Exception as e:
        print(f"⚠️ Не удалось загрузить стиль автора: {e}")
    
    print()
    
    # Инициализация менеджера тем
    manager = TopicManager()
    manager.show_stats()
    
    pending = manager.get_pending_topics()
    
    if not pending:
        print("✅ Все темы обработаны! Добавьте новые в topics.json")
        return
    
    print(f"📋 Найдено {len(pending)} тем в очереди\n")
    
    # Выбор режима
    print("Выберите режим:")
    print("1. Обработать все темы по очереди")
    print("2. Обработать одну конкретную тему")
    print("3. Добавить новую тему")
    
    choice = input("\nВаш выбор (1/2/3): ").strip()
    
    if choice == "3":
        topic = input("\nВведите тему: ").strip()
        angle = input("Вектор статьи (или Enter для пропуска): ").strip()
        notes = input("Заметки по теме (или Enter для пропуска): ").strip()
        
        topic_id = manager.add_topic(topic, angle, notes)
        
        print("\n✅ Тема добавлена в очередь")
        return
    
    elif choice == "2":
        topic_id = input("\nВведите ID темы: ").strip()
        if not topic_id.isdigit():
            print("❌ Неверный ID")
            return
        
        topic_data = manager.get_topic_by_id(int(topic_id))
        if not topic_data:
            print("❌ Тема не найдена")
            return
        
        process_single_topic(manager, topic_data)
    
    elif choice == "1":
        print(f"\n⚙️ Начинаю обработку {len(pending)} тем...\n")
        
        success_count = 0
        for i, topic_data in enumerate(pending, 1):
            print(f"\n{'='*60}")
            print(f"ПРОГРЕСС: {i}/{len(pending)}")
            print(f"{'='*60}")
            
            if process_single_topic(manager, topic_data):
                success_count += 1
            
            if i < len(pending):
                print("\n⏸️ Пауза 5 секунд...")
                time.sleep(5)
        
        print(f"\n{'='*60}")
        print(f"🎉 ГОТОВО!")
        print(f"  Обработано: {len(pending)}")
        print(f"  Успешно: {success_count}")
        print(f"  Ошибки: {len(pending) - success_count}")
        print(f"{'='*60}")
    
    else:
        print("❌ Неверный выбор")


if __name__ == "__main__":
    main()