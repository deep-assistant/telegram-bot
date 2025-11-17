#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции GPT + AdLean API
1. Отправляет запрос к GPT и получает ответ
2. Отправляет ответ GPT в AdLean API для получения рекламы
"""
import urllib.request
import urllib.error
import time
import json
from datetime import datetime

# === НАСТРОЙКИ ИЗ КОНФИГА ===
ADLEAN_API_KEY = "ad-neKuRYJqPWOu57E6ibd7CrbrtafUa9dVadhvghZtOSQ102TXPplLMmB9o5ZGv"
ADLEAN_API_URL = "https://api.adlean.pro/engine/send_message"

# GPT API настройки (из config.py)
GPT_PROXY_URL = "https://api.deep.assistant.run.place"
GPT_ADMIN_TOKEN = "677bafc4f788f69d1f23c1881d49iuyt"

# Тестовые данные
TEST_USER_ID = "1203720181"
TEST_MESSAGE = "Как выложить песню на Spotify?"


def log(prefix: str, message: str):
    """Простое логирование"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{prefix}] {message}")


def test_gpt_api():
    """
    Шаг 1: Проверка GPT API
    Отправляем запрос к GPT и получаем ответ
    """
    print("\n" + "="*80)
    print("ЭТАП 1: ПРОВЕРКА GPT API")
    print("="*80)
    
    log("GPT", f"Отправка запроса к GPT API")
    log("GPT", f"User ID: {TEST_USER_ID}")
    log("GPT", f"Сообщение: {TEST_MESSAGE}")
    
    payload = {
        'userId': TEST_USER_ID,
        'content': TEST_MESSAGE,
        'systemMessage': 'default',
        'model': 'deepseek-chat'  # Базовая модель по умолчанию
    }
    
    params = f"?masterToken={GPT_ADMIN_TOKEN}"
    url = f"{GPT_PROXY_URL}/completions{params}"
    
    try:
        data = json.dumps(payload).encode('utf-8')
        request = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        log("GPT", "Отправка POST запроса...")
        start_time = time.time()
        
        with urllib.request.urlopen(request, timeout=30) as response:
            elapsed = time.time() - start_time
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
        
        if status_code == 200:
            result = json.loads(response_data)
            
            log("GPT", f"✅ Ответ получен за {elapsed:.2f}с")
            
            # Извлекаем контент из ответа
            gpt_response = result['choices'][0]['message']['content']
            gpt_model = result.get('model', 'unknown')
            
            print(f"\n{'='*80}")
            print("📝 ОТВЕТ ОТ GPT:")
            print(f"{'='*80}")
            print(f"Модель: {gpt_model}")
            print(f"Длина ответа: {len(gpt_response)} символов")
            print(f"\nПервые 200 символов:")
            print(gpt_response[:200] + "..." if len(gpt_response) > 200 else gpt_response)
            print(f"{'='*80}\n")
            
            return gpt_response
            
        else:
            log("GPT", f"❌ Ошибка: HTTP {status_code}")
            return None
            
    except urllib.error.HTTPError as e:
        log("GPT", f"❌ HTTP ошибка: {e.code} - {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"Ответ сервера: {error_body[:300]}")
        except:
            pass
        return None
        
    except Exception as e:
        log("GPT", f"❌ Ошибка: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_adlean_api(gpt_response: str):
    """
    Шаг 2: Проверка AdLean API
    Отправляем ответ GPT в AdLean для получения рекламы
    """
    print("\n" + "="*80)
    print("ЭТАП 2: ПРОВЕРКА ADLEAN API")
    print("="*80)
    
    log("AdLean", "Отправка ответа GPT в AdLean API")
    log("AdLean", f"User ID: {TEST_USER_ID}")
    log("AdLean", f"Текст для таргетинга: {TEST_MESSAGE}")
    
    # Формируем payload согласно документации
    payload = {
        "text": gpt_response[:500],  # Ограничиваем как в боте
        "role": "assistant",  # Ответ от ассистента
        "timestamp": int(time.time()),
        "chat_id": f"chat_{TEST_USER_ID}",
        "user_type": "non_authorized",
        "user_metadata": {
            "country": "RU",
            "gender": "unknown",
            "ip": "0.0.0.0"
        }
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        request = urllib.request.Request(
            ADLEAN_API_URL,
            data=data,
            headers={
                "accept": "application/json",
                "Auth": ADLEAN_API_KEY,
                "Content-Type": "application/json"
            },
            method='POST'
        )
        
        log("AdLean", "Отправка POST запроса...")
        start_time = time.time()
        
        with urllib.request.urlopen(request, timeout=10) as response:
            elapsed = time.time() - start_time
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
        
        if status_code == 200:
            result = json.loads(response_data)
            
            log("AdLean", f"✅ Ответ получен за {elapsed:.2f}с")
            
            # Показываем полный JSON
            print(f"\n{'🔵'*40}")
            print("📡 ОТВЕТ ОТ ADLEAN API (JSON):")
            print(f"{'🔵'*40}")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print(f"{'🔵'*40}\n")
            
            have_ads = result.get("have_ads", False)
            content = result.get("content", "") or ""
            
            if have_ads and content:
                print(f"{'🎉'*40}")
                print("✅ РЕКЛАМА ПОЛУЧЕНА!".center(80))
                print(f"{'🎉'*40}")
                print(f"\n{content}\n")
                print(f"{'='*80}\n")
                return True
            else:
                print(f"{'⚠️ '*40}")
                print("❌ РЕКЛАМА НЕ ПОЛУЧЕНА".center(80))
                print(f"{'⚠️ '*40}\n")
                
                log("AdLean", f"have_ads = {have_ads}")
                log("AdLean", f"content = {'пусто' if not content else f'{len(content)} символов'}")
                
                print(f"\n💡 ПРИЧИНЫ:")
                print(f"   1. Нет активных рекламных кампаний")
                print(f"   2. Таргетинг не подходит для текущего пользователя")
                print(f"   3. Бюджет кампании исчерпан")
                print(f"   4. API работает, но реклама не доступна\n")
                
                return False
                
        else:
            log("AdLean", f"❌ Ошибка: HTTP {status_code}")
            return False
            
    except Exception as e:
        log("AdLean", f"❌ Ошибка: {type(e).__name__}: {str(e)}")
        return False


def main():
    """Основная функция тестирования"""
    print("\n" + "🎯"*40)
    print("ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ GPT + ADLEAN".center(80))
    print("🎯"*40)
    
    # Шаг 1: Получаем ответ от GPT
    gpt_response = test_gpt_api()
    
    if not gpt_response:
        print("\n❌ ТЕСТ ПРОВАЛЕН: GPT API не работает")
        print("Проверьте настройки PROXY_URL и ADMIN_TOKEN\n")
        return
    
    # Небольшая пауза
    time.sleep(0.5)
    
    # Шаг 2: Отправляем ответ GPT в AdLean
    ad_received = test_adlean_api(gpt_response)
    
    # Итоговый отчет
    print("\n" + "📊"*40)
    print("ИТОГОВЫЙ ОТЧЕТ".center(80))
    print("📊"*40 + "\n")
    
    print(f"✅ GPT API: Работает корректно")
    print(f"{'✅' if ad_received else '⚠️ '} AdLean API: {'Реклама получена!' if ad_received else 'Реклама не доступна'}")
    
    if not ad_received:
        print(f"\n💡 РЕКОМЕНДАЦИЯ:")
        print(f"   Свяжитесь с NextUP Media (Кирилл Сараев)")
        print(f"   для активации тестовой рекламной кампании\n")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
