from modules.research_module import gather_facts
from modules.plan_module import create_plan
from modules.write_module import write_article
from modules.text_generator import save_script
from modules.prompt_loader import list_available_prompts
from datetime import datetime

def main():
    print("🚀 TikTok Agent — полный цикл\n")

    # === ВЫБОР ПРОМПТА ===
    print("📂 Доступные промпты:")
    available = list_available_prompts()
    for i, p in enumerate(available, 1):
        print(f"  {i}. {p}")
    
    # Выбери номер или оставь пустым для случайного
    prompt_choice = input("\nВыберите промпт (номер или Enter для случайного): ").strip()
    
    if prompt_choice.isdigit():
        selected_prompt = available[int(prompt_choice) - 1]
    else:
        selected_prompt = None  # Случайный
    
    # === ВВОДИ СВОЮ ТЕМУ ЗДЕСЬ ===
    topic = "Свидетельства механизированной обработки камня на базальтовых блоках египетских пирамид"
    
    # === ВВОДИ СВОЁ ВСТУПЛЕНИЕ/СТИЛЬ ===
    user_intro = """
    Стиль: монолог человека который нашёл нестыковки и не может молчать.
    Тон: уверенный, но без утверждений — "есть свидетельства", "обнаружено".
    Сравнения: обязательно с современностью — "сейчас это делают так, а тогда..."
    Концовка: вопрос который делит аудиторию на два лагеря.
    """
    
    print(f"\n📌 Тема: {topic}")
    print(f"📌 Промпт: {selected_prompt if selected_prompt else 'случайный'}")
    print("\n" + "="*50)
    
    try:
        # ЭТАП 1: Сбор фактов
        print("🔍 ЭТАП 1: Сбор информации...")
        facts = gather_facts(topic, user_intro)
        print("✅ Факты собраны\n")
        
        # ЭТАП 2: Создание плана
        print("📋 ЭТАП 2: Создание плана статьи...")
        plan = create_plan(topic, facts)
        print("✅ План готов\n")
        
        # ЭТАП 3: Написание статьи
        print("✍️ ЭТАП 3: Написание статьи...")
        article = write_article(topic, facts, plan, user_intro, selected_prompt)
        print("✅ Статья написана\n")
        
        # Сохранение
        filepath = save_script(article, topic)
        print(f"💾 Сохранено: {filepath}")
        
        # Покажем результат
        print("\n" + "="*50)
        print(article)
        print("="*50)
        print(f"\n📊 Слов в тексте: {len(article.split())}")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Готово!")

if __name__ == "__main__":
    main()