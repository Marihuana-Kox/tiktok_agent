from modules.research_module import gather_facts
from modules.plan_module import create_plan
from modules.write_module import write_article
from modules.text_generator import save_script
from modules.topic_manager import TopicManager
from modules.author_loader import load_author_style
from datetime import datetime
import os
import config  # ← ДОБАВИТЬ ЭТУ СТРОКУ
import time    # ← И ЭТУ (для пауз)

def process_single_topic(manager: TopicManager, topic_data: dict, prompt_style: str = None):
    """Обрабатывает одну тему"""
    
    topic_id = topic_data["id"]
    topic = topic_data["topic"]
    notes = topic_data.get("notes", "")  # Заметки по теме
    
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
    
    try:
        # ЭТАП 1: Сбор фактов
        print("\n🔍 ЭТАП 1: Сбор информации...")
        facts = gather_facts(topic, notes)
        print("✅ Факты собраны")
        
        # ЭТАП 2: Создание плана
        print("\n📋 ЭТАП 2: Создание плана статьи...")
        plan = create_plan(topic, facts)
        print("✅ План готов")
        
        # ЭТАП 3: Написание статьи
        print("\n✍️ ЭТАП 3: Написание статьи...")
        article = write_article(topic, facts, plan, notes, prompt_style)
        print("✅ Статья написана")
        
        # Сохранение
        filename = f"topic_{topic_id}_{topic[:30].replace(' ', '_')}.txt"
        filepath = os.path.join(config.PATHS["scripts"], filename)
        
        content = f"""Тема: {topic}
ID: {topic_id}
Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Автор: {author_name}

{article}
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        manager.mark_completed(topic_id, filepath)
        
        print(f"\n💾 Сохранено: {filepath}")
        print(f"📊 Слов в тексте: {len(article.split())}")
        
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
        notes = input("Заметки по теме (или Enter для пропуска): ").strip()
        
        # Добавляем в менеджер
        topic_id = manager.add_topic(topic, "")
        
        # Обновляем заметки вручную (так как add_topic не принимает notes)
        manager.data["topics"][-1]["notes"] = notes
        manager._save_topics()
        
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
                import time
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